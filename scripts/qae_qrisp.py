"""Qrisp version of the joint-trigger QAE ("Kittilä and Ivalo both pass their 1-in-50 spring level").

    .venv-iqm/bin/python scripts/qae_qrisp.py                         # Qrisp simulator -> out/qrisp_qae.json
    .venv-iqm/bin/python scripts/qae_qrisp.py --backend fake-garnet   # IQM's Garnet noise model via QiskitBackend
    IQM_TOKEN=... .venv-iqm/bin/python scripts/qae_qrisp.py --backend iqm --device garnet   # IQM Resonance

What it does:
  1. checks the Qrisp circuits: P(both trigger) after k Grover iterates equals sin^2((2k+1)θ), a = sin^2 θ;
  2. MLAE over k = 0, 1, 2 (repeated on the simulator to get an RMSE), compared with the exact value
     (factor.py, same as out/qae_sim.json) and with Monte Carlo at the same number of oracle queries;
  3. Qrisp's own IQAE (simulator only: it needs many Grover iterates at a ≈ 0.1 %);
  4. gate counts after compiling for Garnet with IQM's Qrisp pass manager (CZ + PRX, routed on the
     20-qubit square lattice), with Qiskit's transpiler against the same fake device as a cross-check.
Hardware/fake runs go to out/runs/qrisp_qae_<backend>_<time>.json instead of out/qrisp_qae.json.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tulva import qrisp_qae as Q  # noqa: E402
from tulva import quantum as tq  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--backend", default="sim", choices=["sim", "fake-garnet", "iqm"])
ap.add_argument("--device", default="garnet", help="IQM Resonance device (with --backend iqm)")
ap.add_argument("--shots", type=int, default=1000)
ap.add_argument("--reps", type=int, default=None, help="MLAE repetitions (default 10 on sim, 1 otherwise)")
ap.add_argument("--ks", default="0,1,2")
ap.add_argument("--no-iqae", action="store_true")
args = ap.parse_args()
ks = [int(k) for k in args.ks.split(",")]
reps = args.reps or (10 if args.backend == "sim" else 1)

# ── backend ──────────────────────────────────────────────────────────────────
from iqm.qiskit_iqm.fake_backends.fake_garnet import IQMFakeGarnet  # noqa: E402
from iqm.qrisp_iqm import create_iqm_pass_manager  # noqa: E402

fake = IQMFakeGarnet()
connectivity = [tuple(e) for e in fake.coupling_map]
backend, device_label = None, "qrisp-simulator"
if args.backend == "fake-garnet":
    from qrisp.interface import QiskitBackend
    backend, device_label = QiskitBackend(fake), "IQMFakeGarnet (noise model)"
elif args.backend == "iqm":
    from iqm.qrisp_iqm import IQMBackend
    url = os.getenv("IQM_SERVER_URL", "https://resonance.iqm.tech")
    backend = IQMBackend(url, device_instance=args.device, token=os.environ["IQM_TOKEN"])
    connectivity, device_label = backend._connectivity, f"IQM {args.device} ({url})"

# ── instances (same parameters as scripts/qae_sim.py) ─────────────────────────
skill_file = ROOT / "out" / "snow_skill.json"
skill = json.loads(skill_file.read_text())["clusters"]["North"]["outlook_skill_vs_latent_factor"]
outlook_shift = skill * norm.pdf(norm.ppf(0.85)) / 0.15
instances = {"climatology": Q.north_instance(), "high_march_outlook": Q.north_instance(outlook_shift)}
ref_file = ROOT / "out" / "qae_sim.json"
ref = json.loads(ref_file.read_text())["instances"] if ref_file.exists() else {}

results = {
    "instance": "Kittilä AND Ivalo both pass their 1-in-50 spring level (North cluster, two-level model)",
    "backend": device_label, "ks": ks, "shots_per_k": args.shots, "reps": reps,
    "qrisp_version": __import__("qrisp").__version__ if hasattr(__import__("qrisp"), "__version__") else None,
    "instances": {},
}

for name, inst in instances.items():
    exact = inst.exact()
    ref_exact = ref.get(f"kittila_ivalo_both/{name}", {}).get("exact")
    if ref_exact is not None:
        assert abs(ref_exact - exact) < 1e-9, (ref_exact, exact)
    theta = np.arcsin(np.sqrt(exact))

    # 1) circuit check on Qrisp's exact simulator (it reports probabilities to 5 decimals)
    check = [abs(Q.good_probability(inst, k) - np.sin((2 * k + 1) * theta) ** 2) for k in ks]
    assert max(check) < 1e-5, check

    # 2) MLAE
    t0 = time.time()
    est, hits_all = [], []
    for _ in range(reps):
        e, hits = Q.mlae_estimate(inst, ks, args.shots, backend)
        est.append(e)
        hits_all.append(hits)
    nq = tq.oracle_queries([args.shots] * len(ks), ks)
    row = {
        "exact": exact,
        "if_independent": inst.if_independent(),
        "p_hydrology_wet": inst.p_wet,
        "p_trigger_dry_wet": inst.p_area[0],
        "circuit_check_max_abs_error": float(max(check)),
        "mlae_estimates": est,
        "mlae_mean": float(np.mean(est)),
        "mlae_rmse": float(np.sqrt(np.mean((np.array(est) - exact) ** 2))),
        "hits_by_k": hits_all,
        "oracle_queries": nq,
        "mc_same_queries_rmse": float(np.sqrt(exact * (1 - exact) / nq)),
        "seconds": round(time.time() - t0, 1),
    }
    # 3) Qrisp IQAE (simulator only)
    if args.backend == "sim" and not args.no_iqae:
        t0 = time.time()
        iq = [Q.iqae_estimate(inst, eps=3e-4, alpha=0.05) for _ in range(5)]
        row["qrisp_iqae"] = {"eps": 3e-4, "alpha": 0.05, "estimates": iq,
                             "mean": float(np.mean(iq)),
                             "rmse": float(np.sqrt(np.mean((np.array(iq) - exact) ** 2))),
                             "seconds": round(time.time() - t0, 1)}
    results["instances"][name] = row

# ── 4) gate counts for IQM ────────────────────────────────────────────────────
from qiskit import transpile  # noqa: E402

counts = {}
for k in ks:
    qc = Q.compiled_circuit(instances["climatology"], k)
    tc = create_iqm_pass_manager(connectivity).run(qc)
    ops = tc.count_ops()
    qk = transpile(qc.to_qiskit(), fake, optimization_level=3, seed_transpiler=1).count_ops()
    counts[str(k)] = {"qrisp_iqm_pass_manager": {"cz": int(ops.get("cz", 0)), "prx": int(ops.get("prx", 0))},
                      "qiskit_transpile_fake_garnet": {"cz": int(qk.get("cz", 0)), "r": int(qk.get("r", 0))}}
results["gate_counts_garnet"] = counts

stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
if args.backend == "sim":
    out = ROOT / "out" / "qrisp_qae.json"
else:
    out = ROOT / "out" / "runs" / f"qrisp_qae_{args.backend}_{args.device if args.backend == 'iqm' else ''}{stamp}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(results, indent=2))

print(f"\nbackend: {device_label}  ks={ks}  shots/k={args.shots}  reps={reps}")
for name, r in results["instances"].items():
    line = (f"{name:20s} exact {100*r['exact']:.4f}%  MLAE {100*r['mlae_mean']:.4f}% (rmse {100*r['mlae_rmse']:.4f}pp,"
            f" MC same queries {100*r['mc_same_queries_rmse']:.4f}pp)")
    if "qrisp_iqae" in r:
        line += f"  IQAE {100*r['qrisp_iqae']['mean']:.4f}% (rmse {100*r['qrisp_iqae']['rmse']:.4f}pp)"
    print(line)
for k, c in counts.items():
    print(f"k={k}: Qrisp/IQM pass manager CZ {c['qrisp_iqm_pass_manager']['cz']:3d} PRX {c['qrisp_iqm_pass_manager']['prx']:3d}"
          f" | Qiskit transpile CZ {c['qiskit_transpile_fake_garnet']['cz']:3d}")
print("wrote", out.relative_to(ROOT))
