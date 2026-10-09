"""One connected 43-qubit circuit: snow + spring temperature + rain -> all 14 areas at two flood levels.

    python scripts/weather_model.py                                   # fit -> out/weather_model.json (first)
    python scripts/run_big_hw.py --backend mps --shots 200000         # classical check (matrix-product-state sim)
    .venv-iqm/bin/python scripts/run_big_hw.py --backend iqm-fake --dry-run     # gate counts on a 54-qubit layout
    IQM_TOKEN=... .venv-iqm/bin/python scripts/run_big_hw.py --backend iqm --iqm-name emerald --shots 20000

Qubits: 0-2 national snow/temp/rain; 3-11 cluster S,T,R (Ostrobothnia, North, Satakunta–SE); 12-14 cluster wet
spring W; 15-28 area over 1-in-10; 29-42 area over 1-in-50. All qubits are measured, so one run samples every
weather scenario at once. Output: out/runs/big-<backend>-<stamp>.json with counts and the derived probabilities.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import UCRYGate

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tulva import quantum as q  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--backend", default="mps", choices=["mps", "iqm", "iqm-fake"])
ap.add_argument("--iqm-name", default="emerald")
ap.add_argument("--shots", type=int, default=20000)
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()

CLUSTERS = ["Ostrobothnia", "North", "Satakunta–SE"]
VARS = ["snow", "temp", "rain"]
M = json.loads((ROOT / "out" / "weather_model.json").read_text(encoding="utf-8"))
NET = M["network"]


def layout():
    nat = {v: i for i, v in enumerate(VARS)}
    cw = {(c, v): 3 + 3 * ci + vi for ci, c in enumerate(CLUSTERS) for vi, v in enumerate(VARS)}
    wet = {c: 12 + ci for ci, c in enumerate(CLUSTERS)}
    areas = [(c, a["area"]) for c in CLUSTERS for a in NET["clusters"][c]["areas"]]
    a10 = {ca: 15 + i for i, ca in enumerate(areas)}
    a50 = {ca: 15 + len(areas) + i for i, ca in enumerate(areas)}
    return nat, cw, wet, a10, a50, areas


NAT, CW, WET, A10, A50, AREAS = layout()
NQ = 15 + 2 * len(AREAS)


def ang(p):
    return q._angle(p)


def circuit() -> QuantumCircuit:
    qc = QuantumCircuit(NQ, NQ)
    for v in VARS:
        qc.ry(ang(NET["national"][v]["p_high"]), NAT[v])
    for c in CLUSTERS:
        C = NET["clusters"][c]
        for v in VARS:
            q._conditional_ry(qc, NAT[v], CW[(c, v)], *C["weather_given_national"][v])
        # W_c from (S, T, R): control state index i = s + 2t + 4r (first control least significant)
        pw = C["p_wet_given_stw"]
        angles = [ang(pw[f"{i & 1}{(i >> 1) & 1}{(i >> 2) & 1}"]) for i in range(8)]
        qc.append(UCRYGate(angles), [WET[c], CW[(c, "snow")], CW[(c, "temp")], CW[(c, "rain")]])
        for a in C["areas"]:
            k = (c, a["area"])
            q._conditional_ry(qc, WET[c], A10[k], *a["p10"])
            # over 1-in-50 only if over 1-in-10: index i = a10 + 2 w
            qc.append(UCRYGate([0.0, ang(a["p50_given_10"][0]), 0.0, ang(a["p50_given_10"][1])]),
                      [A50[k], A10[k], WET[c]])
    qc.measure(range(NQ), range(NQ))
    return qc


def get_backend():
    if args.backend == "mps":
        from qiskit_aer import AerSimulator
        return AerSimulator(method="matrix_product_state")
    if args.backend == "iqm-fake":
        from iqm.qiskit_iqm import IQMFakeAphrodite
        return IQMFakeAphrodite()
    from iqm.qiskit_iqm import IQMProvider
    if "IQM_TOKEN" not in os.environ:
        env = ROOT / ".env"
        for line in env.read_text().splitlines() if env.exists() else []:
            if line.startswith("IQM_TOKEN=") and line.split("=", 1)[1].strip():
                os.environ["IQM_TOKEN"] = line.split("=", 1)[1].strip()
    return IQMProvider(os.getenv("IQM_SERVER_URL", "https://resonance.iqm.tech"),
                       quantum_computer=args.iqm_name).get_backend()


def derive(counts: dict) -> dict:
    """Event frequencies from the shots (bit i of a qiskit string is s[-1-i])."""
    tot = sum(counts.values())
    north50 = [A50[k] for k in AREAS if k[0] == "North"]
    all10 = [A10[k] for k in AREAS]
    stw_n = [CW[("North", v)] for v in VARS]
    ev = {"north_ge2_50": 0, "all_ge4_10": 0}
    by = {}
    for b, n in counts.items():
        b = b.replace(" ", "")
        bit = lambda i: b[-1 - i] == "1"   # noqa: E731
        n50 = sum(bit(i) for i in north50)
        ev["north_ge2_50"] += n * (n50 >= 2)
        ev["all_ge4_10"] += n * (sum(bit(i) for i in all10) >= 4)
        key = "".join("1" if bit(i) else "0" for i in stw_n)
        by.setdefault(key, [0, 0])
        by[key][0] += n
        by[key][1] += n * (n50 >= 2)
    return {"shots": tot, "north_ge2_50": ev["north_ge2_50"] / tot, "all_ge4_10": ev["all_ge4_10"] / tot,
            "north_ge2_50_by_stw": {k: (v[1] / v[0] if v[0] else None) for k, v in sorted(by.items())},
            "shots_by_stw": {k: v[0] for k, v in sorted(by.items())}}


def main():
    qc = circuit()
    be = get_backend()
    t = transpile(qc, be, optimization_level=3, seed_transpiler=11)
    ops = t.count_ops()
    twoq = int(sum(v for g, v in ops.items() if g in ("cz", "cx", "ecr")))
    print(f"{NQ} qubits, {twoq} two-qubit gates, depth {t.depth()} on {args.backend}")
    if args.dry_run:
        return
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rec = {"backend": args.backend, "device": args.iqm_name if args.backend == "iqm" else args.backend,
           "qubits": NQ, "two_qubit_gates": twoq, "depth": int(t.depth()), "shots": args.shots, "created_utc": stamp,
           "model": "out/weather_model.json", "exact": {k: M["exact"][k] for k in ("north_ge2_50", "all_ge4_10",
                                                                                  "north_ge2_50_by_stw")}, "jobs": []}
    out = ROOT / "out" / "runs" / f"big-{args.backend}{'-' + args.iqm_name if args.backend == 'iqm' else ''}-{stamp}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    job = be.run(t, shots=args.shots)
    rec["jobs"].append(job.job_id() if hasattr(job, "job_id") else None)
    out.write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")
    counts = job.result().get_counts(0)
    rec["counts"] = {str(k): int(v) for k, v in counts.items()}
    rec["result"] = derive(counts)
    out.write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")
    r, e = rec["result"], rec["exact"]
    print("saved", out)
    print(f"P(≥2 of 5 North over 1-in-50): run {100*r['north_ge2_50']:.2f} %  exact {100*e['north_ge2_50']:.2f} %")
    print(f"P(≥4 of 14 over 1-in-10):      run {100*r['all_ge4_10']:.1f} %  exact {100*e['all_ge4_10']:.1f} %")
    for k in ("000", "100", "001", "101", "111"):
        rv = r["north_ge2_50_by_stw"].get(k)
        print(f"  North snow/temp/rain high={k}: run {'-' if rv is None else f'{100*rv:.2f} %'}  "
              f"exact {100*e['north_ge2_50_by_stw'][k]:.2f} %  ({r['shots_by_stw'].get(k, 0)} shots)")


if __name__ == "__main__":
    main()
