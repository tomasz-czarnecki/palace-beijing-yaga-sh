#!/usr/bin/env python3
"""正觉寺 Zhengjue Si (QC11), the Tibetan Buddhist temple of 绮春园 Qichun Yuan: the fifteenth detailed model (Round 28).

  uv run python models/QC11-zhengjue-si/zhengjuesi.py      (after scripts/kit1860.py has run once)

The temple of 1773 outside the west wall of 绮春园 as S01 draws it and S221 (E0681, after 金勋's 成府村志) describes it, in its state before October 1860 (it was
spared then, E0680): from the south the gate 山门 of three bays with a screen wall either side and a side gate in the wall beyond each, the bell and drum towers,
天王殿 Tianwang Dian of five bays in the second cross wall, the front court with the side halls 配殿 of five bays, the main hall 三圣殿 Sansheng Dian of seven bays
with its terrace 月台 and its rear annex 后庑殿 in the first cross wall, the inner court with the raised walk on the axis and the octagonal pavilion 文殊亭 Wenshu
Ting with double eaves, the ranges along its sides with the 五佛殿 in their middles, and at the back the two-storey 最上楼 Zuishang Lou of seven bays with its balcony
and the three-bay 顺山殿 either side; behind it a strip to the back gate 后门.

Method (docs/METHOD.md, 'a compound from the kit and its evidence', Rounds 17-27): the hall kit (scripts/hall_parts.py) for the timber halls, `masonry()` below for
the gate, 天王殿, the towers and the small gates, `lou()` for 最上楼 and `octagon_pavilion()` for 文殊亭; the layout re-read on S01 (plan_readings.csv, plan pixels,
placed by the fit in use, research/georef/). The forms and proportions from the photographs: Sirén's 三圣殿 of 1918-35 before its loss (P0177), the Bundesarchiv
view of about 1900 of 文殊亭 and 最上楼 (P0173), the surviving gate today (P0427); the rebuilds of 2009-11 (P0428, P0429, P0431) are reading aids only (C).
Writes, beside this file: model.glb, params.json, keypoints.json, joints.json, summary.json, report.json (models/README.md).
Frame (scripts/model_site.py): origin at the front middle of 三圣殿's box F0407, at that box's ground; z south along the axis S01 draws (from the gate's middle to
最上楼's), x east, y up.
Grades: what a source shows or states for this object (S01's layout and cells, S221's bays and roofs, the photographs' forms) is `doc`; what is carried in from the
classes or the rebuilds (every height but those measured, the ranges, the side halls' and towers' forms, the small gates) is `fill` (assumed, C).
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
from hall_parts import JU, HallKit, profile  # noqa: E402
from model_mesh import Mesh  # noqa: E402
from model_parts import Parts, arc_pts  # noqa: E402
from model_site import Site  # noqa: E402
from scene1860 import to_xz  # noqa: E402
from shapely.geometry import LineString, Point, Polygon  # noqa: E402
from shapely.prepared import prep  # noqa: E402

# ============================================================ the figures (heights all C unless said, in one place; the environment only for a sweep, README)
SS_COL = float(os.environ.get("QC11_SS_COL", 4.6))     # 三圣殿: its columns above the floor (P0177's proportion, plate_fit.csv; C)
SS_DEPTH = float(os.environ.get("QC11_SS_DEPTH", 0.0))  # 三圣殿: its depth between the eave columns; 0 = S01's rows (13.5 m)
SS_ROOF = os.environ.get("QC11_SS_ROOF", "wd")         # 三圣殿's roof form: wd 庑殿 (P0177 votes 0.44 m against 1.25 m for xs 歇山, README); the environment only for the test
SS_PL = 0.95     # 三圣殿's platform above the court: P0177's six risers, C
YT_PL = 0.80     # its 月台, one riser lower, C
Y_STRIP = 0.75   # the raised walk and 最上楼's terrace above the court (P0430, P0431: rubble faces with five steps today; C)
WS_PL = 0.30     # 文殊亭's own platform above the walk (P0430: two steps; C)
WS_FACE = 2.65   # 文殊亭: one face between its columns (S01's inner octagon about 6.4 m across: C)
WS_H = {"col": 3.40, "band": 3.85, "low_tip": 4.50, "drum0": 5.25, "drum1": 6.40, "up_tip": 7.10, "apex": 8.60, "finial": 9.80}  # above its floor: P0173's proportions to the face
ZS_COL1, ZS_FL2, ZS_UP, ZS_EAVE = 3.80, 4.30, 7.40, 7.90   # 最上楼: ground columns, the balcony's floor, the upper columns' tops, the eave beam's top (C: P0173, P0431)
G_W, G_D = 10.10, 5.60   # the gate's body: S01's cells 10.1 m (P0427's first fit at 9.6 m drew its ends 0.2 m inside the photograph's); its depth C
G_H = {"floor": 0.50, "base": 0.76, "wall": 2.70, "ridge": 5.50}   # the gate read on P0427 at the body's width (0.0217 m a pixel): above its floor; the floor above the forecourt (three steps)
WALL_OUT, WALL_X, WALL_IN = 3.0, 3.4, 3.0   # the outer wall, the cross walls, the inner lines: heights C

P = {
    "layout": ("the outer wall, the gate with its screen walls and side gates, the two towers, the second cross wall with 天王殿 and two small gates, the side halls, 三圣殿 with its 月台 and annex in the first cross wall, the inner court with the ranges, the raised walk, 文殊亭, 最上楼 with its 顺山殿, the back gate, as S01 draws them",
               "S01", "B", "S01 re-read in Round 28 on 3-6x crops with a 5 and 10 px grid (plan_readings.csv); placed by the fit in use (research/georef/); S01 is B until Q2; the axis's distances agree with today's buildings within 3% (OSM, README)"),
    "halls": ("the gate 山门 three bays, bell and drum towers, 天王殿 five bays, 三圣殿 seven bays with 东西配殿 of five and a three-bay rear annex, 文殊亭 octagonal with double eaves, 最上楼 seven bays with three-bay 顺山殿 either side",
              "S221", "B", "S221 section 四 and its section on the halls, quoting 金勋's 成府村志 (E0681; research-only, facts cited); S01's cells agree for the gate, 天王殿, 三圣殿, the annex, 文殊亭, 最上楼 and the 顺山殿"),
    "gate": ("the gate 山门: a masonry gate of three bays, red walls on a grey stone lower course, a round-arched door with a stone frame in the middle and a round window either side, a band of painted beams, a single-eave 歇山 roof in grey tile; three steps",
             "P0427;S221;S01", "B", "it survives (repaired 2003, S228): P0427 (2013) shows it from the front; S221: 三间 筒瓦歇山 (E0681); the back carried round from the front (C); its heights read on P0427 at the body's width, 9.6 m (S01 10.1 m, the box 9.6 m): C"),
    "screens": ("a red screen wall with a framed panel and a round medallion either side of the gate, on the wall line, with a small tiled coping", "P0427;S70;S221;S01", "B", "S221: 门之西侧砌八字明壁两面（西墙现存）; P0427; S01's two elongated cells; their splay not drawn (S01 draws them on the line); heights C"),
    "side_gates": ("a small gate house in the south wall either side, and two in the second cross wall, and the back gate on the north wall: one arched door each, red walls, small 歇山 roofs", "S01;S221;P0453;S70", "B", "S01's three-cell blocks; S221: a side gate each side of the gate; P0453 shows the back gate today; their form C"),
    "towers": ("the bell tower 钟楼 and the drum tower 鼓楼: two storeys of red masonry, an arched door, a skirt roof, the upper storey with arched windows, a 歇山 roof", "S221;S01;P0427;S70", "B", "S221 names them (E0681); S01's two squares, about 5.9 m; P0427 shows their upper storeys and roofs over the screen walls today (whether old or rebuilt, S228 does not say: Q177); which is which and every height C"),
    "tianwang": ("天王殿: five bays, red masonry front and back with three arched doors and two small arched windows, painted beams, a single-eave 歇山 roof in grey tile, standing in the second cross wall", "S221;S01;P0429;S70", "C", "S221: five bays (B); S01's cells (B); the form is the rebuild's of 2009-11 (P0429: a reading aid, not evidence; S228 says the rebuild drew on a Yangshi Lei plan, not seen); the dig's report (E0688) is a title only"),
    "peidian": ("the side halls 配殿 of the front court, five bays each, single-eave 歇山 in grey tile, a porch of red columns before lattice doors and windows", "S221;S01", "B", "S221: 三圣殿东西配殿各五楹，殿顶为歇山顶 (E0681); S01 draws the east one only (B); the west one mirrored about the axis (C); the depth 6.4 m between S01's 5.3 m and today's 9.3 m roof (OSM) (C)"),
    "sansheng": ("三圣殿: seven bays, a single-eave hip roof 庑殿 in grey tile with a ridge, lattice doors in the three middle bays and lattice windows over sill walls in the others, the lattice on the eave columns, a low stone platform", "P0177;S86;S221;S01", "B",
                 "Sirén's photograph of 1918-35 (P0177, CC0; the hall was spared in 1860 and lost by 1933) shows the single eave, the doors and windows and the low terrace with its flights; fitted with a 歇山 its ridge ends stand 1.8 and 3.9 m off the photograph's (1.25 m rms), with a 庑殿 0.27 and 1.14 m (0.44 m): the hip roof is drawn and the dossier's 歇山 reading of P0177 is withdrawn (Q299); S221: 七间, 三进深, 前后有廊 (E0681: the galleries inside the lattice, which P0177 shows on the eave columns); S01's seven bays 23.3 m between the end columns (B); the rebuild of 2009-11 has double eaves (P0428): not followed"),
    "ss_heights": (f"columns {SS_COL} m above the floor, the platform {SS_PL} m, the bracket band, the ridge by the 举架", "P0177;S86", "C", "a sweep on P0177 (README): columns 4.0, 4.6, 5.2 m and depths 11 and 14 m; all points 0.43-0.65 m rms, the anchored test best at 4.6 m (0.60-0.77 m) and the depth of S01 (14 m) better than 11 m at every column; a shallow curve, so C; the platform's six risers; the roof's rise the main hall class"),
    "ss_depth": ("13.5 m between the front and back eave columns (galleries 2.24 m front and back)", "S01", "C", "S01's rows read as the back and front eave columns (y 7581 and 7635, the second on the cross wall's line); the reading of the rows is C; today's roof outline (OSM) is 13.6 m deep, which allows 10-11 m between columns (Q300)"),
    "annex": ("the rear annex 后庑殿 of three bays behind the hall's middle, a rolled 歇山 roof", "S221;S01", "B", "S221: 并接后庑殿三间 (E0681); S01's three cells; its roof and heights C"),
    "yuetai": ("the terrace 月台 before 三圣殿, with three flights at its front", "S01;P0177;S86", "B", "S01's rectangle; P0177 shows the flights and a stone base before them; its height (one riser below the hall) C"),
    "strip": (f"the raised walk on the axis from the annex to 最上楼, {Y_STRIP} m above the court, faced with rubble, flights from the court at its sides", "S01;P0430;S70;P0431", "B", "S01's two lines (B); its height and the rubble face after the court round 文殊亭 and 最上楼's terrace today (P0430, P0431: C)"),
    "wenshu": ("文殊亭: an octagonal pavilion with double eaves in grey tile, red columns, lattice doors 隔扇 on every face, an upper drum with small lattice windows, a gourd finial", "P0173;S88;P0430;S70;S221;S01", "B",
               "P0173 (Bundesarchiv, about 1900, CC BY-SA 3.0 de) shows it with two eaves and four-leaf lattice doors on the two faces it shows, carried round (C; today's repair has windows over sill walls on the diagonals, P0430); S221: 八方重檐亭 under Qianlong, single eaves when S221 was written; repaired with two eaves in 2003 (P0430, P0639); S01's two octagons; its face 2.65 m (S01, C) and its heights from P0173's proportions to the face, fitted at 0.18 m rms (C)"),
    "wenshu_image": ("inside: Manjusri on a lion on a Sumeru base (not drawn)", "S221", "B", "S221 quoting 金勋 (E0681): the image about 3 丈 (9.6 m) high with its mandorla; the pavilion as drawn is 8.6 m to the apex inside its roof: the figure is a memory of the 20th century (Q301)"),
    "zuishang": ("最上楼: seven bays, two storeys, a porch of tall red columns carrying the balcony 平座 of the upper storey with its rail, lattice fronts on both storeys, a 硬山 roof in grey tile with red gable walls, the back a solid wall", "P0173;S88;S221;S01;P0431;S70;P0453", "B",
                 "P0173 shows the tall porch columns, the balcony with its rail on the beam and the lattice fronts; S221: 后楼七间 (E0681); S01's seven bays (B); the 硬山, the red gables and the solid back are the rebuild's (P0431, P0453: C); every height C"),
    "shunshan": ("the 顺山殿, three bays each, one storey, 硬山 in grey tile, porches", "S221;S01", "B", "S221: 楼东西三间顺山殿（西殿现仍存） (E0681); S01's cells (the east one 10.3 m deep against the west one's 7 m, as drawn); their form C"),
    "ranges": ("the ranges along the inner court's sides, eleven bays each on S01's cells: three bays at each end of one storey, 硬山 in grey tile; the middle five the 五佛殿, two storeys with a porch and a balcony, a 硬山 roof with red gables rising over the low ends", "S01;S228;P0430;S70", "B",
               "S01's cells and the west range's projection, the 五佛殿's porch (B); S228 names the east and west 五佛殿 among the halls that survived and were repaired in 2002-03; P0430 shows the east one beside 文殊亭 today: two storeys, red columns through both, a balcony rail, a 硬山 with red gables over a low range (B: a surviving building as repaired); its heights read roughly on P0430 (C); the end ranges' forms C"),
    "walls": (f"the outer wall of rubble 虎皮石 with a grey coping, {WALL_OUT} m; the two cross walls and the inner lines red with grey copings", "S01;P0453;S70;P0429", "B", "S01's lines (B); the rubble wall after P0453 (the north side today), the red walls after P0427 and P0429 (today); heights C"),
    "colours": ("red columns, walls and lattice, green-blue painted beams, grey tile, grey brick sill walls, white stone", "P0427;S70;P0430", "C", "the surviving gate and 文殊亭 as repaired (P0427, P0430); the photographs of 1900-1935 are black and white"),
    "courts": ("the courts earth with their old trees (the planting of Round 12), no generated hill", "S1161;S1162;S228", "B", "the park's old trees stand in this temple (Q213, research/greens/species.csv GS-0807 to GS-0810); 26 old trees remained before the restoration (S228)"),
}
V = {k: v[0] for k, v in P.items()}

COL = {
    "lacquer": "#8a2f22", "lacquer_dark": "#532218", "wall": "#8f8b84", "plaster": "#e4ddcf", "glass_lattice": "#2b3137", "sill": "#7d7973",
    "band": "#2e6a6c", "bracket": "#3b7b70", "bandred": "#7d2c20", "platform": "#b2ab9c", "coping": "#d2ccbe", "step": "#d8d3c7", "marble": "#ece8df",
    "underside": "#4b453d", "fascia": "#3a2a22", "wallred": "#a4402d", "rubble": "#8d8475", "stone": "#a9a69e", "gold": "#c9a245", "plaque": "#20406a",
    "panel": "#5f7a6e", "door": "#7d2a1e", "pave": "#bdb6a6", "bronze": "#4f5c4e",
    "tile_grey": "#5f6469", "ridge_grey": "#4a4e52",
}

# ============================================================ the frame on S01's axis
S = Site("F0407")
m = Mesh(COL)
S.m = m
PARTS = Parts(m, rail_h=0.9, baluster_segs=4)
REPORT = {"halls": {}, "deck_joints": []}

ROWS = list(csv.DictReader(open(HERE / "plan_readings.csv", encoding="utf-8")))
PX = {r["name"]: [tuple(map(float, p.split())) for p in r["plan_px"].split(";")] for r in ROWS}


def plan_scene(px, py):
    lon, lat = plan_to_wgs84(np.array([px], float), np.array([py], float))
    return to_xz(float(lon[0]), float(lat[0]))


def _scene_mid(name):
    q = [plan_scene(*p) for p in PX[name]]
    return np.mean([a[0] for a in q]), np.mean([a[1] for a in q])


_n, _s = _scene_mid("zuishang"), _scene_mid("gate")
ROT_BOX = S.rot
S.rot = round(math.atan2(_s[0] - _n[0], _s[1] - _n[1]), 6)
READ = {k: [tuple(map(float, S.to_local(*plan_scene(*p)))) for p in v] for k, v in PX.items()}


def rect(name):
    q = READ[name]
    xs, zs = [p[0] for p in q], [p[1] for p in q]
    return min(xs), max(xs), min(zs), max(zs)


def mid(name):
    x0, x1, z0, z1 = rect(name)
    return (x0 + x1) / 2, (z0 + z1) / 2


_ax = {n: mid(n)[0] for n in ("gate", "tianwang", "hall", "yuetai", "annex", "strip", "octagon_in", "zuishang")}
AX = float(np.mean(list(_ax.values())))
_sl = lambda a, b: (b[1] - a[1]) / (b[0] - a[0])
_ow = READ["wall_outer"]
REPORT.update({"rot_box": ROT_BOX, "rot_axis": S.rot, "axis_x": round(AX, 2), "axis_spread_m": round(max(_ax.values()) - min(_ax.values()), 2),
               "axis_reads": {k: round(v - AX, 2) for k, v in _ax.items()},
               "wall_slopes_deg": {"north": round(math.degrees(math.atan(_sl(_ow[0], _ow[1]))), 2), "south": round(math.degrees(math.atan(_sl(_ow[5], _ow[4]))), 2)}})

# ============================================================ decks: raised floors the model draws (the walk, the 月台, the platforms)
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


# ============================================================ helpers (Rounds 24-27)
def kp_platform(name, hf, hd, y_top, anchor=True):
    c0 = m.world((0, 0, 0))
    for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        w = m.world((sx * hf, 0, sq * hd))
        tag = compass(w[0] - c0[0], w[2] - c0[2])
        S.kp(f"{name}_pl_foot_{tag}", (w[0], bed(float(w[0]), float(w[2])), w[2]), anchor=anchor)
        S.kp(f"{name}_pl_top_{tag}", (w[0], y_top, w[2]))


def kp_roof(name, H):
    """The eave corners' tips and the ridge's ends as hall_parts draws them (single eave)."""
    CS, CQ, o = H["hf"] - H["e"], H["hd"] - H["e"], H["o"]
    eave, ridge = H["base"] + H["eave"], H["base"] + H["ridge"]
    c0 = m.world((0, 0, 0))
    hs, hq, y0 = CS + o, CQ + o, eave - o * 0.5
    hx, hz = max(hs, hq), min(hs, hq)
    Lc = min(0.55, 0.04 * (hx + hz)) * H.get("lift", 1.0) if H["rf"] in ("wd", "xs") else 0.0
    for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        w = m.world((sx * hs, 0, sq * hq))
        S.kp(f"{name}_eave_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], y0 + Lc, w[2]))
    band = min(0.12 * hz, 0.6) if H["rl"] else 0.0
    rh = {"wd": max(hx - 0.85 * (hz - band), 0.5), "xs": hx - 0.4 * (hz - band)}.get(H["rf"], hx)
    along_s = hs >= hq
    for sg in (-1, 1):
        w = m.world((sg * rh, 0, 0) if along_s else (0, 0, sg * rh))
        tag = ("W" if w[0] < c0[0] else "E") if abs(w[0] - c0[0]) >= abs(w[2] - c0[2]) else ("N" if w[2] < c0[2] else "S")
        S.kp(f"{name}_ridge_{tag}", (w[0], ridge, w[2]))


def draw(name, H, kp=True, entries=True):
    m.cls = H["cls"]
    m.push(H["x"], 0.0, H["z"], H["rot"])
    feet = K.hall(H)
    corners = [m.world((sx * H["hf"], 0, sq * H["hd"])) for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    fw = {k: m.world(v) for k, v in feet.items()}
    if kp:
        kp_platform(name, H["hf"], H["hd"], H["base"] + H["pl"])
        kp_roof(name, H)
        c0 = m.world((0, 0, 0))
        for sx in (-1, 1):
            w = m.world((sx * (H["hf"] - H["e"]), 0, H["hd"] - H["e"]))
            S.kp(f"{name}_col_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], H["base"] + H["pl"], w[2]))
    m.pop()
    for i, c in enumerate(corners):
        if ground(float(c[0]), float(c[2])) <= bed(float(c[0]), float(c[2])) + 1e-6:
            S.JOINTS.append([f"{name}_pl_{i}", float(c[0]), H["foot"], float(c[2]), "platform foot"])
    S.FOOTPRINTS.append([(float(c[0]), float(c[2])) for c in corners])
    add_deck(f"{name}_platform", [(float(c[0]), float(c[2])) for c in corners], H["base"] + H["pl"], register=False)
    if entries:
        for k, f in fw.items():
            S.entry(f"{name}_{k}", float(f[0]), float(f[2]), float(f[1]))
    REPORT["halls"][name] = {"frontage_m": round(2 * H["hf"], 2), "depth_m": round(2 * H["hd"], 2), "platform_m": round(H["pl"], 2), "eave_m": H["eave"], "ridge_m": H["ridge"],
                             "roof": H["rf"], "tile": H["t"], "bays": len(H["b"]), "flights": len(feet), "grade_class": H["cls"], "x": round(H["x"], 2), "z": round(H["z"], 2)}
    return fw


def hall_spec(x, z, rot, bays, depths, edge, pl, col, roof, rolled, cls, bracket=False, ju="main_hall", pf=0.0, pb=0.0, ps=0.0, tile="grey", over=None):
    """A hall from its spans (eave column to eave column) and its section: platform = columns + edge; eave from the column and the band; ridge by the 举架."""
    span, dep = sum(bays), sum(depths)
    hf, hd = span / 2 + edge, dep / 2 + edge
    gs = [bed(*_w(x, z, rot, s * hf, q * hd)[::2]) for s in (-1, 1) for q in (-1, 1)]
    base = bed(*_w(x, z, rot, 0, hd + 0.5)[::2])
    band = 0.85 if bracket else 0.42
    eave = round(pl + col + band, 2)
    o = 1.25 if col >= 4.0 else 1.05
    rise = round(0.6 * (dep / 2 + o), 2)
    H = dict(hf=hf, hd=hd, base=base, foot=min(gs) - 0.15, pl=pl, eave=eave, ridge=round(eave + rise, 2), e=edge, o=o, b=list(bays), d=list(depths), pf=pf, pb=pb, ps=ps,
             dia=0.34 if col < 4.0 else 0.44, st={"front": [0.0]}, bal=0, rf=roof, rl=1 if rolled else 0, db=0, ju=JU[ju], t=tile, te=None,
             bd="br" if bracket else "bm", dr=[len(bays) // 2], rr="w", k="hall", x=x, z=z, rot=rot, cls=cls)
    if over:
        H.update(over)
    return H


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
    S.JOINTS.append([f"{name}_foot", float(foot[0]), low, float(foot[2]), "flight foot"])
    return foot


def terrace(name, poly, top, face="rubble", deck=True, register=True, fp=True):
    """A terrace 台 on an outline: faces from just below the ground up to its top, a stone coping, a flagged top; a deck the ways lie on."""
    poly = [tuple(map(float, p)) for p in Polygon(poly).buffer(0).exterior.coords[:-1]]
    if Polygon(poly).exterior.is_ccw:
        poly = poly[::-1]
    bots = S.skirt(poly, top - 0.16, face, step=2.0)
    for (ax, az), (bx, bz) in zip(poly, poly[1:] + poly[:1]):
        m.poly([(ax, top - 0.16, az), (bx, top - 0.16, bz), (bx, top, bz), (ax, top, az)], "coping")
    m.flat(poly, top, "pave")
    if deck:
        add_deck(name, poly, top, register=register)
    for i, (x, z) in enumerate(poly):
        S.JOINTS.append([f"{name}_{i}", x, bots[i], z, "terrace foot"])
    if fp:  # a terrace the ways climb onto and cross (the walk, the 月台) is a deck, not a footprint
        S.FOOTPRINTS.append(poly)
    return poly


def wall_run(pts_, h, name, gaps=(), thick=0.8, body="wallred", cap="grey", base_h=0.5):
    """A wall along pts_, broken where a gap (x, z, half width) lies on it; its feet are joints, its outline a footprint."""
    runs = []
    for (ax, az), (bx, bz) in zip(pts_[:-1], pts_[1:]):
        L = math.hypot(bx - ax, bz - az)
        ux, uz = (bx - ax) / L, (bz - az) / L
        cuts = []
        for gx, gz, hw in gaps:
            t = (gx - ax) * ux + (gz - az) * uz
            d = abs(-(gx - ax) * uz + (gz - az) * ux)
            if -hw < t < L + hw and d < 3.5:
                cuts.append((t - hw, t + hw))
        cur = 0.0
        for c0, c1 in sorted(cuts):
            if c0 > cur + 0.3:
                runs.append([(ax + ux * cur, az + uz * cur), (ax + ux * c0, az + uz * c0)])
            cur = max(cur, c1)
        if L > cur + 0.3:
            runs.append([(ax + ux * cur, az + uz * cur), (bx, bz)])
    for i, r in enumerate(runs):
        K.wall(r, h, thick=thick, cap=cap, base_h=base_h, body_mat=body)
        S.FOOTPRINTS.append([(float(x), float(z)) for x, z in list(LineString(r).buffer(thick / 2 + 0.1, cap_style="flat").exterior.coords)[:-1]])
        for k, (x, z) in enumerate(r):
            S.joint(f"{name}{i}_{k}", x, z, "wall foot", y=bed(x, z) - 0.15)
    return runs


def column(x, q, y0, y1, dia, mat="lacquer"):
    r = dia / 2
    m.prism([(x + r * math.cos(2 * math.pi * (k + 0.5) / 8), q + r * math.sin(2 * math.pi * (k + 0.5) / 8)) for k in range(8)], y0, y1, mat, top=False)
    m.box(x - r - 0.1, x + r + 0.1, y0 - 0.02, y0 + 0.1, q - r - 0.1, q + r + 0.1, "coping")  # the base stone 柱顶石


def plaque(x, y0, y1, q, w, sgn=1):
    m.box(x - w / 2 - 0.08, x + w / 2 + 0.08, y0 - 0.08, y1 + 0.08, q - 0.04, q + 0.04, "gold")
    m.poly([(x - w / 2, y0, q + sgn * 0.045), (x + w / 2, y0, q + sgn * 0.045), (x + w / 2, y1, q + sgn * 0.045), (x - w / 2, y1, q + sgn * 0.045)], "plaque")


def arched_door(a0, a1, y0, y1, rise, d_wall, sgn, frame=True):
    """The dressing of an arched door cut by wall_holes in the plane q = 0 of the current frame (sgn: +1 the face looks to +q): a stone frame round the arch,
    reveals through the wall's depth d_wall, red plank doors set 0.25 m in with gilt studs."""
    pts = arc_pts(a0, a1, y1, rise, 8)
    dq = -sgn * d_wall
    for (x0, y0_), (x1, y1_) in zip(pts[:-1], pts[1:]):
        m.poly([(x0, y0_, 0), (x1, y1_, 0), (x1, y1_, dq), (x0, y0_, dq)], "underside")
    for a in (a0, a1):
        m.poly([(a, y0, 0), (a, y1, 0), (a, y1, dq), (a, y0, dq)], "stone")
    m.poly([(a0, y0 + 0.01, 0), (a1, y0 + 0.01, 0), (a1, y0 + 0.01, dq), (a0, y0 + 0.01, dq)], "step")
    if frame:  # the stone frame 券脸, proud of the face
        fw = 0.22
        q1 = sgn * 0.05
        m.box(a0 - fw, a0, y0, y1, min(0, q1), max(0, q1), "stone")
        m.box(a1, a1 + fw, y0, y1, min(0, q1), max(0, q1), "stone")
        outer = arc_pts(a0 - fw, a1 + fw, y1, rise + fw, 8)
        for (x0, y0_), (x1, y1_), (x2, y2_), (x3, y3_) in zip(pts[:-1], pts[1:], outer[1:], outer[:-1]):
            m.poly([(x0, y0_, q1), (x1, y1_, q1), (x2, y2_, q1), (x3, y3_, q1)], "stone")
    qd = -sgn * 0.25  # the two leaves, to the arch's springing, the arch's head panel above in dark
    m.poly([(a0, y0, qd), (a1, y0, qd), (a1, y1, qd), (a0, y1, qd)], "door")
    for (x0, y0_), (x1, y1_) in zip(pts[:-1], pts[1:]):
        m.poly([((a0 + a1) / 2, y1, qd), (x0, y0_, qd), (x1, y1_, qd)], "door")
    m.box((a0 + a1) / 2 - 0.02, (a0 + a1) / 2 + 0.02, y0, y1, min(qd, qd + sgn * 0.02), max(qd, qd + sgn * 0.02), "lacquer_dark")
    for k in range(1, 6):
        yy = y0 + (y1 - y0) * k / 6
        for j in range(4):
            for side in (0, 1):
                xa = a0 + (a1 - a0) * (side * 0.5 + (j + 0.5) / 8)
                m.box(xa - 0.035, xa + 0.035, yy - 0.035, yy + 0.035, min(qd, qd + sgn * 0.04), max(qd, qd + sgn * 0.04), "gold")


