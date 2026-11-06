"""The planting check (Round 12): counts of the areas and plants by kind, grade and species, and how every plant and rockery meets the halls, the ways, the water and the ground.

  uv run python tools/check_greens.py              the files as they are (data/greens_1860.json, generated/greens_1860.bin, layers/greens_1860); exits non-zero on a failure
  uv run python tools/check_greens.py --browser    first measures the view in a headless browser (software WebGL): frame times and triangles with the planting off
                                                   and on, at three views and four seasons; writes research/greens/greens_browser.json

Measured against the surface the view walks on (site/reconstruction/generated/ground_grid.i16, ground3d.js groundAt), the boxes (data/halls_1860.geojson),
the ways (data/paths_1860.geojson, strips of their width), the walls and bridges (generated/structures.json) and the water (the lattice's water cells).
Fails: a plant inside a box, or whose crown reaches over one; a land plant on a way's strip, on a wall or a bridge deck, in water, or inside a rockery;
a lotus, floating leaf or reed on land; a plant's base off the ground (or off its water's level) by more than BASE_TOL_M; the ground under a trunk lower
than its base by more than the trunk's sink; a rockery whose base stands above the ground or bed under it, or that stands in a box; a shore rockery that
does not reach the water; generated data over MAX_MB; a browser report older than the data (when one exists).
The browser run needs Node and Playwright outside the repo (NODE_PATH, default /opt/data/cache/scratch/palace_r11_kit_tools/node_modules) and a Chrome (CHROME_PATH).
"""

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, shape
from shapely.ops import unary_union
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from scene1860 import DATUM_M, GENERATED, SITE_DATA, Grid, to_xz  # noqa: E402

OUT = ROOT / "research/greens"
BASE_TOL_M = 0.05
MAX_MB = 4.0
PORT = 8881
WATER = {"lotus", "floating", "reed"}
GRADES = "ABC"

NODE = r"""
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [url, out] = process.argv.slice(2);
  const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH, args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await (await browser.newContext({ viewport: { width: 1400, height: 900 } })).newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  const t0 = Date.now();
  await page.goto(url, { waitUntil: 'load', timeout: 180000 });
  await page.waitForFunction(() => window.__ready === true, null, { timeout: 400000 });
  const res = { url, load_s: (Date.now() - t0) / 1000, views: {} };
  const views = { overview: [-100, 1100, 1700, 0, 0, -150], scene: 'YM03', near: 'YM39' };
  const runs = [['off', { greens: false }], ['summer', { greens: true, season: 'summer' }], ['spring', { greens: true, season: 'spring' }], ['autumn', { greens: true, season: 'autumn' }], ['winter', { greens: true, season: 'winter' }]];
  for (const [label, st] of runs) {
    for (const [name, v] of Object.entries(views)) {
      if (label !== 'off' && label !== 'summer' && name !== 'scene') continue;
      const m = await page.evaluate(({ v, st }) => {
        const V = window.viewer;
        Object.assign(V.state, { kit: true, assumed: true, conf: false, labels: false }, st); V.apply();
        if (Array.isArray(v)) { V.camera.position.set(v[0], v[1], v[2]); V.controls.target.set(v[3], v[4], v[5]); }
        else {
          const bs = V.boxesOf(v); let x = 0, z = 0, y = 0; for (const b of bs) { x += b.cx; z += b.cz; y += (b.y0 + b.y1) / 2; } x /= bs.length; z /= bs.length; y /= bs.length;
          const d = v === 'YM03' ? 220 : 140, el = v === 'YM03' ? 0.5 : 0.4, a = bs[0].a, t = 0.35, dx = a[0] * Math.cos(t) - a[1] * Math.sin(t), dz = a[0] * Math.sin(t) + a[1] * Math.cos(t);
          V.camera.position.set(x + dx * d * Math.cos(el), y + d * Math.sin(el), z + dz * d * Math.cos(el)); V.controls.target.set(x, y, z);
        }
        V.controls.update(); V.kit.update(V.camera, 1e9); V.greens.update(V.camera, 1e9); V.render();
        const gl = V.renderer.getContext(), times = [];
        for (let i = 0; i < 9; i++) { const a0 = performance.now(); V.render(); gl.finish(); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array(4)); times.push(performance.now() - a0); }
        times.shift(); times.sort((a, b) => a - b);
        const r = V.greens.report();
        return { frame_ms_median: Math.round(times[4] * 10) / 10, frame_ms_min: Math.round(times[0] * 10) / 10, frame_ms_max: Math.round(times[7] * 10) / 10, drawn_triangles: V.renderer.info.render.triangles, draw_calls: V.renderer.info.render.calls,
                 greens_near_instances: r.near_instances, greens_near_triangles: r.near_triangles, greens_far_triangles: r.far_triangles_all, rock_triangles: r.rock_triangles };
      }, { v, st });
      res.views[`${name}_${label}`] = m;
    }
  }
  res.report = await page.evaluate(() => { const V = window.viewer; V.state.greens = true; V.state.season = 'summer'; V.apply(); return V.greens.report(); });
  res.errors = errors;
  fs.writeFileSync(out, JSON.stringify(res));
  await browser.close();
})();
"""


