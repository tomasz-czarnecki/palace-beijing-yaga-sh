#!/usr/bin/env python3
"""文源阁 Wenyuan Ge (YM46), the library of the Four Treasuries in its walled rock garden: the eleventh detailed model (Round 25).

  uv run python models/YM46-wenyuan-ge/wenyuange.py      (after scripts/kit1860.py has run once)

The court as S01 draws it and the texts and the 2024 dig describe it, in its state before October 1860: the library of 1774 with six bays on each of two floors
(上下各六楹, S05 j81:35b), its bays and depths from the Guangxu 丈尺册 (S105 note [4]: 明间 5.12 m, four 次间 4.00 m, the stair bay 稍间 1.60 m at the west, 22.72 m;
galleries front and back 3.52 m and the middle 7.68 m, 14.72 m), the two storeys seen from outside with a skirt roof 腰檐 between them (the form of its sisters 文津阁
and 文渊阁, the 1776 poem's 此即肖文津, E2186), black glazed tile with green trim (the dig, S133; S105), a ridge in white and green waves (Malone's fragments, S02 p.90),
grey brick gable walls and dark green columns (S105); the terrace 月台 before it on the pool; the pool with the rock 玲峰 on its stone terrace (S05 j81:36b, Malone
pp.89-90, the dig's base); the stele pavilion east of the library with Qianlong's 文源阁记 (S05 j81:36b, Q110: its platform 4.48 m square); the rockeries round the
court and behind the south gate (S01; the 1776 poem's 詭石堆竒岫; the dig: culverts under the rockery behind the gate) with the pavilion 趣亭 on it (the dig names it,
S133); the court's wall of 虎皮石 rubble with the south gate and the north gate (S133, S942); a small pond in the north-east corner (S942).

Method (docs/METHOD.md, 'a compound from the kit and its evidence', Rounds 17-24): the hall kit (scripts/hall_parts.py) for the gate and the pavilions; the library by
`library()` below on the kit's parts (columns, openings, the roof), from the 丈尺册's figures; the layout re-read on S01 (plan_readings.csv, plan pixels, placed by
the fit in use, research/georef/). No picture of 文源阁 standing or of its ruin is known (Q122, Q125): its form is tested against the photographs of 文津阁, which it
copies (research/scenes/YM46-wenyuan-ge/plate_keypoints.csv).
Writes, beside this file: model.glb, params.json, keypoints.json, joints.json, summary.json, report.json (models/README.md).
Frame (scripts/model_site.py): origin at the front middle of the library's box F0276, at that box's ground; x east along the front, y up, z south (S01's walls run
north-south in it within 0.4 degrees).
Grades: what a source states for this object is `doc`; what is carried in from the classes or guessed (every height, the gate's and the pavilions' forms, the
north-east pond, the small squares) is `fill` (assumed, C).
"""

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from georef import plan_to_wgs84  # noqa: E402
from hall_parts import JU, HallKit, profile  # noqa: E402
from model_mesh import Mesh  # noqa: E402
from model_site import Site, lobed  # noqa: E402
from scene1860 import DATUM_M, to_xz  # noqa: E402
from shapely.geometry import LineString, Point, Polygon, box as sbox, shape  # noqa: E402
from shapely.ops import split, unary_union  # noqa: E402
from shapely.prepared import prep  # noqa: E402

# ------------------------------------------------------------ the figures (heights all C, in one place)
BAYS = [1.60, 4.00, 4.00, 5.12, 4.00, 4.00]   # west to east (S105 note [4], the Guangxu 丈尺册: B)
DEPTHS = [3.52, 7.68, 3.52]                   # front gallery, middle, back gallery (S105 note [4]: B)
Y_C = 0.10      # the court's floor above the library box's ground (Round 10's pad): the yard raised (S942), C
PL = 0.75       # the library's platform above the court, C
YT = 0.45       # the terrace 月台 above the court, C
# the storeys as measured on 文渊阁's south front (P0555) in 文源阁's bays (measure.py, measure.json): a twin's proportion, C
COL1 = 2.51     # the ground storey's columns above the floor, to the beam's underside (measured)
SK_TIP = 3.46   # the skirt roof 腰檐: its tip above the floor (its drip measured at 3.34 m, the drip tiles 0.12 m below the tip)
SK_TOP = 4.45   # where it meets the upper façade: the tiles' rise on P0555 about 1.0 m, C
SK_OUT = 1.50   # its reach beyond the column line, C
WIN2 = (5.08, 6.15)  # the upper windows' lower and upper frames (measured)
UP_TOP = 6.45   # the upper storey's column tops, C
EAVE2 = 6.87    # the upper beam's top, C
Y_TIP = 7.48    # the top eave's tip (its drip measured at 7.26 m, the drip 0.22 m below the tip)
O2 = 1.00       # the top eave's overhang, C
RISE = 0.58     # the roof's rise over its half depth (the 举架 of the storeyed hall class), C
LF_TERR = 0.60  # 玲峰's terrace above the water, C
LF_ROCK = 4.10  # 玲峰 above its terrace: Malone's '12 or 15 feet' (S02 p.90), B
WALL_H = 3.00   # the court wall above the court, C
BT_PL, BT_SIDE = 0.60, 4.48   # the stele pavilion: its platform's height (C) and side (S105 note [2], B)
QT_Y = 2.60     # 趣亭's floor on the rockery above the court, C

P = {
    "layout": ("the court's wall, the library, the terrace 月台, the pool and 玲峰's terrace, the stele pavilion, the rockeries, the two gates as S01 draws them", "S01", "B",
               "S01 re-read in Round 25 on 4x and 6x crops (plan_readings.csv): every line in plan pixels; S01 is B until Q2; its scale here about 0.20 m a pixel across and 0.22 down"),
    "bays": ("six bays: from the west the stair bay 1.60 m, 4.00, 4.00, the 明间 5.12, 4.00, 4.00 m; 22.72 m between the end columns", "S105;S05;S01", "B",
             "the Guangxu 丈尺册 (S105 note [4]): 明间面宽一丈六尺, 四次间各一丈二尺五寸, 西稍间五尺, 71 尺; after 1860, so B; S05 上下各六楹 (A); S01 draws five cells, the west one wide (the stair bay drawn with its neighbour), the 明间 third from the west and in line with both gates"),
    "depth": ("galleries front and back 3.52 m, the middle 7.68 m: 14.72 m between the front and back columns", "S105", "B", "the 丈尺册: 中进深二丈四尺, 前后廊上步各深一丈一尺, 46 尺 (S105 note [4]); S01's grid 13.1 m deep, its gallery lines drawn"),
    "storeys": ("two storeys seen from outside, three inside (明二暗三): the ground storey with its galleries, a skirt roof 腰檐 front and back, the upper storey over the whole depth", "S05;S105;S422", "B",
                "S05 上下各六楹 (A); S105: a lower floor with the study and the west stair, a mezzanine and a top floor of shelves (B); the sisters 文津阁 (P0551) and 文渊阁 (P0555) show the skirt roof and the upper storey over the galleries (twins, form only)"),
    "roof": ("a 硬山 roof, black glazed tile with green trim 剪边, the ridges green with white waves", "S133;S105;S02;E2186", "B",
             "the dig: black glazed tiles (S133, S942's photo: black and green); S105: 硬山, black with green edging; Malone: fragments of glazed tile with waves in white and green (S02 p.90); 硬山 kept against 金勋's memory and a late-Qing sheet of 歇山 (Q111): the 1776 poem says the library copies 文津阁 (此即肖文津, E2186) and 文津阁 and 天一阁 are 硬山; the waves' form C"),
    "colours": ("dark green columns, red door and window frames, green gallery lattice and rails, grey brick gable walls, white plaster under the upper windows, blue-green beams", "S105;S422", "B",
                "S105: grey brick walls and dark green columns (B); the red frames, the green lattice and rails and the plaster band after the sisters' photographs (P0551, P0555: twins, C)"),
    "heights": (f"platform {PL} m; above the floor: the ground storey's columns {COL1} m, the skirt roof's drip {SK_TIP - 0.12:.2f} m, the upper windows {WIN2[0]}-{WIN2[1]} m, the top eave's drip {Y_TIP - 0.22:.2f} m; the roof's rise {RISE} of its half depth", "S422;S105;S101", "C",
                "no figure for a height of 文源阁 has been seen (the dig's report is not out, the 丈尺册 as quoted gives none: Q287); measured on the sister 文渊阁's south front (P0555, twin T056) in 文源阁's bays by a camera fitted jointly with the heights (models/YM46-wenyuan-ge/measure.py: rms 5.0 px; its side bay against its 明间 0.78 on the picture, 文源阁's 0.78), a twin's proportion; the platform and the roof's rise the storeyed hall class and the Qing manual's 举架 (S101)"),
    "plaque": ("the plaque 文源閣 under the upper eave of the 明间", "S05", "A", "S05 j81:36a: 閣額 ... 御書 (A); the board's size and place C"),
    "yuetai": (f"the terrace 月台 before the library, {YT} m above the court, its south edge the pool's bank, flights at its ends", "S01;S05", "B",
               "S01's rectangle joined to the library's front (B); the 1776 poem 亦復有月臺 (S05 j81:37b, A); the dig's terrace (S133); its height and flights C"),
    "pool": ("the pool before the library: Round 10's water W0230 (348 m2), its banks of rock and its face up to the court", "S01;S02;S134", "B",
             "S01 draws the pool with rock banks (B); Malone: a pool before the library with water-worn rock round it (S02 pp.89-90); the dig: one pond south of the hall, tied by culverts to the river outside (S134, S942); the brief's 15 by 7 zhang is in no source we hold"),
    "lingfeng": (f"玲峰: a pierced standing rock {LF_ROCK} m high on an oval stone terrace {LF_TERR} m above the water in the pool, with Qianlong's poem cut on its face", "S05;S02;S134", "B",
                 "S05 j81:36b 閣前石為玲峯刋御製文源閣詩 (A); Malone: 'a huge monolith with inscriptions on it and pierced with many holes, rising 12 or 15 feet from a stone terrace in the middle of the pool' (S02 pp.89-90: 3.7-4.6 m, B); S105 'over 6 m' (Q288); the dig: its base of long slabs tied with iron dovetails (S134); the terrace S01's oval; the rock's form C"),
    "beiting": (f"the stele pavilion east of the library: a {BT_SIDE} m square platform, four columns, a pyramid roof; inside the stele of the 文源阁记", "S05;S105;S01;S02", "B",
                "S05 j81:36b 閣東亭内石碣刋御製文源閣記 (A); the platform 1丈4尺 square (S105 note [2], Q110); Malone saw the marble stele standing (S02 p.89); the pavilion's form and tile C"),
    "rockeries": ("rock banks inside the wall all round, masses in the corners, the large rockery between the pool and the south gate", "S01;S05;S133", "B",
                  "S01 draws them (B); the 1776 poem: strange stones heaped into peaks (詭石堆竒岫, S05 j81:37b, A); the dig: three culverts under the rockery behind the gate (S133); every rock's form and height C"),
    "quting": ("趣亭: a small square pavilion on the rockery's summit with a rock stair", "S133;S01", "C",
               "the dig names a 趣亭 (S133) and S942 two pavilions; S01 draws a small circle on the rockery's summit; the sister 文津阁's pavilion on its rockery (P0550) gives the form (twin: C)"),
    "gate_S": ("the south gate: three bays astride the wall, the middle one the door", "S01;S133", "B", "S01's three cells (B); the dig found the gate (S133); bays, heights and tile C"),
    "gate_N": ("the north gate: a door in the wall", "S01;S942", "B", "S01's small arch on the north wall; the dig: a door south and north (S942); its form C"),
    "wall": (f"the court's wall of 虎皮石 rubble, {WALL_H} m above the court, a tiled coping", "S01;S133", "B", "S01's lines (B); the dig: walls of 虎皮石 rubble, not city brick (S133); height and coping C"),
    "court": (f"the court's floor {Y_C} m above the library's ground, raised above the land outside, earth with the flagstone paths of Round 9", "S942;S134", "C",
              "the dig: the yard raised a little so storm water left by a wall drain, the ground inside higher than outside (S942, S134); paths of unworked flagstones (S942); its level C"),
    "pond_NE": ("a small pond among the rocks in the north-east corner", "S942;S133", "C", "the dig: two ponds, one south of the hall and one in the north-east corner (S942) or east of the library (S133); S01 does not draw it; its place and size C"),
    "squares": ("two small stone pedestals west and east of the south rockery", "S01", "C", "S01 draws two squares about 2.6 m; what they were is unknown: pedestals C"),
}
V = {k: v[0] for k, v in P.items()}

