"""Middle-sized circuit: North cluster, snow + spring temperature + rain -> 5 rivers. Where is the hardware limit?

    python scripts/run_mid_hw.py --backend sim --levels 10            # exact + ideal check
    .venv-iqm/bin/python scripts/run_mid_hw.py --backend iqm-fake --dry-run --levels 10,50
    IQM_TOKEN=... .venv-iqm/bin/python scripts/run_mid_hw.py --backend iqm --levels 10 --shots 20000
    IQM_TOKEN=... .venv-iqm/bin/python scripts/run_mid_hw.py --backend iqm --levels 10,50 --shots 20000

Qubits: 0-2 North snow / temp / rain ("high" = top 30 %), 3 wet spring W (fitted P(W | s,t,r), out/weather_model.json),
4-8 the five North areas over 1-in-10, and with --levels 10,50 also 9-13 over 1-in-50 (only if over 1-in-10).
Sampling only (no Grover powers): the question is whether a 9- or 14-qubit sampler still gives the right joint
frequencies on today's chip. Exact reference = enumeration of the 2^4 weather states, areas independent given W.
Simplification: snow, temp and rain are independent qubits here (their within-cluster correlation is dropped).
"""
from __future__ import annotations

import argparse
import datetime as dt
import itertools
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
ap.add_argument("--backend", default="sim", choices=["sim", "iqm", "iqm-fake"])
ap.add_argument("--iqm-name", default="emerald")
ap.add_argument("--shots", type=int, default=20000)
ap.add_argument("--levels", default="10", choices=["10", "10,50"])
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()

VARS = ["snow", "temp", "rain"]
M = json.loads((ROOT / "out" / "weather_model.json").read_text(encoding="utf-8"))
C = M["network"]["clusters"]["North"]
P_HIGH = 1 - M["network"]["high_quantile"]
AREAS = [a["area"] for a in C["areas"]]
WITH50 = args.levels == "10,50"
NQ = 4 + len(AREAS) * (2 if WITH50 else 1)
Q_W = 3
Q10 = {a: 4 + i for i, a in enumerate(AREAS)}
Q50 = {a: 4 + len(AREAS) + i for i, a in enumerate(AREAS)}


def circuit() -> QuantumCircuit:
    qc = QuantumCircuit(NQ, NQ)
    for i in range(3):
        qc.ry(q._angle(P_HIGH), i)
    pw = C["p_wet_given_stw"]
    qc.append(UCRYGate([q._angle(pw[f"{i & 1}{(i >> 1) & 1}{(i >> 2) & 1}"]) for i in range(8)]), [Q_W, 0, 1, 2])
    for a in C["areas"]:
        q._conditional_ry(qc, Q_W, Q10[a["area"]], *a["p10"])
        if WITH50:
            qc.append(UCRYGate([0.0, q._angle(a["p50_given_10"][0]), 0.0, q._angle(a["p50_given_10"][1])]),
                      [Q50[a["area"]], Q10[a["area"]], Q_W])
    qc.measure(range(NQ), range(NQ))
    return qc


def count_dist(ps):
    d = np.array([1.0])
    for p in ps:
        d = np.convolve(d, [1 - p, p])
    return d


def exact() -> dict:
    res = {"ge2_10": 0.0, "ge2_50": 0.0, "ge2_10_by_stw": {}, "ge2_50_by_stw": {}, "p_stw": {}}
    for stw in itertools.product([0, 1], repeat=3):
        key = "".join(map(str, stw))
        p_stw = float(np.prod([P_HIGH if x else 1 - P_HIGH for x in stw]))
        pw = C["p_wet_given_stw"][key]
        e10 = e50 = 0.0
        for w, p_w in ((0, 1 - pw), (1, pw)):
            e10 += p_w * count_dist([a["p10"][w] for a in C["areas"]])[2:].sum()
            e50 += p_w * count_dist([a["p10"][w] * a["p50_given_10"][w] for a in C["areas"]])[2:].sum()
        res["p_stw"][key] = p_stw
        res["ge2_10_by_stw"][key], res["ge2_50_by_stw"][key] = float(e10), float(e50)
        res["ge2_10"] += p_stw * e10
        res["ge2_50"] += p_stw * e50
    return res


