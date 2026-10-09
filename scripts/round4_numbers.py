"""Round-4 review numbers for the deck (logged in CLAIMS.md, "Round-4 deck pass").

1. Joint year-bootstrap of the North ">=2 of 5 over 1-in-50" fair price (expected loss, % of limit a year) and of the
   snowy-March ratio: resample the 65 springs (peaks and 1 March SWE together), refit the factor loadings exactly as
   fit_dependence.py / price_index.py do, recompute the North snow skill, and re-price exactly. 90 % intervals.
2. Basis-risk check: did the back-test trigger fire in the known Finnish flood-loss springs (list from the business
   case's loss table, business/reports/Tulva flood cover business case.md §1)? Read from out/backtest.json.
3. Chip vs chip control (14-area loader, IQM Emerald, >=4 of 14 over 1-in-10) and exact correlated vs independent.
4. Grover powers k actually run in the hardware results shown on slides 5 and 9.

    .venv/bin/python scripts/round4_numbers.py   ->  out/round4_numbers.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
sys.path.insert(0, str(ROOT / "src"))
from tulva import model, pricing as P  # noqa: E402

CLUSTERS = ["Ostrobothnia", "North", "Satakunta–SE"]
N_BOOT = 400


def s2g(rs):
    return 2 * np.sin(np.pi * rs / 6)


def north_skill(sm, swe, cats, sel, load):
    """Same estimator as fit_dependence.py: mean Gaussian-converted Spearman(SWE index, gauge) / loading."""
    sidx = model.normal_scores(swe)[[str(x) for x in cats]].mean(axis=1, skipna=True)
    ns = model.normal_scores(sm)
    per = []
    for a in sel:
        d = pd.concat([sidx, ns[a]], axis=1).dropna().values.T
        per.append(stats.spearmanr(*d)[0])
    return min(np.mean(s2g(np.array(per))) / load, 0.99)


def bootstrap():
    sm = pd.read_csv(ROOT / "data" / "spring_max.csv", index_col="year")
    swe = pd.read_csv(ROOT / "data" / "swe_mar1.csv", index_col="year").reindex(sm.index)
    g = pd.read_csv(ROOT / "data" / "gauges.csv").set_index("area")
    clus = np.array([CLUSTERS.index(g.loc[a, "cluster"]) for a in sm.columns])
    k = CLUSTERS.index("North")
    sel = [a for a in sm.columns if g.loc[a, "cluster"] == "North"]
    cats = sorted({int(g.loc[a, "swe_catchment"]) for a in sel})
    n, p50 = len(sel), 0.02

    def fit(s, w):
        R = s2g(s.corr(method="spearman", min_periods=25).values)
        a, b, _ = model.fit_factor(R, clus, 3, common_a=True)
        h = float(np.hypot(a[k], b[k]))
        if not np.isfinite(h):
            return None
        sk = north_skill(s, w, cats, sel, h)
        pt = P.p_trigger_exact(n, 2, p50, min(h, 0.99))
        ph = P.p_trigger_exact(n, 2, p50, min(h, 0.99), sk, "high")
        return pt, ph, sk

    point = fit(sm, swe)
    rng = np.random.default_rng(4)
    res = []
    for _ in range(N_BOOT):
        idx = rng.integers(0, len(sm), len(sm))
        s, w = sm.iloc[idx].reset_index(drop=True), swe.iloc[idx].reset_index(drop=True)
        r = fit(s, w)
        if r is not None:
            res.append(r)
    res = np.array(res)
    q = lambda x: [round(float(v), 5) for v in np.percentile(x, [5, 95])]
    return {
        "method": f"{len(res)} joint year-bootstraps (peaks + 1 March SWE resampled together); loadings refit "
                  "(common national loading) and North snow skill re-estimated per resample; exact pricing",
        "point_refit": {"p_tulva": round(point[0], 5), "p_high_snow": round(point[1], 5),
                        "ratio": round(point[1] / point[0], 3), "skill": round(point[2], 3)},
        "p_tulva_ci90": q(res[:, 0]), "p_high_snow_ci90": q(res[:, 1]),
        "ratio_high_over_tulva_ci90": [round(float(v), 2) for v in np.percentile(res[:, 1] / res[:, 0], [5, 95])],
        "skill_ci90": [round(float(v), 3) for v in np.percentile(res[:, 2], [5, 95])],
    }


def basis_risk():
    bt = json.loads((OUT / "backtest.json").read_text())["clusters"]
    # Known loss springs, business case §1 loss table (outside source): year -> (region, cluster it maps to)
    known = {1966: ("south (snowpack ~2× normal)", "Satakunta–SE"), 2005: ("Lapland", "North"),
             2012: ("Ostrobothnia", "Ostrobothnia"), 2013: ("Ostrobothnia", "Ostrobothnia"),
             2018: ("Lapland, record snow", "North"), 2020: ("Lapland, Kemijoki at Rovaniemi", "North"),
             2024: ("Ostrobothnia worst", "Ostrobothnia")}
    rows = {}
    for y, (reg, c) in known.items():
        b = bt[c]
        rows[str(y)] = {"region": reg, "cluster": c,
                        "trigger_ge2_over_gev_1in10": y in b["trigger_years"],
                        "trigger_ge2_over_gev_1in50": y in b["years_ge2_over_fitted_1in50"],
                        "snow_flag": y in b["outlook_flag_years"],
                        "any_cluster_triggered_1in10": [cc for cc in CLUSTERS if y in bt[cc]["trigger_years"]]}
    return rows


def chip_control():
    r = json.loads((OUT / "runs" / "loader-iqm-emerald-20261008T184433Z.json").read_text())
    c = json.loads((OUT / "runs" / "loader-control-indep-iqm-emerald-20261009T135910Z.json").read_text())
    k = 4
    return {"ge4_chip_corr": round(r["p_at_least_k_readout_corrected"][k], 4),
            "ge4_chip_control": round(c["p_at_least_k_readout_corrected"][k], 4),
            "ge4_exact_corr": round(r["p_at_least_k_exact"][k], 4),
            "ge4_exact_indep": round(c["p_at_least_k_exact"][k], 4),
            "ratio_chip": round(r["p_at_least_k_readout_corrected"][k] / c["p_at_least_k_readout_corrected"][k], 2),
            "ratio_exact": round(r["p_at_least_k_exact"][k] / c["p_at_least_k_exact"][k], 2)}


def k_run():
    out = {}
    for f, inst in [("ibm-ibm_marrakesh-20261008T174523Z.json", "A3_kittila_ivalo_both"),
                    ("iqm-garnet-20261008T182534Z.json", "A3_kittila_ivalo_both"),
                    ("product-iqm-emerald-20261009T075338Z.json", "A3_kittila_ivalo_both_high"),
                    ("ibm-ibm_marrakesh-20261008T170341Z.json", "A3_kittila_ivalo_both")]:
        run = json.loads((OUT / "runs" / f).read_text())
        out[f] = sorted({c["k"] for c in run["circuits"] if c["instance"] == inst})
    out["note"] = ("A3 instances (named kittila_ivalo in the code) use identical North-cluster loadings and trigger "
                   "for both areas (np.full in scripts/run_hw.py instance() and run_product_hw.py): a two-river "
                   "North-cluster pair, not Kittilä and Ivalo specifically")
    return out


def main():
    res = {"north_ge2_of5_bootstrap": bootstrap(), "basis_risk_known_loss_years": basis_risk(),
           "loader_chip_vs_control": chip_control(), "grover_k_in_shown_results": k_run()}
    (OUT / "round4_numbers.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
