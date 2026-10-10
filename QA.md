# Q&A drill (shared)

Practise out loud, both directions. Answer in about 20 seconds: accept the premise, give one number, reframe.
Technical questions → Toivo. Business questions → Vaishnav. All numbers are from CLAIMS.md.

## Explain the circuit without notes (Toivo, 30 seconds)
"One qubit is this spring's hydrology: wet or normal. Its probability comes from the March snow. Two more
qubits are two northern rivers (a North-cluster pair: both get the North cluster's average numbers, so it is not
Kittilä and Ivalo specifically); each floods with a probability that depends on the hydrology qubit, and that shared
dependence *is* the correlation. The event 'both flood' is marked with a single CZ gate. Amplitude estimation then
repeats a 'reflect' step to amplify that event and reads out how fast it grows; the growth rate gives the
probability. We run it at 0, 1 and 2 amplification steps and fit the answer by maximum likelihood."

## By juror

**Väinö Mehtola (VTT, hardware):**
- *"What's your noise budget?"* About 50 two-qubit gates. Our 3-qubit circuit is 4 / 23–29 / 42–53 gates for
  0 / 1 / 2 steps; the 4-qubit version passes 60+ and on IBM loses almost all signal. That's the measured limit.
- *"How does your error mitigation work?"* In the same job, on the same qubits, we run two calibration copies
  of the circuit with known answers (one large, one ≈ 0). They give each step's surviving signal and false-positive
  offset, and we invert that. On IBM it moved 0.262 % → 0.149 % (exact 0.125 %).
- *"How did Q50 do?"* (honest, ~25 s) "We ran it on Friday through LUMI, same code, one flag. Three repeats of the
  two-river circuit gave 0.47, 0.53 and 0.11 % against an exact 0.125 %. So not reproducible yet: the one close to
  exact was luck. The cause is our zero-calibration circuit: its offset moved between repeats, 0.002 to 0.006, and
  with 2,000 shots that swings the answer. One Grover step kept only 0.12 to 0.19 of the signal; in the runs we show,
  Emerald kept 0.56 to 0.59, IBM and Garnet 0.77 to 0.78. Our 18-qubit, 14-river sampler read 31 % for four or more rivers, exact 10.9 %,
  Emerald 13.8 %. Next we'd try: many more shots on the calibration circuits, the best-qubit layout with several
  copies (our 4-copy job ran but we couldn't retrieve the result), and error mitigation through FiQCI's tools."
  (Numbers: CLAIMS.md "VTT Q50", out/HARDWARE_RESULTS.md. Readout flips on that run: 2.1 % / 3.4 %.)
  - Feedback for VTT, if asked: "Getting to Q50 needed `module use /appl/local/quantum/modulefiles/hackathon/`
    before loading the modules; a line in the QuickStart would save the next team an hour."
  - Earlier answer, now superseded: on Thursday Q50 had the cryostat issue and our LUMI account was still syncing,
    so the first results are from IQM Garnet and Emerald.
- *"State loading kills the speed-up."* Not for a factor model: one qubit per area, each needing one RY and one
  controlled RY, so it's linear in the number of areas. A two-level version of our 14-area model fits on 18 qubits
  with 44 two-qubit gates (sampled on Emerald).
- *"When would this beat Monte Carlo?"* On ideal hardware the error falls like 1/N vs 1/√N (our simulation
  shows it). It needs fault tolerance, and an expensive model per scenario (a hydrological simulation, many
  perils), not our nanosecond toy. (The ~8k logical qubits figure is for derivative pricing, see below.)
- *"Is there advantage today?"* No, and we say so. At the same budget Monte Carlo is within ±0.004–0.006 pp.

- *"Why quantum and not a supercomputer?"* (mentor feedback) "Today a supercomputer wins: it's classical sampling,
  just faster. Amplitude estimation's advantage is against any classical sampler, supercomputers included:
  quadratically fewer model runs for the same precision. That pays off when each scenario is expensive, such as a
  full hydrological simulation or multi-peril repricing every day, and rare joint events need many runs.
  Fault-tolerant hardware has to arrive first."
- *"Did the snow signal survive on hardware?"* Yes. On IQM Emerald the snowy-vs-LOW-snow risk ratio was 3.05×
  (bootstrap 90 % CI 2.6–3.6) against 2.75× exact (two-river North-cluster pair, 240k shots each). The interval contains the
  exact ratio.
- *"What breaks?"* Rare events: the 14-area circuit at the 1-in-50 level read 16 % vs 4.8 % exact. Gate noise creates
  false triggers that swamp rare signals, which is exactly why this needs error correction.

**Niklas Steinmann (IQM):**
- *"Why Qrisp?"* We wrote the circuit natively in Qrisp, compiled it with IQM's pass manager (fewer gates than
  Qiskit's transpiler: 23 vs 28 at one step) and ran it on Garnet. Same raw result as the Qiskit version.
- *"Garnet vs Emerald?"* Garnet (20 qubits) for the deep amplitude-estimation circuits, Emerald (54) for the
  wide 14-area model. Emerald's readout error was only about 0.5 %.

**Teppo Seesto (IBM):**
- *"How did you use Runtime?"* SamplerV2 in batch mode with dynamical decoupling (XY4) and gate twirling. We put
  20–25 copies of the circuit side by side on Marrakesh's 156 qubits: 25× the shots for the same time (36 s
  of the 10-minute budget), and a map of qubit quality across the chip.
