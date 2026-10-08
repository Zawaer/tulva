"""Download (cached) SYKE/SMHI daily discharge, build spring (Mar–Jun) maxima 1961–2025 per gauge.

Writes data/spring_max.csv (year x area, m3/s), data/gauges.csv (metadata, 1-in-10 / 1-in-50 levels),
data/swe_mar1.csv (catchment SWE on 1 March, mm).
Run: .venv/bin/python scripts/build_dataset.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tulva import model, syke  # noqa: E402

YEARS = range(1961, 2026)


def main():
    maxima, meta = {}, []
    for g in syke.GAUGES:
        q = syke.gauge_series(g)
        sm = model.seasonal_max(q, years=YEARS)
        am = model.seasonal_max(q, months=tuple(range(1, 13)), min_days=330, years=YEARS)
        maxima[g.area] = sm
        x = sm.dropna().values
        gev, gum = model.gev_lmom(x), model.gumbel_lmom(x)
        splice = "" if g.smhi_id else "; ".join(f"{a}/{b}: {n} d overlap, ratio {r:.2f}"
                                               for a, b, n, r in syke.splice_overlap_ratio(g))
        both = pd.concat([sm, am], axis=1).dropna()
        meta.append({
            "area": g.area, "cluster": g.cluster, "gauge": g.name,
            "source": f"SMHI {g.smhi_id}" if g.smhi_id else "SYKE " + "+".join(map(str, g.syke_ids)),
            "swe_catchment": g.swe_id,
            "record_start": q.index.min().year, "record_end": q.index.max().year,
            "years": int(sm.notna().sum()), "first_year": int(sm.first_valid_index()),
            "missing_years": " ".join(str(y) for y in sm.index[sm.isna()] if y >= sm.first_valid_index()),
            "spring_peak_share": round(float((both.iloc[:, 0] >= both.iloc[:, 1] * 0.999).mean()), 2),
            "q10_empirical": round(float(np.nanquantile(x, 0.9)), 1),
            "q10_gev": round(float(model.return_level(gev, 10)), 1),
            "q50_gev": round(float(model.return_level(gev, 50)), 1),
            "q50_gumbel": round(float(model.return_level(gum, 50)), 1),
            "gev_k": round(gev["k"], 3), "record_max": round(float(x.max()), 1),
            "record_max_year": int(sm.idxmax()), "splice_check": splice,
        })
        print(f"{g.area:22s} {meta[-1]['years']:3d} yrs  q10={meta[-1]['q10_gev']:7.1f}  "
              f"q50={meta[-1]['q50_gev']:7.1f}  max={meta[-1]['record_max']:7.1f} ({meta[-1]['record_max_year']})  {splice}")

    df = pd.DataFrame(maxima)
    df.index.name = "year"
    df.round(2).to_csv(ROOT / "data" / "spring_max.csv")
    pd.DataFrame(meta).to_csv(ROOT / "data" / "gauges.csv", index=False)

    swe = {}
    for pid in sorted({g.swe_id for g in syke.GAUGES}):
        s = syke.syke_swe(pid)
        row = {}
        for y in YEARS:
            w = s[(s.index >= f"{y}-02-26") & (s.index <= f"{y}-03-04")]
            row[y] = float(w.iloc[(abs((w.index - pd.Timestamp(f"{y}-03-01")).days)).argmin()]) if len(w) else np.nan
        swe[pid] = pd.Series(row)
    swe = pd.DataFrame(swe)
    swe.index.name = "year"
    swe.to_csv(ROOT / "data" / "swe_mar1.csv")
    print("SWE 1 March, years available per catchment:", swe.notna().sum().to_dict())


if __name__ == "__main__":
    main()
