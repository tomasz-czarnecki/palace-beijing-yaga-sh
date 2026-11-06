#!/usr/bin/env python3
"""养雀笼 Yangque Long (XY05), the aviary gate of the Xiyang Lou, the thirteenth detailed model (Round 26): from the west a Chinese gate of five roofs (S02 p.147; S310):
the portico of two tall columns under the highest roof with its finials and crest, the arched door, the two wings whose walls are the cages (a net over the wall, a fan-headed
window in each), their columns and roofs, the lowest roofs at the ends, the two statues on lotus pedestals (plate 6); from the east a European gate front, concave in plan:
the end pavilions of two columns and a pier, the shell niches with their fountains, the arch with its iron gate under a scrolled cartouche, lattice panels, the cornice,
the balustrade with its finials and the crest over the middle (plate 7; Child's photograph of the 1870s, P0192; the ruin photographs P0175, P0178, P0168).
Plain geometry, one GLB (scripts/model_mesh.py) with every figure in params.json; the method is the pilot's (models/XY01-xieqiqu/README.md).

  uv run python models/XY05-yangque-long/yangquelong.py

Writes, beside this file: model.glb, params.json, keypoints.json, joints.json, summary.json (models/README.md).
Frame (scripts/model_site.py): origin at the front middle of the gate's box XY05-M25, which faces west: x along the west front to the right as one faces it from the west
(south), y up from the box's ground, z west (out of the west front). The east front lies at z about -11.6.
Grades: what plate 6, plate 7 and the photographs show is `doc`; the ends of the range, the roof terrace, the passage's inside and the walls beyond the gate are `fill`
(assumed, C). Every figure is C unless params.json says otherwise.
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

P = {
    "w": (13.9, "S01;S71", "C", "the gate range N-S: the plan 13.89 m (b); plates 6 and 7 both 13.9 m on their modules (c); on plate 6 the wings' outer columns 677 px apart, the module of the west front's readings (48.7 px/m)"),
    "d": (11.6, "S01", "C", "west front to east front with the centre's projection: the plan 11.65 m (b)"),
    "range_w": (-2.5, "S71;S01", "C", "the range's west wall (the door and the cage walls) behind the columns' line: on plate 6 the door's sill stands 6 px above the columns' feet, about 2 m further at the plate's 31 m (Round 26 readings); S01's centre projects 5 m west, with its steps"),
    "col_z": (-0.45, "S71", "C", "the west columns' line: the portico's and the wings' outer columns stand in one plane, their feet at the same height on plate 6 (y 962-966)"),
    "range_e": (-9.8, "S71;S70", "C", "the east front's middle (the arch) from the west front: concave, the ends 1.8 m further east (plate 7: the end pavilions drawn 14% larger than the centre's piers; P0192: the cornice and the balustrade curve back to the middle)"),
    "centre_bay": (5.1, "S71;S70", "C", "the east centre bay over its piers: plate 7 the piers' capitals 270 px apart against the niches' 448 (P0192 595 and 1024): the piers' middles 4.4 m apart"),
    "end_pav": (2.35, "S71;S70", "C", "each end pavilion of the east front, two round columns and a pier: plate 7, the outer columns' capitals 833 px apart (13.4 m)"),
    "arch_w": (2.1, "S71;S70", "C", "the east arch's opening: plate 7 125 px (2.0-2.1 m at the plate's 60 px/m)"),
    "arch_spring": (3.55, "S71", "C", "the arch's springing above the threshold: plate 7, the impost 211 px above it, 1.69 times the opening's width"),
    "arch_top": (4.6, "S70;S71", "C", "the arch's crown: a half circle on P0192, P0175, P0178, P0168 (the rise 0.50-0.53 of the width); plate 7 draws it 1.31 times taller (Q293): the stone as it stood wins"),
    "col_e": (4.6, "S70;S71", "C", "the east columns and piers to their capitals' tops: P0192, the piers' capitals one arch-width above the imposts (plate 7 0.81): 5.6 m above the threshold with the pedestals"),
    "ped_e": (1.0, "S71;S70", "C", "the pedestals under the east columns: plate 7, P0192"),
    "cornice_e": (6.9, "S70;S71", "C", "the east main cornice's top: P0192, about 0.66 arch-widths over the piers' capitals; plate 7's cornice ends 441 px over the ends' feet; the dossier's 6.2 m (Round 6) on another module"),
    "rail_e": (8.0, "S70;S71", "C", "the east balustrade's top: P0192 and plate 7 (61 px over the cornice's ends)"),
    "crest_e": (9.0, "S71", "C", "the crest over the centre: plate 7, 538 px over the threshold"),
    "finial_e": (1.4, "S71", "C", "the finials on the balustrade's pedestals above the rail: plate 7 (the outer ones 86 px over the pedestals' caps)"),
    "niche_w": (1.25, "S70", "C", "the shell niches' openings: P0192, 0.59 arch-widths"),
    "niche_top": (4.45, "S70;S71", "C", "the niche's crown: P0192 (fitted: 4.7 m sat 0.25 m high on it), plate 7 draws it higher (0.5 m), as it draws the arch (Q293)"),
    "basin_y": (1.2, "S70;S71", "C", "the shell basin's rim: P0192, 1.12 arch-widths below the imposts; plate 7 93 px over the threshold"),
    "col_c_w": (2.28, "S71", "C", "the west portico's columns either side of the axis: plate 6, 222 px apart (4.56 m)"),
    "col_c_h": (6.4, "S71", "C", "the portico's columns to their tops under the beam: plate 6, 314 px over their feet"),
    "eave_c": (7.0, "S71", "C", "the portico roof's eave tips: plate 6, 343-349 px; 6.1 m across them"),
    "roof_c_d": (2.2, "S71", "C", "the depth of the west roofs over the columns' line: plate 6, the central ridge 4.1 m between eave tips 6.1 m apart (hips 1.0 m), the wings' ridges as long: shallow roofs like a 牌坊's (S310: 'from the west like a Chinese five-roof 牌坊')"),
    "ridge_c": (7.9, "S71", "C", "the central ridge: plate 6, 392 px over the sill; 4.1 m long"),
    "finial_c": (9.6, "S71", "C", "the central finials' tips: plate 6, 474 px"),
    "eave_wing": (5.1, "S71", "C", "the wings' outer eave tips: plate 6, 252 px over the columns' feet; 15.3 m across the two"),
    "ridge_wing": (5.9, "S71", "C", "the wings' ridge's outer end: plate 6, 290 px"),
    "wing_cap": (4.6, "S71", "C", "the wings' outer columns to their tops: plate 6, 226 px"),
    "eave_end": (3.5, "S71", "C", "the lowest roofs beyond the wings: plate 6, eave about y 800 (the reader)"),
    "cage_x": (4.0, "S71", "C", "the cage windows' middles either side of the axis: plate 6, 1001 and 1383 px (±3.9 m at the columns' module, a little more at the wall)"),
    "door_w": (1.8, "S71", "C", "the west door: plate 6, 77 x 106 px on the dossier's reading (1.9 x 2.6 m)"),
    "door_h": (3.7, "S71", "C", "the west door's crown, round-headed in a carved frame: plate 6, 167 px over the sill at the wall's plane"),
    "cage_win_w": (2.0, "S71", "C", "the cage walls' fan-headed windows: plate 6"),
    "cage_win_top": (3.4, "S71", "C", "their crown: plate 6, 148 px over the sill at the wall's plane"),
    "flank_h": (3.2, "S71", "C", "the low walls either side of the east front, with panels and pilasters: plate 7; their length beyond the gate a guess (5 m)"),
    "statue_h": (1.9, "S71", "C", "the statues on their lotus pedestals before the cage windows: plate 6, their heads 81 px over the sill, nearer than the columns"),
}
V = {k: v[0] for k, v in P.items()}

COL = {
    "brick": "#9c8f80", "marble": "#ebe6da", "wall": "#d9d2c3", "panel": "#c2bbab", "sculpt": "#d6cfbf", "glaze": "#3f8a86", "joint": "#a39a8a",
    "glass_win": "#2e4a4f", "door": "#4a3b2c", "roof": "#46705c", "roofedge": "#3a5e4d", "ridge": "#c9a245", "gilt": "#b59a52", "iron": "#2b2c2b",
    "net": "#3d4340", "cage": "#2a2d2b", "column": "#b34a3a", "pave": "#c9c2b2", "step": "#d2ccbe", "water": "#6f9fb0", "jet": "#d8ecf2", "lead": "#9a968e",
}

S = None
m = None
P_ = None


def rect(x0, x1, z0, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def face(a, b):
    """A face frame from a to b (plan x z): s along, y up, d out of the face to the right of a->b seen from above... the left of the walker."""
    dx, dz = b[0] - a[0], b[1] - a[1]
    m.push(a[0], 0.0, a[1], math.atan2(-dz, dx))
    return math.hypot(dx, dz)


# ------------------------------------------------------------------ the range: walls, roof terrace, passage
def east_line():
    """The east front in plan from south to north (as seen from the east: left to right), concave: the end pavilions forward, the niche bays slanting back, the centre."""
    hw = V["w"] / 2
    ze_c = V["range_e"]
    ze_o = -V["d"]
    ep, cb = V["end_pav"], V["centre_bay"] / 2
    return [(hw, ze_o), (hw - ep, ze_o), (cb, ze_c), (-cb, ze_c), (-(hw - ep), ze_o), (-hw, ze_o)]


def range_body():
    hw = V["w"] / 2
    zw = V["range_w"]
    el = east_line()
    # the outline of the range: the west wall, the north end, the east front, the south end
    outline = [(-hw, zw), (hw, zw)] + el + []
    outline = [(-hw, zw), (hw, zw), (hw, -V["d"])] + el[1:-1] + [(-hw, -V["d"])]
    S.footing(outline, 0.25, "marble", name="range_plinth", lid=True)
    yc = V["cornice_e"]
    # the ends (north and south): plain walls with pilasters at the corners (fill)
    for a, b in (((hw, zw), (hw, -V["d"])), ((-hw, -V["d"]), (-hw, zw))):
        m.cls = "fill"
        L = face(a, b)
        P_.wall_holes(0.0, L, 0.0, yc - 1.0, [], "wall")
        for k in range(3):  # blind arched panels between pilasters and a cartouche over the middle: carried from the fronts (fill, C)
            sc = L * (k + 1) / 4
            m.box(sc - 0.6, sc + 0.6, 1.0, 3.6, 0.0, 0.04, "panel", skip=("back",))
            for p0, p1 in zip(arc_pts(sc - 0.6, sc + 0.6, 3.6, 0.6, 6)[:-1], arc_pts(sc - 0.6, sc + 0.6, 3.6, 0.6, 6)[1:]):
                m.poly([(sc, 3.6, 0.04), (p0[0], p0[1], 0.04), (p1[0], p1[1], 0.04)], "panel")
            m.box(sc - 0.72, sc + 0.72, 0.9, 1.0, 0.0, 0.12, "marble", skip=("back",))
            if k < 2:
                P_.pilaster(L * (k + 1.5) / 4, 0.25, yc - 1.0, w=0.45, out=0.12, flutes=False)
        P_.cartouche(L / 2, yc - 1.6, 0.8, 0.6)
        P_.pilaster(0.35, 0.25, yc - 1.0, w=0.6, out=0.15, flutes=False)
        P_.pilaster(L - 0.35, 0.25, yc - 1.0, w=0.6, out=0.15, flutes=False)
        P_.entablature(0.0, L, yc, h=1.0, out=0.35)
        m.pop()
    m.cls = "fill"
    # the roof terrace behind the east balustrade, leaded (assumed), and its low parapet on the west
    m.flat(outline, yc - 0.05, "lead")
    m.cls = "doc"
    S.FOOTPRINTS.append(outline)
    for i, (x, z) in enumerate(outline):
        S.JOINTS.append([f"range_{i}", x, S.gy(x, z) - 0.15, z, "wall foot"])
    # the passage through: walls either side, a flat ceiling (fill)
    m.cls = "fill"
    for sx in (-1, 1):
        x = sx * 1.15
        m.box(x - 0.02, x + 0.02, 0.25, 4.7, V["range_e"] + 0.1, zw - 0.1, "wall")
    m.box(-1.15, 1.15, 4.7, 4.8, V["range_e"] + 0.1, zw - 0.1, "wall")
    m.flat(rect(-1.15, 1.15, V["range_e"], zw), 0.27, "pave")
    m.cls = "doc"
    return outline


# ------------------------------------------------------------------ the west: portico, door, cage wings, roofs, statues
def west_front():
    """Plate 6: the columns' line (the portico's two and each wing's corner column) before the range's west wall; in the wall the door and, either side, the cage walls
    (a net over the opening, a fan-headed window in it); the open bay at each wing's end with a second column behind the corner; the roofs in three heights."""
    hw = V["w"] / 2
    zw, zc = V["range_w"], V["col_z"]
    pc, ph = V["col_c_w"], V["col_c_h"]
    m.cls = "doc"
    m.push(-hw, 0.0, zw, 0.0)  # face frame: s from the north end (x -hw) southwards, d west
    dw, dh = V["door_w"] / 2, V["door_h"]
    wy = V["wing_cap"] + 0.2
    cw = V["cage_win_w"] / 2
    cage_x = [hw - V["cage_x"], hw + V["cage_x"]]
    cage_open = [(s - 1.45, s + 1.45) for s in cage_x]
    holes = [(hw - dw, hw + dw, 0.25, dh - dw, dw)] + [(a, b, 0.6, wy - 0.4, 0.0) for a, b in cage_open]
    P_.wall_holes(0.0, 2 * hw, 0.25, ph, holes, "wall")
    P_.opening(hw - dw, hw + dw, 0.25, dh - dw, dw, depth=0.5, kind="door", frame=0.22)
    m.box(hw - dw - 0.4, hw + dw + 0.4, dh + 0.1, dh + 0.5, 0.0, 0.25, "sculpt", skip=("back",))  # the carved hood (plate 6)
    # over the door between the portico's columns: a carved transom of three framed panels and a scrolled frame (plate 6)
    for k, (s0, s1) in enumerate(((hw - 1.9, hw - 0.75), (hw - 0.65, hw + 0.65), (hw + 0.75, hw + 1.9))):
        y0, y1 = dh + 0.75, V["col_c_h"] - 0.35
        m.box(s0, s1, y0, y1, 0.0, 0.05, "panel", skip=("back",))
        for (x0, x1, yy0, yy1) in ((s0 - 0.08, s0, y0, y1), (s1, s1 + 0.08, y0, y1), (s0 - 0.08, s1 + 0.08, y1, y1 + 0.08), (s0 - 0.08, s1 + 0.08, y0 - 0.08, y0)):
            m.box(x0, x1, yy0, yy1, 0.0, 0.12, "sculpt", skip=("back",))
        if k == 1:
            P_.cartouche(hw, (y0 + y1) / 2, 0.7, 0.8)
    for sgn in (-1, 1):  # scrolls at the door frame's shoulders
        m.poly([(hw + sgn * (dw + 0.15), dh + 0.1, 0.2), (hw + sgn * (dw + 0.75), dh + 0.1, 0.2), (hw + sgn * (dw + 0.55), dh + 0.65, 0.2)], "sculpt")
    for (x0, x1), s in zip(cage_open, cage_x):
        y0, y1 = 0.6, wy - 0.4
        m.box(x0, x1, y0, y1, -0.9, -0.85, "cage")  # the bird room behind, dark
        for side in ((x0, x0 + 0.05), (x1 - 0.05, x1)):
            m.box(side[0], side[1], y0, y1, -0.9, 0.0, "wall", skip=("back",))
        m.box(x0, x1, y1 - 0.05, y1, -0.9, 0.0, "wall")
        m.box(x0, x1, y0, y0 + 0.05, -0.9, 0.0, "wall")
        x = x0 + 0.2  # the net: a lattice of thin bars over the opening (plate 6 draws the wall as a net)
        while x < x1 - 0.1:
            m.box(x - 0.015, x + 0.015, y0, y1, -0.08, -0.05, "net", skip=("back",))
            x += 0.2
        y = y0 + 0.2
        while y < y1 - 0.1:
            m.box(x0, x1, y - 0.015, y + 0.015, -0.08, -0.05, "net", skip=("back",))
            y += 0.2
        a0, a1 = s - cw, s + cw  # the fan-headed window: an arched frame with radiating bars, in the net (plate 6)
        yt = V["cage_win_top"]
        ys = yt - cw
        pts = arc_pts(a0, a1, ys, cw, 10)
        for p0, p1 in zip(pts[:-1], pts[1:]):
            m.box(min(p0[0], p1[0]) - 0.04, max(p0[0], p1[0]) + 0.04, min(p0[1], p1[1]) - 0.04, max(p0[1], p1[1]) + 0.04, -0.04, 0.06, "marble", skip=("back",))
        for x in (a0, a1):
            m.box(x - 0.08, x + 0.08, 0.9, ys, -0.04, 0.06, "marble", skip=("back",))
        m.box(a0 - 0.1, a1 + 0.1, 0.82, 0.92, -0.04, 0.1, "marble", skip=("back",))
        m.box(a0, a1, ys - 0.04, ys + 0.04, -0.04, 0.05, "marble", skip=("back",))
        for j in range(1, 8):
            t = math.pi * j / 8
            m.poly([(s - 0.02, ys, 0.02), (s + 0.02, ys, 0.02), (s + cw * math.cos(t) + 0.02, ys + cw * math.sin(t), 0.02), (s + cw * math.cos(t) - 0.02, ys + cw * math.sin(t), 0.02)], "marble")
    m.pop()
    for sx, lr in ((-1, "L"), (1, "R")):
        S.kp(f"w_cagewin_{lr}_head", (sx * V["cage_x"], V["cage_win_top"], zw))
        S.kp(f"w_cagewin_{lr}_sill", (sx * V["cage_x"], 0.9, zw))
    S.kp("w_door_head", (0.0, dh, zw))
    S.kp("w_door_sill", (0.0, 0.25, zw), anchor=True)
    # the portico: two tall round columns, the beam, its side frames back to the wall, the highest roof with finials and the crest (plate 6)
    for sx, lr in ((-1, "L"), (1, "R")):
        x = sx * pc
        S.footing(rect(x - 0.42, x + 0.42, zc - 0.42, zc + 0.42), 0.35, "marble", name=f"w_col_C_{lr}")
        m.lathe([(0.32, 0.35), (0.3, 0.5), (0.27, ph - 0.3), (0.31, ph - 0.15), (0.31, ph)], 10, "column", cx=x, cz=zc)
        S.kp(f"w_col_C_{lr}_foot", (x, 0.35, zc + 0.3), anchor=True)
        S.kp(f"w_col_C_{lr}_cap", (x, ph, zc + 0.3))
        m.box(x - 0.1, x + 0.1, ph - 1.1, ph, zw, zc - 0.3, "marble")  # the portico's side beams back to the wall
    yb = V["eave_c"] - 0.25
    m.box(-pc - 0.45, pc + 0.45, ph, yb, zc - 0.35, zc + 0.35, "marble")
    for sx in (-1, 1):  # the carved brackets in the portico's upper corners (plate 6: scrolled spandrels)
        x = sx * (pc - 0.3)
        m.poly([(x, ph - 1.0, zc + 0.36), (x, ph, zc + 0.36), (x - sx * 0.9, ph, zc + 0.36)], "sculpt")
    m.box(-pc - 0.45, pc + 0.45, ph - 0.2, yb, zw, zc - 0.35, "wall")
    # a shallow roof over the columns' line, like a 牌坊's: plate 6 draws its ridge 4.1 m long between eave tips 6.1 m apart, so the hips run back 1.0 m (Round 26 fit)
    r = P_.roof_hip(0.0, zc - 0.2, 3.05, V["roof_c_d"] / 2, V["eave_c"], V["ridge_c"], n=6, lift=0.35, ridge_y=0.15, ends=False)
    m.cls = "fill"
    m.box(-pc - 0.45, pc + 0.45, yb - 0.05, yb + 0.05, zw, zc - 0.35, "wall")  # the portico's ceiling behind the roof
    m.cls = "doc"
    S.kp("w_roof_C_eave_L", r["eaves"][(-1, 1)])
    S.kp("w_roof_C_eave_R", r["eaves"][(1, 1)])
    ridge = sorted(r["ridge"], key=lambda p: p[0])
    for p, lr in zip(ridge, ("L", "R")):
        y = p[1]
        S.kp(f"w_ridge_C_{lr}", p)
        top = V["finial_c"]
        m.box(p[0] - 0.25, p[0] + 0.25, y - 0.1, y + 0.4, p[2] - 0.25, p[2] + 0.25, "ridge")
        m.lathe([(0.24, y + 0.4), (0.16, y + 0.55), (0.3, y + 0.85), (0.14, y + 1.1), (0.22, y + 1.3), (0.06, top - 0.12), (0.0, top)], 8, "gilt", cx=p[0], cz=p[2])
        S.kp(f"w_finial_C_{lr}", (p[0], top, p[2]))
    zr, yr = ridge[0][2], ridge[0][1]
    crest = [(-0.8, yr), (-0.75, yr + 0.45), (-0.35, yr + 0.3), (-0.22, yr + 0.75), (0.0, yr + 0.55), (0.22, yr + 0.75), (0.35, yr + 0.3), (0.75, yr + 0.45), (0.8, yr)]
    for dz in (-0.08, 0.08):
        m.poly([(x, y, zr + dz) for x, y in crest], "gilt")
    S.kp("w_crest_C_top", (0.0, yr + 0.75, zr))
    # the wings: the corner column on the columns' line and one behind it (the open bay), a beam along the front, the roof, finials (plate 6)
    ye, yc_ = V["eave_wing"], V["wing_cap"]
    for sx, lr in ((-1, "L"), (1, "R")):
        xo = sx * (hw - 0.3)
        for k, z in enumerate((zc, (zc + zw) / 2 - 0.2)):
            S.footing(rect(xo - 0.32, xo + 0.32, z - 0.32, z + 0.32), 0.3, "marble", name=f"w_wingcol_{lr}{k}")
            m.lathe([(0.24, 0.3), (0.21, 0.45), (0.19, yc_ - 0.15), (0.22, yc_)], 8, "column", cx=xo, cz=z)
        S.kp(f"w_wing_{lr}_col_out_foot", (xo, 0.3, zc + 0.2), anchor=True)
        S.kp(f"w_wing_{lr}_col_out_cap", (xo, yc_, zc + 0.2))
        x0, x1 = sorted((sx * (pc + 0.45), sx * (hw + 0.05)))
        m.box(x0, x1, yc_, yc_ + 0.45, zc - 0.3, zc + 0.3, "marble")
        m.box(x0, x1, yc_ + 0.3, ye - 0.15, zw, zc - 0.3, "wall", skip=("front", "back"))
        for k in range(3):  # the hanging carved panels under the beam between the columns (plate 6)
            xs = x0 + (x1 - x0) * (k + 0.5) / 3
            m.box(xs - 0.5, xs + 0.5, yc_ - 0.45, yc_, zc + 0.12, zc + 0.2, "sculpt")
        cxw = (x0 + x1) / 2
        rw = P_.roof_hip(cxw, zc - 0.2, (x1 - x0) / 2 + 0.75, V["roof_c_d"] / 2, ye, V["ridge_wing"], n=5, lift=0.3, ridge_y=0.15, ends=False)
        m.cls = "fill"
        m.box(x0, x1, ye - 0.15, ye - 0.05, zw, zc - 0.3, "wall")  # the wing's ceiling between the beam and the wall
        m.cls = "doc"
        S.kp(f"w_wing_{lr}_eave_out", rw["eaves"][(sx, 1)])
        ro = max(rw["ridge"], key=lambda p: sx * p[0])
        S.kp(f"w_wing_{lr}_ridge_out", ro)
        for p in rw["ridge"]:
            y = p[1]
            m.lathe([(0.2, y), (0.14, y + 0.2), (0.26, y + 0.5), (0.11, y + 0.8), (0.0, y + 1.15)], 8, "gilt", cx=p[0], cz=p[2])
        # the lowest roof at the end: a short covered bay beyond the range on the wall that runs on (plate 6; its length beyond the box assumed)
        m.cls = "fill"
        xe0, xe1 = sorted((sx * (hw + 0.05), sx * (hw + 2.2)))
        m.box(xe0, xe1, -0.15, V["eave_end"] - 0.25, zw - 0.3, zw + 0.3, "wall")
        S.JOINTS.append([f"endwall_{lr}", sx * (hw + 2.2), S.gy(sx * (hw + 2.2), zw) - 0.15, zw, "wall foot"])
        P_.roof_hip((xe0 + xe1) / 2, zw + 0.4, (xe1 - xe0) / 2 + 0.3, 1.2, V["eave_end"], V["eave_end"] + 0.7, n=4, lift=0.2, ridge_y=0.12, ends=False)
        S.FOOTPRINTS.append(rect(xe0, xe1, zw - 0.35, zw + 0.35))
        m.cls = "doc"
    # the statues on lotus pedestals before the cage windows (plate 6); the figures' form assumed
    for sx, lr in ((-1, "L"), (1, "R")):
        x, z = sx * V["cage_x"], zc + 0.9
        S.footing(rect(x - 0.45, x + 0.45, z - 0.45, z + 0.45), 0.2, "marble", name=f"statue_{lr}")
        m.lathe([(0.5, 0.2), (0.56, 0.38), (0.36, 0.52), (0.28, 0.62), (0.44, 0.8), (0.36, 0.9)], 10, "sculpt", cx=x, cz=z)
        m.lathe([(0.28, 0.9), (0.3, 1.25), (0.22, 1.55), (0.16, 1.7), (0.2, 1.8), (0.0, V["statue_h"])], 8, "sculpt", cx=x, cz=z)
        S.kp(f"w_statue_{lr}_top", (x, V["statue_h"], z))
    # the paved walk and the floor under the columns (plate 6), the entry
    y = max(S.gy(x, z) for x, z in rect(-3.0, 3.0, 0.0, 6.0)) + 0.02
    m.flat(rect(-1.6, 1.6, 0.5, 6.0), y, "pave")
    m.prism(rect(-hw, hw, zw, 0.5), min(S.gy(x, z) for x, z in rect(-hw, hw, zw, 0.5)) - 0.15, 0.3, "step")
    S.FOOTPRINTS.append(rect(-hw, hw, zw, 0.5))
    S.entry("west_portico", 0.0, 1.2)
    S.CLEAR.append(rect(-hw - 0.5, hw + 0.5, -0.5, 6.5))


