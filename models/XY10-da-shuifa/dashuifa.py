#!/usr/bin/env python3
"""大水法 Dashuifa (XY10), the Great Fountain, the third detailed model (Round 15): the niche with its arch head and crest, the cascade, the two great piers with their consoles
and finials, the quarter-arch buttresses ("great scrolls"), the stairs behind them up to the terrace of 远瀛观, the stepped base courses, the lobed basin with the stag and the hounds,
the two towers (XY10-N01, N02) on their carved pedestals in their own basins ringed with jets, and the court's floor (the sunken area, 1.30 m below the gardens: S603).
Plain geometry, one GLB (scripts/model_mesh.py) with every figure in params.json; the method is the pilot's (models/XY01-xieqiqu/README.md).

  uv run python models/XY10-da-shuifa/dashuifa.py

Writes, beside this file: model.glb, params.json, keypoints.json, joints.json, summary.json (models/README.md).
Frame (scripts/model_site.py): origin at the front middle of the niche's box (XY10-M47), at the court's floor; x east along the front, y up, z south (out of the front).
Grades: a form shown on plate 15, the photograph of 1873 or the ruin photographs is `doc`; what no picture shows (the piers' backs, the stairs' flights, the towers' north faces) is
`fill` (assumed, C). Every figure is C unless params.json says otherwise.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from model_mesh import Mesh  # noqa: E402
from model_parts import Parts, arc_pts  # noqa: E402
from model_site import Site, lobed, offset_aligned, resample, ring  # noqa: E402

# ---------------------------------------------------------------- figures (value, source, grade, note); the iteration log in README.md says what moved and why
P = {
    # the niche and the piers
    "span": (21.2, "S01;S71;S440", "C", "the piers' outer edges: the plan's arc x 10511-10611, 100 px at 4.71 px/m (b); plate 15 and P0641 draw the niche 0.43-0.44 of it"),
    "niche_w": (9.2, "S71;S440", "C", "the niche frame over its posts: 0.43 of the span on plate 15 (191 of 443 px), 0.44 on P0641 (225 of 512 px)"),
    "open_w": (3.7, "S71;S440", "C", "the niche opening: 0.40 of the frame on plate 15, 90 of 225 px on P0641"),
    "pier_w": (3.2, "S440", "C", "the pier's shaft across the front: P0641 76-80 px at 25 px/m; the cornice block 4.2 m (104 px)"),
    "pier_d": (4.4, "S01;S86", "C", "the pier's depth: the plan's band 4.36 m (b); P0214 and P0288 show deep piers, side faces wider than the fronts"),
    "pier_fwd": (0.8, "S01", "C", "the piers stand forward of the niche: the plan draws the band as an arc whose ends come south"),
    "foot": (1.3, "S603", "C", "the piers' and the niche's foot on the plinth course, at the gardens' level: the court is sunk 1.30 m (S603, survey, B); the courses step down from it to the basin (P0641)"),
    "pier_h": (8.6, "S440", "C", "pier foot to cornice top: P0641, 214 px at 25 px/m (the shaft's width the scale); plate 15 draws it 11.5 m at the plan's scale, its heights stretched (k about 1.3)"),
    "flare_h": (3.6, "S440", "C", "the console foot under the shaft: P0641 89-95 px"),
    "cap_h": (1.0, "S71", "C", "the pier's crowning cornice block: plate 15 25 px of 240"),
    "finial_h": (4.5, "S71", "C", "the vase finial over each pier: plate 15, 0.53 of the pier's height (126 of 240 px); gone by 1873 (P0776). The dossier's 14.3 m top is the same reading by the plate's module"),
    "post_cap": (8.7, "S440;S71", "C", "the niche posts' caps, where the head springs: level with the piers' cornice on P0641 (510 and 513 px) and on plate 15 (671 and 670)"),
    "head_rise": (3.7, "S71;S70", "C", "the arch head's rise over the post caps: 0.41 of the frame on plate 15, 0.39 on P0762 (its back)"),
    "head_in": (0.95, "S440;S83;S871", "C", "the head stands this far inside the frame's outer edge each side: the posts' caps stick out about 25 px beyond it on P0641; v1's full-width head was 0.9-1.6 m too wide on P0641, P0340, P0169 and P0776"),
    "head_d": (3.0, "S86", "C", "the head is a deep hood: its shoulder scrolls run back as drums on P0214 and P0288, 0.5-0.8 of its width (the ruin reader); 3 m, C"),
    "open_top": (9.45, "S440;S71", "C", "the opening's top on the axis, 0.75 m over the post caps: P0641 19 px, plate 15 15 px"),
    "crest_h": (4.0, "S71;S871", "C", "the shell crest over the head: plate 15 0.58 of the frame (5.3 m) at its stretched heights; whole in 1873 (P0776)"),
    "post_d": (3.0, "S86", "C", "the posts' depth: as the head"),
    "cascade_steps": (7, "S310;S71", "B", "the seven-step water curtain in the niche (S310, B); plate 15 draws about seven lips below the lion mask"),
    "mask_y": (6.6, "S71", "C", "the lion mask's mouth above the foot: plate 15 draws it 34 px below the post caps; v1's 8.0 m sat 1.8 m above the plate's fit"),
    # the stairs to the terrace of 远瀛观 (the "great scrolls" are their parapets)
    "terrace_y": (4.63, "S71;S871;S70", "C", "the 远瀛观 terrace above the court, where the stairs arrive: plate 15 draws the parapets' curl at the piers' flare (789 and 812 px), 4.3 m over the piers' foot by P0641's heights; P0776's balustrade stands over it; the ground behind the niche on P0762 at about the same level. XY09's terrace box raised to 4.3 m to meet it (Q232)"),
    "stair_w": (3.0, "S01", "C", "each flight's width: the plan's hatched blocks at the arc's ends (CCX-023, 024), about 3 m"),
    "stair_ang": (37.0, "S01", "C", "the flights' turn from the front: the hatched blocks run on the diagonal, out and forward from the arc's ends; plate 14 draws two stairs embracing 大水法"),
    "stair_run": (8.3, "S01;S71", "C", "a flight's run: 30 steps of 0.155 m on treads of 0.28 m; the plan's blocks are about 8 m on the diagonal"),
    # the basin
    "basin_w": (28.4, "S850", "B", "the lobed basin's width on the ruin (S850 view); the plan draws 29.5 m"),
    "basin_z0": (1.6, "S850;S01", "C", "its north edge before the base courses: the pool's centre 12.0 m south of the niche's box middle (ruin), less half its depth"),
    "basin_z1": (18.0, "S850;S01", "C", "its front on the axis: 16.4 m deep on the ruin (C); the plan draws 21 m"),
    "rim_h": (0.6, "S71", "C", "the rim above the court; a low rail of small posts on its front (plate 15)"),
    "water_y": (0.35, "S71", "C", "the water's surface"),
    "stag_z": (10.5, "S01", "C", "the stag's base: the plan's middle rectangle in the pool"),
    "stag_h": (2.2, "S71", "C", "the stag on its rock: plate 15 draws it 77 px from base to antler tips at the basin's depth"),
    "hounds": (10, "S01;S71", "C", "ten hounds round the stag: the plan's ten small rectangles in a ring; plate 15 shows about four a side leaping at it"),
    # the towers
    "tower_x": (31.0, "S603", "B", "the two tower basins' centres 62 m apart, symmetric about the axis (S603, survey); the ruin readings put the east basin 5.6 m further south than the west (Q234)"),
    "tower_z": (15.6, "S01;S850", "C", "their line across the axis: 17.8 m south of the niche's box middle, the mean of the two ruin readings; S01's water bodies 17.5-18.4"),
    "basin_d": (18.0, "S603", "B", "the tower basins, 18 m across, quatrefoil (S603); plate 15 draws a lobed oblong with a straight front and concave corners"),
    "ped_w": (4.6, "S01;S71", "B", "the pedestal, square: the plan 4.6 m (b), plate 15 the same"),
    "ped_h": (5.0, "S71", "C", "the pedestal's height above the water: plate 15, 0.69 of its width at its stretched heights (6.7 m), less the plate's stretch"),
    "tiers": (10, "S71", "C", "the pyramid's tiers: plate 15 draws ten (the reader, +-1); S310's '13 steps' is a search extract, the page not confirmed"),
    "pyr_h": (12.0, "S71", "C", "the pyramid with its pinnacle above the pedestal: plate 15, 2.4 times the pedestal"),
    "tier_b": (3.3, "S71", "C", "the bottom tier's width: 0.72 of the pedestal's front on plate 15"),
    "tier_t": (0.9, "S71", "C", "the top tier's width: 0.19 of the pedestal's front"),
    "jets": (40, "S71", "C", "about forty jets a tower in two rings, the tallest 1.8 times the pedestal (plate 15)"),
}
V = {k: v[0] for k, v in P.items()}

COL = {
    "rustic": "#d6cfc1", "joint": "#a39a8a", "marble": "#ebe6da", "wall": "#cbc4b6", "panel": "#c2bbab", "glaze": "#d6cfbf", "brick": "#9a7b62",
    "glass_win": "#2e4a4f", "door": "#4a3b2c", "roof": "#3f7f6c", "roofedge": "#336a5b", "ridge": "#c9a245", "water": "#6f9fb0", "jet": "#d8ecf2",
    "pave": "#c9c2b2", "pebble": "#b3a993", "step": "#d2ccbe", "sculpt": "#b8b0a2", "parterre": "#6d7748", "hedge": "#4d6a3c", "rock": "#9d978a",
}

S = None
m = None
P_ = None


def rect(x0, x1, z0, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def face(x, z, normal, y=0.0):
    """A face frame at (x, z) facing `normal`: 'S' (+z), 'N' (-z), 'E' (+x), 'W' (-x). s runs to the right as one faces it."""
    rot = {"S": 0.0, "N": math.pi, "E": math.pi / 2, "W": -math.pi / 2}[normal]
    m.push(x, y, z, rot)


# ---------------------------------------------------------------- the niche
def niche():
    f, hw, ow = V["foot"], V["niche_w"] / 2, V["open_w"] / 2
    yc = f + V["post_cap"]
    yh = yc + V["head_rise"]
    yo = f + V["open_top"]
    pd = V["post_d"]
    # the posts: plain marble blocks with sunk fields and drops, console feet, a cap moulding
    for sx in (-1, 1):
        a, b = sorted((sx * ow, sx * hw))
        m.box(a, b, f, yc, -pd, 0.0, "marble", skip=("bottom",))
        m.box(a - 0.12, b + 0.12, yc - 0.45, yc, -pd - 0.12, 0.14, "marble", skip=("bottom",))  # the cap moulding
        face((a + b) / 2, 0.0, "S")
        w = b - a
        m.box(-w / 2 + 0.35, w / 2 - 0.35, f + V["flare_h"] + 0.4, yc - 0.9, 0.0, 0.05, "panel", skip=("back",))
        m.box(-0.18, 0.18, yc - 3.2, yc - 1.0, 0.05, 0.2, "marble", skip=("back",))  # the drop
        m.pop()
        # the console feet of the posts (P0641): a flared block across the front
        m.frustum([(a - 0.25, 0.35), (b + 0.25, 0.35), (b + 0.25, -pd), (a - 0.25, -pd)], [(a, 0.0), (b, 0.0), (b, -pd), (a, -pd)], f, f + V["flare_h"] * 0.6, "marble")
        # the post's back (P0762, the north view)
        face((a + b) / 2, -pd, "N")
        m.box(-w / 2 + 0.35, w / 2 - 0.35, f + 1.0, yc - 0.9, 0.0, 0.05, "panel", skip=("back",))
        m.pop()
    S.kp("niche_post_cap_W", (-hw - 0.12, yc, 0.14))
    S.kp("niche_post_cap_E", (hw + 0.12, yc, 0.14))
    S.kp("niche_open_top", (0.0, yo, 0.0))
    # the head: a deep hood, its front and back a segmental arch over the frame, scrolls at the shoulders (drums running back), an inner lintel band over the opening
    hd = V["head_d"]
    hh = hw - V["head_in"]  # the head is narrower than the posts' caps (P0641, P0340, P0169, P0776: the caps stand about 1 m out beyond it)
    outer = arc_pts(-hh, hh, yc, V["head_rise"], 12)
    inner_top = yo
    for z, sgn in ((0.0, 1), (-hd, -1)):
        for p0, p1 in zip(outer[:-1], outer[1:]):
            m.poly([(p0[0], yc, z), (p1[0], yc, z), (p1[0], p1[1], z), (p0[0], p0[1], z)], "marble")
    for p0, p1 in zip(outer[:-1], outer[1:]):
        m.poly([(p0[0], p0[1], 0.0), (p1[0], p1[1], 0.0), (p1[0], p1[1], -hd), (p0[0], p0[1], -hd)], "marble")
    m.box(-hh, hh, yc - 0.01, yc + 0.02, -hd, 0.0, "marble", skip=("bottom",))
    # the opening runs up into the head as a small light on the axis (P0641, P0762)
    m.box(-ow * 0.55, ow * 0.55, yc, inner_top, -0.02, 0.03, "door", skip=("back",))
    # the hood's front relief: a raised band following the arch, a cartouche on the axis
    for z in (0.18, -hd - 0.18):  # the moulded band along the arch, front and back (P0762 shows the back carved)
        bo = arc_pts(-hh + 0.25, hh - 0.25, yc, V["head_rise"] - 0.25, 12)
        bi = arc_pts(-hh + 0.75, hh - 0.75, yc, V["head_rise"] - 0.75, 12)
        for (a0, b0), (a1, b1) in zip(zip(bo[:-1], bi[:-1]), zip(bo[1:], bi[1:])):
            m.poly([(a0[0], a0[1], z), (a1[0], a1[1], z), (b1[0], b1[1], z), (b0[0], b0[1], z)], "marble")
            zz = 0.0 if z > 0 else -hd
            m.poly([(a0[0], a0[1], z), (a1[0], a1[1], z), (a1[0], a1[1], zz), (a0[0], a0[1], zz)], "marble")
    face(0.0, 0.0, "S")
    P_.cartouche(0.0, yc + V["head_rise"] * 0.55, 2.0, 1.6)
    m.pop()
    for sx in (-1, 1):
        # the shoulder scrolls: drums along the head's depth (P0214, P0288), the head's outermost points
        cx, cy, r = sx * (hh - 0.65), yc + 0.85, 0.8
        ringp = [(cx + r * math.cos(2 * math.pi * k / 10), cy + r * math.sin(2 * math.pi * k / 10)) for k in range(10)]
        for i in range(10):
            a, b = ringp[i], ringp[(i + 1) % 10]
            m.poly([(a[0], a[1], 0.2), (b[0], b[1], 0.2), (b[0], b[1], -hd + 0.2), (a[0], a[1], -hd + 0.2)], "marble")
        m.poly([(p[0], p[1], 0.2) for p in ringp], "marble")
        m.poly([(p[0], p[1], -hd + 0.2) for p in ringp], "marble")
        S.kp(f"niche_head_{'E' if sx > 0 else 'W'}", (sx * (hh - 0.65 + r), cy, 0.2))
    S.kp("niche_head_top", (0.0, yh, 0.0))
    # the same points on the back face, for P0762 (the niche seen from the 远瀛观 terrace)
    S.kp("niche_head_top_N", (0.0, yh, -hd))
    for sx, t in ((-1, "W"), (1, "E")):
        S.kp(f"niche_head_{t}_N", (sx * (hw - V["head_in"] + 0.15), yc + 0.85, -hd + 0.2))
        S.kp(f"niche_post_cap_{t}_N", (sx * (hw + 0.12), yc, -pd - 0.12))
        S.kp(f"niche_open_foot_{t}_N", (sx * ow, V["terrace_y"] + 0.25, -pd))
    S.kp("niche_open_top_N", (0.0, yo, -pd))
    # the crest: a scalloped shell on a cartouche (plate 15, P0776); a fan of ribs
    yct = yh + V["crest_h"]
    m.box(-0.9, 0.9, yh - 0.3, yh + 0.9, -0.5, 0.3, "marble")
    fan = 9
    for k in range(fan):
        t0, t1 = math.pi * k / fan, math.pi * (k + 1) / fan
        r0 = 2.3 if k % 2 == 0 else 2.0
        cy0 = yh + 0.9
        m.poly([(0.0, cy0, 0.4), (r0 * math.cos(t0), cy0 + (yct - cy0) * 0.92 * math.sin(t0), 0.4), (r0 * math.cos(t1), cy0 + (yct - cy0) * 0.92 * math.sin(t1), 0.4)], "marble")
        m.poly([(0.0, cy0, -0.5), (r0 * math.cos(t0), cy0 + (yct - cy0) * 0.92 * math.sin(t0), -0.5), (r0 * math.cos(t1), cy0 + (yct - cy0) * 0.92 * math.sin(t1), -0.5)], "marble")
        m.poly([(r0 * math.cos(t0), cy0 + (yct - cy0) * 0.92 * math.sin(t0), 0.4), (r0 * math.cos(t1), cy0 + (yct - cy0) * 0.92 * math.sin(t1), 0.4),
                (r0 * math.cos(t1), cy0 + (yct - cy0) * 0.92 * math.sin(t1), -0.5), (r0 * math.cos(t0), cy0 + (yct - cy0) * 0.92 * math.sin(t0), -0.5)], "marble")
    m.lathe([(0.35, yct - 0.4), (0.3, yct - 0.15), (0.0, yct)], 6, "marble", cx=0.0, cz=-0.05, cap=False)
    S.kp("niche_crest_top", (0.0, yct, -0.05))
    # the recess: its sill at the terrace's level behind (plate 15's sill band at the piers' flare; P0762 the back sill on the terrace); below it the console band runs on
    # across the opening, the cascade's sheet falling over it (today the infill is gone and the opening runs down to the plinth, P0641)
    ys = V["terrace_y"] + 0.25
    m.box(-ow, ow, f, ys, -pd, 0.0, "marble", skip=("bottom",))
    face(0.0, 0.0, "S")
    P_.cartouche(0.0, (f + ys) / 2, 1.8, (ys - f) * 0.5)
    m.pop()
    m.box(-ow, ow, ys, yo, -pd - 0.2, -pd, "wall")  # the recess's back, rendered (its face on the terrace side brick, P0169)
    face(0.0, -pd, "N")
    m.box(-ow, ow, ys, yo, 0.0, 0.02, "brick", skip=("back",))
    m.pop()
    my = f + V["mask_y"]
    m.box(-0.55, 0.55, my - 0.2, my + 0.9, -pd + 0.02, -pd + 0.45, "sculpt")  # the lion mask
    S.kp("cascade_top", (0.0, my, -pd + 0.45))
    n = int(V["cascade_steps"])
    for k in range(n):
        y1 = my - 0.3 - (my - 0.3 - ys) * k / n
        y0 = my - 0.3 - (my - 0.3 - ys) * (k + 1) / n
        z0, z1 = -pd + 0.45 + (pd - 0.45) * k / n, -pd + 0.45 + (pd - 0.45) * (k + 1) / n
        w = ow * (0.45 + 0.5 * (k + 1) / n)
        m.box(-w, w, ys, y0, z0, z1, "marble", skip=("bottom",))
        m.poly([(-w * 0.9, y0 + 0.02, z1 + 0.02), (w * 0.9, y0 + 0.02, z1 + 0.02), (w * 0.9, y1, z0 + 0.02), (-w * 0.9, y1, z0 + 0.02)], "water")
    S.kp("niche_open_foot_W", (-ow, ys, 0.0))
    S.kp("niche_open_foot_E", (ow, ys, 0.0))
    S.FOOTPRINTS.append(rect(-hw, hw, -pd - 0.2, 0.3))


# ---------------------------------------------------------------- the piers, the buttresses, the stairs
def piers():
    f = V["foot"]
    hs = V["span"] / 2
    pw, pdp = V["pier_w"], V["pier_d"]
    zf = V["pier_fwd"]
    yt = f + V["pier_h"]
    for sx, tag in ((-1, "W"), (1, "E")):
        xo = sx * (hs - 0.5)  # the shaft's outer face; the cornice overhangs 0.5 m to the span
        xi = xo - sx * pw
        a, b = sorted((xi, xo))
        z0, z1 = zf - pdp, zf
        # the console foot: a flared block, and the shaft
        m.frustum([(a - 0.55, z1 + 0.55), (b + 0.55, z1 + 0.55), (b + 0.55, z0 - 0.3), (a - 0.55, z0 - 0.3)], [(a, z1), (b, z1), (b, z0), (a, z0)], f, f + V["flare_h"], "marble")
        m.box(a, b, f + V["flare_h"], yt - V["cap_h"], z0, z1, "marble", skip=("bottom",))
        # the cornice block: architrave, frieze, cornice
        m.box(a - 0.2, b + 0.2, yt - V["cap_h"], yt - V["cap_h"] + 0.3, z0 - 0.2, z1 + 0.2, "marble")
        m.box(a - 0.12, b + 0.12, yt - V["cap_h"] + 0.3, yt - 0.35, z0 - 0.12, z1 + 0.12, "wall")
        m.box(a - 0.5, b + 0.5, yt - 0.35, yt, z0 - 0.5, z1 + 0.5, "marble")
        # the front: a sunk field with a long drop; the console's lyre cartouche; the side faces the same (P0214)
        face((a + b) / 2, z1, "S")
        m.box(-pw / 2 + 0.4, pw / 2 - 0.4, f + V["flare_h"] + 0.4, yt - V["cap_h"] - 0.3, 0.0, 0.04, "panel", skip=("back",))
        m.box(-0.22, 0.22, f + V["flare_h"] + 1.5, yt - V["cap_h"] - 0.6, 0.04, 0.22, "marble", skip=("back",))
        P_.cartouche(0.0, f + V["flare_h"] * 0.5, 1.2, 1.4)
        m.pop()
        face(xo, (z0 + z1) / 2, "E" if sx > 0 else "W")
        m.box(-pdp / 2 + 0.4, pdp / 2 - 0.4, f + V["flare_h"] + 0.4, yt - V["cap_h"] - 0.3, 0.0, 0.04, "panel", skip=("back",))
        m.box(-0.22, 0.22, f + V["flare_h"] + 1.2, yt - V["cap_h"] - 1.0, 0.04, 0.2, "marble", skip=("back",))
        m.pop()
        # the finial: a vase with scrolls and a fruit pyramid (plate 15; gone by 1873)
        cx, cz = (a + b) / 2, (z0 + z1) / 2
        fh = V["finial_h"]
        m.box(cx - 0.9, cx + 0.9, yt, yt + 0.6, cz - 0.9, cz + 0.9, "marble")
        m.lathe([(0.7, yt + 0.6), (0.45, yt + 0.9), (0.95, yt + 1.7), (0.75, yt + 2.3), (0.35, yt + 2.6), (0.55, yt + 2.9), (0.6, yt + 3.6), (0.3, yt + 4.1), (0.0, yt + fh)], 8, "marble", cx=cx, cz=cz, cap=False)
        S.kp(f"pier_{tag}_finial_top", (cx, yt + fh, cz))
        S.kp(f"pier_{tag}_cap_SW", (a - 0.5, yt, z1 + 0.5))
        S.kp(f"pier_{tag}_cap_SE", (b + 0.5, yt, z1 + 0.5))
        S.kp(f"pier_{tag}_flare_S", (cx, f + V["flare_h"], z1))
        S.kp(f"pier_{tag}_foot_S", (cx, f, z1 + 0.55))
        # the vase in the gap between the niche and the pier, on the sill band (plate 15)
        gx = (sx * V["niche_w"] / 2 + xi) / 2
        m.box(gx - 0.5, gx + 0.5, f, f + 1.2, -0.6, 0.4, "marble")
        P_.urn(gx, -0.1, f + 1.2, 1.9)
        m.lathe([(0.32, f + 3.0), (0.4, f + 3.5), (0.0, f + 4.6)], 6, "hedge", cx=gx, cz=-0.1, cap=False)
        S.FOOTPRINTS.append(rect(a - 0.55, b + 0.55, z0 - 0.3, z1 + 0.55))
        stair(sx, xo, z0, z1)


def drum(cx, cy, cz, r, ax, ay, half, n=10, mat="marble"):
    """A short cylinder (a volute's curl seen as a disc), its axis along (ax, ay) in plan (unit), half-length `half`."""
    ux, uz = -ay, ax  # a horizontal direction across the axis
    ring_ = [(math.cos(2 * math.pi * k / n), math.sin(2 * math.pi * k / n)) for k in range(n)]
    pts = lambda s_: [(cx + ax * s_ + ux * r * c, cy + r * sn, cz + ay * s_ + uz * r * c) for c, sn in ring_]
    a, b = pts(-half), pts(half)
    for i in range(n):
        m.poly([a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]], mat)
    m.poly(a, mat)
    m.poly(b, mat)


