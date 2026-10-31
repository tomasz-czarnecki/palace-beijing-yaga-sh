"""Every building as a box on a platform with a simple roof: site/reconstruction/data/halls_1860.geojson, and the walls and bridges as solids: generated/structures.json.

  uv run python scripts/boxes1860.py        (after ground1860.py)

One feature per box. Position, frontage and depth come from research/layers/footprints_1860 (S01 through the transform), with buildings.csv; heights and roofs from research/typology/params.json by hall class. Prints its checks: counts, overlaps between boxes, boxes standing in water, walls through boxes.

basis, on each feature:
  plan     a block drawn on S01; frontage and depth = drawn px / hall scale, reduced to the drawn size where neighbours or water need it (`fit`); heights by class
  stated   a size stated in a source (params.json by_name)
  xiyang   Xiyang Lou massing from params.json xiyang_lou: every part assumed, C
  layout   a compound with no single hall: boxes laid out from the typology: assumed, C
  default  a row with a position and no block drawn: a small default box: assumed, C
  gate     a gate on the walls layer with no hall there: a small default box: assumed, C
"""

import csv
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, MultiLineString, Point, Polygon, shape
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scene1860 import DATUM_M, GENERATED, GROUND_M, ROOT, SITE_DATA, WATER_M, Grid, layer, params, to_lonlat, to_xz  # noqa: E402

# Roof by hall class. Grey rolled ridges are the rule, with named exceptions: S06, S08 (two album leaves viewed), S112; research/typology/halls.md section 5.
ROOF_BY_CLASS = {
    "grand_hall": ("hip_gable", True, False),  # (form, rolled ridge 卷棚, double eaves 重檐). 正大光明殿 is 卷棚歇山: S119, S08
    "main_hall": ("hip_gable", True, False),  # 澹怀堂 卷棚歇山: S112
    "gate_hall": ("hip_gable", True, False),  # 长春园宫门 卷棚歇山: S112
    "side_hall": ("gable", True, False),  # C: params.json
    "small_house": ("gable", True, False),  # S111, S101
    "gallery": ("gable", True, False),  # C
    "storeyed_hall": ("hip_gable", True, False),  # 藏密楼 歇山: S111
    "pavilion_square": ("pyramid", False, False),  # 攒尖: S114, S105
    "temple_hall": ("hip_gable", False, True),  # 安佑宫 重檐歇山: S122, S06
    "tower": ("hip_gable", True, True),  # 三重檐: params.json, C
}
ROLL_DEPTH_FACTOR = 1.5  # deeper than this x the class's largest depth: several parallel rolls 勾连搭 (2-4 rolls: S118; each roll one section deep: 观澜堂, S111)
ROLLS_MAX = 4
RISE_CLAMP = (0.55, 1.5)  # the class's rise (ridge - eave) scales with the depth of the roll, within these limits, so a shallow box isn't a spike. Typology, C
OVERLAP_TOL_M2 = 0.25
FIT_STEP = 0.1  # how fast t falls, from typology size (1) to the drawn size (0)
PUSH_MAX_M = 2.0  # a pair still overlapping at drawn size is moved apart by at most this each: well inside the plan's reading (±10-75 m, Q7)
WATER_TOL = 0.02  # share of a box over water that counts as "stands in water"
ABSORB_SHARE = 0.5  # a drawn block with over half of it inside another is one building drawn twice: it takes no box of its own
SINK_M = 0.2  # a box's foot goes this far below its lowest corner, so nothing floats
GATE_ON_WALL_M = 14  # within this of a wall line a gate point counts as a gate in that wall; read by eye, 10-20 px off the ink (README)
GATE_GAP_M = 6  # the opening in the wall at a gate with no hall. Guess, C
GATE_HALL_NEAR_M = 6  # a hall this near a gate point is the gate itself
GATE_BOX = (8.0, 4.0)  # frontage and depth of a default gate box, m. Guess, C
DEFAULT_BOX = {"gate": ("gate_hall", 8.0, 4.0), "tower": ("storeyed_hall", 12.0, 7.0), "library": ("small_house", 9.0, 6.5), "other": ("small_house", 9.0, 6.5)}  # middle of the class ranges or smaller; guess, C
# Rows of type "other" with a position and no block that are buildings by name. The rest are plots, water, hills, docks or yard labels (research/README.md "For Round 2"): no box.
DEFAULT_OTHER = {"YM01-05", "YM01-06", "YM15-02", "YM40-N01", "YM40-N02", "YM41-07", "YM41-09"}
LAYOUT_COMPOUNDS = {"YM64", "YM65", "YM66", "CC24", "QC60"}  # scene polygon, no hall drawn, no row inside. YM82 is a dock, CC19 a sluice, YM54 and YM55 lakes, XY14 water: no hall typology fits them
LAYOUT_SPACING_M = 8  # between the main hall and its side halls. Guess, C
WALL_CLIP_M = 0.6  # a wall stops this short of a hall standing in its line
RESAMPLE_M = 15
BRIDGE_WIDTH_M = 3.0  # params.json other.bridge: guess, C
BRIDGE_HUMP_M = 0.8  # deck above the bank at mid span. Guess, C (params.json: 1 m above water)

P = params()
CLASSES = P["classes"]
BY_NAME = P["by_name"]
WALL = P["other"]["garden_wall"]  # height 2.8 m (S116, B), thickness 0.8 m (guess, C)
GRID = Grid()
BY_NAME_ALIAS = {"文源阁阁": "文源阁", "大宫门门殿": "大宫门", "雷峰夕照": "雷峰夕照殿"}  # the hall's row in buildings.csv and its key in by_name
GLAZE = {"yellow": ("黄", "金黄"), "blue": ("蓝",), "green": ("孔雀", "绿"), "mixed": ("五色", "二色", "红色", "waves"), "slate": ("石板",), "glazed": ("琉璃", "glazed"), "grey": ("灰",)}

