"""The garden walls of 1860 against today's park boundary.

  uv run python tools/wall_check.py [--rev REV]

The park's wall was rebuilt from 1984 to 2006 on the old line (E2126, S116: a later source, B), and OSM's outline of
圆明园遗址公园 follows it. For each wall of research/layers/walls_1860.geojson, points every 10 m: the distance to that
outline, as a whole and run by run between the plan's vertices. With --rev, the same for the layer at a git revision.
Separating walls lie inside the park and have no outline to meet.
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import shapely
from pyproj import Transformer
from shapely.geometry import LineString, shape

ROOT = Path(__file__).resolve().parent.parent
TO_UTM = Transformer.from_crs(4326, 32650, always_xy=True)


def utm(g):
    return shapely.transform(g, lambda c: np.column_stack(TO_UTM.transform(c[:, 0], c[:, 1])))


def boundary():
    feats = json.loads((ROOT / "research/layers/osm_today.geojson").read_text(encoding="utf-8"))["features"]
    park = next(shape(f["geometry"]) for f in feats if f["properties"].get("name") == "圆明园遗址公园")
    return utm(park).exterior


def report(fc, edge):
    out = {}
    for f in fc["features"]:
        p = f["properties"]
        if f["geometry"]["type"] != "LineString" or p["kind"] != "outer_wall":
            continue
        line = utm(shape(f["geometry"]))
        n = max(2, int(line.length / 10))
        d = np.array([edge.distance(line.interpolate(t, normalized=True)) for t in np.linspace(0, 1, n)])
        runs = []
        c = list(line.coords)
        for i, (a, b) in enumerate(zip(c[:-1], c[1:])):
            seg = LineString([a, b])
            m = max(2, int(seg.length / 10))
            dd = np.array([edge.distance(seg.interpolate(t, normalized=True)) for t in np.linspace(0, 1, m)])
            runs.append({"run": i, "length_m": round(seg.length), "median_m": round(float(np.median(dd)), 1), "max_m": round(float(dd.max()), 1)})
        out[p["id"]] = {"garden": p["garden"], "length_m": round(line.length), "median_m": round(float(np.median(d)), 1), "within_10m": round(float((d < 10).mean()), 2), "within_20m": round(float((d < 20).mean()), 2), "runs": runs}
    return out


def main():
    edge = boundary()
    now = report(json.loads((ROOT / "research/layers/walls_1860.geojson").read_text(encoding="utf-8")), edge)
    before = {}
    if "--rev" in sys.argv:
        rev = sys.argv[sys.argv.index("--rev") + 1]
        before = report(json.loads(subprocess.run(["git", "-C", str(ROOT), "show", f"{rev}:research/layers/walls_1860.geojson"], capture_output=True, check=True).stdout), edge)
    for wid, r in now.items():
        b = before.get(wid)
        print(f"{wid} {r['garden']:14s} {r['length_m']:6d} m: median {r['median_m']:5.1f} m from the park outline, {r['within_10m']:.0%} within 10 m, {r['within_20m']:.0%} within 20 m" + (f"   before: median {b['median_m']} m, {b['within_10m']:.0%} within 10 m" if b else ""))
        for run in r["runs"]:
            br = b["runs"][run["run"]] if b and run["run"] < len(b["runs"]) else None
            print(f"    run {run['run']:2d} {run['length_m']:5d} m  median {run['median_m']:5.1f}  max {run['max_m']:5.1f}" + (f"   before {br['median_m']:5.1f} / {br['max_m']:5.1f}" if br else ""))


if __name__ == "__main__":
    main()