def stair(sx, xo, z_back, z_front):
    """A flight from the court up to the 远瀛观 terrace beside the pier, running out and forward on the diagonal of the plan's hatched blocks (CCX-023, 024; plate 14's two
    stairs embracing 大水法). Its court-side parapet ends in the great volute at its foot and a curl at the pier, with a balustrade on top: the ribbed band of plate 15,
    whose 'ribs' are the balusters (P0776: a balustrade over the curl at the W pier)."""
    ty = V["terrace_y"]
    zt = -4.2  # the terrace's south face (XY09-M43)
    w = V["stair_w"]
    ang = math.radians(V["stair_ang"])
    dx, dz = sx * math.cos(ang), math.sin(ang)  # down the flight
    nx, nz = -dz * sx, dx * sx  # across it, towards the court (south) side
    if nz < 0:
        nx, nz = -nx, -nz
    ax_, az_ = sx * (xo * sx + 2.5), -2.6  # the flight's head (middle of its top edge)
    L = V["stair_run"]
    n = max(2, int(round(ty / 0.155)))
    # the landing against the pier and the terrace's face, reaching the flight's head
    hS = (ax_ + nx * w / 2, az_ + nz * w / 2)
    hN = (ax_ - nx * w / 2, az_ - nz * w / 2)
    land = [(xo, zt), (hN[0] + sx * 0.4, zt), hN, hS, (xo, hS[1])]
    if sx < 0:
        land = land[::-1]
    S.footing(land, ty, "step", name=f"stair_{'E' if sx > 0 else 'W'}_land", corners=False)
    m.cls = "fill"
    for k in range(n):
        t0, t1 = L * k / n, L * (k + 1) / n
        y = ty * (n - k - 1) / n + 0.02
        q = [(hS[0] + dx * t0, hS[1] + dz * t0), (hN[0] + dx * t0, hN[1] + dz * t0), (hN[0] + dx * t1, hN[1] + dz * t1), (hS[0] + dx * t1, hS[1] + dz * t1)]
        lo = min(S.gy(*c) for c in q) - 0.15
        if y > lo:
            m.prism(q, lo, y, "step")
    m.cls = "doc"
    foot = (ax_ + dx * L, az_ + dz * L)
    S.FOOTPRINTS.append([hS, hN, (hN[0] + dx * L, hN[1] + dz * L), (hS[0] + dx * L, hS[1] + dz * L)])
    # the parapets: on the court side (plate 15) and on the far side (fill); solid to the tread line, a balustrade on top
    for side, cls in ((1, "doc"), (-1, "fill")):
        m.cls = cls
        ex, ez = (hS if side > 0 else hN)
        ox, oz = nx * side * 0.25, nz * side * 0.25
        e0 = (ex + ox, ez + oz)
        e1 = (ex + ox + dx * L, ez + oz + dz * L)
        k = 8
        for j in range(k):
            pa = (e0[0] + (e1[0] - e0[0]) * j / k, e0[1] + (e1[1] - e0[1]) * j / k)
            pb = (e0[0] + (e1[0] - e0[0]) * (j + 1) / k, e0[1] + (e1[1] - e0[1]) * (j + 1) / k)
            ya, yb = ty * (1 - j / k) + 0.25, ty * (1 - (j + 1) / k) + 0.25
            for off in (-0.25, 0.25):
                qa = (pa[0] + nx * side * off, pa[1] + nz * side * off)
                qb = (pb[0] + nx * side * off, pb[1] + nz * side * off)
                ga, gb = S.gy(*qa) - 0.15, S.gy(*qb) - 0.15
                m.poly([(qa[0], ga, qa[1]), (qb[0], gb, qb[1]), (qb[0], yb, qb[1]), (qa[0], ya, qa[1])], "marble")
            q0 = (pa[0] - nx * side * 0.25, pa[1] - nz * side * 0.25)
            q1 = (pa[0] + nx * side * 0.25, pa[1] + nz * side * 0.25)
            q2 = (pb[0] + nx * side * 0.25, pb[1] + nz * side * 0.25)
            q3 = (pb[0] - nx * side * 0.25, pb[1] - nz * side * 0.25)
            m.poly([(q0[0], ya, q0[1]), (q1[0], ya, q1[1]), (q2[0], yb, q2[1]), (q3[0], yb, q3[1])], "marble")
        P_.rail([e0, (e1[0] - dx * 1.2, e1[1] - dz * 1.2)], [ty + 0.25, 0.25 + ty * 1.2 / L], posts=2.6)
        m.cls = "doc"
    # the great volute at the parapet's foot and the curl against the pier (plate 15; the volutes lying today, P0641)
    vx, vz = hS[0] + nx * 0.25 + dx * (L - 0.5), hS[1] + nz * 0.25 + dz * (L - 0.5)
    drum(vx, 0.95, vz, 0.95, nx, nz, 0.4)
    drum(vx - dx * 1.0, 0.55, vz - dz * 1.0, 0.55, nx, nz, 0.32)
    cx, cz = hS[0] + nx * 0.25 + dx * 0.4, hS[1] + nz * 0.25 + dz * 0.4
    drum(cx, ty + 0.55, cz, 0.6, nx, nz, 0.35)
    tag = "E" if sx > 0 else "W"
    S.kp(f"scroll_{tag}_top", (cx, ty + 1.15, cz))
    S.kp(f"scroll_{tag}_end", (vx + dx * 0.95, 0.4, vz + dz * 0.95))
    S.kp(f"stair_{tag}_rail_high", (hS[0] + nx * 0.25, ty + 0.25 + P_.rail_h + 0.06, hS[1] + nz * 0.25))
    S.kp(f"stair_{tag}_rail_low", (hS[0] + nx * 0.25 + dx * (L - 1.2), 0.25 + ty * 1.2 / L + P_.rail_h + 0.06, hS[1] + nz * 0.25 + dz * (L - 1.2)))
    S.joint(f"stair_{tag}_foot", foot[0], foot[1], "stair foot")
    S.joint(f"volute_{tag}_foot", vx, vz, "volute foot")
    S.entry(f"stair_{tag}_foot", foot[0] + dx * 0.6, foot[1] + dz * 0.6)
    S.entry(f"stair_{tag}_top", (xo + hN[0]) / 2, (zt + hS[1]) / 2, y=ty)


