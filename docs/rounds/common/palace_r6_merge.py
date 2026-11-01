"""Round 6: merges the workers' JSON lines into the catalogues. A record of how they were made, not a pipeline step: once merged, the catalogues and research/xiyanglou/*.csv are edited by hand.

  uv run python docs/rounds/common/palace_r6_merge.py

Starts from the committed catalogues (git show HEAD), so a rerun gives the same result. Reads /opt/data/cache/scratch/palace_r6_out_*.jsonl and palace_r6_images/.
"""

import csv
import io
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
S = Path("/opt/data/cache/scratch")
OUT = ROOT / "research/xiyanglou"
BASE_COMMIT = "3fa83a0"
TOPICS = ["plates", "surveys", "ruinphotos", "fragments", "views", "perspective", "footprints", "wave2"]
csv.field_size_limit(10**9)


def rows_of(topic):
    f = S / f"palace_r6_out_{topic}.jsonl"
    return [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()] if f.exists() else []


ALL = {t: rows_of(t) for t in TOPICS}
# Coordinator's rulings on wave 2. Fig. 13 of Teng Gu is by 周纘武, dates unknown, about 1930: the book's PD tag is not enough, so a link card (Q50).
for r in ALL["wave2"]:
    if r.get("type") == "picture" and "fig13" in r.get("file", ""):
        r["rights_class"] = "research-only"
        r["notes"] = f"{r.get('notes', '')} Photograph by 周纘武 about 1930, dates unknown; the Commons tag covers the whole book, so kept research-only (Q50).".strip()
# The worker's row on 观水法 said the throne base is gone; S603 p.129 says the platform stands, without balustrades.
FIXES = {"The brick backing and throne base gone.": "The brick backing is gone; the throne platform stands without its balustrades (S603 p.129)."}


def of_type(kind, topics=TOPICS):
    return [dict(r, _topic=t) for t in topics for r in ALL[t] if r.get("type") == kind]


def base_csv(path):
    text = subprocess.run(["git", "show", f"{BASE_COMMIT}:{path}"], cwd=ROOT, capture_output=True, check=True).stdout.decode("utf-8")
    r = csv.DictReader(io.StringIO(text, newline=""))
    return r.fieldnames, list(r)


