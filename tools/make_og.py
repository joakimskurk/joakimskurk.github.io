#!/usr/bin/env python3
"""The index's link preview (Open Graph, og.png, 1200 x 630), in jhf.no's look: the grid, the green, SKURK and the
projects' logos. index.html names it (og:image). The logos are fetched from the repositories.

  python3 tools/make_og.py [OUT.png]

Fonts: Space Grotesk and IBM Plex Mono (SIL Open Font License), in tools/fonts."""
import io
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "tools" / "fonts"
W, H = 1200, 630
BG, PANEL, LINE, FG, DIM, ACCENT = (10, 19, 17), (15, 29, 25), (33, 64, 47), (232, 255, 243), (162, 201, 181), (124, 255, 196)
RAW = "https://raw.githubusercontent.com/joakimskurk"
LOGOS = [  # (picture, the section's colour, as on the page)
    (f"{RAW}/fm1vavehero/HEAD/assets/vavehero-logo.png", (255, 184, 107)),
    (f"{RAW}/fm1stardistroyer/HEAD/docs/readme/banner.png", (124, 255, 196)),
    (f"{RAW}/fm1roboseq/HEAD/assets/roboseq-logo.png", (124, 255, 196)),
    (f"{RAW}/fm1mello/HEAD/docs/logo.png", (124, 255, 196)),
    (f"{RAW}/fm1clock/HEAD/docs/screens/sign.png", (107, 228, 255)),
]


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
    glow = Image.new("RGB", (W, H), BG)               # the page's green light from the top left
    ImageDraw.Draw(glow).ellipse((-300, -420, 700, 260), fill=(26, 58, 46))
    img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(160)), 1)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 32):                         # the grid
        d.line((x, 0, x, H), fill=(15, 27, 24))
    for y in range(0, H, 32):
        d.line((0, y, W, y), fill=(15, 27, 24))

    m = 64
    # the brand: SKRK in its box, SKURK.JHF
    d.rectangle((m, 56, m + 52, 108), outline=ACCENT, width=2)
    f = mono(17)
    d.text((m + 26, 82), "SKRK", font=f, fill=ACCENT, anchor="mm")
    d.text((m + 70, 82), "SKURK", font=grotesk(26), fill=FG, anchor="lm")
    x = m + 70 + d.textlength("SKURK", font=grotesk(26))
    d.text((x, 82), ".", font=grotesk(26), fill=ACCENT, anchor="lm")
    d.text((x + d.textlength(".", font=grotesk(26)), 82), "JHF", font=grotesk(26), fill=FG, anchor="lm")

    # the kicker, the title, the line under it
    y = 160
    d.polygon([(m + 6, y), (m + 12, y + 6), (m + 6, y + 12), (m, y + 6)], outline=ACCENT, width=2)
    d.text((m + 24, y + 6), "PROJECT INDEX", font=mono(18), fill=ACCENT, anchor="lm")
    big = grotesk(76)
    d.text((m, y + 34), "Skurk", font=big, fill=FG)
    x = m + d.textlength("Skurk", font=big)
    d.text((x, y + 34), ".", font=big, fill=ACCENT)
    d.text((x + d.textlength(". ", font=big), y + 34), "instruments, games", font=big, fill=FG)
    d.text((m, y + 120), "& tools", font=big, fill=FG)
    d.text((m, y + 222), "Designs and ideas by Joakim's Skurk of JHF Audio", font=mono(22), fill=DIM)

    # the logos, each in a card with its section's corner
    n, gap, ty = len(LOGOS), 14, 460
    tw = (W - 2 * m - gap * (n - 1)) // n
    th = 110
    for i, (url, col) in enumerate(LOGOS):
        x0 = m + i * (tw + gap)
        d.rectangle((x0, ty, x0 + tw, ty + th), fill=(6, 11, 10), outline=LINE)
        d.line((x0, ty, x0 + 18, ty), fill=col, width=3)
        d.line((x0, ty, x0, ty + 18), fill=col, width=3)
        pic = fetch(url)
        s = min((tw - 24) / pic.size[0], (th - 24) / pic.size[1])
        pic = pic.resize((round(pic.size[0] * s), round(pic.size[1] * s)), Image.LANCZOS)
        img.paste(pic, (x0 + (tw - pic.size[0]) // 2, ty + (th - pic.size[1]) // 2), pic)
    img.save(out, optimize=True)
    print(f"og: {out} ({W} x {H}, {os.path.getsize(out)} B)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT / "og.png")
