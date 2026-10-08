"""Fetch daily discharge and catchment snow water equivalent from open Finnish/Swedish APIs.

Sources (no API key needed):
- SYKE Hydrologiarajapinta 1.1 (OData v3), CC BY 4.0: daily discharge (`Virtaama`) and
  areal snow water equivalent (`LumiAlue`).
- SMHI hydroobs: daily discharge CSV for Swedish stations (Torne at Kukkolankoski).

Raw responses are cached under data/raw/ (git-ignored) so re-runs are offline.
"""
from __future__ import annotations

import io
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"

SYKE = "https://rajapinnat.ymparisto.fi/api/Hydrologiarajapinta/1.1/odata"
SMHI = "https://opendata-download-hydroobs.smhi.se/api/version/latest/parameter/1/station/{sid}/period/corrected-archive/data.csv"
PAUSE_S = 0.15  # polite delay between pages


@dataclass
class Gauge:
    area: str          # flood-risk area (MMM 2024)
    cluster: str       # hydrological cluster used by the joint model
    name: str          # river, gauge
    syke_ids: list[int] = field(default_factory=list)  # Paikka_Ids, newest first; spliced
    smhi_id: int | None = None
    swe_id: int | None = None   # LumiAlue Paikka_Id of the catchment used as snow predictor


# One long-record gauge per river flood-risk area. Clusters follow the product's three regions.
GAUGES: list[Gauge] = [
    Gauge("Lapväärtti", "Ostrobothnia", "Lapväärtinjoki, Perus", [1197, 1198], swe_id=131),
    Gauge("Ilmajoki–Seinäjoki", "Ostrobothnia", "Kyrönjoki, Hanhikoski", [1213], swe_id=131),
    Gauge("Laihia", "Ostrobothnia", "Laihianjoki, Karkkimala", [1204], swe_id=131),
    Gauge("Ylistaro–Koivulahti", "Ostrobothnia", "Kyrönjoki, Skatila", [1214], swe_id=131),
    Gauge("Alavieska–Ylivieska", "Ostrobothnia", "Kalajoki, Niskakoski/Hihnalankoski", [1253, 1254], swe_id=147),
    Gauge("Lower Pyhäjoki", "Ostrobothnia", "Pyhäjoki, Tolpankoski/Pyhänkoski", [1262, 1261], swe_id=147),
    Gauge("Pudasjärvi", "North", "Iijoki, Kurenalus", [1332, 1334, 1333], swe_id=188),
    Gauge("Ivalo", "North", "Ivalojoki, Pajakoski", [1419], swe_id=236),
    Gauge("Kittilä", "North", "Ounasjoki, Köngäs", [1374], swe_id=216),
    Gauge("Rovaniemi", "North", "Ounasjoki, Marraskoski", [1377, 1378], swe_id=216),
    Gauge("Tornio", "North", "Tornionjoki, Kukkolankoski (SMHI 16722)", [1406], smhi_id=16722, swe_id=230),
    Gauge("Pori", "Satakunta–SE", "Kokemäenjoki, Harjavalta", [1188], swe_id=112),
    Gauge("Huittinen", "Satakunta–SE", "Loimijoki, Maurialankoski", [1185, 1184], swe_id=109),
    Gauge("Lower Kymijoki", "Satakunta–SE", "Kymijoki, Anjala", [1058], swe_id=55),
]

_session = requests.Session()
_session.headers.update({"Accept": "application/json", "User-Agent": "tulva-hackathon/0.1 (toivo@stuhi.org)"})


def _get(url: str, params: dict | None = None, tries: int = 4) -> requests.Response:
    for i in range(tries):
        try:
            r = _session.get(url, params=params, timeout=60)
            r.raise_for_status()
            return r
        except requests.RequestException:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))
    raise RuntimeError("unreachable")


def odata_all(entity: str, filt: str, select: str = "Aika,Arvo") -> list[dict]:
    """Page through an OData entity set (500 rows per page), following odata.nextLink."""
    url, params, rows = f"{SYKE}/{entity}", {"$filter": filt, "$select": select}, []
    while url:
        js = _get(url, params).json()
        rows.extend(js.get("value", []))
        url, params = js.get("odata.nextLink"), None
        if url and not url.startswith("http"):
            url = f"{SYKE}/{url}"
        time.sleep(PAUSE_S)
    return rows


def _cached_odata(entity: str, pid: int) -> pd.Series:
    path = RAW / f"{entity}_{pid}.json"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        rows = odata_all(entity, f"Paikka_Id eq {pid}")
        path.write_text(json.dumps(rows))
    rows = json.loads(path.read_text())
    if not rows:
        return pd.Series(dtype=float)
    df = pd.DataFrame(rows)
    s = pd.Series(pd.to_numeric(df["Arvo"], errors="coerce").values,
                  index=pd.to_datetime(df["Aika"]).dt.normalize())
    return s[~s.index.duplicated()].sort_index().dropna()


def syke_discharge(pid: int) -> pd.Series:
    """Daily discharge (m3/s) of one SYKE Paikka_Id."""
    return _cached_odata("Virtaama", pid)


def syke_swe(pid: int) -> pd.Series:
    """Areal snow water equivalent (mm), observed 1st and 16th of each month."""
    return _cached_odata("LumiAlue", pid)


def smhi_discharge(sid: int) -> pd.Series:
    path = RAW / f"smhi_{sid}.csv"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(_get(SMHI.format(sid=sid)).content)
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = [ln for ln in text.splitlines() if ln[:4].isdigit() and ln[4:5] == "-"]
    df = pd.read_csv(io.StringIO("\n".join(lines)), sep=";", header=None, usecols=[0, 1])
    s = pd.Series(pd.to_numeric(df[1], errors="coerce").values, index=pd.to_datetime(df[0]))
    return s[~s.index.duplicated()].sort_index().dropna()


def gauge_series(g: Gauge) -> pd.Series:
    """Daily discharge for a gauge: SMHI if given, else splice SYKE ids (first id wins on overlap)."""
    if g.smhi_id is not None:
        return smhi_discharge(g.smhi_id)
    out = pd.Series(dtype=float)
    for pid in g.syke_ids:
        out = syke_discharge(pid) if out.empty else out.combine_first(syke_discharge(pid))
    return out.sort_index()


def splice_overlap_ratio(g: Gauge) -> list[tuple[int, int, int, float]]:
    """For spliced gauges: (id_a, id_b, overlapping days, median ratio a/b). Sanity check for splicing."""
    res = []
    for a, b in zip(g.syke_ids, g.syke_ids[1:]):
        sa, sb = syke_discharge(a), syke_discharge(b)
        idx = sa.index.intersection(sb.index)
        ratio = float((sa[idx] / sb[idx]).median()) if len(idx) else float("nan")
        res.append((a, b, len(idx), ratio))
    return res
