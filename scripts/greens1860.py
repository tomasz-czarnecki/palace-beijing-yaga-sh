"""Round 12: the planting of 1860, trees, bamboo, lotus, reeds, flower beds, and the rockeries. Writes research/layers/greens_1860.geojson (the areas and rockeries),
its public copy site/reconstruction/data/greens_1860.geojson, site/reconstruction/data/greens_1860.json (species, areas, rockeries for the view) and
site/reconstruction/generated/greens_1860.bin (one record per plant), and research/greens/greens_report.json.

  uv run python scripts/greens1860.py        (after kit1860.py; rerun after any change to the halls, ways, walls, the ground or research/greens/species.csv)

Input, hand-edited: research/greens/species.csv, one row per (scene, plant, place) a source supports (research/greens/README.md). The plan S01 draws no
plant, so no tree has a surveyed place: the places are generated here, seeded, inside an area anchored to the scene's own geometry (its outline on S01,
its water, islands, hills, halls, courts and ways):
  place     the zone: north, south, east, west of the scene's centre; shore (1-5 m from the water); island; hill; hill_foot; court, front_court,
            rear_court (the paved courts of scripts/kit1860.py, in front of or behind the main hall); around_hall (2.5-14 m round the hall named);
            dike, along_way (rows along the ways); bridge; rockery (round its rocks); pond, lake_edge (on the water); scene (the scene's free land).
  pattern   by role: avenue (a row each side of the way, or along the shore), specimen (a pair either side of the hall's front, else darts), grove,
            bamboo, flower_bed (darts in the zone), lotus and reed (clumps on the water, gaps by seeded noise), topiary (a grid set square to the hall).
  count     "about N" in the row's note (the painter's or the text's count), else the zone's area at the kind's spacing and the note's density.
Grades: trees_confidence is the row's (what grows there). extent_confidence is B where a leaf (or a survivor) shows the plant at that side of the scene,
C where only a text names it, or the place is `scene`, or the zone was empty and the area fell back to the scene. Every place is generated (`generated`).
The fill: free land with no sourced area gets the typical planting (willows at the shores, mixed groves on the hills, sparse clumps elsewhere with
open lawn between): `assumed: true`, C, its basis stated; the view hides it with assumed=0.
Clearances, in metres, kept by every plant: the boxes by its crown's radius + BOX_CLEAR_M (at least BOX_MIN_M, which covers the kit's steps); the ways by
half their width + WAY_CLEAR_M (galleries + the crown's radius); the walls, the bridges, the landings, the rockeries; water by WATER_CLEAR_M (willows
WILLOW_CLEAR_M); paddy fields; courts except a court's own specimens. Lotus, floating leaves and reeds stand only on water. Each plant's base is the walk
surface (ground1860.py's lattice, as ground3d.js groundAt), and `lift` is what the generated hills add there (the view lowers the plant by it with assumed=0).
Rockeries: rows whose plant is a rock (石, 假山) and research/terrain/rockeries.csv: a standing stone in a court, a rock screen behind a hall, rockwork on
the shore that runs down into the water, a rock hill on the scene's highest hill. Their base is the lowest ground or bed under them, less ROCK_SINK_M.
"""

import csv
import hashlib
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box as sbox, shape
from shapely.ops import unary_union
from shapely.strtree import STRtree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scene1860 import DATUM_M, GENERATED, LAYERS, ROOT, SITE_DATA, Grid, layer, to_lonlat, to_xz  # noqa: E402

SPECIES = ROOT / "research/greens/species.csv"
ROCK_READINGS = ROOT / "research/terrain/rockeries.csv"
BUILDINGS = ROOT / "research/buildings.csv"
OUT_LAYER = LAYERS / "greens_1860.geojson"
PUB_LAYER = SITE_DATA / "greens_1860.geojson"
OUT_JSON = SITE_DATA / "greens_1860.json"
OUT_BIN = GENERATED / "greens_1860.bin"
REPORT = ROOT / "research/greens/greens_report.json"
CREDIT = ("Planting from the sources in research/greens/species.csv (the 1744 poems, prefaces and album, 日下旧闻考, the imperial poems, eyewitness accounts, today's old trees); "
          "areas anchored to the geometry traced from S01, image courtesy of the Princeton University Art Museum. No plan draws a plant: every tree's place is generated.")

BOX_CLEAR_M, BOX_MIN_M = 0.8, 2.6
WAY_CLEAR_M, GALLERY_CLEAR_M = 0.6, 0.8
WALL_CLEAR_M, BRIDGE_CLEAR_M, LANDING_CLEAR_M = 1.2, 1.5, 3.0
WATER_CLEAR_M, WILLOW_CLEAR_M = 1.2, 0.6
ROCK_CLEAR_M = 0.6
SHORE_BAND_M = (1.0, 5.0)
SHORE_WILLOW_M = 11.0  # the fill's willows along a shore, one in about this many metres before the gaps: the leaves paint 10-30 a leaf (research/greens/README.md). C
HALL_BAND_M = (2.5, 14.0)
LOTUS_EDGE_M, LOTUS_BRIDGE_M, LOTUS_ROUTE_M = 0.8, 5.0, 3.0
REED_BAND_M = 4.0
ROCK_SINK_M = 0.3
TRUNK_SINK_M = 0.5  # greens3d.js sinks every trunk this far, so a slope under it never shows a gap
CROWN_FIT = 0.6  # beside a hall a tree's crown may be this share of its kind's, so it never reaches over the roof. C
VARY = 0.12  # each plant's height and crown, +- this share
SCENE_WITHOUT_OUTLINE_R = 30.0  # a scene with no outline on S01 (福海 YM54): its water body's shore, this far out
FILL_GAP_M = 5.0  # the fill keeps this far beyond a sourced plant's crown, so a sourced group stays legible
FLOWER_BED_MAX = 160  # at most this many plants in a flower bed. C
FLOWER_BED_N = 36  # plants of a flower bed no count is given for: a few beds round the steps, not a field of them. C
SPECIMEN_N = 3  # trees of a specimen row no count is given for. C
DENSITY = {"dense": 1.0, "medium": 0.6, "sparse": 0.32}
FILL_SHARE = {"hill": 0.75, "land": 0.42, "shore": 0.55}  # share of the fill zones that is planted, the rest open lawn (seeded noise). C

# Form defaults: (height, crown diameter, spacing as a share of the crown in a dense grove). Species defaults, C: mature garden trees of the kind in north China.
FORM = {
    "pine": (12.0, 8.0, 1.05), "cypress": (11.0, 4.0, 1.1), "willow": (11.0, 9.0, 1.1), "broad": (13.0, 9.5, 1.0), "blossom": (5.0, 4.5, 1.05),
    "bamboo": (5.0, 2.6, 0.95), "shrub": (1.1, 1.5, 1.05), "topiary": (3.2, 1.8, 2.2), "hedge": (1.6, 1.3, 0.9),
    "lotus": (0.0, 2.6, 0.95), "floating": (0.0, 1.8, 1.2), "reed": (1.9, 1.4, 1.0),
}
# Named plants with their own size and colour: (height, crown, bloom colour or None, autumn colour). Species defaults, C.
PLANT = {
    "白皮松": ("pine", 12.0, 7.0, None, None), "松": ("pine", 12.0, 8.0, None, None),
    "柏": ("cypress", 11.0, 4.2, None, None), "桧": ("cypress", 10.0, 3.8, None, None),
    "柳": ("willow", 11.0, 9.0, None, "yellow"),
    "梧桐": ("broad", 10.0, 7.0, None, "yellow"), "槐": ("broad", 14.0, 10.0, None, "yellow"), "龙爪槐": ("broad", 4.0, 4.5, None, "yellow"),
    "枫": ("broad", 10.0, 7.0, None, "red"), "楓": ("broad", 10.0, 7.0, None, "red"), "红叶树": ("broad", 9.0, 7.0, None, "red"), "黑枣": ("broad", 10.0, 7.0, None, "yellow"),
    "桃": ("blossom", 4.5, 4.2, "pink", "yellow"), "山桃": ("blossom", 5.0, 4.5, "pale", "yellow"), "杏": ("blossom", 6.0, 5.0, "pale", "yellow"),
    "梅": ("blossom", 4.0, 3.5, "pink", "yellow"), "海棠": ("blossom", 6.0, 4.0, "pink", "yellow"), "玉兰": ("blossom", 8.0, 5.0, "white", "brown"),
    "玉蘭": ("blossom", 8.0, 5.0, "white", "brown"), "花树": ("blossom", 5.0, 4.5, "pink", "yellow"), "李": ("blossom", 5.0, 4.0, "white", "yellow"),
    "竹": ("bamboo", 5.0, 2.6, None, None), "牡丹": ("shrub", 1.2, 1.4, "red", "brown"), "芍药": ("shrub", 0.8, 1.0, "pink", "brown"),
    "菊": ("shrub", 0.8, 1.0, None, "gold"), "荷": ("lotus", 0.0, 2.6, "pink", "brown"), "芦苇": ("reed", 2.2, 1.4, None, "straw"), "蒲": ("reed", 1.6, 1.2, None, "straw"),
}
FORM_COLOURS = {"pine": (None, None), "cypress": (None, None), "willow": (None, "yellow"), "broad": (None, "yellow"), "blossom": ("pink", "yellow"), "bamboo": (None, None),
                "shrub": ("pink", "brown"), "topiary": (None, None), "hedge": (None, None), "lotus": ("pink", "brown"), "floating": (None, "brown"), "reed": (None, "straw")}
