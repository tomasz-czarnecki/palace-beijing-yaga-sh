"""Coordinator: object lists for the workers, and the before-coverage for Round 7."""
import csv, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
ROOT = Path("/opt/data/workspace/000_Dev/palace-beijing-yaga-sh")
S = Path("/opt/data/cache/scratch")
W1 = "YM03 YM01 YM02 YM41 YM32 YM54 YM29 YM46 YM45 YM44 YM15 YM20 YM13 YM09 YM14 YM31 YM39 YM38 YM33".split()
W2 = [f"YM{n:02d}" for n in range(1, 41) if f"YM{n:02d}" not in W1] + "YM47 YM48 YM49 YM50 YM51 YM55".split()
W3 = "CC02 CC14 CC04 CC06 CC13 CC18 CC16 CC15 CC09 CC08 CC10 CC01 CC03 CC05 CC07 CC12 CC17".split()
W4 = "QC04 QC08 QC07 QC05 QC11 QC01 QC02 QC17 QC12 QC13 QC14 QC19 QC06".split()
WAVE = {i: 1 for i in W1} | {i: 2 for i in W2} | {i: 3 for i in W3} | {i: 4 for i in W4}
rd = lambda p: list(csv.DictReader(open(ROOT / p, encoding="utf-8", newline="")))
rows = rd("research/buildings.csv")
ev, ph, rc, tw = rd("research/evidence/catalog.csv"), rd("research/photos/catalog.csv"), rd("research/reconstructions/catalog.csv"), rd("research/twins/catalog.csv")
top = lambda x: x.split(":")[0].split("-")[0]
E, P, R = defaultdict(list), defaultdict(list), defaultdict(list)
for e in ev:
    for s in filter(None, e["shows"].split(";")):
        E[top(s)].append(e)
for p in ph:
    if p["relation"] == "self":
        for s in filter(None, p["shows"].split(";")):
            P[top(s)].append(p)
for r in rc:
    for s in filter(None, r["shows"].split(";")):
        R[top(s)].append(r)
kids = Counter(r["parent_id"] for r in rows if r["parent_id"])
byid = {r["id"]: r for r in rows}
with open(S / "palace_r7_scenes.tsv", "w") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["wave", "id", "name_zh", "pinyin", "name_en", "garden", "type", "lat", "lon", "halls", "evidence_rows", "pictures", "reconstructions", "album_leaf"])
    for i in W1 + W2 + W3 + W4:
        r = byid[i]
        leaf = f"P{int(i[2:]):04d}" if i.startswith("YM") and int(i[2:]) <= 40 else ""
        w.writerow([WAVE[i], i, r["name_zh"], r["name_pinyin"], r["name_en"], r["garden"], r["type"], r["lat"][:9], r["lon"][:10], kids[i], len(E[i]), len({p["photo_id"] for p in P[i]}), len({x["recon_id"] for x in R[i]}), leaf])
cols = ["id", "parent_id", "name_zh", "name_pinyin", "name_on_plan", "read", "type", "hall_class", "bays", "bays_plan", "frontage_m", "depth_m", "size_source", "orientation_deg", "storeys", "roof", "roof_tiles", "lat", "lon", "rel_position"]
with open(S / "palace_r7_halls.tsv", "w") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["wave"] + cols + ["own_evidence", "own_pictures"])
    for r in rows:
        t = r["parent_id"] or r["id"]
        if t in WAVE:
            w.writerow([WAVE[t]] + [r[c][:120].replace("\t", " ").replace("\n", " ") for c in cols] + [len([e for e in ev if any(s.split(":")[0] == r["id"] for s in e["shows"].split(";") if s)]), len([p for p in P[t] if any(s.split(":")[0] == r["id"] for s in p["shows"].split(";") if s)])])
with open(S / "palace_r7_existing_evidence.tsv", "w") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["scene", "evidence_id", "kind", "source_id", "title", "date", "locator", "status", "shows"])
    for i in W1 + W2 + W3 + W4:
        for e in E[i]:
            w.writerow([i, e["evidence_id"], e["kind"], e["source_id"], e["title"][:100], e["date"][:30], e["locator"][:60], e["status"], e["shows"][:120]])
with open(S / "palace_r7_existing_pictures.tsv", "w") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["scene", "photo_id", "kind", "title", "date", "creator", "rights_class", "shows", "file", "source_url"])
    seen = set()
    for i in W1 + W2 + W3 + W4:
        for p in P[i]:
            if (i, p["photo_id"]) in seen:
                continue
            seen.add((i, p["photo_id"]))
            w.writerow([i, p["photo_id"], p["kind"], p["title"][:100], p["date"][:30], p["creator"][:40], p["rights_class"], p["shows"][:120], p["file"], p["source_url"]])
with open(S / "palace_r7_existing_recons.tsv", "w") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["scene", "recon_id", "kind", "author", "institution", "year", "title", "rights_class", "link"])
    for i in W1 + W2 + W3 + W4:
        for r in R[i]:
            w.writerow([i, r["recon_id"], r["kind"], r["author"][:40], r["institution"][:40], r["year"], r["title"][:90], r["rights_class"], r["link"]])
# before-coverage, from the panel JSON at HEAD
pages = ROOT / "site/reconstruction/data/buildings"
out = {"commit": "6b27915", "date": "2026-11-05", "note": "Round 7 before: measured on site/reconstruction/data/buildings at HEAD 6b27915, by the coordinator, before any change.", "scenes": {}}
for i in W1 + W2 + W3 + W4:
    pg = json.load(open(pages / f"{i}.json"))
    hall_ids = [c[0] for c in pg["children"]]
    own = 0
    for h in hall_ids:
        hp = json.load(open(pages / f"{h}.json"))
        own += bool(hp["photos"] or hp["evidence"])
    out["scenes"][i] = {"wave": WAVE[i], "dossier": False, "pictures": len(pg["photos"]), "free_pictures": sum(1 for p in pg["photos"] if not p.get("link_only")), "texts": len(pg["evidence"]), "halls": len(hall_ids), "halls_with_own_evidence": own, "dimension_figures": 0}
allhalls = [r["id"] for r in rows if r["parent_id"]]
n_own = sum(1 for h in allhalls if (lambda hp: bool(hp["photos"] or hp["evidence"]))(json.load(open(pages / f"{h}.json"))))
out["totals"] = {"scenes_with_dossier": 15, "scenes_with_dossier_note": "the 15 Xiyang Lou buildings only", "halls": len(allhalls), "halls_with_own_evidence": n_own, "dimension_figures_by_method": {"a": 29, "b": 183, "c": 164, "d": 23, "e": 31}, "dimension_figures_note": "all on the Xiyang Lou (research/xiyanglou/dimensions.csv, 453 rows, 430 on a building)"}
json.dump(out, open(S / "palace_r7_coverage_before.json", "w"), ensure_ascii=False, indent=1)
print({k: v for k, v in out["totals"].items()}, len(out["scenes"]))
