# Business research: what affects data/model/quantum/web (for Toivo and his agents)

From the business research on 8 Oct 2026 (`business/reports/Tulva flood cover business case.md`, notes in
`business/research_notes/`). These are suggestions for Toivo's files; Vaishnav has not edited them.

## Corrections to current framing
1. **"EIOPA: 0 % Nordic flood correlation" is imprecise.** Today Finland has *no* standard-formula flood parameter
   at all (Del. Reg. 2015/35 Annex VII; exempt via Annex XIII). From 30 Jan 2027 (Del. Reg. (EU) 2026/269) Finland
   gets a flood factor of 0.04 % and **0 % flood correlation with SE/NO/DK**; EIOPA considered 25 % for snowmelt
   floods and rejected it (EIOPA-BoS-24/462 §4.70). *Inside* Finland a 19-zone matrix applies (mean ≈ 0.27, many
   pairs 0.75–1.00). Suggest relabelling the baseline "independence" rather than "EIOPA 0 %" in CLAIMS.md / web app.
2. **18 significant flood-risk areas (14 river + 4 coastal)**, MMM 19.12.2024. Our 14 = the river ones; worth checking
   our list against the ministry annex (Tornio, Huittinen, Lower Kymijoki).
3. **"2024 Lapland flood"** not confirmed as damaging in external sources; use 2005 (Ivalo/Kittilä) as the damaging example.
4. **"SYKE totals assume everything floods at once"** was not verified by the research.

## Suggested code changes (Toivo's call)
- **Risk load:** 35 % (1.35× expected loss) is low vs market. Cat bonds: 3.71× (2024), 3.0× (2025), ~2.4–2.5× (2026)
  expected loss (AM Best); flood deals ~3.0–3.4× (Flood Re Vision 2039, FloodSmart Re). Suggest `price_index.py`
  also output a "market price" at 2.5× and 3.5× so the deck number is a code output.
- **Staged payout** (50 % at ≥2 gauges, 100 % at ≥3) reduces basis risk; cheap to price with the existing code.
- **Sales timing:** adverse selection if buyers wait for March snow; product should be bought before winter or priced on the outlook (already done).
- **Climate:** SYKE/FMI 30/2026 and Veijalainen 2010: spring floods shrink and come earlier, fastest in Ostrobothnia;
  Lapland roughly stable to ~2050; Pori/Kymijoki risk shifts to winter/frazil. Lead the demo with the North cluster.

## Quantum
- Hardware: IQM (Resonance and/or Q20 via LUMI) + IBM. Vaishnav says we can use larger circuits than 3–4 qubits
  (noise is still the limit, not qubit count).
- IQM contact recommended **Qrisp** (Eclipse Qrisp, Fraunhofer FOKUS): has Iterative QAE and Monte Carlo integration;
  IQM ships `iqm.qrisp_iqm` backend. No published QAE-on-IQM-via-Qrisp example found, so doing one would be new.
- Closest prior art: Kirke, arXiv:2603.15664 (QAE for cat-insurance tail risk, simulator only); Adam 2022 (AXA/Fraunhofer, insurance QAE on hardware).
- Resource threshold for advantage in pricing: Chakrabarti et al., Quantum 2021: ~8k logical qubits, T-depth ~54M.
- Classical timing on Vaishnav's laptop: Monte Carlo of the North factor model, 1M springs × 14 areas ≈ 0.45 s;
  96k samples × 2 areas ≈ 11 ms. Never claim speed advantage.

## Vaishnav's IQM Emerald runs (9 Oct morning)
New script `scripts/run_product_hw.py` (did not touch run_hw.py): the product trigger "≥2 of 5 North" (6 qubits,
≥2-of-5 marker as a DiagonalGate) and the 3-qubit Kittilä+Ivalo instance under low / normal / high March snow
(same circuit shape, only angles change). Same twin/zero calibration roles, so `analyse_run.py` works on it.
Results logged in CLAIMS.md (section "IQM Emerald runs, 9 Oct"). Also ran `run_loader_hw.py --level 0.02` on emerald:
at 1-in-50 the loader is swamped by noise (16 % vs 4.8 % exact for ≥2) — a clear "rare events need error correction"
data point. Not yet in out/HARDWARE_RESULTS.md / charts; your call whether to add them.
IQM venv on Windows: `.venv-iqm` (added to .gitignore).
