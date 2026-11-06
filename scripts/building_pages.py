"""One page per building and compound, and what the 3D view's panel reads. Idempotent: a second run changes nothing.

  uv run python scripts/building_pages.py        (after boxes1860.py)

Reads research/buildings.csv, research/questions.md, research/sources.md, research/photos/catalog.csv, research/evidence/catalog.csv, research/reconstructions/catalog.csv, research/twins/catalog.csv, research/layers/walls_1860 (the gates), site/reconstruction/data/halls_1860.geojson, research/xiyanglou/views.csv and research/xiyanglou/<ID>-<slug>/dimensions.json (Xiyang Lou objects only: pictures by side, the Dimensions block, the link to the dossier), research/scenes/about.json and research/scenes/<ID>-<slug>/dimensions.json (every other scene or compound with a dossier, its halls inheriting it: the Dimensions block and the link to the dossier). Writes:
  research/buildings/<ID>-<slug>/index.md        every row of buildings.csv and every gate. The block between the markers is rewritten; `## Notes` below it is hand-written and never touched
  research/buildings/README.md                   the list of all of them
  site/reconstruction/data/buildings/<ID>.json   public: names, garden, dates, sources, confidence, the box, the evidence. No plan pixels, no plan readers' notes, no /_local/ or raw/ path (asserted). GARDEN-YM.json etc. hold what speaks for a whole garden, CLASS-grand_hall.json etc. the comparables for a class of hall
  research/raw/buildings/<ID>.json               local only (gitignored): the full version, with the plan readers' notes, for tools/serve_local.py

Notes go on the public site, except what stands below a line holding only `%% private %%`.

Evidence on a page, in this order: its own pictures, its own texts and drawings, the plan S01 as a link, a line saying what was searched and not found; then reconstructions by other people (modern interpretation, not evidence), surviving comparable buildings (not this building), and last what speaks for a set of buildings (the compound, or the nearest compound and the garden) by reference, so the panel fetches it from that page and nothing is written twice. A hall inherits its compound's reconstructions and comparables the same way; every page also refers to its garden and, for a hall, to its class, with `refs_only` set. A research-only picture, drawing or reconstruction is a link card, never an image or a copied text (asserted).
"""

import csv
import json
import math
import re
import unicodedata
from pathlib import Path

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "research/buildings"
SITE_DATA = ROOT / "site/reconstruction/data"
PUBLIC_OUT = SITE_DATA / "buildings"
LOCAL_OUT = ROOT / "research/raw/buildings"
LOCAL_CROPS = ROOT / "research/raw/plancrops"
START = "<!-- generated:start (scripts/building_pages.py): do not edit between these markers -->"
END = "<!-- generated:end -->"
NOTES_HINT = "<!-- Yours: regeneration never touches this part. It goes on the public site; what you write below a line holding only %% private %% stays in the research copy. -->"
PRIVATE_LINE = "%% private %%"
# What may stand in a public file. Anything else stops the script.
PUBLIC_KEYS = {"id", "kind", "title", "subtitle", "object", "parent", "children", "position", "model", "facts", "notes_html", "photos", "photos_inside", "evidence", "reconstructions", "twins", "plan_ref", "fallback", "searched", "questions", "sources", "dimensions", "dossier", "ways", "planting"}
PUBLIC_PLANT_KEYS = {"id", "plant", "latin", "en", "role", "place", "where", "season", "kind", "confidence", "sources", "quote", "drawn"}  # Round 12
PUBLIC_WAY_KEYS = {"id", "kind", "label", "other", "confidence", "assumed", "sources", "length_m"}
PUBLIC_ROUTE_KEYS = {"id", "name", "confidence", "sources", "stop"}
WAY_LABEL = {"imperial_road": "imperial road", "paved_way": "paved way 甬道", "courtyard_path": "court path", "service_path": "service path", "gallery": "covered gallery 游廊", "mountain_gallery": "climbing gallery 爬山廊", "causeway": "causeway", "dike": "dike 堤", "bridge_approach": "bridge approach", "steps": "steps 踏跺", "boat_route": "boat route", "landing": "landing 码头", "dock": "boat dock 船坞"}
PUBLIC_DIMENSION_KEYS = {"id", "part", "what", "label", "value", "err", "unit", "method", "confidence", "source", "locator", "snippet", "key"}
PUBLIC_FACT_KEYS = {"label", "value", "sources", "confidence"}
PUBLIC_PHOTO_KEYS = {"id", "title", "date", "creator", "archive", "source_url", "kind", "group", "conf", "why", "licence", "attribution", "also_shows", "camera_note", "image", "thumb", "link_only", "of", "side_group", "visible", "reliability"}
PUBLIC_RECON_KEYS = {"id", "title", "date", "creator", "archive", "source_url", "kind", "era", "conf", "why", "caveat", "status", "licence", "attribution", "image", "thumb", "link_only"}
PUBLIC_TWIN_KEYS = {"id", "name", "place", "relation", "standing", "confidence", "tells", "basis", "link", "status", "photos"}
PUBLIC_EVIDENCE_KEYS = {"id", "kind", "source_id", "title", "date", "locator", "link", "rights_class", "status", "conf", "excerpt_zh", "excerpt_other", "summary"}
GARDENS = {"Yuanming Yuan": "YM", "Changchun Yuan": "CC", "Xiyang Lou": "XY", "Qichun Yuan": "QC"}
CLASS_NAME = {"grand_hall": "a grand hall", "main_hall": "a main hall", "side_hall": "a side hall", "small_house": "a small house", "gallery": "a gallery", "pavilion_square": "a square pavilion", "pavilion_polygon": "a polygonal pavilion", "gate_hall": "a gate hall", "temple_hall": "a temple hall", "storeyed_hall": "a storeyed hall", "tower": "a tower"}
RELATION_WORD = {"copy of": "Ours was copied from it", "copied from ours": "It was copied from ours", "sister": "Sister: built together, same design", "same design family": "Same design family", "comparable": "Comparable: same court, era or type"}
GARDEN_NAME = {"YM": "圆明园 Yuanming Yuan", "CC": "长春园 Changchun Yuan", "XY": "西洋楼 Xiyang Lou", "QC": "绮春园 Qichun Yuan", "ALL": "the three gardens"}
ALSO_GARDEN = {"西洋楼": "XY", "西洋楼 set": "XY", "圆明园": "YM", "general plan": "ALL", "GARDEN:YM": "YM", "GARDEN:CC": "CC", "GARDEN:XY": "XY", "GARDEN:QC": "QC", "GARDEN:ALL": "ALL"}
NOT_GARDEN = {f"P{n:04d}" for n in (*range(155, 161), 153, 154, 281, 282, 283, 278, 286)}  # the debated Twelve Months (Q43), the scenes of October 1860: kept in the catalog, not repeated on every plain hall
SEARCHED_PICTURES = "the Forty Scenes album, its 1745 woodcuts, the Bertin gouaches and the 1887 lithograph; the 20 Xiyang Lou plates; ruin photographs on Commons, at Östasiatiska museet, the Slovene Ethnographic Museum, Historical Photographs of China, the Rijksmuseum, Wellcome and in NDL's albums of about 1900; today's photographs on Commons"
SEARCHED_TEXTS = {
    "YM": "日下旧闻考 j80-82, the Qianlong poems on Kanripo, 養吉齋叢錄, Malone 1934, the witnesses of 1860, what search indexes show of the Yangshi Lei drawings",
    "XY": "日下旧闻考 j83, the Qianlong poems on Kanripo, Delatour 1803, Malone 1934, the witnesses of 1860, what search indexes show of the Yangshi Lei drawings",
    "CC": "日下旧闻考 j83-84, the Qianlong poems on Kanripo, Malone 1934, what search indexes show of the Yangshi Lei drawings",
    "QC": "養吉齋叢錄 j18, modern studies of 绮春园, what search indexes show of the Yangshi Lei drawings; 日下旧闻考 does not cover this garden, and Jiaqing's 三十景 poems could not be reached (wishlist)",
    "ALL": "日下旧闻考, Malone 1934, the witnesses of 1860, what search indexes show of the Yangshi Lei drawings",
}
GARDEN_POEMS = 6
UNNAMED_LINE = "This block has no name on the plan or in the texts, so no source can be searched for it by name."
ID_RE = re.compile(r"^((?:YM|CC|XY|QC)\d+(?:-[A-Z]*\d+)?|Z-[A-Z]*\d+|G\d+)-")

