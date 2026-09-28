"""Validação cruzada por evento (protocolo fixado na Fase 5).

Fold = um evento (janela_id "ev*"). Teste = linhas daquele evento; treino =
todas as outras janelas (eventos e normais). Nunca aleatório por linha —
autocorrelação horária vazaria. Janelas normais nunca são validadas: o que
importa medir é desempenho em evento.
"""

from __future__ import annotations

from collections.abc import Iterator

import pandas as pd

from ..core.contracts import hourly_index
from ..ingest.common import ROOT, load_config

PROCESSED = ROOT / "data" / "processed"


def carregar_dataset(codigo: int) -> pd.DataFrame:
    ds = pd.read_parquet(PROCESSED / f"dataset_{codigo}.parquet")
    return ds.set_index("ts_utc").sort_index()


def folds_por_evento(ds: pd.DataFrame) -> Iterator[tuple[str, pd.DataFrame, pd.DataFrame]]:
    hourly_index(ds.index)
    eventos = sorted(ds.loc[ds["tipo"] == "evento", "janela_id"].unique())
    for ev in eventos:
        test = ds[ds["janela_id"] == ev]
        train = ds[ds["janela_id"] != ev]
        yield ev, purgar(train, test), test


def purgar(train: pd.DataFrame, test: pd.DataFrame, lookback_h: int | None = None) -> pd.DataFrame:
    """Exclui intervalos de informação que cruzam o teste (inclusive bordas).

    Protege rótulos até o maior horizonte e o contexto horário de chuva.
    A CV continua retrospectiva; para simular emissão use treino_antes.
    """
    if train.empty or test.empty:
        return train.copy()
    h = max((int(c[2:-1]) for c in train if c.startswith("y_") and c.endswith("h")), default=0)
    lookback = max(load_config("features")["janelas_chuva_h"]) if lookback_h is None else lookback_h
    inicio = test.index.min() - pd.Timedelta(hours=lookback)
    fim = test.index.max() + pd.Timedelta(hours=h)
    fora = ((train.index + pd.Timedelta(hours=h) < inicio)
            | (train.index - pd.Timedelta(hours=lookback) > fim))
    return train.loc[fora].copy()