# ---------------------------------------------------------------- the base courses, the basin, the stag and the hounds
def basin_outline():
    hw, z0, z1 = V["basin_w"] / 2, V["basin_z0"], V["basin_z1"]
    d = z1 - z0
    pts = [(-0.55 * hw, z0), (-0.92 * hw, z0 + 0.05 * d), (-hw, z0 + 0.22 * d), (-0.9 * hw, z0 + 0.4 * d), (-hw * 0.97, z0 + 0.6 * d), (-0.86 * hw, z0 + 0.8 * d),
           (-0.64 * hw, z0 + 0.8 * d), (-0.5 * hw, z0 + 0.93 * d), (0.0, z1), (0.5 * hw, z0 + 0.93 * d), (0.64 * hw, z0 + 0.8 * d), (0.86 * hw, z0 + 0.8 * d),
           (hw * 0.97, z0 + 0.6 * d), (0.9 * hw, z0 + 0.4 * d), (hw, z0 + 0.22 * d), (0.92 * hw, z0 + 0.05 * d), (0.55 * hw, z0), (0.0, z0)]
    return resample(lobed(pts, 6), 96)


def base_and_basin():
    f = V["foot"]
    hs = V["span"] / 2
    # the plinth under the whole ensemble, from the terrace's face to the front, and the courses stepping down to the water (P0641: a plinth, then about four courses)
    pl = rect(-hs - 1.5, hs + 1.5, -4.2, 0.4)
    S.footing(pl, f, "rustic", name="plinth")
    S.kp("base_course_C", (0.0, f, 0.4))
    for k, (y, z) in enumerate(((f - 0.32, 0.8), (f - 0.64, 1.2), (f - 0.96, 1.6))):
        m.box(-hs + 1.0 * k, hs - 1.0 * k, 0.0, y, 0.4 + 0.4 * k, z, "rustic", skip=("bottom", "back"))
    out = basin_outline()
    rim_o = offset_aligned(out, 0.6)
    rh, wy = V["rim_h"], V["water_y"]
    # the rim: an outer face from the ground, a top band, the inner face down to the floor; the water
    S.skirt(rim_o, rh, "marble")
    ring(m, rim_o, out, rh, "marble")
    for i in range(len(out)):
        a, b = out[i], out[(i + 1) % len(out)]
        m.poly([(a[0], -0.5, a[1]), (b[0], -0.5, b[1]), (b[0], rh, b[1]), (a[0], rh, a[1])], "marble")
    m.flat(out, wy, "water")
    m.flat(out, -0.5, "pave")
    S.FOOTPRINTS.append(rim_o)
    S.kp("basin_rim_S", (0.0, rh, max(p[1] for p in rim_o)))
    S.kp("basin_rim_W", (min(p[0] for p in rim_o), rh, 0.5 * (V["basin_z0"] + V["basin_z1"])))
    S.kp("basin_rim_E", (max(p[0] for p in rim_o), rh, 0.5 * (V["basin_z0"] + V["basin_z1"])))
    S.entry("basin_front", 0.0, max(p[1] for p in rim_o) + 0.8)  # the axis way to 观水法 (CCX-022) leaves the basin here
    for i, (x, z) in enumerate(rim_o[::12]):
        S.joint(f"basin_rim_{i}", x, z, "rim foot", y=S.gy(x, z) - 0.15)
    # the low rail of small posts on the front (plate 15), on the rim's middle line, in the outline's order
    zc = V["basin_z0"] + 0.72 * (V["basin_z1"] - V["basin_z0"])
    mid = [((p[0] + q[0]) / 2, (p[1] + q[1]) / 2) for p, q in zip(out, rim_o)]
    i0 = max(range(len(mid)), key=lambda i: (mid[i][1] <= zc, -i))
    seq = mid[i0:] + mid[:i0]
    run, best = [], []
    for p in seq:
        if p[1] > zc:
            run.append(p)
        else:
            if len(run) > len(best):
                best = run
            run = []
    best = best if len(best) >= len(run) else run
    if len(best) > 3:
        P_.rail(best[::2] + [best[-1]], rh, h=0.55, posts=1.6, spacing=0.3)
    # pedestals with clipped trees in pots along the front and two urn fountains by the cascade (plate 15)
    for sx in (-1, 1):
        for (x, z) in ((sx * 9.2, V["basin_z0"] + 0.82 * (V["basin_z1"] - V["basin_z0"]) + 1.4), (sx * 13.4, V["basin_z0"] + 0.62 * (V["basin_z1"] - V["basin_z0"]))):
            g = S.gy(x, z)
            m.box(x - 0.5, x + 0.5, g - 0.15, rh + 0.6, z - 0.5, z + 0.5, "marble")
            P_.urn(x, z, rh + 0.6, 0.9)
            m.lathe([(0.25, rh + 1.4), (0.55, rh + 1.8), (0.4, rh + 2.4), (0.0, rh + 2.7)], 6, "hedge", cx=x, cz=z, cap=False)
            S.FOOTPRINTS.append(rect(x - 0.5, x + 0.5, z - 0.5, z + 0.5))
        x, z = sx * 4.6, V["basin_z0"] + 1.4
        m.lathe([(0.55, wy - 0.1), (0.5, wy + 0.5), (0.3, wy + 0.7), (0.35, wy + 1.2)], 8, "marble", cx=x, cz=z)
        P_.urn(x, z, wy + 1.2, 0.9)
        P_.jet(x, z, wy + 2.0, 1.4, 0.06)
    # the cascade's sheet falling from the niche's sill to the water
    ow = V["open_w"] / 2
    ys = V["terrace_y"] + 0.25
    m.poly([(-ow * 0.9, ys, 0.05), (ow * 0.9, ys, 0.05), (ow * 0.9, f, 0.08), (-ow * 0.9, f, 0.08)], "water")
    m.poly([(-ow * 0.9, f, 0.45), (ow * 0.9, f, 0.45), (ow * 0.7, wy, V["basin_z0"] + 0.3), (-ow * 0.7, wy, V["basin_z0"] + 0.3)], "water")
    stag_and_hounds()