- *"Why best qubits?"* We pick qubit groups from today's calibration data. It cut the copy-to-copy spread from
  0–2.95 % to 0.10–0.45 %.

**Shahab Anbarjafari (PwC, AI and explainability):**
- *"Is it explainable?"* The trigger is a public SYKE gauge level anyone can check, and the model's parameters are
  physical (how strongly a region's rivers move together, how much the snow matters). No black box.
- *"Basis risk?"* The cover pays on gauges, not on the insurer's claims. The product pays the full limit at ≥2 gauges
  (that is what slide 3 prices). The back-test: a "≥2 gauges" trigger paid in 2005 when Lapland flooded. We'd fit the
  gauge choice to each buyer's exposure. A staged payout (50 % at 2, 100 % at 3) is a possible variant, not the
  product: it costs 67 % of the full North cover; we have not tested whether it lowers basis risk. Not yet tested
  against claims: that is step one of the pilot (postcode claims for 2005, 2018, 2024).
- *"Does the snow signal work?"* At the 1-in-10 level, the 1 March snow flag caught 11 of 19 payout years in advance, and no payout
  followed a low-snow March. That's in-sample with a small sample, and we say so.

## Business (Vaishnav)
- *"Who buys, and why?"* An insurer buys it for the joint spring-flood loss it retains; a reinsurer carries the
  risk. It's priced and sold in autumn, ahead of the 1 January renewal; the March snow update then tells the insurer
  how much joint risk sits on its own books (claims readiness, capital, next season's price). An index cover pays
  fast, with no claims adjustment.
- *"What does it cost?"* As rate on line (market premium as % of the limit per year), North "≥2 of 5 over
  1-in-50": Tulva 4.9–6.9 %; with the 2027 matrix's average correlation (0.27) 2.8–3.9 %; priced as independent
  1.0–1.3 %. Per €1M of cover that is ~€49–69k a year. After a snowy March the expected loss triples vs autumn
  (1.96 % → 6.4 %), but nobody
  re-prices the autumn cover then: the insurer buys a top-up / second layer if it wants one, staffs claims and uses
  the number in its ORSA.
- *"Your payout is bigger than Finnish flood losses."* "The €10M in the app is only an illustration. The limit is sized from the
  insurer's own claims in the pilot, so the price is a rate: 4.9–6.9 % of whatever limit fits its book."
- *"Isn't the Finnish market tiny?"* See "Isn't the market tiny if each insurer pays €75k?" in the Round 5 section
  (Finland is the proof market). For scale, rain-driven Nordic/European events: Gävle 2021 SEK 1.9bn, storm Boris
  €2.15bn insured.
- *"Do you get capital credit?"* "Under the Solvency II standard formula, an index cover likely gets no capital
  credit (EIOPA Q&A 1597: basis risk can't be haircut there). The value is basis-risk-managed protection of the
  retained loss, plus credit under internal models, where basis risk can be modelled."
- *"Won't sellers just raise the price after a snowy March?"* Yes, that's why it's sold in autumn, ahead of the
  1 January renewal. The price is fixed in autumn; the March update tells the insurer how much joint risk it holds.
  Tulva is the index and pricing engine for whoever carries the risk.
- *"Why now?"* From January 2027 Solvency II charges capital for Finnish flood with fixed correlations: 0 % to
  SE/NO/DK (EIOPA considered 25 % for snowmelt floods and rejected it) and a fixed 19-zone matrix inside Finland (mean
  ≈ 0.27). None of them react to this winter's snow. Insurers must also include climate scenarios in ORSA.

## New jury questions (research/18)

- **Steinmann / Mehtola: "Your 14-area chip result is sampling. Did amplitude estimation run on the full model?"**
  "No, and that's deliberate. Emerald shows a two-level version of the 14-area loader fits: 18 qubits, 44 gates. Amplitude estimation adds
  two loader copies per step, which at 14 areas is far past today's ~50-gate budget. So we ran it on the 3-qubit
  two-river North-cluster pair on IBM Marrakesh, IQM Garnet and Emerald, and VTT Q50. The loader is the part that has to scale, and it scales linearly."
- **Mehtola: "Your calibration circuits have known answers. Isn't the mitigation tuned towards the result you
  wanted?"** "The calibration circuits have *different* known answers, one large and one near zero, never the
  target value. They measure how much signal survives each step and the false-trigger floor, in the same job and
  on the same qubits. We invert that, and only afterwards compare with exact. Raw numbers are on backup slide 11 next to
  the calibrated ones."
- **Toikka: "Do 1961–2025 data hold as winters warm?"** "Not fully. Spring floods are shrinking and coming
  earlier, fastest in Ostrobothnia; Lapland is roughly stable to about 2050; rain and winter floods grow (SYKE/FMI,
  Veijalainen 2010). So the model must be re-fitted on recent decades and conditioned on climate scenarios; that's
  on our roadmap. Today the price already moves with *this* winter's snow, not the 65-year average." (Sources:
  business/NOTES_FOR_TOIVO.md.)
- **Toikka (OP as buyer): "Who sells us this, and why not just buy more treaty reinsurance?"** "A reinsurer or an
  ILS fund that wants Nordic diversification sells it at the 2.5–3.5× multiple we priced. It doesn't replace your
  treaty. It fills the gap the treaty can't: the correlated spring layer you retain, priced jointly in autumn and
  paid in days off a public gauge. We are the index provider and calculation agent, paid by licence: €25k pilot,
  then ~€75k a year per insurer (assumption)."
- **Anbarjafari: "The theme is AI × quantum. Where is the AI?"** "Honestly: the product's early-warning signal is
  statistical, snow index to risk shift, because an insurer has to defend the trigger to a regulator. We built it
  with AI coding agents (Claude Code). The next step is an ML seasonal forecaster: snow plus soil moisture plus
  ECMWF seasonal forecasts."

## Review fixes (Fri 9 Oct evening): the hard questions

**Technical (Toivo)**
- **"Which number did a QPU compute?"** "None of the prices. Every price we quote is computed classically, exactly.
  The QPUs ran the pipeline end to end: a two-level version of our 14-area model on IQM Emerald and VTT
  Q50, amplitude estimation on IBM Marrakesh, IQM Garnet and Emerald and VTT Q50, and the snow effect on Emerald. They show where today's hardware stops. Quantum is our R&D track."
- **"How do your calibration twins scale?"** "Today they validate the noise model: circuits of the same shape with
  known answers, run in the same job. At scale we'd use twins that are classically trivial to compute, for example
  product states, so the known answer never needs the hard simulation."
- **"What's the confidence interval on 0.149 %?"** "Bootstrap 90 %: IBM 0.149 % (0.140–0.157), IQM Garnet 0.164 %
  (0.147–0.180), exact 0.125 %. Both intervals exclude the exact value, so the remaining +17–31 % is a systematic
  bias, not shot noise. Across all our calibrated runs the error ranges from −42 % to +37 %; raw readings were 2–3×
  off."
- **"Did the noise create your fat tail?"** "Partly, and we measured it. We ran the identical 18-qubit circuit with
  correlations switched off. ≥4 of 14 areas: independent exact 4.4 %, chip 9.7 %; correlated exact 10.9 %, chip
  13.8 %. So noise alone roughly doubles the tail. But chip vs chip, the correlated model still gives 1.4× (≥4),
  2.4× (≥5) and 4× (≥6) more multi-area floods. The correlation survives, weakened by noise."
- **"Doesn't this need 8,000 logical qubits?"** "That number is for derivative pricing (Chakrabarti et al. 2021).
  Our circuits are few qubits but deep: 3 qubits for the two-river pair. The bottleneck is a coherent hydrology oracle,
  a flood model evaluated inside the circuit, and the circuit depth that needs."
- **"Two-level circuit vs your continuous model?"** "The circuits use a two-level version of the factor model (wet
  spring or not). For ≥4 of 14 areas over 1-in-10 it gives 10.9 % vs 12.2 % for the continuous model (observed
  15.4 %). The continuous model is the classical reference and the one we price with."

**Business (Vaishnav)**
- **"Who signs as risk carrier?"** "A reinsurer. We are the index provider and calculation agent, like PERILS for
  industry-loss indices, paid by licence: a €25k pilot, then ~€75k a year per insurer (team assumption)."
- **"2005 was about €5M market-wide, below any retention. Why buy?"** "The value is not one river in one year. It's
  the multi-region spring that the treaty doesn't price by snow. The limit is sized from the insurer's own claims in
  the pilot, not from our illustration."
- **"Basis risk?"** "Not tested yet, and we say so. It's step one of the pilot: the insurer's postcode-level claims
  for 2005, 2018 and 2024 against our gauge triggers give a basis-risk map before anything is sold."
- **"What does OP do with the March signal?"** "Claims staffing in the regions at risk; on the bank side, a watch
  on agricultural and mortgage collateral there; and a top-up quote for extra cover if they want it."
- **"Regulated rivers, Kemijoki or Kokemäenjoki?"** "Hydropower regulation changes discharge. The index would use
  gauges on unregulated tributaries, or water levels instead of flow. That is to be tested in the pilot."

## Round 2 (Sat 10 Oct): the sharper questions

- **"Against realistic correlation, how under-priced is it?"** (Toivo) "Its expected loss is about 1.8× a model with
  the regulator's average correlation of 0.27: 1.96 % vs 1.11 % for '≥2 of 5 North' (round-3 recomputation; the earlier 1.09 % was an
  unreproduced Monte Carlo). The 5× is only against independence. The bigger value is
  the snow update: a snowy March moves the same cover's expected loss about ×3 vs autumn."
