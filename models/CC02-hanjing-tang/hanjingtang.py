#!/usr/bin/env python3
"""含经堂 Hanjingtang (CC02), the palace compound on the central island of 长春园 Changchun Yuan, the seventh detailed model and the first of a Chinese compound (Round 17).

  uv run python models/CC02-hanjing-tang/hanjingtang.py

The whole walled compound and its forecourt, as the plan S01 draws them and the ruin shows them: the forecourt with its three glazed archways 琉璃坊楔 and the crossing
stone paths (S05 j83:4a; S940 p.360); the terrace the compound stands on, its curved retaining edge and the flights up it (S01; P0403, P0505, P0815); the five-bay gate
宫门 (S05); the 含经堂 court with its screen wall 影壁, the side halls and the two ranges 梵香楼 and 霞翥楼 (S940 p.360); 含经堂, seven bays, double-eaved 歇山 (S940 p.360,
S361); the rockery and the galleries 墨刻游廊 with the 淳化阁帖 stones (S05 j83:4b; S940 p.361); 淳化轩, seven by three bays on its terrace with two flights (S940 p.361;
S01; P0404); 蕴真斋, seven bays with porches front and back (S940 p.360; S01); the north gate; the halls of the east and west courts at their boxes; the walls.

Method (docs/METHOD.md, 'a compound from the kit and its evidence'): every hall is the hall kit of Round 11 (scripts/hall_parts.py, the Python copy of kit3d.js) from the
hall's numbers in data/kit_1860.json, then adapted to what the dossier, the plan and the ruin say. The layout is read on S01 (plan_readings.csv, plan pixels; placed by
the fit in use, research/georef/) and checked against the Yangshi Lei plan 长春园淳化轩 as S940 prints it (figs. 5, 6; research-only, a reading aid for the layout).
Writes, beside this file: model.glb, params.json, keypoints.json, joints.json, summary.json (models/README.md).
Frame (scripts/model_site.py): origin at the front middle of 含经堂's box F0310, at that box's ground; x east along the front, y up, z south.
Grades: what a source states for this compound (its plan, its bays, its roofs as the texts give them, its platforms on the ruin) is `doc`; the forms carried in from the
hall classes (the halls of the side courts, the brackets, the galleries' details, the archways' faces, the 垂花 side flights) are `fill` (assumed, C).
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
from scene1860 import to_xz  # noqa: E402

P = {
    "terrace_h": (2.1, "S01;S70;S966", "C", "the compound's terrace over the forecourt: S01 draws its edge; P0403, P0505 (2013) and P0815 (2007) show a dressed brick retaining wall with a three-part flight; measured on those three by a sweep of the model (tools/plate_overlay.py fit, rms at the object summed over the three: 1.8 m 1.77, 2.1 m 1.73, 2.4 m 1.82, 2.7 m 2.00, 3.0 m 2.23; d); v1's 1.4 m fitted 1.52-1.71 m rms; the dig's figure is in S990, not seen"),
    "yard_w": (13.5, "S70;S966", "C", "the projecting flight before the gate: P0403, P0505, P0815 about 12-13 m wide between sloping cheeks, a central flight of about 5.6 m and two narrower ones (reader A); S01 draws a yard 24 m wide there (Q244): the ruin's outline wins"),
    "outer_wall_h": (3.6, "S01", "C", "the outer wall 宫墙 above the terrace: S01 draws it, no source gives a height; a garden palace wall of the class, C"),
    "court_wall_h": (3.0, "S01", "C", "the court walls inside: S01; height C"),
    "fore_wall_h": (2.6, "S01;S940", "C", "the forecourt's walls on three sides, with the archways in them (S01; S940 p.360); height C"),
    "gate_pl": (0.6, "S01;S05", "C", "the gate's platform on the terrace; S05 '宫門五楹南嚮'; the bays and the frontage are the box's (S01 19.1 m)"),
    "hjt_bays": (7, "S05;S940", "B", "含經堂七楹 (S05 j83:4a); S940 p.360 面阔七间; S01 draws nine cells: seven bays and a porch at each end, a porch all round 周围廊 (C)"),
    "hjt_roof": ("double-eaved 歇山 with a ridge", "S940;S361", "B", "S940 p.360 重檐歇山顶大殿; S361 v3 p.244 'a seven-bay double-eaved glazed hall' (E0057)"),
    "hjt_tiles": ("yellow glazed", "S361", "C", "glazed: S361 (E0057, B); yellow is C: the twin 乐寿堂 is yellow and Q143 is open (S990's tile finds would settle it)"),
    "hjt_pl": (1.5, "S70", "C", "the hall's platform over the court: P0402 shows a first level about 0.8 m high with a central flight about 4.3 m wide and a second flight behind it to a higher level (reader A, d); the second level C"),
    "hjt_terrace": ("22 x 6 m, 0.8 m, flight 4.3 m", "S70", "C", "the front terrace 月台 of 含经堂: its height and its flight from P0402 (d); its plan C"),
    "hjt_porch": (2.0, "S01", "C", "the porch all round: the end cells of S01's nine, about 2 m"),
    "col_grand": (4.17, "S112", "C", "the column of a grand hall: research/typology/params.json grand_hall as re-read in Round 11 against the measured halls (Q182)"),
    "hjt_ridge": (11.6, "S101", "C", "the ridge above the court: the 举架 of a grand hall (0.5, 0.6, 0.75, 0.9; S101) over the upper roof's half-span of about 4.7 m, on the lower eave, the skirt and the upper wall"),
    "chx_bays": ("7 x 3", "S940", "B", "淳化轩面阔七间，进深三间 (S940 p.360); front and back porches C"),
    "chx_roof": ("rolled 歇山, glazed", "S940", "B", "S940 gives 卷棚歇山 (p.360) and 琉璃歇山 (p.361): read together, a glazed rolled hip-and-gable roof (Q151, Q173); yellow C as for 含经堂"),
    "chx_pl": (1.2, "S70", "C", "the platform: P0404 shows six or seven risers in the flights of the displayed platform (d)"),
    "chx_ridge": (13.0, "S101", "C", "the 举架 of a grand hall over the half-span of the 21 m deep hall (box F0311, S01)"),
    "chx_terrace": ("17 x 5.5 m, two flights at its front ends", "S01;S70", "B", "S01 crop a: the terrace in front of 淳化轩 with two small flights at its ends; P0404: two flights on the south face of the displayed platform"),
    "yz_bays": ("7, porches front and back", "S940;S01", "B", "蕴真斋面阔七间，前后带抱厦 (S940 p.360); S01 draws a cross: the body 32.7 x 10.2 m, the back porch 14.5 x 6.4 m, the front arm 14.5 x 15 m"),
    "yz_pl": (0.9, "S70", "C", "P0405 and P0801: brick-faced platforms stepping down to a sunk court (d)"),
    "yz_roof": ("rolled 歇山, grey", "S01", "C", "no source gives it; grey rolled tile is the rule of the gardens (research/typology/halls.md)"),
    "fx_storeys": (2, "S05", "C", "梵香楼 and 霞翥楼: two storeys read from the name 楼 alone (S05 j83:4b); their ⊐ plan from S01 (plan_readings.csv), mirrored as S940 p.360 says"),
    "gal_w": (3.0, "S01", "C", "the galleries 墨刻游廊: S01's double line, about 3 m over the roof; the wall on the outer side holds the stones (S05 j83:4b '東西廊廡壁間嵌御定淳化閣帖石刻'; S940 p.361)"),
    "screen_wh": ("5.5 x 1.2 x 4.0 m", "S01;S940", "C", "the screen wall: S01 5.4 m by 2 m; S940 p.360; height C"),
    "pailou_h": (7.5, "S05", "C", "the three glazed archways 琉璃坊楔 (S05 j83:4a); their footings were dug (S990); the form is the class of the standing glazed archways, C"),
    "syx_hall": ("11.1 x 7.2 m on a platform 11.9 x 8.3 m", "S940", "B", "三友轩 measured on the ruin (S940 p.364): the box F0318 (14.5 x 13.3 m) is larger (Q108); the model draws the measured size at the box's middle"),
    "stage": ("two storeys, double eaves", "S361;S144", "C", "乐奏钧天 (CC02-13): a two-storey stage (S940 p.360), double eaves (S43 per S361); about 16 m square with its cellar (E0064); drawn at the box's 8.7 m (S01) as a two-storey pavilion, C"),
}
V = {k: v[0] for k, v in P.items()}

COL = {
    "lacquer": "#8a2f22", "lacquer_dark": "#532218", "wall": "#8e8a84", "plaster": "#d9cfbe", "glass_lattice": "#2b3137", "sill": "#7d7973",
    "band": "#2e6a6c", "bracket": "#3b7b70", "bandred": "#7d2c20", "platform": "#b7b0a1", "coping": "#d2ccbe", "step": "#c8c1b1", "marble": "#e9e5dc",
    "underside": "#4b453d", "fascia": "#3a2a22", "wallred": "#9b3d2c", "rock": "#b9ae98", "pave": "#bdb6a6", "deck": "#b4ad9d", "gold": "#c9a245", "stele": "#2a2a2c",
    "trunk": "#5a4634", "leaf_plum": "#5d7f3e", "leaf_pine": "#2f4d33", "bamboo": "#6f8f45",
    "tile_grey": "#5f6469", "tile_yellow": "#d6a31c", "tile_green": "#3f8f6a", "ridge_grey": "#4a4e52", "ridge_yellow": "#a77f16", "ridge_green": "#316f53",
}

S = Site("F0310")
m = Mesh(COL)
S.m = m
KIT = json.load(open(ROOT / "site/reconstruction/data/kit_1860.json", encoding="utf-8"))["halls"]
FEATS = S.F


# ------------------------------------------------------------ the plan readings, into the frame
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


# the axis: the gate's flight, the screen and the north gate (read on S01); the model is drawn on it, the side courts mirrored where S940 says they answer each other
_ax = [np.mean([p[0] for p in READ[n]]) for n in ("gate_flight", "screen", "north_gate")]
AXIS = float(np.mean(_ax))
AXIS_SPREAD = float(max(_ax) - min(_ax))

# the terrace: its level over the forecourt, and the ground function the kit stands on
DECK = READ["deck"]
# Round 17 v2: the gate's projection as the ruin shows it (yard_w), not S01's 24 m: its four corners moved to the axis +- yard_w / 2
_ax0 = float(np.mean([np.mean([p[0] for p in READ[n]]) for n in ("gate_flight", "screen", "north_gate")]))
for i, (x, z) in enumerate(DECK):
    if 10 <= abs(x - _ax0) <= 14 and z > READ["wall_S_W"][0][1] + 5:
        DECK[i] = (_ax0 + math.copysign(V["yard_w"] / 2, x - _ax0), z)
from shapely.geometry import Point, Polygon  # noqa: E402

DECK_POLY = Polygon(DECK)
_gate_foot = (AXIS, rect("gate_flight")[3] + 0.5)
FORE_Y = S.gy(*_gate_foot)
DECK_Y = round(FORE_Y + V["terrace_h"], 2)


def ground(x, z):
    return DECK_Y if DECK_POLY.buffer(-0.05).contains(Point(x, z)) else S.gy(x, z)


K = HallKit(m, ground)
REPORT = {"halls": {}, "deck_y": DECK_Y, "forecourt_y": round(FORE_Y, 2), "axis_x": round(AXIS, 2), "axis_spread_m": round(AXIS_SPREAD, 2)}


def compass(dx, dz):
    return ("N" if dz < 0 else "S") + ("W" if dx < 0 else "E")


# ------------------------------------------------------------ a hall from its box and its kit entry, adapted
def box_local(fid):
    c, u, hf, hd, base = box_frame(FEATS, fid)
    x, z = S.to_local(*c)
    x2, z2 = S.to_local(*(c + u))
    fx, fz = x2 - x, z2 - z
    return x, z, math.atan2(fx, fz), hf, hd


def spec_of(fid, **over):
    p = FEATS[fid]["properties"]
    e = KIT[fid]
    x, z, rot, hf, hd = box_local(fid)
    st = {}
    for side in e.get("st", ["front"]):
        st[side] = [0.0] + [o for o in e.get("so", {}).get(side, [])]
    H = dict(hf=hf, hd=hd, base=DECK_Y, foot=DECK_Y - 0.15, pl=p["platform_m"], eave=p["eave_m"], ridge=p["ridge_m"], e=e["e"], o=e["o"], b=e["b"], d=e["d"],
             pf=e["pf"], pb=e["pb"], ps=e["ps"], dia=e["dia"], st=st, bal=e.get("bal", 0), rf=e["rf"], rl=e["rl"], db=e["db"], ju=e["ju"], t=e["t"], te=e.get("te"),
             bd=e["bd"], dr=e["dr"], rr=e["rr"], k=e["k"], x=x, z=z, rot=rot, cls="doc" if e.get("fig") else "fill", src="dossier" if e.get("fig") else "class")
    H.update(over)
    return H


def bays(n, total, central_k=1.12, end_k=0.92):
    w = [1.0] * n
    w[n // 2] = central_k
    if n >= 5:
        w[0] = w[-1] = end_k
    s = sum(w)
    return [round(total * v / s, 3) for v in w]


def compass(dx, dz):
    return ("N" if dz < 0 else "S") + ("W" if dx < 0 else "E")


def kp_platform(name, hf, hd, y_foot, y_top, anchor=True):
    """The key points of a platform drawn in the current frame: its corners at the foot (where it meets the court) and at the top, named by compass."""
    c0 = m.world((0, 0, 0))
    for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        w = m.world((sx * hf, 0, sq * hd))
        tag = compass(w[0] - c0[0], w[2] - c0[2])
        S.kp(f"{name}_pl_foot_{tag}", (w[0], y_foot, w[2]), anchor=anchor)
        S.kp(f"{name}_pl_top_{tag}", (w[0], y_top, w[2]))


def kp_flight(name, side, off, width, hf, hd, y_top, foot_local):
    """A flight's corners: its top at the platform's edge and its foot, left and right as seen from in front of the flight (facing the platform)."""
    d = {"front": (0, 1), "back": (0, -1), "right": (1, 0), "left": (-1, 0)}[side]
    for lr, lat in (("L", -1), ("R", 1)):
        # seen from in front of the flight, looking back at the platform: the viewer's left is the flight's +lateral for a front flight
        a = lat * width / 2 * (1 if side in ("front", "left") else -1)
        if d[0] == 0:
            top, foot = (off + a, y_top, d[1] * hd), (off + a, foot_local[1], foot_local[2])
        else:
            top, foot = (d[0] * hf, y_top, off + a), (foot_local[0], foot_local[1], off + a)
        S.kp(f"{name}_fl_{side}_{lr}_top", m.world(top))
        S.kp(f"{name}_fl_{side}_{lr}_foot", m.world(foot), anchor=True)


def draw(name, H):
    m.cls = H["cls"]
    m.push(H["x"], 0.0, H["z"], H["rot"])
    feet = K.hall(H)
    corners = [m.world((sx * H["hf"], 0, sq * H["hd"])) for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    fw = {k: m.world(v) for k, v in feet.items()}
    kp_platform(name, H["hf"], H["hd"], H["base"], H["base"] + H["pl"])
    for k, f in feet.items():
        side, off = k.split("_")
        wdt = H.get("fw", {}).get(side, max(H["b"][len(H["b"]) // 2], 2.4) if side in ("front", "back") else 2.6)
        if float(off) == 0.0:
            kp_flight(name, side, 0.0, wdt, H["hf"], H["hd"], H["base"] + H["pl"], f)
    m.pop()
    S.FOOTPRINTS.append([(float(c[0]), float(c[2])) for c in corners])
    for k, f in fw.items():
        S.entry(f"{name}_{k}", float(f[0]), float(f[2]), float(f[1]))
    REPORT["halls"][name] = {"frontage_m": round(2 * H["hf"], 2), "depth_m": round(2 * H["hd"], 2), "platform_m": H["pl"], "eave_m": H["eave"], "ridge_m": H["ridge"], "roof": H["rf"],
                             "rolled": int(bool(H["rl"])), "double": int(bool(H.get("db"))), "tiles": H["t"], "bays": len(H["b"]), "flights": len(feet), "grade_class": H["cls"]}
    return fw


def heights(pl, col, bracket, rise):
    """eave and ridge above the base from the platform, the column, the band and the roof's rise."""
    eave = pl + col + (0.85 if bracket else 0.42)
    return round(eave, 2), round(eave + rise, 2)