def quadruped(x, z, y, L, H, facing, mat, antlers=False):
    """A plain standing or leaping animal: body, neck and head, four legs; `facing` the heading (rad, 0 = +z)."""
    m.push(x, y, z, facing)
    b = L * 0.28
    m.box(-b * 0.5, b * 0.5, H * 0.45, H * 0.72, -L * 0.35, L * 0.25, mat)  # body
    m.box(-b * 0.32, b * 0.32, H * 0.65, H * 0.95, L * 0.2, L * 0.38, mat)  # neck
    m.box(-b * 0.35, b * 0.35, H * 0.85, H * 1.0, L * 0.33, L * 0.55, mat)  # head
    for lx in (-b * 0.35, b * 0.35):
        for lz in (-L * 0.3, L * 0.18):
            m.box(lx - 0.05 * L / 1.3, lx + 0.05 * L / 1.3, 0.0, H * 0.48, lz - 0.05, lz + 0.05, mat)
    if antlers:
        for s in (-1, 1):
            m.poly([(s * 0.08, H * 1.0, L * 0.4), (s * 0.55, H * 1.45, L * 0.3), (s * 0.45, H * 1.5, L * 0.36), (s * 0.04, H * 1.02, L * 0.46)], mat)
    m.pop()


def stag_and_hounds():
    wy = V["water_y"]
    sz = V["stag_z"]
    # the stag on its rock (plate 15: frontal, between jets)
    m.lathe([(1.3, -0.5), (1.2, wy + 0.4), (0.8, wy + 1.2), (0.5, wy + 1.5)], 7, "rock", cx=0.0, cz=sz)
    sh = V["stag_h"] - 1.0
    quadruped(0.0, sz, wy + 1.5, 1.7, sh, 0.0, "sculpt", antlers=True)
    S.kp("stag_top", (0.0, wy + 1.5 + sh * 1.5, sz + 0.5))
    S.kp("stag_foot", (0.0, wy, sz + 1.25))
    for k in range(5):
        a = -0.6 + 1.2 * k / 4
        P_.jet(0.0, sz + 0.6, wy + 1.5 + sh * 0.9, 2.2, 0.05, lean=(math.sin(a) * 1.2, 1.2))
    # the hounds: the plan's ten rectangles round the stag (S01 x 10480-10645, y 1014-1072 at 4.71 px/m about the pool's middle 10560, 1045)
    plan = [(480, 250), (515, 228), (605, 232), (640, 262), (475, 295), (645, 295), (490, 325), (525, 345), (590, 345), (625, 325)]
    for i, (px, py) in enumerate(plan[: int(V["hounds"])]):
        x = (px - 560) / 9.42
        z = sz + (py - 290) / 9.42 * 0.8
        g = -0.5
        m.box(x - 0.45, x + 0.45, g, wy + 0.45, z - 0.35, z + 0.35, "rock")
        head = math.atan2(-x, sz - z)
        quadruped(x, z, wy + 0.45, 1.25, 0.75, head, "sculpt")
        P_.jet(x + math.sin(head) * 0.6, z + math.cos(head) * 0.6, wy + 1.1, 0.5, 0.04, lean=(-x * 0.55, (sz - z) * 0.55))