def derive(counts: dict) -> dict:
    tot = sum(counts.values())
    g10 = g50 = 0
    by = {}
    for b, n in counts.items():
        b = b.replace(" ", "")
        bit = lambda i: b[-1 - i] == "1"  # noqa: E731
        n10 = sum(bit(Q10[a]) for a in AREAS)
        n50 = sum(bit(Q50[a]) for a in AREAS) if WITH50 else 0
        key = "".join("1" if bit(i) else "0" for i in range(3))
        d = by.setdefault(key, [0, 0, 0])
        d[0] += n
        d[1] += n * (n10 >= 2)
        d[2] += n * (n50 >= 2)
        g10 += n * (n10 >= 2)
        g50 += n * (n50 >= 2)
    out = {"shots": tot, "ge2_10": g10 / tot, "shots_by_stw": {k: v[0] for k, v in sorted(by.items())},
           "ge2_10_by_stw": {k: v[1] / v[0] for k, v in sorted(by.items()) if v[0]}}
    if WITH50:
        out["ge2_50"] = g50 / tot
        out["ge2_50_by_stw"] = {k: v[2] / v[0] for k, v in sorted(by.items()) if v[0]}
    return out


def get_backend():
    if args.backend == "sim":
        from qiskit_aer import AerSimulator
        return AerSimulator()
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


def main():
    qc, ex = circuit(), exact()
    be = get_backend()
    t = transpile(qc, be, optimization_level=3, seed_transpiler=11)
    twoq = int(sum(v for g, v in t.count_ops().items() if g in ("cz", "cx", "ecr")))
    print(f"{NQ} qubits, {twoq} two-qubit gates, depth {t.depth()} on {args.backend}")
    if args.dry_run:
        return
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    tag = f"mid{NQ}-{args.backend}{'-' + args.iqm_name if args.backend == 'iqm' else ''}-{stamp}"
    rec = {"backend": args.backend, "device": args.iqm_name if args.backend == "iqm" else args.backend, "qubits": NQ,
           "levels": args.levels, "two_qubit_gates": twoq, "depth": int(t.depth()), "shots": args.shots,
           "created_utc": stamp, "model": "out/weather_model.json", "exact": ex, "jobs": []}
    out = ROOT / "out" / "runs" / f"{tag}.json"
    job = be.run(t, shots=args.shots)
    rec["jobs"].append(job.job_id() if hasattr(job, "job_id") else None)
    out.write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")
    counts = job.result().get_counts(0)
    rec["counts"] = {str(k): int(v) for k, v in counts.items()}
    rec["result"] = r = derive(counts)
    out.write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")
    print("saved", out)
    print(f"P(≥2 of 5 North over 1-in-10): run {100*r['ge2_10']:.2f} %  exact {100*ex['ge2_10']:.2f} %")
    if WITH50:
        print(f"P(≥2 of 5 North over 1-in-50): run {100*r['ge2_50']:.2f} %  exact {100*ex['ge2_50']:.2f} %")
    for k in ("000", "100", "001", "101", "111"):
        line = f"  snow/temp/rain high={k} ({r['shots_by_stw'].get(k, 0)} shots): 1-in-10 run {100*r['ge2_10_by_stw'].get(k, float('nan')):.1f} % exact {100*ex['ge2_10_by_stw'][k]:.1f} %"
        if WITH50:
            line += f" | 1-in-50 run {100*r['ge2_50_by_stw'].get(k, float('nan')):.2f} % exact {100*ex['ge2_50_by_stw'][k]:.2f} %"
        print(line)


if __name__ == "__main__":
    main()
