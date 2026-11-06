#!/usr/bin/env python3
"""螺蛳牌楼 Luosi Pailou (XY13), the east gate of the perspective hill 线法山, the eighteenth detailed model (Round 30): three openings, the arch in the middle between two
free columns, a square-headed door either side under a shell, the end bays with their panels, the wavy cornice that dips over the side bays and rises over the arch, the attic
with its broken scroll pediment and the trophy group over the centre, trophies with round shields over the outer columns, a tower over each side bay with a flared cornice,
a concave pyramidal cap, a lantern and an urn, the carved vines over the faces of the piers growing from vases (plate 19, 线法山东门, P0059; S02 p.159: 'three arches, the side
passages leading through side rooms, vine ornament carved even over the faces of the pillars').
Plain geometry, one GLB (scripts/model_mesh.py) with every figure in params.json; the method is the pilot's (models/XY01-xieqiqu/README.md).

  uv run python models/XY13-luosi-pailou/luosipailou.py

Writes, beside this file: model.glb, params.json, keypoints.json, joints.json, summary.json (models/README.md).
Frame (scripts/model_site.py): origin at the front middle of the gate's box XY13-M56, which faces west: x along the west front to the right as one faces it from the west
(south), y up from the box's ground, z west (out of the front). The east face lies at z = -d.
Grades: what plate 19 shows is `doc`; the east face, the ends, the passages and the side rooms' insides are `fill` (assumed, C, carried round from the west front).
"""

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from model_mesh import Mesh  # noqa: E402
from model_parts import Parts, arc_pts  # noqa: E402
from model_site import Site  # noqa: E402

# Plate 19 is drawn frontally on the gate's axis (x 1189 on the 2400 px copy); read at the dossier's scale, the frontage 22.9 m over x 693-1705 (44.2 px/m), the foot at y 1015
# (Round 30 readings, research/xiyanglou/plate_keypoints.csv). The scale rests on the dossier's weak module (the arch about 3 m, Round 6): every size is C.
P = {
    "w": (22.9, "S71", "C", "the frontage: plate 19, x 693-1705, on the dossier's module (the arch taken as 3 m, weak); S01's figure spans 34-49 m and is ornamental (Q73)"),
    "d": (3.0, "S01", "C", "the depth: the box's guess (Round 6); the towers over the side bays are drawn square on plate 19, 3.05 m across their cornices, so a depth of about 3 m carries them"),
    "col_out": (8.67, "S71", "C", "the outer columns' middles from the axis: plate 19, x 805 and 1572"),
    "col_in": (3.39, "S71", "C", "the inner columns' middles, either side of the arch: plate 19, x 1036 and 1336"),
    "col_r": (0.3, "S71", "C", "the columns' radius: plate 19, the shafts 25-28 px"),
    "col_h": (5.2, "S71", "C", "the columns to their capitals' tops: plate 19, y 785 (dossier 5.4 m)"),
    "plinth": (0.5, "S71", "C", "the columns' bases on their plinths: plate 19, y 990-1015"),
    "arch_w": (2.82, "S71", "C", "the arch's opening: plate 19, x 1128-1252 (the dossier's module took it as 3 m)"),
    "arch_top": (5.77, "S71", "C", "the arch's crown: plate 19, y 760; a half circle, the springing at 4.3 m"),
    "door_w": (1.25, "S71", "C", "the side doors' openings: plate 19, 55 px inside the frames (frames 2.0 m)"),
    "door_x": (6.29, "S71", "C", "the side doors' middles: plate 19, x 920 and 1472 about the axis at x 1191"),
    "door_h": (3.55, "S71", "C", "the side doors' heads: plate 19, y 857, square-headed in moulded frames"),
    "door_crest": (5.5, "S71", "C", "the shell over each door, its top: plate 19, y 772"),
    "cornice_out": (6.9, "S71", "C", "the cornice's top over the outer columns: plate 19, y 708-712 (dossier 6.8 m)"),
    "cornice_in": (6.6, "S71", "C", "the cornice's top over the inner columns: plate 19, y 722-725, lower than over the outer ones: the cornice is wavy"),
    "cornice_dip": (0.15, "S71", "C", "how far the cornice sags between the inner and the outer columns, under the towers: plate 19 hides it behind the towers' bases; assumed"),
    "cornice_c": (7.36, "S71", "C", "the cornice's top on the axis, where it rises in a curve over the arch: plate 19, y 690"),
    "attic_top": (8.5, "S71", "C", "the attic over the centre with its broken scroll pediment and fluted frieze: plate 19, x 1105-1268, its top y 640"),
    "attic_w": (3.7, "S71", "C", "the attic's width at its upper cornice: plate 19, x 1105-1268"),
    "trophy_c": (10.7, "S71", "C", "the trophy group over the centre: plate 19, top y 543 (dossier 11.0 m)"),
    "trophy_in": (8.5, "S71", "C", "the trophies over the inner columns: plate 19, top y 640"),
    "trophy_out": (8.8, "S71", "C", "the trophies with round shields over the outer columns: plate 19, top y 625"),
    "tower_w": (3.05, "S71", "C", "the towers' width at their cornice: plate 19, x 852-990"),
    "tower_base": (7.1, "S71", "C", "the towers' bodies from the main cornice: plate 19, y 700"),
    "tower_cornice": (9.1, "S71", "C", "the towers' flared cornices: plate 19, y 612-615"),
    "tower_cap": (10.65, "S71", "C", "the concave pyramidal caps to the lanterns' plates: plate 19, y 545-548"),
    "tower_top": (12.0, "S71", "C", "the urn finials' tips: plate 19, y 483 (dossier 12.3 m)"),
    "end_top": (7.9, "S71", "C", "the finials at the ends: plate 19, y 664-668"),
}
V = {k: v[0] for k, v in P.items()}

