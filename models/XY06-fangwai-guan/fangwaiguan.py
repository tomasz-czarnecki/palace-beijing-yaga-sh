#!/usr/bin/env python3
"""方外观 Fangwaiguan (XY06), the small two-storey pavilion of the Xiyang Lou, the sixth detailed model (Round 16): the rusticated podium (the 'low room under the terrace',
S258) with its porch, door and two oval windows, the walk on its top with a balustrade and the balcony over the porch; the upper storey of three tall windows with scrolled
pediments, carved corner strips and a frieze of rosettes; the double-eaved Chinese roof with its ridge crest; and the two curved stairs that sweep from the front out and
back up to landings at the ends (plate 8; Ohlmer's photograph of 1873, P0773).
Plain geometry, one GLB (scripts/model_mesh.py) with every figure in params.json; the method is the pilot's (models/XY01-xieqiqu/README.md).

  uv run python models/XY06-fangwai-guan/fangwaiguan.py

Writes, beside this file: model.glb, params.json, keypoints.json, joints.json, summary.json (models/README.md).
Frame (scripts/model_site.py): origin at the front middle of the hall's box XY06-M27 (the podium's front face), at that box's ground; x east along the front, y up, z south.
Grades: what plate 8, P0773 or the photographs since 1914 show is `doc`; the back, the east end above the stair and the stairs' inner faces are `fill` (assumed, C).
Every figure is C unless params.json says otherwise.
"""

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from model_mesh import Mesh  # noqa: E402
from model_parts import Parts, arc_pts  # noqa: E402
from model_site import Site, lobed  # noqa: E402

P = {
    "w": (14.0, "S603;S01", "B", "the podium's front: Durand's survey 'L. 14 m l. 7 m H. 13 m' without the stairs (S603 p.129); the plan 13.85 m (b)"),
    "d": (7.0, "S603", "B", "the block's depth without the stairs (S603 p.129); his restitution plan draws returns, so 7 m may be the core (dossier)"),
    "pod_h": (3.8, "S71;S70", "C", "the podium's top (the upper floor) above the ground: plate 8 at 47.6 px/m (the 14 m on 666 px), 3.8 m; P0355's porch piers about 4.4 m (the reader), Round 6 3.7-3.9 m"),
    "end_panel": (2.7, "S71", "C", "the end panels of stacked rusticated blocks: plate 8, 130 px"),
    "porch_w": (5.06, "S71;S70", "C", "the porch over its piers' outer faces: plate 8 241 px (5.06 m); P0355 5.7 m"),
    "porch_d": (1.2, "S71", "C", "the porch's projection: plate 8 shows only a sliver of the piers' sides; 1.0-1.5 m (the reader)"),
    "door_w": (1.28, "S71", "C", "the door's opening: plate 8, 61 x 138 px"),
    "door_h": (2.9, "S71", "C", "the door's opening, flat-headed in a moulded frame, a carved shell hood above (plate 8, P0212)"),
    "step_run": (0.5, "S71", "C", "the three round steps' treads: plate 8, the lowest edge 42 px (0.9 m in the picture's plane) below the sill on the axis; v1's 0.35 m sat 0.7 m short"),
    "oval_w": (1.0, "S70;S71", "C", "the oval windows' openings: P0212 and P0296 about 1.0 m (plate 8 0.9 m)"),
    "oval_h": (1.8, "S70;S71", "C", "the ovals' height: P0212 (1922, the frames whole) and P0296 about 1.9 m, the plate 1.4 m: the stone as it stood wins; v2's 1.6 m sat 0.7 m short at the foot on P0212"),
    "oval_y": (2.0, "S71", "C", "the ovals' centres above the ground: plate 8"),
    "oval_x": (3.45, "S71", "C", "the ovals' centres either side of the axis: plate 8"),
    "up_inset": (0.55, "S71", "C", "the upper storey stands in from the podium's ends: plate 8, 12.9-13.0 m over the corner strips"),
    "up_set": (1.0, "S71", "C", "the walk before the upper storey: the balustrade crosses the lower part of every upper window on plate 8, so it stands before the wall; its width assumed"),
    "up_h": (4.9, "S71", "C", "the upper storey to its cornice's top (8.7 m above the ground): plate 8"),
    "upwin_w": (1.25, "S71", "C", "the upper windows: plate 8, 1.16, 1.37 and 1.2 m; tall round-headed French windows to the floor"),
    "upwin_wc": (1.37, "S71", "C", "the middle upper window"),
    "upwin_h": (3.5, "S71", "C", "their heads above the upper floor: plate 8"),
    "upwin_x": (3.75, "S71", "C", "the side windows' middles either side of the axis: plate 8 (x 1022 and 1381 against the axis 1203)"),
    "strip_w": (0.84, "S71", "C", "the carved corner strips of the upper storey: plate 8, 40 px"),
    "rail_end": (5.0, "S71", "C", "the walk's balustrade runs from the porch to 5.0 m either side of the axis, before the side windows only, and turns back to the wall: plate 8 (x 965 and 1438); v1's run to the corners sat 1.8 m out"),
    "rail_h": (1.1, "S71", "C", "the walk's balustrade above the upper floor: plate 8, rail top at y 748"),
    "skirt_top": (9.75, "S71", "C", "the lower roof's skirt from the cornice up to a short band that carries the upper roof: plate 8, y 515"),
    "skirt_over": (0.35, "S71", "C", "the lower eave's overhang past the corner strips: plate 8, 13.7 m over its tips"),
    "eave_up": (10.3, "S71", "C", "the upper roof's eave tips: plate 8 y 490; 10.7 m wide"),
    "eave_up_w": (10.7, "S71", "C", "the upper roof over its eave tips"),
    "ridge": (11.3, "S71", "C", "the ridge: plate 8 y 442, 4.6 m long; a hipped roof (no gable shows, C)"),
    "ridge_l": (4.6, "S71", "C", "the ridge's length: plate 8"),
    "crest": (12.5, "S71;S603", "C", "the crest cartouche on the ridge's middle, about 2 m wide: plate 8 y 382; Durand's 'H. 13 m' fits the crest or the ornaments' tips (S603, B)"),
    "stair_out": (4.6, "S71", "C", "the stairs' outer rails at their outermost, beyond the podium's ends: plate 8 4.7 m (W) and 4.1 m (E); the whole front 22.8 m (plan 24.6 m)"),
    "stair_foot": (3.4, "S71", "C", "the lowest step's middle beyond the podium's corner: plate 8 3.5 m (W), 3.2 m (E)"),
    "stair_w": (1.6, "S71;S70", "C", "the flights' width between the rails: assumed from plate 8's proportions"),
    "stair_land_z": (-5.4, "S70", "C", "the landing beside the end wall in its north half: P0773 (the rail's top north of the end window, a landing post beside the wall); P0295 the east stair's wall curving back"),
}
V = {k: v[0] for k, v in P.items()}

