"""Every clickable object shows real evidence in its panel. Prints the coverage and fails on an empty evidence section, or a research-only image on the site.

  uv run python tools/check_evidence.py

Reads what the panel reads: site/reconstruction/data/buildings/<ID>.json. "Own" counts what is tied to the object itself. A plan reference is evidence too, and is counted apart, because it is the weakest kind.
"""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "site/reconstruction/data"
PUBLIC = DATA / "buildings"
SITE = ROOT / "site"


def load(pid, cache={}):
    if pid not in cache:
        cache[pid] = json.load(open(PUBLIC / f"{pid}.json", encoding="utf-8"))
    return cache[pid]


def has_evidence(page):
    return bool(page.get("photos") or page.get("evidence") or page.get("plan_ref"))


def main():
    problems = []
    rows = list(csv.DictReader(open(ROOT / "research/buildings.csv", encoding="utf-8", newline="")))
    fc = json.load(open(DATA / "halls_1860.geojson", encoding="utf-8"))
    clickable = {f["properties"]["building_id"] for f in fc["features"]} | {a for f in fc["features"] for a in f["properties"].get("also", [])} | set(fc.get("shared_rows", {}))
    pages = {p.stem for p in PUBLIC.glob("*.json") if not p.stem.startswith("GARDEN-")}
    for pid in sorted(clickable - pages):
        problems.append(f"{pid}: clickable, no page")
    top_ids = {r["id"] for r in rows if not r["parent_id"]}
    hall_ids = {r["id"] for r in rows if r["parent_id"]}
    gate_ids = {p for p in pages if p.startswith("G") and not p.startswith("GARDEN")}

    def own_kinds(page):
        pictures = [p for p in page["photos"] if not p.get("link_only")]
        cards = [p for p in page["photos"] if p.get("link_only")]
        return bool(pictures), bool(cards), bool(page["evidence"]), bool(page.get("plan_ref"))

    def report(name, ids):
        n = {"picture": 0, "firm": 0, "card": 0, "text": 0, "plan only": 0, "fallback only": 0, "nothing": 0}
        for pid in sorted(ids):
            page = load(pid)
            pic, card, text, plan = own_kinds(page)
            n["picture"] += pic
            n["firm"] += any(not p.get("link_only") and p["conf"] != "guess" for p in page["photos"])
            n["card"] += card and not pic
            n["text"] += text
            if not (pic or card or text):
                if plan:
                    n["plan only"] += 1
                elif page["fallback"] and all(has_evidence(load(f["id"])) for f in page["fallback"]):
                    n["fallback only"] += 1
                else:
                    n["nothing"] += 1
                    problems.append(f"{pid}: an empty evidence section")
            for f in page["fallback"]:
                if not has_evidence(load(f["id"])):
                    problems.append(f"{pid}: its fallback {f['id']} is empty")
            if not (pic or card or text or plan or page["fallback"]):
                problems.append(f"{pid}: nothing at all")
        print(f"{name} ({len(ids)}): own picture {n['picture']} ({n['firm']} not only a guess); link card only {n['card']}; own text or drawing {n['text']}; only the plan and the fallback {n['plan only']}; only the fallback {n['fallback only']}; nothing {n['nothing']}")
        return n

    report("Top level", top_ids)
    named = {r["id"] for r in rows if r["parent_id"] and (r["name_zh"] or r["name_on_plan"])}
    report("Halls", hall_ids)
    report("Named halls", named)
    report("Gates", gate_ids)
    with_own_any = sum(1 for p in hall_ids if any(own_kinds(load(p))[:3]))
    print(f"Halls with evidence of their own {with_own_any}; parent fallback and plan only {len(hall_ids) - with_own_any}")
    print(f"Clickable objects {len(clickable)}; every one of them has a page: {not (clickable - pages)}")

    # no research-only image or path on the site
    catalog = list(csv.DictReader(open(ROOT / "research/photos/catalog.csv", encoding="utf-8", newline="")))
    for r in catalog:
        pid = r["photo_id"]
        if r["rights_class"] != "free":
            for f in (SITE / "reconstruction/photos" / f"{pid}.jpg", SITE / "reconstruction/photos" / f"{pid}_t.jpg", ROOT / "research/photos/images" / f"{pid}.jpg"):
                if f.exists():
                    problems.append(f"{f}: research-only file in a public place")
    bad = {r["photo_id"] for r in catalog if r["rights_class"] != "free"}
    for page_file in PUBLIC.glob("*.json"):
        text = page_file.read_text(encoding="utf-8")
        if "research/raw" in text or "/_local/" in text:
            problems.append(f"{page_file.name}: a research path")
        page = json.loads(text)
        for p in page.get("photos", []) + page.get("photos_inside", []):
            if p["id"] in bad and (p.get("image") or p.get("thumb") or not p.get("link_only")):
                problems.append(f"{page_file.name}: {p['id']} is research-only and shows an image")
            for key in ("image", "thumb"):
                if p.get(key) and not (SITE / "reconstruction" / p[key]).exists():
                    problems.append(f"{page_file.name}: {p[key]} is missing")
        for e in page.get("evidence", []):
            if e["rights_class"] != "free" and (e["excerpt_zh"] or e["excerpt_other"]):
                problems.append(f"{page_file.name}: {e['id']} copies a research-only text")
    extern = [f for f in (SITE / "reconstruction/photos").glob("*") if f.suffix != ".jpg"]
    if extern:
        problems.append(f"unexpected files in site/reconstruction/photos: {extern[:3]}")
    free = sum(r["rights_class"] == "free" for r in catalog)
    shown = len(list((SITE / "reconstruction/photos").glob("P????.jpg")))
    evidence = list(csv.DictReader(open(ROOT / "research/evidence/catalog.csv", encoding="utf-8", newline="")))
    print(f"Pictures: {len(catalog)} in the catalog, {free} free, {len(catalog) - free} link-only; {shown} on the site. Evidence rows: {len(evidence)}, free {sum(e['rights_class'] == 'free' for e in evidence)}, link-only {sum(e['rights_class'] != 'free' for e in evidence)}, seen only in a search index {sum(e['status'] != 'viewed' for e in evidence)}.")
    for p in problems[:40]:
        print("FAIL", p)
    if len(problems) > 40:
        print(f"... and {len(problems) - 40} more")
    print("OK" if not problems else f"{len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
