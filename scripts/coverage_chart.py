"""Coverage review image: one cell per compound, per garden. Darker = more footprints; a crossed cell = no position. Numbers come from research/plan/coverage.json."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

C = json.loads(Path("research/plan/coverage.json").read_text(encoding="utf-8"))
SURFACE = (252, 252, 250)
INK, MUTED, RULE = (32, 32, 30), (105, 105, 100), (214, 212, 205)
STEPS = [(0, "0", (231, 238, 247)), (1, "1-4", (176, 203, 233)), (5, "5-14", (92, 148, 208)), (15, "15+", (28, 84, 150))]
GARDENS = ["Yuanming Yuan", "Changchun Yuan", "Xiyang Lou", "Qichun Yuan"]
CW, CH, GAP, COLS, LEFT = 62, 44, 2, 22, 28
FONT = ImageFont.load_default(13)
SMALL = ImageFont.load_default(12)
TITLE = ImageFont.load_default(24)
HEAD = ImageFont.load_default(16)


def step(n):
    s = STEPS[0]
    for t in STEPS:
        if n >= t[0]:
            s = t
    return s


def main():
    per = C["per_compound"]
    H = 130 + sum(((len([1 for v in per.values() if v["garden"] == g]) - 1) // COLS + 1) * (CH + GAP) + 62 for g in GARDENS)
    W = LEFT * 2 + COLS * (CW + GAP)
    im = Image.new("RGB", (W, H), SURFACE)
    d = ImageDraw.Draw(im)
    d.text((LEFT, 18), f"{C['compounds_with_position']} of {C['compounds']} compounds have a position; {C['footprints']} footprints", font=TITLE, fill=INK)
    d.text((LEFT, 50), "One cell per compound: its id and the footprints inside it. Crossed = not found on the plan, no position.", font=HEAD, fill=MUTED)
    x = LEFT
    for _, lab, col in STEPS:
        d.rectangle((x, 80, x + 22, 96), fill=col)
        d.text((x + 28, 81), lab + " footprints", font=FONT, fill=MUTED)
        x += 130
    d.rectangle((x, 80, x + 22, 96), outline=MUTED)
    d.line((x, 80, x + 22, 96), fill=MUTED)
    d.line((x + 22, 80, x, 96), fill=MUTED)
    d.text((x + 28, 81), "no position", font=FONT, fill=MUTED)
    y = 116
    for g in GARDENS:
        items = sorted((k, v) for k, v in per.items() if v["garden"] == g)
        s = C["by_garden"][g]
        d.text((LEFT, y), f"{g}: {s['compounds_positioned']}/{s['compounds']} compounds, {s['halls_positioned']}/{s['halls']} halls with a position, {s['footprints']} footprints", font=HEAD, fill=INK)
        y += 26
        for i, (k, v) in enumerate(items):
            cx = LEFT + (i % COLS) * (CW + GAP)
            cy = y + (i // COLS) * (CH + GAP)
            if not v["position"]:
                d.rectangle((cx, cy, cx + CW, cy + CH), outline=MUTED)
                d.line((cx, cy, cx + CW, cy + CH), fill=RULE)
                d.line((cx + CW, cy, cx, cy + CH), fill=RULE)
                d.text((cx + 5, cy + 4), k, font=FONT, fill=MUTED)
                continue
            col = step(v["footprints"])[2]
            d.rectangle((cx, cy, cx + CW, cy + CH), fill=col)
            ink = (255, 255, 255) if v["footprints"] >= 5 else INK
            d.text((cx + 5, cy + 4), k, font=FONT, fill=ink)
            d.text((cx + 5, cy + 23), str(v["footprints"]), font=SMALL, fill=ink)
        y += ((len(items) - 1) // COLS + 1) * (CH + GAP) + 34
    im = im.crop((0, 0, W, y))
    im.save("screenshots/r1/coverage.png")
    print(im.size)


if __name__ == "__main__":
    main()