COL = {
    "rustic": "#d8d1c3", "joint": "#a39a8a", "marble": "#ebe6da", "wall": "#cfc6b4", "panel": "#c2bbab", "glaze": "#3f8a86", "sculpt": "#ddd7c9",
    "glass_win": "#2e4a4f", "door": "#4a3b2c", "roof": "#3d5f86", "roofedge": "#34506f", "ridge": "#c9a245", "pave": "#c9c2b2", "step": "#d2ccbe",
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


def frame_ring(c, yc, rx, ry, w, n, d=0.14):
    """An oval frame round an opening: a flat ring proud of the wall and its outer edge (Parts.oval fills its centre, which would cover the glass)."""
    o = [(c + (rx + w) * math.cos(2 * math.pi * k / n), yc + (ry + w) * math.sin(2 * math.pi * k / n)) for k in range(n)]
    i_ = [(c + rx * math.cos(2 * math.pi * k / n), yc + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]
    for k in range(n):
        a, b, cc, e = o[k], o[(k + 1) % n], i_[(k + 1) % n], i_[k]
        m.poly([(a[0], a[1], d), (b[0], b[1], d), (cc[0], cc[1], d), (e[0], e[1], d)], "marble")
        m.poly([(a[0], a[1], 0.0), (b[0], b[1], 0.0), (b[0], b[1], d), (a[0], a[1], d)], "marble")
        m.poly([(e[0], e[1], 0.0), (cc[0], cc[1], 0.0), (cc[0], cc[1], d), (e[0], e[1], d)], "marble")


def podium():
    """The ground storey: rusticated blocks, the end panels of stacked blocks, the ovals in carved frames, the porch with the door and its shell hood, three round steps;
    the cornice band at the upper floor's level. The back and the end faces carried round (fill), the west end's front part seen on P0773."""
    hw, d, ph = V["w"] / 2, V["d"], V["pod_h"]
    # the walls below run from 0.2 m under the ground (the faces' loop below); their corners are the joints (no skirt: it would cover the door and the ovals)
    for i, (x, z) in enumerate(rect(-hw, hw, -d, 0.0)):
        S.joint(f"podium_{i}", x, z, "wall foot", y=S.gy(x, z) - 0.15)
    sides = [((-hw, 0.0), (hw, 0.0), "doc"), ((hw, 0.0), (hw, -d), "fill"), ((hw, -d), (-hw, -d), "fill"), ((-hw, -d), (-hw, 0.0), "doc")]
    for i, (a, b, cls) in enumerate(sides):
        m.cls = cls
        L = face(a, b)
        holes = []
        if i == 0:
            for sx in (-1, 1):
                c = hw + sx * V["oval_x"]
                holes.append((c - V["oval_w"] / 2, c + V["oval_w"] / 2, V["oval_y"] - V["oval_h"] / 2, V["oval_y"] + V["oval_h"] / 2 - 0.01, 0.0))
        P_.wall_holes(0.0, L, -0.2, ph - 0.4, holes, "rustic")
        if i == 0:
            # the ovals' openings as ellipses inside the square holes: the corners filled, a grille, a carved frame with a leafy crest (plate 8, P0212)
            for sx in (-1, 1):
                c = hw + sx * V["oval_x"]
                rx, ry, yc = V["oval_w"] / 2, V["oval_h"] / 2, V["oval_y"]
                n = 16
                ell = [(c + rx * math.cos(2 * math.pi * k / n), yc + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]
                for q in range(4):  # the corner fillets between the ellipse and the square hole
                    ks = range(q * n // 4, (q + 1) * n // 4 + 1)
                    cx_ = c + rx * (1 if q in (0, 3) else -1)
                    cy_ = yc + ry * (1 if q in (0, 1) else -1)
                    for k0, k1 in zip(list(ks)[:-1], list(ks)[1:]):
                        p0, p1 = ell[k0 % n], ell[k1 % n]
                        m.poly([(cx_, cy_, 0.0), (p0[0], p0[1], 0.0), (p1[0], p1[1], 0.0)], "rustic")
                for k in range(n):
                    p0, p1 = ell[k], ell[(k + 1) % n]
                    m.poly([(p0[0], p0[1], 0.0), (p1[0], p1[1], 0.0), (p1[0], p1[1], -0.4), (p0[0], p0[1], -0.4)], "marble")
                m.poly([(p[0], p[1], -0.34) for p in ell], "glass_win")
                m.box(c - 0.03, c + 0.03, yc - ry, yc + ry, -0.34, -0.3, "marble", skip=("back",))
                for yy in (yc - ry / 2, yc, yc + ry / 2):
                    m.box(c - rx, c + rx, yy - 0.025, yy + 0.025, -0.34, -0.3, "marble", skip=("back",))
                frame_ring(c, yc, rx, ry, 0.28, n)
                m.poly([(c - 0.55, yc + ry + 0.25, 0.12), (c + 0.55, yc + ry + 0.25, 0.12), (c, yc + ry + 0.85, 0.12)], "sculpt")
                m.poly([(c - 0.35, yc - ry - 0.2, 0.12), (c + 0.35, yc - ry - 0.2, 0.12), (c, yc - ry - 0.55, 0.12)], "sculpt")
            # the end panels of stacked blocks (plate 8: two columns of blocks with sunk faces), and the rustication between
            for s0 in (0.0, L - V["end_panel"]):
                for row in range(5):
                    y0 = 0.35 + row * 0.62
                    for col in range(2):
                        x0 = s0 + 0.35 + col * (V["end_panel"] - 0.7) / 2
                        m.box(x0 + 0.05, x0 + (V["end_panel"] - 0.7) / 2 - 0.05, y0 + 0.05, y0 + 0.55, 0.0, 0.14, "rustic", skip=("back",))
                        m.box(x0 + 0.2, x0 + (V["end_panel"] - 0.7) / 2 - 0.2, y0 + 0.18, y0 + 0.42, 0.14, 0.16, "joint", skip=("back",))
        P_.rustication(0.0, L, 0.0, ph - 0.4, step=0.62)
        # the cornice band at the upper floor's level
        m.box(-0.1, L + 0.1, ph - 0.4, ph - 0.12, 0.0, 0.25, "marble", skip=("back",))
        m.box(-0.2, L + 0.2, ph - 0.12, ph, 0.0, 0.4, "marble", skip=("back",))
        m.pop()
    m.cls = "doc"
    m.flat(rect(-hw, hw, -d, 0.0), ph - 0.12, "rustic")
    # the porch: two rusticated piers, the door in its frame with the shell hood, the porch's top carries the balcony
    pw, pd = V["porch_w"] / 2, V["porch_d"]
    for sx in (-1, 1):  # the porch's sides from below the ground; its front is the door's wall
        S.skirt([(sx * pw, 0.0), (sx * pw, pd)], ph, "rustic", closed=False)
        S.joint(f"porch_{'W' if sx < 0 else 'E'}", sx * pw, pd, "wall foot", y=S.gy(sx * pw, pd) - 0.15)
    m.flat(rect(-pw, pw, 0.0, pd), ph, "marble")
    m.push(0.0, 0.0, pd)
    dw, dh = V["door_w"] / 2, V["door_h"]
    P_.wall_holes(-pw, pw, -0.2, ph - 0.4, [(-dw, dw, 0.0, dh, 0.0)], "rustic")
    P_.opening(-dw, dw, 0.0, dh, 0.0, depth=0.5, kind="door", frame=0.2)
    for s in (-pw + 0.5, pw - 0.5):  # the piers, 1 m wide, with stacked blocks and a cap
        for row in range(5):
            y0 = row * 0.68
            m.box(s - 0.5 - (0.05 if row % 2 else 0), s + 0.5 + (0.05 if row % 2 else 0), y0 + 0.04, y0 + 0.64, 0.0, 0.12, "rustic", skip=("back",))
        m.box(s - 0.58, s + 0.58, ph - 0.62, ph - 0.4, 0.0, 0.2, "marble", skip=("back",))
    # the shell hood over the door, reaching the porch's top (plate 8, P0212)
    for k in range(7):
        t0, t1 = math.pi * k / 7, math.pi * (k + 1) / 7
        m.poly([(0.0, dh + 0.25, 0.22), (0.75 * math.cos(t0), dh + 0.25 + 0.5 * math.sin(t0), 0.22), (0.75 * math.cos(t1), dh + 0.25 + 0.5 * math.sin(t1), 0.22)], "sculpt")
    m.box(-dw - 0.35, dw + 0.35, dh + 0.18, dh + 0.3, 0.0, 0.3, "marble", skip=("back",))
    m.box(-pw - 0.1, pw + 0.1, ph - 0.4, ph - 0.12, 0.0, 0.25, "marble", skip=("back",))
    m.box(-pw - 0.2, pw + 0.2, ph - 0.12, ph, 0.0, 0.4, "marble", skip=("back",))
    m.pop()
    for sx in (-1, 1):  # the porch's side faces
        m.cls = "doc"
        m.push(sx * pw, 0.0, pd if sx < 0 else 0.0, -sx * math.pi / 2)
        P_.rustication(0.0, pd, 0.0, ph - 0.4, step=0.68)
        m.pop()
    S.kp("porch_foot_L", (-pw, 0.0, pd))
    S.kp("porch_foot_R", (pw, 0.0, pd))
    S.kp("porch_top_L", (-pw - 0.2, ph, pd + 0.4))
    S.kp("porch_top_R", (pw + 0.2, ph, pd + 0.4))
    S.kp("door_head", (0.0, dh, pd))
    S.kp("door_sill", (0.0, 0.0, pd))
    for sx, t in ((-1, "W"), (1, "E")):
        S.kp(f"oval_{t}_top", (sx * V["oval_x"], V["oval_y"] + V["oval_h"] / 2, 0.0))
        S.kp(f"oval_{t}_foot", (sx * V["oval_x"], V["oval_y"] - V["oval_h"] / 2, 0.0))
    S.kp("pod_foot_SW", (-hw, 0.0, 0.0))
    S.kp("pod_foot_SE", (hw, 0.0, 0.0))
    S.kp("pod_top_SW", (-hw - 0.2, ph, 0.4))
    S.kp("pod_top_SE", (hw + 0.2, ph, 0.4))
    # three round steps before the porch, as wide as it (plate 8)
    tr = V["step_run"]
    for k in range(3):
        r = pw + tr * (3 - k)
        y = 0.17 * (k + 1)
        pts = [(r * math.cos(math.pi * j / 20), pd + (tr * (3 - k) + 0.25) * math.sin(math.pi * j / 20)) for j in range(21)]
        lo = min(S.gy(*c) for c in pts) - 0.15
        m.prism(pts, lo, y, "step")
    S.kp("step_foot_C", (0.0, 0.0, pd + tr * 3 + 0.25))
    S.joint("steps_C", 0.0, pd + tr * 3 + 0.15, "stair foot")
    S.entry("door_C", 0.0, pd + tr * 3 + 0.85)
    S.FOOTPRINTS.append(rect(-pw - tr * 3, pw + tr * 3, 0.0, pd + tr * 3 + 0.3))
    S.FOOTPRINTS.append(rect(-hw, hw, -d, 0.0))


def upper():
    """The upper storey: three tall round-headed windows to the floor with scrolled broken pediments, carved corner strips, the frieze of rosettes and the cornice;
    the end windows with their small balconies (P0773); the walk before it and its balustrade, the balcony over the porch with urn pairs (plate 8)."""
    hw, d, ph = V["w"] / 2, V["d"], V["pod_h"]
    ux, us = hw - V["up_inset"], V["up_set"]
    yb, yc = ph, ph + V["up_h"]
    us = V["up_set"]
    z0, z1 = -us, -d + us * 0.55
    sides = [((-ux, z0), (ux, z0), "doc"), ((ux, z0), (ux, z1), "fill"), ((ux, z1), (-ux, z1), "fill"), ((-ux, z1), (-ux, z0), "doc")]
    for i, (a, b, cls) in enumerate(sides):
        m.cls = cls
        L = face(a, b)
        if i == 0:
            xs = [(ux - V["upwin_x"], V["upwin_w"]), (ux, V["upwin_wc"]), (ux + V["upwin_x"], V["upwin_w"])]
        elif i in (1, 3):
            xs = [(L / 2, V["upwin_w"])]
        else:
            xs = [(L / 2 - V["upwin_x"], V["upwin_w"]), (L / 2, V["upwin_w"]), (L / 2 + V["upwin_x"], V["upwin_w"])]
        holes = [(s - w / 2, s + w / 2, yb, yb + V["upwin_h"] - w / 2, w / 2) for s, w in xs]
        P_.wall_holes(0.0, L, yb - 0.05, yc - 0.9, holes, "wall")
        for (s, w), h in zip(xs, holes):
            P_.opening(*h, depth=0.35, kind="win", frame=0.16)
            # the scrolled broken pediment with its cartouche, and the side ears (plate 8)
            top = yb + V["upwin_h"] + 0.16
            for sg in (-1, 1):
                m.poly([(s + sg * (w / 2 + 0.4), top, 0.15), (s + sg * 0.25, top + 0.45, 0.15), (s + sg * 0.25, top + 0.2, 0.15), (s + sg * (w / 2 + 0.25), top - 0.15, 0.15)], "sculpt")
                m.box(s + sg * (w / 2 + 0.22) - 0.08, s + sg * (w / 2 + 0.22) + 0.08, top - 1.2, top - 0.2, 0.0, 0.14, "sculpt", skip=("back",))
            P_.cartouche(s, top + 0.35, 0.4, 0.5)
        # the carved corner strips: square panels with crossed diagonals between leaf bands (plate 8)
        for s in (V["strip_w"] / 2, L - V["strip_w"] / 2):
            sw = V["strip_w"]
            m.box(s - sw / 2, s + sw / 2, yb, yc - 0.9, 0.0, 0.18, "marble", skip=("back",))
            for k in range(4):
                y0 = yb + 0.3 + k * (V["up_h"] - 1.4) / 4
                pnl = (V["up_h"] - 1.4) / 4 - 0.25
                m.box(s - sw / 2 + 0.12, s + sw / 2 - 0.12, y0, y0 + pnl, 0.18, 0.2, "panel", skip=("back",))
                m.poly([(s - sw / 2 + 0.16, y0 + 0.05, 0.21), (s - sw / 2 + 0.24, y0 + 0.05, 0.21), (s + sw / 2 - 0.16, y0 + pnl - 0.05, 0.21), (s + sw / 2 - 0.24, y0 + pnl - 0.05, 0.21)], "sculpt")
                m.poly([(s + sw / 2 - 0.16, y0 + 0.05, 0.21), (s + sw / 2 - 0.24, y0 + 0.05, 0.21), (s - sw / 2 + 0.16, y0 + pnl - 0.05, 0.21), (s - sw / 2 + 0.24, y0 + pnl - 0.05, 0.21)], "sculpt")
        P_.entablature(0.0, L, yc, h=0.9, out=0.4)
        for k in range(6 if i in (0, 2) else 2):  # the rosettes in the frieze
            s = L * (k + 0.5) / (6 if i in (0, 2) else 2)
            m.box(s - 0.14, s + 0.14, yc - 0.6, yc - 0.34, 0.16, 0.22, "sculpt", skip=("back",))
        m.pop()
    m.cls = "doc"
    S.kp("up_cornice_SW", (-ux - 0.4, yc, z0 + 0.4))
    S.kp("up_cornice_SE", (ux + 0.4, yc, z0 + 0.4))
    S.kp("up_cornice_NW", (-ux - 0.4, yc, z1 - 0.4))
    S.kp("up_cornice_NE", (ux + 0.4, yc, z1 - 0.4))
    S.kp("upwin_C_head", (0.0, yb + V["upwin_h"], z0))
    S.kp("upwin_C_sill", (0.0, yb, z0))
    S.kp("upwin_W_head", (-V["upwin_x"], yb + V["upwin_h"], z0))
    S.kp("upwin_E_head", (V["upwin_x"], yb + V["upwin_h"], z0))
    S.kp("end_W_win_head", (-ux, yb + V["upwin_h"], (z0 + z1) / 2))
    S.kp("end_E_win_head", (ux, yb + V["upwin_h"], (z0 + z1) / 2))
    # the core's top under the roof (no gap shows under the skirt)
    m.flat(rect(-ux, ux, z1, z0), yc, "wall")
    # the walk's balustrade on the podium's edge before the side windows, the balcony over the porch (plate 8), round the ends to the landings (P0773), fill at the back
    pw, pd = V["porch_w"] / 2, V["porch_d"]
    rh = V["rail_h"]
    zr = 0.25
    re_ = V["rail_end"]
    for sx in (-1, 1):
        P_.rail([(sx * (pw + 0.05), zr), (sx * re_, zr), (sx * re_, -us + 0.05)], ph, h=rh, posts=2.0)
        m.box(sx * (pw + 0.05) - 0.3, sx * (pw + 0.05) + 0.3, ph, ph + rh + 0.2, zr - 0.3, zr + 0.3, "marble")
    P_.rail([(-pw + 0.25, pd - 0.2), (pw - 0.25, pd - 0.2)], ph, h=rh, posts=2.6)
    for sx in (-1, 1):
        P_.rail([(sx * (pw - 0.25), zr), (sx * (pw - 0.25), pd - 0.2)], ph, h=rh, posts=2.0)
        x = sx * (pw - 0.25)
        m.box(x - 0.32, x + 0.32, ph, ph + rh + 0.3, pd - 0.52, pd + 0.12, "marble")  # the balcony's pedestals with urn pairs
        for dz in (-0.12, 0.12):
            P_.urn(x + dz, pd - 0.2, ph + rh + 0.3, 0.6)
    S.kp("bal_rail_C", (0.0, ph + rh, pd - 0.2))
    S.kp("bal_rail_L", (-re_, ph + rh, zr))
    S.kp("bal_rail_R", (re_, ph + rh, zr))
    # round the ends: from the front corner to the landing (the end window's balcony between), and the back (fill)
    zl = V["stair_land_z"]
    for sx in (-1, 1):
        x = sx * (hw - 0.25)
        P_.rail([(x, -us), (x, zl + 1.1)], ph, h=rh, posts=2.0)
        m.cls = "fill"
        P_.rail([(x, zl - 1.1), (x, -d + 0.25)], ph, h=rh, posts=2.0)
        m.cls = "doc"
    m.cls = "fill"
    P_.rail([(-(hw - 0.25), -d + 0.25), (hw - 0.25, -d + 0.25)], ph, h=rh, posts=2.5)
    m.cls = "doc"


def roofs():
    """The double-eaved Chinese roof (plate 8): a tiled skirt all round from the cornice, a short band, the upper hipped roof with a short ridge, the crest cartouche on
    the ridge's middle and scrolled ornaments on its ends and the upper eave's corners. The tiles glazed blue (S06, through the box's row; violet and green if Choutzé's
    pavilion of 1876 is this one, Q69): C."""
    hw, d, ph = V["w"] / 2, V["d"], V["pod_h"]
    ux, us = hw - V["up_inset"], V["up_set"]
    z0, z1 = -us, -d + us * 0.55
    zc = (z0 + z1) / 2
    hz = (z0 - z1) / 2
    yc = ph + V["up_h"]
    o = V["skirt_over"] + 0.4
    lo = [(-ux - o, z0 + o), (ux + o, z0 + o), (ux + o, z1 - o), (-ux - o, z1 - o)]
    bx, bz = V["eave_up_w"] / 2 - 0.6, hz - 0.6
    hi = [(-bx, zc + bz), (bx, zc + bz), (bx, zc - bz), (-bx, zc - bz)]
    ys = V["skirt_top"]
    mid = [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in zip(lo, hi)]
    m.frustum(lo, mid, yc, yc + (ys - yc) * 0.4, "roofedge")
    m.frustum(mid, hi, yc + (ys - yc) * 0.4, ys, "roof")
    m.flat(lo, yc, "roofedge")
    for (x, z) in lo:  # the curled corner tips with small scrolls
        m.box(x - 0.18, x + 0.18, yc, yc + 0.35, z - 0.18, z + 0.18, "ridge")
    S.kp("eave_lo_SW", (lo[0][0], yc + 0.2, lo[0][1]))
    S.kp("eave_lo_SE", (lo[1][0], yc + 0.2, lo[1][1]))
    m.box(-bx, bx, ys, V["eave_up"] - 0.05, zc - bz, zc + bz, "wall")
    r = P_.roof_hip(0.0, zc, V["eave_up_w"] / 2, hz + 0.2, V["eave_up"] - 0.25, V["ridge"], n=6, lift=0.3, ridge_y=0.15)
    S.kp("eave_up_SW", r["eaves"][(-1, 1)])
    S.kp("eave_up_SE", r["eaves"][(1, 1)])
    rl = V["ridge_l"] / 2
    yr = V["ridge"] + 0.15
    for sx, t in ((-1, "W"), (1, "E")):
        S.kp(f"ridge_{t}", (sx * rl, yr, zc))
        pts = [(sx * rl, yr), (sx * (rl + 0.1), yr + 0.4), (sx * (rl - 0.25), yr + 0.75), (sx * (rl - 0.55), yr + 0.55), (sx * (rl - 0.35), yr)]
        for dz in (-0.1, 0.1):
            m.poly([(p[0], p[1], zc + dz) for p in pts], "ridge")
    # the crest cartouche: scrolls and leaves about 2 m wide on the ridge's middle (plate 8)
    ck = V["crest"]
    crest = [(-1.0, yr), (-0.95, yr + 0.45), (-0.55, yr + 0.55), (-0.4, yr + 0.95), (0.0, ck), (0.4, yr + 0.95), (0.55, yr + 0.55), (0.95, yr + 0.45), (1.0, yr)]
    for dz in (-0.12, 0.12):
        m.poly([(p[0], p[1], zc + dz) for p in crest], "ridge")
    S.kp("crest_top_C", (0.0, ck, zc))


def stairs():
    """The two curved stairs (plate 8; P0773; P0295): from a foot at the front, 3.4 m beyond the podium's corner, the flight runs out and back round a curve, its outermost
    point at mid-height, to a landing at the podium's top in the north half of the end. Solid walls under it, a wave-scroll parapet on the outer edge (P0773), a lower one
    on the inner edge, a volute at the foot (plate 8). The treads' count: about 20 visible on the plate; the rise the podium's."""
    hw, d, ph = V["w"] / 2, V["d"], V["pod_h"]
    w = V["stair_w"]
    zl = V["stair_land_z"]
    for sx, t in ((-1, "W"), (1, "E")):
        # the centreline in plan: foot, outermost, landing (P0773: the top north of the end window)
        xo = hw + V["stair_out"] - 0.25 - w / 2
        ctrl = [(hw + V["stair_foot"], 1.8), (xo - 0.45, 0.6), (xo, -1.3), (xo - 0.3, -3.2), (hw + 2.2, zl - 0.2), (hw + 1.0, zl)]
        pts = lobed_open(ctrl, 6)
        pts = [(sx * x, z) for x, z in pts]
        L = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts[:-1], pts[1:]))
        n = 22
        rise = ph / n
        # sample the band along the centreline: n steps, each a prism from the ground to its tread
        s_acc = [0.0]
        for a, b in zip(pts[:-1], pts[1:]):
            s_acc.append(s_acc[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))

        def at(s):
            for k in range(len(pts) - 1):
                if s_acc[k + 1] >= s:
                    t_ = (s - s_acc[k]) / max(1e-9, s_acc[k + 1] - s_acc[k])
                    a, b = pts[k], pts[k + 1]
                    x, z = a[0] + (b[0] - a[0]) * t_, a[1] + (b[1] - a[1]) * t_
                    tx, tz = (b[0] - a[0]), (b[1] - a[1])
                    ln = math.hypot(tx, tz)
                    return x, z, tx / ln, tz / ln
            a, b = pts[-2], pts[-1]
            ln = math.hypot(b[0] - a[0], b[1] - a[1])
            return b[0], b[1], (b[0] - a[0]) / ln, (b[1] - a[1]) / ln

        L_fl = L - 1.0  # the flight; the last metre the landing
        edges_o, edges_i, ys = [], [], []
        for k in range(n + 1):
            x, z, tx, tz = at(L_fl * k / n)
            nx, nz = -tz, tx  # the normal; its sign: outward = away from the building's axis
            if nx * sx < 0:
                nx, nz = -nx, -nz
            edges_o.append((x + nx * w / 2, z + nz * w / 2))
            edges_i.append((x - nx * w / 2, z - nz * w / 2))
            ys.append(rise * k)
        for k in range(n):
            q = [edges_i[k], edges_o[k], edges_o[k + 1], edges_i[k + 1]]
            lo = min(S.gy(*c) for c in q) - 0.15
            m.prism(q, lo, rise * (k + 1), "step")
        # the landing: from the flight's top to the podium's end, at its top
        xe, ze, _, _ = at(L)
        lq = [edges_i[n], edges_o[n], (sx * (hw - 0.02), ze - w / 2 - 0.3), (sx * (hw - 0.02), ze + w / 2 + 0.3)]
        lo = min(S.gy(*c) for c in lq) - 0.15
        m.prism([(x, z) for x, z in lq], lo, ph, "step")
        # the parapets: solid walls under the flight (P0773: coursed stone), a wave-scroll band on the outer edge, a lower band on the inner
        for edge, h, cls, wave in ((edges_o, 0.95, "doc", 0.25), (edges_i, 0.7, "fill" if sx > 0 else "doc", 0.12)):
            m.cls = cls
            for k in range(n):
                a, b = edge[k], edge[k + 1]
                ga, gb = S.gy(*a) - 0.15, S.gy(*b) - 0.15
                ya, yb = ys[k] + h, ys[k + 1] + h
                m.poly([(a[0], ga, a[1]), (b[0], gb, b[1]), (b[0], yb, b[1]), (a[0], ya, a[1])], "marble")
                # the wave: a small arc over each step's length
                mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
                m.poly([(a[0], ya, a[1]), (b[0], yb, b[1]), (mx, (ya + yb) / 2 + wave, mz)], "sculpt")
                m.poly([(a[0], ya - 0.12, a[1]), (b[0], yb - 0.12, b[1]), (b[0], yb, b[1]), (a[0], ya, a[1])], "marble")
            m.cls = "doc"
        # the volute at the foot of the outer parapet (plate 8)
        fx, fz = edges_o[0]
        m.lathe([(0.5, 0.0), (0.55, 0.3), (0.45, 0.75), (0.25, 1.0), (0.0, 1.05)], 8, "sculpt", cx=fx, cz=fz + 0.2)
        # the landing post beside the end wall (P0773) with an urn
        px, pz = sx * (hw + 0.3), ze - w / 2 - 0.15
        m.box(px - 0.3, px + 0.3, ph, ph + 1.2, pz - 0.3, pz + 0.3, "marble")
        P_.urn(px, pz, ph + 1.2, 0.6)
        fx0, fz0, tx0, tz0 = at(0.0)
        S.kp(f"stair_{t}_foot", (fx0, 0.0, fz0))
        S.kp(f"stair_{t}_rail_foot", (edges_o[0][0], 0.95, edges_o[0][1]))
        S.kp(f"stair_{t}_top", (edges_o[n][0], ph + 0.95, edges_o[n][1]))
        ko = max(range(n + 1), key=lambda k: sx * edges_o[k][0])
        S.kp(f"stair_{t}_out", (edges_o[ko][0], ys[ko] + 0.95, edges_o[ko][1]))
        S.joint(f"stair_{t}_foot", fx0 - tx0 * 0.1, fz0 - tz0 * 0.1, "stair foot")
        S.entry(f"stair_{t}_foot", fx0 - tx0 * 0.7, fz0 - tz0 * 0.7)
        S.FOOTPRINTS.append(edges_i + edges_o[::-1])
        S.FOOTPRINTS.append(lq)
        for k in (n // 3, 2 * n // 3):
            x, z = edges_o[k]
            S.JOINTS.append([f"stair_{t}_wall_{k}", x, S.gy(x, z) - 0.15, z, "wall foot"])


def lobed_open(points, n=6):
    """An open smooth line through control points: Catmull-Rom with the ends repeated."""
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2 + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3) for c in range(2)))
    out.append(points[-1])
    return out


