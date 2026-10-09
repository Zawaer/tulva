"""Voiceover for the demo video: narration.md -> ElevenLabs -> narration.mp3 + src/timing.json.

    python3 deck/video/anim/tts.py            # reuse the cached ElevenLabs take if the text is unchanged
    python3 deck/video/anim/tts.py --fresh    # ask ElevenLabs for a new take
    python3 deck/video/anim/tts.py --voice <voice_id>

Needs ELEVENLABS_API_KEY in the repo's git-ignored .env (never printed) and ffmpeg. One request for the whole
narration (so the voice stays consistent), with character timestamps. The take is then cut at the pauses between
beats and re-joined with a little extra silence, so each scene starts on its beat; src/timing.json holds the beat
and caption times the Remotion scenes read.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CACHE = HERE / "build"          # git-ignored: raw take + alignment
MP3 = HERE / "narration.mp3"
TIMING = HERE / "src" / "timing.json"

VOICE = "XrExE9yKIg1WjnnlVkGX"  # ElevenLabs premade "Matilda": calm, clear, professional (alternatives: Daniel
#                                 onwK4e9ZLuTAKqWW03F9, Alice Xb7hH8MSUJpSbSDYk0k2, River SAz9YHcvj6GT2YYXdXww)
MODEL = "eleven_multilingual_v2"
SETTINGS = {"stability": 0.6, "similarity_boost": 0.8, "style": 0.0, "use_speaker_boost": True, "speed": 1.08}
LEAD = 0.5      # s of silence before the first word
GAP = 0.4       # extra s of silence added at each beat boundary (scene transition)
TAIL = 1.2      # s of silence after the last word (end card holds)


def parse(md: Path) -> list[dict]:
    beats: list[dict] = []
    for line in md.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## (\d+)\s*·\s*(.+)$", line)
        if m:
            beats.append({"n": int(m.group(1)), "title": m.group(2).strip(), "chunks": []})
        elif line.startswith("> ") and beats:
            say, _, show = line[2:].partition("‖")
            beats[-1]["chunks"].append({"say": say.strip(), "show": (show or say).strip()})
    return [b for b in beats if b["chunks"]]


def api_key() -> str:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("ELEVENLABS_API_KEY="):
            return line.split("=", 1)[1].strip().strip("'\"")
    raise SystemExit("ELEVENLABS_API_KEY missing from .env")


def synthesize(text: str, voice: str) -> dict:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128"
    body = json.dumps({"text": text, "model_id": MODEL, "voice_settings": SETTINGS}).encode()
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"xi-api-key": api_key(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:  # the body never contains the key
        raise SystemExit(f"ElevenLabs HTTP {e.code}: {e.read().decode()[:400]}")


def ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         check=True, capture_output=True, text=True).stdout
    return float(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--voice", default=VOICE)
    args = ap.parse_args()

    beats = parse(HERE / "narration.md")
    # Beats are paragraphs (a natural pause); captions inside a beat are joined with spaces.
    spans, text = [], ""
    for bi, b in enumerate(beats):
        if bi:
            text += "\n\n"
        for ci, c in enumerate(b["chunks"]):
            if ci:
                text += " "
            spans.append((bi, len(text), len(text) + len(c["say"]), c))
            text += c["say"]

    key = hashlib.sha256(json.dumps([text, args.voice, MODEL, SETTINGS]).encode()).hexdigest()[:12]
    CACHE.mkdir(exist_ok=True)
    raw_mp3, raw_json = CACHE / f"take-{key}.mp3", CACHE / f"take-{key}.json"
    if args.fresh or not raw_json.exists():
        res = synthesize(text, args.voice)
        raw_mp3.write_bytes(base64.b64decode(res["audio_base64"]))
        raw_json.write_text(json.dumps({"text": text, "voice": args.voice, "model": MODEL, "settings": SETTINGS,
                                        "alignment": res["alignment"]}, ensure_ascii=False))
        print(f"new take {raw_mp3.name}")
    else:
        print(f"cached take {raw_mp3.name}")
    al = json.loads(raw_json.read_text())["alignment"]
    chars, t0s, t1s = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    assert "".join(chars) == text, "alignment does not match the text"

    def first_sound(a: int, b: int) -> float:
        return next(t0s[i] for i in range(a, b) if chars[i].strip())

    def last_sound(a: int, b: int) -> float:
        return next(t1s[i] for i in range(b - 1, a - 1, -1) if chars[i].strip() and chars[i] not in ".,:;!?")

    raw_len = duration(raw_mp3)
    # Beat i of the raw take runs from cut[i] to cut[i+1]; cut in the middle of the pause between beats.
    b_first = [first_sound(*next((s, e) for bi, s, e, _ in spans if bi == k)) for k in range(len(beats))]
    b_last = [last_sound(*[(s, e) for bi, s, e, _ in spans if bi == k][-1]) for k in range(len(beats))]
    cuts = [0.0] + [(b_last[k] + b_first[k + 1]) / 2 for k in range(len(beats) - 1)] + [raw_len]

    # New time = raw time + LEAD + GAP × (beat index); pieces joined with silences in between.
    shift = [LEAD + GAP * k for k in range(len(beats))]
    parts, inputs = [], []
    work = CACHE / "parts"
    work.mkdir(exist_ok=True)

    def silence(seconds: float, name: str) -> Path:
        ffmpeg("-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", f"{seconds:.3f}", "-c:a", "pcm_s16le",
               str(work / name))
        return work / name

    inputs.append(silence(LEAD, "lead.wav"))
    for k in range(len(beats)):
        p = work / f"beat{k}.wav"
        ffmpeg("-i", str(raw_mp3), "-ss", f"{cuts[k]:.3f}", "-to", f"{cuts[k + 1]:.3f}", "-ac", "1", "-ar", "44100",
               "-c:a", "pcm_s16le", str(p))
        inputs.append(p)
        if k < len(beats) - 1:
            inputs.append(silence(GAP, f"gap{k}.wav"))
    inputs.append(silence(TAIL, "tail.wav"))
    lst = work / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in inputs))
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(lst), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100",
           "-c:a", "libmp3lame", "-b:a", "192k", str(MP3))
    total = duration(MP3)

    chunks = [{"beat": bi, "say": c["say"], "show": c["show"],
               "start": round(first_sound(s, e) + shift[bi], 3), "end": round(last_sound(s, e) + shift[bi], 3)}
              for bi, s, e, c in spans]
    words = []
    for bi, s, e, _ in spans:  # word-level times (for emphasis cues inside a scene)
        for m in re.finditer(r"\S+", text[s:e]):
            a, b = s + m.start(), s + m.end()
            words.append({"beat": bi, "w": m.group(), "start": round(t0s[a] + shift[bi], 3),
                          "end": round(t1s[b - 1] + shift[bi], 3)})
    beat_t = [{"n": b["n"], "title": b["title"], "start": round(cuts[k] + shift[k] - (LEAD if k == 0 else GAP / 2), 3),
               "speech_start": round(b_first[k] + shift[k], 3), "speech_end": round(b_last[k] + shift[k], 3)}
              for k, b in enumerate(beats)]
    for k in range(len(beat_t)):
        beat_t[k]["end"] = beat_t[k + 1]["start"] if k + 1 < len(beat_t) else round(total, 3)
    beat_t[0]["start"] = 0.0
    TIMING.write_text(json.dumps({"voice": args.voice, "model": MODEL, "take": raw_mp3.name, "total": round(total, 3),
                                  "beats": beat_t, "chunks": chunks, "words": words}, indent=1, ensure_ascii=False))
    n_words = len(re.findall(r"\S+", " ".join(c["show"] for c in chunks)))
    speech = sum(b["speech_end"] - b["speech_start"] for b in beat_t)
    print(f"{MP3.relative_to(ROOT)}: {total:.2f} s; {n_words} caption words, {60 * n_words / speech:.0f} wpm while "
          f"speaking; beats " + ", ".join(f"{b['n']}: {b['start']:.2f}–{b['end']:.2f}" for b in beat_t))


if __name__ == "__main__":
    main()