md = MarkdownIt("commonmark", {"html": False}).disable("image")  # raw HTML comes out escaped

BASIS_LINE = {
    "plan": "On the block drawn on the Qing plan S01: position and frontage from the plan, heights and roof from the typology of its hall class, its form drawn by the hall kit. It will be updated as the research goes on.",
    "stated": "At a size stated in a source, on the block drawn on the Qing plan S01. Heights and roof from the typology where not stated; its form drawn by the hall kit.",
    "xiyang": "Simple massing of a European palace: position and footprint from the ruin, the plan or a survey, heights read from the plates of the 1780s (research/xiyanglou/boxes.csv). Not a detailed model yet; the figures and their methods are in the Dimensions block.",
    "layout": "Assumed: the plan shows this compound's place and no single hall, so a few boxes are laid out from the typology. Confidence C.",
    "default": "Assumed: a position is known and no block is drawn, so a small default box stands there. Confidence C.",
    "gate": "Assumed: a gate on the walls layer with no hall drawn at its point, so a small default box stands there. Confidence C.",
}
XY = ROOT / "research/xiyanglou"
SCENES = ROOT / "research/scenes"
XY_SIDE = {"S": "South façade", "N": "North façade", "E": "East façade", "W": "West façade", "roof": "Roof and fountains", "fountain": "Roof and fountains", "aerial": "Plans and views from above", "detail": "Details and fragments", "fragment": "Details and fragments"}
XY_FRONT = {"XY02": "E", "XY05": "W", "XY08": "W", "XY12": "W", "XY13": "W", "XY15": "W", "XY07": "N", "XY11": "N", "XY03": "N"}  # the side of the first plate comes first
KIT_ROOF = {"wd": "庑殿 hip", "xs": "歇山 hip-and-gable", "ys": "硬山 flush gable", "xu": "悬山 overhanging gable", "cj": "攒尖 pyramid"}
KIT_CLASS_LINE = "drawn from the typology of its hall class, not from a picture of this hall"
ROOF_WORD = {"hip_gable": "hip-and-gable 歇山", "hip": "hip 庑殿", "gable": "gable 硬山 or 悬山", "pyramid": "pyramid 攒尖"}
SHAPE_WORD = {"terrace": "terrace", "wall": "wall", "pool": "pool", "octagon": "octagon", "court": "sunken court", "basin": "round basin"}


def xy_group(view):
    """Which heading a Xiyang Lou picture stands under in the panel."""
    if not view:
        return "Other pictures"
    if view["state"] == "today":
        return "Ruins today"
    return XY_SIDE.get(view["side"], "Other pictures")


def era_group(p):
    """Which heading a picture stands under in the panel."""
    frm = int(p["date_from"]) if p["date_from"].isdigit() else None
    to = int(p["date_to"]) if p["date_to"].isdigit() else frm
    if p["kind"] == "photo":
        return "today" if ((to or 0) >= 1950 or "today's state" in p["notes"]) else "ruins"
    if to and to <= 1860:
        return "stood"
    if frm is None and p["kind"] in ("painting", "engraving"):
        return "stood"
    return "later"


def public_why(text):
    text = re.sub(r"^KEY PLATE for [^:]+:\s*", "", text or "")
    text = re.sub(r"\s*KEY PLATE for [^:]+:\s*", " ", text)
    text = re.sub(r"\s*BEST for [^.;]*[.;]?", "", text)
    text = re.sub(r"\s*use for layout, roof types\.?", "", text)
    return text.strip()


