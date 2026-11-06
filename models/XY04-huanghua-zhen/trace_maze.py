#!/usr/bin/env python3
"""黄花阵 Huanghua Zhen (XY04), Round 26: the maze's walls read off the plan S01, in plan pixels, into plan_readings.csv beside this file.

  uv run python models/XY04-huanghua-zhen/trace_maze.py [--png <scratch png>]

S01 draws every maze wall as one ink line (a closed outline where a wall rings a bed or a tree circle), the paths as dotted lines, the central ring and octagon, the stair
south of it and the north hall XY04-N01. This script thins the ink inside the maze's outer wall to one-pixel centrelines (Zhang-Suen), traces them into polylines, drops the dots
(short pieces) and the parts drawn by other rules (the ring, the stair, the hall, the basin's wave marks), and writes each line as a row: `W###` (a wall, its points `x y;x y` in
plan pixels of the mosaic). The outer wall is the rectangle the generator draws from the block (S310), so it is masked here. Needs research/raw/plans/princeton_mosaic.jpg
(local only); the CSV is what the generator reads, committed. Deterministic: no random numbers.
"""

import argparse
import csv
import math
from pathlib import Path

import numpy as np
from PIL import Image
from shapely.geometry import LineString

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
X0, Y0, X1, Y1 = 8680, 390, 9090, 915  # the crop of the mosaic
RECT = (8706.0, 415.0, 9056.0, 888.0)  # the maze's outer wall on S01 (W, N, E, S), plan px: the middle of the double line S01 draws for it (W 8700/8712, E 9049/9062, N 411/419, S 882/893: the ink's profiles and zooms, Round 26)
T_INK = 110  # darker than this is ink (the mosaic's paper is about 195)
MIN_LEN = 9.0  # px; a dotted path's dots and the thinning's spurs are shorter
MASKS = [  # (kind, x0, y0, x1, y1) in plan px, or ('circle', cx, cy, r): drawn by the generator from their own readings, not as maze walls
    ("circle", 8878.0, 686.0, 54.0),  # the ring of steps and the octagon
    ("rect", 8862, 715, 8895, 772),  # the stair south of the ring
    ("rect", 8836, 430, 8926, 512),  # the north hall XY04-N01 with its flights
    ("rect", 8862, 539, 8902, 565),  # the wave marks of the small basin below the north wall's bow
]
BAND = 7.5  # px either side of the outer rectangle masked (the outer wall)


def zhang_suen(img):
    """One-pixel skeleton of a boolean image (Zhang & Suen 1984), vectorised."""
    im = np.pad(img.astype(np.uint8), 1)
    changed = True
    while changed:
        changed = False
        for step in (0, 1):
            P = im
            p2, p3, p4, p5 = P[:-2, 1:-1], P[:-2, 2:], P[1:-1, 2:], P[2:, 2:]
            p6, p7, p8, p9 = P[2:, 1:-1], P[2:, :-2], P[1:-1, :-2], P[:-2, :-2]
            c = P[1:-1, 1:-1]
            nb = [p2, p3, p4, p5, p6, p7, p8, p9]
            B = sum(n.astype(int) for n in nb)
            A = sum(((nb[i] == 0) & (nb[(i + 1) % 8] == 1)).astype(int) for i in range(8))
            if step == 0:
                m = (c == 1) & (B >= 2) & (B <= 6) & (A == 1) & (p2 * p4 * p6 == 0) & (p4 * p6 * p8 == 0)
            else:
                m = (c == 1) & (B >= 2) & (B <= 6) & (A == 1) & (p2 * p4 * p8 == 0) & (p2 * p6 * p8 == 0)
            if m.any():
                im[1:-1, 1:-1][m] = 0
                changed = True
    return im[1:-1, 1:-1].astype(bool)


NB = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def trace(sk):
    """Polylines (lists of (row, col)) of a skeleton: chains between end points and junctions, and closed loops."""
    H, W = sk.shape
    pts = set(zip(*np.nonzero(sk)))

    def nbrs(p):
        return [(p[0] + a, p[1] + b) for a, b in NB if (p[0] + a, p[1] + b) in pts]

    deg = {p: len(nbrs(p)) for p in pts}
    nodes = {p for p, d in deg.items() if d != 2}
    seen_edges = set()
    out = []
    for n in sorted(nodes):
        for q in nbrs(n):
            if (n, q) in seen_edges:
                continue
            chain = [n, q]
            seen_edges.add((n, q))
            seen_edges.add((q, n))
            prev, cur = n, q
            while cur not in nodes:
                nx = [r for r in nbrs(cur) if r != prev and (cur, r) not in seen_edges]
                if not nx:
                    break
                r = nx[0]
                seen_edges.add((cur, r))
                seen_edges.add((r, cur))
                chain.append(r)
                prev, cur = cur, r
            out.append(chain)
    used = {p for ch in out for p in ch}
    rest = sorted(pts - used)
    while rest:  # closed loops with no node
        s = rest[0]
        chain = [s]
        prev, cur = None, s
        while True:
            nx = [r for r in nbrs(cur) if r != prev and r not in chain[1:]]
            if not nx or (nx[0] == s and len(chain) > 2):
                break
            prev, cur = cur, nx[0]
            if cur == s:
                break
            chain.append(cur)
        chain.append(s)
        out.append(chain)
        rest = sorted(set(rest) - set(chain))
    return out


