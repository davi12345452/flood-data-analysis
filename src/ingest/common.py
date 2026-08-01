"""Infraestrutura comum de ingestão: HTTP com retry, cache e proveniência.

Regras do projeto que este módulo garante:
- Cache agressivo: nada é rebaixado se já existe em data/raw/ com .meta.json.
- Proveniência: todo arquivo materializado ganha um .meta.json ao lado com
  URL de origem, timestamp UTC do download, parâmetros e contagem de registros.
- Idempotência: escrita atômica (tmp + rename); rodar duas vezes não corrompe.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import httpx
import pandas as pd
import yaml
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
REFERENCE = ROOT / "data" / "reference"
CONFIG_DIR = ROOT / "config"


def load_config(name: str) -> dict:
    return yaml.safe_load((CONFIG_DIR / f"{name}.yaml").read_text(encoding="utf-8"))


def utcnow_iso() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def make_client(timeout_s: float | None = None) -> httpx.Client:
    cfg = load_config("ingest")["http"]
    return httpx.Client(
        headers={"User-Agent": cfg["user_agent"]},
        timeout=timeout_s or cfg["timeout_s"],
        follow_redirects=True,
    )


class TransientHTTPError(Exception):
    """Erro que vale a pena tentar de novo (5xx, timeout, conexão)."""


@retry(
    stop=stop_after_attempt(8),
    wait=wait_exponential(multiplier=2, min=5, max=180),
    retry=retry_if_exception_type(TransientHTTPError),
    reraise=True,
)
def get(client: httpx.Client, url: str, params: dict | None = None) -> httpx.Response:
    """GET com retry exponencial. 4xx não é retentado (erro real, reportar)."""
    try:
        resp = client.get(url, params=params)
    except (httpx.TransportError, httpx.TimeoutException) as exc:
        raise TransientHTTPError(f"{type(exc).__name__}: {exc}") from exc
    if resp.status_code >= 500:
        raise TransientHTTPError(f"HTTP {resp.status_code} em {url}")
    resp.raise_for_status()
    return resp


def meta_path(dest: Path) -> Path:
    return dest.with_name(dest.name + ".meta.json")


def is_cached(dest: Path) -> bool:
    """Um artefato só conta como baixado se o arquivo E o meta existem."""
    return dest.exists() and meta_path(dest).exists()


def is_partial(dest: Path) -> bool:
    """Meta marcado como parcial (ex.: mês corrente) deve ser rebaixado."""
    mp = meta_path(dest)
    if not mp.exists():
        return False
    try:
        return bool(json.loads(mp.read_text(encoding="utf-8")).get("partial", False))
    except (json.JSONDecodeError, OSError):
        return True


def write_meta(
    dest: Path,
    *,
    url: str,
    params: dict | None = None,
    n_records: int | None = None,
    partial: bool = False,
    extra: dict | None = None,
) -> None:
    meta = {
        "url": url,
        "params": params or {},
        "downloaded_at_utc": utcnow_iso(),
        "n_records": n_records,
        "size_bytes": dest.stat().st_size,
        "partial": partial,
    }
    if extra:
        meta.update(extra)
    meta_path(dest).write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def write_parquet(
    df: pd.DataFrame,
    dest: Path,
    *,
    url: str,
    params: dict | None = None,
    partial: bool = False,
    extra: dict | None = None,
) -> None:
    """Escrita atômica de Parquet + meta de proveniência."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".tmp")
    df.to_parquet(tmp, index=False)
    tmp.rename(dest)
    write_meta(dest, url=url, params=params, n_records=len(df), partial=partial, extra=extra)


def download_binary(
    client: httpx.Client,
    url: str,
    dest: Path,
    *,
    params: dict | None = None,
    extra: dict | None = None,
) -> bool:
    """Baixa um arquivo binário (PDF, GRIB2). Retorna False se já estava em cache."""
    if is_cached(dest) and not is_partial(dest):
        return False
    resp = get(client, url, params=params)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".tmp")
    tmp.write_bytes(resp.content)
    tmp.rename(dest)
    write_meta(dest, url=url, params=params, extra=extra)
    return True


def month_ranges(start: dt.date, end: dt.date) -> list[tuple[dt.date, dt.date]]:
    """Pares (primeiro dia, último dia) de cada mês entre start e end, inclusive."""
    out: list[tuple[dt.date, dt.date]] = []
    cur = start.replace(day=1)
    while cur <= end:
        nxt = (cur.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
        out.append((max(cur, start), min(nxt - dt.timedelta(days=1), end)))
        cur = nxt
    return out
