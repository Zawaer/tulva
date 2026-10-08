# Deck

Vaishnav: slides, pitch script, demo-video script and Q&A notes go here.

- `PITCH.md`: the 3:00 spoken script, slide by slide with timing marks (~410 words incl. the ~60 s demo
  voice-over). The `>` lines become each slide's speaker notes.
- `build_deck.py`: builds `Tulva_QxF2026.pptx` (16:9, editable text boxes; charts are inserted from `out/*.png`).
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

## Inserting the demo video

Slide 5 is the video slot: a still of the web app with the label "DEMO VIDEO (≈60 s) — insert recording here".
After the final rebuild, open the pptx in PowerPoint (Insert → Video → This Device) or Keynote, drop the
recording over the frame, delete the label and the still, and set the video to start automatically
(Playback → Start: Automatically) so it plays on the organisers' computer without a click. Save the result
under a new name (e.g. `Tulva_QxF2026_final.pptx`) so a rebuild doesn't overwrite it. Check the video file is
embedded, not linked, before submitting.
