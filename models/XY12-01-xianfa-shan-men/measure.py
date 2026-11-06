#!/usr/bin/env python3
"""The walls of 线法山门 measured as lines on plate 17 (Round 30), by the camera fitted to the gate's own points (research/xiyanglou/plate_cameras_XY12-01.json).

Plate 17 draws a panelled wall from each end of the gate to the sheet's edge, its top falling towards the gate; the feet are behind the clipped trees. The wall is read as a
line: points sampled along its coping (Round 30 readings, below), and for each splay angle off the gate's line and each height the rms distance of the samples from the
projected coping. The angle with the least distance is the plate's vote; S01 draws the hill's west wall straight north-south (0 degrees). Writes measure.json beside this file.

  uv run python models/XY12-01-xianfa-shan-men/measure.py
"""

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from plate_overlay import project  # noqa: E402

# the coping's top on plate 17 (P0057, 2400 x 1393), read at 1.7x (Round 30); x from the sheet's edges to where the hedge meets the gate's scroll
TOP_L = [(50, 812), (300, 829), (560, 846), (790, 860)]
TOP_R = [(1600, 857), (1800, 848), (2000, 835), (2200, 822), (2370, 812)]


def cam_vec(f):
    return np.array([*f["position"], math.radians(f["yaw_deg"]), math.radians(f["pitch_deg"]), math.log(f["f_px"]), f["du_px"], f["dv_px"]])


def seg_dist(p, a, b):
    ab = b - a
    t = np.clip((p - a) @ ab / (ab @ ab), 0.0, 1.0)
    return float(np.linalg.norm(p - (a + t * ab)))


def main():
    summ = json.load(open(HERE / "summary.json", encoding="utf-8"))
    pos, rot = summ["position"], summ["rotationY"]
    c, s = math.cos(rot), math.sin(rot)
    to_scene = lambda x, y, z: np.array([pos[0] + c * x + s * z, pos[1] + y, pos[2] - s * x + c * z])
    cams = json.load(open(ROOT / "research/xiyanglou/plate_cameras_XY12-01.json", encoding="utf-8"))["cameras"]["P0057"]
    size = cams["size"]
    params = json.load(open(HERE / "params.json", encoding="utf-8"))["params"]
    hw = params["w"]["value"] / 2
    out = {"samples": {"L": TOP_L, "R": TOP_R}, "runs": []}
    for fit in ("anchored", "all"):
        cam = cam_vec(cams["fits"][fit])
        best = None
        for ang in range(-40, 85, 5):
            for h in (2.4, 2.7, 3.0, 3.3):
                errs = []
                for sx, samples in ((-1, TOP_L), (1, TOP_R)):
                    a = (sx * (hw + 0.55), -0.9)
                    u = (sx * math.cos(math.radians(ang)), math.sin(math.radians(ang)))
                    pts = [project(cam, to_scene(a[0] + u[0] * L, h, a[1] + u[1] * L), size) for L in np.linspace(0, 60, 61)]
                    img = [p for p, zc in pts if zc > 1.0]
                    for q in samples:
                        q = np.array(q, float)
                        errs.append(min(seg_dist(q, img[i], img[i + 1]) for i in range(len(img) - 1)))
                rms = float(np.sqrt(np.mean(np.square(errs))))
                out["runs"].append({"fit": fit, "splay_deg": ang, "wall_h": h, "rms_px": round(rms, 1), "max_px": round(max(errs), 1)})
                if best is None or rms < best[0]:
                    best = (rms, ang, h)
        out[f"best_{fit}"] = {"rms_px": round(best[0], 1), "splay_deg": best[1], "wall_h": best[2]}
        straight = min((r for r in out["runs"] if r["fit"] == fit and r["splay_deg"] == 0), key=lambda r: r["rms_px"])
        out[f"straight_{fit}"] = straight
        print(f"{fit}: best splay {best[1]} deg, wall {best[2]} m, {best[0]:.1f} px rms; S01's straight line {straight['rms_px']} px (wall {straight['wall_h']} m)")
    json.dump(out, open(HERE / "measure.json", "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
