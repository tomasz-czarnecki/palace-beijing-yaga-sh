#!/usr/bin/env python3
"""正大光明 Zhengda Guangming (YM01), the audience hall of the garden with its gates and courts: the ninth detailed model (Round 19).

  uv run python models/YM01-zhengda-guangming/zhengdaguangming.py

The formal entrance of the garden, from the terrace before 大宫门 Da Gongmen to the rock hill 寿山 behind the hall, in its state of the 1850s: the great gate on the
palace wall with its terrace and bronze lions, the 左门 either side, the court offices 外朝房 before it; the inner court with the court offices 内朝房 and its two long
ranges; the moon-shaped canal lined with marble and its flat bridge (levelled in 1839, S211); the second gate 出入贤良门 with the duty rooms either side, the side gates
and the wall of the gate line; the flagged court with the five-bay side halls; 正大光明殿 on its platform with the terrace 月台 and its four censers (added 1775-1793,
S119), the covered way to the east, the rock peaks behind. The same generator writes two small models of their own: 勤政殿 of 勤政亲贤 (YM02-01) east of the court, and the
spirit wall 大影壁 (YM41-12) 204.8 m south of the gate's terrace, beyond the plan.

Method (docs/METHOD.md, 'a compound from the kit and its evidence', Rounds 17-18): every hall is the hall kit (scripts/hall_parts.py) from its numbers, adapted to its
evidence; the layout read on S01 (plan_readings.csv, plan pixels, placed by the fit in use, research/georef/).
Writes, beside this file: model.glb, params.json, keypoints.json, joints.json, summary.json, report.json (models/README.md); and the two small models' folders.
Frame (scripts/model_site.py): origin at the front middle of 正大光明殿's box F0004, at that box's ground; x east along the front, y up, z south.
Grades: what a source states for this object (the slip's bays, Malone's platform, the dig's gate base, the leaf's colours and forms, the 1860 witnesses) is `doc`; forms
carried in from the hall classes (the side halls, the court offices, the duty rooms, the side gates, the censers, the lions' form, the brackets) are `fill` (assumed, C).
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
from model_site import Site, box_frame  # noqa: E402
from scene1860 import DATUM_M, to_xz  # noqa: E402
from shapely.geometry import LineString, Point, Polygon  # noqa: E402

CHI = 0.32  # 1 营造尺 in metres (research/scenes/README.md)
FT = 0.3048
P = {
    "zg_bays": ("7 bays: 5.168 + 2 x 4.832 + 4 x 4.32 m, porches 1.92 m all round", "S310", "A", "NLC 样001-4 正大光明白差准底 as transcribed on mhymy record 10451: 明间一丈六尺一寸五, 二次间一丈五尺一寸, 四梢间一丈三尺五寸, 廊宽六尺; 32.11 m between the end columns of the seven bays, 35.95 m with the side porches"),
    "zg_depth": ("12.16 m between the 金柱 lines + 2 x 1.92 m porches = 16.0 m", "S310", "A", "金柱中进深三丈八尺 (same slip); 进深五间 (S06, B): the 12.16 m split into three equal spans (C)"),
    "zg_porches": ("open porches front and sides; the rear porch walled in", "S310", "A", "record 10451: 大殿结构本为周围廊式，但后廊被封入室内，仅三面有外廊，两山的廊子内无门窗装修 (the slip, as the 1744 leaf shows)"),
    "zg_fittings": ("door screens in the five middle bays front and back; the end bays windows over a sill wall in front, walled at the back", "S310;S251", "B", "record 10451: 外檐装修全部为隔扇门，前后檐共十樘，后檐两端的两间未安木装修，均砌墙 (A); Barrow 1793: brick to about 4 ft between the inner columns, oiled-paper lattice above, opening entirely on public occasions (E1026, B): the front end bays drawn as windows on a sill wall (C)"),
    "zg_platform": ("39.3 x 19.2 m, 1.22 m high", "S02;S251", "B", "Malone measured the foundation on site: 129 x 63 ft, 4 ft high (S02 p.75, E1009); Barrow: a granite platform about 4 ft high (S251 p.124, E1026)"),
    "zg_col": (5.12, "S02;S251", "C", "16 尺 (research/typology/params.json by_name, kept for this hall in Q182); Barrow's room was 20 ft (6.10 m) to the painted ceiling (E1026), above the eave columns as in a hall with porches"),
    "zg_columns": ("ten columns across the front, red; bases 0.84 m", "S02", "B", "Malone: the façade presented a colonnade of ten columns; round column bases 2 ft 9 in across (S02 pp.75-76, E1009); red by the end of Qianlong's reign (S02 p.76)"),
    "zg_roof": ("single-eave rolled 歇山, grey tile", "S08;S337", "B", "the 1744 leaf: 歇山, single eaves, the ridge reads as rolled, grey (S08 P0001, A for 1744); S337: 单檐卷棚歇山, ten purlins, grey tile (E1013, B); the 举架 of the grand_hall class (C)"),
    "zg_band": ("bracket band, painted blue, green, red and gilt", "S251;S240", "B", "Barrow: a painted frieze in blue, red, green and gilt under a wire net against birds (E1026); Wolseley 1860: the same net under the eaves (E1033); the brackets and their count C"),
    "zg_flights": ("three flights from the terrace to the platform: the middle one 5.17 m wide, one before each end bay", "S02;S08", "C", "Malone: ascended by three sets of stone steps (S02 p.75, B); the 1744 leaf paints a wide middle flight and a narrower one beside it (S08 P0001, A for 1744); where the third stands and the widths C"),
    "zg_plaque": ("正大光明, Yongzheng's hand, on the front eave", "S05", "A", "S05 j80:10b 世宗御題四字額者凡十有四正大光明殿其一也; the board's size and colours C"),
    "yuetai": ("38.40 x 14.82 m, 0.26 m high, four censers", "S119", "B", "月台 12丈 x 4.63丈 x 0.8尺 with four censers, added between 1775 and 1793 (S119, as in research/typology/params.json; a secondary source); S01 draws it as wide as the hall (B); a balustrade round it C (the brief; no source shows one); the censers' form C"),
    "court": ("flagged, from the terrace to the gate line, between the side halls", "S240;S242;S01", "B", "Wolseley 1860: a long flagged court with the hall at its far side (E1033); M'Ghee 1860: a second court about the same size (E2104); its extent as S01 draws it; a raised axis way C"),
    "side_halls": ("five bays each, facing the court", "S05;S01", "B", "S05 j80:9b 東西配殿各五楹 (A); S01's 西穿堂 and 东穿堂 at the court's sides (B); their forms the class's (C)"),
    "gallery_E": ("a covered way from the hall's east end to the east range", "S08;S02;S01", "B", "the 1744 leaf: a long low gallery running east from the hall (S08 P0001); Malone: a covered passage to the east (S02 p.76, E1009); S01's line at y 5413; its form C"),
    "shoushan": ("rock peaks behind the hall, 3-8 m above the hill", "S05;S08", "C", "S05 j80:11a 屋後峭石壁立玉筍嶙峋 (A); the 1744 leaf's tall slender blue-grey peaks among pines (S08 P0001); their number, places and heights C (the leaf's are 2-3 eave heights, painted tall: Q198); on S01's rock ridges (H0055)"),
    "gate": ("出入贤良门: five bays, rolled 歇山, red plank doors in the middle three bays", "S05;S08;S337;S01", "B", "S05 j80:9a 出入賢良門五楹 (A); S01's row of cells, about 21 m (B); S337: 卷棚歇山 (E1013, B); the 1744 leaf: a raised gate hall with red doors in its middle bays (S08 P0001); widths, column and platform the gate_hall class (C)"),
    "gate_plaque": ("出入贤良, Yongzheng's hand", "S05", "A", "S05 j80:9b 出入賢良門額世宗御書; the board C"),
    "zhifang": ("duty rooms either side of the gate, lower, gabled, white walls", "S05;S08;S01", "B", "S05 j80:9a 門左右為直房 (A); the 1744 leaf: lower wings of about five bays, gabled, white walls and green lattice either side of the gate (S08 P0001); at S01's boxes B1151 and B1154; their form C"),
    "gate_line_wall": ("rubble-stone wall about 4 m high on the gate line", "S245;S08", "B", "Varin 1860: the third enclosure had a wall about 4 m high and two small side doors (S245 pp.227-228, E2106, B); the 1744 leaf paints the wall on this line in rubble stone 虎皮石 (S08 P0001); its coping C"),
    "zhaomen": ("two side gates 罩门 in the gate line", "S05;S245;S01", "B", "S05 j80:9b 東西設兩罩門 (A); Varin: two small side doors (B); placed in S01's two gaps beside the gate (B); their form C"),
    "moat": ("the moon-shaped canal, about 3 m wide, lined with white marble, red railings on its banks", "S05;S245;S08;S01", "B", "S05 j80:9b 門前河形如月 (A); S01's two lines about 3 m apart (B, research/plan/water_manual.json); Varin 1860: a canal lined with white marble (S245 pp.227-228, B); the 1744 leaf: red railings along the canal's banks (S08 P0001); the water's level Round 10's (C)"),
    "bridge": ("one flat marble bridge on the axis, 4.6 m wide, its north end flared, wooden railings", "S01;S211;S245;S08", "B", "S01 draws one bridge on the axis with a flared north end (B); S211: the bow-backed bridge before 出入贤良门 levelled flat in 己亥 1839 (E2443, A); Varin 1860: the bridge of marble with two wooden side galleries (S245 p.228, B): read as wooden railings (C); S05 gives three bridges (Q130): not drawn"),
    "dragons": ("two gilt bronze dragons on the bridge", "S245", "B", "Varin: two gilt bronze dragons on the marble bridge, carried off later (S245 p.233 n.1, E2122); their places and form C"),
    "crossing": ("a slab crossing east of the axis", "S01", "C", "S01 breaks the canal's lines for about 3 m east of the axis (x 3365-3379): read as a crossing; a plain stone slab (C)"),
    "inner_court": ("flagged, the court offices 内朝房 either side, a long range on each side", "S242;S05;S01", "B", "M'Ghee 1860: inside the first gate a large flagged courtyard, some hundred yards wide by eighty deep, with guard rooms at each side (E2104, B; his estimate: S01 gives about 85 x 40 m); S05 j80:9a 度橋東西朝房各五楹 (A); S01's west range (B1178) and its unboxed east twin (B); the halls' forms C"),
    "dgm": ("大宫门: five bays on a base 21.57 x 11.33 x 0.77 m, rolled 歇山, red plank doors with gilt studs", "S102;S05;S240;S337", "B", "the 正大光明 survey report: the gate hall's base 21.57 x 11.33 m, 0.77 m high (S102, E1017, B); S05 j80:8b 大宫門五楹 (A); Wolseley 1860: red doors picked out in gold, the sills 2-3 ft above the pavement (E2109, B); S337: 卷棚歇山 (B); the column 4.16 m and the brackets C"),
    "dgm_plaque": ("圆明园, Yongzheng's hand", "S05", "A", "S05 j80:1b 懸大宫門者世宗御書 (the Kangxi plaque hangs on 圆明园殿); the board C"),
    "dgm_terrace": ("the gate's terrace 月台, 21.6 x 10 m, 0.40 m", "S01;S42", "B", "S01 draws a rectangle as wide as the gate before it (B); S42 and S102 measure the spirit wall from the 宫门月台's south edge (E1017); its height C"),
    "lions": ("a pair of bronze lions on stone pedestals on the terrace", "S42;S240;S245;S01", "B", "bronze lions from 1763 (S42); Wolseley: colossal, bronze-coloured, on granite pedestals (S240 p.230, E2123); Varin: bronze on white marble pedestals 3 m high (S245 p.233, E2122); S01's two squares on the terrace (B); their form C (Wolseley's 'colossal' read as about 3.6 m with the pedestal)"),
    "zuomen": ("左门: a small gate in the wall either side of 大宫门", "S42;S01", "B", "S42 两侧设左右门; S01's two small boxes in the wall (both read 左门); their form C"),
    "palace_wall": ("the palace wall of the gate line: red, grey coping, 4.2 m", "S42;S01", "C", "大宫门 stands astride the palace wall (S42 东西骑建宫墙, B); S01's double line west and east of the gate and round the inner court (Round 19's W01); red and the height C (the 宫墙 of the palaces)"),
    "waichaofang": ("外朝房: five bays each, either side of the road before the gate", "S05;S01", "B", "S05 j80:8b 門前左右朝房各五楹 (A); at S01's boxes F0254, F0255 (B); their form the class's (C)"),
    "road": ("the stone road 石甬路 on the axis, 4.8 m wide", "S05;S42;S01", "B", "S05 j80:7b 大宫門前輦道; S42 宫门前石甬路; S01's two lines 4.8 m apart (B)"),
    "colours": ("red columns and doors, green-blue lattice and beams, grey tile, white and rubble walls", "S08;S02", "B", "the 1744 leaf (S08 P0001, A for 1744): red columns and doors, green-blue lattice, grey tile, white walls with grey coping round the office courts, red railings; Malone: red columns by the end of Qianlong's reign (S02 p.76)"),
}
V = {k: v[0] for k, v in P.items()}

COL = {
    "lacquer": "#8a2f22", "lacquer_dark": "#532218", "wall": "#8e8a84", "plaster": "#e4ddcf", "glass_lattice": "#2b3137", "sill": "#7d7973",
    "band": "#2e6a6c", "bracket": "#3b7b70", "bandred": "#7d2c20", "platform": "#b7b0a1", "coping": "#d2ccbe", "step": "#c8c1b1", "marble": "#e9e5dc",
    "underside": "#4b453d", "fascia": "#3a2a22", "wallred": "#9b3d2c", "wallwhite": "#e8e2d6", "rock": "#8f948f", "rubble": "#a39a86", "pave": "#bdb6a6", "gold": "#c9a245",
    "plaque": "#20406a", "bronze": "#4f5c4e", "lion": "#5a5640", "timber": "#7a5a3c", "rail": "#8c3a26", "quay": "#d9d4c8", "granite": "#9c978d",
    "trunk": "#5a4634", "leaf_peach": "#6f8a45", "blossom": "#d8a7b1",
    "tile_grey": "#5f6469", "ridge_grey": "#4a4e52",
}

S = Site("F0004")
m = Mesh(COL)
S.m = m
KIT = json.load(open(ROOT / "site/reconstruction/data/kit_1860.json", encoding="utf-8"))["halls"]
FEATS = S.F
GROUND = json.load(open(ROOT / "site/reconstruction/generated/ground.json", encoding="utf-8"))
WATER = json.load(open(ROOT / "research/layers/water_1860.geojson", encoding="utf-8"))["features"]
REPORT = {"halls": {}}


def plan_local(px, py, site=None):
    lon, lat = plan_to_wgs84(np.array([px], float), np.array([py], float))
    x, z = to_xz(float(lon[0]), float(lat[0]))
    return (site or S).to_local(x, z)


ROWS = list(csv.DictReader(open(HERE / "plan_readings.csv", encoding="utf-8")))
PX = {r["name"]: [tuple(map(float, p.split())) for p in r["plan_px"].split(";")] for r in ROWS}


def _scene_mid(names):
    pts = [to_xz(*[float(v[0]) for v in plan_to_wgs84(np.array([p[0]], float), np.array([p[1]], float))]) for n in names for p in PX[n]]
    return np.mean([p[0] for p in pts]), np.mean([p[1] for p in pts])


# the frame's z along the axis as S01 draws it (Round 19 v2): from the middle of the hall, terrace, gate and bridge to the middle of 大宫门, its terrace, the lions and the
# road; F0004's own bearing (174.8) runs 2 degrees off it and put 大宫门 3 m west of the hall's axis
_n, _s = _scene_mid(("hall_strip", "yuetai", "gate", "bridge")), _scene_mid(("dgm", "dgm_yuetai", "lion_W", "lion_E", "road_S"))
ROT_BOX = S.rot
S.rot = round(math.atan2(_s[0] - _n[0], _s[1] - _n[1]), 6)
READ = {k: [plan_local(*p) for p in v] for k, v in PX.items()}


def rect(name):
    pts = READ[name]
    xs, zs = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), max(xs), min(zs), max(zs)


def mid(name):
    x0, x1, z0, z1 = rect(name)
    return (x0 + x1) / 2, (z0 + z1) / 2


# the axis: one straight line (the frame's z) through the middles S01 draws on it
_ax = [mid(n)[0] for n in ("hall_strip", "yuetai", "gate", "bridge", "dgm", "dgm_yuetai")] + [(READ["lion_W"][0][0] + READ["lion_E"][0][0]) / 2, mid("road_S")[0]]
AXIS = float(np.mean(_ax))
REPORT.update({"rot_box": ROT_BOX, "rot_axis": S.rot, "axis_x": round(AXIS, 2), "axis_spread_m": round(float(max(_ax) - min(_ax)), 2), "axis_reads": [round(float(v), 2) for v in _ax]})

# raised floors the model draws (its terraces): the flights and the paving read them as their ground
RAISED = []


def ground(x, z):
    g = S.gy(x, z)
    for x0, x1, z0, z1, top in RAISED:
        if x0 - 1e-6 <= x <= x1 + 1e-6 and z0 - 1e-6 <= z <= z1 + 1e-6:
            g = max(g, top)
    return g


K = HallKit(m, ground)


def compass(dx, dz):
    return ("N" if dz < 0 else "S") + ("W" if dx < 0 else "E")


def box_local(fid, site=None):
    s_ = site or S
    c, u, hf, hd, base = box_frame(FEATS, fid)
    x, z = s_.to_local(*c)
    x2, z2 = s_.to_local(*(c + u))
    return x, z, math.atan2(x2 - x, z2 - z), hf, hd


def kp_platform(name, hf, hd, y_top, anchor=True):
    c0 = m.world((0, 0, 0))
    for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        w = m.world((sx * hf, 0, sq * hd))
        tag = compass(w[0] - c0[0], w[2] - c0[2])
        S.kp(f"{name}_pl_foot_{tag}", (w[0], ground(float(w[0]), float(w[2])), w[2]), anchor=anchor)
        S.kp(f"{name}_pl_top_{tag}", (w[0], y_top, w[2]))


def kp_roof(name, H):
    """The eave's corner tips and the ridge's ends, named by compass, as hall_parts.roof draws them (Round 18)."""
    CS, CQ, o = H["hf"] - H["e"], H["hd"] - H["e"], H["o"]
    tip = H["base"] + H["eave"] - o * 0.5
    c0 = m.world((0, 0, 0))
    for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        w = m.world((sx * (CS + o), 0, sq * (CQ + o)))
        S.kp(f"{name}_eave_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], tip, w[2]))
    hz = CQ + o
    band = min(0.12 * hz, 0.6) if H["rl"] else 0.0
    rh = {"wd": max(CS + o - 0.85 * (hz - band), 0.5), "xs": CS + o - 0.4 * (hz - band)}.get(H["rf"], CS + o)
    for sx in (-1, 1):
        w = m.world((sx * rh, 0, 0))
        S.kp(f"{name}_ridge_{'W' if w[0] < c0[0] else 'E'}", (w[0], H["base"] + H["ridge"], w[2]))


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
        for sx in (-1, 1):  # the feet of the front corner columns, on the platform (what a painting shows of a colonnade)
            w = m.world((sx * (H["hf"] - H["e"]), 0, H["hd"] - H["e"]))
            S.kp(f"{name}_col_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], H["base"] + H["pl"], w[2]))
    m.pop()
    if site_lists:
        for i, c in enumerate(corners):
            g = ground(float(c[0]), float(c[2]))
            if g <= S.gy(float(c[0]), float(c[2])) + 1e-6:  # a corner on a terrace the model draws is no joint with the ground
                S.JOINTS.append([f"{name}_pl_{i}", float(c[0]), H["foot"], float(c[2]), "platform foot"])
        S.FOOTPRINTS.append([(float(c[0]), float(c[2])) for c in corners])
        for k, f in fw.items():
            S.entry(f"{name}_{k}", float(f[0]), float(f[2]), float(f[1]))
    REPORT["halls"][name] = {"frontage_m": round(2 * H["hf"], 2), "depth_m": round(2 * H["hd"], 2), "platform_m": H["pl"], "eave_m": H["eave"], "ridge_m": H["ridge"], "roof": H["rf"],
                             "rolled": int(bool(H["rl"])), "bays": len(H["b"]), "flights": len(feet), "grade_class": H["cls"], "x": round(H["x"], 2), "z": round(H["z"], 2)}
    return fw


def hall_spec(x, z, rot, bays, depths, edge, pl, col, roof, rolled, cls, bracket=False, ju="main_hall", pf=0.0, pb=0.0, ps=0.0, over=None):
    """A hall from its spans (eave column to eave column) and its section: platform = columns + edge; eave from the column and the band; ridge by the 举架 over the half-span."""
    span, dep = sum(bays), sum(depths)
    hf, hd = span / 2 + edge, dep / 2 + edge
    gx = [x + s * math.cos(rot) * hf + q * math.sin(rot) * hd for s in (-1, 1) for q in (-1, 1)]
    gz = [z - s * math.sin(rot) * hf + q * math.cos(rot) * hd for s in (-1, 1) for q in (-1, 1)]
    gs = [S.gy(a, b) for a, b in zip(gx, gz)]
    fx, fz = x + math.sin(rot) * hd, z + math.cos(rot) * hd
    base = S.gy(fx, fz)
    band = 0.85 if bracket else 0.42
    eave = round(pl + col + band, 2)
    o = 1.25 if col >= 4.0 else 1.1
    rise = round(0.62 * (dep / 2 + o), 2)
    H = dict(hf=hf, hd=hd, base=base, foot=min(gs) - 0.15, pl=pl, eave=eave, ridge=round(eave + rise, 2), e=edge, o=o, b=list(bays), d=list(depths), pf=pf, pb=pb, ps=ps,
             dia=0.36 if col < 4.0 else 0.42, st={"front": [0.0], "back": [0.0]}, bal=0, rf=roof, rl=1 if rolled else 0, db=0, ju=JU[ju], t="grey", te=None,
             bd="br" if bracket else "bm", dr=list(range(len(bays))), rr="d", k="hall", x=x, z=z, rot=rot, cls=cls, src="dossier")
    if over:
        H.update(over)
    return H


def kit_spec(fid, cls="fill", site=None, **over):
    """A hall from its kit entry at its box (Round 11's class form), for the halls of the compound with no figure of their own."""
    p = FEATS[fid]["properties"]
    e = KIT[fid]
    x, z, rot, hf, hd = box_local(fid, site)
    st = {side: [0.0] for side in e.get("st", ["front"])}
    gx = [x + s * math.cos(rot) * hf + q * math.sin(rot) * hd for s in (-1, 1) for q in (-1, 1)]
    gz = [z - s * math.sin(rot) * hf + q * math.cos(rot) * hd for s in (-1, 1) for q in (-1, 1)]
    s_ = site or S
    base = s_.gy(x + math.sin(rot) * hd, z + math.cos(rot) * hd)
    H = dict(hf=hf, hd=hd, base=base, foot=min(s_.gy(a, b) for a, b in zip(gx, gz)) - 0.15, pl=p["platform_m"], eave=p["eave_m"], ridge=p["ridge_m"], e=e["e"], o=e["o"],
             b=e["b"], d=e["d"], pf=e["pf"], pb=e["pb"], ps=e["ps"], dia=e["dia"], st=st, bal=e.get("bal", 0), rf=e["rf"], rl=e["rl"], db=e["db"], ju=e["ju"], t=e["t"],
             te=e.get("te"), bd=e["bd"], dr=e["dr"], rr=e["rr"], k=e["k"], x=x, z=z, rot=rot, cls=cls, src="class")
    H.update(over)
    return H


def plaque(H, q_sign=1, w=2.6, h=1.0):
    """A plaque board 匾 on the eave band at the hall's middle bay (blue board, gold frame: C)."""
    m.push(H["x"], 0, H["z"], H["rot"])
    CQ = H["hd"] - H["e"]
    q = q_sign * (CQ + 0.3)
    y1 = H["base"] + H["eave"] - 0.05
    m.box(-w / 2 - 0.1, w / 2 + 0.1, y1 - h - 0.1, y1, q - 0.05, q + 0.05, "gold")
    zf = q + q_sign * 0.055
    m.poly([(-w / 2, y1 - h, zf), (w / 2, y1 - h, zf), (w / 2, y1 - 0.1, zf), (-w / 2, y1 - 0.1, zf)], "plaque")
    m.pop()


def wall_run(pts, h, name, gaps=(), thick=0.9, body="wallwhite", cap="grey", base_h=0.6, joints=True):
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


def wall_gate(x, z, rot, name, w=2.6, h=3.6, thick=0.9, body="wallwhite"):
    """A gate in a wall 随墙门 (C): two piers, a lintel band, red plank doors set in, a small rolled roof along the wall; entries both sides."""
    m.push(x, 0, z, rot)
    g = min(K.gy_local(a, b) for a in (-w / 2 - 0.5, w / 2 + 0.5) for b in (-thick, thick))
    y0 = g - 0.15
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
    K.roof(lambda a, b, c: (a, b, c), w / 2 + 1.0, thick / 2 + 0.75, g + h - 0.7, g + h + 0.55, form="xu", rolled=True, ju=JU["gallery"], gable_mat="plaster", gableX=w / 2 + 1.0)
    for sg, tag in ((1, "out"), (-1, "in")):
        p_ = m.world((0, 0, sg * 1.2))
        S.entry(f"{name}_{tag}", float(p_[0]), float(p_[2]))
    for sg in (-1, 1):
        p_ = m.world((sg * (w / 2 + 0.3), 0, 0))
        S.joint(f"{name}_pier{sg:+d}", float(p_[0]), float(p_[2]), "gate pier", y=y0)
    m.pop()


def pave(poly, name, dy=0.03, step=5.0, mat="pave", clear=True):
    """Paving over an outline, following the ground (or a terrace) in cells; the planting keeps off it (clear)."""
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
        S.CLEAR.append([tuple(map(float, p)) for p in (pg.exterior.coords[:-1] if pg.geom_type == "Polygon" else poly)])


def censer(x, z, y, name):
    """A bronze censer 香炉 on a stone stand (C): a three-legged round body with a lid and a finial."""
    m.box(x - 0.6, x + 0.6, y, y + 0.55, z - 0.6, z + 0.6, "marble")
    m.box(x - 0.7, x + 0.7, y + 0.5, y + 0.65, z - 0.7, z + 0.7, "marble")
    for a in (0.0, 2.094, 4.189):
        lx, lz = x + 0.3 * math.cos(a), z + 0.3 * math.sin(a)
        m.box(lx - 0.06, lx + 0.06, y + 0.65, y + 0.95, lz - 0.06, lz + 0.06, "bronze")
    m.lathe([(0.25, y + 0.9), (0.5, y + 1.05), (0.55, y + 1.4), (0.42, y + 1.6), (0.5, y + 1.65), (0.3, y + 1.95), (0.12, y + 2.2), (0.18, y + 2.35), (0.0, y + 2.6)], 10, "bronze", cx=x, cz=z)
    S.kp(f"{name}_top", (x, y + 2.6, z))


def lion(x, z, y, face, name):
    """A seated lion 石狮/铜狮 on a pedestal (C form): a 须弥座 pedestal 1.5 m, the lion about 2.1 m, facing out along the road. face: the frame's rot of its front."""
    m.push(x, 0, z, face)
    g0 = min(K.gy_local(a, b) for a in (-1.0, 1.0) for b in (-1.4, 1.4))
    y0 = min(y, g0) - 0.15
    m.cls = "doc"
    # the pedestal: a moulded base, a waist, a top slab (Wolseley: granite; Varin: white marble)
    m.box(-1.05, 1.05, y0, y + 0.35, -1.45, 1.45, "granite", skip=("bottom",))
    m.box(-0.9, 0.9, y + 0.35, y + 1.2, -1.3, 1.3, "granite")
    m.box(-1.0, 1.0, y + 1.2, y + 1.5, -1.4, 1.4, "granite")
    m.cls = "fill"
    b = y + 1.5
    m.box(-0.62, 0.62, b, b + 0.22, -0.95, 1.0, "lion")  # the plinth under the lion
    m.frustum([(-0.55, -0.85), (0.55, -0.85), (0.55, 0.55), (-0.55, 0.55)], [(-0.46, -0.45), (0.46, -0.45), (0.46, 0.5), (-0.46, 0.5)], b + 0.22, b + 0.95, "lion")  # the haunches, seated
    m.frustum([(-0.48, -0.2), (0.48, -0.2), (0.48, 0.62), (-0.48, 0.62)], [(-0.44, 0.05), (0.44, 0.05), (0.44, 0.6), (-0.44, 0.6)], b + 0.9, b + 1.5, "lion")  # the chest, upright
    for sx in (-1, 1):  # the forelegs, straight down to the plinth
        m.box(sx * 0.42 - 0.13, sx * 0.42 + 0.13, b + 0.22, b + 1.05, 0.5, 0.82, "lion")
    m.lathe([(0.0, b + 1.38), (0.6, b + 1.45), (0.66, b + 1.75), (0.6, b + 2.0), (0.42, b + 2.2), (0.0, b + 2.28)], 10, "lion", cx=0.0, cz=0.38)  # the maned head
    m.box(-0.3, 0.3, b + 1.55, b + 1.9, 0.85, 1.08, "lion")  # the muzzle
    m.lathe([(0.0, b + 0.22), (0.2, b + 0.26), (0.24, b + 0.44), (0.2, b + 0.62), (0.0, b + 0.66)], 8, "lion", cx=-0.42 if x < AXIS else 0.42, cz=0.98)  # the ball (male) or the cub under one paw: C
    m.cls = "doc"
    top = m.world((0, b + 2.28, 0.38))
    m.pop()
    S.kp(f"{name}_top", top)
    p_ = m.world((0, 0, 0))
    S.FOOTPRINTS.append([(float(c[0]), float(c[2])) for c in [m.world((sx * 1.05, 0, sq * 1.45)) for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1))]])
    return p_


