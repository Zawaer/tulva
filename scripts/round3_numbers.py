"""Round-3 review numbers for the deck (logged in CLAIMS.md, "Round-3 deck pass").

1. Regulator-style baseline: North ">=2 of 5 gauges over 1-in-50" under ONE equicorrelation of 0.27 (about the mean of
   the 19-zone flood correlation matrix used inside Finland from 2027), Gaussian copula, one-factor quadrature
   (exact) + 2M-sample Monte Carlo check. Compared with the Tulva price from out/pricing.json.
2. Slide 2: Wilson 90 % interval for "10 of 65 springs with >=4 of 14 areas over 1-in-10" and the two independence
   baselines (same gauge-years as observed = like-for-like, vs all 14 gauges every year = binomial).
3. Slide 1: which North (Lapland) areas passed their 1-in-10 / 1-in-50 level in spring 2005 (web/data/app.json, the
   app's replay: empirical 1-in-10 as in out/joint_counts.json, fitted GEV 1-in-50).

    .venv/bin/python scripts/round3_numbers.py   ->  out/round3_numbers.json
"""
import json
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"


def p_ge_m_equicorr(rho, n=5, m=2, p=0.02, nodes=200):
    """P(at least m of n exceed their 1-in-(1/p) level), Gaussian copula with one common correlation rho."""
    c = stats.norm.ppf(1 - p)
    z, w = np.polynomial.hermite_e.hermegauss(nodes)
    w = w / w.sum()
    q = stats.norm.sf((c - np.sqrt(rho) * z) / np.sqrt(1 - rho))  # each gauge's exceedance prob given the factor
    return float(sum(wi * stats.binom.sf(m - 1, n, qi) for wi, qi in zip(w, q)))


def mc_equicorr(rho, n=5, m=2, p=0.02, size=2_000_000, seed=27):
    rng = np.random.default_rng(seed)
    c = stats.norm.ppf(1 - p)
    z = rng.standard_normal((size, 1))
    x = np.sqrt(rho) * z + np.sqrt(1 - rho) * rng.standard_normal((size, n))
    hit = ((x > c).sum(1) >= m)
    return float(hit.mean()), float(hit.std() / np.sqrt(size))


def wilson(k, n, conf=0.90):
    zc = stats.norm.ppf(0.5 + conf / 2)
    ph = k / n
    d = 1 + zc ** 2 / n
    centre = (ph + zc ** 2 / (2 * n)) / d
    half = zc * np.sqrt(ph * (1 - ph) / n + zc ** 2 / (4 * n * n)) / d
    return centre - half, centre + half


def main():
    pr = json.loads((OUT / "pricing.json").read_text())["clusters"]["North"]["triggers"]["ge2"]
    tulva, high = pr["tulva"]["p_exact"], pr["tulva_high_outlook"]["p_exact"]
    reg = p_ge_m_equicorr(0.27)
    reg_mc, reg_se = mc_equicorr(0.27)
    jc = json.loads((OUT / "joint_counts.json").read_text())
    i = jc["k"].index(4)
    k, n = jc["observed_n_years"][i], jc["n_years"]
    lo, hi = wilson(k, n)
    obs = jc["observed"][i]
    ind_same, ind_full = jc["independent_same_years"][i], jc["independent_full14"][i]
    res = {
        "north_ge2_of5_1in50": {
            "tulva_exact": round(tulva, 5), "high_snow_exact": round(high, 5),
            "equicorr_0.27_exact_quadrature": round(reg, 5),
            "equicorr_0.27_mc_2M": round(reg_mc, 5), "equicorr_0.27_mc_se": round(reg_se, 6),
            "tulva_over_equicorr": round(tulva / reg, 3), "high_over_tulva": round(high / tulva, 3),
            "independent_exact": pr["independent"]["p_exact"],
        },
        "ge4_of14_1in10": {
            "observed_years": k, "n_years": n, "observed": round(obs, 4),
            "wilson90": [round(lo, 4), round(hi, 4)],
            "independent_same_gauge_years": ind_same, "independent_all14_binomial": round(ind_full, 4),
            "ratio_same_gauge_years": round(obs / ind_same, 2), "ratio_all14": round(obs / ind_full, 2),
            "ratio_wilson_low_same_years": round(lo / ind_same, 2),
            "note": "35 gauge-years are missing, so in many years fewer than 14 gauges could flood. The like-for-like "
                    "chance baseline uses each year's available gauges (3.9 %); 4.4 % assumes all 14 every year "
                    "(the two-level circuit's independent case, 4.42 %, is the same binomial).",
        },
    }
    app = json.loads((ROOT / "web" / "data" / "app.json").read_text())
    pk = app["replay"]["peaks"]["2005"]
    north = [a for a in app["areas"] if a["cluster"] == "North"]
    res["lapland_2005"] = {
        "over_1in10_empirical": [a["area"] for a in north if pk[a["area"]] and pk[a["area"]] >= a["q10_empirical"]],
        "over_1in50_gev": [a["area"] for a in north if pk[a["area"]] and pk[a["area"]] >= a["q50"]],
        "north_snow_percentile": app["replay"]["swe_north_pct"]["2005"] if "2005" in app["replay"]["swe_north_pct"]
        else app["replay"]["swe_north_pct"],
    }
    (OUT / "round3_numbers.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
