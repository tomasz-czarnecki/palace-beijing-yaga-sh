#!/usr/bin/env python3
"""线法山门 Xianfa Shan Men (XY12-01), the west gate of the perspective hill 线法山, the seventeenth detailed model (Round 30): a triple gate of stone, the arch in the middle under
a raised attic with a broken pediment and a garland crest, a square-headed door either side under a shell, carved pilasters on pedestals, the entablature with its frieze panels,
crests of scrolls and garlands over the side bays, lyre finials over the pilasters and vases at the ends, scrolled buttresses at the foot of the ends, and the panelled walls that
run from the gate's ends towards the viewer with an urn on a pedestal by each (plate 17, 线法山门正面, P0057; S02 p.159: 'a triple gate like a triumphal arch').
Plain geometry, one GLB (scripts/model_mesh.py) with every figure in params.json; the method is the pilot's (models/XY01-xieqiqu/README.md).

  uv run python models/XY12-01-xianfa-shan-men/xianfashanmen.py

Writes, beside this file: model.glb, params.json, keypoints.json, joints.json, summary.json (models/README.md).
Frame (scripts/model_site.py): origin at the front middle of the gate's box XY12-M55, which faces west: x along the west front to the right as one faces it from the west
(south), y up from the box's ground, z west (out of the front). The east face lies at z = -d.
Grades: what plate 17 shows is `doc`; the east face, the ends, the passages' insides and the walls' backs are `fill` (assumed, C, carried round from the west front).
Environment, for a test only (never in a run of step 6): XY12_WALLS=splay draws the walls bending back east at 25 degrees, plate 17's copings' vote, 20-30 degrees (measure.py).
"""

import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from model_mesh import Mesh  # noqa: E402
from model_parts import Parts, arc_pts  # noqa: E402
from model_site import Site  # noqa: E402

