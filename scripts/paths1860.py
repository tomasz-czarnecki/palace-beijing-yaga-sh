"""Round 9: the ways of 1860. Writes research/layers/paths_1860.geojson, landings_1860.geojson, routes_1860.geojson and their public copies in site/reconstruction/data/.

  uv run python scripts/paths1860.py        (after boxes1860.py; prints its checks)

Inputs, hand-edited (research/paths/README.md):
  research/paths/traces.csv   the plan readers' lines in plan pixels on S01, one row per way, landing or dock, with the ids they join
  research/paths/routes.csv   the named tours and axes, as waypoints
  research/paths/grades.csv   what raises or lowers a trace: a dig, a text (key, confidence, sources, basis)
and the layers and boxes already built: research/layers/{water,bridges,walls,scenes}_1860, site/reconstruction/data/halls_1860.geojson.

What it does, in order:
  1. every trace through the plan transform in use (scripts/georef.py), into scene metres (scene1860.py);
  2. each end snapped to what it joins: a hall's door (the side mid-point of its box, 0.6 m out, the front preferred), a gate
     (its box's centre, a gate is walked through; else the gate point), a bridge end, a landing, a point on another line.
     The distance from the warped end to that point is the gap before; after, the end is that point;
  3. a line that crosses a box, a garden wall or water (not over a bridge) is rerouted round it on a 0.75 m grid, kept close to
     the trace (`rerouted_m` is how far it strays at most). A gallery may run inside the box that is its own bay row (`in_box`).
     Gate boxes, terraces, courts and stair bases are walked through;
  4. landings to the shore, 0.3 m inside the land; boat routes stay on the water;
  5. bridge approaches: a bridge end with no way within 1 m gets a C approach to the nearest way, door or gate within 60 m;
  6. minimal C links: in each compound, a hall no way reaches gets one line from its door to the nearest way of the compound,
     or to its entry (a gate, a bridge end, a landing) if none; `assumed: true`, basis `reach`;
  7. routes: the shortest way through the network between the waypoints of routes.csv (A and B ways preferred, a hall walked
     through by its doors), with the halls to stop at.
Confidence: A where a period picture (the 1744 leaves, the 1780s plates) or a dig shows it (`leaf`, grades.csv); B where S01 draws it
or a text describes it; C where it is inferred. `pos_confidence` B for a trace on S01, C for a line made here.
"""

import csv
import heapq
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import shapely
import shapely.ops
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from shapely.geometry import LineString, Point, shape
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
import georef  # noqa: E402
from scene1860 import LAYERS, ROOT, SITE_DATA, layer, to_lonlat, to_xz  # noqa: E402

PATHS = ROOT / "research/paths"
CREDIT = "Traced from the Plan of the Yuanmingyuan, Princeton University Art Museum 2022-27 a-c (S01). Image courtesy of the Princeton University Art Museum. Grades from the Forty Scenes album (BnF) and the sources cited per feature; C lines are guesses, marked assumed."

# Widths by kind, m, where neither the plan's drawn width nor a source gives one. Typology, C.
WIDTH = {
    "imperial_road": 5.0,  # params.json other.paving: the 大宫门 road drawn 23 px wide on S01, about 5 m
    "paved_way": 3.0,  # a 甬道 about as wide as the central bay of the hall it leads to (3-5 m at the big halls); guess
    "courtyard_path": 1.8,  # guess
    "service_path": 1.5,  # guess
    "gallery": 2.4,  # params.json classes.gallery: depth 1.8-2.6 m, one bay of 2.88 m along
    "mountain_gallery": 2.4,
    "causeway": 4.0,  # guess; the drawn strips are 4-9 m of land
    "dike": 5.0,  # guess
    "bridge_approach": 3.0,  # the bridge deck, params.json other.bridge
    "steps": 3.0,  # guess; 如园's front steps 4.6 m wide (S362, a dig)
    "boat_route": 0.0,
}
SURFACE = {  # typology, C, except where a dig is cited on the feature
    "imperial_road": "stone road 石路 (so labelled on S01 south of 大宫门)",
    "paved_way": "stone-slab paved way 甬道",
    "courtyard_path": "brick or stone paving",
    "service_path": "brick or beaten earth",
    "gallery": "brick floor under a roof on posts",
    "mountain_gallery": "stepped brick floor under a roof",
    "causeway": "earth, stone-edged",
    "dike": "earth, stone-edged",
    "bridge_approach": "stone paving",
    "steps": "stone steps 踏跺",
    "boat_route": "water",
}
LAND_KINDS = set(WIDTH) - {"boat_route"}
POINT_KINDS = {"landing", "dock"}
DOOR_OUT_M = 0.6  # a door point stands this far out from the box
SNAP_FREE_M = 25.0  # an end with no id joins the nearest thing within this
SNAP_ID_MAX_M = 25.0  # an id whose point lies farther than this from the traced end is taken as misread: the end joins the nearest thing instead
SNAP_ID_MAX_XY_M = 40.0  # the Xiyang Lou boxes stand on the ruins, up to about 15 m off the plan (Q64)
SHORE_MAX_M = 15.0  # a landing more than this from the traced water stays where it was traced, flagged
GRID_M = 0.75  # routing grid
CLEAR_M = 0.35  # a rerouted line keeps this far off a box or the water
MARGIN_M = 30.0
APPROACH_MAX_M = 60.0
REACH_MAX_M = 120.0
DANGLE_MAX_M = 40.0
SHORE_IN_M = 0.3  # a landing point stands this far inside the land
JOINT_TOL_M = 0.5
BOAT_CLEAR_M = (4.0, 1.5, 0.3)  # a boat keeps this far off the shore, less where the water is narrow
CONF_RANK = {"A": 0, "B": 1, "C": 2}


def rows(p):
    return list(csv.DictReader(open(p, encoding="utf-8", newline=""))) if p.exists() else []


def xz_geom(g):
    return shapely.transform(shape(g), lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1])))


def ll_coords(line):
    c = np.asarray(line.coords)
    lon, lat = to_lonlat(c[:, 0], c[:, 1])
    return [[round(float(a), 7), round(float(b), 7)] for a, b in zip(lon, lat)]


# ------------------------------------------------------------------ the world: boxes, water, walls, bridges, gates

