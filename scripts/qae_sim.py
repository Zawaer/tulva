"""Thursday milestone: joint-trigger amplitude estimation on a simulator, checked against the exact value.

Instance: two Lapland areas (Kittilä, Ivalo) both passing their 1-in-50 spring level ("both flood", as in
May 2005), 3 qubits. Also a 3-area "at least 2 of 3" instance (4 qubits).

Parameters come from out/model_params.json when the data pipeline has produced it; until then the
placeholders below are used and the output says so.

Outputs out/qae_sim.json and prints a summary.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from qiskit import transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tulva import factor, quantum as q  # noqa: E402

OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(8)

# ── parameters ────────────────────────────────────────────────────────────────
params_file = OUT / "model_params.json"
if params_file.exists():
    P = json.loads(params_file.read_text())
    source = "out/model_params.json (fitted to SYKE data)"
    lap = P["clusters"]["North"]
    a_nat, b_cl = lap["national_loading"], lap["cluster_loading"]
else:
    source = "PLACEHOLDER loadings (data pipeline not finished yet)"
    a_nat, b_cl = 0.40, 0.60

TRIGGER = 1 / 50
# March outlook: a top-15 % snow year shifts the factor mean by skill * E[O | O in top 15 %]
from scipy.stats import norm as _norm  # noqa: E402
skill_file = OUT / "snow_skill.json"
SKILL = (json.loads(skill_file.read_text())["clusters"]["North"]["outlook_skill_vs_latent_factor"]
         if skill_file.exists() else 0.7)
OUTLOOK_SHIFT = SKILL * _norm.pdf(_norm.ppf(0.85)) / 0.15
results_skill = {"north_outlook_skill": SKILL, "outlook_shift_sd": OUTLOOK_SHIFT}
# one cluster, 3 areas (Kittilä, Ivalo, Rovaniemi); areas share loadings in this instance
model = factor.build_two_level(np.full(3, a_nat), np.full(3, b_cl), np.zeros(3, int), np.full(3, TRIGGER))
model_hi = factor.build_two_level(np.full(3, a_nat), np.full(3, b_cl), np.zeros(3, int), np.full(3, TRIGGER),
                                  outlook_shift=OUTLOOK_SHIFT)


def hydrology_prior(m: factor.TwoLevelModel) -> tuple[float, list[tuple[float, float]]]:
    """Collapse W -> S -> areas to the single hydrology qubit the small circuit uses (S itself)."""
    p_s = m.p_wet * m.p_cluster_wet[0, 1] + (1 - m.p_wet) * m.p_cluster_wet[0, 0]
    return float(p_s), [tuple(m.p_area[i]) for i in range(m.n_areas)]


def exact_event(m, n_areas: int, event: str) -> float:
    dist = m.count_distribution(list(range(n_areas)))
    return float(dist[n_areas]) if event == "all" else float(dist[2:].sum())


def noise_model(p2: float, ro: float) -> NoiseModel:
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(p2 / 10, 1), ["sx", "x", "rz"])
    nm.add_all_qubit_quantum_error(depolarizing_error(p2, 2), ["cz"])
    nm.add_all_qubit_readout_error(ReadoutError([[1 - ro, ro], [1.5 * ro, 1 - 1.5 * ro]]))
    return nm


BASIS = ["cz", "rz", "sx", "x"]
from qiskit.transpiler import CouplingMap  # noqa: E402
GRID = CouplingMap.from_grid(2, 3)  # tiny square-lattice stand-in (IQM chips are square lattices)
results = {**results_skill, "parameter_source": source, "trigger": "1-in-50 spring maximum", "instances": {}}

for label, n_areas, event in [("kittila_ivalo_both", 2, "all"), ("lapland_atleast2of3", 3, "atleast2")]:
    for outlook, m in [("climatology", model), ("high_march_outlook", model_hi)]:
        p_s, p_area = hydrology_prior(m)
        A = q.a_operator(p_s, p_area[:n_areas])
        exact = exact_event(m, n_areas, event)
        # independence reference: same marginals, no shared hydrology
        p_marg = [p_s * p1 + (1 - p_s) * p0 for p0, p1 in p_area[:n_areas]]
        dist = np.array([1.0])
        for p in p_marg:
            dist = np.convolve(dist, [1 - p, p])
        indep = float(dist[n_areas]) if event == "all" else float(dist[2:].sum())

        # 1) circuit correctness: statevector good-probability for k = 0..3 vs theory
        theta = np.arcsin(np.sqrt(exact))
        sv_check = []
        for k in range(4):
            qc = q.grover_circuit(A, k, event, measure=False)
            pr = Statevector(qc).probabilities()
            good = sum(p for i, p in enumerate(pr)
                       if q.is_good(format(i >> 1, f"0{n_areas}b"), event))
            sv_check.append(abs(good - np.sin((2 * k + 1) * theta) ** 2))
        assert max(sv_check) < 1e-9, f"circuit wrong: {sv_check}"

        # 2) ideal-simulator MLAE, k = 0..3, 1000 shots each, vs Monte Carlo at the same number of queries
        ks, shots = [0, 1, 2, 3], [1000] * 4
        sim = AerSimulator()
        est = []
        for rep in range(20):
            hits = []
            for k in ks:
                t = transpile(q.grover_circuit(A, k, event), sim, seed_transpiler=1)
                cnt = sim.run(t, shots=1000, seed_simulator=100 * rep + k).result().get_counts()
                hits.append(q.good_fraction(cnt, event)[0])
            est.append(q.mlae(hits, shots, ks))
        nq = q.oracle_queries(shots, ks)
        mc = rng.binomial(nq, exact, 4000) / nq

        # 3) noisy simulator (two-qubit error 0.5 %, readout 2 %), with gate counts on a grid layout
        noisy = AerSimulator(noise_model=noise_model(0.005, 0.02))
        cz, hits_noisy = [], []
        for k in ks:
            t = transpile(q.grover_circuit(A, k, event), basis_gates=BASIS, coupling_map=GRID,
                          optimization_level=3, seed_transpiler=1)
            cz.append(int(t.count_ops().get("cz", 0)))
            cnt = noisy.run(t, shots=4000, seed_simulator=7 + k).result().get_counts()
            hits_noisy.append(q.good_fraction(cnt, event)[0])
        raw_noisy = q.mlae(hits_noisy, [4000] * 4, ks)

        results["instances"][f"{label}/{outlook}"] = {
            "qubits": A.num_qubits,
            "exact": exact,
            "if_independent": indep,
            "joint_multiplier": exact / indep,
            "statevector_max_error": max(sv_check),
            "qae_ideal_mean": float(np.mean(est)),
            "qae_ideal_rmse": float(np.sqrt(np.mean((np.array(est) - exact) ** 2))),
            "mc_same_queries_rmse": float(np.sqrt(np.mean((mc - exact) ** 2))),
            "oracle_queries": nq,
            "cz_by_k_grid": cz,
            "qae_noisy_raw": raw_noisy,
        }

# Loader: 3 areas, sample vs exact count distribution
L = q.loader(model, [0, 1, 2])
cnt = AerSimulator().run(transpile(L, AerSimulator()), shots=20000, seed_simulator=3).result().get_counts()
emp = np.zeros(4)
for b, v in cnt.items():
    emp[b.count("1")] += v / 20000
results["loader_check"] = {"exact": model.count_distribution([0, 1, 2]).tolist(), "sampled": emp.tolist()}

(OUT / "qae_sim.json").write_text(json.dumps(results, indent=2))
print("parameters:", source)
for k, v in results["instances"].items():
    print(f"{k:42s} exact {100*v['exact']:.3f}%  indep {100*v['if_independent']:.3f}%  ×{v['joint_multiplier']:.1f}"
          f" | QAE ideal {100*v['qae_ideal_mean']:.3f}% (rmse {100*v['qae_ideal_rmse']:.3f}pp, MC {100*v['mc_same_queries_rmse']:.3f}pp)"
          f" | noisy raw {100*v['qae_noisy_raw']:.3f}%  CZ {v['cz_by_k_grid']}")
print("loader exact", np.round(results["loader_check"]["exact"], 4), "sampled", np.round(emp, 4))
