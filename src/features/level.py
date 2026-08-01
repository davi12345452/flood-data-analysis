"""Features de cota, disponibilidade de sensor e tempo desde atenção.

Tudo causal e sem interpolação: derivada com lacuna no caminho fica NaN
(Armadilha 0 — fabricar valor em lacuna de cheia é o pecado capital daqui).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..ingest.common import ROOT

INTERIM = ROOT / "data" / "interim"


def carregar_ana() -> pd.DataFrame:
    return pd.read_parquet(INTERIM / "ana_hourly.parquet")


def derivadas(nivel: pd.Series) -> pd.DataFrame:
    """nivel, d1h, d3h e d2 (aceleração). NaN propaga — sem interpolação."""
    return pd.DataFrame({
        "nivel": nivel,
        "dnivel_1h": nivel.diff(1),
        "dnivel_3h": nivel.diff(3) / 3,
        "d2nivel": nivel.diff(1).diff(1),
    })


def tempo_desde_atencao(nivel: pd.Series, limiar_cm: float, cap_h: int) -> pd.Series:
    """Horas desde a última observação VÁLIDA >= cota de atenção.

    Horas com nível NaN não resetam nem avançam o marcador de forma especial:
    contam como 'não acima' (conservador). Sem ultrapassagem no histórico
    disponível, vale o teto.
    """
    acima = (nivel >= limiar_cm).fillna(False).to_numpy()
    idx = np.arange(len(acima))
    ultimo = pd.Series(np.where(acima, idx, np.nan), index=nivel.index).ffill()
    horas = idx - ultimo.to_numpy()
    horas = np.where(np.isnan(horas), cap_h, np.minimum(horas, cap_h))
    return pd.Series(horas, index=nivel.index, name="tempo_desde_atencao_h")


def disponibilidade(disp_nivel: pd.Series, janela_h: int) -> pd.Series:
    """Fração média de amostras válidas nas últimas janela_h horas (incluindo
    a hora atual — a disponibilidade de t é conhecida em t). Também é feature:
    ausência de dado a montante é, ela própria, sinal de magnitude."""
    return disp_nivel.fillna(0.0).rolling(janela_h, min_periods=1).mean()


def features_estacao(g: pd.DataFrame, limiar_atencao: float | None,
                     cap_h: int, janela_disp: int) -> pd.DataFrame:
    """Bloco completo de features de uma estação (frame indexado por hora).

    CRÍTICO: o interim só tem linhas para horas com amostra. Sem reindexar
    para a grade horária contínua, diff/rolling atravessam lacunas como se
    fossem 1h — derivadas erradas exatamente nas bordas de falha de sensor.
    """
    g = g.set_index("ts_utc").sort_index()
    grade = pd.date_range(g.index.min(), g.index.max(), freq="h")
    g = g.reindex(grade)
    out = derivadas(g["nivel_cm"].astype(float))
    out["disp"] = disponibilidade(g["disp_nivel"], janela_disp)
    if limiar_atencao is not None:
        out["tempo_desde_atencao_h"] = tempo_desde_atencao(
            g["nivel_cm"].astype(float), limiar_atencao, cap_h
        )
    return out
