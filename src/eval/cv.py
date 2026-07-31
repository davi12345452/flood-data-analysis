"""Validação cruzada por evento (protocolo fixado na Fase 5).

Fold = um evento (janela_id "ev*"). Teste = linhas daquele evento; treino =
todas as outras janelas (eventos e normais). Nunca aleatório por linha —
autocorrelação horária vazaria. Janelas normais nunca são validadas: o que
importa medir é desempenho em evento.
"""

from __future__ import annotations

from collections.abc import Iterator

import pandas as pd

from ..ingest.common import ROOT

PROCESSED = ROOT / "data" / "processed"


def carregar_dataset(codigo: int) -> pd.DataFrame:
    ds = pd.read_parquet(PROCESSED / f"dataset_{codigo}.parquet")
    return ds.set_index("ts_utc").sort_index()


def folds_por_evento(ds: pd.DataFrame) -> Iterator[tuple[str, pd.DataFrame, pd.DataFrame]]:
    eventos = sorted(ds.loc[ds["tipo"] == "evento", "janela_id"].unique())
    for ev in eventos:
        test = ds[ds["janela_id"] == ev]
        train = ds[ds["janela_id"] != ev]
        yield ev, train, test
