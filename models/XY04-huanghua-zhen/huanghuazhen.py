#!/usr/bin/env python3
"""黄花阵 Huanghua Zhen (XY04), the maze of the Xiyang Lou, the twelfth detailed model (Round 26): the carved-brick walls of the maze as S01 draws them, set into the block of
S310 (58.56 x 88.64 m) where today's rebuilt maze stands; the outer wall with the side gates and their finial piers; the clipped trees on the walls and the four weeping
pagoda trees in their circles; in the middle the drum with the straight flight, the two curved flights behind their parapet, and the octagonal pavilion with its arches,
skirt roof, dome and lantern (XY04-01); the north hall (XY04-N01) with its terrace and flight, and the small basin before it (plate 5; S01; S310; S258; S02).
Plain geometry, one GLB (scripts/model_mesh.py) with every figure in params.json; the method is the pilot's (models/XY01-xieqiqu/README.md).

  uv run python models/XY04-huanghua-zhen/trace_maze.py   (only to re-read S01: needs research/raw/; writes plan_readings.csv)
  uv run python models/XY04-huanghua-zhen/huanghuazhen.py

Writes, beside this file: model.glb, params.json, keypoints.json, joints.json, summary.json, report.json (models/README.md).
Frame (scripts/model_site.py): origin at the middle of the south wall's box XY04-M10 on its centre line, at that box's ground; x east along the south wall, y up, z south.
The block runs from z 0 (the south wall) to z -88.64 (the north wall), x -29.28 to 29.28 (the wall boxes of Round 6, which follow S310 and the rebuilt maze, Q66).
The plan's lines (plan_readings.csv, plan pixels of S01) are mapped onto the block by the outer wall's rectangle: S01 draws the maze 73.7 x 99.3 m, S310 gives 58.56 x 88.64 m,
so the pattern is S01's and the size S310's (Q292).
Grades: what plate 5 shows is `doc` (the walls, their trees, the gates, the drum and its flights, the pavilion's front, the hall's roof); the maze's paving, the hall's
walls and back, the pavilion's back and the parts no picture shows are `fill` (assumed, C). Every figure is C unless params.json says otherwise.
"""

import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from model_mesh import Mesh  # noqa: E402
from model_parts import Parts  # noqa: E402
from model_site import Site  # noqa: E402

P = {
    "block_w": (58.56, "S310;S850", "B", "the maze block E-W, 183 尺 (S310, a lead with no survey cited: method e); today's rebuilt maze 55.5-58.7 m (S850, b); the wall boxes of Round 6"),
    "block_d": (88.64, "S310;S850", "B", "the block N-S, 277 尺 (S310, e); today's rebuild 88.4-89.5 m (S850, b)"),
    "plan_rect": ("8706 415 9056 888", "S01", "C", "the outer wall on S01 in plan px (W N E S), the middle of its double line: 73.7 x 99.3 m at the plan's scale; mapped onto the block (Q292)"),
    "wall_h": (1.2, "S310;S02", "B", "the maze walls: 阵墙高约1.20米 (S310, e); Malone 'about shoulder high' (S02 p.145)"),
    "wall_t": (0.6, "S310", "B", "宽约0.60米 (S310, e)"),
    "owall_h": (1.5, "S71", "C", "the outer wall, drawn taller and thicker than the maze walls on plate 5 (the near wall with its base course); assumed"),
    "owall_t": (0.8, "S71", "C", "the outer wall's thickness: plate 5 draws its top wider than the maze walls'; assumed"),
    "band": ("0.30-0.95", "S310;S71", "C", "the carved band of 卐字不断 brick on both faces (S310; plate 5 draws fret and wave-scroll bands): drawn as a framed band of raised keys, no texture"),
    "topiary_step": (5.5, "S71;S310", "C", "the clipped three-tier trees on the walls (plate 5; S310 'three-tier clipped trees on the wall on the plates'): one every 5.5 m along a wall, their spacing read roughly on plate 5"),
    "gate_side_w": (2.6, "S71;S01", "C", "the side gates' openings in the west and east walls: S01's dotted path through the wall at y 672-692 px; plate 5 draws two finial piers and iron leaves"),
    "pier_h": (3.0, "S71", "C", "the side gates' piers to the cap; a pineapple finial of 1.0 m above (plate 5, by the walls' height)"),
    "drum_r": (6.0, "S71;S01", "C", "the drum's radius: plate 5 285 px against the maze's 1315 px at that depth (12.7 m on the block's 58.56), S01's inner circle about 6 m"),
    "ring_r": (8.6, "S01;S71", "C", "the ring of steps' outer radius: S01 100 px (16.7-18.7 m on the block), plate 5 419 px of 1315 (18.7 m)"),
    "drum_h": (3.8, "S71", "C", "the drum's top above the ground: plate 5, 105 px against the pavilion's width 132 px, with the plate's heights about 1.45 times its widths (Q219) and the view from above"),
    "landing_h": (0.75, "S71;S01", "C", "the landing before the drum: the straight flight S01 draws south of the ring (three rungs), five steps on plate 5"),
    "flight_end": (170.0, "S71", "C", "the curved flights run from the landing round both sides to meet behind the drum at its top, degrees from the south: plate 5 shows them climbing behind the parapet"),
    "parapet_h": (0.55, "S71", "C", "the curved parapet's solid part above the treads, its balustrade above: plate 5"),
    "rail_h": (0.9, "S71", "C", "balustrades: the parapet's, the drum's top"),
    "pav_w": (6.4, "S01;S71;S03", "C", "the pavilion across its large faces: S01's octagon 36 px (6.4 m on the block), plate 5 137 px of 1315 (6.1 m); today's redesigned pavilion 6.57 m (S03, B, not the original)"),
    "pav_chamfer": (1.4, "S258;S01", "C", "an octagon of four large faces (arches) and four small ones (windows): S258's description; the small faces 2.0 m"),
    "col_h": (5.2, "S71", "C", "the pavilion's columns from the drum's top to their capitals: plate 5, 143 px, at the drum's reading"),
    "ent_top": (6.1, "S71", "C", "the entablature's top above the drum: plate 5, 175 px"),
    "eave_r": (5.35, "S71", "C", "the skirt roof's eave radius: plate 5 240 px of 1315 (10.7 m across)"),
    "eave_y": (6.3, "S71", "C", "the skirt's eave above the drum: plate 5, 210 px"),
    "dome_base": (7.6, "S71", "C", "the dome's foot above the drum: plate 5, 240 px"),
    "dome_top": (10.6, "S71;S258", "C", "the dome's top (a 'cul-de-four', S258) above the drum: plate 5, 330 px"),
    "lantern_top": (11.8, "S71", "C", "the open lantern's roof above the drum: plate 5, 365 px"),
    "finial_top": (12.9, "S71", "C", "the ball finial's top above the drum: plate 5, 405 px"),
    "hall_w": (14.9, "S01", "C", "the north hall's front: S01's grid 89 px (18.7 m at the plan's scale), on the block 14.9 m; plate 5 reads 18.1 m on the block's width"),
    "hall_d": (10.1, "S01", "C", "its depth: S01 54 px on the block"),
    "hall_eave": (7.0, "S02;S71", "C", "two storeys (S02 p.145, B); the eave a guess from plate 5, where only its roof and upper wall show over the pavilion"),
    "hall_ridge": (9.6, "S71", "C", "the ridge: a gable roof with its ridge over the whole length and finials on its ends (plate 5)"),
    "hall_plat": (0.6, "S01", "C", "the hall's platform and terrace; S01 draws flights on its south side"),
    "basin_r": (3.3, "S01", "C", "the half-round basin with wave marks below the north wall's bow on S01 (34-40 px): a small pool, C"),
    "tree_crown": (3.4, "S310;S71", "C", "the four weeping pagoda trees 龙爪槐 in their tree circles at the inner corners (S310; plate 5 draws four umbrella crowns); their places the four rounded beds S01 draws, the crown's size assumed"),
}
V = {k: v[0] for k, v in P.items()}
import os as _os  # a test of Q292 only (Round 26): R26_BLOCK="73.7 99.3" draws the block at S01's size; never set for the model
if _os.environ.get("R26_BLOCK"):
    V["block_w"], V["block_d"] = (float(v) for v in _os.environ["R26_BLOCK"].split())


