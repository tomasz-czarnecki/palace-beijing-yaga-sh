#!/usr/bin/env python3
"""观水法 Guanshuifa (XY11), the emperor's seat facing the Great Fountain, the fourth detailed model (Round 15): the concave screen of five carved marble panels on its socle,
with pilasters, end piers, cornice, crest and finials; its brick backing; the round throne platform with its curved steps, the throne, the low balustrade with trophies, the two
trophy pedestals and the two obelisks; the raised strip of the gardens behind with the two side gates, their flights down into the court, the clipped hedges and the plain back wall.
Plain geometry, one GLB (scripts/model_mesh.py) with every figure in params.json; the method is the pilot's (models/XY01-xieqiqu/README.md).

  uv run python models/XY11-guan-shuifa/guanshuifa.py

Writes, beside this file: model.glb, params.json, keypoints.json, joints.json, summary.json (models/README.md).
Frame (scripts/model_site.py): origin at the front middle of the screen's box (XY11-M53), at the court's floor; the front faces north, so x runs WEST along the screen
(the right of plate 16), y up, z north (out of the front, towards 大水法).
Grades: what plate 16, Ohlmer's photograph of 1873 or the photographs since show is `doc`; the screen's brick back, the wall's south face and the gates' backs are `fill` (assumed, C).
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
from model_site import Site  # noqa: E402

P = {
    "chord": (14.4, "S70;S01", "C", "the screen's chord over the end piers' outer corners: P0343 (d, by S603's 1.30 m socle), the plan 14.46 m (b)"),
    "sag": (2.8, "S70;S440", "C", "how far the ends come forward of the middle: P0640 and P0764 (the inner panels 0.4 m, the outer 1.4 m forward of the centre one, by their sizes; the reader)"),
    "bay_c": (2.8, "S71;S70", "C", "the centre bay, the widest: plate 16 169 px against 135-158 for the others; the pitch about 2.5 m on P0343"),
    "bay": (2.45, "S71;S70", "C", "the other four bays"),
    "pier_w": (0.9, "S71", "C", "each end pier, a pier and a recessed strip: plate 16 about 40 px of 794"),
    "plat_y": (0.7, "S70", "C", "the platform above the court: five steps of about 0.14 m (P0344, P0764); the platform survives in place (S603 p.129)"),
    "socle_h": (1.3, "S603", "B", "the socle of the trophy wall, as high as the court's slope: S603 note 17 with p.127 (a reading of two statements)"),
    "plinth_h": (0.45, "S70", "C", "the block under each panel: P0764 32 px against the socle's 87 px"),
    "panel_h": (2.2, "S70;S603", "C", "the panel frames: P0764 150 px at the socle's scale (2.2 m), P0343 2.5 m"),
    "panel_w": (1.2, "S70;S603", "C", "the middle panel's frame: P0343, 100 px at 81 px/m"),
    "pil_top": (4.95, "S71;S871", "C", "the pilasters' tops under the entablature: plate 16, 50 px of entablature under the cornice; v1's 4.45 m sat 0.5 m low on P0777 and P0764"),
    "cornice": (5.6, "S71;S70;S871", "C", "the cornice's top above the socle's foot: P0777 (1873, the cornice whole) and the end piers today (P0343, P0764) put it 0.5 m above v1's 5.1 m (plate 16's module 4.0 m, P0343's end pier 5.1 m)"),
    "crest_h": (0.45, "S71", "C", "the openwork crest over the cornice, a mask cartouche on the axis: plate 16, 35-40 px"),
    "urn_h": (1.0, "S71", "C", "the urns of fruit over the four pilasters and the pairs over the end piers: plate 16, about 80 px over the cornice"),
    "backing": (0.9, "S02;S280", "C", "the brick backing behind the panels (S02 pp.158-159: a brick screen holding marble panels; P0300 shows it torn): its depth assumed"),
    "plat_r": (4.0, "S70;S440;S01", "C", "the round platform's radius: P0640 and P0764 (a circle about as wide as the three middle panels); the plan box 14.5 x 11.5 m holds screen and platform"),
    "plat_cz": (3.2, "S440", "C", "the circle's middle before the screen's middle (its back rim just in front of the socle, P0640)"),
    "steps": (5, "S70;S71", "C", "five convex steps: P0344, P0764 and plate 16 (75 px on the axis)"),
    "step_run": (0.36, "S70", "C", "each step's tread"),
    "throne_h": (3.0, "S71", "C", "the throne from the platform to the crown of its canopy: plate 16, about 1.3 panel heights (300 px)"),
    "rail_h": (0.9, "S71", "C", "the low balustrade round the platform with armour trophies on its posts: plate 16, about 90 px; gone today"),
    "trophy_x": (6.9, "S71", "C", "the trophy pedestals at the platform's front corners, before the end piers: plate 16 x 826 and 1573"),
    "obel_x": (8.7, "S71;S70", "C", "the obelisks just beyond the end piers: plate 16 90-110 px outside the screen's ends; today they stand there on a low base (P0764)"),
    "obel_top": (4.4, "S71;S70", "C", "the obelisk's ball top above the court: plate 16, 150 px under the cornice; today the cut tip stands at the panels' tops (P0764)"),
    "gate_x": (16.9, "S01;S603", "C", "the side gates, 33.86 m apart centre to centre: the plan's skewed squares either side of the screen (b)"),
    "gate_w": (5.2, "S71", "C", "each gate's width: plate 16, 219 px at the gates' module"),
    "gate_h": (5.5, "S70;S71", "C", "the gate's crest above its threshold: P0193 (Child, 1870s) draws it 1.06 times its width; plate 16's fit wants it 2.4 m higher (Q233); P0193 is Child's photograph (S70)"),
    "gate_turn": (40.0, "S71", "C", "the flights run obliquely towards the court's middle: plate 16; v2's straight flights put their feet 3 m too far out"),
    "garden_y": (1.3, "S603", "B", "the gardens' level above the court: the slope's drop (S603, survey)"),
    "gate_steps": (10, "S71", "C", "the flight down from each gate to the court: about ten steps on plate 16"),
    "wall_top": (4.0, "S71", "C", "the plain back wall's coping above the court: plate 16, about 150 px under the cornice"),
    "hedge_h": (1.8, "S71", "C", "the clipped hedges between the gates and the screen: plate 16"),
    "wall_z": (-3.0, "S01;S03", "C", "the back wall's line behind the screen; the court's sunk area ends 6.5 m south of the screen's box (XY10-M45), the wall assumed nearer"),
}
V = {k: v[0] for k, v in P.items()}

COL = {
    "rustic": "#d6cfc1", "joint": "#a39a8a", "marble": "#ebe6da", "wall": "#cbc4b6", "panel": "#c2bbab", "glaze": "#d6cfbf", "brick": "#9a7b62",
    "glass_win": "#2e4a4f", "door": "#4a3b2c", "roof": "#3f7f6c", "roofedge": "#336a5b", "ridge": "#c9a245", "water": "#6f9fb0", "jet": "#d8ecf2",
    "pave": "#c9c2b2", "pebble": "#b3a993", "step": "#d2ccbe", "sculpt": "#b8b0a2", "hedge": "#4d6a3c", "earth": "#8f8a6c", "gilt": "#a8925f",
}

S = None
m = None
P_ = None


def rect(x0, x1, z0, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def arc_frame():
    """The screen's plan: a circle through the middle (0, 0) and the ends (+-chord/2, sag)."""
    h, s = V["chord"] / 2, V["sag"]
    R = (h * h + s * s) / (2 * s)
    return R, (0.0, R)


