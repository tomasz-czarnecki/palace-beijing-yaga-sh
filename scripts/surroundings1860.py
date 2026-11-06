"""Round 20: what stood and ran round the three gardens in 1860, as a layer and as the 3D view's massing.

  uv run python scripts/surroundings1860.py        (after build_r1.py and apply_facts.py; before publish_layers.py and ground1860.py)

Reads:
  research/surroundings/features.csv      hand-edited: one row per object outside the walls (id OW###, never renumbered), its kind, names, sources, grade, how its shape is given and how the view masses it
  research/surroundings/geometry.geojson  hand-edited: the lines and outlines a row's `geom` names as `geo` (properties.id), WGS84
  research/layers/osm_ring_today.geojson  today's outlines a row names as `osm:way/<id>` (ODbL; scripts/fetch_osm.py --ring)
  research/buildings.csv                  the rows S01 draws outside the walls (garden 'outside the walls', Z-..): linked, never renumbered
  research/layers/walls_1860, water_1860, footprints_1860, fields_1860   what the massing keeps clear of
Writes:
  research/layers/surroundings_1860.geojson   every object (OW.. and the linked Z- rows), WGS84, with kind, names, sources, confidence, assumed
  research/layers/water_1860.geojson          the lakes outside the walls appended (`outside: true`, ids W09xx from the sheet's layer_id); rewritten without them first
  research/layers/fields_1860.geojson         the fields and paddies outside the walls appended the same way (FD09xx)
  site/reconstruction/data/around_1860.json   the view's massing in scene metres: patches, strips, waters, blocks, halls, labels (site/reconstruction/around3d.js)
  research/surroundings/report.json           what the run made and kept clear, for tools/check_surroundings.py

`geom` forms: `pt:<lon> <lat>` (a point), `pt:<lon> <lat> r=<m>` (a point and an assumed round extent), `geo` (geometry.geojson), `osm:way/<id>` (today's outline), `row:<Z-id>` (a row of buildings.csv), `plan:<x> <y>` (S01 pixels through the fit of Round 8).
`pos_confidence` grades the position, `confidence` the object (that it was there, what it was); the view tints by the weaker. `reader` records which reader's row it came from (not published).
`massing` (k=v;...): houses=<n> (village, town), rows=<n>;per_row=<n>;side=<m> (banner camp), wall=1 (an outline wall), compound=<w>x<d> (temple, office, storehouse, workshop: a walled court with halls), halls=<n>, kit=1 (offices: the hall kit's side halls), mound=<m> (tomb), none.
Everything the massing generates (houses, barracks, halls of a compound with no plan) is `assumed: true`, grade C, whatever the grade of the object itself.
"""

import csv
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box, mapping, shape
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scene1860 import LAYERS, ROOT, SITE_DATA, ground_frame, layer, to_lonlat, to_xz  # noqa: E402

SHEET = ROOT / "research/surroundings/features.csv"
GEO = ROOT / "research/surroundings/geometry.geojson"
REPORT = ROOT / "research/surroundings/report.json"
OUT = LAYERS / "surroundings_1860.geojson"
VIEW = SITE_DATA / "around_1860.json"
OSM_RING = LAYERS / "osm_ring_today.geojson"
KINDS = {"neighbour_garden", "town", "village", "banner_camp", "office", "workshop", "storehouse", "temple", "road", "canal", "river", "sluice", "bridge", "field", "paddy", "orchard", "tomb", "hill_far", "lake", "spring", "other"}
LINE_KINDS = {"road", "canal", "river"}
WIDTH = {"road": 6.0, "canal": 10.0, "river": 15.0}  # m, when no source gives one. C
HOUSE = (11.0, 6.5, 3.6)  # a village house: frontage, depth, eave+roof height. The plan's small_house class outside the walls (S01, Z-B1175-1177: 8.6-11.5 x 6.3-6.9 m). C
HOUSE_GAP_M = 3.0
BARRACK = (33.0, 6.0, 3.8)  # one double row-house of a camp, ten bays of 3.3 m: the S01 guard house ?旗房 (Z-QN07) is a small_house of 3 bays; Swinhoe saw low houses (S241 p.286). C
CLEAR = {"wall": 4.0, "hall": 3.0, "water": 3.0, "road": 2.0}  # generated massing keeps this far from walls, halls, water and roads (m)
SITE_EPS = 0.5  # m: what counts as an overlap


def num(text, default=None):
    try:
        return float(text)
    except (TypeError, ValueError):
        return default


def seed_of(ident):
    return int(hashlib.sha1(ident.encode()).hexdigest()[:8], 16)


def xz_of(geom):
    return shapely.transform(geom, lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1])))


