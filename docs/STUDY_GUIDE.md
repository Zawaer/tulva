# Tulva study guide (Fri evening version, after review round 4 + Q50)

Read this top to bottom once. The words in **bold** are what to say out loud.

## 1. The idea in 5 sentences
1. In some springs, many Finnish rivers flood **at the same time**, because they share one cause: a big snowpack melting at once.
2. Insurers and their capital rules mostly treat floods in different places as **weakly linked**, so they under-price the chance that several flood together.
3. We measured that link from 65 years of public river data (SYKE) and found the **snow on 1 March** predicts it two months ahead.
4. **Tulva** is an index cover that pays an insurer when ≥2 of 5 northern rivers pass their 1-in-50 flood level in the same spring, priced from that measured link and updated in March.
5. We built the pricing math as a quantum algorithm and ran it on **four real quantum computers** (IBM Marrakesh, IQM Garnet, IQM Emerald, VTT Q50), honestly showing where today's hardware works and where it stops.

## 2. Terms in plain words
- **1-in-50 flood level**: a river flow so high it happens on average once in 50 years (2 % chance a year). All 7 big Finnish home insurers use the same 1-in-50 idea for "exceptional flood" (they measure water level at the house; we measure river flow at a gauge).
- **Correlation / link**: how much floods in different places tend to happen together. 0 = independent, 1 = always together.
- **"Chance" / independence**: what you'd expect if rivers flooded independently. Real big-flood springs happen **almost 4× more often** than that.
- **The 2027 rule**: from 30 Jan 2027 Finland's insurer capital rules (Solvency II standard formula) get a flood charge with **fixed** correlations: an average of **0.27** between Finnish zones, 0 to Sweden/Norway/Denmark. Fixed = it never reacts to this winter's snow.
- **Standard formula vs internal model**: smaller insurers use the regulator's formula; big ones (If) use their own approved model. Our "why now" covers both.
- **Parametric / index cover**: pays on a measured number (river flow), not on assessed damage. Fast and transparent, but…
- **Basis risk**: the index can pay when the insurer had small losses, or not pay when it had big ones. We say it openly.
- **Expected loss**: average payout per year as % of the cover limit. The fair price starts there; the market adds a margin (×2.5–3.5).
- **Reinsurer**: the insurer's insurer (Swiss Re, Munich Re…). It carries the risk; we don't.
- **ORSA**: the insurer's own yearly risk self-assessment, a place our March number is useful.
- **Qubit / shot / two-qubit gate**: a quantum bit / one run of the circuit / the noisy operation that limits how big a circuit can be.
- **Amplitude estimation (QAE)**: quantum method to estimate a probability with fewer runs than classical sampling, **on future, error-corrected hardware**. It works by repeating a "boost" step (Grover step, k = number of boosts).
- **Calibration / noise-aware**: we run two extra circuits with known answers on the same chip and use them to correct the noise.

## 3. Numbers to know (all from code, in CLAIMS.md)
| What | Number |
|---|---|
| Big flood springs (≥4 of 14 areas over 1-in-10) | 10 of 65 springs, ~3.9× chance |
| Fair expected loss of the index | **1.96 %** of limit / yr (90 %: 1.6–2.2) |
| Same, using the 2027 rule's 0.27 average | 1.11 %, so **~1.8× under-priced** |
| After a snowy March | **6.4 %**, the risk **triples** (3.3×, range 2.1–4.4×) |
| Premium per €10M layer (insurer → reinsurer) | ~€0.5–0.7M a year |
| Our licence | €25k pilot, then ~€75k/yr per insurer |
| Year 3 (assumption) | 3–6 insurers → €0.2–0.45M/yr, then Nordics |

## 4a. Amplitude estimation (QAE) in plain words
- **What it does:** estimates a probability, here "how likely is it that both rivers flood in the same spring?"
- **How the data goes in:** each qubit is a river or the weather state. Rotation gates set each one's chance of
  flooding from our model, and controlled rotations link them, so rivers flood together on wet springs. The
  circuit is our flood model, written as a quantum state.
- **How it gets the answer:** a "boost" step (Grover) repeatedly amplifies the outcome "both flood", and measuring
  how fast it grows reveals the probability. On perfect hardware this needs about the square root of the runs
  classical Monte Carlo needs, which helps most for rare events.
- **Proof the circuit is right:** on Qiskit's ideal (noise-free) Aer simulator it gives the exact answer, 0.125 %.
  On real chips the gaps are noise; the boost steps (27–46 two-qubit gates) are where noise wins.
- **Why it fits this problem:** pricing rare joint floods means estimating small probabilities, which is exactly
  where QAE's advantage would be largest once hardware is good enough.

