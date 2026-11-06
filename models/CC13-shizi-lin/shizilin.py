#!/usr/bin/env python3
"""狮子林 Shizi Lin (CC13), the rockery garden of 长春园 copied in 1772 from the Suzhou garden and 倪瓒's scroll: the sixteenth detailed model (Round 29).

  uv run python models/CC13-shizi-lin/shizilin.py      (after scripts/ground1860.py and scripts/boxes1860.py)

The garden as S01 draws its walls, halls, pool and rocks, and Qianlong's sixteen poems of 1772-75 name and describe its parts (S05 j83:13b-17a, E0203, E0218; the
yearly poems in S361, E0225-E0266): the west garden with 清閟阁 Qingbi Ge on the pool 曲池 (臨曲池面假山), the rockery 假山 piled by Suzhou craftsmen (吳下髙手堆塑)
round 纳景堂 Najing Tang, the winding stone bridge under its wisteria frame 藤架 (石橋既曲折，藤架復邐迤, about 十數武), the rainbow bridge 虹桥 over the pool's west
arm (跨水為小橋 ... 其下可舟通; 卧波上者形如半，印水觀來體忽圓), the climbing gallery 云廊 up to 探真书屋 Tanzhen Shuwu (雲廊拾級上), the one-bay tower 小香幢
Xiao Xiangchuang with its shrine above (一間樓 ... 上為佛室), the water gate 水门 where the channel leaves through the wall for the lake (跨水為牆下置門; 跨波門徑上騎牆);
and, east of the court of 清淑斋 Qingshu Zhai, the east garden with the stream 溪 and 横碧轩 Hengbi Xuan on it (文軒築溪上; 有橋如弓彎 ... 過橋坐敞軒), the rock
peak with the four-column pavilion 占峰亭 Zhanfeng Ting (峰頂 ... 四柱小亭翼然據), 延景楼 Yanjing Lou (詭石玲瓏棧徑通) and the stone room 云林石室 Yunlin Shishi
(三間十笏). No picture of the garden standing is known; the restored 虹桥 and 水门 on their sites (P0415, P0416, P0500, P0417, 2013-22) test the two arches.

Method (docs/METHOD.md, 'a compound from the kit and its evidence', Rounds 17-28; 'a rock garden', Round 25): the hall kit (scripts/hall_parts.py) for the halls; the rock
masses as irregular blocks on S01's outlines (文源阁's `rock_mass`, Round 25); the layout re-read on S01 (plan_readings.csv, plan pixels, placed by the fit in use);
the pool and the stream are Round 29's water W0368 and W0369 (research/plan/water_manual.json RM004, RM005).
Writes, beside this file: model.glb, params.json, keypoints.json, joints.json, summary.json, report.json (models/README.md).
Frame (scripts/model_site.py): origin at the front middle of 清閟阁's box F0357, at that box's ground; x east along the front, y up, z south.
Grades: what a source states for this object is `doc`; what is carried in from the classes or guessed (every height, the halls' forms, the identifications of the
unnamed halls, the rocks' shapes) is `fill` (assumed, C).
"""

import csv
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from georef import plan_to_wgs84  # noqa: E402
from hall_parts import JU, HallKit  # noqa: E402
from model_mesh import Mesh  # noqa: E402
from model_site import Site  # noqa: E402
from scene1860 import DATUM_M, to_xz  # noqa: E402
from shapely.geometry import LineString, Point, Polygon, box as sbox, shape  # noqa: E402
from shapely.ops import unary_union  # noqa: E402
from shapely.prepared import prep  # noqa: E402

# ------------------------------------------------------------ the figures (heights all C, in one place)
QB_BAYS = [4.32, 4.48, 4.64, 4.96, 4.64, 4.48, 4.32]   # 清閟阁, west to east: S01's seven cells (about 31.8 m between the end columns; their spacing regularised, C)
QB_DEPTHS = [1.60, 5.12, 1.60]                       # its front porch, the rooms, the back gallery: S01's rows (1.9, 4.9, 2.0 m as drawn), C
QB_PL, QB_MID, QB_EAVE, QB_RIDGE = 0.50, 3.70, 7.10, 9.60   # its platform; the upper floor, the eave and the ridge above its ground (a two-storey 阁, C)
HQ_SPAN, HQ_STILT, HQ_RING, HQ_W = 1.60, 1.10, 0.28, 2.40  # 虹桥: the opening, the jambs above the water, the ring's depth (a sweep on P0415, README), the width (S01)
if os.environ.get("CC13_HQ"):  # a sweep for the test on P0415 only, never in a run of step 6: "span,stilt,ring,width"
    HQ_SPAN, HQ_STILT, HQ_RING, HQ_W = map(float, os.environ["CC13_HQ"].split(","))
SM_SPAN, SM_RING, SM_THICK = 3.00, 0.48, 1.40        # 水门: the opening (the channel 3.4 m), the ring, the wall over it (P0416's proportions; its thickness C)
if os.environ.get("CC13_SM"):  # a sweep for the test on P0416 only, never in a run of step 6: "span,ring"
    SM_SPAN, SM_RING = map(float, os.environ["CC13_SM"].split(","))
WALL_H = 3.00      # the garden's walls above the ground, C
TJ_DECK, TJ_W = 0.45, 1.60   # 藤架's stone bridge: its deck above the water and its width, C
TJ_FRAME = 2.60    # the wisteria frame's beams above the deck, C
ZF_Y = 4.80        # 占峰亭's floor above the ground at the east peak (the peak's height), C
ZF_HS = 1.60       # its half side (four columns 2.6 m apart), C
PEAK_W = 5.20      # the west rockery's summit above the ground, C
TZ_Y = 1.80        # the 探真书屋 court's rock terrace above the gallery's foot (雲廊拾級上), C

P = {
    "layout": ("the garden's walls, 清閟阁's range, the pool and its arm and channel, the rockeries, the halls, the court of 清淑斋 and the east garden as S01 draws them", "S01", "B",
               "S01 re-read in Round 29 on 3x, 4x and 5x crops (plan_readings.csv): every line in plan pixels; S01 is B until Q2; its scale here about 0.24 m a pixel"),
    "names": ("the sixteen scenes in the order of 日下旧闻考: 虹桥, 假山, 纳景堂, 清閟阁, 藤架, 磴道, 占峰亭, 清淑斋, 小香幢, 探真书屋, 延景楼, 云林石室, 横碧轩, 水门", "S05;S361", "A",
              "S05 j83:13b (E0220); the two sets of eight poems with prefaces, 1772 (E0203, E0218); S01 labels 清閟阁, 探真书屋, 小香幢 and the half-round of the water gate; which unnamed hall on S01 is which scene is our reading (C): N01 纳景堂, N02 清淑斋, N03 横碧轩, N04 延景楼, the small three-cell house 云林石室"),
    "pool": ("the pool 曲池 before 清閟阁 with its west arm and the rock-lined channel along the south wall to the water gate: Round 29's water W0368, at the lake's level", "S01;S05", "B",
             "S01's wash before the range (the label 清閟阁 on it) (B); the 1772 preface: 臨曲池面假山 (E0203, A); the channel's course along the south wall a reading (C): research/plan/water_manual.json RM004"),
    "qingbi": ("清閟阁: seven bays, two storeys, a front porch on the pool, a gallery behind, a rolled 歇山 roof in grey tile", "S01;S05;S361", "B",
               "S01's seven cells and rows (B); 閣 (S05: a storeyed building, A); Qianlong's copy of 倪瓒's scroll kept in it (E0223, B); the 1772 preface: 清閟小閣置近臨活水 (E0203); bays regularised, every height C"),
    "rockery": ("the rockery 假山 round 纳景堂: rock masses on S01's outline, highest north-east of the hall, rock banks on the water, a stair 磴道 to the summit, two caves", "S01;S05", "B",
                "S01 draws the outline with rock strokes (B); 獅林以石勝 ... 兹令吳下髙手堆塑小景 (E0203, A); 房山石似洞庭 (Fangshan stone like Taihu's, E0240, A); 循巖陟磴 (E0240); every rock's form and height C; the caves after the Suzhou garden (T073: a comparable, C)"),
    "najing": ("纳景堂: three bays in the rockery with a porch, a paved terrace before it", "S01;S05", "C", "S01's hall of four cells (13.2 x 6.6 m) and the plain rectangle south of it (B for the place); the name ours (C); bays, form and heights C"),
    "hongqiao": (f"虹桥: a single stone arch over the pool's west arm, a half circle {HQ_SPAN} m across on jambs {HQ_STILT} m above the water, its ring {HQ_RING} m, a beast's head on the keystone, steps down at both ends", "S05;S01;S361", "A",
                 "the poems: 跨水為小橋 ... 其下可舟通 (E0203), 卧波上者形如半，印水觀來體忽圓 (a half circle on the water, E0227) (A); S01's two lines across the arm (B); the restored bridge on its site (P0415, 2013) for the ring, the keystone head and the steps (B); its span and heights from P0415's proportions (C)"),
    "tengjia": (f"藤架: a winding stone bridge of three turns across the pool on the 明间's line, {TJ_W} m wide, under a timber frame of wisteria", "S05", "A",
                "E0203: 紫藤引架垂隂縵縈可十數武於石橋宛轉 ... 石橋既曲折，藤架復邐迤 (A); E0237: 石橋上置藤蘿架 (A); its place and course C (S01 does not draw it)"),
    "yunlang": ("云廊: the climbing gallery from the range's back up to the 探真书屋 court, its floor stepping up", "S01;S05", "B", "S01's narrow double line stepping down from the court (B); E0252: 雲廊拾級上，書屋號探真 (A); its width and steps C"),
    "tanzhen": (f"探真书屋: two bays in its court, the court on a rock terrace {TZ_Y} m above the gallery's foot", "S01;S05", "B", "S01's two cells and court (B); 拾級上 (E0252, A); the terrace's height and the house's form C"),
    "xiangchuang": ("小香幢: a one-bay tower of two storeys at the north end of the strip, the shrine above, a covered way to the range", "S05;S01", "B",
                    "E0218: 一間樓湧小香幢 (A); E0249: 石磴玲瓏倚翠幢，上為佛室 (A); S01's label on the hill, the strip and its north cell (B); the identification and form C"),
    "watergate": (f"水门: a stone arch {SM_SPAN} m across through the east wall where the channel leaves for the lake, the wall {SM_THICK} m thick over it with a walk on its top; the poem's slab", "S05;S01;S361", "A",
                  "E0265: 跨水為牆下置門 (A); E0266: 跨波門徑上騎牆，歷歷人行來往航 (A); S01's half-round at the south-east corner (B); the restored ring on its site (P0416, P0500, P0417) for its form (B); the slab with the 1772 poem (P0442, A: its place on the gate C)"),
    "qingshu": ("清淑斋: three bays in the court between the rockeries, its walls", "S01;S05", "C", "S01's court and inner rectangle (B); E0246: 就樹得佳隂 ... 溪聲清以沉 (A); the identification and form C"),
    "hengbi": ("横碧轩: an open hall 敞轩 of three bays on the stream, a bow-shaped bridge over the stream before it", "S05;S01", "B",
               "E0261: 文軒築溪上，溪水如帶横 (A); E0262: 有橋如弓彎 ... 過橋坐敞軒 (A); S01's hall of four cells by the stream (B); the identification, bays and form C"),
    "zhanfeng": (f"占峰亭: a square pavilion on four columns on the east garden's peak, {ZF_Y} m above the ground, a stone stair 磴道 up", "S05;S01", "A",
                 "E0243: 峰頂一笠 ... 歷艱陟頂得稍平，四柱小亭翼然據 (A); S01's mountain sign in the east garden (B for the place of a peak); the peak's height and the roof C"),
    "yanjing": ("延景楼: three bays, two storeys, against the east garden's north wall, a rock stair up its side", "S05;S01", "C", "E0255: 詭石玲瓏棧徑通 ... 拾級望遙 (A); S01's three cells (B); the identification and form C"),
    "yunlin": ("云林石室: a three-bay stone room among the rocks of the east garden", "S05;S01", "C", "E0258: 石作夏雲石作林，其中有室 ... 三間十笏惟容膝 (A); S01's three small cells (B); the identification and form C"),
    "stream": ("the stream 溪 of the east garden with the small pond at its end: Round 29's water W0369", "S01;S05", "B", "S01's narrow double line (B); E0261, E0262, E0246 (A); its width 1.8 m C"),
    "walls": (f"the garden's walls, white with a grey tiled coping, {WALL_H} m", "S01", "B", "S01's lines (B); white walls with grey tile after the Suzhou garden (T073, comparable: C); height C"),
}
V = {k: v[0] for k, v in P.items()}

