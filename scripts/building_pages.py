"""One page per building and compound, and what the 3D view's panel reads. Idempotent: a second run changes nothing.

  uv run python scripts/building_pages.py        (after boxes1860.py)

Reads research/buildings.csv, research/questions.md, research/sources.md, research/photos/catalog.csv, research/layers/walls_1860 (the gates), site/reconstruction/data/halls_1860.geojson. Writes:
  research/buildings/<ID>-<slug>/index.md        every row of buildings.csv and every gate. The block between the markers is rewritten; `## Notes` below it is hand-written and never touched
  research/buildings/README.md                   the list of all of them
  site/reconstruction/data/buildings/<ID>.json   public: names, garden, dates, sources, confidence, what the texts say, the box. No plan pixels, no plan readers' notes, no /_local/ or raw/ path (asserted)
  research/raw/buildings/<ID>.json               local only (gitignored): the full version, with the plan readers' notes, for tools/serve_local.py

Notes go on the public site, except what stands below a line holding only `%% private %%`. Pictures are link entries for now: the pictures round brings the free images.
"""

import csv
import json
import re
import unicodedata
from pathlib import Path

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "research/buildings"
SITE_DATA = ROOT / "site/reconstruction/data"
PUBLIC_OUT = SITE_DATA / "buildings"
LOCAL_OUT = ROOT / "research/raw/buildings"
START = "<!-- generated:start (scripts/building_pages.py): do not edit between these markers -->"
END = "<!-- generated:end -->"
NOTES_HINT = "<!-- Yours: regeneration never touches this part. It goes on the public site; what you write below a line holding only %% private %% stays in the research copy. -->"
PRIVATE_LINE = "%% private %%"
# What may stand in a public file. Anything else stops the script.
PUBLIC_KEYS = {"id", "kind", "title", "subtitle", "object", "parent", "children", "position", "model", "facts", "notes_html", "photos", "questions", "sources"}
PUBLIC_FACT_KEYS = {"label", "value", "sources", "confidence"}
PUBLIC_PHOTO_KEYS = {"id", "title", "date", "creator", "archive", "source_url"}
ID_RE = re.compile(r"^((?:YM|CC|XY|QC)\d+(?:-[A-Z]*\d+)?|Z-[A-Z]*\d+|G\d+)-")

md = MarkdownIt("commonmark", {"html": False}).disable("image")  # raw HTML comes out escaped

BASIS_LINE = {
    "plan": "A plain box on the block drawn on the Qing plan S01: position and frontage from the plan, heights and roof from the typology of its hall class. It will be updated as the research goes on.",
    "stated": "A plain box at a size stated in a source, on the block drawn on the Qing plan S01. Heights and roof from the typology where not stated.",
    "xiyang": "Simple massing of a European palace, assumed: sizes from the texts and the ruin polygons, position from the plan or the ruin. Not a reading of the 1786 engravings yet.",
    "layout": "Assumed: the plan shows this compound's place and no single hall, so a few boxes are laid out from the typology. Confidence C.",
    "default": "Assumed: a position is known and no block is drawn, so a small default box stands there. Confidence C.",
    "gate": "Assumed: a gate on the walls layer with no hall drawn at its point, so a small default box stands there. Confidence C.",
}
ROOF_WORD = {"hip_gable": "hip-and-gable 歇山", "hip": "hip 庑殿", "gable": "gable 硬山 or 悬山", "pyramid": "pyramid 攒尖"}
SHAPE_WORD = {"terrace": "terrace", "wall": "wall", "pool": "pool", "octagon": "octagon"}


def split_ids(text):
    return [s.strip() for s in (text or "").split(";") if s.strip()]


def fact(label, value, sources="", confidence="", private=False):
    f = {"label": label, "value": str(value), "sources": sources, "confidence": confidence}
    if private:
        f["private"] = True
    return f


def slug(text):
    s = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    s = s[:44].strip("-")
    return s if s and s[0].isalpha() else f"x{s}" if s else "unnamed"