KIND = {"lotus": "lotus_pond", "floating": "lotus_pond", "reed": "reed_bed", "bamboo": "bamboo_grove", "shrub": "flower_bed", "hedge": "hedge", "topiary": "specimen_tree"}
WATER_FORMS = {"lotus", "floating", "reed"}
GRADE = {"A": 0, "B": 1, "C": 2}
PLACES = {"scene", "north", "south", "east", "west", "front_court", "rear_court", "court", "around_hall", "shore", "island", "hill", "hill_foot", "dike", "along_way",
          "pond", "lake_edge", "bridge", "rockery", "field", "outside_wall"}

# The typical planting of the fill: (species key, share). C; the basis is said in the area's note.
FILL_MIX = {
    "hill": [("松", 0.35), ("落叶乔木", 0.4), ("花树", 0.25)],
    "land": [("落叶乔木", 0.55), ("松", 0.25), ("花树", 0.2)],
    "shore": [("柳", 1.0)],
}
FILL_BASIS = {
    "hill": "typical: the 1744 leaves ring the scenes with hills under pines, broadleaf trees and blossom (S08; research/greens/README.md); Attiret's hills 'sprinkled with flowering trees' (S157); Wolseley's mounds 'topped with trees of every kind' (S240). Not a reading of this hill",
    "land": "typical: clumps of broadleaf trees and pines with open grass between, as the leaves paint the free land (S08) and Barrow's 'wood and lawn' (S1160). Not a reading of this place",
    "shore": "typical: the 1744 leaves paint willows along most shores, 10-30 a leaf (S08, research/greens/README.md). Not a reading of this shore",
}


def seed_of(*parts):
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def xz_geom(g):
    return shapely.transform(g, lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1])))


def polys(g):
    if g is None or g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    return [p for p in getattr(g, "geoms", []) if isinstance(p, Polygon)] + [q for p in getattr(g, "geoms", []) if isinstance(p, MultiPolygon) for q in p.geoms]


def species_key(name, form=None):
    """The plant's key: the longest known name in it whose form is the row's (so 松;菊 drawn as a pine is 松), else its first name; a clipped plant keeps its own key."""
    keys = sorted(PLANT, key=len, reverse=True)
    if form in ("topiary", "hedge"):
        return (re.split(r"[;/ (（]", name.strip())[0] if name else "树") + ("·修剪" if form == "topiary" else "·篱")
    for k in keys:
        if k in (name or "") and (form is None or PLANT[k][0] == form):
            return k
    first = re.split(r"[;/ (（]", name.strip())[0] if name else ""
    for k in keys:
        if k in first:
            return k
    return first or "树"