COL = {
    "lacquer": "#8c3a2b", "lacquer_dark": "#5a2a20", "wall": "#e6e1d6", "plaster": "#ece7dc", "glass_lattice": "#2b3137", "sill": "#8d8a84",
    "band": "#2e6a6c", "bracket": "#3b7b70", "bandred": "#7d2c20", "platform": "#b4ad9e", "coping": "#d0cabc", "step": "#d6d1c4", "marble": "#e2ded3",
    "underside": "#4b453d", "fascia": "#2c3a33", "wallred": "#9b3d2c", "pave": "#bdb6a6", "gold": "#c9a245", "plaque": "#20406a", "timber": "#6e5236",
    "stele": "#dcd8ce", "inscr": "#8c877b", "arch": "#cfcabd", "arch2": "#c2bcae", "beast": "#b7b1a2",
    "rock": "#8f8d86", "rock2": "#a29e94", "rock_face": "#7b786f", "rock_dark": "#6c6a64", "water": "#56747b",
    "leaf": "#56783a", "leaf2": "#6a8c45", "wisteria": "#8a6db5",
    "tile_grey": "#5f6469", "ridge_grey": "#4a4e52",
}

S = Site("F0357")
m = Mesh(COL)
S.m = m
S.ROCKERIES = ["CC13"]
REPORT = {"halls": {}, "deck_joints": [], "rocks": {}}


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


# ------------------------------------------------------------ the water: Round 29's bodies W0368 (the pool, the lake's level) and W0369 (the stream)
def water_body(wid):
    with open(ROOT / "research/terrain/water_levels.csv", encoding="utf-8") as fh:
        lv = [r for r in csv.DictReader(fh) if wid in r["water_ids"].split(";")]
    y = round(float(lv[0]["level_m_egm2008"]) - DATUM_M - S.pos[1], 3)
    f = [f for f in json.load(open(ROOT / "research/layers/water_1860.geojson", encoding="utf-8"))["features"] if f["properties"].get("id") == wid][0]
    g = shape(f["geometry"])
    g = max(g.geoms, key=lambda q: q.area) if g.geom_type != "Polygon" else g
    return y, Polygon([S.to_local(*to_xz(lo, la)) for lo, la in g.exterior.coords[:-1]]).buffer(0), float(lv[0]["level_m_egm2008"])


WATER_Y, POOL, WATER_M = water_body("W0368")
STREAM_Y, STREAM, _ = water_body("W0369")
WATER_U = unary_union([POOL, STREAM])
REPORT.update({"water_y": WATER_Y, "water_m": WATER_M, "stream_y": STREAM_Y, "pool_m2": round(POOL.area, 1), "stream_m2": round(STREAM.area, 1)})

# the ways of Round 9 in the frame: the rocks keep off them
WAYS = []
for f in json.load(open(ROOT / "research/layers/paths_1860.geojson", encoding="utf-8"))["features"]:
    gg = shape(f["geometry"])
    if gg.geom_type != "LineString":
        continue
    loc = [S.to_local(*to_xz(lo, la)) for lo, la in gg.coords]
    if min(abs(x - 30) for x, z in loc) > 90 or min(abs(z - 10) for x, z in loc) > 80:
        continue
    WAYS.append(LineString(loc).buffer((f["properties"].get("width_m") or 1.5) / 2 + 0.4))
WAY_U = unary_union(WAYS) if WAYS else Polygon()

# ------------------------------------------------------------ decks: raised floors the model draws (terraces, platforms, bridges)
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


def rot_to(dx, dz):
    """The push angle that turns the local +z towards (dx, dz)."""
    return math.atan2(dx, dz)


def along_rot(dx, dz):
    """The push angle that turns the local +x along (dx, dz)."""
    return math.atan2(-dz, dx)


# ============================================================ helpers (文源阁's, Round 25)
def flight(name, x, z, rot, width, ytop, ybot, entry=True, cheeks=True, mat="step"):
    """A flight 踏跺 from (x, z) at ytop going out along rot (0: +z) down to ybot, steps of about 0.15 x 0.30 m, the side slabs. Returns the foot (x, y, z)."""
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
        for l0, l1 in ((-w - 0.3, -w), (w, w + 0.3)):
            m.poly([(l0, ytop, 0), (l1, ytop, 0), (l1, ybot + 0.05, run), (l0, ybot + 0.05, run)], mat)
            for lat in (l0, l1):
                m.poly([(lat, ytop, 0), (lat, ybot + 0.05, run), (lat, low, run), (lat, low, 0)], mat)
            m.poly([(l0, ybot + 0.05, run), (l1, ybot + 0.05, run), (l1, low, run), (l0, low, run)], mat)
    foot = m.world((0, ybot, run + 0.2))
    top = m.world((0, ytop, -0.2))
    m.pop()
    S.FOOTPRINTS.append([(float(p[0]), float(p[2])) for p in [_w(x, z, rot, a, b) for a, b in ((-w - 0.3, 0), (w + 0.3, 0), (w + 0.3, run), (-w - 0.3, run))]])
    if entry:
        S.entry(f"{name}_foot", float(foot[0]), float(foot[2]), float(ybot))
        S.entry(f"{name}_top", float(top[0]), float(top[2]), float(ytop))
    return foot


def rock_steps(name, path, y0, y1, width=1.3, seed=0, entry=True):
    """A stair of rough stone 磴道 along a polyline from y0 to y1: blocks stepping up, rocks either side. Returns nothing; its ends are entries."""
    rng = np.random.default_rng(seed)
    ls = LineString(path)
    L = ls.length
    n = max(2, int(round(abs(y1 - y0) / 0.18)))
    for k in range(n):
        t0, t1 = k / n, (k + 1) / n
        a, b = ls.interpolate(t0 * L), ls.interpolate(t1 * L)
        dx, dz = b.x - a.x, b.y - a.y
        Ls = max(math.hypot(dx, dz), 0.2)
        r = along_rot(dx / Ls, dz / Ls)
        yy = y0 + (y1 - y0) * (k + 1) / n
        m.push((a.x + b.x) / 2, 0, (a.y + b.y) / 2, r)
        low = min(bed(*m.world((u, 0, v))[::2]) for u in (-Ls / 2, Ls / 2) for v in (-width / 2, width / 2)) - 0.2
        m.box(-Ls / 2 - 0.05, Ls / 2 + 0.05, low, yy, -width / 2 + rng.uniform(-0.08, 0.08), width / 2 + rng.uniform(-0.08, 0.08), "rock2" if k % 2 else "rock", skip=("bottom",))
        m.pop()
        if k % 2 == 0:
            for sg in (-1, 1):
                q = ls.interpolate((t0 + t1) / 2 * L)
                nx, nz = -dz / Ls, dx / Ls
                lump(q.x + sg * nx * (width / 2 + 0.45), q.y + sg * nz * (width / 2 + 0.45), rng.uniform(0.35, 0.55), bed(q.x, q.y) - 0.2, yy + rng.uniform(0.2, 0.7), rng, "rock")
    S.FOOTPRINTS.append([(float(a), float(b)) for a, b in ls.buffer(width / 2 + 0.3, cap_style="flat").exterior.coords[:-1]])
    if entry:
        S.entry(f"{name}_foot", path[0][0], path[0][1], y0)
        S.entry(f"{name}_top", path[-1][0], path[-1][1], y1)


def wall_run(pts_, h, name, gaps=(), thick=0.6, body="wall", cap="grey", base_h=0.4, ytop=None):
    """A wall along pts_, broken where a gap (x, z, half width) lies on it; its feet are joints, its outline a footprint."""
    runs = []
    for (ax, az), (bx, bz) in zip(pts_[:-1], pts_[1:]):
        L = math.hypot(bx - ax, bz - az)
        if L < 0.05:
            continue
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


def door_in_wall(x, z, rot, name, w=1.6, h=2.6, thick=0.6, y0=None, moon=False):
    """A doorway 洞门 in a garden wall (C): its jambs and head in grey stone, the wall's coping carried over it on a small roof; entries both sides."""
    m.push(x, 0, z, rot)
    g = max(K.gy_local(a, b) for a in (-w / 2, w / 2) for b in (-thick, thick)) if y0 is None else y0
    lo = min(bed(*m.world((a, 0, b))[::2]) for a in (-w / 2 - 0.4, w / 2 + 0.4) for b in (-thick, thick)) - 0.15
    for sg in (-1, 1):
        a0, a1 = (w / 2, w / 2 + 0.45) if sg > 0 else (-w / 2 - 0.45, -w / 2)
        m.box(a0, a1, lo, g + h + 0.6, -thick / 2 - 0.02, thick / 2 + 0.02, "wall")
        m.box(sg * w / 2 - 0.12 if sg > 0 else -w / 2, sg * w / 2 if sg > 0 else -w / 2 + 0.12, g, g + h, -thick / 2 - 0.05, thick / 2 + 0.05, "coping")
    m.box(-w / 2 - 0.45, w / 2 + 0.45, g + h, g + h + 0.6, -thick / 2 - 0.02, thick / 2 + 0.02, "wall")
    m.box(-w / 2, w / 2, g + h - 0.12, g + h, -thick / 2 - 0.05, thick / 2 + 0.05, "coping")
    m.box(-w / 2, w / 2, lo, g + 0.08, -thick / 2 - 0.1, thick / 2 + 0.1, "step")
    K.roof(lambda a, b, c: (a, b, c), w / 2 + 0.7, thick / 2 + 0.45, g + h + 0.55, g + h + 1.15, form="xu", rolled=True, ju=JU["gallery"], gable_mat="plaster", gableX=w / 2 + 0.7, tile="grey")
    for sg, tag in ((1, "in"), (-1, "out")):
        p_ = m.world((0, 0, sg * 1.0))
        S.entry(f"{name}_{tag}", float(p_[0]), float(p_[2]), float(g))
    m.pop()


def column(x, q, y0, y1, dia, mat="lacquer"):
    r = dia / 2
    m.prism([(x + r * math.cos(2 * math.pi * (k + 0.5) / 8), q + r * math.sin(2 * math.pi * (k + 0.5) / 8)) for k in range(8)], y0, y1, mat, top=False)
    m.box(x - r - 0.08, x + r + 0.08, y0 - 0.02, y0 + 0.08, q - r - 0.08, q + r + 0.08, "coping")


def lump(x, z, r, y0, y1, rng, mat="rock", taper=(0.45, 0.85), k6=None):
    """One irregular rock (文源阁's): a ring round (x, z) at y0, a smaller shifted ring at uneven heights below y1, the top a fan to a peak."""
    k6 = k6 or int(rng.integers(6, 9))
    a0 = rng.uniform(0, 2 * math.pi)
    lo = [(x + r * rng.uniform(0.65, 1.25) * math.cos(a0 + 2 * math.pi * (i + rng.uniform(-0.2, 0.2)) / k6), z + r * rng.uniform(0.65, 1.25) * math.sin(a0 + 2 * math.pi * (i + rng.uniform(-0.2, 0.2)) / k6)) for i in range(k6)]
    sx, sz = rng.uniform(-0.25, 0.25) * r, rng.uniform(-0.25, 0.25) * r
    hi = [(x + sx + (px - x) * rng.uniform(*taper), z + sz + (pz - z) * rng.uniform(*taper)) for px, pz in lo]
    h = y1 - y0
    yh = [y1 - min(h * rng.uniform(0.04, 0.16), r * 0.35) for _ in hi]   # a shallow cap: stacked stones, not shards (Round 29)
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