def write_csv(path, fields, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


known_ids = {r["id"] for r in csv.DictReader(open(ROOT / "research/buildings.csv", encoding="utf-8", newline=""))}


def valid_shows(text):
    out = []
    for item in re.split(r"[;]\s*", text or ""):
        item = item.strip()
        if not item:
            continue
        bits = item.split(":")
        if bits[0] == "GARDEN" or bits[0] in known_ids:
            out.append(item)
        else:
            print("  dropped tie", item)
    return ";".join(out)


# ---- pictures
fields, photos = base_csv("research/photos/catalog.csv")
by_pid = {p["photo_id"]: p for p in photos}
next_p = max(int(p["photo_id"][1:]) for p in photos) + 1
slug_to_pid = {}
new_pics = [r for r in of_type("picture") if r.get("plate") in (0, None, "") or r["_topic"] != "plates"]
impressions = [r for r in of_type("picture", ["plates"]) if r not in new_pics]
impressions = [r for t in ["plates"] for r in ALL[t] if r.get("type") == "picture"]  # every impression stays in plates; the panel keeps P0041-60, P0222-24
new_pics = [r for r in of_type("picture") if r["_topic"] != "plates"]
existing_urls = {p["source_url"]: p["photo_id"] for p in photos}
GARDEN_LOOKS = {"fragments_vam_C382": True}
for r in new_pics:
    slug = Path(r.get("file") or r.get("archive_id") or r["title"]).stem
    if r["source_url"] in existing_urls:
        slug_to_pid[slug] = existing_urls[r["source_url"]]
        print("  already catalogued:", slug, existing_urls[r["source_url"]])
        continue
    pid = f"P{next_p:04d}"
    next_p += 1
    slug_to_pid[slug] = pid
    row = {k: "" for k in fields}
    for k in ("title", "date", "kind", "creator", "archive", "archive_id", "source_id", "source_url", "licence", "attribution", "rights_class", "why", "also_shows", "camera_lat", "camera_lon", "bearing", "camera_note", "notes"):
        row[k] = str(r.get(k) or "")
    row["photo_id"], row["date_from"], row["date_to"], row["relation"] = pid, str(r.get("date_from") or ""), str(r.get("date_to") or ""), "self"
    row["shows"] = ";".join(x for x in valid_shows(r.get("shows")).split(";") if x and not x.startswith("GARDEN"))
    if not row["shows"] and "GARDEN" not in row["also_shows"]:
        row["also_shows"] = "GARDEN:XY"
    if r["rights_class"] == "free":
        src = S / "palace_r6_images/ruinphotos_1280" / f"{slug}.jpg"
        if not src.exists() or r["_topic"] == "wave2" and "ruinphotos_1280" not in r.get("file", ""):
            src = Path(r["file"]) if r.get("file") else src
            if src.exists():
                print("  no 1280 px copy:", slug, Image.open(src).size)
        if src.exists():
            dest = ROOT / f"research/photos/images/{pid}.jpg"
            im = Image.open(src).convert("RGB")
            if max(im.size) > 1600:
                im.thumbnail((1600, 1600))
            im.save(dest, quality=82, optimize=True)
            row["file"], row["width"], row["height"] = f"research/photos/images/{pid}.jpg", im.width, im.height
    elif r.get("file") and Path(r["file"]).exists():
        dest = ROOT / f"research/raw/photos/{pid}.jpg"
        shutil.copy(r["file"], dest)
        im = Image.open(dest)
        row["file"], row["width"], row["height"] = f"research/raw/photos/{pid}.jpg", im.width, im.height
    photos.append(row)
    by_pid[pid] = row

# the plates: same Commons files, larger. 2400 px in git, the full size in raw/
(ROOT / "research/raw/plates").mkdir(parents=True, exist_ok=True)
for n in range(1, 21):
    pid = f"P{40 + n:04d}"
    src = S / f"palace_r6_images/plates/plate_{n:02d}_palacemuseum.jpg"
    if src.exists():
        im = Image.open(src)
        shutil.copy(src, ROOT / f"research/photos/images/{pid}.jpg")
        by_pid[pid].update(width=im.width, height=im.height, file=f"research/photos/images/{pid}.jpg")
        full = S / f"palace_r6_images/full/plate_{n:02d}_palacemuseum.jpg"
        if full.exists():
            shutil.copy(full, ROOT / f"research/raw/plates/plate_{n:02d}_palacemuseum.jpg")
src = S / "palace_r6_images/plates/plate_01_chesterbeatty.jpg"
if src.exists():
    im = Image.open(src)
    shutil.copy(src, ROOT / "research/photos/images/P0223.jpg")
    by_pid["P0223"].update(width=im.width, height=im.height, file="research/photos/images/P0223.jpg")
    full = S / "palace_r6_images/full/plate_01_chesterbeatty.jpg"
    if full.exists():
        shutil.copy(full, ROOT / "research/raw/plates/plate_01_chesterbeatty.jpg")

WHY = {
    "P0218": "South front, read from the sun and the low brick near end: plates 11 and 13 are mirror elevations, so the bays decide nothing.",
    "P0219": "South front, the same front as P0218 by its doors and dormer: plates 11 and 13 are mirror elevations, so the bays decide nothing.",
    "P0324": "The same front as the captioned 004536, so the south front; read from the catalogue, not seen.",
}
for c in of_type("correction", ["views", "ruinphotos", "wave2"]):
    p = by_pid.get(c["photo_id"])
    if not p:
        print("  correction for an unknown picture", c["photo_id"])
        continue
    field, new, reason = c["field"], str(c["new"]), c["reason"]
    if field == "shows":
        if new.startswith("add from"):
            p["notes"] = f"{p['notes']} {new}".strip()
        elif new.startswith("add "):
            p["shows"] = valid_shows(p["shows"] + ";" + new[4:])
        else:
            p["shows"] = valid_shows(new)
        if not new.startswith("add from"):
            p["why"] = f"{p['why']} {reason}".strip()
    elif field == "bearing":
        p["bearing"] = new
        p["notes"] = f"{p['notes']} {reason}".strip()
    elif field == "camera_note":
        p["camera_note"] = new
    elif field == "why":
        p["why"] = WHY[c["photo_id"]]
    elif field == "title":
        p["notes"] = f"{p['notes']} {reason}".strip()
    elif field == "file":
        p["notes"] = f"{p['notes']} {reason}".strip()
    else:
        p["notes"] = f"{p['notes']} {new}: {reason}".strip()
for c in of_type("correction", ["plates"]):
    if c["field"] == "source_url/notes" or c["field"] == "notes/licence/date":
        by_pid[c["photo_id"]]["notes"] = f"{by_pid[c['photo_id']]['notes']} {c['new']}".strip()
by_pid["P0224"]["date"] = "1783-1786 (V&A)"
photos.sort(key=lambda p: int(p["photo_id"][1:]))
write_csv(ROOT / "research/photos/catalog.csv", fields, photos)
print(f"pictures: {len(photos)}, new {sum(1 for p in photos if int(p['photo_id'][1:]) >= 720)}")

# ---- views
VIEW_FIELDS = ["photo_id", "id", "side", "visible_part", "state", "reliability", "camera_lat", "camera_lon", "bearing", "camera_note", "note"]
views, seen = [], set()
for v in of_type("view", ["ruinphotos", "views", "fragments", "wave2"]):
    pid = slug_to_pid.get(v["photo_id"], v["photo_id"])
    if pid not in by_pid or v["id"] not in known_ids:
        print("  view dropped:", v["photo_id"], v["id"])
        continue
    if (pid, v["id"]) in seen:
        continue
    seen.add((pid, v["id"]))
    views.append({**{k: v.get(k, "") for k in VIEW_FIELDS}, "photo_id": pid})
for r in new_pics:
    slug = Path(r.get("file") or r.get("archive_id") or r["title"]).stem
    pid = slug_to_pid[slug]
    for item in re.split(r";\s*", r.get("shows") or ""):
        bid = item.split(":")[0].strip()
        if bid in known_ids and (pid, bid) not in seen:
            seen.add((pid, bid))
            views.append({"photo_id": pid, "id": bid, "side": r.get("side", ""), "visible_part": r.get("visible_part", ""), "state": r.get("state", ""), "reliability": r.get("reliability", ""), "camera_lat": r.get("camera_lat", ""), "camera_lon": r.get("camera_lon", ""), "bearing": r.get("bearing", ""), "camera_note": r.get("camera_note", ""), "note": ""})
views.sort(key=lambda v: (v["id"], v["photo_id"]))
write_csv(OUT / "views.csv", VIEW_FIELDS, views)
print("views", len(views))

# ---- dimensions
DIM_FIELDS = ["id", "part", "what", "value_m", "err_m", "method", "confidence", "source_id", "locator", "basis", "status"]
dims = []
for d in of_type("dim"):
    loc = str(d.get("locator") or "")
    if "palace_r6" in loc or "/opt/" in loc:
        loc = re.sub(r"\S*palace_r6\S*", "", loc).strip(" ;,") or ("plates 1 and 2" if d["id"] == "XY01" else "script")
    row = {k: d.get(k, "") for k in DIM_FIELDS}
    row["locator"] = loc
    row["basis"] = re.sub(r"/opt/data/\S+", "", str(d.get("basis") or ""))
    if d["id"] != "GARDEN:XY" and d["id"] not in known_ids:
        print("  dim dropped:", d["id"])
        continue
    dims.append(row)
order = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4}
dims.sort(key=lambda d: (d["id"], d["part"], d["what"], order.get(d["method"], 9)))
write_csv(OUT / "dimensions.csv", DIM_FIELDS, dims)
print("dims", len(dims))

