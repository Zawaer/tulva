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