def on_arc(t, d=0.0):
    """The point at angle t (0 the middle, + to the west) on the screen's front, moved d towards the circle's centre (north); and its inward normal's angle."""
    R, (cx, cz) = arc_frame()
    r = R - d
    x, z = cx + r * math.sin(t), cz - r * math.cos(t)
    return x, z


def screen():
    R, _ = arc_frame()
    yb = V["plat_y"]
    h = V["chord"] / 2
    tmax = math.asin(h / R)
    # the bays along the arc, from the east (-) to the west (+): pier, four bays and the centre one, pier
    widths = [V["pier_w"], V["bay"], V["bay"], V["bay_c"], V["bay"], V["bay"], V["pier_w"]]
    total = sum(widths)
    ts, acc = [], 0.0
    for w in widths:
        ts.append((-tmax + 2 * tmax * acc / total, -tmax + 2 * tmax * (acc + w) / total))
        acc += w
    ysoc, ypl, ypan = yb + V["socle_h"], yb + V["socle_h"] + V["plinth_h"], yb + V["socle_h"] + V["plinth_h"] + V["panel_h"]
    ypil, ycor = yb + V["pil_top"], yb + V["cornice"]
    bk = V["backing"]
    names = ["pier_E", "E2", "E1", "C", "W1", "W2", "pier_W"]
    for i, ((t0, t1), nm) in enumerate(zip(ts, names)):
        a, b = on_arc(t0), on_arc(t1)
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        ang = math.atan2(-(b[1] - a[1]), b[0] - a[0])  # the face frame: s along the bay (westward), d out of it towards the circle's middle (north-ish)
        # the backing: brick, rendered, from the platform to the cornice's foot
        m.cls = "fill"
        m.push(mx, 0.0, mz, ang)
        m.box(-L / 2 - 0.02, L / 2 + 0.02, yb, ycor - 0.6, -bk, -0.25, "wall", skip=("front",))
        m.cls = "doc"
        # the socle with its relief panels
        m.box(-L / 2 - 0.02, L / 2 + 0.02, yb - 0.02, ysoc, -0.25, 0.25, "marble")
        m.box(-L / 2 - 0.1, L / 2 + 0.1, ysoc - 0.18, ysoc, -0.25, 0.38, "marble")
        if nm.startswith("pier"):
            m.box(-L / 2, L / 2, ysoc, ycor - 0.6, -0.25, 0.3, "marble")
            m.box(-0.22, 0.22, ysoc + 0.5, ypil - 0.5, 0.3, 0.38, "joint", skip=("back",))
            m.push(0, 0, 0.25)
            m.box(-L * 0.32, L * 0.32, yb + 0.3, ysoc - 0.35, 0.0, 0.05, "panel", skip=("back",))
            m.pop()
        else:
            m.push(0, 0, 0.25)
            P_.cartouche(0.0, (yb + ysoc) / 2 - 0.05, L * 0.55, V["socle_h"] * 0.5)
            m.pop()
            # the plinth block, the panel in its moulded frame, the crest cartouche over it, the wall face between (brick rendered, plate 16)
            pw = V["panel_w"] * (1.1 if nm == "C" else 1.0) / 2
            m.box(-pw - 0.15, pw + 0.15, ysoc, ypl, -0.25, 0.3, "marble")
            m.box(-L / 2, L / 2, ysoc, ycor - 0.6, -0.25, 0.0, "wall", skip=("back",))
            m.box(-pw - 0.14, pw + 0.14, ypl, ypan, 0.0, 0.2, "marble", skip=("back",))
            m.box(-pw + 0.06, pw - 0.06, ypl + 0.12, ypan - 0.12, 0.2, 0.24, "panel", skip=("back",))
            # the trophy of arms in relief (P0640: a ribboned knot at the top, an oval shield in the middle, crossed arms behind, a drum or a pile of balls below), as plain raised forms
            yc_ = ypl + V["panel_h"] * 0.5
            for sg in (-1, 1):  # crossed lances and swords, corner to corner, behind the shield
                m.poly([(sg * (pw - 0.22), ypl + 0.3, 0.27), (sg * (pw - 0.32), ypl + 0.24, 0.27), (-sg * (pw - 0.22), ypan - 0.42, 0.27), (-sg * (pw - 0.12), ypan - 0.36, 0.27)], "marble")
            P_.oval(0.0, yc_, 0.3, 0.42, n=12, d=0.24)
            m.box(-0.07, 0.07, yc_ + 0.42, ypan - 0.25, 0.24, 0.3, "marble", skip=("back",))  # the staff above the shield
            for sg in (-1, 1):  # the ribbon's two loops
                m.poly([(0.0, ypan - 0.3, 0.3), (sg * 0.28, ypan - 0.18, 0.3), (sg * 0.3, ypan - 0.4, 0.3)], "marble")
            m.box(-0.3, 0.3, ypl + 0.2, ypl + 0.55, 0.24, 0.32, "marble", skip=("back",))  # the drum or balls below
            P_.cartouche(0.0, ypan + 0.32, 0.9, 0.36)
            for s_ in (-pw - 0.3, pw + 0.3):  # the drops down the panel's sides
                m.box(s_ - 0.06, s_ + 0.06, ypan - 0.9, ypan - 0.05, 0.0, 0.12, "marble", skip=("back",))
            kx, kz = _world2(mx, mz, ang, 0.0, 0.2)
            S.kp(f"pan_{nm}_top", (kx, ypan, kz))
            S.kp(f"pan_{nm}_foot", (kx, ypl, kz))
        # the entablature over every bay: architrave, frieze of drops, cornice breaking forward
        m.box(-L / 2 - 0.02, L / 2 + 0.02, ycor - 0.6, ycor - 0.42, -bk, 0.24, "marble")
        m.box(-L / 2 - 0.02, L / 2 + 0.02, ycor - 0.42, ycor - 0.18, -bk, 0.18, "wall")
        m.box(-L / 2 - 0.08, L / 2 + 0.08, ycor - 0.18, ycor, -bk - 0.1, 0.45, "marble")
        for k in range(max(1, int(L / 0.6))):
            s_ = -L / 2 + (k + 0.5) * L / max(1, int(L / 0.6))
            m.box(s_ - 0.06, s_ + 0.06, ycor - 0.4, ycor - 0.22, 0.18, 0.24, "marble", skip=("back",))
        # the crest: openwork scrolls as a low pierced band with a cartouche on the axis
        if not nm.startswith("pier"):
            m.box(-L / 2 + 0.2, L / 2 - 0.2, ycor, ycor + 0.12, -0.1, 0.2, "marble")
            for k in range(2):  # the openwork scrolls: two low C-curves a bay (plate 16)
                s_ = -L / 2 + (k + 0.5) * L / 2
                hump = arc_pts(s_ - 0.45, s_ + 0.45, ycor + 0.12, V["crest_h"] - 0.12, 6)
                for p0, p1 in zip(hump[:-1], hump[1:]):
                    m.poly([(p0[0], ycor + 0.12, 0.1), (p0[0], p0[1], 0.1), (p1[0], p1[1], 0.1), (p1[0], ycor + 0.12, 0.1)], "marble")
            if nm == "C":
                m.box(-0.45, 0.45, ycor, ycor + V["crest_h"] + 0.15, -0.05, 0.25, "marble")
        m.pop()
        # pilasters at the bay's west end (between the panels), and the urns over them
        if 0 < i < len(names) - 2:
            px, pz = b
            m.push(px, 0.0, pz, ang)
            P_.pilaster(0.0, ysoc, ypil, w=0.5, out=0.28)
            m.box(-0.12, 0.12, ypil - 1.4, ypil - 0.4, 0.28, 0.36, "marble", skip=("back",))  # the hanging relief at its top
            m.box(-0.35, 0.35, ycor, ycor + 0.2, -0.15, 0.35, "marble")
            m.pop()
            ux, uz = _world2(px, pz, ang, 0.0, 0.1)
            P_.urn(ux, uz, ycor + 0.2, (V["urn_h"] - 0.2) / 0.95)
        if nm.startswith("pier"):
            # the end pier: its cornice breaks forward; a pair of urns on scrolled pedestals (plate 16)
            side = "E" if nm == "pier_E" else "W"
            ox, oz = (a if side == "E" else b)
            ex, ez = _world2(ox, oz, ang, 0.0, 0.45)
            S.kp(f"scr_cornice_{side}", (ex, ycor, ez))
            S.kp(f"scr_endpier_top_{side}", (ex, ycor - 0.6, ez))
            for d in (-0.22, 0.22):
                ux, uz = _world2(mx, mz, ang, d, 0.05)
                m.box(ux - 0.18, ux + 0.18, ycor, ycor + 0.35, uz - 0.18, uz + 0.18, "marble")
                P_.urn(ux, uz, ycor + 0.35, (V["urn_h"] - 0.3) / 0.95 * 0.8)
            fx, fz = _world2(mx, mz, ang, 0.0, 0.05)
            S.kp(f"finial_{side}_top", (fx, ycor + V["urn_h"] + 0.1, fz))
            S.kp(f"socle_foot_{side}", (ex, yb, ez - 0.07))
    S.kp("socle_top_C", (0.0, ysoc, 0.38))
    S.kp("crest_top_C", (0.0, ycor + V["crest_h"] + 0.15, 0.25))
    S.FOOTPRINTS.append([on_arc(-tmax + 2 * tmax * k / 8, 0.45) for k in range(9)] + [on_arc(tmax - 2 * tmax * k / 8, -V["backing"]) for k in range(9)])