def clean_licence(text):
    text = re.sub(r"\{\{([^}]*)\}\}", r"\1", text or "")
    text = re.sub(r"Commons file tags?: ", "Commons: ", text)
    text = re.sub(r"Commons LicenseShortName ", "Commons: ", text)
    return re.sub(r"; BnF/Gallica: free non-commercial reuse with credit \(project rule, Gallica page not reachable from this server\)", "; BnF: free non-commercial reuse with credit", text)


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
        self.kit = json.load(open(SITE_DATA / "kit_1860.json", encoding="utf-8"))["halls"]  # Round 11: how the kit draws each box (scripts/kit1860.py)
        self.models = {}  # Round 13: detailed models, id and aliases -> summary (models/*/summary.json, published by publish_models)
        for path in sorted((ROOT / "models").glob("*/summary.json")):
            sm = json.load(open(path, encoding="utf-8"))
            sm["folder"] = path.parent
            for i in [sm["id"], *sm.get("aliases", [])]:
                self.models[i] = sm
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
        self.box_row = {p["id"]: p["building_id"] for f in fc["features"] for p in [f["properties"]]}
        self.ways, self.routes_at = load_ways(self.box_row, self.rows)
        self.planting, self.drawn, self.rocks = load_planting()
        self.children = {}
        for r in self.rows.values():
            if r["parent_id"]:
                self.children.setdefault(r["parent_id"], []).append(r["id"])
        self.photos, self.evidence, self.recons, self.twins, self.twin_photos = {}, {}, {}, {}, {}
        for p in rd("research/photos/catalog.csv"):
            if not p["source_url"].startswith("http"):
                continue
            if p["relation"].startswith("twin:"):  # shows another building: it stands beside its pairing, never among the pictures of ours
                for tid in split_ids(p["relation"][5:]):
                    self.twin_photos.setdefault(tid, []).append(p)
                continue
            for item in split_ids(p["shows"]):
                pid, conf = item.split(":")
                self.photos.setdefault(pid, []).append((p, conf))
            tag = ALSO_GARDEN.get(p["also_shows"].strip())
            if tag and not p["shows"] and p["photo_id"] not in NOT_GARDEN:
                self.photos.setdefault(f"GARDEN-{tag}", []).append((p, "likely"))
        for e in rd("research/evidence/catalog.csv"):
            for item in split_ids(e["shows"]):
                bits = item.split(":")
                pid, conf = (f"GARDEN-{bits[1]}", bits[2] if len(bits) > 2 else "likely") if bits[0] == "GARDEN" else (bits[0], bits[1])
                self.evidence.setdefault(pid, []).append((e, conf))
        for r in rd("research/reconstructions/catalog.csv"):
            for item in split_ids(r["shows"]):
                bits = item.split(":")
                pid, conf = (f"GARDEN-{bits[1]}", bits[2]) if bits[0] == "GARDEN" else (bits[0], bits[1])
                self.recons.setdefault(pid, []).append((r, conf))
        for t in rd("research/twins/catalog.csv"):
            self.twins.setdefault(t["object_id"].replace(":", "-"), []).append(t)
        self.xy_views = {(v["photo_id"], v["id"]): v for v in rd("research/xiyanglou/views.csv")}
        self.xy_sheets = {}
        for sheet in XY.glob("XY*/dimensions.json"):
            data = json.load(open(sheet, encoding="utf-8"))
            self.xy_sheets[data["id"]] = data
        self.scene_about = {k: v for k, v in json.load(open(SCENES / "about.json", encoding="utf-8")).items() if not k.startswith("_")}
        self.scene_sheets = {}
        for sheet in SCENES.glob("*/dimensions.json"):
            data = json.load(open(sheet, encoding="utf-8"))
            if data["id"] in self.scene_about:
                self.scene_sheets[data["id"]] = data
        self.tops = [r for r in self.rows.values() if not r["parent_id"] and not r["id"].startswith("Z-") and r["lat"]]
        self.gate_garden = {g: self.nearest(*reversed(f["geometry"]["coordinates"]), [])[0]["garden"] for g, f in self.gates.items()}

    def nearest(self, lat, lon, skip):
        """The named compound nearest to a point: the set of buildings a block in no compound can lean on. Compounds with nothing of their own are skipped."""
        def dist(r):
            return math.hypot((float(r["lat"]) - lat) * 111000, (float(r["lon"]) - lon) * 85000)
        named = [r for r in self.tops if r["id"] not in skip and (r["name_zh"] or r["name_on_plan"]) and "?" not in (r["name_zh"] or r["name_on_plan"]) and (self.photos.get(r["id"]) or self.evidence.get(r["id"]))]
        best = min(named, key=dist)
        return best, dist(best)

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


def kit_row(k):
    """Round 11: how the hall kit or the stone kit draws this box, and where its form comes from."""
    if not k or k["k"] == "shape":
        return None
    if k["k"] in ("stone", "stoneshape"):
        return ["Drawn", "by the stone kit: base, pilasters, arched openings, entablature, balustrade and a glazed roof, as the plates of the 1780s show such fronts; the kit's reading, C, not a detailed model"]
    n = len(k["b"])
    porch = ["all round"] if k.get("ps") else [w for w, key in (("front", "pf"), ("back", "pb")) if k.get(key)]
    bits = [f"{n} bay{'s' if n > 1 else ''}" + (", the middle widest" if n > 2 else ""), (f"a porch {' and '.join(porch)}" if porch else ""), f"steps on the {', '.join(k['st'])}" if k.get("st") else "",
            KIT_ROOF[k["rf"]] + (" with a rolled ridge 卷棚" if k.get("rl") else "") + (", double eaves 重檐" if k.get("db") else "") + f", {k['t']} tile", "bracket sets 斗拱 as a painted band" if k.get("bd") == "br" else "a painted beam under the eave"]
    if k["src"] == "class":
        how = KIT_CLASS_LINE + " (assumed, C)"
    elif k["src"] == "dossier":
        word = {"platform_h": "platform", "column_h": "column", "height_ridge": "ridge", "edge": "platform edge 下出", "porch": "porch", "bays": "bays", "roof": "roof read", "tiles": "tiles read", "stair": "stairs", "bay_width": "bay"}
        how = "from its own figures and readings where the dossier gives them (" + "; ".join(f"{word.get(a, a)}: {b}" for a, b in k.get("fig", {}).items()) + "), the rest from the typology of its hall class"
    else:
        how = "from the size a source states, the rest from the typology of its hall class"
    return ["Drawn", "by the hall kit: " + ", ".join(x for x in bits if x) + ". " + how[0].upper() + how[1:] + "."]


def box_rows(boxes, kit=None):
    rows = []
    kit = kit or {}
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
        if b.get("figures"):
            rows.append(["Own figures", "; ".join(f"{w.replace('_h', '').replace('height_', '')} {v[0]:g} m ({v[1]}, {v[2]}, {v[3]})" for w, v in b["figures"].items())])
        kr = kit_row(kit.get(b["id"]))
        if kr:
            rows.append(kr)
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
        ks = [kit.get(b["id"]) for b in boxes if kit.get(b["id"]) and kit[b["id"]]["k"] != "shape"]
        if ks:
            stone = all(k["k"] in ("stone", "stoneshape") for k in ks)
            cls = sum(k["src"] == "class" for k in ks)
            rows.append(["Drawn", "by the stone kit, the kit's reading of the plates, C, not a detailed model" if stone else f"by the hall kit; {cls} of {len(ks)} {KIT_CLASS_LINE.replace('its hall class', 'their hall class').replace('this hall', 'these halls')}"])
        rows.append(["Confidence", " and ".join(sorted({b["confidence"] for b in boxes})) + (", all assumed" if all(b["assumed"] for b in boxes) else ", some assumed" if any(b["assumed"] for b in boxes) else "")])
    return rows


def model_of(book, pid, kind):
    sm = book.models.get(pid)
    if sm:
        return {"line": sm["line"], "rows": sm["rows"], "detailed": sm["id"]}
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
    return {"line": BASIS_LINE[boxes[0]["basis"]], "rows": box_rows(boxes, book.kit)}


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
    if r["size_lead"]:
        out.append(fact("Lead on its size, from a modern study, not used in the model", r["size_lead"], "", "B"))
    if r["storeys"]:
        out.append(fact("Storeys", r["storeys"], src))
    if r["roof"]:
        out.append(fact("Roof", r["roof"], src))
    if r["roof_tiles"]:
        out.append(fact("Tiles", r["roof_tiles"], src))
    quote = r["rel_position"]
    if quote and "[j" not in quote:  # 日下旧闻考 (S05) stands in the evidence; any other text in this field is not published
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


def photo_entry(p, conf, public, of=None):
    pid = p["photo_id"]
    out = {"id": pid, "title": p["title"], "date": p["date"], "creator": p["creator"], "archive": p["archive"], "source_url": p["source_url"], "kind": p["kind"], "group": era_group(p), "conf": conf, "why": public_why(p["why"]), "attribution": p["attribution"], "licence": clean_licence(p["licence"])}
    if of:
        out["of"] = of
    if p["also_shows"] and not p["also_shows"].startswith("GARDEN"):
        out["also_shows"] = p["also_shows"]
    if p["camera_note"] and p["camera_lat"]:
        out["camera_note"] = p["camera_note"]
    if p["rights_class"] == "free" and p["file"] and p["shows"]:
        out["image"], out["thumb"] = f"photos/{pid}.jpg", f"photos/{pid}_t.jpg"
    elif p["rights_class"] != "free":
        out["link_only"] = True
        if not public and p["file"]:  # the research copy, on the research machine only
            out["image"] = out["thumb"] = f"/_local/photos/{pid}.jpg"
    return out


