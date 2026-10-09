# Tulva: 3-minute pitch script

**Timing: 245 live words + the 37 s silent video + 6 short pauses (~5 s).
At 135 wpm ≈ 2:31 (1 Hook 0:10 · 2 Gap 0:13 · 3 Product 0:17 · 4 Video 0:37 · 5 Quantum 0:13 · 6 Honest 0:10 ·
7 Business 0:35 · 8 Close 0:11). At 120 wpm ≈ 2:44 (0:12 · 0:14 · 0:20 · 0:37 · 0:15 · 0:11 · 0:39 · 0:12).
Target ≤ 2:45, buzzer at 3:00. Pauses are one breath (~0.7 s); the long pause ~1.5 s.**

Simple English, short sentences. **[pause]** = stop for one breath. CAPS = stress that word (say it, don't shout
it). The demo video is **silent (37 s)**: the presenter narrates it **live** on the cues below; the slide-4
narration (66 words, ~29 s at 135 wpm) fits inside the video and is not counted in the 245. Spoken lines are the `>` lines;
`build_deck.py` copies them into each slide's speaker notes, so edit them here and rebuild. Every number is in
`CLAIMS.md`.

**One timing story, everywhere:** the cover is sold in autumn, before the snow falls. In March the snow update
tells the insurer how much joint risk it holds. The price is set in autumn, not after the snow is known.

## 1 · Hook (0:00–0:11)

> In May 2005, four Lapland rivers flooded TOGETHER. The snow had warned us two months EARLIER.
> Tulva turns that warning into a PRICE. [pause]

Q&A only (not spoken): four = Ivalo, Kittilä, Rovaniemi, Tornio over their 1-in-10 level (the map's filled dots); Ivalo,
Kittilä and Rovaniemi also passed their 1-in-50 level. "Warned us" = the North's 1 March snow was in its top 15 %
(87th percentile): an in-sample back-test, not a forecast we made at the time.

## 2 · The gap (0:11–0:25)

> Rivers in one region share ONE snowpack, so they flood TOGETHER. [pause] Big flood springs come FOUR
> times more often than chance. Insurers buy cover in autumn, BEFORE the snow.

Q&A only (not spoken): 10 of 65 springs (15.4 %, 90 % interval 9–24 %) had ≥4 of 14 areas over 1-in-10; chance on the
same gauge-years 3.9 % (3.9×). If all 14 gauges had reported every year, chance would be 4.4 % (3.5×).

## 3 · The product (0:25–0:43)

> The Tulva Index pays when SEVERAL northern rivers pass a rare flood level TOGETHER. Against the average link the
> 2027 capital rule assumes, the fair price is 1.8 TIMES higher. [pause] And after a snowy March, the fair
> risk TRIPLES.

Q&A only (not spoken): fair price = 1.96 % of the limit a year vs 1.11 % at one correlation of 0.27, the mean of the
regulator's 19-zone matrix inside Finland (1.77×); ≈5× only against independence (0.38 %). "Triples" = 6.4 % after a
top-15 % snow March vs 1.96 % (3.3×). The cover is priced in autumn; in March the insurer buys a top-up / second-layer
cover if it wants one, staffs claims in the regions at risk and uses the number in its ORSA. Per €1M of cover: 4.9–6.9 %
rate on line ≈ €49–69k a year.

## 4 · Demo video (0:43–1:20), narrated live

The video is silent; say each line when its caption appears (video time → line):

> [0 s, map] This is our LIVE app. Lines join rivers that flood together.
> [5 s, snow high] March snow set to HIGH… and the northern price JUMPS.
> [12 s, low snow] Real runs on an IQM quantum chip. Red means BOTH rivers flood. Low snow: little red.
> [18 s, snowy] Snowy March: MORE red. Corrected, about THREE times the risk, like the exact answer.
> [24 s, 14-area card] A simplified version of our 14-river model, on ONE chip.
> [29 s, 2005] And 2005: Lapland floods TOGETHER.

## 5 · Quantum, in practice (1:20–1:34)

> On IBM and IQM we ran shallow amplitude estimation on the core: two rivers, three qubits. The 14-river model
> ran on IQM Emerald. [pause] The snow warning SURVIVES on the chip.

## 6 · Quantum, honestly (1:34–1:45)

> But classical computers still WIN today. At 1-in-50, rare floods drown in noise. The method is READY. The
> hardware is not, YET.

## 7 · Business (1:45–2:20)

> Who pays? Insurers with internal models, like the insurer If; a reinsurer carries the risk. We license the
> index: 25 thousand for a pilot, then 75 thousand a year each. Finland first, then Sweden and Norway. Why now?
> From 2027, flood capital uses FIXED correlations, blind to this winter's snow. Our index isn't the insurer's
> losses, but it uses the same 1-in-50 test as all seven Finnish home insurers. Our ask: one insurer's flood
> claims for eight weeks.

## 8 · Close (2:20–2:31)

> Everything you saw, we built THIS weekend. [pause] Next March, the snow will warn us AGAIN. [long pause] This
> time, it will have a PRICE. Thank you.