# ------------------------------------------------------------------ the east: the concave European front
def east_front():
    el = east_line()
    yc, yr = V["cornice_e"], V["rail_e"]
    ped, colh = V["ped_e"], V["col_e"]
    ent_h = yc - (ped + colh)
    names = ["pav_L", "niche_L", "centre", "niche_R", "pav_R"]
    for i in range(5):
        a, b = el[i], el[i + 1]
        m.cls = "doc"
        L = face(a, b)
        kind = names[i]
        holes = []
        if kind == "centre":
            aw = V["arch_w"]
            s0 = L / 2 - aw / 2
            holes.append((s0, s0 + aw, 0.25, V["arch_spring"], V["arch_top"] - V["arch_spring"]))
        elif kind.startswith("niche"):
            nw = V["niche_w"]
            s0 = L / 2 - nw / 2
            holes.append((s0, s0 + nw, V["basin_y"] - 0.2, V["niche_top"] - nw / 2, nw / 2))
        P_.wall_holes(0.0, L, 0.25, ped + colh, holes, "brick")
        m.box(0.0, L, 0.0, ped, 0.0, 0.12, "marble", skip=("back",))  # the pedestal course
        if kind == "centre":
            aw = V["arch_w"]
            s0 = L / 2 - aw / 2
            sp = V["arch_spring"]
            arch_open(s0, s0 + aw, sp, V["arch_top"] - sp)
            # the iron gate, two leaves of scrolled bars (plate 7)
            for x in [s0 + aw * k / 12 for k in range(1, 12)]:
                top = sp + (V["arch_top"] - sp) * math.sqrt(max(0.0, 1 - ((x - L / 2) / (aw / 2)) ** 2)) - 0.05
                m.box(x - 0.018, x + 0.018, 0.27, top, -0.32, -0.28, "iron")
            for y in (0.9, 1.6, 2.3, sp - 0.1):
                m.box(s0, s0 + aw, y - 0.025, y + 0.025, -0.32, -0.28, "iron")
            for sgn in (-1, 1):  # the piers either side, with capitals
                x = L / 2 + sgn * (V["centre_bay"] / 2 - 0.31)
                P_.pilaster(x, ped, ped + colh, w=0.62, out=0.2, flutes=False)
                m.box(x - 0.45, x + 0.45, ped + colh - 0.45, ped + colh, 0.15, 0.4, "sculpt")  # the scrolled capital (P0192)
            # the scrolled cartouche over the arch reaching into the balustrade, lattice panels either side (plate 7, P0192)
            km = L / 2
            m.box(km - 0.55, km + 0.55, V["arch_top"] + 0.15, yc + 0.6, 0.0, 0.32, "sculpt", skip=("back",))
            for sgn in (-1, 1):
                pts = [(km + sgn * 0.5, V["arch_top"] + 0.4), (km + sgn * 1.45, V["arch_top"] + 0.8), (km + sgn * 1.55, V["arch_top"] + 1.15), (km + sgn * 1.2, V["arch_top"] + 1.2), (km + sgn * 0.5, V["arch_top"] + 0.95)]
                m.poly([(x, y, 0.26) for x, y in pts], "sculpt")
                lx = km + sgn * 1.15
                m.box(lx - 0.38, lx + 0.38, V["arch_top"] - 0.25, V["arch_top"] + 0.3, 0.0, 0.05, "panel", skip=("back",))
                for j in range(-3, 4):  # the diamond lattice (plate 7, P0192)
                    m.poly([(lx + j * 0.11 - 0.012, V["arch_top"] - 0.25, 0.07), (lx + j * 0.11 + 0.012, V["arch_top"] - 0.25, 0.07), (lx + j * 0.11 + 0.012 + 0.2, V["arch_top"] + 0.3, 0.07), (lx + j * 0.11 - 0.012 + 0.2, V["arch_top"] + 0.3, 0.07)], "marble")
            S.kp("e_arch_head", _w((s0 + aw / 2, V["arch_top"], 0.0)))
            S.kp("e_arch_foot_L", _w((s0, 0.25, 0.0)), anchor=True)
            S.kp("e_arch_foot_R", _w((s0 + aw, 0.25, 0.0)), anchor=True)
            S.kp("e_impost_L", _w((s0, sp, 0.0)))
            S.kp("e_impost_R", _w((s0 + aw, sp, 0.0)))
            S.kp("e_pier_C_L_cap", _w((L / 2 - V["centre_bay"] / 2 + 0.31, ped + colh, 0.2)))
            S.kp("e_pier_C_R_cap", _w((L / 2 + V["centre_bay"] / 2 - 0.31, ped + colh, 0.2)))
        elif kind.startswith("niche"):
            nw = V["niche_w"]
            s0 = L / 2 - nw / 2
            niche(s0, s0 + nw, V["niche_top"])
            lr = "L" if kind.endswith("L") else "R"
            S.kp(f"e_niche_{lr}_head", _w((L / 2, V["niche_top"], -0.1)))
            S.kp(f"e_niche_{lr}_basin", _w((L / 2, V["basin_y"], 0.6)))
            m.box(L / 2 - 0.5, L / 2 + 0.5, V["niche_top"] + 0.45, V["niche_top"] + 1.15, 0.0, 0.12, "sculpt", skip=("back",))  # the carved head over the niche
        else:
            # the end pavilion: from its outer corner, a round column, a round column, a pier next to the niche bay (plate 7)
            lr = "L" if kind.endswith("L") else "R"
            outer_first = kind == "pav_L"
            pos = [0.4, 1.2, 1.95] if outer_first else [L - 0.4, L - 1.2, L - 1.95]
            for k, s in enumerate(pos):
                if k < 2:
                    m.box(s - 0.42, s + 0.42, 0.0, ped, 0.0, 0.62, "marble", skip=("back",))
                    m.lathe([(0.32, ped), (0.32, ped + 0.25), (0.27, ped + 0.35), (0.25, ped + colh - 0.55), (0.34, ped + colh - 0.3), (0.42, ped + colh)], 10, "marble", cx=s, cz=0.3)
                    for yy in (ped + colh - 0.5, ped + colh - 0.2):  # the capital's volutes as blocks (composite capitals with masks, plate 7)
                        m.box(s - 0.45, s + 0.45, yy, yy + 0.18, 0.15, 0.55, "sculpt")
                else:
                    P_.pilaster(s, ped, ped + colh, w=0.6, out=0.25, flutes=False)
            so = pos[0]
            S.kp(f"e_col_{lr}_out_foot", _w((so, ped, 0.62)))
            S.kp(f"e_col_{lr}_out_cap", _w((so, ped + colh, 0.62)))
            corner = 0.0 if outer_first else L
            S.kp(f"e_foot_{lr}_out", _w((corner, S.gy(*_w((corner, 0.0, 0.3))[::2]) - 0.0, 0.3)))
            S.kp(f"e_cornice_{lr}_end", _w((corner, yc, 0.75)))
            S.kp(f"e_rail_{lr}_end", _w((corner + (0.3 if outer_first else -0.3), yr, 0.5)))
        P_.entablature(0.0, L, yc, h=ent_h, out=0.45 if kind != "centre" else 0.4)
        m.pop()
    # the balustrade along the top, following the concave plan; pedestals with finials over the columns and piers (plate 7)
    m.cls = "doc"
    yb = yc
    offs = 0.3
    rail_pts = []
    for p in el:
        rail_pts.append((p[0], p[1] - offs))
    P_.rail(rail_pts, yb, h=yr - yb, posts=99.0, spacing=0.34, ends=False)
    fin = []
    for i, kind in enumerate(names):
        a, b = el[i], el[i + 1]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        ux, uz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        if kind.startswith("pav"):
            outer_first = kind == "pav_L"
            for s in ([0.4, 1.2, 1.95] if outer_first else [L - 0.4, L - 1.2, L - 1.95]):
                fin.append((a[0] + ux * s, a[1] + uz * s - offs, kind, s))
    for i, (x, z, kind, s) in enumerate(fin):
        m.box(x - 0.3, x + 0.3, yb, yr + 0.05, z - 0.3, z + 0.3, "marble")
        finial(x, z, yr + 0.05)
    # the finials over the centre's piers
    a, b = el[2], el[3]
    for sgn in (-1, 1):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        sm = L / 2 + sgn * (V["centre_bay"] / 2 - 0.31)
        x = a[0] + (b[0] - a[0]) * sm / L
        z = a[1] - offs
        m.box(x - 0.3, x + 0.3, yb, yr + 0.05, z - 0.3, z + 0.3, "marble")
        finial(x, z, yr + 0.05)
        S.kp(f"e_finial_{'L' if x > 0 else 'R'}_in", (x, yr + 0.05 + V["finial_e"], z))
    out_L = max(fin, key=lambda f: f[0])
    out_R = min(fin, key=lambda f: f[0])
    S.kp("e_finial_L_out", (out_L[0], yr + 0.05 + V["finial_e"], out_L[1]))
    S.kp("e_finial_R_out", (out_R[0], yr + 0.05 + V["finial_e"], out_R[1]))
    # the crest over the centre: scrolls and a shell (plate 7, P0192)
    zc = V["range_e"] - offs
    yt = V["crest_e"]
    crest = [(-1.4, yr - 0.4), (-1.3, yr + 0.15), (-0.8, yr + 0.35), (-0.55, yt - 0.45), (-0.25, yt - 0.1), (0.0, yt), (0.25, yt - 0.1), (0.55, yt - 0.45), (0.8, yr + 0.35), (1.3, yr + 0.15), (1.4, yr - 0.4)]
    for dz in (-0.12, 0.12):
        m.poly([(x, y, zc + dz) for x, y in crest], "sculpt")
    for k in range(7):  # the shell's ribs
        t0, t1 = math.pi * k / 7, math.pi * (k + 1) / 7
        m.poly([(0.0, yr + 0.35, zc - 0.16), (0.55 * math.cos(t0), yr + 0.35 + 0.5 * math.sin(t0), zc - 0.16), (0.55 * math.cos(t1), yr + 0.35 + 0.5 * math.sin(t1), zc - 0.16)], "gilt")
    S.kp("e_crest_top", (0.0, yt, zc))
    # the low flanking walls beyond the ends (plate 7): panels between pilasters, a coping; set back from the end pavilions; their length assumed
    hw = V["w"] / 2
    zf = V["range_e"] + 0.8
    for sx in (-1, 1):
        a, b = (sx * hw, zf), (sx * (hw + 5.0), zf)
        if sx < 0:
            a, b = b, a
        L = face(b, a) if sx < 0 else face(a, b)
        m.pop()
        x0, x1 = sorted((sx * hw, sx * (hw + 5.0)))
        S.footing(rect(x0, x1, zf - 0.3, zf + 0.3), V["flank_h"] - 0.2, "wall", name=f"flank_{'S' if sx > 0 else 'N'}")
        m.box(x0 - 0.05, x1 + 0.05, V["flank_h"] - 0.2, V["flank_h"], zf - 0.38, zf + 0.38, "marble")
        for k in range(4):
            x = x0 + (x1 - x0) * (k + 0.5) / 4
            m.box(x - 0.45, x + 0.45, 0.8, V["flank_h"] - 0.6, zf - 0.36, zf - 0.3, "panel")
        for x in (x0, x1):
            m.box(x - 0.25, x + 0.25, 0.0, V["flank_h"] + 0.1, zf - 0.4, zf + 0.4, "marble")
    # the paved apron before the east front (plate 7), the steps to the arch
    g = max(S.gy(x, z) for x, z in rect(-4.0, 4.0, -V["d"] - 3.0, V["range_e"]))
    m.flat([(V["w"] / 2, -V["d"]), (V["w"] / 2, -V["d"] - 3.0), (-V["w"] / 2, -V["d"] - 3.0), (-V["w"] / 2, -V["d"])], g + 0.02, "pave")
    m.prism(rect(-1.6, 1.6, -V["d"] - 0.3, V["range_e"]), S.gy(0.0, V["range_e"]) - 0.15, 0.25, "step")
    S.entry("east_arch", 0.0, -V["d"] - 1.2)
    S.CLEAR.append(rect(-V["w"] / 2 - 0.5, V["w"] / 2 + 0.5, -V["d"] - 3.5, V["range_e"]))
    S.joint("east_steps", 0.0, -V["d"] - 0.2, "stair foot")


