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
    text(slide, MX, 0.42, 9, 0.3, kicker.upper(), size=12, color=BLUE, bold=True)
    text(slide, MX, 0.72, W - 2 * MX, 0.75, title, size=title_size, bold=True)
    footer(slide, n)


def footer(slide, n, dark=False):
    c = PALE_BLUE if dark else GREY
    text(slide, W - MX - 2.0, H - 0.42, 2.0, 0.25,
         [[("Tulva", {"bold": True, "color": WHITE if dark else NAVY}), (f"   {n}", {})]],
         size=11, color=c, align=PP_ALIGN.RIGHT)


def source(slide, s, dark=False):
    text(slide, MX, H - 0.42, W - 2 * MX - 2.2, 0.3, s, size=10, color=PALE_BLUE if dark else GREY)


def stat(slide, x, y, w, big, label, color=NAVY, big_size=40, label_size=13, label_h=0.6):
    text(slide, x, y, w, 0.75, big, size=big_size, bold=True, color=color)
    text(slide, x, y + big_size / 72 * 1.18, w, label_h, label, size=label_size, color=GREY)


def crops():
    """Crops of the web-app screenshot used on slides 1 and 5."""
    ASSETS.mkdir(exist_ok=True)
    shot = Image.open(OUT / "web_shot.png")
    # Year-replay map, 2005 selected (Lapland: Ivalo, Kittilä, Rovaniemi, Tornio lit).
    shot.crop((690, 4160, 1226, 4600)).save(ASSETS / "map_2005.png")
    # Product card (Tulva Index, North cluster).
    shot.crop((60, 112 + 1760, 1220, 640 + 1760)).save(ASSETS / "app_product.png")


