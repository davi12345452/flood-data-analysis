"""Faixa empírica com origem e limites de aplicabilidade explícitos."""

from __future__ import annotations

import pandas as pd


def cobertura_recente(pred: pd.Series, margens: pd.Series, obs: pd.Series,
                      h: int, janela_h: int = 6) -> pd.DataFrame:
    """Cobertura conhecida em cada referência, sem consultar seu próprio futuro."""
    valor = pred.copy()
    margem = margens.copy()
    valor.index = valor.index + pd.Timedelta(hours=h)
    margem.index = margem.index + pd.Timedelta(hours=h)
    grade = pred.index.union(valor.index).sort_values()
    erro = (valor.reindex(grade) - obs.reindex(grade)).abs()
    margem = margem.reindex(grade)
    acerto = (erro <= margem).astype(float).where(erro.notna() & margem.notna())
    janela = acerto.rolling(f"{janela_h}h", closed="right")
    return pd.DataFrame({"cobertura_recente": janela.mean().reindex(pred.index),
                         "n_faixa_recente": janela.count().reindex(pred.index).astype(int)})


def faixa_empirica(valor: float, velocidade: float, calibracao: dict | None) -> dict:
    out = {"inferior_cm": float("nan"), "superior_cm": float("nan"),
           "faixa_status": "sem_calibracao", "n_calibracao": 0}
    if pd.isna(valor) or pd.isna(velocidade):
        return out | {"faixa_status": "dados_insuficientes"}
    if calibracao is None:
        return out
    out["n_calibracao"] = calibracao["n"]
    if calibracao["n"] < 30 or calibracao["margem_cm"] is None:
        return out | {"faixa_status": "amostra_insuficiente"}
    if not (calibracao["velocidade_min_cm_h"] <= velocidade
            <= calibracao["velocidade_max_cm_h"]):
        return out | {"faixa_status": "regime_fora_calibracao"}
    return out | {"inferior_cm": valor - calibracao["margem_cm"],
                  "superior_cm": valor + calibracao["margem_cm"],
                  "faixa_status": "empirica_sem_garantia"}
