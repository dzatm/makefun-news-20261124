#!/usr/bin/env python3
"""Generate the 24 November 2026 front page: THE WORLD — IN ONE IMAGE (v3).

Winner-template rebuild: spec header strip, region chips with counts,
UTC timeline, "day in numbers" strip, 13 numbered feature cards each
with a drawn vector scene + key-figure chip + confidence label + two
named sources, 25 one-line briefs (38 stories total), a world pin map,
a date-check strip listing excluded wrong-day stories, and a
methodology footer. Deterministic: fixed headlines, fixed fonts, fixed
layout, no timestamps, no randomness. Running it twice produces a
byte-identical entry.png.

Date discipline: every story happened or was first reported on Tuesday
24 November 2026 (UTC). Wrong-day stories are listed in the date-check
strip, not in the news columns. Per-story verification notes live in
research-notes-v3.md (transcripts folder).
"""
import hashlib
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 24
PAPER = (247, 242, 231)
INK = (20, 20, 20)
RED = (163, 22, 33)
NAVY = (30, 58, 95)
GREEN = (27, 94, 52)
AMBER = (166, 84, 0)
TEAL = (0, 128, 128)
PURPLE = (94, 48, 128)
DARKGREY = (70, 70, 70)
GREY = (84, 79, 70)
LIGHT = (186, 180, 167)
PINK = (172, 52, 110)
OLIVE = (86, 112, 28)
STEEL = (40, 100, 160)
SKY = (196, 216, 228)
SAND = (232, 214, 170)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def font(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size)


def serif(size):
    return font("DejaVuSerif-Bold.ttf", size)


def sans(size):
    return font("DejaVuSans.ttf", size)


def sans_bold(size):
    return font("DejaVuSans-Bold.ttf", size)


DATE_LINE = "TUESDAY, 24 NOVEMBER 2026"

# Region colours (also used for chips, card tags and map legend).
REGIONS = [
    ("NORTH AMERICA", NAVY),
    ("LATIN AMERICA", TEAL),
    ("EUROPE", PURPLE),
    ("MIDDLE EAST", RED),
    ("AFRICA", AMBER),
    ("SOUTH ASIA", PINK),
    ("EAST ASIA", OLIVE),
    ("SE ASIA", GREEN),
    ("INDIAN OCEAN", STEEL),
    ("GLOBAL", DARKGREY),
]
REGION_COLOUR = dict(REGIONS)

# Short region names for card tags (full names used in the chips row).
REGION_SHORT = {
    "NORTH AMERICA": "N AMERICA",
    "LATIN AMERICA": "LATIN AM",
    "EUROPE": "EUROPE",
    "MIDDLE EAST": "MID EAST",
    "AFRICA": "AFRICA",
    "SOUTH ASIA": "S ASIA",
    "EAST ASIA": "E ASIA",
    "SE ASIA": "SE ASIA",
    "INDIAN OCEAN": "IND OCEAN",
    "GLOBAL": "GLOBAL",
}

CONF_COLOUR = {
    "OFFICIAL": GREEN,
    "CONFIRMED": NAVY,
    "REPORTED": AMBER,
    "CLAIM": RED,
}

# Feature cards 1-13: (region, field, place, headline, detail, key figure,
# confidence, sources, scene name, (lon, lat) for the pin map)
CARDS = [
    ("NORTH AMERICA", "MARKETS", "NEW YORK",
     "DOW CLOSES ABOVE 50,000",
     "Dow ends at 50,018.70 (+0.85%) as money rotates into health and "
     "consumer stocks; Nasdaq falls 1.48% as chips slide — Nvidia −5.9%.",
     "50,018.70", "CONFIRMED", "AP · CNBC", "chart", (-74.0, 40.7)),
    ("NORTH AMERICA", "JUSTICE", "NEW YORK",
     "HUAWEI GUILTY ON 10 OF 12 COUNTS",
     "Brooklyn jury convicts on bank fraud and trade-secret theft; "
     "acquits on racketeering. Sentencing set for September 2027.",
     "10 OF 12", "CONFIRMED", "Reuters · CNN", "courthouse", (-71.5, 37.5)),
    ("EUROPE", "WAR", "UKRAINE",
     "RUSSIAN ATTACKS KILL 9 IN UKRAINE",
     "112 drones launched overnight; 88 downed or suppressed. 59 injured.",
     "112 DRONES", "CONFIRMED", "Kyiv Independent · UA Air Force",
     "skyline_drone", (30.5, 50.4)),
    ("EUROPE", "BUSINESS", "PARIS",
     "SANOFI BUYS INSMED FOR $41BN",
     "Pays $175 a share in cash — biggest pharma deal since 2023.",
     "$41BN", "OFFICIAL", "Sanofi · WSJ", "pill", (2.35, 48.9)),
    ("EUROPE", "SPACE", "KOUROU",
     "ARIANE 6 LIFTS 36 SATELLITES",
     "VA271 lifts off 11:14 UTC; Ariane 6's 10th flight.",
     "36 SATS", "OFFICIAL", "Arianespace · Spaceflight Now",
     "rocket", (-52.6, 5.2)),
    ("NORTH AMERICA", "TECHNOLOGY", "REDMOND",
     "MICROSOFT DECLARES 'CODE RED'",
     "After a historic 24-hour outage, vows one-hour recovery.",
     "24H OUTAGE", "OFFICIAL", "Reuters · Microsoft", "code_red",
     (-122.1, 47.7)),
    ("MIDDLE EAST", "WAR", "RIYADH",
     "HOUTHI DRONE HITS RIYADH TOWER",
     "Drone attack on PIF Tower in the financial district injures 11.",
     "11 HURT", "CONFIRMED", "Al Jazeera · PakistanTV", "tower_drone",
     (46.7, 24.6)),
    ("MIDDLE EAST", "WAR", "GAZA",
     "ISRAELI STRIKES KILL NINE",
     "Strikes kill Hamas security chief Naeem Abu Nahel among nine dead.",
     "9 KILLED", "REPORTED", "PakistanTV · One Turn", "gaza_skyline",
     (34.4, 31.5)),
    ("SE ASIA", "DISASTER", "SERANG, INDONESIA",
     "FACTORY FIRE TOLL RISES TO 26",
     "Candy-plant blaze: 28 missing; negligence probe opens.",
     "26 DEAD", "CONFIRMED", "CNA · AFU.id", "factory_fire", (106.1, -6.1)),
    ("SE ASIA", "DISASTER", "HANOI",
     "GAS BLAST KILLS 6 IN HANOI",
     "01:00 UTC blast at a hot-pot eatery collapses the building.",
     "6 DEAD", "CONFIRMED", "Reuters · AP", "blast", (105.8, 21.0)),
    ("SOUTH ASIA", "DISASTER", "KANNAUJ, INDIA",
     "TRUCK HITS SCHOOL BUS: 4 DIE",
     "00:30 UTC — truck rams parked school bus; 32 injured.",
     "4 DEAD · 32 HURT", "CONFIRMED", "PTI · Hindustan Times", "bus",
     (79.9, 27.0)),
    ("INDIAN OCEAN", "EARTH", "RODRIGUES",
     "M6.4 QUAKE OFF RODRIGUES",
     "11:06 UTC tremor; tsunami watch issued, then lifted.",
     "M6.4", "OFFICIAL", "USGS · GDACS", "seismograph", (63.4, -19.7)),
    ("MIDDLE EAST", "DISASTER", "RAS AL KHAIMAH",
     "13 DIE IN BUS–TRUCK CRASH",
     "Coach carrying 41 hits broken-down lorry; 14 injured.",
     "13 DEAD", "OFFICIAL", "UAE Interior Ministry · Gulf Business",
     "bus_truck", (55.9, 25.8)),
]

