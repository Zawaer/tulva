"""Download spring temperature and rain from FMI open data, one long-record station per cluster.

    python scripts/fetch_weather.py

FMI WFS stored query fmi::observations::weather::monthly::simple (no key, CC BY 4.0): monthly mean temperature
(tmon, °C) and precipitation (rrmon, mm). The query allows 10 years per request, so we page by decade. Raw XML is
cached in data/raw/fmi/ (git-ignored). Writes data/weather_spring.csv: year x cluster, April–May mean temperature
and April–May total precipitation (the melt season, after the 1 March snow is known).
"""
from __future__ import annotations

import re
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "fmi"
URL = "https://opendata.fmi.fi/wfs"
STATIONS = {"North": "Sodankylä", "Ostrobothnia": "Kauhava", "Satakunta–SE": "Pori"}
YEARS = range(1961, 2026)
ROW = re.compile(r"<BsWfs:Time>(\d{4})-(\d{2})-01T00:00:00Z</BsWfs:Time>\s*<BsWfs:ParameterName>(\w+)</BsWfs:ParameterName>"
                 r"\s*<BsWfs:ParameterValue>([^<]*)</BsWfs:ParameterValue>")


def fetch(place: str, y0: int, y1: int) -> str:
    cache = RAW / f"{place}_{y0}_{y1}.xml"
    if cache.exists():
        return cache.read_text(encoding="utf-8")
    p = dict(service="WFS", version="2.0.0", request="getFeature",
             storedquery_id="fmi::observations::weather::monthly::simple", place=place,
             starttime=f"{y0}-01-01T00:00:00Z", endtime=f"{y1}-12-01T00:00:00Z")
    r = requests.get(URL, params=p, timeout=120)
    r.raise_for_status()
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(r.text, encoding="utf-8")
    time.sleep(0.3)
    return r.text


def main():
    rows = []
    for cluster, place in STATIONS.items():
        vals = {}
        for y0 in range(YEARS.start, YEARS.stop, 9):
            for y, m, name, v in ROW.findall(fetch(place, y0, min(y0 + 8, YEARS.stop - 1))):
                if v not in ("", "NaN"):
                    vals[(int(y), int(m), name)] = float(v)
        for y in YEARS:
            t = [vals.get((y, m, "tmon")) for m in (4, 5)]
            r = [vals.get((y, m, "rrmon")) for m in (4, 5)]
            rows.append({"year": y, "cluster": cluster, "station": place,
                         "t_aprmay": None if None in t else round(sum(t) / 2, 2),
                         "rain_aprmay": None if None in r else round(sum(r), 1)})
    df = pd.DataFrame(rows)
    out = ROOT / "data" / "weather_spring.csv"
    df.to_csv(out, index=False)
    print("wrote", out)
    print(df.groupby("cluster")[["t_aprmay", "rain_aprmay"]].agg(["count", "mean", "std"]).round(1))


if __name__ == "__main__":
    main()
