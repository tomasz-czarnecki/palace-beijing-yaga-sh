#!/usr/bin/env python3
"""The plate overlay test (Round 13): a 3D object seen from a plate's or a photograph's camera, laid over the picture, and measured.

  uv run python tools/plate_overlay.py fit --object XY01 [--images P0041,P0042] [--label v3]
  node tools/plate_overlay.mjs --object XY01            (the renders, from one page load; tools/serve_local.py must not be running on 8891)
  uv run python tools/plate_overlay.py compose --object XY01

Generic: any picture with rows in research/xiyanglou/plate_keypoints.csv, any XY object. The object's points come from its detailed model (models/<ID>-<slug>/keypoints.json,
written by the model's generator) or, with no model, from the stone kit's numbers (data/halls_1860.geojson, data/kit_1860.json): the corners at foot and cornice, the ridge, the eave tips,
the pediment, the stair landing, as stonekit3d.js draws them.

The camera is a pinhole: position C, bearing (yaw), pitch, focal length F in the picture's pixels, principal point offset (du, dv); no roll, no lens distortion. Two fits per picture:
  anchored: C, yaw, pitch, F, du, dv from the points the plan or the ruin places (feet, pool rims: `anchor` in keypoints.json) and the priors of the viewpoint
            (research/xiyanglou/viewpoints.csv for plates, photo_viewpoints.csv for photographs: position within err_m, eye height, F 1250 px at 2400 px for the plates, viewpoints.csv `basis`);
            every other point is then a test of the model's heights and widths.
  all:      the same with every point: the best a single camera can do; its residuals are the shape disagreement between model and picture.
  stretch:  plates only: `all` with one more unknown, k, the plate's heights drawn k times its widths. The engravers' idealisation, measured, not tuned into the model.
The error in metres at the object is the pixel error times the point's depth over F.

Writes research/xiyanglou/plate_fit_<object>.csv (a row per point, picture and fit), research/xiyanglou/plate_cameras_<object>.json, site/reconstruction/data/plates.json
(the cameras of free pictures, for ?plate= in the 3D view), screenshots/r13/points_<picture>_<object>.jpg (crosses: the picture's points; circles: the model's).
Research-only pictures (rights_class not free) are read from research/raw/photos/ and their images go to screenshots/r13/local/ only; plates.json never names them.
"""

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))
from scene1860 import DATUM_M, to_xz  # noqa: E402

XY = ROOT / "research/xiyanglou"
SHOTS = ROOT / "screenshots/r13"
SIGMA = {"1": 3.0, "2": 8.0, "3": 15.0}
F_PLATE_2400 = 1250.0  # viewpoints.csv: 'D=f/s with f=1250 px of plates 1-2', on the 2400 px copies


def rd(path):
    return list(csv.DictReader(open(path, encoding="utf-8"))) if path.exists() else []


def catalogue():
    return {r["photo_id"]: r for r in rd(ROOT / "research/photos/catalog.csv")}


def image_path(pid, cat):
    free = cat[pid]["rights_class"] == "free"
    return (ROOT / f"research/photos/images/{pid}.jpg" if free else ROOT / f"research/raw/photos/{pid}.jpg"), free


# ---------------------------------------------------------------- the object's points
def model_points(obj):
    for p in sorted((ROOT / "models").glob("*/keypoints.json")):
        k = json.load(open(p, encoding="utf-8"))
        if obj == k["id"] or obj in k.get("objects", []):
            return k["points"], f"model {p.parent.name}"
    return kit_points(obj), "stone kit"