def rock_mass(name, poly, h_lo, h_hi, seed, step=1.6, keep_off=None, mat="rock", peak=None, peak_h=None, peak_r=8.0, fp_inset=1.2):
    """A rock mass 叠石 over an outline (S01's), as irregular blocks on a jittered grid, higher towards the middle (or towards `peak`); kept off the ways, the water
    and `keep_off`. Piled blocks: a broad one below and a narrower one off-centre on it, a third on the tallest (the Suzhou manner of 叠石, C). Heights C.
    Its footprint is the outline drawn in by `fp_inset` m, so that the planting of Round 12 can stand at its edges among the rocks (the pines, E0218)."""
    rng = np.random.default_rng(seed)
    pg = Polygon(poly).buffer(0).difference(WATER_U.buffer(0.2))
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
            if peak is not None:
                dp = math.hypot(x - peak[0], z - peak[1])
                h = max(h, peak_h * max(0.0, 1 - dp / peak_r) ** 0.8 * rng.uniform(0.8, 1.0))
            r = step * rng.uniform(0.6, 0.85)
            g = bed(x, z)
            mt = mat if rng.uniform() < 0.6 else mat + "2"
            # stacked in tiers no taller than about their width, each set off the one below, the upper ones narrower: the Suzhou manner of 叠石 (C)
            y, rr, ox, oz, tier = g - 0.2, r * 1.1, 0.0, 0.0, 0
            while y < g + h - 0.08:
                th = min(g + h - y, rr * rng.uniform(0.8, 1.3))
                lump(x + ox, z + oz, rr, y, y + th + 0.1, rng, "rock_dark" if (tier >= 2 and rng.uniform() < 0.3) else mt, taper=(0.72, 0.98))
                y += th
                rr *= rng.uniform(0.7, 0.9)
                ox += rng.uniform(-0.3, 0.3) * rr
                oz += rng.uniform(-0.3, 0.3) * rr
                tier += 1
            n += 1
    core = pg.buffer(-fp_inset)
    for gg in ([core] if core.geom_type == "Polygon" else [q for q in getattr(core, "geoms", []) if q.area > 1.0]):
        if gg.is_empty or gg.area < 1.0:
            continue
        S.FOOTPRINTS.append([(float(a), float(b)) for a, b in gg.exterior.coords[:-1]])
        ROCK_FP.append(gg)
    REPORT["rocks"][name] = {"blocks": n, "area_m2": round(pg.area, 1), "h_m": [h_lo, h_hi] + ([peak_h] if peak_h else [])}
    return n


def rock_bank(poly, y_water, seed, every=1.0, skip=None, top_up=(0.0, 0.5), mat="rock"):
    """Rocks along a shore 驳岸 (the Suzhou manner: piled stone, not a dressed face; C): blocks from below the water up to just above the bank."""
    rng = np.random.default_rng(seed)
    ring = poly.exterior
    n = int(ring.length / every)
    k = 0
    for i in range(n):
        p_ = ring.interpolate(i * ring.length / n)
        if skip is not None and skip.contains(p_):
            continue
        top = max(S.gy(p_.x + 0.6, p_.y), y_water + 0.3)
        lump(p_.x, p_.y, rng.uniform(0.5, 0.85), y_water - 0.7, top + rng.uniform(*top_up), rng, mat if i % 3 else mat + "2", taper=(0.6, 0.9))
        k += 1
    return k


# ============================================================ arches: 虹桥 and 水门 (their proportions from the restored arches on their sites, P0415 and P0416)
def arch_faces(u0, u1, y_bed, y_top_fn, R, y_s, t_ring, w, ring_mat="arch", body="arch2", keystone=False, deck_mat=None):
    """The two faces and the barrel of a stilted semicircular arch in the current frame (u along x, the faces at z = +-w/2), opening centred on u = 0 with radius R,
    springing at y_s; the jambs straight from the bed to the springing; the face from the arch's extrados and the jambs up to y_top_fn(u). The ring proud by 3 cm."""
    N = 14
    for sg in (-1, 1):
        zf = sg * w / 2
        # the spandrels over the arch: quads from the intrados to the top
        for i in range(N):
            a0, a1 = math.pi * i / N, math.pi * (i + 1) / N
            p0 = (R * math.cos(a0), y_s + R * math.sin(a0))
            p1 = (R * math.cos(a1), y_s + R * math.sin(a1))
            m.poly([(p0[0], p0[1], zf), (p1[0], p1[1], zf), (p1[0], y_top_fn(p1[0]), zf), (p0[0], y_top_fn(p0[0]), zf)], body)
            # the ring 拱券: voussoirs proud of the face, two tones so the joints read
            q0 = ((R + t_ring) * math.cos(a0), y_s + (R + t_ring) * math.sin(a0))
            q1 = ((R + t_ring) * math.cos(a1), y_s + (R + t_ring) * math.sin(a1))
            zr = zf + sg * 0.03
            m.poly([(p0[0], p0[1], zr), (p1[0], p1[1], zr), (q1[0], q1[1], zr), (q0[0], q0[1], zr)], ring_mat if i % 2 else body)
            # the barrel's soffit
            m.poly([(p0[0], p0[1], -w / 2), (p1[0], p1[1], -w / 2), (p1[0], p1[1], w / 2), (p0[0], p0[1], w / 2)], body)
        # the jambs below the springing and the abutments out to the ends
        for s_, ue in ((-1, u0), (1, u1)):
            m.poly([(s_ * R, y_bed, zf), (ue, y_bed, zf), (ue, y_top_fn(ue), zf), (s_ * R, y_s, zf)], body)
            m.poly([(s_ * R, y_s, zf), (ue, y_top_fn(ue), zf), (s_ * R, y_top_fn(s_ * R), zf)], body)
            m.poly([(s_ * (R + t_ring), y_s, zf + sg * 0.03), (s_ * R, y_s, zf + sg * 0.03), (s_ * R, y_bed, zf + sg * 0.03), (s_ * (R + t_ring), y_bed, zf + sg * 0.03)], ring_mat)
        if keystone:  # the beast's head 吸水兽 on the keystone (P0415)
            yk = y_s + R + t_ring * 0.4
            m.box(-0.17, 0.17, yk - 0.2, yk + 0.18, zf, zf + sg * 0.28, "beast")
            m.box(-0.12, 0.12, yk - 0.32, yk - 0.18, zf + sg * 0.1, zf + sg * 0.3, "beast")
    for s_ in (-1, 1):  # the jambs' inner faces
        m.poly([(s_ * R, y_bed, -w / 2), (s_ * R, y_s, -w / 2), (s_ * R, y_s, w / 2), (s_ * R, y_bed, w / 2)], body)


def hongqiao():
    """虹桥: the stone arch over the west arm, its deck humped over the crown and stepping down to the banks (P0415), on S01's line from the west wall to the rockery."""
    (ax, az), (bx, bz) = pts("hongqiao")[0], pts("hongqiao")[1]
    (cx_, cz_), (dx_, dz_) = pts("hongqiao")[3], pts("hongqiao")[2]
    p0 = ((ax + cx_) / 2, (az + cz_) / 2)   # the west end (on the west wall's line)
    p1 = ((bx + dx_) / 2, (bz + dz_) / 2)   # the east end (on the rockery)
    dx, dz = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dz)
    ux, uz = dx / L, dz / L
    # the arch over the arm's middle: the water's crossing along the line
    cross = LineString([(p0[0] - ux * 4, p0[1] - uz * 4), (p1[0] + ux * 4, p1[1] + uz * 4)]).intersection(POOL)
    seg = max(getattr(cross, "geoms", [cross]), key=lambda g: g.length)
    (wa, wb) = seg.coords[0], seg.coords[-1]
    c = ((wa[0] + wb[0]) / 2, (wa[1] + wb[1]) / 2)
    R = HQ_SPAN / 2
    y_s = WATER_Y + HQ_STILT
    y_crown = y_s + R + HQ_RING + 0.14                 # the deck over the crown
    gW = max(S.gy(c[0] - ux * (L / 2 + 2.5), c[1] - uz * (L / 2 + 2.5)), WATER_Y + 0.4)   # the banks beyond the ends
    gE = max(S.gy(c[0] + ux * (L / 2 + 2.5), c[1] + uz * (L / 2 + 2.5)), WATER_Y + 0.4)
    nW, nE = max(1, round((y_crown - gW) / 0.16)), max(1, round((y_crown - gE) / 0.16))
    flat = R + HQ_RING + 0.25                         # the deck runs level over the whole arch (P0415), the steps beyond it
    uW, uE = -(flat + nW * 0.34), flat + nE * 0.34   # the ends of the steps

    def top(u):
        if -flat <= u <= flat:
            return y_crown
        if u < -flat:
            k = min(nW, math.ceil((-flat - u) / 0.34))
            return y_crown - k * (y_crown - gW) / nW
        k = min(nE, math.ceil((u - flat) / 0.34))
        return y_crown - k * (y_crown - gE) / nE

    r = along_rot(ux, uz)
    m.push(c[0], 0, c[1], r)
    y_bed = min(bed(*m.world((u, 0, v))[::2]) for u in np.linspace(uW, uE, 9) for v in (-HQ_W / 2, HQ_W / 2)) - 0.2
    # the faces: a smooth top over the arch for the spandrels, the steps drawn as blocks over them
    smooth = lambda u: min(y_crown, top(u)) - 0.12
    arch_faces(uW, uE, y_bed, smooth, R, y_s, HQ_RING, HQ_W, keystone=True)
    # the deck: the crown's slab and the steps, each a block the bridge's width
    m.box(-flat, flat, y_crown - 0.16, y_crown, -HQ_W / 2 - 0.06, HQ_W / 2 + 0.06, "arch", skip=("bottom",))
    for k in range(nW):
        ua, ub = -flat - (k + 1) * 0.34, -flat - k * 0.34
        m.box(ua, ub, max(y_bed, top(ua) - 0.6), top(ub - 0.01), -HQ_W / 2 - 0.04, HQ_W / 2 + 0.04, "step", skip=("bottom",))
    for k in range(nE):
        ua, ub = flat + k * 0.34, flat + (k + 1) * 0.34
        m.box(ua, ub, max(y_bed, top(ub) - 0.6), top(ua + 0.01), -HQ_W / 2 - 0.04, HQ_W / 2 + 0.04, "step", skip=("bottom",))
    # key points for P0415: the springings and the jambs' feet at the water, the intrados and extrados crowns, the deck's crown edge, the step ends
    for sg, tag in ((-1, "W"), (1, "E")):
        for zs, side in ((HQ_W / 2, "S"), (-HQ_W / 2, "N")):
            S.kp(f"hq_spring_{tag}_{side}", m.world((sg * R, y_s, zs)))
            S.kp(f"hq_ring_foot_{tag}_{side}", m.world((sg * (R + HQ_RING), WATER_Y, zs)))
            S.kp(f"hq_jamb_water_{tag}_{side}", m.world((sg * R, WATER_Y, zs)))
            S.kp(f"hq_deck_end_{tag}_{side}", m.world(((uW if sg < 0 else uE), top(uW if sg < 0 else uE), zs)))
            S.kp(f"hq_crown_edge_{tag}_{side}", m.world((sg * flat, y_crown, zs)))
    for zs, side in ((HQ_W / 2, "S"), (-HQ_W / 2, "N")):
        S.kp(f"hq_intrados_{side}", m.world((0, y_s + R, zs)))
        S.kp(f"hq_extrados_{side}", m.world((0, y_s + R + HQ_RING, zs)))
        S.kp(f"hq_beast_{side}", m.world((0, y_s + R + HQ_RING * 0.4 - 0.05, zs + (0.28 if zs > 0 else -0.28))))
    endW = m.world((uW - 0.25, 0, 0))
    endE = m.world((uE + 0.25, 0, 0))
    corners = [m.world((u, 0, v)) for u, v in ((uW, -HQ_W / 2 - 0.1), (uE, -HQ_W / 2 - 0.1), (uE, HQ_W / 2 + 0.1), (uW, HQ_W / 2 + 0.1))]
    m.pop()
    S.FOOTPRINTS.append([(float(q[0]), float(q[2])) for q in corners])
    add_deck("hongqiao", [(float(q[0]), float(q[2])) for q in corners], y_crown)
    S.entry("hongqiao_W", float(endW[0]), float(endW[2]), float(gW))
    S.entry("hongqiao_E", float(endE[0]), float(endE[2]), float(gE))
    for nm, e_, g_ in (("hongqiao_W", endW, gW), ("hongqiao_E", endE, gE)):
        S.joint(f"{nm}_foot", float(e_[0]), float(e_[2]), "bridge end", y=float(g_) - 0.05)
    REPORT["halls"]["hongqiao"] = {"span_m": HQ_SPAN, "stilt_m": HQ_STILT, "ring_m": HQ_RING, "width_m": HQ_W, "crown_above_water_m": round(y_crown - WATER_Y, 2),
                                   "length_m": round(uE - uW, 2), "steps": [nW, nE], "banks_above_water_m": [round(gW - WATER_Y, 2), round(gE - WATER_Y, 2)],
                                   "plan_length_m": round(L, 2), "water_m": round(seg.length, 2), "x": round(c[0], 2), "z": round(c[1], 2)}
    return endW, (ux, uz), gW


