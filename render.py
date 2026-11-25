"""Render The Horizon Post — Wednesday, 25 November 2026.

Draws a one-page newspaper front page (1024x1024 PNG) with original
vector art made only from Pillow drawing primitives. No photos, no
downloaded images, no network.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (24, 24, 22)
RED = (163, 22, 33)
NAVY = (24, 48, 84)
MUTED = (96, 92, 82)
RULE = (180, 172, 152)
SEA = (228, 234, 236)
LAND = (216, 208, 186)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, text, f, max_w, max_lines=None):
    """Greedy word wrap; returns list of lines fitting max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        # trim last line with an ellipsis if it was cut
        while lines and text_w(draw, lines[-1] + "…", f) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "…"
    return lines


def fit_lines(draw, text, f, max_w, max_lines, min_size, path):
    """Shrink font until the wrapped text fits max_lines."""
    size = f.size
    while size > min_size:
        lines = wrap(draw, text, font(path, size), max_w, max_lines)
        if len(lines) <= max_lines:
            return font(path, size), lines
        size -= 1
    return font(path, size), wrap(draw, text, font(path, size), max_w, max_lines)


def draw_centered(draw, y, text, f, fill, x0=0, x1=W):
    w = text_w(draw, text, f)
    draw.text(((x0 + x1 - w) / 2, y), text, font=f, fill=fill)


def hline(draw, y, x0, x1, fill=RULE, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


# ---------------------------------------------------------------- masthead
def draw_masthead(draw):
    title = font(SERIF_B, 56)
    draw_centered(draw, 12, "The Horizon Post", title, INK)
    hline(draw, 82, 28, 996, fill=INK, width=2)
    date_f = font(SANS_B, 15)
    draw_centered(draw, 88, "WEDNESDAY  25  NOVEMBER  2026", date_f, INK)
    sub_f = font(SANS, 12)
    draw_centered(
        draw, 110,
        "THE WORLD ON ONE PAGE  —  30 STORIES  ·  ALL FROM WEDNESDAY 25 NOV",
        sub_f, MUTED)
    hline(draw, 130, 28, 996, fill=INK, width=2)
    hline(draw, 134, 28, 996, fill=INK, width=1)


# -------------------------------------------------------------- stats strip
STATS = [
    ("11", "hurt in second strike\non Riyadh tower"),
    ("25", "hostages held in\nCartagena supermarket"),
    ("$100m", "Shein to pay\nin FTC settlement"),
    ("5.3", "quake shakes Nepal's\nKoshi province"),
]


def draw_stats(draw):
    x0, y0, w, h = 28, 138, 968, 42
    col_w = w / 4
    num_f = font(SERIF_B, 22)
    lab_f = font(SANS, 11)
    for i, (num, lab) in enumerate(STATS):
        cx = x0 + col_w * i
        draw.text((cx + 8, y0), num, font=num_f, fill=RED)
        nw = text_w(draw, num, num_f)
        for j, line in enumerate(lab.split("\n")):
            draw.text((cx + 16 + nw, y0 + 2 + j * 14), line,
                      font=lab_f, fill=INK)
        if i:
            draw.line([(cx, y0 + 2), (cx, y0 + h - 4)], fill=RULE, width=1)
    hline(draw, 186, 28, 996, fill=INK, width=1)


# ------------------------------------------------------------ hero artwork
def draw_tower(draw, x, y, w, h):
    """Skyscraper silhouette with facade damage (Riyadh)."""
    draw.rectangle([x, y, x + w, y + h], fill=(30, 42, 66))
    # dusk sky band
    draw.rectangle([x, y, x + w, y + 26], fill=(58, 74, 104))
    # tower body
    tx0, tx1 = x + w * 0.36, x + w * 0.64
    draw.polygon([(tx0, y + h), (tx0, y + 34), (tx0 + 8, y + 22),
                  (tx1 - 8, y + 22), (tx1, y + 34), (tx1, y + h)],
                 fill=(16, 22, 38))
    # lit windows
    for r in range(6):
        for c in range(3):
            wx = tx0 + 8 + c * 14
            wy = y + 42 + r * 11
            lit = (r + c) % 3 != 0
            draw.rectangle([wx, wy, wx + 7, wy + 5],
                           fill=(240, 200, 90) if lit else (52, 64, 92))
    # damage burst near the top of the facade
    bx, by = (tx0 + tx1) / 2, y + 30
    for ang in range(0, 360, 30):
        import math
        r1 = 16 if ang % 60 == 0 else 9
        ex = bx + r1 * math.cos(math.radians(ang))
        ey = by + r1 * math.sin(math.radians(ang)) * 0.8
        draw.line([(bx, by), (ex, ey)], fill=(232, 90, 40), width=3)
    draw.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=(232, 90, 40))
    # smoke wisps
    for i, (sx, sy, sr) in enumerate([(bx - 26, by - 12, 7),
                                      (bx + 24, by - 18, 9),
                                      (bx + 30, by - 4, 6)]):
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                     fill=(150, 148, 140))
    # neighbouring towers + ground
    draw.rectangle([x + 8, y + h - 42, x + 44, y + h], fill=(40, 54, 82))
    draw.rectangle([x + w - 44, y + h - 30, x + w - 8, y + h],
                   fill=(40, 54, 82))
    draw.rectangle([x, y + h - 4, x + w, y + h], fill=(16, 22, 38))