def ll_of(geom):
    return shapely.transform(geom, lambda c: np.column_stack(to_lonlat(c[:, 0], c[:, 1])))


def rounded(c, nd=7):
    if isinstance(c, (int, float)):
        return round(c, nd)
    return [rounded(v, nd) for v in c]


def parse_massing(text):
    out = {}
    for part in (text or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def load_osm():
    if not OSM_RING.exists():
        return {}
    return {f["properties"]["id"]: f for f in json.load(open(OSM_RING, encoding="utf-8"))["features"]}


def load_geo():
    if not GEO.exists():
        return {}
    return {f["properties"]["id"]: shape(f["geometry"]) for f in json.load(open(GEO, encoding="utf-8"))["features"]}


def geometry_of(r, osm, geo, rows):
    """WGS84 geometry and the extent radius (m) a point carries."""
    g = r["geom"].strip()
    if g.startswith("pt:"):
        bits = g[3:].split()
        lon, lat = float(bits[0]), float(bits[1])
        radius = next((float(b[2:]) for b in bits[2:] if b.startswith("r=")), None)
        return Point(lon, lat), radius
    if g == "geo":
        if r["id"] not in geo:
            raise SystemExit(f"{r['id']}: geom geo but no feature in {GEO.name}")
        return geo[r["id"]], None
    if g.startswith("osm:"):
        key = "osm-" + g[4:].replace("/", "-")
        if key not in osm:
            raise SystemExit(f"{r['id']}: {key} not in osm_ring_today")
        gg = shape(osm[key]["geometry"])
        if gg.geom_type == "LineString" and r["kind"] not in LINE_KINDS and gg.is_ring:
            gg = Polygon(gg.coords)
        if gg.geom_type == "MultiLineString" and r["kind"] not in LINE_KINDS:
            polys = list(shapely.polygonize(list(gg.geoms)).geoms)
            gg = unary_union(polys) if polys else gg
        return gg, None
    if g.startswith("row:"):
        row = rows[g[4:]]
        return Point(float(row["lon"]), float(row["lat"])), None
    if g.startswith("plan:"):
        import georef  # the fit of Round 8
        x, y = map(float, g[5:].split())
        lon, lat = georef.plan_to_wgs84([x], [y])
        return Point(float(lon[0]), float(lat[0])), None
    raise SystemExit(f"{r['id']}: geom '{g}' not understood")


class Clear:
    """What the massing keeps off: inside the walls, walls, halls, water, roads."""

    def __init__(self):
        walls = [xz_of(shape(f["geometry"])) for f in layer("walls_1860") if f["geometry"]["type"] == "LineString"]
        self.garden = unary_union([Polygon(w.coords).buffer(0) for w, f in zip(walls, [f for f in layer("walls_1860") if f["geometry"]["type"] == "LineString"]) if f["properties"]["kind"] == "outer_wall"])
        self.walls = unary_union(walls)
        self.halls = unary_union([xz_of(shape(f["geometry"])).buffer(0) for f in layer("footprints_1860")])
        self.water = unary_union([xz_of(shape(f["geometry"])).buffer(0) for f in layer("water_1860") if not f["properties"].get("outside")])
        self.roads = Polygon()
        self.blocked = unary_union([self.garden.buffer(CLEAR["wall"]), self.walls.buffer(CLEAR["wall"]), self.halls.buffer(CLEAR["hall"]), self.water.buffer(CLEAR["water"])])

    def add_roads(self, polys):
        self.roads = unary_union([self.roads, *polys])
        self.blocked = unary_union([self.blocked, self.roads.buffer(CLEAR["road"])])


def blob(c, r, rng, n=28):
    """An assumed round extent drawn as an irregular, seeded outline of about the same area: a guess either way, a circle only looks more exact."""
    k = rng.integers(2, 5)
    ph = rng.uniform(0, 2 * math.pi, 3)
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        f = 1 + 0.16 * math.sin(k * t + ph[0]) + 0.08 * math.sin((k + 2) * t + ph[1]) + 0.05 * math.sin(7 * t + ph[2])
        pts.append((c.x + r * f * math.cos(t), c.y + r * f * 0.82 * math.sin(t)))
    return Polygon(pts).buffer(0)


def rect(cx, cz, w, d, rot_deg):
    """A w (along the bearing's normal) x d rectangle; rot_deg the facing bearing as the kit's orientation_deg (0 = facing north, 90 = east, 180 = south)."""
    a = math.radians(rot_deg)
    # the facing direction in x (east), z (south): bearing 0 -> (0, -1)
    fx, fz = math.sin(a), -math.cos(a)
    rx, rz = -fz, fx
    hw, hd = w / 2, d / 2
    pts = [(cx + sx * hw * rx + sy * hd * fx, cz + sx * hw * rz + sy * hd * fz) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    return Polygon(pts)


def houses_in(area, n, rng, clear, size=HOUSE, facing=180.0):
    """n houses in an area, on a jittered lattice facing south (the north China house faces south), clear of everything. Returns (cx, cz, rot) triples."""
    w, d, _ = size
    if area.is_empty or n <= 0:
        return []
    x0, z0, x1, z1 = area.bounds
    sx, sz = w + HOUSE_GAP_M * 2, d + HOUSE_GAP_M * 3  # lanes run east-west between the rows of houses
    cand = [(x, z) for z in np.arange(z0 + sz / 2, z1, sz) for x in np.arange(x0 + sx / 2, x1, sx)]
    rng.shuffle(cand)
    out = []
    taken = []
    prepared = shapely.prepared.prep(area)
    for x, z in cand:
        if len(out) >= n:
            break
        x += rng.uniform(-1.5, 1.5)
        z += rng.uniform(-1.0, 1.0)
        p = rect(x, z, w, d, facing)
        if not prepared.contains(p) or p.intersects(clear.blocked):
            continue
        out.append((x, z, facing))
        taken.append(p)
    return out


def wall_blocks(outline, h, thick, ident, tint="wall"):
    """An outline wall as blocks along its ring, about 20 m each."""
    out = []
    ring = outline.exterior if outline.geom_type == "Polygon" else outline
    L = ring.length
    n = max(int(L // 20), 4)
    for k in range(n):
        a, b = ring.interpolate(k * L / n), ring.interpolate((k + 1) * L / n)
        dx, dz = b.x - a.x, b.y - a.y
        seg = math.hypot(dx, dz)
        if seg < 0.5:
            continue
        rot = (math.degrees(math.atan2(dx, -dz)) + 90) % 360  # the block's frontage runs along the wall
        out.append({"id": ident, "x": round((a.x + b.x) / 2, 2), "z": round((a.y + b.y) / 2, 2), "w": round(seg + thick, 2), "d": thick, "h": h, "rot": round(rot, 2), "roof": "none", "tint": tint})
    return out


def main():
    global SHEET, GEO, OUT, VIEW, REPORT
    test = "--test" in sys.argv  # a dry run into the scratch folder: the sheet given after --test, nothing in the repo written
    if test:
        sc = Path("/opt/data/cache/scratch/palace_r20_surroundings_test")
        sc.mkdir(parents=True, exist_ok=True)
        SHEET = Path(sys.argv[sys.argv.index("--test") + 1])
        GEO = SHEET.with_name("geometry.geojson")
        OUT, VIEW, REPORT = sc / "surroundings_1860.geojson", sc / "around_1860.json", sc / "report.json"
    rows = {r["id"]: r for r in csv.DictReader(open(ROOT / "research/buildings.csv", encoding="utf-8", newline=""))}
    sheet = list(csv.DictReader(open(SHEET, encoding="utf-8", newline="")))
    osm, geo = load_osm(), load_geo()
    x0, z0, x1, z1 = ground_frame()
    domain = box(x0, z0, x1, z1)
    clear = Clear()
    gates = {f["properties"]["id"]: xz_of(shape(f["geometry"])) for f in layer("walls_1860") if f["geometry"]["type"] == "Point"}
    ways = {f["properties"]["id"]: xz_of(shape(f["geometry"])) for f in layer("paths_1860")}

    seen = set()
    feats, view = [], {"features": [], "patches": [], "strips": [], "waters": [], "blocks": [], "halls": [], "labels": []}
    lakes, fields = [], []
    joins = []
    lines_done = {}
    made = Counter()
    # The lakes outside the walls this sheet draws are kept clear from the start, whatever their place in the sheet.
    for r in sheet:
        if r["kind"].strip() == "lake":
            gl, rl = geometry_of(r, osm, geo, rows)
            gx = xz_of(gl)
            clear.blocked = unary_union([clear.blocked, (gx.buffer(rl, 16) if rl else gx).buffer(CLEAR["water"])])
            clear.lakes = unary_union([getattr(clear, "lakes", Polygon()), gx.buffer(rl, 16) if rl else gx])
    done = [0, 0]
    for r in sheet:
        # What earlier rows built is kept clear by the later ones: the sheet's order is the order of precedence (sourced and small first, villages last). Thin walls do not block.
        fresh = view["blocks"][done[0]:] + view["halls"][done[1]:]
        if fresh:
            clear.blocked = unary_union([clear.blocked] + [rect(b["x"], b["z"], b["w"], b["d"], b["rot"]).buffer(2.0) for b in fresh if b["d"] > 1.5 and b["w"] > 1.5])
            done = [len(view["blocks"]), len(view["halls"])]
        ident = r["id"].strip()
        if ident in seen:
            raise SystemExit(f"{ident} twice in the sheet")
        seen.add(ident)
        kind = r["kind"].strip()
        if kind not in KINDS:
            raise SystemExit(f"{ident}: kind {kind}")
        g_ll, radius = geometry_of(r, osm, geo, rows)
        g = xz_of(g_ll)
        assumed = r["assumed"].strip().lower() == "true"
        width = num(r["width_m"], WIDTH.get(kind))
        m = parse_massing(r["massing"])
        props = {"id": ident, "kind": kind, "name_zh": r["name_zh"], "name_pinyin": r["name_pinyin"], "name_en": r["name_en"], "sources": r["sources"], "confidence": r["confidence"], "pos_confidence": r["pos_confidence"], "assumed": assumed,
                 "state_1860": r["state_1860"], "size": r["size"], "position_basis": r["position_basis"], "note": r["note"]}
        if width and kind in LINE_KINDS:
            props["width_m"] = width
        if r["geom"].startswith("row:"):
            props["row_id"] = r["geom"][4:]
        if radius:
            props["extent_r_m"] = radius
        if r["joins"]:
            props["joins"] = r["joins"]
        out_geom = g_ll
        if radius and g.geom_type == "Point":
            out_geom = ll_of(blob(g, radius, np.random.default_rng(seed_of(ident))))
            props["extent_assumed"] = True
        feats.append({"type": "Feature", "properties": props, "geometry": mapping(out_geom)})
        view["features"].append({"id": ident, "kind": kind, "name_zh": r["name_zh"], "name_pinyin": r["name_pinyin"], "name_en": r["name_en"], "conf": max(r["confidence"], r["pos_confidence"]), "assumed": assumed})  # the view's tint: the weaker of what it was and where it stood
        rng = np.random.default_rng(seed_of(ident))
        area = blob(g, radius, rng) if radius and g.geom_type == "Point" else g if g.geom_type in ("Polygon", "MultiPolygon") else None

        # Lines: roads, canals, rivers. A join snaps the named end onto a gate, a way's end or another line.
        if kind in LINE_KINDS:
            lines = [g] if g.geom_type == "LineString" else list(g.geoms)
            for spec in filter(None, (r["joins"] or "").split(";")):
                end, target = spec.split("@") if "@" in spec else ("auto", spec)
                tgt = gates.get(target) or ways.get(target) or lines_done.get(target)
                if tgt is None:
                    raise SystemExit(f"{ident}: joins {target}, which is no gate, way or earlier line")
                ln = lines[0]
                ends = {"start": Point(ln.coords[0]), "end": Point(ln.coords[-1])}
                which = end if end in ends else min(ends, key=lambda k: ends[k].distance(tgt))
                if target in lines_done:  # onto the other line, at its nearest point
                    best = lines_done[target].interpolate(lines_done[target].project(ends[which]))
                else:  # a gate, or the nearer end of a way
                    cands = [Point(c) for c in tgt.coords] if tgt.geom_type == "Point" else [Point(tgt.coords[0]), Point(tgt.coords[-1])]
                    best = min(cands, key=lambda q: q.distance(ends[which]))
                gap_before = ends[which].distance(best)
                cs = list(ln.coords)
                cs[0 if which == "start" else -1] = (best.x, best.y)
                lines[0] = LineString(cs)
                joins.append({"id": ident, "target": target, "end": which, "gap_before_m": round(gap_before, 2), "confidence": r["confidence"]})
            lines_done[ident] = unary_union(lines) if len(lines) > 1 else lines[0]
            for ln in lines:
                view["strips"].append({"id": ident, "kind": kind, "w": width, "pts": [[round(x, 2), round(z, 2)] for x, z in ln.coords]})
            if kind == "road":
                clear.add_roads([ln.buffer(width / 2) for ln in lines])
            else:  # no house on a canal or a river
                clear.blocked = unary_union([clear.blocked] + [ln.buffer(width / 2 + 3) for ln in lines])
            made[f"strip:{kind}"] += len(lines)
            g_new = unary_union(lines)
            feats[-1]["geometry"] = mapping(ll_of(g_new))
            continue

        # Areas drawn as ground: fields, paddies, orchards, lakes.
        if kind in ("field", "paddy", "orchard"):
            a = (area if area is not None else g.buffer(radius or 60, 16)).difference(clear.garden.buffer(CLEAR["wall"])).difference(clear.halls.buffer(CLEAR["hall"])).difference(clear.water).difference(clear.roads)
            for p in getattr(a, "geoms", [a]):
                if p.area < 50:
                    continue
                view["patches"].append({"id": ident, "kind": kind, "ring": [[round(x, 1), round(z, 1)] for x, z in p.exterior.coords], "holes": [[[round(x, 1), round(z, 1)] for x, z in h.coords] for h in p.interiors]})
            fields.append((r, ll_of(a)))
            made[f"patch:{kind}"] += 1
            continue
        if kind == "lake":
            a = area if area is not None else g.buffer(radius or 50, 16)
            lakes.append((r, ll_of(a)))
            level = num(m.get("level"))
            view["waters"].append({"id": ident, "ring": [[round(x, 1), round(z, 1)] for x, z in a.exterior.coords], "level": level})
            made["water"] += 1
            continue

        # Linked rows of S01: their boxes stand already (the kit draws them); the layer carries them and a label.
        if r["geom"].startswith("row:"):
            made["row"] += 1
            if r["name_zh"]:
                view["labels"].append({"id": ident, "x": round(g.x, 1), "z": round(g.y, 1), "text": r["name_zh"], "sub": r["name_pinyin"], "rank": 3})
            continue

        c = g.centroid if g.geom_type != "Point" else g
        if m.get("none") == "1" or "none" in (r["massing"] or "").split(";"):
            made["record_only"] += 1  # in the layer and the panel, nothing in the view (the lines of October 1860, places with no extent)
            continue
        rank = {"neighbour_garden": 1, "town": 1, "hill_far": 1, "banner_camp": 2, "village": 2, "temple": 3}.get(kind, 3)
        if r["name_zh"] or r["name_en"]:
            label_at = g.representative_point() if g.geom_type in ("Polygon", "MultiPolygon") else c
            view["labels"].append({"id": ident, "x": round(label_at.x, 1), "z": round(label_at.y, 1), "text": r["name_zh"] or r["name_en"], "sub": r["name_pinyin"] or r["name_en"], "rank": rank})
        if kind == "hill_far":
            made["label_only"] += 1
            continue

        for spec in filter(None, m.get("parts", "").split("|")):  # explicit blocks: "lon lat WxDxH[xROT]", each assumed unless the row says otherwise
            lon_s, lat_s, dims = spec.split()
            dd = [float(v) for v in dims.split("x")]
            px, pz = to_xz(float(lon_s), float(lat_s))
            view["blocks"].append({"id": ident, "x": round(float(px), 2), "z": round(float(pz), 2), "w": dd[0], "d": dd[1], "h": dd[2], "rot": dd[3] if len(dd) > 3 else 180.0, "roof": m.get("roof", "hip"), "tint": "garden" if kind == "neighbour_garden" else "temple" if kind == "temple" else "office", "assumed": True})
            made["parts"] += 1
        if area is not None and m.get("wall") == "1":
            ws = wall_blocks(area.buffer(0) if area.geom_type == "Polygon" else max(getattr(area, "geoms", [area]), key=lambda p: p.area), num(m.get("wall_h"), 3.5), 1.0, ident, "garden" if kind == "neighbour_garden" else "wall")
            ws = [b for b in ws if not rect(b["x"], b["z"], b["w"], b["d"], b["rot"]).intersects(clear.garden.buffer(1.0)) and not rect(b["x"], b["z"], b["w"], b["d"], b["rot"]).intersects(clear.halls) and not rect(b["x"], b["z"], b["w"], b["d"], b["rot"]).intersects(getattr(clear, "lakes", Polygon()))]
            view["blocks"] += ws
            made["wall_blocks"] += len(ws)

        if kind in ("village", "town"):
            n = int(num(m.get("houses"), 12))
            a = area if area is not None else c.buffer(80 if kind == "village" else 250, 24)
            hs = houses_in(a, n, rng, clear)
            for x, z, rot in hs:
                view["blocks"].append({"id": ident, "x": round(x, 2), "z": round(z, 2), "w": HOUSE[0], "d": HOUSE[1], "h": HOUSE[2], "rot": rot, "roof": "gable", "tint": "village", "assumed": True})
            if not radius:  # an outline from a map: its ground tinted; an assumed extent only its houses
                pa = a.difference(clear.garden.buffer(CLEAR["wall"])).buffer(0)
                for q in getattr(pa, "geoms", [pa]):
                    view["patches"].append({"id": ident, "kind": kind, "ring": [[round(x, 1), round(z, 1)] for x, z in q.exterior.coords], "holes": []})
            made[f"houses:{kind}"] += len(hs)
            continue
        if kind == "banner_camp":
            nrows, per = int(num(m.get("rows"), 6)), int(num(m.get("per_row"), 8))
            a = area if area is not None else rect(c.x, c.y, per * (BARRACK[0] + 3) + 16, nrows * (BARRACK[1] + 8) + 16, 180.0)  # the rows as the count gives them, lanes of 8 m, a margin inside the wall
            a = a.difference(clear.blocked.difference(clear.roads.buffer(CLEAR["road"])))
            a = a.difference(clear.garden.buffer(CLEAR["wall"]))
            a = max(getattr(a, "geoms", [a]), key=lambda p: p.area)
            view["blocks"] += [b for b in wall_blocks(a, 3.0, 1.0, ident, "camp") if not rect(b["x"], b["z"], b["w"], b["d"], b["rot"]).intersects(clear.halls.buffer(1.0))]
            bx0, bz0, bx1, bz1 = a.buffer(-8).bounds
            k = 0
            for i in range(nrows):
                z = bz0 + (i + 0.5) * (bz1 - bz0) / nrows
                for j in range(per):
                    x = bx0 + (j + 0.5) * (bx1 - bx0) / per
                    w = min(BARRACK[0], (bx1 - bx0) / per - 3)
                    x += rng.uniform(-0.5, 0.5)
                    p = rect(x, z, w, BARRACK[1], 180.0)
                    if w < 4 or not a.contains(p) or p.intersects(clear.blocked):
                        continue
                    view["blocks"].append({"id": ident, "x": round(x, 2), "z": round(z, 2), "w": round(w, 2), "d": BARRACK[1], "h": BARRACK[2], "rot": 180.0, "roof": "gable", "tint": "camp", "assumed": True})
                    k += 1
            view["patches"].append({"id": ident, "kind": "camp", "ring": [[round(x, 1), round(z, 1)] for x, z in a.exterior.coords], "holes": []})
            made["barracks"] += k
            continue
        if kind in ("temple", "office", "storehouse", "workshop") or "compound" in m:
            cw, cd = (float(v) for v in m.get("compound", "40x60").split("x"))
            facing = num(m.get("facing"), 180.0)
            a = area if area is not None else rect(c.x, c.y, cw, cd, facing)
            if a.intersects(clear.garden):
                a = a.difference(clear.garden.buffer(CLEAR["wall"]))
                a = max(getattr(a, "geoms", [a]), key=lambda p: p.area)
            view["blocks"] += [b for b in wall_blocks(a, 3.0, 0.8, ident, "temple" if kind == "temple" else "wall") if not rect(b["x"], b["z"], b["w"], b["d"], b["rot"]).intersects(clear.halls.buffer(1.0)) and not rect(b["x"], b["z"], b["w"], b["d"], b["rot"]).intersects(clear.garden.buffer(1.0))]  # a court's wall stops at a hall of the plan and at the gardens' wall
            nh = int(num(m.get("halls"), 3))
            cx, cz = a.centroid.x, a.centroid.y
            ax, az = math.sin(math.radians(facing)), -math.cos(math.radians(facing))  # toward the front
            L = math.sqrt(a.area) * 0.7
            for k in range(nh):
                t = (k - (nh - 1) / 2) * L / max(nh, 1)
                hx, hz = cx - ax * t, cz - az * t
                cls = "side_hall" if m.get("kit") == "1" and k else "main_hall"
                bays = 5 if k == 0 or kind != "temple" else 3
                w, d = (bays * 3.6, 9.0) if cls == "main_hall" else (bays * 3.3, 6.6)
                p = rect(hx, hz, w, d, facing)
                if not a.contains(p) or p.intersects(clear.blocked):
                    continue
                if m.get("kit") == "1":
                    view["halls"].append({"id": ident, "x": round(hx, 2), "z": round(hz, 2), "w": w, "d": d, "rot": facing, "cls": cls, "bays": bays, "assumed": True})
                else:
                    view["blocks"].append({"id": ident, "x": round(hx, 2), "z": round(hz, 2), "w": w, "d": d, "h": 5.0 if k == 0 else 4.2, "rot": facing, "roof": "hip", "tint": "temple" if kind == "temple" else "office", "assumed": True})
                made[f"halls:{kind}"] += 1
            if m.get("kit") == "1":  # side halls either side of the court's axis
                for sgn in (-1, 1):
                    rx, rz = -az, ax
                    hx, hz = cx + sgn * rx * (math.sqrt(a.area) * 0.32), cz + sgn * rz * (math.sqrt(a.area) * 0.32)
                    p = rect(hx, hz, 3 * 3.3, 6.6, (facing + 90 * sgn) % 360)
                    if a.contains(p) and not p.intersects(clear.blocked):
                        view["halls"].append({"id": ident, "x": round(hx, 2), "z": round(hz, 2), "w": 9.9, "d": 6.6, "rot": (facing - 90 * sgn) % 360, "cls": "side_hall", "bays": 3, "assumed": True})
                        made[f"halls:{kind}"] += 1
            view["patches"].append({"id": ident, "kind": "temple" if kind == "temple" else "office", "ring": [[round(x, 1), round(z, 1)] for x, z in a.exterior.coords], "holes": []})
            continue
        if kind == "neighbour_garden":
            for k, spec in enumerate(filter(None, m.get("blocks", "").split("|"))):
                w, d, h = (float(v) for v in spec.split("x"))
                p = a = area if area is not None else c.buffer(100)
                pt = (area if area is not None else c.buffer(100)).representative_point()
                view["blocks"].append({"id": ident, "x": round(pt.x + k * (w + 10), 2), "z": round(pt.y, 2), "w": w, "d": d, "h": h, "rot": 180.0, "roof": "hip", "tint": "garden", "assumed": True})
            if area is not None:
                if m.get("within"):  # the garden's ground only within this distance of its lakes: today's outline holds later additions
                    area = area.intersection(getattr(clear, "lakes", Polygon()).buffer(float(m["within"])))
                ga = area.buffer(-100).buffer(100).difference(getattr(clear, "lakes", Polygon()))  # opened by 100 m: today's outlines carry thin strips (颐和园's wedge towards 玉泉山) that are no garden ground.difference(clear.garden.buffer(CLEAR["wall"])).buffer(0)  # the garden's ground, not its lake
                for q in getattr(ga, "geoms", [ga]):
                    if q.area > 100:
                        view["patches"].append({"id": ident, "kind": "garden", "ring": [[round(x, 1), round(z, 1)] for x, z in q.exterior.coords], "holes": [[[round(x, 1), round(z, 1)] for x, z in h.coords] for h in q.interiors]})
            made["garden"] += 1
            continue
        if kind == "tomb":
            s = num(m.get("mound"), 6.0)
            view["blocks"].append({"id": ident, "x": round(c.x, 2), "z": round(c.y, 2), "w": s, "d": s, "h": s * 0.35, "rot": 0.0, "roof": "mound", "tint": "tomb", "assumed": assumed})
            made["tomb"] += 1
            continue
        if kind == "sluice":
            w = num(m.get("w"), 12.0)
            view["blocks"].append({"id": ident, "x": round(c.x, 2), "z": round(c.y, 2), "w": w, "d": 4.0, "h": 1.6, "rot": num(m.get("rot"), 0.0), "roof": "flat", "tint": "stone", "assumed": assumed})
            made["sluice"] += 1
            continue
        if kind == "bridge":
            w = num(m.get("w"), 14.0)
            view["blocks"].append({"id": ident, "x": round(c.x, 2), "z": round(c.y, 2), "w": w, "d": num(m.get("d"), 6.0), "h": 0.9, "rot": num(m.get("rot"), 0.0), "roof": "flat", "tint": "stone", "assumed": assumed})
            made["bridge"] += 1
            continue
        made[f"point:{kind}"] += 1

    # The Z- rows outside the walls that the sheet does not name: carried as they are, linked by their own id.
    named_rows = {f["properties"].get("row_id") for f in feats}
    for rid, row in rows.items():
        if row["garden"] == "outside the walls" and rid not in named_rows:
            feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [float(row["lon"]), float(row["lat"])]},
                          "properties": {"id": rid, "kind": "other", "row_id": rid, "name_zh": row["name_zh"], "name_pinyin": row["name_pinyin"], "name_en": row["name_en"], "sources": row["sources"], "confidence": row["confidence"], "pos_confidence": row["pos_confidence"] or "B", "assumed": False,
                                         "state_1860": "", "size": "", "position_basis": row["pos_source"], "note": "S01 draws it outside the walls; its box and page are those of buildings.csv"}})
            made["row"] += 1

    # Gaps of the joins, measured on what is written.
    for j in joins:
        f = next(f for f in feats if f["properties"]["id"] == j["id"])
        ln = xz_of(shape(f["geometry"]))
        ln = ln if ln.geom_type == "LineString" else ln.geoms[0]
        endp = Point(ln.coords[0] if j["end"] == "start" else ln.coords[-1])
        tgt = gates.get(j["target"]) or ways.get(j["target"]) or lines_done.get(j["target"])
        if j["target"] in lines_done:
            j["gap_m"] = round(endp.distance(tgt), 3)
        else:
            cands = [tgt.coords[0]] if tgt.geom_type == "Point" else [tgt.coords[0], tgt.coords[-1]]
            j["gap_m"] = round(min(endp.distance(Point(c)) for c in cands), 3)

    # Water and fields beyond the walls into the layers of 1860 (their own ids, `outside: true`), the earlier copies first removed.
    for name, items, kind_of in (("water_1860", lakes, lambda r: "lake"), ("fields_1860", fields, lambda r: r["kind"])):
        path = LAYERS / f"{name}.geojson"
        fc = json.load(open(path, encoding="utf-8"))
        fc["features"] = [f for f in fc["features"] if not f["properties"].get("outside")]
        for r, gg in items:
            lid = r["layer_id"].strip()
            if not lid:
                raise SystemExit(f"{r['id']}: a {r['kind']} needs a layer_id for {name}")
            area = float(xz_of(gg).area)
            fc["features"].append({"type": "Feature", "properties": {"id": lid, "region_id": "", "kind": kind_of(r), "name_zh": r["name_zh"], "name_pinyin": r["name_pinyin"], "area_m2": round(area), "sources": r["sources"], "confidence": r["confidence"],
                                                                     "note": f"outside the walls, Round 20: {r['id']} in surroundings_1860", "outside": True, "surroundings_id": r["id"], **({"level_m": num(parse_massing(r["massing"]).get("level"))} if parse_massing(r["massing"]).get("level") else {})},
                                   "geometry": {"type": gg.geom_type, "coordinates": rounded(mapping(gg)["coordinates"])}})
        text = json.dumps(fc, ensure_ascii=False, separators=(",", ":"))  # as scripts/build_r1.py writes it: with nothing outside, the file is byte for byte its own
        if test:
            path = OUT.with_name(f"{name}.geojson")
            path.write_text(text, encoding="utf-8")
        elif path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8")

    # Generated massing never stands in a lake outside the walls: a block of a wall or a court that a lake's outline crosses is dropped.
    lakes = getattr(clear, "lakes", Polygon())
    keep = [b for b in view["blocks"] if rect(b["x"], b["z"], b["w"], b["d"], b["rot"]).intersection(lakes).area <= 0.5]
    made["dropped_in_lake"] = len(view["blocks"]) - len(keep)
    view["blocks"] = keep
    # Overlaps of the massing against walls, halls and the gardens' water, measured on what is written.
    def poly_of(b):
        return rect(b["x"], b["z"], b["w"], b["d"], b["rot"])
    over = Counter()
    worst = {}
    inside_walls = unary_union([clear.garden.buffer(-1.0)])
    for b in view["blocks"] + view["halls"]:
        p = poly_of(b)
        for what, geom in (("wall", clear.walls), ("hall", clear.halls), ("water", clear.water), ("inside", inside_walls)):
            a = p.intersection(geom).area if what != "wall" else (p.length and p.intersection(geom).length)
            if a > SITE_EPS:
                over[what] += 1
                worst[what] = max(worst.get(what, 0), round(float(a), 2))

    for f in feats:
        f["geometry"]["coordinates"] = rounded(f["geometry"]["coordinates"])
    fc = {"type": "FeatureCollection", "name": "surroundings_1860", "credit": "Round 20, research/surroundings/README.md; outlines from S01 (Princeton University Art Museum), OpenStreetMap (© OpenStreetMap contributors, ODbL) and the sources named per feature", "features": feats}
    text = json.dumps(fc, ensure_ascii=False) + "\n"
    if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
        OUT.write_text(text, encoding="utf-8")
    view["meta"] = {"frame": "x east, z south, metres, scene1860 (UTM 50N minus origin)", "domain": [x0, z0, x1, z1], "note": "generated by scripts/surroundings1860.py; heights from the ground (around3d.js heightAt)", "counts": dict(sorted(made.items()))}
    vtext = json.dumps(view, ensure_ascii=False, separators=(",", ":")) + "\n"
    if not VIEW.exists() or VIEW.read_text(encoding="utf-8") != vtext:
        VIEW.write_text(vtext, encoding="utf-8")
    report = {"features": len(feats), "by_kind": dict(sorted(Counter(f["properties"]["kind"] for f in feats).items())), "by_confidence": dict(sorted(Counter(f["properties"]["confidence"] for f in feats).items())),
              "assumed": sum(1 for f in feats if f["properties"]["assumed"]), "made": dict(sorted(made.items())), "joins": joins, "overlaps": dict(over), "overlap_worst": worst,
              "blocks": len(view["blocks"]), "halls": len(view["halls"]), "patches": len(view["patches"]), "strips": len(view["strips"]), "view_bytes": len(vtext.encode())}
    rtext = json.dumps(report, ensure_ascii=False, indent=1) + "\n"
    if not REPORT.exists() or REPORT.read_text(encoding="utf-8") != rtext:
        REPORT.write_text(rtext, encoding="utf-8")
    print(f"{len(feats)} features {report['by_kind']}; confidence {report['by_confidence']}; made {report['made']}; overlaps {dict(over)}; view {len(vtext) / 1e3:.0f} kB")


if __name__ == "__main__":
    main()