# ============================================================ the forecourt
m.cls = "doc"
fx0, fx1 = READ["forecourt"][0][0], READ["forecourt"][2][0]
fz1 = (READ["forecourt"][1][1] + READ["forecourt"][2][1]) / 2
fore_south = fz1
# the crossing stone paths 石板甬路十字交叉 and four lawns (S940 p.360): the paths as paving a little above the ground, the lawns left as the ground
cross_z = (READ["forecourt"][0][1] + fz1) / 2 + 6.0
m.cls = "doc"
for (a0, a1, b0, b1) in ((AXIS - 3.0, AXIS + 3.0, READ["deck"][-1][1] + 1.0, fz1 - 0.5), (fx0 + 0.6, fx1 - 0.6, cross_z - 2.5, cross_z + 2.5)):
    xs_, zs_ = np.linspace(a0, a1, max(2, int((a1 - a0) / 6) + 1)), np.linspace(b0, b1, max(2, int((b1 - b0) / 6) + 1))
    for i in range(len(xs_) - 1):
        for j in range(len(zs_) - 1):
            q = [(xs_[i], zs_[j]), (xs_[i + 1], zs_[j]), (xs_[i + 1], zs_[j + 1]), (xs_[i], zs_[j + 1])]
            m.poly([(x, S.gy(x, z) + 0.06, z) for x, z in q], "pave")