- **"Your circuit's exact answer is 1.10 %, but you price 1.96 %?"** (Toivo) "Yes. The circuit uses a two-level
  version of the model, wet spring or not, and that loses 44 % at the 1-in-50 level. More latent qubits per factor fix
  it, at linear gate cost. The prices come from the continuous classical model, not from the chip."
- **"How much of your estimate comes from amplification (k ≥ 1)?"** (Toivo) "Little, today. Signal kept at k = 1 in the runs shown:
  Emerald 0.56–0.59, IBM / Garnet 0.77–0.78, VTT Q50 0.12–0.19 (earlier runs 0.65–0.88); at k = 2 Emerald 0.44,
  IBM / Garnet 0.60–0.69. And
  the false-trigger offset, 2–6 %, dwarfs the 0.1–0.2 % we measure. So it's mostly a calibrated k = 0 estimate. That
  is exactly the gap error correction has to close."
- **"2024: Ostrobothnia flooded, the snow flag was on, the index didn't pay. Basis risk?"** (Vaishnav, Toivo backs up)
  "Yes, that's the honest case: a missed loss. In 2024 only one of six Ostrobothnia gauges passed its 1-in-10 level;
  four peaked at 95–97 %. In back-test terms the snow flag was a false alarm (flag on, no trigger), one of six for
  that cluster; for the insurer it is a miss. The same spring the North index paid without a snow flag, and Lapland
  had no recorded loss (Ivalojoki stayed below the damage limit): a payout without a known loss. That's why the pilot fits the gauge choice to each insurer's own claims. And no
  payout has ever followed a low-snow March."
