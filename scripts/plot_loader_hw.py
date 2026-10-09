"""Pitch chart: Finland's joint spring-flood tail sampled on a real quantum computer (14-area loader)."""
import glob
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
f = [g for g in sorted(glob.glob(str(ROOT / "out" / "runs" / "loader-iqm-emerald-*.json")))
     if abs(json.loads(Path(g).read_text()).get("level", 0) - 0.1) < 1e-9][-1]   # 1-in-10 run only
r = json.loads(Path(f).read_text())
obs = json.loads((ROOT / "out" / "joint_counts.json").read_text())
ks = list(range(2, 9))


OBS = dict(zip(obs["k"], obs["observed"]))


def observed(k):
    v = OBS.get(k)
    return v if v else None


fig, ax = plt.subplots(figsize=(10, 5.6))
ax.semilogy(ks, [r["p_at_least_k_independent"][k] for k in ks], "--", color="#cf222e", lw=2,
            label="If areas flooded independently")
ax.semilogy(ks, [r["p_at_least_k_exact"][k] for k in ks], "-", color="#1f6feb", lw=2.5, label="Tulva joint model (exact)")
ax.semilogy(ks, [r["p_at_least_k_readout_corrected"][k] for k in ks], "s", color="#8250df", ms=9,
            label=f"Sampled on IQM Emerald ({r['qubits']} qubits, {r['two_qubit_gates']} two-qubit gates)")
ov = [(k, observed(k)) for k in ks if observed(k)]
if ov:
    ax.semilogy([k for k, _ in ov], [v for _, v in ov], "o", color="#111", ms=8, label="Observed, SYKE 1961–2025")
ax.set_xlabel("k = number of the 14 river flood-risk areas over their 1-in-10 spring level")
ax.set_ylabel("Chance per spring of k or more areas")
ax.set_title("Finland's joint spring-flood risk, sampled on a real quantum computer", loc="left", fontsize=13)
ax.grid(True, which="both", alpha=0.25)
ax.legend(frameon=False, fontsize=9)
fig.text(0.01, 0.01, f"IQM Emerald via IQM Resonance, job {r['jobs'][0]}, {r['shots']:,} shots, readout-corrected. "
         f"Exact = two-level factor model fitted to SYKE spring peaks.",
         fontsize=7.5, color="#666")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(ROOT / "out" / "loader_emerald.png", dpi=130)
print("saved out/loader_emerald.png")
