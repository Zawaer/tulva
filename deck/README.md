# Deck

Vaishnav: slides, pitch script, demo-video script and Q&A notes go here.

- `PITCH.md`: the 3:00 spoken script, slide by slide with timing marks (~410 words incl. the ~60 s demo
  voice-over). The `>` lines become each slide's speaker notes.
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
build time into slide 5 (poster frame = a still from 2 s in, extracted with imageio-ffmpeg), so after re-recording
just rebuild. The file is embedded, not linked. Playback in PowerPoint/Keynote starts on click by default; if it
should start by itself, set Playback → Start: Automatically and save under a new name (e.g.
`Tulva_QxF2026_final.pptx`) so a rebuild doesn't overwrite it. Google Slides does not autoplay (or reliably play)
video embedded in an uploaded PPTX, so test in PowerPoint or Keynote. The PDF/PNG previews only show the poster.

Slides 2 and 3 use big pitch charts `out/pitch_gap.png` and `out/pitch_cost.png` from
`scripts/pitch_charts.py` (values read from `out/joint_counts.json` and `out/pricing.json`); rerun it before the
deck if those numbers change.

## Demo video (draft)
`deck/video/tulva_demo.mp4`: a 61-second scripted walkthrough of the demo app at 1920×1080 with burned-in captions
(map → snow outlook → index card → real quantum results → the 14-area Emerald chart → 2005 replay).
Re-record after the app changes with:
`source /data/chats/s_7z3ZoxoroN/env.sh; node deck/video/record_demo.mjs`, then convert the webm in
deck/video/raw/ to MP4 (see the ffmpeg line in the git history). It's silent: add the voice-over from PITCH.md
slide 5, or keep it captions-only.
