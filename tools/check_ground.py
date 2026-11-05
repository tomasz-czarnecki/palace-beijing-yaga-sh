"""The ground check (Round 10): hills, water levels, and how every object meets the ground.

  uv run python tools/check_ground.py                     the repo as it is; exits non-zero on a failure
  uv run python tools/check_ground.py --before <dir>      the same measures on an older export of the repo (site/reconstruction and research/layers), for the record; never fails

Measured against the surface the view draws and walks: site/reconstruction/generated/ground_grid.i16, the land mesh rasterised on a 2.5 m lattice (bilinear, land
cells only; under water the bed). Before Round 10 the raster was 5 m, flat land and one water level, with no bed.
  boxes      foot above the lowest ground under the box (floats), ground above the platform's top (buried more than its platform); 9 points a box
  ways       strips as paths3d.js lays them (every 4 m, 0.07 m above the ground); points with no land under them; ends against a bridge's deck, or a box between its foot and its platform's top
  bridges    each deck end against the ground at that end; ends over water
  walls      each course's foot against the lowest ground under it, its top against the highest land plus the wall's height
  landings   their top against the bank at their point
Fails: a hill with no height; a water body with more than one level; an A or B box, way or wall with a gap over GAP_AB_M; a bridge joint or an A or B way end over JOINT_M;
a box over water that is not flagged over_water.
"""

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import shape

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from scene1860 import DATUM_M, GROUND_M, to_xz  # noqa: E402

GAP_AB_M = 0.3
JOINT_M = 0.5
LIFT, STEP_M = 0.07, 4.0  # paths3d.js


