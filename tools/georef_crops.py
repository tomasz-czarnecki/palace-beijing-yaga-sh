"""Round 8 reading tool (the readers' copy ran from scratch as r8crop.py): crops of today's imagery (Esri, reading only) and of the plan S01 mosaic, with labelled grids.

Tiles and crops go to a scratch folder (PALACE_SCRATCH, default /opt/data/cache/scratch), never into git: the tiles are
under the provider's terms and the plan crops are of S01, which stays local (CLAUDE.md, Q6). The plan crop needs
research/raw/plans/princeton_mosaic.jpg (scripts/mosaic_plan.py).

No prediction marker is drawn. The plan crop is centred on the old transform's guess plus a random offset of up to 35 m,
so its centre gives no hint where the feature lies; find the feature by its form.

Commands (uv run python tools/georef_crops.py ...):
  pair  <tag> <lon> <lat> [half_m=120]      imagery crop + plan crop of about the same ground, 640 px each
  img   <tag> <lon> <lat> [half_m=40]       imagery crop only (zoom); z19 when half_m <= 45, else z18
  plan  <tag> <plan_x> <plan_y> [half_px=200]  plan crop only (zoom), unrotated plan pixels
  img2ll  <tag> <col> <row>                 a pixel of an imagery crop -> lon lat (WGS84)
  plan2px <tag> <col> <row>                 a pixel of a plan crop -> plan_x plan_y (mosaic pixels)
  near  - <lon> <lat>                       distance to the nearest old fit point and to the nearest check point written so far
Crops go to /opt/data/cache/scratch/palace_r8_crops/<tag>_img.png and <tag>_plan.png; the grid labels are crop pixels.
"""

import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None
import os

REPO = Path(__file__).resolve().parent.parent
SCRATCH = Path(os.environ.get("PALACE_SCRATCH", "/opt/data/cache/scratch"))
sys.path.insert(0, str(REPO / "scripts"))
import georef  # noqa: E402

georef.JSON_PATH = georef.PREVIOUS_PATH  # navigation only, on the Round 1 fit, as the readers had it
OUT = SCRATCH / "palace_r8_crops"
OUT.mkdir(parents=True, exist_ok=True)
TILES = SCRATCH / "palace_r8_tiles"
TILES.mkdir(parents=True, exist_ok=True)
MOSAIC = REPO / "research/raw/plans/princeton_mosaic.jpg"
URL = "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
SIZE = 640
_MOS = None


def merc(lon, lat, z):
    n = 2**z * 256
    return (lon + 180) / 360 * n, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n


def unmerc(x, y, z):
    n = 2**z * 256
    return x / n * 360 - 180, math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))


def tile(z, tx, ty):
    f = TILES / f"{z}_{tx}_{ty}.jpg"
    if not f.exists():
        for _ in range(3):
            try:
                r = requests.get(URL.format(z=z, x=tx, y=ty), timeout=30, headers={"User-Agent": "palace-beijing-yaga-sh research (reading only)"})
                if r.status_code == 200:
                    f.write_bytes(r.content)
                    break
            except Exception:
                pass
            time.sleep(2)
        time.sleep(0.2)
    return Image.open(f).convert("RGB") if f.exists() else Image.new("RGB", (256, 256), (90, 90, 90))


def grid(im, step=64, colour=(255, 255, 0)):
    d = ImageDraw.Draw(im)
    for v in range(0, SIZE + 1, step):
        d.line([(v, 0), (v, SIZE)], fill=colour, width=1)
        d.line([(0, v), (SIZE, v)], fill=colour, width=1)
        d.text((v + 2, 2), str(v), fill=colour, font=FONT, stroke_width=2, stroke_fill=(0, 0, 0))
        d.text((2, v + 2), str(v), fill=colour, font=FONT, stroke_width=2, stroke_fill=(0, 0, 0))
    for v in range(32, SIZE, 64):  # half ticks
        for w in range(0, SIZE, 16):
            d.point([(v, w), (w, v)], fill=colour)
    return im


