# Decisions

Append one line per decision: date time · who · decision · why.

- 2026-10-08 18:15 · team · Product: parametric spring-flood index cover for Finnish insurers, priced on joint
  flood risk conditioned on the March snowpack. · Fits the brief (early warning + risk), and nobody else does insurance.
- 2026-10-08 18:15 · team · Quantum method: amplitude estimation of the joint-trigger probability (not QAOA). ·
  Pricing = expected payout = estimation problem.
- 2026-10-08 18:15 · team · Hardware: Aalto Q20 via LUMI (Q50 is down), IBM as cross-check.
- 2026-10-08 18:15 · team · Scope: the 14 river flood-risk areas (MMM 2024), spring floods; coast out of scope.
- 2026-10-08 19:00 · Toivo · Quantum instances: A3 = Kittilä+Ivalo "both pass 1-in-50" (3 qubits, 4/27/50/73 CZ for
  k=0..3 on a grid), A4 = Lapland "≥2 of 3" (4 qubits, CZ-triangle marker). Two-level factor model
  (hydrology wet = top 30 %) is the circuit's model; continuous model is the classical reference.
- 2026-10-08 19:40 · Toivo (data) · Gauges: one per flood-risk area, Mar–Jun daily-discharge peak 1961–2025. Lapväärtinjoki Perus (SYKE 1197+1198), Kyrönjoki Hanhikoski (1213) for Ilmajoki–Seinäjoki, Laihianjoki Karkkimala (1204), Kyrönjoki Skatila (1214), Kalajoki Niskakoski/Hihnalankoski (1253+1254), Pyhäjoki (1262+1261), Iijoki Kurenalus (1332+1334+1333), Ivalojoki Pajakoski (1419), Ounasjoki Köngäs (1374) for Kittilä, Ounasjoki Marraskoski (1377+1378) for Rovaniemi (Kemijoki is hydro-regulated), Torne Kukkolankoski from SMHI 16722 (same series as SYKE 1406), Kokemäenjoki Harjavalta (1188) for Pori, Loimijoki Maurialankoski (1185+1184) for Huittinen, Kymijoki Anjala (1058). Renumbered stations spliced (newest id wins; Kalajoki overlap ratio 1.00). · Longest unregulated-ish record per area.
- 2026-10-08 19:40 · Toivo (data) · Model clusters = the 3 product clusters (Ostrobothnia 6: Lapväärtti, Ilmajoki, Laihia, Ylistaro, Alavieska, Pyhäjoki; North 5: Pudasjärvi, Ivalo, Kittilä, Rovaniemi, Tornio; Satakunta–SE 3: Pori, Huittinen, Kymijoki), one common national loading. · Matches the product and the quantum instances. Data-driven average linkage gives 4 groups (Lapland 4 / Pori+Kymi / S-Ostrobothnia+Huittinen / Kalajoki+Pyhäjoki+Iijoki, RMSE 0.18 vs 0.21); stored as alt in out/model_params.json. Exceedance = empirical top 10% per gauge so marginals match the copula.
- 2026-10-08 19:40 · Toivo (data) · out/model_params.json schema: clusters[name] = {national_loading, cluster_loading, within_corr, areas}; gauges[] with q10/q50 (GEV L-moments, m³/s) and z10/z50 thresholds. Snow predictor = SYKE LumiAlue SWE on 1 March (catchments 131,147,188,236,216,230,112,109,55).
- 2026-10-08 21:30 · Toivo (pricing) · Tulva Index pricing: premium = P(trigger) × payout × (1 + 0.35), payout €10M per spring, both parameters (src/tulva/pricing.py). Snow outlook conditions exactly on O_c = s·D_c + √(1−s²)·u in its top/bottom 15 % (s = cluster skill from out/snow_skill.json), not a mean shift of the national factor as in qae_sim.py. · The cluster trigger depends only on the cluster driver D_c; the exact conditional is cheap and avoids mixing skills across clusters.
- 2026-10-08 21:30 · Toivo (pricing) · Back-test trigger = ≥2 of cluster over fitted GEV 1-in-10 (q10_m3s), flag = top-15 % 1 March SWE index of the cluster. Robustness = Student-t copula (df 10, 5) with the same factor correlations and a 200-sample year-bootstrap refit of loadings. · 1-in-50 has ~1 event per cluster in 65 years.
- 2026-10-08 · Vaishnav · Hardware: run the QAE circuits on IQM via IQM Resonance (https://resonance.iqm.tech/). · run_hw.py
  currently connects through LUMI (Q20_CORTEX_URL); Resonance needs an API token and its own device URL, so Toivo to adapt.
- 2026-10-08 19:00 · team · Hardware: IQM Resonance primary (effectively unlimited credits via Niklas Steinmann),
  IBM as the cross-check on a second architecture; Aalto Q20 optional. Same circuits and analysis on all.
- 2026-10-08 22:10 · Toivo · IBM runs use --copies 20–30 (side-by-side copies of the 3–4-qubit circuits on
  disjoint qubits): N× shots per job for the 10-min budget, plus per-copy spread across the chip.
- 2026-10-08 22:10 · Toivo · VTT Q50 is back (CSC Slack): unlimited priority via LUMI. Added --backend q50. IQM-type
  hardware = Q50 (if LUMI access works) and/or IQM Resonance.
- 2026-10-08 · Vaishnav · Business research done; corrections for CLAIMS/web (EIOPA 0 % wording, 18 = 14 river + 4
  coastal areas, risk load vs 2.5–3.5× market, no confirmed 2024 Lapland damage) in business/NOTES_FOR_TOIVO.md. ·
  Mentor: focus on business case + why quantum; Finland-only scope is good. Larger circuits than 3–4 qubits are OK.
- 2026-10-09 · Toivo · Baseline relabelled "independence (no co-flooding)" everywhere (charts, web, CLAIMS); "all at
  once" is "if every area flooded at once (an upper bound)", not attributed to SYKE. EIOPA is cited precisely: 0 % flood
  correlation FI↔SE/NO/DK from 30 Jan 2027 (Del. Reg. 2026/269), 25 % snowmelt option rejected, 19-zone matrix inside
  Finland (mean ≈ 0.27). · Vaishnav's research: "EIOPA 0 %" overstated what the regulator assumes.
- 2026-10-09 · Toivo (pricing) · price_index.py also outputs a market price = expected payout × 2.5 and × 3.5 next to
  the 1.35× technical price, and a staged variant (50 % at ≥2 gauges, 100 % at ≥3) per cluster and scenario
  (out/pricing.json `market_premium_eur`, `staged_ge2_half_ge3_full`). Web app and index_price.png lead with North. ·
  Market multiples from cat-bond/flood-ILS sources; staged payout reduces basis risk; Lapland risk stable to ~2050.
- 2026-10-10 · Toivo (round-3 review) · One calibrated hardware estimator everywhere: the pooled noise-aware MLAE (the
  bootstrap_ci.py estimator; IBM 0.149 %, Garnet 0.164 %), not the per-copy fit, in deck, app, QA and HARDWARE_RESULTS.
  One fair price everywhere: exact quadrature (North ≥2 of 5: 1.96 %, snowy March 6.4 %; equicorrelation 0.27: 1.11 %,
  scripts/round3_numbers.py). Slide 2 chance baseline = same gauge-years (3.9 %), all-14 binomial (4.4 %) explained in
  QA. Deck gets an appendix slide 9 for hardware details. · Hardware juror flagged the inconsistencies.
- 2026-10-10 · Toivo (round-4 review) · The 3-qubit "Kittilä + Ivalo" circuit (A3_*) gives both areas the same
  North-cluster loadings and trigger (np.full in run_hw.py instance() / run_product_hw.py), so deck, script, app, video,
  CLAIMS and QA now call it "a two-river North-cluster pair" (the "≥2 of 3 Lapland" A4 circuit likewise "3 North-cluster
  rivers"). Code instance names stay unchanged (run files depend on them). Slide 3 shows one measure only (expected loss,
  % of the limit a year) with year-bootstrap 90 % intervals (scripts/round4_numbers.py); market-price bars, €/€1M and
  ORSA move to QA. Shown hardware results are k = 0–2 (IBM run 1 with k = 3 is not on the slides). · Business and
  quantum jurors flagged the category error and the overclaim.
- 2026-10-09 · Toivo · VTT Q50 is presented as a fourth chip we ran on, never as a headline success: every repeat is
  shown (0.11–0.53 % vs exact 0.125 %, "calibration not yet stable"), its 14-river loader (31 % vs 10.9 %) is evidence
  of where hardware stops, and the failed 4-copy job is mentioned only as a failed attempt. · Honesty for the VTT juror.
- 2026-10-10 · Toivo · Round 5, deck frozen after this pass. Every snow ratio names its baseline: slide 3 "triples" =
  snowy March vs autumn (5-river cover, 3.3×); slide 5 / video / §5 = snowy vs LOW snow (two-river pair, 3.05× chip,
  2.75× exact); snowy vs normal on the pair is 1.51× / 1.55× (chart, QA). "Fair price" → "expected loss" (model
  comparison). The product pays the full limit at ≥2; staged payout is only a variant. Slide 7 money flows both start
  at the insurer (licence ← Tulva, premium → reinsurer); buyers listed OP first; If named only for the internal model.
  Basis-risk line counts payouts without a recorded loss too. One amplification statement everywhere (round5_numbers).
  · Round-5 business, quantum and coach reviews.
- 2026-10-10 · Toivo · Snow warning tested out of sample (scripts/oos_snow_test.py, both splits): ranking holds, "triples" untestable on 2001–25 (flag fired twice), North unstable; deck untouched, "triples" stays labelled in-sample; QA answer added. · Honesty check.
- 2026-10-10 · Toivo · Round 6 deck: new stage slide 5 "Our circuit: quantum amplitude estimation" (Qiskit drawing of the hardware circuit + one why-quantum line); old 5–8 → 6–9, backups → 10–12. Slide 3 bar "0.27-correlation model" → "Standard assumption (regulator's average link)"; slide 6 retitled "On real chips, the snow effect still shows". Live script re-trimmed to 240 words. · Mentor feedback + mentors' "why quantum?".
