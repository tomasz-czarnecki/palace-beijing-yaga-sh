"""The ground beyond the gardens' domain (Round 20): a ring of 20 m cells about 2 km past the walls, west to 玉泉山, and a far backdrop of 200 m cells out to the Western Hills.

  uv run python scripts/ground_outer1860.py      (after scripts/ground1860.py; needs research/raw/dem/ with the GLO-30 tiles N39/N40 E115/E116)

Reads site/reconstruction/generated/ground.json (domain, datum, plain), research/terrain/ground_edge.json (the inner land on the domain's edge, written by ground1860.py),
the DEM tiles, research/layers/osm_ring_today.geojson (named peaks: which rises are real hills), research/layers/water_1860.geojson (features with `outside: true`:
lakes beyond the domain, carved and given a level). Writes site/reconstruction/generated/ground_outer.json + ground_outer.bin and research/terrain/ground_outer_report.json.

What the heights are (all from a run, see the report):
  - the ring's plain is the inner ground's plain (research/terrain/plain.json), extended as the same plane: on the domain's edge the ring equals the inner land, so the join has no step;
  - the DEM (GLO-30, a SURFACE model of 2011-15) is used only where it shows real relief: rises of at least RELIEF_MIN_M over the plain in a connected massif that holds a named
    OSM peak (万寿山, 玉泉山, 百望山 ...), after a grey opening of OPEN_RING_M that strips buildings and tree crowns narrower than that. The rest of today's city is ignored;
  - the backdrop is the DEM after an opening of OPEN_BACK_M, smoothed; the ring blends into it over its outer BLEND_OUT_M;
  - lakes beyond the domain lie at `level_m` (EGM2008) if the layer gives one, else at today's DEM surface inside them (its median), else the plain minus 1.5 m; beds LAKE_DEPTH_M down.
The ground of 1860 differs: 万寿山 carries today's rebuilt temples (佛香阁 of the 1890s) and its trees, the plain has 160 years of fill and digging. Limits in the report.

Byte layout of ground_outer.bin (little-endian, offsets in ground_outer.json):
  ring.h   int16 [nz][nx], cm above datum_m, row j = z0 + j*step (north to south), column i = x0 + i*step
  ring.c   uint8 [nz][nx], class: 0 plain (the extended plane, C), 1 relief from the DEM (B: today's hill), 2 lake bed, 3 lake shore (raised bank, C), 4 paddy, 5 field (fields_1860 outside the walls)
  back.h   int16 [nz][nx], dm above datum_m
The view triangulates each cell on the diagonal (i,j)-(i+1,j+1); ring cells inside the inner domain and backdrop cells inside the ring are not drawn.
"""

import json
import sys
from pathlib import Path

import numpy as np
import shapely
import tifffile
from scipy import ndimage
from shapely.geometry import Point, Polygon, box, shape
from shapely.ops import polygonize, unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scene1860 import GENERATED, ROOT, layer, raster_mask, to_lonlat, to_xz  # noqa: E402

DEM_DIR = ROOT / "research/raw/dem"
TILES = {(40, 115): "N39_00_E115_00", (41, 115): "N40_00_E115_00", (40, 116): "N39_00_E116_00", (41, 116): "N40_00_E116_00"}  # key: north edge, west edge
RING = (-5600.0, -3400.0, 4200.0, 3800.0)  # x0, z0, x1, z1: about S 39.970 W 116.231 N 40.035 E 116.346 (the round's ring), multiples of BACK_STEP
RING_STEP = 20.0  # the inner ground's root cell: the domain's corners are ring vertices
BACK = (-45000.0, -26000.0, 24000.0, 26000.0)  # to about 115.77 E: the Western Hills and the ranges behind them, fogged
BACK_STEP = 200.0
OPEN_RING_M = 80.0  # grey opening of 3 x 3 cells: buildings and crowns narrower than this go; 5 x 5 (150 m) cut 万寿山 to 80 m from 99 m
OPEN_BACK_M = 450.0
RELIEF_MIN_M = 6.0  # a rise over the plain counts as relief from this
RELIEF_MIN_AREA_M2 = 150000
RELIEF_BLEND_M = 120.0  # the rise fades in over this from the massif's edge
BLEND_OUT_M = 1000.0  # the ring's outer band blends from the plain to the backdrop
LAKE_DEPTH_M = 1.8
LAKE_BANK_M = 0.5  # land at a lake at least this above its water
LAKE_BANK_BLEND_M = 60.0
TEST_WATER = None  # --test-water <geojson>: extra outside lakes for a test run, never written into a layer


