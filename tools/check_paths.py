"""Round 9: checks the ways of 1860 (research/layers/paths_1860, landings_1860, routes_1860, written by scripts/paths1860.py). Exits non-zero on a failure.

  uv run python tools/check_paths.py [--json]

Prints:
  - count and length by kind and by confidence (A / B / C), and how many are assumed;
  - the scenes with traced ways;
  - the joint gaps: for every end of a line, the distance to what it meets (a hall's door, a gate or a box walked through, a bridge end,
    a landing, another line); before snapping (the trace through the transform, `gap_before_m`) and after. FAILS above 0.5 m for an
    A or B line;
  - lines that cross a box, a garden wall or water (not over a bridge), and boat routes over land. FAILS for an A or B line
    unless research/paths/exceptions.csv gives the reason;
  - bridge ends without an approach: FAILS unless research/paths/bridge_ends.csv (written by the generator) says why;
  - routes whose path ids or stops are missing: FAILS.
"""

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import Point

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import paths1860 as P  # noqa: E402

TOL = 0.5


def main():
    as_json = "--json" in sys.argv
    boxes, by_row, water, waters, bridges, gates, walls, wall_segs, scenes = P.load_world()
    router = P.Router(boxes, water, bridges, wall_segs)
    snap = P.Snapper(boxes, by_row, bridges, gates, water, router, scenes)
    paths = json.load(open(P.LAYERS / "paths_1860.geojson", encoding="utf-8"))["features"]
    lands = json.load(open(P.LAYERS / "landings_1860.geojson", encoding="utf-8"))["features"]
    routes = json.load(open(P.LAYERS / "routes_1860.geojson", encoding="utf-8"))["features"]
    exceptions = {(r["key"], r["check"]): r["reason"] for r in P.rows(P.PATHS / "exceptions.csv")}
    ends_note = {(r["bridge"], r["end"]): r for r in P.rows(P.PATHS / "bridge_ends.csv")}
    fails = []

    lines = [(f["properties"], P.xz_geom(f["geometry"])) for f in paths]
    by_kind, by_conf = defaultdict(lambda: [0, 0.0]), defaultdict(lambda: [0, 0.0])
    for p, L in lines:
        by_kind[p["kind"]][0] += 1
        by_kind[p["kind"]][1] += L.length
        by_conf[p["confidence"]][0] += 1
        by_conf[p["confidence"]][1] += L.length
    traced = [p for p, _ in lines if not p["id"].startswith(("RC-", "BA-", "RL-", "DL-"))]
    scenes_traced = sorted({p["scene"] for p in traced if p["scene"]})

    # what an end may meet
    doors = np.array([d for b in boxes if not b.walk_through for d in b.doors().values()])
    through = [b.poly.buffer(0.3) for b in boxes if b.walk_through]
    through_u = shapely.unary_union(through)
    gate_pts = np.array([g[1] for g in gates.values()])
    bridge_ends = np.array([snap.land_end(np.asarray(c)) for _, g in bridges.values() for c in (g.coords[0], g.coords[-1])])
    land_pts = np.array([P.xz_geom(f["geometry"]).coords[0] for f in lands])
    tree = shapely.STRtree([L for _, L in lines])

    def gap(p, L, i):
        e = np.asarray(L.coords[i])
        q = Point(e)
        best = []
        for arr in (doors, gate_pts, bridge_ends, land_pts):
            if len(arr):
                best.append(float(np.min(np.hypot(arr[:, 0] - e[0], arr[:, 1] - e[1]))))
        best.append(through_u.distance(q))
        for j in tree.query(q.buffer(5)):
            o, M = lines[int(j)]
            if o["id"] != p["id"]:
                best.append(M.distance(q))
        return min(best)

    after = []
    for p, L in lines:
        for i in (0, -1):
            g = gap(p, L, i)
            after.append((g, p["id"], p["confidence"], "from" if i == 0 else "to"))
            if g > TOL and p["confidence"] in ("A", "B") and (p["id"], "joint") not in exceptions:
                fails.append(f"joint: {p['id']} ({p['confidence']}) {'from' if i == 0 else 'to'} end {g:.2f} m from anything it may meet")
    before = [g for p, _ in lines if not p["id"].startswith(("RC-", "BA-", "RL-", "DL-")) for g in p["gap_before_m"] if g is not None]
    landing_before = [f["properties"]["gap_before_m"] for f in lands]

    # crossings
    obst = router.land_obstacle()
    cross = []
    for p, L in lines:
        boat = p["kind"] == "boat_route"
        allow = set(filter(None, p["in_box"].split(";")))
        ob = router.land_obstacle(allow) if allow else obst
        if boat:
            bad = router.blocked_line(L, None, True)
            what = {"land": bad} if bad > 0.05 else {}
        else:
            what = {k: v for k, v in (("box", L.intersection(ob[0]).length), ("water", L.intersection(ob[1]).length), ("wall", L.intersection(ob[2]).length)) if v > 0.05}
            if p["kind"] == "steps":  # steps climb onto the platform of the hall they lead to
                mine = set(allow) | {x.split(":")[0] for x in (p["from_at"], p["to_at"]) if x and x[0] in "FXLDG" and ":" in x}
                ob2 = router.land_obstacle(mine)
                what = {k: v for k, v in (("box", L.intersection(ob2[0]).length), ("water", L.intersection(ob2[1]).length), ("wall", L.intersection(ob2[2]).length)) if v > 0.05}
        if what:
            cross.append((p["id"], p["kind"], p["confidence"], {k: round(v, 1) for k, v in what.items()}))
            if p["confidence"] in ("A", "B") and max(what.values()) > TOL and (p["id"], "cross") not in exceptions:
                fails.append(f"crosses: {p['id']} ({p['confidence']}, {p['kind']}) {what}")

    # landings: on the shore
    off_shore = []
    for f in lands:
        q = P.xz_geom(f["geometry"])
        d = water.boundary.distance(q)
        if d > 1.0:
            off_shore.append((f["properties"]["id"], round(d, 1), "in water" if water.contains(q) else "on land"))

    # bridges
    land_lines = [L for p, L in lines if p["kind"] != "boat_route"]
    no_app = []
    for bid, (bp, g) in sorted(bridges.items()):
        for n, c in enumerate((g.coords[0], g.coords[-1]), 1):
            e = Point(snap.land_end(np.asarray(c)))
            if not any(L.distance(e) <= 1.0 for L in land_lines):
                note = ends_note.get((bid, str(n)), {})
                no_app.append((bid, n, note.get("reason", "")))
                if not note.get("reason"):
                    fails.append(f"bridge {bid} end {n}: no approach and no reason in research/paths/bridge_ends.csv")
    both = sum(1 for bid in bridges if not any(x[0] == bid for x in no_app))

    # routes
    ids = {p["id"] for p, _ in lines} | set(bridges)
    for f in routes:
        r = f["properties"]
        missing = [i for i in r["path_ids"] if i not in ids]
        if missing:
            fails.append(f"route {r['id']}: path ids not in the layers: {missing}")
        for s in r["stops"]:
            if s["off_m"] > 25:
                fails.append(f"route {r['id']}: stop {s['id']} {s['off_m']} m off the route")

    g_after = np.array([a[0] for a in after])
    g_ab = np.array([a[0] for a in after if a[2] in ("A", "B")])
    out = {
        "lines": len(lines), "length_m": round(sum(L.length for _, L in lines)),
        "by_kind": {k: {"n": v[0], "m": round(v[1])} for k, v in sorted(by_kind.items())},
        "by_confidence": {k: {"n": v[0], "m": round(v[1])} for k, v in sorted(by_conf.items())},
        "assumed": sum(1 for p, _ in lines if p["assumed"]),
        "traced": len(traced), "bridge_approaches_added": sum(1 for p, _ in lines if p["id"].startswith("BA-")), "links_added": sum(1 for p, _ in lines if p["id"].startswith(("RC-", "RL-"))),
        "landings": dict(Counter(f["properties"]["kind"] for f in lands)), "landings_by_confidence": dict(Counter(f["properties"]["confidence"] for f in lands)),
        "scenes_with_traced_ways": len(scenes_traced),
        "gap_before_m": {"n": len(before), "median": round(float(np.median(before)), 1), "p90": round(float(np.percentile(before, 90)), 1), "max": round(float(np.max(before)), 1)},
        "landing_to_shore_before_m": {"median": round(float(np.median(landing_before)), 1), "max": round(float(np.max(landing_before)), 1)},
        "gap_after_m": {"n": len(g_after), "median": round(float(np.median(g_after)), 2), "max": round(float(g_after.max()), 2), "over_0.5": int((g_after > TOL).sum()),
                        "a_b_max": round(float(g_ab.max()), 2) if len(g_ab) else None, "a_b_over_0.5": int((g_ab > TOL).sum())},
        "crossing": {"n": len(cross), "a_b": sum(1 for c in cross if c[2] in ("A", "B")), "list": cross},
        "landings_off_shore": off_shore,
        "bridges": {"n": len(bridges), "approached_both_ends": both, "ends_without": no_app},
        "routes": [{"id": f["properties"]["id"], "length_m": f["properties"]["length_m"], "lines": len(f["properties"]["path_ids"]), "stops": len(f["properties"]["stops"])} for f in routes],
        "fails": fails,
    }
    if as_json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        print(f"{out['lines']} lines, {out['length_m']} m; traced {out['traced']}, bridge approaches added {out['bridge_approaches_added']}, links added {out['links_added']}; assumed {out['assumed']}")
        print("by kind:", ", ".join(f"{k} {v['n']} ({v['m']} m)" for k, v in out["by_kind"].items()))
        print("by confidence:", ", ".join(f"{k} {v['n']} ({v['m']} m)" for k, v in out["by_confidence"].items()))
        print(f"landings and docks: {out['landings']}, by confidence {out['landings_by_confidence']}; off the shore by more than 1 m: {len(off_shore)} {off_shore[:8]}")
        print(f"scenes with traced ways: {out['scenes_with_traced_ways']}")
        print(f"joint gaps before snapping (traced ends): {out['gap_before_m']}; landings to the shore before: {out['landing_to_shore_before_m']}")
        print(f"joint gaps after: {out['gap_after_m']}")
        print(f"crossing a box, wall or water: {out['crossing']['n']} lines, {out['crossing']['a_b']} of them A or B: {cross[:12]}")
        print(f"bridges: {len(bridges)}, both ends approached {both}; ends without an approach {len(no_app)}: {no_app}")
        print("routes:", out["routes"])
        print("FAIL" if fails else "ok", *fails[:30], sep="\n  ")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