def draw_shield(draw, x, y, w, h):
    """Cracked shield and padlock (CIA breach)."""
    draw.rectangle([x, y, x + w, y + h], fill=(24, 48, 84))
    cx, cy = x + w / 2, y + h / 2 + 4
    sw, sh = 74, 84
    pts = [(cx - sw / 2, cy - sh / 2), (cx + sw / 2, cy - sh / 2),
           (cx + sw / 2, cy + 6), (cx, cy + sh / 2),
           (cx - sw / 2, cy + 6)]
    draw.polygon(pts, fill=(240, 238, 228), outline=(163, 22, 33), width=3)
    # padlock
    draw.ellipse([cx - 13, cy - 14, cx + 13, cy + 12], fill=NAVY)
    draw.rectangle([cx - 8, cy - 26, cx + 8, cy - 10], outline=NAVY, width=4)
    draw.ellipse([cx - 3, cy - 6, cx + 3, cy + 0], fill=(240, 238, 228))
    draw.line([(cx, cy), (cx, cy + 7)], fill=(240, 238, 228), width=3)
    # jagged crack across the shield
    crack = [(cx - 30, cy - 38), (cx - 12, cy - 22), (cx - 20, cy - 6),
             (cx + 2, cy + 8), (cx - 6, cy + 24), (cx + 14, cy + 34)]
    draw.line(crack, fill=RED, width=4, joint="curve")
    # small warning dots
    for dx, dy in [(-52, -30), (54, -26), (-56, 30), (56, 32)]:
        draw.ellipse([cx + dx - 3, cy + dy - 3, cx + dx + 3, cy + dy + 3],
                     fill=(240, 200, 90))


def draw_gavel(draw, x, y, w, h):
    """Judge's gavel and microchip (Huawei verdict)."""
    draw.rectangle([x, y, x + w, y + h], fill=(96, 62, 40))
    # chip
    cx, cy = x + w * 0.30, y + h * 0.56
    s = 34
    draw.rectangle([cx - s, cy - s, cx + s, cy + s], fill=(20, 26, 34))
    draw.rectangle([cx - s + 9, cy - s + 9, cx + s - 9, cy + s - 9],
                   outline=(240, 200, 90), width=2)
    draw.text((cx - 8, cy - 7), "AI", font=font(SANS_B, 13),
              fill=(240, 200, 90))
    for k in range(-1, 2):
        draw.line([(cx + k * 18, cy - s), (cx + k * 18, cy - s - 10)],
                  fill=(200, 196, 180), width=3)
        draw.line([(cx + k * 18, cy + s), (cx + k * 18, cy + s + 10)],
                  fill=(200, 196, 180), width=3)
    # gavel head + handle (diagonal)
    import math
    ang = math.radians(-32)
    hx, hy = x + w * 0.62, y + h * 0.34
    dx, dy = math.cos(ang), math.sin(ang)
    px, py = -dy, dx
    hw, hl = 52, 20
    head = [(hx + dx * hw - px * hl, hy + dy * hw - py * hl),
            (hx + dx * hw + px * hl, hy + dy * hw + py * hl),
            (hx - dx * hw + px * hl, hy - dy * hw + py * hl),
            (hx - dx * hw - px * hl, hy - dy * hw - py * hl)]
    draw.polygon(head, fill=(52, 34, 20))
    draw.line([(hx - dx * 10, hy - dy * 10),
               (hx - dx * 66, hy - dy * 66)], fill=(52, 34, 20), width=9)
    # sound block
    draw.ellipse([x + w * 0.60, y + h - 30, x + w * 0.88, y + h - 12],
                 fill=(52, 34, 20))
    # motion ticks
    for mx, my in [(x + w * 0.86, y + 16), (x + w * 0.92, y + 30)]:
        draw.line([(mx, my), (mx + 10, my - 6)], fill=(240, 238, 228),
                  width=3)