def kit_points(obj):
    """Points of the stone kit's drawing of the object's largest box (stonekit3d.js, the palace block branch)."""
    fc = json.load(open(ROOT / "site/reconstruction/data/halls_1860.geojson", encoding="utf-8"))
    kit = json.load(open(ROOT / "site/reconstruction/data/kit_1860.json", encoding="utf-8"))["halls"]
    feats = [f for f in fc["features"] if f["properties"]["building_id"] == obj and not f["properties"].get("shape")]
    f = max(feats, key=lambda f: f["properties"]["frontage_m"] * f["properties"]["depth_m"])
    p, e = f["properties"], kit[f["properties"]["id"]]
    ring = [np.array(to_xz(*c), float) for c in f["geometry"]["coordinates"][0]]
    c = (ring[0] + ring[2]) / 2
    u, a = ring[1] - ring[0], ring[1] - ring[2]
    hf, hd = np.linalg.norm(u) / 2, np.linalg.norm(a) / 2
    u, a = u / np.linalg.norm(u), a / np.linalg.norm(a)
    base = p["ground_m"] - DATUM_M
    at = lambda s, y, q: [float(c[0] + u[0] * s + a[0] * q), float(y), float(c[1] + u[1] * s + a[1] * q)]
    eave, ridge, plTop = base + p["eave_m"], base + p["ridge_m"], base + p["platform_m"]
    sto = max(1, e.get("sto", 1))
    stairD = min(2 * hd * 0.3, 6) if e.get("stair") else 0
    qF, qB, sF = hd - stairD - 0.3, -hd + 0.3, hf - 0.3
    out = {}

    def compass(pt):
        dx, dz = pt[0] - c[0], pt[2] - c[1]
        return ("N" if dz < 0 else "S") + ("W" if dx < 0 else "E")

    for s in (-sF, sF):
        for q in (qB, qF):
            foot = at(s, base, q)
            tag = compass(foot)
            out[f"blk_foot_{tag}"] = {"scene": foot, "anchor": True}
            out[f"blk_cornice_{tag}"] = {"scene": at(s * (sF + 0.45) / sF, eave, q + (0.45 if q > 0 else -0.45))}
    rs, rq = sF + 0.5, (qF - qB) / 2 + 0.5
    qc = (qF + qB) / 2
    along = rs >= rq
    rl = max(abs(rs - rq), 0.0)
    for sg in (-1, 1):
        pt = at(sg * rl, ridge, qc) if along else at(0, ridge, qc + sg * rl)
        dx, dz = pt[0] - c[0], pt[2] - c[1]
        tag = ("E" if dx > 0 else "W") if abs(dx) > abs(dz) else ("S" if dz > 0 else "N")
        out[f"blk_ridge_{tag}"] = {"scene": pt}
        for sq in (-1, 1):
            tip = at(sg * rs, eave + 0.25, qc + sq * rq)
            out[f"blk_eave_{compass(tip)}"] = {"scene": tip}
    hS = (eave - plTop) / sto
    front = at(0, 0, 1)
    fdir = np.array([front[0] - c[0], front[2] - c[1]])
    ftag = "W" if abs(fdir[0]) > abs(fdir[1]) and fdir[0] < 0 else "E" if abs(fdir[0]) > abs(fdir[1]) else "S" if fdir[1] > 0 else "N"
    if e.get("ped"):
        w = min(sF * 0.45, 7)
        out[f"blk_ped_apex_{ftag}"] = {"scene": at(0, eave + min(2.4, w * 0.4), qF + 0.3)}
    nb = e.get("nb", 3)
    w = 2 * sF / nb
    ow = min(w * 0.5, 2.6)
    yo1 = max(plTop + 0.1 + 0.8, plTop + hS - 0.9 - ow / 2 - 0.35)
    out[f"blk_door_{ftag}_head"] = {"scene": at(0, yo1 + ow / 2, qF)}
    if e.get("stair"):
        out[f"blk_stair_land_{ftag}"] = {"scene": at(0, plTop + min(hS * 0.5, 3.2), qF + 1.6)}
    for g in fc["features"]:
        q = g["properties"]
        if q["building_id"].startswith(obj + "-") and q.get("shape") == "pool":
            rr = [np.array(to_xz(*cc), float) for cc in g["geometry"]["coordinates"][0]]
            cc = (rr[0] + rr[2]) / 2
            uu, aa = rr[1] - rr[0], rr[1] - rr[2]
            y = q["ground_m"] - DATUM_M + q["eave_m"]
            for vec in (uu / 2, -uu / 2, aa / 2, -aa / 2):
                pt = [float(cc[0] + vec[0]), float(y), float(cc[1] + vec[1])]
                dx, dz = vec
                tag = ("E" if dx > 0 else "W") if abs(dx) > abs(dz) else ("S" if dz > 0 else "N")
                key = f"pool12_rim_{tag}" if obj == "XY08" else f"pool_rim_{tag}"
                out[key] = {"scene": pt, "anchor": True}
    return out


