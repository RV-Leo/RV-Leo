"""Genera assets/eous-contrib-{dark,light}.svg: la grilla de contribuciones con Eous caminando encima.

Uso: python scripts/eous_contrib.py [usuario]
Lee el calendario público de GitHub (no necesita token).
"""
import re
import sys
import urllib.request
from pathlib import Path

USER = sys.argv[1] if len(sys.argv) > 1 else "RV-Leo"
OUT_DIR = Path(__file__).resolve().parent.parent / "assets"

CELL, GAP = 11, 3
STEP = CELL + GAP
LEFT, TOP = 30, 34
THEMES = {
    "dark": {
        "levels": ["#161b22", "#2e1065", "#5b21b6", "#7c3aed", "#a78bfa"],
        "glow": "#e9d5ff", "trail": "#3b2a6b",
        "text": "#8b949e", "title": "#c9d1d9", "floor": "#21262d", "shadow": ".35",
    },
    "light": {
        "levels": ["#ebedf0", "#ddd6fe", "#a78bfa", "#7c3aed", "#5b21b6"],
        "glow": "#4c1d95", "trail": "#c4b5fd",
        "text": "#57606a", "title": "#1f2328", "floor": "#d0d7de", "shadow": ".18",
    },
}
LOOP = 14.0   # segundos por vuelta
WALK = 12.0   # segundos cruzando la grilla
PX = 2.5      # tamaño de cada pixel del sprite

PALETTE = {
    "K": "#2a2540",  # contorno
    "W": "#e8e6f3",  # cuerpo
    "S": "#b9b4d0",  # sombra
    "D": "#1b1830",  # pantalla
    "P": "#a78bfa",  # interior de orejas
}
BODY = [
    "...KK......KK...",
    "..KWWK....KWWK..",
    "..KWPK....KPWK..",
    "..KWPK....KPWK..",
    "..KWPK....KPWK..",
    "...KWKKKKKKWK...",
    "..KWWWWWWWWWWK..",
    ".KWWDDDDDDDDWWK.",
    ".KWDDDDDDDDDDWK.",
    ".KWDDDDDDDDDDWK.",
    ".KWDDDDDDDDDDWK.",
    ".KWDDDDDDDDDDWK.",
    ".KWWDDDDDDDDWWK.",
    "..KWWWWWWWWWWK..",
    "..KSWWWWWWWWSK..",
    "...KSSSSSSSSK...",
]
FEET_A = ["...KWK....KWK...", "...KK......KK..."]
FEET_B = ["....KWK..KWK....", "....KK....KK...."]
EYES = [(5, 9), (10, 9)]  # columna, fila (2x2 pixeles cian)


