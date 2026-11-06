#!/usr/bin/env python3
"""九洲清晏 Jiuzhou Qingyan (YM03), the emperor's residence on the largest island of the 后湖 Back Lake: the central axis, the eighth detailed model (Round 18).

  uv run python models/YM03-jiuzhou-qingyan/jiuzhouqingyan.py

The state is 1837-1860: the three axis halls burned on 丙申九月二十六日 (1836) and were rebuilt by 1837 'to the old form' (E1134); the rear porch 抱厦 of 九洲清晏殿 was added in
咸丰五年 (1855; S310 rec. 7237, 10881); 同道堂 was joined to its west in the approved rebuilding (E1169). The plan S01 carries names of the Tongzhi repair here (Q36): it gives
the layout and the positions; the written figures of 1855 (圆明园殿's slip, S310 rec. 11195) and of the Tongzhi survey (样006-3, the courts) give sizes and check the plan.
What is drawn: the front yard from 圆明园殿 to the 前湖 Front Lake and its landing; 圆明园殿 (five bays, the 1855 slip) with its ear rooms; the first court with its galleries,
side gates and two vessels; 奉三无私殿 (seven bays) and its terrace; the second court; 九洲清晏殿 (five bays, porches front and back) with the 1855 rear porch; the link and
同道堂 to its west; the back yard and the landing on the 后湖; the walls of the axis; the island's four bridges (南大桥, 如意桥, 棕亭桥 and the bridge to 来青亭).

Method (docs/METHOD.md, 'a compound from the kit and its evidence', Round 17): every hall is the hall kit (scripts/hall_parts.py) from its numbers, adapted to its evidence;
the layout read on S01 (plan_readings.csv, plan pixels, placed by the fit in use, research/georef/).
Writes, beside this file: model.glb, params.json, keypoints.json, joints.json, summary.json, report.json (models/README.md).
Frame (scripts/model_site.py): origin at the front middle of 圆明园殿's box F0018, at that box's ground; x east along the front, y up, z south.
Grades: what a source states for this axis (its plan, its bays, the 1855 slip, the leaf's colours and galleries) is `doc`; the forms carried in from the hall classes (the
ear rooms, the side gates, the link, 同道堂, the bridges' timber, the vessels, the brackets) are `fill` (assumed, C).
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
P = {
    "ymy_bays": ("4.16 + 4 x 3.84 m", "S310", "A", "圆明园殿 five bays, 明间一丈三尺, 四次间各一丈二尺 (NLC 样007-9-1 of 1855.3, the yellow slip as transcribed on mhymy record 11195; the same on the 1837 sheet); 19.52 m between the end columns"),
    "ymy_depth": ("7.04 + 2 x 1.92 m", "S310", "A", "进深二丈二尺 between the 金柱 lines, front and back porches 各深六尺 (same slip): 10.88 m between the eave columns"),
    "ymy_col": (3.84, "S310", "A", "檐柱高一丈二尺 (same slip)"),
    "ymy_pl": (0.704, "S310", "A", "台明高二尺二寸 (same slip)"),
    "ymy_edge": (0.928, "S310", "A", "下檐出二尺九寸 (same slip): the platform's edge beyond the eave columns"),
    "ymy_roof": ("rolled 硬山, grey", "S310;S76;S08", "B", "record 11195 reads 墀头 on the gables of the 1837 and 1855 sheets and infers a 硬山 roof after the fire (the record author's inference); the 1744 leaf drew a 歇山 (Q100); rolled ridge: the 1745 woodcut's curved ridge ends (S76); grey: the leaf (S08)"),
    "ymy_doors": ("door screens on the 金柱 line, open porches", "S310", "B", "record 11195: in 1837 the 隔扇 were moved to the 金柱 line; the 1745 woodcut draws an open verandah (S76)"),
    "ymy_plaque": ("圆明园, Kangxi's hand, on the front eave", "S05;S310", "A", "S05 j80:1b, 21a 前第一層殿恭懸聖祖御書圓明園額; record 7105 前檐悬; the board's size and colours C"),
    "ymy_ears": ("two-cell ear rooms at both ends", "S01", "C", "S01 draws a two-cell block at each end of the hall, flush with its front half; read as ear rooms 耳房, their form the class's"),
    "yard": ("walled yard from the hall to the shore, landing", "S01;S02", "B", "S01 draws two lines from the hall's front to the shore and the label inside; the landing YMC-023 (Round 9) on the shore; the walls 1.4 m (C); Malone's caption of the 1744 woodcut: reeds and rocks at the water's edge before the hall (S02 p.78): rocks either side outside the yard (C)"),
    "court1": ("S01's: 34.5 m deep (eave columns), 22.6 m between the walls' inner faces", "S01;S310", "B", "S01 places the halls and the walls (re-read in plan pixels); the Tongzhi survey (NLC 样006-3 = 样062-24, 1873-74, quoted in mhymy record 11901) writes 圆明园殿后檐至奉三无私前檐10丈6尺 = 33.92 m (S01 within 0.6 m) and 东西宽8丈1尺2寸 = 25.98 m: 3.4 m wider than S01's walls, which would cut the halls S01 draws beside them; the plan is kept (Q250)"),
    "court2": ("S01's: 22.5 m deep (eave columns)", "S01;S310", "B", "S01 places 九洲清晏殿's front behind 奉三无私殿's; the Tongzhi survey writes 5丈7尺1寸 = 18.27 m (样006-3), perhaps for the Tongzhi design's deeper 双卷 hall: the plan's position is kept (Q250)"),
    "fs_bays": ("7: 3.52 + 4 x 3.04 + 2 x 2.88 m", "S05;S310;S01", "C", "七楹 (S05 j80:20b, A); 前后有廊 (record 7271, B); S01 draws the hall wall to wall, 23.3 m with its edges; the widths C, the middle bay widest as in 圆明园殿's slip"),
    "fs_depth": (10.88, "S310", "C", "between the eave columns, 圆明园殿's section carried over (C); the hall's middle where S01 draws it"),
    "fs_col": (4.16, "S310", "C", "one 尺 above 圆明园殿 (C): the second hall of the axis; 慎德堂 on the same island measures 4.35 m (record 7342)"),
    "fs_pl": (0.8, "S310", "C", "a little above 圆明园殿's 0.704 m (C)"),
    "fs_roof": ("rolled 歇山, grey", "S08", "B", "the 1744 leaf: 歇山, ridge apparently rolled, grey tile (S08 P0003, a reading); rebuilt 'to the old form' in 1837 (E1134)"),
    "fs_terrace": ("20 x 5.2 m, 0.6 m", "S01", "C", "S01 draws a rectangle before the hall (about 20 by 5.2 m); its height a step below the hall's floor (C)"),
    "jz_bays": ("5: 3.84 + 4 x 3.20 m", "S310;S01", "C", "five bays (record 7237, A for 1855; S05 says 七楹 for the 1780s, Q101, Q163); the widths C, to S01's drawn 18.1 m"),
    "jz_depth": (10.88, "S310", "C", "前后有廊 (record 7237, A); 圆明园殿's section carried over (C)"),
    "jz_col": (4.16, "S310", "C", "as 奉三无私殿 (C)"),
    "jz_pl": (0.9, "S01;S70", "C", "P0365 shows the hall's site as a low mound against the back lake; the platform C"),
    "jz_roof": ("rolled 歇山, grey, the largest roof of the island", "S08", "B", "the 1744 leaf: the biggest roof on the island, 歇山, the ridge reads as rolled (not certain) (S08 P0003)"),
    "jz_baosha": ("3 bays, 4.16 m deep, behind the hall", "S310", "A", "后殿五间接后抱厦三间 (record 7237); 样005-27-1 is the design and the work was done in 咸丰五年 (1855) (record 10881); its depth and roof C"),
    "jz_plaques": ("九洲清晏 front, 蔚然深秀 rear", "S05", "A", "S05 j80:21a, 23a: Yongzheng's plaque in front, 蔚然深秀 at the back; boards C"),
    "tongdao": ("the link and 同道堂 at their boxes", "S310;S01", "C", "the approved rebuilding gave the hall's west side the 同道堂 annex (样010-3, E1169); S01 draws a three-cell link and a three-bay hall there (F0569, F0022); their forms the class's"),
    "walls": ("white plaster, grey coping, 3.2 m", "S01;S08", "B", "S01 draws the walls of the axis; the leaf paints the island's walls white with grey coping (S08 P0003); height C"),
    "galleries": ("covered galleries along the courts' sides", "S08", "B", "the 1744 leaf shows covered galleries with white walls and a row of pierced windows between the axis halls (S08 P0003); where they run is C (S01 draws only the walls)"),
    "gates": ("a gate in each side wall of the first court", "S08", "C", "the leaf shows a red gate in a white wall beside the front hall (east); the west one mirrored, both C"),
    "vessels": ("two bronze vessels on stands", "S01", "C", "S01's two marks in the first court; vessels as at the other courts of the garden (C)"),
    "trees": ("flowering trees in the courts", "S08", "B", "the leaf: pink-flowering trees (peach or apricot) all through the courts (S08 P0003, species B); four, places C"),
    "bridges": ("stone abutments, timber deck, red railings", "S08;S70", "B", "the leaf: a flat timber bridge with red-brown railings on the island's west side and a stepped timber bridge with railings at its south-east (S08 P0003, A for 1744); today's 南大桥 and 如意桥 rebuilt on dressed-stone abutments (P0367, P0793, B); decks at Round 10's levels"),
    "zongting": ("a pavilion on the bridge", "S01;S70", "C", "the name 棕亭桥 (S01, read as a guess) and today's rebuilt pavilion bridge (P0368, B for the type); the pavilion's size and roof C"),
    "landings": ("dressed-stone landings with steps to the water", "S01;S02", "C", "Round 9's landings YMC-023 (front) and YMC-031 (back) on S01's shores; M'Ghee and the 1860 witnesses reached the apartments by water and paths (S02 pp.180-183); the steps C"),
}
V = {k: v[0] for k, v in P.items()}

COL = {
    "lacquer": "#8a2f22", "lacquer_dark": "#532218", "wall": "#8e8a84", "plaster": "#e4ddcf", "glass_lattice": "#2b3137", "sill": "#7d7973",
    "band": "#2e6a6c", "bracket": "#3b7b70", "bandred": "#7d2c20", "platform": "#b7b0a1", "coping": "#d2ccbe", "step": "#c8c1b1", "marble": "#e9e5dc",
    "underside": "#4b453d", "fascia": "#3a2a22", "wallred": "#9b3d2c", "wallwhite": "#e8e2d6", "rock": "#b9ae98", "pave": "#bdb6a6", "gold": "#c9a245",
    "plaque": "#20406a", "bronze": "#4f5c4e", "timber": "#7a5a3c", "rail": "#8c3a26", "quay": "#c4bcab",
    "trunk": "#5a4634", "leaf_peach": "#6f8a45", "blossom": "#d8a7b1",
    "tile_grey": "#5f6469", "ridge_grey": "#4a4e52",
}

S = Site("F0018")
m = Mesh(COL)
S.m = m
KIT = json.load(open(ROOT / "site/reconstruction/data/kit_1860.json", encoding="utf-8"))["halls"]
FEATS = S.F
STRUCT = json.load(open(ROOT / "site/reconstruction/generated/structures.json", encoding="utf-8"))


def plan_local(px, py):
    lon, lat = plan_to_wgs84(np.array([px], float), np.array([py], float))
    x, z = to_xz(float(lon[0]), float(lat[0]))
    return S.to_local(x, z)


READ = {}
for r in csv.DictReader(open(HERE / "plan_readings.csv", encoding="utf-8")):
    READ[r["name"]] = [plan_local(*map(float, p.split())) for p in r["plan_px"].split(";")]


def rect(name):
    (ax, az), (bx, bz) = READ[name]
    return min(ax, bx), max(ax, bx), min(az, bz), max(az, bz)


def mid(name):
    x0, x1, z0, z1 = rect(name)
    return (x0 + x1) / 2, (z0 + z1) / 2


# the axis: the middles of the halls, the terrace, the walls, the yard and the two marks as S01 draws them; one straight line (the frame's z) through their mean
_ax = [mid(n)[0] for n in ("ymy_hall", "fs_hall", "fs_terrace", "jz_hall")] + [np.mean([p[0] for p in READ["court1_marks"]]),
                                                                              (READ["wall_W"][0][0] + READ["wall_E"][0][0]) / 2, (READ["yard_W"][0][0] + READ["yard_E"][0][0]) / 2]
AXIS = float(np.mean(_ax))
AXIS_SPREAD = float(max(_ax) - min(_ax))
REPORT = {"halls": {}, "axis_x": round(AXIS, 2), "axis_spread_m": round(AXIS_SPREAD, 2), "axis_reads": [round(float(v), 2) for v in _ax]}


def ground(x, z):
    return S.gy(x, z)


K = HallKit(m, ground)


def compass(dx, dz):
    return ("N" if dz < 0 else "S") + ("W" if dx < 0 else "E")


def box_local(fid):
    c, u, hf, hd, base = box_frame(FEATS, fid)
    x, z = S.to_local(*c)
    x2, z2 = S.to_local(*(c + u))
    return x, z, math.atan2(x2 - x, z2 - z), hf, hd


def kp_platform(name, hf, hd, y_foot, y_top, anchor=True):
    c0 = m.world((0, 0, 0))
    for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        w = m.world((sx * hf, 0, sq * hd))
        tag = compass(w[0] - c0[0], w[2] - c0[2])
        S.kp(f"{name}_pl_foot_{tag}", (w[0], y_foot if y_foot is not None else S.gy(float(w[0]), float(w[2])), w[2]), anchor=anchor)
        S.kp(f"{name}_pl_top_{tag}", (w[0], y_top, w[2]))


def kp_roof(name, H):
    """The eave's corner tips and the ridge's ends (what a painting of the island shows of a hall), named by compass."""
    CS, CQ, o = H["hf"] - H["e"], H["hd"] - H["e"], H["o"]
    tip = H["base"] + H["eave"] - o * 0.5
    c0 = m.world((0, 0, 0))
    for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        w = m.world((sx * (CS + o), 0, sq * (CQ + o)))
        S.kp(f"{name}_eave_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], tip, w[2]))
    hz = CQ + o
    band = min(0.12 * hz, 0.6) if H["rl"] else 0.0
    rh = {"wd": max(CS + o - 0.85 * (hz - band), 0.5), "xs": CS + o - 0.4 * (hz - band)}.get(H["rf"], CS + o)  # as hall_parts.roof draws them (歇山: the hip steps in 0.4 of the slope to the gable)
    for sx in (-1, 1):
        w = m.world((sx * rh, 0, 0))
        S.kp(f"{name}_ridge_{'W' if w[0] < c0[0] else 'E'}", (w[0], H["base"] + H["ridge"], w[2]))


def kp_flight(name, side, width, hd, y_top, foot):
    for lr, lat in (("L", -1), ("R", 1)):
        a = lat * width / 2 * (1 if side == "front" else -1)
        q = hd if side == "front" else -hd
        S.kp(f"{name}_fl_{side}_{lr}_top", m.world((a, y_top, q)))
        S.kp(f"{name}_fl_{side}_{lr}_foot", m.world((a, foot[1], foot[2])), anchor=True)


def draw(name, H, kp=True):
    m.cls = H["cls"]
    m.push(H["x"], 0.0, H["z"], H["rot"])
    feet = K.hall(H)
    corners = [m.world((sx * H["hf"], 0, sq * H["hd"])) for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    fw = {k: m.world(v) for k, v in feet.items()}
    if kp:
        kp_platform(name, H["hf"], H["hd"], None, H["base"] + H["pl"])
        kp_roof(name, H)
        for k, f in feet.items():
            side, off = k.split("_")
            if float(off) == 0.0 and side in ("front", "back"):
                kp_flight(name, side, H.get("fw", {}).get(side, 2.4), H["hd"], H["base"] + H["pl"], f)
    for i, c in enumerate(corners):
        S.JOINTS.append([f"{name}_pl_{i}", float(c[0]), H["foot"], float(c[2]), "platform foot"])
    m.pop()
    S.FOOTPRINTS.append([(float(c[0]), float(c[2])) for c in corners])
    for k, f in fw.items():
        S.entry(f"{name}_{k}", float(f[0]), float(f[2]), float(f[1]))
    REPORT["halls"][name] = {"frontage_m": round(2 * H["hf"], 2), "depth_m": round(2 * H["hd"], 2), "platform_m": H["pl"], "eave_m": H["eave"], "ridge_m": H["ridge"], "roof": H["rf"],
                             "rolled": int(bool(H["rl"])), "tiles": H["t"], "bays": len(H["b"]), "flights": len(feet), "grade_class": H["cls"],
                             "x": round(H["x"], 2), "z": round(H["z"], 2)}
    return fw


def hall_spec(x, z, rot, bays, depth_cols, edge, pl, col, porch, roof, rolled, cls, bracket=False, ju="main_hall", over=None):
    """A hall from its bays and its section: platform = columns + edge; eave and ridge from the column, the band and the 举架 over the half-span."""
    span = sum(bays)
    hf, hd = span / 2 + edge, depth_cols / 2 + edge
    gx = [x + s * math.cos(rot) * hf + q * math.sin(rot) * hd for s in (-1, 1) for q in (-1, 1)]
    gz = [z - s * math.sin(rot) * hf + q * math.cos(rot) * hd for s in (-1, 1) for q in (-1, 1)]
    gs = [S.gy(a, b) for a, b in zip(gx, gz)]
    fx, fz = x + math.sin(rot) * hd, z + math.cos(rot) * hd
    base = S.gy(fx, fz)
    band = 0.85 if bracket else 0.42
    eave = round(pl + col + band, 2)
    o = 1.25 if col >= 4.0 else 1.1
    rise = round(0.62 * (depth_cols / 2 + o), 2)
    H = dict(hf=hf, hd=hd, base=base, foot=min(gs) - 0.15, pl=pl, eave=eave, ridge=round(eave + rise, 2), e=edge, o=o, b=list(bays),
             d=[porch, depth_cols - 2 * porch, porch] if porch else [depth_cols], pf=porch, pb=porch, ps=0, dia=0.36 if col < 4.0 else 0.4,
             st={"front": [0.0], "back": [0.0]}, bal=0, rf=roof, rl=1 if rolled else 0, db=0, ju=JU[ju], t="grey", te=None, bd="br" if bracket else "bm",
             dr=list(range(len(bays))), rr="d", k="hall", x=x, z=z, rot=rot, cls=cls, src="dossier")
    if over:
        H.update(over)
    return H


def plaque(H, q_sign=1, w=2.6, h=1.0):
    """A plaque board 匾 on the eave band at the hall's middle bay, facing out of the front (q_sign 1) or the back (-1). Board blue with a gold frame (C)."""
    m.push(H["x"], 0, H["z"], H["rot"])
    CQ = H["hd"] - H["e"]
    q = q_sign * (CQ + 0.22)
    y1 = H["base"] + H["eave"] - 0.05
    m.box(-w / 2 - 0.1, w / 2 + 0.1, y1 - h - 0.1, y1, q - 0.04 if q_sign > 0 else q - 0.06, q + 0.06 if q_sign > 0 else q + 0.04, "gold")
    zf = q + q_sign * 0.065
    m.poly([(-w / 2, y1 - h, zf), (w / 2, y1 - h, zf), (w / 2, y1 - 0.1, zf), (-w / 2, y1 - 0.1, zf)], "plaque")
    m.pop()


