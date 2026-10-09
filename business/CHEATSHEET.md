# Tulva cheat sheet (Vaishnav)

Plain-language notes for pitching training and Q&A. Full sourced research: `reports/Tulva flood cover business case.md`.

## Tulva in one sentence
Tulva tells Finnish insurers how likely it is that **several areas flood in the same spring**, using this winter's
snow, and sells them a cover that pays fast when that happens.

## How it works (3 steps)
1. **History:** 65 years (1961–2025) of river-flow records from 14 flood areas → which areas flood *together*.
2. **Snow:** amount of snow on 1 March → is this spring riskier than normal?
3. **Price:** chance of a payout × payout + margin = price of the cover.

It is **not** a weather forecast. It is a risk price.

## Words
| Word | Meaning |
|---|---|
| Premium | The price of insurance (what the customer pays per year). |
| Non-life insurance | All insurance except life: home, car, property. |
| Threshold / 1-in-50 | A river level so high it happens once in 50 years on average. |
| Trigger | The rule for paying. Ours: ≥2 rivers in one region pass 1-in-50 in the same spring → pay €10M. |
| Parametric cover | Pays on a measured number (river level), not on inspected damage. Fast, simple. |
| Basis risk | The cover pays but the insurer's real loss is different (or the reverse). Main weakness of parametric covers. |
| Risk load | Margin on top of the expected payout. We use 35 %; the market charges 2.5–3.5× the expected payout. |
| Catastrophe layer | Insurance that only pays for rare, huge disasters. |
| Capital / reserve | Money insurers must keep aside for disasters (Solvency II rules). |
| Capital credit | Buying cover can let an insurer hold a smaller reserve. |
| EIOPA | EU insurance regulator. |
| ORSA | Insurer's own yearly risk self-assessment; must include climate scenarios. |
| QAE | Quantum amplitude estimation: the quantum method that estimates our probability. |
| Monte Carlo | Classical method: simulate many random springs and count. |

## Our numbers (from our code, `CLAIMS.md`)
- Areas in the same region pass their 1-in-10 level together **2.8×** more often than chance.
- Ostrobothnia cover: chance **2.56 %** per spring → price **€346k**. Assuming independence: €77k (**4.5×** too cheap).
- After a high-snow March: Ostrobothnia price **€1.74M** (5× normal).
- Back-test: the March snow signal flagged **11 of 19** paying years (1-in-10 back-test, in-sample) in advance; no payout ever followed a low-snow year.

## Outside facts (cite the source, not "our model")
- Since **2014** the state no longer pays for floods; home insurance does, and only for floods rarer than **1-in-50** (vesi.fi, OP). Same level as our trigger.
- Four insurers write **91 %** of Finnish non-life: OP 32.6 %, LocalTapiola 28.3 %, If 21.9 %, Fennia 8.4 % (Finance Finland 2024).
- Finland has **18** official flood-risk areas: **14 river + 4 coastal** (Ministry of Agriculture and Forestry, Dec 2024). We cover the river ones.
- **Regulation deadline:** today insurers keep **no** reserve for Finnish flood. From **30 Jan 2027** they must (EU Reg. 2026/269).
- **EIOPA 0 %:** the new rules assume Finnish floods are **not** linked to floods in Sweden/Norway/Denmark (0 %). EIOPA looked at 25 % for snowmelt floods and rejected it. *Inside* Finland the rules do link areas. Say "between countries", not "Nordic floods are independent".
- Biggest damaging example: **2005 Lapland** (Ivalo, Kittilä), about €5–17M. (Don't say "2024 Lapland flood": not confirmed as damaging.)
- No Nordic regional parametric flood cover found. Closest: Swiss Re FLOW, sold to companies, not insurers.
- Market cat-bond pricing: **2.4–3.7×** the expected payout (AM Best 2024–26).
- Climate: spring floods shrink and come earlier, fastest in the south/west; **Lapland stays stable to ~2050**. The past is a worse guide → this year's snow matters more.

## Why quantum? (honest version)
- Monte Carlo: **10× more precise needs 100× more samples.** QAE: **10× more precise needs ~10× more steps.**
  That quadratic gain matters most for **rare events**, like a 1-in-50 joint flood.
- Snow on the chip: exact 2.75×, IQM measured 3.05× (90 % interval 2.6–3.6). Our simulator test: at the same 16,000 queries, QAE error ±0.011 pp vs Monte Carlo ±0.027 pp.
- **Today a laptop is faster.** Our whole problem runs classically in under a second (1M simulated springs, 14 areas: ~0.5 s on a laptop). Real quantum advantage needs error-corrected machines, expected in the 2030s (IBM, IQM roadmaps).
- **Our claim:** we built the quantum method, ran it on real IQM and IBM machines, measured the noise, and compared it honestly with exact answers. It is ready for when the hardware catches up. **Never claim we are faster today.**

## Business
- **Customers:** the 4 big Finnish insurers; then reinsurers (Swiss Re, Munich Re, Hannover Re) as capital partners.
- **Model:** 1) license the risk engine to insurers, 2) fee for structuring covers with a reinsurer, 3) grants (Business Finland, EIC).
- **Why now:** 2027 flood reserve rule + ORSA climate scenarios.
- **Start small:** Finland first (mentor agrees), then Nordics and other snowmelt regions (Alps, Canada).
- **Design fixes:** sell before winter (so buyers can't wait for snow data), staged payout (50 % at 2 rivers, 100 % at 3+).

## Expected tough questions
| Question | Answer |
|---|---|
| Isn't the market small? | Yes, past floods are €5–17M. We start in Finland to prove it, then expand. Value is in seeing joint risk before the 2027 rules. |
| Why quantum if a laptop is faster? | Not faster today. The method scales better for rare events; we're validating it on real hardware now. |
| What about basis risk? | Multi-gauge trigger + staged payouts; can add a second trigger tied to the insurer's own losses. |
| Can't insurers wait for March snow and buy only in bad years? | Sales close before winter, or the price follows the snow outlook. |
| Climate change? | Risk shifts earlier and to winter; we re-price every year; Lapland stays stable. |
