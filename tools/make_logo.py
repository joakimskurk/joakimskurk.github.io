#!/usr/bin/env python3
"""Joakim Skurk's logo, redrawn (assets/skurk-logo.svg): the old logo's yellow name, its tilt and its pixel splatter
in purple, green and cyan, in a cleaner cut. The letters are paths (no fonts needed where it is shown).

  python3 tools/make_logo.py            (needs fontTools: pip install fonttools)

Writes assets/skurk-logo.svg (the logo) and assets/skurk-mark.svg (the small one for the top bar and the icon).
Fonts: Space Grotesk (SIL Open Font License), in tools/fonts."""
import random
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parent.parent
YELLOW, YELLOW2, PURPLE, PURPLE2, GREEN, GREEN2, CYAN = \
    "#ffd60a", "#ffb000", "#c86bff", "#8f3fd6", "#45ff3a", "#25b81e", "#2ee6ff"


def font(weight):
    f = TTFont(ROOT / "tools" / "fonts" / "SpaceGrotesk.ttf")
    return instantiateVariableFont(f, {"wght": weight})


def text_path(f, text, size, x, y, tracking=0.0):
    """the text as one SVG path, its baseline at y; returns (d, width)"""
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
    s = size / f["head"].unitsPerEm
    pen = SVGPathPen(gs)
    cx = x
    for ch in text:
        g = cmap[ord(ch)]
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, cx, y)))
        cx += hmtx[g][0] * s + tracking
    return pen.getCommands(), cx - tracking - x


def splatter(cx, cy, rx, ry, px, seed, skew=0.0):
    """the pixel splatter: squares on a grid, thicker in the middle, in the old logo's colours"""
    rnd, out = random.Random(seed), []
    cols = [PURPLE, PURPLE, PURPLE2, GREEN, GREEN, GREEN2, CYAN]
    for gy in range(int((cy - ry) // px), int((cy + ry) // px) + 1):
        for gx in range(int((cx - rx) // px), int((cx + rx) // px) + 1):
            x, y = gx * px, gy * px
            dx, dy = (x - cx - (y - cy) * skew) / rx, (y - cy) / ry
            d = max(0.0, (dx * dx + dy * dy) ** .5 + (rnd.random() - .5) * .35)
            if d < 1 and rnd.random() > d ** 1.6:
                a = min(1, (1 - d) * 1.3) * (.55 + .45 * rnd.random())
                out.append(f'<rect x="{x}" y="{y}" width="{px}" height="{px}" fill="{rnd.choice(cols)}" '
                           f'opacity="{a:.2f}"/>')
    return "\n    ".join(out)


def logo():
    bold, med = font(700), font(600)
    W, H = 1000, 430
    big = 300
    sk, skw = text_path(bold, "SKURK", big, 0, 0, tracking=-6)
    x0 = (W - skw) / 2
    base = 330
    # JOAKIM: spaced out over SKURK, starting over its S
    jo, jow = text_path(med, "JOAKIM", 62, 0, 0, tracking=22)
    skew = -10     # the old logo's lean, as an italic
    word = f'''<g transform="translate({x0:.1f} {base}) skewX({skew})">
      <path d="{sk}" fill="#000" transform="translate(14 14)"/>
      <path d="{sk}" fill="{PURPLE}" transform="translate(8 8)"/>
      <path d="{sk}" fill="{YELLOW}" stroke="#000" stroke-width="7" stroke-linejoin="round" paint-order="stroke"/>
      <path d="{sk}" fill="url(#depth)"/>
    </g>
    <g transform="translate({x0 + 46:.1f} {base - big * .72 - 20:.1f}) skewX({skew})">
      <path d="{jo}" fill="#000" transform="translate(6 6)"/>
      <path d="{jo}" fill="{YELLOW}" stroke="#000" stroke-width="5" stroke-linejoin="round" paint-order="stroke"/>
    </g>'''
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Joakim Skurk">
  <title>Joakim Skurk</title>
  <defs>
    <linearGradient id="depth" x1="0" y1="0" x2="0" y2="1">
      <stop offset=".55" stop-color="{YELLOW2}" stop-opacity="0"/>
      <stop offset="1" stop-color="{YELLOW2}" stop-opacity=".7"/>
    </linearGradient>
  </defs>
  <g transform="rotate(-5 {W / 2} {H / 2})">
    {splatter(W / 2 - 10, H / 2 + 6, 450, 200, 18, 11, skew=.18)}
    {word}
  </g>
</svg>
'''
    return svg


def mark():
    """the small one: SK on a little splatter, square"""
    bold = font(700)
    d, w = text_path(bold, "SK", 300, 0, 0, tracking=-10)
    S = 512
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}" role="img" aria-label="Joakim Skurk">
  <rect width="{S}" height="{S}" rx="96" fill="#050407"/>
  <g transform="rotate(-6 {S / 2} {S / 2})">
    {splatter(S / 2, S / 2, 240, 170, 24, 5, skew=.15)}
    <g transform="translate({(S - w) / 2 + 10:.1f} 362) skewX(-10)">
      <path d="{d}" fill="#000" transform="translate(14 14)"/>
      <path d="{d}" fill="{PURPLE}" transform="translate(8 8)"/>
      <path d="{d}" fill="{YELLOW}" stroke="#000" stroke-width="8" stroke-linejoin="round" paint-order="stroke"/>
    </g>
  </g>
</svg>
'''


if __name__ == "__main__":
    (ROOT / "assets").mkdir(exist_ok=True)
    (ROOT / "assets" / "skurk-logo.svg").write_text(logo())
    (ROOT / "assets" / "skurk-mark.svg").write_text(mark())
    for n in ("skurk-logo.svg", "skurk-mark.svg"):
        print(f"logo: assets/{n} ({(ROOT / 'assets' / n).stat().st_size} B)")
