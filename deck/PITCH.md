# Tulva: 3-minute pitch script

**Slides 1–9 are the whole deck (backup slides removed; details for Q&A are in QA.md and docs/QA_DRILL.md).**
The slides carry one idea each; the details (intervals,
sources, why now) are said or kept for Q&A.

**Timing (final, voiceover video): 230 live words + the 45 s demo video, which speaks for itself + 4 short
pauses and 1 long (~4–5 s). Word count = `>` lines outside §4, [pause] cues removed. At 135 wpm ≈ 2:32 (1 Hook 0:12 ·
2 Gap 0:12 · 3 Product 0:14 · 4 Video 0:45 · 5 Circuit 0:13 · 6 Chips 0:04 · 7 Honest 0:09 · 8 Business 0:30 ·
9 Close 0:13). At 120 wpm ≈ 2:44 (2:45 with a 5 s pause budget). §6 is cut from 20 to 10 words: the video now says
its numbers and the four computers. Rehearsals of a 245-word version with the old 37 s video ran 2:45–2:55 on stage;
the shorter script and the longer video roughly cancel, so keep the pace. Buzzer at 3:00. Pauses are one breath
(~0.7 s); the long pause ~1.5 s.**

Simple English, short sentences. **[pause]** = stop for one breath. CAPS = stress that word (say it, don't shout
it). The demo video (slide 4, 45 s) **has its own voiceover and burned-in captions**: the presenter says nothing
during it. Spoken lines are the `>` lines;
`build_deck.py` copies them into each slide's speaker notes, so edit them here and rebuild. Every number is in
`CLAIMS.md`.

**One timing story, everywhere:** the cover is sold in autumn, before the snow falls. In March the snow update
tells the insurer how much joint risk it holds. The price is set in autumn, not after the snow is known.

## 1 · Hook (0:00–0:12)

> In May 2005, four Lapland rivers hit flood levels TOGETHER. The snow had warned us two months EARLIER.
> Tulva turns that warning into a PRICE. [pause]

Q&A only (not spoken): "flood levels" = river flow (discharge) over each gauge's 1-in-10 level, not damage. Four = Ivalo, Kittilä, Rovaniemi, Tornio over their 1-in-10 level (the map's filled dots); Ivalo,
Kittilä and Rovaniemi also passed their 1-in-50 level. "Warned us" = the North's 1 March snow was in its top 15 %
(87th percentile): an in-sample back-test, not a forecast we made at the time.

## 2 · The gap (0:12–0:24)

> Rivers in one region share ONE snowpack, so they flood TOGETHER: big flood springs come almost FOUR times more
> often than if each river flooded alone. [pause] Insurers buy cover in autumn, BEFORE the snow.

Q&A only (not spoken): 10 of 65 springs (15.4 %, 90 % interval 9–24 %) had ≥4 of 14 areas over 1-in-10; chance on the
same gauge-years 3.9 % (3.9×). If all 14 gauges had reported every year, chance would be 4.4 % (3.5×).

## 3 · The product (0:24–0:38)

> Our index pays when SEVERAL northern rivers flood TOGETHER. The real cost of that risk is almost TWICE what the
> regulator's standard assumption gives. [pause] And after a snowy March, it TRIPLES.

Q&A only (not spoken): a model comparison, not "the rule implies a price": expected loss 1.96 % of the limit a year (year-bootstrap 90 %: 1.6–2.2 %) vs
1.11 % for a model with one correlation of 0.27, the mean of the 2027 Finnish 19-zone flood matrix (1.77×). We used the
19-zone mean, not the Lapland zones' own entries (the repo has neither the entries nor the zone-to-region map). ≈5× only
against independence (0.38 %). "Triples" = 6.4 % after a top-15 % snow March vs the autumn (normal) 1.96 % (3.3×, 90 %: 2.1–4.4×): snowy vs NORMAL,
for the 5-river cover. Not the same as slide 6's 3.05× (snowy vs LOW snow, two-river pair on chip; snowy vs normal
there is 1.51× chip / 1.55× exact). The product pays the full limit at ≥2; a staged payout is only a variant. The
cover is priced in autumn; in March the insurer buys a top-up / second-layer cover if it wants one, staffs claims in
the regions at risk and uses the number in its ORSA. Market price (2.5–3.5× expected loss): 4.9–6.9 % rate on line,
≈ €49–69k a year per €1M of cover.

## 4 · Demo video (0:38–1:23), plays with voiceover

