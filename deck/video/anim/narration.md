# Demo video narration (slide 4, voiceover)

Source of truth for the voiceover and the burned-in captions. `tts.py` reads this file, so edit it here and rerun
`python3 tts.py lines`, listen, then `python3 tts.py build` and `npm run render`. Format: `## N · scene` starts a beat (one scene of the video); each `>` line
is one caption. `say ‖ show` when the caption is written differently from how it is spoken (numbers, names); a
line without `‖` is spoken and shown as written. The end card (beat 5) shows its words on screen instead of a caption.

Every number is in CLAIMS.md (see "Numbers" at the bottom). Voice: ElevenLabs "Protégé narrator", `eleven_multilingual_v2`;
one file per sentence in `lines/`, joined into `narration.mp3` next to this file.

## 1 · Map: spring 2005
> May, two thousand five. ‖ May 2005.
> Four Lapland rivers hit flood levels together.
> Two months earlier,
> the March snow was in its top fifteen percent. ‖ the March snow was in its top 15 %.

## 2 · App: March snow outlook
> Our app turns that snow into a price.
> Set March snow to high, ‖ Set March snow to HIGH,
> and the chance our northern cover pays jumps from about two to six point four percent. ‖ and the chance our northern cover pays jumps from about 2 % to 6.4 %.

## 3 · Chip: IQM Emerald results
> Now a real quantum computer: IQM's Emerald.
> Blue is exact, purple is the chip.
> Snowy versus low-snow March:
> about three times the risk on the chip, two point seven five exact. ‖ about 3× the risk on the chip, 2.75× exact.

## 4 · Computers
> We ran it on IBM, IQM, and Finland's VTT Q fifty. ‖ We ran it on IBM, IQM and Finland's VTT Q50.

## 5 · End card
> Tulva.
> The snow warns two months early.

## Numbers (all from CLAIMS.md)
- "4 of 14 areas over their 1-in-10 level in 2005" (Ivalo 142 %, Kittilä 124 %, Rovaniemi 112 %, Tornio 101 % of
  the empirical 1-in-10 level) and "North 1 March snow: 87th percentile, top 15 %": CLAIMS "Pitch hook", "Review
  fixes" (web app 2005 replay), round-3 slide-1 line; data from web/data/app.json.
- "Two months earlier" / "two months early": 1 March → the May peak ≈ 2–2.5 months (CLAIMS "Pitch hook").
- "about 2 % → 6.4 %": North "≥2 of 5 over 1-in-50", no outlook 1.96 % (app shows 2.0 %) vs high-snow March 6.4 %
  (CLAIMS pricing section / round-4 bootstrap); shown live in the app recording.
- Chip bars (chance both rivers of the two-river North pair pass their 1-in-50 level in one spring): low-snow March
  exact 0.070 % vs IQM Emerald 0.082 % (90 % CI 0.069–0.095 %), snowy March 0.193 % vs 0.249 % (0.235–0.262 %),
  the same bars as slide 6 (CLAIMS "Review fixes", out/bootstrap_ci.json); "about 3×" = calibrated 3.05× (90 % CI
  2.6–3.6) vs exact 2.75× (CLAIMS round 5, job 01a11fa8-…).
- "IBM, IQM and Finland's VTT Q50": IBM Marrakesh, IQM Garnet, IQM Emerald, VTT Q50 (CLAIMS VTT Q50 section; Q50
  counted as run, not as a successful estimate).
