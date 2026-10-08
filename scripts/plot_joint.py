"""Pitch chart: how often k or more of Finland's 14 river flood-risk areas flood in the same spring.

Input: out/joint_counts.json (from fit_dependence.py). Output: out/joint_floods.png
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.ticker import FixedLocator, NullLocator  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
J = json.loads((ROOT / "out" / "joint_counts.json").read_text())

INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0"
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#9a9893"

K = np.array(J["k"])
sel = (K >= 2) & (K <= 10)
k = K[sel]
obs = np.array(J["observed"])[sel]
mod = np.array(J["model_same_years"])[sel]
ind = np.array(J["independent_same_years"])[sel]
nobs = np.array(J["observed_n_years"])[sel]
ny = J["n_years"]

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12})
fig, ax = plt.subplots(figsize=(10, 6.2), dpi=200)
fig.patch.set_facecolor("white")

ax.plot(k, np.full(len(k), 0.1), color=GRAY, lw=2, ls=(0, (6, 4)), zorder=2)
ax.plot(k, ind, color=ORANGE, lw=2.4, zorder=3)
ax.plot(k, mod, color=BLUE, lw=2.4, zorder=4)
m = obs > 0
ax.scatter(k[m], obs[m], s=90, color=INK, edgecolor="white", linewidth=2, zorder=5)
ax.scatter(k[~m], np.full((~m).sum(), 1.6e-3), marker="v", s=40, color=MUTED, zorder=5)

ax.set_yscale("log")
ax.set_ylim(1.2e-3, 0.75)
ax.set_xlim(1.6, 10.4)
ticks = [0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002]
ax.yaxis.set_major_locator(FixedLocator(ticks))
ax.yaxis.set_minor_locator(NullLocator())
ax.set_yticklabels([f"1 in {round(1 / t)} yrs" if t < 0.5 else "1 in 2 yrs" for t in ticks])
ax.set_xticks(k)
ax.set_xticklabels([f"{x}+" for x in k])
ax.set_xlabel("Number of the 14 river flood-risk areas over their own 1-in-10 flood in the same spring",
              color=INK2, fontsize=11.5)
ax.grid(axis="y", color=GRID, lw=1)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(MUTED)
ax.tick_params(colors=INK2, length=0)

# direct labels
def lab(x, y, text, color, dy=0, ha="left"):
    ax.annotate(text, (x, y), xytext=(8, dy), textcoords="offset points", color=color, fontsize=12,
                fontweight="bold", va="center", ha=ha)

lab(k[-1] - 0.05, 0.1, "All 14 at once (SYKE summed figures)", INK2, dy=12, ha="right")
i4 = list(k).index(4)
ax.annotate(f"Independence (EIOPA 0%):\n4+ areas {ind[i4]*100:.1f}% a year", (3.92, ind[i4]), xytext=(-6, -22),
            textcoords="offset points", color=ORANGE, fontsize=12, fontweight="bold", va="center", ha="right")
j = list(k).index(6)
lab(6.1, mod[j], f"Tulva fitted model", BLUE, dy=12)
ax.annotate(f"4+ areas observed in {nobs[i4]} of {ny} years ({obs[i4]*100:.0f}%)\nTulva model: {mod[i4]*100:.1f}%",
            (4, obs[i4]), xytext=(4.6, 0.33), color=INK, fontsize=12, fontweight="bold",
            arrowprops=dict(arrowstyle="-", color=INK2, lw=1))
ax.scatter([], [], s=70, color=INK, label=f"Observed, {1961}–{1960 + ny}")
ax.plot([], [], color=BLUE, lw=2.4, label="Tulva joint model (fitted)")
ax.plot([], [], color=ORANGE, lw=2.4, label="Independence (EIOPA 0%)")
ax.plot([], [], color=GRAY, lw=2, ls=(0, (6, 4)), label="All at once (SYKE sum)")
ax.legend(loc="lower left", frameon=False, fontsize=10.5, labelcolor=INK2)

fig.text(0.015, 0.965, "Finnish river floods come together", fontsize=19, fontweight="bold", color=INK)
fig.text(0.015, 0.915, "How often k or more risk areas have a 1-in-10 spring flood in the same year",
         fontsize=12.5, color=INK2)
fig.text(0.015, 0.018, "Data: SYKE Hydrologiarajapinta (daily discharge, CC BY 4.0) and SMHI (Torne). "
         "Spring (Mar–Jun) peak flow, one gauge per area, 1961–2025.\nModel: Gaussian-copula factor model "
         "(national + 3 regional factors), exact quadrature on the same gauge-years as observed. "
         "▼ = not observed.", fontsize=8.5, color=MUTED)
fig.subplots_adjust(left=0.13, right=0.98, top=0.87, bottom=0.17)
fig.savefig(ROOT / "out" / "joint_floods.png", facecolor="white")
print("wrote out/joint_floods.png")
