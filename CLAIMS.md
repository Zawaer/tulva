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
- *(SUPERSEDED: no innovation line on slide 3 since round 3)* Slide 3 innovation line, outside sources (business/reports/Tulva flood cover business case.md §5, §1, §6): Verisk
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
- *(SUPERSEDED: slide 6 no longer has this line; control run is on slide 9)* Slide 6 "an independent control run reads 2× high": ≥4 of 14 over 1-in-10, chip-independent 9.7 % vs exact
  independent 4.4 % = 2.2× · qae-iqm · loader-control-indep-iqm-emerald-20261009T135910Z
- Slide 2 "≈4×" = 15.4 % / 3.9 % (line "About four times as often" above); slide 3 "≈5× under-priced" = North "≥2 of 5"
  Tulva / independence premium 5.1× (pricing section) · exact
- *(SUPERSEDED: replaced by "per €1M of cover", now QA only)* Slide 3 "Example: €3M limit ≈ €150–210k / year" = the €147k–207k line above, rounded · derived
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
- *(SUPERSEDED: slide 7 shows the per-insurer licence; per-deal fee is only the at-scale QA answer)* Slide 7 "fee per deal (€25k pilot)": the €25k pilot is the team assumption in the licence line above; the per-deal
  fee model replaces the per-insurer licence on the slide · assumption