def resolve(points, C):
    """A point's scene position; view-dependent points (an octagon's face, a rim's extreme) chosen for a camera at C."""
    out = {}
    for name, v in points.items():
        if "scene" in v:
            out[name] = (np.array(v["scene"], float), v.get("anchor", False))
            continue
        cands = v["cands"]
        P = np.array([q["scene"] for q in cands], float)
        if v["pick"] == "facing":
            score = [np.dot(q["n"], [C[0] - q["scene"][0], C[2] - q["scene"][2]]) / (np.hypot(C[0] - q["scene"][0], C[2] - q["scene"][2]) + 1e-9) for q in cands]
            out[name] = (P[int(np.argmax(score))], v.get("anchor", False))
        else:
            cen = P.mean(0)
            look = cen - C
            look = np.array([look[0], look[2]]) / np.hypot(look[0], look[2])
            left = np.array([look[1], -look[0]])
            sc = (P[:, 0] - cen[0]) * left[0] + (P[:, 2] - cen[2]) * left[1]
            out[name] = (P[int(np.argmax(sc) if v["pick"] == "left" else np.argmin(sc))], v.get("anchor", False))
    return out


# ---------------------------------------------------------------- camera
def basis(yaw, pitch):
    f = np.array([math.sin(yaw) * math.cos(pitch), math.sin(pitch), -math.cos(yaw) * math.cos(pitch)])
    r = np.cross(f, [0.0, 1.0, 0.0])
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return f, r, u


def project(cam, X, size):
    """cam: C (3), yaw, pitch, log F, du, dv, and optionally log k: the picture's heights drawn k times its widths (a plate's idealisation; 1 for a camera)."""
    C, yaw, pitch, F, du, dv = cam[:3], cam[3], cam[4], math.exp(cam[5]), cam[6], cam[7]
    k = math.exp(cam[8]) if len(cam) > 8 else 1.0
    f, r, u = basis(yaw, pitch)
    d = np.asarray(X) - C
    zc = d @ f
    return np.array([size[0] / 2 + du + F * (d @ r) / zc, size[1] / 2 + dv - k * F * (d @ u) / zc]), zc


def priors_of(pid, plate, cat):
    """The viewpoint's prior: position (scene x, z), its error, the eye's height above the ground, the bearing, a focal length if known."""
    if plate:
        r = next(r for r in rd(XY / "viewpoints.csv") if r["plate"] == plate)
        eye = {"1": 6.2, "2": 4.6}.get(plate)
        if eye is None:
            import re
            mm = re.search(r"[Ee]ye (?:about )?([\d.]+) m", r["basis"])
            eye = float(mm.group(1)) if mm else 4.0
        return {"lat": float(r["lat"]), "lon": float(r["lon"]), "err": float(r["err_m"]), "bearing": float(r["bearing"]), "eye": eye, "eye_sd": 3.0, "f2400": F_PLATE_2400, "f_sd": 0.25, "kind": "plate", "basis": r["basis"]}
    r = next((r for r in rd(XY / "photo_viewpoints.csv") if r["photo_id"] == pid), None)
    if r is None:
        c = cat[pid]
        r = {"lat": c["camera_lat"], "lon": c["camera_lon"], "err_m": 20, "bearing": c["bearing"], "eye_m": 1.6, "basis": c["camera_note"]}
    return {"lat": float(r["lat"]), "lon": float(r["lon"]), "err": float(r["err_m"]), "bearing": float(r["bearing"]), "eye": float(r.get("eye_m") or 1.6), "eye_sd": float(r.get("eye_sd") or 2.0), "f2400": None, "f_sd": None, "kind": "photo", "basis": r["basis"]}


