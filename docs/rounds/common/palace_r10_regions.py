"""Round 10: the ground's accuracy by region, for research/terrain/README.md. A record, not a pipeline step (needs research/raw/dem/ for the plain's residual).

  uv run python docs/rounds/common/palace_r10_regions.py
"""

import csv
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from scene1860 import DATUM_M, layer, to_xz  # noqa: E402


def xz(g):
    return shapely.transform(shape(g), lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1])))


def main():
    scenes = {f["properties"]["id"]: xz(f["geometry"]).buffer(0) for f in layer("scenes_1860")}
    garden = {f["properties"].get("garden"): Polygon_of(f) for f in layer("walls_1860") if f["properties"]["kind"] == "outer_wall"}
    regions = {
        "Xiyang Lou strip": unary_union([g for k, g in scenes.items() if k.startswith("XY")]).buffer(20),
        "福海 and its shores (150 m)": next(xz(f["geometry"]).buffer(0) for f in layer("water_1860") if f["properties"]["name_zh"] == "福海").buffer(150),
        "western plain (Yuanming Yuan west of x = -700 m)": garden.get("Yuanming Yuan").intersection(shapely.box(-5000, -5000, -700, 5000)),
        "绮春园": garden.get("Qichun Yuan") or unary_union([g for k, g in scenes.items() if k.startswith("QC")]).buffer(30),
    }
    hills = list(csv.DictReader(open(ROOT / "research/terrain/hills_heights.csv", encoding="utf-8")))
    hl = {f["properties"]["id"]: xz(f["geometry"]) for f in layer("hills_1860")}
    rep = json.load(open(ROOT / "research/terrain/ground_report.json", encoding="utf-8"))
    plain = json.load(open(ROOT / "research/terrain/plain.json", encoding="utf-8"))
    z = np.load(ROOT / "research/raw/dem/site_glo30.npz")
    dem = z["dem"].astype(float)
    lat = float(z["north"]) - np.arange(dem.shape[0]) * float(z["step"])
    lon = float(z["west"]) + np.arange(dem.shape[1]) * float(z["step"])
    LON, LAT = np.meshgrid(lon, lat)
    X, Z = to_xz(LON.ravel(), LAT.ravel())
    X, Z = X.reshape(dem.shape), Z.reshape(dem.shape)
    from scipy import ndimage
    low = ndimage.percentile_filter(dem, 20, size=7, mode="nearest")
    P = plain["a"] + plain["bx"] * X / 1000 + plain["bz"] * Z / 1000
    levels = {}
    for r in csv.DictReader(open(ROOT / "research/terrain/water_levels.csv", encoding="utf-8")):
        levels[r["body"]] = float(r["level_m_egm2008"])
    meta = json.load(open(ROOT / "site/reconstruction/generated/ground.json", encoding="utf-8"))
    water = {b["i"]: b for b in meta["bodies"]}
    wfe = {f["properties"]["id"]: xz(f["geometry"]).buffer(0) for f in layer("water_1860")}
    print("| Region | Hills (plan + generated) | By method | Median height, error | Water levels | Plain: DEM low ground minus the plane |")
    print("|---|---|---|---|---|---|")
    for name, g in regions.items():
        if g is None or g.is_empty:
            continue
        hs = [h for h in hills if h["id"] in hl and g.contains(hl[h["id"]].representative_point())]
        m = Counter(h["method"] for h in hs)
        est = [float(h["height_est_m"]) for h in hs]
        err = [float(h["error_m"]) for h in hs]
        lv = sorted({round(b["level"] + DATUM_M, 2) for b in meta["bodies"] if any(i in wfe and g.intersects(wfe[i]) for i in b["ids"])})
        inside = shapely.contains_xy(g, X, Z)
        res = (low - P)[inside]
        plan_n = sum(1 for h in hs if h["basis"] == "plan")
        print(f"| {name} | {plan_n} + {len(hs) - plan_n} | {', '.join(f'{k} {v}' for k, v in sorted(m.items()))} | {np.median(est) if est else 0:.1f} m, ±{np.median(err) if err else 0:.1f} m | "
              f"{(str(lv[0]) + '-' + str(lv[-1]) + ' m (' + str(len(lv)) + ')') if lv else '-'} | rms {np.sqrt(np.mean(res ** 2)):.2f} m, p90 {np.percentile(np.abs(res), 90):.2f} m |")


def Polygon_of(f):
    from shapely.geometry import Polygon
    return Polygon(xz(f["geometry"]).coords).buffer(0)


if __name__ == "__main__":
    main()
