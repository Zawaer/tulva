"""Build deck/Tulva_QxF2026.pptx (16:9, editable) from out/*.png and deck/PITCH.md.

Rerun after the charts in out/ change:
    .venv/bin/python deck/build_deck.py            # pptx only
    .venv/bin/python deck/build_deck.py --pdf      # + PDF and PNG previews (needs LibreOffice + pdftoppm)

Every number on a slide comes from CLAIMS.md (outside sources are cited on the slide).
Speaker notes are the `>` lines of deck/PITCH.md for the matching slide number.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DECK = ROOT / "deck"
ASSETS = DECK / "assets"  # generated crops, rebuilt every run
PPTX = DECK / "Tulva_QxF2026.pptx"
VIDEO = DECK / "video" / "tulva_demo.mp4"  # embedded on slide 4; whatever is on disk at build time

NAVY = RGBColor(0x0B, 0x1F, 0x3A)
BLUE = RGBColor(0x1F, 0x6F, 0xEB)
RED = RGBColor(0xD1, 0x3B, 0x2F)
GREY = RGBColor(0x6B, 0x72, 0x80)
LIGHT = RGBColor(0xF3, 0xF6, 0xFA)
LINE = RGBColor(0xDD, 0xE3, 0xEA)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
PALE_BLUE = RGBColor(0xA9, 0xC8, 0xF5)
FONT = "Arial"

# >>> TEAM DECISION: licence price shown on the Business slide, e.g. "€60k". None = no price shown.
LICENCE_PRICE: str | None = None
# <<<

W, H = 13.333, 7.5
MX = 0.6  # side margin


# --------------------------------------------------------------------------- helpers
def notes_from_pitch() -> dict[int, str]:
    """Slide number -> spoken lines (the '>' lines under '## N · ...')."""
    notes: dict[int, list[str]] = {}
    cur = None
    for line in (DECK / "PITCH.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## (\d+)\s*·\s*(.*)$", line)
        if m:
            cur = int(m.group(1))
            notes[cur] = [f"[{m.group(2).strip()}]"]
        elif cur and line.startswith(">"):
            notes[cur].append(line[1:].strip())
    return {k: v[0] + "\n" + " ".join(v[1:]) for k, v in notes.items()}


def text(slide, x, y, w, h, runs, size=18, color=NAVY, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, spacing=1.0, space_after=0):
    """Add a text box. `runs` is a str, or a list of paragraphs; each paragraph is a str or a
    list of (text, {size,color,bold}) tuples."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    paras = runs if isinstance(runs, list) else [runs]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        p.space_after = Pt(space_after)
        pieces = para if isinstance(para, list) else [(para, {})]
        for t, st in pieces:
            r = p.add_run()
            r.text = t
            f = r.font
            f.name = FONT
            f.size = Pt(st.get("size", size))
            f.bold = st.get("bold", bold)
            f.color.rgb = st.get("color", color)
    return tb


def rect(slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.RECTANGLE, radius=None):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(1)
    s.shadow.inherit = False
    style = s._element.find(qn("p:style"))
    if style is not None:
        s._element.remove(style)
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    return s


def picture(slide, path: Path, x, y, w=None, h=None):
    """Insert an image, fitting it inside (w, h) and keeping its aspect ratio; centred in the box."""
    iw, ih = Image.open(path).size
    if w and h:
        scale = min(w / iw, h / ih)
        pw, ph = iw * scale, ih * scale
        x, y = x + (w - pw) / 2, y + (h - ph) / 2
    elif w:
        pw, ph = w, w * ih / iw
    else:
        pw, ph = h * iw / ih, h
    return slide.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(pw), Inches(ph))


def header(slide, n, kicker, title, title_size=30):
    text(slide, MX, 0.36, 9, 0.3, kicker.upper(), size=16, color=BLUE, bold=True)
    text(slide, MX, 0.72, W - 2 * MX, 0.75, title, size=title_size, bold=True)
    footer(slide, n)


def text_width(t, size):
    """Width in inches of `t` in Arial (Liberation Sans has the same metrics); rough estimate if not installed."""
    try:
        from PIL import ImageFont
        f = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", size * 10)
        return f.getlength(t) / 720
    except OSError:
        return 0.105 * len(t) * size / 16