S.joint("fore_path_S", AXIS, fz1 - 1.0, "paving", y=S.gy(AXIS, fz1 - 1.0) + 0.0)
# the forecourt's walls, with the archways in them
fwall = READ["forecourt"]
m.cls = "doc"
pailou_gaps = {}
for fid in ("F0306", "F0307", "F0308"):
    x, z, rot, hf, hd = box_local(fid)
    pailou_gaps[fid] = (x, z, rot, hf, hd)


def wall_with_gaps(pts, h, gaps, thick=0.9, cap="grey", name=None, on_deck=False, ytop=None):
    """A wall along pts, interrupted where a gap's box (x, z, half width along the wall) crosses it."""
    runs = []
    for (ax, az), (bx, bz) in zip(pts[:-1], pts[1:]):
        L = math.hypot(bx - ax, bz - az)
        ux, uz = (bx - ax) / L, (bz - az) / L
        cuts = []
        for gx, gz, hw in gaps:
            t = (gx - ax) * ux + (gz - az) * uz
            d = abs(-(gx - ax) * uz + (gz - az) * ux)
            if -hw < t < L + hw and d < 4.0:
                cuts.append((t - hw, t + hw))
        cur = 0.0
        for c0, c1 in sorted(cuts):
            if c0 > cur + 0.3:
                runs.append([(ax + ux * cur, az + uz * cur), (ax + ux * c0, az + uz * c0)])
            cur = max(cur, c1)
        if L > cur + 0.3:
            runs.append([(ax + ux * cur, az + uz * cur), (bx, bz)])
    from shapely.geometry import LineString as _LS
    for i, r in enumerate(runs):
        K.wall(r, h, thick=thick, cap=cap, ytop=ytop)
        S.FOOTPRINTS.append([(float(x), float(z)) for x, z in list(_LS(r).buffer(thick / 2 + 0.1, cap_style="flat").exterior.coords)[:-1]])  # the ways go round a wall, through its gates
        for k, (x, z) in enumerate(r if name else []):
            if DECK_POLY.buffer(-0.05).contains(Point(x, z)):  # a wall's end on the terrace's floor: a joint with the deck, measured here, not with the ground of Round 10
                REPORT.setdefault("deck_joints", []).append({"name": f"{name}{i}_{k}", "gap_m": round((ground(x, z) - 0.15) - DECK_Y, 2)})
            else:
                S.joint(f"{name}{i}_{k}", x, z, "wall foot", y=ground(x, z) - 0.15)
    return runs


gaps_fore = [(x, z, hf + 0.2) for (x, z, rot, hf, hd) in pailou_gaps.values()]
wall_with_gaps(fwall, V["fore_wall_h"], gaps_fore, thick=0.8, name="forewall")
# the three archways: their boxes (S01), the class's form (C)
m.cls = "fill"
for i, (fid, (x, z, rot, hf, hd)) in enumerate(pailou_gaps.items()):
    m.push(x, 0, z, rot)
    K.pailou_glazed(2 * hf, max(1.6, 2 * hd * 0.55), V["pailou_h"])
    for sg in (1, -1):
        w = m.world((0, 0, sg * 1.6))
        S.entry(f"pailou_{fid}_{'out' if sg > 0 else 'in'}", float(w[0]), float(w[2]))
    w = m.world((0, 0, 0))
    S.entry(f"pailou_{fid}_mid", float(w[0]), float(w[2]))  # the middle passage: a way runs through
    tagp = {"F0306": "W", "F0307": "S", "F0308": "E"}[fid]
    c0 = m.world((0, 0, 0))
    for sx in (-1, 1):
        w = m.world((sx * hf, 0, 0))
        S.joint(f"pailou_{fid}_{sx:+d}", float(w[0]), float(w[2]), "archway foot", y=S.gy(float(w[0]), float(w[2])) - 0.15)
        for sq in (-1, 1):
            w = m.world((sx * (hf + 0.2), 0, sq * (max(1.6, 2 * hd * 0.55) / 2 + 0.2)))
            S.kp(f"pailou_{tagp}_base_{compass(w[0] - c0[0], w[2] - c0[2])}", (w[0], S.gy(float(w[0]), float(w[2])), w[2]), anchor=True)
    m.pop()

