"""The Xiyang Lou dossiers, one per main building, from the catalogues. Idempotent: a second run changes nothing.

  uv run python scripts/xiyanglou_dossiers.py        (before building_pages.py and xiyanglou_page.py)

Reads research/xiyanglou/: about.json (the text, by hand), views.csv (each picture's side), dimensions.csv (every figure, with its method), boxes.csv (what the 3D boxes take), materials.csv, fragments.csv, rephoto.csv, best.csv, facts.csv, impressions.csv, viewpoints.csv, parts.csv; research/photos/catalog.csv, research/evidence/catalog.csv, research/reconstructions/catalog.csv, research/questions.md, research/wishlist.md.
Writes:
  research/xiyanglou/<ID>-<slug>/README.md       the block between the markers; `## Notes` below it is hand-written and never touched
  research/xiyanglou/<ID>-<slug>/dimensions.json the dimension sheet: `figures` with method and confidence, `model` what the boxes take, `by_method`, public fields only for building_pages.py
  research/xiyanglou/README.md                   the tables between the markers
"""

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
XY = ROOT / "research/xiyanglou"
START = "<!-- generated:start (scripts/xiyanglou_dossiers.py): do not edit between these markers -->"
END = "<!-- generated:end -->"
SIDE_WORD = {"S": "South façade", "N": "North façade", "E": "East façade", "W": "West façade", "roof": "Roof", "fountain": "Fountains", "aerial": "From above", "detail": "Details", "fragment": "Fragments"}
METHOD_WORD = {"a": "a, published survey or measured drawing", "b": "b, measured on the plan or ruin footprint", "c": "c, read from an engraving by perspective", "d": "d, estimated from a ruin photo with a known object", "e": "e, typology, or a figure with no survey behind it"}
WHAT_WORD = {"frontage": "Frontage", "depth": "Depth", "height_cornice": "Cornice height", "height_ridge": "Ridge or top height", "bay_width": "Bay width", "storey_height": "Storey height", "stair_rise": "Stair rise", "stair_width": "Stair width", "terrace_w": "Terrace width", "terrace_d": "Terrace depth", "terrace_h": "Terrace height", "pool_w": "Pool width", "pool_d": "Pool depth (N-S or along)", "pool_depth": "Water depth", "wall_h": "Wall height", "wall_t": "Wall thickness", "diameter": "Diameter"}
UNIT = {"area_ha": "ha", "footprint_m2": "m²", "site_area_m2": "m²", "volume_m3": "m³"}
KEY_WHATS = {"frontage", "depth", "height_cornice", "height_ridge", "terrace_w", "terrace_d", "terrace_h", "pool_w", "pool_d", "wall_h", "diameter"}
METHOD_RANK = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4}