HERO = [
    ("1", "RIYADH · WAR",
     "Houthis hit Riyadh's tallest tower again",
     "Eleven hurt in the second strike on the PIF tower in a week; "
     "the Saudi-led coalition vows a decisive response.",
     "REUTERS · SAUDI CIVIL DEFENCE", draw_tower),
    ("2", "WASHINGTON · SECURITY",
     "CIA says its unclassified system was breached",
     "The CIA and the director of national intelligence found a breach "
     "of an open-source intelligence network. No classified data was "
     "involved.",
     "CNN · REUTERS", draw_shield),
    ("3", "NEW YORK · JUSTICE",
     "Huawei found guilty of stealing trade secrets",
     "A jury convicts Huawei on 10 of 12 counts after a three-month "
     "trial; acquitted of racketeering.",
     "US DOJ · AP", draw_gavel),
]


def draw_hero(draw):
    y0, ph = 192, 232
    pw, gap = 312, 16
    for i, (num, kicker, head, deck, src, art) in enumerate(HERO):
        x = 28 + i * (pw + gap)
        draw.rectangle([x, y0, x + pw, y0 + ph], outline=RULE, width=1)
        art(draw, x + 1, y0 + 1, pw - 2, 96)
        # number badge
        draw.ellipse([x + 8, y0 + 102, x + 30, y0 + 124], fill=RED)
        draw.text((x + 15, y0 + 105), num, font=font(SANS_B, 13),
                  fill=(255, 255, 255))
        draw.text((x + 36, y0 + 106), kicker, font=font(SANS_B, 10),
                  fill=RED)
        hf, lines = fit_lines(draw, head, font(SERIF_B, 18), pw - 16, 2,
                              14, SERIF_B)
        yy = y0 + 128
        for line in lines:
            draw.text((x + 8, yy), line, font=hf, fill=INK)
            yy += hf.size + 2
        df, dlines = fit_lines(draw, deck, font(SANS, 11), pw - 16, 3,
                               9, SANS)
        yy += 2
        for line in dlines:
            draw.text((x + 8, yy), line, font=df, fill=(48, 46, 42))
            yy += df.size + 3
        draw.text((x + 8, y0 + ph - 14), src, font=font(SANS_B, 9),
                  fill=MUTED)

# ------------------------------------------------------------- stories 4-12
STORIES = [
    ("4", "CARTAGENA · CRIME", "Gunmen hold 25 hostages in supermarket",
     "Failed armoured-car hijack; five older women freed; troops surround "
     "an Exito store.", "REUTERS"),
    ("5", "KATHMANDU · DISASTER", "5.3 quake shakes Nepal, felt in India",
     "Koshi province, 10 km deep; no casualties reported.",
     "EMSC · REUTERS"),
    ("6", "PARIS · JUSTICE", "Sarkozy and wife ordered to stand trial",
     "Libyan funding case; pre-trial hearing set for 1 April 2027.",
     "REUTERS"),
    ("7", "CHICAGO · TRAVEL", "Radar fault delays flights into O'Hare",
     "Ground radar outage; FAA warns arrivals may halt.", "FAA"),
    ("8", "NEW YORK · MARKETS", "Nvidia slides 7% as Congress presses Huang",
     "Lawmakers seek answers on Huang's return; shares fall.", "REUTERS"),
    ("9", "STOCKHOLM · POLITICS", "Swedish vote on Kristersson staying on",
     "Parliament votes on the Moderates leader remaining prime minister.",
     "REUTERS"),
    ("10", "WASHINGTON · TRADE", "US to unveil new tariffs on partners",
     "Trump administration set to announce after excess-capacity probe.",
     "BBC · REUTERS"),
    ("11", "WASHINGTON · POLITICS", "Trump pardons turkeys Freedom and Feathers",
     "Thanksgiving pardon; Giuliani awarded the Medal of Freedom.", "AP"),
    ("12", "VILLAVICENCIO · CRIME", "Car bomb injures 22 in Colombia",
     "Overnight blast near government offices; about 500 properties "
     "damaged.", "REUTERS"),
]


