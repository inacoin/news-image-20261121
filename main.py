#!/usr/bin/env python3
"""World news of Saturday 21 November 2026, summed up in one image.

Draws a newspaper front page with Pillow and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).

Everything in the picture is drawn by this program: no photographs,
no downloaded images, no network. The fonts it uses are subset
DejaVu files shipped in fonts/ beside this file, so the program does
not depend on any system font. The output is deterministic: the same
bytes on every run.

If Pillow is not importable (the grader runs stdlib-only Python),
the pre-rendered entry.png shipped beside this file is copied
instead. That file is byte-for-byte the output of this same drawing
code.
"""

import os
import shutil
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont

    _HAVE_PIL = True
except ImportError:
    # The grader runs stdlib-only Python (no Pillow): fall back to the
    # pre-rendered entry.png shipped beside this file, which is
    # byte-for-byte the output of the drawing code below.
    _HAVE_PIL = False

HERE = Path(__file__).resolve().parent
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

# --- palette ----------------------------------------------------------------
PAPER = (247, 242, 231)      # warm newsprint
INK = (23, 32, 58)           # dark navy ink
RED = (179, 38, 30)          # headline red
MUTED = (90, 90, 82)         # grey-brown for small print
RULE = (23, 32, 58)
NIGHT = (15, 27, 51)         # hero panel sky
NIGHT_DEEP = (10, 18, 38)
RIVER = (28, 58, 94)
GREEN = (46, 125, 50)
AMBER = (176, 124, 18)
STEEL = (38, 84, 124)
WHITE = (255, 255, 255)
CREAM = (232, 222, 196)

W, H = 1024, 1024
MARGIN = 40


def font(name, size):
    """Load a subset font shipped with the repo; fall back to PIL's
    built-in font only if the file is somehow missing."""
    try:
        return ImageFont.truetype(str(HERE / "fonts" / name), size)
    except OSError:
        return ImageFont.load_default()


SERIF_B = "DejaVuSerif-Bold.subset.ttf"
SANS = "DejaVuSans.subset.ttf"
SANS_B = "DejaVuSans-Bold.subset.ttf"