def peak(x, z, h, r, seed, name=None):
    """A slender rock peak 笋石 (C form): a twisted tapering shaft of six sides from just below the ground."""
    rng = np.random.default_rng(seed)
    g = S.gy(x, z) - 0.3
    n = 4
    rings = []
    for k in range(n + 1):
        t = k / n
        rr = r * (1.0 - 0.55 * t) * rng.uniform(0.85, 1.1)
        ox, oz = rng.uniform(-0.15, 0.15) * r * t, rng.uniform(-0.15, 0.15) * r * t
        rings.append([(x + ox + rr * rng.uniform(0.75, 1.2) * math.cos(2 * math.pi * i / 6 + k * 0.4), z + oz + rr * rng.uniform(0.75, 1.2) * math.sin(2 * math.pi * i / 6 + k * 0.4)) for i in range(6)])
    for k in range(n):
        m.frustum(rings[k], rings[k + 1], g + (h + 0.3) * k / n, g + (h + 0.3) * (k + 1) / n, "rock")
    m.flat(rings[-1], g + h + 0.3, "rock")
    if name:
        S.kp(name, (x, g + h + 0.3, z))


def railing(pts, name, h=1.0, step=1.8, y_fn=None, mat="rail"):
    """A wooden railing along a polyline: posts every `step` m, a top rail and a middle rail (red: the 1744 leaf)."""
    y_fn = y_fn or ground
    L = LineString(pts)
    n = max(2, int(L.length / step) + 1)
    prev = None
    for k in range(n):
        q = L.interpolate(k / (n - 1), normalized=True)
        y = y_fn(q.x, q.y)
        m.box(q.x - 0.07, q.x + 0.07, y - 0.05, y + h, q.y - 0.07, q.y + 0.07, mat)
        if prev is not None:
            (px_, py_, pz_) = prev
            for hh, th in ((h - 0.08, 0.06), (h * 0.5, 0.04)):
                dx, dz = q.x - px_, q.y - pz_
                ll = math.hypot(dx, dz) or 1.0
                nx, nz = -dz / ll * 0.04, dx / ll * 0.04
                m.poly([(px_ + nx, py_ + hh - th, pz_ + nz), (q.x + nx, y + hh - th, q.y + nz), (q.x + nx, y + hh + th, q.y + nz), (px_ + nx, py_ + hh + th, pz_ + nz)], mat)
                m.poly([(px_ - nx, py_ + hh - th, pz_ - nz), (q.x - nx, y + hh - th, q.y - nz), (q.x - nx, y + hh + th, q.y - nz), (px_ - nx, py_ + hh + th, pz_ - nz)], mat)
        prev = (q.x, y, q.y)


