"""Round 9, a record, not a pipeline step: how research/paths/traces.csv, album.csv, texts.csv and remains.csv were first made from the workers' scratch files.

  uv run python docs/rounds/common/palace_r9_merge.py

From then on the four sheets are hand-edited. What it did:
- the five plan readers' traces (ymc, ymw, ymf, ccx, qc) into one sheet, in that order, with a `region` column;
- `leaf`: the album rows (Forty Scenes, 1744, P0001-P0040; the Xiyang Lou plates, P0041-P0060) that show the same piece:
  same scene, the same kind group, at least one end id in common, reading high or medium. A trace with a leaf is
  graded A by scripts/paths1860.py (drawn on a period picture); its position stays the plan's (B);
- the album, texts and remains sheets copied as they were written, with the workers' status column kept.
"""

import csv
from pathlib import Path

SCRATCH = Path("/opt/data/cache/scratch")
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "research/paths"
REGIONS = ["ymc", "ymw", "ymf", "ccx", "qc"]
GROUP = {"paved_way": "way", "courtyard_path": "way", "imperial_road": "way", "service_path": "way", "gallery": "gallery", "mountain_gallery": "gallery",
         "steps": "steps", "landing": "landing", "dock": "landing", "dike": "dike", "causeway": "dike", "bridge_approach": "approach", "boat_route": "boat", "boat": "boat"}


def rows(p):
    return list(csv.DictReader(open(p, encoding="utf-8", newline="")))


def main():
    album = rows(SCRATCH / "palace_r9_album.csv")
    traces = []
    for reg in REGIONS:
        for r in rows(SCRATCH / f"palace_r9_traces_{reg}.csv"):
            r["region"] = reg
            traces.append(r)
    for t in traces:
        ends = {t["from_id"].strip(), t["to_id"].strip()} - {""}
        hits = []
        for a in album:
            if a["reading"] not in ("high", "medium") or a["scene"] != t["scene"] or GROUP.get(a["kind"]) != GROUP.get(t["kind"]):
                continue
            if ends & ({a["from_id"].strip(), a["to_id"].strip()} - {""}):
                hits.append(a["key"])
        t["leaf"] = ";".join(hits)
        t["evidence"] = ""
    cols = ["key", "region", "scene", "kind", "name_zh", "from_id", "to_id", "points_px", "in_box_row", "water", "drawn_on_s01", "confidence", "leaf", "evidence", "width_m", "sources", "note"]
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "traces.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(traces)
    for name in ("album", "texts", "remains"):
        src = rows(SCRATCH / f"palace_r9_{name}.csv")
        with open(OUT / f"{name}.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(src[0].keys()))
            w.writeheader()
            w.writerows(src)
    print(len(traces), "traces,", sum(1 for t in traces if t["leaf"]), "with a leaf;", len(album), "album rows")


if __name__ == "__main__":
    main()
