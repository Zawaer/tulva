"""Joint-trigger amplitude estimation written in Qrisp (for IQM hardware).

Same instance as quantum.py / scripts/qae_sim.py: "Kittilä and Ivalo both pass their 1-in-50 spring level",
three qubits, built from the North cluster of the fitted factor model. Here the qubits are typed Qrisp
variables rather than circuit indices:

    hydrology : QuantumBool   True = wet spring in the North (cluster driver above its 70 % quantile)
    kittila   : QuantumBool   True = Kittilä passes its 1-in-50 level
    ivalo     : QuantumBool   True = Ivalo passes its 1-in-50 level

State preparation A: RY on the hydrology bool, then each area gets RY(θ_dry) plus an extra RY(θ_wet - θ_dry)
inside `with control(hydrology)`. The oracle is `tag_state({kittila: True, ivalo: True})`, i.e. one CZ.
Grover powers come from Qrisp's `amplitude_amplification` (which builds the reflection about A|0> from the
same state function), and maximum-likelihood amplitude estimation (tulva.quantum.mlae) turns the counts
at k = 0, 1, 2 into an estimate. Qrisp's own `IQAE` is also wired up (`iqae_estimate`), but it needs
dozens of Grover iterates at a ≈ 0.1 %, so it is a simulator-only reference.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from qrisp import IQAE, QuantumBool, amplitude_amplification, control, multi_measurement, ry, x
from qrisp.grover import tag_state

from tulva import factor
from tulva import quantum as tq

ROOT = Path(__file__).resolve().parents[2]
TRIGGER = 1 / 50


@dataclass
class JointTrigger:
    """P(hydrology wet) and, per area, P(trigger | dry), P(trigger | wet)."""

    p_wet: float
    p_area: list[tuple[float, float]]
    names: tuple[str, ...] = ("kittila", "ivalo")

    def exact(self) -> float:
        """P(every area triggers), by enumeration of the hydrology bool."""
        both_dry = np.prod([p0 for p0, _ in self.p_area])
        both_wet = np.prod([p1 for _, p1 in self.p_area])
        return float((1 - self.p_wet) * both_dry + self.p_wet * both_wet)

    def if_independent(self) -> float:
        marg = [self.p_wet * p1 + (1 - self.p_wet) * p0 for p0, p1 in self.p_area]
        return float(np.prod(marg))


def north_instance(outlook_shift: float = 0.0, params_file: Path | None = None) -> JointTrigger:
    """Kittilä + Ivalo from the North cluster loadings, as in scripts/qae_sim.py (two-level model, wet = top 30 %)."""
    P = json.loads((params_file or ROOT / "out" / "model_params.json").read_text())
    north = P["clusters"]["North"]
    a, b = north["national_loading"], north["cluster_loading"]
    m = factor.build_two_level(np.full(2, a), np.full(2, b), np.zeros(2, int), np.full(2, TRIGGER),
                               outlook_shift=outlook_shift)
    # collapse W -> S -> areas to the single hydrology bool S (the cluster driver)
    p_s = m.p_wet * m.p_cluster_wet[0, 1] + (1 - m.p_wet) * m.p_cluster_wet[0, 0]
    inst = JointTrigger(float(p_s), [tuple(map(float, m.p_area[i])) for i in range(2)])
    assert abs(inst.exact() - m.p_at_least(2)) < 1e-12
    return inst


# ── Qrisp building blocks ────────────────────────────────────────────────────

def _angle(p: float) -> float:
    return float(2 * np.arcsin(np.sqrt(np.clip(p, 0.0, 1.0))))


def make_state_function(inst: JointTrigger):
    """A: hydrology bool, then each area conditioned on it."""
    th_w = _angle(inst.p_wet)
    th = [(_angle(p0), _angle(p1)) for p0, p1 in inst.p_area]

    def state_function(hydrology: QuantumBool, *areas: QuantumBool) -> None:
        ry(th_w, hydrology)
        for area, (t_dry, t_wet) in zip(areas, th):
            ry(t_dry, area)
            with control(hydrology):
                ry(t_wet - t_dry, area)

    return state_function


def oracle_all_trigger(hydrology: QuantumBool, *areas: QuantumBool) -> None:
    """Phase -1 on 'every area triggers' (for two areas this is a single CZ)."""
    tag_state({area: True for area in areas})


def allocate(inst: JointTrigger) -> list[QuantumBool]:
    return [QuantumBool(name="hydrology")] + [QuantumBool(name=n) for n in inst.names]


def grover_state(inst: JointTrigger, k: int) -> list[QuantumBool]:
    """A|0> followed by k Grover iterates Q = -A S0 A† S_chi, via qrisp.amplitude_amplification."""
    qbs = allocate(inst)
    sf = make_state_function(inst)
    sf(*qbs)
    if k:
        amplitude_amplification(qbs, sf, oracle_all_trigger, iter=k)
    return qbs


def good_probability(inst: JointTrigger, k: int, shots: int | None = None, backend=None) -> float:
    """Fraction of shots where every area reads True (shots=None: exact, from Qrisp's simulator)."""
    qbs = grover_state(inst, k)
    res = multi_measurement(qbs[1:], shots=shots, backend=backend)
    return float(sum(p for outcome, p in res.items() if all(outcome)))


def compiled_circuit(inst: JointTrigger, k: int):
    """The Qrisp QuantumCircuit for Grover power k, with the area bools measured."""
    qbs = grover_state(inst, k)
    qc = qbs[0].qs.compile()
    for qb in qbs[1:]:
        qc.measure(qb[0])
    return qc


def mlae_estimate(inst: JointTrigger, ks=(0, 1, 2), shots: int = 1000, backend=None) -> tuple[float, list[int]]:
    hits = [int(round(good_probability(inst, k, shots, backend) * shots)) for k in ks]
    return tq.mlae(hits, [shots] * len(ks), list(ks)), hits


def iqae_estimate(inst: JointTrigger, eps: float, alpha: float = 0.05, backend=None) -> float:
    """Qrisp's accelerated IQAE (arXiv:2407.16795). Needs a flag bool that is True on the good states."""
    sf = make_state_function(inst)

    def flagged_state(hydrology, *rest):
        *areas, flag = rest
        sf(hydrology, *areas)
        with control(list(areas)):
            x(flag)

    qargs = allocate(inst) + [QuantumBool(name="all_trigger")]
    mes = {"backend": backend} if backend is not None else {}
    return float(IQAE(qargs, flagged_state, eps=eps, alpha=alpha, mes_kwargs=mes))
