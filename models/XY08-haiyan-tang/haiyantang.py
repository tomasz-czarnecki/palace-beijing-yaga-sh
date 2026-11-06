#!/usr/bin/env python3
"""海晏堂 Haiyantang (XY08), the second detailed model (Round 14): the west block of eleven bays on two storeys with its end pavilions and its attic; the two diagonal stairs that embrace
the pool of the twelve hours 十二时辰水法 (XY08-02) with its twelve seated figures, the shell and the vase fountain; the great pedestals at the court's corners; the link; the water building
of thirteen bays (蓄水楼, XY08-N01 and XY08-01) with the reservoir 锡海 on its roof between the two raised wheel-house tiers; the east block with the zig-zag stairs (XY08-N02, N03).
Plain geometry, one GLB (scripts/model_mesh.py) with every figure in params.json; the method is the pilot's (models/XY01-xieqiqu/README.md).

  uv run python models/XY08-haiyan-tang/haiyantang.py

Writes, beside this file: model.glb, params.json, keypoints.json, joints.json, summary.json (models/README.md).
Frame: origin on the line through the ruin-placed pool (XY08-M42) and reservoir (XY08-M40), level with the middle of the west block's box (XY08-M37), at that box's ground;
x along the west front (south), y up, z out of the west front (west). The east end is at z about -91.
Grades: a form shown on a plate or a photograph of this building is `doc`; the faces no picture shows (the stairs' outer walls, the reservoir, the west face of the west wheel house,
the inner faces) are `fill` (assumed, C). Every figure is C unless params.json says otherwise.
Ground: every part stands on the walk surface of Round 10 (tools/check_ground.py NewGround): the court levels are read, and walls run down below the lowest ground under them.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))
from check_ground import NewGround  # noqa: E402
from model_mesh import Mesh  # noqa: E402
from model_parts import Parts  # noqa: E402
from scene1860 import DATUM_M, to_xz  # noqa: E402

# ---------------------------------------------------------------- figures (value, source, grade, note); the iteration log in README.md says what moved and why
P = {
    # the west block
    "W": (47.2, "S01;S71", "C", "frontage of the west block: plan S01 225 px at the local 4.80 px/m (b); plate 10's eleven bays read on it (c)"),
    "D": (11.0, "S01;S71", "C", "depth of the two-storey range: S01 draws a stepped outline 9.0 m deep behind front parts reaching 22.7 m; plate 11 draws the north end narrow. 11 m, between"),
    "bays": (11, "S310;S109", "B", "eleven bays on both levels, the west front (S310, B)"),
    "pav_w": (10.2, "S71", "C", "the end pavilions under their own square roofs, two bays: plate 10, 294 px at its module"),
    "cen_w": (12.9, "S71", "C", "the centre three bays (window, door, window) proud of the range, with the attic above: plate 10"),
    "cen_proj": (1.0, "S71", "C", "how far the centre stands forward: plate 10 draws free columns at the door, the bays nearly flush"),
    "H1": (7.2, "S71", "C", "the upper floor and the terrace at the head of the stairs: plate 10's module, 208 px"),
    "H2": (13.2, "S71", "C", "the main cornice's top: plate 10's module, 380 px; plates 11 and 13 read 9.3 and 8.6 m at their own tie (Q70)"),
    "ridge_mid": (15.7, "S71", "C", "the long middle roof's ridge: plate 10, 453 px"),
    "ridge_pav": (16.5, "S71", "C", "the end pavilions' short ridges stand higher than the middle ridge: plate 10, 23 px of 2400"),
    "attic_h": (2.6, "S71", "C", "the attic over the centre bays, above the cornice: plate 10"),
    "ped_apex": (17.5, "S71", "C", "top of the attic's broken pediment where its crest starts: plate 10, 123 px above the cornice at its module (4.3 m)"),
    "wing_w": (6.4, "S01", "C", "the single-storey wing rooms with flat roofs and balustrades before the end pavilions (S310: 'flat-roof rooms below with stone balustrades'): plan block B0154, 6.4 m N-S"),
    "wing_d": (6.0, "S01;S71", "C", "how far the wings come forward: plan B0154 is 13.3 m W-E, half of it inside the range; plate 10's balconies are shallow"),
    "wing_x": (20.4, "S71;S871", "C", "the wings' middle from the axis: plate 10 and Ohlmer's P0774 put the balconies' outer corners at the block's ends (v3: fit 3.1-3.5 m off with the plan's place); S01's block B0154 stands 3.3 m in from the end (Q226)"),
    # the terrace, the stairs, the pool
    "terr_w": (7.54, "S01;S310", "C", "the landing before the upper door: the roof of the lower centre's west-going bay (S310), the plan's H hall 7.54 m N-S (x 9776-9831, y 1092-1128)"),
    "terr_z": (11.35, "S01", "C", "its front, the H hall's front on the plan (x 9776), the box's front; the cascade below it. The plan's 'terrace' 19.9 m wide at x 9751-9772 is the two stairs' upper ends with this landing between (v2)"),
    "st_top": ([5.2, 9.6], "S71;S01", "C", "the stair's upper end in plan (x, z): plate 10's upper flights arrive beside the door, their inner walls meeting at the shell (P0303); S01's 'terrace' 19.9 m wide covers both tops (v2)"),
    "st_foot": ([15.5, 36.0], "S01;S71", "C", "the stair's foot at the court: the outer front corner of S01's stair block (x 9660, y 1005: z 35.5, x 20.8 less the band's half-width)"),
    "st_w": (5.0, "S01;S71", "C", "the band's width: S01's blocks 11.4-15.5 m across a diagonal band; plate 10 draws a wide flight with a balustrade each side"),
    "st_land": (3.0, "S71", "C", "the half-way landing with its carved panel: plate 10"),
    "st_land_at": ([11.0, 15.6], "S71", "C", "where the upper flight meets the half-way landing (x, z): plate 10's upper flights run outward from the door's landing, the lower flights forward along the pool (the west reader; v3)"),
    "st_mid": (0.5, "S71", "C", "the half-way landing's level as a share of the rise"),
    "plinth_h": (1.5, "S71", "C", "the plinth under the figures, above the pool's rim: plate 10's module (60 px at 38.9 px/m)"),
    "plinth_d": (1.3, "S71", "C", "its depth before the stair wall: plate 10"),
    "fig_h": (1.45, "S849;S71", "C", "a seated figure on its pedestal, head included; the bronze heads are about 0.5 m high (S849, B), the bodies are lost; plate 10 draws the figure about as tall as the plinth"),
    "head_h": (0.5, "S849", "B", "the bronze heads, about 50 cm high: the press on the originals (S849)"),
    "rim_h": (0.5, "S71", "C", "the pool's rim above the court"),
    "shell_w": (3.2, "S71;S337", "C", "the great shell: plate 10 draws it as wide as two figures; S337 gives about 2 m high (method e, a lead)"),
    "shell_h": (2.7, "S337;S71", "C", "its height above its pedestal: S337's 'about two metres' (a lead); plate 10's fit wants 0.5 m more (v4)"),
    "vase_z": (24.0, "S71", "C", "the vase fountain on the axis, two thirds of the way from the shell to the pool's front rim: plate 10"),
    "vase_h": (1.5, "S71", "C", "the vase fountain's top above the water: plate 10's fit put a 2.35 m vase 1.2 m too high (v4)"),
    "court_z": (47.0, "S71", "C", "the paved court before the pool, to beyond the pedestals: plate 10 draws it paved in squares with a path on the axis"),
    "ped_x": (20.0, "S71", "C", "the two great pedestals at the court's front corners, outside the stair feet: plate 10 (S02: 'two great pedestals')"),
    "ped_z": (39.0, "S71", "C", "as above, a little before the pool's front"),
    "ped_s": (3.4, "S71", "C", "their base, square: plate 10"),
    "ped_h": (2.8, "S71", "C", "their body's height to the cornice; a crown above: plate 10 (v4: the fit put the v3 cornice 2 m too high)"),
    # the link and the water building
    "link_w": (9.4, "S01", "C", "the link between the west block and the west wheel house: plan x 9876-9967, 9.4 m N-S"),
    "link_h": (4.6, "S71", "C", "single storey, arcaded, a balustraded roof: plate 13 draws its arcade below the range's windows"),
    "wb_z0": (-28.4, "S01;S850", "C", "the water building's west face: the box XY08-M39 (plan x 9967)"),
    "wb_z1": (-66.8, "S01;S850", "C", "its east face: the box XY08-M40's east end, placed on the ruin (S850)"),
    "wb_bays": (13, "S604;S415", "B", "thirteen bays on the north and south fronts with two slight projections at the ends (S604 via S415, B); plates 11 and 13 read 3-7-3"),
    "wb_w": (19.1, "S01", "C", "the range's depth N-S: the plan's middle strip y 1062-1153"),
    "wb_proj": (0.75, "S415;S71", "C", "the end sections' projection: 'two slight projections' (S415); plate 11 draws the return as one narrow pilaster strip, about a quarter bay; the plan draws the west wheel house 25.8 m N-S, 3.35 m each side (Q227)"),
    "Hr": (8.1, "S71", "C", "the water building's cornice and roof terrace: plate 12's top landing 8.1 m, plates 11 and 13 8.6-9.3 m by their tie; one level with the east stairs' top"),
    "tank_l": (27.36, "S310;S06;S109", "B", "the reservoir 锡海 27.36 m E-W = 8.55 丈 (S310, S06, S109)"),
    "tank_w": (5.92, "S310;S06", "B", "5.92 m N-S = 1.85 丈 (S310, S06); S109 and the old params say 5.72 (a correction question stays open)"),
    "tank_d": (1.44, "S600", "A", "1.44 m deep = 4 尺 5 寸, from a Qing drawing cited by S600 (n. 46)"),
    "tank_wall": (1.2, "S593;S110", "C", "the tank's walls on the roof: the casing was up to 5 m thick below (S110, S593); on the roof a parapet, C"),
    "pav_lz": (5.5, "S71", "C", "the raised wheel-house tiers at the ends of the roof, E-W: plate 11 draws them 135 px at 24.5 px/m; 27.36 + 2 x 5.5 = 38.4 m, the range"),
    "pav_lx": (14.5, "S71", "C", "the east tier's width N-S: plates 11 and 13 draw it a long hall, its ridge running back N-S; plate 12's fit puts its eaves 2.7 m further out each side than a 9.3 m body (v4; the dossier's 9.3 m was plate 12's module at the stairs' depth)"),
    "pavW_lx": (6.0, "S71", "C", "the west tier's width N-S: plates 11 and 13 draw it about square (the sides reader)"),
    "pav_eave": (3.4, "S71", "C", "their walls above the roof: plate 12's hall eaves 10.3 m less the roof 8.1 m, with plate 11"),
    "pav_ridge": (14.6, "S71", "C", "their ridge: plates 11 and 13 put the crown at 14.3-14.5 m; plate 12 by its module 13.6 m, its fit 1.4 m higher (v4)"),
    # the east block
    "eb_w": (26.1, "S01;S71", "C", "the east block's front: plan x 10154-10264 and plate 12, 26.1 m"),
    "eb_z1": (-90.7, "S01", "C", "its east face: the box XY08-M41"),
    "L1": (3.5, "S71", "C", "the lowest landings at the block's outer ends: plate 12"),
    "L2": (4.8, "S71", "C", "the half-landings beside the door's crest: plate 12 (its module 5.5 m; v4 with L3)"),
    "L3": (6.0, "S71", "C", "the third landings at the outer ends: plate 12 draws four flights a side (the east reader); its corner post fitted 1 m below the v3 level of 6.8 m"),
    "wb_door": (4.2, "S71", "C", "the water building's door crowns (and its window heads): plate 11 at 0.52 of the storey, the dossier's door 1.9 x 4.3 m (v4; v3 had 5.6 m)"),
    "es_door": (4.6, "S71", "C", "the east passage door's crown: plate 12's fit put it 1.8 m above the dossier's 3.6 m arch crown; taken half-way (v4)"),
    "fl_w": (2.6, "S71", "C", "each flight's width: plate 12 draws three flights stacked in the block's depth"),
    "es_door_w": (1.7, "S71", "C", "the passage door: plate 12, 88 px at 51.7 px/m; its arch crown at 3.6 m"),
    "rail": (1.05, "S71", "C", "balustrade height"),
}
V = {k: v[0] for k, v in P.items()}

COL = {
    "rustic": "#d6cfc1", "joint": "#a39a8a", "marble": "#ebe6da", "wall": "#cbc4b6", "panel": "#8f8a82", "glaze": "#3f8a86",
    "glass_win": "#2e4a4f", "door": "#4a3b2c", "roof": "#3f7f6c", "roofedge": "#336a5b", "ridge": "#c9a245", "water": "#6f9fb0", "jet": "#d8ecf2",
    "pave": "#c6bfae", "step": "#d2ccbe", "lead": "#8c8a86", "bronze": "#7a4c30", "rock": "#9d978a", "earth": "#8a7f6c",
}

m = None
PT = None
KP, JOINTS, ENTRIES, FOOTPRINTS = {}, [], [], []
FRAME = {}
G = None


def kp(name, p, anchor=False):
    KP[name] = {"p": [round(float(c), 3) for c in p], "anchor": anchor}


# ---------------------------------------------------------------- the frame and the ground
def frame():
    """The model's origin and turn: on the line through the pool's and the reservoir's boxes (both placed on the ruin, S850), at the west block's box's middle and ground."""
    fc = json.load(open(ROOT / "site/reconstruction/data/halls_1860.geojson", encoding="utf-8"))
    F = {f["properties"]["id"]: f for f in fc["features"]}

    def cen(k):
        r = [np.array(to_xz(*c), float) for c in F[k]["geometry"]["coordinates"][0]]
        return (r[0] + r[2]) / 2

    pool, tank, blk = cen("XY08-M42"), cen("XY08-M40"), cen("XY08-M37")
    u = (pool - tank) / np.linalg.norm(pool - tank)
    o = tank + u * float(np.dot(blk - tank, u))
    rot = math.atan2(u[0], u[1])
    base = F["XY08-M37"]["properties"]["ground_m"] - DATUM_M
    return [round(float(o[0]), 3), round(base, 3), round(float(o[1]), 3)], round(rot, 6)


