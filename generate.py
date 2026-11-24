#!/usr/bin/env python3
"""Generate the 24 November 2026 front page: THE WORLD — IN ONE IMAGE.

Deterministic: fixed headlines, fixed fonts, fixed layout, no timestamps
and no randomness. Running it twice produces a byte-identical entry.png.
"""
import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (20, 20, 20)
RED = (163, 22, 33)
GREY = (96, 92, 84)
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

LEAD = {
    "kicker": "TECHNOLOGY  ·  MARKETS",
    "headline": "HUANG IS BACK AT NVIDIA",
    "deck": "Trump intervenes to reinstate the ousted chief executive; shares surge 31% as Washington splits over chip-smuggling claims.",
}

STORIES = [
    ("CLIMATE  ·  ANTALYA",
     "COP31 TALKS FALTER",
     "Climate talks in Türkiye stall as nations split over fossil fuels and aid."),
    ("IRAN  ·  WASHINGTON",
     "TRUMP WARNS IRAN OF 'VERY TRAUMATIC' OUTCOME",
     "Trump warns Tehran as a second carrier is weighed; US sanctions follow."),
    ("UKRAINE",
     "ZELENSKY SEEKS FOUR-WAY PEACE TALKS",
     "Kyiv urges talks with Russia, Europe and the US 'as soon as possible'."),
    ("GAZA",
     "ISRAELI STRIKE KILLS THREE IN GAZA",
     "A drone strike hits a Gaza police post; a US lawmaker decries the West Bank."),
    ("INDONESIA",
     "24 KILLED IN INDONESIA FACTORY FIRE",
     "A blaze rips through a candy factory; rescue teams search for the missing."),
    ("SOUTH KOREA",
     "SEOUL ON ALERT AS RUSSIAN JETS APPROACH",
     "Island residents take shelter and fighters scramble as Russian jets approach."),
]

FOOTER = "Compiled 24 November 2026  ·  Sources: NYT · The Guardian · France 24 · Al Jazeera · BBC"


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

def hline(draw, y, weight=2, fill=INK, x0=48, x1=None):
    draw.rectangle([x0, y, (x1 or W - 48), y + weight - 1], fill=fill)


def centered(draw, y, text, fnt, fill=INK):
    draw.text((W / 2, y), text, font=fnt, fill=fill, anchor="ma")


def draw_page():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead.
    hline(d, 24, 6)
    hline(d, 34, 2)
    d.text((W / 2, 48), "THE WORLD", font=serif(88), fill=INK, anchor="ma")
    centered(d, 140, "— IN ONE IMAGE —", sans_bold(24), INK)
    d.text((48, 176), DATE_LINE, font=sans_bold(20), fill=INK, anchor="la")
    d.text((W - 48, 176), "ONE DAY · ONE PAGE", font=sans(20), fill=GREY, anchor="ra")
    hline(d, 208, 4)

    # Lead story.
    d.text((48, 226), LEAD["kicker"], font=sans_bold(22), fill=RED, anchor="la")
    y = 256
    for line in wrap(d, LEAD["headline"], serif(58), W - 96):
        d.text((48, y), line, font=serif(58), fill=INK, anchor="la")
        y += 66
    y += 6
    for line in wrap(d, LEAD["deck"], sans(23), W - 96):
        d.text((48, y), line, font=sans(23), fill=INK, anchor="la")
        y += 30
    hline(d, y + 22, 2)
    grid_top = y + 44

    # Story grid: 2 columns x 3 rows, dividers between them.
    col_w = (W - 96 - 32) // 2
    row_h = (950 - grid_top) // 3
    for i, (kicker, headline, summary) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x = 48 + col * (col_w + 32)
        y = grid_top + row * row_h
        d.rectangle([x, y + 5, x + 9, y + 14], fill=RED)
        d.text((x + 18, y), kicker, font=sans_bold(17), fill=RED, anchor="la")
        y += 30
        for line in wrap(d, headline, serif(25), col_w):
            d.text((x, y), line, font=serif(25), fill=INK, anchor="la")
            y += 31
        y += 4
        for line in wrap(d, summary, sans(18), col_w):
            d.text((x, y), line, font=sans(18), fill=GREY, anchor="la")
            y += 23
    d.line([W // 2, grid_top, W // 2, 950], fill=LIGHT, width=1)
    hline(d, grid_top + row_h - 2, 1, LIGHT)
    hline(d, grid_top + 2 * row_h - 2, 1, LIGHT)

    # Footer.
    hline(d, 962, 2)
    centered(d, 974, FOOTER, sans(16), GREY)
    return img


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("entry.png")
    img = draw_page()
    img.save(out, format="PNG")
    data = out.read_bytes()
    print(f"WROTE {out} {len(data)} bytes sha256={hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