def recon_entry(r, conf, public):
    """Shaped like a picture, so the panel draws it the same way."""
    rid = r["recon_id"]
    out = {"id": rid, "title": r["title"], "date": r["year"], "creator": r["author"], "archive": r["institution"], "source_url": r["link"], "kind": r["kind"], "era": r["era"], "conf": conf, "why": r["method_stated"] or r["summary_en"], "caveat": r["caveat"], "status": r["status"], "licence": r["licence"], "attribution": r["attribution"]}
    if r["rights_class"] == "free" and r["local_copy"]:
        out["image"], out["thumb"] = f"photos/{rid}.jpg", f"photos/{rid}_t.jpg"
    elif r["rights_class"] != "free":
        out["link_only"] = True
        if not public and r["local_copy"]:  # the research copy, on the research machine only
            out["image"] = out["thumb"] = f"/_local/reconstructions/{rid}.jpg"
    return out


def twin_entry(book, t, public):
    name = " ".join(x for x in (t["twin_name_zh"], t["twin_name_en"]) if x)
    return {"id": t["twin_id"], "name": name, "place": t["twin_place"], "relation": RELATION_WORD[t["relation"]], "standing": t["still_standing"], "confidence": t["confidence"], "tells": t["what_it_tells"], "basis": t["evidence_for_relation"], "link": t["link"], "status": t["status"], "photos": [photo_entry(p, split_ids(p["shows"])[0].rsplit(":", 1)[1], public) for p in book.twin_photos.get(t["twin_id"], [])]}


def evidence_entry(e, conf):
    return {"id": e["evidence_id"], "kind": e["kind"], "source_id": e["source_id"], "title": e["title"], "date": e["date"], "locator": e["locator"], "link": e["link"], "rights_class": e["rights_class"], "status": e["status"], "conf": conf, "excerpt_zh": e["excerpt_zh"], "excerpt_other": e["excerpt_other"], "summary": e["summary_en"]}


GROUP_ORDER = {"stood": 0, "later": 1, "ruins": 2, "today": 3}
KIND_ORDER = {"text": 0, "poem": 0, "description": 2, "drawing": 3, "plan": 4, "archaeology": 5, "reconstruction": 6}
CONF_ORDER = {"sure": 0, "likely": 1, "guess": 2}


def sort_photos(items):
    return sorted(items, key=lambda x: (CONF_ORDER[x[1]] > 1, GROUP_ORDER[era_group(x[0])], x[0]["rights_class"] != "free", CONF_ORDER[x[1]], x[0]["photo_id"]))


RECON_KIND_ORDER = {"render": 0, "aerial view": 0, "3D model": 1, "drawing": 2, "physical model": 3, "video": 4, "AR/VR": 4, "paper figure": 5, "painting": 6, "game or community build": 9}


def sort_recons(items):
    # images and firm ties first, a search-index entry after a page read, community builds and AI-made last
    def year(text):
        m = re.search(r"\b(1[0-9]{3}|20[0-9]{2})\b", text or "")
        return int(m[1]) if m else 9999
    return sorted(items, key=lambda x: (CONF_ORDER[x[1]] > 1, x[0]["caveat"].startswith(("Made with AI", "A community")), not (x[0]["rights_class"] == "free" and x[0]["local_copy"]), x[0]["status"] != "viewed", RECON_KIND_ORDER.get(x[0]["kind"], 7), year(x[0]["year"]), x[0]["recon_id"]))


def sort_twins(items):
    # a stated relation first, then by grade; one with a picture before one without
    rel = {"copy of": 0, "copied from ours": 1, "sister": 1, "same design family": 2, "comparable": 3}
    return sorted(items, key=lambda t: (rel[t["relation"]], t["confidence"], t["twin_id"]))


def sort_evidence(items):
    # the 1780s account and the 1744 poem first, then the rest by year; a search-index entry last in its kind
    def rank(source):
        return 0 if source in ("S05", "S40") else 2 if source in ("S360", "S361") else 1
    def year(text):
        m = re.search(r"\b(1[0-9]{3}|20[0-9]{2})\b", text or "")
        return int(m[1]) if m else 9999
    return sorted(items, key=lambda x: (KIND_ORDER.get(x[0]["kind"], 9), x[0]["rights_class"] != "free" and x[0]["kind"] == "description", x[0]["status"] != "viewed", rank(x[0]["source_id"]), CONF_ORDER[x[1]], year(x[0]["date"]), x[0]["evidence_id"]))


def plan_ref(book, pid):
    """The plan as a link: it stays off the site until Tomasz decides (Q6)."""
    url = "https://artmuseum.princeton.edu/collections/objects/138657"
    if pid in book.gates:
        return {"text": "Drawn as a gate on the plan of the gardens (S01).", "link": url, "source_id": "S01"}
    r = book.rows[pid]
    if not r["plan_x"]:
        return None
    label = r["name_on_plan"]
    bays = f", {r['bays_plan']} cells" if r["bays_plan"] else ""
    if label and "?" not in label:
        text = f"Drawn on the plan of the gardens (S01), labelled {label}{bays}."
    elif label:
        text = f"Drawn on the plan of the gardens (S01), labelled {label} (? marks an unread character){bays}."
    elif r["parent_id"] or r["id"].startswith("Z-"):
        text = f"Drawn on the plan of the gardens (S01) with no label{bays}: a building stood here, its name unknown."
    else:
        text = "Its place is drawn on the plan of the gardens (S01), with no name written."
    return {"text": text, "link": url, "source_id": "S01"}


def fallback_of(book, pid, kind):
    """What speaks for the set of buildings this one belongs to: [{kind, id, name}], for the panel to fetch."""
    if kind == "gate":
        tag = GARDENS.get(book.gate_garden[pid], "ALL")
        return [{"kind": "garden", "id": f"GARDEN-{tag}", "name": GARDEN_NAME[tag]}]
    r = book.rows[pid]
    tag = GARDENS.get(r["garden"], "ALL")
    garden = {"kind": "garden", "id": f"GARDEN-{tag}", "name": GARDEN_NAME[tag]}
    if r["parent_id"]:
        out = [{"kind": "compound", "id": r["parent_id"], "name": book.short(r["parent_id"])}]
        if not (book.photos.get(r["parent_id"]) or book.evidence.get(r["parent_id"])):
            out.append(garden)
        return out
    if book.photos.get(pid):
        return []
    if not r["lat"]:
        return [garden]
    if book.evidence.get(pid):
        return [garden]
    near, metres = book.nearest(float(r["lat"]), float(r["lon"]), [pid])
    return [{"kind": "nearest", "id": near["id"], "name": book.short(near["id"]), "metres": round(metres, -1)}, garden]