# Xiyang Lou: params.json xiyang_lou, all C. (name of part, building_id, frontage, depth, platform, eave, ridge, roof, extras). Frontage is across the facing direction.
EUROPEAN_DEFAULT = {"platform": 0.8, "eave": 7.0, "ridge": 9.5}  # rows of the strip with no massing in params.json: guess, C
XY_SOURCES = {"XY01": "S108;S06;S03", "XY02": "S02;S109;S01", "XY03": "S02;S109;S01", "XY04": "S109;S02;S01;S06", "XY05": "S02;S01", "XY06": "S06;S03;S01", "XY07": "S06", "XY08": "S109;S110;S03;S01", "XY09": "S109;S03;S01", "XY10": "S109;S06;S01", "XY11": "S01", "XY12": "S01", "XY13": "S01", "XY15": "S06;S01"}
ROW = {}


def bearing_vec(deg):
    """Compass bearing to a unit vector in UTM easting and northing. Grid convergence here, about -0.45 degrees, is ignored against ±10-75 m of reading."""
    t = math.radians(deg)
    return math.sin(t), math.cos(t)


class Box:
    __slots__ = ("id", "bid", "parent", "cx", "cz", "deg", "f", "d", "df", "dd", "t", "fixed", "cls", "basis", "conf", "src", "assumed", "name", "extra", "absorbed", "over_water", "shift", "garden")

    def __init__(self, id, bid, parent, cx, cz, deg, f, d, cls, basis, conf, src, assumed, name, garden, df=None, dd=None, fixed=False, **extra):
        self.id, self.bid, self.parent, self.cx, self.cz, self.deg, self.f, self.d, self.cls = id, bid, parent, cx, cz, deg, f, d, cls
        self.basis, self.conf, self.src, self.assumed, self.name, self.garden = basis, conf, src, assumed, name, garden
        self.df, self.dd = (df if df is not None else f), (dd if dd is not None else d)
        self.t, self.fixed, self.extra, self.absorbed, self.over_water, self.shift = 1.0, fixed, extra, [], False, 0.0

    def size(self, t=None):
        t = self.t if t is None else t
        return self.df + (self.f - self.df) * t, self.dd + (self.d - self.dd) * t

    def axes(self):
        fx, fn = bearing_vec(self.deg)
        # In (x, z), z south: front = (fx, -fn), right along the frontage = (fn, fx).
        return (fx, -fn), (fn, fx)

    def poly(self, t=None):
        f, d = self.size(t)
        (ax, az), (ux, uz) = self.axes()
        return Polygon([(self.cx + s * ux * f / 2 + q * ax * d / 2, self.cz + s * uz * f / 2 + q * az * d / 2) for s, q in ((-1, 1), (1, 1), (1, -1), (-1, -1))])


def rows():
    out = list(csv.DictReader(open(ROOT / "research/buildings.csv", encoding="utf-8", newline="")))
    ROW.update({r["id"]: r for r in out})
    return out


def label(r):
    return r["name_zh"] or r["name_on_plan"] or ""


def row_xz(bid):
    r = ROW[bid]
    return to_xz(float(r["lon"]), float(r["lat"]))


def offset(cx, cz, deg, along, across):
    """A point from (cx, cz): `along` towards the front of a building facing deg, `across` to its right looking at its front from outside... kept simple: along the frontage axis."""
    fx, fn = bearing_vec(deg)
    return cx + fx * along + fn * across, cz - fn * along + fx * across


def xy_box(num, bid, x, z, deg, f, d, platform, eave, ridge, roof="hip", tiles="glazed", part="", rolled=False, double=False, shape_=None, stand=0.0, parent=None, name=None, fixed=True, over_water=False):
    r = ROW.get(bid, {})
    top = bid.split("-")[0]
    return Box(f"{top}-M{num:02d}", bid, parent if parent is not None else (r.get("parent_id") or top if "-" in bid else ""), x, z, deg, f, d, "european", "xiyang", "C", XY_SOURCES.get(top, "S01"), True, name or label(r), "Xiyang Lou", fixed=fixed,
               platform=platform, eave=eave, ridge=ridge, roof=roof, tiles=tiles, part=part, rolled=rolled, double=double, shape=shape_, stand=stand, european=True, over_water=over_water)


