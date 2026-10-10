"""Numbers and map geometry for the demo video: web/data + out/ -> src/data.json.

    python3 deck/video/anim/export_data.py

Everything the animated scenes draw comes from here (the app recording shows the app itself). The asserts check
that the numbers spoken in narration.md still match the data they come from (see CLAIMS.md).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
APP = json.loads((ROOT / "web/data/app.json").read_text(encoding="utf-8"))
PIPE = json.loads((ROOT / "web/data/pipeline.json").read_text(encoding="utf-8"))
BASE = json.loads((ROOT / "web/data/basemap.json").read_text(encoding="utf-8"))
CI = json.loads((ROOT / "out/bootstrap_ci.json").read_text(encoding="utf-8"))

YEAR = "2005"
# Sinusoidal projection centred on 26°E, in 1920x1080 frame pixels (map sits right of centre, above the captions).
LON0, LAT_TOP, K, X0, Y0 = 26.0, 70.3, 80.0, 1390.0, 66.0


def proj(lon: float, lat: float) -> tuple[float, float]:
    return X0 + (lon - LON0) * math.cos(math.radians(lat)) * K, Y0 + (LAT_TOP - lat) * K


def path(geom: dict) -> str:
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    out = []
    for poly in polys:
        for ring in poly:
            pts = [proj(lon, lat) for lon, lat in ring]
            if all(x < 700 or x > 2300 or y < -300 or y > 1300 for x, y in pts):
                continue  # far off screen
            out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z")
    return "".join(out)


def main() -> None:
    peaks = APP["replay"]["peaks"][YEAR]
    areas = []
    for a in APP["areas"]:
        v = peaks.get(a["area"])
        x, y = proj(a["lon"], a["lat"])
        r10 = None if v is None else v / a["q10_empirical"]
        areas.append({"area": a["area"], "cluster": a["cluster"], "x": round(x, 1), "y": round(y, 1),
                      "pct_of_1in10": None if r10 is None else round(100 * r10),
                      "over_1in10": bool(r10 and r10 >= 1), "over_1in50": bool(v and v >= a["q50"])})
    over = [a["area"] for a in areas if a["over_1in10"]]
    assert over == ["Ivalo", "Kittilä", "Rovaniemi", "Tornio"], over          # "four Lapland rivers"
    snow = APP["replay"]["swe_north_pct"][YEAR]
    assert snow["top15"] and snow["pct"] == 87, snow                            # "top fifteen percent"

    north = APP["clusters"]["North"]
    p_no, p_high = north["p_tulva"]["v"], north["p_high_outlook"]["v"]
    assert f"{100 * p_no:.1f}" == "2.0" and f"{100 * p_high:.1f}" == "6.4"      # "from two to six point four"

    r = CI["snow_ratio_high_over_low"]
    assert f"{r['estimate']:.2f}" == "3.05" and f"{r['exact']:.2f}" == "2.75"  # "about three times ... 2.75 exact"
    cases = {k: {"shots": PIPE["cases"][k]["shots_k0"], "total": PIPE["cases"][k]["shots_k0_total"],
                 "shots_all": PIPE["cases"][k]["shots_total"], "estimate": PIPE["cases"][k]["estimate"],
                 "exact": PIPE["cases"][k]["exact"], "ci90": CI[f"emerald snow {k}"]["ci90"]} for k in ("low", "high")}
    for k in ("low", "high"):  # the bars = slide 6's bars (out/bootstrap_ci.json)
        assert abs(cases[k]["estimate"] - CI[f"emerald snow {k}"]["estimate"]) < 1e-12, k
        assert abs(cases[k]["exact"] - CI[f"emerald snow {k}"]["exact"]) < 1e-12, k
    assert (cases["low"]["shots"]["11"], cases["high"]["shots"]["11"]) == (13, 31)

    edges = [e for e in APP["edges"] if e["a"] in over and e["b"] in over]  # the app's map lines (Spearman ≥ 0.6)
    land = [{"name": f["properties"]["name"], "home": f["properties"]["home"], "d": path(f["geometry"])}
            for f in BASE["features"]]
    data = {
        "year": int(YEAR), "areas": areas, "edges": edges, "land": [l for l in land if l["d"]],
        "snow_north_pct": snow["pct"],
        "outlook_north": {"no_outlook": p_no, "high_snow": p_high},
        "shots": {"device": PIPE["device"], "runs": PIPE["runs"], "cases": cases},
        "ratio": {"chip": r["estimate"], "chip_ci90": r["ci90"], "exact": r["exact"]},
        "computers": [  # CLAIMS.md "VTT Q50" section: the four computers the two-river core ran on
            {"maker": "IBM", "name": "Marrakesh"}, {"maker": "IQM", "name": "Garnet"},
            {"maker": "IQM", "name": "Emerald"}, {"maker": "VTT", "name": "Q50", "note": "Finland"}],
        "sources": "web/data/app.json, web/data/pipeline.json, web/data/basemap.json (Natural Earth), "
                   "out/bootstrap_ci.json",
    }
    (HERE / "src" / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"src/data.json: {len(areas)} areas ({', '.join(over)} over 1-in-10 in {YEAR}), North snow {snow['pct']}th pct, "
          f"North {100 * p_no:.1f} % -> {100 * p_high:.1f} %, ratio chip {r['estimate']:.2f} vs exact {r['exact']:.2f}")


if __name__ == "__main__":
    main()