def refs_of(book, pid, kind, fallback):
    """Where else its reconstructions and comparables come from: the garden, unless the fallback has it already, and the class of hall."""
    out = []
    if pid in book.gates:
        return out
    r = book.rows[pid]
    tag = GARDENS.get(r["garden"], "ALL")
    if not any(f["kind"] == "garden" for f in fallback):
        out.append({"kind": "garden", "id": f"GARDEN-{tag}", "name": GARDEN_NAME[tag], "refs_only": True})
    if kind != "compound" and r["hall_class"] in CLASS_NAME:
        out.append({"kind": "class", "id": f"CLASS-{r['hall_class']}", "name": CLASS_NAME[r["hall_class"]], "refs_only": True})
    return out


def searched_line(book, pid, kind, photos, evidence):
    if pid in book.gates:
        named, tag = bool(book.short(pid)), GARDENS.get(book.gate_garden[pid], "ALL")
    else:
        r = book.rows[pid]
        named, tag = bool(r["name_zh"] or (r["name_on_plan"] and "?" not in r["name_on_plan"])), GARDENS.get(r["garden"], "ALL")
    own_pic = bool(photos)
    if own_pic and evidence:
        return ""
    if not named:
        return UNNAMED_LINE
    bits = []
    if not own_pic:
        bits.append(f"No picture of it found in {SEARCHED_PICTURES}.")
    if not evidence:
        bits.append(f"No text or drawing names it in {SEARCHED_TEXTS[tag]}.")
    return " ".join(bits)


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
    photos = sort_photos(book.photos.get(pid, []))
    evidence = [evidence_entry(e, c) for e, c in sort_evidence(book.evidence.get(pid, []))]
    cited += [s for e in evidence for s in split_ids(e["source_id"])]
    cited += [s for p, _ in photos for s in split_ids(p["source_id"])]
    inside = []
    seen = {p["photo_id"] for p, _ in photos}
    for c in book.children.get(pid, []):
        for p, conf in book.photos.get(c, []):
            if p["photo_id"] not in seen and p["rights_class"] == "free":
                seen.add(p["photo_id"])
                inside.append((p, conf, c))
    has_box = bool(boxes) or (kind == "compound" and pid in book.by_parent)
    fallback = fallback_of(book, pid, kind)
    return {
        "id": pid, "kind": kind, "title": book.name(pid), "subtitle": sub, "parent": parent, "children": children, "position": position,
        "object": {"kind": "boxes", "count": len(boxes) or len(book.by_parent.get(pid, []))} if has_box else None,
        "model": model, "facts": facts, "photos_rows": photos, "inside_rows": inside, "evidence": evidence, "recon_rows": sort_recons(book.recons.get(pid, [])), "twin_rows": sort_twins(book.twins.get(pid, [])), "plan_ref": plan_ref(book, pid), "fallback": fallback + refs_of(book, pid, kind, fallback),
        "searched": searched_line(book, pid, kind, photos, evidence), "questions": questions_of(book, pid, names), "cited": cited,
    }


def build_garden(book, tag):
    """What speaks for a whole garden. The garden's own rows, then those for all three."""
    pid = f"GARDEN-{tag}"
    photos = sort_photos(book.photos.get(pid, []) + (book.photos.get("GARDEN-ALL", []) if tag != "ALL" else []))
    rows = book.evidence.get(pid, []) + (book.evidence.get("GARDEN-ALL", []) if tag != "ALL" else [])
    poems = sort_evidence([x for x in rows if x[0]["kind"] == "poem"])[:GARDEN_POEMS]  # this page is fetched for every plain hall: a sample, the rest stay in the catalog
    evidence = [evidence_entry(e, c) for e, c in sort_evidence([x for x in rows if x[0]["kind"] != "poem"] + poems)]
    cited = [s for e in evidence for s in split_ids(e["source_id"])] + [s for p, _ in photos for s in split_ids(p["source_id"])]
    recons = sort_recons(book.recons.get(pid, []) + (book.recons.get("GARDEN-ALL", []) if tag != "ALL" else []))
    twins = sort_twins(book.twins.get(pid, []) + (book.twins.get("GARDEN-ALL", []) if tag != "ALL" else []))
    return {"id": pid, "kind": "garden", "title": GARDEN_NAME[tag], "subtitle": "", "parent": None, "children": [], "position": None, "object": None, "model": None, "facts": [], "photos_rows": photos, "inside_rows": [], "evidence": evidence, "recon_rows": recons, "twin_rows": twins, "plan_ref": None, "fallback": [], "searched": "", "questions": [], "cited": cited}


def build_class(book, cls):
    """Standing buildings comparable to a class of hall: a typology reference, fetched by every hall of that class."""
    pid = f"CLASS-{cls}"
    return {"id": pid, "kind": "class", "title": f"Comparable buildings for {CLASS_NAME[cls]}", "subtitle": "", "parent": None, "children": [], "position": None, "object": None, "model": None, "facts": [], "photos_rows": [], "inside_rows": [], "evidence": [], "recon_rows": [], "twin_rows": sort_twins(book.twins.get(pid, [])), "plan_ref": None, "fallback": [], "searched": "", "questions": [], "cited": []}


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


def page_markdown(page, book_twin_photos=lambda tid: []):
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
    lines += [f"## Pictures ({len(page['photos_rows'])})", ""]
    for p, conf in page["photos_rows"]:
        rights = "" if p["rights_class"] == "free" else " Research-only: link card."
        lines.append(f"- **{p['photo_id']}** ({conf}): {p['title']} ({p['date']}). {p['source_url']}{rights}")
        if p["file"]:
            lines.append(f"\n  ![{p['photo_id']}](../../{p['file'].removeprefix('research/')})\n")
    if not page["photos_rows"]:
        lines.append("None of its own.")
    if page["inside_rows"]:
        lines += ["", f"Of its halls: {', '.join(f'{p['photo_id']} ({c})' for p, _, c in page['inside_rows'])}."]
    lines += ["", f"## Texts and drawings ({len(page['evidence'])})", ""]
    for e in page["evidence"]:
        where = " · ".join(x for x in (e["date"], e["locator"], e["source_id"]) if x)
        lines.append(f"- **{e['id']}** ({e['kind']}, {e['conf']}{', search index only' if e['status'] != 'viewed' else ''}): {e['title']}. {where}. {e['link']}")
        if e["excerpt_zh"]:
            lines.append(f"  > {e['excerpt_zh'].replace(chr(10), ' ')}")
        if e["excerpt_other"]:
            lines.append(f"  > {e['excerpt_other'].replace(chr(10), ' ')}")
        if e["summary"]:
            lines.append(f"  {e['summary']}")
    if not page["evidence"]:
        lines.append("None of its own.")
    if page["plan_ref"]:
        lines += ["", f"**On the plan:** {page['plan_ref']['text']} {page['plan_ref']['link']}"]
    lines += ["", f"## Reconstructions by others ({len(page['recon_rows'])})", "", "Modern interpretation, not evidence."] if page["recon_rows"] else []
    for r, conf in page["recon_rows"]:
        who = ", ".join(x for x in (r["author"], r["institution"], r["year"]) if x)
        rights = "" if r["rights_class"] == "free" else " Research-only: link card."
        lines.append(f"- **{r['recon_id']}** ({r['kind']}, {conf}{', search index only' if r['status'] != 'viewed' else ''}): {r['title']}. {who}. {r['link']}{rights}")
    lines += ["", f"## Surviving comparable buildings, not this building ({len(page['twin_rows'])})", ""] if page["twin_rows"] else []
    for t in page["twin_rows"]:
        lines.append(f"- **{t['twin_id']}** {t['twin_name_zh']} {t['twin_name_en']}, {t['twin_place']}. {RELATION_WORD[t['relation']]}, confidence {t['confidence']}, standing: {t['still_standing']}. {t['what_it_tells']} Basis: {t['evidence_for_relation']} {t['link']}")
        lines += [f"  - {p['photo_id']}: {p['title']}. {p['source_url']}" for p in book_twin_photos(t["twin_id"])]
    if page["fallback"]:
        lines += ["", "## Evidence for the set of buildings", ""]
        for f in page["fallback"]:
            lines.append(f"- {fallback_heading(f, page)}: see {f['id']}")
    if page["searched"]:
        lines += ["", f"**Searched and not found:** {page['searched']}"]
    lines += ["", "## Open questions", ""]
    lines += [f"- {q['id']}: {q['title']}" for q in page["questions"]] or ["None that name it."]
    lines += ["", END, ""]
    return "\n".join(lines)


