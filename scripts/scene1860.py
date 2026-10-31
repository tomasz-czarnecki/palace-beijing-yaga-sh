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


def params():
    return json.load(open(PARAMS, encoding="utf-8"))


class Grid:
    """The 5 m raster ground1860.py writes (site/reconstruction/generated/ground.json + ground_grid.i16): centimetres above DATUM_M, NO_LAND where water stands."""

    NO_LAND = -32768

    def __init__(self):
        meta = json.load(open(GENERATED / "ground.json", encoding="utf-8"))["grid"]
        self.x0, self.z0, self.step, self.w, self.h = meta["x0"], meta["z0"], meta["step_m"], meta["width"], meta["height"]
        self.cm = np.fromfile(GENERATED / "ground_grid.i16", dtype="<i2").reshape(self.h, self.w)
        self.base = GROUND_M - DATUM_M

    def _cell(self, x, z):
        i = int(np.clip(np.floor((x - self.x0) / self.step), 0, self.w - 2))
        j = int(np.clip(np.floor((z - self.z0) / self.step), 0, self.h - 2))
        return i, j, (x - self.x0) / self.step - i, (z - self.z0) / self.step - j

    def at(self, x, z):
        """Ground height above the datum, bilinear. Water cells count as base land: what a wall or a box on the shore is measured from."""
        i, j, a, b = self._cell(x, z)
        v = self.cm[j:j + 2, i:i + 2].astype(float)
        v[v == self.NO_LAND] = self.base * 100
        return float(((v[0, 0] * (1 - a) + v[0, 1] * a) * (1 - b) + (v[1, 0] * (1 - a) + v[1, 1] * a) * b) / 100)
