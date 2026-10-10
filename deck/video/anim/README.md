# Demo video with voiceover (slide 4)

`deck/video/tulva_demo_anim.mp4`: 45 s, 1920×1080, 30 fps, ElevenLabs voiceover, burned-in captions. It is on
slide 4 (`VIDEO` in `deck/build_deck.py`); the silent `deck/video/tulva_demo.mp4` is kept as a backup. Every number is in CLAIMS.md (section "Demo video with voiceover").

| Beat | Time | Scene | Source |
|---|---|---|---|
| 1 | 0–10 s | Animated map: May 2005, Ivalo, Kittilä, Rovaniemi, Tornio over their 1-in-10 level together; two months earlier the North's 1 March snow was in its top 15 % (87th percentile) | `web/data/app.json`, Natural Earth |
| 2 | 10–20 s | **Real web app** recording: "No outlook" → click "High snow", North 2.0 % → 6.4 % | `record_clips.mjs` |
| 3 | 20–33 s | IQM Emerald vs exact bars, as on slide 6: chance both rivers flood, low-snow vs snowy March (chip bars with 90 % intervals); ratio 3.05× chip vs 2.75× exact | `out/bootstrap_ci.json` |
| 4 | 33–39 s | IBM Marrakesh, IQM Garnet, IQM Emerald, VTT Q50 | CLAIMS.md "VTT Q50" |
| 5 | 39–45 s | End card "Tulva. The snow warns two months early." | |

## Rebuild
```
cd deck/video/anim && npm install                 # once (node_modules is git-ignored)
python3 tts.py lines                              # narration.md -> lines/NN_*.mp3, one file per sentence
python3 tts.py check                              # speech-to-text each line (needs the speech_to_text permission)
python3 tts.py build                              # lines -> narration.mp3 + src/timing.json
python3 export_data.py                            # web/data + out/ -> src/data.json (asserts the spoken numbers)
python3 -m http.server 3141 --directory ../../../web &   # only if re-recording the app
node record_clips.mjs                             # -> public/app_snow.mp4 + src/clips.json (after tts.py)
npm run render                                    # -> ../tulva_demo_anim.mp4
npm run studio                                    # optional: preview in the browser
```
- **Voice:** edit `narration.md` (one `>` line = one caption; `say ‖ show` when spoken and written differ), then
  `python3 tts.py lines` (only changed lines are regenerated), listen, then `build`. Key: `ELEVENLABS_API_KEY` in the
  repo's git-ignored `.env.local` or `.env`, from the account that owns the voice. Voice "Protégé narrator (clone)"
  (`AesrdOgpgZSXUSHb7gw3`, an Instant Voice Clone of the original Voice Design voice), `eleven_multilingual_v2`, stability 0.55, similarity 0.8, style 0.25, speed 1.12.
  "Tulva" is also spliced from a Finnish sentence (`lines/10_tulva.fi.mp3`); `USE_SPLICE` in `tts.py` picks it.
  Scenes, the app recording's click and the captions all follow `src/timing.json`, so after a new build re-run
  `record_clips.mjs` and render.
- **Timing:** lines are joined with 0.7 s between sentences and 1.7 s between beats (2.5 s hold on the end card),
  normalised to about −16 LUFS.
- Render: PNG frames → H.264 yuv420p (BT.709), a keyframe every second (`remotion.config.ts`), so PowerPoint plays and
  scrubs it cleanly.
- The app clip is recorded frame by frame with the installed Google Chrome (viewport 1280×720 at 2.5× pixel ratio, so
  the zoom stays sharp); the app's own bar transitions are stepped through the DevTools Animation domain.