def fallback_heading(f, page):
    if f["kind"] == "class":
        return f"Standing buildings comparable to {f['name']} (not this building)"
    if f.get("refs_only"):
        return f"Reconstructions and comparables for the whole garden, {f['name']}"
    bare = not page["photos_rows"]
    what = "picture of this hall" if page["kind"] == "hall" else "picture of this compound" if page["kind"] == "compound" else "picture of this gate"
    if f["kind"] == "compound":
        return f"Evidence for the whole compound {f['name']}" + (f" (no {what} found)" if bare else "")
    if f["kind"] == "nearest":
        return f"Evidence for the nearest named compound, {f['name']}, about {f['metres']:g} m away" + (f" (no {what} found)" if bare else "")
    return f"Evidence for the whole garden, {f['name']}" + (f" (no {what} found)" if bare else "")


def panel_page(book, page, hand, public):
    out = {k: page[k] for k in ("id", "kind", "title", "subtitle", "object", "parent", "children", "position", "model", "questions", "evidence", "searched")}
    out["photos"] = xy_photos(book, page, public) if page["id"].startswith("XY") else [photo_entry(p, c, public) for p, c in page["photos_rows"]]
    out["reconstructions"] = [recon_entry(r, c, public) for r, c in page["recon_rows"]]
    out["twins"] = [twin_entry(book, t, public) for t in page["twin_rows"]]
    out["photos_inside"] = [photo_entry(p, c, public, of=[o, book.short(o)]) for p, c, o in page["inside_rows"]]
    out["plan_ref"] = dict(page["plan_ref"]) if page["plan_ref"] else None
    if not public and out["plan_ref"] and (LOCAL_CROPS / f"{page['id']}.jpg").exists():
        out["plan_ref"]["image"] = f"/_local/plancrops/{page['id']}.jpg"
    out["fallback"] = [{**f, "heading": fallback_heading(f, page)} for f in page["fallback"]]
    out["notes_html"] = notes_html(hand, public)
    out["facts"] = [f for f in page["facts"] if not f.get("private")] if public else page["facts"]
    used = set(page["cited"])
    used |= {s for f in out["facts"] for s in split_ids(f["sources"])}
    used |= {s for s in re.findall(r"\bS\d+\b", json.dumps(out["model"], ensure_ascii=False) + out["notes_html"] + " ".join(t["basis"] for t in out["twins"])) if s in book.sources}
    if page["kind"] not in ("garden", "class"):  # those two are fetched for every plain hall: the rows carry their own links
        used |= {s for r, _ in page["recon_rows"] for s in split_ids(r["source_id"]) if s in book.sources}
    ways = ways_of(book, page)
    if ways:
        out["ways"] = ways
        used |= {s for w in ways.get("reached", []) + ways.get("routes", []) for s in split_ids(w["sources"]) if s in book.sources}
    planting = planting_of(book, page)
    if planting:
        out["planting"] = planting
        used |= {s for k in ("sourced", "not_drawn", "rejected", "rocks") for r in planting.get(k, []) for s in split_ids(r["sources"]) if s in book.sources}
    out["sources"] = sources_of(book, used)
    xy_extras(book, page, out)
    if public:
        assert_public(out)
    return out


def xy_view(book, photo_id, pid):
    return book.xy_views.get((photo_id, pid)) or book.xy_views.get((photo_id, pid.split("-")[0]))


def xy_photos(book, page, public):
    """Pictures by side: the front's first, the other sides, roof and fountains, details, then the ruins today. Inside each heading the engraving first."""
    pid, top = page["id"], page["id"].split("-")[0]
    front = XY_SIDE[XY_FRONT.get(top, "S")]
    rank = {"South façade": 1, "North façade": 2, "East façade": 3, "West façade": 4, "Roof and fountains": 5, "Plans and views from above": 6, "Details and fragments": 7, "Other pictures": 8, "Ruins today": 9, front: 0}
    out = []
    for p, conf in page["photos_rows"]:
        view = xy_view(book, p["photo_id"], pid)
        entry = photo_entry(p, conf, public)
        entry["side_group"] = xy_group(view)
        if view:
            entry["visible"], entry["reliability"] = view["visible_part"], view["reliability"]
        out.append(entry)
    state = {"high": 0, "medium": 1, "low": 2}
    out.sort(key=lambda e: (rank[e["side_group"]], e["conf"] == "guess", e["kind"] != "engraving", state.get(e.get("reliability"), 3), e["id"]))
    return out


def xy_extras(book, page, out):
    """A Xiyang Lou page or a page of a scene with a dossier: its figures, and the way to the dossier. A hall carries its own figures; the scene's come through the fallback."""
    pid = page["id"]
    if pid == "GARDEN-XY":
        out["dossier"] = {"href": "../xiyanglou/", "label": "Read the full Xiyang Lou dossier"}
    if pid in ("GARDEN-YM", "GARDEN-CC", "GARDEN-QC", "GARDEN-ALL"):
        out["dossier"] = {"href": "../scenes/", "label": "Read the scene dossiers"}
    top = pid.split("-")[0]
    if top in book.scene_sheets:
        about = book.scene_about[top]
        public = about.get("public")
        out["dossier"] = {"href": f"../scenes/{top}/" if public else f"../scenes/#{top}", "label": f"Read the dossier of {about['zh']} {about['pinyin']}" if public else f"Read the summary of {about['zh']} {about['pinyin']} among the scene dossiers"}
        figures = book.scene_sheets[top]["figures"]
        mine = figures if pid == top else [d for d in figures if d["id"] == pid]
        if mine:
            out["dimensions"] = mine
        return
    if not pid.startswith("XY"):
        return
    out["dossier"] = {"href": f"../xiyanglou/#{top}", "label": "Read the full Xiyang Lou dossier"}
    sheet = book.xy_sheets.get(top)
    if sheet:
        out["dimensions"] = sheet["figures"] if pid == top else [d for d in sheet["figures"] if d["id"] == pid]


