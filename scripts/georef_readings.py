"""Round 8 readings by eye -> research/georef/check_points.json (the blind check set) and research/georef/control_r8.csv.

  uv run python scripts/georef_readings.py

Reads research/georef/readings_r8/*.jsonl, the readers' own lines (one point each; how they read them:
docs/rounds/common/palace_r8_readers.md). Writes the check set only while it is not frozen; once frozen
(`scripts/georef.py freeze`), it stops if the check points it would write differ from the frozen ones, so the set
can never be edited by a rerun. A check point closer than 30 m to a Round 1 fit point, or than 60 m to another check
point, breaks the readers' rule and is not admitted (listed with the reason, before any error is computed); so is a
point its reader withdrew before any error was computed (WITHDRAWN). Control points are rewritten every run.

The readers' first wave held check points 60 m from any Round 1 fit point and found only 19: the Round 1 fit already
holds most sharp features that survive. Before any error was computed the rule became 30 m (wave 2, from 18:48 UTC);
each check point keeps `nearest_fit_m`, and both the previous and the new fit contain every Round 1 point, so the
comparison stays even.
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import georef  # noqa: E402

ROOT = georef.ROOT
READINGS = ROOT / "research/georef/readings_r8"
FIELDS = ["id", "plan_x", "plan_y", "lat", "lon", "datum", "feature", "kind", "area", "quality", "use", "note"]
CHECK_FROM_FIT_M = 30.0
CHECK_APART_M = 60.0
# Set aside by their readers before any error was computed (their notes, docs/rounds/README.md).
WITHDRAWN = {"K-QB-04": "withdrawn by its reader as a probable misidentification (the bridge stands 30 m west and 85 m north of 鉴碧亭's island; the plan's 20 m east and 110 m north)"}
# Control points on the same rigid feature as a check point: they would decide the check point's error.
SAME_FEATURE = {"C8-XY-01": "a corner of 方河, the pool whose centre is check point K-XY-01", "C8-XY-02": "a corner of 方河, the pool whose centre is check point K-XY-01"}
RULE = (
    "Picked before any fit of Round 8, by five readers who never saw a transform's prediction or an error: each feature "
    "found by its form on a crop of today's imagery and a crop of the plan whose centre was shifted at random by up to 35 m, "
    "read on zoomed crops with labelled grids. Only features unchanged since 1860 (lake and island shores that keep their old "
    "form, ruin foundations in place, gates rebuilt on their base, the garden wall rebuilt on the old line); each at least "
    "30 m from any Round 1 fit point (60 m in the first wave; changed before any error was computed, because the Round 1 fit "
    "already holds most sharp surviving features) and 60 m from every other check point. Frozen by a SHA-256 of the points; never "
    "edited after: a doubt goes in `annotations`. No Round 8 control point within 60 m of a check point enters a fit (georef.py)."
)


def read_lines():
    rows = []
    for f in sorted(READINGS.glob("*.jsonl")):
        for k, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError as e:
                raise SystemExit(f"{f.name}:{k}: {e}")
            r["_file"] = f.name
            rows.append(r)
    return rows


def main():
    rows = read_lines()
    ids = [r["id"] for r in rows]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        raise SystemExit(f"ids written twice: {sorted(dup)}")
    old = [r for r in georef.read_points() if r["use"] == "fit"]
    oe, on = georef._TO_UTM.transform(np.array([r["lon"] for r in old]), np.array([r["lat"] for r in old]))
    checks, refused, control = [], [], []
    for r in rows:
        e, n = georef._TO_UTM.transform(r["lon"], r["lat"])
        d = np.hypot(oe - e, on - n)
        if r["set"] == "check":
            p = {
                "id": r["id"], "region": str(georef.region_of(r["plan_x"], r["plan_y"])[0]), "reader_region": r["region"], "kind": r["kind"],
                "feature": r["feature"], "lon": round(float(r["lon"]), 7), "lat": round(float(r["lat"]), 7),
                "plan_x": round(float(r["plan_x"]), 1), "plan_y": round(float(r["plan_y"]), 1), "plan_read": r["plan_read"],
                "ground_from": r["ground_from"], "unchanged_because": r.get("unchanged_because", ""), "sources": "S01;S160", "note": r.get("note", ""),
            }
            p["nearest_fit_m"] = round(float(d.min()), 1)
            if r["id"] in WITHDRAWN:
                refused.append({**p, "reason": WITHDRAWN[r["id"]]})
            elif d.min() < CHECK_FROM_FIT_M:
                refused.append({**p, "reason": f"{d.min():.0f} m from Round 1 fit point {old[int(d.argmin())]['id']}"})
            else:
                checks.append(p)
        elif r["set"] == "control":
            control.append({
                "id": r["id"], "plan_x": round(float(r["plan_x"]), 1), "plan_y": round(float(r["plan_y"]), 1), "lat": round(float(r["lat"]), 7), "lon": round(float(r["lon"]), 7),
                "datum": f"WGS84 via Esri ({r['ground_from']})", "feature": r["feature"], "kind": r["kind"], "area": str(georef.region_of(r["plan_x"], r["plan_y"])[0]),
                "quality": 1 if r["plan_read"] == "sure" else 2, "use": "excluded" if r["id"] in SAME_FEATURE else "fit",
                "note": SAME_FEATURE.get(r["id"]) or " ".join(x for x in (r.get("unchanged_because", ""), r.get("note", "")) if x),
            })
    checks.sort(key=lambda p: p["id"])
    # Two check points closer than CHECK_APART_M: the later id gives way.
    kept = []
    for p in checks:
        e, n = georef._TO_UTM.transform(p["lon"], p["lat"])
        clash = [q for q in kept if np.hypot(*(np.array(georef._TO_UTM.transform(q["lon"], q["lat"])) - (e, n))) < CHECK_APART_M]
        if clash:
            refused.append({**p, "reason": f"within {CHECK_APART_M:.0f} m of check point {clash[0]['id']}"})
        else:
            kept.append(p)
    checks = kept
    if georef.CHECK_PATH.exists():
        d = json.loads(georef.CHECK_PATH.read_text(encoding="utf-8"))
        if d.get("sha256"):
            if georef._sha(checks) != d["sha256"]:
                raise SystemExit("check_points.json is frozen and the readings would change it: the check set is never edited")
            print("check set frozen and unchanged:", len(checks))
            checks = None
    if checks is not None:
        out = {
            "title": "Blind check set for the placement of the plan S01 on today's ground (Round 8)",
            "rule": RULE,
            "datum": "lon, lat WGS84 (EPSG:4326), read on Esri World Imagery (S160, Web Mercator on WGS84, checked against OSM to about 3 m); plan_x, plan_y pixels on research/raw/plans/princeton_mosaic.jpg",
            "exclusion_m": georef.EXCLUDE_M,
            "points": checks,
            "not_admitted": refused,
            "annotations": [],
            "sha256": "",
            "frozen": "",
        }
        georef.CHECK_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("check set written (not frozen):", len(checks), "points;", len(refused), "not admitted")
    control.sort(key=lambda r: r["id"])
    with open(georef.CONTROL_R8, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(control)
    print("control_r8.csv:", len(control))


if __name__ == "__main__":
    main()