# ---------------------------------------------------------------- the towers in their basins
def tower_outline(cx, cz, sx):
    """The lobed basin: an oblong with a straight front, concave corners, a bulge on the side towards the axis (plate 15); 18 m across (S603)."""
    h = V["basin_d"] / 2
    c = 2.6
    pts = []
    for ux, uz in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        ox, oz = cx + ux * h, cz + uz * h
        for k in range(6):  # a concave quarter notch centred on the square's corner
            a = (math.pi / 2) * k / 5
            pts.append((ox - ux * c * math.cos(a), oz - uz * c * math.sin(a)))
    pts = sorted(pts, key=lambda p: math.atan2(p[1] - cz, p[0] - cx))
    pts = resample(pts, 64)
    out = []
    for (x, z) in pts:
        if (x - cx) * (-sx) > h * 0.9 and abs(z - cz) < h * 0.7:
            x = x + (-sx) * 1.5 * math.cos((z - cz) / (h * 0.7) * math.pi / 2)
        out.append((x, z))
    return out


def towers():
    wy = 0.15
    for sx, tag in ((-1, "W"), (1, "E")):
        cx, cz = sx * V["tower_x"], V["tower_z"]
        out = tower_outline(cx, cz, sx)
        kerb = offset_aligned(out, 0.45)
        band = offset_aligned(out, 1.7)
        S.skirt(kerb, 0.3, "marble")
        ring(m, kerb, out, 0.3, "marble")
        ring(m, band, kerb, 0.03, "pebble")
        for i in range(len(out)):
            a, b = out[i], out[(i + 1) % len(out)]
            m.poly([(a[0], -1.0, a[1]), (b[0], -1.0, b[1]), (b[0], 0.3, b[1]), (a[0], 0.3, a[1])], "marble")
        m.flat(out, wy, "water")
        m.flat(out, -1.0, "pave")
        S.FOOTPRINTS.append(kerb)
        xs, zs = [p[0] for p in kerb], [p[1] for p in kerb]
        S.kp(f"twbasin_{tag}_rim_L", (min(xs), 0.3, cz))
        S.kp(f"twbasin_{tag}_rim_R", (max(xs), 0.3, cz))
        S.kp(f"twbasin_{tag}_rim_S", (cx, 0.3, max(zs)))
        for side, ex in (("W", min(p[0] for p in band) - 0.6), ("E", max(p[0] for p in band) + 0.6)):  # the cross way between the basins (CCX-021) and the ways beyond (CCX-020, 029)
            S.entry(f"twbasin_{tag}_{side}", ex, cz)
        for i, (x, z) in enumerate(kerb[::16]):
            S.joint(f"twbasin_{tag}_kerb_{i}", x, z, "rim foot", y=S.gy(x, z) - 0.15)
        # the pedestal: plinth, sunk relief panel, base and cornice; a shell cartouche on the cornice (plate 15)
        pw = V["ped_w"] / 2
        yp = wy + V["ped_h"]
        m.box(cx - pw - 0.2, cx + pw + 0.2, -1.0, wy + 1.0, cz - pw - 0.2, cz + pw + 0.2, "marble")
        m.box(cx - pw, cx + pw, wy + 1.0, yp - 0.5, cz - pw, cz + pw, "marble", skip=("bottom",))
        m.box(cx - pw - 0.25, cx + pw + 0.25, yp - 0.5, yp, cz - pw - 0.25, cz + pw + 0.25, "marble")
        for nrm in ("S", "N", "E", "W"):
            doc = nrm == "S" or (nrm == "E" and sx < 0) or (nrm == "W" and sx > 0)
            m.cls = "doc" if doc else "fill"
            dx, dz = {"S": (0, pw), "N": (0, -pw), "E": (pw, 0), "W": (-pw, 0)}[nrm]
            face(cx + dx, cz + dz, nrm)
            P_.cartouche(0.0, wy + 1.0 + (V["ped_h"] - 1.5) / 2, 2 * pw - 1.0, V["ped_h"] - 2.4)
            m.pop()
        m.cls = "doc"
        S.kp(f"tower_{tag}_ped_top_SW", (cx - pw - 0.25, yp, cz + pw + 0.25))
        S.kp(f"tower_{tag}_ped_top_SE", (cx + pw + 0.25, yp, cz + pw + 0.25))
        S.kp(f"tower_{tag}_ped_foot_SW", (cx - pw - 0.2, wy, cz + pw + 0.2))
        S.kp(f"tower_{tag}_ped_foot_SE", (cx + pw + 0.2, wy, cz + pw + 0.2))
        # the pyramid: ten tiers, each a tapering body with a projecting cornice and lattice panels; a pinnacle with a star of jets
        n = int(V["tiers"])
        body = V["pyr_h"] - 1.6
        th = body / n
        wb, wt = V["tier_b"] / 2, V["tier_t"] / 2
        y = yp
        for k in range(n):
            w0 = wb + (wt - wb) * k / n
            w1 = wb + (wt - wb) * (k + 1) / n
            sq = lambda w: [(cx - w, cz - w), (cx + w, cz - w), (cx + w, cz + w), (cx - w, cz + w)]
            m.frustum(sq(w0), sq(w1 * 1.02), y, y + th - 0.18, "marble")
            m.prism(sq(w1 + 0.18), y + th - 0.18, y + th, "marble")
            for nrm, (dx, dz) in (("S", (0, 1)), ("E", (1, 0)), ("W", (-1, 0)), ("N", (0, -1))):
                wm = (w0 + w1) / 2
                if wm < 0.5:
                    continue
                face(cx + dx * (wm + 0.01), cz + dz * (wm + 0.01), nrm)
                m.box(-wm * 0.6, wm * 0.6, y + 0.25, y + th - 0.45, 0.0, 0.02, "panel", skip=("back",))
                m.pop()
            y += th
        m.lathe([(wt + 0.1, y), (0.45, y + 0.35), (0.2, y + 0.7), (0.38, y + 1.0), (0.12, y + 1.35), (0.0, y + 1.6)], 6, "marble", cx=cx, cz=cz, cap=False)
        S.kp(f"tower_{tag}_top", (cx, y + 1.6, cz))
        for k in range(6):
            a = 2 * math.pi * k / 6
            P_.jet(cx, cz, y + 1.5, 1.2, 0.05, n=4, lean=(math.cos(a) * 1.0, math.sin(a) * 1.0))
        # the jets: an inner ring round the pedestal and an outer ring along the kerb, on small square bases
        nj = int(V["jets"])
        ni = nj // 3
        for k in range(ni):
            a = 2 * math.pi * (k + 0.5) / ni
            x, z = cx + 4.4 * math.cos(a), cz + 4.4 * math.sin(a)
            m.box(x - 0.18, x + 0.18, wy - 0.1, wy + 0.3, z - 0.18, z + 0.18, "marble")
            P_.jet(x, z, wy + 0.3, 6.5 + 2.5 * (k % 2), 0.09, n=5)
        no = nj - ni
        for k in range(no):
            x, z = out[int(k * len(out) / no)]
            x, z = x + (cx - x) * 0.07, z + (cz - z) * 0.07
            m.box(x - 0.15, x + 0.15, wy - 0.1, wy + 0.25, z - 0.15, z + 0.15, "marble")
            P_.jet(x, z, wy + 0.25, 3.2 + 1.2 * (k % 3) / 2, 0.07, n=5)