- **"Why pay 5–7 % rate on line with no standard-formula capital credit?"** (Vaishnav) "It protects earnings on the
  correlated spring layer below the treaty, and it's ORSA evidence on joint flood risk. Under an internal model, like
  If's, it can be credited. Per €1M of cover it's about €49–69k a year."
- **"Vendor models already include snowmelt (RMS)."** (Toivo) "As far as we can see from public documentation, they
  average over simulated winters; we couldn't check every vendor, so we don't claim none does. Tulva re-states the joint
  risk from this March's measured snow, before the melt."

## "What did you do before the event?" (answer honestly, calmly, ~15 s)
"Before the event we did research: we read up on Finnish floods, insurance and reinsurance, found the public data
sources (SYKE, FMI), and studied which quantum methods fit risk pricing, and that QAOA didn't fit while amplitude
estimation does. All the code, the data analysis, the model, the pricing, the hardware runs and the demo were built
here, from Thursday 18:00. Our commit history starts then."
- If they dig deeper: "We also sketched rough feasibility simulations to decide on the method, but we rebuilt
  everything from scratch here with real data. Nothing from that was reused."
- Don't apologise or over-explain. Research before a hackathon is normal and expected; the pitch-training slides
  even ask for "progress – pre-event and during the event".

## "Your first commits are huge" (~10 s)
"We build with AI coding agents; the first scaffolding and data download landed minutes after 18:00, as the
history shows."

## Traps
- Never say "quantum is faster" or "advantage".
- Never claim "EIOPA assumes 0 % in Finland". The 0 % is cross-border (FI–SE/NO/DK); inside Finland EIOPA uses
  a 19-zone matrix.
- If you don't know: "Good question. We didn't test that during the hackathon; here's how we would."

## Round 3 (Sat 10 Oct): what came off the slides, and the hardware juror's questions

- **"Slide 2 says chance is 3.9 %, your hardware table says 4.4 %. Which?"** (Toivo) "Both are code, different
  baselines. 35 gauge-years are missing, so in many years fewer than 14 gauges could flood. The like-for-like chance
  for the observed 15.4 % uses each year's actual gauges: 3.9 %, so 3.9×. If all 14 reported every year it is 4.4 %
  (3.5×); that is the circuit's independent case. 10 of 65 springs has a 90 % interval of 9–24 %, so even the low
  end is 2.4× chance."