## 4. The quantum part, honestly
- **Small circuit** (two northern rivers, 3 qubits; chance both flood = 0.125 %):

  | Machine | Calibrated result | Error |
  |---|---|---|
  | IBM Marrakesh | 0.149 % | +19 % |
  | IQM Garnet | 0.164 % | +31 % |
  | VTT Q50 (3 repeats) | 0.465 %, 0.534 %, 0.107 % | **not stable**: spread 5× (raw 1.5 %) |

  Q50: the noise calibration itself drifted between repeats, and the boost step kept only 12–19 % of the signal (other chips 56–80 %). Say: **"On Q50 our calibration wasn't stable yet: three repeats spread 5×."** Never say Q50 was the most accurate.

- **The boost steps barely work** on any chip: the signal fades after the first step. So today the answer comes mostly from the **calibrated first measurement**. Say it before they ask.
- **Snow survives on the chip**: snowy-March ratio 3.05× on chip vs 2.75× exact.
- **Big circuit** (all 14 rivers, 18 qubits, 44–49 gates):
  - ≥4 rivers: Emerald 13.8 %, Q50 31 %, exact 10.9 %.
  - The correlation survives on Emerald but weakened; on Q50 noise dominates; rare 1-in-50 events drown in noise everywhere.
- **Bottom line:** **"Classical computers still win today. The method is ready; the hardware isn't yet. We know exactly where it breaks, because we measured it on four machines."**

## 4b. "Why now", explained
- **Flood capital**: insurers must hold a safety buffer of money (capital) big enough to survive a very bad year. From 30 Jan 2027 Finland's rules add a flood part.
- **Fixed correlations**: to size that buffer, the rule assumes how often floods in different Finnish zones happen *together*, from a fixed table (≈0.27 on average). Same numbers every year.
- **That ignore the snow**: in reality "flooding together" changes every year, mainly with the snowpack. The table treats a record-snow year and a no-snow year the same.
- **We give a snow-aware number**: Tulva reads the 1 March snow and updates the risk ("this spring, several northern rivers flooding together is ~3× likelier than normal"). The insurer has two months before the melt to act: extra protection, claims staff, plans.
- **One sentence**: **"From 2027 the rules assume the same flood risk every year. We tell insurers what this year's snow actually means, two months before the melt."**
- **Caution**: we don't change the capital the rule requires. If asked "does it cut our capital?": **"Not under the standard formula. The value is pricing and preparation, not capital relief."**

## 5. Business in one breath
**"Our customers are Finnish home insurers like If Insurance and OP. A reinsurer carries the risk. We license the index and the pricing: 25k for a pilot, then 75k a year. From 2027 flood capital uses fixed correlations that ignore the snow; we give a snow-aware number. Our ask: one insurer's flood claims for eight weeks, to measure basis risk."**

Four tough questions, with simple answers:

**1. "Isn't the market tiny?"**
→ "Yes, Finland alone is small. It's where we prove it works. Sweden, Norway and other snowy regions have the same problem."

**2. "What if the index pays but the insurer had no damage, or the other way round?"**
→ "That can happen. Looking back, it paid in the big flood years 2005 and 2018, but it also missed some. That's why our first step is to test it on a real insurer's claims."

**3. "Does it lower the money the insurer must hold by law?"**
→ "No. It helps them price better and prepare earlier. It's not a trick to lower their capital."

**4. "Did you test the snow warning on years you didn't use to build it?"**
→ "Not yet. We built and checked it on the same 65 years. The pilot is where we test it on new years."

## 6. Mentor questions to ask
**Insurance mentor (OP)**
1. "Would a snow-aware joint-flood number be useful to OP/Pohjola, for pricing, reinsurance or ORSA?"
2. "How does OP handle correlated spring floods in its capital today, standard formula or own model?"
3. "What would you need to see to pilot this? Is 8 weeks of claims data realistic?"
4. "What would make you say no?"
→ If he says something positive, ask: **"Can we quote you on that in the pitch?"**

**CSC / LUMI mentor**
1. "Our 18-qubit run on Q50 read 31 % vs 10.9 % exact, while Emerald got 13.8 %. Is that expected for Q50, or did we use it wrong (layout, error mitigation)?"
2. "Is there FiQCI error mitigation we should switch on?"
3. (Mention the hackathon module needed a `module use …/hackathon/` workaround; useful feedback for them.)

**Ultrahack crew, pitch**
1. "Is the money story on slide 7 clear in 30 seconds?"
2. "Which slide would you cut first?"
3. "Does 'classical still wins' hurt us or help us?"

## 7. Don't say
- "Quantum advantage", "faster than classical", "works on hardware" (without "calibrated").
- "The 2027 rule implies a price" (it sets capital, not prices).
- "Same water level as the home policies" (they use water level, we use river flow).
- "Kittilä and Ivalo circuit" (it's a generic two-river North-cluster pair).
- Anything about our past wins.