- **Realistic baseline (round 2 review, verified):** North "≥2 of 5 over 1-in-50", 2M-sample Monte Carlo of the Gaussian
  copula: independence 0.38 %; **equicorrelation 0.27 (≈ mean of the regulator's 19-zone matrix inside Finland) 1.09 %**;
  Tulva fitted (within-cluster corr 0.56) **1.98 %** → **≈1.8× under-priced vs regulator-style correlation**, ≈5× vs
  independence. Snow conditioning then moves it ×3 within a season (high-snow 6.3 %) · monte-carlo
- **Two-level (circuit) model vs continuous on the product trigger:** 1.10 % vs 1.98 % (−44 %); at 1-in-10 (≥4 of 14)
  10.9 % vs 12.2 %. The circuit's model is a simplified version; prices come from the continuous classical model · exact

## Round-2 deck pass (Sat 10 Oct, early) · derived from the lines above unless marked
- *(SUPERSEDED by "Round-3 deck pass": ≈1.8×, 1.11 %)* **Slide 3 "≈2× under-priced even vs regulator-style correlation"** = North "≥2 of 5 over 1-in-50" Tulva 1.96 % (exact)
  / 1.09 % at equicorrelation 0.27 (monte-carlo, "Realistic baseline" above) = 1.80×, shown rounded as ≈2× (spoken "about
  TWICE"); the second line "≈5× if rivers priced independently" = 5.1× (pricing section). Cross-check: one-factor
  Gauss–Hermite quadrature at equicorrelation 0.27 gives 1.11 % (ratio 1.77×), same rounding · derived / exact
- *(SUPERSEDED: 2.8–3.9 %, "Round-3 deck pass")* **Slide 3 chart, "Regulator-style correlation (0.27)" rate on line 2.7–3.8 %** = 1.09 % × €10M × 2.5–3.5 ÷ €10M
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
- *(SUPERSEDED: caption reworded in round 3)* Demo video caption "Snowy March: more than twice the red" = raw both-flood shots on the app's IQM Emerald grid, 31 vs
  13 of 8,000 (2.4×); spoken "about three times the risk" on slide 5 = calibrated 3.05× (CI 2.6–3.6) · qae-iqm
- *(SUPERSEDED: "3–6 × €75k = €0.2–0.45M", round 3)* **Slide 7 "Year 3: Nordic snowmelt flood, 3–6 insurers ≈ €0.1–0.6M a year"**: ASSUMPTION, the business case's
  illustrative year-3 SOM (business/reports/Tulva flood cover business case.md §5: "3–6 licences at €30–100k, so about
  €0.1–0.6M a year, plus structuring fees"); "€25k pilot, then fee per deal / ~€75k a year" = the licence assumption
  above · assumption
- *(SUPERSEDED: removed from slide 7 in round 3)* Slide 7 "regulator judged snowmelt correlation insignificant (one vendor model)" = EIOPA-BoS-24/462 §4.70 as summarised
  in the business case §3 · source. "65 years of evidence" = SYKE spring peaks 1961–2025 · data
- QA 2024 back-test: Ostrobothnia's top-15 % snow flag was on in 2024 and the Ostrobothnia index did not pay (one of its
  six false alarms: 1962, 1981, 1982, 1988, 2022, 2024); only Alavieska–Ylivieska passed its empirical 1-in-10 (115 %),
  four others peaked at 95–97 % of it. North paid in 2024 (3 of 5 over GEV 1-in-10) without a snow flag (a miss) ·
  exact (counts) · out/backtest.json, web/data/app.json (replay peaks)
- App badges: snow-conditioned probabilities and prices are now labelled "model" (in-sample snow skill), market ranges
  "model + market multiple" (the 2.5–3.5× multiple is an outside source); unconditional model values stay "exact".
  App co-flooding multipliers now round half up (Ostrobothnia 3.15 → 3.2×, as above; it showed 3.1×) · web/app.js
- QA "how much comes from amplification": Kittilä + Ivalo signal gain by Grover step k = 1 / 2 (fitted from the two
  calibration twins): IQM Emerald 0.56–0.59 / 0.44 (low / normal / high snow), IBM run 2 0.78 / 0.69, Garnet run 2
  0.77 / 0.60; false-trigger offset at k = 1–2 2.0–6.3 % vs a 0.07–0.19 % signal · qae-ibm / qae-iqm ·
  out/runs/{ibm-ibm_marrakesh-20261008T174523Z, iqm-garnet-20261008T182534Z, product-iqm-emerald-20261009T075338Z}.analysis.json
- QA "two-level circuit loses 44 % at 1-in-50" = 1.10 % vs 1.98 % (round-2 line above) · exact / monte-carlo

## Round-3 deck pass (Sat 10 Oct) · scripts/round3_numbers.py → out/round3_numbers.json unless marked
- **Regulator-style baseline, North "≥2 of 5 over 1-in-50" at one equicorrelation 0.27: 1.11 %** (one-factor
  Gauss–Hermite quadrature, exact; Monte Carlo 2M samples 1.12 % ± 0.007 pp). Replaces the 1.09 % above, which no script
  in the repo reproduces · exact / monte-carlo
- **Slide 3 "Fair price ≈1.8× what the 2027 capital rule implies"** = Tulva 1.96 % (exact, out/pricing.json; the
  one fair-price number everywhere; the 1.98 % above was a 2M Monte Carlo of the same model) / 1.11 % = **1.77×**,
  shown as ≈1.8× · exact
- Slide 3 chart "2027 rule's average link (0.27)" market rate on line **2.8–3.9 %** = 1.11 % × 2.5–3.5 · derived ·
  scripts/pitch_charts.py. Other bars unchanged (independent 1.0–1.3 %, Tulva 4.9–6.9 %); the "after a snowy March
  16–23 %" bar is removed (not a tradable price)
- **Slide 3 "After a snowy March the fair risk triples (1.96 % → 6.4 %)"** = out/pricing.json North ge2
  `tulva_high_outlook` 6.445 % / 1.963 % = 3.28× · exact (in-sample snow skill). One high-snow number everywhere: 6.4 %
  (the 6.3 % above was Monte Carlo)
- **Slide 2 "10 of 65 springs (90 %: 9–24 %)"**: Wilson 90 % interval 9.4–24.1 % · exact. **"3.9× as often as chance"** =
  15.4 % / 3.9 % (chance = independence on the same gauge-years as observed, out/joint_counts.json
  `independent_same_years`). With all 14 gauges every year (binomial) chance is 4.41 %, i.e. 3.5×; that is the
  4.42 % in out/HARDWARE_RESULTS.md (the circuit's independent case). 35 gauge-years are missing, so the same-years
  baseline is the like-for-like one. At the Wilson lower bound: 2.4× · exact
- App/video stat "2.8×" relabelled: per pair, two areas of one cluster both over 1-in-10 in the same spring vs chance
  (out/dependence.json); slide 2's 3.9× is per spring, ≥4 of 14 · exact
- **Slide 1 "four Lapland rivers flooded together" (2005)**: over their empirical 1-in-10 level Ivalo, Kittilä,
  Rovaniemi, Tornio (the map's four filled dots); over fitted 1-in-50 Ivalo, Kittilä, Rovaniemi; North 1 March snow
  87th percentile (top 15 %), in-sample back-test · data · web/data/app.json replay
- IBM/IQM calibrated values made consistent: deck, app, QA and out/HARDWARE_RESULTS.md now all use the pooled
  noise-aware MLAE (the bootstrap's estimator): **IBM Marrakesh run 2 0.149 %, IQM Garnet run 2 0.164 %** (IBM run 1
  0.146 %). The per-copy fits (0.148 % / 0.163 %) are no longer shown; scripts/hardware_summary.py and export_web.py
  changed. The slide-6 scaling chart's hardware points still use the per-copy fits (≤0.001 pp difference, not visible)
  · qae-ibm / qae-iqm
- Slide 5 "Calibrated, still +19 % / +31 % high" = 0.149 / 0.125 and 0.164 / 0.125 · qae-ibm / qae-iqm. CIs, raw
  readings and job IDs moved to appendix slide 9 (rows: CLAIMS lines above; snow ratio raw 0.388 / 0.296 = 1.3×,
  calibrated 3.05× (2.6–3.6), exact 2.75×; 14-area loader 13.8 % vs 10.9 % (1-in-10), 16.0 % vs 4.8 % (1-in-50);
  control run 9.7 % vs 4.4 %; Emerald signal gain 0.56–0.59 / 0.44)
- Slide 5 "Grover steps k = 0–3": IBM run 1 k = 0..3, other runs k = 0..2 · qae-ibm / qae-iqm
- Slide 6 "18 qubits, 44 two-qubit gates (IQM Emerald): works at 1-in-10, fails at 1-in-50 (16 % vs 4.8 % exact)" =
  the full-scale loader lines above · qae-iqm. The "~8k logical qubits" footnote is removed from the slide (QA only,
  Chakrabarti et al. 2021, derivative pricing, not our estimate)
- Demo video (re-recorded 10 Oct): captions "Real IQM Emerald runs. Red = BOTH rivers flood. Low snow: little red";
  "Snowy March: more red. Corrected: about 3× the risk (exact 2.75×)" = calibrated 3.05× vs exact 2.75× (the grid's
  raw 13 vs 31 of 8,000 is one sample; raw over all 240k shots is 1.3×); 2005 caption now at ~29 s of 37 · qae-iqm
- **Slide 7 revenue**: €25k pilot, then ~€75k per insurer a year (licence line above); **year 3: 3–6 insurers × €75k
  = €225k–450k ≈ €0.2–0.45M a year**; Finland first, then SE/NO snowmelt regions · assumption
- Slide 7 "Why now: 2027: Finland's first Solvency II flood charge uses fixed correlations" = 0 % FI–SE/NO/DK and the
  fixed 19-zone matrix inside Finland (mean ≈ 0.27), Del. Reg. (EU) 2026/269 · source. "No vendor model uses this
  winter's snow" removed (not verifiable)
- Slide 7 "Basis risk: … the same 1-in-50 test as all 7 Finnish home insurers' flood terms" = docs/flood_terms_check.md
  (OP Pohjola, If, LähiTapiola, Fennia, Turva, Pohjantähti, POP; "kerran 50 vuodessa tai harvemmin") · source


## Round-4 deck pass (Sat 10 Oct) · scripts/round4_numbers.py → out/round4_numbers.json unless marked
- **Naming correction (applies to every "Kittilä + Ivalo" / "Kittilä AND Ivalo" / "≥2 of 3 Lapland" circuit line
  above):** the A3/A4 circuits give every river the same North-cluster loadings (national 0.44, cluster 0.60) and the
  same 1-in-50 trigger (np.full in scripts/run_hw.py `instance()` and scripts/run_product_hw.py). They are "a two-river
  North-cluster pair" / "3 North-cluster rivers", not Kittilä and Ivalo specifically. Numbers unchanged · verified in code
- **Slide 3 headline "Fair price ≈1.8× a model using the 0.27 average correlation of the 2027 Finnish flood-zone
  matrix"** = 1.96 % / 1.11 % = 1.77× (round-3 lines). 0.27 = mean of all 19 zones; the Lapland zones' own entries and
  the zone-to-region map are not in the repo, so not used · exact
- **Year-bootstrap 90 % intervals (400 joint resamples of springs + 1 March SWE; loadings refit, North snow skill
  re-estimated, exact pricing):** North "≥2 of 5 over 1-in-50" fair expected loss **1.96 % (1.63–2.15 %)**; after a
  snowy (top-15 %) March **6.4 % (3.57–9.05 %)**; ratio **3.28× (2.12–4.41×)**, shown "triples (90 %: 2.1–4.4×)"; skill
  0.47 (0.27–0.64). Point refit reproduces 1.964 % / 6.445 % · exact + bootstrap.
  Slide 3 chart out/pitch_cost.png now shows only expected loss (0.27 correlation 1.11 %, Tulva 1.96 %, snowy March
  6.4 %); the market-price bars (2.8–3.9 / 4.9–6.9 %) and "€49–69k per €1M" moved to QA
- **Slide 6 "correlation survives but attenuated: chip vs chip-control 1.4× (exact 2.5×)"** = P(≥4 of 14 over 1-in-10),
  IQM Emerald readout-corrected 13.83 % / control 9.69 % = 1.43×; exact 10.86 % / 4.41 % = 2.46× · qae-iqm / exact ·
  loader-iqm-emerald-20261008T184433Z, loader-control-indep-iqm-emerald-20261009T135910Z
- **Slide 5 / appendix "Grover steps k = 0–2"**: the shown results (IBM run 2 174523Z, Garnet run 2 182534Z, Emerald
  075338Z) used k = 0, 1, 2; only IBM run 1 (170341Z, not shown) used k = 0–3 · verified in out/runs
- Slide 5 "amplified circuits keep ≈0.5 of the signal on Emerald, 0.6–0.8 on IBM / Garnet" = signal gain k = 1 / 2:
  Emerald 0.56–0.59 / 0.44, IBM run 2 0.78 / 0.69, Garnet run 2 0.77 / 0.60 (round-2 line) · qae-ibm / qae-iqm
- **Slide 7 basis risk "paid in the 1966, 2005 and 2018 flood springs; missed Ostrobothnia 2012–13 and 2024"**: known
  loss springs from the business case loss table (§1; outside source) vs the back-test trigger (≥2 of cluster over GEV
  1-in-10): 1966 Satakunta–SE (and Ostrobothnia) paid, 2005 North paid, 2018 North paid; at GEV 1-in-50 only 1966 and
  2005; 2012, 2013 Ostrobothnia no trigger; 2020 North no trigger (snow flag on); 2024 Ostrobothnia no trigger with the
  snow flag on (false alarm; North paid that year) · exact (counts) · out/backtest.json
- **Slide 7 "Premium, insurer → reinsurer: ≈€0.5–0.7M a year per €10M layer"** = North "≥2 of 5" market premium
  €491k–€687k (pricing section, model × 2.5–3.5 market multiple) · exact × outside multiple
- Slide 7 "3–6 insurers × €75k ≈ €0.2–0.45M/yr", spoken "up to 450 thousand"; "Upside: Nordic snowmelt" unsized ·
  assumption. "If Insurance" uses a (Sampo group) partial internal model · source (business research
  solvency_regulation.md); which other Finnish insurers use the standard formula is not documented in the repo, so none
  are named. OP named only as "we'd like to pilot with" (QA), no agreement
- Spoken "almost FOUR times" = 3.9× (slide 2). App stat 2.8× now labelled "per river pair" vs slide 2 "per spring" ·
  exact
- Demo video re-recorded (10 Oct, round 4), 37 s, same cue times; captions shortened: "IQM chip. Red: both flood. Low
  snow, little red." and "Snowy March: about three times the risk, close to exact." (= calibrated 3.05× vs exact 2.75×)
  · qae-iqm · deck/video/record_demo.mjs

## VTT Q50 (Fri 9 Oct, via the LUMI hackathon module) · scripts/run_hw.py, scripts/run_loader_hw.py --backend q50 → out/runs/; summary scripts/hardware_summary.py → out/HARDWARE_RESULTS.md, intervals scripts/bootstrap_ci.py → out/bootstrap_ci.json
Producer tag: qae-q50 (VTT Q50 hardware). Same two-level model and circuits as IBM / IQM.
- **3-qubit two-river North-cluster pair, both over 1-in-50, three repeats** (1 copy, k = 0, 1, 2, 2,000 shots per
  circuit, 6,000 per instance; two-qubit gates by k 4 / 27 / 46). Exact **0.125 %** (0.12497 %).
  | Repeat | File | Job | k=0 rate | Raw MLAE | Calibrated (noise-aware MLAE) | Bootstrap 90 % CI | Gain k=0/1/2 | Zero offset k=0 |
  |---|---|---|---|---|---|---|---|---|
  | 1 | q50-20261009T145044Z | 7d20d8ac-1fad-4ecd-951d-6ae4b86055ca | 0.750 % | 1.479 % | **0.465 %** | 0.17–0.80 % | 1.06 / 0.19 / 0.05 | 0.002 |
  | 2 | q50-20261009T145110Z | a6fb9d52-611a-4a6f-bd1c-b1ae18650287 | 0.800 % | 1.577 % | **0.534 %** | 0.20–0.86 % | 1.10 / 0.13 / 0.05 | 0.002 |
  | 3 | q50-20261009T145135Z | 381179fb-a718-402c-afe4-e775300f2c4a | 0.800 % | 1.536 % | **0.107 %** | 0.00–0.48 % | 1.11 / 0.12 / 0.06 | 0.006 |
  Calibrated mean 0.369 %, **range 0.107–0.534 % (deck: "0.11–0.53 %")** vs exact 0.125 %; raw 1.48–1.58 %
  (~12× exact). **Not reproducible across repeats**: the ~5× spread is driven by the zero-calibration offset at k=0
  (0.002 vs 0.006); repeat 3 landing near exact (−14 %) is luck, not precision. **Signal kept at k=1: 0.12–0.19**
  (vs Emerald 0.56–0.59, IBM run 2 0.78, Garnet run 2 0.77 on the same circuit; all A3 runs on other chips 0.56–0.88),
  at k=2 0.05–0.06. Classical MC at the same budget ±0.026 pp · qae-q50 · out/runs/q50-*.analysis.json
- **Failed first attempt** q50-20261009T144440Z (4 copies on best-qubit triples [49,50,51] [43,42,48] [38,39,44]
  [34,33,40], 4,000 shots, k = 0–2): job d02bd3b5-ca4a-48f1-9003-da506d4b7607 submitted, result retrieval failed with
  BadRequestError; no counts, no numbers · out/runs/q50-20261009T144440Z.json
- **14-area loader at 1-in-10 on Q50** (18 qubits, 49 two-qubit gates, 8,000 shots, job
  9cdb0158-7574-4ed3-b077-c8a2d47a1186, readout flip p01 2.1 % / p10 3.4 %): P(≥4 areas) raw 34.2 %, readout-corrected
  **31.2 %** (deck "31 %") vs exact **10.9 %**, independence 4.4 %; Emerald on the same circuit 13.8 %
  (loader-iqm-emerald-20261008T184433Z). P(≥2) 75.2 % vs 37.9 % exact. Noise dominates on Q50 at this size ·
  qae-q50 (sampling) · out/runs/loader-q50-q50-20261009T144517Z.json
- Deck/script wording: "four real quantum computers" = IBM Marrakesh, IQM Garnet, IQM Emerald, VTT Q50 (Q50 counted as
  run, not as a successful estimate). Slide 5 line "VTT Q50: 3 repeats 0.11–0.53 % (exact 0.125 %), calibration not
  yet stable"; slide 6 "Q50 ≥4 of 14 over 1-in-10: 31 % vs 10.9 % exact (Emerald 13.8 %)" · from the lines above

## Round-5 deck pass (Sat 10 Oct, deck freeze) · scripts/round5_numbers.py → out/round5_numbers.json unless marked
- **Snow ratio baselines.** Slide 5 / video / script §5 "snowy vs low snow: 3.05× on chip, 2.75× exact" = two-river
  North-cluster pair both over 1-in-50, calibrated 0.2494 / 0.0818 % vs exact 0.1933 / 0.0704 % (bootstrap 90 %
  2.59–3.63) · qae-iqm / exact · product-iqm-emerald-20261009T075338Z (job 01a11fa8-65a9-74bf-bb38-95a59537f9fc).
  **Snowy vs normal on the same pair: chip 1.51×, exact 1.55×** (slide 5 chart title, QA) · qae-iqm / exact.
  Slide 3 / script §3 "triples" is a different measure: North ≥2 of 5 cover, snowy (top-15 %) March 6.4 % vs the
  autumn (normal) 1.96 % = 3.3× (90 % 2.1–4.4×) · exact (round-4 bootstrap)
- **Slide 3 headline "Expected loss ≈1.8× a model with the 2027 matrix's average correlation (0.27)"** = 1.96 % / 1.11 %
  (round-3 line), a model comparison; "fair price" wording dropped · exact
- **Slide 7 basis risk "1-in-10 back-test: paid in loss springs 1966, 2005, 2018; missed Ostrobothnia 2012–13, 2024 and
  Lapland 2020; since 2005 also paid in 3 North springs with no recorded loss (2015, 2023, 2024)"**: known loss
  springs = business case §1 table (outside source). 1-in-10 triggers in a cluster with no recorded loss there:
  Ostrobothnia 1965, 1966, 1971, 1972, 1974, 1977, 1984, 2000; North 1981, 1993, 2000, 2015, 2023, 2024;
  Satakunta–SE 1984, 1988 (14 springs; pre-2005 loss records are sparse). Footnote "at 1-in-50 the back-test paid
  1966, 2005, not 2018"; at 1-in-50 also Ostrobothnia 1984, 2000 with no recorded loss. Replaces the round-4 "2024
  (snow flag on: a false alarm)" wording: 2024 Ostrobothnia is a missed loss (snow flag on, no trigger); 2024 North
  paid with no recorded Lapland loss · exact (counts) · out/backtest.json
- **Amplification, one statement (slide 9, PITCH, QA, out/HARDWARE_RESULTS.md):** signal kept at k = 1 in the runs
  shown: Emerald 0.56–0.59 (075338Z), IBM / Garnet 0.77–0.78 (run 2: 174523Z / 182534Z), VTT Q50 0.12–0.19 (three
  repeats); earlier runs 0.65–0.88 (IBM run 1 0.65, Garnet run 1 0.66, Emerald 073815Z 0.77–0.88). Supersedes "≈0.5 on
  Emerald, 0.6–0.8 on IBM / Garnet" · qae-ibm / qae-iqm / qae-q50 · out/runs/*.analysis.json
- **Slide 9 job IDs:** Emerald snow ratio 01a11fa8-65a9-74bf-bb38-95a59537f9fc; Emerald control
  01a120f5-ece7-73ff-bcf9-f4e4ba3069d3. Footnote "not shown: first runs IBM 0.146 % (k = 0–3), Garnet 0.073 % (1 copy)"
  = noise-aware MLAE of ibm-ibm_marrakesh-20261008T170341Z (job db3sssqmb58s7388bb00, 25 copies) and
  iqm-garnet-20261008T182125Z (job 01a11cbf-bb06-7672-a667-c85255613143, 1 copy); exact 0.125 % · qae-ibm / qae-iqm
- **Slide 6 chart out/pitch_scaling.png** now also plots the three VTT Q50 repeats (18,000 model evaluations each; abs.
  error 0.34 / 0.41 / 0.018 pp, the last one near exact by luck) from out/runs/q50-*.analysis.json; label "IBM, IQM &
  VTT chips today"; y-axis extended to 1 pp · qae-q50
- Slide 7 buyer "Finnish home insurers: OP, If, LähiTapiola, …" = docs/flood_terms_check.md (seven home insurers).
  "Insurers with their own approved (internal) model, like If" = Sampo partial internal model (business case);
  OP's model type not documented, so not claimed. Licence arrow: insurer → Tulva; premium arrow: insurer → reinsurer
  · source
- QA "Isn't the market tiny if each insurer pays €75k?": ~6 insurers × €75k < €0.5M/yr (assumption); losses per event
  ≈ €5–20M (business case §1 table); premium ≈ €0.5–0.7M/yr per €10M North layer (pricing section above); parametric
  market $3.5bn to $18–21bn, 12–14 %/yr growth (business case §Market size, outside sources, quoted as a range);
  expansion to SE/NO/Alps/Canada/Red River unsized · assumption / source
- QA staged payout: reframed as a variant (costs 67 % of the full North "≥2" cover, pricing section above), not the
  product; the "reduces basis risk" claim is dropped (untested)
- Demo video re-recorded (round 5), 36.7 s, same cue times: 0 s caption "Our app: lines join rivers that flood
  together"; 18 s "Snowy vs low snow: about three times the risk, close to exact." (= 3.05× vs 2.75×) · qae-iqm ·
  deck/video/record_demo.mjs


## Out-of-sample snow test · scripts/oos_snow_test.py → out/oos_snow_test.json, out/OOS_SNOW_TEST.md
Everything fitted (GEV 1-in-10 levels, normal-score transforms, loadings, snow skill, top-15 % cut-off) on the
training springs only, then frozen. Trigger = ≥2 of cluster over frozen GEV 1-in-10. Both splits reported.
- **Fit 1961–2000, test 2001–2025: Spearman(March snow, cluster flood index) out of sample Ostrobothnia 0.69
  (90 % 0.42–0.84; in-sample 0.65), North 0.75 (0.53–0.87; in-sample 0.24), Satakunta–SE 0.33 (−0.05–0.65; in-sample
  0.62)** · exact (rank correlation) + year bootstrap
- Same split, flag vs trigger: the 1961–2000 cut-off fired only **2 of 75** cluster-years after 2000 (snow lower);
  pooled **1 of 2 flagged vs 7 of 73 unflagged springs paid** (Fisher p 0.20) → the snow risk ratio is **not testable**
  on 2001–2025. Ostrobothnia and Satakunta–SE had no trigger at all (Ostrobothnia gauge-years over old 1-in-10: 0.7 %).
  Frozen-model expectation 0.7 / 5.6 payouts · exact (counts) + Clopper-Pearson
- Predicted flagged-vs-unflagged ratio from the 1961–2000 fit: Ostrobothnia 5.2×, North 2.1×, Satakunta–SE 7.8×;
  North "triples" analogue (≥2 of 5 over 1-in-50, snowy vs normal) **2.3×** (full-record fit 3.3×), North skill 0.31
  (full record 0.47) · exact (quadrature)
- **Reverse split (fit 1986–2025, test 1961–1985): pooled 12 of 24 flagged (50 %) vs 4 of 51 unflagged (8 %) springs
  paid, ratio 6.4×, Fisher p 0.0001** (model expected 8.1 / 3.6); Ostrobothnia 8/10 vs 3/15 (p 0.005), Satakunta–SE
  4/11 vs 0/14 (p 0.026), **North fails: 0/3, Spearman −0.14** · exact (counts)
- Sensitivity (trailing-30-spring cut-off): main 2/11 vs 6/64 (p 0.33), reverse 9/20 vs 7/55 (p 0.005) · exact
- Reading: the snow→joint-flood ranking survives on unseen years in 4 of 6 cluster tests; the size of the effect
  ("triples") is not confirmed on recent years (too few flags); per-cluster skill is unstable (North 0.31 vs 0.70 by
  fit period); a fixed snow cut-off is not stationary. Pooled p-values optimistic (clusters share years).
### Spring 2026 out-of-sample check (Vaishnav, 9 Oct) · scripts/season_2026.py → web/data/season2026.json
Model fitted on 1961–2025 only; 2026 snow (SYKE LumiAlue, 1 March) and Mar–Jun 2026 discharge (SYKE Virtaama, SMHI
16722) fetched 9 Oct 2026 (provisional values).
- 1 March 2026 snow, cluster index percentile among 1961–2026: Ostrobothnia **8th**, North **45th**, Satakunta–SE
  **10th** · data
- Said on 1 March (exact, conditioned on that percentile): P(≥2 over 1-in-10) Ostrobothnia 0.4 % (average year
  15 %), North 9.3 % (12.7 %), Satakunta–SE 0.4 % (5.9 %); payout chance (≥2 over 1-in-50) 0.01 % / 0.98 % / 0.01 %
  (average 2.56 / 1.96 / 0.62 %); expected areas over 1-in-10: 0.03 / 0.39 / 0.06 · exact
- What happened: **0 of 14 areas passed their empirical 1-in-10 level; 0 passed 1-in-50; no payout.** Peaks were
  24–55 % of the 1-in-10 level (Rovaniemi 494 m³/s on 18 May = 37 %) · data (counts)

## Stage-deck pass (Sat 10 Oct): slides 1–8 simplified, details to backup slides 9–11
No new numbers; every on-slide number is one already logged above. Wording mapping:
- Slide 1 "May 2005: four Lapland rivers flooded together" = Ivalo, Kittilä, Rovaniemi, Tornio over their 1-in-10
  flow level; "The March snow warned us" = North 1 March snow in its top 15 %, in-sample (backup 9, QA).
- Slide 2 "15.4 %" vs "3.9 %", "≈4× as often as chance" = ≥4 of 14 areas over 1-in-10, observed vs independence on
  the same gauge-years (3.9×, round-3 lines) · exact.
- Slide 3 bars 1.11 % / 1.96 % / 6.4 % = expected loss, North "≥2 of 5 over 1-in-50": one 0.27 correlation, Tulva,
  after a snowy (top-15 %) March; "×3 expected loss after a snowy March" = 6.4 / 1.96 = 3.3× ("triples") · exact.
  Intervals (1.6–2.2 %, 3.6–9.1 %, 2.1–4.4×) on backup 9.
- Slide 5 "3.05× on chip, 2.75× exact, snowy vs low-snow March" = IQM Emerald calibrated vs exact (two-river pair);
  bars = out/bootstrap_ci.json "emerald snow low/high"; "Ran on IBM · IQM · VTT Q50" = hardware runs above.
  CI 2.6–3.6 and job ids on backup 11 · qae-iqm.
- Slide 6 chart out/stage_scaling.png = out/pitch_scaling.png data with labels only (scripts/pitch_charts.py
  scaling_chart_stage) · monte-carlo / qae-sim / qae-ibm / qae-iqm / qae-q50.
- Slide 7 "€25k pilot, then €75k / yr", "Year 3: €0.2–0.45M / yr", "3–6 Finnish insurers, then the Nordics" =
  slide-7 revenue line above · assumption. Premium per €10M layer, back-test years, why now, market size: backup 10.
- Slide 8 "Runs on 4 quantum chips" = IBM Marrakesh, IQM Garnet, IQM Emerald, VTT Q50.

## Animated demo video (Fri 9 Oct, candidate for slide 4, not yet in the deck) · deck/video/anim/ → deck/video/tulva_demo_anim.mp4
43.97 s, ElevenLabs voiceover (deck/video/anim/narration.md) + burned-in captions. No new numbers; each one below is
an existing claim, read by deck/video/anim/export_data.py (which asserts the spoken values) or shown live in the app.
- Map, 2005: 4 of 14 areas over their empirical 1-in-10 level (Ivalo 142 %, Kittilä 124 %, Rovaniemi 112 %, Tornio
  101 % of it); North 1 March snow 87th percentile (top 15 %); fine print "back-test, not a forecast made in 2005";
  "two months later" = 1 March → May peak · data · web/data/app.json (slide-1 / "Pitch hook" / 2005-replay lines above)
- App recording: North "≥2 of 5 over 1-in-50", no outlook 2.0 % (1.96 %) → high-snow March 6.4 %; spoken "from two to
  six point four percent" · exact · the live app (pricing / round-3 lines above)
- Chip: IQM Emerald shot grid, both-flood 13 (low snow) → 31 (snowy) of 8,000; "about three times the risk on the chip,
  2.75 exact" = calibrated 3.05× (90 % CI 2.6–3.6, 240,000 shots per case) vs exact 2.75× · qae-iqm / exact ·
  web/data/pipeline.json, out/bootstrap_ci.json (round-5 line above)
- "We ran it on IBM, IQM and Finland's VTT Q50" = IBM Marrakesh, IQM Garnet, IQM Emerald, VTT Q50 (Q50 run, not a
  successful estimate; card fine print "checked against exact classical values · classical computers still win today ·
  no quantum advantage claimed") · VTT Q50 section above

### VTT Q50 follow-up, 4-gate test with 10× shots (Fri 9 Oct ~17:26 UTC, run by Claude over SSH; mentor's suggestion)
- Same two-river North-cluster pair, k = 0 only (4 two-qubit gates), 20,000 shots per circuit, 3 repeats ·
  qae-q50 · out/runs/q50-20261009T172553Z / 172654Z / 172753Z (.json + .analysis.json) · jobs 78907767-09a3…,
  d9f63642-5b84…, 62070116-faa9… · scripts/run_hw.py --ks 0 --shots 20000, scripts/analyse_run.py
- Raw 0.659 / 0.680 / 0.715 %; zero-calibration offset 0.39 / 0.34 / 0.32 %; gain 0.99 / 1.07 / 1.04;
  calibrated 0.273 / 0.317 / 0.380 % vs exact 0.125 %.
- Reading: with 10× shots the repeats agree (spread 1.4×, was 5× at 2,000 shots, where the zero-calibration circuit
  caught only 4–12 hits). But all three stay ~2–3× high: on Q50 the zero-calibration circuit does not capture all
  of the error (raw 0.66–0.72 % vs calibration 0.32–0.39 %), unlike IBM (+19 %) and IQM Garnet (+31 %).
  Not on the main slides (deck frozen); QA only.
