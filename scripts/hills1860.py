"""Hill heights, and the hills the plan does not draw: research/layers/hills_1860.geojson (the fields) and research/terrain/hills_heights.csv. Round 10.

  uv run python scripts/hills1860.py        (after build_r1.py and apply_facts.py; reads the box and way positions of the last boxes1860.py and paths1860.py run)

S01 draws halls, shores and rockeries 假山 (black hatched clumps), but no earth hills 土山: its 54 hill outlines are closed lobed shapes,
about 5 ha in all (Q29). The album of 1744 (S08) rings nearly every scene with earth hills on its west, north and east (research/terrain/readings.csv,
the two album readers), and the texts put hills behind halls in most scenes. So:
  plan       the 54 outlines of S01 (ids H0001..), kept as build_r1.py writes them
  free_land  land inside the walls that no hall, way, bridge, landing, wall, field, court or shore needs, opened to at least 5 m wide and 200 m2,
             cut by the scene polygons: one feature per piece (H2001..), `group` the piece of land it belongs to. Its outline is generated: assumed, C.
Height of every hill, the first method that gives one (research/terrain/README.md):
  surveyed   a published figure for that hill (the park's page for 线法山, S1000)
  dem        today's GLO-30 rise inside the outline (research/terrain/glo30_rise.npz): at least DEM_MIN_M over two cells; minus CANOPY_M for trees
  painting   an album reading for that scene on that side, scaled so the album's median falls on the middle of Attiret's range (S911); C
  text       a figure in a text for that hill
  typology   by area: a knoll, a courtyard hill 2-4 m, a major hill 6-12 m (the brief's classes); C
Writes research/terrain/rockeries.csv: the rockeries the texts and leaves describe, scene by scene, for the vegetation round (not drawn here).
Positions never depend on the ground, so reading the last run's boxes and ways is a fixed point: a second run changes nothing.
"""

import csv
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import shapely
from scipy import ndimage
from shapely.geometry import Point, Polygon, box, shape
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scene1860 import GROUND_STEP_M, LAYERS, ROOT, SITE_DATA, ground_frame, layer, raster_mask, to_lonlat, to_xz  # noqa: E402

TERRAIN = ROOT / "research/terrain"
STEP = GROUND_STEP_M
CLEAR = {  # metres kept free of hills round what stands or is walked: guesses, C, chosen so a court and its walk stay level
    "box": 6.0, "path": 2.0, "bridge": 4.0, "wall": 2.5, "water": 3.0, "field": 3.0, "landing": 6.0, "court": 5.0, "plan_hill": 1.0,
}
OPEN_M = 2.5  # opening radius: free land narrower than about 5 m is no hill
MIN_AREA_M2 = 200
PART_MIN_M2 = 100
OPEN_GROUND = {"YM15": "山高水长: the open ground for archery, wrestling and fireworks west of the hall (S05 j81; S06); its hills stand on the east (readings R10 hills_texts)"}
DEM_MIN_M, DEM_CELLS, CANOPY_M = 4.0, 2, 2.0  # research/terrain/README.md: under 3 m is noise, trees on flat ground 1.2-3.1 m
DEM_CLIP = (2.0, 12.0)
ATTIRET = (6.5, 19.5)  # 20-60 pieds, French feet 0.3248 m (S911 p.8; readings R10-005, R10-098)
TYPOLOGY = [(400, 2.5, 1.0, "knoll"), (3000, 3.5, 1.5, "courtyard hill, 2-4 m"), (1e12, 8.0, 3.0, "major hill, 6-12 m")]
COMPASS = {"north-east": 45, "north-west": 315, "south-east": 135, "south-west": 225, "north": 0, "east": 90, "south": 180, "west": 270, "ne": 45, "nw": 315, "se": 135, "sw": 225}


def xz(geom):
    return shapely.transform(geom, lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1])))


def model_courts():
    """Round 19: the courts, yards and terraces a detailed model paves (models/*/joints.json `clear` and `decks`, scene x z, from the model's last run) are not free land.
    A generated hill stood 7 m high in the paved court before 正大光明殿 (YM01). Positions never depend on the ground, so this is a fixed point too.
    Round 27: `level` too, the courts a model leaves earth for their trees (the planting may stand there) but no generated hill may (鸿慈永祜 YM17)."""
    out = []
    for jp in sorted((ROOT / "models").glob("*/joints.json")):
        j = json.load(open(jp, encoding="utf-8"))
        polys = list(j.get("clear", [])) + [d["poly"] for d in j.get("decks", [])] + list(j.get("level", []))
        out += [Polygon(p).buffer(0).buffer(CLEAR["court"]) for p in polys if len(p) >= 3]
    return out


