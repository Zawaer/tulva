"""Export everything the demo web app needs into web/data/app.json (and pricing.json).

    python scripts/export_web.py

Reads only generated files in out/ and data/. Every number carries a `src` label:
exact / monte-carlo / qae-sim / qae-sim-noisy / qae-q20 / qae-ibm / qae-iqm / data / placeholder.
out/pricing.json (index-cover prices) and hardware runs in out/runs/ (latest IBM / IQM QAE run, 14-area
loader on IQM Emerald, Qrisp run) fill in automatically when they exist;
rerun this script after they appear.
"""
from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.stats import binom, norm

ROOT = Path(__file__).resolve().parents[1]
OUT, DATA, WEB = ROOT / "out", ROOT / "data", ROOT / "web" / "data"

PAYOUT_EUR = 10_000_000
EDGE_MIN_SPEARMAN = 0.6          # draw a map line when spring peaks correlate at least this much
SLIDER_PCTS = list(range(5, 100, 5))

# Approximate town coordinates of each flood-risk area (lat, lon); display only.
COORDS = {
    "Lapväärtti": (62.24, 21.53),
    "Ilmajoki–Seinäjoki": (62.73, 22.58),
    "Laihia": (62.98, 22.01),
    "Ylistaro–Koivulahti": (62.94, 22.51),
    "Alavieska–Ylivieska": (64.10, 24.45),
    "Lower Pyhäjoki": (64.45, 24.30),
    "Pudasjärvi": (65.36, 26.99),
    "Ivalo": (68.66, 27.54),
    "Kittilä": (67.65, 24.91),
    "Rovaniemi": (66.50, 25.73),
    "Tornio": (65.85, 24.15),
    "Pori": (61.48, 21.80),
    "Huittinen": (61.18, 22.70),
    "Lower Kymijoki": (60.68, 26.83),
}


NE_URL = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
          "ne_50m_admin_0_countries.geojson")
BASEMAP_COUNTRIES = {"Finland", "Aland", "Sweden", "Norway", "Russia", "Estonia"}
BBOX = (5.0, 53.0, 50.0, 74.0)   # lon_min, lat_min, lon_max, lat_max


def basemap() -> dict:
    """Country outlines (Natural Earth 1:50m, public domain) clamped to a box around Finland, cached in data/raw."""
    cache = DATA / "raw" / "ne_50m_admin_0_countries.geojson"
    if not cache.exists():
        import urllib.request
        cache.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(NE_URL, cache)
    fc = json.loads(cache.read_text(encoding="utf-8"))
    x0, y0, x1, y1 = BBOX

    def clamp(ring):
        out = []
        for lon, lat in ring:
            pt = [round(min(max(lon, x0), x1), 3), round(min(max(lat, y0), y1), 3)]
            if not out or out[-1] != pt:
                out.append(pt)
        return out

    feats = []
    for f in fc["features"]:
        name = f["properties"]["ADMIN"]
        if name not in BASEMAP_COUNTRIES:
            continue
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        keep = []
        for poly in polys:
            xs = [c[0] for c in poly[0]]
            ys = [c[1] for c in poly[0]]
            if max(xs) < x0 or min(xs) > x1 or max(ys) < y0 or min(ys) > y1:
                continue
            rings = [clamp(r) for r in poly]
            if len(rings[0]) >= 4:
                keep.append(rings)
        if keep:
            feats.append({"type": "Feature", "properties": {"name": name, "home": name in ("Finland", "Aland")},
                          "geometry": {"type": "MultiPolygon", "coordinates": keep}})
    return {"type": "FeatureCollection", "source": "Natural Earth 1:50m admin-0 (public domain)", "features": feats}


def load(p: Path):
    return json.loads(p.read_text()) if p.exists() else None


