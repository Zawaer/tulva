"""Voiceover for the demo video: narration.md -> one ElevenLabs file per sentence -> narration.mp3 + src/timing.json.

    python3 deck/video/anim/tts.py lines          # generate missing/changed lines into lines/ (one request at a time)
    python3 deck/video/anim/tts.py lines --fresh  # regenerate every line
    python3 deck/video/anim/tts.py check          # speech-to-text each line file: what ElevenLabs hears
    python3 deck/video/anim/tts.py build --dry-run  # print the timeline only
    python3 deck/video/anim/tts.py build          # join the lines -> narration.mp3 + src/timing.json

A line is one sentence of narration.md (consecutive `>` caption lines up to a full stop). Each is generated on its
own with the neighbouring sentences as context, saved as lines/NN_slug.mp3 with its character alignment in
lines/NN_slug.json, so a single line can be redone. Foreign words in SPLICE are also generated inside a sentence of
their own language, cut out by the alignment and spliced into the English line (lines/NN_slug.fi.mp3); build uses
the spliced file for the words in USE_SPLICE (pick by ear). Needs ELEVENLABS_API_KEY in the repo's
git-ignored .env.local or .env (never printed), and ffmpeg.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import subprocess
import unicodedata
import urllib.error
import urllib.request
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LINES = HERE / "lines"
WORK = HERE / "build"           # git-ignored scratch for the join
MP3 = HERE / "narration.mp3"
TIMING = HERE / "src" / "timing.json"

VOICE = "AesrdOgpgZSXUSHb7gw3"  # "Protégé narrator (clone)": Instant Voice Clone of Toivo's Voice Design voice
#                                 gVAop54BusNm4YRoeTzF (old account) from 95 s of its clips; poised British female
MODEL = "eleven_multilingual_v2"
SETTINGS = {"stability": 0.55, "similarity_boost": 0.8, "style": 0.25, "speed": 1.12}
SPLICE = {"Tulva": ("fi", "Tämä on tulva.")}   # word -> (language tag, native carrier sentence; lower case,
#                                                capitalised "Tulva" is read as the name "Tuula")
USE_SPLICE: set[str] = {"Tulva"}               # words whose spliced version goes into the build
#                                                ("Tulva.": STT hears the English take as "Tolva")
LEAD, SENT_GAP, BEAT_GAP, TAIL = 0.7, 0.7, 1.7, 2.5   # s of silence: start, between sentences, between beats, end
PRE, POST = 0.06, 0.22          # s kept before the first / after the last sound of a line when joining


# ------------------------------------------------------------------------------------------------- narration.md
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


def sentences(beats: list[dict]) -> list[dict]:
    """Group each beat's caption chunks into sentences; keep each chunk's character span in its sentence."""
    out: list[dict] = []
    for bi, b in enumerate(beats):
        cur = None
        for c in b["chunks"]:
            if cur is None:
                cur = {"beat": bi, "text": "", "chunks": []}
            if cur["text"]:
                cur["text"] += " "
            cur["chunks"].append({**c, "a": len(cur["text"]), "b": len(cur["text"]) + len(c["say"])})
            cur["text"] += c["say"]
            if c["say"].rstrip().endswith((".", "!", "?")):
                out.append(cur)
                cur = None
        if cur:
            out.append(cur)
    for i, s in enumerate(out):
        slug = unicodedata.normalize("NFKD", s["text"]).encode("ascii", "ignore").decode().lower()
        s["n"] = i + 1
        s["stem"] = f"{i + 1:02d}_" + "-".join(re.findall(r"[a-z0-9]+", slug)[:4])
    return out


# ------------------------------------------------------------------------------------------------- ElevenLabs
def api_key() -> str:
    for name in (".env.local", ".env"):
        p = ROOT / name
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.startswith("ELEVENLABS_API_KEY="):
                    return line.split("=", 1)[1].strip().strip("'\"")
    raise SystemExit("ELEVENLABS_API_KEY missing from .env.local / .env")


def request(url: str, body: bytes, ctype: str) -> dict:
    req = urllib.request.Request(url, data=body, method="POST", headers={"xi-api-key": api_key(), "Content-Type": ctype})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:  # the body never contains the key
        raise SystemExit(f"ElevenLabs HTTP {e.code}: {e.read().decode()[:400]}")


def synthesize(text: str, prev: str | None = None, nxt: str | None = None) -> dict:
    body = {"text": text, "model_id": MODEL, "voice_settings": SETTINGS}
    if prev:
        body["previous_text"] = prev
    if nxt:
        body["next_text"] = nxt
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128"
    return request(url, json.dumps(body).encode(), "application/json")


def transcribe(path: Path, lang: str | None = None) -> str:
    b = uuid.uuid4().hex
    hint = f"--{b}\r\nContent-Disposition: form-data; name=\"language_code\"\r\n\r\n{lang}\r\n" if lang else ""
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"model_id\"\r\n\r\nscribe_v1\r\n{hint}"
            f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{path.name}\"\r\n"
            f"Content-Type: audio/mpeg\r\n\r\n").encode() + path.read_bytes() + f"\r\n--{b}--\r\n".encode()
    return request("https://api.elevenlabs.io/v1/speech-to-text", body, f"multipart/form-data; boundary={b}")["text"]


# ------------------------------------------------------------------------------------------------- audio helpers
def ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         check=True, capture_output=True, text=True).stdout
    return float(out)


def digest(text: str) -> str:
    return hashlib.sha256(json.dumps([text, VOICE, MODEL, SETTINGS]).encode()).hexdigest()[:12]


def first_sound(al: dict, a: int, b: int) -> float:
    return next(al["character_start_times_seconds"][i] for i in range(a, b) if al["characters"][i].strip())


def last_sound(al: dict, a: int, b: int) -> float:
    ch = al["characters"]
    return next(al["character_end_times_seconds"][i] for i in range(b - 1, a - 1, -1)
                if ch[i].strip() and ch[i] not in ".,:;!?")


def generate(stem: str, text: str, prev: str | None, nxt: str | None, fresh: bool) -> tuple[Path, dict, bool]:
    mp3, meta = LINES / f"{stem}.mp3", LINES / f"{stem}.json"
    h = digest(text)
    if not fresh and meta.exists() and json.loads(meta.read_text())["hash"] == h and mp3.exists():
        return mp3, json.loads(meta.read_text()), False
    res = synthesize(text, prev, nxt)
    mp3.write_bytes(base64.b64decode(res["audio_base64"]))
    al = res["alignment"]
    assert "".join(al["characters"]) == text, f"alignment does not match: {text}"
    m = {"text": text, "hash": h, "voice": VOICE, "model": MODEL, "settings": SETTINGS, "context": [prev, nxt],
         "duration": round(duration(mp3), 3), "alignment": al}
    meta.write_text(json.dumps(m, ensure_ascii=False, indent=1))
    return mp3, m, True


def splice(stem: str, line: dict, word: str, native_mp3: Path, native: dict) -> Path:
    """Replace `word` in the English line with the same word cut from the native-language sentence."""
    al, nal = line["alignment"], native["alignment"]
    i = re.search(rf"\b{re.escape(word)}\b", line["text"]).start()
    j = re.search(rf"\b{re.escape(word)}\b", native["text"], re.I).start()
    pad0, pad1 = 0.04, 0.12
    ws = max(0.0, al["character_start_times_seconds"][i] - pad0)
    we = al["character_end_times_seconds"][i + len(word) - 1] + pad1
    ns = max(0.0, nal["character_start_times_seconds"][j] - pad0)
    ne = min(native["duration"], nal["character_end_times_seconds"][j + len(word) - 1] + pad1)
    out = LINES / f"{stem}.{SPLICE[word][0]}.mp3"
    f = 0.015
    ffmpeg("-i", str(LINES / f"{stem}.mp3"), "-i", str(native_mp3), "-filter_complex",
           f"[0:a]atrim=0:{ws:.3f},asetpts=PTS-STARTPTS[a];"
           f"[1:a]atrim={ns:.3f}:{ne:.3f},asetpts=PTS-STARTPTS,afade=t=in:d={f},afade=t=out:st={ne - ns - f:.3f}:d={f}[b];"
           f"[0:a]atrim={we:.3f},asetpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=0:a=1[o]",
           "-map", "[o]", "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "192k", str(out))
    # alignment of the spliced file: the word's characters take the native timing, later characters shift
    shift = (ne - ns) - (we - ws)
    t0, t1 = list(al["character_start_times_seconds"]), list(al["character_end_times_seconds"])
    for k in range(len(t0)):
        if i <= k < i + len(word):
            t0[k] = ws + nal["character_start_times_seconds"][j + k - i] - ns
            t1[k] = ws + nal["character_end_times_seconds"][j + k - i] - ns
        elif k >= i + len(word):
            t0[k] += shift
            t1[k] += shift
    meta = {**line, "spliced": {"word": word, "from": native_mp3.name}, "duration": round(duration(out), 3),
            "alignment": {"characters": al["characters"], "character_start_times_seconds": t0,
                          "character_end_times_seconds": t1}}
    out.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    return out


# ------------------------------------------------------------------------------------------------- commands
def cmd_lines(sents: list[dict], fresh: bool) -> None:
    LINES.mkdir(exist_ok=True)
    keep = set()
    for k, s in enumerate(sents):          # one request at a time (plan limit: 5 concurrent)
        prev = sents[k - 1]["text"] if k else None
        nxt = sents[k + 1]["text"] if k + 1 < len(sents) else None
        mp3, meta, new = generate(s["stem"], s["text"], prev, nxt, fresh)
        keep |= {mp3.name, mp3.with_suffix(".json").name}
        print(f"{'new   ' if new else 'cached'} {mp3.name:42s} {meta['duration']:5.2f} s  {s['text']}")
        for word, (lang, carrier) in SPLICE.items():
            if re.search(rf"\b{re.escape(word)}\b", s["text"]):
                nstem = f"{lang}_{word.lower()}"
                nmp3, nmeta, nnew = generate(nstem, carrier, None, None, fresh)
                out = splice(s["stem"], meta, word, nmp3, nmeta)
                keep |= {nmp3.name, nmp3.with_suffix(".json").name, out.name, out.with_suffix(".json").name}
                print(f"{'new   ' if nnew else 'cached'} {nmp3.name:42s} {nmeta['duration']:5.2f} s  {carrier}")
                print(f"spliced {out.name:41s} {duration(out):5.2f} s  {s['text']} ('{word}' from {nmp3.name})")
    for p in LINES.iterdir():               # drop files of lines that no longer exist
        if p.name not in keep:
            p.unlink()
            print(f"removed {p.name}")


def cmd_check() -> None:
    norm = lambda x: re.sub(r"[^a-z0-9äöå ]", "", x.lower()).split()
    for mp3 in sorted(LINES.glob("*.mp3")):
        meta = json.loads(mp3.with_suffix(".json").read_text())
        tag = SPLICE[meta["spliced"]["word"]][0] if "spliced" in meta else mp3.stem.split("_")[0]
        heard = transcribe(mp3, {"fi": "fin"}.get(tag))   # spliced / native files: hint the language
        ok = "ok  " if norm(heard) == norm(meta["text"]) else "DIFF"
        print(f"{ok} {mp3.name:42s} wrote: {meta['text']}\n     {'':42s} heard: {heard}")


def cmd_build(beats: list[dict], sents: list[dict], dry: bool) -> None:
    placed, t, inputs = [], LEAD, []
    WORK.mkdir(exist_ok=True)
    for k, s in enumerate(sents):
        tag = next((SPLICE[w][0] for w in USE_SPLICE if re.search(rf"\b{re.escape(w)}\b", s["text"])), None)
        stem = s["stem"] + (f".{tag}" if tag else "")
        mp3, meta = LINES / f"{stem}.mp3", json.loads((LINES / f"{stem}.json").read_text())
        if meta["text"] != s["text"] or meta.get("hash") != digest(s["text"]):
            raise SystemExit(f"{mp3.name} is out of date: run `tts.py lines` first")
        al, n = meta["alignment"], len(s["text"])
        a = max(0.0, first_sound(al, 0, n) - PRE)
        b = min(meta["duration"], last_sound(al, 0, n) + POST)
        if k:
            t += BEAT_GAP if s["beat"] != sents[k - 1]["beat"] else SENT_GAP
        placed.append({**s, "mp3": mp3, "al": al, "off": t - a, "t0": t, "t1": t + b - a, "cut": (a, b)})
        t += b - a
    total = t + TAIL

    def at(p: dict, i: int, start: bool) -> float:
        key = "character_start_times_seconds" if start else "character_end_times_seconds"
        return round(p["al"][key][i] + p["off"], 3)

    chunks, words = [], []
    for p in placed:
        for c in p["chunks"]:
            chunks.append({"beat": p["beat"], "say": c["say"], "show": c["show"],
                           "start": round(first_sound(p["al"], c["a"], c["b"]) + p["off"], 3),
                           "end": round(last_sound(p["al"], c["a"], c["b"]) + p["off"], 3)})
        for m in re.finditer(r"\S+", p["text"]):
            words.append({"beat": p["beat"], "w": m.group(), "start": at(p, m.start(), True), "end": at(p, m.end() - 1, False)})
    beat_t = []
    for k, b in enumerate(beats):
        ps = [p for p in placed if p["beat"] == k]
        prev_end = placed[placed.index(ps[0]) - 1]["t1"] if k else None
        beat_t.append({"n": b["n"], "title": b["title"], "start": 0.0 if k == 0 else round((prev_end + ps[0]["t0"]) / 2, 3),
                       "speech_start": round(first_sound(ps[0]["al"], 0, len(ps[0]["text"])) + ps[0]["off"], 3),
                       "speech_end": round(last_sound(ps[-1]["al"], 0, len(ps[-1]["text"])) + ps[-1]["off"], 3)})
    for k in range(len(beat_t)):
        beat_t[k]["end"] = beat_t[k + 1]["start"] if k + 1 < len(beat_t) else round(total, 3)
    print("\n".join(f"  {p['t0']:6.2f}–{p['t1']:6.2f}  beat {p['beat'] + 1}  {p['mp3'].name}" for p in placed))
    print(f"total {total:.2f} s; beats " + ", ".join(f"{b['n']}: {b['start']:.2f}–{b['end']:.2f}" for b in beat_t))
    if dry:
        return

    def silence(sec: float, name: str) -> Path:
        ffmpeg("-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", f"{sec:.3f}", "-c:a", "pcm_s16le", str(WORK / name))
        return WORK / name

    inputs.append(silence(LEAD, "lead.wav"))
    for k, p in enumerate(placed):
        if k:
            inputs.append(silence(p["t0"] - placed[k - 1]["t1"], f"gap{k}.wav"))
        piece = WORK / f"line{k:02d}.wav"
        ffmpeg("-i", str(p["mp3"]), "-af", f"atrim={p['cut'][0]:.3f}:{p['cut'][1]:.3f},asetpts=PTS-STARTPTS,"
               f"afade=t=out:st={p['cut'][1] - p['cut'][0] - 0.03:.3f}:d=0.03", "-ac", "1", "-ar", "44100",
               "-c:a", "pcm_s16le", str(piece))
        inputs.append(piece)
    inputs.append(silence(TAIL, "tail.wav"))
    (WORK / "list.txt").write_text("".join(f"file '{p}'\n" for p in inputs))
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(WORK / "list.txt"), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
           "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "192k", str(MP3))  # -16 LUFS: loud enough for a hall PA
    TIMING.write_text(json.dumps({"voice": VOICE, "model": MODEL, "settings": SETTINGS,
                                  "lines": [p["mp3"].name for p in placed], "total": round(duration(MP3), 3),
                                  "beats": beat_t, "chunks": chunks, "words": words}, indent=1, ensure_ascii=False))
    print(f"{MP3.relative_to(ROOT)}: {duration(MP3):.2f} s, {TIMING.relative_to(ROOT)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["lines", "check", "build"])
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    beats = parse(HERE / "narration.md")
    sents = sentences(beats)
    if args.cmd == "lines":
        cmd_lines(sents, args.fresh)
    elif args.cmd == "check":
        cmd_check()
    else:
        cmd_build(beats, sents, args.dry_run)


if __name__ == "__main__":
    main()
