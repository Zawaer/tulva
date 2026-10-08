# Claims

Every number in the deck: value · what produced it (exact / monte-carlo / qae-sim / qae-q20 / qae-ibm / source)
· script and commit.

## Numbers

### Joint flood data (spring Mar–Jun peaks, 14 areas, 1961–2025) · commit 60bebb0
- Areas over own 1-in-10 together, pairs within a cluster: **2.8×** independence (Ostrobothnia 3.2×, North 2.9×, Satakunta–SE 1.3×); between clusters **1.4×** · exact (counts) · scripts/fit_dependence.py → out/dependence.json
- Mean Spearman of spring peaks: **0.55 within cluster, 0.19 between** · exact · scripts/fit_dependence.py
- **≥4 of 14 areas over 1-in-10 in the same year: 10 of 65 years (15%)**; fitted model **12.2%**; independence (no co-flooding) **3.9%** (same gauge-years) · observed exact; model exact (quadrature), MC 200k agrees (full-14: 13.1% vs 13.0%) · scripts/fit_dependence.py → out/joint_counts.json
- ≥5 areas: observed 5 of 65 years (7.7%), model 7.4%, independence 0.8% · same
- Years with ≥4 areas: 1966, 1971, 1977, 1981, 1984, 1988, 2000, 2005, 2018, 2024; max 6 areas (1966) · exact
- Factor loadings (3 product clusters, one national loading): national **0.44** (90% bootstrap 0.31–0.54); cluster Ostrobothnia **0.64**, North **0.60**, Satakunta–SE **0.46** · least-squares fit + 400 year-bootstraps · out/model_params.json
- 1-in-50 level, all 14 areas, model vs independence: P(≥2) 6.0% vs 3.1%; **P(≥3) 2.5% vs 0.25% (10×)**; P(≥4) 1.1% vs 0.014% · exact (quadrature), model extrapolation · out/joint_counts.json
- Product trigger "≥2 gauges in cluster over 1-in-50": Ostrobothnia 2.6% vs 0.57% indep; North 2.0% vs 0.38%; Satakunta–SE 0.62% vs 0.12% · exact · out/model_params.json
- 1 March snow (SYKE areal SWE) vs cluster spring flood index, Spearman: Ostrobothnia **0.69**, North **0.39**, Satakunta–SE 0.53 · exact · out/snow_skill.json
- P(≥2 cluster areas over 1-in-10) in top-15% snow years vs other years: Ostrobothnia **60% vs 11%**, North **40% vs 7%**, Satakunta–SE 30% vs 0% (10 top years each) · exact (counts, in-sample) · out/snow_skill.json
- Outlook skill (corr of March SWE with the cluster's latent factor): Ostrobothnia 0.74, North 0.47, Satakunta–SE 0.68 · derived · out/snow_skill.json

### Tulva Index pricing (€10M per triggered spring, premium = expected payout × 1.35) · scripts/price_index.py → out/pricing.json, out/index_price.png
- **"≥2 of 6 Ostrobothnia gauges over 1-in-50": P = 2.56 % → premium €346k; independence (no co-flooding) 0.57 % → €77k (Tulva 4.5× the independence price)** · exact (quadrature); MC 1M springs 2.61 % ± 0.016 pp
- **North "≥2 of 5": 1.96 % → €265k vs €52k independent (5.1×)**; Satakunta–SE "≥2 of 3": 0.62 % → €83k vs €16k (5.2×) · exact; MC 1M agrees (1.96 %, 0.62 %)
- "≥3 of cluster": Ostrobothnia €143k vs €2k (69×), North €89k vs €1k (85×), Satakunta–SE €8.3k vs €0.1k (77×) · exact; MC 1M agrees
- "≥1 of cluster": independence over-prices: Ostrobothnia €1.04M vs €1.54M (0.67×), North €961k vs €1.30M (0.74×), Satakunta–SE €718k vs €794k (0.90×). Correlation concentrates floods in fewer springs, so "any gauge" triggers less often · exact
- Full correlation (if every area flooded at once, an upper bound): every trigger = 2 % → €270k, the same for m = 1, 2, 3 · exact
- After a **high-snow March outlook (top 15 %)**: Ostrobothnia "≥2" **€1.74M** (5.0× climatology), North €870k (3.3×), Satakunta–SE €390k (4.7×); after a **low-snow outlook (bottom 15 %)**: €0.8k, €22k, €0.9k · exact conditional on the outlook (in-sample skill 0.74 / 0.47 / 0.68); MC 1M agrees
- Robustness, Student-t copula with the same correlations, "≥2": price ×1.06 (df 10) / ×1.09 (df 5) Ostrobothnia, ×1.10 / ×1.18 North, ×1.33 / ×1.62 Satakunta–SE; "≥3": ×1.21–1.94 (df 10), ×1.38–3.00 (df 5). Gaussian Tulva price is a lower bound if tails are heavier · exact (2-D quadrature) + MC 1M
- Loading uncertainty (200 year-bootstrap refits), "≥2" premium 90 % interval: Ostrobothnia **€312k–€368k** (×4.1–4.8 independence), North €220k–€291k (×4.2–5.6), Satakunta–SE €55k–€118k (×3.4–7.4) · bootstrap + exact
- **Market price (expected payout × 2.5 to × 3.5, cat-bond / flood-ILS multiples), "≥2": North €491k–€687k (technical
  ×1.35: €265k), Ostrobothnia €641k–€897k (€346k), Satakunta–SE €155k–€216k (€83k)**; under independence €96k–€134k /
  €142k–€199k / €30k–€41k; after a high-snow March €1.61M–€2.26M / €3.22M–€4.51M / €722k–€1.01M · exact × multiple ·
  scripts/price_index.py → out/pricing.json (`market_premium_eur`). Multiples are outside sources (AM Best cat bonds
  2.4–3.7× 2024–26; flood ILS ~3.0–3.4×), not our model
- **Staged payout (50 % of €10M at ≥2 gauges, 100 % at ≥3), technical (market 2.5–3.5×):** North: independence €26k
  (€49k–€69k), Tulva **€177k (€328k–€459k)**, high-snow €604k (€1.12M–€1.56M), low-snow €13k (€25k–€34k); Ostrobothnia:
  €39k (€73k–€102k), €245k (€453k–€634k), €1.27M (€2.36M–€3.30M), €0.4k (€0.8k–€1.1k); Satakunta–SE: €8k (€15k–€21k),
  €46k (€85k–€119k), €218k (€404k–€566k), €0.5k (€0.9k–€1.2k). Staged costs 67 % (North) / 71 % / 55 % of the full "≥2"
  cover under Tulva vs ~51 % under independence (with independence a 3rd gauge almost never joins) · exact; MC 1M agrees ·
  out/pricing.json (`staged_ge2_half_ge3_full`)
- Baseline context (outside source, not our model): "independence (no co-flooding)" is our comparison, not a regulator's
  number. From 30 Jan 2027 (Del. Reg. (EU) 2026/269) Finland gets a Solvency II standard-formula flood factor with 0 %
  flood correlation to SE/NO/DK; EIOPA considered 25 % for snowmelt floods and rejected it (EIOPA-BoS-24/462 §4.70);
  inside Finland a 19-zone matrix applies (mean ≈ 0.27) · business/NOTES_FOR_TOIVO.md

### Back-test on 1961–2025 (trigger "≥2 of cluster over fitted GEV 1-in-10") · scripts/backtest_index.py → out/backtest.json
- Paying years: Ostrobothnia 1965, 1966, 1971, 1972, 1974, 1977, 1984, 2000 (8/65 = 12 %, model 15 %, independence 11 %); North 1981, 1993, 2000, 2005, 2015, 2018, 2023, 2024 (8/65, model 13 %, indep 8 %); Satakunta–SE 1966, 1984, 1988 (3/65, model 6 %, indep 3 %) · exact (counts)
- March outlook (top-15 % SWE, 10 flags per cluster) flagged **11 of 19** paying cluster-years in advance (58 %, 90 % CI 40–74 %); 11 of 30 flags were followed by a payout (37 % vs 10 % base rate); **no payout ever followed a bottom-15 % snow year** (0 of ~30 cluster-years) · exact (counts), in-sample, small sample. Per cluster: Ostrobothnia 4/8 hit (1965, 1966, 1974, 1984), North 4/8 (1993, 2000, 2005, 2018), Satakunta–SE 3/3 (1966, 1984, 1988); Fisher one-sided p = 0.016 / 0.016 / 0.003
- Observed "≥2 over fitted 1-in-50" cluster-years: **4** (Ostrobothnia 1984, 2000; North 2005; Satakunta–SE 1966); model expects 3.4, independence 0.7 · exact (counts) vs exact (model)

## Simplified or assumed
- Tulva Index technical price = expected payout × (1 + 35 % risk load), one €10M payout per spring; the market charges 2.5–3.5× expected payout (see market-price line), so the technical price is a floor; no expenses, capital cost or reinsurance margin; Gaussian copula at 1-in-50 is extrapolation (t-copula check shows the price could be 5–60 % higher for ≥2).
- Back-test uses GEV 1-in-10 (1-in-50 too rare in 65 years) and is in-sample (snow skill and loadings fitted to the same years).
- Flood = spring (Mar–Jun) peak daily discharge over the gauge's own empirical top-10% (1-in-10) / GEV 1-in-50; discharge is not damage; ice-jam/frazil floods (Pori in winter) are missed.
- Joint tail beyond observed (k≥6, 1-in-50 levels) is Gaussian-copula extrapolation (no tail dependence); at k≥6 the model is above observed (slightly conservative).
- Snow skill is in-sample on 10 top-snow years per cluster; wide uncertainty.
- P(Kittilä AND Ivalo both pass 1-in-50 in the same spring) = 0.125 % (two-level model, exact) vs 0.040 % if
  independent (×3.1); 0.193 % after a top-15 % March snow outlook. QAE on ideal simulator: 0.125 % ± 0.011 pp
  vs Monte Carlo ± 0.027 pp at the same 16,000 oracle queries · exact / qae-sim / monte-carlo ·
  scripts/qae_sim.py
- P(≥2 of 3 Lapland areas pass 1-in-50) = 0.359 % (exact) vs 0.119 % if independent (×3.0) · exact · scripts/qae_sim.py
- Qrisp version, Kittilä AND Ivalo both pass 1-in-50 (exact 0.125 %): MLAE over Grover powers k=0,1,2 on
  Qrisp's simulator 0.118 % ± 0.017 pp RMSE (10 reps, 9,000 oracle queries each) vs Monte Carlo ± 0.037 pp at the
  same queries; Qrisp's IQAE (ε=3·10⁻⁴, deep circuits, simulator only) 0.125 %. Compiled for IQM Garnet with
  IQM's Qrisp pass manager: 4 / 23 / 45 CZ at k=0/1/2 (Qiskit transpile: 4 / 28 / 52) · qae-sim-qrisp ·
  scripts/qae_qrisp.py → out/qrisp_qae.json (simulator shots unseeded: estimates vary run to run)

(Simplified) The quantum circuits use a two-level discretisation of the fitted factor model (wet = top 30 %);
the continuous model is the classical reference. The outlook shift uses the in-sample snow skill (North 0.47).
- Full 14-area loader: 18 qubits, 49 CZ on a 20-qubit square lattice. Sampling reproduces the exact two-level
  model: P(≥4 areas over 1-in-10) exact 10.9 %, ideal-sim 10.8 %, independence 4.4 %. With 0.5 % CZ +
  2–3 % readout noise: 14.0 % (biased up by readout errors; needs readout mitigation) · exact / qae-sim ·
  scripts/loader_check.py
- **IBM hardware (ibm_marrakesh, job db3sssqmb58s7388bb00, 8 Oct 20:10):** P(Kittilä AND Ivalo both pass 1-in-50):
  exact 0.125 % · raw MLAE 0.308 % · noise-aware MLAE (two-twin calibration) 0.146 % · k=0 only 0.446 %.
  25 side-by-side copies × 2,000 shots per circuit (200k shots per estimate); 4/23/42/61 two-qubit gates for
  k=0..3. Per-copy k=0 rate ranged 0–2.95 % across the chip (qubit quality varies) · qae-ibm ·
  scripts/run_hw.py + scripts/analyse_run.py
- IBM, ≥2 of 3 Lapland (4 qubits): amplified circuits (k≥1, 67–164 two-qubit gates) were fully scrambled
  (signal gain ≈ 0); noise-aware estimate 0.491 % vs exact 0.359 %. A measured limit of today's hardware · qae-ibm
- **IBM run 2 (ibm_marrakesh, best-calibrated qubit triples, 20 copies, k=0..2, 4,000 shots):** exact 0.125 % ·
  raw 0.262 % · noise-aware 0.149 % · per-copy calibrated 0.148 % · k=0 only 0.237 %. Qubit selection cut the
  copy-to-copy spread from 0–2.95 % to 0.10–0.45 % and raised surviving signal (gain k=1: 0.78 vs 0.65).
  Residual bias +0.023 pp. Classical Monte Carlo with the same number of model evaluations would have ±0.004 pp, so
  classical wins on today's hardware · qae-ibm · IBM usage total 36 s of 600
- **IQM Garnet run 1 (8 Oct 21:21, job 613143, 34 s, 17 credits):** Kittilä+Ivalo exact 0.125 % · raw 0.269 % ·
  noise-aware 0.073 % (only 6,000 shots ≈ 7 expected events: shot-noise limited). ≥2 of 3 Lapland: exact 0.359 % ·
  raw 1.070 % · noise-aware 0.432 % (better than IBM's 0.491 %; 65 % of signal survives k=1 on Garnet) · qae-iqm
- **IQM Garnet run 2 (4 side-by-side copies, 10,000 shots, k=0..2):** Kittilä+Ivalo exact 0.125 % · raw 0.368 % ·
  noise-aware 0.164 % · per-copy calibrated 0.163 % · k=0 only 0.335 % (readout false positives). 120k shots.
  Per-copy k=0 rates 0.28–0.46 % · qae-iqm
- IQM Resonance credits: 280 per account (250 event voucher + 30 monthly); ~0.5 credits per second of runtime.
- **Full-scale loader on IQM Emerald (job 01a11cd4-da38-718b-80c9-7e259c6e4452, 8,000 shots):** all 14 river areas,
  18 qubits, 44 two-qubit gates, readout flips 0.5 %/0.6 % (corrected). P(≥4 areas over 1-in-10 in a spring):
  hardware 13.8 % · exact model 10.9 % · independence 4.4 % · observed 1961–2025 15.4 %. P(≥5): 6.3 % / 4.8 % /
  0.9 % / 7.7 %. The chip reproduces the joint tail that independence misses · qae-iqm (sampling) ·
  scripts/run_loader_hw.py, chart out/loader_emerald.png
- **Qrisp on IQM Garnet:** native Qrisp implementation, IQM pass manager 4/23/45 CZ; raw MLAE 0.354 % (exact
  0.125 %; no calibration circuits in this run), consistent with the raw Qiskit run (0.368 %) · qae-iqm ·
  scripts/qae_qrisp.py