def wall_run(pts, h, name, gaps=(), thick=0.9):
    """A white wall along pts, broken where a gap (x, z, half width) lies on it; its feet are joints, its outline a footprint."""
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
        K.wall(r, h, thick=thick, cap="grey", body_mat="wallwhite")
        S.FOOTPRINTS.append([(float(x), float(z)) for x, z in list(LineString(r).buffer(thick / 2 + 0.1, cap_style="flat").exterior.coords)[:-1]])
        for k, (x, z) in enumerate(r):
            S.joint(f"{name}{i}_{k}", x, z, "wall foot", y=S.gy(x, z) - 0.15)
    return runs


def wall_gate(x, z, rot, name, w=2.6, h=3.6, thick=0.9):
    """A gate in a wall 随墙门 (C): two piers, a lintel band, red plank doors set in, a small rolled roof along the wall; entries both sides."""
    m.push(x, 0, z, rot)
    g = min(K.gy_local(a, b) for a in (-w / 2 - 0.5, w / 2 + 0.5) for b in (-thick, thick))
    y0 = g - 0.15
    for sg in (-1, 1):
        m.box(sg * w / 2 - (0.5 if sg > 0 else 0) + (0 if sg > 0 else -0.5) + (0.5 if sg > 0 else 0), sg * w / 2 + (0.5 if sg > 0 else 0), y0, g + h - 0.6, -thick / 2 - 0.05, thick / 2 + 0.05, "wallwhite") if False else None
        a0, a1 = (w / 2, w / 2 + 0.6) if sg > 0 else (-w / 2 - 0.6, -w / 2)
        m.box(a0, a1, y0, g + h - 0.6, -thick / 2 - 0.08, thick / 2 + 0.08, "wallwhite")
        m.box(a0, a1, y0, g + 0.5, -thick / 2 - 0.1, thick / 2 + 0.1, "platform")
    m.box(-w / 2, w / 2, g + h - 1.25, g + h - 0.6, -thick / 2 - 0.05, thick / 2 + 0.05, "band")
    m.box(-w / 2, w / 2, y0, g + 0.15, -thick / 2 - 0.2, thick / 2 + 0.2, "step")
    for i, (a0, a1) in enumerate(((-w / 2 + 0.05, -0.02), (0.02, w / 2 - 0.05))):
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


