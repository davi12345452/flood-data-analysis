"""Métricas hidrológicas (NSE e KGE obrigatórias) e utilitários NaN-safe.

Pares com observação OU previsão ausente são excluídos do cálculo — e a
FRAÇÃO excluída é reportada junto (Armadilha 0: se o dado some nos picos,
a métrica calculada só no que sobrou mede o caso fácil).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _validos(obs: pd.Series, pred: pd.Series) -> tuple[np.ndarray, np.ndarray, float]:
    o, p = np.asarray(obs, dtype=float), np.asarray(pred, dtype=float)
    ok = ~(np.isnan(o) | np.isnan(p))
    cobertura = float(ok.mean()) if len(ok) else 0.0
    return o[ok], p[ok], cobertura


def nse(obs: pd.Series, pred: pd.Series) -> float:
    o, p, _ = _validos(obs, pred)
    if len(o) < 2 or np.var(o) == 0:
        return np.nan
    return 1.0 - float(np.sum((o - p) ** 2) / np.sum((o - o.mean()) ** 2))


def kge(obs: pd.Series, pred: pd.Series) -> float:
    o, p, _ = _validos(obs, pred)
    if len(o) < 2 or o.std() == 0 or o.mean() == 0:
        return np.nan
    r = float(np.corrcoef(o, p)[0, 1]) if p.std() > 0 else 0.0
    alpha = float(p.std() / o.std())
    beta = float(p.mean() / o.mean())
    return 1.0 - float(np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2))


def rmse(obs: pd.Series, pred: pd.Series) -> float:
    o, p, _ = _validos(obs, pred)
    return float(np.sqrt(np.mean((o - p) ** 2))) if len(o) else np.nan


def mae(obs: pd.Series, pred: pd.Series) -> float:
    o, p, _ = _validos(obs, pred)
    return float(np.mean(np.abs(o - p))) if len(o) else np.nan


def resumo(obs: pd.Series, pred: pd.Series) -> dict:
    _, _, cobertura = _validos(obs, pred)
    return {
        "NSE": nse(obs, pred),
        "KGE": kge(obs, pred),
        "RMSE_cm": rmse(obs, pred),
        "MAE_cm": mae(obs, pred),
        "cobertura": cobertura,
        "n": int((~(pd.isna(obs) | pd.isna(pred))).sum()),
    }
