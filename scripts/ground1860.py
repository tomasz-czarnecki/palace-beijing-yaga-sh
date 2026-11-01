"""The ground of the 3D view: land cut exactly to the water layer, with hills as soft mounds; flat water; paddy; banks.

  uv run python scripts/ground1860.py

Reads research/layers (water, fields, islands, hills, bridges, walls). Writes site/reconstruction/generated/:
  ground.json        the frame, the levels, offsets into ground.bin, the grid's size
  ground.bin         little-endian: for each part (land, bank, water, paddy) positions f32 x,y,z and indices u32; land also has rgb u8
  ground_grid.i16    5 m raster, cm above the datum, -32768 where water stands (bridges count as land): walk mode, boxes1860.py

Not a survey of 1860. Levels are constants in scene1860.py. No height comes from the DEM cell by cell: research/terrain/README.md says it can't tell (trees, modern fill).
"""

import json
import sys
from pathlib import Path

import numpy as np
import shapely
from scipy import ndimage
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box, shape
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scene1860 import DATUM_M, GENERATED, GROUND_M, WATER_M, layer, lonlat_affine, params, to_lonlat, to_xz  # noqa: E402

MARGIN_M = 320  # land modelled round the walls
CELL_M = 15  # land mesh
GRID_M = 5  # height raster
SIMPLIFY_M = 0.4  # the traced shore is pixel-stepped; below any reading of the plan (±10-75 m, Q7)
ISLAND_RISE_M = 0.8  # islands as raised ground: no number found, a guess, C
ISLAND_RISE_OVER_M = 25  # over how many metres from the shore it comes up
PADDY_DROP_M = 0.25  # 稻田 below the land, C
HILL_SLOPE_LIMIT = 0.8  # height at most this x half-width + 0.5 m: hills_1860 estimates run high on small outlines (research/terrain/README.md "mostly snapped to a residual peak")
BRIDGE_WALK_M = 6  # walkable width burned into the raster: wider than the 3 m deck (params.json other.bridge) so a 5 m cell can't miss it
BANK_BELOW_M = 0.3  # the bank goes this far under the water
XY12 = {"lat": 40.012211, "lon": 116.308173, "d": 42, "h": 8}  # 线法山 mound, params.json xiyang_lou XY12: the plan's outer ring at local scale, 42 m; 8 m in S310 (search extract), plate 18 7.4 m; C. Position from buildings.csv


def xz_geom(geom):
    return shapely.transform(geom, lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1])))


def polys(geom):
    if geom.is_empty:
        return []
    if isinstance(geom, Polygon):
        return [geom]
    return [g for g in getattr(geom, "geoms", []) if isinstance(g, Polygon) and g.area > 0]


class Mesh:
    def __init__(self, level=None):
        self.key, self.pos, self.idx, self.level = {}, [], [], level

    def v(self, x, z):
        k = (round(x * 100), round(z * 100))
        if k not in self.key:
            self.key[k] = len(self.pos)
            self.pos.append((x, z))
        return self.key[k]

    def tri(self, a, b, c):
        ia, ib, ic = self.v(*a), self.v(*b), self.v(*c)
        if ia in (ib, ic) or ib == ic:
            return
        # Upward normals: y up, x east, z south, so counter-clockwise from above in (x, z) reads clockwise.
        if (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) > 0:
            ib, ic = ic, ib
        self.idx += [ia, ib, ic]

    def cdt(self, poly):
        for t in shapely.constrained_delaunay_triangles(poly).geoms:
            p = list(t.exterior.coords)
            self.tri(p[0], p[1], p[2])


def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def mask_of(poly, xs, zs):
    """Boolean raster of a polygon on the grid, working only inside its bounds."""
    out = np.zeros((len(zs), len(xs)), bool)
    x0, z0, x1, z1 = poly.bounds
    i0, i1 = np.searchsorted(xs, x0), np.searchsorted(xs, x1)
    j0, j1 = np.searchsorted(zs, z0), np.searchsorted(zs, z1)
    if i1 > i0 and j1 > j0:
        gx, gz = np.meshgrid(xs[i0:i1], zs[j0:j1])
        out[j0:j1, i0:i1] = shapely.contains_xy(poly, gx, gz)
    return out


