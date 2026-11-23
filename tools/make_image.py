#!/usr/bin/env python3
"""Draw the 23 November 2026 news-image front page (1024x1024 PNG).

Newspaper format per the news-image-newspaper template: masthead, lead
story, 6-number stat strip, pinned world map, 36 numbered stories in
7 region sections (each with a named source), 18 captioned picture
cards, DATE CHECK footer. Deterministic: fixed strings, fixed fonts,
no network, no timestamps, no randomness.

Run: python3 tools/make_image.py [output-path]
Default output: world-news-23-nov-2026.png next to this repo root.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stories import STORIES, STATS, CARDS, PINS, COLUMNS, EDITION_DATE  # noqa: E402

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

W, H = 1024, 1024
MARGIN = 14

PAPER = (247, 243, 232)
INK = (20, 20, 20)
GREY = (90, 88, 80)
AMBER = (180, 83, 9)
TEAL = (15, 59, 58)
NAVY = (20, 33, 61)
SEA = (214, 230, 236)
LAND = (232, 220, 192)
LAND_LINE = (120, 110, 80)
RED = (178, 34, 34)
CARD_BG = (255, 255, 255)
RULE = (180, 175, 160)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_SERIF = lambda s: font("DejaVuSerif-Bold.ttf", s)          # noqa: E731
F_BOLD = lambda s: font("DejaVuSans-Bold.ttf", s)            # noqa: E731
F_REG = lambda s: font("DejaVuSans.ttf", s)                  # noqa: E731


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns list of lines fitting width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if text_w(draw, trial, fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [""]


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


# Rough continent outlines (lon, lat) for the stylised world map.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-75, 62),
     (-65, 60), (-55, 52), (-60, 47), (-70, 42), (-75, 35), (-80, 32),
     (-85, 30), (-90, 21), (-95, 19), (-105, 20), (-110, 24), (-120, 34),
     (-125, 40), (-125, 49), (-135, 58), (-155, 60), (-168, 66)],
    # Greenland
    [(-58, 64), (-45, 60), (-40, 65), (-30, 68), (-25, 70), (-35, 76),
     (-55, 76), (-58, 70)],
    # South America
    [(-80, 9), (-75, 11), (-62, 10), (-55, 6), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -28), (-55, -35), (-65, -41), (-70, -50),
     (-73, -54), (-70, -40), (-72, -20), (-77, -12), (-80, -5), (-80, 9)],
    # Africa
    [(-17, 15), (-10, 31), (-5, 35), (10, 37), (20, 32), (32, 31), (35, 28),
     (43, 12), (51, 11), (48, 2), (40, -10), (35, -18), (32, -26), (26, -34),
     (18, -35), (14, -22), (12, -6), (8, 4), (-8, 5), (-13, 8), (-17, 15)],
    # Eurasia
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (10, 58), (18, 56),
     (24, 58), (30, 62), (40, 68), (55, 68), (70, 72), (90, 75), (110, 76),
     (130, 72), (150, 70), (170, 66), (178, 65), (170, 60), (162, 56),
     (156, 51), (142, 50), (140, 40), (130, 33), (122, 30), (115, 22),
     (108, 18), (105, 9), (100, 8), (98, 12), (94, 16), (90, 22), (86, 20),
     (80, 15), (77, 8), (75, 12), (72, 20), (66, 25), (61, 25), (57, 26),
     (52, 28), (48, 30), (44, 29), (40, 32), (36, 36), (30, 38), (26, 38),
     (23, 36), (19, 40), (12, 44), (3, 42), (-2, 37), (-10, 36)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (130, -32), (137, -35),
     (140, -38), (147, -39), (150, -37), (153, -27), (153, -24), (146, -19),
     (142, -15), (142, -11), (136, -12), (132, -12), (126, -14), (122, -17),
     (118, -20), (113, -22)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 41),
     (142, 44), (144, 44), (141, 40), (139, 37), (137, 35), (134, 34)],
    # Indonesia
    [(95, 5), (98, 3), (100, 0), (104, -3), (106, -6), (110, -7), (114, -8),
     (118, -9), (120, -10), (122, -9), (125, -9), (128, -4), (130, -2),
     (132, 0), (136, -2), (140, -4), (141, -8), (138, -8), (135, -5),
     (131, -1), (128, 1), (125, 1), (122, 0), (119, 0), (117, 2), (115, 1),
     (112, -2), (110, -5), (108, -6), (106, -5), (104, -2), (101, 1),
     (98, 4), (95, 5)],
    # New Zealand
    [(167, -45), (170, -42), (173, -40), (176, -38), (178, -37), (175, -40),
     (172, -43), (168, -46), (167, -45)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (1, 52), (-5, 50)],
]


def draw_map(draw, box):
    """Draw stylised continents + numbered pins inside box (x0,y0,x1,y1)."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=SEA, outline=RULE)
    bw, bh = x1 - x0, y1 - y0

    def proj(lon, lat):
        return (x0 + (lon + 180.0) / 360.0 * bw,
                y0 + (85.0 - lat) / 145.0 * bh)

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_LINE)
    for num, _lon, _lat, dlon, dlat in PINS:
        px, py = proj(dlon, dlat)
        r = 4
        draw.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                     outline=(255, 255, 255))
        fnt = F_BOLD(6)
        tw = text_w(draw, str(num), fnt)
        draw.text((px - tw / 2, py - 4), str(num), font=fnt,
                  fill=(255, 255, 255))


