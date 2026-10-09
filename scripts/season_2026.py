"""Spring 2026 check: what the model said on 1 March 2026 (snow only) vs what the rivers did by June.

    python scripts/season_2026.py            -> web/data/season2026.json (+ prints a summary)

Out-of-sample by construction: the model is fitted on 1961–2025 (data/, out/model_params.json, out/snow_skill.json);
2026 snow and discharge are fetched here from SYKE (Virtaama, LumiAlue) and SMHI (Torne), cached in
data/raw/season2026/ (git-ignored). Prediction = the same factor model the web app uses (export_web.p_atleast),
conditioned on the cluster's 1 March 2026 SWE percentile. Result = each gauge's Mar–Jun 2026 peak vs its empirical
1-in-10 level (replay rule) and its GEV 1-in-50 level (product trigger).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binom, norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tulva import syke  # noqa: E402

OUT, DATA, WEB = ROOT / "out", ROOT / "data", ROOT / "web" / "data"
RAW = DATA / "raw" / "season2026"
YEAR = 2026
CLUSTERS = ["Ostrobothnia", "North", "Satakunta–SE"]


def p_atleast(k: int, n: int, z: float, h: float, mean: float = 0.0, sd: float = 1.0) -> float:
    """P(at least k of n areas exceed z); area latent = h*D + sqrt(1-h^2)*e, D ~ N(mean, sd)."""
    d = np.linspace(mean - 8 * sd, mean + 8 * sd, 1601)
    w = norm.pdf(d, mean, sd)
    w /= w.sum()
    p = norm.sf((z - h * d) / math.sqrt(1 - h * h))
    return float((w * binom.sf(k - 1, n, p)).sum())


def expected_over(n: int, z: float, h: float, mean: float, sd: float) -> float:
    d = np.linspace(mean - 8 * sd, mean + 8 * sd, 1601)
    w = norm.pdf(d, mean, sd)
    w /= w.sum()
    return float(n * (w * norm.sf((z - h * d) / math.sqrt(1 - h * h))).sum())


def cached(name: str, fetch):
    p = RAW / name
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    RAW.mkdir(parents=True, exist_ok=True)
    rows = fetch()
    p.write_text(json.dumps(rows), encoding="utf-8")
    return rows


def series(rows: list[dict]) -> pd.Series:
    if not rows:
        return pd.Series(dtype=float)
    df = pd.DataFrame(rows)
    s = pd.Series(pd.to_numeric(df["Arvo"], errors="coerce").values, index=pd.to_datetime(df["Aika"]).dt.normalize())
    return s[~s.index.duplicated()].sort_index().dropna()


def discharge_2026(g: syke.Gauge) -> pd.Series:
    if g.smhi_id is not None:
        return syke.smhi_discharge(g.smhi_id)      # full corrected archive, cached in data/raw
    out = pd.Series(dtype=float)
    for pid in g.syke_ids:
        rows = cached(f"Virtaama_{pid}.json",
                      lambda pid=pid: syke.odata_all("Virtaama", f"Paikka_Id eq {pid} and Aika ge datetime'{YEAR}-01-01T00:00:00'"))
        s = series(rows)
        out = s if out.empty else out.combine_first(s)
    return out.sort_index()


def swe_1march_2026(pid: int) -> float | None:
    rows = cached(f"LumiAlue_{pid}.json",
                  lambda: syke.odata_all("LumiAlue", f"Paikka_Id eq {pid} and Aika ge datetime'{YEAR}-02-20T00:00:00' "
                                                     f"and Aika le datetime'{YEAR}-03-10T00:00:00'"))
    s = series(rows)
    key = pd.Timestamp(f"{YEAR}-03-01")
    if key in s.index:
        return float(s[key])
    return float(s.iloc[(abs(s.index - key)).argmin()]) if len(s) else None


def main():
    params = json.loads((OUT / "model_params.json").read_text(encoding="utf-8"))
    skill = json.loads((OUT / "snow_skill.json").read_text(encoding="utf-8"))
    gauges = pd.read_csv(DATA / "gauges.csv").set_index("area")
    swe_hist = pd.read_csv(DATA / "swe_mar1.csv").set_index("year")

    # 1 March 2026 snow per catchment, appended to the 1961–2025 table
    cats = sorted({int(c) for c in swe_hist.columns})
    swe26 = {c: swe_1march_2026(c) for c in cats}
    swe_all = swe_hist.copy()
    swe_all.loc[YEAR] = [swe26.get(int(c)) for c in swe_hist.columns]
    swe_all.columns = [int(c) for c in swe_all.columns]

    # Spring 2026 peaks
    peaks = {}
    for g in syke.GAUGES:
        q = discharge_2026(g)
        spring = q[(q.index >= f"{YEAR}-03-01") & (q.index <= f"{YEAR}-06-30")]
        peaks[g.area] = {"peak": (None if spring.empty else round(float(spring.max()), 1)),
                         "peak_date": (None if spring.empty else spring.idxmax().strftime("%Y-%m-%d")),
                         "days": int(spring.notna().sum()),
                         "last_day": (None if q.empty else q.index.max().strftime("%Y-%m-%d"))}

    out = {"year": YEAR, "fitted_on": "1961–2025", "clusters": {}, "snow_mm_2026": {str(k): v for k, v in swe26.items()},
           "sources": "SYKE Hydrologiarajapinta (Virtaama daily discharge, LumiAlue areal SWE), SMHI 16722 (Torne); "
                      "values for 2026 are provisional"}
    z50, z10 = norm.isf(1 / 50), norm.isf(0.1)
    for cname in CLUSTERS:
        c = params["clusters"][cname]
        h = math.sqrt(c["national_loading"] ** 2 + c["cluster_loading"] ** 2)
        n = len(c["areas"])
        s = skill["clusters"][cname]["outlook_skill_vs_latent_factor"]
        swe_c = skill["clusters"][cname]["swe_catchments"]
        df = swe_all[[int(x) for x in swe_c]].astype(float)
        ns = pd.DataFrame(norm.ppf(df.rank() / (df.notna().sum() + 1)), index=df.index, columns=df.columns)
        idx = ns.mean(axis=1, skipna=True).dropna()
        vals = idx.values
        pct = float((vals < idx[YEAR]).sum() + 0.5) / len(vals) * 100
        o = norm.ppf(pct / 100)
        mean, sd = s * o, math.sqrt(1 - s * s)
        areas = []
        n_over10 = n_over50 = 0
        for a in c["areas"]:
            pk = peaks[a]
            q10, q50 = float(gauges.loc[a, "q10_empirical"]), float(gauges.loc[a, "q50_gev"])
            over10 = pk["peak"] is not None and pk["peak"] > q10
            over50 = pk["peak"] is not None and pk["peak"] > q50
            n_over10 += over10
            n_over50 += over50
            areas.append({"area": a, "gauge": gauges.loc[a, "gauge"], "peak_2026": pk["peak"], "peak_date": pk["peak_date"],
                          "days_with_data": pk["days"], "q10_empirical": q10, "q50_gev": q50,
                          "ratio_to_q10": (None if pk["peak"] is None else round(pk["peak"] / q10, 2)),
                          "over_1in10": bool(over10), "over_1in50": bool(over50)})
        out["clusters"][cname] = {
            "n": n, "snow_pct_2026": round(pct, 1), "snow_mm_2026_by_catchment": {str(k): swe26.get(int(k)) for k in swe_c},
            "predicted": {
                "p_ge2_1in50": p_atleast(2, n, z50, h, mean, sd), "p_ge2_1in50_average_year": p_atleast(2, n, z50, h),
                "p_ge2_1in10": p_atleast(2, n, z10, h, mean, sd), "p_ge2_1in10_average_year": p_atleast(2, n, z10, h),
                "p_ge1_1in10": p_atleast(1, n, z10, h, mean, sd), "p_ge1_1in10_average_year": p_atleast(1, n, z10, h),
                "expected_areas_over_1in10": expected_over(n, z10, h, mean, sd),
                "expected_areas_over_1in10_average_year": expected_over(n, z10, h, 0.0, 1.0),
                "src": "exact", "note": "factor model (1961–2025 fit) conditioned on the cluster's 1 March 2026 SWE percentile"},
            "result": {"areas_over_1in10": n_over10, "areas_over_1in50": n_over50, "payout": bool(n_over50 >= 2),
                       "src": "data"},
            "areas": areas,
        }
    WEB.mkdir(parents=True, exist_ok=True)
    (WEB / "season2026.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", WEB / "season2026.json")
    for cname, c in out["clusters"].items():
        p = c["predicted"]
        print(f"{cname:13s} snow {c['snow_pct_2026']:5.1f} pct | P(≥2 over 1-in-10) {100*p['p_ge2_1in10']:.1f} % (avg {100*p['p_ge2_1in10_average_year']:.1f}) "
              f"| payout chance {100*p['p_ge2_1in50']:.2f} % (avg {100*p['p_ge2_1in50_average_year']:.2f}) "
              f"| expected areas over 1-in-10 {p['expected_areas_over_1in10']:.2f} -> actual {c['result']['areas_over_1in10']} of {c['n']}, over 1-in-50 {c['result']['areas_over_1in50']}")
        for a in c["areas"]:
            print(f"    {a['area']:22s} peak {a['peak_2026']} on {a['peak_date']} ({a['days_with_data']} d) = {a['ratio_to_q10']}× its 1-in-10 level")


if __name__ == "__main__":
    main()
