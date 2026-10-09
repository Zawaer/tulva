"""Bootstrap 90 % intervals for calibrated hardware estimates (resampling the good-count of every circuit
binomially and re-running the same noise-aware MLAE). Also the snow ratio on IQM Emerald."""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from tulva import quantum as q  # noqa: E402

rng = np.random.default_rng(5)

def split(counts, copies, nb):
    out = [defaultdict(int) for _ in range(copies)]
    for b, v in counts.items():
        b = b.replace(" ", "")
        for j in range(copies):
            lo = len(b) - (j + 1) * nb
            out[j][b[lo:lo + nb]] += v
    return out

def groups_of(run, inst):
    g = defaultdict(lambda: defaultdict(lambda: [0, 0])); info = {}
    for c in run["circuits"]:
        if c["instance"] != inst or "counts" not in c:
            continue
        parts = split(c["counts"], c.get("copies", 1), c["n_areas"]) if c.get("copies", 1) > 1 else [c["counts"]]
        for p in parts:
            good, tot = q.good_fraction(p, c["event"])
            g[c["role"]][c["k"]][0] += good; g[c["role"]][c["k"]][1] += tot
        info[c["role"]] = c
    return g, info

def estimate(g, info):
    ks = sorted(g["target"])
    th1 = np.arcsin(np.sqrt(info["twin"]["exact"])); th0 = np.arcsin(np.sqrt(info["zero"]["exact"]))
    gain, off = [], []
    for k in ks:
        y1, y0 = np.sin((2*k+1)*th1)**2, np.sin((2*k+1)*th0)**2
        o1 = g["twin"][k][0]/g["twin"][k][1]; o0 = g["zero"][k][0]/g["zero"][k][1]
        gg = float(np.clip((o1-o0)/(y1-y0), 0.05, 1.2)) if abs(y1-y0) > 0.05 else 1.0
        gain.append(gg); off.append(max(0.0, o0 - gg*y0))
    return q.mlae([g["target"][k][0] for k in ks], [g["target"][k][1] for k in ks], ks, gain=gain, offset=off)

def boot(g, info, n=300):
    out = []
    for _ in range(n):
        gb = {r: {k: [rng.binomial(v[1], v[0]/v[1]), v[1]] for k, v in d.items()} for r, d in g.items()}
        out.append(estimate(gb, info))
    return np.percentile(out, [5, 95]), np.array(out)

res = {}
def do(fname, inst, label):
    run = json.loads((ROOT/"out"/"runs"/fname).read_text())
    g, info = groups_of(run, inst)
    est = estimate(g, info); (lo, hi), samples = boot(g, info)
    res[label] = {"run": fname, "instance": inst, "exact": info["target"]["exact"], "estimate": est, "ci90": [lo, hi]}
    print(f"{label:34s} exact {100*info['target']['exact']:.3f}%  est {100*est:.3f}%  90% CI {100*lo:.3f}–{100*hi:.3f}%  rel {100*(est/info['target']['exact']-1):+.0f}%")
    return samples

import glob
runs = {Path(f).name: f for f in glob.glob(str(ROOT/"out"/"runs"/"*.json")) if not f.endswith(".analysis.json")}
for f in sorted(runs):
    if f.startswith("ibm-ibm_marrakesh") or f.startswith("iqm-garnet"):
        run = json.loads(Path(runs[f]).read_text())
        for inst in sorted({c["instance"] for c in run["circuits"]}):
            do(f, inst, f"{f[:28]}|{inst[:14]}")
snow = sorted(f for f in runs if f.startswith("product-iqm-emerald"))
if snow:
    f = snow[-1]
    lo = do(f, "A3_kittila_ivalo_both_low", "emerald snow low"); hi = do(f, "A3_kittila_ivalo_both_high", "emerald snow high")
    ratio = hi/lo; r5, r95 = np.percentile(ratio, [5, 95])
    res["snow_ratio_high_over_low"] = {"estimate": float(res["emerald snow high"]["estimate"]/res["emerald snow low"]["estimate"]), "ci90": [float(r5), float(r95)],
                                       "exact": res["emerald snow high"]["exact"]/res["emerald snow low"]["exact"]}
    print("snow ratio high/low:", res["snow_ratio_high_over_low"])
    do(f, "A3_kittila_ivalo_both_clim", "emerald snow normal")  # last, so the intervals above keep their RNG stream
(ROOT/"out"/"bootstrap_ci.json").write_text(json.dumps(res, indent=2, default=float))
