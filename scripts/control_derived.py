"""Round 8 control points derived by script, not read by eye: research/georef/control_shapes.csv.

  uv run python scripts/control_derived.py

Two kinds, both mapped through the previous fit (princeton-1920s.previous.json) only, so the file does not depend on
the fit it feeds (a rerun after the refit writes the same file):
- `ruin`: the Xiyang Lou rows that Round 6 moved onto their ruins (research/evidence/facts.csv, decision correct on
  lat and lon; read on 0.46 m imagery, about ±3-4 m): the row's block on the plan against its ruin. Quality 2.
- `shore`: today's lakes that keep their old outline (OSM natural=water in the park, at least 3000 m²; the traced
  water_1860 near them). The traced shore is laid on today's by a translation (trimmed nearest-point iterations,
  shore points every 4 m); the lake's centre, and for a lake over 4 ha each quarter of its shore, gives a point.
  Only where the shores agree after the shift (median under 6 m and 60% of today's shore within 10 m) and the traced
  water near the lake holds 0.7-1.4 times today's (a lake re-dug wider or narrower fails, though one bank may agree). Shore points
  within 60 m of a check point are left out of the matching, so no check point's own shore feeds the fit. Quality 2.
Rows within 60 m of a check point are written with use=excluded; georef.py drops them too.
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np
import shapely
from scipy.spatial import cKDTree
from shapely.geometry import Polygon, shape

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import georef  # noqa: E402
import shore_check  # noqa: E402

ROOT = georef.ROOT
OUT = ROOT / "research/georef/control_shapes.csv"
FIELDS = ["id", "plan_x", "plan_y", "lat", "lon", "datum", "feature", "kind", "area", "quality", "use", "note"]
QUARTER_AREA = 40000.0
AREA_RATIO = (0.7, 1.4)  # the traced water near a lake against today's lake: a lake re-dug larger or smaller fails
# Lakes a reader saw re-dug, whatever the numbers say (research/georef/readings_r8/notes_*.md).
LAKES_REDUG = {"1352930636": "reader YW: the pond on the plain of 山高水长 has straight modern banks and another width (notes_YW 18:35, 19:01)"}
# Round 6 rows whose position was read on a ruin (research/xiyanglou/boxes.csv basis). The others it moved stay out:
NOT_ON_A_RUIN = {
    "XY02": "plan position with an interpolated offset, no ruin (Q64)",
    "XY03": "the gate of today's rebuilt maze (Q66)",
    "XY04": "today's rebuilt maze; whether it keeps the old line is open (Q66)",
    "XY04-01": "today's rebuilt maze (Q66)",
    "XY04-N01": "today's rebuilt maze (Q66)",
    "XY05": "plan position, err 15 m: pulled down about 1924, no ruin (Q64)",
    "XY08-N01": "placed from the plan beside 海晏堂, not read on a ruin",
    "XY08-N02": "placed from the plan beside 海晏堂, not read on a ruin",
    "XY11": "on OSM's point, err 15 m, under trees (Q71)",
    "XY15-N01": "moved with 方河, not read on a ruin",
    "XY15-N02": "moved with 方河, not read on a ruin",
}
AGREE_MEDIAN_M, AGREE_SHARE = 6.0, 0.6


class Prev:
    """The previous fit, loaded apart from the fit in use."""

    def __init__(self):
        self.model = georef._model_of(georef.PREVIOUS_PATH)
        d = json.loads(georef.PREVIOUS_PATH.read_text(encoding="utf-8"))["transform"]
        self.step = np.array(d["inverse_step"])

    def to_utm(self, x, y):
        return self.model(np.asarray(x, float), np.asarray(y, float))

    def to_plan(self, e, n, iterations=30):
        e, n = np.asarray(e, float), np.asarray(n, float)
        ce, cn = self.model(np.array([6000.0]), np.array([4000.0]))
        xs = 6000 + self.step[0, 0] * (e - ce[0]) + self.step[0, 1] * (n - cn[0])
        ys = 4000 + self.step[1, 0] * (e - ce[0]) + self.step[1, 1] * (n - cn[0])
        for _ in range(iterations):
            pe, pn = self.model(xs, ys)
            xs, ys = xs + self.step[0, 0] * (e - pe) + self.step[0, 1] * (n - pn), ys + self.step[1, 0] * (e - pe) + self.step[1, 1] * (n - pn)
        return xs, ys


def warp_ring(prev, coords):
    c = np.asarray(coords, float)
    e, n = prev.to_utm(c[:, 0], c[:, 1])
    out = np.column_stack([e, n])
    out[-1] = out[0]  # a matrix product may differ in the last bit between a ring's first and last point
    return out


def check_utm():
    pts = georef.read_check()["points"]
    e, n = georef._TO_UTM.transform(np.array([p["lon"] for p in pts]), np.array([p["lat"] for p in pts]))
    return np.c_[e, n]


def near_check(chk, e, n):
    return float(np.hypot(chk[:, 0] - e, chk[:, 1] - n).min())


def ruins(chk):
    corrected = {}
    for r in csv.DictReader(open(ROOT / "research/evidence/facts.csv", encoding="utf-8", newline="")):
        if r["decision"] == "correct" and r["field"] in ("lat", "lon") and r["id"].startswith("XY"):
            corrected.setdefault(r["id"], set()).add(r["field"])
    out = []
    for r in csv.DictReader(open(ROOT / "research/buildings.csv", encoding="utf-8", newline="")):
        if r["id"] in corrected and corrected[r["id"]] == {"lat", "lon"} and r["plan_x"] and r["lat"]:
            e, n = georef._TO_UTM.transform(float(r["lon"]), float(r["lat"]))
            d = near_check(chk, e, n)
            use, note = ("fit", "") if d >= georef.EXCLUDE_M else ("excluded", f"{d:.0f} m from a check point")
            if r["id"] in NOT_ON_A_RUIN:
                use, note = "excluded", NOT_ON_A_RUIN[r["id"]]
            out.append({"id": f"X8-{r['id']}", "plan_x": r["plan_x"], "plan_y": r["plan_y"], "lat": r["lat"], "lon": r["lon"], "datum": "WGS84 via Esri (Round 6 ruin reading)",
                        "feature": f"{r['name_zh'] or r['id']}: the plan's block against the ruin (Round 6)", "kind": "ruin", "area": "XYL", "quality": 2,
                        "use": use, "note": note})
    return out


def shores(chk):
    prev, cur = Prev(), None
    water = json.loads((ROOT / "research/layers/water_1860.geojson").read_text(encoding="utf-8"))
    regs = {r["region_id"]: r for r in json.loads((ROOT / "research/plan/regions.json").read_text(encoding="utf-8"))["regions"]}
    # The traced water in plan pixels, straight from the tracing (research/plan/regions.json, by the layer's region_id), then
    # through the previous fit: nothing here depends on the fit in use, so a rerun after a refit writes the same file.
    polys = []
    for f in water["features"]:
        reg = regs[f["properties"]["region_id"]]
        g = Polygon(reg["polygon"], reg.get("holes") or []).buffer(0)
        for q in [g] if g.geom_type == "Polygon" else list(g.geoms):
            polys.append(Polygon(warp_ring(prev, q.exterior.coords), [warp_ring(prev, h.coords) for h in q.interiors]).buffer(0))
    tree_chk = cKDTree(chk)
    out = []
    for oid, name, g, gu in shore_check.lakes():
        if oid.split("-")[-1] in LAKES_REDUG:
            continue
        near = [w for w in polys if w.distance(gu) < 60]
        if not near:
            continue
        pw = shapely.unary_union(near)
        today = shore_check.shore_points(gu)
        ps = shore_check.shore_points(pw)
        ps = ps[cKDTree(today).query(ps)[0] < 80]
        free = tree_chk.query(today)[0] >= georef.EXCLUDE_M
        if len(ps) < 10 or free.mean() < 0.6:
            continue
        today = today[free]
        t, d0, d1 = shore_check.match(today, ps)
        if np.median(d1) > AGREE_MEDIAN_M or (d1 < 10).mean() < AGREE_SHARE:
            continue
        # The traced water must hold about as much as today's lake: one re-dug wider or narrower fails, though one bank may agree.
        ratio = pw.intersection(gu.buffer(30)).area / gu.area
        if not AREA_RATIO[0] <= ratio <= AREA_RATIO[1]:
            continue
        c = gu.centroid
        sets = [("centre", today, (c.x, c.y))]
        if gu.area > QUARTER_AREA:
            for qn, (sx, sy) in {"NE": (1, 1), "NW": (-1, 1), "SW": (-1, -1), "SE": (1, -1)}.items():
                m = (np.sign(today[:, 0] - c.x) == sx) & (np.sign(today[:, 1] - c.y) == sy)
                if m.sum() >= 30:
                    q = today[m]
                    sets.append((qn, q, tuple(q.mean(axis=0))))
        for label, pts, (pe, pn) in sets:
            tq, _, dq = shore_check.match(pts, ps) if label != "centre" else (t, None, d1)
            if np.median(dq) > AGREE_MEDIAN_M or (dq < 10).mean() < AGREE_SHARE:
                continue
            if label != "centre":
                # A quarter's shore must turn enough to fix both directions, or the shift slides along it.
                v = np.diff(pts, axis=0)
                v = v[np.hypot(v[:, 0], v[:, 1]) < 10]
                if len(v) < 10:
                    continue
                u = v / np.hypot(v[:, 0], v[:, 1])[:, None]
                ev = np.linalg.eigvalsh(u.T @ u / len(u))
                if ev[0] / ev[1] < 0.15:
                    continue
            d = near_check(chk, pe, pn)
            # tq lays today's shore on the plan's: the plan's point for today's (pe, pn) is (pe, pn) - tq, through the previous fit.
            px, py = prev.to_plan(np.array([pe - tq[0]]), np.array([pn - tq[1]]))
            lon, lat = georef._TO_LL.transform(pe, pn)
            out.append({"id": f"S8-{oid.split('-')[-1]}-{label}", "plan_x": round(float(px[0]), 1), "plan_y": round(float(py[0]), 1), "lat": round(float(lat), 7), "lon": round(float(lon), 7),
                        "datum": "WGS84 via OSM (lake outline)", "feature": f"{name or 'lake'} {oid}, {label} of today's shore laid on the traced one",
                        "kind": "shore", "area": str(georef.region_of(px, py)[0]), "quality": 2,
                        "use": "fit" if d >= georef.EXCLUDE_M else "excluded",
                        "note": f"area ratio {ratio:.2f}; shift {np.hypot(*tq):.1f} m, median {np.median(dq):.1f} m after it, {(dq < 10).mean():.0%} of the shore within 10 m" + ("" if d >= georef.EXCLUDE_M else f"; {d:.0f} m from a check point")})
    return out


def main():
    chk = check_utm()
    rows = ruins(chk) + shores(chk)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    from collections import Counter

    print(OUT.relative_to(ROOT), len(rows), Counter((r["kind"], r["use"]) for r in rows))


if __name__ == "__main__":
    main()
