#!/usr/bin/env python3
"""Checks the detailed models (Round 13): every models/*/summary.json.

  uv run python tools/check_models.py

Fails (exit 1) on:
  - a summary without its sources: params.json missing, a figure with no source, a source id not in research/sources.md, a README.md without an evidence list;
  - a GLB that does not load as scripts/model_mesh.py writes it (one node, one mesh, quantised positions), or differs from its published copy (site/reconstruction/models/<ID>/model.glb), or is not in data/models.json;
  - `hides` listing one of the model's own boxes;
  - a joint more than JOINT_M off: every contact of joints.json (wall feet, plinths, stair feet, basin feet, paving) against the walk surface of Round 10
    (gap = the model's underside minus the ground; above JOINT_M it floats; below -BURIED_M it is buried deeper than a foundation course);
  - a way of Round 9 that ends at the model's boxes and is not within JOINT_M of an entry of the model (a door, a stair foot) in plan and height, unless it is drawn by the model itself (steps, galleries);
  - a file over the budget: GLB_GZ_MB compressed, GLB_RAW_MB raw.
Writes models/check_models.json.
"""

import gzip
import json
import re
import sys
from pathlib import Path

import numpy as np
from shapely.geometry import Point, Polygon

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))
from check_ground import NewGround  # noqa: E402
from model_mesh import read_glb  # noqa: E402
from scene1860 import to_xz  # noqa: E402

JOINT_M, BURIED_M = 0.5, 1.0
GLB_GZ_MB, GLB_RAW_MB = 1.5, 3.0