(video plays with voiceover, ~45 s) Say nothing; click to start it. The video has its own voice and burned-in
captions (deck/video/anim/narration.md): 2005 map and the March snow → the app, March snow set to high, the North
cover's chance from about 2 % to 6.4 % → IQM Emerald vs exact bars (as slide 6), snowy vs low-snow March 3× on
chip, 2.75× exact → IBM,
IQM and VTT Q50 → "Tulva. The snow warns two months early." If the hall sound fails, the captions carry it.

## 5 · Our circuit (1:23–1:36)

> Each qubit is a river or the weather; the gates ARE our flood model. Why quantum? Twice the accuracy: normal
> simulation needs four times the work, quantum only twice.

Q&A only (not spoken): method = quantum amplitude estimation (QAE), in its maximum-likelihood form (MLAE): Grover
powers k = 0, 1, 2, no phase estimation, plus noise-aware calibration on hardware. The figure is the circuit we ran
(instance A3_kittila_ivalo_both in scripts/run_hw.py, drawn by scripts/qae_circuit_figure.py): A = RY on the
wet-spring qubit, RY + controlled-RY on each river qubit (angles 2·arcsin(√p) from the model); CZ marks "both
flood"; one Grover step = A† · reflect about |000⟩ · A. On an ideal simulator: 0.125 % (exact 0.125 %), ±0.011 pp vs
Monte Carlo ±0.027 pp at the same 16,000 oracle queries (≈2.5× tighter). "Only twice" is the ideal scaling (error ∝
1/N vs 1/√N); our shallow k = 0–2 runs do not reach it on today's chips (slide 7).

## 6 · Quantum, in practice (1:36–1:40)

> And on a REAL quantum chip, a snowy March still shows about THREE times the risk.

The numbers (3.05× on chip, 2.75× exact) and the four computers are on the slide and in the video, so they are
not repeated here.

Q&A only (not spoken): the two-river core is a North-cluster pair with identical loadings and 1-in-50 trigger, not
Kittilä and Ivalo specifically. The 3.05× is IQM Emerald (calibrated, 90 %: 2.6–3.6). The simplified 14-river model
(two-level, 18 qubits, sampling only) ran on IQM's Emerald and Q50. Method: calibrated sampling plus shallow amplitude
estimation (Grover steps k = 0–2). Signal kept at k = 1 in the runs shown:
Emerald 0.56–0.59, IBM / Garnet 0.77–0.78, VTT Q50 0.12–0.19 (earlier runs 0.65–0.88), so the estimate is mostly the
calibrated k = 0 circuit.
VTT Q50 (via LUMI): three repeats gave 0.11–0.53 % vs exact 0.125 %; calibration not yet stable, k = 1 keeps only
0.12–0.19 of the signal. It is the fourth computer we ran on, not a headline result (QA.md).

## 7 · Quantum, honestly (1:40–1:49)

> Classical computers still WIN today: rare floods drown in chip noise. The method is READY. The hardware is
> not, YET.

## 8 · Business (1:49–2:19)

> Our customers: insurers like OP and If. In March, two months before the melt, our index tells them how risky
> this spring is, so they can buy extra cover IN TIME, paid automatically on the index. They pay US a licence:
> 25 thousand to pilot, then 75 thousand a year. From 2027, capital rules assume the SAME flood risk every year, whatever the snow. Our ask: one
> insurer's flood claims, eight weeks.

Q&A only (not spoken): premium per €10M North layer ≈ €0.5–0.7M a year (model × 2.5–3.5 market multiple) goes insurer →
reinsurer; the licence goes insurer → Tulva (the reinsurer pays Tulva nothing). "The regulator's formula" = the 2027
Solvency II standard formula; "their own model" = an approved internal model (If: Sampo's partial internal model; we
don't claim OP uses one). Year 3 = 3–6 insurers × €75k (assumption); Nordic snowmelt upside unsized (assumption). We'd
like to pilot with OP; there is no agreement. Basis risk (1-in-10 back-test): paid in loss springs 1966, 2005, 2018;
missed Ostrobothnia 2012–13 and 2024 (snow flag on, index silent) and Lapland 2020; since 2005 also paid in 2015, 2023
and 2024 in the North with no recorded Lapland loss. At the 1-in-50 product level: paid 1966 and 2005 only.

## 9 · Close (2:19–2:32)

> Everything you saw, we built THIS weekend. [pause] Next March, the snow will warn us AGAIN. [long pause] This
> time, it will have a PRICE. Thank you.
