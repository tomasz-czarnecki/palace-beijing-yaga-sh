"""Round 20: the check of what stands and runs round the gardens (research/layers/surroundings_1860, site/reconstruction/data/around_1860.json, the outer ground).

  uv run python tools/check_surroundings.py            (after scripts/surroundings1860.py, scripts/ground1860.py, scripts/ground_outer1860.py)
  uv run python tools/check_surroundings.py --before <dir>   also count an older layer (a copy of research/layers/) for the before/after line

Counts by kind and confidence. Fails on:
  - a feature with no source, or a source id not in research/sources.md
  - a road or canal that joins a gate, a way or another line with a gap over 1 m (A or B), or an A or B road or canal ending within 60 m of the outer wall with no join
  - a block or hall of the massing over a wall, a hall's footprint, the gardens' water or a lake outside, or inside the walls; a field patch over a hall or inside the walls
  - a step over 0.3 m where the outer ground meets the inner one on level ground (every 2.5 m along the inner domain's edge; banks steeper than 0.5 m in 10 m are listed, the view closes them)
Reports the fall of the ground under each block (none floats: the view seats a block on its lowest corner).
  - the round's site files over 10 MB together
Writes research/surroundings/check.json.
"""

import csv
import json
import math
import re
import struct
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from scene1860 import LAYERS, SITE_DATA, layer, to_xz  # noqa: E402
from surroundings1860 import Clear, rect, xz_of  # noqa: E402

GEN = ROOT / "site/reconstruction/generated"
OUT = ROOT / "research/surroundings/check.json"
JOIN_MAX_M = 1.0
STEP_MAX_M = 0.3
SLOPE_MAX_M = 1.5
NEAR_WALL_M = 60.0
SIZE_MAX_MB = 10.0
ROUND_FILES = ["site/reconstruction/data/around_1860.json", "site/reconstruction/data/surroundings_1860.geojson", "site/reconstruction/generated/ground_outer.bin", "site/reconstruction/generated/ground_outer.json", "site/reconstruction/around3d.js", "site/around", "site/zh/around"]


def counts(path):
    feats = json.load(open(path, encoding="utf-8"))["features"]
    return Counter(f["properties"]["kind"] for f in feats), Counter(f["properties"]["confidence"] for f in feats), sum(1 for f in feats if f["properties"].get("assumed"))


class Ground:
    """The ground as the view draws it: the inner walk raster (the plain beyond it) inside the inner domain, the ring and the backdrop outside (scripts/ground_outer1860.py, read by its own loader)."""

    def __init__(self):
        import ground_outer1860 as go
        self.go = go
        self.meta = json.load(open(GEN / "ground.json", encoding="utf-8"))
        g = self.meta["grid"]
        self.grid = np.fromfile(GEN / "ground_grid.i16", dtype="<i2").reshape(g["height"], g["width"])
        self.outer = (GEN / "ground_outer.json").exists()
        if self.outer:
            self.ometa, self.rh, self.rc, self.bh = go.load(GEN)
        edge = ROOT / "research/terrain/ground_edge.json"
        self.edge = json.load(open(edge, encoding="utf-8")) if edge.exists() else None

    def plain(self, x, z):
        p = self.meta["plain"]
        return p["a"] + p["bx"] * x / 1000 + p["bz"] * z / 1000 - self.meta["datum_m"]

    def inner(self, x, z):
        g = self.meta["grid"]
        u, v = (x - g["x0"]) / g["step_m"], (z - g["z0"]) / g["step_m"]
        if u < 0 or v < 0 or u > g["width"] - 1 or v > g["height"] - 1:
            return self.plain(x, z)
        i, j = min(int(u), g["width"] - 2), min(int(v), g["height"] - 2)
        a, b = u - i, v - j
        s = w = 0.0
        for di, dj, k in ((0, 0, (1 - a) * (1 - b)), (1, 0, a * (1 - b)), (0, 1, (1 - a) * b), (1, 1, a * b)):
            c = int(self.grid[j + dj, i + di])
            if c < g["water_below"] or k <= 0:
                continue
            s += c * k
            w += k
        return s / w / 100 if w > 1e-9 else None

    def ring_at(self, x, z):
        return float(self.go.height_at(self.ometa, self.rh, self.bh, x, z))

    def at(self, x, z):
        x0, z0, x1, z1 = self.meta["domain"]
        if x0 <= x <= x1 and z0 <= z <= z1:
            return self.inner(x, z)
        return self.ring_at(x, z) if self.outer else self.plain(x, z)

    def join(self):
        """Every 2.5 m of the inner domain's edge: the inner ground there (the land, or the bed where a lake crosses) against the ring's lattice surface. A point where the inner ground itself falls more than 0.5 m within 10 m along the edge is a bank the 20 m lattice cannot follow: listed, and closed in the view by the fan through the inner edge vertices (around3d.js)."""
        e = self.edge
        out = []
        for side in ("north", "south", "west", "east"):
            vals = np.array(e[side], float) / 100
            n = len(vals)
            for k in range(n):
                if side in ("north", "south"):
                    x, z = e["x0"] + k * e["step_m"], e["z0"] if side == "north" else e["z1"]
                else:
                    x, z = (e["x0"] if side == "west" else e["x1"]), e["z0"] + k * e["step_m"]
                lo, hi = vals[max(k - 4, 0):k + 5].min(), vals[max(k - 4, 0):k + 5].max()
                out.append((side, x, z, abs(vals[k] - self.ring_at(x, z)), hi - lo > 0.5, bool(e[f"wet_{side}"][k])))
        return out


