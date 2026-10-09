"""Big, simple pitch charts for deck slides 2 and 3 (readable from a jury table).

Inputs: out/joint_counts.json (fit_dependence.py), out/pricing.json (price_index.py).
Outputs: out/pitch_gap.png (slide 2), out/pitch_cost.png (slide 3), out/pitch_loader.png (slide 5),
out/pitch_scaling.png (slide 6). Slides 5 and 6 redraw out/loader_emerald.png and out/qae_scaling.png from their
saved results with deck-size fonts (no new computation).
Figure sizes equal the slot sizes on the slide (inches), so font sizes are true slide points.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
NAVY, BLUE, RED, GREY, LIGHTGREY = "#0b1f3a", "#1f6feb", "#cf222e", "#6b7280", "#dde3ea"
plt.rcParams.update({"font.family": "sans-serif",
                     "font.sans-serif": ["Liberation Sans", "Arial", "Helvetica", "DejaVu Sans"], "font.size": 22,
                     "text.color": NAVY, "axes.edgecolor": LIGHTGREY})
DPI = 200


def clean(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)


def gap_chart():
    """Slide 2: P(>=4 of 14 areas over their own 1-in-10 in the same spring)."""
    j = json.loads((OUT / "joint_counts.json").read_text())
    i = j["k"].index(4)
    n_obs, n_years = j["observed_n_years"][i], j["n_years"]
    bars = [("Observed\n1961–2025", j["observed"][i], NAVY),
            ("Tulva\nmodel", j["model_same_years"][i], BLUE),
            ("If\nindependent", j["independent_same_years"][i], RED)]
    fig, ax = plt.subplots(figsize=(7.9, 5.25), dpi=DPI)
    xs = range(len(bars))
    ax.bar(xs, [b[1] for b in bars], width=0.62, color=[b[2] for b in bars])
    for x, (_, v, c) in zip(xs, bars):
        ax.text(x, v + 0.006, f"{100 * v:.1f} %", ha="center", va="bottom", fontsize=34, fontweight="bold",
                color=c)
    ax.text(0, j["observed"][i] / 2, f"{n_obs} of {n_years}\nsprings", ha="center", va="center",
            fontsize=18, color="white")
    ax.set_xticks(list(xs), [b[0] for b in bars], fontsize=22)
    ax.set_yticks([])
    ax.set_ylim(0, max(b[1] for b in bars) * 1.28)
    clean(ax)
    ax.set_title("How often do ≥4 of 14 river areas\nflood in the same spring?", loc="left", fontsize=24,
                 fontweight="bold", pad=14)
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "pitch_gap.png", dpi=DPI, facecolor="white")
    plt.close(fig)


def cost_chart():
    """Slide 3: market price per year of the North '>=2 of 5 over 1-in-50' €10M cover."""
    t = json.loads((OUT / "pricing.json").read_text())["clusters"]["North"]["triggers"]["ge2"]
    rows = [("If independent", t["independent"]["market_premium_eur"], RED),
            ("Tulva", t["tulva"]["market_premium_eur"], BLUE),
            ("After a snowy March", t["tulva_high_outlook"]["market_premium_eur"], NAVY)]

    def eur(v):
        return f"€{v / 1e6:.2f}M" if v >= 1e6 else f"€{v / 1e3:.0f}k"

    fig, ax = plt.subplots(figsize=(12.1, 2.85), dpi=DPI)
    ys = [2, 1, 0]
    xmax = max(r[1][1] for r in rows) / 1e3
    for y, (lab, (lo, hi), c) in zip(ys, rows):
        lo, hi = lo / 1e3, hi / 1e3
        w = max(hi - lo, xmax * 0.012)
        ax.barh(y, w, left=lo, height=0.55, color=c)
        ax.text(hi + xmax * 0.015, y, f"{eur(lo * 1e3)}–{eur(hi * 1e3)}", va="center", fontsize=26,
                fontweight="bold", color=c)
    ax.set_yticks(ys, [r[0] for r in rows], fontsize=24)
    ax.set_xlim(0, xmax * 1.42)
    ax.set_ylim(-0.6, 2.6)
    ax.set_xticks([0, 500, 1000, 1500, 2000], ["€0", "€0.5M", "€1M", "€1.5M", "€2M"], fontsize=18,
                  color=GREY)
    ax.grid(axis="x", color=LIGHTGREY, lw=1)
    ax.set_axisbelow(True)
    clean(ax)
    ratio = t["tulva"]["premium_eur"] / t["independent"]["premium_eur"]
    ax.text(xmax * 1.42, 2, f"≈{ratio:.0f}× too cheap", ha="right", va="center", fontsize=28,
            fontweight="bold", color=RED)
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "pitch_cost.png", dpi=DPI, facecolor="white")
    plt.close(fig)


def loader_chart():
    """Slide 5: P(>=k of 14 areas over 1-in-10), IQM Emerald 18-qubit loader vs exact vs independence."""
    r = json.loads((OUT / "runs" / "loader-iqm-emerald-20261008T184433Z.json").read_text())  # 1-in-10 run
    obs = json.loads((OUT / "joint_counts.json").read_text())
    o = dict(zip(obs["k"], obs["observed"]))
    ks = list(range(2, 9))
    fig, ax = plt.subplots(figsize=(7.6, 4.35), dpi=DPI)
    ax.semilogy(ks, [r["p_at_least_k_independent"][k] for k in ks], "--", color=RED, lw=3, label="If independent")
    ax.semilogy(ks, [r["p_at_least_k_exact"][k] for k in ks], "-", color=BLUE, lw=3.5, label="Tulva model")
    ax.semilogy(ks, [r["p_at_least_k_readout_corrected"][k] for k in ks], "s", color="#8250df", ms=13,
                label="IQM Emerald chip")
    ov = [(k, o[k]) for k in ks if o.get(k)]
    ax.semilogy([k for k, _ in ov], [v for _, v in ov], "o", color=NAVY, ms=11, label="Observed 1961–2025")
    ax.set_yticks([1e-1, 1e-2, 1e-3, 1e-4], ["10 %", "1 %", "0.1 %", "0.01 %"], fontsize=17)
    ax.set_xticks(ks, [str(k) for k in ks], fontsize=17)
    ax.minorticks_off()
    ax.set_xlabel("At least k of 14 areas flood in one spring", fontsize=17)
    ax.grid(True, which="major", color=LIGHTGREY, lw=1)
    clean(ax)
    ax.legend(frameon=False, fontsize=17, loc="lower left", handlelength=1.6, borderaxespad=0.2)
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "pitch_loader.png", dpi=DPI, facecolor="white")
    plt.close(fig)


def scaling_chart():
    """Slide 6: estimation error vs model evaluations: classical MC, ideal QAE, real hardware (Kittilä+Ivalo)."""
    d = json.loads((OUT / "qae_scaling.json").read_text())
    hw = json.loads((OUT / "qae_scaling_hardware_points.json").read_text())["hardware_points"]
    mc, ideal = d["monte_carlo"], d["curves"]["ideal"]
    fig, ax = plt.subplots(figsize=(7.6, 4.6), dpi=DPI)
    ax.loglog([p["queries"] for p in mc], [100 * p["rmse"] for p in mc], color=NAVY, lw=3.5)
    ax.loglog([p["queries"] for p in ideal], [100 * p["rmse"] for p in ideal], "o-", color=BLUE, lw=3, ms=8)
    last, qmax = ideal[-1], mc[-1]["queries"]
    xs = [last["queries"], qmax]
    ax.loglog(xs, [100 * last["rmse"] * last["queries"] / x for x in xs], ":", color=BLUE, lw=3)
    for vendor, mk, col in (("IBM", "D", "#0f62fe"), ("IQM", "P", "#00a19a")):
        pts = [p for p in hw if p["vendor"] == vendor]
        ax.loglog([p["queries"] for p in pts], [100 * p["abs_error"] for p in pts], mk, color=col, ms=16,
                  mec="black", mew=1)
    ax.text(1.2e6, 2.6e-3, "Classical\nMonte Carlo", fontsize=18, fontweight="bold", color=NAVY, ha="right",
            va="top")
    ax.text(5.5e2, 1.3e-3, "Ideal quantum\n(needs fault tolerance)", fontsize=18, fontweight="bold", color=BLUE,
            va="top")
    ax.text(1.2e6, 0.1, "IBM & IQM chips today", fontsize=18, fontweight="bold", color="#0f62fe", ha="right")
    ax.set_xticks([1e3, 1e4, 1e5, 1e6], ["1k", "10k", "100k", "1M"], fontsize=17)
    ax.set_yticks([1e-1, 1e-2, 1e-3, 1e-4], ["0.1", "0.01", "0.001", "0.0001"], fontsize=17)
    ax.minorticks_off()
    ax.set_xlabel("Model evaluations", fontsize=17)
    ax.set_ylabel("Error (percentage points)", fontsize=17)
    ax.grid(True, which="major", color=LIGHTGREY, lw=1)
    clean(ax)
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "pitch_scaling.png", dpi=DPI, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    gap_chart()
    cost_chart()
    loader_chart()
    scaling_chart()
    print("wrote out/pitch_gap.png, out/pitch_cost.png, out/pitch_loader.png, out/pitch_scaling.png")
