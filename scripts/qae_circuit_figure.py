"""Stage figure of the quantum amplitude estimation (QAE) circuit we ran on hardware → out/stage_qae_circuit.png.

Circuit = instance A3_kittila_ivalo_both of scripts/run_hw.py (two-river North-cluster pair, event "both rivers pass
1-in-50"), built with the same gates as src/tulva/quantum.py:
  A operator   a_operator(): RY(θ_wet) on the wet-spring qubit; RY + CRY on each river qubit
  marking      mark_event(..., "all", 2): one CZ between the two river qubits (S_ψ)
  Grover step  grover_circuit(): Q = A S0 A† S_ψ, repeated k = 0, 1, 2 times (MLAE, no phase estimation)
The drawing is Qiskit's own ('mpl'); A† and S0 are drawn as labelled blocks so it stays legible at slide size.
Angles are the real ones of the run_hw.py target instance (2·arcsin(√p)), printed by this script.

    .venv/bin/python scripts/qae_circuit_figure.py
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister  # noqa: E402
from qiskit.circuit import Gate, Parameter  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "out"
NAVY, BLUE, GREY, PURPLE, LIGHT = "#0b1f3a", "#1f6feb", "#6b7280", "#8250df", "#f3f6fa"


def real_angles():
    """Angles of the target circuit in scripts/run_hw.py (same parameters, same collapse to 3 qubits)."""
    import json
    import numpy as np
    from tulva import factor, quantum as q
    lap = json.loads((OUT / "model_params.json").read_text())["clusters"]["North"]
    m = factor.build_two_level(np.full(3, lap["national_loading"]), np.full(3, lap["cluster_loading"]),
                               np.zeros(3, int), np.full(3, 1 / 50))
    p_s = m.p_wet * m.p_cluster_wet[0, 1] + (1 - m.p_wet) * m.p_cluster_wet[0, 0]
    A = q.a_operator(float(p_s), [tuple(m.p_area[i]) for i in range(2)])
    return A, float(p_s), [tuple(map(float, m.p_area[i])) for i in range(2)]


def build():
    wet, r1, r2 = QuantumRegister(1, "wet spring"), QuantumRegister(1, "river 1"), QuantumRegister(1, "river 2")
    c = ClassicalRegister(2, "out")
    qc = QuantumCircuit(wet, r1, r2, c)
    tw, t1, t2, d1, d2 = (Parameter(s) for s in ("θw", "θ1", "θ2", "φ1", "φ2"))
    # A: our flood model (same gate order as quantum.a_operator)
    qc.ry(tw, 0)
    qc.ry(t1, 1)
    qc.cry(d1, 0, 1)
    qc.ry(t2, 2)
    qc.cry(d2, 0, 2)
    qc.barrier()
    # one Grover step Q = A S0 A† S_psi
    qc.cz(1, 2)                                   # S_psi: marks "both rivers flood"
    qc.append(Gate("A†", 3, []), [0, 1, 2])
    qc.append(Gate("S₀", 3, []), [0, 1, 2])       # reflection about |000>
    qc.append(Gate("A", 3, []), [0, 1, 2])
    qc.barrier()
    qc.measure([1, 2], [0, 1])
    return qc


def main():
    A, p_s, p_area = real_angles()
    print("target instance (run_hw.py A3_kittila_ivalo_both): P(wet) =", round(p_s, 4),
          "| P(river | dry, wet) =", [tuple(round(x, 4) for x in p) for p in p_area])
    print("A operator, ops:", dict(A.count_ops()))
    qc = build()
    style = {"fontsize": 20, "subfontsize": 15, "textcolor": NAVY, "gatetextcolor": "#ffffff",
             "linecolor": NAVY, "creglinecolor": GREY, "barrierfacecolor": "#ffffff", "backgroundcolor": "#ffffff",
             "displaycolor": {"ry": (BLUE, "#ffffff"), "cry": (BLUE, "#ffffff"), "cz": (PURPLE, "#ffffff"),
                              "A†": (GREY, "#ffffff"), "S₀": (GREY, "#ffffff"), "A": (GREY, "#ffffff"),
                              "measure": (NAVY, "#ffffff")}}
    fig = qc.draw("mpl", style=style, fold=-1, scale=1.0, cregbundle=True, plot_barriers=False,
                  initial_state=False)
    ax = fig.axes[0]
    for t in list(ax.texts):
        s, (x, y) = t.get_text(), t.get_position()
        plain = s.replace("$", "").replace("{", "").replace("}", "").replace("\\;", " ")
        if plain in ("wet spring", "river 1", "river 2"):
            t.set_text(plain)
            t.set_clip_on(False)
            t.set_fontsize(19)
            t.set_fontweight("bold")
        elif s == "out":
            t.set_text("readout")
            t.set_fontsize(16)
            t.set_color(GREY)
        elif s in ("0", "1", "2") and y > -2.5:      # qubit indices inside the A† / S0 / A blocks
            t.remove()
        elif s in ("A†", "S₀", "A"):
            t.set_fontsize(14)
            t.set_fontweight("bold")
    # brackets above the circuit: what each part is (x = Qiskit's column positions: A in 1-3, CZ 4, blocks 5-7)
    top = 0.55

    def bracket(x0, x1, label, color):
        ax.plot([x0, x0, x1, x1], [top, top + 0.15, top + 0.15, top], color=color, lw=3, clip_on=False)
        ax.text((x0 + x1) / 2, top + 0.27, label, ha="center", va="bottom", fontsize=13, fontweight="bold", linespacing=1.0,
                color=color, clip_on=False)

    bracket(0.75, 3.55, "A\nflood model", BLUE)
    bracket(3.75, 7.7, "Grover step Q\n× k  (k = 0, 1, 2)", PURPLE)
    bracket(7.85, 9.6, "count:\nboth flood?", NAVY)
    ax.text(4.16, -2.42, "mark\nboth flood", ha="center", va="top", fontsize=12, color=PURPLE, linespacing=0.95)
    ax.text(6.27, -2.42, "reflect", ha="center", va="top", fontsize=12, color=GREY)
    ax.set_xlim(-2.4, ax.get_xlim()[1] + 0.1)
    ax.set_ylim(-3.45, 1.75)
    fig.savefig(OUT / "stage_qae_circuit.png", dpi=200, bbox_inches="tight", pad_inches=0.05, facecolor="white")
    plt.close(fig)
    print("wrote out/stage_qae_circuit.png")


if __name__ == "__main__":
    main()