def masked(x, y):
    W_, N_, E_, S_ = RECT
    if not (W_ + BAND < x < E_ - BAND and N_ + BAND < y < S_ - BAND):
        return True
    for m in MASKS:
        if m[0] == "circle" and math.hypot(x - m[1], y - m[2]) < m[3]:
            return True
        if m[0] == "rect" and m[1] <= x <= m[3] and m[2] <= y <= m[4]:
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", default="")
    a = ap.parse_args()
    Image.MAX_IMAGE_PIXELS = None
    im = np.asarray(Image.open(ROOT / "research/raw/plans/princeton_mosaic.jpg").convert("L").crop((X0, Y0, X1, Y1)), float)
    ink = im < T_INK
    for r in range(ink.shape[0]):
        for c in range(ink.shape[1]):
            if ink[r, c] and masked(c + X0, r + Y0):
                ink[r, c] = False
    sk = zhang_suen(ink)
    rows = []
    for ch in trace(sk):
        xy = [(c + X0 + 0.5, r + Y0 + 0.5) for r, c in ch]
        if len(xy) < 2:
            continue
        L = LineString(xy)
        if L.length < MIN_LEN:
            continue
        s = L.simplify(0.9)
        rows.append([(round(x, 1), round(y, 1)) for x, y in s.coords])
    # an end within 6 px of the outer rectangle is taken onto it (the band masked above cut it short)
    W_, N_, E_, S_ = RECT
    for line in rows:
        for k in (0, -1):
            x, y = line[k]
            d = {"W": x - W_, "E": E_ - x, "N": y - N_, "S": S_ - y}
            side, dist = min(d.items(), key=lambda t: t[1])
            if dist < BAND + 6:
                line[k] = (W_ if side == "W" else E_ if side == "E" else x, N_ if side == "N" else S_ if side == "S" else y)
    # the joins the thinning makes into the masked band (a short piece reaching the outer wall's double line) and the bits of the north wall's hatched inner line are not walls
    def near_rect(p, d):
        return min(abs(p[0] - W_), abs(E_ - p[0]), abs(p[1] - N_), abs(S_ - p[1])) <= d
    rows = [l for l in rows if not all(near_rect(p, BAND + 3) for p in l) and not (LineString(l).length < 20 and (near_rect(l[0], 0.01) or near_rect(l[-1], 0.01)))]
    rows.sort(key=lambda l: (min(p[1] for p in l), min(p[0] for p in l)))
    out = HERE / "plan_readings.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "kind", "points_px", "note"])
        w.writerow(["RECT", "outer_wall", f"{W_} {N_};{E_} {N_};{E_} {S_};{W_} {S_}", "the maze's outer wall on S01, the middle of its double line (W 8700/8712, E 9049/9062, N 411/419, S 882/893 by the ink's profiles); the generator maps it onto the block of S310"])
        w.writerow(["RING", "ring", "8878.0 686.0", "the ring of steps round the drum: centre, by eye on the ink (S01 draws an outer circle of 100 px with radial ticks, an inner circle, and the octagon)"])
        w.writerow(["STAIR", "stair", "8865 717;8892 717;8892 760;8865 760", "the straight flight south of the ring: three rungs drawn (S01)"])
        w.writerow(["HALL", "hall", "8837 432;8926 432;8926 486;8837 486", "the north hall XY04-N01 as S01 draws its grid (Round 6: 18.74 x 11.42 m)"])
        w.writerow(["BASIN", "basin", "8862 539;8902 539;8902 565;8862 565", "wave marks in a half-round below the north wall's bow: a small basin (C)"])
        w.writerow(["GATE_S", "gate", "8879 888", "the south gate's opening on the axis (dotted path through the outer wall; 花园门 XY03 stands there)"])
        w.writerow(["GATE_W", "gate", "8706 682", "the west side opening: the dotted path through the outer wall, ink gap y 672-692"])
        w.writerow(["GATE_E", "gate", "9056 682", "the east side opening, mirrored from the west (S01's dots on the east side run 9015-9040; plate 5 draws a gate there with finial piers)"])
        w.writerow(["GATE_N", "gate", "8883 415", "the north opening behind the hall (Round 9: 8877-8890 x 405-415)"])
        for i, l in enumerate(rows, 1):
            w.writerow([f"W{i:03d}", "wall", ";".join(f"{x} {y}" for x, y in l), "traced by trace_maze.py"])
    print(f"{len(rows)} wall lines, {sum(LineString(l).length for l in rows):.0f} px of wall")
    if a.png:
        from PIL import ImageDraw
        sc = 3
        bg = Image.fromarray(im.astype(np.uint8)).convert("RGB").resize((im.shape[1] * sc, im.shape[0] * sc))
        d = ImageDraw.Draw(bg)
        for i, l in enumerate(rows):
            col = [(230, 30, 30), (30, 120, 230), (20, 160, 60), (200, 120, 0)][i % 4]
            d.line([((x - X0) * sc, (y - Y0) * sc) for x, y in l], fill=col, width=2)
        bg.save(a.png)


if __name__ == "__main__":
    main()