# ---------------------------------------------------------------- the court's floor
def court():
    """The floor of the sunken area (XY10-M45, 110 x 60 m, S603), paved in bands round the basins with four parterres before the towers (plate 15), less the basins and the plinth."""
    from shapely.geometry import Polygon, box as sbox
    from shapely.ops import unary_union
    x, z, hf, hd, _ = S.box_local("XY10-M45")
    area = sbox(x - hf, z - hd, x + hf, z + hd)
    holes = unary_union([Polygon(fp).buffer(0) for fp in S.FOOTPRINTS if len(fp) >= 3])
    hs = V["span"] / 2
    holes = unary_union([holes, sbox(-hs - 1.5, -9.0, hs + 1.5, 0.4)])
    beds = []
    for sx in (-1, 1):
        for z0, z1 in ((V["tower_z"] + 8.0, V["tower_z"] + 16.5),):
            beds.append(sbox(min(sx * 3.4, sx * 19.0), z0, max(sx * 3.4, sx * 19.0), z1))
    floor = area.difference(holes)
    step = 6.0
    xs = np.arange(x - hf, x + hf, step)
    zs = np.arange(z - hd, z + hd, step)

    def lay(geom, y, mat):
        for gx in xs:
            for gz in zs:
                piece = geom.intersection(sbox(gx, gz, gx + step, gz + step))
                for q in getattr(piece, "geoms", [piece]):
                    if q.geom_type == "Polygon" and q.area > 0.01:
                        m.flat([(float(a), float(b)) for a, b in list(q.exterior.coords)[:-1]], y, mat)

    bed_u = unary_union(beds)
    lay(floor.difference(bed_u.buffer(0.6)), 0.015, "pave")
    lay(bed_u.buffer(0.6).difference(bed_u).intersection(floor), 0.025, "pebble")
    lay(bed_u.intersection(floor), 0.03, "parterre")


