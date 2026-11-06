#!/usr/bin/env python3
"""远瀛观 Yuanyingguan (XY09), the hall of the tapestries on its terrace behind 大水法, the fifth detailed model (Round 16): the raised terrace with its retaining walls
of piers, its paved forecourt, trees and balustrades; the hall on its base, an inverted 凹 in plan: the two wings with chamfered corners come one bay forward, each with
a big window, a low roof of eight slopes, a balustrade and a square lantern with a clock face on every side; between them the centre block with the clock gate (the door
between two carved columns on pedestals with lions, an entablature block over each, the attic with the clock wheel under an arched moulding and a crest), a door-like
opening either side; the centre's roofs in tiers (a fish-scale roof, the main hipped roof, a pedestal band and the crown); the body behind under a hipped roof.
Plain geometry, one GLB (scripts/model_mesh.py) with every figure in params.json; the method is the pilot's (models/XY01-xieqiqu/README.md).

  uv run python models/XY09-yuanying-guan/yuanyingguan.py

Writes, beside this file: model.glb, params.json, keypoints.json, joints.json, summary.json (models/README.md).
Frame (scripts/model_site.py): the hall's box XY09-M44 gives the turn and the front (the wings' front plane, z = 0); the origin is moved along the front onto 大水法's axis
(models/XY10-da-shuifa/: the two boxes stand 0.72 m apart across the axis, within the ruin readings' 3-4 m; plate 14 and S01 draw one axis). x east along the front,
y up from the ground at the box (the terrace's foot), z south (out of the front, towards 大水法).
Grades: what plate 14, the photographs of 1873-76 or the ruin since shows is `doc`; the hall's rear and end faces, the body behind the centre block, the terrace's south
face behind 大水法 and its back stair are `fill` (assumed, C). Every figure is C unless params.json says otherwise.
"""

import json
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
    # the terrace (S603: 35 x about 31 m, which way not stated; Q67)
    "terr_w": (31.0, "S603;S71", "B", "the terrace W-E: S603's 'about 31 m' taken W-E (plate 14 draws the side rails about 30 m apart, c); order not stated (Q67)"),
    "terr_d": (35.0, "S603", "B", "the terrace N-S: S603's 35 m; its south face meets 大水法's model (models/XY10-da-shuifa/, the stairs' landings)"),
    "terr_y": (4.3, "S71;S871;S70", "C", "the terrace's top above its foot: 大水法's stairs arrive 4.63 m above the court (Round 15, Q232); the court lies 0.33 m below this box's ground"),
    "pier_step": (3.9, "S603", "C", "the retaining walls' piers ('monolithic piers with long rusticated stones', S603 p.131-132): their spacing assumed"),
    "rail_h": (1.0, "S71", "C", "the forecourt's balustrades: plate 14"),
    "front_rail_x": (9.0, "S71", "C", "the straight front balustrade's ends, where it turns back north: plate 14 x 744-1661 at the rail's depth; 大水法's stairs arrive beyond them"),
    # the hall (S603: 21 x 28 m from the post grid, order not stated; Q67)
    "hall_w": (28.0, "S603;S71;S850", "B", "the hall W-E: S603's 28 m (the post grid); the rubble core 28.4 m W-E (S850, b); plate 14's wings and centre at the 6.0 m column spacing make 27-28 m, against 18 m at 4.2 m (Q67)"),
    "hall_d": (21.0, "S603;S850", "B", "the hall N-S: S603's 21 m; the rubble core N-S 20.1 m (S850, b)"),
    "S": (6.0, "S70;S71;S603", "C", "the carved columns' spacing, the module of the front: plate 14's own ratios against S603's 28 m (the centre 431 px, the columns 228 px apart, the wings 200 px) and P0216's door (the column 3.0 m off the door's axis at a 2.0 m door); the dossier's 4.2 m (the 'centre bays 4 m', c) gives an 18 m front. P0183's brick courses then 10.6 cm"),
    "base_h": (1.2, "S70;S71", "C", "the hall's floor above the terrace: the door's and the side openings' jambs stop at the pedestals' top on P0216 and P0757 (reader 2); plate 14 a raised base and the threshold 41 px above the pedestals' foot"),
    "wing_w": (7.2, "S71", "C", "each wing over its outer side face and the centre block's corner: 28 m less the centre; its front face 5.0 m, plate 14's 200 px at 40 px/m (the 28 m on 1125 px)"),
    "wing_ch": (1.1, "S71", "C", "the wings' chamfered corners, outer and inner: plate 14, facets of 35-41 px with their own pilasters (reader 1); S603's 'eight-slope' wing roofs fit a chamfered plan"),
    "wing_d": (8.0, "S71", "C", "each wing's depth as a pavilion under its own roof: assumed; the body runs on behind"),
    "recess": (4.5, "S71", "C", "how far the centre block stands back of the wings' front: the wing's inner face holds one window bay (plate 14, reader 1: 0.7-0.9 of the wing's front); S310 '倒凹'"),
    "ctr_w": (13.6, "S71;S70", "C", "the centre block's front: P0183's pier between column and side opening 0.27 S (the openings' axes 5.6 m out, P0183, P0216, P0719 all put them 1 m further out than v2's 4.75 m); plate 14 draws that pier 0.12 S"),
    "ctr_d": (12.0, "S71", "C", "the centre block's depth under its tiered roof: assumed, about square as plate 14 draws the main roof"),
    "band_h": (0.9, "S71", "C", "the low band over the centre block's cornice, under the fish-scale roof: plate 14 (the roof's eave about 1 m over the cornice at the attic's scrolls)"),
    "cornice": (8.0, "S70;S71", "C", "the main cornice's and the entablature blocks' top above the terrace: P0183 1.34 S (the photographs; plate 14 draws the order short, 1.11-1.27 S: trust the photographs, reader 1)"),
    "col_ped": (1.25, "S70", "C", "the pedestals' top, on the floor's level: P0216, P0757 (0.17-0.21 of the shaft and capital, reader 2)"),
    "col_top": (7.1, "S70", "C", "the capitals' top above the pedestals' foot: P0183 1.19 S; P0216 1.74 times the door's height"),
    "col_r": (0.45, "S70", "C", "the shaft's radius: shaft and capital 6.5-6.7 shaft widths (P0216, P0757, reader 2)"),
    "cap_h": (1.4, "S70", "C", "the capital: 0.24 of the shaft and capital (P0216, reader 2), a Corinthian type with a mask (P0183)"),
    "ped_w": (1.9, "S70", "C", "the pedestal: 1.9-2.5 shaft widths (reader 2)"),
    "blk_w": (2.3, "S70", "C", "the entablature block: 2.5-2.8 shaft widths wide, standing proud of the wall (reader 2)"),
    "col_d": (1.1, "S70", "C", "the columns' axis before the wall: each stands before a plain pier bonded into the wall, its block projecting deeply (P0179, P0216, P0291, reader 2)"),
    "door_w": (1.9, "S70;S71", "C", "the door's opening: P0183 0.32 S (reader 1), P0216 2.0 m at the plate's figure (reader 2)"),
    "door_h": (4.2, "S70", "C", "the door's opening above the floor to its arch's crown: its head 0.90 S above the pedestals' foot (P0183)"),
    "cwin_w": (1.65, "S70", "C", "the centre block's side openings: door-like, to the floor, 1.65 x 4.0 m, their crowns level with the door's (P0216, P0179, reader 2)"),
    "cwin_x": (5.6, "S70;S71", "C", "the side openings' axes: P0183's pier between column and opening 0.27 S (reader 1); v2's 4.75 m sat 1 m inside on P0183, P0216 and P0719"),
    "win_w": (1.45, "S71", "C", "the wings' windows: plate 14, 0.25 x 0.65 of the wing's front, on a carved sill block 0.23 of it above the foot"),
    "win_h": (3.8, "S71", "C", "as above"),
    "win_sill": (2.3, "S71", "C", "the wings' window sills above the terrace: on a carved sill block 0.23 Wf above the wing's foot on the base (plate 14); v2's 1.35 m sat 1.6 m low on the plate"),
    "clock_y": (9.7, "S70;S71", "C", "the clock wheel's centre above the terrace: 1.61 S on P0183, 1.60 on plate 14: the attic agrees on both"),
    "clock_r": (0.8, "S70;S71", "C", "the wheel's radius: P0183 0.25 S across, plate 14 0.31 S"),
    "attic_w": (3.0, "S70", "C", "the attic between its pilasters' outer faces: P0183, 230 of 446 px"),
    "attic_top": (10.9, "S70;S71", "C", "the arched moulding's top: 1.81 S (P0183), 1.84 (plate 14)"),
    "crest_top": (11.7, "S70;S71", "C", "the crest's top: 1.95 S (P0183), 1.94 (plate 14)"),
    "scroll_x": (3.5, "S70;S71", "C", "the attic's foot scrolls' tips either side of the axis: P0183 1.17 S, plate 14 1.09 S over their span"),
    "skirt_top": (10.6, "S71", "C", "the fish-scale roof from a low band over the cornice to the main roof's foot: plate 14 draws its eave tips 2 m over the cornice (1.63 against 1.24 Wf), a band with the attic's scrolls between"),
    "roof_eave": (10.6, "S71", "C", "the main hipped roof's eave: plate 14, its corner tips (lifted) level with the attic's arch, 2.08 Wf"),
    "roof_w": (9.5, "S71", "C", "the main roof over its eave tips: plate 14, 359 px (1.57 S)"),
    "roof_apex": (13.2, "S71", "C", "the main roof's top: plate 14, 2.50 Wf (2.19 S); the dossier's 12.4 m on the old 2 m base and a 4.2 m column spacing"),
    "crown": (15.5, "S71", "C", "the crown's top: plate 14, 2.92 Wf (2.56 S); box XY09-M44 had 12.6 m above the terrace"),
    "lan_w": (2.3, "S71", "C", "the lanterns' width: plate 14, 0.4 of the wing's front"),
    "lan_foot": (8.6, "S71", "C", "the deck under the lantern, its balustrade's top 9.3 m (plate 14, 1.60 Wf)"),
    "lan_eave": (11.7, "S71", "C", "the lantern's eave: plate 14, 2.02 Wf"),
    "lan_clock": (10.3, "S71", "C", "the lantern's clock centre: plate 14, 1.77 Wf; the face 0.26 Wf across"),
    "lan_top": (14.2, "S71", "C", "the lantern's urn finial: plate 14, 2.45 Wf"),
    "body_ridge": (10.2, "S603;S71", "C", "the body behind under a hipped Chinese roof (S603 p.133: side bays two-slope Chinese tile, B): its ridge assumed; plate 14 shows only low roofs behind the wings, below the centre's main roof and the lanterns (v3's 12.0 m competed with the centre's tiers in the overlay)"),
    "trees": (8, "S71", "C", "the forecourt's trees: plate 14, four a side in a row running outward, the innermost in line with the wings' inner faces; none before the centre"),
}
V = {k: v[0] for k, v in P.items()}