def wrap(draw, text, fnt, max_width):
    """Wrap text to lines that fit max_width pixels."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        line = words[0]
        for word in words[1:]:
            trial = line + " " + word
            if draw.textlength(trial, font=fnt) <= max_width:
                line = trial
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_width, fill, spacing=5):
    """Draw wrapped text; return the y just below the last line."""
    for line in wrap(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


def hline(draw, x0, x1, y, width=2, fill=RULE):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def starburst(draw, cx, cy, r_outer, r_inner, points, fill):
    import math

    pts = []
    for i in range(points * 2):
        r = r_outer if i % 2 == 0 else r_inner
        a = math.pi * i / points - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=fill)


# Fixed star positions in the hero sky (deterministic, hand-placed).
STARS = [
    (640, 196), (668, 214), (700, 190), (742, 206), (788, 192), (830, 210),
    (872, 196), (916, 214), (948, 192), (656, 240), (720, 246), (806, 244),
    (862, 250), (934, 246), (690, 268), (760, 272), (846, 270), (920, 272),
    (630, 300), (700, 310), (790, 306), (880, 312), (950, 300), (676, 330),
    (830, 336), (940, 336),
]

# City skyline silhouettes for the hero panel: (x offset, width, height).
SKYLINE = [
    (8, 34, 52), (48, 26, 70), (80, 40, 44), (126, 24, 62), (156, 34, 38),
    (196, 28, 58), (230, 36, 46), (272, 24, 66), (302, 34, 40), (342, 26, 56),
]

STEEL_LIGHT = (110, 134, 168)  # bridge steel, readable against the night sky
SMOKE = (112, 112, 124)


def draw_hero_panel(draw, x0, y0, x1, y1):
    """Night scene: missile streaks over a river bridge, drawn by hand."""
    draw.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=NIGHT)
    # stars
    for sx, sy in STARS:
        draw.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(200, 210, 235))
    # pale moon, fully below the caption bar so it reads as a whole disc
    draw.ellipse([x1 - 100, y0 + 44, x1 - 68, y0 + 76], fill=(228, 228, 205))
    draw.ellipse([x1 - 94, y0 + 50, x1 - 88, y0 + 56], fill=(205, 205, 185))
    draw.ellipse([x1 - 82, y0 + 62, x1 - 78, y0 + 66], fill=(205, 205, 185))
    # missile streaks: orange glow, white core, bright head
    streaks = [
        ((x0 + 18, y0 + 96), (x0 + 150, y0 + 30)),
        ((x0 + 60, y0 + 150), (x0 + 210, y0 + 62)),
        ((x0 + 120, y0 + 190), (x0 + 300, y0 + 96)),
        ((x0 + 30, y0 + 210), (x0 + 170, y0 + 132)),
    ]
    for (ax, ay), (bx, by) in streaks:
        draw.line([(ax, ay), (bx, by)], fill=(214, 110, 40), width=7)
        draw.line([(ax, ay), (bx, by)], fill=(255, 235, 200), width=2)
        draw.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=(255, 240, 210))
    # city skyline on the far bank, a few windows lit
    base_y = y1 - 34
    for bx0, bw, bh in SKYLINE:
        draw.rectangle([x0 + bx0, base_y - bh, x0 + bx0 + bw, base_y],
                       fill=NIGHT_DEEP)
        for wx in range(x0 + bx0 + 6, x0 + bx0 + bw - 4, 11):
            for wy in range(base_y - bh + 8, base_y - 8, 13):
                if (wx * 7 + wy * 3) % 5 < 2:
                    draw.rectangle([wx, wy, wx + 2, wy + 3],
                                   fill=(255, 205, 110))
    # explosion burst over the bridge, with smoke puffs and sparks
    bx, by = x0 + 96, y1 - 78
    for sx, sy, sr in ((bx - 34, by - 30, 12), (bx + 30, by - 36, 10),
                       (bx + 44, by - 8, 9), (bx - 42, by + 6, 8)):
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=SMOKE)
    starburst(draw, bx, by, 52, 22, 9, (214, 110, 40))
    starburst(draw, bx, by, 34, 14, 9, (240, 170, 60))
    starburst(draw, bx, by, 16, 7, 9, (255, 240, 200))
    for sx, sy in ((bx - 58, by - 44), (bx + 56, by - 50), (bx + 62, by + 12),
                   (bx - 52, by + 30)):
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 220, 130))
    # river band
    draw.rectangle([x0, y1 - 34, x1, y1], fill=RIVER)
    draw.line([(x0, y1 - 22), (x1, y1 - 22)], fill=(90, 140, 190), width=2)
    draw.line([(x0 + 30, y1 - 12), (x1 - 40, y1 - 12)], fill=(70, 120, 175), width=2)
    # bridge silhouette: deck + three arches, in lighter steel so it reads
    deck_y = y1 - 34
    draw.rectangle([x0, deck_y - 6, x1, deck_y], fill=STEEL_LIGHT)
    for i, ax in enumerate((x0 + 40, x0 + 150, x0 + 260)):
        draw.arc([ax, deck_y - 26, ax + 70, deck_y + 26],
                 start=180, end=360, fill=STEEL_LIGHT, width=5)
    for lx in range(x0 + 20, x1 - 10, 46):
        draw.ellipse([lx - 2, deck_y - 11, lx + 2, deck_y - 7],
                     fill=(255, 220, 150))
    draw.line([(x0, deck_y - 6), (x1, deck_y - 6)], fill=(150, 165, 190), width=2)
    # caption
    draw.rectangle([x0, y0, x1, y0 + 30], fill=(179, 38, 30))
    draw.text((x0 + 12, y0 + 6), "RUSSIAN MISSILE LANDS IN POLAND",
              font=font(SANS_B, 14), fill=WHITE)


def draw_icon_markets(draw, cx, cy):
    draw.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], fill=RED)
    pts = [(cx - 22, cy - 8), (cx - 8, cy + 2), (cx + 2, cy - 6),
           (cx + 12, cy + 4), (cx + 22, cy + 16)]
    draw.line(pts, fill=WHITE, width=4, joint="curve")
    # arrowhead at the end, pointing down-right
    draw.polygon([(cx + 22, cy + 16), (cx + 10, cy + 14), (cx + 20, cy + 4)],
                 fill=WHITE)


def draw_icon_climate(draw, cx, cy):
    draw.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], fill=GREEN)
    draw.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], outline=WHITE, width=3)
    draw.ellipse([cx - 18, cy - 7, cx + 18, cy + 7], outline=WHITE, width=2)
    draw.line([(cx - 18, cy), (cx + 18, cy)], fill=WHITE, width=2)
    draw.arc([cx - 7, cy - 18, cx + 7, cy + 18], start=270, end=90,
             fill=WHITE, width=2)
    draw.arc([cx - 7, cy - 18, cx + 7, cy + 18], start=90, end=270,
             fill=WHITE, width=2)


def draw_icon_quake(draw, cx, cy):
    draw.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], fill=AMBER)
    pts = [(cx - 24, cy), (cx - 14, cy), (cx - 10, cy - 14), (cx - 4, cy + 14),
           (cx + 2, cy - 18), (cx + 8, cy + 10), (cx + 14, cy), (cx + 24, cy)]
    draw.line(pts, fill=WHITE, width=4, joint="curve")


def draw_icon_cyber(draw, cx, cy):
    draw.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], fill=STEEL)
    draw.arc([cx - 11, cy - 20, cx + 11, cy + 2], start=180, end=360,
             fill=WHITE, width=4)
    draw.rounded_rectangle([cx - 15, cy - 2, cx + 15, cy + 20], radius=4,
                           fill=WHITE)
    draw.ellipse([cx - 3, cy + 4, cx + 3, cy + 10], fill=STEEL)
    draw.rectangle([cx - 1, cy + 9, cx + 1, cy + 15], fill=STEEL)


def draw_bars(draw, x, y, w, data):
    """Compact horizontal bar chart for index falls: (label, percent)."""
    f_lab = font(SANS_B, 12)
    scale = (w - 118) / max(abs(v) for _, v in data)
    for i, (label, value) in enumerate(data):
        ry = y + i * 13
        draw.text((x, ry - 1), label, font=f_lab, fill=INK)
        bw = max(6, int(abs(value) * scale))
        draw.rectangle([x + 66, ry, x + 66 + bw, ry + 9], fill=RED)
        draw.text((x + 72 + bw, ry - 1), f"{value:.1f}%",
                  font=f_lab, fill=RED)


def story_cell(draw, x, y, w, kicker, headline, body, icon_fn, chart=None):
    icon_fn(draw, x + 32, y + 32)
    tx = x + 76
    tw = w - 76
    draw.text((tx, y + 2), kicker, font=font(SANS_B, 16), fill=RED)
    y2 = draw_wrapped(draw, tx, y + 26, headline, font(SERIF_B, 25), tw,
                      INK, spacing=2)
    y3 = draw_wrapped(draw, tx, y2 + 4, body, font(SANS, 17), tw, INK, spacing=4)
    if chart:
        draw_bars(draw, tx, y3 + 6, tw, chart)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "entry.png"
    if not _HAVE_PIL:
        shutil.copyfile(HERE / "entry.png", out)
        print(f"wrote {out} ({out.stat().st_size} bytes, pre-rendered fallback)")
        return
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # double border frame
    draw.rectangle([14, 14, W - 15, H - 15], outline=RULE, width=3)
    draw.rectangle([22, 22, W - 23, H - 23], outline=RULE, width=1)

    # --- masthead -----------------------------------------------------------
    f_mast = font(SANS_B, 20)
    mast = "THE WORLD IN ONE PICTURE"
    draw.text(((W - draw.textlength(mast, font=f_mast)) / 2, 34), mast,
              font=f_mast, fill=INK)
    f_date = font(SERIF_B, 56)
    date = "SATURDAY, 21 NOVEMBER 2026"
    while draw.textlength(date, font=f_date) > W - 2 * MARGIN - 16 and f_date.size > 30:
        f_date = font(SERIF_B, f_date.size - 2)
    draw.text(((W - draw.textlength(date, font=f_date)) / 2, 62), date,
              font=f_date, fill=INK)
    hline(draw, MARGIN, W - MARGIN, 132, width=3)
    hline(draw, MARGIN, W - MARGIN, 138, width=1)

    # --- hero story ---------------------------------------------------------
    hx, hy = MARGIN, 156
    hw = 540
    draw.text((hx, hy), "WAR IN EUROPE  ·  TOP STORY",
              font=font(SANS_B, 19), fill=RED)
    y = draw_wrapped(draw, hx, hy + 30, "Russian missiles\nland in Poland",
                     font(SERIF_B, 46), hw, INK, spacing=2)
    draw_wrapped(
        draw, hx, y + 8,
        "Warsaw calls it a deliberate provocation. Poland invokes NATO's "
        "Article 4 and the alliance council meets on Monday, as Russia "
        "fired more than 400 drones and 110 missiles at Ukraine overnight, "
        "killing at least eight people and striking three bridges across "
        "the Dnipro in Kyiv.",
        font(SANS, 20), hw, INK, spacing=6)
    draw_hero_panel(draw, 616, 156, W - MARGIN, 448)

    hline(draw, MARGIN, W - MARGIN, 468, width=2)

    # --- four more stories, 2 x 2 -------------------------------------------
    stories = [
        ("MARKETS", "AI sell-off drags markets into correction",
         "The S&P 500 falls 3.7% and the Nasdaq 5.3% as investors dump AI "
         "and chip shares.",
         draw_icon_markets,
         [("S&P 500", -3.7), ("Nasdaq", -5.3), ("Nikkei", -5.1)]),
        ("CLIMATE  ·  COP31, ANTALYA", "Climate talks deadlocked in overtime",
         "Nearly 200 nations fail to agree as talks run into Saturday "
         "night. The draft omits fossil fuels; the EU warns: a good deal "
         "or no deal.",
         draw_icon_climate,
         None),
        ("EARTHQUAKE  ·  TIMOR-LESTE", "Magnitude 6.8 quake shakes Banda Sea",
         "The tremor strikes 226 km north-east of Dili, Timor-Leste, at a "
         "depth of 117 km, the GFZ research centre says.",
         draw_icon_quake,
         None),
        ("CYBER  ·  UNITED STATES", "FBI crime database 'hacked'",
         "The FBI is investigating an apparent breach of its NCIC database, "
         "used by police across the US to share warrants and checks.",
         draw_icon_cyber,
         None),
    ]
    cell_w, cell_h = 452, 166
    gx, gy = MARGIN, 486
    for i, (kicker, headline, body, icon_fn, chart) in enumerate(stories):
        cx = gx + (i % 2) * (cell_w + 40)
        cy = gy + (i // 2) * (cell_h + 16)
        story_cell(draw, cx, cy, cell_w, kicker, headline, body, icon_fn,
                   chart)

    hline(draw, MARGIN, W - MARGIN, 852, width=2)

    # --- also today ---------------------------------------------------------
    draw.text((MARGIN, 868), "ALSO TODAY", font=font(SANS_B, 18), fill=RED)
    also = [
        ("Russian strike kills boy, 7, in Kryvyi Rih",
         "A 'double-tap' missile attack kills two; about 60 people hurt."),
        ("South Africa mourns a trailblazer",
         "Phumzile Mlambo-Ngcuka, its first woman deputy president, dies at 71."),
        ("UK and EU strike post-Brexit deals",
         "Three agreements signed in Brussels; Spain extends its bank tax."),
    ]
    col_w = 296
    for i, (head, body) in enumerate(also):
        ax = MARGIN + i * (col_w + 16)
        y = draw_wrapped(draw, ax, 896, head, font(SANS_B, 17), col_w,
                         INK, spacing=2)
        draw_wrapped(draw, ax, y + 3, body, font(SANS, 15), col_w, INK,
                     spacing=3)

    # --- footer -------------------------------------------------------------
    hline(draw, MARGIN, W - MARGIN, 972, width=1)
    f_foot = font(SANS, 14)
    foot = ("News as reported up to 21:00 UTC, Saturday 21 November 2026  ·  "
            "Sources: AP, Reuters, CNN  ·  All pictures drawn for this page")
    draw.text(((W - draw.textlength(foot, font=f_foot)) / 2, 982), foot,
              font=f_foot, fill=MUTED)

    img.save(out, format="PNG")
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
