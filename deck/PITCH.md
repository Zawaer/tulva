# Tulva: 3-minute pitch script

Total 3:00 including the demo video (≈60 s, its voice-over is recorded in the video). Spoken lines are the `>`
lines; `build_deck.py` copies them into each slide's speaker notes, so edit them here and rebuild.
Every number is from `CLAIMS.md` (or a cited outside source on slide 8). About 140 words per minute.

## 1 · Hook (0:00–0:12)

> In May 2005, Kittilä and Ivalo flooded together. The snow had warned us two months earlier.
> Nobody priced that warning. Tulva does.

## 2 · The gap (0:12–0:32)

> Finnish rivers share one snowpack, so they flood together. In 65 years of SYKE data, four or more of fourteen
> river areas flooded in the same spring 15 percent of the time. Independence says 3.9.
> And reinsurance renews on 1 January, before the snow arrives.

## 3 · What it costs (0:32–0:45)

> That gap has a price. A cover paying when two of five northern gauges pass their 1-in-50 level: about
> 100 thousand euros a year if you assume independence. On the joint risk, 500 to 700 thousand. Five times more.

## 4 · Tulva Index (0:45–1:05)

> The Tulva Index pays ten million euros if two of those gauges pass 1-in-50 this spring. Bought in winter,
> triggered by a public gauge anyone can check. Back-tested, the March snow flag caught 11 of 19 payout years,
> 2005 included.

## 5 · Demo video (1:05–2:05)

Voice-over recorded in the video (not spoken live):

> This is Tulva, built this weekend on 65 years of SYKE river data. The map shows Finland's fourteen river
> flood-risk areas in three clusters; lines join areas whose spring peaks move together. Now set the March snow
> outlook to high snow. In the North, the chance that two gauges pass their 1-in-50 level jumps, and the index
> price follows: from 265 thousand to 870 thousand euros, technical. The product card shows the same cover
> three ways: independence, Tulva, and Tulva after a snowy March. Under the hood, the same joint model runs on
> real quantum chips, IBM Marrakesh and IQM Garnet and Emerald, next to the exact answer and classical Monte
> Carlo. Finally, replay 2005: the Lapland cluster lights up, Kittilä and Ivalo together.

## 6 · Quantum, in practice (2:05–2:25)

> Pricing this cover means estimating one rare joint probability: a job for quantum amplitude estimation. We
> loaded all fourteen areas onto IQM Emerald, 18 qubits, 44 two-qubit gates, and it reproduced the joint tail.
> On IBM and IQM, calibrated amplitude estimation landed within 0.04 points of the exact answer.

## 7 · Quantum, honestly (2:25–2:39)

> Honestly: classical Monte Carlo still wins today. Quantum wins at scale, with fault-tolerant hardware and
> expensive models: a full hydrological simulation per scenario, many perils, daily repricing.

## 8 · Business (2:39–2:54)

> Who buys? Finland's non-life insurers, for the flood risk they keep, and the reinsurers behind them. We license
> the pricing and trigger engine. Why now? From 2027, Solvency II gives Finland a flood factor with zero
> correlation to its neighbours. Finland first, then the Nordics and Central Europe.

## 9 · Close (2:54–3:00)

> Tulva prices Finland's spring floods as a joint risk, and runs it on real quantum hardware.