def footer(slide, n, dark=False):
    c = PALE_BLUE if dark else GREY
    text(slide, W - MX - 2.0, H - 0.42, 2.0, 0.25,
         [[("Tulva", {"bold": True, "color": WHITE if dark else NAVY}), (f"   {n}", {})]],
         size=12, color=c, align=PP_ALIGN.RIGHT)


def source(slide, s, dark=False):
    # citations only (not read aloud); kept at 12 pt so they stay out of the way
    text(slide, MX, H - 0.44, W - 2 * MX - 2.2, 0.3, s, size=12, color=PALE_BLUE if dark else GREY)


def stat(slide, x, y, w, big, label, color=NAVY, big_size=40, label_size=16, label_h=0.6):
    text(slide, x, y, w, 0.75, big, size=big_size, bold=True, color=color)
    text(slide, x, y + big_size / 72 * 1.18, w, label_h, label, size=label_size, color=GREY)


def crops():
    """Crops of the web-app screenshot used on slides 1 and 4."""
    ASSETS.mkdir(exist_ok=True)
    shot = Image.open(OUT / "web_shot.png")
    # Year-replay map, 2005 selected (Lapland: Ivalo, Kittilä, Rovaniemi, Tornio lit).
    shot.crop((690, 4160, 1226, 4600)).save(ASSETS / "map_2005.png")
    # Product card (Tulva Index, North cluster).
    shot.crop((60, 112 + 1760, 1220, 640 + 1760)).save(ASSETS / "app_product.png")


