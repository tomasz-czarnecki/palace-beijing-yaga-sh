"""Fetch OpenStreetMap features around Yuanmingyuan and save them as GeoJSON (ODbL, (c) OpenStreetMap contributors).

Writes research/raw/osm/overpass.json (the raw answer) and research/layers/osm_today.geojson.
Round 20: `--ring` asks for the surroundings (RING_BBOX, no buildings, no minor streets) and writes research/raw/osm/overpass_ring.json and research/layers/osm_ring_today.geojson: today's water, canals, main roads, parks, places and names, the reference for the layer surroundings_1860.
"""

import sys

import json
import time
from collections import Counter
from datetime import date
from pathlib import Path

import requests

URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
BBOX = (39.985, 116.280, 40.025, 116.325)  # south, west, north, east: the three gardens with a margin
RAW = Path("research/raw/osm/overpass.json")
OUT = Path("research/layers/osm_today.geojson")
UA = "palace-beijing-yaga-sh research bot"
RING_BBOX = (39.972, 116.232, 40.035, 116.345)  # the ring about 2 km beyond the walls, west to 玉泉山 (Round 20)
RING_RAW = Path("research/raw/osm/overpass_ring.json")
RING_OUT = Path("research/layers/osm_ring_today.geojson")
RING_QUERY = """
[out:json][timeout:180];
(
  way["natural"="water"]({b});
  relation["natural"="water"]({b});
  way["waterway"]({b});
  way["landuse"="reservoir"]({b});
  way["natural"~"^(hill|ridge|wood|scrub)$"]({b});
  node["natural"~"^(peak|hill|spring)$"]({b});
  way["historic"]({b});
  node["historic"]({b});
  relation["historic"]({b});
  way["leisure"="park"]({b});
  relation["leisure"="park"]({b});
  relation["boundary"="protected_area"]({b});
  way["boundary"="protected_area"]({b});
  way["amenity"~"^(place_of_worship|university)$"]({b});
  node["amenity"="place_of_worship"]({b});
  way["landuse"~"^(farmland|orchard|meadow)$"]({b});
  way["highway"~"^(motorway|trunk|primary|secondary|tertiary|unclassified)$"]({b});
  node["place"]({b});
  way["place"]({b});
  way["bridge"]["name"]({b});
  node[~"^name$"~"(旗|营|村|庄|屯|寺|庙|闸|桥|园|坊|厂)"]({b});
  way["name"~"(旗|营|闸|园|寺|庙)"]({b});
);
out geom;
"""

QUERY = """
[out:json][timeout:120];
(
  way["natural"="water"]({b});
  relation["natural"="water"]({b});
  way["water"]({b});
  way["waterway"]({b});
  way["landuse"="reservoir"]({b});
  way["place"="islet"]({b});
  way["place"="island"]({b});
  way["natural"="hill"]({b});
  node["natural"="peak"]({b});
  way["historic"]({b});
  node["historic"]({b});
  relation["historic"]({b});
  way["ruins"]({b});
  way["building"="ruins"]({b});
  way["leisure"="park"]({b});
  relation["leisure"="park"]({b});
  way["tourism"]({b});
  node["tourism"]({b});
  relation["boundary"="protected_area"]({b});
  way["barrier"="wall"]({b});
  way["barrier"="city_wall"]({b});
  way["man_made"="bridge"]({b});
  way["bridge"]({b});
  way["highway"]({b});
  node["barrier"="gate"]({b});
  node["entrance"]({b});
  way["building"]({b});
);
out geom;
"""


def fetch(query=QUERY, bbox=BBOX) -> dict:
    """Run the Overpass query on the first mirror that answers."""
    body = {"data": query.format(b=",".join(map(str, bbox)))}
    for url in URLS:
        print("asking", url)
        try:
            r = requests.post(url, data=body, headers={"User-Agent": UA}, timeout=200)
            if r.status_code == 200:
                return r.json() | {"_mirror": url, "_date": date.today().isoformat()}
            print(" status", r.status_code)
        except requests.RequestException as e:
            print(" failed", e)
        time.sleep(5)
    raise SystemExit("no Overpass mirror answered")


def to_feature(el: dict) -> dict | None:
    """Convert one OSM element to a GeoJSON feature; relations become MultiPolygon-less line bags."""
    tags = el.get("tags", {})
    props = {"id": f"osm-{el['type']}-{el['id']}", "sources": "S_OSM", "confidence": "B", "note": "today's state", **tags}
    if el["type"] == "node":
        geom = {"type": "Point", "coordinates": [el["lon"], el["lat"]]}
    elif el["type"] == "way":
        coords = [[p["lon"], p["lat"]] for p in el.get("geometry", [])]
        if len(coords) < 2:
            return None
        closed = len(coords) > 3 and coords[0] == coords[-1]
        if closed and not {"highway", "barrier", "waterway"} & tags.keys():
            geom = {"type": "Polygon", "coordinates": [coords]}
        else:
            geom = {"type": "LineString", "coordinates": coords}
    else:
        lines = [[[p["lon"], p["lat"]] for p in m.get("geometry", [])] for m in el.get("members", []) if m["type"] == "way"]
        lines = [ln for ln in lines if len(ln) > 1]
        if not lines:
            return None
        props["roles"] = [m.get("role", "") for m in el.get("members", []) if m["type"] == "way" and m.get("geometry")]
        geom = {"type": "MultiLineString", "coordinates": lines}
    return {"type": "Feature", "properties": props, "geometry": geom}


def main() -> None:
    global RAW, OUT
    if "--ring" in sys.argv:
        RAW, OUT = RING_RAW, RING_OUT
    RAW.parent.mkdir(parents=True, exist_ok=True)
    if RAW.exists():
        data = json.loads(RAW.read_text())
    else:
        data = fetch(RING_QUERY, RING_BBOX) if RAW == RING_RAW else fetch()
        RAW.write_text(json.dumps(data, ensure_ascii=False))
    feats = [f for f in map(to_feature, data["elements"]) if f]
    OUT.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "attribution": "(c) OpenStreetMap contributors, ODbL",
                "fetched": data.get("_date"),
                "features": feats,
            },
            ensure_ascii=False,
        )
    )
    c = Counter(f["geometry"]["type"] for f in feats)
    print(len(data["elements"]), "elements,", len(feats), "features", dict(c))


if __name__ == "__main__":
    main()
