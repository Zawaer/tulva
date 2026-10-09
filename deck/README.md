# Deck

Vaishnav: slides, pitch script, demo-video script and Q&A notes go here.

- `PITCH.md`: the spoken script, slide by slide with timing marks (≈2:43 at 135 wpm: 228 live words + the 37 s demo video,
  which the presenter narrates live). The `>` lines become each slide's speaker notes.
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

The PPTX now contains the demo video: `build_deck.py` embeds whatever `deck/video/tulva_demo.mp4` is on disk at
build time into slide 4 (poster frame = a still from 2 s in, extracted with imageio-ffmpeg), so after re-recording
just rebuild. The file is embedded, not linked. Playback in PowerPoint/Keynote starts on click by default; if it
should start by itself, set Playback → Start: Automatically and save under a new name (e.g.
`Tulva_QxF2026_final.pptx`) so a rebuild doesn't overwrite it. Google Slides does not autoplay (or reliably play)
video embedded in an uploaded PPTX, so test in PowerPoint or Keynote. The PDF/PNG previews only show the poster.

Slides 2 and 3 use big pitch charts `out/pitch_gap.png` and `out/pitch_cost.png` from
`scripts/pitch_charts.py` (values read from `out/joint_counts.json` and `out/pricing.json`); rerun it before the
deck if those numbers change.

## Demo video
`deck/video/tulva_demo.mp4`: a 37-second scripted walkthrough of the demo app at 1920×1080, page zoom 1.5, short
burned-in captions: map → snow outlook set to high → real IQM Emerald shots (low vs snowy March) → all 14 areas on
one chip (1-in-10 run, ≥4 row highlighted) → 2005 replay. It is silent: the presenter narrates it live (PITCH.md,
slide 4). Re-record after the app changes (app served on :3141):
`source /data/chats/s_7z3ZoxoroN/env.sh; PLAYWRIGHT_PKG=/data/chats/s_7z3ZoxoroN/talkoot/package.json node deck/video/record_demo.mjs`,
then trim the lead-in it prints and convert: `ffmpeg -ss <first caption s> -i deck/video/raw/<newest>.webm -c:v libx264
-crf 22 -pix_fmt yuv420p -movflags +faststart -an deck/video/tulva_demo.mp4` (ffmpeg from `imageio_ffmpeg`).