- **"The video shows 2.8×, slide 2 shows 3.9×."** "Different questions. 2.8× is per pair: two rivers of one cluster
  both over 1-in-10 in the same spring, vs chance. 3.9× is per spring: four or more of all 14 areas at once."
- **"The shot grid shows 13 vs 31 red squares. Is that the 3×?"** "No. That grid is one 8,000-shot sample, raw.
  Across all 240,000 shots per level the raw ratio is only 1.3×, because noise adds a floor of false 'both flood'
  shots. After the calibration circuits remove that floor it is 3.05× (90 % CI 2.6–3.6) vs 2.75× exact."
- **"Did deep amplitude estimation work?"** "No. We ran shallow amplitude estimation, Grover steps k = 0–2 in the results we show (one early IBM run went to k = 3). The signal
  fades with every step on today's chips (signal kept at k = 1 in the runs shown: Emerald 0.56–0.59, IBM / Garnet
  0.77–0.78, VTT Q50 0.12–0.19; earlier runs 0.65–0.88), so the estimate is mostly a calibrated k = 0 reading. The
  3-qubit two-river North-cluster core ran it on IBM Marrakesh, IQM Garnet and Emerald, and VTT Q50; the simplified
  14-river loader only sampled, on IQM Emerald and VTT Q50."
- **"What are the intervals on slide 5?"** (backup slide 11) "IBM Marrakesh 0.149 % (0.140–0.157), IQM Garnet
  0.164 % (0.147–0.180), exact 0.125 %; raw 0.262 % / 0.368 %. Both intervals exclude exact: +19 % / +31 %
  systematic bias. The chart's chip is IQM Emerald; the table's are Marrakesh and Garnet."
- **"~18 qubits and ~50 gates work?"** "At the 1-in-10 level: the 18-qubit, 44-gate 14-river loader read 13.8 % vs
  10.9 % exact. At 1-in-50 the same circuit read 16 % vs 4.8 %: it fails. Rare events need error correction."
- **"Where does the ~8,000 logical qubits figure come from?"** (removed from slide 6) "Not ours: it's Chakrabarti et
  al. 2021's estimate for derivative pricing. We have no resource estimate for a hydrology oracle yet."
- **"Why ≈1.8× and not 2×?"** "1.96 % vs 1.11 % = 1.77×. We round to 1.8×, not up to 2×."
- **"Can anyone buy the cover at the snowy-March price (16–23 % rate on line)?"** "No, and the slide no longer shows
  it as a price. The cover is fixed in autumn. In March the insurer acts on the number: a top-up or second-layer
  cover if available, claims staffing, ORSA."
- **"Two rivers or four in 2005?"** "Four Lapland areas passed their 1-in-10 level: Ivalo, Kittilä, Rovaniemi and
  Tornio. Ivalo, Kittilä and Rovaniemi also passed 1-in-50. The 'snow warned us' line is an in-sample back-test: the
  North's 1 March snow was at the 87th percentile."
- **"Basis risk?"** (backup slide 10; said, not shown, on slide 7) "The index is not the insurer's own losses. It is mitigated because our trigger is
  the same 1-in-50 idea that all seven Finnish home insurers use in their flood terms (OP, If, LähiTapiola, Fennia,
  Turva, Pohjantähti, POP). It is the same idea, not the same test: the policies look at the water LEVEL at the
  insured site, certified by SYKE; we look at river DISCHARGE at a gauge against a fitted GEV 1-in-50 level. So the
  index and the policies need not switch on together. Turva's guide even lists an ordinary spring flood as not
  covered. Still to be tested against claims in the pilot."
- **"Revenue?"** "Assumption: €25k pilot, then ~€75k a year per insurer. 3–6 insurers × €75k = €0.2–0.45M a year by
  year 3. Finland first (open data, seven home insurers), then snowmelt regions in Sweden and Norway."