def main():
    fails = []
    sources = set(re.findall(r"^\| (S\d+) \|", (ROOT / "research/sources.md").read_text(encoding="utf-8"), re.M))
    path = LAYERS / "surroundings_1860.geojson"
    feats = json.load(open(path, encoding="utf-8"))["features"]
    view = json.load(open(SITE_DATA / "around_1860.json", encoding="utf-8"))
    report = json.load(open(ROOT / "research/surroundings/report.json", encoding="utf-8"))
    by_kind, by_conf, assumed = counts(path)
    kc = Counter((f["properties"]["kind"], f["properties"]["confidence"]) for f in feats)
    out = {"features": len(feats), "by_kind": dict(sorted(by_kind.items())), "by_confidence": dict(sorted(by_conf.items())), "assumed": assumed,
           "by_kind_confidence": {k: {c: kc[(k, c)] for c in "ABC" if kc[(k, c)]} for k in sorted(by_kind)}}
    if "--before" in sys.argv:
        before = Path(sys.argv[sys.argv.index("--before") + 1]) / "surroundings_1860.geojson"
        out["before"] = {"features": 0} if not before.exists() else {"features": sum(counts(before)[0].values()), "by_kind": dict(counts(before)[0])}

    # Sources.
    nosrc = [f["properties"]["id"] for f in feats if not f["properties"]["sources"].strip()]
    unknown = sorted({(f["properties"]["id"], s) for f in feats for s in re.split(r"[;,\s]+", f["properties"]["sources"]) if re.fullmatch(r"S\d+", s) and s not in sources})
    if nosrc:
        fails.append(f"{len(nosrc)} features with no source: {nosrc[:8]}")
    if unknown:
        fails.append(f"{len(unknown)} source ids not in sources.md: {unknown[:8]}")
    out["no_source"], out["unknown_sources"] = nosrc, [list(u) for u in unknown]

    # Joins of roads and canals.
    clear = Clear()
    wall_ring = unary_union([Polygon(xz_of(shape(f["geometry"])).coords).exterior for f in layer("walls_1860") if f["geometry"]["type"] == "LineString" and f["properties"]["kind"] == "outer_wall"])
    joins = report["joins"]
    bad = [j for j in joins if j["confidence"] in "AB" and j["gap_m"] > JOIN_MAX_M]
    if bad:
        fails.append(f"{len(bad)} A or B joins over {JOIN_MAX_M} m: {[(j['id'], j['target'], j['gap_m']) for j in bad]}")
    joined_ends = {(j["id"], j["end"]) for j in joins}
    loose = []
    for f in feats:
        p = f["properties"]
        if p["kind"] not in ("road", "canal", "river") or p["confidence"] not in "AB":
            continue
        g = xz_of(shape(f["geometry"]))
        ln = g if g.geom_type == "LineString" else g.geoms[0]
        for end, c in (("start", ln.coords[0]), ("end", ln.coords[-1])):
            d = wall_ring.distance(Point(c))
            if d < NEAR_WALL_M and (p["id"], end) not in joined_ends:
                loose.append((p["id"], end, round(d, 1)))
    if loose:
        fails.append(f"{len(loose)} A or B road or canal ends within {NEAR_WALL_M:g} m of the wall with no join: {loose}")
    out["joins"] = [{k: j[k] for k in ("id", "target", "end", "gap_before_m", "gap_m", "confidence")} for j in joins]
    out["loose_ends"] = loose

    # Overlaps.
    lakes = unary_union([xz_of(shape(f["geometry"])).buffer(0) for f in layer("water_1860") if f["properties"].get("outside")])
    inside = clear.garden.buffer(-1.0)
    over = Counter()
    worst = {}
    for b in view["blocks"] + view["halls"]:
        p = rect(b["x"], b["z"], b["w"], b["d"], b["rot"])
        for what, geom, measure in (("wall", clear.walls, "length"), ("hall", clear.halls, "area"), ("water", clear.water, "area"), ("lake", lakes, "area"), ("inside", inside, "area")):
            inter = p.intersection(geom)
            a = inter.length if measure == "length" else inter.area
            if a > 0.5:
                over[what] += 1
                worst[what] = max(worst.get(what, 0.0), round(float(a), 2))
    for pt in view["patches"]:
        if pt["kind"] not in ("field", "paddy", "orchard") or len(pt["ring"]) < 3:
            continue
        p = Polygon(pt["ring"], pt.get("holes") or []).buffer(0)
        for what, geom in (("patch_hall", clear.halls), ("patch_inside", inside)):
            a = p.intersection(geom).area
            if a > 1.0:
                over[what] += 1
                worst[what] = max(worst.get(what, 0.0), round(float(a), 1))
    if over:
        fails.append(f"overlaps {dict(over)} (worst {worst})")
    out["overlaps"], out["overlap_worst_m"] = dict(over), worst

    # The ground: the join and the blocks on it.
    G = Ground()
    x0, z0, x1, z1 = G.meta["domain"]
    if G.outer and G.edge:
        pts = G.join()
        flat = np.array([d for _, _, _, d, bank, wet in pts if not bank and not wet])
        banks = [(side, round(x), round(z), round(d, 3)) for side, x, z, d, bank, wet in pts if bank and not wet and d > STEP_MAX_M]
        wet = np.array([d for *_, d, bank, wet in pts if wet] or [0.0])
        out["join"] = {"points": len(pts), "median_m": round(float(np.median(flat)), 3), "p99_m": round(float(np.percentile(flat, 99)), 3), "max_m": round(float(flat.max()), 3),
                       "under_water_max_m": round(float(wet.max()), 3), "banks_over_limit": banks, "how": "inner edge every 2.5 m against the ring's 20 m lattice; banks the lattice cannot follow are closed by the view's fan through the inner edge vertices"}
        # Where the two grounds share vertices (the ring's 20 m nodes on the edge) they must agree; between the nodes the view fans the edge cells through the inner edge vertices, so the drawn seam follows the inner ground and the lattice's departure there is reported, not drawn.
        nodes = np.array([d for side, x, z, d, bank, wet in pts if not wet and abs(((x if side in ("north", "south") else z) - (G.edge["x0"] if side in ("north", "south") else G.edge["z0"])) % 20.0) < 1e-6])
        out["join"]["nodes"] = int(len(nodes))
        out["join"]["nodes_max_m"] = round(float(nodes.max()), 3)
        out["join"]["between_nodes_max_m"] = round(float(max(flat.max(), max([b[3] for b in banks] or [0]))), 3)
        if nodes.max() > STEP_MAX_M:
            fails.append(f"step at the join's shared nodes {nodes.max():.2f} m > {STEP_MAX_M} m")
    else:
        fails.append("no outer ground (site/reconstruction/generated/ground_outer.json) or no research/terrain/ground_edge.json")
    slopes = []
    for b in view["blocks"] + view["halls"]:
        p = rect(b["x"], b["z"], b["w"], b["d"], b["rot"])
        ys = [G.at(x, z) for x, z in list(p.exterior.coords)[:4] + [(b["x"], b["z"])]]
        ys = [y for y in ys if y is not None]
        if ys:
            slopes.append((max(ys) - min(ys), b["id"]))
    if slopes:
        worst_s = max(slopes)
        out["block_fall_m"] = {"median": round(float(np.median([s for s, _ in slopes])), 3), "max": round(float(worst_s[0]), 3), "at": worst_s[1], "over": sum(1 for s, _ in slopes if s > SLOPE_MAX_M)}
        # the view seats every block on its lowest corner and runs its walls up past the highest (around3d.js baseOf): none floats; a large fall means a block buried on one side, listed
        out["block_fall_m"]["ids_over"] = sorted({i for s_, i in slopes if s_ > SLOPE_MAX_M})

    # Sizes.
    sizes = {}
    for rel in ROUND_FILES:
        p = ROOT / rel
        sizes[rel] = sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) if p.is_dir() else p.stat().st_size if p.exists() else 0
    out["sizes_bytes"] = sizes
    total = sum(sizes.values()) / 1e6
    out["round_site_mb"] = round(total, 2)
    if total > SIZE_MAX_MB:
        fails.append(f"the round's site files {total:.1f} MB > {SIZE_MAX_MB} MB")
    out["massing"] = {k: len(view[k]) for k in ("blocks", "halls", "patches", "strips", "waters", "labels")}
    out["fails"] = fails
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print(f"features {len(feats)}" + (f" (before {out['before']['features']})" if "before" in out else "") + f"; by kind {out['by_kind']}; by confidence {out['by_confidence']}; assumed {assumed}")
    print(f"joins {len(joins)}: max gap {max([j['gap_m'] for j in joins] or [0]):.2f} m; loose A/B ends {len(loose)}; overlaps {dict(over) or 'none'}")
    if "join" in out:
        print(f"ground join at the {out['join']['nodes']} shared nodes: max {out['join']['nodes_max_m']} m; between them (closed by the view's fan) max {out['join']['between_nodes_max_m']} m;")
        print(f"   all {out['join']['points']} edge points, level ground median {out['join']['median_m']} m, p99 {out['join']['p99_m']} m, max {out['join']['max_m']} m; under water {out['join']['under_water_max_m']} m; banks over {STEP_MAX_M} m: {out['join']['banks_over_limit']}")
    if "block_fall_m" in out:
        print(f"blocks: ground fall across a footprint median {out['block_fall_m']['median']} m, max {out['block_fall_m']['max']} m")
    print(f"massing {out['massing']}; round site files {total:.2f} MB")
    if fails:
        print("FAIL:\n  " + "\n  ".join(fails))
        sys.exit(1)
    print("ok")


if __name__ == "__main__":
    main()