def read_csv(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(x):
    try:
        v = float(x)
        return None if math.isnan(v) else v
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- factor-model trigger probability

GH_X, GH_W = np.polynomial.hermite_e.hermegauss(120)   # probabilists' Gauss-Hermite: E[f(X)], X~N(0,1)
GH_W = GH_W / GH_W.sum()


def p_atleast(k: int, n: int, z: float, h: float, mean: float = 0.0, sd: float = 1.0) -> float:
    """P(>=k of n gauges have Z_i > z), Z_i = C + sqrt(1-h^2) e_i, C ~ N(h*mean, h^2 * sd^2) the cluster's
    common factor (national + cluster loading, h^2 = a^2 + b^2)."""
    c = h * (mean + sd * GH_X)
    p = norm.sf((z - c) / math.sqrt(1 - h * h))
    return float(np.sum(GH_W * binom.sf(k - 1, n, p)))


def p_atleast_tail(k: int, n: int, z: float, h: float, s: float, side: str, q: float = 0.15) -> float:
    """Same, given the March outlook O (corr s with the common factor) is in its top / bottom fraction q."""
    lo, hi = (norm.isf(q), 8.0) if side == "high" else (-8.0, norm.ppf(q))
    o = np.linspace(lo, hi, 801)
    w = norm.pdf(o)
    w /= w.sum()
    sd = math.sqrt(1 - s * s)
    return float(sum(wi * p_atleast(k, n, z, h, mean=s * oi, sd=sd) for oi, wi in zip(o, w)))


def cluster_swe_index(swe_rows: list[dict], catchments: list[int]) -> dict[int, float]:
    """Mean normal score of 1 March SWE over the cluster's catchments, as in out/snow_skill.json."""
    # Same as fit_dependence.py (model.normal_scores + nan-mean): missing years are skipped, not ranked top.
    import pandas as pd
    years = [int(r["year"]) for r in swe_rows]
    df = pd.DataFrame({c: [num(r[str(c)]) for r in swe_rows] for c in catchments}, index=years, dtype=float)
    ns = pd.DataFrame(norm.ppf(df.rank() / (df.notna().sum() + 1)), index=df.index, columns=df.columns)
    idx = ns.mean(axis=1, skipna=True).dropna()
    return {int(y): float(v) for y, v in idx.items()}


# ---------------------------------------------------------------- pricing.json (other agent) merge

def normalise_pricing(raw) -> dict:
    """Pass out/pricing.json through untouched plus a best-effort flat view: cluster -> {key: value}."""
    if raw is None:
        return {"status": "pending", "note": "out/pricing.json not produced yet; prices shown as placeholders."}
    view_keys = {"indep": "independent", "tulva": "tulva", "high": "tulva_high_outlook", "low": "tulva_low_outlook",
                 "full": "full_correlation"}
    flat = {}
    for cname, c in (raw.get("clusters") or {}).items():
        t = (c.get("triggers") or {}).get("ge2") or {}
        flat[cname] = {}
        for view, key in view_keys.items():
            d = t.get(key)
            if not isinstance(d, dict) or d.get("premium_eur") is None:
                continue
            note = (f"P = {d.get('p_exact')} (exact); premium = P × payout × (1 + {raw.get('risk_load')} risk load)"
                    + (f"; Monte Carlo check P = {d['p_mc']} ± {d.get('p_mc_se')}" if d.get("p_mc") is not None else ""))
            flat[cname][view] = {"v": d["premium_eur"], "p": d.get("p_exact"), "p_mc": d.get("p_mc"),
                                 "market": d.get("market_premium_eur"),
                                 "rate_on_line": d.get("rate_on_line"), "src": "exact", "note": note}
            st = (c.get("staged_ge2_half_ge3_full") or {}).get(key)
            if st:
                flat[cname][view]["staged"] = {"v": st["premium_eur"], "market": st["market_premium_eur"],
                                               "expected_payout": st["expected_payout_eur"]}
        boot = ((raw.get("bootstrap") or {}).get("clusters") or {}).get(cname) or {}
        if boot.get("ge2_premium_eur_5_50_95"):
            flat[cname]["tulva_boot90"] = boot["ge2_premium_eur_5_50_95"]
    return {"status": "ready", "generated_from": "out/pricing.json", "risk_load": raw.get("risk_load"),
            "market_multiples": raw.get("market_multiples"), "market_note": raw.get("market_note"),
            "payout_eur": raw.get("payout_eur"), "flat": flat, "raw": raw}


# ---------------------------------------------------------------- QAE / hardware runs

def run_src(name: str) -> str | None:
    """Source label of a run file in out/runs/ (None = rehearsal on a fake backend / simulator)."""
    if name.startswith("ibm-ibm"):
        return "qae-ibm"
    if name.startswith(("iqm-garnet", "iqm-emerald", "iqm-radiance")):
        return "qae-iqm"
    if name.startswith(("q20", "q50")):
        return "qae-q20"
    return None


def runs_summary() -> list[dict]:
    res = []
    for a in sorted((OUT / "runs").glob("*.analysis.json"), key=lambda p: p.name.rsplit("-", 1)[-1]):
        run = load(a.with_name(a.name.replace(".analysis.json", ".json"))) or {}
        backend = run.get("backend", a.name.split("-2026")[0])
        res.append({"file": f"out/runs/{a.name}", "backend": backend, "device": run.get("device"),
                    "src": run_src(a.name) or "qae-sim-noisy", "ems": run.get("ems"), "jobs": run.get("jobs", []),
                    "best_qubits": bool(run.get("layout_triples")),
                    "param_source": run.get("param_source"), "created_utc": run.get("created_utc"),
                    "instances": load(a) or {}})
    return res


def hardware_summary(runs: list[dict]) -> dict:
    """Latest real-hardware QAE result per platform and instance, the latest 14-area loader run, the latest Qrisp run."""
    qae = {}
    for inst in ("A3_kittila_ivalo_both", "A4_lapland_atleast2of3"):
        rows = {}
        for r in runs:                       # sorted by timestamp: later runs overwrite earlier ones
            s = r["instances"].get(inst)
            if r["src"] == "qae-sim-noisy" or not s:
                continue
            corr = s["noise_aware_mlae"]  # pooled noise-aware MLAE = the bootstrap_ci.py estimator (deck: 0.149 % IBM, 0.164 % Garnet)
            rows[r["src"]] = {
                "src": r["src"], "platform": {"qae-ibm": "IBM", "qae-iqm": "IQM", "qae-q20": "Aalto"}[r["src"]],
                "device": r["device"] or r["backend"], "jobs": r["jobs"], "file": r["file"], "created_utc": r["created_utc"],
                "best_qubits": r["best_qubits"], "copies": s.get("copies", 1), "shots": s["shots"],
                "exact": s["exact"], "raw": s["raw_mlae"], "corrected": corr, "k0": s["k0_only"],
                "two_qubit_gates_by_k": s["two_qubit_gates_by_k"], "oracle_queries": s["oracle_queries"],
                "mc_rmse_same_queries": s["mc_rmse_same_queries"]}
        key = "kittila_ivalo_both" if inst.startswith("A3") else "lapland_atleast2of3"
        qae[key] = [rows[k] for k in ("qae-ibm", "qae-iqm", "qae-q20") if k in rows]

    loader = None
    # only the 1-in-10 run is comparable with the observed years; the 1-in-50 run is a separate "noise limit" result
    lf = [f for f in sorted((OUT / "runs").glob("loader-iqm-emerald-*.json")) if abs(load(f).get("level", 0) - 0.1) < 1e-9]
    if lf:
        r = load(lf[-1])
        obs = (r.get("observed_reference") or {}).get("observed") or load(OUT / "joint_counts.json")["observed"]
        ks = list(range(2, 8))
        loader = {"file": f"out/runs/{lf[-1].name}", "device": r["device"], "jobs": r["jobs"], "shots": r["shots"],
                  "qubits": r["qubits"], "two_qubit_gates": r["two_qubit_gates"], "created_utc": r["created_utc"],
                  "readout_flip": [r["readout_p01"], r["readout_p10"]], "level": r["level"], "k": ks,
                  "hardware": [r["p_at_least_k_readout_corrected"][k] for k in ks],
                  "hardware_raw": [r["p_at_least_k_raw"][k] for k in ks],
                  "exact": [r["p_at_least_k_exact"][k] for k in ks],
                  "independent": [r["p_at_least_k_independent"][k] for k in ks],
                  "observed": [obs[k - 1] for k in ks]}
        # control: the identical circuit with the correlations switched off, same chip and gate count
        cf = sorted((OUT / "runs").glob("loader-control-indep-iqm-emerald-*.json"))
        if cf:
            c = load(cf[-1])
            loader["control"] = [c["p_at_least_k_readout_corrected"][k] for k in ks]
            loader["control_file"] = f"out/runs/{cf[-1].name}"
            loader["control_jobs"] = c["jobs"]

    qrisp = None
    qf = sorted((OUT / "runs").glob("qrisp_qae_iqm_*.json"))
    if qf:
        r = load(qf[-1])
        c = r["instances"]["climatology"]
        qrisp = {"file": f"out/runs/{qf[-1].name}", "backend": r["backend"], "raw_mlae": c["mlae_mean"],
                 "exact": c["exact"], "shots_per_k": r["shots_per_k"],
                 "cz_by_k": [v["qrisp_iqm_pass_manager"]["cz"] for v in r["gate_counts_garnet"].values()]}
    return {"qae": qae, "loader": loader, "qrisp": qrisp}


NORTH_CLUSTER = "North"


def main() -> None:
    WEB.mkdir(parents=True, exist_ok=True)
    gauges = read_csv(DATA / "gauges.csv")
    params = load(OUT / "model_params.json")
    dep = load(OUT / "dependence.json")
    skill = load(OUT / "snow_skill.json")
    counts = load(OUT / "joint_counts.json")
    qae = load(OUT / "qae_sim.json")
    swe = read_csv(DATA / "swe_mar1.csv")
    smax = read_csv(DATA / "spring_max.csv")

    g_by = {g["area"]: g for g in params["gauges"]}
    areas = []
    for g in gauges:
        a = g["area"]
        lat, lon = COORDS[a]
        areas.append({"area": a, "cluster": g["cluster"], "gauge": g["gauge"], "source": g["source"],
                      "lat": lat, "lon": lon, "years": int(g["years"]),
                      "q10": g_by[a]["q10_m3s"], "q50": g_by[a]["q50_m3s"],
                      "record_max": num(g["record_max"]), "record_max_year": int(g["record_max_year"])})
    names = [a["area"] for a in areas]

    sm = dep["spearman_matrix"]
    edges = [{"a": x, "b": y, "rho": sm[x][y]} for i, x in enumerate(names) for y in names[i + 1:]
             if sm[x][y] >= EDGE_MIN_SPEARMAN]

    # Cluster trigger: >=2 gauges over their 1-in-50 level, under three views and a range of March outlooks.
    clusters = {}
    # Lead with the North (Lapland) cluster: spring-flood risk there is roughly stable to ~2050 (SYKE/FMI).
    order = sorted(params["cluster_names"], key=lambda c: c != "North")
    for cname in order:
        c = params["clusters"][cname]
        a_, b_ = c["national_loading"], c["cluster_loading"]
        h = math.sqrt(a_ * a_ + b_ * b_)
        n = len(c["areas"])
        z50 = norm.isf(1 / 50)
        s = skill["clusters"][cname]["outlook_skill_vs_latent_factor"]
        p_ind = float(binom.sf(1, n, 1 / 50))
        p_clim = p_atleast(2, n, z50, h)
        p_high = p_atleast_tail(2, n, z50, h, s, "high")
        p_low = p_atleast_tail(2, n, z50, h, s, "low")
        by_pct = {}
        for pct in SLIDER_PCTS:
            o = norm.ppf(pct / 100)
            by_pct[str(pct)] = p_atleast(2, n, z50, h, mean=s * o, sd=math.sqrt(1 - s * s))
        idx = cluster_swe_index(swe, skill["clusters"][cname]["swe_catchments"])
        yrs = sorted(idx)
        latest = yrs[-1]
        vals = np.array([idx[y] for y in yrs])
        latest_pct = float((vals < idx[latest]).sum() + 0.5) / len(vals) * 100
        clusters[cname] = {
            "areas": c["areas"], "n": n, "national_loading": a_, "cluster_loading": b_,
            "outlook_skill": s,
            "spearman_swe_vs_flood": skill["clusters"][cname]["spearman_swe_vs_flood_index"],
            "p_independent": {"v": p_ind, "src": "exact", "note": "independence (no co-flooding): binomial, each gauge 2 %/yr"},
            "p_tulva": {"v": p_clim, "src": "exact", "note": "factor model, Gauss–Hermite quadrature",
                        "check_model_params": params["cluster_trigger_ge2_over_1in50"][cname]["p_ge2_model"]},
            "p_high_outlook": {"v": p_high, "src": "exact", "note": "factor model given a top-15 % 1 March SWE"},
            "p_low_outlook": {"v": p_low, "src": "exact", "note": "factor model given a bottom-15 % 1 March SWE"},
            "p_by_snow_pct": {"v": by_pct, "src": "exact",
                              "note": "factor model conditioned on 1 March SWE percentile; in-sample snow skill"},
            "latest_march": {"year": latest, "pct": round(latest_pct, 1), "src": "data",
                             "note": "SYKE areal SWE 1 March, cluster index percentile among 1961–" + str(latest)},
            "observed": {"p_ge2_1in10_top_snow": skill["clusters"][cname]["p_ge2_over_1in10_top_snow"],
                         "p_ge2_1in10_other": skill["clusters"][cname]["p_ge2_over_1in10_other"],
                         "n_top_years": skill["clusters"][cname]["n_top_years"], "src": "exact"},
        }

    # Year replay: each area's spring peak vs its fitted 1-in-10 level.
    # Level = the gauge's own empirical 90th percentile, strict ">" (same rule as out/joint_counts.json).
    import pandas as pd
    df = pd.DataFrame([{a: num(r[a]) for a in names} for r in smax], index=[int(r["year"]) for r in smax])
    thr = df.quantile(0.9)
    for a in areas:
        a["q10_empirical"] = round(float(thr[a["area"]]), 2)
    replay = {str(y): {a: (None if pd.isna(v) else float(v)) for a, v in row.items()} for y, row in df.iterrows()}
    swe_nat = cluster_swe_index(swe, skill["clusters"]["National"]["swe_catchments"])
    nat_vals = np.array(list(swe_nat.values()))
    swe_pct = {str(y): round(float((nat_vals < v).sum() + 0.5) / len(nat_vals) * 100) for y, v in swe_nat.items()}
    swe_north = cluster_swe_index(swe, skill["clusters"][NORTH_CLUSTER]["swe_catchments"])
    north_vals = np.array(list(swe_north.values()))
    north_top = set(skill["clusters"][NORTH_CLUSTER]["top_years"])
    swe_north_pct = {str(y): {"pct": round(float((north_vals < v).sum() + 0.5) / len(north_vals) * 100),
                              "top15": y in north_top} for y, v in swe_north.items()}

    runs = runs_summary()
    app = {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "payout_eur": PAYOUT_EUR,
        "edge_min_spearman": EDGE_MIN_SPEARMAN,
        "areas": areas,
        "edges": edges,
        "dependence": {"within": dep["spearman_within_mean"], "between": dep["spearman_between_mean"],
                       "joint_1in10": dep["joint_exceedance_1in10"], "src": "exact"},
        "clusters": clusters,
        "joint_counts": {"observed_years_ge4": counts["observed_years"].get("4", []),
                         "max_year": counts["max_observed_year"], "max_count": counts["max_observed_count"]},
        "replay": {"peaks": replay, "swe_national_pct": swe_pct, "swe_north_pct": swe_north_pct, "src": "data",
                   "level_src": "the gauge's empirical 1-in-10 level (top 10 % of its 1961–2025 spring peaks), as in out/joint_counts.json"},
        "qae": qae,
        "runs": runs,
        "hardware": hardware_summary(runs),
    }
    (WEB / "app.json").write_text(json.dumps(app, ensure_ascii=False, indent=1))
    (WEB / "basemap.json").write_text(json.dumps(basemap(), ensure_ascii=False, separators=(",", ":")))
    (WEB / "pricing.json").write_text(json.dumps(normalise_pricing(load(OUT / "pricing.json")),
                                                 ensure_ascii=False, indent=1))
    print(f"wrote {WEB/'app.json'} ({len(areas)} areas, {len(edges)} edges); pricing:",
          "ready" if (OUT / "pricing.json").exists() else "pending")
    for k, v in clusters.items():
        print(f"  {k}: indep {v['p_independent']['v']:.4f}  tulva {v['p_tulva']['v']:.4f} "
              f"(model_params {v['p_tulva']['check_model_params']})  p10 {v['p_by_snow_pct']['v']['10']:.4f} "
              f"p90 {v['p_by_snow_pct']['v']['90']:.4f} hi {v['p_high_outlook']['v']:.4f} lo {v['p_low_outlook']['v']:.4f}  latest {v['latest_march']}")


if __name__ == "__main__":
    main()
