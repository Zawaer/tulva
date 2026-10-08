"""Classical joint flood model: spring maxima, marginal fits, Gaussian-copula factor model.

Factor model (latent normal score of gauge i in cluster c):
    Z_i = a_c * F + b_c * G_c + sqrt(1 - a_c^2 - b_c^2) * e_i
F is one national factor, G_c one factor per cluster, e_i idiosyncratic; all iid N(0,1).
Implied correlation: a_c^2 + b_c^2 within cluster c, a_c * a_d between clusters c and d.
Gauge i is "over its 1-in-T level" when Z_i > Phi^-1(1 - 1/T).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import optimize, special, stats

# ---------------------------------------------------------------- maxima

def seasonal_max(q: pd.Series, months=(3, 4, 5, 6), min_days: int = 110,
                 years: range = range(1961, 2026)) -> pd.Series:
    """Max daily discharge in the given months of each year; NaN if fewer than min_days observed."""
    s = q[q.index.month.isin(months)]
    g = s.groupby(s.index.year)
    mx, n = g.max(), g.count()
    mx[n < min_days] = np.nan
    return mx.reindex(list(years))


# ---------------------------------------------------------------- marginals

def gev_lmom(x: np.ndarray) -> dict:
    """GEV parameters by L-moments (Hosking 1990). Shape k in Hosking's sign (k>0: bounded upper tail)."""
    x = np.sort(np.asarray(x, float)[~np.isnan(x)])
    n = len(x)
    j = np.arange(1, n + 1)
    b0 = x.mean()
    b1 = np.sum((j - 1) / (n - 1) * x) / n
    b2 = np.sum((j - 1) * (j - 2) / ((n - 1) * (n - 2)) * x) / n
    l1, l2, l3 = b0, 2 * b1 - b0, 6 * b2 - 6 * b1 + b0
    t3 = l3 / l2
    c = 2 / (3 + t3) - np.log(2) / np.log(3)
    k = 7.8590 * c + 2.9554 * c ** 2
    if abs(k) < 1e-6:  # Gumbel limit
        alpha = l2 / np.log(2)
        return {"dist": "gumbel", "loc": l1 - 0.5772 * alpha, "scale": alpha, "k": 0.0, "n": n}
    g = special.gamma(1 + k)
    alpha = l2 * k / ((1 - 2 ** (-k)) * g)
    xi = l1 - alpha * (1 - g) / k
    return {"dist": "gev", "loc": xi, "scale": alpha, "k": k, "n": n}


def gumbel_lmom(x: np.ndarray) -> dict:
    x = np.sort(np.asarray(x, float)[~np.isnan(x)])
    n = len(x)
    j = np.arange(1, n + 1)
    b0 = x.mean()
    b1 = np.sum((j - 1) / (n - 1) * x) / n
    alpha = (2 * b1 - b0) / np.log(2)
    return {"dist": "gumbel", "loc": b0 - 0.5772 * alpha, "scale": alpha, "k": 0.0, "n": n}


def return_level(par: dict, T: float) -> float:
    y = -np.log(1 - 1 / T)  # Gumbel reduced variate is -log(y)
    if par["k"] == 0.0:
        return par["loc"] - par["scale"] * np.log(y)
    return par["loc"] + par["scale"] / par["k"] * (1 - y ** par["k"])


# ---------------------------------------------------------------- dependence

