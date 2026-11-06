#!/usr/bin/env python3
"""线法墙 Xianfa Qiang (XY15), the perspective walls east of 方河, the nineteenth detailed model (Round 30): an outdoor stage of flats set like wings, narrowing towards a
back wall, with a European town painted across them, seen from the far side of the water (S02 pp.159-160; plate 20, 湖东线法画, P0060; the plan's 线法画, S01).
The first pair of flats, nearest the water, are the two rusticated arched gates plate 20 draws at its edges: banded piers, an arch with radiating voussoirs, corbels with
figures under the cornice, a hipped stone cap with urns and a pineapple, a lion on a ball on a console at each side. The other five pairs are flats cut to the outline of the
painted houses, their tops falling towards the axis as a street's eaves would; the back wall is cut to a range of hills. The painted scenes themselves are lost: the flats carry
the houses' parts in low relief (roofs, windows, doors), assumed. The landing on the axis: six steps down to 方河 with rounded ends (plate 20).
Plain geometry, one GLB (scripts/model_mesh.py) with every figure in params.json; the method is the pilot's (models/XY01-xieqiqu/README.md).

  uv run python models/XY15-xianfa-qiang/xianfaqiang.py

Writes, beside this file: model.glb, params.json, keypoints.json, joints.json, summary.json (models/README.md).
Frame (scripts/model_site.py): origin at the front middle of the back wall's box XY15-M69, which faces west: x along the front to the right as one faces it from the west
(south), y up from the box's ground, z west (out of the front, towards 方河). Each flat stands on its own box of Round 6 (S01's six a side, moved 5 m as 方河 is).
Grades: the gates and the landing as plate 20 draws them are `doc` (C); the flats' outlines and their relief, the back wall's outline and every back are `fill` (assumed, C).
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

# Plate 20's left gate is read at the plan's flat, 7.3 m over its body's 332 px (x 179-511 on the 2400 px copy), the foot at y 879 (Round 30 readings).
P = {
    "flat_w": (7.3, "S01", "C", "each flat: S01's elements 7.27 x 1.8 m (b), six a side (Q16, Q73); the boxes of Round 6 place them"),
    "flat_t": (0.45, "S02", "C", "a flat's thickness: S02 'walls set like the wings of a stage'; the plan's 1.8 m ink taken as the flat and its bracing behind (assumed)"),
    "gate_arch_w": (2.38, "S71;S01", "C", "the gates' arches: plate 20, 100 px of the left gate's 350 (2.09 m) and 110 of the right's 300 (2.68 m) at the plan's 7.3 m; the mean (Q314)"),
    "gate_arch_top": (6.55, "S71;S01", "C", "the arches' crowns: plate 20, the left gate 6.03 m, the right 7.06 m on their own widths; the mean (Q314)"),
    "gate_cornice": (8.6, "S71;S01", "C", "the cornice's top: plate 20, the left gate 7.97 m (y 497 over 879, 47.9 px/m), the right 9.29 m (y 522 over 904, 41.1 px/m): the plate draws the two gates 17% apart in proportion (Q314); the mean, near the dossier's 8.7 m"),
    "gate_cornice_h": (0.7, "S71", "C", "the cornice's depth: plate 20, y 494-526"),
    "gate_ridge": (10.4, "S71;S01", "C", "the hipped cap's ridge: plate 20, 9.62 and 11.19 m (y 418, 444); its length 3.9 m (x 255-445)"),
    "gate_ridge_l": (3.85, "S71", "C", "the cap's ridge length: plate 20, 190 px of the left gate's 350 (3.96 m) and 154 of the right's 300 (3.75 m)"),
    "gate_urn": (11.0, "S71;S01", "C", "the urns at the ridge's ends, their tips: plate 20, 10.35 and 11.65 m"),
    "gate_pine": (11.65, "S71;S01", "C", "the pineapple on the ridge's middle, its tip: plate 20, 10.8 and 12.5 m"),
    "gate_course": (0.6, "S71", "C", "the piers' courses of banded blocks: plate 20, eight from the impost band to the foot on the left gate"),
    "lion_y": (5.0, "S71;S01", "C", "the impost ledge the lions sit on, at the piers' outer corners: plate 20, 4.4 and 5.7 m; the lions on balls to about 6.1 m"),
    "eye_h": (1.6, "S02", "C", "the height the flats' eaves converge to on the axis (a standing viewer across the water): the stage's rule, assumed"),
    "eave_1": (8.2, "S71", "C", "the eaves' height at the first pair's offset (23.2 m), just under the gates' cornice: plate 20's painted houses beside the gates rise to it; assumed"),
    "flat_min": (4.2, "S71", "C", "the lowest flat's top: assumed, so that the innermost pair still screens the wings behind"),
    "back_h": (6.0, "S02;S71", "C", "the back wall's height with hills on it to 7.6 m: S02 'a back wall' painted; plate 20 paints hills behind the town; the height assumed"),
    "steps_w": (9.0, "S71", "C", "the landing's width on the axis: plate 20, its top step about 530 px against the gates' 1,340 px apart; assumed from the camera prior"),
    "steps_n": (6, "S71", "C", "six steps with rounded ends, each wider than the one above: plate 20, read at 1.5x (the dossier's first count was five)"),
}
V = {k: v[0] for k, v in P.items()}

COL = {
    "rustic": "#d8cfbd", "joint": "#9f9584", "marble": "#ebe6da", "wall": "#d9d2c3", "sculpt": "#ddd6c6", "panel": "#c2bbab", "roof": "#d2cab9", "roofedge": "#c6bead", "ridge": "#d9d2c3",
    "scene": "#e2dccd", "scene_roof": "#8c6f5c", "glass_win": "#2e4a4f", "door": "#4a3b2c", "timber": "#6f5b47", "pave": "#c9c2b2", "step": "#d2ccbe", "hill": "#a6ad97",
    "gilt": "#b59a52", "jet": "#d8ecf2",
}

S = None
m = None
P_ = None


def rect(x0, x1, z0, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def screens():
    """The flats' boxes of Round 6, by pair from the water: [(bid, side, k)]: XY15-M57 N1, M58 S1, ..., M67 N6, M68 S6."""
    out = []
    for k in range(6):
        out.append((f"XY15-M{57 + 2 * k}", "N", k + 1))
        out.append((f"XY15-M{58 + 2 * k}", "S", k + 1))
    return out