def load_questions():
    """Q id -> (title, text), open questions only."""
    text = (ROOT / "research/questions.md").read_text(encoding="utf-8").split("\n## Resolved")[0]
    out = {}
    current = None
    for line in text.splitlines():
        m = re.match(r"^- \*\*(Q\d+)\. (.+?)\*\*", line)
        if m:
            current = m[1]
            out[current] = [m[2].strip().rstrip("."), line]
        elif current and line.startswith("  "):
            out[current][1] += "\n" + line
    return {k: tuple(v) for k, v in out.items()}


def load_sources():
    out = {}
    for line in (ROOT / "research/sources.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| (S\d+) \| (.*)", line)
        if not m:
            continue
        cols = [c.strip() for c in m[2].rstrip(" |").split(" | ")]
        url = re.search(r"https?://[^\s|)]+", line)
        text = re.split(r"(?<=[a-z0-9)])\. ", cols[0])[0]
        out[m[1]] = {"id": m[1], "text": text[:180], "licence": cols[2][:140] if len(cols) > 2 else "", "url": url[0].rstrip(".,;") if url else ""}
    return out


class Book:
    def __init__(self):
        rd = lambda path: list(csv.DictReader(open(ROOT / path, encoding="utf-8", newline="")))
        self.rows = {r["id"]: r for r in rd("research/buildings.csv")}
        self.gates = {f["properties"]["id"]: f for f in json.load(open(ROOT / "research/layers/walls_1860.geojson", encoding="utf-8"))["features"] if f["geometry"]["type"] == "Point"}
        fc = json.load(open(SITE_DATA / "halls_1860.geojson", encoding="utf-8"))
        self.boxes, self.by_parent = {}, {}
        for f in fc["features"]:
            p = f["properties"]
            self.boxes.setdefault(p["building_id"], []).append(p)
            for a in p.get("also", []):
                self.boxes.setdefault(a, []).append(p)
            if p["parent_id"]:
                self.by_parent.setdefault(p["parent_id"], []).append(p)
        for row_id, target in fc.get("shared_rows", {}).items():
            self.boxes.setdefault(row_id, []).extend(self.boxes.get(target, []))
        self.questions = load_questions()
        self.sources = load_sources()
        self.children = {}
        for r in self.rows.values():
            if r["parent_id"]:
                self.children.setdefault(r["parent_id"], []).append(r["id"])
        self.photos = {}
        for p in rd("research/photos/catalog.csv"):
            if not p["source_url"].startswith("http"):
                continue
            for item in split_ids(p["shows"]):
                self.photos.setdefault(item.split(":")[0], []).append(p)

    def name(self, pid):
        """Chinese and pinyin first, then what the page is."""
        if pid in self.gates:
            p = self.gates[pid]["properties"]
            return " ".join(x for x in (p.get("name_zh"), p.get("name_pinyin")) if x) or "Gate without a name read on the plan"
        r = self.rows[pid]
        zh = r["name_zh"] or r["name_on_plan"]
        return " ".join(x for x in (zh, r["name_pinyin"]) if x) or "Hall without a name on the plan"

    def short(self, pid):
        if pid in self.gates:
            return self.gates[pid]["properties"].get("name_zh") or ""
        r = self.rows[pid]
        return r["name_zh"] or r["name_on_plan"] or ""

    def slug_of(self, pid):
        if pid in self.gates:
            return slug(self.gates[pid]["properties"].get("name_pinyin", ""))
        r = self.rows[pid]
        return slug(r["name_pinyin"] or r["name_en"])


