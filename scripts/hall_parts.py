"""The hall kit in Python (Round 17): a Qing timber hall drawn from numbers into a detailed model's mesh (scripts/model_mesh.py), with the shapes of the browser's kit
(site/reconstruction/kit3d.js, Round 11), so that a compound modelled from its evidence looks like the halls around it. Imported, not run.

First used by 含经堂 Hanjingtang (models/CC02-hanjing-tang/, Round 17); the recipe for the later Chinese compounds (docs/METHOD.md).
What it ports from kit3d.js, part for part: the platform 台基 and its coping, the flights 踏跺 (here with their side slabs 垂带), the balustrade, the columns at the bays,
the beam ring 额枋 and on 大式 halls the bracket band 斗拱 stepping out, the doors 隔扇 and windows 槛窗 over a sill wall, recessed behind their frames with lattice bars,
the transom, the 硬山 gable walls, the roof (庑殿 wd, 歇山 xs, 硬山 ys, 悬山 xu, 攒尖 cj; rolled 卷棚 or with a ridge; the 举架 profile; the corner lift 起翘), the double eave 重檐,
a second storey with a balcony 平座. New here: the palace wall 宫墙 with its coping, the screen wall 影壁, the glazed archway 琉璃牌楼, a gallery 游廊 with a wall on one side,
a rock pile, paving.

Frame of a hall: s (x) along its front, y up, q (z) out of the front; `Hall.at(cx, cz, rot)` pushes it into the model's frame (rot as in Mesh.push: 0 faces +z, pi/2 faces +x).
Every part takes the mesh's current grade class (`mesh.cls`: doc or fill); the caller sets it before each part.
Materials it uses (the caller's colour table must hold them): lacquer, lacquer_dark, wall, plaster, glass_lattice, sill, band, bracket, bandred, platform, coping, step, marble,
underside, fascia, wallred, tile_<colour>, ridge_<colour>, rock, pave, gold.
"""

import math

import numpy as np

# 举架 by class, from eave to ridge (as scripts/kit1860.py JU)
JU = {"grand_hall": [0.5, 0.6, 0.75, 0.9], "main_hall": [0.5, 0.65, 0.85], "side_hall": [0.5, 0.65, 0.85], "gate_hall": [0.5, 0.65, 0.85], "small_house": [0.5, 0.7],
      "gallery": [0.5, 0.7], "storeyed_hall": [0.5, 0.7], "tower": [0.5, 0.65, 0.75, 0.9], "pavilion": [0.5, 0.7, 0.9]}


def profile(ju, curve=1.0):
    """kit3d.js profile(): the roof's height share at v (0 eave, 1 ridge), concave by the 举架 steps."""
    n = len(ju)
    ys = [0.0]
    for i in range(n):
        ys.append(ys[i] + ju[i] / n)
    top = ys[n]

    def f(v):
        x = min(max(v, 0.0), 1.0) * n
        i = min(int(math.floor(x)), n - 1)
        fr = x - i
        yv = (ys[i] + (ys[i + 1] - ys[i]) * fr) / top
        return min(max(v + (yv - v) * curve, 0.0), 1.0)
    return f