def arched_window(a0, a1, y0, y1, rise, d_wall, sgn):
    """A small arched window: reveals, a lattice set 0.15 m in, a stone sill."""
    pts = arc_pts(a0, a1, y1, rise, 6)
    dq = -sgn * 0.15
    for (x0, y0_), (x1, y1_) in zip(pts[:-1], pts[1:]):
        m.poly([(x0, y0_, 0), (x1, y1_, 0), (x1, y1_, dq), (x0, y0_, dq)], "lacquer")
    for a in (a0, a1):
        m.poly([(a, y0, 0), (a, y1, 0), (a, y1, dq), (a, y0, dq)], "lacquer")
    m.poly([(a0, y0, dq), (a1, y0, dq), (a1, y1, dq), (a0, y1, dq)], "glass_lattice")
    for (x0, y0_), (x1, y1_) in zip(pts[:-1], pts[1:]):
        m.poly([((a0 + a1) / 2, y1, dq), (x0, y0_, dq), (x1, y1_, dq)], "glass_lattice")
    n = max(2, round((a1 - a0) / 0.18))
    for k in range(1, n):
        xa = a0 + (a1 - a0) * k / n
        m.box(xa - 0.015, xa + 0.015, y0, y1 + rise * 0.8, min(dq, dq + sgn * 0.03), max(dq, dq + sgn * 0.03), "lacquer")
    for k in range(1, 4):
        yy = y0 + (y1 + rise * 0.6 - y0) * k / 4
        m.box(a0, a1, yy - 0.015, yy + 0.015, min(dq, dq + sgn * 0.03), max(dq, dq + sgn * 0.03), "lacquer")
    m.box(a0 - 0.08, a1 + 0.08, y0 - 0.08, y0, min(0, sgn * 0.08), max(0, sgn * 0.08), "stone")