COL = {
    "rustic": "#c8c2b5", "joint": "#8f877a", "marble": "#ebe6da", "wall": "#a5a29a", "panel": "#8f8a82", "glaze": "#3f8a86", "sculpt": "#ddd7c9",
    "glass_win": "#2e4a4f", "door": "#4a3b2c", "roof": "#3f7f6c", "roofedge": "#336a5b", "scale": "#4a8a78", "ridge": "#c9a245", "gilt": "#b59a55",
    "pave": "#c9c2b2", "step": "#d2ccbe", "earth": "#8a7f6c", "leaf": "#4f6b3d", "trunk": "#6b5a45", "clock": "#e6e0cc",
}

S = None
m = None
P_ = None
F = {}  # derived levels


def rect(x0, x1, z0, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def face(a, b):
    """Push a face frame on the wall from a to b (plan x, z): s along it from a, d out of it (to the left of a->b seen from above with z south: the outline runs front W->E, east S->N, back E->W, west N->S)."""
    dx, dz = b[0] - a[0], b[1] - a[1]
    m.push(a[0], 0.0, a[1], math.atan2(-dz, dx))
    return math.hypot(dx, dz)


def wall(a, b, y0, y1, holes, kind_cls="doc", thick=0.6, cornice=None, pil=(), head="scroll", mat="wall", rust=False):
    """A wall face from a to b with openings: holes = [(s_mid, w, sill, h, rise, kind, head)]; its reveals and glass by Parts.opening; pilasters at s in `pil`; an entablature to `cornice`."""
    keep = m.cls
    m.cls = kind_cls
    L = face(a, b)
    hs = [(s - w / 2, s + w / 2, y0 + sill, y0 + sill + h - rise, rise) for s, w, sill, h, rise, kind, hd in holes]
    P_.wall_holes(0.0, L, y0, y1, hs, mat)
    for (s, w, sill, h, rise, kind, hd), hh in zip(holes, hs):
        P_.opening(hh[0], hh[1], hh[2], hh[3], rise, depth=0.4, kind=kind, frame=0.2, head=hd)
    if rust:
        P_.rustication(0.0, L, y0, y1)
    for s in pil:
        P_.pilaster(s, y0, (cornice or y1) - 0.9, w=0.6, out=0.2)
    if cornice:
        P_.entablature(0.0, L, cornice, h=0.9, out=0.5)
    m.pop()
    m.cls = keep
    return L


def ring_walls(poly, y0, y1, holes_by_side, cls_by_side, cornice, pil_by_side=None):
    """Walls round a closed outline (front W->E first); side i from poly[i] to poly[i+1]."""
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        wall(a, b, y0, y1, holes_by_side.get(i, []), cls_by_side.get(i, "fill"), cornice=cornice, pil=(pil_by_side or {}).get(i, ()))


def even_windows(L, n, w, sill, h, kind="win", head="scroll", margin=1.0):
    if n <= 0:
        return []
    step = (L - 2 * margin) / n
    return [(margin + step * (k + 0.5), w, sill, h, w / 2, kind, head) for k in range(n)]


def terrace():
    """The terrace (XY09-M43): retaining walls of piers with rusticated stones on the east, west and north (S603); its south face behind 大水法 (fill: 大水法's model stands before it);
    the paved top; the balustrades of the forecourt (plate 14), open where 大水法's stairs arrive; a back stair down to the north (assumed, for reach)."""
    ty = V["terr_y"]
    hw = V["terr_w"] / 2
    zf, zb = F["terr_front"], F["terr_front"] - V["terr_d"]
    poly = [(-hw, zf), (hw, zf), (hw, zb), (-hw, zb)]
    # the retaining walls: a skirt from just below the ground to the top, with piers proud of it and joints of long stones between
    S.footing(poly, ty, "rustic", name="terrace", corners=True, lid=False, fp=False)
    sides = [((-hw, zf), (hw, zf), "fill"), ((hw, zf), (hw, zb), "doc"), ((hw, zb), (-hw, zb), "doc"), ((-hw, zb), (-hw, zf), "doc")]
    for a, b, cls in sides[1:]:
        m.cls = cls
        L = face(a, b)
        n = max(2, round(L / V["pier_step"]))
        for k in range(n + 1):
            s = L * k / n
            m.box(s - 0.45, s + 0.45, -0.2, ty - 0.35, 0.0, 0.25, "rustic", skip=("back",))
            if 0 < k < n:  # the pier's foot is a joint (its face follows the wall's skirt; the box itself starts 0.2 m below the frame's zero)
                t = s / L
                px_, pz_ = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                S.JOINTS.append([f"terr_pier_{len(S.JOINTS)}", px_, S.gy(px_, pz_) - 0.15, pz_, "wall foot"])
        y = 0.6
        while y < ty - 0.4:
            m.box(0.0, L, y - 0.03, y + 0.03, 0.0, 0.015, "joint", skip=("back",))
            y += 0.6
        m.box(-0.1, L + 0.1, ty - 0.35, ty, 0.0, 0.35, "marble")  # the coping
        m.pop()
    m.cls = "doc"
    # the paving: big slabs in a grid (plate 14), over the whole top; the ways that cross it lie on it (scripts/model_site.py, deck)
    m.flat(poly, ty, "pave")
    S.deck("terrace", ty, poly)
    x = -hw + 2.0
    while x < hw - 0.5:
        m.box(x - 0.04, x + 0.04, ty, ty + 0.012, zb + 0.5, zf - 0.3, "joint", skip=("bottom",))
        x += 2.0
    z = zf - 2.0
    while z > zb + 0.5:
        m.box(-hw + 0.3, hw - 0.3, ty, ty + 0.012, z - 0.04, z + 0.04, "joint", skip=("bottom",))
        z -= 2.0
    # the balustrades: the front between 大水法's stair heads (urns on the posts, plate 14), and along the sides; the back one is fill
    zr = zf - 0.35
    fx = V["front_rail_x"]
    for sx in (-1, 1):  # the straight front, in two runs from the axis (no post there), turning back north at its ends
        P_.rail([(0.0, zr), (sx * fx, zr), (sx * fx, zr - 1.6)], ty, posts=3.6, ends=False)
        m.box(sx * fx - 0.22, sx * fx + 0.22, ty, ty + V["rail_h"] + 0.08, zr - 0.22, zr + 0.22, "marble")
        for x_ in (1.8, 5.3, fx):
            m.box(sx * x_ - 0.25, sx * x_ + 0.25, ty, ty + V["rail_h"] + 0.1, zr - 0.25, zr + 0.25, "marble")
            P_.urn(sx * x_, zr, ty + V["rail_h"] + 0.1, 0.75)
        xr = sx * (hw - 0.35)
        P_.rail([(xr, zf - 0.35), (xr, zb + 0.35)], ty, posts=3.0)
        S.kp(f"terr_rail_{'L' if sx < 0 else 'R'}", (sx * fx, ty + V["rail_h"], zr))
    S.kp("terr_rail_C", (0.0, ty + V["rail_h"], zr))
    m.cls = "fill"
    P_.rail([(-hw + 0.35, zb + 0.35), (-1.6, zb + 0.35)], ty, posts=3.0)
    P_.rail([(1.6, zb + 0.35), (hw - 0.35, zb + 0.35)], ty, posts=3.0)
    # the back stair down to the north on the axis (assumed: no picture or plan shows how the terrace was reached from the ranges behind)
    n = int(round(ty / 0.16))
    run = 0.3
    for k in range(n):
        y = ty - (k + 1) * ty / n
        q = rect(-1.5, 1.5, zb - run * (k + 1), zb - run * k)
        lo = min(S.gy(*c) for c in q) - 0.15
        if y > lo:
            m.prism(q, lo, y + 0.001, "step")
    zfoot = zb - run * n
    for sx in (-1, 1):
        q = [(sx * 1.5, zb), (sx * 1.8, zb), (sx * 1.8, zfoot), (sx * 1.5, zfoot)]
        m.prism(q, S.gy(sx * 1.65, zfoot) - 0.15, 0.6, "marble")
        m.poly([(sx * 1.8, 0.6, zfoot), (sx * 1.8, ty + 0.9, zb), (sx * 1.5, ty + 0.9, zb), (sx * 1.5, 0.6, zfoot)], "marble")
    m.cls = "doc"
    S.FOOTPRINTS.append(rect(-1.9, 1.9, zfoot, zb))
    S.joint("back_stair_foot", 0.0, zfoot + 0.1, "stair foot")
    S.entry("back_stair_foot", 0.0, zfoot - 0.6)
    # the rims as footprints: the ways and the planting keep clear of the walls (the top is walked: ways cross it)
    for a, b in ((poly[1], poly[2]), (poly[2], poly[3]), (poly[3], poly[0])):
        xs, zs = sorted((a[0], b[0])), sorted((a[1], b[1]))
        S.FOOTPRINTS.append(rect(xs[0] - 0.4, xs[1] + 0.4, zs[0] - 0.4, zs[1] + 0.4))
    # the entries where 大水法's stairs arrive (its model draws the flights and their landings)
    for tag in ("W", "E"):
        x, z = F[f"stair_{tag}_top"]
        S.entry(f"terr_stair_{tag}", x, F["terr_front"] - 1.0, y=ty)


def tree(x, z, y, h, r):
    m.lathe([(0.14, y), (0.12, y + h * 0.45)], 5, "trunk", cx=x, cz=z, cap=False)
    m.lathe([(0.0, y + h * 0.35), (r * 0.8, y + h * 0.45), (r, y + h * 0.65), (r * 0.7, y + h * 0.85), (0.0, y + h)], 7, "leaf", cx=x, cz=z, cap=False)


def forecourt_trees():
    """Plate 14: four trees a side in a row running outward, each in a square pit, the innermost in line with the wings' inner faces; none on the band before the centre.
    Their kind not read (C)."""
    ty = V["terr_y"]
    zt = F["terr_front"] - 4.0
    for sx in (-1, 1):
        for k, x in enumerate((6.0, 8.6, 11.2, 13.8)):
            z = zt + 0.4 * k
            m.box(sx * x - 0.6, sx * x + 0.6, ty, ty + 0.12, z - 0.6, z + 0.6, "marble")
            tree(sx * x, z, ty + 0.12, 5.6 - 0.2 * k, 1.35)
            S.FOOTPRINTS.append(rect(sx * x - 0.6, sx * x + 0.6, z - 0.6, z + 0.6))


def hall():
    """The hall (S603's 28 x 21 m): an inverted 凹 (S310) on a base 1.2 m high: two wings with chamfered corners come forward one bay; the centre block between them;
    the body behind. Grey brick dressed with white marble (S02 p.155)."""
    ty = V["terr_y"]
    yb = ty + V["base_h"]  # the hall's floor
    F["yb"] = yb
    hw, hd = V["hall_w"] / 2, V["hall_d"]
    ch, wd, rc = V["wing_ch"], V["wing_d"], V["recess"]
    cw = V["ctr_w"] / 2
    yc = ty + V["cornice"]
    # the outline: front W->E, round the wings' chamfers, into the recess and out again; the back
    outline = [(-hw, -ch), (-hw + ch, 0.0), (-cw - ch, 0.0), (-cw, -ch), (-cw, -rc), (cw, -rc), (cw, -ch), (cw + ch, 0.0), (hw - ch, 0.0), (hw, -ch), (hw, -hd), (-hw, -hd)]
    # the base: the outline less the recess's inside, 0.4 m out, its top the floor; three flights up from the recess (plate 14: on the axis and before the side openings)
    from shapely.geometry import Polygon
    bpoly = Polygon(outline).buffer(0.4, join_style=2)
    base = [(float(x), float(z)) for x, z in list(bpoly.exterior.coords)[:-1]]
    m.prism(base, ty - 0.05, yb - 0.12, "marble")
    m.prism(base, yb - 0.12, yb, "marble")
    S.FOOTPRINTS.append(base)
    zb0 = -rc + 0.4  # the base's front edge in the recess
    nst = 8
    for x0, x1, tag in ((-1.3, 1.3, "C"), (-V["cwin_x"] - 0.85, -V["cwin_x"] + 0.85, "W"), (V["cwin_x"] - 0.85, V["cwin_x"] + 0.85, "E")):
        for k in range(nst):
            z0 = zb0 + 0.3 * k
            m.prism(rect(x0, x1, z0, z0 + 0.3), ty - 0.05, yb - (k + 1) * V["base_h"] / nst, "step")
        if tag == "C":
            for sx in (-1, 1):  # the flight's cheeks
                m.prism(rect(sx * 1.3 - 0.15, sx * 1.3 + 0.15, zb0, zb0 + 0.3 * nst)[::(1 if sx > 0 else 1)], ty - 0.05, yb - 0.3, "marble")
    S.kp("hall_step_C", (0.0, ty, zb0 + 0.3 * nst))
    S.entry("door_C", 0.0, zb0 + 0.3 * nst + 0.6, y=ty)
    # ---- the wings
    for sx, tag in ((-1, "W"), (1, "E")):
        xo, xi = sx * hw, sx * cw
        f0, f1 = sorted(((xo - sx * ch), (xi + sx * ch)))
        mid = (f0 + f1) / 2
        Wf = f1 - f0
        # the front face: one big window on a carved sill block, paired pilasters, festoons (plate 14)
        wall((f0, 0.0), (f1, 0.0), yb, yc, [(Wf / 2, V["win_w"], V["win_sill"] - V["base_h"], V["win_h"], V["win_w"] / 2, "win", "pediment")], "doc", cornice=yc, pil=(0.4, Wf - 0.4))
        m.push(f0, 0, 0.0)
        for s in (0.4, Wf - 0.4):
            m.box(s - 0.09, s + 0.09, yc - 3.6, yc - 1.4, 0.2, 0.3, "sculpt", skip=("back",))  # the hanging drops
        m.box(Wf / 2 - 0.9, Wf / 2 + 0.9, yb + V["win_sill"] - V["base_h"] - 0.55, yb + V["win_sill"] - V["base_h"] - 0.2, 0.0, 0.25, "sculpt", skip=("back",))  # the sill block
        m.pop()
        # the chamfers, each with its own pilaster (plate 14): the outline's segments either side of the front, in its order (outward normal to the south-west or -east)
        chs = [((-hw, -ch), (-hw + ch, 0.0)), ((-cw - ch, 0.0), (-cw, -ch))] if sx < 0 else [((cw, -ch), (cw + ch, 0.0)), ((hw - ch, 0.0), (hw, -ch))]
        for a, b in chs:
            wall(a, b, yb, yc, [], "doc", cornice=yc, pil=(math.hypot(ch, ch) / 2,))
        # the inner side face (towards the centre): one window bay, seen on plate 14
        inner = ((xi, -ch), (xi, -rc)) if sx < 0 else ((xi, -rc), (xi, -ch))
        wall(inner[0], inner[1], yb, yc, [((rc - ch) / 2, V["win_w"] * 0.9, V["win_sill"] - V["base_h"], V["win_h"], V["win_w"] * 0.45, "win", "scroll")], "doc", cornice=yc)
        # the outer side face: carried round from the front, fill
        outer = ((xo, -ch), (xo, -wd - 4.0)) if sx > 0 else ((xo, -wd - 4.0), (xo, -ch))
        wall(outer[0], outer[1], yb, yc, even_windows(wd + 4.0 - ch, 3, V["win_w"], V["win_sill"] - V["base_h"], V["win_h"], margin=0.8), "fill", cornice=yc)
        S.kp(f"wing_{tag}_foot_SW", (f0, yb, 0.0))
        S.kp(f"wing_{tag}_foot_SE", (f1, yb, 0.0))
        S.kp(f"wing_{tag}_cornice_SW", (f0, yc, 0.5))
        S.kp(f"wing_{tag}_cornice_SE", (f1, yc, 0.5))
        S.kp(f"wing_{tag}_win_head", (mid, yb + V["win_sill"] - V["base_h"] + V["win_h"], 0.0))
        S.kp(f"wing_{tag}_win_sill", (mid, yb + V["win_sill"] - V["base_h"], 0.0))
        # the wing's low roof of eight slopes over its chamfered plan (S603 p.133), flame finials over the corner pilasters, the deck, its balustrade, the lantern
        zc = -wd / 2
        lw = V["lan_w"] / 2
        yl = ty + V["lan_foot"]
        e = 0.5
        x0, x1 = sorted((xo, xi))
        c2 = ch + e * 0.4
        lo = [(x0 - e + c2, e), (x1 + e - c2, e), (x1 + e, e - c2), (x1 + e, -wd - e + c2), (x1 + e - c2, -wd - e), (x0 - e + c2, -wd - e), (x0 - e, -wd - e + c2), (x0 - e, e - c2)]
        dk = lw + 0.6
        hi = [(mid - dk + 0.4, zc + dk), (mid + dk - 0.4, zc + dk), (mid + dk, zc + dk - 0.4), (mid + dk, zc - dk + 0.4), (mid + dk - 0.4, zc - dk), (mid - dk + 0.4, zc - dk), (mid - dk, zc - dk + 0.4), (mid - dk, zc + dk - 0.4)]
        md = [((p[0] + q[0]) / 2, (p[1] + q[1]) / 2) for p, q in zip(lo, hi)]
        m.frustum(lo, md, yc, yc + (yl - yc) * 0.62, "roof")
        m.frustum(md, hi, yc + (yl - yc) * 0.62, yl - 0.05, "roof")
        m.flat(lo, yc, "roofedge")
        m.flat(hi, yl - 0.05, "marble")
        for s in (f0 + 0.4, f1 - 0.4):  # the flame finials over the front pilasters (plate 14)
            m.lathe([(0.22, yc), (0.22, yc + 0.25), (0.1, yc + 0.4), (0.2, yc + 0.7), (0.0, yc + 1.15)], 6, "marble", cx=s, cz=0.25, cap=False)
        dsq = [(mid - dk, zc + dk), (mid + dk, zc + dk), (mid + dk, zc - dk), (mid - dk, zc - dk)]
        P_.rail(dsq + [dsq[0]], yl - 0.05, h=0.75, posts=1.5)
        S.kp(f"lantern_{tag}_rail_L", (mid - dk, yl + 0.7, zc + dk))
        S.kp(f"lantern_{tag}_rail_R", (mid + dk, yl + 0.7, zc + dk))
        ye = ty + V["lan_eave"]
        yk = ty + V["lan_clock"]
        m.box(mid - lw, mid + lw, yl - 0.05, ye - 0.35, zc - lw, zc + lw, "wall")
        for k in range(4):  # a clock face on every side, framed pilasters at the corners
            m.push(mid, 0, zc, k * math.pi / 2)
            m.push(0, 0, lw)
            P_.oval(0.0, yk, 0.75, 0.75, n=18)
            m.box(-0.55, 0.55, yk - 0.55, yk + 0.55, 0.06, 0.08, "clock", skip=("back",))
            m.box(-0.03, 0.03, yk, yk + 0.45, 0.08, 0.11, "door", skip=("back",))
            m.box(0.0, 0.32, yk - 0.03, yk + 0.03, 0.08, 0.11, "door", skip=("back",))
            for s in (-lw + 0.15, lw - 0.15):
                m.box(s - 0.15, s + 0.15, yl, ye - 0.35, 0.0, 0.1, "marble", skip=("back",))
            m.pop()
            m.pop()
        m.box(mid - lw - 0.25, mid + lw + 0.25, ye - 0.35, ye, zc - lw - 0.25, zc + lw + 0.25, "marble")
        S.kp(f"lantern_{tag}_clock", (mid, yk, zc + lw + 0.08))
        ytop = ty + V["lan_top"]
        lr = P_.roof_hip(mid, zc, 1.5, 1.5, ye, ytop - 1.4, n=5, lift=0.35, ridge_y=0.05, ends=False)
        m.box(mid - 0.3, mid + 0.3, ytop - 1.45, ytop - 1.15, zc - 0.3, zc + 0.3, "marble")
        m.lathe([(0.25, ytop - 1.15), (0.32, ytop - 0.8), (0.14, ytop - 0.55), (0.24, ytop - 0.3), (0.0, ytop)], 8, "ridge", cx=mid, cz=zc, cap=False)
        S.kp(f"lantern_{tag}_top", (mid, ytop, zc))
        S.kp(f"lantern_{tag}_eave_L", lr["eaves"][(-1, 1)])
        S.kp(f"lantern_{tag}_eave_R", lr["eaves"][(1, 1)])
    # ---- the centre block: the clock gate's front, a door-like opening each side
    zc0 = -rc
    clock_gate(zc0, ty, yb, yc)
    holes = [(cw - V["cwin_x"], V["cwin_w"], 0.0, V["door_h"] - 0.2, V["cwin_w"] / 2, "win", None), (cw + V["cwin_x"], V["cwin_w"], 0.0, V["door_h"] - 0.2, V["cwin_w"] / 2, "win", None),
             (cw, V["door_w"], 0.0, V["door_h"], V["door_w"] / 2, "door", None)]
    wall((-cw, zc0), (cw, zc0), yb, yc, holes, "doc", cornice=yc, pil=(0.35, 2 * cw - 0.35))
    for sx, tag in ((-1, "W"), (1, "E")):
        xw = sx * V["cwin_x"]
        S.kp(f"ctrwin_{tag}_head", (xw, yb + V["door_h"] - 0.2, zc0))
        S.kp(f"ctrwin_{tag}_foot_L", (xw - V["cwin_w"] / 2, yb, zc0))
        S.kp(f"ctrwin_{tag}_foot_R", (xw + V["cwin_w"] / 2, yb, zc0))
        # the opening's hood: two stepped halves and a shell keystone (P0179, P0772), a leafy crest over it (plate 14)
        m.push(xw, 0, zc0)
        top = yb + V["door_h"] - 0.2 + 0.2
        for sg in (-1, 1):  # the hood's two stepped halves, on the frame's arch
            m.box(sg * 0.15 if sg > 0 else -(V["cwin_w"] / 2 + 0.3), (V["cwin_w"] / 2 + 0.3) if sg > 0 else -0.15, top - 0.05, top + 0.12, 0.0, 0.24, "sculpt", skip=("back",))
            m.box(sg * 0.15 if sg > 0 else -(V["cwin_w"] / 2 + 0.1), (V["cwin_w"] / 2 + 0.1) if sg > 0 else -0.15, top + 0.12, top + 0.3, 0.0, 0.2, "sculpt", skip=("back",))
        for k in range(6):
            t0, t1 = math.pi * k / 6, math.pi * (k + 1) / 6
            m.poly([(0.0, top + 0.1, 0.24), (0.4 * math.cos(t0), top + 0.1 + 0.55 * math.sin(t0), 0.24), (0.4 * math.cos(t1), top + 0.1 + 0.55 * math.sin(t1), 0.24)], "sculpt")
        m.pop()
    S.kp("ctr_foot_L", (-cw, yb, zc0))
    S.kp("ctr_foot_R", (cw, yb, zc0))
    S.kp("ctr_cornice_L", (-cw, yc, zc0 + 0.5))
    S.kp("ctr_cornice_R", (cw, yc, zc0 + 0.5))
    S.kp("door_head", (0.0, yb + V["door_h"], zc0))
    S.kp("door_sill", (0.0, yb, zc0))
    # ---- the body behind and the centre block's sides above the wings' roofs: carried round (fill)
    zb_ = -hd
    wall((hw, zb_), (-hw, zb_), yb, yc, even_windows(2 * hw, 7, V["win_w"], 0.2, V["win_h"]), "fill", cornice=yc)
    for sx in (-1, 1):
        a, b = ((sx * hw, -wd - 4.0), (sx * hw, zb_)) if sx > 0 else ((sx * hw, zb_), (sx * hw, -wd - 4.0))
        wall(a, b, yb, yc, even_windows(hd - wd - 4.0, 2, V["win_w"], 0.2, V["win_h"]), "fill", cornice=yc)
    m.cls = "fill"
    m.box(-hw + 0.3, hw - 0.3, yc - 0.3, yc, zb_ + 0.3, -wd + 0.3, "wall", skip=("bottom",))
    P_.roof_hip(0.0, (-wd + zb_) / 2, hw + 0.5, (hd - wd) / 2 + 0.5, yc, ty + V["body_ridge"], n=5, lift=0.3, ridge_y=0.3)
    m.cls = "doc"
    # the centre's tiered roofs
    tiered_roof(zc0, ty, yc)
    S.FOOTPRINTS.append(outline)


def clock_gate(z0, ty, yb, yc):
    """The clock gate (plate 14; P0183 of 1873 with the attic whole, P0190 of 1876, the ruins since): two carved columns on pedestals before plain piers, a lion on each
    pedestal (plate 14 only: gone by 1873), an entablature block over each breaking forward, the door's carved hood; over the cornice the attic with the clock wheel, its
    arched moulding and the crest, big scrolls at its foot running out over the blocks."""
    S_ = V["S"] / 2
    r = V["col_r"]
    yp = ty + V["col_ped"]
    ytop = ty + V["col_top"]
    d = z0 + V["col_d"]
    pw, bw = V["ped_w"] / 2, V["blk_w"] / 2
    for sx, tag in ((-1, "W"), (1, "E")):
        x = sx * S_
        # the plain pier behind the column, bonded into the wall
        m.box(x - 0.75, x + 0.75, yb, yc - 0.9, z0, z0 + 0.25, "marble", skip=("back",))
        # the pedestal on its stepped plinth (plate 14: three tiers into the forecourt)
        m.box(x - pw - 0.25, x + pw + 0.25, ty - 0.05, ty + 0.2, d - pw - 0.25, d + pw + 0.25, "marble")
        m.box(x - pw, x + pw, ty + 0.2, yp - 0.15, d - pw, d + pw, "marble")
        m.box(x - pw - 0.1, x + pw + 0.1, yp - 0.15, yp, d - pw - 0.1, d + pw + 0.1, "marble")
        m.push(x, 0, d + pw)
        P_.cartouche(0.0, (ty + yp) / 2 + 0.05, pw * 1.2, 0.45)
        m.pop()
        # the shaft wound with foliage (plate 14, P0179): bands of relief on a turned shaft, a tall capital with volutes and a mask (P0183)
        prof = [(r + 0.08, yp), (r + 0.08, yp + 0.3), (r, yp + 0.4)]
        ys0, ys1 = yp + 0.4, ytop - V["cap_h"]
        n = 8
        for k in range(n):
            y0 = ys0 + (ys1 - ys0) * k / n
            y1 = ys0 + (ys1 - ys0) * (k + 1) / n
            prof += [(r + 0.07, y0 + (y1 - y0) * 0.35), (r + 0.02, y0 + (y1 - y0) * 0.75), (r, y1)]
        prof += [(r + 0.1, ys1 + 0.15), (r + 0.25, ytop - 0.55), (r + 0.5, ytop - 0.2), (r + 0.55, ytop)]
        m.lathe(prof, 10, "sculpt", cx=x, cz=d)
        for k in range(4):  # the capital's volutes at its corners
            a = math.pi / 4 + k * math.pi / 2
            vx, vz = x + (r + 0.42) * math.cos(a), d + (r + 0.42) * math.sin(a)
            m.box(vx - 0.13, vx + 0.13, ytop - 0.6, ytop - 0.1, vz - 0.13, vz + 0.13, "sculpt")
        # the entablature block over the column, proud of the wall and of the cornice (P0179, P0183, P0216)
        m.box(x - bw + 0.2, x + bw - 0.2, ytop, ytop + 0.35, z0, d + bw - 0.2, "marble")
        m.box(x - bw + 0.1, x + bw - 0.1, ytop + 0.35, yc - 0.35, z0, d + bw - 0.1, "wall")
        m.box(x - bw, x + bw, yc - 0.35, yc, z0, d + bw, "marble")
        S.kp(f"col_{tag}_cap", (x, ytop, d + r + 0.5))
        S.kp(f"col_{tag}_base", (x, yp, d + r + 0.08))
        S.kp(f"col_{tag}_ped_foot", (x, ty, d + pw + 0.25))
        S.kp(f"ent_{tag}_top", (x, yc, d + bw))
        # the seated lion on the pedestal, before the shaft (plate 14; none on the photographs of 1873-76)
        lz = d + pw - 0.35
        m.box(x - 0.3, x + 0.3, yp, yp + 0.45, lz - 0.35, lz + 0.15, "sculpt")
        m.lathe([(0.22, yp + 0.4), (0.26, yp + 0.6), (0.2, yp + 0.8), (0.0, yp + 0.88)], 7, "sculpt", cx=x, cz=lz + 0.05)
    # the door's carved frame and its tall foliate hood (plate 14; P0183: a deep frame, broken by 1873)
    dw, dh = V["door_w"] / 2, V["door_h"]
    m.push(0.0, 0, z0)
    hood = arc_pts(-dw - 0.5, dw + 0.5, yb + dh - dw, dw + 0.5, 8)
    for p0, p1 in zip(hood[:-1], hood[1:]):
        m.poly([(p0[0], p0[1], 0.22), (p1[0], p1[1], 0.22), (p1[0], p1[1] + 0.35, 0.22), (p0[0], p0[1] + 0.35, 0.22)], "sculpt")
    for s in (-dw - 0.4, dw + 0.4):
        m.box(s - 0.22, s + 0.22, yb, yb + dh - dw, 0.0, 0.25, "sculpt", skip=("back",))
    # the hood over the arch: a segmental cartouche with scrolled ends (P0183: a deep carved hood, broken by 1873; plate 14: a foliate cartouche rising over the arch)
    hc = arc_pts(-dw - 0.75, dw + 0.75, yb + dh + 0.35, 0.95, 10)
    m.poly([(p[0], p[1], 0.3) for p in hc] + [(dw + 0.75, yb + dh + 0.1, 0.3), (-dw - 0.75, yb + dh + 0.1, 0.3)], "sculpt")
    for sg in (-1, 1):
        m.box(sg * (dw + 0.75) - 0.2, sg * (dw + 0.75) + 0.2, yb + dh + 0.05, yb + dh + 0.5, 0.0, 0.36, "sculpt", skip=("back",))
    m.pop()
    # the attic: pilasters either side of the wheel, the wheel, the arched moulding, the crest
    aw = V["attic_w"] / 2
    ya, yt, ycr = ty + V["clock_y"], ty + V["attic_top"], ty + V["crest_top"]
    zf = z0 + 0.2
    rr = V["clock_r"]
    ysp = ya  # the arch springs at the wheel's centre
    m.box(-aw, aw, yc, ysp, z0 - 0.8, zf, "wall")
    for s in (-aw + 0.25, aw - 0.25):
        m.box(s - 0.25, s + 0.25, yc, ysp, zf, zf + 0.2, "marble")
        m.box(s - 0.32, s + 0.32, ysp - 0.25, ysp, zf, zf + 0.3, "marble")
    outer = arc_pts(-aw, aw, ysp, yt - ysp, 12)
    inner = arc_pts(-aw + 0.45, aw - 0.45, ysp, yt - ysp - 0.45, 12)
    for (p0, q0), (p1, q1) in zip(zip(outer[:-1], inner[:-1]), zip(outer[1:], inner[1:])):
        m.poly([(p0[0], p0[1], zf + 0.25), (p1[0], p1[1], zf + 0.25), (q1[0], q1[1], zf + 0.25), (q0[0], q0[1], zf + 0.25)], "marble")
        m.poly([(p0[0], p0[1], z0 - 0.8), (p1[0], p1[1], z0 - 0.8), (p1[0], p1[1], zf + 0.25), (p0[0], p0[1], zf + 0.25)], "marble")
        m.poly([(p0[0], p0[1], z0 - 0.8), (p0[0], ysp, z0 - 0.8), (p1[0], ysp, z0 - 0.8), (p1[0], p1[1], z0 - 0.8)], "wall")
    m.poly([(p[0], p[1], zf) for p in inner], "wall")  # the tympanum behind the wheel
    m.push(0.0, 0, zf)
    P_.oval(0.0, ya, rr, rr, n=20, d=0.05)
    for k in range(8):  # the rosette's spokes (P0183)
        t = math.pi * k / 8
        c_, s_ = math.cos(t) * (rr - 0.14), math.sin(t) * (rr - 0.14)
        m.poly([(c_, ya + s_, 0.2), (-c_, ya - s_, 0.2), (-c_, ya - s_ + 0.06, 0.2), (c_, ya + s_ + 0.06, 0.2)], "sculpt")
    m.box(-0.18, 0.18, ya - 0.18, ya + 0.18, 0.1, 0.26, "sculpt", skip=("back",))
    m.box(-aw + 0.6, aw - 0.6, yc + 0.15, ya - rr - 0.15, 0.0, 0.1, "sculpt", skip=("back",))  # the carved panel under the wheel
    for k in range(7):  # the leafy crest over the moulding
        t0, t1 = math.pi * k / 7, math.pi * (k + 1) / 7
        m.poly([(0.0, yt - 0.15, 0.3), (0.85 * math.cos(t0), yt - 0.15 + (ycr - yt + 0.15) * math.sin(t0), 0.3), (0.85 * math.cos(t1), yt - 0.15 + (ycr - yt + 0.15) * math.sin(t1), 0.3)], "sculpt")
    # the big C-scrolls at the attic's foot, running out over the entablature blocks (P0183, plate 14)
    sxp = V["scroll_x"]
    for sx in (-1, 1):
        pts = [(sx * aw, yc + 1.9), (sx * (aw + 0.25), yc + 1.2), (sx * (aw + 0.75), yc + 0.6), (sx * (sxp - 0.5), yc + 0.35), (sx * sxp, yc + 0.45), (sx * (sxp + 0.1), yc + 0.15), (sx * (sxp - 0.2), yc), (sx * aw, yc)]
        m.poly([(p[0], p[1], 0.18) for p in pts], "marble")
        m.poly([(p[0], p[1], -0.4) for p in pts], "marble")
        for p0, p1 in zip(pts, pts[1:] + pts[:1]):
            m.poly([(p0[0], p0[1], 0.18), (p1[0], p1[1], 0.18), (p1[0], p1[1], -0.4), (p0[0], p0[1], -0.4)], "marble")
    m.pop()
    S.kp("clock_C", (0.0, ya, zf + 0.2))
    S.kp("clock_arch_top", (0.0, yt, zf + 0.25))
    S.kp("clock_crest_top", (0.0, ycr, zf + 0.3))
    S.kp("attic_scroll_L", (-sxp - 0.1, yc + 0.2, zf + 0.18))
    S.kp("attic_scroll_R", (sxp + 0.1, yc + 0.2, zf + 0.18))


def tiered_roof(z0, ty, yc):
    """The centre's roofs in tiers (plate 14; S603 p.133: 'central hipped Chinese roof of 3 stepped levels, curved hips, Chinese tiles'): a hipped roof of fish-scale tiles
    as wide as the centre block from the cornice, the steeper ribbed main hipped roof above it, its front slope pierced by the attic, a pedestal band with scrolls and the
    vase-like crown."""
    cw, cd = V["ctr_w"] / 2, V["ctr_d"]
    zc = z0 - cd / 2
    ys, ye, ya, yk = ty + V["skirt_top"], ty + V["roof_eave"], ty + V["roof_apex"], ty + V["crown"]
    # the low band over the cornice, round the block (plate 14)
    yc0 = yc
    m.box(-cw + 0.1, cw - 0.1, yc, yc + V["band_h"], z0 - cd + 0.1, z0 - 0.1, "wall", skip=("bottom",))
    m.box(-cw, cw, yc + V["band_h"] - 0.15, yc + V["band_h"], z0 - cd, z0 + 0.05, "marble", skip=("bottom",))
    yc = yc + V["band_h"]
    e = 0.45
    rw = V["roof_w"] / 2
    lo = [(-cw - e, z0 + e), (cw + e, z0 + e), (cw + e, z0 - cd - e), (-cw - e, z0 - cd - e)]
    hi = [(-rw + 0.9, zc + cd / 2 - 1.6), (rw - 0.9, zc + cd / 2 - 1.6), (rw - 0.9, zc - cd / 2 + 1.6), (-rw + 0.9, zc - cd / 2 + 1.6)]
    md = [(a[0] * 0.55 + b[0] * 0.45, a[1] * 0.55 + b[1] * 0.45) for a, b in zip(lo, hi)]
    m.frustum(lo, md, yc - 0.05, yc + (ys - yc) * 0.5, "scale")
    m.frustum(md, hi, yc + (ys - yc) * 0.5, ys, "scale")
    m.flat(lo, yc - 0.05, "roofedge")
    for (x, z) in lo:  # the curled corner tips
        m.box(x - 0.2, x + 0.2, yc - 0.05, yc + 0.55, z - 0.2, z + 0.2, "ridge")
    m.box(hi[0][0], hi[1][0], ys - 0.05, ye, hi[2][1], hi[0][1], "wall")
    S.kp("scale_eave_L", (lo[0][0], yc + 0.5, lo[0][1]))
    S.kp("scale_eave_R", (lo[1][0], yc + 0.5, lo[1][1]))
    yc = yc0
    r = P_.roof_hip(0.0, zc, rw, cd / 2 - 0.9, ye, ya, n=6, lift=0.45, ridge_y=0.1, ends=False)
    S.kp("roof_C_eave_L", r["eaves"][(-1, 1)])
    S.kp("roof_C_eave_R", r["eaves"][(1, 1)])
    S.kp("roof_C_apex", (0.0, ya, zc))
    # the pedestal band with scrolls and the crown (plate 14)
    m.box(-1.2, 1.2, ya - 0.3, ya + 0.7, zc - 1.2, zc + 1.2, "marble")
    for sx in (-1, 1):
        m.poly([(sx * 1.2, ya + 0.7, zc + 1.21), (sx * 1.9, ya - 0.1, zc + 1.21), (sx * 1.2, ya - 0.1, zc + 1.21)], "marble")
    m.lathe([(0.6, ya + 0.7), (0.7, ya + 1.0), (0.35, ya + 1.25), (0.62, (ya + yk) / 2 + 0.3), (0.3, yk - 0.4), (0.18, yk - 0.2), (0.0, yk)], 10, "ridge", cx=0.0, cz=zc, cap=False)
    S.kp("crown_top", (0.0, yk, zc))


def frame_from_dashuifa():
    """The front of the terrace and the heads of 大水法's stairs, from 大水法's model (Round 15), in this frame."""
    s10 = json.load(open(ROOT / "models/XY10-da-shuifa/summary.json", encoding="utf-8"))
    j10 = json.load(open(ROOT / "models/XY10-da-shuifa/joints.json", encoding="utf-8"))
    p10, r10 = s10["position"], s10["rotationY"]
    c, s = math.cos(r10), math.sin(r10)
    to_scene10 = lambda x, z: (p10[0] + c * x + s * z, p10[2] - s * x + c * z)
    ax = S.to_local(*to_scene10(0.0, 0.0))
    F["axis_dx"] = ax[0]
    F["dz_turn"] = r10 - S.rot
    return to_scene10, j10, p10


def build():
    global S, m, P_
    S = Site("XY09-M44")
    to_scene10, j10, p10 = frame_from_dashuifa()
    # move the origin along the front onto 大水法's axis
    sx_, _, sz_ = S.to_scene((F["axis_dx"], 0.0, 0.0))
    S.pos = [round(sx_, 3), S.pos[1], round(sz_, 3)]
    F["terr_front"] = round(S.to_local(*to_scene10(0.0, -4.2))[1], 3)  # 大水法's terrace face (dashuifa.py stair(): zt)
    ent = {e["name"]: e["scene"] for e in j10["entries"]}
    for tag in ("W", "E"):
        e = ent[f"stair_{tag}_top"]
        F[f"stair_{tag}_top"] = S.to_local(e[0], e[2])
    F["court_y"] = p10[1] - S.pos[1]
    m = Mesh(COL)
    S.m = m
    P_ = Parts(m, rail_h=V["rail_h"], baluster_segs=4)
    m.cls = "doc"
    terrace()
    forecourt_trees()
    hall()


def summary(tris, fill, size):
    ty = V["terr_y"]
    rows = [
        ["Terrace", f"{V['terr_w']:g} × {V['terr_d']:g} m (S603, survey, B; which way is not stated: Q67), its top {ty:g} m above its foot, where 大水法's stairs arrive (Round 15, C, Q232); retaining walls of piers and long rusticated stones (S603, B; the pier spacing assumed); paved; the front balustrade with urns, the side balustrades, eight trees in square pits (plate 14, C); a stair down at the back (assumed, for reach)"],
        ["Hall", f"{V['hall_w']:g} × {V['hall_d']:g} m (S603's post grid, B; Q67), an inverted 凹 (S310, B): two wings with chamfered corners come {V['recess']:g} m forward of the centre block (plate 14, C); on a base {V['base_h']:g} m high (P0216, P0757, C); grey brick dressed with white marble (S02 p.155, B); the cornice {V['cornice']:g} m above the terrace (P0183, C)"],
        ["Clock gate", f"the door ({V['door_w']:g} × {V['door_h']:g} m) between two carved columns {V['S']:g} m apart on pedestals, their capitals {V['col_top']:g} m above the terrace, an entablature block over each standing proud (P0183 of 1873, P0216, P0757, C); a lion on each pedestal (plate 14 only, C); the attic with the clock wheel, its arched moulding and crest {V['crest_top']:g} m above the terrace (P0183, plate 14: they agree, C); a door-like opening either side (P0179, P0216, C)"],
        ["Wings and lanterns", f"a big window on a carved sill block in each wing's front, pilasters on every face and chamfer; a low roof of eight slopes, a deck with a balustrade and a square lantern with a clock face on every side, its finial {V['lan_top']:g} m above the terrace (plate 14; S603 p.133, C)"],
        ["Roofs", f"over the centre: a fish-scale hipped roof as wide as the block, the main hipped roof to {V['roof_apex']:g} m pierced by the attic, a pedestal band and the crown at {V['crown']:g} m (plate 14; S603 p.133, C); the body behind under a hipped Chinese roof (S603, B; its form assumed); glazed green tile (the 2016 dig found glazed fittings, S153; the colour assumed, Q69)"],
        ["Scale", f"the front's module is the columns' spacing, {V['S']:g} m: plate 14's ratios against Durand's 28 m and P0216's door (C); the dossier's 4.2 m made the whole front 18 m. Heights from the photographs where they show the part (the order), from plate 14 scaled by the attic where they agree (the roofs)"],
        ["Assumed", "the hall's rear and end faces, the body behind, the terrace's south face behind 大水法 and the back stair: carried round from the front (C, the pale tint with conf=1)"],
    ]
    return {
        "id": "XY09", "aliases": [], "name": "远瀛观 Yuanyingguan", "glb": "model.glb", "position": S.pos, "rotationY": S.rot,
        "line": "Modelled from plate 14 of 1783-86, Ohlmer's and Piry's photographs of the clock gate (1873, 1876), the ruin photographs since 1900, Durand's survey (S603) and the plan S01; every figure is a reading (C) unless the row says otherwise. The rear, the ends and the body behind the centre are carried round (assumed).",
        "rows": rows,
        "caption": {"frontage_m": V["hall_w"], "depth_m": V["hall_d"], "eave_m": round(ty + V["cornice"], 1), "ridge_m": round(ty + V["crown"], 1), "assumed": True, "confidence": "C"},
        "hides": [],
        "tris": tris, "fill_tris": fill, "glb_bytes": size,
    }


def main():
    build()
    size = m.write_glb(HERE / "model.glb", "XY09 远瀛观 Yuanyingguan", extras={"id": "XY09"})
    tris = m.count()
    prims = {k: len(v["idx"]) // 3 for k, v in sorted(m.prims.items())}
    fill = sum(n for k, n in prims.items() if k.endswith("~fill"))
    S.write(HERE, "XY09", ["XY09"], P, "x east along the front, y up from the terrace's foot at the hall's box, z south (out of the front, towards 大水法); the origin on 大水法's axis at the wings' front plane; metres", summary(tris, fill, size))
    print(f"model.glb {size / 1e6:.2f} MB, {tris} triangles ({fill} fill), {P_.balusters} balusters, {len(S.KP)} key points, {len(S.JOINTS)} joints, {len(S.ENTRIES)} entries; position {S.pos} rotY {S.rot}; terrace front z {F['terr_front']}, stair heads {F['stair_W_top']}, {F['stair_E_top']}")


if __name__ == "__main__":
    main()
