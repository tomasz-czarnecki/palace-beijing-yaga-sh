"""Merge the text inventory, the plan readings and the traced regions into research/buildings.csv and research/layers/*_1860.geojson.

Inputs (all in the repo): research/plan/inventory_texts.csv, research/plan/readings/<area>/*.csv, research/plan/blocks.csv, regions.json,
regions_classified.csv, walls.json, gates.json, hills_texts.csv, osm_points.csv, research/typology/params.json, research/georef/princeton-1920s.json.
Writes: research/buildings.csv, research/layers/{walls,water,islands,hills,bridges,scenes,footprints,fields}_1860.geojson, research/plan/new_ids.csv,
research/plan/coverage.json. Decisions are constants below; every number it prints comes from this run. Run after scripts/georef.py and scripts/trace_plan.py.
"""

import csv
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from pypinyin import lazy_pinyin
from pyproj import Transformer
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, mapping
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).parent))
import georef  # noqa: E402

PLAN = Path("research/plan")
LAYERS = Path("research/layers")
AREAS = ["ym_central", "ym_west", "ym_east", "cc_xyl", "qc"]
AREA_TAG = {"ym_central": "C", "ym_west": "W", "ym_east": "E", "cc_xyl": "X", "qc": "Q"}
AREA_PREFIX = {"ym_central": "YM", "ym_west": "YM", "ym_east": "YM", "cc_xyl": "CC", "qc": "QC"}
READ_RANK = {"sure": 3, "likely": 2, "guess": 1, "not_found": 0, "": 0}

# Hall scale of S01, research/typology/halls.md section 2: the plan draws halls smaller than the ground scale of 4.77 px/m.
PX_PER_M_FRONTAGE = 4.18
PX_PER_M_DEPTH = 3.31

# Which reader wins where two read the same compound (question Q-lines in research/questions.md give the reasons).
COMPOUND_OWNER = {"YM15": "ym_west", "YM25": "ym_east", "YM26": "ym_east", "YM46": "ym_west", "YM51": "ym_east", "YM53": "ym_west", "YM42": "ym_central"}
COMPOUND_UNION = {"YM14", "YM38"}  # both readers saw a part; the polygon is the union
COMPOUND_DROP = {("ym_east", "YM53")}  # a guess at a place that ym_east itself also records as 船坞

# S41 (via the inventory notes) lists these album scenes as different on later plans, so the album does not show the 1860 state: row confidence B, not A.
CHANGED_BY_1860 = {"YM02", "YM03", "YM09", "YM05", "YM08", "YM19", "YM06", "YM07", "YM16", "YM14", "YM39", "YM40", "YM34", "YM33", "YM24", "YM23"}

# Malone (S02 p.232) says S01 draws 谐奇趣 about two inches too far south. The ruin stands, so the group is moved to it: plan px added before warping.
# Target: centre of the OSM ruin outline of the main block, read in scripts below (XY01_RUIN); see research/questions.md.
XY01_RUIN = None  # filled in by xy01_shift()

# Rows the plan shows as a labelled plot, a hill or a dock, not a hall: they keep their position, but get no footprint or box.
NOT_A_BUILDING_NOTE = re.compile(r"blank cell|no building drawn|no building", re.I)
HILL_RECTS = {"YM01-12": "寿山"}
DOCK_RECTS = {"YM29-07"}

# Typology names that differ from the row name.
BY_NAME_ALIAS = {"雷峰夕照殿": "雷峰夕照", "舍卫城南门": "多宝阁"}

# Closing radius (px) for the water layer when deriving islands. Bridges and short dams cut the water network; 45 px is about 9 m on the ground.
ISLAND_CLOSING_PX = 45
# Malone's nine islands round the Back Lake (S02 p.52): the plan draws causeways, so some are not enclosed by the closed water. Readers' outlines follow their shores.
ISLAND_FROM_SCENE = ["YM03", "YM04", "YM05", "YM06", "YM07", "YM08", "YM09", "YM10", "YM11"]

# Labels written on a lake that name a building beside it, not the lake (reader cc_xyl).
LABEL_NOT_WATER = {"海岳开襟", "翠交轩", "静便趣", "流香渚", "谐奇趣"}

NOT_A_SCENE = {"YM54", "YM55"}  # 福海 and 后湖 are rows because the texts list them, but they are water: water_1860

UTM = Transformer.from_crs(4326, 32650, always_xy=True)


