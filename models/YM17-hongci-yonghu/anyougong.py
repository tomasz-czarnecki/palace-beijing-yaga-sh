#!/usr/bin/env python3
"""鸿慈永祜 Hongci Yonghu (YM17), the ancestral temple 安佑宫 Anyou Gong with its gates, moats and archways: the fourteenth detailed model (Round 27).

  uv run python models/YM17-hongci-yonghu/anyougong.py

The imperial ancestral temple in the north-west of the garden, built in 1742-43 on the model of 寿皇殿 (S05 j81:19b-21b), where the portraits of Kangxi and
Yongzheng were kept and the emperors came at the new and full moon. From the south: the four marble 华表 round the glazed archway 鸿慈永祜坊, the hall 致孚殿 in its
yard to the east, the outer moat 月河 with five marble bridges, the forecourt with the three timber archways 三坊 and the two stone qilin, the outer wall with its
five gates, the court between the walls with the waiting rooms 朝房, the well pavilions and the inner moat with its five bridges, the gate 安佑门 on its terrace in the
inner wall, and inside the inner court the side halls 配殿, the two stele pavilions 碑亭, the two green-glazed burners 燎亭, and the hall 安佑宫 of nine bays with double
eaves on its marble terrace with five flights, its bronzes before it.

Method (docs/METHOD.md, 'a compound from the kit and its evidence', Rounds 17-25): every hall is the hall kit (scripts/hall_parts.py) from its numbers, adapted to
its evidence; the layout read on S01 (plan_readings.csv, plan pixels, placed by the fit in use, research/georef/); the leaf of 1744 (S08 P0017) for the roofs, colours,
the gates' and archways' forms, the railings; the ruin photograph of about 1882 (P0196) and the surviving pieces at Peking University (S943, S980) for the 华表, the
qilin and the ramp stone.
Writes, beside this file: model.glb, params.json, keypoints.json, joints.json, summary.json, report.json (models/README.md).
Frame (scripts/model_site.py): origin at the front middle of 安佑宫's box F0096, at that box's ground; z along the axis as S01 draws it (from the hall to the middle of
the four 华表), x east along the front, y up.
Grades: what a source states for this object (S01's layout and the hall's grid, S05's halls, bays and names, Malone's pillars, bridges, gates and walls, the leaf's
forms and colours, the surviving pieces' sizes) is `doc`; forms carried in from the classes (the waiting rooms, the corner ranges, the well pavilions, the burners,
the bronzes, the qilin's and the 华表's carving, the brackets) are `fill` (assumed, C).
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
from model_parts import Parts, arc_pts  # noqa: E402
from model_site import Site, box_frame  # noqa: E402
from scene1860 import DATUM_M, to_xz  # noqa: E402
from shapely.geometry import LineString, Point, Polygon  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

# ============================================================ the figures (value, source, grade, note): params.json
import os  # noqa: E402
HALL_COL = float(os.environ.get("YM17_COL", 4.6))  # the column of 安佑宫 above its floor (C: see P["hall_col"]); the environment only for the sweep (README)
HALL_RISE = float(os.environ.get("YM17_RISE", 6.9))  # the upper roof's rise from the lower eave's line to the ridge (C)
YT_H = 1.6  # the marble terrace above the court (C: see P["terrace"])
P = {
    "layout": ("as S01 draws the compound, re-read in plan pixels (plan_readings.csv)", "S01", "B", "Round 27 reading on 2.5-6x crops with a 5 px grid; placed by the fit in use (research/georef/); S01 is B until Q2 is settled"),
    "axis": ("one straight axis from the hall to the middle of the four 华表", "S01", "B", "the middles S01 draws on it (hall, terrace, flights, 安佑门, the bridges' middles, the three gates, the qilin, the south archway, the 华表 square, the north gate) spread over a few metres (report.json axis_spread_m); the axis-borne parts are centred on their mean"),
    "hall_bays": ("nine bays, ten column lines across the front, as S01 draws them", "S05;S01;S02", "B", "S05 j81:20a 重檐正殿九楹 (A); S01's ten lines (B, plan_readings.csv hall_cols); Malone: ten pillars across the front, forty in all (S02 p.88 n., E1562, B: what he counted on the ruin's platform)"),
    "hall_depth": ("four rows of columns, three spans back to front about 4.2, 7.2 and 2.6 m, the front span a porch", "S01;S02", "B", "S01's four rows (hall_rows); with the ten lines Malone's forty pillars; the porch's depth and the doors behind it C"),
    "hall_size": ("about 30 x 14 m between the end columns, by S01", "S01", "B", "the box of Round 2 (34 x 20.5 m) came from the hall scale of 4.2 px/m, C; by the fit in use S01's columns span 30 m and 14 m; no stated size is known (the Yangshi Lei sheet 安佑宫供器尺寸及殿底样, E1566, not seen)"),
    "hall_roof": ("double-eaved 歇山 in yellow glazed tile", "S08;S360;S02", "A", "the leaf: a gable triangle shows at the east end of the upper roof, so 歇山 (S08 P0017, A for 1744); S360's note (E1560): nine bays, 重檐歇山, yellow glazed; Malone: a double roof of yellow glazed tile (E1562)"),
    "hall_col": (HALL_COL, "S08", "C", "the leaf paints the lower columns about 0.15 of the hall's width (P0017, read on the 1300 px copy); with S01's 30 m, 4.6 m; the leaf's fit (research/scenes/YM17-hongci-yonghu/plate_fit.csv) tests it; the 举架 and the upper storey the grand_hall class (C)"),
    "hall_front": ("red lattice doors in all nine bays behind a porch of red columns, green-blue beams under both eaves", "S08", "A", "the leaf on the enlarged crop (ym17_c1, Round 7): red columns, red lattice, green-blue painted beams under both eaves; the doors' pattern C"),
    "hall_plaque": ("安佑宫, Qianlong's hand", "S05", "A", "S05 j81:21a 與安佑門安佑宫額皆御書; the board C"),
    "terrace": ("one marble terrace under the hall and before it, T-shaped as S01 draws it, 1.6 m above the court, balustraded, five flights", "S01;S02;S08;S943", "B", "S01's outline (platform and 月台 as one, no line between) (B); Malone: a marble terrace with five stairs, the middle one carved with dragons (E1562, B); the leaf: white balustrades (A); its height C: the ramp stone 3.15 m long (S943) laid at a stair's slope gives 1.4 m, S01's flights (3.6-5.1 m long) 1.8-2.6 m at 0.15 m risers"),
    "flights": ("three flights at the front, one on each side of the 月台, as S01 draws them, their runs S01's", "S01;S02", "B", "S01 (flight_C, _W, _E, _SW, _SE); Malone's five stairs (E1562); the risers 0.15 m and so the treads from the runs C"),
    "ramp": ("the dragon-and-cloud ramp stone 御路 in the middle flight, 1.30 m wide", "S943", "B", "one of its stones is at Peking University, 3.15 x 1.30 m, the relief 1.00 m wide, its pair at the east gate of 颐和园 (S943); the carving drawn as raised blocks (C)"),
    "bronzes": ("two censers, two cranes and two deer on the terrace", "S361;S02;S08", "B", "E1564 (S361): bronze deer and cranes before the hall; Malone: incense burners and bronze birds and animals (E1562); the leaf: vessels on the terrace (A, too small to name); places and forms C"),
    "beiting": ("two octagonal stele pavilions with double eaves, yellow, over marble steles", "S05;S02;S08;S01", "B", "S05 碑亭各一 (A); Malone: two double-roofed pavilions over marble steles (E1562, B); the leaf: double eaves, yellow (A); S01's octagons about 6.6 m (B); walls, arched doors and heights C"),
    "peidian": ("the side halls, five bays each, single-eave 歇山 in yellow tile", "S05;S08;S01", "B", "S05 左右配殿各五楹 (A); S01's cells against the inner wall (B); the leaf: yellow 歇山 roofs (A); heights and porches C"),
    "liaoting": ("two green-glazed burners 燎炉 by the inner gate", "S05;S02;S01", "B", "S05 燎亭各一 (A); Malone: two green glazed incense burners in the inner court (E1562, B); at S01's squares; their form C"),
    "gate": ("安佑门: five bays, single-eave 歇山 in yellow tile, on a marble terrace in the inner wall", "S05;S08;S02;S01", "B", "S05 宫門五楹南向為安佑門 (A); the leaf: a yellow-roofed gate hall with a white terrace and balustrade before it (A); Malone: a marble terrace with the inner gate (E1563, B); S01: 12.3 x 6.3 m between its columns, a middle row on the wall line (B); the widths' split, the column 3.8 m, the terrace 1.2 m and its depth C"),
    "gate_plaque": ("安佑门, Qianlong's hand", "S05", "A", "S05 j81:21a; the board C"),
    "walls": ("two red walls with yellow glazed coping", "S02;S08;S01", "B", "Malone (E1563, B); S01's lines (B); the leaf paints both walls vermilion, their caps read grey-green on the leaf (A for the red; the cap's yellow is Malone's); heights 4.2 and 4.4 m and thickness C"),
    "inner_side_gates": ("a small gate either side of 安佑门 in the inner wall, yellow roofs", "S01;S08", "B", "S01's cells (B); the leaf: small gates with yellow roofs (A); their form C"),
    "inner_moat": ("a moon river between the walls, lined with stone, five marble bridges", "S05;S02;S01", "B", "S05 門前白玉石橋三座 (A); Malone: a second moat with three bridges and two side bridges (E1563, B); S01's channel and breaks (B, water RM002); its lining, railing and the bridges' form C"),
    "chaofang": ("waiting rooms 朝房, five bays each, between the walls", "S05;S01", "B", "S05 朝房各五楹 (A); S01's cells (B); their form the class's (C)"),
    "jingting": ("two well pavilions between the walls", "S05;S02;S01", "B", "S05 左右井亭各一 (A); Malone: two covered wells (E1563, B); S01's squares (B); the form C"),
    "outer_gates": ("five gates in the outer wall: three glazed gates in the middle, a smaller gate at each side", "S02;S08;S01", "B", "Malone: five gates in a red wall (E1563, B); S01's blocks (B); the leaf: three arched gates with glazed frames and yellow roofs, red doors, and small side gates with yellow roofs (A); sizes and heights C"),
    "qilin": ("two stone qilin on stone bases before the three middle gates", "S02;S943;S01", "B", "Malone (E1563, B); S943: 1.74 m high on bases 0.98 m high, 1.41 x 1.95 m, each beast and its base cut from two stones; first before 大宫门, here from 1741; at Peking University since 1925 (B); S01's squares (B); the beast's form C (no photograph on disk)"),
    "sanfang": ("three timber archways 三坊 before the gates, red posts held by diagonal props, small yellow roofs", "S05;S08;S01", "B", "S05 坊南及東西復有三坊環列 with their six faces named (A); the leaf: timber archways with red diagonal props 戗杆 and yellow roofs with green-blue painted beams (A); S01's bars, 9.3-9.6 m (B); four posts and three roofs, heights C"),
    "outer_moat": ("the outer moat 月河, a U round the forecourt, lined with stone, red railings on its banks, five marble bridges", "S05;S02;S08;S01", "B", "S05 其南為月河橋 (A); Malone: five marble bridges, the middle one for the emperor alone (E1563, B); the leaf: three white arched bridges with balustrades and red railings along the banks (A); S01's band and breaks (B, water RM003); the two end bridges' form C"),
    "zhifu": ("致孚殿: three bays facing west in a red-walled yard, yellow tile", "S05;S08;S01", "B", "S05 又東南為致孚殿三楹西向 (A), with the carved 圆明园记 inside (S05 j81:21b); the leaf: a small yellow-roofed hall in a red-walled yard (A); S01's yard and cells (B); heights C"),
    "liulifang": ("the glazed archway 鸿慈永祜坊: three glazed gates between four short red walls with glazed discs", "S05;S02;S08;S01", "B", "S05: 琉璃坊座南面額 鸿慈永祜, north face 燕翼長詒 (A); Malone: a glazed pailou of four short walls and three gates (E1561, B); the leaf: three gates with blue-green glazed frames and yellow roofs between red walls with round glazed panels (A); S01's bar 13.7 x 2.5 m (B); heights C"),
    "huabiao": ("four marble 华表 at the corners of a square of 30 m round the archway, 8 m high on octagonal bases 1.24 m high", "S02;S980;S818;S01", "B", "Malone: four marble pillars about 100 ft apart at the corners of a square (E1561); S01's squares 30.2 x 30.0 m apart (B); S980, S818: about 8 m high, the base 1.24 m (B); S05 has 左右石華表各一 (two, Q179): four drawn; the dragon, the cloud board, the dew plate and the beast after P0196 (c. 1882) and P0809-P0813 (today), their sizes C"),
    "colours": ("red walls and columns, yellow glazed roofs, green-blue beams, white marble", "S08;S02", "A", "the leaf (S08 P0017, A for 1744); Malone's yellow glazed tile (E1562, E1563)"),
    "corner_ranges": ("a long range in a walled yard in each north corner of the outer court", "S01", "B", "S01's cells and yard lines (B); S05 names no building there: unnamed (C: a store or kitchen range, grey tile)"),
    "north_gate": ("a gate of three bays in the outer wall's north side", "S01", "B", "S01's three cells (B); form C"),
    "paving": ("the forecourt, the ways on the axis and between the gates paved; the courts earth with their trees", "S08", "C", "the leaf paints the forecourt and the inner court grey; the planting of Round 12 keeps its trees in the courts (research/greens/species.csv GS-0634)"),
}
V = {k: v[0] for k, v in P.items()}

COL = {
    "lacquer": "#8a2f22", "lacquer_dark": "#532218", "wall": "#93392a", "plaster": "#e4ddcf", "glass_lattice": "#2b3137", "sill": "#7d7973",
    "band": "#2e6a6c", "bracket": "#3b7b70", "bandred": "#7d2c20", "platform": "#b7b0a1", "coping": "#d2ccbe", "step": "#d8d3c7", "marble": "#ece8df",
    "marble_shade": "#cfc9bc", "underside": "#4b453d", "fascia": "#3a2a22", "wallred": "#a4402d", "rock": "#8f948f", "pave": "#bdb6a6", "gold": "#c9a245",
    "plaque": "#20406a", "bronze": "#4f5c4e", "stone_q": "#bcb6aa", "timber": "#7a5a3c", "rail": "#8c3a26", "quay": "#d9d4c8", "granite": "#9c978d",
    "disc": "#3f8f6a", "earth": "#8a7f6c",
    "tile_grey": "#5f6469", "ridge_grey": "#4a4e52", "tile_yellow": "#d6a31c", "ridge_yellow": "#a77f16", "tile_green": "#3f8f6a", "ridge_green": "#316f53",
}

S = Site("F0096")
m = Mesh(COL)
S.m = m
KIT = json.load(open(ROOT / "site/reconstruction/data/kit_1860.json", encoding="utf-8"))["halls"]
FEATS = S.F
GROUND = json.load(open(ROOT / "site/reconstruction/generated/ground.json", encoding="utf-8"))
WATER = json.load(open(ROOT / "research/layers/water_1860.geojson", encoding="utf-8"))["features"]
REPORT = {"halls": {}}
PARTS = Parts(m, rail_h=0.9, baluster_segs=4)


def plan_local(px, py):
    lon, lat = plan_to_wgs84(np.array([px], float), np.array([py], float))
    x, z = to_xz(float(lon[0]), float(lat[0]))
    return S.to_local(x, z)


ROWS = list(csv.DictReader(open(HERE / "plan_readings.csv", encoding="utf-8")))
PX = {r["name"]: [tuple(map(float, p.split())) for p in r["plan_px"].split(";")] for r in ROWS}


def _scene_mid(names):
    pts = [to_xz(*[float(v[0]) for v in plan_to_wgs84(np.array([p[0]], float), np.array([p[1]], float))]) for n in names for p in PX[n]]
    return np.mean([p[0] for p in pts]), np.mean([p[1] for p in pts])


# the frame's z along the axis S01 draws: from the middle of the hall's terrace and 安佑门 to the middle of the four 华表 and the forecourt's south archway
_n, _s = _scene_mid(("platform", "yuetai", "flight_C", "gate")), _scene_mid(("huabiao", "pailou_S", "qilin"))
ROT_BOX = S.rot
S.rot = round(math.atan2(_s[0] - _n[0], _s[1] - _n[1]), 6)
RAW = {k: [plan_local(*p) for p in v] for k, v in PX.items()}
# The fit in use shears S01 here: in this frame the plan's north-south lines run within 0.8 degrees of the axis, but its east-west lines fall 7.4 degrees to the
# east (the four long walls: slopes -0.124, -0.136, -0.125, -0.133), so S01's rectangles come out as parallelograms and the outer wall 113 m deep for 100 m.
# The temple is rectilinear: every reading is rectified about the axis, z' = z - k (x - x_axis), k the walls' mean slope; points on the axis do not move, the
# corners of the outer wall move 6 m. The two moats are traced water (research/plan/water_manual.json): their points there are S01's lines rectified the same way
# (`--moats` writes them), so that they keep their places between the walls.
_sl = lambda a, b: (b[1] - a[1]) / (b[0] - a[0])
_ow, _iw = RAW["outer_wall"], RAW["inner_wall"]
K_SHEAR = float(np.mean([_sl(_ow[0], _ow[1]), _sl(_ow[3], _ow[2]), _sl(_iw[0], _iw[1]), _sl(_iw[3], _iw[2])]))
X_PIVOT = float(np.mean([np.mean([p[0] for p in RAW[n]]) for n in ("platform", "yuetai", "flight_C", "gate", "gates_S", "qilin", "pailou_S", "huabiao", "gate_N")]))


def rectify(p):
    return (p[0], p[1] - K_SHEAR * (p[0] - X_PIVOT))


READ = {k: [rectify(p) for p in v] for k, v in RAW.items()}
REPORT["shear"] = {"k": round(K_SHEAR, 4), "deg": round(math.degrees(math.atan(K_SHEAR)), 2), "pivot_x": round(X_PIVOT, 2),
                   "outer_wall_corners_moved_m": [round(abs(K_SHEAR * (p[0] - X_PIVOT)), 2) for p in RAW["outer_wall"]]}


def plan_px_of(x, z, guess):
    """The plan pixel whose local point is (x, z): Newton on plan_local from a guess."""
    p = np.array(guess, float)
    for _ in range(8):
        f0 = np.array(plan_local(*p))
        J = np.column_stack([(np.array(plan_local(p[0] + 0.5, p[1])) - f0) / 0.5, (np.array(plan_local(p[0], p[1] + 0.5)) - f0) / 0.5])
        d = np.linalg.solve(J, np.array([x, z]) - f0)
        p = p + d
        if np.hypot(*d) < 1e-3:
            break
    return p


if "--moats" in sys.argv:  # write the moats' rectified points into research/plan/water_manual.json (run once after a change to plan_readings.csv, then build_r1.py)
    wm_path = ROOT / "research/plan/water_manual.json"
    txt = wm_path.read_text(encoding="utf-8")
    man = json.loads(txt)
    for rid, nm in (("RM002", "moat_inner"), ("RM003", "moat_outer")):
        new = [[round(float(v), 1) for v in plan_px_of(*rectify(q), p)] for p, q in zip(PX[nm], RAW[nm])]
        old = next(r for r in man if r["region_id"] == rid)["points"]
        txt = txt.replace(json.dumps(old, ensure_ascii=False), json.dumps(new, ensure_ascii=False))
        print(rid, "moved px", round(max(np.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(old, new)), 1))
    wm_path.write_text(txt, encoding="utf-8")
    sys.exit(0)


def rect(name):
    pts = READ[name]
    xs, zs = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), max(xs), min(zs), max(zs)


def mid(name):
    x0, x1, z0, z1 = rect(name)
    return (x0 + x1) / 2, (z0 + z1) / 2


_ax = {n: mid(n)[0] for n in ("platform", "yuetai", "flight_C", "gate", "gates_S", "qilin", "pailou_S", "huabiao", "gate_N")}
_ax["bridge_inner_mid"] = READ["bridges_inner"][2][0]
_ax["bridge_outer_mid"] = READ["bridges_outer"][2][0]
AXIS = float(np.mean(list(_ax.values())))
REPORT.update({"rot_box": ROT_BOX, "rot_axis": S.rot, "axis_x": round(AXIS, 2), "axis_spread_m": round(float(max(_ax.values()) - min(_ax.values())), 2),
               "axis_reads": {k: round(float(v - AXIS), 2) for k, v in _ax.items()}})

RAISED = []  # raised floors the model draws: (polygon, top); the flights, walls and paving read them as their ground


def ground(x, z):
    g = S.gy(x, z)
    for poly, top in RAISED:
        if poly.buffer(1e-6).contains(Point(x, z)):
            g = max(g, top)
    return g


K = HallKit(m, ground)


def compass(dx, dz):
    return ("N" if dz < 0 else "S") + ("W" if dx < 0 else "E")


def box_local(fid):
    c, u, hf, hd, base = box_frame(FEATS, fid)
    x, z = S.to_local(*c)
    x2, z2 = S.to_local(*(c + u))
    return x, z, math.atan2(x2 - x, z2 - z), hf, hd


def kp_platform(name, hf, hd, y_top, anchor=True):
    c0 = m.world((0, 0, 0))
    for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        w = m.world((sx * hf, 0, sq * hd))
        tag = compass(w[0] - c0[0], w[2] - c0[2])
        S.kp(f"{name}_pl_foot_{tag}", (w[0], S.gy(float(w[0]), float(w[2])), w[2]), anchor=anchor)
        S.kp(f"{name}_pl_top_{tag}", (w[0], y_top, w[2]))


def kp_roof(name, H):
    """The eave corners' tips and the ridge's ends, by compass, as hall_parts draws them; on a double eave the lower eave is `<name>_low_eave_`."""
    CS, CQ, o = H["hf"] - H["e"], H["hd"] - H["e"], H["o"]
    base, eave, ridge = H["base"], H["base"] + H["eave"], H["base"] + H["ridge"]
    c0 = m.world((0, 0, 0))
    tip = eave - o * 0.5
    if H.get("db"):
        RS, RQ = CS + o, CQ + o
        for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            w = m.world((sx * RS, 0, sq * RQ))
            S.kp(f"{name}_low_eave_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], tip + min(0.35, 0.03 * (RS + RQ)), w[2]))
        inS, inQ = CS - max(H["pf"], H["ps"], 1.5), CQ - max(H["pf"], H["pb"], 1.5)
        yUp = eave + (ridge - eave) * H.get("upper", 0.36)
        lip = o * 0.75
        hs, hq, y0 = inS + lip, inQ + lip, yUp - lip * 0.5
    else:
        hs, hq, y0 = CS + o, CQ + o, tip
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


def draw(name, H, kp=True, site_lists=True):
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
    if site_lists:
        for i, c in enumerate(corners):
            g = ground(float(c[0]), float(c[2]))
            if g <= S.gy(float(c[0]), float(c[2])) + 1e-6:
                S.JOINTS.append([f"{name}_pl_{i}", float(c[0]), H["foot"], float(c[2]), "platform foot"])
        S.FOOTPRINTS.append([(float(c[0]), float(c[2])) for c in corners])
        for k, f in fw.items():
            S.entry(f"{name}_{k}", float(f[0]), float(f[2]), float(f[1]))
    REPORT["halls"][name] = {"frontage_m": round(2 * H["hf"], 2), "depth_m": round(2 * H["hd"], 2), "platform_m": round(H["pl"], 2), "eave_m": H["eave"], "ridge_m": H["ridge"],
                             "roof": H["rf"], "double_eave": int(bool(H.get("db"))), "tile": H["t"], "bays": len(H["b"]), "flights": len(feet), "grade_class": H["cls"],
                             "x": round(H["x"], 2), "z": round(H["z"], 2)}
    return fw


def hall_spec(x, z, rot, bays, depths, edge, pl, col, roof, rolled, cls, bracket=False, ju="main_hall", pf=0.0, pb=0.0, ps=0.0, tile="yellow", over=None):
    """A hall from its spans (eave column to eave column) and its section: platform = columns + edge; eave from the column and the band; ridge by the 举架."""
    span, dep = sum(bays), sum(depths)
    hf, hd = span / 2 + edge, dep / 2 + edge
    gx = [x + s * math.cos(rot) * hf + q * math.sin(rot) * hd for s in (-1, 1) for q in (-1, 1)]
    gz = [z - s * math.sin(rot) * hf + q * math.cos(rot) * hd for s in (-1, 1) for q in (-1, 1)]
    gs = [ground(a, b) for a, b in zip(gx, gz)]
    base = ground(x + math.sin(rot) * hd, z + math.cos(rot) * hd)
    band = 0.85 if bracket else 0.42
    eave = round(pl + col + band, 2)
    o = 1.25 if col >= 4.0 else 1.05
    rise = round(0.62 * (dep / 2 + o), 2)
    H = dict(hf=hf, hd=hd, base=base, foot=min(gs) - 0.15, pl=pl, eave=eave, ridge=round(eave + rise, 2), e=edge, o=o, b=list(bays), d=list(depths), pf=pf, pb=pb, ps=ps,
             dia=0.36 if col < 4.0 else 0.46, st={"front": [0.0]}, bal=0, rf=roof, rl=1 if rolled else 0, db=0, ju=JU[ju], t=tile, te=None,
             bd="br" if bracket else "bm", dr=[len(bays) // 2], rr="w", k="hall", x=x, z=z, rot=rot, cls=cls, src="dossier")
    if over:
        H.update(over)
    return H


def plaque(H, q_sign=1, w=2.4, h=1.0, name=None):
    """A plaque board 匾 on the eave band at the hall's middle bay (blue board, gold frame: C)."""
    m.push(H["x"], 0, H["z"], H["rot"])
    CQ = H["hd"] - H["e"]
    q = q_sign * (CQ + 0.3)
    y1 = H["base"] + H["eave"] - 0.05
    m.box(-w / 2 - 0.1, w / 2 + 0.1, y1 - h - 0.1, y1, q - 0.05, q + 0.05, "gold")
    zf = q + q_sign * 0.055
    m.poly([(-w / 2, y1 - h, zf), (w / 2, y1 - h, zf), (w / 2, y1 - 0.1, zf), (-w / 2, y1 - 0.1, zf)], "plaque")
    if name:
        S.kp(name, m.world((0, y1 - h / 2, zf)))
    m.pop()


