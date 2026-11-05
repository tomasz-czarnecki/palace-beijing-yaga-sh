"""What a refit moved: boxes, rows and layers in the working tree against a git revision.

  uv run python tools/georef_shift.py [REV] [--write]     REV defaults to HEAD; --write stores research/georef/shift_r8.json

Distances in metres between the same id before and after: the centre of a box, a row's position, the centroid of a
layer feature (walls: every vertex). Ids are never renumbered, so the same id is the same thing.
"""

import csv
import io
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from shapely.geometry import shape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research/georef/shift_r8.json"
K_LON = np.cos(np.radians(40.005)) * 111320
K_LAT = 110950


def at_rev(rev, rel):
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{rev}:{rel}"], capture_output=True, check=True).stdout.decode("utf-8")


def metres(a, b):
    return float(np.hypot((a[0] - b[0]) * K_LON, (a[1] - b[1]) * K_LAT))


def stats(d):
    d = np.asarray(d, float)
    if not len(d):
        return {"n": 0}
    return {"n": int(len(d)), "median_m": round(float(np.median(d)), 1), "p90_m": round(float(np.percentile(d, 90)), 1), "max_m": round(float(d.max()), 1),
            "over_3_m": int((d > 3).sum()), "over_5_m": int((d > 5).sum()), "over_10_m": int((d > 10).sum())}


def centres(fc, key="id"):
    out = {}
    for f in fc["features"]:
        g = shape(f["geometry"])
        c = g.centroid if not g.is_empty else None
        if c is not None:
            out[f["properties"][key]] = (c.x, c.y, f["properties"])
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    rev = args[0] if args else "HEAD"
    res = {"against": rev}
    # Boxes of the 3D view.
    rel = "site/reconstruction/data/halls_1860.geojson"
    old, new = centres(json.loads(at_rev(rev, rel))), centres(json.loads((ROOT / rel).read_text(encoding="utf-8")))
    common = sorted(set(old) & set(new))
    d = {i: metres(old[i], new[i]) for i in common}
    res["boxes"] = stats(list(d.values()))
    res["boxes"]["only_before"], res["boxes"]["only_after"] = sorted(set(old) - set(new)), sorted(set(new) - set(old))
    by_basis = {}
    for i in common:
        by_basis.setdefault(new[i][2].get("basis", ""), []).append(d[i])
    res["boxes_by_basis"] = {k: stats(v) for k, v in sorted(by_basis.items())}
    by_garden = {}
    for i in common:
        by_garden.setdefault(new[i][2].get("garden", ""), []).append(d[i])
    res["boxes_by_garden"] = {k: stats(v) for k, v in sorted(by_garden.items())}
    res["boxes_largest"] = [[i, round(d[i], 1)] for i in sorted(d, key=d.get, reverse=True)[:10]]
    # Rows.
    rel = "research/buildings.csv"
    o = {r["id"]: r for r in csv.DictReader(io.StringIO(at_rev(rev, rel)))}
    n = {r["id"]: r for r in csv.DictReader(open(ROOT / rel, encoding="utf-8", newline=""))}
    rd = [metres((float(o[i]["lon"]), float(o[i]["lat"])), (float(n[i]["lon"]), float(n[i]["lat"]))) for i in n if i in o and o[i]["lat"] and n[i]["lat"]]
    res["rows"] = stats(rd)
    # Layers.
    res["layers"] = {}
    for name in ("walls_1860", "water_1860", "islands_1860", "hills_1860", "bridges_1860", "scenes_1860", "footprints_1860", "fields_1860"):
        rel = f"research/layers/{name}.geojson"
        a, b = json.loads(at_rev(rev, rel)), json.loads((ROOT / rel).read_text(encoding="utf-8"))
        if name == "walls_1860":
            va = {f["properties"]["id"]: f["geometry"]["coordinates"] for f in a["features"]}
            vb = {f["properties"]["id"]: f["geometry"]["coordinates"] for f in b["features"]}
            vd, gd = [], []
            for i in va:
                if i not in vb:
                    continue
                if isinstance(va[i][0], list):
                    if len(va[i]) == len(vb[i]):
                        vd += [metres(p, q) for p, q in zip(va[i], vb[i])]
                else:
                    gd.append(metres(va[i], vb[i]))
            res["layers"]["walls_1860"] = {"wall_vertices": stats(vd), "gates": stats(gd)}
            continue
        ca, cb = centres(a), centres(b)
        res["layers"][name] = stats([metres(ca[i], cb[i]) for i in ca if i in cb])
    print(json.dumps(res, ensure_ascii=False, indent=1))
    if "--write" in sys.argv:
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
