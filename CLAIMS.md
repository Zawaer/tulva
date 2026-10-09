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

## Pitch hook (verified 8 Oct)
"In May 2005, Kittilä and Ivalo flooded together. The snow had warned us for two months."
- 2005 is a North-cluster trigger year (≥2 areas over 1-in-10, and over the fitted 1-in-50) · out/backtest.json
- The 1 March snow index flagged 2005 in advance (one of the North's top-15 % snow years: 1969, 1973, 1974, 1993,
  1998, 2000, 2005, 2016, 2018, 2020) · out/snow_skill.json, out/backtest.json
- 1 March → the May peak ≈ 2–2.5 months. Damage ~€5M (SYKE/FMI, research notes); see business/CHEATSHEET.md for
  the €5–17M range and its sources.
- *(SUPERSEDED by the control-run comparison in "Review fixes"; the app no longer shows this line)* Web app line "5 areas at once 7× likelier than independence says": P(≥5 of 14 over 1-in-10) on IQM Emerald
  6.3 % vs independence 0.93 % = 6.8× (exact model 4.8 % = 5.2×; observed 7.7 % = 8.3×) · qae-iqm / exact ·
  out/runs/loader-iqm-emerald-*.json
- "When does quantum matter" chart (out/qae_scaling.png): at the hardware runs' budgets (5×10⁴–8×10⁵ model
  evaluations) classical Monte Carlo error is ~0.004–0.016 pp; the calibrated hardware estimates are off by
  0.021–0.052 pp (IBM best 0.021, IQM 4-copy 0.038), so ~5–10× worse than classical today. Ideal QAE extrapolated
  (1/N) would be ~0.0002 pp at 10⁶, i.e. ~25× better than Monte Carlo · qae-sim / qae-ibm / qae-iqm ·
  scripts/qae_scaling.py, out/qae_scaling_hardware_points.json