def eave(o):
    """The flats' top at the offset o from the axis: a street's eaves falling to the eye's height on the axis (the stage's rule, assumed)."""
    return max(V["flat_min"], V["eye_h"] + (V["eave_1"] - V["eye_h"]) * o / 23.2)


# ------------------------------------------------------------------ the gates (the first pair), plate 20
def gate(cx, zf, lr):
    """A rusticated arched gate on the flat whose west face is at z = zf, middle x = cx; drawn in a face frame facing west (+z)."""
    w = V["flat_w"]
    aw, at = V["gate_arch_w"], V["gate_arch_top"]
    sp = at - aw / 2
    yc, ch = V["gate_cornice"], V["gate_cornice_h"]
    pier = (w - aw) / 2
    m.cls = "doc"
    m.push(cx - w / 2, 0.0, zf, 0.0)
    c = w / 2
    P_.wall_holes(0.0, w, 0.0, yc - ch, [(c - aw / 2, c + aw / 2, 0.0, sp, aw / 2)], "rustic")
    for s0 in (0.0, w - pier):  # the piers' banded blocks to the impost
        P_.rusticated(s0 + 0.05, s0 + pier - 0.05, 0.25, sp, course=V["gate_course"], out=0.16)
        m.box(s0, s0 + pier, sp - 0.05, sp + 0.25, 0.0, 0.28, "marble", skip=("back",))  # the impost band
    m.box(0.0, w, 0.0, 0.25, 0.0, 0.3, "marble", skip=("back",))
    # the arch's ring and the voussoirs radiating to the cornice (plate 20)
    pts = arc_pts(c - aw / 2, c + aw / 2, sp, aw / 2, 14)
    ring = arc_pts(c - aw / 2 - 0.35, c + aw / 2 + 0.35, sp, aw / 2 + 0.35, 14)
    for (p0, q0), (p1, q1) in zip(zip(pts[:-1], ring[:-1]), zip(pts[1:], ring[1:])):
        m.poly([(p0[0], p0[1], 0.14), (q0[0], q0[1], 0.14), (q1[0], q1[1], 0.14), (p1[0], p1[1], 0.14)], "marble")
    for k in range(1, 12):  # the fan of joints from the arch up to the cornice
        a = math.pi * k / 12
        r0, r1 = aw / 2 + 0.38, aw / 2 + 2.6
        x0, y0 = c + r0 * math.cos(a), sp + r0 * math.sin(a)
        x1, y1 = c + r1 * math.cos(a), sp + r1 * math.sin(a)
        if y1 > yc - ch - 0.05:
            t = (yc - ch - 0.05 - y0) / (y1 - y0)
            x1, y1 = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        x1 = min(max(x1, 0.05), w - 0.05)
        nx, ny = -math.sin(a) * 0.035, math.cos(a) * 0.035
        m.poly([(x0 - nx, y0 - ny, 0.03), (x1 - nx, y1 - ny, 0.03), (x1 + nx, y1 + ny, 0.03), (x0 + nx, y0 + ny, 0.03)], "joint")
    m.box(c - 0.3, c + 0.3, at - 0.1, at + 0.75, 0.0, 0.32, "marble", skip=("back",))  # the keystone
    # the arch's reveal through the flat and the painted house seen through it (plate 20 shows a house with a round-headed window inside the arch)
    for s in (c - aw / 2, c + aw / 2):
        m.poly([(s, 0.0, 0.0), (s, sp, 0.0), (s, sp, -V["flat_t"]), (s, 0.0, -V["flat_t"])], "rustic")
    for p0, p1 in zip(pts[:-1], pts[1:]):
        m.poly([(p0[0], p0[1], 0.0), (p1[0], p1[1], 0.0), (p1[0], p1[1], -V["flat_t"]), (p0[0], p0[1], -V["flat_t"])], "rustic")
    # the corbels with figures under the cornice at the piers' tops
    for s in (pier / 2, w - pier / 2):
        m.box(s - 0.32, s + 0.32, yc - ch - 1.2, yc - ch, 0.0, 0.38, "marble", skip=("back",))
        m.box(s - 0.16, s + 0.16, yc - ch - 1.05, yc - ch - 0.2, 0.38, 0.46, "sculpt", skip=("back",))
    # the cornice
    m.box(-0.2, w + 0.2, yc - ch, yc - ch + 0.25, -0.05, 0.3, "marble", skip=("back",))
    m.box(-0.35, w + 0.35, yc - ch + 0.25, yc, -0.2, 0.45, "marble")
    S.kp(f"gate_{lr}_arch_crown", _w((c, at, 0.0)))
    S.kp(f"gate_{lr}_arch_foot_l", _w((c - aw / 2, 0.25, 0.0)), anchor=True)
    S.kp(f"gate_{lr}_arch_foot_r", _w((c + aw / 2, 0.25, 0.0)), anchor=True)
    S.kp(f"gate_{lr}_foot_l", _w((0.0, 0.0, 0.0)), anchor=True)
    S.kp(f"gate_{lr}_foot_r", _w((w, 0.0, 0.0)), anchor=True)
    S.kp(f"gate_{lr}_cornice_l", _w((-0.35, yc, 0.45)))
    S.kp(f"gate_{lr}_cornice_r", _w((w + 0.35, yc, 0.45)))
    # the lions on their balls on consoles at the outer sides (plate 20)
    for s, nm in ((0.3, "l"), (w - 0.3, "r")):  # plate 20: on the impost band at the piers' outer corners, on projecting consoles
        m.box(s - 0.45, s + 0.45, V["lion_y"] - 0.5, V["lion_y"], -0.2, 0.75, "marble")
        m.lathe([(0.3, V["lion_y"]), (0.36, V["lion_y"] + 0.3), (0.3, V["lion_y"] + 0.6), (0.0, V["lion_y"] + 0.62)], 8, "sculpt", cx=s, cz=0.35)
        m.box(s - 0.25, s + 0.25, V["lion_y"] + 0.55, V["lion_y"] + 1.05, 0.05, 0.6, "sculpt")
        m.lathe([(0.22, V["lion_y"] + 0.95), (0.28, V["lion_y"] + 1.15), (0.2, V["lion_y"] + 1.3), (0.0, V["lion_y"] + 1.33)], 8, "sculpt", cx=s, cz=0.5)
        S.kp(f"gate_{lr}_lion_{nm}", _w((s, V["lion_y"] + 1.3, 0.5)))
    m.pop()
    # the back of the flat (fill): plain, the bracing posts behind
    m.cls = "fill"
    m.push(cx + w / 2, 0.0, zf - V["flat_t"], math.pi)
    P_.wall_holes(0.0, w, 0.0, yc - ch, [(c - aw / 2, c + aw / 2, 0.0, sp, aw / 2)], "rustic")
    m.box(-0.2, w + 0.2, yc - ch, yc - ch + 0.25, -0.05, 0.3, "marble", skip=("back",))
    m.pop()
    for e in (cx - w / 2, cx + w / 2):  # the ends
        m.poly([(e, 0.0, zf), (e, yc - ch, zf), (e, yc - ch, zf - V["flat_t"]), (e, 0.0, zf - V["flat_t"])], "rustic")
    m.cls = "doc"
    # the hipped stone cap with its urns and the pineapple (plate 20)
    hz = V["flat_t"] / 2 + 0.6
    zc = zf - V["flat_t"] / 2
    r = cap(cx, zc, w / 2 + 0.3, hz, V["gate_ridge_l"] / 2, V["gate_cornice"], V["gate_ridge"])
    for p in r["ridge"]:
        m.lathe([(0.24, p[1]), (0.3, p[1] + 0.12), (0.16, p[1] + 0.2), (0.3, p[1] + 0.42), (0.2, V["gate_urn"] - 0.15), (0.0, V["gate_urn"])], 8, "sculpt", cx=p[0], cz=p[2])
    ridge = sorted(r["ridge"], key=lambda p: p[0])
    y = ridge[0][1]
    m.lathe([(0.25, y), (0.3, y + 0.15), (0.2, y + 0.25), (0.34, y + 0.55), (0.3, y + 0.85), (0.12, V["gate_pine"] - 0.08), (0.0, V["gate_pine"])], 10, "sculpt", cx=cx, cz=zc)
    S.kp(f"gate_{lr}_pine_top", (cx, V["gate_pine"], zc))
    S.kp(f"gate_{lr}_urn_l_top", (ridge[0][0], V["gate_urn"], ridge[0][2]))
    S.kp(f"gate_{lr}_urn_r_top", (ridge[1][0], V["gate_urn"], ridge[1][2]))
    S.kp(f"gate_{lr}_ridge_l", ridge[0])
    S.kp(f"gate_{lr}_ridge_r", ridge[1])


