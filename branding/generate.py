#!/usr/bin/env python3
"""Generate every Himalo brand asset from the vector sources defined below.

    pip install cairosvg pillow
    python3 branding/generate.py

Writes SVG masters plus Android launcher icons, Play Store graphics and web
icons into branding/. Edit the shapes or colours here and re-run.
"""
import io
import os

import cairosvg
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

GREEN_TOP = "#34D07F"
GREEN_BOTTOM = "#16965A"
INK = "#0A1510"
SNOW = "#FFFFFF"

# The mark on a 1024 grid: two Himalayan peaks rising out of a food bowl.
# It fits inside the centred 61% circle, the adaptive-icon safe zone.
BACK_PEAK = "M510 596 L668 380 L812 596 Z"
BACK_SNOW = "M616 451 L668 380 L714 451 L692 472 L668 455 L644 474 Z"
FRONT_PEAK = "M226 596 L456 232 L686 596 Z"
SEPARATOR = "M475 262 L686 596"
FRONT_SNOW = "M378 355 L456 232 L534 355 L495 392 L456 361 L417 394 Z"
BOWL = "M212 628 Q212 616 224 616 H800 Q812 616 812 628 A300 206 0 0 1 212 628 Z"

# "Himalo" set in Outfit Bold (SIL OFL), converted to outlines. Font units, y-up,
# cap height 706, total advance 3296.
WORDMARK = """
<path transform="translate(0,0)" d="M68 0V706H225V0ZM505 0V706H663V0ZM162 295V431H557V295Z"/>
<path transform="translate(730,0)" d="M54 0V486H207V0ZM131 553Q95 553 71.5 577.5Q48 602 48 637Q48 673 71.5 697.0Q95 721 131 721Q167 721 190.0 697.0Q213 673 213 637Q213 602 190.0 577.5Q167 553 131 553Z"/>
<path transform="translate(991,0)" d="M54 0V486H207V0ZM365 0V284Q365 321 342.5 341.5Q320 362 287 362Q264 362 246.0 352.5Q228 343 217.5 326.0Q207 309 207 284L148 310Q148 368 173.0 409.5Q198 451 241.0 473.5Q284 496 338 496Q389 496 429.5 473.0Q470 450 494.0 409.0Q518 368 518 311V0ZM676 0V284Q676 321 653.5 341.5Q631 362 598 362Q575 362 557.0 352.5Q539 343 528.5 326.0Q518 309 518 284L430 296Q432 358 459.5 402.5Q487 447 532.5 471.5Q578 496 635 496Q691 496 734.5 472.5Q778 449 803.5 405.5Q829 362 829 301V0Z"/>
<path transform="translate(1864,0)" d="M257 -10Q190 -10 137.5 23.0Q85 56 54.5 113.0Q24 170 24 243Q24 316 54.5 373.0Q85 430 137.5 463.0Q190 496 257 496Q306 496 345.5 477.0Q385 458 410.0 424.5Q435 391 438 348V138Q435 95 410.5 61.5Q386 28 346.0 9.0Q306 -10 257 -10ZM288 128Q337 128 367.0 160.5Q397 193 397 243Q397 277 383.5 303.0Q370 329 345.5 343.5Q321 358 289 358Q257 358 232.5 343.5Q208 329 193.5 303.0Q179 277 179 243Q179 210 193.0 184.0Q207 158 232.0 143.0Q257 128 288 128ZM391 0V131L414 249L391 367V486H541V0Z"/>
<path transform="translate(2459,0)" d="M54 0V726H207V0Z"/>
<path transform="translate(2720,0)" d="M288 -11Q213 -11 152.5 22.5Q92 56 57.0 114.0Q22 172 22 244Q22 316 57.0 373.0Q92 430 152.0 463.5Q212 497 288 497Q364 497 424.0 464.0Q484 431 519.0 373.5Q554 316 554 244Q554 172 519.0 114.0Q484 56 424.0 22.5Q364 -11 288 -11ZM288 128Q321 128 346.0 142.5Q371 157 384.5 183.5Q398 210 398 244Q398 278 384.0 303.5Q370 329 345.5 343.5Q321 358 288 358Q256 358 231.0 343.5Q206 329 192.0 303.0Q178 277 178 243Q178 210 192.0 183.5Q206 157 231.0 142.5Q256 128 288 128Z"/>
"""
WORDMARK_ADVANCE = 3296
WORDMARK_CAP = 706


def mark(separator_colour, dy=-8):
    return f"""<g transform="translate(0,{dy})">
    <path d="{BACK_PEAK}" fill="{INK}"/>
    <path d="{BACK_SNOW}" fill="{SNOW}"/>
    <path d="{FRONT_PEAK}" fill="{INK}"/>
    <path d="{SEPARATOR}" stroke="{separator_colour}" stroke-width="18" stroke-linecap="round"/>
    <path d="{FRONT_SNOW}" fill="{SNOW}"/>
    <path d="{BOWL}" fill="{INK}"/>
  </g>"""