def dem_mosaic(south, west, north, east):
    """GLO-30 heights (EGM2008 m) over a lon/lat box, from the 1-degree tiles; returns array, north, west, step."""
    st = 1 / 3600
    rows = []
    for n in range(int(np.ceil(north)), int(np.floor(south)), -1):
        row = []
        for w in range(int(np.floor(west)), int(np.ceil(east))):
            a = tifffile.imread(DEM_DIR / f"Copernicus_DSM_COG_10_{TILES[(n, w)]}_DEM.tif")[:3600, :3600]
            row.append(a)
        rows.append(np.hstack(row))
    full = np.vstack(rows)
    n0, w0 = int(np.ceil(north)), int(np.floor(west))
    i0, i1 = int((n0 - north) / st), int((n0 - south) / st) + 1
    j0, j1 = int((west - w0) / st), int((east - w0) / st) + 1
    return full[i0:i1, j0:j1].astype(np.float32), n0 - i0 * st, w0 + j0 * st, st


def sampler(arr, north, west, st):
    def f(lon, lat):
        u, v = (np.asarray(lon) - west) / st, (north - np.asarray(lat)) / st
        return ndimage.map_coordinates(arr, [v, u], order=1, mode="nearest")
    return f


def lattice(x0, z0, x1, z1, step):
    xs, zs = np.arange(x0, x1 + step / 2, step), np.arange(z0, z1 + step / 2, step)
    X, Z = np.meshgrid(xs, zs)
    return xs, zs, X, Z


def tri_interp(H, x0, z0, step, x, z):
    """The mesh's own surface: each cell split on (i,j)-(i+1,j+1), as the view draws it."""
    u, v = (np.asarray(x, float) - x0) / step, (np.asarray(z, float) - z0) / step
    i = np.clip(np.floor(u).astype(int), 0, H.shape[1] - 2)
    j = np.clip(np.floor(v).astype(int), 0, H.shape[0] - 2)
    a, b = u - i, v - j
    h00, h10, h01, h11 = H[j, i], H[j, i + 1], H[j + 1, i], H[j + 1, i + 1]
    return np.where(a >= b, h00 + a * (h10 - h00) + b * (h11 - h10), h00 + b * (h01 - h00) + a * (h11 - h01))


def load(generated=GENERATED):
    """The outer ground as the view reads it: (meta, ring heights m, ring class, backdrop heights m), for checks."""
    meta = json.loads((generated / "ground_outer.json").read_text())
    raw = (generated / "ground_outer.bin").read_bytes()
    r, b = meta["ring"], meta["back"]
    rh = np.frombuffer(raw, "<i2", r["nx"] * r["nz"], r["off_h"]).reshape(r["nz"], r["nx"]) / 100.0
    rc = np.frombuffer(raw, "u1", r["nx"] * r["nz"], r["off_c"]).reshape(r["nz"], r["nx"])
    bh = np.frombuffer(raw, "<i2", b["nx"] * b["nz"], b["off_h"]).reshape(b["nz"], b["nx"]) / 10.0
    return meta, rh, rc, bh


def height_at(meta, rh, bh, x, z):
    """Ring or backdrop surface at scene x, z (outside the inner domain); inside it use the inner ground."""
    r, b = meta["ring"], meta["back"]
    x, z = np.asarray(x, float), np.asarray(z, float)
    inring = (x >= r["x0"]) & (x <= r["x1"]) & (z >= r["z0"]) & (z <= r["z1"])
    return np.where(inring, tri_interp(rh, r["x0"], r["z0"], r["step"], x, z), tri_interp(bh, b["x0"], b["z0"], b["step"], x, z))


def outside_lakes():
    feats = []
    try:
        feats = [f for f in layer("water_1860") if f["properties"].get("outside")]
    except FileNotFoundError:
        pass
    if TEST_WATER:
        feats += json.load(open(TEST_WATER, encoding="utf-8"))["features"]
    out = []
    for f in feats:
        g = shape(f["geometry"])
        if g.geom_type in ("LineString", "MultiLineString"):
            g = unary_union(list(polygonize(g)))
        g = shapely.transform(g, lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1]))).buffer(0)
        if g.is_empty or g.area < 400:
            continue
        out.append((f["properties"], g))
    return out