def cap(cx, zc, hx, hz, rl, y0, y1):
    """The gates' hipped stone cap (plate 20): a trapezoid front and back from the cornice's length to a short ridge, steep triangular ends; a sunk panel in the front
    slope, as the plate draws it. Its ridge half-length rl is the plate's, not the box's (a hip roof of the flat's depth would carry a ridge 6 m long)."""
    E = [(cx - hx, y0, zc - hz), (cx + hx, y0, zc - hz), (cx + hx, y0, zc + hz), (cx - hx, y0, zc + hz)]
    R = [(cx - rl, y1, zc), (cx + rl, y1, zc)]
    m.poly([E[3], E[2], R[1], R[0]], "roof")
    m.poly([E[1], E[0], R[0], R[1]], "roof")
    m.poly([E[0], E[3], R[0]], "roof")
    m.poly([E[2], E[1], R[1]], "roof")
    m.flat([(p[0], p[2]) for p in E], y0, "roof")
    m.box(cx - rl - 0.15, cx + rl + 0.15, y1 - 0.05, y1 + 0.12, zc - 0.15, zc + 0.15, "ridge")
    # the sunk panel on the front slope: a triangle-and-band of mouldings (plate 20 draws the front slope framed)
    k = 0.2
    pa = [(E[3][0] * (1 - k) + R[0][0] * k + 0.5, E[3][1] * (1 - k) + R[0][1] * k, E[3][2] * (1 - k) + R[0][2] * k + 0.04),
          (E[2][0] * (1 - k) + R[1][0] * k - 0.5, E[2][1] * (1 - k) + R[1][1] * k, E[2][2] * (1 - k) + R[1][2] * k + 0.04),
          (R[1][0] - 0.2, y1 - 0.25, zc + 0.12), (R[0][0] + 0.2, y1 - 0.25, zc + 0.12)]
    m.poly(pa, "panel")
    return {"ridge": [(R[0][0], y1 + 0.12, zc), (R[1][0], y1 + 0.12, zc)]}