# One-line briefs 14-38: (region, field, text, source)
BRIEFS = [
    ("EUROPE", "WAR",
     "Putin admits strikes cut refining ~30%; export limits set", "ISW"),
    ("EUROPE", "WAR",
     "Leaked Rosstat data points to vast war death toll", "ISW"),
    ("AFRICA", "WAR",
     "Ukraine hits Russian ships off Benghazi; 2 Libyans die", "One Turn"),
    ("EUROPE", "DEFENCE",
     "MI5 warns Ukraine suppliers of Russian sabotage", "BBC"),
    ("MIDDLE EAST", "DIPLOMACY",
     "Iran refuses talks until seven conditions met", "PakistanTV"),
    ("MIDDLE EAST", "DEFENCE",
     "Katz: Iran developing chemical weapons", "Times of Israel"),
    ("EAST ASIA", "SPACE",
     "China names first foreign Tiangong astronaut", "Straits Times"),
    ("SE ASIA", "HUMAN RIGHTS",
     "14 nations recognise ICJ Rohingya ruling", "Horizon"),
    ("SE ASIA", "HUMAN RIGHTS",
     "Malaysia to return 6,500+ Rohingya refugees", "JAWS brief"),
    ("GLOBAL", "TECHNOLOGY",
     "Guterres: AI-risk framework within a year", "UN"),
    ("NORTH AMERICA", "HEALTH",
     "US measles deaths reach 14; cases near 6,000", "Horizon"),
    ("SOUTH ASIA", "EARTH",
     "M5.6 quake in Nepal's Koshi province", "HKO"),
    ("LATIN AMERICA", "CRIME",
     "Car bomb destroys buildings in Villavicencio", "The Hindu"),
    ("LATIN AMERICA", "CRIME",
     "Mexico to try 'El Chapo Isidro' despite US bid", "Horizon"),
    ("LATIN AMERICA", "ECONOMY",
     "Venezuela reports $237.5B public debt", "NXplace"),
    ("AFRICA", "EDUCATION",
     "Borno school enrolment nearly doubles", "Al Jazeera"),
    ("EUROPE", "ECONOMY",
     "De Cos tipped to succeed Lagarde at ECB", "Horizon"),
    ("EUROPE", "ENERGY",
     "Macron wants strategic rare-earth reserves", "Horizon"),
    ("EUROPE", "WELFARE",
     "UK disability-benefit shake-up threatens many", "Guardian"),
    ("NORTH AMERICA", "CRIME",
     "DOJ recovers $8B, charges 800+ in scam surge", "Fox News"),
    ("NORTH AMERICA", "WEATHER",
     "Record king tides flood Bay Area roads", "ABC7"),
    ("GLOBAL", "TRADE",
     "US preparing tariffs on 16 economies", "US media"),
    ("AFRICA", "SPORT",
     "CAS verdict due on AFCON final award", "Morning Sport Talk"),
    ("NORTH AMERICA", "SPORT",
     "Warriors edge Celtics 88–87; Rockets win", "Sofascore"),
    ("GLOBAL", "SPORT",
     "FIFA: four nations to co-host 2031 Women's World Cup", "AP"),
]