- **"No vendor model uses this winter's snow?"** (removed: we can't verify it) "We dropped that claim. What we can say:
  the 2027 standard-formula correlations are fixed and don't react to the snow."

## Round 4 (Sat 10 Oct): what came off the slides, and why

- **"A correlation matrix doesn't imply a price."** (Toivo) "Right, and the slide no longer says it does. We compare
  two models: ours, fitted to SYKE data, and the same model with one correlation of 0.27, the average of the 2027
  Finnish flood-zone matrix. Expected loss 1.96 % vs 1.11 % of the limit a year: 1.8×. The 0.27 is the mean of
  all 19 zones. We did not use the Lapland zones' own entries: we don't have the zone-to-region mapping (Annex IX)
  or the cell values in the repo, so we can't say whether they would move the ratio. If the Lapland zones are in a
  0.75–1.00 block, the gap would be smaller."
- **"How sure are the 1.96 % and the 'triples'?"** (Toivo) "Year-bootstrap, refitting the model and the snow skill on
  resampled springs: 1.96 % has a 90 % interval of 1.6–2.2 %; the snowy-March risk 6.4 % has 3.6–9.1 %, so 'triples'
  is 3.3× with 2.1–4.4×. In-sample snow skill, and we say so."
- **"What would the market charge?"** (moved off slide 3) "At the cat-bond / flood-ILS multiple of 2.5–3.5× expected
  loss: 4.9–6.9 % rate on line, ≈€49–69k a year per €1M of cover, ≈€0.5–0.7M a year for a €10M North layer. That
  premium goes from the insurer to the reinsurer; our licence is separate."
- **"What does the insurer do in March?"** (ORSA moved off slide 3) "Buys top-up or second-layer cover if available,
  staffs claims in the regions at risk, and uses the snow-conditioned number as evidence in its ORSA."
- **"Is the 3-qubit circuit really Kittilä and Ivalo?"** (Toivo) "No. Both rivers get the North cluster's average
  loadings and the same 1-in-50 trigger, so it's a two-river North-cluster pair. The app shows Kittilä's and Ivalo's
  real records as the story; the circuit is the cluster pair. Same for '≥2 of 3': three North-cluster rivers."
- **"How much did amplification actually do?"** "Little: it's calibrated sampling plus shallow amplitude estimation.
  Signal kept at k = 1 in the runs shown: Emerald 0.56–0.59, IBM / Garnet 0.77–0.78, VTT Q50 0.12–0.19 (earlier runs
  0.65–0.88). Most of the information comes from the calibrated k = 0 circuit."
- **"Does correlation survive on the 14-river chip run?"** "Attenuated. Chip vs the identical independent circuit on
  the same chip: 1.4× more ≥4-area springs; exact: 2.5×. Noise inflates both."
- **"Why now, if If uses an internal model?"** (Vaishnav) "Two buyers, two reasons. Standard-formula insurers get fixed
  2027 flood correlations that ignore this winter's snow: Tulva shows them the joint risk the rule doesn't see.
  Internal-model insurers, like If Insurance (Sampo's partial internal model), get a snow-aware joint-flood number to
  feed their own model, and can get capital credit for an index cover there. We don't know which other Finnish
  insurers use the standard formula; their SFCRs would say."
- **"Who are you talking to?"** "No one has signed anything. We'd like to pilot with OP, the largest writer; that is
  an aspiration, not an agreement."
- **"Basis risk, in numbers?"** "Back-test at the 1-in-10 level against the known flood-loss springs: the index paid in
  1966, 2005 and 2018; at 1-in-50 (the product level), in 1966 and 2005 only. It missed Ostrobothnia 2012–13 and 2024,
  and Lapland 2020 (Kemijoki at Rovaniemi is hydro-regulated; we use the Ounasjoki gauge). 2024 Ostrobothnia is a
  miss: the snow flag was on, the region flooded, but only one of six gauges passed 1-in-10. The other way round:
  since 2005 the North index also paid in 2015, 2023 and 2024 with no recorded Lapland loss. Over 1961–2025 the
  1-in-10 triggers fired in 14 springs with no recorded loss in that cluster, but loss records before 2005 are sparse;
  at 1-in-50, two (Ostrobothnia 1984, 2000)."
- **"Year 3 and beyond?"** "Assumption: 3–6 insurers × €75k = €225–450k a year. The Nordic snowmelt market (Sweden,
  Norway, with their own 2027 flood factors) is the upside; we haven't sized it."
- **"Slide 1 says rivers 'hit flood levels'. Damage?"** "Discharge, not damage: river flow over each gauge's 1-in-10
  level. 2005 losses were about €5M house damage (Helminen; Yle reported ~€17M on a broader definition)."

## Round 5 (Sat 10 Oct, deck freeze): two snow ratios, licence flow, market size

- **"Slide 3 says a snowy March triples the risk, slide 5 says 3.05×. Same thing?"** (Toivo) "No, two baselines. Slide 3
  is the product, five northern rivers: after a snowy March the expected loss is 6.4 % vs 1.96 % priced in autumn,
  3.3×, snowy vs NORMAL. Slide 5 is the two-river pair on the chip, snowy vs LOW snow: 3.05× on Emerald, 2.75× exact.
  Snowy vs normal on that pair is only about 1.5× (1.51× chip, 1.55× exact): the pair is a smaller, rarer event and
  low snow is a lower base. Slide 3 says 'after a snowy March', slide 5 'snowy vs low-snow March'; backup slide 9 has both." (out/round5_numbers.json)
- **"Who pays Tulva: the insurer or the reinsurer?"** (Vaishnav) "The insurer. It pays the premium to the reinsurer
  that carries the risk, and a separate licence to us for the index and pricing. The reinsurer pays us nothing in the
  pilot model."
- **"Isn't the market tiny if each insurer pays €75k?"** (Vaishnav, full answer) "In Finland, yes: about six insurers
  × €75k is under €0.5M a year, and Finnish spring-flood losses are single-digit to low-double-digit €M per event
  (business case §1: 1966 ≈ €10M, 2005 ≈ €5M house damage, 2012–13 ≈ €20M total). Finland is the proof market: open
  data and a new 2027 rule. Expansion: Sweden and Norway first (same snowmelt rivers, their own
  new 2027 flood factors, and the 0 % cross-border correlation is a blind spot for Nordic groups like If / Sampo);
  then other snowmelt basins such as the Alps, Canada and the Red River (direction, not sized). At scale the revenue
  is a per-deal fee from reinsurers and brokers on covers that carry about €0.5–0.7M a year of premium per €10M layer
  (CLAIMS), in a parametric market estimated at $3.5bn to $18–21bn, growing 12–14 % a year (estimates differ about
  six-fold; business case §Market size)."
  - Spoken version (~20 s): "Finland alone is small, under half a million a year. We know that. Finland is our proof
    market: open data and a new rule in 2027. The engine works on any snowmelt basin: Sweden and Norway next, then the
    Alps and Canada. At scale we'd earn per deal from reinsurers, not just licences."
- **"Is the payout staged?"** "No. The product pays the full limit when ≥2 of 5 northern gauges pass 1-in-50; that is
  what slide 3 prices. A staged version (50 % at 2, 100 % at 3) costs 67 % of it; it is a variant we could offer."

## Added Fri evening (Vaishnav)

- **"So what is the tool for, exactly?"** "Two numbers per region, every spring. One: how likely it is that many of
  an insurer's customers flood at once this spring (the joint-flood probability, updated from the 1 March snow).
  Two: what protecting against that would cost (the fair price of a reinsurance cover built on the Tulva Index).
  From those two, the insurer decides whether to buy reinsurance, how much, and at what price, and shows the
  number in its ORSA. It is about many claims at once, the insurer's accumulation problem, not about pricing a
  single house. Tulva never carries or pays the cover: a reinsurer does; we license the engine."
- **"What if the trigger fires but there is no flood?"** "The trigger *is* the flood: a gauge reading above the
  1-in-50 level, the same test all seven Finnish home insurers use to pay homeowners (docs/flood_terms_check.md),
  certified by SYKE's Flood Centre. 'Fires with no damage' can happen when defences hold or the flooded land is
  empty; then the insurer is paid without a loss, the reinsurer bears it, and that is priced into the premium. The
  reverse, damage without a trigger, is the insurer's basis risk; we reduce it with a multi-gauge trigger
  (≥2 of 5), the staged payout, and by testing the trigger against the insurer's own claims in the pilot."

## "Did you test the snow warning out of sample?" (Toivo, ~15 s) · CLAIMS.md "Out-of-sample snow test"
"Yes, both ways. Fit on 1961 to 2000, tested on the 25 springs since: March snow still ranks the flood years,
correlation about 0.7 in Ostrobothnia and the North. But snowpacks shrank, so the old top-15 % flag fired only twice,
too few to confirm 'triples'. Run backwards, flagged springs paid 50 % versus 8 %."
- If pushed: "Weak spots: Satakunta–SE drops to 0.33 after 2000, and the North fails the backwards test. So the
  direction holds, the exact size is in-sample, and a real flag needs a cut-off re-based to today's snow."
  (out/OOS_SNOW_TEST.md)


## Q50 follow-up (Fri evening)
- **"Is the Q50 spread just noise from deep circuits?"** "Partly. We re-ran only the 4-gate circuit with ten times
  more shots, three times. Now the repeats agree, 0.27 to 0.38 %, so the earlier 5× spread was mostly too few
  shots on the calibration circuit. But they're still two to three times above the exact 0.125 %: on Q50 our
  calibration circuit doesn't catch all the error yet, unlike IBM and IQM where we got within 20 to 30 %."
- **"Why was Q50 worse than IBM and IQM?"** "On the qubits we got, Q50 read a 0 as a 1 about 5 % of the time,
  against about 0.7 % on IBM and 1.6 % on IQM Garnet (measured from our zero-answer calibration circuits). Our
  answer is only 0.125 %, so a 5 % error floor has to be removed almost perfectly. Even a proper per-qubit readout
  correction leaves 0.27–0.36 %, so part of the error is correlated between qubits or depends on the state, which
  a simple calibration can't remove. Next: pick the best qubits from Q50's calibration data and use FiQCI's error
  mitigation." (Numbers: Claude's check on out/runs/q50-20261009T172*, ibm-ibm_marrakesh-20261008T1745*,
  iqm-garnet-20261008T182125Z; tensor-product readout inversion with p01 from the zero circuit, p10 0–3.4 %.)


