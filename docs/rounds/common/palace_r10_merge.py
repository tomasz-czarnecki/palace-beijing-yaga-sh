"""Round 10: merge the five workers' rows (scratch) into research/terrain/readings.csv. A record, not a pipeline step: readings.csv is hand-edited from here on.

  uv run python docs/rounds/common/palace_r10_merge.py

Each row gets an id R10-###, the worker, and the S-ids of its source (existing ids where the source is already in research/sources.md, S1000+ for the new ones, listed there).
Grades: the workers graded pre-1860 texts A; the repo grades a written description only B (research/paths/texts.csv, CLAUDE.md "Confidence"), so text rows graded A become B. Album rows keep A for what a leaf shows (a hill, a shore's kind) and C for a height read by module.
"""

import csv
from pathlib import Path

SCRATCH = Path("/opt/data/cache/scratch")
OUT = Path(__file__).resolve().parents[3] / "research/terrain/readings.csv"
WORKERS = ["hills_survey", "hills_texts", "water", "album_a", "album_b"]
# Substring of the worker's source title (or URL) -> S-id. First match wins.
SOURCES = [
    ("日下", "S05"), ("KR2k0036", "S05"), ("四十景", "S08"), ("Forty Scenes", "S08"), ("gallica.bnf.fr", "S08"),
    ("御制诗文集注", "S361"), ("御製詩文集注", "S361"), ("Attiret", "S911"), ("Wolseley", "S240"), ("Swinhoe", "S241"), ("M'Ghee", "S242"),
    ("Hérisson", "S246"), ("Malone", "S02"), ("Copernicus", "S04"), ("node 494772255", "S03"), ("node 10895631007", "S03"), ("Overpass", "S03"),
    ("S944", "S944"), ("响水", "S944"), ("1933", "S15"), ("S220", "S220"), ("S316", "S316"), ("S155", "S155"), ("S133", "S133"), ("S362", "S362"), ("S360", "S360"),
    ("= S146", "S146"), ("FABDEM", "S158"),
    ("线法山, scene page", "S1000"), ("China Daily", "S1001"), ("圆明园研究 11", "S1002"), ("贾贯峰", "S1003"), ("国家环保总局", "S1004"), ("燕赵都市报", "S1005"),
    ("陈名杰", "S1006"), ("秦静", "S1007"), ("名城办发", "S1008"), ("清华同衡", "S1009"), ("王其亨", "S1010"), ("杨茂艺", "S1011"), ("央视", "S1012"),
    ("OpenTopography", "S1013"), ("ICESat-2", "S1014"), ("Wikipedia zh", "S1015"), ("TanDEM-X", "S1016"), ("AW3D30", "S1016"),
]


def sid(row):
    t = row["source_title"] + " " + row["source_url"]
    for key, s in SOURCES:
        if key in t:
            return s
    return ""


def main():
    out = []
    for w in WORKERS:
        for r in csv.DictReader(open(SCRATCH / f"palace_r10_ground_notes_{w}.csv", encoding="utf-8", newline="")):
            g = r["grade"]
            if r["method"] == "text" and g == "A":
                g = "B"
            out.append({"id": f"R10-{len(out) + 1:03d}", "worker": w, "kind": r["kind"], "ref": r["ref"], "scene_id": r["scene_id"], "name_zh": r["name_zh"], "where": r["where"],
                        "lat": r["lat"], "lon": r["lon"], "value_m": r["value_m"], "value_text": r["value_text"], "conversion": r["conversion"], "method": r["method"],
                        "error_m": r["error_m"], "state_date": r["state_date"], "sources": sid(r), "source_title": r["source_title"], "source_url": r["source_url"], "page": r["page"],
                        "grade": g, "verified": r["verified"], "note": r["note"]})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    missing = [r["id"] for r in out if not r["sources"] and r["kind"] != "none_found"]
    print(f"{len(out)} rows -> {OUT}; rows with no S-id: {len(missing)} {missing[:20]}")


if __name__ == "__main__":
    main()