def box_rows(boxes):
    rows = []
    if len(boxes) == 1:
        b = boxes[0]
        rows.append(["Box", f"{b['frontage_m']:g} × {b['depth_m']:g} m, {b['hall_class'].replace('_', ' ')}" + (f", {SHAPE_WORD[b['shape']]}" if b.get("shape") else "")])
        if b.get("part"):
            rows.append(["Part", b["part"]])
        if not b.get("shape"):
            rows.append(["Heights", f"platform {b['platform_m']:g} m, eave {b['eave_m']:g} m, ridge {b['ridge_m']:g} m above the ground"])
            word = ROOF_WORD.get(b["roof"], b["roof"])
            bits = [word, "rolled ridge 卷棚" if b.get("rolled") else "", "double eaves 重檐" if b.get("double") else "", f"{b['rolls']} parallel rolls 勾连搭" if b.get("rolls") else "", f"{b['tiles']} tile"]
            rows.append(["Roof", ", ".join(x for x in bits if x)])
        rows.append(["Faces", f"{b['orientation_deg']:g}° from north"])
        if b.get("fit") is not None:
            rows.append(["Fit", "reduced towards the size drawn on the plan, to stand clear of its neighbours or the water" + (f"; moved {b['moved_m']:g} m" if b.get("moved_m") else "")])
        elif b.get("moved_m"):
            rows.append(["Fit", f"moved {b['moved_m']:g} m, to stand clear of its neighbours or the water"])
        if b.get("over_water"):
            rows.append(["Water", "stands partly over the water layer: on piers or on a bank too thin for the layer to show"])
        rows.append(["Confidence", f"{b['confidence']}{', assumed' if b['assumed'] else ''}"])
    else:
        counted = {}
        for b in boxes:
            key = (b.get("part") or b["hall_class"].replace("_", " "), b["frontage_m"], b["depth_m"], b["eave_m"], b["ridge_m"])
            counted[key] = counted.get(key, 0) + 1
        for (part, f, d, eave, ridge), n in list(counted.items())[:10]:
            rows.append([f"{n} ×" if n > 1 else "1 ×", f"{part}: {f:g} × {d:g} m, eave {eave:g} m, ridge {ridge:g} m"])
        if len(counted) > 10:
            rows.append(["More", f"{len(counted) - 10} other kinds of box"])
        rows.append(["Confidence", " and ".join(sorted({b["confidence"] for b in boxes})) + (", all assumed" if all(b["assumed"] for b in boxes) else ", some assumed" if any(b["assumed"] for b in boxes) else "")])
    return rows


def model_of(book, pid, kind):
    boxes = book.boxes.get(pid, [])
    if kind == "compound" and not boxes:
        inner = book.by_parent.get(pid, [])
        if inner:
            assumed = sum(b["assumed"] for b in inner)
            return {"line": f"{len(inner)} boxes stand in this compound, {len(inner) - assumed} on blocks drawn on the plan, {assumed} assumed. Its halls are listed below.", "rows": []}
    if not boxes and kind == "gate":
        return {"line": "No box of its own: the hall drawn at this point stands for the gate in the 3D view.", "rows": []}
    if not boxes:
        return {"line": "No box in the 3D view: the plan shows no building here, or a plot, water, a hill or a name only.", "rows": []}
    return {"line": BASIS_LINE[boxes[0]["basis"]], "rows": box_rows(boxes)}


def clean_note(text):
    """The inventory's note, without the workers' shorthand. Facts and citations stay."""
    text = re.sub(r"\bname_en: [^.|]*\.(?:[^.|]*\d\.)?\s*", "", text)
    text = re.sub(r"\s*\(seen via Malone, picture worker holds the ID\)", "", text)
    text = re.sub(r"[;:,]?\s*see conflicts\.?", ".", text, flags=re.I)
    text = re.sub(r"\.\.+", ".", text)
    return text.strip(" ;")


