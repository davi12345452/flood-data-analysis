"""Relatório de QC (reports/02_qc.md) a partir de data/interim/."""

from __future__ import annotations

import datetime as dt

import pandas as pd

from ..ingest.common import ROOT, load_config

INTERIM = ROOT / "data" / "interim"
REPORT = ROOT / "reports" / "02_qc.md"


def resumo_flags_ana(ana: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for (codigo, estacao), g in ana.groupby(["codigo", "estacao"]):
        linhas.append({
            "estacao": estacao,
            "horas": len(g),
            "nivel_valido_pct": round(100 * g["nivel_cm"].notna().mean(), 1),
            "nivel_zero_pct": round(100 * g["flag_nivel_zero"].mean(), 2),
            "stuck_pct": round(100 * g["flag_stuck"].mean(), 2),
            "spike_n": int(g["flag_spike"].sum()),
            "fora_ordem_n": int(g["flag_fora_de_ordem"].sum()),
            "dst_incerto_pct": round(100 * g["flag_dst_incerto"].mean(), 1),
        })
    return pd.DataFrame(linhas)


def disponibilidade_eventos(ana: pd.DataFrame) -> pd.DataFrame:
    """A tabela da Armadilha 0: % de horas com nível válido em cada evento."""
    eventos = load_config("ingest")["janelas_eventos"]
    linhas = []
    for ev in eventos:
        ini = pd.Timestamp(ev["inicio"], tz="UTC")
        fim = pd.Timestamp(ev["fim"], tz="UTC") + pd.Timedelta(hours=23)
        janela = ana[(ana["ts_utc"] >= ini) & (ana["ts_utc"] <= fim)]
        horas_esperadas = int((fim - ini).total_seconds() // 3600) + 1
        for estacao, g in janela.groupby("estacao"):
            linhas.append({
                "evento": ev["nome"],
                "estacao": estacao,
                "nivel_valido_pct": round(100 * g["nivel_cm"].notna().sum() / horas_esperadas, 1),
            })
    tabela = pd.DataFrame(linhas)
    return tabela.pivot(index="estacao", columns="evento", values="nivel_valido_pct").reset_index()


def resumo_ons(ons: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for usina, g in ons.groupby("usina"):
        linhas.append({
            "usina": usina,
            "horas": len(g),
            "defluente_valido_pct": round(100 * g["defluente_m3s"].notna().mean(), 1),
            "defluente_zero_pct": round(100 * g["flag_defluente_zero"].mean(), 2),
            "stuck_pct": round(100 * g["flag_stuck"].mean(), 2),
            "dst_incerto_pct": round(100 * g["flag_dst_incerto"].mean(), 1),
            "pos_rompimento_h": int(g["flag_pos_rompimento"].sum()),
        })
    return pd.DataFrame(linhas)


def run() -> None:
    ana = pd.read_parquet(INTERIM / "ana_hourly.parquet")
    ons = pd.read_parquet(INTERIM / "ons_hourly.parquet")
    gerado = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")

    corpo = f"""# Fase 2 — QC e alinhamento temporal

Gerado em {gerado} por `make qc-report`. Fonte: `data/interim/*.parquet`.

## Decisões de fuso horário (a parte que destrói projetos em silêncio)

| Fonte | Fuso dos timestamps brutos | Evidência |
|---|---|---|
| ANA SOAP | **UTC-3 fixo** | Cota de 1065 cm às 18:00 de 28/07/2026 no SOAP = valor declarado no boletim SACE para 18:00 local |
| ONS horário | **UTC-3 fixo** | Cross-correlação defluência 14 de Julho × vazão ANA José Júlio: máximo em lag 0 (r=0,998), picos coincidentes em 04/09/2023 22:00 |
| MERGE | UTC | Documentação CPTEC |

Convenção do ONS: "hora fim" (registro 01:00 = intervalo 00:00-00:59, conforme
dicionário oficial) — rótulos deslocados para o início do período no interim.

Incerteza residual: nas janelas de horário de verão (até fev/2019) as fontes
podem ter seguido o horário oficial (UTC-2). Como não há como verificar
retroativamente, as horas afetadas carregam `flag_dst_incerto` (±1h). Nenhum
dos eventos de referência (2023-2024) é afetado.

## Regras de agregação para a grade horária (UTC, rótulo = início do período)

| Variável | Regra | Racional |
|---|---|---|
| nivel_cm, vazao_m3s | instantâneo no topo da hora | média suavizaria picos — inaceitável para cheia |
| chuva_mm | soma das amostras de 15 min na hora (`chuva_n` conta quantas) | chuva é fluxo acumulado |
| disp_nivel | fração das 4 amostras com nível válido | Armadilha 0: disponibilidade é variável de primeira classe |
| Lacunas | **permanecem NaN — nenhuma interpolação** | Armadilha 0: interpolar lacuna de cheia fabrica picos suavizados |

## ANA — flags por estação (grade horária)

{resumo_flags_ana(ana).to_markdown(index=False)}

`nivel_zero_pct` = horas com pelo menos um zero de nível marcado (vira NaN).
`spike_n` = variações >200 cm/15min entre amostras regulares (máx. real
observado nos eventos: 77 cm). `stuck_pct` = nível idêntico por ≥6h.

## Armadilha 0 medida — % de horas com nível válido por evento

{disponibilidade_eventos(ana).to_markdown(index=False)}

## ONS — usinas CERAN (grade horária)

{resumo_ons(ons).to_markdown(index=False)}

Durante o pico de maio/2024 (01-03/05) as três usinas transmitiram só ~9 de 72
horas — o preditor de montante desaparece exatamente no maior evento
(Armadilhas 0 e 6 combinadas). `flag_pos_rompimento` cobre a 14 de Julho de
2024-05-01 a 2024-12-31.

Nota sobre `stuck_pct` (13-24%): defluência idêntica por ≥12h em usina a fio
d'água pode ser despacho constante legítimo ou réplica preguiçosa do agente —
o feed não é consistido. A flag informa; não é motivo de exclusão automática.
"""
    REPORT.write_text(corpo, encoding="utf-8")
    print(f"[qc.report] relatório em {REPORT}")


if __name__ == "__main__":
    run()
