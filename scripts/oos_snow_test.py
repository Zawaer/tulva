"""Out-of-sample test of the 1 March snow warning.

Everything that is fitted is fitted on a TRAINING block of springs only, then frozen and evaluated on the
held-out TEST block:
  - per-gauge GEV (L-moments) 1-in-10 and 1-in-50 spring levels,
  - the per-catchment SWE and per-gauge discharge normal-score transforms (training empirical CDF),
  - the copula factor loadings (national + cluster, least squares on training Spearman correlations),
  - the snow skill (corr of the cluster SWE index with the cluster's latent factor),
  - the top-15 % snow cut-off (85th percentile of the training SWE index).
Main split: train 1961-2000, test 2001-2025. Robustness (reverse): train 1986-2025, test 1961-1985.

Evaluated on the test block, per cluster:
  - Spearman(March SWE index, cluster flood index), in-sample (training) vs out-of-sample (test);
  - hit table: snow flag (SWE index >= frozen cut-off) vs index trigger (>= 2 of the cluster's gauges over the
    frozen GEV 1-in-10 level);
  - predicted risk ratio P(trigger | flag) / P(trigger | no flag) from the training fit (exact, pricing.py
    quadrature) vs the observed ratio in the test years, with Clopper-Pearson intervals, Fisher exact p and a
    year-bootstrap interval.

Inputs:  data/spring_max.csv, data/swe_mar1.csv, data/gauges.csv
Outputs: out/oos_snow_test.json, out/OOS_SNOW_TEST.md
Run: .venv/bin/python scripts/oos_snow_test.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tulva import model, pricing as P  # noqa: E402

OUT = ROOT / "out"
CLUSTERS = ["Ostrobothnia", "North", "Satakunta–SE"]
TOP, M, P10, P50 = 0.15, 2, 0.1, 0.02
N_BOOT = 4000
SPLITS = {"main": ((1961, 2000), (2001, 2025)), "reverse": ((1986, 2025), (1961, 1985))}


def r(x, d=3):
    if x is None:
        return None
    x = float(x)
    if np.isnan(x):
        return None
    if np.isinf(x):
        return "inf"
    return round(x, d)


def g2r(rs):
    return 2 * np.sin(np.pi * np.asarray(rs) / 6)


def ecdf_scores(train: pd.Series, x: pd.Series) -> pd.Series:
    """Normal score of x under the training empirical CDF: Phi^-1((#train <= x + 0.5) / (n + 1))."""
    t = np.sort(train.dropna().values)
    n = len(t)
    u = (np.searchsorted(t, x.values, side="right") + 0.5) / (n + 1)
    out = stats.norm.ppf(np.clip(u, 0.5 / (n + 1), 1 - 0.5 / (n + 1)))
    return pd.Series(np.where(x.notna(), out, np.nan), index=x.index)


def clopper(k, n, conf=0.90):
    if n == 0:
        return [None, None]
    a = (1 - conf) / 2
    lo = 0.0 if k == 0 else stats.beta.ppf(a, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(1 - a, k + 1, n - k)
    return [r(lo), r(hi)]


def boot_ratio(trig: np.ndarray, flag: np.ndarray, rng, n_boot=N_BOOT):
    """Year-bootstrap 90 % interval of P(trig|flag)/P(trig|no flag); resamples with no flagged or no unflagged
    years are dropped; 0/0 dropped; x/0 counted as +inf."""
    n = len(trig)
    vals = []
    for _ in range(n_boot):
        i = rng.integers(0, n, n)
        t, f = trig[i], flag[i]
        if f.sum() == 0 or (~f).sum() == 0:
            continue
        a, b = t[f].mean(), t[~f].mean()
        if a == 0 and b == 0:
            continue
        vals.append(np.inf if b == 0 else a / b)
    if not vals:
        return [None, None], 0
    vals = np.sort(vals)
    q = lambda f: vals[min(len(vals) - 1, int(np.floor(f * len(vals))))]
    return [r(q(0.05), 2), r(q(0.95), 2)], len(vals)


def boot_spearman(x: np.ndarray, y: np.ndarray, rng, n_boot=N_BOOT):
    n = len(x)
    v = [stats.spearmanr(x[i], y[i])[0] for i in (rng.integers(0, n, n) for _ in range(n_boot))]
    return [r(np.nanpercentile(v, 5)), r(np.nanpercentile(v, 95))]


def fit(sm, swe, cats, areas, clus, train):
    """Fit everything on the training years only."""
    smt, swt = sm.loc[train[0]:train[1]], swe.loc[train[0]:train[1]]
    q10 = {}
    q50 = {}
    for a in areas:
        g = model.gev_lmom(smt[a].values)
        q10[a], q50[a] = model.return_level(g, 10), model.return_level(g, 50)
    R = g2r(smt.corr(method="spearman", min_periods=20).values)
    av, bv, rmse = model.fit_factor(R, clus, 3, common_a=True)
    par = {"train": list(train), "q10": q10, "q50": q50, "national_loading": float(av[0]),
           "cluster_loading": {c: float(bv[k]) for k, c in enumerate(CLUSTERS)}, "fit_rmse": float(rmse),
           "clusters": {}}
    for k, c in enumerate(CLUSTERS):
        sel = [a for a in areas if clus[areas.index(a)] == k]
        sidx = swt[[str(x) for x in cats[c]]].apply(lambda s: ecdf_scores(s, s)).mean(axis=1, skipna=True)
        h = float(np.hypot(av[0], bv[k]))
        per = [stats.spearmanr(*pd.concat([sidx, smt[a]], axis=1).dropna().values.T)[0] for a in sel]
        skill = float(min(np.mean(g2r(per)) / h, 0.99))
        cut = float(sidx.dropna().quantile(1 - TOP))
        n = len(sel)
        p_clim = P.p_trigger_exact(n, M, P10, h)
        p_hi = P.p_trigger_exact(n, M, P10, h, skill, "high")
        p_rest = (p_clim - TOP * p_hi) / (1 - TOP)
        p50_clim = P.p_trigger_exact(n, M, P50, h)
        p50_hi = P.p_trigger_exact(n, M, P50, h, skill, "high")
        par["clusters"][c] = {"areas": sel, "swe_catchments": cats[c], "h": h, "skill": skill,
                              "snow_cutoff_swe_index": cut,
                              "pred_p_trigger_1in10_flag": p_hi, "pred_p_trigger_1in10_noflag": p_rest,
                              "pred_p_trigger_1in10_climatology": p_clim,
                              "pred_ratio_flag_vs_noflag": p_hi / p_rest,
                              "pred_ratio_flag_vs_climatology": p_hi / p_clim,
                              "pred_1in50_ge2_climatology": p50_clim, "pred_1in50_ge2_flag": p50_hi,
                              "pred_1in50_ratio_flag_vs_climatology": p50_hi / p50_clim}
    return par


def evaluate(sm, swe, par, years, block, rng):
    """Apply the frozen fit to the given block of years."""
    train = par["train"]
    smt, swt = sm.loc[train[0]:train[1]], swe.loc[train[0]:train[1]]
    sb, wb = sm.loc[block[0]:block[1]], swe.loc[block[0]:block[1]]
    out = {}
    for c, pc in par["clusters"].items():
        sel = pc["areas"]
        cols = [str(x) for x in pc["swe_catchments"]]
        sidx = pd.concat([ecdf_scores(swt[x], wb[x]) for x in cols], axis=1).mean(axis=1, skipna=True)
        fidx = pd.concat([ecdf_scores(smt[a], sb[a]) for a in sel], axis=1).mean(axis=1, skipna=True)
        over = sb[sel].gt(pd.Series(par["q10"])[sel]).where(sb[sel].notna())
        cnt = over.sum(axis=1, min_count=1)
        d = pd.concat([sidx.rename("s"), fidx.rename("f"), cnt.rename("cnt")], axis=1).dropna()
        trig = (d.cnt >= M).values
        flag = (d.s >= pc["snow_cutoff_swe_index"]).values
        rho, pval = stats.spearmanr(d.s, d.f)
        # sensitivity (not the main test): cut-off = 85th pct of the preceding 30 springs' SWE index (known on 1 March)
        sall = pd.concat([ecdf_scores(swt[x], swe[x]) for x in cols], axis=1).mean(axis=1, skipna=True)
        cut_tr = np.array([sall.loc[y - 30:y - 1].dropna().quantile(1 - TOP) for y in d.index])
        flag_tr = d.s.values >= cut_tr
        t2 = [int((trig & flag_tr).sum()), int((~trig & flag_tr).sum()), int((trig & ~flag_tr).sum()),
              int((~trig & ~flag_tr).sum())]
        k11, k10 = int((trig & flag).sum()), int((~trig & flag).sum())
        k01, k00 = int((trig & ~flag).sum()), int((~trig & ~flag).sum())
        nf, nn = k11 + k10, k01 + k00
        pf = k11 / nf if nf else np.nan
        pn = k01 / nn if nn else np.nan
        ratio = (np.inf if pn == 0 and pf > 0 else (np.nan if pn == 0 else pf / pn))
        ci_ratio, nb = boot_ratio(trig, flag, rng)
        if nf < 3:  # with 0-2 flagged years the bootstrap ratio is degenerate; do not report it
            ci_ratio, nb = [None, None], 0
        # calibration vs the frozen model: binomial test of observed triggers in flagged / unflagged years
        ef, en = nf * pc["pred_p_trigger_1in10_flag"], nn * pc["pred_p_trigger_1in10_noflag"]
        out[c] = {
            "years": int(len(d)),
            "spearman_swe_vs_flood_index": r(rho), "spearman_p_one_sided": r(pval / 2 if rho > 0 else 1 - pval / 2, 4),
            "spearman_ci90_bootstrap": boot_spearman(d.s.values, d.f.values, rng),
            "flag_years": [int(y) for y in d.index[flag]],
            "trigger_years": [int(y) for y in d.index[trig]],
            "hits": [int(y) for y in d.index[trig & flag]],
            "false_alarms": [int(y) for y in d.index[~trig & flag]],
            "misses": [int(y) for y in d.index[trig & ~flag]],
            "table": {"flag_trigger": k11, "flag_no_trigger": k10, "noflag_trigger": k01, "noflag_no_trigger": k00},
            "p_trigger_flag": r(pf), "p_trigger_flag_ci90": clopper(k11, nf),
            "p_trigger_noflag": r(pn), "p_trigger_noflag_ci90": clopper(k01, nn),
            "observed_ratio": r(ratio, 2), "observed_ratio_ci90_bootstrap": ci_ratio, "bootstrap_valid": nb,
            "fisher_p_one_sided": r(stats.fisher_exact([[k11, k10], [k01, k00]], alternative="greater")[1], 4),
            "trigger_rate_all": r(trig.mean()), "pred_trigger_rate_all": r(pc["pred_p_trigger_1in10_climatology"]),
            "expected_triggers_flag": r(ef, 2), "expected_triggers_noflag": r(en, 2),
            "gauge_exceed_rate_1in10": r(np.nanmean(over.values)),
            "mean_swe_index": r(d.s.mean(), 2), "mean_flood_index": r(d.f.mean(), 2),
            "sensitivity_trailing30_cutoff": {
                "flag_years": [int(y) for y in d.index[flag_tr]],
                "table": dict(zip(["flag_trigger", "flag_no_trigger", "noflag_trigger", "noflag_no_trigger"], t2)),
                "fisher_p_one_sided": r(stats.fisher_exact([[t2[0], t2[1]], [t2[2], t2[3]]],
                                                           alternative="greater")[1], 4)},
        }
    return out


def pooled(ev):
    t = {k: sum(v["table"][k] for v in ev.values()) for k in next(iter(ev.values()))["table"]}
    nf, nn = t["flag_trigger"] + t["flag_no_trigger"], t["noflag_trigger"] + t["noflag_no_trigger"]
    pf, pn = t["flag_trigger"] / nf, t["noflag_trigger"] / nn
    ef = sum(v["expected_triggers_flag"] for v in ev.values())
    en = sum(v["expected_triggers_noflag"] for v in ev.values())
    return {"table": t, "p_trigger_flag": r(pf), "p_trigger_flag_ci90": clopper(t["flag_trigger"], nf),
            "p_trigger_noflag": r(pn), "p_trigger_noflag_ci90": clopper(t["noflag_trigger"], nn),
            "observed_ratio": r(np.inf if pn == 0 else pf / pn, 2),
            "hit_rate": r(t["flag_trigger"] / max(1, t["flag_trigger"] + t["noflag_trigger"])),
            "fisher_p_one_sided": r(stats.fisher_exact([[t["flag_trigger"], t["flag_no_trigger"]],
                                                        [t["noflag_trigger"], t["noflag_no_trigger"]]],
                                                       alternative="greater")[1], 4),
            "model_expected_triggers_flag": r(ef, 2), "model_expected_triggers_noflag": r(en, 2),
            "sensitivity_trailing30_cutoff": (lambda u: {"table": u, "fisher_p_one_sided": r(stats.fisher_exact(
                [[u["flag_trigger"], u["flag_no_trigger"]], [u["noflag_trigger"], u["noflag_no_trigger"]]],
                alternative="greater")[1], 4)})({k: sum(v["sensitivity_trailing30_cutoff"]["table"][k]
                                                    for v in ev.values()) for k in t}),
            "note": "pooled over the 3 clusters (cluster-years); clusters share years, so not independent"}


def main():
    sm = pd.read_csv(ROOT / "data" / "spring_max.csv", index_col="year")
    swe = pd.read_csv(ROOT / "data" / "swe_mar1.csv", index_col="year")
    gauges = pd.read_csv(ROOT / "data" / "gauges.csv")
    areas = list(sm.columns)
    cl_of = dict(zip(gauges.area, gauges.cluster))
    g_idx = gauges.set_index("area")
    clus = np.array([CLUSTERS.index(cl_of[a]) for a in areas])
    cats = {c: sorted({int(g_idx.loc[a, "swe_catchment"]) for a in areas if cl_of[a] == c}) for c in CLUSTERS}
    rng = np.random.default_rng(2026)

    res = {"description": __doc__.strip().split("\n\n")[0],
           "definitions": {"flag": "cluster SWE index (mean training-ECDF normal score of 1 March SWE over the "
                                   "cluster's catchments) >= training 85th percentile",
                           "trigger": ">= 2 of the cluster's gauges over the training-fitted GEV 1-in-10 level",
                           "flood_index": "mean training-ECDF normal score of the cluster's spring peaks",
                           "pred_ratio": "exact P(trigger | top-15 % outlook) / P(trigger | rest) from the training "
                                         "loadings and skill (pricing.p_trigger_exact)",
                           "intervals": "90 %: Clopper-Pearson for frequencies, year-bootstrap (4000) for ratio and "
                                        "Spearman"},
           "splits": {}}
    for name, (train, test) in SPLITS.items():
        par = fit(sm, swe, cats, areas, clus, train)
        ins = evaluate(sm, swe, par, None, train, rng)
        oos = evaluate(sm, swe, par, None, test, rng)
        sp = {"train": f"{train[0]}–{train[1]}", "test": f"{test[0]}–{test[1]}",
              "fit": {"national_loading": r(par["national_loading"]),
                      "cluster_loading": {c: r(v) for c, v in par["cluster_loading"].items()},
                      "q10_gev": {a: r(v, 1) for a, v in par["q10"].items()},
                      "clusters": {c: {k: (r(v, 4) if isinstance(v, float) else v) for k, v in pc.items()
                                       if k not in ("areas",)} for c, pc in par["clusters"].items()}},
              "in_sample": ins, "out_of_sample": oos,
              "pooled_in_sample": pooled(ins), "pooled_out_of_sample": pooled(oos)}
        res["splits"][name] = sp
        print(f"\n=== {name}: train {sp['train']} test {sp['test']}  loadings a={par['national_loading']:.2f} "
              f"b={ {c: round(v, 2) for c, v in par['cluster_loading'].items()} }")
        for c in CLUSTERS:
            pc, i, o = par["clusters"][c], ins[c], oos[c]
            print(f"{c:13s} skill {pc['skill']:.2f} predRatio {pc['pred_ratio_flag_vs_noflag']:.1f} "
                  f"(P {pc['pred_p_trigger_1in10_flag']:.2f}/{pc['pred_p_trigger_1in10_noflag']:.3f}) "
                  f"1in50 hi/clim {pc['pred_1in50_ratio_flag_vs_climatology']:.2f} | "
                  f"rho in {i['spearman_swe_vs_flood_index']} oos {o['spearman_swe_vs_flood_index']} "
                  f"{o['spearman_ci90_bootstrap']} | OOS table {o['table']} flags {o['flag_years']} "
                  f"trig {o['trigger_years']} ratio {o['observed_ratio']} {o['observed_ratio_ci90_bootstrap']} "
                  f"fisher {o['fisher_p_one_sided']} exp {o['expected_triggers_flag']}/{o['expected_triggers_noflag']}"
                  f" exceed {o['gauge_exceed_rate_1in10']} swe {o['mean_swe_index']} fl {o['mean_flood_index']}"
                  f"\n      trailing30: {o['sensitivity_trailing30_cutoff']}")
        print("pooled in ", sp["pooled_in_sample"])
        print("pooled oos", sp["pooled_out_of_sample"])
    (OUT / "oos_snow_test.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
