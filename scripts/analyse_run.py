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
per_copy = defaultdict(lambda: defaultdict(lambda: [0, 0]))  # (instance, k, copy) for target circuits
per_copy_role = defaultdict(lambda: [0, 0])                  # (instance, role, k, copy) -> [good, shots]


def split_counts(counts: dict, copies: int, nb: int) -> list[dict]:
    """Split counts of a widened circuit into one count dict per copy (qiskit strings: highest clbit first)."""
    out = [defaultdict(int) for _ in range(copies)]
    for b, v in counts.items():
        b = b.replace(" ", "")
        for j in range(copies):
            lo = len(b) - (j + 1) * nb
            out[j][b[lo:lo + nb]] += v
    return out
info = {}
for c in run["circuits"]:
    if "counts" not in c:
        continue
    copies = c.get("copies", 1)
    parts = split_counts(c["counts"], copies, c["n_areas"]) if copies > 1 else [c["counts"]]
    g = groups[(c["instance"], c["role"])][c["k"]]
    for j, part in enumerate(parts):
        good, tot = q.good_fraction(part, c["event"])
        g[0] += good
        g[1] += tot
        pr = per_copy_role[(c["instance"], c["role"], c["k"], j)]
        pr[0] += good
        pr[1] += tot
        if c["role"] == "target":
            pc = per_copy[(c["instance"], c["k"])][j]
            pc[0] += good
            pc[1] += tot
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
    # per-copy calibration: each copy's twin/zero ran on the same physical qubits (--best-qubits)
    copies = c0.get("copies", 1)
    aware_per_copy = None
    if copies > 1 and run.get("layout_triples"):
        ll_theta = np.zeros_like(q._THETA)
        for j in range(copies):
            for k in ks:
                t = per_copy_role[(inst, "target", k, j)]
                o1 = per_copy_role[(inst, "twin", k, j)]
                o0 = per_copy_role[(inst, "zero", k, j)]
                y1, y0 = np.sin((2 * k + 1) * th1) ** 2, np.sin((2 * k + 1) * th0) ** 2
                r1, r0 = o1[0] / o1[1], o0[0] / o0[1]
                g = float(np.clip((r1 - r0) / (y1 - y0), 0.05, 1.2)) if abs(y1 - y0) > 0.05 else 1.0
                off = max(0.0, r0 - g * y0)
                p = np.clip(g * np.sin((2 * k + 1) * q._THETA) ** 2 + off, 1e-12, 1 - 1e-12)
                ll_theta += t[0] * np.log(p) + (t[1] - t[0]) * np.log(1 - p)
        aware_per_copy = float(np.sin(q._THETA[np.argmax(ll_theta)]) ** 2)
    k0 = tgt[0][0] / tgt[0][1] if 0 in tgt else float("nan")
    nq = q.oracle_queries(shots, ks)
    summary[inst] = {
        "exact": exact, "raw_mlae": raw, "noise_aware_mlae": aware, "k0_only": k0,
        "noise_aware_per_copy_mlae": aware_per_copy,
        "gain_by_k": dict(zip(ks, gain)), "offset_by_k": dict(zip(ks, offset)),
        "two_qubit_gates_by_k": {k: info[(inst, "target", k)]["two_qubit_gates"] // c0.get("copies", 1) for k in ks},
        "oracle_queries": nq, "mc_rmse_same_queries": float(np.sqrt(exact * (1 - exact) / nq)),
        "copies": c0.get("copies", 1),
        "per_copy_k0_rate": [v[0] / v[1] for _, v in sorted(per_copy[(inst, 0)].items())] if (inst, 0) in per_copy else [],
        "shots": int(sum(shots)), "mc_rmse_same_shots": float(np.sqrt(exact * (1 - exact) / sum(shots))),
    }
out = Path(sys.argv[1]).with_suffix(".analysis.json")
out.write_text(json.dumps(summary, indent=2))
for inst, s in summary.items():
    print(f"{inst}: exact {100*s['exact']:.3f}% | raw {100*s['raw_mlae']:.3f}% | noise-aware {100*s['noise_aware_mlae']:.3f}%"
          + (f" | per-copy calibrated {100*s['noise_aware_per_copy_mlae']:.3f}%" if s['noise_aware_per_copy_mlae'] else "")
          + f" | k=0 {100*s['k0_only']:.3f}% | MC rmse (same queries) {100*s['mc_rmse_same_queries']:.3f}pp"
          f" | copies {s['copies']} | gain {[round(v, 2) for v in s['gain_by_k'].values()]} offset {[round(v, 4) for v in s['offset_by_k'].values()]} | 2q {list(s['two_qubit_gates_by_k'].values())}")
