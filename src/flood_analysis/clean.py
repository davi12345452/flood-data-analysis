"""Quality control, unit conversion and annual-maxima extraction.

Raw gauge records carry duplicated dates, calendar gaps, provisional readings and
occasional impossible values (negative discharge). Flood statistics are computed
on the extreme tail of the distribution, so a single bad value can move a
100-year estimate noticeably; everything in this module exists to make the series
safe to feed into :mod:`flood_analysis.frequency`.
"""

from __future__ import annotations

import pandas as pd

from .config import (
    APPROVED_QUALIFIERS,
    CFS_TO_CMS,
    FEET_TO_METRES,
)

WATER_YEAR_START_MONTH = 10  # USGS convention: a water year runs Oct 1 -> Sep 30.


def add_metric_units(frame: pd.DataFrame) -> pd.DataFrame:
    """Add SI columns next to the imperial ones published by NWIS."""
    out = frame.copy()
    if "discharge_cfs" in out.columns:
        out["discharge_cms"] = out["discharge_cfs"] * CFS_TO_CMS
    if "gage_height_ft" in out.columns:
        out["gage_height_m"] = out["gage_height_ft"] * FEET_TO_METRES
    return out


def add_water_year(frame: pd.DataFrame, start_month: int = WATER_YEAR_START_MONTH) -> pd.DataFrame:
    """Label every row with its water year and calendar year.

    Flood peaks in temperate basins straddle the New Year, so a calendar year can
    split a single flood season in two. The water year keeps a season intact.
    """
    out = frame.copy()
    dates = pd.to_datetime(out["date"])
    out["year"] = dates.dt.year
    out["month"] = dates.dt.month
    out["day_of_year"] = dates.dt.dayofyear
    out["water_year"] = dates.dt.year.where(dates.dt.month < start_month, dates.dt.year + 1)
    return out


def flag_provisional(frame: pd.DataFrame, columns: tuple[str, ...] = ("discharge_cfs",)) -> pd.DataFrame:
    """Add a boolean ``*_approved`` column derived from the NWIS quality code."""
    out = frame.copy()
    for column in columns:
        qualifier = f"{column}_qualifier"
        if qualifier not in out.columns:
            continue
        codes = out[qualifier].astype(str).str.strip()
        out[f"{column}_approved"] = codes.isin(APPROVED_QUALIFIERS)
    return out


def clean_daily_record(
    frame: pd.DataFrame,
    value_column: str = "discharge_cfs",
    drop_provisional: bool = False,
) -> pd.DataFrame:
    """Return a gap-explicit daily series ready for analysis.

    Steps: drop rows without a date, keep the first reading of duplicated dates,
    void physically impossible discharge, optionally void provisional readings,
    then reindex onto a complete daily calendar so gaps become explicit ``NaN``
    rather than invisible jumps between consecutive rows.
    """
    if value_column not in frame.columns:
        raise KeyError(f"Column {value_column!r} is missing from the record.")

    out = frame.dropna(subset=["date"]).copy()
    out["date"] = pd.to_datetime(out["date"])
    out = out.drop_duplicates(subset="date", keep="first").sort_values("date")

    if value_column.startswith("discharge"):
        out.loc[out[value_column] < 0, value_column] = pd.NA

    out = flag_provisional(out, columns=(value_column,))
    approved_column = f"{value_column}_approved"
    if drop_provisional and approved_column in out.columns:
        out.loc[~out[approved_column], value_column] = pd.NA

    full_index = pd.date_range(out["date"].min(), out["date"].max(), freq="D")
    out = out.set_index("date").reindex(full_index)
    out.index.name = "date"
    out = out.reset_index()

    out[value_column] = pd.to_numeric(out[value_column], errors="coerce")
    out = add_metric_units(out)
    return add_water_year(out)


def coverage_by_year(
    frame: pd.DataFrame,
    value_column: str = "discharge_cfs",
    year_column: str = "water_year",
) -> pd.DataFrame:
    """Observed days per year, as an absolute count and as a fraction."""
    grouped = frame.groupby(year_column)[value_column]
    coverage = pd.DataFrame(
        {
            "observed_days": grouped.count(),
            "total_days": grouped.size(),
        }
    )
    coverage["coverage"] = coverage["observed_days"] / coverage["total_days"]
    return coverage.reset_index()


def annual_maxima(
    frame: pd.DataFrame,
    value_column: str = "discharge_cfs",
    year_column: str = "water_year",
    min_coverage: float = 0.9,
) -> pd.DataFrame:
    """Extract the annual maximum series used by the frequency analysis.

    Years with less than ``min_coverage`` of their days observed are dropped: the
    largest reading of a half-observed year is not an annual maximum, and keeping
    it biases the fitted distribution downwards.
    """
    coverage = coverage_by_year(frame, value_column, year_column)
    complete_years = set(coverage.loc[coverage["coverage"] >= min_coverage, year_column])

    usable = frame.dropna(subset=[value_column])
    usable = usable[usable[year_column].isin(complete_years)]
    if usable.empty:
        return pd.DataFrame(columns=[year_column, "peak", "date"])

    peak_rows = usable.loc[usable.groupby(year_column)[value_column].idxmax()]
    result = peak_rows[[year_column, value_column, "date"]].rename(columns={value_column: "peak"})
    return result.sort_values(year_column).reset_index(drop=True)