def ground_at(x, z):
    from check_ground import NewGround
    if not hasattr(ground_at, "G"):
        ground_at.G = NewGround(ROOT)
    g = ground_at.G.land(x, z)
    return g if g is not None else ground_at.G.at(x, z)


def fit_camera(obs, pts, size, pr, use):
    """obs: name -> (x, y, sure); pts: name -> (X, anchor); use: 'anchored' or 'all'."""
    W, H = size
    x0, z0 = to_xz(pr["lon"], pr["lat"])
    gy = ground_at(x0, z0)
    C0 = np.array([x0, gy + pr["eye"], z0])
    yaw0 = math.radians(pr["bearing"])
    F0 = pr["f2400"] * W / 2400 if pr["f2400"] else 0.9 * W
    names = [n for n in obs if n in pts and (use != "anchored" or pts[n][1])]
    plate = pr["kind"] == "plate"

    def res(t):
        cam = t
        out = []
        for n in names:
            p, zc = project(cam, pts[n][0], size)
            s = SIGMA.get(obs[n][2], 8.0)
            if zc <= 0.5:
                out += [100.0, 100.0]
                continue
            out += [(p[0] - obs[n][0]) / s, (p[1] - obs[n][1]) / s]
        out += [(cam[0] - C0[0]) / pr["err"], (cam[2] - C0[2]) / pr["err"], (cam[1] - C0[1]) / pr["eye_sd"]]
        if pr["f_sd"]:
            out.append((cam[5] - math.log(F0)) / pr["f_sd"])
        out += [cam[6] / (0.08 * W), cam[7] / (0.12 * H), cam[4] / (0.03 if plate else 0.15)]
        out.append(((cam[3] - yaw0 + math.pi) % (2 * math.pi) - math.pi) / math.radians(25))
        if len(cam) > 8:
            out.append(cam[8] / 1.0)  # a weak pull towards k = 1
        return np.array(out)

    t0 = np.array([*C0, yaw0, 0.0, math.log(F0), 0.0, 0.0] + ([0.0] if use == "stretch" else []))
    best = None
    for dyaw in (0.0, 0.15, -0.15):
        t = t0.copy()
        t[3] += dyaw
        r = least_squares(res, t, loss="soft_l1", f_scale=2.0, max_nfev=4000)
        if best is None or r.cost < best.cost:
            best = r
    return best.x, names, C0


def stats(rows):
    if not rows:
        return {"n": 0}
    e = np.array([r["err_px"] for r in rows])
    em = np.array([r["err_m"] for r in rows])
    return {"n": len(rows), "rms_px": round(float(np.sqrt((e ** 2).mean())), 1), "median_px": round(float(np.median(e)), 1), "max_px": round(float(e.max()), 1),
            "rms_m": round(float(np.sqrt((em ** 2).mean())), 2), "median_m": round(float(np.median(em)), 2), "max_m": round(float(em.max()), 2)}