def draw_scene(draw, key, box, accent):
    """Tiny pictogram for a picture card inside box (x0,y0,x1,y1)."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=accent)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    w, h = x1 - x0, y1 - y0
    white = (255, 255, 255)
    dark = (20, 20, 20)
    if key == "ship":
        draw.polygon([(x0 + 8, cy + 6), (x1 - 8, cy + 6), (x1 - 16, cy + 12),
                      (x0 + 16, cy + 12)], fill=white)
        draw.rectangle([cx - 2, cy - 8, cx + 2, cy + 6], fill=white)
        draw.polygon([(cx, cy - 12), (cx + 8, cy - 6), (cx, cy - 2)],
                     fill=(255, 200, 60))
    elif key == "flags":
        for i, fx in enumerate((x0 + 12, cx, x1 - 12)):
            draw.line([fx, y0 + 6, fx, y1 - 4], fill=white, width=2)
            draw.polygon([(fx, y0 + 6), (fx + 10, y0 + 9), (fx, y0 + 12)],
                         fill=(255, 200, 60) if i % 2 else white)
    elif key == "building":
        draw.rectangle([x0 + 10, y0 + 8, x1 - 10, y1 - 4], fill=white)
        draw.line([cx, y0 + 8, cx - 6, y1 - 4], fill=dark, width=2)
        draw.line([cx - 6, y1 - 4, cx + 4, y0 + 14], fill=dark, width=2)
    elif key == "ballot":
        draw.rectangle([x0 + 12, y0 + 10, x1 - 12, y1 - 6], fill=white)
        draw.rectangle([cx - 10, y0 + 12, cx + 10, y0 + 15], fill=dark)
        draw.text((cx - 8, y0 + 18), "258", font=F_BOLD(10), fill=dark)
    elif key == "flame":
        draw.polygon([(cx, y0 + 4), (cx + 10, cy), (cx + 6, y1 - 6),
                      (cx - 6, y1 - 6), (cx - 10, cy)], fill=(255, 200, 60))
        draw.polygon([(cx, cy - 2), (cx + 5, cy + 4), (cx, y1 - 8),
                      (cx - 5, cy + 4)], fill=RED)
    elif key == "waves":
        for yy in (cy - 4, cy + 3):
            pts = []
            for xx in range(x0 + 6, x1 - 4, 4):
                pts.append((xx, yy + (4 if (xx // 4) % 2 else -4)))
            draw.line(pts, fill=white, width=2)
    elif key == "chart":
        draw.line([(x0 + 8, y0 + 8), (cx - 4, cy), (cx + 6, cy - 4),
                   (x1 - 8, y1 - 8)], fill=white, width=3)
        draw.polygon([(x1 - 8, y1 - 8), (x1 - 16, y1 - 8), (x1 - 8, y1 - 16)],
                     fill=white)
    elif key == "tanker":
        draw.rectangle([x0 + 6, cy, x1 - 6, cy + 8], fill=white)
        draw.rectangle([x1 - 22, cy - 8, x1 - 10, cy], fill=white)
        draw.rectangle([x0 + 10, cy - 6, x0 + 22, cy], fill=(255, 200, 60))
    elif key == "drone":
        draw.line([x0 + 10, y0 + 8, x1 - 10, y1 - 8], fill=white, width=2)
        draw.line([x1 - 10, y0 + 8, x0 + 10, y1 - 8], fill=white, width=2)
        for px, py in ((x0 + 10, y0 + 8), (x1 - 10, y0 + 8),
                       (x0 + 10, y1 - 8), (x1 - 10, y1 - 8)):
            draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=white)
    elif key == "dome":
        draw.pieslice([cx - 14, y0 + 4, cx + 14, y0 + 28], 180, 360,
                      fill=white)
        draw.rectangle([x0 + 10, y1 - 8, x1 - 10, y1 - 4], fill=white)
        draw.rectangle([cx - 2, y0 + 2, cx + 2, y0 + 6], fill=white)
    elif key == "heli":
        draw.line([x0 + 8, y0 + 6, x1 - 8, y0 + 6], fill=white, width=2)
        draw.ellipse([cx - 12, cy - 6, cx + 12, cy + 6], fill=white)
        draw.polygon([(cx + 12, cy), (x1 - 6, cy - 2), (x1 - 6, cy + 4)],
                     fill=white)
    elif key == "cloud":
        for ox, oy, r in ((-8, 2, 8), (0, -4, 10), (9, 2, 8)):
            draw.ellipse([cx + ox - r, cy + oy - r, cx + ox + r,
                          cy + oy + r], fill=white)
        draw.rectangle([cx - 14, cy + 2, cx + 16, cy + 8], fill=white)
    elif key == "truck":
        draw.rectangle([x0 + 8, cy - 6, cx + 6, cy + 6], fill=white)
        draw.rectangle([cx + 8, cy - 2, x1 - 8, cy + 6], fill=(255, 200, 60))
        for wx in (x0 + 16, cx, x1 - 14):
            draw.ellipse([wx - 4, cy + 6, wx + 4, cy + 12], fill=dark)
    elif key == "un":
        draw.rectangle([x0 + 12, y0 + 10, x1 - 12, y1 - 4], fill=white)
        draw.line([cx, y0 + 2, cx, y0 + 10], fill=white, width=2)
        draw.polygon([(cx, y0 + 2), (cx + 8, y0 + 4), (cx, y0 + 7)],
                     fill=(255, 200, 60))
    elif key == "sat":
        draw.rectangle([cx - 6, cy - 5, cx + 6, cy + 5], fill=white)
        draw.rectangle([x0 + 6, cy - 3, cx - 8, cy + 3], fill=(255, 200, 60))
        draw.rectangle([cx + 8, cy - 3, x1 - 6, cy + 3], fill=(255, 200, 60))
    elif key == "mine":
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=white)
        for ang in range(0, 360, 45):
            import math
            dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            draw.line([cx + dx * 8, cy + dy * 8, cx + dx * 13, cy + dy * 13],
                      fill=white, width=2)
    elif key == "badge":
        draw.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=(255, 200, 60))
        draw.text((cx - 4, cy - 7), "*", font=F_BOLD(14), fill=dark)
    elif key == "screen":
        draw.rectangle([x0 + 10, y0 + 6, x1 - 10, y1 - 8], fill=white)
        draw.line([x0 + 14, y0 + 11, x1 - 18, y0 + 11], fill=dark, width=2)
        draw.line([x0 + 14, y0 + 16, x1 - 14, y0 + 16], fill=dark, width=2)
        draw.line([x0 + 14, y0 + 21, x1 - 22, y0 + 21], fill=dark, width=2)
    # subtle frame
    draw.rectangle(box, outline=(0, 0, 0, 40))


def draw_cards_row(draw, cards, y, height):
    """One row of 9 picture cards; returns bottom y."""
    gap = 8
    total_w = W - 2 * MARGIN
    cw = (total_w - gap * (len(cards) - 1)) // len(cards)
    for i, (caption, scene, accent) in enumerate(cards):
        x0 = MARGIN + i * (cw + gap)
        x1 = x0 + cw
        draw.rectangle([x0, y, x1, y + height], fill=CARD_BG, outline=RULE)
        draw_scene(draw, scene, (x0 + 1, y + 1, x1 - 1, y + 26), accent)
        lines = wrap(draw, caption, F_REG(8), cw - 6)
        draw_lines(draw, lines[:2], x0 + 3, y + 28, F_REG(8), INK, 10)
    return y + height


def story_block_height(draw, stories, col_w):
    """Height of a column's stories (without section headers)."""
    total = 0
    for _num, _region, headline, summary, source in stories:
        hl = wrap(draw, headline, F_BOLD(10), col_w - 22)
        sl = wrap(draw, summary, F_REG(9), col_w - 22)
        src = wrap(draw, "— " + source, F_REG(8), col_w - 22)
        total += len(hl) * 12 + len(sl) * 11 + len(src) * 10 + 6
    return total


