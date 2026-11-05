"""Round 9 path readers' crop tool. Plan S01 crops stay in scratch (CLAUDE.md, Q6): never copy them into the repo.

Run from the repo:  cd /opt/data/workspace/000_Dev/palace-beijing-yaga-sh && uv run python /opt/data/cache/scratch/palace_r9_tools/crop.py <command> ...

  crop <tag> <plan_x> <plan_y> [half_px=250]
        -> palace_r9_crops/<tag>.png (clean) and <tag>_ids.png (with row ids, gates G.., bridges BR.. drawn in red/blue).
        The output is 2x the plan (half_px=250 -> 1000 px image, about 120 m of ground). The yellow grid lines are every
        50 plan pixels and are LABELLED IN ABSOLUTE PLAN PIXELS, so you read coordinates straight off the grid.
  show <tag> <traces.csv> <plan_x> <plan_y> [half_px=250]
        -> palace_r9_crops/<tag>_check.png: your traced lines (green = B, orange = C, magenta = landing) over the crop, to check them.
  ids <scene_id>
        -> lists the rows of that scene with plan pixels, and the gates and bridges within its box.
Scale: about 4.2-4.8 plan px per metre (hall scale 4.18 px/m along the frontage); 10 m is about 45 px.
"""
import csv
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None
REPO = Path("/opt/data/workspace/000_Dev/palace-beijing-yaga-sh")
CTX = Path("/opt/data/cache/scratch/palace_r9_context")
OUT = Path("/opt/data/cache/scratch/palace_r9_crops")
OUT.mkdir(exist_ok=True)
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
SMALL = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
K = 2


def load(name):
    return list(csv.DictReader(open(CTX / name, encoding="utf-8")))


def base(x, y, h):
    im = Image.open(REPO / "research/raw/plans/princeton_mosaic.jpg")
    c = im.crop((x - h, y - h, x + h, y + h)).convert("RGB").resize((2 * h * K, 2 * h * K))
    d = ImageDraw.Draw(c)
    x0, y0 = x - h, y - h
    g0 = (x0 // 50 + 1) * 50
    for gx in range(g0, x + h, 50):
        X = (gx - x0) * K
        d.line([(X, 0), (X, 2 * h * K)], fill=(230, 200, 0), width=1)
        if gx % 100 == 0:
            d.text((X + 2, 2), str(gx), fill=(160, 0, 160), font=SMALL)
    g0 = (y0 // 50 + 1) * 50
    for gy in range(g0, y + h, 50):
        Y = (gy - y0) * K
        d.line([(0, Y), (2 * h * K, Y)], fill=(230, 200, 0), width=1)
        if gy % 100 == 0:
            d.text((2, Y + 2), str(gy), fill=(160, 0, 160), font=SMALL)
    return c, d, x0, y0


def to(x0, y0, px, py):
    return ((float(px) - x0) * K, (float(py) - y0) * K)


def crop(tag, x, y, h=250):
    x, y, h = int(x), int(y), int(h)
    c, d, x0, y0 = base(x, y, h)
    c.save(OUT / f"{tag}.png")
    for r in load("rows.csv"):
        px, py = float(r["plan_x"]), float(r["plan_y"])
        if abs(px - x) < h and abs(py - y) < h:
            X, Y = to(x0, y0, px, py)
            d.ellipse([X - 3, Y - 3, X + 3, Y + 3], fill=(220, 0, 0))
            d.text((X + 4, Y - 6), r["id"], fill=(200, 0, 0), font=FONT)
    for g in load("gates.csv"):
        px, py = float(g["plan_x"]), float(g["plan_y"])
        if abs(px - x) < h and abs(py - y) < h:
            X, Y = to(x0, y0, px, py)
            d.rectangle([X - 4, Y - 4, X + 4, Y + 4], outline=(0, 0, 220), width=2)
            d.text((X + 5, Y + 2), g["id"], fill=(0, 0, 220), font=FONT)
    for b in load("bridges.csv"):
        a = to(x0, y0, b["x1"], b["y1"])
        e = to(x0, y0, b["x2"], b["y2"])
        if any(0 <= p[0] <= 2 * h * K and 0 <= p[1] <= 2 * h * K for p in (a, e)):
            d.line([a, e], fill=(0, 90, 255), width=3)
            d.text((e[0] + 4, e[1]), b["id"], fill=(0, 60, 200), font=FONT)
    c.save(OUT / f"{tag}_ids.png")
    print(OUT / f"{tag}.png", OUT / f"{tag}_ids.png")


def show(tag, traces, x, y, h=250):
    x, y, h = int(x), int(y), int(h)
    c, d, x0, y0 = base(x, y, h)
    for r in csv.DictReader(open(traces, encoding="utf-8")):
        pts = [to(x0, y0, *p.split()) for p in r["points_px"].split(";") if p.strip()]
        col = (220, 0, 220) if r["kind"] in ("landing", "dock") else (0, 170, 0) if r.get("confidence", "") in ("A", "B") else (255, 140, 0)
        if len(pts) == 1:
            X, Y = pts[0]
            d.ellipse([X - 5, Y - 5, X + 5, Y + 5], outline=col, width=3)
        else:
            d.line(pts, fill=col, width=3)
        if pts:
            d.text((pts[0][0] + 4, pts[0][1] + 4), r.get("key", ""), fill=col, font=SMALL)
    c.save(OUT / f"{tag}_check.png")
    print(OUT / f"{tag}_check.png")


def ids(scene):
    rows = [r for r in load("rows.csv") if r["id"] == scene or r["parent_id"] == scene]
    for r in rows:
        print(r["id"], r["name_zh"], r["type"], r["hall_class"], r["plan_x"], r["plan_y"], r["bays_plan"])
    sc = next((s for s in load("scenes.csv") if s["id"] == scene), None)
    if sc:
        m = 60
        x1, y1, x2, y2 = int(sc["minx"]) - m, int(sc["miny"]) - m, int(sc["maxx"]) + m, int(sc["maxy"]) + m
        print(f"scene box plan px {x1},{y1} - {x2},{y2}; centre {sc['cx']},{sc['cy']}")
        for g in load("gates.csv"):
            if x1 <= float(g["plan_x"]) <= x2 and y1 <= float(g["plan_y"]) <= y2:
                print("gate", g["id"], g["name"], g["plan_x"], g["plan_y"])
        for b in load("bridges.csv"):
            if x1 <= float(b["x1"]) <= x2 and y1 <= float(b["y1"]) <= y2:
                print("bridge", b["id"], b["name_zh"], b["x1"], b["y1"], b["x2"], b["y2"])


if __name__ == "__main__":
    cmd, *a = sys.argv[1:]
    {"crop": crop, "show": show, "ids": ids}[cmd](*a)