class HallKit:
    def __init__(self, mesh, ground=None):
        """ground(x, z) -> y: the walk surface in the model's frame (Site.gy), for the feet of flights and walls."""
        self.m = mesh
        self.ground = ground

    # ------------------------------------------------------------ frames
    def gy_local(self, s, q):
        """The ground under a point of the current local frame, in the model's y."""
        w = self.m.world((s, 0.0, q))
        return self.ground(float(w[0]), float(w[2])) if self.ground else 0.0

    def quad(self, a, b, c, d, mat):
        self.m.poly([a, b, c, d], mat)

    # ------------------------------------------------------------ the roof
    def roof(self, P, hx, hz, y0, y1, form="xs", rolled=False, ju=None, curve=1.0, liftK=1.0, tile="grey", edge=None, gable_mat="lacquer", near=True,
             gableX=None, gableFrom=0.0, ridge_mat=None):
        """kit3d.js roof(): P(x, y, z) maps the roof's frame (x along the ridge, z across) into the current frame. y0 the eave's edge, y1 the ridge."""
        m = self.m
        prof = profile(ju or JU["main_hall"], curve)
        band = min(0.12 * hz, 0.6) if rolled else 0.0
        yTop = y1 - 0.6 * band if rolled else y1
        Y = lambda v: y0 + (yTop - y0) * prof(v)
        nv = max(3, len(ju or JU["main_hall"]) + 1) if near else 2
        vb = 0.4 if form == "xs" else 1.0
        q = lambda v: hz - (hz - band) * v
        rHalf = max(hx - 0.85 * (hz - band), 0.05 * hx)

        def L(v):
            if form == "wd":
                return hx - (hx - rHalf) * v
            if form == "xs":
                return hx - (hz - band) * min(v, vb)
            return hx
        Lc = min(0.55, 0.04 * (hx + hz)) * liftK if form in ("wd", "xs") else 0.0
        up = lambda t, v: Lc * max(0.0, (abs(t) - 0.45) / 0.55) ** 2 * (1 - v) ** 2
        nu = min(10, max(4, round(hx / 2.2))) if near else 2
        nw = 4 if near else 2
        tmat, emat = f"tile_{tile}", (f"tile_{edge}" if edge else None)
        rmat = ridge_mat or f"ridge_{tile}"
        col = lambda j: emat if (emat and j == 0) else tmat
        for sg in (1, -1):
            for j in range(nv):
                v0, v1 = j / nv, (j + 1) / nv
                for i in range(nu):
                    t0, t1 = -1 + 2 * i / nu, -1 + 2 * (i + 1) / nu
                    pt = lambda t, v: P(t * L(v), Y(v) + up(t, v), sg * q(v))
                    m.poly([pt(t0, v0), pt(t1, v0), pt(t1, v1), pt(t0, v1)], col(j))
        if form in ("wd", "xs"):
            for sx in (1, -1):
                jMax = max(1, round(nv * vb))
                for j in range(jMax):
                    v0, v1 = j / jMax * vb, (j + 1) / jMax * vb
                    for i in range(nw):
                        w0, w1 = -1 + 2 * i / nw, -1 + 2 * (i + 1) / nw
                        pt = lambda w, v: P(sx * L(v), Y(v) + up(w, v), w * q(v))
                        m.poly([pt(w0, v0), pt(w1, v0), pt(w1, v1), pt(w0, v1)], col(j))
        arc = []
        if rolled:
            for k in range(5):
                t = k / 4
                arc.append((band * math.cos(math.pi * t), yTop + (y1 - yTop) * math.sin(math.pi * t)))
            Lr = L(1)
            for k in range(4):
                m.poly([P(-Lr, arc[k][1], arc[k][0]), P(Lr, arc[k][1], arc[k][0]), P(Lr, arc[k + 1][1], arc[k + 1][0]), P(-Lr, arc[k + 1][1], arc[k + 1][0])], tmat)

        def gable(xg, vFrom):
            nn = nv if near else 2
            pts = [(q(vFrom + (1 - vFrom) * j / nn), Y(vFrom + (1 - vFrom) * j / nn)) for j in range(nn + 1)]
            topPts = arc[1:-1] if rolled else [(0.0, yTop)]
            ring = pts + topPts + [(-z, y) for z, y in reversed(pts)]
            base = Y(vFrom)
            for sx in (1, -1):
                for k in range(len(ring) - 1):
                    m.poly([P(sx * xg, base, ring[k][0]), P(sx * xg, ring[k][1] - 0.02, ring[k][0]), P(sx * xg, ring[k + 1][1] - 0.02, ring[k + 1][0]), P(sx * xg, base, ring[k + 1][0])], gable_mat)
        if form == "xs":
            gable(L(vb), vb)
        if form in ("ys", "xu"):
            gable(gableX if gableX is not None else hx, gableFrom)
        if form == "xu" and near:
            for sx in (1, -1):
                for j in range(nv):
                    v0, v1 = j / nv, (j + 1) / nv
                    for sg in (1, -1):
                        m.poly([P(sx * hx, Y(v0) - 0.32, sg * q(v0)), P(sx * hx, Y(v0) + 0.02, sg * q(v0)), P(sx * hx, Y(v1) + 0.02, sg * q(v1)), P(sx * hx, Y(v1) - 0.32, sg * q(v1))], "lacquer_dark")
        if near:
            v1 = 1 / nv
            for sg in (1, -1):
                for i in range(nu):
                    t0, t1 = -1 + 2 * i / nu, -1 + 2 * (i + 1) / nu
                    pt = lambda t, v, dy: P(t * L(v), Y(v) + up(t, v) - dy, sg * q(v))
                    m.poly([pt(t0, 0, 0.22), pt(t1, 0, 0.22), pt(t1, v1, 0.22), pt(t0, v1, 0.22)], "underside")
                    m.poly([pt(t0, 0, 0), pt(t1, 0, 0), pt(t1, 0, 0.22), pt(t0, 0, 0.22)], "fascia")
            if form in ("wd", "xs"):
                for sx in (1, -1):
                    for i in range(nw):
                        w0, w1 = -1 + 2 * i / nw, -1 + 2 * (i + 1) / nw
                        pt = lambda w, v, dy: P(sx * L(v), Y(v) + up(w, v) - dy, w * q(v))
                        m.poly([pt(w0, 0, 0), pt(w1, 0, 0), pt(w1, 0, 0.22), pt(w0, 0, 0.22)], "fascia")
                        m.poly([pt(w0, 0, 0.22), pt(w1, 0, 0.22), pt(w1, v1 * vb, 0.22), pt(w0, v1 * vb, 0.22)], "underside")
            # ridges
            Lr, hr = L(1), min(0.9, max(0.3, 0.1 + 0.06 * hz))
            if not rolled and Lr > 0.3:
                yb = y1 - 0.05
                m.poly([P(-Lr, yb + hr, -0.16), P(Lr, yb + hr, -0.16), P(Lr, yb + hr, 0.16), P(-Lr, yb + hr, 0.16)], rmat)
                m.poly([P(-Lr, yb, 0.16), P(Lr, yb, 0.16), P(Lr, yb + hr, 0.16), P(-Lr, yb + hr, 0.16)], rmat)
                m.poly([P(Lr, yb, -0.16), P(-Lr, yb, -0.16), P(-Lr, yb + hr, -0.16), P(Lr, yb + hr, -0.16)], rmat)
                for sx in (1, -1):  # the end beasts 正吻, as blocks
                    x0, x1 = sx * Lr, sx * (Lr - 0.5)
                    m.poly([P(x0, yb, 0.2), P(x1, yb, 0.2), P(x1, yb + hr * 1.9, 0.2), P(x0, yb + hr * 1.7, 0.2)], rmat)
                    m.poly([P(x1, yb, -0.2), P(x0, yb, -0.2), P(x0, yb + hr * 1.7, -0.2), P(x1, yb + hr * 1.9, -0.2)], rmat)
                    m.poly([P(x0, yb + hr * 1.7, -0.2), P(x0, yb + hr * 1.7, 0.2), P(x1, yb + hr * 1.9, 0.2), P(x1, yb + hr * 1.9, -0.2)], rmat)

            def strip(pts, w):
                for a, b in zip(pts[:-1], pts[1:]):
                    m.poly([P(*a), P(*b), P(b[0], b[1] + w, b[2]), P(a[0], a[1] + w, a[2])], rmat)
            if form in ("wd", "xs"):
                for sx in (1, -1):
                    for sg in (1, -1):
                        strip([(sx * L(vb * j / nv), Y(vb * j / nv) + up(1, vb * j / nv), sg * q(vb * j / nv)) for j in range(nv + 1)], 0.22)
            if form in ("xs", "ys", "xu"):
                xv = L(vb) if form == "xs" else hx
                vf = vb if form == "xs" else 0.0
                for sx in (1, -1):
                    for sg in (1, -1):
                        strip([(sx * (xv - 0.15), Y(vf + (1 - vf) * j / nv), sg * q(vf + (1 - vf) * j / nv)) for j in range(nv + 1)], 0.2)

    def pyramid(self, hx, hz, y0, y1, sides=4, ju=None, tile="grey", edge=None, liftK=1.0, near=True):
        """kit3d.js pyramid(): a 攒尖 of n sides up to a finial, in the current frame."""
        m = self.m
        prof = profile(ju or JU["pavilion"], 1.0)
        Y = lambda v: y0 + (y1 - y0) * prof(v)
        if sides == 4:
            C = [(-hx, hz), (hx, hz), (hx, -hz), (-hx, -hz)]
        else:
            R = min(hx, hz) / math.cos(math.pi / sides)
            C = [(R * math.cos(math.pi / 2 + (k + 0.5) * 2 * math.pi / sides), R * math.sin(math.pi / 2 + (k + 0.5) * 2 * math.pi / sides)) for k in range(sides)]
        Lc = min(0.5, 0.06 * (hx + hz)) * liftK
        up = lambda t, v: Lc * max(0.0, (abs(t) - 0.4) / 0.6) ** 2 * (1 - v) ** 2
        nv, nu = (5, 4) if near else (2, 1)
        for k in range(len(C)):
            a, b = C[k], C[(k + 1) % len(C)]
            for j in range(nv):
                mat = f"tile_{edge}" if (edge and j == 0) else f"tile_{tile}"
                v0, v1 = j / nv, (j + 1) / nv
                for i in range(nu):
                    t0, t1 = -1 + 2 * i / nu, -1 + 2 * (i + 1) / nu

                    def pt(t, v):
                        f = (t + 1) / 2
                        return ((a[0] + (b[0] - a[0]) * f) * (1 - v), Y(v) + up(t, v), (a[1] + (b[1] - a[1]) * f) * (1 - v))
                    m.poly([pt(t0, v0), pt(t1, v0), pt(t1, v1), pt(t0, v1)], mat)
            m.poly([(a[0], Y(0) + Lc, a[1]), (b[0], Y(0) + Lc, b[1]), (b[0], Y(0) - 0.2, b[1]), (a[0], Y(0) - 0.2, a[1])], "fascia")
        r = min(0.45, 0.08 * (hx + hz))
        tip = (0, y1 + 3 * r, 0)
        ring = [(r, y1 + r, 0), (0, y1 + r, r), (-r, y1 + r, 0), (0, y1 + r, -r)]
        for k in range(4):
            m.poly([ring[k], ring[(k + 1) % 4], tip], f"ridge_{tile}")
            m.poly([(0, y1 - 0.1, 0), ring[(k + 1) % 4], ring[k]], f"ridge_{tile}")
        for a in C:
            for j in range(nv):
                v0, v1 = j / nv, (j + 1) / nv
                p = lambda v, dy: (a[0] * (1 - v), Y(v) + up(1, v) + dy, a[1] * (1 - v))
                m.poly([p(v0, 0), p(v1, 0), p(v1, 0.2), p(v0, 0.2)], f"ridge_{tile}")

    # ------------------------------------------------------------ flights
    def flight(self, side, off, hf, hd, plTop, width, tread=0.3, chuidai=True):
        """A flight 踏跺 out of a platform's side (front, back, left, right), centred `off` along it, with the side slabs 垂带 sloping from the platform's edge to the foot.
        Returns the foot's middle (s, y, q) in the current frame. The blocks reach just below the lowest ground under them."""
        m = self.m
        dirs = {"front": (0, 1), "back": (0, -1), "right": (1, 0), "left": (-1, 0)}
        dx, dq = dirs[side]
        along = dx == 0
        edge = hd if along else hf

        def loc(out, lat):
            return (off + lat, dq * (edge + out)) if along else (dx * (edge + out), off + lat)
        gF = self.gy_local(*loc(1.0, 0))
        h0 = plTop - gF
        if h0 < 0.12:
            return None
        n = max(1, round(h0 / 0.15))
        run = n * tread
        samples = [self.gy_local(*loc(o, l)) for o in (0.05, run) for l in (-width / 2, width / 2)] + [self.gy_local(*loc(run, 0))]
        yG = samples[-1]
        yLow = min(samples) - 0.15
        rise = (plTop - yG) / n

        def span(d0, d1, y1, l0, l1, mat):
            if along:
                a, b = sorted((dq * (edge + d0), dq * (edge + d1)))
                m.box(off + l0, off + l1, yLow, y1, a, b, mat)
            else:
                a, b = sorted((dx * (edge + d0), dx * (edge + d1)))
                m.box(a, b, yLow, y1, off + l0, off + l1, mat)
        w = width / 2
        for k in range(n):
            span(k * tread, (k + 1) * tread, plTop - (k + 1) * rise + (0 if k else 0), -w, w, "step")
        if chuidai:  # 垂带: a slab each side, sloping from the platform's top to the foot
            cw = 0.4
            for l0, l1 in ((-w - cw, -w), (w, w + cw)):
                for lat in (l0, l1):
                    pass
                pts = []
                for d, y in ((0.0, plTop), (run, yG + 0.05)):
                    pts.append((d, y))
                # a sloped prism: the top face from (0, plTop) to (run, yG), sides down to yLow
                def P(d, lat, y):
                    s, qq = loc(d, lat)
                    return (s, y, qq)
                top = [P(0, l0, plTop), P(0, l1, plTop), P(run, l1, yG + 0.05), P(run, l0, yG + 0.05)]
                m.poly(top, "step")
                for lat in (l0, l1):
                    m.poly([P(0, lat, plTop), P(run, lat, yG + 0.05), P(run, lat, yLow), P(0, lat, yLow)], "step")
                m.poly([P(run, l0, yG + 0.05), P(run, l1, yG + 0.05), P(run, l1, yLow), P(run, l0, yLow)], "step")
        s, qq = loc(run, 0)
        return (s, yG, qq)

    # ------------------------------------------------------------ the platform and its balustrade
    def platform(self, hf, hd, top, foot, coping=True, mat="platform"):
        m = self.m
        m.box(-hf, hf, foot, top, -hd, hd, mat, skip=("bottom",))
        if coping and top - foot > 0.25:
            m.box(-hf - 0.04, hf + 0.04, top - 0.16, top, -hd - 0.04, hd + 0.04, "coping", skip=("bottom",))

    def balustrade(self, hf, hd, y, gaps, h=0.85):
        """Stone balustrade inset from the platform's edge; gaps: {side: [(lat0, lat1), ...]} left open for the flights."""
        m = self.m
        ins = 0.15
        s0, q0 = hf - ins, hd - ins

        def run(a0, a1, fixed, onS):
            if a1 - a0 < 0.4:
                return
            box = (lambda x0, x1, z0, z1, y0, y1: m.box(fixed + x0, fixed + x1, y0, y1, z0, z1, "marble")) if onS else (lambda x0, x1, z0, z1, y0, y1: m.box(x0, x1, y0, y1, fixed + z0, fixed + z1, "marble"))
            if onS:
                m.box(fixed - 0.09, fixed + 0.09, y + h - 0.13, y + h, a0, a1, "marble")
                m.box(fixed - 0.07, fixed + 0.07, y, y + 0.16, a0, a1, "marble")
            else:
                m.box(a0, a1, y + h - 0.13, y + h, fixed - 0.09, fixed + 0.09, "marble")
                m.box(a0, a1, y, y + 0.16, fixed - 0.07, fixed + 0.07, "marble")
            npost = max(1, round((a1 - a0) / 1.8))
            for k in range(npost + 1):
                t = a0 + (a1 - a0) * k / npost
                if onS:
                    m.box(fixed - 0.11, fixed + 0.11, y, y + h + 0.18, t - 0.11, t + 0.11, "marble")
                else:
                    m.box(t - 0.11, t + 0.11, y, y + h + 0.18, fixed - 0.11, fixed + 0.11, "marble")
            # the panels between the posts, pierced in the middle
            for k in range(npost):
                ta, tb = a0 + (a1 - a0) * k / npost + 0.12, a0 + (a1 - a0) * (k + 1) / npost - 0.12
                if tb - ta < 0.3:
                    continue
                if onS:
                    m.box(fixed - 0.04, fixed + 0.04, y + 0.16, y + 0.42, ta, tb, "marble")
                else:
                    m.box(ta, tb, y + 0.16, y + 0.42, fixed - 0.04, fixed + 0.04, "marble")

        def cut(a0, a1, holes):
            segs, cur = [], a0
            for h0, h1 in sorted(holes):
                segs.append((cur, h0))
                cur = h1
            segs.append((cur, a1))
            return segs
        for side, fixed, onS, (a0, a1) in (("front", q0, False, (-s0, s0)), ("back", -q0, False, (-s0, s0)), ("right", s0, True, (-q0, q0)), ("left", -s0, True, (-q0, q0))):
            for b0, b1 in cut(a0, a1, gaps.get(side, [])):
                run(b0, b1, fixed, onS)

    # ------------------------------------------------------------ the body
    def columns(self, xs, qs, hs, hq, y0, y1, dia):
        r = dia / 2
        seen = set()
        n = 8
        ring = [(r * math.cos(2 * math.pi * (k + 0.5) / n), r * math.sin(2 * math.pi * (k + 0.5) / n)) for k in range(n)]

        def put(s, q):
            k = (round(s, 2), round(q, 2))
            if k in seen:
                return
            seen.add(k)
            pts = [(s + a, q + b) for a, b in ring]
            self.m.prism(pts, y0, y1, "lacquer", top=False)
            self.m.box(s - r - 0.1, s + r + 0.1, y0 - 0.02, y0 + 0.1, q - r - 0.1, q + r + 0.1, "coping")  # the base stone 柱顶石
        for s in xs:
            put(s, hq)
            put(s, -hq)
        for q in qs:
            put(-hs, q)
            put(hs, q)

    def ring_band(self, hs, hq, t, y0, y1, out, mat):
        m = self.m
        m.box(-hs - out, hs + out, y0, y1, hq - t + out, hq + out, mat)
        m.box(-hs - out, hs + out, y0, y1, -hq - out, -hq + t - out, mat)
        m.box(-hs - out, -hs + t - out, y0, y1, -hq + t - out, hq - t + out, mat)
        m.box(hs - t + out, hs + out, y0, y1, -hq + t - out, hq - t + out, mat)

    def bands(self, hs, hq, top, brackets, dia, cap):
        """The beam ring at the column line; on 大式 halls the bracket band above it, stepping out (kit3d.js bands()). cap: the roof's underside limit."""
        bandH = 0.85 if brackets else 0.42
        bt = max(dia * 0.9, 0.22)
        if brackets:
            y1 = top - 0.5
            self.ring_band(hs, hq, bt, top - bandH, y1, 0, "band")
            self.ring_band(hs + 0.12, hq + 0.12, bt + 0.12, y1, min(y1 + 0.3, cap), 0, "bracket")
            self.ring_band(hs + 0.22, hq + 0.22, bt + 0.22, min(y1 + 0.3, cap), min(top, cap), 0, "bandred")
            # the bracket sets as blocks along the band, one between each pair of columns and one on each: their rhythm
            return bandH
        self.ring_band(hs, hq, bt, top - bandH, top, 0, "band")
        return bandH

    def bracket_sets(self, xs, hs, hq, y0, y1, per_bay=2):
        """Bracket sets 斗拱 as stepped blocks along the front and back: one on each column, `per_bay` between (the 攒 of a 大式 hall; their number C)."""
        m = self.m
        pos = []
        for a, b in zip(xs[:-1], xs[1:]):
            pos.append(a)
            for k in range(1, per_bay + 1):
                pos.append(a + (b - a) * k / (per_bay + 1))
        pos.append(xs[-1])
        h = y1 - y0
        for s in pos:
            for sg in (1, -1):
                q = sg * hq
                m.box(s - 0.16, s + 0.16, y0, y0 + h * 0.4, q - 0.16, q + 0.16, "bracket")
                m.box(s - 0.26, s + 0.26, y0 + h * 0.4, y0 + h * 0.75, q - 0.1 + sg * 0.12, q + 0.1 + sg * 0.12, "bracket")
                m.box(s - 0.12, s + 0.12, y0 + h * 0.75, y1, q - 0.08 + sg * 0.24, q + 0.08 + sg * 0.24, "bracket")

    def opening(self, sa, sb, qf, sgn, y0, y1, door, onS, gate=False):
        """kit3d.js opening(): one bay of a façade, faces in the plane qf (or s = qf with onS), the pane 0.12 m behind the frame."""
        m = self.m
        w = sb - sa
        if w < 0.6 or y1 - y0 < 1.2:
            return

        def at(a, y, d):
            f = qf - sgn * d
            return (f, y, a) if onS else (a, y, f)

        def F(a0, a1, yy0, yy1, d, mat):
            m.poly([at(a0, yy1, d), at(a0, yy0, d), at(a1, yy0, d), at(a1, yy1, d)], mat)

        def R(a, yy0, yy1, d0, d1, mat):
            m.poly([at(a, yy1, d0), at(a, yy0, d0), at(a, yy0, d1), at(a, yy1, d1)], mat)

        def Rh(a0, a1, yy, d0, d1, mat):
            m.poly([at(a0, yy, d0), at(a1, yy, d0), at(a1, yy, d1), at(a0, yy, d1)], mat)
        H = y1 - y0
        sill = 0 if door else min(0.9, 0.3 * H)
        lint = y0 + max(H * 0.8, sill + 1.2)
        fr = 0.1
        if gate:
            F(sa + fr, sb - fr, y0, lint, 0.3, "lacquer")
            R(sa + fr, y0, y1, 0, 0.3, "lacquer")
            R(sb - fr, y0, y1, 0, 0.3, "lacquer")
            F(sa, sa + fr, y0, y1, 0, "lacquer")
            F(sb - fr, sb, y0, y1, 0, "lacquer")
            F(sa, sb, lint - 0.08, lint + 0.08, 0, "lacquer")
            F(sa, sb, y1 - 0.12, y1, 0, "lacquer")
            F((sa + sb) / 2 - 0.03, (sa + sb) / 2 + 0.03, y0, lint, 0.28, "lacquer_dark")
            for k in range(1, 5):  # door nails 门钉, as rows of studs: a band each
                yy = y0 + (lint - y0) * k / 5.5
                F(sa + fr + 0.1, sb - fr - 0.1, yy - 0.03, yy + 0.03, 0.27, "gold")
            F(sa + fr, sb - fr, lint, y1, 0.12, "glass_lattice")
            return
        if sill > 0:
            F(sa, sb, y0, y0 + sill, -0.04, "wall")
            Rh(sa, sb, y0 + sill, -0.04, 0.12, "sill")
        F(sa + fr, sb - fr, y0 + sill, y1, 0.12, "glass_lattice")
        F(sa, sa + fr, y0 + sill, y1, 0, "lacquer")
        F(sb - fr, sb, y0 + sill, y1, 0, "lacquer")
        F(sa, sb, lint - 0.06, lint + 0.06, 0, "lacquer")
        F(sa, sb, y1 - 0.1, y1, 0, "lacquer")
        if sill > 0:
            F(sa, sb, y0 + sill, y0 + sill + 0.08, 0, "lacquer")
        R(sa + fr, y0 + sill, y1, 0, 0.12, "lacquer")
        R(sb - fr, y0 + sill, y1, 0, 0.12, "lacquer")
        Rh(sa + fr, sb - fr, y1 - 0.1, 0, 0.12, "lacquer")
        leaves = 4 if door else max(2, round(w / 1.1))
        for k in range(1, leaves):
            s = sa + w * k / leaves
            F(s - 0.04, s + 0.04, y0 + sill, lint, 0.04, "lacquer")
        yk = y0 + (lint - y0) * 0.42
        if door:
            F(sa + fr, sb - fr, y0, yk, 0.03, "lacquer")
            F(sa + fr, sb - fr, yk + (lint - yk) * 0.12, yk + (lint - yk) * 0.17, 0.02, "lacquer")
        yL0 = yk if door else y0 + sill
        for k in (1, 2):
            yy = yL0 + (lint - yL0) * k / 3
            F(sa + fr, sb - fr, yy - 0.025, yy + 0.025, 0.06, "lacquer")
        nvb = max(2, round(w / 0.55))
        for k in range(1, nvb):
            s = sa + w * k / nvb
            F(s - 0.022, s + 0.022, yL0, lint, 0.07, "lacquer")
        nt = max(2, round(w / 0.7))
        for k in range(1, nt):
            s = sa + w * k / nt
            F(s - 0.02, s + 0.02, lint, y1, 0.07, "lacquer")

    def body(self, H, hs, hq, pf, pb, ps, y0, y1, first_floor, xs, qs, cap=None):
        """kit3d.js body(): columns, bands, ceiling, the front and back bays (doors where H['dr']), the sides (windows, or 硬山 gable walls), the dark core behind the panes."""
        m = self.m
        bandH = 0.85 if H["bd"] == "br" else 0.42
        top = y1 - bandH
        qw, qr, sw = hq - pf, -(hq - pb), hs - ps
        self.columns(xs, qs, hs, hq, y0, top, H["dia"])
        self.bands(hs, hq, y1, H["bd"] == "br", H["dia"], cap if cap is not None else y1)
        if H["bd"] == "br":
            self.bracket_sets(xs, hs + 0.12, hq + 0.12, top + 0.42, y1 - 0.02, H.get("per_bay", 2))
        m.poly([(-hs, top, hq), (hs, top, hq), (hs, top, -hq), (-hs, top, -hq)], "underside")
        doors = set(H["dr"])
        for qf, sgn, front in ((qw, 1, True), (qr, -1, False)):
            for i in range(len(xs) - 1):
                sa, sb = max(xs[i], -sw), min(xs[i + 1], sw)
                if sb - sa < 0.5:
                    continue
                door = first_floor and (i in doors if front else (H["rr"] == "d" and i == (len(xs) - 1) // 2))
                if H["k"] == "gate" and not door:
                    m.box(sa, sb, y0, top, min(qf, qf - sgn * 0.5), max(qf, qf - sgn * 0.5), "wallred")
                    continue
                self.opening(sa, sb, qf, sgn, y0, top, door, False, gate=H["k"] == "gate" and door)
                if (pf if front else pb) > 0:
                    r = H["dia"] / 2
                    m.box(sa - r, sa + r, y0, top, qf - r, qf + r, "lacquer")
        if H["rf"] == "ys":
            for sg in (1, -1):
                m.box(hs - 0.2 if sg > 0 else -hs - 0.42, hs + 0.42 if sg > 0 else -hs + 0.2, y0, y1 + 0.1, -hq - 0.42, hq + 0.42, "wall")
                m.poly([(sg * (hs + 0.44), y1 - 0.5, hq - 0.6), (sg * (hs + 0.44), y0 + 0.9, hq - 0.6), (sg * (hs + 0.44), y0 + 0.9, -hq + 0.6), (sg * (hs + 0.44), y1 - 0.5, -hq + 0.6)], "plaster")
        else:
            qin = [q for q in qs if qr - 0.01 <= q <= qw + 0.01]
            for sg in (1, -1):
                if H.get("side_wall"):
                    m.box(sw - 0.35 if sg > 0 else -sw, sw if sg > 0 else -sw + 0.35, y0, top, qr, qw, "wall")
                    continue
                for i in range(len(qin) - 1):
                    qa, qb = qin[i + 1], qin[i]
                    if qb - qa < 0.6:
                        continue
                    self.opening(qa, qb, sg * sw, sg, y0, top, False, True)
                if len(qin) < 2:
                    m.box(sw - 0.3 if sg > 0 else -sw, sw if sg > 0 else -sw + 0.3, y0, top, qr, qw, "wall")
        if H["k"] != "gate":  # a gate has no rooms: its plank doors stand 0.3 m in, and a dark core would hide them
            m.box(-sw + 0.15, sw - 0.15, y0, top - 0.05, qr + 0.15, qw - 0.15, "glass_lattice")
        else:
            m.poly([(-sw, top - 0.05, qw - 0.3), (sw, top - 0.05, qw - 0.3), (sw, top - 0.05, qr + 0.3), (-sw, top - 0.05, qr + 0.3)], "underside")

    # ------------------------------------------------------------ a whole hall
    def hall(self, H):
        """A hall from its numbers, in the current frame (push it first). H keys, as kit_1860.json: hf hd (half sizes of the platform), foot (y of its lowest ground), base (y of
        its ground at the front), pl (platform height), eave, ridge (above base), e (platform edge 下出), o (overhang 上出), b (bay widths), d (widths across), pf pb ps (porches),
        dia, st ({side: [offsets]}), fw (flight width by side), bal, rf, rl, db, ju, t, te, bd, dr, rr, k (hall, gate, tower), mid (a second storey's floor above base, or None).
        Returns the flights' feet {name: (s, y, q)} in the current frame."""
        m = self.m
        hf, hd, base = H["hf"], H["hd"], H["base"]
        plTop, eave, ridge = base + H["pl"], base + H["eave"], base + H["ridge"]
        CS, CQ, o = hf - H["e"], hd - H["e"], H["o"]
        self.platform(hf, hd, plTop, H["foot"], mat=H.get("platform_mat", "platform"))
        feet, gaps = {}, {}
        for side, offs in H.get("st", {}).items():
            for off in offs:
                wdt = H.get("fw", {}).get(side, max(H["b"][len(H["b"]) // 2], 2.4) if side in ("front", "back") else 2.6)
                f = self.flight(side, off, hf, hd, plTop, wdt)
                if f:
                    feet[f"{side}_{off:+.1f}"] = f
                    gaps.setdefault(side, []).append((off - wdt / 2 - 0.4, off + wdt / 2 + 0.4))
        if H.get("bal"):
            self.balustrade(hf, hd, plTop, gaps)
        xs = [-CS]
        for w in H["b"]:
            xs.append(xs[-1] + w)
        xs[-1] = CS
        qs = [CQ]
        for w in H["d"]:
            qs.append(qs[-1] - w)
        qs[-1] = -CQ
        RS, RQ, tip = CS + o, CQ + o, eave - o * 0.5
        ju, form = H["ju"], H["rf"]
        ropt = dict(rolled=bool(H["rl"]), ju=ju, tile=H["t"], edge=H.get("te"), gable_mat="lacquer" if form == "xs" else "wall", liftK=H.get("lift", 1.0))
        if H.get("mid"):
            mid = base + H["mid"]
            self.body(H, CS, CQ, H["pf"], H["pb"], H["ps"], plTop, mid, True, xs, qs)
            self.skirt(CS + o * 0.8, CQ + o * 0.8, CS - 0.1, CQ - 0.1, mid - o * 0.4, mid + 0.5, H["t"], H.get("te"))
            self.balcony(CS - 0.05, CQ - 0.05, mid + 0.5)
            k = (CS - 0.1) / CS
            self.body(dict(H, dr=[], rr="w"), CS - 0.1, CQ - 0.1, 0, 0, 0, mid + 0.5, eave, False, [x * k for x in xs], [CQ - 0.1, -(CQ - 0.1)])
            self.roof_over(RS, RQ, tip, ridge, form, ropt, o)
        elif H.get("db"):
            self.body(H, CS, CQ, H["pf"], H["pb"], H["ps"], plTop, eave, True, xs, qs)
            inS, inQ = CS - max(H["pf"], H["ps"], 1.5), CQ - max(H["pf"], H["pb"], 1.5)
            yUp = eave + (ridge - eave) * H.get("upper", 0.36)
            self.skirt(RS, RQ, inS, inQ, tip, eave + 0.8, H["t"], H.get("te"))
            m.box(-inS, inS, eave + 0.2, yUp - 0.6, -inQ, inQ, "wall")
            self.bands(inS, inQ, yUp, H["bd"] == "br", H["dia"], yUp)
            if H["bd"] == "br":
                xi = [x * inS / CS for x in xs]
                self.bracket_sets(xi, inS + 0.12, inQ + 0.12, yUp - 0.43, yUp - 0.02, H.get("per_bay", 2))
            lip = o * 0.75
            self.roof_over(inS + lip, inQ + lip, yUp - lip * 0.5, ridge, form, ropt, o)
        else:
            gate = H["k"] == "gate"
            self.body(H, CS, CQ, 0 if gate else H["pf"], 0 if gate else H["pb"], 0 if gate else H["ps"], plTop, eave, True, xs, qs)
            self.roof_over(RS, RQ, tip, ridge, form, ropt, o)
        return feet

    def roof_over(self, hs, hq, y0, y1, form, ropt, o):
        along = hs >= hq
        P = (lambda x, y, z: (x, y, z)) if along else (lambda x, y, z: (z, y, -x))
        hx, hz = (hs, hq) if along else (hq, hs)
        opt = dict(ropt)
        if form == "cj":
            self.pyramid(hs, hq, y0, y1, tile=opt["tile"], edge=opt.get("edge"))
            return
        if form == "ys":
            hx2 = min(hx, hx - o + 0.45)
            opt["gableX"] = hx2
            self.roof(P, hx2, hz, y0, y1, form=form, **opt)
            return
        if form == "xu":
            opt["gableX"] = hx - min(0.6, o * 0.5)
        self.roof(P, hx, hz, y0, y1, form=form, **opt)

    def skirt(self, os_, oq, is_, iq, y0, y1, tile, edge=None):
        """A skirt roof 腰檐 (or the lower eave of a 重檐) from the outer rectangle at y0 up to the inner one at y1, with a corner lift."""
        m = self.m
        n0 = [(-os_, oq), (os_, oq), (os_, -oq), (-os_, -oq)]
        n1 = [(-is_, iq), (is_, iq), (is_, -iq), (-is_, -iq)]
        lift = min(0.35, 0.03 * (os_ + oq))
        mat = f"tile_{edge or tile}"
        for k in range(4):
            a0, b0, a1, b1 = n0[k], n0[(k + 1) % 4], n1[k], n1[(k + 1) % 4]
            # two bands: the edge colour at the eave, the field above
            mid = 0.3
            pa = (a0[0] + (a1[0] - a0[0]) * mid, y0 + lift + (y1 - y0 - lift) * mid, a0[1] + (a1[1] - a0[1]) * mid)
            pb = (b0[0] + (b1[0] - b0[0]) * mid, y0 + lift + (y1 - y0 - lift) * mid, b0[1] + (b1[1] - b0[1]) * mid)
            m.poly([(a0[0], y0 + lift, a0[1]), (b0[0], y0 + lift, b0[1]), pb, pa], mat)
            m.poly([pa, pb, (b1[0], y1, b1[1]), (a1[0], y1, a1[1])], f"tile_{tile}")
            m.poly([(a0[0], y0 + lift, a0[1]), (b0[0], y0 + lift, b0[1]), (b0[0], y0 - 0.2, b0[1]), (a0[0], y0 - 0.2, a0[1])], "fascia")
            m.poly([(a0[0], y0 - 0.2, a0[1]), (b0[0], y0 - 0.2, b0[1]), (b1[0], y0 - 0.2, b1[1]), (a1[0], y0 - 0.2, a1[1])], "underside")
        # the hip strips of the skirt
        for k in range(4):
            a0, a1 = n0[k], n1[k]
            m.poly([(a0[0], y0 + lift, a0[1]), (a1[0], y1, a1[1]), (a1[0], y1 + 0.2, a1[1]), (a0[0], y0 + lift + 0.2, a0[1])], f"ridge_{tile}")

    def balcony(self, hs, hq, y):
        m = self.m
        self.ring_band(hs, hq, 0.08, y + 0.85, y + 0.95, 0, "lacquer")
        self.ring_band(hs, hq, 0.06, y, y + 0.12, 0, "lacquer")
        for s0, q0, s1, q1 in ((-hs, hq, hs, hq), (-hs, -hq, hs, -hq), (-hs, -hq, -hs, hq), (hs, -hq, hs, hq)):
            L = math.hypot(s1 - s0, q1 - q0)
            n = max(1, round(L / 1.5))
            for k in range(n + 1):
                s, q = s0 + (s1 - s0) * k / n, q0 + (q1 - q0) * k / n
                m.box(s - 0.06, s + 0.06, y, y + 0.95, q - 0.06, q + 0.06, "lacquer")
            for k in range(round(L / 0.3)):  # balusters of the 平座 rail, thin
                t = (k + 0.5) / round(L / 0.3)
                s, q = s0 + (s1 - s0) * t, q0 + (q1 - q0) * t
                if k % 2 == 0:
                    m.box(s - 0.025, s + 0.025, y + 0.12, y + 0.85, q - 0.025, q + 0.025, "lacquer")

    # ------------------------------------------------------------ walls, screens, archways, galleries, rocks
    def wall(self, pts, h, thick=0.9, cap="grey", base_h=0.6, closed=False, coping=True, ytop=None):
        """A palace wall 宫墙 along a polyline (x, z) of the current frame: a stone footing, the red plastered body, a tiled coping with a small roof both ways.
        Feet follow the ground every 2.5 m; the top is level per segment at the higher end's ground + h."""
        m = self.m
        n = len(pts)
        segs = list(zip(pts, pts[1:] + ([pts[0]] if closed else [])))
        feet = []
        ytop_given = ytop
        for (ax, az), (bx, bz) in segs:
            ytop = ytop_given
            L = math.hypot(bx - ax, bz - az)
            if L < 0.05:
                continue
            ux, uz = (bx - ax) / L, (bz - az) / L
            nx, nz = -uz, ux
            k = max(1, int(math.ceil(L / 2.5)))
            t = thick / 2
            gs = [self.ground(ax + (bx - ax) * i / k, az + (bz - az) * i / k) for i in range(k + 1)]
            ytop = max(gs) + h if ytop is None else ytop  # a wall on a terrace's edge: its top from the terrace (the caller), its foot on the ground outside
            ext = t if (closed or True) else 0.0
            for i in range(k):
                s0, s1 = (L * i / k, L * (i + 1) / k)
                if i == 0:
                    s0 -= ext
                if i == k - 1:
                    s1 += ext
                p = lambda s, d: (ax + ux * s + nx * d, az + uz * s + nz * d)
                y0a, y0b = gs[i] - 0.15, gs[i + 1] - 0.15
                for d in (t, -t):
                    (x0, z0), (x1, z1) = p(s0, d), p(s1, d)
                    yb = min(gs[i], gs[i + 1])
                    m.poly([(x0, y0a, z0), (x1, y0b, z1), (x1, yb + base_h, z1), (x0, yb + base_h, z0)], "platform")
                    m.poly([(x0, yb + base_h, z0), (x1, yb + base_h, z1), (x1, ytop, z1), (x0, ytop, z0)], "wallred")
                for s in ((s0, ) if i == 0 else ()) + ((s1, ) if i == k - 1 else ()):
                    (x0, z0), (x1, z1) = p(s, t), p(s, -t)
                    yy = gs[0] if s == s0 else gs[-1]
                    m.poly([(x0, yy - 0.15, z0), (x1, yy - 0.15, z1), (x1, ytop, z1), (x0, ytop, z0)], "wallred")
            # the coping: a small two-way roof
            p = lambda s, d: (ax + ux * s + nx * d, az + uz * s + nz * d)
            o = t + 0.25
            for d in (o, -o):
                (x0, z0), (x1, z1) = p(-t - 0.1, d), p(L + t + 0.1, d)
                (x2, z2), (x3, z3) = p(L + t + 0.1, 0), p(-t - 0.1, 0)
                m.poly([(x0, ytop + 0.05, z0), (x1, ytop + 0.05, z1), (x2, ytop + 0.55, z2), (x3, ytop + 0.55, z3)], f"tile_{cap}")
                m.poly([(x0, ytop + 0.05, z0), (x1, ytop + 0.05, z1), (x1, ytop - 0.12, z1), (x0, ytop - 0.12, z0)], "fascia")
            (x0, z0), (x1, z1) = p(-t - 0.1, 0), p(L + t + 0.1, 0)
            m.box  # noqa: B018
            for d in (0.12, -0.12):
                (xa, za), (xb, zb) = p(-t - 0.1, d), p(L + t + 0.1, d)
                m.poly([(xa, ytop + 0.5, za), (xb, ytop + 0.5, zb), (xb, ytop + 0.72, zb), (xa, ytop + 0.72, za)], f"ridge_{cap}")
            (xa, za), (xb, zb), (xc, zc), (xd, zd) = p(-t - 0.1, 0.12), p(L + t + 0.1, 0.12), p(L + t + 0.1, -0.12), p(-t - 0.1, -0.12)
            m.poly([(xa, ytop + 0.72, za), (xb, ytop + 0.72, zb), (xc, ytop + 0.72, zc), (xd, ytop + 0.72, zd)], f"ridge_{cap}")
            m.poly([(x0, ytop - 0.12, z0), (x1, ytop - 0.12, z1), p(L + t + 0.1, 0) and (x1, ytop - 0.12, z1), (x0, ytop - 0.12, z0)], "underside") if False else None
            feet.append(((ax, az), gs[0]))
        return feet

    def screen(self, cx, cz, w, d, h, tile="grey", panel="plaster", base=0.7):
        """A screen wall 影壁 standing free, in the current frame: a stone base 须弥座 `base` high, the body with a framed panel on both faces, a small hip roof with a ridge."""
        m = self.m
        g = min(self.ground(cx + a, cz + b) for a in (-w / 2, w / 2) for b in (-d / 2, d / 2))
        y0 = g - 0.15
        m.box(cx - w / 2 - 0.15, cx + w / 2 + 0.15, y0, g + base, cz - d / 2 - 0.15, cz + d / 2 + 0.15, "marble", skip=("bottom",))
        m.box(cx - w / 2, cx + w / 2, g + base, g + h - 0.5, cz - d / 2, cz + d / 2, "wall", skip=("bottom",))
        for sg in (1, -1):
            zf = cz + sg * (d / 2 + 0.01)
            m.poly([(cx - w / 2 + 0.6, g + 1.1, zf), (cx + w / 2 - 0.6, g + 1.1, zf), (cx + w / 2 - 0.6, g + h - 0.95, zf), (cx - w / 2 + 0.6, g + h - 0.95, zf)], panel)
            m.poly([(cx - 0.6, g + 1.9, zf + sg * 0.01), (cx + 0.6, g + 1.9, zf + sg * 0.01), (cx + 0.6, g + h - 1.6, zf + sg * 0.01), (cx - 0.6, g + h - 1.6, zf + sg * 0.01)], f"tile_{tile}")
            m.box(cx - w / 2, cx + w / 2, g + h - 0.62, g + h - 0.5, cz - d / 2 - 0.06, cz + d / 2 + 0.06, "band")
        self.m.push(cx, 0, cz)
        self.roof(lambda x, y, z: (x, y, z), w / 2 + 0.35, d / 2 + 0.45, g + h - 0.55, g + h + 0.35, form="wd", rolled=False, ju=[0.5, 0.7], tile=tile)
        self.m.pop()
        return g

    def pailou_glazed(self, w, d, h, nbays=3, tile="yellow", edge="green", body="wallred"):
        """A glazed archway 琉璃牌楼 in the current frame (centred, its face along x): a masonry body on a stone base with three round-headed passages, a glazed frieze of
        imitation beams and brackets, three roofs (the middle one higher), the ends as buttress piers. Its form is the class of the standing glazed archways (C)."""
        m = self.m
        g = min(self.gy_local(a, b) for a in (-w / 2, w / 2) for b in (-d / 2, d / 2))
        y0 = g - 0.15
        m.box(-w / 2 - 0.2, w / 2 + 0.2, y0, g + 0.5, -d / 2 - 0.2, d / 2 + 0.2, "marble", skip=("bottom",))
        bw = w / (nbays + 0.2 * (nbays + 1) / 0.6)
        pier = (w - nbays * bw) / (nbays + 1)
        xs = []
        x = -w / 2
        for k in range(nbays):
            x += pier
            xs.append((x, x + bw))
            x += bw
        yb = g + 0.5
        hm = h * 0.62
        # the body as a wall with three arched holes, both faces, and the passages' soffits
        from model_parts import Parts  # noqa: E402
        P = Parts(m)
        for sg in (1, -1):
            m.push(0, 0, sg * d / 2, 0 if sg > 0 else math.pi)
            holes = [((a0 if sg > 0 else -a1), (a1 if sg > 0 else -a0), yb, yb + (hm - (bw / 2)) * (1.0 if k != nbays // 2 else 1.08), bw / 2) for k, (a0, a1) in enumerate(xs)]
            P.wall_holes(-w / 2, w / 2, yb, yb + hm, holes, body)
            m.pop()
        for k, (a0, a1) in enumerate(xs):
            top = yb + (hm - bw / 2) * (1.0 if k != nbays // 2 else 1.08)
            m.box(a0, a0 + 0.02, yb, top, -d / 2, d / 2, body)
            m.box(a1 - 0.02, a1, yb, top, -d / 2, d / 2, body)
            from model_parts import arc_pts  # noqa: E402
            pts = arc_pts(a0, a1, top, bw / 2, 8)
            for (x0, y0_), (x1, y1_) in zip(pts[:-1], pts[1:]):
                m.poly([(x0, y0_, d / 2), (x1, y1_, d / 2), (x1, y1_, -d / 2), (x0, y0_, -d / 2)], "underside")
        m.box(-w / 2, w / 2, yb + hm, yb + hm + 0.02, -d / 2, d / 2, body)
        # the glazed frieze: beams, a panel 匾 in the middle, bracket band
        yf0, yf1 = yb + hm, yb + hm + h * 0.16
        m.box(-w / 2 - 0.05, w / 2 + 0.05, yf0, yf1, -d / 2 - 0.05, d / 2 + 0.05, "band")
        for sg in (1, -1):
            m.box(-w / 2 + 0.2, w / 2 - 0.2, yf0 + 0.15, yf0 + 0.35, sg * (d / 2 + 0.05), sg * (d / 2 + 0.1), f"tile_{edge}")
            m.box(-1.0, 1.0, yf0 + 0.45, yf1 - 0.1, sg * (d / 2 + 0.05), sg * (d / 2 + 0.12), "gold")
        self.bracket_sets([-w / 2, -w / 6, w / 6, w / 2], w / 2, d / 2 + 0.05, yf1, yf1 + 0.45, per_bay=2)
        # three roofs: the middle one higher and over the middle passage
        mid = xs[nbays // 2]
        yr = yf1 + 0.45
        self.m.push((mid[0] + mid[1]) / 2, 0, 0)
        self.roof(lambda x, y, z: (x, y, z), (mid[1] - mid[0]) / 2 + pier * 0.6, d / 2 + 0.7, yr + 0.9, yr + 2.3, form="wd", ju=[0.5, 0.7], tile=tile, edge=edge)
        m.box(-(mid[1] - mid[0]) / 2 - pier * 0.4, (mid[1] - mid[0]) / 2 + pier * 0.4, yr, yr + 0.95, -d / 2 + 0.05, d / 2 - 0.05, "band")
        self.m.pop()
        for k in (0, nbays - 1):
            a0, a1 = xs[k]
            cx = (a0 + a1) / 2 + (-1 if k == 0 else 1) * 0.3
            self.m.push(cx, 0, 0)
            self.roof(lambda x, y, z: (x, y, z), (a1 - a0) / 2 + pier * 0.8, d / 2 + 0.6, yr + 0.05, yr + 1.2, form="wd", ju=[0.5, 0.7], tile=tile, edge=edge)
            self.m.pop()
        return g

    def gallery(self, pts, width, y_floor_fn, eave=2.9, ridge=4.1, wall_side=0, tile="grey", wall_mat="wall", bay=3.2, stones=False):
        """A covered way 游廊 along a polyline (x, z): its own low platform, posts at the bays, a hanging fascia, a bench rail, a rolled 悬山 roof per straight run.
        wall_side: +1 or -1 a solid back wall on that side (+1 the right of the run's direction, -1 its left), with the set-in stone slabs (`stones`) on its inner face; 0 open both sides."""
        m = self.m
        half = width / 2
        for (ax, az), (bx, bz) in zip(pts[:-1], pts[1:]):
            L = math.hypot(bx - ax, bz - az)
            if L < 0.8:
                continue
            ux, uz = (bx - ax) / L, (bz - az) / L
            rot = math.atan2(ux, uz) - math.pi / 2
            mx, mz = (ax + bx) / 2, (az + bz) / 2
            y0 = max(y_floor_fn(ax, az), y_floor_fn(bx, bz), y_floor_fn(mx, mz))
            gl = min(self.ground(ax, az), self.ground(bx, bz), self.ground(mx, mz))
            m.push(mx, 0, mz, rot)
            # the run's frame: x along it, z across (+z on the right of the direction)
            hl = L / 2
            m.box(-hl - 0.05, hl + 0.05, gl - 0.15, y0, -half - 0.1, half + 0.1, "platform", skip=("bottom",))
            m.box(-hl - 0.05, hl + 0.05, y0 - 0.12, y0, -half - 0.12, half + 0.12, "coping", skip=("bottom",))
            top = y0 + eave
            n = max(1, round(L / bay))
            for k in range(n + 1):
                s = -hl + L * k / n
                for qz in (-half + 0.2, half - 0.2):
                    if wall_side and qz * wall_side < 0 and False:
                        continue
                    m.prism([(s + 0.12 * math.cos(a), qz + 0.12 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 7)[:-1]], y0, top - 0.3, "lacquer", top=False)
            for qz in (-half + 0.2, half - 0.2):
                m.box(-hl, hl, top - 0.32, top, qz - 0.1, qz + 0.1, "band")
                m.box(-hl, hl, top - 0.62, top - 0.32, qz - 0.03, qz + 0.03, "lacquer")  # the hanging fascia 倒挂楣子
            if wall_side:
                qz = wall_side * (half - 0.2)
                zw0, zw1 = sorted((qz, qz + wall_side * 0.35))
                zw0, zw1 = (qz - 0.18, qz + 0.18)
                m.box(-hl, hl, y0, top - 0.32, zw0, zw1, wall_mat)
                if stones:  # the carved slabs 帖石 set in the wall's inner face, a row of dark panels at eye height
                    face = qz - wall_side * 0.19
                    ns = max(1, int(L / 1.0))
                    for k in range(ns):
                        s0 = -hl + L * (k + 0.1) / ns
                        s1 = -hl + L * (k + 0.9) / ns
                        m.poly([(s0, y0 + 0.9, face), (s1, y0 + 0.9, face), (s1, y0 + 1.8, face), (s0, y0 + 1.8, face)], "stele")
            else:
                for qz in (-half + 0.2, half - 0.2):
                    m.box(-hl, hl, y0, y0 + 0.45, qz - 0.15, qz + 0.15, "lacquer")
            m.poly([(-hl, top - 0.32, -half + 0.1), (hl, top - 0.32, -half + 0.1), (hl, top - 0.32, half - 0.1), (-hl, top - 0.32, half - 0.1)], "underside")
            self.roof(lambda x, y, z: (x, y, z), hl + 0.25, half + 0.55, top - 0.35, y0 + ridge, form="xu", rolled=True, ju=JU["gallery"], tile=tile, gable_mat="plaster", gableX=hl + 0.25)
            m.pop()

    def rocks(self, cx, cz, rx, rz, n, seed, hmax=2.5, mat="rock"):
        """A rock pile 叠石: n irregular blocks inside an ellipse, seeded; each from just below the ground. Placement C."""
        rng = np.random.default_rng(seed)
        m = self.m
        for k in range(n):
            a, r = rng.uniform(0, 2 * math.pi), math.sqrt(rng.uniform(0, 1))
            x, z = cx + rx * r * math.cos(a), cz + rz * r * math.sin(a)
            s = rng.uniform(0.5, 1.4) * (1.2 - 0.5 * r)
            h = rng.uniform(0.5, 1.0) * hmax * (1.1 - 0.6 * r)
            g = self.ground(x, z) - 0.2
            k6 = 6
            lo = [(x + s * rng.uniform(0.7, 1.2) * math.cos(2 * math.pi * i / k6 + 0.3 * k), z + s * rng.uniform(0.7, 1.2) * math.sin(2 * math.pi * i / k6 + 0.3 * k)) for i in range(k6)]
            hi = [(x + (px - x) * rng.uniform(0.35, 0.7) + rng.uniform(-0.2, 0.2), z + (pz - z) * rng.uniform(0.35, 0.7) + rng.uniform(-0.2, 0.2)) for px, pz in lo]
            m.frustum(lo, hi, g, g + h, mat)
            m.flat(hi, g + h, mat)