def _world2(mx, mz, ang, s, d):
    """A point s along and d out of a bay's face whose frame is (mx, mz, ang), in the model's plan."""
    c, sn = math.cos(ang), math.sin(ang)
    return mx + c * s + sn * d, mz - sn * s + c * d


def platform():
    yb = V["plat_y"]
    R, (cx, cz) = arc_frame()
    pr, pcz = V["plat_r"], V["plat_cz"]
    h = V["chord"] / 2
    # the level: the round platform and a strip before the whole screen, from the court (a solid riser) to yb
    circle = [(pr * math.sin(2 * math.pi * k / 40), pcz + pr * math.cos(2 * math.pi * k / 40)) for k in range(40)]
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    tmax = math.asin(h / R)
    strip = [on_arc(-tmax + 2 * tmax * k / 16, -0.3) for k in range(17)] + [on_arc(tmax - 2 * tmax * k / 16, 1.6) for k in range(17)]
    lvl = unary_union([Polygon(circle), Polygon(strip)]).buffer(0)
    lvl = lvl.simplify(0.05)
    poly = [(float(a), float(b)) for a, b in list(lvl.exterior.coords)[:-1]]
    S.footing(poly, yb, "step", name="platform")
    # the five convex steps round the circle's front, each ending short of the one below (plate 16)
    n = int(V["steps"])
    run = V["step_run"]
    rise = yb / n
    for k in range(n):
        r_out = pr + run * (n - k)
        r_in = pr + run * (n - k - 1)
        span = math.radians(62 + 3.5 * (n - k))
        seg = 16
        y = rise * (k + 1)
        for j in range(seg):
            a0 = -span + 2 * span * j / seg
            a1 = -span + 2 * span * (j + 1) / seg
            q = [(r_in * math.sin(a0), pcz + r_in * math.cos(a0)), (r_out * math.sin(a0), pcz + r_out * math.cos(a0)), (r_out * math.sin(a1), pcz + r_out * math.cos(a1)), (r_in * math.sin(a1), pcz + r_in * math.cos(a1))]
            m.prism(q, -0.15, y, "step")
    zf = pcz + pr + run * n
    S.kp("steps_foot_C", (0.0, 0.0, zf))
    S.kp("plat_front_C", (0.0, yb, pcz + pr))
    for s_, tag in ((-1, "E"), (1, "W")):
        a = s_ * math.radians(62 + 3.5 * n)
        S.kp(f"steps_foot_{tag}", ((pr + run * n) * math.sin(a), 0.0, pcz + (pr + run * n) * math.cos(a)))
    S.FOOTPRINTS.append([((pr + run * n) * math.sin(2 * math.pi * k / 24), pcz + (pr + run * n) * math.cos(2 * math.pi * k / 24)) for k in range(24)])
    S.joint("steps_foot_C", 0.0, zf - 0.1, "stair foot")
    S.entry("steps_foot_C", 0.0, zf + 0.6)
    # the throne (plate 16): a carved base, the seat, a tall back, a canopy with a tasselled pelmet under a ribbed fan and a crown
    tz = pcz - 1.0
    th = V["throne_h"]
    m.box(-1.3, 1.3, yb, yb + 0.3, tz - 0.9, tz + 0.9, "marble")  # the lobed, carved base
    m.box(-1.05, 1.05, yb + 0.3, yb + 0.5, tz - 0.7, tz + 0.75, "sculpt")
    m.box(-0.75, 0.75, yb + 0.5, yb + 0.95, tz - 0.55, tz + 0.45, "sculpt")  # the seat
    for sg in (-1, 1):  # the arms with scrolled ends
        m.box(sg * 0.75 - 0.12, sg * 0.75 + 0.12, yb + 0.95, yb + 1.35, tz - 0.55, tz + 0.4, "sculpt")
    m.box(-0.7, 0.7, yb + 0.95, yb + 2.1, tz - 0.62, tz - 0.42, "sculpt")  # the tall back
    m.poly([(-0.7, yb + 2.1, tz - 0.5), (0.7, yb + 2.1, tz - 0.5), (0.0, yb + 2.45, tz - 0.5)], "sculpt")
    m.box(-0.95, 0.95, yb + 2.2, yb + 2.42, tz - 0.75, tz + 0.55, "gilt")  # the tasselled pelmet of the canopy
    for k in range(7):  # the ribbed fan over it
        t0, t1 = math.pi * k / 7, math.pi * (k + 1) / 7
        m.poly([(0.0, yb + 2.42, tz - 0.62), (0.9 * math.cos(t0), yb + 2.42 + (th - 2.62) * math.sin(t0), tz - 0.62), (0.9 * math.cos(t1), yb + 2.42 + (th - 2.62) * math.sin(t1), tz - 0.62)], "sculpt")
    m.lathe([(0.16, yb + th - 0.25), (0.11, yb + th - 0.1), (0.0, yb + th)], 6, "gilt", cx=0.0, cz=tz - 0.62, cap=False)
    S.kp("throne_top", (0.0, yb + th, tz - 0.4))
    # the low balustrade round the platform with trophies on its posts, from the screen's ends to the steps
    span = math.radians(62 + 3.5 * n)
    for s_ in (-1, 1):
        pts = [(s_ * pr * math.sin(span + (math.pi - span) * k / 6 * 0.55), pcz + pr * math.cos(span + (math.pi - span) * k / 6 * 0.55)) for k in range(7)]
        pts = [(x * 0.97, z) for x, z in pts]
        P_.rail(pts, yb, h=V["rail_h"], posts=1.3, spacing=0.3)
        for x, z in pts[::2]:
            m.box(x - 0.22, x + 0.22, yb + V["rail_h"], yb + V["rail_h"] + 0.45, z - 0.15, z + 0.15, "marble")