def row_facts(r):
    """Public facts, then the research copy's."""
    src, conf = r["sources"], r["confidence"]
    out = []
    names = " ".join(x for x in (r["name_zh"], r["name_pinyin"]) if x)
    if names:
        out.append(fact("Name", names, src, conf))
    if r["name_en"]:
        out.append(fact("English", r["name_en"], src))
    if r["name_on_plan"] and r["name_on_plan"] != r["name_zh"]:
        out.append(fact("Written on the plan", r["name_on_plan"], "S01", conf))
    out.append(fact("Garden", r["garden"], src))
    out.append(fact("Type", r["type"], src, conf))
    if r["built"]:
        out.append(fact("Built", r["built"], src))
    if r["changed"]:
        out.append(fact("Changed", r["changed"], src))
    if r["destroyed"]:
        out.append(fact("Destroyed", r["destroyed"], src))
    if r["lat"]:
        out.append(fact("Position", f"{float(r['lat']):.5f}, {float(r['lon']):.5f}. {r['pos_source']}", "S01", r["pos_confidence"]))
    else:
        out.append(fact("Position", "Not placed: the name was not found on the plan."))
    if r["bays"] or r["bays_plan"]:
        out.append(fact("Bays", " / ".join(x for x in (f"{r['bays']} in the texts" if r["bays"] else "", f"{r['bays_plan']} on the plan" if r["bays_plan"] else "") if x), src))
    if r["frontage_m"] and r["depth_m"]:
        out.append(fact("Size in the inventory", f"{r['frontage_m']} × {r['depth_m']} m. {re.sub(r'stated: research/typology/params.json by_name.*', 'stated in a source', r['size_source'])}", "S01"))
    if r["storeys"]:
        out.append(fact("Storeys", r["storeys"], src))
    if r["roof"]:
        out.append(fact("Roof", r["roof"], src))
    if r["roof_tiles"]:
        out.append(fact("Tiles", r["roof_tiles"], src))
    quote = r["rel_position"]
    if quote and "[j" in quote:  # 日下旧闻考, public domain (S05); any other text in this field is not published
        out.append(fact("日下旧闻考", quote, "S05"))
    elif quote:
        out.append(fact("Where the text puts it", quote, src, private=True))
    note = r["notes"]
    head, plan = note, ""
    if " | plan:" in note:
        head, plan = note.split(" | plan:", 1)
    elif note.startswith("plan:"):
        head, plan = "", note[5:]
    head = clean_note(head)
    if head:
        out.append(fact("Note", head, src))
    if plan.strip():
        out.append(fact("Plan reader's note", plan.strip(), "S01", private=True))
    if r["read"]:
        out.append(fact("How it was read", r["read"], "S01", private=True))
    if r["plan_x"]:
        out.append(fact("Plan pixels", f"{r['plan_x']}, {r['plan_y']}", "S01", private=True))
    return out


def gate_facts(p):
    out = []
    names = " ".join(x for x in (p.get("name_zh"), p.get("name_pinyin")) if x)
    if names:
        out.append(fact("Name", names, p["sources"], p["confidence"]))
    out.append(fact("Type", "gate in the walls", p["sources"], p["confidence"]))
    if p.get("note"):
        out.append(fact("Note", p["note"], p["sources"]))
    if p.get("read"):
        out.append(fact("How it was read", p["read"], "S01", private=True))
    return out


def questions_of(book, pid, names):
    terms = [re.escape(pid)] + [re.escape(n) for n in names if len(n) >= 2 and "?" not in n]
    pattern = re.compile("(?<![A-Za-z0-9-])(?:" + "|".join(terms) + ")(?![0-9-])")
    return [{"id": q, "title": t} for q, (t, text) in sorted(book.questions.items(), key=lambda kv: int(kv[0][1:])) if pattern.search(text)]


def sources_of(book, cited):
    def order(s):
        m = re.match(r"S(\d+)$", s)
        return (0, int(m[1])) if m else (1, 0)
    return [book.sources.get(s, {"id": s, "text": "OpenStreetMap contributors, ODbL" if "OSM" in s else "", "licence": "", "url": ""}) for s in sorted(set(cited), key=lambda s: (order(s), s))]