def _w(p):
    q = m.world(p)
    return (float(q[0]), float(q[1]), float(q[2]))


# ------------------------------------------------------------------ the flats: cut-outs of the painted houses
def flat(cx, zf, side, k):
    """A flat 7.3 m wide whose west face is at zf: its top falls towards the axis (eave()), stepped where one painted house meets the next, the houses' roofs, windows and
    doors in low relief; the bracing behind. All assumed (C): the painted scenes are lost."""
    w, t = V["flat_w"], V["flat_t"]
    xs = [cx - w / 2, cx + w / 2]
    o_in, o_out = min(abs(x) for x in xs), max(abs(x) for x in xs)
    left_is_outer = abs(xs[0]) > abs(xs[1])
    m.cls = "fill"
    # two houses a flat, the outer one taller (a street's eaves), each with a gable or a hipped roof drawn in profile
    n_h = 2
    hw_ = w / n_h
    for j in range(n_h):
        s0, s1 = xs[0] + j * hw_, xs[0] + (j + 1) * hw_
        o0, o1 = abs(s0), abs(s1)
        e0, e1 = eave(o0), eave(o1)
        roof_h = 1.1 + 0.25 * ((k + j) % 2)
        top = [(s0, e0), (s1, e1)]
        # the wall of the house, cut to its eaves, its roof in profile above (a gable on every other house)
        m.poly([(s0, 0.0, zf), (s1, 0.0, zf), (s1, e1, zf), (s0, e0, zf)], "scene")
        if (k + j) % 2 == 0:
            mid = ((s0 + s1) / 2, (e0 + e1) / 2 + roof_h)
            m.poly([(s0, e0, zf), (s1, e1, zf), (mid[0], mid[1], zf)], "scene_roof")
            m.poly([(mid[0], mid[1], zf - t), (s1, e1, zf - t), (s0, e0, zf - t)], "panel")
            outline = [(s0, e0), (mid[0], mid[1]), (s1, e1)]
        else:
            r0, r1 = (s0 + 0.5, e0 + roof_h * 0.8), (s1 - 0.5, e1 + roof_h * 0.8)
            m.poly([(s0, e0, zf), (s1, e1, zf), (r1[0], r1[1], zf), (r0[0], r0[1], zf)], "scene_roof")
            m.poly([(r0[0], r0[1], zf - t), (r1[0], r1[1], zf - t), (s1, e1, zf - t), (s0, e0, zf - t)], "panel")
            outline = [(s0, e0), r0, r1, (s1, e1)]
            # a dormer and a chimney, as plate 20's roofs have them
            cxr = (s0 + s1) / 2
            ye = (e0 + e1) / 2 + roof_h * 0.8
            m.box(cxr - 0.25, cxr + 0.25, ye - 0.1, ye + 0.6, zf - 0.1, zf + 0.12, "scene_roof", skip=("back",))
        # the top edge's thickness
        for (a0, b0), (a1, b1) in zip(outline[:-1], outline[1:]):
            m.poly([(a0, b0, zf), (a1, b1, zf), (a1, b1, zf - t), (a0, b0, zf - t)], "panel")
        # windows in rows under the eaves, a door at the foot (relief)
        floors = max(1, int((min(e0, e1) - 0.6) / 2.6))
        nwin = 3
        for f in range(floors):
            yb = 0.9 + f * 2.6 if f else 0.9
            for q in range(nwin):
                s = s0 + (q + 0.5) * hw_ / nwin
                if f == 0 and q == 1:
                    m.box(s - 0.45, s + 0.45, 0.0, 2.3, zf, zf + 0.05, "door", skip=("back",))
                    m.box(s - 0.55, s + 0.55, 2.3, 2.42, zf, zf + 0.09, "marble", skip=("back",))
                    continue
                if yb + 1.5 > min(e0, e1) - 0.3:
                    continue
                m.box(s - 0.32, s + 0.32, yb, yb + 1.4, zf, zf + 0.04, "glass_win", skip=("back",))
                m.box(s - 0.4, s + 0.4, yb - 0.1, yb, zf, zf + 0.1, "marble", skip=("back",))
                m.box(s - 0.4, s + 0.4, yb + 1.4, yb + 1.5, zf, zf + 0.1, "marble", skip=("back",))
                m.box(s - 0.025, s + 0.025, yb, yb + 1.4, zf + 0.04, zf + 0.07, "marble", skip=("back",))
        m.poly([(s0, 0.0, zf - t), (s0, e0, zf - t), (s1, e1, zf - t), (s1, 0.0, zf - t)], "panel")
    # the ends and the bracing: two raking posts behind
    for x in xs:
        o = abs(x)
        m.poly([(x, 0.0, zf), (x, eave(o), zf), (x, eave(o), zf - t), (x, 0.0, zf - t)], "panel")
    for x in (xs[0] + 1.2, xs[1] - 1.2):
        h = eave(abs(x)) - 0.4
        m.poly([(x - 0.1, h, zf - t), (x + 0.1, h, zf - t), (x + 0.1, 0.0, zf - t - 1.3), (x - 0.1, 0.0, zf - t - 1.3)], "timber")
    S.FOOTPRINTS.append(rect(xs[0], xs[1], zf - t - 1.35, zf))
    for x in xs:
        S.JOINTS.append([f"flat_{side}{k}_{'in' if abs(x) == o_in else 'out'}", x, S.gy(x, zf) - 0.05, zf, "wall foot"])
    S.kp(f"flat_{side}{k}_top_in", (xs[1] if left_is_outer else xs[0], eave(o_in), zf))
    S.kp(f"flat_{side}{k}_top_out", (xs[0] if left_is_outer else xs[1], eave(o_out), zf))
    m.cls = "doc"


