# Targeted study guide for Toivo (Fri night)

Built from your three mentor talks. First what you already explain well,
then only the gaps, each in small steps. About 25 minutes. Say the answers out loud.

## What the talks showed

**You already explain well:**
- that quantum doesn't beat classical yet, honestly
- who the customer is (OP, If) and that a reinsurer (Swiss Re) exists
- the €75k licence and that the data is public (SYKE)
- the noise vs simulator difference
- the overall vision; the last talk went smoothly

**Gaps, most important first:**
1. The core "4×" claim: said wrongly ("several rivers 4× more likely than one").
2. Business mechanics: what "preparing" means, how the automatic payout differs from normal reinsurance, why
   March pricing for homeowners is weak.
3. What the quantum algorithm is: you weren't sure we use QAE, or what it does.
4. Monte Carlo, and why QAE would be faster.
5. How data goes into the circuit (the encoding question).
6. Why we compare to "0.27" (a mentor didn't get it).
7. What the model predicts and how far ahead; what the back-test really showed.
8. Reading the Q50 numbers (which gate count is which).

---

## Gap 1: the "4×" claim, said correctly

1. We have 14 rivers and 65 springs (1961–2025).
2. We asked: in how many springs did **4 or more** rivers flood at once? Answer: **10 of 65, about 15 %**.
3. Then: if each river flooded on its own, like separate coin flips, how often would 4+ flood at once by
   chance? About **4 %**.
4. 15 % vs 4 %: big multi-river springs happen **almost 4× more often than chance**.
5. Why: rivers in a region share **one snowpack**, so they rise together.

**Say:** "Big flood springs, when 4 or more rivers flood at once, happen almost four times more often than if
rivers flooded independently, because they share the same snow."
**Never say:** "several rivers flooding is 4× more likely than one river flooding." That's a different claim,
and it's wrong.

---

## Gap 2: business mechanics, one year in the life of OP

1. **Autumn:** OP renews its reinsurance. It buys flood cover from a reinsurer that **pays automatically if our
   index triggers** (≥2 of 5 northern rivers pass their 1-in-50 level). OP pays a premium for it, and pays us a
   licence.
2. **1 March:** we read the snow. A snowy March means this spring's joint-flood risk is about **3× normal**.
3. **March–April, "preparing"** (you couldn't answer this; now you can):
   - buy **extra cover** for this spring from the reinsurer
   - line up **claims adjusters and repair/drying contractors** in the risky region
   - **text customers** to move belongings up and protect basements, which means fewer claims
   - **set aside reserves** and warn management early
4. **May:** the melt. If the index triggers, the reinsurer pays OP **within days**.
5. **Every year, flood or not:** OP pays us the licence.

**Automatic (parametric) vs normal reinsurance** (the open question):
- **Normal** pays OP's *actual* losses after every claim is assessed. That takes **months**, needs loss data,
  and the amount can be argued over.
- **Ours** pays on the **river gauges**. Fast, simple, nothing to argue about.
- **The catch, basis risk:** the index can trigger when OP's losses are small, or miss when they're big. The
  8-week pilot with OP's claims measures this.

**Why not "price home insurance in March"?** People buy and renew home policies all year round, so a March
price for homeowners doesn't work. The March number is **for the insurer**, not the homeowner.

---

## Gap 3: what our quantum algorithm is

1. **Name:** quantum amplitude estimation (**QAE**). Our version is **maximum-likelihood amplitude estimation**
   (MLAE). Say it with confidence: "we use QAE."
2. **Its job:** estimate one probability: "what's the chance both northern rivers flood in the same spring?"
3. **How:** build a circuit whose qubits *are* the flood model (Gap 5). The chance "both flood" becomes a number
   inside the quantum state (an "amplitude").
4. **Then:** a Grover step **boosts** that outcome. We run the circuit with **0, 1 and 2** boosts, count how
   often "both flood" comes out each time, and combine the counts statistically to read off the probability.
5. **Result on a perfect simulator:** **0.125 %**, exactly the true answer.

---

## Gap 4: Monte Carlo, and why QAE would be faster

1. **Monte Carlo = simulate many random springs and count.** Roll the "dice" for the weather and each river,
   check whether both flood, repeat a million times, and divide.
2. **The problem with rare events:** the answer is 0.125 %, about 1 spring in 800. With 16,000 simulated springs
   you see only about 20 "both flood" cases, so the estimate wobbles.
3. **The rule for Monte Carlo:** to be **2× more accurate** you need **4× more samples**.
4. **The rule for QAE (ideal hardware):** 2× more accurate needs only **2× more** runs. That's the
   "quadratic speed-up".
5. **Our measurement:** on the perfect simulator, at the same 16,000 runs, QAE's error was **0.011** percentage
   points vs Monte Carlo's **0.027**: about **2.5× more accurate**.

**Why it fails today:** each boost adds many two-qubit gates (**4** gates with no boost, **27** with one,
**46** with two). Every gate adds noise, so by the second boost the signal is gone. QAE's advantage needs
**error-corrected** hardware.

**Say:** "Pricing rare floods means estimating tiny probabilities. Sampling needs four times the runs for twice
the accuracy; amplitude estimation only twice. On a perfect simulator it was 2.5× more accurate, but today's
noisy chips lose that."

---

## Gap 5: how the data goes into the circuit

Our real numbers for the 3-qubit circuit:
1. **Qubit "wet spring":** a wet spring happens with probability **0.30**. A rotation (RY) sets the qubit to be
   "1" 30 % of the time.
2. **Qubits "river 1" and "river 2":** each river's chance to pass its 1-in-50 level is
   - **0.09 %** in a dry spring
   - **6.45 %** in a wet spring

   A rotation sets the "dry" chance; a **controlled rotation** (CRY) raises it to the "wet" chance only when
   the wet-spring qubit is 1. **That's how "flooding together" enters the circuit.**
3. **The angle is fixed by the maths:** angle = 2 · arcsin(√p). For p = 0.30 that's about 1.16 radians.
4. **So the amplitude IS the probability.** There's no free "feature map" to tune as in quantum machine
   learning. Rescaling would give a wrong answer (feature-map tuning is a quantum-ML idea; it doesn't apply to QAE).
5. **Check by hand:** both flood = 0.30 × 0.0645 × 0.0645 + 0.70 × 0.0009 × 0.0009 ≈ **0.125 %**. If rivers
   were independent (each 2 %): 2 % × 2 % = **0.04 %**. Together is about **3× likelier**.

**Say:** "Each angle comes straight from a probability in our model, so the amplitude is the probability. What
we tuned was calibration and circuit depth, not the encoding."

---

## Gap 6: why compare to "0.27"

1. From **30 Jan 2027** Finland's insurer capital rules (Solvency II) get a flood part.
2. To size the flood buffer, the rule must assume how linked floods are between Finnish zones. It uses a **fixed
   table**, about **0.27 on average**. Call it **"the standard assumption"**.
3. Insurers anchor on what the regulator assumes.
4. We plug that same average link into our model: expected loss **1.11 %** of the cover a year. With the link we
   actually measured: **1.96 %**, about **1.8× higher**.
5. **Why:** rivers sharing one snowpack are linked much more strongly than the national average, and the table
   ignores snow.

**Say:** "We compare to the regulator's standard assumption because that's what insurers anchor on. Inside one
region, rivers that share a snowpack are linked more strongly, so the real cost is about 1.8× higher."

---

## Gap 7: what the model predicts, and the back-test

1. **It forecasts one spring at a time:** the 1 March snow forecasts the coming spring (melt March–June). Not
   years ahead.
2. **Data:** 65 springs of river flow and snow (SYKE), 1961–2025. Both series cover the same 65 years.
3. **Back-test, honestly:** we built the rule on 1961–2000 and tested it on 2001–2025.
   - March snow still **ranked** the flood years: correlation about **0.7** in Ostrobothnia and the North.
   - But winters had less snow, so the "snowy March" flag fired only **twice**: too few to confirm ×3.
   - Backwards (built on 1986–2025, tested on 1961–1985): snowy springs paid **12 of 24** (50 %), normal ones
     **4 of 51** (8 %).

**Say:** "The direction holds on unseen years; the exact size is confirmed only on older years. The pilot tests
it on new years." **Don't say** "the predictions came quite close."

---

## Gap 8: reading the Q50 numbers

| Boost steps (k) | Two-qubit gates | What happened on Q50 |
|---|---|---|
| 0 | 4 | stable after 10× shots, but 2–3× too high |
| 1 | 27 | signal mostly gone (kept 12–19 %) |
| 2 | 46 | signal gone |

- **First runs** (2,000 shots): 0.47 %, 0.53 %, 0.11 % vs true 0.125 %. The spread came from too few shots on
  the calibration circuit.
- **The suggested re-run** (4 gates, 20,000 shots): 0.27–0.38 %, stable but still high. Q50 misread 0 as 1
  about **5 %** of the time on our qubits, vs under 2 % on IBM and IQM.

**Say:** "We re-ran the 4-gate circuit with ten times more shots: stable, but
still high, because Q50's readout errors on our qubits were larger. IBM and IQM came within 20–30 %."

---

## Self-test: answer out loud, without looking
1. What does "almost 4× more than chance" compare?
2. Walk through one year for OP: autumn, March, May.
3. Name the four ways of "preparing".
4. How is the automatic payout different from normal reinsurance, and what's the catch?
5. What does QAE estimate, and how?
6. Monte Carlo vs QAE: how many runs for twice the accuracy?
7. How does a probability become a gate? Why can't we "tune the embedding"?
8. What is the "standard assumption", and why compare to it?
9. Does the model predict years ahead?
10. Why did Q50 do worse than IBM?

Any you can't answer in 15 seconds: reread that gap.
