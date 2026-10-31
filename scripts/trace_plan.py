#!/usr/bin/env python3
"""Trace the Princeton plan (S01) into vector regions, in plan pixels.

Input:  research/raw/plans/princeton_mosaic.jpg (12955 x 9049, gitignored)
        research/plan/bridges_manual.json   short ink lines that repair gaps (each with a reason)
        research/plan/classes_manual.csv    class of a region, given by a point inside it
        research/plan/walls_manual.json     walls, picked by eye from crops
        research/plan/gates_manual.json     gates, read from crops at full zoom
        research/plan/slips_manual.json     pasted slips and patches, outlined by eye
Output: research/plan/regions.json, regions_classified.csv, blocks.csv, walls.json, gates.json,
        slips.json, trace_summary.json
        Review images (never committed): screenshots/r1/trace_*

Everything is deterministic: no random numbers, no hidden state. Numbers in the summary come from
this run. The scratch cache only speeds up a rerun and holds no data of its own: `--fresh` ignores it.

    .venv/bin/python scripts/trace_plan.py [--fresh] [--no-review]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
from shapely.geometry import LineString, MultiPoint, Point, Polygon
from shapely.strtree import STRtree

Image.MAX_IMAGE_PIXELS = None

ROOT = Path(__file__).resolve().parent.parent
MOSAIC = ROOT / "research/raw/plans/princeton_mosaic.jpg"
OUT = ROOT / "research/plan"
SHOTS = ROOT / "screenshots/r1"
CACHE = Path("/opt/data/cache/scratch/palace_r1b_trace/cache")

# --- ink ---
BG_BLOCK = 8            # background is estimated on blocks of this many pixels
T_LO, T_HI = 35, 70     # hysteresis on (local paper brightness - max(R,G,B)); max() ignores blue and green tints
MIN_INK = 15            # ink specks smaller than this (px) are dropped

# --- scroll gaps: x range cleared of ink, and the columns the lines are sampled at on each side ---
SEAMS = [
    {"name": "a|b", "clear": (4314, 4330), "xl": 4312, "xr": 4332, "max_dy": 24},
    {"name": "b|c", "clear": (8605, 8680), "xl": 8604, "xr": 8684, "max_dy": 45},
]
MAX_RUN = 24            # an ink run longer than this at a sampling column runs along the seam: no stitch

# --- regions: radii of the erosion, largest first (a gap narrower than 2r does not leak at that level),
# with the smallest eroded area a new seed must have at that level ---
LEVELS = [(10, 3000), (6, 800), (3, 300)]
MIN_REGION = 1500       # px2, the brief's limit for a region
MIN_HOLE = 1500         # holes smaller than this are filled in the polygon (labels, specks, hall bays)
SIMPLIFY = 1.5          # px


def log(*a):
    print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)


# ---------------------------------------------------------------------------------------- ink
def block_percentile(v: np.ndarray, s: int, q: float) -> np.ndarray:
    h, w = v.shape[0] // s, v.shape[1] // s
    return np.percentile(v[: h * s, : w * s].reshape(h, s, w, s), q, axis=(1, 3)).astype(np.float32)


def load_rgb() -> np.ndarray:
    return np.asarray(Image.open(MOSAIC).convert("RGB"))


def make_ink(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return the ink mask, the mount mask and the sharper mask used for the hall bays (full resolution)."""
    h, w = rgb.shape[:2]
    v = rgb.max(axis=2)
    small = block_percentile(v, BG_BLOCK, 75)
    bg = ndi.median_filter(ndi.grey_closing(small, size=5), size=9, mode="nearest")
    bgf = np.asarray(Image.fromarray(bg).resize((w, h), Image.BILINEAR))
    dark = np.clip(bgf - v.astype(np.float32), 0, 255)
    del v, bgf
    lo, hi = dark > T_LO, dark > T_HI
    thin = dark > T_CELL
    del dark
    lab, n = ndi.label(lo, structure=np.ones((3, 3), bool))
    keep = np.zeros(n + 1, bool)
    keep[np.unique(lab[hi])] = True
    size = np.bincount(lab.ravel(), minlength=n + 1)
    keep &= size >= MIN_INK
    keep[0] = False
    ink = keep[lab]
    del lab, lo
    # the mount is the saturated yellow silk round the paper
    hs, ws = h // BG_BLOCK, w // BG_BLOCK
    rs = np.stack(
        [rgb[: hs * BG_BLOCK, : ws * BG_BLOCK, c].reshape(hs, BG_BLOCK, ws, BG_BLOCK).mean(axis=(1, 3)) for c in range(3)],
        -1,
    ).astype(np.float32)
    yb = (rs[..., 0] + rs[..., 1]) / 2 - rs[..., 2]
    mount_s = ndi.binary_opening(ndi.median_filter(yb, size=5) > 44, structure=np.ones((9, 9), bool))
    ml, mn = ndi.label(mount_s)
    edge = np.unique(np.r_[ml[0], ml[-1], ml[:, 0], ml[:, -1]])
    mount_s = np.isin(ml, edge[edge > 0])
    mount = np.asarray(Image.fromarray(mount_s.astype(np.uint8)).resize((w, h), Image.NEAREST)).astype(bool)
    ink[mount] = False
    thin[mount] = False
    for seam in SEAMS:
        thin[:, seam["clear"][0] : seam["clear"][1]] = False
    thin = ndi.binary_closing(thin, structure=np.ones((3, 3), bool))
    return ink, mount, thin