# ============================================================ the terrace
m.cls = "doc"
# its floor: the courts' paving, one level, and the retaining face all round (down to the ground outside)
m.flat(DECK, DECK_Y, "deck")
S.skirt(DECK, DECK_Y, "platform")
for i, (x, z) in enumerate(DECK):
    S.JOINTS.append([f"terrace_{i}", x, S.gy(x, z) - 0.15, z, "terrace foot"])
S.deck("terrace", DECK_Y, DECK)
S.CLEAR.append([tuple(p) for p in DECK])  # the planting keeps off the paved courts (scripts/greens1860.py: `clear`); the ways may cross them
S.CLEAR.append([tuple(READ["forecourt"][1]), tuple(READ["forecourt"][2])] + [tuple(p) for p in DECK[2:]])  # and off the forecourt up to the terrace's curved edge: four lawns where the yurts were pitched, S940 p.360 (no tree there, C)
for nm, (x, z) in (("terr_W_end", DECK[-1]), ("terr_E_end", DECK[2]), ("terr_yard_SW", DECK[-6]), ("terr_yard_SE", DECK[-7]), ("terr_yard_NW", DECK[-5]), ("terr_yard_NE", DECK[-8])):
    S.kp(f"{nm}_top", (x, DECK_Y, z))
    S.kp(f"{nm}_foot", (x, S.gy(x, z), z), anchor=True)
# the coping along the curved south edge (the face the forecourt sees)
south = DECK[3:] + [DECK[0]] if False else DECK[2:]
for (ax, az), (bx, bz) in zip(south[:-1], south[1:]):
    L = math.hypot(bx - ax, bz - az)
    ux, uz = (bx - ax) / L, (bz - az) / L
    nx, nz = -uz * 0.35, ux * 0.35
    m.poly([(ax - nx, DECK_Y + 0.02, az - nz), (bx - nx, DECK_Y + 0.02, bz - nz), (bx + nx, DECK_Y + 0.02, bz + nz), (ax + nx, DECK_Y + 0.02, az + nz)], "coping")


def flight_free(cx, cz, ux, uz, width, y_top, name, cls="doc", treads=0.3):
    """A flight down from the terrace's edge: its top at (cx, cz) on the edge, running out along (ux, uz) to the ground; side slabs 垂带."""
    m.cls = cls
    rot = math.atan2(ux, uz)
    m.push(cx, 0, cz, rot)
    g_at = lambda q: ground(*[float(v) for v in (m.world((0, 0, q))[0], m.world((0, 0, q))[2])])
    h = y_top - S.gy(*[float(v) for v in (m.world((0, 0, 3.0))[0], m.world((0, 0, 3.0))[2])])
    n = max(1, round(h / 0.15))
    run = n * treads
    gF = S.gy(*[float(v) for v in (m.world((0, 0, run))[0], m.world((0, 0, run))[2])])
    rise = (y_top - gF) / n
    low = min(gF, min(S.gy(*[float(v) for v in (m.world((s, 0, q))[0], m.world((s, 0, q))[2])]) for s in (-width / 2, width / 2) for q in (0.1, run))) - 0.15
    for k in range(n):
        m.box(-width / 2, width / 2, low, y_top - (k + 1) * rise, k * treads - 0.05, (k + 1) * treads, "step")
    for s0, s1 in ((-width / 2 - 0.45, -width / 2), (width / 2, width / 2 + 0.45)):
        m.poly([(s0, y_top + 0.05, -0.05), (s1, y_top + 0.05, -0.05), (s1, gF + 0.1, run), (s0, gF + 0.1, run)], "step")
        for s in (s0, s1):
            m.poly([(s, y_top + 0.05, -0.05), (s, gF + 0.1, run), (s, low, run), (s, low, -0.05)], "step")
        m.poly([(s0, gF + 0.1, run), (s1, gF + 0.1, run), (s1, low, run), (s0, low, run)], "step")
    foot = m.world((0, 0, run + 0.15))
    for lr, s_ in (("L", -width / 2), ("R", width / 2)):
        S.kp(f"{name}_{lr}_top", m.world((s_, y_top, 0.0)))
        w_ = m.world((s_, 0, run))
        S.kp(f"{name}_{lr}_foot", (w_[0], gF, w_[2]), anchor=True)
    for s in (-width / 2, width / 2):
        w = m.world((s, 0, run))
        S.JOINTS.append([f"{name}_foot_{'L' if s < 0 else 'R'}", float(w[0]), low, float(w[2]), "flight foot"])
    m.pop()
    S.entry(f"{name}_foot", float(foot[0]), float(foot[2]))
    S.entry(f"{name}_top", float(cx), float(cz), y_top)
    return run


gx0, gx1, gz0, gz1 = rect("gate_flight")
_yard_front = max(p[1] for p in DECK if abs(p[0] - AXIS) < 8)
REPORT["gate_flight_run_m"] = flight_free(AXIS, _yard_front, 0.0, 1.0, 5.6, DECK_Y, "gate_flight")
for sg in (-1, 1):  # the two narrower flights either side of the central one (P0403, P0505)
    flight_free(AXIS + sg * (2.8 + 0.45 + 0.45 + 1.15), _yard_front, 0.0, 1.0, 2.3, DECK_Y, f"gate_flight_{'W' if sg < 0 else 'E'}")
for nm, sgn in (("side_flight_W", -1), ("side_flight_E", 1)):
    (ax, az), (bx, bz) = READ[nm]
    cx, cz = (ax + bx) / 2, (az + bz) / 2
    L = math.hypot(bx - ax, bz - az)
    ux, uz = (bx - ax) / L, (bz - az) / L
    nx, nz = (-uz, ux) if (-uz * 0 + ux) > 0 else (uz, -ux)
    if nz < 0:
        nx, nz = -nx, -nz
    # the flight's top on the curved edge: the nearest edge point
    from shapely.geometry import LineString  # noqa: E402
    edge = LineString(DECK[2:] if False else DECK)
    pp = edge.interpolate(edge.project(Point(cx, cz)))
    flight_free(pp.x, pp.y, nx, nz, min(L, 9.0), DECK_Y, nm, cls="fill")

# ============================================================ the walls of the compound
m.cls = "doc"
OUTER_TOP = V["outer_wall_h"]
gate = box_local("F0309")
north = rect("north_gate")
wall_with_gaps(READ["wall_W"], OUTER_TOP, [], name="wallW", ytop=DECK_Y + OUTER_TOP)
wall_with_gaps(READ["wall_E"], OUTER_TOP, [], name="wallE", ytop=DECK_Y + OUTER_TOP)
wall_with_gaps(READ["wall_N"], OUTER_TOP, [((north[0] + north[1]) / 2, READ["wall_N"][0][1], 2.6)], name="wallN", ytop=DECK_Y + OUTER_TOP)
wall_with_gaps(READ["wall_S_W"], OUTER_TOP, [], name="wallSW", ytop=DECK_Y + OUTER_TOP)
wall_with_gaps(READ["wall_S_E"], OUTER_TOP, [], name="wallSE", ytop=DECK_Y + OUTER_TOP)
wall_with_gaps(READ["court_W"], V["court_wall_h"], [], name="courtW", on_deck=True)
wall_with_gaps(READ["court_E"], V["court_wall_h"], [], name="courtE", on_deck=True)
cw = READ["cross_W"]
wall_with_gaps([cw[0], cw[1]], V["court_wall_h"], [], name="crossW_a", on_deck=True)
wall_with_gaps([cw[2], cw[3]], V["court_wall_h"], [], name="crossW_b", on_deck=True)
ce = READ["cross_E"]
wall_with_gaps([ce[0], ce[1]], V["court_wall_h"], [], name="crossE_a", on_deck=True)
wall_with_gaps([ce[2], ce[3]], V["court_wall_h"], [], name="crossE_b", on_deck=True)