def monochrome_png(rel, size):
    # Themed-icon layer for Android 13+: only alpha is used, so keep the ink
    # shapes opaque and cut out the snow caps and separator.
    raw = cairosvg.svg2png(bytestring=svg(mark("#FFFFFF")).encode(), output_width=size, output_height=size)
    img = Image.open(io.BytesIO(raw)).convert("RGBA")
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    px, po = img.load(), out.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            ink = 255 - max(r, g, b)  # 245 for INK, 0 for white
            po[x, y] = (0, 0, 0, a * min(255, ink * 255 // 245) // 255)
    path = os.path.join(HERE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out.save(path)


def gradient_defs():
    return f"""<defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{GREEN_TOP}"/><stop offset="1" stop-color="{GREEN_BOTTOM}"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.12" r="0.55">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.35"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </radialGradient>
  </defs>"""


def svg(body, w=1024, h=1024):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n  {body}\n</svg>\n'


def icon(shape):
    """Full-colour icon. shape: 'rounded', 'square' (Play Store; Google masks it) or 'circle'."""
    clip = {"rounded": 'rx="228"', "square": "", "circle": 'rx="512"'}[shape]
    return svg(f"""{gradient_defs()}
  <rect width="1024" height="1024" {clip} fill="url(#bg)"/>
  <rect width="1024" height="1024" {clip} fill="url(#glow)"/>
  {mark("#27BF71")}""")


def adaptive_background():
    return svg(f"""{gradient_defs()}
  <rect width="1024" height="1024" fill="url(#bg)"/>
  <rect width="1024" height="1024" fill="url(#glow)"/>""")


def wordmark(x, baseline, cap_px, fill):
    s = cap_px / WORDMARK_CAP
    return f'<g transform="translate({x},{baseline}) scale({s:.5f},{-s:.5f})" fill="{fill}">{WORDMARK}</g>'


def horizontal_logo(text_fill):
    # App icon + wordmark on a transparent background.
    h, cap = 400, 170
    text_x = 460
    width = int(text_x + WORDMARK_ADVANCE * cap / WORDMARK_CAP + 20)
    icon_body = icon("rounded").split("\n", 1)[1].rsplit("</svg>", 1)[0]
    body = f"""<svg x="0" y="0" width="{h}" height="{h}" viewBox="0 0 1024 1024">{icon_body}</svg>
  {wordmark(text_x, 285, cap, text_fill)}"""
    return svg(body, width, h)


def feature_graphic():
    # Play Store feature graphic, 1024x500.
    cap = 120
    text_w = WORDMARK_ADVANCE * cap / WORDMARK_CAP
    mark_px = 380
    gap = 0
    total = mark_px + gap + text_w
    x0 = (1024 - total) / 2
    return svg(f"""{gradient_defs()}
  <rect width="1024" height="500" fill="url(#bg)"/>
  <rect width="1024" height="500" fill="url(#glow)"/>
  <g transform="translate({x0:.1f},{(500 - mark_px) / 2 - 20:.1f}) scale({mark_px/1024:.5f})">{mark("#27BF71", dy=0)}</g>
  {wordmark(x0 + mark_px + gap, 300, cap, INK)}""", 1024, 500)


def write(rel, text):
    path = os.path.join(HERE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
    return path


def png(svg_text, rel, w, h=None):
    path = os.path.join(HERE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cairosvg.svg2png(bytestring=svg_text.encode(), write_to=path, output_width=w, output_height=h or w)


def main():
    # Vector masters
    write("himalo-icon.svg", icon("rounded"))
    write("himalo-mark.svg", svg(mark("#FFFFFF")))
    write("himalo-logo-horizontal.svg", horizontal_logo(INK))
    write("himalo-logo-horizontal-on-dark.svg", horizontal_logo("#FFFFFF"))

    # Android launcher icons (drop android/res/ into app/src/main/res/)
    densities = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
    for name, f in densities.items():
        d = f"android/res/mipmap-{name}"
        png(icon("rounded"), f"{d}/ic_launcher.png", int(48 * f))
        png(icon("circle"), f"{d}/ic_launcher_round.png", int(48 * f))
        png(svg(mark("#27BF71")), f"{d}/ic_launcher_foreground.png", int(108 * f))
        png(adaptive_background(), f"{d}/ic_launcher_background.png", int(108 * f))
        monochrome_png(f"{d}/ic_launcher_monochrome.png", int(108 * f))
    adaptive = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@mipmap/ic_launcher_background" />
    <foreground android:drawable="@mipmap/ic_launcher_foreground" />
    <monochrome android:drawable="@mipmap/ic_launcher_monochrome" />
</adaptive-icon>
"""
    write("android/res/mipmap-anydpi-v26/ic_launcher.xml", adaptive)
    write("android/res/mipmap-anydpi-v26/ic_launcher_round.xml", adaptive)
    # In-app logo (replaces the old nutritrack_logo drawable)
    png(icon("rounded"), "android/res/drawable-nodpi/himalo_logo.png", 1024)

    # Google Play listing
    png(icon("square"), "playstore/icon-512.png", 512)
    png(feature_graphic(), "playstore/feature-graphic-1024x500.png", 1024, 500)

    # Web / Firebase Hosting
    png(icon("rounded"), "web/favicon-32.png", 32)
    png(icon("square"), "web/apple-touch-icon.png", 180)
    png(icon("rounded"), "web/icon-192.png", 192)
    png(icon("rounded"), "web/icon-512.png", 512)

    # Previews
    png(horizontal_logo(INK), "himalo-logo-horizontal.png", 1200, int(1200 * 400 / (400 + WORDMARK_ADVANCE * 170 / WORDMARK_CAP + 20)))


if __name__ == "__main__":
    main()
