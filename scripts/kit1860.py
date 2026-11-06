"""The numbers of the hall kit and the stone kit: site/reconstruction/data/kit_1860.json, one entry per box of data/halls_1860.geojson, and the paved courts between the halls: generated/courts.bin. Round 11.

  uv run python scripts/kit1860.py        (after boxes1860.py and paths1860.py)

The browser draws every hall from these numbers (site/reconstruction/kit3d.js for the Qing halls, stonekit3d.js for the Xiyang Lou); it adds no number of its own except the shapes of the parts.
Each entry says where its form comes from (`src`):
  model    a detailed model, models/<ID>-<slug>/summary.json: the kit draws nothing for it (none yet)
  dossier  the hall's own figures (research/scenes, research/xiyanglou: dimensions.json) or its own reading in research/scenes/halls.csv (roof form, tiles), each figure with its method and grade (`fig`)
  stated   a size stated in a source (research/typology/params.json by_name)
  class    the defaults of its hall class (params.json): `assumed`, C, "drawn from the typology of its hall class, not from a picture of this hall"
The kit draws inside the box: the platform is the box's footprint, the columns stand the platform's edge (下出) inside it, the roof reaches the overhang (上出) beyond the columns, the heights are the box's.
Variation (`sh`) is seeded by the box id and only for `class` halls: a lacquer shade, a wall shade, the curve of the roof and the lift of its corners, 硬山 or 悬山 on an unread gable.
The courts: the ground between the halls of a compound, closed over gaps up to 2 x COURT_REACH_M, less water, hills and the halls themselves, cut to the compound's outline: assumed, C (no source draws a court's paving).
"""

import csv
import hashlib
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import Polygon, box as sbox, shape
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scene1860 import DATUM_M, GENERATED, ROOT, SITE_DATA, Grid, figures, layer, params, to_xz  # noqa: E402

P = params()
CLASSES = P["classes"]
BY_NAME = P["by_name"]
FIG = figures()
ROWS = {r["id"]: r for r in csv.DictReader(open(ROOT / "research/buildings.csv", encoding="utf-8", newline=""))}
FOOT = {f["properties"]["id"]: f["properties"] for f in layer("footprints_1860")}

# 举架 by class, from eave to ridge (S101 as summarised in research/typology/halls.md section 4; scripts/typology_rules.py uses the same lists). The roof's profile in the kit.
JU = {"grand_hall": [0.5, 0.6, 0.75, 0.9], "temple_hall": [0.5, 0.65, 0.75, 0.9], "main_hall": [0.5, 0.65, 0.85], "side_hall": [0.5, 0.65, 0.85], "gate_hall": [0.5, 0.65, 0.85],
      "small_house": [0.5, 0.7], "gallery": [0.5, 0.7], "storeyed_hall": [0.5, 0.7], "tower": [0.5, 0.65, 0.75, 0.9], "pavilion_square": [0.5, 0.7, 0.9], "pavilion_polygon": [0.5, 0.7, 0.9]}
BRACKETS = {"grand_hall", "temple_hall", "gate_hall", "tower"}  # 大式 halls carry bracket sets 斗拱 (S101; 澹怀堂 and 长春园宫门 have them on grey rolled roofs, S112). 小式 halls a painted beam only
BACK_PORCH = {"small_house": 0.7, "main_hall": 0.8, "grand_hall": 1.0, "temple_hall": 1.0, "side_hall": 0.3, "storeyed_hall": 0.6}  # share of class halls given a back porch too: 前后廊 (S111: 惠如春, 松风阁 two 4-chi porches); the shares are a guess, C
ALL_ROUND = {"grand_hall", "temple_hall"}  # 周围廊: 正大光明殿 'porch all round' (S02, params by_name)
STEP_RISE_M = 0.15  # a step 踏跺 about half a chi; tread at most 0.3 m, and the flight no longer than the roof's overhang (the kit stays within its box plus an overhang). C
COURT_REACH_M = 11.0  # halls this near each other (2 x) share a paved court. C
APRON_M = 1.5  # paving 散水 round each hall of a compound (S104: eaves drip courses of pebble mosaic). Width C
COURT_CELL_M = 5.0
COURT_LIFT_M = 0.04  # above the ground; the ways lie 0.07 above it (paths3d.js)
COURT_SCALE = 0.2  # metres per unit of x and z in courts.bin; y in cm
WORD = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13}