def back_wall(cx, zf, w):
    """The back wall: painted (S02), its top cut to a range of hills (plate 20 paints hills behind the town); assumed."""
    t = V["flat_t"]
    m.cls = "fill"
    n = 16
    xs = [cx - w / 2 + w * i / n for i in range(n + 1)]
    hs = [V["back_h"] + 1.6 * max(0.0, math.sin(math.pi * i / n * 2.0 + 0.4)) * (0.6 + 0.4 * math.cos(i * 1.7)) for i in range(n + 1)]
    for (x0, h0), (x1, h1) in zip(zip(xs[:-1], hs[:-1]), zip(xs[1:], hs[1:])):
        m.poly([(x0, 0.0, zf), (x1, 0.0, zf), (x1, V["back_h"] - 1.5, zf), (x0, V["back_h"] - 1.5, zf)], "scene")
        m.poly([(x0, V["back_h"] - 1.5, zf), (x1, V["back_h"] - 1.5, zf), (x1, h1, zf), (x0, h0, zf)], "hill")
        m.poly([(x0, h0, zf), (x1, h1, zf), (x1, h1, zf - t), (x0, h0, zf - t)], "panel")
        m.poly([(x1, 0.0, zf - t), (x0, 0.0, zf - t), (x0, h0, zf - t), (x1, h1, zf - t)], "panel")
    for x in (xs[0], xs[-1]):
        h = hs[0] if x == xs[0] else hs[-1]
        m.poly([(x, 0.0, zf), (x, h, zf), (x, h, zf - t), (x, 0.0, zf - t)], "panel")
    for x in (cx - w / 2 + 1.5, cx, cx + w / 2 - 1.5):
        m.poly([(x - 0.1, V["back_h"] - 0.5, zf - t), (x + 0.1, V["back_h"] - 0.5, zf - t), (x + 0.1, 0.0, zf - t - 1.3), (x - 0.1, 0.0, zf - t - 1.3)], "timber")
    S.FOOTPRINTS.append(rect(cx - w / 2, cx + w / 2, zf - t - 1.35, zf))
    S.JOINTS.append(["back_N", cx - w / 2, S.gy(cx - w / 2, zf) - 0.05, zf, "wall foot"])
    S.JOINTS.append(["back_S", cx + w / 2, S.gy(cx + w / 2, zf) - 0.05, zf, "wall foot"])
    S.kp("back_top_C", (cx, V["back_h"], zf))
    m.cls = "doc"