COL = {
    "marble": "#ebe6da", "wall": "#dcd5c6", "panel": "#c2bbab", "sculpt": "#ddd6c6", "vine": "#b9b19e", "joint": "#a39a8a", "glaze": "#3f8a86",
    "glass_win": "#2e4a4f", "door": "#4a3b2c", "roof": "#46705c", "roofedge": "#3a5e4d", "ridge": "#c9a245", "gilt": "#b59a52", "pave": "#c9c2b2", "step": "#d2ccbe",
    "coping": "#b9b2a4", "jet": "#d8ecf2",
}

S = None
m = None
P_ = None


def rect(x0, x1, z0, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def face(a, b):
    dx, dz = b[0] - a[0], b[1] - a[1]
    m.push(a[0], 0.0, a[1], math.atan2(-dz, dx))
    return math.hypot(dx, dz)


def _w(p):
    q = m.world(p)
    return (float(q[0]), float(q[1]), float(q[2]))


def cornice_y(x):
    """The cornice's top along the front (x from the axis): rising in a curve over the arch to `cornice_c` on the axis, `cornice_in` over the inner columns, `cornice_out`
    over the outer ones with a slight sag between under the towers, level over the end bays (plate 19)."""
    a = abs(x)
    ci, co = V["col_in"], V["col_out"]
    if a <= ci:
        t = a / ci
        return V["cornice_in"] + (V["cornice_c"] - V["cornice_in"]) * math.cos(math.pi * t / 2) ** 1.5
    if a <= co:
        t = (a - ci) / (co - ci)
        return V["cornice_in"] + (V["cornice_out"] - V["cornice_in"]) * t - V["cornice_dip"] * math.sin(math.pi * t)
    return V["cornice_out"]


def wavy_band(c, s0, s1, ylo, yhi, d0, d1, mat, n=40):
    """A band on the face whose top follows the cornice (ylo, yhi: offsets below the cornice's top; d0, d1 its planes); c the axis's s."""
    ss = [s0 + (s1 - s0) * k / n for k in range(n + 1)]
    for a, b in zip(ss[:-1], ss[1:]):
        ya, yb = cornice_y(a - c), cornice_y(b - c)
        m.poly([(a, ya - ylo, d1), (b, yb - ylo, d1), (b, yb - yhi, d1), (a, ya - yhi, d1)], mat)
        m.poly([(a, ya - yhi, d0), (b, yb - yhi, d0), (b, yb - yhi, d1), (a, ya - yhi, d1)], mat)
        m.poly([(a, ya - ylo, d1), (b, yb - ylo, d1), (b, yb - ylo, d0), (a, ya - ylo, d0)], mat)
    for s in (s0, s1):
        y = cornice_y(s - c)
        m.poly([(s, y - ylo, d0), (s, y - ylo, d1), (s, y - yhi, d1), (s, y - yhi, d0)], mat)


def vine(s, y0, y1, d, w=0.45, mat="vine"):
    """Carved vine in low relief climbing a pier: a winding stem with leaves either side, from a vase at its foot (plate 19; S02 p.159)."""
    n = int((y1 - y0) / 0.3)
    prev = None
    for k in range(n + 1):
        y = y0 + (y1 - y0) * k / n
        x = s + w * 0.35 * math.sin(k * 0.9)
        if prev:
            m.poly([(prev[0] - 0.035, prev[1], d), (prev[0] + 0.035, prev[1], d), (x + 0.035, y, d), (x - 0.035, y, d)], mat)
        if k % 2 == 0 and 0 < k < n:
            sg = 1 if (k // 2) % 2 else -1
            m.poly([(x, y, d), (x + sg * w * 0.5, y + 0.12, d + 0.01), (x + sg * w * 0.42, y + 0.28, d + 0.01), (x + sg * 0.05, y + 0.1, d)], mat)
        prev = (x, y)
    m.lathe([(0.12, 0.0), (0.2, 0.25), (0.13, 0.45), (0.17, 0.55), (0.0, 0.56)], 8, "sculpt", cx=s, cz=d + 0.15)


def front(doc=True):
    """One face in a face frame (s from the face's left end seen from outside, d out of it); the axis at s = w/2."""
    w = V["w"]
    c = w / 2
    m.cls = "doc" if doc else "fill"
    aw, at = V["arch_w"], V["arch_top"]
    sp = at - aw / 2
    dw, dh, dx = V["door_w"], V["door_h"], V["door_x"]
    ylow = V["cornice_in"] - V["cornice_dip"] - 1.2
    holes = [(c - aw / 2, c + aw / 2, 0.0, sp, aw / 2)] + [(c + sx * dx - dw / 2, c + sx * dx + dw / 2, 0.0, dh, 0.0) for sx in (-1, 1)]
    P_.wall_holes(0.0, w, 0.0, ylow, holes, "wall")
    # the wall between the low line and the wavy entablature
    wavy_band(c, 0.0, w, 1.2, 1.2 + (V["cornice_c"] - ylow) + 0.2, -0.01, 0.0, "wall")
    # the arch: its moulded ring, the jambs with carved panels, the keystone with a mask and garland (plate 19)
    a0, a1 = c - aw / 2, c + aw / 2
    pts = arc_pts(a0, a1, sp, aw / 2, 12)
    ring = arc_pts(a0 - 0.3, a1 + 0.3, sp, aw / 2 + 0.3, 12)
    for (p0, q0), (p1, q1) in zip(zip(pts[:-1], ring[:-1]), zip(pts[1:], ring[1:])):
        m.poly([(p0[0], p0[1], 0.15), (q0[0], q0[1], 0.15), (q1[0], q1[1], 0.15), (p1[0], p1[1], 0.15)], "marble")
    for s in (a0 - 0.45, a1):
        m.box(s, s + 0.45, 0.0, sp, 0.0, 0.16, "marble", skip=("back",))
        m.box(s + 0.12, s + 0.33, 0.5, sp - 0.4, 0.16, 0.21, "sculpt", skip=("back",))
        m.box(s - 0.05, s + 0.5, sp - 0.2, sp, 0.0, 0.25, "marble", skip=("back",))
    m.box(c - 0.25, c + 0.25, at - 0.05, at + 0.55, 0.0, 0.3, "sculpt", skip=("back",))
    # the side doors: moulded frames, a hood and a shell between scrolls (plate 19)
    for sx in (-1, 1):
        s = c + sx * dx
        P_.opening(s - dw / 2, s + dw / 2, 0.0, dh, 0.0, depth=0.4, kind="door", frame=0.3)
        m.box(s - dw / 2 - 0.42, s + dw / 2 + 0.42, dh + 0.3, dh + 0.48, 0.0, 0.32, "marble", skip=("back",))
        for sg in (-1, 1):
            P_.scroll(s + sg * (dw / 2 + 0.15), dh + 0.48, 0.7, 0.55, sx=sg, d=0.22, t=0.14)
        P_.shell(s, dh + 0.72, (V["door_crest"] - dh - 0.72) / 1.05, d=0.14)
    # the carved vines over the piers' faces, each from a vase (plate 19: on every pier between the openings and the columns)
    for sx in (-1, 1):
        for xs in (V["col_in"] - 0.85, (V["col_in"] + V["door_x"] - dw / 2) / 2 + 0.1, V["door_x"] + dw / 2 + 0.75, V["col_out"] - 0.75):
            vine(c + sx * xs, 0.55, V["cornice_in"] - 1.6, 0.03)
    # the free columns: plinth, base, shaft, a capital with volutes, a block over it in the entablature (plate 19)
    ph, ch, r = V["plinth"], V["col_h"], V["col_r"]
    for sx in (-1, 1):
        for xs in (V["col_out"], V["col_in"]):
            s = c + sx * xs
            q = (s, 0.0, 0.75)  # the shaft's middle in the face frame (lathe() draws in the current frame)
            m.box(s - 0.48, s + 0.48, 0.0, ph, 0.27, 1.23, "marble")
            m.lathe([(r + 0.12, ph), (r + 0.12, ph + 0.18), (r, ph + 0.3), (r * 0.9, ch - 0.6), (r + 0.06, ch - 0.45), (r + 0.18, ch)], 10, "marble", cx=q[0], cz=q[2])
            m.box(s - 0.5, s + 0.5, ch - 0.38, ch - 0.18, 0.4, 1.1, "sculpt")
            m.box(s - 0.45, s + 0.45, ch, cornice_y(s - c) - 0.25, 0.3, 1.2, "marble")
            # the carved vine winding round the shaft (S02 p.159: 'even over the faces of the pillars')
            vine_col((s, 0.0, 0.75), r, ph + 0.4, ch - 0.6)
    # the end bays: a pier with a sunk panel and its scrolled ornament (plate 19)
    for sx in (-1, 1):
        s = c + sx * (V["col_out"] + w / 2) / 2
        m.box(s - 0.55, s + 0.55, 0.9, V["cornice_out"] - 1.6, 0.0, 0.05, "panel", skip=("back",))
        m.box(s - 0.2, s + 0.2, V["cornice_out"] - 2.6, V["cornice_out"] - 1.9, 0.05, 0.12, "sculpt", skip=("back",))
        m.box(s - 0.08, s + 0.08, 1.4, V["cornice_out"] - 2.6, 0.05, 0.1, "sculpt", skip=("back",))
    m.box(0.0, w, 0.0, 0.35, 0.0, 0.2, "marble", skip=("back",))  # the plinth course
    # the entablature, following the cornice: architrave, frieze, the cornice projecting
    wavy_band(c, -0.1, w + 0.1, 0.0, 0.18, 0.0, 0.62, "marble")
    wavy_band(c, -0.05, w + 0.05, 0.18, 0.36, 0.0, 0.45, "marble")
    wavy_band(c, 0.0, w, 0.36, 0.95, 0.0, 0.2, "panel")
    wavy_band(c, 0.0, w, 0.95, 1.2, 0.0, 0.3, "marble")


def vine_col(q, r, y0, y1):
    """The vine round a column's shaft: a spiral band with leaves (plate 19, S02 p.159)."""
    n = 18
    prev = None
    for k in range(n + 1):
        y = y0 + (y1 - y0) * k / n
        a = k * 0.85
        x, z = q[0] + (r + 0.03) * math.cos(a), q[2] + (r + 0.03) * math.sin(a)
        if prev:
            m.box(min(prev[0], x) - 0.03, max(prev[0], x) + 0.03, prev[1], y + 0.02, min(prev[2], z) - 0.03, max(prev[2], z) + 0.03, "vine")
        prev = (x, y, z)


def crests():
    """Over the entablature, in the gate's middle plane (two-sided): the attic with its broken scroll pediment and the trophy group, the trophies over the columns,
    the towers over the side bays, the end finials (plate 19)."""
    w, d = V["w"], V["d"]
    zc = -d / 2
    m.cls = "doc"
    m.push(-w / 2, 0.0, zc, 0.0)
    c = w / 2
    yc = V["cornice_c"]
    # the attic: a block on the curve with a broken scroll pediment, the trophy group on it
    aw_ = V["attic_w"] / 2
    m.box(c - aw_ + 0.15, c + aw_ - 0.15, yc - 0.2, V["attic_top"] - 0.35, -0.6, 0.6, "marble")
    m.box(c - aw_, c + aw_, V["attic_top"] - 0.35, V["attic_top"], -0.7, 0.7, "marble")
    for sg in (-1, 1):
        P_.scroll(c + sg * (aw_ - 0.1), yc - 0.3, 1.3, 0.7, sx=sg, d=0.0, t=0.5)
    for k in range(7):  # the attic's fluted face
        x = c - 1.35 + k * 0.45
        m.box(x - 0.08, x + 0.08, yc + 0.1, V["attic_top"] - 0.5, 0.6, 0.66, "sculpt")
        m.box(x - 0.08, x + 0.08, yc + 0.1, V["attic_top"] - 0.5, -0.66, -0.6, "sculpt")
    trophy(c, V["attic_top"], V["trophy_c"], 1.4)
    S.kp("trophy_C_top", _w((c, V["trophy_c"], 0.0)))
    S.kp("attic_top_L", _w((c - aw_, V["attic_top"], 0.7)))
    S.kp("attic_top_R", _w((c + aw_, V["attic_top"], 0.7)))
    for sx, lr in ((-1, "L"), (1, "R")):
        # trophies over the inner columns, on blocks
        s = c + sx * V["col_in"]
        y0 = V["cornice_in"]
        m.box(s - 0.4, s + 0.4, y0 - 0.1, y0 + 0.45, -0.4, 0.4, "marble")
        trophy(s, y0 + 0.45, V["trophy_in"], 0.75)
        S.kp(f"trophy_in_{lr}_top", _w((s, V["trophy_in"], 0.0)))
        # trophies with a round shield over the outer columns
        s = c + sx * V["col_out"]
        y0 = V["cornice_out"]
        m.box(s - 0.45, s + 0.45, y0 - 0.1, y0 + 0.4, -0.45, 0.45, "marble")
        trophy(s, y0 + 0.4, V["trophy_out"], 0.9, shield=True)
        S.kp(f"trophy_out_{lr}_top", _w((s, V["trophy_out"], 0.0)))
        # the end finials (urns)
        s = c + sx * (w / 2 - 0.4)
        p = (s, 0.0, 0.0)
        m.lathe([(0.25, y0), (0.3, y0 + 0.15), (0.18, y0 + 0.25), (0.34, y0 + 0.55), (0.22, V["end_top"] - 0.25), (0.08, V["end_top"] - 0.1), (0.0, V["end_top"])], 8, "sculpt", cx=p[0], cz=p[2])
        S.kp(f"end_finial_{lr}_top", _w((s, V["end_top"], 0.0)))
        # the tower over the side bay: body with a cartouche and scrolls, flared cornice, concave pyramidal cap, lantern, urn
        s = c + sx * (V["col_out"] + V["col_in"]) / 2
        tw = V["tower_w"] / 2
        tb, tc, tcap, tt = V["tower_base"], V["tower_cornice"], V["tower_cap"], V["tower_top"]
        y_dip = cornice_y(sx * (V["col_out"] + V["col_in"]) / 2)
        m.box(s - tw + 0.3, s + tw - 0.3, y_dip - 0.2, tc - 0.25, -d / 2 + 0.3, d / 2 - 0.3, "wall")
        for dd in (d / 2 - 0.3, -d / 2 + 0.3):
            sg = 1 if dd > 0 else -1
            m.box(s - 0.55, s + 0.55, tb + 0.2, tc - 0.55, min(dd, dd + sg * 0.08), max(dd, dd + sg * 0.08), "panel")
            for so in (-1, 1):
                m.push(0, 0, dd + sg * 0.04, 0.0)
                P_.scroll(s + so * (tw - 0.35), y_dip, tb - y_dip + 0.6, 0.55, sx=-so, d=0.0, t=0.12)
                m.pop()
        m.box(s - tw - 0.05, s + tw + 0.05, tc - 0.25, tc, -d / 2 - 0.05, d / 2 + 0.05, "marble")
        cap_ring = lambda r_: [(s + r_ * a_, r_ * b_) for a_, b_ in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        prof = [(tw + 0.05, tc), (tw * 0.78, tc + 0.35), (tw * 0.55, tc + 0.9), (tw * 0.38, tcap - 0.45), (0.42, tcap - 0.3)]
        for (r0, y0_), (r1, y1_) in zip(prof[:-1], prof[1:]):
            ring0 = [(x, z * (d / 2 + 0.05) / (tw + 0.05)) for x, z in cap_ring(r0)]
            ring1 = [(x, z * (d / 2 + 0.05) / (tw + 0.05)) for x, z in cap_ring(r1)]
            m.frustum(ring0, ring1, y0_, y1_, "marble")
        m.box(s - 0.42, s + 0.42, tcap - 0.3, tcap + 0.05, -0.42, 0.42, "marble")
        p = (s, 0.0, 0.0)
        m.lathe([(0.3, tcap + 0.05), (0.36, tcap + 0.2), (0.2, tcap + 0.35), (0.4, tcap + 0.65), (0.3, tt - 0.35), (0.12, tt - 0.2), (0.2, tt - 0.1), (0.0, tt)], 10, "sculpt", cx=p[0], cz=p[2])
        S.kp(f"tower_{lr}_finial", _w((s, tt, 0.0)))
        S.kp(f"tower_{lr}_cap", _w((s, tcap, 0.0)))
        for so, lr2 in ((-1, "l"), (1, "r")):
            S.kp(f"tower_{lr}_cornice_{lr2}", _w((s + so * (tw + 0.05), tc, d / 2 + 0.05)))
    m.pop()


def trophy(s, y0, top, wd, shield=False):
    """A group of arms and banners on a block, as a flat cut-out with a helmet-like crown (plate 19: trophies over the centre and the columns); in the face frame, two-sided."""
    h = top - y0
    outline = [(s - wd / 2, y0), (s + wd / 2, y0), (s + wd * 0.6, y0 + h * 0.35), (s + wd * 0.3, y0 + h * 0.75), (s + 0.12, y0 + h * 0.82), (s, y0 + h), (s - 0.12, y0 + h * 0.82), (s - wd * 0.3, y0 + h * 0.75), (s - wd * 0.6, y0 + h * 0.35)]
    P_.slab(outline, -0.18, 0.18, "sculpt")
    for k in (-1, 1):  # the crossed staffs and banners
        m.poly([(s + k * wd * 0.15, y0 + 0.05, 0.2), (s + k * wd * 0.2, y0 + 0.05, 0.2), (s - k * wd * 0.55, y0 + h * 0.85, 0.2), (s - k * wd * 0.6, y0 + h * 0.85, 0.2)], "gilt")
        m.poly([(s - k * wd * 0.6, y0 + h * 0.85, -0.2), (s - k * wd * 0.55, y0 + h * 0.85, -0.2), (s + k * wd * 0.2, y0 + 0.05, -0.2), (s + k * wd * 0.15, y0 + 0.05, -0.2)], "gilt")
    if shield:
        P_.wreath(s, y0 + h * 0.45, wd * 0.32, tube=0.08, n=12, mat="marble")
        m.poly([(s + wd * 0.26 * math.cos(2 * math.pi * k / 12), y0 + h * 0.45 + wd * 0.26 * math.sin(2 * math.pi * k / 12), 0.21) for k in range(12)], "gilt")
        m.poly([(s + wd * 0.26 * math.cos(2 * math.pi * k / 12), y0 + h * 0.45 + wd * 0.26 * math.sin(2 * math.pi * k / 12), -0.21) for k in range(12)][::-1], "gilt")


def body():
    w, d = V["w"], V["d"]
    hw = w / 2
    S.footing(rect(-hw - 0.15, hw + 0.15, -d - 0.15, 1.35), 0.0, "marble", name="gate_foot", lid=False)
    m.flat(rect(-hw - 0.15, hw + 0.15, -d - 0.15, 1.35), 0.02, "pave")
    m.cls = "doc"
    face((-hw, 0.0), (hw, 0.0))
    front(doc=True)
    m.pop()
    face((hw, -d), (-hw, -d))
    front(doc=False)
    m.pop()
    # the ends: a plain face with a panel, the cornice carried round (fill)
    m.cls = "fill"
    for a, b in (((hw, 0.0), (hw, -d)), ((-hw, -d), (-hw, 0.0))):
        L = face(a, b)
        P_.wall_holes(0.0, L, 0.0, V["cornice_out"] - 1.2, [], "wall")
        m.box(0.4, L - 0.4, 1.0, V["cornice_out"] - 1.8, 0.0, 0.05, "panel", skip=("back",))
        P_.entablature(0.0, L, V["cornice_out"], h=1.2, out=0.45, ends=False)
        m.pop()
    # the passages and the side rooms: the arch's barrel, the doors' reveals, a cross wall in each side room (S02: 'the side passages leading through side rooms'), the top a lead flat
    aw, at = V["arch_w"], V["arch_top"]
    sp = at - aw / 2
    pts = arc_pts(-aw / 2, aw / 2, sp, aw / 2, 12)
    for p0, p1 in zip(pts[:-1], pts[1:]):
        m.poly([(p0[0], p0[1], 0.0), (p1[0], p1[1], 0.0), (p1[0], p1[1], -d), (p0[0], p0[1], -d)], "wall")
    for s in (-aw / 2, aw / 2):
        m.poly([(s, 0.0, 0.0), (s, sp, 0.0), (s, sp, -d), (s, 0.0, -d)], "wall")
    for sx in (-1, 1):
        s = sx * V["door_x"]
        for e in (s - V["door_w"] / 2 - 0.9, s + V["door_w"] / 2 + 0.9):
            m.box(e - 0.1, e + 0.1, 0.0, V["door_h"] + 0.8, -d + 0.4, -0.4, "wall")
        m.box(s - V["door_w"] / 2 - 0.9, s + V["door_w"] / 2 + 0.9, V["door_h"] + 0.8, V["door_h"] + 0.85, -d + 0.4, -0.4, "wall")
        m.flat(rect(s - V["door_w"] / 2 - 0.9, s + V["door_w"] / 2 + 0.9, -d + 0.4, -0.4), 0.03, "pave")
    xs = [-hw - 0.4, hw + 0.4]
    m.flat(rect(xs[0], xs[1], -d - 0.4, 0.4), V["cornice_in"] - V["cornice_dip"] - 0.05, "coping")
    m.cls = "doc"
    for sx, lr in ((-1, "L"), (1, "R")):
        S.kp(f"end_{lr}_foot", (sx * hw, 0.0, 0.0), anchor=True)
        S.kp(f"end_{lr}_top", (sx * (hw + 0.62), V["cornice_out"], 0.62))
        for nm, xs_ in (("out", V["col_out"]), ("in", V["col_in"])):
            S.kp(f"col_{nm}_{lr}_cap", (sx * xs_, V["col_h"], 0.75 + V["col_r"]))
            S.kp(f"col_{nm}_{lr}_foot", (sx * xs_, V["plinth"], 0.75 + V["col_r"]), anchor=True)
            S.kp(f"cornice_{nm}_{lr}", (sx * xs_, cornice_y(xs_), 0.62))
        S.kp(f"cornice_dip_{lr}", (sx * (V["col_out"] + V["col_in"]) / 2, cornice_y((V["col_out"] + V["col_in"]) / 2), 0.62))
        S.kp(f"door_{lr}_head", (sx * V["door_x"], V["door_h"], 0.0))
        S.kp(f"door_{lr}_crest", (sx * V["door_x"], V["door_crest"], 0.2))
        S.kp(f"arch_foot_{lr}", (sx * aw / 2, 0.0, 0.0), anchor=True)
        S.kp(f"arch_spring_{lr}", (sx * aw / 2, sp, 0.0))
        S.JOINTS.append([f"col_{lr}_out", sx * V["col_out"], S.gy(sx * V["col_out"], 0.75) - 0.05, 0.75, "column plinth"])
    S.kp("arch_crown", (0.0, at, 0.0))
    S.kp("cornice_C", (0.0, V["cornice_c"], 0.62))
    S.FOOTPRINTS.append(rect(-hw - 0.2, -aw / 2 - 0.5, -d - 0.2, 1.3))
    S.FOOTPRINTS.append(rect(aw / 2 + 0.5, hw + 0.2, -d - 0.2, 1.3))
    S.entry("west_arch", 0.0, 1.6)
    S.entry("east_arch", 0.0, -d - 0.8)
    S.CLEAR.append(rect(-hw - 1.0, hw + 1.0, -d - 2.0, 3.0))


def build():
    global S, m, P_
    S = Site("XY13-M56")
    m = Mesh(COL)
    S.m = m
    P_ = Parts(m, rail_h=1.0, baluster_segs=6)
    m.cls = "doc"
    body()
    crests()


def summary(tris, fill, size):
    rows = [
        ["West front", f"{V['w']:g} m wide (plate 19 on the dossier's weak module, C): the arch {V['arch_w']:g} m wide to {V['arch_top']:g} m between two free columns, a square-headed door {V['door_w']:g} × {V['door_h']:g} m either side under a shell, the end bays with their panels; four columns {V['col_h']:g} m, the carved vines over the piers and round the shafts (S02 p.159)"],
        ["Cornice and crests", f"the wavy cornice at {V['cornice_out']:g} m over the outer columns and {V['cornice_in']:g} m over the inner ones, rising to {V['cornice_c']:g} m over the arch; the attic with its broken scroll pediment ({V['attic_top']:g} m) and the trophy group ({V['trophy_c']:g} m), trophies over the columns, the end urns (plate 19, C)"],
        ["Towers", f"a tower over each side bay, {V['tower_w']:g} m square: a body with scrolls and a cartouche, a flared cornice at {V['tower_cornice']:g} m, a concave pyramidal cap, a lantern and an urn to {V['tower_top']:g} m (plate 19, C)"],
        ["Assumed", f"the depth ({V['d']:g} m), the east face, the ends, the passages and the side rooms, carried round from the west front (C, the pale tint with conf=1)"],
    ]
    return {
        "id": "XY13", "aliases": [], "name": "螺蛳牌楼 Luosi Pailou", "glb": "model.glb", "position": S.pos, "rotationY": S.rot,
        "line": "Modelled from plate 19 of 1783-86, drawn frontally; the plan draws only an ornamental figure and no photograph of it is in hand, so every figure is a reading (C) on a weak module.",
        "rows": rows,
        "caption": {"frontage_m": V["w"], "depth_m": V["d"], "eave_m": V["cornice_out"], "ridge_m": V["tower_top"], "assumed": True, "confidence": "C"},
        # the walls layer's gate G39, 'wall gap east of 线法山, towards 螺蛳牌楼', 20 m west of the gate on its axis: S01 draws a gap with no gate, and plate 19, taken from about 36 m
        # west on the axis, looks through that place and shows paving and clipped trees there; the kit's default gate hall GB39 is a phantom in the plate's view
        "hides": ["GB39"],
        "tris": tris, "fill_tris": fill, "glb_bytes": size,
    }


def main():
    build()
    size = m.write_glb(HERE / "model.glb", "XY13 螺蛳牌楼 Luosi Pailou", extras={"id": "XY13"})
    tris = m.count()
    prims = {k: len(v["idx"]) // 3 for k, v in sorted(m.prims.items())}
    fill = sum(n for k, n in prims.items() if k.endswith("~fill"))
    S.write(HERE, "XY13", ["XY13"], P, "x south along the west front (to the right seen from the west), y up from the ground at the gate's box, z west (out of the front); the origin at the west front's middle; metres", summary(tris, fill, size))
    print(f"model.glb {size / 1e6:.2f} MB, {tris} triangles ({fill} fill), {len(S.KP)} key points, {len(S.JOINTS)} joints, {len(S.ENTRIES)} entries; position {S.pos} rotY {S.rot}")


if __name__ == "__main__":
    main()