# UTC timeline: (HH:MM, label, side, x-nudge px)
TIMELINE = [
    ("00:30", "India bus crash", "below", 22),
    ("01:00", "Hanoi blast", "above", 14),
    ("05:30", "Sanofi–Insmed deal", "above", 0),
    ("11:06", "M6.4 quake", "below", -42),
    ("11:14", "Ariane 6 launch", "above", 4),
    ("11:37", "Ukraine 9 dead", "below", 42),
    ("13:58", "Gaza strikes", "above", 0),
    ("21:00", "Dow closes 50,018", "below", 0),
    ("21:33", "Riyadh drone hit", "above", 0),
]

# Day in numbers: (big figure, caption)
NUMBERS = [
    ("50,018.70", "Dow close, Tue"),
    ("10 of 12", "Huawei counts guilty"),
    ("$41BN", "Sanofi buys Insmed"),
    ("112", "drones at Ukraine"),
    ("36", "satellites on Ariane 6"),
    ("26", "dead in factory fire"),
]

DATE_CHECK = (
    "DATE CHECK — every story above happened or was first reported on "
    "Tuesday 24 Nov 2026 (UTC). Left out as earlier news: Mon 23 Nov: "
    "Huang reinstated as Nvidia CEO · Iran claim of 3 tankers mined in "
    "Hormuz · Trump hush-money appeal ruling · Sun 22 Nov: COP31 ends "
    "without a deal · Alcaraz wins ATP Finals."
)

METHOD = (
    "HOW SURE: OFFICIAL = on the record · CONFIRMED = 2+ outlets · "
    "REPORTED = single wire/local source · CLAIM = one side's account. "
    "All scenes are original vector drawings — no photos. Stories "
    "cross-checked against named sources and dated in UTC."
)


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def hline(draw, y, weight=2, fill=INK, x0=MARGIN, x1=None):
    draw.rectangle([x0, y, (x1 or W - MARGIN), y + weight - 1], fill=fill)


def fit_font(draw, text, make_font, max_w, start):
    """Largest size <= start whose single-line width fits max_w."""
    size = start
    while size > 7 and draw.textlength(text, font=make_font(size)) > max_w:
        size -= 1
    return make_font(size)


# ---------------------------------------------------------------- scenes
def scene_chart(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 244, 238))
    base = y + h - 8
    d.line([x + 8, y + 6, x + 8, base], fill=INK, width=1)
    d.line([x + 8, base, x + w - 6, base], fill=INK, width=1)
    lvl = y + int(h * 0.32)
    for sx in range(x + 12, x + w - 8, 10):
        d.line([sx, lvl, sx + 5, lvl], fill=RED, width=1)
    pts = [(x + 12, base - 6), (x + int(w * .3), base - 12),
           (x + int(w * .5), base - 10), (x + int(w * .7), y + int(h * .45)),
           (x + w - 14, y + 9)]
    d.line(pts, fill=GREEN, width=3)
    d.polygon([(x + w - 14, y + 5), (x + w - 6, y + 12), (x + w - 18, y + 14)], fill=GREEN)
    d.text((x + 14, lvl - 13), "50,000", font=sans_bold(9), fill=RED, anchor="la")


def scene_courthouse(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 236, 224))
    cx = x + w // 2
    top = y + 8
    d.polygon([(x + 14, top + 12), (cx, top), (x + w - 14, top + 12)], fill=NAVY)
    d.rectangle([x + 14, top + 12, x + w - 14, top + 16], fill=NAVY)
    col_top, col_bot = top + 19, y + h - 12
    for i in range(5):
        cxp = x + 24 + i * (w - 48) // 4
        d.rectangle([cxp - 3, col_top, cxp + 3, col_bot], fill=NAVY)
    d.rectangle([x + 10, col_bot, x + w - 10, col_bot + 4], fill=NAVY)
    d.rectangle([x + 6, col_bot + 5, x + w - 6, col_bot + 8], fill=NAVY)
    d.ellipse([cx - 4, top + 5, cx + 4, top + 13], fill=PAPER)


def _buildings(d, x, y, w, h, colour=INK, ground=None):
    ground = ground if ground is not None else y + h - 6
    heights = [0.55, 0.8, 0.45, 0.7, 0.6, 0.85, 0.5]
    bw = w // len(heights)
    for i, f in enumerate(heights):
        bx = x + i * bw + 2
        bh = int((ground - y) * f)
        d.rectangle([bx, ground - bh, bx + bw - 5, ground], fill=colour)
        for wy in range(ground - bh + 5, ground - 5, 9):
            for wx in range(bx + 4, bx + bw - 8, 8):
                d.rectangle([wx, wy, wx + 3, wy + 4], fill=(250, 230, 150))
    d.rectangle([x, ground, x + w, ground + 2], fill=colour)
    return ground


def _burst(d, cx, cy, r, colour=RED):
    import math
    for k in range(8):
        a = k * math.pi / 4
        d.line([cx, cy, cx + r * math.cos(a), cy + r * math.sin(a)],
               fill=colour, width=2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=colour)


def scene_skyline_drone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 232, 240))
    _buildings(d, x + 4, y + 8, w - 8, h - 8)
    dx, dy = x + int(w * .68), y + 12
    d.ellipse([dx - 6, dy - 2, dx + 6, dy + 3], fill=RED)
    d.line([dx - 10, dy - 5, dx + 10, dy - 5], fill=RED, width=1)
    _burst(d, x + int(w * .68), y + int(h * .38), 8, AMBER)