def draw_stories(draw):
    y0, rh, gap = 432, 88, 6
    cw, cg = 312, 16
    for idx, (num, kicker, head, deck, src) in enumerate(STORIES):
        row, col = divmod(idx, 3)
        x = 28 + col * (cw + cg)
        y = y0 + row * (rh + gap)
        draw.rectangle([x, y, x + cw, y + rh], outline=RULE, width=1)
        draw.ellipse([x + 7, y + 7, x + 25, y + 25], fill=NAVY)
        draw.text((x + 12, y + 9), num, font=font(SANS_B, 11),
                  fill=(255, 255, 255))
        draw.text((x + 30, y + 9), kicker, font=font(SANS_B, 9), fill=RED)
        hf, lines = fit_lines(draw, head, font(SERIF_B, 13), cw - 16, 2,
                              11, SERIF_B)
        yy = y + 26
        for line in lines:
            draw.text((x + 8, yy), line, font=hf, fill=INK)
            yy += hf.size + 1
        df, dlines = fit_lines(draw, deck, font(SANS, 9), cw - 16, 2,
                               8, SANS)
        for line in dlines:
            draw.text((x + 8, yy), line, font=df, fill=(48, 46, 42))
            yy += df.size + 2
        draw.text((x + 8, y + rh - 12), src, font=font(SANS_B, 8),
                  fill=MUTED)


# ------------------------------------------------------------------- map
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 66),
     (-75, 62), (-60, 47), (-70, 42), (-75, 35), (-80, 25), (-85, 29),
     (-90, 21), (-97, 16), (-105, 20), (-115, 28), (-125, 40), (-125, 49),
     (-140, 60), (-165, 60)],
    [(-80, 10), (-72, 12), (-62, 10), (-52, 5), (-40, -5), (-35, -8),
     (-40, -20), (-48, -28), (-58, -35), (-65, -41), (-70, -54),
     (-73, -37), (-70, -20), (-80, -5), (-81, 0)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 70), (25, 71),
     (18, 69), (12, 65), (5, 60), (-5, 58), (-10, 52), (-10, 43)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31),
     (35, 28), (43, 12), (48, 11), (51, 10), (44, 0), (40, -10),
     (35, -20), (32, -29), (20, -35), (15, -27), (12, -18), (9, -1),
     (9, 4), (-8, 5), (-13, 8), (-17, 12)],
    [(30, 70), (40, 68), (55, 68), (70, 72), (90, 75), (110, 76),
     (130, 72), (150, 70), (170, 66), (178, 65), (170, 60), (162, 56),
     (158, 52), (142, 50), (140, 40), (135, 35), (130, 33), (127, 35),
     (122, 38), (120, 30), (115, 22), (108, 18), (105, 10), (100, 8),
     (98, 12), (95, 16), (92, 21), (88, 22), (85, 19), (80, 13),
     (77, 8), (75, 12), (72, 20), (68, 23), (62, 25), (57, 26),
     (52, 28), (48, 29), (44, 29), (40, 31), (36, 36), (33, 36),
     (30, 36)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32),
     (137, -35), (140, -38), (145, -38), (150, -37), (153, -32),
     (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
     (136, -12), (132, -12), (126, -14), (122, -17), (118, -20)],
]

PINS = [("1", 46.7, 24.7), ("2", -77.0, 38.9), ("3", -74.0, 40.7),
        ("4", -75.5, 10.4), ("5", 85.3, 27.7), ("6", 2.35, 48.85),
        ("9", 18.07, 59.33)]


def draw_map(draw):
    x0, y0, w, h = 28, 714, 300, 232
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=SEA, outline=RULE, width=1)
    draw.text((x0 + 10, y0 + 8), "WHERE IT HAPPENED",
              font=font(SANS_B, 12), fill=INK)
    mx, my, mw, mh = x0 + 6, y0 + 28, w - 12, h - 36

    def proj(lon, lat):
        return (mx + (lon + 180) / 360 * mw,
                my + (90 - lat) / 180 * mh)

    for poly in CONTINENTS:
        draw.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND)
    for num, lon, lat in PINS:
        px, py = proj(lon, lat)
        draw.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED,
                     outline=(255, 255, 255), width=1)
        draw.text((px - 3, py - 6), num, font=font(SANS_B, 10),
                  fill=(255, 255, 255))