COL = {
    "lacquer": "#8c3a2b", "pillar": "#2c4636", "rail_green": "#3d6a55", "lacquer_dark": "#22362a", "wall": "#dcd6c9", "plaster": "#e4ddcf", "glass_lattice": "#2b3137", "sill": "#8d8a84",
    "band": "#2e6a6c", "bracket": "#3b7b70", "bandred": "#7d2c20", "platform": "#b7b0a1", "coping": "#d2ccbe", "step": "#d8d3c6", "marble": "#ebe7de",
    "underside": "#4b453d", "fascia": "#2c3a33", "wallred": "#9b3d2c", "brick": "#8e8d89", "brick_dark": "#77766f", "rubble": "#8a8172", "court": "#b5aa92",
    "pave": "#bdb6a6", "gold": "#c9a245", "plaque": "#20406a", "timber": "#7a5a3c", "stele": "#d9d5cb", "inscr": "#8c877b",
    "rock": "#918f86", "rock2": "#a19c90", "rock_ling": "#b3aea1", "rock_face": "#7b786f", "water": "#56747b",
    "tile_black": "#2a2c2e", "ridge_black": "#1e1f21", "tile_green": "#3f8f6a", "ridge_green": "#316f53", "wave_white": "#e9e7de",
    "tile_grey": "#5f6469", "ridge_grey": "#4a4e52", "tile_yellow": "#d6a31c", "ridge_yellow": "#a77f16",
}

S = Site("F0276")
m = Mesh(COL)
S.m = m
S.ROCKERIES = ["YM46"]
REPORT = {"halls": {}, "deck_joints": []}


def plan_scene(px, py):
    lon, lat = plan_to_wgs84(np.array([px], float), np.array([py], float))
    return to_xz(float(lon[0]), float(lat[0]))


ROWS = list(csv.DictReader(open(HERE / "plan_readings.csv", encoding="utf-8")))
PX = {r["name"]: [[tuple(map(float, p.split())) for p in part.split(";")] for part in r["plan_px"].split("|")] for r in ROWS}
READ = {k: [[S.to_local(*plan_scene(*p)) for p in part] for part in v] for k, v in PX.items()}


def pts(name, k=0):
    return [(float(x), float(z)) for x, z in READ[name][k]]


def rect(name):
    q = pts(name)
    xs, zs = [p[0] for p in q], [p[1] for p in q]
    return min(xs), max(xs), min(zs), max(zs)


def mid(name):
    x0, x1, z0, z1 = rect(name)
    return (x0 + x1) / 2, (z0 + z1) / 2


# ------------------------------------------------------------ the water: Round 10's level for the pool W0230, its outline from the layer
with open(ROOT / "research/terrain/water_levels.csv", encoding="utf-8") as fh:
    _lv = [r for r in csv.DictReader(fh) if "W0230" in r["water_ids"].split(";")]
WATER_Y = round(float(_lv[0]["level_m_egm2008"]) - DATUM_M - S.pos[1], 3)
_w = [f for f in json.load(open(ROOT / "research/layers/water_1860.geojson", encoding="utf-8"))["features"] if f["properties"].get("id") == "W0230"][0]
_g = shape(_w["geometry"])
_g = max(_g.geoms, key=lambda q: q.area) if _g.geom_type != "Polygon" else _g
POOL = Polygon([S.to_local(*to_xz(lo, la)) for lo, la in _g.exterior.coords[:-1]]).buffer(0)
REPORT.update({"water_y": WATER_Y, "water_m": float(_lv[0]["level_m_egm2008"]), "court_y": Y_C, "pool_m2": round(POOL.area, 1)})

# the ways of Round 9 in the frame: the rocks keep off them
WAYS = []
for f in json.load(open(ROOT / "research/layers/paths_1860.geojson", encoding="utf-8"))["features"]:
    gg = shape(f["geometry"])
    if gg.geom_type != "LineString":
        continue
    loc = [S.to_local(*to_xz(lo, la)) for lo, la in gg.coords]
    if min(abs(x) for x, z in loc) > 80 or min(abs(z - 10) for x, z in loc) > 80:
        continue
    WAYS.append(LineString(loc).buffer((f["properties"].get("width_m") or 1.5) / 2 + 0.5))
WAY_U = unary_union(WAYS) if WAYS else Polygon()

# ------------------------------------------------------------ decks: raised floors the model draws (the court, the terrace, the platforms)
DECKS = []  # [name, top, Polygon, prepared]


def add_deck(name, poly, top, register=True):
    pg = Polygon(poly).buffer(0)
    DECKS.append([name, top, pg, prep(pg)])
    if register:
        S.deck(name, top, [tuple(map(float, p)) for p in pg.exterior.coords[:-1]])
    return pg


def ground(x, z):
    g = S.gy(x, z)
    pt = Point(x, z)
    for _, top, pg, pp in DECKS:
        if pp.covers(pt):
            g = max(g, top)
    return g


def bed(x, z):
    return S.gy(x, z)


K = HallKit(m, ground)


def compass(dx, dz):
    return ("N" if dz < 0 else "S") + ("W" if dx < 0 else "E")


def _w(x, z, rot, a, b):
    c, s = math.cos(rot), math.sin(rot)
    return np.array([x + c * a + s * b, 0.0, z - s * a + c * b])


# ============================================================ helpers (from 方壶胜境's generator, Round 24)
def flight(name, x, z, rot, width, ytop, ybot, entry=True, cheeks=True, mat="step"):
    """A flight 踏跺 from (x, z) at ytop going out along rot (0: +z) down to ybot, steps of about 0.15 x 0.30 m, the side slabs 垂带. Returns the foot (x, y, z)."""
    n = max(1, round((ytop - ybot) / 0.15))
    rise = (ytop - ybot) / n
    run = n * 0.30
    m.push(x, 0, z, rot)
    w = width / 2
    low = min(bed(*m.world((a, 0, b))[::2]) for a in (-w, w) for b in (0.1, run)) - 0.15
    low = min(low, ybot - 0.15)
    for k in range(n):
        m.box(-w, w, low, ytop - (k + 1) * rise, k * 0.30, (k + 1) * 0.30, mat, skip=("bottom",))
    if cheeks:
        for l0, l1 in ((-w - 0.4, -w), (w, w + 0.4)):
            m.poly([(l0, ytop, 0), (l1, ytop, 0), (l1, ybot + 0.05, run), (l0, ybot + 0.05, run)], mat)
            for lat in (l0, l1):
                m.poly([(lat, ytop, 0), (lat, ybot + 0.05, run), (lat, low, run), (lat, low, 0)], mat)
            m.poly([(l0, ybot + 0.05, run), (l1, ybot + 0.05, run), (l1, low, run), (l0, low, run)], mat)
    foot = m.world((0, ybot, run + 0.2))
    top = m.world((0, ytop, -0.2))
    m.pop()
    S.FOOTPRINTS.append([(float(p[0]), float(p[2])) for p in [_w(x, z, rot, a, b) for a, b in ((-w - 0.4, 0), (w + 0.4, 0), (w + 0.4, run), (-w - 0.4, run))]])
    if entry:
        S.entry(f"{name}_foot", float(foot[0]), float(foot[2]), float(ybot))
        S.entry(f"{name}_top", float(top[0]), float(top[2]), float(ytop))
    return foot