def scene_pill(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 238, 226))
    bx, by = x + 18, y + 12
    d.rectangle([bx, by, bx + 34, y + h - 8], outline=NAVY, width=3)
    d.rectangle([bx + 8, by - 6, bx + 26, by], fill=NAVY)
    d.rectangle([bx + 5, by + 14, bx + 29, by + 30], fill=(255, 255, 255), outline=NAVY, width=1)
    d.line([bx + 17, by + 18, bx + 17, by + 26], fill=RED, width=3)
    d.line([bx + 13, by + 22, bx + 21, by + 22], fill=RED, width=3)
    px, py = x + int(w * .52), y + int(h * .30)
    d.rounded_rectangle([px, py, px + 56, py + 22], radius=11, fill=RED)
    d.rectangle([px + 28, py, px + 56, py + 22], fill=(245, 245, 245))
    d.rounded_rectangle([px, py, px + 56, py + 22], radius=11, outline=INK, width=1)
    tx, ty = x + int(w * .64), y + h - 19
    d.polygon([(tx, ty), (tx + 34, ty), (tx + 34, ty + 13), (tx, ty + 13)], fill=AMBER)
    d.text((tx + 17, ty + 1), "$175", font=sans_bold(9), fill=(255, 255, 255), anchor="ma")


def scene_rocket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 34, 64))
    for sx, sy in [(14, 10), (40, 20), (w - 30, 12), (w - 55, 24), (70, 8)]:
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=(255, 255, 255))
    cx = x + w // 2
    nose = y + 4
    tail = y + h - 12
    d.polygon([(cx, nose), (cx - 8, nose + 12), (cx + 8, nose + 12)], fill=(240, 240, 240))
    d.rectangle([cx - 8, nose + 12, cx + 8, tail], fill=(240, 240, 240))
    d.rectangle([cx - 8, nose + 17, cx + 8, nose + 20], fill=RED)
    for s in (-1, 1):
        bx = cx + s * 14
        d.rectangle([bx - 4, nose + 14, bx + 4, tail], fill=(210, 210, 210))
        d.polygon([(bx - 5, tail), (bx + 5, tail), (bx, tail + 8)], fill=AMBER)
    d.polygon([(cx - 6, tail), (cx + 6, tail), (cx, tail + 11)], fill=AMBER)
    d.polygon([(cx - 3, tail), (cx + 3, tail), (cx, tail + 7)], fill=(255, 220, 90))


