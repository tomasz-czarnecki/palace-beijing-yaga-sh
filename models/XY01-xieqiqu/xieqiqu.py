#!/usr/bin/env python3
"""谐奇趣 Xieqiqu (XY01), the pilot model of Round 13: the main block, the two curved colonnades, the two octagonal music pavilions 八角奏乐亭, the south stair with its terrace,
the scalloped pool 海棠形喷水池 and the north stairs and basin. Plain geometry, written as one GLB (scripts/model_mesh.py) with every figure in params.json.

  uv run python models/XY01-xieqiqu/xieqiqu.py

Writes, beside this file: model.glb, params.json (every figure with its source and grade), keypoints.json (named points for tools/plate_overlay.py, local and scene),
joints.json (where the model touches the ground and the ways, for tools/check_models.py), summary.json (what the site reads; models/README.md).
Frame: origin on the axis at the middle of the main block, at its base (the box XY01-M01's ground, data/halls_1860.geojson); x east along the south front, y up, z south (out of the front).
Grades: the primitives of a form shown on a plate or an 1873 photograph are `doc`; the west end, the rear of the colonnades and octagons, the roof's back and the like, carried round from
the documented bays, are `fill` (assumed, C). Every figure is C unless params.json says otherwise: no measured drawing of this building has been seen (Yangshi Lei 985, Q72).
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
from scene1860 import DATUM_M, to_xz  # noqa: E402

# ---------------------------------------------------------------- figures (value, source, grade, note); the iteration log in README.md says what moved and why
P = {
    "W": (27.2, "S01;S71;S70", "C", "frontage of the main block: plan S01 126 px (b), plates 1 and 2 read on that module (c)"),
    "D": (8.6, "S89;S90;S01", "C", "depth, measured on the photographs P0185-P0189 (measure.py, method d): 8.60 ± 0.42 m; plan 8.6 m, the old box 14 m"),
    "H1": (3.9, "S89;S90;S108", "C", "ground storey to the floor of the main storey, measured on P0185-P0189 (measure.py, second pass): 3.92 ± 0.18 m; also the colonnades' and the octagons' lower cornice, one level by S108 Fig. 8 (B). The plates' module gave 4.5-5.5 m"),
    "H2": (8.7, "S89;S90", "C", "top of the main storey's cornice (wing roofs), measured on P0185-P0189: 8.65 ± 0.21 m; the plates' module gave 11.2 and 8.8 m"),
    "Ht": (11.6, "S89;S90", "C", "top of the top storey's cornice, measured on P0186, P0187, P0189: 11.56 ± 0.24 m. The plates draw the top storey about 1.5 times as tall against the main storey (Q219): 16.3 and 13.9 m by their module"),
    "ridge": (14.0, "S71;S70", "C", "roof apex under the ridge cap (the ridge line 14.35 m): the roof rises 0.17 of the top storey's width on both plates (54/322 px, 90/538 px), 2.1 m, plus 0.6 m for the plates' view from below the cornice, on the photographs' storey. A full camera fit on the plates gives 15.65 ± 0.32 m, pulled up by their tall top storey (Q219); the dossier's 18.3 m was the plates' module"),
    "rail": (1.0, "S71", "C", "balustrade height: plate 2 draws 1.2 m, heavy for a rail"),
    "Wc": (11.7, "S89;S90", "C", "width of the three-bay centre block, measured on P0186, P0187, P0189: 11.71 ± 0.28 m; plates 13.8 and 14.4 m"),
    "proj": (0.4, "S71;S70", "C", "the centre block stands forward of the wings, plates 1 and 2"),
    "oct_flats": (8.7, "S01;S71", "C", "octagon across the flats: plan 8.6 m, plate 1 8.9 m, plate 2 9.0 m"),
    "oct_up": (7.4, "S89;S90", "C", "octagon, upper cornice (roof foot), measured on P0185 with the block: 7.41 ± 0.33 m; plate 1's module 9.3 m"),
    "oct_apex": (10.0, "S71;S70", "C", "octagon roof apex below the crown: plates 1-2 with every other figure at the photographs' values (measure.py --roofs): 9.99 ± 0.17 m; plate 1's module gave 12.5 m"),
    "oct_x": (30.9, "S850;S01", "B", "octagon centres from the axis: rubble 61.76 m apart (S850); the boxes stand 32.4 and 29.3 m off, made symmetric"),
    "oct_z": (23.75, "S850;S01", "C", "octagon centres south of the block's middle: the boxes 22.7 and 24.8 m"),
    "col_w": (4.0, "S01", "C", "colonnade depth: S01 draws 3.8 m (the gallery trace CCX-001), the box 4 m"),
    "col_bays": (9, "S108;S310", "B", "nine bays each, the survey's description"),
    "col_z0": (1.4, "S01", "B", "the colonnades leave the block's flanks 1.4 m south of its middle: the gallery traces CCX-001/002 on S01 (plan px y 1492 in a block drawn y 1465-1506); a quarter ellipse to the octagon, 17.3 x 18 m"),
    "terr_R": (12.4, "S71;S01", "C", "the curved terrace: its front at the pool's back (S01), its ends at the wings, where the lower flights turn outward (plate 1)"),
    "terr_h": (1.9, "S71", "C", "the terrace's level in front of the landing: 0.46 of the main floor's height on plate 1"),
    "land_w": (8.0, "S71;S89", "C", "the landing in front of the main storey's middle, half-octagonal (plate 1); its flights' outer pier at 0.45 of the half-frontage on P0186 and P0187"),
    "land_d": (3.4, "S71", "C", "its depth, plate 1"),
    "pool_w": (27.3, "S01", "C", "scalloped pool 27.3 x 13.2 m (plan, as drawn); today's bank 35.6 x 16.2 m (S850) goes round a later lining"),
    "pool_d": (13.2, "S01", "C", "as above"),
    "pool_z": (25.4, "S01", "C", "pool centre south of the block's middle, the box XY01-M06"),
    "pool_rim": (0.6, "S71", "C", "rim above the court"),
    "nst_w": (23.0, "S01", "C", "north stairs: outer width of the two hatched squares on S01"),
    "nst_d": (8.8, "S01", "C", "their depth north of the block, S01"),
    "nst_h": (1.9, "S71", "C", "the side terraces of the north stairs: plate 2's 2.4 m by its module, scaled as its main floor (5.1 to 4.1 m)"),
    "nst_foot": (2.3, "S89;S90", "C", "the lower north flights' feet, towards the axis, measured on P0189 (sure 3, in grass): 2.32 ± 0.28 m; plate 2 draws them further out (Q221)"),
    "nland_w": (8.0, "S71;S89", "C", "the north landing in front of the middle door, plate 2 and P0189"),
    "nfount_d": (4.5, "S310", "B", "north basin 4.5 m across (a search extract, method e)"),
    "nfount_z": (-27.0, "S71", "C", "north basin on the axis, the ring pavement of plate 2; it was set back on its spot in 1987 (S814, S815), not surveyed here"),
}
V = {k: v[0] for k, v in P.items()}

COL = {
    "rustic": "#d6cfc1", "joint": "#a39a8a", "marble": "#ebe6da", "wall": "#b9b2a5", "panel": "#8f8a82", "glaze": "#3f8a86",
    "glass_win": "#2e4a4f", "door": "#4a3b2c", "roof": "#c9a245", "roofedge": "#b5532d", "ridge": "#8f6b2a", "water": "#6f9fb0", "jet": "#d8ecf2",
    "pave": "#c6bfae", "step": "#d2ccbe", "lead": "#8c8a86",
}


def reset(over=None):
    """Fresh state for a build, with figures overridden (measure.py varies them); the module's globals are what the drawing functions read."""
    global m, KP, JOINTS, ENTRIES, FOOTPRINTS, FOOT, W, D, H1, H2, Ht, RIDGE, RAIL, hw, hd, hc, zS, zN, PROJ
    V.clear()
    V.update({k: v[0] for k, v in P.items()})
    V.update(over or {})
    m = Mesh(COL)
    KP, JOINTS, ENTRIES, FOOTPRINTS, FOOT = {}, [], [], [], {}  # FOOTPRINTS: polygons (x, z) the ways must go round (scripts/paths1860.py)  # KP: name -> point (local), or {"cands": [...], "pick": ...}; JOINTS [name, x, y, z, kind]; ENTRIES where a way may arrive
    W, D, H1, H2, Ht, RIDGE, RAIL = V["W"], V["D"], V["H1"], V["H2"], V["Ht"], V["ridge"], V["rail"]
    hw, hd, hc = W / 2, D / 2, V["Wc"] / 2
    zS, zN = hd, -hd
    PROJ = V["proj"]


