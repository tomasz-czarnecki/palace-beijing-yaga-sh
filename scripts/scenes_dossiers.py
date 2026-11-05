"""The scene dossiers, one per scene or compound outside the Xiyang Lou, from the sheets in research/scenes/ and the catalogues. Idempotent: a second run changes nothing.

  uv run python scripts/scenes_dossiers.py        (after boxes1860.py; before building_pages.py and scenes_page.py)

Reads research/scenes/: about.json (the text, by hand), halls.csv (each hall as a source states it), dimensions.csv (every figure, with its method and scale), views.csv (how a picture serves a modeller), best.csv, digs.csv, interior.csv, parts.csv; research/buildings.csv, research/photos/catalog.csv, research/evidence/catalog.csv, research/reconstructions/catalog.csv, research/twins/catalog.csv, research/layers/scenes_1860, islands_1860, water_1860, research/typology/params.json, research/questions.md, research/wishlist.md.
Writes:
  research/scenes/<ID>-<slug>/README.md        the block between the markers; `## Notes` below it is hand-written and never touched
  research/scenes/<ID>-<slug>/dimensions.json  the dimension sheet: the figures of dimensions.csv, and the scene's extent, islands and water measured here on the traced plan (method b, status run); public fields only, for building_pages.py
  research/scenes/README.md                    the tables between the markers
  research/scenes/typology_check.json          measured figures against the defaults of typology/params.json, by hall class
"""

import csv
import json
import re
from pathlib import Path

import pyproj
import shapely
from shapely.geometry import shape

ROOT = Path(__file__).resolve().parent.parent
SC = ROOT / "research/scenes"
LAYERS = ROOT / "research/layers"
START = "<!-- generated:start (scripts/scenes_dossiers.py): do not edit between these markers -->"
END = "<!-- generated:end -->"
METHOD_WORD = {"a": "a, a published survey, excavation report or measured drawing, or a Qing drawing or text that writes the figure", "b": "b, measured on the plan or a ruin footprint", "c": "c, read from a painting or woodcut by module", "d": "d, estimated from a photograph with a known object", "e": "e, typology, or a figure with no survey behind it"}
WHAT_WORD = {"frontage": "Frontage", "depth": "Depth", "height_ridge": "Ridge height", "height_eave": "Eave height", "column_h": "Column height", "platform_h": "Platform height", "bay_width": "Bay width", "terrace_w": "Terrace width", "terrace_d": "Terrace depth", "court_w": "Court width", "court_d": "Court depth", "island_w": "Island, long side", "island_d": "Island, short side", "pool_w": "Pool width", "pool_d": "Pool depth (along)", "wall_h": "Wall height", "wall_t": "Wall thickness", "diameter": "Diameter", "extent_long": "Extent, long side", "extent_short": "Extent, short side", "area": "Area", "island_area": "Island area", "water_area": "Water inside the outline", "lake_area": "Lake area", "height": "Height"}
UNIT = {"area": "m²", "island_area": "m²", "water_area": "m²", "lake_area": "m²", "footprint_m2": "m²", "area_m2": "m²", "volume_m3": "m³", "area_ha": "ha"}
KEY_WHATS = {"frontage", "depth", "height_ridge", "height_eave", "column_h", "platform_h", "terrace_w", "terrace_d", "court_w", "court_d", "island_w", "island_d", "pool_w", "pool_d", "diameter", "extent_long", "extent_short", "area", "lake_area", "height"}
METHOD_RANK = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4}
VIEW_WORD = {"album": "The album of 1744", "woodcut": "The woodcuts of 1745", "gouache": "The gouaches of 1750-92", "1887": "The lithograph of 1887", "yangshilei": "Yangshi Lei drawings", "tangyang": "Card models 烫样", "ruin": "Ruin photographs", "today": "Today", "aerial": "From above", "detail": "Details", "": "Not yet sorted"}
INTERIOR_KINDS = {"furniture", "painting", "plaque", "couplet", "object"}
COMPASS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
TO_UTM = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32650", always_xy=True)
TYPO_WHATS = {"frontage": "frontage_range_m", "depth": "depth_m", "height_ridge": "ridge_m", "height_eave": "eave_m", "column_h": "column_m", "platform_h": "platform_m"}


