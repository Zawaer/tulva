"""Full-scale loader on real hardware: all 14 river flood-risk areas on one circuit (18 qubits).

Samples the two-level joint flood model at the 1-in-10 level (common enough to measure with a few thousand
shots, and directly comparable with the 65 observed years). Readout errors are the main bias for a wide,
shallow circuit, so the same job also runs two calibration circuits on the same qubits (all areas 0 / all 1)
and the count distribution of flooded areas is unfolded with the measured flip rates.

    .venv-iqm/bin/python scripts/run_loader_hw.py --backend iqm --iqm-name emerald
    .venv-iqm/bin/python scripts/run_loader_hw.py --backend iqm-fake          # rehearsal (54-qubit fake)
    .venv/bin/python     scripts/run_loader_hw.py --backend ibm --ibm-name ibm_marrakesh

Saves out/runs/loader-<backend>-<device>-<time>.json (job ids written before waiting) and prints
P(≥k areas) raw / readout-corrected / exact / independence / observed.
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
from scipy.optimize import nnls
from scipy.stats import binom

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tulva import factor, quantum as q  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--backend", default="iqm-fake", choices=["iqm", "iqm-fake", "ibm", "sim", "q50", "q20"])
ap.add_argument("--iqm-name", default="emerald")
ap.add_argument("--ibm-name", default="ibm_marrakesh")
ap.add_argument("--shots", type=int, default=8000)
ap.add_argument("--level", type=float, default=0.1, help="per-area trigger probability (0.1 = 1-in-10)")
ap.add_argument("--independent", action="store_true",
                help="control run: same circuit shape, all correlations switched off (loadings 0)")
args = ap.parse_args()

P = json.loads((ROOT / "out" / "model_params.json").read_text())
names = P["cluster_names"]
gauges = P["gauges"]
area_cluster = np.array([names.index(g["cluster"]) for g in gauges])
a_nat = np.full(len(gauges), P["national_loading"])
b_cl = np.array([P["cluster_loading"][g["cluster"]] for g in gauges])
if args.independent:
    # tiny (not zero) loadings: keeps the same gates as the real run (zero angles crash the transpiler); correlation ~1e-6
    a_nat, b_cl = np.full_like(a_nat, 1e-3), np.full_like(b_cl, 1e-3)
model = factor.build_two_level(a_nat, b_cl, area_cluster, np.full(len(gauges), args.level))
N = len(gauges)


def backend_():
    if args.backend == "iqm":
        from iqm.qiskit_iqm import IQMProvider
        os.environ["IQM_TOKEN"]
        return IQMProvider(os.getenv("IQM_SERVER_URL", "https://resonance.iqm.tech"),
                           quantum_computer=args.iqm_name).get_backend()
    if args.backend in ("q50", "q20"):     # on LUMI with the fiqci-vtt-qiskit module and DEVICES set
        from iqm.qiskit_iqm import IQMProvider
        dev = "q50" if args.backend == "q50" else "radiance20"
        url = os.getenv("Q50_CORTEX_URL" if args.backend == "q50" else "Q20_CORTEX_URL")
        return IQMProvider(url, quantum_computer=dev).get_backend()
    if args.backend == "iqm-fake":
        from iqm.qiskit_iqm import IQMFakeAphrodite
        return IQMFakeAphrodite()
    if args.backend == "ibm":
        from qiskit_ibm_runtime import QiskitRuntimeService
        kw = {"channel": "ibm_quantum_platform", "token": os.environ["IBM_QUANTUM_TOKEN"]}
        return QiskitRuntimeService(**kw).backend(args.ibm_name)
    from qiskit_aer import AerSimulator
    return AerSimulator()


def readout_transfer(n: int, p01: float, p10: float) -> np.ndarray:
    """T[observed weight, true weight] for n independent bits with flip rates 0→1 p01 and 1→0 p10."""
    T = np.zeros((n + 1, n + 1))
    for w in range(n + 1):
        keep = binom.pmf(np.arange(w + 1), w, 1 - p10)          # ones that stay ones
        add = binom.pmf(np.arange(n - w + 1), n - w, p01)       # zeros that flip to one
        T[:, w] = np.convolve(keep, add)
    return T


def weight_dist(counts: dict, n: int) -> np.ndarray:
    d = np.zeros(n + 1)
    tot = sum(counts.values())
    for b, v in counts.items():
        d[b.replace(" ", "").count("1")] += v / tot
    return d


def main():
    be = backend_()
    L = q.loader(model)                                    # measures the 14 area qubits
    nq = L.num_qubits
    area_q = list(range(nq - N, nq))
    cal0 = QuantumCircuit(nq, N, name="cal_all0")
    cal0.measure(area_q, range(N))
    cal1 = QuantumCircuit(nq, N, name="cal_all1")
    cal1.x(area_q)
    cal1.measure(area_q, range(N))
    tL = transpile(L, be, optimization_level=3, seed_transpiler=3)
    layout = tL.layout.final_index_layout() if tL.layout is not None else None
    tcal = transpile([cal0, cal1], be, optimization_level=1, initial_layout=layout)
    circs = [tL, *tcal]
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dev = {"iqm": args.iqm_name, "ibm": args.ibm_name}.get(args.backend, args.backend)
    tag = "-control-indep" if args.independent else ""
    path = ROOT / "out" / "runs" / f"loader{tag}-{args.backend}-{dev}-{stamp}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    ops = tL.count_ops()
    rec = {"backend": args.backend, "device": dev, "created_utc": stamp, "shots": args.shots, "level": args.level,
           "control_independent": bool(args.independent), "qubits": nq, "two_qubit_gates": int(sum(v for g, v in ops.items() if g in ("cz", "cx", "ecr"))),
           "layout": layout, "jobs": []}
    if args.backend == "ibm":
        from qiskit_ibm_runtime import SamplerV2
        job = SamplerV2(mode=be).run(circs, shots=args.shots)
        rec["jobs"].append(job.job_id())
        path.write_text(json.dumps(rec, indent=2))
        counts = [r.data.c.get_counts() for r in job.result()]
    else:
        job = be.run(circs, shots=args.shots)
        rec["jobs"].append(job.job_id())
        path.write_text(json.dumps(rec, indent=2))
        res = job.result()
        counts = [res.get_counts(i) for i in range(len(circs))]
    raw = weight_dist(counts[0], N)
    p01 = float(sum(weight_dist(counts[1], N) * np.arange(N + 1)) / N)       # mean fraction read as 1 when 0
    p10 = float(1 - sum(weight_dist(counts[2], N) * np.arange(N + 1)) / N)   # mean fraction read as 0 when 1
    T = readout_transfer(N, p01, p10)
    corr, _ = nnls(T, raw)
    corr = corr / corr.sum()
    exact = model.count_distribution()
    ind = np.array([1.0])
    for i in range(N):
        pi = float(model.count_distribution([i])[1])
        ind = np.convolve(ind, [1 - pi, pi])
    tail = lambda d: [float(d[k:].sum()) for k in range(N + 1)]  # noqa: E731
    jc = json.loads((ROOT / "out" / "joint_counts.json").read_text()) if (ROOT / "out" / "joint_counts.json").exists() else {}
    rec.update({"counts": [{str(k): int(v) for k, v in c.items()} for c in counts], "readout_p01": p01,
                "readout_p10": p10, "p_at_least_k_raw": tail(raw), "p_at_least_k_readout_corrected": tail(corr),
                "p_at_least_k_exact": tail(exact), "p_at_least_k_independent": tail(ind),
                "observed_reference": jc})
    path.write_text(json.dumps(rec, indent=2))
    print(f"{dev}: {nq} qubits, {rec['two_qubit_gates']} two-qubit gates, readout p01={p01:.3f} p10={p10:.3f}")
    for k in (2, 3, 4, 5, 6):
        print(f"  P(≥{k}) raw {rec['p_at_least_k_raw'][k]:.3f}  corrected {rec['p_at_least_k_readout_corrected'][k]:.3f}"
              f"  exact {rec['p_at_least_k_exact'][k]:.3f}  independent {rec['p_at_least_k_independent'][k]:.3f}")
    print("saved", path)


if __name__ == "__main__":
    main()