# ============================================================ the moat (research/plan/water_manual.json, W0364) and its level
moat_f = next(f for f in WATER if f["properties"].get("region_id") == "RM001")
MOAT = Polygon([S.to_local(*to_xz(*c)) for c in moat_f["geometry"]["coordinates"][0]]).buffer(0)
moat_body = next(b for b in GROUND["bodies"] if moat_f["properties"]["id"] in b["ids"])
WATER_Y = moat_body["level"] - S.pos[1]
REPORT["moat"] = {"water_id": moat_f["properties"]["id"], "level_scene": round(moat_body["level"], 3), "water_y": round(WATER_Y, 3), "area_m2": round(MOAT.area, 1),
                  "length_m": round(MOAT.minimum_rotated_rectangle.length / 2, 1)}

# ============================================================ 正大光明殿 YM01-08 and its terrace
zb, zf_ = rect("hall_strip")[2], rect("yuetai")[3]  # S01's back of the hall and front of the terrace
ZC_GROUP = (zb + zf_) / 2
PL_D = 2 * (8.0 + 1.64)  # the platform's depth: 16.0 m between the eave columns + its edge both sides (Malone: 63 ft = 19.2 m)
YT_D, YT_W, YT_H = 46.3 * CHI, 120 * CHI, 0.8 * CHI  # 4.63丈, 12丈, 0.8尺 (S119)
GROUP_D = PL_D + YT_D
Z_BACK = ZC_GROUP - GROUP_D / 2  # centred on S01's group (S01 draws hall and terrace about 0.8 times the stated sizes: Q256)
ZH = Z_BACK + PL_D / 2
Z_YT0, Z_YT1 = Z_BACK + PL_D, Z_BACK + PL_D + YT_D
REPORT["s01_group_depth_m"] = round(zf_ - zb, 2)
REPORT["model_group_depth_m"] = round(GROUP_D, 2)
yt_ground = max(S.gy(AXIS + s * YT_W / 2, z) for s in (-1, 0, 1) for z in (Z_YT0, Z_YT1))
YT_TOP = yt_ground + YT_H
RAISED.append((AXIS - YT_W / 2, AXIS + YT_W / 2, Z_YT0 - 0.05, Z_YT1, YT_TOP))