def build(book, pid):
    if pid in book.gates:
        f = book.gates[pid]
        p = f["properties"]
        facts = gate_facts(p)
        kind, parent, children, sub, position = "gate", None, [], "Gate in the garden walls", f["geometry"]["coordinates"]
        cited = split_ids(p["sources"])
    else:
        r = book.rows[pid]
        facts = row_facts(r)
        compound = not r["parent_id"] and not pid.startswith("Z-")
        kind = "compound" if compound else "hall"
        parent = [r["parent_id"], book.short(r["parent_id"])] if r["parent_id"] else None
        children = [[c, book.short(c)] for c in book.children.get(pid, [])]
        sub = " · ".join(x for x in (r["name_en"], r["garden"]) if x)
        position = [round(float(r["lon"]), 6), round(float(r["lat"]), 6)] if r["lat"] else None
        cited = split_ids(r["sources"])
    boxes = book.boxes.get(pid, [])
    model = model_of(book, pid, kind)
    for b in boxes:
        cited += split_ids(b["sources"])
    if pid in book.gates or not book.rows[pid]["parent_id"]:
        cited += [s for b in book.by_parent.get(pid, [])[:1] for s in split_ids(b["sources"])]
    names = [book.short(pid)]
    if pid not in book.gates:
        names.append(book.rows[pid]["name_zh"])
    photos = [{"id": p["photo_id"], "title": p["title"], "date": p["date"], "creator": p["creator"], "archive": p["archive"], "source_url": p["source_url"]} for p in book.photos.get(pid, [])]
    has_box = bool(boxes) or (kind == "compound" and pid in book.by_parent)
    return {
        "id": pid, "kind": kind, "title": book.name(pid), "subtitle": sub, "parent": parent, "children": children, "position": position,
        "object": {"kind": "boxes", "count": len(boxes) or len(book.by_parent.get(pid, []))} if has_box else None,
        "model": model, "facts": facts, "photos": photos, "questions": questions_of(book, pid, names), "cited": cited,
    }


def read_notes(path):
    """The hand-written part of an existing page, whole. A page without the markers stops the script: it may hold someone's text."""
    if not path.exists():
        return f"## Notes\n\n{NOTES_HINT}\n"
    text = path.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise SystemExit(f"{path}: markers missing. Put the generated block back, or move the hand-written text and delete the file")
    return text.split(END, 1)[1].lstrip("\n")


def notes_html(hand, public):
    body = re.sub(r"^## Notes\s*", "", hand)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    if public:
        body = re.split(rf"^{re.escape(PRIVATE_LINE)}\s*$", body, flags=re.M)[0]
    else:
        body = re.sub(rf"^{re.escape(PRIVATE_LINE)}\s*$", "", body, flags=re.M)
    return md.render(body.strip()).strip() if body.strip() else ""


def page_markdown(page):
    pid = page["id"]
    lines = [START, "", f"# {pid}: {page['title']}", ""]
    if page["subtitle"]:
        lines += [page["subtitle"], ""]
    if page["object"]:
        lines += [f"**3D object:** {page['object']['count']} box{'es' if page['object']['count'] != 1 else ''}. Open it: `/reconstruction/3d.html?b={pid}`", ""]
    else:
        lines += ["**3D object:** none yet.", ""]
    if page["parent"]:
        lines += [f"**Part of:** {page['parent'][0]} {page['parent'][1]}".rstrip(), ""]
    lines += ["## What we know", ""]
    for f in page["facts"]:
        tag = " · ".join(x for x in (f["sources"].replace(";", ", "), f"confidence {f['confidence']}" if f["confidence"] else "") if x)
        private = " *(research copy, not public)*" if f.get("private") else ""
        lines.append(f"- **{f['label']}:** {f['value']}{f' ({tag})' if tag else ''}{private}")
    lines += ["", "## Our model now", "", page["model"]["line"], ""]
    if page["model"]["rows"]:
        lines += [f"- **{k}:** {v}" for k, v in page["model"]["rows"]] + [""]
    if page["children"]:
        lines += [f"## Inside it ({len(page['children'])})", ""] + [f"- {c} {n}".rstrip() for c, n in page["children"]] + [""]
    lines += [f"## Pictures ({len(page['photos'])})", ""]
    lines += [f"- {p['id']}: {p['title']} ({p['date']}). {p['source_url']}" for p in page["photos"]] or ["None in the catalog yet."]
    lines += ["", "## Open questions", ""]
    lines += [f"- {q['id']}: {q['title']}" for q in page["questions"]] or ["None that name it."]
    lines += ["", END, ""]
    return "\n".join(lines)


def panel_page(book, page, hand, public):
    out = {k: page[k] for k in ("id", "kind", "title", "subtitle", "object", "parent", "children", "position", "model", "photos", "questions")}
    out["notes_html"] = notes_html(hand, public)
    out["facts"] = [f for f in page["facts"] if not f.get("private")] if public else page["facts"]
    used = set(page["cited"])
    used |= {s for f in out["facts"] for s in split_ids(f["sources"])}
    used |= {s for s in re.findall(r"\bS\d+\b", json.dumps(out["model"], ensure_ascii=False) + out["notes_html"]) if s in book.sources}
    out["sources"] = sources_of(book, used)
    if public:
        assert_public(out)
    return out