_FACE = []


def _w(p):
    """A point given in the current face frame, in the model frame."""
    q = m.world(p)
    return (float(q[0]), float(q[1]), float(q[2]))


def arch_open(a0, a1, spring, rise):
    pts = arc_pts(a0, a1, spring, rise, 10)
    for s in (a0, a1):
        m.poly([(s, 0.25, 0.0), (s, 0.25, -1.0), (s, spring, -1.0), (s, spring, 0.0)], "marble")
    for p0, p1 in zip(pts[:-1], pts[1:]):
        m.poly([(p0[0], p0[1], 0.0), (p0[0], p0[1], -1.0), (p1[0], p1[1], -1.0), (p1[0], p1[1], 0.0)], "marble")
    f = 0.32
    m.box(a0 - f, a0, 0.25, spring, 0.0, 0.12, "marble", skip=("back",))
    m.box(a1, a1 + f, 0.25, spring, 0.0, 0.12, "marble", skip=("back",))
    for s in (a0 - f - 0.05, a1 - 0.05):  # the impost blocks
        m.box(s, s + f + 0.1, spring - 0.2, spring, 0.0, 0.2, "marble", skip=("back",))
    outer = arc_pts(a0 - f, a1 + f, spring, rise + f, 10)
    for (p0, q0), (p1, q1) in zip(zip(pts[:-1], outer[:-1]), zip(pts[1:], outer[1:])):
        m.poly([(p0[0], p0[1], 0.12), (q0[0], q0[1], 0.12), (q1[0], q1[1], 0.12), (p1[0], p1[1], 0.12)], "marble")
    # the fluted band round the archivolt (P0192): ribs on a wider ring
    outer2 = arc_pts(a0 - f - 0.35, a1 + f + 0.35, spring, rise + f + 0.35, 14)
    for k, ((p0), (p1)) in enumerate(zip(outer2[:-1], outer2[1:])):
        if k % 2 == 0:
            q = arc_pts(a0 - f, a1 + f, spring, rise + f, 14)
            m.poly([(q[k][0], q[k][1], 0.16), (p0[0], p0[1], 0.16), (p1[0], p1[1], 0.16), (q[k + 1][0], q[k + 1][1], 0.16)], "sculpt")
    km = (a0 + a1) / 2
    m.box(km - 0.22, km + 0.22, spring + rise - 0.05, spring + rise + 0.6, 0.0, 0.3, "sculpt", skip=("back",))