class Box:
    def __init__(self, f):
        p = f["properties"]
        self.p = p
        self.id, self.bid, self.parent = p["id"], p["building_id"], p.get("parent_id") or ""
        ring = np.asarray(xz_geom(f["geometry"]).exterior.coords)[:4]
        self.c = (ring[0] + ring[2]) / 2
        uv, av = ring[1] - ring[0], ring[1] - ring[2]
        self.hf, self.hd = np.linalg.norm(uv) / 2, np.linalg.norm(av) / 2
        self.u, self.a = uv / (2 * self.hf), av / (2 * self.hd)
        self.poly = shapely.Polygon(ring)
        shape_ = p.get("shape")
        self.in_wall = False
        self.gate = p["building_id"].startswith("G") or p.get("hall_class") == "gate_hall" or ROWTYPE.get(p["building_id"]) == "gate"
        self.walk_through = self.gate or shape_ in ("terrace", "court") or (shape_ == "octagon" and p.get("ridge_m") == p.get("eave_m"))
        self.maze = shape_ == "wall" and p["building_id"].startswith("XY04")  # the maze's walls stand for the plan, not traced (xiyanglou/boxes.csv): the way through is not known
        self.walk_through = self.walk_through or self.maze

    def doors(self):
        o = DOOR_OUT_M
        ent = MODEL_ENTRIES.get(self.bid) if MODEL_DOORS["on"] else None
        if ent:
            # Round 13: a detailed model stands here: its own doors and stair feet (models/<ID>-<slug>/joints.json), those outside this box, are the doors
            out = {f"model {n}": xz for n, xz in ent if self.walk_through or not self.poly.buffer(-0.05).contains(Point(xz))}  # a court's entries lie inside it (Round 15)
            if out:
                return out
        return {"front": self.c + self.a * (self.hd + o), "back": self.c - self.a * (self.hd + o), "right": self.c + self.u * (self.hf + o), "left": self.c - self.u * (self.hf + o)}


def model_entries():
    """Round 13: building id -> [(name, xz)] of every detailed model's entries, for the model's id and its aliases; and every model's footprints (shapely polygons) into MODEL_FOOTPRINTS."""
    out = {}
    for sp in sorted((ROOT / "models").glob("*/summary.json")):
        sm = json.load(open(sp, encoding="utf-8"))
        jp = sp.parent / "joints.json"
        if not jp.exists():
            continue
        jj = json.load(open(jp, encoding="utf-8"))
        ent = [(e["name"], np.array([e["scene"][0], e["scene"][2]], float)) for e in jj["entries"]]
        MODEL_FOOTPRINTS.extend(shapely.Polygon(fp).buffer(0) for fp in jj.get("footprints", []))
        for i in [sm["id"], *sm.get("aliases", [])]:
            out[i] = ent
    return out


MODEL_FOOTPRINTS = []
MODEL_ENTRIES = model_entries()
MODEL_ZONE = shapely.ops.unary_union(MODEL_FOOTPRINTS).buffer(6.0) if MODEL_FOOTPRINTS else None
MODEL_DOORS = {"on": True}  # off while snapping the steps and galleries a model draws itself: they keep the box's sides, as traced


ROWTYPE = {r["id"]: r["type"] for r in rows(ROOT / "research/buildings.csv")}
ROWS = {r["id"]: r for r in rows(ROOT / "research/buildings.csv")}


def load_world():
    fc = json.load(open(SITE_DATA / "halls_1860.geojson", encoding="utf-8"))
    boxes = [Box(f) for f in fc["features"]]
    by_row = defaultdict(list)
    for b in boxes:
        by_row[b.bid].append(b)
        for also in b.p.get("also", []) or []:
            by_row[also].append(b)
    for r, target in fc.get("shared_rows", {}).items():
        by_row[r] = by_row.get(target, [])
    water = unary_union([xz_geom(f["geometry"]).buffer(0) for f in layer("water_1860")]).buffer(0)
    waters = [(f["properties"]["id"], f["properties"].get("name_zh", ""), xz_geom(f["geometry"]).buffer(0)) for f in layer("water_1860")]
    bridges = {}
    for f in layer("bridges_1860"):
        bridges[f["properties"]["id"]] = (f["properties"], xz_geom(f["geometry"]))
    gates = {}
    for f in layer("walls_1860"):
        if f["properties"].get("kind") == "gate":
            gates[f["properties"]["id"]] = (f["properties"], np.asarray(xz_geom(f["geometry"]).coords[0]))
    walls = [xz_geom(f["geometry"]) for f in layer("walls_1860") if f["geometry"]["type"] == "LineString"]
    wall_union = unary_union(walls)
    for b in boxes:
        if not b.walk_through and b.poly.intersects(wall_union):
            b.walk_through = b.in_wall = True  # the garden wall stops at a hall standing in its line (boxes1860.py): that hall is the way through the wall
    st = json.load(open(ROOT / "site/reconstruction/generated/structures.json", encoding="utf-8"))
    wall_segs = unary_union([LineString([(s[0], s[1]), (s[2], s[3])]) for s in st["wall"]["segments"]]).buffer(0.5)
    scenes = {f["properties"]["id"]: (f["properties"], xz_geom(f["geometry"]).buffer(0)) for f in layer("scenes_1860")}
    return boxes, by_row, water, waters, bridges, gates, walls, wall_segs, scenes


# ------------------------------------------------------------------ routing on a grid

