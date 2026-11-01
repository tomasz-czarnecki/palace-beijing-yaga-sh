"""Round 6: the rows' new sizes, positions and part names as evidence/facts.csv rows. A record; facts.csv is hand-edited from here on.

  uv run python docs/rounds/common/palace_r6_facts_seed.py     (after palace_r6_merge.py and palace_r6_boxes_seed.py; starts from the committed facts.csv)
"""

import csv
import io
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
text = subprocess.run(["git", "show", "3fa83a0:research/evidence/facts.csv"], cwd=ROOT, capture_output=True, check=True).stdout.decode("utf-8")
reader = csv.DictReader(io.StringIO(text, newline=""))
fields, rows = reader.fieldnames, list(reader)
boxes = list(csv.DictReader(open(ROOT / "research/xiyanglou/boxes.csv", encoding="utf-8", newline="")))
parts = list(csv.DictReader(open(ROOT / "research/xiyanglou/parts.csv", encoding="utf-8", newline="")))


def add(bid, field, value, source, locator, basis, conf="C", decision="correct", reason=""):
    rows.append({"id": bid, "field": field, "value": value, "source_id": source, "locator": locator, "basis": basis, "suggest_confidence": conf, "decision": decision, "reason": reason})


# The row takes the size of its main box. (id, part word, why the old figure was wrong)
MAIN = {
    "XY01": ("main block", "39.7 x 38.6 m was the OSM ruin outline of the whole group"),
    "XY01-01": ("octagonal", "hall scale"), "XY01-N01": ("octagonal", "hall scale"), "XY01-02": ("pool", "hall scale"),
    "XY02": (None, "10 x 8 m was a guess. Whole east front, plate 3"),
    "XY03": ("gate", "typology"),
    "XY04": (None, "89 x 59 m stood in the wrong order: 88.64 m is N-S"),
    "XY04-01": ("central", "hall scale"), "XY04-N01": ("two-storey", "hall scale"),
    "XY05": ("gate block", "20 x 10 m was a guess"),
    "XY06": ("hall, two", "44 x 24.2 m was the OSM polygon, which follows the moat bank"),
    "XY07": ("pavilion", "typology"),
    "XY08": ("west block", "19 x 44 m stood with depth and frontage swapped, and was short"),
    "XY08-01": ("long block", "30.6 x 27.5 m was a hall scale of the whole H block"),
    "XY08-02": ("pool", "27.5 x 17.5 m came from a hall scale"),
    "XY08-N01": ("west waterwheel", "hall scale"), "XY08-N02": ("east block", "hall scale"),
    "XY09": ("hall", "59.2 x 51.0 m was an OSM polygon that holds 大水法's niche as well"),
    "XY10": ("niche", "depth 3 m: plan's arc is 4.4 m"),
    "XY10-N01": ("pyramid", "hall scale"), "XY10-N02": ("pyramid", "hall scale"),
    "XY11": ("throne", "12 x 6 m was a guess"),
    "XY12-02": ("pavilion", "hall scale"), "XY12-01": ("gate", "none recorded"),
    "XY13": ("gate", "8 x 1.5 m was a guess, against plate 19"),
    "XY15": ("screen", "6 x 1 m was a guess"),
    "XY15-N01": ("range", "hall scale"), "XY15-N02": ("range", "hall scale"),
}
for bid, (word, why) in MAIN.items():
    mine = [b for b in boxes if b["building_id"] == bid and (word is None or word in b["part"])] or [b for b in boxes if b["building_id"] == bid]
    b = mine[0]
    f, d = b["frontage_m"], b["depth_m"]
    if bid == "XY02":
        f = "20.1"
    if bid == "XY04":
        f, d = "58.56", "88.64"
    src = b["sources"]
    add(bid, "frontage_m", f, src, "research/xiyanglou/boxes.csv", b["basis"], b["confidence"], "correct", why)
    add(bid, "depth_m", d, src, "research/xiyanglou/boxes.csv", b["basis"], b["confidence"], "correct", why)
    if bid not in ("XY07", "XY15", "XY04", "XY11", "XY02", "XY12-02", "XY12-01", "XY13"):
        add(bid, "lat", b["lat"], "S850;S01", "on the ruin, research/xiyanglou/boxes.csv", b["basis"], "B", "correct", "The row stood off the ruin")
        add(bid, "lon", b["lon"], "S850;S01", "on the ruin, research/xiyanglou/boxes.csv", b["basis"], "B", "correct", "The row stood off the ruin")
for bid, lat, lon, why in (("XY04", "40.012455", "116.302242", "Rebuilt maze, measured"), ("XY02", "40.011819", "116.301918", "Plan's offset interpolated, err 15 m"), ("XY11", "40.011836", "116.306679", "On OSM's point")):
    add(bid, "lat", lat, "S850;S01", why, why, "B")
    add(bid, "lon", lon, "S850;S01", why, why, "B")
add("XY12", "frontage_m", "41.7", "S01", "plan's outer ring, local scale", "191-197 px", "C", "correct", "No size recorded")
add("XY12", "depth_m", "41.7", "S01", "plan's outer ring, local scale", "191-197 px", "C", "correct", "No size recorded")
add("XY14", "frontage_m", "145.9", "S01;S03", "W-E plan 145.9 m, OSM 149.2 m", "Plan and OSM agree", "B", "correct", "No size recorded")
add("XY14", "depth_m", "51.9", "S01;S03", "N-S plan; today's bank is 7 m inside it on the north", "Plan", "B", "correct", "No size recorded")
add("XY08", "built", "乾隆二十四年 (1759) basically finished, known as 水法殿十一间楼; the board 海晏堂 hung only from 四十六年 (1781)", "S310", "mhymy /dasl/ysltd/12168", "As stated; archive not named on the page", "B", "apply")
for p in parts:
    act = p["action"]
    if p["name_en"]:
        add(p["id"], "name_en", p["name_en"], p["source_id"], "", p["basis"], p["confidence"], "apply", "")
    if p["name_zh"] and act == "name" and p["id"] == "XY08-N01":
        add(p["id"], "name_zh", "西水车房 Xi Shuiche Fang", p["source_id"], "", p["basis"], p["confidence"], "name", "The plan's third character reads like 車")
    if act.startswith("merge:"):
        add(p["id"], "name_en", f"Part of {act[6:]}: {p['what']}", p["source_id"], "Round 6", p["basis"], p["confidence"], "note", "Merged: no box of its own")
    elif act == "retire":
        add(p["id"], "name_en", f"Retired in Round 6, no box: {p['what']}", p["source_id"], "Round 6", p["basis"], p["confidence"], "note", "Not a building")
    elif act == "keep" and p["what"]:
        add(p["id"], "name_en", p["what"], p["source_id"], "Round 6", p["basis"], p["confidence"], "note", "A building stood here, name unknown")
with open(ROOT / "research/evidence/facts.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
print(len(rows), "facts")
