"""Treino separado da inferência; artefatos locais reutilizáveis por conteúdo."""
import hashlib
import json
import pickle
from dataclasses import dataclass
from pathlib import Path

import lightgbm as lgb
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from ..core.paths import ROOT
from ..core.provenance import frame_hash, runtime, sha256
from ..core.storage import atomic_write
from . import baselines, gbm


@dataclass
class Forecast:
    columns: list[str]
    own: str
    estimator: object | None = None
    delta: bool = False
    missing_aux: bool = False
    fallback: 'Forecast | None' = None
    artifact_id: str | None = None

    def predict(self, test: pd.DataFrame) -> pd.Series:
        pred = (self.fallback.predict(test) if self.fallback else
                pd.Series(float('nan'), index=test.index, name='pred'))
        if self.estimator is None:
            return pred
        ok = (test[self.own].notna() if self.missing_aux else test[self.columns].notna().all(axis=1))
        if ok.any():
            pred.loc[ok] = self.estimator.predict(test.loc[ok, self.columns])
            if self.delta:
                pred.loc[ok] += test.loc[ok, self.own]
        return pred


def fit(train: pd.DataFrame, codigo: int, h: int, motor: str, cfg: dict) -> Forecast:
    own, target = f'nivel_{baselines.PROPRIA[codigo]}', f'y_{h}h'
    if motor == 'linear':
        cols = baselines._cols_lags(train, codigo)
        tr = train.dropna(subset=cols + [target])
        model = Forecast(cols, own)
        if len(tr) >= max(10, len(cols)+1):
            model.estimator = LinearRegression().fit(tr[cols], tr[target])
        return model
    if motor == 'ridge_montante':
        cols = [c for c in train if c.startswith(('nivel_', 'dnivel_1h_', 'dnivel_3h_'))]
        tr = train.dropna(subset=cols + [target])
        model = Forecast(cols, own, delta=True, fallback=fit(train, codigo, h, 'linear', cfg))
        if len(tr) >= 500:
            model.estimator = make_pipeline(StandardScaler(), Ridge(alpha=100.))
            model.estimator.fit(tr[cols], tr[target]-tr[own])
        return model
    if motor not in ('gbm_nivel', 'gbm_delta', 'gbm_postos'):
        raise ValueError(f'Motor desconhecido: {motor}')
    cols = gbm.colunas_features(train)
    if motor == 'gbm_postos' and not any(c.startswith('posto_') for c in cols):
        raise ValueError('GBM de postos requer features de chuva ANA; reconstrua o pool.')
    if motor != 'gbm_postos':
        cols = [c for c in cols if not c.startswith('posto_')]
    model = Forecast(cols, own, delta=motor != 'gbm_nivel', missing_aux=True)
    train = train.dropna(subset=[target, own]).copy()
    if train.empty:
        return model
    if model.delta:
        train[target] -= train[own]
    tr, ev = gbm._split_early_stopping(train, cfg['valid_frac_janelas'])
    if len(tr) < 500 or len(ev) < 50:
        tr, ev = train, None
    model.estimator = lgb.LGBMRegressor(**(cfg['lgbm'] | {'n_jobs': 4, 'random_state': 42}))
    kwargs = {} if ev is None else {
        'eval_set': [(ev[cols], ev[target])],
        'callbacks': [lgb.early_stopping(cfg['early_stopping_rounds'], verbose=False)]}
    model.estimator.fit(tr[cols], tr[target], **kwargs)
    return model


def fit_cached(train, codigo, h, motor, cfg, cache: Path | None = None) -> Forecast:
    if cache is None:
        return fit(train, codigo, h, motor, cfg)
    sources = [Path(__file__), Path(gbm.__file__), Path(baselines.__file__)]
    from ..eval import cv
    sources.extend([Path(cv.__file__), ROOT / "uv.lock", ROOT / "config/features.yaml"])
    signature = {'train': frame_hash(train), 'codigo': codigo, 'h': h, 'motor': motor,
                 'config': cfg, 'runtime': runtime(), 'code': [sha256(p) for p in sources]}
    key = hashlib.sha256(json.dumps(signature, sort_keys=True).encode()).hexdigest()
    dest = cache / f'{key}.pkl'
    if dest.exists():
        with dest.open("rb") as source:
            return pickle.load(source)
    model = fit(train, codigo, h, motor, cfg)
    model.artifact_id = key
    atomic_write(dest, lambda tmp: tmp.write_bytes(pickle.dumps(model)))
    return model