def draw_column(draw, regions, x, y, col_w, grid_bottom):
    """Draw region sections + stories in one column; returns bottom y.

    Per story: 1-line headline + max 2 lines of summary+source combined
    (summary is truncated with an ellipsis if it would spill to 3 lines),
    so every story costs exactly 35 px and columns stay in the grid.
    """
    by_region = {}
    for s in STORIES:
        by_region.setdefault(s[1], []).append(s)
    for region in regions:
        stories = by_region[region]
        # section header bar
        draw.rectangle([x, y, x + col_w, y + 19], fill=TEAL)
        label = f"{region}  ·  {len(stories)}"
        draw.text((x + 6, y + 4), label, font=F_BOLD(10), fill=(255, 255, 255))
        y += 24
        for num, _r, headline, summary, source in stories:
            draw.text((x, y), f"{num:02d}", font=F_BOLD(10), fill=AMBER)
            tx = x + 22
            hl = wrap(draw, headline, F_BOLD(10), col_w - 22)
            y = draw_lines(draw, hl[:1], tx, y, F_BOLD(10), INK, 11)
            text = summary + " — " + source
            lines = wrap(draw, text, F_REG(8), col_w - 22)
            while len(lines) > 2 and len(summary) > 40:
                summary = summary[:-4].rstrip().rstrip(".")
                text = summary + "… — " + source
                lines = wrap(draw, text, F_REG(8), col_w - 22)
            y = draw_lines(draw, lines[:2], tx, y, F_REG(8), (40, 40, 40), 10)
            y += 4
    return y


