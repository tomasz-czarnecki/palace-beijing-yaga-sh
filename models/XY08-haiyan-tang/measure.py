#!/usr/bin/env python3
"""Measure 海晏堂's heights on the photographs (method d with resection), as the pilot's models/XY01-xieqiqu/measure.py: one least-squares over every picture's camera and the figures.

  uv run python models/XY08-haiyan-tang/measure.py [--photos P0774,P0170,P0299] [--figs H1,H2,Hr] [--plates] [--out measure.json]

The photographs (Ohlmer's P0774 of 1873 from the west, the ruin photographs P0170 of about 1902 and P0299 of about 1914-20) are true perspectives; the plates are not, so by default
the figures come from the photographs and the plates are then tested against them (tools/plate_overlay.py). With --plates the plates are used as well, each with its own vertical stretch k.
Scale: the west block's frontage W (S01, 47.2 m) and the plan's positions are held; every measured figure scales with them.
Each key point is affine in the figures; the slope is taken by building the model's points once per figure (haiyantang.reset / build), so the fit never rebuilds the model.
Writes measure/<out> (each figure: prior, measured, its standard error, the pictures' residuals before and after). It changes nothing in haiyantang.py: the figures are carried there by hand.
"""

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools"))
import haiyantang as X  # noqa: E402
import plate_overlay as T  # noqa: E402

SD = {"H1": 2.0, "H2": 2.0, "Hr": 2.0, "ped_apex": 2.5, "attic_h": 1.5, "ridge_pav": 2.5, "ridge_mid": 2.5, "pav_eave": 1.5, "pav_ridge": 2.5, "L1": 1.5, "L2": 1.5,
      "plinth_h": 0.8, "fig_h": 0.5, "shell_h": 1.0, "link_h": 1.5, "ped_h": 1.5, "D": 3.0, "wing_d": 3.0, "cen_w": 3.0, "pav_w": 3.0}


