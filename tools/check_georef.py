"""The placement check: the frozen blind check set against the fit in use, and the layers against the fit.

  uv run python tools/check_georef.py                   check; exits non-zero on a failure
  uv run python tools/check_georef.py --write-baseline  after a deliberate refit: store the medians as the new baseline

Fails if
- research/georef/check_points.json no longer matches the hash written when it was frozen (the set is never edited);
- the median distance of any region on the check set gets worse than the committed baseline
  (research/georef/check_baseline.json) by more than 0.1 m;
- research/buildings.csv holds a plan-placed position that the fit in use would put more than 0.5 m elsewhere
  (the rows and layers were not rebuilt after a refit: run scripts/build_r1.py and the steps after it).
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import georef  # noqa: E402

BASELINE = ROOT / "research/georef/check_baseline.json"
TOLERANCE_M = 0.1
SYNC_M = 0.5


def corrected_rows():
    """Rows whose lat/lon a fact replaced (evidence/facts.csv, decision correct): they no longer follow the plan."""
    out = set()
    with open(ROOT / "research/evidence/facts.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["decision"] == "correct" and r["field"] in ("lat", "lon"):
                out.add(r["id"])
    return out


def main():
    check = georef.read_check()
    errs = georef.check_errors(georef._model_of(georef.JSON_PATH), check["points"])
    now = georef.check_summary(errs)
    fit_name = json.loads(georef.JSON_PATH.read_text(encoding="utf-8"))["transform"]["name"]
    if "--write-baseline" in sys.argv:
        BASELINE.write_text(json.dumps({"sha256": check["sha256"], "fit": fit_name, "by_region": now}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("baseline written:", BASELINE.relative_to(ROOT))
    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    fails = []
    if base["sha256"] != check["sha256"]:
        fails.append("the baseline was written for another check set")
    print(f"check set: {len(check['points'])} points, frozen {check.get('frozen')}; fit: {fit_name}")
    print(f"{'region':9s} {'n':>3s} {'median':>7s} {'p90':>6s} {'max':>6s}   baseline median")
    for rg in ("all",) + georef.REGIONS:
        s, b = now[rg], base["by_region"].get(rg, {})
        flag = ""
        if s["median_m"] is not None and b.get("median_m") is not None and s["median_m"] > b["median_m"] + TOLERANCE_M:
            fails.append(f"{rg}: median {s['median_m']} m, baseline {b['median_m']} m")
            flag = "  WORSE"
        print(f"{rg:9s} {s['n']:3d} {s['median_m']!s:>7s} {s['p90_m']!s:>6s} {s['max_m']!s:>6s}   {b.get('median_m')!s}{flag}")

    # The rows follow the fit in use.
    skip = corrected_rows()
    rows = [r for r in csv.DictReader(open(ROOT / "research/buildings.csv", encoding="utf-8", newline="")) if r["plan_x"] and r["lat"] and r["pos_source"].startswith("S01") and r["id"] not in skip]
    lon, lat = georef.plan_to_wgs84(np.array([float(r["plan_x"]) for r in rows]), np.array([float(r["plan_y"]) for r in rows]))
    k = np.cos(np.radians(40.0)) * 111320
    d = np.hypot((lon - np.array([float(r["lon"]) for r in rows])) * k, (lat - np.array([float(r["lat"]) for r in rows])) * 110950)
    off = [(r["id"], round(float(v), 2)) for r, v in zip(rows, d) if v > SYNC_M]
    print(f"rows placed from the plan: {len(rows)}, off the fit in use by more than {SYNC_M} m: {len(off)}")
    if off:
        fails.append(f"{len(off)} rows of buildings.csv do not follow the fit in use, e.g. {off[:5]}: rerun scripts/build_r1.py and the steps after it")
    if fails:
        print("FAIL:\n  " + "\n  ".join(fails))
        sys.exit(1)
    print("ok")


if __name__ == "__main__":
    main()