# --------------------------------------------------------------------------- slides
def s1_hook(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    text(s, MX, 0.5, 7, 0.5, [[("Tulva", {"bold": True, "color": NAVY}),
                                ("   spring-flood risk, priced jointly", {"color": GREY, "size": 18})]],
         size=22)
    text(s, MX, 1.85, 6.8, 3.2,
         [[("In May 2005, Kittilä and Ivalo flooded ", {}), ("together.", {"color": BLUE})],
          [("The snow had warned us two months earlier.", {"size": 24, "bold": False, "color": GREY})]],
         size=42, bold=True, spacing=1.05, space_after=18)
    text(s, MX, 4.6, 6.4, 0.9,
         "The 1 March snow flagged 2005 in advance. Then both rivers flooded in the same spring.",
         size=18, color=NAVY)
    pic = picture(s, ASSETS / "map_2005.png", 7.6, 0.95, w=5.1)
    pic.line.color.rgb = LINE
    # the screenshot's own town labels are ~7 pt on the slide: cover them with 16 pt labels
    for name, x, cy, right in [("Ivalo", 10.6, 2.07, False), ("Kittilä", 9.66, 2.74, True),
                               ("Rovaniemi", 10.15, 3.47, False), ("Tornio", 9.47, 3.88, True)]:
        lw = 0.16 + 0.125 * len(name)
        bx = x - lw if right else x
        rect(s, bx, cy - 0.17, lw, 0.34, LIGHT)
        text(s, bx, cy - 0.17, lw, 0.34, name, size=16, bold=True, color=NAVY, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
    text(s, 7.6, 0.95 + pic.height / 914400 + 0.1, 5.1, 0.35, "Tulva app: spring 2005 replay",
         size=16, color=GREY, align=PP_ALIGN.RIGHT)
    source(s, "Source: SYKE discharge 1961–2025 and 1 March snow (SWE); Tulva back-test (out/backtest.json)")
    footer(s, n)
    return s


def s2_gap(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, n, "The gap", "Finland's rivers flood together, not one at a time")
    picture(s, OUT / "pitch_gap.png", MX, 1.6, 7.9, 5.25)  # scripts/pitch_charts.py
    x = 8.95
    text(s, x, 1.65, 3.8, 0.6, "Springs with ≥4 of 14 areas over their 1-in-10 level",
         size=16, color=GREY)
    stat(s, x, 2.3, 3.8, "15.4 %", "observed (10 of 65 years)", NAVY, 38)
    stat(s, x, 3.3, 3.8, "12.2 %", "Tulva joint model", BLUE, 38)
    stat(s, x, 4.3, 3.8, "3.9 %", "if areas were independent", RED, 38)
    rect(s, x, 5.4, 3.8, 0.02, LINE)
    text(s, x, 5.55, 3.8, 1.2, "Reinsurance renews 1 January, before the snow signal arrives.",
         size=18, bold=True, color=NAVY)
    source(s, "Source: SYKE 1961–2025 (+ SMHI Torne), Tulva model (exact); vesi.fi / OP (1-in-50 rule)")
    return s


def s3_product(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, n, "The product", "Tulva Index: bought in winter, pays in spring")
    rect(s, MX, 1.55, W - 2 * MX, 0.95, NAVY, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.12)
    text(s, MX + 0.4, 1.55, W - 2 * MX - 0.8, 0.95,
         [[("Pays €10M", {"color": WHITE}),
           (" if ≥2 of 5 northern gauges pass their 1-in-50 level this spring", {"color": WHITE, "bold": False})]],
         size=24, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    text(s, MX, 2.62, 6, 0.3, "MARKET PRICE PER YEAR", size=16, bold=True, color=BLUE)
    picture(s, OUT / "pitch_cost.png", MX, 2.95, W - 2 * MX, 2.85)  # scripts/pitch_charts.py
    # innovativeness, said once
    rect(s, MX, 5.92, 0.08, 0.72, BLUE)
    text(s, MX + 0.28, 5.88, W - 2 * MX - 0.3, 0.8,
         [[("Today's cat models assume how areas flood together. ", {"color": GREY, "bold": False}),
           ("Tulva measures it from 65 years of river data, ties it to this winter's snow, and prices it as a cover.",
            {})]],
         size=18, bold=True, color=NAVY, anchor=MSO_ANCHOR.MIDDLE)
    source(s, "Source: SYKE 1961–2025, Tulva model (exact). Market price = 2.5–3.5× expected payout "
              "(AM Best, flood ILS)")
    return s


def poster_frame() -> Path:
    """First-seconds still of the demo video, shown before playback starts."""
    import imageio_ffmpeg
    ASSETS.mkdir(exist_ok=True)
    out = ASSETS / "video_poster.png"
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-ss", "2", "-i", str(VIDEO),
                    "-frames:v", "1", str(out)], check=True)
    return out


def s4_demo(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, W, H, NAVY)
    fh = 5.85
    fw = fh * 16 / 9
    fx, fy = (W - fw) / 2, 0.55
    if VIDEO.exists():
        s.shapes.add_movie(str(VIDEO), Inches(fx), Inches(fy), Inches(fw), Inches(fh),
                           poster_frame_image=str(poster_frame()), mime_type="video/mp4")
    else:  # placeholder if the recording is missing
        rect(s, fx, fy, fw, fh, RGBColor(0x14, 0x2B, 0x4D), line=PALE_BLUE)
        picture(s, ASSETS / "app_product.png", fx + 0.15, fy + 0.15, fw - 0.3, fh - 0.3)
        print(f"warning: {VIDEO.relative_to(ROOT)} missing, slide 4 has a placeholder")
    text(s, 1.0, 6.55, W - 2.0, 0.4,
         "Live app: joint-flood map → March snow → index price → quantum runs → 2005 replay",
         size=16, color=WHITE, align=PP_ALIGN.CENTER)
    footer(s, n, dark=True)
    return s


def s5_quantum(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, n, "Quantum, in practice",
           "The full model fits on a chip today; amplitude estimation works on a 3-qubit piece of it.",
           title_size=24)
    picture(s, OUT / "pitch_loader.png", MX, 1.8, 7.6, 4.35)  # scripts/pitch_charts.py
    text(s, MX, 6.25, 7.6, 0.4, "At the 1-in-10 level the chip reproduces the joint tail.", size=16, color=NAVY)
    x, w = 8.6, 4.15
    text(s, x, 1.8, w, 0.3, "ALL 14 AREAS ON IQM EMERALD", size=16, color=BLUE, bold=True)
    stat(s, x, 2.1, 1.6, "18", "qubits", NAVY, 36, 16, 0.3)
    stat(s, x + 1.7, 2.1, 2.4, "44", "two-qubit gates", NAVY, 36, 16, 0.3)
    rect(s, x, 3.3, w, 0.015, LINE)
    text(s, x, 3.42, w, 0.3, "AMPLITUDE ESTIMATION", size=16, color=BLUE, bold=True)
    text(s, x, 3.75, w, 0.3, "Kittilä and Ivalo both pass 1-in-50", size=16, color=GREY)
    rows = [("Exact", "0.125 %", NAVY), ("IBM Marrakesh", "0.148 %", BLUE), ("IQM Garnet", "0.163 %", BLUE)]
    y = 4.1
    for lab, cal, c in rows:
        text(s, x, y + 0.08, 2.4, 0.4, lab, size=18, bold=True)
        text(s, x + 2.6, y, 1.55, 0.5, cal, size=24, bold=True, color=c, align=PP_ALIGN.RIGHT)
        rect(s, x, y + 0.52, w, 0.012, LINE)
        y += 0.56
    text(s, x, 5.9, w, 0.8, [[("Snow signal on the chip: ", {"bold": True}),
                             ("snowy vs low March 3.1× (exact 2.7×)", {"color": BLUE, "bold": True})]],
         size=16, color=NAVY)
    source(s, "IQM Emerald job 01a11cd4…, readout-corrected; IBM / IQM values calibrated (20 / 4 side-by-side "
              "copies); snow: Emerald, 10 copies")
    return s

def s6_honest(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, n, "Quantum, honestly", "Classical Monte Carlo still wins today")
    picture(s, OUT / "pitch_scaling.png", MX, 1.65, 7.6, 4.6)  # scripts/pitch_charts.py
    text(s, MX, 6.35, 7.6, 0.4, "Kittilä and Ivalo both pass 1-in-50: estimation error vs effort",
         size=16, color=GREY)
    x, w = 8.75, 4.0
    text(s, x, 1.75, w, 0.4, "Where quantum could pay off", size=20, bold=True, color=BLUE)
    items = [("Fault-tolerant hardware", "~8k logical qubits needed"),
             ("Expensive models", "a hydrology model per scenario"),
             ("More work per price", "many perils, daily repricing")]
    y = 2.45
    for a, b in items:
        rect(s, x, y + 0.08, 0.08, 0.8, BLUE)
        text(s, x + 0.3, y, w - 0.3, 1.1, [[(a, {"bold": True})], [(b, {"color": GREY})]], size=18)
        y += 1.2
    rect(s, x, 6.0, w, 0.02, LINE)
    text(s, x, 6.1, w, 0.5, "Error: QAE ∝ 1/N, Monte Carlo ∝ 1/√N", size=16, color=NAVY)
    source(s, "Source: Tulva simulations (qae-sim) + IBM Marrakesh / IQM Garnet runs; Chakrabarti et al., "
              "Quantum 5, 463 (2021)")
    return s


def s7_business(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, n, "Business", "Who buys, why, and why now")
    cols = [
        ("Who buys", "Finnish non-life insurers", "For the flood risk they keep. "
         "Four groups write 91 % of the market. Then reinsurers and ILS investors."),
        ("How we earn", "Engine licence", (f"{LICENCE_PRICE} per insurer per year. " if LICENCE_PRICE else "")
         + "Pricing and trigger engine, licensed per insurer or reinsurer. Fee on placed covers."),
        ("Why now", "30 Jan 2027", "Finland gets a Solvency II flood capital factor: insurers need a "
         "joint-flood view now. The engine is quantum-ready as hardware matures."),
        ("Scale", "Finland → Nordics → Europe", "Same engine, any snowmelt or river region. "
         "Gävle 2021: SEK 1.9bn claims. Storm Boris 2024: €2.15bn insured."),
    ]
    cw, gap = 2.85, 0.193
    for i, (k, head, body) in enumerate(cols):
        x = MX + i * (cw + gap)
        c = RED if k == "Why now" else BLUE
        rect(s, x, 1.65, cw, 4.25, LIGHT)
        rect(s, x, 1.65, cw, 0.07, c)
        text(s, x + 0.2, 1.9, cw - 0.4, 0.3, k.upper(), size=16, bold=True, color=c)
        text(s, x + 0.2, 2.3, cw - 0.4, 1.1, head, size=22, bold=True, color=NAVY, spacing=0.95)
        text(s, x + 0.2, 3.45, cw - 0.4, 2.4, body, size=16, color=NAVY, spacing=1.05)
    rect(s, MX, 6.1, 0.08, 0.45, BLUE)
    text(s, MX + 0.25, 6.1, W - 2 * MX, 0.45,
         [[("Ask  ", {"color": BLUE}),
           ("First step: a paid pilot with one Finnish insurer this autumn, before the 1 January reinsurance buy.",
            {})]],
         size=17, bold=True, color=NAVY, anchor=MSO_ANCHOR.MIDDLE)
    source(s, "Sources: Finance Finland 2024; Del. Reg. (EU) 2026/269; Finansinspektionen 2023 (Gävle); "
              "PERILS 2025 (Boris)")
    return s

def s8_close(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, W, H, NAVY)
    text(s, MX + 0.2, 0.55, 6, 0.6, "Tulva", size=28, bold=True, color=WHITE)
    text(s, MX + 0.2, 1.35, 11.5, 1.7,
         [[("Tulva prices Finland's spring floods as a ", {}), ("joint risk", {"color": PALE_BLUE}),
           (", and runs it on real quantum hardware.", {})]],
         size=38, bold=True, color=WHITE, spacing=1.05)
    def chip_rows(label, chips, y, fill, line=None):
        text(s, MX + 0.2, y, 11, 0.35, label, size=16, bold=True, color=PALE_BLUE)
        x, y = MX + 0.2, y + 0.4
        for c in chips:
            w = 0.32 + text_width(c, 16)
            if x + w > W - MX:
                x, y = MX + 0.2, y + 0.62
            rect(s, x, y, w, 0.5, fill, line=line, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.5)
            text(s, x, y, w, 0.5, c, size=16, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            x += w + 0.1
    chip_rows("BUILT THIS WEEKEND", ["SYKE data pipeline", "Joint flood model", "Index pricing",
                                     "QAE on IBM & IQM"], 3.05, RGBColor(0x1A, 0x36, 0x5F))
    chip_rows("RESOURCES USED", ["SYKE open data", "IBM Marrakesh", "IQM Garnet & Emerald (Resonance)", "Qrisp",
                                 "Qiskit", "AI coding agents"], 4.15, NAVY, line=PALE_BLUE)
    text(s, MX + 0.2, 5.9, 11, 0.8,
         [[("Toivo Kallio", {"bold": True}), ("  ·  ", {"color": PALE_BLUE}), ("Vaishnav Rane", {"bold": True})],
          [("Team 21 STUHI  ·  Quantum x Finance 2026, Hanken × Ultrahack", {"color": PALE_BLUE, "size": 16})]],
         size=20, color=WHITE, space_after=4)
    footer(s, n, dark=True)
    return s


SLIDES = [s1_hook, s2_gap, s3_product, s4_demo, s5_quantum, s6_honest, s7_business, s8_close]


def build():
    crops()
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(W), Inches(H)
    notes = notes_from_pitch()
    for i, fn in enumerate(SLIDES, start=1):
        slide = fn(prs, i)
        slide.notes_slide.notes_text_frame.text = notes.get(i, "")
    prs.save(PPTX)
    print(f"wrote {PPTX.relative_to(ROOT)} ({len(SLIDES)} slides)")


def export():
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        sys.exit("LibreOffice not found: apt-get install -y --no-install-recommends libreoffice-impress")
    subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(DECK), str(PPTX)],
                   check=True, capture_output=True)
    pdf = PPTX.with_suffix(".pdf")
    prev = DECK / "preview"
    shutil.rmtree(prev, ignore_errors=True)
    prev.mkdir()
    subprocess.run(["pdftoppm", "-png", "-r", "90", str(pdf), str(prev / "slide")], check=True)
    print(f"wrote {pdf.relative_to(ROOT)} and {len(list(prev.glob('*.png')))} previews in deck/preview/")


if __name__ == "__main__":
    build()
    if "--pdf" in sys.argv:
        export()
