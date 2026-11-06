"""Parts shared by the detailed models of the Xiyang Lou (Round 14): façade openings, pilasters, entablatures, rustication, cartouches, balustrades, urns, a concave hip roof.
Imported, not run. Lifted from the pilot's generator (models/XY01-xieqiqu/xieqiqu.py, Round 13), which keeps its own copies so that its GLB stays byte for byte.

Usage: `P = Parts(mesh, rail_h=1.0)`, then `P.opening(...)` etc. The façade helpers draw in a face frame set with `mesh.push` (s along the face, y up, d out of the face);
the balustrades and urns in plan (x, z) at a level. Materials used: marble, joint, panel, glaze, glass_win, door, roof, roofedge, ridge (the caller's colour table must hold them).
"""

import math


def arc_pts(a0, a1, y, rise, n):
    """A segmental head from (a0, y) over to (a1, y), crown y + rise."""
    half = (a1 - a0) / 2
    c = (a0 + a1) / 2
    R = (half * half + rise * rise) / (2 * rise)
    cy = y + rise - R
    t1 = math.atan2(y - cy, half)
    t0 = math.pi - t1  # not atan2(y - cy, -half): for a semicircle y - cy is +-0.0 and atan2 may give -pi, an arch hanging downward (Round 14)
    return [(c + R * math.cos(t0 + (t1 - t0) * k / n), cy + R * math.sin(t0 + (t1 - t0) * k / n)) for k in range(n + 1)]