def rd(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def top_of(bid):
    return bid.split("-")[0]


def ties(text):
    """`YM03:sure;YM03-01:likely` -> {id: conf}; GARDEN tags are left out."""
    out = {}
    for item in filter(None, (text or "").split(";")):
        bits = item.split(":")
        if bits[0] != "GARDEN":
            out[bits[0]] = bits[1] if len(bits) > 1 else "likely"
    return out


def what_label(what):
    if what.startswith("other:"):
        return what[6:].replace("_", " ").capitalize()
    return WHAT_WORD.get(what, what.replace("_", " ").capitalize())


def unit_of(what):
    return UNIT.get(what.removeprefix("other:"), "m")


def fig(v):
    return f"{float(v):g}"


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in rows:
        out.append("| " + " | ".join(str(c).replace("|", "/").replace("\n", " ") for c in r) + " |")
    return out


def compass(deg):
    return COMPASS[round(float(deg) / 45) % 8] if deg not in ("", None) else ""


def utm(geom):
    return shapely.transform(geom, lambda c: __import__("numpy").column_stack(TO_UTM.transform(c[:, 0], c[:, 1])))


def extent(geom):
    """Long and short side of the minimum rotated rectangle, in metres, and the bearing of the long side."""
    rect = shapely.minimum_rotated_rectangle(geom)
    xs, ys = rect.exterior.coords.xy
    sides = [((xs[i + 1] - xs[i]) ** 2 + (ys[i + 1] - ys[i]) ** 2) ** 0.5 for i in range(2)]
    return max(sides), min(sides)


def measured(scene_id, zh, layers):
    """Figures measured here on the traced layers (method b, status run): the outline the plan reader drew round the scene, its islands, the water inside it."""
    out = []
    polys = [utm(shape(f["geometry"])) for f in layers["scenes"] if f["properties"]["id"] == scene_id]
    base = dict(id=scene_id, method="b", source_id="S01", status="run", err_m="")
    if polys:
        geom = shapely.union_all(polys)
        long, short = extent(geom)
        loc = "layers/scenes_1860, UTM 50N, minimum rotated rectangle"
        basis = "the outline a plan reader drew round the island or court of the scene (Round 1); not a boundary known from a source"
        out += [dict(base, part="the scene's outline on the plan", what="extent_long", value_m=round(long), err_m=10, confidence="C", locator=loc, scale="the georeferenced plan S01 (RMS 10.6 m, research/georef/)", basis=basis),
                dict(base, part="the scene's outline on the plan", what="extent_short", value_m=round(short), err_m=10, confidence="C", locator=loc, scale="the georeferenced plan S01 (RMS 10.6 m, research/georef/)", basis=basis),
                dict(base, part="the scene's outline on the plan", what="area", value_m=round(geom.area, -2), err_m=round(geom.area * 0.1, -2), confidence="C", locator="layers/scenes_1860, UTM 50N, polygon area", scale="UTM 50N", basis=basis)]
        water = [utm(shape(f["geometry"])) for f in layers["water"]]
        wet = sum(w.intersection(geom).area for w in water if w.intersects(geom))
        if wet > 50:
            out.append(dict(base, part="water inside the scene's outline", what="water_area", value_m=round(wet, -1), err_m=round(wet * 0.1, -1), confidence="B", locator="layers/water_1860 within layers/scenes_1860", scale="UTM 50N", basis="the water traced from S01 inside the reader's outline"))
    for f in layers["islands"]:
        if scene_id in (f["properties"].get("scene_ids") or "").split(";"):
            g = utm(shape(f["geometry"]))
            long, short = extent(g)
            part = f"island {f['properties']['id']}" + (f" ({f['properties']['name_zh']})" if f["properties"].get("name_zh") else "")
            loc = "layers/islands_1860, UTM 50N, minimum rotated rectangle"
            out += [dict(base, part=part, what="island_w", value_m=round(long), err_m=10, confidence="B", locator=loc, scale="the georeferenced plan S01", basis="land enclosed by the water traced from S01"),
                    dict(base, part=part, what="island_d", value_m=round(short), err_m=10, confidence="B", locator=loc, scale="the georeferenced plan S01", basis="land enclosed by the water traced from S01"),
                    dict(base, part=part, what="island_area", value_m=round(g.area, -2), err_m=round(g.area * 0.1, -2), confidence="B", locator="layers/islands_1860, UTM 50N, polygon area", scale="UTM 50N", basis="land enclosed by the water traced from S01")]
    if not polys and zh:
        for f in layers["water"]:
            if f["properties"].get("name_zh") == zh:
                g = utm(shape(f["geometry"]))
                long, short = extent(g)
                loc = f"layers/water_1860 {f['properties']['id']}, UTM 50N, minimum rotated rectangle"
                out += [dict(base, part=f"the lake {zh}", what="extent_long", value_m=round(long), err_m=10, confidence="B", locator=loc, scale="the georeferenced plan S01", basis="the water traced from S01, islands included in the rectangle"),
                        dict(base, part=f"the lake {zh}", what="extent_short", value_m=round(short), err_m=10, confidence="B", locator=loc, scale="the georeferenced plan S01", basis="the water traced from S01, islands included in the rectangle"),
                        dict(base, part=f"the lake {zh}", what="lake_area", value_m=round(g.area, -2), err_m=round(g.area * 0.08, -2), confidence="B", locator=f"layers/water_1860 {f['properties']['id']}, UTM 50N, polygon area", scale="UTM 50N", basis="the water traced from S01, islands left out")]
    return out


def figure_public(d):
    return {"id": d["id"], "part": d["part"], "what": d["what"], "label": what_label(d["what"]), "value": float(d["value_m"]), "err": float(d["err_m"] or 0), "unit": unit_of(d["what"]), "method": d["method"], "confidence": d["confidence"], "source": d["source_id"], "locator": d["locator"], "snippet": d["status"] == "snippet", "key": d["what"] in KEY_WHATS, "scale": d.get("scale", "")}


def sort_figures(rows):
    return sorted(rows, key=lambda d: (not d["key"], d["locator"].startswith("layers/"), METHOD_RANK.get(d["method"], 9), d["id"] != top_of(d["id"]), d["id"], d["what"] not in ("frontage", "depth", "extent_long", "extent_short"), d["part"], d["what"], d["value"]))


def stated(hall_rows, field):
    """What the sources say of one field of a hall, best grade first: `5 (S05 j80:9b)`."""
    rank = {"A": 0, "B": 1, "C": 2}
    seen, out = set(), []
    for h in sorted(hall_rows, key=lambda h: (rank.get(h["confidence"], 3), h["source_id"])):
        v = h[field].strip()
        if v and v not in seen:
            seen.add(v)
            out.append(f"{v} ({h['source_id']})")
    return "; ".join(out)


def typology_check(dims, rows, params):
    """Measured figures (methods a, b on a ruin, d) on a hall with a class, against the class defaults."""
    classes = params["classes"]
    out = {}
    overall = {d["id"] for d in dims if d["what"] == "other:overall_depth"}
    for d in dims:
        what = "depth" if d["what"] == "other:overall_depth" else d["what"]
        if d["what"] == "depth" and d["id"] in overall:
            continue  # a roll or a bay between columns: the hall's overall depth stands for it
        if "inside" in d["part"] or "clear" in d["what"]:
            continue  # a room's inside, not the hall
        d = dict(d, what=what)
        if d["method"] not in ("a", "d") or d["what"] not in TYPO_WHATS or d["id"] not in rows:
            continue
        cls = rows[d["id"]]["hall_class"]
        if cls not in classes:
            continue
        ref = classes[cls].get(TYPO_WHATS[d["what"]])
        if ref is None:
            continue
        lo, hi = (ref if isinstance(ref, list) else (ref * 0.85, ref * 1.15))
        if isinstance(ref, list) and d["what"] == "column_h":
            lo, hi = min(ref) * 0.85, max(ref) * 1.15
        v = float(d["value_m"])
        item = {"id": d["id"], "name": rows[d["id"]]["name_zh"], "what": d["what"], "value": v, "default": ref, "within": lo <= v <= hi, "ratio": round(v / ((lo + hi) / 2), 2), "source": d["source_id"], "locator": d["locator"], "status": d["status"]}
        out.setdefault(cls, []).append(item)
    return {cls: {"n": len(items), "within": sum(i["within"] for i in items), "outside": [i for i in items if not i["within"]], "all": items} for cls, items in sorted(out.items())}


def main():
    about = json.load(open(SC / "about.json", encoding="utf-8"))
    halls, dims, views, best, digs, interior, parts = (rd(SC / n) for n in ("halls.csv", "dimensions.csv", "views.csv", "best.csv", "digs.csv", "interior.csv", "parts.csv"))
    rows = {r["id"]: r for r in rd(ROOT / "research/buildings.csv")}
    photos = {p["photo_id"]: p for p in rd(ROOT / "research/photos/catalog.csv")}
    evidence = rd(ROOT / "research/evidence/catalog.csv")
    recons = rd(ROOT / "research/reconstructions/catalog.csv")
    twins = rd(ROOT / "research/twins/catalog.csv")
    params = json.load(open(ROOT / "research/typology/params.json", encoding="utf-8"))
    layers = {k: json.load(open(LAYERS / f"{n}.geojson", encoding="utf-8"))["features"] for k, n in (("scenes", "scenes_1860"), ("islands", "islands_1860"), ("water", "water_1860"))}
    questions = (ROOT / "research/questions.md").read_text(encoding="utf-8").split("\n## Resolved")[0]
    wishlist = (ROOT / "research/wishlist.md").read_text(encoding="utf-8").splitlines()
    children = {}
    for r in rows.values():
        if r["parent_id"]:
            children.setdefault(r["parent_id"], []).append(r["id"])
    ev_by, ph_by, rc_by = {}, {}, {}
    for e in evidence:
        for k, c in ties(e["shows"]).items():
            ev_by.setdefault(k, []).append((e, c))
    for p in photos.values():
        if p["relation"] != "self" or not p["source_url"].startswith("http"):
            continue
        for k, c in ties(p["shows"]).items():
            ph_by.setdefault(k, []).append((p, c))
    for r in recons:
        for k, c in ties(r["shows"]).items():
            rc_by.setdefault(k, []).append((r, c))
    ids = [k for k in about if not k.startswith("_")]
    summary, all_figures = [], []
    for sid in ids:
        a = about[sid]
        r = rows[sid]
        folder = SC / f"{sid}-{a['slug']}"
        folder.mkdir(exist_ok=True)
        path = folder / "README.md"
        hand = "## Notes\n\n<!-- Yours: regeneration never touches this part. -->\n"
        if path.exists():
            text = path.read_text(encoding="utf-8")
            if END not in text:
                raise SystemExit(f"{path}: markers missing")
            hand = text.split(END, 1)[1].lstrip("\n")
        mine = [sid] + children.get(sid, [])
        sheet_rows = [d for d in dims if top_of(d["id"]) == sid] + measured(sid, a["zh"], layers)
        figures = sort_figures([figure_public(d) for d in sheet_rows])
        all_figures += [(d, sid) for d in sheet_rows]
        by_method = {m: sum(d["method"] == m for d in figures) for m in "abcde"}
        new_by_method = {m: sum(d["method"] == m for d in sheet_rows if d["status"] != "run") for m in "abcde"}
        sheet = {"id": sid, "name": f"{a['zh']} {a['pinyin']}", "by_method": by_method, "figures": figures}
        (folder / "dimensions.json").write_text(json.dumps(sheet, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

        my_halls = [h for h in halls if h["scene"] == sid]
        page = f"/scenes/{sid}/" if a.get("public") else f"/scenes/#{sid}"
        title_en = f', "{a["en"]}"' if a["en"] else ""
        lines = [START, "", f"# {sid}: {a['zh']} {a['pinyin']}{title_en}", ""]
        if a.get("role_en"):
            lines += [f"Malone calls it {a['role_en']}.", ""]
        lines += [f"Wave {a['wave']} · {r['garden']} · 3D: `/reconstruction/3d.html?b={sid}` · Page: `{page}` · Row: `research/buildings/{sid}-{a['slug']}/`", ""]
        blank = "Not written yet: the rows below are what the catalogues hold."
        lines += ["## What it was", "", a["what_en"] or blank, ""]
        facts = [(k, r[k]) for k in ("built", "changed", "destroyed") if r[k]]
        if facts:
            lines += ["From the inventory row: " + "; ".join(f"**{k}** {v}" for k, v in facts) + f" ({r['sources'].replace(';', ', ')}).", ""]
        lines += ["## The scene itself", "", "### The leaf of 1744, its poem and preface", "", a["scene_en"] or ("Not one of the Forty Scenes of 1744." if not (sid.startswith("YM") and int(sid[2:]) <= 40) else blank), "", "### How later sources differ", "", a["later_en"] or blank, ""]
        # building by building
        lines += [f"## Building by building ({len(children.get(sid, []))} rows)", "", "From `research/buildings.csv`, with what the sources state in `research/scenes/halls.csv` beside it. Size: a stated size where a source gives one, else the plan's block at the hall scale (rough; `research/typology/halls.md`). Faces: the compass point the front faces (assumed where no reader or source says).", ""]
        trow = []
        for cid in [sid] + children.get(sid, []):
            c = rows[cid]
            hs = [h for h in my_halls if h["id"] == cid]
            size = f"{fig(c['frontage_m'])} × {fig(c['depth_m'])}" if c["frontage_m"] and c["depth_m"] else ""
            src = "stated" if c["size_source"].startswith("stated") else "plan" if "plan px" in c["size_source"] else (c["size_source"][:20] or "no source given")
            faces = compass(c["orientation_deg"]) + (" (assumed)" if c["orientation_assumed"] == "True" and c["orientation_deg"] else "")
            name = " ".join(x for x in (c["name_zh"], c["name_pinyin"]) if x) or "unnamed"
            trow.append([cid, name, c["name_on_plan"], c["type"], stated(hs, "bays") or c["bays"] or (f"plan {c['bays_plan']}" if c["bays_plan"] else ""), f"{size} ({src})" if size else "", stated(hs, "faces") or faces, stated(hs, "storeys") or c["storeys"], stated(hs, "roof") or c["roof"], stated(hs, "tiles") or c["roof_tiles"], c["confidence"]])
        lines += table(["Row", "Name", "On the plan", "Type", "Bays", "Size m", "Faces", "Storeys", "Roof", "Tiles", "Grade"], trow) + [""]
        if my_halls:
            lines += ["### As each source states it", ""]
            lines += table(["Row", "Plaque", "Bays", "Depth", "Roof", "Storeys", "Faces", "Place", "Built / changed", "Source", "Basis", "Grade", "Seen"], [[h["id"], " ".join(x for x in (h["plaque_zh"], h["pinyin"]) if x), h["bays"], " ".join(x for x in (h["depth"], h["purlins"]) if x), h["roof"], h["storeys"], h["faces"], h["relation"], " / ".join(x for x in (h["built"], h["changed"]) if x), f"{h['source_id']} {h['locator']}".strip(), h["basis"][:160], h["confidence"], h["status"]] for h in my_halls]) + [""]
        new = [h for h in my_halls if h["id"] == "NEW"]
        if new:
            lines += [f"Named in the sources and not yet a row of their own: {len(new)} (`NEW` above). They wait for a plan reading that ties them to a block.", ""]
        # evidence for each hall
        lines += ["## Evidence for each hall", ""]
        erow, bare = [], 0
        for cid in children.get(sid, []):
            pics = sorted({p["photo_id"] for p, _ in ph_by.get(cid, [])})
            texts = sorted({e["evidence_id"] for e, _ in ev_by.get(cid, [])})
            drawings = sorted({e["evidence_id"] for e, _ in ev_by.get(cid, []) if e["kind"] == "drawing"})
            hfig = [d for d in sheet_rows if d["id"] == cid]
            if not (pics or texts or hfig):
                bare += 1
                continue
            erow.append([cid, rows[cid]["name_zh"] or rows[cid]["name_on_plan"], len(pics), ", ".join(pics[:6]) + (" …" if len(pics) > 6 else ""), len(texts), ", ".join(texts[:8]) + (" …" if len(texts) > 8 else ""), ", ".join(drawings[:4]), len(hfig)])
        if erow:
            lines += table(["Row", "Name", "Pictures", "Ids", "Texts", "Ids", "Drawings", "Figures"], erow) + [""]
        lines += [f"{bare} of {len(children.get(sid, []))} rows have nothing of their own: they show the plan and the scene's evidence (the panel's fallback).", ""]
        # pictures of the scene
        mine_views = [v for v in views if top_of(v["id"]) == sid]
        scene_pics = {}
        for cid in mine:
            for p, c in ph_by.get(cid, []):
                scene_pics.setdefault(p["photo_id"], (p, c, cid))
        lines += [f"### Pictures of the scene ({len(scene_pics)})", ""]
        if mine_views:
            for kind in VIEW_WORD:
                vs = [v for v in mine_views if v["view"] == kind]
                if not vs:
                    continue
                lines += [f"**{VIEW_WORD[kind]}** ({len(vs)})", ""]
                lines += table(["Picture", "Row", "What shows", "State", "Reliability", "Rights", "Link"], [[v["photo_id"], v["id"], v["visible_part"], v["state"], v["reliability"], photos[v["photo_id"]]["rights_class"], photos[v["photo_id"]]["source_url"]] for v in sorted(vs, key=lambda v: ({"high": 0, "medium": 1, "low": 2}.get(v["reliability"], 3), v["photo_id"]))]) + [""]
        rest = [x for pid, x in sorted(scene_pics.items()) if pid not in {v["photo_id"] for v in mine_views}]
        if rest:
            lines += ["Not yet read for a modeller:", ""]
            lines += table(["Picture", "Row", "Tie", "Kind", "Date", "Rights", "Title"], [[p["photo_id"], cid, c, p["kind"], p["date"][:30], p["rights_class"], p["title"][:90]] for p, c, cid in rest]) + [""]
        # texts
        scene_ev = {}
        for cid in mine:
            for e, c in ev_by.get(cid, []):
                scene_ev.setdefault(e["evidence_id"], (e, c, cid))
        kinds = {}
        for e, _, _ in scene_ev.values():
            kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
        lines += [f"### Texts, drawings and reports ({len(scene_ev)})", "", "By kind: " + (", ".join(f"{k} {n}" for k, n in sorted(kinds.items())) or "none") + ". Excerpts and summaries: `research/evidence/catalog.csv`.", ""]
        order = sorted(scene_ev.values(), key=lambda x: ({"drawing": 0, "archaeology": 1, "plan": 2, "text": 3, "description": 4, "poem": 5}.get(x[0]["kind"], 6), x[0]["date"], x[0]["evidence_id"]))
        lines += table(["Evidence", "Row", "Kind", "Title", "Date", "Locator", "Rights", "Seen"], [[e["evidence_id"], cid, e["kind"], e["title"][:80], e["date"][:24], f"{e['source_id']} {e['locator']}"[:60], e["rights_class"], e["status"]] for e, c, cid in order[:60]]) + [""]
        if len(order) > 60:
            lines += [f"And {len(order) - 60} more, most of them dated poems: `grep {sid} research/evidence/catalog.csv`.", ""]
        # interior and setting
        own_int = [i for i in interior if top_of(i["id"]) == sid]
        lines += ["## Interior and setting", "", "### Interior", "", a["interior_en"] or "Nothing written yet.", ""]
        rows_int = [i for i in own_int if i["kind"] in INTERIOR_KINDS]
        if rows_int:
            lines += table(["Row", "Kind", "What", "Source", "Quote or basis", "Grade", "Seen"], [[i["id"], i["kind"], i["what"], f"{i['source_id']} {i['locator']}".strip(), i["quote_or_basis"][:160], i["confidence"], i["status"]] for i in rows_int]) + [""]
        lines += ["### The garden around it", "", a["setting_en"] or "Nothing written yet.", ""]
        rows_set = [i for i in own_int if i["kind"] not in INTERIOR_KINDS]
        if rows_set:
            lines += table(["Row", "Kind", "What", "Source", "Quote or basis", "Grade", "Seen"], [[i["id"], i["kind"], i["what"], f"{i['source_id']} {i['locator']}".strip(), i["quote_or_basis"][:160], i["confidence"], i["status"]] for i in rows_set]) + [""]
        # what survives
        own_digs = [d for d in digs if top_of(d["id"]) == sid]
        lines += ["## What survives today", "", a["survives_en"] or "Nothing written yet.", ""]
        if own_digs:
            lines += table(["Row", "Year", "By", "What was found", "Source", "Link", "Seen", "Grade"], [[d["id"], d["year"], d["by"], d["what_found"], d["source_id"], d["link"], d["status"], d["confidence"]] for d in own_digs]) + [""]
        else:
            lines += ["No excavation or survey of its remains found in this round.", ""]
        # reconstructions
        own_rc = {}
        for cid in mine:
            for rr, c in rc_by.get(cid, []):
                own_rc.setdefault(rr["recon_id"], (rr, c))
        lines += [f"## Modern reconstructions, not evidence ({len(own_rc)})", "", "Never a source for a size or a position here.", ""]
        if a["recons_en"]:
            lines += [a["recons_en"], ""]
        if own_rc:
            lines += table(["Id", "Kind", "Author", "Year", "Title", "Built from, as stated", "Rights", "Seen"], [[rr["recon_id"], rr["kind"], rr["author"][:40], rr["year"], rr["title"][:70], rr["method_stated"][:120], rr["rights_class"], rr["status"]] for rr, c in sorted(own_rc.values(), key=lambda x: x[0]["recon_id"])]) + [""]
        own_tw = [t for t in twins if top_of(t["object_id"].replace(":", "-")) == sid]
        if own_tw:
            lines += [f"### Surviving comparable buildings, not this building ({len(own_tw)})", ""]
            lines += table(["Id", "Row", "Building", "Relation", "Standing", "Grade", "What it tells"], [[t["twin_id"], t["object_id"], f"{t['twin_name_zh']} {t['twin_name_en']}, {t['twin_place']}", t["relation"], t["still_standing"], t["confidence"], t["what_it_tells"][:120]] for t in own_tw]) + [""]
        # best views
        own_best = sorted([b for b in best if b["id"] == sid], key=lambda b: int(b["rank"]))
        lines += ["## The best views for modellers", ""]
        if a["best_en"]:
            lines += [a["best_en"], ""]
        lines += table(["Rank", "Picture or text", "Why"], [[b["rank"], b["ref"], b["why"]] for b in own_best]) + [""] if own_best else ["None chosen yet."] + [""]
        # dimension sheet
        lines += ["## Dimension sheet", "", f"Machine-readable: `dimensions.json`. Figures by method: " + ", ".join(f"{m} {n}" for m, n in by_method.items()) + ". " + "; ".join(METHOD_WORD.values()) + ". Rows marked `run` were measured by `scripts/scenes_dossiers.py` on the traced layers. The Qing module: 1 营造尺 = 0.32 m.", ""]
        lines += table(["Row", "Part", "What", "Value", "±", "Method", "Grade", "Source", "Locator", "Scale", "Basis", "Seen"], [[d["id"], d["part"], what_label(d["what"]), f"{fig(d['value_m'])} {unit_of(d['what'])}", fig(d["err_m"] or 0), d["method"], d["confidence"], d["source_id"], d["locator"], d.get("scale", ""), d["basis"][:160], d["status"]] for d in sorted(sheet_rows, key=lambda d: (d["id"] != sid, d["id"], METHOD_RANK.get(d["method"], 9), d["part"], d["what"]))]) + [""]
        own_parts = [p for p in parts if top_of(p["id"]) == sid]
        if own_parts:
            lines += ["## Unnamed rows identified", ""]
            lines += table(["Row", "Name", "What", "Basis", "Source", "Grade", "Action"], [[p["id"], " ".join(x for x in (p["name_zh"], p["name_pinyin"]) if x), p["what"], p["basis"][:140], p["source_id"], p["confidence"], p["action"]] for p in own_parts]) + [""]
        # gaps
        pat = re.compile(rf"(?<![A-Za-z0-9-])(?:{sid}|{re.escape(a['zh'])})(?![0-9])") if a["zh"] else re.compile(rf"(?<![A-Za-z0-9-]){sid}(?![0-9])")
        qs = [l for l in questions.splitlines() if pat.search(l) and re.match(r"^- \*\*Q\d+\.", l)]
        ws = [l for l in wishlist if l.startswith("|") and pat.search(l)]
        lines += ["## Gaps and wishlist", "", a["gaps_en"] or "Not written yet.", "", "### Open questions that name it", ""] + [f"- {re.sub(r'^- ', '', q)[:320]}" for q in qs] + ([] if qs else ["None."]) + ["", "### Wishlist rows that name it", ""] + (["| What | Replaces | Where held | How |", "|---|---|---|---|"] + ws[:12] if ws else ["None; see `research/wishlist.md`."]) + ["", END, ""]
        text = "\n".join(lines) + "\n" + hand
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8")
        own_ev_halls = sum(1 for cid in children.get(sid, []) if ph_by.get(cid) or ev_by.get(cid))
        free_pics = sum(1 for p, c, cid in scene_pics.values() if p["rights_class"] == "free")
        texts_n = len(scene_ev)
        drawings_n = sum(1 for e, c, cid in scene_ev.values() if e["kind"] == "drawing")
        written = sum(bool(a[k]) for k in ("what_en", "scene_en", "later_en", "interior_en", "setting_en", "survives_en", "best_en", "gaps_en"))
        score = texts_n / 10 + free_pics * 2 + len(own_digs) * 4 + new_by_method["a"] * 2 + len(mine_views) + written * 3
        summary.append(dict(id=sid, zh=a["zh"], pinyin=a["pinyin"], wave=a["wave"], public=bool(a.get("public")), folder=folder.name, halls=len(children.get(sid, [])), halls_own=own_ev_halls, pics=len(scene_pics), free=free_pics, texts=texts_n, drawings=drawings_n, digs=len(own_digs), dims=by_method, new_dims=new_by_method, written=written, score=round(score, 1), views=len(mine_views)))

    check = typology_check([d for d, _ in all_figures], rows, params)
    (SC / "typology_check.json").write_text(json.dumps(check, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    readme = SC / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else f"# Scenes\n\n{START}\n{END}\n"
    head, rest = text.split(START, 1)
    tail = rest.split(END, 1)[1]
    t = [START, "", "## Every scene and compound, as measured here", "", "Halls: rows inside it; own: with a picture or text of their own. Pictures: tied to the scene or its halls (free). Read: pictures read for a modeller in `views.csv`. Texts: evidence rows (drawings). Digs: excavations or surveys of the remains. Figures by method a b c d e, with the new ones from research in brackets (the rest measured here on the traced layers). Prose: sections written, of 8. Score: how well documented, used to pick the public pages (texts/10 + free pictures × 2 + digs × 4 + new a-figures × 2 + read pictures + sections × 3).", ""]
    t += table(["Id", "Name", "Wave", "Halls", "Own", "Pictures", "Read", "Texts", "Digs", "a", "b", "c", "d", "e", "Prose", "Score", "Public", "Dossier"], [[s["id"], f"{s['zh']} {s['pinyin']}", s["wave"], s["halls"], s["halls_own"], f"{s['pics']} ({s['free']})", s["views"], f"{s['texts']} ({s['drawings']})", s["digs"], *[f"{s['dims'][m]} ({s['new_dims'][m]})" if s["new_dims"][m] else s["dims"][m] for m in "abcde"], s["written"], s["score"], "yes" if s["public"] else "", f"[{s['folder']}]({s['folder']}/README.md)"] for s in summary]) + [""]
    total = {m: sum(s["dims"][m] for s in summary) for m in "abcde"}
    new_total = {m: sum(s["new_dims"][m] for s in summary) for m in "abcde"}
    t += [f"Dossiers: {len(summary)}, public pages {sum(s['public'] for s in summary)}. Figures in all: {sum(total.values())} (" + ", ".join(f"{m} {n}" for m, n in total.items()) + f"); from research {sum(new_total.values())} (" + ", ".join(f"{m} {n}" for m, n in new_total.items()) + f"), measured here on the layers {sum(total.values()) - sum(new_total.values())}. Halls with evidence of their own: {sum(s['halls_own'] for s in summary)} of {sum(s['halls'] for s in summary)}.", ""]
    t += ["## Typology check", "", "Measured figures (methods a and d) on a hall with a class, against `research/typology/params.json`: a range for frontage and depth, ±15% round a single default. A hall's overall depth stands for its depth where both are given; a room's inside is left out. `typology_check.json` holds every item. Proposals stand in the hand-written part above and in `research/questions.md`.", ""]
    t += table(["Class", "Figures", "Within", "Outside", "Outside: row, what, value against default"], [[cls, c["n"], c["within"], len(c["outside"]), "; ".join(f"{i['id']} {i['name']} {i['what']} {i['value']:g} vs {i['default']}" for i in c["outside"][:6])] for cls, c in check.items()]) + ["", END]
    new = head + "\n".join(t) + tail
    if new != text:
        readme.write_text(new, encoding="utf-8")
    best5 = sorted(summary, key=lambda s: -s["score"])[:12]
    print(f"{len(ids)} dossiers; figures {sum(total.values())} {total}, from research {new_total}; halls with own evidence {sum(s['halls_own'] for s in summary)}; best documented: " + ", ".join(f"{s['id']} {s['score']}" for s in best5))


if __name__ == "__main__":
    main()
