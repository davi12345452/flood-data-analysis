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
import os
from pathlib import Path

import httpx
import pandas as pd
import yaml
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ..core.paths import CONFIG_DIR
from ..core.paths import RAW as RAW  # noqa: PLC0414
from ..core.paths import REFERENCE as REFERENCE  # noqa: PLC0414
from ..core.paths import ROOT as ROOT  # noqa: PLC0414
from ..core.storage import atomic_write, parquet, text


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
        event_hooks={"request": [_offline_request]},
    )


def _offline_request(request: httpx.Request) -> None:
    if os.environ.get("FLOOD_OFFLINE") == "1":
        raise RuntimeError(f"Modo offline: HTTP bloqueado ({request.url}).")


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
    if os.environ.get("FLOOD_OFFLINE") == "1":
        raise RuntimeError(f"Modo offline: recurso não disponível no cache ({url}).")
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
    if not dest.exists() or not meta_path(dest).exists():
        return False
    try:
        meta = json.loads(meta_path(dest).read_text())
        if meta.get("size_bytes", dest.stat().st_size) != dest.stat().st_size:
            return False
        if "sha256" in meta:
            from ..core.provenance import sha256
            return sha256(dest) == meta["sha256"]
        return True  # compatibilidade com o cache histórico sem hash
    except (ValueError, OSError):
        return False


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
    from ..core.provenance import sha256
    meta = {
        "sha256": sha256(dest),
        "url": url,
        "params": params or {},
        "downloaded_at_utc": utcnow_iso(),
        "n_records": n_records,
        "size_bytes": dest.stat().st_size,
        "partial": partial,
    }
    if extra:
        meta.update(extra)
    text(json.dumps(meta, indent=2, ensure_ascii=False), meta_path(dest))


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
    parquet(df, dest)
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
    atomic_write(dest, lambda tmp: tmp.write_bytes(resp.content))
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


def source_order(path: Path) -> tuple[float, str]:
    """Ordem de revisão: download mais recente vence, independentemente do nome."""
    try:
        meta = json.loads(meta_path(path).read_text())
        stamp = pd.Timestamp(meta["downloaded_at_utc"]).timestamp()
    except (OSError, ValueError, KeyError):
        stamp = path.stat().st_mtime
    return stamp, str(path)