def data_hash():
    return hashlib.md5((SITE_DATA / "greens_1860.json").read_bytes() + (GENERATED / "greens_1860.bin").read_bytes()).hexdigest()


def run_browser():
    scratch = Path(os.environ.get("GREENS_SCRATCH", "/opt/data/cache/scratch"))
    js = scratch / "palace_greens_check_browser.js"
    js.write_text(NODE)
    env = dict(os.environ, NODE_PATH=os.environ.get("NODE_PATH", "/opt/data/cache/scratch/palace_r11_kit_tools/node_modules"), CHROME_PATH=os.environ.get("CHROME_PATH", "/opt/hermes/tools/chromium-1208/chrome-linux64/chrome"))
    srv = subprocess.Popen([sys.executable, str(ROOT / "tools/serve_local.py"), "--port", str(PORT), "--public"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(2)
        tmp = scratch / "palace_greens_check_after.json"
        subprocess.run(["node", str(js), f"http://127.0.0.1:{PORT}/reconstruction/3d.html?shot=1", str(tmp)], env=env, check=True, timeout=3000)
        out = {"data_hash": data_hash(), "measured_utc": time.strftime("%Y-%m-%d %H:%M", time.gmtime()), **json.load(open(tmp))}
    finally:
        srv.terminate()
        srv.wait()
    (OUT / "greens_browser.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def stats(v):
    v = np.asarray(v, float)
    if not len(v):
        return "n 0"
    return f"n {len(v)}, median {np.median(v):.2f}, p90 {np.percentile(v, 90):.2f}, max {v.max():.2f} m"


def xz(geom):
    return shapely.transform(shape(geom), lambda c: np.column_stack(to_xz(c[:, 0], c[:, 1])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--browser", action="store_true")
    args = ap.parse_args()
    if args.browser:
        run_browser()
    fails = []
    meta = json.load(open(SITE_DATA / "greens_1860.json", encoding="utf-8"))
    raw = np.fromfile(GENERATED / "greens_1860.bin", dtype=[("x", "<u2"), ("z", "<u2"), ("y", "<i2"), ("area", "<u2"), ("sp", "u1"), ("h", "u1"), ("c", "u1"), ("f", "u1"), ("lift", "u1"), ("pad", "u1")])
    X0, Z0 = meta["domain"]
    x, z, y = X0 + raw["x"] / 10, Z0 + raw["z"] / 10, raw["y"] / 100
    crown, height, flags = raw["c"] / 10, raw["h"] / 10, raw["f"]
    sp = meta["species"]
    form = np.array([sp[i]["form"] for i in raw["sp"]])
    key = np.array([sp[i]["key"] for i in raw["sp"]])
    water_plant = np.isin(form, list(WATER))
    assumed = (flags & 1).astype(bool)
    tconf = np.array([GRADES[(f >> 1) & 3] for f in flags])
    econf = np.array([GRADES[(f >> 3) & 3] for f in flags])
    out = {"plants": int(len(raw)), "by_form": dict(Counter(form.tolist())), "by_species": dict(Counter(key.tolist()).most_common()), "trees_confidence": dict(Counter(tconf.tolist())),
           "extent_confidence": dict(Counter(econf.tolist())), "assumed": int(assumed.sum()), "on_generated_hills": int(((flags >> 5) & 1).sum())}
    print(f"plants {len(raw)}: by form {out['by_form']}; species grade {out['trees_confidence']}; extent grade {out['extent_confidence']}; assumed (the fill) {out['assumed']}; on generated hills {out['on_generated_hills']}")
    layer = json.load(open(SITE_DATA / "greens_1860.geojson", encoding="utf-8"))["features"]
    areas = [f["properties"] for f in layer if f["properties"]["kind"] != "rockery"]
    rocks_l = [f for f in layer if f["properties"]["kind"] == "rockery"]
    out["areas"] = {"n": len(areas), "by_kind": dict(Counter(a["kind"] for a in areas)), "extent_confidence": dict(Counter(a["extent_confidence"] for a in areas)),
                    "trees_confidence": dict(Counter(a["trees_confidence"] for a in areas)), "assumed": sum(a["assumed"] for a in areas),
                    "scenes": len({a["scene"] for a in areas if not a["scene"].startswith("GARDEN")})}
    print(f"areas {len(areas)} in {out['areas']['scenes']} scenes: by kind {out['areas']['by_kind']}; extent {out['areas']['extent_confidence']}; species {out['areas']['trees_confidence']}; assumed {out['areas']['assumed']}")
    if len(areas) != len(meta["areas"]):
        fails.append(f"the layer has {len(areas)} areas, the view's index {len(meta['areas'])}")

    G = Grid()
    halls = json.load(open(SITE_DATA / "halls_1860.geojson", encoding="utf-8"))["features"]
    boxes = [xz(f["geometry"]) for f in halls]
    btree = STRtree(boxes)
    paths = json.load(open(SITE_DATA / "paths_1860.geojson", encoding="utf-8"))["features"]
    strips = unary_union([xz(f["geometry"]).buffer((f["properties"].get("width_m") or 2) / 2, cap_style="flat") for f in paths if f["properties"]["kind"] != "boat_route"])
    st = json.load(open(GENERATED / "structures.json", encoding="utf-8"))
    walls = unary_union([LineString([(s[0], s[1]), (s[2], s[3])]) for s in st["wall"]["segments"]]).buffer(st["wall"]["thickness_m"] / 2)
    decks = unary_union([LineString([(q[0], q[2]) for q in b["pts"]]).buffer(b["width_m"] / 2) for b in st["bridges"]])
    rock_fps = [xz(f["geometry"]) for f in rocks_l]
    rocks = unary_union(rock_fps) if rock_fps else Polygon()
    for g in (strips, walls, decks, rocks):
        shapely.prepare(g)
    pts = shapely.points(np.column_stack([x, z]))
    land = ~water_plant
    in_box = np.zeros(len(raw), bool)
    over_box = np.zeros(len(raw), bool)
    over_by = []
    for i in np.where(land)[0]:
        r = crown[i] / 2
        near = btree.query(pts[i].buffer(r + 0.05))
        if not len(near):
            continue
        d = min(boxes[j].distance(pts[i]) for j in near)
        if d <= 0:
            in_box[i] = True
        elif d < r and form[i] not in ("shrub", "hedge"):
            over_box[i] = True
            over_by.append(r - d)
        elif d < 0.5:
            over_box[i] = True
            over_by.append(0.5 - d)
    on_way = land & shapely.contains(strips, pts)
    on_wall = land & shapely.contains(walls, pts)
    on_deck = land & shapely.contains(decks, pts)
    in_rock = shapely.contains(rocks, pts)
    wet, gap, slope_gap, lvl_gap = [], [], [], []
    land_in_water = np.zeros(len(raw), bool)
    water_on_land = np.zeros(len(raw), bool)
    for i in range(len(raw)):
        if water_plant[i]:
            if not G.is_water(x[i], z[i]) or G.land_at(x[i], z[i]) is not None:
                water_on_land[i] = True
            lev = G.level_at(x[i], z[i])
            lvl_gap.append(abs(y[i] - (lev if lev is not None else 0.0)))
            continue
        g = G.land_at(x[i], z[i])
        if g is None or G.is_water(x[i], z[i]):
            land_in_water[i] = True
            continue
        gap.append(abs(y[i] - g))
        rt = max(height[i] * 0.05, 0.25)
        lows = [G.land_at(x[i] + dx, z[i] + dz) for dx, dz in ((rt, 0), (-rt, 0), (0, rt), (0, -rt))]
        lows = [v for v in lows if v is not None]
        slope_gap.append(max(0.0, y[i] - min(lows)) if lows else 0.0)
    gap, slope_gap, lvl_gap = np.array(gap), np.array(slope_gap), np.array(lvl_gap)
    sink = meta["trunk_sink_m"]
    res = {"in_box": int(in_box.sum()), "crown_over_box": int(over_box.sum()), "crown_over_box_max_m": round(max(over_by), 2) if over_by else 0, "on_way": int(on_way.sum()), "on_wall": int(on_wall.sum()),
           "on_bridge": int(on_deck.sum()), "in_rockery": int(in_rock.sum()), "land_plant_in_water": int(land_in_water.sum()), "water_plant_on_land": int(water_on_land.sum()),
           "base_gap_max_m": round(float(gap.max()), 3) if len(gap) else 0, "base_gap_over_tol": int((gap > BASE_TOL_M).sum()), "trunk_slope_gap_max_m": round(float(slope_gap.max()), 2) if len(slope_gap) else 0,
           "trunk_slope_gap_over_sink": int((slope_gap > sink).sum()), "water_level_gap_max_m": round(float(lvl_gap.max()), 3) if len(lvl_gap) else 0}
    out["placement"] = res
    print(f"plants inside a box {res['in_box']}; crown over a box {res['crown_over_box']} (max {res['crown_over_box_max_m']} m); on a way {res['on_way']}; on a wall {res['on_wall']}; on a bridge {res['on_bridge']}; in a rockery {res['in_rockery']}")
    print(f"land plants in water {res['land_plant_in_water']}; lotus, floating leaves and reeds on land {res['water_plant_on_land']}")
    print(f"base against the ground: {stats(gap)}; over {BASE_TOL_M} m {res['base_gap_over_tol']}; ground under the trunk below its base: {stats(slope_gap)}, over the {sink} m sink {res['trunk_slope_gap_over_sink']}; water plants against their level: max {res['water_level_gap_max_m']} m")
    for k, label in (("in_box", "inside a box"), ("crown_over_box", "with a crown over a box"), ("on_way", "on a way"), ("on_wall", "on a wall"), ("on_bridge", "on a bridge"), ("in_rockery", "inside a rockery"),
                     ("land_plant_in_water", "land plants in water"), ("water_plant_on_land", "water plants on land"), ("base_gap_over_tol", f"bases off the ground by more than {BASE_TOL_M} m"),
                     ("trunk_slope_gap_over_sink", "trunks whose ground falls away more than their sink")):
        if res[k]:
            fails.append(f"{res[k]} plants {label}")
    if res["water_level_gap_max_m"] > BASE_TOL_M:
        fails.append(f"a water plant off its level by {res['water_level_gap_max_m']} m")

    # rockeries
    rk = []
    for f, fp in zip(rocks_l, rock_fps):
        p = f["properties"]
        xs0, zs0, xs1, zs1 = fp.bounds
        gx, gz = np.meshgrid(np.arange(xs0, xs1 + 0.5, 0.75), np.arange(zs0, zs1 + 0.5, 0.75))
        inside = shapely.contains_xy(fp, gx.ravel(), gz.ravel())
        samp = list(zip(gx.ravel()[inside], gz.ravel()[inside])) + list(fp.exterior.coords)
        lowest = min(G.at(a, b) for a, b in samp)
        base = p["base_m"] - DATUM_M
        wet_share = sum(G.is_water(a, b) for a, b in samp) / len(samp)
        hits_box = any(boxes[j].intersects(fp) for j in btree.query(fp))
        rk.append({"id": p["id"], "rock": p["rock"], "float_m": round(base - lowest, 2), "wet": round(wet_share, 2), "box": hits_box, "height_m": p["height_m"], "grade": p["confidence"], "extent": p["extent_confidence"]})
    out["rockeries"] = {"n": len(rk), "by_kind": dict(Counter(r["rock"] for r in rk)), "grade": dict(Counter(r["grade"] for r in rk)), "extent": dict(Counter(r["extent"] for r in rk)),
                        "floating": sum(r["float_m"] > 0.01 for r in rk), "in_box": sum(r["box"] for r in rk), "shore_dry": [r["id"] for r in rk if r["rock"] == "shore" and r["wet"] == 0],
                        "shore_meeting_water": sum(1 for r in rk if r["rock"] == "shore" and r["wet"] > 0), "height_m": stats([r["height_m"] for r in rk])}
    R = out["rockeries"]
    print(f"rockeries {R['n']}: by kind {R['by_kind']}; grade {R['grade']}; extent {R['extent']}; base above the ground or bed {R['floating']}; in a box {R['in_box']}; shore rockwork meeting the water {R['shore_meeting_water']}, dry {len(R['shore_dry'])}; height above the ground {R['height_m']}")
    if R["floating"]:
        fails.append(f"{R['floating']} rockeries float")
    if R["in_box"]:
        fails.append(f"{R['in_box']} rockeries stand in a box")
    if R["shore_dry"]:
        fails.append(f"shore rockeries that do not reach the water: {R['shore_dry']}")

    files = {p.name: round(p.stat().st_size / 1e6, 3) for p in (SITE_DATA / "greens_1860.json", SITE_DATA / "greens_1860.geojson", GENERATED / "greens_1860.bin")}
    out["files_mb"] = files
    total = sum(files.values())
    print(f"files {files}, together {total:.2f} MB")
    if total > MAX_MB:
        fails.append(f"generated data {total:.2f} MB over {MAX_MB} MB")

    bfile = OUT / "greens_browser.json"
    if bfile.exists():
        br = json.load(open(bfile))
        if br.get("data_hash") != data_hash():
            fails.append("research/greens/greens_browser.json was measured on other data: run with --browser")
        else:
            out["browser"] = {"measured_utc": br["measured_utc"], "views": br["views"], "errors": br.get("errors", [])}
            for k, v in br["views"].items():
                print(f"  {k}: {v['frame_ms_median']} ms, {v['drawn_triangles']} triangles drawn, {v['draw_calls']} calls; near plants {v['greens_near_instances']}")
            if br.get("errors"):
                fails.append(f"browser errors: {br['errors'][:3]}")
    (OUT / "greens_check.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if fails:
        print("FAIL:\n  " + "\n  ".join(fails))
        sys.exit(1)
    print("ok")


if __name__ == "__main__":
    main()
