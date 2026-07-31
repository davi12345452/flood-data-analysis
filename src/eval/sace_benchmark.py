"""Baseline 4: as previsões oficiais do SACE contra a cota observada (ANA).

Compara cada previsão em prosa (com horizonte explícito) com o nível
observado no timestamp alvo. Anexa a seção ao reports/06_baselines.md.
"""

from __future__ import annotations

import pandas as pd

from ..ingest.common import ROOT
from . import metrics

INTERIM = ROOT / "data" / "interim"
REPORT = ROOT / "reports" / "06_baselines.md"

NOMES = {86510000: "Muçum", 86720000: "Encantado", 86879300: "Estrela"}


def avaliar() -> pd.DataFrame:
    prev = pd.read_parquet(INTERIM / "sace_previsoes.parquet")
    prev = prev[prev["horizonte_h"].notna() & prev["codigo"].isin(NOMES)]
    ana = pd.read_parquet(INTERIM / "ana_hourly.parquet")

    linhas = []
    for codigo, grupo in prev.groupby("codigo"):
        serie = (ana[ana["codigo"] == codigo]
                 .set_index("ts_utc")["nivel_cm"].sort_index())
        alvo_hora = grupo["alvo_utc"].dt.round("h")
        obs = serie.reindex(alvo_hora).to_numpy(dtype=float)
        g = grupo.assign(obs_cm=obs)
        for hz, sub in g.groupby("horizonte_h"):
            linhas.append({
                "alvo": NOMES[codigo],
                "horizonte_h": int(hz),
                **metrics.resumo(sub["obs_cm"], sub["prevista_cm"]),
            })
    return pd.DataFrame(linhas).sort_values(["alvo", "horizonte_h"])


def run() -> None:
    tabela = avaliar()
    t = tabela.copy()
    for c in ("NSE", "KGE"):
        t[c] = t[c].round(3)
    for c in ("RMSE_cm", "MAE_cm"):
        t[c] = t[c].round(1)
    t["cobertura"] = (t["cobertura"] * 100).round(1)

    secao = f"""

## Baseline 4 — Previsões oficiais do SACE (benchmark externo)

Previsões em prosa (2022+, horizonte explícito de 4-6h) comparadas com a cota
observada da ANA no timestamp alvo. São previsões emitidas EM EVENTOS (o SACE
só publica boletim quando o rio ameaça), então o regime é o difícil — não
compare diretamente com as métricas pooled acima, que incluem recessões e
antecedências; a comparação justa (mesmas horas) fica para a Fase 8.

{t.to_markdown(index=False)}

Interpretação: MAE de ~30-60 cm em horizonte de 4-6h emitida durante eventos é
a régua operacional. O modelo da Fase 7, avaliado NAS MESMAS horas de emissão,
precisa entregar erro comparável ou menor.
"""
    with REPORT.open("a", encoding="utf-8") as f:
        f.write(secao)
    print(tabela.round(3).to_string(index=False))
    print(f"[sace_benchmark] seção anexada a {REPORT}")


if __name__ == "__main__":
    run()
