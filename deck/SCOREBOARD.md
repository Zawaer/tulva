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

### Round 3 — merged fixes, ranked by expected score gain

1. **S3 March bar / wording** (business + coach). Price is fixed in autumn, so "After a snowy March 16–23 %" reads as untradeable; reframe as the insurer's March action (claims staffing, top-up quote, ORSA evidence) and say it plainly ("after a snowy March, fair risk triples"). Pick one framing (fair price vs under-priced) and align "≈2×" with the true 1.8×. Est. +0.5–1 Business.
2. **S7 revenue + regulation wording** (business + coach). One revenue model, not "fee per deal" and "~€75k/yr"; frame €0.1–0.6M as a pilot wedge or show capital/premium at stake. "Regulator judged snowmelt NOT linked" overstates: 0% is cross-border only (domestic matrix mean 0.27). Drop "No vendor model uses this winter's snow". Say "the insurer If". Est. +0.5 Business/Impact.
3. **Name basis risk + the 1-in-50 match** (business). One line on S3/S7: trigger = same 1-in-50 test as all 7 Finnish home policies (docs/flood_terms_check.md); basis risk tested against claims in pilot step 1. Est. +0.5 Innov./Business.
4. **S1 map vs hook** (business + coach). Four dots filled, script says two rivers; highlight only Kittilä and Ivalo. Remove "(out/backtest.json)" footer. Small but cheap.
5. **S5 density** (coach; business notes Emerald vs Garnet mix-up). Keep chart + "3.05× vs 2.75×"; move CI lines, bias, qubit/gate box, job ID to appendix. ⚠ **Methodology flag:** don't delete the bias/CI caveats outright. Move them to the appendix/QA and label which chip each number comes from, or Methodology drops (the business juror already noted the +19/+31 % bias CIs exclude exact).
6. **Jargon** (coach). "shots" → "runs"; slide 2 "independence" → "chance"; explain "regulator's average correlation" (S3).

⚠ **Progress flag:** none of these cuts remove evidence. Keep S8 build list and job IDs (in the appendix if they come off S5).