def fetch_calendar(user):
    req = urllib.request.Request(
        f"https://github.com/users/{user}/contributions",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    cells = {}
    for td in re.findall(r"<td[^>]*ContributionCalendar-day[^>]*>", html):
        m = re.search(r'id="contribution-day-component-(\d+)-(\d+)"', td)
        lvl = re.search(r'data-level="(\d)"', td)
        if m and lvl:
            cells[(int(m.group(2)), int(m.group(1)))] = int(lvl.group(1))
    total = re.search(r"([\d,]+)\s+contributions?\s+in the last year", html)
    total = int(total.group(1).replace(",", "")) if total else 0
    return cells, total


def pixels(rows, y0=0):
    out = []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in PALETTE:
                out.append(f'<rect x="{x * PX}" y="{(y + y0) * PX}" width="{PX}" height="{PX}" fill="{PALETTE[ch]}"/>')
    return "".join(out)


def build(cells, total, theme):
    th = THEMES[theme]
    cols = max(c for c, _ in cells) + 1
    grid_w = cols * STEP
    width = LEFT + grid_w + 20
    floor = TOP + 7 * STEP + 8
    sprite_w, sprite_h = 16 * PX, (len(BODY) + len(FEET_A)) * PX
    height = int(floor + sprite_h + 10)
    x0, x1 = LEFT - sprite_w - 20, width + 10

    css = [
        "text{font-family:'Segoe UI',Helvetica,Arial,sans-serif;fill:%s;font-size:11px}" % th["text"],
        ".t{fill:%s;font-size:13px;font-weight:600}" % th["title"],
        "@keyframes glow{0%,100%{fill:var(--c)}1.5%{fill:var(--g)}9%{fill:var(--c)}}",
        "rect.e{animation:glow %ss linear infinite}" % LOOP,
        f"@keyframes hop{{0%,100%{{transform:translateY(0)}}1.5%{{transform:translateY(-3px)}}6%{{transform:translateY(0)}}}}",
        "rect.d{animation:glow %ss linear infinite,hop %ss ease-out infinite;transform-box:fill-box}" % (LOOP, LOOP),
        "@media (prefers-reduced-motion:reduce){rect.d,rect.e{animation:none}}",
    ]
    rects = []
    for (c, r), lvl in sorted(cells.items()):
        cx = LEFT + c * STEP
        # momento en que el centro de Eous pasa por esta columna
        t = (cx + CELL / 2 - x0 - sprite_w / 2) / (x1 - x0) * WALK
        # las casillas vacías se iluminan suave al paso de Eous; las que tienen
        # contribuciones brillan fuerte y dan un saltito
        cls, glow = ("d", th["glow"]) if lvl else ("e", th["trail"])
        rects.append(
            f'<rect class="{cls}" x="{cx}" y="{TOP + r * STEP}" width="{CELL}" height="{CELL}" rx="2" '
            f'style="--c:{th["levels"][lvl]};--g:{glow};fill:{th["levels"][lvl]};animation-delay:{t:.2f}s"/>'
        )

    eyes = "".join(
        f'<rect x="{ex * PX}" y="{ey * PX}" width="{2 * PX}" height="{2 * PX}" fill="#5eead4">'
        f'<animate attributeName="height" values="{2 * PX};{0.6 * PX};{2 * PX}" keyTimes="0;0.5;1" dur="0.25s" begin="2s;blink.end+3s" id="{"blink" if i == 0 else f"b{i}"}"/>'
        f'<animate attributeName="y" values="{ey * PX};{(ey + 0.7) * PX};{ey * PX}" keyTimes="0;0.5;1" dur="0.25s" begin="2s;blink.end+3s"/>'
        "</rect>"
        for i, (ex, ey) in enumerate(EYES)
    )
    frame_a = f'<g>{pixels(FEET_A, len(BODY))}<animate attributeName="opacity" values="1;0" dur="0.4s" calcMode="discrete" repeatCount="indefinite"/></g>'
    frame_b = f'<g opacity="0">{pixels(FEET_B, len(BODY))}<animate attributeName="opacity" values="0;1" dur="0.4s" calcMode="discrete" repeatCount="indefinite"/></g>'
    bob = f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -2;0 0" dur="0.4s" repeatCount="indefinite"/>'
    walk_kt = f"0;{WALK / LOOP:.4f};1"
    sprite = (
        f'<g><animateTransform attributeName="transform" type="translate" '
        f'values="{x0} {floor};{x1} {floor};{x1} {floor}" keyTimes="{walk_kt}" dur="{LOOP}s" repeatCount="indefinite"/>'
        f'<ellipse cx="{sprite_w / 2}" cy="{sprite_h + 1}" rx="{sprite_w / 2.6}" ry="2.5" fill="#000" opacity="{th["shadow"]}"/>'
        f'<g>{bob}{pixels(BODY)}{eyes}{frame_a}{frame_b}</g></g>'
    )

    label = f"{total} contribuciones"

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">'
        f"<title>{label}: Eous camina sobre la grilla y la ilumina a su paso</title>"
        f'<style>{"".join(css)}</style>'
        f'<text class="t" x="{LEFT}" y="18">{label}</text>'
        f'<text x="2" y="{TOP + 1 * STEP + 9}">L</text><text x="2" y="{TOP + 3 * STEP + 9}">M</text><text x="2" y="{TOP + 5 * STEP + 9}">V</text>'
        f'{"".join(rects)}'
        f'<line x1="{LEFT}" y1="{floor + sprite_h + 2}" x2="{LEFT + grid_w - GAP}" y2="{floor + sprite_h + 2}" stroke="{th["floor"]}" stroke-width="1"/>'
        f"{sprite}</svg>"
    )


if __name__ == "__main__":
    cells, total = fetch_calendar(USER)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        (OUT_DIR / f"eous-contrib-{theme}.svg").write_text(build(cells, total, theme), encoding="utf-8")
    print(f"{len(cells)} días, {total} contribuciones")
