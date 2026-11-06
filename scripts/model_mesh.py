"""Mesh and GLB writer for the detailed models (models/<ID>-<slug>/). Imported, not run. Round 13.

Pattern of the Küstrin models (kostrzyn-yaga-sh models/B01-schloss/mesh_lib.py): triangles per material, flat-shaded, written as one node with one mesh.
New here: every primitive carries a grade class, `doc` (the form is shown on a plate or photograph of this building) or `fill` (carried round from the documented bays, or typology: assumed, C);
the material is named `<material>` or `<material>~fill`, which the view uses for ?assumed=0 and ?conf=1. All materials double-sided, so winding never matters.
Positions are quantised to uint16 with the node's scale and translation (KHR_mesh_quantization), normals int8: what site/reconstruction/glb_lite.js reads.
Frame: x along the main front (east), y up from the model's base, z out of the main front (south for 谐奇趣), metres.
"""

import json
import math
import struct

import numpy as np


def srgb_to_linear(hexstr):
    c = [int(hexstr[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]


def ear_clip(pts):
    """Triangles of a simple polygon (2D, either winding), by ear clipping. Indices into pts."""
    n = len(pts)
    if n < 3:
        return []
    P = np.asarray(pts, float)
    area = 0.5 * sum(P[i, 0] * P[(i + 1) % n, 1] - P[(i + 1) % n, 0] * P[i, 1] for i in range(n))
    idx = list(range(n)) if area > 0 else list(range(n))[::-1]
    out = []

    def inside(p, a, b, c):
        d1 = (p[0] - b[0]) * (a[1] - b[1]) - (a[0] - b[0]) * (p[1] - b[1])
        d2 = (p[0] - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (p[1] - c[1])
        d3 = (p[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (p[1] - a[1])
        return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))

    guard = 0
    while len(idx) > 3 and guard < 10000:
        guard += 1
        m = len(idx)
        for k in range(m):
            i0, i1, i2 = idx[(k - 1) % m], idx[k], idx[(k + 1) % m]
            a, b, c = P[i0], P[i1], P[i2]
            if (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) <= 1e-12:
                continue
            if any(inside(P[j], a, b, c) for j in idx if j not in (i0, i1, i2)):
                continue
            out.append((i0, i1, i2))
            idx.pop(k)
            break
        else:
            break
    if len(idx) == 3:
        out.append(tuple(idx))
    return out


class Mesh:
    def __init__(self, colours):
        self.colours = colours  # material -> "#rrggbb"
        self.prims = {}
        self.cls = "doc"
        self._stack = [(np.zeros(3), 0.0)]

    # ---- frames: a translation and a turn about y, nested ----
    def push(self, x=0.0, y=0.0, z=0.0, rot=0.0):
        t0, r0 = self._stack[-1]
        c, s = math.cos(r0), math.sin(r0)
        off = np.array([c * x + s * z, y, -s * x + c * z])
        self._stack.append((t0 + off, r0 + rot))

    def pop(self):
        self._stack.pop()

    def _tf(self, p):
        t, r = self._stack[-1]
        c, s = math.cos(r), math.sin(r)
        x, y, z = p
        return np.array([c * x + s * z, y, -s * x + c * z]) + t

    def world(self, p):
        return self._tf(np.asarray(p, float))

    def _p(self, mat):
        key = mat if self.cls == "doc" else f"{mat}~fill"
        return self.prims.setdefault(key, {"pos": [], "nor": [], "idx": []})

    # ---- primitives ----
    def poly(self, pts, mat):
        """A planar polygon (convex, or simple and given flat), any winding."""
        pts = [self._tf(np.asarray(q, float)) for q in pts]
        n = np.zeros(3)
        for i in range(1, len(pts) - 1):
            n = n + np.cross(pts[i] - pts[0], pts[i + 1] - pts[0])
        ln = np.linalg.norm(n)
        if ln < 1e-10:
            return
        n = n / ln
        p = self._p(mat)
        base = len(p["pos"])
        p["pos"] += [q.tolist() for q in pts]
        p["nor"] += [n.tolist()] * len(pts)
        for i in range(1, len(pts) - 1):
            p["idx"] += [base, base + i, base + i + 1]

    def tri(self, a, b, c, mat):
        self.poly([a, b, c], mat)

    def flat(self, pts2, y, mat):
        """A horizontal simple polygon (x, z) at height y, non-convex allowed."""
        for i, j, k in ear_clip(pts2):
            self.poly([(pts2[i][0], y, pts2[i][1]), (pts2[j][0], y, pts2[j][1]), (pts2[k][0], y, pts2[k][1])], mat)

    def box(self, x0, x1, y0, y1, z0, z1, mat, skip=()):
        if x1 - x0 < 1e-6 or y1 - y0 < 1e-6 or z1 - z0 < 1e-6:
            return
        f = {
            "front": [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
            "back": [(x1, y0, z0), (x0, y0, z0), (x0, y1, z0), (x1, y1, z0)],
            "left": [(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)],
            "right": [(x1, y0, z1), (x1, y0, z0), (x1, y1, z0), (x1, y1, z1)],
            "top": [(x0, y1, z1), (x1, y1, z1), (x1, y1, z0), (x0, y1, z0)],
            "bottom": [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
        }
        for k, v in f.items():
            if k not in skip:
                self.poly(v, mat)

    def prism(self, pts2, y0, y1, mat, top=True, bottom=False, side_mat=None):
        """A vertical extrusion of a simple polygon (x, z)."""
        n = len(pts2)
        for i in range(n):
            (ax, az), (bx, bz) = pts2[i], pts2[(i + 1) % n]
            self.poly([(ax, y0, az), (bx, y0, bz), (bx, y1, bz), (ax, y1, az)], side_mat or mat)
        if top:
            self.flat(pts2, y1, mat)
        if bottom:
            self.flat(pts2, y0, mat)

    def frustum(self, pts_lo, pts_hi, y0, y1, mat):
        """Sides between two rings of the same count (a tapering shaft, a roof skirt)."""
        n = len(pts_lo)
        for i in range(n):
            a, b = pts_lo[i], pts_lo[(i + 1) % n]
            c, d = pts_hi[(i + 1) % n], pts_hi[i]
            self.poly([(a[0], y0, a[1]), (b[0], y0, b[1]), (c[0], y1, c[1]), (d[0], y1, d[1])], mat)

    def lathe(self, profile, segs, mat, cx=0.0, cz=0.0, cap=True):
        """A turned solid (a baluster, an urn, a finial): profile [(r, y), ...] from bottom to top."""
        ring = lambda r: [(cx + r * math.cos(2 * math.pi * k / segs), cz + r * math.sin(2 * math.pi * k / segs)) for k in range(segs)]
        for (r0, y0), (r1, y1) in zip(profile[:-1], profile[1:]):
            if r0 < 1e-4 and r1 < 1e-4:
                continue
            lo, hi = ring(max(r0, 1e-4)), ring(max(r1, 1e-4))
            self.frustum(lo, hi, y0, y1, mat)
        if cap and profile[-1][0] > 1e-3:
            self.flat(ring(profile[-1][0]), profile[-1][1], mat)

    def count(self):
        return sum(len(p["idx"]) // 3 for p in self.prims.values())

    # ---- writing ----
    def write_glb(self, path, name, extras=None):
        prims = {k: v for k, v in self.prims.items() if v["idx"]}
        allpos = np.concatenate([np.asarray(v["pos"], float) for v in prims.values()])
        lo, hi = allpos.min(0), allpos.max(0)
        scale = np.maximum(hi - lo, 1e-6) / 65535.0
        bin_ = bytearray()
        views, accs, gprims, mats = [], [], [], []

        def add_view(data, stride=None, target=None):
            while len(bin_) % 4:
                bin_.append(0)
            v = {"buffer": 0, "byteOffset": len(bin_), "byteLength": len(data)}
            if stride:
                v["byteStride"] = stride
            if target:
                v["target"] = target
            bin_.extend(data)
            views.append(v)
            return len(views) - 1

        for key in sorted(prims):
            v = prims[key]
            pos = np.asarray(v["pos"], float)
            nor = np.asarray(v["nor"], float)
            idx = np.asarray(v["idx"], np.uint32)
            # split into chunks of < 65536 vertices so indices stay uint16
            tris = idx.reshape(-1, 3)
            start = 0
            while start < len(tris):
                chunk, used = [], {}
                while start < len(tris):
                    t = tris[start]
                    new = [i for i in t if i not in used]
                    if len(used) + len(new) > 65535:
                        break
                    for i in new:
                        used[i] = len(used)
                    chunk.append([used[i] for i in t])
                    start += 1
                order = np.array(sorted(used, key=used.get), np.int64)
                q = np.round((pos[order] - lo) / scale).astype(np.uint16)
                qp = np.zeros((len(order), 4), np.uint16)
                qp[:, :3] = q
                nn = np.zeros((len(order), 4), np.int8)
                nn[:, :3] = np.round(nor[order] * 127).astype(np.int8)
                ci = np.asarray(chunk, np.uint16).ravel()
                vp = add_view(qp.tobytes(), 8, 34962)
                vn = add_view(nn.tobytes(), 4, 34962)
                vi = add_view(ci.tobytes(), None, 34963)
                qmin, qmax = q.min(0), q.max(0)
                accs.append({"bufferView": vp, "componentType": 5123, "count": len(order), "type": "VEC3", "min": qmin.tolist(), "max": qmax.tolist()})
                ap = len(accs) - 1
                accs.append({"bufferView": vn, "componentType": 5120, "normalized": True, "count": len(order), "type": "VEC3"})
                an = len(accs) - 1
                accs.append({"bufferView": vi, "componentType": 5123, "count": len(ci), "type": "SCALAR"})
                ai = len(accs) - 1
                mat_name = key
                if mat_name not in [m["name"] for m in mats]:
                    base = key.split("~")[0]
                    col = srgb_to_linear(self.colours[base])
                    mats.append({"name": mat_name, "doubleSided": True, "pbrMetallicRoughness": {"baseColorFactor": col + [1.0], "metallicFactor": 0.0, "roughnessFactor": 0.9}})
                mi = [m["name"] for m in mats].index(mat_name)
                gprims.append({"attributes": {"POSITION": ap, "NORMAL": an}, "indices": ai, "material": mi})
        gltf = {
            "asset": {"version": "2.0", "generator": "palace-beijing-yaga-sh scripts/model_mesh.py"},
            "extensionsUsed": ["KHR_mesh_quantization"], "extensionsRequired": ["KHR_mesh_quantization"],
            "scene": 0, "scenes": [{"nodes": [0]}],
            "nodes": [{"name": name, "mesh": 0, "translation": lo.tolist(), "scale": scale.tolist(), "extras": extras or {}}],
            "meshes": [{"primitives": gprims}], "materials": mats, "accessors": accs, "bufferViews": views,
            "buffers": [{"byteLength": 0}],
        }
        while len(bin_) % 4:
            bin_.append(0)
        gltf["buffers"][0]["byteLength"] = len(bin_)
        js = json.dumps(gltf, separators=(",", ":")).encode()
        js += b" " * ((4 - len(js) % 4) % 4)
        out = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(bin_))
        out += struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(bin_), 0x004E4942) + bytes(bin_)
        with open(path, "wb") as fh:
            fh.write(out)
        return len(out)


def read_glb(path):
    """The JSON and the binary chunk of a GLB, and the positions of every primitive in model metres (for checks)."""
    data = open(path, "rb").read()
    magic, ver, total = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67 and total == len(data), "not a GLB"
    jl = struct.unpack("<I", data[12:16])[0]
    g = json.loads(data[20:20 + jl])
    b0 = 20 + jl + 8
    node = g["nodes"][0]
    sc, tr = np.array(node.get("scale", [1, 1, 1])), np.array(node.get("translation", [0, 0, 0]))
    out = {}
    for pr in g["meshes"][0]["primitives"]:
        a = g["accessors"][pr["attributes"]["POSITION"]]
        v = g["bufferViews"][a["bufferView"]]
        raw = np.frombuffer(data, np.uint16, count=a["count"] * 4, offset=b0 + v["byteOffset"]).reshape(-1, 4)[:, :3]
        name = g["materials"][pr["material"]]["name"]
        out.setdefault(name, []).append(raw * sc + tr)
    return g, {k: np.concatenate(v) for k, v in out.items()}