def main():
    global TEST_WATER
    if "--test-water" in sys.argv:
        TEST_WATER = sys.argv[sys.argv.index("--test-water") + 1]
    gmeta = json.loads((GENERATED / "ground.json").read_text())
    datum, pl = gmeta["datum_m"], gmeta["plain"]
    dx0, dz0, dx1, dz1 = gmeta["domain"]
    plain = lambda x, z: pl["a"] + pl["bx"] * x / 1000 + pl["bz"] * z / 1000 - datum  # noqa: E731
    edge = json.loads((ROOT / "research/terrain/ground_edge.json").read_text())
    assert (edge["x0"], edge["z0"], edge["x1"], edge["z1"]) == (dx0, dz0, dx1, dz1)
    for v in (dx0, dz0, dx1, dz1):
        assert abs(v / RING_STEP - round(v / RING_STEP)) < 1e-9

    # The DEM over the backdrop's lon/lat box.
    lo, la = to_lonlat(np.array([BACK[0], BACK[2], BACK[0], BACK[2]]), np.array([BACK[1], BACK[1], BACK[3], BACK[3]]))
    s, w, n, e = la.min() - 0.01, lo.min() - 0.01, la.max() + 0.01, lo.max() + 0.01
    dem, north, west, st = dem_mosaic(s, w, n, e)
    cell_m = st * 111000 * np.cos(np.radians(40.0))  # about 23.6 m east-west, 30.9 m north-south
    k_ring = max(3, int(round(OPEN_RING_M / 27)))
    k_back = max(5, int(round(OPEN_BACK_M / 27)))
    open_ring = ndimage.grey_opening(dem, size=(k_ring, k_ring))
    open_back = ndimage.gaussian_filter(ndimage.grey_opening(dem, size=(k_back, k_back)), 2.0)
    S_ring, S_back, S_raw = sampler(open_ring, north, west, st), sampler(open_back, north, west, st), sampler(dem, north, west, st)

    # Ring lattice.
    rxs, rzs, RX, RZ = lattice(*RING, RING_STEP)
    rlon, rlat = to_lonlat(RX, RZ)
    P = plain(RX, RZ)
    rise = ndimage.gaussian_filter(S_ring(rlon, rlat) - datum - P, 1.0)
    lab, nlab = ndimage.label(rise > RELIEF_MIN_M)
    peaks = []
    for f in json.load(open(ROOT / "research/layers/osm_ring_today.geojson", encoding="utf-8"))["features"]:
        p = f["properties"]
        if p.get("natural") in ("peak", "hill") and f["geometry"]["type"] == "Point":
            x, z = to_xz(*f["geometry"]["coordinates"])
            peaks.append((p.get("name", ""), float(x), float(z)))
    keep, massifs = np.zeros(nlab + 1, bool), []
    for name, x, z in peaks:
        i, j = int(round((x - RING[0]) / RING_STEP)), int(round((z - RING[1]) / RING_STEP))
        if 0 <= i < len(rxs) and 0 <= j < len(rzs):
            # the peak's own cell or the highest rise within 100 m
            win = (slice(max(j - 5, 0), j + 6), slice(max(i - 5, 0), i + 6))
            ids = set(lab[win][lab[win] > 0].tolist())
            for k in ids:
                area = (lab == k).sum() * RING_STEP ** 2
                if area >= RELIEF_MIN_AREA_M2 and not keep[k]:
                    keep[k] = True
                    massifs.append({"peak": name, "area_ha": round(area / 1e4, 1), "max_rise_m": round(float(rise[lab == k].max()), 1)})
    mask = keep[lab]
    d_in = ndimage.distance_transform_edt(mask) * RING_STEP
    t_rel = np.clip(d_in / RELIEF_BLEND_M, 0, 1)
    t_rel = t_rel * t_rel * (3 - 2 * t_rel)
    relief = np.where(mask, np.maximum(rise - RELIEF_MIN_M * (1 - t_rel), 0), 0.0)
    H = P + relief
    C = np.where(relief > 0.5, 1, 0).astype(np.uint8)

    # Backdrop lattice, and the ring's outer band blended into it.
    bxs, bzs, BX, BZ = lattice(*BACK, BACK_STEP)
    blon, blat = to_lonlat(BX, BZ)
    HB = S_back(blon, blat) - datum
    back_at_ring = tri_interp(HB, BACK[0], BACK[1], BACK_STEP, RX, RZ)
    d_out = np.minimum.reduce([RX - RING[0], RING[2] - RX, RZ - RING[1], RING[3] - RZ])
    t_out = np.clip(1 - d_out / BLEND_OUT_M, 0, 1)
    t_out = t_out * t_out * (3 - 2 * t_out)
    H = H * (1 - t_out) + back_at_ring * t_out
    # The backdrop, where the ring lies under it, takes the ring's surface (so a far view of the edge matches)
    ib0, ib1 = int((RING[0] - BACK[0]) / BACK_STEP), int((RING[2] - BACK[0]) / BACK_STEP)
    jb0, jb1 = int((RING[1] - BACK[1]) / BACK_STEP), int((RING[3] - BACK[1]) / BACK_STEP)
    stride = int(BACK_STEP / RING_STEP)
    HB[jb0:jb1 + 1, ib0:ib1 + 1] = H[::stride, ::stride]

    # Lakes beyond the domain.
    domain = box(dx0, dz0, dx1, dz1)
    lakes_out, lake_rep = [], []
    near_bank = np.full(H.shape, -np.inf)
    for p, g in outside_lakes():
        g_out = g.difference(domain)
        if g_out.is_empty:
            continue
        m = raster_mask(g_out, rxs, rzs)
        inner_body = next((b for b in gmeta["bodies"] if p.get("id") in b["ids"]), None) if g.intersects(domain) else None
        if inner_body is not None:
            level, how = float(inner_body["level"]), "the inner ground's body (ground.json): the lake crosses the domain's edge"
        elif p.get("level_m") not in (None, ""):
            level, how = float(p["level_m"]) - datum, "layer"
        else:
            inner = g_out.buffer(-30)
            mm = raster_mask(inner, rxs, rzs) if not inner.is_empty else m
            if mm.sum() >= 10:
                level, how = float(np.median(S_raw(rlon[mm], rlat[mm]))) - datum, "dem median"
            else:
                level, how = float(np.median(P[m])) - 1.5 if m.any() else 0.0, "plain - 1.5"
        dist_in = ndimage.distance_transform_edt(m) * RING_STEP
        bed = level - np.minimum(LAKE_DEPTH_M, 0.4 + dist_in / 20.0)
        H[m] = np.minimum(H[m], bed[m])
        C[m] = 2
        d_lake = ndimage.distance_transform_edt(~m) * RING_STEP
        tb = np.clip(1 - d_lake / LAKE_BANK_BLEND_M, 0, 1)
        near_bank = np.maximum(near_bank, np.where(~m & (tb > 0), level + LAKE_BANK_M * 1.0 - (1 - tb) * 3.0, -np.inf))
        rings = []
        for poly in getattr(g_out.simplify(2.0), "geoms", [g_out.simplify(2.0)]):
            if poly.geom_type != "Polygon" or poly.area < 400:
                continue
            rings.append({"outer": [[round(x, 1), round(z, 1)] for x, z in poly.exterior.coords[:-1]], "holes": [[[round(x, 1), round(z, 1)] for x, z in r.coords[:-1]] for r in poly.interiors]})
        lakes_out.append({"id": p.get("id", ""), "name_zh": p.get("name_zh", p.get("name", "")), "level": round(level, 2), "level_how": how, "polys": rings})
        lake_rep.append({"id": p.get("id", ""), "name": p.get("name_zh", p.get("name", "")), "level_m_egm2008": round(level + datum, 2), "how": how, "area_ha": round(g_out.area / 1e4, 1)})
    raise_ = (near_bank > H) & (C != 2)
    H[raise_] = near_bank[raise_]
    C[raise_ & (C == 0)] = 3

    # Paddies and fields outside the walls (fields_1860 `outside: true`): a class for the ground's tint, the heights untouched (the view drapes the patches themselves).
    for f in layer("fields_1860"):
        if not f["properties"].get("outside"):
            continue
        g = shapely.transform(shape(f["geometry"]), lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1]))).buffer(0).difference(domain)
        if not g.is_empty:
            m = raster_mask(g, rxs, rzs) & (C == 0)
            C[m] = 4 if f["properties"].get("kind") == "paddy" else 5

    # The join: ring vertices on the domain's edge take the inner land, which is the plain there unless water or a hill reaches the edge.
    def edge_vals(name):
        return np.array(edge[name], float) / 100.0
    i0, i1 = int(round((dx0 - RING[0]) / RING_STEP)), int(round((dx1 - RING[0]) / RING_STEP))
    j0, j1 = int(round((dz0 - RING[1]) / RING_STEP)), int(round((dz1 - RING[1]) / RING_STEP))
    k = int(round(RING_STEP / edge["step_m"]))
    H[j0, i0:i1 + 1] = edge_vals("north")[::k]
    H[j1, i0:i1 + 1] = edge_vals("south")[::k]
    H[j0:j1 + 1, i0] = edge_vals("west")[::k]
    H[j0:j1 + 1, i1] = edge_vals("east")[::k]
    for name, sl in (("north", (j0, slice(i0, i1 + 1))), ("south", (j1, slice(i0, i1 + 1))), ("west", (slice(j0, j1 + 1), i0)), ("east", (slice(j0, j1 + 1), i1))):
        wet_e = np.array(edge.get(f"wet_{name}", [0] * len(edge[name])))[::k].astype(bool)
        C[sl] = np.where(wet_e, 2, C[sl])
    H[j0 + 1:j1, i0 + 1:i1] = P[j0 + 1:j1, i0 + 1:i1]  # not drawn; the plain, so a sampler never sees a hole
    steps = []
    for name, along, fixed, horiz in (("north", np.arange(dx0, dx1 + 1e-6, edge["step_m"]), dz0, True), ("south", np.arange(dx0, dx1 + 1e-6, edge["step_m"]), dz1, True),
                                     ("west", np.arange(dz0, dz1 + 1e-6, edge["step_m"]), dx0, False), ("east", np.arange(dz0, dz1 + 1e-6, edge["step_m"]), dx1, False)):
        xq, zq = (along, np.full_like(along, fixed)) if horiz else (np.full_like(along, fixed), along)
        ring_v = tri_interp(np.round(H * 100) / 100, RING[0], RING[1], RING_STEP, xq, zq)
        wet_e = np.array(edge.get(f"wet_{name}", [0] * len(along))).astype(bool)
        dd = np.abs(ring_v - edge_vals(name))
        steps.append((float(dd[~wet_e].max()) if (~wet_e).any() else 0.0, float(dd[wet_e].max()) if wet_e.any() else 0.0, int(wet_e.sum())))
    # The ring against the backdrop on the ring's outer edge (both linear along it).
    oe = np.concatenate([np.abs(H[0, ::stride] - HB[jb0, ib0:ib1 + 1]), np.abs(H[-1, ::stride] - HB[jb1, ib0:ib1 + 1]), np.abs(H[::stride, 0] - HB[jb0:jb1 + 1, ib0]), np.abs(H[::stride, -1] - HB[jb0:jb1 + 1, ib1])])

    # Write.
    hq = np.clip(np.round(H * 100), -32767, 32767).astype("<i2")
    bq = np.clip(np.round(HB * 10), -32767, 32767).astype("<i2")
    parts = [hq.tobytes(), C.astype("u1").tobytes(), bq.tobytes()]
    offs = []
    blob = b""
    for part in parts:
        part = part + b"\0" * (-len(part) % 4)
        offs.append(len(blob))
        blob += part
    GENERATED.mkdir(parents=True, exist_ok=True)
    (GENERATED / "ground_outer.bin").write_bytes(blob)
    meta = {
        "what": "Round 20: the ground past the inner domain: a ring of 20 m cells and a backdrop of 200 m cells (scripts/ground_outer1860.py)",
        "frame": "x east, z south, metres; scene frame of scene1860.py", "datum_m": datum, "domain": gmeta["domain"],
        "ring": {"x0": RING[0], "z0": RING[1], "x1": RING[2], "z1": RING[3], "step": RING_STEP, "nx": len(rxs), "nz": len(rzs), "off_h": offs[0], "off_c": offs[1], "h_unit": "cm", "hole": gmeta["domain"]},
        "back": {"x0": BACK[0], "z0": BACK[1], "x1": BACK[2], "z1": BACK[3], "step": BACK_STEP, "nx": len(bxs), "nz": len(bzs), "off_h": offs[2], "h_unit": "dm", "hole": list(RING)},
        "classes": {"0": "plain: the inner ground's plane, extended (C)", "1": "relief: today's DEM on a named massif, opened (B)", "2": "lake bed (C)", "3": "lake bank, raised (C)", "4": "paddy (fields_1860, outside the walls)", "5": "field (fields_1860, outside the walls)"},
        "lakes": lakes_out,
        "diagonal": "each cell split on (i,j)-(i+1,j+1)",
    }
    (GENERATED / "ground_outer.json").write_text(json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    ringP = plain(RX, RZ)
    report = {
        "ring": {"bounds_xz": list(RING), "step_m": RING_STEP, "nodes": int(H.size), "lonlat_sw": [round(float(rlon[-1, 0]), 4), round(float(rlat[-1, 0]), 4)], "lonlat_ne": [round(float(rlon[0, -1]), 4), round(float(rlat[0, -1]), 4)],
                 "classes": {str(c): int((C == c).sum()) for c in range(6)}, "highest_m_egm2008": round(float(H.max() + datum), 1)},
        "back": {"bounds_xz": list(BACK), "step_m": BACK_STEP, "nodes": int(HB.size), "lonlat_sw": [round(float(blon[-1, 0]), 3), round(float(blat[-1, 0]), 3)], "lonlat_ne": [round(float(blon[0, -1]), 3), round(float(blat[0, -1]), 3)], "highest_m_egm2008": round(float(HB.max() + datum), 1)},
        "massifs": massifs,
        "lakes": lake_rep,
        "join_inner_step_m": {**{n: {"dry": round(st_[0], 3), "under_water": round(st_[1], 3), "wet_points": st_[2]} for n, st_ in zip(("north", "south", "west", "east"), steps)}, "max_dry": round(max(x[0] for x in steps), 3), "max_under_water": round(max(x[1] for x in steps), 3),
                              "how": "every 2.5 m of the domain's edge: the inner ground there (ground_edge.json: land, or the bed where a lake crosses the edge) against the ring's own surface (cm-rounded, its cell triangles); the view meets the inner mesh's own edge vertices, so the drawn seam is closed either way"},
        "join_backdrop_step_m": round(float(oe.max()), 3),
        "plain_vs_dem_backdrop_at_ring_edge_m": {"median": round(float(np.median((back_at_ring - ringP)[d_out < RING_STEP])), 2), "p10": round(float(np.percentile((back_at_ring - ringP)[d_out < RING_STEP], 10)), 2), "p90": round(float(np.percentile((back_at_ring - ringP)[d_out < RING_STEP], 90)), 2)},
        "dem_limits": [
            "GLO-30 is a surface model (TanDEM-X 2011-15), 1 arc second (about 24 x 31 m here): roofs and tree crowns are in it.",
            f"Ring: the DEM only on massifs holding a named OSM peak, after a grey opening of {OPEN_RING_M:.0f} m (buildings and crowns narrower than that removed; a forest canopy stays, some 5-15 m too high).",
            "万寿山 carries today's temples rebuilt in the 1880s-90s (佛香阁 on its terrace) and today's trees; its earth was heaped in 1750 from the lake: the hill is the one of 1860 within the DEM's error, the buildings are not modelled.",
            "Everything else in the ring is the plane of the inner ground (research/terrain/plain.json) extended: today's city, fill, cuttings and modern reservoirs are ignored, and so is any small rise of 1860.",
            f"Backdrop: the DEM after an opening of {OPEN_BACK_M:.0f} m and a smoothing of about 60 m: the ranges' silhouette, not their detail; it is drawn under fog.",
        ],
        "sizes_bytes": {"ground_outer.bin": len(blob), "ground_outer.json": (GENERATED / "ground_outer.json").stat().st_size},
        "sources": "S04 (GLO-30), S03 (OSM peaks), research/terrain/plain.json",
    }
    (ROOT / "research/terrain/ground_outer_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"ring {len(rxs)} x {len(rzs)} at {RING_STEP:.0f} m; backdrop {len(bxs)} x {len(bzs)} at {BACK_STEP:.0f} m; massifs {[m['peak'] for m in massifs]}; lakes {[(l['name'], l['level_m_egm2008'], l['how']) for l in lake_rep]}")
    print(f"join step to the inner ground {max(x[0] for x in steps):.3f} m dry, {max(x[1] for x in steps):.3f} m under water; to the backdrop {oe.max():.3f} m; highest ring {H.max() + datum:.1f} m, backdrop {HB.max() + datum:.1f} m; bin {len(blob) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