def to_scene(p, pos=None, rot=None):
    pos = pos or FRAME["pos"]
    rot = FRAME["rot"] if rot is None else rot
    c, s = math.cos(rot), math.sin(rot)
    x, y, z = p
    return [round(pos[0] + c * x + s * z, 3), round(pos[1] + y, 3), round(pos[2] - s * x + c * z, 3)]


def gy(x, z):
    """The walk surface under a model point, in the model's y."""
    sx, _, sz = to_scene((x, 0.0, z))
    g = G.land(sx, sz)
    if g is None:
        g = G.at(sx, sz)
    return g - FRAME["pos"][1]


def gmin(poly, n=4):
    """The lowest ground under a polygon (corners and a grid inside its box)."""
    xs, zs = [p[0] for p in poly], [p[1] for p in poly]
    pts = list(poly) + [(x, z) for x in np.linspace(min(xs), max(xs), n) for z in np.linspace(min(zs), max(zs), n)]
    return min(gy(x, z) for x, z in pts)


def gmax(poly, n=4):
    xs, zs = [p[0] for p in poly], [p[1] for p in poly]
    pts = list(poly) + [(x, z) for x in np.linspace(min(xs), max(xs), n) for z in np.linspace(min(zs), max(zs), n)]
    return max(gy(x, z) for x, z in pts)