def terrace(name, poly, top, face="platform", deck=True, kind="terrace foot", paved=True):
    """A terrace 台 on an outline: faces from just below the ground (the bed under water) up to its top, a coping, a flagged top; a deck the ways lie on."""
    poly = [tuple(map(float, p)) for p in Polygon(poly).buffer(0).exterior.coords[:-1]]
    if Polygon(poly).exterior.is_ccw:
        poly = poly[::-1]
    bots = S.skirt(poly, top - 0.18, face, step=2.0)
    for (ax, az), (bx, bz) in zip(poly, poly[1:] + poly[:1]):
        m.poly([(ax, top - 0.18, az), (bx, top - 0.18, bz), (bx, top, bz), (ax, top, az)], "coping")
    m.flat(poly, top, "pave" if paved else face)
    if deck:
        add_deck(name, poly, top)
    for i, (x, z) in enumerate(poly):
        if POOL.buffer(0.3).contains(Point(x, z)):
            S.JOINTS.append([f"{name}_{i}", x, bots[i], z, kind])
    return poly


def wall_run(pts_, h, name, gaps=(), thick=0.8, body="rubble", cap="grey", base_h=0.5, ytop=None):
    """A wall along pts_, broken where a gap (x, z, half width) lies on it; its feet are joints, its outline a footprint."""
    runs = []
    for (ax, az), (bx, bz) in zip(pts_[:-1], pts_[1:]):
        L = math.hypot(bx - ax, bz - az)
        ux, uz = (bx - ax) / L, (bz - az) / L
        cuts = []
        for gx, gz, hw in gaps:
            t = (gx - ax) * ux + (gz - az) * uz
            d = abs(-(gx - ax) * uz + (gz - az) * ux)
            if -hw < t < L + hw and d < 3.0:
                cuts.append((t - hw, t + hw))
        cur = 0.0
        for c0, c1 in sorted(cuts):
            if c0 > cur + 0.3:
                runs.append([(ax + ux * cur, az + uz * cur), (ax + ux * c0, az + uz * c0)])
            cur = max(cur, c1)
        if L > cur + 0.3:
            runs.append([(ax + ux * cur, az + uz * cur), (bx, bz)])
    for i, r in enumerate(runs):
        K.wall(r, h, thick=thick, cap=cap, base_h=base_h, body_mat=body, ytop=ytop)
        S.FOOTPRINTS.append([(float(x), float(z)) for x, z in list(LineString(r).buffer(thick / 2 + 0.1, cap_style="flat").exterior.coords)[:-1]])
        for k, (x, z) in enumerate(r):
            S.joint(f"{name}{i}_{k}", x, z, "wall foot", y=bed(x, z) - 0.15)
    return runs


def wall_gate(x, z, rot, name, w=2.2, h=3.4, thick=0.8, body="rubble", cap="grey"):
    """A gate in a wall 随墙门 (C): two piers, a lintel band, plank doors with studs, a small roof along the wall; entries both sides."""
    m.push(x, 0, z, rot)
    g = max(K.gy_local(a, b) for a in (-w / 2, w / 2) for b in (-thick, thick))
    y0 = min(bed(*m.world((a, 0, b))[::2]) for a in (-w / 2 - 0.5, w / 2 + 0.5) for b in (-thick, thick)) - 0.15
    for sg in (-1, 1):
        a0, a1 = (w / 2, w / 2 + 0.6) if sg > 0 else (-w / 2 - 0.6, -w / 2)
        m.box(a0, a1, y0, g + h - 0.6, -thick / 2 - 0.08, thick / 2 + 0.08, body)
        m.box(a0, a1, y0, g + 0.5, -thick / 2 - 0.1, thick / 2 + 0.1, "platform")
    m.box(-w / 2, w / 2, g + h - 1.25, g + h - 0.6, -thick / 2 - 0.05, thick / 2 + 0.05, "band")
    m.box(-w / 2, w / 2, y0, g + 0.15, -thick / 2 - 0.2, thick / 2 + 0.2, "step")
    for a0, a1 in ((-w / 2 + 0.05, -0.02), (0.02, w / 2 - 0.05)):
        m.box(a0, a1, g + 0.15, g + h - 1.25, -0.06, 0.06, "lacquer")
        for yy in (g + 0.9, g + 1.5, g + 2.1):
            for sg in (-1, 1):
                for k in range(3):
                    xx = a0 + (a1 - a0) * (k + 0.5) / 3
                    m.box(xx - 0.04, xx + 0.04, yy - 0.04, yy + 0.04, sg * 0.06 - 0.02, sg * 0.06 + 0.02, "gold")
    K.roof(lambda a, b, c: (a, b, c), w / 2 + 1.0, thick / 2 + 0.75, g + h - 0.7, g + h + 0.55, form="xu", rolled=True, ju=JU["gallery"], gable_mat="plaster", gableX=w / 2 + 1.0, tile=cap)
    for sg, tag in ((1, "in"), (-1, "out")):
        p_ = m.world((0, 0, sg * 1.3))
        S.entry(f"{name}_{tag}", float(p_[0]), float(p_[2]), float(ground(float(p_[0]), float(p_[2]))))
    m.pop()


def column(x, q, y0, y1, dia, mat="pillar"):
    r = dia / 2
    m.prism([(x + r * math.cos(2 * math.pi * (k + 0.5) / 8), q + r * math.sin(2 * math.pi * (k + 0.5) / 8)) for k in range(8)], y0, y1, mat, top=False)
    m.box(x - r - 0.1, x + r + 0.1, y0 - 0.02, y0 + 0.1, q - r - 0.1, q + r + 0.1, "coping")  # the base stone 柱顶石


def lump(x, z, r, y0, y1, rng, mat="rock", taper=(0.45, 0.85), k6=None):
    """One irregular rock: a ring of points round (x, z) at y0, a smaller ring shifted sideways and at uneven heights below y1, the top a fan to a peak: no two alike."""
    k6 = k6 or int(rng.integers(6, 9))
    a0 = rng.uniform(0, 2 * math.pi)
    lo = [(x + r * rng.uniform(0.65, 1.25) * math.cos(a0 + 2 * math.pi * (i + rng.uniform(-0.2, 0.2)) / k6), z + r * rng.uniform(0.65, 1.25) * math.sin(a0 + 2 * math.pi * (i + rng.uniform(-0.2, 0.2)) / k6)) for i in range(k6)]
    sx, sz = rng.uniform(-0.25, 0.25) * r, rng.uniform(-0.25, 0.25) * r
    hi = [(x + sx + (px - x) * rng.uniform(*taper), z + sz + (pz - z) * rng.uniform(*taper)) for px, pz in lo]
    h = y1 - y0
    yh = [y1 - h * rng.uniform(0.05, 0.3) for _ in hi]
    for i in range(k6):
        j = (i + 1) % k6
        m.poly([(lo[i][0], y0, lo[i][1]), (lo[j][0], y0, lo[j][1]), (hi[j][0], yh[j], hi[j][1])], mat)
        m.poly([(lo[i][0], y0, lo[i][1]), (hi[j][0], yh[j], hi[j][1]), (hi[i][0], yh[i], hi[i][1])], mat)
    cx_, cz_ = float(np.mean([p[0] for p in hi])), float(np.mean([p[1] for p in hi]))
    for i in range(k6):
        j = (i + 1) % k6
        m.poly([(hi[i][0], yh[i], hi[i][1]), (hi[j][0], yh[j], hi[j][1]), (cx_, y1, cz_)], mat)
    return lo


ROCK_FP = []


def rock_mass(name, poly, h_lo, h_hi, seed, step=1.7, keep_off=None, mat="rock", fp=True):
    """A rock mass 叠石 over an outline (S01's), as irregular blocks on a jittered grid, higher towards the middle; kept off the ways and `keep_off`. Heights C."""
    rng = np.random.default_rng(seed)
    pg = Polygon(poly).buffer(0).intersection(COURT_IN.buffer(-0.3))
    if keep_off is not None:
        pg = pg.difference(keep_off)
    pg = pg.difference(WAY_U)
    if pg.is_empty:
        return 0
    x0, z0, x1, z1 = pg.bounds
    depth = max(1.0, min(x1 - x0, z1 - z0))
    pp = prep(pg)
    n = 0
    for gx in np.arange(x0 + step / 2, x1, step):
        for gz in np.arange(z0 + step / 2, z1, step):
            x, z = gx + rng.uniform(-0.4, 0.4) * step, gz + rng.uniform(-0.4, 0.4) * step
            if not pp.contains(Point(x, z)):
                continue
            d = pg.boundary.distance(Point(x, z))
            t = min(1.0, d / (depth * 0.45))
            h = (h_lo + (h_hi - h_lo) * t) * rng.uniform(0.55, 1.0)
            r = step * rng.uniform(0.6, 0.85)
            g = ground(x, z)
            mt = mat if rng.uniform() < 0.6 else mat + "2"
            if h > 1.3:  # piled 叠石: a broad block below, a narrower one set off-centre on it
                h0 = h * rng.uniform(0.5, 0.65)
                lump(x, z, r, g - 0.2, g + h0, rng, mt, taper=(0.7, 0.95))
                lump(x + rng.uniform(-0.35, 0.35) * r, z + rng.uniform(-0.35, 0.35) * r, r * rng.uniform(0.55, 0.75), g + h0 - 0.15, g + h, rng, mt)
            else:
                lump(x, z, r, g - 0.2, g + h, rng, mt, taper=(0.55, 0.9))
            n += 1
    if fp:
        for gg in ([pg] if pg.geom_type == "Polygon" else [q for q in pg.geoms if q.area > 1.0]):
            S.FOOTPRINTS.append([(float(a), float(b)) for a, b in gg.exterior.coords[:-1]])
            ROCK_FP.append(gg)
    REPORT.setdefault("rocks", {})[name] = {"blocks": n, "area_m2": round(pg.area, 1), "h_m": [h_lo, h_hi]}
    return n


