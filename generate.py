#!/usr/bin/env python3
"""Generate the 24 November 2026 front page: THE WORLD — IN ONE IMAGE (v2).

Dense broadsheet: a lead story, a markets strip with a mini bar chart,
and 33 short stories in three columns with region colour chips, plus a
small seismograph trace on the earthquake story. Deterministic: fixed
headlines, fixed fonts, fixed layout, no timestamps and no randomness.
Running it twice produces a byte-identical entry.png.
"""
import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
PAPER = (247, 242, 231)
INK = (20, 20, 20)
RED = (163, 22, 33)
NAVY = (30, 58, 95)
GREEN = (27, 94, 52)
AMBER = (166, 84, 0)
TEAL = (0, 105, 105)
PURPLE = (94, 48, 128)
DARKGREY = (70, 70, 70)
GREY = (78, 74, 66)
LIGHT = (178, 172, 160)

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
COUNT_LINE = "34 STORIES · ONE PAGE"

LEAD = {
    "kicker": "TECHNOLOGY  ·  MARKETS",
    "headline": "HUANG IS BACK AT NVIDIA",
    "deck": (
        "The board reinstates Jensen Huang as chief executive after "
        "Washington backs his return; shares leapt 31% on Monday, then "
        "slipped about 6% on Tuesday as he apologised to staff and "
        "refused to name a successor."
    ),
}

# Markets strip: (label, change %) — Monday 23 Nov close, reported Tuesday.
MARKETS = [
    ("S&P 500", 4.73),
    ("NASDAQ", 6.51),
    ("NIKKEI", 3.91),
    ("DAX", 2.15),
    ("FTSE 100", 1.30),
    ("HANG SENG", -0.62),
]
MARKETS_EXTRA = "BRENT $86.7  −2.99%    ·    GOLD +3.9%    ·    NAT GAS +12.0%"