def xiyang_lou():
    """The strip's massing. Numbers from params.json xiyang_lou unless the comment says otherwise; positions from buildings.csv. Every part: assumed, C."""
    out, n = [], [0]

    def add(bid, x, z, deg, f, d, *a, **k):
        n[0] += 1
        out.append(xy_box(n[0], bid, x, z, deg, f, d, *a, **k))

    # 谐奇趣 XY01: main 28 x 14 x 12, corridors, octagons d 8 x 11, pool at the south. Ridge = eave + 3, a guess.
    x, z = row_xz("XY01")
    add("XY01", x, z, 175.1, 28, 14, 1.0, 12, 15, part="main block, three levels")
    ox1, oz1 = row_xz("XY01-01")
    ox2, oz2 = row_xz("XY01-N01")
    for bid, ox, oz, side in (("XY01-01", ox1, oz1, -1), ("XY01-N01", ox2, oz2, 1)):
        add(bid, ox, oz, 175.1, 8, 8, 0.5, 8, 11, roof="pyramid", part="octagonal music pavilion, two storeys", shape_="octagon")
        # The curved corridor as one straight run from the main block's corner to the pavilion, 4 m wide, 6 m high.
        cx, cz = offset(x, z, 175.1, -5, -side * 12)
        ang = math.degrees(math.atan2(oz - cz, ox - cx))
        length = math.hypot(ox - cx, oz - cz) - 3
        add(bid, (cx + ox) / 2, (cz + oz) / 2, (ang + 90) % 360, max(length, 6), 4, 0.3, 5, 6, roof="hip", part="corridor (9 bays, curved; a straight run here)")
    px, pz = row_xz("XY01-02")
    add("XY01-02", px, pz, 174.8, 30, 18, 0.5, 0.5, 0.5, part="fountain pool", shape_="pool")
    # 蓄水楼 XY02: 10 x 8 x 9 + north wing, one storey.
    x, z = row_xz("XY02")
    add("XY02", x, z, 91.8, 10, 8, 0.5, 6.5, 9, part="reservoir house, two storeys")
    wx, wz = offset(x, z, 91.8, 0, -9)
    add("XY02", wx, wz, 91.8, 8, 6, 0.3, 3.5, 5, part="north wing, one storey (size a guess)")
    # 花园门 XY03: 8 x 3 x 6.
    x, z = row_xz("XY03")
    add("XY03", x, z, 174.8, 8, 3, 0.3, 4.5, 6, part="south gate of the maze")
    # 黄花阵 XY04: outer 73 x 99, walls 1.2 x 0.6; ring d 20, pavilion d 10. The maze's plan is not traced: outer wall and two rings stand for it.
    x, z = row_xz("XY04-01")
    deg = 174.6
    cx, cz = offset(x, z, deg, -5, 0)
    for inset in (0, 11, 22):
        w, h = 73 - 2 * inset, 99 - 2 * inset
        for (a, c, ff, dd, dg) in ((h / 2, 0, w, 0.6, deg), (-h / 2, 0, w, 0.6, deg), (0, -w / 2, h, 0.6, deg + 90), (0, w / 2, h, 0.6, deg + 90)):
            mx, mz = offset(cx, cz, deg, a, c)
            add("XY04", mx, mz, dg, ff, dd, 0.0, 1.2, 1.2, part="maze wall, 1.2 x 0.6 m (S109); the plan of the maze is not traced: outer wall and two rings stand for it", shape_="wall")
    add("XY04-01", x, z, deg, 20, 20, 0.0, 1.0, 1.0, part="round stair base", shape_="octagon")
    add("XY04-01", x, z, deg, 10, 10, 0.2, 3.5, 7, roof="pyramid", part="central pavilion, timber with a glazed roof (S109)", shape_="octagon", stand=1.0)
    x, z = row_xz("XY04-N01")
    add("XY04-N01", x, z, 174.6, 18, 10, 0.5, 6.5, 9, part="north building, two storeys")
    # 养雀笼 XY05: 20 x 10 x 8, gateway.
    x, z = row_xz("XY05")
    add("XY05", x, z, 272.0, 20, 10, 0.5, 6, 8, part="gate-like block")
    # 方外观 XY06: 13 x 11 x 11 on the terrace of the ruin polygon 44 x 24 (terrace height a guess).
    x, z = row_xz("XY06")
    add("XY06", x, z, 174.4, 44, 24.2, 0, 1.0, 1.0, part="terrace and stairs (OSM ruin polygon, S03)", shape_="terrace")
    add("XY06", x, z, 174.4, 13, 11, 0.2, 8, 11, tiles="blue", part="two storeys, 3 bays, double eaves, blue glaze (S06)", double=True, stand=1.0)
    # 五竹亭 XY07: five pavilions 6 x 6 x 5 with galleries. Not drawn on S01 (Q15); a row is a guess.
    x, z = row_xz("XY07")
    for k in range(-2, 3):
        mx, mz = offset(x, z, 174.1, 0, k * 11)
        add("XY07", mx, mz, 174.1, 6, 6, 0.3, 3.5, 5, roof="pyramid", part="pavilion (Q15: not drawn on the plan; five in a row is a guess)")
        if k < 2:
            gx, gz = offset(x, z, 174.1, 0, (k + 0.5) * 11)
            add("XY07", gx, gz, 174.1, 5, 2.4, 0.2, 2.6, 3.2, roof="gable", part="gallery")
    # 海晏堂 XY08: west block 19 x 44 x 13 facing west, tank block 27 x 10 x 9, east block in rows; pool on the west.
    x, z = row_xz("XY08")
    add("XY08", x, z, 262.6, 44, 19, 1.0, 10, 13, part="west block, two storeys, 11 bays on the west front (S109)")
    x, z = row_xz("XY08-01")
    add("XY08-01", x, z, 174.0, 27.36, 10, 0.5, 7, 9, part="锡海 tank block; tank 27.36 x 5.72 x 1.44 m (S109, B), block C")
    x, z = row_xz("XY08-02")
    add("XY08-02", x, z, 264.2, 27.5, 17.5, 0.5, 0.5, 0.5, part="pool of the twelve hours", shape_="pool")
    # 远瀛观 XY09: 21 x 18 x 15 on a base of 2 m; the ruin polygon 59 x 51 taken as its terrace.
    x, z = row_xz("XY09")
    add("XY09", x, z, 174.7, 59.2, 51.0, 0, 2.0, 2.0, part="terrace (OSM ruin polygon, S03)", shape_="terrace")
    add("XY09", x, z, 174.7, 21, 18, 0.2, 12, 15, part="three-storey centre, double-eave hip roof (S109)", double=True, stand=2.0)
    # 大水法 XY10: pool 29 x 19, niche wall 20 x 3 x 9 to the north, two 13-tier towers (height a guess).
    x, z = row_xz("XY10")
    add("XY10", x, z, 173.9, 29, 19, 0.5, 0.5, 0.5, part="pool", shape_="pool")
    nx_, nz_ = offset(x, z, 173.9, -11, 0)
    add("XY10", nx_, nz_, 173.9, 20, 3, 0.5, 9, 9, part="niche wall", shape_="wall", tiles="stone")
    for bid in ("XY10-N01", "XY10-N02"):
        x, z = row_xz(bid)
        add(bid, x, z, 173.9, 5.3, 6, 0.3, 1.0, 9, roof="pyramid", part="13-tier fountain tower in its pool (S109, S06)", tiles="stone", over_water=True)
    # 观水法 XY11: platform 12 x 6 x 1 + screen 15 x 1 x 5, facing north to the fountain.
    x, z = row_xz("XY11")
    add("XY11", x, z, 353.5, 12, 6, 0, 1.0, 1.0, part="throne platform", shape_="terrace")
    sx_, sz_ = offset(x, z, 353.5, -4, 0)
    add("XY11", sx_, sz_, 353.5, 15, 1, 0, 5, 5, part="screen", shape_="wall", tiles="stone")
    # 线法山 XY12: the mound is in the ground (ground1860.py); pavilion on top, gate below.
    x, z = row_xz("XY12-02")
    add("XY12-02", x, z, 173.5, 7.5, 7.5, 0.3, 3.5, 6.6, roof="pyramid", part="small octagon on top", shape_="octagon")
    x, z = row_xz("XY12-01")
    add("XY12-01", x, z, 83.5, 10, 2, 0.2, 6, 6, part="triple gate like a triumphal arch; size a guess", shape_="wall", tiles="stone")
    # 螺蛳牌楼 XY13: 8 x 1.5 x 7.
    x, z = row_xz("XY13")
    add("XY13", x, z, 85.9, 8, 1.5, 0.2, 6, 7, roof="gable", part="arch")
    # 线法墙 XY15: paired screens 6 x 1 x 5. S01 draws 6 per side (Q16); the plan's stagger read by eye.
    x, z = row_xz("XY15")
    for k in range(6):
        along = -24 + k * 9.6
        off = 25 - k * 3.6
        for side in (-1, 1):
            mx, mz = offset(x, z, 85.0, along, side * off)
            add("XY15", mx, mz, 85.0 - side * 18, 6, 1, 0.0, 5, 5, part="screen for perspective paintings (S06); six per side as on S01 (Q16)", shape_="wall", tiles="stone")
    return out