def scene_code_red(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 232, 232))
    mx, my = x + 22, y + 8
    mw, mh = w - 44, h - 22
    d.rectangle([mx, my, mx + mw, my + mh], fill=(30, 30, 40))
    d.rectangle([mx + 4, my + 4, mx + mw - 4, my + mh - 4], fill=(120, 20, 28))
    d.text((mx + mw // 2, my + mh // 2 - 8), "CODE RED", font=sans_bold(13),
           fill=(255, 255, 255), anchor="ma")
    d.rectangle([mx + mw // 2 - 3, my + mh, mx + mw // 2 + 3, my + mh + 5], fill=INK)
    d.rectangle([mx + mw // 2 - 16, my + mh + 5, mx + mw // 2 + 16, my + mh + 8], fill=INK)


def scene_tower_drone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(228, 236, 244))
    tx = x + int(w * .38)
    d.polygon([(tx, y + h - 6), (tx + 8, y + 6), (tx + 26, y + 6), (tx + 34, y + h - 6)],
              fill=NAVY)
    for wy in range(y + 14, y + h - 14, 10):
        d.line([tx + 8, wy, tx + 26, wy], fill=(250, 230, 150), width=2)
    dx, dy = x + int(w * .78), y + 14
    d.ellipse([dx - 7, dy - 2, dx + 7, dy + 3], fill=RED)
    d.line([dx - 12, dy - 6, dx + 12, dy - 6], fill=RED, width=1)
    d.line([dx, dy + 4, tx + 30, y + 22], fill=RED, width=1)
    _burst(d, tx + 30, y + 22, 8, AMBER)


def scene_gaza_skyline(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 230, 214))
    ground = _buildings(d, x + 4, y + 12, w - 8, h - 12, colour=(96, 84, 70))
    sx = x + int(w * .55)
    for i, r in enumerate((5, 8, 11)):
        d.ellipse([sx - r, y + 4 + i * 3, sx + r, y + 4 + i * 3 + r * 2],
                  outline=(120, 115, 105), width=2)
    _burst(d, sx, ground - int(h * .35), 7, RED)


def scene_factory_fire(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 234, 220))
    base = y + h - 8
    fx = x + 16
    d.rectangle([fx, base - 22, fx + 70, base], fill=(110, 96, 80))
    d.polygon([(fx, base - 22), (fx + 18, base - 32), (fx + 36, base - 22)], fill=(110, 96, 80))
    d.polygon([(fx + 34, base - 22), (fx + 52, base - 32), (fx + 70, base - 22)], fill=(110, 96, 80))
    d.rectangle([fx + 58, base - 44, fx + 66, base - 22], fill=(110, 96, 80))
    for i, fx2 in enumerate((fx + 12, fx + 30, fx + 48)):
        fh = 16 + (i % 2) * 7
        d.polygon([(fx2 - 6, base - 22), (fx2, base - 22 - fh), (fx2 + 6, base - 22)], fill=RED)
        d.polygon([(fx2 - 3, base - 22), (fx2, base - 22 - fh + 7), (fx2 + 3, base - 22)],
                  fill=AMBER)
    d.ellipse([fx + 52, base - 56, fx + 76, base - 40], outline=(120, 115, 105), width=2)


def scene_blast(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(236, 232, 224))
    bx = x + int(w * .3)
    d.rectangle([bx, y + 16, bx + 52, y + h - 6], fill=(120, 104, 84))
    for wy in range(y + 22, y + h - 14, 11):
        for wx in (bx + 8, bx + 24, bx + 40):
            d.rectangle([wx, wy, wx + 7, wy + 6], fill=(250, 230, 150))
    d.polygon([(bx + 52, y + h - 6), (bx + 78, y + h - 6), (bx + 58, y + h - 22)],
              fill=(120, 104, 84))
    _burst(d, bx + 62, y + int(h * .5), 13, RED)
    _burst(d, bx + 62, y + int(h * .5), 7, AMBER)


def _bus(d, x, y, w, colour, label=None):
    d.rounded_rectangle([x, y, x + w, y + 26], radius=5, fill=colour)
    for wx in range(x + 6, x + w - 10, 14):
        d.rectangle([wx, y + 5, wx + 9, y + 13], fill=(220, 238, 248))
    for wx in (x + 10, x + w - 18):
        d.ellipse([wx, y + 21, wx + 11, y + 32], fill=INK)
        d.ellipse([wx + 3, y + 24, wx + 8, y + 29], fill=(200, 200, 200))
    if label:
        d.text((x + w // 2, y + 14), label, font=sans_bold(8),
               fill=(255, 255, 255), anchor="ma")


def scene_bus(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(234, 238, 240))
    road = y + h - 12
    d.rectangle([x, road, x + w, road + 3], fill=DARKGREY)
    _bus(d, x + 10, road - 32, 86, AMBER, "SCHOOL")
    tx = x + 104
    d.rectangle([tx, road - 36, tx + 26, road - 4], fill=NAVY)
    d.rectangle([tx + 26, road - 30, tx + 44, road - 4], fill=NAVY)
    d.rectangle([tx + 30, road - 27, tx + 40, road - 18], fill=(220, 238, 248))
    for wx in (tx + 6, tx + 32):
        d.ellipse([wx, road - 9, wx + 11, road + 2], fill=INK)
    _burst(d, x + 100, road - 24, 7, RED)


def scene_seismograph(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(244, 240, 230))
    mid = y + h // 2
    for gx in range(x + 10, x + w - 6, 16):
        d.line([gx, y + 5, gx, y + h - 5], fill=(214, 208, 192), width=1)
    pts = [(x + 8, mid), (x + int(w * .3), mid), (x + int(w * .4), mid - 14),
           (x + int(w * .48), mid + 12), (x + int(w * .56), mid - 8),
           (x + int(w * .64), mid), (x + w - 10, mid)]
    d.line(pts, fill=RED, width=2)
    d.text((x + w - 10, y + 4), "M6.4", font=sans_bold(10), fill=RED, anchor="ra")


def scene_bus_truck(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(234, 238, 240))
    road = y + h - 12
    d.rectangle([x, road, x + w, road + 3], fill=DARKGREY)
    _bus(d, x + 8, road - 32, 78, STEEL)
    tx = x + 96
    d.rectangle([tx, road - 34, tx + 34, road - 4], fill=(140, 140, 140))
    d.rectangle([tx + 34, road - 28, tx + 48, road - 4], fill=(140, 140, 140))
    for wx in (tx + 5, tx + 36):
        d.ellipse([wx, road - 9, wx + 11, road + 2], fill=INK)
    _burst(d, x + 92, road - 22, 7, RED)
    d.text((tx + 17, road - 44), "PARKED", font=sans_bold(7), fill=DARKGREY, anchor="ma")


SCENES = {
    "chart": scene_chart,
    "courthouse": scene_courthouse,
    "skyline_drone": scene_skyline_drone,
    "pill": scene_pill,
    "rocket": scene_rocket,
    "code_red": scene_code_red,
    "tower_drone": scene_tower_drone,
    "gaza_skyline": scene_gaza_skyline,
    "factory_fire": scene_factory_fire,
    "blast": scene_blast,
    "bus": scene_bus,
    "seismograph": scene_seismograph,
    "bus_truck": scene_bus_truck,
}

# Simplified continent polygons (lon, lat) for the pin map.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 62), (-78, 58), (-76, 50), (-70, 45), (-66, 44), (-70, 42),
     (-74, 39), (-76, 35), (-80, 32), (-81, 26), (-84, 30), (-89, 30),
     (-94, 29), (-97, 26), (-97, 22), (-94, 18), (-90, 15), (-86, 13),
     (-83, 9), (-79, 9), (-81, 13), (-84, 16), (-88, 21), (-90, 21),
     (-91, 19), (-97, 16), (-102, 18), (-105, 20), (-108, 23), (-110, 24),
     (-114, 29), (-117, 33), (-122, 37), (-124, 46), (-128, 52),
     (-133, 57), (-150, 60), (-158, 58), (-162, 61), (-168, 66)],
    # Greenland
    [(-58, 64), (-52, 60), (-44, 60), (-40, 63), (-32, 68), (-22, 70),
     (-20, 76), (-28, 80), (-45, 80), (-58, 76), (-58, 64)],
    # South America
    [(-79, 9), (-72, 12), (-64, 10), (-55, 6), (-50, 0), (-44, -3),
     (-35, -8), (-39, -13), (-40, -21), (-48, -26), (-52, -33), (-58, -39),
     (-62, -41), (-65, -45), (-67, -50), (-68, -54), (-71, -54), (-74, -50),
     (-74, -44), (-73, -37), (-71, -30), (-70, -20), (-70, -18), (-75, -15),
     (-77, -12), (-79, -8), (-81, -4), (-80, 1), (-77, 4), (-79, 9)],
    # Europe
    [(-9, 43), (-2, 44), (-1, 46), (-4, 48), (0, 49), (2, 51), (5, 53),
     (8, 55), (8, 57), (10, 59), (5, 59), (5, 61), (10, 63), (14, 66),
     (18, 69), (25, 71), (31, 70), (40, 68), (45, 68), (50, 69), (55, 68),
     (60, 69), (66, 69), (60, 65), (55, 60), (50, 55), (48, 50), (45, 47),
     (40, 45), (38, 47), (35, 45), (32, 46), (28, 45), (24, 45), (23, 40),
     (22, 37), (19, 40), (15, 40), (16, 38), (12, 44), (8, 44), (3, 43),
     (3, 42), (0, 39), (-2, 37), (-6, 36), (-9, 37), (-9, 43)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 55), (-3, 57), (-5, 58), (-7, 58), (-8, 55),
     (-6, 52), (-5, 50)],
    # Africa
    [(-6, 35), (0, 36), (10, 37), (11, 34), (20, 32), (25, 32), (30, 31),
     (32, 31), (34, 28), (35, 24), (37, 22), (39, 20), (40, 15), (43, 12),
     (48, 11), (51, 12), (50, 15), (48, 11), (46, 5), (42, 0), (40, -5),
     (40, -10), (39, -15), (36, -20), (35, -24), (33, -27), (28, -33),
     (20, -35), (18, -32), (16, -28), (14, -22), (12, -18), (13, -12),
     (12, -6), (9, -1), (9, 4), (4, 6), (-2, 5), (-7, 4), (-13, 8),
     (-17, 12), (-17, 15), (-16, 20), (-15, 25), (-13, 28), (-10, 31),
     (-6, 35)],
    # Asia (incl. Arabia, India, SE Asia)
    [(40, 45), (45, 47), (48, 50), (50, 55), (55, 60), (60, 65), (66, 69),
     (75, 72), (85, 73), (95, 76), (105, 77), (115, 73), (125, 72),
     (135, 71), (145, 72), (155, 70), (165, 69), (175, 67), (178, 65),
     (170, 60), (162, 58), (158, 52), (156, 50), (150, 45), (142, 42),
     (141, 40), (140, 35), (137, 34), (133, 34), (129, 33), (126, 34),
     (122, 31), (120, 27), (118, 25), (114, 22), (110, 20), (108, 15),
     (109, 12), (106, 9), (104, 8), (103, 5), (100, 6), (98, 10), (97, 15),
     (94, 17), (92, 16), (91, 22), (88, 22), (86, 20), (84, 19), (80, 15),
     (80, 13), (77, 8), (76, 10), (73, 16), (72, 20), (70, 22), (68, 23),
     (66, 25), (62, 25), (58, 23), (56, 26), (52, 25), (50, 24), (48, 28),
     (47, 30), (50, 26), (55, 24), (58, 23), (59, 22), (57, 19), (55, 17),
     (52, 15), (48, 14), (45, 12), (43, 12), (42, 15), (39, 20), (37, 24),
     (35, 29), (36, 36), (36, 40), (40, 41), (40, 45)],
    # Indonesia / Papua (simplified)
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -9),
     (125, -9), (130, -3), (136, -2), (141, -3), (146, -6), (150, -9),
     (147, -8), (142, -8), (137, -7), (132, -4), (128, -3), (124, 0),
     (120, 1), (117, 3), (113, 4), (110, 2), (105, -2), (100, 2),
     (97, 5), (95, 5)],
    # Japan (simplified)
    [(130, 31), (133, 34), (137, 35), (140, 36), (141, 40), (141, 43),
     (143, 43), (145, 44), (143, 42), (142, 40), (140, 38), (138, 35),
     (135, 34), (132, 33), (130, 31)],
    # Australia
    [(113, -22), (114, -28), (115, -34), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (137, -35), (139, -37), (141, -38), (145, -38),
     (147, -38), (150, -37), (151, -34), (153, -30), (153, -27), (151, -24),
     (150, -22), (149, -20), (146, -19), (145, -15), (142, -11), (142, -14),
     (141, -17), (140, -18), (139, -17), (136, -15), (135, -12), (132, -11),
     (130, -12), (126, -14), (122, -17), (118, -20), (114, -22), (113, -22)],
    # New Zealand (simplified)
    [(167, -45), (171, -42), (174, -39), (176, -38), (178, -37), (176, -36),
     (174, -37), (172, -40), (169, -43), (167, -45)],
]