## Mentor feedback (Fri evening)
Feedback: lead the business case with "buy extra cover in time"; home-insurance pricing in
March is weak (policies are bought all year round); be able to say what "preparing" means and how the automatic
(parametric) payout differs from ordinary reinsurance; quantify the quantum gain.

- **"What does 'preparing' actually mean for an insurer?"** "Four concrete things, before the melt: (1) buy extra
  reinsurance cover for this spring; (2) line up claims capacity in the risky regions: adjusters, drying and
  repair contractors; (3) warn customers by text to move belongings up and protect basements, which cuts claims;
  (4) set aside reserves and tell management early, instead of finding out when the claims arrive."
- **"How is your automatic payout different from ordinary reinsurance?"** "Ordinary reinsurance pays the insurer's
  actual losses, after every claim is assessed: that takes months and needs loss data. Ours pays on the river
  gauges: when the index triggers, the money comes in days, with no loss assessment and nothing to argue about. The
  catch is basis risk: the index can differ from the real losses. That's what the 8-week pilot measures."
- **"Why would a reinsurer sell top-up cover in March if it can see the snow too?"** "It will charge more after a
  snowy March, and that's fine: our index makes the price fair and transparent for both. The insurer's gain is
  getting cover in place before the melt instead of being caught unprotected."
