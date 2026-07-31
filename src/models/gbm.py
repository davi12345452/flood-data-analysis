"""LightGBM raso para previsão de cota (Fase 7).

- NaN entra nativo no LightGBM — nenhuma imputação (Armadilha 0).
- Early stopping numa fatia cronologicamente final das JANELAS de treino
  (nunca o teste do fold).
- Variante "restrito": treino só com linhas >= cota de atenção da própria
  estação (Armadilha 2); o teste não muda.
"""

from __future__ import annotations

import lightgbm as lgb
import numpy as np
import pandas as pd

from ..ingest.common import REFERENCE, load_config

APELIDO = {86510000: "mu", 86720000: "en", 86879300: "es"}

COLUNAS_META = {"janela_id", "tipo"}


def colunas_features(ds: pd.DataFrame) -> list[str]:
    return [c for c in ds.columns
            if not c.startswith("y_") and c not in COLUNAS_META]


def _split_early_stopping(train: pd.DataFrame, frac: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Janelas de treino ordenadas pelo início; as últimas `frac` viram eval."""
    inicios = train.groupby("janela_id").apply(lambda g: g.index.min(), include_groups=False)
    ordem = inicios.sort_values().index.tolist()
    n_eval = max(1, int(len(ordem) * frac))
    janelas_eval = set(ordem[-n_eval:])
    eval_mask = train["janela_id"].isin(janelas_eval)
    return train[~eval_mask], train[eval_mask]


def treinar_prever(train: pd.DataFrame, test: pd.DataFrame, codigo: int, h: int,
                   restrito: bool = False) -> tuple[pd.Series, pd.Series]:
    """Retorna (previsões no teste, importância por ganho)."""
    cfg = load_config("model")
    alvo = f"y_{h}h"
    cols = colunas_features(train)

    if restrito:
        cotas = pd.read_csv(REFERENCE / "cotas_referencia.csv").set_index("codigo")
        limiar = float(cotas.loc[codigo, "atencao_cm"])
        train = train[train[f"nivel_{APELIDO[codigo]}"] >= limiar]

    train = train[train[alvo].notna()]
    tr, ev = _split_early_stopping(train, cfg["valid_frac_janelas"])
    if len(tr) < 500 or len(ev) < 50:
        tr, ev = train, None

    modelo = lgb.LGBMRegressor(**cfg["lgbm"])
    if ev is not None and len(ev):
        modelo.fit(
            tr[cols], tr[alvo],
            eval_set=[(ev[cols], ev[alvo])],
            callbacks=[lgb.early_stopping(cfg["early_stopping_rounds"], verbose=False)],
        )
    else:
        modelo.fit(tr[cols], tr[alvo])

    pred = pd.Series(modelo.predict(test[cols]), index=test.index, name="pred")
    # linha sem rótulo observável não é avaliável, mas a previsão existe;
    # quem consome cruza com obs. Importância por ganho, normalizada:
    imp = pd.Series(modelo.booster_.feature_importance("gain"), index=cols)
    imp = imp / imp.sum() if imp.sum() > 0 else imp
    return pred, imp