# ============================================================ the gate 宫门
H = spec_of("F0309", pl=V["gate_pl"], cls="doc")
H["eave"], H["ridge"] = heights(H["pl"], 3.6, True, 3.0)
H["bd"] = "br"
draw("gate", H)
# the north gate 北宫门 (S940 p.360), a small gate in the north wall, with a flight down outside (C)
m.cls = "fill"
nx0, nx1, nz0, nz1 = north
ncx = AXIS
nz_wall = READ["wall_N"][0][1]
NG = dict(hf=2.6, hd=2.4, base=DECK_Y, foot=min(S.gy(ncx, nz_wall - 2.4), DECK_Y) - 0.15, pl=0.15, e=0.3, o=0.8, b=[4.0], d=[4.2], pf=0, pb=0, ps=0, dia=0.34, st={"front": [0.0]}, bal=0,
          rf="ys", rl=1, db=0, ju=JU["gate_hall"], t="grey", bd="bm", dr=[0], rr="d", k="gate", x=ncx, z=nz_wall, rot=0.0, cls="fill", src="class")
NG["eave"], NG["ridge"] = heights(0.15, 3.2, False, 1.8)
NG["st"] = {}
draw("north_gate", NG)
# its platform's outer half stands over the ground outside the wall: a deck the ways lie on, and the flight down from its north edge
S.deck("north_gate", DECK_Y + 0.15, [(ncx - 2.6, nz_wall - 2.4), (ncx + 2.6, nz_wall - 2.4), (ncx + 2.6, nz_wall + 2.4), (ncx - 2.6, nz_wall + 2.4)])
REPORT["north_flight_run_m"] = flight_free(ncx, nz_wall - 2.4, 0.0, -1.0, 3.2, DECK_Y + 0.15, "north_flight", cls="fill")

# ============================================================ the 含经堂 court
# the screen wall
m.cls = "doc"
sx0, sx1, sz0, sz1 = rect("screen")
gs_ = K.screen(AXIS, (sz0 + sz1) / 2, 5.5, 1.2, 4.0, tile="grey", base=0.4)
for tag, sx_ in (("W", -1), ("E", 1)):
    S.kp(f"screen_foot_{tag}", (AXIS + sx_ * 2.9, gs_, (sz0 + sz1) / 2 + 0.75), anchor=True)
    S.kp(f"screen_base_top_{tag}", (AXIS + sx_ * 2.9, gs_ + 0.4, (sz0 + sz1) / 2 + 0.75))
    S.kp(f"screen_top_{tag}", (AXIS + sx_ * 2.75, gs_ + 4.0 - 0.5, (sz0 + sz1) / 2 + 0.6))