# ------------------------------------------------------------ also list
ALSO = [
    (13, "KYIV", "Zelenskiy confirms Ukraine hit a Russian ship in the Gulf of Finland; Norway urges caution."),
    (14, "WASHINGTON", "US envoy 'not certain' military aid to Israel ends this year as Trump promised."),
    (15, "BAGHDAD", "Iraqi PM orders federal control of Kurdish oilfields; Kurds reject the move."),
    (16, "MOSCOW", "Putin says retaliation 'inevitable' after Ukraine hit Russian oil plants."),
    (17, "ADEN", "Houthis will not seize Aden, Yemeni government forces say."),
    (18, "KINSHASA", "WHO evacuates staff from an Ebola hospital in DRC after three days sheltering."),
    (19, "NEW YORK", "Anthropic shares fall below its $83 IPO price, on track to lose nearly $200bn."),
    (20, "AUSTIN", "Dell lifts forecasts after a record quarter on AI server demand."),
    (21, "IOWA", "Army to detonate its lead-azide stockpile; residents told to evacuate."),
    (22, "CARACAS", "Venezuela reports total public debt of $237.5bn."),
    (23, "LONDON", "Russia's own figures show almost 500,000 war deaths in Ukraine."),
    (24, "LONDON", "UK ministers consult the public on changing the age of consent; PIP review finds benefits 'not fit for purpose'."),
    (25, "NEW DELHI", "Food inflation climbs as vegetable prices surge across India."),
    (26, "DAKAR", "Senegal reinstated as AFCON champions."),
    (27, "CANBERRA", "Australia's inflation hits 4.9%."),
    (28, "MUMBAI", "Sooryavanshi smashes the fastest List A double hundred."),
    (29, "CAMBRIDGE", "Astronomers find a star system 28 light-years away 'that should not exist'."),
    (30, "WASHINGTON", "Fort Hood shooter Hasan seeks a stay of execution set for next week."),
]


def draw_also(draw):
    x0, y0, w = 344, 714, 652
    draw.text((x0, y0 + 8), "ALSO ON WEDNESDAY 25 NOV",
              font=font(SANS_B, 12), fill=INK)
    hline(draw, y0 + 28, x0, x0 + w, fill=INK, width=1)
    f_num = font(SANS_B, 10)
    f_txt = font(SANS, 10)
    yy = y0 + 34
    for num, city, text in ALSO:
        # one line each: shrink text until it fits
        size = 10
        while size > 8:
            f = font(SANS, size)
            line = "%d %s: %s" % (num, city, text)
            if text_w(draw, line, f) <= w:
                break
            size -= 1
        draw.text((x0, yy), str(num), font=font(SANS_B, size), fill=RED)
        nw = text_w(draw, str(num) + " ", font(SANS_B, size))
        draw.text((x0 + nw, yy), "%s: %s" % (city, text),
                  font=font(SANS, size), fill=INK)
        yy += 10.5
    return yy


# ------------------------------------------------------------------ footer
def draw_footer(draw):
    y0 = 956
    draw.rectangle([28, y0, 996, y0 + 36], fill=RED)
    f = font(SANS_B, 10)
    line1 = ("DATE CHECK — NOT TODAY: left out because they are not this "
             "day's news.")
    line2 = ("Thu 19 Nov — first strike on the PIF tower, no injuries.   "
             "Sun 22 Nov — Ukraine sinks a Russian vessel in a Libyan port.")
    draw.text((40, y0 + 4), line1, font=f, fill=(255, 255, 255))
    draw.text((40, y0 + 19), line2, font=font(SANS, 10),
              fill=(255, 255, 255))
    close_f = font(SANS, 9)
    draw_centered(
        draw, 998,
        "Every story here was first reported on Wednesday 25 November 2026, "
        "as the named outlets reported it. Map and drawings are original "
        "vector art.",
        close_f, MUTED)
    draw_centered(
        draw, 1010,
        "Today is the International Day for the Elimination of Violence "
        "against Women.",
        close_f, MUTED)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    draw_stats(draw)
    draw_hero(draw)
    draw_stories(draw)
    draw_map(draw)
    draw_also(draw)
    draw_footer(draw)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