SM_STAIR = []


def watergate():
    """水门: the arch through the east wall over the channel, the wall thick over it with a walk on its top and low parapets (門徑上騎牆), the slab with the poem."""
    (ix, iz), (ox, oz) = pts("watergate")[0], pts("watergate")[1]
    dx, dz = ox - ix, oz - iz
    L = math.hypot(dx, dz)
    ux, uz = dx / L, dz / L
    # the gate on the east wall's line: where the channel crosses it
    wx = float(np.mean([p[0] for p in pts("wall_E")]))
    t = (wx - ix) / ux if abs(ux) > 0.2 else L / 2
    c = (ix + ux * t, iz + uz * t)
    R = SM_SPAN / 2
    g_bank = max(S.gy(c[0] + uz * (R + 1.5), c[1] - ux * (R + 1.5)), S.gy(c[0] - uz * (R + 1.5), c[1] + ux * (R + 1.5)), WATER_Y + 0.4)
    y_s = g_bank - 0.10            # the springings on the banks' rock (P0416: the ring stands on the banks either side of the water)
    y_wall = y_s + R + SM_RING + 1.15   # the walk on the wall's top
    r = rot_to(ux, uz)             # local +z along the water (out of the garden); the arch's span along local x
    m.push(c[0], 0, c[1], r)
    hw = R + SM_RING + 1.6          # the gate's block along the wall
    y_bed = min(bed(*m.world((u, 0, v))[::2]) for u in (-hw, 0, hw) for v in (-SM_THICK / 2, SM_THICK / 2)) - 0.2
    m.cls = "doc"
    # the faces are along local x: build in a frame turned so that the arch's u is local x and the faces at z = +-thick/2
    arch_faces(-hw, hw, y_bed, lambda u: y_wall, R, y_s, SM_RING, SM_THICK, keystone=False)
    m.box(-hw, hw, y_wall - 0.12, y_wall, -SM_THICK / 2 - 0.04, SM_THICK / 2 + 0.04, "coping", skip=("bottom",))
    m.cls = "fill"
    for sg in (-1, 1):  # the walk's parapets, white with a grey cap (C)
        z0 = sg * SM_THICK / 2
        m.box(-hw, hw, y_wall, y_wall + 0.75, min(z0, z0 - sg * 0.24), max(z0, z0 - sg * 0.24), "wall")
        m.box(-hw - 0.02, hw + 0.02, y_wall + 0.75, y_wall + 0.85, min(z0, z0 - sg * 0.26) - 0.02, max(z0, z0 - sg * 0.26) + 0.02, "coping")
    m.cls = "doc"
    # the slab with the poem of 1772 over the arch on the garden's face (P0442: marble, running script; its place C)
    zf = -SM_THICK / 2 - 0.04
    m.box(-0.95, 0.95, y_s + R + SM_RING + 0.12, y_s + R + SM_RING + 0.92, zf - 0.04, zf, "marble")
    m.poly([(-0.8, y_s + R + SM_RING + 0.22, zf - 0.045), (0.8, y_s + R + SM_RING + 0.22, zf - 0.045), (0.8, y_s + R + SM_RING + 0.82, zf - 0.045), (-0.8, y_s + R + SM_RING + 0.82, zf - 0.045)], "inscr")
    for zs, side in ((-SM_THICK / 2, "in"), (SM_THICK / 2, "out")):
        for sg, tag in ((-1, "S"), (1, "N")):  # the gate's local +x points north
            S.kp(f"sm_spring_{tag}_{side}", m.world((sg * R, y_s, zs)))
            S.kp(f"sm_ring_foot_{tag}_{side}", m.world((sg * (R + SM_RING), y_s, zs)))
            S.kp(f"sm_ring_mid_{tag}_{side}", m.world((sg * (R + SM_RING) * math.cos(math.pi / 4), y_s + (R + SM_RING) * math.sin(math.pi / 4), zs)))
            S.kp(f"sm_intr_mid_{tag}_{side}", m.world((sg * R * math.cos(math.pi / 4), y_s + R * math.sin(math.pi / 4), zs)))
        S.kp(f"sm_intrados_{side}", m.world((0, y_s + R, zs)))
        S.kp(f"sm_extrados_{side}", m.world((0, y_s + R + SM_RING, zs)))
    corners = [m.world((u, 0, v)) for u, v in ((-hw, -SM_THICK / 2), (hw, -SM_THICK / 2), (hw, SM_THICK / 2), (-hw, SM_THICK / 2))]
    ends = [m.world((sg * hw, 0, 0)) for sg in (-1, 1)]
    m.pop()
    S.FOOTPRINTS.append([(float(q[0]), float(q[2])) for q in corners])
    for i, q in enumerate(corners):
        S.JOINTS.append([f"watergate_{i}", float(q[0]), float(bed(float(q[0]), float(q[2])) - 0.2), float(q[2]), "gate foot"])
    # the stair up to the walk from the garden: rough stone against the wall's inner face, north of the arch (門徑上騎牆: the walk is reached from the garden; its stair C)
    n_end = m.world((hw, 0, 0)) if False else None
    m.push(c[0], 0, c[1], r)
    top_w = m.world((hw - 0.6, 0, -SM_THICK / 2 + 0.3))
    foot_w = m.world((hw - 0.6, 0, -SM_THICK / 2 - (y_wall - g_bank) / 0.17 * 0.3 - 0.6))
    m.pop()
    m.cls = "fill"
    SM_STAIR[:] = [(float(foot_w[0]), float(foot_w[2])), (float(top_w[0]), float(top_w[2]))]
    rock_steps("sm_stair", SM_STAIR, S.gy(*SM_STAIR[0]), y_wall, width=1.2, seed=2970)
    m.cls = "doc"
    REPORT["halls"]["watergate"] = {"span_m": SM_SPAN, "ring_m": SM_RING, "thick_m": SM_THICK, "spring_above_water_m": round(y_s - WATER_Y, 2), "walk_above_water_m": round(y_wall - WATER_Y, 2),
                                    "x": round(c[0], 2), "z": round(c[1], 2)}
    return [(float(e[0]), float(e[2])) for e in ends], y_wall