zg_b = [1.92, 4.32, 4.32, 4.832, 5.168, 4.832, 4.32, 4.32, 1.92]  # porch, seven bays, porch: ten columns across the front (Malone)
zg_d = [1.92, 4.0533, 4.0533, 4.0534, 1.92]
Hz = hall_spec(AXIS, ZH, 0.0, zg_b, zg_d, 1.64, 1.22, V["zg_col"], "xs", True, "doc", bracket=True, ju="grand_hall", pf=1.92, pb=0.0, ps=1.92)
Hz["base"] = YT_TOP  # its front stands on the terrace
Hz["pl"] = round(1.22 - YT_H, 2)  # Malone's 4 ft above the court: 0.96 m above the terrace
Hz["eave"] = round(Hz["pl"] + V["zg_col"] + 0.85, 2)
Hz["ridge"] = round(Hz["eave"] + 0.62 * (8.0 + Hz["o"]), 2)
Hz["dr"] = [2, 3, 4, 5, 6]
Hz["rr"] = "d"
Hz["side_wall"] = True
Hz["dia"] = 0.52  # the bases 0.84 m (Malone) under columns of about 0.5 m (C)
Hz["st"] = {"front": [0.0]}
Hz["fw"] = {"front": 5.168}
Hz["per_bay"] = 2
Hz["foot"] = min(Hz["foot"], S.gmin([(AXIS - Hz["hf"], ZH - Hz["hd"]), (AXIS + Hz["hf"], ZH + Hz["hd"])]) - 0.15)
fw_zg = draw("zg", Hz)
plaque(Hz, 1, w=3.4, h=1.2)
S.kp("zg_plaque", m.world((AXIS, Hz["base"] + Hz["eave"] - 0.65, ZH + Hz["hd"] - Hz["e"] + 0.36)))
m.cls = "doc"
m.push(AXIS, 0, ZH)
CS, CQ = Hz["hf"] - Hz["e"], Hz["hd"] - Hz["e"]
plTop = Hz["base"] + Hz["pl"]
# the two other flights before the end bays (Malone's three sets; the leaf's second flight beside the middle one)
xs_ = [-CS]
for w_ in zg_b:
    xs_.append(xs_[-1] + w_)
for sg in (-1, 1):
    off = sg * (CS - 1.92 - 4.32 / 2 - 4.32)
    f = K.flight("front", off, Hz["hf"], Hz["hd"], plTop, 3.0)
    if f:
        fwp = m.world(f)
        S.entry(f"zg_front_{off:+.1f}", float(fwp[0]), float(fwp[2]), float(fwp[1]))
# the gable walls behind the open side porches, plastered red as the walls of the bays (C: the slip says only that the side porches have no fittings)
sw_ = CS - 1.92
top_ = plTop + V["zg_col"] - 0.05
for sg in (-1, 1):
    m.box(sg * sw_ - 0.04 if sg > 0 else -sw_ - 0.02, sg * sw_ + 0.02 if sg > 0 else -sw_ + 0.04, plTop, top_, -CQ, CQ - 1.92, "wallred")
# the rear end bays walled (record 10451: 后檐两端的两间未安木装修，均砌墙)
y0 = plTop
for i in (1, 7):
    m.box(xs_[i] + 0.2, xs_[i + 1] - 0.2, y0, y0 + V["zg_col"] - 0.05, -CQ - 0.05, -CQ + 0.4, "wallred")
m.pop()
REPORT["zg_rear_walls"] = "bays 1 and 7"

# the terrace 月台: S119's figures, centred on the axis before the platform; its own flight to the court, a balustrade round it (C), four censers (S119; form C)
m.cls = "doc"
m.push(AXIS, 0, (Z_YT0 + Z_YT1) / 2)
hw, hd_ = YT_W / 2, YT_D / 2
yt_foot = min(S.gy(AXIS + s * hw, (Z_YT0 + Z_YT1) / 2 + q * hd_) for s in (-1, 1) for q in (-1, 1)) - 0.15
K.platform(hw, hd_, YT_TOP, yt_foot, coping=False)
m.box(-hw - 0.03, hw + 0.03, YT_TOP - 0.12, YT_TOP + 0.01, -hd_ - 0.03, hd_ + 0.03, "marble", skip=("bottom",))
yt_flights = {}
for side, off, wdt in (("front", 0.0, 5.168), ("left", 0.0, 3.0), ("right", 0.0, 3.0)):
    f = K.flight(side, off, hw, hd_, YT_TOP, wdt)
    if f:
        yt_flights[side] = m.world(f)
m.cls = "fill"
K.balustrade(hw, hd_, YT_TOP, {"front": [(-3.1, 3.1)], "left": [(-2.0, 2.0)], "right": [(-2.0, 2.0)], "back": [(-hw, hw)]}, h=0.85)
for k, cx in enumerate((-11.5, -5.5, 5.5, 11.5)):
    censer(cx, 1.2, YT_TOP, f"censer_{k}")