def round_window(cx, cy, r, sgn):
    """A round window with a stone ring and a stone grille, set 0.12 m into the wall (P0427)."""
    n = 16
    ring_o = [(cx + (r + 0.18) * math.cos(2 * math.pi * k / n), cy + (r + 0.18) * math.sin(2 * math.pi * k / n)) for k in range(n)]
    ring_i = [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
    q1, qd = sgn * 0.05, -sgn * 0.12
    for k in range(n):
        a, b, c, d = ring_o[k], ring_o[(k + 1) % n], ring_i[(k + 1) % n], ring_i[k]
        m.poly([(a[0], a[1], q1), (b[0], b[1], q1), (c[0], c[1], q1), (d[0], d[1], q1)], "stone")
        m.poly([(d[0], d[1], q1), (c[0], c[1], q1), (c[0], c[1], qd), (d[0], d[1], qd)], "stone")
    for k in range(n):
        a, b = ring_i[k], ring_i[(k + 1) % n]
        m.poly([(cx, cy, qd), (a[0], a[1], qd), (b[0], b[1], qd)], "glass_lattice")
    for t in np.linspace(-r * 0.75, r * 0.75, 5):  # the grille: a lattice of crossing bars
        h = math.sqrt(max(r * r - t * t, 0.0))
        m.box(cx + t - 0.03, cx + t + 0.03, cy - h, cy + h, min(qd, qd + sgn * 0.05), max(qd, qd + sgn * 0.05), "stone")
        m.box(cx - h, cx + h, cy + t - 0.03, cy + t + 0.03, min(qd, qd + sgn * 0.05), max(qd, qd + sgn * 0.05), "stone")


def masonry(name, x, z, rot, W, D, floor, wall_top, front, back=None, sides=(), roof="xs", rise=None, o=0.95, base_h=0.9, steps=("front", "back"), band=True,
            brackets=False, step_w=None, kp=True, cls="fill"):
    """A masonry hall (the gate, 天王殿, the towers' lower storey, the small gates) in a frame at (x, z) turned rot (0 faces +z): a low platform `floor` above the
    ground, a grey stone lower course 下碱 `base_h` high, red walls to `wall_top` (above the floor) with holes: front/back lists of ('door', a0, a1, h, rise) or
    ('win', a0, a1, y0, h, rise) or ('round', cx, cy, r); a band of painted beams, a bracket band if asked, a roof (歇山 or 硬山) from the eave tip to the ridge.
    Returns the floor's y and the flights' feet."""
    m.cls = cls
    m.push(x, 0, z, rot)
    hw, hd = W / 2, D / 2
    gs = [K.gy_local(a, b) for a in (-hw, hw) for b in (-hd, hd)]
    g_front = K.gy_local(0, hd + 0.6)
    y_fl = g_front + floor
    pe = 0.35  # the platform's edge beyond the walls
    m.box(-hw - pe, hw + pe, min(gs) - 0.15, y_fl, -hd - pe, hd + pe, "platform", skip=("bottom",))
    m.box(-hw - pe - 0.03, hw + pe + 0.03, y_fl - 0.14, y_fl, -hd - pe - 0.03, hd + pe + 0.03, "coping", skip=("bottom",))
    t = 0.7  # wall thickness
    yw = y_fl + wall_top
    for side, holes in (("front", front), ("back", back if back is not None else front)):
        sg = 1 if side == "front" else -1
        m.push(0, 0, sg * hd, 0 if sg > 0 else math.pi)
        hl = [(h[1], h[2], y_fl, y_fl + h[3], h[4]) for h in holes if h[0] == "door"] + [(h[1], h[2], y_fl + h[3], y_fl + h[3] + h[4], h[5]) for h in holes if h[0] == "win"]
        for d, mat_lo in ((0.0, "stone"), (-t, "stone")):
            # the lower course and the red wall above it, both faces (the inner face for the reveals' ends)
            lo_holes = [(a0, a1, b0, b1, r) for a0, a1, b0, b1, r in hl]
            PARTS.wall_holes(-hw, hw, y_fl, y_fl + base_h, [h for h in lo_holes if h[2] < y_fl + base_h], mat_lo, d=d)
            PARTS.wall_holes(-hw, hw, y_fl + base_h, yw, [(a0, a1, max(b0, y_fl + base_h), b1, r) for a0, a1, b0, b1, r in lo_holes if b1 + r > y_fl + base_h], "wallred", d=d)
        for h in holes:
            if h[0] == "door":
                arched_door(h[1], h[2], y_fl, y_fl + h[3], h[4], t, 1)
            elif h[0] == "win":
                arched_window(h[1], h[2], y_fl + h[3], y_fl + h[3] + h[4], h[5], t, 1)
            elif h[0] == "round":
                round_window(h[1], y_fl + h[2], h[3], 1)
        m.box(-hw - 0.02, hw + 0.02, y_fl - 0.02, y_fl + 0.12, -0.02, 0.06, "stone")
        m.pop()
    for sg in (1, -1):  # the end walls, solid (or with their own holes)
        m.push(sg * hw, 0, 0, sg * math.pi / 2)
        hl = [h for h in sides if h[0] == "win"]
        PARTS.wall_holes(-hd, hd, y_fl, y_fl + base_h, [], "stone", d=0.0)
        PARTS.wall_holes(-hd, hd, y_fl + base_h, yw, [(h[1], h[2], y_fl + h[3], y_fl + h[3] + h[4], h[5]) for h in hl], "wallred", d=0.0)
        for h in hl:
            arched_window(h[1], h[2], y_fl + h[3], y_fl + h[3] + h[4], h[5], t, 1)
        m.pop()
    m.box(-hw + t, hw - t, y_fl, yw - 0.05, -hd + t, hd - t, "underside", skip=("bottom",))  # the inside, in shade
    yb = yw
    if band:  # the painted beams 额枋 on the wall's head, a little proud
        m.box(-hw - 0.06, hw + 0.06, yw, yw + 0.42, -hd - 0.06, hd + 0.06, "band")
        yb = yw + 0.42
    if brackets:
        m.box(-hw - 0.16, hw + 0.16, yb, yb + 0.3, -hd - 0.16, hd + 0.16, "bracket")
        yb += 0.3
    y_tip = yb + 0.12
    rr = rise if rise is not None else 0.6 * (hd + o)
    along = W >= D
    Pf = (lambda a, b, c: (a, b, c)) if along else (lambda a, b, c: (c, b, -a))
    hx, hz = (hw + o, hd + o) if along else (hd + o, hw + o)
    if roof:
        K.roof(Pf, hx, hz, y_tip, y_tip + rr, form=roof, rolled=False, ju=JU["gate_hall"], tile="grey", gable_mat="wallred", gableX=(hw + 0.1 if roof == "ys" else None))
    else:  # a tower's lower storey: its head under the skirt roof drawn by the caller
        m.box(-hw - 0.1, hw + 0.1, y_tip - 0.12, y_tip, -hd - 0.1, hd + 0.1, "underside")
    todo = []
    for side in steps:
        sg = 1 if side == "front" else -1
        n = max(1, round(floor / 0.15))
        if floor < 0.12:
            continue
        sw = step_w or min(3.2, W * 0.4)
        todo.append((side, m.world((0, 0, sg * (hd + pe))), rot + (0 if sg > 0 else math.pi), sw, K.gy_local(0, sg * (hd + pe + n * 0.3 + 0.3))))
    if kp:
        c0 = m.world((0, 0, 0))
        for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            w = m.world((sx * hw, 0, sq * hd))
            tag = compass(w[0] - c0[0], w[2] - c0[2])
            S.kp(f"{name}_wall_foot_{tag}", (w[0], y_fl, w[2]), anchor=True)
            S.kp(f"{name}_wall_top_{tag}", (w[0], yw, w[2]))
            w = m.world((sx * (hw + o), 0, sq * (hd + o)))
            S.kp(f"{name}_eave_{tag}", (w[0], y_tip + min(0.55, 0.04 * (hx + hz)), w[2]))
        rh = (hx - 0.4 * hz) if roof == "xs" else hx
        for sg in (-1, 1):
            w = m.world((sg * rh, 0, 0) if along else (0, 0, sg * rh))
            tag = ("W" if w[0] < c0[0] else "E") if abs(w[0] - c0[0]) >= abs(w[2] - c0[2]) else ("N" if w[2] < c0[2] else "S")
            S.kp(f"{name}_ridge_{tag}", (w[0], y_tip + rr, w[2]))
    corners = [m.world((sx * (hw + pe), 0, sq * (hd + pe))) for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    m.pop()
    feet = {}
    for side, p0, frot, sw, ybot in todo:  # the flights at the top level: flight() pushes its own frame
        feet[side] = flight(f"{name}_{side}", float(p0[0]), float(p0[2]), frot, sw, y_fl, ybot, entry=True)
    S.FOOTPRINTS.append([(float(c[0]), float(c[2])) for c in corners])
    for i, c in enumerate(corners):
        S.JOINTS.append([f"{name}_pl_{i}", float(c[0]), min(gs) - 0.15, float(c[2]), "platform foot"])
    add_deck(f"{name}_floor", [(float(c[0]), float(c[2])) for c in corners], y_fl, register=False)
    REPORT["halls"][name] = {"frontage_m": round(W, 2), "depth_m": round(D, 2), "floor_m": round(floor, 2), "wall_top_m": round(wall_top, 2), "eave_tip_m": round(y_tip - y_fl, 2),
                             "ridge_m": round(y_tip + rr - y_fl, 2), "roof": roof, "x": round(x, 2), "z": round(z, 2)}
    return y_fl, feet


def gate_house(name, nm, rot, w_door=1.5, h_door=2.5, floor=0.3, wall_top=3.0, cls="fill"):
    """A small gate in a wall (the side gates, the back gate): masonry with one arched door, a small 歇山 roof (C)."""
    x0, x1, z0, z1 = rect(nm)
    x, z = (x0 + x1) / 2, (z0 + z1) / 2
    W, D = (x1 - x0, z1 - z0) if abs(math.sin(rot)) < 0.5 else (z1 - z0, x1 - x0)
    W, D = max(W - 0.6, 4.2), max(D - 0.4, 3.0)
    door = [("door", -w_door / 2, w_door / 2, h_door - w_door / 2, w_door / 2)]
    y, feet = masonry(name, x, z, rot, W, D, floor, wall_top, door, door, roof="xs", o=0.75, base_h=0.8, step_w=w_door + 0.6, kp=False, cls=cls)
    return x, z, W, D


# ============================================================ the outer wall, the cross walls, the inner lines (S01)
OW = READ["wall_outer"]
OUT_POLY = Polygon(OW)
REPORT["outer_wall_m"] = {"west_side": round(math.hypot(OW[5][0] - OW[0][0], OW[5][1] - OW[0][1]), 1), "north_side": round(math.hypot(OW[1][0] - OW[0][0], OW[1][1] - OW[0][1]), 1),
                          "south_side": round(math.hypot(OW[4][0] - OW[5][0], OW[4][1] - OW[5][1]), 1), "area_m2": round(OUT_POLY.area, 0)}

gx_, gz_ = mid("gate")
ywx, ywz = mid("yemen_W")
yex, yez = mid("yemen_E")
bgx, bgz = mid("back_gate")
sw_x0, sw_x1, sw_z0, sw_z1 = rect("screen_W")
se_x0, se_x1, se_z0, se_z1 = rect("screen_E")
# the south side: the gate, the screen walls and the side gates stand on it; the wall runs between them
south_gaps = [(gx_, gz_, G_W / 2 + 0.1), ((sw_x0 + sw_x1) / 2, (sw_z0 + sw_z1) / 2, (sw_x1 - sw_x0) / 2 + 0.1), ((se_x0 + se_x1) / 2, (se_z0 + se_z1) / 2, (se_x1 - se_x0) / 2 + 0.1),
              (ywx, ywz, (rect("yemen_W")[1] - rect("yemen_W")[0]) / 2 - 0.2), (yex, yez, (rect("yemen_E")[1] - rect("yemen_E")[0]) / 2 - 0.2)]
m.cls = "doc"
wall_run([OW[5], OW[4]], WALL_OUT, "wall_S", gaps=south_gaps, body="rubble")
wall_run([OW[4], OW[3], OW[2], OW[1]], WALL_OUT, "wall_E", body="rubble")
wall_run([OW[1], OW[0]], WALL_OUT, "wall_N", gaps=[(bgx, bgz, 2.6)], body="rubble")
wall_run([OW[0], OW[5]], WALL_OUT, "wall_W", body="rubble")
N_WALL_FP = len(S.FOOTPRINTS)

# ============================================================ the south front: the gate 山门 (it survives: P0427), the screen walls, the side gates
g_floor_y, g_feet = masonry("gate", gx_, gz_, 0.0, G_W, G_D, G_H["floor"], G_H["wall"],
                            [("door", -0.6, 0.6, 1.15, 0.6), ("round", -2.86, 1.25, 0.62), ("round", 2.86, 1.25, 0.62)],
                            [("door", -0.6, 0.6, 1.15, 0.6), ("round", -2.86, 1.25, 0.62), ("round", 2.86, 1.25, 0.62)],
                            roof="xs", rise=G_H["ridge"] - (G_H["wall"] + 0.54), o=1.25, base_h=G_H["base"], brackets=False, step_w=2.2, cls="doc")
m.cls = "doc"
m.push(gx_, 0, gz_)
for sg in (1, -1):  # the plaque over the door (P0427: a pale board with the name in four scripts: its board drawn, C), the front and back
    plaque(0.0, g_floor_y + 2.25, g_floor_y + 2.55, sg * (G_D / 2 + 0.06), 1.1, sg)
S.kp("gate_door_head", (0.0, g_floor_y + 1.75, G_D / 2))
S.kp("gate_door_foot_L", (-0.6, g_floor_y, G_D / 2))
S.kp("gate_door_foot_R", (0.6, g_floor_y, G_D / 2))
S.kp("gate_win_W_c", (-2.86, g_floor_y + 1.25, G_D / 2))
S.kp("gate_win_E_c", (2.86, g_floor_y + 1.25, G_D / 2))
for k in list(S.KP):
    if k.startswith("gate_") and k in ("gate_door_head", "gate_door_foot_L", "gate_door_foot_R", "gate_win_W_c", "gate_win_E_c"):
        S.KP[k]["p"] = [round(float(v), 3) for v in m.world(S.KP[k]["p"])]
m.pop()


def screen_wall(name, nm, cls="doc"):
    """A red screen wall on the wall line with a framed panel and a round medallion (P0427), a stone base and a small tiled coping."""
    x0, x1, z0, z1 = rect(nm)
    x, z = (x0 + x1) / 2, (z0 + z1) / 2
    L = x1 - x0
    m.cls = cls
    m.push(x, 0, z)
    g = min(K.gy_local(a, b) for a in (-L / 2, L / 2) for b in (-0.6, 0.6))
    h = 2.95
    m.box(-L / 2, L / 2, g - 0.15, g + 0.6, -0.5, 0.5, "stone", skip=("bottom",))
    m.box(-L / 2, L / 2, g + 0.6, g + h, -0.42, 0.42, "wallred", skip=("bottom",))
    for sg in (1, -1):
        q = sg * 0.43
        m.box(-L / 2 + 0.45, L / 2 - 0.45, g + 0.95, g + h - 0.35, min(q, q + sg * 0.04), max(q, q + sg * 0.04), "panel")  # the framed panel (grey-green glazed frame: C)
        m.box(-L / 2 + 0.6, L / 2 - 0.6, g + 1.1, g + h - 0.5, min(q, q + sg * 0.05), max(q, q + sg * 0.05), "wallred")
        ring = [(0.75 * math.cos(2 * math.pi * k / 12), g + 1.78 + 0.5 * math.sin(2 * math.pi * k / 12)) for k in range(12)]
        for k in range(12):
            a, b = ring[k], ring[(k + 1) % 12]
            m.poly([(0, g + 1.78, q + sg * 0.07), (a[0], a[1], q + sg * 0.07), (b[0], b[1], q + sg * 0.07)], "panel")
        for cx in (-1, 1):  # corner pieces 岔角
            for cy in (-1, 1):
                xx, yy = cx * (L / 2 - 0.85), g + 1.78 + cy * 0.55
                m.box(xx - 0.22, xx + 0.22, yy - 0.15, yy + 0.15, min(q, q + sg * 0.07), max(q, q + sg * 0.07), "panel")
    m.box(-L / 2 - 0.05, L / 2 + 0.05, g + h, g + h + 0.12, -0.5, 0.5, "band")
    K.roof(lambda a, b, c: (a, b, c), L / 2 + 0.3, 0.85, g + h + 0.1, g + h + 0.75, form="xs", rolled=False, ju=JU["gallery"], tile="grey")
    S.kp(f"{name}_top_W", m.world((-L / 2, g + h, 0.45)))
    S.kp(f"{name}_top_E", m.world((L / 2, g + h, 0.45)))
    m.pop()
    S.FOOTPRINTS.append([(x - L / 2, z - 0.55), (x + L / 2, z - 0.55), (x + L / 2, z + 0.55), (x - L / 2, z + 0.55)])
    for sx in (-1, 1):
        S.joint(f"{name}_{sx:+d}", x + sx * L / 2, z, "wall foot", y=g - 0.15)


screen_wall("screen_W", "screen_W")
screen_wall("screen_E", "screen_E")
gate_house("yemen_W", "yemen_W", 0.0)
gate_house("yemen_E", "yemen_E", 0.0)
m.cls = "doc"

# ============================================================ the towers 钟楼 and 鼓楼 (S01's squares; their form C)


def tower(name, nm, face_rot):
    x0, x1, z0, z1 = rect(nm)
    x, z = (x0 + x1) / 2, (z0 + z1) / 2
    W = min(x1 - x0, z1 - z0) - 0.2
    door = [("door", -0.75, 0.75, 1.9, 0.75)]
    win = [("win", -0.6, 0.6, 1.3, 1.0, 0.6)]
    y_fl, feet = masonry(name, x, z, face_rot, W, W, 0.3, 4.0, door, [], sides=(), roof=None, rise=0.1, o=0.6, base_h=1.0, steps=("front",), band=True, step_w=2.0, kp=False, cls="fill")
    # the upper storey: a skirt roof 腰檐 at the first floor, the upper walls set in with an arched window each side, the beams, a 歇山 roof
    m.cls = "fill"
    m.push(x, 0, z, face_rot)
    hw = W / 2
    y1 = y_fl + 4.0 + 0.42
    K.skirt(hw + 1.0, hw + 1.0, hw - 0.4, hw - 0.4, y1 + 0.1, y1 + 0.95, "grey")
    up = hw - 0.45
    y2, y3 = y1 + 0.75, y1 + 3.3
    for k in range(4):
        m.push(0, 0, 0, k * math.pi / 2)
        m.push(0, 0, up)
        PARTS.wall_holes(-up, up, y2, y3, [(-0.55, 0.55, y2 + 0.7, y2 + 1.6, 0.55)], "wallred")
        arched_window(-0.55, 0.55, y2 + 0.7, y2 + 1.6, 0.55, 0.5, 1)
        m.pop()
        m.pop()
    m.box(-up - 0.06, up + 0.06, y3, y3 + 0.42, -up - 0.06, up + 0.06, "band")
    m.box(-up - 0.16, up + 0.16, y3 + 0.42, y3 + 0.7, -up - 0.16, up + 0.16, "bracket")
    yt = y3 + 0.82
    K.roof(lambda a, b, c: (a, b, c), up + 1.05, up + 1.05, yt, yt + 2.4, form="xs", rolled=False, ju=JU["pavilion"], tile="grey")
    S.kp(f"{name}_ridge_top", m.world((0, yt + 2.4, 0)))
    c0 = m.world((0, 0, 0))
    for sx, sq in ((-1, 1), (1, 1)):
        w = m.world((sx * hw, 0, sq * hw))
        S.kp(f"{name}_wall_foot_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], y_fl, w[2]), anchor=True)
        w = m.world((sx * (up + 1.05), 0, sq * (up + 1.05)))
        S.kp(f"{name}_eave_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], yt + 0.4, w[2]))
    m.pop()
    REPORT["halls"][name].update({"skirt_m": round(y1 + 0.1 - y_fl, 2), "upper_eave_m": round(yt - y_fl, 2), "ridge_m": round(yt + 2.4 - y_fl, 2)})


tower("bell", "bell", math.pi / 2)    # its door faces the axis (east)
tower("drum", "drum", -math.pi / 2)   # its door faces the axis (west)
for nm in ("sq_W", "sq_E"):  # the small squares south of the towers: stone pedestals (C)
    x_, z_ = mid(nm)
    g_ = ground(x_, z_)
    m.cls = "fill"
    m.box(x_ - 0.9, x_ + 0.9, g_ - 0.15, g_ + 0.45, z_ - 0.9, z_ + 0.9, "stone")
    m.box(x_ - 0.7, x_ + 0.7, g_ + 0.45, g_ + 0.6, z_ - 0.7, z_ + 0.7, "coping")
    S.FOOTPRINTS.append([(x_ - 0.9, z_ - 0.9), (x_ + 0.9, z_ - 0.9), (x_ + 0.9, z_ + 0.9), (x_ - 0.9, z_ + 0.9)])
    S.joint(f"{nm}_foot", x_, z_ + 0.9, "pedestal foot", y=g_ - 0.15)
m.cls = "doc"

# ============================================================ the second cross wall with 天王殿 and two small gates
tx0, tx1, tz0, tz1 = rect("tianwang")
TW_B = [3.04, 3.2, 3.52, 3.2, 3.04]
TW_W, TW_D = sum(TW_B) + 0.6, 7.6
tw_x, tw_z = AX, (tz0 + tz1) / 2
xs_tw = np.cumsum([0] + TW_B) - sum(TW_B) / 2
mids = [(a + b) / 2 for a, b in zip(xs_tw[:-1], xs_tw[1:])]
tw_front = [("win", mids[0] - 0.45, mids[0] + 0.45, 1.25, 0.9, 0.45), ("door", mids[1] - 0.7, mids[1] + 0.7, 1.9, 0.7), ("door", mids[2] - 0.8, mids[2] + 0.8, 2.1, 0.8),
            ("door", mids[3] - 0.7, mids[3] + 0.7, 1.9, 0.7), ("win", mids[4] - 0.45, mids[4] + 0.45, 1.25, 0.9, 0.45)]
tw_y, tw_feet = masonry("tw", tw_x, tw_z, 0.0, TW_W, TW_D, 0.6, 4.0, tw_front, tw_front, roof="xs", rise=0.6 * (TW_D / 2 + 1.2), o=1.2, base_h=0.9, brackets=True, step_w=2.8, cls="fill")
m.push(tw_x, 0, tw_z)
plaque(mids[2], tw_y + 4.0 + 0.45, tw_y + 4.0 + 1.25, TW_D / 2 + 0.25, 1.6)
m.pop()
cw2 = READ["cross_wall_2"]
_tw_gaps = [(tw_x, tw_z, TW_W / 2 + 0.2)]
sg2W, sg2E = mid("sidegate2_W"), mid("sidegate2_E")
_tw_gaps += [(sg2W[0], sg2W[1], 2.3), (sg2E[0], sg2E[1], 2.3)]
m.cls = "doc"
wall_run([cw2[0], cw2[1], cw2[2], cw2[3]], WALL_X, "cross2", gaps=_tw_gaps, body="wallred")
gate_house("sidegate2_W", "sidegate2_W", 0.0, w_door=1.3, h_door=2.3, wall_top=2.9)
gate_house("sidegate2_E", "sidegate2_E", 0.0, w_door=1.3, h_door=2.3, wall_top=2.9)
m.cls = "doc"

# ============================================================ the front court's side halls 配殿 (S221: five bays, 歇山; S01 the east one)
px0, px1, pz0, pz1 = rect("peidian_E")
PD_B = [3.36, 3.6, 3.84, 3.6, 3.36]
PD_D = [1.6, 4.8]
pd_hd = sum(PD_D) / 2 + 0.7
pd_z = (pz0 + pz1) / 2
x_wall_E = (READ["wall_outer"][2][0] + READ["wall_outer"][3][0]) / 2
pd_xE = min((px0 + px1) / 2, x_wall_E - 0.6 - pd_hd)
pd_xW = 2 * AX - pd_xE
x_wall_W = (READ["wall_outer"][0][0] + READ["wall_outer"][5][0]) / 2
pd_xW = max(pd_xW, x_wall_W + 0.6 + pd_hd)
for nm, x_, rot in (("pd_E", pd_xE, -math.pi / 2), ("pd_W", pd_xW, math.pi / 2)):
    H = hall_spec(x_, pd_z, rot, PD_B, PD_D, 0.7, 0.45, 3.4, "xs", False, "fill", pf=1.6, ju="side_hall")
    H["dr"] = [2]
    H["rr"] = "w"
    draw(nm, H)
REPORT["peidian"] = {"x_E": round(pd_xE, 2), "x_W": round(pd_xW, 2), "s01_cell_m": [round(px1 - px0, 2), round(pz1 - pz0, 2)]}

# ============================================================ 三圣殿 (P0177, S221, S01), its 月台 and its rear annex
hx0, hx1, hz0, hz1 = rect("hall")
rows = [p[1] for p in READ["hall_rows"]]  # back edge, back eave columns, back façade, front eave columns, front edge (inner, outer)
cols_ss = [p[0] for p in READ["hall_cols"]]
SS_B = [3.2, 3.36, 3.36, 3.68, 3.36, 3.36, 3.2]
s01_span = cols_ss[-1] - cols_ss[0]
dep_s01 = rows[3] - rows[1]
SS_DEP = SS_DEPTH if SS_DEPTH > 0 else dep_s01
SS_D = [2.24, SS_DEP - 4.48, 2.24]
ss_z = (rows[1] + rows[3]) / 2 + (dep_s01 - SS_DEP) / 2  # a shallower hall keeps its front on the cross wall's line
SS_E = 0.9  # P0177: the platform's edge narrow before the sill walls
ss_hd = SS_DEP / 2 + SS_E
Hss = hall_spec(AX, ss_z, 0.0, SS_B, SS_D, SS_E, SS_PL, SS_COL, SS_ROOF, False, "doc", bracket=True, ju="main_hall", pf=0.0, pb=0.0, ps=0.0)  # P0177: the lattice on the eave columns (the galleries of S221 inside)
Hss.update(dict(dr=[2, 3, 4], rr="d", o=1.55, side_wall=True, st={"front": [0.0]}, fw={"front": 3.4}, per_bay=2))  # one step down to the 月台; the back joins the annex at its level
Hss["ridge"] = round(Hss["eave"] + 0.55 * (SS_DEP / 2 + 1.55), 2)
REPORT["sansheng_s01"] = {"between_end_columns_m": round(s01_span, 2), "model_span_m": round(sum(SS_B), 2), "rows_m": [round(r - rows[0], 2) for r in rows], "depth_used_m": round(SS_DEP, 2),
                          "platform_s01_m": [round(hx1 - hx0, 2), round(hz1 - hz0, 2)]}
# the terrace in front: from the platform's front to S01's 月台 front, one riser lower; three flights at its front (P0177)
yx0, yx1, yz0, yz1 = rect("yuetai")
yt_front = yz1
yt_back = ss_z + ss_hd - 0.05
yt_poly = [(yx0, yt_back), (yx1, yt_back), (yx1, yt_front), (yx0, yt_front)]
m.cls = "doc"
terrace("yuetai", yt_poly, YT_PL, face="platform", fp=False)
for nm, xo, wdt in (("yt_C", 0.0, 3.4), ("yt_W", -(yx1 - yx0) / 2 + 1.9, 2.2), ("yt_E", (yx1 - yx0) / 2 - 1.9, 2.2)):
    flight(nm, (yx0 + yx1) / 2 + xo, yt_front, 0.0, wdt, YT_PL, ground(AX + xo, yt_front + 2.0))
REPORT["yuetai_m"] = [round(yx1 - yx0, 2), round(yt_front - yt_back, 2)]
S.kp("yt_SW", (yx0, YT_PL, yt_front))
S.kp("yt_SE", (yx1, YT_PL, yt_front))
for nm, xo in (("yt_C", 0.0), ("yt_W", -(yx1 - yx0) / 2 + 1.9), ("yt_E", (yx1 - yx0) / 2 - 1.9)):
    for sx, tag in ((-1, "L"), (1, "R")):
        w_ = (3.4 if nm == "yt_C" else 2.2) / 2 + 0.4
        n_ = max(1, round(YT_PL / 0.15))
        S.kp(f"{nm}_foot_{tag}", ((yx0 + yx1) / 2 + xo + sx * w_, ground((yx0 + yx1) / 2 + xo, yt_front + n_ * 0.3 + 0.5), yt_front + n_ * 0.3), anchor=True)
# the stone base before the east flight (P0177; a censer's base: C)
m.cls = "fill"
cbx, cbz = (yx0 + yx1) / 2 + (yx1 - yx0) / 2 - 1.9, yt_front + 3.6
g_ = ground(cbx, cbz)
m.lathe([(0.0, g_ - 0.1), (0.55, g_ - 0.1), (0.55, g_ + 0.15), (0.42, g_ + 0.3), (0.38, g_ + 0.55), (0.5, g_ + 0.7), (0.0, g_ + 0.7)], 8, "stone", cx=cbx, cz=cbz)
S.FOOTPRINTS.append([(cbx - 0.6, cbz - 0.6), (cbx + 0.6, cbz - 0.6), (cbx + 0.6, cbz + 0.6), (cbx - 0.6, cbz + 0.6)])
m.cls = "doc"
fss = draw("ss", Hss)
_cs, _cq = Hss["hf"] - SS_E, Hss["hd"] - SS_E
_xs = [-_cs]
for _b in SS_B:
    _xs.append(_xs[-1] + _b)
_xs[-1] = _cs
for i, x in enumerate(_xs):  # the front columns' feet and tops, numbered from the west (P0177)
    S.kp(f"ss_fcol{i}_foot", (AX + x, Hss["base"] + SS_PL, ss_z + _cq), anchor=True)
    S.kp(f"ss_fcol{i}_top", (AX + x, Hss["base"] + SS_PL + SS_COL, ss_z + _cq))
m.push(AX, 0, ss_z)
plaque(0.0, Hss["base"] + SS_PL + SS_COL + 0.05, Hss["base"] + SS_PL + SS_COL + 0.8, SS_DEP / 2 + 0.28, 2.0)
m.pop()
# the rear annex 后庑殿: three bays behind the middle, joined to the hall's back (S221; S01)
ax0, ax1, az0, az1 = rect("annex")
AN_B = [3.04, 3.84, 3.04]
AN_D = [4.6]
an_hd = sum(AN_D) / 2 + 0.8
an_z = (ss_z - ss_hd) - an_hd + 0.4
Han = hall_spec(AX, an_z, math.pi, AN_B, AN_D, 0.8, SS_PL, 3.5, "xs", True, "fill", ju="side_hall")
Han.update(dict(st={"front": [0.0]}, fw={"front": 2.4}, dr=[1], rr="d"))  # its front faces north: a step down to the walk
# the annex's back door opens onto the raised walk: one riser down (S01 joins them)
an_back = an_z - an_hd
REPORT["annex_m"] = {"s01": [round(ax1 - ax0, 2), round(az1 - az0, 2)], "back_z": round(an_back, 2)}

# ============================================================ the cross wall through 三圣殿 and the inner lines with their doors
cw1 = READ["cross_wall_1"]
ss_hf = sum(SS_B) / 2 + SS_E
z_cw = ss_z + SS_DEP / 2  # on the front eave columns' line
wall_run([cw1[0], (AX - ss_hf, z_cw)], WALL_X, "cross1W", body="wallred")
wall_run([(AX + ss_hf, z_cw), cw1[3]], WALL_X, "cross1E", body="wallred")
iw, ie = READ["inner_W"], READ["inner_E"]
dW, dE = mid("inner_W_door"), mid("inner_E_door")
wall_run([iw[0], (iw[1][0], z_cw)], WALL_IN, "innerW", gaps=[(iw[0][0], dW[1], 0.9)], body="wallred")
wall_run([ie[0], (ie[1][0], z_cw)], WALL_IN, "innerE", gaps=[(ie[0][0], dE[1], 0.9)], body="wallred")
for nm, (x_, z_) in (("door_innerW", (iw[0][0], dW[1])), ("door_innerE", (ie[0][0], dE[1]))):
    S.entry(f"{nm}_in", x_ + (1.0 if nm.endswith("W") else -1.0), z_)
    S.entry(f"{nm}_out", x_ - (1.0 if nm.endswith("W") else -1.0), z_)

# ============================================================ the raised walk on the axis, 文殊亭 on it
sx0, sx1, sz0, sz1 = rect("strip")
zs_x0, zs_x1, zs_z0, zs_z1 = rect("zuishang")
strip_poly = [(sx0, an_back + 0.3), (sx1, an_back + 0.3), (sx1, zs_z1 - 0.2), (sx0, zs_z1 - 0.2)]
m.cls = "doc"
terrace("walk", strip_poly, Y_STRIP, face="rubble", fp=False)
draw("annex", Han)  # after the walk, so that its step lands on the walk's deck
oc_x, oc_z = mid("octagon_in")
for nm, side in (("walk_W", -1), ("walk_E", 1)):
    flight(nm, sx1 if side > 0 else sx0, oc_z + 6.0, side * math.pi / 2, 2.4, Y_STRIP, ground(AX + side * 10, oc_z + 6.0))
for nm, side in (("walk_SW", -1), ("walk_SE", 1)):
    flight(nm, sx1 if side > 0 else sx0, an_back - 4.0, side * math.pi / 2, 2.0, Y_STRIP, ground(AX + side * 10, an_back - 4.0))
REPORT["walk_m"] = [round(sx1 - sx0, 2), round((an_back + 0.3) - (zs_z1 - 0.2), 2)]
S.kp("walk_SW_corner", (sx0, Y_STRIP, an_back + 0.3))


def octagon(r, off=math.pi / 8):
    return [(r * math.cos(off + 2 * math.pi * k / 8), r * math.sin(off + 2 * math.pi * k / 8)) for k in range(8)]


WS_CORNERS = ["ESE", "SSE", "SSW", "WSW", "WNW", "NNW", "NNE", "ENE"]  # octagon(r) vertex k in the frame (x east, z south): angle 22.5 + 45k degrees from +x towards +z


def oct_roof(R_out, R_in, y_tip, y_top, lift, under_to=None, nv=5, tile="grey"):
    """An octagonal roof or skirt in the current frame: eight faces from the eave ring (radius R_out at y_tip, its corners lifted by `lift`, the lift fading towards
    the faces' middles and up the slope) to the ring R_in at y_top, concave by the pavilion's 举架; a thin fascia under the eave edge, the soffit back to under_to
    (radius, y), the hip ridges along the corners."""
    prof = profile(JU["pavilion"])
    O, I = octagon(R_out), octagon(R_in)
    up = lambda t, v: lift * max(0.0, (abs(t) - 0.35) / 0.65) ** 2 * (1 - v) ** 2
    for k in range(8):
        a0, b0, a1, b1 = O[k], O[(k + 1) % 8], I[k], I[(k + 1) % 8]

        def P(t, v):
            f = (t + 1) / 2
            xo, zo = a0[0] + (b0[0] - a0[0]) * f, a0[1] + (b0[1] - a0[1]) * f
            xi, zi = a1[0] + (b1[0] - a1[0]) * f, a1[1] + (b1[1] - a1[1]) * f
            return (xo + (xi - xo) * v, y_tip + (y_top - y_tip) * prof(v) + up(t, v), zo + (zi - zo) * v)
        nu = 4
        for j in range(nv):
            for i in range(nu):
                t0, t1 = -1 + 2 * i / nu, -1 + 2 * (i + 1) / nu
                m.poly([P(t0, j / nv), P(t1, j / nv), P(t1, (j + 1) / nv), P(t0, (j + 1) / nv)], f"tile_{tile}")
            if j == 0:
                for i in range(nu):
                    t0, t1 = -1 + 2 * i / nu, -1 + 2 * (i + 1) / nu
                    p0, p1 = P(t0, 0), P(t1, 0)
                    m.poly([p0, p1, (p1[0], p1[1] - 0.2, p1[2]), (p0[0], p0[1] - 0.2, p0[2])], "fascia")
                    if under_to:
                        R2, y2 = under_to
                        q0, q1 = octagon(R2)[k], octagon(R2)[(k + 1) % 8]
                        f0, f1 = (t0 + 1) / 2, (t1 + 1) / 2
                        u0 = (q0[0] + (q1[0] - q0[0]) * f0, y2, q0[1] + (q1[1] - q0[1]) * f0)
                        u1 = (q0[0] + (q1[0] - q0[0]) * f1, y2, q0[1] + (q1[1] - q0[1]) * f1)
                        m.poly([(p0[0], p0[1] - 0.2, p0[2]), (p1[0], p1[1] - 0.2, p1[2]), u1, u0], "underside")
        for j in range(nv):  # the hip ridge along the corner a0 -> a1
            pa, pb = P(-1, j / nv), P(-1, (j + 1) / nv)
            m.poly([pa, pb, (pb[0], pb[1] + 0.2, pb[2]), (pa[0], pa[1] + 0.2, pa[2])], f"ridge_{tile}")


def octagon_pavilion(cx, cz, base):
    """文殊亭 (P0173, P0430, S01): an octagonal platform, eight red columns, a lattice door on the south and north faces and lattice windows over grey brick sill walls
    on the others, the beam band and brackets, the lower eave, an upper drum with small windows, the upper eave and a gourd finial."""
    m.cls = "doc"
    m.push(cx, 0, cz)
    Rc = WS_FACE / 2 / math.sin(math.pi / 8)  # the column ring's circumradius
    Rp = Rc + 1.15
    fl = base + WS_PL
    m.prism(octagon(Rp), base - 0.1, fl - 0.14, "platform", top=False)
    m.prism(octagon(Rp + 0.04), fl - 0.14, fl, "coping")
    C = octagon(Rc)
    H_ = {k: fl + v for k, v in WS_H.items()}
    for x, z in C:
        column(x, z, fl, H_["col"] + 0.1, 0.36)
    for k in range(8):
        a, b = C[k], C[(k + 1) % 8]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        nrm = math.atan2(mx, mz)
        m.push(mx, 0, mz, nrm)
        door = True  # P0173: lattice doors 隔扇 on the two faces it shows (the south and south-east); carried round (C; today's repair has windows on the diagonals, P0430)
        K.opening(-L / 2 + 0.2, L / 2 - 0.2, 0.0, 1, fl, H_["col"], door, False)
        m.box(-L / 2, L / 2, H_["col"] - 0.05, H_["band"], -0.12, 0.12, "band")
        m.pop()
    m.prism(octagon(Rc - 0.25), fl, H_["col"] - 0.05, "glass_lattice", top=False)
    m.flat(octagon(Rc - 0.25), H_["col"] - 0.05, "underside")
    for k in range(8):  # bracket sets 斗拱 at the corners and between (P0430)
        for t in (0.0, 0.5):
            a, b = C[k], C[(k + 1) % 8]
            x, z = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            m.box(x - 0.16, x + 0.16, H_["band"], H_["band"] + 0.28, z - 0.16, z + 0.16, "bracket")
    # the lower eave: an octagonal skirt from the tip ring (corners lifted) up to the drum (P0173, P0430)
    LIFT = 0.35
    y_lo = H_["low_tip"] - LIFT
    oct_roof(Rc + 1.3, Rc - 0.95 + 0.15, y_lo, H_["drum0"], LIFT, under_to=(Rc, H_["band"] + 0.28))
    # the upper drum: red columns at its corners, small lattice windows 槛窗 between, the band and brackets
    Ru = Rc - 0.95
    U = octagon(Ru)
    for x, z in U:
        column(x, z, H_["drum0"] - 0.2, H_["drum1"], 0.3)
    for k in range(8):
        a, b = U[k], U[(k + 1) % 8]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        m.push(mx, 0, mz, math.atan2(mx, mz))
        m.box(-L / 2, L / 2, H_["drum0"] - 0.2, H_["drum0"] + 0.25, -0.1, 0.06, "band")
        K.opening(-L / 2 + 0.15, L / 2 - 0.15, 0.0, 1, H_["drum0"] + 0.25, H_["drum1"] - 0.05, False, False)
        m.box(-L / 2, L / 2, H_["drum1"] - 0.05, H_["drum1"] + 0.4, -0.12, 0.12, "band")
        m.pop()
    m.prism(octagon(Ru - 0.2), H_["drum0"], H_["drum1"], "glass_lattice", top=False)
    for k in range(8):
        a = U[k]
        m.box(a[0] - 0.14, a[0] + 0.14, H_["drum1"] + 0.4, H_["drum1"] + 0.62, a[1] - 0.14, a[1] + 0.14, "bracket")
    # the upper eave and the finial
    R_up = Ru + 1.25
    oct_roof(R_up, 0.22, H_["up_tip"] - LIFT, H_["apex"], LIFT, under_to=(Ru, H_["drum1"] + 0.62))
    m.lathe([(0.0, H_["apex"] + 0.2), (0.32, H_["apex"] + 0.25), (0.22, H_["apex"] + 0.45), (0.38, H_["apex"] + 0.7), (0.3, H_["apex"] + 0.95), (0.18, H_["apex"] + 1.0),
             (0.12, H_["finial"] - 0.05), (0.0, H_["finial"])], 10, "ridge_grey")
    # key points: the columns' feet and tops by compass, the eaves' tips over the corners, the apex
    for k, (x, z) in enumerate(C):
        S.kp(f"ws_col_{WS_CORNERS[k]}_foot", m.world((x, fl, z)), anchor=True)
        S.kp(f"ws_col_{WS_CORNERS[k]}_top", m.world((x, H_["col"], z)))
        a = octagon(Rc + 1.3)[k]
        S.kp(f"ws_low_eave_{WS_CORNERS[k]}", m.world((a[0], H_["low_tip"], a[1])))
        a = octagon(R_up)[k]
        S.kp(f"ws_up_eave_{WS_CORNERS[k]}", m.world((a[0], H_["up_tip"], a[1])))
    S.kp("ws_apex", m.world((0, H_["apex"], 0)))
    S.kp("ws_finial", m.world((0, H_["finial"], 0)))
    feet = []
    for side, rot in (("S", 0.0), ("N", math.pi)):  # two steps down to the walk, south and north
        m.push(0, 0, 0, rot)
        q0 = Rp * math.cos(math.pi / 8)
        for kk in range(2):
            yk = fl - (kk + 1) * WS_PL / 2
            m.box(-1.2, 1.2, base - 0.1, yk, q0 + kk * 0.32, q0 + (kk + 1) * 0.32, "step")
        f = m.world((0, base, q0 + 0.9))
        feet.append((side, f))
        m.pop()
    foot = [m.world((p[0], 0, p[1])) for p in octagon(Rp)]
    m.pop()
    for side, f in feet:
        S.entry(f"ws_{side}", float(f[0]), float(f[2]), base)
    S.FOOTPRINTS.append([(float(c[0]), float(c[2])) for c in foot])
    add_deck("ws_platform", [(float(c[0]), float(c[2])) for c in foot], fl, register=False)
    REPORT["halls"]["wenshu"] = {"face_m": WS_FACE, "across_columns_m": round(2 * Rc * math.cos(math.pi / 8), 2), "platform_across_m": round(2 * Rp * math.cos(math.pi / 8), 2),
                                 "s01_octagons_m": {"outer": [round(rect("octagon_out")[1] - rect("octagon_out")[0], 2), round(rect("octagon_out")[3] - rect("octagon_out")[2], 2)],
                                                    "inner": [round(rect("octagon_in")[1] - rect("octagon_in")[0], 2), round(rect("octagon_in")[3] - rect("octagon_in")[2], 2)]},
                                 "heights_above_floor_m": WS_H, "floor_above_court_m": round(fl, 2), "x": round(cx, 2), "z": round(cz, 2)}


octagon_pavilion(oc_x, oc_z, Y_STRIP)

# ============================================================ 最上楼 (P0173, S221, S01; the 硬山 and the solid back after the rebuild, C)
ZS_B = [3.52, 3.68, 3.84, 4.16, 3.84, 3.68, 3.52]
zrows = [p[1] for p in READ["zuishang_rows"]]  # back line, façade, front edge


def lou(name, cx, cz, rot, bays, HQ, q_fac, fl, H, roof="ys", doors=(2, 3, 4), back_solid=True, report=None):
    """A two-storey hall 楼 (最上楼, the 五佛殿) in a frame at (cx, cz) turned rot (0 faces +z), the porch columns at q = HQ, the back columns at -HQ, the façade at q_fac:
    the porch of tall columns running up to the upper eave (P0173, P0430, P0431), the ground storey's doors and windows at the façade line, the balcony 平座 over
    the porch with its rail, the upper storey's windows, the beams, the roof in grey tile; `ys`: red gable walls 硬山 with grey corbels and barge bands (the rebuild,
    C); `xs`: a 歇山 over red end walls. H: (ground columns, balcony floor, upper columns' tops, eave beam's top) above the floor. Returns the frame's half sizes."""
    col1, fl2, up, eave = H
    HX = sum(bays) / 2
    xs = list(np.cumsum([0] + list(bays)) - HX)
    m.cls = "doc"
    m.push(cx, 0, cz, rot)
    for x in xs:
        column(x, HQ, fl, fl + up, 0.42)                     # the porch's columns run up to the upper eave (通柱)
    m.cls = "fill"
    for x in xs:
        column(x, q_fac, fl, fl + up, 0.38)
    m.cls = "doc"
    nb = len(bays)
    for i in range(nb):  # the ground storey's façade: doors in the middle bays, windows over sill walls in the others
        K.opening(xs[i] + 0.2, xs[i + 1] - 0.2, q_fac, 1, fl, fl + col1 - 0.05, i in doors, False)
        m.box(xs[i], xs[i + 1], fl + col1 - 0.05, fl + fl2, q_fac - 0.12, q_fac + 0.12, "band")
    # the porch's beam and the balcony 平座: the floor beam over the porch columns (P0173: painted with round ornaments), the floor, the rail between the columns
    m.box(-HX - 0.2, HX + 0.2, fl + col1, fl + fl2, HQ - 0.22, HQ + 0.22, "band")
    for i in range(nb):
        for t in (0.25, 0.5, 0.75):
            xx = xs[i] + (xs[i + 1] - xs[i]) * t
            m.box(xx - 0.16, xx + 0.16, fl + col1 + 0.1, fl + fl2 - 0.1, HQ + 0.22, HQ + 0.25, "gold")
    m.box(-HX, HX, fl + fl2 - 0.12, fl + fl2, q_fac, HQ + 0.3, "lacquer_dark")
    m.box(-HX, HX, fl + col1 - 0.02, fl + col1, q_fac + 0.1, HQ - 0.2, "underside")
    for i in range(nb):
        a0, a1 = xs[i] + 0.22, xs[i + 1] - 0.22
        y0 = fl + fl2
        m.box(a0, a1, y0 + 0.92, y0 + 1.02, HQ + 0.12, HQ + 0.26, "lacquer")       # the rail's top
        m.box(a0, a1, y0 + 0.02, y0 + 0.12, HQ + 0.12, HQ + 0.26, "lacquer")       # its foot
        m.box(a0, a1, y0 + 0.42, y0 + 0.48, HQ + 0.15, HQ + 0.23, "lacquer")
        nbb = max(3, int((a1 - a0) / 0.22))
        for k in range(1, nbb):
            xb = a0 + (a1 - a0) * k / nbb
            m.box(xb - 0.025, xb + 0.025, y0 + 0.12, y0 + 0.92, HQ + 0.16, HQ + 0.22, "lacquer")
        for t in (0.0, 1.0):
            xx = a0 + (a1 - a0) * t
            m.box(xx - 0.06, xx + 0.06, y0, y0 + 1.12, HQ + 0.12, HQ + 0.26, "lacquer")
    # the upper storey: windows at the façade line (after P0173's and P0430's lattice fronts), the hanging lattice under the eave beam
    for i in range(nb):
        K.opening(xs[i] + 0.2, xs[i + 1] - 0.2, q_fac, 1, fl + fl2 + 0.1, fl + up - 0.05, False, False)
        m.box(xs[i] + 0.2, xs[i + 1] - 0.2, fl + up - 0.45, fl + up - 0.3, HQ - 0.03, HQ + 0.03, "lacquer")
    m.box(-HX - 0.2, HX + 0.2, fl + up, fl + eave, HQ - 0.22, HQ + 0.22, "band")
    m.box(-HX, HX, fl + up, fl + eave, q_fac - 0.2, q_fac + 0.2, "band")
    m.box(-HX, HX, fl + up - 0.02, fl + up, q_fac + 0.1, HQ - 0.2, "underside")
    for x in xs:  # bracket blocks on the eave beam (C)
        m.box(x - 0.15, x + 0.15, fl + eave, fl + eave + 0.25, HQ - 0.15, HQ + 0.25, "bracket")
    m.box(-HX + 0.3, HX - 0.3, fl, fl + up - 0.1, -HQ + 0.4, q_fac - 0.15, "glass_lattice")
    o = 1.2
    y_tip = fl + eave + 0.12
    hz = HQ + o
    rise = 0.55 * hz
    ridge = y_tip + rise
    prof = profile(JU["storeyed_hall"])
    m.cls = "fill"
    if back_solid:  # the back: a solid red wall to the eave on a grey stone lower course (P0453, the rebuild: C)
        m.box(-HX - 0.45, HX + 0.45, fl - 0.02, fl + 1.0, -HQ - 0.45, -HQ + 0.2, "stone")
        m.box(-HX - 0.45, HX + 0.45, fl + 1.0, fl + eave + 0.3, -HQ - 0.45, -HQ + 0.2, "wallred")
    WX0, WX1 = HX - 0.3, HX + 0.5
    if roof == "ys":
        for sx in (1, -1):  # the gable walls 山墙: red on a grey stone lower course, the corbels 墀头 at the front, up to the roof's line (P0431: C)
            xa, xb = sorted((sx * WX0, sx * WX1))
            m.box(xa, xb, fl - 0.02, fl + 1.0, -HQ - 0.45, HQ + 0.45, "stone")
            m.box(xa, xb, fl + 1.0, y_tip, -HQ - 0.45, HQ + 0.45, "wallred")
            for xf in (xa, xb):  # the gable's triangle up to the roof's profile
                pts = [(xf, y_tip, -hz + 0.05)] + [(xf, y_tip + (ridge - y_tip) * prof(v) - 0.05, -(hz * (1 - v))) for v in np.linspace(0, 1, 7)[1:]]
                pts2 = [(xf, y_tip + (ridge - y_tip) * prof(v) - 0.05, hz * (1 - v)) for v in np.linspace(0, 1, 7)[::-1][1:]] + [(xf, y_tip, hz - 0.05)]
                ring = pts + pts2
                for k in range(len(ring) - 1):
                    m.poly([(xf, y_tip, ring[k][2]), ring[k], ring[k + 1], (xf, y_tip, ring[k + 1][2])], "wallred")
            for sq in (1, -1):  # the corbel 墀头 under the eave's end, grey brick
                qa, qb = sorted((sq * (HQ + 0.45), sq * (HQ + 0.9)))
                m.box(xa - 0.04, xb + 0.04, y_tip - 0.9, y_tip + 0.1, qa, qb, "wall")
                m.box(xa - 0.06, xb + 0.06, y_tip - 0.25, y_tip + 0.1, min(qa, qb) - 0.1 * (sq < 0), max(qa, qb) + 0.1 * (sq > 0), "coping")
        m.cls = "doc"
        K.roof(lambda x, y, z: (x, y, z), WX1 + 0.06, hz, y_tip, ridge, form="ys", rolled=False, ju=JU["storeyed_hall"], tile="grey", gable_mat="wallred", gableX=WX1)
        for sx in (1, -1):  # the barge band 博缝 along each gable's rake (grey brick)
            xg = sx * (WX1 + 0.04)
            for sg in (1, -1):
                for j in range(8):
                    v0, v1 = j / 8, (j + 1) / 8
                    qa_, qb_ = sg * hz * (1 - v0), sg * hz * (1 - v1)
                    ya_, yb_ = y_tip + (ridge - y_tip) * prof(v0), y_tip + (ridge - y_tip) * prof(v1)
                    m.poly([(xg, ya_ + 0.02, qa_), (xg, yb_ + 0.02, qb_), (xg, yb_ - 0.45, qb_), (xg, ya_ - 0.45, qa_)], "wall")
        hx_r = WX1 + 0.06
    else:
        for sx in (1, -1):  # the end walls: red, both storeys, from the back to the façade; the porch open at its ends
            xa, xb = sorted((sx * (HX - 0.05), sx * (HX + 0.35)))
            m.box(xa, xb, fl - 0.02, fl + 1.0, -HQ - 0.45, q_fac + 0.1, "stone")
            m.box(xa, xb, fl + 1.0, fl + eave, -HQ - 0.45, q_fac + 0.1, "wallred")
        m.cls = "doc"
        hx_r = HX + o
        K.roof(lambda x, y, z: (x, y, z), hx_r, hz, y_tip, ridge, form="xs", rolled=False, ju=JU["storeyed_hall"], tile="grey", gable_mat="lacquer")
    c0 = m.world((0, 0, 0))
    for i, x in enumerate(xs):  # key points: the porch columns' feet, beams, rails and tops (numbered from the frame's left: west for a south front)
        S.kp(f"{name}_col{i}_foot", m.world((x, fl, HQ)), anchor=True)
        S.kp(f"{name}_col{i}_beam", m.world((x, fl + col1, HQ)))
        S.kp(f"{name}_col{i}_rail", m.world((x, fl + fl2 + 1.02, HQ)))
        S.kp(f"{name}_col{i}_top", m.world((x, fl + up, HQ)))
    for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        w = m.world((sx * hx_r, 0, sq * hz))
        S.kp(f"{name}_eave_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], y_tip, w[2]))
    rh = hx_r if roof == "ys" else hx_r - 0.4 * hz
    for sx in (-1, 1):
        w = m.world((sx * rh, 0, 0))
        tag = ("W" if w[0] < c0[0] else "E") if abs(w[0] - c0[0]) >= abs(w[2] - c0[2]) else ("N" if w[2] < c0[2] else "S")
        S.kp(f"{name}_ridge_{tag}", (w[0], ridge, w[2]))
    corners = [m.world((sx * (WX1 + 0.1), 0, sq * (HQ + 0.6))) for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    m.pop()
    REPORT["halls"][name] = {"frontage_m": round(2 * HX, 2), "depth_columns_m": round(2 * HQ, 2), "porch_m": round(HQ - q_fac, 2), "floor_y": round(fl, 2), "ground_columns_m": col1,
                             "balcony_floor_m": fl2, "upper_columns_top_m": up, "eave_tip_m": round(y_tip - fl, 2), "ridge_m": round(ridge - fl, 2), "roof": roof,
                             "x": round(cx, 2), "z": round(cz, 2), **(report or {})}
    return HX, HQ, WX1, [(float(c[0]), float(c[2])) for c in corners]


_zb, _zf, _zp = zrows[0] + 0.55, zrows[1], zrows[2] - 0.75   # 最上楼: the back columns inside the back wall's face; the ground façade (S01's line); the porch columns 0.75 m in
ZZC = (_zb + _zp) / 2
ZHX, ZHQ, ZWX1, zs_corners = lou("zs", AX, ZZC, 0.0, ZS_B, (_zp - _zb) / 2, _zf - ZZC, Y_STRIP, (ZS_COL1, ZS_FL2, ZS_UP, ZS_EAVE), roof="ys",
                                report={"s01_frontage_m": round(zs_x1 - zs_x0, 2)})

# 最上楼's terrace: the walk's level under the tower and its porch, its back on S01's back line; a flight at each end of its front (C)
zt_poly = [(AX - ZWX1 - 0.3, zrows[0] - 0.1), (AX + ZWX1 + 0.3, zrows[0] - 0.1), (AX + ZWX1 + 0.3, zrows[2]), (AX - ZWX1 - 0.3, zrows[2])]
terrace("zs_terrace", zt_poly, Y_STRIP, face="rubble", fp=False)
for nm, sxx in (("zs_flW", -1), ("zs_flE", 1)):
    xf = AX + sxx * (ZWX1 - 3.0)
    flight(nm, xf, zrows[2], 0.0, 2.4, Y_STRIP, ground(xf, zrows[2] + 2.0))

# the 顺山殿 at its ends (S221; S01's cells; one storey, 硬山, porches: C)
for nm, rn, side in (("shunshan_W", "shunshan_W", -1), ("shunshan_E", "shunshan_E", 1)):
    x0, x1, z0, z1 = rect(rn)
    inner = AX + side * (ZWX1 + 0.35)
    outer = x0 if side < 0 else x1
    L = abs(outer - inner)
    bays = [L / 3 - 0.4] * 3
    dep = (z1 - z0) - 1.2
    depths = [1.6, dep - 1.6]
    xc = (inner + outer) / 2 + side * 0.1
    zc = (z0 + z1) / 2
    H = hall_spec(xc, zc, 0.0, bays, depths, 0.6, 0.45, 3.3, "ys", False, "fill", pf=1.6, ju="side_hall")
    H["dr"] = [1]
    draw(nm, H)

# ============================================================ the ranges along the inner court (S01): north 3 bays, the 五佛殿 5 bays with its porch, south 3 bays


WF_H = (3.6, 4.1, 6.9, 7.4)   # the 五佛殿: ground columns, balcony floor, upper columns' tops, eave beam (C: the east one on P0430, two storeys with a balcony, 硬山 with red gables)


def court_range(nm, rn, face):
    """A range along the inner court's side on S01's cells: three bays at each end, one storey, 硬山 (C); the 五佛殿 in the middle five bays, two storeys with a
    porch and a balcony, a 硬山 roof with red gables rising over the low ends (the east one survives, repaired 2002-03: P0430; S228), its porch S01's projection on
    the west range (carried over to the east one, C)."""
    x0, x1, z0, z1 = rect(rn)
    depth_all = x1 - x0
    zN, zS = z0, z1
    L = zS - zN
    bay = L / 11
    rot = math.pi / 2 if face > 0 else -math.pi / 2
    back = x0 if face > 0 else x1
    for tag, za, zb, nb in (("N", zN, zN + 3 * bay, 3), ("S", zN + 8 * bay, zS, 3)):
        dcol = depth_all - 1.4
        hd = dcol / 2 + 0.7
        bays = [(zb - za - 0.3 - 1.4) / nb] * nb
        H = hall_spec(back + face * hd, (za + zb) / 2, rot, bays, [dcol], 0.7, 0.45, 3.1, "ys", False, "fill", ju="side_hall")
        H["dr"] = [nb // 2]
        draw(f"{nm}_{tag}", H)
    # the 五佛殿: its back on the range's back line, its porch columns 0.6 m in from the porch's edge
    za, zb = zN + 3 * bay, zN + 8 * bay
    porch_line = (rect("porch_W")[1] if face > 0 else x0 - (rect("porch_W")[1] - rect("porch_W")[0]))
    q_back, q_por = 0.55, abs(porch_line - back) - 0.6
    HQ = (q_por - q_back) / 2
    qc = back + face * (q_back + HQ)
    bays = [(zb - za - 1.2) / 5] * 5
    fl = 0.45
    yg = min(bed(back + face * a, z_) for a in (0.0, q_por + 0.6) for z_ in (za, zb))
    pf = [(back + face * 0.1, za + 0.1), (back + face * (q_por + 0.75), za + 0.1), (back + face * (q_por + 0.75), zb - 0.1), (back + face * 0.1, zb - 0.1)]
    m.cls = "fill"
    terrace(f"{nm}_wf_pl", pf, fl, face="platform", register=False)
    flight(f"{nm}_wf_fl", back + face * (q_por + 0.75), (za + zb) / 2, rot, 2.6, fl, bed(back + face * (q_por + 3.0), (za + zb) / 2))
    lou(f"{nm}_wf", qc, (za + zb) / 2, rot, bays, HQ, HQ - 1.8, fl, WF_H, roof="ys", doors=(2,), back_solid=True,
        report={"s01_bays_m": round(zb - za, 2), "porch_line_x": round(porch_line, 2)})
court_range("range_W", "range_W", +1)
court_range("range_E", "range_E", -1)

# ============================================================ the back gate on the north wall and the corner walls of the north range
gate_house("back_gate", "back_gate", math.pi)
nb = READ["nrange_back"]
x_shW0 = rect("shunshan_W")[0]
x_shE1 = rect("shunshan_E")[1]
wall_run([nb[0], (x_shW0, nb[0][1] + (nb[1][1] - nb[0][1]) * (x_shW0 - nb[0][0]) / (nb[1][0] - nb[0][0]))], WALL_IN, "nyardW", body="wallred")
wall_run([(x_shE1, nb[0][1] + (nb[1][1] - nb[0][1]) * (x_shE1 - nb[0][0]) / (nb[1][0] - nb[0][0])), nb[1]], WALL_IN, "nyardE", body="wallred")

# ============================================================ the courts: no generated hill inside the wall (joints.json `level`); the planting stays
S.LEVEL.append([tuple(map(float, p)) for p in Polygon(OW).buffer(-0.6, join_style=2).exterior.coords[:-1]])
# the forecourt outside the gate (P0427 paves it today; the dig of 2005 found a road base and a carriageway there, E0685): open ground, no hill, no planting
S.CLEAR.append([(gx_ - 9.0, gz_ + G_D / 2 + 0.4), (gx_ + 9.0, gz_ + G_D / 2 + 0.4), (gx_ + 9.0, gz_ + 18.0), (gx_ - 9.0, gz_ + 18.0)])

# ============================================================ joints on the decks (measured here, not by tools/check_models.py)
for nm, x, y, z in S.ENTRIES:
    on = [(top, dn) for dn, top, pg, pp in DECKS if pp.covers(Point(x, z))]
    if on:
        REPORT["deck_joints"].append([nm, max(on)[1], round(y - ground(x, z), 3)])

# ============================================================ write
REPORT["triangles"] = m.count()
n_bytes = m.write_glb(HERE / "model.glb", "QC11 正觉寺 Zhengjue Si", extras={"frame": "x east, y up, z south along S01's axis; origin at 三圣殿's box front middle"})
aliases = ["QC11-01", "QC11-02", "QC11-03", "QC11-04", "QC11-05", "QC11-B1357", "QC11-B1367"]
ss = REPORT["halls"]["ss"]
depth_total = (gz_ + G_D / 2) - OW[0][1]
summary = {
    "id": "QC11",
    "aliases": aliases,
    "name": "正觉寺 Zhengjue Si",
    "glb": "model.glb",
    "position": S.pos,
    "rotationY": S.rot,
    "line": "The temple of 1773 as S01 draws its walls, courts and halls and S221 names them (after 金勋), spared in 1860: the gate as it survives (P0427), the towers, 天王殿, the side halls, 三圣殿 with its hip roof after Sirén's photograph (P0177), the raised walk with 文殊亭 after the view of about 1900 (P0173), the two-storey 五佛殿 as the east one survives (P0430), 最上楼 with its balcony and the 顺山殿. Every height but those read on the photographs, and the end ranges', side halls' and towers' forms, are C.",
    "rows": [
        ["Layout", "As S01 draws it (re-read in Round 28 in plan pixels, B): the outer wall about 67 x 145 m, the gate in the south wall, two cross walls, the inner court; the distances along the axis agree with today's buildings within 3% (OSM)"],
        ["山门 (gate)", "Three bays, red walls on a grey stone course, a round-arched door with a stone frame and a round window either side, a band of painted beams, a single-eave 歇山 in grey tile (it survives, repaired 2003: P0427; S221 三间 筒瓦歇山; B); 10.1 m wide as S01 draws it, its heights read on P0427 (the wall 2.7 m, the ridge 5.5 m above its floor; the photograph's fit 0.15 m rms; C); the plaque in four scripts (S221) drawn as a board"],
        ["Screen walls and side gates", "A red screen wall with a framed panel and medallion either side of the gate (S221: 八字明壁, the west one survives; P0427), a side gate in the wall beyond each (S221; S01), two small gates in the second cross wall and the back gate on the north wall (S01; P0453); their forms C"],
        ["Bell and drum towers", "Two storeys of red masonry with a skirt roof and a 歇山 top on S01's squares (S221 names them; P0427 shows their tops today); which is which and every height C"],
        ["天王殿", "Five bays (S221) in the second cross wall (S01); red masonry fronts with three arched doors, a 歇山 roof: the form of the rebuild of 2009-11 (P0429), a reading aid only (C)"],
        ["配殿 (side halls)", "Five bays each, single-eave 歇山 in grey tile (S221: 三圣殿东西配殿各五楹); S01 draws the east one, the west one is mirrored (C); porches and heights C"],
        ["三圣殿", f"Seven bays (S221), {ss['frontage_m']} m along its platform, a single-eave hip roof 庑殿 in grey tile with a ridge, lattice doors in the three middle bays and windows over sill walls in the others, the bracket band, a low stone platform with the 月台 and three flights before it, after Sirén's photograph (P0177, 1918-35, CC0) of the hall the fire of 1860 spared: the photograph fits a hip roof at 0.44 m rms and a 歇山 at 1.25 m (Q299); the rebuild of 2009-11 has double eaves (P0428), not followed; its column {SS_COL} m and its depth {round(SS_DEP, 1)} m (S01's rows) from a sweep on the photograph (C, Q300); the three-bay rear annex (S221 后庑殿三间; S01) with a rolled roof (C)"],
        ["文殊亭", "Octagonal with double eaves in grey tile, red columns, four-leaf lattice doors on every face, an upper drum with small windows and a gourd finial, on the raised walk (P0173, about 1900, fitted at 0.18 m rms; it survives, repaired with two eaves in 2003: P0430; S221; S01's octagons); its face 2.65 m and its heights from P0173's proportions (C); inside, the great Manjusri on a lion (S221) is not drawn (Q301)"],
        ["最上楼", "Seven bays, two storeys: the tall porch columns carrying the balcony with its rail, lattice fronts on both storeys (P0173; S221 后楼七间; S01), the 硬山 roof with red gables and the solid back wall after the rebuild (P0431, P0453: C); the three-bay 顺山殿 at its ends (S221; S01; the west one survives), one storey, 硬山 (C)"],
        ["Inner court", "The raised walk on the axis from the annex to 最上楼's terrace (S01), faced with rubble and 0.75 m high as the court is today (P0430, P0431: C); the ranges along the sides on S01's cells, their middle five bays the 五佛殿: two storeys with a porch and a balcony and a 硬山 with red gables over the one-storey ends, as the east one stands today (P0430; S228 names them among the survivors; the west one's porch on S01, the east one's carried over: C)"],
        ["Walls and courts", "The outer wall of rubble with a grey coping (P0453 today; C), the cross walls and inner lines red (C); the courts earth with their old trees (the planting of Round 12, Q213), no generated hill in them"],
        ["What survives", "The gate, 文殊亭, the east and west 五佛殿, the side halls, the west corner rooms and the west 顺山殿 (repaired 2002-03); the Qing base, column bases and lower walls of 三圣殿; 天王殿, 三圣殿 and 最上楼 were rebuilt in 2009-11 and the temple opened in July 2011 (S228)"],
        ["Assumed", "Every height except the gate's (P0427), 三圣殿's column and 文殊亭's proportions (P0173, P0177); the ranges', side halls', towers', small gates' and annex's forms; the rubble walk and terraces; which tower is the bell tower; the colours (the survivors as repaired): C, the pale tint with conf=1"],
    ],
    "caption": {"frontage_m": round(OW[1][0] - OW[0][0], 1), "depth_m": round(depth_total, 1), "eave_m": round(ss["eave_m"], 2), "ridge_m": round(ss["ridge_m"], 2), "assumed": True, "confidence": "C"},
    "hides": [],
    "tris": m.count(),
    "glb_bytes": n_bytes,
}
S.write(HERE, "QC11", aliases, P, "origin at the front middle of 三圣殿's box F0407 at its ground; z south along S01's axis (the gate's middle to 最上楼's), x east, y up (scripts/model_site.py)", summary)
json.dump(REPORT, open(HERE / "report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
print(f"QC11: {m.count()} triangles, GLB {n_bytes / 1e6:.2f} MB; axis {AX:.2f} (spread {REPORT['axis_spread_m']} m); 三圣殿 S01 span {s01_span:.2f} m, depth {SS_DEP:.2f}; "
      f"ridge {ss['ridge_m']}; deck joints {len(REPORT['deck_joints'])}")