# (kicker, headline, summary, chip colour)
STORIES = [
    ("CLIMATE  ·  ANTALYA",
     "COP31 ENDS IN COLLAPSE",
     "No deal for first time since 2009; ~130 nations reject text silent on fossil fuels.",
     GREEN),
    ("MIDDLE EAST  ·  RIYADH",
     "HOUTHI DRONE HITS RIYADH",
     "Drone attack on PIF Tower injures 11 in financial district.",
     RED),
    ("GAZA",
     "ISRAELI STRIKES KILL NINE",
     "Strikes kill Hamas security chief Naeem Abu Nahel.",
     RED),
    ("IRAN  ·  HORMUZ",
     "TANKERS HIT MINES IN HORMUZ",
     "IRGC: three oil tankers catch fire after hitting naval mines.",
     RED),
    ("IRAN  ·  WASHINGTON",
     "TEHRAN SETS SEVEN CONDITIONS",
     "Iran refuses talks until seven conditions are met.",
     NAVY),
    ("ISRAEL  ·  IRAN",
     "KATZ: IRAN MAKING CHEMICAL ARMS",
     "'Game-changer': IDF and CENTCOM prepare strike options.",
     RED),
    ("UKRAINE  ·  RUSSIA",
     "PUTIN ADMITS OIL STRIKES BITE",
     "Ukraine strikes cut refining ~30%; fuel export limits imposed.",
     RED),
    ("RUSSIA",
     "LEAKED DATA: VAST WAR TOLL",
     "Hacked Rosstat data points to hundreds of thousands dead.",
     RED),
    ("LIBYA",
     "UKRAINE HITS SHIPS OFF BENGHAZI",
     "Two Libyan soldiers die; Tripoli demands answers from Kyiv.",
     RED),
    ("BRITAIN",
     "MI5 WARNS OF RUSSIAN SABOTAGE",
     "Firms supplying Ukraine told to 'act now' against sabotage.",
     NAVY),
    ("JUSTICE  ·  NEW YORK",
     "HUAWEI CONVICTED OF BANK FRAUD",
     "Trade-secret theft too; acquitted of racketeering.",
     DARKGREY),
    ("TECHNOLOGY",
     "MICROSOFT DECLARES 'CODE RED'",
     "After historic 24-hour outage, vows one-hour recovery.",
     AMBER),
    ("SPACE  ·  CHINA",
     "FIRST GUEST ASTRONAUT ON TIANGONG",
     "Pakistan's Zeeshan Ali to fly on Shenzhou-24.",
     TEAL),
    ("MYANMAR",
     "14 NATIONS BACK ICJ RULING",
     "UK, Spain, Canada, Australia among 14 recognising ruling.",
     NAVY),
    ("MALAYSIA",
     "MALAYSIA TO RETURN 6,500 ROHINGYA",
     "Kuala Lumpur to send thousands of refugees back.",
     NAVY),
    ("UNITED NATIONS",
     "GUTERRES: AI RULES WITHIN A YEAR",
     "UN chief urges AI-risk framework within a year.",
     AMBER),
    ("HEALTH  ·  UNITED STATES",
     "MEASLES DEATHS RISE TO 14",
     "Pennsylvania reports ninth death; US cases near 6,000.",
     TEAL),
    ("NEPAL",
     "M5.6 QUAKE ON NEPAL BORDER",
     "Tremor strikes Koshi province near Chinese border.",
     GREEN),
    ("INDIAN OCEAN",
     "M6.4 QUAKE OFF RODRIGUES",
     "Tsunami watch issued, then lifted; no damage.",
     GREEN),
    ("INDONESIA",
     "FACTORY FIRE TOLL RISES TO 26",
     "Serang candy-plant blaze: 28 missing; negligence probe.",
     GREEN),
    ("COLOMBIA",
     "CAR BOMB ROCKS VILLAVICENCIO",
     "Blast destroys buildings; Cartagena hostages freed.",
     RED),
    ("MEXICO",
     "MEXICO TO TRY 'EL CHAPO ISIDRO'",
     "Cartel figure to face trial despite US extradition bid.",
     DARKGREY),
    ("VENEZUELA",
     "VENEZUELA OWES $237.5 BILLION",
     "Debt figure published ahead of vast restructuring.",
     AMBER),
    ("NIGERIA",
     "BORNO SCHOOL ENROLMENT DOUBLES",
     "Pupils return in north-east despite conflict, poverty.",
     NAVY),
    ("EUROPE  ·  ECB",
     "DE COS TIPPED FOR ECB TOP JOB",
     "Pablo Hernández de Cos favourite for ECB presidency.",
     NAVY),
    ("BRITAIN",
     "BENEFIT SHAKE-UP THREATENS MANY",
     "Hundreds of thousands could lose disability benefits.",
     NAVY),
    ("UNITED STATES",
     "DOJ RECOVERS $8BN FROM SCAMS",
     "800+ charged in largest US anti-scam surge.",
     DARKGREY),
    ("BUSINESS",
     "SANOFI TO BUY INSMED FOR $41BN",
     "French drugmaker pays $175 a share in cash.",
     AMBER),
    ("TRADE",
     "US PLANS TARIFFS ON 16 NATIONS",
     "New duties eyed on China, EU and Japan.",
     AMBER),
    ("SPORT  ·  TENNIS",
     "ALCARAZ WINS ATP FINALS AT LAST",
     "Beats Zverev 6–2 7–6 in Turin; 14 straight wins.",
     PURPLE),
    ("SPORT  ·  NBA",
     "WARRIORS EDGE CELTICS 88–87",
     "Golden State survives final possession; Rockets win too.",
     PURPLE),
    ("SPORT  ·  FOOTBALL",
     "CAS TO RULE ON AFCON FINAL ROW",
     "Senegal challenge award of 3–0 win to Morocco.",
     PURPLE),
    ("BANGLADESH",
     "EXILED EX-PM SETS RETURN DATE",
     "Ousted leader, sentenced to death, vows 16 Dec return.",
     NAVY),
]

FOOTER = (
    "Compiled 24 November 2026  ·  Sources: Reuters · BBC · Al Jazeera · "
    "ISW · The Guardian · Straits Times · CNA · Investopedia"
)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns the lines of text that fit max_w."""
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


def centered(draw, y, text, fnt, fill=INK):
    draw.text((W / 2, y), text, font=fnt, fill=fill, anchor="ma")


def draw_globe(draw, cx, cy, r):
    """Tiny globe: circle, equator, two meridian ellipses."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=2)
    draw.line([cx - r, cy, cx + r, cy], fill=INK, width=1)
    draw.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=INK, width=1)
    draw.line([cx, cy - r, cx, cy + r], fill=INK, width=1)


def draw_seismograph(draw, x, y, w):
    """Flat trace, sharp spike, flat trace — a quake on paper."""
    pts = [
        (x, y), (x + w * 0.30, y), (x + w * 0.38, y - 7),
        (x + w * 0.46, y + 6), (x + w * 0.54, y - 4),
        (x + w * 0.62, y), (x + w, y),
    ]
    draw.line(pts, fill=RED, width=2)


