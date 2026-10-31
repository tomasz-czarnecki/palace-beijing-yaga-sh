"""A crop of the plan S01 round every object that has plan pixels, with a marker. Local only: research/raw/plancrops/<ID>.jpg, served by tools/serve_local.py under /_local/plancrops/. The plan stays off the public site until Tomasz decides (Q6).

  uv run python tools/plan_crops.py
"""

import csv
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research/raw/plancrops"
Image.MAX_IMAGE_PIXELS = None
HALF_TOP, HALF_HALL, SIZE = 330, 190, 560


def main():
    plan = Image.open(ROOT / "research/raw/plans/princeton_mosaic.jpg").convert("RGB")
    OUT.mkdir(parents=True, exist_ok=True)
    made = 0
    for r in csv.DictReader(open(ROOT / "research/buildings.csv", encoding="utf-8", newline="")):
        if not r["plan_x"]:
            continue
        out = OUT / f"{r['id']}.jpg"
        if out.exists():
            continue
        half = HALF_HALL if r["parent_id"] else HALF_TOP
        x, y = float(r["plan_x"]), float(r["plan_y"])
        im = plan.crop((int(x - half), int(y - half), int(x + half), int(y + half))).resize((SIZE, SIZE), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        c = SIZE / 2
        d.ellipse((c - 20, c - 20, c + 20, c + 20), outline=(200, 40, 30), width=3)
        im.save(out, "JPEG", quality=72, optimize=True)
        made += 1
    print(made, "crops in", OUT)


if __name__ == "__main__":
    main()