def wall_run(pts, h, name, gaps=(), thick=1.0, body="wallred", cap="yellow", base_h=0.6, joints=True):
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
        K.wall(r, h, thick=thick, cap=cap, base_h=base_h, body_mat=body)
        S.FOOTPRINTS.append([(float(x), float(z)) for x, z in list(LineString(r).buffer(thick / 2 + 0.1, cap_style="flat").exterior.coords)[:-1]])
        if joints:
            for k, (x, z) in enumerate(r):
                S.joint(f"{name}{i}_{k}", x, z, "wall foot", y=S.gy(x, z) - 0.15)
    return runs


def wall_gate(x, z, rot, name, w=2.6, h=3.8, thick=1.0, body="wallred", tile="yellow", edge="green"):
    """A gate in a wall 随墙门 (C): two piers, a lintel band, red plank doors with gilt studs, a small glazed roof along the wall; entries both sides."""
    m.push(x, 0, z, rot)
    g = min(K.gy_local(a, b) for a in (-w / 2 - 0.5, w / 2 + 0.5) for b in (-thick, thick))
    y0 = g - 0.15
    for sg in (-1, 1):
        a0, a1 = (w / 2, w / 2 + 0.7) if sg > 0 else (-w / 2 - 0.7, -w / 2)
        m.box(a0, a1, y0, g + h - 0.6, -thick / 2 - 0.1, thick / 2 + 0.1, body)
        m.box(a0, a1, y0, g + 0.5, -thick / 2 - 0.12, thick / 2 + 0.12, "marble")
    m.box(-w / 2, w / 2, g + h - 1.25, g + h - 0.6, -thick / 2 - 0.05, thick / 2 + 0.05, "band")
    m.box(-w / 2 - 0.7, w / 2 + 0.7, g + h - 0.6, g + h - 0.45, -thick / 2 - 0.12, thick / 2 + 0.12, "bracket")
    m.box(-w / 2, w / 2, y0, g + 0.15, -thick / 2 - 0.25, thick / 2 + 0.25, "step")
    for a0, a1 in ((-w / 2 + 0.05, -0.02), (0.02, w / 2 - 0.05)):
        m.box(a0, a1, g + 0.15, g + h - 1.25, -0.06, 0.06, "lacquer")
        for yy in (g + 0.9, g + 1.6, g + 2.3):
            for sg in (-1, 1):
                for k in range(3):
                    xx = a0 + (a1 - a0) * (k + 0.5) / 3
                    m.box(xx - 0.04, xx + 0.04, yy - 0.04, yy + 0.04, sg * 0.06 - 0.02, sg * 0.06 + 0.02, "gold")
    K.roof(lambda a, b, c: (a, b, c), w / 2 + 1.1, thick / 2 + 0.8, g + h - 0.5, g + h + 0.75, form="xs", rolled=False, ju=JU["gallery"], tile=tile, edge=edge)
    for sg, tag in ((1, "out"), (-1, "in")):
        p_ = m.world((0, 0, sg * 1.3))
        S.entry(f"{name}_{tag}", float(p_[0]), float(p_[2]))
    for sg in (-1, 1):
        p_ = m.world((sg * (w / 2 + 0.35), 0, 0))
        S.joint(f"{name}_pier{sg:+d}", float(p_[0]), float(p_[2]), "gate pier", y=y0)
    top = m.world((0, g + h + 0.75, 0))
    m.pop()
    return top


