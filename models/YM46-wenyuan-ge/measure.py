#!/usr/bin/env python3
"""文源阁 YM46: the storeys' heights measured on a photograph of its sister 文渊阁 (P0555), the 丈尺册's bays as the scale (Round 25).

  uv run python models/YM46-wenyuan-ge/measure.py

No picture of 文源阁 standing is known (Q122, Q125), and no figure for a height has been seen (Q287). Its sisters were built for the same books in the same years
on the same model (天一阁): 文渊阁 in the palace (1776) is the best kept, six bays with a narrow stair bay at the west, a gallery front and back, a skirt roof
between two storeys (twin T056). P0555 (Commons, CC BY-SA 4.0) shows its south front from the bridge before it: four front columns of the ground storey, the
skirt roof's drip line, the upper windows, the top eave. Its side bay against its 明间 is 0.78 on the picture where the façade is nearest the camera; 文源阁's
丈尺册 gives 4.00 / 5.12 = 0.78. So the picture is read in 文源阁's bays (west to east 1.60, 4.00, 4.00, 5.12, 4.00, 4.00 m: columns 2 to 5 at x -5.76, -1.76,
3.36, 7.36 m from the middle) and a pinhole camera is fitted jointly with five heights above the gallery floor: the columns' tops (under the beam), the skirt
roof's drip, the upper windows' sill and head, the top eave's drip. Lines (the drips, the sills, the heads) are measured across, as lines: only their
distance from the reading counts. The front of the upper storey is taken at the outer columns' line, the skirt's drip 1.5 m and the top eave's 1.0 m beyond
it (the model's; the drips' heights move about 0.1 m for each 0.5 m of projection, shown below).
What this measures is 文渊阁's proportion carried to 文源阁's bays: a twin's figure, grade C for 文源阁, never A or B. Writes measure.json beside this file.
"""

import csv
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from plate_overlay import basis  # noqa: E402

SIZE = (1280, 960)
HQ = 7.36                          # the outer columns' line from the middle (丈尺册: 3.52 + 7.68 / 2)
COLX = {"col2": -5.76, "col3": -1.76, "col4": 3.36, "col5": 7.36}
HEIGHTS = ["col_top", "skirt_drip", "win2_sill", "win2_head", "eave_drip"]
SIGMA = {"3": 2.0, "2": 3.0, "1": 5.0}


def project(cam, X):
    C, yaw, pitch, F = cam[:3], cam[3], cam[4], math.exp(cam[5])
    f, r, u = basis(yaw, pitch)
    d = np.asarray(X, float) - C
    zc = d @ f
    return np.array([SIZE[0] / 2 + F * (d @ r) / zc, SIZE[1] / 2 - F * (d @ u) / zc]), zc


def readings():
    """The rows of research/scenes/YM46-wenyuan-ge/plate_keypoints.csv for P0555: columns' feet and tops as points, the drips, sills and heads as lines."""
    rows = [r for r in csv.DictReader(open(ROOT / "research/scenes/YM46-wenyuan-ge/plate_keypoints.csv", encoding="utf-8")) if r["photo_id"] == "P0555"]  # the lines are `skip` for tools/plate_overlay.py, read here
    pts, lines = [], []
    for r in rows:
        n = r["point"]
        obs = (float(r["x"]), float(r["y"]), SIGMA.get(r["sure"], 4.0))
        m_ = re.match(r"lib_colS(\d)_(foot|top)$", n)
        if m_:
            pts.append((f"col{m_[1]}", m_[2], obs))
        elif n.startswith("lib_skS"):
            lines.append(("skirt_drip", "skirt", obs))
        elif n.startswith("lib_eaveS"):
            lines.append(("eave_drip", "eave", obs))
        elif n.startswith("lib_win2_sill"):
            lines.append(("win2_sill", "0", obs))
        elif n.startswith("lib_win2_head"):
            lines.append(("win2_head", "0", obs))
    return pts, lines


def residuals(t, pts, lines, sk_out, o2):
    cam, H = t[:6], dict(zip(HEIGHTS, t[6:]))
    out = []
    for col, what, (x, y, s) in pts:
        X = (COLX[col], 0.0 if what == "foot" else H["col_top"], HQ)
        p, zc = project(cam, X)
        out += [(p[0] - x) / s, (p[1] - y) / s] if zc > 0.5 else [100.0, 100.0]
    for h, zo, (x, y, s) in lines:
        z = HQ + {"skirt": sk_out, "eave": o2}.get(zo, 0.0)
        yy = H[h]
        a, _ = project(cam, (-12.0, yy, z))
        b, _ = project(cam, (12.0, yy, z))
        # the line's image y at the reading's x, measured across the line
        dx, dy = b - a
        n = np.array([-dy, dx]) / math.hypot(dx, dy)
        out.append(((np.array([x, y]) - a) @ n) / s)
    F0 = (SIZE[0] / 2) / math.tan(math.radians(29))  # an assumed lens (a phone of 2016, about 58 degrees across): a weak prior
    out.append((cam[5] - math.log(F0)) / 0.3)
    return np.array(out)


def fit(sk_out=1.5, o2=1.0):
    pts, lines = readings()
    t0 = np.array([0.5, -0.8, 25.0, 0.0, 0.25, math.log(1150.0), 3.5, 4.5, 6.0, 8.0, 9.5])
    best = None
    for zc in (15.0, 25.0, 40.0):
        for pitch in (0.15, 0.3):
            t = t0.copy()
            t[2], t[4] = zc, pitch
            t[3] = 0.0  # facing north (-z): yaw as plate_overlay.basis reads it (forward = (sin yaw, ., -cos yaw))
            r = least_squares(residuals, t, args=(pts, lines, sk_out, o2), loss="soft_l1", f_scale=2.0, max_nfev=6000)
            if best is None or r.cost < best.cost:
                best = r
    res = residuals(best.x, pts, lines, sk_out, o2)[:-1]
    sig = [o[2] for _, _, o in pts for _ in (0, 1)] + [o[2] for _, _, o in lines]
    px = np.abs(res * np.array(sig))
    return best.x, float(np.sqrt(np.mean(px ** 2))), float(np.max(px)), len(pts), len(lines)


def main():
    out = {"photo": "P0555", "building": "文渊阁 (twin T056), read in 文源阁's bays (S105)", "cases": []}
    for sk_out, o2 in ((1.5, 1.0), (1.0, 1.0), (2.0, 1.5)):
        t, rms, mx, n_p, n_l = fit(sk_out, o2)
        H = {k: round(float(v), 2) for k, v in zip(HEIGHTS, t[6:])}
        cam = {"C": [round(float(c), 2) for c in t[:3]], "yaw_deg": round(math.degrees(t[3]), 1), "pitch_deg": round(math.degrees(t[4]), 1), "hfov_deg": round(2 * math.degrees(math.atan(SIZE[0] / 2 / math.exp(t[5]))), 1)}
        out["cases"].append({"skirt_out_m": sk_out, "eave_out_m": o2, "heights_m": H, "camera": cam, "rms_px": round(rms, 2), "max_px": round(mx, 2), "points": n_p, "line_readings": n_l})
        print(f"skirt {sk_out} eave {o2}: {H}  rms {rms:.2f} px (max {mx:.2f}); camera {cam}")
    json.dump(out, open(HERE / "measure.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
