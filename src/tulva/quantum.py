"""Quantum circuits for Tulva.

Two circuit families, both built from the two-level flood model in factor.py:

* Loader (full scale): national qubit -> cluster qubits -> area qubits. Each arrow is one RY plus one
  controlled RY, so the gate count grows linearly with the number of areas. Sampling it draws flood
  scenarios with the model's correlations built in.

* Joint-trigger amplitude estimation (small): hydrology qubit + 2 or 3 area qubits. The event we price
  ("both areas trigger", "at least 2 of 3 trigger") is marked directly on the area qubits with CZ gates,
  so there is no adder, comparator or extra objective qubit. Grover powers k amplify the event's
  probability; maximum-likelihood amplitude estimation (MLAE) turns the counts into an estimate.
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit


def _angle(p: float) -> float:
    return 2 * np.arcsin(np.sqrt(np.clip(p, 0.0, 1.0)))


def _conditional_ry(qc: QuantumCircuit, control: int, target: int, p0: float, p1: float) -> None:
    """Target gets P(1) = p0 if control is |0>, p1 if control is |1>.  One RY + one CRY."""
    qc.ry(_angle(p0), target)
    qc.cry(_angle(p1) - _angle(p0), control, target)


# ── loader ────────────────────────────────────────────────────────────────────

def loader(model, areas: list[int] | None = None, measure: bool = True) -> QuantumCircuit:
    """Qubit 0 = national W, then one qubit per cluster used, then one per area."""
    areas = list(range(model.n_areas)) if areas is None else list(areas)
    clusters = sorted(set(model.area_cluster[areas]))
    n = 1 + len(clusters) + len(areas)
    qc = QuantumCircuit(n, len(areas)) if measure else QuantumCircuit(n)
    qc.ry(_angle(model.p_wet), 0)
    for i, c in enumerate(clusters):
        _conditional_ry(qc, 0, 1 + i, *model.p_cluster_wet[c])
    for j, a in enumerate(areas):
        cq = 1 + clusters.index(model.area_cluster[a])
        _conditional_ry(qc, cq, 1 + len(clusters) + j, *model.p_area[a])
    if measure:
        qc.measure(range(1 + len(clusters), n), range(len(areas)))
    return qc


# ── joint-trigger amplitude estimation ───────────────────────────────────────

def a_operator(p_wet: float, p_area: list[tuple[float, float]]) -> QuantumCircuit:
    """Qubit 0 = hydrology state (wet with p_wet); qubits 1.. = areas with P(trigger | dry), P(trigger | wet)."""
    qc = QuantumCircuit(1 + len(p_area), name="A")
    qc.ry(_angle(p_wet), 0)
    for i, (p0, p1) in enumerate(p_area):
        _conditional_ry(qc, 0, 1 + i, p0, p1)
    return qc


def mark_event(qc: QuantumCircuit, event: str, n_areas: int) -> None:
    """Phase -1 on the good states. 'all': every area triggers. 'atleast2' (3 areas): majority.

    majority(a,b,c) = ab ⊕ bc ⊕ ca, so three CZs give exactly (-1)^majority.
    """
    areas = list(range(1, 1 + n_areas))
    if event == "all":
        if n_areas == 2:
            qc.cz(areas[0], areas[1])
        else:
            qc.h(areas[-1])
            qc.mcx(areas[:-1], areas[-1])
            qc.h(areas[-1])
    elif event == "atleast2":
        assert n_areas == 3
        qc.cz(areas[0], areas[1])
        qc.cz(areas[1], areas[2])
        qc.cz(areas[0], areas[2])
    else:
        raise ValueError(event)


def reflect_zero(qc: QuantumCircuit) -> None:
    """Reflection about |0...0> (up to a global phase)."""
    q = list(range(qc.num_qubits))
    qc.x(q)
    qc.h(q[-1])
    qc.mcx(q[:-1], q[-1])
    qc.h(q[-1])
    qc.x(q)


def grover_circuit(A: QuantumCircuit, k: int, event: str, measure: bool = True) -> QuantumCircuit:
    """A followed by k Grover iterates Q = A S0 A† S_chi; measures the area qubits."""
    n_areas = A.num_qubits - 1
    qc = QuantumCircuit(A.num_qubits, n_areas) if measure else QuantumCircuit(A.num_qubits)
    qc.compose(A, inplace=True)
    for _ in range(k):
        mark_event(qc, event, n_areas)
        qc.compose(A.inverse(), inplace=True)
        reflect_zero(qc)
        qc.compose(A, inplace=True)
    if measure:
        qc.measure(range(1, A.num_qubits), range(n_areas))
    return qc


def is_good(bitstring: str, event: str) -> bool:
    """bitstring as returned by qiskit counts (area n-1 ... area 0)."""
    ones = bitstring.replace(" ", "").count("1")
    n = len(bitstring.replace(" ", ""))
    return ones == n if event == "all" else ones >= 2


def good_fraction(counts: dict, event: str) -> tuple[int, int]:
    good = sum(v for b, v in counts.items() if is_good(b, event))
    return good, sum(counts.values())


# ── estimation ───────────────────────────────────────────────────────────────

_THETA = np.linspace(1e-5, np.pi / 2 - 1e-5, 20001)


def mlae(hits: list[int], shots: list[int], ks: list[int], gain: list[float] | None = None,
         offset: list[float] | None = None) -> float:
    """Maximum-likelihood amplitude estimation (Suzuki et al. 2020).

    Ideal model: P(good | k) = sin^2((2k+1)θ), a = sin^2 θ.
    Noise-aware model: P = gain_k * sin^2((2k+1)θ) + offset_k, with gain_k and offset_k measured on two
    calibration circuits with the same gates but known answers.
    """
    ll = np.zeros_like(_THETA)
    for i, (h, s, k) in enumerate(zip(hits, shots, ks)):
        p = np.sin((2 * k + 1) * _THETA) ** 2
        if gain is not None:
            p = gain[i] * p + (offset[i] if offset is not None else 0.0)
        p = np.clip(p, 1e-12, 1 - 1e-12)
        ll += h * np.log(p) + (s - h) * np.log(1 - p)
    return float(np.sin(_THETA[np.argmax(ll)]) ** 2)


def oracle_queries(shots: list[int], ks: list[int]) -> int:
    """Model evaluations used: one shot at Grover power k applies A (2k+1) times."""
    return int(sum(s * (2 * k + 1) for s, k in zip(shots, ks)))