# ---- the small catalogues
write_csv(OUT / "fragments.csv", ["id", "what", "material", "from_where_stated", "now_at", "now_place_zh", "moved", "status_today", "source_id", "locator", "link", "confidence", "web_status", "note"], of_type("fragment"))
write_csv(OUT / "materials.csv", ["id", "part", "what", "colour", "source_id", "locator", "quote_or_basis", "confidence", "status"], of_type("material"))
facts_out = of_type("fact")
for f in facts_out + of_type("fragment"):
    for a, b in FIXES.items():
        for k in ("value", "status_today", "note"):
            if a in str(f.get(k, "")):
                f[k] = f[k].replace(a, b)
write_csv(OUT / "facts.csv", ["id", "field", "value", "source_id", "locator", "quote_or_basis", "suggest_confidence", "status"], facts_out)
write_csv(OUT / "parts.csv", ["id", "name_zh", "name_pinyin", "name_en", "what", "basis", "source_id", "confidence", "action"], of_type("part"))
write_csv(OUT / "best.csv", ["id", "rank", "photo_id", "why"], of_type("best"))
write_csv(OUT / "viewpoints.csv", ["plate", "photo_id", "id", "lat", "lon", "bearing", "dist_m", "err_m", "basis"], of_type("viewpoint"))
rephotos = []
for r in of_type("rephoto"):
    resolve = lambda k: slug_to_pid.get(k) or next((v for s, v in slug_to_pid.items() if s.startswith(k + "_")), k)
    old, new = resolve(r["old"]), resolve(r["new"])
    if old not in by_pid or new not in by_pid:
        print("  rephoto dropped:", r["old"], r["new"])
        continue
    rephotos.append({"id": r["id"], "old": old, "new": new, "same_view": r["same_view"], "what_changed": r["what_changed"], "note": r.get("note", "")})
