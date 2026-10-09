# Deck

Vaishnav: slides, pitch script, demo-video script and Q&A notes go here.

- `PITCH.md`: the spoken script, slide by slide with timing marks (≈2:31 at 135 wpm, ≈2:44 at 120 wpm: 230 live words + the 44.5 s demo
  video, which has its own voiceover). The `>` lines become each slide's speaker notes.
- `build_deck.py`: builds `Tulva_QxF2026.pptx` (16:9, editable text boxes; charts are inserted from `out/*.png`, the demo video from `deck/video/`).
- `Tulva_QxF2026.pdf`, `preview/slide-N.png`: exports for checking layout.

## Rebuild (after charts in `out/` or the script change)

```
.venv/bin/python deck/build_deck.py          # pptx only
.venv/bin/python deck/build_deck.py --pdf    # + PDF and PNG previews (needs LibreOffice + pdftoppm)
```

Needs `python-pptx` and Pillow in the project venv
(`VIRTUAL_ENV=$PWD/.venv uv pip install python-pptx`). For `--pdf`:
`apt-get install -y --no-install-recommends libreoffice-impress poppler-utils`.
Every number on a slide must come from `CLAIMS.md`; edit numbers in `build_deck.py`, not in the pptx, or they
are lost on the next rebuild.

## Demo video (embedded)

The PPTX contains the demo video: `build_deck.py` embeds whatever `deck/video/tulva_demo_anim.mp4` is on disk at
build time into slide 4 (poster frame = a still from 9.6 s in, `POSTER_AT`, extracted with imageio-ffmpeg), so after
re-rendering just rebuild. The file is embedded, not linked. Playback in PowerPoint/Keynote starts on click by default; if it
should start by itself, set Playback → Start: Automatically and save under a new name (e.g.
`Tulva_QxF2026_final.pptx`) so a rebuild doesn't overwrite it. Google Slides does not autoplay (or reliably play)
video embedded in an uploaded PPTX, so test in PowerPoint or Keynote. The PDF/PNG previews only show the poster.

Slides 1–9 are the stage deck (one idea per slide, title ≤ 8 words, body ≥ 28 pt, no footnotes). Slides 2, 3 and 6
draw their bars natively in `build_deck.py` (values from CLAIMS.md / `out/bootstrap_ci.json`); slide 5 shows the QAE
circuit `out/stage_qae_circuit.png` from `scripts/qae_circuit_figure.py`; slide 7 uses `out/stage_scaling.png` from
`scripts/pitch_charts.py`. Caveats, intervals, sources, back-test years and job ids live on backup slides 10–12 (Q&A
only; slide 10 uses `out/pitch_cost.png`) and in QA.md.

## Demo video
`deck/video/tulva_demo_anim.mp4` (slide 4): 44.5 s, ElevenLabs voiceover ("Protégé narrator (clone)") and burned-in
captions; animated 2005 map → real app recording (March snow set to high) → the real IQM Emerald shots → the four
computers → end card. Built with Remotion in `deck/video/anim/` (see its README; narration in `narration.md`). The
presenter says nothing during it.

Backup: `deck/video/tulva_demo.mp4`, a 37-second scripted walkthrough of the demo app at 1920×1080, page zoom 1.5, short
burned-in captions: map → snow outlook set to high → real IQM Emerald shots (low vs snowy March) → a simplified (two-level) 14-river model on
one chip (1-in-10 run, ≥4 row highlighted) → 2005 replay. It is silent (it was narrated live before the voiceover
video). To use it, point `VIDEO` in `build_deck.py` back at it and restore the live cues in PITCH.md §4. Re-record after the app changes (app served on :3141):
`source /data/chats/s_7z3ZoxoroN/env.sh; PLAYWRIGHT_PKG=/data/chats/s_7z3ZoxoroN/talkoot/package.json node deck/video/record_demo.mjs`,
then trim the lead-in it prints and convert: `ffmpeg -ss <first caption s> -i deck/video/raw/<newest>.webm -c:v libx264
-crf 22 -pix_fmt yuv420p -movflags +faststart -an deck/video/tulva_demo.mp4` (ffmpeg from `imageio_ffmpeg`).
