"""Today's lakes against the traced water of 1860: where the shores still agree, and what offset is left.

  uv run python tools/shore_check.py [--rev REV] [--write]

For each lake of today's park in OSM (natural=water inside the park, at least 3000 m²; research/layers/osm_today.geojson),
the traced water of water_1860 within 60 m of it: the share of today's shore with a traced shore within 10 m, the median
distance between the shores, and the offset left: traced minus today, as for the check set, by the translation that
best lays the traced shore on today's (trimmed nearest-point iterations, shore points every 4 m). A lake re-dug to another outline shows as a poor match whatever the fit; one that
keeps its old outline shows the fit's local error as the offset. With --rev, the same for the layer at that git revision,
so a refit can be compared. --write stores research/georef/shores_r8.json.
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from pyproj import Transformer
from scipy.spatial import cKDTree
from shapely.geometry import shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research/georef/shores_r8.json"
TO_UTM = Transformer.from_crs(4326, 32650, always_xy=True)
MIN_AREA = 3000.0
STEP = 4.0


def utm(g):
    import shapely

    return shapely.transform(g, lambda c: np.column_stack(TO_UTM.transform(c[:, 0], c[:, 1])))


def shore_points(g):
    pts = []
    for poly in getattr(g, "geoms", [g]):
        for ring in [poly.exterior, *poly.interiors]:
            n = max(4, int(ring.length / STEP))
            pts += [ring.interpolate(t, normalized=True).coords[0] for t in np.linspace(0, 1, n, endpoint=False)]
    return np.asarray(pts)


def match(today, plan_shore):
    """Translation laying the plan's shore on today's, and the distances before and after."""
    tree = cKDTree(plan_shore)
    d0, _ = tree.query(today)
    t = np.zeros(2)
    for _ in range(15):
        d, i = tree.query(today - t)
        keep = d < max(15.0, np.percentile(d, 70))
        step = np.median(plan_shore[i[keep]] - (today[keep] - t), axis=0)
        t = t - step
        if np.hypot(*step) < 0.05:
            break
    d1, _ = tree.query(today - t)
    return t, d0, d1


def lakes():
    feats = json.loads((ROOT / "research/layers/osm_today.geojson").read_text(encoding="utf-8"))["features"]
    park = next(shape(f["geometry"]) for f in feats if f["properties"].get("name") == "圆明园遗址公园")
    out = []
    for f in feats:
        p = f["properties"]
        if p.get("natural") != "water" or f["geometry"]["type"] not in ("Polygon", "MultiPolygon", "MultiLineString"):
            continue
        g = shape(f["geometry"])
        if g.geom_type == "MultiLineString":  # a lake whose outline OSM keeps as a relation of ways: close it
            import shapely

            g = shapely.unary_union(list(shapely.polygonize(list(g.geoms)).geoms))
            if g.is_empty:
                continue
        if not g.intersects(park) or g.intersection(park).area < 0.5 * g.area:
            continue
        gu = utm(g)
        if gu.area >= MIN_AREA:
            out.append((p["id"], p.get("name", ""), g, gu))
    return out


def run(water_fc):
    plan = [utm(shape(f["geometry"])).buffer(0) for f in water_fc["features"]]
    res = []
    for oid, name, g, gu in lakes():
        near = [w for w in plan if w.distance(gu) < 60]
        if not near:
            res.append({"osm": oid, "name": name, "area_m2": round(gu.area), "matched": False})
            continue
        pw = unary_union(near)
        today = shore_points(gu)
        ps = shore_points(pw)
        ps = ps[cKDTree(today).query(ps)[0] < 80]  # only the traced shore near this lake
        if len(ps) < 10:
            res.append({"osm": oid, "name": name, "area_m2": round(gu.area), "matched": False})
            continue
        t, d0, d1 = match(today, ps)
        inter = gu.intersection(pw.buffer(0)).area
        res.append({
            "osm": oid, "name": name, "lon": round(g.centroid.x, 5), "lat": round(g.centroid.y, 5), "area_m2": round(gu.area), "matched": True,
            "share_within_10m": round(float((d0 < 10).mean()), 2), "median_m": round(float(np.median(d0)), 1),
            "offset_e_m": round(float(-t[0]), 1), "offset_n_m": round(float(-t[1]), 1), "offset_m": round(float(np.hypot(*t)), 1),
            "median_after_offset_m": round(float(np.median(d1)), 1), "share_within_10m_after_offset": round(float((d1 < 10).mean()), 2),
            "overlap_of_today": round(inter / gu.area, 2),
        })
    return res


def main():
    cur = json.loads((ROOT / "research/layers/water_1860.geojson").read_text(encoding="utf-8"))
    out = {"note": __doc__.split("\n\n")[1], "now": run(cur)}
    if "--rev" in sys.argv:
        rev = sys.argv[sys.argv.index("--rev") + 1]
        old = json.loads(subprocess.run(["git", "-C", str(ROOT), "show", f"{rev}:research/layers/water_1860.geojson"], capture_output=True, check=True).stdout)
        out["rev"] = rev
        out["before"] = run(old)
    print(f"{'osm':18s} {'area':>7s} {'within10':>8s} {'median':>6s} {'offset':>6s} {'E':>6s} {'N':>6s} {'after':>6s}" + ("   before: within10 median offset" if "before" in out else ""))
    before = {r["osm"]: r for r in out.get("before", [])}
    for r in out["now"]:
        if not r["matched"]:
            print(f"{r['osm']:18s} {r['area_m2']:7d}  no traced water near it")
            continue
        b = before.get(r["osm"])
        tail = f"   {b['share_within_10m']:>8} {b['median_m']:>6} {b['offset_m']:>6}" if b and b.get("matched") else ""
        print(f"{r['osm']:18s} {r['area_m2']:7d} {r['share_within_10m']:8.2f} {r['median_m']:6.1f} {r['offset_m']:6.1f} {r['offset_e_m']:6.1f} {r['offset_n_m']:6.1f} {r['median_after_offset_m']:6.1f}{tail}  {r['name']}")
    if "--write" in sys.argv:
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