# ============================================================ the open hall 敞轩 and the square pavilion
def open_hall(name, cx, cz, rot, bays, depth, pl, col, eave, ridge, rf="xs", rolled=True, bench=True, open_sides=("front", "back", "left", "right")):
    """An open hall 敞轩 (C): a platform, columns at the bays, a low seat rail 坐凳栏杆 between them, the beam band and its hanging fascia, the roof."""
    m.push(cx, 0, cz, rot)
    hf = sum(bays) / 2 + 0.6
    hd = depth / 2 + 0.6
    base = max(K.gy_local(a, b) for a in (-hf, hf) for b in (-hd, hd))
    foot = min(bed(*m.world((a, 0, b))[::2]) for a in (-hf, 0, hf) for b in (-hd, hd)) - 0.15
    plt = base + pl
    K.platform(hf, hd, plt, foot)
    cs, cq = sum(bays) / 2, depth / 2
    xs = [-cs]
    for b in bays:
        xs.append(xs[-1] + b)
    xs[-1] = cs
    for x in xs:
        for q in (-cq, cq):
            column(x, q, plt, plt + col, 0.26)
    for q in (-cq + depth / 3, cq - depth / 3) if depth > 5.5 else ():
        for x in (-cs, cs):
            column(x, q, plt, plt + col, 0.26)
    top = plt + col
    K.bands(cs, cq, top + 0.42, False, 0.26, top + 0.42)
    for (s0, q0, s1, q1) in ((-cs, cq, cs, cq), (-cs, -cq, cs, -cq), (-cs, -cq, -cs, cq), (cs, -cq, cs, cq)):
        Lr = math.hypot(s1 - s0, q1 - q0)
        if abs(q1 - q0) < 0.01:
            m.box(s0, s1, top - 0.45, top - 0.3, q0 - 0.03, q0 + 0.03, "lacquer")  # the hanging fascia 倒挂楣子
        else:
            m.box(s0 - 0.03, s0 + 0.03, top - 0.45, top - 0.3, q0, q1, "lacquer")
    if bench:
        for i in range(len(xs) - 1):
            mid_ = (xs[i] + xs[i + 1]) / 2
            for q in (-cq, cq):
                if q > 0 and abs(mid_) < bays[len(bays) // 2] / 2 + 0.01:
                    continue   # the middle bay of the front is the way in
                m.box(xs[i] + 0.15, xs[i + 1] - 0.15, plt, plt + 0.48, q - 0.16, q + 0.16, "lacquer")
        for x in (-cs, cs):
            m.box(x - 0.16, x + 0.16, plt, plt + 0.48, -cq + 0.15, cq - 0.15, "lacquer")
    m.poly([(-cs, top + 0.0, cq), (cs, top + 0.0, cq), (cs, top, -cq), (-cs, top, -cq)], "underside")
    o = 0.9
    K.roof_over(cs + o, cq + o, top + 0.42 - o * 0.5, base + ridge, rf, dict(rolled=rolled, ju=JU["small_house"], tile="grey", gable_mat="lacquer"), o)
    feet = {"front": K.flight("front", 0.0, hf, hd, plt, min(2.4, bays[len(bays) // 2]))}
    c0 = m.world((0, 0, 0))
    for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        w = m.world((sx * (cs + o), 0, sq * (cq + o)))
        S.kp(f"{name}_eave_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], top + 0.42 - o * 0.5, w[2]))
    corners = [m.world((sx * hf, 0, sq * hd)) for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    fw = {k: m.world(v) for k, v in feet.items() if v is not None}
    m.pop()
    poly = [(float(q[0]), float(q[2])) for q in corners]
    S.FOOTPRINTS.append(poly)
    add_deck(f"{name}_platform", poly, plt, register=False)
    for k, f in fw.items():
        S.entry(f"{name}_{k}", float(f[0]), float(f[2]), float(f[1]))
        S.joint(f"{name}_{k}_foot", float(f[0]), float(f[2]), "flight foot", y=float(f[1]) - 0.05)
    for i, q in enumerate(corners):
        S.JOINTS.append([f"{name}_pl_{i}", float(q[0]), float(bed(float(q[0]), float(q[2])) - 0.12), float(q[2]), "platform foot"])
    REPORT["halls"][name] = {"frontage_m": round(2 * cs, 2), "depth_m": round(2 * cq, 2), "column_m": col, "eave_m": round(col + 0.42 - o * 0.5 + pl, 2), "ridge_m": ridge, "floor_y": round(plt, 2)}
    return poly, plt


def square_pavilion(name, cx, cz, y_floor, hs, col=2.9, rise=1.9, tile="grey"):
    """A square pavilion on four columns 四柱亭 with a seat rail and a pyramid roof (E0243: 四柱小亭; the roof and sizes C)."""
    m.push(cx, 0, cz)
    cs = hs - 0.3
    K.platform(hs, hs, y_floor, y_floor - 0.6)
    for x in (-cs, cs):
        for q in (-cs, cs):
            column(x, q, y_floor, y_floor + col, 0.24)
    K.bands(cs, cs, y_floor + col + 0.38, False, 0.24, y_floor + col + 0.38)
    for sg in (1, -1):
        m.box(-cs + 0.14, cs - 0.14, y_floor + col - 0.4, y_floor + col - 0.28, sg * cs - 0.03, sg * cs + 0.03, "lacquer")
        m.box(sg * cs - 0.03, sg * cs + 0.03, y_floor + col - 0.4, y_floor + col - 0.28, -cs + 0.14, cs - 0.14, "lacquer")
        m.box(sg * cs - 0.13, sg * cs + 0.13, y_floor, y_floor + 0.46, -cs + 0.14, cs - 0.14, "lacquer")
    m.box(-cs + 0.14, cs - 0.14, y_floor, y_floor + 0.46, -cs - 0.13, -cs + 0.13, "lacquer")
    K.pyramid(cs + 0.8, cs + 0.8, y_floor + col + 0.38 - 0.4, y_floor + col + 0.38 + rise, tile=tile)
    for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        w = m.world((sx * (cs + 0.8), 0, sq * (cs + 0.8)))
        S.kp(f"{name}_eave_{compass(sx, sq)}", (w[0], y_floor + col - 0.02, w[2]))
        w = m.world((sx * cs, 0, sq * cs))
        S.kp(f"{name}_col_{compass(sx, sq)}_foot", (w[0], y_floor, w[2]))
    S.kp(f"{name}_finial", m.world((0, y_floor + col + 0.38 + rise + 0.6, 0)))
    m.pop()
    return [(cx - hs, cz - hs), (cx + hs, cz - hs), (cx + hs, cz + hs), (cx - hs, cz + hs)]


def kit_hall(name, cx, cz, rot, bays, depths, pl, eave, ridge, rf="xs", rl=1, pf=0.0, pb=0.0, mid=None, dr=None, st=None, k="hall", rr="w", side_wall=False, fw=None, base=None):
    """A hall by the kit (HallKit.hall) at (cx, cz) facing rot; returns its platform polygon and floor; its flights are entries."""
    hf = sum(bays) / 2 + 0.75
    hd = sum(depths) / 2 + 0.75
    m.push(cx, 0, cz, rot)
    b0 = max(K.gy_local(a, b) for a in (-hf, hf) for b in (-hd, hd)) if base is None else base
    foot = min(bed(*m.world((a, 0, b))[::2]) for a in (-hf, 0, hf) for b in (-hd, 0, hd)) - 0.15
    nb = len(bays)
    H = dict(hf=hf, hd=hd, base=b0, foot=foot, pl=pl, eave=eave, ridge=ridge, e=0.75, o=0.95, b=bays, d=depths, pf=pf, pb=pb, ps=0.0, dia=0.30,
             st=st if st is not None else {"front": [0.0]}, fw=fw or {}, bal=0, rf=rf, rl=rl, db=0, ju=JU["small_house"], t="grey", te=None, bd="bm",
             dr=dr if dr is not None else [nb // 2], rr=rr, k=k, side_wall=side_wall)
    if mid:
        H["mid"] = mid
        H["ju"] = JU["storeyed_hall"]
    feet = K.hall(H)
    c0 = m.world((0, 0, 0))
    o = H["o"]
    cs, cq = hf - H["e"], hd - H["e"]
    for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        w = m.world((sx * (cs + o), 0, sq * (cq + o)))
        S.kp(f"{name}_eave_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], b0 + eave - o * 0.5, w[2]))
        w = m.world((sx * hf, 0, sq * hd))
        S.kp(f"{name}_pl_top_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], b0 + pl, w[2]))
    corners = [m.world((sx * hf, 0, sq * hd)) for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    fwd = {kk: m.world(v) for kk, v in feet.items()}
    m.pop()
    poly = [(float(q[0]), float(q[2])) for q in corners]
    S.FOOTPRINTS.append(poly)
    add_deck(f"{name}_platform", poly, b0 + pl, register=False)
    for kk, f in fwd.items():
        S.entry(f"{name}_{kk}", float(f[0]), float(f[2]), float(f[1]))
        if not any(pp.covers(Point(float(f[0]), float(f[2]))) for _, _, _, pp in DECKS[:-1]):
            S.joint(f"{name}_{kk}_foot", float(f[0]), float(f[2]), "flight foot", y=float(f[1]) - 0.05)
    for i, q in enumerate(corners):  # each corner on its own ground (the bed where it stands in the water)
        S.JOINTS.append([f"{name}_pl_{i}", float(q[0]), float(bed(float(q[0]), float(q[2])) - 0.12), float(q[2]), "platform foot"])
    REPORT["halls"][name] = {"frontage_m": round(sum(bays), 2), "depth_m": round(sum(depths), 2), "bays": bays, "platform_m": pl, "eave_m": eave, "ridge_m": ridge,
                             "storeys": 2 if mid else 1, "floor_y": round(b0 + pl, 2), "x": round(cx, 2), "z": round(cz, 2)}
    return poly, b0 + pl, b0


# ============================================================ the walls of the west garden, the court of 清淑斋 and the east garden
m.cls = "fill"
wW, wS, wE = pts("wall_W"), pts("wall_S"), pts("wall_E")
gate_n = pts("watergate")
hq_rd = pts("hongqiao")
hq_west = ((hq_rd[0][0] + hq_rd[3][0]) / 2, (hq_rd[0][1] + hq_rd[3][1]) / 2)
# the west wall: a doorway where 虹桥 lands on it (丛芳榭之東為獅子林為虹橋: the way in from 丛芳榭, C)
wall_run(wW, WALL_H, "wall_W", gaps=[(hq_west[0], hq_west[1], 1.5)])
wall_run(wS + [(wE[-1][0] + 0.2, wS[-1][1])], WALL_H, "wall_S")
REPORT["walls"] = {"W_m": round(LineString(wW).length, 1), "S_m": round(LineString(wS).length, 1), "E_m": round(LineString(wE).length, 1)}

# ============================================================ the pool: rock banks round it, the arm, the channel (Round 29's water W0368)
m.cls = "fill"
range_poly = Polygon(pts("range")).buffer(0)
skip_bank = unary_union([range_poly.buffer(0.6), LineString(wW).buffer(0.9), LineString(wS).buffer(0.9)])
inside_pool = POOL.intersection(sbox(-60, -20, 40, 60)).buffer(0)
inner = max(getattr(inside_pool, "geoms", [inside_pool]), key=lambda g: g.area)
n_bank = rock_bank(inner, WATER_Y, 2901, every=1.05, skip=skip_bank)
n_bank += rock_bank(STREAM, STREAM_Y, 2902, every=0.9, top_up=(-0.1, 0.35))
REPORT["bank_rocks"] = n_bank
m.cls = "doc"

# ============================================================ 清閟阁: seven bays, two storeys, on the pool
r0 = pts("range")
QX = (r0[0][0] + r0[1][0] + r0[2][0] + r0[3][0]) / 4
QZ = (r0[0][1] + r0[1][1] + r0[2][1] + r0[3][1]) / 4
q_rot = rot_to(-(r0[1][1] - r0[0][1]), r0[1][0] - r0[0][0]) if False else math.atan2(r0[1][1] - r0[0][1], r0[1][0] - r0[0][0]) * -1
q_rot = -math.atan2(r0[1][1] - r0[0][1], r0[1][0] - r0[0][0])   # its front's normal: the frame's +z turned with the range's west-east line
qb_poly, QB_FLOOR, QB_BASE = kit_hall("qb", QX, QZ, q_rot, QB_BAYS, QB_DEPTHS, QB_PL, QB_EAVE, QB_RIDGE, rf="xs", rl=1, pf=QB_DEPTHS[0], pb=QB_DEPTHS[-1],
                                      mid=QB_MID, dr=[2, 3, 4], st={"back": [0.0]}, rr="d")
REPORT["halls"]["qb"].update({"plan_m": [round(LineString(r0[:2]).length, 2), round(LineString(r0[1:3]).length, 2)], "rot_deg": round(math.degrees(q_rot), 2)})
# the plaque 清閟閣 under the upper eave (its place C)
m.push(QX, 0, QZ, q_rot)
hdq = sum(QB_DEPTHS) / 2
m.box(-1.3, 1.3, QB_BASE + QB_MID + 1.85, QB_BASE + QB_MID + 2.55, hdq - 0.05, hdq + 0.02, "plaque")
for i, x in enumerate([-sum(QB_BAYS) / 2 + sum(QB_BAYS[:j]) for j in range(len(QB_BAYS) + 1)]):
    w = m.world((x, 0, hdq))
    S.kp(f"qb_col{i}_foot", (w[0], QB_FLOOR, w[2]))
qb_front_mid = m.world((0, 0, hdq + 0.75))
qb_back = m.world((0, 0, -hdq - 0.75))
m.pop()

# ============================================================ 藤架: the winding stone bridge under the wisteria frame, across the pool on the 明间's line
tj = pts("tengjia")
tj[0] = (float(qb_front_mid[0]), float(qb_front_mid[2]))
tj_y = WATER_Y + TJ_DECK
rng_t = np.random.default_rng(2910)
tj_land = None
for i, ((ax, az), (bx, bz)) in enumerate(zip(tj[:-1], tj[1:])):
    L = math.hypot(bx - ax, bz - az)
    r = along_rot((bx - ax) / L, (bz - az) / L)
    m.push((ax + bx) / 2, 0, (az + bz) / 2, r)
    y_b = min(bed(*m.world((u, 0, v))[::2]) for u in (-L / 2, 0, L / 2) for v in (-TJ_W / 2, TJ_W / 2)) - 0.15
    hl = L / 2 + TJ_W / 2
    m.box(-hl, hl, tj_y - 0.18, tj_y, -TJ_W / 2, TJ_W / 2, "arch", skip=("bottom",))              # the slabs
    for u in np.arange(-L / 2, L / 2 + 0.01, max(1.6, L / max(1, round(L / 2.2)))):              # the piers
        m.box(u - 0.25, u + 0.25, y_b, tj_y - 0.18, -TJ_W / 2 + 0.1, TJ_W / 2 - 0.1, "arch2", skip=("bottom",))
    for sg in (-1, 1):                                                                            # a low stone rail each side (C)
        m.box(-hl, hl, tj_y, tj_y + 0.42, sg * TJ_W / 2 - 0.08, sg * TJ_W / 2 + 0.08, "arch2")
    # the frame: posts by the rails, beams across, purlins along, the wisteria on top and hanging (E0203 垂茸紫瑣: purple)
    for u in np.arange(-L / 2, L / 2 + 0.01, max(1.8, L / max(1, round(L / 2.2)))):
        for sg in (-1, 1):
            m.box(u - 0.07, u + 0.07, tj_y, tj_y + TJ_FRAME, sg * (TJ_W / 2 - 0.05) - 0.07, sg * (TJ_W / 2 - 0.05) + 0.07, "timber")
        m.box(u - 0.06, u + 0.06, tj_y + TJ_FRAME, tj_y + TJ_FRAME + 0.14, -TJ_W / 2 - 0.35, TJ_W / 2 + 0.35, "timber")
    for v in np.linspace(-TJ_W / 2 - 0.2, TJ_W / 2 + 0.2, 5):
        m.box(-hl, hl, tj_y + TJ_FRAME + 0.14, tj_y + TJ_FRAME + 0.22, v - 0.04, v + 0.04, "timber")
    for k in range(int(L / 0.9) + 1):
        u = -L / 2 + k * 0.9 + rng_t.uniform(-0.2, 0.2)
        lump(*m.world((u, 0, rng_t.uniform(-0.5, 0.5)))[::2], 0.0, 0.0, 0.0, rng_t) if False else None
        for v0 in (-TJ_W / 2 - 0.3, -0.35, TJ_W / 2 - 0.4):   # the foliage in clumps with light between them, not a slab
            if rng_t.uniform() < 0.8:
                dv_ = rng_t.uniform(0.45, 0.75)
                m.box(u - rng_t.uniform(0.25, 0.4), u + rng_t.uniform(0.25, 0.4), tj_y + TJ_FRAME + 0.18, tj_y + TJ_FRAME + 0.32 + rng_t.uniform(0, 0.12), v0, v0 + dv_, "leaf" if rng_t.uniform() < 0.5 else "leaf2")
        for sg in (-1, 1):
            if rng_t.uniform() < 0.7:
                vv = sg * (TJ_W / 2 + rng_t.uniform(0.0, 0.3))
                m.box(u - 0.09, u + 0.09, tj_y + TJ_FRAME - rng_t.uniform(0.35, 0.7), tj_y + TJ_FRAME + 0.2, vv - 0.09, vv + 0.09, "wisteria")
    corners = [m.world((u, 0, v)) for u, v in ((-hl, -TJ_W / 2), (hl, -TJ_W / 2), (hl, TJ_W / 2), (-hl, TJ_W / 2))]
    m.pop()
    add_deck(f"tengjia_{i}", [(float(q[0]), float(q[2])) for q in corners], tj_y)
    S.FOOTPRINTS.append([(float(q[0]), float(q[2])) for q in corners])
tj_end = tj[-1]
g_tj = S.gy(*tj_end)
S.kp("tj_frame_start", (tj[0][0], tj_y + TJ_FRAME, tj[0][1]))
REPORT["halls"]["tengjia"] = {"length_m": round(LineString(tj).length, 2), "deck_above_water_m": TJ_DECK, "width_m": TJ_W, "turns": len(tj) - 2,
                              "start_step_m": round(QB_FLOOR - tj_y, 2), "end_step_m": round(tj_y - g_tj, 2)}
# the step down from the hall's porch to the bridge, and from the bridge onto the rockery's path (C)
if QB_FLOOR - tj_y > 0.1:
    flight("tj_N", tj[0][0], tj[0][1] - 0.05, 0.0, TJ_W, QB_FLOOR, tj_y, entry=False, cheeks=False, mat="arch2")
if abs(tj_y - g_tj) > 0.1:
    a_, b_ = tj[-2], tj[-1]
    Ld = math.hypot(b_[0] - a_[0], b_[1] - a_[1])
    if tj_y > g_tj:
        flight("tj_S", b_[0], b_[1], rot_to((b_[0] - a_[0]) / Ld, (b_[1] - a_[1]) / Ld), TJ_W, tj_y, g_tj, entry=False, cheeks=False, mat="arch2")
S.entry("tengjia_N", tj[0][0], tj[0][1] - 0.4, QB_FLOOR)   # on the porch, at the head of the step down to the bridge
S.entry("tengjia_S", tj_end[0], tj_end[1], max(g_tj, tj_y) if tj_y > g_tj else g_tj)

# ============================================================ 虹桥 over the west arm, its doorway in the west wall
hq_endW, hq_dir, hq_gW = hongqiao()
m.cls = "fill"
door_in_wall(hq_west[0], hq_west[1], along_rot(-hq_dir[1], hq_dir[0]), "hq_door", w=2.2, h=2.7, y0=None)
m.cls = "doc"

# ============================================================ 水门 through the east wall where the channel leaves; the east wall either side
sm_ends, sm_walk = watergate()
# the way of Round 9 that reaches the water gate's box from the garden (a reach link, scripts/paths1860.py) ends short of the stair: a few flagstones join them (C)
for f in json.load(open(ROOT / "research/layers/paths_1860.geojson", encoding="utf-8"))["features"]:
    if str(f["properties"].get("from_at", "")).startswith("F0359:"):
        a_ = S.to_local(*to_xz(*f["geometry"]["coordinates"][0]))
        if math.dist(a_, SM_STAIR[0]) < 6.0:
            m.cls = "fill"
            ls_ = LineString([a_, SM_STAIR[0]])
            for k in range(max(1, int(ls_.length / 0.7))):
                q = ls_.interpolate((k + 0.5) * ls_.length / max(1, int(ls_.length / 0.7)))
                g_ = S.gy(q.x, q.y)
                m.box(q.x - 0.45, q.x + 0.45, g_ - 0.1, g_ + 0.06, q.y - 0.4, q.y + 0.4, "pave", skip=("bottom",))
            S.entry("sm_way", float(a_[0]), float(a_[1]))
            REPORT["sm_way_m"] = round(ls_.length, 2)
            m.cls = "doc"
m.cls = "fill"
e_top = (wE[0][0], wE[0][1])
north_of_gate = min(sm_ends, key=lambda p: p[1])
south_of_gate = max(sm_ends, key=lambda p: p[1])
# the court of 清淑斋 against the east wall: a doorway through the east wall into it (C)
nc = pts("nanjing_N02_court")
nc_x0, nc_x1, nc_z0, nc_z1 = rect("nanjing_N02_court")
door_e = (float(np.mean([p[0] for p in wE])), nc_z1 - 2.2)   # in the court's open south part, before the hall (C)
wall_run([e_top, (north_of_gate[0], north_of_gate[1])], WALL_H, "wall_E", gaps=[(door_e[0], door_e[1], 1.2)])
wall_run([(south_of_gate[0], south_of_gate[1]), (wS[-1][0] + 0.2, wS[-1][1])], WALL_H, "wall_SE")
door_in_wall(door_e[0], door_e[1], math.pi / 2, "qs_door_W", w=1.6, h=2.5)
m.cls = "doc"

# ============================================================ the rockery of the west garden, 纳景堂 in it with its terrace, the summit and its stair 磴道, two caves
nj = pts("najing")
NJX, NJZ = mid("najing")
nj_rot = -math.atan2(nj[1][1] - nj[0][1], nj[1][0] - nj[0][0])
m.cls = "fill"
tx0, tx1, tz0, tz1 = rect("najing_terrace")
ter_y = max(S.gy((tx0 + tx1) / 2, (tz0 + tz1) / 2), WATER_Y + 0.5) + 0.12   # a paved court a step above the ground (S01's plain rectangle; C)
ter = [(tx0, tz0), (tx1, tz0), (tx1, tz1), (tx0, tz1)]
S.skirt(ter, ter_y, "platform")
m.flat(ter, ter_y, "pave")
add_deck("najing_terrace", ter, ter_y)
S.FOOTPRINTS.append(ter)
for i, (x, z) in enumerate(ter):
    S.JOINTS.append([f"nj_terrace_{i}", x, bed(x, z) - 0.15, z, "terrace foot"])
nj_poly, NJ_FLOOR, _ = kit_hall("nj", NJX, NJZ, nj_rot, [3.84, 4.48, 3.84], [1.28, 4.16], 0.40, 3.9, 6.1, rf="xs", rl=1, pf=1.28, dr=[1], st={"front": [0.0]}, base=ter_y)
m.cls = "doc"
peakW = pts("peak_W")[0]
blocked_W = unary_union([Polygon(nj_poly).buffer(1.2), Polygon(ter).buffer(0.8), Polygon(qb_poly).buffer(1.0), LineString(tj).buffer(TJ_W / 2 + 0.8),
                         Point(*tj_end).buffer(2.0)] + [Polygon(d[2].exterior.coords).buffer(0.6) for d in DECKS if d[0] == "hongqiao"])
# the stair 磴道 from the terrace's north-east corner round to the summit's pad (C)
pad_y = max(S.gy(*peakW), WATER_Y + 0.5) + PEAK_W - 0.9
stair_path = [(tx1 + 0.8, tz0 - 0.5), (tx1 + 3.5, tz0 - 3.0), (peakW[0] + 1.0, peakW[1] + 4.5), (peakW[0], peakW[1] + 1.9)]
blocked_W = unary_union([blocked_W, LineString(stair_path).buffer(1.2), Point(*peakW).buffer(1.9)])
# two caves 洞 through the rockery: gaps the paths run through, with lintel stones over them (the Suzhou garden's manner; C)
blocked_W = unary_union([blocked_W, LineString(SM_STAIR).buffer(1.3)])
caves = [((NJX - 9.5, NJZ - 3.0), (NJX - 6.0, NJZ - 6.5)), ((peakW[0] + 2.5, peakW[1] + 9.0), (peakW[0] + 6.0, peakW[1] + 11.5))]
blocked_W = unary_union([blocked_W] + [LineString(c_).buffer(0.9) for c_ in caves])
m.cls = "fill"
n_rocks = rock_mass("west", pts("rockery"), 1.4, 3.4, 2920, keep_off=blocked_W, peak=peakW, peak_h=PEAK_W, peak_r=10.0)
# standing peaks 峰石 among the masses: tall narrow stacks of pierced stone, the 'lions' of the garden's name (the Suzhou garden's, T073: a comparable; places and heights C)
rng_s = np.random.default_rng(2925)
rock_poly_W = Polygon(pts("rockery")).buffer(0).difference(WATER_U.buffer(0.6)).difference(blocked_W.buffer(0.4)).difference(WAY_U)
n_peaks = 0
for _ in range(400):
    if n_peaks >= 16:
        break
    bx0, bz0, bx1, bz1 = rock_poly_W.bounds
    x, z = rng_s.uniform(bx0, bx1), rng_s.uniform(bz0, bz1)
    if not rock_poly_W.contains(Point(x, z).buffer(0.7)):
        continue
    g = bed(x, z)
    h = rng_s.uniform(2.6, 4.2)
    y, rr = g - 0.2, rng_s.uniform(0.45, 0.6)
    while y < g + h:
        th = min(g + h - y, rr * rng_s.uniform(1.2, 1.8))
        lump(x + rng_s.uniform(-0.12, 0.12), z + rng_s.uniform(-0.12, 0.12), rr, y, y + th + 0.06, rng_s, "rock2", taper=(0.8, 1.15), k6=7)
        y += th
        rr *= rng_s.uniform(0.85, 1.12)   # the waist and the head: 瘦, 透 (C)
    n_peaks += 1
REPORT["standing_peaks_W"] = n_peaks
pad = [(peakW[0] - 1.8, peakW[1] - 1.8), (peakW[0] + 1.8, peakW[1] - 1.8), (peakW[0] + 1.8, peakW[1] + 1.8), (peakW[0] - 1.8, peakW[1] + 1.8)]
rng_p = np.random.default_rng(2921)
S.skirt(pad, pad_y, "rock_face")
m.flat(pad, pad_y, "rock")
for (ax, az), (bx, bz) in zip(pad, pad[1:] + pad[:1]):
    for t in np.linspace(0, 1, 4)[:-1]:
        x, z = ax + (bx - ax) * t, az + (bz - az) * t
        lump(x, z, rng_p.uniform(0.5, 0.75), bed(x, z) - 0.1, pad_y + rng_p.uniform(-0.1, 0.5), rng_p, "rock")
add_deck("peak_W_pad", pad, pad_y)
S.FOOTPRINTS.append(pad)
rock_steps("dengdao_W", stair_path, ter_y if Polygon(ter).buffer(1.0).contains(Point(*stair_path[0])) else S.gy(*stair_path[0]), pad_y, seed=2922)
for i, (a_, b_) in enumerate(caves):
    rng_c = np.random.default_rng(2930 + i)
    dx, dz = b_[0] - a_[0], b_[1] - a_[1]
    Lc = math.hypot(dx, dz)
    nx, nz = -dz / Lc, dx / Lc
    for t in np.linspace(0, 1, 4):
        x, z = a_[0] + dx * t, a_[1] + dz * t
        g = bed(x, z)
        for sg in (-1, 1):
            lump(x + sg * nx * 1.15, z + sg * nz * 1.15, 0.55, g - 0.2, g + 2.3 + rng_c.uniform(0, 0.3), rng_c, "rock2", taper=(0.8, 0.95))
        lump(x, z, 0.95, g + 2.15, g + 2.75 + rng_c.uniform(0, 0.4), rng_c, "rock", taper=(0.8, 1.0))   # the lintel over the way
    S.kp(f"cave_{i}_mouth", (a_[0], bed(*a_) + 2.15, a_[1]))
m.cls = "doc"
S.kp("peak_W_pad", (peakW[0], pad_y, peakW[1]))
REPORT["peak_W"] = {"pad_above_ground_m": round(pad_y - S.gy(*peakW), 2), "x": round(peakW[0], 2), "z": round(peakW[1], 2)}

# ============================================================ the climbing gallery 云廊 and 探真书屋 on its rock terrace
yl = pts("yunlang")
yl[0] = (float(qb_back[0]), float(qb_back[2]))
g_foot = S.gy(*yl[0])
tz = pts("tanzhen_court")
tz_y = g_foot + TZ_Y
# the gallery's floor rises along its length from the range's back to the court's edge: runs of about 2 m, each a step up
yl_line = LineString(yl)
yl_pts = [yl_line.interpolate(d) for d in np.linspace(0, yl_line.length, max(3, int(yl_line.length / 2.2)) + 1)]
yl_rise = {}
climb_len = min(yl_line.length, 16.0)   # the climb happens in the first 16 m (the steps S01 draws); the rest runs level along the court's edge (C)


def yl_floor(x, z):
    d = yl_line.project(Point(x, z))
    return max(S.gy(x, z), g_foot + 0.25 + (TZ_Y - 0.25) * min(1.0, d / climb_len))


m.cls = "fill"
K.gallery([(p.x, p.y) for p in yl_pts], 2.0, yl_floor, eave=2.7, ridge=3.8, wall_side=0, tile="grey")
for p in yl_pts[::2]:
    S.JOINTS.append([f"yunlang_{len(S.JOINTS)}", p.x, bed(p.x, p.y) - 0.1, p.y, "gallery foot"])
S.FOOTPRINTS.append([(float(a), float(b)) for a, b in yl_line.buffer(1.1, cap_style="flat").exterior.coords[:-1]])
m.cls = "doc"
# the court's terrace of piled rock, its floor at tz_y
tz_poly = [(float(x), float(z)) for x, z in Polygon(tz).buffer(0).exterior.coords[:-1]]
S.skirt(tz_poly, tz_y, "rock_face", step=1.5)
m.flat(tz_poly, tz_y, "pave")
add_deck("tanzhen_court", tz_poly, tz_y)
rng_z = np.random.default_rng(2940)
for (ax, az), (bx, bz) in zip(tz_poly, tz_poly[1:] + tz_poly[:1]):
    Le = math.hypot(bx - ax, bz - az)
    for t in np.linspace(0, 1, max(2, int(Le / 1.3)))[:-1]:
        x, z = ax + (bx - ax) * t, az + (bz - az) * t
        lump(x, z, rng_z.uniform(0.45, 0.7), bed(x, z) - 0.2, tz_y + rng_z.uniform(-0.3, 0.25), rng_z, "rock")
for i, (x, z) in enumerate(tz_poly):
    S.JOINTS.append([f"tz_court_{i}", x, bed(x, z) - 0.15, z, "terrace foot"])
S.FOOTPRINTS.append(tz_poly)
TX, TZc = mid("tanzhen")
m.cls = "fill"
tz_house, _, _ = kit_hall("tz", TX, TZc, 0.0 + q_rot, [3.52, 3.52], [1.12, 3.84], 0.35, 3.4, 5.2, rf="ys", rl=1, pf=1.12, dr=[0, 1], st={"front": [0.0]}, base=tz_y)
m.cls = "doc"
S.kp("yunlang_top", (yl_pts[-1].x, tz_y, yl_pts[-1].y))
REPORT["yunlang"] = {"length_m": round(yl_line.length, 2), "rise_m": TZ_Y, "court_y": round(tz_y, 2)}

# the gallery west along the range's back to 丛芳榭 (S01's double line with posts; C form)
gw = pts("gallery_W")
m.cls = "fill"
K.gallery(gw, 2.2, lambda x, z: S.gy(x, z) + 0.3, eave=2.8, ridge=3.9, wall_side=0, tile="grey")
S.FOOTPRINTS.append([(float(a), float(b)) for a, b in LineString(gw).buffer(1.2, cap_style="flat").exterior.coords[:-1]])
for i, (x, z) in enumerate(gw):
    S.JOINTS.append([f"gallery_W_{i}", x, bed(x, z) - 0.1, z, "gallery foot"])
m.cls = "doc"

# ============================================================ 小香幢: the one-bay tower at the strip's north end, the covered way from the range
xs_ = pts("xiangchuang_strip")
XC = mid("xiangchuang")
m.cls = "fill"
xc_poly, XC_FLOOR, _ = kit_hall("xc", XC[0], XC[1], q_rot, [3.52], [3.52], 0.6, 6.6, 8.8, rf="xs", rl=0, mid=3.4, dr=[0], st={"front": [0.0]})
strip_x = (xs_[0][0] + xs_[1][0]) / 2
strip = [(strip_x, XC[1] + 3.2), (strip_x, float(np.mean([qb_poly[1][1], qb_poly[2][1]])) - 0.2)]
K.gallery(strip, 2.0, lambda x, z: S.gy(x, z) + 0.3, eave=2.7, ridge=3.8, wall_side=0, tile="grey")
S.FOOTPRINTS.append([(float(a), float(b)) for a, b in LineString(strip).buffer(1.1, cap_style="flat").exterior.coords[:-1]])
m.cls = "doc"
REPORT["halls"]["xc"]["strip_m"] = round(LineString(strip).length, 2)

# ============================================================ the court of 清淑斋 (N02) between the rockeries
m.cls = "fill"
door_court_E = (nc_x1, (nc_z0 + nc_z1) / 2 + 6.0)
wall_run([(nc_x0 + 0.3, nc_z0), (nc_x1, nc_z0), (nc_x1, nc_z1), (nc_x0 + 0.3, nc_z1)], 2.7, "qs_court", gaps=[(door_court_E[0], door_court_E[1], 1.1)])
door_in_wall(door_court_E[0], door_court_E[1], math.pi / 2, "qs_door_E", w=1.6, h=2.4)
QSX, QSZ = mid("qingshu")
qs_poly, _, _ = kit_hall("qs", QSX, QSZ - 1.0, q_rot, [2.88, 3.36, 2.88], [1.12, 4.48], 0.45, 3.5, 5.6, rf="xs", rl=1, pf=1.12, dr=[1], st={"front": [0.0]})
S.CLEAR.append([(nc_x0 + 0.8, nc_z0 + 0.6), (nc_x1 - 0.6, nc_z0 + 0.6), (nc_x1 - 0.6, nc_z1 - 0.6), (nc_x0 + 0.8, nc_z1 - 0.6)])
m.cls = "doc"

# ============================================================ the east garden: its wall, the stream with 横碧轩 and the bow bridge, the peak with 占峰亭, 延景楼, 云林石室
m.cls = "fill"
ew = pts("east_wall")
ew = ew + [(nc_x1, nc_z1)]
wall_run(ew, WALL_H, "wall_EG")
m.cls = "doc"
# 横碧轩 on the stream: an open hall facing the stream (east), the bow bridge 弓彎 over the stream before it
HBX, HBZ = mid("hengbi")
hb_rot = q_rot + math.pi / 2
m.cls = "fill"
hb_poly, HB_FLOOR = open_hall("hb", HBX, HBZ, hb_rot, [3.2, 3.84, 3.2], 6.0, 0.55, 3.1, 4.25, 6.0, rf="xs", rolled=True)
m.cls = "doc"
# the bow bridge: a small stone arch over the stream east of the hall, on the hall's axis (C)
hb_dir = (math.sin(hb_rot), math.cos(hb_rot))
ray = LineString([(HBX, HBZ), (HBX + hb_dir[0] * 25, HBZ + hb_dir[1] * 25)]).intersection(STREAM)
bow = None
if not ray.is_empty:
    sseg = min(getattr(ray, "geoms", [ray]), key=lambda g: Point(HBX, HBZ).distance(g))
    bc = sseg.interpolate(0.5, normalized=True)
    Rb, wb = 0.9, 1.4
    y_sb = STREAM_Y + 0.15
    yb_top = y_sb + Rb + 0.28 + 0.1
    gA, gB = S.gy(bc.x - hb_dir[0] * 3.0, bc.y - hb_dir[1] * 3.0), S.gy(bc.x + hb_dir[0] * 3.0, bc.y + hb_dir[1] * 3.0)
    half = Rb + 1.6
    m.push(bc.x, 0, bc.y, along_rot(*hb_dir))
    ybb = min(bed(*m.world((u, 0, v))[::2]) for u in (-half, 0, half) for v in (-wb / 2, wb / 2)) - 0.2

    def bow_top(u):
        ends = gA if u < 0 else gB
        return yb_top - (yb_top - ends) * min(1.0, (abs(u) / half)) ** 2
    arch_faces(-half, half, ybb, bow_top, Rb, y_sb, 0.28, wb, keystone=False)
    for k in range(10):
        ua, ub = -half + 2 * half * k / 10, -half + 2 * half * (k + 1) / 10
        m.poly([(ua, bow_top(ua), -wb / 2), (ub, bow_top(ub), -wb / 2), (ub, bow_top(ub), wb / 2), (ua, bow_top(ua), wb / 2)], "arch")
        for sg in (-1, 1):
            m.poly([(ua, bow_top(ua), sg * wb / 2), (ub, bow_top(ub), sg * wb / 2), (ub, bow_top(ub) + 0.35, sg * wb / 2), (ua, bow_top(ua) + 0.35, sg * wb / 2)], "arch2")
    bA, bB = m.world((-half - 0.2, 0, 0)), m.world((half + 0.2, 0, 0))
    bc_ = [m.world((u, 0, v)) for u, v in ((-half, -wb / 2), (half, -wb / 2), (half, wb / 2), (-half, wb / 2))]
    S.kp("bow_crown", m.world((0, yb_top, 0)))
    m.pop()
    S.FOOTPRINTS.append([(float(q[0]), float(q[2])) for q in bc_])
    S.entry("bow_W", float(bA[0]), float(bA[2]), float(gA))
    S.entry("bow_E", float(bB[0]), float(bB[2]), float(gB))
    for nm, q, g_ in (("bow_W", bA, gA), ("bow_E", bB, gB)):
        S.joint(f"{nm}_foot", float(q[0]), float(q[2]), "bridge end", y=float(g_) - 0.05)
    bow = {"span_m": 2 * Rb, "crown_above_stream_m": round(yb_top - STREAM_Y, 2), "x": round(bc.x, 2), "z": round(bc.y, 2)}
REPORT["halls"]["bow_bridge"] = bow

# 延景楼: three bays, two storeys against the north wall, facing south over the rocks
YJX, YJZ = mid("yanjing")
m.cls = "fill"
yj_poly, YJ_FLOOR, _ = kit_hall("yj", YJX, YJZ + 1.0, q_rot, [3.2, 3.52, 3.2], [1.12, 3.84], 0.5, 6.8, 9.0, rf="xs", rl=1, pf=1.12, mid=3.5, dr=[1], st={"front": [0.0]})
# 云林石室: three small bays of stone among the rocks (三間十笏惟容膝), a stone room: grey walls, small windows (C)
YLX, YLZ = mid("yunlin")
yl_poly, _, _ = kit_hall("ylss", YLX, YLZ + 0.6, q_rot, [2.4, 2.72, 2.4], [3.52], 0.3, 2.9, 4.4, rf="ys", rl=1, dr=[1], st={"front": [0.0]})
m.cls = "doc"
# the east peak with 占峰亭 on it, its stair 磴道 from the south (E0243 歷艱陟頂得稍平)
pk = mid("peak_E")
zf_y = S.gy(*pk) + ZF_Y
m.cls = "fill"
zpad = [(pk[0] - ZF_HS - 0.7, pk[1] - ZF_HS - 0.7), (pk[0] + ZF_HS + 0.7, pk[1] - ZF_HS - 0.7), (pk[0] + ZF_HS + 0.7, pk[1] + ZF_HS + 0.7), (pk[0] - ZF_HS - 0.7, pk[1] + ZF_HS + 0.7)]
S.skirt(zpad, zf_y, "rock_face")
m.flat(zpad, zf_y, "rock")
add_deck("zhanfeng_pad", zpad, zf_y)
S.FOOTPRINTS.append(zpad)
m.cls = "doc"
square_pavilion("zf", pk[0], pk[1], zf_y + 0.3, ZF_HS)
m.cls = "fill"
zstair = [(pk[0] - 6.5, pk[1] + 5.0), (pk[0] - 4.5, pk[1] + 2.0), (pk[0] - ZF_HS - 0.9, pk[1] + 0.4)]   # from the south-west, clear of 横碧轩 (C)
rock_steps("dengdao_E", zstair, S.gy(*zstair[0]), zf_y, seed=2950)
blocked_E = unary_union([Polygon(hb_poly).buffer(1.2), Polygon(yj_poly).buffer(1.0), Polygon(yl_poly).buffer(0.8), Polygon(zpad).buffer(0.3), LineString(zstair).buffer(1.2),
                         Polygon(qs_poly).buffer(0.8), STREAM.buffer(0.6)] + ([Point(bow["x"], bow["z"]).buffer(2.6)] if bow else []))
n_rocks += rock_mass("east_N", pts("rocks_E", 0), 1.2, 2.8, 2960, keep_off=blocked_E)
n_rocks += rock_mass("east_W", pts("rocks_E", 1), 1.3, 3.0, 2961, keep_off=blocked_E)
n_rocks += rock_mass("east_stream", pts("rocks_E", 2), 0.8, 2.0, 2962, keep_off=blocked_E)
peak_poly = Point(*pk).buffer(7.5)
n_rocks += rock_mass("east_peak", list(peak_poly.exterior.coords)[:-1], 1.5, 2.8, 2963, keep_off=unary_union([blocked_E.difference(Polygon(zpad).buffer(0.3)), Polygon(zpad).buffer(0.2)]),
                     peak=pk, peak_h=ZF_Y + 0.3, peak_r=7.5)
for (ax, az), (bx, bz) in zip(zpad, zpad[1:] + zpad[:1]):
    rng_e = np.random.default_rng(int(abs(ax * 100)) % 1000)
    for t in np.linspace(0, 1, 4)[:-1]:
        x, z = ax + (bx - ax) * t, az + (bz - az) * t
        lump(x, z, rng_e.uniform(0.6, 0.9), bed(x, z) - 0.1, zf_y + rng_e.uniform(-0.2, 0.3), rng_e, "rock")
m.cls = "doc"
REPORT["rock_blocks"] = n_rocks
REPORT["halls"]["zf"] = {"floor_above_ground_m": round(zf_y + 0.3 - S.gy(*pk), 2), "side_m": round(2 * (ZF_HS - 0.3), 2), "x": round(pk[0], 2), "z": round(pk[1], 2)}

# ============================================================ level, clear and the decks' joints
garden_W = Polygon(wW + [wS[-1], (wE[0][0], wS[-1][1]), wE[0]]).buffer(0)
garden_E = Polygon(ew).buffer(0)
north = Polygon([(r0[0][0] - 4, r0[0][1] + 1), (xs_[0][0] - 1, r0[0][1] + 1), (xs_[0][0] - 1, xs_[0][1] - 4), (xs_[1][0] + 2, xs_[1][1] - 4), (xs_[1][0] + 2, r0[1][1] + 6), (r0[1][0] + 2, r0[1][1] + 6)]).buffer(0)
for g_ in (garden_W, garden_E, Polygon(nc).buffer(0)):
    if g_.geom_type == "Polygon" and g_.area > 10:
        S.LEVEL.append([(float(a), float(b)) for a, b in g_.exterior.coords[:-1]])
S.CLEAR.append(ter)
REPORT["level_m2"] = round(sum(Polygon(q).area for q in S.LEVEL), 1)

for nm, x, y, z in S.ENTRIES:
    on = [(top, dn) for dn, top, pg, pp in DECKS if pp.covers(Point(x, z))]
    if on:
        REPORT["deck_joints"].append([nm, max(on)[1], round(y - ground(x, z), 3)])

# ============================================================ write
REPORT["triangles"] = m.count()
n_bytes = m.write_glb(HERE / "model.glb", "CC13 狮子林 Shizi Lin", extras={"frame": "x east along 清閟阁's front, y up, z south; origin at the front middle of its box F0357"})
aliases = ["CC13-01", "CC13-02", "CC13-03", "CC13-04", "CC13-05", "CC13-06", "CC13-07", "CC13-08", "CC13-09", "CC13-10", "CC13-11", "CC13-12", "CC13-13", "CC13-14",
           "CC13-N01", "CC13-N02", "CC13-N03", "CC13-N04"]
qb = REPORT["halls"]["qb"]
summary = {
    "id": "CC13",
    "aliases": aliases,
    "name": "狮子林 Shizi Lin",
    "glb": "model.glb",
    "position": S.pos,
    "rotationY": S.rot,
    "line": "The rockery garden of 1772 after the Suzhou garden and 倪瓒's scroll, as S01 draws its walls, halls, pool and rocks and Qianlong's sixteen poems describe them: 清閟阁 on the winding pool facing the rockery, the rainbow bridge and the water gate (their arches after the restored ones on their sites), the stone bridge under its wisteria frame, the climbing gallery to 探真书屋, 小香幢, the court of 清淑斋, the stream with 横碧轩 and the four-column pavilion on the peak. No picture of the garden standing is known: which unnamed hall is which scene, every height and form, and every rock are C.",
    "rows": [
        ["Layout", "As S01 draws it (re-read in Round 29 in plan pixels, B): the west garden about 39 x 49 m inside its walls, the court of N02 against its east wall, the east garden beyond with its curved wall; the pool before 清閟阁 traced from S01's wash (Round 29's water W0368, at the lake's level), its west arm and the channel along the south wall to the water gate (C: S01 draws rocks in that band)"],
        ["Names", "The sixteen scenes of 1772-73 (S05 j83; E0203, E0218, A). S01 labels 清閟阁, 探真书屋, 小香幢 and the water gate; the others are our reading (C): 纳景堂 the hall in the rockery, 清淑斋 the hall in the court between the rockeries, 横碧轩 the hall on the stream, 延景楼 the range on the east garden's north wall, 云林石室 the small three-bay house among its rocks"],
        ["清閟阁", f"Seven bays and two storeys (S01's cells, B; 閣, S05, A), {qb['frontage_m']} m with the bays regularised, a porch on the pool and a gallery behind, a rolled 歇山 in grey tile, the plaque; the 1772 preface: by the water, facing the rockery across the winding pool (臨曲池面假山, A); Qianlong's copy of 倪瓒's scroll was kept here (E0223); every height C"],
        ["The rockery", f"Rock masses on S01's outline round 纳景堂, highest north-east of the hall (its summit {PEAK_W} m, C), piled in tiers, rock banks on the water, a stone stair 磴道 to the summit and two caves the paths run through (Suzhou craftsmen piled it, 吳下髙手堆塑, of Fangshan stone like Taihu's, E0203, E0240: A; every rock's form C)"],
        ["Bridges", f"虹桥 over the pool's west arm on S01's line: one stone arch, a half circle {HQ_SPAN} m across on jambs {HQ_STILT} m above the water, a beast's head on the keystone, steps down to both banks (the poems: a small bridge over the water that boats pass under, a half circle on the water: A; the ring, the head and the steps after the bridge restored on its site, P0415, B; its sizes C); the doorway in the west wall where it lands (C). 藤架: a stone bridge of three turns across the pool under a frame of purple wisteria (E0203, E0237: A; its course C)"],
        ["水门", f"A stone arch {SM_SPAN} m across through the east wall where the channel leaves for the lake, the wall over it with a walk on its top (跨水為牆下置門; 跨波門徑上騎牆: A; S01's half-round, B; the ring after the restored one, P0416, B); the marble slab with the poem of 1772 on its garden face (P0442: the slab survives; its place on the gate C)"],
        ["West garden's halls", "纳景堂 of three bays with its terrace in the rockery (S01's hall and rectangle); the climbing gallery 云廊 from 清閟阁's back up to the court of 探真书屋 on its rock terrace (雲廊拾級上, A; S01); 探真书屋 of two bays (S01); 小香幢, a one-bay tower of two storeys with the shrine above (一間樓 ... 上為佛室, A) at the north end of S01's strip; the gallery west to 丛芳榭; forms and heights C"],
        ["East garden", f"The court of 清淑斋 (S01; 就樹得佳隂, A); the stream 溪 (S01; Round 29's water W0369) with 横碧轩, an open hall of three bays facing it, and a bow-shaped bridge over it (文軒築溪上; 有橋如弓彎 ... 過橋坐敞軒: A); the peak S01 marks with 占峰亭, a square pavilion on four columns (四柱小亭, A), {ZF_Y} m up a stone stair (C); 延景楼, three bays and two storeys (C); 云林石室 of three small bays among the rocks (三間十笏, A); rock masses on S01's strokes"],
        ["Walls", f"White with a grey tiled coping (the Suzhou garden's manner, C), {WALL_H} m, on S01's lines; doorways into the court of 清淑斋 (C)"],
        ["What survives", "Scattered remains (E2000, about 2011); the rainbow bridge and the water gate re-erected on their sites (P0415, P0416, P0500, 2013), the marble slab with the poem of the water gate (P0442). No dig has been published (Q119)"],
        ["Assumed", "Every height; the identification of the unnamed halls; the halls' bays, roofs and porches (the classes); the pool's channel along the south wall; the course of 藤架; the rocks' shapes, the caves, the stairs; the colours: C, the pale tint with conf=1"],
    ],
    "caption": {"frontage_m": round(garden_E.bounds[2] - garden_W.bounds[0], 1), "depth_m": round(max(garden_W.bounds[3], garden_E.bounds[3]) - min(Polygon(tz).bounds[1], garden_E.bounds[1]), 1),
                "eave_m": QB_EAVE, "ridge_m": QB_RIDGE, "assumed": True, "confidence": "C"},
    "hides": [],
    "tris": m.count(),
    "glb_bytes": n_bytes,
}
S.write(HERE, "CC13", aliases, P, "origin at the front middle of 清閟阁's box F0357 at its ground; x east along the front, y up, z south (scripts/model_site.py)", summary)
json.dump(REPORT, open(HERE / "report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"CC13: {m.count()} triangles, GLB {n_bytes / 1e6:.2f} MB; water {WATER_Y:.2f} stream {STREAM_Y:.2f}; 清閟阁 floor {QB_FLOOR:.2f}; rocks {n_rocks}, bank {n_bank}; "
      f"虹桥 {REPORT['halls']['hongqiao']}; 水门 {REPORT['halls']['watergate']}")