class Router:
    def __init__(self, boxes, water, bridges, wall_segs):
        solid = [b.poly for b in boxes if not b.walk_through]
        self.solid_boxes = boxes
        self._union_plain = unary_union(solid)
        # Round 13: where a detailed model stands, its own footprints (models/<ID>-<slug>/joints.json) are the obstacle, not its boxes; the steps and galleries it draws keep the boxes (MODEL_DOORS off)
        self._union_model = unary_union([b.poly for b in boxes if not b.walk_through and b.bid not in MODEL_ENTRIES] + MODEL_FOOTPRINTS)
        shapely.prepare(self._union_plain)
        shapely.prepare(self._union_model)
        self.box_tree = shapely.STRtree([b.poly for b in boxes])
        self.water = water.union(unary_union([g.buffer(3.0) for _, g in bridges.values()]))  # a boat passes under a bridge
        self.water_in = self.water.buffer(-1.0)
        shapely.prepare(self.water_in)
        bridge_lanes = unary_union([g.buffer(2.0, cap_style="flat").union(Point(g.coords[0]).buffer(2.5)).union(Point(g.coords[-1]).buffer(2.5)) for _, g in bridges.values()])
        self.wet = water.difference(bridge_lanes)  # water a land way may not cross
        self.walls = wall_segs
        shapely.prepare(self.wet)
        shapely.prepare(self.walls)
        self.dry = None

    @property
    def box_union(self):
        return self._union_model if MODEL_DOORS["on"] else self._union_plain

    def land_obstacle(self, allow_boxes=()):
        if not allow_boxes:
            return self.box_union, self.wet, self.walls
        model = MODEL_DOORS["on"]
        keep = unary_union([b.poly for b in self.solid_boxes if not b.walk_through and b.id not in allow_boxes and not (model and b.bid in MODEL_ENTRIES)] + (MODEL_FOOTPRINTS if model else []))
        shapely.prepare(keep)
        return keep, self.wet, self.walls

    def blocked_line(self, line, obst, boat=False):
        """Length of the line that runs where it may not."""
        if boat:
            # a boat keeps to the water; its first and last 10 m leave the landing, over the bank
            if line.length < 24:
                return 0.0
            mid = shapely.ops.substring(line, 10, line.length - 10)
            return mid.difference(self.water_in).length
        boxes_, wet, walls = obst
        return line.intersection(boxes_).length + line.intersection(wet).length + line.intersection(walls).length

    def route(self, a, b, obst, prefer=None, boat=False, max_m=None):
        """Shortest way from a to b on a 0.75 m grid round the obstacles, kept near `prefer` (a line). None if no way."""
        a, b = np.asarray(a, float), np.asarray(b, float)
        lo = np.minimum(a, b) - MARGIN_M
        hi = np.maximum(a, b) + MARGIN_M
        if prefer is not None:
            pb = np.asarray(prefer.bounds)
            lo = np.minimum(lo, pb[:2] - 10)
            hi = np.maximum(hi, pb[2:] + 10)
        nx, nz = int((hi[0] - lo[0]) / GRID_M) + 1, int((hi[1] - lo[1]) / GRID_M) + 1
        if nx * nz > 900_000:
            return None
        xs = lo[0] + np.arange(nx) * GRID_M
        zs = lo[1] + np.arange(nz) * GRID_M
        X, Z = np.meshgrid(xs, zs)
        if boat:
            win = shapely.clip_by_rect(self.water, lo[0] - 5, lo[1] - 5, hi[0] + 5, hi[1] + 5)
            near_end = (np.hypot(X - a[0], Z - a[1]) < 14) | (np.hypot(X - b[0], Z - b[1]) < 14)
            wide = shapely.contains_xy(win.buffer(-BOAT_CLEAR_M[0]), X, Z)
            mid = shapely.contains_xy(win.buffer(-BOAT_CLEAR_M[1]), X, Z)
            narrow = shapely.contains_xy(win.buffer(-BOAT_CLEAR_M[2]), X, Z)
            free = narrow | (near_end & shapely.contains_xy(win.buffer(1.0), X, Z))
            cost = np.where(wide, 1.0, np.where(mid, 2.0, 4.0))
        else:
            boxes_, wet, walls = obst
            box_win = shapely.clip_by_rect(boxes_, lo[0] - 1, lo[1] - 1, hi[0] + 1, hi[1] + 1).buffer(CLEAR_M)
            wet_win = shapely.clip_by_rect(wet, lo[0] - 1, lo[1] - 1, hi[0] + 1, hi[1] + 1).buffer(CLEAR_M)
            wall_win = shapely.clip_by_rect(walls, lo[0] - 1, lo[1] - 1, hi[0] + 1, hi[1] + 1)
            bad = unary_union([box_win, wet_win, wall_win])
            free = ~shapely.contains_xy(bad, X, Z)
        if not boat:
            cost = np.ones_like(X)
        if prefer is not None:
            d = shapely.distance(prefer, shapely.points(X.ravel(), Z.ravel())).reshape(X.shape)
            cost = cost * (1.0 + np.clip((d - 1.0) / 4.0, 0, 1.5))
        ia = self._nearest_free(free, (a - lo) / GRID_M)
        ib = self._nearest_free(free, (b - lo) / GRID_M)
        if ia is None or ib is None:
            return None
        idx = -np.ones(free.shape, dtype=np.int64)
        fz, fx = np.nonzero(free)
        idx[fz, fx] = np.arange(len(fz))
        src, dst, w = [], [], []
        for dz, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
            z0, z1 = max(0, -dz), nz - max(0, dz)
            x0, x1 = max(0, -dx), nx - max(0, dx)
            A = idx[z0:z1, x0:x1]
            B = idx[z0 + dz:z1 + dz, x0 + dx:x1 + dx]
            ok = (A >= 0) & (B >= 0)
            step = math.hypot(dx, dz) * GRID_M
            ca = cost[z0:z1, x0:x1][ok]
            cb = cost[z0 + dz:z1 + dz, x0 + dx:x1 + dx][ok]
            src.append(A[ok])
            dst.append(B[ok])
            w.append(step * (ca + cb) / 2)
        src, dst, w = np.concatenate(src), np.concatenate(dst), np.concatenate(w)
        n = len(fz)
        g = coo_matrix((np.concatenate([w, w]), (np.concatenate([src, dst]), np.concatenate([dst, src]))), shape=(n, n)).tocsr()
        s, t = idx[ia[1], ia[0]], idx[ib[1], ib[0]]
        dist, pred = dijkstra(g, indices=s, return_predecessors=True)
        if not np.isfinite(dist[t]):
            return None
        chain = [t]
        while chain[-1] != s:
            chain.append(pred[chain[-1]])
        chain.reverse()
        pts = [a] + [np.array([xs[fx[k]], zs[fz[k]]]) for k in chain] + [b]
        line = LineString(pts)
        for tol in (0.6, 0.3, 0.0):
            simple = line.simplify(tol) if tol else line
            if self.blocked_line(simple, obst, boat) <= self.blocked_line(line, obst, boat) + 0.05:
                line = simple
                break
        if max_m and line.length > max_m:
            return None
        return line

    @staticmethod
    def _nearest_free(free, ij):
        i, j = int(round(ij[0])), int(round(ij[1]))
        h, w = free.shape
        for r in range(0, 14):
            best = None
            for dj in range(-r, r + 1):
                for di in range(-r, r + 1):
                    if max(abs(di), abs(dj)) != r:
                        continue
                    x, z = i + di, j + dj
                    if 0 <= x < w and 0 <= z < h and free[z, x]:
                        d = di * di + dj * dj
                        if best is None or d < best[0]:
                            best = (d, (x, z))
            if best:
                return best[1]
        return None


# ------------------------------------------------------------------ snapping

class Snapper:
    def __init__(self, boxes, by_row, bridges, gates, water, router, scenes):
        self.boxes, self.by_row, self.bridges, self.gates, self.water, self.router, self.scenes = boxes, by_row, bridges, gates, water, router, scenes
        self.by_parent = defaultdict(list)
        for b in boxes:
            self.by_parent[b.parent].append(b)
        self.box_of = {b.id: b for b in boxes}
        self.gate_box = {b.bid: b for b in boxes if b.bid.startswith("G")}

    def free(self, p):
        q = Point(p)
        return not self.router.wet.contains(q) and not self.router.box_union.contains(q)

    def door(self, box, ref, prefer_front=True, nxt=None):
        if box.walk_through and not (MODEL_DOORS["on"] and MODEL_ENTRIES.get(box.bid)):  # Round 15: a court or terrace a model draws is met at the model's entries
            return box.c.copy(), "through", box
        best = None
        for side, p in box.doors().items():
            d = float(np.hypot(*(p - ref)))
            if nxt is not None:
                d += float(np.hypot(*(p - np.asarray(nxt, float))))  # the door with the least detour on the way to the line's next point
            if side == "front" and prefer_front:
                d *= 0.9
            if not self.free(p):
                d += 1000
            if best is None or d < best[0]:
                best = (d, p, side)
        return best[1].copy(), best[2], box

    def anchor(self, ident, ref, done, landings, nxt=None):
        """The point an end with this id meets, and what it is: (xz, kind, detail)."""
        ident = (ident or "").strip()
        if not ident:
            return None
        if ident in landings:
            return landings[ident]["xz"].copy(), "landing", ident
        if ident in done:
            line = done[ident]
            if line.geom_type == "Point":
                return np.asarray(line.coords[0]), "path", ident
            q = line.interpolate(line.project(Point(ref)))
            return np.array([q.x, q.y]), "path", ident
        if ident.startswith("BR") and ident in self.bridges:
            g = self.bridges[ident][1]
            ends = [np.asarray(g.coords[0]), np.asarray(g.coords[-1])]
            e = min(ends, key=lambda p: np.hypot(*(p - ref)))
            return self.land_end(e), "bridge", ident
        if ident in self.gates:
            if ident in self.gate_box:
                return self.gate_box[ident].c.copy(), "gate", ident
            gp = self.gates[ident][1]
            near = [b for b in self.boxes if b.gate and np.hypot(*(b.c - gp)) < 8]
            if near:
                return near[0].c.copy(), "gate", ident
            return gp.copy(), "gate", ident
        if ident in self.by_row and self.by_row[ident]:
            box = min(self.by_row[ident], key=lambda b: np.hypot(*(b.c - ref)))
            p, side, box = self.door(box, ref, nxt=nxt)
            return p, ("gate" if box.gate else "door"), f"{box.id}:{side}"
        if ident in self.by_parent and self.by_parent[ident]:
            box = min(self.by_parent[ident], key=lambda b: np.hypot(*(b.c - ref)))
            p, side, box = self.door(box, ref, nxt=nxt)
            return p, ("gate" if box.gate else "door"), f"{box.id}:{side}"
        r = ROWS.get(ident)
        if r and r.get("lat"):
            p = np.asarray(to_xz(float(r["lon"]), float(r["lat"])))
            return self.land_end(p), "row point", ident
        return None

    def land_end(self, p):
        """A point on land: itself, or the nearest land within 6 m."""
        q = Point(p)
        if not self.router.wet.contains(q):
            return np.asarray(p, float)
        b = self.router.wet.boundary
        n = b.interpolate(b.project(q))
        v = np.array([n.x, n.y]) - p
        L = np.hypot(*v) or 1
        return np.array([n.x, n.y]) + v / L * SHORE_IN_M if L < 6 else np.asarray(p, float)