def rd(name):
    with open(XY / name, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def rd_root(path):
    with open(ROOT / path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def top_of(bid):
    return bid.split("-")[0]


def what_label(what):
    if what.startswith("other:"):
        return what[6:].replace("_", " ").capitalize()
    return WHAT_WORD.get(what, what)


def unit_of(what):
    return UNIT.get(what.removeprefix("other:"), "m")


def fig(v):
    return f"{float(v):g}"


def figure_public(d):
    return {"id": d["id"], "part": d["part"], "what": d["what"], "label": what_label(d["what"]), "value": float(d["value_m"]), "err": float(d["err_m"] or 0), "unit": unit_of(d["what"]), "method": d["method"], "confidence": d["confidence"], "source": d["source_id"], "locator": d["locator"], "snippet": d["status"] == "snippet", "key": d["what"] in KEY_WHATS}


def sort_figures(rows):
    return sorted(rows, key=lambda d: (not d["key"], d["id"], d["what"] not in ("frontage", "depth"), METHOD_RANK.get(d["method"], 9), d["part"], d["what"], d["value"]))


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in rows:
        out.append("| " + " | ".join(str(c).replace("|", "/").replace("\n", " ") for c in r) + " |")
    return out


def main():
    about = json.load(open(XY / "about.json", encoding="utf-8"))
    views, dims, boxes = rd("views.csv"), rd("dimensions.csv"), rd("boxes.csv")
    materials, fragments, rephoto, best, facts, impressions, viewpoints = rd("materials.csv"), rd("fragments.csv"), rd("rephoto.csv"), rd("best.csv"), rd("facts.csv"), rd("impressions.csv"), rd("viewpoints.csv")
    photos = {p["photo_id"]: p for p in rd_root("research/photos/catalog.csv")}
    evidence = rd_root("research/evidence/catalog.csv")
    recons = rd_root("research/reconstructions/catalog.csv")
    questions = (ROOT / "research/questions.md").read_text(encoding="utf-8").split("\n## Resolved")[0]
    wishlist = (ROOT / "research/wishlist.md").read_text(encoding="utf-8").splitlines()
    ids = [k for k in about if k.startswith("XY")]
    summary = []
    for bid in ids:
        a = about[bid]
        folder = XY / f"{bid}-{a['slug']}"
        folder.mkdir(exist_ok=True)
        path = folder / "README.md"
        hand = "## Notes\n\n<!-- Yours: regeneration never touches this part. -->\n"
        if path.exists():
            text = path.read_text(encoding="utf-8")
            if END not in text:
                raise SystemExit(f"{path}: markers missing")
            hand = text.split(END, 1)[1].lstrip("\n")
        my_dims = [figure_public(d) for d in dims if top_of(d["id"]) == bid]
        my_dims = sort_figures(my_dims)
        by_method = {m: sum(d["method"] == m for d in my_dims) for m in "abcde"}
        my_boxes = [b for b in boxes if top_of(b["building_id"]) == bid]
        seen, model = set(), []
        for b in my_boxes:
            key = (b["building_id"], b["part"])
            if key in seen:
                continue
            seen.add(key)
            model.append({"id": b["building_id"], "part": b["part"], "frontage": float(b["frontage_m"]), "depth": float(b["depth_m"]), "eave": float(b["eave_m"]), "top": float(b["ridge_m"]), "confidence": b["confidence"], "assumed": b["assumed"] == "yes", "sources": b["sources"]})
        sheet = {"id": bid, "name": f"{a['zh']} {a['pinyin']}", "by_method": by_method, "figures": my_dims, "model": model}
        (folder / "dimensions.json").write_text(json.dumps(sheet, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

        my_views = [v for v in views if top_of(v["id"]) == bid]
        lines = [START, "", f"# {bid}: {a['zh']} {a['pinyin']}, \"{a['en']}\"", "", f"3D: `/reconstruction/3d.html?b={bid}` · Page: `/xiyanglou#{bid}` · Row: `research/buildings/{bid}-{a['slug']}/`", "", "## What it was", "", a["what_en"], "", "## After 1860", "", a["after_en"], ""]
        my_facts = [f for f in facts if top_of(f["id"]) == bid]
        if my_facts:
            lines += ["### Dated facts, as found", ""]
            lines += table(["Row", "Field", "Value", "Source", "Grade", "Seen"], [[f["id"], f["field"], f["value"], f"{f['source_id']} {f['locator']}", f["suggest_confidence"], f["status"]] for f in my_facts]) + [""]
        lines += ["## Evidence by side", "", "State: 1780s engraving, ruin photograph, today, or moved. Reliability says how well it serves a modeller.", ""]
        order = ["S", "N", "E", "W", "roof", "fountain", "aerial", "detail", "fragment", ""]
        counts = {}
        for side in order:
            rows = [v for v in my_views if v["side"] == side]
            if not rows:
                continue
            counts[side] = len(rows)
            lines += [f"### {SIDE_WORD.get(side, 'Side not settled')} ({len(rows)})", ""]
            lines += table(["Picture", "Row", "Date", "What shows", "State", "Reliability", "Rights", "Link"], [[v["photo_id"], v["id"], photos[v["photo_id"]]["date"][:34], v["visible_part"], v["state"], v["reliability"], photos[v["photo_id"]]["rights_class"], photos[v["photo_id"]]["source_url"]] for v in sorted(rows, key=lambda v: (v["state"] != "1780s", {"high": 0, "medium": 1, "low": 2}.get(v["reliability"], 3), v["photo_id"]))]) + [""]
        lines += ["## Dimension sheet", "", f"Machine-readable: `dimensions.json`. Figures by method: " + ", ".join(f"{m} {n}" for m, n in by_method.items()) + ". Method: " + "; ".join(METHOD_WORD.values()) + ".", ""]
        lines += ["### What the 3D boxes take now (`research/xiyanglou/boxes.csv`)", ""]
        lines += table(["Row", "Part", "Frontage × depth", "Eave", "Top", "Grade", "Sources"], [[m["id"], m["part"], f"{fig(m['frontage'])} × {fig(m['depth'])}", fig(m["eave"]), fig(m["top"]), f"{m['confidence']}{', assumed' if m['assumed'] else ''}", m["sources"]] for m in model]) + [""]
        lines += ["### Every figure", ""]
        rows = [d for d in dims if top_of(d["id"]) == bid]
        rows = sorted(rows, key=lambda d: (d["id"], d["what"] not in ("frontage", "depth"), METHOD_RANK.get(d["method"], 9), d["part"]))
        lines += table(["Row", "Part", "What", "Value", "±", "Method", "Grade", "Source", "Locator", "Basis"], [[d["id"], d["part"], what_label(d["what"]), f"{fig(d['value_m'])} {unit_of(d['what'])}", fig(d["err_m"] or 0), d["method"] + (" (search extract)" if d["status"] == "snippet" else ""), d["confidence"], d["source_id"], d["locator"], d["basis"]] for d in rows]) + [""]
        lines += ["## Materials and colours of the 1780s state", ""]
        own = [m for m in materials if top_of(m["id"]) == bid]
        lines += table(["Row", "Part", "What", "Colour", "Source", "Grade", "Seen"], [[m["id"], m["part"], m["what"], m["colour"], f"{m['source_id']} {m['locator']}", m["confidence"], m["status"]] for m in own]) + [""] if own else ["Nothing stated for this building alone."] + [""]
        lines += ["What holds for the group: see `research/xiyanglou/README.md`, Materials.", ""]
        lines += ["## What survives, and what was moved", "", a["survives_en"], ""]
        own = [f for f in fragments if top_of(f["id"]) == bid]
        if own:
            lines += table(["Row", "What", "Material", "Said to be from", "Now at", "Moved", "Today", "Source", "Grade"], [[f["id"], f["what"], f["material"], f["from_where_stated"], f"{f['now_at']} {f['now_place_zh']}", f["moved"], f["status_today"], f"{f['source_id']} {f['link']}", f["confidence"]] for f in own]) + [""]
        lines += ["## The best views for modellers", ""]
        own = sorted([b for b in best if b["id"] == bid], key=lambda b: int(b["rank"]))
        lines += table(["Rank", "Picture", "Why"], [[b["rank"], b["photo_id"], b["why"]] for b in own]) + [""] if own else ["None chosen."] + [""]
        own = [r for r in rephoto if top_of(r["id"]) == bid]
        if own:
            lines += ["## Rephotography", ""]
            lines += table(["Row", "Old", "New", "Same view", "What changed"], [[r["id"], r["old"], r["new"], r["same_view"], r["what_changed"]] for r in own]) + [""]
        plates = a["plates"]
        own = [i for i in impressions if i["plate"] and int(i["plate"]) in plates]
        lines += [f"## Impressions of its plates ({', '.join(map(str, plates))})", ""]
        lines += table(["Plate", "Holder", "Date", "Px", "Rights", "Link"], [[i["plate"], i["archive"], i["date"][:40], i["width"], i["rights_class"], i["source_url"]] for i in own]) + [""]
        own = [e for e in evidence if re.search(rf"(?<![A-Za-z0-9-]){bid}(?:[:-])", e["shows"])]
        lines += [f"## Texts, drawings and reports ({len(own)})", ""]
        lines += table(["Evidence", "Kind", "Title", "Date", "Locator", "Rights", "Seen"], [[e["evidence_id"], e["kind"], e["title"], e["date"], f"{e['source_id']} {e['locator']}", e["rights_class"], e["status"]] for e in own]) + [""]
        own = [r for r in recons if re.search(rf"(?<![A-Za-z0-9-]){bid}(?:[:-])", r["shows"])]
        if own:
            lines += [f"## Reconstructions by others, not evidence ({len(own)})", ""]
            lines += table(["Id", "Author", "Year", "Title", "Rights"], [[r["recon_id"], r["author"], r["year"], r["title"], r["rights_class"]] for r in own]) + [""]
        pat = re.compile(rf"(?<![A-Za-z0-9-])(?:{bid}|{a['zh']})(?![0-9])")
        qs = [l for l in questions.splitlines() if pat.search(l) and re.match(r"^- \*\*Q\d+\.", l)]
        lines += ["## Open questions", ""] + [f"- {re.sub(r'^- ', '', q)[:320]}" for q in qs] + ([] if qs else ["None that name it."]) + [""]
        ws = [l for l in wishlist if l.startswith("|") and pat.search(l)]
        lines += ["## Wishlist", ""] + ws[:12] + ([] if ws else ["None that name it; see `research/wishlist.md`."]) + ["", END, ""]
        new = "\n".join(lines) + "\n" + hand
        if not path.exists() or path.read_text(encoding="utf-8") != new:
            path.write_text(new, encoding="utf-8")
        summary.append(dict(id=bid, zh=a["zh"], pinyin=a["pinyin"], counts=counts, views=len(my_views), dims=by_method, plates=len(plates), folder=folder.name))

    # the overview's tables
    readme = XY / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else f"# Xiyang Lou\n\n{START}\n{END}\n"
    head, rest = text.split(START, 1)
    tail = rest.split(END, 1)[1]
    t = [START, "", "## The buildings, as measured here", "", "Pictures per side count `views.csv` rows, parts included. S N E W are façades; O all else.", ""]
    t += table(["Id", "Name", "Pictures", "S", "N", "E", "W", "O", "Figures a", "b", "c", "d", "e", "Dossier"], [[s["id"], f"{s['zh']} {s['pinyin']}", s["views"], s["counts"].get("S", 0), s["counts"].get("N", 0), s["counts"].get("E", 0), s["counts"].get("W", 0), sum(n for k, n in s["counts"].items() if k not in "SNEW"), *[s["dims"][m] for m in "abcde"], f"[{s['folder']}]({s['folder']}/README.md)"] for s in summary]) + [""]
    t += ["## The plates and where they were drawn from", "", "Viewpoints are estimates, with a focal length carried from plate 2: `viewpoints.csv` says how. Shown as arrows on `site/xiyanglou/keyplan.svg`, made by `scripts/xiyanglou_page.py` from our own layers only.", ""]
    vp = {int(v["plate"]): v for v in viewpoints}
    rows = []
    for n in range(1, 21):
        own = [i for i in impressions if i["plate"] and int(i["plate"]) == n]
        free = sorted([i for i in own if i["rights_class"] == "free"], key=lambda i: -int(i["width"] or 0))
        pid = f"P{40 + n:04d}"
        v = vp[n]
        rows.append([n, photos[pid]["title"].split(" (")[0], pid, f"{free[0]['archive'][:30]}, {free[0]['width']} px" if free else "", len(own), f"{float(v['lat']):.5f}, {float(v['lon']):.5f}", f"{v['bearing']}°", f"{v['dist_m']} ± {v['err_m']} m"])
    t += table(["Plate", "Title", "Picture", "Best free copy listed", "Impressions listed", "Viewpoint", "Looks", "Distance"], rows) + ["", f"Every impression: `impressions.csv`, {len(impressions)} rows. In git: Palace Museum copies at 2400 px as P0041-P0060; the Chester Beatty plate 1 as P0223. Full size: `research/raw/plates/`, local.", ""]
    t += ["## Materials: what holds for the group", ""]
    t += table(["Part", "What", "Colour", "Source", "Grade", "Seen"], [[m["part"], m["what"], m["colour"], m["source_id"], m["confidence"], m["status"]] for m in materials if m["id"] == "GARDEN:XY"]) + [""]
    t += ["## Fragments that are not tied to one building, or not Xiyang Lou at all", ""]
    t += table(["Row", "What", "Now at", "Moved", "Source", "Grade", "Note"], [[f["id"], f["what"], f["now_at"], f["moved"], f["source_id"], f["confidence"], f["note"]] for f in fragments if not f["id"].startswith("XY")]) + [""]
    total = {m: sum(s["dims"][m] for s in summary) for m in "abcde"}
    t += [f"Dimension figures in all: {sum(1 for d in dims)}, of which on a named building {sum(total.values())}: " + ", ".join(f"{m} {n}" for m, n in total.items()) + ".", "", END]
    new = head + "\n".join(t) + tail
    if new != text:
        readme.write_text(new, encoding="utf-8")
    print(f"{len(ids)} dossiers; pictures tied to a side {len(views)}; figures {len(dims)}, on a building {total}; fragments {len(fragments)}; rephotography {len(rephoto)}; impressions {len(impressions)}")


if __name__ == "__main__":
    main()
