"""The frame every Round 2 script shares: scene metres, base levels, layer access. Imported, not run.

Scene coordinates: x = east, z = south, y = height above DATUM_M, in metres. x and z are UTM 50N (EPSG:32650) minus the origin below, as CLAUDE.md asks for metric work.
Levels: research/terrain/README.md: use the DEM for base levels only, because it is a surface model of today (trees, modern fill, lakes lined and flattened).
"""

import json
from pathlib import Path

import numpy as np
from pyproj import Transformer

ROOT = Path(__file__).resolve().parent.parent
LAYERS = ROOT / "research/layers"
SITE_DATA = ROOT / "site/reconstruction/data"
GENERATED = ROOT / "site/reconstruction/generated"
PARAMS = ROOT / "research/typology/params.json"

GROUND_M = 45.0  # EGM2008. Base land level: "ground at about 45 m" (research/terrain/README.md, S04, S159), error 1-2 m. C for 1860
WATER_M = 43.5  # EGM2008. One level for all water: 福海's flat reading today (same README). The other lakes read 41-42.5 m but connect by canals; lined modern lakes, so not the levels of 1860. C
DATUM_M = WATER_M  # scene y = 0 is the water
ORIGIN_E, ORIGIN_N = 440000.0, 4428500.0  # about the middle of the three gardens

_fwd = Transformer.from_crs(4326, 32650, always_xy=True)
_inv = Transformer.from_crs(32650, 4326, always_xy=True)


def to_xz(lon, lat):
    e, n = _fwd.transform(lon, lat)
    return e - ORIGIN_E, ORIGIN_N - n


def to_lonlat(x, z):
    return _inv.transform(np.asarray(x) + ORIGIN_E, ORIGIN_N - np.asarray(z))


def lonlat_affine():
    """x, z as first-order functions of lon, lat, for the browser: [c0, c_lon, c_lat] about (lon0, lat0). Residual over the site printed by ground1860.py."""
    lon0, lat0 = to_lonlat(0.0, 0.0)
    lon0, lat0 = float(lon0), float(lat0)
    d = 0.01
    x0, z0 = to_xz(lon0, lat0)
    xe, ze = to_xz(lon0 + d, lat0)
    xn, zn = to_xz(lon0, lat0 + d)
    return {"lon0": lon0, "lat0": lat0, "x": [x0, (xe - x0) / d, (xn - x0) / d], "z": [z0, (ze - z0) / d, (zn - z0) / d]}


def layer(name):
    return json.load(open(LAYERS / f"{name}.geojson", encoding="utf-8"))["features"]


# Round 10: the ground's raster and the root of its mesh. The domain is the walls' extent plus GROUND_MARGIN_M, on multiples of GROUND_ROOT_M.
GROUND_STEP_M = 2.5
GROUND_ROOT_M = 20.0
GROUND_MARGIN_M = 320.0


def ground_frame():
    """x0, z0, x1, z1 of the ground's domain in scene metres (multiples of GROUND_ROOT_M round the outer walls)."""
    from shapely.geometry import shape
    from shapely.ops import unary_union
    import shapely

    lines = [shapely.transform(shape(f["geometry"]), lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1]))) for f in layer("walls_1860") if f["geometry"]["type"] == "LineString"]
    wx0, wz0, wx1, wz1 = unary_union(lines).bounds
    r = GROUND_ROOT_M
    return (float(np.floor((wx0 - GROUND_MARGIN_M) / r) * r), float(np.floor((wz0 - GROUND_MARGIN_M) / r) * r),
            float(np.ceil((wx1 + GROUND_MARGIN_M) / r) * r), float(np.ceil((wz1 + GROUND_MARGIN_M) / r) * r))


