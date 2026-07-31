"""Relatório de cobertura da Fase 1 (reports/01_cobertura.md).

Para cada estação/fonte: período disponível, percentual de lacunas na grade
de 15 min (ANA) ou horária (ONS), e resolução temporal real (mediana do
intervalo entre registros). Zeros de nível são contados à parte: pela
Armadilha 0 eles são falha de sensor, não medição.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd

from .common import RAW, ROOT, load_config

REPORT = ROOT / "reports" / "01_cobertura.md"


def _resolucao_minutos(serie_dt: pd.Series) -> float | None:
    difs = serie_dt.sort_values().diff().dropna()
    return difs.median().total_seconds() / 60 if len(difs) else None


def cobertura_ana() -> pd.DataFrame:
    estacoes = {e["codigo"]: e["nome"] for e in load_config("stations")["estacoes_fluviometricas"]}
    linhas = []
    for codigo, nome in estacoes.items():
        arquivos = sorted((RAW / "ana_soap" / f"estacao={codigo}").rglob("*.parquet"))
        if not arquivos:
            linhas.append({"estacao": nome, "codigo": codigo, "status": "SEM DADOS"})
            continue
        df = pd.concat((pd.read_parquet(a) for a in arquivos), ignore_index=True)
        df["dt"] = pd.to_datetime(df["DataHora"], errors="coerce")
        df = df.dropna(subset=["dt"]).drop_duplicates(subset="dt")
        res_min = _resolucao_minutos(df["dt"])
        periodo = (df["dt"].max() - df["dt"].min())
        esperados = periodo.total_seconds() / (15 * 60) + 1
        nivel_validos = df["Nivel"].notna() & (df["Nivel"] != 0)
        linhas.append({
            "estacao": nome,
            "codigo": codigo,
            "inicio": df["dt"].min(),
            "fim": df["dt"].max(),
            "registros": len(df),
            "lacunas_grade_15min_pct": round(100 * (1 - len(df) / esperados), 1),
            "nivel_zero_ou_nan_pct": round(100 * (1 - nivel_validos.mean()), 1),
            "resolucao_mediana_min": res_min,
        })
    return pd.DataFrame(linhas)


def cobertura_ons() -> pd.DataFrame:
    usinas = [u["nome_ons"] for u in load_config("stations")["usinas_ceran"]]
    arquivos = sorted((RAW / "ons" / "dados_hidrologicos_ho").glob("*.parquet"))
    if not arquivos:
        return pd.DataFrame()
    df = pd.concat(
        (pd.read_parquet(a, columns=["nom_reservatorio", "din_instante", "val_vazaodefluente"])
         for a in arquivos),
        ignore_index=True,
    )
    # A partir de 2026-02 o ONS passou a preencher nom_reservatorio com
    # espaços extras — normalizar antes de filtrar (idem na Fase 2).
    df["nom_reservatorio"] = df["nom_reservatorio"].str.strip()
    df = df[df["nom_reservatorio"].isin(usinas)]
    df["dt"] = pd.to_datetime(df["din_instante"], errors="coerce")
    linhas = []
    for usina, grupo in df.groupby("nom_reservatorio"):
        grupo = grupo.dropna(subset=["dt"]).drop_duplicates(subset="dt")
        horas = (grupo["dt"].max() - grupo["dt"].min()).total_seconds() / 3600 + 1
        linhas.append({
            "usina": usina,
            "inicio": grupo["dt"].min(),
            "fim": grupo["dt"].max(),
            "registros": len(grupo),
            "lacunas_grade_horaria_pct": round(100 * (1 - len(grupo) / horas), 1),
            "defluente_nan_pct": round(100 * grupo["val_vazaodefluente"].isna().mean(), 1),
            "resolucao_mediana_min": _resolucao_minutos(grupo["dt"]),
        })
    return pd.DataFrame(linhas)


def cobertura_merge() -> dict:
    diarios = list((RAW / "merge" / "daily").rglob("*.grib2"))
    horarios = list((RAW / "merge" / "hourly").rglob("*.grib2"))
    cfg = load_config("ingest")
    inicio = dt.date.fromisoformat(cfg["periodo"]["inicio"])
    dias_esperados = (dt.date.today() - dt.timedelta(days=1) - inicio).days + 1
    horas_eventos = sum(
        ((dt.datetime.fromisoformat(e["fim"]) - dt.datetime.fromisoformat(e["inicio"])).days + 1) * 24
        for e in cfg["janelas_eventos"]
    )
    return {
        "diarios": len(diarios), "diarios_esperados": dias_esperados,
        "horarios_eventos": len(horarios), "horarios_esperados": horas_eventos,
    }


def cobertura_sace() -> pd.DataFrame:
    idx = RAW / "sace" / "index.parquet"
    if not idx.exists():
        return pd.DataFrame()
    indice = pd.read_parquet(idx).dropna(subset=["emissao"])
    baixados = {p.name for p in (RAW / "sace" / "boletins").rglob("*.pdf")}
    indice["baixado"] = indice["arquivo"].isin(baixados)
    resumo = indice.groupby(indice["emissao"].dt.year).agg(
        boletins=("arquivo", "count"), baixados=("baixado", "sum")
    )
    return resumo.reset_index(names="ano")


def _tabela(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False) if not df.empty else "_sem dados_"


def run() -> None:
    ana, ons, mrg, sace = cobertura_ana(), cobertura_ons(), cobertura_merge(), cobertura_sace()
    gerado = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    corpo = f"""# Fase 1 — Relatório de cobertura

Gerado em {gerado} a partir do cache local (`data/raw/`). Reexecutável com
`make coverage`.

## ANA — SOAP legado (telemetriaws1), grade nominal de 15 min

Percentual de "nível zero ou ausente" reportado à parte: pela Armadilha 0,
zero de nível é falha de sensor, não medição.

{_tabela(ana)}

## ONS — dados_hidrologicos_ho (usinas CERAN), grade horária

{_tabela(ons)}

## MERGE/CPTEC (GRIB2)

- Diários: {mrg["diarios"]} de {mrg["diarios_esperados"]} esperados no período de modelagem
- Horários (janelas de eventos): {mrg["horarios_eventos"]} de ~{mrg["horarios_esperados"]} esperados

## SACE — boletins por ano de emissão

{_tabela(sace)}
"""
    REPORT.write_text(corpo, encoding="utf-8")
    print(f"[coverage] relatório em {REPORT}")


if __name__ == "__main__":
    run()
