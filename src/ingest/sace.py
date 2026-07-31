"""Ingestão dos boletins do SACE Taquari (SGB/CPRM).

O índice boletins.php?idbacia=9 lista todos os PDFs (a paginação é só no
cliente). Cada boletim traz cotas observadas e a previsão oficial da época —
o benchmark externo do projeto. Fase 1 materializa índice + PDFs brutos;
a extração das tabelas de dentro dos PDFs acontece quando os baselines
(Fase 6) precisarem delas.

Scraping educado: rate limit configurável e user-agent identificável.
"""

from __future__ import annotations

import re
import time
from urllib.parse import quote

import pandas as pd

from .common import RAW, download_binary, get, load_config, make_client, write_parquet

RE_LINK = re.compile(r"href='(boletins/Taquari/([^']+\.pdf))'")
RE_EMISSAO = re.compile(r"^(\d{8})_(\d{1,2})")


def parse_index(html: str) -> pd.DataFrame:
    """Extrai (arquivo, data/hora de emissão) dos links do índice."""
    linhas = []
    for caminho, nome in RE_LINK.findall(html):
        m = RE_EMISSAO.match(nome)
        emissao = None
        if m:
            try:
                emissao = pd.Timestamp(
                    f"{m.group(1)[:4]}-{m.group(1)[4:6]}-{m.group(1)[6:8]} "
                    f"{int(m.group(2)):02d}:00"
                )
            except ValueError:
                pass  # nome fora do padrão: mantém no índice com emissão nula
        linhas.append({"arquivo": nome, "caminho": caminho, "emissao": emissao})
    df = pd.DataFrame(linhas, columns=["arquivo", "caminho", "emissao"])
    return df.drop_duplicates(subset="arquivo").reset_index(drop=True)


def run() -> None:
    cfg = load_config("ingest")["sace"]
    with make_client() as client:
        resp = get(client, cfg["index_url"])
        indice = parse_index(resp.text)
        if indice.empty:
            raise RuntimeError(
                "Índice do SACE não devolveu nenhum boletim — layout mudou? "
                f"(HTTP {resp.status_code}, {len(resp.text)} bytes)"
            )
        # O índice é re-raspado a cada execução (boletins novos aparecem).
        write_parquet(
            indice, RAW / "sace" / "index.parquet",
            url=cfg["index_url"], partial=True,
        )
        print(f"[sace] índice: {len(indice)} boletins", flush=True)

        baixados = pulados = 0
        for _, linha in indice.iterrows():
            ano = linha["emissao"].year if pd.notna(linha["emissao"]) else "sem_data"
            dest = RAW / "sace" / "boletins" / str(ano) / linha["arquivo"]
            url = cfg["base_url"] + quote(linha["caminho"])
            if download_binary(client, url, dest):
                baixados += 1
                time.sleep(cfg["pausa_s"])
            else:
                pulados += 1
    print(f"[sace] PDFs: baixados={baixados} pulados(cache)={pulados}")


if __name__ == "__main__":
    run()
