"""Os três baselines internos (Fase 6). Nenhum modelo avança sem batê-los.

1. Persistência: a cota atual se mantém.
2. Regressão linear com lags de cota (própria e de montante).
3. Propagação com tempo de viagem constante: a cota de montante, deslocada
   pelo tempo de viagem e reescalada linearmente.

Todos operam sobre o dataset supervisionado da Fase 5. Ajustes (regressão,
tempo de viagem, reescala) acontecem SÓ no treino de cada fold.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# Montante imediato usado pelos baselines 2 e 3
MONTANTE = {86510000: "jj", 86720000: "mu", 86879300: "en"}
PROPRIA = {86510000: "mu", 86720000: "en", 86879300: "es"}


def persistencia(test: pd.DataFrame, codigo: int, h: int) -> pd.Series:
    return test[f"nivel_{PROPRIA[codigo]}"].rename("pred")


def _cols_lags(ds: pd.DataFrame, codigo: int) -> list[str]:
    aps = [PROPRIA[codigo], MONTANTE[codigo]]
    return [c for c in ds.columns
            if any(c == f"{base}_{ap}" for ap in aps
                   for base in ("nivel", "dnivel_1h", "dnivel_3h"))]


def regressao_lags(train: pd.DataFrame, test: pd.DataFrame,
                   codigo: int, h: int) -> pd.Series:
    cols = _cols_lags(train, codigo)
    alvo = f"y_{h}h"
    tr = train[cols + [alvo]].dropna()
    modelo = LinearRegression().fit(tr[cols], tr[alvo])
    ok = test[cols].notna().all(axis=1)
    pred = pd.Series(np.nan, index=test.index, name="pred")
    if ok.any():
        pred[ok] = modelo.predict(test.loc[ok, cols])
    return pred


def estimar_tempo_viagem(train: pd.DataFrame, codigo: int,
                         max_lag_h: int = 24) -> int:
    """Lag (h) que maximiza a correlação montante(t-lag) × alvo(t) no treino."""
    alvo = train[f"nivel_{PROPRIA[codigo]}"]
    montante = train[f"nivel_{MONTANTE[codigo]}"]
    melhor, melhor_r = 1, -np.inf
    for lag in range(max_lag_h + 1):
        r = alvo.corr(montante.shift(lag))
        if pd.notna(r) and r > melhor_r:
            melhor, melhor_r = lag, r
    return melhor


def propagacao(train: pd.DataFrame, test: pd.DataFrame,
               codigo: int, h: int) -> pd.Series:
    """pred(t+h) = a + b * nivel_montante(t - max(tau - h, 0)).

    tau estimado no treino; a reescala linear (a, b) idem. Os datasets são
    indexados por hora contínua dentro de cada janela, então shift posicional
    dentro da janela equivale a shift temporal — o shift é feito por janela
    para não vazar entre janelas.
    """
    tau = estimar_tempo_viagem(train, codigo)
    atraso = max(tau - h, 0)
    alvo = f"y_{h}h"
    up = f"nivel_{MONTANTE[codigo]}"

    def desloca(df: pd.DataFrame) -> pd.Series:
        return df.groupby("janela_id")[up].shift(atraso)

    x_tr = desloca(train)
    tr = pd.DataFrame({"x": x_tr, "y": train[alvo]}).dropna()
    if len(tr) < 10:
        return pd.Series(np.nan, index=test.index, name="pred")
    modelo = LinearRegression().fit(tr[["x"]], tr["y"])
    x_te = desloca(test)
    pred = pd.Series(np.nan, index=test.index, name="pred")
    ok = x_te.notna()
    if ok.any():
        pred[ok] = modelo.predict(x_te[ok].to_frame("x"))
    return pred