# ------------------------------------------------------------------ the landing to 方河 on the axis
def landing():
    """Five steps with rounded ends down from the stage to the water on the axis (plate 20); the bank found on the walk surface of Round 10."""
    G = S.G
    z_bank, lvl = None, None
    for i in range(0, 400):
        z = 25.0 + i * 0.1
        sx, _, sz = S.to_scene((0.0, 0.0, z))
        if G.land(sx, sz) is None:  # the first point the walk surface calls water
            lv = G.level(sx, sz)
            z_bank, lvl = z - 0.4, (lv if lv is not None else G.at(sx, sz)) - S.pos[1]
            break
    if z_bank is None:
        return None
    top = S.gy(0.0, z_bank - 0.6)
    n = V["steps_n"]
    rise = max((top - lvl + 0.3) / n, 0.12)
    tread = 0.4
    hw = V["steps_w"] / 2
    m.cls = "doc"
    bed = S.gy(0.0, z_bank + n * tread + 0.5)
    for k in range(n):
        y = top - (k + 1) * rise + 0.02
        z0, z1 = z_bank - 0.6 + k * tread, z_bank - 0.6 + (k + 1) * tread
        w_ = hw + 0.15 * (k + 1)
        outline = [(-w_, z0)] + [(-w_ - 0.6 * math.sin(math.pi * j / 6) * 0.0 - 0.4 * math.sin(math.pi * j / 6), z0 + (z1 - z0) * j / 6) for j in range(1, 6)] + [(-w_, z1), (w_, z1)] + \
                  [(w_ + 0.4 * math.sin(math.pi * j / 6), z1 - (z1 - z0) * j / 6) for j in range(1, 6)] + [(w_, z0)]
        m.prism(outline, min(bed, y) - 0.2, y + rise, "step")
    m.flat(rect(-hw - 0.4, hw + 0.4, z_bank - 1.6, z_bank - 0.6), top + 0.02, "pave")
    S.FOOTPRINTS.append(rect(-hw - 1.0, hw + 1.0, z_bank - 0.6, z_bank - 0.6 + n * tread))
    S.kp("steps_top_l", (-hw - 0.15, top + 0.02, z_bank - 0.6), anchor=True)
    S.kp("steps_top_r", (hw + 0.15, top + 0.02, z_bank - 0.6), anchor=True)
    yb = top - n * rise + 0.02
    S.kp("steps_foot_l", (-hw - 0.15 * n, yb + rise, z_bank - 0.6 + n * tread))
    S.kp("steps_foot_r", (hw + 0.15 * n, yb + rise, z_bank - 0.6 + n * tread))
    S.JOINTS.append(["steps_head", 0.0, S.gy(0.0, z_bank - 1.0) - 0.05, z_bank - 1.0, "stair head"])
    S.entry("landing", 0.0, z_bank - 1.4)
    return {"z_bank": round(z_bank, 2), "water": round(lvl, 2), "top": round(top, 2), "rise": round(rise, 3)}