def rect(x0, x1, z0, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def skirt(poly, top, mat, closed=True, step=2.5):
    """Vertical faces from just below the ground (followed along the edges, every `step` m) up to `top`. Returns the bottoms at the polygon's corners."""
    n = len(poly)
    bots = []
    for i in range(n if closed else n - 1):
        (ax, az), (bx, bz) = poly[i], poly[(i + 1) % n]
        L = math.hypot(bx - ax, bz - az)
        k = max(1, int(math.ceil(L / step)))
        pts = [(ax + (bx - ax) * t / k, az + (bz - az) * t / k) for t in range(k + 1)]
        ys = [gy(x, z) - 0.15 for x, z in pts]
        bots.append(ys[0])
        tops = top if isinstance(top, (list, tuple)) else None
        for j in range(k):
            ya, yb = (tops[i] + (tops[(i + 1) % n] - tops[i]) * j / k, tops[i] + (tops[(i + 1) % n] - tops[i]) * (j + 1) / k) if tops else (top, top)
            (x0, z0), (x1, z1) = pts[j], pts[j + 1]
            m.poly([(x0, ys[j], z0), (x1, ys[j + 1], z1), (x1, yb, z1)], mat)
            m.poly([(x0, ys[j], z0), (x1, yb, z1), (x0, ya, z0)], mat)
    if not closed:
        bots.append(gy(*poly[-1]) - 0.15)
    return bots


def footing(poly, top, mat="rustic", name=None, kind="wall foot", corners=True):
    """A plinth from just below the ground (followed along its edges) up to `top`; its corners are joints."""
    bots = skirt(poly, top, mat)
    m.flat(poly, top, mat)
    FOOTPRINTS.append(list(poly))
    if name and corners:
        for i, (x, z) in enumerate(poly):
            JOINTS.append([f"{name}_{i}", x, bots[i], z, kind])
    return min(bots)


# ---------------------------------------------------------------- façades, drawn in a face frame
def face(x, z, normal):
    """Push a face frame at (x, z) facing `normal` in the model's plan: 'W' (+z), 'E' (-z), 'S' (+x), 'N' (-x)."""
    rot = {"W": 0.0, "E": math.pi, "S": math.pi / 2, "N": -math.pi / 2}[normal]
    m.push(x, 0, z, rot)


def bays(s0, s1, n):
    w = (s1 - s0) / n
    return [(s0 + i * w, s0 + (i + 1) * w) for i in range(n)]


def west_block():
    W, D, H1, H2 = V["W"], V["D"], V["H1"], V["H2"]
    hw = W / 2
    zB = -11.35
    zF = zB + D
    hc, cp = V["cen_w"] / 2, V["cen_proj"]
    px = hw - V["pav_w"]  # the end pavilions from px to hw
    FRAME["zF"], FRAME["zB"] = zF, zB
    y0 = footing(rect(-hw, hw, zB, zF), 0.45, "marble", name="wblock")
    m.box(-hc, hc, y0, 0.45, zF, zF + cp, "marble")
    for sx, tag in ((-1, "N"), (1, "S")):
        for sz, tz in ((1, "W"), (-1, "E")):
            kp(f"blk_foot_{tag}{tz}", (sx * hw, max(0.0, gy(sx * hw, zF if sz > 0 else zB)), zF if sz > 0 else zB), anchor=True)

    bw = W / V["bays"]
    cen = [-hw + bw * (i + 0.5) for i in range(V["bays"])]

    # ---- the west front: ground storey (rusticated, arched windows; the middle hidden by the terrace), upper storey of eleven bays (plate 10)
    m.cls = "doc"
    face(0, zF, "W")
    holes = [(c - 0.75, c + 0.75, 1.4, H1 - 2.1, 0.75) for c in cen if abs(c) > V["terr_w"] / 2 + 0.6]
    P_.wall_holes(-hw, hw, 0.45, H1 - 0.4, holes, "rustic")
    for h in holes:
        P_.opening(*h, kind="win", frame=0.16)
    P_.rustication(-hw, hw, 0.45, H1 - 0.4)
    m.box(-hw - 0.12, hw + 0.12, H1 - 0.4, H1, 0, 0.28, "marble", skip=("back",))
    # upper storey: pavilions' bays with pedimented heads, two bays with arched frames, a plain bay, the door; the centre bays proud
    ytop = H2 - 1.1
    for s0, s1, kind in ((-hw, -hc, "side"), (hc, hw, "side")):
        hs = []
        for c in cen:
            if s0 <= c <= s1:
                hs.append((c - 0.85, c + 0.85, H1 + 0.55, ytop - 1.25, 0.0 if abs(c) > px else 0.0))
        P_.wall_holes(s0, s1, H1, ytop, hs, "wall")
        for (a, b, c0, c1, r) in hs:
            c = (a + b) / 2
            if abs(c) > px:
                P_.opening(a, b, c0, c1, 0, kind="win", head="pediment", frame=0.18)
            elif abs(c) > hc + bw:
                P_.opening(a, b, c0, c1, 0, kind="win", frame=0.18)
                # the arched frame over the window (plate 10: the two bays each side of the plain bay)
                m.poly([(a - 0.45, c1 + 0.2, 0.12), (b + 0.45, c1 + 0.2, 0.12), (b + 0.45, c1 + 0.45, 0.12), (a - 0.45, c1 + 0.45, 0.12)], "marble")
                from model_parts import arc_pts
                ring_o = arc_pts(a - 0.45, b + 0.45, c1 + 0.45, 1.05, 8)
                ring_i = arc_pts(a - 0.2, b + 0.2, c1 + 0.45, 0.8, 8)
                for (p0, q0), (p1, q1) in zip(zip(ring_i[:-1], ring_o[:-1]), zip(ring_i[1:], ring_o[1:])):
                    m.poly([(p0[0], p0[1], 0.12), (q0[0], q0[1], 0.12), (q1[0], q1[1], 0.12), (p1[0], p1[1], 0.12)], "marble")
                P_.cartouche(c, c1 + 0.95, 0.7, 0.55)
            else:
                P_.opening(a, b, c0, c1, 0, kind="win", head="cornice", frame=0.18)
        for k in range(int(round((s1 - s0) / bw)) + 1):
            s = s0 + k * bw
            P_.pilaster(s, H1, ytop, w=0.62, out=0.24)
        P_.entablature(s0, s1, H2, h=1.1, ends=True)
    # the pavilions' edges: clustered pilasters (plate 10)
    for s in (-px, px, -hw + 0.3, hw - 0.3):
        P_.pilaster(s, H1, ytop, w=0.45, out=0.36)
    m.pop()
    # the centre, proud by cen_proj: window, door, window; free columns at the door (plate 10)
    face(0, zF + cp, "W")
    m.poly([(-hc, 0.45, 0), (-hc, 0.45, -cp), (-hc, H2, -cp), (-hc, H2, 0)], "wall")
    m.poly([(hc, 0.45, -cp), (hc, 0.45, 0), (hc, H2, 0), (hc, H2, -cp)], "wall")
    P_.wall_holes(-hc, hc, 0.45, H1, [], "rustic")
    cb = bays(-hc, hc, 3)
    hs = [(cb[0][0] + bw / 2 - 0.85, cb[0][0] + bw / 2 + 0.85, H1 + 0.55, ytop - 1.25, 0), (-1.2, 1.2, H1 + 0.05, ytop - 0.9, 0), (cb[2][0] + bw / 2 - 0.85, cb[2][0] + bw / 2 + 0.85, H1 + 0.55, ytop - 1.25, 0)]
    P_.wall_holes(-hc, hc, H1, ytop, hs, "wall")
    for i, h in enumerate(hs):
        P_.opening(*h, kind="door" if i == 1 else "win", head="cornice" if i != 1 else None, frame=0.24 if i == 1 else 0.18)
    for s in (-hc + 0.3, cb[0][1], cb[1][1], hc - 0.3):
        P_.pilaster(s, H1, ytop, w=0.6, out=0.3)
    for s in (-1.85, 1.85):
        P_.column(s, 0.75, H1, ytop + 0.3, r=0.32)
    # the door hood with a cartouche over the door (S310: 'a door hood with a glazed gourd top')
    m.box(-2.3, 2.3, ytop - 0.9 + 0.24, ytop + 0.3, 0, 1.0, "marble", skip=("back",))
    P_.cartouche(0, ytop - 0.15, 1.1, 0.75)
    P_.entablature(-hc, hc, H2, h=1.1, out=0.5)
    # the attic: a panelled wall over the centre bays, urns, and the broken pediment with its crest (plate 10)
    ya = H2 + V["attic_h"]
    m.box(-hc + 0.2, hc - 0.2, H2, ya - 0.35, -1.6, 0.05, "wall")
    m.box(-hc, hc, ya - 0.35, ya, -1.7, 0.3, "marble")
    for sc in (-hc + 2.2, hc - 2.2):
        P_.cartouche(sc, H2 + (V["attic_h"] - 0.35) / 2, 2.4, 1.2)
        P_.urn(sc, -0.6, ya, 0.9) if False else None
    for sc in (-hc + 0.3, -hc + 4.0, hc - 4.0, hc - 0.3):
        m.push(sc, 0, 0, 0)
        P_.urn(0, -0.6, ya, 1.0)
        m.pop()
    pa = V["ped_apex"]
    for sx in (-1, 1):  # the broken pediment's two scrolls
        m.poly([(sx * 3.4, ya, 0.25), (sx * 1.1, ya, 0.25), (sx * 1.1, pa - 0.3, 0.25), (sx * 2.2, pa - 0.9, 0.25), (sx * 3.4, ya + 0.6, 0.25)], "marble")
        m.poly([(sx * 3.4, ya, -0.25), (sx * 1.1, ya, -0.25), (sx * 1.1, pa - 0.3, -0.25), (sx * 2.2, pa - 0.9, -0.25), (sx * 3.4, ya + 0.6, -0.25)], "marble")
    m.box(-1.1, 1.1, ya, pa, -0.3, 0.3, "marble")
    m.box(-0.8, 0.8, ya + 0.3, pa - 0.4, 0.3, 0.38, "panel")
    m.lathe([(0.75, pa), (0.75, pa + 0.15), (0.45, pa + 0.3), (0.62, pa + 0.6), (0.3, pa + 0.85), (0.0, pa + 1.0)], 8, "ridge", cx=0, cz=0, cap=False)
    kp("blk_ped_apex_W", (0, pa, 0.3))
    kp("attic_crest_top", (0, pa + 1.0, 0.0))
    kp("blk_door_W_head", (0, ytop - 0.9 + 0.05, 0.05))
    m.pop()
    # the attic in the model's frame for the key points
    zc = zF + cp
    kp("attic_top_N", (-hc - 0.3, ya, zc + 0.3))
    kp("attic_top_S", (hc + 0.3, ya, zc + 0.3))
    for sx, tag in ((-1, "N"), (1, "S")):
        kp(f"blk_cornice_{tag}W", (sx * (hw + 0.45), H2, zF + 0.45))
        kp(f"blk_cornice_{tag}E", (sx * (hw + 0.45), H2, zB - 0.45))
        kp(f"colW_{tag}_cap", (sx * 1.85, ytop + 0.3, zc + 0.75))

    # ---- the rear (east) face: two storeys of windows, the link in the middle (plates 11 and 13, raking)
    face(0, zB, "E")
    lw = V["link_w"] / 2
    holes = [(c - 0.75, c + 0.75, 1.4, H1 - 2.1, 0.75) for c in cen if abs(c) > lw + 0.9]
    P_.wall_holes(-hw, hw, 0.45, H1 - 0.4, holes, "rustic")
    for h in holes:
        P_.opening(*h, kind="win", frame=0.16)
    P_.rustication(-hw, hw, 0.45, H1 - 0.4)
    m.box(-hw - 0.12, hw + 0.12, H1 - 0.4, H1, 0, 0.28, "marble", skip=("back",))
    hs = [(c - 0.8, c + 0.8, H1 + 0.55, ytop - 1.25, 0) for c in cen]
    P_.wall_holes(-hw, hw, H1, ytop, hs, "wall")
    for h in hs:
        P_.opening(*h, kind="win", head="scroll", frame=0.18)
    for k in range(V["bays"] + 1):
        P_.pilaster(-hw + k * bw, H1, ytop, w=0.55, out=0.22)
    P_.entablature(-hw, hw, H2, h=1.1)
    m.pop()
    # ---- the two ends (plates 11 and 13): rusticated corners, a window below, a great framed panel above
    for sx, tag in ((-1, "N"), (1, "S")):
        face(sx * hw, (zF + zB) / 2, tag)
        hd = D / 2
        P_.wall_holes(-hd, hd, 0.45, H1 - 0.4, [], "rustic")
        P_.rustication(-hd, hd, 0.45, H1 - 0.4)
        P_.cartouche(0, (0.45 + H1 - 0.4) / 2, 2.2, (H1 - 0.85) * 0.55)  # a framed panel on the ground storey too (plate 11)
        m.box(-hd - 0.12, hd + 0.12, H1 - 0.4, H1, 0, 0.28, "marble", skip=("back",))
        P_.wall_holes(-hd, hd, H1, ytop, [], "wall")
        P_.cartouche(0, (H1 + ytop) / 2, 3.0, (ytop - H1) * 0.62)
        for s in (-hd + 0.3, -hd + 1.0, hd - 1.0, hd - 0.3):
            P_.pilaster(s, H1, ytop, w=0.5, out=0.3)
        for s in (-hd + 0.35, hd - 0.35):  # quoins
            y = 0.45
            while y < H1 - 0.6:
                m.box(s - 0.45, s + 0.45, y, y + 0.42, 0, 0.08, "marble", skip=("back",))
                y += 0.84
        P_.entablature(-hd, hd, H2, h=1.1)
        m.pop()
        kp(f"end_panel_{tag}", (sx * (hw + 0.1), (H1 + ytop) / 2, (zF + zB) / 2))

    # ---- the roofs: the end pavilions' square hip roofs, the long middle roof, green glazed with yellow ridges (S310)
    m.box(-hw, hw, H2 - 0.02, H2, zB, zF, "lead", skip=("bottom",))
    ov = 0.9
    for sx, tag in ((-1, "N"), (1, "S")):
        cxp = sx * (px + hw) / 2
        r = P_.roof_hip(cxp, (zF + zB) / 2, V["pav_w"] / 2 + ov, D / 2 + ov, H2 + 0.05, V["ridge_pav"] - 0.35, along="x", doc={"N", "S", "E", "W"})
        e = r["ridge"]
        kp(f"blk_ridge_{tag}", e[0] if (e[0][0] < e[1][0]) == (sx < 0) else e[1])
        for (ex, ez), p in r["eaves"].items():
            if ex == sx:
                kp(f"blk_eave_{tag}{'W' if ez > 0 else 'E'}", p)
    r = P_.roof_hip(0, (zF + zB) / 2, px + 1.0, D / 2 + ov, H2 + 0.05, V["ridge_mid"] - 0.35, along="x", doc={"W", "N", "S"}, ends=False)
    # where the middle ridge runs into the pavilion's inner hip: the hip's height reaches the ridge's at this distance from the pavilion's middle (the roof_hip profile)
    y0p, y1p, hxp, rlp = H2 + 0.05, V["ridge_pav"] - 0.35, V["pav_w"] / 2 + ov, max(V["pav_w"] / 2 - D / 2, 0.4)
    tt = min(1.0, max(0.0, (V["ridge_mid"] - 0.35 - y0p) / (y1p - y0p))) ** (1 / 1.45)
    reach = hxp + (rlp - hxp) * tt
    for sx, tag in ((-1, "N"), (1, "S")):
        kp(f"midroof_ridge_{tag}", (sx * ((px + hw) / 2 - reach), V["ridge_mid"], (zF + zB) / 2))
    # crests over the rear windows' line (plates 11 and 13 draw a row of small crests on the rear roof)
    m.cls = "doc"
    for c in cen:
        if abs(c) < px - 1:
            m.box(c - 0.5, c + 0.5, H2, H2 + 0.9, zB - 0.25, zB + 0.25, "marble")
            m.poly([(c - 0.5, H2 + 0.9, zB - 0.26), (c + 0.5, H2 + 0.9, zB - 0.26), (c, H2 + 1.35, zB - 0.26)], "marble")

    # ---- the wings: single-storey rooms with flat roofs and balustrades before the end pavilions (S310; plate 10's balconies)
    wz1 = zF + V["wing_d"]
    for sx, tag in ((-1, "N"), (1, "S")):
        x0, x1 = sorted((sx * (V["wing_x"] - V["wing_w"] / 2), sx * (V["wing_x"] + V["wing_w"] / 2)))
        footing(rect(x0, x1, zF, wz1), 0.45, "marble", name=f"wing{tag}")
        m.box(x0 + 0.6, x1 - 0.6, 0.45, H1 - 0.4, zF, wz1 - 0.6, "panel", skip=("bottom",))  # the inside; the faces carry the walls and their openings
        m.box(x0 - 0.1, x1 + 0.1, H1 - 0.4, H1, zF, wz1 + 0.1, "marble", skip=("bottom",))
        face((x0 + x1) / 2, wz1, "W")
        hs = [(-0.8, 0.8, 1.4, H1 - 2.2, 0.8)]
        P_.wall_holes(-(x1 - x0) / 2, (x1 - x0) / 2, 0.45, H1 - 0.4, hs, "rustic", d=0.01)
        P_.opening(*hs[0], kind="win", frame=0.16)
        m.pop()
        for side, xx in (("N", x0), ("S", x1)):
            outer = (side == "N") == (sx < 0)
            face(xx, (zF + wz1) / 2, side)
            m.cls = "doc" if outer else "fill"
            hs = [(-0.75, 0.75, 1.4, H1 - 2.2, 0.75)]
            P_.wall_holes(-V["wing_d"] / 2, V["wing_d"] / 2, 0.45, H1 - 0.4, hs, "rustic", d=0.01)
            P_.opening(*hs[0], kind="win", frame=0.16)
            m.pop()
            m.cls = "doc"
        P_.rail([(x0 + 0.15, zF + 0.1), (x0 + 0.15, wz1 - 0.15), (x1 - 0.15, wz1 - 0.15), (x1 - 0.15, zF + 0.1)], H1)
        for xx in (x0 + 0.15, x1 - 0.15):
            P_.urn(xx, wz1 - 0.15, H1 + V["rail"] + 0.06, 0.9)
        kp(f"wing_rail_{tag}W", ((x0 if sx < 0 else x1) - 0.0, H1 + V["rail"], wz1 - 0.15))
    FRAME["wz1"] = wz1


# ---------------------------------------------------------------- the terrace, the stairs, the figures, the pool, the shell, the pedestals
def stair_path(sx):
    """One side's stair in plan: the upper flight from T (at the landing before the door) outward to L0, the half-way landing and the lower flight from L0 to the foot F.
    Units along (u) and across, outward (n), per segment."""
    T = np.array([sx * V["st_top"][0], V["st_top"][1]])
    L0 = np.array([sx * V["st_land_at"][0], V["st_land_at"][1]])
    F = np.array([sx * V["st_foot"][0], V["st_foot"][1]])

    def un(a, b):
        L = float(np.linalg.norm(b - a))
        u = (b - a) / L
        n = np.array([u[1], -u[0]])
        if n[0] * sx < 0:
            n = -n
        return L, u, n

    l1, u1, n1 = un(T, L0)
    l2, u2, n2 = un(L0, F)
    return T, L0, F, (l1, u1, n1), (l2, u2, n2)


def terrace_and_stairs():
    H1, R = V["H1"], V["rail"]
    zF, cp = FRAME["zF"], V["cen_proj"]
    tw = V["terr_w"] / 2
    tz = V["terr_z"]
    # the terrace: solid, rusticated, from the centre bays to its front at tz; the cascade face with the shell group in front (plate 10)
    poly = rect(-tw, tw, zF + cp, tz)
    footing(poly, H1, "rustic", name="terrace", corners=False)
    JOINTS.append(["terrace_front_N", -tw, gy(-tw, tz) - 0.15, tz, "wall foot"])
    JOINTS.append(["terrace_front_S", tw, gy(tw, tz) - 0.15, tz, "wall foot"])
    m.box(-tw, tw, H1 - 0.02, H1, zF + cp, tz, "pave", skip=("bottom",))
    face(0, tz, "W")
    m.box(-tw - 0.1, tw + 0.1, H1 - 0.45, H1, 0, 0.3, "marble", skip=("back",))
    # the cascade's niche and the fish-and-shell group as a stepped panel (plate 10: two fish over a shell, a scroll frame)
    m.box(-2.4, 2.4, 2.6, H1 - 0.45, 0, 0.35, "marble", skip=("back",))
    m.box(-1.7, 1.7, 3.0, H1 - 0.9, 0.35, 0.5, "panel", skip=("back",))
    for sx in (-1, 1):
        m.poly([(sx * 2.4, 2.6, 0.36), (sx * 3.6, 2.0, 0.36), (sx * 3.4, 3.6, 0.36), (sx * 2.4, H1 - 0.45, 0.36)], "marble")
    m.pop()
    # the terrace's front is the cascade's parapet, not a balustrade (plate 10, the west reader): a solid parapet rising to a scrolled middle with the two fish on it
    m.box(-tw, tw, H1, H1 + 0.9, tz - 0.45, tz + 0.05, "marble")
    m.poly([(-1.6, H1 + 0.9, tz + 0.06), (1.6, H1 + 0.9, tz + 0.06), (0.9, H1 + 1.5, tz + 0.06), (-0.9, H1 + 1.5, tz + 0.06)], "marble")
    m.box(-1.6, 1.6, H1 + 0.9, H1 + 1.5, tz - 0.4, tz + 0.05, "marble")
    for sx in (-1, 1):  # the two fish, heads down towards the axis, as plain tapering forms
        m.push(sx * 0.55, 0, tz - 0.15, 0)
        m.lathe([(0.0, H1 + 1.5), (0.22, H1 + 1.75), (0.18, H1 + 2.3), (0.05, H1 + 2.6), (0.22, H1 + 2.85)], 6, "marble", cx=0, cz=0, cap=True)
        m.pop()
    kp("blk_stair_land_W", (0, H1 + 0.9, tz + 0.05))
    for sx, tag in ((-1, "N"), (1, "S")):
        kp(f"terr_rail_{tag}", (sx * (tw - 0.2), H1 + R + 0.06, tz - 0.15))

    for sx, tag in ((-1, "N"), (1, "S")):
        T, L0, F, (l1, u1, n1), (l2, u2, n2) = stair_path(sx)
        hw = V["st_w"] / 2
        gF = gy(*F)
        top_l, land = 1.6, V["st_land"]
        ymid = gF + (H1 - gF) * V["st_mid"]
        na = int(round((H1 - ymid) / 0.155))
        nb_ = int(round((ymid - gF) / 0.155))
        # steps: (origin, u, n, a, b, y): the top landing, the upper flight, the half-way landing, the lower flight
        segs = [(T, u1, n1, 0.0, top_l, H1)]
        for k in range(na):
            segs.append((T, u1, n1, top_l + (l1 - top_l) * k / na, top_l + (l1 - top_l) * (k + 1) / na, H1 - (H1 - ymid) * (k + 1) / na))
        segs.append((L0, u2, n2, 0.0, land, ymid))
        for k in range(nb_):
            segs.append((L0, u2, n2, land + (l2 - land) * k / nb_, land + (l2 - land) * (k + 1) / nb_, ymid - (ymid - gF) * (k + 1) / nb_))
        m.cls = "doc"
        polys = []
        for O, u, n, a, b, y in segs:
            if y <= gF + 0.01:
                continue
            q = [O + u * a - n * hw, O + u * b - n * hw, O + u * b + n * hw, O + u * a + n * hw]
            m.flat([tuple(p) for p in q], y, "step")
            ybs = min(gy(*p) for p in q) - 0.15  # this step's footing follows the ground
            m.poly([(q[1][0], ybs, q[1][1]), (q[2][0], ybs, q[2][1]), (q[2][0], y, q[2][1]), (q[1][0], y, q[1][1])], "step")
            for side, i0, i1 in (("in", 0, 1), ("out", 3, 2)):
                m.cls = "doc" if side == "in" else "fill"
                m.poly([(q[i0][0], ybs, q[i0][1]), (q[i1][0], ybs, q[i1][1]), (q[i1][0], y, q[i1][1]), (q[i0][0], y, q[i0][1])], "rustic" if side == "in" else "wall")
                m.cls = "doc"
        # the bend's outer wedge, at the landing's level
        wedge = [tuple(L0), tuple(L0 + n1 * hw), tuple(L0 + n2 * hw)]
        m.flat(wedge, ymid, "step")
        m.cls = "fill"
        skirt([wedge[1], wedge[2]], ymid, "wall", closed=False)
        m.cls = "doc"
        band1 = [tuple(T - n1 * hw), tuple(L0 - n1 * hw), tuple(L0 + n1 * hw), tuple(T + n1 * hw)]
        band2 = [tuple(L0 - n2 * hw), tuple(F - n2 * hw), tuple(F + n2 * hw), tuple(L0 + n2 * hw)]
        FOOTPRINTS.extend([band1, band2, wedge])
        # balustrades along both edges, sloping; urns on the posts (plate 10: carved marble balustrades, S02's small jets on them not drawn)
        for side in (-1, 1):
            pts = [T + u1 * 0.0 + n1 * side * (hw - 0.2), T + u1 * top_l + n1 * side * (hw - 0.2), L0 + n1 * side * (hw - 0.2), L0 + n2 * side * (hw - 0.2), L0 + u2 * land + n2 * side * (hw - 0.2), F - u2 * 0.4 + n2 * side * (hw - 0.2)]
            ys = [H1, H1, ymid, ymid, ymid, gF + 0.15]
            if side < 0:
                # the landing's inner parapet is solid, a long low box with a carved front (plate 10, P0303), not a balustrade
                P_.rail([tuple(p) for p in pts[:3]], ys[:3], posts=2.4)
                a_, b_ = pts[3], pts[4]
                d_ = (b_ - a_) / np.linalg.norm(b_ - a_)
                pq = [tuple(a_ - n2 * 0.25), tuple(b_ - n2 * 0.25), tuple(b_ + n2 * 0.25), tuple(a_ + n2 * 0.25)]
                m.prism(pq, ymid, ymid + V["rail"], "marble")
                P_.rail([tuple(p) for p in pts[4:]], ys[4:], posts=2.4)
            else:
                P_.rail([tuple(p) for p in pts], ys, posts=2.4)
            for p, y in zip(pts[1:-1], ys[1:-1]):
                P_.urn(p[0], p[1], y + R + 0.06, 0.8)
        q = L0 + u2 * land - n2 * (hw - 0.2)  # the post at the landing's front end on the inner side, over the figures
        kp(f"stair_{tag}_landing", (q[0], ymid + R, q[1]))
        kp(f"stair_{tag}_foot", tuple([(F + n2 * hw)[0], gF, (F + n2 * hw)[1]]), anchor=True)
        JOINTS.append([f"stair_{tag}_foot", float(F[0]), gF - 0.15, float(F[1]), "stair foot"])
        ENTRIES.append([f"stair_{tag}_foot", float(F[0] + u2[0] * 0.6), gF, float(F[1] + u2[1] * 0.6)])
        FRAME[f"stair_{tag}"] = {"T": T, "L0": L0, "F": F, "u1": u1, "n1": n1, "u2": u2, "n2": n2, "l1": l1, "l2": l2, "gF": gF, "ymid": ymid, "bands": [band1, band2, wedge]}
    m.cls = "doc"


def figures_and_pool():
    """The plinths at the stair walls' feet with the twelve seated figures, six a side (plate 10; S823's order); the pool, its rim, the shell, the vase fountain, the jets."""
    rim = V["rim_h"]
    gpool = 0.5 * (gy(-12.0, 30.0) + gy(12.0, 30.0))  # the court beside the pool (the ground's own water body there lies 1.5 m lower, under this pool)
    yr = gpool + rim
    FRAME["yr"] = yr
    order = {"S": ["鼠 rat", "虎 tiger", "龙 dragon", "马 horse", "猴 monkey", "狗 dog"], "N": ["牛 ox", "兔 hare", "蛇 snake", "羊 goat", "鸡 rooster", "猪 boar"]}
    inner_edge = {}
    for sx, tag in ((-1, "N"), (1, "S")):
        S = FRAME[f"stair_{tag}"]
        L0, u, n, l2 = S["L0"], S["u2"], S["n2"], S["l2"]
        hw = V["st_w"] / 2
        pdp = V["plinth_d"]
        # the plinth runs along the lower flight's inner wall, from the half-way landing to near the foot
        A, B = L0 + u * 0.3 - n * hw, L0 + u * (l2 - 3.2) - n * hw
        poly = [tuple(A), tuple(B), tuple(B - n * pdp), tuple(A - n * pdp)]
        ytop = yr + V["plinth_h"]
        y0 = skirt(poly, ytop, "marble")[3]
        m.flat(poly, ytop, "marble")
        FOOTPRINTS.append(poly)
        S["plinth"] = poly
        # carved panels on the plinth's face (plate 10, P0439)
        npan = 6
        for k in range(npan):
            t0, t1 = (k + 0.12) / npan, (k + 0.88) / npan
            p0, p1 = A - n * (pdp + 0.02) + (B - A) * t0, A - n * (pdp + 0.02) + (B - A) * t1
            m.poly([(p0[0], yr + 0.25, p0[1]), (p1[0], yr + 0.25, p1[1]), (p1[0], ytop - 0.3, p1[1]), (p0[0], ytop - 0.3, p0[1])], "panel")
        inner_edge[tag] = (A - n * pdp, B - n * pdp)
        JOINTS.append([f"plinth_{tag}", float((A - n * pdp)[0]), y0, float((A - n * pdp)[1]), "plinth foot"])
        # six figures, facing the pool (across, inward), numbered 1 at the back (by the landing) to 6 at the front
        for k in range(6):
            t = (k + 0.5) / 6
            c = A - n * (pdp / 2) + (B - A) * t
            facing = math.atan2(-n[0], -n[1])
            figure(c[0], c[1], ytop, facing, order[tag][k])
            if k in (0, 5):
                kp(f"zod_{tag}{k + 1}_head", (c[0], ytop + 0.35 + V["fig_h"], c[1]))
            if k == 5:
                q = B - n * pdp
                kp(f"zod_plinth_{tag}6_front", (q[0], ytop, q[1]))

    # the pool: back at the terrace's front, sides along the plinths, a convex front between the stair feet (plate 10; S01's slip)
    (aN, bN), (aS, bS) = inner_edge["N"], inner_edge["S"]
    fN, fS = FRAME["stair_N"]["F"], FRAME["stair_S"]["F"]
    front = []
    p0, p1 = bN + (fN - bN) * 0.45, bS + (fS - bS) * 0.45
    for k in range(13):
        t = k / 12
        x = p0[0] + (p1[0] - p0[0]) * t
        z = p0[1] + (p1[1] - p0[1]) * t + 2.6 * math.sin(math.pi * t)
        front.append((x, z))
    # the water: everything between the terrace's front, the stairs, the plinths and the front rim
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    tz = V["terr_z"]
    region = Polygon([(p0[0] - 30, tz), (p1[0] + 30, tz), (p1[0] + 30, p1[1]), *front[::-1][1:-1], (p0[0] - 30, p0[1])][::-1] if False else [(-40, tz), (40, tz), (40, p1[1])] + front[::-1] + [(-40, p0[1])])
    solid = unary_union([Polygon(q) for t in ("N", "S") for q in FRAME[f"stair_{t}"]["bands"] + [FRAME[f"stair_{t}"]["plinth"]]])
    water = region.difference(solid)
    if water.geom_type != "Polygon":
        water = max(water.geoms, key=lambda g: g.distance(Polygon([(-0.5, tz + 2), (0.5, tz + 2), (0.5, tz + 3), (-0.5, tz + 3)])) * -1 + g.area * 1e-6)
    water = water.simplify(0.05)
    outer = [tuple(c) for c in list(water.exterior.coords)[:-1]]
    FOOTPRINTS.append(outer)
    # rim: a band along the front only (the back and sides are the terrace and the plinths)
    band = [tuple(bN)] + front + [tuple(bS)]
    for (ax, az), (bx, bz) in zip(band[:-1], band[1:]):
        L = math.hypot(bx - ax, bz - az)
        nx, nz = (bz - az) / L * 0.55, -(bx - ax) / L * 0.55  # outward is towards +z for a N->S run
        if nz < 0:
            nx, nz = -nx, -nz
        ya_, yb_ = gy(ax + nx, az + nz) - 0.15, gy(bx + nx, bz + nz) - 0.15
        m.poly([(ax + nx, ya_, az + nz), (bx + nx, yb_, bz + nz), (bx + nx, yr, bz + nz), (ax + nx, yr, az + nz)], "marble")
        m.poly([(ax + nx, yr, az + nz), (bx + nx, yr, bz + nz), (bx, yr, bz), (ax, yr, az)], "marble")
        m.poly([(ax, yr, az), (bx, yr, bz), (bx, yr - 0.4, bz), (ax, yr - 0.4, az)], "marble")
    # the scrollwork with the sea creatures on the rim (plate 10): low carved blocks
    for k in (2, 4, 8, 10):
        x, z = front[k]
        m.box(x - 0.7, x + 0.7, yr, yr + 0.45, z - 0.1, z + 0.55, "marble")
    water_y = yr - 0.3
    FRAME["water_y"] = water_y
    m.flat(outer, water_y, "water")
    m.flat(outer, yr - 1.1, "panel")
    mid = front[6]
    kp("pool12_rim_W", (mid[0], yr, mid[1] + 0.55), anchor=True)
    KP["pool12_rim_L"] = {"cands": [{"p": [x, yr, z + 0.55]} for x, z in front], "pick": "left", "anchor": True}
    KP["pool12_rim_R"] = {"cands": [{"p": [x, yr, z + 0.55]} for x, z in front], "pick": "right", "anchor": True}
    for nm, (x, z) in (("pool_rim_front", mid), ("pool_rim_N", front[1]), ("pool_rim_S", front[-2])):
        pass
    # the paved court before the pool, out to beyond the pedestals (plate 10): it covers the dip of the ground's own pool basin there (Round 10 has the pool as a sunken water body)
    cz = V["court_z"]
    cx = V["ped_x"] + V["ped_s"] / 2 + 2.0
    fN, fS = FRAME["stair_N"]["F"], FRAME["stair_S"]["F"]
    court = [(-cx, fN[1] - 2.0), (float(fN[0]) - 2.5, fN[1] - 2.0)] + [(x, z + 0.55) for x, z in band] + [(float(fS[0]) + 2.5, fS[1] - 2.0), (cx, fS[1] - 2.0), (cx, cz), (-cx, cz)]
    yc = 0.5 * (gy(-cx + 1, cz - 1) + gy(cx - 1, cz - 1))
    yc = max(yc, yr - V["rim_h"])
    FRAME["court_y"] = yc
    bots = skirt(court, yc, "pave")
    m.flat(court, yc, "pave")
    FOOTPRINTS.append(court)  # the planting keeps off the paved court (plate 10 draws none on it)
    m.flat([(-1.6, z) for z in (mid[1] + 0.6,)] + [(1.6, mid[1] + 0.6), (1.6, cz), (-1.6, cz)], yc + 0.02, "step")
    for k, (x, z) in enumerate(court):
        if k in (0, len(court) - 3, len(court) - 2, len(court) - 1):
            JOINTS.append([f"court_{k}", x, gy(x, z) - 0.15, z, "paving foot"])
    # where the court stands above the ground at its front, steps on the axis down to it
    gfr = gy(0.0, cz + 0.2)
    nstep = int(round((yc - gfr) / 0.15))
    for k in range(nstep):
        m.box(-2.2, 2.2, gfr - 0.15, yc - (yc - gfr) * (k + 1) / nstep, cz, cz + 0.35 * (k + 1), "step", skip=("bottom",))
    zf = cz + 0.35 * max(nstep, 1) + 0.3
    ENTRIES.append(["court_front", 0.0, gy(0.0, zf), zf])
    JOINTS.append(["court_steps_foot", 0.0, gfr - 0.15, cz + 0.35 * max(nstep, 1), "stair foot"])
    ENTRIES.append(["court_N", -cx + 0.3, yc, cz - 4.0])
    ENTRIES.append(["court_S", cx - 0.3, yc, cz - 4.0])

    # the shell: a great scallop on a pedestal before the cascade, the rockwork round its foot (plate 10, P0303, P0358, P0753)
    sz = V["terr_z"] + 1.0
    m.box(-0.9, 0.9, yr - 1.1, water_y + 0.9, sz - 0.6, sz + 0.6, "marble")
    shell(0, sz + 0.3, water_y + 0.9, V["shell_w"], V["shell_h"])
    kp("shell_top", (0, water_y + 0.9 + V["shell_h"], sz))
    # the carved column rising from the shell's hinge with a flat round basin above the shell's rim, the jet falling from it (plate 10, the west reader)
    yb_ = water_y + 0.9 + V["shell_h"] + 0.35
    m.lathe([(0.22, water_y + 0.9), (0.18, water_y + 1.6), (0.24, yb_ - 0.3), (0.3, yb_ - 0.15)], 6, "marble", cx=0, cz=sz + 0.1, cap=False)
    m.lathe([(0.3, yb_ - 0.15), (0.75, yb_), (0.8, yb_ + 0.12), (0.0, yb_ + 0.13)], 10, "marble", cx=0, cz=sz + 0.1, cap=False)
    kp("shell_basin_top", (0, yb_ + 0.12, sz + 0.1))
    rng = np.random.default_rng(14)
    for k in range(14):
        a = math.pi * (0.05 + 0.9 * k / 13)
        r = 2.4 + rng.uniform(0, 0.9)
        x, z = r * math.cos(a) * 1.4, sz + 0.4 + r * math.sin(a) * 0.55
        h = rng.uniform(0.4, 1.1)
        m.box(x - 0.45, x + 0.45, water_y - 0.2, water_y + h, z - 0.4, z + 0.4, "rock")
    # the vase fountain on the axis: a tiered basin on a pedestal, its jet into the shell (plate 10)
    vz = V["vase_z"]
    vh = V["vase_h"] / 2.35
    m.lathe([(0.75, yr - 1.1), (0.75, water_y + 0.4 * vh), (0.5, water_y + 0.55 * vh), (0.35, water_y + 1.1 * vh), (0.95, water_y + 1.45 * vh), (1.05, water_y + 1.65 * vh), (0.6, water_y + 1.7 * vh), (0.25, water_y + 1.9 * vh), (0.45, water_y + 2.3 * vh), (0.0, water_y + 2.35 * vh)], 10, "marble", cx=0, cz=vz, cap=False)
    m.flat([(0.9 * math.cos(2 * math.pi * k / 10), vz + 0.9 * math.sin(2 * math.pi * k / 10)) for k in range(10)], water_y + 1.6 * vh, "water")
    P_.jet(0, vz, water_y + V["vase_h"], 3.2, 0.12)  # a plain vertical jet (plate 10)
    kp("vase_top", (0, water_y + V["vase_h"], vz))


def figure(x, z, y, facing, label):
    """One seated figure: a stone pedestal, a robed body as plain forms, a bronze head with a muzzle; no species features beyond the head's mass (simple and factual, the brief)."""
    m.push(x, 0, z, facing)
    m.box(-0.42, 0.42, y, y + 0.35, -0.42, 0.42, "marble")
    yb = y + 0.35
    body_h = V["fig_h"] - V["head_h"]
    # the robe: a seated block widening at the knees, the shoulders narrower
    m.lathe([(0.34, yb), (0.36, yb + 0.35), (0.3, yb + 0.5), (0.26, yb + body_h - 0.1), (0.14, yb + body_h)], 8, "marble", cx=0, cz=-0.05, cap=True)
    m.box(-0.3, 0.3, yb, yb + 0.42, 0.0, 0.42, "marble")  # the knees and the robe's lap, forward
    # the head: bronze, a rounded mass with a forward muzzle, the neck
    yh = yb + body_h
    hh = V["head_h"]
    m.lathe([(0.1, yh - 0.04), (0.11, yh + 0.06), (0.15, yh + 0.14), (0.17, yh + hh * 0.5), (0.14, yh + hh * 0.8), (0.07, yh + hh * 0.97), (0.0, yh + hh)], 10, "bronze", cx=0, cz=-0.02, cap=False)
    # the muzzle: a short tapering form forward and slightly down (the heads all carry one; the species' features are not modelled)
    r0 = [(-0.11, yh + 0.12), (0.11, yh + 0.12), (0.1, yh + 0.3), (-0.1, yh + 0.3)]
    r1 = [(-0.085, yh + 0.1), (0.085, yh + 0.1), (0.08, yh + 0.25), (-0.08, yh + 0.25)]
    z0, z1 = 0.08, 0.24
    for i in range(4):
        a, b = r0[i], r0[(i + 1) % 4]
        c, d = r1[(i + 1) % 4], r1[i]
        m.poly([(a[0], a[1], z0), (b[0], b[1], z0), (c[0], c[1], z1), (d[0], d[1], z1)], "bronze")
    m.poly([(p[0], p[1], z1) for p in r1], "bronze")
    m.pop()
    FIGS.append(label)


FIGS = []


def shell(x, z, y, w, h):
    """The scallop: a fan of ribs rising from the hinge, tilted forward, on a short foot."""
    n = 9
    hinge = (x, y, z)
    rim = []
    for k in range(n + 1):
        a = math.pi * (0.08 + 0.84 * k / n)
        rim.append((x + math.cos(a) * w / 2 * -1, y + math.sin(a) * h, z + 0.4 + 0.35 * math.sin(a)))
    for k in range(n):
        a, b = rim[k], rim[k + 1]
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 0.05, (a[2] + b[2]) / 2 + 0.25)
        m.poly([hinge, a, mid], "marble")
        m.poly([hinge, mid, b], "marble")
    m.poly([hinge, rim[0], (x, y + 0.3, z - 0.3), ], "marble")
    m.poly([hinge, (x, y + 0.3, z - 0.3), rim[-1]], "marble")
    m.lathe([(0.5, y - 0.2), (0.3, y), (0.0, y + 0.05)], 8, "marble", cx=x, cz=z, cap=False)


