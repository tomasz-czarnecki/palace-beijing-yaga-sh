"""Round 9: which of today's park paths (OSM, research/layers/osm_today) may follow an alignment of 1860, and which are modern. Writes research/paths/osm_judged.csv; prints the counts.

  uv run python tools/osm_paths.py          (after scripts/paths1860.py)

A modern path is never evidence by itself: nothing here goes into paths_1860. The judgement, per OSM way of the kinds walked in the park
(footway, path, pedestrian, steps, cycleway, track, service) inside the three garden walls, in UTM metres:
  over_water   share of its length over the water of 1860 (water_1860), more than 2.5 m from a bridge: it runs on fill, so modern there;
  through_box  share through a box of 1860 (halls_1860);
  near_way     share within 5 m of a way traced in Round 9 (paths_1860, A or B, not the links made here);
  on_shore     share on the land of 1860 within 8 m of its water: along an old shore or on a dike.
Class: `modern` when over_water + through_box >= 0.25; else `old_alignment_plausible` when near_way >= 0.6 or on_shore >= 0.7;
else `undecided`. Plausible means only that it lies where a way of 1860 lay or could lie (a shore, a dike), not that it is that way.
"""

import csv
import json
import sys
from collections import Counter
from pathlib import Path

import shapely
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import paths1860 as P  # noqa: E402

KINDS = {"footway", "path", "pedestrian", "steps", "cycleway", "track", "service"}


def main():
    boxes, by_row, water, waters, bridges, gates, walls, wall_segs, scenes = P.load_world()
    hull = shapely.concave_hull(shapely.MultiPoint([c for w in walls for c in w.coords]), ratio=0.3).buffer(5)
    wet = water.difference(unary_union([g.buffer(2.5) for _, g in bridges.values()]))
    boxes_u = unary_union([b.poly for b in boxes])
    ways = [P.xz_geom(f["geometry"]) for f in json.load(open(P.LAYERS / "paths_1860.geojson", encoding="utf-8"))["features"]
            if f["properties"]["confidence"] in ("A", "B") and f["properties"]["kind"] != "boat_route"]
    near = unary_union(ways).buffer(5)
    shore = water.buffer(8).difference(water)
    for g in (wet, boxes_u, near, shore, hull):
        shapely.prepare(g)
    out = []
    for f in json.load(open(P.LAYERS / "osm_today.geojson", encoding="utf-8"))["features"]:
        p = f["properties"]
        if p.get("highway") not in KINDS or f["geometry"]["type"] != "LineString":
            continue
        L = P.xz_geom(f["geometry"])
        if L.length < 3 or not hull.intersects(L):
            continue
        L = L.intersection(hull)
        if L.is_empty or L.length < 3:
            continue
        n = L.length
        s = {k: round(L.intersection(g).length / n, 2) for k, g in (("over_water", wet), ("through_box", boxes_u), ("near_way", near), ("on_shore", shore))}
        cls = "modern" if s["over_water"] + s["through_box"] >= 0.25 else "old_alignment_plausible" if s["near_way"] >= 0.6 or s["on_shore"] >= 0.7 else "undecided"
        out.append({"osm_id": p["id"], "highway": p["highway"], "name": p.get("name", ""), "length_m": round(n, 1), **s, "class": cls})
    with open(P.PATHS / "osm_judged.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(sorted(out, key=lambda r: str(r["osm_id"])))
    c, m = Counter(), Counter()
    for r in out:
        c[r["class"]] += 1
        m[r["class"]] += r["length_m"]
    print(f"{len(out)} OSM ways inside the walls, {round(sum(m.values()))} m:", {k: (c[k], round(m[k])) for k in sorted(c)})


if __name__ == "__main__":
    main()