write_csv(OUT / "rephoto.csv", ["id", "old", "new", "same_view", "what_changed", "note"], rephotos)
print("rephoto", len(rephotos))
IMP_FIELDS = ["plate", "title", "date", "creator", "archive", "archive_id", "source_id", "source_url", "licence", "attribution", "rights_class", "width", "height", "notes"]
imp = sorted(impressions, key=lambda r: (int(r.get("plate") or 0), r.get("archive", "")))
write_csv(OUT / "impressions.csv", IMP_FIELDS, imp)
print("impressions", len(imp))

# ---- evidence
efields, ev = base_csv("research/evidence/catalog.csv")
next_e = max(int(e["evidence_id"][1:]) for e in ev) + 1
for e in of_type("evidence"):
    row = {k: str(e.get(k) or "") for k in efields}
    row["evidence_id"] = f"E{next_e}"
    next_e += 1
    row["shows"] = valid_shows(e.get("shows")) or "GARDEN:XY:likely"
    if row["rights_class"] != "free":
        row["excerpt_zh"] = row["excerpt_other"] = ""
    ev.append(row)
write_csv(ROOT / "research/evidence/catalog.csv", efields, ev)
print("evidence", len(ev))

# ---- sources
text = subprocess.run(["git", "show", f"{BASE_COMMIT}:research/sources.md"], cwd=ROOT, capture_output=True, check=True).stdout.decode("utf-8").rstrip("\n")
lines = ["", "", "## Round 6: the Xiyang Lou (S700-S729 the plates, S730-S769 surveys, S770-S809 ruin photographs, S810-S849 fragments, texts and materials, S850-S869 footprints, S870-S899 the second wave)", "", "| ID | Source | Year | Reuse | Status | Link / note |", "|---|---|---|---|---|---|"]
seen_s = set()
for s in sorted(of_type("source"), key=lambda s: s["id"]):
    if s["id"] in seen_s or re.search(rf"^\| {s['id']} \|", text, flags=re.M):
        continue
    seen_s.add(s["id"])
    clean = lambda v: re.sub(r"\s+", " ", str(v or "")).replace("|", "/")
    lines.append(f"| {s['id']} | {clean(s['text'])} | {clean(s['year'])} | {clean(s['reuse'])} | {clean(s['status'])} | {clean(s['link'])}{'. ' + clean(s['note']) if s.get('note') else ''} |")
(ROOT / "research/sources.md").write_text(text + "\n".join(lines) + "\n", encoding="utf-8")
print("sources", len(seen_s))
json.dump(slug_to_pid, open(S / "palace_r6_idmap.json", "w"), ensure_ascii=False, indent=0)