def points(over):
    X.reset(over)
    X.build()
    out = {}
    for k, v in X.KP.items():
        if "p" in v:
            out[k] = {"scene": X.to_scene(v["p"]), "anchor": v.get("anchor", False)}
        else:
            out[k] = {"cands": [{"scene": X.to_scene(c["p"])} for c in v["cands"]], "pick": v["pick"], "anchor": v.get("anchor", False)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--photos", default="P0774,P0170,P0299")
    ap.add_argument("--figs", default="H1,H2,Hr,ped_apex")
    ap.add_argument("--plates", action="store_true", help="the plates too, each with its own vertical stretch k")
    ap.add_argument("--out", default="measure.json")
    a = ap.parse_args()
    X.load()
    figs = {k: SD[k] for k in a.figs.split(",")}
    keys = list(figs)
    nf = len(keys)
    p0 = {k: X.P[k][0] for k in keys}
    cat = T.catalogue()
    allrows = [r for r in T.rd(ROOT / "research/xiyanglou/plate_keypoints.csv") if r["object"].split("-")[0] == "XY08" and not r.get("use", "").startswith("skip")]
    pics = [p for p in a.photos.split(",") if p]
    if a.plates:
        pics += sorted({r["photo_id"] for r in allrows if r["plate"]})
    base = points({})
    slopes = {k: points({k: p0[k] + 1.0}) for k in keys}
    data = []
    for pid in pics:
        mine = [r for r in allrows if r["photo_id"] == pid]
        if len(mine) < 4:
            print(pid, "has", len(mine), "points: left out")
            continue
        path, free = T.image_path(pid, cat)
        size = Image.open(path).size
        plate = next((r["plate"] for r in mine if r["plate"]), "")
        pr = T.priors_of(pid, plate, cat)
        x0, z0 = T.to_xz(pr["lon"], pr["lat"])
        C = np.array([x0, 0, z0])
        r0 = T.resolve(base, C)
        lin = {}
        for n in r0:
            P0 = r0[n][0]
            J = np.stack([T.resolve(slopes[k], C)[n][0] - P0 for k in keys], axis=1)
            lin[n] = (P0, J)
        obs = [(r["point"], float(r["x"]), float(r["y"]), r["sure"]) for r in mine if r["point"] in lin]
        cam0, _, _ = T.fit_camera({o[0]: (o[1], o[2], o[3]) for o in obs}, r0, size, pr, "stretch" if plate else "all")
        data.append({"pid": pid, "size": size, "pr": pr, "obs": obs, "lin": lin, "cam0": cam0})
    sizes = [len(d["cam0"]) for d in data]
    offs = np.cumsum([nf] + sizes)

    def unpack(t):
        return t[:nf], [t[offs[i]: offs[i + 1]] for i in range(len(data))]

    def res(t, prior=True):
        f, cams = unpack(t)
        out = []
        for d, cam in zip(data, cams):
            for n, u, v, s in d["obs"]:
                P0, J = d["lin"][n]
                p, zc = T.project(cam, P0 + J @ f, d["size"])
                sg = T.SIGMA.get(s, 8.0)
                out += [(p[0] - u) / sg, (p[1] - v) / sg] if zc > 0.5 else [100.0, 100.0]
            pr = d["pr"]
            x0, z0 = T.to_xz(pr["lon"], pr["lat"])
            gy = T.ground_at(x0, z0)
            W, H = d["size"]
            out += [(cam[0] - x0) / pr["err"], (cam[2] - z0) / pr["err"], (cam[1] - gy - pr["eye"]) / pr["eye_sd"], cam[6] / (0.08 * W), cam[7] / (0.12 * H), cam[4] / (0.03 if pr["kind"] == "plate" else 0.15)]
            if len(cam) > 8:
                out.append(cam[8])
        if prior:
            out += [f[i] / figs[k] for i, k in enumerate(keys)]
        return np.array(out)

    t0 = np.concatenate([np.zeros(nf)] + [d["cam0"] for d in data])
    r = least_squares(res, t0, loss="soft_l1", f_scale=2.0, max_nfev=6000)
    f, cams = unpack(r.x)
    try:
        se = np.sqrt(np.diag(np.linalg.inv(r.jac.T @ r.jac)))[:nf]
    except np.linalg.LinAlgError:
        se = np.full(nf, np.nan)
    out = {"pictures": [d["pid"] for d in data], "scale": "W 47.2 m (S01) and the plan's positions held", "figures": {}, "residuals": {}}
    for i, k in enumerate(keys):
        out["figures"][k] = {"prior": p0[k], "measured": round(p0[k] + float(f[i]), 2), "se": round(float(se[i]), 2), "prior_sd": figs[k]}
    for d, cam in zip(data, cams):
        e0, e1 = [], []
        for n, u, v, s in d["obs"]:
            P0, J = d["lin"][n]
            p, _ = T.project(d["cam0"], P0, d["size"])
            e0.append(math.hypot(p[0] - u, p[1] - v))
            p, _ = T.project(cam, P0 + J @ f, d["size"])
            e1.append(math.hypot(p[0] - u, p[1] - v))
        out["residuals"][d["pid"]] = {"n": len(e0), "rms_px_before": round(float(np.sqrt(np.mean(np.square(e0)))), 1), "rms_px_after": round(float(np.sqrt(np.mean(np.square(e1)))), 1),
                                      "f_px": round(math.exp(cam[5]), 0), "k": round(math.exp(cam[8]), 3) if len(cam) > 8 else 1.0}
    (HERE / "measure").mkdir(exist_ok=True)
    json.dump(out, open(HERE / "measure" / a.out, "w", encoding="utf-8"), indent=1)
    for k, v in out["figures"].items():
        print(f"{k:10s} prior {v['prior']:6.2f}  measured {v['measured']:6.2f} ± {v['se']:.2f}")
    for k, v in out["residuals"].items():
        print(k, v)


if __name__ == "__main__":
    main()