def gallery_run(pts, wall_side, name, width=2.4):
    """A covered gallery 游廊 along pts with the court's wall behind it (white, pierced windows 什锦窗 on its faces), its floor 0.3 m above the ground."""
    K.gallery(pts, width, lambda a, b: S.gy(a, b) + 0.3, eave=2.9, ridge=4.0, wall_side=wall_side, wall_mat="wallwhite")
    for (ax, az), (bx, bz) in zip(pts[:-1], pts[1:]):
        L = math.hypot(bx - ax, bz - az)
        if L < 0.8:
            continue
        ux, uz = (bx - ax) / L, (bz - az) / L
        nx, nz = -uz, ux
        # the wall's faces in the gallery's frame: +z on the right of the run (hall_parts.gallery)
        rot = math.atan2(ux, uz) - math.pi / 2
        mx, mz = (ax + bx) / 2, (az + bz) / 2
        y0 = max(S.gy(ax, az), S.gy(bx, bz), S.gy(mx, mz)) + 0.3
        m.push(mx, 0, mz, rot)
        qz = wall_side * (width / 2 - 0.2)
        n = max(1, round(L / 3.2))
        for k in range(n):
            s = -L / 2 + L * (k + 0.5) / n
            for face in (qz - 0.19, qz + 0.19):
                sg = 1 if face > qz else -1
                f = face + sg * 0.01
                m.poly([(s - 0.45, y0 + 1.0, f), (s + 0.45, y0 + 1.0, f), (s + 0.45, y0 + 1.9, f), (s - 0.45, y0 + 1.9, f)], "coping")
                m.poly([(s - 0.33, y0 + 1.1, f + sg * 0.005), (s + 0.33, y0 + 1.1, f + sg * 0.005), (s + 0.33, y0 + 1.8, f + sg * 0.005), (s - 0.33, y0 + 1.8, f + sg * 0.005)], "glass_lattice")
        m.pop()
        S.FOOTPRINTS.append([(ax + nx * width / 2, az + nz * width / 2), (bx + nx * width / 2, bz + nz * width / 2), (bx - nx * width / 2, bz - nz * width / 2), (ax - nx * width / 2, az - nz * width / 2)])
    for k, (x, z) in enumerate((pts[0], pts[-1])):
        S.joint(f"{name}_{k}", x, z, "gallery foot", y=S.gy(x, z) - 0.15)