def draw_pin_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 236, 244), outline=INK, width=1)
    lon0, lon1, lat1, lat0 = -170, 190, 82, -58

    def proj(lon, lat):
        px = x + (lon - lon0) / (lon1 - lon0) * w
        py = y + (lat1 - lat) / (lat1 - lat0) * h
        return px, py

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=(196, 214, 176), outline=(120, 140, 100))
    for glon in range(-150, 181, 30):
        gx, _ = proj(glon, 0)
        d.line([gx, y + 2, gx, y + h - 2], fill=(206, 222, 236), width=1)
    for glat in range(-60, 81, 30):
        _, gy2 = proj(0, glat)
        d.line([x + 2, gy2, x + w - 2, gy2], fill=(206, 222, 236), width=1)
    for i, card in enumerate(CARDS):
        lon, lat = card[9]
        px, py = proj(lon, lat)
        r = 7
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED, outline=(255, 255, 255), width=1)
        d.text((px, py - 5), str(i + 1), font=sans_bold(8),
               fill=(255, 255, 255), anchor="ma")
    d.text((x + 6, y + 4), "WHERE IT HAPPENED — PINS 1–13",
           font=sans_bold(9), fill=NAVY, anchor="la")


def draw_card(d, x, y, w, h, num, card, lead=False):
    region, field, place, headline, detail, keyfig, conf, sources, scene, _ll = card
    colour = REGION_COLOUR[region]
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    # Number badge.
    d.rectangle([x, y, x + 22, y + 18], fill=colour)
    d.text((x + 11, y + 2), str(num), font=sans_bold(11),
           fill=(255, 255, 255), anchor="ma")
    # Key-figure chip (top right) — measured first so the tag can fit beside it.
    kf = sans_bold(10 if lead else 9)
    kw = int(d.textlength(keyfig, font=kf)) + 12
    d.rectangle([x + w - kw - 4, y + 3, x + w - 4, y + 19], fill=INK)
    d.text((x + w - kw // 2 - 4, y + 5), keyfig, font=kf,
           fill=(255, 255, 255), anchor="ma")
    # Tag line (drop the place if the full tag cannot fit beside the chip).
    tag_max = w - 27 - kw - 10
    tag = f"{REGION_SHORT[region]} · {field} · {place}"
    if d.textlength(tag, font=sans_bold(7)) > tag_max:
        tag = f"{REGION_SHORT[region]} · {field}"
    tag_f = fit_font(d, tag, sans_bold, tag_max, 10 if lead else 8)
    d.text((x + 27, y + 3), tag, font=tag_f, fill=colour, anchor="la")
    if lead:
        scene_w = 300
        SCENES[scene](d, x + w - scene_w - 6, y + 26, scene_w, h - 52)
        tx = x + 8
        tw = w - scene_w - 22
        d.text((tx, y + 22), headline, font=fit_font(d, headline, serif, tw, 30),
               fill=INK, anchor="la")
        yy = y + 58
        for line in wrap(d, detail, sans(13), tw)[:2]:
            d.text((tx, yy), line, font=sans(13), fill=INK, anchor="la")
            yy += 15
    else:
        scene_h = 40
        SCENES[scene](d, x + 4, y + 22, w - 8, scene_h)
        tx = x + 6
        tw = w - 12
        yy = y + 22 + scene_h + 3
        hf = fit_font(d, headline, serif, tw, 13)
        lines = wrap(d, headline, hf, tw)[:2]
        for line in lines:
            d.text((tx, yy), line, font=hf, fill=INK, anchor="la")
            yy += 14
        for line in wrap(d, detail, sans(9), tw)[:2]:
            d.text((tx, yy), line, font=sans(9), fill=GREY, anchor="la")
            yy += 11
    # Footer: confidence + sources.
    fy = y + h - 15
    d.rectangle([x + 5, fy, x + 5 + 8 + int(d.textlength(conf, font=sans_bold(8))),
                 fy + 12], fill=CONF_COLOUR[conf])
    d.text((x + 9, fy + 1), conf, font=sans_bold(8), fill=(255, 255, 255), anchor="la")
    src_x = x + 5 + 8 + int(d.textlength(conf, font=sans_bold(8))) + 5
    d.text((src_x, fy + 1), sources, font=sans(8), fill=GREY, anchor="la")


def draw_page():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    total = len(CARDS) + len(BRIEFS)
    fields = {c[1] for c in CARDS} | {b[1] for b in BRIEFS}
    counts = {}
    for c in CARDS:
        counts[c[0]] = counts.get(c[0], 0) + 1
    for b in BRIEFS:
        counts[b[0]] = counts.get(b[0], 0) + 1

    # Masthead.
    hline(d, 8, 5)
    hline(d, 15, 2)
    d.text((W / 2, 17), "THE WORLD — IN ONE IMAGE", font=serif(34), fill=INK, anchor="ma")
    d.text((MARGIN, 59), DATE_LINE, font=sans_bold(13), fill=INK, anchor="la")
    d.text((W - MARGIN, 59), "ONE PAGE · EVERY STORY DATED", font=sans(11),
           fill=GREY, anchor="ra")
    hline(d, 79, 3)

    # Spec strip.
    spec = (f"{total} STORIES • {len(REGIONS)} REGIONS • {len(fields)} FIELDS • "
            f"EVERY ONE FROM TUESDAY 24 NOVEMBER 2026 (UTC)")
    d.rectangle([MARGIN, 85, W - MARGIN, 107], fill=INK)
    d.text((W / 2, 89), spec, font=fit_font(d, spec, sans_bold, W - 2 * MARGIN - 16, 15),
           fill=(255, 255, 255), anchor="ma")

    # Region chips with counts.
    cy = 113
    cx = MARGIN
    for name, colour in REGIONS:
        label = f"{name} {counts.get(name, 0)}"
        cw = int(d.textlength(label, font=sans_bold(10))) + 18
        d.rectangle([cx, cy, cx + cw, cy + 18], fill=colour)
        d.text((cx + cw // 2, cy + 3), label, font=sans_bold(10),
               fill=(255, 255, 255), anchor="ma")
        cx += cw + 6

    # UTC timeline strip.
    ty = 134
    d.text((MARGIN, ty), "THE DAY IN UTC", font=sans_bold(11), fill=RED, anchor="la")
    axis_y = ty + 40
    ax0, ax1 = MARGIN + 6, W - MARGIN - 6
    d.line([ax0, axis_y, ax1, axis_y], fill=INK, width=2)
    for hh in range(0, 25, 3):
        px = ax0 + (ax1 - ax0) * hh / 24
        d.line([px, axis_y - 4, px, axis_y + 4], fill=INK, width=1)
        d.text((px, axis_y + 6), f"{hh:02d}:00", font=sans(8), fill=GREY, anchor="ma")
    for hhmm, label, side, nudge in TIMELINE:
        hh, mm = int(hhmm[:2]), int(hhmm[3:])
        px = ax0 + (ax1 - ax0) * (hh + mm / 60) / 24
        d.ellipse([px - 4, axis_y - 4, px + 4, axis_y + 4], fill=RED)
        above = side == "above"
        ly = axis_y - 26 if above else axis_y + 18
        d.line([px, axis_y, px + nudge, ly + (10 if above else 0)], fill=RED, width=1)
        d.text((px + nudge, ly), f"{hhmm} {label}", font=sans_bold(8), fill=INK, anchor="ma")

    # Day in numbers strip.
    ny = 206
    d.text((MARGIN, ny), "THE DAY IN NUMBERS", font=sans_bold(11), fill=RED, anchor="la")
    cell_w = (W - 2 * MARGIN) // len(NUMBERS)
    for i, (big, cap) in enumerate(NUMBERS):
        cxp = MARGIN + i * cell_w
        d.text((cxp + cell_w // 2, ny + 12), big, font=serif(20), fill=INK, anchor="ma")
        d.text((cxp + cell_w // 2, ny + 36), cap, font=sans(9), fill=GREY, anchor="ma")
        if i:
            d.line([cxp, ny + 14, cxp, ny + 46], fill=LIGHT, width=1)
    hline(d, ny + 50, 2)

    # Lead card (full width) + 12 cards in 4 cols x 3 rows.
    gy = ny + 58
    lead_h = 104
    draw_card(d, MARGIN, gy, W - 2 * MARGIN, lead_h, 1, CARDS[0], lead=True)
    gy += lead_h + 7
    cols, rows = 4, 3
    gap = 7
    card_w = (W - 2 * MARGIN - (cols - 1) * gap) // cols
    card_h = 120
    for i, card in enumerate(CARDS[1:]):
        col, row = i % cols, i // cols
        draw_card(d, MARGIN + col * (card_w + gap), gy + row * (card_h + gap),
                  card_w, card_h, i + 2, card)
    gy += rows * (card_h + gap)

    # Bottom block: briefs (left, 3 cols) + pin map (right).
    by = gy + 2
    map_w = 372
    brief_w = W - 2 * MARGIN - map_w - 12
    d.text((MARGIN, by), "ALSO TODAY — ONE-LINE BRIEFS", font=sans_bold(11),
           fill=RED, anchor="la")
    bcols = 3
    bcol_w = (brief_w - 2 * 8) // bcols
    brow_h = 18
    brows = (len(BRIEFS) + bcols - 1) // bcols
    for i, (region, field, text, source) in enumerate(BRIEFS):
        col, row = i % bcols, i // bcols
        bx = MARGIN + col * (bcol_w + 8)
        yy = by + 16 + row * brow_h
        colour = REGION_COLOUR[region]
        d.rectangle([bx, yy + 1, bx + 16, yy + 13], fill=colour)
        d.text((bx + 8, yy + 2), str(i + 14), font=sans_bold(8),
               fill=(255, 255, 255), anchor="ma")
        lines = wrap(d, f"{text} ({source})", sans(8), bcol_w - 21)[:2]
        for j, line in enumerate(lines):
            d.text((bx + 19, yy + j * 8), line, font=sans(8), fill=INK, anchor="la")
    draw_pin_map(d, MARGIN + brief_w + 12, by, map_w, 16 + brows * brow_h - 4)

    # Date-check strip + methodology footer.
    fy = by + 16 + brows * brow_h + 6
    d.rectangle([MARGIN, fy, W - MARGIN, fy + 28], fill=(240, 234, 220), outline=INK, width=1)
    yy = fy + 4
    for line in wrap(d, DATE_CHECK, sans_bold(9), W - 2 * MARGIN - 12)[:2]:
        d.text((MARGIN + 6, yy), line, font=sans_bold(9), fill=INK, anchor="la")
        yy += 11
    hline(d, fy + 34, 2)
    yy = fy + 40
    for line in wrap(d, METHOD, sans(9), W - 2 * MARGIN)[:2]:
        d.text((MARGIN, yy), line, font=sans(9), fill=GREY, anchor="la")
        yy += 11
    return img


def add_grain(img, amp=4, density=0.045, seed=20261124):
    """Deterministic newsprint grain: seeded sparse luminance speckle."""
    rng = random.Random(seed)
    px = img.load()
    for yy in range(H):
        for xx in range(W):
            if rng.random() < density:
                n = rng.randint(-amp, amp)
                r, g, b = px[xx, yy]
                px[xx, yy] = (max(0, min(255, r + n)),
                              max(0, min(255, g + n)),
                              max(0, min(255, b + n)))
    return img


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("entry.png")
    img = add_grain(draw_page())
    img.save(out, format="PNG")
    data = out.read_bytes()
    print(f"WROTE {out} {len(data)} bytes sha256={hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
