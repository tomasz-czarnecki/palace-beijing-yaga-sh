"""The kit check (Round 11): is every hall drawn by the hall kit or the stone kit, with its roof class from the data, inside its box, on the ground, met by the ways; and what it costs to draw.

  uv run python tools/check_kit.py                        the spec (data/kit_1860.json) against the boxes, and the last browser run (research/kit/kit_browser.json); exits non-zero on a failure
  uv run python tools/check_kit.py --browser              first measures the view in a headless browser (software WebGL): the kit's own report of what it drew, frame times and triangles,
                                                          with the kit and with the plain boxes; writes research/kit/kit_browser.json
  uv run python tools/check_kit.py --browser --before-url http://127.0.0.1:<port>/reconstruction/3d.html   also measures an older export served elsewhere (before Round 11)
  uv run python tools/check_kit.py --before <dir>         the joints of the ways in an older export (site/), for the record

The browser run needs Node and Playwright outside the repo (NODE_PATH, default /opt/data/cache/scratch/palace_r11_kit_tools/node_modules) and a Chrome (CHROME_PATH). It starts tools/serve_local.py --public on PORT.
Fails: a box with no kit entry; a hall the browser did not draw (no triangles at either level); a roof class, rolled ridge or double eave that differs from the box's;
a kit hall reaching beyond its box by more than its overhang (body or roof) or its steps beyond the overhang; a step flight whose foot is off the ground by more than JOINT_M;
an A or B way ending at a box side with no flight within REACH_M of its end and more than JOINT_M below the platform's top; a browser report older than the spec.
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

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from scene1860 import DATUM_M, Grid, to_xz  # noqa: E402

DATA = ROOT / "site/reconstruction/data"
OUT = ROOT / "research/kit"
JOINT_M = 0.3
REACH_M = 1.5  # a way's end this near a step flight's footprint meets it
TOL_M = 0.05
STONE_STEPS_M = 1.6  # a straight flight out of a European block, where a way reaches it: its run kept within 1.5 m
LIFT = 0.07  # paths3d.js
PORT = 8873
ROOF = {"hip": {"wd"}, "hip_gable": {"xs"}, "gable": {"ys", "xu"}, "pyramid": {"cj"}}
NODE = r"""
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [url, out, withReport] = process.argv.slice(2);
  const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH, args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await (await browser.newContext({ viewport: { width: 1400, height: 900 } })).newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  const t0 = Date.now();
  await page.goto(url, { waitUntil: 'load', timeout: 180000 });
  await page.waitForFunction(() => window.__ready === true, null, { timeout: 400000 });
  const res = { url, load_s: (Date.now() - t0) / 1000, views: {} };
  const views = { overview: [-100, 1100, 1700, 0, 0, -150], court: 'YM44', hall: 'YM03-01' };
  for (const kit of [true, false]) {
    for (const [name, v] of Object.entries(views)) {
      const m = await page.evaluate(({ v, kit }) => {
        const V = window.viewer;
        if ('kit' in V.state) V.state.kit = kit; else if (kit) return null;
        V.state.assumed = true; V.state.conf = false; V.apply();
        if (Array.isArray(v)) { V.camera.position.set(v[0], v[1], v[2]); V.controls.target.set(v[3], v[4], v[5]); }
        else {
          const bs = V.boxesOf(v); let x = 0, z = 0, y = 0; for (const b of bs) { x += b.cx; z += b.cz; y += (b.y0 + b.y1) / 2; } x /= bs.length; z /= bs.length; y /= bs.length;
          const d = v === 'YM44' ? 150 : 40, el = v === 'YM44' ? 0.5 : 0.2, a = bs[0].a, t = 0.35, dx = a[0] * Math.cos(t) - a[1] * Math.sin(t), dz = a[0] * Math.sin(t) + a[1] * Math.cos(t);
          V.camera.position.set(x + dx * d * Math.cos(el), y + d * Math.sin(el), z + dz * d * Math.cos(el)); V.controls.target.set(x, y, z);
        }
        V.controls.update(); V.render();
        const gl = V.renderer.getContext(), times = [];
        for (let i = 0; i < 13; i++) { const a0 = performance.now(); V.render(); gl.finish(); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array(4)); times.push(performance.now() - a0); }
        times.shift(); times.sort((a, b) => a - b);
        let total = 0; V.scene.traverse((o) => { if (o.isMesh && o.geometry) total += (o.geometry.index ? o.geometry.index.count : o.geometry.attributes.position.count) / 3; });
        return { frame_ms_median: Math.round(times[6] * 10) / 10, frame_ms_min: Math.round(times[0] * 10) / 10, frame_ms_max: Math.round(times[11] * 10) / 10, drawn_triangles: V.renderer.info.render.triangles, draw_calls: V.renderer.info.render.calls, triangles_in_memory: total };
      }, { v, kit });
      if (m) res.views[`${name}_${kit ? 'kit' : 'boxes'}`] = m;
    }
  }
  if (withReport === '1') res.report = await page.evaluate(() => { window.viewer.state.kit = true; window.viewer.apply(); return window.viewer.kit.report(); });
  res.errors = errors;
  fs.writeFileSync(out, JSON.stringify(res));
  await browser.close();
})();
"""


def spec_hash():
    return hashlib.md5((DATA / "kit_1860.json").read_bytes() + (DATA / "halls_1860.geojson").read_bytes()).hexdigest()


def run_browser(before_url):
    scratch = Path(os.environ.get("KIT_SCRATCH", "/opt/data/cache/scratch"))
    js = scratch / "palace_kit_check_browser.js"
    js.write_text(NODE)
    env = dict(os.environ, NODE_PATH=os.environ.get("NODE_PATH", "/opt/data/cache/scratch/palace_r11_kit_tools/node_modules"), CHROME_PATH=os.environ.get("CHROME_PATH", "/opt/hermes/tools/chromium-1208/chrome-linux64/chrome"))
    srv = subprocess.Popen([sys.executable, str(ROOT / "tools/serve_local.py"), "--port", str(PORT), "--public"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(2)
        out = {"spec_hash": spec_hash(), "measured_utc": time.strftime("%Y-%m-%d %H:%M", time.gmtime())}
        tmp = scratch / "palace_kit_check_after.json"
        subprocess.run(["node", str(js), f"http://127.0.0.1:{PORT}/reconstruction/3d.html?shot=1", str(tmp), "1"], env=env, check=True, timeout=3000)
        out["after"] = json.load(open(tmp))
        if before_url:
            tmpb = scratch / "palace_kit_check_before.json"
            subprocess.run(["node", str(js), before_url + ("&" if "?" in before_url else "?") + "shot=1", str(tmpb), "0"], env=env, check=True, timeout=3000)
            out["before"] = json.load(open(tmpb))
    finally:
        srv.terminate()
        srv.wait()
    OUT.mkdir(parents=True, exist_ok=True)
    report = out["after"].pop("report")
    (OUT / "kit_browser.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (OUT / "kit_report.json").write_text(json.dumps(report, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def frame(p):
    ring = np.array([to_xz(*c) for c in p["_ring"][:4]])
    c = (ring[0] + ring[2]) / 2
    u = (ring[1] - ring[0]) / np.linalg.norm(ring[1] - ring[0])
    a = (ring[1] - ring[2]) / np.linalg.norm(ring[1] - ring[2])
    return c, u, a, np.linalg.norm(ring[1] - ring[0]) / 2, np.linalg.norm(ring[1] - ring[2]) / 2


def way_ends(paths, boxes, G, steps_of=None):
    """Ends of ways that meet a box side ('F0568:front'): (grade, gap to the nearest flight in m or None, the drop from the platform's top to the way, the step's foot against the way)."""
    out = []
    for f in paths:
        p = f["properties"]
        coords = f["geometry"]["coordinates"]
        for at, pt in ((p.get("from_at"), coords[0]), (p.get("to_at"), coords[-1])):
            if not at or ":" not in at:
                continue
            bid, side = at.split(":", 1)
            if bid not in boxes or side not in ("front", "back", "left", "right"):
                continue
            b = boxes[bid]
            x, z = to_xz(*pt)
            g = G.at(x, z) if not G.is_water(x, z) else None
            if g is None:
                continue
            strip = g + LIFT
            top = b["ground_m"] - DATUM_M + (b.get("stand") or 0) + b["platform_m"]
            gap, foot = None, None
            for st in (steps_of or {}).get(bid, []):
                if st[0] != side:
                    continue
                d = math.hypot(x - st[1], z - st[2]) - st[6] / 2
                if gap is None or d < gap:
                    gap, foot = max(d, 0.0), st[3]
            grade = "AB" if not p["assumed"] else "C"
            entered = not (b.get("shape") in ("pool", "basin", "wall", "court") or b.get("stand"))  # a pool's rim, a wall, a court, or a hall on a terrace: no flight of its own
            out.append({"entered": entered, "box": bid, "side": side, "grade": grade, "drop_m": round(top - strip, 2), "gap_m": None if gap is None else round(gap, 2), "foot_m": None if foot is None else round(abs(foot - g), 2)})
    return out


def stats(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return {"n": 0}
    a = np.array(xs)
    return {"n": len(xs), "median": round(float(np.median(a)), 2), "p90": round(float(np.percentile(a, 90)), 2), "max": round(float(a.max()), 2)}


def before_joints(site):
    hall = {f["properties"]["id"]: f["properties"] for f in json.load(open(site / "reconstruction/data/halls_1860.geojson", encoding="utf-8"))["features"]}
    paths = json.load(open(site / "reconstruction/data/paths_1860.geojson", encoding="utf-8"))["features"]
    ends = way_ends(paths, hall, Grid())
    return {"way_ends_at_a_box_side": len(ends), "drop_platform_to_way_m": stats([e["drop_m"] for e in ends]), "with_steps": 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--browser", action="store_true")
    ap.add_argument("--before-url")
    ap.add_argument("--before", type=Path)
    args = ap.parse_args()
    if args.before:
        print(json.dumps(before_joints(args.before / "site" if (args.before / "site").exists() else args.before), indent=1))
        return
    if args.browser:
        run_browser(args.before_url)

    fc = json.load(open(DATA / "halls_1860.geojson", encoding="utf-8"))
    boxes = {}
    for f in fc["features"]:
        p = dict(f["properties"])
        p["_ring"] = f["geometry"]["coordinates"][0]
        boxes[p["id"]] = p
    spec = json.load(open(DATA / "kit_1860.json", encoding="utf-8"))
    K = spec["halls"]
    fails = []
    res = {}

    # 1. every box has an entry; the roof class follows the data
    missing = [i for i in boxes if i not in K]
    if missing:
        fails.append(f"{len(missing)} boxes with no kit entry: {missing[:8]}")
    bad_roof = []
    for i, e in K.items():
        p = boxes[i]
        if e["k"] in ("shape", "stoneshape") or "rf" not in e:
            continue
        if e["rf"] not in ROOF[p["roof"]] or ("rl" in e and bool(e["rl"]) != bool(p["rolled"]) and e["k"] != "stone") or bool(e.get("db", 0)) != bool(p["double"]):
            bad_roof.append((i, p["roof"], p["rolled"], p["double"], e["rf"], e.get("rl"), e.get("db")))
    if bad_roof:
        fails.append(f"{len(bad_roof)} roofs that differ from the data: {bad_roof[:6]}")
    chinese = {i: e for i, e in K.items() if e["k"] not in ("shape", "stone", "stoneshape")}
    stone = {i: e for i, e in K.items() if e["k"] in ("stone", "stoneshape")}
    res["counts"] = {
        "boxes": len(boxes), "kit_entries": len(K), "hall_kit": len(chinese), "stone_kit": len(stone), "shapes_left_as_boxes": sum(e["k"] == "shape" for e in K.values()),
        "by_kind": dict(Counter(e["k"] for e in K.values())),
        "roof_class": dict(Counter(f"{e['rf']}{' 卷棚' if e.get('rl') else ''}{' 重檐' if e.get('db') else ''}" for e in chinese.values())),
        "roof_class_stone": dict(Counter(e.get("rf") for e in stone.values())),
        "tiles": dict(Counter(e.get("t") for e in K.values() if e["k"] != "shape")), "tile_edges": dict(Counter(e["te"] for e in K.values() if e.get("te"))),
        "form_from": dict(Counter(e["src"] for e in K.values())),
        "assumed_form": sum(e["a"] for e in K.values()), "assumed_box": sum(bool(b["assumed"]) for b in boxes.values()),
        "form_grade": dict(Counter(e.get("g") for e in K.values())),
        "steps_sides": dict(Counter(len(e.get("st", [])) for e in chinese.values())), "balustrades": sum(e.get("bal", 0) for e in chinese.values()),
        "bracket_band": sum(e.get("bd") == "br" for e in chinese.values()), "porches": {"front": sum(e.get("pf", 0) > 0 for e in chinese.values()), "back": sum(e.get("pb", 0) > 0 for e in chinese.values()), "all_round": sum(e.get("ps", 0) > 0 for e in chinese.values())},
        "courts_ha": round(spec["courts"]["area_m2"] / 1e4, 1), "court_triangles": spec["courts"]["triangles"],
    }

    # 2. the browser's own report: drawn, inside the box, steps on the ground
    bfile, rfile = OUT / "kit_browser.json", OUT / "kit_report.json"
    if not (bfile.exists() and rfile.exists()):
        fails.append("no browser run: run with --browser")
    else:
        br = json.load(open(bfile, encoding="utf-8"))
        rep = json.load(open(rfile, encoding="utf-8"))
        if br["spec_hash"] != spec_hash():
            fails.append("research/kit/kit_browser.json is older than data/kit_1860.json or halls_1860.geojson: run with --browser")
        if br["after"].get("errors"):
            fails.append(f"page errors: {br['after']['errors'][:3]}")
        R = rep["boxes"]
        drawn = [i for i in K if K[i]["k"] != "shape" and K[i]["src"] != "model"]
        not_drawn = [i for i in drawn if i not in R or not (R[i]["tris"].get("near") and R[i]["tris"].get("far"))]
        if not_drawn:
            fails.append(f"{len(not_drawn)} kit halls not drawn: {not_drawn[:8]}")
        wrong = [i for i in drawn if i in R and R[i]["rf"] != K[i].get("rf")]
        if wrong:
            fails.append(f"{len(wrong)} halls drawn with another roof than the spec: {wrong[:6]}")
        over = []
        for i in drawn:
            if i not in R:
                continue
            o = K[i].get("o", 0.0) or 0.0
            stone = K[i]["k"] in ("stone", "stoneshape")
            lim = 0.6 if stone else o + TOL_M  # the stone kit: cornices and balustrades may stand 0.6 m proud of the plan's block
            ex = max(R[i]["out"]["body"], R[i]["out"]["roof"])
            if ex > lim or R[i]["out"]["steps"] > (STONE_STEPS_M if stone else o + TOL_M):
                over.append((i, round(ex, 2), round(R[i]["out"]["steps"], 2), o))
        if over:
            fails.append(f"{len(over)} halls beyond their box by more than an overhang: {over[:6]}")
        G = Grid()
        steps_of = {i: R[i].get("steps", []) for i in R}
        feet = []
        for i, sts in steps_of.items():
            for st in sts:
                x, z = st[1], st[2]
                g = G.land_at(x, z)  # the land, as the view's groundAt reads it (ground3d.js)
                feet.append(abs(st[3] - g) if g is not None else 9.99)
        bad_feet = sum(f > JOINT_M for f in feet)
        if bad_feet:
            fails.append(f"{bad_feet} step flights with a foot off the ground by more than {JOINT_M} m")
        paths = json.load(open(DATA / "paths_1860.geojson", encoding="utf-8"))["features"]
        ends = way_ends(paths, boxes, G, steps_of)
        unmet = [e for e in ends if e["entered"] and e["grade"] == "AB" and (e["gap_m"] is None or e["gap_m"] > REACH_M) and e["drop_m"] > JOINT_M]
        if unmet:
            fails.append(f"{len(unmet)} A or B ways end at a box side with no step flight within {REACH_M} m and a drop over {JOINT_M} m: {[(e['box'], e['side']) for e in unmet[:6]]}")
        res["drawn"] = {"halls_drawn": len(drawn) - len(not_drawn), "of": len(drawn), "near_triangles_median": stats([R[i]["tris"]["near"] for i in drawn if i in R])["median"],
                        "far_triangles_median": stats([R[i]["tris"]["far"] for i in drawn if i in R])["median"]}
        res["beyond_box_m"] = {"body_or_roof": stats([max(R[i]["out"]["body"], R[i]["out"]["roof"]) for i in drawn if i in R]), "steps": stats([R[i]["out"]["steps"] for i in drawn if i in R]),
                               "hall_kit_over_overhang": sum(1 for i in drawn if i in R and K[i]["k"] not in ("stone", "stoneshape") and max(R[i]["out"]["body"], R[i]["out"]["roof"]) > (K[i].get("o") or 0) + TOL_M)}
        res["joints"] = {"step_flights": len(feet), "step_foot_to_ground_m": stats(feet),
                         "way_ends_at_a_box_side": len(ends), "of_them_A_or_B": sum(e["grade"] == "AB" for e in ends), "at_a_pool_wall_court_or_terrace_hall": sum(not e["entered"] for e in ends),
                         "met_by_a_flight_within_m": REACH_M, "met": sum(1 for e in ends if e["gap_m"] is not None and e["gap_m"] <= REACH_M),
                         "gap_way_end_to_flight_m": stats([e["gap_m"] for e in ends]), "drop_platform_top_to_way_m": stats([e["drop_m"] for e in ends]),
                         "drop_left_where_no_flight_m": stats([e["drop_m"] for e in ends if e["entered"] and (e["gap_m"] is None or e["gap_m"] > REACH_M)]),
                         "no_flight_where_entered": [(e["box"], e["side"], e["grade"], e["drop_m"]) for e in ends if e["entered"] and (e["gap_m"] is None or e["gap_m"] > REACH_M)]}
        res["cost"] = {"browser": {k: v for k, v in br.items() if k in ("measured_utc",)}, "after": br["after"]["views"], "after_load_s": br["after"]["load_s"],
                       "before": br.get("before", {}).get("views"), "before_load_s": br.get("before", {}).get("load_s"),
                       "near_triangles_if_all_built": rep["near_triangles_all"], "far_triangles": rep["far_triangles"], "court_triangles": rep["court_triangles"], "lod_m": rep["lod_m"], "tile_m": rep["tile_m"], "tiles": rep["tiles"]}
    sizes = {n: (ROOT / n).stat().st_size for n in ("site/reconstruction/data/kit_1860.json", "site/reconstruction/generated/courts.bin", "site/reconstruction/kit3d.js", "site/reconstruction/stonekit3d.js")}
    res["files_mb"] = {k.split("/")[-1]: round(v / 1e6, 3) for k, v in sizes.items()} | {"total": round(sum(sizes.values()) / 1e6, 2)}
    res["fails"] = fails
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "kit_check.json").write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "fails"}, ensure_ascii=False, indent=1))
    if fails:
        print("FAIL:\n  " + "\n  ".join(fails))
        sys.exit(1)
    print("kit check passed")


if __name__ == "__main__":
    main()