def main():
    G = NewGround(ROOT)
    sources = set(re.findall(r"^\|\s*(S\d+)\s*\|", (ROOT / "research/sources.md").read_text(encoding="utf-8"), re.M)) | set(re.findall(r"\b(S\d+)\b", (ROOT / "research/sources.md").read_text(encoding="utf-8")))
    published = json.load(open(ROOT / "site/reconstruction/data/models.json", encoding="utf-8"))["models"]
    halls = json.load(open(ROOT / "site/reconstruction/data/halls_1860.geojson", encoding="utf-8"))["features"]
    paths = json.load(open(ROOT / "site/reconstruction/data/paths_1860.geojson", encoding="utf-8"))["features"]
    fails, report = [], {}
    for sp in sorted((ROOT / "models").glob("*/summary.json")):
        folder = sp.parent
        sm = json.load(open(sp, encoding="utf-8"))
        mid = sm["id"]
        rep = report.setdefault(mid, {"folder": folder.name})
        bad = lambda msg: fails.append(f"{mid}: {msg}")
        # sources
        pj = folder / "params.json"
        if not pj.exists():
            bad("no params.json")
        else:
            params = json.load(open(pj, encoding="utf-8"))["params"]
            for k, v in params.items():
                ids = re.findall(r"S\d+", v.get("source", ""))
                if not ids:
                    bad(f"figure {k} has no source")
                for s in ids:
                    if s not in sources:
                        bad(f"figure {k} cites {s}, not in sources.md")
            rep["figures"] = len(params)
            rep["grades"] = {g: sum(1 for v in params.values() if v["grade"] == g) for g in "ABC"}
        readme = folder / "README.md"
        if not readme.exists() or "## Evidence" not in readme.read_text(encoding="utf-8"):
            bad("README.md without an '## Evidence' list")
        for k in ("line", "rows", "caption", "glb", "position", "rotationY"):
            if k not in sm:
                bad(f"summary without {k}")
        # the GLB
        glb = folder / sm["glb"]
        try:
            g, prims = read_glb(glb)
            rep["materials"] = len(g["materials"])
            rep["primitives"] = len(g["meshes"][0]["primitives"])
            verts = np.concatenate(list(prims.values()))
            rep["extent_m"] = [round(float(x), 1) for x in verts.max(0) - verts.min(0)]
            tris = sum(g["accessors"][p["indices"]]["count"] // 3 for p in g["meshes"][0]["primitives"])
            fill = sum(g["accessors"][p["indices"]]["count"] // 3 for p in g["meshes"][0]["primitives"] if g["materials"][p["material"]]["name"].endswith("~fill"))
            rep["triangles"], rep["fill_triangles"] = tris, fill
        except Exception as e:  # noqa: BLE001
            bad(f"GLB does not load: {e}")
            continue
        raw = glb.read_bytes()
        gz = len(gzip.compress(raw, 9))
        rep["glb_mb"], rep["glb_gz_mb"] = round(len(raw) / 1e6, 2), round(gz / 1e6, 2)
        if gz > GLB_GZ_MB * 1e6:
            bad(f"GLB {gz / 1e6:.2f} MB compressed, over {GLB_GZ_MB} MB")
        if len(raw) > GLB_RAW_MB * 1e6:
            bad(f"GLB {len(raw) / 1e6:.2f} MB, over {GLB_RAW_MB} MB")
        pub = ROOT / "site/reconstruction/models" / mid / "model.glb"
        if not pub.exists() or pub.read_bytes() != raw:
            bad("published GLB missing or stale: run scripts/building_pages.py")
        if mid not in published:
            bad("not in data/models.json")
        # hides
        own = {f["properties"]["id"] for f in halls if f["properties"]["building_id"] in [mid, *sm.get("aliases", [])]}
        for h in sm.get("hides", []):
            if h in own:
                bad(f"hides its own box {h}")
        # joints with the ground
        jj = json.load(open(folder / "joints.json", encoding="utf-8"))
        gaps = []
        for j in jj["joints"]:
            x, y, z = j["scene"]
            gy = G.land(x, z)
            if gy is None:
                gy = G.at(x, z)
            gap = y - gy
            gaps.append({"name": j["name"], "kind": j["kind"], "gap_m": round(gap, 2)})
            if gap > JOINT_M:
                bad(f"joint {j['name']} floats {gap:.2f} m above the ground")
            if gap < -BURIED_M:
                bad(f"joint {j['name']} buried {-gap:.2f} m")
        rep["joints"] = gaps
        rep["joint_gap_m"] = {"max_above": round(max(g["gap_m"] for g in gaps), 2), "max_below": round(-min(g["gap_m"] for g in gaps), 2), "n": len(gaps)}
        # the ways that end at the model's boxes
        entries = np.array([e["scene"] for e in jj["entries"]])
        ways = []
        for f in paths:
            p = f["properties"]
            for end, at in ((0, p.get("from_at")), (-1, p.get("to_at"))):
                if not at or at.split(":")[0] not in own:
                    continue
                drawn = p["kind"] in ("steps", "gallery")
                lon, lat = f["geometry"]["coordinates"][end][:2]
                x, z = to_xz(lon, lat)
                gy = G.land(x, z)
                y = (gy if gy is not None else 0) + 0.07
                for dk in jj.get("decks", []):  # Round 16: on a terrace the model draws, the way lies on it (3d.js lays it there)
                    if Polygon(dk["poly"]).contains(Point(x, z)):
                        y = dk["y"] + 0.07
                d = np.hypot(entries[:, 0] - x, entries[:, 2] - z)
                k = int(np.argmin(d))
                dy = abs(entries[k, 1] - y)
                ok = drawn or (d[k] <= JOINT_M and dy <= JOINT_M)
                ways.append({"way": p["id"], "kind": p["kind"], "at": at, "entry": jj["entries"][k]["name"], "plan_m": round(float(d[k]), 2), "height_m": round(float(dy), 2), "drawn_by_model": bool(drawn), "ok": bool(ok)})
                if not ok:
                    bad(f"way {p['id']} ({at}) ends {d[k]:.2f} m in plan, {dy:.2f} m in height from the nearest entry {jj['entries'][k]['name']}")
        rep["ways"] = ways
    json.dump({"fails": fails, "models": report, "limits": {"joint_m": JOINT_M, "buried_m": BURIED_M, "glb_gz_mb": GLB_GZ_MB, "glb_raw_mb": GLB_RAW_MB}}, open(ROOT / "models/check_models.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for mid, r in report.items():
        print(f"{mid}: {r.get('triangles')} triangles ({r.get('fill_triangles')} fill), GLB {r.get('glb_mb')} MB, {r.get('glb_gz_mb')} MB compressed; joints {r.get('joint_gap_m')}; ways {len(r.get('ways', []))}, {sum(not w['ok'] for w in r.get('ways', []))} off")
    if fails:
        print("FAIL:")
        for f in fails:
            print("  " + f)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
