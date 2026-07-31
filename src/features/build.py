"""Montagem do frame de features horário (pool completo).

A Fase 5 recorta este frame nas janelas amostradas e seleciona o subconjunto
por estação alvo. Chuva horária só existe onde o MERGE horário foi baixado —
a Fase 5 garante o download para TODA janela amostrada, para que nenhuma
feature seja sistematicamente ausente fora de eventos (o que vazaria a
informação "isto é um evento" pela máscara de NaN).
"""

from __future__ import annotations

import pandas as pd

from ..ingest.common import REFERENCE, ROOT, load_config
from . import dams, level, rain

PROCESSED = ROOT / "data" / "processed"

APELIDO_ESTACAO = {
    86472000: "jj",   # Linha José Julio (Antas)
    86472600: "st",   # Santa Tereza
    86510000: "mu",   # Muçum
    86720000: "en",   # Encantado
    86879300: "es",   # Estrela
    86895000: "pm",   # Porto Mariante
    86950000: "tq",   # Taquari
}


def montar() -> pd.DataFrame:
    cfg = load_config("features")
    cotas = pd.read_csv(REFERENCE / "cotas_referencia.csv").set_index("codigo")

    # 1. Chuva: acumulados horários (onde há MERGE horário) + API diário (sempre)
    horaria = rain.carregar_macro_horaria()
    ac = rain.acumulados(horaria, cfg["janelas_chuva_h"])
    diaria = rain.carregar_macro_diaria()
    api = rain.api_diaria(diaria, cfg["api_decaimentos"])

    # 2. Cota + disponibilidade + tempo desde atenção, por estação
    ana = level.carregar_ana()
    blocos = [ac]
    for codigo, apelido in APELIDO_ESTACAO.items():
        g = ana[ana["codigo"] == codigo]
        if g.empty:
            continue
        limiar = float(cotas.loc[codigo, "atencao_cm"]) if codigo in cotas.index else None
        bloco = level.features_estacao(
            g, limiar, cfg["tempo_desde_atencao_cap_h"], cfg["disponibilidade_janela_h"]
        )
        bloco.columns = [f"{c}_{apelido}" for c in bloco.columns]
        blocos.append(bloco)

    # 3. UHEs
    blocos.append(dams.features_uhes(dams.carregar_ons()))

    frame = pd.concat(blocos, axis=1).sort_index()
    frame = frame.join(rain.juntar_api_em_horas(api, frame.index))
    frame.index.name = "ts_utc"
    return frame


def run() -> None:
    frame = montar()
    PROCESSED.mkdir(parents=True, exist_ok=True)
    out = PROCESSED / "features_hourly.parquet"
    frame.reset_index().to_parquet(out, index=False)
    n_chuva = frame.filter(like="chuva_").notna().any(axis=1).sum()
    print(f"[features] {frame.shape[0]} horas × {frame.shape[1]} features em {out}")
    print(f"[features] horas com chuva horária disponível: {n_chuva} "
          f"(janelas de eventos; Fase 5 amplia por amostra)")


if __name__ == "__main__":
    run()
