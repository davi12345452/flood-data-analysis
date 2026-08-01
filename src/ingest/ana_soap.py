"""Ingestão do webservice SOAP legado da ANA (telemetriaws1).

Série telemétrica de ~15 min com cota (cm), vazão (m³/s) e chuva (mm), sem
credencial. Particionado por estação/ano/mês em data/raw/ana_soap/.

Valores são materializados como vieram (zeros travados, lacunas e tudo mais):
QC é responsabilidade da Fase 2. DataHora fica como string — o fuso do serviço
ainda não foi confirmado e a conversão acontece numa única fronteira na Fase 2.
"""

from __future__ import annotations

import datetime as dt
import sys
import time
import xml.etree.ElementTree as ET

import pandas as pd

from .common import (
    RAW,
    get,
    is_cached,
    is_partial,
    load_config,
    make_client,
    month_ranges,
    write_parquet,
)

CAMPOS = ["CodEstacao", "DataHora", "Vazao", "Nivel", "Chuva"]


def parse_dados_xml(text: str) -> pd.DataFrame:
    """Extrai os registros do DataSet .NET devolvido pelo serviço."""
    root = ET.fromstring(text)
    linhas = []
    for el in root.iter():
        if el.tag.endswith("DadosHidrometereologicos"):
            reg = {}
            for filho in el:
                tag = filho.tag.split("}")[-1]
                if tag in CAMPOS:
                    reg[tag] = (filho.text or "").strip() or None
            if reg:
                linhas.append(reg)
    df = pd.DataFrame(linhas, columns=CAMPOS)
    for col in ("Vazao", "Nivel", "Chuva"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def fetch_month(client, base_url: str, codigo: int, ini: dt.date, fim: dt.date) -> pd.DataFrame:
    params = {
        "codEstacao": str(codigo),
        "dataInicio": ini.strftime("%d/%m/%Y"),
        "dataFim": fim.strftime("%d/%m/%Y"),
    }
    resp = get(client, f"{base_url}/DadosHidrometeorologicos", params=params)
    return parse_dados_xml(resp.text)


def run(codigos: list[int] | None = None) -> None:
    cfg = load_config("ingest")
    estacoes = load_config("stations")["estacoes_fluviometricas"]
    if codigos is None:
        codigos = [e["codigo"] for e in estacoes]
    inicio = dt.date.fromisoformat(cfg["periodo"]["inicio"])
    hoje = dt.date.today()
    base_url = cfg["ana_soap"]["base_url"]
    pausa = cfg["ana_soap"]["pausa_s"]

    baixados = pulados = vazios = 0
    falhas: list[str] = []
    with make_client() as client:
        for codigo in codigos:
            for ini, fim in month_ranges(inicio, hoje):
                dest = (
                    RAW / "ana_soap" / f"estacao={codigo}"
                    / f"ano={ini.year}" / f"mes={ini.month:02d}.parquet"
                )
                mes_corrente = (ini.year, ini.month) == (hoje.year, hoje.month)
                if is_cached(dest) and not is_partial(dest):
                    pulados += 1
                    continue
                try:
                    df = fetch_month(client, base_url, codigo, ini, fim)
                except Exception as exc:
                    # Serviço legado instável (504/timeout): registrar e seguir.
                    # O mês fica sem cache e será retentado na próxima execução.
                    falhas.append(f"{codigo} {ini:%Y-%m}: {type(exc).__name__}: {exc}")
                    print(f"[ana_soap] FALHA {codigo} {ini:%Y-%m} — segue adiante", flush=True)
                    continue
                write_parquet(
                    df,
                    dest,
                    url=f"{base_url}/DadosHidrometeorologicos",
                    params={
                        "codEstacao": str(codigo),
                        "dataInicio": ini.strftime("%d/%m/%Y"),
                        "dataFim": fim.strftime("%d/%m/%Y"),
                    },
                    partial=mes_corrente,
                )
                baixados += 1
                if df.empty:
                    vazios += 1
                time.sleep(pausa)
            print(f"[ana_soap] estação {codigo}: ok", flush=True)
    print(f"[ana_soap] baixados={baixados} pulados(cache)={pulados} vazios={vazios} "
          f"falhas={len(falhas)}")
    if falhas:
        log = RAW / "ana_soap" / "falhas_ultimo_run.txt"
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text("\n".join(falhas) + "\n", encoding="utf-8")
        print(f"[ana_soap] meses com falha registrados em {log} — reexecute para retentar")


if __name__ == "__main__":
    codigos = [int(c) for c in sys.argv[1:]] or None
    run(codigos)