# Plate 17 is drawn frontally on the gate's axis: its front is read at one scale, the plan's 13.6 m over the body's 787 px (x 807-1592 on the 2400 px copy), 57.7 px/m,
# the foot at y 998 (Round 30 readings, research/xiyanglou/plate_keypoints.csv).
P = {
    "w": (13.6, "S01;S71", "C", "the body's width: the gap in the hill's west wall on S01, 13.58 m (b); plate 17's body is the module (787 px)"),
    "d": (2.0, "S01", "C", "the depth: the box's guess (Round 6); plate 17 shows no side"),
    "pil_out": (5.96, "S71", "C", "the outer pilasters' middles from the axis: plate 17, x 852 and 1540 about the axis at x 1196 (Round 30 readings at 3x)"),
    "pil_out_w": (1.05, "S71", "C", "the outer pilasters' width: plate 17, about 60 px with their borders"),
    "pil_in": (2.32, "S71", "C", "the inner pilasters' middles either side of the arch: plate 17, x 1062 and 1330"),
    "pil_in_w": (1.04, "S71", "C", "the inner pilasters' width: plate 17, 60 px"),
    "ped_h": (0.55, "S71", "C", "the pilasters' pedestals: plate 17, their caps about 32 px over the foot (the trees cover the foot: weak)"),
    "shaft_top": (4.40, "S71", "C", "the pilasters' shafts to the capitals' necks: plate 17, y 745"),
    "cap_top": (4.85, "S71", "C", "the capitals' tops (with the dentils and the carved dosseret over them): plate 17, y 720"),
    "cornice": (6.03, "S71", "C", "the cornice's top: plate 17, y 650 over the foot at 998 (dossier 6.1 m)"),
    "frieze": (5.35, "S71", "C", "the frieze's long panels: plate 17, y 670-690 (5.35-5.70 m)"),
    "arch_w": (2.08, "S71", "C", "the arch's opening: plate 17, x 1140-1260 between the jambs' panels (dossier 2.3 m)"),
    "arch_top": (4.25, "S71", "C", "the arch's crown (the intrados): plate 17, y 753; a half circle, the springing at 3.2 m (the imposts at y 815: 3.17 m)"),
    "door_w": (1.30, "S71", "C", "the side doors' openings: plate 17, x 925-1000 inside the beaded frames (frames 1.9 m over all; dossier 1.6 m)"),
    "door_h": (2.65, "S71", "C", "the side doors' heads: plate 17, y 845; square-headed in a beaded frame"),
    "door_x": (4.04, "S71", "C", "the side doors' middles from the axis: plate 17, x 962 and 1430"),
    "door_crest": (4.56, "S71", "C", "the shell over each door's scrolled hood, its top: plate 17, y 735; the hood at y 795-805"),
    "attic_top": (7.04, "S71", "C", "the broken pediment over the centre, its top: plate 17, y 592, x 1118-1283 (2.9 m wide)"),
    "crest_top": (8.58, "S71", "C", "the garland crest over the centre with its ribbons, its top: plate 17, y 503 (dossier 8.7 m)"),
    "side_crest_top": (7.63, "S71", "C", "the crests of scrolls and garlands over the side bays: plate 17, y 558; 2.5 m wide"),
    "urn_top": (7.25, "S71", "C", "the lyre-and-garland finials over the four pilasters: plate 17, y 578-585"),
    "vase_top": (6.64, "S71", "C", "the vases at the ends of the cornice: plate 17, y 615"),
    "scroll_h": (2.4, "S71", "C", "the scrolled buttresses at the ends' feet: plate 17, from y 858 to the foot, about 1 m out from the body"),
    "wall_h": (2.7, "S71;S116", "C", "the walls either side: plate 17, 155 px at the gate's end (2.7 m at the gate's scale); the garden walls of 2.8 m (S116, S117) agree"),
    "wall_end": (30.0, "S01", "C", "the walls' run from the gate to the strip's long walls: S01 draws the hill's west wall north and south of the gap, about 145 px (30 m) each (b)"),
    "wall_splay": (0.0, "S01;S71", "C", "the walls' angle off the gate's line: S01 draws them straight north-south (0). Plate 17's copings read as lines (measure.py) vote for walls bending back east at 20-30 degrees, 2.4 m high (4.9-6.5 px rms against 17.4-17.8 px for the straight line), but its panels grow towards the sheet's edges as if the walls came forward: the plate's perspective is constructed, the plan wins (Q312)"),
    "wall_pil": (2.6, "S71", "C", "the walls' pilasters with sunk panels between: plate 17, eight a side between the gate and the sheet's edge"),
    "wall_urn": (1.4, "S71", "C", "two urns on pedestals a side before the walls next to the gate, 1.4 and 2.55 m along the wall from its start at the gate: plate 17, x 688, 620 and 1715, 1787 (68-72 px apart, 1.1-1.2 m at the fitted camera)"),
}
V = {k: v[0] for k, v in P.items()}
WALLS = os.environ.get("XY12_WALLS", "straight")  # Round 30: XY12_WALLS=splay draws them at wall_splay_test for a test only

COL = {
    "marble": "#ebe6da", "wall": "#d9d2c3", "panel": "#c2bbab", "sculpt": "#ddd6c6", "glaze": "#3f8a86", "joint": "#a39a8a", "rustic": "#d5cdbd",
    "glass_win": "#2e4a4f", "door": "#4a3b2c", "roof": "#46705c", "roofedge": "#3a5e4d", "ridge": "#c9a245", "gilt": "#b59a52", "pave": "#c9c2b2", "step": "#d2ccbe",
    "brick": "#9c8f80", "coping": "#b9b2a4", "jet": "#d8ecf2",
}

S = None
m = None
P_ = None


