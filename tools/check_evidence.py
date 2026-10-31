"""Every clickable object shows real evidence in its panel. Prints the coverage, with reconstructions and comparables before and after Round 5, and fails on an empty evidence section, a research-only image or file on the site, or a row of research/reconstructions/catalog.csv or research/twins/catalog.csv with no link or licence.

  uv run python tools/check_evidence.py

Reads what the panel reads: site/reconstruction/data/buildings/<ID>.json. "Own" counts what is tied to the object itself; "inherited" counts its own or what reaches it through `fallback` (compound, garden, class of hall). A plan reference is evidence too, and is counted apart, because it is the weakest kind. "Before" comes from research/evidence/coverage_before_r5.json, measured at commit 5fbd637.
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


def evidence_fallback(page):
    """A `refs_only` entry brings reconstructions and comparables, not evidence."""
    return [f for f in page["fallback"] if not f.get("refs_only")]


def free_image(page):
    return any(p.get("image") and not p.get("link_only") for p in page["photos"] + page.get("reconstructions", []) + [x for t in page.get("twins", []) for x in t["photos"]])


def has_recon(page):
    return bool(page.get("reconstructions"))


def has_twin_photo(page):
    return any(x.get("image") and not x.get("link_only") for t in page.get("twins", []) for x in t["photos"])


def coverage(ids):
    n = dict(objects=len(ids), free_image_own=0, free_image_inherited=0, reconstruction_own=0, reconstruction_inherited=0, twin_photo_own=0, twin_photo_inherited=0, twin_row_own=0)
    for pid in ids:
        page = load(pid)
        others = [load(f["id"]) for f in page["fallback"]]
        for key, test in (("free_image", free_image), ("reconstruction", has_recon), ("twin_photo", has_twin_photo)):
            n[f"{key}_own"] += test(page)
            n[f"{key}_inherited"] += test(page) or any(test(x) for x in others)
        n["twin_row_own"] += bool(page.get("twins"))
    return n


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
                elif evidence_fallback(page) and all(has_evidence(load(f["id"])) for f in evidence_fallback(page)):
                    n["fallback only"] += 1
                else:
                    n["nothing"] += 1
                    problems.append(f"{pid}: an empty evidence section")
            for f in evidence_fallback(page):
                if not has_evidence(load(f["id"])):
                    problems.append(f"{pid}: its fallback {f['id']} is empty")
            if not (pic or card or text or plan or evidence_fallback(page)):
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
    before = json.load(open(ROOT / "research/evidence/coverage_before_r5.json", encoding="utf-8"))["counts"]
    for name, key, ids in (("Top level", "top", top_ids), ("Halls", "halls", hall_ids)):
        now, old = coverage(sorted(ids)), before[key]
        print(f"{name}, before -> now: free image own {old['free_image_own']} -> {now['free_image_own']}, inherited {old['free_image_inherited']} -> {now['free_image_inherited']}; reconstruction own {old['reconstruction_own']} -> {now['reconstruction_own']}, inherited {old['reconstruction_inherited']} -> {now['reconstruction_inherited']}; twin or comparable photo own {old['twin_photo_own']} -> {now['twin_photo_own']}, inherited {old['twin_photo_inherited']} -> {now['twin_photo_inherited']}; twin pairing own {now['twin_row_own']}")

    # no research-only image or path on the site
    catalog = list(csv.DictReader(open(ROOT / "research/photos/catalog.csv", encoding="utf-8", newline="")))
    for r in catalog:
        pid = r["photo_id"]
        if r["rights_class"] != "free":
            for f in (SITE / "reconstruction/photos" / f"{pid}.jpg", SITE / "reconstruction/photos" / f"{pid}_t.jpg", ROOT / "research/photos/images" / f"{pid}.jpg"):
                if f.exists():
                    problems.append(f"{f}: research-only file in a public place")
    bad = {r["photo_id"] for r in catalog if r["rights_class"] != "free"}

    recons = list(csv.DictReader(open(ROOT / "research/reconstructions/catalog.csv", encoding="utf-8", newline="")))
    twins = list(csv.DictReader(open(ROOT / "research/twins/catalog.csv", encoding="utf-8", newline="")))
    bad_recon = {r["recon_id"] for r in recons if r["rights_class"] != "free"}
    on_site = {f.stem for f in SITE.rglob("*.jpg")} | {f.stem.removesuffix("_t") for f in SITE.rglob("*_t.jpg")}
    for rid in sorted(bad_recon & on_site):
        problems.append(f"{rid}: research-only file under site/")
    for rid in sorted(bad):
        if rid in on_site:
            problems.append(f"{rid}: research-only file under site/")
    for f in (ROOT / "research/reconstructions/images").glob("*.jpg"):
        if f.stem in bad_recon:
            problems.append(f"{f}: research-only file in a public place")
    for r in recons:
        if not r["link"].startswith("http") or not r["licence"]:
            problems.append(f"{r['recon_id']}: no link or no licence")
        if r["local_copy"] and not (ROOT / r["local_copy"]).exists() and r["rights_class"] == "free":
            problems.append(f"{r['recon_id']}: {r['local_copy']} is missing")
        if r["rights_class"] == "free" and r["local_copy"] and not r["attribution"]:
            problems.append(f"{r['recon_id']}: free with no credit")
        if r["rights_class"] != "free" and r["local_copy"] and not r["local_copy"].startswith("research/raw/"):
            problems.append(f"{r['recon_id']}: research-only copy outside research/raw/")
    twin_ids = {t["twin_id"] for t in twins}
    for t in twins:
        if not t["link"].startswith("http") or not t["licence"]:
            problems.append(f"{t['twin_id']}: no link or no licence")
    for r in catalog:
        if r["relation"].startswith("twin:"):
            for tid in r["relation"][5:].split(";"):
                if tid not in twin_ids:
                    problems.append(f"{r['photo_id']}: {tid} is not in the twin catalogue")
        elif r["relation"] != "self":
            problems.append(f"{r['photo_id']}: relation {r['relation']}")
    for page_file in PUBLIC.glob("*.json"):
        text = page_file.read_text(encoding="utf-8")
        if "research/raw" in text or "/_local/" in text:
            problems.append(f"{page_file.name}: a research path")
        page = json.loads(text)
        for p in page.get("reconstructions", []):
            if p["id"] in bad_recon and (p.get("image") or p.get("thumb") or not p.get("link_only")):
                problems.append(f"{page_file.name}: {p['id']} is research-only and shows an image")
            for key in ("image", "thumb"):
                if p.get(key) and not (SITE / "reconstruction" / p[key]).exists():
                    problems.append(f"{page_file.name}: {p[key]} is missing")
        for p in page.get("photos", []) + page.get("photos_inside", []) + [x for t in page.get("twins", []) for x in t["photos"]]:
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
    shown_recon = len(list((SITE / "reconstruction/photos").glob("R????.jpg")))
    evidence = list(csv.DictReader(open(ROOT / "research/evidence/catalog.csv", encoding="utf-8", newline="")))
    print(f"Pictures: {len(catalog)} in the catalog, {free} free, {len(catalog) - free} link-only; {shown} on the site. Evidence rows: {len(evidence)}, free {sum(e['rights_class'] == 'free' for e in evidence)}, link-only {sum(e['rights_class'] != 'free' for e in evidence)}, seen only in a search index {sum(e['status'] != 'viewed' for e in evidence)}.")
    who = {}
    for r in recons:
        who[r["kind"]] = who.get(r["kind"], 0) + 1
    print(f"Reconstructions: {len(recons)}, free {sum(r['rights_class'] == 'free' for r in recons)}, {shown_recon} on the site, with a local copy {sum(bool(r['local_copy']) for r in recons)}, kept off the panels {sum(not r['shows'] for r in recons)}; by kind {dict(sorted(who.items()))}.")
    print(f"Twins: {len(twins)} pairings on {len({t['object_id'] for t in twins})} objects or classes; with a picture {len({tid for r in catalog if r['relation'].startswith('twin:') for tid in r['relation'][5:].split(';')})}; pictures {sum(r['relation'].startswith('twin:') for r in catalog)}.")
    for p in problems[:40]:
        print("FAIL", p)
    if len(problems) > 40:
        print(f"... and {len(problems) - 40} more")
    print("OK" if not problems else f"{len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