def pedestals():
    """The two great pedestals at the court's front corners (plate 10; S02 'two great pedestals'): a tapered body on a base, a cornice, a crowning finial."""
    for sx, tag in ((-1, "N"), (1, "S")):
        cx, cz, s = sx * V["ped_x"], V["ped_z"], V["ped_s"] / 2
        y0 = footing(rect(cx - s - 0.3, cx + s + 0.3, cz - s - 0.3, cz + s + 0.3), gy(cx, cz) + 0.5, "marble", name=f"ped_{tag}")
        yb = gy(cx, cz) + 0.5
        top = yb + V["ped_h"]
        m.frustum([(cx - s, cz - s), (cx + s, cz - s), (cx + s, cz + s), (cx - s, cz + s)], [(cx - s * 0.82, cz - s * 0.82), (cx + s * 0.82, cz - s * 0.82), (cx + s * 0.82, cz + s * 0.82), (cx - s * 0.82, cz + s * 0.82)], yb, top - 0.5, "marble")
        for k, (a0, a1) in enumerate(((0, 1), (1, 2), (2, 3), (3, 0))):
            pass
        m.box(cx - s - 0.15, cx + s + 0.15, top - 0.5, top, cz - s - 0.15, cz + s + 0.15, "marble")
        for fn in ("W", "S", "N", "E"):
            off = {"W": (0, s * 0.92), "E": (0, -s * 0.92), "S": (s * 0.92, 0), "N": (-s * 0.92, 0)}[fn]
            face(cx + off[0], cz + off[1], fn)
            m.cls = "doc" if fn in ("W", "N" if sx > 0 else "S") or fn == ("S" if sx > 0 else "N") else "fill"
            P_.cartouche(0, (yb + top) / 2 - 0.2, 1.6, 2.0)
            m.pop()
        m.cls = "doc"
        m.lathe([(s * 0.9, top), (s * 0.7, top + 0.5), (s * 0.55, top + 1.4), (s * 0.3, top + 2.0), (0.25, top + 2.4), (0.0, top + 2.7)], 4, "marble", cx=cx, cz=cz, cap=False)
        kp(f"ped_{tag}_top", (cx, top, cz))