def ll(geom):
    return shapely.transform(geom, lambda c: np.column_stack(to_lonlat(c[:, 0], c[:, 1])))


def polys(g):
    if g.is_empty:
        return []
    return [g] if isinstance(g, Polygon) else [p for p in getattr(g, "geoms", []) if isinstance(p, Polygon)]


def num(s):
    m = re.findall(r"\d+(?:\.\d+)?", s or "")
    if not m:
        return None
    v = [float(x) for x in m[:2]]
    return sum(v) / len(v) if re.search(r"\d\s*[-–]\s*\d", s) else v[0]


def bearing_word(text):
    t = (text or "").lower()
    for w, deg in COMPASS.items():
        if re.search(rf"\b{w}\b", t):
            return deg
    if "behind" in t or "back" in t:
        return 0
    if "front" in t or "foreground" in t:
        return 180
    return None


def ang(a, b):
    return abs((a - b + 180) % 360 - 180)


def cells_to_poly(mask, xs, zs):
    """A raster mask (cell centres at xs, zs) as a polygon: rows merged into runs, then unioned."""
    rects = []
    for j in np.flatnonzero(mask.any(axis=1)):
        row = mask[j]
        d = np.diff(np.r_[0, row.astype(np.int8), 0])
        for a, b in zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1)):
            rects.append(box(xs[a] - STEP / 2, zs[j] - STEP / 2, xs[b - 1] + STEP / 2, zs[j] + STEP / 2))
    return shapely.union_all(rects).simplify(1.0).buffer(0)


class DEM:
    def __init__(self):
        z = np.load(TERRAIN / "glo30_rise.npz")
        self.rise = z["rise_dm"].astype(float) / 10
        self.rise[z["rise_dm"] == -32768] = np.nan
        north, west, step = float(z["north"]), float(z["west"]), float(z["step"])
        lat = north - np.arange(self.rise.shape[0]) * step
        lon = west + np.arange(self.rise.shape[1]) * step
        LON, LAT = np.meshgrid(lon, lat)
        X, Z = to_xz(LON.ravel(), LAT.ravel())
        self.X, self.Z = X.reshape(self.rise.shape), Z.reshape(self.rise.shape)

    def read(self, g):
        m = shapely.contains_xy(g.buffer(15), self.X, self.Z) & np.isfinite(self.rise)
        if not m.any():
            return None
        v = self.rise[m]
        return float(v.max()), int((v >= 3.0).sum()), int(m.sum())