def normal_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Per-column ranks -> Phi^-1(r/(n+1)), NaN kept."""
    r = df.rank()
    n = df.notna().sum()
    return pd.DataFrame(stats.norm.ppf(r / (n + 1)), index=df.index, columns=df.columns)


def exceed(df: pd.DataFrame, p: float = 0.1) -> pd.DataFrame:
    """1 where the value is in the gauge's own top fraction p of its record, 0 otherwise, NaN if missing.

    Empirical (rank-based) so every gauge has the same marginal rate as the copula model."""
    thr = df.quantile(1 - p)
    out = (df > thr).astype(float)
    return out.where(df.notna())


def implied_corr(a: np.ndarray, b: np.ndarray, clus: np.ndarray) -> np.ndarray:
    """Correlation matrix of the factor model; a,b indexed by cluster id, clus = cluster id per gauge."""
    A, B = a[clus], b[clus]
    R = np.outer(A, A) + np.where(clus[:, None] == clus[None, :], np.outer(B, B), 0.0)
    np.fill_diagonal(R, 1.0)
    return R


def fit_factor(R: np.ndarray, clus: np.ndarray, n_clusters: int, common_a: bool = False,
               W: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray, float]:
    """Least squares on the off-diagonal of R. Returns (a per cluster, b per cluster, rmse)."""
    iu = np.triu_indices(len(clus), 1)
    w = np.ones(len(iu[0])) if W is None else W[iu]
    ok = ~np.isnan(R[iu])

    def unpack(th):
        a = np.full(n_clusters, th[0]) if common_a else th[:n_clusters]
        b = th[1:] if common_a else th[n_clusters:]
        return a, b

    def resid(th):
        a, b = unpack(th)
        return (np.sqrt(w) * (implied_corr(a, b, clus)[iu] - R[iu]))[ok]

    k = 1 + n_clusters if common_a else 2 * n_clusters
    th0 = np.full(k, 0.4)
    res = optimize.least_squares(resid, th0, bounds=(0.0, 0.99))
    a, b = unpack(res.x)
    # keep it a valid model: a^2 + b^2 < 1
    s = np.sqrt(a ** 2 + b ** 2)
    shrink = np.where(s > 0.99, 0.99 / s, 1.0)
    a, b = a * shrink, b * shrink
    rmse = float(np.sqrt(np.mean((implied_corr(a, b, clus)[iu] - R[iu])[ok] ** 2)))
    return a, b, rmse


# ---------------------------------------------------------------- exact count distribution

def count_pmf(a: np.ndarray, b: np.ndarray, clus: np.ndarray, p: float | np.ndarray,
              n_nodes: int = 48) -> np.ndarray:
    """P(exactly k gauges exceed), k = 0..n, under the factor model. Gauss–Hermite quadrature over F and G_c
    (numerically exact to ~1e-10). p: marginal exceedance probability (scalar or per gauge)."""
    n = len(clus)
    p = np.broadcast_to(np.asarray(p, float), (n,))
    thr = stats.norm.ppf(1 - p)
    x, wts = np.polynomial.hermite_e.hermegauss(n_nodes)
    wts = wts / wts.sum()
    total = np.zeros(n + 1)
    for f, wf in zip(x, wts):
        pmf = np.array([1.0])
        for c in np.unique(clus):
            idx = np.where(clus == c)[0]
            ac, bc = a[c], b[c]
            sd = np.sqrt(max(1 - ac ** 2 - bc ** 2, 1e-12))
            cpmf = np.zeros(len(idx) + 1)
            for g, wg in zip(x, wts):
                pi = stats.norm.sf((thr[idx] - ac * f - bc * g) / sd)
                cpmf += wg * poisson_binomial(pi)
            pmf = np.convolve(pmf, cpmf)
        total += wf * pmf
    return total


def poisson_binomial(p: np.ndarray) -> np.ndarray:
    pmf = np.array([1.0])
    for pi in np.atleast_1d(p):
        pmf = np.convolve(pmf, [1 - pi, pi])
    return pmf


def at_least(pmf: np.ndarray) -> np.ndarray:
    """P(count >= k) for k = 0..n."""
    return pmf[::-1].cumsum()[::-1]


def simulate(a: np.ndarray, b: np.ndarray, clus: np.ndarray, n_years: int, seed: int = 0) -> np.ndarray:
    """Monte Carlo latent normal scores, shape (n_years, n_gauges)."""
    rng = np.random.default_rng(seed)
    nc = len(a)
    F = rng.standard_normal((n_years, 1))
    G = rng.standard_normal((n_years, nc))
    E = rng.standard_normal((n_years, len(clus)))
    A, B = a[clus], b[clus]
    return A * F + B * G[:, clus] + np.sqrt(1 - A ** 2 - B ** 2) * E
