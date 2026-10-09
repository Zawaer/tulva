# Task for a Claude Code session on Toivo's Mac: animated demo video with voiceover

Give this file to Claude Code in the repo root on the Mac ("Do docs/VIDEO_TASK.md").

## Setup on the Mac
1. `git pull`
2. Put the ElevenLabs key in `.env` (git-ignored) as `ELEVENLABS_API_KEY=...`. Never print, log or commit it.
3. Start the web app: `python3 -m http.server 3141 --directory web` (open http://localhost:3141 to check).

## Goal
A polished 40–45 s demo video with an ElevenLabs voiceover that replaces the 37 s silent clip on slide 4,
keeping the whole pitch under 3 min (script: deck/PITCH.md). Read CLAUDE.md first.

- **A demo, not an ad.** Mix animated scenes with real recordings of our web app (Playwright; see
  deck/video/record_demo.mjs). Only real numbers from CLAIMS.md; no new claims, no "quantum advantage".
- **Suggested beats:**
  1. Animated map of Finland's 14 river areas lighting up together in May 2005.
  2. Real app: March snow set high → the northern price jumps.
  3. Real IQM chip results: dots, red = both rivers flood; low vs snowy March; "snowy vs low snow ≈3× on chip,
     2.75× exact".
  4. "Ran on IBM, IQM and Finland's VTT Q50."
  5. End card: "Tulva: the snow warns two months early."
- **Burned-in captions** that match the voice (safety if the hall sound fails).
- **Tool:** Remotion in `deck/video/anim/` (add `node_modules` to .gitignore), or any reliable code-to-video route.
  Use the deck colours from deck/build_deck.py (navy / blue / red).
- **Voice:** ElevenLabs, clear calm neutral English. Narration ≈90–100 words; save it to
  `deck/video/anim/narration.md` and the mp3 next to it. Sync scenes to the audio.
- **Output:** `deck/video/tulva_demo_anim.mp4` (with audio, 1920×1080, 30 fps). Do NOT overwrite
  `deck/video/tulva_demo.mp4` (fallback) and do NOT change deck/build_deck.py or PITCH.md until Toivo approves.
- **Check:** extract frames at several timestamps and look at them; captions legible, nothing overlapping, audio
  length matches.

## After Toivo approves
- Point slide 4 in deck/build_deck.py at the new file, rebuild the deck.
- Replace PITCH.md §4's live narration cues with "(video plays with voiceover)" and re-check total timing ≤ 2:50.

## Commits
`git pull --rebase` before every push. Commit source and the mp4 (not node_modules) as
`git -c user.name="Toivo" -c user.email="toivo@stuhi.org"`, with messages ending
`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
