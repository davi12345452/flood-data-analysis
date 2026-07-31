"""Features das UHEs CERAN (defluência horária do ONS).

Usinas a fio d'água sem regularização: a defluência é observação de vazão de
montante, não variável de controle. A 14 de Julho, última da cascata, carrega
o sinal integrado — as derivadas ficam só nela para conter a contagem.
"""

from __future__ import annotations

import pandas as pd

from ..ingest.common import ROOT

INTERIM = ROOT / "data" / "interim"

APELIDOS = {"MONTE CLARO": "mc", "CASTRO ALVES": "ca", "14 DE JULHO": "qj"}


def carregar_ons() -> pd.DataFrame:
    return pd.read_parquet(INTERIM / "ons_hourly.parquet")


def features_uhes(ons: pd.DataFrame) -> pd.DataFrame:
    """defluente das 3 usinas + derivadas (1h, 3h) da 14 de Julho."""
    blocos = []
    for usina, apelido in APELIDOS.items():
        g = (ons[ons["usina"] == usina]
             .drop_duplicates(subset="ts_utc")
             .set_index("ts_utc").sort_index())
        # Grade contínua: sem isso, diff atravessa lacunas de transmissão
        # (ex.: o apagão de maio/2024) como se fossem 1h.
        g = g.reindex(pd.date_range(g.index.min(), g.index.max(), freq="h"))
        serie = g["defluente_m3s"].astype(float)
        bloco = pd.DataFrame({f"defluente_{apelido}": serie})
        if apelido == "qj":
            bloco[f"ddefluente_{apelido}_1h"] = serie.diff(1)
            bloco[f"ddefluente_{apelido}_3h"] = serie.diff(3) / 3
        blocos.append(bloco)
    return pd.concat(blocos, axis=1).sort_index()