XY_REPLACED = {"XY01", "XY01-01", "XY01-N01", "XY01-02", "XY02", "XY03", "XY04-01", "XY04-N01", "XY05", "XY06", "XY07", "XY08", "XY08-01", "XY08-02", "XY09", "XY10", "XY10-N01", "XY10-N02", "XY11", "XY12-01", "XY12-02", "XY13", "XY15"}


def footprint_boxes():
    out = []
    for f in layer("footprints_1860"):
        p = f["properties"]
        bid = p["building_id"]
        if bid in XY_REPLACED:
            continue
        r = ROW[bid]
        ring = shapely.transform(shape(f["geometry"]), lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1])))
        c = ring.centroid
        b = Box(p["id"], bid, p["parent_id"], c.x, c.y, p["orientation_deg"], p["frontage_m"], p["depth_m"], p["hall_class"], "plan", p["confidence"], p["sources"], False, label(r), r["garden"], fixed=p["note"].startswith(("stated", "typology")))
        (ax, az), (ux, uz) = b.axes()
        coords = np.array(ring.exterior.coords)
        along = (coords[:, 0] - c.x) * ux + (coords[:, 1] - c.y) * uz
        across = (coords[:, 0] - c.x) * ax + (coords[:, 1] - c.y) * az
        df, dd = np.ptp(along), np.ptp(across)
        b.df, b.dd = min(df, b.f), min(dd, b.d)
        if p["note"].startswith("stated"):
            b.basis = "stated"
        elif r["garden"] == "Xiyang Lou":
            b.extra.update(platform=EUROPEAN_DEFAULT["platform"], eave=EUROPEAN_DEFAULT["eave"], ridge=EUROPEAN_DEFAULT["ridge"], roof="hip", tiles="glazed", european=True, part="a block drawn on the plan in the Xiyang Lou strip; heights a guess")
            b.basis, b.assumed, b.conf = "xiyang", True, "C"
        out.append(b)
    return out


def default_boxes(existing, rows_all):
    """Rows with a position and no block: a small default box, unless a box already stands there."""
    out = []
    polys = [b.poly() for b in existing]
    tree = shapely.STRtree(polys)
    k = 0
    attached = {}
    for r in rows_all:
        if r["footprint_id"] or not r["lat"] or not (r["parent_id"] or r["id"].startswith("Z-")) or r["id"] in XY_REPLACED:
            continue
        if not (r["type"] in ("gate", "tower", "library") or r["id"] in DEFAULT_OTHER):
            continue
        cls, f, d = DEFAULT_BOX[r["type"] if r["type"] in DEFAULT_BOX else "other"]
        x, z = to_xz(float(r["lon"]), float(r["lat"]))
        deg = float(r["orientation_deg"]) if r["orientation_deg"] else 175.0
        k += 1
        b = Box(f"D{k:03d}", r["id"], r["parent_id"], x, z, deg, f, d, cls, "default", "C", r["sources"], True, label(r), r["garden"])
        hit = [i for i in tree.query(b.poly()) if polys[i].intersection(b.poly()).area > 0.5 * b.poly().area]
        if hit:
            attached[r["id"]] = existing[int(hit[0])].id
            continue
        out.append(b)
    return out, attached


