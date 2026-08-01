"""Ingestão dos dados hidráulicos por reservatório do ONS (CKAN + S3).

Datasets:
- dados_hidrologicos_ho: base horária, Parquet mensal, desde 2019.
- dados-hidrologicos-res: base diária, histórico mais longo.

Os arquivos são baixados como vieram (todos os reservatórios do SIN); o filtro
para as usinas da CERAN acontece na Fase 2. Dados NÃO consistidos pelo ONS.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import time

import pandas as pd

from .common import (
    RAW,
    get,
    is_cached,
    is_partial,
    load_config,
    make_client,
    write_meta,
)


def fetch_catalog(client, ckan_base: str, dataset: str) -> list[dict]:
    resp = get(client, f"{ckan_base}/package_show", params={"id": dataset})
    payload = resp.json()
    if not payload.get("success"):
        raise RuntimeError(f"CKAN package_show falhou para {dataset}: {payload}")
    resources = payload["result"]["resources"]
    dest = RAW / "ons" / dataset / "_catalog.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(resources, indent=2, ensure_ascii=False), encoding="utf-8")
    write_meta(dest, url=f"{ckan_base}/package_show", params={"id": dataset},
               n_records=len(resources))
    return resources


def _era_atual(name: str, hoje: dt.date) -> bool:
    """Recurso do mês/ano corrente ainda cresce — marcar como parcial."""
    m = re.search(r"(\d{4})[-_](\d{2})", name)
    if m:
        return (int(m.group(1)), int(m.group(2))) == (hoje.year, hoje.month)
    m = re.search(r"(\d{4})", name)
    return bool(m) and int(m.group(1)) == hoje.year


def run() -> None:
    cfg = load_config("ingest")
    ckan_base = cfg["ons"]["ckan_base"]
    hoje = dt.date.today()

    with make_client() as client:
        for dataset in cfg["ons"]["datasets"]:
            resources = fetch_catalog(client, ckan_base, dataset)
            parquets = [r for r in resources if r.get("format", "").upper() == "PARQUET"]
            baixados = pulados = 0
            for res in parquets:
                nome = re.sub(r"[^A-Za-z0-9_.-]", "_", res["name"]) + ".parquet"
                dest = RAW / "ons" / dataset / nome
                if is_cached(dest) and not is_partial(dest):
                    pulados += 1
                    continue
                resp = get(client, res["url"])
                dest.parent.mkdir(parents=True, exist_ok=True)
                tmp = dest.with_name(dest.name + ".tmp")
                tmp.write_bytes(resp.content)
                tmp.rename(dest)
                try:
                    n = len(pd.read_parquet(dest))
                except Exception as exc:  # arquivo corrompido no S3: reportar, não engolir
                    dest.unlink()
                    raise RuntimeError(f"Parquet ilegível de {res['url']}: {exc}") from exc
                write_meta(dest, url=res["url"], n_records=n,
                           partial=_era_atual(res["name"], hoje))
                baixados += 1
                time.sleep(0.1)
            print(f"[ons] {dataset}: baixados={baixados} pulados(cache)={pulados} "
                  f"(de {len(parquets)} recursos parquet)", flush=True)


if __name__ == "__main__":
    run()
