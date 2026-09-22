"""Atualização por erros já observados, com relógios explícitos.

Nunca usa o erro da previsão que está sendo corrigida. Lacunas permanecem
lacunas. Parâmetros são escolhidos em eventos anteriores, não na rodada viva.
"""

from __future__ import annotations

import pandas as pd


def corrigir(pred: pd.Series, obs: pd.Series, h: int, *, ganho: float = 0.5,
             janela_h: int = 6, min_amostras: int = 3) -> pd.DataFrame:
    """Subtrai média de erros amadurecidos em (t-janela, t].

    pred é indexada pela referência; obs pelo instante da observação. Um
    erro de pred(t-h) só entra na correção em t, quando obs(t) existe.
    Ganho zero mantém o modelo original. A contagem acompanha cada ajuste.
    """
    if h <= 0 or janela_h <= 0 or min_amostras < 1 or not 0 <= ganho <= 1:
        raise ValueError("Horizonte/janela/amostras positivos e ganho entre 0 e 1.")
    if pred.index.has_duplicates or obs.index.has_duplicates:
        raise ValueError("Timestamps duplicados no replay.")
    pred = pred.sort_index()
    passada = pred.copy()
    passada.index = passada.index + pd.Timedelta(hours=h)
    # Inclui referências e validades: rolling temporal não atravessa lacunas
    # por número de linhas e não ffill-a uma correção que já expirou.
    grade = pred.index.union(passada.index).sort_values()
    erro = (passada.reindex(grade) - obs.reindex(grade))
    rolling = erro.rolling(f"{janela_h}h", min_periods=min_amostras, closed="right")
    vies = rolling.mean().reindex(pred.index)
    n = erro.rolling(f"{janela_h}h", closed="right").count().reindex(pred.index)
    ajuste = -ganho * vies.fillna(0)
    return pd.DataFrame({"base_cm": pred, "ajuste_cm": ajuste,
                         "previsto_cm": pred + ajuste, "n_ajuste": n.astype(int)})