def layout_boxes(land_water):
    """A compound with no single hall: a main hall on the scene polygon's land, two side halls, all from the class table."""
    out, skipped, k = [], [], 0
    scenes = {f["properties"]["id"]: f for f in layer("scenes_1860")}
    for cid in sorted(LAYOUT_COMPOUNDS):
        r = ROW[cid]
        poly = shapely.transform(shape(scenes[cid]["geometry"]), lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1]))).buffer(0)
        land = poly.difference(land_water)
        if land.is_empty:
            skipped.append(cid)
            continue
        c = land.representative_point()
        deg = 175.0
        main, side = CLASSES["main_hall"], CLASSES["side_hall"]
        mf, md = sum(main["frontage_range_m"]) / 2, sum(main["depth_m"]) / 2
        sf, sd = sum(side["frontage_range_m"]) / 2, sum(side["depth_m"]) / 2
        name = label(r)
        parts = [(0, 0, deg, mf, md, "main_hall", "main hall")]
        for s in (-1, 1):
            parts.append((md / 2 + LAYOUT_SPACING_M, s * (mf / 2 - sd / 2), (deg + (90 if s > 0 else -90)) % 360, sf, sd, "side_hall", "side hall"))
        for along, across, dg, ff, dd, cls, what in parts:
            x, z = offset(c.x, c.y, deg, along, across)
            k += 1
            b = Box(f"L{k:03d}", cid, cid, x, z, dg, ff, dd, cls, "layout", "C", "S01;" + r["sources"], True, name, r["garden"], part=f"{what}: laid out from the typology, no hall drawn here")
            if b.poly().difference(poly).area > 0.3 * b.poly().area or b.poly().intersection(land_water).area > 0.2 * b.poly().area:
                skipped.append(f"{cid} {what}")
                continue
            out.append(b)
    return out, skipped


def gate_boxes(existing, walls_union):
    """A gate on the walls layer with no hall at its point gets a small default box. Its page is G##."""
    out, gaps, on_wall = [], [], 0
    polys = [b.poly() for b in existing]
    tree = shapely.STRtree(polys)
    for f in layer("walls_1860"):
        if f["geometry"]["type"] != "Point":
            continue
        p = f["properties"]
        x, z = to_xz(*f["geometry"]["coordinates"])
        pt = Point(x, z)
        near = tree.query(pt, predicate="dwithin", distance=GATE_HALL_NEAR_M)
        d = walls_union.distance(pt)
        snap = walls_union.interpolate(walls_union.project(pt)) if d <= GATE_ON_WALL_M else None
        on_wall += d <= GATE_ON_WALL_M
        if len(near):
            continue
        at = snap or pt
        deg = 175.0
        if snap is not None:
            # Across the wall: the gate faces along the normal of the nearest wall piece.
            s = walls_union.project(pt)
            a, b = walls_union.interpolate(max(s - 3, 0)), walls_union.interpolate(s + 3)
            deg = (math.degrees(math.atan2(b.x - a.x, -(b.y - a.y))) + 90) % 360
            gaps.append(at)
        out.append(Box(f"GB{p['id'][1:]}", p["id"], "", at.x, at.y, deg, GATE_BOX[0], GATE_BOX[1], "gate_hall", "gate", "C", p["sources"], True, p.get("name_zh", ""), "", part="gate on the walls layer, no hall drawn at this point: a small default box"))
    return out, gaps, on_wall


def sat_push(a, b):
    """Smallest move that separates two rectangles along one of their axes: (dx, dz, depth) with b moving by +, or None."""
    pa, pb = np.array(a.poly().exterior.coords)[:4], np.array(b.poly().exterior.coords)[:4]
    best = None
    (fa, fb), (ua, ub) = a.axes(), b.axes()
    for ax in (fa, ua, fb, ub):
        ax = np.array(ax)
        ia, ib = pa @ ax, pb @ ax
        overlap = min(ia.max(), ib.max()) - max(ia.min(), ib.min())
        if overlap <= 0:
            return None
        sign = 1 if ib.mean() >= ia.mean() else -1
        if best is None or overlap < best[2]:
            best = (ax[0] * sign, ax[1] * sign, overlap)
    return best


