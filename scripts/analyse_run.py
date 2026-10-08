"""Analyse a saved run: raw MLAE, noise-aware MLAE (decay from the twin), k=0 only, vs exact and Monte Carlo.

    python scripts/analyse_run.py out/runs/<file>.json
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tulva import quantum as q  # noqa: E402

run = json.loads(Path(sys.argv[1]).read_text())
groups = defaultdict(lambda: defaultdict(lambda: [0, 0]))   # (instance, role) -> k -> [good, shots]
info = {}
for c in run["circuits"]:
    if "counts" not in c:
        continue
    good, tot = q.good_fraction(c["counts"], c["event"])
    g = groups[(c["instance"], c["role"])][c["k"]]
    g[0] += good
    g[1] += tot
    info[(c["instance"], c["role"])] = c
    info[(c["instance"], c["role"], c["k"])] = c


summary = {}
for (inst, role) in sorted({k for k in groups if k[1] == "target"}):
    tgt, twin = groups[(inst, "target")], groups[(inst, "twin")]
    ks = sorted(tgt)
    c0 = info[(inst, "target")]
    exact = c0["exact"]
    hits, shots = [tgt[k][0] for k in ks], [tgt[k][1] for k in ks]
    raw = q.mlae(hits, shots, ks)
    # affine noise model per k from the two twins: observed = gain_k * ideal + offset_k
    zero = groups[(inst, "zero")]
    th1 = np.arcsin(np.sqrt(info[(inst, "twin")]["exact"]))
    th0 = np.arcsin(np.sqrt(info[(inst, "zero")]["exact"]))
    gain, offset = [], []
    for k in ks:
        y1, y0 = np.sin((2 * k + 1) * th1) ** 2, np.sin((2 * k + 1) * th0) ** 2
        o1, o0 = twin[k][0] / twin[k][1], zero[k][0] / zero[k][1]
        g = (o1 - o0) / (y1 - y0) if abs(y1 - y0) > 0.05 else 1.0
        g = float(np.clip(g, 0.05, 1.2))
        gain.append(g)
        offset.append(float(max(0.0, o0 - g * y0)))
    aware = q.mlae(hits, shots, ks, gain=gain, offset=offset)
    k0 = tgt[0][0] / tgt[0][1] if 0 in tgt else float("nan")
    nq = q.oracle_queries(shots, ks)
    summary[inst] = {
        "exact": exact, "raw_mlae": raw, "noise_aware_mlae": aware, "k0_only": k0,
        "gain_by_k": dict(zip(ks, gain)), "offset_by_k": dict(zip(ks, offset)),
        "two_qubit_gates_by_k": {k: info[(inst, "target", k)]["two_qubit_gates"] for k in ks},
        "oracle_queries": nq, "mc_rmse_same_queries": float(np.sqrt(exact * (1 - exact) / nq)),
        "shots": int(sum(shots)), "mc_rmse_same_shots": float(np.sqrt(exact * (1 - exact) / sum(shots))),
    }
out = Path(sys.argv[1]).with_suffix(".analysis.json")
out.write_text(json.dumps(summary, indent=2))
for inst, s in summary.items():
    print(f"{inst}: exact {100*s['exact']:.3f}% | raw {100*s['raw_mlae']:.3f}% | noise-aware {100*s['noise_aware_mlae']:.3f}%"
          f" | k=0 {100*s['k0_only']:.3f}% | MC rmse (same queries) {100*s['mc_rmse_same_queries']:.3f}pp"
          f" | gain {[round(v, 2) for v in s['gain_by_k'].values()]} offset {[round(v, 4) for v in s['offset_by_k'].values()]} | 2q {list(s['two_qubit_gates_by_k'].values())}")
