"""Métricas de detecção e de pico (Fase 8).

Detecção: ultrapassagem da cota de inundação hora a hora (POD, FAR, CSI,
viés de frequência). Pico: erro no valor e no tempo do pico, evento a evento,
com a cobertura de dado em torno do pico reportada junto (Armadilha 0).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def deteccao(obs: pd.Series, pred: pd.Series, limiar: float) -> dict:
    ok = obs.notna() & pred.notna()
    o = obs[ok] >= limiar
    p = pred[ok] >= limiar
    hits = int((o & p).sum())
    misses = int((o & ~p).sum())
    falsos = int((~o & p).sum())
    pod = hits / (hits + misses) if hits + misses else np.nan
    far = falsos / (hits + falsos) if hits + falsos else np.nan
    csi = hits / (hits + misses + falsos) if hits + misses + falsos else np.nan
    vies = (hits + falsos) / (hits + misses) if hits + misses else np.nan
    return {"POD": pod, "FAR": far, "CSI": csi, "vies_freq": vies,
            "horas_obs_acima": hits + misses, "n": int(ok.sum())}


def pico_por_evento(g: pd.DataFrame, janela_cobertura_h: int = 12) -> dict | None:
    """g: linhas de um (alvo, evento, h, variante) com ts_utc, obs, pred.

    Erro de valor e de tempo do pico + cobertura de observação em ±12h do
    pico observado. None se não houver observação válida.
    """
    g = g.dropna(subset=["obs"]).sort_values("ts_utc")
    if g.empty:
        return None
    i_obs = g["obs"].idxmax()
    t_obs, v_obs = g.loc[i_obs, "ts_utc"], float(g.loc[i_obs, "obs"])

    gp = g.dropna(subset=["pred"])
    if gp.empty:
        return None
    i_pred = gp["pred"].idxmax()
    t_pred, v_pred = gp.loc[i_pred, "ts_utc"], float(gp.loc[i_pred, "pred"])

    em_torno = g[(g["ts_utc"] >= t_obs - pd.Timedelta(hours=janela_cobertura_h))
                 & (g["ts_utc"] <= t_obs + pd.Timedelta(hours=janela_cobertura_h))]
    horas_esperadas = 2 * janela_cobertura_h + 1
    return {
        "pico_obs_cm": v_obs,
        "erro_valor_pico_cm": v_pred - v_obs,
        "erro_tempo_pico_h": (t_pred - t_obs).total_seconds() / 3600,
        "cobertura_pico": len(em_torno) / horas_esperadas,
    }
