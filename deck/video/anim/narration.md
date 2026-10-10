# Demo video narration (slide 2, voiceover)

Source of truth for the voiceover and the burned-in captions. `tts.py` reads this file, so edit it here and rerun
`python3 tts.py lines`, listen, then `python3 tts.py build` and `npm run render`. Format: `## N · scene` starts a beat (one scene of the video); each `>` line
is one caption. `say ‖ show` when the caption is written differently from how it is spoken (numbers, names); a
line without `‖` is spoken and shown as written. The end card (last beat) shows its words on screen instead of a caption.

Every number is in CLAIMS.md (see "Numbers" at the bottom). Voice: ElevenLabs "Protégé narrator", `eleven_multilingual_v2`;
one file per sentence in `lines/`, joined into `narration.mp3` next to this file.

## 1 · App: March snow outlook
> Our app turns that snow into a price.
> Set March snow to high, ‖ Set March snow to HIGH,
> and the chance our northern cover pays jumps from about two to six point four percent. ‖ and the chance our northern cover pays jumps from about 2 % to 6.4 %.

## 2 · Chip: IQM Emerald results
> Now a real quantum computer: IQM's Emerald.
> Blue is exact, purple is the chip.
> Snowy versus low-snow March:
> about three times the risk on the chip, two point seven five exact. ‖ about 3× the risk on the chip, 2.75× exact.

## 3 · Computers
> We ran it on IBM, IQM, and Finland's VTT Q fifty. ‖ We ran it on IBM, IQM and Finland's VTT Q50.

## 4 · End card
> Tulva.
> The snow warns two months early.

## Numbers (all from CLAIMS.md)
- "Two months early": 1 March → the May peak ≈ 2–2.5 months (CLAIMS "Pitch hook").
- "about 2 % → 6.4 %": North "≥2 of 5 over 1-in-50", no outlook 1.96 % (app shows 2.0 %) vs high-snow March 6.4 %
  (CLAIMS pricing section / round-4 bootstrap); shown live in the app recording.
- Chip bars (chance both rivers of the two-river North pair pass their 1-in-50 level in one spring): low-snow March
  exact 0.070 % vs IQM Emerald 0.082 % (90 % CI 0.069–0.095 %), snowy March 0.193 % vs 0.249 % (0.235–0.262 %),
  the same bars as slide 6 (CLAIMS "Review fixes", out/bootstrap_ci.json); "about 3×" = calibrated 3.05× (90 % CI
  2.6–3.6) vs exact 2.75× (CLAIMS round 5, job 01a11fa8-…).
- "IBM, IQM and Finland's VTT Q50": IBM Marrakesh, IQM Garnet, IQM Emerald, VTT Q50 (CLAIMS VTT Q50 section; Q50
  counted as run, not as a successful estimate).