def assert_public(page):
    pid = page["id"]
    assert set(page) <= PUBLIC_KEYS, (pid, set(page) - PUBLIC_KEYS)
    for f in page["facts"]:
        assert set(f) == PUBLIC_FACT_KEYS, (pid, f)
    for p in page["photos"]:
        assert set(p) <= PUBLIC_PHOTO_KEYS and p["source_url"].startswith("http"), (pid, p["id"])
    text = json.dumps(page, ensure_ascii=False)
    for word in ("/_local/", "raw/", "plan_x", "princeton_mosaic"):
        assert word not in text, (pid, word)


def write_if_changed(path, text):
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def existing_folders():
    """ID -> folder. An ID is a prefix of its children's (YM03 and YM03-11), so folders are matched by pattern, never by glob."""
    out = {}
    if PAGES.exists():
        for d in PAGES.iterdir():
            m = ID_RE.match(d.name + "-")
            if d.is_dir() and m:
                out[m[1]] = d
    return out


def write_folder(book, pid, page, folders):
    """Writes the page, keeping the folder of this ID whatever its slug was. Returns the hand-written part and the folder's name."""
    wanted = PAGES / f"{pid}-{book.slug_of(pid)}"
    old = folders.get(pid)
    if old and old != wanted:
        old.rename(wanted)
    path = wanted / "index.md"
    hand = read_notes(path)
    write_if_changed(path, page_markdown(page) + "\n" + hand)
    return hand, wanted.name


def main():
    book = Book()
    ids = sorted(book.rows) + sorted(book.gates, key=lambda g: int(g[1:]))
    PAGES.mkdir(exist_ok=True)
    folders = existing_folders()
    readme = ["# Buildings", "", "One folder per row of `research/buildings.csv` (compounds `YM..`, `CC..`, `XY..`, `QC..`, halls inside them, `Z-..` in no compound) and per gate (`G..`). Generated by `scripts/building_pages.py`; only the `## Notes` part of a page is yours, and it goes on the site unless it stands below a line holding only `%% private %%`.", "", "| ID | Name | Garden | Boxes | Assumed |", "|---|---|---|---:|---|"]
    written = set()
    for pid in ids:
        page = build(book, pid)
        hand, folder = write_folder(book, pid, page, folders)
        boxes = book.boxes.get(pid, [])
        garden = book.rows[pid]["garden"] if pid in book.rows else "walls"
        readme.append(f"| [{pid}]({folder}/index.md) | {page['title']} | {garden} | {len(boxes)} | {'yes' if any(b['assumed'] for b in boxes) else ''} |")
        write_if_changed(PUBLIC_OUT / f"{pid}.json", json.dumps(panel_page(book, page, hand, True), ensure_ascii=False, separators=(",", ":")))
        write_if_changed(LOCAL_OUT / f"{pid}.json", json.dumps(panel_page(book, page, hand, False), ensure_ascii=False, separators=(",", ":")))
        written.add(pid)
    write_if_changed(PAGES / "README.md", "\n".join(readme) + "\n")
    for folder in (PUBLIC_OUT, LOCAL_OUT):
        for f in folder.glob("*.json"):  # IDs that left the data: their JSON goes, a folder with notes never does
            if f.stem not in written:
                f.unlink()
    orphans = sorted(k for k in existing_folders() if k not in written)
    with_box = sum(1 for p in ids if book.boxes.get(p))
    missing = sorted({s for p in book.rows.values() for s in split_ids(p["sources"]) if s not in book.sources and s.startswith("S") and s[1:].isdigit()})
    print(f"{len(ids)} pages ({len(book.rows)} rows, {len(book.gates)} gates); {with_box} with a box of their own; sources cited and not in sources.md: {missing}")
    if orphans:
        print("Folders whose ID left the data (kept, they may hold notes):", orphans)


if __name__ == "__main__":
    main()