def shore_point(p, water):
    q = Point(p)
    b = water.boundary
    n = b.interpolate(b.project(q))
    if q.distance(n) > SHORE_MAX_M:
        return np.asarray(p, float), None, float(q.distance(n))
    s = np.array([n.x, n.y])
    # which way is the water: probe round the shore point
    dirs = [np.array([math.cos(t), math.sin(t)]) for t in np.linspace(0, 2 * math.pi, 16, endpoint=False)]
    wet = [d for d in dirs if water.contains(Point(s + d * 3))]
    if not wet:
        return s, None, float(q.distance(n))
    w = np.mean(wet, axis=0)
    w = w / (np.linalg.norm(w) or 1)
    return s - w * SHORE_IN_M, w, float(q.distance(n))


def bearing(v):
    """A scene direction (x east, z south) as a compass bearing."""
    return round((math.degrees(math.atan2(v[0], -v[1])) + 360) % 360, 1)


# ------------------------------------------------------------------ main

def main():
    boxes, by_row, water, waters, bridges, gates, walls, wall_segs, scenes = load_world()
    router = Router(boxes, water, bridges, wall_segs)
    snap = Snapper(boxes, by_row, bridges, gates, water, router, scenes)
    traces = rows(PATHS / "traces.csv")
    grades = {r["key"]: r for r in rows(PATHS / "grades.csv")}
    photo_of = {r["key"]: r["photo_id"] for r in rows(PATHS / "album.csv")}

    def warp(t):
        pts = [tuple(map(float, p.split())) for p in t["points_px"].split(";") if p.strip()]
        lon, lat = georef.plan_to_wgs84(np.array([p[0] for p in pts]), np.array([p[1] for p in pts]))
        x, z = to_xz(np.asarray(lon), np.asarray(lat))
        return np.column_stack([x, z])

    def grade(t):
        g = grades.get(t["key"], {})
        conf = t["confidence"] or "C"
        basis = "s01" if conf == "B" else "typology"
        srcs = [s for s in (t["sources"] or "S01").split(";") if s]
        leaf = [photo_of[k] for k in t["leaf"].split(";") if k in photo_of] if t["leaf"] else []
        if leaf:
            conf, basis = "A", "leaf"
            srcs += ["S08"] if any(p <= "P0040" for p in leaf) else ["S71"]
        if g:
            conf = g["confidence"] or conf
            basis = g["basis"] or basis
            srcs += [s for s in g["sources"].split(";") if s]
        return conf, basis, sorted(set(srcs), key=srcs.index), sorted(set(leaf))

    # 1. landings and docks first: other lines end on them
    landings = {}
    for t in traces:
        if t["kind"] not in POINT_KINDS:
            continue
        raw = warp(t)[0]
        p, wdir, gap = shore_point(raw, water)
        wid, wname = min(((wid_, nm, poly.distance(Point(p))) for wid_, nm, poly in waters), key=lambda x: x[2])[:2]
        conf, basis, srcs, leaf = grade(t)
        landings[t["key"]] = {"xz": p, "raw": raw, "dir": wdir, "gap_before": gap, "t": t, "water_id": wid, "water_name": wname, "conf": conf, "basis": basis, "sources": srcs, "leaf": leaf}

    # 2. lines, in an order where a line another ends on comes first
    lines_t = [t for t in traces if t["kind"] not in POINT_KINDS]
    keyset = {t["key"] for t in lines_t}
    deps = {t["key"]: {x for x in (t["from_id"], t["to_id"]) if x in keyset and x != t["key"]} for t in lines_t}
    order, seen = [], set()

    def visit(k, stack=()):
        if k in seen or k in stack:
            return
        for d in sorted(deps[k]):
            visit(d, stack + (k,))
        seen.add(k)
        order.append(k)

    for t in lines_t:
        visit(t["key"])
    by_key = {t["key"]: t for t in lines_t}
    raw_lines = {t["key"]: LineString(warp(t)) if len(t["points_px"].split(";")) > 1 else Point(warp(t)[0]) for t in lines_t}
    done = {}
    paths = []
    for k in order:
        t = by_key[k]
        pts = warp(t)
        if len(pts) < 2:
            continue
        boat = t["kind"] == "boat_route"
        ends = []
        MODEL_DOORS["on"] = t["kind"] not in ("steps", "gallery")
        if MODEL_DOORS["on"] and MODEL_ZONE is not None and (t["from_id"] in MODEL_ENTRIES or t["to_id"] in MODEL_ENTRIES):
            # Round 13: a way that ends at a detailed model: its traced points inside the model (and 6 m round it) give way to the model; the end snaps from the first point beyond
            pts = np.array([p for j, p in enumerate(pts) if j in (0, len(pts) - 1) or not MODEL_ZONE.contains(Point(p))])
        for i, (ident, end, nxt) in enumerate(((t["from_id"], pts[0], pts[1]), (t["to_id"], pts[-1], pts[-2]))):
            ref = done if ident in done else {**raw_lines, **done}
            model_end = MODEL_DOORS["on"] and ident in MODEL_ENTRIES and MODEL_ZONE is not None and MODEL_ZONE.contains(Point(end))
            if model_end:
                end = nxt
            a = snap.anchor(ident, end, ref, landings, nxt=nxt)
            far = SNAP_ID_MAX_XY_M if ident.startswith("XY") or t["scene"].startswith("XY") else SNAP_ID_MAX_M
            if a is not None and np.hypot(*(a[0] - end)) > far and not boat and not model_end:
                b = nearest_anything(end, snap, done, landings, boxes, t["scene"])
                a = (b[0], b[1], f"free: {b[2]} ({ident} lies {np.hypot(*(a[0] - end)):.0f} m off)") if b is not None else None
            if a is None and not boat:
                a = nearest_anything(end, snap, done, landings, boxes, t["scene"])
                if a is not None:
                    a = (a[0], a[1], "free: " + a[2])
            if a is None:
                ends.append((end, "free", "", float("nan")))
            else:
                ends.append((a[0], a[1], a[2], float(np.hypot(*(a[0] - end)))))
        pts[0], pts[-1] = ends[0][0], ends[1][0]
        line = LineString(pts)
        allow = set()
        if t["in_box_row"]:
            allow |= {b.id for b in by_row.get(t["in_box_row"], [])}
        if t["kind"] == "steps":  # steps climb onto the platform of the hall they lead to
            allow |= {e[2].split(":")[0] for e in ends if e[1] in ("door", "gate") and e[2]}
        obst = router.land_obstacle(allow) if not boat else None
        before = router.blocked_line(line, obst, boat)
        rerouted = 0.0
        if before > 0.05:
            new = reroute(line, router, obst, boat)
            if new is not None:
                rerouted = round(float(max(line.distance(Point(c)) for c in new.coords)), 1)
                line = new
        after = router.blocked_line(line, obst, boat)
        conf, basis, srcs, leaf = grade(t)
        width = float(t["width_m"]) if t["width_m"] else WIDTH[t["kind"]]
        done[k] = line
        paths.append({
            "id": k, "kind": t["kind"], "name_zh": t["name_zh"], "scene": t["scene"], "width_m": round(width, 1),
            "width_source": "drawn on S01" if t["width_m"] else "typology, C", "surface": SURFACE[t["kind"]],
            "from_id": t["from_id"], "to_id": t["to_id"], "from_at": ends[0][2] or ends[0][1], "to_at": ends[1][2] or ends[1][1],
            "gap_before_m": [None if math.isnan(e[3]) else round(e[3], 1) for e in ends],
            "sources": ";".join(srcs), "confidence": conf, "pos_confidence": "B", "assumed": conf == "C", "basis": basis,
            "leaf": ";".join(leaf), "in_box": ";".join(sorted(allow)), "drawn": t["drawn_on_s01"], "rerouted_m": rerouted,
            "blocked_before_m": round(before, 1), "blocked_m": round(after, 1), "note": t["note"], "_line": line,
        })

    MODEL_DOORS["on"] = True
    # 3. bridge approaches
    land_lines = [p["_line"] for p in paths if p["kind"] != "boat_route"]
    approaches = []
    no_approach = []
    for bid, (bp, g) in sorted(bridges.items()):
        for n, e in enumerate((np.asarray(g.coords[0]), np.asarray(g.coords[-1])), 1):
            e = snap.land_end(e)
            pe = Point(e)
            near = [L for L in land_lines if L.distance(pe) <= 1.0]
            if near:
                continue
            target = nearest_network(e, land_lines, boxes, snap, landings, exclude_bridge=g, max_m=APPROACH_MAX_M)
            if target is None:
                no_approach.append((bid, n, "nothing to reach within 60 m on this bank"))
                continue
            line = LineString([e, target[0]])
            obst = router.land_obstacle()
            if router.blocked_line(line, obst) > 0.05:
                line = reroute(line, router, obst, False, max_m=APPROACH_MAX_M * 1.6)
            if line is None or router.blocked_line(line, obst) > 0.05:
                no_approach.append((bid, n, "no dry way round the boxes within 60 m"))
                continue
            pid = f"BA-{bid}-{n}"
            approaches.append({
                "id": pid, "kind": "bridge_approach", "name_zh": "", "scene": bp.get("building_id", "").split("-")[0], "width_m": WIDTH["bridge_approach"], "width_source": "typology, C",
                "surface": SURFACE["bridge_approach"], "from_id": bid, "to_id": target[2], "from_at": "bridge", "to_at": target[1], "gap_before_m": [0.0, 0.0],
                "sources": "S01", "confidence": "C", "pos_confidence": "C", "assumed": True, "basis": "reach", "leaf": "", "in_box": "", "drawn": "nothing: the bridge end must lead somewhere",
                "rerouted_m": 0.0, "blocked_before_m": 0.0, "blocked_m": 0.0, "note": f"Added so that {bid}'s end {n} reaches the nearest way; no source draws it.", "_line": line,
            })
            land_lines.append(line)
    paths += approaches

    # 4. minimal C links inside each compound
    reach = []
    unreached = []
    for sid in sorted(scenes):
        sp, spoly = scenes[sid]
        kids = [b for b in boxes if b.parent == sid and b.p.get("shape") != "wall"]
        if not kids:
            continue
        zone = spoly.buffer(40)
        net = [L for L in land_lines if L.intersects(zone)]
        entries = []
        if not net:
            for gid, (gp, gxz) in gates.items():
                if spoly.buffer(20).contains(Point(gxz)):
                    entries.append(LineString([gxz, gxz + 0.01]))
            for bid, (bp, g) in bridges.items():
                for e in (g.coords[0], g.coords[-1]):
                    if spoly.buffer(10).contains(Point(e)):
                        entries.append(LineString([snap.land_end(np.asarray(e)), snap.land_end(np.asarray(e)) + 0.01]))
            for lk, L in landings.items():
                if spoly.buffer(15).contains(Point(L["xz"])):
                    entries.append(LineString([L["xz"], L["xz"] + 0.01]))
            net = entries
        kids.sort(key=lambda b: -(b.hf * b.hd))
        n = 0
        for b in kids:
            doors = list(b.doors().values()) if not b.walk_through else [b.c]
            if any(L.distance(Point(d)) <= 1.0 for L in net for d in doors) or any(L.intersects(b.poly) for L in net if b.walk_through):
                continue
            if not net:
                net = [LineString([snap.door(b, b.c + b.a)[0], snap.door(b, b.c + b.a)[0] + 0.01])]  # no entry known: the biggest hall's door is the root
                continue
            best = None
            for side, d in b.doors().items() if not b.walk_through else [("through", b.c)]:
                if not snap.free(d) and not b.walk_through:
                    continue
                for L in net:
                    q = L.interpolate(L.project(Point(d)))
                    dd = q.distance(Point(d)) * (0.85 if side == "front" else 1.0)
                    if best is None or dd < best[0]:
                        best = (dd, d, np.array([q.x, q.y]), side)
            if best is None or best[0] > REACH_MAX_M:
                unreached.append((sid, b.id, "no free door" if best is None else f"nearest way {best[0]:.0f} m"))
                continue
            line = LineString([best[1], best[2]])
            obst = router.land_obstacle({b.id})
            if line.length < 0.05:
                continue
            if router.blocked_line(line, obst) > 0.05:
                line = reroute(line, router, obst, False, max_m=REACH_MAX_M * 1.6)
            if line is None or router.blocked_line(line, obst) > 0.05:
                unreached.append((sid, b.id, "no dry way round the boxes"))
                continue
            n += 1
            pid = f"RC-{sid}-{n:02d}"
            reach.append({
                "id": pid, "kind": "courtyard_path", "name_zh": "", "scene": sid, "width_m": 1.5, "width_source": "typology, C", "surface": SURFACE["courtyard_path"],
                "from_id": b.bid, "to_id": "", "from_at": f"{b.id}:{best[3]}", "to_at": "path", "gap_before_m": [0.0, 0.0], "sources": "S01", "confidence": "C", "pos_confidence": "C",
                "assumed": True, "basis": "reach", "leaf": "", "in_box": "", "drawn": "nothing: reach only", "rerouted_m": 0.0, "blocked_before_m": 0.0, "blocked_m": 0.0,
                "note": "Added only so that the hall is reachable: no source draws it.", "_line": line,
            })
            net.append(line)
            land_lines.append(line)
    paths += reach

    # 4b. a traced end that meets nothing (its id misread, or none given) gets one C link to the nearest way, door or gate within 40 m
    dangling = []
    joints = joint_points(boxes, gates, bridges, landings, snap)
    landp = [q for q in paths if q["kind"] != "boat_route"]
    ltree = shapely.STRtree([q["_line"] for q in landp])
    for p in [q for q in landp if not q["id"].startswith(("BA-", "RC-"))]:
        L = p["_line"]
        for n, c in enumerate((L.coords[0], L.coords[-1]), 1):
            e = np.asarray(c)
            near = [landp[int(j)]["_line"] for j in ltree.query(Point(e).buffer(DANGLE_MAX_M)) if landp[int(j)] is not p]
            if meets(e, near, joints) <= JOINT_TOL_M:
                continue
            others = near
            target = nearest_network(e, others, boxes, snap, landings, exclude_bridge=None, max_m=DANGLE_MAX_M)
            line = None
            if target is not None:
                line = LineString([e, target[0]])
                obst = router.land_obstacle()
                if router.blocked_line(line, obst) > 0.05:
                    line = reroute(line, router, obst, False, max_m=DANGLE_MAX_M * 1.6)
                if line is not None and router.blocked_line(line, obst) > 0.05:
                    line = None
            if line is None:
                dangling.append((p["id"], n, "nothing to join within 40 m"))
                continue
            paths.append({
                "id": f"DL-{p['id']}-{n}", "kind": "courtyard_path", "name_zh": "", "scene": p["scene"], "width_m": 1.5, "width_source": "typology, C", "surface": SURFACE["courtyard_path"],
                "from_id": p["id"], "to_id": target[2], "from_at": "path", "to_at": target[1], "gap_before_m": [0.0, 0.0], "sources": "S01", "confidence": "C", "pos_confidence": "C",
                "assumed": True, "basis": "reach", "leaf": "", "in_box": "", "drawn": "nothing: the traced end meets nothing", "rerouted_m": 0.0, "blocked_before_m": 0.0, "blocked_m": 0.0,
                "note": f"Added so that the {'start' if n == 1 else 'end'} of {p['id']} meets a way: the trace ends {meets(e, others, joints):.0f} m from anything. No source draws it.", "_line": line,
            })
    with open(PATHS / "dangling.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["path", "end", "reason"])
        w.writerows(dangling)

    # 5. routes, which may add a C line where the network falls apart; then the layers
    routes, links = build_routes(paths, landings, boxes, by_row, bridges, gates, snap, router)
    paths += links
    feats = []
    for p in paths:
        line = p.pop("_line")
        p["length_m"] = round(line.length, 1)
        feats.append({"type": "Feature", "properties": {k: v for k, v in p.items()}, "geometry": {"type": "LineString", "coordinates": ll_coords(line)}})
        p["_line"] = line
    lfeats = []
    for k, L in landings.items():
        t = L["t"]
        lon, lat = to_lonlat(L["xz"][0], L["xz"][1])
        lfeats.append({"type": "Feature", "properties": {
            "id": k, "kind": t["kind"], "name_zh": t["name_zh"], "scene": t["scene"], "serves": ";".join(x for x in (t["from_id"], t["to_id"]) if x),
            "water": t["water"] or L["water_name"], "water_id": L["water_id"], "facing_deg": bearing(L["dir"]) if L["dir"] is not None else None,
            "gap_before_m": round(L["gap_before"], 1), "sources": ";".join(L["sources"]), "confidence": L["conf"], "pos_confidence": "B", "assumed": L["conf"] == "C",
            "basis": L["basis"], "leaf": ";".join(L["leaf"]), "drawn": t["drawn_on_s01"], "note": t["note"]},
            "geometry": {"type": "Point", "coordinates": [round(float(lon), 7), round(float(lat), 7)]}})

    write("paths_1860", feats, CREDIT)
    write("landings_1860", lfeats, CREDIT)
    write("routes_1860", routes, CREDIT + " Routes: the shortest way through these lines between waypoints chosen from the sources cited.")

    # 6. what it did
    by_kind = defaultdict(lambda: [0, 0.0])
    by_conf = defaultdict(lambda: [0, 0.0])
    for f in feats:
        p = f["properties"]
        by_kind[p["kind"]][0] += 1
        by_kind[p["kind"]][1] += p["length_m"]
        by_conf[p["confidence"]][0] += 1
        by_conf[p["confidence"]][1] += p["length_m"]
    gaps = [g for f in feats if not f["properties"]["id"].startswith(("BA-", "RC-")) for g in f["properties"]["gap_before_m"] if g is not None]
    print(f"{len(feats)} lines: {len(paths) - len(approaches) - len(reach) - len(links) - sum(1 for p in paths if p['id'].startswith('DL-'))} traced, {len(approaches)} bridge approaches added, {len(reach)} minimal links added, {len(links)} route links {[p['id'] for p in links]}, {sum(1 for p in paths if p['id'].startswith('DL-'))} links at dangling ends ({len(dangling)} left: {dangling[:6]}); {len(lfeats)} landings and docks; {len(routes)} routes")
    print("by kind:", {k: (v[0], round(v[1])) for k, v in sorted(by_kind.items())})
    print("by confidence:", {k: (v[0], round(v[1])) for k, v in sorted(by_conf.items())})
    if gaps:
        g = np.array(gaps)
        print(f"traced ends, gap before snapping: median {np.median(g):.1f} m, 90% {np.percentile(g, 90):.1f} m, max {g.max():.1f} m (n {len(g)})")
    print(f"rerouted round a box, wall or water: {sum(1 for p in paths if p['rerouted_m'] > 0)}; still blocked: {[(p['id'], p['blocked_m']) for p in paths if p['blocked_m'] > 0.05][:20]}")
    print(f"bridge ends without an approach: {len(no_approach)} {no_approach[:12]}")
    print(f"halls no link could reach: {len(unreached)} {unreached[:8]}")
    # what has no way, and why: read by tools/check_paths.py
    with open(PATHS / "bridge_ends.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["bridge", "end", "approach", "reason"])
        land = [(p["id"], p["_line"]) for p in paths if p["kind"] != "boat_route"]
        for bid, (bp, g) in sorted(bridges.items()):
            for n, e in enumerate((g.coords[0], g.coords[-1]), 1):
                e = Point(snap.land_end(np.asarray(e)))
                near = [pid for pid, L in land if L.distance(e) <= 1.0]
                reason = next((r for b_, n_, r in no_approach if b_ == bid and n_ == n), "")
                w.writerow([bid, n, ";".join(sorted(near)), "" if near else reason])
    with open(PATHS / "unreached.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["scene", "box", "reason"])
        w.writerows(sorted(unreached))


def joint_points(boxes, gates, bridges, landings, snap):
    """Everything a way's end may meet, but other ways: doors, boxes walked through, gates, bridge ends, landings."""
    pts = [d for b in boxes if not b.walk_through for d in b.doors().values()]
    pts += [g[1] for g in gates.values()]
    pts += [snap.land_end(np.asarray(c)) for _, g in bridges.values() for c in (g.coords[0], g.coords[-1])]
    pts += [L["xz"] for L in landings.values()]
    through = unary_union([b.poly.buffer(0.3) for b in boxes if b.walk_through])
    return np.array(pts), through


def meets(e, lines, joints):
    pts, through = joints
    d = float(np.min(np.hypot(pts[:, 0] - e[0], pts[:, 1] - e[1])))
    d = min(d, through.distance(Point(e)))
    q = Point(e)
    for L in lines:
        if d <= JOINT_TOL_M:
            break
        d = min(d, L.distance(q))
    return d


def nearest_anything(p, snap, done, landings, boxes, scene):
    best = None
    q = Point(p)
    for k, L in done.items():
        d = L.distance(q)
        if best is None or d < best[0]:
            r = L.interpolate(L.project(q))
            best = (d, np.array([r.x, r.y]), "path", k)
    for k, L in landings.items():
        d = float(np.hypot(*(L["xz"] - p)))
        if best is None or d < best[0]:
            best = (d, L["xz"].copy(), "landing", k)
    for bid, (bp, g) in snap.bridges.items():
        for e in (g.coords[0], g.coords[-1]):
            d = q.distance(Point(e))
            if best is None or d < best[0]:
                best = (d, snap.land_end(np.asarray(e)), "bridge", bid)
    for b in boxes:
        if b.parent != scene and b.bid != scene:
            continue
        pt, side, _ = snap.door(b, p)
        d = float(np.hypot(*(pt - p)))
        if best is None or d < best[0]:
            best = (d, pt, "door", f"{b.id}:{side}")
    if best is None or best[0] > SNAP_FREE_M:
        return None
    return best[1], best[2], best[3]


def nearest_network(e, lines, boxes, snap, landings, exclude_bridge, max_m):
    q = Point(e)
    best = None
    for L in lines:
        d = L.distance(q)
        if d < 1.0 or d > max_m:
            continue
        r = L.interpolate(L.project(q))
        if best is None or d < best[0]:
            best = (d, np.array([r.x, r.y]), "path", "")
    for b in boxes:
        if np.hypot(*(b.c - e)) > max_m + 30:
            continue
        pt, side, _ = snap.door(b, e)
        d = float(np.hypot(*(pt - e)))
        if d <= max_m and (best is None or d < best[0]) and snap.free(pt):
            best = (d, pt, "door" if not b.gate else "gate", b.bid)
    if best is None:
        return None
    return best[1], best[2] if best[2] != "door" else "door", best[3]


def reroute(line, router, obst, boat, max_m=None):
    """Route the whole line again round what it crosses, kept near the trace."""
    c = np.asarray(line.coords)
    new = router.route(c[0], c[-1], obst, prefer=line, boat=boat, max_m=max_m)
    return new


def write(name, feats, credit):
    fc = {"type": "FeatureCollection", "name": name, "crs_note": "WGS84 (EPSG:4326)", "attribution": credit, "features": feats}
    text = json.dumps(fc, ensure_ascii=False, separators=(",", ":")) + "\n"
    (LAYERS / f"{name}.geojson").write_text(text, encoding="utf-8")
    (SITE_DATA / f"{name}.geojson").write_text(text, encoding="utf-8")


# ------------------------------------------------------------------ routes

def build_routes(paths, landings, boxes, by_row, bridges, gates, snap, router):
    """Each route of routes.csv as the shortest way through the network between its waypoints."""
    defs = rows(PATHS / "routes.csv")
    if not defs:
        return [], []
    key = lambda p: (round(float(p[0]), 1), round(float(p[1]), 1))  # noqa: E731
    nodes = {}

    def node(p):
        k = key(p)
        if k not in nodes:
            nodes[k] = len(nodes)
        return nodes[k]

    edges = defaultdict(list)  # node -> [(node, weight, edge info)]

    def add(a, b, w, info):
        edges[a].append((b, w, info))
        edges[b].append((a, w, info))

    # every line, split at the points where other lines meet it
    cut = defaultdict(set)
    land = [p for p in paths if p["kind"] != "boat_route"]
    ends = [(p, np.asarray(p["_line"].coords[i])) for p in paths for i in (0, -1)]
    tree = shapely.STRtree([p["_line"] for p in paths])
    for p, e in ends:
        for j in tree.query(Point(e).buffer(JOINT_TOL_M)):
            q = paths[int(j)]
            if q is p:
                continue
            if q["_line"].distance(Point(e)) <= JOINT_TOL_M:
                cut[q["id"]].add(round(q["_line"].project(Point(e)), 2))
    for p in paths:
        if p["blocked_m"] > 0.05:
            continue  # a line still crossing a box, a wall, water or land carries no route
        L = p["_line"]
        ds = sorted({0.0, round(L.length, 2)} | cut[p["id"]])
        f = {"A": 1.0, "B": 1.0, "C": 1.35}[p["confidence"]]
        for d0, d1 in zip(ds, ds[1:]):
            if d1 - d0 < 0.01:
                continue
            seg = shapely.ops.substring(L, d0, d1)
            a, b = node(seg.coords[0]), node(seg.coords[-1])
            # the points where other lines meet it are not on this line's vertices: join them
            add(a, b, seg.length * f, {"id": p["id"], "line": seg, "boat": p["kind"] == "boat_route"})
        for d in cut[p["id"]]:
            q = L.interpolate(d)
            for e in (n for n in ends if n[0] is not p):
                if np.hypot(e[1][0] - q.x, e[1][1] - q.y) <= JOINT_TOL_M:
                    add(node((q.x, q.y)), node(e[1]), 0.01, {"id": "", "line": None, "boat": False})
    # ends that meet within the tolerance
    allnodes = list(nodes.items())
    pts = np.array([k for k, _ in allnodes])
    for i, (k, n) in enumerate(allnodes):
        d = np.hypot(pts[:, 0] - k[0], pts[:, 1] - k[1])
        for j in np.nonzero((d <= JOINT_TOL_M) & (d > 0))[0]:
            add(n, allnodes[j][1], float(d[j]), {"id": "", "line": None, "boat": False})
    # bridges: deck between the two ends, joined to what meets each end
    for bid, (bp, g) in bridges.items():
        e1, e2 = snap.land_end(np.asarray(g.coords[0])), snap.land_end(np.asarray(g.coords[-1]))
        deck = LineString([e1, e2])
        a, b = node(e1), node(e2)
        add(a, b, deck.length, {"id": bid, "line": deck, "boat": False})
        for e, n in ((e1, a), (e2, b)):
            for k, m in list(nodes.items()):
                if m != n and math.hypot(k[0] - e[0], k[1] - e[1]) <= 1.0:
                    add(n, m, 0.01, {"id": "", "line": None, "boat": False})
    # halls and gates: walked through by their doors, at a cost
    centres = {}
    for b in boxes:
        c = node(b.c)
        centres[b.id] = c
        for side, d in b.doors().items():
            k = key(d)
            if k in nodes:
                add(c, nodes[k], float(np.hypot(*(d - b.c))) * 2.5, {"id": f"via:{b.id}", "line": LineString([d, b.c]), "boat": False})
        if b.walk_through:
            for k, m in list(nodes.items()):
                if m != c and b.poly.buffer(1.0).contains(Point(k)):
                    add(c, m, math.hypot(k[0] - b.c[0], k[1] - b.c[1]), {"id": f"via:{b.id}", "line": LineString([k, b.c]), "boat": False})
    for k, L in landings.items():
        n = node(L["xz"])
        centres[k] = n

    def where(ident):
        ident = ident.strip()
        if ident in landings:
            return centres[ident]
        if ident in by_row and by_row[ident]:
            return centres[by_row[ident][0].id]
        if ident in snap.gate_box:
            return centres[snap.gate_box[ident].id]
        if ident in gates:
            return node(gates[ident][1])
        if ident.startswith("BR") and ident in bridges:
            return node(snap.land_end(np.asarray(bridges[ident][1].coords[0])))
        hit = next((p for p in paths if p["id"] == ident), None)
        if hit:
            return node(hit["_line"].coords[0])
        raise SystemExit(f"routes.csv: waypoint {ident} is not a row with a box, a gate, a bridge, a landing or a line")

    inv = {v: k for k, v in nodes.items()}

    def search(s, t, boat):
        dist = {s: 0.0}
        prev = {}
        h = [(0.0, s)]
        while h:
            d, u = heapq.heappop(h)
            if u == t:
                break
            if d > dist.get(u, 1e18):
                continue
            for v, w, info in edges[u]:
                if info["boat"] != boat and info["line"] is not None and not info["id"].startswith("via:"):
                    continue
                if boat and info["id"].startswith("via:"):
                    continue
                nd = d + w
                if nd < dist.get(v, 1e18):
                    dist[v] = nd
                    prev[v] = (u, info)
                    heapq.heappush(h, (nd, v))
        return dist, prev

    added = []
    out = []
    for r in defs:
        boat = r["mode"] == "boat"
        wps = [w for w in r["waypoints"].split(";") if w.strip()]
        seq_lines, ids, total = [], [], 0.0
        for a, b in zip(wps, wps[1:]):
            s, t = where(a), where(b)
            dist, prev = search(s, t, boat)
            if t not in dist and not boat:
                # the network falls apart between two waypoints: one C line joins the two pieces where they come nearest
                back, _ = search(t, None, boat)
                A = np.array([inv[n] for n in dist])
                B = np.array([inv[n] for n in back])
                dd = np.hypot(A[:, None, 0] - B[None, :, 0], A[:, None, 1] - B[None, :, 1])
                i, j = np.unravel_index(np.argmin(dd), dd.shape)
                line = router.route(A[i], B[j], router.land_obstacle(), max_m=max(60.0, dd[i, j] * 2.5)) or LineString([A[i], B[j]])
                n_link = sum(1 for p in added if p["id"].startswith(f"RL-{r['id']}-")) + 1
                pid = f"RL-{r['id']}-{n_link:02d}"
                link = {
                    "id": pid, "kind": "courtyard_path", "name_zh": "", "scene": "", "width_m": 1.5, "width_source": "typology, C", "surface": SURFACE["courtyard_path"],
                    "from_id": a, "to_id": b, "from_at": "path", "to_at": "path", "gap_before_m": [0.0, 0.0], "sources": "S01", "confidence": "C", "pos_confidence": "C",
                    "assumed": True, "basis": "reach", "leaf": "", "in_box": "", "drawn": "nothing: route link",
                    "rerouted_m": 0.0, "blocked_before_m": 0.0, "blocked_m": round(router.blocked_line(line, router.land_obstacle()), 1),
                    "note": f"Added only so that route {r['id']} can go on from {a} to {b}: the traced ways do not join here. No source draws it.", "_line": line,
                }
                added.append(link)
                add(node(line.coords[0]), node(line.coords[-1]), line.length * 1.35, {"id": pid, "line": line, "boat": False})
                for e, k in ((A[i], line.coords[0]), (B[j], line.coords[-1])):
                    if key(e) != key(k):
                        add(node(e), node(k), float(np.hypot(e[0] - k[0], e[1] - k[1])), {"id": "", "line": None, "boat": False})
                inv.update({v: k for k, v in nodes.items()})
                dist, prev = search(s, t, boat)
            if t not in dist:
                raise SystemExit(f"routes.csv {r['id']}: no way from {a} to {b} through the network")
            chain = []
            u = t
            while u != s:
                pu, info = prev[u]
                chain.append((pu, u, info))
                u = pu
            chain.reverse()
            for pu, u, info in chain:
                if info["id"] and (not ids or ids[-1] != info["id"]):
                    ids.append(info["id"])
                a_, b_ = np.asarray(inv[pu]), np.asarray(inv[u])
                if info["line"] is not None:
                    c = np.asarray(info["line"].coords)
                    if np.hypot(*(c[0] - a_)) > np.hypot(*(c[-1] - a_)):
                        c = c[::-1]
                    seq_lines.extend(map(tuple, c))
                else:
                    seq_lines.extend([tuple(a_), tuple(b_)])
        clean = [seq_lines[0]]
        for p in seq_lines[1:]:
            if math.hypot(p[0] - clean[-1][0], p[1] - clean[-1][1]) > 0.05:
                clean.append(p)
        line = LineString(clean)
        stops = []
        for sid in [x for x in r["stops"].split(";") if x.strip()]:
            if sid in landings:
                sp, nm = landings[sid]["xz"], landings[sid]["t"]["name_zh"] or sid
            elif sid in by_row and by_row[sid]:
                sp, nm = by_row[sid][0].c, ROWS.get(sid, {}).get("name_zh") or by_row[sid][0].p.get("name") or sid
            elif sid.startswith("BR") and sid in bridges:
                sp, nm = np.asarray(bridges[sid][1].centroid.coords[0]), bridges[sid][0].get("name_zh") or sid
            else:
                raise SystemExit(f"routes.csv {r['id']}: stop {sid} unknown")
            along = line.project(Point(sp))
            stops.append({"id": sid, "name": nm, "along_m": round(along, 1), "off_m": round(line.distance(Point(sp)), 1)})
        stops.sort(key=lambda s: s["along_m"])
        props = {"id": r["id"], "name_en": r["name_en"], "name_zh": r["name_zh"], "mode": r["mode"], "path_ids": [i for i in ids if not i.startswith("via:")], "via": [i[4:] for i in ids if i.startswith("via:")],
                 "stops": stops, "length_m": round(line.length, 1), "sources": r["sources"], "confidence": r["confidence"], "note": r["note"]}
        out.append({"type": "Feature", "properties": props, "geometry": {"type": "LineString", "coordinates": ll_coords(line)}})
    return out, added


if __name__ == "__main__":
    main()