### IQM Emerald runs, 9 Oct (Vaishnav) · scripts/run_product_hw.py, scripts/run_loader_hw.py → out/runs/
Two-level model (circuit's own model), North loadings, 8,000 shots per circuit, noise-aware = two calibration twins.
- **Product trigger "≥2 of 5 North gauges over 1-in-50"** (6 qubits): exact 1.10 % → hardware noise-aware **1.41 %**
  (raw 9.42 %); after a top-15 % snow March exact 1.70 % → **2.08 %** (raw 9.61 %). k=0 13 CZ, k=1 234 CZ (k=1 mostly
  noise) · qae-iqm (emerald) · product-iqm-emerald-20261009T073815Z
- **Snow on hardware, Kittilä + Ivalo both over 1-in-50** (3 qubits, 4/27/46 CZ): low-snow / normal / high-snow March
  exact 0.070 % / 0.125 % / 0.193 % → hardware noise-aware **0.097 % / 0.197 % / 0.269 %**. Order and roughly the
  size of the snow effect survive; level biased high by ~0.03–0.07 pp · qae-iqm (emerald)
- 14-area loader at 1-in-50 (18 qubits, 44 CZ, 20,000 shots): P(≥2 areas) readout-corrected 16.0 % vs exact 4.8 %
  (independence 3.1 %); P(≥3) 4.6 % vs 0.8 %. At rare levels gate noise creates false triggers that swamp the true
  signal (at 1-in-10 the same circuit was close, see above) · qae-iqm (sampling) · loader-iqm-emerald-20261009T074104Z
- **Rerun with side-by-side copies** (IQM Emerald, 10 copies of the 3-qubit circuit = 240,000 shots per instance; 6
  copies of the 6-qubit k=0 circuit = 48,000): Kittilä + Ivalo low / normal / high snow, exact 0.070 / 0.125 /
  0.193 % → noise-aware **0.082 / 0.166 / 0.249 %** (errors 0.012–0.056 pp, about half of the 1-copy run). **High-snow
  vs low-snow risk ratio: exact 2.8×, hardware 3.0×.** *(SUPERSEDED by 3.05× vs 2.75×, "Review fixes" below)* Product "≥2 of 5 North", k=0 only: exact 1.10 % / 1.70 % →
  1.84 % / 2.68 % (worse than the k=0,1 run: the ≈0 twin has no single-trigger states, so it under-calibrates the
  false ≥2 counts) · qae-iqm (emerald) · product-iqm-emerald-20261009T075338Z
- Snow ratio, recomputed from product-iqm-emerald-20261009T075338Z.analysis.json (use these): high-snow / low-snow
  exact 0.1933/0.0704 = **2.7×**, hardware calibrated 0.2494/0.0818 = **3.1×** (supersedes the rounded 2.8×/3.0× above) *(SUPERSEDED: use 3.05×,
  90 % CI 2.6–3.6, vs 2.75× exact, "Review fixes" below)*

### Snow + spring temperature + rain (Vaishnav, 9 Oct) · scripts/fetch_weather.py, scripts/weather_model.py → out/weather_model.json
FMI monthly observations (Sodankylä / Kauhava / Pori), April–May mean temperature and total rain, 1961–2025.
In-sample, and uses the *observed* April–May weather, so it is a perfect-forecast upper bound.
- Share of year-to-year flood variation explained (R² of cluster flood index): North **0.17 snow only → 0.28 with
  temperature + rain** (rain matters, β = +0.34); Ostrobothnia 0.49 → 0.51; Satakunta–SE 0.40 → 0.43. April–May mean
  temperature adds almost nothing · exact (least squares)
- Back-test, top-15 % predicted years vs payout cluster-years (≥2 over GEV 1-in-10): snow only **9 of 19**, snow +
  temperature + rain **12 of 19** (this script's snow index; Toivo's backtest_index.py gets 11 of 19 with snow) · exact (counts)
- Two-level network, P(≥2 of 5 North over 1-in-50): 1.09 % overall; 0.62 % with low snow/temp/rain, 1.46 % snowy,
  2.28 % snowy + warm + wet · exact (enumeration of 2^15 states)

### 43-qubit weather circuit (Vaishnav, 9 Oct) · scripts/run_big_hw.py
One connected circuit: national + regional snow/temp/rain, wet-spring per cluster, 14 areas at 1-in-10 and 1-in-50.
- Classical check (Aer matrix-product-state simulator, 200,000 shots, ~2 min on a laptop): matches exact (1.11 % vs
  1.09 %; ≥4 of 14 over 1-in-10 9.6 % vs 9.6 %) · monte-carlo (MPS sampling) · big-mps-20261009T112913Z
- **IQM Emerald, 43 qubits, 237 CZ, 20,000 shots: noise dominates.** P(≥2 of 5 North over 1-in-50) 26 % vs exact 1.09 %;
  ≥4 of 14 over 1-in-10 40 % vs 9.6 %. Weather qubits early in the circuit stay near their 30 % (25–39 %); area
  qubits at the end read 1 about 21–23 % of the time instead of 2–10 %. Errors pile up along the circuit · qae-iqm
  (sampling, raw) · big-iqm-emerald-20261009T113236Z

### Where today's hardware stops: weather → rivers samplers on IQM Emerald (Vaishnav, 9 Oct) · scripts/run_mid_hw.py
North cluster only; snow / April–May temperature / rain as three "high = top 30 %" qubits (independent, within-cluster
correlation dropped), wet-spring qubit from the fitted P(W | s,t,r), five area qubits. 20,000 shots, raw (no calibration).
- **9 qubits, 22 CZ, areas over 1-in-10: works.** P(≥2 of 5) 16.5 % vs exact 13.6 %; by scenario, snowy + rainy
  30.0 % vs 29.1 %, all three high 27.5 % vs 28.0 %, snowy only 20.9 % vs 18.0 %, nothing high 12.5 % vs 7.8 %
  (noise adds fake floods mostly in the quiet scenario) · qae-iqm (sampling, raw) · mid9-iqm-emerald-20261009T115325Z
- **14 qubits, 54 CZ, areas at 1-in-10 and 1-in-50: noise-dominated.** ≥2 over 1-in-10 23.2 % vs 13.6 %; ≥2 over
  1-in-50 5.3 % vs 1.09 % (quiet scenario 4.3 % vs 0.62 %). Scenario order survives, levels do not · qae-iqm ·
  mid14-iqm-emerald-20261009T115403Z
- Measured limit, all runs together: ≤ ~15 qubits, ≤ ~50 two-qubit gates, events no rarer than ~1-in-10 give the
  right numbers raw or after calibration; 1-in-50 events and ≥ ~200 gates do not · qae-iqm
- Licence price on slide 7: "€25k pilot season, then ~€75k per insurer per year (indicative)": ASSUMPTION set by the
  team from typical risk-model SaaS pricing (research estimate €50–150k/insurer/yr); to validate in a pilot · assumption

### Pitch-derived numbers (10 Oct deck revision) · derived from the lines above, no new computation
- **Rate on line** (market premium ÷ limit, per year), North "≥2 of 5 over 1-in-50": independence **1.0–1.3 %**,
  Tulva **4.9–6.9 %**, after a high-snow March **16–23 %** (low-snow 0.4–0.6 %); Ostrobothnia 1.4–2.0 % / 6.4–9.0 % /
  32–45 %; Satakunta–SE 0.3–0.4 % / 1.5–2.2 % / 7.2–10.1 % · exact × multiple ÷ limit · out/pricing.json
  (`market_premium_eur` / `payout_eur`), chart scripts/pitch_charts.py → out/pitch_cost.png. Limit = each insurer's
  retained 1-in-50 joint loss; €10M is illustrative only (business case §4 "size the limit", §9 row 10)
- "About four times as often as independence": ≥4 of 14 over 1-in-10, observed 15.4 % vs independence 3.9 % = 3.9× ·
  exact (counts) · out/joint_counts.json
- Calibration in relative terms (Kittilä + Ivalo, exact 0.125 %): raw 0.262 % (IBM, 2.1×) / 0.368 % (Garnet, 2.9×) →
  calibrated 0.148 % (+18 %) / 0.163 % (+30 %): "from 2–3× off to within ~20–30 % of exact" *(SUPERSEDED: "within
  20–30 %" dropped; slide 5 shows bootstrap CIs and "raw readings were 2–3× off")* · qae-ibm / qae-iqm ·
  out/HARDWARE_RESULTS.md
- Measured limits line on slide 6: "~18 qubits / ~50 two-qubit gates work" = 14-area loader on Emerald (18 qubits,
  44 CZ) right at 1-in-10, 3-qubit QAE (≤ 53 CZ) calibrates well, 4-qubit (67–164 CZ) and 43-qubit (237 CZ) circuits
  scrambled; "1-in-50: 16 % vs 4.8 % exact" = same 18-qubit loader, P(≥2 of 14 over 1-in-50), readout-corrected ·
  qae-iqm · out/HARDWARE_RESULTS.md
- Slide 3 innovation line, outside sources (business/reports/Tulva flood cover business case.md §5, §1, §6): Verisk
  Inland Flood Model for Central Europe covers FI/SE/NO and is precipitation-driven (Verisk docs); SYKE publishes
  spring peak outlooks but nobody turns them into a priced joint-loss distribution; Swiss Re FLOW pays on a single
  river gauge, for companies · source
- QA capital credit: EIOPA Q&A 1597, basis risk cannot be haircut in the standard formula; index covers can be
  credited under internal models · source (business case §3)
- *(Replaced 9 Oct evening, see below)* Demo video deck/video/tulva_demo.mp4: 37 s, shows the 1-in-10 Emerald loader run (job 01a11cd4…, ≥4: hardware
  13.8 % vs exact 10.9 % vs independence 4.4 %) · qae-iqm

## Review fixes (Fri 9 Oct evening)
- **Control run, IQM Emerald (independent loader, same 18 qubits / 44 CZ, 8,000 shots):** noise alone fattens tails.
  P(≥4 areas over 1-in-10): exact independent 4.4 %, chip-independent 9.7 %; exact correlated 10.9 %, chip-correlated
  13.8 %. ≥5: 0.9 / 2.6 / 4.8 / 6.3 %. ≥6: 0.1 / 0.6 / 1.9 / 2.4 %. → On the same chip, the correlated model gives
  1.4× (≥4), 2.4× (≥5), 4× (≥6) more multi-area floods than the identical independent circuit (exact: 2.5× / 5.3× / 19×).
  The correlation survives on hardware but is attenuated by noise. Supersedes the "7× likelier than independence" line,
  which compared hardware with an exact value · qae-iqm (sampling) · out/runs/loader-control-indep-iqm-emerald-*.json
- **Bootstrap 90 % intervals of calibrated QAE estimates** (scripts/bootstrap_ci.py → out/bootstrap_ci.json), Kittilä+Ivalo
  exact 0.125 %: IBM run 1 0.146 % (0.133–0.157), IBM run 2 0.149 % (0.140–0.157), IQM Garnet run 1 0.073 % (0.038–0.114),
  IQM Garnet run 2 0.164 % (0.147–0.180). Lapland ≥2 of 3 exact 0.359 %: IBM 0.491 % (0.378–0.612), Garnet 0.432 %
  (0.366–0.510). All calibrated runs: −42 % to +37 % (best +17 %); raw readings were 2–3× off. The IBM/IQM best-run biases
  (+17–31 %) are systematic (intervals exclude exact) · qae-ibm / qae-iqm
- **Snow ratio on IQM Emerald, high/low March:** 3.05× (90 % CI 2.6–3.6) vs exact 2.75×. The interval contains the exact
  ratio, so the snow signal survives on hardware · qae-iqm · out/bootstrap_ci.json
- Illustrative limit for the pitch: €3M (≈ one insurer's share of the 2005 Lapland insured loss, market ~€5–17M per the
  business report) × market rate 4.9–6.9 % = **€147k–207k per year** (North ≥2 of 5) · derived
- Normal-snow March on IQM Emerald (same run): 0.166 % (90 % CI 0.151–0.180 %) vs exact 0.125 % · qae-iqm ·
  out/bootstrap_ci.json ("emerald snow normal"; appended after the others, so their intervals are unchanged).
  Slide 5 chart out/pitch_snow.png: low / normal / high exact 0.070 / 0.125 / 0.193 %, chip 0.082 / 0.166 / 0.249 %
  with these intervals
- Slide 5 table: IBM run 2 0.149 % (0.140–0.157), IQM Garnet run 2 0.164 % (0.147–0.180), exact 0.125 % (noise-aware
  MLAE, the bootstrap's estimator; the per-copy values 0.148 / 0.163 % above are the same runs) · qae-ibm / qae-iqm
- Slide 6 "an independent control run reads 2× high": ≥4 of 14 over 1-in-10, chip-independent 9.7 % vs exact
  independent 4.4 % = 2.2× · qae-iqm · loader-control-indep-iqm-emerald-20261009T135910Z
- Slide 2 "≈4×" = 15.4 % / 3.9 % (line "About four times as often" above); slide 3 "≈5× under-priced" = North "≥2 of 5"
  Tulva / independence premium 5.1× (pricing section) · exact
- Slide 3 "Example: €3M limit ≈ €150–210k / year" = the €147k–207k line above, rounded · derived
- Web app 2005 replay: North cluster 1 March snow index = **87th percentile (top 15 %)**; national index 62nd · data ·
  scripts/export_web.py. (The app previously showed the national 59th: export_web ranked missing SWE years as the
  snowiest; fixed to match fit_dependence.py, so its top-15 % years now equal out/snow_skill.json. Same fix moves the
  app's "Observed March 2025" North percentile from 27th to 32nd.)
- Web app loader card: dashed "chip, independent circuit" series = the control run above (readout-corrected); the
  sentence "1.4×–4× more multi-area floods than an identical independent circuit (≥4 to ≥6)" is computed from the
  two runs in web/app.js · qae-iqm
- Demo video (re-recorded 9 Oct evening), 37 s, captions ≥ 5 s each: map → snow high → IQM Emerald shots low/snowy
  ("about 3× the risk" = the 3.05× calibrated ratio; the raw shot grid shows 13 vs 31 both-flood shots of 8,000) →
  14-area loader (18 qubits) → 2005 replay (North snow top 15 %) · deck/video/record_demo.mjs
- Slide 7 "fee per deal (€25k pilot)": the €25k pilot is the team assumption in the licence line above; the per-deal
  fee model replaces the per-insurer licence on the slide · assumption
- **Realistic baseline (round 2 review, verified):** North "≥2 of 5 over 1-in-50", 2M-sample Monte Carlo of the Gaussian
  copula: independence 0.38 %; **equicorrelation 0.27 (≈ mean of the regulator's 19-zone matrix inside Finland) 1.09 %**;
  Tulva fitted (within-cluster corr 0.56) **1.98 %** → **≈1.8× under-priced vs regulator-style correlation**, ≈5× vs
  independence. Snow conditioning then moves it ×3 within a season (high-snow 6.3 %) · monte-carlo
- **Two-level (circuit) model vs continuous on the product trigger:** 1.10 % vs 1.98 % (−44 %); at 1-in-10 (≥4 of 14)
  10.9 % vs 12.2 %. The circuit's model is a simplified version; prices come from the continuous classical model · exact

## Round-2 deck pass (Sat 10 Oct, early) · derived from the lines above unless marked
- **Slide 3 "≈2× under-priced even vs regulator-style correlation"** = North "≥2 of 5 over 1-in-50" Tulva 1.96 % (exact)
  / 1.09 % at equicorrelation 0.27 (monte-carlo, "Realistic baseline" above) = 1.80×, shown rounded as ≈2× (spoken "about
  TWICE"); the second line "≈5× if rivers priced independently" = 5.1× (pricing section). Cross-check: one-factor
  Gauss–Hermite quadrature at equicorrelation 0.27 gives 1.11 % (ratio 1.77×), same rounding · derived / exact
- **Slide 3 chart, "Regulator-style correlation (0.27)" rate on line 2.7–3.8 %** = 1.09 % × €10M × 2.5–3.5 ÷ €10M
  (same method as the other bars: probability × payout × market multiple ÷ limit) · derived · scripts/pitch_charts.py
  (`P_REG_027`) → out/pitch_cost.png. Other bars unchanged: independent 1.0–1.3 %, Tulva 4.9–6.9 %, after a snowy March
  16–23 %
- **Slide 3 "Per €1M of cover: ~€49–69k / year"** = Tulva rate on line 4.9–6.9 % × €1M (replaces the €3M example) · derived
- Spoken "this March's snow moves it THREE times more" = after a top-15 % snow March 6.4 % vs 1.96 % (3.3×; "×3" in the
  realistic-baseline line) · exact
- **Slide 5 "+19 % / +31 % bias (calibrated; raw 2–3× off)"** = IBM run 2 0.149 % / 0.125 % = +19 %, IQM Garnet run 2
  0.164 % / 0.125 % = +31 % (bootstrap estimator, intervals exclude exact); raw 2.1× / 2.9× · qae-ibm / qae-iqm
- Slide 5 block "a two-level version of the 14-area model: 18 qubits, 44 two-qubit gates on IQM Emerald (sampling)" =
  the full-scale loader line above; replaces "all 14 areas, one chip" / "whole model" wording in deck, app, video and QA
- Demo video caption "Snowy March: more than twice the red" = raw both-flood shots on the app's IQM Emerald grid, 31 vs
  13 of 8,000 (2.4×); spoken "about three times the risk" on slide 5 = calibrated 3.05× (CI 2.6–3.6) · qae-iqm
- **Slide 7 "Year 3: Nordic snowmelt flood, 3–6 insurers ≈ €0.1–0.6M a year"**: ASSUMPTION, the business case's
  illustrative year-3 SOM (business/reports/Tulva flood cover business case.md §5: "3–6 licences at €30–100k, so about
  €0.1–0.6M a year, plus structuring fees"); "€25k pilot, then fee per deal / ~€75k a year" = the licence assumption
  above · assumption
- Slide 7 "regulator judged snowmelt correlation insignificant (one vendor model)" = EIOPA-BoS-24/462 §4.70 as summarised
  in the business case §3 · source. "65 years of evidence" = SYKE spring peaks 1961–2025 · data
- QA 2024 back-test: Ostrobothnia's top-15 % snow flag was on in 2024 and the Ostrobothnia index did not pay (one of its
  six false alarms: 1962, 1981, 1982, 1988, 2022, 2024); only Alavieska–Ylivieska passed its empirical 1-in-10 (115 %),
  four others peaked at 95–97 % of it. North paid in 2024 (3 of 5 over GEV 1-in-10) without a snow flag (a miss) ·
  exact (counts) · out/backtest.json, web/data/app.json (replay peaks)
- App badges: snow-conditioned probabilities and prices are now labelled "model" (in-sample snow skill), market ranges
  "model + market multiple" (the 2.5–3.5× multiple is an outside source); unconditional model values stay "exact".
  App co-flooding multipliers now round half up (Ostrobothnia 3.15 → 3.2×, as above; it showed 3.1×) · web/app.js