def build():
    global S, m, P_
    S = Site("XY10-M47")
    m = Mesh(COL)
    S.m = m
    P_ = Parts(m, rail_h=1.0, baluster_segs=4)
    m.cls = "doc"
    niche()
    piers()
    m.cls = "doc"
    base_and_basin()
    towers()
    m.cls = "doc"
    court()


def summary(tris, fill, size):
    yt = V["foot"] + V["pier_h"]
    rows = [
        ["Niche", f"the frame {V['niche_w']:g} m wide over its posts, the opening {V['open_w']:g} m, the posts' caps {V['foot'] + V['post_cap']:.1f} m above the court, the deep arch head to {V['foot'] + V['post_cap'] + V['head_rise']:.1f} m and the shell crest to {V['foot'] + V['post_cap'] + V['head_rise'] + V['crest_h']:.1f} m (plate 15, P0641, P0762, P0776, C); seven water steps in the recess under the lion mask (S310, B)"],
        ["Piers", f"two square piers {V['pier_w']:g} m across, their outer edges {V['span']:g} m apart (S01, b), console feet, cornice at {yt:.1f} m, vase finials to {yt + V['finial_h']:.1f} m (plate 15; gone by 1873, P0776); proportions from P0641 (C)"],
        ["Stairs", f"a flight beside each pier up to the terrace of 远瀛观, {V['terrace_y']:g} m above the court, on the diagonal of S01's hatched blocks (C); its court-side parapet is plate 15's ribbed band: a balustrade on top, a curl at the pier, the great volute at its foot (plate 15, P0776; the volutes lying today were re-laid in 1978-83). The treads behind the parapet are assumed"],
        ["Basin", f"lobed, {V['basin_w']:g} m wide (the ruin, S850, B), {V['basin_z1'] - V['basin_z0']:.1f} m deep (C), with a low rail on its front, potted trees on pedestals, two urn fountains; the stag on its rock and ten hounds round it in the plan's places (S01, plate 15, C)"],
        ["Towers", f"two pyramids of {int(V['tiers'])} tiers (plate 15, C; S310 says 13) on carved pedestals {V['ped_w']:g} m square (S01, B), {V['ped_h']:g} m high, their tops {V['ped_h'] + V['pyr_h'] + 0.15:.1f} m above the water; basins {V['basin_d']:g} m across, {2 * V['tower_x']:g} m apart (S603, survey, B), about {int(V['jets'])} jets each"],
        ["Court", "the sunken area 110 × 60 m, 1.30 m below the gardens (S603, survey, B): paved bands, four parterres before the towers (plate 15, C)"],
        ["Colours", "white marble (S02 p.157, B); the stag and hounds in stone grey: their material is not stated in the sources read (C)"],
    ]
    return {
        "id": "XY10", "aliases": ["XY10-N01", "XY10-N02"], "name": "大水法 Dashuifa", "glb": "model.glb", "position": S.pos, "rotationY": S.rot,
        "line": "Modelled from plate 15 of 1783-86, Ohlmer's photograph of 1873, the ruin photographs of 1902-1922 and today's (P0641 for the proportions), the plan S01 and Durand's survey (S603); every figure is a reading (C) unless the row says otherwise. Faces no picture shows (the piers' backs, the stairs' flights, the towers' north faces) are carried round from the documented parts (assumed).",
        "rows": rows,
        "caption": {"frontage_m": V["span"], "depth_m": V["pier_d"], "eave_m": round(yt, 1), "ridge_m": round(V["foot"] + V["post_cap"] + V["head_rise"] + V["crest_h"], 1), "assumed": True, "confidence": "C"},
        "hides": [],
        "tris": tris, "fill_tris": fill, "glb_bytes": size,
    }


def main():
    build()
    size = m.write_glb(HERE / "model.glb", "XY10 大水法 Dashuifa", extras={"id": "XY10"})
    tris = m.count()
    prims = {k: len(v["idx"]) // 3 for k, v in sorted(m.prims.items())}
    fill = sum(n for k, n in prims.items() if k.endswith("~fill"))
    S.write(HERE, "XY10", ["XY10", "XY10-N01", "XY10-N02"], P, "x east along the niche's front, y up from the court's floor, z south (out of the front); metres", summary(tris, fill, size))
    print(f"model.glb {size / 1e6:.2f} MB, {tris} triangles ({fill} fill), {P_.balusters} balusters, {len(S.KP)} key points, {len(S.JOINTS)} joints, {len(S.ENTRIES)} entries; position {S.pos} rotY {S.rot}")


if __name__ == "__main__":
    main()
