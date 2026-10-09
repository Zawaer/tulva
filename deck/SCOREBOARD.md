# Review loop scoreboard (independent simulated jury; fresh reviewers each round)

Criteria 1–5: Impact · Business plan · Progress · Innovativeness · Methodology.

| Round | Reviewer | Impact | Business | Progress | Innov. | Method | Key finding |
|---|---|---|---|---|---|---|---|
| 1 | OP (business) | 3 | 2 | 5 | 4 | 5 | payout not sized to real losses; who carries risk; fee vs premium |
| 1 | PwC (business) | 3 | 2.5 | 4 | 3.5 | 4 | cover vs licence confusion |
| 1 | IQM/VTT/IBM (tech) | 3 | 3 | 5 | 3 | 4 | cherry-picked calibration; no control run; label contradictions |
| 1 | Pitch coach | – | – | – | – | – | dense; weak ending; video/hook contradiction |
| 2 | OP (business) | 3 | 3 | 5 | 4 | 4 | "why now" regulation wording wrong; 5× vs straw man; need concrete chain |
| 2 | PwC (business) | 3 | 2.5 | 5 | 3 | 4 | revenue model one line; basis risk untested; 2024 false alarm |
| 2 | IQM/VTT/IBM (tech) | 4 | 3 | 5 | 4 | 4 | "whole model on one chip" overstated; vs 0.27 corr only 1.8×; CI excludes exact |
| 2 | Pitch coach | 7.5/10 | | | | | runs ~3:10 when nervous; 3× vs 2.4× on screen; simpler lines |
| 3 | OP/PwC (business) | 3.5 | 3 | 4.5 | 4 | 4 | March price nobody can transact at; regulator 0% overstated; basis risk never named |
| 3 | IQM/VTT/IBM (tech) | 3.5 | 3 | 4.5 | 3.5 | 4 | independence 3.9 % vs 4.42 % unexplained; 2.8× vs ≈4× unlabelled; IBM 0.149 vs 0.148 %; QAE depth and 1-in-50 limit overstated by omission |
| 3 | Pitch coach | 7.5/10 | | | | | ~2:31, fits; S3 wording ambiguous; S7 money story weak; S5 too dense |
| 4 | Business juror | 3.5 | 3 | 4.5 | 4 | 4 | matrix doesn't "imply a price"; why-now vs If (internal model) mismatch; size beyond licences; basis risk in numbers |
| 4 | Quantum juror | 3.5 | 3 | 4.5 | 3.5 | 4 | "Kittilä + Ivalo" circuit is an identical-loading North pair; k = 0–2 not 0–3; amplification gain ≈0.5; "works at 1-in-10" overstated |
| 4 | Pitch coach | 7.5/10 | | | | | runs 2:45–2:55 on stage; cut 20–25 words; captions too long for 6 s; "FOUR" vs 3.9× |

### Round 3 — merged fixes, ranked by expected score gain

1. **S3 March bar / wording** (business + coach). Price is fixed in autumn, so "After a snowy March 16–23 %" reads as untradeable; reframe as the insurer's March action (claims staffing, top-up quote, ORSA evidence) and say it plainly ("after a snowy March, fair risk triples"). Pick one framing (fair price vs under-priced) and align "≈2×" with the true 1.8×. Est. +0.5–1 Business.
2. **S7 revenue + regulation wording** (business + coach). One revenue model, not "fee per deal" and "~€75k/yr"; frame €0.1–0.6M as a pilot wedge or show capital/premium at stake. "Regulator judged snowmelt NOT linked" overstates: 0% is cross-border only (domestic matrix mean 0.27). Drop "No vendor model uses this winter's snow". Say "the insurer If". Est. +0.5 Business/Impact.
3. **Name basis risk + the 1-in-50 match** (business). One line on S3/S7: trigger = same 1-in-50 test as all 7 Finnish home policies (docs/flood_terms_check.md); basis risk tested against claims in pilot step 1. Est. +0.5 Innov./Business.
4. **S1 map vs hook** (business + coach). Four dots filled, script says two rivers; highlight only Kittilä and Ivalo. Remove "(out/backtest.json)" footer. Small but cheap.
5. **S5 density** (coach; business notes Emerald vs Garnet mix-up). Keep chart + "3.05× vs 2.75×"; move CI lines, bias, qubit/gate box, job ID to appendix. ⚠ **Methodology flag:** don't delete the bias/CI caveats outright. Move them to the appendix/QA and label which chip each number comes from, or Methodology drops (the business juror already noted the +19/+31 % bias CIs exclude exact).
6. **Jargon** (coach). "shots" → "runs"; slide 2 "independence" → "chance"; explain "regulator's average correlation" (S3).

