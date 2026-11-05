"""Round 9: context for the path readers, in plan pixels. Run once from the repo: uv run python /opt/data/cache/scratch/palace_r9_tools/ctx.py"""
import csv
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path("/opt/data/workspace/000_Dev/palace-beijing-yaga-sh")
sys.path.insert(0, str(REPO / "scripts"))
import georef  # noqa: E402

OUT = Path("/opt/data/cache/scratch/palace_r9_context")
OUT.mkdir(exist_ok=True)

rows = list(csv.DictReader(open(REPO / "research/buildings.csv", encoding="utf-8")))
with open(OUT / "rows.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "parent_id", "name_zh", "type", "hall_class", "plan_x", "plan_y", "bays_plan", "garden"])
    for r in rows:
        if r["plan_x"]:
            w.writerow([r["id"], r["parent_id"], r["name_zh"] or r["name_on_plan"], r["type"], r["hall_class"], r["plan_x"], r["plan_y"], r["bays_plan"], r["garden"]])

gates = json.load(open(REPO / "research/plan/gates.json", encoding="utf-8"))
with open(OUT / "gates.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "name", "plan_x", "plan_y", "note"])
    for g in gates:
        w.writerow([g["id"], g.get("label", ""), g["x"], g["y"], g.get("note", "")])

br = json.load(open(REPO / "research/layers/bridges_1860.geojson", encoding="utf-8"))["features"]
with open(OUT / "bridges.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "building_id", "name_zh", "x1", "y1", "x2", "y2", "note"])
    for b in br:
        c = np.array(b["geometry"]["coordinates"])
        xs, ys = georef.wgs84_to_plan(c[:, 0], c[:, 1])
        p = b["properties"]
        w.writerow([p["id"], p.get("building_id", ""), p.get("name_zh", ""), int(xs[0]), int(ys[0]), int(xs[-1]), int(ys[-1]), p.get("note", "")])

sc = json.load(open(REPO / "research/layers/scenes_1860.geojson", encoding="utf-8"))["features"]
with open(OUT / "scenes.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "name_zh", "garden", "cx", "cy", "minx", "miny", "maxx", "maxy"])
    for s in sc:
        g = s["geometry"]
        ring = np.array(g["coordinates"][0] if g["type"] == "Polygon" else g["coordinates"][0][0])
        xs, ys = georef.wgs84_to_plan(ring[:, 0], ring[:, 1])
        p = s["properties"]
        w.writerow([p["id"], p.get("name_zh", ""), p.get("garden", ""), int(xs.mean()), int(ys.mean()), int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())])
print("written", OUT)