m.cls = "doc"
kp_platform("yt", hw, hd_, YT_TOP)
corners = [m.world((sx * hw, 0, sq * hd_)) for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
m.pop()
for i, c in enumerate(corners[2:]):
    S.joint(f"yt_{i}", float(c[0]), float(c[2]), "terrace foot", y=yt_foot)
S.FOOTPRINTS.append([(float(c[0]), float(c[2])) for c in corners])
for side, f in yt_flights.items():
    S.entry(f"yt_{side}", float(f[0]), float(f[2]), float(f[1]))
S.deck("yuetai", YT_TOP, [(float(c[0]), float(c[2])) for c in corners])
REPORT["halls"]["yuetai"] = {"frontage_m": round(YT_W, 2), "depth_m": round(YT_D, 2), "platform_m": round(YT_H, 2)}

# ============================================================ the court: side halls, the east gallery, paving, the axis way
z_gateN = mid("gate_line")[1]  # the gate line's wall
XW_C = rect("side_W")[1]  # the west side hall's front (its east face)
XE_C = rect("court_E")[0]
for fid, nm in (("F0005", "side_W"), ("F0006", "side_E")):
    Hs = kit_spec(fid, "fill")
    Hs["st"] = {"front": [0.0]}
    Hs["rf"], Hs["rl"] = "xs", 1  # rolled 歇山 grey, as the leaf's halls round the court (C)
    draw(nm, Hs, kp=False)
# the covered way east from the hall's back corner to the east range (the leaf; S01's line at y 5413)
gx0, gz = AXIS + Hz["hf"], rect("gallery_E")[2] + 1.2
m.cls = "doc"
K.gallery([(gx0 + 0.2, gz), (XE_C - 0.6, gz)], 2.6, lambda a, b: ground(a, b) + 0.3, eave=3.1, ridge=4.3, wall_side=-1, wall_mat="wallwhite")
S.FOOTPRINTS.append([(gx0, gz - 1.4), (XE_C, gz - 1.4), (XE_C, gz + 1.4), (gx0, gz + 1.4)])
for k, x in enumerate((gx0 + 0.2, XE_C - 0.6)):
    S.joint(f"gal_E_{k}", x, gz, "gallery foot", y=S.gy(x, gz) - 0.15)
# the court's east wall (S01) from the gallery to the gate line; white with grey coping (the leaf), 3.6 m (C)
m.cls = "doc"
wall_run([(XE_C + 0.45, gz - 1.6), (XE_C + 0.45, z_gateN)], 3.6, "court_E")
# the flagged court (Wolseley, M'Ghee): from the terrace's line to the gate line, between the side halls; the raised axis way to the gate (C)
court = [(XW_C + 0.3, Z_BACK - 2.0), (XE_C, Z_BACK - 2.0), (XE_C, z_gateN - 0.5), (XW_C + 0.3, z_gateN - 0.5)]
pave(court, "court", dy=0.03)
m.cls = "fill"
# ============================================================ 出入贤良门 YM01-01, the duty rooms, the gate line's wall and the side gates
gx0_, gx1_, gz0_, gz1_ = rect("gate")
GATE_W = 5 * 4.16  # five bays (S05); the widths C: 20.8 m between the end columns, S01 draws about 21 m
Hg = hall_spec(AXIS, (gz0_ + gz1_) / 2 + 0.6, 0.0, [4.0, 4.16, 4.48, 4.16, 4.0], [3.0, 3.0], 0.89, 0.9, 3.84, "xs", True, "doc", bracket=True, ju="gate_hall")
Hg["k"] = "gate"
Hg["dr"] = [1, 2, 3]
Hg["fw"] = {"front": 4.48, "back": 4.48}
Hg["st"] = {"front": [0.0], "back": [0.0]}
fw_gate = draw("gate", Hg)
plaque(Hg, 1, w=2.6, h=0.95)
plaque(Hg, -1, w=2.6, h=0.95)
GATE = dict(Hg)
m.cls = "fill"
for fid, nm in (("F1358", "zhifang_W"), ("F1359", "zhifang_E")):
    Hr = kit_spec(fid, "fill")
    x0r, x1r, z0r, z1r = rect(nm)
    Hr["x"] = (x0r + x1r) / 2
    Hr["z"] = (z0r + z1r) / 2 + 0.3
    Hr["rot"] = 0.0
    Hr["hf"] = (x1r - x0r) / 2
    Hr["hd"] = max((z1r - z0r) / 2, 2.6)
    n = 5 if nm == "zhifang_E" else 4
    Hr["b"] = [(2 * (Hr["hf"] - Hr["e"])) / n] * n
    Hr["d"] = [2 * (Hr["hd"] - Hr["e"])]
    Hr["pf"], Hr["pb"], Hr["ps"] = 0.0, 0.0, 0.0
    Hr["rf"], Hr["rl"] = "ys", 1  # gabled, as the leaf's wings (C)
    Hr["dr"] = [n // 2]
    Hr["rr"] = "w"
    Hr["st"] = {"front": [0.0]}
    Hr["base"] = S.gy(Hr["x"], Hr["z"] + Hr["hd"])
    Hr["foot"] = S.gmin([(Hr["x"] - Hr["hf"], Hr["z"] - Hr["hd"]), (Hr["x"] + Hr["hf"], Hr["z"] + Hr["hd"])]) - 0.15
    draw(nm, Hr)
# the gate line's wall: rubble stone (the leaf), 4 m (Varin), from the court's west side to its east wall, broken at the gate, the duty rooms and the two side gates
m.cls = "doc"
zw = z_gateN + 0.45
zmW, zmE = mid("zhaomen_W"), mid("zhaomen_E")
gaps = [(AXIS, zw, Hg["hf"] + 0.1), (mid("zhifang_W")[0], zw, (rect("zhifang_W")[1] - rect("zhifang_W")[0]) / 2), (mid("zhifang_E")[0], zw, (rect("zhifang_E")[1] - rect("zhifang_E")[0]) / 2),
        (zmW[0], zw, 2.2), (zmE[0], zw, 2.2)]
wall_run([(rect("gate_line")[0], zw), (XE_C + 0.9, zw)], 4.0, "gateline", gaps=gaps, body="rubble", base_h=0.0)
m.cls = "fill"
for nm, (x, z) in (("zhaomen_W", zmW), ("zhaomen_E", zmE)):
    wall_gate(x, zw, 0.0, nm, w=2.4, h=3.8, body="rubble")
# the axis way 甬路 from the gate's back flight to the terrace's flight, raised 0.1 m (C)
m.cls = "doc"
z_way0, z_way1 = Z_YT1 + 1.6, Hg["z"] - Hg["hd"] - 1.4
m.box(AXIS - 2.6, AXIS + 2.6, S.gy(AXIS, (z_way0 + z_way1) / 2) - 0.12, S.gy(AXIS, (z_way0 + z_way1) / 2) + 0.12, z_way0, z_way1, "marble", skip=("bottom",))

# ============================================================ the moat: marble lining, coping and red railings on both banks; the bridge; the crossing
m.cls = "doc"
ring = list(MOAT.exterior.coords)
lin = MOAT.exterior
BRIDGE = rect("bridge")
CROSS = rect("crossing_E")
bx0, bx1 = AXIS - 2.3, AXIS + 2.3  # the bridge 4.6 m wide on the axis (S01 x 3297.5-3320)
skip_x = [(bx0 - 0.3, bx1 + 0.3), (CROSS[0] - 0.2, CROSS[1] + 0.2)]
n_seg = max(8, int(lin.length / 1.2))
pts = [lin.interpolate(k / n_seg, normalized=True) for k in range(n_seg + 1)]
c_ = MOAT.centroid
for a, b in zip(pts[:-1], pts[1:]):
    mxp, mzp = (a.x + b.x) / 2, (a.y + b.y) / 2
    dx, dz = b.x - a.x, b.y - a.y
    L = math.hypot(dx, dz)
    if L < 1e-3:
        continue
    nx, nz = -dz / L, dx / L
    # outward normal: away from the water
    if MOAT.contains(Point(mxp + nx * 0.3, mzp + nz * 0.3)):
        nx, nz = -nx, -nz
    ya, yb = S.gy(a.x + nx * 0.8, a.y + nz * 0.8), S.gy(b.x + nx * 0.8, b.y + nz * 0.8)
    top_a, top_b = ya + 0.08, yb + 0.08
    # the lining's face from the coping to below the water, and the coping slab 0.7 m wide on the bank
    m.poly([(a.x, top_a, a.y), (b.x, top_b, b.y), (b.x, WATER_Y - 0.6, b.y), (a.x, WATER_Y - 0.6, a.y)], "quay")
    m.poly([(a.x, top_a, a.y), (a.x + nx * 0.7, top_a, a.y + nz * 0.7), (b.x + nx * 0.7, top_b, b.y + nz * 0.7), (b.x, top_b, b.y)], "marble")
    m.poly([(a.x + nx * 0.7, top_a, a.y + nz * 0.7), (a.x + nx * 0.7, ya - 0.1, a.y + nz * 0.7), (b.x + nx * 0.7, yb - 0.1, b.y + nz * 0.7), (b.x + nx * 0.7, top_b, b.y + nz * 0.7)], "marble")
# the railings on both banks, 0.45 m back from the edge, broken at the bridge and the crossing (the leaf's red railings)
bank_line = MOAT.buffer(0.42, join_style=2).exterior
nrp = max(10, int(bank_line.length / 1.0))
cur = []
runs = []
for k in range(nrp + 1):
    q = bank_line.interpolate(k / nrp, normalized=True)
    blocked = any(x0 - 0.6 <= q.x <= x1 + 0.6 for x0, x1 in ((bx0, bx1), (CROSS[0] - 0.1, CROSS[1] + 0.1)))
    near_end = q.x < MOAT.bounds[0] + 0.3 or q.x > MOAT.bounds[2] - 0.3
    if blocked or near_end:
        if len(cur) > 2:
            runs.append(cur)
        cur = []
    else:
        cur.append((q.x, q.y))
if len(cur) > 2:
    runs.append(cur)
for i, r in enumerate(runs):
    railing(r, f"moat_rail_{i}", h=1.0, step=2.0, y_fn=lambda x, z: ground(x, z) + 0.08)
REPORT["moat"]["railing_runs"] = len(runs)
# the bridge on the axis: a flat marble deck (levelled 1839), its north end flared (S01), wooden railings (Varin), two gilt dragons (Varin; C)
bz0, bz1 = BRIDGE[2], BRIDGE[3]
yb0, yb1 = ground(AXIS, bz0 - 0.5), ground(AXIS, bz1 + 0.5)
deck_y = max(yb0, yb1) + 0.15
zc_m = float(np.mean([p[1] for p in ring if abs(p[0] - AXIS) < 3.0])) if any(abs(p[0] - AXIS) < 3.0 for p in ring) else (bz0 + bz1) / 2
m.cls = "doc"
m.box(bx0, bx1, WATER_Y - 0.8, deck_y, bz0, bz1, "marble", skip=("bottom",))  # deck and its spandrel walls (a solid flat bridge over a 3 m channel: C)
m.box(bx0 + 0.6, bx1 - 0.6, WATER_Y - 0.8, WATER_Y + 1.0, bz0 - 0.02, bz1 + 0.02, "underside", skip=("top", "bottom"))  # the opening under it, dark
fl = rect("bridge_flare")
for sg in (-1, 1):  # the flared north end: low splayed parapets (八字) from the deck's sides to S01's 9 m
    xa, xb = AXIS + sg * 2.3, AXIS + sg * (fl[1] - fl[0]) / 2
    m.poly([(xa, deck_y, bz0), (xb, ground(xb, fl[2]) + 0.05, fl[2]), (xb, ground(xb, fl[2]) + 0.6, fl[2]), (xa, deck_y + 0.6, bz0)], "marble")
    m.poly([(xa, deck_y, bz0), (xb, ground(xb, fl[2]) - 0.1, fl[2]), (xb, ground(xb, fl[2]) + 0.05, fl[2]), (xa, deck_y + 0.0, bz0)], "marble")
pave([(AXIS - 2.3, bz0), (AXIS + 2.3, bz0), (AXIS + (fl[1] - fl[0]) / 2, fl[2]), (AXIS - (fl[1] - fl[0]) / 2, fl[2])], "bridge_flare", dy=0.04, step=3.0, mat="marble", clear=False)
for sg in (-1, 1):
    railing([(AXIS + sg * 2.15, bz0), (AXIS + sg * 2.15, bz1)], f"bridge_rail_{sg}", h=1.05, step=1.2, y_fn=lambda x, z: deck_y)
m.cls = "fill"
for sg in (-1, 1):  # the gilt dragons on their bases at the bridge's south end (Varin; places and form C)
    x, z = AXIS + sg * 2.0, bz1 - 0.5
    m.box(x - 0.35, x + 0.35, deck_y, deck_y + 0.5, z - 0.45, z + 0.45, "marble")
    m.lathe([(0.25, deck_y + 0.5), (0.32, deck_y + 0.8), (0.18, deck_y + 1.15), (0.26, deck_y + 1.35), (0.1, deck_y + 1.6), (0.0, deck_y + 1.7)], 8, "gold", cx=x, cz=z)
m.cls = "doc"
S.kp("bridge_deck_SW", (bx0, deck_y, bz1))
S.kp("bridge_deck_SE", (bx1, deck_y, bz1))
S.kp("bridge_deck_NW", (bx0, deck_y, bz0))
S.kp("bridge_deck_NE", (bx1, deck_y, bz0))
for end, z in (("N", bz0), ("S", bz1)):
    S.joint(f"bridge_{end}", AXIS, z + (0.3 if end == "N" else -0.3) * 0, "bridge end", y=min(deck_y, S.gy(AXIS, z)) - 0.05)
    S.entry(f"bridge_{end}", AXIS, z - 1.0 if end == "N" else z + 1.0)
REPORT["bridge"] = {"width_m": round(bx1 - bx0, 2), "length_m": round(bz1 - bz0, 2), "deck_y": round(deck_y, 3), "water_y": round(WATER_Y, 3), "deck_above_water_m": round(deck_y - WATER_Y, 2)}
# the crossing east of the axis: a plain stone slab bridge (C)
m.cls = "fill"
cx0, cx1, cz0, cz1 = CROSS
cy = max(ground((cx0 + cx1) / 2, cz0 - 0.8), ground((cx0 + cx1) / 2, cz1 + 0.8)) + 0.1
m.box(cx0 - 0.1, cx1 + 0.1, WATER_Y - 0.8, cy, cz0 - 0.6, cz1 + 0.6, "quay", skip=("bottom",))
m.box(cx0 + 0.4, cx1 - 0.4, WATER_Y - 0.8, WATER_Y + 0.7, cz0 - 0.62, cz1 + 0.62, "underside", skip=("top", "bottom"))
S.entry("crossing_N", (cx0 + cx1) / 2, cz0 - 1.2)
S.entry("crossing_S", (cx0 + cx1) / 2, cz1 + 1.2)
m.cls = "doc"

# ============================================================ the inner court: 内朝房, the two ranges, the side walls, paving
for fid, nm in (("F0002", "neichaofang_W"), ("F0003", "neichaofang_E")):
    Hn = kit_spec(fid, "fill")
    Hn["st"] = {"front": [0.0]}
    Hn["rf"], Hn["rl"] = "xs", 1
    draw(nm, Hn, kp=False)
# the east range (no box: S01 draws it as the twin of B1178); nine bays facing west, the class small_house (C)
m.cls = "fill"
rx0, rx1, rz0, rz1 = rect("range_E")
nb = 9
Hre = dict(hf=(rx1 - rx0) / 2 + 0.6, hd=(rz1 - rz0) / 2, x=(rx0 + rx1) / 2, z=(rz0 + rz1) / 2, rot=-math.pi / 2, pl=0.45, e=0.66, o=0.82, pf=1.28, pb=0.0, ps=0.0, dia=0.23,
           st={"front": [0.0]}, bal=0, rf="xu", rl=1, db=0, ju=JU["small_house"], t="grey", te=None, bd="bm", dr=[4], rr="w", k="hall", cls="fill", src="class")
Hre["hf"], Hre["hd"] = (rz1 - rz0) / 2, (rx1 - rx0) / 2 + 0.6  # its front faces west: s runs along z
Hre["b"] = [(2 * (Hre["hf"] - Hre["e"])) / nb] * nb
Hre["d"] = [1.28, 2 * (Hre["hd"] - Hre["e"]) - 1.28]
Hre["base"] = S.gy(rx0 - 0.6, Hre["z"])
Hre["foot"] = S.gmin([(rx0 - 0.6, rz0), (rx1 + 0.6, rz1)]) - 0.15
Hre["eave"] = round(0.45 + 2.75 + 0.42, 2)
Hre["ridge"] = round(Hre["eave"] + 0.62 * (Hre["hd"] - Hre["e"] + 0.82), 2)
draw("range_E", Hre, kp=False)
# the side walls of the inner court (the garden wall, Round 19's W01): red palace wall with grey coping (C), from the moat's line to the 大宫门 wall's corners
m.cls = "doc"
WALL_H = 4.2
for nm in ("wall_inner_W", "wall_inner_E"):
    (ax, az), (bx, bz) = READ[nm]
    wall_run([(ax, az), (bx, bz)], WALL_H, nm, body="wallred", thick=1.2, base_h=0.8)
# the 大宫门 wall's two runs with the 左门
dgm_x0, dgm_x1, dgm_z0, dgm_z1 = rect("dgm")
zuoW, zuoE = mid("zuomen_W"), mid("zuomen_E")
for nm, zm in (("dgm_wall_W", zuoW), ("dgm_wall_E", zuoE)):
    pts_ = READ[nm]
    wall_run(pts_, WALL_H, nm, gaps=[(zm[0], zm[1], 1.8)], body="wallred", thick=1.2, base_h=0.8)
m.cls = "fill"
for nm, (x, z) in (("zuomen_W", zuoW), ("zuomen_E", zuoE)):
    # the gate's line: the wall's direction where it stands
    pts_ = READ["dgm_wall_W" if nm.endswith("W") else "dgm_wall_E"]
    (ax, az), (bx, bz) = pts_[0], pts_[1]
    rot = -math.atan2(bz - az, bx - ax)  # the gate's x along the wall (Mesh.push: x maps to (cos rot, -sin rot))
    wall_gate(x, z, rot, nm, w=2.4, h=4.4, thick=1.2, body="wallred")

# ============================================================ 大宫门 YM41-01: the dig's base (B), five bays; its terrace, the lions; the 外朝房; the road
m.cls = "doc"
DGM_W, DGM_D = 21.57, 11.33
dgm_b = [3.84, 4.0, 4.4, 4.0, 3.84]  # C: 20.08 m between the end columns, the base 21.57 m (S102) with a 0.75 m edge
dgm_edge = (DGM_W - sum(dgm_b)) / 2
Hd = hall_spec(AXIS, (dgm_z0 + dgm_z1) / 2, 0.0, dgm_b, [DGM_D / 2 - dgm_edge, DGM_D / 2 - dgm_edge], dgm_edge, 0.77, 4.16, "xs", True, "doc", bracket=True, ju="gate_hall")
Hd["k"] = "gate"
Hd["dr"] = [1, 2, 3]
Hd["fw"] = {"front": 4.4, "back": 4.4}
# its terrace (S01, height C) and the lions on it (S01's squares): raised before the gate is drawn, so its front flight lands on it
tx0, tx1, tz0, tz1 = rect("dgm_yuetai")
tz0 = Hd["z"] + Hd["hd"]
T_W = DGM_W
t_ground = max(S.gy(AXIS + s * T_W / 2, z) for s in (-1, 0, 1) for z in (tz0, tz1))
T_TOP = t_ground + 0.40
RAISED.append((AXIS - T_W / 2, AXIS + T_W / 2, tz0 - 0.05, tz1, T_TOP))
fw_dgm = draw("dgm", Hd)
plaque(Hd, 1, w=2.8, h=1.0)
DGM = dict(Hd)
m.push(AXIS, 0, (tz0 + tz1) / 2)
thw, thd = T_W / 2, (tz1 - tz0) / 2
t_foot = min(S.gy(AXIS + s * thw, (tz0 + tz1) / 2 + q * thd) for s in (-1, 1) for q in (-1, 1)) - 0.15
K.platform(thw, thd, T_TOP, t_foot, coping=False)
m.box(-thw - 0.03, thw + 0.03, T_TOP - 0.12, T_TOP + 0.01, -thd - 0.03, thd + 0.03, "granite", skip=("bottom",))
tf = K.flight("front", 0.0, thw, thd, T_TOP, 6.0)
kp_platform("dgm_terr", thw, thd, T_TOP)
tcorners = [m.world((sx * thw, 0, sq * thd)) for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
tfw = m.world(tf) if tf else None
m.pop()
for i, c in enumerate(tcorners[2:]):
    S.joint(f"dgm_terr_{i}", float(c[0]), float(c[2]), "terrace foot", y=t_foot)
S.FOOTPRINTS.append([(float(c[0]), float(c[2])) for c in tcorners])
if tfw is not None:
    S.entry("dgm_terr_front", float(tfw[0]), float(tfw[2]), float(tfw[1]))
S.deck("dgm_terrace", T_TOP, [(float(c[0]), float(c[2])) for c in tcorners])
for nm in ("lion_W", "lion_E"):
    (lx, lz) = READ[nm][0]
    lion(lx, lz, T_TOP, 0.0, nm)
REPORT["halls"]["dgm_terrace"] = {"frontage_m": round(T_W, 2), "depth_m": round(tz1 - tz0, 2), "platform_m": 0.40}
# the 外朝房 (F0254, F0255)
for fid, nm in (("F0254", "waichaofang_W"), ("F0255", "waichaofang_E")):
    Hw = kit_spec(fid, "fill")
    Hw["st"] = {"front": [0.0]}
    draw(nm, Hw, kp=False)
# the road 石甬路 south from the terrace's flight, 4.8 m (S01), to the model's end
m.cls = "doc"
rz0 = tz1 + (tfw[2] - tz1 if tfw is not None else 0.0)
rz1 = rect("road_S")[3]
pave([(AXIS - 2.4, rz0), (AXIS + 2.4, rz0), (AXIS + 2.4, rz1), (AXIS - 2.4, rz1)], "road", dy=0.06, step=4.0, mat="marble")

# ============================================================ the inner court's paving (M'Ghee's flagged court), round the moat's south bank
inner = Polygon([(READ["wall_inner_W"][0][0] + 0.7, MOAT.bounds[1]), (READ["wall_inner_E"][0][0] - 0.7, MOAT.bounds[1]),
                 (READ["wall_inner_E"][1][0] - 0.7, Hd["z"] - Hd["hd"]), (READ["wall_inner_W"][1][0] + 0.7, Hd["z"] - Hd["hd"])])
inner = inner.difference(MOAT.buffer(1.2))
# keep the part south of the moat
parts = [g for g in (inner.geoms if inner.geom_type == "MultiPolygon" else [inner]) if g.centroid.y > MOAT.centroid.y]
inner_s = max(parts, key=lambda g: g.area)
pave([tuple(p) for p in inner_s.exterior.coords[:-1]], "inner_court", dy=0.03)
# the yard north of the moat, between it and the gate line (paved, C)
north = Polygon([(MOAT.bounds[0] + 2.0, zw + 0.6), (XE_C + 0.9, zw + 0.6), (XE_C + 0.9, MOAT.bounds[3]), (MOAT.bounds[0] + 2.0, MOAT.bounds[3])]).difference(MOAT.buffer(1.2))
parts = [g for g in (north.geoms if north.geom_type == "MultiPolygon" else [north]) if g.centroid.y < MOAT.centroid.y]
north_y = max(parts, key=lambda g: g.area)
pave([tuple(p) for p in north_y.exterior.coords[:-1]], "gate_yard", dy=0.03)
# the axis way across the inner court, from the bridge to 大宫门's back flight (C)
z_w0, z_w1 = bz1 + 0.2, Hd["z"] - Hd["hd"] - 1.6
m.box(AXIS - 2.4, AXIS + 2.4, S.gy(AXIS, (z_w0 + z_w1) / 2) - 0.12, S.gy(AXIS, (z_w0 + z_w1) / 2) + 0.12, z_w0, z_w1, "marble", skip=("bottom",))
z_w0, z_w1 = zw + 2.2, bz0 - 0.1
m.box(AXIS - 2.4, AXIS + 2.4, S.gy(AXIS, (z_w0 + z_w1) / 2) - 0.12, S.gy(AXIS, (z_w0 + z_w1) / 2) + 0.12, z_w0, z_w1, "marble", skip=("bottom",))

# ============================================================ 寿山: the rock peaks behind the hall (S05 'jade shoots'; the leaf), on S01's rock ridges
m.cls = "fill"
rng = np.random.default_rng(19)
peaks = [(-14, -7, 4.5), (-9, -9.5, 6.5), (-4.5, -7.5, 5.0), (-1.5, -10.5, 7.5), (2.0, -8.0, 5.5), (5.5, -10.0, 6.8), (9.5, -7.5, 4.8), (13.5, -9.0, 5.8), (-11.5, -12.0, 3.8), (11.0, -12.5, 4.2)]
for k, (dx, dz, h) in enumerate(peaks):
    peak(AXIS + dx, Z_BACK + dz, h, 0.75 + 0.1 * (k % 3), 300 + k, name=f"peak_{k}_top" if k in (3, 5) else None)
K.rocks(AXIS - 8.0, Z_BACK - 6.0, 6.0, 2.0, 9, 41, hmax=1.6)
K.rocks(AXIS + 8.0, Z_BACK - 6.5, 6.0, 2.0, 9, 42, hmax=1.6)
for x in (AXIS - 8.0, AXIS + 8.0):
    S.FOOTPRINTS.append([(x - 6.5, Z_BACK - 8.5), (x + 6.5, Z_BACK - 8.5), (x + 6.5, Z_BACK - 3.5), (x - 6.5, Z_BACK - 3.5)])
S.CLEAR.append([(AXIS - 18, Z_BACK - 13.5), (AXIS + 18, Z_BACK - 13.5), (AXIS + 18, Z_BACK - 1.0), (AXIS - 18, Z_BACK - 1.0)])
m.cls = "doc"

# ============================================================ key points on the leaf's halls: the gate, the duty rooms
REPORT["court_depth_m"] = round(z_gateN - Z_YT1, 2)
REPORT["court_width_m"] = round(XE_C - XW_C, 2)
REPORT["inner_court_m"] = {"width": round(READ["wall_inner_E"][0][0] - READ["wall_inner_W"][0][0], 2), "depth_moat_to_dgm": round((Hd["z"] - Hd["hd"]) - MOAT.bounds[3], 2)}
REPORT["hall_to_dgm_terrace_m"] = round(tz1 - Z_BACK, 2)
REPORT["s01_hall_frontage_m"] = round(rect("hall_strip")[1] - rect("hall_strip")[0], 2)
REPORT["s01_dgm_frontage_m"] = round(dgm_x1 - dgm_x0, 2)
REPORT["s01_gate_frontage_m"] = round(gx1_ - gx0_, 2)
REPORT["triangles"] = m.count()

# ============================================================ write YM01
n_bytes = m.write_glb(HERE / "model.glb", "YM01 正大光明 Zhengda Guangming", extras={"frame": "x east along the front, y up, z south; origin at 正大光明殿's box front middle"})
aliases = ["YM01-01", "YM01-02", "YM01-03", "YM01-08", "YM01-09", "YM01-B1151", "YM01-B1154", "YM41-01", "YM41-02", "YM41-04"]
# the plan's wall segments inside the gate court: the model draws its walls there (walls_cut); the phantom gate boxes on the bridge and at the 左门 (gates.json G02; G27, G28)
cut_local = [(READ["wall_inner_W"][0][0] - 4.0, MOAT.bounds[1] - 12.0), (READ["wall_inner_E"][0][0] + 4.0, MOAT.bounds[1] - 12.0),
             (READ["wall_inner_E"][1][0] + 4.0, tz1 + 4.0), (READ["wall_inner_W"][1][0] - 4.0, tz1 + 4.0)]
walls_cut = [[S.to_scene((x, 0.0, z))[::2] for x, z in cut_local]]
summary = {
    "id": "YM01",
    "aliases": aliases,
    "name": "正大光明 Zhengda Guangming",
    "glb": "model.glb",
    "position": S.pos,
    "rotationY": S.rot,
    "line": "The formal entrance of the garden as it stood in the 1850s, from the terrace before 大宫门 to the rock peaks behind the audience hall: the plan S01 gives the layout, the yellow slip 样001-4 the hall's seven bays, depth and porches (A), Malone and Barrow its platform (B), the dig the gate's base (B), the leaf of 1744 the roofs, colours, railings and the gallery, the witnesses of 1860 the flagged courts, the marble canal and bridge, the lions. Heights, the halls round the courts and every ornament are C.",
    "rows": [
        ["Layout", "As S01 draws it (re-read in Round 19 in plan pixels, B): 大宫门 on the palace wall, the inner court with its offices and ranges, the moon-shaped canal, 出入贤良门 on the gate line, the court and 正大光明殿 with its terrace; S01 draws the hall and terrace 0.8 times the stated sizes (Q256), the model keeps the stated sizes centred where S01 draws them"],
        ["正大光明殿", "Seven bays 4.32 + 4.32 + 4.83 + 5.17 + 4.83 + 4.32 + 4.32 m with porches of 1.92 m all round, 16.0 m deep (the slip 样001-4, A); the rear porch walled in, the front end bays windows over a sill wall, the rear end bays walled (the slip, A; Barrow, B); ten red columns across the front (Malone, B); the platform 39.3 x 19.2 m, 1.22 m above the court (Malone, Barrow, B); three flights (Malone; the leaf); rolled 歇山, grey tile, a painted bracket band (the leaf, S337, Barrow, B); column 5.12 m and the roof's pitch C; Yongzheng's plaque 正大光明 (S05, A)"],
        ["Terrace 月台", "38.40 x 14.82 m, 0.26 m high, with four censers (S119, B; added 1775-1793); the balustrade and the censers' form C"],
        ["Court", "Flagged (Wolseley, M'Ghee 1860, B), 79 x 22.6 m between the side halls and from the terrace to the gate line (S01); the five-bay side halls 东西配殿 (S05, A; their form C); a covered way east from the hall (the leaf, Malone, B); the rock peaks of 寿山 behind (S05, the leaf; places and heights C)"],
        ["出入贤良门", "Five bays (S05, A), rolled 歇山 (S337, B), red plank doors in the middle bays (the leaf); the duty rooms either side, lower and gabled (S05, the leaf); the gate line's rubble wall about 4 m high with two side gates (Varin 1860, the leaf, S05; B); widths and heights C"],
        ["Canal and bridge", "The moon-shaped canal about 3 m wide lined with white marble (S05, S01, Varin; B), red railings on its banks (the leaf); one flat marble bridge on the axis, its north end flared (S01; levelled flat in 1839, S211, A), wooden railings and two gilt dragons (Varin, B; their form C); a slab crossing where S01 breaks the canal east of the axis (C). S05 gives three bridges (Q130)"],
        ["Inner court", "Flagged (M'Ghee 1860, B); the court offices 内朝房, five bays each (S05, A; form C); a long range on each side (S01; the east one has no box, C); the garden wall round it, red (Round 19's W01 on S01; colour and height C)"],
        ["大宫门", "Five bays (S05, A) on the dig's base 21.57 x 11.33 m, 0.77 m high (S102, B); rolled 歇山 (S337, B); red plank doors with gilt studs (Wolseley 1860, B); Yongzheng's plaque 圆明园 (S05, A); the column 4.16 m and the brackets C; on the palace wall (S42) with a 左门 either side (S42, S01; form C)"],
        ["Terrace and lions", "The gate's terrace as S01 draws it (21.6 x 10 m; height 0.40 m C) with a pair of bronze lions on stone pedestals where S01 draws two squares (1763, S42; Wolseley, Varin 1860; B); the lions' form C"],
        ["Before the gate", "The court offices 外朝房, five bays each (S05, A; at S01's boxes; form C); the stone road on the axis 4.8 m wide (S05, S42, S01; B)"],
        ["Beyond the model", "勤政殿 of 勤政亲贤 (YM02-01) and the spirit wall 大影壁 (YM41-12) are models of their own, drawn by this model's generator"],
        ["Assumed", "Every height but the platforms', the halls round the courts, the ranges and duty rooms, the side gates, the censers, the lions' and dragons' form, the balustrade, the brackets, the rock peaks: the hall kit's classes and the Qing manual's typology (C, the pale tint with conf=1)"],
    ],
    "caption": {"frontage_m": round(READ["wall_inner_E"][0][0] - READ["wall_inner_W"][0][0], 1), "depth_m": round(rz1 - (Z_BACK - 12.0), 1), "eave_m": REPORT["halls"]["zg"]["eave_m"], "ridge_m": REPORT["halls"]["zg"]["ridge_m"], "assumed": True, "confidence": "C"},
    "hides": ["GB02", "GB27", "GB28"],
    "bridges": ["BR006"],
    "walls_cut": walls_cut,
    "tris": m.count(),
    "glb_bytes": n_bytes,
}
S.write(HERE, "YM01", aliases, P, "origin at the front middle of 正大光明殿's box F0004 at its ground; x east along the front, y up, z south (scripts/model_site.py)", summary)
MAIN_REPORT = REPORT
print(f"YM01: {m.count()} triangles, GLB {n_bytes / 1e6:.2f} MB; axis {AXIS:.2f} (spread {REPORT['axis_spread_m']} m); court {REPORT['court_depth_m']} m deep; moat water {WATER_Y:.2f}, bridge deck {deck_y:.2f}")

# ============================================================ 勤政殿 YM02-01: its own model (five bays, 抱厦 front and back: S310 rec. 7310)
P2 = {
    "qz_plan": ("five bays with a three-bay porch 抱厦 front and back, facing south", "S310;S01", "A", "勤政殿地盘图样 (mhymy ysltd 7310, free part) and ysltd/11009: 五间 facing south with 抱厦三间 front and rear (A); S01 draws the same: five bays about 22 m, the middle three run on south and north (B, plan_readings.csv qz_*); S05 j80:11b 正殿五楹 (A)"),
    "qz_sizes": ("22.2 m frontage, 6.6 m deep body, porches 3.3 m", "S01", "B", "S01 in plan pixels (x 3627.5-3734, y 5397.5-5457.5); the bays' widths, the depth's split and every height C"),
    "qz_roof": ("rolled 歇山, grey; the porches' rolled roofs joined to the hall's slopes", "S08", "C", "the class (the 1744 leaf shows an earlier state here: S41); grey as the garden's halls (S08)"),
    "qz_plaques": ("勤政亲贤 front, 为君难 rear", "S05", "A", "S05 j80:18a: 額曰勤政親賢; 後楹額曰為君難; boards C"),
    "qz_court": ("the walled court before it as S01 draws it, paved, a gate in its south wall", "S01", "B", "S01 crop 'qinzheng': the court x 3602.5-3760, y 5460-5587, a small gate box in the south wall; white walls with grey coping (C)"),
}
S2 = Site("F0008")
m2 = Mesh(COL)
S2.m = m2
MAIN = (m, S, K)
m, S, K = m2, S2, HallKit(m2, S2.gy)
RAISED_SAVE = list(RAISED)
RAISED.clear()
K.ground = ground
READ2 = {k: [plan_local(*p, site=S2) for p in v] for k, v in PX.items()}
qx0, qx1 = min(p[0] for p in READ2["qz_hall"]), max(p[0] for p in READ2["qz_hall"])
qz0, qz1 = min(p[1] for p in READ2["qz_hall"]), max(p[1] for p in READ2["qz_hall"])
bsx0, bsx1 = min(p[0] for p in READ2["qz_baosha_S"]), max(p[0] for p in READ2["qz_baosha_S"])
bs_z1 = max(p[1] for p in READ2["qz_baosha_S"])
bn_z0 = min(p[1] for p in READ2["qz_baosha_N"])
QX = (qx0 + qx1) / 2
q_b = [(qx1 - qx0 - 1.6) / 5] * 5
Hq = hall_spec(QX, (qz0 + qz1) / 2, 0.0, q_b, [qz1 - qz0 - 1.6], 0.8, 0.6, 3.84, "xs", True, "doc", ju="main_hall")
Hq["st"] = {}
Hq["dr"] = [2]
Hq["rr"] = "w"
draw("qz", Hq)
plaque(Hq, -1, w=2.4, h=0.9)  # 为君难 on the rear (S05), here on the hall's back eave over the rear porch's roof (C)
for side, zA, zB, rot in (("S", qz1 - 0.8, bs_z1, 0.0), ("N", bn_z0, qz0 + 0.8, math.pi)):
    dep = abs(zB - zA)
    pb_b = [(bsx1 - bsx0 - 1.6) / 3] * 3
    zc = (zA + zB) / 2
    Hp = hall_spec(QX, zc, rot, pb_b, [dep - 0.8], 0.8, 0.6, 3.2, "xs", True, "doc", ju="small_house")
    Hp["base"] = Hq["base"]
    Hp["foot"] = min(Hp["foot"], Hq["foot"])
    Hp["eave"] = round(0.6 + 3.2 + 0.42, 2)
    Hp["ridge"] = round(Hq["eave"] + 0.9, 2)
    Hp["st"] = {"front": [0.0]}
    Hp["fw"] = {"front": 3.2}
    Hp["dr"] = [1]
    Hp["pf"] = 0
    draw(f"qz_baosha_{side}", Hp)
    if side == "S":
        plaque(Hp, 1, w=2.4, h=0.9)  # 勤政亲贤 (S05), on the front porch's eave (C)
        S.kp("qz_plaque", m.world((QX, Hp["base"] + Hp["eave"] - 0.5, zc + Hp["hd"] - Hp["e"] + 0.36)))
# the court before it: paving, white walls, the south gate (S01; C)
cx0_, cx1_ = min(p[0] for p in READ2["qz_court"]), max(p[0] for p in READ2["qz_court"])
cz0_, cz1_ = min(p[1] for p in READ2["qz_court"]), max(p[1] for p in READ2["qz_court"])
gq = [p for p in READ2["qz_gate"]]
gqx = (gq[0][0] + gq[1][0]) / 2
m.cls = "doc"
pave([(cx0_ + 0.5, max(cz0_, bs_z1 + 0.3)), (cx1_ - 0.5, max(cz0_, bs_z1 + 0.3)), (cx1_ - 0.5, cz1_ - 0.5), (cx0_ + 0.5, cz1_ - 0.5)], "qz_court", dy=0.03)
m.cls = "fill"
wall_run([(cx0_, cz0_), (cx0_, cz1_), (cx1_, cz1_), (cx1_, cz0_)], 3.4, "qz_wall", gaps=[(gqx, cz1_, 1.9)])
wall_run([(cx0_, cz0_), (QX - Hq["hf"] - 0.2, cz0_)], 3.4, "qz_wallNW")
wall_run([(QX + Hq["hf"] + 0.2, cz0_), (cx1_, cz0_)], 3.4, "qz_wallNE")
wall_gate(gqx, cz1_, 0.0, "qz_gate", w=2.6, h=3.8)
m.cls = "doc"
n2 = m.write_glb(ROOT / "models/YM02-01-qinzheng-dian/model.glb", "YM02-01 勤政殿 Qinzheng Dian", extras={"frame": "x east along the front, y up, z south; origin at the front middle of the box F0008"})
sm2 = {"id": "YM02-01", "aliases": [], "name": "勤政殿 Qinzheng Dian", "glb": "model.glb", "position": S.pos, "rotationY": S.rot,
       "line": "The emperor's office hall of 勤政亲贤 east of the audience court: five bays with a three-bay porch 抱厦 front and back as the Yangshi Lei plan 勤政殿地盘图样 has it (A) and S01 draws it (B), its walled court before it; every height, the roofs and the court's walls are C.",
       "rows": [["Plan", "Five bays facing south with three-bay porches front and rear (勤政殿地盘图样, mhymy ysltd 7310 and 11009, A; S05 j80:11b, A); 22.2 m wide on S01 (B)"],
                ["Roofs", "Rolled 歇山, grey, the porches' roofs joined to the hall's slopes (C: no picture of the 1860 state; the 1744 leaf shows an earlier one, S41)"],
                ["Plaques", "勤政亲贤 in front, 为君难 at the back (S05 j80:18a, A; boards C)"],
                ["Court", "As S01 draws it, walled, paved, a gate in its south wall (B; the walls' height and colour C)"],
                ["Inside", "In 1837 (most likely) the east study got a front porch, a south door and large glass panes (S211 竹叶亭杂记; not drawn: the interior is out of scope)"]],
       "caption": {"frontage_m": round(2 * Hq["hf"], 1), "depth_m": round(bs_z1 - bn_z0, 1), "eave_m": Hq["eave"], "ridge_m": Hq["ridge"], "assumed": True, "confidence": "C"},
       "hides": [], "tris": m.count(), "glb_bytes": n2, "made_by": "models/YM01-zhengda-guangming/zhengdaguangming.py"}
S.write(ROOT / "models/YM02-01-qinzheng-dian", "YM02-01", ["YM02-01"], P2, "origin at the front middle of the box F0008 at its ground; x east along the front, y up, z south (scripts/model_site.py)", sm2)
MAIN_REPORT["qinzheng"] = {"triangles": m.count(), "frontage_m": round(2 * Hq["hf"], 2), "depth_m": round(bs_z1 - bn_z0, 2), "court_m": [round(cx1_ - cx0_, 2), round(cz1_ - cz0_, 2)]}
print(f"YM02-01: {m.count()} triangles, GLB {n2 / 1e6:.2f} MB")

# ============================================================ 大影壁 YM41-12: its own model, 204.8 m south of the gate's terrace on the axis (S102), off the plan
P3 = {
    "yb_size": ("41.6 m long, 1.5 m thick, 4.57 m high", "S102;S02", "B", "the survey report: 东西长41.6 m (S102, E1017); Malone measured it before it was torn down: 137 ft long, over 5 ft thick, about 15 ft high (S02 p.69, E2114: 41.8 x 1.52 x 4.57 m)"),
    "yb_place": ("204.8 m south of the gate terrace's south edge, on the axis", "S102", "B", "自宫门月台南沿至影壁 204.8 m (S102, E1017); beyond the plan S01, which stops about 140 m south of the gate: on the model's axis (C for its bearing)"),
    "yb_form": ("a screen wall on a stone base, its faces framed, a tiled hip coping", "S02", "C", "Malone: an ornamented spirit wall (S02 p.69); the base, the panels and the coping the screen wall's typology (C)"),
}
S3 = Site("F0252")
m3 = Mesh(COL)
S3.m = m3
m, S, K = m3, S3, HallKit(m3, S3.gy)
K.ground = S3.gy
# the place: the main frame's axis, the terrace's south edge + 204.8 m
Sm = MAIN[1]
p_sc = Sm.to_scene((AXIS, 0.0, tz1 + 204.8))
S.pos = [round(p_sc[0], 3), round(S.G.land(p_sc[0], p_sc[2]) or S.G.at(p_sc[0], p_sc[2]), 3), round(p_sc[2], 3)]
S.rot = Sm.rot
m.cls = "doc"
g_yb = K.screen(0.0, 0.0, 41.6, 1.52, 4.57, tile="grey", panel="plaster", base=0.9)
for sgz in (1, -1):  # the ornament (Malone: 'ornamented', no more): a lozenge in the middle and a quarter-piece in each corner of the panel, grey brick (C)
    zf = sgz * (0.76 + 0.02)
    cy = g_yb + 0.9 + (4.57 - 0.9 - 0.5) / 2
    m.poly([(-3.2, cy, zf), (0.0, cy - 1.15, zf), (3.2, cy, zf), (0.0, cy + 1.15, zf)], "tile_grey")
    for sx in (-1, 1):
        for top in (True, False):
            x0 = sx * (20.8 - 0.6)
            y0_ = g_yb + 4.57 - 0.95 if top else g_yb + 1.1
            dy = -0.8 if top else 0.8
            m.poly([(x0, y0_, zf), (x0 - sx * 2.0, y0_, zf), (x0, y0_ + dy, zf)], "tile_grey")
for sx in (-1, 1):
    for sq in (-1, 1):
        S.joint(f"yb_{'W' if sx < 0 else 'E'}{'N' if sq < 0 else 'S'}", sx * 20.95, sq * 0.91, "base foot", y=S.gy(sx * 20.95, sq * 0.91) - 0.15)
S.FOOTPRINTS.append([(-20.95, -0.91), (20.95, -0.91), (20.95, 0.91), (-20.95, 0.91)])
S.kp("yb_top_W", (-20.8, S.gy(-20.8, 0) + 4.57, 0.0))
S.kp("yb_top_E", (20.8, S.gy(20.8, 0) + 4.57, 0.0))
n3 = m.write_glb(ROOT / "models/YM41-12-da-yingbi/model.glb", "YM41-12 大影壁 Da Yingbi", extras={"frame": "x east along the wall, y up, z south; origin at the wall's middle"})
sm3 = {"id": "YM41-12", "aliases": [], "name": "大影壁 Da Yingbi", "glb": "model.glb", "position": S.pos, "rotationY": S.rot,
       "line": "The spirit wall that closed the road south of 大宫门: its length, thickness and height from Malone's measurements and the survey report (B), its place 204.8 m south of the gate's terrace (the survey report, B), beyond the plan; its ornament is not known and its form is the screen wall's typology (C).",
       "rows": [["Size", "41.6 m long (S102), over 5 ft = 1.52 m thick and about 15 ft = 4.57 m high (Malone, S02 p.69); B"],
                ["Place", "On the axis, 204.8 m south of the 大宫门 terrace's south edge (S102, B); off S01, so the bearing is the model's axis (C)"],
                ["Form", "A stone base, the faces framed with a middle panel, a grey tiled hip coping (C: Malone calls it ornamented and gives no more)"],
                ["Later", "It stood after 1860 until it was torn down for its materials, after Malone measured it (S02 p.69)"]],
       "caption": {"frontage_m": 41.6, "depth_m": 1.52, "top_m": round(DATUM_M + S.pos[1] + 4.57 + 0.35, 2), "assumed": True, "confidence": "C"},
       "hides": [], "tris": m.count(), "glb_bytes": n3, "made_by": "models/YM01-zhengda-guangming/zhengdaguangming.py"}
S.write(ROOT / "models/YM41-12-da-yingbi", "YM41-12", ["YM41-12"], P3, "origin at the wall's middle at its ground; x east along the wall, y up, z south (scripts/model_site.py)", sm3)
MAIN_REPORT["yingbi"] = {"triangles": m.count(), "position": S.pos, "south_of_terrace_m": 204.8}
print(f"YM41-12: {m.count()} triangles, GLB {n3 / 1e6:.2f} MB at {S.pos}")
m, S, K = MAIN
json.dump(MAIN_REPORT, open(HERE / "report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
