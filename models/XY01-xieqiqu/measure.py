#!/usr/bin/env python3
"""Measure 谐奇趣's heights and widths on the 1873 photographs (method d with resection), as Küstrin's B01 fit.py: one least-squares over every photograph's camera and the model's figures.

  uv run python models/XY01-xieqiqu/measure.py

The photographs P0185-P0189 are true perspectives, the plates are not (Round 13: tools/plate_overlay.py), so the as-built figures come from the photographs and the plates are then tested against them.
Scale: the block's frontage W (S01, 27.2 m) and the octagons' spacing (S850) are held; every measured figure scales with them (±15 % on W: Q72).
Each key point's position is affine in the figures; the slope is taken by building the model's points once per figure (xieqiqu.reset / build), so the fit never rebuilds the model.
Writes measure/measure.json (each figure: prior, measured, its standard error, the photographs' residuals before and after). It changes nothing in xieqiqu.py: the figures are carried there by hand, with this file named.
"""

import csv
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
import xieqiqu as X  # noqa: E402
import plate_overlay as T  # noqa: E402

PHOTOS = ["P0185", "P0186", "P0187", "P0188", "P0189"]
FIGS = {"H1": 2.0, "H2": 2.0, "Ht": 2.0, "Wc": 3.0, "D": 3.0, "oct_up": 2.0, "nst_foot": 2.0}  # prior standard deviation, m
# The roofs: no photograph shows them (gone by 1873), so ridge and apex are read on the plates, every other figure held at the photographs' values:
#   uv run python models/XY01-xieqiqu/measure.py --roofs
ROOFS = (["P0041", "P0042"], {"ridge": 3.0, "oct_apex": 3.0})
if "--roofs" in sys.argv:
    PHOTOS, FIGS = ROOFS
# (Tried in Round 13 and dropped: the south pool's width and place on plate 1 alone. The plate's depth is too compressed: the pool ran 35 m into the lake. See README.md.)


def points(over):
    X.reset(over)
    X.build()
    pos, rot = X.frame()
    out = {}
    for k, v in X.KP.items():
        if "p" in v:
            out[k] = {"scene": X.to_scene(v["p"], pos, rot), "anchor": v.get("anchor", False)}
        else:
            cands = []
            for c in v["cands"]:
                q = {"scene": X.to_scene(c["p"], pos, rot)}
                if "n" in c:
                    cs, sn = math.cos(rot), math.sin(rot)
                    q["n"] = [cs * c["n"][0] + sn * c["n"][1], -sn * c["n"][0] + cs * c["n"][1]]
                cands.append(q)
            out[k] = {"cands": cands, "pick": v["pick"], "anchor": v.get("anchor", False)}
    return out


def main():
    p0 = {k: X.P[k][0] for k in FIGS}
    cat = T.catalogue()
    rows = [r for r in T.rd(ROOT / "research/xiyanglou/plate_keypoints.csv") if r["photo_id"] in PHOTOS and not r.get("use", "").startswith("skip")]
    base = points({})
    slopes = {}
    for k in FIGS:
        bumped = points({k: p0[k] + 1.0})
        slopes[k] = bumped
    data = []
    for pid in PHOTOS:
        mine = [r for r in rows if r["photo_id"] == pid]
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
            J = np.stack([T.resolve(slopes[k], C)[n][0] - P0 for k in FIGS], axis=1)
            lin[n] = (P0, J)
        obs = [(r["point"], float(r["x"]), float(r["y"]), r["sure"]) for r in mine if r["point"] in lin]
        cam0, _, _ = T.fit_camera({o[0]: (o[1], o[2], o[3]) for o in obs}, r0, size, pr, "all")
        data.append({"pid": pid, "size": size, "pr": pr, "obs": obs, "lin": lin, "cam0": cam0})
    keys = list(FIGS)
    nf = len(keys)

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
            out += [f[i] / FIGS[k] for i, k in enumerate(keys)]
        return np.array(out)

    t0 = np.concatenate([np.zeros(nf)] + [d["cam0"] for d in data])
    before = res(t0, prior=False)
    r = least_squares(res, t0, loss="soft_l1", f_scale=2.0, max_nfev=6000)
    f, cams = unpack(r.x)
    Jm = r.jac
    try:
        cov = np.linalg.inv(Jm.T @ Jm)
        se = np.sqrt(np.diag(cov))[:nf]
    except np.linalg.LinAlgError:
        se = np.full(nf, np.nan)
    out = {"photos": PHOTOS, "scale": "W 27.2 m (S01) and the octagons 61.8 m apart (S850) held", "figures": {}, "residuals": {}}
    for i, k in enumerate(keys):
        out["figures"][k] = {"prior": p0[k], "measured": round(p0[k] + float(f[i]), 2), "se": round(float(se[i]), 2), "prior_sd": FIGS[k]}
    for d, cam in zip(data, cams):
        e0, e1 = [], []
        for n, u, v, s in d["obs"]:
            P0, J = d["lin"][n]
            p, zc = T.project(d["cam0"], P0, d["size"])
            e0.append(math.hypot(p[0] - u, p[1] - v))
            p, zc = T.project(cam, P0 + J @ f, d["size"])
            e1.append(math.hypot(p[0] - u, p[1] - v))
        out["residuals"][d["pid"]] = {"n": len(e0), "rms_px_before": round(float(np.sqrt(np.mean(np.square(e0)))), 1), "rms_px_after": round(float(np.sqrt(np.mean(np.square(e1)))), 1), "f_px": round(math.exp(cam[5]), 0)}
    (HERE / "measure").mkdir(exist_ok=True)
    name = "measure_roofs.json" if "--roofs" in sys.argv else "measure.json"
    json.dump(out, open(HERE / "measure" / name, "w", encoding="utf-8"), indent=1)
    for k, v in out["figures"].items():
        print(f"{k:9s} prior {v['prior']:6.2f}  measured {v['measured']:6.2f} ± {v['se']:.2f}")
    for k, v in out["residuals"].items():
        print(k, v)


if __name__ == "__main__":
    main()