def ornaments():
    """The trophy pedestals before the end piers, the obelisks beyond them (plate 16; the obelisks stand today on a low base, P0764)."""
    yb = V["plat_y"]
    _, _ = arc_frame()
    for sx, tag in ((-1, "E"), (1, "W")):
        x, z = sx * V["trophy_x"], V["sag"] + 1.6
        S.footing(rect(x - 0.75, x + 0.75, z - 0.75, z + 0.75), 0.25, "marble", name=f"trophy_{tag}")
        m.box(x - 0.6, x + 0.6, 0.25, 1.25, z - 0.6, z + 0.6, "marble")
        m.box(x - 0.72, x + 0.72, 1.25, 1.42, z - 0.72, z + 0.72, "marble")
        for nrm, (dx, dz) in (("N", (0, 0.6)),):
            m.push(x, 0, z + 0.6, 0.0)
            P_.cartouche(0.0, 0.75, 0.8, 0.6)
            m.pop()
        # the trophy: a cuirass on a stand, a helmet, shields and banners, as plain forms
        m.box(x - 0.35, x + 0.35, 1.42, 2.3, z - 0.25, z + 0.25, "marble")
        m.lathe([(0.3, 2.3), (0.32, 2.5), (0.0, 2.75)], 6, "marble", cx=x, cz=z)
        m.poly([(x - 0.7, 1.6, z + 0.05), (x - 0.25, 1.6, z + 0.05), (x - 0.25, 2.6, z + 0.05), (x - 0.7, 2.9, z + 0.05)], "marble")
        m.poly([(x + 0.25, 1.6, z + 0.05), (x + 0.7, 1.6, z + 0.05), (x + 0.7, 2.9, z + 0.05), (x + 0.25, 2.6, z + 0.05)], "marble")
        S.kp(f"trophy_{tag}_ped_top", (x, 1.42, z + 0.72))
        # the obelisk on its base, claw feet, a tapering shaft with a medallion, the ball
        ox, oz = sx * V["obel_x"], V["sag"] - 0.2
        yt = V["obel_top"]
        ys = yb + V["socle_h"]
        S.footing(rect(ox - 0.8, ox + 0.8, oz - 0.8, oz + 0.8), ys, "marble", name=f"obel_{tag}")
        m.box(ox - 0.85, ox + 0.85, ys - 0.15, ys, oz - 0.85, oz + 0.85, "marble")
        for cx_ in (-0.45, 0.45):
            for cz_ in (-0.45, 0.45):
                m.lathe([(0.14, ys), (0.1, ys + 0.3)], 5, "marble", cx=ox + cx_, cz=oz + cz_)
        m.box(ox - 0.55, ox + 0.55, ys + 0.3, ys + 0.5, oz - 0.55, oz + 0.55, "marble")
        sq = lambda w: [(ox - w, oz - w), (ox + w, oz - w), (ox + w, oz + w), (ox - w, oz + w)]
        m.frustum(sq(0.42), sq(0.16), ys + 0.5, yt - 0.3, "marble")
        m.push(ox, 0, oz + 0.38, 0.0)
        P_.oval(0.0, ys + 1.0, 0.22, 0.3)
        m.pop()
        m.lathe([(0.0, yt - 0.3), (0.15, yt - 0.25), (0.15, yt - 0.05), (0.0, yt)], 6, "marble", cx=ox, cz=oz, cap=False)
        S.kp(f"obel_{tag}_top", (ox, yt, oz))
        S.kp(f"obel_{tag}_foot", (ox, ys + 0.3, oz + 0.55))


