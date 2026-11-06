#!/usr/bin/env python3
"""方壶胜境 Fanghu Shengjing (YM29), the towers on their terraces over the water: the tenth detailed model (Round 24).

  uv run python models/YM29-fanghu-shengjing/fanghushengjing.py      (after scripts/kit1860.py has run once)

The scene as the leaf of 1744 paints it and S01 draws it, in its state before October 1860: three ranges of two-storey towers, each a five-bay middle block with a
pair of side towers (nine towers, S361's note, E1852): at the water the front range, whose upper floor bore the plaque 宜春殿, with the three-bay entry before it; on the
upper, brick-faced terrace (Malone, S02 pp.92-93) 哕鸾殿 and, at the back, 琼华楼; the side towers joined to their middle block, and the middle range to the rear one, by
two-storey galleries ('elevated walks connecting their second stories', Malone); the lower terrace on the water with its stepped bastions (the ruin's line today, P0383);
the galleries on their strips out to the two cruciform water terraces with 集瑞亭 and 凝祥亭; the causeway with the two archways 坊座 (S05 j82:12b) to the square terrace
of 迎薰亭 with its bronze dragons and phoenixes (E1856) and the steps to the water for the barge (Malone).

Method (docs/METHOD.md, 'a compound from the kit and its evidence', Rounds 17-19): every hall is the hall kit (scripts/hall_parts.py) from its numbers, adapted to the leaf;
two-storey towers by `tower()` below (the kit's second storey with a skirt roof and a balcony, and the leaf's double top eave on the rear range); the layout read on S01
(plan_readings.csv, plan pixels, placed by the fit in use, research/georef/). The inlet the terraces stand in is Round 24's water W0365 (research/plan/water_manual.json).
Writes, beside this file: model.glb, params.json, keypoints.json, joints.json, summary.json, report.json (models/README.md).
Frame (scripts/model_site.py): origin at the front middle of the front range's box F0164, at that box's ground; x east along the front, y up, z south, turned to the axis
S01 draws (from 琼华楼 and 哕鸾殿 to the entry, the causeway and 迎薰亭).
Grades: what a source states for this object (S01's layout, the leaf's storeys, roofs, colours and parts, the texts' names and counts) is `doc`; what is carried in from the
hall classes or guessed (every height, the bays' widths, the galleries' form, the archways' and the bronzes' form, the court's furniture) is `fill` (assumed, C).
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
from hall_parts import HallKit, JU  # noqa: E402
from model_mesh import Mesh  # noqa: E402
from model_site import Site  # noqa: E402
from scene1860 import DATUM_M, to_xz  # noqa: E402
from shapely.geometry import LineString, Point, Polygon  # noqa: E402
from shapely.prepared import prep  # noqa: E402

LIFT_LOW = 2.6   # the lower terrace's top above the water (C)
LIFT_CW = 1.9    # the causeway and the three water terraces above the water (C)
LIFT_UP = 3.0    # the upper terrace above the lower one (C)
P = {
    "layout": ("the lower terrace on the water, the upper terrace behind it, the three ranges, galleries, strips, causeway and three water terraces as S01 draws them", "S01", "B",
               "S01 re-read in Round 24 on 3x and 4x crops (plan_readings.csv): every block, strip and terrace in plan pixels; S01 is B until Q2; its scale here about 0.22 m a pixel"),
    "water": ("the inlet before the terraces, 2.59 ha, its level 42.76 m (Round 10's rule for a body)", "S01;S08", "B",
              "S01's region R0018, classed land by default and taken as water in Round 24 (research/plan/water_manual.json, W0365; Q191); the leaf paints the terraces standing in the water (S08 P0029); its level the plain along its shore less 1.5 m (research/terrain/water_levels.csv, C)"),
    "names": ("nine towers: 宜春殿 with 锦绮楼 and 翡翠楼 at the water; 哕鸾殿 with 碧云楼 and 紫霞楼; 琼华楼 with 千祥阁 and 万福阁; the pavilions 迎薰亭, 集瑞亭, 凝祥亭", "S05;S310;S361", "A",
              "S05 j82:12a-13a: 臨池樓宇為方壺勝境上下各五楹 ... 其北樓宇為噦鸞殿又北為瓊華樓, the upper plaque of the front 宜春殿 (A); the twenty plaques written in 乾隆五年 1740 (S310 rec. 8298); S361's note: three five-bay towers each with a pair of side towers, 2,235 Buddha images in the nine towers (E1852, B); which side tower bore which plaque C"),
    "storeys": ("every tower of two storeys; the three pavilions on the water of one", "S05;S02;S258;S08", "A",
                "S05: 上下各五楹 (the front, A); Malone: all of two stories (S02 pp.92-93, E1850, B); S258: apart from the three pavilions on the water every building has an upper floor (E1849, B); the leaf (S08 P0029)"),
    "low_terrace": (f"the lower terrace, its top {LIFT_LOW} m above the water, white marble faces and balustrade, stepped bastions", "S01;S08;S02", "B",
                    "its outline S01 (B); the leaf: a white marble base with a balustrade under the front range, stepping out at the bastions (S08 P0029); Malone: three two-storey buildings on the lower terrace by the lake (E1850); today's line of bastions in the water (P0383, P0787: free photographs, B); its height C (the leaf's base about 0.6 times a storey)"),
    "up_terrace": (f"the upper terrace, {LIFT_UP} m above the lower one, brick faces, a balustrade along its south edge", "S01;S02;S08", "B",
                   "Malone: the upper terrace brick-faced (S02 pp.92-93); its outline S01; the leaf paints the middle court above the front range's roofs with a white rail at its edge; its height C"),
    "fr": ("宜春殿: five bays, two storeys, a skirt roof and a balcony between, 歇山 with yellow tile and green trim 剪边", "S05;S08;S01", "A",
           "S05 上下各五楹 (A); the leaf: red columns and lattice on both storeys, a balustraded balcony at the upper floor, 歇山 in yellow with green edges (S08 P0029, crop ym29_c1; research/scenes/halls.csv); S01's five cells 20.6 x 10.6 m (B); every height C"),
    "entry": ("the three-bay entry: one storey before the middle bays, its flat roof the upper floor's balcony", "S01;S08", "B",
              "S01 draws a block 8.5 x 5.0 m before the five cells with a flight before it (B); the leaf paints a lower front with a door in the middle under the white rail of the upper floor (S08 P0029, crop p29_centre5); three bays C"),
    "fr_towers": ("锦绮楼 and 翡翠楼: two storeys, 歇山 with their gables to the front, yellow with green trim", "S01;S08;S310", "B",
                  "S01's blocks 7.5 x 9.4 m and 7.1 x 10.0 m at the ends of the front range (B); the leaf: two-storey corner blocks, their gables to the water, yellow with green edges (S08 P0029); the names from the plaque list (S310 rec. 8298), which is which C"),
    "hl": ("哕鸾殿: five bays, two storeys, 歇山 in purple-brown tile with green trim", "S05;S08;S01", "A",
           "S05 其北樓宇為噦鸞殿 (樓宇: two storeys, A); the leaf: 歇山, purplish-brown field with green trim, two levels of columns (S08 P0029; Q175); S01's five cells 20.9 x 10.3 m; the bays and heights C"),
    "hl_towers": ("碧云楼 and 紫霞楼: two storeys, 歇山, purple-brown with green trim", "S01;S08;S310", "B", "S01's three-cell blocks 13.1 x 7.4 and 13.6 x 7.9 m (B); the leaf (S08 P0029); the names S310 rec. 8298, which is which C"),
    "qh": ("琼华楼: five bays, two storeys, a double top eave 重檐 in yellow tile with blue trim", "S05;S08;S01", "A",
           "S05 又北為瓊華樓 (A); the leaf: the centre 重檐 with a yellow field and blue edging (S08 P0029, crop ym29_c1b; research/scenes/halls.csv); S01's five cells 22.8 x 11.1 m; heights C"),
    "qh_towers": ("千祥阁 and 万福阁: two storeys, double top eave, purple-brown with green trim", "S01;S08;S310", "B", "S01's four-cell blocks 13.7 x 8.2 and 13.6 x 8.4 m (B); the leaf: the flanking buildings purple-brown with green edging and two tiers of eaves (S08 P0029); names S310, which is which C"),
    "qh_rear": ("a terrace behind 琼华楼 at the upper level", "S01", "C", "S01 draws a plain rectangle 22.8 x 8.3 m behind the five cells, beyond the north line: read as a terrace (C)"),
    "galleries": ("two-storey galleries joining each middle block to its side towers and the side towers of the upper ranges to each other", "S02;S01;S08", "B",
                  "Malone: elevated walks connecting their second stories (S02 pp.92-93, E1850); S01's double lines and the strips of cells down the court's sides (bays about 3.2 m); the leaf's red two-storey galleries along the front; their width 4.0 m and roofs C"),
    "rooms": ("two small rooms behind the front galleries", "S01", "C", "S01's plain squares 4.3 x 3.1 and 4.6 x 3.4 m behind the links; read as stair rooms to the upper floor (C)"),
    "stair_up": (f"a flight on the axis from the front range's platform up to the upper terrace, {LIFT_UP - 0.45:.2f} m", "S01", "B", "S01's cells x 8033-8058 from the terrace's face to the front range's back, 5.3 m on the axis (B): the front range's middle hall is the way through; seventeen steps of 0.15 x 0.30 m C"),
    "strips": ("the galleries out to the two water terraces, single-storey, on stone strips in the water", "S01;S02;S08", "B",
               "S01: double lines on strips about 4.4 m wide from the side towers out and south to the cruciform terraces; Malone: a bridge and two piers to three small terraces (E1850); the leaf's galleries (S08 P0029); single storey and their roofs C"),
    "cross_pav": ("集瑞亭 and 凝祥亭: square pavilions with a lower eave and a cross-ridge 十字脊 roof, blue tile with yellow trim, on stepped cruciform terraces", "S01;S08;S310", "B",
                  "S01: stepped crosses with a 3 x 3 grid (B); the leaf: 重檐 with cross ridges, gables on all four sides, blue with yellow trim (S08 P0029; research/scenes/halls.csv YM29-03); open pavilions (Malone); their size and heights C"),
    "causeway": (f"the causeway from the jut before the entry to the middle water terrace, {LIFT_CW} m above the water", "S01;S08", "B",
                 "S01: two lines about 5.3 m apart, 15 m long, a flight at its north end down from the jut (B); the leaf: white balustrades along it (S08 P0029); its height C"),
    "pailou": ("two archways 坊座 on the causeway: four red posts, three yellow roofs, plaques both faces", "S05;S258;S08", "B",
               "S05 j82:12b 南建坊座二, the south plaques 芝田日永 and 閬苑春深, the north 鳯鳴珠樹 and 鹿夀靈臺 (A); S258: a pailou at the foot of the first stair (E1849, B); the leaf paints a small yellow roof on red posts on the causeway (S08 P0029); places and form C (Q17)"),
    "pav": ("迎薰亭: square, double eaves 重檐, a yellow pyramid roof with a gilt finial, on the square terrace", "S01;S08;S310;S361", "B",
            "the leaf: 重檐 square pyramid, yellow, gilt finial, red columns (S08 P0029); S01: the outer square 7.9 x 6.0 m on a terrace 18.6 x 16.2 m (B); the name S310, S361 (E1852: on a high terrace in the water); taken square 6.6 m, heights C"),
    "pav_deck": ("the square water terrace: white balustrade, a flight each side, three flights to the water for the barge", "S01;S02;S08", "B",
                 "S01: the terrace with a flight east and west and three along the front (B); Malone: marble balustrades and steps for the barge (E1850); the leaf (S08 P0029)"),
    "bronzes": ("two bronze dragons and two bronze phoenixes on stone stands at the water terrace's corners", "S310;S08", "B",
                "S310: 方壶胜境铜龙、凤立样底图, an elevation sheet of the bronze dragons and phoenixes (E1856, title only); the leaf paints four dark bronze figures at the middle terrace's corners (S08 P0029); their form, size and which stands where C"),
    "court": ("the middle court flagged, with bronze vessels and potted flowering trees before 哕鸾殿; the rear court flagged", "S08;S258", "B",
              "the leaf: a grey-paved court with bronze vessels in a row and potted flowering trees (S08 P0029); S258: octagonal paving (E1849); the vessels' and trees' number and places C"),
    "walls": ("the upper terrace's west, east and north walls, red with yellow glazed coping, a gate in the west and east walls", "S01;S08;S310", "C",
              "S01's lines and the two three-cell gates astride the walls (B); the plaque 蕊珠门 (S310 rec. 8298); the colour C (the leaf shows orange-red walls with yellow coping round the courts to the north-east)"),
    "colours": ("red columns and lattice, green-blue beams, white marble, glazed roofs in yellow, purple-brown and blue with green, blue or yellow trim", "S08", "A",
                "the leaf of 1744 (S08 P0029; research/scenes/halls.csv; Q175: Malone's 'golden glazed tile' reads the poem's 十二金堂, the leaf shows several colours)"),
    "heights": ("ground storey 3.6 m, the upper floor 4.4 m above the platform, upper storey 3.2 m, platforms 0.45 m; the roofs by the 举架", "S101", "C",
                "the storeyed_hall class (research/typology/params.json) and the Qing manual's 举架 (S101); no measured drawing or dig gives a height here (Q119)"),
}
V = {k: v[0] for k, v in P.items()}

COL = {
    "lacquer": "#8a2f22", "lacquer_dark": "#532218", "wall": "#8e8a84", "plaster": "#e4ddcf", "glass_lattice": "#2b3137", "sill": "#7d7973",
    "band": "#2e6a6c", "bracket": "#3b7b70", "bandred": "#7d2c20", "platform": "#b7b0a1", "coping": "#d2ccbe", "step": "#d8d3c6", "marble": "#ebe7de",
    "underside": "#4b453d", "fascia": "#3a2a22", "wallred": "#9b3d2c", "wallwhite": "#e8e2d6", "rock": "#8f948f", "pave": "#bdb6a6", "gold": "#c9a245",
    "plaque": "#20406a", "bronze": "#4f5c4e", "brickface": "#8d8a84", "timber": "#7a5a3c", "soil": "#6b5a43",
    "trunk": "#5a4634", "leaf_peach": "#6f8a45", "blossom": "#d8a7b1", "pot": "#4d6e7a",
    "tile_grey": "#5f6469", "ridge_grey": "#4a4e52", "tile_yellow": "#d6a31c", "ridge_yellow": "#a77f16", "tile_green": "#3f8f6a", "ridge_green": "#316f53",
    "tile_purple": "#6c4b55", "ridge_purple": "#4e3540", "tile_blue": "#2f5a96", "ridge_blue": "#23446f",
}

S = Site("F0164")
m = Mesh(COL)
S.m = m
REPORT = {"halls": {}, "joints_on_decks": []}


def plan_scene(px, py):
    lon, lat = plan_to_wgs84(np.array([px], float), np.array([py], float))
    return to_xz(float(lon[0]), float(lat[0]))


ROWS = list(csv.DictReader(open(HERE / "plan_readings.csv", encoding="utf-8")))
PX = {r["name"]: [tuple(map(float, p.split())) for p in r["plan_px"].split(";")] for r in ROWS}


def _scene_mid(names):
    pts = [plan_scene(*p) for n in names for p in PX[n]]
    return np.mean([p[0] for p in pts]), np.mean([p[1] for p in pts])


# the frame's z along the axis S01 draws: from the middle of 琼华楼 and 哕鸾殿 to the middle of the entry, the causeway and 迎薰亭 (F0164's bearing runs 0.6 degrees off it)
_n, _s = _scene_mid(("qh", "hl")), _scene_mid(("entry", "causeway", "pav"))
ROT_BOX = S.rot
S.rot = round(math.atan2(_s[0] - _n[0], _s[1] - _n[1]), 6)
READ = {k: [S.to_local(*plan_scene(*p)) for p in v] for k, v in PX.items()}


def rect(name):
    pts = READ[name]
    xs, zs = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), max(xs), min(zs), max(zs)


def mid(name):
    x0, x1, z0, z1 = rect(name)
    return (x0 + x1) / 2, (z0 + z1) / 2


_ax = [mid(n)[0] for n in ("qh", "hl", "fr", "entry", "causeway", "pav", "stair_up")]
AXIS = float(np.mean(_ax))
REPORT.update({"rot_box": ROT_BOX, "rot_axis": S.rot, "axis_x": round(AXIS, 2), "axis_spread_m": round(float(max(_ax) - min(_ax)), 2), "axis_reads": [round(float(v), 2) for v in _ax]})

# ------------------------------------------------------------ levels: the water (Round 10's level for the body holding W0365), the terraces above it (C)
with open(ROOT / "research/terrain/water_levels.csv", encoding="utf-8") as fh:
    _lv = [r for r in csv.DictReader(fh) if "W0365" in r["water_ids"].split(";")]
WATER_Y = round(float(_lv[0]["level_m_egm2008"]) - DATUM_M - S.pos[1], 3)
Y_LOW = round(WATER_Y + LIFT_LOW, 3)
Y_CW = round(WATER_Y + LIFT_CW, 3)
Y_UP = round(Y_LOW + LIFT_UP, 3)
REPORT.update({"water_y": WATER_Y, "water_m": float(_lv[0]["level_m_egm2008"]), "low_y": Y_LOW, "causeway_y": Y_CW, "up_y": Y_UP})

# raised floors the model draws (its terraces): the flights, the halls and the paving read them as their ground
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
    """The ground of Round 10 under a point (the bed under water): where a terrace's face starts."""
    return S.gy(x, z)


