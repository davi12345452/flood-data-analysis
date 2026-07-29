"""Project-wide paths, constants and gauge station catalogue."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# USGS NWIS parameter codes.
PARAM_DISCHARGE = "00060"  # discharge, cubic feet per second
PARAM_GAGE_HEIGHT = "00065"  # gage height, feet

# Unit conversions (the NWIS service publishes imperial units).
CFS_TO_CMS = 0.028316846592  # cubic feet per second -> cubic metres per second
FEET_TO_METRES = 0.3048

# Quality codes considered trustworthy for statistical analysis.
# "A" = approved for publication, "P" = provisional (subject to revision).
APPROVED_QUALIFIERS = frozenset({"A", "A:e", "A e"})

# Return periods (years) reported by the frequency analysis.
DEFAULT_RETURN_PERIODS = (2, 5, 10, 25, 50, 100, 200, 500)

# Peaks-over-threshold defaults.
DEFAULT_THRESHOLD_QUANTILE = 0.99
DEFAULT_MIN_SEPARATION_DAYS = 5
DEFAULT_MIN_DURATION_DAYS = 1


@dataclass(frozen=True)
class Station:
    """A river gauge station tracked by this project."""

    site_no: str
    name: str
    river: str
    state: str

    @property
    def slug(self) -> str:
        """Filesystem-friendly identifier used for cached datasets."""
        return f"{self.site_no}_{self.name.lower().replace(' ', '_')}"


# Long-record stations on rivers with a well documented flood history.
STATIONS: dict[str, Station] = {
    "baton_rouge": Station(
        site_no="07374000",
        name="Baton Rouge",
        river="Mississippi River",
        state="LA",
    ),
    "vicksburg": Station(
        site_no="07289000",
        name="Vicksburg",
        river="Mississippi River",
        state="MS",
    ),
    "hermann": Station(
        site_no="06934500",
        name="Hermann",
        river="Missouri River",
        state="MO",
    ),
    "harrisburg": Station(
        site_no="01570500",
        name="Harrisburg",
        river="Susquehanna River",
        state="PA",
    ),
}

DEFAULT_STATION = "baton_rouge"


def resolve_station(key: str) -> Station:
    """Look up a station by catalogue key or by raw USGS site number."""
    if key in STATIONS:
        return STATIONS[key]
    for station in STATIONS.values():
        if station.site_no == key:
            return station
    if key.isdigit():
        return Station(site_no=key, name=f"site {key}", river="unknown", state="--")
    raise KeyError(
        f"Unknown station {key!r}. Known keys: {', '.join(sorted(STATIONS))}, "
        "or pass a numeric USGS site number."
    )


def ensure_directories() -> None:
    """Create the output directories the pipeline writes to."""
    for directory in (RAW_DIR, PROCESSED_DIR, REPORTS_DIR, FIGURES_DIR):
        directory.mkdir(parents=True, exist_ok=True)
