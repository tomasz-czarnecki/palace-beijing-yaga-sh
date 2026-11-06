"""The ground of the 3D view (Round 10): the plain, the water at one level per body, lakebeds and banks, the hills, and flat pads under the halls.

  uv run python scripts/ground1860.py        (after hills1860.py; reads the box layout of boxes1860.py, which does not depend on the ground)

Reads research/layers (water, fields, hills, bridges, walls), research/terrain/plain.json (the plain, from the DEM: terrain_dem.py), research/terrain/readings.csv
(the shores' kinds), research/xiyanglou/boxes.csv (the sunken court). Writes site/reconstruction/generated/:
  ground.json        the frame, the plain, the water bodies with their levels and depths, the bridges' decks, offsets into ground.bin
  ground.bin         little-endian parts: land (x,y,z f32, indices u32, rgb u8, code u8, y without the assumed hills i16 cm), skirt (banks and steps, rgb u8), bed, water, paddy, court
  ground_grid.i16    2.5 m lattice, the surface one walks on, rasterised from the land mesh: cm above the datum; water -20000 + the bed in cm; bridge decks as land
  ground_level.u8    10 m cells: 1 + the index of the water body (ground.json bodies), 0 where there is none: the level for boats and landings
and research/terrain/water_levels.csv (one row per body), research/terrain/ground_report.json (what the run measured: hills as modelled, banks by kind, the mesh against the raster).

Levels (all C): the plain is the DEM's low envelope as a plane (research/terrain/plain.json). Each water body (water polygons touching within 1 m) lies FREEBOARD_M under the
plain along its own shore; near the water the land is pulled to that freeboard, far from it the plain rules. Beds 1.5-2.3 m down (research/terrain/readings.csv, the water worker).
Banks: an earth slope by default (the album: low grass banks 0.4-0.8 m); stone where a hall or a landing meets the water, and where a leaf or a text says stone or rock for that scene and side.
Hills: research/layers/hills_1860 (heights: hills1860.py), each piece of land one smooth mound, its peak limited by its width. Pads: the halls of one compound on one level, blended out.
"""

import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import shapely
from scipy import ndimage
from scipy.spatial import cKDTree
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box, shape
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scene1860 import DATUM_M, GENERATED, GROUND_M, GROUND_ROOT_M, GROUND_STEP_M, ROOT, WATER_M, ground_frame, layer, lonlat_affine, raster_mask, to_lonlat, to_xz  # noqa: E402

STEP = GROUND_STEP_M
TERRAIN = ROOT / "research/terrain"
SIMPLIFY_M = 0.4  # the traced shore is pixel-stepped; below any reading of the plan (±10-75 m, Q7)
FREEBOARD_M = 1.5  # land above the water near the shore: between the album's bank tops (0.4-1.5 m) and today's 2-5 m step (research/terrain/README.md). C
FREEBOARD_BLEND_M = 60  # beyond this from the water the plain rules
EARTH_RAMP_M = 10.0  # an earth bank rises from the waterline to the land over this: 0.4-0.8 m at 3-5 m from the edge, as the album's low grass banks
ROCK_RAMP_M, STONE_RAMP_M = 6.0, 4.0
TOP = {"earth": 0.05, "rock": 0.8, "stone": 0.9}  # the land's edge above the water: rock 0.8 m (album: YM05, YM07 0.8 m), stone at least 0.9 m. C
EDGE = {"earth": 0.10, "rock": 0.6, "stone": 1.0}  # the bed at the edge below the water. An earth bank has no skirt: the 0.15 m between its edge and the bed lies under the water surface, which meets the land at the shore
BED_RAMP_M = 8.0
DEPTH = {"福海": 2.3}  # m: 福海 about 2.3 usually, 3.8 at its deepest (1997 dredging; S1002, snippet; R10 water rows); 后湖 about 2, channels about 2, 长春园 and 绮春园 1.8-2.2
DEPTH_DEFAULT, DEPTH_SMALL, SMALL_M2 = 2.0, 1.5, 3000
HILL_SLOPE = 0.45  # a hill's peak at most this x its half-width + 0.3 m: smoothstep flanks then reach about 34 degrees, an earth hill's steepest. C
HILL_BLEND_SIGMA_M = 8.0
NEAR_BOX_M, NEAR_LANDING_M = 3.0, 6.0  # a shore this near a hall or a landing is stone: the album draws dressed stone under halls and terraces at the water; Attiret: cut-stone quays where galleries and paths end (S911)
PAD_GAP_M = 4.0  # boxes nearer than this share one pad (one court level)
PAD_APRON_M = 1.5
PAD_BLEND_M = 6.0
PAD_MIN_ABOVE_M = 0.4  # a pad at least this above the nearest water
PADDY_DROP_M = 0.25  # 稻田 below the land, C
COURT_DROP_M = 1.30  # 大水法's sunken fountain area: "1.30 m below the gardens" (S603, survey; research/xiyanglou/boxes.csv XY10). Q71
COURT_HILL_CLEAR_M = 5.0
XY12 = {"lat": 40.012211, "lon": 116.308173, "d": 42}  # 线法山: the plan's outer ring at local scale, 42 m (params.json XY12); its height is H0030's (hills1860.py: the park's 8 m, S1000)
TOL_M = 0.20  # a mesh cell is split while the raster departs from its corners' plane by more than this
TOL_BED_M = 0.60
BED_MAX_LEVEL = 1  # under open water the bed needs no cell finer than 10 m
CHUNK = 65535  # vertices per chunk: 16-bit indices
WALK_MARGIN_M = 30  # the walk raster covers walls, boxes and ways plus this; past it the plain
MAX_LEVEL = 2  # 20 m root cells down to 5 m
CUT_MIN_LEVEL = 1  # cells the shore crosses are at most 10 m
WATER_BASE = -20000  # ground_grid.i16: water cells hold this + the bed in cm
NO_DATA = -32768
LEVEL_CELL_M = 10.0
BRIDGE_WALK_M = 6  # the walkable strip burned into the raster: wider than the 3 m deck (params.json other.bridge)
BRIDGE_HUMP_M = 0.8  # deck above its ends at mid span. Guess, C
BRIDGE_ON_LAND = 0.05  # a deck on land lies this above the ground
CODES = {"level": 0, "hill_b": 1, "hill_c": 2, "hill_assumed": 3, "bank_stone": 4, "bank_rock": 5}


def xz_geom(geom):
    return shapely.transform(geom, lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1])))


def polys(geom):
    if geom.is_empty:
        return []
    if isinstance(geom, Polygon):
        return [geom]
    return [g for g in getattr(geom, "geoms", []) if isinstance(g, Polygon) and g.area > 0]


def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def bilinear(arr, x0, z0, x, z):
    u = np.clip((np.asarray(x) - x0) / STEP, 0, arr.shape[1] - 1.0001)
    v = np.clip((np.asarray(z) - z0) / STEP, 0, arr.shape[0] - 1.0001)
    i, j = np.floor(u).astype(int), np.floor(v).astype(int)
    a, b = u - i, v - j
    return (arr[j, i] * (1 - a) + arr[j, i + 1] * a) * (1 - b) + (arr[j + 1, i] * (1 - a) + arr[j + 1, i + 1] * a) * b


