"""The site of a detailed model (Round 15): its frame from a box, the walk surface of Round 10 under it, footings that follow the ground, and the files a generator writes
(params.json, keypoints.json, joints.json, summary.json; models/README.md). Imported, not run.

Lifted from 海晏堂's generator (models/XY08-haiyan-tang/haiyantang.py, Round 14), which keeps its own copies so that its GLB stays as it is.
Frame: origin at the front middle of the main box, at that box's ground; x along the front (to the right as one faces it from outside: east for a south front), y up,
z out of the front. rotationY as halls3d.js reads a box (models/README.md).
"""

import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))
from check_ground import NewGround  # noqa: E402
from scene1860 import DATUM_M, to_xz  # noqa: E402

_G = None


def ground():
    global _G
    if _G is None:
        _G = NewGround(ROOT)
    return _G


def boxes():
    fc = json.load(open(ROOT / "site/reconstruction/data/halls_1860.geojson", encoding="utf-8"))
    return {f["properties"]["id"]: f for f in fc["features"]}


def box_frame(F, bid):
    """The box's middle, its front direction (unit, scene x z), its half sizes and its ground (scene y)."""
    f = F[bid]
    r = [np.array(to_xz(*c), float) for c in f["geometry"]["coordinates"][0]]
    c = (r[0] + r[2]) / 2
    p = f["properties"]
    a = math.radians(p["orientation_deg"])
    u = np.array([math.sin(a), -math.cos(a)])  # the front's normal: bearing orientation_deg, x east, z south
    return c, u, p["frontage_m"] / 2, p["depth_m"] / 2, p["ground_m"] - DATUM_M


