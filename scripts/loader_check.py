"""Full-scale loader: all 14 river flood-risk areas on one circuit (1 national + 3 cluster + 14 area qubits = 18).

Checks, on a simulator, that sampling the circuit reproduces the exact count distribution of the two-level
model, at the 1-in-10 level (where we have observations to compare) and at the 1-in-50 insurance trigger.
Also reports gate counts on a 20-qubit square lattice (Q20-like) and a noisy-simulator run.

Outputs out/loader_check.json and out/loader_check.png.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from qiskit import transpile
from qiskit.transpiler import CouplingMap
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tulva import factor, quantum as q  # noqa: E402

OUT = ROOT / "out"
P = json.loads((OUT / "model_params.json").read_text())
names = P["cluster_names"]
gauges = P["gauges"]
area_names = [g["area"] for g in gauges]
area_cluster = np.array([names.index(g["cluster"]) for g in gauges])
a_nat = np.full(len(gauges), P["national_loading"])
b_cl = np.array([P["cluster_loading"][g["cluster"]] for g in gauges])
joint = json.loads((OUT / "joint_counts.json").read_text()) if (OUT / "joint_counts.json").exists() else None

GRID = CouplingMap.from_grid(4, 5)
BASIS = ["cz", "rz", "sx", "x"]
nm = NoiseModel()
nm.add_all_qubit_quantum_error(depolarizing_error(0.0005, 1), ["sx", "x", "rz"])
nm.add_all_qubit_quantum_error(depolarizing_error(0.005, 2), ["cz"])
nm.add_all_qubit_readout_error(ReadoutError([[0.98, 0.02], [0.03, 0.97]]))

res = {"areas": area_names, "levels": {}}
for label, trig in [("1-in-10", 0.1), ("1-in-50", 0.02)]:
    m = factor.build_two_level(a_nat, b_cl, area_cluster, np.full(len(gauges), trig))
    exact = m.count_distribution()
    L = q.loader(m)
    t = min((transpile(L, basis_gates=BASIS, coupling_map=GRID, optimization_level=3, seed_transpiler=s)
             for s in range(3)), key=lambda c: c.count_ops().get("cz", 0))
    cz = int(t.count_ops().get("cz", 0))
    depth2 = int(t.depth(lambda i: i.operation.num_qubits == 2))
    dist = {}
    for sim_name, sim, shots in [("ideal", AerSimulator(method="statevector"), 50_000),
                                 ("noisy", AerSimulator(method="matrix_product_state", noise_model=nm), 4_000)]:
        cnt = sim.run(t, shots=shots, seed_simulator=4).result().get_counts()
        d = np.zeros(len(gauges) + 1)
        for b, v in cnt.items():
            d[b.replace(" ", "").count("1")] += v / shots
        dist[sim_name] = d
    # independence with the same marginals
    p_marg = m.count_distribution([0])  # placeholder to keep API symmetric
    ind = np.array([1.0])
    for i in range(len(gauges)):
        pi = float(m.count_distribution([i])[1])
        ind = np.convolve(ind, [1 - pi, pi])
    tail = lambda d: [float(d[k:].sum()) for k in range(len(d))]  # noqa: E731
    res["levels"][label] = {
        "qubits": L.num_qubits, "cz_q20_like_grid": cz, "two_qubit_depth": depth2,
        "p_at_least_k_exact": tail(exact), "p_at_least_k_ideal_sampled": tail(dist["ideal"]),
        "p_at_least_k_noisy_sampled": tail(dist["noisy"]), "p_at_least_k_independent": tail(ind),
    }
    print(f"{label}: {L.num_qubits} qubits, {cz} CZ, 2q-depth {depth2}")
    for k in (2, 3, 4, 5):
        r = res["levels"][label]
        print(f"   P(≥{k}) exact {r['p_at_least_k_exact'][k]:.4f}  ideal {r['p_at_least_k_ideal_sampled'][k]:.4f}"
              f"  noisy {r['p_at_least_k_noisy_sampled'][k]:.4f}  independent {r['p_at_least_k_independent'][k]:.4f}")
if joint:
    res["observed_1in10_reference"] = joint
(OUT / "loader_check.json").write_text(json.dumps(res, indent=2))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

r = res["levels"]["1-in-10"]
ks = np.arange(1, 9)
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.semilogy(ks, [r["p_at_least_k_exact"][k] for k in ks], "-", color="#1f6feb", lw=2.5, label="Two-level model, exact")
ax.semilogy(ks, [r["p_at_least_k_ideal_sampled"][k] for k in ks], "o", color="#1f6feb", ms=7,
            label="Loader circuit, ideal simulator (50k shots)")
ax.semilogy(ks, [r["p_at_least_k_noisy_sampled"][k] for k in ks], "s", mfc="none", color="#d4a72c", ms=8,
            label="Loader circuit, noisy simulator (0.5 % CZ, 2–3 % readout, 4k shots)")
ax.semilogy(ks, [r["p_at_least_k_independent"][k] for k in ks], "--", color="#cf222e", lw=2,
            label="Independence (EIOPA 0 %)")
ax.set_xlabel("k = number of the 14 river areas over their 1-in-10 spring level")
ax.set_ylabel("P(k or more in the same spring)")
ax.set_title(f"Finland's joint spring-flood model on one circuit: {r['qubits']} qubits, {r['cz_q20_like_grid']} two-qubit gates",
             loc="left")
ax.grid(True, which="both", alpha=0.25)
ax.legend(frameon=False, fontsize=9)
fig.tight_layout()
fig.savefig(OUT / "loader_check.png", dpi=130)