def fit_boxes(boxes, water):
    """Typology size (t = 1) comes down towards the drawn size (t = 0) for boxes that overlap a neighbour or stand in water. Stated sizes and the massing don't move."""
    log = {}
    # One building drawn twice: its smaller block joins the larger.
    idx = shapely.STRtree([b.poly(0) for b in boxes])
    absorbed = set()
    for i, b in enumerate(boxes):
        for j in idx.query(b.poly(0)):
            j = int(j)
            if j <= i or i in absorbed or j in absorbed:
                continue
            c = boxes[j]
            if b.extra.get("shape") or c.extra.get("shape"):
                continue
            pa, pb = b.poly(0), c.poly(0)
            if pa.intersection(pb).area > ABSORB_SHARE * min(pa.area, pb.area):
                keep, drop = (i, j) if (pa.area, -i) >= (pb.area, -j) else (j, i)
                if boxes[drop].bid != boxes[keep].bid:
                    boxes[keep].absorbed.append(boxes[drop].bid)
                absorbed.add(drop)
    dropped = [boxes[i] for i in sorted(absorbed)]
    boxes = [b for i, b in enumerate(boxes) if i not in absorbed]
    log["absorbed"] = [(d.bid, d.id) for d in dropped]

    solid = [b for b in boxes if b.extra.get("shape") not in ("terrace", "wall", "pool") and not b.extra.get("over_water")]
    tree = shapely.STRtree([b.poly(1) for b in solid])
    pairs = sorted({(min(i, int(j)), max(i, int(j))) for i, b in enumerate(solid) for j in tree.query(b.poly(1)) if int(j) != i})
    for _ in range(11):
        changed = False
        for i, j in pairs:
            a, b = solid[i], solid[j]
            if a.poly().intersection(b.poly()).area > OVERLAP_TOL_M2:
                for q in (a, b):
                    if not q.fixed and q.t > 0:
                        q.t = max(0.0, q.t - FIT_STEP)
                        changed = True
        if not changed:
            break
    for _ in range(4):
        moved = False
        for i, j in pairs:
            a, b = solid[i], solid[j]
            if a.poly().intersection(b.poly()).area <= OVERLAP_TOL_M2:
                continue
            push = sat_push(a, b)
            if not push or push[2] > 2 * PUSH_MAX_M:
                continue
            dx, dz, depth = push
            movers = [q for q in (a, b) if not q.fixed]
            if not movers:
                continue
            share = (depth + 0.05) / len(movers)
            for q in movers:
                s = 1 if q is b else -1
                q.cx += s * dx * share
                q.cz += s * dz * share
                q.shift += share
            moved = True
        if not moved:
            break

    # Water: come down to the drawn size first, then step back onto land.
    prepared = water
    shapely.prepare(prepared)
    for b in solid:
        share = b.poly().intersection(prepared).area / b.poly().area
        while share > WATER_TOL and b.t > 0 and not b.fixed:
            b.t = max(0.0, b.t - FIT_STEP)
            share = b.poly().intersection(prepared).area / b.poly().area
        if share > WATER_TOL and not b.fixed:
            best = (share, 0, 0)
            for r in (1.5, 3.0, 4.5):
                for k in range(8):
                    dx, dz = r * math.cos(k * math.pi / 4), r * math.sin(k * math.pi / 4)
                    cx0, cz0 = b.cx, b.cz
                    b.cx, b.cz = cx0 + dx, cz0 + dz
                    s = b.poly().intersection(prepared).area / b.poly().area
                    b.cx, b.cz = cx0, cz0
                    if s < best[0] - 0.01:
                        best = (s, dx, dz)
            b.cx += best[1]
            b.cz += best[2]
            b.shift += math.hypot(best[1], best[2])
            share = best[0]
        b.over_water = share > WATER_TOL
    return boxes, log


def roof_of(b, r):
    cls = b.cls
    form, rolled, double = ROOF_BY_CLASS.get(cls, ("hip_gable", True, False))
    tiles = "grey"
    text = (r.get("roof") or "") if r else ""
    if "庑殿" in text:
        form = "hip"
    elif "歇山" in text:
        form = "hip_gable"
    elif "悬山" in text or "硬山" in text:
        form = "gable"
    elif "攒尖" in text:
        form = "pyramid"
    if text:
        rolled = "卷棚" in text
    if "重檐" in text:
        double = True
    t = (r.get("roof_tiles") or "") if r else ""
    for code, keys in GLAZE.items():
        if any(k in t for k in keys):
            tiles = code
            break
    name = label(r) if r else ""
    named = BY_NAME.get(BY_NAME_ALIAS.get(name, name), {})
    if "yellow" in named.get("tiles", ""):
        tiles = "yellow"
    elif "black" in named.get("tiles", ""):
        tiles = "black"
    if (b.parent or "") == "YM29" and cls not in ("small_house", "side_hall", "gallery"):
        tiles = "mixed"  # 方壶胜境: blue, yellow, green glazed halls, and a grey-roofed side court in the same leaf (S08, viewed)
    return form, rolled, double, tiles


def heights(b, r, f, d):
    """platform, eave, ridge, mid_eave, rolls from the class, or from a stated hall in by_name."""
    c = CLASSES.get(b.cls) or CLASSES["small_house"]
    name = label(r) if r else ""
    named = BY_NAME.get(BY_NAME_ALIAS.get(name, name), {})
    platform = named.get("platform_m", c["platform_m"])
    column = named.get("column_m")
    eave = c["eave_m"]
    if isinstance(column, (int, float)):
        eave = platform + column
    mid = c.get("mid_eave_m")
    storeys = int(r.get("storeys") or 0) if r else 0
    tiers = None
    if storeys >= 3 or (named.get("storeys") == 3):
        t = CLASSES["tower"]
        platform, ridge, tiers, mid = t["platform_m"], named.get("ridge_m", t["ridge_m"]), t["tiers_m"], None
        return platform, tiers[-1], ridge, None, 1, tiers
    if (storeys == 2 or named.get("storeys") == 2) and mid is None:
        t = CLASSES["storeyed_hall"]
        platform, eave, mid = t["platform_m"], t["eave_m"], t["mid_eave_m"]
        c = t
    lo, hi = c["depth_m"]
    rolls = 1
    if b.cls in ("main_hall", "grand_hall", "side_hall", "small_house", "gate_hall") and d > ROLL_DEPTH_FACTOR * hi:
        rolls = min(ROLLS_MAX, max(2, round(d / ((lo + hi) / 2))))
    if "rolls" in named:
        rolls = named["rolls"]
    rise = (c["ridge_m"] - c["eave_m"]) * min(max((d / rolls) / ((lo + hi) / 2), RISE_CLAMP[0]), RISE_CLAMP[1])
    if b.cls == "pavilion_square":
        rise = (c["ridge_m"] - c["eave_m"]) * min(max(min(f, d) / ((lo + hi) / 2), RISE_CLAMP[0]), RISE_CLAMP[1])
    ridge = named.get("ridge_m", eave + rise)
    if b.cls == "temple_hall" and "ridge_m" not in named:
        ridge = c.get("ridge_double_eave_m", ridge)
    return platform, eave, ridge, mid, rolls, tiers


