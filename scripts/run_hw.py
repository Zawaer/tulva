"""Run the Tulva QAE batch on a backend and save everything needed to analyse it later.

    python scripts/run_hw.py --backend sim-noisy                       # local rehearsal, generic noise
    .venv-iqm/bin/python scripts/run_hw.py --backend iqm-fake            # rehearsal with IQM's noise model (20q)
    IQM_TOKEN=... .venv-iqm/bin/python scripts/run_hw.py --backend iqm --iqm-name garnet   # IQM Resonance
    python scripts/run_hw.py --backend ibm-fake                         # rehearsal with ibm_kingston's noise
    python scripts/run_hw.py --backend ibm --ibm-name ibm_kingston      # IBM Quantum (saved account)
    python scripts/run_hw.py --backend q20 [--ems 2]                    # Aalto Q20 on LUMI

IQM's Qiskit plugin needs an older Qiskit than IBM's runtime, so IQM runs use the separate .venv-iqm
(see README).

Batch = for each instance and each Grover power k: the target circuit and two calibration twins with the
same gates and layout but known answers: one large ("twin") and one ≈ 0 ("zero"). Together they give an
affine noise model per k, observed = gain_k * ideal + offset_k, which the noise-aware estimate inverts.

Every job id and raw count dict is written to out/runs/<backend>-<timestamp>.json before analysis, so
nothing is lost if a session dies (results can be re-fetched with backend.retrieve_job(job_id)).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

import numpy as np
from qiskit import transpile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tulva import factor, quantum as q  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--backend", default="sim-noisy", choices=["sim", "sim-noisy", "iqm", "iqm-fake", "ibm", "ibm-fake", "q20"])
ap.add_argument("--ibm-name", default="ibm_kingston")
ap.add_argument("--iqm-name", default="garnet", help="IQM Resonance device, e.g. garnet (20q), emerald (54q)")
ap.add_argument("--iqm-fake", default="apollo", choices=["apollo", "aphrodite"],
                help="IQM fake backend: apollo = 20-qubit square lattice, aphrodite = 54-qubit")
ap.add_argument("--ems", type=int, default=0, help="FiQCI-EMS mitigation level (q20 only); 0 = raw")
ap.add_argument("--shots", type=int, default=2000)
ap.add_argument("--ks", default="0,1,2,3")
ap.add_argument("--repeats", type=int, default=1)
args = ap.parse_args()
KS = [int(k) for k in args.ks.split(",")]


def get_backend():
    if args.backend in ("sim", "sim-noisy"):
        from qiskit_aer import AerSimulator
        from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error
        if args.backend == "sim":
            return AerSimulator()
        nm = NoiseModel()
        nm.add_all_qubit_quantum_error(depolarizing_error(0.0005, 1), ["sx", "x", "rz"])
        nm.add_all_qubit_quantum_error(depolarizing_error(0.005, 2), ["cz"])
        nm.add_all_qubit_readout_error(ReadoutError([[0.98, 0.02], [0.03, 0.97]]))
        return AerSimulator(noise_model=nm, basis_gates=["cz", "rz", "sx", "x"])
    if args.backend == "iqm":
        from iqm.qiskit_iqm import IQMProvider
        url = os.getenv("IQM_SERVER_URL", "https://resonance.meetiqm.com")
        return IQMProvider(url, quantum_computer=args.iqm_name, token=os.environ["IQM_TOKEN"]).get_backend()
    if args.backend == "iqm-fake":
        from iqm.qiskit_iqm import IQMFakeAphrodite, IQMFakeApollo
        return (IQMFakeApollo if args.iqm_fake == "apollo" else IQMFakeAphrodite)()
    if args.backend == "ibm-fake":
        from qiskit_ibm_runtime.fake_provider import FakeKingston
        return FakeKingston()
    if args.backend == "q20":
        from iqm.qiskit_iqm import IQMProvider
        be = IQMProvider(os.getenv("Q20_CORTEX_URL"), quantum_computer="radiance20").get_backend()
        if args.ems:
            from fiqci.ems import FiQCIBackend   # API may differ by version: check help() on LUMI
            be = FiQCIBackend(be, mitigation_level=args.ems)
        return be
    from qiskit_ibm_runtime import QiskitRuntimeService
    return QiskitRuntimeService().backend(args.ibm_name)


# ── instances (parameters from the fitted model when available) ──────────────
pf = ROOT / "out" / "model_params.json"
if pf.exists():
    lap = json.loads(pf.read_text())["clusters"]["North"]
    A_NAT, B_CL, SRC = lap["national_loading"], lap["cluster_loading"], "out/model_params.json"
else:
    A_NAT, B_CL, SRC = 0.40, 0.60, "PLACEHOLDER"


def collapse(m):
    p_s = m.p_wet * m.p_cluster_wet[0, 1] + (1 - m.p_wet) * m.p_cluster_wet[0, 0]
    return float(p_s), [tuple(m.p_area[i]) for i in range(m.n_areas)]


def instance(trigger: float, shift: float = 0.0):
    return factor.build_two_level(np.full(3, A_NAT), np.full(3, B_CL), np.zeros(3, int), np.full(3, trigger),
                                  outlook_shift=shift)


INSTANCES = {
    "A3_kittila_ivalo_both": (2, "all"),
    "A4_lapland_atleast2of3": (3, "atleast2"),
}
TARGET = instance(1 / 50)
TWIN = instance(1 / 6)       # same structure, larger answer → measures how much signal survives (gain)
ZERO = instance(1e-5)        # same structure, answer ≈ 0 → measures false positives (offset)


def exact(m, n, event):
    d = m.count_distribution(list(range(n)))
    return float(d[n]) if event == "all" else float(d[2:].sum())


def main():
    backend = get_backend()
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    record = {"backend": args.backend, "ems": args.ems, "shots": args.shots, "ks": KS, "param_source": SRC,
              "created_utc": stamp, "circuits": [], "jobs": []}
    circuits = []
    for name, (n, event) in INSTANCES.items():
        for role, m in (("target", TARGET), ("twin", TWIN), ("zero", ZERO)):
            p_s, p_area = collapse(m)
            A = q.a_operator(p_s, p_area[:n])
            for k in KS:
                for r in range(args.repeats):
                    qc = q.grover_circuit(A, k, event)
                    qc.name = f"{name}|{role}|k{k}|r{r}"
                    circuits.append(qc)
                    record["circuits"].append({"name": qc.name, "instance": name, "role": role, "k": k,
                                               "rep": r, "event": event, "n_areas": n,
                                               "exact": exact(m, n, event)})
    # fix the layout so target and twin land on the same physical qubits
    tqcs = transpile(circuits, backend, optimization_level=3, seed_transpiler=11)
    for c, t in zip(record["circuits"], tqcs):
        ops = t.count_ops()
        c["two_qubit_gates"] = int(sum(v for g, v in ops.items() if g in ("cz", "cx", "ecr")))
        c["depth"] = int(t.depth())
    out_dir = ROOT / "out" / "runs"
    out_dir.mkdir(parents=True, exist_ok=True)
    dev = {"iqm": args.iqm_name, "iqm-fake": args.iqm_fake, "ibm": args.ibm_name}.get(args.backend, "")
    record["device"] = dev or args.backend
    path = out_dir / f"{args.backend}{'-' + dev if dev else ''}{'-ems' + str(args.ems) if args.ems else ''}-{stamp}.json"

    if args.backend in ("ibm", "ibm-fake"):
        from qiskit_ibm_runtime import SamplerV2
        sampler = SamplerV2(mode=backend)
        if args.backend == "ibm":   # error suppression that the Sampler supports
            sampler.options.dynamical_decoupling.enable = True
            sampler.options.dynamical_decoupling.sequence_type = "XY4"
            sampler.options.twirling.enable_gates = True
        job = sampler.run(tqcs, shots=args.shots)
        record["jobs"].append(job.job_id())
        path.write_text(json.dumps(record, indent=2))
        res = job.result()
        counts = [r.data.c.get_counts() if hasattr(r.data, "c") else next(iter(r.data.values())).get_counts()
                  for r in res]
    else:
        job = backend.run(tqcs, shots=args.shots)
        record["jobs"].append(job.job_id())
        path.write_text(json.dumps(record, indent=2))          # job id saved before waiting
        result = job.result()
        counts = [result.get_counts(i) for i in range(len(tqcs))]
    for c, cnt in zip(record["circuits"], counts):
        c["counts"] = {str(k): int(v) for k, v in cnt.items()}
    path.write_text(json.dumps(record, indent=2))
    print("saved", path)


if __name__ == "__main__":
    main()