def img_crop(tag, lon, lat, half_m):
    z = 19 if half_m <= 45 else 18
    cx, cy = merc(lon, lat, z)
    mpp = 156543.03392 * math.cos(math.radians(lat)) / 2**z
    half_px = half_m / mpp
    x0, y0, x1, y1 = cx - half_px, cy - half_px, cx + half_px, cy + half_px
    tx0, ty0, tx1, ty1 = int(x0 // 256), int(y0 // 256), int(x1 // 256), int(y1 // 256)
    canvas = Image.new("RGB", ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256))
    for ty in range(ty0, ty1 + 1):
        for tx in range(tx0, tx1 + 1):
            canvas.paste(tile(z, tx, ty), ((tx - tx0) * 256, (ty - ty0) * 256))
    box = (x0 - tx0 * 256, y0 - ty0 * 256, x1 - tx0 * 256, y1 - ty0 * 256)
    im = canvas.transform((SIZE, SIZE), Image.EXTENT, box, Image.BICUBIC)
    meta = {"z": z, "x0": x0, "y0": y0, "scale": (x1 - x0) / SIZE, "m_per_crop_px": round(2 * half_m / SIZE, 3)}
    (OUT / f"{tag}_img.json").write_text(json.dumps(meta))
    grid(im).save(OUT / f"{tag}_img.png")
    return OUT / f"{tag}_img.png", meta


def mosaic():
    global _MOS
    if _MOS is None:
        _MOS = Image.open(MOSAIC).convert("RGB")
    return _MOS


def plan_crop(tag, px, py, half_px):
    box = (px - half_px, py - half_px, px + half_px, py + half_px)
    im = mosaic().transform((SIZE, SIZE), Image.EXTENT, box, Image.BICUBIC)
    meta = {"x0": box[0], "y0": box[1], "scale": 2 * half_px / SIZE, "m_per_crop_px_approx": round(2 * half_px / SIZE / 4.77, 3)}
    (OUT / f"{tag}_plan.json").write_text(json.dumps(meta))
    grid(im, colour=(255, 0, 255)).save(OUT / f"{tag}_plan.png")
    return OUT / f"{tag}_plan.png", meta


def offset(tag, r_px):
    h = hashlib.sha256(tag.encode()).digest()
    a = h[0] / 255 * 2 * math.pi
    d = (0.4 + 0.6 * h[1] / 255) * r_px
    return d * math.cos(a), d * math.sin(a)


def main():
    cmd, tag = sys.argv[1], sys.argv[2]
    a = sys.argv[3:]
    if cmd == "pair":
        lon, lat = float(a[0]), float(a[1])
        half_m = float(a[2]) if len(a) > 2 else 120.0
        p, _ = img_crop(tag, lon, lat, half_m)
        x, y = georef.wgs84_to_plan(np.array([lon]), np.array([lat]))
        ox, oy = offset(tag, 35 * 4.77)
        q, _ = plan_crop(tag, float(x[0]) + ox, float(y[0]) + oy, half_m * 4.77 * 1.15)
        print(p, q, "(plan crop is unrotated: plan north is turned about 7 deg from true north, and covers about 15% more ground)")
    elif cmd == "img":
        print(img_crop(tag, float(a[0]), float(a[1]), float(a[2]) if len(a) > 2 else 40.0)[0])
    elif cmd == "plan":
        print(plan_crop(tag, float(a[0]), float(a[1]), float(a[2]) if len(a) > 2 else 200.0)[0])
    elif cmd == "img2ll":
        m = json.loads((OUT / f"{tag}_img.json").read_text())
        lon, lat = unmerc(m["x0"] + float(a[0]) * m["scale"], m["y0"] + float(a[1]) * m["scale"], m["z"])
        print(f"{lon:.7f} {lat:.7f}")
    elif cmd == "plan2px":
        m = json.loads((OUT / f"{tag}_plan.json").read_text())
        print(f"{m['x0'] + float(a[0]) * m['scale']:.1f} {m['y0'] + float(a[1]) * m['scale']:.1f}")
    elif cmd == "near":
        # distance to the nearest old fit point, and to the nearest check point already written by any worker
        lon, lat = float(a[0]), float(a[1])
        k = math.cos(math.radians(lat)) * 111320
        fits = [{"id": r["id"], "lon": r["lon"], "lat": r["lat"]} for r in georef.read_points() if r["use"] == "fit"]
        d = sorted((math.hypot((f["lon"] - lon) * k, (f["lat"] - lat) * 110950), f["id"]) for f in fits)[0]
        chk = []
        for f in list(SCRATCH.glob("palace_r8_out_*.jsonl")) + list((REPO / "research/georef/readings_r8").glob("*.jsonl")):
            for line in f.read_text().splitlines():
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                if r.get("set") == "check":
                    chk.append((math.hypot((r["lon"] - lon) * k, (r["lat"] - lat) * 110950), r["id"]))
        c = sorted(chk)[0] if chk else (float("inf"), "-")
        print(f"nearest old fit point {d[1]} at {d[0]:.0f} m; nearest check point {c[1]} at {c[0]:.0f} m")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