def fill_from(mask_keep, arr):
    """arr where mask_keep, else the value of the nearest cell where mask_keep."""
    idx = ndimage.distance_transform_edt(~mask_keep, return_distances=False, return_indices=True)
    return arr[idx[0], idx[1]]


def courts():
    out = []
    for r in csv.DictReader(open(ROOT / "research/xiyanglou/boxes.csv", encoding="utf-8", newline="")):
        if r["shape"] != "court":
            continue
        cx, cz = to_xz(float(r["lon"]), float(r["lat"]))
        t = math.radians(float(r["orientation_deg"]))
        fx, fz = math.sin(t), -math.cos(t)
        ax, az = math.cos(t), math.sin(t)
        hf, hd = float(r["frontage_m"]) / 2, float(r["depth_m"]) / 2
        out.append((r["building_id"], Polygon([(float(cx) + sa * ax * hf + sb * fx * hd, float(cz) + sa * az * hf + sb * fz * hd) for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1))])))
    return out


def plain_fn():
    p = json.load(open(TERRAIN / "plain.json", encoding="utf-8"))
    return p, (lambda x, z: p["a"] + p["bx"] * np.asarray(x) / 1000 + p["bz"] * np.asarray(z) / 1000 - DATUM_M)


# ---- shores -------------------------------------------------------------------------------------------------

COMPASS = {"north-east": 45, "north-west": 315, "south-east": 135, "south-west": 225, "north": 0, "east": 90, "south": 180, "west": 270}


def bearing_word(text):
    import re
    t = (text or "").lower()
    for w, deg in COMPASS.items():
        if re.search(rf"\b{w}\b", t):
            return deg
    return None


def shore_rules():
    """Scene rows of research/terrain/readings.csv that set a shore's kind: (scene, kind, top, bearing or None, reading id, grade)."""
    out = []
    for r in csv.DictReader(open(TERRAIN / "readings.csv", encoding="utf-8", newline="")):
        if r["kind"] != "bank" or not r["scene_id"] or r["scene_id"].startswith("GARDEN") or r["state_date"].startswith(("19", "20")) and "modern" in r["value_text"]:
            continue
        v = r["value_text"].lower()
        kind = "rock" if v.startswith("rock") else "stone" if v.startswith("stone") else "earth" if v.startswith("earth") else None
        if kind is None:
            continue
        try:
            top = float(r["value_m"]) if r["value_m"] else None
        except ValueError:
            top = None
        for s in r["scene_id"].split(";"):
            out.append((s, kind, top, bearing_word(r["where"]), r["id"], r["grade"]))
    return out


# ---- the quadtree mesh --------------------------------------------------------------------------------------

class Mesh:
    def __init__(self):
        self.key, self.pos, self.idx = {}, [], []

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
        area = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        if abs(area) < 1e-6:
            return
        # Upward normals: y up, x east, z south, so counter-clockwise from above in (x, z) reads clockwise.
        if area > 0:
            ib, ic = ic, ib
        self.idx += [ia, ib, ic]

    def poly(self, p):
        for t in shapely.constrained_delaunay_triangles(p).geoms:
            q = list(t.exterior.coords)
            self.tri(q[0], q[1], q[2])

    def fan(self, pts):
        """A convex ring (no repeat) from its centre."""
        cx = sum(p[0] for p in pts) / len(pts)
        cz = sum(p[1] for p in pts) / len(pts)
        for a, b in zip(pts, pts[1:] + pts[:1]):
            self.tri((cx, cz), a, b)


def build_quadtree(x0, z0, nx, nz, land_r, bed_r, holes_prepared, holes):
    """Leaves (level, i, j) of a quadtree over root cells of GROUND_ROOT_M, refined by the raster's departure from a plane, 2:1 balanced; cells the holes cross are never coarser than a neighbour."""
    R = GROUND_ROOT_M
    fine = 2 ** MAX_LEVEL
    lvl = np.zeros((nz * fine, nx * fine), np.int8)  # level of the leaf covering each finest cell
    cut_cache = {}

    def size(l):
        return R / 2 ** l

    def bounds(l, i, j):
        s = size(l)
        return x0 + i * s, z0 + j * s, x0 + (i + 1) * s, z0 + (j + 1) * s

    def cut(l, i, j):
        k = (l, i, j)
        if k not in cut_cache:
            b = box(*bounds(l, i, j))
            if not shapely.intersects(holes_prepared, b):
                cut_cache[k] = 0  # all land
            elif shapely.contains(holes_prepared, b):
                cut_cache[k] = 2  # all hole
            else:
                cut_cache[k] = 1
        return cut_cache[k]

    def deviates(l, i, j):
        n = 2 ** (MAX_LEVEL - l)
        c = cut(l, i, j)
        if c == 2 and l >= BED_MAX_LEVEL:
            return False
        arr, tol = (bed_r, TOL_BED_M) if c == 2 else (land_r, TOL_M)
        sub = arr[j * n:(j + 1) * n + 1, i * n:(i + 1) * n + 1]
        if sub.shape != (n + 1, n + 1):
            return False
        a, b = np.meshgrid(np.linspace(0, 1, n + 1), np.linspace(0, 1, n + 1))
        plane = (sub[0, 0] * (1 - a) + sub[0, -1] * a) * (1 - b) + (sub[-1, 0] * (1 - a) + sub[-1, -1] * a) * b
        return float(np.abs(sub - plane).max()) > tol

    leaves = {(0, i, j) for j in range(nz) for i in range(nx)}
    work = list(leaves)
    while work:
        nxt = []
        for k in work:
            l, i, j = k
            if l >= MAX_LEVEL:
                continue
            if (l < CUT_MIN_LEVEL and cut(l, i, j) == 1) or deviates(l, i, j):
                leaves.discard(k)
                kids = [(l + 1, 2 * i + a, 2 * j + b) for b in (0, 1) for a in (0, 1)]
                leaves.update(kids)
                nxt += kids
        work = nxt

    def paint():
        for (l, i, j) in leaves:
            n = 2 ** (MAX_LEVEL - l)
            lvl[j * n:(j + 1) * n, i * n:(i + 1) * n] = l

    paint()
    H, W = lvl.shape

    def neighbour_max(l, i, j):
        n = 2 ** (MAX_LEVEL - l)
        r0, r1, c0, c1 = j * n, (j + 1) * n, i * n, (i + 1) * n
        out = []
        out.append(lvl[r0 - 1, c0:c1].max() if r0 > 0 else -1)  # north (z smaller)
        out.append(lvl[r1, c0:c1].max() if r1 < H else -1)  # south
        out.append(lvl[r0:r1, c0 - 1].max() if c0 > 0 else -1)  # west
        out.append(lvl[r0:r1, c1].max() if c1 < W else -1)  # east
        return out

    changed = True
    passes = 0
    while changed:
        changed = False
        passes += 1
        for k in list(leaves):
            l, i, j = k
            if l >= MAX_LEVEL:
                continue
            nb = max(neighbour_max(l, i, j))
            if nb > l + 1 or (cut(l, i, j) == 1 and nb > l):
                leaves.discard(k)
                n = 2 ** (MAX_LEVEL - l)
                for b in (0, 1):
                    for a in (0, 1):
                        leaves.add((l + 1, 2 * i + a, 2 * j + b))
                lvl[j * n:(j + 1) * n, i * n:(i + 1) * n] = l + 1
                changed = True
    return leaves, lvl, bounds, cut, neighbour_max, passes