def load_ways(box_row, rows):
    """Round 9: research/layers/paths_1860, landings_1860 and routes_1860 by the rows, gates and bridges they touch."""
    ways, routes_at = {}, {}
    names = {}
    for name in ("paths_1860", "landings_1860", "bridges_1860", "walls_1860"):
        f = ROOT / "research/layers" / f"{name}.geojson"
        if f.exists():
            for x in json.load(open(f, encoding="utf-8"))["features"]:
                q = x["properties"]
                names[q["id"]] = q.get("name_zh") or WAY_LABEL.get(q.get("kind", ""), "") or q["id"]
    bridge_row = {}
    f = ROOT / "research/layers/bridges_1860.geojson"
    for x in json.load(open(f, encoding="utf-8"))["features"]:
        if x["properties"].get("building_id"):
            bridge_row[x["properties"]["id"]] = x["properties"]["building_id"]

    def touched(ident, at):
        out = set()
        for v in (ident or "", (at or "").split(":")[0]):
            v = v.strip()
            if not v:
                continue
            if v in box_row:
                out.add(box_row[v])
            elif v in bridge_row:
                out |= {v, bridge_row[v]}
            elif v in rows or v.startswith("G"):
                out.add(v)
        return out

    def label(ident):
        if not ident:
            return "another way"
        if ident in rows:
            r = rows[ident]
            return r["name_zh"] or r["name_on_plan"] or ident
        return names.get(ident, ident)

    f = ROOT / "research/layers/paths_1860.geojson"
    if not f.exists():
        return ways, routes_at
    for x in json.load(open(f, encoding="utf-8"))["features"]:
        q = x["properties"]
        ends = [(q["from_id"], q["from_at"]), (q["to_id"], q["to_at"])]
        for i, (ident, at) in enumerate(ends):
            other = ends[1 - i]
            for row in touched(ident, at):
                ways.setdefault(row, []).append({"id": q["id"], "kind": q["kind"], "label": WAY_LABEL[q["kind"]], "other": label(other[0] or box_row.get((other[1] or "").split(":")[0], "")),
                                                 "confidence": q["confidence"], "assumed": q["assumed"], "sources": q["sources"], "length_m": q["length_m"]})
    for x in json.load(open(ROOT / "research/layers/landings_1860.geojson", encoding="utf-8"))["features"]:
        q = x["properties"]
        for row in split_ids(q["serves"]):
            if row in rows:
                ways.setdefault(row, []).append({"id": q["id"], "kind": q["kind"], "label": WAY_LABEL[q["kind"]], "other": q["water"] or "the water", "confidence": q["confidence"], "assumed": q["assumed"], "sources": q["sources"], "length_m": 0})
    for x in json.load(open(ROOT / "research/layers/routes_1860.geojson", encoding="utf-8"))["features"]:
        q = x["properties"]
        hit = {s["id"]: s["name"] for s in q["stops"]}
        for v in q["via"]:
            if v in box_row:
                hit.setdefault(box_row[v], "")
        for row in hit:
            for r in ([row] if row in rows else []) + ([rows[row]["parent_id"]] if row in rows and rows[row]["parent_id"] else []):
                lst = routes_at.setdefault(r, [])
                if not any(e["id"] == q["id"] for e in lst):
                    lst.append({"id": q["id"], "name": q["name_en"], "confidence": q["confidence"], "sources": q["sources"], "stop": row in {s["id"] for s in q["stops"]} and r == row})
    for lst in ways.values():
        lst.sort(key=lambda w: ({"A": 0, "B": 1, "C": 2}[w["confidence"]], w["id"]))
        seen = set()
        lst[:] = [w for w in lst if not (w["id"] in seen or seen.add(w["id"]))]
    return ways, routes_at


PLACE_WORDS = {"scene": "in the scene", "north": "north side", "south": "south side", "east": "east side", "west": "west side", "front_court": "front court", "rear_court": "rear court",
               "court": "in the courts", "around_hall": "beside a hall", "shore": "at the shore", "island": "on the island", "hill": "on the hills", "hill_foot": "at the foot of the hills",
               "dike": "on the dike", "along_way": "along the way", "pond": "on the water", "lake_edge": "at the water's edge", "bridge": "by the bridge", "rockery": "by the rocks",
               "field": "in the fields", "outside_wall": "beyond the walls"}


def load_planting():
    """Round 12: research/greens/species.csv by scene, what the view drew for each row (data/greens_1860.geojson), the rockeries by scene."""
    rows = {}
    for r in csv.DictReader(open(ROOT / "research/greens/species.csv", encoding="utf-8")):
        rows.setdefault(r["scene_id"], []).append(r)
    drawn, rocks = {}, {}
    path = SITE_DATA / "greens_1860.geojson"
    if path.exists():
        for f in json.load(open(path, encoding="utf-8"))["features"]:
            p = f["properties"]
            if p["kind"] == "rockery":
                rocks.setdefault(p["scene"].split("-")[0], []).append(p)
                continue
            for rid in split_ids(p["rows"]):
                d = drawn.setdefault(rid, {"count": 0, "extent": p["extent_confidence"], "fill": p["assumed"]})
                d["count"] += p["count"]
    return rows, drawn, rocks


def planting_of(book, page):
    """What a page shows of the planting: the rows of its scene (a compound also its halls'), what the view drew of each, what is not drawn and why, the rockeries."""
    pid, kind = page["id"], page["kind"]
    if kind == "compound":
        keys = [pid] + book.children.get(pid, [])
    elif kind == "garden":
        keys = [pid, "GARDEN-ALL"] if pid != "GARDEN-ALL" else [pid]
    elif kind == "hall":
        keys = [pid]
    else:
        return None
    rows = [r for k in keys for r in book.planting.get(k, [])]
    rocks = book.rocks.get(pid, []) if kind == "compound" else []
    if not rows and not rocks:
        return None

    def free(r):
        return all("public domain" in book.sources.get(s, {}).get("licence", "") for s in split_ids(r["sources"]))

    def entry(r):
        e = {"id": r["id"], "plant": r["plant_zh"], "latin": r["latin"], "en": r["name_en"], "role": r["role"], "place": PLACE_WORDS.get(r["place"], r["place"]), "where": r["place_text"][:160],
             "season": r["season"], "kind": r["source_kind"], "confidence": r["confidence"], "sources": r["sources"], "quote": r["quote"][:60] if free(r) and r["source_kind"] in ("poem", "preface", "text", "account") else "",
             "drawn": book.drawn.get(r["id"], {}).get("count", 0)}
        return e

    keep = [r for r in rows if r["use"] == "keep"]
    out = {"sourced": [entry(r) for r in keep if r["form"] not in ("none", "rock")],
           "not_drawn": [entry(r) for r in keep if r["form"] == "none"],
           "rejected": [{**entry(r), "where": r["reject_reason"][:160], "drawn": 0} for r in rows if r["use"] == "reject"],
           "rocks": [{"id": p["id"], "rock": p["rock"], "height_m": p["height_m"], "confidence": p["confidence"], "extent": p["extent_confidence"], "sources": p["sources"], "where": p["note"][:160]} for p in rocks]}
    order = {"A": 0, "B": 1, "C": 2}
    for k in ("sourced", "not_drawn", "rejected"):
        out[k].sort(key=lambda e: (order.get(e["confidence"], 3), e["plant"], e["id"]))
        out[k] = out[k][:60]
    return {k: v for k, v in out.items() if v}