def pave(poly, name, dy=0.03, step=5.0, mat="pave", clear=True):
    """Paving over an outline, following the ground (or a terrace) in cells."""
    pg = Polygon(poly).buffer(0)
    x0, z0, x1, z1 = pg.bounds
    xs, zs = np.arange(x0, x1 + step, step), np.arange(z0, z1 + step, step)
    for i in range(len(xs) - 1):
        for j in range(len(zs) - 1):
            cell = Polygon([(xs[i], zs[j]), (xs[i + 1], zs[j]), (xs[i + 1], zs[j + 1]), (xs[i], zs[j + 1])]).intersection(pg)
            if cell.is_empty or cell.area < 0.05:
                continue
            geoms = [cell] if cell.geom_type == "Polygon" else [g for g in getattr(cell, "geoms", []) if g.geom_type == "Polygon"]
            for g in geoms:
                c = list(g.exterior.coords)[:-1]
                pts = [(float(a), ground(float(a), float(b)) + dy, float(b)) for a, b in c]
                if len(pts) >= 3:
                    for t in range(1, len(pts) - 1):
                        m.poly([pts[0], pts[t], pts[t + 1]], mat)
    if clear:
        S.CLEAR.append([tuple(map(float, p)) for p in pg.exterior.coords[:-1]])


def rail_run(a, b, ya, yb, h=0.95, step=1.7, mat="marble", panel=True, post=0.22):
    """A rail along a straight run (x, z) from a to b, its foot from ya to yb: posts, a top rail, a foot rail, and pierced panels between (stone) or a middle rail (timber)."""
    (ax, az), (bx, bz) = a, b
    L = math.hypot(bx - ax, bz - az)
    if L < 0.3:
        return
    ux, uz = (bx - ax) / L, (bz - az) / L
    nx, nz = -uz, ux
    n = max(1, round(L / step))
    for k in range(n + 1):
        t = k / n
        x, z, y = ax + (bx - ax) * t, az + (bz - az) * t, ya + (yb - ya) * t
        m.box(x - post / 2, x + post / 2, y - 0.05, y + h + 0.16, z - post / 2, z + post / 2, mat)
    th = 0.09 if panel else 0.05
    rails = ((h - 0.12, h), (0.0, 0.14)) if panel else ((h - 0.08, h), (h * 0.45, h * 0.45 + 0.07))
    for y0, y1 in rails:
        q = [(ax + nx * th, ya + y0, az + nz * th), (bx + nx * th, yb + y0, bz + nz * th), (bx - nx * th, yb + y0, bz - nz * th), (ax - nx * th, ya + y0, az - nz * th)]
        top = [(p[0], p[1] + (y1 - y0), p[2]) for p in q]
        m.poly(top, mat)
        m.poly([q[0], q[1], top[1], top[0]], mat)
        m.poly([q[3], q[2], top[2], top[3]], mat)
        m.poly(q, mat)
    if panel:
        for k in range(n):
            t0, t1 = (k + 0.12) / n, (k + 0.88) / n
            p0 = (ax + (bx - ax) * t0, ya + (yb - ya) * t0, az + (bz - az) * t0)
            p1 = (ax + (bx - ax) * t1, ya + (yb - ya) * t1, az + (bz - az) * t1)
            for sg in (1, -1):
                d = sg * 0.045
                m.poly([(p0[0] + nx * d, p0[1] + 0.14, p0[2] + nz * d), (p1[0] + nx * d, p1[1] + 0.14, p1[2] + nz * d),
                        (p1[0] + nx * d, p1[1] + 0.48, p1[2] + nz * d), (p0[0] + nx * d, p0[1] + 0.48, p0[2] + nz * d)], mat)


def rail_poly(pts, y_fn, gaps=(), **kw):
    """rail_run along a polyline, left open where a point falls inside a gap polygon."""
    for a, b in zip(pts[:-1], pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(L / 0.5))
        cur = None
        for k in range(n + 1):
            t = k / n
            p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            blocked = any(g.contains(Point(*p)) for g in gaps)
            if blocked:
                if cur is not None and math.hypot(p[0] - cur[0], p[1] - cur[1]) > 0.6:
                    q = prev
                    rail_run(cur, q, y_fn(*cur), y_fn(*q), **kw)
                cur = None
            elif cur is None:
                cur = p
            prev = p
        if cur is not None and math.hypot(b[0] - cur[0], b[1] - cur[1]) > 0.6:
            rail_run(cur, b, y_fn(*cur), y_fn(*b), **kw)


def strut(p0, p1, r, mat):
    """A square pole between two points (a prop 戗杆)."""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = p1 - p0
    d /= np.linalg.norm(d)
    a = np.cross(d, [0.0, 1.0, 0.0]) if abs(d[1]) < 0.95 else np.cross(d, [1.0, 0.0, 0.0])
    a /= np.linalg.norm(a)
    b = np.cross(d, a)
    cs = [a * r + b * r, -a * r + b * r, -a * r - b * r, a * r - b * r]
    for i in range(4):
        c0, c1 = cs[i], cs[(i + 1) % 4]
        m.poly([tuple(p0 + c0), tuple(p0 + c1), tuple(p1 + c1), tuple(p1 + c0)], mat)


def disc(cx, cy, z, r, mat, n=16, sgn=1):
    """A round panel in the plane z (a glazed medallion 盒子)."""
    pts = [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n), z) for k in range(n)]
    m.poly(pts, mat)


# ============================================================ the water: the two moats (research/plan/water_manual.json RM002, RM003) and their levels
def water_body(region):
    f = next(f for f in WATER if f["properties"].get("region_id") == region)
    poly = Polygon([S.to_local(*to_xz(*c)) for c in f["geometry"]["coordinates"][0]]).buffer(0)
    # the body's level from research/terrain/water_levels.csv (ground.json lists only a body's first ids)
    row = next(r for r in csv.DictReader(open(ROOT / "research/terrain/water_levels.csv", encoding="utf-8")) if f["properties"]["id"] in r["water_ids"].split(";"))
    return f["properties"]["id"], poly, float(row["level_m_egm2008"]) - DATUM_M - S.pos[1]


WID_IN, MOAT_IN, WY_IN = water_body("RM002")
WID_OUT, MOAT_OUT, WY_OUT = water_body("RM003")
REPORT["moats"] = {"inner": {"water_id": WID_IN, "water_y": round(WY_IN, 3), "area_m2": round(MOAT_IN.area, 1)},
                   "outer": {"water_id": WID_OUT, "water_y": round(WY_OUT, 3), "area_m2": round(MOAT_OUT.area, 1)}}


def moat_span(poly, x, z_hint):
    """The water's extent along z at x, the piece nearest z_hint: (z0, z1)."""
    line = LineString([(x, z_hint - 30), (x, z_hint + 30)]).intersection(poly)
    parts = [line] if line.geom_type == "LineString" else list(getattr(line, "geoms", []))
    parts = [p for p in parts if not p.is_empty]
    best = min(parts, key=lambda p: abs((p.bounds[1] + p.bounds[3]) / 2 - z_hint))
    return best.bounds[1], best.bounds[3]


def lining(poly, water_y, name, coping=0.65, mat_face="quay"):
    """The moat's stone lining: a face from the bank down below the water and a coping slab on the bank, following the ground."""
    lin = poly.exterior
    n_seg = max(8, int(lin.length / 1.2))
    pts = [lin.interpolate(k / n_seg, normalized=True) for k in range(n_seg + 1)]
    for a, b in zip(pts[:-1], pts[1:]):
        dx, dz = b.x - a.x, b.y - a.y
        L = math.hypot(dx, dz)
        if L < 1e-3:
            continue
        nx, nz = -dz / L, dx / L
        if poly.contains(Point((a.x + b.x) / 2 + nx * 0.3, (a.y + b.y) / 2 + nz * 0.3)):
            nx, nz = -nx, -nz
        ya, yb = S.gy(a.x + nx * 0.9, a.y + nz * 0.9), S.gy(b.x + nx * 0.9, b.y + nz * 0.9)
        ta, tb = ya + 0.1, yb + 0.1
        m.poly([(a.x, ta, a.y), (b.x, tb, b.y), (b.x, water_y - 0.6, b.y), (a.x, water_y - 0.6, a.y)], mat_face)
        m.poly([(a.x, ta, a.y), (a.x + nx * coping, ta, a.y + nz * coping), (b.x + nx * coping, tb, b.y + nz * coping), (b.x, tb, b.y)], "marble")
        m.poly([(a.x + nx * coping, ta, a.y + nz * coping), (a.x + nx * coping, ya - 0.12, a.y + nz * coping), (b.x + nx * coping, yb - 0.12, b.y + nz * coping),
                (b.x + nx * coping, tb, b.y + nz * coping)], "marble")


def arch_bridge(name, x, z_hint, poly, water_y, width, hump=0.55, abut=1.5, arched=True, kp=False):
    """A marble bridge across a moat along z at x: its deck humped over a round arch (or flat over a slab opening), spandrel walls, a stone rail each side;
    ends on the banks are entries and joints. Returns the gap polygon for the bank railings."""
    z0w, z1w = moat_span(poly, x, z_hint)
    za, zb = z0w - abut, z1w + abut
    ya, yb = ground(x, za), ground(x, zb)
    hw = width / 2
    n = 8
    prof = []
    for k in range(n + 1):
        t = k / n
        prof.append((za + (zb - za) * t, ya + (yb - ya) * t + 0.12 + (hump * math.sin(math.pi * t) if arched else 0.18)))
    yb_low = water_y - 0.6
    for (z0, y0), (z1, y1) in zip(prof[:-1], prof[1:]):
        m.poly([(x - hw, y0, z0), (x + hw, y0, z0), (x + hw, y1, z1), (x - hw, y1, z1)], "marble")
        for sx in (-1, 1):
            m.poly([(x + sx * hw, y0, z0), (x + sx * hw, y1, z1), (x + sx * hw, yb_low, z1), (x + sx * hw, yb_low, z0)], "marble")
    for (zz, yy) in (prof[0], prof[-1]):
        m.poly([(x - hw, yy, zz), (x + hw, yy, zz), (x + hw, yy - 0.5, zz), (x - hw, yy - 0.5, zz)], "marble")
    # the opening: a dark arch (or a slot) on both faces over the water
    zc, span = (z0w + z1w) / 2, (z1w - z0w)
    r = max(0.6, span / 2 + 0.05)
    top_mid = max(y for _, y in prof) - 0.35
    if arched:
        spring = min(water_y + 0.15, top_mid - r)
        spring = max(spring, water_y - 0.3)
        r = min(r, top_mid - spring)
        pts = [(zc + r * math.cos(math.pi * k / 10), spring + r * math.sin(math.pi * k / 10)) for k in range(11)]
    else:
        spring = water_y + 0.1
        pts = [(zc + span / 2, spring), (zc + span / 2, top_mid - 0.15), (zc - span / 2, top_mid - 0.15), (zc - span / 2, spring)]
    for sx in (-1, 1):
        xf = x + sx * (hw + 0.012)
        m.poly([(xf, water_y - 0.05, pts[0][0])] + [(xf, y, z) for z, y in pts] + [(xf, water_y - 0.05, pts[-1][0])], "underside")
    m.box(x - hw + 0.05, x + hw - 0.05, water_y - 0.6, spring + (r if arched else 0.0) * 0.95, zc - (r if arched else span / 2) * 0.9, zc + (r if arched else span / 2) * 0.9,
          "underside", skip=("top", "bottom"))
    # the rails, following the deck
    for sx in (-1, 1):
        xr = x + sx * (hw - 0.12)
        for (z0, y0), (z1, y1) in zip(prof[:-1], prof[1:]):
            rail_run((xr, z0), (xr, z1), y0, y1, h=0.85, step=1.4, mat="marble")
    S.entry(f"{name}_N", x, za - 0.6)
    S.entry(f"{name}_S", x, zb + 0.6)
    for zz, tag in ((za, "N"), (zb, "S")):
        for sx in (-1, 1):
            S.joint(f"{name}_{tag}{'W' if sx < 0 else 'E'}", x + sx * hw, zz, "bridge end", y=min(ground(x + sx * hw, zz), S.gy(x + sx * hw, zz)) - 0.05)
    if kp:
        S.kp(f"{name}_crown", (x, max(y for _, y in prof), zc))
    REPORT.setdefault("bridges", {})[name] = {"width_m": round(width, 2), "length_m": round(zb - za, 2), "water_span_m": round(span, 2),
                                              "crown_above_water_m": round(max(y for _, y in prof) - water_y, 2), "x": round(x, 2)}
    return Polygon([(x - hw - 0.8, za - 1.0), (x + hw + 0.8, za - 1.0), (x + hw + 0.8, zb + 1.0), (x - hw - 0.8, zb + 1.0)])