def rasterise(pos2, ys, idx, x0, z0, w, h):
    """The mesh's height at every lattice point it covers (NaN elsewhere)."""
    out = np.full((h, w), np.nan)
    tri = np.asarray(idx).reshape(-1, 3)
    P = np.asarray(pos2)
    A, B, C = P[tri[:, 0]], P[tri[:, 1]], P[tri[:, 2]]
    ya, yb, yc = ys[tri[:, 0]], ys[tri[:, 1]], ys[tri[:, 2]]
    lo = np.floor((np.minimum(np.minimum(A, B), C) - [x0, z0]) / STEP - 1e-9).astype(int) + 1
    hi = np.floor((np.maximum(np.maximum(A, B), C) - [x0, z0]) / STEP + 1e-9).astype(int)
    lo = np.maximum(lo, 0)
    hi[:, 0] = np.minimum(hi[:, 0], w - 1)
    hi[:, 1] = np.minimum(hi[:, 1], h - 1)
    cnt = np.maximum(hi - lo + 1, 0)
    n = cnt[:, 0] * cnt[:, 1]
    t = np.repeat(np.arange(len(tri)), n)
    off = np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n)
    ci = lo[t, 0] + off % np.maximum(cnt[t, 0], 1)
    cj = lo[t, 1] + off // np.maximum(cnt[t, 0], 1)
    px, pz = x0 + ci * STEP, z0 + cj * STEP
    ax, az, bx, bz, cx, cz = A[t, 0], A[t, 1], B[t, 0], B[t, 1], C[t, 0], C[t, 1]
    det = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz)
    with np.errstate(divide="ignore", invalid="ignore"):
        l1 = ((bz - cz) * (px - cx) + (cx - bx) * (pz - cz)) / det
        l2 = ((cz - az) * (px - cx) + (ax - cx) * (pz - cz)) / det
    l3 = 1 - l1 - l2
    e = -1e-7
    ok = (l1 >= e) & (l2 >= e) & (l3 >= e) & np.isfinite(l1)
    out[cj[ok], ci[ok]] = l1[ok] * ya[t[ok]] + l2[ok] * yb[t[ok]] + l3[ok] * yc[t[ok]]
    return out