def main():
    readings = list(csv.DictReader(open(TERRAIN / "readings.csv", encoding="utf-8", newline="")))
    hill_rows = [r for r in readings if r["kind"] == "hill_height"]
    album = [r for r in hill_rows if r["method"] == "painting" and num(r["value_m"]) is not None]
    k_album = (sum(ATTIRET) / 2) / float(np.median([num(r["value_m"]) for r in album]))
    scenes = {f["properties"]["id"]: (xz(shape(f["geometry"])).buffer(0), f["properties"]) for f in layer("scenes_1860")}
    halls = json.load(open(SITE_DATA / "halls_1860.geojson", encoding="utf-8"))["features"]
    main_hall = {}
    for f in halls:
        p = f["properties"]
        s = p["parent_id"] or p["building_id"].split("-")[0]
        a = p["frontage_m"] * p["depth_m"]
        if s not in main_hall or a > main_hall[s][0]:
            main_hall[s] = (a, xz(shape(f["geometry"])).centroid)

    # Free land.
    x0, z0, x1, z1 = ground_frame()
    xs, zs = np.arange(x0, x1 + STEP / 2, STEP), np.arange(z0, z1 + STEP / 2, STEP)
    garden = unary_union([Polygon(xz(shape(f["geometry"])).coords).buffer(0) for f in layer("walls_1860") if f["properties"]["kind"] == "outer_wall"])
    water = unary_union([xz(shape(f["geometry"])).buffer(0) for f in layer("water_1860")])
    plan_hills = [f for f in layer("hills_1860") if not f["properties"]["id"].startswith("H2")]
    excl = [water.buffer(CLEAR["water"])]
    excl += [xz(shape(f["geometry"])).buffer(CLEAR["box"]) for f in halls]
    excl += [xz(shape(f["geometry"])).buffer(max(f["properties"].get("width_m") or 2, 1) / 2 + CLEAR["path"]) for f in layer("paths_1860") if f["properties"]["kind"] != "boat_route"]
    excl += [xz(shape(f["geometry"])).buffer(CLEAR["bridge"]) for f in layer("bridges_1860")]
    excl += [xz(shape(f["geometry"])).buffer(CLEAR["wall"]) for f in layer("walls_1860") if f["geometry"]["type"] == "LineString"]
    excl += [xz(shape(f["geometry"])).buffer(CLEAR["field"]) for f in layer("fields_1860")]
    excl += [xz(shape(f["geometry"])).buffer(CLEAR["landing"]) for f in layer("landings_1860")]
    excl += [xz(shape(f["geometry"])).buffer(CLEAR["plan_hill"]) for f in plan_hills]
    excl += [g for sid, (g, p) in scenes.items() if p.get("garden") == "Xiyang Lou" or sid.startswith("XY") or sid in OPEN_GROUND]
    excl += [xz(shape(f["geometry"])).buffer(CLEAR["court"]) for f in halls if f["properties"].get("shape") == "court"]
    excl += model_courts()
    free = raster_mask(garden, xs, zs) & ~raster_mask(unary_union(excl), xs, zs)
    disk = np.hypot(*np.mgrid[-2:3, -2:3]) * STEP <= OPEN_M + 0.01
    free = ndimage.binary_opening(free, structure=disk)
    lab, n = ndimage.label(free)
    sizes = ndimage.sum(free, lab, index=np.arange(1, n + 1)) * STEP * STEP
    keep = np.flatnonzero(sizes >= MIN_AREA_M2) + 1

    gen = []
    scene_tree = list(scenes.items())
    slices = ndimage.find_objects(lab)
    for gi, k in enumerate(keep, 1):
        sl = slices[k - 1]
        sub = lab[sl] == k
        comp = cells_to_poly(sub, xs[sl[1]], zs[sl[0]])
        rest = comp
        pieces = []
        for sid, (sg, sp) in scene_tree:
            if not sg.intersects(comp):
                continue
            part = comp.intersection(sg)
            rest = rest.difference(sg)
            for q in polys(part):
                pieces.append((sid, q))
        for q in polys(rest):
            pieces.append(("", q))
        for sid, q in pieces:
            if q.area >= PART_MIN_M2:
                gen.append({"group": f"G{gi:03d}", "scene": sid, "poly": q})
    gen.sort(key=lambda h: (h["group"], -h["poly"].area))

    dem = DEM()
    out_feats, table = [], []

    def height(hid, g, scene, refs):
        """The first method of the ladder that gives a figure: (height, method, error, sources, confidence, readings, note)."""
        own = [r for r in hill_rows if hid in r["ref"].split(";") and r["method"] in ("text",) and num(r["value_m"]) is not None]
        pub = [r for r in own if r["sources"] == "S1000"]
        if pub:
            r = pub[0]
            return num(r["value_m"]), "surveyed: published by the park (method not stated); today's hill", float(r["error_m"] or 2), "S1000", "B", r["id"], r["value_text"][:60]
        d = dem.read(g)
        note = ""
        if d:
            peak, hi, cells = d
            if peak >= DEM_MIN_M and hi >= DEM_CELLS:
                h = float(np.clip(peak - CANOPY_M, *DEM_CLIP))
                return round(h, 1), f"dem: GLO-30 peak {peak:.1f} m above the local low ground over {cells} cells, {hi} of them 3 m or more, minus {CANOPY_M} m for trees", 3.0, "S04;S159", "C", "", ""
            note = f"GLO-30 shows {peak:.1f} m at most here: flat today (hills cut 1967-73, S145) or below the noise"
        c = g.centroid
        mh = main_hall.get(scene)
        side = None
        if mh is not None and mh[1].distance(c) > 5:
            side = math.degrees(math.atan2(c.x - mh[1].x, -(c.y - mh[1].y))) % 360
        rows = [r for r in album if hid in r["ref"].split(";")]
        how = "this outline"
        if not rows and scene:
            cand = [r for r in album if scene in r["scene_id"].split(";")]
            if side is not None:
                rows = [r for r in cand if bearing_word(r["where"]) is not None and ang(bearing_word(r["where"]), side) <= 45]
                how = "this side of the scene"
            if not rows and cand:
                rows, how = cand, "the scene's hills, no reading on this side"
        if rows:
            v = float(np.median([num(r["value_m"]) for r in rows])) * k_album
            h = float(np.clip(v, *ATTIRET))
            err = max(3.0, 0.5 * h) + (2.0 if how.startswith("the scene") else 0)
            return round(h, 1), f"painting: album reading ({how}), median {v / k_album:.0f} m as painted x {k_album:.2f} so the album's median falls on the middle of Attiret's 6.5-19.5 m, clipped to it", round(err, 1), "S08;S911", "C", ";".join(r["id"] for r in rows[:6]), note
        txt = [r for r in hill_rows if hid in r["ref"].split(";") and r["method"] == "text" and num(r["value_m"]) is not None]
        if txt:
            r = txt[0]
            return num(r["value_m"]), "text: " + r["value_text"][:60], float(r["error_m"] or 3), r["sources"], "C", r["id"], note
        for lim, h, e, what in TYPOLOGY:
            if g.area < lim:
                return h, f"typology: {what} (area {g.area:.0f} m2)", e, "S157", "C", "", note

    for f in plan_hills:
        p = dict(f["properties"])
        g = xz(shape(f["geometry"])).buffer(0)
        sc = [sid for sid, (sg, _) in scenes.items() if sg.contains(g.representative_point())]
        h, method, err, src, conf, rids, note = height(p["id"], g, sc[0] if sc else "", None)
        p.update(height_est_m=h, height_method=method, error_m=err, sources="S01;" + src, confidence=conf, assumed=False, basis="plan", group=p["id"], scene_id=sc[0] if sc else "", readings=rids)
        if note:
            p["dem_note"] = note
        out_feats.append({"type": "Feature", "geometry": f["geometry"], "properties": p})
    for n, hl in enumerate(gen, 1):
        hid = f"H{2000 + n}"
        g = hl["poly"]
        h, method, err, src, conf, rids, note = height(hid, g, hl["scene"], None)
        p = {"id": hid, "kind": "hill", "name_zh": "", "name_pinyin": "", "area_m2": round(g.area), "sources": "S08;S01;" + src, "confidence": "C",
             "note": "generated: free land inside the walls (no hall, way, bridge, landing, wall, field, court or shore within reach), where the album of 1744 rings the scenes with earth hills; outline assumed",
             "height_est_m": h, "height_method": method, "error_m": err, "assumed": True, "basis": "free_land", "group": hl["group"], "scene_id": hl["scene"], "readings": rids}
        if note:
            p["dem_note"] = note
        gl = ll(g)
        gl = shapely.set_precision(gl, 1e-7)
        out_feats.append({"type": "Feature", "geometry": json.loads(shapely.to_geojson(gl)), "properties": p})

    fc = json.load(open(LAYERS / "hills_1860.geojson", encoding="utf-8"))
    fc["features"] = out_feats
    fc["note_r10"] = "Round 10: heights by scripts/hills1860.py (research/terrain/hills_heights.csv); H2001.. generated on free land, assumed"
    (LAYERS / "hills_1860.geojson").write_text(json.dumps(fc, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

    cols = ["id", "basis", "group", "scene_id", "area_m2", "height_est_m", "error_m", "method", "height_method", "sources", "confidence", "assumed", "readings", "dem_note"]
    with open(TERRAIN / "hills_heights.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for f in out_feats:
            p = f["properties"]
            w.writerow([p["id"], p["basis"], p["group"], p["scene_id"], p["area_m2"], p["height_est_m"], p["error_m"], p["height_method"].split(":")[0], p["height_method"], p["sources"], p["confidence"], "yes" if p["assumed"] else "no", p["readings"], p.get("dem_note", "")])

    rock = [r for r in readings if r["kind"] == "rockery"]
    with open(TERRAIN / "rockeries.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["reading", "scene_id", "where", "what", "sources", "grade", "state_date"])
        for r in rock:
            w.writerow([r["id"], r["scene_id"], r["where"], r["value_text"], r["sources"], r["grade"], r["state_date"]])

    from collections import Counter
    by = Counter((f["properties"]["basis"], f["properties"]["height_method"].split(":")[0]) for f in out_feats)
    area = Counter()
    for f in out_feats:
        area[f["properties"]["basis"]] += f["properties"]["area_m2"]
    print(f"album scale k = {k_album:.3f} (median of {len(album)} album readings -> {sum(ATTIRET) / 2} m)")
    print(f"{len(out_feats)} hills: {dict(sorted(by.items()))}; area plan {area['plan'] / 1e4:.1f} ha, free land {area['free_land'] / 1e4:.1f} ha in {len(keep)} pieces of land")
    print(f"rockeries described: {len(rock)} rows in {len({s for r in rock for s in r['scene_id'].split(';') if s})} scenes")


if __name__ == "__main__":
    main()