def build(output_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead ----
    title = "THE WORLD IN ONE IMAGE"
    f_title = F_SERIF(34)
    tw = text_w(d, title, f_title)
    d.text(((W - tw) / 2, 8), title, font=f_title, fill=INK)
    d.line([MARGIN, 52, W - MARGIN, 52], fill=INK, width=2)
    sub = f"{EDITION_DATE}  ·  36 STORIES  ·  7 REGIONS  ·  EVERY STORY SOURCED"
    f_sub = F_BOLD(11)
    tw = text_w(d, sub, f_sub)
    d.text(((W - tw) / 2, 58), sub, font=f_sub, fill=AMBER)

    # ---- Stat strip (6 boxes) ----
    sy, sh = 80, 44
    sw = (W - 2 * MARGIN - 5 * 8) // 6
    for i, (num, label, _src) in enumerate(STATS):
        x0 = MARGIN + i * (sw + 8)
        d.rectangle([x0, sy, x0 + sw, sy + sh], fill=CARD_BG, outline=RULE)
        d.text((x0 + 8, sy + 3), num, font=F_BOLD(19), fill=AMBER)
        lines = wrap(d, label, F_REG(8), sw - 16)
        draw_lines(d, lines[:2], x0 + 8, sy + 26, F_REG(8), GREY, 10)

    # ---- Lead story (left) + map (right) ----
    ly = 132
    lead_w = 624
    d.text((MARGIN, ly), "LEAD — UKRAINE'S WAR REACHES LIBYA",
           font=F_BOLD(10), fill=AMBER)
    head = ["UKRAINE SINKS RUSSIAN", "WARSHIP OFF LIBYA"]
    y = draw_lines(d, head, MARGIN, ly + 18, F_SERIF(29), INK, 34)
    deck = ("Ukrainian sea drones sank the corvette Merkury off Benghazi, "
            "destroying a helicopter and hitting a second ship — as Russian "
            "strikes killed 15 people across the Kyiv region.")
    dl = wrap(d, deck, F_REG(11), lead_w)
    y = draw_lines(d, dl, MARGIN, y + 4, F_REG(11), (40, 40, 40), 14)
    d.text((MARGIN, y + 4), "Reuters · AP · CNN  —  23 NOV",
           font=F_REG(9), fill=GREY)

    mx0, my0, mx1, my1 = 652, ly, W - MARGIN, 258
    d.text((mx0, ly), "WHERE IT HAPPENED — PINS = STORY NUMBERS",
           font=F_BOLD(10), fill=TEAL)
    draw_map(d, (mx0, ly + 18, mx1, my1))

    # ---- Picture cards, row 1 ----
    y = draw_cards_row(d, CARDS[:9], 264, 50)

    # ---- Story grid ----
    grid_top = 322
    grid_bottom = 906
    col_w = (W - 2 * MARGIN - 2 * 8) // 3
    col_x = [MARGIN, MARGIN + col_w + 8, MARGIN + 2 * (col_w + 8)]
    bottoms = []
    for i, regions in enumerate(COLUMNS):
        bottoms.append(draw_column(d, regions, col_x[i], grid_top, col_w,
                                   grid_bottom))
    max_bottom = max(bottoms)
    assert max_bottom <= grid_bottom, f"grid overflow: {max_bottom}"
    # Fill the shortest column once with a checking note (informative,
    # not filler). Only one copy: drawing it in every short column
    # duplicates the same text.
    note = ("HOW THIS PAGE WAS CHECKED — Every story was verified against "
            "its named source on 23 Nov 2026 before drawing. Casualty "
            "figures are those reported that day; later reporting may "
            "revise them.")
    for i, b in enumerate(bottoms):
        if grid_bottom - b >= 64:
            d.rectangle([col_x[i], b + 4, col_x[i] + col_w, grid_bottom - 4],
                        outline=RULE)
            lines = wrap(d, note, F_REG(9), col_w - 12)
            draw_lines(d, lines, col_x[i] + 6, b + 10, F_REG(9), GREY, 12)
            break

    # ---- Picture cards, row 2 ----
    draw_cards_row(d, CARDS[9:], 912, 50)

    # ---- Footer: DATE CHECK ----
    d.line([MARGIN, 970, W - MARGIN, 970], fill=INK, width=2)
    foot = ("DATE CHECK — Every story on this page is from the 23 November 2026 "
            "news cycle. Events from late Sunday 22 Nov are dated to this "
            "edition, as reported on Monday. Sources are named with each story.")
    fl = wrap(d, foot, F_REG(9), W - 2 * MARGIN)
    y = draw_lines(d, fl, MARGIN, 976, F_REG(9), INK, 12)
    d.text((MARGIN, y + 2), "THE WORLD IN ONE IMAGE · 23 NOV 2026 · 36 STORIES · 7 REGIONS",
           font=F_BOLD(9), fill=GREY)

    img.save(output_path, "PNG", optimize=True)

    # ---- Count checks (template rules) ----
    regions = sorted({s[1] for s in STORIES})
    assert len(STORIES) == 36, len(STORIES)
    assert len(regions) == 7, regions
    assert sum(len([s for s in STORIES if s[1] == r]) for r in regions) == 36
    assert len(STATS) == 6
    assert len(CARDS) == 18
    assert len(PINS) == 12
    size = os.path.getsize(output_path)
    assert size <= 1024 * 1024, f"over 1 MiB: {size}"
    print(f"OK {output_path}: {size} bytes, 1024x1024")
    print(f"stories={len(STORIES)} regions={len(regions)} "
          f"({', '.join(f'{r}:{len([s for s in STORIES if s[1]==r])}' for r in regions)})")
    print(f"stats={len(STATS)} cards={len(CARDS)} pins={len(PINS)} "
          f"grid_bottom_max={max_bottom}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "world-news-23-nov-2026.png")
    build(out)