class NewGround:
    def __init__(self, base):
        meta = json.load(open(base / "site/reconstruction/generated/ground.json", encoding="utf-8"))
        g = meta["grid"]
        self.meta, self.x0, self.z0, self.step, self.w, self.h = meta, g["x0"], g["z0"], g["step_m"], g["width"], g["height"]
        raw = np.fromfile(base / "site/reconstruction/generated/ground_grid.i16", dtype="<i2").reshape(self.h, self.w).astype(float)
        self.wet = raw < g["water_below"]
        self.y = np.where(self.wet, raw - g["water_base"], raw) / 100
        lv = meta["levels"]
        self.lv = lv
        self.cells = np.fromfile(base / "site/reconstruction/generated/ground_level.u8", dtype="u1").reshape(lv["height"], lv["width"])
        self.levels = {b["i"]: b["level"] for b in meta["bodies"]}
        p = meta["plain"]
        self.plain = lambda x, z: p["a"] + p["bx"] * x / 1000 + p["bz"] * z / 1000 - DATUM_M

    def _q(self, x, z):
        u, v = (x - self.x0) / self.step, (z - self.z0) / self.step
        if u < 0 or v < 0 or u > self.w - 1 or v > self.h - 1:
            return None
        i, j = min(int(u), self.w - 2), min(int(v), self.h - 2)
        return i, j, u - i, v - j

    def at(self, x, z):
        """Land or bed."""
        q = self._q(x, z)
        if q is None:
            return self.plain(x, z)
        i, j, a, b = q
        v = self.y[j:j + 2, i:i + 2]
        return float((v[0, 0] * (1 - a) + v[0, 1] * a) * (1 - b) + (v[1, 0] * (1 - a) + v[1, 1] * a) * b)

    def land(self, x, z):
        """As ground3d.js groundAt: land cells only, None over water."""
        q = self._q(x, z)
        if q is None:
            return self.plain(x, z)
        i, j, a, b = q
        wt = np.array([[(1 - a) * (1 - b), a * (1 - b)], [(1 - a) * b, a * b]]) * ~self.wet[j:j + 2, i:i + 2]
        s = wt.sum()
        return float((self.y[j:j + 2, i:i + 2] * wt).sum() / s) if s > 1e-9 else None

    def level(self, x, z):
        i = int(np.clip((x - self.lv["x0"]) // self.lv["cell_m"], 0, self.lv["width"] - 1))
        j = int(np.clip((z - self.lv["z0"]) // self.lv["cell_m"], 0, self.lv["height"] - 1))
        c = int(self.cells[j, i])
        return self.levels.get(c - 1) if c else None


class OldGround:
    """Before Round 10: a 5 m raster of flat land and hill mounds, -32768 on water; one water level at y = 0, no bed. paths3d.js took the nearest cell."""

    def __init__(self, base):
        meta = json.load(open(base / "site/reconstruction/generated/ground.json", encoding="utf-8"))
        g = meta["grid"]
        self.x0, self.z0, self.step, self.w, self.h = g["x0"], g["z0"], g["step_m"], g["width"], g["height"]
        raw = np.fromfile(base / "site/reconstruction/generated/ground_grid.i16", dtype="<i2").reshape(self.h, self.w)
        self.wet = raw == -32768
        self.y = np.where(self.wet, 0, raw) / 100
        self.base = GROUND_M - DATUM_M

    def at(self, x, z):
        i = int(np.clip(round((x - self.x0) / self.step), 0, self.w - 1))
        j = int(np.clip(round((z - self.z0) / self.step), 0, self.h - 1))
        return 0.0 if self.wet[j, i] else float(self.y[j, i])

    def land(self, x, z):
        i = int(np.clip(round((x - self.x0) / self.step), 0, self.w - 1))
        j = int(np.clip(round((z - self.z0) / self.step), 0, self.h - 1))
        return None if self.wet[j, i] else float(self.y[j, i])

    def level(self, x, z):
        return 0.0


def xz(geom):
    return shapely.transform(shape(geom), lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1])))


def stats(v):
    v = np.asarray([x for x in v if x is not None], float)
    if not len(v):
        return "n 0"
    return f"n {len(v)}, median {np.median(v):.2f}, p90 {np.percentile(v, 90):.2f}, max {v.max():.2f} m"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", type=Path)
    a = ap.parse_args()
    base = a.before or ROOT
    G = OldGround(base) if a.before else NewGround(base)
    data = base / "site/reconstruction/data"
    fails = []
    out = {"state": "before" if a.before else "now"}

    # Hills.
    hills = json.load(open(base / "research/layers/hills_1860.geojson", encoding="utf-8"))["features"]
    meth = Counter((f["properties"].get("height_method") or "none").split(":")[0].split(" ")[0] for f in hills)
    conf = Counter(f["properties"].get("confidence") for f in hills)
    basis = Counter(f["properties"].get("basis", "plan") for f in hills)
    no_h = [f["properties"]["id"] for f in hills if not isinstance(f["properties"].get("height_est_m"), (int, float))]
    area = sum(f["properties"].get("area_m2", 0) for f in hills)
    print(f"hills {len(hills)} ({dict(basis)}), {area / 1e4:.1f} ha; by method {dict(meth)}; by confidence {dict(conf)}; with no height {len(no_h)}")
    out["hills"] = {"n": len(hills), "area_ha": round(area / 1e4, 1), "method": dict(meth), "confidence": dict(conf), "basis": dict(basis), "no_height": len(no_h)}
    if no_h:
        fails.append(f"{len(no_h)} hills with no height, e.g. {no_h[:5]}")

    # Water: one level per body.
    if not a.before:
        meta = G.meta
        buf = (base / "site/reconstruction/generated/ground.bin").read_bytes()
        x0, z0 = meta["domain"][:2]
        bad, n = 0, 0
        for c in meta["parts"]["water"]:
            q = np.frombuffer(buf, "<i2", c["verts"] * 3, c["pos"]).reshape(-1, 3).astype(float)
            idx = np.frombuffer(buf, "<u2", c["indices"], c["idx"]).reshape(-1, 3)
            cen = q[idx].mean(axis=1)
            for (px, py, pz), tri in zip(cen, idx):
                ys = q[tri, 1] / 100
                n += 1
                if ys.max() - ys.min() > 0.011:
                    bad += 1
        print(f"water: {len(meta['bodies'])} bodies, levels {min(b['level'] for b in meta['bodies']) + DATUM_M:.2f}-{max(b['level'] for b in meta['bodies']) + DATUM_M:.2f} m; water triangles spanning two levels {bad} of {n}")
        out["water"] = {"bodies": len(meta["bodies"]), "tris_two_levels": bad}
        if bad > 0.002 * n:
            fails.append(f"{bad} water triangles span two levels")
    else:
        print("water: one level for all water (y = 0, 43.5 m)")
        out["water"] = {"bodies": 1}

    # Boxes.
    halls = json.load(open(data / "halls_1860.geojson", encoding="utf-8"))["features"]
    rows = []
    water_flag_missing = []
    for f in halls:
        p = f["properties"]
        ring = xz(f["geometry"])
        c = list(ring.exterior.coords)[:4]
        pts = c + [((u[0] + v[0]) / 2, (u[1] + v[1]) / 2) for u, v in zip(c, c[1:] + c[:1])] + [(ring.centroid.x, ring.centroid.y)]
        g_all = [G.at(x, z) for x, z in pts]
        g_land = [G.land(x, z) for x, z in pts]
        g_land = [v for v in g_land if v is not None]
        ground = p["ground_m"] - DATUM_M
        foot = ground if p.get("stand") else p["foot_m"] - DATUM_M
        shape_ = p.get("shape")
        top = ground + (p.get("stand") or 0) + (p["eave_m"] if shape_ in ("terrace", "wall", "pool", "basin", "court") else p["platform_m"])
        floats = foot - min(g_all)
        buried = (max(g_land) - top) if g_land and shape_ != "court" else 0.0
        rows.append((p["id"], p["confidence"], max(floats, 0), max(buried, 0), p.get("over_water", False)))
        wet_share = sum(1 for x, z in pts if G.land(x, z) is None) / len(pts)
        if wet_share > 0.5 and not p.get("over_water") and shape_ not in ("pool", "basin"):
            water_flag_missing.append(p["id"])
    fl = [r[2] for r in rows]
    bu = [r[3] for r in rows]
    gap = [max(r[2], r[3]) for r in rows]
    ab_bad = [(r[0], round(max(r[2], r[3]), 2)) for r in rows if r[1] in ("A", "B") and max(r[2], r[3]) > GAP_AB_M]
    print(f"boxes {len(rows)}: floating {sum(v > 0.01 for v in fl)} ({stats([v for v in fl if v > 0.01])}); buried past the platform {sum(v > 0.01 for v in bu)} ({stats([v for v in bu if v > 0.01])}); "
          f"gap over {GAP_AB_M} m: {sum(v > GAP_AB_M for v in gap)}, of them A or B {len(ab_bad)}; over water and not flagged: {len(water_flag_missing)}")
    out["boxes"] = {"n": len(rows), "floating": sum(v > 0.01 for v in fl), "float_max_m": round(max(fl), 2), "buried": sum(v > 0.01 for v in bu), "buried_max_m": round(max(bu), 2),
                    "gap_over_0.3": sum(v > GAP_AB_M for v in gap), "gap_over_0.3_AB": len(ab_bad), "in_water_unflagged": len(water_flag_missing)}
    if not a.before:
        if ab_bad:
            fails.append(f"{len(ab_bad)} A or B boxes off the ground by more than {GAP_AB_M} m, e.g. {sorted(ab_bad, key=lambda r: -r[1])[:5]}")
        if water_flag_missing:
            fails.append(f"{len(water_flag_missing)} boxes stand in water unflagged: {water_flag_missing[:5]}")

    # Bridges.
    st = json.load(open(base / "site/reconstruction/generated/structures.json", encoding="utf-8"))
    joints, over_water = [], []
    deck_end = {}
    for b in st["bridges"]:
        for side, pt in (("1", b["pts"][0]), ("2", b["pts"][-1])):
            x, y, z = pt
            deck_end[(b["id"], side)] = (x, y, z)
            g = G.land(x, z)
            if g is None:
                over_water.append(f"{b['id']}:{side}")
                lev = G.level(x, z)
                joints.append(abs(y - (lev if lev is not None else 0.0)))
            else:
                joints.append(abs(y - g))
    print(f"bridges {len(st['bridges'])}: deck end against the ground {stats(joints)}; over {JOINT_M} m: {sum(j > JOINT_M for j in joints)}; ends over water {len(over_water)} {over_water[:8]}")
    out["bridges"] = {"n": len(st["bridges"]), "joint_max_m": round(max(joints), 2), "joint_over_0.5": sum(j > JOINT_M for j in joints), "ends_over_water": len(over_water)}
    if not a.before and sum(j > JOINT_M for j in joints):
        fails.append(f"{sum(j > JOINT_M for j in joints)} bridge ends off the ground by more than {JOINT_M} m")

    # Ways.
    paths = json.load(open(data / "paths_1860.geojson", encoding="utf-8"))["features"]
    # A way meets a box anywhere from the box's foot to its platform's top: the steps stand there.
    box_ground = {f["properties"]["id"]: (f["properties"]["foot_m"] - DATUM_M, f["properties"]["ground_m"] - DATUM_M + f["properties"]["platform_m"]) for f in halls}
    no_land, n_pts, end_gaps, end_gaps_ab = 0, 0, [], []
    base_y = GROUND_M - DATUM_M

    def y_at(x, z):
        g = G.land(x, z)
        return (g if g is not None else base_y) + LIFT, g is None

    for f in paths:
        p = f["properties"]
        if p["kind"] == "boat_route":
            continue
        line = xz(f["geometry"])
        cs = list(line.coords)
        for (ax, az), (bx, bz) in zip(cs, cs[1:]):
            L = math.hypot(bx - ax, bz - az)
            k = max(1, math.ceil(L / STEP_M))
            for t in range(k):
                _, wet = y_at(ax + (bx - ax) * t / k, az + (bz - az) * t / k)
                n_pts += 1
                no_land += wet
        for at, (x, z) in ((p.get("from_at") or "", cs[0]), (p.get("to_at") or "", cs[-1])):
            y, _ = y_at(x, z)
            ref = at.split(":")[0]
            if ref.startswith("BR"):
                ends = [deck_end.get((ref, "1")), deck_end.get((ref, "2"))]
                ends = [e for e in ends if e]
                if not ends:
                    continue
                e = min(ends, key=lambda e: math.hypot(e[0] - x, e[2] - z))
                d = abs(y - LIFT - e[1])
            elif ref in box_ground:
                lo, hi = box_ground[ref]
                d = max(lo - (y - LIFT), (y - LIFT) - hi, 0.0)
            else:
                continue
            end_gaps.append(d)
            if p["confidence"] in ("A", "B"):
                end_gaps_ab.append((p["id"], round(d, 2)))
    bad_ends = [e for e in end_gaps_ab if e[1] > JOINT_M]
    print(f"ways: strip points with no land under them {no_land} of {n_pts}; ends at a bridge or a box: {stats(end_gaps)}, over {JOINT_M} m {sum(d > JOINT_M for d in end_gaps)} (A or B {len(bad_ends)})")
    out["ways"] = {"points": n_pts, "no_land": no_land, "ends": len(end_gaps), "end_max_m": round(max(end_gaps), 2) if end_gaps else 0, "ends_over_0.5": sum(d > JOINT_M for d in end_gaps), "ends_over_0.5_AB": len(bad_ends)}
    if not a.before and bad_ends:
        fails.append(f"{len(bad_ends)} A or B way ends off a bridge deck or a box's ground by more than {JOINT_M} m, e.g. {sorted(bad_ends, key=lambda e: -e[1])[:5]}")

    # Walls.
    hang, short = [], []
    H = st["wall"]["height_m"]
    for ax, az, bx, bz, y0, y1 in st["wall"]["segments"]:
        L = math.hypot(bx - ax, bz - az)
        k = max(2, int(L / 1.25) + 1)
        ys = [G.at(ax + (bx - ax) * t / (k - 1), az + (bz - az) * t / (k - 1)) for t in range(k)]
        ls = [G.land(ax + (bx - ax) * t / (k - 1), az + (bz - az) * t / (k - 1)) for t in range(k)]
        ls = [v for v in ls if v is not None]
        hang.append(max(y0 - min(ys), 0))
        if ls:
            short.append(max(max(ls) + H - y1, 0))
    print(f"walls {len(st['wall']['segments'])} courses: foot above the ground {sum(v > 0.01 for v in hang)} ({stats([v for v in hang if v > 0.01])}); top under the land's height + {H} m: {sum(v > 0.01 for v in short)} ({stats([v for v in short if v > 0.01])})")
    out["walls"] = {"courses": len(hang), "hanging": sum(v > 0.01 for v in hang), "hang_max_m": round(max(hang), 2), "low": sum(v > 0.01 for v in short), "low_max_m": round(max(short) if short else 0, 2)}
    if not a.before and sum(v > GAP_AB_M for v in hang):
        fails.append(f"{sum(v > GAP_AB_M for v in hang)} wall courses hang more than {GAP_AB_M} m")

    # Landings.
    lands = json.load(open(data / "landings_1860.geojson", encoding="utf-8"))["features"]
    steps = []
    for f in lands:
        p = f["properties"]
        if p.get("facing_deg") is None:
            continue
        x, z = to_xz(*f["geometry"]["coordinates"])
        g = G.land(x, z)
        lev = G.level(x, z)
        top = max((g if g is not None else base_y) + 0.05, (lev + 0.4) if (lev is not None and not a.before) else -1e9)
        steps.append(abs(top - (g if g is not None else base_y)))
    print(f"landings {len(steps)}: top against the bank {stats(steps)}")
    out["landings"] = {"n": len(steps), "step_max_m": round(max(steps), 2) if steps else 0, "over_0.5": sum(s > JOINT_M for s in steps)}

    if not a.before:
        (ROOT / "research/terrain/ground_check.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    if fails and not a.before:
        print("FAIL:\n  " + "\n  ".join(fails))
        sys.exit(1)
    print("ok" if not a.before else "(before: measured, not judged)")


if __name__ == "__main__":
    main()