K = HallKit(m, ground)


def compass(dx, dz):
    return ("N" if dz < 0 else "S") + ("W" if dx < 0 else "E")


# ============================================================ parts
def kp_platform(name, hf, hd, y_top):
    c0 = m.world((0, 0, 0))
    for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        w = m.world((sx * hf, 0, sq * hd))
        S.kp(f"{name}_pl_top_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], y_top, w[2]))


def kp_roof(name, H, y_tip=None, half=None):
    """The eave's corner tips and the ridge's ends, named by compass, as hall_parts.roof draws them (Round 18)."""
    CS, CQ, o = H["hf"] - H["e"], H["hd"] - H["e"], H["o"]
    tip = y_tip if y_tip is not None else H["base"] + H["eave"] - o * 0.5
    hs, hq = half if half else (CS + o, CQ + o)
    c0 = m.world((0, 0, 0))
    for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        w = m.world((sx * hs, 0, sq * hq))
        S.kp(f"{name}_eave_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], tip, w[2]))
    along = hs >= hq
    hx, hz = (hs, hq) if along else (hq, hs)
    band = min(0.12 * hz, 0.6) if H["rl"] else 0.0
    rh = {"wd": max(hx - 0.85 * (hz - band), 0.5), "xs": hx - 0.4 * (hz - band)}.get(H["rf"], hx)
    for sx in (-1, 1):
        w = m.world((sx * rh, 0, 0) if along else (0, 0, sx * rh))
        tag = ("W" if w[0] < c0[0] else "E") if along else ("N" if w[2] < c0[2] else "S")
        S.kp(f"{name}_ridge_{tag}", (w[0], H["base"] + H["ridge"], w[2]))


def tower(H, top_db=False):
    """A two-storey tower 楼 (hall_parts.HallKit.hall's second storey: the ground storey, a skirt roof 腰檐, the balcony 平座, the upper storey) with its own top: a single
    eave, or with top_db the double eave 重檐 the leaf paints on 琼华楼's range (a drum above the first top eave, a second roof over it)."""
    hf, hd, base = H["hf"], H["hd"], H["base"]
    plTop, eave, ridge = base + H["pl"], base + H["eave"], base + H["ridge"]
    CS, CQ, o = hf - H["e"], hd - H["e"], H["o"]
    K.platform(hf, hd, plTop, H["foot"], mat=H.get("platform_mat", "platform"))
    feet, gaps = {}, {}
    for side, offs in H.get("st", {}).items():
        for off in offs:
            wdt = H.get("fw", {}).get(side, 2.4)
            f = K.flight(side, off, hf, hd, plTop, wdt)
            if f:
                feet[f"{side}_{off:+.1f}"] = f
                gaps.setdefault(side, []).append((off - wdt / 2 - 0.4, off + wdt / 2 + 0.4))
    if H.get("bal"):
        K.balustrade(hf, hd, plTop, gaps)
    xs = [-CS]
    for w in H["b"]:
        xs.append(xs[-1] + w)
    xs[-1] = CS
    qs = [CQ]
    for w in H["d"]:
        qs.append(qs[-1] - w)
    qs[-1] = -CQ
    RS, RQ, tip = CS + o, CQ + o, eave - o * 0.5
    form = H["rf"]
    ropt = dict(rolled=bool(H["rl"]), ju=H["ju"], tile=H["t"], edge=H.get("te"), gable_mat="lacquer" if form == "xs" else "wall", liftK=H.get("lift", 1.0))
    midy = base + H["mid"]
    K.body(H, CS, CQ, H["pf"], H["pb"], H["ps"], plTop, midy, True, xs, qs)
    if H.get("skirt", True):
        K.skirt(CS + o * 0.8, CQ + o * 0.8, CS - 0.1, CQ - 0.1, midy - o * 0.4, midy + 0.5, H["t"], H.get("te"))
    K.balcony(CS - 0.05, CQ - 0.05, midy + 0.5)
    k = (CS - 0.1) / CS
    m.box(-CS + 0.05, CS - 0.05, midy + 0.35, midy + 0.5, -CQ + 0.05, CQ - 0.05, "timber")  # the upper floor
    K.body(dict(H, dr=[], rr="w"), CS - 0.1, CQ - 0.1, 0, 0, 0, midy + 0.5, eave, False, [x * k for x in xs], [CQ - 0.1, -(CQ - 0.1)])
    if top_db:
        inS, inQ = max(CS - 1.4, CS * 0.6), max(CQ - 1.4, CQ * 0.55)
        yUp = eave + (ridge - eave) * 0.38
        K.skirt(RS, RQ, inS, inQ, tip, eave + 0.8, H["t"], H.get("te"))
        m.box(-inS, inS, eave + 0.2, yUp - 0.6, -inQ, inQ, "lacquer")
        K.bands(inS, inQ, yUp, False, H["dia"], yUp)
        lip = o * 0.75
        K.roof_over(inS + lip, inQ + lip, yUp - lip * 0.5, ridge, form, ropt, o)
        H["_top"] = (inS + lip, inQ + lip, yUp - lip * 0.5)
    else:
        K.roof_over(RS, RQ, tip, ridge, form, ropt, o)
    return feet


def spec(name, x0, x1, z0, z1, base, nb, cls, roof="xs", tile="yellow", edge="green", pl=0.45, col1=3.6, col2=3.2, nd=2, rolled=False, pf=1.2, ju="storeyed_hall",
         storeys=2, rot=0.0, **over):
    """A tower or hall from S01's block (its outline taken as the platform), on the deck at `base`: bays equal across, two spans deep; heights C (P['heights'])."""
    hf, hd = (x1 - x0) / 2, (z1 - z0) / 2
    e = 0.45
    span, dep = 2 * (hf - e), 2 * (hd - e)
    band = 0.42
    o = 1.1
    if storeys == 2:
        midh = round(pl + col1 + band, 2)
        eave = round(midh + 0.5 + col2 + band, 2)
    else:
        midh = None
        eave = round(pl + col1 + band, 2)
    hz = (min(span, dep) if roof != "xs" or span >= dep else min(span, dep)) / 2 + o
    rise = round(0.62 * hz, 2)
    H = dict(hf=hf, hd=hd, base=base, foot=min(bed(a, b) for a in (x0, x1) for b in (z0, z1)) - 0.15 if base - min(bed(a, b) for a in (x0, x1) for b in (z0, z1)) < 0.2 else base - 0.15,
             pl=pl, eave=eave, ridge=round(eave + rise, 2), e=e, o=o, b=[span / nb] * nb, d=[dep / nd] * nd, pf=pf, pb=0.0, ps=0.0, dia=0.36, st={}, bal=0, rf=roof,
             rl=1 if rolled else 0, db=0, ju=JU[ju], t=tile, te=edge, bd="bm", dr=[nb // 2], rr="w", k="hall", x=(x0 + x1) / 2, z=(z0 + z1) / 2, rot=rot, cls=cls, mid=midh)
    H.update(over)
    return H


def draw(name, H, top_db=False, kp=True):
    m.cls = H["cls"]
    m.push(H["x"], 0.0, H["z"], H["rot"])
    if H.get("mid"):
        feet = tower(H, top_db)
    else:
        feet = K.hall(H)
    corners = [m.world((sx * H["hf"], 0, sq * H["hd"])) for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    fw = {k: m.world(v) for k, v in feet.items()}
    if kp:
        kp_platform(name, H["hf"], H["hd"], H["base"] + H["pl"])
        if top_db and "_top" in H:
            kp_roof(name, H, y_tip=H["_top"][2], half=H["_top"][:2])
            kp_roof(name + "_low", H)
        else:
            kp_roof(name, H)
        c0 = m.world((0, 0, 0))
        for sx in (-1, 1):  # the feet of the front corner columns, on the platform (what a painting shows of a colonnade)
            w = m.world((sx * (H["hf"] - H["e"]), 0, H["hd"] - H["e"]))
            S.kp(f"{name}_col_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], H["base"] + H["pl"], w[2]))
    m.pop()
    m.cls = "doc"
    S.FOOTPRINTS.append([(float(c[0]), float(c[2])) for c in corners])
    for k, f in fw.items():
        S.entry(f"{name}_{k}", float(f[0]), float(f[2]), float(f[1]))
    REPORT["halls"][name] = {"frontage_m": round(2 * H["hf"], 2), "depth_m": round(2 * H["hd"], 2), "platform_m": H["pl"], "floor2_m": H.get("mid"), "eave_m": H["eave"],
                             "ridge_m": H["ridge"], "roof": H["rf"] + ("+db" if top_db else ""), "tile": f"{H['t']}/{H.get('te')}", "bays": len(H["b"]), "grade_class": H["cls"],
                             "x": round(H["x"], 2), "z": round(H["z"], 2), "base_y": round(H["base"], 2)}
    return fw


def rail_line(a, b, y, h=0.9, mat="marble"):
    """A stone balustrade 栏杆 from a to b at height y: a sill, posts every 1.8 m with their caps, a top rail, pierced panels."""
    (ax, az), (bx, bz) = a, b
    L = math.hypot(bx - ax, bz - az)
    if L < 0.4:
        return
    m.push(ax, 0, az, math.atan2(bx - ax, bz - az) - math.pi / 2)
    m.box(0, L, y, y + 0.14, -0.08, 0.08, mat)
    m.box(0, L, y + h - 0.12, y + h, -0.09, 0.09, mat)
    n = max(1, round(L / 1.8))
    for k in range(n + 1):
        t = L * k / n
        m.box(t - 0.11, t + 0.11, y, y + h + 0.2, -0.11, 0.11, mat)
    for k in range(n):
        ta, tb = L * k / n + 0.13, L * (k + 1) / n - 0.13
        if tb - ta > 0.3:
            m.box(ta, tb, y + 0.14, y + 0.45, -0.04, 0.04, mat)
            for t in np.linspace(ta + 0.2, tb - 0.2, max(1, round((tb - ta) / 0.45))):
                m.box(t - 0.05, t + 0.05, y + 0.45, y + h - 0.12, -0.05, 0.05, mat)
    m.pop()


def rail_poly(pts, y, closed=True, gaps=(), inset=0.25, h=0.9):
    """A balustrade along a polygon's edges, inset from them, broken where a gap (x, z, half width) lies on an edge."""
    pg = Polygon(pts)
    inner = pg.buffer(-inset, join_style=2)
    if inner.is_empty:
        return
    if inner.geom_type != "Polygon":
        inner = max(inner.geoms, key=lambda g: g.area)
    q = list(inner.exterior.coords)
    segs = list(zip(q[:-1], q[1:])) if closed else list(zip(q[:-2], q[1:-1]))
    for (ax, az), (bx, bz) in segs:
        L = math.hypot(bx - ax, bz - az)
        if L < 0.3:
            continue
        ux, uz = (bx - ax) / L, (bz - az) / L
        cuts = []
        for gx, gz, hw in gaps:
            t = (gx - ax) * ux + (gz - az) * uz
            d = abs(-(gx - ax) * uz + (gz - az) * ux)
            if -hw < t < L + hw and d < 1.6:
                cuts.append((t - hw, t + hw))
        cur = 0.0
        for c0, c1 in sorted(cuts):
            if c0 > cur + 0.3:
                rail_line((ax + ux * cur, az + uz * cur), (ax + ux * c0, az + uz * c0), y, h)
            cur = max(cur, c1)
        if L > cur + 0.3:
            rail_line((ax + ux * cur, az + uz * cur), (bx, bz), y, h)


def terrace(name, poly, top, face="marble", rail=True, gaps=(), deck=True, kind="terrace foot", paved=True):
    """A terrace 台 on an outline: faces from just below the ground (the bed under water) up to its top, a coping, a flagged top, a balustrade; a deck the ways lie on."""
    poly = [tuple(map(float, p)) for p in Polygon(poly).buffer(0).exterior.coords[:-1]]
    if Polygon(poly).exterior.is_ccw:
        poly = poly[::-1]
    bots = S.skirt(poly, top - 0.18, face, step=2.0)
    for (ax, az), (bx, bz) in zip(poly, poly[1:] + poly[:1]):  # the coping: a band 0.18 m round the top
        m.poly([(ax, top - 0.18, az), (bx, top - 0.18, bz), (bx, top, bz), (ax, top, az)], "coping")
    m.flat(poly, top, "pave" if paved else face)
    if rail:
        rail_poly(poly, top, gaps=gaps)
    if deck:
        add_deck(name, poly, top)  # a deck, not a footprint: the ways cross it and meet the model's entries on it (Round 17); the planting keeps off it
    for i, (x, z) in enumerate(poly):
        if bed(x, z) < top - 0.05:
            S.JOINTS.append([f"{name}_{i}", x, bots[i], z, kind])
    return poly


def flight(name, x, z, rot, width, ytop, ybot, entry=True, cheeks=True):
    """A flight 踏跺 from (x, z) at ytop going out along rot (0: +z) down to ybot: steps of about 0.15 x 0.30 m, each block down to the ground below, the side slabs 垂带.
    Returns the foot's middle (x, y, z) in the frame."""
    n = max(1, round((ytop - ybot) / 0.15))
    rise = (ytop - ybot) / n
    run = n * 0.30
    m.push(x, 0, z, rot)
    w = width / 2
    low = min(bed(*m.world((a, 0, b))[::2]) for a in (-w, w) for b in (0.1, run)) - 0.15
    for k in range(n):
        m.box(-w, w, low, ytop - (k + 1) * rise, k * 0.30, (k + 1) * 0.30, "step", skip=("bottom",))
    if cheeks:
        for l0, l1 in ((-w - 0.4, -w), (w, w + 0.4)):
            m.poly([(l0, ytop, 0), (l1, ytop, 0), (l1, ybot + 0.05, run), (l0, ybot + 0.05, run)], "step")
            for lat in (l0, l1):
                m.poly([(lat, ytop, 0), (lat, ybot + 0.05, run), (lat, low, run), (lat, low, 0)], "step")
            m.poly([(l0, ybot + 0.05, run), (l1, ybot + 0.05, run), (l1, low, run), (l0, low, run)], "step")
    foot = m.world((0, ybot, run + 0.2))
    top = m.world((0, ytop, -0.2))
    m.pop()
    S.FOOTPRINTS.append([(float(p[0]), float(p[2])) for p in [_w(x, z, rot, a, b) for a, b in ((-w - 0.4, 0), (w + 0.4, 0), (w + 0.4, run), (-w - 0.4, run))]])
    if entry:
        S.entry(f"{name}_foot", float(foot[0]), float(foot[2]), float(ybot))
        S.entry(f"{name}_top", float(top[0]), float(top[2]), float(ytop))
    return foot


def _w(x, z, rot, a, b):
    c, s = math.cos(rot), math.sin(rot)
    return np.array([x + c * a + s * b, 0.0, z - s * a + c * b])


def gallery2(name, a, b, width, base, cls="fill", tile="green", edge=None, kp=False):
    """A two-storey gallery 楼廊 from a to b (Malone's elevated walks): a narrow tower of 3.2 m bays, both storeys latticed, a rolled roof along it."""
    (ax, az), (bx, bz) = a, b
    L = math.hypot(bx - ax, bz - az)
    rot = math.atan2(-(bz - az), bx - ax)
    nb = max(1, round(L / 3.2))
    H = spec(name, -L / 2, L / 2, -width / 2, width / 2, base, nb, cls, roof="xu", tile=tile, edge=edge, pl=0.2, col1=3.6, col2=3.0, nd=1, rolled=True, pf=0.0, ju="gallery")
    H.update(x=(ax + bx) / 2, z=(az + bz) / 2, rot=rot, e=0.15, o=0.7, dr=[], skirt=False)
    H["ridge"] = round(H["eave"] + 1.3, 2)
    H["foot"] = base - 0.15
    return draw(name, H, kp=kp)


def wall_run(pts, h, name, gaps=(), thick=0.9, body="wallred", cap="yellow", base_h=0.6, ytop=None):
    """A wall along pts, broken where a gap (x, z, half width) lies on it; its feet are joints, its outline a footprint."""
    runs = []
    for (ax, az), (bx, bz) in zip(pts[:-1], pts[1:]):
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
            g = ground(x, z)
            if g <= bed(x, z) + 1e-6:
                S.joint(f"{name}{i}_{k}", x, z, "wall foot", y=g - 0.15)
            else:
                REPORT["joints_on_decks"].append([f"{name}{i}_{k}", round(g - 0.15, 3)])
    return runs


def wall_gate(x, z, rot, name, w=2.6, h=3.8, thick=0.9, body="wallred", cap="yellow"):
    """A gate in a wall 随墙门 (C): two piers, a lintel band, red plank doors with gilt studs, a small roof along the wall; entries both sides."""
    m.push(x, 0, z, rot)
    g = max(K.gy_local(a, b) for a in (-w / 2, w / 2) for b in (-thick, thick))
    y0 = min(K.gy_local(a, b) for a in (-w / 2 - 0.5, w / 2 + 0.5) for b in (-thick, thick)) - 0.15
    for sg in (-1, 1):
        a0, a1 = (w / 2, w / 2 + 0.6) if sg > 0 else (-w / 2 - 0.6, -w / 2)
        m.box(a0, a1, y0, g + h - 0.6, -thick / 2 - 0.08, thick / 2 + 0.08, body)
        m.box(a0, a1, y0, g + 0.5, -thick / 2 - 0.1, thick / 2 + 0.1, "platform")
    m.box(-w / 2, w / 2, g + h - 1.25, g + h - 0.6, -thick / 2 - 0.05, thick / 2 + 0.05, "band")
    m.box(-w / 2, w / 2, y0, g + 0.15, -thick / 2 - 0.2, thick / 2 + 0.2, "step")
    for a0, a1 in ((-w / 2 + 0.05, -0.02), (0.02, w / 2 - 0.05)):
        m.box(a0, a1, g + 0.15, g + h - 1.25, -0.06, 0.06, "lacquer")
        for yy in (g + 0.9, g + 1.6, g + 2.3):
            for sg in (-1, 1):
                for k in range(3):
                    xx = a0 + (a1 - a0) * (k + 0.5) / 3
                    m.box(xx - 0.04, xx + 0.04, yy - 0.04, yy + 0.04, sg * 0.06 - 0.02, sg * 0.06 + 0.02, "gold")
    K.roof(lambda a, b, c: (a, b, c), w / 2 + 1.0, thick / 2 + 0.75, g + h - 0.7, g + h + 0.55, form="xu", rolled=True, ju=JU["gallery"], gable_mat="plaster", gableX=w / 2 + 1.0, tile=cap)
    for sg, tag in ((1, "out"), (-1, "in")):
        p_ = m.world((0, 0, sg * 1.3))
        S.entry(f"{name}_{tag}", float(p_[0]), float(p_[2]), float(ground(float(p_[0]), float(p_[2]))))
    m.pop()


def pave(poly, name, y, step=4.0, mat="pave", clear=True):
    """Flags over an outline at a deck's height (the planting keeps off it: clear)."""
    pg = Polygon(poly).buffer(0)
    for g in ([pg] if pg.geom_type == "Polygon" else list(pg.geoms)):
        m.flat([tuple(p) for p in g.exterior.coords[:-1]], y + 0.03, mat)
    if clear:
        S.CLEAR.append([tuple(map(float, p)) for p in pg.exterior.coords[:-1]])


def censer(x, z, y, name=None):
    """A bronze vessel 香炉 on a stone stand (C): three legs, a round body, a lid and a finial."""
    m.box(x - 0.55, x + 0.55, y, y + 0.5, z - 0.55, z + 0.55, "marble")
    for a in (0.0, 2.094, 4.189):
        lx, lz = x + 0.28 * math.cos(a), z + 0.28 * math.sin(a)
        m.box(lx - 0.05, lx + 0.05, y + 0.5, y + 0.8, lz - 0.05, lz + 0.05, "bronze")
    m.lathe([(0.22, y + 0.75), (0.45, y + 0.9), (0.5, y + 1.25), (0.38, y + 1.42), (0.44, y + 1.47), (0.26, y + 1.75), (0.1, y + 1.95), (0.15, y + 2.05), (0.0, y + 2.3)], 10, "bronze", cx=x, cz=z)
    if name:
        S.kp(name, (x, y + 2.3, z))


def potted_tree(x, z, y, seed):
    """A flowering tree in a glazed pot (the leaf's court; C): the pot, a short trunk, a round crown in blossom."""
    rng = np.random.default_rng(seed)
    m.lathe([(0.0, y), (0.42, y), (0.55, y + 0.55), (0.6, y + 0.62), (0.0, y + 0.62)], 10, "pot", cx=x, cz=z)
    m.box(x - 0.07, x + 0.07, y + 0.6, y + 1.5, z - 0.07, z + 0.07, "trunk")
    r = rng.uniform(0.75, 0.95)
    m.lathe([(0.0, y + 1.25), (r * 0.8, y + 1.45), (r, y + 1.85), (r * 0.75, y + 2.3), (0.0, y + 2.5)], 9, "blossom", cx=x, cz=z)


def bronze_bird(x, z, y, face, name):
    """A bronze phoenix 铜凤 on a stone stand (C form: a body, a raised neck and crest, a long tail; E1856 names them, the leaf paints dark bronze birds)."""
    m.push(x, 0, z, face)
    m.box(-0.55, 0.55, y, y + 0.9, -0.55, 0.55, "marble")
    m.box(-0.65, 0.65, y + 0.9, y + 1.05, -0.65, 0.65, "marble")
    b = y + 1.05
    m.box(-0.06, 0.06, b, b + 0.45, -0.06, 0.06, "bronze")
    m.frustum([(-0.2, -0.45), (0.2, -0.45), (0.22, 0.25), (-0.22, 0.25)], [(-0.14, -0.35), (0.14, -0.35), (0.16, 0.2), (-0.16, 0.2)], b + 0.4, b + 0.8, "bronze")
    m.frustum([(-0.08, 0.1), (0.08, 0.1), (0.08, 0.28), (-0.08, 0.28)], [(-0.06, 0.25), (0.06, 0.25), (0.06, 0.4), (-0.06, 0.4)], b + 0.75, b + 1.45, "bronze")
    m.box(-0.08, 0.08, b + 1.4, b + 1.58, 0.22, 0.55, "bronze")
    m.poly([(0, b + 1.55, 0.3), (0, b + 1.85, 0.2), (0, b + 1.6, 0.1)], "bronze")
    m.poly([(-0.15, b + 0.7, -0.4), (0.15, b + 0.7, -0.4), (0.25, b + 0.2, -1.15), (-0.25, b + 0.2, -1.15)], "bronze")
    m.pop()
    S.kp(f"{name}_top", _w(x, z, face, 0, 0.2) + np.array([0, b + 1.85, 0]))


def bronze_dragon(x, z, y, face, name):
    """A bronze dragon 铜龙 rearing on a stone stand (C form: a coiled body, a raised neck, a head; E1856)."""
    m.push(x, 0, z, face)
    m.box(-0.55, 0.55, y, y + 0.9, -0.55, 0.55, "marble")
    m.box(-0.65, 0.65, y + 0.9, y + 1.05, -0.65, 0.65, "marble")
    b = y + 1.05
    m.lathe([(0.0, b), (0.42, b + 0.02), (0.45, b + 0.25), (0.3, b + 0.35), (0.0, b + 0.36)], 9, "bronze")
    pts = [(0.0, 0.1, -0.15), (0.05, 0.6, 0.0), (-0.05, 1.0, 0.12), (0.0, 1.35, 0.3)]
    for (x0_, y0_, z0_), (x1_, y1_, z1_) in zip(pts[:-1], pts[1:]):
        r = 0.16
        m.frustum([(x0_ - r, z0_ - r), (x0_ + r, z0_ - r), (x0_ + r, z0_ + r), (x0_ - r, z0_ + r)], [(x1_ - r * 0.85, z1_ - r * 0.85), (x1_ + r * 0.85, z1_ - r * 0.85), (x1_ + r * 0.85, z1_ + r * 0.85), (x1_ - r * 0.85, z1_ + r * 0.85)], b + y0_ + 0.3, b + y1_ + 0.3, "bronze")
    m.box(-0.14, 0.14, b + 1.6, b + 1.85, 0.25, 0.7, "bronze")
    for sx in (-1, 1):
        m.poly([(sx * 0.08, b + 1.85, 0.35), (sx * 0.12, b + 2.15, 0.15), (sx * 0.1, b + 1.85, 0.25)], "bronze")
    m.pop()
    S.kp(f"{name}_top", _w(x, z, face, 0, 0.4) + np.array([0, b + 2.15, 0]))


def pailou(x, z, rot, w, y, name, plaque_s=True):
    """A timber archway 牌坊 across the causeway (C form after the leaf's small yellow roof on red posts): four posts on stone drums with their braces, beams and a
    plaque each face, three roofs (the middle higher) in yellow with green trim."""
    m.push(x, 0, z, rot)
    xs = [-w / 2, -w / 6, w / 6, w / 2]
    hm, hs = 5.0, 4.0
    for k, px_ in enumerate(xs):
        top = hm if k in (1, 2) else hs
        m.box(px_ - 0.32, px_ + 0.32, y - 0.15, y + 0.75, -0.42, 0.42, "marble")  # 夹杆石
        m.prism([(px_ + 0.17 * math.cos(a), 0.17 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]], y, y + top, "lacquer", top=False)
        for sg in (-1, 1):  # the raking braces 戗柱
            m.poly([(px_ - 0.05, y + 0.7, sg * 0.42), (px_ + 0.05, y + 0.7, sg * 0.42), (px_ + 0.05, y + 2.6, sg * 0.08), (px_ - 0.05, y + 2.6, sg * 0.08)], "lacquer")
    for (a0, a1, top) in ((xs[0], xs[1], hs), (xs[1], xs[2], hm), (xs[2], xs[3], hs)):
        m.box(a0, a1, y + top - 1.1, y + top - 0.75, -0.14, 0.14, "band")
        m.box(a0, a1, y + top - 0.6, y + top - 0.15, -0.16, 0.16, "band")
        m.box(a0, a1, y + top - 0.15, y + top + 0.05, -0.2, 0.2, "bracket")
        m.push((a0 + a1) / 2, 0, 0)
        K.roof(lambda a, b, c: (a, b, c), (a1 - a0) / 2 + 0.55, 0.85, y + top + 0.05, y + top + 0.95, form="wd", ju=[0.5, 0.7], tile="yellow", edge="green")
        m.pop()
    for sg in (1, -1):
        m.box(-0.75, 0.75, y + hm - 0.75, y + hm - 0.15, sg * 0.17 - 0.02, sg * 0.17 + 0.02, "gold")
        m.box(-0.62, 0.62, y + hm - 0.68, y + hm - 0.22, sg * 0.19 - 0.01, sg * 0.19 + 0.01, "plaque")
    m.pop()
    S.kp(f"{name}_top", _w(x, z, rot, 0, 0) + np.array([0, y + hm + 0.95, 0]))
    for k, px_ in enumerate((xs[0], xs[3])):
        p_ = _w(x, z, rot, px_, 0)
        S.FOOTPRINTS.append([(p_[0] - 0.35, p_[2] - 0.45), (p_[0] + 0.35, p_[2] - 0.45), (p_[0] + 0.35, p_[2] + 0.45), (p_[0] - 0.35, p_[2] + 0.45)])


def square_pav(name, cx, cz, base, side, cls, tile="yellow", edge=None):
    """迎薰亭: a square pavilion with double eaves 重檐 and a pyramid roof 攒尖 with a gilt finial (the leaf), three bays a side, open."""
    m.cls = cls
    m.push(cx, 0, cz)
    hs = side / 2
    pl, e = 0.45, 0.45
    K.platform(hs, hs, base + pl, base - 0.15)
    CS = hs - e
    xs = [-CS, -CS / 3, CS / 3, CS]
    col_top = base + pl + 3.4
    K.columns(xs, xs, CS, CS, base + pl, col_top, 0.34)
    K.columns([-CS * 0.45, CS * 0.45], [-CS * 0.45, CS * 0.45], CS * 0.45, CS * 0.45, base + pl, col_top + 1.6, 0.32)  # the inner columns that carry the upper eave
    K.bands(CS, CS, col_top + 0.42, False, 0.34, col_top + 0.42)
    for a0, a1 in zip(xs[:-1], xs[1:]):  # the hanging fascia 倒挂楣子 and low rails 坐凳 of an open pavilion
        for sg in (1, -1):
            m.box(a0 + 0.17, a1 - 0.17, col_top - 0.5, col_top - 0.08, sg * CS - 0.03, sg * CS + 0.03, "lacquer")
            m.box(sg * CS - 0.03, sg * CS + 0.03, col_top - 0.5, col_top - 0.08, a0 + 0.17, a1 - 0.17, "lacquer")
    for a0, a1 in ((xs[0], xs[1]), (xs[2], xs[3])):
        for sg in (1, -1):
            m.box(a0 + 0.17, a1 - 0.17, base + pl, base + pl + 0.5, sg * CS - 0.15, sg * CS + 0.15, "lacquer")
            m.box(sg * CS - 0.15, sg * CS + 0.15, base + pl, base + pl + 0.5, a0 + 0.17, a1 - 0.17, "lacquer")
    m.poly([(-CS, col_top, CS), (CS, col_top, CS), (CS, col_top, -CS), (-CS, col_top, -CS)], "underside")
    o = 1.0
    y_low = col_top + 0.42 - o * 0.4
    inS = CS * 0.45 + 0.1
    K.skirt(CS + o, CS + o, inS, inS, y_low, col_top + 1.25, tile, edge)
    yUp = col_top + 1.6 + 0.42
    m.box(-inS, inS, col_top + 1.0, yUp - 0.42, -inS, inS, "lacquer")
    K.bands(inS, inS, yUp, False, 0.3, yUp)
    lip = 0.8
    ridge = yUp + 2.9
    K.pyramid(inS + lip, inS + lip, yUp - lip * 0.4, ridge, tile=tile, edge=edge)
    m.lathe([(0.0, ridge + 0.3), (0.26, ridge + 0.45), (0.3, ridge + 0.75), (0.16, ridge + 0.95), (0.22, ridge + 1.15), (0.0, ridge + 1.55)], 10, "gold")  # the gilt finial 宝顶
    c0 = m.world((0, 0, 0))
    for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        w = m.world((sx * (CS + o), 0, sq * (CS + o)))
        S.kp(f"{name}_eave_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], y_low, w[2]))
        w = m.world((sx * CS, 0, sq * CS))
        S.kp(f"{name}_col_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], base + pl, w[2]))
    S.kp(f"{name}_finial", m.world((0, ridge + 1.55, 0)))
    m.pop()
    m.cls = "doc"
    S.FOOTPRINTS.append([(cx - hs, cz - hs), (cx + hs, cz - hs), (cx + hs, cz + hs), (cx - hs, cz + hs)])
    REPORT["halls"][name] = {"frontage_m": side, "depth_m": side, "platform_m": pl, "eave_m": round(y_low - base, 2), "ridge_m": round(ridge - base, 2), "finial_m": round(ridge + 1.55 - base, 2),
                             "roof": "cj+db", "tile": tile, "grade_class": cls, "x": round(cx, 2), "z": round(cz, 2), "base_y": round(base, 2)}


def cross_pav(name, cx, cz, base, side, cls, tile="blue", edge="yellow"):
    """集瑞亭 / 凝祥亭: a square pavilion with a lower eave all round and a cross-ridge roof 十字脊 above (two 歇山 crossing: a gable on every side), open, red columns."""
    m.cls = cls
    m.push(cx, 0, cz)
    hs = side / 2
    pl, e = 0.4, 0.4
    K.platform(hs, hs, base + pl, base - 0.15)
    CS = hs - e
    xs = [-CS, -CS / 3, CS / 3, CS]
    col_top = base + pl + 3.2
    K.columns(xs, xs, CS, CS, base + pl, col_top, 0.32)
    K.bands(CS, CS, col_top + 0.42, False, 0.32, col_top + 0.42)
    for a0, a1 in zip(xs[:-1], xs[1:]):
        for sg in (1, -1):
            m.box(a0 + 0.16, a1 - 0.16, col_top - 0.5, col_top - 0.08, sg * CS - 0.03, sg * CS + 0.03, "lacquer")
            m.box(sg * CS - 0.03, sg * CS + 0.03, col_top - 0.5, col_top - 0.08, a0 + 0.16, a1 - 0.16, "lacquer")
            if (a0, a1) != (xs[1], xs[2]):
                m.box(a0 + 0.16, a1 - 0.16, base + pl, base + pl + 0.5, sg * CS - 0.14, sg * CS + 0.14, "lacquer")
                m.box(sg * CS - 0.14, sg * CS + 0.14, base + pl, base + pl + 0.5, a0 + 0.16, a1 - 0.16, "lacquer")
    m.poly([(-CS, col_top, CS), (CS, col_top, CS), (CS, col_top, -CS), (-CS, col_top, -CS)], "underside")
    o = 0.95
    y_low = col_top + 0.42 - o * 0.4
    inS = CS * 0.62
    K.skirt(CS + o, CS + o, inS, inS, y_low, col_top + 1.2, tile, edge)
    yUp = col_top + 1.5 + 0.42
    m.box(-inS, inS, col_top + 0.9, yUp - 0.42, -inS, inS, "lacquer")
    K.bands(inS, inS, yUp, False, 0.3, yUp)
    lip = 0.75
    ridge = yUp + 2.4
    for P_ in ((lambda a, b, c: (a, b, c)), (lambda a, b, c: (c, b, -a))):
        K.roof(P_, inS + lip, (inS + lip) * 0.62, yUp - lip * 0.4, ridge, form="xs", ju=JU["pavilion"], tile=tile, edge=edge, gable_mat="lacquer")
    m.lathe([(0.0, ridge + 0.2), (0.2, ridge + 0.3), (0.22, ridge + 0.55), (0.0, ridge + 0.85)], 8, "gold")
    c0 = m.world((0, 0, 0))
    for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        w = m.world((sx * (CS + o), 0, sq * (CS + o)))
        S.kp(f"{name}_eave_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], y_low, w[2]))
    S.kp(f"{name}_top", m.world((0, ridge + 0.85, 0)))
    m.pop()
    m.cls = "doc"
    S.FOOTPRINTS.append([(cx - hs, cz - hs), (cx + hs, cz - hs), (cx + hs, cz + hs), (cx - hs, cz + hs)])
    REPORT["halls"][name] = {"frontage_m": side, "depth_m": side, "platform_m": pl, "eave_m": round(y_low - base, 2), "ridge_m": round(ridge - base, 2), "roof": "xs x2 (十字脊)+lower eave",
                             "tile": f"{tile}/{edge}", "grade_class": cls, "x": round(cx, 2), "z": round(cz, 2), "base_y": round(base, 2)}


def cross_outline(cx, cz, a, b):
    """A stepped cross 十字 terrace (S01's outline): a square of half-side a, and an arm of half-width b on each side stepping out to a + 0.55 (a - b) + 0.6."""
    ext = a + 0.55 * (a - b) + 0.6
    pg = Polygon([(-a, -a), (a, -a), (a, a), (-a, a)]).union(Polygon([(-b, -ext), (b, -ext), (b, ext), (-b, ext)])).union(Polygon([(-ext, -b), (ext, -b), (ext, b), (-ext, b)]))
    return [(cx + float(x), cz + float(z)) for x, z in pg.exterior.coords[:-1]]


# ============================================================ the lower terrace on the water (S01's outline, its bastions) and the upper terrace behind it
m.cls = "doc"
low_pts = READ["low_deck"]
up_pts = READ["up_deck"]
low_pg = Polygon(low_pts).buffer(0)
up_pg = Polygon(up_pts).buffer(0)
z_face = max(p[1] for p in up_pts)  # the upper terrace's south face (S01's line y 1088-1084)
fx0, fx1, fz0, fz1 = rect("fr")
sx0, sx1, sz0, sz1 = rect("stair_up")
# the upper terrace: brick faces, its flagged top; a balustrade along its south face (the leaf), broken at the head of the stair on the axis. S01's face runs 2.6 degrees
# off the axis frame (3.6 m over the terrace's width): at the axis it stands 5.3 m from the front range's back, room for the flight S01's cells draw there
stair_w = sx1 - sx0
up_poly = terrace("up_terrace", up_pts, Y_UP, face="brickface", rail=False)
(ax_, az_), (bx_, bz_) = up_pts[5], up_pts[4]  # the south face, west to east (S01 y 1088 to 1084)
L_ = math.hypot(bx_ - ax_, bz_ - az_)
ux_, uz_ = (bx_ - ax_) / L_, (bz_ - az_) / L_
nx_, nz_ = (uz_, -ux_) if -ux_ < 0 else (-uz_, ux_)  # the normal into the terrace (north)
_pf = lambda t: (ax_ + ux_ * t + nx_ * 0.25, az_ + uz_ * t + nz_ * 0.25)
_tc = (AXIS - ax_) * ux_ + (sz0 - az_) * uz_
_hw = stair_w / 2 + 0.4
rail_line(_pf(0.5), _pf(_tc - _hw), Y_UP)
rail_line(_pf(_tc + _hw), _pf(L_ - 0.5), Y_UP)
Z_FACE_AXIS = az_ + uz_ * _tc
REPORT["stair_gap_m"] = round(fz0 - Z_FACE_AXIS, 2)
# the lower terrace: white marble faces, the balustrade along its water edges (not along the upper terrace's face, not where the strips and the causeway meet it)
low_poly = terrace("low_terrace", low_pts, Y_LOW, face="marble", rail=False)
cw = rect("causeway")
strip_W, strip_E = READ["strip_W"], READ["strip_E"]
# the balustrade along the water edges: walk the outline inset by 0.25 m and drop the runs along the upper face and across the strips and the causeway
_inner = Polygon(low_poly).buffer(-0.25, join_style=2)
_iq = list(_inner.exterior.coords)
_cut = [Polygon(strip_W).buffer(0.6), Polygon(strip_E).buffer(0.6), Polygon([(cw[0] - 0.4, cw[2] - 3.0), (cw[1] + 0.4, cw[2] - 3.0), (cw[1] + 0.4, cw[2] + 1.0), (cw[0] - 0.4, cw[2] + 1.0)])]
for a, b in zip(_iq[:-1], _iq[1:]):
    if max(a[1], b[1]) < z_face + 1.0:
        continue
    seg = LineString([a, b])
    for c in _cut:
        seg = seg.difference(c)
    for part in ([seg] if seg.geom_type == "LineString" else list(getattr(seg, "geoms", []))):
        if part.is_empty or part.length < 0.4:
            continue
        cs = list(part.coords)
        rail_line(cs[0], cs[-1], Y_LOW)
# the flight on the axis from the front range's platform up to the upper terrace (S01's cells, from the terrace's face to the front range's back; 17 steps C)
f_up = flight("stair_up", AXIS, sz0, 0.0, stair_w - 0.9, Y_UP, Y_LOW + 0.45)
S.kp("stair_up_foot_C", (float(f_up[0]), Y_LOW, float(f_up[2])))

# ============================================================ the strips, the galleries out to the cross terraces, the cross terraces and their pavilions
for side, st, cr, gal in (("W", strip_W, "cross_W", "gal_out_W"), ("E", strip_E, "cross_E", "gal_out_E")):
    terrace(f"strip_{side}", st, Y_LOW, face="marble", rail=False)
    # the cross terrace: S01's stepped cross, its middle at S01's point; its arms 0.62 times its square (C)
    cxx, czz = READ[cr][0]
    a = 3.6  # the stepped cross about 10 m across, as S01 draws it (9.5-10 m; C)
    pts = cross_outline(cxx, czz, a, a * 0.55)
    terrace(f"cross_{side}", pts, Y_CW, face="marble", rail=True, gaps=[])
    # the gallery on the strip from the side tower out and down to the cross terrace (single storey: C); its last run steps down to the cross terrace
    g = READ[gal]
    m.cls = "fill"
    K.gallery([g[0], g[1]], 3.0, lambda x, z: Y_LOW, eave=3.1, ridge=4.3, wall_side=0, tile="green")
    tail = (g[2][0], czz - a * 1.1 if g[2][1] > g[1][1] else czz + a * 1.1)
    K.gallery([g[1], (g[1][0], (g[1][1] + tail[1]) / 2)], 3.0, lambda x, z: Y_LOW, eave=3.1, ridge=4.3, wall_side=0, tile="green")
    m.cls = "doc"
    # a flight from the strip's end down to the cross terrace
    zs_ = [p[1] for p in st]
    f_ = flight(f"strip_{side}_down", g[2][0], max(zs_), 0.0, 2.6, Y_LOW, Y_CW, entry=True)
    cross_pav(f"pav_{side}", cxx, czz, Y_CW, 6.0, "doc")

# ============================================================ the causeway, its archways, the middle water terrace, 迎薰亭, the bronzes, the steps to the water
cw_x0, cw_x1, cw_z0, cw_z1 = cw
ef = rect("entry_flight")
# the jut before the entry is the lower terrace's (S01); the flight down from it to the causeway (S01's cells)
f_cw = flight("entry_flight", AXIS, ef[2], 0.0, ef[1] - ef[0] - 0.8, Y_LOW, Y_CW)
pd = rect("pav_deck")
cw_poly = [(AXIS - (cw_x1 - cw_x0) / 2, float(f_cw[2]) - 0.3), (AXIS + (cw_x1 - cw_x0) / 2, float(f_cw[2]) - 0.3), (AXIS + (cw_x1 - cw_x0) / 2, pd[2] + 0.3), (AXIS - (cw_x1 - cw_x0) / 2, pd[2] + 0.3)]
terrace("causeway", cw_poly, Y_CW, face="marble", rail=False)
for sgn in (-1, 1):
    xe = AXIS + sgn * ((cw_x1 - cw_x0) / 2 - 0.25)
    rail_line((xe, float(f_cw[2]) - 0.1), (xe, pd[2] - 0.1), Y_CW)
REPORT["causeway_m"] = {"width": round(cw_x1 - cw_x0, 2), "length": round(pd[2] - float(f_cw[2]), 2)}
# the two archways 坊座 (S05: two, south of the front building; places C: at the causeway's two ends, the leaf's small yellow roof)
m.cls = "fill"
for k, zz in enumerate((float(f_cw[2]) + 1.6, pd[2] - 1.6)):
    pailou(AXIS, zz, 0.0, (cw_x1 - cw_x0) - 0.3, Y_CW, f"pailou_{'N' if k == 0 else 'S'}")
m.cls = "doc"
# the middle terrace (S01's square), its balustrade broken for the causeway and the flights
pd_poly = [(pd[0], pd[2]), (pd[1], pd[2]), (pd[1], pd[3]), (pd[0], pd[3])]
fW, fE = rect("pav_fl_W"), rect("pav_fl_E")
fS = READ["pav_fl_S"]
front_fl = [((fS[0][0] + fS[1][0]) / 2, abs(fS[1][0] - fS[0][0])), ((fS[2][0] + fS[3][0]) / 2, abs(fS[3][0] - fS[2][0])), ((fS[4][0] + fS[5][0]) / 2, abs(fS[5][0] - fS[4][0]))]
gaps = [(AXIS, pd[2], (cw_x1 - cw_x0) / 2 + 0.2), (pd[0], (fW[2] + fW[3]) / 2, 1.6), (pd[1], (fE[2] + fE[3]) / 2, 1.6)] + [(x, pd[3], w / 2 + 0.3) for x, w in front_fl]
terrace("pav_terrace", pd_poly, Y_CW, face="marble", rail=True, gaps=gaps)
for nm, (x, w) in zip(("W", "C", "E"), front_fl):  # three flights to the water for the barge (Malone): down to just above the water
    flight(f"pav_fl_S{nm}", x, pd[3], 0.0, max(w - 0.4, 2.0), Y_CW, WATER_Y + 0.15, entry=(nm == "C"))
for nm, rr, xx in (("W", fW, pd[0]), ("E", fE, pd[1])):
    flight(f"pav_fl_{nm}", xx, (rr[2] + rr[3]) / 2, -math.pi / 2 if nm == "W" else math.pi / 2, 2.6, Y_CW, WATER_Y + 0.15, entry=False)
pv = rect("pav")
PAV_X, PAV_Z = AXIS, (pv[2] + pv[3]) / 2
square_pav("yingxun", PAV_X, PAV_Z, Y_CW, 6.6, "doc")
m.cls = "fill"
inset = 1.3
bronze_dragon(pd[0] + inset, pd[3] - inset, Y_CW, 0.0, "dragon_SW")
bronze_dragon(pd[1] - inset, pd[3] - inset, Y_CW, 0.0, "dragon_SE")
bronze_bird(pd[0] + inset, pd[2] + inset + 1.2, Y_CW, 0.0, "phoenix_NW")
bronze_bird(pd[1] - inset, pd[2] + inset + 1.2, Y_CW, 0.0, "phoenix_NE")
for x_, z_ in ((pd[0] + inset, pd[3] - inset), (pd[1] - inset, pd[3] - inset), (pd[0] + inset, pd[2] + inset + 1.2), (pd[1] - inset, pd[2] + inset + 1.2)):
    S.FOOTPRINTS.append([(x_ - 0.7, z_ - 0.7), (x_ + 0.7, z_ - 0.7), (x_ + 0.7, z_ + 0.7), (x_ - 0.7, z_ + 0.7)])
m.cls = "doc"

# ============================================================ the front range: 宜春殿, the entry, the side towers, the links, the small rooms
Hf = spec("fr", fx0, fx1, fz0, fz1, Y_LOW, 5, "doc", tile="yellow", edge="green", pl=0.45)
Hf["x"] = AXIS
Hf["st"] = {}  # its back is the stair's foot
Hf["rr"] = "d"
draw("fr", Hf)
REPORT["fr_s01_m"] = [round(fx1 - fx0, 2), round(fz1 - fz0, 2)]
# the three-bay entry: one storey, its flat roof the balcony of the upper floor (the leaf), three bays C
ex0, ex1, ez0, ez1 = rect("entry")
ew = ex1 - ex0
m.cls = "doc"
m.push(AXIS, 0, (fz1 + ez1) / 2)
hd_e = (ez1 - fz1) / 2 + 0.4
K.platform(ew / 2, hd_e, Y_LOW + Hf["pl"], Y_LOW - 0.15)
xs_e = [-ew / 2 + 0.4, -ew / 6, ew / 6, ew / 2 - 0.4]
y_e0, y_e1 = Y_LOW + Hf["pl"], Y_LOW + Hf["mid"]
K.body(dict(Hf, dr=[1], k="hall", bd="bm"), ew / 2 - 0.4, hd_e - 0.4, 0.0, 0.0, 0.0, y_e0, y_e1, True, xs_e, [hd_e - 0.4, -(hd_e - 0.4)])
m.box(-ew / 2, ew / 2, y_e1 - 0.05, y_e1 + 0.5, -hd_e, hd_e, "band")
m.box(-ew / 2 - 0.1, ew / 2 + 0.1, y_e1 + 0.35, y_e1 + 0.5, -hd_e - 0.1, hd_e + 0.1, "timber")
K.balcony(ew / 2, hd_e, y_e1 + 0.5)
m.box(-1.3, 1.3, y_e1 - 0.75, y_e1 - 0.05, hd_e - 0.02, hd_e + 0.06, "gold")  # the plaque 方壶胜境 (Qianlong's hand, S05: 額為皇上御書) over the door (board C)
m.box(-1.15, 1.15, y_e1 - 0.68, y_e1 - 0.12, hd_e + 0.06, hd_e + 0.08, "plaque")
m.pop()
S.FOOTPRINTS.append([(AXIS - ew / 2, fz1), (AXIS + ew / 2, fz1), (AXIS + ew / 2, fz1 + 2 * hd_e), (AXIS - ew / 2, fz1 + 2 * hd_e)])
S.kp("entry_col_SW", (AXIS - ew / 2 + 0.4, y_e0, fz1 + 2 * hd_e - 0.4))
S.kp("entry_col_SE", (AXIS + ew / 2 - 0.4, y_e0, fz1 + 2 * hd_e - 0.4))
S.entry("entry_door", AXIS, fz1 + 2 * hd_e + 0.3, Y_LOW)
REPORT["halls"]["entry"] = {"frontage_m": round(ew, 2), "depth_m": round(2 * hd_e, 2), "eave_m": round(Hf["mid"], 2), "roof": "flat (balcony)", "grade_class": "doc"}
for side, nm in (("W", "fr_W"), ("E", "fr_E")):
    x0, x1, z0, z1 = rect(nm)
    H = spec(nm, x0, x1, z0, z1, Y_LOW, 3, "doc", tile="yellow", edge="green", pl=0.45, nd=3)
    H["st"] = {"back": [0.0]}
    draw(nm, H)
for side, nm, a_, b_ in (("W", "fr_link_W", rect("fr_W")[1], fx0), ("E", "fr_link_E", fx1, rect("fr_E")[0])):
    zl = READ[nm][0][1]
    gallery2(nm, (a_ - 0.3, zl), (b_ + 0.3, zl), 4.0, Y_LOW)
m.cls = "fill"
for nm in ("fr_room_W", "fr_room_E"):
    x0, x1, z0, z1 = rect(nm)
    H = spec(nm, x0, x1, z0, z1, Y_LOW, 1, "fill", roof="xs", tile="green", edge=None, pl=0.3, storeys=1, nd=1, rolled=True, pf=0.0, ju="small_house")
    H["dr"] = []
    H["rr"] = "d"
    draw(nm, H, kp=False)
m.cls = "doc"

# ============================================================ the upper terrace: 哕鸾殿's range, 琼华楼's range, the galleries, the court
hx0, hx1, hz0, hz1 = rect("hl")
Hh = spec("hl", hx0, hx1, hz0, hz1, Y_UP, 5, "doc", tile="purple", edge="green", pl=0.45)
Hh["x"] = AXIS
Hh["st"] = {"front": [0.0], "back": [0.0]}
draw("hl", Hh)
for nm in ("hl_W", "hl_E"):
    x0, x1, z0, z1 = rect(nm)
    H = spec(nm, x0, x1, z0, z1, Y_UP, 3, "doc", tile="purple", edge="green", pl=0.45)
    H["st"] = {"front": [0.0]}
    draw(nm, H)
for nm, a_, b_ in (("hl_link_W", rect("hl_W")[1], hx0), ("hl_link_E", hx1, rect("hl_E")[0])):
    zl = READ[nm][0][1]
    gallery2(nm, (a_ - 0.3, zl), (b_ + 0.3, zl), 4.0, Y_UP)
# the rear terrace behind 琼华楼 (S01's rectangle; C) at the upper level, and 琼华楼's range
qr = rect("qh_rear")
terrace("qh_rear", [(qr[0], qr[2]), (qr[1], qr[2]), (qr[1], qr[3] + 1.0), (qr[0], qr[3] + 1.0)], Y_UP, face="brickface", rail=True, gaps=[])
qx0, qx1, qz0, qz1 = rect("qh")
Hq = spec("qh", qx0, qx1, qz0, qz1, Y_UP, 5, "doc", tile="yellow", edge="blue", pl=0.6)
Hq["x"] = AXIS
Hq["st"] = {"front": [0.0]}
Hq["ridge"] = round(Hq["ridge"] + 1.6, 2)
draw("qh", Hq, top_db=True)
for nm in ("qh_W", "qh_E"):
    x0, x1, z0, z1 = rect(nm)
    H = spec(nm, x0, x1, z0, z1, Y_UP, 4, "doc", tile="purple", edge="green", pl=0.45)
    H["st"] = {"front": [0.0]}
    H["ridge"] = round(H["ridge"] + 1.0, 2)
    draw(nm, H, top_db=True)
for nm, a_, b_ in (("qh_link_W", rect("qh_W")[1], qx0), ("qh_link_E", qx1, rect("qh_E")[0])):
    zl = READ[nm][0][1]
    gallery2(nm, (a_ - 0.3, zl), (b_ + 0.3, zl), 4.0, Y_UP)
for nm, top_, low_ in (("gal_W", "qh_W", "hl_W"), ("gal_E", "qh_E", "hl_E")):
    gx = READ[nm][0][0]
    gallery2(nm, (gx, rect(top_)[3] - 0.3), (gx, rect(low_)[2] + 0.3), 4.0, Y_UP)
# the courts: flagged (the leaf; S258's octagonal paving not drawn), the vessels and the potted trees before 哕鸾殿 (the leaf; C)
up_in = Polygon(up_poly).buffer(-0.5, join_style=2)
pave([tuple(p) for p in up_in.exterior.coords[:-1]], "up_court", Y_UP)
pave([tuple(p) for p in Polygon(low_poly).buffer(-0.3, join_style=2).exterior.coords[:-1]], "low_court", Y_LOW)
m.cls = "fill"
zc = (hz1 + Z_FACE_AXIS) / 2
for k, dx in enumerate((-9.0, -3.0, 3.0, 9.0)):
    censer(AXIS + dx, zc - 1.0, Y_UP, f"vessel_{k}_top" if k in (0, 3) else None)
for k, dx in enumerate((-14.0, -6.0, 6.0, 14.0)):
    potted_tree(AXIS + dx, zc + 2.2, Y_UP, 240 + k)
m.cls = "doc"

# ============================================================ the walls of the upper terrace and their two gates (S01; C)
W0 = up_pts
xw = sum(p[0] for p in READ["gate_W"]) / 2
zw_ = sum(p[1] for p in READ["gate_W"]) / 2
xe = sum(p[0] for p in READ["gate_E"]) / 2
ze_ = sum(p[1] for p in READ["gate_E"]) / 2
nw, ne, se, sw = W0[0], W0[3], W0[4], W0[5]
wall_h = 3.6
wall_run([(sw[0] + 0.45, sw[1] - 0.6), (nw[0] + 0.45, nw[1] + 0.45)], wall_h, "wall_W", gaps=[(nw[0] + 0.45, zw_, 1.9)], ytop=Y_UP + wall_h)
wall_run([(se[0] - 0.45, se[1] - 0.6), (ne[0] - 0.45, ne[1] + 0.45)], wall_h, "wall_E", gaps=[(ne[0] - 0.45, ze_, 1.9)], ytop=Y_UP + wall_h)
wall_run([(nw[0] + 0.45, nw[1] + 0.45), (qx0 - 0.2, nw[1] + 0.45 + (W0[1][1] - nw[1]) * (qx0 - nw[0]) / (W0[1][0] - nw[0]))], wall_h, "wall_NW", ytop=Y_UP + wall_h)
wall_run([(qx1 + 0.2, ne[1] + 0.45 - (ne[1] - W0[2][1]) * (ne[0] - qx1) / (ne[0] - W0[2][0])), (ne[0] - 0.45, ne[1] + 0.45)], wall_h, "wall_NE", ytop=Y_UP + wall_h)
wall_gate(nw[0] + 0.45, zw_, math.pi / 2, "gate_W", body="wallred")
wall_gate(ne[0] - 0.45, ze_, math.pi / 2, "gate_E", body="wallred")
# the gates open on the ground outside: a flight down the terrace's face to it
for nm, x_, z_, rot in (("gate_W", nw[0], zw_, -math.pi / 2), ("gate_E", ne[0], ze_, math.pi / 2)):
    gout = ground(x_ + (-1.5 if nm == "gate_W" else 1.5), z_)
    if Y_UP - gout > 0.2:
        flight(f"{nm}_steps", x_ + (-0.0 if nm == "gate_W" else 0.0), z_, rot, 2.6, Y_UP, gout)

# ============================================================ key points the leaf shows well: the terraces' corners at the water
for nm, (x, z) in (("pav_terrace_SW", (pd[0], pd[3])), ("pav_terrace_SE", (pd[1], pd[3])), ("pav_terrace_NW", (pd[0], pd[2])), ("pav_terrace_NE", (pd[1], pd[2]))):
    S.kp(nm, (x, Y_CW, z))
    S.kp(nm + "_water", (x, WATER_Y, z), anchor=True)
# the bastions' outer corners at the water (the ruin's line today: P0383, P0787)
for i, (x, z) in enumerate(READ["low_deck"]):
    S.kp(f"low_{i:02d}_water", (x, WATER_Y, z), anchor=True)
    S.kp(f"low_{i:02d}_top", (x, Y_LOW, z))

# ============================================================ write
REPORT["triangles"] = m.count()
n_bytes = m.write_glb(HERE / "model.glb", "YM29 方壶胜境 Fanghu Shengjing", extras={"frame": "x east along the front, y up, z south; origin at the front range's box front middle"})
aliases = ["YM29-01", "YM29-03", "YM29-04", "YM29-05", "YM29-N01", "YM29-N02", "YM29-AE005", "YM29-AE006", "YM29-AE007", "YM29-B0146", "YM29-B0173", "YM29-B0175", "YM29-B0176"]
summary = {
    "id": "YM29",
    "aliases": aliases,
    "name": "方壶胜境 Fanghu Shengjing",
    "glb": "model.glb",
    "position": S.pos,
    "rotationY": S.rot,
    "line": "The towers on their terraces over the water as the leaf of 1744 paints them and S01 draws them: nine two-storey towers in three ranges (S05, S361, Malone), the lower terrace with its stepped bastions on the water, the upper brick-faced terrace, the galleries joining the towers' upper floors, the causeway with its two archways to 迎薰亭 and the two cruciform terraces with 集瑞亭 and 凝祥亭; S01 gives the layout (B), the leaf the storeys, roofs, colours and parts (A for 1744), the texts the names; every height, every bay's width and the ornaments are C.",
    "rows": [
        ["Layout", "As S01 draws it, re-read in Round 24 in plan pixels (B): the lower terrace on the water and its bastions, the upper terrace behind it, three ranges each of a five-bay middle block and two side towers, the galleries, the strips out to the two cross terraces, the causeway and the square terrace; the bastions' line matches the ruin's today (P0383, P0787)"],
        ["The water", "The inlet the terraces stand in (S01; the leaf), water in the ground since Round 24 (W0365; Q191); its level the rule of Round 10 (C)"],
        ["宜春殿 and the entry", "The front range: five bays on two floors (S05 上下各五楹, A), a skirt roof and a balcony between them, 歇山 in yellow tile with green trim, red columns and lattice (the leaf, A for 1744); the three-bay entry before it, one storey under the upper floor's balcony (S01, the leaf; bays C); the plaque 方壶胜境 over its door (S05; board C)"],
        ["Side towers at the water", "锦绮楼 and 翡翠楼 (the 1740 plaques, S310; which is which C): two storeys, 歇山 with their gables to the water, yellow with green trim (the leaf); S01's blocks"],
        ["哕鸾殿's range", "On the upper terrace (Malone: brick-faced; S05 其北樓宇為噦鸞殿): five bays on two floors, 歇山 in purple-brown tile with green trim (the leaf; Q175); 碧云楼 and 紫霞楼 either side, joined by two-storey galleries (Malone's elevated walks)"],
        ["琼华楼's range", "At the back (S05 又北為瓊華樓): five bays on two floors under a double top eave, yellow with blue trim (the leaf); 千祥阁 and 万福阁 either side, purple-brown with green trim and two tiers of eaves (the leaf); galleries joining them and running down the court's sides to the middle range (S01, Malone); a terrace behind (S01's rectangle, C)"],
        ["The courts", "Flagged; bronze vessels and potted flowering trees before 哕鸾殿 (the leaf; their number and places C); the stair on the axis from the lower terrace (S01; its steps C); the walls round the upper terrace, red with yellow coping, a gate in the west and east walls (S01; colour C; 蕊珠门 is one of the 1740 plaques)"],
        ["On the water", "The galleries on their strips out to two stepped cross terraces (S01; Malone: a bridge and two piers to three small terraces) with 集瑞亭 and 凝祥亭: a lower eave and a cross-ridge 十字脊 roof, blue with yellow trim (the leaf); the causeway with two archways 坊座 (S05; places and form C) to the square terrace of 迎薰亭: double eaves, a yellow pyramid roof with a gilt finial (the leaf), four bronzes, two dragons and two phoenixes (E1856; form C), three flights to the water for the barge (S01, Malone)"],
        ["Assumed", "Every height (the terraces 2.6 and 1.9 m above the water, the upper terrace 3.0 m above the lower, the storeys 3.6 and 3.2 m), every bay's width, the galleries' width and form, the archways, the bronzes, the vessels and trees, the walls' colour, the rear terrace: the hall kit's classes and the Qing manual's typology (C, the pale tint with conf=1). No dig and no Yangshi Lei sheet with figures has been seen (Q119, E1855)"],
    ],
    "caption": {"frontage_m": round(max(p[0] for p in READ["strip_E"]) - min(p[0] for p in READ["strip_W"]), 1), "depth_m": round(pd[3] - qr[2], 1),
                "eave_m": REPORT["halls"]["qh"]["eave_m"], "ridge_m": REPORT["halls"]["qh"]["ridge_m"], "assumed": True, "confidence": "C"},
    "hides": [],
    "tris": m.count(),
    "glb_bytes": n_bytes,
}
S.write(HERE, "YM29", aliases, P, "origin at the front middle of the front range's box F0164 at its ground; x east along the front, y up, z south, turned to the axis S01 draws (scripts/model_site.py)", summary)
json.dump(REPORT, open(HERE / "report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"YM29: {m.count()} triangles, GLB {n_bytes / 1e6:.2f} MB; axis {AXIS:.2f} (spread {REPORT['axis_spread_m']} m); water {WATER_Y:.2f}, low {Y_LOW:.2f}, causeway {Y_CW:.2f}, up {Y_UP:.2f}")
