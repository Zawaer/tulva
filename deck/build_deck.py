"""Build deck/Tulva_QxF2026.pptx (16:9, editable) from out/*.png and deck/PITCH.md.

Rerun after the charts in out/ change:
    .venv/bin/python deck/build_deck.py            # pptx only
    .venv/bin/python deck/build_deck.py --pdf      # + PDF and PNG previews (needs LibreOffice + pdftoppm)

Every number on a slide comes from CLAIMS.md. Slides 1-8 are the whole deck (one idea each, big type); caveats,
intervals and sources are in QA.md. Order: hook, demo video, gap, product, circuit, classical still wins, who pays,
close.
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
VIDEO = DECK / "video" / "tulva_demo_anim.mp4"  # slide 2: 35 s demo with voiceover (deck/video/anim/);
#                                               deck/video/tulva_demo.mp4 (silent, 37 s) is kept as a backup
POSTER_AT = 1.2  # s into the video: the live app, "Our app turns that snow into a price."

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
    # Spoken lines only, so the notes can be memorised; Q&A details live in QA.md.
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
# Stage deck (slides 1-8): one idea per slide, title <= 8 words, body >= 28 pt, big numbers >= 60 pt.
# Caveats, intervals and sources live on the backup slides (10-12) and in QA.md.
TITLE_SIZE = 40
BODY = 28
PURPLE = RGBColor(0x82, 0x50, 0xDF)  # IQM chip, as in scripts/pitch_charts.py


def title(slide, n, t, dark=False):
    text(slide, MX, 0.5, W - 2 * MX, 0.8, t, size=TITLE_SIZE, bold=True, color=WHITE if dark else NAVY)
    footer(slide, n, dark=dark)


def s1_hook(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    text(s, MX, 0.5, 6, 0.5, "Tulva", size=28, bold=True)
    text(s, MX, 1.75, 5.6, 3.6,
         [[("May 2005: four Lapland rivers flooded ", {}), ("together.", {"color": BLUE})]],
         size=48, bold=True, spacing=1.05)
    text(s, MX, 4.55, 5.6, 0.6, "The March snow warned us.", size=32, color=GREY)
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
    footer(s, n)
    return s


def s3_gap(prs, n):
    """Observed 15.4 % vs chance 3.9 % of springs with >=4 of 14 areas over 1-in-10 (CLAIMS.md, slide 2 lines)."""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    title(s, n, "Rivers flood together, not one at a time")
    text(s, MX, 1.4, 9, 0.5, "Springs when ≥4 of 14 rivers flood", size=BODY, color=GREY)
    base, scale, bw = 5.55, 2.55 / 15.4, 2.6  # inches per percentage point
    for x, v, lab, c in [(1.2, 15.4, "Observed", NAVY), (4.6, 3.9, "By chance", GREY)]:
        h = v * scale
        rect(s, x, base - h, bw, h, c)
        text(s, x - 0.3, base - h - 0.85, bw + 0.6, 0.8, f"{v:.1f} %", size=44, bold=True, color=c,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.BOTTOM)
        text(s, x - 0.3, base + 0.1, bw + 0.6, 0.5, lab, size=BODY, color=NAVY, align=PP_ALIGN.CENTER)
    rect(s, 0.9, base, 6.6, 0.02, LINE)
    text(s, 8.0, 2.3, 4.7, 1.8, "≈4×", size=120, bold=True, color=RED, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE)
    text(s, 8.0, 4.15, 4.7, 0.6, "as often as chance", size=BODY, color=GREY, align=PP_ALIGN.CENTER)
    rect(s, MX, 6.3, 0.1, 0.6, BLUE)
    text(s, MX + 0.3, 6.3, 10, 0.6, "Cover is bought in autumn, before the snow.", size=30, bold=True,
         anchor=MSO_ANCHOR.MIDDLE)
    return s


def s4_product(prs, n):
    """North '>=2 of 5 over 1-in-50' expected loss: standard assumption (one 0.27 correlation, the mean of the 2027
    19-zone matrix) 1.11 %, Tulva 1.96 %, snowy March 6.4 %."""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    title(s, n, "Tulva Index: pays if ≥2 northern rivers flood")
    rows = [("Standard assumption (regulator's average link)", 1.11, "1.11 %", GREY), ("Tulva", 1.96, "1.96 %", BLUE),
            ("Tulva, after a snowy March", 6.4, "6.4 %", NAVY)]
    scale, y = 5.4 / 6.4, 1.65
    for lab, v, vt, c in rows:
        text(s, MX, y, 8.3, 0.5, lab, size=BODY, color=NAVY)
        rect(s, MX, y + 0.55, v * scale, 0.6, c)
        text(s, MX + v * scale + 0.2, y + 0.5, 2.2, 0.7, vt, size=36, bold=True, color=c,
             anchor=MSO_ANCHOR.MIDDLE)
        y += 1.4
    text(s, MX, 5.9, 8, 0.5, "Expected loss, % of limit per year", size=24, color=GREY)
    rect(s, 9.0, 1.65, 3.73, 4.4, LIGHT)
    text(s, 9.0, 1.95, 3.73, 2.0, "×3", size=130, bold=True, color=RED, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE)
    text(s, 9.2, 4.1, 3.33, 1.5, "chance of a big joint flood after a snowy March", size=BODY, bold=True, color=NAVY,
         align=PP_ALIGN.CENTER)
    return s



def autoplay(slide, spid: int) -> None:
    """Make the embedded video start automatically when the slide appears (PowerPoint 'Start: Automatically')."""
    from lxml import etree
    ns = "http://schemas.openxmlformats.org/presentationml/2006/main"
    xml = (f'<p:timing xmlns:p="{ns}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
           '<p:childTnLst><p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq">'
           '<p:childTnLst><p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/>'
           '<p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>'
           '<p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
           '<p:par><p:cTn id="5" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" '
           'nodeType="afterEffect"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
           '<p:cmd type="call" cmd="playFrom(0.0)"><p:cBhvr><p:cTn id="6" dur="1" fill="hold"/>'
           f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:cmd></p:childTnLst></p:cTn></p:par>'
           '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>'
           '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
           '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
           '</p:seq><p:video><p:cMediaNode vol="80000"><p:cTn id="7" fill="hold" display="0"><p:stCondLst>'
           f'<p:cond delay="indefinite"/></p:stCondLst></p:cTn><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
           '</p:cMediaNode></p:video></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>')
    sld = slide._element
    for old_t in sld.findall(f"{{{ns}}}timing"):
        sld.remove(old_t)
    t = etree.fromstring(xml)
    ext = sld.find(f"{{{ns}}}extLst")
    if ext is not None:
        ext.addprevious(t)
    else:
        sld.append(t)

def poster_frame() -> Path:
    """Still of the demo video at POSTER_AT, shown before playback starts."""
    import imageio_ffmpeg
    ASSETS.mkdir(exist_ok=True)
    out = ASSETS / "video_poster.png"
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-ss", str(POSTER_AT), "-i", str(VIDEO),
                    "-frames:v", "1", str(out)], check=True)
    return out


def s2_demo(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, W, H, NAVY)
    fh = 5.85
    fw = fh * 16 / 9
    fx, fy = (W - fw) / 2, 0.55
    if VIDEO.exists():
        movie = s.shapes.add_movie(str(VIDEO), Inches(fx), Inches(fy), Inches(fw), Inches(fh),
                                   poster_frame_image=str(poster_frame()), mime_type="video/mp4")
        autoplay(s, movie.shape_id)
    else:  # placeholder if the recording is missing
        rect(s, fx, fy, fw, fh, RGBColor(0x14, 0x2B, 0x4D), line=PALE_BLUE)
        picture(s, ASSETS / "app_product.png", fx + 0.15, fy + 0.15, fw - 0.3, fh - 0.3)
        print(f"warning: {VIDEO.relative_to(ROOT)} missing, the video slide has a placeholder")
    footer(s, n, dark=True)
    return s


def s5_circuit(prs, n):
    """The QAE circuit we ran (out/stage_qae_circuit.png from scripts/qae_circuit_figure.py) + why quantum.
    Simulator numbers: CLAIMS.md (qae-sim 0.125 % ± 0.011 pp vs Monte Carlo ± 0.027 pp at 16,000 oracle queries)."""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    title(s, n, "Our circuit: quantum amplitude estimation")
    picture(s, OUT / "stage_qae_circuit.png", MX, 1.35, W - 2 * MX, 3.6)
    text(s, MX, 5.15, W - 2 * MX, 1.4,
         [[("Qubits = wet spring + rivers. Gates = our flood model.", {})],
          [("Why quantum?  ", {"bold": True, "color": RED}), ("2× accuracy: sampling needs 4× the runs, QAE 2×.", {})]],
         size=BODY, color=NAVY, space_after=8)
    return s


def s6_honest(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    title(s, n, "Classical still wins today")
    picture(s, OUT / "stage_scaling.png", MX, 1.55, 8.2, 4.9)  # scripts/pitch_charts.py
    x, w = 9.25, 3.5
    rect(s, x - 0.3, 1.9, 0.1, 2.4, RED)
    text(s, x, 1.9, w, 2.4, "Rare 1-in-50 floods drown in noise.", size=36, bold=True, color=NAVY,
         anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, x, 4.7, w, 1.2, "Prices are computed classically.", size=BODY, color=GREY)
    return s


def s7_business(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    title(s, n, "Who pays")
    # money flows FROM the insurer: licence to Tulva (left), premium to the reinsurer (right)
    bw, bh, y = 3.0, 1.3, 1.65
    xs = [MX, (W - bw) / 2, W - MX - bw]
    for x, lab, fill, col in [(xs[0], "Tulva", BLUE, WHITE), (xs[1], "Insurer", NAVY, WHITE),
                              (xs[2], "Reinsurer", LIGHT, NAVY)]:
        rect(s, x, y, bw, bh, fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.12)
        text(s, x, y, bw, bh, lab, size=36, bold=True, color=col, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    for x0, x1, shape, lab in [(xs[0] + bw, xs[1], MSO_SHAPE.LEFT_ARROW, "licence"),
                               (xs[1] + bw, xs[2], MSO_SHAPE.RIGHT_ARROW, "premium")]:
        rect(s, x0 + 0.15, y + bh / 2 - 0.05, x1 - x0 - 0.3, 0.5, BLUE, shape=shape)
        text(s, x0 - 0.2, y + bh / 2 - 0.62, x1 - x0 + 0.4, 0.5, lab, size=24, bold=True, color=BLUE,
             align=PP_ALIGN.CENTER)
    text(s, xs[0], y + bh + 0.15, 5.0, 0.5, "€25k pilot, then €75k / yr", size=BODY, bold=True, color=NAVY)
    text(s, MX, 3.75, W - 2 * MX, 1.1, "Year 3: €0.2–0.45M / yr", size=64, bold=True, color=NAVY)
    text(s, MX, 4.85, W - 2 * MX, 0.5, "3–6 Finnish insurers, then the Nordics", size=BODY, color=GREY)
    rect(s, MX, 5.55, W - 2 * MX, 1.35, NAVY, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.1)  # two lines at 32 pt
    text(s, MX + 0.4, 5.55, W - 2 * MX - 0.6, 1.35,
         [[("Ask:  ", {"color": PALE_BLUE}), ("8 weeks of one insurer's claims data, to test on real losses.", {})]],
         size=32, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    return s


def s8_close(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, W, H, NAVY)
    title(s, n, "Built during this hackathon", dark=True)
    x, y = MX, 1.55
    for c in ["SYKE data pipeline", "Joint flood model", "Index pricing", "Live app", "Runs on 4 quantum chips"]:
        w = 0.5 + text_width(c, 24)
        if x + w > W - MX:
            x, y = MX, y + 0.8
        rect(s, x, y, w, 0.65, RGBColor(0x1A, 0x36, 0x5F), line=PALE_BLUE, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
             radius=0.5)
        text(s, x, y, w, 0.65, c, size=24, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        x += w + 0.2
    text(s, MX, 3.45, W - 2 * MX, 1.0,
         [[("Next March, the snow will warn us ", {}), ("again.", {"color": PALE_BLUE})]],
         size=44, bold=True, color=WHITE)
    text(s, MX, 4.4, W - 2 * MX, 0.6, "This time, it will have a price.", size=32, color=PALE_BLUE)
    text(s, MX, 5.85, 11, 0.9,
         [[("Toivo Kallio", {"bold": True}), ("  ·  ", {"color": PALE_BLUE}), ("Vaishnav Rane", {"bold": True})],
          [("Team 21 STUHI  ·  Quantum x Finance 2026", {"color": PALE_BLUE, "size": 18})]],
         size=24, color=WHITE, space_after=4)
    return s


# --------------------------------------------------------------------------- backup slides (Q&A only)
def bullets(slide, x, y, w, h, items, size=16):
    text(slide, x, y, w, h, [[("▪  ", {"color": BLUE, "bold": True}), (t, {})] if isinstance(t, str) else t
                             for t in items], size=size, color=NAVY, space_after=9, spacing=1.05)


def backup_header(slide, n, t):
    text(slide, MX, 0.36, 9, 0.3, "BACKUP · Q&A ONLY", size=16, color=BLUE, bold=True)
    text(slide, MX, 0.72, W - 2 * MX, 0.7, t, size=30, bold=True)
    footer(slide, n)


def s10_backup_product(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    backup_header(s, n, "Product and pricing in detail")
    text(s, MX, 1.5, 9, 0.3, "EXPECTED LOSS, % OF THE LIMIT PER YEAR (YEAR-BOOTSTRAP 90 % INTERVALS)", size=14,
         bold=True, color=BLUE)
    picture(s, OUT / "pitch_cost.png", MX, 1.85, W - 2 * MX, 2.0)  # scripts/pitch_charts.py
    bullets(s, MX, 4.05, W - 2 * MX, 3.0, [
        "Index: pays the full limit if ≥2 of 5 northern rivers pass their 1-in-50 level (a staged payout is only a "
        "variant). Priced in autumn; in March the insurer can buy top-up cover and staff claims in the regions at risk.",
        "Tulva 1.96 % (1.6–2.2 %) vs 1.11 % for the standard assumption (a model with one 0.27 correlation) = 1.77× (≈1.8×). 0.27 = mean of the "
        "2027 Finnish 19-zone flood matrix, Del. Reg. (EU) 2026/269. ≈5× only vs independence (0.38 %).",
        "Snowy (top-15 %) March vs autumn (normal): 6.4 % (3.6–9.1 %) vs 1.96 % = 3.3× (90 %: 2.1–4.4×).",
        "Market price = expected loss × 2.5–3.5: 4.9–6.9 % rate on line ≈ €49–69k a year per €1M of cover.",
        "Slide 1: 'flooded' = flow over each gauge's 1-in-10 level; North's 1 March snow in its top 15 % (in-sample). "
        "Slide 2: 10 of 65 springs (15.4 %, 90 %: 9–24 %) had ≥4 of 14 areas over 1-in-10; chance on the same "
        "gauge-years 3.9 % (3.9×), 4.4 % if all gauges reported (3.5×). SYKE 1961–2025 (+ SMHI Torne).",
    ], size=15)
    return s


def s11_backup_business(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    backup_header(s, n, "Basis risk and business in detail")
    bullets(s, MX, 1.6, W - 2 * MX, 5.4, [
        [("Basis risk (1-in-10 back-test).  ", {"bold": True}),
         ("Paid in loss springs 1966, 2005, 2018; missed Ostrobothnia 2012–13 and 2024 and Lapland 2020; since 2005 "
          "also paid in 3 North springs with no recorded loss (2015, 2023, 2024). At the 1-in-50 product level: paid "
          "1966 and 2005 only.", {})],
        [("Why now.  ", {"bold": True}),
         ("From 2027 the Solvency II standard formula fixes flood correlations that ignore the snow (19-zone matrix "
          "inside Finland, mean ≈ 0.27; 0 % to SE/NO/DK; Del. Reg. (EU) 2026/269). Insurers with an approved internal "
          "model, like If, can use a snow-aware joint-flood number.", {})],
        [("Money flows.  ", {"bold": True}),
         ("Insurer → reinsurer: premium ≈ €0.5–0.7M a year per €10M North layer (model × 2.5–3.5 market multiple). "
          "Insurer → Tulva: licence, €25k pilot, then ~€75k a year (assumption). The reinsurer pays Tulva nothing.",
          {})],
        [("Year 3.  ", {"bold": True}),
         ("3–6 insurers × €75k ≈ €0.2–0.45M a year (assumption); Nordic snowmelt upside unsized (assumption). "
          "Buyers: Finnish home insurers (OP, If, LähiTapiola, …); no pilot agreement yet.", {})],
        [("Market size.  ", {"bold": True}),
         ("Losses per event ≈ €5–20M; parametric insurance market $3.5bn to $18–21bn, 12–14 %/yr growth "
          "(business case, outside sources, quoted as a range).", {})],
        [("Ask.  ", {"bold": True}),
         ("One insurer's flood claims for 8 weeks → basis-risk map + firm quote for 1 Jan 2028.", {})],
    ], size=17)
    return s


def s12_backup_hardware(prs, n):
    """Hardware details (intervals, raw readings, job IDs, amplification, resources)."""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    backup_header(s, n, "Hardware runs in detail")
    hdr = ["Chip", "Circuit", "Exact", "Raw", "Calibrated (90 % CI)", "Job"]
    rows = [
        ["IBM Marrakesh", "North-cluster pair, 3 qubits, k = 0–2", "0.125 %", "0.262 %", "0.149 % (0.140–0.157)",
         "db3tddsvf2bc73ctoprg"],
        ["IQM Garnet", "North-cluster pair, 3 qubits, k = 0–2", "0.125 %", "0.368 %", "0.164 % (0.147–0.180)",
         "01a11cc3-7f6c…"],
        ["IQM Emerald", "Snowy / low-snow ratio, same pair, k = 0–2", "2.75×", "1.3×", "3.05× (2.6–3.6)",
         "01a11fa8-65a9…"],
        ["IQM Emerald", "14 rivers ≥4 over 1-in-10, 18 q / 44 CZ", "10.9 %", "–", "13.8 % (readout-corr.)",
         "01a11cd4-da38…"],
        ["IQM Emerald", "14 rivers ≥2 over 1-in-50, same circuit", "4.8 %", "–", "16.0 % (fails)",
         "01a11f9b-c62a…"],
        ["IQM Emerald", "Control: independent circuit, ≥4 over 1-in-10", "4.4 %", "–", "9.7 % (noise fattens tails)",
         "01a120f5-ece7…"],
        ["VTT Q50", "Same pair, 3 repeats: not stable", "0.125 %", "1.48–1.58 %",
         "0.47 / 0.53 / 0.11 %", "7d20d8ac / a6fb9d52 / 381179fb"],
        ["VTT Q50", "14 rivers ≥4 over 1-in-10, 18 q / 49 CZ", "10.9 %", "34.2 %", "31.2 % (readout-corr.)",
         "9cdb0158-7574…"],
    ]
    cols = [1.65, 4.05, 0.9, 1.3, 2.55, 1.8]
    widths = [c * (W - 2 * MX) / sum(cols) for c in cols]
    y = 1.4
    for r_i, row in enumerate([hdr] + rows):
        x = MX
        if r_i:
            rect(s, MX, y + 0.41, W - 2 * MX, 0.012, LINE)
        for c_i, (cell, cw) in enumerate(zip(row, widths)):
            text(s, x, y, cw - 0.1, 0.42, cell, size=(12 if c_i == 5 else 14) if r_i else 13,
                 bold=(r_i == 0 or c_i == 4), color=BLUE if r_i == 0 else (GREY if c_i == 5 else NAVY),
                 anchor=MSO_ANCHOR.MIDDLE)
            x += cw
        y += 0.42
    text(s, MX, y + 0.05, W - 2 * MX, 1.9,
         ["Method: calibrated sampling + shallow amplitude estimation (noise-aware MLAE, Grover steps k = 0–2, two "
          "known-answer calibration circuits in the same job; bootstrap 90 % intervals). Pair = two rivers with "
          "identical North-cluster loadings and 1-in-50 trigger. Snowy vs normal on the same pair: 1.51× chip, 1.55× "
          "exact. Simplified 14-river model = two-level version, 18 qubits, sampling only. IBM / Garnet intervals "
          "exclude exact (+19 % / +31 % bias). Classical Monte Carlo at the same budget is more precise (±0.004 pp).",
          "Signal kept at k = 1 in the runs shown: Emerald 0.56–0.59, IBM / Garnet 0.77–0.78, VTT Q50 0.12–0.19 "
          "(earlier runs 0.65–0.88): the estimate is mostly the calibrated k = 0 circuit. Q50's zero-calibration offset "
          "moved 0.002 → 0.006 between repeats (the 5× spread). Not shown: first runs IBM 0.146 % (k = 0–3), "
          "Garnet 0.073 % (1 copy).",
          "Resources: SYKE open data · IBM Marrakesh · IQM Garnet & Emerald (Resonance) · VTT Q50 (LUMI) · Qrisp · "
          "Qiskit · AI coding agents."],
         size=12, color=GREY, space_after=4)
    return s


# Stage deck only. The backup slides (s10-s12) are kept as functions but not built: their details are in QA.md.
SLIDES = [s1_hook, s2_demo, s3_gap, s4_product, s5_circuit, s6_honest, s7_business, s8_close]


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
    for f in prev.glob("slide-*.png"):  # pdftoppm zero-pads past 9 pages; keep slide-N.png names
        f.rename(prev / f"slide-{int(f.stem.split('-')[1])}.png")
    print(f"wrote {pdf.relative_to(ROOT)} and {len(list(prev.glob('*.png')))} previews in deck/preview/")


if __name__ == "__main__":
    build()
    if "--pdf" in sys.argv:
        export()
