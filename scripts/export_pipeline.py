"""Export the "from data to answer" walkthrough for the web app: web/data/pipeline.json.

    python scripts/export_pipeline.py

One worked example end to end: will Kittilä and Ivalo both pass their 1-in-50 spring level?
Inputs (SYKE spring peaks, 1 March snow), the four numbers the model hands to the circuit, the real IQM Emerald
shots, and the estimate vs the exact answer, for a low-snow, normal and snowy March.
Reads data/, out/model_params.json, out/snow_skill.json and the product-iqm-emerald runs in out/runs/.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tulva import factor  # noqa: E402

OUT, DATA, WEB = ROOT / "out", ROOT / "data", ROOT / "web" / "data"
AREAS = ["Kittilä", "Ivalo"]
RUN_K0 = "product-iqm-emerald-20261009T073815Z"       # 1 copy: clean per-shot counts to show
RUN_BEST = "product-iqm-emerald-20261009T075338Z"     # 10 copies: the estimate we quote


def main():
    sm = pd.read_csv(DATA / "spring_max.csv")
    g = pd.read_csv(DATA / "gauges.csv").set_index("area")
    sw = pd.read_csv(DATA / "swe_mar1.csv")
    rivers = {a: {"gauge": g.loc[a, "gauge"], "q50": float(g.loc[a, "q50_gev"]),
                  "peaks": {int(y): (None if pd.isna(v) else round(float(v))) for y, v in zip(sm.year, sm[a])}}
              for a in AREAS}
    cat = {a: str(int(g.loc[a, "swe_catchment"])) for a in AREAS}
    snow_idx = sw.set_index("year")[[cat[a] for a in AREAS]].mean(axis=1).dropna()
    snow = {"catchments": cat, "mm": {int(y): round(float(v)) for y, v in snow_idx.items()},
            "p15": round(float(snow_idx.quantile(0.15))), "p50": round(float(snow_idx.quantile(0.5))),
            "p85": round(float(snow_idx.quantile(0.85)))}

    north = json.loads((OUT / "model_params.json").read_text())["clusters"]["North"]
    skill = json.loads((OUT / "snow_skill.json").read_text())["clusters"]["North"]["outlook_skill_vs_latent_factor"]
    shift = skill * norm.pdf(norm.ppf(0.85)) / 0.15
    k0 = json.loads((OUT / "runs" / f"{RUN_K0}.json").read_text())
    best = json.loads((OUT / "runs" / f"{RUN_BEST}.analysis.json").read_text())
    best_run = json.loads((OUT / "runs" / f"{RUN_BEST}.json").read_text())

    cases = {}
    for key, s in (("low", -shift), ("clim", 0.0), ("high", shift)):
        m = factor.build_two_level(np.full(2, north["national_loading"]), np.full(2, north["cluster_loading"]),
                                   np.zeros(2, int), np.full(2, 1 / 50), outlook_shift=s)
        p_wet = float(m.p_wet * m.p_cluster_wet[0, 1] + (1 - m.p_wet) * m.p_cluster_wet[0, 0])
        inst = f"A3_kittila_ivalo_both_{key}"
        c0 = next(c for c in k0["circuits"] if c["instance"] == inst and c["role"] == "target" and c["k"] == 0)
        counts = {"00": 0, "01": 0, "10": 0, "11": 0}
        for b, v in c0["counts"].items():
            counts[b.replace(" ", "")[-2:]] += v
        gates = {c["k"]: c["two_qubit_gates"] for c in best_run["circuits"]
                 if c["instance"] == inst and c["role"] == "target"}
        cases[key] = {
            "p_wet": p_wet, "p_flood_dry": float(m.p_area[0][0]), "p_flood_wet": float(m.p_area[0][1]),
            "exact": float(m.count_distribution([0, 1])[2]),
            "shots_k0": counts, "shots_k0_total": sum(counts.values()),
            "estimate": best[inst]["noise_aware_mlae"], "raw": best[inst]["raw_mlae"],
            "shots_total": best[inst]["shots"], "copies": best[inst].get("copies", 10),
            "two_qubit_gates_by_k": gates,
        }
    # everything that goes in: all 14 rivers, snow per cluster, April–May temperature and rain per cluster
    wx = pd.read_csv(DATA / "weather_spring.csv") if (DATA / "weather_spring.csv").exists() else None
    clusters = {}
    for cl in ["Ostrobothnia", "North", "Satakunta–SE"]:
        areas = [a for a in sm.columns if a != "year" and g.loc[a, "cluster"] == cl]
        cats = sorted({str(int(g.loc[a, "swe_catchment"])) for a in areas if not pd.isna(g.loc[a, "swe_catchment"])})
        snow_cl = sw.set_index("year")[[c for c in cats if c in sw.columns]].mean(axis=1)
        entry = {"areas": [{"area": a, "gauge": g.loc[a, "gauge"], "source": g.loc[a, "source"],
                            "q10": float(g.loc[a, "q10_gev"]), "q50": float(g.loc[a, "q50_gev"]),
                            "peaks": {int(y): (None if pd.isna(v) else round(float(v))) for y, v in zip(sm.year, sm[a])}}
                           for a in areas],
                 "snow_mm": {int(y): (None if pd.isna(v) else round(float(v))) for y, v in snow_cl.items()},
                 "snow_catchments": cats}
        if wx is not None:
            w = wx[wx.cluster == cl].set_index("year")
            entry["station"] = w.station.iloc[0]
            entry["temp_c"] = {int(y): (None if pd.isna(v) else float(v)) for y, v in w.t_aprmay.items()}
            entry["rain_mm"] = {int(y): (None if pd.isna(v) else float(v)) for y, v in w.rain_aprmay.items()}
        clusters[cl] = entry
    out = {"example": "Kittilä and Ivalo both pass their 1-in-50 spring level", "all_data": clusters,
           "rivers": rivers, "snow": snow, "independent": (1 / 50) ** 2, "snow_shift_sd": shift,
           "device": "IQM Emerald (54 qubits, IQM Resonance)", "runs": [RUN_K0, RUN_BEST], "cases": cases}
    WEB.mkdir(parents=True, exist_ok=True)
    (WEB / "pipeline.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", WEB / "pipeline.json")
    for k, c in cases.items():
        print(k, f"exact {100*c['exact']:.3f}%  hw {100*c['estimate']:.3f}%  shots {c['shots_k0']}")


if __name__ == "__main__":
    main()