def cmd_fit(args):
    cat = catalogue()
    pts_def, origin = model_points(args.object)
    rows = [r for r in rd(XY / "plate_keypoints.csv") if r["object"].split("-")[0] == args.object.split("-")[0]]
    images = args.images.split(",") if args.images else sorted({r["photo_id"] for r in rows})
    SHOTS.mkdir(parents=True, exist_ok=True)
    (SHOTS / "local").mkdir(exist_ok=True)
    table, cams = [], {}
    for pid in images:
        mine = [r for r in rows if r["photo_id"] == pid]
        if not mine:
            continue
        plate = mine[0]["plate"]
        path, free = image_path(pid, cat)
        size = Image.open(path).size
        pr = priors_of(pid, plate, cat)
        x0, z0 = to_xz(pr["lon"], pr["lat"])
        pts = resolve(pts_def, np.array([x0, 0, z0]))
        obs = {r["point"]: (float(r["x"]), float(r["y"]), r["sure"]) for r in mine if not r.get("use", "").startswith("skip")}
        skipped = {r["point"]: (float(r["x"]), float(r["y"]), r["sure"]) for r in mine if r.get("use", "").startswith("skip")}
        missing = sorted(n for n in obs if n not in pts)
        cams[pid] = {"plate": plate, "image": f"{pid}.jpg", "free": free, "size": list(size), "object": args.object, "points_from": origin, "prior": pr, "not_in_model": missing, "fits": {}}
        for use in ("anchored", "all", "stretch") if plate else ("anchored", "all"):
            n_anchor = sum(1 for n in obs if n in pts and pts[n][1])
            if use == "anchored" and n_anchor < 3:
                cams[pid]["fits"][use] = {"skipped": f"{n_anchor} anchor points"}
                continue
            cam, used, C0 = fit_camera(obs, pts, size, pr, use)
            # a second pass with the faces chosen for the fitted camera
            pts = resolve(pts_def, cam[:3])
            cam, used, C0 = fit_camera(obs, pts, size, pr, use)
            out = []
            for n, (u, v, s) in list(obs.items()) + list(skipped.items()):
                if n not in pts:
                    continue
                p, zc = project(cam, pts[n][0], size)
                F = math.exp(cam[5])
                err = float(np.hypot(p[0] - u, p[1] - v))
                row = {"image": pid, "plate": plate, "object": args.object, "fit": use, "point": n, "sure": s, "role": "skipped" if n in skipped else "anchor" if pts[n][1] else "test", "in_fit": n in used,
                       "x_img": u, "y_img": v, "x_model": round(float(p[0]), 1), "y_model": round(float(p[1]), 1), "dx": round(float(p[0] - u), 1), "dy": round(float(p[1] - v), 1),
                       "err_px": round(err, 1), "depth_m": round(float(zc), 1), "err_m": round(err * float(zc) / F, 2)}
                out.append(row)
            table += out
            gy = ground_at(cam[0], cam[2])
            cams[pid]["fits"][use] = {
                "position": [round(float(c), 2) for c in cam[:3]], "yaw_deg": round(math.degrees(cam[3]) % 360, 2), "pitch_deg": round(math.degrees(cam[4]), 2), "f_px": round(math.exp(cam[5]), 1),
                "du_px": round(float(cam[6]), 1), "dv_px": round(float(cam[7]), 1), "k_vertical": round(math.exp(cam[8]), 3) if len(cam) > 8 else 1.0, "eye_above_ground_m": round(float(cam[1] - gy), 2), "moved_from_prior_m": round(float(np.hypot(cam[0] - C0[0], cam[2] - C0[2])), 1),
                "points": stats([r for r in out if r["role"] != "skipped"]), "tests": stats([r for r in out if r["role"] == "test"]), "sure12": stats([r for r in out if r["sure"] in ("1", "2") and r["role"] != "skipped"]), "skipped": stats([r for r in out if r["role"] == "skipped"])}
        draw_points(pid, path, free, [r for r in table if r["image"] == pid], args.object)
        a = cams[pid]["fits"].get("all", {})
        b = cams[pid]["fits"].get("anchored", {})
        print(f"{pid} plate {plate or '-'}: {len(obs)} read, {len(missing)} not in the model; all: {a.get('points')}; anchored tests: {b.get('tests', b.get('skipped'))}")
    with open(XY / f"plate_fit_{args.object}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(table[0].keys()))
        w.writeheader()
        w.writerows(table)
    json.dump({"object": args.object, "label": args.label, "points_from": origin, "cameras": cams}, open(XY / f"plate_cameras_{args.object}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    publish_cameras()


def publish_cameras():
    """site/reconstruction/data/plates.json: every free picture's fitted cameras, for the 3D view's ?plate= mode. Research-only pictures stay out."""
    out = {}
    for p in sorted(XY.glob("plate_cameras_*.json")):
        d = json.load(open(p, encoding="utf-8"))
        for pid, c in d["cameras"].items():
            if not c["free"]:
                continue
            W, H = c["size"]
            for use, f in c["fits"].items():
                if "position" not in f:
                    continue
                out.setdefault(pid, {"object": d["object"], "plate": c["plate"], "image": f"photos/{pid}.jpg", "size": [W, H], "fits": {}})["fits"][use] = {
                    "position": f["position"], "yaw_deg": f["yaw_deg"], "pitch_deg": f["pitch_deg"], "f_px": f["f_px"], "du_px": f["du_px"], "dv_px": f["dv_px"], "k_vertical": f.get("k_vertical", 1.0), "rms_px": f["points"]["rms_px"]}
    json.dump({"note": "Round 13: cameras of the plates and photographs fitted by tools/plate_overlay.py, for ?plate=<photo id> in 3d.html. Pixels of the 2400 px copy (size).", "plates": out},
              open(ROOT / "site/reconstruction/data/plates.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)


def draw_points(pid, path, free, rows, obj):
    im = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(im)
    sc = max(1, round(im.width / 1200))
    for r in rows:
        col = (230, 40, 40) if r["fit"] == "all" else (40, 120, 255)
        x, y, mx, my = r["x_img"], r["y_img"], r["x_model"], r["y_model"]
        if r["fit"] == "all":
            d.line([(x - 6 * sc, y), (x + 6 * sc, y)], fill=(20, 200, 60), width=2 * sc)
            d.line([(x, y - 6 * sc), (x, y + 6 * sc)], fill=(20, 200, 60), width=2 * sc)
        if -1e4 < mx < 1e4 and -1e4 < my < 1e4:
            d.ellipse([mx - 5 * sc, my - 5 * sc, mx + 5 * sc, my + 5 * sc], outline=col, width=sc)
            d.line([(x, y), (mx, my)], fill=col, width=1)
    dest = SHOTS if free else SHOTS / "local"
    im.save(dest / f"points_{pid}_{obj}.jpg", quality=85)


# ---------------------------------------------------------------- composites: the render beside and over the picture
def cmd_compose(args):
    cat = catalogue()
    d = json.load(open(XY / f"plate_cameras_{args.object}.json", encoding="utf-8"))
    for pid, c in d["cameras"].items():
        path, free = image_path(pid, cat)
        dest = SHOTS if free else SHOTS / "local"
        for use in ("all", "anchored", "stretch"):
            rp = dest / f"render_{pid}_{args.object}_{use}.png"
            if not rp.exists():
                continue
            pl = Image.open(path).convert("RGB")
            W = 1600
            H = round(pl.height * W / pl.width)
            pl = pl.resize((W, H), Image.LANCZOS)
            rn = Image.open(rp).convert("RGB").resize((W, H), Image.LANCZOS)
            Image.blend(pl, rn, 0.5).save(dest / f"overlay_{pid}_{args.object}_{use}_blend.jpg", quality=85)
            g = np.asarray(rn.convert("L"), float)
            gx = np.abs(np.diff(g, axis=1, prepend=g[:, :1]))
            gy = np.abs(np.diff(g, axis=0, prepend=g[:1, :]))
            e = np.clip((gx + gy - 14) * 6, 0, 255).astype(np.uint8)
            edge = Image.fromarray(e).filter(ImageFilter.MaxFilter(3))
            base = pl.convert("L").convert("RGB")
            red = Image.new("RGB", (W, H), (235, 30, 30))
            Image.composite(red, base, edge).save(dest / f"overlay_{pid}_{args.object}_{use}_edges.jpg", quality=85)
            side = Image.new("RGB", (W * 2 + 10, H), (255, 255, 255))
            side.paste(pl, (0, 0))
            side.paste(rn, (W + 10, 0))
            side.resize((W, round(H / 2))).save(dest / f"overlay_{pid}_{args.object}_{use}_side.jpg", quality=85)
            print("composed", pid, use)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fit")
    f.add_argument("--object", required=True)
    f.add_argument("--images", default="")
    f.add_argument("--label", default="")
    c = sub.add_parser("compose")
    c.add_argument("--object", required=True)
    args = ap.parse_args()
    {"fit": cmd_fit, "compose": cmd_compose}[args.cmd](args)


if __name__ == "__main__":
    main()
