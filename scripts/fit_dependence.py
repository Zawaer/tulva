"""Fit the joint flood model to spring maxima and measure the March-snow signal.

Inputs:  data/spring_max.csv, data/gauges.csv, data/swe_mar1.csv (from build_dataset.py)
Outputs: out/model_params.json, out/joint_counts.json, out/snow_skill.json, out/dependence.json
Run: .venv/bin/python scripts/fit_dependence.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.cluster import hierarchy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tulva import model  # noqa: E402

OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)
CLUSTERS = ["Ostrobothnia", "North", "Satakunta–SE"]
P10, P50 = 0.1, 0.02
N_BOOT = 400
SNOW_TOP = 0.15


def r(x, d=3):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), d)


def spearman_to_gauss(rs):
    return 2 * np.sin(np.pi * rs / 6)


def pair_multiplier(ex: pd.DataFrame, pairs):
    obs = exp = 0.0
    for i, j in pairs:
        d = ex[[i, j]].dropna()
        obs += (d[i] * d[j]).sum()
        exp += len(d) * d[i].mean() * d[j].mean()
    return obs, exp


def main():
    sm = pd.read_csv(ROOT / "data" / "spring_max.csv", index_col="year")
    gauges = pd.read_csv(ROOT / "data" / "gauges.csv")
    swe = pd.read_csv(ROOT / "data" / "swe_mar1.csv", index_col="year")
    areas = list(sm.columns)
    cl_of = dict(zip(gauges.area, gauges.cluster))
    clus = np.array([CLUSTERS.index(cl_of[a]) for a in areas])
    n = len(areas)

    # ---------------- correlations
    rs = sm.corr(method="spearman", min_periods=30)
    R = spearman_to_gauss(rs.values)
    iu = np.triu_indices(n, 1)
    same = (clus[:, None] == clus[None, :])[iu]
    rs_u = rs.values[iu]
    dep = {
        "spearman_within_mean": r(rs_u[same].mean()), "spearman_between_mean": r(rs_u[~same].mean()),
        "spearman_all_mean": r(rs_u.mean()),
        "spearman_block_mean": {
            f"{CLUSTERS[c]} x {CLUSTERS[d]}": r(np.mean([rs.values[i, j] for i in range(n) for j in range(n)
                                                          if clus[i] == c and clus[j] == d and i != j]))
            for c in range(3) for d in range(c, 3)},
        "spearman_matrix": {a: {b: r(rs.loc[a, b]) for b in areas} for a in areas},
    }

    # ---------------- joint exceedance multiplier (pairs both over own 1-in-10)
    ex = model.exceed(sm, P10)
    pairs = [(areas[i], areas[j]) for i, j in zip(*iu)]
    mult = {}
    for name, sel in [("within", same), ("between", ~same)]:
        o, e = pair_multiplier(ex, [p for p, s in zip(pairs, sel) if s])
        mult[name] = {"observed_pairs": int(o), "expected_independent": r(e, 1), "multiplier": r(o / e, 2)}
    for c, cn in enumerate(CLUSTERS):
        o, e = pair_multiplier(ex, [(areas[i], areas[j]) for i, j in zip(*iu) if clus[i] == c and clus[j] == c])
        mult[cn] = {"observed_pairs": int(o), "expected_independent": r(e, 1), "multiplier": r(o / e, 2)}
    dep["joint_exceedance_1in10"] = mult

    # ---------------- factor model fits
    a1, b1, rm1 = model.fit_factor(R, clus, 3, common_a=True)
    a3, b3, rm3 = model.fit_factor(R, clus, 3, common_a=False)

    # bootstrap the main (common national loading) fit over years
    rng = np.random.default_rng(1)
    boots = []
    for _ in range(N_BOOT):
        s = sm.iloc[rng.integers(0, len(sm), len(sm))]
        Rb = spearman_to_gauss(s.corr(method="spearman", min_periods=25).values)
        a, b, _ = model.fit_factor(Rb, clus, 3, common_a=True)
        boots.append(np.r_[a[0], b])
    lo, hi = np.nanpercentile(np.array(boots), [5, 95], axis=0)

    # data-driven grouping for comparison: average linkage on 1 - R
    D = 1 - np.clip(R, -1, 1)
    np.fill_diagonal(D, 0)
    Z = hierarchy.linkage(D[iu], method="average")
    dd = {}
    for k in (3, 4):
        lab = hierarchy.fcluster(Z, k, criterion="maxclust") - 1
        a_, b_, rm_ = model.fit_factor(R, lab, k, common_a=True)
        dd[f"{k}_groups"] = {"groups": [[areas[i] for i in range(n) if lab[i] == g] for g in range(k)],
                             "national": r(a_[0]), "cluster": [r(x) for x in b_], "rmse": r(rm_)}

    # ---------------- per-gauge return levels
    g_idx = gauges.set_index("area")
    params = {
        "description": "Gaussian-copula factor model on spring (Mar–Jun) max discharge, 1961–2025. "
                       "Z_i = a*F + b_c*G_c + sqrt(1-a^2-b_c^2)*e_i; gauge i over its 1-in-T level iff "
                       "Z_i > Phi^-1(1-1/T). Fit: least squares on off-diagonal copula correlations "
                       "(rho = 2 sin(pi*rho_s/6)).",
        "cluster_names": CLUSTERS,
        "clusters": {c: {"national_loading": r(a1[0]), "cluster_loading": r(b1[k]),
                         "within_corr": r(a1[0] ** 2 + b1[k] ** 2),
                         "areas": [a for a in areas if cl_of[a] == c]} for k, c in enumerate(CLUSTERS)},
        "national_loading": r(a1[0]),
        "cluster_loading": {c: r(b1[k]) for k, c in enumerate(CLUSTERS)},
        "ci90": {"national": [r(lo[0]), r(hi[0])],
                 **{c: [r(lo[k + 1]), r(hi[k + 1])] for k, c in enumerate(CLUSTERS)}},
        "fit_rmse": r(rm1),
        "alt_per_cluster_national_loading": {
            "national": {c: r(a3[k]) for k, c in enumerate(CLUSTERS)},
            "cluster": {c: r(b3[k]) for k, c in enumerate(CLUSTERS)}, "fit_rmse": r(rm3)},
        "alt_data_driven_grouping": dd,
        "gauges": [{
            "area": a, "cluster": cl_of[a], "gauge": g_idx.loc[a, "gauge"], "source": g_idx.loc[a, "source"],
            "years": int(g_idx.loc[a, "years"]),
            "q10_m3s": r(g_idx.loc[a, "q10_gev"], 1), "q50_m3s": r(g_idx.loc[a, "q50_gev"], 1),
            "p10": P10, "p50": P50,
            "z10": r(stats.norm.ppf(1 - P10), 4), "z50": r(stats.norm.ppf(1 - P50), 4),
        } for a in areas],
    }
    a_m, b_m = a1, b1

    # cluster trigger: >=2 gauges in a cluster over 1-in-50 (the product)
    trig = {}
    for k, c in enumerate(CLUSTERS):
        idx = clus == k
        pm = model.count_pmf(a_m, b_m, np.full(idx.sum(), k), P50)
        trig[c] = {"n_gauges": int(idx.sum()), "p_ge2_model": r(model.at_least(pm)[2], 5),
                   "p_ge2_independent": r(model.at_least(model.poisson_binomial(np.full(idx.sum(), P50)))[2], 5)}
    params["cluster_trigger_ge2_over_1in50"] = trig

    # ---------------- joint counts: years with >= k areas over own 1-in-10
    counts = ex.sum(axis=1, min_count=1)
    avail = ex.notna()
    ks = list(range(1, n + 1))
    obs = {k: float((counts >= k).mean()) for k in ks}
    # model / independence on the same gauge-years as observed (average over each year's available set)
    mod_same, ind_same = np.zeros(n + 1), np.zeros(n + 1)
    cache = {}
    for y in sm.index:
        m = tuple(avail.loc[y].values)
        if m not in cache:
            sel = np.array(m)
            cache[m] = (np.pad(model.at_least(model.count_pmf(a_m, b_m, clus[sel], P10)), (0, n + 1 - sel.sum() - 1)),
                        np.pad(model.at_least(model.poisson_binomial(np.full(sel.sum(), P10))), (0, n + 1 - sel.sum() - 1)))
        mod_same += cache[m][0]
        ind_same += cache[m][1]
    mod_same /= len(sm)
    ind_same /= len(sm)
    full_mod = model.at_least(model.count_pmf(a_m, b_m, clus, P10))
    full_ind = model.at_least(model.poisson_binomial(np.full(n, P10)))
    mc = model.simulate(a_m, b_m, clus, 200_000, seed=7)
    mc_cnt = (mc > stats.norm.ppf(1 - P10)).sum(axis=1)
    m50 = model.at_least(model.count_pmf(a_m, b_m, clus, P50))
    i50 = model.at_least(model.poisson_binomial(np.full(n, P50)))
    jc = {
        "definition": "Per year, number of the 14 areas whose spring peak is in its own top 10% (1961–2025). "
                      "P(>=k) per year. 'same_years' versions use each year's available gauges, matching observed.",
        "n_years": len(sm), "gauge_years_missing": int((~avail).values.sum()),
        "k": ks,
        "observed": [r(obs[k], 4) for k in ks],
        "observed_years": {k: [int(y) for y in counts.index[counts >= k]] for k in ks if obs[k] > 0 and k >= 3},
        "observed_n_years": [int((counts >= k).sum()) for k in ks],
        "model_same_years": [r(mod_same[k], 4) for k in ks],
        "independent_same_years": [r(ind_same[k], 4) for k in ks],
        "model_full14": [r(full_mod[k], 5) for k in ks],
        "model_full14_montecarlo_200k": [r((mc_cnt >= k).mean(), 5) for k in ks],
        "independent_full14": [r(full_ind[k], 6) for k in ks],
        "all_at_once_full14": [P10 for _ in ks],
        "one_in_50": {"k": ks[:6], "model": [r(m50[k], 5) for k in ks[:6]],
                      "independent": [r(i50[k], 6) for k in ks[:6]]},
        "max_observed_count": int(counts.max()), "max_observed_year": int(counts.idxmax()),
    }

    # ---------------- snow skill (1 March catchment SWE)
    ns = model.normal_scores(sm)
    swe_ns = model.normal_scores(swe)
    snow = {"definition": "SWE index = mean normal score of 1 March areal SWE over the cluster's catchments; "
                          "flood index = mean normal score of the cluster's spring peaks. Top years = top 15% "
                          "of the SWE index.", "clusters": {}}
    for k, c in enumerate(CLUSTERS + ["National"]):
        sel = [a for a in areas if c == "National" or cl_of[a] == c]
        cats = sorted({int(g_idx.loc[a, "swe_catchment"]) for a in sel})
        sidx = swe_ns[[str(x) for x in cats]].mean(axis=1, skipna=True)
        fidx = ns[sel].mean(axis=1, skipna=True)
        d = pd.concat([sidx.rename("s"), fidx.rename("f"), ex[sel].sum(axis=1, min_count=1).rename("cnt")], axis=1).dropna()
        rho = stats.spearmanr(d.s, d.f)[0]
        top = d.s >= d.s.quantile(1 - SNOW_TOP)
        # skill vs the cluster's latent factor: corr(s, Z_i) = skill * sqrt(a^2 + b_c^2)
        per = [stats.spearmanr(*pd.concat([sidx, ns[a]], axis=1).dropna().values.T)[0] for a in sel]
        load = np.sqrt(a_m[0] ** 2 + b_m[k] ** 2) if c != "National" else a_m[0]
        snow["clusters"][c] = {
            "swe_catchments": cats, "years": len(d),
            "spearman_swe_vs_flood_index": r(rho),
            "spearman_swe_vs_each_gauge": {a: r(spearman_to_gauss(v)) for a, v in zip(sel, per)},
            "outlook_skill_vs_latent_factor": r(min(np.mean(spearman_to_gauss(np.array(per))) / load, 0.99)),
            "n_top_years": int(top.sum()), "top_years": [int(y) for y in d.index[top]],
            "p_ge2_over_1in10_top_snow": r((d.cnt[top] >= 2).mean()),
            "p_ge2_over_1in10_other": r((d.cnt[~top] >= 2).mean()),
            "p_ge2_over_1in10_below_median_snow": r((d.cnt[d.s < d.s.median()] >= 2).mean()),
        }

    (OUT / "model_params.json").write_text(json.dumps(params, indent=1, ensure_ascii=False))
    (OUT / "joint_counts.json").write_text(json.dumps(jc, indent=1, ensure_ascii=False))
    (OUT / "snow_skill.json").write_text(json.dumps(snow, indent=1, ensure_ascii=False))
    (OUT / "dependence.json").write_text(json.dumps(dep, indent=1, ensure_ascii=False))

    print("Spearman within/between:", dep["spearman_within_mean"], dep["spearman_between_mean"])
    print("Multiplier:", {k: v["multiplier"] for k, v in mult.items()})
    print("Loadings national", params["national_loading"], params["ci90"]["national"], "cluster",
          params["cluster_loading"], "rmse", params["fit_rmse"])
    print("Alt per-cluster national:", params["alt_per_cluster_national_loading"])
    print("Data-driven:", json.dumps(dd, ensure_ascii=False))
    print("Trigger >=2 over 1-in-50:", trig)
    for k in range(2, 9):
        print(f"k>={k}: obs {obs[k]:.3f} ({jc['observed_n_years'][k-1]} y)  model {mod_same[k]:.3f}  "
              f"indep {ind_same[k]:.4f}  | full14 model {full_mod[k]:.4f} mc {(mc_cnt>=k).mean():.4f} indep {full_ind[k]:.5f}")
    print("Years >=4:", jc["observed_years"].get(4))
    print("1-in-50 model/indep:", jc["one_in_50"])
    for c, v in snow["clusters"].items():
        print(c, {k: v[k] for k in ("years", "spearman_swe_vs_flood_index", "outlook_skill_vs_latent_factor",
                                    "p_ge2_over_1in10_top_snow", "p_ge2_over_1in10_other")})


if __name__ == "__main__":
    main()