# 含经堂: seven bays and a porch all round, double eaves, glazed
H = spec_of("F0310", cls="doc")
CS = H["hf"] - H["e"]
H["b"] = [V["hjt_porch"]] + bays(7, 2 * CS - 2 * V["hjt_porch"]) + [V["hjt_porch"]]
H["pf"] = H["pb"] = H["ps"] = V["hjt_porch"]
CQ = H["hd"] - H["e"]
H["d"] = [V["hjt_porch"], 2 * CQ - 2 * V["hjt_porch"], V["hjt_porch"]]
H.update(pl=V["hjt_pl"], db=1, rf="xs", rl=0, t="yellow", te=None, bd="br", bal=1, dr=[3, 4, 5], rr="d", per_bay=2)
H["eave"] = round(V["hjt_pl"] + V["col_grand"] + 0.85, 2)
H["ridge"] = V["hjt_ridge"]
H["upper"] = 0.47
H["st"] = {"front": [0.0], "back": [0.0]}
H["fw"] = {"front": 4.8, "back": 4.8}
draw("hanjingtang", H)
# its front terrace 月台, 0.8 m, with a flight of 4.3 m (P0402); the hall's own flight climbs from it
m.cls = "doc"
m.push(H["x"], 0, H["z"], H["rot"])
tq0, tdep, thw = H["hd"], 6.0, 11.0
m.push(0, 0, tq0 + tdep / 2)
K.platform(thw, tdep / 2, DECK_Y + 0.8, DECK_Y - 0.15)
f = K.flight("front", 0.0, thw, tdep / 2, DECK_Y + 0.8, 4.3)
kp_platform("hjt_terrace", thw, tdep / 2, DECK_Y, DECK_Y + 0.8)
kp_flight("hjt_terrace", "front", 0.0, 4.3, thw, tdep / 2, DECK_Y + 0.8, f)
fw_ = m.world(f)
corners = [m.world((sx * thw, 0, sq * tdep / 2)) for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
m.pop()
m.pop()
S.FOOTPRINTS.append([(float(c[0]), float(c[2])) for c in corners])
S.entry("hjt_terrace_front", float(fw_[0]), float(fw_[2]), float(fw_[1]))
# the side halls: the west one at its box (F0317, labelled 涵光室, Q242), the east one mirrored (S940 p.360: east and west alike)
Hw = spec_of("F0317", cls="fill", pl=0.6)
Hw["eave"], Hw["ridge"] = heights(0.6, 3.4, False, 2.6)
draw("peidian_W", Hw)
He = dict(Hw, x=2 * AXIS - Hw["x"], rot=-Hw["rot"])
draw("peidian_E", He)
# 梵香楼 and 霞翥楼: a ⊐ of two-storey ranges each side, open to the court (S01), mirrored
m.cls = "fill"


def range_hall(name, x0, x1, z0, z1, face, mirror=False):
    """A two-storey range over the rectangle, its front to `face` ('E', 'W', 'N', 'S')."""
    if mirror:
        x0, x1 = 2 * AXIS - x1, 2 * AXIS - x0
        face = {"E": "W", "W": "E"}.get(face, face)
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    rot = {"S": 0.0, "N": math.pi, "E": math.pi / 2, "W": -math.pi / 2}[face]
    along_x = face in ("N", "S")
    hf, hd = ((x1 - x0) / 2, (z1 - z0) / 2) if along_x else ((z1 - z0) / 2, (x1 - x0) / 2)
    n = max(1, round(2 * hf / 3.6))
    Hr = dict(hf=hf, hd=hd, base=DECK_Y, foot=DECK_Y - 0.15, pl=0.7, e=0.35, o=1.1, b=[(2 * hf - 0.7) / n] * n, d=[(2 * hd - 0.7) * 0.25, (2 * hd - 0.7) * 0.75],
              pf=(2 * hd - 0.7) * 0.25, pb=0, ps=0, dia=0.3, st={"front": [0.0]}, bal=0, rf="xs", rl=1, db=0, ju=JU["storeyed_hall"], t="grey", bd="bm",
              dr=[n // 2], rr="w", k="hall", x=cx, z=cz, rot=rot, cls="fill", src="class", mid=4.3)
    Hr["eave"], Hr["ridge"] = 7.9, round(7.9 + 0.55 * (hd + 1.1), 2)
    draw(name, Hr)


for mir, tag in ((False, "fanxiang"), (True, "xiazhu")):
    x0, x1, z0, z1 = rect("fx_range_W")
    range_hall(f"{tag}_range", x0, x1, z0, z1, "E", mir)
    x0, x1, z0, z1 = rect("fx_wing_NW")
    range_hall(f"{tag}_wingN", x0 + 0.4, x1, z0, z1, "S", mir)
    x0, x1, z0, z1 = rect("fx_wing_SW")
    range_hall(f"{tag}_wingS", x0 + 0.4, x1, z0, z1, "N", mir)

# ============================================================ the galleries 墨刻游廊 and the rockery
m.cls = "doc"
for nm, side in (("gal_W", 1), ("gal_E", -1)):
    pts = READ[nm]
    x = (pts[0][0] + pts[1][0]) / 2
    x = AXIS + (x - AXIS) if nm == "gal_W" else AXIS + (x - AXIS)
    run = [(x, pts[0][1] - 0.3), (x, pts[1][1] + 0.3)]
    # the wall on the outer side (away from the axis): the run goes north (-z); its left is -x
    ws = 1 if x < AXIS else -1
    ws = -ws if run[1][1] < run[0][1] else ws
    K.gallery(run, V["gal_w"], lambda a, b: DECK_Y, eave=3.0, ridge=4.3, wall_side=ws, stones=True)  # +1 the right of the run (hall_parts.gallery): the wall on the side away from the axis
    S.FOOTPRINTS.append([(x - 1.6, run[0][1]), (x + 1.6, run[0][1]), (x + 1.6, run[1][1]), (x - 1.6, run[1][1])])
m.cls = "fill"
for nm, seed, h in (("rock_axis_W", 17, 2.6), ("rock_axis_E", 18, 2.6), ("rock_W", 19, 2.0)):
    x0, x1, z0, z1 = rect(nm)
    if nm == "rock_axis_W":
        x1 = min(x1, AXIS - 2.0)
    if nm == "rock_axis_E":
        x0 = max(x0, AXIS + 2.0)
    K.rocks((x0 + x1) / 2, (z0 + z1) / 2, (x1 - x0) / 2, (z1 - z0) / 2, int((x1 - x0) * (z1 - z0) / 6) + 6, seed, hmax=h)
for i, (x, z) in enumerate(READ["rock_syx"]):
    K.rocks(x, z, 3.0, 2.5, 7, 40 + i, hmax=2.2)

# ============================================================ 淳化轩 and its terrace
H = spec_of("F0311", cls="doc")
CS, CQ = H["hf"] - H["e"], H["hd"] - H["e"]
H["b"] = bays(7, 2 * CS)
H["pf"] = H["pb"] = 2.2
H["ps"] = 0
H["d"] = [2.2] + [round((2 * CQ - 4.4) / 3, 3)] * 3 + [2.2]
H.update(pl=V["chx_pl"], db=0, rf="xs", rl=1, t="yellow", te=None, bd="br", bal=0, dr=[3], rr="d", per_bay=2)
H["eave"] = round(V["chx_pl"] + V["col_grand"] + 0.85, 2)
H["ridge"] = V["chx_ridge"]
H["st"] = {"back": [0.0]}
draw("chunhuaxuan", H)
CHX = dict(H)
# the terrace 月台: a platform at the hall's floor, a step lower; two flights at its front ends; a balustrade
x0, x1, z0, z1 = rect("chx_terrace")
hx, hz = (x1 - x0) / 2, (z1 - z0) / 2
chx_back = box_local("F0311")
m.cls = "doc"
m.push(AXIS, 0, z0 + hz, 0.0)
plTop = DECK_Y + V["chx_pl"] - 0.15
K.platform(hx, hz + 0.3, plTop, DECK_Y - 0.15)
feet = {}
for off in (-hx + 4.0, hx - 4.0):  # v2: the flights stand 2.5-3 m in from the terrace's ends (P0404, reader B)
    f = K.flight("front", off, hx, hz + 0.3, plTop, 2.6)
    feet[f"{off:+.1f}"] = m.world(f)
K.balustrade(hx, hz + 0.3, plTop, {"front": [(-hx + 2.3, -hx + 5.7), (hx - 5.7, hx - 2.3)], "back": [(-hx, hx)]})
kp_platform("chx_terrace", hx, hz + 0.3, DECK_Y, plTop)
for off_, tag_ in ((-hx + 4.0, "W"), (hx - 4.0, "E")):
    for lr, a_ in (("L", -1.3), ("R", 1.3)):
        S.kp(f"chx_terrace_fl_{tag_}_{lr}_top", m.world((off_ + a_, plTop, hz + 0.3)))
        S.kp(f"chx_terrace_fl_{tag_}_{lr}_foot", m.world((off_ + a_, DECK_Y, hz + 0.3 + round((plTop - DECK_Y) / 0.15) * 0.3)), anchor=True)
corners = [m.world((sx * hx, 0, sq * (hz + 0.3))) for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
m.pop()
S.FOOTPRINTS.append([(float(c[0]), float(c[2])) for c in corners])
for k, f in feet.items():
    S.entry(f"chx_terrace_{k}", float(f[0]), float(f[2]), float(f[1]))
REPORT["halls"]["chunhuaxuan_terrace"] = {"frontage_m": round(2 * hx, 2), "depth_m": round(2 * hz + 0.6, 2), "platform_m": round(plTop - DECK_Y, 2), "flights": len(feet)}

# ============================================================ 蕴真斋: the body, the back porch, the front porch on its terrace
x0, x1, z0, z1 = rect("yz_bar")
bx0, bx1, bz0, bz1 = rect("yz_back")
fx0_, fx1_, fz0_, fz1_ = rect("yz_front")
hw = (x1 - x0) / 2
col_y = 3.6
Hb = dict(hf=hw, hd=(z1 - z0) / 2, base=DECK_Y, foot=DECK_Y - 0.15, pl=V["yz_pl"], e=0.6, o=1.3, b=bays(7, 2 * hw - 1.2), d=[1.8, (z1 - z0) - 1.2 - 3.6, 1.8],
          pf=1.8, pb=1.8, ps=0, dia=0.4, st={}, bal=0, rf="xs", rl=1, db=0, ju=JU["main_hall"], t="grey", bd="bm", dr=[3], rr="d", k="hall",
          x=AXIS, z=(z0 + z1) / 2, rot=0.0, cls="doc", src="dossier")
Hb["eave"], Hb["ridge"] = heights(V["yz_pl"], col_y, False, 0.62 * ((z1 - z0) / 2 + 0.7))
draw("yunzhenzhai", Hb)
half_p = (bx1 - bx0) / 2
for nm, za, zb, face in (("yunzhenzhai_back", bz0, z0 + 0.6, math.pi), ("yunzhenzhai_front", z1 - 0.6, z1 + 3.0, 0.0)):
    depth = zb - za
    Hp = dict(hf=half_p, hd=depth / 2, base=DECK_Y, foot=DECK_Y - 0.15, pl=V["yz_pl"], e=0.4, o=1.0, b=bays(3, 2 * half_p - 0.8), d=[depth - 0.8],
              pf=0, pb=0, ps=0, dia=0.36, st={"front": [0.0]}, bal=0, rf="xs", rl=1, db=0, ju=JU["side_hall"], t="grey", bd="bm", dr=[1], rr="w", k="hall",
              x=AXIS, z=(za + zb) / 2, rot=face, cls="doc", src="dossier", side_wall=True, fw={"front": 2.6 if nm.endswith("back") else 4.0})  # the back flight about 2.6 m (P0405, v1 fit)
    Hp["eave"], Hp["ridge"] = Hb["eave"] - 0.2, round(Hb["eave"] - 0.2 + 0.6 * (half_p + 0.8), 2)
    Hp["eave"] = round(Hp["eave"], 2)
    draw(nm, Hp)
# the front arm: a terrace 月台 a step below the hall's floor, out to the end S01 draws
m.cls = "doc"
tz0, tz1 = z1 + 3.0, fz1_
m.push(AXIS, 0, (tz0 + tz1) / 2, 0.0)
th = (tz1 - tz0) / 2
plT = DECK_Y + V["yz_pl"] - 0.15
K.platform(half_p, th, plT, DECK_Y - 0.15)
kp_platform("yunzhenzhai_terrace", half_p, th, DECK_Y, plT)
f = K.flight("front", 0.0, half_p, th, plT, 4.0)
fw_ = m.world(f)
corners = [m.world((sx * half_p, 0, sq * th)) for sx, sq in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
m.pop()
S.FOOTPRINTS.append([(float(c[0]), float(c[2])) for c in corners])
S.entry("yunzhenzhai_terrace_front", float(fw_[0]), float(fw_[2]), float(fw_[1]))

# ============================================================ the halls of the side courts at their boxes (the kit's numbers, adapted where a source speaks)
SIDE = {
    "F0315": dict(pl=0.7, b=bays(5, 13.1)),  # P0410: 0.6-0.75 m by its risers, the column markers about 2.4 m apart (reader C); five bays (S940 p.360)                    # 渊映斋 CC02-07: five bays, 歇山 (S940 p.360): the kit's dossier entry
    "F0640": dict(pl=0.9),  # P0410: about 0.9 m, six risers (reader C)                    # AX011: north of 渊映斋, where S940 puts the dressing room 扮戏房 (five bays): C
    "F0321": dict(),                    # 神心妙达 CC02-14: five bays with a front porch (S940 p.360)
    "F1002": dict(),                    # B0542
    "F1028": dict(),                    # B0583
    "F0452": dict(),                    # N01, labelled 静莲斋 (S01); by S940's order 理心楼 (Q243)
    "F0991": dict(),                    # B0521
    "F0975": dict(),                    # B0501
    "F0976": dict(),                    # B0503
    "F1011": dict(),                    # B0555
    "F0990": dict(),                    # B0520
}
for fid, over in SIDE.items():
    Hs = spec_of(fid, **over)
    # inside the outer wall: a box the plan readers drew across it is drawn inside it (C)
    wx0, wx1 = READ["wall_W"][0][0] + 0.8, READ["wall_E"][0][0] - 0.8
    wz0 = READ["wall_N"][0][1] + 0.8
    cxs = [Hs["x"] + sx * (abs(math.cos(Hs["rot"])) * Hs["hf"] + abs(math.sin(Hs["rot"])) * Hs["hd"]) for sx in (-1, 1)]
    czs = [Hs["z"] + sz * (abs(math.sin(Hs["rot"])) * Hs["hf"] + abs(math.cos(Hs["rot"])) * Hs["hd"]) for sz in (-1, 1)]
    if cxs[0] < wx0:
        Hs["x"] += wx0 - cxs[0]
    if cxs[1] > wx1:
        Hs["x"] -= cxs[1] - wx1
    if czs[0] < wz0:
        Hs["z"] += wz0 - czs[0]
    draw(f"side_{fid}", Hs)
# 三友轩 CC02-10: the measured hall on its measured platform at the box's middle (S940 p.364)
Hs = spec_of("F0318", cls="doc")
Hs.update(hf=11.9 / 2, hd=8.3 / 2, e=0.4, b=bays(3, 11.1), d=[7.2], pf=0, pb=0, ps=0, pl=0.6, dia=0.3)
Hs["eave"], Hs["ridge"] = heights(0.6, 3.2, False, 2.2)
Hs["st"] = {"front": [0.0]}
draw("sanyouxuan", Hs)
SYX = dict(Hs)
# the stage 乐奏钧天 CC02-13: a two-storey pavilion on a high stage platform, double eaves (C), facing north to 神心妙达
Hs = spec_of("F0320", cls="fill")
Hs.update(pl=1.2, mid=4.8, rf="xs", rl=0, b=bays(3, 2 * (Hs["hf"] - Hs["e"])), d=[2 * (Hs["hd"] - Hs["e"])], pf=0, pb=0, ps=0, dia=0.36, db=0)
Hs["eave"], Hs["ridge"] = 8.6, 11.2
Hs["st"] = {"back": [0.0]}
draw("stage", Hs)

# ============================================================ the court trees the texts name, on the terrace's floor (the planting of Round 12 keeps off the terrace)
def tree(x, z, kind, h, seed):
    """A tree in the model: a trunk and a crown of a few faceted layers; plum 梅 and pine 松 by their habit, bamboo 竹 a clump of culms. Placement C."""
    rng = np.random.default_rng(seed)
    g = ground(x, z)
    if kind == "bamboo":
        for k in range(9):
            a, r = rng.uniform(0, 2 * math.pi), rng.uniform(0, 0.7)
            bx, bz = x + r * math.cos(a), z + r * math.sin(a)
            hh = h * rng.uniform(0.75, 1.0)
            m.prism([(bx + 0.04 * math.cos(t), bz + 0.04 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 5)[:-1]], g - 0.1, g + hh, "bamboo", top=False)
            m.lathe([(0.0, g + hh * 0.55), (0.45, g + hh * 0.75), (0.25, g + hh * 0.95), (0.0, g + hh + 0.2)], 5, "bamboo", cx=bx, cz=bz)
        return
    tr = 0.12 if kind == "plum" else 0.2
    m.prism([(x + tr * math.cos(t), z + tr * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 7)[:-1]], g - 0.1, g + h * (0.45 if kind == "plum" else 0.55), "trunk", top=False)
    mat = "leaf_plum" if kind == "plum" else "leaf_pine"
    if kind == "plum":
        m.lathe([(0.0, g + h * 0.4), (h * 0.33, g + h * 0.6), (h * 0.28, g + h * 0.85), (0.0, g + h)], 7, mat, cx=x, cz=z)
    else:
        for k, (y0, r) in enumerate(((0.5, 0.42), (0.68, 0.34), (0.84, 0.24))):
            m.lathe([(0.0, g + h * y0), (h * r, g + h * (y0 + 0.04)), (h * r * 0.7, g + h * (y0 + 0.12)), (0.0, g + h * (y0 + 0.16))], 7, mat, cx=x + rng.uniform(-0.3, 0.3), cz=z + rng.uniform(-0.3, 0.3))


m.cls = "doc"
# 淳化轩's court: plum trees 庭梅 (E0068, a poem of 1792 on the plums of 淳化轩's court); four, either side of the axis before the terrace (places C)
tz = rect("chx_terrace")[3] + 7.0
for k, dx in enumerate((-12.0, -7.5, 7.5, 12.0)):
    tree(AXIS + dx, tz + (k % 2) * 2.5, "plum", 4.2, 60 + k)
# 三友轩: pine, bamboo and plum outside it (S940 p.364, citing the 活计档); behind it, to the north, where the plan leaves room (B0555 stands 2 m before its front; places C)
sx_, sz_ = SYX["x"], SYX["z"] - SYX["hd"] - 3.0
tree(sx_ - 4.0, sz_, "pine", 7.5, 70)
tree(sx_, sz_ + 1.0, "bamboo", 5.0, 71)
tree(sx_ + 4.0, sz_, "plum", 4.0, 72)
from shapely.geometry import Polygon as _P
_fps = [_P(fp).buffer(0) for fp in S.FOOTPRINTS[:]]
REPORT["trees_in_a_footprint"] = sum(1 for (x, z) in [(AXIS + dx, tz + (k % 2) * 2.5) for k, dx in enumerate((-12.0, -7.5, 7.5, 12.0))] + [(sx_ - 4.0, sz_), (sx_, sz_ + 1.0), (sx_ + 4.0, sz_)] if any(f.contains(Point(x, z)) for f in _fps))
REPORT["court_trees"] = {"plum": 5, "pine": 1, "bamboo": 1, "basis": "E0068 (淳化轩's court plums), S940 p.364 (pine, bamboo and plum outside 三友轩); places C"}

# the covered walk from 三友轩 to 淳化轩's west end: 三友轩 is 淳化轩's west side hall 西顺山殿 (S940 p.364); P0406 shows column bases along its east side (reader B); C
m.cls = "fill"
wx0 = SYX["x"] + SYX["hf"]
wx1 = CHX["x"] - CHX["hf"]
if wx1 - wx0 > 1.5:
    K.gallery([(wx0, SYX["z"]), (wx1, SYX["z"])], 2.6, lambda a, b: DECK_Y + 0.3, eave=2.9, ridge=4.1)
    S.FOOTPRINTS.append([(wx0, SYX["z"] - 1.4), (wx1, SYX["z"] - 1.4), (wx1, SYX["z"] + 1.4), (wx0, SYX["z"] + 1.4)])
    REPORT["sanyou_walk_m"] = round(wx1 - wx0, 1)

# ============================================================ key points (for tools/plate_overlay.py): what a ruin photograph shows of the platforms
def kp_box(prefix, name):
    pass


for name, h in REPORT["halls"].items():
    pass

summary_rows = []
REPORT["triangles"] = m.count()

# ============================================================ write
n_bytes = m.write_glb(HERE / "model.glb", "CC02 含经堂 Hanjingtang", extras={"frame": "x east along the front, y up, z south; origin at 含经堂's box front middle"})
aliases = ["CC02-01", "CC02-02", "CC02-03", "CC02-04", "CC02-05", "CC02-06", "CC02-07", "CC02-08", "CC02-09", "CC02-10", "CC02-11", "CC02-13", "CC02-14",
           "CC02-AX011", "CC02-B0501", "CC02-B0503", "CC02-B0520", "CC02-B0521", "CC02-B0542", "CC02-B0555", "CC02-B0583", "CC02-N01", "CC02-N05"]
summary = {
    "id": "CC02",
    "aliases": aliases,
    "name": "含经堂 Hanjingtang",
    "glb": "model.glb",
    "position": S.pos,
    "rotationY": S.rot,
    "line": "The walled compound as the plan S01 draws it, on the terrace the dig shows, with every hall drawn by the hall kit from its numbers and adapted to what the texts and the ruin say: 含经堂 seven bays, double-eaved, glazed (S940, S361); 淳化轩 seven by three bays on its terrace (S940, P0404); 蕴真斋 with its porches (S940, S01). No picture of any hall standing survives: every elevation is the kit's (C); the halls of the side courts are their class's (assumed).",
    "rows": [
        ["Layout", "The walled compound and its forecourt as the plan S01 draws them (re-read in Round 17, B), checked against the Yangshi Lei plans 长春园淳化轩 as S940 prints them (figs. 5, 6)"],
        ["Forecourt", "Walls on three sides with the three glazed archways 琉璃坊楔 (S05; their form the class's, C), crossing stone paths and four lawns where the yurts stood (S940 p.360)"],
        ["Terrace", f"The compound stands {V['terrace_h']} m above the forecourt: measured on the ruin photographs P0403, P0505, P0815 (C); the curved edge from S01; the gate's projection {V['yard_w']} m wide with three flights as the ruin shows it (S01 draws 24 m, Q244)"],
        ["Gate 宫门", "Five bays (S05 '宫門五楹南嚮'), at its box on S01; doors, bracket band and roof from the hall kit (C)"],
        ["含经堂", "Seven bays and a porch all round (S05; S940 p.360; S01's nine cells), double-eaved 歇山 (S940, S361), yellow glazed (glazed: S361; the colour C, Q143); a front terrace of 0.8 m with a 4.3 m flight before a 1.5 m platform (P0402, C)"],
        ["Court of 含经堂", "The screen wall 影壁 on the axis (S01, S940; its 0.4 m base from P0402), side halls east and west (S940), the two-storey ⊐ ranges 梵香楼 (west) and 霞翥楼 (east) on S01's plan (storeys from the names, C)"],
        ["Galleries and rockery", "The galleries 墨刻游廊 with the 淳化阁帖 stones set in their outer walls (S05 j83:4b; S940 p.361); the rockery between 含经堂 and 淳化轩 (S01, S940; its rocks placed C); plum trees in the court (E0068; places C)"],
        ["淳化轩", "Seven by three bays (S940 p.360), rolled 歇山, glazed (S940 pp.360-361; colour C, Q151); its terrace 17 x 5.5 m with two flights 2.5-3 m in from its ends (S01; P0404)"],
        ["蕴真斋", "Seven bays with porches front and back (S940 p.360; S01's cross), its front arm a terrace; rolled grey 歇山 (C)"],
        ["Side courts", "Every hall inside the wall at its box, drawn from its class by the hall kit (assumed); 三友轩 at its measured 11.1 x 7.2 m on 11.9 x 8.3 m (S940 p.364) with pine, bamboo and plum (S940); 渊映斋 five bays and the dressing room's platform from P0410; the stage 乐奏钧天 as a two-storey pavilion (C)"],
        ["Assumed", "Every elevation (no picture of any hall standing survives), the halls of the side courts, the archways' faces, the north gate, the flights on the curves: from the hall kit's classes and the Qing manual's typology (C, the pale tint with conf=1)"],
    ],
    "caption": {"frontage_m": round(READ["wall_E"][0][0] - READ["wall_W"][0][0], 1), "depth_m": round(fore_south - READ["wall_N"][0][1], 1), "eave_m": REPORT["halls"]["hanjingtang"]["eave_m"],
                "ridge_m": REPORT["halls"]["hanjingtang"]["ridge_m"], "assumed": True, "confidence": "C"},
    "hides": [],
    "tris": m.count(),
    "glb_bytes": n_bytes,
}
S.write(HERE, "CC02", aliases, P, "origin at the front middle of 含经堂's box F0310 at its ground; x east along the front, y up, z south (scripts/model_site.py)", summary)
json.dump(REPORT, open(HERE / "report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"CC02: {m.count()} triangles, {sum(1 for k in m.prims if k.endswith('~fill'))} fill materials, GLB {n_bytes / 1e6:.2f} MB; deck {DECK_Y} (forecourt {FORE_Y:.2f}), axis {AXIS:.2f} (spread {AXIS_SPREAD:.2f} m)")