def court():
    """The paved apron before the front, between the stairs' feet, to the box's front (S01's porch and stairs, XY06-M26): plain slabs (plate 8), C."""
    hw = V["w"] / 2
    zf = 3.15
    q = rect(-hw - 3.0, hw + 3.0, 0.0, zf + 1.0)
    pts = [(x, z) for x, z in q]
    y = max(S.gy(x, z) for x, z in pts) + 0.02
    m.flat(pts, y, "pave")
    x = -hw - 3.0
    while x < hw + 3.0:
        m.box(x - 0.03, x + 0.03, y, y + 0.01, 0.1, zf + 0.9, "joint", skip=("bottom",))
        x += 1.5


def build():
    global S, m, P_
    S = Site("XY06-M27")
    m = Mesh(COL)
    S.m = m
    P_ = Parts(m, rail_h=V["rail_h"], baluster_segs=4)
    m.cls = "doc"
    court()
    podium()
    upper()
    roofs()
    stairs()


def summary(tris, fill, size):
    rows = [
        ["Podium", f"{V['w']:g} × {V['d']:g} m (S603, survey, B), {V['pod_h']:g} m to the upper floor (plate 8, C): rusticated, end panels of stacked blocks, two oval windows with grilles in carved frames, the porch {V['porch_w']:g} m wide with the door ({V['door_w']:g} × {V['door_h']:g} m) and its shell hood, three round steps (plate 8; P0212, P0355, C); the 'low room under the terrace' (S258, B)"],
        ["Upper storey", f"{V['w'] - 2 * V['up_inset']:.1f} m wide, set back {V['up_set']:g} m behind a balustrade on the podium's top, with the balcony over the porch and its urn pairs; three tall round-headed windows with scrolled pediments, carved corner strips, a frieze of rosettes, the cornice {V['pod_h'] + V['up_h']:.1f} m above the ground (plate 8, C); a window with a small balcony on each end (P0773, 1873, C)"],
        ["Roof", f"double-eaved Chinese roof: the skirt from the cornice, the upper hipped roof with a {V['ridge_l']:g} m ridge at {V['ridge']:g} m, the crest at {V['crest']:g} m (plate 8, C; Durand's H. 13 m, S603, B); glazed blue tile (S06, C; violet and green if Choutzé's pavilion of 1876 is this one, Q69)"],
        ["Stairs", f"two curved stairs from feet {V['stair_foot']:g} m beyond the podium's corners, out to {V['stair_out']:g} m and back to landings at the upper floor in the north half of the ends (plate 8, P0773, P0295, C): solid walls, a wave-scroll parapet, a volute at the foot"],
        ["Assumed", "the back, the east end above its stair, the stairs' inner faces and the apron's paving: carried round from the front (C, the pale tint with conf=1)"],
    ]
    return {
        "id": "XY06", "aliases": [], "name": "方外观 Fangwaiguan", "glb": "model.glb", "position": S.pos, "rotationY": S.rot,
        "line": "Modelled from plate 8 of 1783-86, Ohlmer's photograph of 1873 (the roof still on), the ruin photographs since 1914 and Durand's survey (S603); every figure is a reading (C) unless the row says otherwise. The back and the faces no picture shows are carried round (assumed).",
        "rows": rows,
        "caption": {"frontage_m": V["w"], "depth_m": V["d"], "eave_m": round(V["pod_h"] + V["up_h"], 1), "ridge_m": V["ridge"], "assumed": True, "confidence": "C"},
        "hides": [],
        "tris": tris, "fill_tris": fill, "glb_bytes": size,
    }


def main():
    build()
    size = m.write_glb(HERE / "model.glb", "XY06 方外观 Fangwaiguan", extras={"id": "XY06"})
    tris = m.count()
    prims = {k: len(v["idx"]) // 3 for k, v in sorted(m.prims.items())}
    fill = sum(n for k, n in prims.items() if k.endswith("~fill"))
    S.write(HERE, "XY06", ["XY06"], P, "x east along the front, y up from the ground at the hall's box, z south (out of the front); the origin at the podium's front middle; metres", summary(tris, fill, size))
    print(f"model.glb {size / 1e6:.2f} MB, {tris} triangles ({fill} fill), {P_.balusters} balusters, {len(S.KP)} key points, {len(S.JOINTS)} joints, {len(S.ENTRIES)} entries; position {S.pos} rotY {S.rot}")


if __name__ == "__main__":
    main()