def gardens():
    """The raised strip of the gardens behind and beside the screen, its front a retaining face to the court; the gates on it with their flights; the hedges; the back wall."""
    gy_ = V["garden_y"]
    wz = V["wall_z"]
    gx = V["gate_x"]
    R, _ = arc_frame()
    h = V["chord"] / 2
    tmax = math.asin(h / R)
    xe = gx + V["gate_w"] / 2 + 2.0
    back = [on_arc(tmax - 2 * tmax * k / 12, -V["backing"] - 0.02) for k in range(13)]
    fz = V["sag"] + 0.4
    poly = [(-xe, wz), (xe, wz), (xe, fz), (V["obel_x"] + 0.8, fz), (V["obel_x"] + 0.8, V["sag"] - 1.0)] + back + [(-V["obel_x"] - 0.8, V["sag"] - 1.0), (-V["obel_x"] - 0.8, fz), (-xe, fz)]
    S.footing(poly, gy_, "rustic", name="strip", corners=False, lid=False)
    for x in (-xe, -V["obel_x"] - 0.8, V["obel_x"] + 0.8, xe):
        S.joint(f"strip_{'E' if x < 0 else 'W'}_{abs(x):.0f}", x, fz, "retaining foot", y=S.gy(x, fz) - 0.15)
    m.flat([(x, z) for x, z in poly], gy_ + 0.02, "earth")
    # the back wall with its coping, from end to end (fill on its south face)
    gw = V["gate_w"] / 2
    for a, b in ((-xe, -gx - gw), (-gx + gw, gx - gw), (gx + gw, xe)):
        m.box(a, b, gy_, V["wall_top"] - 0.15, wz - 0.3, wz + 0.3, "wall", skip=("back", "bottom"))
        m.box(a - 0.1, b + 0.1, V["wall_top"] - 0.15, V["wall_top"], wz - 0.4, wz + 0.4, "marble")
        m.cls = "fill"
        S.skirt([(a, wz - 0.3), (b, wz - 0.3)], V["wall_top"] - 0.15, "wall", closed=False)
        m.cls = "doc"
    S.kp("wall_top_E", (-gx + V["gate_w"] / 2 + 0.3, V["wall_top"], wz + 0.4))
    S.kp("wall_top_W", (gx - V["gate_w"] / 2 - 0.3, V["wall_top"], wz + 0.4))
    # the hedges between the gates and the obelisks, on the strip before the wall (plate 16)
    for sx in (-1, 1):
        a, b = sorted((sx * (V["obel_x"] + 1.4), sx * (gx - V["gate_w"] / 2 - 0.4)))
        m.box(a, b, gy_, gy_ + V["hedge_h"], wz + 0.6, wz + 2.0, "hedge")
        a, b = sorted((sx * (gx + V["gate_w"] / 2 + 0.4), sx * xe))
        m.box(a, b, gy_, gy_ + V["hedge_h"], wz + 0.6, wz + 2.0, "hedge")
    for sx, tag in ((-1, "E"), (1, "W")):
        gate(sx * gx, wz, gy_, tag)


