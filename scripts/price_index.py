"""Price the Tulva Index (parametric spring-flood cover) per cluster and trigger, with robustness checks.

Cover: pays PAYOUT once in a spring when >= m of the cluster's gauges pass their 1-in-50 spring level.
Premium = P(trigger) x PAYOUT x (1 + RISK_LOAD).
Scenarios: independence (EIOPA 0 %), Tulva fitted model (climatology), full correlation (all at once),
Tulva after a top-15 % / bottom-15 % March snow outlook. Exact (1-D quadrature) and Monte Carlo (>= 1M springs).
Robustness: Student-t copula (df 10, 5) and a year-bootstrap of the fitted loadings.

Inputs:  out/model_params.json, out/snow_skill.json, data/spring_max.csv, data/gauges.csv
Outputs: out/pricing.json, out/index_price.png
Run: .venv/bin/python scripts/price_index.py [--sims 1000000] [--payout 10e6] [--load 0.35] [--boot 200]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tulva import model, pricing as P  # noqa: E402

OUT = ROOT / "out"
P50 = 0.02
MS = (1, 2, 3)
SCEN = ["independent", "tulva", "full_correlation", "tulva_high_outlook", "tulva_low_outlook"]


def r(x, d=6):
    return round(float(x), d)


def bootstrap_h(n_boot: int, clusters: list[str]) -> np.ndarray:
    """Refit the factor model on year-bootstraps (same procedure as fit_dependence.py); returns h per cluster."""
    sm = pd.read_csv(ROOT / "data" / "spring_max.csv", index_col="year")
    g = pd.read_csv(ROOT / "data" / "gauges.csv").set_index("area")
    clus = np.array([clusters.index(g.loc[a, "cluster"]) for a in sm.columns])
    rng = np.random.default_rng(7)
    hs = []
    for _ in range(n_boot):
        s = sm.iloc[rng.integers(0, len(sm), len(sm))]
        Rb = 2 * np.sin(np.pi * s.corr(method="spearman", min_periods=25).values / 6)
        a, b, _ = model.fit_factor(Rb, clus, len(clusters), common_a=True)
        hs.append(np.hypot(a, b))
    return np.array(hs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sims", type=int, default=1_000_000)
    ap.add_argument("--payout", type=float, default=10e6)
    ap.add_argument("--load", type=float, default=0.35)
    ap.add_argument("--boot", type=int, default=200)
    args = ap.parse_args()

    mp = json.loads((OUT / "model_params.json").read_text())
    sk = json.loads((OUT / "snow_skill.json").read_text())["clusters"]
    names = mp["cluster_names"]
    prem = lambda p: P.premium(p, args.payout, args.load)

    res = {"description": "Tulva Index: pays a fixed sum once per spring when >= m of a cluster's gauges pass "
                          "their own 1-in-50 spring (Mar-Jun) peak-discharge level. Premium = P(trigger) x payout "
                          "x (1 + risk load). Model: Gaussian-copula factor model fitted to SYKE/SMHI spring "
                          "maxima 1961-2025 (out/model_params.json); outlook = 1 March SYKE SWE, top/bottom 15 % "
                          "(skill from out/snow_skill.json).",
           "payout_eur": args.payout, "risk_load": args.load, "return_period_years": 50,
           "mc_springs": args.sims, "clusters": {}}

    seed = 100
    for c in names:
        a, b = mp["national_loading"], mp["cluster_loading"][c]
        h = float(np.hypot(a, b))
        n = len(mp["clusters"][c]["areas"])
        s = sk[c]["outlook_skill_vs_latent_factor"]
        cres = {"n_gauges": n, "areas": mp["clusters"][c]["areas"], "national_loading": a, "cluster_loading": b,
                "within_corr": r(h ** 2, 3), "outlook_skill": s, "triggers": {}}
        # Monte Carlo: one simulation per scenario, reused for all m
        mc = {"tulva": P.mc_counts(a, b, n, P50, args.sims, seed=seed),
              "tulva_high_outlook": P.mc_counts(a, b, n, P50, args.sims, s, "high", seed=seed + 1),
              "tulva_low_outlook": P.mc_counts(a, b, n, P50, args.sims, s, "low", seed=seed + 2),
              "t10": P.mc_counts(a, b, n, P50, args.sims, df=10, seed=seed + 3),
              "t5": P.mc_counts(a, b, n, P50, args.sims, df=5, seed=seed + 4)}
        seed += 10
        for m in MS:
            if m > n:
                continue
            ex = {"independent": P.p_trigger_independent(n, m, P50),
                  "tulva": P.p_trigger_exact(n, m, P50, h),
                  "full_correlation": P.p_trigger_comonotone(n, m, P50),
                  "tulva_high_outlook": P.p_trigger_exact(n, m, P50, h, s, "high"),
                  "tulva_low_outlook": P.p_trigger_exact(n, m, P50, h, s, "low")}
            trig = {}
            for k in SCEN:
                d = {"p_exact": r(ex[k], 7), "expected_payout_eur": round(ex[k] * args.payout),
                     "premium_eur": round(prem(ex[k])), "rate_on_line": r(prem(ex[k]) / args.payout, 5),
                     "return_period_years": r(1 / ex[k], 1) if ex[k] > 0 else None}
                if k in mc:
                    pm, se = P.mc_prob(mc[k], m)
                    d["p_mc"], d["p_mc_se"] = r(pm, 7), r(se, 7)
                trig[k] = d
            for df in (10, 5):
                pe = P.p_trigger_t_exact(n, m, P50, h, df)
                pm, se = P.mc_prob(mc[f"t{df}"], m)
                trig[f"tulva_t_copula_df{df}"] = {"p_exact": r(pe, 7), "p_mc": r(pm, 7), "p_mc_se": r(se, 7),
                                                  "premium_eur": round(prem(pe)),
                                                  "vs_gaussian": r(pe / ex["tulva"], 3)}
            trig["mispricing_tulva_vs_independent"] = r(ex["tulva"] / ex["independent"], 3)
            trig["high_vs_low_outlook"] = r(ex["tulva_high_outlook"] / ex["tulva_low_outlook"], 1)
            trig["high_outlook_vs_climatology"] = r(ex["tulva_high_outlook"] / ex["tulva"], 3)
            cres["triggers"][f"ge{m}"] = trig
        res["clusters"][c] = cres

    # ---------------- bootstrap of the loadings -> interval on the ">= 2" price
    hs = bootstrap_h(args.boot, names)
    boot = {"n_boot": args.boot, "method": "year-bootstrap refit of the factor loadings (common national loading), "
            "exact price per refit; outlook skill held fixed", "clusters": {}}
    for k, c in enumerate(names):
        n = len(mp["clusters"][c]["areas"])
        s = sk[c]["outlook_skill_vs_latent_factor"]
        ok = ~np.isnan(hs[:, k])
        pb = np.array([P.p_trigger_exact(n, 2, P50, h) for h in hs[ok, k]])
        pbh = np.array([P.p_trigger_exact(n, 2, P50, h, s, "high") for h in hs[ok, k]])
        mis = pb / P.p_trigger_independent(n, 2, P50)
        q = lambda x: [r(v) for v in np.percentile(x, [5, 50, 95])]
        boot["clusters"][c] = {"ge2_p_5_50_95": q(pb), "ge2_premium_eur_5_50_95": [round(prem(v)) for v in
                                                                                  np.percentile(pb, [5, 50, 95])],
                               "ge2_high_outlook_premium_eur_5_50_95": [round(prem(v)) for v in
                                                                       np.percentile(pbh, [5, 50, 95])],
                               "ge2_mispricing_5_50_95": [r(v, 2) for v in np.percentile(mis, [5, 50, 95])]}
        # also: the price at the ci90 endpoints stored in model_params.json
        ci = mp.get("ci90", {})
        if c in ci:
            lo = np.hypot(ci["national"][0], ci[c][0])
            hi = np.hypot(ci["national"][1], ci[c][1])
            boot["clusters"][c]["ge2_premium_eur_at_ci90_loading_ends"] = [
                round(prem(P.p_trigger_exact(n, 2, P50, min(x, 0.99)))) for x in (lo, hi)]
    res["bootstrap"] = boot

    (OUT / "pricing.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    for c in names:
        for m in MS:
            t = res["clusters"][c]["triggers"].get(f"ge{m}")
            if t:
                print(f"{c:13s} >={m}: indep {t['independent']['premium_eur']:>9,}  tulva {t['tulva']['premium_eur']:>9,}"
                      f" (mc p {t['tulva']['p_mc']:.5f}±{t['tulva']['p_mc_se']:.5f} vs {t['tulva']['p_exact']:.5f})"
                      f"  full {t['full_correlation']['premium_eur']:>9,}  hi {t['tulva_high_outlook']['premium_eur']:>9,}"
                      f"  lo {t['tulva_low_outlook']['premium_eur']:>7,}  x{t['mispricing_tulva_vs_independent']}"
                      f"  t10 x{t['tulva_t_copula_df10']['vs_gaussian']} t5 x{t['tulva_t_copula_df5']['vs_gaussian']}")
        print("   boot", res["bootstrap"]["clusters"][c])
    plot(res)


def plot(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink, ink2, muted, grid, surf = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#fcfcfb"
    rows = [("independent", "Independence\n(EIOPA 0 %)", "#a9a8a2"),
            ("tulva", "Tulva model", "#2a78d6"),
            ("tulva_high_outlook", "Tulva, high-snow\nMarch outlook", "#eb6834"),
            ("tulva_low_outlook", "Tulva, low-snow\nMarch outlook", "#1baf7a")]
    cl = ["Ostrobothnia", "North"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharex=True, facecolor=surf)
    vmax = max(res["clusters"][c]["triggers"]["ge2"][k]["premium_eur"] for c in cl for k, _, _ in rows)
    for ax, c in zip(axes, cl):
        t = res["clusters"][c]["triggers"]["ge2"]
        ax.set_facecolor(surf)
        y = np.arange(len(rows))[::-1]
        for yi, (k, lab, col) in zip(y, rows):
            v = t[k]["premium_eur"]
            ax.barh(yi, v / 1e3, height=0.62, color=col, edgecolor=surf, linewidth=2)
            ax.text(v / 1e3 + vmax / 1e3 * 0.015, yi, f"€{v / 1e3:,.0f}k", va="center", ha="left",
                    fontsize=11, color=ink, fontweight="bold" if k == "tulva" else "normal")
        ax.set_yticks(y, [lab for _, lab, _ in rows] if ax is axes[0] else [""] * len(rows),
                      fontsize=10, color=ink2)
        n = res["clusters"][c]["n_gauges"]
        ax.set_title(f"{c}: pays when ≥2 of {n} gauges pass 1-in-50\n"
                     f"Tulva = {t['mispricing_tulva_vs_independent']:.1f}× the independence price",
                     loc="left", fontsize=11.5, color=ink)
        ax.grid(axis="x", color=grid, linewidth=0.8)
        ax.set_axisbelow(True)
        for sp in ("top", "right", "left"):
            ax.spines[sp].set_visible(False)
        ax.spines["bottom"].set_color(muted)
        ax.tick_params(axis="x", colors=ink2, labelsize=9)
        ax.tick_params(axis="y", length=0)
        ax.set_xlabel("Annual premium, € thousand (€10M cover, 35 % risk load)", fontsize=9.5, color=ink2)
    axes[0].set_xlim(0, vmax / 1e3 * 1.22)
    fig.suptitle("Tulva Index: what a parametric spring-flood cover should cost", x=0.01, ha="left",
                 fontsize=14, color=ink, fontweight="bold")
    fig.text(0.01, 0.01,
             "Data: SYKE daily discharge (14 gauges) and SMHI Tornionjoki, spring (Mar–Jun) peaks 1961–2025; "
             "SYKE 1 March snow water equivalent.\nModel: Gaussian-copula factor model fitted to the peaks; "
             "outlook = top/bottom 15 % of March snow. Premium = P(trigger) × €10M × 1.35.\nExact quadrature; Monte Carlo of "
             f"{res['mc_springs']:,} springs agrees. 1-in-50 levels are model extrapolation beyond the 65-year record.",
             fontsize=8, color=muted, ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.11, 1, 0.97))
    fig.savefig(OUT / "index_price.png", dpi=180, facecolor=surf)


if __name__ == "__main__":
    main()
