"""Round-5 review numbers (deck freeze): every figure is read from saved results, no new model runs.

1. Snow ratio baselines on IQM Emerald: snowy vs LOW snow (slide 5, video) and snowy vs NORMAL (to contrast with
   slide 3's "triples" = snowy March vs the autumn/normal price). Chip = calibrated noise-aware MLAE.
2. Basis risk: back-test trigger years (≥2 of cluster over GEV 1-in-10, and the 1-in-50 subset) that are NOT a known
   loss spring for that cluster (business case §1 loss table, as in round4_numbers.py).
3. Amplification: signal kept (gain) at k = 1 / 2 per run, shown runs vs earlier runs.
4. Appendix traceability: job IDs and the unshown first runs (IBM run 1, Garnet run 1).

    .venv/bin/python scripts/round5_numbers.py   # → out/round5_numbers.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
RUNS = OUT / "runs"
CLUSTERS = ["Ostrobothnia", "North", "Satakunta–SE"]
# Same table as scripts/round4_numbers.py basis_risk(): year -> cluster the known loss maps to
KNOWN_LOSS = {1966: "Satakunta–SE", 2005: "North", 2012: "Ostrobothnia", 2013: "Ostrobothnia", 2018: "North",
              2020: "North", 2024: "Ostrobothnia"}
SHOWN = {"ibm-ibm_marrakesh-20261008T174523Z": "IBM Marrakesh run 2", "iqm-garnet-20261008T182534Z": "IQM Garnet run 2",
         "product-iqm-emerald-20261009T075338Z": "IQM Emerald (snow run)", "q50-20261009T145044Z": "VTT Q50 repeat 1",
         "q50-20261009T145110Z": "VTT Q50 repeat 2", "q50-20261009T145135Z": "VTT Q50 repeat 3"}
EARLIER = {"ibm-ibm_marrakesh-20261008T170341Z": "IBM Marrakesh run 1", "iqm-garnet-20261008T182125Z": "IQM Garnet run 1",
           "product-iqm-emerald-20261009T073815Z": "IQM Emerald first snow run"}


def snow_ratios():
    b = json.loads((OUT / "bootstrap_ci.json").read_text())
    lo, no, hi = b["emerald snow low"], b["emerald snow normal"], b["emerald snow high"]
    return {"snowy_vs_low": {"chip": round(hi["estimate"] / lo["estimate"], 3), "exact": round(hi["exact"] / lo["exact"], 3),
                             "chip_ci90": [round(v, 2) for v in b["snow_ratio_high_over_low"]["ci90"]]},
            "snowy_vs_normal": {"chip": round(hi["estimate"] / no["estimate"], 3),
                                "exact": round(hi["exact"] / no["exact"], 3)},
            "note": "two-river North-cluster pair, both over 1-in-50, calibrated (noise-aware MLAE), run "
                    "product-iqm-emerald-20261009T075338Z. Slide 3's 'triples' (3.3x) is a different measure: North "
                    ">=2 of 5 cover, snowy (top-15 %) March vs the autumn price, continuous classical model."}


def basis_risk():
    bt = json.loads((OUT / "backtest.json").read_text())["clusters"]
    res = {}
    for level, key in (("1in10", "trigger_years"), ("1in50", "years_ge2_over_fitted_1in50")):
        paid_loss, missed, no_loss = [], [], []
        for y, c in sorted(KNOWN_LOSS.items()):
            (paid_loss if y in bt[c][key] else missed).append(f"{y} {c}")
        for c in CLUSTERS:
            for y in bt[c][key]:
                if KNOWN_LOSS.get(y) != c:
                    no_loss.append((y, c))
        no_loss.sort()
        res[level] = {"paid_in_known_loss_springs": paid_loss, "missed_known_loss_springs": missed,
                      "paid_no_recorded_loss": [f"{y} {c}" for y, c in no_loss],
                      "paid_no_recorded_loss_n_springs": len({y for y, _ in no_loss}),
                      "paid_no_recorded_loss_since_2005": [f"{y} {c}" for y, c in no_loss if y >= 2005]}
    res["note"] = ("Known loss springs = business case §1 loss table (outside source; records before 2005 are sparse and "
                   "Finance Finland stopped tracking flood claims after 2015), so 'no recorded loss' is not 'no loss'.")
    return res


def gains():
    def g(stem):
        a = json.loads((RUNS / f"{stem}.analysis.json").read_text())
        return {inst: {k: round(v, 2) for k, v in d["gain_by_k"].items() if k in ("1", "2")}
                for inst, d in a.items() if inst.startswith("A3")}
    return {"shown": {lab: g(s) for s, lab in SHOWN.items()}, "earlier": {lab: g(s) for s, lab in EARLIER.items()}}


def traceability():
    jobs = {}
    for stem in ["product-iqm-emerald-20261009T075338Z", "loader-control-indep-iqm-emerald-20261009T135910Z",
                 "ibm-ibm_marrakesh-20261008T170341Z", "iqm-garnet-20261008T182125Z"]:
        jobs[stem] = json.loads((RUNS / f"{stem}.json").read_text())["jobs"]
    first = {}
    for stem, lab in (("ibm-ibm_marrakesh-20261008T170341Z", "IBM run 1"), ("iqm-garnet-20261008T182125Z", "Garnet run 1")):
        a = json.loads((RUNS / f"{stem}.analysis.json").read_text())["A3_kittila_ivalo_both"]
        first[lab] = {"calibrated_pct": round(100 * a["noise_aware_mlae"], 3), "exact_pct": round(100 * a["exact"], 3),
                      "copies": a["copies"], "ks": sorted(int(k) for k in a["gain_by_k"])}
    return {"jobs": jobs, "first_runs_not_shown": first}


def main():
    res = {"snow_ratio_baselines": snow_ratios(), "basis_risk": basis_risk(), "amplification_gain": gains(),
           "appendix": traceability()}
    (OUT / "round5_numbers.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