def niche(a0, a1, top):
    """A round-headed niche with a shell head, a fountain vase in it over a shell basin (plate 7, P0192)."""
    r = (a1 - a0) / 2
    sp = top - r
    pts = arc_pts(a0, a1, sp, r, 10)
    y0 = V["basin_y"] - 0.2
    m.box(a0, a1, y0, sp, -0.42, -0.4, "panel")  # the niche's back
    m.box(a0, a1, y0 - 0.02, y0, -0.42, 0.0, "marble")  # its floor
    for s in (a0, a1):
        m.poly([(s, y0, 0.01), (s, y0, -0.42), (s, sp, -0.42), (s, sp, 0.01)], "marble")
    c = (a0 + a1) / 2
    for k in range(10):  # the shell head: ribs fanning from the springing's middle
        p0, p1 = pts[k], pts[k + 1]
        m.poly([(c, sp, -0.4), (p0[0], p0[1], 0.02), (p1[0], p1[1], 0.02)], "sculpt" if k % 2 == 0 else "marble")
    f = 0.16
    m.box(a0 - f, a0, y0, sp, 0.0, 0.1, "marble", skip=("back",))
    m.box(a1, a1 + f, y0, sp, 0.0, 0.1, "marble", skip=("back",))
    ring_ = arc_pts(a0 - f, a1 + f, sp, r + f, 10)
    for (p0, q0), (p1, q1) in zip(zip(pts[:-1], ring_[:-1]), zip(pts[1:], ring_[1:])):
        m.poly([(p0[0], p0[1], 0.1), (q0[0], q0[1], 0.1), (q1[0], q1[1], 0.1), (p1[0], p1[1], 0.1)], "marble")
    # the shell basin projecting at the foot, the vase stack in the niche, a small jet (S02 p.147: carved marble fountains either side of the door)
    yb = V["basin_y"]
    m.lathe([(0.12, 0.25), (0.22, yb * 0.45), (0.18, yb * 0.7), (0.6, yb - 0.08), (0.66, yb), (0.0, yb)], 10, "marble", cx=c, cz=0.25)
    m.flat([(c + 0.58 * math.cos(2 * math.pi * k / 10), 0.25 + 0.58 * math.sin(2 * math.pi * k / 10)) for k in range(10)], yb - 0.04, "water")
    yv = yb + (top - yb) * 0.62  # the tiered stem of vases and bowls standing in the niche (plate 7, P0192)
    m.lathe([(0.16, yb), (0.2, yb + 0.4), (0.34, yb + 0.7), (0.2, yb + 1.0), (0.12, yb + 1.2), (0.3, yb + 1.45), (0.22, yv - 0.2), (0.07, yv), (0.0, yv + 0.05)], 8, "sculpt", cx=c, cz=-0.15)
    P_.jet(c, -0.15, yv, 0.3, 0.05, n=5)