def rows(path: Path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def clean_name(s: str) -> str:
    """Name as written on the plan. Reader remarks in brackets go; ? stays for an unread character."""
    s = re.sub(r"\([^)]*\)", "", s or "").strip()
    return s if re.search(r"[一-鿿]", s) else ""


def pinyin(s: str) -> str:
    """Machine romanisation of a plan label; research/README.md says so. Empty if a character is unread."""
    if not s or "?" in s or " " in s or "/" in s:
        return ""
    return " ".join(w.capitalize() for w in lazy_pinyin(s))


def to_wgs(x, y) -> tuple[float, float]:
    lon, lat = georef.plan_to_wgs84(np.array([float(x)]), np.array([float(y)]))
    return float(lon[0]), float(lat[0])


def warp_ring(pts) -> list[list[float]]:
    a = np.array(pts, dtype=float)
    lon, lat = georef.plan_to_wgs84(a[:, 0], a[:, 1])
    return [[round(float(u), 7), round(float(v), 7)] for u, v in zip(lon, lat)]


def area_m2(lonlat_ring) -> float:
    a = np.array(lonlat_ring)
    x, y = UTM.transform(a[:, 0], a[:, 1])
    return float(Polygon(zip(x, y)).area)


def write_layer(name: str, features: list[dict], extra: dict | None = None) -> None:
    fc = {
        "type": "FeatureCollection",
        "name": name,
        "crs_note": "WGS84 (EPSG:4326)",
        "attribution": "Traced from the Plan of the Yuanmingyuan, Princeton University Art Museum 2022-27 a-c (S01). Image courtesy of the Princeton University Art Museum.",
        **(extra or {}),
        "features": features,
    }
    (LAYERS / f"{name}.geojson").write_text(json.dumps(fc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"  {name}: {len(features)}")


def poly_feature(geom_rings, props: dict) -> dict:
    """geom_rings: list of rings (first outer, rest holes), already WGS84."""
    return {"type": "Feature", "properties": props, "geometry": {"type": "Polygon", "coordinates": [r + [r[0]] if r[0] != r[-1] else r for r in geom_rings]}}


# ---- blocks ----

def norm_block(b: dict) -> None:
    """Keep w, h, ncols, nrows in the plan's frame: a box turned by about 90 degrees gets its sides swapped. Readers' S, N, E, W are plan directions."""
    while b["ang"] > 45:
        b["ang"] -= 90
        b["w"], b["h"], b["ncols"], b["nrows"] = b["h"], b["w"], b["nrows"], b["ncols"]
    while b["ang"] < -45:
        b["ang"] += 90
        b["w"], b["h"], b["ncols"], b["nrows"] = b["h"], b["w"], b["nrows"], b["ncols"]


def load_blocks() -> tuple[dict, dict]:
    blocks = {}
    for r in rows(PLAN / "blocks.csv"):
        blocks[r["block_id"]] = {"cx": float(r["cx"]), "cy": float(r["cy"]), "w": float(r["w_px"]), "h": float(r["h_px"]), "ang": float(r["angle_deg"]), "ncols": int(r["ncols"] or 0), "nrows": int(r["nrows"] or 0), "cells": int(r["cells"] or 0)}
    merged = {}  # block -> the block it was merged into
    kept_apart = []
    fixes = [(a, r) for a in AREAS for r in rows(PLAN / "readings" / a / "blocks_fix.csv")]
    rejected = set()
    for a, r in fixes:
        act, bid = r["action"].strip(), r["block_id"].strip()
        if act == "add":
            blocks[f"{bid}"] = {"cx": float(r["x"]), "cy": float(r["y"]), "w": float(r["w_px"]), "h": float(r["h_px"]), "ang": float(r["angle_deg"] or 0), "ncols": 0, "nrows": 0, "cells": 0, "added": a}
        elif act == "resize" and bid in blocks:
            b = blocks[bid]
            b.update(cx=float(r["x"]), cy=float(r["y"]), w=float(r["w_px"]), h=float(r["h_px"]), ang=float(r["angle_deg"] or 0))
        elif act == "reject":
            rejected.add(bid)
    for b in blocks.values():
        norm_block(b)
    for a, r in fixes:
        act, bid = r["action"].strip(), r["block_id"].strip()
        if act.startswith("merge:"):
            tgt = act.split(":", 1)[1].strip()
            if bid in blocks and tgt in blocks and bid != tgt:
                merged[bid] = tgt
    for bid, tgt in list(merged.items()):
        while tgt in merged:
            tgt = merged[tgt]
        a, b = blocks[bid], blocks[tgt]
        x0 = min(a["cx"] - a["w"] / 2, b["cx"] - b["w"] / 2)
        x1 = max(a["cx"] + a["w"] / 2, b["cx"] + b["w"] / 2)
        y0 = min(a["cy"] - a["h"] / 2, b["cy"] - b["h"] / 2)
        y1 = max(a["cy"] + a["h"] / 2, b["cy"] + b["h"] / 2)
        if (x1 - x0) * (y1 - y0) > 1.6 * (a["w"] * a["h"] + b["w"] * b["h"]):  # an L or a T: its bounding box is not a hall, keep the wings as two boxes
            del merged[bid]
            kept_apart.append((bid, tgt))
            continue
        merged[bid] = tgt
        b.update(cx=(x0 + x1) / 2, cy=(y0 + y1) / 2, w=x1 - x0, h=y1 - y0, ncols=b["ncols"] + a["ncols"], cells=b["cells"] + a["cells"])
    print("merges kept apart (L or T shapes):", kept_apart)
    return blocks, {"merged": merged, "rejected": rejected}


def dedupe_added(blocks: dict) -> int:
    """Two readers may add the same missed hall at an area edge; so can a reader and a detected block."""
    gone = 0
    ids = list(blocks)
    pts = np.array([[blocks[i]["cx"], blocks[i]["cy"]] for i in ids])
    for k, i in enumerate(ids):
        if "added" not in blocks[i]:
            continue
        d = np.hypot(*(pts - pts[k]).T)
        for j in np.where(d < 15)[0]:
            o = ids[j]
            if o != i and o in blocks and i in blocks and (("added" not in blocks[o]) or j < k):
                ratio = (blocks[i]["w"] * blocks[i]["h"]) / max(1, blocks[o]["w"] * blocks[o]["h"])
                if 0.5 < ratio < 2:
                    blocks[i]["duplicate_of"] = o
                    gone += 1
                    break
    return gone


def rect_ring(b: dict) -> list:
    c, s = math.cos(math.radians(b["ang"])), math.sin(math.radians(b["ang"]))
    return [(b["cx"] + u * c - v * s, b["cy"] + u * s + v * c) for u, v in ((-b["w"] / 2, -b["h"] / 2), (b["w"] / 2, -b["h"] / 2), (b["w"] / 2, b["h"] / 2), (-b["w"] / 2, b["h"] / 2))]


def bearing_of(b: dict, facing: str) -> float:
    """Compass bearing (deg clockwise from north) of the way the front faces. Plan y runs south, and the plan is turned from true north, so go through the warp."""
    a = math.radians(b["ang"])
    d = {"S": (-math.sin(a), math.cos(a)), "N": (math.sin(a), -math.cos(a)), "E": (math.cos(a), math.sin(a)), "W": (-math.cos(a), -math.sin(a))}[facing]
    lon0, lat0 = to_wgs(b["cx"], b["cy"])
    lon1, lat1 = to_wgs(b["cx"] + 40 * d[0], b["cy"] + 40 * d[1])
    x0, y0 = UTM.transform(lon0, lat0)
    x1, y1 = UTM.transform(lon1, lat1)
    return round(math.degrees(math.atan2(x1 - x0, y1 - y0)) % 360, 1)


def facing_of(b: dict, note: str, group_cx: float | None) -> tuple[str, bool]:
    """(facing, assumed). A reader's note wins. Default: a hall long E-W faces south, one long N-S faces east (side hall, either way possible)."""
    letters = re.findall(r"\b([SNEW])\b", (note or "").split("(")[0])
    if len(set(letters)) == 1:
        return letters[0], False
    if {"E", "W"} <= set(letters) and group_cx is not None:
        return ("E" if b["cx"] < group_cx else "W"), False
    if {"N", "S"} <= set(letters):
        return "S", True
    return ("S" if b["w"] >= b["h"] else "E"), True


def hall_class(type_: str, name: str, frontage: float, depth: float, cells: int) -> str:
    """Class name in research/typology/params.json, from what the row says and its size."""
    t, n = type_ or "", name or ""
    if t == "gate" or n.endswith("门"):
        return "gate_hall"
    if t == "tower" or n.endswith(("楼", "阁")):
        return "storeyed_hall"
    if t == "pavilion" or n.endswith(("亭", "榭")):
        return "pavilion_square"
    if t == "gallery" or n.endswith("廊"):
        return "gallery"
    long_, short = max(frontage, depth), min(frontage, depth)
    if short < 4.5 and long_ / max(short, 1) >= 4:
        return "gallery"
    if long_ >= 20 and short <= 9.5:  # a long low range of service rooms, not a great hall
        return "small_house"
    if long_ < 8 and long_ / max(short, 1) < 1.4:
        return "pavilion_square"
    if t == "temple" and long_ >= 25:
        return "temple_hall"
    if long_ >= 30:
        return "grand_hall"
    if long_ >= 16:
        return "main_hall"
    if long_ >= 12:
        return "side_hall"
    return "small_house"


# ---- main ----

def main() -> None:
    inv = {r["id"]: r for r in rows(PLAN / "inventory_texts.csv")}
    blocks, fix = load_blocks()
    added_dupes = dedupe_added(blocks)
    params = json.loads(Path("research/typology/params.json").read_text(encoding="utf-8"))

    # -- compounds --
    raw_comp = defaultdict(list)
    for a in AREAS:
        for r in rows(PLAN / "readings" / a / "compounds.csv"):
            if (a, r["id"]) in COMPOUND_DROP:
                continue
            raw_comp[r["id"]].append((a, r))

    # stable ids for compounds the texts do not list
    new_map = {}
    path = PLAN / "new_ids.csv"
    if path.exists():
        new_map = {r["reader_id"]: r["id"] for r in rows(path)}
    counters = Counter()
    for v in new_map.values():
        counters[v[:2]] = max(counters[v[:2]], int(v[2:]))
    for p, base in (("YM", 55), ("CC", 21), ("QC", 52)):
        counters[p] = max(counters[p], base)
    seen_new = {}
    for cid, lst in raw_comp.items():
        if cid in inv or not cid.startswith("NEW-") or cid in new_map:
            continue
        a, r = lst[0]
        nm = clean_name(r["name_on_plan"])
        xy = (float(r["plan_x"] or 0), float(r["plan_y"] or 0))
        pts = [tuple(map(float, q.split())) for q in r["polygon_px"].split(";") if q.strip()]
        pg = Polygon(pts).buffer(0) if len(pts) >= 3 else None
        hit = None
        for k, (n2, xy2, pg2) in seen_new.items():
            same_name = nm and n2 == nm and math.hypot(xy[0] - xy2[0], xy[1] - xy2[1]) < 200
            same_shape = pg is not None and pg2 is not None and pg.intersection(pg2).area > 0.5 * min(pg.area, pg2.area)
            if same_name or same_shape:
                hit = k
                break
        if hit:
            new_map[cid] = new_map[hit]
            continue
        seen_new[cid] = (nm, xy, pg)
        p = AREA_PREFIX[a]
        counters[p] += 1
        new_map[cid] = f"{p}{counters[p]:02d}"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["reader_id", "id"])
        w.writerows(sorted(new_map.items()))

    def remap(s: str) -> str:
        for k in sorted(new_map, key=len, reverse=True):
            s = s.replace(k, new_map[k])
        m = re.fullmatch(r"NEW-(\w+?)-(N?\d+)", s)
        return f"Z-{AREA_TAG[m[1]]}{m[2]}" if m else s

    comp = {}
    for cid, lst in raw_comp.items():
        fid = remap(cid)
        if cid in COMPOUND_OWNER:
            lst = [x for x in lst if x[0] == COMPOUND_OWNER[cid]] or lst
        lst = sorted(lst, key=lambda x: -READ_RANK.get(x[1]["read"], 0))
        a, best = lst[0]
        polys = []
        for _, r in (lst if cid in COMPOUND_UNION else [lst[0]]):
            if r["polygon_px"].strip():
                pts = [tuple(map(float, p.split())) for p in r["polygon_px"].split(";") if p.strip()]
                if len(pts) >= 3:
                    polys.append(Polygon(pts).buffer(0))
        poly = unary_union(polys) if polys else None
        if poly is not None and poly.geom_type == "MultiPolygon":
            poly = max(poly.geoms, key=lambda g: g.area) if cid not in COMPOUND_UNION else poly.buffer(25).buffer(-25)
            if poly.geom_type == "MultiPolygon":
                poly = max(poly.geoms, key=lambda g: g.area)
        if fid in comp:  # same place read twice as a new compound
            continue
        comp[fid] = {"id": fid, "reader_id": cid, "area": a, "row": best, "poly": poly, "read": best["read"], "x": best["plan_x"], "y": best["plan_y"], "name": clean_name(best["name_on_plan"]), "malone": best["malone_no"], "note": best["note"]}

    # -- 谐奇趣: Malone's known error, moved to the ruin --
    shift = xy01_shift(comp)

    # -- named rows --
    raw_named = defaultdict(list)
    for a in AREAS:
        for r in rows(PLAN / "readings" / a / "named.csv"):
            raw_named[remap(r["id"])].append((a, r))
    named = {}
    conflicts = []
    for nid, lst in raw_named.items():
        lst = sorted(lst, key=lambda x: -READ_RANK.get(x[1]["read"], 0))
        a, best = lst[0]
        best = dict(best)
        for _, o in lst[1:]:
            if not best["block_ids"].strip() and o["block_ids"].strip():
                best["block_ids"] = o["block_ids"]
                best["plan_x"], best["plan_y"] = o["plan_x"], o["plan_y"]
        if len(lst) > 1 and {x[1]["block_ids"] for x in lst} != {best["block_ids"]}:
            conflicts.append((nid, [(x[0], x[1]["block_ids"]) for x in lst]))
        best["parent_id"] = remap(best["parent_id"])
        best["area"] = a
        named[nid] = best

    # A block can belong to one row only; the first row in id order keeps it, the others keep their position.
    claimed = {}
    for nid in sorted(named):
        keep = []
        for b in re.split(r"[;\s]+", named[nid]["block_ids"].strip()):
            if not b:
                continue
            b = fix["merged"].get(b, b)
            if b in claimed and claimed[b] != nid:
                named[nid]["note"] += f" [shares block {b} with {claimed[b]}]"
                continue
            if b in blocks:
                claimed[b] = nid
                if b not in keep:
                    keep.append(b)
        named[nid]["blocks"] = keep

    # blocks a reader rejected stay rejected unless another reader named them
    gone = {b for b in fix["rejected"] if b not in claimed} | set(fix["merged"]) | {k for k, b in blocks.items() if "duplicate_of" in b and k not in claimed}
    live = {k: b for k, b in blocks.items() if k not in gone}

    # rects given in notes
    hill_rects = []
    for nid, n in named.items():
        if NOT_A_BUILDING_NOTE.search(n["note"]) or nid in HILL_RECTS or nid in DOCK_RECTS:
            n["not_building"] = True
            for b in n["blocks"]:
                claimed.pop(b, None)
                live.pop(b, None)
            n["blocks"] = []
            if nid in HILL_RECTS:
                m = re.search(r"rect=(\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?)", n["note"])
                hill_rects.append({"x1": n["plan_x"], "y1": n["plan_y"], "name_on_plan": HILL_RECTS[nid], "note": f"{m[1]} x {m[2]} rect read on the plan for {nid}"})
            continue
        m = re.search(r"rect=(\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?),\s*(-?\d+(?:\.\d+)?)", n["note"])
        if m and not n["blocks"] and n["plan_x"]:
            key = f"R-{nid}"
            live[key] = {"cx": float(n["plan_x"]), "cy": float(n["plan_y"]), "w": float(m[1]), "h": float(m[2]), "ang": float(m[3]), "ncols": int(n["ncols"] or 0), "nrows": int(n["nrows"] or 0), "cells": 0, "from_note": True}
            norm_block(live[key])
            n["blocks"] = [key]
            claimed[key] = nid

    # move the 谐奇趣 group
    if shift is not None:
        poly0 = comp["XY01"]["poly"]
        for k, b in live.items():
            if poly0 is not None and poly0.contains(Point(b["cx"], b["cy"])):
                b["cx"] += shift[0]
                b["cy"] += shift[1]
                b["moved"] = True
        for nid, n in named.items():
            if n["parent_id"] == "XY01" or nid == "XY01":
                if n["plan_x"]:
                    n["plan_x"], n["plan_y"] = float(n["plan_x"]) + shift[0], float(n["plan_y"]) + shift[1]
        c = comp["XY01"]
        c["x"], c["y"] = float(c["x"]) + shift[0], float(c["y"]) + shift[1]
        from shapely.affinity import translate

        c["poly"] = translate(poly0, shift[0], shift[1])

    # -- parent for unnamed blocks: the smallest compound that holds the centre --
    polys = [(c["poly"].area, cid, c["poly"]) for cid, c in comp.items() if c["poly"] is not None and cid not in NOT_A_SCENE]
    polys.sort(key=lambda t: t[0])

    def parent_of(x, y) -> str:
        p = Point(x, y)
        for _, cid, g in polys:
            if g.contains(p):
                return cid
        return ""

    # gardens by the wall rings
    walls = json.loads((PLAN / "walls.json").read_text(encoding="utf-8"))
    walls = walls if isinstance(walls, list) else walls["walls"]
    rings = {w["garden"]: Polygon(w["points"]).buffer(0) for w in walls if w.get("kind") == "outer_wall"}

    def garden_of(x, y, cid="") -> str:
        p = cid[:2]
        if p == "YM":
            return "Yuanming Yuan"
        if p == "CC":
            return "Changchun Yuan"
        if p == "XY":
            return "Xiyang Lou"
        if p == "QC":
            return "Qichun Yuan"
        pt = Point(x, y)
        for g, r in rings.items():
            if r.contains(pt):
                return g
        return "outside the walls"

    # -- rows --
    F = "id,parent_id,name_zh,name_pinyin,name_en,name_on_plan,read,garden,type,hall_class,built,changed,destroyed,sources,confidence,pos_confidence,lat,lon,pos_source,plan_x,plan_y,footprint_id,bays,bays_plan,frontage_m,depth_m,size_source,orientation_deg,orientation_assumed,storeys,roof,roof_tiles,rel_position,notes,size_lead".split(",")
    out = []
    footprints = []
    fp_counter = 0
    osm = {r["proposed_building_id"].strip(): r for r in rows(PLAN / "osm_points.csv") if r.get("proposed_building_id", "").strip() and r["trust"] == "plausible"}

    def add_footprints(rowid: str, parent: str, bids: list, row: dict, facing_note: str, conf: str, name: str, type_: str) -> tuple:
        """One footprint per block. Returns the first block's size and bearing, for the row."""
        nonlocal fp_counter
        first = None
        ids = []
        group_cx = float(np.mean([live[b]["cx"] for b in bids])) if bids else None
        for b in sorted(bids):
            bl = live[b]
            fp_counter += 1
            fid = f"F{fp_counter:04d}"
            ids.append(fid)
            facing, assumed = facing_of(bl, facing_note, group_cx)
            along_w = facing in "SN"
            front_px, depth_px = (bl["w"], bl["h"]) if along_w else (bl["h"], bl["w"])
            if depth_px / PX_PER_M_DEPTH > 2.5 * front_px / PX_PER_M_FRONTAGE and not rowid.startswith("XY"):  # a hall does not face along its long axis
                facing, assumed = {"S": "E", "N": "W", "E": "S", "W": "N"}[facing], True
                along_w = not along_w
                front_px, depth_px = depth_px, front_px
            frontage, depth = max(front_px / PX_PER_M_FRONTAGE, 2.0), max(depth_px / PX_PER_M_DEPTH, 2.0)
            ncols, nrows = (bl["ncols"], bl["nrows"]) if along_w else (bl["nrows"], bl["ncols"])
            bearing = bearing_of(bl, facing)
            ring = warp_ring(rect_ring(bl))
            props = {
                "id": fid, "building_id": rowid, "parent_id": parent, "name_zh": name, "block": b, "source_kind": "added by reader" if "added" in bl else ("rect read by reader" if "from_note" in bl else "detected"),
                "orientation_deg": bearing, "orientation_assumed": assumed, "frontage_m": round(frontage, 1), "depth_m": round(depth, 1),
                "drawn_m": [round(area_m2(ring) ** 0.5, 1)], "ncols": ncols or None, "nrows": nrows or None, "hall_class": hall_class(type_, name, frontage, depth, bl["cells"]),
                "sources": "S01", "confidence": conf, "note": "size = drawn px / hall scale (S01; typology section 2). Moved to the ruin, see Q on 谐奇趣" if bl.get("moved") else "size = drawn px / hall scale (S01; typology section 2)",
            }
            footprints.append(poly_feature([ring], props))
            if first is None:
                first = (frontage, depth, bearing, assumed, ncols, nrows, bl["cells"])
        return ids, first

    done_ids = set()

    def base_row(rid: str) -> dict:
        r = dict.fromkeys(F, "")
        s = inv.get(rid)
        r["id"] = rid
        if s:
            for k in ("parent_id", "name_zh", "name_pinyin", "name_en", "garden", "type", "built", "changed", "destroyed", "sources", "confidence", "bays", "frontage_m", "depth_m", "storeys", "roof", "roof_tiles", "rel_position"):
                r[k] = s.get(k, "")
            r["notes"] = s.get("notes", "")
            if rid in CHANGED_BY_1860 and r["confidence"] == "A":
                r["confidence"] = "B"
                r["notes"] = (r["notes"] + " Album does not show the 1860 state here (S41).").strip()
        return r

    def merge_src(r, *ids):
        cur = [x for x in r["sources"].split(";") if x]
        for i in ids:
            if i and i not in cur:
                cur.append(i)
        r["sources"] = ";".join(cur)

    def apply_size(r, first, type_, name):
        have_text = bool(r["frontage_m"] and r["depth_m"])
        if first:
            fr, de, br, assumed, nc, nr, cells = first
            r["orientation_deg"], r["orientation_assumed"] = br, assumed
            if nc:
                r["bays_plan"] = f"{nc}x{nr}"
            if not have_text:
                r["frontage_m"], r["depth_m"] = round(fr, 1), round(de, 1)
                r["size_source"] = "S01 plan px / hall scale"
            else:
                r["size_source"] = "text (see notes)"
            r["hall_class"] = hall_class(type_, name, float(r["frontage_m"]), float(r["depth_m"]), cells)
        elif have_text:
            r["size_source"] = "text (see notes)"

    # 1. compounds and inventory rows
    for rid in list(inv) + [c for c in comp if c not in inv]:
        r = base_row(rid)
        c = comp.get(rid)
        if not inv.get(rid):
            r["parent_id"] = ""
            r["name_zh"] = c["name"]
            r["name_pinyin"] = pinyin(c["name"])
            r["type"] = "compound"
            r["destroyed"] = "1860"
            r["sources"] = "S01"
            r["confidence"] = "C" if c["read"] == "guess" else "B"
            r["notes"] = ""
        n = named.get(rid)
        if c:
            r["name_on_plan"] = c["name"]
            r["read"] = c["read"]
            r["notes"] = (r["notes"] + " | plan: " + c["note"]).strip(" |") if c["note"] else r["notes"]
            if c["x"] and c["read"] != "not_found":
                r["plan_x"], r["plan_y"] = round(float(c["x"])), round(float(c["y"]))
                r["pos_source"] = f"S01 {c['read']}"
                r["pos_confidence"] = "C" if c["read"] == "guess" else "B"
                merge_src(r, "S01")
        if n:
            nm = clean_name(n["name_on_plan"])
            r["name_on_plan"] = nm or r["name_on_plan"]
            r["read"] = n["read"] if not c else c["read"]
            nnote = n["note"]
            r["notes"] = (r["notes"] + " | plan: " + nnote).strip(" |") if nnote else r["notes"]
            if n["plan_x"] and not r["plan_x"]:
                r["plan_x"], r["plan_y"] = round(float(n["plan_x"])), round(float(n["plan_y"]))
                r["pos_source"] = f"S01 {n['read']}"
                r["pos_confidence"] = "C" if n["read"] == "guess" else "B"
            elif n["blocks"] and not r["plan_x"]:
                b = live[n["blocks"][0]]
                r["plan_x"], r["plan_y"] = round(b["cx"]), round(b["cy"])
                r["pos_source"] = f"S01 {n['read']}"
                r["pos_confidence"] = "C" if n["read"] == "guess" else "B"
            merge_src(r, "S01")
            if n["read"] == "guess" and r["confidence"] != "A":
                r["confidence"] = "C"
            if not r["parent_id"] and n["parent_id"] and n["parent_id"] != rid:
                r["parent_id"] = n["parent_id"]
            type_ = r["type"]
            if type_ == "bridge":
                n["is_bridge"] = True
            elif n.get("not_building"):
                r["notes"] = (r["notes"] + " | no box: the plan shows a labelled plot, hill or dock here, not a hall").strip(" |")
            elif n["blocks"]:
                ids, first = add_footprints(rid, r["parent_id"], n["blocks"], r, n["orientation_note"], r["pos_confidence"] or "B", r["name_zh"] or nm, type_)
                r["footprint_id"] = ";".join(ids)
                apply_size(r, first, type_, r["name_zh"] or nm)
        if r["plan_x"] == "" and rid in osm:
            o = osm[rid]
            r["lat"], r["lon"] = round(float(o["lat"]), 6), round(float(o["lon"]), 6)
            r["pos_source"] = "S03 OSM point, not found on S01"
            r["pos_confidence"] = "C"
            merge_src(r, "S03")
        if r["plan_x"] != "":
            lon, lat = to_wgs(r["plan_x"], r["plan_y"])
            r["lat"], r["lon"] = round(lat, 6), round(lon, 6)
        out.append(r)
        done_ids.add(rid)

    # 2. named rows not in inventory
    for nid, n in sorted(named.items()):
        if nid in done_ids:
            continue
        r = base_row(nid)
        nm = clean_name(n["name_on_plan"])
        r["parent_id"] = n["parent_id"]
        r["name_zh"] = nm
        r["name_pinyin"] = pinyin(nm)
        r["name_on_plan"] = nm
        r["read"] = n["read"]
        r["destroyed"] = "1860"
        r["sources"] = "S01"
        r["confidence"] = "C" if n["read"] == "guess" else "B"
        r["notes"] = "plan: " + n["note"] if n["note"] else ""
        r["type"] = "gate" if nm.endswith("门") else ("pavilion" if nm.endswith(("亭", "榭")) else ("tower" if nm.endswith(("楼", "阁")) else ("temple" if nm.endswith(("庙", "寺", "殿", "祠", "庵")) else "other")))
        x, y = n["plan_x"], n["plan_y"]
        if n["blocks"]:
            b = live[n["blocks"][0]]
            x, y = b["cx"], b["cy"]
        if x != "":
            r["plan_x"], r["plan_y"] = round(float(x)), round(float(y))
            lon, lat = to_wgs(r["plan_x"], r["plan_y"])
            r["lat"], r["lon"] = round(lat, 6), round(lon, 6)
            r["pos_source"] = f"S01 {n['read']}"
            r["pos_confidence"] = "C" if n["read"] == "guess" else "B"
        if n["ncols"]:
            r["bays"] = n["ncols"]
        if n["blocks"]:
            ids, first = add_footprints(nid, r["parent_id"], n["blocks"], r, n["orientation_note"], r["pos_confidence"] or "B", nm, r["type"])
            r["footprint_id"] = ";".join(ids)
            apply_size(r, first, r["type"], nm)
        r["garden"] = garden_of(r["plan_x"] or 0, r["plan_y"] or 0, r["parent_id"] or nid)
        out.append(r)
        done_ids.add(nid)

    # 3. every other live block = an unnamed building on the plan
    unnamed = 0
    for k, b in sorted(live.items()):
        if k in claimed:
            continue
        parent = parent_of(b["cx"], b["cy"])
        tag = k
        m = re.match(r"A-(\w+)-(\d+)", k)
        if m:
            tag = f"A{AREA_TAG.get(m[1], m[1][0].upper())}{m[2]}"
        rid = f"{parent or 'Z'}-{tag}"
        r = base_row(rid)
        r["parent_id"] = parent
        r["type"] = "hall"
        r["destroyed"] = "1860"
        r["sources"] = "S01"
        r["confidence"] = "B"
        r["pos_confidence"] = "B"
        r["pos_source"] = "S01 block, unnamed"
        r["plan_x"], r["plan_y"] = round(b["cx"]), round(b["cy"])
        lon, lat = to_wgs(b["cx"], b["cy"])
        r["lat"], r["lon"] = round(lat, 6), round(lon, 6)
        r["garden"] = garden_of(b["cx"], b["cy"], parent)
        ids, first = add_footprints(rid, parent, [k], r, "", "B", "", "hall")
        r["footprint_id"] = ";".join(ids)
        apply_size(r, first, "hall", "")
        r["bays"] = (first[4] or "") if first else ""
        out.append(r)
        unnamed += 1

    # stated sizes win over the plan
    apply_by_name(out, params, footprints)

    # garden and class for rows that have none yet
    for r in out:
        if not r["garden"]:
            r["garden"] = garden_of(r["plan_x"] or 0, r["plan_y"] or 0, r["parent_id"] or r["id"])
        if r["garden"] == "Changchun Yuan (Xiyang Lou)":
            r["garden"] = "Xiyang Lou"

    out.sort(key=sort_key)
    with open("research/buildings.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, F, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)
    print("buildings.csv", len(out), "rows; unnamed blocks", unnamed, "; added blocks dropped as duplicates", added_dupes)
    print("named reader conflicts on blocks", conflicts)

    # -- layers --
    print("layers:")
    bname = {r["id"]: r for r in out}
    write_layer("footprints_1860", footprints)

    scenes = []
    for cid, c in sorted(comp.items()):
        if c["poly"] is None or cid in NOT_A_SCENE:
            continue
        g = c["poly"].simplify(1.0)
        ring = warp_ring(list(g.exterior.coords)[:-1])
        r = bname[cid]
        scenes.append(poly_feature([ring], {"id": cid, "name_zh": r["name_zh"], "name_pinyin": r["name_pinyin"], "name_en": r["name_en"], "name_on_plan": r["name_on_plan"], "garden": r["garden"], "read": c["read"], "malone_no": c["malone"], "area_m2": round(area_m2(ring)), "sources": r["sources"], "confidence": r["confidence"], "note": "outline drawn by the plan reader round the compound's island or court"}))
    write_layer("scenes_1860", scenes)

    water_layers(comp, bname, hill_rects)
    lines_layers(walls, named, live, bname)

    coverage(out, comp, footprints)


def xy01_shift(comp) -> tuple[float, float] | None:
    """OSM has an outline of the main block's ruin? Measured by the site worker: use the outline with name 谐奇趣 else the nearest ruin polygon to the OSM point."""
    d = json.loads((LAYERS / "osm_today.geojson").read_text(encoding="utf-8"))
    # OSM point 谐奇趣 is 42 m off its ruin (S03; site notes), so take the ruin polygon nearest that point.
    pt = None
    cands = []
    for f in d["features"]:
        p = f["properties"]
        if p.get("name") == "谐奇趣" and f["geometry"]["type"] == "Point":
            pt = Point(f["geometry"]["coordinates"])
        if f["geometry"]["type"] in ("Polygon", "MultiPolygon") and (p.get("historic") == "ruins" or p.get("building") == "ruins" or p.get("ruins")):
            g = Polygon(f["geometry"]["coordinates"][0]) if f["geometry"]["type"] == "Polygon" else MultiPolygon([Polygon(c[0]) for c in f["geometry"]["coordinates"]])
            cands.append((f["properties"].get("id"), p.get("name"), g))
    if pt is None or not cands:
        print("XY01: no ruin outline in OSM, group not moved")
        return None
    oid, nm, g = min(cands, key=lambda t: t[2].distance(pt))
    dist_m = g.distance(pt) * 111000
    lon, lat = g.centroid.x, g.centroid.y
    x, y = georef.wgs84_to_plan(np.array([lon]), np.array([lat]))
    c = comp["XY01"]
    sx, sy = float(x[0]) - float(c["x"]), float(y[0]) - float(c["y"])
    print(f"XY01 ruin {oid} name={nm} {dist_m:.0f} m from the OSM point; centre -> plan ({x[0]:.0f},{y[0]:.0f}); shift ({sx:.0f},{sy:.0f}) px = {math.hypot(sx, sy) / 4.77:.0f} m")
    if dist_m > 80 or math.hypot(sx, sy) > 450:
        print("XY01: ruin match too far, group not moved")
        return None
    return sx, sy


def apply_by_name(out, params, footprints) -> None:
    """Sizes stated in the typology win over the plan: by_name (key = hall name, `parent` = hint) and xiyang_lou (box or footprint_m, by id)."""
    fp_by_id = {f["properties"]["id"]: f["properties"] for f in footprints}

    def set_size(r, fr, de, src, what):
        if fr:
            r["frontage_m"] = fr
        if de:
            r["depth_m"] = de
        r["size_source"] = what
        for s in (src or "").split(";"):
            if s and s not in r["sources"].split(";"):
                r["sources"] += ";" + s
        for fid in [x for x in r["footprint_id"].split(";") if x][:1]:
            if fr:
                fp_by_id[fid]["frontage_m"] = fr
            if de:
                fp_by_id[fid]["depth_m"] = de
            fp_by_id[fid]["note"] = what

    bound, unbound = [], []
    for name, v in params["by_name"].items():
        if not v.get("frontage_m") and not v.get("depth_m"):
            continue
        short = BY_NAME_ALIAS.get(name, name.split(" ")[0])
        hits = [r for r in out if short in (r["name_zh"], r["name_on_plan"]) and r["parent_id"]]
        hint = str(v.get("parent") or "")[:4]
        hits.sort(key=lambda r: (r["parent_id"] != hint, not r["footprint_id"]))
        if not hits:
            hits = [r for r in out if short in (r["name_zh"], r["name_on_plan"])]
        if hits:
            set_size(hits[0], v.get("frontage_m"), v.get("depth_m"), v.get("sources"), f"stated: research/typology/params.json by_name[{name}]")
            bound.append(hits[0]["id"])
        else:
            unbound.append(name)
    for xid, v in params["xiyang_lou"].items():
        r = next((x for x in out if x["id"] == xid), None)
        if r is None:
            continue
        fr, de = None, None
        m = re.match(r"\s*(?:[^\d]*)(\d+(?:\.\d+)?) x (\d+(?:\.\d+)?)", str(v.get("box", "")))
        if v.get("footprint_m"):
            fr, de = v["footprint_m"][:2]
        elif m:
            fr, de = float(m[1]), float(m[2])
        if fr:
            set_size(r, fr, de, v.get("sources"), f"typology xiyang_lou, {v.get('confidence', 'C')}")
    print("sizes from by_name:", bound, "not bound:", unbound)


def sort_key(r):
    i = r["id"]
    order = {"YM": 0, "XY": 2, "CC": 1, "QC": 3, "Z-": 4}
    return (order.get(i[:2], 5), i)


def water_layers(comp, bname, hill_rects) -> None:
    data = json.loads((PLAN / "regions.json").read_text(encoding="utf-8"))
    regs = {r["region_id"]: r for r in data["regions"]}
    cls = {r["region_id"]: r for r in rows(PLAN / "regions_classified.csv")}
    names = {}
    hill_pts = []
    for a in AREAS:
        for r in rows(PLAN / "readings" / a / "features.csv"):
            k, rid = r["kind"], r["region_id"].strip()
            if k == "water_fix" and rid in cls:
                m = re.search(r"\b(water|island|land|hill|field|court|outside|wall_strip)\b", r["note"])
                if m:
                    cls[rid].update({"class": m[1], "confidence": "B", "note": (cls[rid].get("note", "") + " | fixed by reader " + a).strip(" |")})
            elif k in ("water_name", "island_name", "hill_name") and rid:
                names[rid] = clean_name(r["name_on_plan"]) or r["name_on_plan"]
            elif k == "hill":
                hill_pts.append(r)
    hill_pts += hill_rects
    feats = defaultdict(list)
    water_polys = []
    idn = Counter()
    prefix = {"water": "W", "island": "I", "hill": "H", "field": "FD"}
    # Round 25: traced water a later reading found to be land (research/plan/water_removed.json): dropped, its number kept taken so that the ids after it do not move
    removed = {r["region_id"] for r in json.loads((PLAN / "water_removed.json").read_text(encoding="utf-8"))} if (PLAN / "water_removed.json").exists() else set()
    for rid, c in sorted(cls.items()):
        k = c["class"]
        if k not in prefix or rid not in regs:
            continue
        if k == "water" and rid in removed:
            idn["water"] += 1
            continue
        reg = regs[rid]
        outer = reg["polygon"]
        holes = reg.get("holes") or []
        g = Polygon(outer, holes).buffer(0)
        if g.is_empty:
            continue
        if k == "water":
            water_polys.append(g)
        ring_sets = [warp_ring(outer)] + [warp_ring(h) for h in holes]
        idn[k] += 1
        nm = names.get(rid) or re.sub(r"\s+[A-Za-z].*$", "", c.get("name_zh", "") or "")
        if nm in LABEL_NOT_WATER:
            nm = ""
        conf = {"A": "B"}.get(c["confidence"], c["confidence"] or "C")  # S01 is at most B until Q2 is settled
        area = area_m2(ring_sets[0])
        kind = {"water": "canal" if reg.get("max_half_width_px", 99) < 40 else ("lake" if area > 15000 else "pond")}.get(k, k)
        props = {"id": f"{prefix[k]}{idn[k]:04d}", "region_id": rid, "kind": kind, "name_zh": nm, "name_pinyin": pinyin(nm) if nm else "", "area_m2": round(area), "sources": "S01", "confidence": conf, "note": c.get("note", "")}
        feats[k].append((g, ring_sets, props))
    # Round 19: water the tracer could not close (a canal drawn as two ink lines a few px apart), traced by hand in plan px: research/plan/water_manual.json.
    # Numbered after the traced bodies, so their ids do not move.
    # Round 27: `islands` false (a moat inside a compound) keeps a body out of the islands' water network, so that it does not cut an island and renumber the rest.
    for r in json.loads((PLAN / "water_manual.json").read_text(encoding="utf-8")) if (PLAN / "water_manual.json").exists() else []:
        g = Polygon(r["points"]).buffer(0)
        if r.get("islands", True):
            water_polys.append(g)
        idn["water"] += 1
        props = {"id": f"W{idn['water']:04d}", "region_id": r["region_id"], "kind": r["kind"], "name_zh": r["name_zh"], "name_pinyin": pinyin(r["name_zh"]) if r["name_zh"] else "",
                 "area_m2": round(area_m2(warp_ring(r["points"]))), "sources": "S01", "confidence": r["confidence"], "note": r["note"]}
        feats["water"].append((g, [warp_ring(r["points"])], props))
    write_layer("water_1860", [poly_feature(rs, p) for _, rs, p in feats["water"]])
    write_layer("fields_1860", [poly_feature(rs, p) for _, rs, p in feats["field"]])

    # islands: land wholly enclosed by the closed water network, plus the regions classed island by eye that are named
    all_water = unary_union(water_polys).buffer(ISLAND_CLOSING_PX).buffer(-ISLAND_CLOSING_PX)
    parts = all_water.geoms if all_water.geom_type == "MultiPolygon" else [all_water]
    holes = []
    for p in parts:
        for inner in p.interiors:
            h = Polygon(inner)
            if 1500 <= h.area <= 2_500_000:
                holes.append(h)
    named_comp = [(cid, c) for cid, c in comp.items() if c["x"] and c["read"] != "not_found"]
    isl = []
    for k, h in enumerate(sorted(holes, key=lambda g: -g.area), 1):
        ring = warp_ring(list(h.simplify(1.5).exterior.coords)[:-1])
        inside = [cid for cid, c in named_comp if h.contains(Point(float(c["x"]), float(c["y"])))]
        nm = bname[inside[0]]["name_zh"] if len(inside) == 1 else ""
        isl.append(poly_feature([ring], {"id": f"I{k:03d}", "name_zh": nm, "name_pinyin": bname[inside[0]]["name_pinyin"] if len(inside) == 1 else "", "scene_ids": ";".join(inside), "area_m2": round(area_m2(ring)), "sources": "S01", "confidence": "B", "note": "derived: land enclosed by the closed water layer; named after the compound on it where there is exactly one"}))
    n = len(isl)
    got = {i for f in isl for i in f["properties"]["scene_ids"].split(";")}
    for cid in ISLAND_FROM_SCENE:
        c = comp.get(cid)
        if cid in got or c is None or c["poly"] is None:
            continue
        n += 1
        ring = warp_ring(list(c["poly"].simplify(1.5).exterior.coords)[:-1])
        isl.append(poly_feature([ring], {"id": f"I{n:03d}", "name_zh": bname[cid]["name_zh"], "name_pinyin": bname[cid]["name_pinyin"], "scene_ids": cid, "area_m2": round(area_m2(ring)), "sources": "S01;S02", "confidence": "B", "note": "one of the nine islands (S02 p.52): outline is the reader's scene polygon, because a causeway keeps it from closing"}))
    write_layer("islands_1860", isl)

    # hills
    texts = [r for r in rows(PLAN / "hills_texts.csv") if r["lat"]]
    tx = np.array([UTM.transform(float(r["lon"]), float(r["lat"])) for r in texts])
    hills = []
    for g, rs, p in feats["hill"]:
        hills.append(hill_props(rs, p, tx, texts))
    n = len(hills)
    for r in hill_pts:
        if not r["x1"]:
            continue
        m = re.search(r"(\d+)\s*[x×]\s*(\d+)", r["note"])
        w, h = (float(m[1]), float(m[2])) if m else (120, 100)
        x, y = float(r["x1"]), float(r["y1"])
        ring = warp_ring([(x + w / 2 * math.cos(t), y + h / 2 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 16, endpoint=False)])
        n += 1
        nm = clean_name(r["name_on_plan"])
        hills.append(hill_props([ring], {"id": f"H{n:04d}", "region_id": "", "kind": "hill", "name_zh": nm, "name_pinyin": pinyin(nm), "area_m2": round(area_m2(ring)), "sources": "S01", "confidence": "C", "note": "outline approximated from reader's size: " + r["note"]}, tx, texts))
    write_layer("hills_1860", clear_of_courts(hills))


COURT_CLEAR_M = 5.0  # Q71: a hill read on the plan (C) gives way to a surveyed sunken court (research/xiyanglou/boxes.csv, shape court; S603)


def clear_of_courts(hills: list[dict]) -> list[dict]:
    """Trim the hills off the surveyed sunken courts of the Xiyang Lou (大水法's fountain area): a survey beats a C reading. A hill left with nothing is dropped."""
    from shapely.geometry import shape as shp
    from shapely.ops import transform as stf

    to_ll = Transformer.from_crs(32650, 4326, always_xy=True)
    courts = []
    with open(Path("research/xiyanglou/boxes.csv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["shape"] != "court":
                continue
            e, n = UTM.transform(float(r["lon"]), float(r["lat"]))
            t = math.radians(float(r["orientation_deg"]))
            fe, fn = math.sin(t), math.cos(t)  # facing
            ae, an = math.cos(t), -math.sin(t)  # across
            hf, hd = float(r["frontage_m"]) / 2, float(r["depth_m"]) / 2
            courts.append(Polygon([(e + sa * ae * hf + sb * fe * hd, n + sa * an * hf + sb * fn * hd) for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1))]).buffer(COURT_CLEAR_M))
    if not courts:
        return hills
    clear = unary_union(courts)
    out, trimmed, dropped = [], [], []
    for h in hills:
        g = stf(lambda x, y: UTM.transform(x, y), shp(h["geometry"]))
        if not g.intersects(clear):
            out.append(h)
            continue
        rest = g.difference(clear)
        if rest.is_empty or rest.area < 50:
            dropped.append(h["properties"]["id"])
            continue
        if rest.geom_type != "Polygon":
            rest = max(rest.geoms, key=lambda q: q.area)
        ring = [[round(a, 7), round(b, 7)] for a, b in (to_ll.transform(x, y) for x, y in rest.exterior.coords)]
        h["geometry"] = {"type": "Polygon", "coordinates": [ring]}
        h["properties"]["area_m2"] = round(rest.area)
        h["properties"]["note"] = (h["properties"].get("note", "") + " Trimmed clear of the surveyed sunken court of 大水法 (S603), Q71.").strip()
        trimmed.append(h["properties"]["id"])
        out.append(h)
    print(f"hills trimmed clear of the surveyed sunken courts: {trimmed}; dropped, nothing left: {dropped}")
    return out


def hill_props(rings, p, tx, texts) -> dict:
    a = np.array(rings[0]).mean(axis=0)
    x, y = UTM.transform(a[0], a[1])
    d = np.hypot(tx[:, 0] - x, tx[:, 1] - y)
    k = int(np.argmin(d))
    area = p["area_m2"]
    if d[k] < 120 and texts[k]["height_est_m"] and re.fullmatch(r"[\d.]+", texts[k]["height_est_m"]):
        p.update(height_est_m=float(texts[k]["height_est_m"]), height_method=texts[k]["height_method"], name_zh=p["name_zh"] or texts[k]["name_zh"], sources="S01;" + texts[k]["sources"])
    else:
        p.update(height_est_m=round(float(np.clip(math.sqrt(area) / 8, 3, 10)), 1), height_method="rule: sqrt(area)/8, clipped to 3-10 m; research/terrain/README.md; Attiret S157 gives 6-18 m", sources="S01;S157")
    p["confidence"] = "C"
    return poly_feature(rings, p)


# Q64 (Round 8). Changchun Yuan's west wall north of plan y about 2700 lies in the middle scroll's seam (x 8635-8660); the
# traced line at x 8690 was placed there by eye and runs through the plan's own maze hedge and 谐奇趣's west pavilion, and
# through their ruins. The ruins win: north of plan y 1900 the line moves west, square to itself, until every Xiyang Lou
# box (research/xiyanglou/boxes.csv, placed on the ruins in Round 6) stands at least WALL_CLEAR_M east of it; between
# y 1900 and 2400 it returns to the traced line. Gates on that run (the sluice 五孔闸, G43) move with it. The shift is
# printed, and recorded in research/questions.md (Q64).
WALL_CLEAR_M = 3.0
WALL_SEAM_RUN = {"W02": {"x": 8690.0, "top_y": 100.0, "full_below_y": 1900.0, "taper_to_y": 2400.0}}
WALL_RUN_GATE_PX = 40  # a gate this near the moved run (about 8 m) moves with it
WALL_MOVED = {}


def xy_box_polygons_utm() -> list:
    out = []
    with open(Path("research/xiyanglou/boxes.csv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            e, n = UTM.transform(float(r["lon"]), float(r["lat"]))
            t = math.radians(float(r["orientation_deg"]))
            fe, fn = math.sin(t), math.cos(t)
            ae, an = math.cos(t), -math.sin(t)
            hf, hd = float(r["frontage_m"]) / 2, float(r["depth_m"]) / 2
            out.append((r["building_id"], [(e + sa * ae * hf + sb * fe * hd, n + sa * an * hf + sb * fn * hd) for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1))]))
    return out


def wall_clear_of_ruins(w: dict):
    """The wall's points in UTM, with the seam run moved off the Xiyang Lou ruins (Q64); and what was moved, for the log."""
    rule = WALL_SEAM_RUN.get(w["id"])
    pts = [list(map(float, p)) for p in w["points"]]
    if rule:
        # Insert the taper's two vertices on the traced run, just before its last point (the ring closes at the top corner).
        k = max(i for i, p in enumerate(pts) if abs(p[0] - rule["x"]) < 1 and abs(p[1] - rule["top_y"]) < 1)
        pts = pts[:k] + [[rule["x"], rule["taper_to_y"]], [rule["x"], rule["full_below_y"]]] + pts[k:]
    e, n = georef.plan_to_utm(np.array([p[0] for p in pts]), np.array([p[1] for p in pts]))
    e, n = np.asarray(e, float), np.asarray(n, float)
    moved = None
    if rule:
        top = [i for i, p in enumerate(pts) if abs(p[0] - rule["x"]) < 1 and abs(p[1] - rule["top_y"]) < 1]
        low = next(i for i, p in enumerate(pts) if abs(p[1] - rule["full_below_y"]) < 1 and abs(p[0] - rule["x"]) < 1)
        a, b = np.array([e[low], n[low]]), np.array([e[top[0]], n[top[0]]])
        d = (b - a) / np.linalg.norm(b - a)
        west = np.array([-d[1], d[0]]) if -d[1] < 0 else np.array([d[1], -d[0]])  # square to the run, pointing west
        need = 0.0
        hit = set()
        for bid, poly in xy_box_polygons_utm():
            for q in poly:
                q = np.asarray(q)
                along = (q - a) @ d
                if -5 <= along <= np.linalg.norm(b - a) + 5:
                    s = (q - a) @ west  # metres west of the traced run
                    if s + WALL_CLEAR_M > need:
                        need = s + WALL_CLEAR_M
                    if s > -WALL_CLEAR_M:
                        hit.add(bid)
        if need > 0:
            for i in top + [low]:
                e[i], n[i] = e[i] + need * west[0], n[i] + need * west[1]
            moved = {"wall": w["id"], "shift_m": round(float(need), 1), "boxes_cleared": sorted(hit)}
            WALL_MOVED[w["id"]] = (rule, need * west)
    return e, n, moved


def gate_on_moved_run(x: float, y: float):
    """The shift (east, north metres) of a gate that stands on a moved wall run, else None."""
    for rule, vec in WALL_MOVED.values():
        if abs(x - rule["x"]) <= WALL_RUN_GATE_PX and rule["top_y"] - WALL_RUN_GATE_PX <= y <= rule["taper_to_y"]:
            t = 1.0 if y <= rule["full_below_y"] else (rule["taper_to_y"] - y) / (rule["taper_to_y"] - rule["full_below_y"])
            return vec * t
    return None


def lines_layers(walls, named, live, bname) -> None:
    out = []
    to_ll = Transformer.from_crs(32650, 4326, always_xy=True)
    for w in walls:
        e, n, moved = wall_clear_of_ruins(w)
        lon, lat = to_ll.transform(e, n)
        note = "read by eye, 10-20 px off the ink, Qichun 20-40 px; research/plan/walls.json"
        if moved:
            note += f". North of the plan's y 1700 the west side is moved {moved['shift_m']} m west, off the Xiyang Lou ruins of {', '.join(moved['boxes_cleared'])}: the plan's line there lies in a scroll seam (Q64)"
            print("wall moved off the Xiyang Lou ruins:", moved)
        out.append({"type": "Feature", "properties": {"id": w["id"], "kind": w["kind"], "garden": w["garden"], "sources": "S01" + (";S850" if moved else ""), "confidence": "B", "note": note}, "geometry": {"type": "LineString", "coordinates": [[round(float(u), 7), round(float(v), 7)] for u, v in zip(lon, lat)]}})
    gates = json.loads((PLAN / "gates.json").read_text(encoding="utf-8"))
    gates = gates if isinstance(gates, list) else gates["gates"]
    for g in gates:
        if g["id"] == "G22":
            g["label"], g["note"] = "蒨园门", g.get("note", "") + " Read by two readers as 蒨园门, the Changchun side; not 绮园门."
    extra = []
    for a in AREAS:
        for r in rows(PLAN / "readings" / a / "features.csv"):
            if r["kind"] == "gate" and r["x1"] and not (r["id"] or "").startswith("G"):
                x, y = float(r["x1"]), float(r["y1"])
                if all(math.hypot(g["x"] - x, g["y"] - y) > 40 for g in gates + extra):
                    extra.append({"id": f"G{len(gates) + len(extra) + 1:02d}", "label": clean_name(r["name_on_plan"]), "x": x, "y": y, "orientation_deg": None, "note": r["note"], "read": r["read"] or "none", "source": "S01"})
    for g in gates + extra:
        lon, lat = to_wgs(g["x"], g["y"])
        shift = gate_on_moved_run(g["x"], g["y"])
        if shift is not None:
            ge, gn = UTM.transform(lon, lat)
            lon, lat = to_ll.transform(ge + shift[0], gn + shift[1])
            g["note"] = (g.get("note", "") + f" Moved {np.hypot(*shift):.1f} m west with its wall run, off the Xiyang Lou ruins (Q64).").strip()
            print("gate moved with its wall run:", g["id"], round(float(np.hypot(*shift)), 1), "m")
        nm = g.get("label", "")
        out.append({"type": "Feature", "properties": {"id": g["id"], "kind": "gate", "name_zh": nm, "name_pinyin": pinyin(nm), "read": g.get("read", ""), "sources": "S01", "confidence": "B" if g.get("read") in ("sure", "likely") else "C", "note": g.get("note", "")}, "geometry": {"type": "Point", "coordinates": [round(lon, 7), round(lat, 7)]}})
    write_layer("walls_1860", out)

    br = []
    k = 0
    seen = []
    for a in AREAS:
        for r in rows(PLAN / "readings" / a / "features.csv"):
            if r["kind"] != "bridge" or not r["x1"]:
                continue
            x1, y1 = float(r["x1"]), float(r["y1"])
            x2, y2 = float(r["x2"] or x1), float(r["y2"] or y1)
            if any(math.hypot((x1 + x2) / 2 - sx, (y1 + y2) / 2 - sy) < 25 for sx, sy in seen):
                continue
            seen.append(((x1 + x2) / 2, (y1 + y2) / 2))
            k += 1
            lon, lat = georef.plan_to_wgs84(np.array([x1, x2]), np.array([y1, y2]))
            nm = clean_name(r["name_on_plan"])
            bid = r["id"] if r["id"] in bname else ""
            br.append({"type": "Feature", "properties": {"id": f"BR{k:03d}", "building_id": bid, "name_zh": nm or (bname[bid]["name_zh"] if bid else ""), "name_pinyin": pinyin(nm), "read": r["read"], "sources": "S01", "confidence": "C" if r["read"] == "guess" else "B", "note": r["note"]}, "geometry": {"type": "LineString", "coordinates": [[round(float(u), 7), round(float(v), 7)] for u, v in zip(lon, lat)]}})
    write_layer("bridges_1860", br)


def coverage(out, comp, footprints) -> None:
    tops = [r for r in out if not r["parent_id"]]
    tops_m = [r for r in tops if not r["id"].startswith("Z-")]
    halls = [r for r in out if r["parent_id"] or r["id"].startswith("Z-")]
    res = {
        "rows": len(out),
        "compounds": len(tops_m),
        "compounds_with_position": sum(1 for r in tops_m if r["lat"]),
        "compounds_with_polygon": sum(1 for c in comp.values() if c["poly"] is not None),
        "compounds_no_position": [r["id"] for r in tops_m if not r["lat"]],
        "forty_scenes_positioned": sum(1 for r in tops_m if re.fullmatch(r"YM(0[1-9]|[123]\d|40)", r["id"]) and r["lat"]),
        "xiyang_lou_positioned": sum(1 for r in tops_m if r["id"].startswith("XY") and r["lat"]),
        "halls_rows": len(halls),
        "halls_with_position": sum(1 for r in halls if r["lat"]),
        "halls_with_footprint": sum(1 for r in halls if r["footprint_id"]),
        "halls_named": sum(1 for r in halls if r["name_zh"]),
        "halls_named_with_footprint": sum(1 for r in halls if r["name_zh"] and r["footprint_id"]),
        "footprints": len(footprints),
        "by_garden": {},
    }
    for g in sorted({r["garden"] for r in out}):
        sel = [r for r in out if r["garden"] == g]
        res["by_garden"][g] = {
            "compounds": sum(1 for r in sel if r in tops_m),
            "compounds_positioned": sum(1 for r in sel if r in tops_m and r["lat"]),
            "halls": sum(1 for r in sel if r["parent_id"] or r["id"].startswith("Z-")),
            "halls_positioned": sum(1 for r in sel if (r["parent_id"] or r["id"].startswith("Z-")) and r["lat"]),
            "footprints": sum(len([x for x in r["footprint_id"].split(";") if x]) for r in sel),
        }
    # Check: where the plan puts a compound, against OSM's own hand-placed point for it (not used for the fit unless the point was also a control point).
    osm = {r["proposed_building_id"].strip(): r for r in rows(PLAN / "osm_points.csv") if r.get("proposed_building_id", "").strip() and r["trust"] == "plausible"}
    diffs = defaultdict(list)
    for r in tops_m:
        o = osm.get(r["id"])
        if o and r["lat"] and str(r["pos_source"]).startswith("S01"):
            a = UTM.transform(float(r["lon"]), float(r["lat"]))
            b = UTM.transform(float(o["lon"]), float(o["lat"]))
            diffs[r["garden"]].append(math.hypot(a[0] - b[0], a[1] - b[1]))
    res["plan_vs_osm_points_m"] = {g: {"n": len(v), "median": round(float(np.median(v))), "p90": round(float(np.percentile(v, 90)))} for g, v in diffs.items()}
    per = defaultdict(lambda: {"rows": 0, "footprints": 0, "named": 0})
    for r in out:
        p = r["parent_id"] or r["id"]
        per[p]["rows"] += 1
        per[p]["footprints"] += len([x for x in r["footprint_id"].split(";") if x])
        per[p]["named"] += 1 if r["name_zh"] and r["parent_id"] else 0
    res["per_compound"] = {r["id"]: {"name": r["name_zh"], "garden": r["garden"], "position": bool(r["lat"]), "read": r["read"], "halls_named": per[r["id"]]["named"], "footprints": per[r["id"]]["footprints"]} for r in tops_m}
    (PLAN / "coverage.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "per_compound"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