def feature(b):
    r = ROW.get(b.bid)
    f, d = b.size()
    corners = list(b.poly().exterior.coords)[:4]
    grounds = [GRID.at(x, z) for x, z in corners]
    g = GRID.at(b.cx, b.cz)
    e = b.extra
    if "eave" in e:
        platform, eave, ridge, mid, rolls, tiers = e["platform"], e["eave"], e["ridge"], None, 1, None
        form, rolled, double, tiles = e.get("roof", "hip"), e.get("rolled", False), e.get("double", False), e.get("tiles", "glazed")
    else:
        platform, eave, ridge, mid, rolls, tiers = heights(b, r, f, d)
        form, rolled, double, tiles = roof_of(b, r)
    over = b.over_water or e.get("over_water", False)
    foot = (0.0 - SINK_M) if over else min(grounds + [g]) - SINK_M
    lon, lat = to_lonlat(np.array([c[0] for c in corners]), np.array([c[1] for c in corners]))
    ring = [[round(float(a), 7), round(float(q), 7)] for a, q in zip(lon, lat)]
    ring.append(ring[0])
    props = {
        "id": b.id, "building_id": b.bid, "parent_id": b.parent or "", "name": b.name, "garden": b.garden,
        "hall_class": b.cls, "frontage_m": round(f, 2), "depth_m": round(d, 2),
        "platform_m": round(platform, 2), "eave_m": round(eave, 2), "ridge_m": round(ridge, 2),
        "roof": form, "rolled": rolled, "double": double, "tiles": tiles, "orientation_deg": round(b.deg % 360, 1),
        "sources": b.src, "confidence": b.conf, "assumed": b.assumed, "basis": b.basis,
        "ground_m": round(g + DATUM_M, 2), "foot_m": round(foot + DATUM_M, 2),
    }
    if rolls > 1:
        props["rolls"] = rolls
    if mid:
        props["mid_eave_m"] = round(mid, 2)
    if tiers:
        props["tiers_m"] = tiers
    if b.t < 1:
        props["fit"] = round(b.t, 1)
    if b.shift > 0:
        props["moved_m"] = round(b.shift, 1)
    if over:
        props["over_water"] = True
    if b.absorbed:
        props["also"] = b.absorbed
    for k in ("shape", "european", "part", "stand"):
        if e.get(k):
            props[k] = e[k]
    return {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring]}, "properties": props}


def wall_segments(wall_lines, boxes, gaps):
    """Wall lines minus what stands in them, resampled so the top follows the ground."""
    cut = unary_union([b.poly().buffer(WALL_CLIP_M) for b in boxes if b.extra.get("shape") not in ("wall",)] + [g.buffer(GATE_GAP_M / 2) for g in gaps])
    segs = []
    kept = 0.0
    cut_len = 0.0
    for line in wall_lines:
        rest = line.difference(cut)
        cut_len += line.length - rest.length
        pieces = rest.geoms if isinstance(rest, MultiLineString) else [rest]
        for piece in pieces:
            if piece.is_empty:
                continue
            kept += piece.length
            n = max(1, int(piece.length / RESAMPLE_M))
            pts = [piece.interpolate(i / n, normalized=True) for i in range(n + 1)]
            # Keep the corners: resample each straight run.
            coords = list(piece.coords)
            pts = []
            for (ax, az), (bx, bz) in zip(coords, coords[1:]):
                m = max(1, int(math.hypot(bx - ax, bz - az) / RESAMPLE_M))
                pts += [(ax + (bx - ax) * i / m, az + (bz - az) * i / m) for i in range(m)]
            pts.append(coords[-1])
            for (ax, az), (bx, bz) in zip(pts, pts[1:]):
                ga, gb = GRID.at(ax, az), GRID.at(bx, bz)
                segs.append([round(ax, 2), round(az, 2), round(bx, 2), round(bz, 2), round(min(ga, gb) - 0.2 if GRID.at((ax + bx) / 2, (az + bz) / 2) > 0.5 else -0.2, 2), round(max(ga, gb) + WALL["height_m"], 2)])
    return segs, kept, cut_len


def bridges_3d():
    out = []
    for f in layer("bridges_1860"):
        p = f["properties"]
        line = shapely.transform(shape(f["geometry"]), lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1])))
        n = max(2, min(8, int(line.length / 6)))
        pts = []
        for i in range(n + 1):
            q = line.interpolate(i / n, normalized=True)
            hump = BRIDGE_HUMP_M * math.sin(math.pi * i / n)
            pts.append([round(q.x, 2), round(GRID.at(q.x, q.y) + hump + 0.1, 2), round(q.y, 2)])
        bid = p.get("building_id") or ""
        out.append({"id": p["id"], "building_id": bid, "name": p.get("name_zh", ""), "width_m": BRIDGE_WIDTH_M, "pts": pts})
    return out