def main():
    import boxes1860  # the layout only: positions do not depend on the ground

    x0, z0, x1, z1 = ground_frame()
    xs, zs = np.arange(x0, x1 + STEP / 2, STEP), np.arange(z0, z1 + STEP / 2, STEP)
    W, Hn = len(xs), len(zs)
    X, Z = np.meshgrid(xs, zs)
    plain_meta, plain = plain_fn()
    P = plain(X, Z)
    domain = box(x0, z0, x1, z1)

    # Water bodies: polygons touching within 1 m.
    water_feats = [(f["properties"], xz_geom(shape(f["geometry"])).buffer(0)) for f in layer("water_1860")]
    water = unary_union([g for _, g in water_feats]).intersection(domain).simplify(SIMPLIFY_M).buffer(0)
    # Round 20: water outside the walls (`outside: true`) forms bodies of its own, never merged with the gardens' even where a canal meets a sluice.
    comps, comp_side = [], []
    for side in (False, True):
        feats_side = [g for p, g in water_feats if bool(p.get("outside")) == side]
        if feats_side:
            cs = polys(unary_union([g.buffer(0.5) for g in feats_side]))
            comps += cs
            comp_side += [side] * len(cs)
    tree = shapely.STRtree(comps)
    body_of = {}
    for p, g in water_feats:
        hit = [int(h) for h in tree.query(g.representative_point(), predicate="intersects") if comp_side[int(h)] == bool(p.get("outside"))]
        body_of[p["id"]] = hit[0] if hit else -1
    bodies = []
    for b, cg in enumerate(comps):
        members = [(p, g) for p, g in water_feats if body_of[p["id"]] == b]
        if not members:
            continue
        geom = unary_union([g for _, g in members]).buffer(0)
        ring = geom.boundary
        pts = [ring.interpolate(t, normalized=True) for t in np.linspace(0, 1, 64, endpoint=False)]
        level = float(np.median(plain(np.array([q.x for q in pts]), np.array([q.y for q in pts])))) - FREEBOARD_M
        given = [float(p["level_m"]) - DATUM_M for p, _ in members if p.get("level_m") not in (None, "")]
        if given:
            level = given[0]  # Round 20: a level the layer states (EGM2008 m), outside the walls only
        names = sorted({p["name_zh"] for p, _ in members if p["name_zh"]})
        area = sum(g.area for _, g in members)
        depth = next((DEPTH[n] for n in names if n in DEPTH), DEPTH_SMALL if area < SMALL_M2 else DEPTH_DEFAULT)
        bodies.append({"index": len(bodies), "comp": b, "ids": [p["id"] for p, _ in members], "names": names, "area_m2": round(area), "level": level, "depth": depth, "geom": geom})
    body_geom_tree = shapely.STRtree([b["geom"] for b in bodies])

    # Rasters of what is where.
    wet = raster_mask(water, xs, zs)
    body_r = np.full((Hn, W), -1, int)
    for b in bodies:
        m = raster_mask(b["geom"].intersection(domain), xs, zs) & wet
        if comp_side[b["comp"]]:
            m &= body_r < 0  # outside water never takes a cell of the gardens' water
        body_r[m] = b["index"]
    wet &= body_r >= 0
    levels = np.array([b["level"] for b in bodies])
    depths = np.array([b["depth"] for b in bodies])

    # Land base: the freeboard near the water, the plain far from it.
    dW, idxW = ndimage.distance_transform_edt(~wet, return_indices=True)
    dW *= STEP
    near_level = levels[body_r[idxW[0], idxW[1]]]
    t = smooth(dW / FREEBOARD_BLEND_M)
    N = (near_level + FREEBOARD_M) * (1 - t) + P * t

    # Hills.
    court_polys = courts()
    court_all = unary_union([c for _, c in court_polys]) if court_polys else Polygon()
    clear = court_all.buffer(COURT_HILL_CLEAR_M)
    hills = layer("hills_1860")
    groups = {}
    for f in hills:
        p = f["properties"]
        if p["id"] == "H0030":
            continue  # inside the 线法山 ring below
        g = xz_geom(shape(f["geometry"])).buffer(0)
        if g.intersects(clear):
            g = g.difference(clear)
        if g.is_empty:
            continue
        groups.setdefault(p.get("group") or p["id"], []).append((p, g))
    h30 = next(f["properties"] for f in hills if f["properties"]["id"] == "H0030")
    cx, cz = to_xz(XY12["lon"], XY12["lat"])
    groups["H0030"] = [(h30, Point(float(cx), float(cz)).buffer(XY12["d"] / 2, 32))]
    hill = np.zeros((Hn, W))
    hill_src = np.zeros((Hn, W))  # without the assumed hills
    hill_code = np.zeros((Hn, W), np.uint8)
    modelled = {}
    for gid, members in groups.items():
        geom = unary_union([g for _, g in members]).buffer(0)
        pad = geom.buffer(STEP / 2)
        m = raster_mask(pad, xs, zs) & ~wet
        if not m.any():
            continue
        jj, ii = np.nonzero(m)
        sl = (slice(max(jj.min() - 2, 0), jj.max() + 3), slice(max(ii.min() - 2, 0), ii.max() + 3))
        ms = m[sl]
        d = ndimage.distance_transform_edt(ms) * STEP
        half = d.max()
        Hf = np.zeros(ms.shape)
        lab = np.full(ms.shape, -1)
        for k, (p, g) in enumerate(members):
            mk = raster_mask(g.buffer(STEP / 2), xs[sl[1]], zs[sl[0]]) & ms
            Hf[mk] = p["height_est_m"]
            lab[mk] = k
        if (lab < 0).any() and (lab >= 0).any():
            fill = ndimage.distance_transform_edt(lab < 0, return_distances=False, return_indices=True)
            Hf = Hf[fill[0], fill[1]]
            lab = lab[fill[0], fill[1]]
        if len(members) > 1:
            s = HILL_BLEND_SIGMA_M / STEP
            Hf = ndimage.gaussian_filter(Hf * ms, s) / np.maximum(ndimage.gaussian_filter(ms.astype(float), s), 1e-6)
        cap = HILL_SLOPE * half + 0.3
        prof = np.minimum(Hf, cap) * smooth(d / max(half, 1e-6)) * ms
        hill[sl] = np.maximum(hill[sl], prof)
        p0 = members[0][0]
        if not p0.get("assumed"):
            hill_src[sl] = np.maximum(hill_src[sl], prof)
        code = CODES["hill_assumed"] if p0.get("assumed") else CODES["hill_b"] if p0.get("confidence") in ("A", "B") else CODES["hill_c"]
        hill_code[sl][(prof > 0.3) & (prof >= hill[sl] - 1e-9)] = code
        for k, (p, g) in enumerate(members):
            sel = (lab == k) & ms
            modelled[p["id"]] = round(float(prof[sel].max()), 2) if sel.any() else 0.0
    modelled["H0030"] = modelled.get("H0030", 0.0)

    # Shores: pieces of the water's edge, each with a kind.
    layout = boxes1860.layout()
    box_polys = [b.poly() for b in layout]
    box_tree = shapely.STRtree(box_polys)
    landings = [xz_geom(shape(f["geometry"])) for f in layer("landings_1860")]
    land_tree = shapely.STRtree(landings) if landings else None
    scenes = {f["properties"]["id"]: xz_geom(shape(f["geometry"])).buffer(0) for f in layer("scenes_1860")}
    main_of = {}
    for b in layout:
        s = b.parent or b.bid.split("-")[0]
        f, d = b.size()
        if s not in main_of or f * d > main_of[s][0]:
            main_of[s] = (f * d, b.cx, b.cz)
    rules = shore_rules()
    seg_pts, seg_kind, seg_top, seg_body, seg_grade = [], [], [], [], []
    kinds_len = Counter()
    for b in bodies:
        g = b["geom"].intersection(domain).simplify(SIMPLIFY_M)
        for q in polys(g):
            for ring in [q.exterior] + list(q.interiors):
                L = ring.length
                n = max(1, int(math.ceil(L / 2.0)))
                for k in range(n):
                    a = ring.interpolate(k / n, normalized=True)
                    seg_pts.append((a.x, a.y))
                    seg_body.append(b["index"])
    seg_pts = np.array(seg_pts)
    spt = shapely.points(seg_pts)
    near_box = np.zeros(len(seg_pts), bool)
    hit = box_tree.query(spt, predicate="dwithin", distance=NEAR_BOX_M)
    near_box[hit[0]] = True
    near_land = np.zeros(len(seg_pts), bool)
    if land_tree is not None:
        hit = land_tree.query(spt, predicate="dwithin", distance=NEAR_LANDING_M)
        near_land[hit[0]] = True
    kind = np.array(["earth"] * len(seg_pts), dtype=object)
    top = np.zeros(len(seg_pts))
    grade = np.array(["C"] * len(seg_pts), dtype=object)
    for s, k, tp, brg, rid, gr in rules:
        sg = scenes.get(s)
        if sg is None:
            continue
        inside = shapely.contains_xy(sg.buffer(15), seg_pts[:, 0], seg_pts[:, 1])
        if brg is not None and s in main_of:
            _, mx, mz = main_of[s]
            b_ = np.degrees(np.arctan2(seg_pts[:, 0] - mx, -(seg_pts[:, 1] - mz))) % 360
            inside &= np.abs((b_ - brg + 180) % 360 - 180) <= 60
        if k == "earth":
            grade[inside & (kind == "earth")] = gr
            continue
        kind[inside] = k
        grade[inside] = gr
        if tp:
            top[inside] = tp
    stone = near_box | near_land
    kind[stone] = "stone"
    for k in ("earth", "rock", "stone"):
        kinds_len[k] = int((kind == k).sum()) * 2
    ktree = cKDTree(seg_pts)

    # Natural land with hills, then the banks.
    Nn = N + hill
    Ns = N + hill_src
    land_pts = ~wet
    dist, nearest = ktree.query(np.column_stack([X[land_pts], Z[land_pts]]), k=1, distance_upper_bound=16)
    ok = np.isfinite(dist)

    def banked(Nat):
        out = Nat.copy()
        vals = Nat[land_pts]
        res = vals.copy()
        nk = nearest[ok]
        Lk = levels[np.array(seg_body)[nk]]
        kk = kind[nk]
        dd = dist[ok]
        v = vals[ok]
        r = np.empty_like(v)
        e = kk == "earth"
        r[e] = Lk[e] + TOP["earth"] + (v[e] - Lk[e] - TOP["earth"]) * smooth(dd[e] / EARTH_RAMP_M)
        ro = kk == "rock"
        tr = np.where(top[nk][ro] > 0, top[nk][ro], TOP["rock"])
        r[ro] = Lk[ro] + tr + (v[ro] - Lk[ro] - tr) * smooth(dd[ro] / ROCK_RAMP_M)
        st = kk == "stone"
        r[st] = np.maximum(v[st], Lk[st] + TOP["stone"])
        res[ok] = r
        out[land_pts] = res
        return out

    F = banked(Nn)
    Fs = banked(Ns)
    code = hill_code.copy()
    lk = np.zeros(land_pts.sum(), np.uint8)
    lk[ok] = np.where(kind[nearest[ok]] == "stone", CODES["bank_stone"], np.where(kind[nearest[ok]] == "rock", CODES["bank_rock"], 0))
    cl = code[land_pts]
    sel = (lk > 0) & (np.r_[dist][...] < 3.0) if False else (lk > 0) & (dist < 3.0)
    cl[sel] = lk[sel]
    code[land_pts] = cl

    # Fields (paddy) and the sunken court: flat, below the land.
    fields = [xz_geom(shape(f["geometry"])).buffer(0) for f in layer("fields_1860")]
    paddy = unary_union(fields).intersection(domain).simplify(SIMPLIFY_M).buffer(0).difference(water).buffer(0)
    paddy_levels = []
    for q in polys(paddy):
        m = raster_mask(q, xs, zs)
        lev = float(np.median(N[m])) - PADDY_DROP_M if m.any() else float(plain(q.centroid.x, q.centroid.y)) - PADDY_DROP_M
        F[m] = lev
        Fs[m] = lev
        paddy_levels.append((q, lev))
    court = court_all.intersection(domain).difference(water).buffer(0)
    court_levels = []
    for q in polys(court):
        ring = q.buffer(6).difference(q.buffer(1))
        m = raster_mask(ring, xs, zs) & ~wet
        lev = float(np.median(F[m])) - COURT_DROP_M
        mm = raster_mask(q, xs, zs)
        F[mm] = lev
        Fs[mm] = lev
        court_levels.append((q, lev))

    # Pads: the boxes of one compound on one level, blended out.
    feet = unary_union([p.buffer(PAD_GAP_M / 2) for p in box_polys])
    pad_groups = polys(feet)
    pad_tree = shapely.STRtree(pad_groups)
    gi = pad_tree.query(shapely.points([(b.cx, b.cz) for b in layout]), predicate="intersects")
    members = {}
    for bi, g in zip(*gi):
        members.setdefault(int(g), []).append(int(bi))
    pad_mask = np.zeros((Hn, W), bool)
    pad_level = np.zeros((Hn, W))
    pads_n = 0
    for g, bis in members.items():
        shape_ = unary_union([box_polys[i].buffer(PAD_APRON_M) for i in bis]).buffer(0)
        mfull = raster_mask(shape_, xs, zs)
        foot = raster_mask(unary_union([box_polys[i] for i in bis]), xs, zs) & ~wet
        mland = mfull & ~wet
        if not mland.any():
            continue
        if any(box_polys[i].intersects(court_all) for i in bis):
            mland &= ~raster_mask(court_all.buffer(-0.01), xs, zs) if False else mland
        lev = float(np.median(F[foot])) if foot.any() else float(np.median(F[mland]))
        lev = max(lev, float(near_level[mland].max()) + PAD_MIN_ABOVE_M)
        pad_mask |= mland
        pad_level[mland] = lev
        pads_n += 1
    # The sunken court's own boxes stand on its floor: no pad lifts them.
    for q, lev in court_levels:
        mm = raster_mask(q, xs, zs)
        pad_level[mm & pad_mask] = lev
    dP, idxP = ndimage.distance_transform_edt(~pad_mask, return_indices=True)
    dP *= STEP
    near_pad = pad_level[idxP[0], idxP[1]]
    w = smooth(dP / PAD_BLEND_M)
    blend = land_pts & (dP < PAD_BLEND_M) & ~raster_mask(court, xs, zs) & ~raster_mask(paddy, xs, zs)
    for A in (F, Fs):
        A[blend] = near_pad[blend] * (1 - w[blend]) + A[blend] * w[blend]
        A[pad_mask] = pad_level[pad_mask]
    code[pad_mask] = 0

    # Beds.
    dL, idxL = ndimage.distance_transform_edt(wet, return_indices=True)
    dL *= STEP
    Lw = np.where(wet, levels[np.maximum(body_r, 0)], 0)
    Dw = np.where(wet, depths[np.maximum(body_r, 0)], 0)
    shore_x, shore_z = X[idxL[0], idxL[1]], Z[idxL[0], idxL[1]]
    _, nk = ktree.query(np.column_stack([shore_x[wet], shore_z[wet]]), k=1)
    ek = np.array([EDGE[k] for k in kind[nk]])
    bed = np.zeros((Hn, W))
    bed[wet] = Lw[wet] - (ek + (Dw[wet] - ek) * smooth(dL[wet] / BED_RAMP_M))

    # The rasters the mesh samples: land extended over the water, bed extended over the land.
    land_r = fill_from(~wet, F)
    # Round 20: the land along the domain's edge, every 2.5 m, for the ring beyond (scripts/ground_outer1860.py joins to it). cm above the datum.
    surf = np.where(wet, fill_from(wet, np.where(wet, bed, 0)), land_r)  # what the mesh has on the edge: the land, or the bed where water reaches it
    edge = {"x0": x0, "z0": z0, "x1": float(xs[-1]), "z1": float(zs[-1]), "step_m": STEP, "note": "the ground on the domain's edge (the land, the bed under water): north (z0, west to east), south (z1), west (x0, north to south), east (x1); cm above datum_m; wet_* 1 where water",
            "north": np.round(surf[0, :] * 100).astype(int).tolist(), "south": np.round(surf[-1, :] * 100).astype(int).tolist(),
            "west": np.round(surf[:, 0] * 100).astype(int).tolist(), "east": np.round(surf[:, -1] * 100).astype(int).tolist(),
            "wet_north": wet[0, :].astype(int).tolist(), "wet_south": wet[-1, :].astype(int).tolist(), "wet_west": wet[:, 0].astype(int).tolist(), "wet_east": wet[:, -1].astype(int).tolist()}
    (TERRAIN / "ground_edge.json").write_text(json.dumps(edge, separators=(",", ":")) + "\n", encoding="utf-8")
    land_rs = fill_from(~wet, Fs)
    bed_r = fill_from(wet, np.where(wet, bed, 0))
    code_r = fill_from(~wet, code)

    holes = unary_union([water, paddy, court]).buffer(0)
    holes_prep = holes
    shapely.prepare(holes_prep)
    nx, nz = int(round((x1 - x0) / GROUND_ROOT_M)), int(round((z1 - z0) / GROUND_ROOT_M))
    leaves, lvl, bounds, cut, nbmax, passes = build_quadtree(x0, z0, nx, nz, land_r, bed_r, holes_prep, holes)

    land, bedm, padm, courtm = Mesh(), Mesh(), Mesh(), Mesh()
    parts_tree = shapely.STRtree(polys(holes))
    hole_list = polys(holes)
    water_p, paddy_p, court_p = water, paddy, court
    for g_ in (water_p, paddy_p, court_p):
        shapely.prepare(g_)
    for (l, i, j) in leaves:
        bx0, bz0, bx1, bz1 = bounds(l, i, j)
        c = cut(l, i, j)
        if c == 0:
            nb = nbmax(l, i, j)  # north, south, west, east
            mx, mz = (bx0 + bx1) / 2, (bz0 + bz1) / 2
            ring = [(bx0, bz0)]
            if nb[0] > l:
                ring.append((mx, bz0))
            ring.append((bx1, bz0))
            if nb[3] > l:
                ring.append((bx1, mz))
            ring.append((bx1, bz1))
            if nb[1] > l:
                ring.append((mx, bz1))
            ring.append((bx0, bz1))
            if nb[2] > l:
                ring.append((bx0, mz))
            if len(ring) == 4:
                land.tri(ring[0], ring[1], ring[2])
                land.tri(ring[0], ring[2], ring[3])
            else:
                land.fan(ring)
            continue
        cell = box(bx0, bz0, bx1, bz1)
        if c == 2:
            target = None
            if shapely.contains(water_p, cell):
                continue  # the bed has its own coarser pass below
            for g_, m_ in ((paddy_p, padm), (court_p, courtm)):
                if shapely.contains(g_, cell):
                    target = m_
                    break
            if target is not None:
                target.tri((bx0, bz0), (bx1, bz0), (bx1, bz1))
                target.tri((bx0, bz0), (bx1, bz1), (bx0, bz1))
                continue
        hits = parts_tree.query(cell, predicate="intersects")
        hole_here = unary_union([hole_list[k] for k in hits])
        for q in polys(cell.difference(hole_here)):
            land.poly(q)
        for g_, m_ in ((paddy_p, padm), (court_p, courtm)):
            for q in polys(cell.intersection(g_)):
                m_.poly(q)
    # The bed: root cells, cut to the water. Under the water's surface nothing finer is seen.
    for j in range(nz):
        for i in range(nx):
            cell = box(x0 + i * GROUND_ROOT_M, z0 + j * GROUND_ROOT_M, x0 + (i + 1) * GROUND_ROOT_M, z0 + (j + 1) * GROUND_ROOT_M)
            if not shapely.intersects(water_p, cell):
                continue
            if shapely.contains(water_p, cell):
                c0 = cell.bounds
                bedm.tri((c0[0], c0[1]), (c0[2], c0[1]), (c0[2], c0[3]))
                bedm.tri((c0[0], c0[1]), (c0[2], c0[3]), (c0[0], c0[3]))
                continue
            for q in polys(cell.intersection(water_p)):
                bedm.poly(q)

    pos = np.array(land.pos)
    y_land = bilinear(land_r, x0, z0, pos[:, 0], pos[:, 1])
    y_alt = bilinear(land_rs, x0, z0, pos[:, 0], pos[:, 1])
    # Codes at the vertices: the nearest lattice point's.
    ci = np.clip(np.round((pos[:, 0] - x0) / STEP).astype(int), 0, W - 1)
    cj = np.clip(np.round((pos[:, 1] - z0) / STEP).astype(int), 0, Hn - 1)
    vcode = code_r[cj, ci]
    bpos = np.array(bedm.pos) if bedm.pos else np.zeros((0, 2))
    y_bed = bilinear(bed_r, x0, z0, bpos[:, 0], bpos[:, 1]) if len(bpos) else np.zeros(0)

    # Skirts: every land edge used by one triangle, down to what lies beyond it.
    count = Counter()
    li = np.asarray(land.idx).reshape(-1, 3)
    for a, b, c in li:
        for e in ((a, b), (b, c), (c, a)):
            count[(min(e), max(e))] += 1
    edges = np.array([e for e, n in count.items() if n == 1])
    ea, eb = pos[edges[:, 0]], pos[edges[:, 1]]
    on_edge = ((np.isclose(ea[:, 0], x0) & np.isclose(eb[:, 0], x0)) | (np.isclose(ea[:, 0], x1) & np.isclose(eb[:, 0], x1)) |
               (np.isclose(ea[:, 1], z0) & np.isclose(eb[:, 1], z0)) | (np.isclose(ea[:, 1], z1) & np.isclose(eb[:, 1], z1)))
    edges, ea, eb = edges[~on_edge], ea[~on_edge], eb[~on_edge]
    mid = (ea + eb) / 2
    in_paddy = shapely.contains_xy(paddy_p.buffer(0.05), mid[:, 0], mid[:, 1])
    in_court = shapely.contains_xy(court_p.buffer(0.05), mid[:, 0], mid[:, 1])
    skirt_pos, skirt_idx, skirt_rgb = [], [], []
    bank_col = {"earth": (126, 118, 96), "rock": (110, 104, 94), "stone": (176, 170, 156)}
    _, sk_n = ktree.query(mid, k=1)
    for k_, (a, b) in enumerate(edges):
        ya, yb = y_land[a], y_land[b]
        (ax, az), (bx, bz) = pos[a], pos[b]
        if in_court[k_]:
            q = [lev for g_, lev in court_levels if g_.buffer(0.1).contains(Point(mid[k_]))]
            lo_a = lo_b = q[0] if q else ya - COURT_DROP_M
            col = bank_col["stone"]
        elif in_paddy[k_]:
            q = [lev for g_, lev in paddy_levels if g_.buffer(0.1).contains(Point(mid[k_]))]
            lo_a = lo_b = q[0] if q else ya - PADDY_DROP_M
            col = bank_col["earth"]
        else:
            if kind[sk_n[k_]] == "earth":
                continue  # the bed meets the land's edge: no step
            lo_a = float(bilinear(bed_r, x0, z0, ax, az))
            lo_b = float(bilinear(bed_r, x0, z0, bx, bz))
            col = bank_col[kind[sk_n[k_]]]
        n0 = len(skirt_pos)
        skirt_pos += [(ax, ya, az), (bx, yb, bz), (bx, lo_b - 0.05, bz), (ax, lo_a - 0.05, az)]
        skirt_idx += [n0, n0 + 1, n0 + 2, n0, n0 + 2, n0 + 3]
        skirt_rgb += [col] * 4

    # The walk surface: the land mesh rasterised on the lattice; water holds its bed.
    walk = rasterise(pos, y_land, land.idx, x0, z0, W, Hn)
    for m_, ys_ in ((padm, None), (courtm, None)):
        if m_.pos:
            pp = np.array(m_.pos)
            yy = np.array([next((lev for g_, lev in (paddy_levels if m_ is padm else court_levels) if g_.buffer(0.2).contains(Point(p))), F[min(max(int(round((p[1] - z0) / STEP)), 0), Hn - 1), min(max(int(round((p[0] - x0) / STEP)), 0), W - 1)]) for p in pp])
            if m_ is padm:
                pad_y = yy
            else:
                court_y = yy
            r_ = rasterise(pp, yy, m_.idx, x0, z0, W, Hn)
            walk = np.where(np.isnan(walk), r_, walk)
    if not padm.pos:
        pad_y = np.zeros(0)
    if not courtm.pos:
        court_y = np.zeros(0)
    missing = np.isnan(walk) & ~wet
    walk[missing] = land_r[missing]
    grid = np.round(walk * 100)
    grid[wet] = WATER_BASE + np.round(bed[wet] * 100)

    # Bridges: decks from land end to land end, a hump between; burned into the walk surface. The ends read the drawn surface over land cells only, as the view does.
    walk_land = np.where(np.isnan(walk), land_r, walk)

    def land_only(px_, pz_):
        u = np.clip((px_ - x0) / STEP, 0, W - 1.0001)
        v = np.clip((pz_ - z0) / STEP, 0, Hn - 1.0001)
        i_, j_ = np.floor(u).astype(int), np.floor(v).astype(int)
        a_, b_ = u - i_, v - j_
        acc, wsum = np.zeros(len(u)), np.zeros(len(u))
        for di, dj, wt in ((0, 0, (1 - a_) * (1 - b_)), (1, 0, a_ * (1 - b_)), (0, 1, (1 - a_) * b_), (1, 1, a_ * b_)):
            dry = ~wet[j_ + dj, i_ + di]
            acc += walk_land[j_ + dj, i_ + di] * wt * dry
            wsum += wt * dry
        return np.where(wsum > 1e-9, acc / np.maximum(wsum, 1e-9), walk_land[j_, i_])

    bridges = []
    joints = []
    for f in layer("bridges_1860"):
        p = f["properties"]
        line = xz_geom(shape(f["geometry"]))
        n = max(8, int(line.length / 1.0))
        q = [line.interpolate(k / n, normalized=True) for k in range(n + 1)]
        qx, qz = np.array([a.x for a in q]), np.array([a.y for a in q])
        on_water = shapely.contains_xy(water, qx, qz)
        hland = land_only(qx, qz)
        lw = np.flatnonzero(~on_water)
        ends = []
        if on_water.any():
            w0, w1 = np.flatnonzero(on_water)[[0, -1]]
            left = [k for k in lw if k < w0]
            right = [k for k in lw if k > w1]
            # An end inside the water polygon (the line stops short of the bank) takes the nearest land's height there.
            ya_ = hland[left[-1]] if left else hland[0]
            yb_ = hland[right[0]] if right else hland[n]
            deck = np.empty(n + 1)
            for k in range(n + 1):
                if k <= w0 and left:
                    deck[k] = hland[k] + BRIDGE_ON_LAND
                elif k >= w1 and right:
                    deck[k] = hland[k] + BRIDGE_ON_LAND
                else:
                    tt = (k - w0) / max(w1 - w0, 1)
                    deck[k] = ya_ + (yb_ - ya_) * tt + BRIDGE_ON_LAND + BRIDGE_HUMP_M * math.sin(math.pi * tt)
            for side, has, kk in (("1", left, 0), ("2", right, n)):
                joints.append({"bridge": p["id"], "end": side, "on_land": bool(has), "gap_m": round(float(abs(deck[kk] - hland[kk])) if has else None, 3) if has else None})
        else:
            deck = hland + BRIDGE_ON_LAND
            for side, kk in (("1", 0), ("2", n)):
                joints.append({"bridge": p["id"], "end": side, "on_land": True, "gap_m": round(float(abs(deck[kk] - hland[kk])), 3)})
        keep = np.unique(np.r_[0, np.arange(0, n + 1, max(1, n // 8)), n])
        pts = [[round(float(qx[k]), 2), round(float(deck[k]), 2), round(float(qz[k]), 2)] for k in keep]
        bridges.append({"id": p["id"], "building_id": p.get("building_id") or "", "name": p.get("name_zh", ""), "pts": pts})
        strip = line.buffer(BRIDGE_WALK_M / 2)
        m = raster_mask(strip, xs, zs)
        if m.any():
            jj, ii = np.nonzero(m)
            pxs, pzs = xs[ii], zs[jj]
            s = np.array([line.project(Point(a, b), normalized=True) for a, b in zip(pxs, pzs)])
            dk = np.interp(s, np.linspace(0, 1, n + 1), deck)
            wm = wet[jj, ii]
            grid[jj[wm], ii[wm]] = np.round(dk[wm] * 100)
    grid = np.clip(grid, -32767, 32767).astype("<i2")

    # Water level cells for the browser.
    lx, lz = np.arange(x0, x1, LEVEL_CELL_M) + LEVEL_CELL_M / 2, np.arange(z0, z1, LEVEL_CELL_M) + LEVEL_CELL_M / 2
    LX, LZ = np.meshgrid(lx, lz)
    bi = body_r[np.clip(np.round((LZ - z0) / STEP).astype(int), 0, Hn - 1), np.clip(np.round((LX - x0) / STEP).astype(int), 0, W - 1)]
    lvl_cells = np.where(bi >= 0, bi + 1, 0)
    near_cells = ndimage.distance_transform_edt(lvl_cells == 0, return_distances=True, return_indices=True)
    fillc = lvl_cells[near_cells[1][0], near_cells[1][1]]
    lvl_cells = np.where(near_cells[0] * LEVEL_CELL_M <= 30, fillc, 0).astype(np.uint8) if len(bodies) < 255 else None

    # Water surfaces.
    water_mesh = Mesh()
    water_y = []
    for b in bodies:
        for q in polys(b["geom"].intersection(domain).simplify(SIMPLIFY_M).buffer(0)):
            n0 = len(water_mesh.pos)
            for t_ in shapely.constrained_delaunay_triangles(q).geoms:
                cc = list(t_.exterior.coords)
                water_mesh.tri(cc[0], cc[1], cc[2])
            water_y += [b["level"]] * (len(water_mesh.pos) - n0)
    # Vertices shared between bodies (a touch within 1 m) keep the first level: they are few.
    water_y = np.array(water_y[:len(water_mesh.pos)] + [bodies[0]["level"]] * (len(water_mesh.pos) - len(water_y)))

    # Colours of the land: plain outside the gardens, greener inside, darker green with height.
    garden = unary_union([Polygon(xz_geom(shape(f["geometry"])).coords).buffer(0) for f in layer("walls_1860") if f["properties"]["kind"] == "outer_wall"])
    rng = np.random.default_rng(1860)
    inside = shapely.contains_xy(garden, pos[:, 0], pos[:, 1]).astype(float)
    base_here = bilinear(N, x0, z0, pos[:, 0], pos[:, 1])
    t_hill = np.clip((y_land - base_here) / 7, 0, 1)
    outside_c, inside_c, hill_c = np.array([170, 164, 124.0]), np.array([137, 152, 98.0]), np.array([78, 108, 62.0])
    noise = rng.normal(0, 1.2, len(pos)) * inside
    rgb = np.empty((len(pos), 3))
    for k in range(3):
        rgb[:, k] = (outside_c[k] * (1 - inside) + inside_c[k] * inside) * (1 - t_hill) + hill_c[k] * t_hill + noise
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)

    GENERATED.mkdir(parents=True, exist_ok=True)
    # The walk raster only where anything stands or is walked.
    reach = unary_union([garden.buffer(WALK_MARGIN_M)] + [p.buffer(WALK_MARGIN_M) for p in box_polys] + [xz_geom(shape(f["geometry"])).buffer(WALK_MARGIN_M) for f in layer("paths_1860")]).bounds
    wi0, wj0 = max(int(np.floor((reach[0] - x0) / STEP)), 0), max(int(np.floor((reach[1] - z0) / STEP)), 0)
    wi1, wj1 = min(int(np.ceil((reach[2] - x0) / STEP)) + 1, W), min(int(np.ceil((reach[3] - z0) / STEP)) + 1, Hn)
    grid[wj0:wj1, wi0:wi1].tofile(GENERATED / "ground_grid.i16")
    lvl_cells.tofile(GENERATED / "ground_level.u8")

    out = {"buf": [], "n": 0}

    def put(b):
        b = b + b"\0" * (-len(b) % 4)
        off = out["n"]
        out["buf"].append(b)
        out["n"] += len(b)
        return off

    def part(p3, idx, **extra):
        """Chunks of at most CHUNK vertices: positions int16 (x and z in decimetres from the domain's corner, y in centimetres), indices uint16, extras per vertex."""
        p3 = np.asarray(p3, float).reshape(-1, 3)
        idx = np.asarray(idx, np.int64).reshape(-1, 3)
        q = np.column_stack([np.round((p3[:, 0] - x0) * 10), np.round(p3[:, 1] * 100), np.round((p3[:, 2] - z0) * 10)])
        q = np.clip(q, -32767, 32767).astype("<i2")
        chunks = []
        start = 0
        while start < len(idx):
            remap = {}
            tris = []
            k = start
            while k < len(idx) and len(remap) <= CHUNK - 3:
                tris.append([remap.setdefault(int(v), len(remap)) for v in idx[k]])
                k += 1
            order = np.array(sorted(remap, key=remap.get), np.int64)
            e = {"verts": len(order), "pos": put(q[order].tobytes()), "indices": len(tris) * 3, "idx": put(np.asarray(tris, "<u2").tobytes())}
            for name, (a, dt) in extra.items():
                e[name] = put(np.asarray(a, dt)[order].tobytes())
            chunks.append(e)
            start = k
        return chunks

    land_xyz = np.column_stack([pos[:, 0], y_land, pos[:, 1]])
    parts_meta = {
        "land": part(land_xyz, land.idx, code=((vcode.astype(np.uint8) | (inside.astype(np.uint8) << 3)), "u1"), hill=(np.round(t_hill * 255), "u1"), yalt=(np.clip(np.round(y_alt * 100), -32767, 32767), "<i2")),
        "skirt": part(skirt_pos, skirt_idx, rgb=(np.array(skirt_rgb, np.uint8).reshape(-1, 3), "u1")),
        "bed": part(np.column_stack([bpos[:, 0], y_bed, bpos[:, 1]]) if len(bpos) else np.zeros((0, 3)), bedm.idx),
        "water": part(np.column_stack([np.array(water_mesh.pos)[:, 0], water_y, np.array(water_mesh.pos)[:, 1]]), water_mesh.idx),
        "paddy": part(np.column_stack([np.array(padm.pos)[:, 0], pad_y, np.array(padm.pos)[:, 1]]) if padm.pos else np.zeros((0, 3)), padm.idx),
        "court": part(np.column_stack([np.array(courtm.pos)[:, 0], court_y, np.array(courtm.pos)[:, 1]]) if courtm.pos else np.zeros((0, 3)), courtm.idx),
    }
    (GENERATED / "ground.bin").write_bytes(b"".join(out["buf"]))
    aff = lonlat_affine()
    meta = {
        "frame": "x east, z south, y above datum, metres; UTM 50N minus origin", "pos_unit": "int16: x and z in decimetres from domain[0], domain[1]; y in centimetres",
        "datum_m": DATUM_M, "ground_m": GROUND_M, "water_m": WATER_M, "lonlat": aff, "domain": [x0, z0, x1, z1],
        "plain": {"a": plain_meta["a"], "bx": plain_meta["bx"], "bz": plain_meta["bz"], "note": "y_EGM2008 = a + bx * x/1000 + bz * z/1000; scene y = that - datum_m"},
        "codes": CODES, "code_inside_bit": 8, "parts": parts_meta,
        "grid": {"x0": float(xs[wi0]), "z0": float(zs[wj0]), "step_m": STEP, "width": wi1 - wi0, "height": wj1 - wj0, "no_data": NO_DATA, "water_base": WATER_BASE, "water_below": -10000},
        "levels": {"x0": x0, "z0": z0, "cell_m": LEVEL_CELL_M, "width": len(lx), "height": len(lz)},
        "bodies": [{"i": b["index"], "level": round(b["level"], 3), "depth": b["depth"], "ids": b["ids"][:3], "names": b["names"]} for b in bodies],
        "bridges": bridges,
    }
    (GENERATED / "ground.json").write_text(json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

    with open(TERRAIN / "water_levels.csv", "w", encoding="utf-8", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["body", "water_ids", "names", "area_m2", "level_m_egm2008", "depth_m", "method", "sources", "confidence"])
        for b in bodies:
            wr.writerow([b["index"], ";".join(b["ids"]), ";".join(b["names"]), b["area_m2"], round(b["level"] + DATUM_M, 2), b["depth"],
                         f"the plain along its shore minus {FREEBOARD_M} m; depth {'福海 2.3 m (S1002)' if b['depth'] == 2.3 else 'small pond' if b['depth'] == DEPTH_SMALL else 'about 2 m (S1002)'}", "S04;S159;S1002", "C"])

    # What the run measured.
    rnd = np.random.default_rng(10)
    tri = np.asarray(land.idx).reshape(-1, 3)
    cen = pos[tri].mean(axis=1)
    ymesh = y_land[tri].mean(axis=1)
    yr = bilinear(land_r, x0, z0, cen[:, 0], cen[:, 1])
    dev = np.abs(ymesh - yr)
    lv = Counter(l for l, _, _ in leaves)
    report = {
        "plain": {k: plain_meta[k] for k in ("a", "bx", "bz", "fall_m_per_km", "falls_towards_deg", "rms_m")},
        "freeboard_m": FREEBOARD_M,
        "bodies": len(bodies), "levels_m": [round(float(levels.min() + DATUM_M), 2), round(float(levels.max() + DATUM_M), 2)],
        "shore_m": dict(kinds_len), "shore_grade_A_m": int((grade == "A").sum()) * 2,
        "hills_modelled": modelled,
        "pads": pads_n,
        "mesh": {"leaves_by_level": {str(k): v for k, v in sorted(lv.items())}, "balance_passes": passes, "land_tris": len(tri), "land_verts": len(pos), "skirt_quads": len(skirt_idx) // 6,
                 "bed_tris": len(bedm.idx) // 3, "water_tris": len(water_mesh.idx) // 3, "centroid_dev_vs_raster_m": {"median": round(float(np.median(dev)), 3), "p99": round(float(np.percentile(dev, 99)), 3), "max": round(float(dev.max()), 3)}},
        "bridge_joints": joints,
        "highest_m": round(float(F[~wet].max() + DATUM_M), 2), "hill_max_m": round(float(hill.max()), 2),
    }
    (TERRAIN / "ground_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    sizes = {p.name: p.stat().st_size for p in GENERATED.iterdir()}
    print(f"domain {x1 - x0:.0f} x {z1 - z0:.0f} m, lattice {W} x {Hn}; {len(bodies)} water bodies, levels {levels.min() + DATUM_M:.2f}-{levels.max() + DATUM_M:.2f} m; shore {dict(kinds_len)} m")
    print(f"hills {len(groups)} groups, highest modelled {hill.max():.1f} m; pads {pads_n}; leaves {dict(sorted(lv.items()))} in {passes} passes")
    print(f"land {len(pos)} verts {len(tri)} tris; skirts {len(skirt_idx) // 6}; bed {len(bedm.idx) // 3}; water {len(water_mesh.idx) // 3}; paddy {len(padm.idx) // 3}; court {len(courtm.idx) // 3}")
    print(f"mesh vs raster at triangle centres: median {np.median(dev):.3f} m, p99 {np.percentile(dev, 99):.3f}, max {dev.max():.3f}")
    print(f"generated: {', '.join(f'{k} {v / 1e6:.2f} MB' for k, v in sorted(sizes.items()))}; total {sum(sizes.values()) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
