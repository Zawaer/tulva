"""Pricing of the Tulva Index: parametric cover paying a fixed sum when >= m of a cluster's gauges pass their
1-in-T spring level.

Within cluster c the fitted factor model (model.py) reduces to one driver:
    Z_i = h * D_c + sqrt(1 - h^2) * e_i,   h = sqrt(a^2 + b_c^2),   D_c = (a F + b_c G_c) / h ~ N(0, 1)
so a cluster trigger depends only on (n, m, p, h). Exact values integrate over D_c on a fine grid; Monte Carlo
simulates the full three-factor model (national F, cluster G_c, local e_i).

March snow outlook: O_c = s * D_c + sqrt(1 - s^2) * u, s = outlook skill vs the cluster's latent factor
(out/snow_skill.json). A "top-15 % outlook" conditions on O_c > Phi^-1(0.85) (bottom: O_c < Phi^-1(0.15)); this
is the exact conditional distribution of D_c, not just a mean shift.

Student-t copula (robustness): Z_i = X_i / sqrt(W / nu), W ~ chi2(nu) common to all gauges in a spring, X from
the same Gaussian factor model; thresholds are t_nu quantiles, so marginals are unchanged and only the joint
tail grows heavier.
"""
from __future__ import annotations

import numpy as np
from scipy import stats

_D = np.linspace(-9, 9, 6001)
_DW = _D[1] - _D[0]


def binom_at_least(n: int, m: int, q: np.ndarray) -> np.ndarray:
    """P(Binomial(n, q) >= m), vectorised over q."""
    return stats.binom.sf(m - 1, n, q)


def outlook_weight(skill: float, side: str | None, frac: float = 0.15) -> np.ndarray:
    """Density of D_c on the grid _D, given the outlook (None = climatology, 'high' = top frac, 'low' = bottom)."""
    w = stats.norm.pdf(_D)
    if side is not None:
        sd = np.sqrt(max(1 - skill ** 2, 1e-12))
        if side == "high":
            w = w * stats.norm.sf((stats.norm.isf(frac) - skill * _D) / sd)
        elif side == "low":
            w = w * stats.norm.cdf((stats.norm.ppf(frac) - skill * _D) / sd)
        else:
            raise ValueError(side)
    return w / (w.sum() * _DW)


def p_trigger_exact(n: int, m: int, p: float, h: float, skill: float = 0.0, side: str | None = None,
                    frac: float = 0.15) -> float:
    """P(>= m of n exchangeable gauges exceed their (1-p) level) under the Gaussian one-driver model."""
    t = stats.norm.isf(p)
    q = stats.norm.sf((t - h * _D) / np.sqrt(1 - h ** 2))
    return float((outlook_weight(skill, side, frac) * binom_at_least(n, m, q)).sum() * _DW)


def p_trigger_t_exact(n: int, m: int, p: float, h: float, df: float, n_w: int = 400) -> float:
    """Same under a Student-t copula with df degrees of freedom (2-D quadrature over D and W)."""
    t = stats.t.isf(p, df)
    u = (np.arange(n_w) + 0.5) / n_w                     # midpoint rule on W's quantiles
    s = np.sqrt(stats.chi2.ppf(u, df) / df)[:, None]     # sqrt(W/nu)
    q = stats.norm.sf((t * s - h * _D[None, :]) / np.sqrt(1 - h ** 2))
    return float((binom_at_least(n, m, q).mean(0) * stats.norm.pdf(_D)).sum() * _DW)


def p_trigger_independent(n: int, m: int, p: float) -> float:
    return float(binom_at_least(n, m, np.array(p)))


def p_trigger_comonotone(n: int, m: int, p: float) -> float:
    """All gauges move together: >= m trigger iff all do, probability p (for 1 <= m <= n)."""
    return float(p)


def mc_counts(a: float, b: float, n: int, p: float, n_sims: int, skill: float = 0.0, side: str | None = None,
              frac: float = 0.15, df: float | None = None, seed: int = 0, chunk: int = 500_000) -> np.ndarray:
    """Monte Carlo of the continuous three-factor model for one cluster; returns the count of triggered gauges
    per simulated spring. side='high'/'low' samples the outlook O_c from its truncated normal, then D_c | O_c,
    then F | D_c and G_c | (F, D_c), so the full factor structure is kept."""
    rng = np.random.default_rng(seed)
    h = np.hypot(a, b)
    thr = stats.norm.isf(p) if df is None else stats.t.isf(p, df)
    out = []
    left = n_sims
    while left > 0:
        k = min(chunk, left)
        left -= k
        if side is None:
            F = rng.standard_normal(k)
            G = rng.standard_normal(k)
        else:
            lo, hi = (stats.norm.isf(frac), np.inf) if side == "high" else (-np.inf, stats.norm.ppf(frac))
            O = stats.truncnorm.rvs(lo, hi, size=k, random_state=rng)
            D = skill * O + np.sqrt(1 - skill ** 2) * rng.standard_normal(k)
            ra = a / h                                    # corr(F, D)
            F = ra * D + np.sqrt(1 - ra ** 2) * rng.standard_normal(k)
            G = (h * D - a * F) / b
        Z = (a * F + b * G)[:, None] + np.sqrt(1 - h ** 2) * rng.standard_normal((k, n))
        if df is not None:
            Z = Z / np.sqrt(rng.chisquare(df, (k, 1)) / df)
        out.append((Z > thr).sum(1).astype(np.int8))
    return np.concatenate(out)


def mc_prob(counts: np.ndarray, m: int) -> tuple[float, float]:
    """(estimate, standard error) of P(count >= m)."""
    x = counts >= m
    pr = float(x.mean())
    return pr, float(np.sqrt(pr * (1 - pr) / len(x)))


def premium(p: float, payout: float = 10e6, risk_load: float = 0.35) -> float:
    """Premium = expected payout x (1 + risk load)."""
    return p * payout * (1 + risk_load)


# Market price: cat bonds traded at ~2.4-3.7x expected loss in 2024-26 (AM Best), flood ILS ~3.0-3.4x
# (Flood Re Vision 2039, FloodSmart Re); see business/CHEATSHEET.md. Premium = multiple x expected loss.
MARKET_MULTIPLES = (2.5, 3.5)


def market_price(p: float, payout: float = 10e6, multiple: float = 2.5) -> float:
    """Premium = expected payout x multiple (market convention for cat bonds / ILS)."""
    return p * payout * multiple


# Staged payout: a fraction of the limit at >= m gauges (steps in ascending m).
STAGES = ((2, 0.5), (3, 1.0))


def staged_payout_fraction(p_at_least: dict[int, float], stages=STAGES) -> float:
    """Expected payout as a fraction of the limit for a staged cover, from P(>= m) per stage threshold.
    Pays the highest stage reached: E = sum_j (f_j - f_{j-1}) P(>= m_j)."""
    e, prev = 0.0, 0.0
    for m, f in stages:
        e += (f - prev) * p_at_least[m]
        prev = f
    return float(e)
