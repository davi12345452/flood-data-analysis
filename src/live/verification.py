"""Conferência de emissões arquivadas; replays nunca contam como emissões."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .operational import ALVOS

COLUNAS = ["execucao", "alvo", "codigo", "h", "motor", "emitido_em_utc",
           "valido_para_utc", "previsto_cm", "observado_cm", "erro_cm"]


def conferir(frame: pd.DataFrame, pasta: Path, agora: pd.Timestamp) -> pd.DataFrame:
    linhas = []
    for arquivo in sorted(pasta.glob("emissao_*/previsoes.parquet")):
        previsoes = pd.read_parquet(arquivo)
        for p in previsoes.itertuples(index=False):
            if (p.modo != "emissao" or pd.isna(p.emitido_em_utc)
                    or not p.emitido_em_utc < p.valido_para_utc <= agora
                    or p.codigo not in ALVOS or pd.isna(p.previsto_cm)):
                continue
            ap = ALVOS[p.codigo][1]
            observado = frame[f"nivel_{ap}"].get(p.valido_para_utc, float("nan"))
            if pd.isna(observado):
                continue
            linhas.append({"execucao": arquivo.parent.name, "alvo": p.alvo, "codigo": p.codigo,
                           "h": p.h, "motor": p.motor, "emitido_em_utc": p.emitido_em_utc,
                           "valido_para_utc": p.valido_para_utc, "previsto_cm": p.previsto_cm,
                           "observado_cm": observado, "erro_cm": p.previsto_cm - observado})
    return pd.DataFrame(linhas, columns=COLUNAS)
