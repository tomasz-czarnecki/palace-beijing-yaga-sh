"""What the 30 m DEM (S04) can give the ground of 1860: the plain's slope, today's lake surfaces, and today's rises above the local ground. Needs research/raw/dem/.

  uv run python scripts/terrain_dem.py        (after clip_dem.py)

Reads research/raw/dem/site_glo30.npz (clip_dem.py), research/layers/osm_today.geojson (today's water), research/layers/water_1860.geojson.
Writes, small and committed, so the later steps run without research/raw/:
  research/terrain/plain.json       the plain as a plane through the low ground (EGM2008), its fall and direction; today's lake surfaces
  research/terrain/glo30_rise.npz   per DEM cell: today's height above the local low ground, decimetres (int16; -32768 = water today or no data)
The rise holds trees and modern fill as well as hills (research/terrain/README.md): scripts/hills1860.py reads it with a canopy allowance and a floor.
"""

import json
import sys
from pathlib import Path

import numpy as np
import shapely
from scipy import ndimage
from shapely.geometry import shape
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scene1860 import ROOT, layer, to_xz  # noqa: E402

DEM = ROOT / "research/raw/dem/site_glo30.npz"
OUT = ROOT / "research/terrain"
LOW_WINDOW = 7  # cells (about 210 m N-S, 170 m E-W): the low envelope takes the 20th percentile in this window
LOW_PCT = 20
BASE_SIGMA = 1.5  # cells: the low envelope smoothed into the local base
WATER_BUFFER_M = 12  # DEM cells this near today's water are left out of the plain fit (the bank and the edited lake edge)
NO = -32768


def today_water():
    out = []
    for f in layer("osm_today"):
        p, g = f["properties"], f["geometry"]
        if g["type"] not in ("Polygon", "MultiPolygon"):
            continue
        if p.get("natural") == "water" or p.get("water") or p.get("landuse") in ("reservoir", "basin"):
            out.append(shapely.transform(shape(g), lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1]))).buffer(0))
    return unary_union(out)


def main():
    z = np.load(DEM)
    dem = z["dem"].astype(float)
    north, west, step = float(z["north"]), float(z["west"]), float(z["step"])
    rows, cols = dem.shape
    lat = north - np.arange(rows) * step  # cell centres: RasterPixel.IsPoint (research/terrain/README.md)
    lon = west + np.arange(cols) * step
    LON, LAT = np.meshgrid(lon, lat)
    X, Z = to_xz(LON.ravel(), LAT.ravel())
    X, Z = X.reshape(dem.shape), Z.reshape(dem.shape)

    water = today_water()
    wet = shapely.contains_xy(water, X, Z)
    near = shapely.contains_xy(water.buffer(WATER_BUFFER_M), X, Z)
    walls = unary_union([shapely.transform(shape(f["geometry"]), lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1]))) for f in layer("walls_1860") if f["properties"]["kind"] == "outer_wall"])
    x0, z0, x1, z1 = walls.bounds
    inside = (X > x0 - 200) & (X < x1 + 200) & (Z > z0 - 200) & (Z < z1 + 200)

    # The low envelope: trees and hills stand above it, open ground lies near it.
    filled = np.where(wet, np.inf, dem)
    low = ndimage.percentile_filter(filled, LOW_PCT, size=LOW_WINDOW, mode="nearest")
    low[~np.isfinite(low)] = np.nan
    use = inside & ~near & np.isfinite(low)
    A = np.column_stack([np.ones(use.sum()), X[use] / 1000, Z[use] / 1000])
    y = low[use]
    keep = np.ones(len(y), bool)
    for _ in range(5):
        coef, *_ = np.linalg.lstsq(A[keep], y[keep], rcond=None)
        res = y - A @ coef
        s = res[keep].std()
        keep = np.abs(res) < 2 * s
    a, bx, bz = (float(c) for c in coef)  # y = a + bx * x_km + bz * z_km; z runs south
    fall = float(np.hypot(bx, bz))  # m per km
    # Direction of the fall: towards decreasing height. In (east, north): (-bx, +bz), since north = -z.
    az = float(np.degrees(np.arctan2(-bx, bz)) % 360)

    base = ndimage.gaussian_filter(np.where(np.isfinite(low), low, np.nanmedian(low)), BASE_SIGMA)
    rise = dem - base
    rise_dm = np.round(rise * 10).astype(np.int16)
    rise_dm[wet] = NO

    lakes = []
    for f in layer("water_1860"):
        p = f["properties"]
        if p["area_m2"] < 15000:
            continue
        g = shapely.transform(shape(f["geometry"]), lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1]))).buffer(0)
        m = shapely.contains_xy(g, X, Z) & wet
        if m.sum() >= 5:
            lakes.append({"id": p["id"], "name_zh": p["name_zh"], "cells": int(m.sum()), "median_m": round(float(np.median(dem[m])), 2), "p10_m": round(float(np.percentile(dem[m], 10)), 2), "p90_m": round(float(np.percentile(dem[m], 90)), 2), "x": round(g.centroid.x), "z": round(g.centroid.y)})
    # Today's lakes along the plain's fall: does the water fall the same way?
    if len(lakes) >= 3:
        L = np.array([[1, q["x"] / 1000, q["z"] / 1000] for q in lakes])
        lc, *_ = np.linalg.lstsq(L, np.array([q["median_m"] for q in lakes]), rcond=None)
        lake_fall = {"per_km": round(float(np.hypot(lc[1], lc[2])), 2), "towards_deg": round(float(np.degrees(np.arctan2(-lc[1], lc[2])) % 360)), "n": len(lakes)}
    else:
        lake_fall = None

    OUT.mkdir(parents=True, exist_ok=True)
    plain = {
        "what": "the plain as a plane through the DEM's low envelope (20th percentile in 7 x 7 cells), open ground inside the walls and 200 m round, more than 12 m from today's water; EGM2008. Today's surface: trees lifted, modern fill kept (research/terrain/README.md)",
        "sources": "S04;S159;S03",
        "y_m": "a + bx * x_km + bz * z_km (scene frame: x east, z south, km from the origin of scene1860.py)",
        "a": round(a, 3), "bx": round(bx, 4), "bz": round(bz, 4),
        "fall_m_per_km": round(fall, 3), "falls_towards_deg": round(az, 1),
        "fit_cells": int(keep.sum()), "rms_m": round(float(res[keep].std()), 2),
        "at_origin_m": round(a, 2),
        "lakes_today": lakes, "lakes_fall_today": lake_fall,
    }
    (OUT / "plain.json").write_text(json.dumps(plain, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    np.savez_compressed(OUT / "glo30_rise.npz", rise_dm=rise_dm, north=north, west=west, step=step)
    print(f"plain: {a:.2f} m at the origin, falls {fall:.2f} m/km towards {az:.0f} deg, fit on {keep.sum()} cells, rms {res[keep].std():.2f} m")
    print(f"today's lakes: {[(q['name_zh'] or q['id'], q['median_m']) for q in lakes]}; their fall {lake_fall}")
    land = rise[~wet & inside]
    print(f"rise over land inside: p50 {np.percentile(land, 50):.2f}, p90 {np.percentile(land, 90):.2f}, p99 {np.percentile(land, 99):.2f}, max {land.max():.2f} m")


if __name__ == "__main__":
    main()