def finial(x, z, y):
    """The tall finials on the balustrade's pedestals: a lyre-like body and a flame (plate 7), as a turned shape."""
    h = V["finial_e"]
    m.lathe([(0.24, y), (0.18, y + 0.12), (0.26, y + 0.35), (0.12, y + 0.6), (0.2, y + 0.85), (0.08, y + 1.1), (0.12, y + 1.25), (0.0, y + h)], 8, "sculpt", cx=x, cz=z)


def build():
    global S, m, P_
    S = Site("XY05-M25")
    m = Mesh(COL)
    S.m = m
    P_ = Parts(m, rail_h=1.0, baluster_segs=6)
    m.cls = "doc"
    range_body()
    west_front()
    east_front()


def summary(tris, fill, size):
    rows = [
        ["West front", f"a Chinese gate of five roofs (S02 p.147, S310: B): the portico's two columns {V['col_c_h']:g} m under the highest roof (ridge {V['ridge_c']:g} m, finials {V['finial_c']:g} m), the arched door, the wings' columns and roofs (eave {V['eave_wing']:g} m), the lowest roofs at the ends; the cage walls as a net with a fan-headed window in each, two statues on lotus pedestals (plate 6, C)"],
        ["East front", f"a European front {V['w']:g} m wide, concave (the ends {abs(V['d'] + V['range_e']):.1f} m forward): end pavilions of two columns ({V['col_e']:g} m on {V['ped_e']:g} m pedestals) and a pier, shell niches with fountain vases, the arch {V['arch_w']:g} m wide to {V['arch_top']:g} m with its iron gate, the scrolled cartouche and lattice panels, the cornice at {V['cornice_e']:g} m, the balustrade to {V['rail_e']:g} m with finials, the crest at {V['crest_e']:g} m (plate 7; P0192, P0175, P0178, P0168: C)"],
        ["Plan", f"{V['w']:g} × {V['d']:g} m with the portico's projection (S01, b); a passage through the middle, the bird rooms either side (S310, B)"],
        ["Assumed", "the ends of the range, the roof terrace, the passage's inside, the walls beyond the gate and their lowest roofs, the low walls either side of the east front beyond what plate 7 shows, the statues' figures (C, the pale tint with conf=1)"],
    ]
    return {
        "id": "XY05", "aliases": [], "name": "养雀笼 Yangque Long", "glb": "model.glb", "position": S.pos, "rotationY": S.rot,
        "line": "Modelled from plates 6 and 7 of 1783-86 and the photographs of the east front from the 1870s to about 1922 (Child, Sirén); it was pulled down about 1924 and no plan survey is in hand, so every figure is a reading (C) on the plan's footprint.",
        "rows": rows,
        "caption": {"frontage_m": V["w"], "depth_m": V["d"], "eave_m": V["cornice_e"], "ridge_m": V["ridge_c"], "assumed": True, "confidence": "C"},
        "hides": ["GB36"],  # the walls layer's gate G36, 'passage through 养雀笼', left at the plan's place 13 m east of the gate's box (Round 6 moved the box onto the ruin): a phantom of this gate's own passage
        "tris": tris, "fill_tris": fill, "glb_bytes": size,
    }


def main():
    build()
    size = m.write_glb(HERE / "model.glb", "XY05 养雀笼 Yangque Long", extras={"id": "XY05"})
    tris = m.count()
    prims = {k: len(v["idx"]) // 3 for k, v in sorted(m.prims.items())}
    fill = sum(n for k, n in prims.items() if k.endswith("~fill"))
    S.write(HERE, "XY05", ["XY05"], P, "x south along the west front (to the right seen from the west), y up from the ground at the gate's box, z west (out of the west front); the origin at the west front's middle; metres", summary(tris, fill, size))
    print(f"model.glb {size / 1e6:.2f} MB, {tris} triangles ({fill} fill), {P_.balusters} balusters, {len(S.KP)} key points, {len(S.JOINTS)} joints, {len(S.ENTRIES)} entries; position {S.pos} rotY {S.rot}")


if __name__ == "__main__":
    main()
