"""Agregação do MERGE recente por sub-bacia, para a janela do evento em curso.

A Fase 3 agrega apenas as janelas já catalogadas (eventos/amostras). Aqui a
janela é "agora": os GRIB2 recém-baixados viram uma partição `janela=live` no
mesmo formato, e a série diária do ano corrente é ATUALIZADA por acréscimo —
reprocessar o ano inteiro apagaria os meses cujo GRIB não está mais em cache.
"""

from __future__ import annotations

import datetime as dt

import pandas as pd

from ..ingest.common import RAW, ROOT
from ..spatial.merge_agg import RE_DIA, RE_HORA, PesosPorGrade, agregar_arquivo

INTERIM_MERGE = ROOT / "data" / "interim" / "merge"


def horaria_live(desde: pd.Timestamp) -> pd.Timestamp:
    """Agrega os GRIB2 horários >= desde em horaria/janela=live.parquet."""
    cache = PesosPorGrade()
    destino = INTERIM_MERGE / "horaria"
    destino.mkdir(parents=True, exist_ok=True)

    linhas, ilegiveis = [], []
    for a in sorted((RAW / "merge" / "hourly").rglob("*.grib2")):
        m = RE_HORA.search(a.name)
        if not m:
            continue
        rotulo = pd.Timestamp(dt.datetime.strptime(m.group(1), "%Y%m%d%H"), tz="UTC")
        if rotulo < desde:
            continue
        valores = agregar_arquivo(a, cache)
        if valores is None:
            ilegiveis.append(a.name)
            continue
        # rótulo do arquivo = FIM da acumulação horária; saída = início
        linhas.extend({"ts_utc": rotulo - pd.Timedelta(hours=1), "codigo": c,
                       "chuva_mm": v} for c, v in valores.items())
    df = pd.DataFrame(linhas)
    df.to_parquet(destino / "janela=live.parquet", index=False)
    print(f"[live.merge] horária: {len(df)} linhas até {df['ts_utc'].max()} "
          f"({len(ilegiveis)} ilegíveis)", flush=True)
    return df["ts_utc"].max()


def diaria_incremental() -> pd.Timestamp:
    """Processa os GRIB2 diários em cache e MESCLA com a partição do ano."""
    cache = PesosPorGrade()
    destino = INTERIM_MERGE / "diaria"
    por_ano: dict[int, list] = {}
    for a in sorted((RAW / "merge" / "daily").rglob("*.grib2")):
        m = RE_DIA.search(a.name)
        if m:
            por_ano.setdefault(int(m.group(1)[:4]), []).append(a)

    ultimo = None
    for ano, lista in sorted(por_ano.items()):
        linhas = []
        for a in lista:
            rotulo = pd.Timestamp(
                dt.datetime.strptime(RE_DIA.search(a.name).group(1), "%Y%m%d"), tz="UTC")
            valores = agregar_arquivo(a, cache)
            if valores is None:
                continue
            inicio = rotulo + pd.Timedelta(hours=12) - pd.Timedelta(hours=24)
            linhas.extend({"ts_utc": inicio, "codigo": c, "chuva_mm": v}
                          for c, v in valores.items())
        novo = pd.DataFrame(linhas)
        out = destino / f"ano={ano}.parquet"
        if out.exists():
            antigo = pd.read_parquet(out)
            novo = pd.concat([antigo, novo], ignore_index=True)
            # o recém-agregado vence em caso de reprocessamento do mesmo dia
            novo = novo.drop_duplicates(subset=["ts_utc", "codigo"], keep="last")
        novo = novo.sort_values(["ts_utc", "codigo"])
        novo.to_parquet(out, index=False)
        ultimo = novo["ts_utc"].max()
        print(f"[live.merge] diária {ano}: até {ultimo}", flush=True)
    return ultimo