class Site:
    def __init__(self, bid, front_offset=None):
        """The frame at the front middle of box `bid` (or `front_offset` m along its normal from its middle)."""
        self.F = boxes()
        c, u, hf, hd, base = box_frame(self.F, bid)
        off = hd if front_offset is None else front_offset
        o = c + u * off
        self.rot = round(math.atan2(u[0], u[1]), 6)
        self.pos = [round(float(o[0]), 3), round(float(base), 3), round(float(o[1]), 3)]
        self.G = ground()
        self.m = None
        self.KP, self.JOINTS, self.ENTRIES, self.FOOTPRINTS = {}, [], [], []
        self.DECKS = []  # Round 16: raised floors the model draws and people walk on (a terrace): [name, y, polygon (x, z)]
        self.CLEAR = []  # Round 17: areas the planting keeps off but the ways may cross (a paved court, a lawn): polygons (x, z); scripts/greens1860.py reads them
        self.ROCKERIES = []  # Round 25: scene ids whose rockeries and standing rocks the model draws itself; scripts/greens1860.py places none for them
        self.LEVEL = []  # Round 27: courts the model leaves earth (their trees stay) where no generated hill may stand: polygons (x, z); scripts/hills1860.py reads them

    # ---- frames
    def to_scene(self, p):
        c, s = math.cos(self.rot), math.sin(self.rot)
        x, y, z = p
        return [round(self.pos[0] + c * x + s * z, 3), round(self.pos[1] + y, 3), round(self.pos[2] - s * x + c * z, 3)]

    def to_local(self, sx, sz):
        c, s = math.cos(self.rot), math.sin(self.rot)
        dx, dz = sx - self.pos[0], sz - self.pos[2]
        return c * dx - s * dz, s * dx + c * dz

    def box_local(self, bid):
        """A box's middle in the frame (x, z) and its ground in the frame's y."""
        c, u, hf, hd, base = box_frame(self.F, bid)
        x, z = self.to_local(*c)
        return x, z, hf, hd, base - self.pos[1]

    # ---- the ground
    def gy(self, x, z):
        """The walk surface under a frame point, in the frame's y (land; the bed where there is water)."""
        sx, _, sz = self.to_scene((x, 0.0, z))
        g = self.G.land(sx, sz)
        if g is None:
            g = self.G.at(sx, sz)
        return g - self.pos[1]

    def gmin(self, poly, n=4):
        xs, zs = [p[0] for p in poly], [p[1] for p in poly]
        pts = list(poly) + [(x, z) for x in np.linspace(min(xs), max(xs), n) for z in np.linspace(min(zs), max(zs), n)]
        return min(self.gy(x, z) for x, z in pts)

    def skirt(self, poly, top, mat, closed=True, step=2.5, below=0.15):
        """Vertical faces from just below the ground (followed along the edges every `step` m) up to `top` (a number or one per corner). The bottoms at the corners."""
        m = self.m
        n = len(poly)
        bots = []
        for i in range(n if closed else n - 1):
            (ax, az), (bx, bz) = poly[i], poly[(i + 1) % n]
            L = math.hypot(bx - ax, bz - az)
            k = max(1, int(math.ceil(L / step)))
            pts = [(ax + (bx - ax) * t / k, az + (bz - az) * t / k) for t in range(k + 1)]
            ys = [self.gy(x, z) - below for x, z in pts]
            bots.append(ys[0])
            tops = top if isinstance(top, (list, tuple)) else None
            for j in range(k):
                if tops:
                    ta, tb = tops[i], tops[(i + 1) % n]
                    ya, yb = ta + (tb - ta) * j / k, ta + (tb - ta) * (j + 1) / k
                else:
                    ya = yb = top
                (x0, z0), (x1, z1) = pts[j], pts[j + 1]
                m.poly([(x0, ys[j], z0), (x1, ys[j + 1], z1), (x1, yb, z1)], mat)
                m.poly([(x0, ys[j], z0), (x1, yb, z1), (x0, ya, z0)], mat)
        if not closed:
            bots.append(self.gy(*poly[-1]) - below)
        return bots

    def footing(self, poly, top, mat="rustic", name=None, kind="wall foot", corners=True, lid=True, fp=True):
        """A block from just below the ground up to `top`; its corners are joints, its outline a footprint."""
        bots = self.skirt(poly, top, mat)
        if lid:
            self.m.flat(poly, top, mat)
        if fp:
            self.FOOTPRINTS.append([tuple(p) for p in poly])
        if name and corners:
            for i, (x, z) in enumerate(poly):
                self.JOINTS.append([f"{name}_{i}", x, bots[i], z, kind])
        return min(bots)

    def kp(self, name, p, anchor=False):
        self.KP[name] = {"p": [round(float(c), 3) for c in p], "anchor": anchor}

    def joint(self, name, x, z, kind, y=None):
        self.JOINTS.append([name, x, self.gy(x, z) - 0.05 if y is None else y, z, kind])

    def entry(self, name, x, z, y=None):
        self.ENTRIES.append([name, x, self.gy(x, z) if y is None else y, z])

    def deck(self, name, y, poly):
        """Round 16: a raised floor the model draws (a terrace) at frame height y over the outline poly: the view lays the ways that cross it on it, and tools/check_models.py
        measures a way's end there against it, not against the ground of Round 10."""
        self.DECKS.append([name, y, [tuple(p) for p in poly]])

    # ---- the files
    def write(self, here, obj_id, objects, P, frame_note, summary):
        params = {k: {"value": v[0], "source": v[1], "grade": v[2], "note": v[3]} for k, v in P.items()}
        json.dump({"id": obj_id, "frame": frame_note, "params": params}, open(here / "params.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        pts = {k: {"local": v["p"], "scene": self.to_scene(v["p"]), "anchor": v.get("anchor", False)} for k, v in self.KP.items()}
        json.dump({"id": obj_id, "objects": objects, "position": self.pos, "rotationY": self.rot, "points": pts}, open(here / "keypoints.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        json.dump({"id": obj_id, "position": self.pos, "rotationY": self.rot,
                   "joints": [{"name": j[0], "scene": self.to_scene(j[1:4]), "kind": j[4]} for j in self.JOINTS],
                   "entries": [{"name": e[0], "scene": self.to_scene(e[1:4])} for e in self.ENTRIES],
                   "footprints": [[self.to_scene((x, 0.0, z))[::2] for x, z in fp] for fp in self.FOOTPRINTS],
                   **({"decks": [{"name": n, "y": self.to_scene((0.0, y, 0.0))[1], "poly": [self.to_scene((x, 0.0, z))[::2] for x, z in poly]} for n, y, poly in self.DECKS]} if self.DECKS else {}),
                   **({"clear": [[self.to_scene((x, 0.0, z))[::2] for x, z in fp] for fp in self.CLEAR]} if self.CLEAR else {}),
                   **({"rockeries": sorted(self.ROCKERIES)} if self.ROCKERIES else {}),
                   **({"level": [[self.to_scene((x, 0.0, z))[::2] for x, z in fp] for fp in self.LEVEL]} if self.LEVEL else {})},
                  open(here / "joints.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(summary, open(here / "summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def lobed(points, n=6):
    """A smooth closed outline through control points (x, z): Catmull-Rom, n points a span."""
    out = []
    k = len(points)
    for i in range(k):
        p0, p1, p2, p3 = (np.array(points[(i + j - 1) % k], float) for j in range(4))
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            q = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
            out.append((float(q[0]), float(q[1])))
    return out


def offset(poly, d):
    """A closed outline moved outward by d (inward for d < 0), by shapely (mitred)."""
    from shapely.geometry import Polygon
    g = Polygon(poly).buffer(d, join_style=2, mitre_limit=3.0)
    if g.geom_type != "Polygon":
        g = max(g.geoms, key=lambda q: q.area)
    c = list(g.exterior.coords)[:-1]
    return [(float(x), float(z)) for x, z in c]


def offset_aligned(poly, d):
    """offset(), resampled to len(poly) points, started at the point nearest poly[0] and wound the same way, so that ring() can join them point by point."""
    n = len(poly)
    off = resample(offset(poly, d), n)
    area = lambda q: sum(q[i][0] * q[(i + 1) % len(q)][1] - q[(i + 1) % len(q)][0] * q[i][1] for i in range(len(q)))
    if (area(off) > 0) != (area(poly) > 0):
        off = off[::-1]
    k = min(range(n), key=lambda i: (off[i][0] - poly[0][0]) ** 2 + (off[i][1] - poly[0][1]) ** 2)
    return off[k:] + off[:k]


def ring(m, outer, inner, y, mat):
    """A flat band between two closed outlines with the same number of points, at y."""
    n = len(outer)
    for i in range(n):
        a, b = outer[i], outer[(i + 1) % n]
        c, d = inner[(i + 1) % n], inner[i]
        m.poly([(a[0], y, a[1]), (b[0], y, b[1]), (c[0], y, c[1]), (d[0], y, d[1])], mat)


def resample(poly, n):
    """A closed outline resampled to n points evenly along its length."""
    P = np.array(poly + [poly[0]], float)
    seg = np.hypot(*np.diff(P, axis=0).T)
    s = np.r_[0, np.cumsum(seg)]
    t = np.linspace(0, s[-1], n, endpoint=False)
    return [(float(np.interp(v, s, P[:, 0])), float(np.interp(v, s, P[:, 1]))) for v in t]
