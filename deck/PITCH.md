# Tulva: 3-minute pitch script

**Slides 1–8 are the stage deck. Backup slides 9–11 (product & pricing, basis risk & business, hardware) are
for Q&A only: never show them in the 3 minutes.** The slides carry one idea each; the details (intervals,
sources, why now) are said or kept for Q&A.

**Timing (round 5, frozen): 225 live words + the 37 s silent video + 6 short pauses (~5 s).
At 135 wpm ≈ 2:22 (1 Hook 0:11 · 2 Gap 0:13 · 3 Product 0:15 · 4 Video 0:37 · 5 Quantum 0:15 · 6 Honest 0:09 ·
7 Business 0:26 · 8 Close 0:11). At 120 wpm ≈ 2:35. Rehearsals of the 245-word version ran 2:45–2:55 on stage, so
expect ≈2:35–2:45 now. Buzzer at 3:00. Pauses are one breath (~0.7 s); the long pause ~1.5 s.**

Simple English, short sentences. **[pause]** = stop for one breath. CAPS = stress that word (say it, don't shout
it). The demo video is **silent (37 s)**: the presenter narrates it **live** on the cues below; the slide-4
narration (55 words, ~25 s at 135 wpm) fits inside the video and is not counted in the 225. Spoken lines are the `>` lines;
`build_deck.py` copies them into each slide's speaker notes, so edit them here and rebuild. Every number is in
`CLAIMS.md`.

**One timing story, everywhere:** the cover is sold in autumn, before the snow falls. In March the snow update
tells the insurer how much joint risk it holds. The price is set in autumn, not after the snow is known.

## 1 · Hook (0:00–0:11)

> In May 2005, four Lapland rivers hit flood levels TOGETHER. The snow had warned us two months EARLIER.
> Tulva turns that warning into a PRICE. [pause]

Q&A only (not spoken): "flood levels" = river flow (discharge) over each gauge's 1-in-10 level, not damage. Four = Ivalo, Kittilä, Rovaniemi, Tornio over their 1-in-10 level (the map's filled dots); Ivalo,
Kittilä and Rovaniemi also passed their 1-in-50 level. "Warned us" = the North's 1 March snow was in its top 15 %
(87th percentile): an in-sample back-test, not a forecast we made at the time.

## 2 · The gap (0:11–0:24)

> Rivers in one region share ONE snowpack: they flood TOGETHER. [pause] Big flood springs come almost
> FOUR times more often than chance. Insurers buy cover in autumn, BEFORE the snow.

Q&A only (not spoken): 10 of 65 springs (15.4 %, 90 % interval 9–24 %) had ≥4 of 14 areas over 1-in-10; chance on the
same gauge-years 3.9 % (3.9×). If all 14 gauges had reported every year, chance would be 4.4 % (3.5×).

## 3 · The product (0:24–0:40)

> Our index pays when SEVERAL northern rivers pass a rare flood level TOGETHER. Its expected loss is 1.8
> TIMES what the regulator's 2027 average correlation gives. [pause] After a snowy March, it TRIPLES from autumn.

Q&A only (not spoken): a model comparison, not "the rule implies a price": expected loss 1.96 % of the limit a year (year-bootstrap 90 %: 1.6–2.2 %) vs
1.11 % for a model with one correlation of 0.27, the mean of the 2027 Finnish 19-zone flood matrix (1.77×). We used the
19-zone mean, not the Lapland zones' own entries (the repo has neither the entries nor the zone-to-region map). ≈5× only
against independence (0.38 %). "Triples" = 6.4 % after a top-15 % snow March vs the autumn (normal) 1.96 % (3.3×, 90 %: 2.1–4.4×): snowy vs NORMAL,
for the 5-river cover. Not the same as slide 5's 3.05× (snowy vs LOW snow, two-river pair on chip; snowy vs normal
there is 1.51× chip / 1.55× exact). The product pays the full limit at ≥2; a staged payout is only a variant. The
cover is priced in autumn; in March the insurer buys a top-up / second-layer cover if it wants one, staffs claims in
the regions at risk and uses the number in its ORSA. Market price (2.5–3.5× expected loss): 4.9–6.9 % rate on line,
≈ €49–69k a year per €1M of cover.

## 4 · Demo video (0:40–1:17), narrated live

The video is silent; say each line when its caption appears (video time → line):

> [0 s, map] This is our app. Lines join rivers that flood together.
> [5 s, snow high] March snow set to HIGH… and the northern price JUMPS.
> [12 s, low snow] IQM chip. Red: BOTH rivers flood. Low snow, little red.
> [18 s, snowy] Snowy versus low snow: about THREE times the risk, close to exact.
> [24 s, 14-area card] A simplified version of our 14-river model, on ONE chip.
> [29 s, 2005] And 2005: Lapland floods TOGETHER.

## 5 · Quantum, in practice (1:17–1:32)

> Our two-river core ran on IBM, IQM and Finland's VTT Q50; the simplified 14-river model on IQM's Emerald and Q50.
> [pause] On chip, the snow warning SURVIVES: snowy versus low snow, 3.05 times; exact, 2.75.

Q&A only (not spoken): the two-river core is a North-cluster pair with identical loadings and 1-in-50 trigger, not
Kittilä and Ivalo specifically. Simplified = two-level (wet spring or not) version of the 14-river model, 18 qubits, sampling only. Method:
calibrated sampling plus shallow amplitude estimation (Grover steps k = 0–2). Signal kept at k = 1 in the runs shown:
Emerald 0.56–0.59, IBM / Garnet 0.77–0.78, VTT Q50 0.12–0.19 (earlier runs 0.65–0.88), so the estimate is mostly the
calibrated k = 0 circuit.
VTT Q50 (via LUMI): three repeats gave 0.11–0.53 % vs exact 0.125 %; calibration not yet stable, k = 1 keeps only
0.12–0.19 of the signal. It is the fourth computer we ran on, not a headline result (QA.md).

## 6 · Quantum, honestly (1:32–1:42)

> Classical computers still WIN today. On a perfect simulator our circuit gives the EXACT answer; on real chips,
> rare floods drown in noise. The method is READY. The hardware is not, YET.

## 7 · Business (1:42–2:09)

> Insurers like OP and If pay a reinsurer the premium, and US a licence: 25 thousand to pilot, then 75
> thousand a year. Year three: up to 450 thousand. From 2027, the regulator's formula FIXES flood correlations, blind
> to snow. Insurers with their own model can use our snow-aware number. Our ask: one insurer's flood claims, eight
> weeks.

Q&A only (not spoken): premium per €10M North layer ≈ €0.5–0.7M a year (model × 2.5–3.5 market multiple) goes insurer →
reinsurer; the licence goes insurer → Tulva (the reinsurer pays Tulva nothing). "The regulator's formula" = the 2027
Solvency II standard formula; "their own model" = an approved internal model (If: Sampo's partial internal model; we
don't claim OP uses one). Year 3 = 3–6 insurers × €75k (assumption); Nordic snowmelt upside unsized (assumption). We'd
like to pilot with OP; there is no agreement. Basis risk (1-in-10 back-test): paid in loss springs 1966, 2005, 2018;
missed Ostrobothnia 2012–13 and 2024 (snow flag on, index silent) and Lapland 2020; since 2005 also paid in 2015, 2023
and 2024 in the North with no recorded Lapland loss. At the 1-in-50 product level: paid 1966 and 2005 only.

## 8 · Close (2:09–2:21)

> Everything you saw, we built THIS weekend. [pause] Next March, the snow will warn us AGAIN. [long pause] This
> time, it will have a PRICE. Thank you.