# ---------------------------------------------------------------- the link, the water building, the reservoir, the wheel-house tiers
def link():
    lw, lh, zB = V["link_w"] / 2, V["link_h"], FRAME["zB"]
    z0, z1 = V["wb_z0"], zB
    footing(rect(-lw, lw, z0, z1), 0.4, "marble", name="link")
    m.box(-lw + 0.95, lw - 0.95, 0.4, lh - 0.4, z0, z1, "panel", skip=("bottom", "front", "back"))  # the dark inside behind the arcade's faces
    m.box(-lw - 0.1, lw + 0.1, lh - 0.4, lh, z0, z1, "marble", skip=("bottom",))
    L = z1 - z0
    for side in ("N", "S"):
        # three round arches (plate 11): the one by the water building a door, the other two niches with vases
        face((-lw if side == "N" else lw), (z0 + z1) / 2, side)
        nb = 3
        bb = bays(-L / 2, L / 2, nb)
        hs = [(a + 1.2, b - 1.2, 0.4, lh - 1.0 - (b - a - 2.4) / 2, (b - a - 2.4) / 2) for a, b in bb]
        east = 2 if side == "S" else 0  # in the face frame s runs west on the north face and east on the south face
        P_.wall_holes(-L / 2, L / 2, 0.4, lh - 0.4, hs, "wall", d=0.01)
        for i, h in enumerate(hs):
            if i == east:
                P_.opening(*h, kind="door", frame=0.16, depth=0.5)
            else:
                P_.opening(*h, kind="door", frame=0.16, depth=0.9, bars=False) if False else None
                a0, a1, b0, b1, rise = h
                from model_parts import arc_pts
                pts = arc_pts(a0, a1, b1, rise, 8)
                for x0_, x1_ in ((a0, a0), (a1, a1)):
                    m.poly([(x0_, b0, 0), (x0_, b0, -0.9), (x0_, b1, -0.9), (x0_, b1, 0)], "marble")
                for p0, p1 in zip(pts[:-1], pts[1:]):
                    m.poly([(p0[0], p0[1], 0), (p0[0], p0[1], -0.9), (p1[0], p1[1], -0.9), (p1[0], p1[1], 0)], "marble")
                m.poly([(a0, b0, -0.9), (a1, b0, -0.9), (a1, b1, -0.9), (a0, b1, -0.9)], "panel")
                c = ((a0 + a1) / 2, b1)
                for p0, p1 in zip(pts[:-1], pts[1:]):
                    m.poly([(c[0], c[1], -0.9), (p1[0], p1[1], -0.9), (p0[0], p0[1], -0.9)], "panel")
                m.box((a0 + a1) / 2 - 0.4, (a0 + a1) / 2 + 0.4, b0, b0 + 0.6, -0.85, -0.25, "marble")
                P_.urn((a0 + a1) / 2, -0.55, b0 + 0.6, 1.2) if False else m.lathe([(0.2, b0 + 0.6), (0.38, b0 + 1.0), (0.3, b0 + 1.5), (0.15, b0 + 1.7), (0.0, b0 + 1.9)], 8, "marble", cx=(a0 + a1) / 2, cz=-0.55, cap=False)
        for a, b in bb:
            P_.pilaster(a, 0.4, lh - 0.4, w=0.55, out=0.22)
        P_.pilaster(L / 2, 0.4, lh - 0.4, w=0.55, out=0.22)
        m.pop()
    P_.rail([(-lw + 0.15, z0 + 0.3), (-lw + 0.15, z1 - 0.3)], lh)
    P_.rail([(lw - 0.15, z0 + 0.3), (lw - 0.15, z1 - 0.3)], lh)
    # a flight on the link's roof rising east to the water building's roof terrace, at the west tier's door (plate 11: the balustrade sloping up at the link's east end)
    Hr = V["Hr"]
    n = int(round((Hr - lh) / 0.16))
    run = n * 0.3
    for k in range(n):
        za, zb = z0 + run * (n - k - 1) / n, z0 + run * (n - k) / n
        m.box(-1.3, 1.3, lh, lh + (Hr - lh) * (k + 1) / n, za, zb, "step", skip=("bottom",))
    for sx in (-1, 1):
        P_.rail([(sx * 1.45, z0 + run), (sx * 1.45, z0 + 0.1)], [lh, Hr], posts=2.2)
    kp("link_rail_S", (lw - 0.15, lh + V["rail"], z1 - 0.3))
    kp("link_rail_N", (-lw + 0.15, lh + V["rail"], z1 - 0.3))


