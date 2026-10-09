"""Snow + spring temperature + rain flood model, and its 43-qubit circuit.

    python scripts/weather_model.py            # fit, exact answers, back-test -> out/weather_model.json

Per cluster c and year: flood driver D_c = standardised mean normal score of the cluster's spring peaks;
snow s_c = mean z of the cluster's 1 March SWE catchments; t_c, r_c = z of April–May temperature and rain
(data/weather_spring.csv, FMI). Fit D_c = b_s s + b_t t + b_r r + noise by least squares.

Two-level network for the circuit (43 qubits):
  3 national weather qubits (snow, temp, rain: "high" = top 30 %)          -> correlation between regions
  9 cluster weather qubits S_c, T_c, R_c (each from its national qubit)
  3 cluster "wet spring" qubits W_c (top 30 % of D_c), from (S_c, T_c, R_c): 8 fitted probabilities
  14 area qubits "over 1-in-10" and 14 "over 1-in-50" (only if over 1-in-10), from W_c and the fitted loadings
Exact answers come from enumerating the 2^15 weather/cluster states (areas are independent given W_c).
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tulva.factor import p_exceed_given_region, p_region  # noqa: E402

OUT, DATA = ROOT / "out", ROOT / "data"
CLUSTERS = ["Ostrobothnia", "North", "Satakunta–SE"]
VARS = ["snow", "temp", "rain"]
HIGH = 0.7                     # "high" / "wet" = top 30 %
CUT = norm.ppf(HIGH)


def zscore(x: pd.Series) -> pd.Series:
    return (x - x.mean()) / x.std()


def normal_scores(x: pd.Series) -> pd.Series:
    r = x.rank()
    return pd.Series(norm.ppf((r - 0.5) / x.notna().sum()), index=x.index)


def load():
    params = json.loads((OUT / "model_params.json").read_text(encoding="utf-8"))
    sm = pd.read_csv(DATA / "spring_max.csv").set_index("year")
    g = pd.read_csv(DATA / "gauges.csv").set_index("area")
    swe = pd.read_csv(DATA / "swe_mar1.csv").set_index("year")
    w = pd.read_csv(DATA / "weather_spring.csv")
    frames = {}
    for c in CLUSTERS:
        areas = params["clusters"][c]["areas"]
        d = zscore(pd.concat([normal_scores(sm[a]) for a in areas], axis=1).mean(axis=1))
        cats = sorted({str(int(g.loc[a, "swe_catchment"])) for a in areas if not pd.isna(g.loc[a, "swe_catchment"])})
        s = zscore(pd.concat([zscore(swe[k]) for k in cats if k in swe], axis=1).mean(axis=1))
        wc = w[w.cluster == c].set_index("year")
        frames[c] = pd.DataFrame({"D": d, "snow": s, "temp": zscore(wc.t_aprmay), "rain": zscore(wc.rain_aprmay)})
    return params, sm, g, frames


def fit(frames):
    out = {}
    for c, f in frames.items():
        f = f.dropna()
        X = f[VARS].values
        b, *_ = np.linalg.lstsq(X, f.D.values, rcond=None)
        r2 = 1 - np.var(f.D.values - X @ b) / np.var(f.D.values)
        b1, *_ = np.linalg.lstsq(f[["snow"]].values, f.D.values, rcond=None)
        r2s = 1 - np.var(f.D.values - f.snow.values * b1[0]) / np.var(f.D.values)
        out[c] = {"years": len(f), "beta": dict(zip(VARS, map(float, b))), "r2_all": float(r2), "r2_snow": float(r2s),
                  "corr_xx": np.corrcoef(X.T).round(3).tolist()}
    return out


def national_loadings(frames):
    """a_v = sqrt(mean pairwise correlation of variable v across clusters)."""
    a = {}
    for v in VARS:
        df = pd.concat({c: frames[c][v] for c in CLUSTERS}, axis=1).dropna()
        cc = df.corr().values[np.triu_indices(3, 1)]
        a[v] = float(np.sqrt(max(0.0, cc.mean())))
    return a


def p_wet_given_combo(beta, corr, rng, n=2_000_000):
    """P(D > CUT | each of the 8 high/low combinations of (snow, temp, rain)), within-cluster correlation kept."""
    x = rng.multivariate_normal(np.zeros(3), np.array(corr), size=n)
    b = np.array([beta[v] for v in VARS])
    sd = np.sqrt(max(1e-6, 1 - b @ np.array(corr) @ b))
    d = x @ b + sd * rng.standard_normal(n)
    hi = x > CUT
    res = {}
    for combo in itertools.product([0, 1], repeat=3):
        m = np.all(hi == np.array(combo, bool), axis=1)
        res["".join(map(str, combo))] = float((d[m] > CUT).mean())
    return res


def build(params, frames, fitres, rng):
    a = national_loadings(frames)
    net = {"high_quantile": HIGH, "national": {v: {"p_high": 1 - HIGH, "loading": a[v]} for v in VARS},
           "clusters": {}}
    for c in CLUSTERS:
        cw = {v: [p_exceed_given_region(CUT, a[v], lo, hi) for lo, hi in ((-np.inf, CUT), (CUT, np.inf))] for v in VARS}
        pw = p_wet_given_combo(fitres[c]["beta"], fitres[c]["corr_xx"], rng)
        cl = params["clusters"][c]
        r = float(np.hypot(cl["national_loading"], cl["cluster_loading"]))   # corr(area, cluster driver)
        areas = []
        for name in cl["areas"]:
            p10 = [p_exceed_given_region(norm.isf(0.1), r, lo, hi) for lo, hi in ((-np.inf, CUT), (CUT, np.inf))]
            p50 = [p_exceed_given_region(norm.isf(0.02), r, lo, hi) for lo, hi in ((-np.inf, CUT), (CUT, np.inf))]
            areas.append({"area": name, "p10": p10, "p50_given_10": [p50[i] / p10[i] for i in range(2)]})
        net["clusters"][c] = {"weather_given_national": cw, "p_wet_given_stw": pw, "areas": areas}
    return net


def count_dist(ps):
    d = np.array([1.0])
    for p in ps:
        d = np.convolve(d, [1 - p, p])
    return d


def exact(net):
    """Enumerate national (3) x cluster weather (9) x W (3) states; areas independent given W."""
    cl = [net["clusters"][c] for c in CLUSTERS]
    pn = 1 - HIGH
    res = {"north_ge2_50": 0.0, "all_ge4_10": 0.0, "north_ge2_50_by_stw": {}, "p_stw_north": {}}
    north = CLUSTERS.index("North")
    # per-cluster, per-W count distributions
    d10 = [[count_dist([a["p10"][w] for a in c["areas"]]) for w in (0, 1)] for c in cl]
    d50 = [[count_dist([a["p10"][w] * a["p50_given_10"][w] for a in c["areas"]]) for w in (0, 1)] for c in cl]
    acc = {}
    for nat in itertools.product([0, 1], repeat=3):
        p_nat = np.prod([pn if x else 1 - pn for x in nat])
        per_cluster = []
        for c in cl:
            dist_w = {}   # (stw, w) -> prob
            for stw in itertools.product([0, 1], repeat=3):
                p = np.prod([c["weather_given_national"][v][nat[i]] if stw[i] else 1 - c["weather_given_national"][v][nat[i]]
                             for i, v in enumerate(VARS)])
                pw = c["p_wet_given_stw"]["".join(map(str, stw))]
                dist_w[(stw, 1)] = p * pw
                dist_w[(stw, 0)] = p * (1 - pw)
            per_cluster.append(dist_w)
        # North marginals
        for (stw, w), p in per_cluster[north].items():
            key = "".join(map(str, stw))
            acc.setdefault(key, [0.0, 0.0])
            acc[key][0] += p_nat * p
            acc[key][1] += p_nat * p * d50[north][w][2:].sum()
            res["north_ge2_50"] += p_nat * p * d50[north][w][2:].sum()
        # all 14 over 1-in-10: convolve cluster count distributions over W states
        cw = [{w: sum(p for (s, ww), p in pc.items() if ww == w) for w in (0, 1)} for pc in per_cluster]
        tot = np.array([1.0])
        for i in range(3):
            tot = np.convolve(tot, cw[i][0] * d10[i][0] + cw[i][1] * d10[i][1])
        res["all_ge4_10"] += p_nat * tot[4:].sum()
    for k, (p, pe) in acc.items():
        res["p_stw_north"][k] = p
        res["north_ge2_50_by_stw"][k] = pe / p
    return res


def backtest(sm, g, frames, fitres, params):
    """Payout cluster-years (≥2 gauges over fitted GEV 1-in-10): how many are in the top-15 % predicted years?"""
    out = {}
    for which in ("snow", "all"):
        hits = total = 0
        for c in CLUSTERS:
            f = frames[c].dropna()
            pred = f.snow * fitres[c]["beta"]["snow"] if which == "snow" else f[VARS].values @ np.array(
                [fitres[c]["beta"][v] for v in VARS])
            pred = pd.Series(np.asarray(pred), index=f.index)
            if which == "snow":   # snow-only regression coefficient
                b1 = np.linalg.lstsq(f[["snow"]].values, f.D.values, rcond=None)[0][0]
                pred = f.snow * b1
            areas = params["clusters"][c]["areas"]
            over = sum((sm.loc[f.index, a] > g.loc[a, "q10_gev"]).astype(int) for a in areas)
            pay = over >= 2
            flag = pred >= pred.quantile(0.85)
            hits += int((pay & flag).sum())
            total += int(pay.sum())
        out[which] = {"hits": hits, "payout_years": total}
    return out


def main():
    rng = np.random.default_rng(1)
    params, sm, g, frames = load()
    fitres = fit(frames)
    net = build(params, frames, fitres, rng)
    ex = exact(net)
    bt = backtest(sm, g, frames, fitres, params)
    res = {"fit": fitres, "network": net, "exact": ex, "backtest_top15": bt,
           "note": "In-sample. Temperature and rain are observed April–May values, i.e. a perfect-forecast upper bound."}
    (OUT / "weather_model.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    for c in CLUSTERS:
        f = fitres[c]
        print(f"{c:13s} R² snow only {f['r2_snow']:.2f} -> snow+temp+rain {f['r2_all']:.2f}  beta "
              + " ".join(f"{v}={f['beta'][v]:+.2f}" for v in VARS))
    print("national loadings", {v: round(net['national'][v]['loading'], 2) for v in VARS})
    print(f"exact: P(≥2 of 5 North over 1-in-50) {100*ex['north_ge2_50']:.2f} %, P(≥4 of 14 over 1-in-10) {100*ex['all_ge4_10']:.1f} %")
    for k in ("000", "100", "110", "111", "011"):
        print(f"  North snow/temp/rain high={k}: P {100*ex['north_ge2_50_by_stw'][k]:.2f} %  (weight {100*ex['p_stw_north'][k]:.1f} %)")
    print("back-test top-15 % flags:", bt)


if __name__ == "__main__":
    main()