def pave(poly, name, dy=0.03, step=5.0):
    """Paving over an outline, following the ground in cells; the planting keeps off it (clear)."""
    pg = Polygon(poly)
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
                m.flat([(float(a), float(b)) for a, b in c], 0.0, "pave") if False else None
                pts = [(float(a), S.gy(float(a), float(b)) + dy, float(b)) for a, b in c]
                if len(pts) >= 3:
                    # a cell as a fan of triangles at its corners' ground (the ground is near level here)
                    for t in range(1, len(pts) - 1):
                        m.poly([pts[0], pts[t], pts[t + 1]], "pave")
    S.CLEAR.append([tuple(p) for p in poly])


def tree(x, z, h, seed, blossom=False):
    rng = np.random.default_rng(seed)
    g = S.gy(x, z)
    m.prism([(x + 0.13 * math.cos(t), z + 0.13 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 7)[:-1]], g - 0.1, g + h * 0.45, "trunk", top=False)
    mat = "blossom" if blossom else "leaf_peach"
    m.lathe([(0.0, g + h * 0.38), (h * 0.34, g + h * 0.58), (h * 0.3, g + h * 0.82), (0.0, g + h)], 7, mat, cx=x + rng.uniform(-0.2, 0.2), cz=z + rng.uniform(-0.2, 0.2))


def vessel(x, z, name):
    """A bronze vessel on a stone stand (C): a square stand, a round-bellied vessel with a lid."""
    g = S.gy(x, z)
    m.box(x - 0.55, x + 0.55, g - 0.15, g + 0.75, z - 0.55, z + 0.55, "marble")
    m.box(x - 0.65, x + 0.65, g + 0.65, g + 0.8, z - 0.65, z + 0.65, "marble")
    m.lathe([(0.25, g + 0.8), (0.42, g + 0.95), (0.55, g + 1.35), (0.42, g + 1.75), (0.3, g + 1.85), (0.38, g + 1.95), (0.22, g + 2.2), (0.06, g + 2.45), (0.0, g + 2.5)], 10, "bronze", cx=x, cz=z)
    S.joint(f"{name}_stand", x, z, "stand foot", y=g - 0.15)
    S.FOOTPRINTS.append([(x - 0.7, z - 0.7), (x + 0.7, z - 0.7), (x + 0.7, z + 0.7), (x - 0.7, z + 0.7)])


def landing(px, pz, ux, uz, width, name, water_y, yard_y=None):
    """A dressed-stone landing on the shore: a quay platform at the ground and steps down along (ux, uz) into the water to 0.3 m below its level (C)."""
    rot = math.atan2(ux, uz)
    m.push(px, 0, pz, rot)
    g = S.gy(px, pz) if yard_y is None else yard_y
    n = max(1, round((g - (water_y - 0.3)) / 0.18))
    tread = 0.35
    rise = (g - (water_y - 0.3)) / n
    run = n * tread
    bed = min(S.gy(*[float(v) for v in (m.world((0, 0, run + 0.5))[0], m.world((0, 0, run + 0.5))[2])]), water_y - 1.2) - 0.1
    # the quay: a platform 2 m deep at the top, its face down to the bed, side walls
    m.box(-width / 2 - 1.2, width / 2 + 1.2, bed, g, -2.0, 0.0, "quay", skip=("bottom",))
    m.box(-width / 2 - 1.25, width / 2 + 1.25, g - 0.15, g + 0.02, -2.05, 0.05, "coping", skip=("bottom",))
    for k in range(n):
        m.box(-width / 2, width / 2, bed, g - (k + 1) * rise, k * tread, (k + 1) * tread, "step", skip=("bottom",))
    for sg in (-1, 1):
        a0, a1 = (width / 2, width / 2 + 1.2) if sg > 0 else (-width / 2 - 1.2, -width / 2)
        m.poly([(a0, g + 0.02, 0.0), (a1, g + 0.02, 0.0), (a1, water_y + 0.3, run), (a0, water_y + 0.3, run)], "coping")
        for a in (a0, a1):
            m.poly([(a, g + 0.02, 0.0), (a, water_y + 0.3, run), (a, bed, run), (a, bed, 0.0)], "quay")
        m.poly([(a0, water_y + 0.3, run), (a1, water_y + 0.3, run), (a1, bed, run), (a0, bed, run)], "quay")
    top = m.world((0, 0, -1.0))
    for sg in (-1, 1):
        w_ = m.world((sg * (width / 2 + 1.2), 0, -2.0))
        S.joint(f"{name}_quay{sg:+d}", float(w_[0]), float(w_[2]), "quay foot", y=g - 0.15)
    for lr, s_ in (("L", -width / 2), ("R", width / 2)):
        S.kp(f"{name}_top_{lr}", m.world((s_, g, 0.0)))
    m.pop()
    S.entry(f"{name}_top", float(top[0]), float(top[2]), g)
    return run


# ============================================================ the halls of the axis, front to back
ZY = mid("ymy_hall")[1]
ZF = mid("fs_hall")[1]
JZ_FRONT = rect("jz_hall")[3]

# 圆明园殿 YM03-01: the 1855 slip (A)
ymy_b = [3.84, 3.84, 4.16, 3.84, 3.84]
Hy = hall_spec(AXIS, ZY, 0.0, ymy_b, 7.04 + 2 * 1.92, V["ymy_edge"], V["ymy_pl"], V["ymy_col"], 1.92, "ys", True, "doc")
Hy["fw"] = {"front": 4.16, "back": 4.16}
Hy["dr"] = [0, 1, 2, 3, 4]
draw("ymy", Hy)
plaque(Hy, 1, w=2.8, h=1.0)
S.kp("ymy_plaque", m.world((AXIS, Hy["base"] + Hy["eave"] - 0.55, ZY + Hy["hd"] - Hy["e"] + 0.3)))
YMY = dict(Hy)

# its ear rooms (S01 two cells each; C)
m.cls = "fill"
for nm, sg in (("ymy_ear_W", -1), ("ymy_ear_E", 1)):
    x0, x1, z0, z1 = rect(nm)
    inner = AXIS + sg * Hy["hf"]
    outer = x0 if sg < 0 else x1  # S01's outer end of the block
    w_ = abs(outer - inner)
    zf = ZY + Hy["hd"] - 0.6  # flush with the hall's front half (S01)
    dep = max(z1 - z0, 3.2)
    He = dict(hf=w_ / 2, hd=dep / 2, base=S.gy((inner + outer) / 2, zf), foot=S.gy((inner + outer) / 2, zf) - 0.15, pl=0.45, e=0.3, o=0.75, b=[(w_ - 0.6) / 2] * 2, d=[dep - 0.6],
              pf=0, pb=0, ps=0, dia=0.28, st={}, bal=0, rf="ys", rl=1, db=0, ju=JU["small_house"], t="grey", te=None, bd="bm", dr=[], rr="w", k="hall",
              x=(inner + outer) / 2, z=zf - dep / 2, rot=0.0, cls="fill", src="class")
    He["eave"], He["ridge"] = round(0.45 + 2.9 + 0.42, 2), round(0.45 + 2.9 + 0.42 + 0.62 * (dep / 2 + 0.75), 2)
    draw(nm, He, kp=False)

