#!/usr/bin/env python3
"""The index's link preview (Open Graph, og.png, 1200 x 630), in the page's look: the Joakim Skurk logo on its
pixel splatter, the sections and the projects' logos. index.html names it (og:image). The projects' logos are
fetched from the repositories (curl).

  python3 tools/make_og.py [OUT.png]

Fonts: Space Grotesk and IBM Plex Mono (SIL Open Font License), in tools/fonts."""
import io
import os
import random
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "tools" / "fonts"
W, H = 1200, 630
BG, LINE, FG, DIM = (5, 4, 7), (44, 35, 66), (255, 248, 224), (207, 195, 234)
YELLOW, PURPLE, GREEN, CYAN = (255, 214, 10), (200, 107, 255), (69, 255, 58), (46, 230, 255)
RAW = "https://raw.githubusercontent.com/joakimskurk"
LOGOS = [f"{RAW}/fm1vavehero/HEAD/assets/vavehero-logo.png",
         f"{RAW}/fm1stardistroyer/HEAD/docs/readme/banner.png",
         f"{RAW}/fm1roboseq/HEAD/assets/roboseq-logo.png",
         f"{RAW}/fm1mello/HEAD/docs/logo.png",
         f"{RAW}/fm1clock/HEAD/docs/screens/sign.png"]
SECTIONS = [("AUDIO", GREEN), ("GAMES", PURPLE), ("TOOLS", CYAN), ("FIRMWARE", YELLOW)]


def grotesk(size, weight="Bold"):
    f = ImageFont.truetype(str(FONTS / "SpaceGrotesk.ttf"), size)
    f.set_variation_by_name(weight)
    return f


def mono(size):
    return ImageFont.truetype(str(FONTS / "PlexMono.ttf"), size)


def fetch(url):
    data = subprocess.run(["curl", "-sfL", url], check=True, capture_output=True).stdout
    return Image.open(io.BytesIO(data)).convert("RGBA")


def main(out):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img, "RGBA")
    for x in range(0, W, 24):                         # the grid
        d.line((x, 0, x, H), fill=(14, 11, 20))
    for y in range(0, H, 24):
        d.line((0, y, W, y), fill=(14, 11, 20))

    # the pixel splatter behind the logo, as on the page
    rnd, P = random.Random(7), 10
    cx, cy, rx, ry = 300, 250, 300, 210
    cols = [PURPLE, (155, 79, 214), GREEN, (47, 194, 42), CYAN, (224, 160, 255)]
    for y in range(0, H, P):
        for x in range(0, 640, P):
            dist = (((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2) ** .5 + (rnd.random() - .5) * .5
            if dist < 1 and rnd.random() > dist * .85:
                a = round(((1 - dist) * .45 * rnd.random() + .04) * 255)
                d.rectangle((x, y, x + P - 1, y + P - 1), fill=rnd.choice(cols) + (a,))

    # the logo, its edges faded into the dark
    logo = Image.open(ROOT / "assets" / "skurk-logo.webp").convert("RGBA")
    lw = 560
    logo = logo.resize((lw, round(logo.size[1] * lw / logo.size[0])), Image.LANCZOS)
    mask = Image.new("L", logo.size, 0)
    md = ImageDraw.Draw(mask)
    for k in range(40):                               # a soft oval: brighter towards the middle
        t = k / 40
        md.ellipse((t * lw * .28, t * logo.size[1] * .28, lw - t * lw * .28, logo.size[1] - t * logo.size[1] * .28),
                   fill=round(min(1, t * 2.2) * 255))
    logo.putalpha(mask)
    logo = logo.rotate(3, resample=Image.BICUBIC, expand=True)
    img.paste(logo, (cx - logo.size[0] // 2, cy - logo.size[1] // 2), logo)
    d = ImageDraw.Draw(img, "RGBA")

    # the words, on the right
    tx = 650
    d.text((tx, 120), "Instruments,", font=grotesk(54), fill=FG)
    d.text((tx, 180), "games & tools", font=grotesk(54), fill=FG)
    d.text((tx, 262), "Designs and ideas by Joakim's Skurk", font=mono(20), fill=DIM)
    d.text((tx, 290), "of JHF Audio", font=mono(20), fill=DIM)
    x = tx
    for name, col in SECTIONS:                        # the sections, as chips
        f = mono(16)
        w = d.textlength(name, font=f) + 28
        d.rectangle((x + 3, 343, x + w + 3, 377), fill=(0, 0, 0))
        d.rectangle((x, 340, x + w, 374), fill=(17, 13, 26), outline=col, width=2)
        d.text((x + w / 2, 357), name, font=f, fill=col, anchor="mm")
        x += w + 12

    # the projects' logos along the bottom
    m, gap, ty, th = 56, 14, 468, 106
    n = len(LOGOS)
    tw = (W - 2 * m - gap * (n - 1)) // n
    for i, url in enumerate(LOGOS):
        x0 = m + i * (tw + gap)
        d.rectangle((x0 + 3, ty + 3, x0 + tw + 3, ty + th + 3), fill=(120, 100, 6))
        d.rectangle((x0, ty, x0 + tw, ty + th), fill=(0, 0, 0), outline=LINE)
        d.line((x0, ty, x0 + 16, ty), fill=YELLOW, width=3)
        d.line((x0, ty, x0, ty + 16), fill=YELLOW, width=3)
        pic = fetch(url)
        s = min((tw - 24) / pic.size[0], (th - 24) / pic.size[1])
        pic = pic.resize((round(pic.size[0] * s), round(pic.size[1] * s)), Image.LANCZOS)
        img.paste(pic, (x0 + (tw - pic.size[0]) // 2, ty + (th - pic.size[1]) // 2), pic)
    img.save(out, optimize=True)
    print(f"og: {out} ({W} x {H}, {os.path.getsize(out)} B)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT / "og.png")