def main():
    water_all = [xz_geom(shape(f["geometry"])).buffer(0) for f in layer("water_1860")]
    fields_all = [xz_geom(shape(f["geometry"])).buffer(0) for f in layer("fields_1860")]
    wall_lines = [xz_geom(shape(f["geometry"])) for f in layer("walls_1860") if f["geometry"]["type"] == "LineString"]
    wx0, wz0, wx1, wz1 = unary_union(wall_lines).bounds
    x0, z0 = np.floor((wx0 - MARGIN_M) / CELL_M) * CELL_M, np.floor((wz0 - MARGIN_M) / CELL_M) * CELL_M
    x1, z1 = np.ceil((wx1 + MARGIN_M) / CELL_M) * CELL_M, np.ceil((wz1 + MARGIN_M) / CELL_M) * CELL_M
    domain = box(x0, z0, x1, z1)
    water = unary_union(water_all).intersection(domain).simplify(SIMPLIFY_M).buffer(0)
    paddy = unary_union(fields_all).intersection(domain).simplify(SIMPLIFY_M).buffer(0).difference(water).buffer(0)
    holes = unary_union([water, paddy]).buffer(0)

    # Inside the wall rings: a tone of the land's colour, so the gardens read from far off.
    garden = unary_union([Polygon(xz_geom(shape(f["geometry"])).coords).buffer(0) for f in layer("walls_1860") if f["properties"]["kind"] == "outer_wall"])

    # Height raster.
    xs = np.arange(x0, x1 + GRID_M, GRID_M)
    zs = np.arange(z0, z1 + GRID_M, GRID_M)
    h = np.zeros((len(zs), len(xs)))  # above base land
    rise = np.zeros_like(h)
    for f in layer("islands_1860"):
        for p in polys(xz_geom(shape(f["geometry"])).buffer(0)):
            m = mask_of(p, xs, zs)
            if m.any():
                d = ndimage.distance_transform_edt(m) * GRID_M
                rise = np.maximum(rise, ISLAND_RISE_M * smooth(d / ISLAND_RISE_OVER_M))
    capped = 0
    mounds = []
    for f in layer("hills_1860"):
        for p in polys(xz_geom(shape(f["geometry"])).buffer(0)):
            mounds.append((p, f["properties"]["height_est_m"]))
    cx, cz = to_xz(XY12["lon"], XY12["lat"])
    mounds.append((Point(cx, cz).buffer(XY12["d"] / 2, 32), XY12["h"]))
    hill = np.zeros_like(h)
    for p, height in mounds:
        # A mound on a raster finer than its smallest cell: pad the mask once so a small outline still rasters.
        m = mask_of(p.buffer(GRID_M / 2), xs, zs)
        if not m.any():
            continue
        d = ndimage.distance_transform_edt(m) * GRID_M
        half = d.max()
        use = min(height, HILL_SLOPE_LIMIT * half + 0.5)
        capped += use < height
        hill = np.maximum(hill, use * smooth(d / half))
    h = rise + hill

    g = h + GROUND_M - DATUM_M  # y of the land surface
    lookup = lambda x, z: float(ndimage.map_coordinates(g, [[(z - z0) / GRID_M], [(x - x0) / GRID_M]], order=1, mode="nearest")[0])

    # Land mesh: grid cells, cut only where the water or paddy crosses them.
    nx, nz = int((x1 - x0) / CELL_M), int((z1 - z0) / CELL_M)
    cells = np.array([box(x0 + i * CELL_M, z0 + j * CELL_M, x0 + (i + 1) * CELL_M, z0 + (j + 1) * CELL_M) for j in range(nz) for i in range(nx)])
    parts = polys(holes)
    tree = shapely.STRtree(parts)
    hits = tree.query(cells, predicate="intersects")
    touched = np.zeros(len(cells), bool)
    touched[hits[0]] = True
    land = Mesh()
    for c, t in zip(cells, touched):
        bx0, bz0, bx1, bz1 = c.bounds
        if not t:
            land.tri((bx0, bz0), (bx1, bz0), (bx1, bz1))
            land.tri((bx0, bz0), (bx1, bz1), (bx0, bz1))
    by_cell = {}
    for i, j in zip(*hits):
        by_cell.setdefault(int(i), []).append(int(j))
    for i, js in by_cell.items():
        piece = cells[i].difference(unary_union([parts[j] for j in js]))
        for p in polys(piece):
            land.cdt(p)

    # Banks: every land edge used by one triangle only, away from the domain's edge.
    count = {}
    pos = land.pos
    for k in range(0, len(land.idx), 3):
        tri = land.idx[k:k + 3]
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            e = (min(a, b), max(a, b))
            count[e] = count.get(e, 0) + 1
    y_land = np.array([lookup(px, pz) for px, pz in pos])
    bank_pos, bank_idx = [], []
    for (a, b), n in count.items():
        if n != 1:
            continue
        (ax, az), (bx, bz) = pos[a], pos[b]
        if (ax in (x0, x1) and bx == ax) or (az in (z0, z1) and bz == az):
            continue
        k = len(bank_pos)
        bank_pos += [(ax, y_land[a], az), (bx, y_land[b], bz), (bx, -BANK_BELOW_M, bz), (ax, -BANK_BELOW_M, az)]
        bank_idx += [k, k + 1, k + 2, k, k + 2, k + 3]  # DoubleSide in the view: which way a bank faces is not worked out here

    water_mesh = Mesh()
    for p in polys(water):
        water_mesh.cdt(p)
    paddy_mesh = Mesh()
    for p in polys(paddy):
        paddy_mesh.cdt(p)

    # Colours of the land: plain outside the gardens, greener inside, darker green with height. Small seeded noise so large flats aren't one colour.
    rng = np.random.default_rng(1860)
    px = np.array([p[0] for p in pos])
    pz = np.array([p[1] for p in pos])
    inside = shapely.contains_xy(garden, px, pz).astype(float)
    t_hill = np.clip((y_land - (GROUND_M - DATUM_M) - ISLAND_RISE_M) / 6, 0, 1)
    rgb = np.empty((len(pos), 3))
    outside_c, inside_c, hill_c = np.array([170, 164, 124.0]), np.array([137, 152, 98.0]), np.array([86, 116, 70.0])
    noise = rng.normal(0, 1.2, len(pos)) * inside
    for k in range(3):
        rgb[:, k] = (outside_c[k] * (1 - inside) + inside_c[k] * inside) * (1 - t_hill) + hill_c[k] * t_hill + noise
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)

    # The raster for walking and for the boxes: water marked, bridges walkable.
    grid = np.round(g * 100).astype(np.int16)
    grid_water = np.zeros_like(grid, bool)
    for p in polys(water):
        grid_water |= mask_of(p, xs, zs)
    for f in layer("bridges_1860"):
        line = xz_geom(shape(f["geometry"]))
        grid_water &= ~mask_of(line.buffer(BRIDGE_WALK_M / 2), xs, zs)
    grid[grid_water] = -32768

    GENERATED.mkdir(parents=True, exist_ok=True)
    grid.astype("<i2").tofile(GENERATED / "ground_grid.i16")

    def pack(out, mesh_pos, idx, rgb_arr=None):
        arr = np.asarray(mesh_pos, "<f4")
        ind = np.asarray(idx, "<u4")
        entry = {"pos": out["n"], "verts": len(arr)}
        out["buf"].append(arr.tobytes()); out["n"] += arr.nbytes
        entry["idx"] = out["n"]; entry["indices"] = len(ind)
        out["buf"].append(ind.tobytes()); out["n"] += ind.nbytes
        if rgb_arr is not None:
            entry["rgb"] = out["n"]
            b = rgb_arr.tobytes() + b"\0" * (-rgb_arr.nbytes % 4)
            out["buf"].append(b); out["n"] += len(b)
        return entry

    out = {"buf": [], "n": 0}
    parts_meta = {
        "land": pack(out, [(p[0], y, p[1]) for p, y in zip(pos, y_land)], land.idx, rgb),
        "bank": pack(out, bank_pos, bank_idx),
        "water": pack(out, [(p[0], 0.0, p[1]) for p in water_mesh.pos], water_mesh.idx),
        "paddy": pack(out, [(p[0], GROUND_M - DATUM_M - PADDY_DROP_M, p[1]) for p in paddy_mesh.pos], paddy_mesh.idx),
    }
    (GENERATED / "ground.bin").write_bytes(b"".join(out["buf"]))
    aff = lonlat_affine()
    meta = {
        "frame": "x east, z south, y above datum, metres; UTM 50N minus origin",
        "datum_m": DATUM_M, "ground_m": GROUND_M, "water_m": WATER_M, "lonlat": aff,
        "domain": [x0, z0, x1, z1], "parts": parts_meta,
        "grid": {"x0": float(xs[0]), "z0": float(zs[0]), "step_m": GRID_M, "width": len(xs), "height": len(zs), "no_land": -32768},
    }
    (GENERATED / "ground.json").write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")

    # Checks.
    worst = 0.0
    for lon, lat in [(116.281, 39.994), (116.315, 40.0147), (116.281, 40.0147), (116.315, 39.994), (116.30, 40.005)]:
        x, z = to_xz(lon, lat)
        ax = aff["x"][0] + aff["x"][1] * (lon - aff["lon0"]) + aff["x"][2] * (lat - aff["lat0"])
        az = aff["z"][0] + aff["z"][1] * (lon - aff["lon0"]) + aff["z"][2] * (lat - aff["lat0"])
        worst = max(worst, abs(x - ax), abs(z - az))
    print(f"domain {x1 - x0:.0f} x {z1 - z0:.0f} m; water {water.area / 1e4:.1f} ha (layer {sum(w.area for w in water_all) / 1e4:.1f}), paddy {paddy.area / 1e4:.1f} ha")
    print(f"land {len(pos)} verts, {len(land.idx) // 3} tris; bank {len(bank_idx) // 3}; water {len(water_mesh.pos)} verts, {len(water_mesh.idx) // 3} tris; paddy {len(paddy_mesh.idx) // 3}; ground.bin {out['n'] / 1e6:.2f} MB")
    print(f"{len(mounds)} mounds, {capped} capped by the slope limit; highest {g.max() - (GROUND_M - DATUM_M):.1f} m above base land; browser's lon/lat fit worst {worst:.3f} m at the corners")


if __name__ == "__main__":
    main()