# 奉三无私殿 YM03-02: seven bays (S05), porches front and back (record 7271); widths C
fs_b = [2.88, 3.04, 3.04, 3.52, 3.04, 3.04, 2.88]  # Round 18 v2: wall to wall on S01 (23.3 m with its edges), not the Tongzhi survey's 25.98 m (Q250)
Hf = hall_spec(AXIS, ZF, 0.0, fs_b, V["fs_depth"], 0.93, V["fs_pl"], V["fs_col"], 1.92, "xs", True, "doc", bracket=False)
Hf["fw"] = {"front": 3.84, "back": 3.84}
Hf["dr"] = [2, 3, 4]
draw("fs", Hf)
plaque(Hf, 1, w=2.6, h=0.95)
FS = dict(Hf)
# its front terrace 月台 (S01), 0.6 m, a flight on the axis (C)
m.cls = "doc"
tx0, tx1, tz0, tz1 = rect("fs_terrace")
thw, tdep = (tx1 - tx0) / 2, max(tz1 - tz0, 4.0)
tz_mid = ZF + Hf["hd"] + tdep / 2 - 0.05
m.push(AXIS, 0, tz_mid)
tb = S.gy(AXIS, tz_mid + tdep / 2)
K.platform(thw, tdep / 2, tb + 0.6, min(S.gy(AXIS + s * thw, tz_mid + q * tdep / 2) for s in (-1, 1) for q in (-1, 1)) - 0.15)
f = K.flight("front", 0.0, thw, tdep / 2, tb + 0.6, 4.16)
K.balustrade(thw, tdep / 2, tb + 0.6, {"front": [(-2.5, 2.5)], "back": [(-thw, thw)]})
kp_platform("fs_terrace", thw, tdep / 2, None, tb + 0.6)
fw_ = m.world(f)
corners = [m.world((sx * thw, 0, sq * tdep / 2)) for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
m.pop()
S.FOOTPRINTS.append([(float(c[0]), float(c[2])) for c in corners])
for i, c in enumerate(corners[2:]):
    S.joint(f"fs_terrace_{i}", float(c[0]), float(c[2]), "terrace foot", y=min(S.gy(float(c[0]), float(c[2])), tb) - 0.15)
S.entry("fs_terrace_front", float(fw_[0]), float(fw_[2]), float(fw_[1]))
REPORT["halls"]["fs_terrace"] = {"frontage_m": round(2 * thw, 2), "depth_m": round(tdep, 2), "platform_m": 0.6}

# 九洲清晏殿 YM03-03: five bays, porches front and back (record 7237); its front at S01's
jz_b = [3.20, 3.20, 3.84, 3.20, 3.20]
JZ_HD = V["jz_depth"] / 2 + 0.93
Hj = hall_spec(AXIS, JZ_FRONT - JZ_HD, 0.0, jz_b, V["jz_depth"], 0.93, V["jz_pl"], V["jz_col"], 1.92, "xs", True, "doc")
Hj["fw"] = {"front": 3.84}
Hj["st"] = {"front": [0.0]}
Hj["dr"] = [1, 2, 3]
Hj["ridge"] = round(Hj["ridge"] + 0.4, 2)
draw("jz", Hj)
plaque(Hj, 1, w=2.6, h=0.95)
JZ = dict(Hj)
# the rear porch 抱厦 of 1855: three bays behind the middle, on the hall's platform carried back, its roof under the hall's eave (A for the porch; its form C)
bs_b = [3.20, 3.84, 3.20]
bs_dep = 4.16
bz = Hj["z"] - Hj["hd"] - bs_dep / 2 + 0.93 - 0.05
Hb = hall_spec(AXIS, bz, math.pi, bs_b, bs_dep - 0.4, 0.93, V["jz_pl"], 3.6, 0, "xs", True, "doc")
Hb["base"] = Hj["base"]
Hb["foot"] = min(Hb["foot"], Hj["foot"])
Hb["eave"] = round(V["jz_pl"] + 3.2 + 0.42, 2)
Hb["ridge"] = round(Hj["eave"] + 1.0, 2)  # v3: its ridge runs into the hall's back slope (勾连搭), not under the hall's eave (v2 drew it 0.4 m above its own eave)
Hb["st"] = {"front": [0.0]}
Hb["fw"] = {"front": 3.2}
Hb["dr"] = [1]
Hb["pf"] = 0
draw("jz_baosha", Hb)
plaque(Hb, 1, w=2.4, h=0.9)  # 蔚然深秀, the rear plaque (S05), here on the porch's eave (C)

# the link and 同道堂 west of 九洲清晏殿 (E1169; at their boxes, the class's form)
m.cls = "fill"
for fid, nm in (("F0569", "link"), ("F0022", "tongdao")):
    x, z, rot, hf, hd = box_local(fid)
    p = FEATS[fid]["properties"]
    nb = 3
    if fid == "F0569":  # the link runs from 同道堂's east end to the hall's west porch: its east end at the hall's platform
        east = AXIS - Hj["hf"]
        west = x - hf
        x, hf = (east + west) / 2, (east - west) / 2
    Hs = dict(hf=hf, hd=hd, base=S.gy(x, z + hd), foot=min(S.gy(x + s * hf, z + q * hd) for s in (-1, 1) for q in (-1, 1)) - 0.15, pl=0.6, e=0.4, o=0.9,
              b=[(2 * hf - 0.8) / nb] * nb, d=[2 * hd - 0.8], pf=0, pb=0, ps=0, dia=0.3, st={"front": [0.0]} if fid == "F0022" else {}, bal=0, rf="ys", rl=1, db=0,
              ju=JU["side_hall"], t="grey", te=None, bd="bm", dr=[1], rr="w", k="hall", x=x, z=z, rot=0.0, cls="fill", src="class")
    Hs["eave"] = round(0.6 + 3.3 + 0.42, 2)
    Hs["ridge"] = round(Hs["eave"] + 0.62 * (hd + 0.9), 2)
    draw(nm, Hs, kp=False)

# ============================================================ walls, galleries and gates of the axis
m.cls = "doc"
XW, XE = READ["wall_W"][0][0], READ["wall_E"][0][0]  # Round 18 v2: the walls on S01's lines (the Tongzhi survey's 25.98 m made them cut the halls S01 draws beside them: Q250)
CIN = ((XE - XW) / 2 - 0.45)  # half the court between the walls' inner faces
WALL_X = (XE - XW) / 2
z_south = ZY - Hy["hd"] + 0.3  # the walls start at 圆明园殿's back corners (the ear rooms close the gap to the hall)
z_north = rect("jz_hall")[2] - 0.0  # and run north to the line of the hall's back, where S01's range of 同道堂 and the east block close the axis
gate_z = ZY - Hy["hd"] - 6.0
for sg, tag in ((-1, "W"), (1, "E")):
    xw = XW if sg < 0 else XE
    wall_run([(xw, z_south), (xw, ZF + Hf["hd"])], 3.2, f"wall_{tag}1", gaps=[(xw, gate_z, 1.9)])
    wall_run([(xw, ZF - Hf["hd"]), (xw, z_north)], 3.2, f"wall_{tag}2")
    m.cls = "fill"
    wall_gate(xw, gate_z, sg * math.pi / 2, f"gate_{tag}")
    m.cls = "doc"
    S.kp(f"wall_{tag}_top_S", (xw, S.gy(xw, z_south) + 3.2, z_south))
# the galleries 游廊 along the courts' sides, against the walls (the leaf), from hall to hall; in the second court they turn to the hall's porch ends
GW = 2.0
for sg, tag in ((-1, "W"), (1, "E")):
    xg = (XW + 0.45 + GW / 2) if sg < 0 else (XE - 0.45 - GW / 2)
    ws = 1 if sg > 0 else -1  # the wall on the side away from the axis; a run going north (-z) has +x on its right
    ws = -ws  # north-going runs: +1 is the right of the direction (-z) = -x
    gallery_run([(xg, ZY - Hy["hd"] - 0.1), (xg, gate_z + 2.2)], ws, f"gal1_{tag}a", width=GW)
    gallery_run([(xg, gate_z - 2.2), (xg, ZF + Hf["hd"] + 0.1)], ws, f"gal1_{tag}b", width=GW)
    jz_front = Hj["z"] + Hj["hd"]
    gallery_run([(xg, ZF - Hf["hd"] - 0.1), (xg, jz_front - 1.2)], ws, f"gal2_{tag}", width=GW)
    # the turn to the hall's front porch end, along its front eave columns
    xe = AXIS + sg * (Hj["hf"] - 0.3)
    zt = jz_front - 1.2 - GW / 2
    if abs(xe - xg) > GW:
        gallery_run([(xg - sg * GW / 2, zt), (xe, zt)] if sg < 0 else [(xe, zt), (xg - sg * GW / 2, zt)], 0, f"gal2t_{tag}", width=GW)

# ============================================================ the courts: paving, the axis way, vessels and trees
m.cls = "doc"
c1 = [(XW + 0.45, ZY - Hy["hd"]), (XE - 0.45, ZY - Hy["hd"]), (XE - 0.45, ZF + Hf["hd"]), (XW + 0.45, ZF + Hf["hd"])]
c2 = [(XW + 0.45, ZF - Hf["hd"]), (XE - 0.45, ZF - Hf["hd"]), (XE - 0.45, Hj["z"] + Hj["hd"]), (XW + 0.45, Hj["z"] + Hj["hd"])]
pave(c1, "court1", dy=0.02)
pave(c2, "court2", dy=0.02)
# the raised axis way 甬路 (C)
for z0, z1 in ((ZF + Hf["hd"] + tdep, ZY - Hy["hd"] - 1.5), (Hj["z"] + Hj["hd"] + 1.5, ZF - Hf["hd"] - 1.5)):
    m.box(AXIS - 1.6, AXIS + 1.6, S.gy(AXIS, (z0 + z1) / 2) - 0.1, S.gy(AXIS, (z0 + z1) / 2) + 0.1, z0, z1, "marble", skip=("bottom",))
m.cls = "fill"
for i, (x, z) in enumerate(READ["court1_marks"]):
    xs_ = AXIS + (x - AXIS) * 1.0
    vessel(xs_, z, f"vessel_{'W' if xs_ < AXIS else 'E'}")
    S.kp(f"vessel_{'W' if xs_ < AXIS else 'E'}_top", (xs_, S.gy(xs_, z) + 2.5, z))
m.cls = "doc"
tree_spots = [(AXIS - 6.5, ZY - Hy["hd"] - 7.5), (AXIS + 6.5, ZY - Hy["hd"] - 7.5), (AXIS - 6.5, Hj["z"] + Hj["hd"] + 5.0), (AXIS + 6.5, Hj["z"] + Hj["hd"] + 5.0)]
for k, (x, z) in enumerate(tree_spots):
    tree(x, z, 5.5, 80 + k, blossom=(k % 2 == 0))

# ============================================================ the front yard and the landing on the 前湖
m.cls = "doc"
yx0, yx1 = READ["yard_W"][0][0], READ["yard_E"][0][0]
yhalf = (yx1 - yx0) / 2
shore = READ["shore_S"]
z_shore = float(np.mean([p[1] for p in shore]))
z_yard0 = ZY + Hy["hd"]
yard = [(AXIS - yhalf, z_yard0), (AXIS + yhalf, z_yard0), (AXIS + yhalf, z_shore - 2.0), (AXIS - yhalf, z_shore - 2.0)]
pave(yard, "yard", dy=0.02)
for sg, tag in ((-1, "W"), (1, "E")):
    xw = AXIS + sg * yhalf
    pts = [(xw, z_yard0 + 0.2), (xw, z_shore - 2.0)]
    K.wall(pts, 1.4, thick=0.6, cap="grey", base_h=0.4, body_mat="wallwhite")
    S.FOOTPRINTS.append([(xw - 0.4, pts[0][1]), (xw + 0.4, pts[0][1]), (xw + 0.4, pts[1][1]), (xw - 0.4, pts[1][1])])
    for k, (x, z) in enumerate(pts):
        S.joint(f"yardwall_{tag}{k}", x, z, "wall foot", y=S.gy(x, z) - 0.15)
WATER_S, WATER_N = None, None
G = json.load(open(ROOT / "site/reconstruction/generated/ground.json", encoding="utf-8"))
for b in G["bodies"]:
    if "前湖" in b["names"]:
        WATER_S = b["level"] - S.pos[1]
    if "后湖" in b["names"]:
        WATER_N = b["level"] - S.pos[1]
REPORT["water_front_y"], REPORT["water_back_y"] = round(WATER_S, 3), round(WATER_N, 3)
REPORT["landing_front_run_m"] = round(landing(AXIS, z_shore - 0.0, 0.0, 1.0, 5.0, "landing_S", WATER_S, yard_y=S.gy(AXIS, z_shore - 2.5)), 2)
# the rocks and reeds at the water's edge before the hall, outside the yard (Malone's caption of the 1744 woodcut; places C)
m.cls = "fill"
for k, sg in enumerate((-1, 1)):
    K.rocks(AXIS + sg * (yhalf + 6.0), z_shore - 1.5, 4.0, 1.6, 9, 90 + k, hmax=1.4)

# ============================================================ the back yard and the landing on the 后湖
m.cls = "doc"
shoreN = READ["shore_N"]
zN = float(np.interp(AXIS, [p[0] for p in shoreN], [p[1] for p in shoreN]))
z_back = Hb["z"] - Hb["hd"]
REPORT["back_yard_m"] = round(z_back - zN, 2)
pave([(AXIS - 3.0, zN + 2.0), (AXIS + 3.0, zN + 2.0), (AXIS + 3.0, z_back - 1.4), (AXIS - 3.0, z_back - 1.4)], "back_way", dy=0.03)
REPORT["landing_back_run_m"] = round(landing(AXIS, zN, 0.0, -1.0, 5.0, "landing_N", WATER_N, yard_y=S.gy(AXIS, zN + 2.5)), 2)

# ============================================================ the island's bridges (Round 18 v3: each its own small model, so that the panel's view frames it): stone abutments,
# a timber deck on posts, red railings, the deck at Round 10's levels. The unnamed bridge to 来青亭 (BR007) stays Round 10's plain deck: the dossier does not give it.
BRIDGES = {"BR001": ("nandaqiao", "doc", "YM03-22", "nanda-qiao", "南大桥 Nan Da Qiao"), "BR002": ("ruyiqiao", "doc", "YM03-21", "ruyi-qiao", "如意桥 Ruyi Qiao"),
           "BR005": ("zongtingqiao", "fill", "YM03-23", "zongting-qiao", "棕亭桥 Zongting Qiao")}
BRIDGE_ROWS = {
    "BR001": ("The bridge from the island's south-west corner to the shore of 正大光明 (S01, the label sure), its deck at the level Round 10 gives it: dressed-stone abutments as today's bridge rebuilt on the old ones shows (P0367, B), a timber deck on posts with red railings as the 1744 leaf paints the island's west bridge (S08 P0003, A for 1744). Its span's timber and its posts are C.",
              [["Abutments", "Dressed stone at both ends (today's rebuilding on the old ones, P0367, B)"], ["Deck", "Timber on posts, 3 m wide (Round 9's bridges), at Round 10's levels"], ["Railings", "Red posts and two rails (the 1744 leaf, A for 1744; their rhythm C)"]]),
    "BR002": ("The bridge from the island's south-east corner towards 勤政亲贤 (S01, the label sure): dressed-stone abutments as the bridge rebuilt on its surviving abutments shows (P0793, B), a timber deck with red railings as the 1744 leaf paints the bridge at the island's south-east (S08 P0003, A for 1744; the leaf draws it stepped, the deck here follows Round 10's level). Timber and posts C.",
              [["Abutments", "Dressed stone (today's rebuilding on the surviving abutments, P0793, B)"], ["Deck", "Timber on posts, 3 m wide, at Round 10's levels (the leaf's steps not drawn)"], ["Railings", "Red posts and two rails (the 1744 leaf, A for 1744; rhythm C)"]]),
    "BR005": ("棕亭桥 at the island's north-west corner (S01, the label read as a guess): a bridge with a pavilion on it, as its name and today's rebuilding show (P0368, B for the type); every size and the roof are C.",
              [["Pavilion", "Four columns and a pyramid roof on the bridge's middle (the name, P0368: C)"], ["Deck", "Timber with red railings at Round 10's levels; stone abutments (C)"]]),
}
MAIN = (m, S, K)
br_report = {}


def build_bridge(b):
    """One bridge as its own model: a frame at the deck's middle along the bridge, the same parts as v2."""
    global m, S, K
    nm, cls, rid, slug, title = BRIDGES[b["id"]]
    xs_, zs_ = [p[0] for p in b["pts"]], [p[2] for p in b["pts"]]
    dx, dz = xs_[-1] - xs_[0], zs_[-1] - zs_[0]
    Sb = Site("F0018")
    mid_x, mid_z = (xs_[0] + xs_[-1]) / 2, (zs_[0] + zs_[-1]) / 2
    Sb.pos = [round(mid_x, 3), round(min(p[1] for p in b["pts"]), 3), round(mid_z, 3)]
    Sb.rot = round(math.atan2(dx, dz), 6)
    mb = Mesh(COL)
    Sb.m = mb
    m, S, K = mb, Sb, HallKit(mb, Sb.gy)
    m.cls = cls

    pts = [(*S.to_local(p[0], p[2]), p[1] - S.pos[1]) for p in b["pts"]]
    (ax, az, ay), (bx, bz, by) = pts[0], pts[-1]
    L = math.hypot(bx - ax, bz - az)
    ux, uz = (bx - ax) / L, (bz - az) / L
    nx, nz = -uz, ux
    hw = b["width_m"] / 2
    # the deck along the Round 10 line (its y per point), planks over a beam band
    ys = [p[2] for p in pts]
    for (x0, z0, y0), (x1, z1, y1) in zip(pts[:-1], pts[1:]):
        q = [(x0 + nx * hw, y0, z0 + nz * hw), (x1 + nx * hw, y1, z1 + nz * hw), (x1 - nx * hw, y1, z1 - nz * hw), (x0 - nx * hw, y0, z0 - nz * hw)]
        m.poly(q, "timber")
        for sgn in (1, -1):
            m.poly([(x0 + sgn * nx * hw, y0, z0 + sgn * nz * hw), (x1 + sgn * nx * hw, y1, z1 + sgn * nz * hw), (x1 + sgn * nx * hw, y1 - 0.45, z1 + sgn * nz * hw), (x0 + sgn * nx * hw, y0 - 0.45, z0 + sgn * nz * hw)], "rail")
        m.poly([(x0 + nx * hw, y0 - 0.45, z0 + nz * hw), (x1 + nx * hw, y1 - 0.45, z1 + nz * hw), (x1 - nx * hw, y1 - 0.45, z1 - nz * hw), (x0 - nx * hw, y0 - 0.45, z0 - nz * hw)], "underside")
    # railings: posts every 1.6 m, a top rail and a mid rail, both sides
    n_post = max(2, int(L / 1.6) + 1)
    for k in range(n_post):
        t = k / (n_post - 1)
        x, z = ax + (bx - ax) * t, az + (bz - az) * t
        y = float(np.interp(t * L, [math.hypot(p[0] - ax, p[1] - az) for p in pts], ys))
        for sgn in (1, -1):
            px_, pz_ = x + sgn * nx * (hw - 0.08), z + sgn * nz * (hw - 0.08)
            m.box(px_ - 0.07, px_ + 0.07, y, y + 1.05, pz_ - 0.07, pz_ + 0.07, "rail")
    for sgn in (1, -1):
        for hh, th in ((1.0, 0.07), (0.55, 0.04)):
            for (x0, z0, y0), (x1, z1, y1) in zip(pts[:-1], pts[1:]):
                o0 = (x0 + sgn * nx * (hw - 0.08), z0 + sgn * nz * (hw - 0.08))
                o1 = (x1 + sgn * nx * (hw - 0.08), z1 + sgn * nz * (hw - 0.08))
                m.poly([(o0[0], y0 + hh - th, o0[1]), (o1[0], y1 + hh - th, o1[1]), (o1[0], y1 + hh + th, o1[1]), (o0[0], y0 + hh + th, o0[1])], "rail")
    # posts under the deck where it is over water (the bed from the walk surface), every 3 m
    n_leg = max(1, int(L / 3.0))
    for k in range(1, n_leg):
        t = k / n_leg
        x, z = ax + (bx - ax) * t, az + (bz - az) * t
        y = float(np.interp(t * L, [math.hypot(p[0] - ax, p[1] - az) for p in pts], ys))
        g = S.gy(x, z)
        if g < y - 0.6:
            for sgn in (1, -1):
                px_, pz_ = x + sgn * nx * (hw - 0.3), z + sgn * nz * (hw - 0.3)
                m.prism([(px_ + 0.14 * math.cos(a), pz_ + 0.14 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 7)[:-1]], g - 0.2, y - 0.45, "timber", top=False)
    # the abutments: dressed stone from the bed to the deck at each end, 1.6 m along the bridge, flared walls (P0367)
    for end, (ex, ez, ey), sgn_u in (("a", pts[0], 1), ("b", pts[-1], -1)):
        m.push(ex, 0, ez, math.atan2(ux * sgn_u, uz * sgn_u))
        g0 = min(S.gy(*[float(v) for v in (m.world((s, 0, q))[0], m.world((s, 0, q))[2])]) for s in (-hw - 0.5, hw + 0.5) for q in (-0.5, 0.0, 1.6))
        m.box(-hw - 0.5, hw + 0.5, g0 - 0.2, ey - 0.02, -0.6, 1.6, "quay", skip=("bottom",))
        m.box(-hw - 0.55, hw + 0.55, ey - 0.2, ey + 0.02, -0.65, 1.65, "coping", skip=("bottom",))
        m.pop()
        w_ = m.world((0, 0, 0))
        S.joint(f"{nm}_{end}", float(ex), float(ez), "bridge end", y=min(ey, S.gy(float(ex), float(ez))) - 0.05 if S.gy(float(ex), float(ez)) <= ey + 0.3 else S.gy(float(ex), float(ez)) - 0.05)
        S.kp(f"{nm}_abut_{end}_L", m.world((ex - nx * (hw + 0.5) * sgn_u, ey, ez - nz * (hw + 0.5) * sgn_u)) if False else (ex - nx * (hw + 0.5), ey, ez - nz * (hw + 0.5)))
        S.kp(f"{nm}_abut_{end}_R", (ex + nx * (hw + 0.5), ey, ez + nz * (hw + 0.5)))
    # 棕亭桥: the pavilion on the bridge's middle (P0368; C)
    if b["id"] == "BR005":
        mx_, mz_ = (ax + bx) / 2, (az + bz) / 2
        ymid = float(np.interp(L / 2, [math.hypot(p[0] - ax, p[1] - az) for p in pts], ys))
        m.push(mx_, 0, mz_, math.atan2(ux, uz))
        for s_ in (-1, 1):
            for q_ in (-1, 1):
                m.prism([(s_ * 1.6 + 0.13 * math.cos(a), q_ * 1.9 + 0.13 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 7)[:-1]], ymid, ymid + 2.9, "lacquer", top=False)
        m.box(-1.75, 1.75, ymid + 2.6, ymid + 2.95, -2.05, 2.05, "band")
        K.pyramid(2.6, 2.9, ymid + 2.7, ymid + 4.6, tile="grey")
        m.pop()
    br_report[b["id"]] = {"name": nm, "length_m": round(L, 1), "deck_y": [round(min(ys), 2), round(max(ys), 2)], "grade_class": cls}
    n_b = m.write_glb(HERE.parent / f"{rid}-{slug}" / "model.glb", f"{rid} {title}", extras={"frame": "x across the bridge, y up, z along it from its first end; origin at the deck's middle"})
    Pb = {k: P[k] for k in ("bridges", "zongting") if k in P and (k != "zongting" or b["id"] == "BR005")}
    line, rows = BRIDGE_ROWS[b["id"]]
    sm = {"id": rid, "aliases": [], "name": title, "glb": "model.glb", "position": S.pos, "rotationY": S.rot, "line": line, "rows": rows,
          "caption": {"frontage_m": round(math.hypot(dx, dz), 1), "depth_m": b["width_m"], "top_m": round(DATUM_M + S.pos[1] + max(p[1] for p in b["pts"]) - S.pos[1] + (4.6 if b["id"] == "BR005" else 1.05), 2),
                      "assumed": True, "confidence": "C"},  # top_m: the railing's top (the pavilion's at 棕亭桥), so the panel's line reads a height, not NaN
          "bridges": [b["id"]], "hides": [], "tris": m.count(), "glb_bytes": n_b, "made_by": "models/YM03-jiuzhou-qingyan/jiuzhouqingyan.py"}
    S.write(HERE.parent / f"{rid}-{slug}", rid, [rid], Pb, "origin at the deck's middle at its lowest point; x across, y up, z along the bridge (scripts/model_site.py)", sm)
    br_report[b["id"]]["model"] = f"models/{rid}-{slug}/"
    br_report[b["id"]]["triangles"] = m.count()
    m, S, K = MAIN


for b in STRUCT["bridges"]:
    if b["id"] in BRIDGES:
        (HERE.parent / f"{BRIDGES[b['id']][2]}-{BRIDGES[b['id']][3]}").mkdir(exist_ok=True)
        build_bridge(b)
REPORT["bridges"] = br_report

# ============================================================ key points along the axis (what the leaf shows) and the report's measures
REPORT["court1_depth_m"] = round((ZY - (Hy["hd"] - Hy["e"])) - (ZF + (Hf["hd"] - Hf["e"])), 2)
REPORT["court2_depth_m"] = round((ZF - (Hf["hd"] - Hf["e"])) - (Hj["z"] + (Hj["hd"] - Hj["e"])), 2)
REPORT["court_width_m"] = round(2 * CIN, 2)
REPORT["s01_walls_apart_m"] = round(READ["wall_E"][0][0] - READ["wall_W"][0][0] - 0.9, 2)
REPORT["s01_fs_frontage_m"] = round(rect("fs_hall")[1] - rect("fs_hall")[0], 2)
REPORT["s01_ymy_frontage_m"] = round(rect("ymy_hall")[1] - rect("ymy_hall")[0], 2)
REPORT["s01_jz_frontage_m"] = round(rect("jz_hall")[1] - rect("jz_hall")[0], 2)
REPORT["triangles"] = m.count()

# ============================================================ write
n_bytes = m.write_glb(HERE / "model.glb", "YM03 九洲清晏 Jiuzhou Qingyan", extras={"frame": "x east along the front, y up, z south; origin at 圆明园殿's box front middle"})
aliases = ["YM03-01", "YM03-02", "YM03-03", "YM03-13", "YM03-N02"]
summary = {
    "id": "YM03",
    "aliases": aliases,
    "name": "九洲清晏 Jiuzhou Qingyan",
    "glb": "model.glb",
    "position": S.pos,
    "rotationY": S.rot,
    "line": "The central axis as it stood from the rebuilding of 1837 to 1860: the plan S01 gives the layout and the positions, the slip of 1855 the front hall's bays, depth, column and platform (A), the Tongzhi survey the courts (B), the leaf of 1744 the colours, the roofs and the galleries. 奉三无私殿's and 九洲清晏殿's own figures are on the Yangshi Lei sheets (E1161-E1171, not seen): their bays' widths, depths and heights are 圆明园殿's carried over (C).",
    "rows": [
        ["Layout", "The axis as S01 draws it (re-read in Round 18 in plan pixels, B): front yard, 圆明园殿, first court, 奉三无私殿 and its terrace, second court, 九洲清晏殿; the plan's names here are of 1873 (Q36), the axis halls kept theirs"],
        ["圆明园殿", "Five bays 4.16 + 4 × 3.84 m, 7.04 m deep with porches of 1.92 m front and back, columns 3.84 m, platform 0.70 m with a 0.93 m edge (the slip of 1855, S310 rec. 11195, A); doors on the 金柱 line since 1837, open porches (B); rolled 硬山 after 1837 (record 11195's reading of the gables, B; the 1744 leaf drew a 歇山, Q100); Kangxi's plaque 圆明园 (S05, A); ear rooms at both ends (S01, C)"],
        ["Front yard", "Walled on two sides from the hall to the 前湖 (S01, B) with a stone landing (Round 9's YMC-023; its steps C); rocks at the water's edge either side (Malone's caption of the 1744 woodcut, places C)"],
        ["First court", "As S01 draws it, 22.6 m between the walls' inner faces; 34.5 m between the halls' eave columns, where the Tongzhi survey writes 33.92 m and a width of 25.98 m (样006-3, B; Q250); covered galleries with white walls and pierced windows along both sides (the 1744 leaf, B; where they run C); a gate in each side wall (C); two bronze vessels where S01 draws two marks (C); flowering trees (the leaf, places C)"],
        ["奉三无私殿", "Seven bays (S05, A) with porches front and back (record 7271, B), wall to wall as S01 draws it (23.3 m, B); the bays' widths, depth, column 4.16 m and platform 0.8 m (C); rolled 歇山, grey (the 1744 leaf, B); the front terrace as S01 draws it (0.6 m, C)"],
        ["Second court", "As S01 places the halls (21 m between the eave columns; the Tongzhi survey writes 18.27 m, Q250); galleries turning to 九洲清晏殿's porch ends (C)"],
        ["九洲清晏殿", "Five bays with porches front and back (record 7237, A; S05 says seven for the 1780s, Q101); widths to S01's 18.1 m, depth and heights C; rolled 歇山, the island's largest roof (the 1744 leaf, B); the three-bay rear porch 抱厦 of 1855 (records 7237, 10881, A; its form C); the plaques 九洲清晏 and 蔚然深秀 (S05, A)"],
        ["West annex", "The link and 同道堂 west of the hall, joined to it in the rebuilding of 1837 (E1169); at their boxes on S01, their form the class's (C)"],
        ["Back and the lake", "A paved way from the rear porch to a stone landing on the 后湖 (Round 9's YMC-031; the steps C)"],
        ["Bridges", "南大桥, 如意桥 and 棕亭桥 are models of their own (YM03-22, YM03-21, YM03-23), drawn by this model's generator"],
        ["Assumed", "Every elevation but 圆明园殿's (no picture of the rebuilt halls survives), the ear rooms, the gates, the link and 同道堂, the vessels, the brackets, the bridges' timber: the hall kit's classes and the Qing manual's typology (C, the pale tint with conf=1)"],
    ],
    "caption": {"frontage_m": round(XE - XW + 0.9, 1), "depth_m": round((z_shore) - zN, 1), "eave_m": REPORT["halls"]["jz"]["eave_m"], "ridge_m": REPORT["halls"]["jz"]["ridge_m"], "assumed": True, "confidence": "C"},
    "hides": [],
    "tris": m.count(),
    "glb_bytes": n_bytes,
}
S.write(HERE, "YM03", aliases, P, "origin at the front middle of 圆明园殿's box F0018 at its ground; x east along the front, y up, z south (scripts/model_site.py)", summary)
json.dump(REPORT, open(HERE / "report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"YM03: {m.count()} triangles, GLB {n_bytes / 1e6:.2f} MB; axis {AXIS:.2f} (spread {AXIS_SPREAD:.2f} m); courts {REPORT['court1_depth_m']} / {REPORT['court2_depth_m']} m")