# --------------------------------------------------------------------------- slides
def s1_hook(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    text(s, MX, 0.5, 4, 0.5, [[("Tulva", {"bold": True, "color": NAVY}),
                                ("   spring-flood risk, priced jointly", {"color": GREY, "size": 14})]],
         size=22)
    text(s, MX, 1.85, 6.8, 3.2,
         [[("In May 2005, Kittilä and Ivalo flooded ", {}), ("together.", {"color": BLUE})],
          [("The snow had warned us two months earlier.", {"size": 24, "bold": False, "color": GREY})]],
         size=42, bold=True, spacing=1.05, space_after=18)
    text(s, MX, 4.6, 6.4, 0.9,
         "1 March snow flagged 2005 in advance. Kittilä and Ivalo then passed their flood levels in the same spring.",
         size=15, color=NAVY)
    pic = picture(s, ASSETS / "map_2005.png", 7.6, 0.95, w=5.1)
    pic.line.color.rgb = LINE
    text(s, 7.6, 0.95 + pic.height / 914400 + 0.1, 5.1, 0.3, "Tulva app, year replay: spring 2005",
         size=10, color=GREY, align=PP_ALIGN.RIGHT)
    source(s, "Source: SYKE discharge 1961–2025 and 1 March snow (SWE); Tulva back-test (out/backtest.json)")
    footer(s, n)
    return s


def s2_gap(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, n, "The gap", "Finland's rivers flood together, not one at a time")
    picture(s, OUT / "joint_floods.png", MX, 1.6, 7.9, 5.25)
    x = 8.95
    text(s, x, 1.65, 3.8, 0.6, "Springs when ≥4 of the 14 river areas flooded (own 1-in-10 level)",
         size=13, color=GREY)
    stat(s, x, 2.25, 3.8, "15.4 %", "observed, 1961–2025 (10 of 65 years)", NAVY, 38)
    stat(s, x, 3.3, 3.8, "12.2 %", "Tulva joint model", BLUE, 38)
    stat(s, x, 4.35, 3.8, "3.9 %", "if areas were independent", RED, 38)
    rect(s, x, 5.45, 3.8, 0.02, LINE)
    text(s, x, 5.6, 3.8, 1.0,
         ["Home insurance pays only for floods rarer than 1-in-50.",
          "Reinsurance renews 1 January, before the snow signal."],
         size=12.5, color=NAVY, space_after=6)
    source(s, "Source: SYKE 1961–2025 (+ SMHI Torne), Tulva model (exact); vesi.fi / OP (1-in-50 rule)")
    return s


def s3_cost(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, n, "What it costs", "Priced as independent, a joint flood cover is ~5× too cheap")
    text(s, MX, 1.55, 12, 0.4,
         "North cluster: pays €10M if ≥2 of 5 gauges pass their 1-in-50 level. Market price per year:",
         size=15, color=GREY)
    stat(s, MX, 2.0, 3.6, "€96k–134k", "if areas were independent", RED, 34, 13)
    text(s, 4.25, 2.05, 0.8, 0.6, "→", size=34, color=GREY)
    stat(s, 5.0, 2.0, 3.9, "€491k–687k", "Tulva joint risk  (technical €265k)", BLUE, 34, 13)
    stat(s, 9.4, 2.0, 3.4, "5.1×", "Tulva vs independence", NAVY, 34, 13)
    picture(s, OUT / "index_price.png", MX, 3.2, W - 2 * MX, 3.75)
    source(s, "Source: SYKE 1961–2025, Tulva model (exact; MC 1M agrees). Market = 2.5–3.5× expected payout "
              "(AM Best cat bonds, flood ILS)")
    return s


def s4_product(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, n, "The product", "Tulva Index: bought in winter, pays in spring")
    card = rect(s, MX, 1.6, W - 2 * MX, 1.3, NAVY, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08)
    text(s, MX + 0.4, 1.72, 11.5, 0.3, "TULVA INDEX · NORTH CLUSTER", size=11, color=PALE_BLUE, bold=True)
    text(s, MX + 0.4, 2.02, 11.6, 0.7,
         [[("Pays €10M", {"color": WHITE}),
           (" if ≥2 of 5 northern gauges pass their 1-in-50 level this spring", {"color": WHITE, "bold": False})]],
         size=26, bold=True)
    tiles = [("Independence", "€96k–134k", RED), ("Tulva", "€491k–687k", BLUE),
             ("After a snowy March", "€1.61M–2.26M", NAVY)]
    tw, gap = 3.85, 0.225
    for i, (lab, val, c) in enumerate(tiles):
        x = MX + i * (tw + gap)
        rect(s, x, 3.15, tw, 1.45, LIGHT)
        rect(s, x, 3.15, 0.07, 1.45, c)
        text(s, x + 0.3, 3.28, tw - 0.4, 0.3, lab, size=13, color=GREY)
        text(s, x + 0.3, 3.6, tw - 0.4, 0.6, val, size=32, bold=True, color=c)
        text(s, x + 0.3, 4.2, tw - 0.4, 0.3, "market price per year", size=11, color=GREY)
    feats = [("Bought in winter", "before the snow signal exists"),
             ("Staged option", "50 % paid at 2 gauges, 100 % at 3"),
             ("Explainable trigger", "public SYKE gauges anyone can check")]
    for i, (a, b) in enumerate(feats):
        x = MX + i * (tw + gap)
        text(s, x, 4.85, tw, 0.75, [[(a, {"bold": True})], [(b, {"color": GREY, "size": 13})]], size=16)
    rect(s, MX, 5.75, W - 2 * MX, 0.02, LINE)
    text(s, MX, 5.92, W - 2 * MX, 0.6,
         [[("11 of 19", {"bold": True, "color": BLUE, "size": 26}),
           ("   payout years flagged in advance by the 1 March snow, 2005 included", {"size": 16})]],
         size=16, anchor=MSO_ANCHOR.MIDDLE)
    source(s, "Source: Tulva model, exact; market 2.5–3.5× expected payout. Back-test 1961–2025, all clusters, "
              "≥2 gauges over 1-in-10, in-sample")
    return s


def s5_demo(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, W, H, NAVY)
    # Frame where the video goes; the still is a placeholder underneath it.
    fx, fy, fw, fh = 1.0, 0.55, W - 2.0, 5.85
    rect(s, fx, fy, fw, fh, RGBColor(0x14, 0x2B, 0x4D), line=PALE_BLUE)
    picture(s, ASSETS / "app_product.png", fx + 0.15, fy + 0.15, fw - 0.3, fh - 0.3)
    lab = rect(s, fx + fw / 2 - 3.6, fy + fh / 2 - 0.45, 7.2, 0.9, BLUE,
               shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.2)
    text(s, fx + fw / 2 - 3.6, fy + fh / 2 - 0.45, 7.2, 0.9,
         "DEMO VIDEO (≈60 s) — insert recording here", size=22, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, fx, 6.55, fw, 0.4,
         "Live app: the joint-flood map → March snow outlook → index price → real quantum runs → 2005 replay",
         size=14, color=WHITE, align=PP_ALIGN.CENTER)
    footer(s, n, dark=True)
    return s


def s6_quantum(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, n, "Quantum, in practice",
           "Pricing = a joint-flood probability → quantum amplitude estimation", title_size=27)
    picture(s, OUT / "loader_emerald.png", MX, 1.65, w=7.6)
    text(s, MX, 6.05, 7.6, 0.4, "The chip reproduces the joint tail that independence misses.",
         size=14, color=NAVY)
    x, w = 8.6, 4.15
    text(s, x, 1.65, w, 0.3, "ALL 14 AREAS ON IQM EMERALD", size=11, color=BLUE, bold=True)
    stat(s, x, 1.95, 2.0, "18", "qubits", NAVY, 40, 13, 0.3)
    stat(s, x + 2.1, 1.95, 2.0, "44", "two-qubit gates", NAVY, 40, 13, 0.3)
    rect(s, x, 3.2, w, 0.015, LINE)
    text(s, x, 3.4, w, 0.3, "AMPLITUDE ESTIMATION, IBM & IQM", size=11, color=BLUE, bold=True)
    text(s, x, 3.68, w, 0.3, "P(Kittilä and Ivalo both pass 1-in-50)", size=13, color=GREY)
    rows = [("Exact", "", "0.125 %", NAVY), ("IBM Marrakesh", "0.262 →", "0.148 %", BLUE),
            ("IQM Garnet", "0.368 →", "0.163 %", BLUE)]
    y = 3.98
    for lab, raw, cal, c in rows:
        text(s, x, y + 0.08, 1.9, 0.4, lab, size=15, bold=True)
        text(s, x + 1.85, y + 0.1, 1.05, 0.4, raw, size=13, color=GREY, align=PP_ALIGN.RIGHT)
        text(s, x + 2.9, y, 1.25, 0.5, cal, size=22, bold=True, color=c, align=PP_ALIGN.RIGHT)
        rect(s, x, y + 0.53, w, 0.012, LINE)
        y += 0.56
    text(s, x, y + 0.05, w, 0.3, "raw → calibrated", size=11, color=GREY, align=PP_ALIGN.RIGHT)
    text(s, x, 6.0, w, 0.6, [[("Snow signal on the chip: ", {"bold": True}),
                              ("snowy vs low March 3.1× (exact 2.7×)", {"color": BLUE, "bold": True})]],
         size=13, color=NAVY)
    source(s, "IQM Emerald job 01a11cd4…, 8,000 shots; snow runs: Emerald, 10 copies, 240k shots each; IBM "
              "ibm_marrakesh (20 copies); IQM Garnet (4 copies); also native Qrisp on Garnet")
    return s

def s7_honest(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, n, "Quantum, honestly", "Classical Monte Carlo still wins today")
    picture(s, OUT / "qae_scaling.png", MX, 1.65, w=7.6)
    x, w = 8.75, 4.0
    text(s, x, 1.75, w, 0.4, "Quantum wins at scale, with:", size=16, bold=True, color=BLUE)
    items = [("Fault-tolerant hardware", "~8k logical qubits for comparable pricing (Chakrabarti et al. 2021)"),
             ("Expensive models", "full hydrological simulation per scenario"),
             ("More work per price", "multi-peril, daily repricing")]
    y = 2.35
    for a, b in items:
        rect(s, x, y + 0.08, 0.08, 0.75 if len(b) > 45 else 0.5, BLUE)
        text(s, x + 0.3, y, w - 0.3, 1.0, [[(a, {"bold": True})], [(b, {"color": GREY, "size": 13})]], size=16)
        y += 1.15
    rect(s, x, 5.85, w, 0.02, LINE)
    text(s, x, 5.95, w, 0.7, "Ideal QAE error falls like 1/N, Monte Carlo like 1/√N.", size=13, color=NAVY)
    source(s, "Source: Tulva simulations (qae-sim) + IBM Marrakesh / IQM Garnet runs; Chakrabarti et al., "
              "Quantum 5, 463 (2021)")
    return s


def s8_business(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, n, "Business", "Who buys, why, and why now")
    cols = [
        ("Who buys", "Finnish non-life insurers", "For the flood they keep under reinsurance. "
         "Four groups write 91 % of the market. Then reinsurers and ILS investors."),
        ("How we earn", "Engine licence", "Pricing and trigger engine, licensed per insurer or reinsurer. "
         "Structuring fee on placed covers."),
        ("Why now", "30 Jan 2027", "Solvency II flood factor for Finland: 0 % correlation with SE/NO/DK "
         "(25 % for snowmelt rejected). ORSA needs climate scenarios."),
        ("Scale", "Finland → Nordics → Central Europe", "Same engine, any snowmelt or river region. "
         "Gävle 2021: SEK 1.9bn claims. Storm Boris 2024: €2.15bn insured."),
    ]
    cw, gap = 2.85, 0.193
    for i, (k, head, body) in enumerate(cols):
        x = MX + i * (cw + gap)
        c = RED if k == "Why now" else BLUE
        rect(s, x, 1.65, cw, 4.25, LIGHT)
        rect(s, x, 1.65, cw, 0.07, c)
        text(s, x + 0.25, 1.92, cw - 0.5, 0.3, k.upper(), size=11, bold=True, color=c)
        text(s, x + 0.25, 2.27, cw - 0.5, 1.1, head, size=22, bold=True, color=NAVY, spacing=0.95)
        text(s, x + 0.25, 3.5, cw - 0.5, 2.3, body, size=15, color=NAVY, spacing=1.1)
    rect(s, MX, 6.1, 0.08, 0.45, BLUE)
    text(s, MX + 0.25, 6.1, W - 2 * MX, 0.45,
         "First step: a paid pilot with one insurer in autumn, ahead of the 1 January renewals.",
         size=15, bold=True, color=NAVY, anchor=MSO_ANCHOR.MIDDLE)
    source(s, "Sources: Finance Finland 2024; Del. Reg. (EU) 2026/269; EIOPA-BoS-24/462 §4.70; "
              "Finansinspektionen 2023 (Gävle); PERILS 2025 (Boris)")
    return s

def s9_close(prs, n):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, W, H, NAVY)
    text(s, MX + 0.2, 0.7, 6, 0.6, "Tulva", size=28, bold=True, color=WHITE)
    text(s, MX + 0.2, 1.75, 11.5, 2.0,
         [[("Tulva prices Finland's spring floods as a ", {}), ("joint risk", {"color": PALE_BLUE}),
           (", and runs it on real quantum hardware.", {})]],
         size=38, bold=True, color=WHITE, spacing=1.05)
    text(s, MX + 0.2, 4.15, 11, 0.35, "BUILT THIS WEEKEND", size=12, bold=True, color=PALE_BLUE)
    chips = ["SYKE data pipeline", "Joint flood model", "Index pricing", "QAE on IBM & IQM"]
    x = MX + 0.2
    for c in chips:
        w = 0.32 + 0.118 * len(c)
        rect(s, x, 4.55, w, 0.55, RGBColor(0x1A, 0x36, 0x5F), shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.5)
        text(s, x, 4.55, w, 0.55, c, size=15, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        x += w + 0.2
    text(s, MX + 0.2, 5.75, 11, 0.8,
         [[("Toivo Kallio", {"bold": True}), ("  ·  ", {"color": PALE_BLUE}), ("Vaishnav Rane", {"bold": True})],
          [("Team 21 STUHI  ·  Quantum x Finance 2026, Hanken × Ultrahack", {"color": PALE_BLUE, "size": 14})]],
         size=20, color=WHITE, space_after=4)
    footer(s, n, dark=True)
    return s


SLIDES = [s1_hook, s2_gap, s3_cost, s4_product, s5_demo, s6_quantum, s7_honest, s8_business, s9_close]


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