def main():
    rows_all = rows()
    water = unary_union([shapely.transform(shape(f["geometry"]), lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1]))).buffer(0) for f in layer("water_1860")]).buffer(0)
    wall_lines = [shapely.transform(shape(f["geometry"]), lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1]))) for f in layer("walls_1860") if f["geometry"]["type"] == "LineString"]
    walls_union = unary_union(wall_lines)

    boxes = footprint_boxes() + xiyang_lou()
    defaults, attached = default_boxes(boxes, rows_all)
    boxes += defaults
    layouts, skipped = layout_boxes(water)
    boxes += layouts
    gates, gaps, gates_on_wall = gate_boxes(boxes, walls_union)
    boxes += gates
    boxes, log = fit_boxes(boxes, water)

    feats = [feature(b) for b in boxes]
    shared = dict(attached)  # rows whose box stands for them, for the pages
    by_id = {b.id: b for b in boxes}
    fc = {
        "type": "FeatureCollection",
        "name": "halls_1860",
        "credit": "Positions traced from S01, Yuanmingyuan plan, image courtesy of the Princeton University Art Museum. Heights and roofs: typology. Guesses are marked assumed, confidence C.",
        "shared_rows": {k: by_id[v].bid for k, v in shared.items() if v in by_id},
        "features": feats,
    }
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    (SITE_DATA / "halls_1860.geojson").write_text(json.dumps(fc, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

    segs, kept, cut_len = wall_segments(wall_lines, boxes, gaps)
    structures = {"wall": {"thickness_m": WALL["thickness_m"], "height_m": WALL["height_m"], "sources": WALL["sources"], "confidence": WALL["confidence"], "segments": segs}, "bridges": bridges_3d()}
    (GENERATED / "structures.json").write_text(json.dumps(structures, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

    # Checks, on what was written.
    polys = []
    for b in boxes:
        polys.append(b.poly())
    solid = [i for i, b in enumerate(boxes) if b.extra.get("shape") not in ("terrace", "wall", "pool") and not (b.extra.get("shape") == "octagon" and b.extra["ridge"] == b.extra["eave"])]  # a stair base carries what stands on it
    tree = shapely.STRtree([polys[i] for i in solid])
    overlaps, worst = [], 0
    for n, i in enumerate(solid):
        for m in tree.query(polys[i]):
            m = int(m)
            if m <= n:
                continue
            a = polys[i].intersection(polys[solid[m]]).area
            if a > OVERLAP_TOL_M2:
                overlaps.append((boxes[i].id, boxes[solid[m]].id, round(a, 1)))
    overlaps.sort(key=lambda o: -o[2])
    # What overlaps at the end is two blocks the plan itself draws touching or overlapping, more than PUSH_MAX_M apart: they're left as drawn. Also written down for checking.
    in_water = [(b.id, b.bid, b.name, round(polys[i].intersection(water).area / polys[i].area, 2)) for i, b in enumerate(boxes) if polys[i].intersection(water).area / polys[i].area > WATER_TOL and b.extra.get("shape") not in ("pool",)]
    centre_water = [x for x in in_water if x[3] > 0.5]
    over_flag = sum(f["properties"].get("over_water", False) for f in feats)
    floating = 0
    for f in feats:
        p = f["properties"]
        if not p.get("over_water") and p["foot_m"] > p["ground_m"]:
            floating += 1
    walls_through = sum(1 for i, b in enumerate(boxes) if polys[i].intersects(walls_union))
    n = len(feats)
    by_basis = {}
    by_conf = {}
    for f in feats:
        p = f["properties"]
        by_basis[p["basis"]] = by_basis.get(p["basis"], 0) + 1
        by_conf[p["confidence"]] = by_conf.get(p["confidence"], 0) + 1
    assumed = sum(f["properties"]["assumed"] for f in feats)
    rows_boxed = {f["properties"]["building_id"] for f in feats} | {a for f in feats for a in f["properties"].get("also", [])} | set(shared)
    print(f"{n} boxes: {n - assumed} on a source (a block drawn on S01 or a stated size), {assumed} assumed; by basis {dict(sorted(by_basis.items()))}; by confidence {dict(sorted(by_conf.items()))}")
    print(f"{sum(1 for b in boxes if b.t < 1)} reduced below the typology size, {sum(1 for b in boxes if b.t == 0)} to the drawn size; {sum(1 for b in boxes if b.shift > 0)} moved, largest {max(b.shift for b in boxes):.1f} m; {len(log['absorbed'])} blocks drawn twice absorbed: {log['absorbed']}")
    print(f"rows with a box: {len(rows_boxed)} of {len(rows_all)} (+ {sum(1 for f in feats if f['properties']['building_id'].startswith('G'))} gate boxes); rows sharing a box: {sorted(shared)}; layout skipped: {skipped}")
    print(f"overlaps left {len(overlaps)}, worst {overlaps[:6]}")
    print(f"boxes over water > {WATER_TOL:.0%}: {len(in_water)}, more than half over water {len(centre_water)}: {centre_water}; flagged over_water {over_flag}; floating {floating}")
    print(f"gates {gates_on_wall} on a wall line, {len(gates)} default gate boxes, {len(gaps)} gaps cut; wall kept {kept:.0f} m, cut {cut_len:.0f} m at halls and gates, {len(segs)} segments; boxes the wall lines cross, wall stopped at them: {walls_through}")
    print(f"halls_1860.geojson {(SITE_DATA / 'halls_1860.geojson').stat().st_size / 1e6:.2f} MB, structures.json {(GENERATED / 'structures.json').stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