# ============================================================ the wall and the court
W4 = pts("wall")                    # NW, NE, SE, SW (the line's middle)
WALL_POLY = Polygon(W4)
COURT_IN = WALL_POLY.buffer(-0.45, join_style=2)
xg_s, zg_s = mid("gate_S_cell")[0], mid("gate_S")[1]
xg_n, zg_n = mid("gate_N")
lib_cols = [p[0] for p in pts("lib_cols")]
x_ming_plan = (lib_cols[2] + lib_cols[3]) / 2
lx0, lx1, lz0, lz1 = rect("lib")
lib_corners = pts("lib")
LZ = float(np.mean([p[1] for p in lib_corners]))       # the library's middle (the plan's grid), in depth
LX_PLAN = float(np.mean([p[0] for p in lib_corners]))   # and across
HX, HQ = sum(BAYS) / 2, sum(DEPTHS) / 2
XS = [-HX]
for b_ in BAYS:
    XS.append(XS[-1] + b_)
X_MING = (XS[3] + XS[4]) / 2                             # the 明间's middle in the library's own frame: 0.80 m east of its middle
LX = LX_PLAN                                             # the 丈尺册's rectangle centred on S01's grid
REPORT["layout"] = {"plan_lib_m": [round(lx1 - lx0, 2), round(lz1 - lz0, 2)], "lib_m": [round(2 * HX, 2), round(2 * HQ, 2)],
                    "ming_x_plan": round(x_ming_plan, 2), "ming_x_model": round(LX + X_MING, 2), "gate_S_x": round(xg_s, 2), "gate_N_x": round(xg_n, 2),
                    "lingfeng_x": round(mid("lingfeng")[0], 2), "court_m": [round(W4[1][0] - W4[0][0], 2), round(W4[3][1] - W4[0][1], 2)]}
P_TOP = Y_C + PL                                          # the library's floor
PL_HF, PL_HD = HX + 1.0, HQ + 0.9                          # its platform: 1.0 m beyond the end columns (the gable walls), 0.9 m beyond the front and back
YT_Z0 = LZ + PL_HD
yx0, yx1, _, yz1 = rect("yuetai")

# the court's floor: inside the wall, round the pool, split so that each piece has no hole
court = COURT_IN.difference(POOL)
pieces = []
for g_ in ([court] if court.geom_type == "Polygon" else list(court.geoms)):
    if g_.area < 1.0:
        continue
    if len(g_.interiors):
        cz = POOL.centroid.y
        for h_ in split(g_, LineString([(-200, cz), (200, cz)])).geoms:
            pieces.append(h_)
    else:
        pieces.append(g_)
for i, g_ in enumerate(pieces):
    ring_ = [(float(a), float(b)) for a, b in g_.exterior.coords[:-1]]
    m.flat(ring_, Y_C, "court")
    add_deck(f"court_{i}", ring_, Y_C)
S.CLEAR.append([(float(a), float(b)) for a, b in COURT_IN.exterior.coords[:-1]])
REPORT["court_m2"] = round(court.area, 1)

# the wall with its two gates
GATE_HF = 5.82
wall_run(W4 + [W4[0]], WALL_H, "wall", gaps=[(xg_s, zg_s, GATE_HF - 0.2), (xg_n, zg_n, 1.75)], ytop=Y_C + WALL_H)
N_WALL_FP = len(S.FOOTPRINTS)  # the rocks stand against the wall: its footprints are not in their keep-off set
m.cls = "fill"
wall_gate(xg_n, (W4[0][1] + (W4[1][1] - W4[0][1]) * (xg_n - W4[0][0]) / (W4[1][0] - W4[0][0])), 0.0, "gate_N")
m.cls = "doc"

# ============================================================ the pool: its face up to the court, rock on its banks, 玲峰 on its terrace
pool_ring = [(float(a), float(b)) for a, b in POOL.exterior.coords[:-1]]
if not Polygon(pool_ring).exterior.is_ccw:
    pool_ring = pool_ring[::-1]
_bots = S.skirt(pool_ring, Y_C, "rock_face", step=1.5)
yt_south = LineString([(yx0 - 1, yz1), (yx1 + 1, yz1)]).buffer(1.6)
rng_b = np.random.default_rng(4601)
bank = LineString(pool_ring + pool_ring[:1])
nb = int(bank.length / 1.1)
for k in range(nb):
    p_ = bank.interpolate(k * bank.length / nb)
    if yt_south.contains(p_):
        continue  # the terrace's own face meets the water there
    lump(p_.x, p_.y, rng_b.uniform(0.7, 1.1), WATER_Y - 0.6, Y_C + rng_b.uniform(-0.1, 0.45), rng_b, "rock" if k % 3 else "rock2", taper=(0.6, 0.9))