class Parts:
    def __init__(self, mesh, rail_h=1.0, baluster_segs=6):
        self.m = mesh
        self.rail_h = rail_h
        self.balusters = 0
        self.baluster_segs = baluster_segs  # 4 keeps a long run of balustrades within the GLB budget

    # ------------------------------------------------------------ walls and openings, in a face frame
    def wall_holes(self, s0, s1, y0, y1, holes, mat, d=0.0):
        """Wall rectangle in the plane d with holes (a0, a1, b0, b1, rise): rectangle to b1, a round head of `rise` above it (0: square)."""
        m = self.m
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

    def opening(self, a0, a1, b0, b1, rise, depth=0.32, kind="win", frame=0.16, head=None, bars=True, bar_step=0.75):
        """The dressing of a hole cut by wall_holes: reveals, glass or door leaf recessed, glazing bars, a proud frame, a sill, a head ('cornice', 'scroll', 'pediment', 'oval')."""
        m = self.m
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
            top = b1 + rise * 0.9
            nv = 2 if (a1 - a0) > 1.6 else 1
            for k in range(1, nv + 1):
                s = a0 + (a1 - a0) * k / (nv + 1)
                m.box(s - 0.035, s + 0.035, b0, top, dd, dd + 0.05, "marble", skip=("back",))
            n = max(2, round((b1 - b0) / bar_step))
            for k in range(1, n):
                y = b0 + (b1 - b0) * k / n
                m.box(a0, a1, y - 0.03, y + 0.03, dd, dd + 0.05, "marble", skip=("back",))
        if kind == "door":
            mid = (a0 + a1) / 2
            m.box(mid - 0.03, mid + 0.03, b0, b1, dd, dd + 0.04, "marble", skip=("back",))
            for y in (b0 + (b1 - b0) * 0.35, b0 + (b1 - b0) * 0.7):
                m.box(a0 + 0.12, a1 - 0.12, y - 0.025, y + 0.025, dd, dd + 0.03, "marble", skip=("back",))
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
        top = b1 + rise + frame
        mid = (a0 + a1) / 2
        if head == "cornice":
            m.box(a0 - frame - 0.2, a1 + frame + 0.2, top, top + 0.16, 0, 0.26, "marble", skip=("back",))
            m.box(mid - 0.35, mid + 0.35, top + 0.16, top + 0.62, 0.02, 0.14, "marble", skip=("back",))
            m.box(mid - 0.2, mid + 0.2, top + 0.24, top + 0.5, 0.14, 0.18, "glaze", skip=("back",))
        elif head == "scroll":
            w = (a1 - a0) / 2 + frame + 0.15
            m.poly([(mid - w, top, 0.12), (mid + w, top, 0.12), (mid, top + 0.55, 0.12)], "marble")
            m.box(mid - w, mid + w, top - 0.02, top + 0.1, 0, 0.16, "marble", skip=("back",))
        elif head == "pediment":
            w = (a1 - a0) / 2 + frame + 0.25
            m.box(mid - w, mid + w, top, top + 0.18, 0, 0.3, "marble", skip=("back",))
            for sx in (-1, 1):  # a broken segmental pediment: two raking halves and a cartouche between
                m.poly([(mid + sx * w, top + 0.18, 0.2), (mid + sx * w * 0.35, top + 0.18, 0.2), (mid + sx * w * 0.35, top + 0.62, 0.2), (mid + sx * w, top + 0.3, 0.2)], "marble")
            m.box(mid - 0.22, mid + 0.22, top + 0.18, top + 0.85, 0.05, 0.22, "panel", skip=("back",))
        elif head == "oval":
            self.oval(mid, top + 0.75, 0.62, 0.42)

    def oval(self, sc, yc, rx, ry, n=14, d=0.0):
        """An oval frame (the bull's-eye cartouches over the side windows of the water building, plates 11 and 13), with a dark centre."""
        m = self.m
        ring = [(sc + rx * math.cos(2 * math.pi * k / n), yc + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]
        inner = [(sc + (rx - 0.16) * math.cos(2 * math.pi * k / n), yc + (ry - 0.14) * math.sin(2 * math.pi * k / n)) for k in range(n)]
        for k in range(n):
            a, b, c, e = ring[k], ring[(k + 1) % n], inner[(k + 1) % n], inner[k]
            m.poly([(a[0], a[1], d + 0.14), (b[0], b[1], d + 0.14), (c[0], c[1], d + 0.14), (e[0], e[1], d + 0.14)], "marble")
            m.poly([(a[0], a[1], d), (b[0], b[1], d), (b[0], b[1], d + 0.14), (a[0], a[1], d + 0.14)], "marble")
        m.poly([(p[0], p[1], d + 0.06) for p in inner], "panel")

    def pilaster(self, s, y0, y1, w=0.55, out=0.22, mat="marble", flutes=True):
        m = self.m
        m.box(s - w / 2, s + w / 2, y0, y1, 0, out, mat, skip=("back",))
        m.box(s - w / 2 - 0.08, s + w / 2 + 0.08, y0, y0 + 0.35, 0, out + 0.06, mat, skip=("back",))
        m.box(s - w / 2 - 0.1, s + w / 2 + 0.1, y1 - 0.32, y1, 0, out + 0.1, mat, skip=("back",))
        if flutes:
            m.box(s - 0.1, s - 0.06, y0 + 0.45, y1 - 0.45, out, out + 0.015, "joint", skip=("back",))
            m.box(s + 0.06, s + 0.1, y0 + 0.45, y1 - 0.45, out, out + 0.015, "joint", skip=("back",))

    def column(self, s, d, y0, y1, r=0.3, segs=8):
        """A free column before the face (the frontispiece of 海晏堂's upper door, plate 10): base, shaft with entasis, capital."""
        self.m.lathe([(r + 0.1, y0), (r + 0.1, y0 + 0.3), (r, y0 + 0.4), (r * 0.92, y1 - 0.6), (r + 0.12, y1 - 0.35), (r + 0.18, y1)], segs, "marble", cx=s, cz=d)

    def entablature(self, s0, s1, y, h=1.0, out=0.45, ends=True):
        """Architrave, frieze and cornice over a storey; y is the cornice's top."""
        m = self.m
        skip = ("back",) if ends else ("back", "left", "right")
        m.box(s0 - 0.12, s1 + 0.12, y - h, y - h + 0.3, 0, 0.22, "marble", skip=skip)
        m.box(s0 - 0.12, s1 + 0.12, y - h + 0.3, y - 0.32, 0, 0.16, "wall", skip=skip)
        m.box(s0 - out + 0.12, s1 + out - 0.12, y - 0.32, y - 0.16, 0, out - 0.12, "marble", skip=skip)
        m.box(s0 - out, s1 + out, y - 0.16, y, 0, out, "marble", skip=skip)

    def rustication(self, s0, s1, y0, y1, step=0.55):
        y = y0 + step
        while y < y1 - 0.15:
            self.m.box(s0, s1, y - 0.035, y + 0.035, 0, 0.018, "joint", skip=("back",))
            y += step

    def cartouche(self, sc, yc, w, h):
        """A framed panel with glazed ornament."""
        m = self.m
        m.box(sc - w / 2, sc + w / 2, yc - h / 2, yc + h / 2, 0, 0.06, "panel", skip=("back",))
        m.box(sc - w / 2 - 0.12, sc - w / 2, yc - h / 2, yc + h / 2, 0, 0.14, "marble", skip=("back",))
        m.box(sc + w / 2, sc + w / 2 + 0.12, yc - h / 2, yc + h / 2, 0, 0.14, "marble", skip=("back",))
        m.box(sc - w / 2 - 0.12, sc + w / 2 + 0.12, yc + h / 2, yc + h / 2 + 0.12, 0, 0.14, "marble", skip=("back",))
        m.box(sc - w / 2 - 0.12, sc + w / 2 + 0.12, yc - h / 2 - 0.12, yc - h / 2, 0, 0.14, "marble", skip=("back",))
        k = min(w, h) * 0.32
        m.poly([(sc, yc - k * 1.4, 0.09), (sc + k, yc, 0.09), (sc, yc + k * 1.4, 0.09), (sc - k, yc, 0.09)], "glaze")

    # ------------------------------------------------------------ in plan
    def baluster(self, x, z, y, h):
        if self.baluster_segs < 6:
            self.m.lathe([(0.075, y), (0.05, y + 0.12), (0.095, y + h * 0.42), (0.04, y + h * 0.8), (0.07, y + h * 0.88)], self.baluster_segs, "marble", cx=x, cz=z, cap=False)
        else:
            self.m.lathe([(0.075, y), (0.075, y + 0.08), (0.05, y + 0.12), (0.095, y + h * 0.42), (0.04, y + h * 0.78), (0.07, y + h * 0.84), (0.07, y + h * 0.88)], 6, "marble", cx=x, cz=z, cap=False)
        self.balusters += 1

    def rail(self, pts, y, h=None, posts=3.2, ends=True, spacing=0.36):
        """A balustrade along a polyline in plan; y the foot (a list per point for a sloping rail)."""
        m = self.m
        h = h or self.rail_h
        ys = y if isinstance(y, (list, tuple)) else [y] * len(pts)
        for (a, ya), (b, yb) in zip(zip(pts[:-1], ys[:-1]), zip(pts[1:], ys[1:])):
            ax, az = a
            bx, bz = b
            L = math.hypot(bx - ax, bz - az)
            if L < 0.05:
                continue
            ux, uz = (bx - ax) / L, (bz - az) / L
            nx, nz = -uz * 0.17, ux * 0.17
            for y0, y1, wd in ((0, 0.14, 1.0), (h - 0.12, h, 1.15)):
                q = [(ax + nx * wd, ya + y0, az + nz * wd), (bx + nx * wd, yb + y0, bz + nz * wd), (bx - nx * wd, yb + y0, bz - nz * wd), (ax - nx * wd, ya + y0, az - nz * wd)]
                top = [(p[0], p[1] + (y1 - y0), p[2]) for p in q]
                m.poly(top, "marble")
                m.poly([q[0], q[1], top[1], top[0]], "marble")
                m.poly([q[3], q[2], top[2], top[3]], "marble")
            n = max(1, int(L / spacing))
            for k in range(n):
                t = (k + 0.5) / n
                self.baluster(ax + (bx - ax) * t, az + (bz - az) * t, ya + (yb - ya) * t + 0.14, h - 0.26)
            npost = max(1, round(L / posts))
            for k in range(npost + 1) if ends else range(1, npost):
                t = k / npost
                x, z, yy = ax + (bx - ax) * t, az + (bz - az) * t, ya + (yb - ya) * t
                m.box(x - 0.2, x + 0.2, yy, yy + h + 0.06, z - 0.2, z + 0.2, "marble")

    def urn(self, x, z, y, s=1.0):
        self.m.lathe([(0.2 * s, y), (0.2 * s, y + 0.1 * s), (0.08 * s, y + 0.16 * s), (0.24 * s, y + 0.42 * s), (0.18 * s, y + 0.62 * s), (0.08 * s, y + 0.7 * s), (0.11 * s, y + 0.8 * s), (0.0, y + 0.95 * s)], 8, "marble", cx=x, cz=z, cap=False)

    def jet(self, x, z, y, h, r, n=6, lean=(0.0, 0.0)):
        """A plain jet as a thin cone, its tip leaning by `lean` (dx, dz) metres."""
        ring = [(x + r * math.cos(2 * math.pi * k / n), z + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
        tip = (x + lean[0], y + h, z + lean[1])
        for i in range(n):
            a, b = ring[i], ring[(i + 1) % n]
            self.m.poly([(a[0], y, a[1]), (b[0], y, b[1]), tip], "jet")

    # ------------------------------------------------------------ roofs
    def roof_hip(self, cx, cz, hx, hz, y0, y1, n=6, lift=0.35, along="x", doc=None, ridge_y=0.35, ends=True):
        """Concave hip roof over a rectangle centred (cx, cz), half sizes hx (along x) and hz; the ridge along `along`. Corners lifted.
        doc: the sides drawn as documented (a set of 'N', 'S', 'E', 'W' for -z, +z, +x, -x); the others go to the fill class. Returns the eave corners and ridge ends."""
        m = self.m
        if along == "z":
            hx, hz = hz, hx
        rl = max(hx - hz, 0.4)
        rings = []
        for k in range(n + 1):
            t = k / n
            rings.append((hx + (rl - hx) * t, hz * (1 - t) + 0.02 * t, y0 + (y1 - y0) * (t ** 1.45), lift * (1 - t) ** 2))
        keep = m.cls

        def P(a, y, b):  # (along, y, across) -> (x, y, z)
            return (cx + a, y, cz + b) if along == "x" else (cx + b, y, cz + a)

        for k in range(n):
            (x0, z0, ya, la), (x1, z1, yb, lb) = rings[k], rings[k + 1]
            mat = "roofedge" if k == 0 else "roof"
            for sz in (1, -1):
                side = ("S" if sz > 0 else "N") if along == "x" else ("E" if sz > 0 else "W")
                if doc is not None:
                    m.cls = "doc" if side in doc else "fill"
                m.poly([P(-x0, ya + la, sz * z0), P(x0, ya + la, sz * z0), P(x1, yb + lb, sz * z1), P(-x1, yb + lb, sz * z1)], mat)
            for sa in (1, -1):
                side = ("E" if sa > 0 else "W") if along == "x" else ("S" if sa > 0 else "N")
                if doc is not None:
                    m.cls = "doc" if side in doc else "fill"
                for sz in (1, -1):
                    m.poly([P(sa * x0, ya + la, sz * z0), P(sa * x1, yb + lb, sz * z1), P(sa * x1, yb, 0), P(sa * x0, ya, 0)], mat)
        m.cls = keep
        x0, z0, ya, la = rings[0]
        m.poly([P(-x0, ya + la, z0), P(x0, ya + la, z0), P(x0, ya + la, -z0), P(-x0, ya + la, -z0)], "ridge")
        # the ridge with a glazed cap and ornaments at its ends (plates 10-13: crests on every ridge end)
        a0, a1 = P(-rl - 0.2, 0, 0), P(rl + 0.2, 0, 0)
        if along == "x":
            m.box(cx - rl - 0.2, cx + rl + 0.2, y1 - 0.05, y1 + ridge_y, cz - 0.18, cz + 0.18, "ridge")
        else:
            m.box(cx - 0.18, cx + 0.18, y1 - 0.05, y1 + ridge_y, cz - rl - 0.2, cz + rl + 0.2, "ridge")
        if ends and rl < 1.0:  # a short ridge (a square pavilion roof): one crowning ornament on its middle
            c = P(0, 0, 0)
            m.lathe([(0.45, y1 + ridge_y - 0.05), (0.45, y1 + ridge_y + 0.15), (0.25, y1 + ridge_y + 0.3), (0.38, y1 + ridge_y + 0.65), (0.15, y1 + ridge_y + 0.95), (0.0, y1 + ridge_y + 1.1)], 8, "ridge", cx=c[0], cz=c[2], cap=False)
        elif ends:
            for sa in (-1, 1):
                e = P(sa * rl, 0, 0)
                m.box(e[0] - 0.18, e[0] + 0.18, y1 + ridge_y - 0.05, y1 + ridge_y + 0.45, e[2] - 0.18, e[2] + 0.18, "ridge")
        out = {"ridge": [P(-rl, y1 + ridge_y, 0), P(rl, y1 + ridge_y, 0)], "eaves": {}}
        for sa in (-1, 1):
            for sz in (-1, 1):
                p = P(sa * x0, ya + la, sz * z0)
                out["eaves"][(1 if p[0] > cx else -1, 1 if p[2] > cz else -1)] = p
        return out

    # ------------------------------------------------------------ Round 30: the east end's ornament (线法山门, 螺蛳牌楼, 线法墙), in a face frame
    def shell(self, sc, yb, r, d=0.0, ribs=9, mat="sculpt", rib_mat="marble", depth=0.18):
        """A scallop shell standing on its hinge at (sc, yb): a fan of ribs, alternately raised (plates 17 and 19: over the doors and the arch)."""
        m = self.m
        pts = [(sc + r * math.cos(math.pi * k / ribs), yb + r * 1.05 * math.sin(math.pi * k / ribs)) for k in range(ribs + 1)]
        for k in range(ribs):
            dd = d + (depth if k % 2 == 0 else depth * 0.55)
            m.poly([(sc, yb, d + 0.04), (pts[k][0], pts[k][1], dd), (pts[k + 1][0], pts[k + 1][1], dd)], mat if k % 2 == 0 else rib_mat)
        m.box(sc - r * 0.35, sc + r * 0.35, yb - 0.12, yb + 0.02, d, d + depth + 0.04, mat, skip=("back",))

    def wreath(self, sc, yc, r, d=0.0, tube=0.12, n=14, mat="sculpt", width_y=1.0):
        """A ring of laurel standing in the face's plane (plate 17: the garland over the gate's centre)."""
        m = self.m
        for k in range(n):
            a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
            p0 = (sc + r * math.cos(a0), yc + r * width_y * math.sin(a0))
            p1 = (sc + r * math.cos(a1), yc + r * width_y * math.sin(a1))
            for dd in (d - tube, d + tube):
                q0 = (sc + (r - tube) * math.cos(a0), yc + (r - tube) * width_y * math.sin(a0))
                q1 = (sc + (r - tube) * math.cos(a1), yc + (r - tube) * width_y * math.sin(a1))
                o0 = (sc + (r + tube) * math.cos(a0), yc + (r + tube) * width_y * math.sin(a0))
                o1 = (sc + (r + tube) * math.cos(a1), yc + (r + tube) * width_y * math.sin(a1))
                m.poly([(q0[0], q0[1], dd), (o0[0], o0[1], dd), (o1[0], o1[1], dd), (q1[0], q1[1], dd)], mat)
            m.poly([(p0[0] + tube * math.cos(a0), p0[1] + tube * math.sin(a0), d - tube), (p1[0] + tube * math.cos(a1), p1[1] + tube * math.sin(a1), d - tube),
                    (p1[0] + tube * math.cos(a1), p1[1] + tube * math.sin(a1), d + tube), (p0[0] + tube * math.cos(a0), p0[1] + tube * math.sin(a0), d + tube)], mat)

    def slab(self, outline, d0, d1, mat="sculpt"):
        """A cut-out panel (a scrolled crest, a cartouche's outline) between the planes d0 and d1: the outline (s, y), convex pieces or a fan from its first point."""
        m = self.m
        m.poly([(s, y, d1) for s, y in outline], mat)
        m.poly([(s, y, d0) for s, y in outline[::-1]], mat)
        n = len(outline)
        for i in range(n):
            (a, b), (c, e) = outline[i], outline[(i + 1) % n]
            m.poly([(a, b, d0), (c, e, d0), (c, e, d1), (a, b, d1)], mat)

    def scroll(self, sc, y0, h, w, sx=1, d=0.0, t=0.2, mat="sculpt", n=10):
        """A volute in profile, its curl at the foot (plate 17: the buttress scrolls at the gate's ends; plate 19: the crest's consoles): a band that sweeps out by w over the height h and curls in."""
        pts = []
        for k in range(n + 1):
            u = k / n
            pts.append((sc + sx * w * (1 - u) ** 1.6, y0 + h * u))
        curl = [(sc + sx * (w - 0.5 * w * (1 - math.cos(math.pi * j / 6)) * 0.6), y0 + 0.3 * w * math.sin(math.pi * j / 6)) for j in range(7)]
        outer = curl[::-1] + pts[1:]
        inner = [(s - sx * min(t, abs(s - sc)), y) for s, y in outer]
        for (a, b), (c, e), (f, g), (p, q) in zip(outer[:-1], outer[1:], inner[1:], inner[:-1]):
            self.m.poly([(a, b, d - t / 2), (c, e, d - t / 2), (f, g, d - t / 2), (p, q, d - t / 2)], mat)
            self.m.poly([(p, q, d + t / 2), (f, g, d + t / 2), (c, e, d + t / 2), (a, b, d + t / 2)], mat)
            self.m.poly([(a, b, d - t / 2), (a, b, d + t / 2), (c, e, d + t / 2), (c, e, d - t / 2)], mat)

    def rusticated(self, s0, s1, y0, y1, course=0.62, out=0.14, mat="rustic", joint="joint", bands=True):
        """A pier of banded blocks (plate 20: the gates of 线法墙): projecting blocks on a recessed core, the joints dark."""
        m = self.m
        m.box(s0, s1, y0, y1, 0.0, out * 0.4, joint, skip=("back",))
        y = y0
        k = 0
        while y < y1 - 0.05:
            yt = min(y + course - 0.08, y1)
            inset = 0.0 if k % 2 == 0 else 0.12
            m.box(s0 + inset, s1 - inset, y + 0.04, yt, out * 0.4, out, mat, skip=("back",))
            if bands and (s1 - s0) > 1.2:
                mid = (s0 + s1) / 2 + (0.25 if k % 2 else -0.25)
                m.box(mid - 0.03, mid + 0.03, y + 0.04, yt, out, out + 0.01, joint, skip=("back",))
            y += course
            k += 1