def raster_mask(geom, xs, zs):
    """Boolean raster (rows = zs, cols = xs) of the cell centres inside a geometry, working only inside its bounds."""
    import shapely

    out = np.zeros((len(zs), len(xs)), bool)
    if geom.is_empty:
        return out
    gx0, gz0, gx1, gz1 = geom.bounds
    i0, i1 = np.searchsorted(xs, gx0), np.searchsorted(xs, gx1)
    j0, j1 = np.searchsorted(zs, gz0), np.searchsorted(zs, gz1)
    if i1 > i0 and j1 > j0:
        shapely.prepare(geom)
        gx, gz = np.meshgrid(xs[i0:i1], zs[j0:j1])
        out[j0:j1, i0:i1] = shapely.contains_xy(geom, gx, gz)
    return out


def params():
    return json.load(open(PARAMS, encoding="utf-8"))


class Grid:
    """The 2.5 m lattice ground1860.py writes (site/reconstruction/generated/ground.json + ground_grid.i16): the land mesh rasterised, cm above DATUM_M;
    water cells hold WATER_BASE + the bed in cm; bridge decks count as land. ground_level.u8: the water body of each 10 m cell (ground.json bodies)."""

    def __init__(self):
        meta = json.load(open(GENERATED / "ground.json", encoding="utf-8"))
        g = meta["grid"]
        self.x0, self.z0, self.step, self.w, self.h = g["x0"], g["z0"], g["step_m"], g["width"], g["height"]
        self.water_base, self.water_below = g["water_base"], g["water_below"]
        raw = np.fromfile(GENERATED / "ground_grid.i16", dtype="<i2").reshape(self.h, self.w).astype(float)
        self.wet = raw < self.water_below
        self.y = np.where(self.wet, raw - self.water_base, raw) / 100  # land or bed, metres above the datum
        lv = meta["levels"]
        self.lv = lv
        self.cells = np.fromfile(GENERATED / "ground_level.u8", dtype="u1").reshape(lv["height"], lv["width"])
        self.levels = {b["i"]: b["level"] for b in meta["bodies"]}
        self.bridges = meta["bridges"]
        self.base = GROUND_M - DATUM_M

    def _cell(self, x, z):
        i = int(np.clip(np.floor((x - self.x0) / self.step), 0, self.w - 2))
        j = int(np.clip(np.floor((z - self.z0) / self.step), 0, self.h - 2))
        return i, j, min(max((x - self.x0) / self.step - i, 0.0), 1.0), min(max((z - self.z0) / self.step - j, 0.0), 1.0)

    def at(self, x, z):
        """Height above the datum, bilinear: the land, or the bed where water stands."""
        i, j, a, b = self._cell(x, z)
        v = self.y[j:j + 2, i:i + 2]
        return float((v[0, 0] * (1 - a) + v[0, 1] * a) * (1 - b) + (v[1, 0] * (1 - a) + v[1, 1] * a) * b)

    def land_at(self, x, z):
        """The land's height, bilinear over the land cells only; None if all four are water."""
        i, j, a, b = self._cell(x, z)
        v, wt = self.y[j:j + 2, i:i + 2], np.array([[(1 - a) * (1 - b), a * (1 - b)], [(1 - a) * b, a * b]])
        wt = wt * ~self.wet[j:j + 2, i:i + 2]
        s = wt.sum()
        return float((v * wt).sum() / s) if s > 1e-9 else None

    def is_water(self, x, z):
        i = int(np.clip(round((x - self.x0) / self.step), 0, self.w - 1))
        j = int(np.clip(round((z - self.z0) / self.step), 0, self.h - 1))
        return bool(self.wet[j, i])

    def level_at(self, x, z):
        """The level of the water body nearest (within 30 m), or None."""
        i = int(np.clip((x - self.lv["x0"]) // self.lv["cell_m"], 0, self.lv["width"] - 1))
        j = int(np.clip((z - self.lv["z0"]) // self.lv["cell_m"], 0, self.lv["height"] - 1))
        c = int(self.cells[j, i])
        return self.levels.get(c - 1) if c else None