def bank_rails(poly, gaps, name, h, mat, panel, step):
    """A rail on both banks of a moat, 0.4 m back from the water's edge, open at the bridges and round the ends."""
    line = poly.buffer(0.45, join_style=2).exterior
    npt = max(10, int(line.length / 0.8))
    cur, runs = [], []
    for k in range(npt + 1):
        q = line.interpolate(k / npt, normalized=True)
        if any(g.contains(q) for g in gaps):
            if len(cur) > 2:
                runs.append(cur)
            cur = []
        else:
            cur.append((q.x, q.y))
    if len(cur) > 2:
        runs.append(cur)
    for r in runs:
        simp = list(LineString(r).simplify(0.15).coords)
        for a, b in zip(simp[:-1], simp[1:]):
            rail_run(a, b, S.gy(*a) + 0.1, S.gy(*b) + 0.1, h=h, step=step, mat=mat, panel=panel, post=0.2 if panel else 0.14)
    REPORT.setdefault("bank_rails", {})[name] = len(runs)


# ============================================================ small structures
def censer(x, z, y, name):
    m.box(x - 0.6, x + 0.6, y, y + 0.5, z - 0.6, z + 0.6, "marble")
    for a in (0.0, 2.094, 4.189):
        lx, lz = x + 0.3 * math.cos(a), z + 0.3 * math.sin(a)
        m.box(lx - 0.06, lx + 0.06, y + 0.5, y + 0.8, lz - 0.06, lz + 0.06, "bronze")
    m.lathe([(0.25, y + 0.75), (0.5, y + 0.9), (0.55, y + 1.25), (0.42, y + 1.45), (0.5, y + 1.5), (0.3, y + 1.8), (0.12, y + 2.05), (0.18, y + 2.2), (0.0, y + 2.45)], 10, "bronze", cx=x, cz=z)
    S.kp(f"{name}_top", (x, y + 2.45, z))


def crane(x, z, y, face):
    m.push(x, 0, z, face)
    m.box(-0.45, 0.45, y, y + 0.35, -0.45, 0.45, "marble")
    for sx in (-0.12, 0.12):
        m.box(sx - 0.03, sx + 0.03, y + 0.35, y + 1.05, -0.03, 0.03, "bronze")
    m.lathe([(0.0, y + 0.95), (0.2, y + 1.0), (0.24, y + 1.15), (0.18, y + 1.32), (0.0, y + 1.38)], 8, "bronze", cz=-0.05)
    strut((0, y + 1.25, 0.12), (0, y + 2.05, 0.28), 0.04, "bronze")
    m.box(-0.06, 0.06, y + 2.0, y + 2.12, 0.22, 0.48, "bronze")
    m.pop()


def deer(x, z, y, face):
    m.push(x, 0, z, face)
    m.box(-0.45, 0.45, y, y + 0.35, -0.7, 0.7, "marble")
    for sx in (-0.13, 0.13):
        for sz in (-0.38, 0.38):
            m.box(sx - 0.04, sx + 0.04, y + 0.35, y + 1.0, sz - 0.04, sz + 0.04, "bronze")
    m.frustum([(-0.16, -0.5), (0.16, -0.5), (0.16, 0.5), (-0.16, 0.5)], [(-0.13, -0.45), (0.13, -0.45), (0.13, 0.45), (-0.13, 0.45)], y + 0.95, y + 1.32, "bronze")
    strut((0, y + 1.25, 0.42), (0, y + 1.7, 0.58), 0.07, "bronze")
    m.box(-0.08, 0.08, y + 1.62, y + 1.8, 0.5, 0.82, "bronze")
    for sx in (-1, 1):
        strut((sx * 0.05, y + 1.78, 0.56), (sx * 0.28, y + 2.2, 0.48), 0.025, "bronze")
    m.pop()