def seed(s):
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)


def rnd(s, k):
    """A number in [0, 1) for box s, draw k: the same on every run."""
    return (seed(f"{s}:{k}") % 10000) / 10000


def first_int(text):
    m = re.match(r"\s*(\d+)", text or "")
    return int(m.group(1)) if m else None


def count_in(text, noun):
    m = re.search(r"(\d+|" + "|".join(WORD) + r")\s+(?:\w+\s+)?" + noun, text or "")
    return (int(m.group(1)) if m.group(1).isdigit() else WORD[m.group(1)]) if m else None


def model_ids():
    out = set()
    for p in (ROOT / "models").glob("*/summary.json"):
        s = json.load(open(p, encoding="utf-8"))
        out.add(s["id"])
        out.update(s.get("aliases", []))
    return out


def steps_by_box(feats):
    """The sides of each box that a way of Round 9 reaches (paths_1860 from_at / to_at, 'F0568:front'), with where along the side the way arrives (m from the side's middle): steps there."""
    frames = {}
    for f in feats:
        ring = np.array([to_xz(*c) for c in f["geometry"]["coordinates"][0][:4]])
        c = (ring[0] + ring[2]) / 2
        u = (ring[1] - ring[0]) / np.linalg.norm(ring[1] - ring[0])
        a = (ring[1] - ring[2]) / np.linalg.norm(ring[1] - ring[2])
        frames[f["properties"]["id"]] = (c, u, a)
    out = defaultdict(dict)
    for f in json.load(open(SITE_DATA / "paths_1860.geojson", encoding="utf-8"))["features"]:
        p = f["properties"]
        coords = f["geometry"]["coordinates"]
        for at, pt in ((p.get("from_at"), coords[0]), (p.get("to_at"), coords[-1])):
            if at and ":" in at:
                bid, side = at.split(":", 1)
                if side in ("front", "back", "left", "right") and bid in frames:
                    c, u, a = frames[bid]
                    d = np.array(to_xz(*pt)) - c
                    off = float(d @ u) if side in ("front", "back") else float(d @ a)
                    out[bid].setdefault(side, []).append(round(off, 2))
    return out