COL = {
    "brick": "#a7a49c", "carved": "#8d8a83", "coping": "#bdb9ae", "marble": "#ebe6da", "wall": "#e2dccf", "panel": "#c9c2b2", "sculpt": "#d9d3c5",
    "glass_win": "#2e4a4f", "door": "#4a3b2c", "roof": "#3f7f6c", "roofedge": "#336a5b", "ridge": "#c9a245", "gilt": "#b59a52", "iron": "#2f302f",
    "pave": "#c8bea6", "step": "#d2ccbe", "topiary": "#4e6a3a", "tree": "#5b7a45", "trunk": "#5a4634", "water": "#6f9fb0", "earth": "#8a7f6c",
}

S = None
m = None
P_ = None
X_AX = 0.0
C = (0.0, 0.0)
REPORT = {}


def rect(x0, x1, z0, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


# ------------------------------------------------------------------ the plan
def readings():
    return list(csv.DictReader(open(HERE / "plan_readings.csv", encoding="utf-8")))


def plan_map():
    W_, N_, E_, S_ = (float(v) for v in V["plan_rect"].split())
    sx, sz = V["block_w"] / (E_ - W_), V["block_d"] / (S_ - N_)
    return lambda px, py: (-V["block_w"] / 2 + (px - W_) * sx, -(S_ - py) * sz)


def pts_of(row):
    return [tuple(float(v) for v in p.split()) for p in row["points_px"].split(";")]


# ------------------------------------------------------------------ walls
def wall_line(pts, H, t, name, carved=True, topiary=True, caps=(True, True), tree_from=2.0):
    """A wall along a polyline in the frame: the body from just below the ground to H above it, a coping, on both faces a carved band (a frame and raised keys), clipped
    trees on top every topiary_step m. Its ends are joints."""
    n = len(pts)
    gys = [S.gy(x, z) for x, z in pts]
    segs = []
    for i in range(n - 1):
        (ax, az), (bx, bz) = pts[i], pts[i + 1]
        L = math.hypot(bx - ax, bz - az)
        if L < 0.05:
            continue
        segs.append((i, ax, az, bx, bz, L))
    acc = 0.0
    next_tree = tree_from
    for k, (i, ax, az, bx, bz, L) in enumerate(segs):
        ux, uz = (bx - ax) / L, (bz - az) / L
        nx, nz = -uz, ux
        e0 = t / 2 if (k > 0 or not caps[0]) else 0.0  # overlap into the neighbour so corners close
        e1 = t / 2 if (k < len(segs) - 1 or not caps[1]) else 0.0
        a = (ax - ux * e0, az - uz * e0)
        b = (bx + ux * e1, bz + uz * e1)
        ga, gb = gys[i] - 0.15, gys[i + 1] - 0.15
        ta, tb = gys[i] + H, gys[i + 1] + H
        for s in (1, -1):
            p0 = (a[0] + nx * t / 2 * s, a[1] + nz * t / 2 * s)
            p1 = (b[0] + nx * t / 2 * s, b[1] + nz * t / 2 * s)
            m.poly([(p0[0], ga, p0[1]), (p1[0], gb, p1[1]), (p1[0], tb - 0.1, p1[1]), (p0[0], ta - 0.1, p0[1])], "brick")
        # the coping: a slab 0.06 m proud each side, 0.1 m thick
        c = t / 2 + 0.06
        q = [(a[0] + nx * c, a[1] + nz * c), (b[0] + nx * c, b[1] + nz * c), (b[0] - nx * c, b[1] - nz * c), (a[0] - nx * c, a[1] - nz * c)]
        ys = [ta, tb, tb, ta]
        m.poly([(q[j][0], ys[j], q[j][1]) for j in range(4)], "coping")
        for j0, j1 in ((0, 1), (2, 3)):
            m.poly([(q[j0][0], ys[j0] - 0.1, q[j0][1]), (q[j1][0], ys[j1] - 0.1, q[j1][1]), (q[j1][0], ys[j1], q[j1][1]), (q[j0][0], ys[j0], q[j0][1])], "coping")
        if (k == 0 and caps[0]) or (k == len(segs) - 1 and caps[1]):
            for p, g, tt, sgn in ((a, ga, ta, -1), (b, gb, tb, 1)) if len(segs) == 1 else (((a, ga, ta, -1),) if k == 0 and caps[0] else ()) + (((b, gb, tb, 1),) if k == len(segs) - 1 and caps[1] else ()):
                p0 = (p[0] + nx * c, p[1] + nz * c)
                p1 = (p[0] - nx * c, p[1] - nz * c)
                m.poly([(p0[0], g, p0[1]), (p1[0], g, p1[1]), (p1[0], tt, p1[1]), (p0[0], tt, p0[1])], "brick")
        # the carved band in a face frame (s along, y up from the segment's mean ground, d out of the face)
        if carved and L > 0.8:
            gm = (gys[i] + gys[i + 1]) / 2
            for s in (1, -1):
                o = (ax + nx * t / 2 * s, az + nz * t / 2 * s)
                rot = math.atan2(-uz, ux) if s > 0 else math.atan2(uz, -ux)
                start = o if s > 0 else (bx + nx * t / 2 * s, bz + nz * t / 2 * s)
                m.push(start[0], gm, start[1], rot)
                m.box(0.05, L - 0.05, 0.28, 0.33, 0.0, 0.025, "carved", skip=("back",))
                m.box(0.05, L - 0.05, 0.92, 0.97, 0.0, 0.025, "carved", skip=("back",))
                nk = max(1, int((L - 0.3) / 0.75))
                for j in range(nk):
                    sc = 0.15 + (L - 0.3) * (j + 0.5) / nk
                    y0 = 0.45 if j % 2 == 0 else 0.6
                    m.box(sc - 0.16, sc + 0.16, y0, y0 + 0.2, 0.0, 0.02, "carved", skip=("back", "bottom"))
                m.pop()
        # clipped trees on the coping
        if topiary:
            while next_tree < acc + L:
                d = next_tree - acc
                x, z = ax + ux * d, az + uz * d
                y = gys[i] + (gys[i + 1] - gys[i]) * d / L + H
                clipped_tree(x, z, y)
                next_tree += V["topiary_step"]
        acc += L
    for idx in (0, n - 1):
        x, z = pts[idx]
        S.JOINTS.append([f"{name}_{'a' if idx == 0 else 'b'}", x, gys[idx] - 0.15, z, "wall foot"])
    return acc


def clipped_tree(x, z, y):
    """A clipped tree of three tiers on a wall (plate 5)."""
    m.box(x - 0.05, x + 0.05, y, y + 1.25, z - 0.05, z + 0.05, "trunk")
    for k, r in enumerate((0.42, 0.34, 0.24)):
        y0 = y + 0.25 + k * 0.38
        m.lathe([(0.04, y0), (r, y0 + 0.11), (0.03, y0 + 0.3)], 5, "topiary", cx=x, cz=z, cap=False)


def outer_wall(x3):
    """The outer wall on the block's lines, open at the south gate (花园门 XY03's box fills it), at the side gates and at the north opening (S01)."""
    hw, d = V["block_w"] / 2, V["block_d"]
    H, t = V["owall_h"], V["owall_t"]
    mp = plan_map()
    rd = {r["id"]: r for r in readings()}
    zw = mp(0, pts_of(rd["GATE_W"])[0][1])[1]
    ze = mp(0, pts_of(rd["GATE_E"])[0][1])[1]
    xn = mp(pts_of(rd["GATE_N"])[0][0], 0)[0]
    gw, gs = V["gate_side_w"] / 2 + 0.55, 3.95
    REPORT["side_gate_z"] = round(zw, 2)
    runs = [
        ("owall_S_W", [(x3 - gs, 0.0), (-hw, 0.0), (-hw, zw + gw)]),
        ("owall_W_N", [(-hw, zw - gw), (-hw, -d), (xn - 1.0 - 0.45, -d)]),
        ("owall_N_E", [(xn + 1.0 + 0.45, -d), (hw, -d), (hw, ze - gw)]),
        ("owall_E_S", [(hw, ze + gw), (hw, 0.0), (x3 + gs, 0.0)]),
    ]
    total = 0.0
    for name, pts in runs:
        total += wall_line(pts, H, t, name)
        for k in range(len(pts) - 1):
            a, b = pts[k], pts[k + 1]
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            ux, uz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            nx, nz = -uz * (t / 2 + 0.1), ux * (t / 2 + 0.1)
            S.FOOTPRINTS.append([(a[0] + nx - ux * 0.4, a[1] + nz - uz * 0.4), (b[0] + nx + ux * 0.4, b[1] + nz + uz * 0.4), (b[0] - nx + ux * 0.4, b[1] - nz + uz * 0.4), (a[0] - nx - ux * 0.4, a[1] - nz - uz * 0.4)])
    REPORT["outer_wall_m"] = round(total, 1)
    o = t / 2
    for tag, x, z in (("SW", -hw - o, o), ("SE", hw + o, o), ("NW", -hw - o, -d - o), ("NE", hw + o, -d - o)):
        S.kp(f"owall_foot_{tag}", (x, S.gy(x, z), z), anchor=True)
        S.kp(f"owall_top_{tag}", (x, S.gy(x, z) + H, z), anchor=True)
    S.kp("swall_top_gate_L", (x3 - gs, S.gy(x3 - gs, o) + H, o), anchor=True)
    S.kp("swall_top_gate_R", (x3 + gs, S.gy(x3 + gs, o) + H, o), anchor=True)
    # the side gates: two piers with pineapple finials and iron leaves (plate 5); the north opening between two plain piers
    for side, x, z in (("w", -hw, zw), ("e", hw, ze)):
        for sz, tag in ((1, "S"), (-1, "N")):
            pz = z + sz * (V["gate_side_w"] / 2 + 0.55)
            g = S.footing(rect(x - 0.55, x + 0.55, pz - 0.55, pz + 0.55), S.gy(x, pz) + V["pier_h"] - 0.35, "brick", name=f"{side}gate_pier_{tag}")
            y = S.gy(x, pz) + V["pier_h"]
            m.box(x - 0.65, x + 0.65, y - 0.35, y, pz - 0.65, pz + 0.65, "coping")
            m.box(x - 0.56, x + 0.56, S.gy(x, pz) + 0.8, y - 0.6, pz - 0.4, pz + 0.4, "carved")  # a carved panel on all four faces
            m.lathe([(0.32, y), (0.22, y + 0.12), (0.42, y + 0.45), (0.36, y + 0.75), (0.12, y + 0.95), (0.0, y + 1.05)], 8, "sculpt", cx=x, cz=pz, cap=False)
            # the picture's left and right from the south: the west gate's south pier is the left, the east gate's north pier is the left
            lr = ("L" if tag == "S" else "R") if side == "w" else ("L" if tag == "N" else "R")
            S.kp(f"{side}gate_finial_{lr}", (x, y + 1.05, pz))
            S.kp(f"{side}gate_pier_top_{lr}", (x + (0.65 if side == "w" else -0.65), y, pz))
        # the iron leaves, closed, with bars (plate 5)
        y0 = S.gy(x, z)
        hz = V["gate_side_w"] / 2
        for k in range(15):  # the iron leaves, closed: bars and three rails (plate 5)
            zz = z - hz + 2 * hz * (k + 0.5) / 15
            m.box(x - 0.02, x + 0.02, y0 + 0.05, y0 + 2.5 + 0.12 * math.cos(math.pi * (zz - z) / hz), zz - 0.02, zz + 0.02, "iron")
        for yy in (0.4, 1.3, 2.2):
            m.box(x - 0.03, x + 0.03, y0 + yy - 0.03, y0 + yy + 0.03, z - hz, z + hz, "iron")
        S.entry(f"{side}gate_out", x + (-1.6 if side == "w" else 1.6), z)
        S.entry(f"{side}gate_in", x + (1.6 if side == "w" else -1.6), z)
    for sx in (-1, 1):
        px = xn + sx * 1.45
        S.footing(rect(px - 0.45, px + 0.45, -d - 0.45, -d + 0.45), S.gy(px, -d) + 1.9, "brick", name=f"ngate_pier_{'W' if sx < 0 else 'E'}")
        m.lathe([(0.3, S.gy(px, -d) + 1.9), (0.3, S.gy(px, -d) + 2.0), (0.2, S.gy(px, -d) + 2.1), (0.0, S.gy(px, -d) + 2.45)], 8, "sculpt", cx=px, cz=-d, cap=False)
    S.entry("ngate_out", xn, -d - 1.6)
    S.entry("sgate_in", x3, -1.4)
    return zw, ze


def maze_walls():
    mp = plan_map()
    total, n = 0.0, 0
    for r in readings():
        if r["kind"] != "wall":
            continue
        pts = [mp(*p) for p in pts_of(r)]
        total += wall_line(pts, V["wall_h"], V["wall_t"], r["id"].lower())
        n += 1
    REPORT["maze_walls"] = n
    REPORT["maze_walls_m"] = round(total, 1)


def floor():
    """The maze's paths: the floor between the walls, paved (assumed, C), on the walk surface in 3 m cells."""
    hw, d = V["block_w"] / 2 - V["owall_t"] / 2, V["block_d"] - V["owall_t"] / 2
    z0 = -V["owall_t"] / 2
    m.cls = "fill"
    nx, nz = int(math.ceil(2 * hw / 3.0)), int(math.ceil((d + z0) / 3.0))
    xs = [-hw + 2 * hw * i / nx for i in range(nx + 1)]
    zs = [z0 - (d + z0) * j / nz for j in range(nz + 1)]
    G = [[S.gy(x, z) + 0.03 for x in xs] for z in zs]
    for j in range(nz):
        for i in range(nx):
            m.poly([(xs[i], G[j][i], zs[j]), (xs[i + 1], G[j][i + 1], zs[j]), (xs[i + 1], G[j + 1][i + 1], zs[j + 1]), (xs[i], G[j + 1][i], zs[j + 1])], "pave")
    m.cls = "doc"
    S.CLEAR.append(rect(-hw, hw, -d, z0))


# ------------------------------------------------------------------ the centre: drum, flights, pavilion
def at(r, th, cx=None, cz=None):
    """A point at radius r and angle th from the south (+z), positive towards the east (+x)."""
    cx = C[0] if cx is None else cx
    cz = C[1] if cz is None else cz
    return (cx + r * math.sin(th), cz + r * math.cos(th))


def sector(r0, r1, t0, t1, y0, y1, mat, n=None):
    """An annular sector from y0 to y1 (a step, a landing)."""
    n = n or max(2, int(abs(t1 - t0) / math.radians(8)) + 1)
    ins = [at(r0, t0 + (t1 - t0) * k / n) for k in range(n + 1)]
    out = [at(r1, t0 + (t1 - t0) * k / n) for k in range(n + 1)]
    for k in range(n):
        m.poly([(out[k][0], y1, out[k][1]), (out[k + 1][0], y1, out[k + 1][1]), (ins[k + 1][0], y1, ins[k + 1][1]), (ins[k][0], y1, ins[k][1])], mat)
        m.poly([(out[k][0], y0, out[k][1]), (out[k + 1][0], y0, out[k + 1][1]), (out[k + 1][0], y1, out[k + 1][1]), (out[k][0], y1, out[k][1])], mat)
    for p, q in ((ins[0], out[0]), (ins[-1], out[-1])):
        m.poly([(p[0], y0, p[1]), (q[0], y0, q[1]), (q[0], y1, q[1]), (p[0], y1, p[1])], mat)


def centre():
    Rd, Ro, Hd = V["drum_r"], V["ring_r"], V["drum_h"]
    g0 = min(S.gy(*at(Ro, math.radians(a))) for a in range(0, 360, 30)) - 0.15
    yl = V["landing_h"]
    # the drum: a 32-sided body, base and cornice rings, carved panels (plate 5: a large panel on the front, smaller ones round)
    n = 32
    ring = [at(Rd, 2 * math.pi * k / n) for k in range(n)]
    m.prism(ring, g0, Hd - 0.3, "marble", top=False)
    m.prism([at(Rd + 0.12, 2 * math.pi * k / n) for k in range(n)], Hd - 0.3, Hd, "marble")
    m.prism([at(Rd + 0.1, 2 * math.pi * k / n) for k in range(n)], g0, yl + 0.3, "marble", top=False)
    for k in range(8):
        th = 2 * math.pi * k / 8
        w = 2.3 if k == 0 else 1.2
        m.push(*_tan_frame(Rd, th))
        y0 = yl + 0.55 if k == 0 else Hd * 0.45
        m.box(-w / 2, w / 2, y0, Hd - 0.55, 0.0, 0.06, "panel", skip=("back",))
        m.box(-w / 2 - 0.1, w / 2 + 0.1, Hd - 0.62, Hd - 0.55, 0.0, 0.1, "sculpt", skip=("back",))
        m.box(-w / 2 - 0.1, w / 2 + 0.1, y0 - 0.07, y0, 0.0, 0.1, "sculpt", skip=("back",))
        m.box(-w * 0.3, w * 0.3, (y0 + Hd - 0.55) / 2 - 0.35, (y0 + Hd - 0.55) / 2 + 0.35, 0.06, 0.12, "sculpt", skip=("back",))
        m.pop()
    S.FOOTPRINTS.append([at(Ro + 0.2, 2 * math.pi * k / 24) for k in range(24)])
    for k in range(8):
        x, z = at(Ro, 2 * math.pi * k / 8)
        S.JOINTS.append([f"ring_foot_{k}", x, S.gy(x, z) - 0.15, z, "wall foot"])
    # the landing before the drum and the straight flight to it (S01's three rungs; five steps on plate 5)
    tl = math.radians(18)
    sector(Rd, Ro, -tl, tl, g0, yl, "step")
    fx0, fx1 = at(Ro, -tl)[0], at(Ro, tl)[0]
    zf = at(Ro, 0.0)[1]
    nst = 5
    run = 0.34
    for k in range(nst):
        z1 = zf + run * (nst - k)
        y = yl * (k + 1) / nst
        lo = min(S.gy(fx0, z1), S.gy(fx1, z1)) - 0.15
        m.prism(rect(fx0, fx1, zf - 0.3, z1), lo, y, "step")
    zfoot = zf + run * nst
    S.kp("front_step_foot_C", (C[0], S.gy(C[0], zfoot), zfoot))
    S.joint("front_steps", C[0], zfoot - 0.1, "stair foot")
    S.entry("front_steps", C[0], zfoot + 0.7)
    S.FOOTPRINTS.append(rect(fx0 - 0.2, fx1 + 0.2, zf - 0.3, zfoot + 0.1))
    S.kp("drum_foot_C", (C[0], yl, C[1] + Rd))
    S.kp("drum_top_C", (C[0], Hd, C[1] + Rd + 0.12))
    # the two curved flights between the drum and the parapet, from the landing round to the back, where they meet at the drum's top (plate 5)
    te = math.radians(V["flight_end"])
    nsteps = int(round((Hd - yl) / 0.15))
    rise = (Hd - yl) / nsteps
    for sg in (1, -1):
        for k in range(nsteps):
            t0 = sg * (tl + (te - tl) * k / nsteps)
            t1 = sg * (tl + (te - tl) * (k + 1) / nsteps)
            sector(Rd, Ro - 0.3, min(t0, t1), max(t0, t1), g0, yl + rise * (k + 1), "step", n=2)
    sector(Rd, Ro - 0.3, te, 2 * math.pi - te, g0, Hd, "step")  # the back landing
    REPORT["flight_steps"] = nsteps
    REPORT["flight_tread_m"] = round((te - tl) * (Rd + Ro) / 2 / nsteps, 2)
    # the parapet: a solid curved wall with a carved band, its top rising with the flights, a balustrade on it, posts with urns (plate 5)
    ph = V["parapet_h"]
    npar = 48
    def tread_at(th):
        a = abs(th)
        if a <= tl:
            return yl
        if a >= te:
            return Hd
        return yl + (Hd - yl) * (a - tl) / (te - tl)
    rp = Ro - 0.15
    ths = [-math.pi + 2 * math.pi * k / npar for k in range(npar + 1)]
    for k in range(npar):
        a0, a1 = ths[k], ths[k + 1]
        if abs((a0 + a1) / 2) < tl:
            continue  # the landing's front is open to the straight flight
        for r in (Ro, Ro - 0.3):
            p0, p1 = at(r, a0), at(r, a1)
            y0, y1 = tread_at(a0) + ph, tread_at(a1) + ph
            m.poly([(p0[0], g0, p0[1]), (p1[0], g0, p1[1]), (p1[0], y1, p1[1]), (p0[0], y0, p0[1])], "marble")
        q0, q1, r0, r1 = at(Ro, a0), at(Ro, a1), at(Ro - 0.3, a1), at(Ro - 0.3, a0)
        y0, y1 = tread_at(a0) + ph, tread_at(a1) + ph
        m.poly([(q0[0], y0, q0[1]), (q1[0], y1, q1[1]), (r0[0], y1, r0[1]), (r1[0], y0, r1[1])], "sculpt")
        # the carved scroll band on the outer face (plate 5): a raised strip under the coping
        b0, b1 = at(Ro + 0.03, a0), at(Ro + 0.03, a1)
        m.poly([(b0[0], y0 - 0.45, b0[1]), (b1[0], y1 - 0.45, b1[1]), (b1[0], y1 - 0.12, b1[1]), (b0[0], y0 - 0.12, b0[1])], "carved")
    for sg in (1, -1):
        run_pts = [at(rp, sg * (tl + (te - tl) * k / 12)) for k in range(13)]
        run_y = [tread_at(sg * (tl + (te - tl) * k / 12)) + ph for k in range(13)]
        P_.rail(run_pts, run_y, h=V["rail_h"] * 0.7, posts=4.5, spacing=0.4)
    back = [at(rp, te + (2 * math.pi - 2 * te) * k / 4) for k in range(5)]
    P_.rail(back, Hd + ph, h=V["rail_h"] * 0.7, posts=4.5, spacing=0.4)
    for sg, lr in ((-1, "L"), (1, "R")):
        x, z = at(rp, sg * tl)
        top = yl + ph + 1.0
        m.box(x - 0.28, x + 0.28, g0, top, z - 0.28, z + 0.28, "marble")
        P_.urn(x, z, top, 0.7)
        S.kp(f"ring_post_{lr}_top", (x, top + 0.66, z))
        xo, zo = at(rp, sg * math.pi / 2)
        S.kp(f"ring_rail_{lr}_out", (xo + sg * 0.17, tread_at(sg * math.pi / 2) + ph + V["rail_h"] * 0.7, zo))
    # the drum's top: the floor, a balustrade round its edge open at the back where the flights arrive
    m.flat([at(Rd, 2 * math.pi * k / n) for k in range(n)], Hd, "pave")
    edge = [at(Rd - 0.25, -te + 2 * te * k / 24) for k in range(25)]
    P_.rail(edge, Hd, h=V["rail_h"], posts=3.0, spacing=0.4)
    for sg in (-1, 1):  # the urn posts either side of the pavilion's front (plate 5)
        x, z = at(Rd - 0.25, sg * math.radians(14))
        m.box(x - 0.25, x + 0.25, Hd, Hd + 1.15, z - 0.25, z + 0.25, "marble")
        P_.urn(x, z, Hd + 1.15, 0.6)
    pavilion()


def _tan_frame(r, th):
    """A face frame tangent to the circle at angle th: s along the tangent, d outward."""
    x, z = at(r, th)
    return (x, 0.0, z, th)


def pavilion():
    """The octagon of four large faces with open arches and four small ones with windows (S258; plate 5), corner columns, the entablature, the tiled skirt,
    the ribbed dome, the open lantern and the ball (plate 5). The front (south) and the faces plate 5 shows are documented; the back faces are carried round (fill)."""
    Hd = V["drum_h"]
    a, c = V["pav_w"] / 2, V["pav_chamfer"]
    cx, cz = C
    octo = [(cx - (a - c), cz + a), (cx + (a - c), cz + a), (cx + a, cz + (a - c)), (cx + a, cz - (a - c)), (cx + (a - c), cz - a), (cx - (a - c), cz - a), (cx - a, cz - (a - c)), (cx - a, cz + (a - c))]
    ch, et = V["col_h"], V["ent_top"]
    yb = Hd
    for i in range(8):
        p, q = octo[i], octo[(i + 1) % 8]
        large = i % 2 == 0
        # faces: 0 S, 2 E, 4 N, 6 W (large); the south and the two front diagonals and the sides plate 5 shows: doc; the north and the back diagonals: fill
        m.cls = "fill" if i in (3, 4, 5) else "doc"
        L = math.hypot(q[0] - p[0], q[1] - p[1])
        # a face frame walked from q to p, so that d points out of the octagon (the corners run anticlockwise seen from above)
        m.push(q[0], yb, q[1], math.atan2(-(p[1] - q[1]), p[0] - q[0]))
        if large:
            w_o, spring, rise = 2.3, 3.5, 1.15
            s0 = L / 2 - w_o / 2
            P_.wall_holes(0.0, L, 0.0, ch, [(s0, s0 + w_o, 0.0, spring, rise)], "wall")
            arch_dressing(s0, s0 + w_o, spring, rise)
        else:
            w_o = 0.9
            s0 = L / 2 - w_o / 2
            P_.wall_holes(0.0, L, 0.0, ch, [(s0, s0 + w_o, 1.4, 3.6, 0.45)], "wall")
            P_.opening(s0, s0 + w_o, 1.4, 3.6, 0.45, depth=0.3, kind="win", frame=0.12, head="scroll")
        P_.entablature(0.0, L, et, h=et - ch, out=0.35)
        m.pop()
        # the corner column, free before the corner (plate 5 draws a column at every corner)
        ox, oz = p[0] + (p[0] - cx) / math.hypot(p[0] - cx, p[1] - cz) * 0.32, p[1] + (p[1] - cz) / math.hypot(p[0] - cx, p[1] - cz) * 0.32
        m.lathe([(0.34, yb), (0.34, yb + 0.3), (0.25, yb + 0.4), (0.22, yb + ch - 0.55), (0.34, yb + ch - 0.3), (0.4, yb + ch)], 8, "marble", cx=ox, cz=oz)
    m.cls = "doc"
    # the column feet and caps of the south face's corners
    for tag, p in (("SW", octo[0]), ("SE", octo[1])):
        d = math.hypot(p[0] - cx, p[1] - cz)
        ox, oz = p[0] + (p[0] - cx) / d * 0.32, p[1] + (p[1] - cz) / d * 0.32
        S.kp(f"pav_col_{tag}_foot", (ox, yb, oz))
        S.kp(f"pav_col_{tag}_cap", (ox, yb + ch, oz))
    S.kp("pav_ent_top_C", (cx, yb + et, cz + a + 0.35))
    S.kp("pav_arch_head_S", (cx, yb + 3.5 + 1.15, cz + a))
    m.flat(octo, yb + et - 0.02, "wall")
    # a vase on a pedestal inside (plate 5 shows an ornament standing in the front arch): fill
    m.cls = "fill"
    m.lathe([(0.45, yb), (0.45, yb + 0.9), (0.3, yb + 1.0), (0.5, yb + 1.6), (0.35, yb + 2.1), (0.12, yb + 2.3), (0.25, yb + 2.6), (0.0, yb + 2.7)], 8, "sculpt", cx=cx, cz=cz)
    m.cls = "doc"
    # the skirt: from the entablature's top out to the eave, tiled; an octagon like the body's, scaled
    def scaled(f, dy=0.0):
        return [(cx + (x - cx) * f, cz + (z - cz) * f) for x, z in octo]
    re_, ye = V["eave_r"], yb + V["eave_y"]
    f_e = re_ / a
    f_i = (a + 0.05) / a
    lo, hi = scaled(f_e), scaled(f_i)
    ys = yb + V["dome_base"] - 0.35
    m.frustum(lo, hi, ye, ys, "roof")
    m.flat(lo, ye, "roofedge")
    m.frustum(lo, lo, ye - 0.18, ye, "roofedge")
    for (x, z) in lo:  # small scrolls at the corners
        m.box(x - 0.15, x + 0.15, ye, ye + 0.4, z - 0.15, z + 0.15, "gilt")
    # the dome on a short band, ribs, cartouche dormers on the four large faces (plate 5)
    m.prism(scaled(f_i * 0.98), ys, yb + V["dome_base"], "wall")
    rb = a * 0.92
    yd0, yd1 = yb + V["dome_base"], yb + V["dome_top"]
    prof = [(rb * math.cos(math.pi / 2 * k / 6), yd0 + (yd1 - yd0) * math.sin(math.pi / 2 * k / 6)) for k in range(7)]
    prof[-1] = (0.72, yd1)
    m.lathe(prof, 16, "roof", cx=cx, cz=cz, cap=True)
    for k in range(8):
        th = 2 * math.pi * k / 8 + math.pi / 8
        for (r0, y0), (r1, y1) in zip(prof[:-1], prof[1:]):
            p0, p1 = at(r0 + 0.05, th, cx, cz), at(r1 + 0.05, th, cx, cz)
            m.poly([(p0[0], y0, p0[1]), (p1[0], y1, p1[1]), (p1[0], y1 + 0.12, p1[1]), (p0[0], y0 + 0.12, p0[1])], "gilt")
    for k in range(4):
        th = math.pi / 2 * k
        x, z = at(rb * 0.9, th, cx, cz)
        m.push(x, yd0, z, th)
        m.cls = "doc" if k in (0, 1, 3) else "fill"
        m.box(-0.45, 0.45, 0.2, 1.3, -0.4, 0.15, "sculpt", skip=("back",))
        P_.oval(0.0, 0.8, 0.3, 0.38, n=10, d=0.15)
        m.pop()
    m.cls = "doc"
    S.kp("pav_dome_top", (cx, yd1, cz))
    # the lantern: six posts, a small roof, the ball
    yl0, yl1 = yd1, yb + V["lantern_top"] - 0.35
    for k in range(6):
        x, z = at(0.6, 2 * math.pi * k / 6, cx, cz)
        m.box(x - 0.07, x + 0.07, yl0, yl1, z - 0.07, z + 0.07, "marble")
    m.lathe([(0.85, yl1), (0.85, yl1 + 0.08), (0.55, yl1 + 0.2), (0.12, yb + V["lantern_top"])], 8, "roof", cx=cx, cz=cz)
    S.kp("pav_lantern_top", (cx, yb + V["lantern_top"], cz))
    yf = yb + V["lantern_top"]
    ft = yb + V["finial_top"]
    m.lathe([(0.1, yf), (0.1, yf + 0.25), (0.32, yf + 0.45), (0.38, yf + 0.65), (0.3, yf + 0.85), (0.08, ft - 0.1), (0.0, ft)], 8, "gilt", cx=cx, cz=cz)
    S.kp("pav_finial_top", (cx, ft, cz))
    S.kp("pav_eave_L", (cx - re_, ye, cz))
    S.kp("pav_eave_R", (cx + re_, ye, cz))
    REPORT["pavilion_top_above_ground_m"] = round(ft, 2)


def arch_dressing(a0, a1, spring, rise):
    """The arch's reveal and moulded frame (an open arch: no glass), a keystone."""
    from model_parts import arc_pts
    pts = arc_pts(a0, a1, spring, rise, 8)
    for s in (a0, a1):
        m.poly([(s, 0.0, 0.0), (s, 0.0, -0.3), (s, spring, -0.3), (s, spring, 0.0)], "marble")
    for p0, p1 in zip(pts[:-1], pts[1:]):
        m.poly([(p0[0], p0[1], 0.0), (p0[0], p0[1], -0.3), (p1[0], p1[1], -0.3), (p1[0], p1[1], 0.0)], "marble")
    f = 0.16
    m.box(a0 - f, a0, 0.0, spring, 0.0, 0.1, "sculpt", skip=("back",))
    m.box(a1, a1 + f, 0.0, spring, 0.0, 0.1, "sculpt", skip=("back",))
    ring_ = arc_pts(a0 - f, a1 + f, spring, rise + f, 8)
    for (p0, q0), (p1, q1) in zip(zip(pts[:-1], ring_[:-1]), zip(pts[1:], ring_[1:])):
        m.poly([(p0[0], p0[1], 0.1), (q0[0], q0[1], 0.1), (q1[0], q1[1], 0.1), (p1[0], p1[1], 0.1)], "sculpt")
    km = (a0 + a1) / 2
    m.box(km - 0.18, km + 0.18, spring + rise - 0.05, spring + rise + 0.45, 0.0, 0.18, "gilt", skip=("back",))


# ------------------------------------------------------------------ the north hall, the basin, the trees
def north_hall():
    """XY04-N01: two storeys (S02), five bays by three, a hipped Chinese roof with finials on its ridge ends (plate 5); its south terrace with a balustrade and a flight
    (S01's steps, Round 9's CCX-127). Only its roof and the upper wall show on plate 5: the façades are carried from the group (fill), the roof is documented."""
    mp = plan_map()
    rd = {r["id"]: r for r in readings()}
    q = pts_of(rd["HALL"])
    (x0, z0), (x1, z1) = mp(q[0][0], q[0][1]), mp(q[2][0], q[2][1])
    w, d = V["hall_w"], V["hall_d"]
    zc = (z0 + z1) / 2
    hx = w / 2
    zf, zb = zc + d / 2, zc - d / 2
    REPORT["hall_centre"] = [round(X_AX, 2), round(zc, 2)]
    pl = V["hall_plat"]
    ter = 2.4
    base = S.footing(rect(X_AX - hx - 0.4, X_AX + hx + 0.4, zb - 0.4, zf + ter), S.gy(X_AX, zc) + pl, "marble", name="hall_platform")
    y0 = S.gy(X_AX, zc) + pl
    H1, eave = 3.9, V["hall_eave"]
    sides = [((X_AX - hx, zf), (X_AX + hx, zf), "fill", 5), ((X_AX + hx, zf), (X_AX + hx, zb), "fill", 3), ((X_AX + hx, zb), (X_AX - hx, zb), "fill", 5), ((X_AX - hx, zb), (X_AX - hx, zf), "fill", 3)]
    for a, b, cls, nb in sides:
        m.cls = cls
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        m.push(a[0], y0, a[1], math.atan2(-(b[1] - a[1]), b[0] - a[0]))
        bw = L / nb
        holes = []
        for k in range(nb):
            s = bw * (k + 0.5)
            ww = 1.3 if not (nb == 5 and k == 2) else 1.6
            holes.append((s - ww / 2, s + ww / 2, 0.0 if (nb == 5 and k == 2 and a[1] == zf) else 0.7, 2.7, ww / 2))
            holes.append((s - 0.55, s + 0.55, H1 + 0.6, H1 + 2.0, 0.0))
        P_.wall_holes(0.0, L, 0.0, eave - 0.7, holes, "wall")
        for h in holes:
            kind = "door" if h[2] == 0.0 else "win"
            P_.opening(*h, depth=0.3, kind=kind, frame=0.14)
        for k in range(nb + 1):
            P_.pilaster(bw * k, 0.0, eave - 0.7, w=0.45, out=0.15, flutes=False)
        m.box(-0.1, L + 0.1, H1 - 0.1, H1 + 0.15, 0.0, 0.2, "marble", skip=("back",))
        P_.entablature(0.0, L, eave, h=0.7, out=0.35)
        m.pop()
    m.cls = "doc"
    m.flat(rect(X_AX - hx, X_AX + hx, zb, zf), eave - 0.02, "wall")
    # a gable roof with its ridge over the whole length and finials on the ridge's ends (plate 5; the Round 26 reader: 'a gable roof with ridge-end finials')
    ov = 0.9
    x0, x1 = X_AX - hx - 0.45, X_AX + hx + 0.45
    ye, yr = eave + 0.15, V["hall_ridge"]
    for sz in (1, -1):
        ze = zc + sz * (d / 2 + ov)
        m.poly([(x0, ye, ze), (x1, ye, ze), (x1, yr, zc), (x0, yr, zc)], "roof")
        m.poly([(x0, ye - 0.2, ze), (x1, ye - 0.2, ze), (x1, ye, ze), (x0, ye, ze)], "roofedge")
    for x in (x0 + 0.05, x1 - 0.05):  # the gables
        m.cls = "fill"
        m.poly([(x, eave, zc + d / 2), (x, eave, zc - d / 2), (x, yr - 0.1, zc)], "wall")
        m.cls = "doc"
    m.box(x0 - 0.1, x1 + 0.1, yr - 0.05, yr + 0.3, zc - 0.2, zc + 0.2, "ridge")
    S.kp("hall_eave_SW", (x0, ye, zc + d / 2 + ov))
    S.kp("hall_eave_SE", (x1, ye, zc + d / 2 + ov))
    for x, tag in ((x0, "W"), (x1, "E")):
        p = (x, yr + 0.3, zc)
        S.kp(f"hall_ridge_{tag}", p)
        m.lathe([(0.3, p[1]), (0.22, p[1] + 0.25), (0.35, p[1] + 0.6), (0.12, p[1] + 1.0), (0.0, p[1] + 1.2)], 8, "gilt", cx=p[0], cz=p[2])
        S.kp(f"hall_finial_{tag}", (p[0], p[1] + 1.2, p[2]))
    # the terrace before it with a balustrade, open at the middle flight
    m.flat(rect(X_AX - hx - 0.4, X_AX + hx + 0.4, zf, zf + ter), y0, "pave")
    for sx in (-1, 1):
        P_.rail([(X_AX + sx * 1.8, zf + ter - 0.2), (X_AX + sx * (hx + 0.2), zf + ter - 0.2), (X_AX + sx * (hx + 0.2), zf + 0.2)], y0, h=V["rail_h"], posts=2.6)
    nst = 4
    zs = zf + ter
    for k in range(nst):
        z1 = zs + 0.32 * (nst - k)
        y = S.gy(X_AX, zs) + pl * (k + 1) / (nst + 1)
        lo = S.gy(X_AX, z1) - 0.15
        m.prism(rect(X_AX - 1.6, X_AX + 1.6, zs - 0.05, z1), lo, y, "step")
    zfoot = zs + 0.32 * nst
    S.joint("hall_steps", X_AX, zfoot - 0.1, "stair foot")
    S.entry("hall_steps", X_AX, zfoot + 0.7)
    S.FOOTPRINTS.append(rect(X_AX - hx - 0.6, X_AX + hx + 0.6, zb - 0.6, zfoot + 0.1))
    S.entry("hall_back", X_AX, zb - 1.4)
    return zb


def basin():
    mp = plan_map()
    rd = {r["id"]: r for r in readings()}
    q = pts_of(rd["BASIN"])
    (x0, z0), (x1, z1) = mp(q[0][0], q[0][1]), mp(q[2][0], q[2][1])
    r = V["basin_r"]
    cz = z0  # the straight side north, the half-round to the south (S01)
    ths = [-math.pi / 2 + math.pi * k / 12 for k in range(13)]
    outer = [(X_AX + r * math.sin(t), cz + r * math.cos(t)) for t in ths]
    inner = [(X_AX + (r - 0.35) * math.sin(t), cz + (r - 0.35) * math.cos(t)) for t in ths]
    g = min(S.gy(x, z) for x, z in outer + [(X_AX, cz)])
    m.cls = "fill"
    m.prism(outer, g - 0.15, g + 0.4, "marble", top=False)
    m.prism(inner, g - 0.15, g + 0.4, "marble", top=False)
    for k in range(12):
        m.poly([(outer[k][0], g + 0.4, outer[k][1]), (outer[k + 1][0], g + 0.4, outer[k + 1][1]), (inner[k + 1][0], g + 0.4, inner[k + 1][1]), (inner[k][0], g + 0.4, inner[k][1])], "marble")
    m.flat(inner, g + 0.22, "water")
    m.cls = "doc"
    S.FOOTPRINTS.append(outer)
    S.joint("basin_rim", X_AX, cz + r, "wall foot", y=S.gy(X_AX, cz + r) - 0.15)


def weeping_trees():
    """龙爪槐 in their tree circles (S310), on the four rounded beds S01 draws at the inner corners; plate 5 draws four umbrella crowns."""
    mp = plan_map()
    spots = {"NW": (8738, 570), "NE": (9027, 565), "SW": (8743, 812), "SE": (9017, 823)}  # S01, by eye on plan_readings' trace (Round 26)
    for tag, (px, py) in spots.items():
        x, z = mp(px, py)
        g = S.gy(x, z)
        ring_ = [(x + 1.6 * math.cos(2 * math.pi * k / 16), z + 1.6 * math.sin(2 * math.pi * k / 16)) for k in range(16)]
        m.prism(ring_, g - 0.15, g + 0.3, "marble", top=False)
        m.lathe([(0.22, g - 0.1), (0.2, g + 2.0), (0.35, g + 2.5)], 6, "trunk", cx=x, cz=z, cap=False)
        R = V["tree_crown"]
        m.lathe([(R * 0.9, g + 1.1), (R, g + 1.6), (R * 0.95, g + 2.3), (R * 0.75, g + 3.0), (R * 0.35, g + 3.5), (0.0, g + 3.65)], 12, "tree", cx=x, cz=z, cap=False)
        m.flat([(x + R * 0.9 * math.cos(2 * math.pi * k / 12), z + R * 0.9 * math.sin(2 * math.pi * k / 12)) for k in range(12)], g + 1.1, "tree")
        S.kp(f"tree_{tag}_top", (x, g + 3.65, z))
        S.joint(f"tree_{tag}", x, z, "trunk")
        REPORT.setdefault("trees", {})[tag] = [round(x, 2), round(z, 2)]


# ------------------------------------------------------------------ build
def build():
    global S, m, P_, X_AX, C
    S = Site("XY04-M10", front_offset=0.0)
    m = Mesh(COL)
    S.m = m
    P_ = Parts(m, rail_h=V["rail_h"], baluster_segs=4)
    m.cls = "doc"
    x3, _, _, _, _ = S.box_local("XY03-M09")
    X_AX = round(x3, 3)
    mp = plan_map()
    rd = {r["id"]: r for r in readings()}
    cpx = pts_of(rd["RING"])[0]
    cxp, czp = mp(*cpx)
    C = (X_AX, czp)
    REPORT["axis_x"] = X_AX
    REPORT["ring_centre_plan_x"] = round(cxp, 2)
    REPORT["centre"] = [round(C[0], 2), round(C[1], 2)]
    floor()
    outer_wall(x3)
    maze_walls()
    centre()
    north_hall()
    basin()
    weeping_trees()
    # the old boxes' centres, for the record: the drum's box and the hall's box against where the plan puts them
    for bid in ("XY04-M22", "XY04-M24"):
        bx, bz, _, _, _ = S.box_local(bid)
        REPORT[f"box_{bid}"] = [round(bx, 2), round(bz, 2)]


def summary(tris, fill, size):
    rows = [
        ["Maze walls", f"{REPORT['maze_walls']} runs of carved grey brick, {REPORT['maze_walls_m']:.0f} m, {V['wall_h']:g} × {V['wall_t']:g} m (S310, B): the pattern traced on the plan S01 (plan_readings.csv) and set into the block of {V['block_w']:g} × {V['block_d']:g} m (S310, today's rebuild; Q292); a framed band of raised keys for the 卐字 carving, clipped trees of three tiers on the copings (plate 5, C)"],
        ["Outer wall and gates", f"{REPORT['outer_wall_m']:.0f} m, {V['owall_h']:g} m high (C), open at the south gate (花园门 XY03, the kit's), at a west and an east gate with pineapple-finial piers and iron leaves, and at the north behind the hall (S01; plate 5, C)"],
        ["Drum and flights", f"a round drum {2 * V['drum_r']:g} m across, its top {V['drum_h']:g} m up, with carved panels; a straight flight to a landing, then two curved flights of {REPORT['flight_steps']} steps climbing round the drum behind a carved parapet with a balustrade to meet at its back (plate 5; S01's ring {2 * V['ring_r']:g} m and flight, C)"],
        ["Pavilion", f"an octagon {V['pav_w']:g} m across, four arched large faces and four small ones with windows (S258, B), corner columns {V['col_h']:g} m, a tiled skirt, a ribbed dome, an open lantern and a gilt ball {REPORT['pavilion_top_above_ground_m']:.1f} m above the ground (plate 5, C); a vase inside (assumed)"],
        ["North hall", f"{V['hall_w']:g} × {V['hall_d']:g} m (S01 on the block), two storeys (S02, B) to {V['hall_eave']:g} m, a hipped Chinese roof with finials (plate 5, C), its terrace and flight; the walls carried from the group (assumed)"],
        ["Trees and basin", "four weeping pagoda trees in round curbs at the inner corners (S310, B; places from S01, C); a half-round basin before the hall (S01, C)"],
        ["Assumed", "the paving of the paths, the hall's façades, the pavilion's back faces and the vase inside it, the basin: carried round or guessed (C, the pale tint with conf=1)"],
    ]
    return {
        "id": "XY04", "aliases": ["XY04-01", "XY04-N01"], "name": "黄花阵 Huanghua Zhen", "glb": "model.glb", "position": S.pos, "rotationY": S.rot,
        "line": "Modelled from plate 5 of 1783-86 and the plan S01: the walls follow S01's lines, set into the block whose size the archive figures give (58.56 × 88.64 m, S310) at the place of today's rebuilt maze; heights and forms read on plate 5 (C). No picture of the maze before 1987 shows it from the ground; the Yangshi Lei plan 样337-146 is not in hand.",
        "rows": rows,
        "caption": {"frontage_m": V["block_w"], "depth_m": V["block_d"], "eave_m": V["wall_h"], "ridge_m": REPORT["pavilion_top_above_ground_m"], "assumed": True, "confidence": "C"},
        "hides": [],
        "ways_cut": [[S.to_scene((x, 0.0, z))[::2] for x, z in rect(-V["block_w"] / 2 + 0.5, V["block_w"] / 2 - 0.5, -V["block_d"] + 0.5, -0.5)]],
        "tris": tris, "fill_tris": fill, "glb_bytes": size,
    }


def main():
    build()
    size = m.write_glb(HERE / "model.glb", "XY04 黄花阵 Huanghua Zhen", extras={"id": "XY04"})
    tris = m.count()
    prims = {k: len(v["idx"]) // 3 for k, v in sorted(m.prims.items())}
    fill = sum(n for k, n in prims.items() if k.endswith("~fill"))
    S.write(HERE, "XY04", ["XY04", "XY04-01", "XY04-N01"], P, "x east along the south wall, y up from the ground at the south wall's box, z south; the origin on the south wall's centre line at its middle; metres", summary(tris, fill, size))
    REPORT.update({"tris": tris, "fill_tris": fill, "glb_bytes": size, "balusters": P_.balusters, "keypoints": len(S.KP), "joints": len(S.JOINTS), "entries": len(S.ENTRIES)})
    json.dump(REPORT, open(HERE / "report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"model.glb {size / 1e6:.2f} MB, {tris} triangles ({fill} fill), {P_.balusters} balusters, {len(S.KP)} key points, {len(S.JOINTS)} joints, {len(S.ENTRIES)} entries; position {S.pos} rotY {S.rot}")
    print(json.dumps({k: v for k, v in REPORT.items() if k not in ('tris',)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
