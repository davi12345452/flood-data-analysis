"""Detecção de eventos e sorteio de janelas normais.

Evento = bloco contíguo de horas em que QUALQUER estação alvo está na cota de
atenção ou acima; blocos próximos (< fusao_gap_h) são fundidos. A janela
amostrada estende o bloco com antecedência (para as features de chuva longa)
e cauda (recessão).

Janelas normais são sorteadas com semente fixa fora dos eventos (com buffer),
para o modelo aprender o regime base sem afogar os eventos.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from ..ingest.common import REFERENCE, ROOT, load_config

INTERIM = ROOT / "data" / "interim"
PROCESSED = ROOT / "data" / "processed"


def detectar_eventos() -> pd.DataFrame:
    cfg = load_config("dataset")
    cotas = pd.read_csv(REFERENCE / "cotas_referencia.csv").set_index("codigo")
    ana = pd.read_parquet(INTERIM / "ana_hourly.parquet")

    acima_qualquer = []
    for alvo in cfg["alvos"]:
        g = ana[ana["codigo"] == alvo].set_index("ts_utc")
        limiar = float(cotas.loc[alvo, "atencao_cm"])
        acima = g["nivel_cm"] >= limiar
        acima_qualquer.append(acima[acima].index.to_series())
    horas_acima = pd.concat(acima_qualquer).sort_values().drop_duplicates()
    if horas_acima.empty:
        raise RuntimeError("Nenhuma hora acima da cota de atenção — algo errado.")

    gap = pd.Timedelta(hours=cfg["eventos"]["fusao_gap_h"])
    novo_bloco = horas_acima.diff() > gap
    bloco_id = novo_bloco.cumsum()
    eventos = []
    for _, horas in horas_acima.groupby(bloco_id):
        ini_acima, fim_acima = horas.min(), horas.max()
        eventos.append({
            "inicio_acima": ini_acima,
            "fim_acima": fim_acima,
            "janela_inicio": ini_acima - pd.Timedelta(hours=cfg["eventos"]["antecedencia_h"]),
            "janela_fim": fim_acima + pd.Timedelta(hours=cfg["eventos"]["cauda_h"]),
            "horas_acima": len(horas),
        })
    df = pd.DataFrame(eventos)
    df["evento_id"] = [f"ev{ini:%Y%m%d}" for ini in df["inicio_acima"]]

    # pico por estação alvo dentro de cada evento (para o relatório)
    for alvo in cfg["alvos"]:
        g = ana[ana["codigo"] == alvo].set_index("ts_utc")["nivel_cm"]
        picos = []
        for _, ev in df.iterrows():
            janela = g.loc[ev["janela_inicio"]:ev["janela_fim"]]
            picos.append(float(janela.max()) if janela.notna().any() else np.nan)
        df[f"pico_{alvo}"] = picos
    return df


def sortear_normais(eventos: pd.DataFrame) -> pd.DataFrame:
    cfg = load_config("dataset")["normais"]
    ana = pd.read_parquet(INTERIM / "ana_hourly.parquet")
    inicio_dados = ana["ts_utc"].min().ceil("D")
    fim_dados = ana["ts_utc"].max().floor("D") - pd.Timedelta(hours=cfg["duracao_h"])

    proibido = [(ev["janela_inicio"] - pd.Timedelta(hours=cfg["buffer_h"]),
                 ev["janela_fim"] + pd.Timedelta(hours=cfg["buffer_h"]))
                for _, ev in eventos.iterrows()]

    rng = np.random.default_rng(cfg["semente"])
    janelas = []
    for ano in range(inicio_dados.year, fim_dados.year + 1):
        sorteadas = 0
        tentativas = 0
        while sorteadas < cfg["por_ano"] and tentativas < 200:
            tentativas += 1
            base = pd.Timestamp(f"{ano}-01-01", tz="UTC")
            ini = base + pd.Timedelta(hours=int(rng.integers(0, 365 * 24 - cfg["duracao_h"])))
            fim = ini + pd.Timedelta(hours=cfg["duracao_h"])
            if ini < inicio_dados or fim > ana["ts_utc"].max():
                continue
            if any(ini <= p_fim and fim >= p_ini for p_ini, p_fim in proibido):
                continue
            if any(ini <= j["fim"] and fim >= j["inicio"] for j in janelas):
                continue
            janelas.append({"inicio": ini, "fim": fim,
                            "janela_id": f"nm{ini:%Y%m%d}"})
            sorteadas += 1
    return pd.DataFrame(janelas)


def run() -> None:
    eventos = detectar_eventos()
    normais = sortear_normais(eventos)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    eventos.to_parquet(PROCESSED / "eventos.parquet", index=False)
    normais.to_parquet(PROCESSED / "janelas_normais.parquet", index=False)

    # Lista de janelas para o download do MERGE horário (consumida por
    # src.ingest.merge run_windows)
    janelas = [
        {"nome": ev["evento_id"], "inicio": str(ev["janela_inicio"]),
         "fim": str(ev["janela_fim"])}
        for _, ev in eventos.iterrows()
    ] + [
        {"nome": j["janela_id"], "inicio": str(j["inicio"]), "fim": str(j["fim"])}
        for _, j in normais.iterrows()
    ]
    (PROCESSED / "janelas_amostradas.json").write_text(
        json.dumps(janelas, indent=2), encoding="utf-8"
    )
    total_h = sum(
        (pd.Timestamp(j["fim"]) - pd.Timestamp(j["inicio"])).total_seconds() / 3600
        for j in janelas
    )
    print(f"[dataset.events] {len(eventos)} eventos, {len(normais)} janelas normais, "
          f"~{total_h:.0f} horas amostradas")
    print(eventos[["evento_id", "inicio_acima", "fim_acima", "horas_acima"]
                  + [c for c in eventos.columns if c.startswith("pico_")]]
          .to_string(index=False))


if __name__ == "__main__":
    run()