def build():
    global S, m, P_
    S = Site("XY15-M69")
    m = Mesh(COL)
    S.m = m
    P_ = Parts(m, rail_h=1.0, baluster_segs=6)
    m.cls = "doc"
    for bid, side, k in screens():
        x, z, hf, hd, base = S.box_local(bid)
        zf = z + hd
        if k == 1:
            gate(x, zf, "L" if side == "N" else "R")
            S.FOOTPRINTS.append(rect(x - V["flat_w"] / 2 - 0.9, x + V["flat_w"] / 2 + 0.9, zf - V["flat_t"] - 0.1, zf + 0.35))
            for e in (x - V["flat_w"] / 2, x + V["flat_w"] / 2):
                S.JOINTS.append([f"gate_{side}_{'N' if e < x else 'S'}", e, S.gy(e, zf) - 0.05, zf, "wall foot"])
            S.footing(rect(x - V["flat_w"] / 2, x + V["flat_w"] / 2, zf - V["flat_t"], zf), 0.0, "rustic", lid=False, fp=False)
        else:
            flat(x, zf, side, k)
            S.footing(rect(x - V["flat_w"] / 2, x + V["flat_w"] / 2, zf - V["flat_t"], zf), 0.0, "panel", lid=False, fp=False)
    x, z, hf, hd, base = S.box_local("XY15-M69")
    back_wall(x, z + hd, 2 * hf)
    S.footing(rect(x - hf, x + hf, z + hd - V["flat_t"], z + hd), 0.0, "panel", lid=False, fp=False)
    S.REPORT = {"landing": landing()}
    S.entry("stage", 0.0, 20.0)


