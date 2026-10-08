"""Discretised factor model of joint spring flooding.

Continuous model (fitted from SYKE data in model.py):
    z_area = a * N + b_c * C_c + sqrt(1 - a^2 - b_c^2) * e_area
N = national hydrology factor, C_c = cluster factor, e = local noise, all standard normal.
An area "triggers" when z_area exceeds its own level (e.g. its 1-in-50 spring maximum).

For quantum circuits we need a few qubits per factor, so this module builds a two-level
(binary) version of the same model:
    W   = 1 if N is "wet" (above a cut)                  -> one qubit
    S_c = 1 if the cluster driver D_c is "wet"           -> one qubit per cluster
    area triggers with P(trigger | S_c)                  -> one qubit per area
and computes everything about that network exactly, by enumeration. The exact numbers here are the
reference every quantum result is checked against.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

_GRID = np.linspace(-8, 8, 8001)
_PDF = norm.pdf(_GRID)


def _region_mask(lo: float, hi: float) -> np.ndarray:
    return (_GRID >= lo) & (_GRID < hi)


def p_exceed_given_region(threshold: float, rho: float, lo: float, hi: float, shift: float = 0.0) -> float:
    """P(rho*X + sqrt(1-rho^2)*e > threshold | X in [lo, hi)), X ~ N(shift, 1)."""
    w = norm.pdf(_GRID - shift) * _region_mask(lo, hi)
    pc = norm.sf((threshold - rho * _GRID) / np.sqrt(max(1e-12, 1 - rho**2)))
    return float((w * pc).sum() / w.sum())


def p_region(lo: float, hi: float, shift: float = 0.0) -> float:
    return float(norm.cdf(hi - shift) - norm.cdf(lo - shift))


@dataclass
class TwoLevelModel:
    """Binary network W -> S_c -> areas, exact by enumeration."""

    p_wet: float                       # P(W = 1)
    p_cluster_wet: np.ndarray          # shape (n_clusters, 2): P(S_c = 1 | W = w)
    p_area: np.ndarray                 # shape (n_areas, 2): P(trigger | S_c = s) for the area's cluster
    area_cluster: np.ndarray           # cluster index of each area

    @property
    def n_areas(self) -> int:
        return len(self.area_cluster)

    def count_distribution(self, areas: list[int] | None = None) -> np.ndarray:
        """P(exactly k of the given areas trigger), k = 0..len(areas)."""
        areas = list(range(self.n_areas)) if areas is None else list(areas)
        clusters = sorted(set(self.area_cluster[areas]))
        out = np.zeros(len(areas) + 1)
        for w in (0, 1):
            pw = self.p_wet if w else 1 - self.p_wet
            for states in itertools.product((0, 1), repeat=len(clusters)):
                ps = pw
                for c, s in zip(clusters, states):
                    pc = self.p_cluster_wet[c, w]
                    ps *= pc if s else 1 - pc
                dist = np.array([1.0])
                for a in areas:
                    s = states[clusters.index(self.area_cluster[a])]
                    p = self.p_area[a, s]
                    dist = np.convolve(dist, [1 - p, p])
                out += ps * dist
        return out

    def p_at_least(self, k: int, areas: list[int] | None = None) -> float:
        return float(self.count_distribution(areas)[k:].sum())


def build_two_level(loadings_national: np.ndarray, loadings_cluster: np.ndarray, area_cluster: np.ndarray,
                    trigger_prob: np.ndarray, wet_quantile: float = 0.7, outlook_shift: float = 0.0
                    ) -> TwoLevelModel:
    """Discretise the continuous factor model.

    loadings_national[a], loadings_cluster[a]: the area's loadings a, b_c.
    trigger_prob[a]: the area's unconditional trigger probability (e.g. 1/50).
    wet_quantile: factors above this quantile count as "wet".
    outlook_shift: shift of the national factor's mean, in standard deviations, from a March snow outlook.
    """
    cut = norm.ppf(wet_quantile)
    p_wet = p_region(cut, np.inf, outlook_shift)
    n_clusters = int(area_cluster.max()) + 1
    p_cluster_wet = np.zeros((n_clusters, 2))
    p_area = np.zeros((len(area_cluster), 2))
    for c in range(n_clusters):
        members = np.where(area_cluster == c)[0]
        a = float(np.mean(loadings_national[members]))
        b = float(np.mean(loadings_cluster[members]))
        r = a / np.hypot(a, b)                  # corr(N, D_c), D_c = (a N + b C_c) / hypot(a, b)
        for w, (lo, hi) in enumerate([(-np.inf, cut), (cut, np.inf)]):
            p_cluster_wet[c, w] = p_exceed_given_region(cut, r, lo, hi, outlook_shift)
        for m in members:
            rho = float(np.hypot(loadings_national[m], loadings_cluster[m]))   # corr(z_area, D_c)
            t = norm.isf(trigger_prob[m])
            for s, (lo, hi) in enumerate([(-np.inf, cut), (cut, np.inf)]):
                p_area[m, s] = p_exceed_given_region(t, rho, lo, hi)
    return TwoLevelModel(p_wet, p_cluster_wet, p_area, area_cluster)


def monte_carlo_continuous(loadings_national, loadings_cluster, area_cluster, trigger_prob, n: int,
                           outlook_shift: float = 0.0, seed: int = 0) -> np.ndarray:
    """Count of triggered areas per simulated spring under the continuous model (the classical reference)."""
    rng = np.random.default_rng(seed)
    n_clusters = int(area_cluster.max()) + 1
    N = rng.standard_normal((n, 1)) + outlook_shift
    C = rng.standard_normal((n, n_clusters))[:, area_cluster]
    e = rng.standard_normal((n, len(area_cluster)))
    a, b = np.asarray(loadings_national), np.asarray(loadings_cluster)
    z = a * N + b * C + np.sqrt(1 - a**2 - b**2) * e
    return (z > norm.isf(trigger_prob)).sum(1)