def rect(x0, x1, z0, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def face(a, b):
    """A face frame from a to b (plan x z): s along, y up, d out of the face (to the left of a->b seen from above)."""
    dx, dz = b[0] - a[0], b[1] - a[1]
    m.push(a[0], 0.0, a[1], math.atan2(-dz, dx))
    return math.hypot(dx, dz)


def _w(p):
    q = m.world(p)
    return (float(q[0]), float(q[1]), float(q[2]))


# ------------------------------------------------------------------ one face of the gate (the west front as plate 17 draws it; the east face carried round)
def front(doc=True):
    """Drawn in a face frame whose s runs from the face's left end (seen from outside) and d out of the face; s = 0 at the left end, the axis at w/2."""
    w = V["w"]
    c = w / 2
    m.cls = "doc" if doc else "fill"
    ped, sh, cap, yc = V["ped_h"], V["shaft_top"], V["cap_top"], V["cornice"]
    aw, at = V["arch_w"], V["arch_top"]
    sp = at - aw / 2
    dw, dh, dx = V["door_w"], V["door_h"], V["door_x"]
    holes = [(c - aw / 2, c + aw / 2, 0.0, sp, aw / 2)] + [(c + sx * dx - dw / 2, c + sx * dx + dw / 2, 0.0, dh, 0.0) for sx in (-1, 1)]
    P_.wall_holes(0.0, w, 0.0, yc - 1.1, holes, "wall")
    # the arch: its ring, the small jamb pilasters with their carved panels, the keystone shell (plate 17)
    a0, a1 = c - aw / 2, c + aw / 2
    pts = arc_pts(a0, a1, sp, aw / 2, 12)
    ring = arc_pts(a0 - 0.28, a1 + 0.28, sp, aw / 2 + 0.28, 12)
    for (p0, q0), (p1, q1) in zip(zip(pts[:-1], ring[:-1]), zip(pts[1:], ring[1:])):
        m.poly([(p0[0], p0[1], 0.12), (q0[0], q0[1], 0.12), (q1[0], q1[1], 0.12), (p1[0], p1[1], 0.12)], "marble")
    for s in (a0 - 0.42, a1):
        m.box(s, s + 0.42, 0.0, sp, 0.0, 0.14, "marble", skip=("back",))
        m.box(s + 0.12, s + 0.3, 0.6, sp - 0.35, 0.14, 0.19, "sculpt", skip=("back",))
        m.box(s - 0.04, s + 0.46, sp - 0.18, sp, 0.0, 0.22, "marble", skip=("back",))  # the impost
    P_.shell(c, at + 0.18, 0.5, d=0.1)
    m.box(c - 0.2, c + 0.2, at - 0.05, at + 0.3, 0.0, 0.26, "sculpt", skip=("back",))
    # the side doors: beaded frames, a scrolled hood with a shell (plate 17)
    for sx in (-1, 1):
        s = c + sx * dx
        P_.opening(s - dw / 2, s + dw / 2, 0.0, dh, 0.0, depth=0.35, kind="door", frame=0.26)
        m.box(s - dw / 2 - 0.36, s + dw / 2 + 0.36, dh + 0.26, dh + 0.42, 0.0, 0.3, "marble", skip=("back",))
        for sg in (-1, 1):  # the hood's scrolls
            P_.scroll(s + sg * (dw / 2 + 0.2), dh + 0.42, 0.55, 0.45, sx=sg, d=0.2, t=0.14)
        P_.shell(s, dh + 0.62, (V["door_crest"] - dh - 0.62) / 1.05, d=0.12)
    # the pilasters: pedestal, a shaft carved with a running chain of ornament, capital with dentils, the dosseret in the frieze (plate 17)
    for sx in (-1, 1):
        for xs, ww in ((V["pil_out"], V["pil_out_w"]), (V["pil_in"], V["pil_in_w"])):
            s = c + sx * xs
            m.box(s - ww / 2 - 0.08, s + ww / 2 + 0.08, 0.0, ped, 0.0, 0.36, "marble", skip=("back",))
            m.box(s - ww / 2 - 0.12, s + ww / 2 + 0.12, ped - 0.1, ped, 0.0, 0.42, "marble", skip=("back",))
            m.box(s - ww / 2, s + ww / 2, ped, sh, 0.0, 0.26, "marble", skip=("back",))
            m.box(s - ww * 0.22, s + ww * 0.22, ped + 0.35, sh - 0.3, 0.26, 0.31, "sculpt", skip=("back",))
            for k in range(int((sh - ped - 0.8) / 0.55)):
                y = ped + 0.55 + k * 0.55
                m.box(s - ww * 0.15, s + ww * 0.15, y, y + 0.26, 0.31, 0.36, "marble", skip=("back",))
            m.box(s - ww / 2 - 0.1, s + ww / 2 + 0.1, sh, cap, 0.0, 0.38, "sculpt", skip=("back",))
            for k in range(5):  # the dentils
                x = s - ww / 2 + (k + 0.5) * ww / 5
                m.box(x - 0.05, x + 0.05, sh - 0.12, sh, 0.26, 0.34, "marble", skip=("back",))
            m.box(s - ww * 0.3, s + ww * 0.3, cap, yc - 0.35, 0.0, 0.32, "marble", skip=("back",))
            P_.shell(s, cap + 0.12, 0.2, d=0.32, ribs=5, depth=0.06)
    # the entablature over the whole front, the frieze's long panels between the dossets (plate 17)
    P_.entablature(0.0, w, yc, h=yc - cap + 0.1, out=0.28)  # plate 17: the cornice ends 14 px (0.24 m) beyond the body
    for s0, s1 in ((c - V["pil_out"] + V["pil_out_w"] / 2 + 0.3, c - V["pil_in"] - V["pil_in_w"] / 2 - 0.3), (c - V["pil_in"] + V["pil_in_w"] / 2 + 0.3, c + V["pil_in"] - V["pil_in_w"] / 2 - 0.3),
                   (c + V["pil_in"] + V["pil_in_w"] / 2 + 0.3, c + V["pil_out"] - V["pil_out_w"] / 2 - 0.3)):
        m.box(s0, s1, V["frieze"], V["frieze"] + 0.3, 0.16, 0.22, "panel", skip=("back",))
        m.box(s0 + 0.2, s1 - 0.2, V["frieze"] + 0.12, V["frieze"] + 0.18, 0.22, 0.25, "sculpt", skip=("back",))


def crests():
    """The crowning ornament, standing in the gate's middle plane (two-sided): the attic with its broken pediment and the garland crest over the centre, the side crests
    of scrolls and garlands, the lyre finials over the pilasters, the vases at the ends (plate 17)."""
    w, d = V["w"], V["d"]
    zc = -d / 2
    yc = V["cornice"]
    m.cls = "doc"
    m.push(-w / 2, 0.0, zc, 0.0)
    c = w / 2
    # the attic: a block over the centre with a broken segmental pediment
    m.box(c - 1.5, c + 1.5, yc, V["attic_top"] - 0.45, -0.45, 0.45, "marble")
    for sx in (-1, 1):
        P_.slab([(c + sx * 1.6, V["attic_top"] - 0.45), (c + sx * 0.45, V["attic_top"] - 0.45), (c + sx * 0.45, V["attic_top"]), (c + sx * 1.1, V["attic_top"] - 0.2)][:: sx], -0.4, 0.4, "marble")
    P_.cartouche(c, V["attic_top"] - 0.3, 0.6, 0.5)
    S.kp("attic_top", _w((c, V["attic_top"], 0.0)))
    # the garland crest: a wreath on the pediment with crossed ribbons over it and a shell at its foot
    r = (V["crest_top"] - V["attic_top"] - 0.45) / 2
    yw = V["attic_top"] + 0.15 + r
    P_.wreath(c, yw, r, d=0.0, tube=0.13, width_y=1.0)
    for sx in (-1, 1):
        P_.slab([(c, yw + r - 0.1), (c + sx * 0.55, yw + r + 0.3), (c + sx * 0.45, yw + r + 0.45), (c, yw + r + 0.12)][:: sx], -0.06, 0.06, "sculpt")
    P_.shell(c, V["attic_top"] - 0.05, 0.42, d=0.2)
    S.kp("crest_top", _w((c, V["crest_top"], 0.0)))
    for sx, lr in ((-1, "L"), (1, "R")):
        # the side crest over each side bay: two scrolls back to back and a garland ring between them
        s = c + sx * (V["door_x"] + 0.12)  # plate 17: the side crests stand 7 px outside the doors' middles
        top = V["side_crest_top"]
        for sg in (-1, 1):
            P_.slab([(s + sg * 1.25, yc), (s + sg * 0.25, yc), (s + sg * 0.25, yc + 0.75), (s + sg * 0.75, yc + 0.6), (s + sg * 1.25, yc + 0.2)][:: sg], -0.25, 0.25, "sculpt")
            P_.scroll(s + sg * 0.3, yc + 0.55, 0.6, 0.5, sx=sg, d=0.0, t=0.18)
        rr = (top - yc - 0.75) / 2
        P_.wreath(s, yc + 0.75 + rr, rr, tube=0.11)
        S.kp(f"side_crest_{lr}_top", _w((s, top, 0.0)))
        # the lyre finials over the pilasters: a block, a lyre of two scrolls, a garland knot
        for nm, xs in (("out", V["pil_out"]), ("in", V["pil_in"])):
            s = c + sx * xs
            m.box(s - 0.32, s + 0.32, yc, yc + 0.35, -0.32, 0.32, "marble")
            h = V["urn_top"] - yc - 0.35
            for sg in (-1, 1):
                P_.slab([(s, yc + 0.35), (s + sg * 0.3, yc + 0.35 + h * 0.15), (s + sg * 0.34, yc + 0.35 + h * 0.6), (s + sg * 0.12, yc + 0.35 + h * 0.85), (s, yc + 0.35 + h * 0.7)][:: sg], -0.1, 0.1, "sculpt")
            P_.wreath(s, V["urn_top"] - 0.2, 0.18, tube=0.06, n=10)
            S.kp(f"urn_{nm}_{lr}_top", _w((s, V["urn_top"], 0.0)))
        # the vases at the cornice's ends
        s = c + sx * (w / 2 - 0.05)
        m.lathe([(0.18, yc), (0.24, yc + 0.12), (0.16, yc + 0.2), (0.28, yc + 0.42), (0.2, V["vase_top"] - 0.15), (0.06, V["vase_top"] - 0.05), (0.0, V["vase_top"])], 8, "sculpt", cx=s, cz=0.0)
        S.kp(f"vase_{lr}_top", _w((s, V["vase_top"], 0.0)))
    m.pop()


def body():
    w, d = V["w"], V["d"]
    hw = w / 2
    # the footing under the whole gate (follows the ground: the hill's foot falls about 1 m in 10 m to the west)
    S.footing(rect(-hw - 0.15, hw + 0.15, -d - 0.15, 0.15), 0.0, "marble", name="gate_foot", lid=False)
    m.cls = "doc"
    face((-hw, 0.0), (hw, 0.0))
    front(doc=True)
    m.pop()
    face((hw, -d), (-hw, -d))
    front(doc=False)
    m.pop()
    # the ends (north and south): plain with a pilaster at each corner and a sunk panel (fill)
    m.cls = "fill"
    for a, b in (((hw, 0.0), (hw, -d)), ((-hw, -d), (-hw, 0.0))):
        L = face(a, b)
        P_.wall_holes(0.0, L, 0.0, V["cornice"] - 1.1, [], "wall")
        m.box(0.35, L - 0.35, 1.0, V["shaft_top"] - 0.4, 0.0, 0.05, "panel", skip=("back",))
        P_.entablature(0.0, L, V["cornice"], h=V["cornice"] - V["cap_top"] + 0.1, out=0.45, ends=False)
        m.pop()
    # the passages: the arch's barrel and the doors' reveals through the depth, the roof's top as a lead flat (fill)
    aw, at = V["arch_w"], V["arch_top"]
    sp = at - aw / 2
    pts = arc_pts(-aw / 2, aw / 2, sp, aw / 2, 12)
    for p0, p1 in zip(pts[:-1], pts[1:]):
        m.poly([(p0[0], p0[1], 0.0), (p1[0], p1[1], 0.0), (p1[0], p1[1], -d), (p0[0], p0[1], -d)], "wall")
    for s in (-aw / 2, aw / 2):
        m.poly([(s, 0.0, 0.0), (s, sp, 0.0), (s, sp, -d), (s, 0.0, -d)], "wall")
    for sx in (-1, 1):
        s = sx * V["door_x"]
        for e in (s - V["door_w"] / 2, s + V["door_w"] / 2):
            m.poly([(e, 0.0, 0.0), (e, V["door_h"], 0.0), (e, V["door_h"], -d), (e, 0.0, -d)], "wall")
        m.box(s - V["door_w"] / 2, s + V["door_w"] / 2, V["door_h"], V["door_h"] + 0.02, -d, 0.0, "wall")
    m.flat(rect(-hw - 0.4, hw + 0.4, -d - 0.4, 0.4), V["cornice"], "coping")
    m.cls = "doc"
    # the threshold through the arch and the doors
    y = max(S.gy(x, z) for x, z in rect(-aw / 2, aw / 2, -d, 0.0)) + 0.02
    m.flat(rect(-aw / 2, aw / 2, -d - 0.2, 0.2), y, "pave")
    for sx in (-1, 1):
        s = sx * V["door_x"]
        m.flat(rect(s - V["door_w"] / 2, s + V["door_w"] / 2, -d - 0.2, 0.2), max(S.gy(x, z) for x, z in rect(s - 0.7, s + 0.7, -d, 0.0)) + 0.02, "pave")
    # the scrolled buttresses at the ends' feet (plate 17)
    for sx, lr in ((-1, "L"), (1, "R")):
        x = sx * hw
        m.push(x, 0.0, -0.3, 0.0)
        P_.scroll(sx * 0.15, 0.0, V["scroll_h"], 0.9, sx=sx, d=0.0, t=0.5, mat="marble")
        m.pop()
        S.kp(f"scroll_{lr}_top", (x + sx * 0.15, V["scroll_h"], -0.05))
        S.JOINTS.append([f"scroll_{lr}", sx * (hw + 1.0), S.gy(sx * (hw + 1.0), -0.3) - 0.1, -0.3, "wall foot"])
    # the key points of the west front (plate 17)
    c0 = 0.0
    for sx, lr in ((-1, "L"), (1, "R")):
        S.kp(f"foot_{lr}", (sx * hw, 0.0, 0.0), anchor=True)
        S.kp(f"cornice_{lr}", (sx * (hw + 0.28), V["cornice"], 0.28))
        for nm, xs in (("out", V["pil_out"]), ("in", V["pil_in"])):
            S.kp(f"pil_{nm}_{lr}_cap", (sx * xs, V["cap_top"], 0.38))
            S.kp(f"pil_{nm}_{lr}_foot", (sx * xs, 0.0, 0.36), anchor=True)
        S.kp(f"door_{lr}_head", (sx * V["door_x"], V["door_h"], 0.0))
        S.kp(f"door_{lr}_crest", (sx * V["door_x"], V["door_crest"], 0.15))
        S.kp(f"arch_foot_{lr}", (sx * aw / 2, 0.0, 0.0), anchor=True)
    S.kp("arch_crown", (c0, at, 0.0))
    S.FOOTPRINTS.append(rect(-hw - 0.2, -V["door_x"] - 0.75, -d - 0.2, 0.45))
    S.FOOTPRINTS.append(rect(V["door_x"] + 0.75, hw + 0.2, -d - 0.2, 0.45))
    S.entry("west_arch", 0.0, 0.8)
    S.entry("east_arch", 0.0, -d - 0.8)
    S.CLEAR.append(rect(-hw - 1.0, hw + 1.0, -d - 1.5, 2.0))
    # plate 17 draws the forecourt level, planted with rows of clipped trees: no generated hill of Round 10 there (a 4.3 m hill of free land stood north-west of the gate)
    S.LEVEL.append(rect(-hw - 31.0, hw + 31.0, -2.5, 30.0))


def walls():
    """The panelled walls from the gate's ends (plate 17): a wall with pilasters and sunk panels between them, a coping; an urn on a pedestal at its foot by the gate.
    On S01's straight north-south line (`wall_splay` 0); XY12_WALLS=splay for the test of plate 17's vote."""
    hw = V["w"] / 2
    ang = math.radians(V["wall_splay"]) if WALLS == "straight" else math.radians(-25.0)  # -25: plate 17's copings' vote, 20-30 degrees (measure.py)
    t = 0.7
    L = V["wall_end"]
    pil = V["wall_pil"]
    for sx, lr in ((-1, "L"), (1, "R")):
        a = (sx * (hw + 0.55), -0.9)
        u = (sx * math.cos(ang), math.sin(ang))
        b = (a[0] + u[0] * L, a[1] + u[1] * L)
        n_in = (u[1], -u[0]) if sx < 0 else (-u[1], u[0])  # towards the forecourt
        off = lambda p, k: (p[0] + n_in[0] * k, p[1] + n_in[1] * k)
        poly = [off(a, t / 2), off(b, t / 2), off(b, -t / 2), off(a, -t / 2)]
        m.cls = "doc"
        S.footing(poly, V["wall_h"] - 0.25, "wall", name=f"wall_{lr}", lid=False)
        cp = [off(a, t * 0.65), off(b, t * 0.65), off(b, -t * 0.65), off(a, -t * 0.65)]
        m.prism(cp, V["wall_h"] - 0.25, V["wall_h"], "coping")
        n = int(L / pil)
        for side, cls in ((1, "doc"), (-1, "fill")):
            m.cls = cls
            pa, pb = off(a, side * t / 2), off(b, side * t / 2)
            # face(): d = (-uz, ux) of the walk; the forecourt face needs d = n_in
            inward_first = (sx > 0) == (side > 0)
            Lf = face(pa, pb) if inward_first else face(pb, pa)
            sgate = (lambda s: s) if inward_first else (lambda s: Lf - s)
            for k in range(n + 1):
                s = min(max(sgate(k * pil), 0.25), Lf - 0.25)
                m.box(s - 0.22, s + 0.22, -0.1, V["wall_h"] - 0.3, 0.0, 0.12, "marble", skip=("back",))
            for k in range(n):
                s0, s1 = sorted((sgate(k * pil + 0.55), sgate((k + 1) * pil - 0.55)))
                m.box(s0, s1, 0.55, V["wall_h"] - 0.75, 0.0, 0.04, "panel", skip=("back",))
                m.box(s0 - 0.06, s1 + 0.06, 0.49, 0.55, 0.0, 0.08, "marble", skip=("back",))
                m.box(s0 - 0.06, s1 + 0.06, V["wall_h"] - 0.75, V["wall_h"] - 0.69, 0.0, 0.08, "marble", skip=("back",))
            m.pop()
        m.cls = "doc"
        # key points on the forecourt face's top and foot at each pilaster, counted from the gate
        for k in range(1, n + 1):
            p = off((a[0] + u[0] * k * pil, a[1] + u[1] * k * pil), t / 2 + 0.12)
            S.kp(f"wall_{lr}_pil{k}_top", (p[0], V["wall_h"], p[1]))
            S.kp(f"wall_{lr}_pil{k}_foot", (p[0], S.gy(*p), p[1]))
        g = off(a, t / 2)
        S.kp(f"wall_{lr}_gate_top", (g[0], V["wall_h"], g[1]))
        S.JOINTS.append([f"wall_{lr}_end", b[0], S.gy(*b) - 0.15, b[1], "wall foot"])
        # the urn on its pedestal by the gate, before the wall (plate 17)
        for j, along in enumerate((V["wall_urn"], V["wall_urn"] + 1.15)):  # plate 17: two urns on pedestals a side, before the wall next to the gate
            px, pz = off((a[0] + u[0] * along, a[1] + u[1] * along), t / 2 + 0.9)
            g = S.gy(px, pz)
            S.footing(rect(px - 0.4, px + 0.4, pz - 0.4, pz + 0.4), g + 1.3, "marble", name=f"urn_ped_{lr}{j}")
            m.box(px - 0.48, px + 0.48, g + 1.3, g + 1.42, pz - 0.48, pz + 0.48, "marble")
            m.lathe([(0.22, g + 1.42), (0.3, g + 1.55), (0.2, g + 1.65), (0.42, g + 1.95), (0.36, g + 2.25), (0.16, g + 2.4), (0.22, g + 2.5), (0.0, g + 2.75)], 10, "sculpt", cx=px, cz=pz)
            S.kp(f"wall_urn_{lr}{j}_top", (px, g + 2.75, pz))
        S.FOOTPRINTS.append(poly)


def build():
    global S, m, P_
    S = Site("XY12-M55")
    m = Mesh(COL)
    S.m = m
    P_ = Parts(m, rail_h=1.0, baluster_segs=6)
    m.cls = "doc"
    body()
    crests()
    walls()


def summary(tris, fill, size):
    rows = [
        ["West front", f"a triple gate {V['w']:g} m wide (S01's gap, b): the arch {V['arch_w']:g} m wide to {V['arch_top']:g} m, a square-headed door {V['door_w']:g} × {V['door_h']:g} m either side under a shell, four carved pilasters on pedestals with capitals at {V['cap_top']:g} m, the entablature with its frieze panels to {V['cornice']:g} m (plate 17, C)"],
        ["Crests", f"the attic with its broken pediment ({V['attic_top']:g} m) and the garland crest over the centre ({V['crest_top']:g} m), crests of scrolls and garlands over the side bays ({V['side_crest_top']:g} m), lyre finials over the pilasters ({V['urn_top']:g} m) and vases at the ends (plate 17, C)"],
        ["Walls", f"panelled walls {V['wall_h']:g} m high with pilasters, sunk panels and a coping, from the gate's ends north and south {V['wall_end']:g} m on S01's straight line (plate 17's copings lean back east: Q312), an urn on a pedestal by the gate on each side (plate 17, C)"],
        ["Assumed", f"the depth ({V['d']:g} m), the east face, the ends and the passages, carried round from the west front; the walls' backs and their ends (C, the pale tint with conf=1)"],
    ]
    return {
        "id": "XY12-01", "aliases": [], "name": "线法山门 Xianfa Shan Men", "glb": "model.glb", "position": S.pos, "rotationY": S.rot,
        "line": "Modelled from plate 17 of 1783-86, drawn frontally and read at the plan's width; no photograph of the gate standing or of its ruin is known, so every figure is a reading (C).",
        "rows": rows,
        "caption": {"frontage_m": V["w"], "depth_m": V["d"], "eave_m": V["cornice"], "ridge_m": V["crest_top"], "assumed": True, "confidence": "C"},
        "hides": [],
        "tris": tris, "fill_tris": fill, "glb_bytes": size,
    }


def main():
    build()
    size = m.write_glb(HERE / "model.glb", "XY12-01 线法山门 Xianfa Shan Men", extras={"id": "XY12-01"})
    tris = m.count()
    prims = {k: len(v["idx"]) // 3 for k, v in sorted(m.prims.items())}
    fill = sum(n for k, n in prims.items() if k.endswith("~fill"))
    S.write(HERE, "XY12-01", ["XY12-01"], P, "x south along the west front (to the right seen from the west), y up from the ground at the gate's box, z west (out of the front); the origin at the west front's middle; metres", summary(tris, fill, size))
    print(f"model.glb {size / 1e6:.2f} MB, {tris} triangles ({fill} fill), {len(S.KP)} key points, {len(S.JOINTS)} joints, {len(S.ENTRIES)} entries; position {S.pos} rotY {S.rot}; walls {WALLS}")


if __name__ == "__main__":
    main()
