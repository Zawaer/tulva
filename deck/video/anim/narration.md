# Demo video narration (slide 4, voiceover)

Source of truth for the voiceover and the burned-in captions. `tts.py` reads this file, so edit it here and rerun
`python3 tts.py` (then `npm run render`). Format: `## N · scene` starts a beat (one scene of the video); each `>` line
is one caption. `say ‖ show` when the caption is written differently from how it is spoken (numbers, names); a
line without `‖` is spoken and shown as written. The end card (beat 5) shows its words on screen instead of a caption.

Every number is in CLAIMS.md (see "Numbers" at the bottom). Voice: ElevenLabs `eleven_multilingual_v2`, calm
neutral English; the mp3 is `narration.mp3` next to this file.

## 1 · Map: spring 2005
> First of March, two thousand five. ‖ 1 March 2005.
> Lapland's snowpack is in its top fifteen percent. ‖ Lapland's snowpack is in its top 15 %.
> Two months later,
> four Lapland rivers pass their flood levels together.

## 2 · App: March snow outlook
> Our app turns that snow into a price.
> Set March snow to high, ‖ Set March snow to HIGH,
> and the chance our northern cover pays jumps from two to six point four percent. ‖ and the chance our northern cover pays jumps from 2 % to 6.4 %.

## 3 · Chip: IQM Emerald shots
> Each square is one shot on IQM's Emerald quantum computer.
> Red: both rivers flood.
> Snowy versus low snow:
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
- "Two months": 1 March → the May peak ≈ 2–2.5 months (CLAIMS "Pitch hook").
- "2 % → 6.4 %": North "≥2 of 5 over 1-in-50", no outlook 1.96 % (app shows 2.0 %) vs high-snow March 6.4 %
  (CLAIMS pricing section / round-4 bootstrap); shown live in the app recording.
- "13 vs 31 red of 8,000 shots": IQM Emerald raw shot grid, low vs snowy March (CLAIMS round-3 line);
  "about 3×" = calibrated 3.05× (90 % CI 2.6–3.6) vs exact 2.75× (CLAIMS round 5, job 01a11fa8-…).
- "IBM, IQM and Finland's VTT Q50": IBM Marrakesh, IQM Garnet, IQM Emerald, VTT Q50 (CLAIMS VTT Q50 section; Q50
  counted as run, not as a successful estimate).
