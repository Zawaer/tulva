"""'When does quantum matter?' Estimation error vs budget for the Kittilä+Ivalo joint-trigger QAE.

Lines: classical Monte Carlo (error ~ 1/sqrt(N)), QAE on an ideal simulator (~ 1/N), and QAE under
two-qubit error rates of 0.1 %, 0.3 % and 1 % (readout 1 %). Noisy outcome probabilities are computed
exactly with a density-matrix simulator, then binomial sampling gives many repetitions cheaply.
Budget is counted in oracle queries (model evaluations): a shot at Grover power k costs 2k+1.

Outputs out/qae_scaling.json and out/qae_scaling.png.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from qiskit import transpile
from qiskit.quantum_info import Statevector
from qiskit.transpiler import CouplingMap
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tulva import factor, quantum as q  # noqa: E402

OUT = ROOT / "out"
rng = np.random.default_rng(21)
lap = json.loads((OUT / "model_params.json").read_text())["clusters"]["North"]
m = factor.build_two_level(np.full(2, lap["national_loading"]), np.full(2, lap["cluster_loading"]),
                           np.zeros(2, int), np.full(2, 1 / 50))
p_s = m.p_wet * m.p_cluster_wet[0, 1] + (1 - m.p_wet) * m.p_cluster_wet[0, 0]
A = q.a_operator(float(p_s), [tuple(m.p_area[i]) for i in range(2)])
exact = float(m.count_distribution([0, 1])[2])
EVENT = "all"
KS_ALL = [0, 1, 2, 4, 8, 16]
SCHEDULES = [[0], [0, 1], [0, 1, 2], [0, 1, 2, 4], [0, 1, 2, 4, 8], [0, 1, 2, 4, 8, 16]]
SHOTS = 500
GRID = CouplingMap.from_grid(2, 2)
BASIS = ["cz", "rz", "sx", "x"]


def noise(p2):
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(p2 / 10, 1), ["sx", "x", "rz"])
    nm.add_all_qubit_quantum_error(depolarizing_error(p2, 2), ["cz"])
    nm.add_all_qubit_readout_error(ReadoutError([[0.99, 0.01], [0.015, 0.985]]))
    return nm


def good_probs(p2):
    out, cz = {}, {}
    for k in KS_ALL:
        if p2 is None:
            pr = Statevector(q.grover_circuit(A, k, EVENT, measure=False)).probabilities()
            out[k] = float(sum(p for i, p in enumerate(pr) if (i >> 1) == 0b11))
            continue
        t = transpile(q.grover_circuit(A, k, EVENT), basis_gates=BASIS, coupling_map=GRID,
                      optimization_level=3, seed_transpiler=2)
        cz[k] = int(t.count_ops().get("cz", 0))
        sim = AerSimulator(method="density_matrix", noise_model=noise(p2))
        res = sim.run(t, shots=400_000, seed_simulator=5).result().get_counts()
        out[k] = res.get("11", 0) / 400_000
    return out, cz


curves, gate_counts = {}, {}
for label, p2 in [("ideal", None), ("2q error 0.1%", 0.001), ("2q error 0.3%", 0.003), ("2q error 1%", 0.01)]:
    probs, cz = good_probs(p2)
    if cz:
        gate_counts = cz
    pts = []
    for sch in SCHEDULES:
        errs = [q.mlae([rng.binomial(SHOTS, probs[k]) for k in sch], [SHOTS] * len(sch), sch) - exact
                for _ in range(200)]
        pts.append({"kmax": max(sch), "queries": q.oracle_queries([SHOTS] * len(sch), sch),
                    "rmse": float(np.sqrt(np.mean(np.square(errs)))), "bias": float(np.mean(errs))})
    curves[label] = pts
    print(label, [(p["kmax"], f"{100*p['rmse']:.4f}pp") for p in pts], flush=True)

qmax = max(p["queries"] for p in curves["ideal"])
import glob as _g0  # noqa: E402
for _f in _g0.glob(str(OUT / "runs" / "*.analysis.json")):
    _a = json.loads(Path(_f).read_text()).get("A3_kittila_ivalo_both")
    if _a and (Path(_f).name.startswith("ibm-ibm") or Path(_f).name.startswith("iqm-garnet")):
        qmax = max(qmax, 1.3 * _a["oracle_queries"])
mc = [{"queries": float(n), "rmse": float(np.sqrt(exact * (1 - exact) / n))} for n in np.geomspace(SHOTS, qmax, 20)]
json.dump({"exact": exact, "shots_per_power": SHOTS, "two_qubit_gates_by_k_grid": gate_counts,
           "curves": curves, "monte_carlo": mc}, open(OUT / "qae_scaling.json", "w"), indent=2)

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

fig, ax = plt.subplots(figsize=(10, 6))
ax.loglog([p["queries"] for p in mc], [100 * p["rmse"] for p in mc], color="#222", lw=2.5,
          label="Classical Monte Carlo  (error ∝ 1/√N)")
_id = curves["ideal"][-1]
_xs = np.geomspace(_id["queries"], qmax, 10)
ax.loglog(_xs, 100 * _id["rmse"] * _id["queries"] / _xs, ":", color="#1f6feb", lw=1.5, alpha=0.7,
          label="Ideal QAE, extrapolated (∝ 1/N)")
styles = {"ideal": ("#1f6feb", "o-"), "2q error 0.1%": ("#2da44e", "s--"), "2q error 0.3%": ("#d4a72c", "^--"),
          "2q error 1%": ("#cf222e", "v:")}
for lab, pts in curves.items():
    col, st = styles[lab]
    name = "Quantum amplitude estimation, ideal  (∝ 1/N)" if lab == "ideal" else f"QAE with {lab}"
    ax.loglog([p["queries"] for p in pts], [100 * p["rmse"] for p in pts], st, color=col, lw=2, ms=6, label=name)
# real hardware points (Kittilä+Ivalo, calibrated estimate vs exact) from out/runs/*.analysis.json
import glob as _glob  # noqa: E402
hw_pts = []
for f in sorted(_glob.glob(str(OUT / "runs" / "*.analysis.json"))):
    name = Path(f).name
    if not (name.startswith("ibm-ibm") or name.startswith("iqm-garnet") or name.startswith("iqm-emerald")):
        continue
    a3 = json.loads(Path(f).read_text()).get("A3_kittila_ivalo_both")
    if not a3:
        continue
    est = a3.get("noise_aware_per_copy_mlae") or a3["noise_aware_mlae"]
    vendor = "IBM" if name.startswith("ibm") else "IQM"
    hw_pts.append((vendor, a3["oracle_queries"], abs(est - a3["exact"]), name))
for vendor, mk, col in (("IBM", "D", "#0f62fe"), ("IQM", "P", "#00a19a")):
    pts = [p for p in hw_pts if p[0] == vendor]
    if pts:
        ax.loglog([p[1] for p in pts], [100 * p[2] for p in pts], mk, color=col, ms=11, mec="black", mew=0.8,
                  label=f"Real hardware: {'IBM Marrakesh' if vendor == 'IBM' else 'IQM Garnet'} (calibrated, error vs exact)")
json.dump({"hardware_points": [{"vendor": v, "queries": int(qq), "abs_error": e, "run": n} for v, qq, e, n in hw_pts]},
          open(OUT / "qae_scaling_hardware_points.json", "w"), indent=2)
ax.set_xlabel("Model evaluations (oracle queries)", fontsize=12)
ax.set_ylabel("Error in P(both flood), percentage points", fontsize=12)
ax.set_title("When does quantum matter?  P(two-river North-cluster pair both pass their 1-in-50 level)\n"
             f"exact {100*exact:.3f} %  ·  3 qubits  ·  simulator curves + real hardware points", fontsize=13, loc="left")
ax.grid(True, which="both", alpha=0.25)
ax.legend(fontsize=9, frameon=True, framealpha=0.92, loc="lower left")
fig.text(0.01, 0.01, "Fitted to SYKE spring peaks 1961–2025. Noisy curves: depolarising noise + 1 % readout, "
         "square-lattice routing; simulator error = RMS over 200 repetitions.\nHardware points = |calibrated estimate − exact| of one run "
         "(mostly residual bias), at that run's total model evaluations.", fontsize=8, color="#666")
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(OUT / "qae_scaling.png", dpi=130)
print("saved out/qae_scaling.png; CZ by k:", gate_counts)
