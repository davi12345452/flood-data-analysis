"""Download and parse daily river gauge records from the USGS NWIS web service.

The service is public and needs no API key. It answers in the RDB format: a
tab-separated table preceded by ``#`` comment lines and followed, right after the
header, by an extra row of column format specifiers that must be discarded.
"""

from __future__ import annotations

import re
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

from .config import (
    PARAM_DISCHARGE,
    PARAM_GAGE_HEIGHT,
    RAW_DIR,
    Station,
)

NWIS_DAILY_VALUES_URL = "https://waterservices.usgs.gov/nwis/dv/"

# Column names look like ``<time series id>_<parameter code>_<statistic code>``,
# optionally suffixed with ``_cd`` for the companion quality-code column.
_VALUE_COLUMN = re.compile(r"^(?P<ts>\d+)_(?P<param>\d{5})_(?P<stat>\d{5})$")

# Statistic codes, in the order we prefer them: daily mean, then daily maximum.
_STAT_PREFERENCE = ("00003", "00001", "00002")

_PARAM_LABELS = {
    PARAM_DISCHARGE: "discharge_cfs",
    PARAM_GAGE_HEIGHT: "gage_height_ft",
}


class NWISError(RuntimeError):
    """Raised when the NWIS service cannot serve the requested record."""


def build_request_params(
    site_no: str,
    start: str,
    end: str,
    parameter_codes: tuple[str, ...] = (PARAM_DISCHARGE, PARAM_GAGE_HEIGHT),
) -> dict[str, str]:
    """Assemble the query string for a daily-values request."""
    return {
        "format": "rdb",
        "sites": site_no,
        "startDT": start,
        "endDT": end,
        "parameterCd": ",".join(parameter_codes),
        "siteStatus": "all",
    }


def fetch_raw(
    site_no: str,
    start: str,
    end: str,
    parameter_codes: tuple[str, ...] = (PARAM_DISCHARGE, PARAM_GAGE_HEIGHT),
    timeout: int = 120,
) -> str:
    """Return the raw RDB payload for one station and date range."""
    response = requests.get(
        NWIS_DAILY_VALUES_URL,
        params=build_request_params(site_no, start, end, parameter_codes),
        timeout=timeout,
        headers={"User-Agent": "flood-data-analysis/0.1 (https://github.com/davi12345452)"},
    )
    if response.status_code == 404:
        raise NWISError(f"No daily values published for site {site_no} between {start} and {end}.")
    response.raise_for_status()
    return response.text


def _select_columns(columns: list[str]) -> dict[str, str]:
    """Map each parameter of interest to the best available time-series column.

    A station can publish several series for the same parameter (mean, maximum,
    minimum, or duplicated sensors). We keep one column per parameter, following
    ``_STAT_PREFERENCE``.
    """
    candidates: dict[str, list[tuple[int, str]]] = {}
    for column in columns:
        match = _VALUE_COLUMN.match(column)
        if match is None:
            continue
        param = match.group("param")
        if param not in _PARAM_LABELS:
            continue
        stat = match.group("stat")
        rank = _STAT_PREFERENCE.index(stat) if stat in _STAT_PREFERENCE else len(_STAT_PREFERENCE)
        candidates.setdefault(param, []).append((rank, column))

    selected: dict[str, str] = {}
    for param, options in candidates.items():
        options.sort()
        selected[options[0][1]] = _PARAM_LABELS[param]
    return selected


def parse_rdb(text: str) -> pd.DataFrame:
    """Parse an RDB payload into a tidy frame.

    Returns columns ``site_no``, ``date`` and, when published by the station,
    ``discharge_cfs`` / ``gage_height_ft`` plus their ``*_qualifier`` columns.
    """
    lines = [line for line in text.splitlines() if not line.startswith("#")]
    lines = [line for line in lines if line.strip()]
    if len(lines) < 2:
        raise NWISError("RDB payload contains no data rows.")

    # Line 0 is the header, line 1 is the format-specifier row that must be dropped.
    body = "\n".join([lines[0], *lines[2:]])
    frame = pd.read_csv(StringIO(body), sep="\t", dtype=str)

    if "datetime" not in frame.columns:
        raise NWISError("RDB payload has no 'datetime' column.")

    selected = _select_columns(list(frame.columns))
    if not selected:
        raise NWISError("RDB payload has no discharge or gage-height columns.")

    out = pd.DataFrame({"date": pd.to_datetime(frame["datetime"], errors="coerce")})
    out["site_no"] = frame.get("site_no", pd.Series(dtype=str)).astype(str).str.strip()

    for source, label in selected.items():
        out[label] = pd.to_numeric(frame[source], errors="coerce")
        qualifier = f"{source}_cd"
        if qualifier in frame.columns:
            out[f"{label}_qualifier"] = frame[qualifier].astype(str).str.strip()

    out = out.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    ordered = ["site_no", "date"] + [c for c in out.columns if c not in {"site_no", "date"}]
    return out[ordered]


def cache_path(station: Station, start: str, end: str, raw_dir: Path = RAW_DIR) -> Path:
    """Path of the on-disk copy for a station/date-range combination."""
    return raw_dir / f"{station.slug}_{start}_{end}.csv"


def load_station_data(
    station: Station,
    start: str,
    end: str,
    refresh: bool = False,
    raw_dir: Path = RAW_DIR,
) -> pd.DataFrame:
    """Return the daily record for a station, downloading it only when needed.

    The first call hits the NWIS service and writes a CSV under ``data/raw``;
    later calls read that file, so the rest of the pipeline runs offline.
    """
    destination = cache_path(station, start, end, raw_dir)
    if destination.exists() and not refresh:
        return pd.read_csv(destination, parse_dates=["date"], dtype={"site_no": str})

    frame = parse_rdb(fetch_raw(station.site_no, start, end))
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(destination, index=False)
    return frame