def ways_of(book, page):
    """What a page shows of the ways: the lines and landings that touch it (a compound: those of its halls, counted), the routes that pass it."""
    pid = page["id"]
    out = {}
    if page["kind"] == "compound":
        mine = [w for k in [pid] + book.children.get(pid, []) for w in book.ways.get(k, [])]
        seen = set()
        mine = [w for w in mine if not (w["id"] in seen or seen.add(w["id"]))]
    else:
        mine = book.ways.get(pid, [])
    if mine:
        out["reached"] = mine[:40]
    if book.routes_at.get(pid):
        out["routes"] = book.routes_at[pid]
    return out


def assert_public(page):
    pid = page["id"]
    assert set(page) <= PUBLIC_KEYS, (pid, set(page) - PUBLIC_KEYS)
    for w in page.get("ways", {}).get("reached", []):
        assert set(w) == PUBLIC_WAY_KEYS, (pid, w)
    for w in page.get("ways", {}).get("routes", []):
        assert set(w) == PUBLIC_ROUTE_KEYS, (pid, w)
    for k in ("sourced", "not_drawn", "rejected"):
        for e in page.get("planting", {}).get(k, []):
            assert set(e) == PUBLIC_PLANT_KEYS, (pid, e)
    for d in page.get("dimensions", []):
        assert set(d) - {"scale"} == PUBLIC_DIMENSION_KEYS, (pid, d)  # a scene's figures also say the scale used
    for f in page["facts"]:
        assert set(f) == PUBLIC_FACT_KEYS, (pid, f)
    for p in page["photos"] + page.get("photos_inside", []):
        assert set(p) <= PUBLIC_PHOTO_KEYS and p["source_url"].startswith("http"), (pid, p["id"], set(p) - PUBLIC_PHOTO_KEYS)
        assert not (p.get("link_only") and (p.get("image") or p.get("thumb"))), (pid, p["id"], "a research-only picture with an image")
    for r in page.get("reconstructions", []):
        assert set(r) <= PUBLIC_RECON_KEYS and r["source_url"].startswith("http"), (pid, r["id"], set(r) - PUBLIC_RECON_KEYS)
        assert not (r.get("link_only") and (r.get("image") or r.get("thumb"))), (pid, r["id"], "a research-only reconstruction with an image")
    for t in page.get("twins", []):
        assert set(t) <= PUBLIC_TWIN_KEYS and t["link"].startswith("http"), (pid, t["id"], set(t) - PUBLIC_TWIN_KEYS)
        for p in t["photos"]:
            assert set(p) <= PUBLIC_PHOTO_KEYS and not (p.get("link_only") and (p.get("image") or p.get("thumb"))), (pid, t["id"], p["id"])
    for e in page.get("evidence", []):
        assert set(e) <= PUBLIC_EVIDENCE_KEYS, (pid, e["id"])
        assert e["rights_class"] == "free" or not (e["excerpt_zh"] or e["excerpt_other"]), (pid, e["id"], "copied text from a research-only source")
    text = json.dumps(page, ensure_ascii=False)
    for word in ("/_local/", "research/raw", "plan_x", "princeton_mosaic"):
        assert word not in text, (pid, word)


def publish_models(book):
    """Round 13, as Küstrin's: check every models/*/summary.json, copy its GLB to site/reconstruction/models/<ID>/, write data/models.json. Stops on a summary that fails."""
    out = {}
    for sm in {id(v): v for v in book.models.values()}.values():
        mid, folder = sm["id"], sm["folder"]
        problems = []
        if mid not in book.rows:
            problems.append("id not a row of buildings.csv")
        problems += [f"alias {a} not a row" for a in sm.get("aliases", []) if a not in book.rows]
        for k in ("glb", "position", "rotationY", "line", "rows", "caption"):
            if k not in sm:
                problems.append(f"no {k}")
        if not all(k in sm.get("caption", {}) for k in ("frontage_m", "depth_m")):
            problems.append("caption needs frontage_m and depth_m")
        own = {b["id"] for i in [mid, *sm.get("aliases", [])] for b in book.boxes.get(i, [])}
        problems += [f"hides its own box {h}" for h in sm.get("hides", []) if h in own]
        glb = folder / sm["glb"]
        if not glb.exists():
            problems.append("GLB missing")
        if problems:
            raise SystemExit(f"models/{folder.name}/summary.json: " + "; ".join(problems))
        dest = SITE_DATA.parent / "models" / mid / "model.glb"
        data = glb.read_bytes()
        if not dest.exists() or dest.read_bytes() != data:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        out[mid] = {"url": f"models/{mid}/model.glb", "name": sm["name"], "aliases": sm.get("aliases", []), "position": sm["position"], "rotationY": sm["rotationY"],
                    "caption": sm["caption"], "hides": sm.get("hides", []), "boxes": sorted(own)}
        jp = folder / "joints.json"
        decks = json.load(open(jp, encoding="utf-8")).get("decks") if jp.exists() else None
        if decks:  # Round 16: raised floors the model draws (a terrace): the view lays the ways on them
            out[mid]["decks"] = decks
    write_if_changed(SITE_DATA / "models.json", json.dumps({"note": "Round 13: detailed models (models/<ID>-<slug>/summary.json), written by scripts/building_pages.py. Their boxes stay as the click target, unseen.", "models": out}, ensure_ascii=False, indent=1) + "\n")
    return out


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
    write_if_changed(path, page_markdown(page, lambda tid: book.twin_photos.get(tid, [])) + "\n" + hand)
    return hand, wanted.name


def main():
    book = Book()
    publish_models(book)
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
    for tag in GARDEN_NAME:
        page = build_garden(book, tag)
        write_if_changed(PUBLIC_OUT / f"{page['id']}.json", json.dumps(panel_page(book, page, "", True), ensure_ascii=False, separators=(",", ":")))
        write_if_changed(LOCAL_OUT / f"{page['id']}.json", json.dumps(panel_page(book, page, "", False), ensure_ascii=False, separators=(",", ":")))
        written.add(page["id"])
    for cls in CLASS_NAME:
        page = build_class(book, cls)
        write_if_changed(PUBLIC_OUT / f"{page['id']}.json", json.dumps(panel_page(book, page, "", True), ensure_ascii=False, separators=(",", ":")))
        write_if_changed(LOCAL_OUT / f"{page['id']}.json", json.dumps(panel_page(book, page, "", False), ensure_ascii=False, separators=(",", ":")))
        written.add(page["id"])
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