def water_building():
    z0, z1, Hr = V["wb_z0"], V["wb_z1"], V["Hr"]
    hwr, pj = V["wb_w"] / 2, V["wb_proj"]
    L = z0 - z1
    nb = V["wb_bays"]
    bw = L / nb
    e3 = 3 * bw
    # the plan: the middle at ±hwr, the end sections at ±(hwr + pj)
    secs = [(z0 - e3, z0, hwr + pj, "W"), (z1 + e3, z0 - e3, hwr, "M"), (z1, z1 + e3, hwr + pj, "E")]
    for za, zb, hx, tag in secs:
        footing(rect(-hx, hx, za, zb), 0.45, "marble", name=f"wb_{tag}")
        m.box(-hx, hx, Hr - 0.02, Hr, za, zb, "lead", skip=("bottom",))
    # the two long fronts: thirteen bays, pilasters, tall windows under oval cartouches, doors in the middle of each end section and on the axis (plates 11 and 13)
    for side, sx in (("N", -1), ("S", 1)):
        m.cls = "doc"
        for za, zb, hx, tag in secs:
            face(sx * hx, (za + zb) / 2, side)
            hl = (zb - za) / 2
            nsec = int(round((zb - za) / bw))
            cs = [-hl + bw * (i + 0.5) for i in range(nsec)]
            # in the face frame, s runs along the face; for the north face (rot -pi/2) s = -z, for the south s = z
            doors = []
            hs = []
            for i, c in enumerate(cs):
                if (tag in ("W", "E") and i == 1) or (tag == "M" and i == nsec // 2):
                    hs.append((c - 0.95, c + 0.95, 0.45, V["wb_door"] - 0.95, 0.95))
                    doors.append(len(hs) - 1)
                else:
                    hs.append((c - 0.5, c + 0.5, 1.5, V["wb_door"] + 0.2, 0.0))
            P_.wall_holes(-hl, hl, 0.45, Hr - 1.0, hs, "wall")
            for i, h in enumerate(hs):
                if i in doors:
                    P_.opening(*h, kind="door", frame=0.2, head=None)
                    P_.cartouche((h[0] + h[1]) / 2, V["wb_door"] + 1.1, 1.2, 0.6)
                else:
                    P_.opening(*h, kind="win", frame=0.15, head="oval")
            for k in range(nsec + 1):
                P_.pilaster(-hl + k * bw, 0.45, Hr - 1.0, w=0.45, out=0.2)
            P_.entablature(-hl, hl, Hr, h=1.0, out=0.4)
            m.pop()
            for i, c in enumerate(cs):
                if (tag in ("W", "E") and i == 1) or (tag == "M" and i == nsec // 2):
                    zz = (za + zb) / 2 + (c if side == "S" else -c)
                    ENTRIES.append([f"wb_door_{side}{tag}", sx * (hx + 0.6), gy(sx * (hx + 0.6), zz), zz])
                    kp(f"wb_door_{side}{'C' if tag == 'M' else tag}_head", (sx * (hx + 0.05), V["wb_door"], zz))
        # the end sections' return faces (the slight projection)
        for za, zb in ((z0 - e3, z0 - e3), (z1 + e3, z1 + e3)):
            pass
        for zz, sg in ((z0 - e3, -1), (z1 + e3, 1)):
            x0, x1 = sorted((sx * hwr, sx * (hwr + pj)))
            m.poly([(x0, 0.45, zz), (x1, 0.45, zz), (x1, Hr, zz), (x0, Hr, zz)], "wall")
        # roof balustrade with urns over the pilasters (plates 11 and 13)
        pts = [(sx * (hwr + pj - 0.2), z0 - 0.2), (sx * (hwr + pj - 0.2), z0 - e3), (sx * (hwr - 0.2), z0 - e3), (sx * (hwr - 0.2), z1 + e3), (sx * (hwr + pj - 0.2), z1 + e3), (sx * (hwr + pj - 0.2), z1 + 0.2)]
        P_.rail(pts, Hr, posts=bw)
        for k in range(nb + 1):
            zz = z0 - k * bw
            xx = sx * ((hwr + pj if (k <= 3 or k >= nb - 3) else hwr) - 0.2)
            P_.urn(xx, zz, Hr + V["rail"] + 0.06, 0.7)
        for tz, zz in (("W", z0), ("E", z1)):
            kp(f"wb_foot_{side}{tz}", (sx * (hwr + pj), max(0.0, gy(sx * (hwr + pj), zz)), zz), anchor=True)
            kp(f"wb_cornice_{side}{tz}", (sx * (hwr + pj + 0.4), Hr, zz + (0.4 if tz == "W" else -0.4)))
            kp(f"wb_rail_{side}{tz}", (sx * (hwr + pj - 0.2), Hr + V["rail"], zz + (-0.2 if tz == "W" else 0.2)))
    # the west face (against the link: no picture, carried round) and the east face (behind the east block)
    m.cls = "fill"
    face(0, z0, "W")
    hx = hwr + pj
    lw = V["link_w"] / 2
    hs = [(c - 0.5, c + 0.5, 1.5, Hr - 3.0, 0) for c in (-hx + 2.5, -hx + 5.5, hx - 5.5, hx - 2.5)]
    P_.wall_holes(-hx, hx, 0.45, Hr - 1.0, hs, "wall")
    for h in hs:
        P_.opening(*h, kind="win", frame=0.15)
    P_.entablature(-hx, hx, Hr, h=1.0, out=0.4)
    m.pop()
    face(0, z1, "E")
    P_.wall_holes(-hx, hx, 0.45, Hr - 1.0, [], "wall")
    m.pop()
    m.cls = "doc"
    # the reservoir 锡海 on the roof between the two raised tiers: 27.36 x 5.92 m inside, 1.44 m of water; its parapet walls (fill: no picture shows it whole)
    tl, tw, td, tk = V["tank_l"], V["tank_w"], V["tank_d"], V["tank_wall"]
    zc = (z0 + z1) / 2
    m.cls = "fill"
    y_floor = Hr + 0.1
    y_top = y_floor + td + 0.25
    ox, oz = tw / 2 + tk, tl / 2
    # the long walls; its ends are the raised tiers' inner walls (27.36 + 2 x 5.5 = 38.4 m, the range)
    m.prism(rect(-ox, ox, zc - oz, zc + oz), Hr, y_top, "rustic", top=False)
    m.flat(rect(-ox, -tw / 2, zc - oz, zc + oz), y_top, "marble")
    m.flat(rect(tw / 2, ox, zc - oz, zc + oz), y_top, "marble")
    # inner faces of the tin-lined basin and its water
    for x0, x1, za, zb in ((-tw / 2, tw / 2, zc - oz, zc - oz), (-tw / 2, tw / 2, zc + oz, zc + oz)):
        m.poly([(x0, y_floor, za), (x1, y_floor, za), (x1, y_top, za), (x0, y_top, za)], "lead")
    for xx in (-tw / 2, tw / 2):
        m.poly([(xx, y_floor, zc - oz), (xx, y_floor, zc + oz), (xx, y_top, zc + oz), (xx, y_top, zc - oz)], "lead")
    m.flat(rect(-tw / 2, tw / 2, zc - oz, zc + oz), y_floor + td * 0.85, "water")
    m.cls = "doc"
    kp("tank_top_W", (0, y_top, zc + oz))
    # the raised wheel-house tiers at both ends of the roof (plates 11, 12, 13): walls with a window or door, pilasters, a hip roof
    lz, lx = V["pav_lz"] / 2, V["pav_lx"] / 2
    ye = Hr + V["pav_eave"]
    for tag, zp in (("W", z0 - V["pav_lz"] / 2), ("E", z1 + V["pav_lz"] / 2)):
        lx = V["pav_lx"] / 2 if tag == "E" else V["pavW_lx"] / 2  # the east tier a hall running N-S, the west one about square (plates 11, 13: the sides reader)
        m.prism(rect(-lx, lx, zp - lz, zp + lz), Hr, Hr + 0.3, "marble", top=False)
        for side in ("N", "S", "E", "W"):
            outer = side in ("N", "S") or (side == tag)
            m.cls = "doc" if (side in ("N", "S") or (tag == "E" and side == "E")) else "fill"
            if side in ("N", "S"):
                face((-lx if side == "N" else lx), zp, side)
                hl = lz
            else:
                face(0, zp + (lz if side == "W" else -lz), side)
                hl = lx
            if side in ("N", "S"):
                hs = [(-0.75, 0.75, Hr + 0.5, ye - 1.2, 0.0)]
            elif outer:
                hs = [(-hl + 1.0, -hl + 2.3, Hr + 0.5, ye - 1.2, 0.0), (-0.75, 0.75, Hr + 0.3, ye - 0.9, 0.0), (hl - 2.3, hl - 1.0, Hr + 0.5, ye - 1.2, 0.0)]
            else:
                hs = [(-0.75, 0.75, Hr + 0.3, ye - 0.9, 0.0)]
            P_.wall_holes(-hl, hl, Hr, ye - 0.6, hs, "wall")
            for i, h in enumerate(hs):
                door = (len(hs) == 3 and i == 1) or (not outer and side not in ("N", "S"))
                P_.opening(*h, kind="door" if door else "win", frame=0.16, head="cornice" if not door else None)
            for s in (-hl + 0.3, hl - 0.3):
                P_.pilaster(s, Hr, ye - 0.6, w=0.5, out=0.25)
            P_.entablature(-hl, hl, ye, h=0.6, out=0.35)
            m.pop()
        m.cls = "doc"
        r = P_.roof_hip(0, zp, lx + 0.8, lz + 0.8, ye + 0.05, V["pav_ridge"] - 0.35, along="x", doc={"N", "S", "E", "W"})
        e = r["ridge"]
        kp(f"wbpav_{tag}_ridge", ((e[0][0] + e[1][0]) / 2, e[0][1], zp))
        for (ex, ez), p in r["eaves"].items():
            kp(f"wbpav_{tag}_eave_{'S' if ex > 0 else 'N'}{'W' if ez > 0 else 'E'}", p)
    # the roof terrace's paving between the tiers and the tank
    FRAME["Hr"] = Hr


# ---------------------------------------------------------------- the east block with the zig-zag stairs (plate 12)
def east_block():
    """Plate 12 (the east reader): four flights a side. Flight 1 from the court beside the passage door outward to the lowest landing L1 at the outer corner; flight 2 back inward to a
    half-landing L2 beside the door's crest; flight 3 outward to L3 at the outer end; flight 4, long, inward to the top on the axis before the raised hall. The four stand one behind the other."""
    Hr, R = V["Hr"], V["rail"]
    hx = V["eb_w"] / 2
    z1, z0 = V["eb_z1"], V["wb_z1"]
    fw = V["fl_w"]
    cw = V["es_door_w"] / 2 + 0.7  # the centre bay with the door and its crest
    hl2 = cw + 2.2  # the half-landings L2 from cw to hl2
    xo = hx - 2.65  # the outer landings from xo to hx
    zA, zB_, zC, zD, zE = (z1 + k * fw for k in range(5))  # F1 zA..zB, F2 zB..zC, F3 zC..zD, F4 zD..zE
    L1, L2, L3 = V["L1"], V["L2"], V["L3"]
    # the platform behind, at the water building's roof, and the outer and centre masses
    footing(rect(-hx, hx, zE, z0), Hr, "rustic", name="eb_top")
    m.box(-hx, hx, Hr - 0.02, Hr, zE, z0, "pave", skip=("bottom",))
    for sx in (-1, 1):
        t = "N" if sx < 0 else "S"
        x0, x1 = sorted((sx * xo, sx * hx))
        footing(rect(x0, x1, zA, zC), L1, "rustic", name=f"eb_L1{t}", corners=False)
        footing(rect(x0, x1, zC, zE), L3, "rustic", name=f"eb_L3{t}", corners=False)
        h0, h1 = sorted((sx * cw, sx * hl2))
        footing(rect(h0, h1, zB_, zD), L2, "rustic", name=f"eb_L2{t}", corners=False)
        JOINTS.append([f"eb_corner_{t}E", sx * hx, gy(sx * hx, zA) - 0.15, zA, "wall foot"])
        # the side face's panels (plates 11 and 13 at the far end: large carved panels)
        face(sx * hx, (zA + zC) / 2, t)
        P_.cartouche(0, L1 * 0.5, (zC - zA) * 0.6, L1 * 0.55)
        m.pop()
        face(sx * hx, (zC + zE) / 2, t)
        P_.cartouche(0, L3 * 0.5, (zE - zC) * 0.6, L3 * 0.5)
        m.pop()
        face(sx * hx, (zE + z0) / 2, t)
        P_.cartouche(0, Hr * 0.5, (z0 - zE) * 0.6, Hr * 0.45)
        P_.entablature(-(z0 - zE) / 2, (z0 - zE) / 2, Hr, h=0.5, out=0.3)
        m.pop()
    # the centre: the passage door with its crest rising in front of a plain wall (plate 12; the plan's E-W passage), the top landing behind
    footing(rect(-cw, cw, zA, zD), L2 + 1.0, "rustic", name="eb_centre", corners=False)
    footing(rect(-cw, cw, zD, zE), Hr, "rustic", name="eb_top_c", corners=False)
    yb = gy(0, zA) - 0.15
    face(0, zA, "E")
    dw = V["es_door_w"] / 2
    ys_ = V["es_door"] - dw  # the arch's springing
    m.poly([(-dw, 0.0, 0.01), (dw, 0.0, 0.01), (dw, ys_, 0.01), (-dw, ys_, 0.01)], "door")
    from model_parts import arc_pts
    arc = arc_pts(-dw, dw, ys_, dw, 8)
    for p0, p1 in zip(arc[:-1], arc[1:]):
        m.poly([(0, ys_, 0.01), (p0[0], p0[1], 0.01), (p1[0], p1[1], 0.01)], "door")
    for s_ in (-dw - 0.25, dw + 0.25):
        P_.pilaster(s_, 0.0, V["es_door"] + 0.2, w=0.4, out=0.2)
    m.box(-dw - 0.5, dw + 0.5, V["es_door"] + 0.2, V["es_door"] + 0.55, 0, 0.35, "marble", skip=("back",))
    P_.cartouche(0, (V["es_door"] + 0.55 + L2 + 1.0) / 2, 1.5, max(0.4, L2 + 1.0 - V["es_door"] - 0.55 - 0.3))
    m.poly([(-1.0, L2 + 1.0, 0.05), (1.0, L2 + 1.0, 0.05), (0.0, L2 + 1.8, 0.05)], "marble")  # the crest's top
    m.pop()
    kp("es_door_head", (0, V["es_door"], zA - 0.05))
    ENTRIES.append(["es_door", 0.0, gy(0, zA - 0.8), zA - 0.8])
    JOINTS.append(["es_door_sill", 0.0, yb, zA, "wall foot"])

    def flight(xa, xb, ya, yb_, za, zb):
        """A flight along x from (xa, ya) to (xb, yb_), between za and zb; solid below each tread."""
        n = max(2, int(round(abs(yb_ - ya) / 0.155)))
        lo = gy(xa, (za + zb) / 2) - 0.15
        for k in range(n):
            x0 = xa + (xb - xa) * k / n
            x1 = xa + (xb - xa) * (k + 1) / n
            lo_k = min(gy(x0, za), gy(x1, za), gy(x0, zb), gy(x1, zb)) - 0.15
            y = ya + (yb_ - ya) * (k + 1) / n
            m.box(min(x0, x1), max(x0, x1), lo_k, y, za, zb, "step", skip=("bottom",))
        FOOTPRINTS.append(rect(min(xa, xb), max(xa, xb), za, zb))
        return lo

    for sx, tag in ((-1, "N"), (1, "S")):
        g0 = gy(sx * cw, zA - 0.5)
        lo = flight(sx * cw, sx * xo, g0, L1, zA, zB_)
        flight(sx * xo, sx * hl2, L1, L2, zB_, zC)
        flight(sx * hl2, sx * xo, L2, L3, zC, zD)
        flight(sx * xo, sx * cw, L3, Hr, zD, zE)
        face(sx * (cw + xo) / 2, zA, "E")
        P_.cartouche(0, max(0.9, (g0 + L1) / 3), 2.6, 1.1)
        m.pop()
        # the walls showing above each lower flight carry large carved panels (plate 12)
        for zz, ylo, yhi in ((zB_, (g0 + L1) / 2, (L1 + L2) / 2), (zC, (L1 + L2) / 2, (L2 + L3) / 2), (zD, (L2 + L3) / 2, (L3 + Hr) / 2)):
            if yhi - ylo > 0.7:
                face(sx * (cw + xo) / 2 + sx * 0.6, zz, "E")
                P_.cartouche(0, (ylo + yhi) / 2 + 0.25, 2.2, (yhi - ylo) * 0.55)
                m.pop()
        # balustrades along each flight's front edge (sloping), the landings' outer edges, the top
        P_.rail([(sx * (cw + 0.2), zA + 0.2), (sx * (xo - 0.1), zA + 0.2)], [g0 + 0.1, L1], posts=2.2)
        P_.rail([(sx * (xo + 0.1), zA + 0.2), (sx * (hx - 0.2), zA + 0.2), (sx * (hx - 0.2), zC - 0.2)], L1, posts=2.2)
        P_.rail([(sx * (xo - 0.1), zB_ + 0.2), (sx * (hl2 + 0.1), zB_ + 0.2)], [L1, L2], posts=2.2)
        P_.rail([(sx * (hl2 - 0.1), zB_ + 0.2), (sx * (cw + 0.2), zB_ + 0.2)], L2, posts=2.2)
        P_.rail([(sx * (hl2 + 0.1), zC + 0.2), (sx * (xo - 0.1), zC + 0.2)], [L2, L3], posts=2.2)
        P_.rail([(sx * (xo + 0.1), zC + 0.2), (sx * (hx - 0.2), zC + 0.2), (sx * (hx - 0.2), zE - 0.2)], L3, posts=2.2)
        P_.rail([(sx * (xo - 0.1), zD + 0.2), (sx * (cw + 0.2), zD + 0.2)], [L3, Hr], posts=2.2)
        P_.rail([(sx * (hx - 0.2), zE + 0.2), (sx * (hx - 0.2), z0 + 0.2)], Hr, posts=2.2)
        for y, zz in ((L1, zA + 0.2), (L3, zC + 0.2)):
            P_.urn(sx * (hx - 0.2), zz, y + R + 0.06, 0.8)
        kp(f"es_L1_rail_{tag}", (sx * (hx - 0.2), L1 + R, zA + 0.2))
        kp(f"es_L3_rail_{tag}", (sx * (hx - 0.2), L3 + R, zC + 0.2))
        kp(f"es_foot_{tag}", (sx * cw, g0, zA), anchor=True)
        kp(f"es_corner_{tag}E_foot", (sx * hx, max(0.0, gy(sx * hx, zA)), zA), anchor=True)
        JOINTS.append([f"es_F1_foot_{tag}", sx * (cw + 0.3), lo, zA, "stair foot"])
        ENTRIES.append([f"es_F1_foot_{tag}", sx * (cw + 0.4), g0, zA - 0.6])
    # the short balustrade on the axis at the top, before the raised hall (plate 12)
    P_.rail([(-cw + 0.2, zD + 0.2), (cw - 0.2, zD + 0.2)], Hr, posts=1.6)
    kp("es_top_rail_C", (0, Hr + R, zD + 0.2))


def reset(over=None):
    """The figures, with some overridden (measure.py varies them)."""
    V.clear()
    V.update({k: v[0] for k, v in P.items()})
    V.update(over or {})


def load():
    """The ground and the frame, once."""
    global G
    if G is None:
        G = NewGround(ROOT)
        pos, rot = frame()
        FRAME.update({"pos": pos, "rot": rot})


def build():
    global m, P_
    m = Mesh(COL)
    P_ = Parts(m, rail_h=V["rail"], baluster_segs=4)
    KP.clear()
    JOINTS.clear()
    ENTRIES.clear()
    FOOTPRINTS.clear()
    FIGS.clear()
    m.cls = "doc"
    west_block()
    m.cls = "doc"
    terrace_and_stairs()
    figures_and_pool()
    pedestals()
    m.cls = "doc"
    link()
    water_building()
    m.cls = "doc"
    east_block()


def main():
    load()
    pos, rot = FRAME["pos"], FRAME["rot"]
    reset()
    build()
    size = m.write_glb(HERE / "model.glb", "XY08 海晏堂 Haiyantang", extras={"id": "XY08"})
    tris = m.count()
    prims = {k: len(v["idx"]) // 3 for k, v in sorted(m.prims.items())}
    fill = sum(n for k, n in prims.items() if k.endswith("~fill"))
    params = {k: {"value": v[0], "source": v[1], "grade": v[2], "note": v[3]} for k, v in P.items()}
    json.dump({"id": "XY08", "frame": "x south along the west front, y up from the west block's base, z west (out of the front); metres", "params": params}, open(HERE / "params.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    pts = {}
    for k, v in KP.items():
        if "p" in v:
            pts[k] = {"local": v["p"], "scene": to_scene(v["p"]), "anchor": v.get("anchor", False)}
        else:
            pts[k] = {"cands": [{"scene": to_scene(c["p"])} for c in v["cands"]], "pick": v["pick"], "anchor": v.get("anchor", False)}
    objects = ["XY08", "XY08-01", "XY08-02", "XY08-N01", "XY08-N02", "XY08-N03", "XY08-AX001"]
    json.dump({"id": "XY08", "objects": objects, "position": pos, "rotationY": rot, "points": pts}, open(HERE / "keypoints.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump({"id": "XY08", "position": pos, "rotationY": rot,
               "joints": [{"name": j[0], "scene": to_scene(j[1:4]), "kind": j[4]} for j in JOINTS],
               "entries": [{"name": e[0], "scene": to_scene(e[1:4])} for e in ENTRIES],
               "footprints": [[to_scene((x, 0.0, z))[::2] for x, z in fp] for fp in FOOTPRINTS]},
              open(HERE / "joints.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    summary_write(pos, rot, tris, fill, size)
    print(f"model.glb {size / 1e6:.2f} MB, {tris} triangles ({fill} fill), {P_.balusters} balusters, {len(KP)} key points, {len(JOINTS)} joints, {len(ENTRIES)} entries; position {pos} rotY {rot}")


def summary_write(pos, rot, tris, fill, size):
    W, H1, H2 = V["W"], V["H1"], V["H2"]
    summary = {
        "id": "XY08", "aliases": ["XY08-01", "XY08-02", "XY08-N01", "XY08-N02", "XY08-N03", "XY08-AX001"], "name": "海晏堂 Haiyantang", "glb": "model.glb", "position": pos, "rotationY": rot,
        "line": "Modelled from the four plates of 1783-86 (10 west, 11 north, 12 east, 13 south), Ohlmer's photograph of the west front of 1873 and the ruin photographs of about 1902-1920, the plan S01 and the ruin's footprint; every figure is a reading (C) unless the row says otherwise. Faces no picture shows (the stairs' outer walls, the reservoir on the roof, the west wheel house's west face) are carried round from the documented parts (assumed).",
        "rows": [],
        "caption": {"frontage_m": W, "depth_m": round(V["D"], 1), "eave_m": H2, "ridge_m": V["ridge_pav"], "assumed": True, "confidence": "C"},
        "hides": [],
        "tris": tris, "fill_tris": fill, "glb_bytes": size,
    }
    summary["rows"] = rows()
    json.dump(summary, open(HERE / "summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def rows():
    W, H1, H2 = V["W"], V["H1"], V["H2"]
    return [
        ["West block", f"{W:g} m along the west front, eleven bays on two storeys (S310, B): upper floor and terrace at {H1:g} m, cornice {H2:g} m, end pavilions under square roofs to {V['ridge_pav']:g} m, the attic's pediment {V['ped_apex']:g} m (plate 10, C)"],
        ["Stairs", f"two diagonal flights {V['st_w']:g} m wide from the terrace to the court, a landing half-way, carved balustrades (plate 10, C); in plan S01's stair blocks (B)"],
        ["Water clock 十二时辰水法", f"the pool between the stairs with a convex front (S01's slip, plate 10, C); twelve seated figures with bronze heads about {V['head_h']:g} m high (S849, B) on plinths {V['plinth_h']:g} m high, six a side; south 鼠 虎 龙 马 猴 狗, north 牛 兔 蛇 羊 鸡 猪 (S823, C); the great shell and the vase fountain on the axis (plate 10, P0303, C)"],
        ["Where the heads are", "seven are in China: ox, tiger, monkey and boar at the Poly Art Museum; horse at the garden since 2020; rat and hare at the National Museum since 2013. Dragon, snake, goat, rooster and dog: whereabouts unknown (S822, S823, S817)"],
        ["Water building 蓄水楼", f"thirteen bays, {V['wb_z0'] - V['wb_z1']:.1f} m, its cornice and roof terrace at {V['Hr']:g} m (plates 11-13, C); the reservoir 锡海 {V['tank_l']:g} × {V['tank_w']:g} m, {V['tank_d']:g} m deep (S310, S06, B; S600, A) on the roof between two raised tiers with hip roofs to {V['pav_ridge']:g} m (plates 11, 12, C)"],
        ["East stairs", f"three flights in a zig-zag to landings at {V['L1']:g}, {V['L2']:g} and {V['Hr']:g} m over the passage door (plate 12, C)"],
        ["Colours", "white stone, light wall panels, peacock-green glazed tiles with yellow ridges (S310, B, as said of the wing roofs), red-brown bronze heads (S823)"],
    ]


if __name__ == "__main__":
    main()
