"""Genera assets/banner-{dark,light}.png: "Leo" al frente y "AJAX" translúcido detrás.

Uso: python scripts/banner.py  (necesita Pillow y las fuentes Segoe UI de Windows)
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path(__file__).resolve().parent.parent / "assets"
FONT = "C:/Windows/Fonts/seguibl.ttf"  # Segoe UI Black
W, H = 1800, 340
THEMES = {
    "dark": {
        "stops": [(0.0, (13, 17, 23)), (0.45, (46, 16, 101)), (1.0, (124, 58, 237))],
        "name": (255, 255, 255, 255), "ghost": (196, 181, 253, 110),
    },
    "light": {
        "stops": [(0.0, (237, 233, 254)), (0.5, (167, 139, 250)), (1.0, (124, 58, 237))],
        "name": (46, 16, 101, 255), "ghost": (76, 29, 149, 90),
    },
}


def gradient(stops):
    row = Image.new("RGB", (W, 1))
    px = row.load()
    for x in range(W):
        t = x / (W - 1)
        for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
            if t0 <= t <= t1:
                k = (t - t0) / (t1 - t0)
                px[x, 0] = tuple(int(c0[i] + (c1[i] - c0[i]) * k) for i in range(3))
                break
    return row.resize((W, H))


def wave_mask():
    mask = Image.new("L", (W, H), 0)
    edge = [(x, H - 60 + 26 * math.sin(x / W * 2 * math.pi * 1.1 + 0.6)) for x in range(W, -1, -6)]
    ImageDraw.Draw(mask).polygon([(0, 0), (W, 0)] + edge, fill=255)
    return mask


def build(theme):
    th = THEMES[theme]
    mask = wave_mask()
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.paste(gradient(th["stops"]), (0, 0), mask)

    # "AJAX" gigante solo con contorno, recortado por la ola
    ghost = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(ghost)
    gfont = ImageFont.truetype(FONT, 260)
    gw = gd.textlength("AJAX", font=gfont)
    gd.text(((W - gw) / 2, -22), "AJAX", font=gfont, fill=(0, 0, 0, 0), stroke_width=3, stroke_fill=th["ghost"])
    ghost.putalpha(Image.composite(ghost.getchannel("A"), Image.new("L", (W, H), 0), mask))
    img = Image.alpha_composite(img, ghost)

    d = ImageDraw.Draw(img)
    nfont = ImageFont.truetype(FONT, 132)
    nw = d.textlength("Leo", font=nfont)
    d.text(((W - nw) / 2, 64), "Leo", font=nfont, fill=th["name"])
    return img


if __name__ == "__main__":
    for theme in THEMES:
        build(theme).save(OUT_DIR / f"banner-{theme}.png", optimize=True)
    print("ok")
