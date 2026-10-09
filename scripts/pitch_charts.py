"""Big, simple pitch charts for deck slides 2 and 3 (readable from a jury table).

Inputs: out/joint_counts.json (fit_dependence.py), out/pricing.json (price_index.py).
Outputs: out/pitch_gap.png (slide 2), out/pitch_cost.png (slide 3), out/pitch_snow.png (slide 5; pitch_loader.png is no
longer on a slide),
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
PURPLE = "#8250df"  # IQM chip, as on the loader chart
plt.rcParams.update({"font.family": "sans-serif",
                     "font.sans-serif": ["Liberation Sans", "Arial", "Helvetica", "DejaVu Sans"], "font.size": 22,
                     "text.color": NAVY, "axes.edgecolor": LIGHTGREY})
DPI = 200


def clean(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)


def gap_chart():
    """Slide 2: P(>=4 of 14 areas over their own 1-in-10 in the same spring), observed vs chance (independence on the
    same gauge-years as observed; 35 gauge-years are missing). Wilson 90 % interval from scripts/round3_numbers.py."""
    j = json.loads((OUT / "joint_counts.json").read_text())
    r3 = json.loads((OUT / "round3_numbers.json").read_text())["ge4_of14_1in10"]
    i = j["k"].index(4)
    n_obs, n_years = j["observed_n_years"][i], j["n_years"]
    obs, ind = j["observed"][i], j["independent_same_years"][i]
    lo, hi = r3["wilson90"]
    fig, ax = plt.subplots(figsize=(12.1, 4.35), dpi=DPI)
    xs = [0, 2]
    ax.bar(xs, [obs, ind], width=0.9, color=[NAVY, RED])
    for x, v, c in zip(xs, [obs, ind], [NAVY, RED]):
        ax.text(x, v + 0.005, f"{100 * v:.1f} %", ha="center", va="bottom", fontsize=40, fontweight="bold", color=c)
    ax.text(0, obs / 2, f"{n_obs} of {n_years}\nsprings\n(90 %: {100 * lo:.0f}–{100 * hi:.0f} %)", ha="center",
            va="center", fontsize=21, color="white")
    ax.text(1.0, obs * 0.62, f"{obs / ind:.1f}×", ha="center", va="center", fontsize=72, fontweight="bold",
            color=RED)
    ax.text(1.0, obs * 0.36, "as often\nas chance", ha="center", va="center", fontsize=22, color=GREY)
    ax.set_xticks(xs, ["Observed 1961–2025", "By chance (no co-flooding)"], fontsize=24)
    ax.set_xlim(-0.8, 2.8)
    ax.set_yticks([])
    ax.set_ylim(0, obs * 1.3)
    clean(ax)
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "pitch_gap.png", dpi=DPI, facecolor="white")
    plt.close(fig)


# North ">=2 of 5 over 1-in-50" under one equicorrelation of 0.27 (~ mean of the regulator's 19-zone matrix inside
# Finland): one-factor quadrature, scripts/round3_numbers.py (MC 2M agrees).
P_REG_027 = json.loads((OUT / "round3_numbers.json").read_text())["north_ge2_of5_1in50"]["equicorr_0.27_exact_quadrature"]


def cost_chart():
    """Slide 3: ONE measure only, the fair expected loss of the North '>=2 of 5 over 1-in-50' cover as % of the
    limit per year: one 0.27 correlation (mean of the 2027 Finnish flood-zone matrix), Tulva, and Tulva after a
    snowy (top-15 %) March. Whiskers = joint year-bootstrap 90 % intervals (scripts/round4_numbers.py)."""
    d = json.loads((OUT / "pricing.json").read_text())
    t = d["clusters"]["North"]["triggers"]["ge2"]
    b = json.loads((OUT / "round4_numbers.json").read_text())["north_ge2_of5_bootstrap"]
    rows = [("0.27 average correlation", P_REG_027, None, GREY),
            ("Tulva, priced in autumn", t["tulva"]["p_exact"], b["p_tulva_ci90"], BLUE),
            ("Tulva after a snowy March", t["tulva_high_outlook"]["p_exact"], b["p_high_snow_ci90"], NAVY)]
    fig, ax = plt.subplots(figsize=(12.1, 2.0), dpi=DPI)
    ys = [2, 1, 0]
    xmax = 100 * max(r[2][1] if r[2] else r[1] for r in rows)
    for y, (lab, v, ci, c) in zip(ys, rows):
        ax.barh(y, 100 * v, height=0.62, color=c)
        right = 100 * v
        if ci:
            ax.errorbar(100 * v, y, xerr=[[100 * (v - ci[0])], [100 * (ci[1] - v)]], color=RED if c == NAVY else NAVY,
                        lw=2.5, capsize=6, capthick=2.5)
            right = 100 * ci[1]
        txt = f"{100 * v:.2f} %" if v < 0.03 else f"{100 * v:.1f} %"
        if ci:
            txt += f"  ({100 * ci[0]:.1f}–{100 * ci[1]:.1f})"
        ax.text(right + xmax * 0.015, y, txt, va="center", fontsize=22, fontweight="bold", color=c)
    ax.set_yticks(ys, [r[0] for r in rows], fontsize=19)
    ax.set_xlim(0, xmax * 1.45)
    ax.set_ylim(-0.55, 2.55)
    ax.set_xticks([0, 2, 4, 6, 8], ["0 %", "2 %", "4 %", "6 %", "8 %"], fontsize=17, color=GREY)
    ax.grid(axis="x", color=LIGHTGREY, lw=1)
    ax.set_axisbelow(True)
    clean(ax)
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


def snow_chart():
    """Slide 5: snow signal on IQM Emerald, a two-river North-cluster pair both over 1-in-50, low / normal / high March snow:
    exact vs calibrated chip estimate with bootstrap 90 % intervals (scripts/bootstrap_ci.py)."""
    b = json.loads((OUT / "bootstrap_ci.json").read_text())
    rows = [("Low snow", b["emerald snow low"]), ("Normal", b["emerald snow normal"]),
            ("Snowy", b["emerald snow high"])]
    r = b["snow_ratio_high_over_low"]
    fig, ax = plt.subplots(figsize=(7.6, 4.6), dpi=DPI)
    w = 0.36
    for i, (lab, d) in enumerate(rows):
        e, c, lo, hi = (100 * d["exact"], 100 * d["estimate"], 100 * d["ci90"][0], 100 * d["ci90"][1])
        ax.bar(i - w / 2 - 0.02, e, w, color=BLUE)
        ax.bar(i + w / 2 + 0.02, c, w, color=PURPLE)
        ax.errorbar(i + w / 2 + 0.02, c, yerr=[[c - lo], [hi - c]], color=NAVY, lw=2.5, capsize=7, capthick=2.5)
        ax.text(i - w / 2 - 0.02, e + 0.006, f"{e:.3f}", ha="center", va="bottom", fontsize=15, color=NAVY)
        ax.text(i + w / 2 + 0.02, hi + 0.006, f"{c:.3f}", ha="center", va="bottom", fontsize=15, color=NAVY)
    ax.set_xticks(range(3), [x[0] for x in rows], fontsize=20)
    ax.set_yticks([0, 0.1, 0.2], ["0", "0.1 %", "0.2 %"], fontsize=16, color=GREY)
    ax.set_ylim(0, 0.36)
    ax.grid(axis="y", color=LIGHTGREY, lw=1)
    ax.set_axisbelow(True)
    clean(ax)
    # the slide title carries the headline ratio (snowy vs LOW snow); the chart adds snowy vs NORMAL so both baselines are named
    hi, no = b["emerald snow high"], b["emerald snow normal"]
    ax.text(-0.45, 0.345, f"Snowy vs normal: {hi['estimate'] / no['estimate']:.2f}× chip, "
            f"{hi['exact'] / no['exact']:.2f}× exact", fontsize=21, fontweight="bold", color=NAVY, va="top")
    ax.text(-0.45, 0.300, "% chance both rivers pass 1-in-50", fontsize=17, color=GREY, va="top")
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=BLUE, label="Exact"), Patch(color=PURPLE, label="IQM Emerald (90 % CI)")],
              frameon=False, fontsize=16, loc="upper left", bbox_to_anchor=(0.0, 0.8))
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "pitch_snow.png", dpi=DPI, facecolor="white")
    plt.close(fig)


def scaling_chart():
    """Slide 6: estimation error vs model evaluations: classical MC, ideal QAE, real hardware (two-river North-cluster pair)."""
    d = json.loads((OUT / "qae_scaling.json").read_text())
    hw = json.loads((OUT / "qae_scaling_hardware_points.json").read_text())["hardware_points"]
    mc, ideal = d["monte_carlo"], d["curves"]["ideal"]
    fig, ax = plt.subplots(figsize=(7.6, 4.6), dpi=DPI)
    ax.loglog([p["queries"] for p in mc], [100 * p["rmse"] for p in mc], color=NAVY, lw=3.5)
    ax.loglog([p["queries"] for p in ideal], [100 * p["rmse"] for p in ideal], "o-", color=BLUE, lw=3, ms=8)
    last, qmax = ideal[-1], mc[-1]["queries"]
    xs = [last["queries"], qmax]
    ax.loglog(xs, [100 * last["rmse"] * last["queries"] / x for x in xs], ":", color=BLUE, lw=3)
    # VTT Q50: the three repeats of the same circuit, read from their saved analyses (no new computation)
    for f in sorted((OUT / "runs").glob("q50-20261009T14*.analysis.json")):
        a = json.loads(f.read_text())["A3_kittila_ivalo_both"]
        hw.append({"vendor": "VTT", "queries": a["oracle_queries"], "abs_error": abs(a["noise_aware_mlae"] - a["exact"])})
    for vendor, mk, col in (("IBM", "D", "#0f62fe"), ("IQM", "P", "#00a19a"), ("VTT", "^", "#d4731c")):
        pts = [p for p in hw if p["vendor"] == vendor]
        ax.loglog([p["queries"] for p in pts], [100 * p["abs_error"] for p in pts], mk, color=col, ms=16,
                  mec="black", mew=1)
    q = [p for p in hw if p["vendor"] == "VTT"]
    ax.text(q[0]["queries"] / 1.5, 100 * max(p["abs_error"] for p in q), "VTT Q50,\n3 repeats", fontsize=15,
            color="#d4731c", fontweight="bold", va="center", ha="right")
    ax.text(1.2e6, 2.6e-3, "Classical\nMonte Carlo", fontsize=20, fontweight="bold", color=NAVY, ha="right",
            va="top")
    ax.text(5.5e2, 1.3e-3, "Ideal quantum\n(needs fault tolerance)", fontsize=20, fontweight="bold", color=BLUE,
            va="top")
    ax.text(1.2e6, 0.2, "IBM, IQM & VTT\nchips today", fontsize=20, fontweight="bold", color="#0f62fe", ha="right",
            va="bottom")
    ax.set_xticks([1e3, 1e4, 1e5, 1e6], ["1k", "10k", "100k", "1M"], fontsize=21)
    ax.set_yticks([1, 1e-1, 1e-2, 1e-3, 1e-4], ["1", "0.1", "0.01", "0.001", "0.0001"], fontsize=21)
    ax.set_ylim(7e-5, 1.0)
    ax.minorticks_off()
    ax.set_xlabel("Model evaluations", fontsize=21)
    ax.set_ylabel("Error (percentage points)", fontsize=21)
    ax.grid(True, which="major", color=LIGHTGREY, lw=1)
    clean(ax)
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "pitch_scaling.png", dpi=DPI, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    gap_chart()
    cost_chart()
    loader_chart()
    snow_chart()
    scaling_chart()
    print("wrote out/pitch_gap.png, out/pitch_cost.png, out/pitch_loader.png, out/pitch_snow.png, out/pitch_scaling.png")
