"""Product-level QAE runs: the real Tulva North trigger and the March snow outlook, on hardware.

    python scripts/run_product_hw.py --backend sim                                   # ideal check
    .venv-iqm/bin/python scripts/run_product_hw.py --backend iqm-fake                # IQM noise rehearsal
    IQM_TOKEN=... .venv-iqm/bin/python scripts/run_product_hw.py --backend iqm --iqm-name emerald

Instances (North cluster loadings from out/model_params.json, two-level model as in run_hw.py):
* N5_north_atleast2of5_{clim,high}: the product trigger, "≥2 of 5 North gauges pass 1-in-50", without and
  with a top-15 % March snow outlook. 6 qubits; the ≥2-of-5 marker is a diagonal phase gate.
* A3_kittila_ivalo_both_{low,clim,high}: the 3-qubit instance under a bottom-15 % / no / top-15 % snow outlook.
  Same circuit shape in all three, only the rotation angles change, so the hardware sees the snow effect directly.

Each instance has the same two calibration twins as run_hw.py (large "twin", ≈0 "zero") with the same shape and
snow shift, so scripts/analyse_run.py works unchanged on the output in out/runs/product-<backend>-<stamp>.json.
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
from qiskit.circuit.library import DiagonalGate
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tulva import factor, quantum as q  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--backend", default="sim", choices=["sim", "iqm", "iqm-fake"])
ap.add_argument("--iqm-name", default="emerald", help="IQM Resonance device, e.g. garnet (20q), emerald (54q)")
ap.add_argument("--shots", type=int, default=4000)
ap.add_argument("--ks-n5", default="0,1", help="Grover powers for the 6-qubit product instance")
ap.add_argument("--ks-a3", default="0,1,2", help="Grover powers for the 3-qubit snow instances")
ap.add_argument("--instances", default="all", help="comma-separated instance names, or 'all'")
args = ap.parse_args()


def get_backend():
    if args.backend == "sim":
        from qiskit_aer import AerSimulator
        return AerSimulator()
    if args.backend == "iqm-fake":
        from iqm.qiskit_iqm import IQMFakeAphrodite
        return IQMFakeAphrodite()
    from iqm.qiskit_iqm import IQMProvider
    if "IQM_TOKEN" not in os.environ:   # read from the git-ignored .env
        env = ROOT / ".env"
        for line in env.read_text().splitlines() if env.exists() else []:
            if line.startswith("IQM_TOKEN=") and line.split("=", 1)[1].strip():
                os.environ["IQM_TOKEN"] = line.split("=", 1)[1].strip()
    url = os.getenv("IQM_SERVER_URL", "https://resonance.iqm.tech")
    return IQMProvider(url, quantum_computer=args.iqm_name).get_backend()


# ── model and snow outlook (same parameters as run_hw.py / qae_sim.py) ───────
north = json.loads((ROOT / "out" / "model_params.json").read_text())["clusters"]["North"]
A_NAT, B_CL = north["national_loading"], north["cluster_loading"]
SKILL = json.loads((ROOT / "out" / "snow_skill.json").read_text())["clusters"]["North"]["outlook_skill_vs_latent_factor"]
SHIFT = SKILL * norm.pdf(norm.ppf(0.85)) / 0.15     # mean shift after a top-15 % (or, negated, bottom-15 %) March
SNOW = {"low": -SHIFT, "clim": 0.0, "high": SHIFT}


def model(n: int, trigger: float, shift: float):
    return factor.build_two_level(np.full(n, A_NAT), np.full(n, B_CL), np.zeros(n, int), np.full(n, trigger),
                                  outlook_shift=shift)


def collapse(m):
    p_s = m.p_wet * m.p_cluster_wet[0, 1] + (1 - m.p_wet) * m.p_cluster_wet[0, 0]
    return float(p_s), [tuple(m.p_area[i]) for i in range(m.n_areas)]


def exact(m, n, event):
    d = m.count_distribution(list(range(n)))
    return float(d[n]) if event == "all" else float(d[2:].sum())


def mark_atleast2(qc: QuantumCircuit, n_areas: int) -> None:
    """Phase -1 on area states with ≥2 triggers (any n), as one diagonal gate for the transpiler to synthesise."""
    diag = [-1.0 if bin(i).count("1") >= 2 else 1.0 for i in range(2 ** n_areas)]
    qc.append(DiagonalGate(diag), list(range(1, 1 + n_areas)))


def grover(A: QuantumCircuit, k: int, event: str) -> QuantumCircuit:
    n = A.num_qubits - 1
    if event == "all" or n == 3:
        return q.grover_circuit(A, k, event)
    qc = QuantumCircuit(A.num_qubits, n)
    qc.compose(A, inplace=True)
    for _ in range(k):
        mark_atleast2(qc, n)
        qc.compose(A.inverse(), inplace=True)
        q.reflect_zero(qc)
        qc.compose(A, inplace=True)
    qc.measure(range(1, A.num_qubits), range(n))
    return qc


KS_N5 = [int(k) for k in args.ks_n5.split(",")]
KS_A3 = [int(k) for k in args.ks_a3.split(",")]
INSTANCES = {   # name: (n_areas, event, snow, ks)
    "N5_north_atleast2of5_clim": (5, "atleast2", "clim", KS_N5),
    "N5_north_atleast2of5_high": (5, "atleast2", "high", KS_N5),
    "A3_kittila_ivalo_both_low": (2, "all", "low", KS_A3),
    "A3_kittila_ivalo_both_clim": (2, "all", "clim", KS_A3),
    "A3_kittila_ivalo_both_high": (2, "all", "high", KS_A3),
}
ROLES = {"target": 1 / 50, "twin": 1 / 6, "zero": 1e-5}


def main():
    wanted = set(INSTANCES) if args.instances == "all" else set(args.instances.split(","))
    backend = get_backend()
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    record = {"backend": args.backend, "device": args.iqm_name if args.backend == "iqm" else args.backend,
              "shots": args.shots, "snow_shift_sd": SHIFT, "north_snow_skill": SKILL,
              "param_source": "out/model_params.json, out/snow_skill.json", "created_utc": stamp,
              "circuits": [], "jobs": []}
    circuits = []
    for name, (n, event, snow, ks) in INSTANCES.items():
        if name not in wanted:
            continue
        for role, trig in ROLES.items():
            m = model(n, trig, SNOW[snow])
            p_s, p_area = collapse(m)
            A = q.a_operator(p_s, p_area)
            for k in ks:
                qc = grover(A, k, event)
                qc.name = f"{name}|{role}|k{k}"
                circuits.append(qc)
                record["circuits"].append({"name": qc.name, "instance": name, "role": role, "k": k, "rep": 0,
                                           "event": event, "n_areas": n, "snow": snow,
                                           "exact": exact(m, n, event)})
    tqcs = transpile(circuits, backend, optimization_level=3, seed_transpiler=11)
    for c, t in zip(record["circuits"], tqcs):
        ops = t.count_ops()
        c["two_qubit_gates"] = int(sum(v for g, v in ops.items() if g in ("cz", "cx", "ecr")))
        c["depth"] = int(t.depth())
    out_dir = ROOT / "out" / "runs"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"product-{args.backend}{'-' + args.iqm_name if args.backend == 'iqm' else ''}-{stamp}.json"
    job = backend.run(tqcs, shots=args.shots)
    record["jobs"].append(job.job_id())
    path.write_text(json.dumps(record, indent=2))          # job id saved before waiting
    result = job.result()
    for i, c in enumerate(record["circuits"]):
        c["counts"] = {str(k): int(v) for k, v in result.get_counts(i).items()}
    path.write_text(json.dumps(record, indent=2))
    print("saved", path)
    for c in record["circuits"]:
        if c["role"] == "target":
            print(f"{c['instance']:30s} k={c['k']} exact {100 * c['exact']:.3f}%  2q={c['two_qubit_gates']}")


if __name__ == "__main__":
    main()