def summary(tris, fill, size):
    rows = [
        ["Gates", f"the first pair of flats, nearest the water, as plate 20 draws them: rusticated piers, an arch {V['gate_arch_w']:g} m wide to {V['gate_arch_top']:g} m with radiating voussoirs, corbels under the cornice at {V['gate_cornice']:g} m, a hipped cap to {V['gate_ridge']:g} m with urns and a pineapple ({V['gate_pine']:g} m), a lion on a ball at each side (read at the plan's {V['flat_w']:g} m, C)"],
        ["Flats", f"five more pairs of flats {V['flat_w']:g} m wide on S01's places, narrowing towards the back wall; cut to the outline of painted houses whose eaves fall towards the axis (from {eave(23.2):.1f} m to {V['flat_min']:g} m), their roofs, windows and doors in low relief: assumed, the paintings are lost (S02: 'partly modeled and partly painted', C)"],
        ["Back wall", f"{V['back_h']:g} m with a range of hills on it (S02: a back wall, painted; its height and outline assumed, C)"],
        ["Landing", f"{V['steps_n']} steps {V['steps_w']:g} m wide with rounded ends from the stage down to 方河 on the axis (plate 20, C)"],
        ["Assumed", "the flats' and the back wall's outlines and relief, every back with its bracing (C, the pale tint with conf=1); the two ranges at the ends are the kit's"],
    ]
    return {
        "id": "XY15", "aliases": [], "name": "线法墙 Xianfa Qiang", "glb": "model.glb", "position": S.pos, "rotationY": S.rot,
        "line": "Modelled from plate 20 of 1783-86 and the plan's six flats a side; the two gates are the plate's, every flat's outline and relief is assumed, because the painted scenes are lost (C).",
        "rows": rows,
        "caption": {"frontage_m": 2 * 24.4 + V["flat_w"], "depth_m": 33.5, "eave_m": V["gate_cornice"], "ridge_m": V["gate_pine"], "assumed": True, "confidence": "C"},
        "hides": [],
        "tris": tris, "fill_tris": fill, "glb_bytes": size,
    }


def main():
    build()
    size = m.write_glb(HERE / "model.glb", "XY15 线法墙 Xianfa Qiang", extras={"id": "XY15"})
    tris = m.count()
    prims = {k: len(v["idx"]) // 3 for k, v in sorted(m.prims.items())}
    fill = sum(n for k, n in prims.items() if k.endswith("~fill"))
    S.write(HERE, "XY15", ["XY15"], P, "x south along the back wall's west front (to the right seen from the west), y up from the ground at the back wall's box, z west (out of the front, towards 方河); the origin at the back wall's front middle; metres", summary(tris, fill, size))
    import json
    json.dump(S.REPORT, open(HERE / "report.json", "w", encoding="utf-8"), indent=1)
    print(f"model.glb {size / 1e6:.2f} MB, {tris} triangles ({fill} fill), {len(S.KP)} key points, {len(S.JOINTS)} joints, {len(S.ENTRIES)} entries; landing {S.REPORT['landing']}")


if __name__ == "__main__":
    main()
