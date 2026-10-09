# Q&A drill (shared)

Practise out loud, both directions. Answer in about 20 seconds: accept the premise, give one number, reframe.
Technical questions → Toivo. Business questions → Vaishnav. All numbers are from CLAIMS.md.

## Explain the circuit without notes (Toivo, 30 seconds)
"One qubit is this spring's hydrology: wet or normal. Its probability comes from the March snow. Two more
qubits are Kittilä and Ivalo; each floods with a probability that depends on the hydrology qubit, and that shared
dependence *is* the correlation. The event 'both flood' is marked with a single CZ gate. Amplitude estimation then
repeats a 'reflect' step to amplify that event and reads out how fast it grows; the growth rate gives the
probability. We run it at 0, 1 and 2 amplification steps and fit the answer by maximum likelihood."

## By juror

**Väinö Mehtola (VTT, hardware):**
- *"What's your noise budget?"* About 50 two-qubit gates. Our 3-qubit circuit is 4 / 23–29 / 42–53 gates for
  0 / 1 / 2 steps; the 4-qubit version passes 60+ and on IBM loses almost all signal. That's the measured limit.
- *"How does your error mitigation work?"* In the same job, on the same qubits, we run two calibration copies
  of the circuit with known answers (one large, one ≈ 0). They give each step's surviving signal and false-positive
  offset, and we invert that. On IBM it moved 0.262 % → 0.148 % (exact 0.125 %).
- *"Why not Q50?"* It was down (cryostat) and our CSC access is still being fixed; we ran IQM Garnet and Emerald,
  which use the same architecture.

**Lauri Toikka (OP, physicist):**
- *"State loading kills the speed-up."* Not for a factor model: one qubit per area, each needing one RY and one
  controlled RY, so it's linear in the number of areas. All 14 areas fit on 18 qubits with 44 two-qubit gates (run
  on Emerald).
- *"When would this beat Monte Carlo?"* On ideal hardware the error falls like 1/N vs 1/√N (our simulation
  shows it). It needs fault tolerance: published estimates for comparable pricing are about 8,000 logical qubits
  (Chakrabarti et al. 2021). It also needs an expensive model per scenario (a hydrological simulation, many
  perils), not our nanosecond toy.
- *"Is there advantage today?"* No, and we say so. At the same budget Monte Carlo is within ±0.004–0.006 pp.

- *"Why quantum and not a supercomputer?"* (mentor feedback) "Today a supercomputer wins: it's classical sampling,
  just faster. Amplitude estimation's advantage is against any classical sampler, supercomputers included:
  quadratically fewer model runs for the same precision. That pays off when each scenario is expensive, such as a
  full hydrological simulation or multi-peril repricing every day, and rare joint events need many runs.
  Fault-tolerant hardware has to arrive first."
- *"Did the snow signal survive on hardware?"* Yes. On IQM Emerald the snowy-vs-low-snow risk ratio was 3.1× against
  2.7× exact (Kittilä + Ivalo, 240k shots each).
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
- *"Basis risk?"* The cover pays on gauges, not on the insurer's claims. The back-test: a "≥2 gauges" trigger paid
  in 2005 when Lapland flooded. We'd fit the gauge choice to each buyer's exposure; the staged payout
  (50 % at 2, 100 % at 3) reduces it.
- *"Does the snow signal work?"* At the 1-in-10 level, the 1 March snow flag caught 11 of 19 payout years in advance, and no payout
  followed a low-snow March. That's in-sample with a small sample, and we say so.

## Business (Vaishnav)
- *"Who buys, and why?"* A Finnish non-life insurer, for the flood losses it keeps under its reinsurance retention.
  Reinsurance is bought on 1 January, before the spring signal exists; an index cover pays fast with no claims
  adjustment.
- *"What does it cost?"* North cluster, €10M if ≥2 gauges pass 1-in-50: market price €491k–€687k a
  year (always quote market prices). If priced as independent, it would be €96k–€134k. The market currently has no price for this joint risk.
- *"Isn't Finland too small?"* Finland is the pilot with the best open data. The same engine prices Sweden
  (Gävle 2021, SEK 1.9bn), Norway and Central Europe (storm Boris, €2.15bn insured).
- *"Won't sellers just raise the price after a snowy March?"* Yes, that's why it's bought in winter, and Tulva is the
  pricing engine for whoever carries the risk.
- *"Why now?"* EIOPA adds a Finnish flood capital factor from January 2027, and insurers must include climate
  scenarios in ORSA.

## New jury questions (research/18)

- **Steinmann / Mehtola: "Your 14-area chip result is sampling. Did amplitude estimation run on the full model?"**
  "No, and that's deliberate. Emerald shows the full loader fits: 18 qubits, 44 gates. Amplitude estimation adds
  two loader copies per step, which at 14 areas is far past today's ~50-gate budget. So we ran it on the 3-qubit
  Kittilä–Ivalo piece on Marrakesh and Garnet. The loader is the part that has to scale, and it scales linearly."
- **Mehtola: "Your calibration circuits have known answers. Isn't the mitigation tuned towards the result you
  wanted?"** "The calibration circuits have *different* known answers, one large and one near zero, never the
  target value. They measure how much signal survives each step and the false-trigger floor, in the same job and
  on the same qubits. We invert that, and only afterwards compare with exact. Raw numbers are on the slide next to
  the calibrated ones."
- **Toikka: "Do 1961–2025 data hold as winters warm?"** "Not fully. Spring floods are shrinking and coming
  earlier, fastest in Ostrobothnia; Lapland is roughly stable to about 2050; rain and winter floods grow (SYKE/FMI,
  Veijalainen 2010). So the model must be re-fitted on recent decades and conditioned on climate scenarios; that's
  on our roadmap. Today the price already moves with *this* winter's snow, not the 65-year average." (Sources:
  business/NOTES_FOR_TOIVO.md.)
- **Toikka (OP as buyer): "Who sells us this, and why not just buy more treaty reinsurance?"** "A reinsurer or an
  ILS fund that wants Nordic diversification sells it at the 2.5–3.5× multiple we priced. It doesn't replace your
  treaty. It fills the gap the treaty can't: the correlated spring layer you retain, priced once the snow is known
  and paid in days off a public gauge. We license the engine to whichever side you're on."
- **Anbarjafari: "The theme is AI × quantum. Where is the AI?"** "Honestly: the product's early-warning signal is
  statistical, snow index to risk shift, because an insurer has to defend the trigger to a regulator. We built it
  with AI coding agents (Claude Code). The next step is an ML seasonal forecaster: snow plus soil moisture plus
  ECMWF seasonal forecasts."

## Traps
- Never say "quantum is faster" or "advantage".
- Never claim "EIOPA assumes 0 % in Finland". The 0 % is cross-border (FI–SE/NO/DK); inside Finland EIOPA uses
  a 19-zone matrix.
- If you don't know: "Good question. We didn't test that this weekend; here's how we would."