reset()
PLINTH = 0.45
E2, E3 = 0.8, 0.65  # the main and the top storey's entablatures, by the plates' proportion to the storey


def kp(name, p, anchor=False):
    KP[name] = {"p": [round(float(c), 3) for c in p], "anchor": anchor}


# ---------------------------------------------------------------- façade helpers: drawn in a face frame (s along the face, y up, d out of the face) set with m.push
def wall_holes(s0, s1, y0, y1, holes, mat, d=0.0):
    """Wall rectangle in the plane d with holes (a0, a1, b0, b1, rise): rectangle to b1, a round head of `rise` above it (0: square)."""
    xs = sorted({s0, s1, *(h[0] for h in holes), *(h[1] for h in holes)})
    ys = sorted({y0, y1, *(h[2] for h in holes), *(min(h[3] + h[4], y1) for h in holes)})
    xs = [x for x in xs if s0 <= x <= s1]
    ys = [y for y in ys if y0 <= y <= y1]
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            cx, cy = (xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2
            if any(h[0] < cx < h[1] and h[2] < cy < h[3] + h[4] for h in holes):
                continue
            m.poly([(xs[i], ys[j], d), (xs[i + 1], ys[j], d), (xs[i + 1], ys[j + 1], d), (xs[i], ys[j + 1], d)], mat)
    for a0, a1, b0, b1, rise in holes:
        if rise > 0:
            pts = arc_pts(a0, a1, b1, rise, 8)
            mid = len(pts) // 2
            tl, tr = (a0, b1 + rise), (a1, b1 + rise)
            for p0, p1 in zip(pts[:mid], pts[1:mid + 1]):
                m.poly([(tl[0], tl[1], d), (p0[0], p0[1], d), (p1[0], p1[1], d)], mat)
            for p0, p1 in zip(pts[mid:-1], pts[mid + 1:]):
                m.poly([(tr[0], tr[1], d), (p0[0], p0[1], d), (p1[0], p1[1], d)], mat)


def arc_pts(a0, a1, y, rise, n):
    """A segmental head from (a0, y) over to (a1, y), crown y + rise."""
    half = (a1 - a0) / 2
    c = (a0 + a1) / 2
    R = (half * half + rise * rise) / (2 * rise)
    cy = y + rise - R
    t0 = math.atan2(y - cy, -half)
    t1 = math.atan2(y - cy, half)
    return [(c + R * math.cos(t0 + (t1 - t0) * k / n), cy + R * math.sin(t0 + (t1 - t0) * k / n)) for k in range(n + 1)]


def opening(a0, a1, b0, b1, rise, depth=0.32, kind="win", frame=0.16, head=None, bars=True):
    """The dressing of a hole cut by wall_holes: reveals, glass or door leaf recessed, glazing bars, a proud frame, a sill, a head."""
    pts = arc_pts(a0, a1, b1, rise, 8) if rise > 0 else [(a0, b1), (a1, b1)]
    m.poly([(a0, b0, 0), (a0, b0, -depth), (a0, b1, -depth), (a0, b1, 0)], "marble")
    m.poly([(a1, b0, -depth), (a1, b0, 0), (a1, b1, 0), (a1, b1, -depth)], "marble")
    m.poly([(a0, b0, -depth), (a0, b0, 0), (a1, b0, 0), (a1, b0, -depth)], "marble")
    for p0, p1 in zip(pts[:-1], pts[1:]):
        m.poly([(p0[0], p0[1], 0), (p0[0], p0[1], -depth), (p1[0], p1[1], -depth), (p1[0], p1[1], 0)], "marble")
    g = "glass_win" if kind == "win" else "door"
    dd = -depth + 0.06
    m.poly([(a0, b0, dd), (a1, b0, dd), (a1, b1, dd), (a0, b1, dd)], g)
    if rise > 0:
        c = ((a0 + a1) / 2, b1)
        for p0, p1 in zip(pts[:-1], pts[1:]):
            m.poly([(c[0], c[1], dd), (p1[0], p1[1], dd), (p0[0], p0[1], dd)], g)
    if bars and kind == "win":
        mid = (a0 + a1) / 2
        top = b1 + rise * 0.9
        m.box(mid - 0.035, mid + 0.035, b0, top, dd, dd + 0.05, "marble", skip=("back",))
        n = max(2, round((b1 - b0) / 0.75))
        for k in range(1, n):
            y = b0 + (b1 - b0) * k / n
            m.box(a0, a1, y - 0.03, y + 0.03, dd, dd + 0.05, "marble", skip=("back",))
    if kind == "door":
        mid = (a0 + a1) / 2
        m.box(mid - 0.03, mid + 0.03, b0, b1, dd, dd + 0.04, "marble", skip=("back",))
    if frame:
        f = frame
        m.box(a0 - f, a0, b0 - (0.12 if kind == "win" else 0), b1, 0, 0.1, "marble", skip=("back",))
        m.box(a1, a1 + f, b0 - (0.12 if kind == "win" else 0), b1, 0, 0.1, "marble", skip=("back",))
        if rise > 0:
            ring = arc_pts(a0 - f, a1 + f, b1, rise + f, 8)
            for (p0, q0), (p1, q1) in zip(zip(pts[:-1], ring[:-1]), zip(pts[1:], ring[1:])):
                m.poly([(p0[0], p0[1], 0.1), (q0[0], q0[1], 0.1), (q1[0], q1[1], 0.1), (p1[0], p1[1], 0.1)], "marble")
            km = (a0 + a1) / 2
            m.box(km - 0.13, km + 0.13, b1 + rise - 0.05, b1 + rise + f + 0.22, 0, 0.16, "marble", skip=("back",))
        else:
            m.box(a0 - f, a1 + f, b1, b1 + f, 0, 0.1, "marble", skip=("back",))
        if kind == "win":
            m.box(a0 - f - 0.08, a1 + f + 0.08, b0 - 0.2, b0 - 0.08, 0, 0.18, "marble", skip=("back",))
    if head == "cornice":
        top = b1 + rise + frame
        m.box(a0 - frame - 0.2, a1 + frame + 0.2, top, top + 0.16, 0, 0.26, "marble", skip=("back",))
        m.box((a0 + a1) / 2 - 0.35, (a0 + a1) / 2 + 0.35, top + 0.16, top + 0.62, 0.02, 0.14, "marble", skip=("back",))
        m.box((a0 + a1) / 2 - 0.2, (a0 + a1) / 2 + 0.2, top + 0.24, top + 0.5, 0.14, 0.18, "glaze", skip=("back",))
    elif head == "scroll":
        top = b1 + rise + frame
        mid = (a0 + a1) / 2
        w = (a1 - a0) / 2 + frame + 0.15
        m.poly([(mid - w, top, 0.12), (mid + w, top, 0.12), (mid, top + 0.55, 0.12)], "marble")
        m.box(mid - w, mid + w, top - 0.02, top + 0.1, 0, 0.16, "marble", skip=("back",))


def pilaster(s, y0, y1, w=0.55, out=0.22, mat="marble"):
    m.box(s - w / 2, s + w / 2, y0, y1, 0, out, mat, skip=("back",))
    m.box(s - w / 2 - 0.08, s + w / 2 + 0.08, y0, y0 + 0.35, 0, out + 0.06, mat, skip=("back",))
    m.box(s - w / 2 - 0.1, s + w / 2 + 0.1, y1 - 0.32, y1, 0, out + 0.1, mat, skip=("back",))
    # the fluting read as two shadow lines
    m.box(s - 0.1, s - 0.06, y0 + 0.45, y1 - 0.45, out, out + 0.015, "joint", skip=("back",))
    m.box(s + 0.06, s + 0.1, y0 + 0.45, y1 - 0.45, out, out + 0.015, "joint", skip=("back",))


def entablature(s0, s1, y, h=1.0, out=0.45, ends=True):
    """Architrave, frieze and cornice over a storey; y is the cornice's top."""
    skip = ("back",) if ends else ("back", "left", "right")
    m.box(s0 - 0.12, s1 + 0.12, y - h, y - h + 0.3, 0, 0.22, "marble", skip=skip)
    m.box(s0 - 0.12, s1 + 0.12, y - h + 0.3, y - 0.32, 0, 0.16, "wall", skip=skip)
    m.box(s0 - out + 0.12, s1 + out - 0.12, y - 0.32, y - 0.16, 0, out - 0.12, "marble", skip=skip)
    m.box(s0 - out, s1 + out, y - 0.16, y, 0, out, "marble", skip=skip)


def rustication(s0, s1, y0, y1, step=0.55):
    y = y0 + step
    while y < y1 - 0.15:
        m.box(s0, s1, y - 0.035, y + 0.035, 0, 0.018, "joint", skip=("back",))
        y += step


def cartouche(sc, yc, w, h):
    """A framed panel with glazed ornament: P0188's two cartouches either side of the east door, and the plates' panels."""
    m.box(sc - w / 2, sc + w / 2, yc - h / 2, yc + h / 2, 0, 0.06, "panel", skip=("back",))
    m.box(sc - w / 2 - 0.12, sc - w / 2, yc - h / 2, yc + h / 2, 0, 0.14, "marble", skip=("back",))
    m.box(sc + w / 2, sc + w / 2 + 0.12, yc - h / 2, yc + h / 2, 0, 0.14, "marble", skip=("back",))
    m.box(sc - w / 2 - 0.12, sc + w / 2 + 0.12, yc + h / 2, yc + h / 2 + 0.12, 0, 0.14, "marble", skip=("back",))
    m.box(sc - w / 2 - 0.12, sc + w / 2 + 0.12, yc - h / 2 - 0.12, yc - h / 2, 0, 0.14, "marble", skip=("back",))
    k = min(w, h) * 0.32
    m.poly([(sc, yc - k * 1.4, 0.09), (sc + k, yc, 0.09), (sc, yc + k * 1.4, 0.09), (sc - k, yc, 0.09)], "glaze")


# ---------------------------------------------------------------- balustrades and urns, in plan (x, z) at a level
BAL = {"n": 0}


def baluster(x, z, y, h):
    m.lathe([(0.075, y), (0.075, y + 0.08), (0.05, y + 0.12), (0.095, y + h * 0.42), (0.04, y + h * 0.78), (0.07, y + h * 0.84), (0.07, y + h * 0.88)], 6, "marble", cx=x, cz=z, cap=False)
    BAL["n"] += 1


def rail(pts, y, h=None, posts=3.2, ends=True, slope=None):
    """A balustrade along a polyline in plan; y the foot (a list per point for a sloping rail)."""
    h = h or RAIL
    ys = y if isinstance(y, (list, tuple)) else [y] * len(pts)
    for (a, ya), (b, yb) in zip(zip(pts[:-1], ys[:-1]), zip(pts[1:], ys[1:])):
        ax, az = a
        bx, bz = b
        L = math.hypot(bx - ax, bz - az)
        if L < 0.05:
            continue
        ux, uz = (bx - ax) / L, (bz - az) / L
        nx, nz = -uz * 0.17, ux * 0.17
        # base and top rail as slanted slabs
        for y0, y1, wd in ((0, 0.14, 1.0), (h - 0.12, h, 1.15)):
            q = [(ax + nx * wd, ya + y0, az + nz * wd), (bx + nx * wd, yb + y0, bz + nz * wd), (bx - nx * wd, yb + y0, bz - nz * wd), (ax - nx * wd, ya + y0, az - nz * wd)]
            top = [(p[0], p[1] + (y1 - y0), p[2]) for p in q]
            m.poly(top, "marble")
            m.poly([q[0], q[1], top[1], top[0]], "marble")
            m.poly([q[3], q[2], top[2], top[3]], "marble")
        n = max(1, int(L / 0.36))
        for k in range(n):
            t = (k + 0.5) / n
            x, z, yy = ax + (bx - ax) * t, az + (bz - az) * t, ya + (yb - ya) * t
            baluster(x, z, yy + 0.14, h - 0.26)
        npost = max(1, round(L / posts))
        for k in range(npost + 1) if ends else range(1, npost):
            t = k / npost
            x, z, yy = ax + (bx - ax) * t, az + (bz - az) * t, ya + (yb - ya) * t
            m.box(x - 0.2, x + 0.2, yy, yy + h + 0.06, z - 0.2, z + 0.2, "marble")


def urn(x, z, y, s=1.0):
    m.lathe([(0.2 * s, y), (0.2 * s, y + 0.1 * s), (0.08 * s, y + 0.16 * s), (0.24 * s, y + 0.42 * s), (0.18 * s, y + 0.62 * s), (0.08 * s, y + 0.7 * s), (0.11 * s, y + 0.8 * s), (0.0, y + 0.95 * s)], 8, "marble", cx=x, cz=z, cap=False)


# ---------------------------------------------------------------- the main block
def bays(s0, s1, n):
    w = (s1 - s0) / n
    return [(s0 + i * w, s0 + (i + 1) * w) for i in range(n)]


def main_block():
    # ground storey: rusticated, arched windows; the south middle hidden by the landing, the north middle by the stair landing
    wing_b = bays(hc, hw, 2)
    for side in ("S", "N", "E", "W"):
        m.cls = "fill" if side == "W" else "doc"
        if side in ("S", "N"):
            m.push(0, 0, zS if side == "S" else zN, 0 if side == "S" else math.pi)
            L = hw
        else:
            m.push(hw if side == "E" else -hw, 0, 0, math.pi / 2 if side == "E" else -math.pi / 2)
            L = hd
        # plinth course
        m.box(-L - 0.12, L + 0.12, 0, PLINTH, -0.2, 0.12, "marble", skip=("back",))
        holes = []
        if side in ("S", "N"):
            wb = (hw - hc) / 2
            centres = [(-hw + wb / 2 + wb * i) for i in range(2)] + [(-hc + hc / 3 + 2 * hc / 3 * i) for i in range(3)] + [(hc + wb / 2 + wb * i) for i in range(2)]
            centres = sorted(centres)
            for c in centres:
                if abs(c) < V["land_w"] / 2 + 0.5 and side == "S":
                    continue
                if abs(c) < V["nland_w"] / 2 + 0.3 and side == "N":
                    holes.append((c - 0.75, c + 0.75, PLINTH, H1 - 1.6, 0.75))  # the porch door under the landing (S108: a three-bay porch behind)
                    continue
                holes.append((c - 0.6, c + 0.6, 1.25, H1 - 1.55, 0.6))
        else:
            # the ends: the colonnade joins at z 0.4..4.4 (E, W); one arched window either side of it
            for c in (-2.6, 3.6) if side == "E" else (2.6, -3.6):
                pass
            holes = [(-3.6 - 0.6, -3.6 + 0.6, 1.25, H1 - 1.55, 0.6)]
        wall_holes(-L, L, PLINTH, H1 - 0.35, holes, "rustic")
        for h in holes:
            opening(h[0], h[1], h[2], h[3], h[4], kind="door" if h[2] < 1 else "win", frame=0.14)
        rustication(-L, L, PLINTH, H1 - 0.35)
        # the floor band at H1
        m.box(-L - 0.1, L + 0.1, H1 - 0.35, H1, 0, 0.25, "marble", skip=("back",))
        m.pop()
    m.cls = "doc"

    # main storey: wings (2 bays each side) and the centre block (3 bays), on the S and N fronts; the ends 3 parts (P0188: a door between two cartouches)
    for side in ("S", "N"):
        sgn = 1 if side == "S" else -1
        m.push(0, 0, zS if side == "S" else zN, 0 if side == "S" else math.pi)
        y0, y1 = H1, H2
        # wings
        for s0, s1 in ((-hw, -hc), (hc, hw)):
            holes = []
            for a, b in bays(s0, s1, 2):
                c = (a + b) / 2
                holes.append((c - 0.72, c + 0.72, y0 + 0.6, y1 - E2 - 0.85, 0))
            wall_holes(s0, s1, y0, y1 - E2, holes, "wall")
            for h in holes:
                opening(*h, kind="win", head="scroll" if side == "S" else "cornice")
            for s in (s0, (s0 + s1) / 2, s1):
                pilaster(s, y0, y1 - E2)
            entablature(s0, s1, y1, h=E2, ends=True)
        # the clustered corner pilasters
        for s in (-hw + 0.25, hw - 0.25):
            pilaster(s, y0, y1 - E2, w=0.4, out=0.3)
        # centre block, proud of the wings, rising through the top storey
        m.push(0, 0, PROJ, 0)
        m.poly([(-hc, y0, 0), (-hc, y0, -PROJ), (-hc, Ht, -PROJ), (-hc, Ht, 0)], "wall")
        m.poly([(hc, y0, -PROJ), (hc, y0, 0), (hc, Ht, 0), (hc, Ht, -PROJ)], "wall")
        holes = []
        cb = bays(-hc, hc, 3)
        for i, (a, b) in enumerate(cb):
            c = (a + b) / 2
            if side == "N":
                holes.append((c - 1.05, c + 1.05, y0 + 0.05, y1 - E2 - 0.35 - 1.05, 1.05))  # three arched openings (plate 2, P0189)
            elif i == 1:
                holes.append((c - 0.8, c + 0.8, y0 + 0.05, y1 - E2 - 0.85, 0))  # the door to the landing
            else:
                holes.append((c - 0.75, c + 0.75, y0 + 0.6, y1 - E2 - 0.85, 0))
        wall_holes(-hc, hc, y0, y1 - E2, holes, "wall")
        for i, h in enumerate(holes):
            door = side == "N" and i == 1 or side == "S" and i == 1
            opening(*h, kind="door" if door else "win", head="cornice" if side == "S" else None, frame=0.2 if side == "N" else 0.16)
        for s in (-hc + 0.35, -hc + 1.05, cb[0][1], cb[1][1], hc - 1.05, hc - 0.35):
            pilaster(s, y0, y1 - E2, w=0.5)
        entablature(-hc, hc, y1, h=E2, ends=True)
        # top storey
        y0t, y1t = y1, Ht
        holes = []
        for a, b in cb:
            c = (a + b) / 2
            holes.append((c - 0.62, c + 0.62, y0t + 0.3, y1t - E3 - 0.3, 0))
        wall_holes(-hc, hc, y0t, y1t - E3, holes, "wall")
        for h in holes:
            opening(*h, kind="win")
        for s in (-hc + 0.35, -hc + 1.05, cb[0][1], cb[1][1], hc - 1.05, hc - 0.35):
            pilaster(s, y0t, y1t - E3, w=0.5)
        entablature(-hc, hc, y1t, h=E3, ends=True)
        m.pop()
        m.pop()
        n = "S" if side == "S" else "N"
        w_, e_ = (-1, 1) if side == "S" else (-1, 1)
        zf = sgn * (hd + PROJ)
        for tag, xs in (("W", -1), ("E", 1)):
            kp(f"top_cornice_{n}{tag}", (xs * (hc + 0.45), Ht, zf + sgn * 0.45))
            kp(f"top_foot_{n}{tag}", (xs * hc, H2, zf))
            kp(f"wing_cornice_{n}{tag}", (xs * (hw + 0.45), H2, sgn * (hd + 0.45)))
            kp(f"wing_rail_{n}{tag}", (xs * (hw + 0.1), H2 + RAIL, sgn * (hd + 0.1)))
            kp(f"base_top_{n}{tag}", (xs * hw, H1, sgn * hd))
            kp(f"foot_{n}{tag}", (xs * hw, 0, sgn * hd), anchor=True)
        kp(f"topwin_{n}_head", (0, Ht - E3 - 0.3 + 0.16, zf + 0.05))
        if side == "S":
            kp("win2_S_head", (0, H2 - E2 - 0.85 + 0.16, zf + 0.05))
        else:
            kp("door2_N_head", (0, H2 - E2 - 0.35 + 0.2, zf + 0.05))

    # main storey, the two ends: 3 parts, a door between two cartouches (P0188), the colonnade's roof against the ground storey
    for side in ("E", "W"):
        m.cls = "doc" if side == "E" else "fill"
        sg = 1 if side == "E" else -1
        m.push(sg * hw, 0, 0, math.pi / 2 * sg)
        y0, y1 = H1, H2
        hole = [(-0.8, 0.8, y0 + 0.05, y1 - E2 - 0.3 - 0.8, 0.8)]
        wall_holes(-hd, hd, y0, y1 - E2, hole, "wall")
        opening(*hole[0], kind="door", frame=0.2)
        for sc in (-hd / 2 - 0.2, hd / 2 + 0.2):
            cartouche(sc, (y0 + y1 - E2) / 2 + 0.1, 1.4, (y1 - y0) * 0.5)
        for s in (-hd + 0.25, -hd + 0.85, -1.4, 1.4, hd - 0.85, hd - 0.25):
            pilaster(s, y0, y1 - E2, w=0.45)
        entablature(-hd, hd, y1, h=E2, ends=True)
        m.pop()
        kp(f"main{side}_door_head", (sg * (hw + 0.05), y1 - E2 - 0.3 + 0.2, 0))
    KP["mainE_cornice_S"] = KP["wing_cornice_SE"]
    KP["mainE_cornice_N"] = KP["wing_cornice_NE"]
    KP["mainE_rail_S"] = KP["wing_rail_SE"]
    KP["mainE_rail_N"] = KP["wing_rail_NE"]
    KP["mainE_wall_foot_S"] = KP["base_top_SE"]
    KP["mainE_wall_foot_N"] = KP["base_top_NE"]

    # top storey's ends (no picture: carried round, C)
    m.cls = "fill"
    for sg in (1, -1):
        m.push(sg * hc, 0, 0, math.pi / 2 * sg)
        dd = hd + PROJ
        holes = [(-0.62, 0.62, H2 + 0.3, Ht - E3 - 0.3, 0)]
        wall_holes(-dd, dd, H2, Ht - E3, holes, "wall")
        opening(*holes[0], kind="win")
        for s in (-dd + 0.35, -dd + 1.05, dd - 1.05, dd - 0.35):
            pilaster(s, H2, Ht - E3, w=0.5)
        entablature(-dd, dd, Ht, h=E3, ends=False)
        m.pop()
    m.cls = "doc"
    # floors and roofs: the wing roofs flat behind the balustrade, lead-grey
    m.box(-hw, -hc, H2 - 0.02, H2, -hd, hd, "lead", skip=("bottom",))
    m.box(hc, hw, H2 - 0.02, H2, -hd, hd, "lead", skip=("bottom",))
    # wing balustrades along the S, N and end edges, urns on the corners (plates 1-2: urns and a bird on each corner)
    for sx in (-1, 1):
        rail([(sx * hc, hd + 0.1), (sx * (hw + 0.1), hd + 0.1), (sx * (hw + 0.1), -hd - 0.1), (sx * hc, -hd - 0.1)], H2)
        for zz in (hd + 0.1, -hd - 0.1):
            urn(sx * (hw + 0.1), zz, H2 + RAIL + 0.06, 1.0)

    FOOTPRINTS.append([(-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd)])
    # the top roof: a hipped roof of Chinese form, yellow-ochre glazed with an orange-red edge (materials.csv, C), corners lifted
    tz = hd + PROJ
    roof_hip(hc + 0.75, tz + 0.75, Ht + 0.05, RIDGE, side_doc=("S", "N"))
    # the attic's ornaments: a crest at the middle of the ridge and scrolls at its ends (plates 1-2)


def roof_hip(hx, hz, y0, y1, side_doc=("S",), n=6):
    """Concave hip roof over a rectangle hx x hz (half sizes); ridge along x. Corners lifted 0.35 m."""
    rl = max(hx - hz, 0.4)
    rings = []
    for k in range(n + 1):
        t = k / n
        x = hx + (rl - hx) * t
        z = hz * (1 - t) + 0.02 * t
        y = y0 + (y1 - y0) * (t ** 1.45)
        lift = 0.35 * (1 - t) ** 2
        rings.append((x, z, y, lift))
    # the four slopes: S and N trapezoids, E and W triangles (as quads with a short top)
    for k in range(n):
        (x0, z0, ya, la), (x1, z1, yb, lb) = rings[k], rings[k + 1]
        mat = "roofedge" if k == 0 else "roof"
        for sz, tag in ((1, "S"), (-1, "N")):
            m.cls = "doc" if tag in side_doc else "fill"
            m.poly([(-x0, ya + la, sz * z0), (x0, ya + la, sz * z0), (x1, yb + lb, sz * z1), (-x1, yb + lb, sz * z1)], mat)
            m.poly([(-x0, ya + la, sz * z0), (-x1, yb + lb, sz * z1), (-x1, yb + lb, 0), (-x0, ya, 0)] if False else [(-x0, ya + la, sz * z0), (-x1, yb + lb, sz * z1), (-x1, yb, 0), (-x0, ya, 0)], mat)
            m.poly([(x0, ya + la, sz * z0), (x0, ya, 0), (x1, yb, 0), (x1, yb + lb, sz * z1)], mat)
    m.cls = "doc"
    # eave underside and fascia
    x0, z0, ya, la = rings[0]
    m.poly([(-x0, ya + la, z0), (x0, ya + la, z0), (x0, ya + la, -z0), (-x0, ya + la, -z0)], "ridge")
    # ridge, a crest in its middle, scrolls at its ends
    m.box(-rl - 0.2, rl + 0.2, y1 - 0.05, y1 + 0.35, -0.18, 0.18, "ridge")
    for sx in (-1, 1):
        m.box(sx * rl - 0.25, sx * rl + 0.25, y1 + 0.3, y1 + 0.95, -0.12, 0.12, "roofedge")
        m.poly([(sx * (rl + 0.25), y1 + 0.95, 0), (sx * (rl + 0.6), y1 + 1.25, 0), (sx * (rl + 0.25), y1 + 0.6, 0)], "roofedge")
    m.poly([(-0.9, y1 + 0.35, 0), (0.9, y1 + 0.35, 0), (0.6, y1 + 1.2, 0), (0, y1 + 1.6, 0), (-0.6, y1 + 1.2, 0)], "roofedge")
    kp("ridge_W", (-rl, y1 + 0.35, 0))
    kp("ridge_E", (rl, y1 + 0.35, 0))
    for tag, sx, sz in (("SW", -1, 1), ("SE", 1, 1), ("NW", -1, -1), ("NE", 1, -1)):
        kp(f"roof_eave_{tag}", (sx * x0, ya + la, sz * z0))


# ---------------------------------------------------------------- the south stair: a landing at the main floor, two flights down to a curved terrace, its ends stepping down to the court
def south_stair():
    lw, ld, R, th = V["land_w"] / 2, V["land_d"], V["terr_R"], V["terr_h"]
    # landing: half-octagon in plan against the façade, top at H1
    c = ld * 0.55
    land = [(-lw, zS), (lw, zS), (lw, zS + ld - c), (lw - c, zS + ld), (-lw + c, zS + ld), (-lw, zS + ld - c)]
    m.prism(land, 0, H1, "rustic")
    m.push(0, 0, zS + ld, 0)
    # the landing's front: a grotto niche with a figure group and a cascade (plate 1), as a dark niche and a water sheet
    m.poly([(-1.2, th + 0.2, 0.02), (1.2, th + 0.2, 0.02), (1.2, H1 - 1.4, 0.02), (-1.2, H1 - 1.4, 0.02)], "panel")
    m.box(-1.45, 1.45, H1 - 1.4, H1 - 1.1, 0, 0.18, "marble", skip=("back",))
    for sc in (-lw + c + 0.8, lw - c - 0.8):
        cartouche(sc, (th + H1) / 2, 1.0, H1 - th - 1.2)
    m.pop()
    rail([(-lw, zS + 0.2), (-lw, zS + ld - c), (-lw + c, zS + ld - 0.1), (lw - c, zS + ld - 0.1), (lw, zS + ld - c), (lw, zS + 0.2)], H1)
    for sx in (-1, 1):
        urn(sx * (lw - c), zS + ld - 0.1, H1 + RAIL + 0.06, 1.3)
    kp("stair_rail_S", (0, H1 + RAIL, zS + ld - 0.1))
    # the terrace: a half disc of radius R at th, its curved front wall over the pool's back, a rail on its edge, spouts below (plate 1)
    N = 28
    arc = [(R * math.cos(math.pi * k / N), zS + R * math.sin(math.pi * k / N)) for k in range(N + 1)]
    m.prism(arc, 0, th, "pave", side_mat="rustic")
    inner = [(x * 0.985, zS + (z - zS) * 0.985) for x, z in arc[3:N - 2]]
    rail(inner, th)
    for k in range(4, N - 3, 3):
        x, z = arc[k]
        m.box(x - 0.15, x + 0.15, th - 0.6, th - 0.3, z - 0.1, z + 0.5, "marble")
    FOOT.update({"R": R, "th": th})
    # upper flights: beside the landing, running south from the façade down to the terrace (plate 1 draws their treads beside the landing; P0187 and P0186 show the east one
    # high at the landing's corner pier, low towards the pool)
    nst = int(round((H1 - th) / 0.16))
    run = nst * 0.3
    fw = 2.2
    for sx in (-1, 1):
        x0, x1 = sorted((sx * lw, sx * (lw + fw)))
        for k in range(nst):
            za, zb = zS + run * k / nst, zS + run * (k + 1) / nst
            yk = H1 - (H1 - th) * (k + 1) / nst
            m.box(x0, x1, 0, yk, za, zb, "step", skip=("bottom",))
        xo = sx * (lw + fw + 0.1)
        rail([(xo, zS + 0.1), (xo, zS + run)], [H1, th])
        m.box(min(xo - sx * 0.25, xo + sx * 0.25), max(xo - sx * 0.25, xo + sx * 0.25), 0, H1 + RAIL + 0.1, zS, zS + 0.5, "marble")
        m.push(xo + sx * 0.26, 0, zS + run / 2, sx * math.pi / 2)
        cartouche(0, (H1 + th) / 2 - 0.4, 1.2, 1.2)
        m.pop()
    # lower flights at the terrace's two ends, running outward along the wings to the court (plate 1: the curved rail falls to the wings' corners, the feet turned outward)
    n = int(round(th / 0.15))
    run2 = n * 0.3
    z0, z1 = zS + 0.35, zS + 2.45
    for sx in (-1, 1):
        for k in range(n):
            xa, xb = sx * (R - 0.6 + run2 * k / n), sx * (R - 0.6 + run2 * (k + 1) / n)
            y = th - th * (k + 1) / n
            if y > 0.001:
                m.box(min(xa, xb), max(xa, xb), 0, y, z0, z1, "step", skip=("bottom",))
        for zr in (z0 - 0.05, z1 + 0.05):
            rail([(sx * (R - 0.6), zr), (sx * (R - 0.6 + run2), zr)], [th, 0.05])
        foot = (sx * (R - 0.6 + run2 + 0.4), 0.0, (z0 + z1) / 2)
        JOINTS.append([f"south_stair_foot_{'E' if sx > 0 else 'W'}", *foot, "stair foot"])
        ENTRIES.append([f"south_stair_foot_{'E' if sx > 0 else 'W'}", *foot])
    FOOTPRINTS.append([(-lw - 2.4, zS), (lw + 2.4, zS), (lw + 2.4, zS + 4.2), (-lw - 2.4, zS + 4.2)])
    FOOTPRINTS.append(arc)
    for sx in (-1, 1):
        x0, x1 = sorted((sx * (R - 0.6), sx * (R - 0.6 + run2)))
        FOOTPRINTS.append([(x0, z0), (x1, z0), (x1, z1), (x0, z1)])


# ---------------------------------------------------------------- the pool 海棠形: four lobes and scallops, a rim, water, the fish and the jets
def pool():
    pw, pd, pz, rim = V["pool_w"] / 2, V["pool_d"] / 2, V["pool_z"], V["pool_rim"]

    def outline(scale=1.0, n=96):
        pts = []
        for k in range(n):
            t = 2 * math.pi * k / n
            r = 1.0 + 0.07 * math.cos(4 * t) - 0.035 * abs(math.sin(10 * t))
            x, z = math.cos(t), math.sin(t)
            sq = (abs(x) ** 3 + abs(z) ** 3) ** (1 / 3)  # a rounded rectangle, the plan's form
            pts.append((pw * scale * x / sq * r, pz + pd * scale * z / sq * r))
        return pts

    outer, inner = outline(1.0), outline(0.94)
    FOOTPRINTS.append(outer)
    for i in range(len(outer)):
        a, b = outer[i], outer[(i + 1) % len(outer)]
        c, d = inner[(i + 1) % len(outer)], inner[i]
        m.poly([(a[0], -0.3, a[1]), (b[0], -0.3, b[1]), (b[0], rim, b[1]), (a[0], rim, a[1])], "marble")
        m.poly([(a[0], rim, a[1]), (b[0], rim, b[1]), (c[0], rim, c[1]), (d[0], rim, d[1])], "marble")
        m.poly([(d[0], rim, d[1]), (c[0], rim, c[1]), (c[0], rim - 0.25, c[1]), (d[0], rim - 0.25, d[1])], "marble")
    m.flat(inner, rim - 0.18, "water")
    # the fish 翻尾石鱼 (1.65 m long, S840, B) on a pedestal, its jet; pedestals with urns either side; a ring of small jets
    m.box(-0.6, 0.6, rim - 0.2, rim + 0.4, pz - 0.6, pz + 0.6, "marble")
    m.box(-0.45, 0.45, rim + 0.4, rim + 1.27, pz - 0.82, pz + 0.82, "panel")
    jet(0, pz, rim + 1.27, 5.0, 0.25)
    for sx in (-1, 1):
        x = sx * pw * 0.48
        m.box(x - 0.55, x + 0.55, rim - 0.2, rim + 1.4, pz - 0.55, pz + 0.55, "marble")
        urn(x, pz, rim + 1.4, 1.6)
        jet(x, pz, rim + 2.9, 2.5, 0.15)
    for k in range(10):
        t = math.pi * (0.1 + 0.8 * k / 9)
        x, z = pw * 0.7 * math.cos(t), pz - pd * 0.55 * math.sin(t)
        m.box(x - 0.25, x + 0.25, rim - 0.2, rim + 0.25, z - 0.35, z + 0.35, "panel")
    kp("pool_rim_W", (-pw * 1.07, rim, pz), anchor=True)
    kp("pool_rim_E", (pw * 1.07, rim, pz), anchor=True)
    kp("pool_rim_S", (0, rim, pz + pd * 1.07), anchor=True)
    kp("pool_rim_N", (0, rim, pz - pd * 1.07), anchor=True)
    for x, z, tag in ((-pw, pz, "W"), (pw, pz, "E"), (0, pz + pd, "S")):
        JOINTS.append([f"pool_rim_{tag}", x, -0.3, z, "basin foot"])


def jet(x, z, y, h, r):
    ring = [(x + r * math.cos(2 * math.pi * k / 6), z + r * math.sin(2 * math.pi * k / 6)) for k in range(6)]
    for i in range(6):
        a, b = ring[i], ring[(i + 1) % 6]
        m.poly([(a[0], y, a[1]), (b[0], y, b[1]), (x, y + h, z)], "jet")


# ---------------------------------------------------------------- the octagons 八角奏乐亭: two storeys, column clusters below, windows above, a bell-formed roof of Chinese form
def octagon(cx, cz, tag):
    a = V["oct_flats"] / 2
    R = a / math.cos(math.pi / 8)
    side = 2 * a * math.tan(math.pi / 8)
    up, apex = V["oct_up"], V["oct_apex"]
    ring = lambda r, off=0.0: [(cx + r * math.cos(math.pi / 8 + math.pi / 4 * k + off), cz + r * math.sin(math.pi / 8 + math.pi / 4 * k + off)) for k in range(8)]
    m.cls = "doc"
    m.prism(ring(R + 0.5), 0, PLINTH, "marble")
    FOOTPRINTS.append(ring(R + 0.5))
    JOINTS.append([f"oct{tag}_plinth", cx, 0.0, cz + a + 0.5, "plinth foot"])
    cands = {k: [] for k in ("foot", "low_L", "low_R", "up_L", "up_R", "door_head")}
    for k in range(8):
        th = math.pi / 4 * k  # face normal angle: k=2 is +z (south)
        n = (math.cos(th), math.sin(th))
        fc = (cx + a * n[0], cz + a * n[1])
        rot = math.atan2(n[0], n[1])
        towards_col = (tag == "W" and k == 7) or (tag == "E" and k == 5)  # the face the colonnade meets (north-east / north-west)
        visible = n[1] > -0.2  # faces turned south, east or west: the plates and P0185 show them
        m.cls = "doc" if visible else "fill"
        m.push(fc[0], 0, fc[1], rot)
        door = k == 2
        if towards_col:
            hole = [(-1.0, 1.0, PLINTH, H1 - 1.2, 0)]
            wall_holes(-side / 2, side / 2, PLINTH, H1 - 0.35, hole, "rustic")
        else:
            hole = [(-0.75, 0.75, PLINTH if door else 1.0, H1 - 1.55, 0.75)]
            wall_holes(-side / 2, side / 2, PLINTH, H1 - 0.35, hole, "rustic")
            opening(*hole[0], kind="door" if door else "win", frame=0.14)
        rustication(-side / 2, side / 2, PLINTH, H1 - 0.35)
        m.box(-side / 2 - 0.15, side / 2 + 0.15, H1 - 0.35, H1, 0, 0.3, "marble", skip=("back",))
        hole2 = [(-0.6, 0.6, H1 + 0.45, up - 1.25, 0)]
        wall_holes(-side / 2, side / 2, H1, up - 0.9, hole2, "wall")
        opening(*hole2[0], kind="win")
        m.box(-side / 2 - 0.1, side / 2 + 0.1, up - 0.9, up - 0.55, 0, 0.18, "marble", skip=("back",))
        m.box(-side / 2 - 0.25, side / 2 + 0.25, up - 0.55, up, 0, 0.4, "marble", skip=("back",))
        m.pop()
        # the column clusters at the corners of the lower storey (plate 1), pilasters above
        corner = (cx + R * math.cos(th + math.pi / 8), cz + R * math.sin(th + math.pi / 8))
        for dx in (-0.32, 0, 0.32):
            ang = th + math.pi / 8 + math.pi / 2
            px, pz = corner[0] + dx * math.cos(ang) + 0.25 * math.cos(th + math.pi / 8), corner[1] + dx * math.sin(ang) + 0.25 * math.sin(th + math.pi / 8)
            m.lathe([(0.2, PLINTH), (0.2, PLINTH + 0.3), (0.15, PLINTH + 0.4), (0.13, H1 - 0.75), (0.2, H1 - 0.55), (0.2, H1 - 0.35)], 6, "marble", cx=px, cz=pz)
        m.box(corner[0] - 0.25, corner[0] + 0.25, H1, up - 0.9, corner[1] - 0.25, corner[1] + 0.25, "marble")
        left = (-n[1], n[0])  # seen from outside, looking at the face: the viewer's left
        Lp = lambda off, y, out=0.0: (fc[0] + n[0] * out + left[0] * off, y, fc[1] + n[1] * out + left[1] * off)
        cands["foot"].append({"p": [fc[0] + n[0] * 0.5, 0.0, fc[1] + n[1] * 0.5], "n": list(n)})
        cands["low_L"].append({"p": list(Lp(side / 2 + 0.15, H1, 0.3)), "n": list(n)})
        cands["low_R"].append({"p": list(Lp(-side / 2 - 0.15, H1, 0.3)), "n": list(n)})
        cands["up_L"].append({"p": list(Lp(side / 2 + 0.25, up, 0.4)), "n": list(n)})
        cands["up_R"].append({"p": list(Lp(-side / 2 - 0.25, up, 0.4)), "n": list(n)})
        if not towards_col:
            cands["door_head"].append({"p": list(Lp(0, H1 - 1.55 + 0.75 + 0.14, 0.05)), "n": list(n)})
    m.cls = "doc"
    # floor slab at the upper storey, the inside dark behind the openings
    m.flat(ring(R - 0.3), PLINTH + 0.02, "pave")
    # the roof: a short steep skirt, then a concave pyramid to the apex; a crown and finial (plate 1)
    rr = [(R + 0.9, up + 0.05), (R + 0.2, up + 0.75), (R * 0.72, up + 1.55), (R * 0.42, up + 2.35), (R * 0.18, apex - 0.35), (0.5, apex)]
    for k in range(len(rr) - 1):
        (r0, y0), (r1, y1) = rr[k], rr[k + 1]
        lo, hi = ring(r0), ring(r1)
        mat = "roofedge" if k == 0 else "roof"
        for i in range(8):
            j = (i + 1) % 8
            facing = math.sin(math.pi / 8 + math.pi / 4 * i + math.pi / 8) > -0.2
            m.cls = "doc" if facing else "fill"
            m.poly([(lo[i][0], y0, lo[i][1]), (lo[j][0], y0, lo[j][1]), (hi[j][0], y1, hi[j][1]), (hi[i][0], y1, hi[i][1])], mat)
    m.cls = "doc"
    m.flat(ring(R + 0.9), up + 0.05, "ridge")
    m.lathe([(0.55, apex), (0.55, apex + 0.3), (0.35, apex + 0.45), (0.45, apex + 0.75), (0.2, apex + 0.95), (0.08, apex + 1.4), (0.0, apex + 1.5)], 8, "roofedge", cx=cx, cz=cz, cap=False)
    eaves = ring(R + 0.9)
    pre = f"oct{tag}_"
    for k, v in cands.items():
        KP[pre + k] = {"cands": v, "pick": "facing"}
    # the cornices' left and right ends as seen: the outline's extremes over the eight corners (the readers took the octagon's outline, plate 1 showing two or three faces)
    for k, (y, r) in {"low": (H1, R + 0.32), "up": (up, R + 0.45)}.items():
        ring_c = [{"p": [x, y, z]} for x, z in ring(r)]
        KP[pre + k + "out_L"] = {"cands": ring_c, "pick": "left"}
        KP[pre + k + "out_R"] = {"cands": ring_c, "pick": "right"}
    KP[pre + "eave_L"] = {"cands": [{"p": [x, up + 0.05, z]} for x, z in eaves], "pick": "left"}
    KP[pre + "eave_R"] = {"cands": [{"p": [x, up + 0.05, z]} for x, z in eaves], "pick": "right"}
    kp(pre + "apex", (cx, apex, cz))
    KP[pre + "foot"]["anchor"] = True
    ENTRIES.append([f"oct{tag}_door", cx, 0.0, cz + a + 0.8])  # at the foot of its plinth


# ---------------------------------------------------------------- the colonnades: a quarter circle of nine bays from the block's flank to the octagon
def colonnade(sx, tag):
    wdt, nb = V["col_w"], V["col_bays"]
    zc = V["oct_z"] - V["oct_flats"] / 2 - 0.35  # the arc ends just inside the octagon's north face
    z0 = V["col_z0"]  # it leaves the block's flank here (the trace CCX-001/002 on S01)
    ax, bz = V["oct_x"] - hw, zc - z0  # a quarter ellipse, tangent to the flank's normal at the start and to the octagon's axis at the end
    x0 = sx * hw
    pts = []
    for k in range(nb + 1):
        t = (math.pi / 2) * k / nb
        pts.append((t, x0 + sx * ax * math.sin(t), zc - bz * math.cos(t)))
    inner = lambda t, d: (x0 + sx * (ax - d) * math.sin(t), zc - (bz - d) * math.cos(t))
    for k in range(nb):
        t0, xa, za = pts[k]
        t1, xb, zb = pts[k + 1]
        L = math.hypot(xb - xa, zb - za)
        mx, mz = (xa + xb) / 2, (za + zb) / 2
        ux, uz = (xb - xa) / L, (zb - za) / L
        fx, fz = -uz * sx, ux * sx  # perpendicular, towards the ellipse's centre (the pool)
        if fx * (x0 - mx) + fz * (zc - mz) < 0:
            fx, fz = -fx, -fz
        rot = math.atan2(fx, fz)
        for face, out in (("front", 1), ("back", -1)):
            m.cls = "doc" if face == "front" else "fill"
            m.push(mx + fx * out * wdt / 2, 0, mz + fz * out * wdt / 2, rot if out > 0 else rot + math.pi)
            hl = L / 2 + 0.25
            hole = [(-0.75, 0.75, 1.2, H1 - 1.65, 0.75)]
            wall_holes(-hl, hl, PLINTH, H1 - 0.35, hole, "wall")
            opening(*hole[0], kind="win", frame=0.12)
            m.box(-hl - 0.05, hl + 0.05, 0, PLINTH, -0.15, 0.15, "marble", skip=("back",))
            for s in (-hl + 0.45, hl - 0.45):
                m.lathe([(0.2, PLINTH), (0.2, PLINTH + 0.3), (0.15, PLINTH + 0.4), (0.13, H1 - 0.85), (0.2, H1 - 0.6), (0.2, H1 - 0.45)], 6, "marble", cx=s, cz=0.25)
            m.box(-hl - 0.05, hl + 0.05, H1 - 0.45, H1, 0, 0.35, "marble", skip=("back",))
            m.pop()
        m.cls = "doc"
        m.push(mx, 0, mz, rot)
        m.box(-wdt / 2, wdt / 2, H1 - 0.12, H1, -L / 2 - 0.25, L / 2 + 0.25, "lead", skip=("bottom",))
        m.box(-wdt / 2, wdt / 2, PLINTH - 0.02, PLINTH, -L / 2 - 0.25, L / 2 + 0.25, "pave", skip=("bottom",))
        m.pop()
    FOOTPRINTS.append([inner(t, wdt / 2 + 0.2) for t, _, _ in pts] + [inner(t, -wdt / 2 - 0.2) for t, _, _ in pts[::-1]])
    front = [inner(t, wdt / 2 - 0.1) for t, _, _ in pts]
    back = [inner(t, -wdt / 2 + 0.1) for t, _, _ in pts]
    m.cls = "doc"
    rail(front, H1)
    m.cls = "fill"
    rail(back, H1)
    m.cls = "doc"
    p_in = (x0, zc - (bz - wdt / 2))
    p_out = (x0 + sx * (ax - wdt / 2), zc)
    kp(f"col{tag}_in", (p_in[0], H1, p_in[1]))
    kp(f"col{tag}_out", (p_out[0], H1, p_out[1]))
    kp(f"col{tag}_rail_in", (p_in[0], H1 + RAIL, p_in[1]))
    kp(f"col{tag}_rail_out", (p_out[0], H1 + RAIL, p_out[1]))
    for t, x, z in pts[:: max(1, nb // 3)]:
        JOINTS.append([f"col{tag}_foot_{round(math.degrees(t))}", x, 0.0, z, "colonnade foot"])


# ---------------------------------------------------------------- the north side: a landing at the main floor, flights down to two side terraces, flights from them to the court; the basin
def north_side():
    lw, nh = V["nland_w"] / 2, V["nst_h"]
    ow = V["nst_w"] / 2
    dep = V["nst_d"]
    zl = zN - 3.0  # the landing's front
    m.box(-lw, lw, 0, H1, zl, zN, "rustic", skip=("back",))
    FOOTPRINTS.append([(-lw, zl), (lw, zl), (lw, zN), (-lw, zN)])
    rail([(-lw, zl + 0.1), (lw, zl + 0.1)], H1)
    kp("nland_C", (0, H1, zl))
    # the porch door under the landing (S108: a three-bay porch behind; P0189: a door at the foot on the axis)
    m.push(0, 0, zl, math.pi)
    hole = [(-0.9, 0.9, 0.0, 3.0, 0)]
    m.poly([(-0.9, 0, 0.01), (0.9, 0, 0.01), (0.9, 3.0, 0.01), (-0.9, 3.0, 0.01)], "door")
    m.box(-1.15, 1.15, 3.0, 3.35, 0, 0.18, "marble", skip=("back",))
    for s in (-1.05, 1.05):
        m.box(s - 0.15, s + 0.15, 0, 3.0, 0, 0.14, "marble", skip=("back",))
    m.pop()
    ENTRIES.append(["north_porch_door", 0.0, 0.0, zl - 0.2])
    # plate 2 and P0189: flights from the landing outward along the façade down to two side terraces (S01's hatched squares), then lower flights running back towards the axis
    nst = int(round((H1 - nh) / 0.16))
    eb0 = ow - 2.6  # side terraces from eb0 to ow
    zU, zL0, zL1 = zN - 2.6, zN - dep + 2.6, zN - dep  # upper flights z zU..zN; lower flights z zL1..zL0
    xf = V["nst_foot"]
    for sx in (-1, 1):
        lo, hi = sorted((sx * lw, sx * ow))
        # the podium under the upper flights and the walk between them and the lower flights, at the side terraces' level
        m.box(lo, hi, 0, nh, zL0, zN, "rustic", skip=("back",))
        m.box(min(sx * eb0, sx * ow), max(sx * eb0, sx * ow), 0, nh, zL1, zL0, "rustic")
        run = eb0 - lw
        for k in range(nst):
            xa, xb = sx * (lw + run * k / nst), sx * (lw + run * (k + 1) / nst)
            yk = H1 - (H1 - nh) * (k + 1) / nst
            m.box(min(xa, xb), max(xa, xb), nh, yk, zU, zN, "step", skip=("bottom", "back"))
        rail([(sx * lw, zU - 0.1), (sx * eb0, zU - 0.1)], [H1, nh])
        rail([(sx * ow, zN - 0.2), (sx * ow, zL1 + 0.1), (sx * eb0, zL1 + 0.1)], nh)
        # lower flights: from the side terrace inward, down to the court, feet facing the axis
        n2 = int(round(nh / 0.16))
        run2 = eb0 - xf
        for k in range(n2):
            xa, xb = sx * (eb0 - run2 * k / n2), sx * (eb0 - run2 * (k + 1) / n2)
            m.box(min(xa, xb), max(xa, xb), 0, nh - nh * (k + 1) / n2, zL1, zL0, "step", skip=("bottom",))
        rail([(sx * eb0, zL1 + 0.1), (sx * xf, zL1 + 0.1)], [nh, 0.05])
        rail([(sx * eb0, zL0 - 0.1), (sx * xf, zL0 - 0.1)], [nh, 0.05])
        m.push(sx * (eb0 + ow) / 2, 0, zL1, math.pi)
        cartouche(0, nh / 2, 1.4, nh * 0.55)
        m.pop()
        FOOTPRINTS.append([(sx * lw, zL0), (sx * ow, zL0), (sx * ow, zN), (sx * lw, zN)])
        FOOTPRINTS.append([(sx * xf, zL1), (sx * ow, zL1), (sx * ow, zL0), (sx * xf, zL0)])
        kp(f"nstair_foot_{'E' if sx > 0 else 'W'}", (sx * xf, 0, (zL0 + zL1) / 2), anchor=True)
        kp(f"nterr_rail_{'E' if sx > 0 else 'W'}", (sx * ow, nh + RAIL, zL1))
        foot = (sx * (xf - 0.4), 0.0, (zL0 + zL1) / 2)
        JOINTS.append([f"north_stair_foot_{'E' if sx > 0 else 'W'}", *foot, "stair foot"])
        ENTRIES.append([f"north_stair_foot_{'E' if sx > 0 else 'W'}", *foot])
    # the north basin 菊花式, 4.5 m across (S310, B), on the axis in a round paved ring (plate 2, P0189, P0348)
    r = V["nfount_d"] / 2
    zf = V["nfount_z"]
    ringp = lambda rr, n=48, lob=0.0: [(rr * (1 + lob * math.cos(4 * 2 * math.pi * k / n)) * math.cos(2 * math.pi * k / n), zf + rr * (1 + lob * math.cos(4 * 2 * math.pi * k / n)) * math.sin(2 * math.pi * k / n)) for k in range(n)]
    m.prism(ringp(r + 4.0), -0.2, 0.05, "pave")
    o, i = ringp(r, lob=0.06), ringp(r - 0.3, lob=0.06)
    for k in range(len(o)):
        a, b, c, d = o[k], o[(k + 1) % len(o)], i[(k + 1) % len(o)], i[k]
        m.poly([(a[0], 0.0, a[1]), (b[0], 0.0, b[1]), (b[0], 0.75, b[1]), (a[0], 0.75, a[1])], "marble")
        m.poly([(a[0], 0.75, a[1]), (b[0], 0.75, b[1]), (c[0], 0.75, c[1]), (d[0], 0.75, d[1])], "marble")
    m.flat(i, 0.6, "water")
    FOOTPRINTS.append(o)
    m.lathe([(0.6, 0.5), (0.4, 1.0), (0.9, 1.6), (0.25, 2.0), (0.5, 2.6), (0.15, 3.0), (0.3, 3.3), (0.0, 3.6)], 8, "marble", cx=0, cz=zf, cap=False)
    jet(0, zf, 3.6, 3.5, 0.15)
    KP["nfount_rim_L"] = {"cands": [{"p": [x, 0.75, z]} for x, z in o], "pick": "left", "anchor": True}
    KP["nfount_rim_R"] = {"cands": [{"p": [x, 0.75, z]} for x, z in o], "pick": "right", "anchor": True}
    kp("nfount_rim_front", (0, 0.75, zf - r * 1.06), anchor=True)
    JOINTS.append(["north_basin_ring", 0.0, -0.2, zf - r - 4.0, "paving foot"])


def build():
    main_block()
    for sx, tag in ((-1, "W"), (1, "E")):
        octagon(sx * V["oct_x"], V["oct_z"], tag)
        colonnade(sx, tag)
    m.cls = "doc"
    south_stair()
    pool()
    north_side()
    m.cls = "doc"
    for sx, sz, tag in ((-1, 1, "SW"), (1, 1, "SE"), (-1, -1, "NW"), (1, -1, "NE")):
        JOINTS.append([f"block_{tag}", sx * hw, 0.0, sz * hd, "wall foot"])


def frame():
    """Scene position and turn of the model's origin: the box XY01-M01's middle and its front (halls3d.js: a = ring[1] - ring[2])."""
    fc = json.load(open(ROOT / "site/reconstruction/data/halls_1860.geojson", encoding="utf-8"))
    f = next(f for f in fc["features"] if f["properties"]["id"] == "XY01-M01")
    ring = [np.array(to_xz(*c), float) for c in f["geometry"]["coordinates"][0]]
    c = (ring[0] + ring[2]) / 2
    a = ring[1] - ring[2]
    a /= np.linalg.norm(a)
    rot = math.atan2(a[0], a[1])
    base = f["properties"]["ground_m"] - DATUM_M
    return [round(float(c[0]), 3), round(base, 3), round(float(c[1]), 3)], round(rot, 6)


def to_scene(p, pos, rot):
    c, s = math.cos(rot), math.sin(rot)
    x, y, z = p
    return [round(pos[0] + c * x + s * z, 3), round(pos[1] + y, 3), round(pos[2] - s * x + c * z, 3)]


def main():
    reset()
    build()
    pos, rot = frame()
    size = m.write_glb(HERE / "model.glb", "XY01 谐奇趣 Xieqiqu", extras={"id": "XY01"})
    tris = m.count()
    prims = {k: len(v["idx"]) // 3 for k, v in sorted(m.prims.items())}
    fill = sum(n for k, n in prims.items() if k.endswith("~fill"))
    params = {k: {"value": v[0], "source": v[1], "grade": v[2], "note": v[3]} for k, v in P.items()}
    json.dump({"id": "XY01", "frame": "x east along the south front, y up from the base, z south; metres", "params": params}, open(HERE / "params.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    pts = {}
    for k, v in KP.items():
        if "p" in v:
            pts[k] = {"local": v["p"], "scene": to_scene(v["p"], pos, rot), "anchor": v.get("anchor", False)}
        else:
            cands = []
            for c in v["cands"]:
                q = {"scene": to_scene(c["p"], pos, rot)}
                if "n" in c:
                    cs, sn = math.cos(rot), math.sin(rot)
                    q["n"] = [round(cs * c["n"][0] + sn * c["n"][1], 4), round(-sn * c["n"][0] + cs * c["n"][1], 4)]
                cands.append(q)
            pts[k] = {"cands": cands, "pick": v["pick"], "anchor": v.get("anchor", False)}
    json.dump({"id": "XY01", "objects": ["XY01", "XY01-01", "XY01-N01", "XY01-02"], "position": pos, "rotationY": rot, "points": pts}, open(HERE / "keypoints.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump({"id": "XY01", "position": pos, "rotationY": rot,
               "joints": [{"name": j[0], "scene": to_scene(j[1:4], pos, rot), "kind": j[4]} for j in JOINTS],
               "entries": [{"name": e[0], "scene": to_scene(e[1:4], pos, rot)} for e in ENTRIES],
               "footprints": [[to_scene((x, 0.0, z), pos, rot)[::2] for x, z in fp] for fp in FOOTPRINTS]},
              open(HERE / "joints.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    summary = {
        "id": "XY01", "aliases": ["XY01-01", "XY01-N01", "XY01-02"], "name": "谐奇趣 Xieqiqu", "glb": "model.glb", "position": pos, "rotationY": rot,
        "line": "Modelled from the plates of 1783-86 (plates 1 and 2, the south and north fronts), Ohlmer's photographs of 1873 from the south, east and north, the plan S01 and the ruin's footprint; every figure is a reading (C) until the Qing drawing 样式雷 985 with its 120 dimensions is seen. The west end, the rear of the colonnades and octagons and the roof's back have no picture: carried round from the documented bays (assumed).",
        "rows": [
            ["Main block", f"{W:g} × {D:g} m, three storeys: ground storey to {H1:g} m, main storey cornice {H2:g} m, top storey cornice {Ht:g} m, ridge {RIDGE:g} m (plates 1-2, P0187-P0189, C)"],
            ["Bays", "7, 7 and 3 (S108, S310, B); the ends a door between two cartouches (P0188, B as photographed, C carried to the west end)"],
            ["Colonnades", f"two quarter ellipses of {V['col_bays']} bays from the block's flanks (S01's traces, B), {V['col_w']:g} m deep, cornice at {H1:g} m, one level with the block's ground storey and the octagons' lower cornice (S108 Fig. 8, B)"],
            ["Music pavilions", f"two octagons {V['oct_flats']:g} m across, {V['oct_x'] * 2:.1f} m apart (S850, B), cornices {H1:g} and {V['oct_up']:g} m, apex {V['oct_apex']:g} m (plate 1, C)"],
            ["South stair", f"a landing at {H1:g} m, a flight down either side of it to a curved terrace at {V['terr_h']:g} m over the pool (plate 1, P0186, P0187), flights at the terrace's ends running out to the court (plate 1 only, C, Q220)"],
            ["Pools", f"south 海棠 pool {V['pool_w']:g} × {V['pool_d']:g} m (S01, C) with the fish 翻尾石鱼 (S840, B); north basin {V['nfount_d']:g} m across (S310, B)"],
            ["Colours", "white stone, grey wall panels, blue-green windows, a yellow-ochre glazed roof with an orange-red edge (the unfinished watercolour of plate 1, S700, C)"],
            ["Fit to the pictures", "Ohlmer's photographs of 1873: 0.3-0.6 m rms at the building over 64 points (P0185-P0189); plate 2: 1.3 m; plate 1: 1.6 m once its heights, drawn 1.57 times its widths, are allowed for (Q219). research/xiyanglou/plate_fit_XY01.csv"],
            ["Storeys measured", "on the photographs, the plan's frontage as the scale: the plates draw the top storey half as tall again (Q219)"],
        ],
        "caption": {"frontage_m": W, "depth_m": D, "eave_m": Ht, "ridge_m": RIDGE, "assumed": True, "confidence": "C"},
        "hides": [],
        "tris": tris, "fill_tris": fill, "glb_bytes": size,
    }
    json.dump(summary, open(HERE / "summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"model.glb {size / 1e6:.2f} MB, {tris} triangles ({fill} fill), {BAL['n']} balusters, {len(KP)} key points; position {pos} rotY {rot}")


if __name__ == "__main__":
    main()
