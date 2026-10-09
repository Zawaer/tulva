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


W, H = 13.333, 7.5
MX = 0.6  # side margin


# --------------------------------------------------------------------------- helpers
def notes_from_pitch() -> dict[int, str]:
    """Slide number -> spoken lines (the '>' lines under '## N · ...')."""
    notes: dict[int, list[str]] = {}
    qa: dict[int, list[str]] = {}
    cur, in_qa = None, False
    for line in (DECK / "PITCH.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## (\d+)\s*·\s*(.*)$", line)
        if m:
            cur, in_qa = int(m.group(1)), False
            notes[cur] = [f"[{m.group(2).strip()}]"]
        elif cur and line.startswith(">"):
            notes[cur].append(line[1:].strip())
        elif cur and (line.startswith("Q&A only") or (in_qa and line.strip())):
            in_qa = True
            qa.setdefault(cur, []).append(line.strip())
        else:
            in_qa = False
    return {k: v[0] + "\n" + " ".join(v[1:]) + ("\n\n" + " ".join(qa[k]) if k in qa else "")
            for k, v in notes.items()}


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
    text(s, MX, 0.5, 6, 0.5, [[("Tulva", {"bold": True, "color": NAVY}),
                                ("   spring-flood risk, priced jointly", {"color": GREY, "size": 20})]],
         size=24)
    text(s, MX, 1.7, 5.6, 4.2,
         [[("In May 2005, four Lapland rivers hit flood levels ", {}), ("together.", {"color": BLUE})],
          [("Lapland's snow had warned us two months earlier.", {"size": 28, "bold": False, "color": GREY})],
          [("Flow over 1-in-10 level · snow top 15 % · in-sample", {"size": 16, "bold": False, "color": GREY})]],
         size=44, bold=True, spacing=1.05, space_after=24)
    # map, scaled up; town labels are placed as fractions of the map so they follow its size
    mx, my, mw = 6.35, 0.45, 6.4
    pic = picture(s, ASSETS / "map_2005.png", mx, my, w=mw)
    pic.line.color.rgb = LINE
    mh = pic.height / 914400
    for name, fx, fy, right in [("Ivalo", 0.588, 0.2675, False), ("Kittilä", 0.404, 0.4275, True),
                                ("Rovaniemi", 0.500, 0.602, False), ("Tornio", 0.367, 0.700, True)]:
        lw = 0.2 + 0.14 * len(name)
        x, cy = mx + fx * mw, my + fy * mh
        bx = x - lw if right else x
        rect(s, bx, cy - 0.2, lw, 0.4, LIGHT)
        text(s, bx, cy - 0.2, lw, 0.4, name, size=18, bold=True, color=NAVY, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
    text(s, mx, my + mh + 0.08, mw, 0.35, "Tulva app, spring 2005: filled = over its 1-in-10 flood level", size=14,
         color=GREY, align=PP_ALIGN.RIGHT)
    source(s, "Source: SYKE discharge 1961–2025 and 1 March snow (SWE)")
    footer(s, n)
    return s


def s2_gap(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, n, "The gap", "Finland's rivers flood together, not one at a time")
    text(s, MX, 1.5, W - 2 * MX, 0.4, "Springs when ≥4 of 14 river areas pass their 1-in-10 flood level",
         size=20, color=GREY)
    picture(s, OUT / "pitch_gap.png", MX, 1.95, W - 2 * MX, 4.2)  # scripts/pitch_charts.py
    rect(s, MX, 6.3, 0.1, 0.55, BLUE)
    text(s, MX + 0.3, 6.3, W - 2 * MX, 0.55, "Cover is bought in autumn. The snow signal comes in March.",
         size=28, bold=True, color=NAVY, anchor=MSO_ANCHOR.MIDDLE)
    source(s, "Source: SYKE 1961–2025 (+ SMHI Torne); chance = rivers flood independently, same gauge-years as observed")
    return s


def s3_product(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, n, "The product", "Tulva Index: sold in autumn, updated in March")
    rect(s, MX, 1.5, W - 2 * MX, 0.8, NAVY, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.12)
    text(s, MX + 0.4, 1.5, W - 2 * MX - 0.8, 0.8,
         "Pays if ≥2 of 5 northern rivers pass their 1-in-50 flood level",
         size=26, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    text(s, MX, 2.42, W - 2 * MX, 0.95,
         "Fair price ≈1.8× a model using the 0.27 average correlation of the 2027 Finnish flood-zone matrix",
         size=26, bold=True, color=RED, spacing=1.0)
    text(s, MX, 3.42, 9, 0.3, "EXPECTED LOSS, % OF THE LIMIT PER YEAR (90 % INTERVALS)", size=14, bold=True,
         color=BLUE)
    picture(s, OUT / "pitch_cost.png", MX, 3.75, W - 2 * MX, 2.0)  # scripts/pitch_charts.py
    rect(s, MX, 5.9, W - 2 * MX, 0.95, LIGHT)
    rect(s, MX, 5.9, 0.1, 0.95, BLUE)
    text(s, MX + 0.3, 5.9, W - 2 * MX - 0.45, 0.95,
         [[("After a snowy March the risk triples ", {"color": NAVY}),
           ("(1.96 % → 6.4 %; 90 %: 2.1–4.4×)", {"color": GREY})],
          [("Priced in autumn. In March the insurer acts on it: top-up cover, claims staff in the regions at risk.",
            {"size": 17, "bold": False})]],
         size=21, bold=True, color=NAVY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    source(s, "Sources: SYKE 1961–2025, Tulva model, year-bootstrap intervals; 0.27 = mean of the 19-zone matrix, "
              "Del. Reg. (EU) 2026/269")
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
         "Live app: joint-flood map → March snow → quantum chip → 2005 replay",
         size=18, color=WHITE, align=PP_ALIGN.CENTER)
    footer(s, n, dark=True)
    return s


def s5_quantum(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, n, "Quantum, in practice", "It runs on four real quantum computers today")
    text(s, MX, 1.55, 7.6, 0.4, "Two-river North-cluster pair on IQM Emerald", size=20,
         bold=True, color=NAVY)
    picture(s, OUT / "pitch_snow.png", MX, 2.0, 7.6, 4.6)  # scripts/pitch_charts.py
    x, w = 8.65, 4.1
    text(s, x, 1.55, w, 0.7, "CALIBRATED SAMPLING + SHALLOW AMPLITUDE ESTIMATION", size=16, color=BLUE, bold=True)
    items = [("Two-river core", "IBM Marrakesh, IQM Garnet and Emerald: 3 qubits, Grover steps k = 0–2"),
             ("14-river model", "IQM Emerald: 18 qubits, sampling only"),
             ("Amplification", "amplified circuits keep ≈0.5 of the signal on Emerald, 0.6–0.8 on IBM / Garnet"),
             ("VTT Q50, Finland's own", "3 repeats: 0.11–0.53 % vs 0.125 % exact. Calibration not yet stable")]
    y = 2.4
    for k, v in items:
        text(s, x, y, w, 0.35, k, size=20, bold=True, color=NAVY)
        text(s, x, y + 0.38, w, 0.62, v, size=16, color=GREY)
        rect(s, x, y + 1.0, w, 0.012, LINE)
        y += 1.08
    source(s, "Intervals, raw readings and job IDs: appendix")
    return s


def s6_honest(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, n, "Quantum, honestly", "Classical Monte Carlo still wins today")
    picture(s, OUT / "pitch_scaling.png", MX, 1.6, 7.2, 4.35)  # scripts/pitch_charts.py
    text(s, MX, 6.05, 7.2, 0.4, "Two-river North-cluster pair, both over 1-in-50: error vs effort", size=18,
         color=GREY)
    x, w = 8.2, 4.55
    text(s, x, 1.6, w, 0.45, "Method ready, hardware not yet", size=20, bold=True, color=BLUE)
    rect(s, x, 2.2, w, 1.7, LIGHT)
    rect(s, x, 2.2, 0.08, 1.7, RED)
    text(s, x + 0.3, 2.35, w - 0.45, 1.5, "Today: rare floods drown in noise.", size=30, bold=True, color=NAVY,
         spacing=1.0)
    text(s, x, 4.05, w, 1.5,
         [[("14 rivers, 18 qubits:", {"bold": True, "color": NAVY})],
          [("≥4 over 1-in-10: exact 10.9 %; IQM Emerald 13.8 %, VTT Q50 31 %", {})],
          [("Emerald: correlation attenuated (1.4× vs exact 2.5×); 1-in-50: 16 % vs 4.8 % exact", {})]],
         size=17, color=GREY)
    text(s, x, 5.85, w, 0.9, "Prices are computed classically; quantum is the R&D track.", size=20, bold=True,
         color=NAVY)
    return s


def s7_business(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, n, "Business", "Who pays whom, and why now")
    steps = [
        ("Buyer", "Finnish home insurers", "e.g. If Insurance", BLUE),
        ("Risk carrier", "A reinsurer", "Premium, insurer → reinsurer: ≈€0.5–0.7M a year per €10M layer", BLUE),
        ("Tulva", "Index + pricing licence", "Licence → Tulva: €25k pilot, then ~€75k a year", BLUE),
        ("Year 3", ["3–6 insurers", "× €75k ≈", "€0.2–0.45M/yr"], "Upside: Nordic snowmelt (assumption)",
         NAVY),
    ]
    gap = 0.45
    cw = (W - 2 * MX - 3 * gap) / 4
    y0, bh = 1.5, 2.6
    for i, (k, big, small, c) in enumerate(steps):
        x = MX + i * (cw + gap)
        rect(s, x, y0, cw, bh, LIGHT)
        rect(s, x, y0, cw, 0.07, c)
        text(s, x + 0.2, y0 + 0.2, cw - 0.4, 0.35, k.upper(), size=16, bold=True, color=c)
        text(s, x + 0.2, y0 + 0.58, cw - 0.4, 1.3, big, size=22, bold=True, color=NAVY, spacing=1.0)
        if small:
            text(s, x + 0.2, y0 + bh - 0.82, cw - 0.4, 0.72, small, size=14, color=GREY, anchor=MSO_ANCHOR.BOTTOM)
        if i < 3:
            text(s, x + cw, y0 + bh / 2 - 0.3, gap, 0.6, "→", size=30, bold=True, color=BLUE, align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE)
    rect(s, MX, 4.25, 0.1, 0.82, RED)
    text(s, MX + 0.3, 4.25, W - 2 * MX - 0.3, 0.82,
         [[("Why now  ", {"color": RED}),
           ("From 2027 standard-formula insurers get fixed flood correlations that ignore the snow; internal-model "
            "insurers like If Insurance get a snow-aware joint-flood number for their own model.", {})]],
         size=17, bold=True, color=NAVY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    rect(s, MX, 5.17, 0.1, 0.82, BLUE)
    text(s, MX + 0.3, 5.17, W - 2 * MX - 0.3, 0.82,
         [[("Basis risk  ", {"color": BLUE}),
           ("same 1-in-50 idea Finnish home policies use, but on river flow. Back-test: paid in the 1966, 2005 and 2018 "
            "flood springs; missed Ostrobothnia 2012–13 and 2024 (snow flag on: a false alarm).", {})]],
         size=17, bold=True, color=NAVY, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    rect(s, MX, 6.09, W - 2 * MX, 0.72, NAVY, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.12)
    text(s, MX + 0.3, 6.09, W - 2 * MX - 0.4, 0.72,
         [[("Ask  ", {"color": PALE_BLUE}),
           ("One insurer's flood claims for 8 weeks → basis-risk map + firm quote for 1 Jan 2028.", {})]],
         size=19, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    source(s, "Del. Reg. (EU) 2026/269 · back-test at 1-in-10 (at 1-in-50: 1966, 2005) · premium = model × 2.5–3.5 "
              "· prices: assumptions")
    return s


def s8_close(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, W, H, NAVY)
    text(s, MX + 0.2, 0.55, 6, 0.6, "Tulva", size=28, bold=True, color=WHITE)
    text(s, MX + 0.2, 1.4, 11.8, 2.0,
         [[("Next March, the snow will warn us ", {}), ("again.", {"color": PALE_BLUE})],
          [("This time, it will have a price.", {"size": 30, "bold": False, "color": PALE_BLUE})]],
         size=40, bold=True, color=WHITE, spacing=1.05, space_after=14)
    def chip_rows(label, chips, y, fill, line=None):
        text(s, MX + 0.2, y, 11, 0.3, label, size=13, bold=True, color=PALE_BLUE)
        x, y = MX + 0.2, y + 0.33
        for c in chips:
            w = 0.26 + text_width(c, 13)
            if x + w > W - MX:
                x, y = MX + 0.2, y + 0.5
            rect(s, x, y, w, 0.4, fill, line=line, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.5)
            text(s, x, y, w, 0.4, c, size=13, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            x += w + 0.1
    chip_rows("BUILT THIS WEEKEND", ["SYKE data pipeline", "Joint flood model", "Index pricing", "Live app",
                                     "QAE on IBM, IQM & VTT Q50"], 3.55, RGBColor(0x1A, 0x36, 0x5F))
    chip_rows("RESOURCES USED", ["SYKE open data", "IBM Marrakesh", "IQM Garnet & Emerald (Resonance)", "VTT Q50 (LUMI)", "Qrisp",
                                 "Qiskit", "AI coding agents"], 4.45, NAVY, line=PALE_BLUE)
    text(s, MX + 0.2, 5.85, 11, 0.8,
         [[("Toivo Kallio", {"bold": True}), ("  ·  ", {"color": PALE_BLUE}), ("Vaishnav Rane", {"bold": True})],
          [("Team 21 STUHI  ·  Quantum x Finance 2026, Hanken × Ultrahack", {"color": PALE_BLUE, "size": 16})]],
         size=20, color=WHITE, space_after=4)
    footer(s, n, dark=True)
    return s


def s9_appendix(prs, n):
    """Hardware details moved off slide 5 (intervals, raw readings, job IDs) so the main slides stay readable."""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, n, "Appendix", "Hardware runs in detail", title_size=28)
    hdr = ["Chip", "Circuit", "Exact", "Raw", "Calibrated (90 % CI)", "Job"]
    rows = [
        ["IBM Marrakesh", "North-cluster pair, 3 qubits, k = 0–2", "0.125 %", "0.262 %", "0.149 % (0.140–0.157)",
         "db3tddsvf2bc73ctoprg"],
        ["IQM Garnet", "North-cluster pair, 3 qubits, k = 0–2", "0.125 %", "0.368 %", "0.164 % (0.147–0.180)",
         "01a11cc3-7f6c…"],
        ["IQM Emerald", "Snowy / low March ratio, same pair, k = 0–2", "2.75×", "1.3×", "3.05× (2.6–3.6)",
         "product-…075338Z"],
        ["IQM Emerald", "14 rivers ≥4 over 1-in-10, 18 q / 44 CZ", "10.9 %", "–", "13.8 % (readout-corr.)",
         "01a11cd4-da38…"],
        ["IQM Emerald", "14 rivers ≥2 over 1-in-50, same circuit", "4.8 %", "–", "16.0 % (fails)",
         "01a11f9b-c62a…"],
        ["IQM Emerald", "Control: independent circuit, ≥4 over 1-in-10", "4.4 %", "–", "9.7 % (noise fattens tails)",
         "…T135910Z"],
        ["VTT Q50", "Same pair, 3 repeats: not stable", "0.125 %", "1.48–1.58 %",
         "0.47 / 0.53 / 0.11 %", "7d20d8ac / a6fb9d52 / 381179fb"],
        ["VTT Q50", "14 rivers ≥4 over 1-in-10, 18 q / 49 CZ", "10.9 %", "34.2 %", "31.2 % (readout-corr.)",
         "9cdb0158-7574…"],
    ]
    cols = [1.65, 4.05, 0.9, 1.3, 2.55, 1.8]
    widths = [c * (W - 2 * MX) / sum(cols) for c in cols]
    y = 1.6
    for r_i, row in enumerate([hdr] + rows):
        x = MX
        if r_i:
            rect(s, MX, y + 0.5, W - 2 * MX, 0.012, LINE)
        for c_i, (cell, cw) in enumerate(zip(row, widths)):
            text(s, x, y, cw - 0.1, 0.5, cell, size=(12 if c_i == 5 else 14) if r_i else 13, bold=(r_i == 0 or c_i == 4),
                 color=BLUE if r_i == 0 else (GREY if c_i == 5 else NAVY), anchor=MSO_ANCHOR.MIDDLE)
            x += cw
        y += 0.52
    text(s, MX, y + 0.05, W - 2 * MX, 1.2,
         ["Calibrated = noise-aware MLAE, two known-answer calibration circuits in the same job; bootstrap 90 % intervals. "
          "IBM / Garnet intervals exclude exact (+19 % / +31 % bias). Pair = two rivers with identical North-cluster "
          "loadings and 1-in-50 trigger. Classical Monte Carlo at the same budget is more precise (±0.004 pp).",
          "Signal kept by amplification (k = 1 / 2): Emerald 0.56–0.59 / 0.44; VTT Q50 0.12–0.19 / 0.05–0.06. "
          "Q50 zero-calibration offset moved 0.002 → 0.006 between repeats, driving the 5× spread."],
         size=12, color=GREY, space_after=4)
    footer(s, n)
    return s


SLIDES = [s1_hook, s2_gap, s3_product, s4_demo, s5_quantum, s6_honest, s7_business, s8_close, s9_appendix]


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
