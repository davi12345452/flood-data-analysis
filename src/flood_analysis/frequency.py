"""Flood frequency analysis: fit extreme-value distributions to annual maxima.

Three fits are provided because they disagree in exactly the region that matters
— the far tail — and the spread between them is the honest uncertainty band:

* **Gumbel (EV1)**, fitted with L-moments, which are far less sensitive to a
  single outlying peak than ordinary moments.
* **Log-Pearson type III**, the reference method of USGS Bulletin 17B/17C for
  the United States, fitted on base-10 logarithms.
* **GEV**, fitted by maximum likelihood, which lets the data choose the tail
  shape instead of assuming it.

All return levels are expressed in the unit of the input series.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy import stats

EULER_MASCHERONI = 0.5772156649015329


def _as_clean_array(values) -> np.ndarray:
    """Coerce input to a 1-D float array without NaNs."""
    array = np.asarray(values, dtype=float).ravel()
    array = array[np.isfinite(array)]
    if array.size < 5:
        raise ValueError(f"At least 5 annual maxima are required, got {array.size}.")
    return array


# --------------------------------------------------------------------------- #
# Empirical (plotting position) analysis
# --------------------------------------------------------------------------- #

_PLOTTING_POSITION_COEFFICIENTS = {
    "weibull": 0.0,
    "gringorten": 0.44,
    "cunnane": 0.40,
    "hazen": 0.5,
}


def plotting_positions(n: int, method: str = "weibull") -> np.ndarray:
    """Exceedance probabilities for ranks 1..n (rank 1 = largest observation).

    The general form is ``(i - a) / (n + 1 - 2a)``. Weibull (``a = 0``) is
    unbiased for the exceedance probability itself; Gringorten is the usual
    choice when the sample is assumed Gumbel-distributed.
    """
    if method not in _PLOTTING_POSITION_COEFFICIENTS:
        raise ValueError(
            f"Unknown plotting position {method!r}. "
            f"Options: {', '.join(sorted(_PLOTTING_POSITION_COEFFICIENTS))}."
        )
    if n < 1:
        raise ValueError("n must be positive.")
    a = _PLOTTING_POSITION_COEFFICIENTS[method]
    ranks = np.arange(1, n + 1, dtype=float)
    return (ranks - a) / (n + 1 - 2 * a)


def empirical_frequency(values, method: str = "weibull") -> pd.DataFrame:
    """Rank the observed peaks and attach empirical return periods."""
    array = _as_clean_array(values)
    ordered = np.sort(array)[::-1]
    exceedance = plotting_positions(ordered.size, method)
    return pd.DataFrame(
        {
            "rank": np.arange(1, ordered.size + 1),
            "peak": ordered,
            "exceedance_probability": exceedance,
            "return_period": 1.0 / exceedance,
        }
    )


# --------------------------------------------------------------------------- #
# Distribution fits
# --------------------------------------------------------------------------- #


@dataclass
class DistributionFit:
    """A fitted extreme-value distribution with a common interface."""

    name: str
    params: dict[str, float] = field(default_factory=dict)
    sample_size: int = 0

    def return_level(self, return_period) -> np.ndarray:
        raise NotImplementedError

    def cdf(self, x) -> np.ndarray:
        raise NotImplementedError

    def _validate_return_period(self, return_period) -> np.ndarray:
        periods = np.atleast_1d(np.asarray(return_period, dtype=float))
        if np.any(periods <= 1.0):
            raise ValueError("Return periods must be greater than 1 year.")
        return periods


@dataclass
class GumbelFit(DistributionFit):
    """Gumbel (extreme value type I) fitted with L-moments."""

    def return_level(self, return_period) -> np.ndarray:
        periods = self._validate_return_period(return_period)
        reduced_variate = -np.log(-np.log(1.0 - 1.0 / periods))
        return self.params["loc"] + self.params["scale"] * reduced_variate

    def cdf(self, x) -> np.ndarray:
        return stats.gumbel_r.cdf(x, loc=self.params["loc"], scale=self.params["scale"])


@dataclass
class LogPearson3Fit(DistributionFit):
    """Log-Pearson type III fitted on base-10 logarithms (Bulletin 17B)."""

    def return_level(self, return_period) -> np.ndarray:
        periods = self._validate_return_period(return_period)
        z = stats.norm.ppf(1.0 - 1.0 / periods)
        k = _frequency_factor(z, self.params["skew_log"])
        log_level = self.params["mean_log"] + k * self.params["std_log"]
        return np.power(10.0, log_level)

    def cdf(self, x) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        skew = self.params["skew_log"]
        logs = np.log10(np.where(x > 0, x, np.nan))
        if abs(skew) < 1e-8:
            return stats.norm.cdf(logs, self.params["mean_log"], self.params["std_log"])
        shape = 4.0 / skew**2
        scale = 0.5 * abs(skew) * self.params["std_log"]
        origin = self.params["mean_log"] - 2.0 * self.params["std_log"] / skew
        standardised = (logs - origin) / scale
        if skew > 0:
            return stats.gamma.cdf(standardised, shape)
        return 1.0 - stats.gamma.cdf(-standardised, shape)


@dataclass
class GEVFit(DistributionFit):
    """Generalised extreme value distribution fitted by maximum likelihood.

    ``shape`` follows the SciPy sign convention (``c``): ``c < 0`` is a heavy
    Frechet tail, ``c > 0`` a bounded Weibull tail, ``c = 0`` reduces to Gumbel.
    """

    def return_level(self, return_period) -> np.ndarray:
        periods = self._validate_return_period(return_period)
        return stats.genextreme.ppf(
            1.0 - 1.0 / periods,
            self.params["shape"],
            loc=self.params["loc"],
            scale=self.params["scale"],
        )

    def cdf(self, x) -> np.ndarray:
        return stats.genextreme.cdf(
            x, self.params["shape"], loc=self.params["loc"], scale=self.params["scale"]
        )


def _frequency_factor(z: np.ndarray, skew: float) -> np.ndarray:
    """Pearson III frequency factor via the Wilson-Hilferty approximation."""
    z = np.asarray(z, dtype=float)
    if abs(skew) < 1e-8:
        return z
    k = skew / 6.0
    return (2.0 / skew) * (np.power((z - k) * k + 1.0, 3) - 1.0)


def _l_moments(sorted_ascending: np.ndarray) -> tuple[float, float]:
    """First two sample L-moments of an ascending array."""
    n = sorted_ascending.size
    b0 = float(sorted_ascending.mean())
    weights = (np.arange(1, n + 1, dtype=float) - 1.0) / (n - 1.0)
    b1 = float(np.mean(weights * sorted_ascending))
    return b0, 2.0 * b1 - b0


def fit_gumbel(values) -> GumbelFit:
    """Fit a Gumbel distribution using L-moments."""
    array = np.sort(_as_clean_array(values))
    l1, l2 = _l_moments(array)
    if l2 <= 0:
        raise ValueError("Sample has no dispersion; a Gumbel fit is undefined.")
    scale = l2 / np.log(2.0)
    loc = l1 - EULER_MASCHERONI * scale
    return GumbelFit(
        name="Gumbel (L-moments)",
        params={"loc": float(loc), "scale": float(scale)},
        sample_size=array.size,
    )


def fit_log_pearson3(values) -> LogPearson3Fit:
    """Fit a log-Pearson type III distribution to strictly positive peaks."""
    array = _as_clean_array(values)
    if np.any(array <= 0):
        raise ValueError("Log-Pearson III requires strictly positive peaks.")
    logs = np.log10(array)
    n = logs.size
    mean_log = float(logs.mean())
    std_log = float(logs.std(ddof=1))
    if std_log <= 0:
        raise ValueError("Log-transformed sample has no dispersion.")
    # Unbiased sample skewness, as prescribed by Bulletin 17B.
    skew_log = float(n * np.sum((logs - mean_log) ** 3) / ((n - 1) * (n - 2) * std_log**3))
    return LogPearson3Fit(
        name="Log-Pearson III",
        params={"mean_log": mean_log, "std_log": std_log, "skew_log": skew_log},
        sample_size=n,
    )


def fit_gev(values) -> GEVFit:
    """Fit a GEV distribution by maximum likelihood."""
    array = _as_clean_array(values)
    shape, loc, scale = stats.genextreme.fit(array)
    return GEVFit(
        name="GEV (maximum likelihood)",
        params={"shape": float(shape), "loc": float(loc), "scale": float(scale)},
        sample_size=array.size,
    )


FITTERS = {
    "gumbel": fit_gumbel,
    "log_pearson3": fit_log_pearson3,
    "gev": fit_gev,
}


def fit_all(values) -> dict[str, DistributionFit]:
    """Fit every supported distribution, skipping the ones that do not converge."""
    fits: dict[str, DistributionFit] = {}
    for key, fitter in FITTERS.items():
        try:
            fits[key] = fitter(values)
        except (ValueError, RuntimeError):
            continue
    if not fits:
        raise ValueError("No distribution could be fitted to the supplied sample.")
    return fits


# --------------------------------------------------------------------------- #
# Reporting helpers
# --------------------------------------------------------------------------- #


def return_level_table(
    values,
    return_periods,
    fits: dict[str, DistributionFit] | None = None,
) -> pd.DataFrame:
    """Return levels for every fitted distribution, one row per return period."""
    fits = fits or fit_all(values)
    periods = np.asarray(return_periods, dtype=float)
    table = pd.DataFrame({"return_period_years": periods})
    table["annual_exceedance_probability"] = 1.0 / periods
    for key, fit in fits.items():
        table[key] = fit.return_level(periods)
    return table


def goodness_of_fit(values, fits: dict[str, DistributionFit] | None = None) -> pd.DataFrame:
    """Compare fits with a Kolmogorov-Smirnov statistic and a tail-weighted RMSE.

    The KS p-value is indicative only: the parameters were estimated from the
    same sample, which makes the classical null distribution optimistic.
    """
    array = _as_clean_array(values)
    fits = fits or fit_all(array)
    empirical = empirical_frequency(array)
    observed = empirical["peak"].to_numpy()

    rows = []
    for key, fit in fits.items():
        ks = stats.kstest(array, fit.cdf)
        modelled = fit.return_level(empirical["return_period"].to_numpy())
        residuals = observed - modelled
        rows.append(
            {
                "distribution": key,
                "name": fit.name,
                "ks_statistic": float(ks.statistic),
                "ks_pvalue": float(ks.pvalue),
                "rmse": float(np.sqrt(np.mean(residuals**2))),
                "bias": float(np.mean(residuals)),
            }
        )
    return pd.DataFrame(rows).sort_values("rmse").reset_index(drop=True)


def bootstrap_return_levels(
    values,
    return_periods,
    distribution: str = "gumbel",
    n_iterations: int = 500,
    confidence: float = 0.90,
    seed: int = 42,
) -> pd.DataFrame:
    """Non-parametric bootstrap confidence band around the return-level curve.

    Resamples the annual maxima with replacement, refits, and reports the
    empirical percentiles of the resulting return levels. This captures sampling
    uncertainty only — it says nothing about whether the chosen distribution is
    the right one, which is why several distributions are reported side by side.
    """
    if distribution not in FITTERS:
        raise ValueError(f"Unknown distribution {distribution!r}.")
    if not 0 < confidence < 1:
        raise ValueError("confidence must lie strictly between 0 and 1.")

    array = _as_clean_array(values)
    periods = np.asarray(return_periods, dtype=float)
    fitter = FITTERS[distribution]
    rng = np.random.default_rng(seed)

    draws = []
    for _ in range(n_iterations):
        sample = rng.choice(array, size=array.size, replace=True)
        try:
            draws.append(fitter(sample).return_level(periods))
        except (ValueError, RuntimeError):
            continue

    if len(draws) < 2:
        raise RuntimeError("Bootstrap failed: almost every resample was degenerate.")

    matrix = np.vstack(draws)
    tail = (1.0 - confidence) / 2.0
    return pd.DataFrame(
        {
            "return_period_years": periods,
            "estimate": fitter(array).return_level(periods),
            "lower": np.quantile(matrix, tail, axis=0),
            "upper": np.quantile(matrix, 1.0 - tail, axis=0),
            "n_successful_resamples": len(draws),
        }
    )


def exceedance_probability_over_window(return_period: float, years: int) -> float:
    """Chance of seeing at least one T-year flood within ``years`` years.

    The classic counter-intuitive result: a 100-year flood has a 26% chance of
    occurring at least once during a 30-year mortgage.
    """
    if return_period <= 1:
        raise ValueError("Return period must be greater than 1 year.")
    if years < 1:
        raise ValueError("Window must cover at least one year.")
    return float(1.0 - (1.0 - 1.0 / return_period) ** years)