⚠ **Progress flag:** none of these cuts remove evidence. Keep S8 build list and job IDs (in the appendix if they come off S5).

### Round 4 — merged fixes (applied 10 Oct)

1. **S3 category error**: headline now "Fair price ≈1.8× a model using the 0.27 average correlation of the 2027
   Finnish flood-zone matrix"; one measure only (expected loss) with year-bootstrap 90 % intervals (1.96 %: 1.6–2.2;
   triples: 2.1–4.4×); market bars, €/€1M and ORSA moved to QA; 19-zone mean, not Lapland entries (not in repo).
2. **S7 why-now vs buyer**: two-way line (standard-formula insurers: fixed correlations ignore the snow; internal-model
   insurers like If Insurance: a snow-aware number for their own model); premium insurer → reinsurer (≈€0.5–0.7M per
   €10M layer) vs licence → Tulva; year-3 revenue spoken; Nordic upside labelled assumption; OP only as a pilot wish (QA).
3. **1-in-50 wording**: "same 1-in-50 idea", level at site vs discharge at gauge; QA "same water level" fixed.
4. **Basis risk in numbers** (S7): paid 1966, 2005, 2018; missed Ostrobothnia 2012–13 and the 2024 false alarm.
5. **Quantum honesty** (S5/S6/S9, script §5, app, video): "two-river North-cluster pair" everywhere; k = 0–2; calibrated
   sampling + shallow AE, amplified circuits keep ≈0.5 of the signal on Emerald; S6 "correlation survives but
   attenuated (1.4× vs 2.5× exact)"; S5 table moved off (appendix).
6. **Number consistency**: "almost FOUR times"; app 2.8× labelled "per river pair" vs "per spring".
7. **S1 hook**: "hit flood levels" (discharge over 1-in-10), in-sample note kept.
8. **Video**: captions at 12 s / 18 s shortened, re-recorded, same cue times.
9. **Script**: 245 → 222 live words.

| Round | Reviewer | Impact | Business | Progress | Innov. | Method | Key finding |
|---|---|---|---|---|---|---|---|
| 5 | Business juror | 3.5 | 3 | 4.5 | 4 | 4.5 | "triples" vs 3.05× use different baselines; arrows read as reinsurer → Tulva; If-only buyer; basis-risk 2024 mix-up |
| 5 | Quantum juror | 3.5 | 3 | 4.5 | 3.5 | 4.5 | "simplified" missing on 14-river claim; amplification numbers differ across slide 9 / QA / results; filenames not job IDs |
| 5 | Pitch coach | 8/10 | | | | | name each ratio's baseline; "fair price" vs expected loss; de-clutter slides 5–6; jargon in §7 |

### Round 5 — merged fixes (applied 10 Oct, deck frozen)

1. **Snow-ratio baselines** (all three): slide 3 = snowy vs autumn (3.3×); slide 5 headline, video 18 s caption and
   §5 = snowy vs low snow (3.05× vs 2.75×); snowy vs normal 1.51× / 1.55× on the chart and in QA.
2. **"Simplified" 14-river model** on slide 5 and §5 (IQM's Emerald and Q50).
3. **"Expected loss", not "fair price"** on slide 3 and §3 (model comparison with the 2027 matrix's 0.27).
4. **Slide 7**: licence arrow insurer → Tulva, premium arrow insurer → reinsurer; buyers "OP, If, LähiTapiola, …";
   regulator's formula / own approved model glossed; basis risk with payouts without recorded loss; 1-in-50 footnote.
5. **Product consistency**: full payout at ≥2; staged payout only a variant in QA.
6. **De-clutter**: slide 5 loses k = 0–2 and the amplification block; slide 6 loses the 14-river block (slide 9 has
   it); slide 6 chart adds VTT Q50.
7. **One amplification statement** and **real job IDs** on slide 9; first runs footnoted.
8. Small: "This is our app"; stale QA chip lists; stale CLAIMS entries superseded; market-size QA answer.