def qilin(x, z, face, name):
    """A stone qilin on its base: the base 1.41 x 1.95 x 0.98 m and the beast 1.74 m high (S943); the beast standing, its form C."""
    m.push(x, 0, z, face)
    g0 = min(K.gy_local(a, b) for a in (-0.75, 0.75) for b in (-1.0, 1.0))
    y0 = g0 - 0.15
    m.cls = "doc"
    m.box(-0.78, 0.78, y0, g0 + 0.2, -1.05, 1.05, "stone_q", skip=("bottom",))
    m.box(-0.62, 0.62, g0 + 0.2, g0 + 0.78, -0.9, 0.9, "stone_q")
    m.box(-0.705, 0.705, g0 + 0.78, g0 + 0.98, -0.975, 0.975, "stone_q")
    m.cls = "fill"
    b = g0 + 0.98
    m.box(-0.5, 0.5, b, b + 0.12, -0.85, 0.85, "stone_q")
    for sx in (-0.26, 0.26):
        for sz in (-0.55, 0.5):
            m.box(sx - 0.1, sx + 0.1, b + 0.12, b + 0.72, sz - 0.11, sz + 0.11, "stone_q")
    m.frustum([(-0.32, -0.72), (0.32, -0.72), (0.32, 0.62), (-0.32, 0.62)], [(-0.27, -0.66), (0.27, -0.66), (0.27, 0.55), (-0.27, 0.55)], b + 0.65, b + 1.12, "stone_q")
    m.frustum([(-0.25, 0.3), (0.25, 0.3), (0.25, 0.72), (-0.25, 0.72)], [(-0.2, 0.42), (0.2, 0.42), (0.2, 0.7), (-0.2, 0.7)], b + 1.0, b + 1.42, "stone_q")
    m.lathe([(0.0, b + 1.32), (0.24, b + 1.36), (0.27, b + 1.52), (0.2, b + 1.66), (0.0, b + 1.74)], 8, "stone_q", cx=0.0, cz=0.62)
    m.box(-0.13, 0.13, b + 1.36, b + 1.56, 0.78, 0.98, "stone_q")
    strut((0.0, b + 1.62, 0.55), (0.0, b + 1.74, 0.3), 0.05, "stone_q")
    strut((0.0, b + 0.95, -0.7), (0.0, b + 0.55, -1.0), 0.08, "stone_q")
    m.cls = "doc"
    top = m.world((0, b + 1.74, 0.62))
    foot = [m.world((sx * 0.78, 0, sq * 1.05)) for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    m.pop()
    S.kp(f"{name}_top", top)
    S.FOOTPRINTS.append([(float(c[0]), float(c[2])) for c in foot])
    for i, c in enumerate(foot):
        S.JOINTS.append([f"{name}_base_{i}", float(c[0]), y0, float(c[2]), "base foot"])


def huabiao(x, z, name, board_rot=0.0):
    """A marble 华表: the octagonal sumeru base 1.24 m (S980), the octagonal shaft with a dragon coiled round it (P0196), the cloud board, the dew plate and the
    seated beast, 8 m in all (S980); every part's size but the base's height and the whole C."""
    g = min(S.gy(x + a, z + b) for a in (-1.0, 1.0) for b in (-1.0, 1.0))
    y0 = g - 0.15
    m.cls = "doc"
    m.lathe([(1.02, y0), (1.02, g + 0.22), (0.9, g + 0.3), (0.84, g + 0.36), (0.84, g + 0.88), (0.92, g + 0.96), (1.02, g + 1.06), (1.02, g + 1.24)], 8, "marble", cx=x, cz=z)
    m.lathe([(0.47, g + 1.24), (0.44, g + 1.4), (0.42, g + 6.5), (0.44, g + 6.75)], 8, "marble", cx=x, cz=z)
    m.cls = "fill"
    nseg = 36
    for k in range(nseg):  # the dragon: a raised coil, one and a half turns
        t0, t1 = k / nseg, (k + 1) / nseg
        a0, a1 = 3 * math.pi * t0, 3 * math.pi * t1
        y_0, y_1 = g + 1.6 + 4.6 * t0, g + 1.6 + 4.6 * t1
        r = 0.45
        p0 = (x + r * math.cos(a0), y_0, z + r * math.sin(a0))
        p1 = (x + r * math.cos(a1), y_1, z + r * math.sin(a1))
        strut(p0, p1, 0.1 + 0.03 * math.sin(math.pi * t0), "marble_shade")
    m.push(x, 0, z, board_rot)  # the cloud board 云板 through the shaft
    m.box(-1.05, 1.05, g + 5.55, g + 6.15, -0.08, 0.08, "marble")
    m.box(-1.2, -0.85, g + 5.75, g + 6.3, -0.09, 0.09, "marble")
    m.box(0.85, 1.2, g + 5.75, g + 6.3, -0.09, 0.09, "marble")
    m.pop()
    m.cls = "doc"
    m.lathe([(0.3, g + 6.75), (0.55, g + 6.82), (0.66, g + 6.98), (0.6, g + 7.12), (0.0, g + 7.15)], 10, "marble", cx=x, cz=z)
    m.cls = "fill"
    m.lathe([(0.25, g + 7.15), (0.28, g + 7.45), (0.18, g + 7.6), (0.24, g + 7.78), (0.12, g + 7.95), (0.0, g + 8.0)], 8, "marble_shade", cx=x, cz=z)
    m.cls = "doc"
    S.kp(f"{name}_top", (x, g + 8.0, z))
    S.kp(f"{name}_foot", (x, g, z), anchor=True)
    S.FOOTPRINTS.append([(x - 1.05, z - 1.05), (x + 1.05, z - 1.05), (x + 1.05, z + 1.05), (x - 1.05, z + 1.05)])
    for i, (a, b) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        S.joint(f"{name}_{i}", x + a * 0.95, z + b * 0.95, "base foot", y=y0)
    return g


def glazed_gate(cx, cz, rot, w, d, h_open, h_body, ridge, name, doors=True, arched=True, tile="yellow", edge="green", plaque_w=0.0):
    """A glazed gate 琉璃门: a marble base, a red masonry body with a passage (arched, or square under a lintel), a glazed frame round the passage, a glazed frieze
    with a bracket band, a small hip-gable roof; red plank doors with gilt studs in the passage (the leaf's gates; form C)."""
    m.push(cx, 0, cz, rot)
    g = min(K.gy_local(a, b) for a in (-w / 2, w / 2) for b in (-d / 2, d / 2))
    y0 = g - 0.15
    yb = g + 0.45
    m.box(-w / 2 - 0.25, w / 2 + 0.25, y0, yb, -d / 2 - 0.25, d / 2 + 0.25, "marble", skip=("bottom",))
    ow = min(w - 1.2, max(1.6, w * 0.5))
    rise = ow / 2 if arched else 0.0
    top_open = yb + h_open
    b1 = top_open - rise
    ytop = yb + h_body
    for sg in (1, -1):
        m.push(0, 0, sg * d / 2, 0 if sg > 0 else math.pi)
        PARTS.wall_holes(-w / 2, w / 2, yb, ytop, [(-ow / 2, ow / 2, yb, b1, rise)], "wallred")
        # the glazed frame round the passage
        fr = 0.28
        for s0 in (-ow / 2 - fr, ow / 2):
            m.box(s0, s0 + fr, yb, b1, 0.0, 0.05, f"tile_{edge}")
        if arched:
            pts_i = arc_pts(-ow / 2, ow / 2, b1, rise, 10)
            pts_o = arc_pts(-ow / 2 - fr, ow / 2 + fr, b1, rise + fr, 10)
            for (a0, c0), (a1, c1), (o0, p0), (o1, p1) in zip(pts_i[:-1], pts_i[1:], pts_o[:-1], pts_o[1:]):
                m.poly([(a0, c0, 0.05), (a1, c1, 0.05), (o1, p1, 0.05), (o0, p0, 0.05)], f"tile_{edge}")
        else:
            m.box(-ow / 2 - fr, ow / 2 + fr, b1, b1 + fr, 0.0, 0.05, f"tile_{edge}")
        m.pop()
    # the passage's sides and head
    m.box(-ow / 2 - 0.02, -ow / 2, yb, b1, -d / 2, d / 2, "wallred")
    m.box(ow / 2, ow / 2 + 0.02, yb, b1, -d / 2, d / 2, "wallred")
    if arched:
        pts = arc_pts(-ow / 2, ow / 2, b1, rise, 10)
        for (x0, y0_), (x1, y1_) in zip(pts[:-1], pts[1:]):
            m.poly([(x0, y0_, d / 2), (x1, y1_, d / 2), (x1, y1_, -d / 2), (x0, y0_, -d / 2)], "underside")
    else:
        m.poly([(-ow / 2, b1, d / 2), (ow / 2, b1, d / 2), (ow / 2, b1, -d / 2), (-ow / 2, b1, -d / 2)], "underside")
    m.box(-ow / 2, ow / 2, y0, yb + 0.02, -d / 2 - 0.3, d / 2 + 0.3, "step")
    if doors:
        for a0, a1 in ((-ow / 2 + 0.04, -0.02), (0.02, ow / 2 - 0.04)):
            m.box(a0, a1, yb, b1, -0.07, 0.07, "lacquer")
            for yy in np.linspace(yb + 0.5, b1 - 0.4, 5):
                for sg in (-1, 1):
                    for k in range(3):
                        xx = a0 + (a1 - a0) * (k + 0.5) / 3
                        m.box(xx - 0.04, xx + 0.04, yy - 0.04, yy + 0.04, sg * 0.07 - 0.02, sg * 0.07 + 0.02, "gold")
        if arched:
            pts = arc_pts(-ow / 2 + 0.04, ow / 2 - 0.04, b1, rise - 0.04, 8)
            m.poly([(0.0, b1, 0.0)] + [(px_, py_, 0.0) for px_, py_ in pts], "lacquer")
    # the frieze: a glazed band of imitation beams, a panel in the middle, the bracket band
    fz0 = ytop - 0.95
    m.box(-w / 2 - 0.06, w / 2 + 0.06, fz0, ytop, -d / 2 - 0.06, d / 2 + 0.06, "band")
    for sg in (1, -1):
        m.box(-w / 2 + 0.15, w / 2 - 0.15, fz0 + 0.12, fz0 + 0.3, sg * (d / 2 + 0.06), sg * (d / 2 + 0.1), f"tile_{edge}")
        if plaque_w > 0:
            m.box(-plaque_w / 2, plaque_w / 2, fz0 + 0.36, ytop - 0.06, sg * (d / 2 + 0.06), sg * (d / 2 + 0.12), "gold")
            m.box(-plaque_w / 2 + 0.08, plaque_w / 2 - 0.08, fz0 + 0.42, ytop - 0.12, sg * (d / 2 + 0.12), sg * (d / 2 + 0.13), "plaque")
    K.bracket_sets([-w / 2, -w / 6, w / 6, w / 2], w / 2, d / 2 + 0.06, ytop, ytop + 0.42, per_bay=2)
    K.roof(lambda a, b, c: (a, b, c), w / 2 + 0.75, d / 2 + 0.8, ytop + 0.4, ridge + g, form="xs", rolled=False, ju=JU["gate_hall"], tile=tile, edge=edge)
    out = {"ridge": m.world((0, g + ridge, 0)), "eave_L": m.world((-w / 2 - 0.75, ytop + 0.4, d / 2 + 0.8)), "eave_R": m.world((w / 2 + 0.75, ytop + 0.4, d / 2 + 0.8))}
    for sg, tag in ((1, "out"), (-1, "in")):
        p_ = m.world((0, 0, sg * (d / 2 + 0.9)))
        S.entry(f"{name}_{tag}", float(p_[0]), float(p_[2]))
    corners = [m.world((sx * (w / 2 + 0.25), 0, sq * (d / 2 + 0.25))) for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    m.pop()
    for i, c in enumerate(corners):
        S.JOINTS.append([f"{name}_{i}", float(c[0]), y0, float(c[2]), "gate base"])
    return out, g


def short_wall(cx, cz, rot, w, d, h, name):
    """A short red wall with a glazed disc on each face and a small glazed coping roof (the leaf's walls between the archway's gates; C)."""
    m.push(cx, 0, cz, rot)
    g = min(K.gy_local(a, b) for a in (-w / 2, w / 2) for b in (-d / 2, d / 2))
    m.box(-w / 2 - 0.1, w / 2 + 0.1, g - 0.15, g + 0.45, -d / 2 - 0.1, d / 2 + 0.1, "marble", skip=("bottom",))
    m.box(-w / 2, w / 2, g + 0.45, g + h, -d / 2, d / 2, "wallred")
    for sg in (1, -1):
        disc(0.0, g + 0.45 + (h - 0.45) * 0.55, sg * (d / 2 + 0.02), min(w, h) * 0.26, "tile_yellow")
        disc(0.0, g + 0.45 + (h - 0.45) * 0.55, sg * (d / 2 + 0.035), min(w, h) * 0.2, "disc")
    m.box(-w / 2 - 0.04, w / 2 + 0.04, g + h - 0.4, g + h, -d / 2 - 0.04, d / 2 + 0.04, "band")
    K.roof(lambda a, b, c: (a, b, c), w / 2 + 0.35, d / 2 + 0.45, g + h, g + h + 0.85, form="xs", rolled=False, ju=JU["gallery"], tile="yellow", edge="green")
    m.pop()
    return g


def timber_pailou(cx, cz, rot, w, name, kp=False):
    """A timber archway of four posts and three roofs 四柱三楼: red posts in stone clasps 夹杆石, painted beams, a plaque in the middle bay, a bracket band, small
    hip roofs in yellow with green edges, and the red diagonal props 戗杆 both ways (the leaf; S01's width; every height C)."""
    m.push(cx, 0, cz, rot)
    g = min(K.gy_local(a, b) for a in (-w / 2, w / 2) for b in (-2.8, 2.8))
    wm = w * 0.4
    ws = (w - wm) / 2
    posts = [-w / 2, -wm / 2, wm / 2, w / 2]
    m.cls = "doc"
    for k, s in enumerate(posts):
        top = g + (7.1 if k in (1, 2) else 6.0)
        m.prism([(s + 0.25 * math.cos(a), 0.25 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]], g - 0.15, top, "lacquer", top=True)
        m.box(s - 0.42, s + 0.42, g - 0.15, g + 1.5, -0.42, 0.42, "marble", skip=("bottom",))  # the clasp stones 夹杆石 (C)
        m.box(s - 0.46, s + 0.46, g + 1.4, g + 1.55, -0.46, 0.46, "marble")
        for sg in (1, -1):  # the props 戗杆
            strut((s, top - 2.3, sg * 0.2), (s, g - 0.1, sg * 2.7), 0.09, "lacquer")
            S.JOINTS.append([f"{name}_prop{k}{'S' if sg > 0 else 'N'}", float(m.world((s, 0, sg * 2.7))[0]), g - 0.1, float(m.world((s, 0, sg * 2.7))[2]), "prop foot"])
        S.JOINTS.append([f"{name}_post{k}", float(m.world((s, 0, 0))[0]), g - 0.15, float(m.world((s, 0, 0))[2]), "post foot"])
    # the middle bay: two beams with the plaque between, the bracket band, the roof
    m.box(-wm / 2, wm / 2, g + 4.25, g + 4.6, -0.16, 0.16, "band")
    m.box(-wm / 2 + 0.3, wm / 2 - 0.3, g + 4.6, g + 5.45, -0.12, 0.12, "gold")
    m.box(-wm / 2 + 0.42, wm / 2 - 0.42, g + 4.7, g + 5.35, 0.12, 0.13, "plaque")
    m.box(-wm / 2 + 0.42, wm / 2 - 0.42, g + 4.7, g + 5.35, -0.13, -0.12, "plaque")
    m.box(-wm / 2 - 0.1, wm / 2 + 0.1, g + 5.45, g + 5.95, -0.18, 0.18, "band")
    K.bracket_sets([-wm / 2, 0.0, wm / 2], wm / 2, 0.2, g + 5.95, g + 6.4, per_bay=2)
    K.roof(lambda a, b, c: (a, b, c), wm / 2 + 0.95, 1.25, g + 6.4, g + 7.95, form="wd", rolled=False, ju=JU["gate_hall"], tile="yellow", edge="green")
    for sg in (-1, 1):  # the side bays
        c = sg * (wm / 2 + ws / 2)
        m.box(c - ws / 2, c + ws / 2, g + 3.55, g + 3.85, -0.14, 0.14, "band")
        m.box(c - ws / 2 + 0.2, c + ws / 2 - 0.2, g + 3.85, g + 4.45, -0.1, 0.1, "bracket")
        m.box(c - ws / 2, c + ws / 2, g + 4.45, g + 4.85, -0.16, 0.16, "band")
        m.box(c - ws / 2, c + ws / 2, g + 4.85, g + 5.2, -0.3, 0.3, "bracket")
        m.push(c, 0, 0)
        K.roof(lambda a, b, cc: (a, b, cc), ws / 2 + 0.7, 1.05, g + 5.2, g + 6.45, form="wd", rolled=False, ju=JU["gate_hall"], tile="yellow", edge="green")
        m.pop()
    out = {"ridge": m.world((0, g + 7.95, 0)), "post_L": m.world((-w / 2, g, 0)), "post_R": m.world((w / 2, g, 0))}
    for sg, tag in ((1, "S"), (-1, "N"), (0, "C")):  # either side of the middle bay, and its middle (a way through the archway's box ends there)
        p_ = m.world((0, 0, sg * 1.2))
        S.entry(f"{name}_{tag}", float(p_[0]), float(p_[2]))
    fps = [[m.world((s + a, 0, b)) for a, b in ((-0.42, -0.42), (0.42, -0.42), (0.42, 0.42), (-0.42, 0.42))] for s in posts]
    m.pop()
    for fp in fps:
        S.FOOTPRINTS.append([(float(c[0]), float(c[2])) for c in fp])
    if kp:
        S.kp(f"{name}_ridge", out["ridge"])
    return out


def octagon(r, n=8, off=math.pi / 8):
    return [(r * math.cos(off + 2 * math.pi * k / n), r * math.sin(off + 2 * math.pi * k / n)) for k in range(n)]


def stele_pavilion(cx, cz, name):
    """An octagonal stele pavilion 碑亭 with double eaves in yellow tile over a marble stele (S05, Malone, the leaf; S01's octagon; walls, doors and heights C)."""
    m.push(cx, 0, cz, 0.0)
    R_pl, R_w = 3.75, 3.05  # circumradius of the platform and the wall's octagon
    g = min(K.gy_local(*p) for p in octagon(R_pl))
    plt = g + 0.6
    m.cls = "doc"
    m.prism(octagon(R_pl), g - 0.15, plt, "marble")
    for side, rot in (("S", 0.0), ("N", math.pi)):  # flights front and back (C)
        m.push(0, 0, 0, rot)
        for k in range(4):
            yk = plt - (k + 1) * 0.15
            m.box(-0.9, 0.9, g - 0.15, yk, R_pl * math.cos(math.pi / 8) + k * 0.3, R_pl * math.cos(math.pi / 8) + (k + 1) * 0.3, "step")
        f = m.world((0, 0, R_pl * math.cos(math.pi / 8) + 1.35))
        S.entry(f"{name}_{side}", float(f[0]), float(f[2]))
        m.pop()
    y_wall = plt + 3.4
    oc = octagon(R_w)
    for k in range(8):
        a, b = oc[k], oc[(k + 1) % 8]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        nrm = math.atan2(mx, mz)  # the face's outward direction as a Mesh rot (0 faces +z)
        m.push(mx, 0, mz, nrm)
        door = k % 2 == 1  # the faces turned to the four quarters (C)
        holes = [(-0.6, 0.6, plt, plt + 1.9, 0.6)] if door else []
        PARTS.wall_holes(-L / 2, L / 2, plt, y_wall, holes, "wallred")
        PARTS.wall_holes(-L / 2, L / 2, plt, y_wall, holes, "wallred", d=-0.5)
        if door:
            m.box(-0.62, -0.6, plt, plt + 1.9, -0.5, 0.0, "wallred")
            m.box(0.6, 0.62, plt, plt + 1.9, -0.5, 0.0, "wallred")
            pts = arc_pts(-0.6, 0.6, plt + 1.9, 0.6, 8)
            for (x0, y0_), (x1, y1_) in zip(pts[:-1], pts[1:]):
                m.poly([(x0, y0_, 0.0), (x1, y1_, 0.0), (x1, y1_, -0.5), (x0, y0_, -0.5)], "underside")
        m.pop()
    m.box(-R_w * 0.92, R_w * 0.92, y_wall - 0.02, y_wall, -R_w * 0.92, R_w * 0.92, "underside")
    m.prism(octagon(R_w + 0.06), y_wall - 0.55, y_wall, "band", top=False)
    m.prism(octagon(R_w + 0.25), y_wall, y_wall + 0.35, "bracket", top=False)
    # the lower eave: an octagonal skirt
    lo_o, lo_i = octagon(R_w + 1.35), octagon(R_w - 0.6)
    y_lo, y_lo2 = y_wall + 0.25, y_wall + 1.0
    for k in range(8):
        a0, b0, a1, b1 = lo_o[k], lo_o[(k + 1) % 8], lo_i[k], lo_i[(k + 1) % 8]
        m.poly([(a0[0], y_lo + 0.25, a0[1]), (b0[0], y_lo + 0.25, b0[1]), (b1[0], y_lo2, b1[1]), (a1[0], y_lo2, a1[1])], "tile_yellow")
        m.poly([(a0[0], y_lo + 0.25, a0[1]), (b0[0], y_lo + 0.25, b0[1]), (b0[0], y_lo - 0.05, b0[1]), (a0[0], y_lo - 0.05, a0[1])], "fascia")
        m.poly([(a0[0], y_lo - 0.05, a0[1]), (b0[0], y_lo - 0.05, b0[1]), (b1[0], y_lo - 0.05, b1[1]), (a1[0], y_lo - 0.05, a1[1])], "underside")
        m.poly([(a0[0], y_lo + 0.25, a0[1]), (a1[0], y_lo2, a1[1]), (a1[0], y_lo2 + 0.18, a1[1]), (a0[0], y_lo + 0.43, a0[1])], "ridge_yellow")
    # the upper drum and the upper roof
    R_u = R_w - 0.75
    y_u0, y_u1 = y_lo2 - 0.1, y_lo2 + 1.15
    m.prism(octagon(R_u), y_u0, y_u1 - 0.45, "wallred", top=False)
    m.prism(octagon(R_u + 0.05), y_u1 - 0.45, y_u1, "band", top=False)
    m.prism(octagon(R_u + 0.2), y_u1, y_u1 + 0.3, "bracket", top=False)
    hx = (R_u + 1.25) * math.cos(math.pi / 8)
    K.pyramid(hx, hx, y_u1 + 0.25, y_u1 + 3.3, sides=8, tile="yellow")
    # the stele inside on its base (Malone)
    m.box(-0.55, 0.55, plt, plt + 0.6, -0.3, 0.3, "marble_shade")
    m.box(-0.45, 0.45, plt + 0.6, plt + 3.0, -0.15, 0.15, "marble")
    tip = m.world((0, y_u1 + 3.3 + 0.9, 0))
    foot = [m.world((p[0], 0, p[1])) for p in octagon(R_pl)]
    m.pop()
    S.kp(f"{name}_top", tip)
    S.kp(f"{name}_foot_S", (cx, S.gy(cx, cz + R_pl * math.cos(math.pi / 8)), cz + R_pl * math.cos(math.pi / 8)), anchor=True)
    S.kp(f"{name}_low_eave_S", (cx, y_lo + 0.25, cz + (R_w + 1.35) * math.cos(math.pi / 8)))
    S.FOOTPRINTS.append([(float(c[0]), float(c[2])) for c in foot])
    for i, c in enumerate(foot[::2]):
        S.JOINTS.append([f"{name}_pl_{i}", float(c[0]), g - 0.15, float(c[2]), "platform foot"])
    REPORT["halls"][name] = {"across_m": round(2 * R_pl * math.cos(math.pi / 8), 2), "platform_m": 0.6, "low_eave_m": round(y_lo + 0.25 - g, 2), "top_m": round(y_u1 + 4.2 - g, 2)}


def burner(cx, cz, rot, name):
    """A green-glazed burner 燎炉 (Malone; S05 燎亭): a marble base, a glazed body with an arched mouth, a small glazed hip-gable roof; its form C."""
    m.push(cx, 0, cz, rot)
    g = min(K.gy_local(a, b) for a in (-1.0, 1.0) for b in (-0.9, 0.9))
    m.box(-1.05, 1.05, g - 0.15, g + 0.45, -0.9, 0.9, "marble", skip=("bottom",))
    m.box(-0.8, 0.8, g + 0.45, g + 2.1, -0.65, 0.65, "tile_green")
    m.box(-0.88, 0.88, g + 2.1, g + 2.3, -0.72, 0.72, "band")
    pts = arc_pts(-0.32, 0.32, g + 1.1, 0.32, 8)
    m.poly([(-0.32, g + 0.65, 0.66), (0.32, g + 0.65, 0.66)] + [(px_, py_, 0.66) for px_, py_ in reversed(pts)], "underside")
    K.roof(lambda a, b, c: (a, b, c), 1.05, 0.9, g + 2.3, g + 3.2, form="xs", rolled=False, ju=JU["gallery"], tile="green", edge="green")
    m.pop()
    S.FOOTPRINTS.append([(cx - 1.1, cz - 1.1), (cx + 1.1, cz - 1.1), (cx + 1.1, cz + 1.1), (cx - 1.1, cz + 1.1)])
    S.joint(f"{name}_foot", cx, cz, "base foot", y=g - 0.15)


def well_pavilion(cx, cz, side, name):
    """A well pavilion 井亭 (S05; Malone's covered wells): four red posts on a low platform round a stone well curb, a 盝顶 roof open in the middle (C)."""
    m.push(cx, 0, cz, 0.0)
    g = min(K.gy_local(a, b) for a in (-side / 2 - 0.4, side / 2 + 0.4) for b in (-side / 2 - 0.4, side / 2 + 0.4))
    plt = g + 0.3
    hs = side / 2
    m.box(-hs - 0.45, hs + 0.45, g - 0.15, plt, -hs - 0.45, hs + 0.45, "marble", skip=("bottom",))
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.prism([(sx * hs + 0.14 * math.cos(a), sz * hs + 0.14 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 7)[:-1]], plt, plt + 2.9, "lacquer", top=False)
    K.ring_band(hs, hs, 0.22, plt + 2.5, plt + 2.95, 0, "band")
    m.lathe([(0.55, plt), (0.55, plt + 0.55), (0.4, plt + 0.6), (0.0, plt + 0.6)], 10, "marble_shade")
    lo = [(-hs - 0.85, hs + 0.85), (hs + 0.85, hs + 0.85), (hs + 0.85, -hs - 0.85), (-hs - 0.85, -hs - 0.85)]
    hi = [(-hs * 0.45, hs * 0.45), (hs * 0.45, hs * 0.45), (hs * 0.45, -hs * 0.45), (-hs * 0.45, -hs * 0.45)]
    m.frustum(lo, hi, plt + 2.95, plt + 3.75, "tile_yellow")
    m.prism(hi, plt + 3.75, plt + 3.9, "ridge_yellow", top=False)
    m.poly([(-hs - 0.85, plt + 2.95, hs + 0.85), (hs + 0.85, plt + 2.95, hs + 0.85), (hs + 0.85, plt + 2.95, -hs - 0.85), (-hs - 0.85, plt + 2.95, -hs - 0.85)], "underside")
    m.pop()
    S.FOOTPRINTS.append([(cx - hs - 0.45, cz - hs - 0.45), (cx + hs + 0.45, cz - hs - 0.45), (cx + hs + 0.45, cz + hs + 0.45), (cx - hs - 0.45, cz + hs + 0.45)])
    S.joint(f"{name}_foot", cx, cz + hs + 0.45, "platform foot", y=g - 0.15)


def terrace(poly_pts, top, name, mat="marble"):
    """A raised terrace over an outline: faces from just below the ground (followed along the edges) to the top, a coping band, the floor; its corners joints."""
    bots = S.skirt(poly_pts, top, mat)
    m.flat(poly_pts, top, "pave")
    for i, (x, z) in enumerate(poly_pts):
        S.JOINTS.append([f"{name}_{i}", x, bots[i], z, "terrace foot"])
    S.FOOTPRINTS.append([tuple(p) for p in poly_pts])
    S.deck(name, top, poly_pts)
    RAISED.append((Polygon(poly_pts), top))
    return min(bots)


def edge_rails(poly_pts, top, gaps, skip_back_z=None, h=0.9):
    """A stone balustrade 0.2 m in from a terrace's edges, open at the flights (gaps: polygons) and along its back (an edge whose middle lies north of skip_back_z)."""
    inner = Polygon(poly_pts).buffer(-0.2, join_style=2)
    pts = list(inner.exterior.coords)
    for a, b in zip(pts[:-1], pts[1:]):
        if skip_back_z is not None and (a[1] + b[1]) / 2 < skip_back_z and abs(a[1] - b[1]) < 0.3:
            continue
        rail_poly([a, b], lambda x, z: top, gaps=gaps, h=h, step=1.6, mat="marble", panel=True)


# ============================================================ 安佑宫 YM17-10 and its terrace
m.cls = "doc"
cols = sorted(READ["hall_cols"], key=lambda p: p[0])
xs01 = [p[0] for p in cols]
bays = [round(b, 3) for b in np.diff(xs01)]
rows = sorted(READ["hall_rows"], key=lambda p: p[1])
zs01 = [p[1] for p in rows]
spans = [round(s, 3) for s in np.diff(zs01)]  # back to front
HALL_ZC = (zs01[0] + zs01[-1]) / 2
REPORT["hall_s01"] = {"bays_m": bays, "spans_back_to_front_m": spans, "between_end_columns_m": round(xs01[-1] - xs01[0], 2), "between_rows_m": round(zs01[-1] - zs01[0], 2),
                      "s01_middle_off_axis_m": round((xs01[0] + xs01[-1]) / 2 - AXIS, 2)}
px0, px1, pz0, pz1 = rect("platform")
yx0, yx1, yz0, yz1 = rect("yuetai")
pw, yw = (px1 - px0) / 2, (yx1 - yx0) / 2
T_PTS = [(AXIS - pw, pz0), (AXIS + pw, pz0), (AXIS + pw, yz0), (AXIS + yw, yz0), (AXIS + yw, yz1), (AXIS - yw, yz1), (AXIS - yw, yz0), (AXIS - pw, yz0)]
court_g = max(S.gy(AXIS + s, yz1 + 0.5) for s in (-yw, 0.0, yw))
YT_TOP = court_g + YT_H
REPORT["terrace"] = {"platform_m": [round(2 * pw, 2), round(yz0 - pz0, 2)], "yuetai_m": [round(2 * yw, 2), round(yz1 - yz0, 2)], "top_above_court_m": YT_H,
                     "court_ground_y": round(court_g, 3)}
terrace(T_PTS, YT_TOP, "terrace")
# the flights: three at the front, one on each side of the 月台, their runs as S01 draws them
m.push(AXIS, 0, (yz0 + yz1) / 2)
fl = {}
for nm, side in (("flight_C", "front"), ("flight_W", "front"), ("flight_E", "front"), ("flight_SW", "left"), ("flight_SE", "right")):
    x0, x1, z0, z1 = rect(nm)
    if side == "front":
        off, wdt, run = (x0 + x1) / 2 - AXIS, x1 - x0, z1 - yz1
        if nm == "flight_C":
            off = 0.0
    else:
        off, wdt, run = (z0 + z1) / 2 - (yz0 + yz1) / 2, z1 - z0, (yx0 - x0) if side == "left" else (x1 - yx1)
    n_steps = max(1, round((YT_TOP - court_g) / 0.15))
    f = K.flight(side, off, yw, (yz1 - yz0) / 2, YT_TOP, wdt, tread=max(0.3, run / n_steps))
    fl[nm] = (f, off, wdt, run, side)
m.pop()
gaps_T = []
for nm, (f, off, wdt, run, side) in fl.items():
    if f is None:
        continue
    m.push(AXIS, 0, (yz0 + yz1) / 2)
    fw = m.world(f)
    m.pop()
    S.entry(f"terrace_{nm}", float(fw[0]), float(fw[2]), float(fw[1]))
    if side == "front":
        gaps_T.append(Polygon([(AXIS + off - wdt / 2 - 0.3, yz1 - 1.0), (AXIS + off + wdt / 2 + 0.3, yz1 - 1.0), (AXIS + off + wdt / 2 + 0.3, yz1 + 1.0), (AXIS + off - wdt / 2 - 0.3, yz1 + 1.0)]))
    else:
        xe = AXIS - yw if side == "left" else AXIS + yw
        zc_ = (yz0 + yz1) / 2 + off
        gaps_T.append(Polygon([(xe - 1.0, zc_ - wdt / 2 - 0.3), (xe + 1.0, zc_ - wdt / 2 - 0.3), (xe + 1.0, zc_ + wdt / 2 + 0.3), (xe - 1.0, zc_ + wdt / 2 + 0.3)]))
REPORT["flights"] = {nm: {"width_m": round(v[2], 2), "run_m": round(v[3], 2)} for nm, v in fl.items()}
# the ramp stone 御路 in the middle flight (S943: 1.30 m wide), its carving as raised blocks (C)
fC, offC, wC, runC, _ = fl["flight_C"]
z_top, z_foot = yz1, yz1 + max(runC, 0.3 * round((YT_TOP - court_g) / 0.15))
yF = S.gy(AXIS, z_foot)
for sx in (-1, 1):
    m.poly([(AXIS + sx * 0.65, YT_TOP + 0.04, z_top), (AXIS + sx * 0.65, yF + 0.04, z_foot), (AXIS + sx * 0.65, yF - 0.2, z_foot), (AXIS + sx * 0.65, YT_TOP - 0.3, z_top)], "marble_shade")
m.poly([(AXIS - 0.65, YT_TOP + 0.04, z_top), (AXIS + 0.65, YT_TOP + 0.04, z_top), (AXIS + 0.65, yF + 0.04, z_foot), (AXIS - 0.65, yF + 0.04, z_foot)], "marble_shade")
m.cls = "fill"
for k in range(7):
    t = (k + 0.5) / 7
    zz, yy = z_top + (z_foot - z_top) * t, YT_TOP + (yF - YT_TOP) * t + 0.04
    a = 0.3 * math.sin(k * 1.7)
    m.box(AXIS + a - 0.22, AXIS + a + 0.22, yy - 0.05, yy + 0.09, zz - 0.18, zz + 0.18, "marble")
m.cls = "doc"
S.kp("ramp_top", (AXIS, YT_TOP, z_top))
S.kp("ramp_foot", (AXIS, yF, z_foot), anchor=True)
# the balustrade round the terrace (the leaf), open at the flights and along the back (on the inner wall)
edge_rails(T_PTS, YT_TOP, gaps_T, skip_back_z=pz0 + 0.6)
# the hall on the terrace: S01's grid centred on the axis, a 台明 0.3 m (C)
hb = bays
hd_spans = list(reversed(spans))  # front to back for the kit
Hh = hall_spec(AXIS, HALL_ZC, 0.0, hb, hd_spans, 0.9, 0.3, HALL_COL, "xs", False, "doc", bracket=True, ju="grand_hall", pf=hd_spans[0], pb=0.0, ps=0.0, tile="yellow")
Hh["base"] = YT_TOP
Hh["foot"] = YT_TOP - 0.2
Hh["db"] = 1
Hh["eave"] = round(0.3 + HALL_COL + 0.85, 2)
Hh["ridge"] = round(Hh["eave"] + HALL_RISE, 2)  # the upper roof: the grand_hall class's rise over the inner spans (C; the leaf's fit tests it)
Hh["upper"] = 0.34
Hh["dr"] = list(range(len(hb)))  # red lattice doors in every bay (the leaf)
Hh["rr"] = "w"
Hh["side_wall"] = True
Hh["dia"] = 0.5
Hh["per_bay"] = 1
Hh["st"] = {"front": [0.0]}
Hh["fw"] = {"front": hb[len(hb) // 2]}
fw_hall = draw("hall", Hh)
# the plaque under the upper eave, on the upper storey's band, as on the imperial double-eaved halls (its place and the board C)
m.push(Hh["x"], 0, Hh["z"], Hh["rot"])
_CQ = Hh["hd"] - Hh["e"]
_inQ = _CQ - max(Hh["pf"], Hh["pb"], 1.5)
_yUp = Hh["base"] + Hh["eave"] + (Hh["ridge"] - Hh["eave"]) * Hh["upper"]
_q = _inQ + 0.42
m.box(-0.85, 0.85, _yUp - 1.55, _yUp - 0.05, _q - 0.05, _q + 0.05, "gold")
m.poly([(-0.72, _yUp - 1.45, _q + 0.056), (0.72, _yUp - 1.45, _q + 0.056), (0.72, _yUp - 0.15, _q + 0.056), (-0.72, _yUp - 1.45 + 1.3, _q + 0.056)], "plaque")
S.kp("hall_plaque", m.world((0, _yUp - 0.8, _q + 0.06)))
m.pop()
REPORT["halls"]["hall"]["above_court_m"] = {"eave": round(YT_TOP - court_g + Hh["eave"], 2), "ridge": round(YT_TOP - court_g + Hh["ridge"], 2)}
# the bronzes on the 月台 (E1564, Malone; places and forms C)
m.cls = "fill"
zb_ = yz1 - 2.2
for sx in (-1, 1):
    censer(AXIS + sx * (yw - 2.0), zb_, YT_TOP, f"censer_{'W' if sx < 0 else 'E'}")
    crane(AXIS + sx * 4.6, yz0 + 3.0, YT_TOP, 0.0)
    deer(AXIS + sx * 7.8, yz0 + 3.3, YT_TOP, 0.0)
m.cls = "doc"

# ============================================================ the inner court: side halls, stele pavilions, burners, the axis way
for nm, rot in (("peidian_W", math.pi / 2), ("peidian_E", -math.pi / 2)):
    x0, x1, z0, z1 = rect(nm)
    L, D = z1 - z0, x1 - x0
    Hp = hall_spec((x0 + x1) / 2, (z0 + z1) / 2, rot, [L / 5 - 0.32] * 5, [1.5, D - 1.5 - 1.6], 0.8, 0.6, 3.6, "xs", False, "doc", ju="main_hall", pf=1.5, tile="yellow")
    Hp["dr"] = [2]
    draw(nm, Hp)
for nm in ("beiting_W", "beiting_E"):
    stele_pavilion(*mid(nm), nm)
m.cls = "fill"
for nm in ("liaoting_W", "liaoting_E"):
    burner(*mid(nm), 0.0, nm)
m.cls = "doc"

# ============================================================ 安佑门 YM17-06 on its terrace, the inner wall and its side gates
gx0, gx1, gz0, gz1 = rect("gate")
G_SPAN = 56 * 0.219  # S01: the end columns at x 959 and 1015 (12.3 m)
G_DEP = rect("gate")[3] - rect("gate")[2] - 2 * 0.2  # S01's rows 1358-1386, less the line's width
g_b = [G_SPAN * f for f in (0.19, 0.2, 0.22, 0.2, 0.19)]
iw_x0, iw_x1, iw_z0, iw_z1 = rect("inner_wall")
GATE_Z = iw_z1  # the middle row on the wall's line
G_PL = 1.2
Hg = hall_spec(AXIS, GATE_Z, 0.0, g_b, [G_DEP / 2, G_DEP / 2], 0.9, G_PL, 3.8, "xs", False, "doc", bracket=True, ju="gate_hall", tile="yellow")
Hg["k"] = "gate"
Hg["dr"] = [1, 2, 3]
Hg["st"] = {"back": [0.0]}
Hg["fw"] = {"back": g_b[2]}
# its terrace before it (the leaf; Malone's marble terrace): the platform carried 3.5 m forward, a balustrade, three flights (C)
G_TERR = 2.5
g_court = max(S.gy(AXIS + s, GATE_Z + Hg["hd"] + G_TERR + 0.5) for s in (-Hg["hf"], 0, Hg["hf"]))
G_TOP = max(Hg["base"], g_court) + G_PL
Hg["base"] = G_TOP - G_PL
gt = [(AXIS - Hg["hf"], GATE_Z + Hg["hd"] - 0.05), (AXIS + Hg["hf"], GATE_Z + Hg["hd"] - 0.05), (AXIS + Hg["hf"], GATE_Z + Hg["hd"] + G_TERR), (AXIS - Hg["hf"], GATE_Z + Hg["hd"] + G_TERR)]
terrace(gt, G_TOP, "gate_terrace")
fw_gate = draw("gate", Hg)
plaque(Hg, 1, w=2.0, h=0.9, name="gate_plaque")
m.push(AXIS, 0, GATE_Z + Hg["hd"] + G_TERR / 2)
gfl = {}
for off, wdt in ((0.0, g_b[2]), (-(g_b[2] / 2 + g_b[1] + g_b[0] / 2), g_b[0]), (g_b[2] / 2 + g_b[1] + g_b[0] / 2, g_b[0])):
    f = K.flight("front", off, Hg["hf"], G_TERR / 2, G_TOP, wdt)
    if f:
        gfl[off] = (m.world(f), wdt)
m.pop()
gaps_G = []
for off, (fw, wdt) in gfl.items():
    S.entry(f"gate_front_{off:+.1f}", float(fw[0]), float(fw[2]), float(fw[1]))
    zf_ = GATE_Z + Hg["hd"] + G_TERR
    gaps_G.append(Polygon([(AXIS + off - wdt / 2 - 0.3, zf_ - 1.0), (AXIS + off + wdt / 2 + 0.3, zf_ - 1.0), (AXIS + off + wdt / 2 + 0.3, zf_ + 1.0), (AXIS + off - wdt / 2 - 0.3, zf_ + 1.0)]))
edge_rails(gt, G_TOP, gaps_G, skip_back_z=GATE_Z + Hg["hd"] + 0.6)
REPORT["halls"]["gate"].update({"terrace_depth_m": G_TERR, "top_above_court_m": round(G_TOP - g_court, 2), "between_end_columns_m": round(G_SPAN, 2), "depth_m_s01": round(G_DEP, 2)})
# the inner wall (Malone: red, yellow glazed coping), broken at the gate and the two side gates
IW_H = 4.2
gsw, gse = mid("gate_side_W"), mid("gate_side_E")
wall_run([(iw_x0, iw_z1), (iw_x0, iw_z0), (iw_x1, iw_z0), (iw_x1, iw_z1)], IW_H, "iwall")
wall_run([(iw_x0, iw_z1), (iw_x1, iw_z1)], IW_H, "iwall_S", gaps=[(AXIS, iw_z1, Hg["hf"] + 0.05), (gsw[0], iw_z1, 1.9), (gse[0], iw_z1, 1.9)])
for nm, (x, z) in (("gate_side_W", gsw), ("gate_side_E", gse)):
    wall_gate(x, iw_z1, 0.0, nm, w=2.4, h=4.4)
for tag, x in (("SW", iw_x0), ("SE", iw_x1)):
    S.kp(f"iwall_{tag}_top", (x, S.gy(x, iw_z1) + IW_H, iw_z1))
# the axis way in the inner court, from the gate's back flight to the terrace's middle flight (C)
z_w0, z_w1 = z_foot + 0.3, GATE_Z - Hg["hd"] - 2.0
m.cls = "doc"
pave([(AXIS - 2.6, z_w0), (AXIS + 2.6, z_w0), (AXIS + 2.6, z_w1), (AXIS - 2.6, z_w1)], "way_inner", dy=0.1, step=4.0, mat="marble")

# ============================================================ between the walls: the inner moat and its bridges, the waiting rooms, the wells
m.cls = "doc"
lining(MOAT_IN, WY_IN, "moat_in")
gaps_in = []
for k, (bx, bz) in enumerate(READ["bridges_inner"]):
    x_b = AXIS if k == 2 else bx
    w_b = 3.2 if k == 2 else 2.4
    gaps_in.append(arch_bridge(f"bridge_in_{k}", x_b, bz, MOAT_IN, WY_IN, w_b, hump=0.45 if k in (1, 2, 3) else 0.3, abut=1.3, arched=k in (1, 2, 3), kp=k == 2))
m.cls = "fill"
bank_rails(MOAT_IN, gaps_in, "moat_in", h=0.85, mat="marble", panel=True, step=1.8)
for nm, rot in (("chaofang_W", math.pi / 2), ("chaofang_E", -math.pi / 2)):
    x0, x1, z0, z1 = rect(nm)
    L, D = z1 - z0, x1 - x0
    Hc = hall_spec((x0 + x1) / 2, (z0 + z1) / 2, rot, [L / 5 - 0.28] * 5, [D - 1.4], 0.7, 0.45, 3.2, "xs", True, "fill", ju="side_hall", tile="grey")
    draw(nm, Hc, kp=False)
for nm in ("jingting_W", "jingting_E"):
    x0, x1, z0, z1 = rect(nm)
    well_pavilion((x0 + x1) / 2, (z0 + z1) / 2, 2.4, nm)
m.cls = "doc"

# ============================================================ the outer wall, its five gates, the north gate, the corner yards
ow_x0, ow_x1, ow_z0, ow_z1 = rect("outer_wall")
OW_H = 4.4
gS = READ["gates_S"]
cW, cE = (gS[0][0] + gS[1][0]) / 2, (gS[4][0] + gS[5][0]) / 2
dG = (cE - cW) / 2
three = [(AXIS - dG, 3.6, 3.2, 4.9, 7.0, "gate3_W"), (AXIS, 5.0, 3.8, 5.6, 8.0, "gate3_C"), (AXIS + dG, 3.6, 3.2, 4.9, 7.0, "gate3_E")]
gow, goe, gn = mid("gate_out_W"), mid("gate_out_E"), mid("gate_N")
gaps_ow = [(x, ow_z1, w / 2 + 0.05) for x, w, *_ in three] + [(gow[0], ow_z1, 1.9), (goe[0], ow_z1, 1.9)]
wall_run([(ow_x0, ow_z1), (ow_x0, ow_z0), (ow_x1, ow_z0), (ow_x1, ow_z1)], OW_H, "owall", gaps=[(AXIS, ow_z0, 4.6)])
wall_run([(ow_x0, ow_z1), (ow_x1, ow_z1)], OW_H, "owall_S", gaps=gaps_ow)
G3 = {}
for x, w, ho, hb_, rg, nm in three:
    out, g = glazed_gate(x, ow_z1, 0.0, w, 2.3, ho, hb_, rg, nm, doors=True, arched=True, plaque_w=1.6 if nm == "gate3_C" else 0.0)
    G3[nm] = out
    S.kp(f"{nm}_ridge", out["ridge"])
m.cls = "fill"
for nm, (x, z) in (("gate_out_W", gow), ("gate_out_E", goe)):
    S.kp(f"{nm}_ridge", wall_gate(x, ow_z1, 0.0, nm, w=2.6, h=4.6))
Hn = hall_spec(AXIS, ow_z0, 0.0, [2.4, 2.9, 2.4], [2.1, 2.1], 0.7, 0.6, 3.4, "xs", False, "fill", ju="gate_hall", tile="yellow")
Hn["k"] = "gate"
Hn["dr"] = [1]
Hn["st"] = {"front": [0.0], "back": [0.0]}
draw("gate_N", Hn, kp=False)
m.cls = "doc"
for tag, x in (("SW", ow_x0), ("SE", ow_x1)):
    S.kp(f"owall_{tag}_top", (x, S.gy(x, ow_z1) + OW_H, ow_z1))
# the corner yards and their ranges (S01; unnamed, C)
m.cls = "fill"
for yard, rng, face in (("yard_NW", "range_NW", math.pi / 2), ("yard_NE", "range_NE", -math.pi / 2)):
    pts = READ[yard]
    wall_run(pts, 3.4, yard, gaps=[((pts[1][0] + pts[2][0]) / 2, pts[1][1], 1.5)], thick=0.8, cap="grey")
    wall_gate((pts[1][0] + pts[2][0]) / 2, pts[1][1], 0.0, f"{yard}_gate", w=2.0, h=3.4, thick=0.8, tile="grey", edge=None)
    x0, x1, z0, z1 = rect(rng)
    L, D = z1 - z0, x1 - x0
    nb = max(4, round(L / 3.3))
    Hr = hall_spec((x0 + x1) / 2, (z0 + z1) / 2, face, [L / nb - 0.6 / nb * 2] * nb, [max(D - 1.2, 2.6)], 0.6, 0.45, 3.0, "ys", True, "fill", ju="side_hall", tile="grey")
    draw(rng, Hr, kp=False)
m.cls = "doc"

# ============================================================ the forecourt: the qilin, the three timber archways, the paving
m.cls = "doc"
for k, (qx, qz) in enumerate(READ["qilin"]):
    qilin(qx, qz, 0.0, f"qilin_{'W' if k == 0 else 'E'}")
PL = {}
for nm, rot in (("pailou_W", math.pi / 2), ("pailou_E", -math.pi / 2), ("pailou_S", 0.0)):
    x0, x1, z0, z1 = rect(nm)
    w = (z1 - z0) if nm != "pailou_S" else (x1 - x0)
    cx = (x0 + x1) / 2  # as S01 draws it (the south one 1.2 m west of the mean axis: within S01's spread, REPORT axis_reads)
    PL[nm] = timber_pailou(cx, (z0 + z1) / 2, rot, w, nm, kp=True)
    REPORT["halls"][nm] = {"frontage_m": round(w, 2), "ridge_m": 7.95}

# ============================================================ the outer moat 月河 and its five bridges
m.cls = "doc"
lining(MOAT_OUT, WY_OUT, "moat_out")
gaps_out = []
for k, (bx, bz) in enumerate(READ["bridges_outer"]):
    x_b = AXIS if k == 2 else bx
    w_b = {0: 2.4, 1: 3.0, 2: 4.2, 3: 3.0, 4: 2.4}[k]
    gaps_out.append(arch_bridge(f"bridge_out_{k}", x_b, bz, MOAT_OUT, WY_OUT, w_b, hump=0.7 if k in (1, 2, 3) else 0.35, abut=1.8, arched=k in (1, 2, 3), kp=k in (1, 2, 3)))
bank_rails(MOAT_OUT, gaps_out, "moat_out", h=1.0, mat="rail", panel=False, step=2.0)
# the paving: the forecourt between the side archways, from the outer wall to the south archway; the axis way to the middle bridge and between the walls (C)
pw_x0, pw_x1 = rect("pailou_W")[1] + 1.6, rect("pailou_E")[0] - 1.6
z_fc0, z_fc1 = ow_z1 + 1.4, rect("pailou_S")[3] + 2.4
pave([(pw_x0, z_fc0), (pw_x1, z_fc0), (pw_x1, z_fc1), (pw_x0, z_fc1)], "forecourt", dy=0.04, step=5.0)
zb_n = moat_span(MOAT_OUT, AXIS, READ["bridges_outer"][2][1])[0] - 1.8
pave([(AXIS - 2.4, z_fc1), (AXIS + 2.4, z_fc1), (AXIS + 2.4, zb_n - 0.5), (AXIS - 2.4, zb_n - 0.5)], "way_forecourt", dy=0.1, step=4.0, mat="marble")
zi_s = moat_span(MOAT_IN, AXIS, READ["bridges_inner"][2][1])[1] + 1.3
pave([(AXIS - 2.4, zi_s + 0.5), (AXIS + 2.4, zi_s + 0.5), (AXIS + 2.4, ow_z1 - 1.6), (AXIS - 2.4, ow_z1 - 1.6)], "way_between_S", dy=0.1, step=4.0, mat="marble")
zi_n = moat_span(MOAT_IN, AXIS, READ["bridges_inner"][2][1])[0] - 1.3
z_gf = max(f[0][2] for f in gfl.values()) if gfl else GATE_Z + Hg["hd"] + G_TERR + 2.4
if zi_n - 0.5 > z_gf + 0.3:
    pave([(AXIS - 2.4, z_gf + 0.3), (AXIS + 2.4, z_gf + 0.3), (AXIS + 2.4, zi_n - 0.5), (AXIS - 2.4, zi_n - 0.5)], "way_between_N", dy=0.1, step=4.0, mat="marble")

# ============================================================ 致孚殿 YM17-05 in its yard
m.cls = "doc"
zx0, zx1, zz0, zz1 = rect("zhifu_yard")
zg = mid("zhifu_gate")
wall_run([(zx0, zz0), (zx1, zz0), (zx1, zz1), (zx0, zz1), (zx0, zz0)], 3.4, "zhifu_wall", gaps=[(zx0, zg[1], 1.6)], thick=0.8)
wall_gate(zx0, zg[1], math.pi / 2, "zhifu_gate", w=2.2, h=3.6, thick=0.8)
hx0, hx1, hz0, hz1 = rect("zhifu_hall")
Hz = hall_spec((hx0 + hx1) / 2, (hz0 + hz1) / 2, -math.pi / 2, [(hz1 - hz0 - 1.4) / 3] * 3, [1.4, hx1 - hx0 - 1.4 - 1.4], 0.7, 0.5, 3.4, "xs", False, "doc", ju="small_house", pf=1.4, tile="yellow")
Hz["dr"] = [1]
draw("zhifu", Hz)

# ============================================================ 鸿慈永祜坊 YM17-01 and the four 华表 YM17-02
m.cls = "doc"
hbx = [p[0] for p in READ["huabiao"]]
hbz = [p[1] for p in READ["huabiao"]]
HB_C = (float(np.mean(hbx)), float(np.mean(hbz)))
lx0, lx1, lz0, lz1 = rect("liulifang")
LF_W, LF_D = lx1 - lx0, max(lz1 - lz0, 2.4)
LF_X, LF_Z = HB_C[0], (lz0 + lz1) / 2
REPORT["liulifang"] = {"s01_length_m": round(LF_W, 2), "s01_depth_m": round(lz1 - lz0, 2), "s01_off_square_middle_m": round((lx0 + lx1) / 2 - HB_C[0], 2),
                       "square_m": [round((hbx[1] + hbx[3] - hbx[0] - hbx[2]) / 2, 2), round((hbz[2] + hbz[3] - hbz[0] - hbz[1]) / 2, 2)]}
sw_w = 1.65  # the four short walls (C), the gates between them: the middle 2.9 m, the sides 2.15 m
gate_w = [(LF_W - 4 * sw_w) * f for f in (0.3, 0.4, 0.3)]
x = LF_X - LF_W / 2
parts_lf = []
for k in range(4):
    parts_lf.append(("wall", x + sw_w / 2, sw_w))
    x += sw_w
    if k < 3:
        parts_lf.append(("gate", x + gate_w[k] / 2, gate_w[k]))
        x += gate_w[k]
gi = 0
for kind, cx, w in parts_lf:
    if kind == "wall":
        short_wall(cx, LF_Z, 0.0, w, LF_D - 0.3, 3.3, "lf_wall")
    else:
        mid_gate = gi == 1
        out, _ = glazed_gate(cx, LF_Z, 0.0, w + 0.5, LF_D, 3.3 if mid_gate else 2.9, 4.6 if mid_gate else 4.0, 7.4 if mid_gate else 6.5, f"liulifang_{gi}", doors=False, arched=False,
                             plaque_w=1.5 if mid_gate else 0.0)
        S.kp(f"liulifang_{gi}_ridge", out["ridge"])
        gi += 1
S.FOOTPRINTS.append([(LF_X - LF_W / 2 - 0.3, LF_Z - LF_D / 2 - 0.3), (LF_X + LF_W / 2 + 0.3, LF_Z - LF_D / 2 - 0.3), (LF_X + LF_W / 2 + 0.3, LF_Z + LF_D / 2 + 0.3),
                     (LF_X - LF_W / 2 - 0.3, LF_Z + LF_D / 2 + 0.3)])
for k, (hx, hz) in enumerate(READ["huabiao"]):
    huabiao(hx, hz, f"huabiao_{['NW', 'NE', 'SW', 'SE'][k]}", board_rot=0.0)
pave([(LF_X - 2.0, LF_Z - LF_D / 2 - 6.0), (LF_X + 2.0, LF_Z - LF_D / 2 - 6.0), (LF_X + 2.0, LF_Z + LF_D / 2 + 6.0), (LF_X - 2.0, LF_Z + LF_D / 2 + 6.0)], "way_liulifang", dy=0.08,
     step=4.0, mat="marble", clear=True)

# ============================================================ the courts where no generated hill may stand (joints.json `level`, scripts/hills1860.py): the walled compound, the
# forecourt inside the outer moat, 致孚殿's yard, the square of the four 华表 (Malone: the archway stands in a hollow between hills, E1561)
S.LEVEL.append([(ow_x0 - 3, ow_z0 - 3), (ow_x1 + 3, ow_z0 - 3), (ow_x1 + 3, ow_z1 + 3), (ow_x0 - 3, ow_z1 + 3)])
S.LEVEL.append([(ow_x0 - 3, ow_z1), (ow_x1 + 3, ow_z1), (ow_x1 + 3, zb_n + 0.5), (ow_x0 - 3, zb_n + 0.5)])
S.LEVEL.append([(zx0 - 2, zz0 - 2), (zx1 + 2, zz0 - 2), (zx1 + 2, zz1 + 2), (zx0 - 2, zz1 + 2)])
S.LEVEL.append([(min(hbx) - 5, min(hbz) - 5), (max(hbx) + 5, min(hbz) - 5), (max(hbx) + 5, max(hbz) + 5), (min(hbx) - 5, max(hbz) + 5)])

# ============================================================ the report and the files
REPORT["triangles"] = m.count()
REPORT["walls"] = {"inner_m": [round(iw_x1 - iw_x0, 2), round(iw_z1 - iw_z0, 2)], "outer_m": [round(ow_x1 - ow_x0, 2), round(ow_z1 - ow_z0, 2)], "inner_h": IW_H, "outer_h": OW_H}
n_bytes = m.write_glb(HERE / "model.glb", "YM17 鸿慈永祜 Hongci Yonghu", extras={"frame": "x east along the front, y up, z south along the axis; origin at 安佑宫's box front middle"})
aliases = ["YM17-01", "YM17-02", "YM17-03", "YM17-04", "YM17-05", "YM17-06", "YM17-07", "YM17-08", "YM17-09", "YM17-10", "YM17-11", "YM17-12", "YM17-13",
           "YM17-AW012", "YM17-AW013", "YM17-B0156", "YM17-B0158", "YM17-N01"]
depth_total = hbz[2] + 1.2 - (ow_z0 - 1.0)
summary = {
    "id": "YM17",
    "aliases": aliases,
    "name": "鸿慈永祜 Hongci Yonghu",
    "glb": "model.glb",
    "position": S.pos,
    "rotationY": S.rot,
    "line": "The ancestral temple 安佑宫 as S01 draws its layout and S05 names its halls (1742-43, after 寿皇殿): the hall of nine bays on S01's grid of ten by four columns (Malone counted forty pillars), double-eaved 歇山 in yellow tile after the leaf of 1744, on its marble terrace with five flights; the gate 安佑门, the two walls, the two moats with five bridges each, the three timber archways, the glazed archway and the four 华表 as S01, S05, Malone and the leaf give them. Every height, the smaller buildings' forms and all ornament are C.",
    "rows": [
        ["Layout", "As S01 draws it (re-read in Round 27 in plan pixels, B): from the four 华表 round the glazed archway in the south, past 致孚殿, over the outer moat to the forecourt, the outer wall, the court between the walls with the inner moat, 安佑门 in the inner wall and the inner court with the hall at its back; one axis through them"],
        ["安佑宫", "Nine bays (S05 重檐正殿九楹, A) on S01's ten column lines and four rows, about 30 x 14 m between the end columns (B; Malone counted ten pillars across the front and forty in all, B); a porch at the front, red lattice doors in every bay, red columns, green-blue beams under both eaves (the leaf, A); double-eaved 歇山 in yellow glazed tile (the leaf, A; S360, Malone, B); the plaque 安佑宫 in Qianlong's hand (S05, A); the column 4.6 m from the leaf's proportion, the roofs' rise C"],
        ["Terrace", "One marble terrace under the hall and before it, T-shaped as S01 draws it, with five flights, three at the front and one on each side of the 月台 (S01; Malone's five stairs, B); the middle flight with the dragon-and-cloud ramp stone, 1.30 m wide (S943: one of its stones is at Peking University, B); white balustrades (the leaf, A); its height 1.6 m C; two censers, two cranes and two deer before the hall (S361, Malone, B; their forms and places C)"],
        ["Inner court", "The side halls 配殿 of five bays, yellow 歇山 (S05, A; the leaf; S01), the two octagonal stele pavilions with double eaves (S05, Malone, the leaf; S01's octagons), the two green-glazed burners (S05, Malone, B; form C); a way on the axis (C); the court's trees are the planting's (the leaf's rows of small conifers)"],
        ["安佑门", "Five bays (S05, A), single-eave 歇山 in yellow tile (the leaf, A), its doors in the middle row on the inner wall's line (S01, B), on a marble terrace with a balustrade and three flights (Malone, the leaf, B; its size C); the plaque 安佑门 (S05, A)"],
        ["Walls", "Two red walls with yellow glazed coping (Malone, B; the leaf paints them vermilion), 72 x 61 m and 96 x 100 m as S01 draws them (B); a small gate either side of 安佑门 (S01; the leaf); the outer wall's five gates: three glazed arched gates in the middle and a smaller gate each side (Malone, S01, the leaf; B), a gate of three bays on the north side (S01); heights C"],
        ["Between the walls", "The inner moat, a moon river with three marble bridges before the gate and one at each side (S05, A; Malone, B; S01's channel and breaks: water of Round 27), its lining and railings C; the waiting rooms 朝房 of five bays (S05, A; form C); two well pavilions (S05, Malone; form C); in the north corners two walled yards with long ranges (S01; unnamed, C)"],
        ["Forecourt", "The two stone qilin on their bases before the three middle gates (Malone; S943: 1.74 m on bases 0.98 m high, 1.41 x 1.95 m; S01's squares; B; the beast's form C); the three timber archways 三坊 with red posts held by diagonal props and small yellow roofs (S05, A, with their six faces named; the leaf, A; S01's bars), their heights C; paved (the leaf)"],
        ["Outer moat", "The U-shaped moat 月河 round the forecourt (S05, A; S01's band: water of Round 27) with five marble bridges, the middle one for the emperor (Malone, B); three arched bridges with white balustrades and red railings along the banks as the leaf paints them (A); the two end bridges and the lining C"],
        ["致孚殿", "Three bays facing west in a red-walled yard, yellow tile (S05, A; the leaf, A; S01's yard and cells, B); inside, the carved text of Yongzheng's 圆明园记 (S05 j81:21b; not drawn); heights C"],
        ["Glazed archway and 华表", "鸿慈永祜坊 (S05, A): three gates with glazed frames and yellow roofs between four short red walls with round glazed panels (Malone, B; the leaf, A), 13.7 m as S01 draws it (B), its heights C; the four marble 华表 at the corners of a square of 30 m (Malone, S01: B), 8 m high on octagonal bases 1.24 m high (S980, B), the dragon, cloud board, dew plate and beast after the photograph of about 1882 (P0196) and the pair at Peking University (C for their sizes)"],
        ["What survives", "The 华表: two at Peking University, two before the old National Library (moved 1925; S980); the qilin pair at Peking University (S943); one ramp stone at Peking University, its pair at the east gate of 颐和园 (S943). The masonry was pulled down under the Republic (S02 p.218); no dig of the platform has been published"],
        ["Assumed", "Every height (the terrace 1.6 m, the hall's column 4.6 m and its roofs, the gates', walls', archways' and pavilions' heights), the porches, the brackets, the corner ranges, the waiting rooms', wells' and burners' forms, the bronzes, the qilin's and 华表's carving, the bridges' form, the linings and railings: the classes, the Qing manual and the leaf (C, the pale tint with conf=1)"],
    ],
    "caption": {"frontage_m": round(ow_x1 - ow_x0, 1), "depth_m": round(depth_total, 1), "eave_m": REPORT["halls"]["hall"]["above_court_m"]["eave"],
                "ridge_m": REPORT["halls"]["hall"]["above_court_m"]["ridge"], "assumed": True, "confidence": "C"},
    "hides": [],
    "bridges": ["BR014", "BR015"],
    "tris": m.count(),
    "glb_bytes": n_bytes,
}
S.write(HERE, "YM17", aliases, P, "origin at the front middle of 安佑宫's box F0096 at its ground; z south along S01's axis, x east, y up (scripts/model_site.py)", summary)
json.dump(REPORT, open(HERE / "report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"YM17: {m.count()} triangles, GLB {n_bytes / 1e6:.2f} MB; axis {AXIS:.2f} (spread {REPORT['axis_spread_m']} m); hall {REPORT['hall_s01']['between_end_columns_m']} x "
      f"{REPORT['hall_s01']['between_rows_m']} m; moats {WID_IN} {WY_IN:.2f}, {WID_OUT} {WY_OUT:.2f}")