def gate(x, wz, y0, tag):
    """A side gate (plate 16, P0193): a round-arched opening with a double door, pilasters with carved panels, a bell-shaped pediment with a shell crest; a flight down to the court."""
    w = V["gate_w"] / 2
    H = V["gate_h"]
    zf = wz + 1.1
    ow, oh = 1.0, 3.0
    m.box(x - w, x + w, y0, y0 + H - 1.6, wz - 0.3, zf, "marble", skip=("bottom", "front", "back"))
    m.cls = "fill"
    m.box(x - w, x + w, y0, y0 + H - 1.6, wz - 0.3, zf, "marble", skip=("bottom", "front", "left", "right", "top"))
    m.cls = "doc"
    m.push(x, 0, zf, 0.0)
    P_.wall_holes(-w, w, y0, y0 + H - 1.6, [(-ow, ow, y0, y0 + oh - ow, ow)], "marble")
    P_.opening(-ow, ow, y0, y0 + oh - ow, ow, depth=0.6, kind="door", frame=0.18)
    for s_ in (-w + 0.45, w - 0.45, -ow - 0.6, ow + 0.6):
        P_.pilaster(s_, y0, y0 + H - 1.9, w=0.5, out=0.2)
    P_.entablature(-w, w, y0 + H - 1.6, h=0.6, out=0.3)
    # the bell-shaped pediment: a curved gable and a shell crest
    yb = y0 + H - 1.6
    curve = [(-w + 0.2, yb), (-w * 0.7, yb + 0.7), (-w * 0.35, yb + 0.9), (0.0, yb + 1.15), (w * 0.35, yb + 0.9), (w * 0.7, yb + 0.7), (w - 0.2, yb)]
    m.poly([(p[0], p[1], 0.05) for p in curve], "marble")
    m.poly([(p[0], p[1], -0.9) for p in curve], "marble")
    for p0, p1 in zip(curve[:-1], curve[1:]):
        m.poly([(p0[0], p0[1], 0.05), (p1[0], p1[1], 0.05), (p1[0], p1[1], -0.9), (p0[0], p0[1], -0.9)], "marble")
    fan = 7
    for k in range(fan):
        t0, t1 = math.pi * k / fan, math.pi * (k + 1) / fan
        m.poly([(0.0, yb + 1.1, 0.12), (0.55 * math.cos(t0), yb + 1.1 + 0.45 * math.sin(t0), 0.12), (0.55 * math.cos(t1), yb + 1.1 + 0.45 * math.sin(t1), 0.12)], "marble")
    m.pop()
    S.kp(f"gate_{tag}_top", (x, yb + 1.55, zf + 0.12))
    jin = x + (ow if x < 0 else -ow)
    S.kp(f"gate_{tag}_jamb_in", (jin, y0, zf))
    S.FOOTPRINTS.append(rect(x - w, x + w, wz - 0.3, zf))
    # the flight down to the court: ten steps turned towards the court's middle (plate 16), plain stringers
    n = int(V["gate_steps"])
    fw = 1.9
    z0 = V["sag"] + 0.4
    a = math.radians(V["gate_turn"])
    sx = -1 if x < 0 else 1
    dx, dz = -sx * math.sin(a), math.cos(a)  # down the flight
    ux, uz = dz, -dx  # across it
    top = (x, z0)
    run = 0.36
    for k in range(n):
        q = [(top[0] + dx * run * k + ux * s_ * fw, top[1] + dz * run * k + uz * s_ * fw) for s_ in (-1, 1)]
        q += [(top[0] + dx * run * (k + 1) + ux * s_ * fw, top[1] + dz * run * (k + 1) + uz * s_ * fw) for s_ in (1, -1)]
        y = y0 * (n - k) / n
        lo = min(S.gy(*c) for c in q) - 0.15
        m.prism(q, lo, y, "step")
    for s_ in (-1, 1):  # the stringers
        e0 = (top[0] + ux * s_ * (fw + 0.12), top[1] + uz * s_ * (fw + 0.12))
        e1 = (e0[0] + dx * run * n, e0[1] + dz * run * n)
        q = [(e0[0] - ux * 0.12, e0[1] - uz * 0.12), (e0[0] + ux * 0.12, e0[1] + uz * 0.12), (e1[0] + ux * 0.12, e1[1] + uz * 0.12), (e1[0] - ux * 0.12, e1[1] - uz * 0.12)]
        m.prism(q, -0.15, y0 + 0.15, "marble")
    # the threshold between the strip's edge and the gate
    m.box(x - fw, x + fw, y0 - 0.05, y0 + 0.01, zf, z0, "step", skip=("bottom",))
    fx, fz = top[0] + dx * run * n, top[1] + dz * run * n
    S.kp(f"gate_{tag}_steps_foot", (fx, 0.0, fz))
    S.FOOTPRINTS.append([(top[0] + ux * fw * 1.1, top[1] + uz * fw * 1.1), (top[0] - ux * fw * 1.1, top[1] - uz * fw * 1.1), (fx - ux * fw * 1.1, fz - uz * fw * 1.1), (fx + ux * fw * 1.1, fz + uz * fw * 1.1)])
    S.joint(f"gate_{tag}_steps_foot", fx - dx * 0.1, fz - dz * 0.1, "stair foot")
    S.entry(f"gate_{tag}_steps_foot", fx + dx * 0.6, fz + dz * 0.6)
    S.entry(f"gate_{tag}_out", x, wz - 1.0)