def count_from(row):
    """The count a row states: 'about 12', '10-12', '20+', or a Chinese count of trees (二株, 两株, 十余本)."""
    text = " ".join([row.get("note", ""), row.get("place_text", "")])
    m = re.search(r"about (\d+)\s*(?:[-–]|to)?\s*(\d+)?", text)
    if m:
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        return (a + b) / 2
    m = re.search(r"(\d+)\s*[-–]\s*(\d+)\s+(?:pines|trees|willows|peach|apricot|blossom|broadleaf|bamboo|magnolia|stones|cypress|clumps|beds)", text)
    if m:
        return (int(m.group(1)) + int(m.group(2))) / 2
    m = re.search(r"\b(a pair of|a|one|two|three|four|five|six|eight|ten)\b(?:\s+[\w-]+){0,3}?\s+(trees?|pines?|willows?|arbours?|magnolias?|peach(?:es)?|apricots?|cypress(?:es)?|stones?|clumps?|tree-arbours)\b", text.lower())
    if m and row.get("role") == "specimen":  # "a large weeping tree", "four tree-arbours": a count only where the row is a specimen
        return {"a pair of": 2, "a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "eight": 8, "ten": 10}[m.group(1)]
    zh = row.get("quote", "") + row.get("place_text", "")
    m = re.search(r"([一二兩两三四五六七八九十]+)(?:餘|余)?(?:株|本|樹|树|棵)", zh)
    if m:
        d = {"一": 1, "二": 2, "兩": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
        s = m.group(1)
        if s.startswith("十"):
            return 10 + (d.get(s[1:], 0) if len(s) > 1 else 0) + (2 if "餘" in zh or "余" in zh else 0)
        if "十" in s:
            return d.get(s[0], 1) * 10 + d.get(s[-1], 0) if s[-1] != "十" else d.get(s[0], 1) * 10
        return d.get(s, 0) or None
    return None


def density_of(row):
    t = (row.get("note", "") + " " + row.get("place_text", "")).lower()
    for k in ("dense", "thick", "solid", "密"):
        if k in t:
            return "dense"
    for k in ("sparse", "a few", "scattered", "single", "few "):
        if k in t:
            return "sparse"
    return "medium"


class Site:
    """Everything a plant must keep clear of, in scene metres, and the zones it is placed in."""

    def __init__(self):
        self.G = Grid()
        print("reading the layers ...")
        self.gardens = {}
        for f in layer("walls_1860"):
            p = f["properties"]
            if p["kind"] == "outer_wall":
                self.gardens[{"Yuanming Yuan": "YM", "Changchun Yuan": "CC", "Qichun Yuan": "QC"}[p["garden"]]] = Polygon(xz_geom(shape(f["geometry"])).coords)
        self.outer_walls = {g: LineString(p.exterior.coords) for g, p in self.gardens.items()}
        self.inside = unary_union(list(self.gardens.values()))
        self.scenes = {}
        for f in layer("scenes_1860"):
            self.scenes[f["properties"]["id"]] = (xz_geom(shape(f["geometry"])).buffer(0), f["properties"])
        self.water_feats = [(f["properties"], xz_geom(shape(f["geometry"])).buffer(0)) for f in layer("water_1860")]
        self.water = unary_union([g for _, g in self.water_feats]).buffer(0)
        self.islands = unary_union([xz_geom(shape(f["geometry"])).buffer(0) for f in layer("islands_1860")])
        self.hill_feats = [(f["properties"], xz_geom(shape(f["geometry"])).buffer(0)) for f in layer("hills_1860")]
        self.hills = unary_union([g for p, g in self.hill_feats if (p.get("height_est_m") or 0) >= 1.0]).buffer(0)
        self.fields = unary_union([xz_geom(shape(f["geometry"])).buffer(0) for f in layer("fields_1860")])
        halls = json.load(open(SITE_DATA / "halls_1860.geojson", encoding="utf-8"))["features"]
        self.boxes = []
        for f in halls:
            p = f["properties"]
            self.boxes.append((p, xz_geom(shape(f["geometry"]))))
        self.box_polys = [g for _, g in self.boxes]
        # Round 13: a detailed model's own footprints (models/<ID>-<slug>/joints.json: its stairs, terrace, colonnades, pools) are kept clear as boxes are
        for jp in sorted((ROOT / "models").glob("*/joints.json")):
            self.box_polys += [Polygon(fp).buffer(0) for fp in json.load(open(jp, encoding="utf-8")).get("footprints", [])]
        self.box_tree = STRtree(self.box_polys)
        self.box_union = unary_union(self.box_polys)
        paths = json.load(open(SITE_DATA / "paths_1860.geojson", encoding="utf-8"))["features"]
        self.paths = []
        for f in paths:
            p = f["properties"]
            line = xz_geom(shape(f["geometry"]))
            self.paths.append((p, line))
        ways = [(p, l) for p, l in self.paths if p["kind"] != "boat_route"]
        self.way_strips = unary_union([l.buffer((p.get("width_m") or 2) / 2, cap_style="flat") for p, l in ways])
        self.way_clear = unary_union([l.buffer((p.get("width_m") or 2) / 2 + (GALLERY_CLEAR_M if "gallery" in p["kind"] else WAY_CLEAR_M)) for p, l in ways])
        self.galleries = unary_union([l.buffer((p.get("width_m") or 2.4) / 2) for p, l in ways if "gallery" in p["kind"]])
        self.boat = unary_union([l for p, l in self.paths if p["kind"] == "boat_route"])
        st = json.load(open(GENERATED / "structures.json", encoding="utf-8"))
        self.wall_lines = unary_union([LineString([(s[0], s[1]), (s[2], s[3])]) for s in st["wall"]["segments"]])
        self.wall_clear = self.wall_lines.buffer(st["wall"]["thickness_m"] / 2 + WALL_CLEAR_M)
        self.bridges = [(b, LineString([(q[0], q[2]) for q in b["pts"]])) for b in st["bridges"]]
        self.bridge_clear = unary_union([l.buffer(b["width_m"] / 2 + BRIDGE_CLEAR_M) for b, l in self.bridges])
        lands = json.load(open(SITE_DATA / "landings_1860.geojson", encoding="utf-8"))["features"]
        self.landings = unary_union([Point(*to_xz(*f["geometry"]["coordinates"])).buffer(LANDING_CLEAR_M) for f in lands])
        import kit1860

        self.courts = kit1860.court_area(halls).buffer(0)
        print("free land ...")
        self.not_dry = unary_union([self.box_union.buffer(BOX_MIN_M), self.way_clear, self.wall_clear, self.bridge_clear, self.landings, self.fields])
        self.water_clear = self.water.buffer(WATER_CLEAR_M)
        self.willow_clear = self.water.buffer(WILLOW_CLEAR_M)
        self.not_free = unary_union([self.water_clear, self.not_dry])
        self.free = self.inside.difference(self.not_free).difference(self.courts).buffer(0)
        self.court_free = self.courts.difference(self.not_free).buffer(0)
        self.shore_land = self.inside.intersection(self.water.buffer(SHORE_BAND_M[1])).difference(self.willow_clear).difference(self.not_dry).difference(self.courts).buffer(0)
        self.gallery_clear = self.galleries.buffer(GALLERY_CLEAR_M + 3.0)
        for g in (self.way_clear, self.wall_clear, self.bridge_clear, self.landings, self.fields, self.courts, self.water_clear, self.willow_clear, self.gallery_clear):
            shapely.prepare(g)
        self.rocks = []  # footprints, added as the rockeries are placed
        self.rock_union = Polygon()
        self.buildings = {r["id"]: r for r in csv.DictReader(open(BUILDINGS, encoding="utf-8"))}
        self.boxes_of_scene = defaultdict(list)
        for p, g in self.boxes:
            sid = (p.get("parent_id") or p.get("building_id") or "").split("-")[0]
            self.boxes_of_scene[sid].append((p, g))
        self.lift = self.hill_lift()

    def freeze_rocks(self):
        """After the rockeries are placed: the clearances round them, prepared."""
        self.rock_near = self.rock_union.buffer(ROCK_CLEAR_M)
        self.rock_far = self.rock_union.buffer(3.0)
        self.rock_water = self.rock_union.buffer(1.0)
        for g in (self.rock_near, self.rock_far, self.rock_water):
            shapely.prepare(g)

    def hill_lift(self):
        """What the generated hills add to the walk surface, on its lattice: ground.bin's land minus its yalt, rasterised (ground1860.rasterise)."""
        import ground1860

        meta = json.load(open(GENERATED / "ground.json", encoding="utf-8"))
        buf = (GENERATED / "ground.bin").read_bytes()
        x0, z0 = meta["domain"][:2]
        g = meta["grid"]
        out = np.zeros((g["height"], g["width"]))
        for c in meta["parts"]["land"]:
            q = np.frombuffer(buf, "<i2", c["verts"] * 3, c["pos"]).reshape(-1, 3).astype(float)
            idx = np.frombuffer(buf, "<u2", c["indices"], c["idx"])
            yalt = np.frombuffer(buf, "<i2", c["verts"], c["yalt"]).astype(float) / 100
            d = q[:, 1] / 100 - yalt
            if not np.any(d > 0.01):
                continue
            r = ground1860.rasterise(np.column_stack([x0 + q[:, 0] / 10, z0 + q[:, 2] / 10]), d, idx, g["x0"], g["z0"], g["width"], g["height"])
            ok = np.isfinite(r)
            out[ok] = np.maximum(out[ok], r[ok])
        return out

    def lift_at(self, x, z):
        G = self.G
        i, j, a, b = G._cell(x, z)
        v = self.lift[j:j + 2, i:i + 2]
        return float((v[0, 0] * (1 - a) + v[0, 1] * a) * (1 - b) + (v[1, 0] * (1 - a) + v[1, 1] * a) * b)

    def region(self, sid):
        """The scene's outline, or for a scene with none (a lake such as 福海 YM54) its water body's shore; None if it has no position."""
        if sid.startswith("GARDEN"):
            return self.gardens.get(sid.split("-")[-1], self.inside)
        if sid in self.scenes:
            return self.scenes[sid][0]
        b = self.buildings.get(sid)
        if not b or not b.get("lon"):
            return None
        pt = Point(*to_xz(float(b["lon"]), float(b["lat"])))
        near = [(g.distance(pt), g) for p, g in self.water_feats if g.distance(pt) < 60]
        if near:
            w = min(near, key=lambda t: (t[0], -t[1].area))[1]
            return w.buffer(SCENE_WITHOUT_OUTLINE_R).intersection(self.inside)
        return pt.buffer(60).intersection(self.inside)

    def main_hall(self, sid):
        bs = self.boxes_of_scene.get(sid, [])
        bs = [b for b in bs if not b[0].get("shape") and b[0].get("hall_class") != "gallery"] or bs
        return max(bs, key=lambda b: b[1].area) if bs else None

    def hall_named(self, sid, row):
        text = " ".join([row.get("place_text", ""), row.get("quote", ""), row.get("note", "")])
        for m in re.findall(r"\b([A-Z]{2}\d{2}-[A-Z0-9]+)\b", text):
            bs = [b for b in self.boxes if b[0].get("building_id") == m]
            if bs:
                return bs[0]
        if "-" in sid:
            bs = [b for b in self.boxes if b[0].get("building_id") == sid]
            if bs:
                return bs[0]
        best = None
        scene = sid.split("-")[0]
        for p, g in self.boxes_of_scene.get(scene, []):
            name = self.buildings.get(p.get("building_id"), {}).get("name_zh", "")
            if len(name) >= 2 and name in text and (best is None or len(name) > best[0]):
                best = (len(name), (p, g))
        return best[1] if best else None


def front_of(p, g):
    """The box's centre, its front (unit vector the hall faces, x east z south), its half frontage and half depth."""
    c = np.array(g.centroid.coords[0])
    a = math.radians(p.get("orientation_deg") or 180)
    f = np.array([math.sin(a), -math.cos(a)])
    return c, f, (p.get("frontage_m") or 10) / 2, (p.get("depth_m") or 8) / 2


def zone(site, sid, place, row, hall):
    """The land (or water) an area of this place takes in the scene, before the clearances; and whether it fell back to the scene."""
    R = site.region(sid.split("-")[0])
    if R is None:
        return None, True
    free, cfree = site.free.intersection(R.buffer(4)), site.court_free.intersection(R.buffer(4))
    cx, cz = R.centroid.x, R.centroid.y
    x0, z0, x1, z1 = R.bounds
    big = 4000
    if place in ("north", "south", "east", "west"):
        h = {"north": sbox(-big, -big, big, cz - 0.1 * (z1 - z0)), "south": sbox(-big, cz + 0.1 * (z1 - z0), big, big),
             "west": sbox(-big, -big, cx - 0.1 * (x1 - x0), big), "east": sbox(cx + 0.1 * (x1 - x0), -big, big, big)}[place]
        z = free.intersection(h)
    elif place == "shore":
        z = site.shore_land.intersection(R.buffer(SHORE_BAND_M[1] + 4))
    elif place == "island":
        z = free.intersection(site.islands)
    elif place == "hill":
        z = free.intersection(site.hills.buffer(1))
        if z.area < 30:
            z = free.intersection(unary_union([g for p, g in site.hill_feats if g.intersects(R.buffer(40))]).buffer(1)).intersection(R.buffer(40))
    elif place == "hill_foot":
        z = free.intersection(site.hills.buffer(9)).difference(site.hills)
    elif place in ("court", "front_court", "rear_court"):
        z = cfree
        if place != "court" and hall is not None:
            # the half-plane in front of (or behind) the main hall's centre line
            c, f, hf, hd = front_of(*hall)
            f = f if place == "front_court" else -f
            u = np.array([-f[1], f[0]])
            half = Polygon([c + u * big, c - u * big, c - u * big + f * big, c + u * big + f * big])
            z = z.intersection(half)
    elif place == "around_hall" and hall is not None:
        g = hall[1]
        z = site.free.union(site.court_free).intersection(g.buffer(HALL_BAND_M[1])).difference(g.buffer(HALL_BAND_M[0]))
    elif place in ("dike", "along_way", "bridge"):
        if place == "bridge":
            ends = [Point(*l.coords[0]) for b, l in site.bridges if l.intersects(R.buffer(30))] + [Point(*l.coords[-1]) for b, l in site.bridges if l.intersects(R.buffer(30))]
            z = free.union(cfree).intersection(unary_union([e.buffer(12) for e in ends])) if ends else Polygon()
        else:
            kinds = ("dike", "causeway") if place == "dike" else ("paved_way", "imperial_road", "causeway", "dike", "service_path", "courtyard_path")
            lines = [l for p, l in site.paths if p["kind"] in kinds and l.intersects(R.buffer(10))]
            z = free.union(cfree).intersection(unary_union([l.buffer(9) for l in lines])) if lines else Polygon()
    elif place == "rockery":
        z = free.intersection(site.rock_union.buffer(6)).intersection(R.buffer(6)) if not site.rock_union.is_empty else Polygon()
    elif place == "pond":
        reach = 90 if re.search(r"whole|almost all|8\d%|9\d%|全|满", row.get("note", "") + row.get("place_text", "")) else 30
        z = site.water.buffer(-LOTUS_EDGE_M).intersection(R.buffer(reach))
        z = z.difference(site.bridge_clear.buffer(LOTUS_BRIDGE_M - BRIDGE_CLEAR_M)).difference(site.boat.buffer(LOTUS_ROUTE_M) if not site.boat.is_empty else Polygon()).difference(site.box_union.buffer(2))
    elif place == "lake_edge":
        z = site.water.intersection(site.inside.difference(site.water).buffer(REED_BAND_M)).buffer(-0.3).intersection(R.buffer(30))
        z = z.difference(site.bridge_clear).difference(site.boat.buffer(LOTUS_ROUTE_M) if not site.boat.is_empty else Polygon()).difference(site.box_union.buffer(2)).difference(site.landings.buffer(3))
    elif place == "outside_wall" and sid.startswith("GARDEN"):
        g = sid.split("-")[-1]
        walls = [w for k, w in site.outer_walls.items() if g in (k, "ALL")]
        z = free.intersection(unary_union([w.buffer(14) for w in walls])).difference(unary_union([w.buffer(2) for w in walls])) if walls else Polygon()
    elif place == "outside_wall":
        # beyond the compound's own walls: the land round its outline
        z = site.free.intersection(R.buffer(30)).difference(R)
    else:
        z = free
    z = z.buffer(0) if not z.is_empty else z
    return z, False


def sample_darts(geom, n, min_d, rng, tries=30):
    """Up to n points inside geom at least min_d apart (dart throwing, seeded)."""
    if geom.is_empty or n <= 0:
        return np.zeros((0, 2))
    shapely.prepare(geom)
    x0, z0, x1, z1 = geom.bounds
    out = []
    cell = max(min_d, 0.5)
    grid = {}
    need = int(n)
    for _ in range(tries):
        k = max(need * 4, 64)
        xs, zs = rng.uniform(x0, x1, k), rng.uniform(z0, z1, k)
        ok = shapely.contains_xy(geom, xs, zs)
        for x, z in zip(xs[ok], zs[ok]):
            i, j = int(x // cell), int(z // cell)
            if any(math.hypot(x - a, z - b) < min_d for di in (-1, 0, 1) for dj in (-1, 0, 1) for a, b in grid.get((i + di, j + dj), ())):
                continue
            grid.setdefault((i, j), []).append((x, z))
            out.append((x, z))
            if len(out) >= need:
                return np.array(out)
    return np.array(out) if out else np.zeros((0, 2))


def noise_keep(xs, zs, share, s, scale=38.0):
    """A smooth seeded field over the site: keep the points under the share's quantile, so a fill leaves open glades, not a rash of single trees."""
    r = np.random.default_rng(s)
    ph = r.uniform(0, 2 * math.pi, 6)
    k = [(1 / scale, 0.7 / scale), (-0.6 / scale, 1.1 / scale), (1.7 / scale, -1.3 / scale)]
    v = sum(np.sin(xs * a + zs * b + ph[i]) + np.sin(xs * b - zs * a + ph[i + 3]) * 0.6 for i, (a, b) in enumerate(k))
    return v < np.quantile(v, share) if len(v) > 20 else np.ones(len(xs), bool)


class Planter:
    def __init__(self, site):
        self.site = site
        self.plants = []  # dicts
        self.hash = defaultdict(list)
        self.cell = 4.0

    def clear_of_others(self, x, z, r, factor):
        i, j = int(x // self.cell), int(z // self.cell)
        reach = int(math.ceil((r + 6) / self.cell))
        for di in range(-reach, reach + 1):
            for dj in range(-reach, reach + 1):
                for q in self.hash.get((i + di, j + dj), ()):
                    if math.hypot(x - q["x"], z - q["z"]) < (r + q["c"] / 2) * factor:
                        return False
        return True

    def ok(self, x, z, form, crown, area):
        """The crown this plant may have here (its own, or down to CROWN_FIT of it beside a hall or a gallery), or 0 if it may not stand here."""
        s = self.site
        x, z = round(x * 10) / 10, round(z * 10) / 10  # as stored
        if form in WATER_FORMS:
            if not (s.G.is_water(x, z) and s.G.land_at(x, z) is None) or s.rock_water.contains(Point(x, z)):
                return 0
            # one body's level all round, so the clump never sits where two levels meet
            levels = {s.G.level_at(x + dx, z + dz) for dx in (-1.5, 0, 1.5) for dz in (-1.5, 0, 1.5)}
            return crown if len(levels) == 1 and None not in levels else 0
        y = s.G.land_at(x, z)
        if y is None or s.G.is_water(x, z):
            return 0
        # the ground under the trunk may fall away no more than the trunk's sink (as tools/check_greens.py measures it)
        rt = max(FORM[form][0] * 1.15 * 0.05, 0.25)
        lows = [s.G.land_at(x + dx, z + dz) for dx, dz in ((rt, 0), (-rt, 0), (0, rt), (0, -rt))]
        if any(v is None for v in lows) or y - min(lows) > TRUNK_SINK_M * 0.8:
            return 0
        pt = Point(x, z)
        r = crown / 2
        if s.way_clear.contains(pt) or s.wall_clear.contains(pt) or s.bridge_clear.contains(pt) or s.landings.contains(pt) or s.fields.contains(pt):
            return 0
        if (s.willow_clear if form == "willow" else s.water_clear).contains(pt):
            return 0
        if s.courts.contains(pt) and not area.get("in_court"):
            return 0
        if s.rock_near.contains(pt):
            return 0
        if form not in ("shrub", "hedge"):
            near = s.box_tree.query(pt.buffer(r + BOX_CLEAR_M))
            if len(near):
                d = min(s.box_polys[i].distance(pt) for i in near)
                if d < BOX_MIN_M:
                    return 0
                r = min(r, d - BOX_CLEAR_M)
            if s.gallery_clear.contains(pt):
                d = s.galleries.distance(pt)
                r = min(r, (d - GALLERY_CLEAR_M) / 0.8)
            if form != "bamboo" and s.rock_far.contains(pt):
                r = min(r, s.rock_union.distance(pt) / 0.5)
        else:
            near = s.box_tree.query(pt.buffer(BOX_MIN_M))
            if len(near) and min(s.box_polys[i].distance(pt) for i in near) < BOX_MIN_M:
                return 0
        return 2 * r if r >= CROWN_FIT * crown / 2 else 0

    def add(self, x, z, sp, form, h, c, area):
        x, z = round(x * 10) / 10, round(z * 10) / 10
        p = {"x": float(x), "z": float(z), "sp": sp, "form": form, "h": h, "c": c, "area": area["idx"]}
        if form in WATER_FORMS:
            lev = self.site.G.level_at(x, z)
            p["y"] = lev if lev is not None else 0.0
            p["lift"] = 0.0
        else:
            p["y"] = self.site.G.land_at(x, z)
            p["lift"] = self.site.lift_at(x, z)
        self.plants.append(p)
        self.hash[(int(x // self.cell), int(z // self.cell))].append(p)
        return p

    def place(self, area, pts, sp, form, h, c, factor, rng):
        n = 0
        for x, z in pts:
            hv, cv = h * (1 + rng.uniform(-VARY, VARY)), c * (1 + rng.uniform(-VARY, VARY))
            fit = self.ok(x, z, form, cv, area)
            if not fit:
                continue
            if fit < cv:
                hv *= max(fit / cv, 0.75)
                cv = fit
            if not self.clear_of_others(x, z, cv / 2, factor):
                continue
            self.add(x, z, sp, form, hv, cv, area)
            n += 1
        return n


def line_points(lines, spacing, offset, phase, rng):
    out = []
    for l in lines:
        for side in (-1, 1):
            o = l.offset_curve(side * offset) if offset else l
            for g in getattr(o, "geoms", [o]):
                if g.is_empty or g.length < spacing:
                    continue
                d = phase * spacing
                while d < g.length:
                    p = g.interpolate(d)
                    out.append((p.x + rng.uniform(-0.4, 0.4), p.y + rng.uniform(-0.4, 0.4)))
                    d += spacing
    return out


# ---- rockeries ----
ROCK_NAMED = ("青莲朵", "青蓮朵", "青云片", "青雲片", "玲峰", "立石", "standing", "upright stone", "single stone")  # a named or standing stone is one stone, whatever else the text says
ROCK_WORDS = [
    ("shore", ("shore", "bank", "water", "矶", "磯", "pool", "lake", "pond", "stream", "fishing", "cascade", "瀑", "waterfall", "溪")),
    ("screen", ("石壁", "screen", "rock wall", "峭石", "cliff", "壁")),
    ("hill", ("假山", "rockery", "rock hill", "hill", "山", "洞", "cave", "叠石", "疊石", "peak", "峰")),
    ("standing", ("立石", "standing", "stone", "石", "玲", "rock")),
]


def rock_kind(text, place):
    if place == "shore" or place == "lake_edge":
        return "shore"
    if place in ("court", "front_court", "rear_court"):
        return "standing"
    if place == "hill":
        return "hill"
    t = text.lower()
    if any(w in t for w in ROCK_NAMED):
        return "standing"
    for k, words in ROCK_WORDS:
        if any(w in t for w in words):
            return k
    return "standing"


def rock_place(where):
    w = where.lower()
    if any(k in w for k in ("shore", "bank", "water", "pool", "lake", "pond", "stream", "矶")):
        return "shore"
    if "court" in w or "庭" in w:
        return "court"
    if any(k in w for k in ("hill", "peak", "mound", "山")):
        return "hill"
    return "around_hall"


ROCK_SIZE = {"standing": (1.6, 1.1, 3.2), "screen": (None, 3.2, 4.0), "shore": (16.0, 4.4, 1.6), "hill": (13.0, 10.0, 5.0)}  # length, width, height above the highest ground. C


def place_rock(site, sid, kind, hall, rng):
    """A rockery's footprint in scene metres, or None."""
    R = site.region(sid.split("-")[0])
    if R is None:
        return None
    L, W, H = ROCK_SIZE[kind]
    obstacles = unary_union([site.box_union.buffer(1.0), site.way_strips.buffer(0.3), site.bridge_clear, site.wall_clear, site.landings, site.rock_union.buffer(1.5)])
    if hall is None:
        hall = site.main_hall(sid.split("-")[0])
    if kind == "standing":
        cand = site.court_free.union(site.free).intersection(R.buffer(5))
        if hall is not None:
            c, f, hf, hd = front_of(*hall)
            for d in (hd + 6, hd + 9, hd + 4, hd + 12):
                p = Point(c[0] + f[0] * d, c[1] + f[1] * d)
                fp = shapely.affinity.rotate(sbox(-L / 2, -W / 2, L / 2, W / 2), rng.uniform(0, 180), origin=(0, 0))
                fp = shapely.affinity.translate(fp, p.x, p.y)
                if not fp.intersects(obstacles) and cand.contains(p) and site.G.land_at(p.x, p.y) is not None and not site.water.intersects(fp):
                    return fp
        pts = sample_darts(cand.difference(obstacles.buffer(1.5)), 1, 1, rng)
        if len(pts):
            return Point(*pts[0]).buffer(L / 2, 6)
        return None
    if kind == "screen":
        if hall is None:
            return None
        c, f, hf, hd = front_of(*hall)
        Lx = max(min(2 * hf * 0.9, 26), 8)
        for d in (hd + 5, hd + 7.5, hd + 10):
            ctr = c - f * d
            u = np.array([-f[1], f[0]])
            a, b = ctr - u * Lx / 2, ctr + u * Lx / 2
            fp = LineString([a, b]).buffer(W / 2, cap_style="round").difference(obstacles)
            fp = max(polys(fp), key=lambda g: g.area) if polys(fp) else None
            if fp is not None and fp.area > 0.5 * Lx * W and not fp.intersects(site.water.buffer(0.5)):
                return fp
        kind = "hill"
    if kind == "shore":
        shore = R.buffer(15).intersection(site.water.boundary)
        if shore.is_empty:
            return None
        ref = Point(*front_of(*hall)[0]) if hall is not None else R.centroid
        lines = [g for g in getattr(shore, "geoms", [shore]) if g.length > 6]
        if not lines:
            return None
        for t in range(6):
            line = min(lines, key=lambda g: g.distance(ref) + rng.uniform(0, 25) * t)
            d0 = line.project(ref)
            seg = shapely.ops.substring(line, max(0, d0 - L / 2 + rng.uniform(-6, 6)), min(line.length, d0 + L / 2 + rng.uniform(-6, 6)))
            fp = seg.buffer(W / 2, cap_style="round").difference(obstacles)
            fp = max(polys(fp), key=lambda g: g.area) if polys(fp) else None
            if fp is not None and fp.area > 12 and fp.intersects(site.water) and fp.difference(site.water).area > 2:
                return fp
        return None
    # hill: on the scene's highest hill, else beside the main hall
    L, W, H = ROCK_SIZE["hill"]
    hs = [(p.get("height_est_m") or 0, g) for p, g in site.hill_feats if g.intersects(R.buffer(30))]
    if hs:
        h, g = max(hs, key=lambda t: t[0])
        p = g.representative_point()
        best, best_y = p, site.G.land_at(p.x, p.y) or 0
        for x, z in sample_darts(g, 40, 2, rng):
            y = site.G.land_at(x, z)
            if y is not None and y > best_y:
                best, best_y = Point(x, z), y
        r = min(L / 2, max(3.0, math.sqrt(g.area / math.pi) * 0.45))
        fp = best.buffer(r, 10).difference(obstacles)
        fp = max(polys(fp), key=lambda g: g.area) if polys(fp) else None
        if fp is not None and fp.area > 10:
            return fp
    if hall is not None:
        c, f, hf, hd = front_of(*hall)
        u = np.array([-f[1], f[0]])
        for side in (1, -1):
            ctr = c + u * side * (hf + 9)
            fp = Point(*ctr).buffer(5, 10).difference(obstacles)
            fp = max(polys(fp), key=lambda g: g.area) if polys(fp) else None
            if fp is not None and fp.area > 20 and site.G.land_at(*ctr) is not None:
                return fp
    return None


def rock_levels(site, fp):
    """Base (the lowest ground or bed under it, less the sink) and top (its height over the highest ground under it)."""
    xs, zs = [], []
    x0, z0, x1, z1 = fp.bounds
    for x in np.arange(x0, x1 + 1e-6, 1.0):
        for z in np.arange(z0, z1 + 1e-6, 1.0):
            if fp.contains(Point(x, z)):
                xs.append(x)
                zs.append(z)
    xs += [c[0] for c in fp.exterior.coords]
    zs += [c[1] for c in fp.exterior.coords]
    ys = [site.G.at(x, z) for x, z in zip(xs, zs)]
    land = [site.G.land_at(x, z) for x, z in zip(xs, zs)]
    land = [v for v in land if v is not None]
    return min(ys) - ROCK_SINK_M, (max(land) if land else max(ys))


# ---- main ----
def rows():
    out = []
    for r in csv.DictReader(open(SPECIES, encoding="utf-8")):
        out.append(r)
    return out


def merge_rows(rs):
    """Rows that say the same thing (scene, plant, place, hall) make one area."""
    groups = defaultdict(list)
    for r in rs:
        hall = re.findall(r"\b([A-Z]{2}\d{2}-[A-Z0-9]+)\b", r["place_text"])
        groups[(r["scene_id"], species_key(r["plant_zh"], r["form"]), r["form"], r["place"], r["role"] == "avenue", hall[0] if hall and r["place"] in ("around_hall", "court") else "")].append(r)
    return groups


def lonlat_ring(coords, nd=7):
    xs, zs = np.array([c[0] for c in coords]), np.array([c[1] for c in coords])
    lon, lat = to_lonlat(xs, zs)
    return [[round(float(a), nd), round(float(b), nd)] for a, b in zip(lon, lat)]


def geo_of(g, tol=0.6):
    g = g.simplify(tol, preserve_topology=True)
    ps = [p for p in polys(g) if p.area > 1.0]
    if not ps:
        return None
    rings = [[lonlat_ring(p.exterior.coords)] + [lonlat_ring(i.coords) for i in p.interiors if Polygon(i).area > 25] for p in ps]
    return {"type": "Polygon", "coordinates": rings[0]} if len(rings) == 1 else {"type": "MultiPolygon", "coordinates": rings}


def main():
    site = Site()
    meta = json.load(open(GENERATED / "ground.json", encoding="utf-8"))
    dx0, dz0 = meta["domain"][:2]
    all_rows = rows()
    keep = [r for r in all_rows if r["use"] == "keep"]
    planted = [r for r in keep if r["form"] not in ("none", "rock") and r["place"] in PLACES and r["place"] != "field"]
    rocks_rows = [r for r in keep if r["form"] == "rock"]
    print(f"species.csv: {len(all_rows)} rows, {len(keep)} kept; drawn as plants {len(planted)}, rocks {len(rocks_rows)}, not drawn {len(keep) - len(planted) - len(rocks_rows)}")

    species = {}  # key -> index

    def sp_index(key, form, row=None):
        if key not in species:
            spec = PLANT.get(key)
            f = spec[0] if spec else form
            h, c = (spec[1], spec[2]) if spec else FORM[f][:2]
            bloom, autumn = (spec[3], spec[4]) if spec else FORM_COLOURS[f]
            species[key] = {"i": len(species), "key": key, "form": f, "h": h, "c": c, "bloom": bloom, "autumn": autumn,
                            "latin": (row or {}).get("latin", ""), "en": (row or {}).get("name_en", "")}
        return species[key]

    # 1. rockeries first: the plants keep clear of them
    rock_groups = defaultdict(list)
    for r in rocks_rows:
        hall = re.findall(r"\b([A-Z]{2}\d{2}-[A-Z0-9]+)\b", r["place_text"])
        kind = rock_kind(" ".join([r["plant_zh"], r["place_text"], r["note"], r["quote"]]), r["place"])
        rock_groups[(r["scene_id"], kind, hall[0] if hall else "")].append(("row", r))
    for r in csv.DictReader(open(ROCK_READINGS, encoding="utf-8")):
        r = dict(r, scene_id=(r["scene_id"] or "").split(";")[0])
        if not r["scene_id"]:
            continue  # a reading with no scene: kept in the readings, not placed
        place = rock_place(r["where"])
        kind = rock_kind(r["where"] + " " + r["what"], place)
        rock_groups[(r["scene_id"], kind, "")].append(("reading", r))
    rockeries = []
    for (sid, kind, hall_id), items in sorted(rock_groups.items()):
        if sid.startswith("GARDEN"):
            continue
        rng = np.random.default_rng(seed_of("rock", sid, kind, hall_id))
        first = next((x for t, x in items if t == "row"), None) or {"place_text": items[0][1]["where"], "quote": items[0][1]["what"], "note": ""}
        hall = site.hall_named(sid, first) if first else None
        fp = place_rock(site, sid, kind, hall, rng)
        if fp is None:
            rockeries.append({"scene": sid, "kind": kind, "placed": False, "items": items})
            continue
        fp = fp.simplify(0.2)
        base, top_ground = rock_levels(site, fp)
        if kind == "screen" and fp.intersects(site.hills.buffer(-1)) is False and fp.area > 200:
            kind = "hill"
        L, W, H = ROCK_SIZE[kind]
        h_above = H * (1 + rng.uniform(-0.2, 0.2))
        site.rocks.append(fp)
        site.rock_union = unary_union(site.rocks)
        srcs = sorted({s for t, x in items for s in (x.get("sources", "")).split(";") if s})
        grades = [x.get("confidence") or x.get("grade") or "C" for t, x in items]
        conf = min(grades, key=lambda g: GRADE.get(g, 2))
        leaf = any(t == "row" and x.get("source_kind") == "leaf" for t, x in items)
        rockeries.append({"scene": sid, "kind": kind, "placed": True, "fp": fp, "base": base, "top": top_ground + h_above, "h_above": h_above, "sources": srcs,
                          "confidence": conf, "extent_confidence": "B" if leaf and kind != "hill" else "C", "items": items, "hall": hall[0]["building_id"] if hall else ""})
    site.freeze_rocks()
    print(f"rockeries: {sum(r['placed'] for r in rockeries)} placed of {len(rockeries)} groups")

    # 2. the sourced areas
    planter = Planter(site)
    areas = []
    groups = merge_rows(planted)
    SPECIFIC = {"scene": 3, "north": 2, "south": 2, "east": 2, "west": 2, "outside_wall": 3}
    order = sorted(groups.items(), key=lambda kv: (min(GRADE[r["confidence"]] for r in kv[1]), {"specimen": 0, "avenue": 1}.get(kv[1][0]["role"], 2), SPECIFIC.get(kv[0][3], 1), kv[0]))
    for key, rs in order:
        sid, spk, form, place, is_avenue, hall_id = key
        best = min(rs, key=lambda r: GRADE[r["confidence"]])
        sp = sp_index(spk, form, best)
        form = sp["form"]
        rng = np.random.default_rng(seed_of(*key))
        hall = None if sid.startswith("GARDEN") else (site.hall_named(sid, best) or (site.main_hall(sid.split("-")[0]) if place in ("around_hall", "front_court", "rear_court") else None))
        if place == "pond" and form not in WATER_FORMS:
            place = "shore"
        if sid.startswith("GARDEN"):
            if place == "outside_wall" or "wall" in (best["place_text"] + best["note"]).lower():
                z, fell = zone(site, sid, "outside_wall", best, None)
            else:
                areas.append({"idx": len(areas), "key": key, "rows": rs, "sp": sp, "placed": 0, "skip": "garden-wide: informs the fill, no area of its own"})
                continue
        else:
            z, fell = zone(site, sid, place, best, hall)
        if z is None or z.is_empty or z.area < 2:
            z2, _ = zone(site, sid, "pond" if form in WATER_FORMS else "scene", best, hall)
            if z2 is not None and not z2.is_empty and z2.area >= 2 and form not in WATER_FORMS:
                z, fell = z2, True
            elif form in WATER_FORMS and z2 is not None and not z2.is_empty:
                z, fell = z2, True
            else:
                areas.append({"idx": len(areas), "key": key, "rows": rs, "sp": sp, "placed": 0, "skip": "no land (or water) for this place in the scene"})
                continue
        # a court takes plants only where the row puts them in a court, or a specimen beside its hall
        a = {"idx": len(areas), "key": key, "rows": rs, "sp": sp, "geom": z, "fell": fell, "in_court": place in ("court", "front_court", "rear_court") or (place == "around_hall" and best["role"] == "specimen"), "hall": hall[0]["building_id"] if hall else ""}
        areas.append(a)
        n_stated = next((count_from(r) for r in rs if count_from(r)), None)
        dens = density_of(best)
        h, c = sp["h"], sp["c"]
        if best.get("height_m"):
            h = float(best["height_m"])
        spacing = c * FORM[form][2]
        factor = 0.9 if dens == "dense" else 1.0
        if form in WATER_FORMS:
            share = 0.6 if GRADE[best["confidence"]] < 2 else 0.35  # a typical (C) reed or lotus bed is kept thinner
            m = re.search(r"(\d{2})\s*[-–]?\s*(\d{2})?\s*%", best["note"] + best["place_text"])
            if m:
                share = (int(m.group(1)) + int(m.group(2) or m.group(1))) / 200
            elif "whole" in (best["note"] + best["place_text"]).lower():
                share = 0.85
            cap = 9000 if form == "lotus" else 5000
            n = min(int(z.area / (spacing ** 2) * 1.15), cap)
            pts = sample_darts(z, n, spacing * 0.92, rng, tries=8)
            if len(pts):
                pts = pts[noise_keep(pts[:, 0], pts[:, 1], share, seed_of("w", *key), scale=14.0)]
            a["placed"] = planter.place(a, pts, sp["i"], form, h, c, 0.85, rng)
            a["pattern"] = "clumps"
            continue
        if is_avenue or place in ("dike", "along_way"):
            R = site.region(sid.split("-")[0]) if not sid.startswith("GARDEN") else z
            kinds = ("dike", "causeway") if place == "dike" else ("paved_way", "imperial_road", "causeway", "dike")
            lines = [l for p, l in site.paths if p["kind"] in kinds and l.intersects(R.buffer(10))]
            if lines:
                width = max((p.get("width_m") or 3) for p, l in site.paths if l in lines)
                pts = line_points([l.intersection(R.buffer(10)) for l in lines], max(spacing * 0.9, 5), width / 2 + 2.2, (seed_of(spk) % 100) / 100, rng)
            else:
                shore = site.inside.difference(site.water).buffer(0).boundary.intersection(R.buffer(8))
                shore = [g for g in getattr(shore, "geoms", [shore]) if isinstance(g, LineString)]
                pts = line_points(shore, max(spacing * 0.9, 5), 0, (seed_of(spk) % 100) / 100, rng)
                pts = [p for p in pts if site.water.distance(Point(*p)) < 0.2]
                # pulled 2.5 m inland
                out = []
                for x, zz in pts:
                    q = Point(x, zz)
                    for d in (2.4, 3.0, 3.8):
                        best_p = None
                        for t in range(8):
                            ang = t * math.pi / 4
                            cand = (x + d * math.cos(ang), zz + d * math.sin(ang))
                            if site.water.distance(Point(*cand)) >= d - 0.3:
                                best_p = cand
                                break
                        if best_p:
                            out.append(best_p)
                            break
                pts = out
            if n_stated:
                pts = pts[: int(n_stated * 1.5)] if len(pts) > n_stated * 1.5 else pts
            a["placed"] = planter.place(a, pts, sp["i"], form, h, c, 0.75, rng)
            a["pattern"] = "avenue"
            if a["placed"]:
                continue
        if best["role"] == "specimen" and hall is not None and (n_stated or 2) <= 6 and place in ("around_hall", "front_court", "court", "scene", "south"):
            cc, f, hf, hd = front_of(*hall)
            u = np.array([-f[1], f[0]])
            n_want = int(n_stated or 2)
            pts = []
            for d in (hd + max(c / 2 + 1.5, 4), hd + 7, hd + 10):
                for k in range(n_want):
                    side = (k % 2) * 2 - 1
                    lat = (hf * 0.55 + c * 0.2) * (1 + (k // 2) * 0.7)
                    pts.append(cc + f * d + u * side * lat)
            a["placed"] = 0
            got = []
            for x, zz in pts:
                if len(got) >= n_want:
                    break
                if planter.place(a, [(x, zz)], sp["i"], form, h, c, 1.0, rng):
                    got.append((x, zz))
            a["placed"] = len(got)
            a["pattern"] = "pair" if n_want == 2 else "single"
            if a["placed"]:
                continue
        if form == "topiary":
            hall_c = front_of(*hall) if hall is not None else None
            ang = math.degrees(math.atan2(hall_c[1][1], hall_c[1][0])) if hall_c else 0
            step = max(spacing, 4.5)
            x0, z0, x1, z1 = z.bounds
            gx, gz = np.meshgrid(np.arange(-300, 300, step), np.arange(-300, 300, step))
            P = np.column_stack([gx.ravel(), gz.ravel()])
            a_r = math.radians(ang)
            R2 = np.array([[math.cos(a_r), -math.sin(a_r)], [math.sin(a_r), math.cos(a_r)]])
            P = P @ R2.T + np.array(z.centroid.coords[0])
            P = P[shapely.contains_xy(z, P[:, 0], P[:, 1])]
            if n_stated and len(P) > n_stated:
                d = np.hypot(*(P - np.array(z.centroid.coords[0])).T)
                P = P[np.argsort(d)[: int(n_stated)]]
            a["placed"] = planter.place(a, P, sp["i"], form, h, c, 0.8, rng)
            a["pattern"] = "grid"
            continue
        if n_stated:
            n = n_stated
        elif best["role"] == "specimen":
            n = SPECIMEN_N  # a specimen with no count: a few trees, never a grove
        elif form == "shrub":
            n = FLOWER_BED_N
        else:
            n = z.area / (spacing ** 2) * DENSITY["sparse" if place in ("scene", "outside_wall") and dens == "medium" else dens] * (0.6 if fell else 1.0)
        n = int(min(max(n, 1), z.area / (spacing ** 2) * 1.2, 2500, FLOWER_BED_MAX if form in ("shrub", "hedge") and not n_stated else 1e9))
        pts = sample_darts(z, n * 3, spacing * (0.85 if dens == "dense" else 1.0), rng)
        placed = 0
        for p in pts:
            if placed >= n:
                break
            placed += planter.place(a, [p], sp["i"], form, h, c, factor, rng)
        a["placed"] = placed
        a["pattern"] = "groves"
    print(f"sourced areas: {sum(1 for a in areas if a.get('placed'))} with plants, {len(planter.plants)} plants")

    # 3. the fill: what no source names. One area per garden and zone, its plants drawn from the zone's typical mix
    n_before = len(planter.plants)
    # what the sourced plants already hold: each one's crown and a ring round it (the fill keeps its distance from a sourced group too), and the rockeries
    taken = unary_union(shapely.buffer(shapely.points([(p["x"], p["z"]) for p in planter.plants if p["form"] not in WATER_FORMS]),
                                       [p["c"] / 2 + FILL_GAP_M for p in planter.plants if p["form"] not in WATER_FORMS], quad_segs=4).tolist() + [site.rock_union.buffer(2)])
    for g, garden in sorted(site.gardens.items()):
        for zone_kind in ("shore", "hill", "land"):
            if zone_kind == "shore":
                fz = garden.intersection(site.shore_land).intersection(site.water.buffer(4.0))
            elif zone_kind == "hill":
                fz = garden.intersection(site.hills).intersection(site.free)
            else:
                fz = garden.difference(site.hills).difference(site.water.buffer(4.0)).intersection(site.free)
            fz = fz.difference(taken).buffer(0)
            if fz.is_empty:
                continue
            mix = [(sp_index(k, PLANT[k][0] if k in PLANT else ("blossom" if k == "花树" else "broad")), share) for k, share in FILL_MIX[zone_kind]]
            rng = np.random.default_rng(seed_of("fill", g, zone_kind))
            # garden-wide rows (GARDEN-YM, -ALL) of this zone: they name what grows, not where
            zplaces = {"shore": ("shore", "lake_edge", "dike"), "hill": ("hill", "hill_foot"), "land": ("scene", "along_way", "around_hall", "court")}[zone_kind]
            garden_rows = [r for r in planted if r["scene_id"] in (f"GARDEN-{g}", "GARDEN-ALL") and r["place"] in zplaces and r["form"] not in WATER_FORMS and "wall" not in (r["place_text"] + r["note"]).lower()]
            a = {"idx": len(areas), "key": (f"GARDEN-{g}", "; ".join(f"{sp['key']} {round(share * 100)}%" for sp, share in mix), "mixed", zone_kind, False, ""), "rows": [], "garden_rows": garden_rows,
                 "sp": mix[0][0], "mix": mix, "geom": fz, "fell": False, "fill": zone_kind, "garden": g, "in_court": False}
            areas.append(a)
            spacing = sum(sp["c"] * FORM[sp["form"]][2] * share for sp, share in mix) * (1.9 if zone_kind == "shore" else 1.0)
            if zone_kind == "shore":
                # a band: its length is its area over its width; a willow every SHORE_WILLOW_M along it
                n = int(fz.area / (SHORE_BAND_M[1] - SHORE_BAND_M[0]) / SHORE_WILLOW_M * FILL_SHARE[zone_kind])
                pts = sample_darts(fz, int(n / FILL_SHARE[zone_kind]) + 10, SHORE_WILLOW_M * 0.75, rng, tries=8)
            else:
                n = int(fz.area / (spacing ** 2) * FILL_SHARE[zone_kind])
                pts = sample_darts(fz, int(n / FILL_SHARE[zone_kind]) + 10, spacing * 0.9, rng, tries=6)
            if len(pts):
                pts = pts[noise_keep(pts[:, 0], pts[:, 1], FILL_SHARE[zone_kind], seed_of("glade", g, zone_kind), scale=30.0 if zone_kind != "shore" else 22.0)]
            cum = np.cumsum([share for _, share in mix])
            placed = 0
            for x, zz in pts:
                sp = mix[int(np.searchsorted(cum, rng.uniform(0, cum[-1])))][0]
                placed += planter.place(a, [(x, zz)], sp["i"], sp["form"], sp["h"], sp["c"], 1.0, rng)
            a["placed"] = placed
            a["pattern"] = "fill"
            print(f"  fill {g} {zone_kind}: {fz.area / 1e4:.1f} ha, target {n}, darts {len(pts)}, placed {placed}")
    print(f"fill: {len(planter.plants) - n_before} plants")

    # 4. write
    feats, area_meta = [], []
    for a in areas:
        if not a.get("placed"):
            continue
        sid, spk, form, place, is_av, hall_id = a["key"]
        sp, rs = a["sp"], a["rows"]
        fill = a.get("fill")
        if fill:
            conf_t = conf_e = "C"
            srcs = ["S08", "S157", "S240"] if fill == "hill" else (["S08", "S1160"] if fill == "land" else ["S08"])
            note = FILL_BASIS[fill]
            gr = a.get("garden_rows") or []
            if gr:
                note += ". Garden-wide statements of what grew (not where): " + "; ".join(dict.fromkeys(f"{r['plant_zh']} ({r['id']}, {r['confidence']})" for r in gr))[:300]
                srcs = sorted(set(srcs) | {x for r in gr for x in r["sources"].split(";") if x})
            gen = "extent, species and places"
            assumed = True
        else:
            conf_t = min((r["confidence"] for r in rs), key=lambda g: GRADE[g])
            leafish = any(r["source_kind"] in ("leaf", "survivor") for r in rs)
            conf_e = "B" if leafish and place != "scene" and not a["fell"] else "C"
            srcs = sorted({s for r in rs for s in r["sources"].split(";") if s})
            note = "; ".join(dict.fromkeys(r["place_text"] for r in rs if r["place_text"]))[:400]
            if a["fell"]:
                note = ("the place named had no free land or water here: placed in the scene. " + note)[:400]
            gen = "places" if conf_e == "B" else "extent and places"
            assumed = False
        n = a["placed"]
        kind = "grove" if fill else KIND.get(form) or ("avenue" if a.get("pattern") == "avenue" else "specimen_tree" if a.get("pattern") in ("pair", "single") or (rs and rs[0]["role"] == "specimen" and n <= 6) else "grove")
        dens = n / max(a["geom"].area, 1) * 1e4
        props = {"id": f"GA-{a['idx'] + 1:04d}", "scene": sid, "kind": kind, "species": spk, "latin": sp["latin"] if not fill else "", "form": form, "place": place,
                 "pattern": a.get("pattern"), "count": n, "density": round(dens, 1), "height_m": round(sp["h"] if not (rs and rs[0].get("height_m")) else float(rs[0]["height_m"]), 1),
                 "season": "; ".join(sorted({r["season"] for r in rs if r["season"]})) if rs else "", "extent_confidence": conf_e, "trees_confidence": conf_t,
                 "assumed": assumed, "generated": gen, "rows": ";".join(r["id"] for r in (rs or a.get("garden_rows") or [])), "sources": ";".join(srcs), "hall": a.get("hall", ""), "note": note}
        geo = geo_of(a["geom"], 1.5 if fill else 0.8)
        if geo is None:
            continue
        a["props"] = props
        feats.append({"type": "Feature", "properties": props, "geometry": geo})
        area_meta.append([props["id"], sid, kind, spk, conf_e, conf_t, int(assumed)])
    # area index in the binary is the position in area_meta
    pos_of = {}
    for i, a in enumerate([a for a in areas if a.get("props")]):
        pos_of[a["idx"]] = i
    rock_out = []
    for k, r in enumerate([r for r in rockeries if r["placed"]]):
        rid = f"GR-{k + 1:03d}"
        r["id"] = rid
        item_ids = [x["id"] if t == "row" else x["reading"] for t, x in r["items"]]
        where = "; ".join(dict.fromkeys((x.get("place_text") or x.get("where") or "") for t, x in r["items"]))[:300]
        props = {"id": rid, "scene": r["scene"], "kind": "rockery", "rock": r["kind"], "base_m": round(r["base"] + DATUM_M, 2), "top_m": round(r["top"] + DATUM_M, 2),
                 "height_m": round(r["h_above"], 1), "extent_confidence": r["extent_confidence"], "trees_confidence": "", "confidence": r["confidence"], "assumed": False,
                 "generated": "the footprint and its place: the size is typology", "rows": ";".join(item_ids), "sources": ";".join(r["sources"]), "hall": r["hall"], "note": where}
        feats.append({"type": "Feature", "properties": props, "geometry": geo_of(r["fp"], 0.15)})
        ring = [[round((x - dx0) * 10), round((z - dz0) * 10)] for x, z in r["fp"].exterior.coords[:-1]]
        rock_out.append({"id": rid, "scene": r["scene"], "k": r["kind"], "ring": ring, "y0": round(r["base"] * 100), "y1": round(r["top"] * 100), "g": r["confidence"], "ge": r["extent_confidence"], "s": rid and seed_of(rid) % 10000})
    fc = {"type": "FeatureCollection", "name": "greens_1860", "credit": CREDIT, "features": feats}
    text = json.dumps(fc, ensure_ascii=False, separators=(",", ":")) + "\n"
    OUT_LAYER.write_text(text, encoding="utf-8")
    PUB_LAYER.write_text(text, encoding="utf-8")

    # the binary: 14 bytes a plant
    rec = np.zeros(len(planter.plants), dtype=[("x", "<u2"), ("z", "<u2"), ("y", "<i2"), ("area", "<u2"), ("sp", "u1"), ("h", "u1"), ("c", "u1"), ("f", "u1"), ("lift", "u1"), ("pad", "u1")])
    by_idx = {a["idx"]: a for a in areas}
    kept = [p for p in planter.plants if p["area"] in pos_of]
    rec = rec[: len(kept)]
    for i, p in enumerate(kept):
        a = by_idx[p["area"]]
        pr = a["props"]
        flags = (1 if pr["assumed"] else 0) | (GRADE[pr["trees_confidence"]] << 1) | (GRADE[pr["extent_confidence"]] << 3) | ((1 if p["lift"] > 0.05 else 0) << 5) | ((1 if p["form"] in WATER_FORMS else 0) << 6)
        rec[i] = (round((p["x"] - dx0) * 10), round((p["z"] - dz0) * 10), round(p["y"] * 100), pos_of[p["area"]], p["sp"], min(round(p["h"] * 10), 255), min(round(p["c"] * 10), 255), flags, min(round(p["lift"] * 10), 255), 0)
    rec.tofile(OUT_BIN)
    sp_list = sorted(species.values(), key=lambda s: s["i"])
    out = {"name": "greens_1860", "credit": CREDIT,
           "note": "Round 12 (scripts/greens1860.py). generated/greens_1860.bin: 14 bytes a plant: x, z uint16 in dm from the ground's domain corner; y int16 cm above the datum (the walk surface, or the water's level for lotus and reeds); area uint16 (an index into `areas`); species uint8 (into `species`); height, crown uint8 in dm; flags uint8 (1 assumed, 2-4 trees grade A0 B1 C2, 8-16 extent grade, 32 on a generated hill, 64 on the water); lift uint8 in dm (what the generated hills add there); a pad byte. rocks: ring in dm from the corner, y0 base and y1 top in cm.",
           "record_bytes": 14, "count": len(kept), "domain": [dx0, dz0], "datum_m": DATUM_M, "trunk_sink_m": TRUNK_SINK_M,
           "species": [{k: s[k] for k in ("key", "form", "h", "c", "bloom", "autumn", "latin", "en")} for s in sp_list],
           "areas": area_meta, "rocks": rock_out}
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

    # report
    forms = Counter(sp_list[p["sp"]]["form"] for p in kept)
    rep = {"rows": len(all_rows), "kept": len(keep), "drawn_rows": len(planted), "rock_rows": len(rocks_rows),
           "areas": len(area_meta), "areas_by_kind": dict(Counter(f["properties"]["kind"] for f in feats)),
           "areas_sourced": sum(1 for a in area_meta if not a[6]), "areas_fill": sum(1 for a in area_meta if a[6]),
           "plants": len(kept), "by_form": dict(forms), "assumed_plants": int(sum(1 for p in kept if by_idx[p["area"]]["props"]["assumed"])),
           "rockeries": len(rock_out), "rockeries_unplaced": [(r["scene"], r["kind"], len(r["items"])) for r in rockeries if not r["placed"]],
           "areas_skipped": [(a["key"][0], a["key"][1], a["key"][3], a["skip"]) for a in areas if a.get("skip")],
           "areas_empty": [(a["key"][0], a["key"][1], a["key"][3]) for a in areas if a.get("geom") is not None and not a.get("placed") and not a.get("fill")],
           "files_mb": {"layer": round(PUB_LAYER.stat().st_size / 1e6, 2), "json": round(OUT_JSON.stat().st_size / 1e6, 2), "bin": round(OUT_BIN.stat().st_size / 1e6, 2)}}
    REPORT.write_text(json.dumps(rep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(kept)} plants ({dict(forms)}); assumed {rep['assumed_plants']}; areas {len(area_meta)} (sourced {rep['areas_sourced']}, fill {rep['areas_fill']}); rockeries {len(rock_out)}; "
          f"skipped {len(rep['areas_skipped'])}, empty {len(rep['areas_empty'])}; files {rep['files_mb']}")


if __name__ == "__main__":
    import shapely.affinity  # noqa: F401
    import shapely.ops  # noqa: F401

    main()