def draw_markets(draw, top):
    """Boxed markets strip with a mini bar chart of index moves."""
    box_h = 46
    draw.rectangle([MARGIN, top, W - MARGIN, top + box_h], outline=INK, width=2)
    draw.text((MARGIN + 10, top + 5), "MARKETS · MON CLOSE",
              font=sans_bold(11), fill=RED, anchor="la")
    # Mini bars: one per index, scaled so 6.51% is the tallest.
    base = top + box_h - 8
    x = MARGIN + 10
    max_h = 20
    peak = max(abs(v) for _, v in MARKETS)
    for label, pct in MARKETS:
        h = max(2, round(max_h * abs(pct) / peak))
        colour = GREEN if pct >= 0 else RED
        draw.rectangle([x, base - h, x + 10, base], fill=colour)
        draw.text((x + 16, base - 11), f"{label} {pct:+.2f}%",
                  font=sans_bold(10), fill=INK, anchor="la")
        x += 16 + int(draw.textlength(f"{label} {pct:+.2f}%", font=sans_bold(10))) + 14
    draw.text((W - MARGIN - 10, top + 5), MARKETS_EXTRA,
              font=sans(10), fill=GREY, anchor="ra")
    return top + box_h


def draw_page():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead.
    hline(d, 14, 6)
    hline(d, 23, 2)
    draw_globe(d, MARGIN + 22, 60, 19)
    draw_globe(d, W - MARGIN - 22, 60, 19)
    d.text((W / 2, 27), "THE WORLD", font=serif(52), fill=INK, anchor="ma")
    centered(d, 84, "— IN ONE IMAGE —", sans_bold(15), INK)
    d.text((MARGIN, 106), DATE_LINE, font=sans_bold(14), fill=INK, anchor="la")
    d.text((W - MARGIN, 106), COUNT_LINE, font=sans(12), fill=GREY, anchor="ra")
    hline(d, 128, 3)

    # Lead story.
    d.text((MARGIN, 137), LEAD["kicker"], font=sans_bold(12), fill=RED, anchor="la")
    d.text((MARGIN, 154), LEAD["headline"], font=serif(42), fill=INK, anchor="la")
    y = 204
    for line in wrap(d, LEAD["deck"], sans(14), W - 2 * MARGIN):
        d.text((MARGIN, y), line, font=sans(14), fill=INK, anchor="la")
        y += 18
    hline(d, y + 5, 2)

    # Markets strip.
    grid_top = draw_markets(d, y + 12) + 8

    # Story grid: 3 columns x 11 rows.
    cols, rows = 3, 11
    gutter = 24
    col_w = (W - 2 * MARGIN - (cols - 1) * gutter) // cols
    grid_bottom = 964
    row_h = (grid_bottom - grid_top) // rows
    kicker_f = sans_bold(10)
    head_f = serif(13)
    sum_f = sans(11)
    for i, (kicker, headline, summary, colour) in enumerate(STORIES):
        col, row = i % cols, i // cols
        x = MARGIN + col * (col_w + gutter)
        yy = grid_top + row * row_h
        d.rectangle([x, yy + 3, x + 7, yy + 10], fill=colour)
        d.text((x + 12, yy), kicker, font=kicker_f, fill=colour, anchor="la")
        yy += 12
        head_lines = wrap(d, headline, head_f, col_w)[:2]
        for line in head_lines:
            d.text((x, yy), line, font=head_f, fill=INK, anchor="la")
            yy += 15
        max_sum = 2 if len(head_lines) == 1 else 1
        for line in wrap(d, summary, sum_f, col_w)[:max_sum]:
            d.text((x, yy), line, font=sum_f, fill=GREY, anchor="la")
            yy += 13
        if "QUAKE OFF RODRIGUES" in headline:
            draw_seismograph(d, x + col_w - 70, yy + 2, 66)
    # Dividers.
    for c in range(1, cols):
        x = MARGIN + c * (col_w + gutter) - gutter // 2
        d.line([x, grid_top, x, grid_bottom], fill=LIGHT, width=1)
    for r in range(1, rows):
        yy = grid_top + r * row_h - 2
        hline(d, yy, 1, LIGHT)

    # Footer.
    hline(d, 972, 2)
    centered(d, 980, FOOTER, sans(12), GREY)
    return img


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("entry.png")
    img = draw_page()
    img.save(out, format="PNG")
    data = out.read_bytes()
    print(f"WROTE {out} {len(data)} bytes sha256={hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