def bay_list(n, central, side, end=None):
    """n bays, central widest, ends 梢间 narrower where given: symmetrical."""
    if n <= 1:
        return [central]
    half = []
    for i in range(1, (n + 1) // 2 + (0 if n % 2 else 0)):
        half.append(side)
    if end is not None and len(half) >= 2:
        half[-1] = end
    if n % 2:
        return half[::-1] + [central] + half
    # even: two central bays (文源阁's six), side outward
    half = [side] * (n // 2 - 1)
    if end is not None and half:
        half[-1] = end
    return half[::-1] + [central, central] + half


def hall_entry(p, steps, models):
    bid, cls, f, d = p["building_id"], p["hall_class"], p["frontage_m"], p["depth_m"]
    row = ROWS.get(bid, {})
    named_key = {"文源阁阁": "文源阁", "大宫门门殿": "大宫门", "雷峰夕照": "雷峰夕照殿"}.get(p["name"], p["name"])
    named = BY_NAME.get(named_key, {}) if p["basis"] == "stated" or named_key in BY_NAME else {}
    c = CLASSES.get(cls) or CLASSES["small_house"]
    fig = FIG.get(bid, {}) if "-" in bid or bid[:2] in ("QC", "CC", "YM") else {}
    used = {k: f"{v[0]} m, {v[1]} {v[2]}, {v[3]}" for k, v in (p.get("figures") or {}).items()}
    sid = p["id"]
    is_class = not used and not named and "roof_src" not in p and "tiles_src" not in p
    e = {}

    # kind
    name = p["name"] or ""
    if p.get("tiers_m"):
        kind = "tower"
    elif cls == "gate_hall" and ("坊" in name or "牌楼" in name):
        kind = "pailou"
    elif cls == "gate_hall":
        kind = "gate"
    elif cls == "gallery":
        kind = "gallery"
    elif p["roof"] == "pyramid" and (cls.startswith("pavilion") or max(f, d) < 10):
        kind = "pavilion"
    else:
        kind = "hall"
    e["k"] = kind

    # platform edge 下出 and overhang 上出; the column line keeps at least 60 % of the box
    edge = (fig.get("other:platform_overhang") or {}).get("value") or named.get("platform_edge_m") or c["platform_edge_m"]
    if "other:platform_overhang" in fig:
        used["edge"] = f"{edge} m, {fig['other:platform_overhang']['method']} {fig['other:platform_overhang']['confidence']}, {fig['other:platform_overhang']['source']}"
    edge = min(edge, 0.2 * min(f, d))
    over = min(c["overhang_m"], 0.22 * min(f, d) + 0.25)
    if kind == "pailou":
        edge, over = min(0.3, 0.2 * d), 0.6
    cs, cq = f - 2 * edge, d - 2 * edge  # the column line
    e["e"], e["o"] = round(edge, 2), round(over, 2)

    # bays along the frontage
    n = first_int(row.get("bays")) or first_int(row.get("bays_plan")) or (FOOT.get(sid) or {}).get("ncols")
    bays_src = "count from buildings.csv or the plan" if n else "count from the class bay"
    central, side, end = c["bay_m"]["central"], c["bay_m"]["side"], c["bay_m"].get("end")
    if "bay_m" in named:
        central, side, end = named["bay_m"]["central"], named["bay_m"]["side"], named["bay_m"].get("end")
        bays_src = "stated widths (by_name)"
    if "bay_width" in fig and fig["bay_width"]["value"] < 0.45 * cs + 0.01:
        central = fig["bay_width"]["value"]
        side = (fig.get("other:secondary_bay_width") or fig.get("other:side_bay_width") or {"value": side})["value"]
        end = (fig.get("other:end_bay_width") or {"value": None})["value"]
        used["bays"] = f"central {central} m, side {side} m" + (f", end {end} m" if end else "") + f", {fig['bay_width']['method']} {fig['bay_width']['confidence']}, {fig['bay_width']['source']}"
        bays_src = "dossier widths"
    if kind in ("pavilion",):
        n = 1 if cs < 8 else 3
    if not n or not (1.4 <= cs / n <= 7.5):
        n = max(1, round(cs / ((central + side) / 2)))
        if kind not in ("gallery",) and n > 2 and n % 2 == 0 and not (row.get("bays") or "").strip():
            n += 1 if cs / (n + 1) >= 2.0 else -1
    n = min(n, 60)
    widths = bay_list(n, central, side, end) if kind != "gallery" else [cs / n] * n
    k = cs / sum(widths)
    e["b"] = [round(w * k, 2) for w in widths]
    e["bs"] = bays_src + (f", scaled {k:.2f} to the box" if abs(k - 1) > 0.02 else "")

    # depth: porches and rows of columns across
    porch = (fig.get("other:porch_depth") or {}).get("value") or named.get("porch_m") if isinstance(named.get("porch_m"), (int, float)) or "other:porch_depth" in fig else c["porch_m"]
    if "other:porch_depth" in fig:
        used["porch"] = f"{porch} m, {fig['other:porch_depth']['method']} {fig['other:porch_depth']['confidence']}, {fig['other:porch_depth']['source']}"
    porch = porch or 0
    pf = pb = ps = 0.0
    if kind in ("hall", "tower") and cq >= 4.2 and porch:
        pf = min(porch, 0.25 * cq)
        if rnd(sid, "back") < (1.0 if not is_class else BACK_PORCH.get(cls, 0.5)) and cq >= 6.0:
            pb = pf
        if (cls in ALL_ROUND or named.get("porch") == "all round") and cs >= 12:
            ps = pf
    e["pf"], e["pb"], e["ps"] = round(pf, 2), round(pb, 2), round(ps, 2)
    inner = cq - pf - pb
    rows_n = (FOOT.get(sid) or {}).get("nrows") or 1
    nd = max(1, min(4, rows_n if rows_n > 1 else round(inner / 4.5) or 1))
    e["d"] = [round(x, 2) for x in ([pf] if pf else []) + [inner / nd] * nd + ([pb] if pb else [])]

    # heights: the box's own; the column is what lies between platform and eave
    e["col"] = round(p["eave_m"] - p["platform_m"], 2) if not p.get("tiers_m") else round(p["tiers_m"][0] - p["platform_m"], 2)
    dia = (fig.get("other:column_diameter") or {}).get("value") or named.get("column_dia_m") or 0.07 * max(e["b"])
    e["dia"] = round(min(max(dia, 0.18), 0.6), 2)

    # steps: the front always (gates also the back); every side a way reaches, at the middle bay, or where the way arrives if that is further out (`so`)
    reached = steps.get(sid, {})
    st = {"front"} | set(reached)
    if kind in ("gate", "pailou"):
        st |= {"back"}
    if p.get("over_water"):
        st = set(reached)
    e["st"] = sorted(st)
    so = {}
    for side, offs in reached.items():
        half = (cs if side in ("front", "back") else cq) / 2
        for off in offs:
            if abs(off) > 0.5 * max(e["b"][len(e["b"]) // 2], 2.4):
                so.setdefault(side, []).append(round(max(-half + 1.3, min(half - 1.3, off)), 2))
    if so:
        e["so"] = so
    e["bal"] = int(cls in ("grand_hall", "temple_hall") and p["platform_m"] >= 0.55 or p["platform_m"] >= 0.95)

    # roof class from the data
    form = {"hip": "wd", "hip_gable": "xs", "pyramid": "cj"}.get(p["roof"])
    if p["roof"] == "gable":
        gk = p.get("gable_kind")
        if gk:
            form = "xu" if gk == "xuanshan" else "ys"
        elif cls == "gallery" or kind == "gallery":
            form = "xu"  # 卷棚悬山: params.json classes.gallery
        elif cls == "side_hall":
            form = "ys"  # 卷棚硬山 first in params.json classes.side_hall
        else:
            form = "ys" if rnd(sid, "gable") < 0.6 else "xu"  # small_house 卷棚硬山 or 悬山 (params.json): the choice is seeded, C
        e["gk"] = "stated" if gk else "seeded" if cls not in ("gallery", "side_hall") else "class"
    e["rf"], e["rl"], e["db"] = form, int(bool(p["rolled"])), int(bool(p["double"]))
    if form == "cj":
        e["sd"] = p.get("sides") or (8 if cls == "pavilion_polygon" else 4)
    e["ju"] = JU.get(cls, JU["small_house"])
    tiles = p["tiles"]
    if tiles == "mixed":
        tiles = ("yellow", "blue", "green")[seed(sid) % 3]  # 方壶胜境: blue, yellow, green glazed halls (S08, viewed); which hall has which is not read: C
    e["t"] = tiles
    if p.get("tile_edge"):
        e["te"] = p["tile_edge"]
    e["bd"] = "br" if (cls in BRACKETS or "翘" in str(named.get("roof", ""))) else "bm"

    # openings: doors in the middle bay(s) at the front, windows elsewhere; the back a door in the middle on through halls (seeded for class halls)
    mid = n // 2
    e["dr"] = [mid] if n % 2 else [mid - 1, mid]
    if kind == "gate" and n >= 5:
        e["dr"] = [mid - 1, mid, mid + 1]
    e["rr"] = "d" if (kind == "gate" or (cls in ("main_hall", "grand_hall") and rnd(sid, "rear") < 0.5)) else "w"

    # variation, only where the form is the class's
    if is_class:
        e["sh"] = [seed(sid) % 3, seed(sid + "w") % 3]
        e["v"] = [round(0.85 + 0.3 * rnd(sid, "curve"), 2), round(0.8 + 0.4 * rnd(sid, "lift"), 2)]
    else:
        e["sh"] = [0, 0]
        e["v"] = [1.0, 1.0]

    # where the form comes from
    if bid in models:
        src = "model"
    elif used or "roof_src" in p or "tiles_src" in p:
        src = "dossier"
    elif p["basis"] == "stated":
        src = "stated"
    else:
        src = "class"
    if p.get("roof_src", "class") != "class":
        used["roof"] = p["roof_src"] if p["roof_src"].startswith("halls.csv") else f"buildings.csv {row.get('confidence') or 'C'}"
    if p.get("tiles_src"):
        used["tiles"] = p["tiles_src"]
    e["src"] = src
    e["a"] = int(src == "class")
    grades = [g for k, v in used.items() if k not in ("roof", "tiles") for g in re.findall(r"\b[abcd] ([ABC])\b", v)] + [v.split(" ")[-1] for k, v in used.items() if k in ("roof", "tiles")]
    e["g"] = "C" if src == "class" else min(grades) if grades else ("B" if src == "stated" else "C")
    if used:
        e["fig"] = used
    return e


# ---- the Xiyang Lou: the stone kit ----
XY_ROOF = {
    # field and edge colour of the glazed roofs. XY01: the Crawford painting (S700, research/xiyanglou/materials.csv), yellow-ochre field, orange-red edge. XY06: blue (S06; Q69). Else the strip's rule in materials.csv: violet and green on the one surviving roof (S828), C.
    "XY01": ("ochre", "red"),
    "XY06": ("blue", None),
}
XY_ROOF_DEFAULT = ("green", "purple")
XY_STAIRS = {"XY06": "the plan draws curved stairs either side (params.json xiyang_lou XY06)", "XY08": "two horseshoe stairs on the west front (research/xiyanglou/boxes.csv XY08-02, the ruin)", "XY09": "a double stair to the terrace (plate 14)"}


def stone_entry(p, steps):
    bid, part = p["building_id"], (p.get("part") or "").lower()
    top = bid.split("-")[0]
    shape_ = p.get("shape")
    e = {"k": "stone"}
    st = count_in(part, "storeys") or count_in(part, "levels") or (2 if "two storeys" in part else None)
    if st is None:
        st = 2 if p["eave_m"] - p["platform_m"] >= 8.5 else 1
    e["sto"] = st
    nb = count_in(part, "bays") or count_in(part, "arches") or count_in(part, "gates")
    fig = FIG.get(bid, {}) or FIG.get(top, {})
    bw = (fig.get("bay_width") or {}).get("value")
    used = {}
    if not nb:
        nb = max(1, round((p["frontage_m"] - 1.0) / (bw or 4.3)))  # 4.3 m: 海晏堂's bays on plate 10 (boxes.csv XY08); C
        if nb > 2 and nb % 2 == 0:
            nb += 1
    else:
        used["bays"] = f"{nb}, from the part as boxes.csv names it"
    if bw:
        used["bay_width"] = f"{bw} m, {fig['bay_width']['method']} {fig['bay_width']['confidence']}, {fig['bay_width']['source']}"
    e["nb"] = min(nb, 25)
    e["ns"] = max(1, round(p["depth_m"] / max(p["frontage_m"] / e["nb"], 3.0)))
    field, edge = XY_ROOF.get(top, XY_ROOF_DEFAULT)
    if p["tiles"] == "blue":
        field, edge = "blue", None
    if p["tiles"] == "stone":
        field, edge = "stone", None
    e["t"], e["te"] = field, edge
    e["rf"] = {"hip": "wd", "pyramid": "cj", "gable": "ys", "hip_gable": "xs"}.get(p["roof"], "wd")
    e["db"] = int(bool(p["double"]))
    e["sd"] = 8 if shape_ == "octagon" else 4
    if any(w in part for w in ("main block", "west block", "reservoir house", "hall, two storeys", "hall, five roofs", "gate block", "east gate")):
        e["ped"] = 1  # a pediment over the middle bays: the plates draw one on the main fronts (research/xiyanglou, plates 1, 3, 6, 10, 14, 19); its form is the kit's, C
    if top in XY_STAIRS and ("west block" in part or "terrace" in part or "hall, porch" in part):
        e["stair"] = 1
        used["stair"] = XY_STAIRS[top]
    if "corridor" in part or "gallery" in part:
        e["k2"] = "arcade"
    if "pyramid fountain tower" in part:
        e["k2"] = "obelisk"
        e["tiers"] = 13  # 'two 13-tier towers' (S109, params.json xiyang_lou XY10)
    if "niche" in part:
        e["k2"] = "niche"
        e["cascade"] = 1  # the stepped cascade down the niche to the shell pool: plate 15; its steps and width are the kit's, C
    if "screen" in part or "far wall" in part:
        e["k2"] = "screen"
    if "maze wall" in part:
        e["k2"] = "hedgewall"
    if "triple gate" in part:
        e["k2"] = "gatewall"
    if shape_ in ("pool", "basin"):
        e["jet"] = 1
    if "bamboo" in part:
        e["bamboo"] = 1
    reached = steps.get(p["id"], {})
    if reached and p["platform_m"] >= 0.25 and shape_ not in ("pool", "basin", "wall", "court"):
        e["st"] = sorted(reached)
        e["so"] = {side: sorted(set(offs)) for side, offs in reached.items()}
    e["src"] = "dossier"
    e["a"] = 1  # the façade's parts are the kit's reading of the plates, not a survey of this front: C
    e["g"] = "C"
    if used:
        e["fig"] = used
    return e


def shape_entry(p):
    return {"k": "shape", "src": "stated" if p["basis"] == "stated" else "class", "a": int(p["assumed"]), "g": p["confidence"]}


# ---- the courts ----
def court_area(feats):
    """The courts as one geometry in scene metres (also read by scripts/greens1860.py, Round 12)."""
    xz = lambda g: shapely.transform(g, lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1])))
    water = unary_union([xz(shape(f["geometry"])).buffer(0) for f in layer("water_1860")]).buffer(0.8)
    hills = unary_union([xz(shape(f["geometry"])).buffer(0) for f in layer("hills_1860") if (f["properties"].get("height_est_m") or 0) >= 1.0])
    scenes = {f["properties"]["id"]: xz(shape(f["geometry"])).buffer(0) for f in layer("scenes_1860")}
    groups, all_boxes = defaultdict(list), []
    for f in feats:
        p = f["properties"]
        poly = xz(shape(f["geometry"]))
        all_boxes.append(poly)
        if p.get("european") or p.get("shape") or p.get("over_water") or p["hall_class"] == "gallery":
            continue
        groups[p["parent_id"] or p["building_id"]].append(poly)
    parts = []
    for gid, polys in groups.items():
        u = unary_union(polys)
        apron = u.buffer(APRON_M, join_style="mitre")
        closed = u.buffer(COURT_REACH_M, join_style="mitre").buffer(-(COURT_REACH_M - APRON_M), join_style="mitre") if len(polys) > 1 else apron
        area = closed.difference(hills.difference(apron))
        if gid in scenes:
            area = area.intersection(scenes[gid].buffer(APRON_M)).union(apron)
        parts.append(area)
    return unary_union(parts).difference(water).difference(unary_union(all_boxes)).buffer(0)


def courts(feats):
    G = Grid()
    court = court_area(feats)
    # a grid of cells, cut to the court; each piece triangulated, heights from the ground
    x0, z0, x1, z1 = court.bounds
    xs = np.arange(math.floor(x0 / COURT_CELL_M) * COURT_CELL_M, x1 + COURT_CELL_M, COURT_CELL_M)
    zs = np.arange(math.floor(z0 / COURT_CELL_M) * COURT_CELL_M, z1 + COURT_CELL_M, COURT_CELL_M)
    cells = np.array([sbox(x, z, x + COURT_CELL_M, z + COURT_CELL_M) for x in xs for z in zs])
    shapely.prepare(court)
    hit = cells[shapely.intersects(court, cells)]
    pieces = shapely.intersection(hit, court)
    tris = []
    for g in pieces:
        if g.is_empty:
            continue
        if abs(g.area - COURT_CELL_M ** 2) < 1e-6:
            (ax, az, bx, bz) = g.bounds
            tris += [((ax, az), (ax, bz), (bx, bz)), ((ax, az), (bx, bz), (bx, az))]
            continue
        for t in shapely.get_parts(shapely.constrained_delaunay_triangles(g)):
            c = list(t.exterior.coords)[:3]
            tris.append(tuple(c))
    verts = []
    for t in tris:
        a, b, c = t
        # wound so the face looks up (+y): x east, z south
        if (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) > 0:
            b, c = c, b
        for x, z in (a, b, c):
            verts.append((round(x / COURT_SCALE), round((G.at(x, z) + COURT_LIFT_M) * 100), round(z / COURT_SCALE)))
    arr = np.array(verts, dtype="<i2")
    arr.tofile(GENERATED / "courts.bin")
    return {"file": "generated/courts.bin", "triangles": len(tris), "area_m2": round(court.area), "cell_m": COURT_CELL_M, "scale_xz_m": COURT_SCALE, "scale_y_m": 0.01, "lift_m": COURT_LIFT_M,
            "sources": "S01;S104", "confidence": "C", "assumed": True,
            "basis": f"the ground between the halls of each compound, closed over gaps up to {2 * COURT_REACH_M:g} m, with an apron of {APRON_M:g} m round each hall (S104: drip courses round the halls); less water, hills and the halls; cut to the compound's outline on S01. No source draws the paving of a court."}


def main():
    fc = json.load(open(SITE_DATA / "halls_1860.geojson", encoding="utf-8"))
    feats = fc["features"]
    steps = steps_by_box(feats)
    models = model_ids()
    halls = {}
    for f in feats:
        p = f["properties"]
        if p.get("european") and not p.get("shape"):
            halls[p["id"]] = stone_entry(p, steps)
        elif p.get("european"):
            e = stone_entry(p, steps)
            e["k"] = "stoneshape"
            halls[p["id"]] = e
        elif p.get("shape"):
            halls[p["id"]] = shape_entry(p)
        else:
            halls[p["id"]] = hall_entry(p, steps, models)
    court = courts(feats)
    out = {
        "name": "kit_1860",
        "note": "Round 11: the numbers the browser's hall kit (kit3d.js) and stone kit (stonekit3d.js) draw each box of halls_1860.geojson from (scripts/kit1860.py). Keys: k kind; b bay widths along the frontage at the column line (m); d widths across, front to back; pf, pb, ps porches; e platform edge 下出; o overhang 上出; col column; dia its diameter; st sides with steps; bal balustrade; rf roof (wd 庑殿, xs 歇山, ys 硬山, xu 悬山, cj 攒尖); rl rolled 卷棚; db double eaves; sd sides of a 攒尖; ju 举架 eave to ridge; t tile colour; te edge 剪边; bd eave band (br bracket sets, bm painted beam); dr door bays; rr rear (w windows, d a door in the middle); sh shades; v curve and corner lift; src where the form comes from; a assumed; g its grade; fig the figures used.",
        "credit": "Heights and roofs from research/typology/params.json, the dossiers and the readings of the 1744 album; positions traced from S01, image courtesy of the Princeton University Art Museum. Colours chosen for the view where no source gives them.",
        "gallery": {k: CLASSES["gallery"][k] for k in ("bay_m", "platform_m", "column_m", "eave_m", "ridge_m", "overhang_m")} | {"ju": JU["gallery"]},
        "courts": court,
        "halls": halls,
    }
    (SITE_DATA / "kit_1860.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    from collections import Counter
    C = Counter
    hs = [h for h in halls.values() if h["k"] not in ("shape",)]
    print(f"{len(halls)} entries: kinds {dict(C(h['k'] for h in halls.values()))}")
    print(f"form from: {dict(C(h['src'] for h in halls.values()))}; assumed {sum(h['a'] for h in halls.values())}; roofs {dict(C(h.get('rf') for h in hs))}; tiles {dict(C(h.get('t') for h in hs))}")
    print(f"courts: {court['triangles']} triangles over {court['area_m2'] / 1e4:.1f} ha; kit_1860.json {(SITE_DATA / 'kit_1860.json').stat().st_size / 1e6:.2f} MB, courts.bin {(GENERATED / 'courts.bin').stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
