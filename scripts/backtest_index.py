"""Back-test the Tulva Index trigger on the observed record and check the March-snow early warning.

1-in-50 is too rare to back-test on 65 springs, so the trigger here is ">= 2 of the cluster's gauges over their
fitted (GEV) 1-in-10 spring level". For every cluster: the years it would have paid, observed frequency vs the
model and independence, and whether the 1 March snow outlook (top 15 % of the cluster SWE index) flagged them.
In-sample: the snow skill and the model were fitted on these same years.

Inputs:  data/spring_max.csv, data/swe_mar1.csv, data/gauges.csv, out/model_params.json, out/snow_skill.json
Output:  out/backtest.json
Run: .venv/bin/python scripts/backtest_index.py
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
M, TOP = 2, 0.15


def wilson(k, n, z=1.645):
    """90 % Wilson interval for k of n."""
    if n == 0:
        return [None, None]
    ph = k / n
    d = 1 + z ** 2 / n
    c = (ph + z ** 2 / (2 * n)) / d
    w = z * np.sqrt(ph * (1 - ph) / n + z ** 2 / (4 * n ** 2)) / d
    return [round(float(max(0, c - w)), 3), round(float(min(1, c + w)), 3)]


def main():
    sm = pd.read_csv(ROOT / "data" / "spring_max.csv", index_col="year")
    swe = pd.read_csv(ROOT / "data" / "swe_mar1.csv", index_col="year")
    mp = json.loads((OUT / "model_params.json").read_text())
    sk = json.loads((OUT / "snow_skill.json").read_text())["clusters"]
    q10 = {g["area"]: g["q10_m3s"] for g in mp["gauges"]}
    q50 = {g["area"]: g["q50_m3s"] for g in mp["gauges"]}
    swe_ns = model.normal_scores(swe)

    res = {"description": "Trigger = >= 2 of the cluster's gauges over their fitted GEV 1-in-10 spring level "
                          "(q10_m3s in out/model_params.json). Outlook flag = 1 March SWE index (mean normal score "
                          "of the cluster's SYKE catchments) in its top 15 %. In-sample, 1961-2025.",
           "trigger_m": M, "outlook_top_fraction": TOP, "clusters": {}}
    for c in mp["cluster_names"]:
        areas = mp["clusters"][c]["areas"]
        n = len(areas)
        over = sm[areas].gt(pd.Series(q10)[areas]).where(sm[areas].notna())
        cnt = over.sum(axis=1, min_count=1)
        nobs = sm[areas].notna().sum(axis=1)
        trig = cnt >= M
        over50 = sm[areas].gt(pd.Series(q50)[areas]).where(sm[areas].notna())

        sidx = swe_ns[[str(x) for x in sk[c]["swe_catchments"]]].mean(axis=1, skipna=True).dropna()
        flag = sidx >= sidx.quantile(1 - TOP)
        years = sidx.index.intersection(cnt.dropna().index)
        T, F = trig[years], flag[years]
        hits = sorted(int(y) for y in years[T & F])
        misses = sorted(int(y) for y in years[T & ~F])
        false_al = sorted(int(y) for y in years[F & ~T])
        low = sidx[years] <= sidx[years].quantile(TOP)

        a, b = mp["national_loading"], mp["cluster_loading"][c]
        h = float(np.hypot(a, b))
        s = sk[c]["outlook_skill_vs_latent_factor"]
        p_model = P.p_trigger_exact(n, M, 0.1, h)
        p_ind = P.p_trigger_independent(n, M, 0.1)
        p_hi = P.p_trigger_exact(n, M, 0.1, h, s, "high")
        p_lo = P.p_trigger_exact(n, M, 0.1, h, s, "low")
        nt, nf = int(T.sum()), int(F.sum())
        res["clusters"][c] = {
            "n_gauges": n, "years": len(years),
            "gauge_years_missing": int((n - nobs[years]).sum()),
            "trigger_years": sorted(int(y) for y in years[T]),
            "trigger_detail": {int(y): {"n_over_1in10": int(cnt[y]), "n_observed": int(nobs[y]),
                                        "areas": [a_ for a_ in areas if over.loc[y, a_] == 1],
                                        "swe_index": round(float(sidx[y]), 2), "outlook_flag": bool(flag[y])}
                               for y in years[T]},
            "observed_freq": round(nt / len(years), 3), "observed_freq_ci90": wilson(nt, len(years)),
            "model_p": round(p_model, 3), "independent_p": round(p_ind, 4),
            "outlook_flag_years": sorted(int(y) for y in years[F]),
            "hits": hits, "misses": misses, "false_alarms": false_al,
            "hit_rate": round(len(hits) / nt, 2) if nt else None, "hit_rate_ci90": wilson(len(hits), nt),
            "false_alarm_ratio": round(len(false_al) / nf, 2) if nf else None,
            "p_trigger_given_flag_observed": round(len(hits) / nf, 2) if nf else None,
            "p_trigger_given_flag_ci90": wilson(len(hits), nf),
            "p_trigger_given_flag_model": round(p_hi, 3),
            "p_trigger_no_flag_observed": round(len(misses) / (len(years) - nf), 3),
            "p_trigger_given_low_snow_observed": round(float(T[low].mean()), 3),
            "p_trigger_given_low_snow_model": round(p_lo, 3),
            "triggers_in_low_snow_years": sorted(int(y) for y in years[T & low]),
            "years_ge2_over_fitted_1in50": sorted(int(y) for y in over50.index[(over50.sum(axis=1) >= 2)]),
            "ge2_over_1in50_observed": int((over50.loc[years].sum(axis=1) >= 2).sum()),
            "ge2_over_1in50_expected_model": round(len(years) * P.p_trigger_exact(n, M, 0.02, h), 2),
            "ge2_over_1in50_expected_independent": round(len(years) * P.p_trigger_independent(n, M, 0.02), 2),
            "fisher_exact_p_one_sided": round(float(stats.fisher_exact(
                [[len(hits), len(false_al)], [len(misses), len(years) - nf - len(misses)]],
                alternative="greater")[1]), 4),
        }
        d = res["clusters"][c]
        print(f"{c}: paid {d['trigger_years']} ({nt}/{len(years)}={d['observed_freq']}, model {d['model_p']}, "
              f"indep {d['independent_p']}); flagged {nf}: hits {hits} misses {misses} false {false_al}; "
              f"P(trig|flag) {d['p_trigger_given_flag_observed']} vs model {d['p_trigger_given_flag_model']}; "
              f"low-snow {d['p_trigger_given_low_snow_observed']} ({d['triggers_in_low_snow_years']}); "
              f"Fisher p {d['fisher_exact_p_one_sided']}; >=2 over 1-in-50: {d['years_ge2_over_fitted_1in50']}")

    allT = sum(len(v["trigger_years"]) for v in res["clusters"].values())
    allH = sum(len(v["hits"]) for v in res["clusters"].values())
    allF = sum(len(v["outlook_flag_years"]) for v in res["clusters"].values())
    res["pooled"] = {"cluster_trigger_years": allT, "flagged_in_advance": allH,
                     "hit_rate": round(allH / allT, 2), "hit_rate_ci90": wilson(allH, allT),
                     "flags": allF, "flag_precision": round(allH / allF, 2), "flag_precision_ci90": wilson(allH, allF),
                     "base_rate": round(allT / sum(v["years"] for v in res["clusters"].values()), 3)}
    for k in ("ge2_over_1in50_observed", "ge2_over_1in50_expected_model", "ge2_over_1in50_expected_independent"):
        res["pooled"][k] = round(sum(v[k] for v in res["clusters"].values()), 2)
    print("pooled", res["pooled"])
    (OUT / "backtest.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