def build():
    global S, m, P_
    S = Site("XY11-M53")
    m = Mesh(COL)
    S.m = m
    P_ = Parts(m, rail_h=V["rail_h"], baluster_segs=4)
    m.cls = "doc"
    platform()
    screen()
    m.cls = "doc"
    ornaments()
    gardens()


def summary(tris, fill, size):
    yb = V["plat_y"]
    rows = [
        ["Screen", f"five carved marble panels of European arms in a concave screen {V['chord']:g} m over its end piers (P0343, S01, C), its ends {V['sag']:g} m forward (P0640, P0764, C); the socle {V['socle_h']:g} m (S603, B), panels {V['panel_h']:g} m high (P0764, C), cornice {yb + V['cornice']:.1f} m above the court, a crest and eight urns (plate 16, C); brick backing behind (S02, B; its depth assumed). The panels were set back in 1977 on their old spot (S817, B)"],
        ["Platform and throne", f"the round platform {V['plat_y']:g} m above the court with {int(V['steps'])} convex steps (P0344, P0764; in place, S603 p.129, B); on it the throne with its canopy, {V['throne_h']:g} m high, and the low balustrade with trophies (plate 16, C)"],
        ["Pedestals and obelisks", f"two trophy pedestals before the end piers and two obelisks on their bases beyond them, their balls {V['obel_top']:g} m above the court (plate 16; the obelisks stand today, P0764, C)"],
        ["Gates and wall", f"the side gates {2 * V['gate_x']:.1f} m apart (S01, C) on the gardens' level, {V['garden_y']:g} m above the court (S603, B), each with a flight of {int(V['gate_steps'])} steps down (plate 16, C) and the form of P0193; clipped hedges and the plain back wall (plate 16, C)"],
        ["Colours", "white marble (S02 pp.158-159, B), the backing and the wall rendered brick, the throne gilt (C: the plate is not coloured)"],
    ]
    return {
        "id": "XY11", "aliases": [], "name": "观水法 Guanshuifa", "glb": "model.glb", "position": S.pos, "rotationY": S.rot,
        "line": "Modelled from plate 16 of 1783-86, Ohlmer's photograph of 1873 and the photographs since 1914 (the panels re-erected in 1977, the platform in place), the plan S01 and Durand's survey (S603); every figure is a reading (C) unless the row says otherwise. Faces no picture shows (the screen's brick back, the wall's south face) are carried round (assumed).",
        "rows": rows,
        "caption": {"frontage_m": V["chord"], "depth_m": round(V["plat_cz"] + V["plat_r"] + V["step_run"] * V["steps"], 1), "eave_m": round(yb + V["cornice"], 1), "ridge_m": round(yb + V["cornice"] + V["urn_h"], 1), "assumed": True, "confidence": "C"},
        "hides": [],
        "tris": tris, "fill_tris": fill, "glb_bytes": size,
    }


def main():
    build()
    size = m.write_glb(HERE / "model.glb", "XY11 观水法 Guanshuifa", extras={"id": "XY11"})
    tris = m.count()
    prims = {k: len(v["idx"]) // 3 for k, v in sorted(m.prims.items())}
    fill = sum(n for k, n in prims.items() if k.endswith("~fill"))
    S.write(HERE, "XY11", ["XY11"], P, "x west along the screen (the front faces north), y up from the court's floor, z north (out of the front); metres", summary(tris, fill, size))
    print(f"model.glb {size / 1e6:.2f} MB, {tris} triangles ({fill} fill), {P_.balusters} balusters, {len(S.KP)} key points, {len(S.JOINTS)} joints, {len(S.ENTRIES)} entries; position {S.pos} rotY {S.rot}")


if __name__ == "__main__":
    main()