- **"Don't customers just buy home insurance in March?"** "No, policies renew all year round, so we don't sell a
  March price to homeowners. The March number is for the insurer: extra cover and preparation."
- **"Quantify the quantum advantage."** "Classical Monte Carlo needs four times the samples for twice the accuracy;
  amplitude estimation needs only twice. On the ideal simulator, at the same 16,000 model evaluations, QAE's error
  was 0.011 percentage points against Monte Carlo's 0.027, about 2.5 times more accurate. On today's noisy chips
  that gain is lost; it needs error-corrected hardware." (CLAIMS: qae-sim, scripts/qae_sim.py)
- **"Does the model forecast years ahead?"** "No, one spring at a time: the 1 March snow forecasts the coming spring's
  melt, March to June."

## Deck round 6 (Sat) · new slide 5 "Our circuit: quantum amplitude estimation"
- **"What exactly is your circuit?"** (Toivo, point at slide 5, ~20 s) "Three qubits: the wet spring and two
  northern rivers. A is our flood model: one RY sets the chance of a wet spring; each river gets an RY plus a
  controlled RY, so its flood chance depends on the spring. A CZ marks 'both rivers flood'. One Grover step is: mark,
  undo A, reflect about zero, redo A. The method is quantum amplitude estimation in its maximum-likelihood form: we
  run 0, 1 and 2 Grover steps, no phase estimation, and fit the probability from the counts. On hardware we add two
  known-answer calibration circuits in the same job." (Figure: scripts/qae_circuit_figure.py; the circuit is
  instance A3_kittila_ivalo_both of scripts/run_hw.py, gates from src/tulva/quantum.py.)
- **"Why compare quantum to classical at all?"** "Because it's an honest experiment: the same probability problem,
  solved both ways. Classical exact and Monte Carlo are the reference; they tell us whether the chip got it right,
  where quantum stands today, and what has to improve, noise and depth, before it pays off."
- **"Did you try other feature maps, embeddings or input scaling?"** "In amplitude estimation the encoding isn't a
  free choice like in quantum machine learning. Each rotation angle is set exactly from a probability in our model,
  2·arcsin(√p), so the amplitude IS the probability. Scaling it would change the answer. What we tuned instead was
  calibration and circuit depth: how many Grover steps survive the noise."
- **"Why quantum here?"** (spoken on slide 5) "Pricing rare floods means estimating tiny probabilities. For twice
  the accuracy, sampling needs four times the runs; amplitude estimation only twice. That's the ideal scaling; our
  shallow runs on today's chips don't reach it, which is why classical still wins today (slide 7)."
- **"What is the 'standard assumption' on slide 3?"** "The 2027 Solvency II formula links Finnish flood zones with a
  correlation matrix; its average is 0.27. We priced our cover with that one average link: 1.11 %. Our snow-aware
  model gives 1.96 %, 1.8 times more."


## Late Friday additions
- **"Isn't this just Swiss Re FLOW?"** "FLOW pays a single company per day one river gauge is high. Ours protects
  an insurer against many customers flooding at once: several rivers in a region together, priced from 65 years of
  data, and updated from the March snow."
- **"€75k flat seems small. Why not a share of the premium?"** "The flat licence is the simple starting point for a
  pilot. At scale we'd add a small share of the premium on every cover written on our index, the way financial
  index providers earn. We haven't priced that share yet." (Assumption, not researched.)
- **"Who else could use the index?"** "Reinsurers directly, and later investors through a flood cat bond with our
  index as the trigger, like the UK's Flood Re did in 2025 (£140M)."
