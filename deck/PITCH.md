# Tulva: 3-minute pitch script

**Timing: 240 live words + the 37 s silent video + 6 short pauses (~5 s).
At 135 wpm ≈ 2:29 (1 Hook 0:12 · 2 Gap 0:18 · 3 Product 0:21 · 4 Video 0:37 · 5 Quantum 0:13 · 6 Honest 0:10 ·
7 Business 0:25 · 8 Close 0:13). At 120 wpm ≈ 2:42 (0:14 · 0:20 · 0:23 · 0:37 · 0:15 · 0:11 · 0:28 · 0:14).
Target < 2:45, buzzer at 3:00. Pauses are one breath (~0.7 s); the long pause ~1.5 s.**

Simple English, short sentences. **[pause]** = stop for one breath. CAPS = stress that word (say it, don't shout
it). The demo video is **silent (37 s)**: the presenter narrates it **live** on the cues below; the slide-4
narration (61 words, ~27 s at 135 wpm) fits inside the video and is not counted in the 240. Spoken lines are the `>` lines;
`build_deck.py` copies them into each slide's speaker notes, so edit them here and rebuild. Every number is in
`CLAIMS.md`.

**One timing story, everywhere:** the cover is sold in autumn, before the snow falls. In March the snow update
tells the insurer how much joint risk it holds. The price is set in autumn, not after the snow is known.

## 1 · Hook (0:00–0:12)

> In May 2005, two Lapland rivers flooded at the SAME time. Lapland's snow had warned us two months EARLIER.
> Tulva turns that warning into a PRICE. [pause]

## 2 · The gap (0:12–0:30)

> Finland's rivers in one region share ONE snowpack, so they flood TOGETHER. [pause] Springs with many floods
> come about FOUR times more often than chance says. Insurers carry that joint risk and buy cover in autumn,
> BEFORE the snow falls.

## 3 · The product (0:30–0:51)

> The Tulva Index pays when SEVERAL northern rivers pass a rare flood level TOGETHER. Even against the
> regulator's average correlation, the fair price is about TWICE as high. [pause] This March's snow moves it
> THREE times more. No vendor model uses this winter's snow. Tulva does.

Q&A only (not spoken): "about TWICE" = 1.96 % vs 1.09 % (≈1.8×) against one equicorrelation of 0.27, the mean of the
regulator's 19-zone matrix inside Finland; ≈5× only against independence. "THREE times more" = after a snowy March
(top 15 %) 6.4 % vs 1.96 %. Vendor models (Verisk inland flood, Central Europe incl. FI/SE/NO) are
precipitation-driven; RMS says it models snowmelt but averages over simulated winters: none reprices from this
March's measured snow. Per €1M of cover: 4.9–6.9 % rate on line ≈ €49–69k a year.

## 4 · Demo video (0:51–1:28), narrated live

The video is silent; say each line when its caption appears (video time → line):

> [0 s, map] This is our LIVE app. Lines join rivers that flood together.
> [5 s, snow high] March snow set to HIGH… and the northern price JUMPS.
> [12 s, shots, low snow] REAL shots from an IQM quantum chip. Red means BOTH rivers flood. Low snow: little red.
> [18 s, snowy] Snowy March: MORE red. More than TWICE as much.
> [24 s, 14-area card] A simplified version of our 14-river model, on ONE chip.
> [31 s, 2005] And 2005: Lapland floods TOGETHER.

## 5 · Quantum, in practice (1:28–1:41)

> We ran a quantum method for rare events on IBM and IQM. [pause] The snow warning SURVIVES on the chip: about
> three times the risk, like the exact answer.

## 6 · Quantum, honestly (1:41–1:51)

> But honestly: classical computers still WIN today. Rare floods drown in hardware noise. The method is READY.
> The hardware is not, YET.

## 7 · Business (1:51–2:16)

> Who pays? First, insurers with internal models, like If. A reinsurer carries the risk; we earn a fee per deal
> for index and price. Why now? From 2027, EU rules make Finnish insurers hold capital for flood, but judged
> snowmelt floods NOT linked. We have the evidence. Our ask: one insurer's flood claims for eight weeks.

## 8 · Close (2:16–2:29)

> Everything you saw, we built THIS weekend. [pause] Next March, the snow will warn us AGAIN. [long pause] This
> time, it will have a PRICE. Thank you.
