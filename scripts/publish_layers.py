"""Public copies of the working layers: research/layers/*.geojson -> site/reconstruction/data/, in the Küstrin pattern.

  uv run python scripts/publish_layers.py

Geometry traced from S01 is public with credit (research/README.md "Public and private"). What is dropped: the plan readers' working fields (plan pixels, block and region numbers).
The plan image and the overlay never pass through here. Also writes buildings_1860 (one point per row of buildings.csv with a position) and labels_1860 (names for the 3D view).
"""

import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scene1860 import LAYERS, ROOT, SITE_DATA  # noqa: E402

S01_CREDIT = "Traced from S01, plan of the Yuanmingyuan, image courtesy of the Princeton University Art Museum"
OSM_CREDIT = "© OpenStreetMap contributors, ODbL"
DROP = {"region_id", "block", "source_kind", "ncols", "nrows", "drawn_m", "height_method"}
KEEP_OSM_TAGS = ("name", "name:en", "historic", "ruins", "natural", "waterway", "tourism", "leisure")
ROUND = 7


def rounded(c):
    if isinstance(c[0], (int, float)):
        return [round(v, ROUND) for v in c]
    return [rounded(v) for v in c]


def write(name, features, credit, **extra):
    fc = {"type": "FeatureCollection", "name": name, "credit": credit, **extra, "features": features}
    path = SITE_DATA / f"{name}.geojson"
    path.write_text(json.dumps(fc, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return path.stat().st_size


def layer_1860(name):
    features = []
    for f in json.load(open(LAYERS / f"{name}.geojson", encoding="utf-8"))["features"]:
        props = {k: v for k, v in f["properties"].items() if k not in DROP}
        if props.get("note"):  # no paths of the research folder on the site
            props["note"] = re.sub(r"[;,]?\s*research/[\w./-]+", "", props["note"]).strip()
        features.append({"type": "Feature", "geometry": {"type": f["geometry"]["type"], "coordinates": rounded(f["geometry"]["coordinates"])}, "properties": props})
    return features


def osm_today():
    """Today's park, for orientation: water, ruins and named places, and the park's paths. Buildings of the city round it and most tags stay out."""
    features = []
    for f in json.load(open(LAYERS / "osm_today.geojson", encoding="utf-8"))["features"]:
        p = f["properties"]
        kind = "water" if p.get("natural") == "water" or p.get("waterway") else "ruin" if p.get("historic") or p.get("ruins") else "path" if p.get("highway") in ("footway", "path", "pedestrian", "cycleway", "steps") else "named" if p.get("name") and f["geometry"]["type"] == "Point" else None
        if not kind:
            continue
        props = {"id": p["id"], "kind": kind, "sources": "S03", "confidence": "B", "note": "today's state"}
        props.update({k: p[k] for k in KEEP_OSM_TAGS if p.get(k)})
        features.append({"type": "Feature", "geometry": {"type": f["geometry"]["type"], "coordinates": rounded(f["geometry"]["coordinates"])}, "properties": props})
    return features


def building_points(rows):
    out = []
    for r in rows:
        if not r["lat"]:
            continue
        props = {k: r[k] for k in ("id", "parent_id", "name_zh", "name_pinyin", "name_en", "name_on_plan", "garden", "type", "built", "sources", "confidence", "pos_confidence")}
        out.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [round(float(r["lon"]), ROUND), round(float(r["lat"]), ROUND)]}, "properties": props})
    return out


def labels(rows):
    """Rank 1: the three gardens and the Xiyang Lou. Rank 2: the Forty Scenes and the European palaces, the named compounds of the other gardens as the plan reads them."""
    out = [{"zh": "圆明园", "en": "Yuanming Yuan", "lon": 116.2935, "lat": 40.0090, "rank": 1},
           {"zh": "长春园", "en": "Changchun Yuan", "lon": 116.3088, "lat": 40.0090, "rank": 1},
           {"zh": "绮春园", "en": "Qichun Yuan", "lon": 116.3035, "lat": 39.9985, "rank": 1},
           {"zh": "西洋楼", "en": "Xiyang Lou", "lon": 116.3050, "lat": 40.0128, "rank": 1}]
    for r in rows:
        if r["parent_id"] or not r["lat"] or not r["name_zh"] or "?" in r["name_zh"] or r["read"] == "guess":
            continue
        n = r["id"][2:]
        major = (r["id"].startswith("YM") and n.isdigit() and int(n) <= 40) or r["id"].startswith("XY") or (r["id"][:2] in ("CC", "QC") and r["read"] == "sure" and r["type"] in ("scene", "compound", "temple") and int(n) < 22)
        if major and r["id"] not in ("YM54", "YM55"):
            out.append({"id": r["id"], "zh": r["name_zh"], "en": r["name_pinyin"], "lon": round(float(r["lon"]), 6), "lat": round(float(r["lat"]), 6), "rank": 2})
    return out


def main():
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    sizes = {}
    for name in ("walls_1860", "water_1860", "islands_1860", "hills_1860", "bridges_1860", "scenes_1860", "footprints_1860", "fields_1860"):
        sizes[name] = write(name, layer_1860(name), S01_CREDIT)
    sizes["osm_today"] = write("osm_today", osm_today(), OSM_CREDIT)
    rows = list(csv.DictReader(open(ROOT / "research/buildings.csv", encoding="utf-8", newline="")))
    sizes["buildings_1860"] = write("buildings_1860", building_points(rows), S01_CREDIT + "; names from the texts, research/sources.md")
    labs = labels(rows)
    (SITE_DATA / "labels_1860.json").write_text(json.dumps(labs, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print({k: f"{v / 1e3:.0f} kB" for k, v in sizes.items()}, f"; {len(labs)} labels")


if __name__ == "__main__":
    main()