for i in range(0, len(pool_ring), max(1, len(pool_ring) // 12)):
    S.JOINTS.append([f"pool_{i}", pool_ring[i][0], _bots[i], pool_ring[i][1], "pool face foot"])

lf_x, lf_z = mid("lingfeng")
lx_a, lx_b, lz_a, lz_b = rect("lingfeng")
LF_TOP = WATER_Y + LF_TERR
oval = [(lf_x + (lx_b - lx_a) / 2 * math.cos(t), lf_z + (lz_b - lz_a) / 2 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 20, endpoint=False)]
oval_bed = min(bed(x, z) for x, z in oval) - 0.15
m.prism(oval, oval_bed, LF_TOP - 0.15, "platform", top=False)
m.frustum(oval, [(lf_x + (x - lf_x) * 1.02, lf_z + (z - lf_z) * 1.02) for x, z in oval], LF_TOP - 0.15, LF_TOP, "coping")
m.flat([(lf_x + (x - lf_x) * 1.02, lf_z + (z - lf_z) * 1.02) for x, z in oval], LF_TOP, "coping")
for k in range(0, 20, 5):
    S.JOINTS.append([f"lf_terrace_{k}", oval[k][0], oval_bed, oval[k][1], "terrace foot"])
S.FOOTPRINTS.append(oval)


def standing_rock(cx, cz, y0, h, seed):
    """玲峰: a tall pierced rock (C form after S05's 'eighty-one holes' and Malone's 'pierced with many holes'): tiers of blocks, two side by side at some tiers so that
    the light passes between them, the top heavier than the waist, the poem's panel cut on the south face."""
    rng = np.random.default_rng(seed)
    tiers = 10
    yy = y0
    off = 0.0
    prof = [0.75, 0.62, 0.5, 0.46, 0.52, 0.62, 0.74, 0.86, 0.9, 0.7]  # the waist narrow, the head broad: the 瘦 and 透 of a prized rock (C)
    for t in range(tiers):
        th = h / tiers * rng.uniform(0.9, 1.15)
        w = prof[t]
        off += rng.uniform(-0.12, 0.12)
        top_t = min(yy + th * 1.25, y0 + h)
        if t in (2, 5, 7):  # a hole through: two blocks with the light between them
            for sg in (-1, 1):
                lump(cx + off + sg * w * 0.6, cz + rng.uniform(-0.15, 0.15), w * 0.42, yy, top_t, rng, "rock_ling", taper=(0.8, 1.05), k6=8)
        else:
            lump(cx + off, cz + rng.uniform(-0.12, 0.12), w, yy, top_t, rng, "rock_ling", taper=(0.85, 1.1), k6=8)
        yy += th * 0.92
        if yy >= y0 + h - 0.2:
            break
    top = y0 + h
    # the poem cut on the face: a smoothed panel (its place and size C)
    m.poly([(cx - 0.22, y0 + 2.6, cz + 0.62), (cx + 0.22, y0 + 2.6, cz + 0.62), (cx + 0.2, y0 + 3.3, cz + 0.6), (cx - 0.2, y0 + 3.3, cz + 0.6)], "inscr")
    S.kp("lingfeng_top", (cx + off + 0.1, top, cz))
    S.kp("lingfeng_foot", (cx, y0, cz + 0.5))


standing_rock(lf_x, lf_z, LF_TOP, LF_ROCK, 4646)
S.kp("lf_terrace_S", (lf_x, LF_TOP, lf_z + (lz_b - lz_a) / 2))
REPORT["lingfeng"] = {"terrace_m": [round(lx_b - lx_a, 2), round(lz_b - lz_a, 2)], "terrace_top_above_water": LF_TERR, "rock_m": LF_ROCK, "x": round(lf_x, 2), "z": round(lf_z, 2),
                      "in_pool": bool(POOL.contains(Point(lf_x, lf_z)))}


# ============================================================ the library
def window2(sa, sb, qf, sgn, y0, y1):
    """An upper window band 槛窗 (the sisters' short upper windows, P0555): red frames round each leaf, lattice bars on the glazing set 0.12 m back."""
    w = sb - sa
    at = lambda a, y, d: (a, y, qf - sgn * d)
    F = lambda a0, a1, yy0, yy1, d, mat: m.poly([at(a0, yy1, d), at(a0, yy0, d), at(a1, yy0, d), at(a1, yy1, d)], mat)
    F(sa, sb, y0 - 0.08, y0, -0.03, "sill")
    F(sa + 0.08, sb - 0.08, y0, y1, 0.12, "glass_lattice")
    for a0_, a1_ in ((sa, sa + 0.08), (sb - 0.08, sb)):
        F(a0_, a1_, y0, y1, 0.0, "lacquer")
    F(sa, sb, y0, y0 + 0.08, 0.0, "lacquer")
    F(sa, sb, y1 - 0.08, y1, 0.0, "lacquer")
    for a in (sa + 0.08, sb - 0.08):
        m.poly([at(a, y1, 0), at(a, y0, 0), at(a, y0, 0.12), at(a, y1, 0.12)], "lacquer")
    m.poly([at(sa, y1 - 0.08, 0), at(sb, y1 - 0.08, 0), at(sb, y1 - 0.08, 0.12), at(sa, y1 - 0.08, 0.12)], "lacquer")
    leaves = max(2, round(w / 0.75))
    for k in range(1, leaves):  # the leaves' stiles
        s = sa + w * k / leaves
        F(s - 0.05, s + 0.05, y0, y1, 0.02, "lacquer")
    for k in range(1, leaves * 3):  # the lattice: thin bars, three a leaf, and two rails
        s = sa + w * k / (leaves * 3)
        F(s - 0.015, s + 0.015, y0 + 0.08, y1 - 0.08, 0.08, "lacquer")
    for f_ in (0.35, 0.68):
        yy = y0 + (y1 - y0) * f_
        F(sa + 0.08, sb - 0.08, yy - 0.015, yy + 0.015, 0.08, "lacquer")


def library():
    """文源阁 from the 丈尺册's figures (S105 note [4]) in the form of its sisters: the platform, the galleries front and back with the doors and windows at the inner
    columns, the grey brick gable walls 硬山 with their corbels 墀头, the skirt roof 腰檐 front and back, the upper storey over the whole depth with its windows and
    plaque, the 硬山 roof in black glaze with green trim and the white-and-green wave ridges."""
    m.push(LX, 0, LZ)
    K.platform(PL_HF, PL_HD, P_TOP, Y_C - 0.15)
    feet = {}
    for side in ("front", "back"):
        f = K.flight(side, X_MING, PL_HF, PL_HD, P_TOP, 3.6)
        if f:
            feet[side] = m.world(f)
    # the ground storey: the outer columns 廊柱 at the galleries' edge, the inner ones 金柱 at the façade
    q_in = HQ - DEPTHS[0]
    for x in XS:
        for q in (HQ, -HQ, q_in, -q_in):
            column(x, q, P_TOP, P_TOP + COL1 + 0.42, 0.40)
    for sg in (1, -1):
        qf = sg * q_in
        for i in range(len(BAYS)):
            K.opening(XS[i] + 0.2, XS[i + 1] - 0.2, qf, sg, P_TOP, P_TOP + COL1, i == 3, False)
        # the gallery: the beam over the outer columns, its ceiling, the hanging lattice 倒挂楣子 and the low rail 坐凳栏杆 (the rail C, after 文渊阁)
        m.box(-HX, HX, P_TOP + COL1, P_TOP + COL1 + 0.42, sg * HQ - 0.2, sg * HQ + 0.2, "band")
        m.box(-HX, HX, P_TOP + COL1 - 0.02, P_TOP + COL1, min(sg * q_in, sg * HQ), max(sg * q_in, sg * HQ), "underside")
        for i in range(len(BAYS)):
            a0, a1 = XS[i] + 0.22, XS[i + 1] - 0.22
            m.box(a0, a1, P_TOP + COL1 - 0.1, P_TOP + COL1, sg * HQ - 0.05, sg * HQ + 0.05, "rail_green")
            m.box(a0, a1, P_TOP + COL1 - 0.55, P_TOP + COL1 - 0.49, sg * HQ - 0.04, sg * HQ + 0.04, "rail_green")
            nbar = max(2, int((a1 - a0) / 0.28))
            for kb in range(1, nbar):
                xb = a0 + (a1 - a0) * kb / nbar
                m.box(xb - 0.02, xb + 0.02, P_TOP + COL1 - 0.5, P_TOP + COL1 - 0.1, sg * HQ - 0.03, sg * HQ + 0.03, "rail_green")
            m.box(a0, a1, P_TOP + COL1 - 0.33, P_TOP + COL1 - 0.29, sg * HQ - 0.03, sg * HQ + 0.03, "rail_green")
            if i != 3:  # the low rail: a sill, a top rail and bars (文渊阁's, P0555; C)
                m.box(a0, a1, P_TOP, P_TOP + 0.1, sg * HQ - 0.12, sg * HQ + 0.12, "rail_green")
                m.box(a0, a1, P_TOP + 0.62, P_TOP + 0.7, sg * HQ - 0.1, sg * HQ + 0.1, "rail_green")
                for kb in range(1, max(2, int((a1 - a0) / 0.22))):
                    xb = a0 + (a1 - a0) * kb / max(2, int((a1 - a0) / 0.22))
                    m.box(xb - 0.02, xb + 0.02, P_TOP + 0.1, P_TOP + 0.62, sg * HQ - 0.02, sg * HQ + 0.02, "rail_green")
    m.box(-HX + 0.3, HX - 0.3, P_TOP, P_TOP + COL1 - 0.05, -q_in + 0.25, q_in - 0.25, "glass_lattice")
    # the gable walls 山墙, grey brick on a stone base 下碱, full height, with their corbels 墀头 under the eaves at both ends
    WX0, WX1 = HX - 0.35, HX + 0.5
    for sx in (1, -1):
        xa, xb = sorted((sx * WX0, sx * WX1))
        m.box(xa, xb, P_TOP - 0.02, P_TOP + 1.1, -HQ - SK_OUT + 0.25, HQ + SK_OUT - 0.25, "brick_dark")
        m.box(xa, xb, P_TOP + 1.1, P_TOP + SK_TIP - 0.2, -HQ - SK_OUT + 0.25, HQ + SK_OUT - 0.25, "brick")  # the ground storey's end piers 墀头 under the skirt roof's ends (as 文津阁, P0551)
        m.box(xa, xb, P_TOP + SK_TIP - 0.2, P_TOP + Y_TIP, -HQ - 0.5, HQ + 0.5, "brick")
        for sq in (1, -1):  # the wall between the skirt roof's slope and the upper storey
            q0_, q1_ = sq * (HQ + 0.5), sq * (HQ + SK_OUT - 0.25)
            for xf in (xa, xb):
                m.poly([(xf, P_TOP + SK_TIP - 0.2, q0_), (xf, P_TOP + SK_TIP - 0.2, q1_), (xf, P_TOP + SK_TIP + 0.05, q1_), (xf, P_TOP + SK_TOP - 0.1, q0_)], "brick")
        for sq in (1, -1):
            for k, (dy0, dy1, out) in enumerate(((1.6, 1.15, 0.15), (1.15, 0.8, 0.3), (0.8, 0.5, 0.45))):
                qa, qb = sorted((sq * (HQ + 0.5), sq * (HQ + 0.5 + out)))
                m.box(xa - 0.05, xb + 0.05, P_TOP + Y_TIP - dy0, P_TOP + Y_TIP - dy1 + 0.02, qa, qb, "brick" if k < 2 else "coping")
            # the pier's cap 戗檐 under the skirt roof's end
            qa, qb = sorted((sq * (HQ + 0.5), sq * (HQ + SK_OUT)))
            m.box(xa - 0.06, xb + 0.06, P_TOP + SK_TIP - 0.45, P_TOP + SK_TIP - 0.2, qa, qb, "coping")
    # the skirt roof 腰檐: front and back, from the upper façade out beyond the outer columns, black with the green edge
    for sg in (1, -1):
        xl, xr = -WX1, WX1
        q0, q1 = sg * (HQ - 0.05), sg * (HQ + SK_OUT)
        y0, y1 = P_TOP + SK_TOP, P_TOP + SK_TIP
        qm, ym = q0 + (q1 - q0) * 0.62, y0 + (y1 - y0) * 0.66 - 0.06  # a slight sag: the 举架's curve
        m.poly([(xl, y0, q0), (xr, y0, q0), (xr, ym, qm), (xl, ym, qm)], "tile_black")
        m.poly([(xl, ym, qm), (xr, ym, qm), (xr, y1 + 0.12, q1), (xl, y1 + 0.12, q1)], "tile_green")
        m.poly([(xl, y1 + 0.12, q1), (xr, y1 + 0.12, q1), (xr, y1 - 0.12, q1), (xl, y1 - 0.12, q1)], "fascia")
        m.poly([(xl, y1 - 0.12, q1), (xr, y1 - 0.12, q1), (xr, y0 - 0.3, q0), (xl, y0 - 0.3, q0)], "underside")
        m.box(xl, xr, y0 - 0.02, y0 + 0.2, min(q0, q0 - sg * 0.25), max(q0, q0 - sg * 0.25), "ridge_black")
        for xe in (xl, xr):  # the end tiles rolled down the wall's corbel
            m.poly([(xe, y0 + 0.2, q0), (xe, ym + 0.15, qm), (xe, y1 + 0.25, q1), (xe, y1 - 0.12, q1), (xe, y0 - 0.3, q0)], "tile_green")
    # the upper storey over the whole depth: the plaster band, the windows between dark green columns, the beam, the plaque
    for sg in (1, -1):
        qf = sg * HQ
        m.box(-WX0, WX0, P_TOP + COL1 + 0.42, P_TOP + SK_TOP - 0.25, min(qf, qf - sg * 0.3), max(qf, qf - sg * 0.3), "underside")  # the beams' zone under the skirt, in shade (P0555)
        m.box(-WX0, WX0, P_TOP + SK_TOP - 0.25, P_TOP + WIN2[0], min(qf, qf - sg * 0.3), max(qf, qf - sg * 0.3), "wall")
        m.box(-WX0, WX0, P_TOP + WIN2[1], P_TOP + UP_TOP, min(qf, qf - sg * 0.3), max(qf, qf - sg * 0.3), "wall")
        for i in range(len(BAYS)):
            window2(XS[i] + 0.2, XS[i + 1] - 0.2, qf, sg, P_TOP + WIN2[0], P_TOP + WIN2[1])
        for x in XS:
            column(x, qf, P_TOP + SK_TOP - 0.1, P_TOP + UP_TOP, 0.38)
        m.box(-WX0, WX0, P_TOP + UP_TOP, P_TOP + EAVE2, sg * HQ - 0.22, sg * HQ + 0.22, "band")
        m.box(-WX0, WX0, P_TOP + EAVE2, P_TOP + Y_TIP + 0.55, sg * HQ - 0.25, sg * HQ + 0.25, "underside")  # the rafters' zone under the top eave
    m.box(-HX + 0.4, HX - 0.4, P_TOP + SK_TOP, P_TOP + UP_TOP - 0.05, -HQ + 0.35, HQ - 0.35, "glass_lattice")
    xm = X_MING
    yp0, yp1 = P_TOP + WIN2[1] - 0.35, P_TOP + Y_TIP + 0.2  # the plaque hangs over the eave's shade down onto the windows' head (文渊阁's, P0555)
    m.box(xm - 0.5, xm + 0.5, yp0, yp1, HQ + 0.28, HQ + 0.36, "gold")
    m.box(xm - 0.38, xm + 0.38, yp0 + 0.12, yp1 - 0.12, HQ + 0.36, HQ + 0.39, "plaque")
    for nm_, yy_ in (("lib_plaque_top", yp1), ("lib_plaque_bottom", yp0)):
        w_ = m.world((xm, 0, HQ + 0.36))
        S.kp(nm_, (w_[0], yy_, w_[2]))
    # the roof: 硬山, its gables in the walls' plane, black with green trim; the ridges green with the white waves
    y_tip = P_TOP + Y_TIP
    hz = HQ + O2
    ridge = y_tip + RISE * hz
    m.poly([(-WX0, P_TOP + Y_TIP + 0.5, HQ + 0.22), (WX0, P_TOP + Y_TIP + 0.5, HQ + 0.22), (WX0, P_TOP + Y_TIP + 0.5, -HQ - 0.22), (-WX0, P_TOP + Y_TIP + 0.5, -HQ - 0.22)], "underside")
    K.roof(lambda x, y, z: (x, y, z), WX1 + 0.08, hz, y_tip, ridge, form="ys", rolled=False, ju=JU["storeyed_hall"], tile="black", edge="green",
           gable_mat="brick", gableX=WX1, ridge_mat="ridge_green")
    prof_r = profile(JU["storeyed_hall"])
    for sx in (1, -1):  # the barge band 博缝 along each gable's rake, proud of the wall
        xg = sx * (WX1 + 0.04)
        for sg in (1, -1):
            for j in range(8):
                v0, v1 = j / 8, (j + 1) / 8
                qa_, qb_ = sg * hz * (1 - v0), sg * hz * (1 - v1)
                ya_, yb_ = y_tip + (ridge - y_tip) * prof_r(v0), y_tip + (ridge - y_tip) * prof_r(v1)
                m.poly([(xg, ya_ - 0.02, qa_), (xg, yb_ - 0.02, qb_), (xg, yb_ - 0.5, qb_), (xg, ya_ - 0.5, qa_)], "brick_dark")
    hr = min(0.9, max(0.3, 0.1 + 0.06 * hz))
    for sg in (1, -1):  # Malone's 'wave design in white and green': white crests along the main ridge's faces (their form C)
        n = int(2 * (WX1 - 0.6) / 0.7)
        for k in range(n):
            x0 = -(WX1 - 0.6) + k * 0.7
            m.poly([(x0, ridge + 0.1, sg * 0.165), (x0 + 0.25, ridge + hr * 0.5, sg * 0.165), (x0 + 0.45, ridge + hr * 0.35, sg * 0.165), (x0 + 0.7, ridge + 0.1, sg * 0.165)], "wave_white")
    c0 = m.world((0, 0, 0))
    for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        w = m.world((sx * PL_HF, 0, sq * PL_HD))
        tag = compass(w[0] - c0[0], w[2] - c0[2])
        S.kp(f"lib_pl_top_{tag}", (w[0], P_TOP, w[2]))
        w = m.world((sx * (WX1 + 0.08), 0, sq * hz))
        S.kp(f"lib_eave_{tag}", (w[0], y_tip, w[2]))
        w = m.world((sx * WX1, 0, sq * (HQ + 0.5)))
        S.kp(f"lib_wall_foot_{tag}", (w[0], P_TOP, w[2]))
        S.kp(f"lib_wall_top_{tag}", (w[0], P_TOP + Y_TIP - 1.6, w[2]))
        w = m.world((sx * WX1, 0, sq * (HQ + SK_OUT)))
        S.kp(f"lib_sk_tip_{tag}", (w[0], P_TOP + SK_TIP, w[2]))
    for sx in (-1, 1):
        w = m.world((sx * (WX1 + 0.08), 0, 0))
        S.kp(f"lib_ridge_{'W' if sx < 0 else 'E'}", (w[0], ridge, w[2]))
    for i, x in enumerate(XS):  # the outer columns of the front and back, numbered from the west
        for sq, tag in ((1, "S"), (-1, "N")):
            w = m.world((x, 0, sq * HQ))
            S.kp(f"lib_col{tag}{i}_foot", (w[0], P_TOP, w[2]))
            S.kp(f"lib_col{tag}{i}_top", (w[0], P_TOP + COL1, w[2]))
            S.kp(f"lib_ucol{tag}{i}_top", (w[0], P_TOP + UP_TOP, w[2]))
            w = m.world((x, 0, sq * (HQ + SK_OUT)))
            S.kp(f"lib_sk{tag}{i}", (w[0], P_TOP + SK_TIP - 0.12, w[2]))  # the skirt's drip in front of the column (P0555's line read at the column)
            w = m.world((x, 0, sq * (HQ + O2)))
            S.kp(f"lib_eave{tag}{i}", (w[0], P_TOP + Y_TIP - 0.22, w[2]))  # the top eave's drip in front of the column
    corners = [m.world((sx * PL_HF, 0, sq * PL_HD)) for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    m.pop()
    S.FOOTPRINTS.append([(float(c[0]), float(c[2])) for c in corners])
    add_deck("lib_platform", [(float(c[0]), float(c[2])) for c in corners], P_TOP, register=False)
    for k, f in feet.items():
        S.entry(f"lib_{k}", float(f[0]), float(f[2]), float(f[1]))
    REPORT["halls"]["lib"] = {"frontage_m": round(2 * HX, 2), "depth_m": round(2 * HQ, 2), "platform_m": [round(2 * PL_HF, 2), round(2 * PL_HD, 2), PL],
                              "column_m": COL1, "skirt_drip_m": round(SK_TIP - 0.12, 2), "windows2_m": list(WIN2), "eave_drip_m": round(Y_TIP - 0.22, 2), "ridge_m": round(ridge - P_TOP, 2), "ridge_above_court_m": round(ridge - Y_C, 2), "bays": BAYS, "depths": DEPTHS,
                              "x": round(LX, 2), "z": round(LZ, 2), "floor_y": round(P_TOP, 2)}
    return ridge


# the terrace 月台 first (the library's front flight lands on it)
yt_poly = [(yx0, YT_Z0 - 0.3), (yx1, YT_Z0 - 0.3), (yx1, yz1), (yx0, yz1)]
terrace("yuetai", yt_poly, Y_C + YT, face="platform")
zmid = (YT_Z0 + yz1) / 2
for nm, xx, rot in (("yt_W", yx0, -math.pi / 2), ("yt_E", yx1, math.pi / 2)):
    flight(nm, xx, zmid, rot, 2.6, Y_C + YT, Y_C)
S.FOOTPRINTS.append(yt_poly)
REPORT["yuetai_m"] = [round(yx1 - yx0, 2), round(yz1 - YT_Z0, 2)]
S.kp("yt_SW", (yx0, Y_C + YT, yz1))
S.kp("yt_SE", (yx1, Y_C + YT, yz1))
RIDGE = library()

# ============================================================ the stele pavilion 碑亭 (its platform from the 丈尺册, its form C)
bx_, bz_ = mid("beiting")
m.cls = "fill"
m.push(bx_, 0, bz_)
hs = BT_SIDE / 2
K.platform(hs, hs, Y_C + BT_PL, Y_C - 0.15)
f_bt = K.flight("front", 0.0, hs, hs, Y_C + BT_PL, 2.0)
cs = hs - 0.5
col_top = Y_C + BT_PL + 3.3
for x in (-cs, cs):
    for q in (-cs, cs):
        column(x, q, Y_C + BT_PL, col_top + 0.4, 0.32, "lacquer")
K.bands(cs, cs, col_top + 0.42, False, 0.32, col_top + 0.42)
for sg in (1, -1):
    m.box(-cs + 0.18, cs - 0.18, col_top - 0.45, col_top - 0.05, sg * cs - 0.03, sg * cs + 0.03, "lacquer")
    m.box(sg * cs - 0.03, sg * cs + 0.03, col_top - 0.45, col_top - 0.05, -cs + 0.18, cs - 0.18, "lacquer")
K.pyramid(cs + 0.95, cs + 0.95, col_top + 0.42 - 0.45, col_top + 0.42 + 2.3, tile="black", edge="green")
m.cls = "doc"
yb = Y_C + BT_PL
m.box(-0.8, 0.8, yb, yb + 0.15, -0.45, 0.45, "marble")       # the stele 碑 on its base 须弥座 (Malone: marble; the form C)
m.box(-0.7, 0.7, yb + 0.15, yb + 0.55, -0.37, 0.37, "marble")
m.box(-0.78, 0.78, yb + 0.55, yb + 0.72, -0.43, 0.43, "marble")
m.box(-0.55, 0.55, yb + 0.72, yb + 2.85, -0.17, 0.17, "stele")
m.poly([(-0.45, yb + 1.0, 0.175), (0.45, yb + 1.0, 0.175), (0.45, yb + 2.6, 0.175), (-0.45, yb + 2.6, 0.175)], "inscr")
m.lathe([(0.0, yb + 2.85), (0.62, yb + 2.85), (0.64, yb + 3.15), (0.5, yb + 3.4), (0.0, yb + 3.55)], 12, "stele", cx=0.0, cz=0.0)
c0 = m.world((0, 0, 0))
for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
    w = m.world((sx * hs, 0, sq * hs))
    S.kp(f"bt_pl_top_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], Y_C + BT_PL, w[2]))
S.kp("bt_finial", m.world((0, col_top + 0.42 + 2.3, 0)))
fbt = m.world(f_bt) if f_bt else None
m.pop()
S.FOOTPRINTS.append([(bx_ - hs, bz_ - hs), (bx_ + hs, bz_ - hs), (bx_ + hs, bz_ + hs), (bx_ - hs, bz_ + hs)])
add_deck("bt_platform", [(bx_ - hs, bz_ - hs), (bx_ + hs, bz_ - hs), (bx_ + hs, bz_ + hs), (bx_ - hs, bz_ + hs)], Y_C + BT_PL, register=False)
if fbt is not None:
    S.entry("bt_front", float(fbt[0]), float(fbt[2]), float(fbt[1]))
REPORT["halls"]["beiting"] = {"platform_m": BT_SIDE, "plan_square_m": [round(rect("beiting")[1] - rect("beiting")[0], 2), round(rect("beiting")[3] - rect("beiting")[2], 2)],
                              "eave_m": round(col_top + 0.42 - 0.45 - Y_C, 2), "finial_m": round(col_top + 0.42 + 2.3 - Y_C, 2), "x": round(bx_, 2), "z": round(bz_, 2)}

# ============================================================ the south gate (three bays astride the wall; C form, the kit's gate)
m.cls = "fill"
GB = [3.4, 3.84, 3.4]
gate_hd = 2.7
foot_g = min(bed(xg_s + a, zg_s + b) for a in (-GATE_HF, GATE_HF) for b in (-gate_hd, gate_hd)) - 0.15
Hg = dict(hf=GATE_HF, hd=gate_hd, base=Y_C, foot=foot_g, pl=0.45, eave=4.47, ridge=6.35, e=0.5, o=0.9, b=GB, d=[2 * gate_hd - 1.0], pf=0.0, pb=0.0, ps=0.0, dia=0.34,
          st={"front": [0.0], "back": [0.0]}, fw={"front": 3.0, "back": 3.0}, bal=0, rf="ys", rl=1, db=0, ju=JU["gate_hall"], t="grey", te=None, bd="bm", dr=[1], rr="d", k="gate")
m.push(xg_s, 0, zg_s)
gfeet = K.hall(Hg)
gw = {k: m.world(v) for k, v in gfeet.items()}
c0 = m.world((0, 0, 0))
for sx, sq in ((-1, 1), (1, 1)):
    w = m.world((sx * GATE_HF, 0, sq * gate_hd))
    S.kp(f"gate_pl_top_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], Y_C + 0.45, w[2]))
m.pop()
m.cls = "doc"
S.FOOTPRINTS.append([(xg_s - GATE_HF, zg_s - gate_hd), (xg_s + GATE_HF, zg_s - gate_hd), (xg_s + GATE_HF, zg_s + gate_hd), (xg_s - GATE_HF, zg_s + gate_hd)])
if not any(k.startswith("front") for k in gw):  # the ground outside meets the gate's floor: the threshold is the door
    gw["front_+0.0"] = np.array([xg_s, ground(xg_s, zg_s + gate_hd + 0.3), zg_s + gate_hd + 0.3])
for k, f in gw.items():
    S.entry(f"gate_S_{k}", float(f[0]), float(f[2]), float(f[1]))
    if not any(pp.covers(Point(float(f[0]), float(f[2]))) for _, _, _, pp in DECKS):
        S.joint(f"gate_S_{k}_foot", float(f[0]), float(f[2]), "flight foot", y=float(f[1]) - 0.05)
add_deck("gate_S_floor", [(xg_s - GATE_HF, zg_s - gate_hd), (xg_s + GATE_HF, zg_s - gate_hd), (xg_s + GATE_HF, zg_s + gate_hd), (xg_s - GATE_HF, zg_s + gate_hd)], Y_C + 0.45, register=False)
# the forecourt outside the gate, open ground to the gap in the double line (S01): no generated hill, no planting there (clear)
gx0, gx1, gz0, gz1 = rect("gap_S")
S.CLEAR.append([(xg_s - 7.0, zg_s + gate_hd), (xg_s + 7.0, zg_s + gate_hd), (max(gx1, xg_s) + 4.0, gz0), (min(gx0, xg_s) - 4.0, gz0)])
REPORT["forecourt_m"] = round(gz0 - zg_s - gate_hd, 2)
REPORT["halls"]["gate_S"] = {"frontage_m": round(2 * GATE_HF, 2), "depth_m": round(2 * gate_hd, 2), "bays": GB, "eave_m": Hg["eave"], "ridge_m": Hg["ridge"]}

# ============================================================ the rockeries (S01's outlines), 趣亭 on the south one, the pond in the north-east corner
keep = unary_union([POOL.buffer(0.4), Polygon(yt_poly).buffer(0.8)])
qx, qz = mid("quting")
QT_HS = 1.6
qt_pad = sbox(qx - QT_HS - 0.6, qz - QT_HS - 0.6, qx + QT_HS + 0.6, qz + QT_HS + 0.6)
stair_band = sbox(qx - 1.0, qz - QT_HS - 0.6 - 2.6 * 2.0, qx + 1.0, qz - QT_HS - 0.4)
ne = pts("rocks_NE")
pond_c = (ne[1][0] - 4.6, ne[1][1] + 3.6)
POND = Point(*pond_c).buffer(2.4, 8)
POND = Polygon([(pond_c[0] + 2.8 * math.cos(t) * (1 + 0.12 * math.sin(3 * t)), pond_c[1] + 2.1 * math.sin(t) * (1 + 0.12 * math.cos(2 * t))) for t in np.linspace(0, 2 * math.pi, 16, endpoint=False)])
blocked = unary_union([keep, qt_pad, stair_band, POND.buffer(0.2), Point(*mid("stone_S")).buffer(1.0), Point(*mid("stone_W")).buffer(1.0)] + [Polygon(fp).buffer(0.5) for fp in S.FOOTPRINTS[N_WALL_FP:]])
n_rocks = 0
n_rocks += rock_mass("north_W", pts("rocks_N", 0), 0.8, 1.9, 11, keep_off=blocked)
n_rocks += rock_mass("north_E", pts("rocks_N", 1), 0.8, 1.9, 12, keep_off=blocked)
n_rocks += rock_mass("NE", ne, 1.2, 2.6, 13, keep_off=blocked)
n_rocks += rock_mass("west", pts("rocks_W"), 0.7, 1.7, 14, keep_off=blocked)
n_rocks += rock_mass("east", pts("rocks_E"), 0.7, 1.7, 15, keep_off=blocked)
n_rocks += rock_mass("SW", pts("rocks_SW"), 1.2, 2.8, 16, keep_off=blocked)
n_rocks += rock_mass("SE", pts("rocks_SE"), 1.2, 2.6, 17, keep_off=blocked)
n_rocks += rock_mass("pool_W", pts("rock_poolW"), 0.8, 1.8, 18, keep_off=blocked)
n_rocks += rock_mass("SE_group", pts("rock_SE"), 0.8, 2.0, 19, keep_off=blocked)
n_rocks += rock_mass("south", pts("rock_S"), 1.8, QT_Y + 0.8, 20, keep_off=blocked, step=1.6)
REPORT["rock_blocks"] = n_rocks
S.kp("rock_S_top", (qx, Y_C + QT_Y + 0.8, qz + QT_HS + 1.5))

# 趣亭: a pad of rock at the summit, the pavilion, a stair of rock down to the way along the pool (C)
m.cls = "fill"
qy = Y_C + QT_Y
pad = [(qx - QT_HS - 0.6, qz - QT_HS - 0.6), (qx + QT_HS + 0.6, qz - QT_HS - 0.6), (qx + QT_HS + 0.6, qz + QT_HS + 0.6), (qx - QT_HS - 0.6, qz + QT_HS + 0.6)]
S.skirt(pad, qy, "rock_face")
m.flat(pad, qy, "rock")
rng_q = np.random.default_rng(4650)
for (ax, az), (bx, bz) in zip(pad, pad[1:] + pad[:1]):
    for t in np.linspace(0, 1, 5)[:-1]:
        x, z = ax + (bx - ax) * t, az + (bz - az) * t
        if abs(x - qx) < 1.2 and z < qz:
            continue  # the stair's head
        lump(x, z, rng_q.uniform(0.5, 0.8), Y_C - 0.1, qy + rng_q.uniform(-0.2, 0.5), rng_q, "rock")
add_deck("quting_pad", pad, qy, register=False)
m.push(qx, 0, qz)
Hq = dict(hf=QT_HS, hd=QT_HS, base=qy, foot=qy - 0.1, pl=0.25, eave=3.0, ridge=4.6, e=0.3, o=0.75, b=[2 * QT_HS - 0.6], d=[2 * QT_HS - 0.6], pf=0.0, pb=0.0, ps=0.0, dia=0.24,
          st={}, bal=0, rf="xs", rl=0, db=0, ju=JU["pavilion"], t="yellow", te="green", bd="bm", dr=[0], rr="d", k="hall", side_wall=False)
cs_q = QT_HS - 0.3
for x in (-cs_q, cs_q):
    for q in (-cs_q, cs_q):
        column(x, q, qy + 0.25, qy + 3.0, 0.24, "lacquer")
K.platform(QT_HS, QT_HS, qy + 0.25, qy - 0.1)
K.bands(cs_q, cs_q, qy + 3.0, False, 0.24, qy + 3.0)
for sg in (1, -1):
    m.box(-cs_q + 0.14, cs_q - 0.14, qy + 2.2, qy + 2.55, sg * cs_q - 0.03, sg * cs_q + 0.03, "lacquer")
    m.box(sg * cs_q - 0.03, sg * cs_q + 0.03, qy + 2.2, qy + 2.55, -cs_q + 0.14, cs_q - 0.14, "lacquer")
    m.box(-cs_q + 0.14, cs_q - 0.14, qy + 0.25, qy + 0.7, sg * cs_q - 0.12, sg * cs_q + 0.12, "lacquer") if sg > 0 else None
K.pyramid(cs_q + 0.75, cs_q + 0.75, qy + 3.0 - 0.38, qy + 4.6, tile="yellow", edge="green")
S.kp("quting_ridge", m.world((0, qy + 4.6, 0)))
m.pop()
f_q = flight("quting_stair", qx, qz - QT_HS - 0.6, math.pi, 1.8, qy, Y_C, mat="rock")
m.cls = "doc"
S.FOOTPRINTS.append(pad)
REPORT["halls"]["quting"] = {"side_m": 2 * QT_HS, "floor_above_court_m": QT_Y, "ridge_above_court_m": round(QT_Y + 4.6, 2), "x": round(qx, 2), "z": round(qz, 2)}

# the pond in the north-east corner (the dig; C): a sunk basin, its water, a rim of rock
m.cls = "fill"
pr = [(float(a), float(b)) for a, b in POND.exterior.coords[:-1]]
if not Polygon(pr).exterior.is_ccw:
    pr = pr[::-1]
for (ax, az), (bx, bz) in zip(pr, pr[1:] + pr[:1]):
    m.poly([(ax, Y_C - 0.9, az), (bx, Y_C - 0.9, bz), (bx, Y_C + 0.02, bz), (ax, Y_C + 0.02, az)], "rock_face")
m.flat(pr, Y_C - 0.9, "rock_face")
m.flat(pr, Y_C - 0.35, "water")
rng_p = np.random.default_rng(4660)
for k in range(0, len(pr), 1):
    x, z = pr[k]
    lump(x, z, rng_p.uniform(0.45, 0.75), Y_C - 0.6, Y_C + rng_p.uniform(0.2, 0.8), rng_p, "rock")
S.FOOTPRINTS.append(pr)
m.cls = "doc"

# the standing stone and the two pedestals S01 draws (C)
m.cls = "fill"
standing = np.random.default_rng(4670)
for nm in ("stone_W", "stone_S"):
    sx_, sz_ = mid(nm)
    lump(sx_, sz_, 0.5, ground(sx_, sz_) - 0.1, ground(sx_, sz_) + 1.6, standing, "rock_ling", taper=(0.6, 0.9))
    S.FOOTPRINTS.append([(sx_ - 0.6, sz_ - 0.6), (sx_ + 0.6, sz_ - 0.6), (sx_ + 0.6, sz_ + 0.6), (sx_ - 0.6, sz_ + 0.6)])
for nm in ("sq_W", "sq_E"):
    x_, z_ = mid(nm)
    g_ = ground(x_, z_)
    m.box(x_ - 0.6, x_ + 0.6, g_ - 0.1, g_ + 0.55, z_ - 0.6, z_ + 0.6, "marble")
    m.box(x_ - 0.7, x_ + 0.7, g_ + 0.55, g_ + 0.65, z_ - 0.7, z_ + 0.7, "marble")
    lump(x_, z_, 0.35, g_ + 0.65, g_ + 1.5, standing, "rock_ling", taper=(0.6, 0.9))
    S.FOOTPRINTS.append([(x_ - 0.7, z_ - 0.7), (x_ + 0.7, z_ - 0.7), (x_ + 0.7, z_ + 0.7), (x_ - 0.7, z_ + 0.7)])
m.cls = "doc"

# ============================================================ joints on the decks (measured here, not by tools/check_models.py)
for nm, x, y, z in S.ENTRIES:
    on = [(top, dn) for dn, top, pg, pp in DECKS if pp.covers(Point(x, z))]
    if on:
        REPORT["deck_joints"].append([nm, max(on)[1], round(y - ground(x, z), 3)])

# ============================================================ write
REPORT["triangles"] = m.count()
n_bytes = m.write_glb(HERE / "model.glb", "YM46 文源阁 Wenyuan Ge", extras={"frame": "x east along the front, y up, z south; origin at the library's box front middle"})
aliases = ["YM46-01", "YM46-02", "YM46-03", "YM46-N01", "YM46-N02"]
lib = REPORT["halls"]["lib"]
summary = {
    "id": "YM46",
    "aliases": aliases,
    "name": "文源阁 Wenyuan Ge",
    "glb": "model.glb",
    "position": S.pos,
    "rotationY": S.rot,
    "line": "The library of the Four Treasuries in its walled rock garden, as S01 draws the court and the texts and the dig of 2024 describe it: the library's six bays and its depth from the Guangxu 丈尺册 (B), two storeys outside with the skirt roof of its sisters 文津阁 and 文渊阁, black glazed tile with green trim (the dig), the terrace on the pool, 玲峰 on its stone terrace in the water, the stele pavilion, the rockeries, the wall and the gates; every height and the smaller buildings' forms are C. No picture of 文源阁 standing is known.",
    "rows": [
        ["The library", f"文源阁 (1774; S05 上下各六楹): six bays from the west, the stair bay 1.60 m, 4.00, 4.00, the 明间 5.12, 4.00, 4.00 m, 22.72 m, and 14.72 m deep with galleries of 3.52 m front and back (the Guangxu 丈尺册, S105: B; S01 draws the same grid within 1-1.6 m); doors in the 明间, windows in the other bays, the stair bay at the west"],
        ["Its form", f"Two storeys outside, three inside (S105: a mezzanine), a skirt roof 腰檐 front and back between grey brick gable walls (S105; the form of 文津阁, which the 1776 poem says it copies, and of 文渊阁: twins, form only); dark green columns (S105), red frames (the sisters); the plaque 文源閣 in Qianlong's hand under the upper eave (S05); the storeys measured on 文渊阁's front (P0555) in 文源阁's bays: columns {COL1} m, the skirt's drip {SK_TIP - 0.12:.2f} m, the upper windows {WIN2[0]}-{WIN2[1]} m, the top eave's drip {Y_TIP - 0.22:.2f} m above the floor (a twin's proportion, C; Q287)"],
        ["The roof", "硬山 in black glazed tile with green trim (the dig, S133; S105), the ridges green with white waves (Malone saw fragments of white-and-green wave-pattern tile, S02 p.90); a 歇山 is also argued for (Q111): 硬山 follows 文津阁 and 天一阁"],
        ["玲峰 and the pool", f"The pool before the library (S01; Round 10's water) with rock banks (Malone) and the terrace 月台 on its north side (S01; the 1776 poem's 月臺); 玲峰 on its oval stone terrace in the water (S01; the dig: a base of long slabs tied with iron dovetails), {LF_ROCK} m high (Malone's '12 or 15 feet': B; S105 says over 6 m, Q288), pierced, Qianlong's poem cut on it (S05); its form C"],
        ["Stele pavilion", "East of the library (S05: 閣東亭内石碣刋御製文源閣記): its platform 4.48 m square (the 丈尺册, S105; Q110), the stele of the 文源阁记 (Malone saw it standing); the pavilion's form and tile C"],
        ["The garden", "Rock banks inside the wall, rock masses in the corners and the rockery between the pool and the south gate as S01 draws them (the 1776 poem: 詭石堆竒岫; the dig: culverts under the rockery behind the gate); 趣亭 on its summit (named by the dig, S133; its place and form C, after the sister's pavilion on its rockery, P0550); a small pond in the north-east corner (the dig, S942; place and size C)"],
        ["Wall and gates", "The court's wall of 虎皮石 rubble (the dig, S133), the three-bay south gate and the north gate (S01; the dig); their heights and forms C; the court raised a little above the land outside (the dig, S942; its level C)"],
        ["What survives", "The library and the stele pavilion's platforms, the gate and its steps, the base of 玲峰 and its broken pieces (S105, S134; dug in 2024 by 北京市考古研究院, S133); Malone saw the marble stele still standing in the 1930s (S02 p.89); where it stands now is not in what we have read"],
        ["Assumed", f"Every height (the storeys after the sister 文渊阁, the platform {PL} m, the court {Y_C} m, the roof's rise), the end piers and corbels, the rails, the wave crests' form, the gates', the stele pavilion's and 趣亭's forms, the rocks' shapes and heights, the pond's place: the classes, the Qing manual and the sisters' photographs (C, the pale tint with conf=1)"],
    ],
    "caption": {"frontage_m": lib["frontage_m"], "depth_m": lib["depth_m"], "eave_m": round(Y_TIP + PL, 2), "ridge_m": round(RIDGE - Y_C, 2), "assumed": True, "confidence": "C"},
    "hides": [],
    "tris": m.count(),
    "glb_bytes": n_bytes,
}
S.write(HERE, "YM46", aliases, P, "origin at the front middle of the library's box F0276 at its ground; x east along the front, y up, z south (scripts/model_site.py)", summary)
json.dump(REPORT, open(HERE / "report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"YM46: {m.count()} triangles, GLB {n_bytes / 1e6:.2f} MB; water {WATER_Y:.2f}, court {Y_C}, library floor {P_TOP:.2f}, ridge {RIDGE:.2f}; rocks {n_rocks}; "
      f"明间 plan {x_ming_plan:.2f} model {LX + X_MING:.2f}; 玲峰 in pool {REPORT['lingfeng']['in_pool']}")