def runs(col: np.ndarray) -> list[tuple[int, int]]:
    d = np.diff(np.r_[0, col.astype(np.int8), 0])
    return list(zip(np.flatnonzero(d == 1).tolist(), (np.flatnonzero(d == -1) - 1).tolist()))


def stitch_seam(ink: np.ndarray, seam: dict) -> list[tuple[int, int, int, int]]:
    """Clear the gap and join the ink runs on both sides by a monotone alignment. Return the new lines."""
    a, b = seam["clear"]
    ink[:, a:b] = False
    xl, xr = seam["xl"], seam["xr"]
    left = [(s + e) / 2 for s, e in runs(ink[:, xl]) if e - s < MAX_RUN]
    right = [(s + e) / 2 for s, e in runs(ink[:, xr]) if e - s < MAX_RUN]
    n, m = len(left), len(right)
    skip = 1.0
    cost = np.zeros((n + 1, m + 1))
    cost[:, 0] = np.arange(n + 1) * skip
    cost[0, :] = np.arange(m + 1) * skip
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            dy = abs(left[i - 1] - right[j - 1])
            match = cost[i - 1, j - 1] + (dy / seam["max_dy"] if dy <= seam["max_dy"] else 1e6)
            cost[i, j] = min(match, cost[i - 1, j] + skip, cost[i, j - 1] + skip)
    lines = []
    i, j = n, m
    while i > 0 and j > 0:
        dy = abs(left[i - 1] - right[j - 1])
        if dy <= seam["max_dy"] and abs(cost[i, j] - (cost[i - 1, j - 1] + dy / seam["max_dy"])) < 1e-9:
            lines.append((xl, int(left[i - 1]), xr, int(right[j - 1])))
            i, j = i - 1, j - 1
        elif abs(cost[i, j] - (cost[i - 1, j] + skip)) < 1e-9:
            lines.append((xl, int(left[i - 1]), (a + b) // 2, int(left[i - 1])))
            i -= 1
        else:
            lines.append(((a + b) // 2, int(right[j - 1]), xr, int(right[j - 1])))
            j -= 1
    return lines


def draw_lines(ink: np.ndarray, lines, width: int = 3) -> None:
    """Burn straight lines into the mask. Pixels are computed directly, so the mask stays one array."""
    h, w = ink.shape
    r = width // 2
    for x0, y0, x1, y1 in lines:
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        xs = np.round(np.linspace(x0, x1, n)).astype(int)
        ys = np.round(np.linspace(y0, y1, n)).astype(int)
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                xx, yy = np.clip(xs + dx, 0, w - 1), np.clip(ys + dy, 0, h - 1)
                ink[yy, xx] = True


# ------------------------------------------------------------------------------------ regions
CROSS = ndi.generate_binary_structure(2, 1)


def grow(labels: np.ndarray, allowed: np.ndarray, n: int) -> None:
    """Geodesic growth of labels into allowed pixels, n steps of 4-neighbours. Ties: the larger id."""
    for _ in range(n):
        d = ndi.grey_dilation(labels, footprint=CROSS)
        new = (labels == 0) & allowed & (d > 0)
        if not new.any():
            break
        labels[new] = d[new]


def make_regions(free: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    dist = ndi.distance_transform_edt(free).astype(np.float32)
    labels = np.zeros(free.shape, np.int32)
    nxt = 1
    prev = None
    for r, min_seed in LEVELS:
        m = dist > r
        if prev is not None:
            grow(labels, m, prev - r + 1)
        rest = m & (labels == 0)
        l, n = ndi.label(rest)
        size = np.bincount(l.ravel(), minlength=n + 1)
        ok = np.flatnonzero(size >= min_seed)
        ok = ok[ok > 0]
        remap = np.zeros(n + 1, np.int32)
        remap[ok] = np.arange(nxt, nxt + len(ok))
        nxt += len(ok)
        labels[rest] = remap[l[rest]]
        log(f"  level r={r}: {len(ok)} new seeds, {nxt - 1} in all")
        prev = r
    grow(labels, free, prev + 3)
    return labels, dist


def crack_rings(mask: np.ndarray) -> list[list[tuple[int, int]]]:
    """All boundary rings of a boolean mask, as vertex lists on the pixel corners (inside on the right)."""
    m = np.pad(mask, 1).astype(np.int8)
    next_v: dict[tuple[int, int], list[tuple[int, int]]] = {}
    dv = m[1:, :] - m[:-1, :]  # horizontal cracks between row y-1 and y
    dh = m[:, 1:] - m[:, :-1]  # vertical cracks between col x-1 and x
    for y, x in zip(*np.nonzero(dv > 0)):
        next_v.setdefault((int(x), int(y) + 1), []).append((int(x) + 1, int(y) + 1))
    for y, x in zip(*np.nonzero(dv < 0)):
        next_v.setdefault((int(x) + 1, int(y) + 1), []).append((int(x), int(y) + 1))
    for y, x in zip(*np.nonzero(dh > 0)):
        next_v.setdefault((int(x) + 1, int(y) + 1), []).append((int(x) + 1, int(y)))
    for y, x in zip(*np.nonzero(dh < 0)):
        next_v.setdefault((int(x) + 1, int(y)), []).append((int(x) + 1, int(y) + 1))
    rings = []
    while next_v:
        start = min(next_v)
        ring = [start]
        cur = start
        prev_d = None
        while True:
            opts = next_v[cur]
            if len(opts) == 1 or prev_d is None:
                nx = opts.pop(0)
            else:
                # at a diagonal touch keep the region 4-connected: turn right
                rd = (-prev_d[1], prev_d[0])
                pick = next((o for o in opts if (o[0] - cur[0], o[1] - cur[1]) == rd), opts[0])
                opts.remove(pick)
                nx = pick
            if not opts:
                del next_v[cur]
            prev_d = (nx[0] - cur[0], nx[1] - cur[1])
            cur = nx
            if cur == start:
                break
            ring.append(cur)
        rings.append([(x - 1, y - 1) for x, y in ring])
    return rings


def ring_area(r) -> float:
    a = np.asarray(r, float)
    return abs(np.dot(a[:, 0], np.roll(a[:, 1], -1)) - np.dot(a[:, 1], np.roll(a[:, 0], -1))) / 2


def simple_ring(r, ox, oy):
    p = Polygon(r).simplify(SIMPLIFY, preserve_topology=True)
    if p.is_empty or p.geom_type != "Polygon":
        return [[x + ox, y + oy] for x, y in r]
    return [[int(round(x)) + ox, int(round(y)) + oy] for x, y in list(p.exterior.coords)[:-1]]


def region_table(labels: np.ndarray, dist: np.ndarray, rgb: np.ndarray) -> tuple[list[dict], np.ndarray]:
    """Number the regions by area (largest = R0001), measure them and trace their polygons."""
    n = int(labels.max())
    size = np.bincount(labels.ravel(), minlength=n + 1)
    size[0] = 0
    ok = np.flatnonzero(size >= MIN_REGION)
    ok = ok[np.argsort(-size[ok], kind="stable")]
    remap = np.zeros(n + 1, np.int32)
    remap[ok] = np.arange(1, len(ok) + 1)
    labels = remap[labels]
    k = len(ok)
    # tint stats on a 1/2 grid, on paper at least 6 px off the ink. yb = (R+G)/2-B, gr = G-R
    step = 2
    l2 = labels[::step, ::step]
    d2 = dist[::step, ::step]
    r2, g2, b2 = [rgb[::step, ::step, c].astype(np.float32) for c in range(3)]
    yb, gr = (r2 + g2) / 2 - b2, g2 - r2
    lum = (r2 + g2 + b2) / 3

    def mean_on(mask, val):
        cnt = np.bincount(l2[mask], minlength=k + 1).astype(float)
        tot = np.bincount(l2[mask], weights=val[mask], minlength=k + 1)
        with np.errstate(invalid="ignore", divide="ignore"):
            out = tot / cnt
        return out

    core = d2 > 6
    yb_m, gr_m, lum_m = mean_on(core, yb), mean_on(core, gr), mean_on(core, lum)
    rim = (d2 > 6) & (d2 <= 30)
    yb_r, gr_r = mean_on(rim, yb), mean_on(rim, gr)
    mid = d2 > 40
    yb_c, gr_c = mean_on(mid, yb), mean_on(mid, gr)
    del r2, g2, b2, yb, gr, lum, rim, mid, core

    objs = ndi.find_objects(labels, max_label=k)
    out = []
    for i, sl in enumerate(objs, 1):
        crop = labels[sl] == i
        y0, x0 = sl[0].start, sl[1].start
        rings = crack_rings(crop)
        rings.sort(key=ring_area, reverse=True)
        ext = rings[0]
        holes = [r for r in rings[1:] if ring_area(r) >= MIN_HOLE]
        filled = ring_area(ext)
        ys, xs = np.nonzero(crop)
        # a point well inside: the deepest pixel of the region
        dcrop = np.where(crop, dist[sl], 0)
        iy, ix = np.unravel_index(int(np.argmax(dcrop)), dcrop.shape)
        rec = {
            "region_id": f"R{i:04d}",
            "area_px": int(crop.sum()),
            "area_filled_px": int(filled),
            "centroid": [round(float(xs.mean()) + x0, 1), round(float(ys.mean()) + y0, 1)],
            "inner_point": [int(ix + x0), int(iy + y0)],
            "max_half_width_px": round(float(dcrop[iy, ix]), 1),
            "bbox": [x0, y0, sl[1].stop, sl[0].stop],
            "tint": {
                "yb": round(float(yb_m[i]), 2) if np.isfinite(yb_m[i]) else None,
                "gr": round(float(gr_m[i]), 2) if np.isfinite(gr_m[i]) else None,
                "lum": round(float(lum_m[i]), 1) if np.isfinite(lum_m[i]) else None,
                "yb_rim": round(float(yb_r[i]), 2) if np.isfinite(yb_r[i]) else None,
                "gr_rim": round(float(gr_r[i]), 2) if np.isfinite(gr_r[i]) else None,
                "yb_mid": round(float(yb_c[i]), 2) if np.isfinite(yb_c[i]) else None,
                "gr_mid": round(float(gr_c[i]), 2) if np.isfinite(gr_c[i]) else None,
            },
            "polygon": simple_ring(ext, x0, y0),
            "holes": [simple_ring(r, x0, y0) for r in holes],
        }
        out.append(rec)
    return out, labels



# --------------------------------------------------------------------------------- hall blocks
T_CELL = 70             # bay lines are thin: a sharper threshold than the regions use, then a 3x3 closing
CELL_ERODE = 0
CELL_MIN_AREA = 80      # px2: counters of the written characters are smaller
CELL_MAX_AREA = 4000
CELL_MIN_SIDE = 8       # px
CELL_MAX_LONG = 72      # px: a longer or deeper enclosure is a courtyard or a yard, not a bay
CELL_MAX_SHORT = 46
CELL_MAX_ASPECT = 9
CELL_MIN_RECT = 0.72    # hole-filled area / minimum-area rectangle: straight sides, not a shoreline lobe
GAP_MAX = 12            # px: largest ink wall between two bays of one hall
OVERLAP_MIN = 0.65      # shared wall as a share of the shorter side
SIDE_RATIO = 1.6        # the sides on the shared wall must agree this well (the row keeps its depth)
ANGLE_TOL = 12          # deg
SINGLE_MIN_SIDE = 14    # a lone cell counts only from this size
SINGLE_MIN_RECT = 0.85
BLOCK_MAX_SIDE = 700
BLOCK_MIN_FILL = 0.62   # bays / rectangle of the block: below this the group is not one hall


def min_rect(points: np.ndarray) -> tuple[float, float, float, float, float]:
    """Minimum-area rectangle: cx, cy, long side, short side, angle of the long side (deg, -90..90]."""
    hull = MultiPoint(points).convex_hull
    if hull.geom_type != "Polygon":
        x0, y0 = points.min(axis=0)
        x1, y1 = points.max(axis=0)
        return (x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0), min(x1 - x0, y1 - y0), 0.0
    h = np.asarray(hull.exterior.coords)
    best = None
    for (ax, ay), (bx, by) in zip(h[:-1], h[1:]):
        t = math.atan2(by - ay, bx - ax)
        c, s = math.cos(t), math.sin(t)
        u = h[:, 0] * c + h[:, 1] * s
        v = -h[:, 0] * s + h[:, 1] * c
        area = (u.max() - u.min()) * (v.max() - v.min())
        if best is None or area < best[0] - 1e-9:
            best = (area, t, u.min(), u.max(), v.min(), v.max())
    _, t, u0, u1, v0, v1 = best
    c, s = math.cos(t), math.sin(t)
    um, vm = (u0 + u1) / 2, (v0 + v1) / 2
    cx, cy = um * c - vm * s, um * s + vm * c
    du, dv = u1 - u0, v1 - v0
    ang = math.degrees(t)
    if dv > du:
        du, dv = dv, du
        ang += 90
    ang = (ang + 90) % 180 - 90
    if ang == -90:
        ang = 90.0
    return cx, cy, du, dv, ang


def find_cells(ink: np.ndarray, mount: np.ndarray) -> tuple[list[dict], np.ndarray]:
    free = ~((ndi.binary_dilation(ink, iterations=CELL_ERODE) if CELL_ERODE else ink) | mount)
    lab, n = ndi.label(free)
    size = np.bincount(lab.ravel(), minlength=n + 1)
    size[0] = 0
    ids = np.flatnonzero((size >= CELL_MIN_AREA // 2) & (size <= CELL_MAX_AREA))
    objs = ndi.find_objects(lab)
    cells = []
    for i in ids:
        sl = objs[i - 1]
        y0, x0 = sl[0].start, sl[1].start
        m = ndi.binary_fill_holes(lab[sl] == i)
        area = int(m.sum())
        if area < CELL_MIN_AREA // 2:
            continue
        ys, xs = np.nonzero(m)
        # corners of the boundary pixels are enough for the hull
        pts = np.c_[xs + x0 + 0.5, ys + y0 + 0.5]
        cx, cy, a, b, ang = min_rect(pts)
        a, b = a + 1, b + 1
        rect = area / max(a * b, 1)
        a2, b2 = a + 2 * CELL_ERODE, b + 2 * CELL_ERODE
        if b2 < CELL_MIN_SIDE or a2 / b2 > CELL_MAX_ASPECT or rect < CELL_MIN_RECT or a2 * b2 < CELL_MIN_AREA:
            continue
        if a2 > CELL_MAX_LONG or b2 > CELL_MAX_SHORT:
            continue
        cells.append({"cx": cx, "cy": cy, "a": a2, "b": b2, "ang": ang, "rect": rect, "area": area, "pts": pts[:: max(1, len(pts) // 200)]})
    return cells, lab


def axes(c):
    t = math.radians(c["ang"])
    return (math.cos(t), math.sin(t)), (-math.sin(t), math.cos(t))


def same_hall(A: dict, B: dict) -> bool:
    """Two bays belong together if they are parallel, share nearly a whole wall and keep the row's depth."""
    d = abs(A["ang"] - B["ang"]) % 90
    if min(d, 90 - d) > ANGLE_TOL:
        return False
    (ux, uy), (vx, vy) = axes(A)
    dx, dy = B["cx"] - A["cx"], B["cy"] - A["cy"]
    du, dv = dx * ux + dy * uy, dx * vx + dy * vy
    # half extents of B on A's axes
    aligned = min(d, 90 - d) == d
    bu, bv = (B["a"] / 2, B["b"] / 2) if aligned else (B["b"] / 2, B["a"] / 2)
    au, av = A["a"] / 2, A["b"] / 2
    if abs(du) > abs(dv) * 1:
        side_a, side_b, gap = av, bv, abs(du) - au - bu
        off = abs(dv)
    else:
        side_a, side_b, gap = au, bu, abs(dv) - av - bv
        off = abs(du)
    if gap > GAP_MAX or gap < -6:
        return False
    if max(side_a, side_b) / max(min(side_a, side_b), 1e-6) > SIDE_RATIO:
        return False
    overlap = min(off * -1 + side_a + side_b, 2 * min(side_a, side_b))
    return overlap >= OVERLAP_MIN * 2 * min(side_a, side_b)


def count_lines(vals: np.ndarray, tol: float) -> int:
    v = np.sort(vals)
    return int(1 + (np.diff(v) > tol).sum()) if len(v) else 0


def block_poly(b: dict) -> Polygon:
    t = math.radians(b["angle_deg"])
    c, s = math.cos(t), math.sin(t)
    pts = []
    for u, v in ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)):
        pts.append((b["cx"] + u * b["w_px"] * c - v * b["h_px"] * s, b["cy"] + u * b["w_px"] * s + v * b["h_px"] * c))
    return Polygon(pts)


def drop_nested(blocks: list[dict]) -> list[dict]:
    """A block lying 70 % inside a larger block is the same hall seen twice: keep the larger."""
    order = sorted(range(len(blocks)), key=lambda i: -blocks[i]["w_px"] * blocks[i]["h_px"])
    polys = [block_poly(blocks[i]) for i in order]
    tree = STRtree(polys)
    keep = [True] * len(order)
    for k, p in enumerate(polys):
        if not keep[k]:
            continue
        for j in tree.query(p):
            j = int(j)
            if j > k and keep[j]:
                q = polys[j]
                if q.intersection(p).area > 0.7 * q.area:
                    keep[j] = False
    return [blocks[order[k]] for k in range(len(order)) if keep[k]]


def make_blocks(cells: list[dict]) -> list[dict]:
    n = len(cells)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    G = 120
    grid: dict[tuple[int, int], list[int]] = {}
    for i, c in enumerate(cells):
        grid.setdefault((int(c["cx"]) // G, int(c["cy"]) // G), []).append(i)
    for i, c in enumerate(cells):
        gx, gy = int(c["cx"]) // G, int(c["cy"]) // G
        for ax_ in range(gx - 2, gx + 3):
            for ay_ in range(gy - 2, gy + 3):
                for j in grid.get((ax_, ay_), ()):
                    if j > i and same_hall(c, cells[j]):
                        parent[find(j)] = find(i)
    groups: dict[int, list[int]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    out = []
    for g in sorted(groups.values(), key=lambda g: g[0]):
        cs = [cells[i] for i in g]
        if len(cs) == 1:
            c = cs[0]
            if c["b"] < SINGLE_MIN_SIDE or c["rect"] < SINGLE_MIN_RECT:
                continue
        pts = np.vstack([c["pts"] for c in cs])
        # the direction comes from the bays (their median), which is steadier than the hull of a small group
        rel = np.array([((c["ang"] + 45) % 90) - 45 for c in cs])
        ang = float(np.median(rel))
        t = math.radians(ang)
        ux, uy, vx, vy = math.cos(t), math.sin(t), -math.sin(t), math.cos(t)
        pu, pv = pts[:, 0] * ux + pts[:, 1] * uy, pts[:, 0] * vx + pts[:, 1] * vy
        um, vm = (pu.min() + pu.max()) / 2, (pv.min() + pv.max()) / 2
        cx, cy = um * ux + vm * vx, um * uy + vm * vy
        w, h = pu.max() - pu.min() + 7, pv.max() - pv.min() + 7  # half an ink line on each side, plus the pixel
        if h > w:
            w, h = h, w
            ang = ang + 90
            t = math.radians(ang)
            ux, uy, vx, vy = math.cos(t), math.sin(t), -math.sin(t), math.cos(t)
        ang = (ang + 90) % 180 - 90
        if max(w, h) > BLOCK_MAX_SIDE or min(w, h) < SINGLE_MIN_SIDE:
            continue
        cu = np.array([c["cx"] * ux + c["cy"] * uy for c in cs])
        cv = np.array([c["cx"] * vx + c["cy"] * vy for c in cs])
        cols = count_lines(cu, 9)
        rows = count_lines(cv, 9)
        regular = cols * rows == len(cs)
        fill = sum((c["a"] + 5) * (c["b"] + 5) for c in cs) / max(w * h, 1)  # a bay with its share of the ink
        rect = float(np.mean([c["rect"] for c in cs]))
        score = 0.35 * min(1, fill) + 0.35 * rect + 0.2 * (1 if regular else 0) + 0.1 * min(1, (len(cs) - 1) / 4)
        if len(cs) >= 2 and (score < 0.62 or fill < BLOCK_MIN_FILL):
            continue
        note = "" if regular else "irregular grid"
        if len(cs) == 1:
            note = "single cell"
        out.append({"cx": round(cx, 1), "cy": round(cy, 1), "w_px": round(w, 1), "h_px": round(h, 1), "angle_deg": round(ang, 1), "cells": len(cs),
                    "ncols": cols, "nrows": rows, "score": round(score, 3), "note": note})
    out = drop_nested(out)
    out.sort(key=lambda b: (round(b["cy"] / 100), b["cx"]))
    for i, b in enumerate(out, 1):
        b["block_id"] = f"B{i:04d}"
    return out



# ------------------------------------------------------------------------------ classification
SEAM_C_X = 8660         # scroll c starts here: its wash is green along the shore
WASH_ABC = 1.2          # scrolls a, b: shore tint above the local 30th percentile of nearby regions
WASH_C_GR = -13.0       # scroll c: green along the shore
WASH_C_YB = -1.5        # scroll c: the lake body reads cooler than the land nearby
CLASS_MIN_AREA = 3000   # px2, smaller regions never become water by tint alone


def neighbours(labels: np.ndarray, reg: dict, r: int = 10) -> dict[int, int]:
    """Labels on a ring r px outside the region, with counts (0 = ink or nothing)."""
    x0, y0, x1, y1 = reg["bbox"]
    i = int(reg["region_id"][1:])
    sl = (slice(max(0, y0 - r), y1 + r), slice(max(0, x0 - r), x1 + r))
    crop = labels[sl]
    m = crop == i
    ring = ndi.binary_dilation(m, iterations=r) & ~m
    v, c = np.unique(crop[ring], return_counts=True)
    return {int(a): int(b) for a, b in zip(v, c)}


def classify(regions: list[dict], labels: np.ndarray, blocks: list[dict], walls: list[dict]) -> list[dict]:
    k = len(regions)
    h, w = labels.shape
    # how many hall blocks touch a region: the four points just outside each block
    touch = np.zeros(k + 1, int)
    for b in blocks:
        reach = max(b["w_px"], b["h_px"]) / 2 + 14
        seen = set()
        for px, py in ((b["cx"] - reach, b["cy"]), (b["cx"] + reach, b["cy"]), (b["cx"], b["cy"] - reach), (b["cx"], b["cy"] + reach)):
            if 0 <= px < w and 0 <= py < h:
                seen.add(int(labels[int(py), int(px)]))
        for i in seen - {0}:
            touch[i] += 1
    area = np.array([r["area_px"] for r in regions], float)
    pts = np.array([r["inner_point"] for r in regions], float)
    nan = float("nan")
    yb = np.array([r["tint"]["yb_rim"] if r["tint"]["yb_rim"] is not None else nan for r in regions], float)
    gr = np.array([r["tint"]["gr_rim"] if r["tint"]["gr_rim"] is not None else nan for r in regions], float)
    perim = np.array([np.hypot(*(np.roll(np.array(r["polygon"], float), -1, axis=0) - np.array(r["polygon"], float)).T).sum() for r in regions])
    big = area >= 8000
    rows = []
    rings = {wl["garden"]: Polygon(wl["points"]) for wl in walls if wl["kind"] == "outer_wall"}
    tree_lines = [LineString(wl["points"]) for wl in walls]
    for i, r in enumerate(regions):
        near = np.hypot(*(pts[big] - pts[i]).T) < 900
        vals = yb[big][near]
        vals = vals[np.isfinite(vals)]
        base = np.percentile(vals, 30) if len(vals) > 3 else float(np.nanmedian(yb))
        wash = float(yb[i] - base) if np.isfinite(yb[i]) else 0.0
        x = pts[i][0]
        if x < SEAM_C_X:
            wet = wash > WASH_ABC
        else:
            wet = (np.isfinite(gr[i]) and gr[i] > WASH_C_GR) or wash < WASH_C_YB
        cl, conf, note = "land", "C", "default"
        p = Point(r["inner_point"])
        if not any(rg.contains(p) for rg in rings.values()):
            cl, conf, note = "outside", "C", "inner point outside the wall rings"
        elif wet and touch[i + 1] <= 1 and area[i] >= CLASS_MIN_AREA:
            cl, conf, note = "water", ("B" if abs(wash) > 2.0 or x >= SEAM_C_X else "C"), f"auto: wash {wash:+.1f}, no halls"
        elif touch[i + 1] >= 1 and area[i] < 30000:
            x0, y0, x1, y1 = r["bbox"]
            if r["area_filled_px"] / max((x1 - x0) * (y1 - y0), 1) > 0.72:
                cl, conf, note = "court", "C", "auto: small rectangle beside halls"
        mean_hw = area[i] / max(perim[i], 1)
        if cl != "outside" and mean_hw < 22 and area[i] >= 8000:
            poly = np.array(r["polygon"], float)[:: max(1, len(r["polygon"]) // 20)]
            d = [min(ln.distance(Point(q)) for ln in tree_lines) for q in poly]
            if float(np.median(d)) < 80:
                cl, conf, note = "wall_strip", "C", "auto: narrow strip along a wall"
        rows.append({"region_id": r["region_id"], "class": cl, "name_zh": "", "confidence": conf, "note": note})
    # manual classes, given by a point inside the region, win. They survive a renumbering
    p = OUT / "classes_manual.csv"
    missing = []
    if p.exists():
        with p.open(encoding="utf-8", newline="") as f:
            for m in csv.DictReader(f):
                x, y = int(m["x"]), int(m["y"])
                i = int(labels[y, x])
                if i == 0:
                    missing.append(m)
                    continue
                rows[i - 1].update({"class": m["class"], "name_zh": m["name_zh"], "confidence": m["confidence"], "note": "manual: " + m["note"]})
    if missing:
        log("manual classes on no region:", len(missing), [(m["x"], m["y"]) for m in missing][:10])
    # hills and islands read off the neighbours. Only regions still on the default land
    cls = [row["class"] for row in rows]
    for i, r in enumerate(regions):
        row = rows[i]
        if row["class"] != "land" or row["note"] != "default" or area[i] < 3000:
            continue
        nb = neighbours(labels, r)
        total = sum(c for a, c in nb.items() if a)
        if not total:
            continue
        wet_share = sum(c for a, c in nb.items() if a and cls[a - 1] == "water") / total
        top = max(((c, a) for a, c in nb.items() if a), default=(0, 0))
        if wet_share >= 0.6:
            row.update({"class": "island", "note": f"auto: {wet_share:.0%} of the outline faces water"})
        elif top[0] / total >= 0.8 and cls[top[1] - 1] in ("land", "island") and touch[i + 1] == 0 and area[i] <= 200000 and perim[i] ** 2 / area[i] > 22:
            row.update({"class": "hill", "note": f"auto: closed lobed outline inside {regions[top[1] - 1]['region_id']}, no halls"})
    return rows



# ------------------------------------------------------------------------------- simple outputs
def write_outputs(walls, classes, regions, blocks, counts) -> None:
    (OUT / "walls.json").write_text(
        json.dumps(
            [{"id": w["id"], "kind": w["kind"], "garden": w["garden"], "points": w["points"], "note": w.get("note", ""), "source": "S01"} for w in walls],
            ensure_ascii=False,
            indent=1,
        ),
        "utf-8",
    )
    for name in ("gates", "slips"):
        (OUT / f"{name}.json").write_text(json.dumps(read_json(OUT / f"{name}_manual.json", []), ensure_ascii=False, indent=1), "utf-8")
    area_by: dict[str, int] = {}
    for c, r in zip(classes, regions):
        area_by[c["class"]] = area_by.get(c["class"], 0) + r["area_px"]
    (OUT / "trace_summary.json").write_text(
        json.dumps(
            {
                "source": "S01",
                "regions": len(regions),
                "regions_per_class": dict(sorted(counts.items())),
                "area_px_per_class": dict(sorted(area_by.items())),
                "blocks": len(blocks),
                "blocks_cells": sum(b["cells"] for b in blocks),
                "blocks_single_cell": sum(1 for b in blocks if b["cells"] == 1),
            },
            ensure_ascii=False,
            indent=1,
        ),
        "utf-8",
    )


# ------------------------------------------------------------------------------- review images
TEST_CROPS = {"jiuzhou": (2800, 4400, 1400, 900), "zhengda": (2900, 5200, 1400, 900), "changchun": (9900, 2700, 1200, 1000)}
COLOURS = {"water": (40, 120, 255), "field": (230, 220, 0), "hill": (160, 110, 30), "wall_strip": (255, 0, 255), "outside": (120, 120, 120), "court": (255, 120, 120), "island": (60, 200, 90)}


def review(rgb: np.ndarray, labels: np.ndarray, regions: list[dict], classes: list[dict], blocks: list[dict]) -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    k = len(regions) + 1
    pal = np.zeros((k, 3), np.float32)
    alpha = np.zeros(k, np.float32)
    for i, c in enumerate(classes, 1):
        if c["class"] in COLOURS:
            pal[i] = COLOURS[c["class"]]
            alpha[i] = 0.45
    step = 6
    lab = labels[::step, ::step]
    im = np.asarray(Image.fromarray(rgb).resize((lab.shape[1], lab.shape[0]), Image.BOX)).astype(np.float32)
    mix = im * (1 - alpha[lab][..., None]) + pal[lab] * alpha[lab][..., None]
    img = Image.fromarray(mix.astype(np.uint8))
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=12)
    for r in regions:
        if r["area_px"] >= 60000:
            x, y = r["inner_point"]
            d.text((x / step - 13, y / step - 6), r["region_id"][1:], fill=(255, 255, 0), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
    img.save(SHOTS / "trace_classes.jpg", quality=85)
    for name, (x, y, w_, h_) in TEST_CROPS.items():
        crop = Image.fromarray(rgb[y : y + h_, x : x + w_].copy())
        d = ImageDraw.Draw(crop)
        for b in blocks:
            if x - 50 <= b["cx"] < x + w_ + 50 and y - 50 <= b["cy"] < y + h_ + 50:
                pts = [(px - x, py - y) for px, py in block_poly(b).exterior.coords]
                d.line(pts, fill=(255, 0, 0) if b["cells"] > 1 else (0, 110, 255), width=2)
        crop.save(SHOTS / f"trace_blocks_{name}.jpg", quality=88)


# -------------------------------------------------------------------------------------- main
def read_json(p: Path, default):
    return json.loads(p.read_text("utf-8")) if p.exists() else default


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh", action="store_true", help="ignore the cached ink mask")
    ap.add_argument("--no-review", action="store_true", help="skip the review images")
    args = ap.parse_args()
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    rgb = load_rgb()
    log("mosaic", rgb.shape)

    p_ink, p_mount, p_thin = CACHE / "ink.npy", CACHE / "mount.npy", CACHE / "thin.npy"
    if p_ink.exists() and p_mount.exists() and p_thin.exists() and not args.fresh:
        ink, mount, thin = np.load(p_ink), np.load(p_mount), np.load(p_thin)
    else:
        ink, mount, thin = make_ink(rgb)
        CACHE.mkdir(parents=True, exist_ok=True)
        np.save(p_ink, ink)
        np.save(p_mount, mount)
        np.save(p_thin, thin)
    log("ink share", round(float(ink.mean()), 4), "mount share", round(float(mount.mean()), 4))

    ink = ink.copy()
    seam_lines = []
    for seam in SEAMS:
        lines = stitch_seam(ink, seam)
        seam_lines += lines
        draw_lines(ink, lines)
        log("seam", seam["name"], "lines", len(lines))
    bridges = read_json(OUT / "bridges_manual.json", [])
    draw_lines(ink, [tuple(b["line"]) for b in bridges], width=5)
    log("manual bridges", len(bridges))
    walls_manual = read_json(OUT / "walls_manual.json", [])
    wall_lines = []
    for wl in walls_manual:
        if wl.get("burn"):
            pts = wl["points"]
            wall_lines += [(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]) for i in range(len(pts) - 1)]
    draw_lines(ink, wall_lines, width=3)
    log("wall segments burnt", len(wall_lines))
    free = ~ink & ~mount

    labels, dist = make_regions(free)
    regions, labels = region_table(labels, dist, rgb)
    log("regions", len(regions))

    np.save(CACHE / "labels.npy", labels)
    np.save(CACHE / "ink_final.npy", ink)
    (OUT / "regions.json").write_text(
        json.dumps(
            {
                "source": "S01",
                "coords": "plan pixels on research/raw/plans/princeton_mosaic.jpg, origin top-left, y down",
                "params": {"levels": LEVELS, "min_region_px2": MIN_REGION, "min_hole_px2": MIN_HOLE, "simplify_px": SIMPLIFY},
                "regions": regions,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        "utf-8",
    )

    cells, _ = find_cells(thin, mount)
    del _
    log("cells", len(cells))
    blocks = make_blocks(cells)
    log("blocks", len(blocks), "from cells", sum(b["cells"] for b in blocks))
    with (OUT / "blocks.csv").open("w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f, lineterminator="\n")
        fields = ["block_id", "cx", "cy", "w_px", "h_px", "angle_deg", "cells", "ncols", "nrows", "score", "note"]
        wr.writerow(fields)
        for b in blocks:
            wr.writerow([b[k] for k in fields])

    classes = classify(regions, labels, blocks, walls_manual)
    with (OUT / "regions_classified.csv").open("w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, ["region_id", "class", "name_zh", "confidence", "note"], lineterminator="\n")
        wr.writeheader()
        wr.writerows(classes)
    counts: dict[str, int] = {}
    for c in classes:
        counts[c["class"]] = counts.get(c["class"], 0) + 1
    log("classes", counts)
    np.save(CACHE / "labels.npy", labels)
    write_outputs(walls_manual, classes, regions, blocks, counts)
    if not args.no_review:
        review(rgb, labels, regions, classes, blocks)
    log("done in", round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
