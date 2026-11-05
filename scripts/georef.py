"""Georeference the Princeton plan (S01) on today's landscape.

Round 8 (the fit in use): reads the control points of Round 1 (research/georef/princeton-1920s.csv) and of
Round 8 (research/georef/control_r8.csv), fits in UTM 50N (EPSG:32650) a plain affine and thin-plate splines
with a smoothness limit set per garden region by leave-one-out, scores them on the frozen blind check set
(research/georef/check_points.json, never edited after it was frozen) against the Round 1 fit, keeps the Round 1
fit in any region where the new one does worse on the check set, and stores the result in
research/georef/princeton-1920s.json. The Round 1 fit stays beside it as princeton-1920s.previous.json. All
figures in both files come from runs of this script.

Import (numpy and pyproj only):

    from georef import plan_to_wgs84, wgs84_to_plan
    lons, lats = plan_to_wgs84(xs, ys)   # plan_x, plan_y = pixels on research/raw/plans/princeton_mosaic.jpg
    xs, ys = wgs84_to_plan(lons, lats)

Commands:

    python scripts/georef.py fit        Round 8: compare transforms, score them on the check set, write the JSON
    python scripts/georef.py previous   rebuild the Round 1 fit from princeton-1920s.csv alone (princeton-1920s.previous.json)
    python scripts/georef.py freeze     hash the check set once, before any fit sees it (refuses to run twice)
    python scripts/georef.py accuracy   research/layers/georef_error.geojson: expected error by region and grid cell, from the check set
    python scripts/georef.py overlay    warp the mosaic to research/overlays/princeton-1920s.jpg + .json
    python scripts/georef.py images     screenshots/r8/georef_residuals.png (no plan image, public-safe) and georef_overlay.jpg (local)
"""

import csv
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
from pyproj import Transformer

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "research/georef/princeton-1920s.csv"
CONTROL_R8 = ROOT / "research/georef/control_r8.csv"
CONTROL_SHAPES = ROOT / "research/georef/control_shapes.csv"
CHECK_PATH = ROOT / "research/georef/check_points.json"
JSON_PATH = ROOT / "research/georef/princeton-1920s.json"
PREVIOUS_PATH = ROOT / "research/georef/princeton-1920s.previous.json"
ERROR_LAYER = ROOT / "research/layers/georef_error.geojson"
WALLS_PLAN = ROOT / "research/plan/walls.json"
MOSAIC = ROOT / "research/raw/plans/princeton_mosaic.jpg"
OVERLAY = ROOT / "research/overlays/princeton-1920s.jpg"
OSM = ROOT / "research/layers/osm_today.geojson"
SHOTS = ROOT / "screenshots/r8"
PREVIOUS_DATE = "2026-10-31"  # the Round 1 fit; fixed so a rebuild gives the same file
FIT_DATE = "2026-11-05"  # Round 8

_TO_UTM = Transformer.from_crs(4326, 32650, always_xy=True)
_TO_LL = Transformer.from_crs(32650, 4326, always_xy=True)

# Scroll gaps on the mosaic, used only by the per-scroll test.
SEAMS = (4305.0, 8640.0)
# Coordinates are normalised for numerical stability: plan pixels and metres both in thousands.
UNIT_PX = 1000.0
UNIT_M = 200.0
AREAS = ("YM-west", "YM-houhu", "YM-fuhai", "CC-lakes", "XYL", "QC", "walls")


# --------------------------------------------------------------- transforms


def _tps_kernel(r2):
    with np.errstate(divide="ignore", invalid="ignore"):
        k = 0.5 * r2 * np.log(r2)
    return np.nan_to_num(k, nan=0.0, posinf=0.0, neginf=0.0)


def _design(kind, x, y):
    """Polynomial design matrix. Plan y is flipped so that all terms are in a right-handed frame."""
    if kind == "affine":
        return np.c_[np.ones_like(x), x, y]
    if kind == "poly2":
        return np.c_[np.ones_like(x), x, y, x * x, x * y, y * y]
    if kind == "poly3":
        return np.c_[np.ones_like(x), x, y, x * x, x * y, y * y, x**3, x * x * y, x * y * y, y**3]
    raise ValueError(kind)


class Fit:
    """A plan -> UTM mapping. Inputs and outputs in plan pixels and metres."""

    def __init__(self, kind, params, x0, y0, e0, n0):
        self.kind, self.params = kind, params
        self.x0, self.y0, self.e0, self.n0 = x0, y0, e0, n0

    def _norm(self, x, y):
        return (np.asarray(x, float) - self.x0) / UNIT_PX, -(np.asarray(y, float) - self.y0) / UNIT_PX

    def __call__(self, x, y):
        x, y = self._norm(x, y)
        shape = x.shape
        x, y = x.ravel(), y.ravel()
        p = self.params
        if self.kind == "similarity":
            a, b, c, d = p["coef"]
            e = a * x - b * y + c
            n = b * x + a * y + d
        elif self.kind in ("affine", "poly2", "poly3"):
            g = _design(self.kind, x, y)
            e, n = g @ np.array(p["coef_e"]), g @ np.array(p["coef_n"])
        elif self.kind == "tps":
            cen = np.array(p["centers"])
            w = np.array(p["weights"])
            a = np.array(p["affine"])
            e, n = np.empty_like(x), np.empty_like(x)
            step = max(1000, 4_000_000 // max(1, len(cen)))  # about 32 MB of kernel at a time
            for s in range(0, len(x), step):
                xs, ys = x[s : s + step], y[s : s + step]
                k = _tps_kernel((xs[:, None] - cen[:, 0]) ** 2 + (ys[:, None] - cen[:, 1]) ** 2)
                g = np.c_[np.ones_like(xs), xs, ys]
                e[s : s + step] = k @ w[:, 0] + g @ a[:, 0]
                n[s : s + step] = k @ w[:, 1] + g @ a[:, 1]
        else:
            raise ValueError(self.kind)
        return (e * UNIT_M + self.e0).reshape(shape), (n * UNIT_M + self.n0).reshape(shape)

    def to_dict(self):
        return {"kind": self.kind, "params": self.params, "origin": [self.x0, self.y0, self.e0, self.n0]}

    @classmethod
    def from_dict(cls, d):
        return cls(d["kind"], d["params"], *d["origin"])


def fit(kind, x, y, e, n, lam=0.0, weights=None):
    """Least squares fit. weights: per-point weights for polynomials; for TPS the inverse scales the smoothing."""
    x0, y0, e0, n0 = float(x.mean()), float(y.mean()), float(e.mean()), float(n.mean())
    f = Fit(kind, {}, x0, y0, e0, n0)
    xn, yn = f._norm(x, y)
    en, nn = (e - e0) / UNIT_M, (n - n0) / UNIT_M
    w = np.ones_like(x) if weights is None else weights
    if kind == "similarity":
        m = np.zeros((2 * len(x), 4))
        m[::2] = np.c_[xn, -yn, np.ones_like(xn), np.zeros_like(xn)]
        m[1::2] = np.c_[yn, xn, np.zeros_like(xn), np.ones_like(xn)]
        rhs = np.empty(2 * len(x))
        rhs[::2], rhs[1::2] = en, nn
        ww = np.repeat(np.sqrt(w), 2)
        f.params = {"coef": np.linalg.lstsq(m * ww[:, None], rhs * ww, rcond=None)[0].tolist()}
    elif kind in ("affine", "poly2", "poly3"):
        g = _design(kind, xn, yn)
        sw = np.sqrt(w)[:, None]
        f.params = {
            "coef_e": np.linalg.lstsq(g * sw, en * sw[:, 0], rcond=None)[0].tolist(),
            "coef_n": np.linalg.lstsq(g * sw, nn * sw[:, 0], rcond=None)[0].tolist(),
        }
    elif kind == "tps":
        k = _tps_kernel((xn[:, None] - xn[None]) ** 2 + (yn[:, None] - yn[None]) ** 2)
        k = k + np.diag(lam / w)
        g = np.c_[np.ones_like(xn), xn, yn]
        m = np.block([[k, g], [g.T, np.zeros((3, 3))]])
        rhs = np.zeros((len(x) + 3, 2))
        rhs[: len(x), 0], rhs[: len(x), 1] = en, nn
        sol = np.linalg.solve(m, rhs)
        f.params = {
            "lambda": lam,
            "centers": np.c_[xn, yn].tolist(),
            "weights": sol[: len(x)].tolist(),
            "affine": sol[len(x) :].tolist(),
        }
    else:
        raise ValueError(kind)
    return f


class Panels:
    """One transform per scroll (test of the gaps). Discontinuous at the seams by design."""

    def __init__(self, fits):
        self.fits = fits

    def __call__(self, x, y):
        x, y = np.asarray(x, float), np.asarray(y, float)
        e, n = np.empty_like(x), np.empty_like(x)
        p = _panel(x)
        for i, f in enumerate(self.fits):
            m = p == i
            if m.any():
                e[m], n[m] = f(x[m], y[m])
        return e, n


def _panel(x):
    return np.digitize(x, SEAMS)


def _rms(dx, dy):
    return float(np.sqrt(np.mean(dx**2 + dy**2))) if len(dx) else None


# --------------------------------------------------------------- control points


def read_points(path=CSV_PATH):
    with open(path, encoding="utf8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["plan_x"], r["plan_y"] = float(r["plan_x"]), float(r["plan_y"])
        r["lat"], r["lon"] = float(r["lat"]), float(r["lon"])
        r["quality"] = int(r["quality"])
        r["use"] = (r.get("use") or "fit").strip()
    return rows


def _arrays(rows):
    x = np.array([r["plan_x"] for r in rows])
    y = np.array([r["plan_y"] for r in rows])
    e, n = _TO_UTM.transform(np.array([r["lon"] for r in rows]), np.array([r["lat"] for r in rows]))
    return x, y, np.asarray(e), np.asarray(n)


def _weights(rows, q2):
    return np.array([1.0 if r["quality"] == 1 else q2 for r in rows])


def _fitter(spec):
    """spec: dict(name, kind, lam, panels, q2). Returns f(x, y, e, n, w) -> mapping."""

    def run(x, y, e, n, w):
        if spec.get("panels"):
            p, fits = _panel(x), []
            for i in range(3):
                m = p == i
                fits.append(fit(spec["kind"], x[m], y[m], e[m], n[m], spec.get("lam", 0.0), w[m]))
            return Panels(fits)
        return fit(spec["kind"], x, y, e, n, spec.get("lam", 0.0), w)

    return run


def evaluate(spec, rows):
    """Residuals (model minus control point, metres) of the fit and of leave-one-out."""
    x, y, e, n = _arrays(rows)
    w = _weights(rows, spec.get("q2", 1.0))
    run = _fitter(spec)
    pe, pn = run(x, y, e, n, w)(x, y)
    res = np.c_[pe - e, pn - n]
    loo = np.empty_like(res)
    for i in range(len(x)):
        keep = np.arange(len(x)) != i
        try:
            ee, nn = run(x[keep], y[keep], e[keep], n[keep], w[keep])(x[i:i + 1], y[i:i + 1])
            loo[i] = ee[0] - e[i], nn[0] - n[i]
        except (np.linalg.LinAlgError, ValueError):
            loo[i] = np.nan, np.nan
    return res, loo


def _per_area(rows, res, loo):
    out = {}
    areas = np.array([r["area"] for r in rows])
    for a in AREAS:
        m = areas == a
        if m.any():
            out[a] = {
                "n": int(m.sum()),
                "rms_m": round(_rms(res[m, 0], res[m, 1]), 1),
                "loo_rms_m": round(_rms(loo[m, 0], loo[m, 1]), 1),
                "loo_median_m": round(float(np.median(np.hypot(loo[m, 0], loo[m, 1]))), 1),
            }
    return out


SPECS = [
    {"name": "similarity", "kind": "similarity"},
    {"name": "affine", "kind": "affine"},
    {"name": "poly2", "kind": "poly2"},
    {"name": "poly3", "kind": "poly3"},
    {"name": "affine per scroll", "kind": "affine", "panels": True},
    {"name": "poly2 per scroll", "kind": "poly2", "panels": True},
    {"name": "tps lam=0", "kind": "tps", "lam": 0.0},
    {"name": "tps lam=0.01", "kind": "tps", "lam": 0.01},
    {"name": "tps lam=0.03", "kind": "tps", "lam": 0.03},
    {"name": "tps lam=0.1", "kind": "tps", "lam": 0.1},
    {"name": "tps lam=0.3", "kind": "tps", "lam": 0.3},
    {"name": "tps lam=1", "kind": "tps", "lam": 1.0},
    {"name": "tps lam=3", "kind": "tps", "lam": 3.0},
    {"name": "tps lam=10", "kind": "tps", "lam": 10.0},
    {"name": "tps lam=0.3 q2 half", "kind": "tps", "lam": 0.3, "q2": 0.5},
    {"name": "tps lam=1 q2 half", "kind": "tps", "lam": 1.0, "q2": 0.5},
    {"name": "tps lam=0.3 per scroll", "kind": "tps", "lam": 0.3, "panels": True},
    {"name": "tps lam=1 per scroll", "kind": "tps", "lam": 1.0, "panels": True},
]


def affine_summary(rows):
    """Scale and rotation of the plan: the same data as a similarity, plus the two scales of an affine."""
    x, y, e, n = _arrays(rows)
    s = fit("similarity", x, y, e, n)
    a, b = s.params["coef"][:2]
    m_per_px = float(np.hypot(a, b)) * UNIT_M / UNIT_PX
    a2 = fit("affine", x, y, e, n)
    lin = np.array([a2.params["coef_e"][1:3], a2.params["coef_n"][1:3]]) * UNIT_M / UNIT_PX
    sv = np.linalg.svd(lin, compute_uv=False)
    return {
        "similarity_px_per_m": round(1 / m_per_px, 3),
        "similarity_m_per_px": round(m_per_px, 4),
        "similarity_rotation_deg": round(float(np.degrees(np.arctan2(b, a))), 2),
        "affine_px_per_m_along_plan_x": round(float(1 / np.linalg.norm(lin[:, 0])), 3),
        "affine_px_per_m_along_plan_y": round(float(1 / np.linalg.norm(lin[:, 1])), 3),
        "affine_singular_px_per_m": [round(float(1 / v), 3) for v in sv],
    }


# What the eye saw on the chips; the numbers beside it come from the run.
AREA_NOTES = {
    "YM-west": "Few surviving shapes; many ditches are modern. No anchor on the plain x 700-1500, y 3500-5600, in the north-west fields, or at the north-west and south-west corners. Pond outlines look schematic.",
    "YM-houhu": "后湖, 前湖 and the 曲院风荷 lake match in size and shape.",
    "YM-fuhai": "Shore outline matches; the 蓬岛瑶台 islands match closely. The north shore points are less sure.",
    "CC-lakes": "Closest fit: 含经堂 enclosure, 海岳开襟 and 玉玲珑馆 islands. No independent check here.",
    "XYL": "Buildings keep their east-west order. One independent check only, read off the axis, so this rests on leave-one-out.",
    "QC": "East lake fits well, west part less so. Schematic in places: the 鉴碧亭 island is drawn round and is square today, and 正觉寺 is drawn narrower than its surviving walls. These lakes were re-dug in modern times (assumed, not checked), so shore points may not be original.",
    "walls": "Short fragments and modern roads assumed to follow the old line. Weakest area: no independent check, both western corners unanchored.",
}


def _verdicts(per_area, checks, block):
    out = {}
    for a in AREAS:
        pa = per_area.get(a)
        if not pa:
            continue
        c = [p["dist_m"] for p in checks if p["area"] == a]
        check_med = float(np.median(c)) if c else None
        blk = block["per_area_rms_m"].get(a)
        # Reads to: the largest of the three figures, rounded up to 5 m.
        base = max(pa["loo_rms_m"], check_med or 0.0, blk or 0.0)
        out[a] = {
            "reads_to_plus_minus_m": int(np.ceil(base / 5.0) * 5),
            "loo_rms_m": pa["loo_rms_m"],
            "block_cv_rms_m": blk,
            "check_median_m": None if check_med is None else round(check_med, 1),
            "check_n": len(c),
            "note": AREA_NOTES[a],
        }
    return out


def _check(model, rows):
    """Distance from the model to points that were not in the fit."""
    if not rows:
        return []
    cx, cy, ce, cn = _arrays(rows)
    pe, pn = model(cx, cy)
    return [
        {"id": r["id"], "feature": r["feature"], "area": r["area"], "dE_m": round(float(a), 1), "dN_m": round(float(b), 1), "dist_m": round(float(np.hypot(a, b)), 1)}
        for r, a, b in zip(rows, pe - ce, pn - cn)
    ]


def _check_stats(points):
    if not points:
        return {"n": 0, "rms_m": None, "median_m": None}
    d = np.array([p["dist_m"] for p in points])
    return {"n": len(points), "rms_m": round(float(np.sqrt(np.mean(d**2))), 1), "median_m": round(float(np.median(d)), 1)}


def block_cv(spec, rows, block_px=1500.0):
    """Hold out whole squares of the plan (about 300 m): the error far from any control point."""
    x, y, e, n = _arrays(rows)
    w = _weights(rows, spec.get("q2", 1.0))
    run = _fitter(spec)
    blocks = (x // block_px).astype(int) * 1000 + (y // block_px).astype(int)
    out = np.full((len(x), 2), np.nan)
    for b in np.unique(blocks):
        m = blocks == b
        pe, pn = run(x[~m], y[~m], e[~m], n[~m], w[~m])(x[m], y[m])
        out[m] = np.c_[pe - e[m], pn - n[m]]
    areas = np.array([r["area"] for r in rows])
    d = np.hypot(out[:, 0], out[:, 1])
    res = {"block_px": block_px, "rms_m": round(_rms(out[:, 0], out[:, 1]), 1), "median_m": round(float(np.median(d)), 1), "per_area_rms_m": {}}
    for a in AREAS:
        if (areas == a).any():
            res["per_area_rms_m"][a] = round(_rms(out[areas == a, 0], out[areas == a, 1]), 1)
    return res


def seam_test(rows):
    """Is there a jump at the scroll gaps? Step terms on a global polynomial, and two local affines per seam."""
    x, y, e, n = _arrays(rows)
    xn, yn = (x - x.mean()) / UNIT_PX, -(y - y.mean()) / UNIT_PX
    out = {"polynomial_steps": {}, "local_affine_gap_m": {}}
    for kind in ("poly2", "poly3"):
        g = np.c_[_design(kind, xn, yn), x > SEAMS[0], x > SEAMS[1]].astype(float)
        for label, v in (("E", e - e.mean()), ("N", n - n.mean())):
            c = np.linalg.lstsq(g, v, rcond=None)[0]
            r = v - g @ c
            cov = (r @ r / (len(v) - g.shape[1])) * np.linalg.inv(g.T @ g)
            for i, seam in zip((-2, -1), SEAMS):
                out["polynomial_steps"][f"{kind} {label} x={seam:.0f}"] = {"jump_m": round(float(c[i]), 1), "se_m": round(float(cov[i, i] ** 0.5), 1)}
    for seam in SEAMS:
        for label, v in (("E", e), ("N", n)):
            vals = []
            for side in (-1, 1):
                m = ((x - seam) * side > 0) & (np.abs(x - seam) < 1500)
                g = np.c_[np.ones(m.sum()), x[m] - seam, y[m] - 4000.0]
                vals.append(np.linalg.lstsq(g, v[m], rcond=None)[0][0])
            out["local_affine_gap_m"][f"{label} x={seam:.0f}"] = round(float(vals[1] - vals[0]), 1)
    return out


def _spec_label(spec):
    return spec["name"]


def run_fit_previous(out_path=PREVIOUS_PATH):
    """The Round 1 fit, rebuilt from princeton-1920s.csv alone; kept beside the Round 8 fit as `previous`."""
    rows = read_points()
    used = [r for r in rows if r["use"] == "fit"]
    comparison, best = [], None
    for spec in SPECS:
        res, loo = evaluate(spec, used)
        d = np.hypot(loo[:, 0], loo[:, 1])
        ok = np.isfinite(d)
        item = {
            "name": _spec_label(spec),
            "rms_m": round(_rms(res[:, 0], res[:, 1]), 1),
            "loo_rms_m": round(_rms(loo[ok, 0], loo[ok, 1]), 1),
            "loo_median_m": round(float(np.median(d[ok])), 1),
            "per_area": _per_area(used, res, loo),
        }
        comparison.append(item)
        # A per-scroll model would break continuity at the seams, so it must beat the continuous ones clearly.
        score = item["loo_rms_m"] + (3.0 if spec.get("panels") else 0.0)
        if best is None or score < best[0]:
            best = (score, spec, res, loo, item)
    _, spec, res, loo, item = best
    x, y, e, n = _arrays(used)
    w = _weights(used, spec.get("q2", 1.0))
    model = _fitter(spec)(x, y, e, n, w)
    if isinstance(model, Panels):
        tr = {"type": "panels", "seams": SEAMS, "fits": [f.to_dict() for f in model.fits]}
    else:
        tr = {"type": "single", "fit": model.to_dict()}
    tr["name"] = spec["name"]
    # Linear part of the inverse, used as the fixed-point step of wgs84_to_plan.
    a = fit("affine", x, y, e, n)
    lin = np.array([a.params["coef_e"][1:3], a.params["coef_n"][1:3]]) * UNIT_M / UNIT_PX
    lin = lin @ np.diag([1.0, -1.0])
    tr["inverse_step"] = np.linalg.inv(lin).tolist()
    # Independent check points: never used in the fit.
    checks = _check(model, [r for r in rows if r["use"] == "check"])
    first = _check(model, [r for r in rows if r["use"] == "check-first-pass"])
    shape_ids = ("CHK-XY11", "CHK-islet-NW", "CHK-islet-E", "CHK-canqiao")
    block = block_cv(spec, used)
    verdict = _verdicts(item["per_area"], checks, block)
    rejected = [{"id": r["id"], "feature": r["feature"], "reason": r.get("note", "")} for r in rows if r["use"] == "rejected"]
    out = {
        "plan": "S01",
        "source": "Plan of the Yuanmingyuan Imperial Garden-Palace, Princeton University Art Museum 2022-27 a-c",
        "mosaic": "research/raw/plans/princeton_mosaic.jpg",
        "pixel_frame": "plan_x, plan_y: pixels on the mosaic, origin top-left",
        "datum": "control points WGS84 (EPSG:4326); fitted in UTM 50N (EPSG:32650)",
        "date": PREVIOUS_DATE,
        "n_points": len(used),
        "n_by_area": {a: sum(r["area"] == a for r in used) for a in AREAS},
        "global_scale": affine_summary(used),
        "transform": tr,
        "chosen": item,
        "comparison": comparison,
        "independent_check": {
            "warning": "Not a blind test. The kept set was edited after seeing errors: plan positions re-read on a sheet that marked the prediction, 3 large misses dropped (see rejected). first_pass is the unedited first reading; it includes misreadings of the plan, so it is an upper bound.",
            "points": checks,
            **_check_stats(checks),
            "on_shapes": _check_stats([c for c in checks if c["id"] in shape_ids]),
            "on_osm_labels": _check_stats([c for c in checks if c["id"] not in shape_ids]),
            "first_pass": {**_check_stats(first), "points": first},
        },
        "block_cross_validation": block,
        "seam_test": seam_test(used),
        "per_area_verdict": verdict,
        "rejected": rejected,
        "residuals": [
            {
                "id": r["id"], "area": r["area"], "kind": r["kind"], "quality": r["quality"],
                "dE_m": round(float(a1[0]), 1), "dN_m": round(float(a1[1]), 1),
                "loo_dE_m": round(float(b1[0]), 1), "loo_dN_m": round(float(b1[1]), 1),
                "loo_m": round(float(np.hypot(*b1)), 1),
            }
            for r, a1, b1 in zip(used, res, loo)
        ],
    }
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf8")
    print(f"{'transform':28s} {'rms':>7s} {'LOO':>7s} {'LOOmed':>7s}  LOO per area")
    for c in comparison:
        pa = " ".join(f"{k}:{v['loo_rms_m']:.0f}" for k, v in c["per_area"].items())
        print(f"{c['name']:28s} {c['rms_m']:7.1f} {c['loo_rms_m']:7.1f} {c['loo_median_m']:7.1f}  {pa}")
    print("chosen:", item["name"], "| scale:", out["global_scale"])
    if checks:
        ic = out["independent_check"]
        print("check kept:", ic["n"], ic["rms_m"], "rms", ic["median_m"], "median | shapes", ic["on_shapes"], "| labels", ic["on_osm_labels"], "| first pass", ic["first_pass"]["n"], ic["first_pass"]["rms_m"], ic["first_pass"]["median_m"])
    return out


# --------------------------------------------------------------- Round 8: regions, check set, piecewise fit

# The six regions the accuracy is reported by, as rules on plan pixels (the plan's own frame, so a rule never moves
# with the fit). Lines: x 2800 west of the nine islands; x 5300 west of 福海's west shore scenes; x 8640 the wall
# between Yuanming Yuan and Changchun Yuan (the middle scroll's seam is there too); y 1150 the Xiyang Lou strip's
# south edge; y 4600-4650 and 4950 the walls between Qichun Yuan and the two others (plan/walls.json W02, W03).
REGIONS = ("YM-west", "YM-east", "YM-fuhai", "CC", "XYL", "QC")
REGION_NAMES = {"YM-west": "Yuan Ming Yuan, west", "YM-east": "Yuan Ming Yuan, east and the nine islands", "YM-fuhai": "福海 Fuhai and its shores", "CC": "Changchun Yuan", "XYL": "The Xiyang Lou strip", "QC": "Qichun Yuan"}
REGION_NOTES = {
    "YM-west": "Yuan Ming Yuan west of the nine islands: the plain of 山高水长, 安佑宫, the west wall. The plan is schematic here (Q8) and many ponds were dug or filled after 1950.",
    "YM-east": "Yuan Ming Yuan from the nine islands round 后湖 to 福海's west shore scenes: 前湖, the 正大光明 axis, 舍卫城.",
    "YM-fuhai": "福海 and its shore scenes, up to the wall with Changchun Yuan.",
    "CC": "Changchun Yuan without the Xiyang Lou strip: its lakes, 含经堂, the south and east walls.",
    "XYL": "The Xiyang Lou strip on Changchun Yuan's north edge; ruins read on today's imagery.",
    "QC": "Qichun Yuan; its lakes were re-dug in modern times.",
}
EXCLUDE_M = 60.0  # a control point this close to a check point on the ground stays out of every fit (check_points.json "rule")
LAM_GRID = (0.03, 0.1, 0.3, 1.0, 3.0, 10.0)  # TPS smoothing, in the normalised units of fit(); Round 1 chose 1.0
Q2_WEIGHT = 0.5  # quality 2 points count half, as in Round 1
PIN_STEP_PX = 240.0  # spacing of the points that hold a region to the previous fit (about 50 m)
PIN_LAM = 0.03


def region_of(x, y):
    """Region code of plan pixels, by the rules above."""
    x, y = np.atleast_1d(np.asarray(x, float)), np.atleast_1d(np.asarray(y, float))
    out = np.empty(x.shape, object)
    east = x >= 8640
    cc_bottom = np.where(x < 10350, 4650.0, 4950.0)
    out[east & (y < 1150)] = "XYL"
    out[east & (y >= 1150) & (y < cc_bottom)] = "CC"
    out[east & (y >= cc_bottom)] = "QC"
    west = ~east
    qc = west & (x >= 5200) & (y >= 4600)
    out[qc] = "QC"
    rest = west & ~qc
    out[rest & (x >= 5300)] = "YM-fuhai"
    out[rest & (x >= 2800) & (x < 5300)] = "YM-east"
    out[rest & (x < 2800)] = "YM-west"
    return out


def region_polygons():
    """The regions as plan-pixel polygons, clipped to the wall rings with a margin of about 60 m."""
    from shapely.geometry import Polygon, box
    from shapely.ops import unary_union

    W, H = 12955, 9049
    rules = {
        "XYL": [box(8640, 0, W, 1150)],
        "CC": [box(8640, 1150, 10350, 4650), box(10350, 1150, W, 4950)],
        "QC": [box(8640, 4650, 10350, H), box(10350, 4950, W, H), box(5200, 4600, 8640, H)],
        "YM-fuhai": [box(5300, 0, 8640, 4600)],
        "YM-east": [box(2800, 0, 5300, 4600), box(2800, 4600, 5200, H)],
        "YM-west": [box(0, 0, 2800, H)],
    }
    rings = json.loads(WALLS_PLAN.read_text(encoding="utf8"))
    garden = unary_union([Polygon(w["points"]).buffer(0) for w in rings if w["kind"] == "outer_wall"]).buffer(300)
    return {k: unary_union(v).intersection(garden) for k, v in rules.items()}


def _sha(points):
    canon = json.dumps(points, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf8")).hexdigest()


def read_check():
    """The frozen check set; stops if its points no longer match the hash written when it was frozen."""
    d = json.loads(CHECK_PATH.read_text(encoding="utf8"))
    if d.get("sha256") != _sha(d["points"]):
        raise SystemExit("check_points.json: the points no longer match the frozen hash. The check set is never edited; annotate in 'annotations' instead.")
    return d


def run_freeze():
    d = json.loads(CHECK_PATH.read_text(encoding="utf8"))
    if d.get("sha256"):
        raise SystemExit("already frozen: " + d["sha256"])
    d["sha256"] = _sha(d["points"])
    d["frozen"] = FIT_DATE
    CHECK_PATH.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf8")
    print("frozen", len(d["points"]), "points", d["sha256"])


def read_control():
    """Round 1 and Round 8 control points with use=fit (read by eye: control_r8.csv; derived by script: control_shapes.csv).
    A Round 8 point within EXCLUDE_M of a check point is left out, whatever its file says."""
    rows = [dict(r, round="r1") for r in read_points() if r["use"] == "fit"]
    excluded = []
    chk = read_check()["points"] if CHECK_PATH.exists() else []
    ce, cn = _TO_UTM.transform(np.array([p["lon"] for p in chk], float), np.array([p["lat"] for p in chk], float))
    ce, cn = np.atleast_1d(ce), np.atleast_1d(cn)
    for path in (CONTROL_R8, CONTROL_SHAPES):
        if not path.exists():
            continue
        for r in read_points(path):
            e, n = _TO_UTM.transform(r["lon"], r["lat"])
            d = np.hypot(ce - e, cn - n) if len(chk) else np.array([np.inf])
            if r["use"] != "fit" or d.min() < EXCLUDE_M:
                why = r.get("note") or r["use"]
                if d.min() < EXCLUDE_M:
                    why = f"{d.min():.0f} m from check point {chk[int(d.argmin())]['id']}"
                excluded.append({"id": r["id"], "feature": r["feature"], "reason": why})
                continue
            rows.append(dict(r, round="r8"))
    for r in rows:
        r["region"] = str(region_of(r["plan_x"], r["plan_y"])[0])
    return rows, excluded


def _tps(x, y, e, n, lam_pt, qw):
    return fit("tps", x, y, e, n, 1.0, qw / lam_pt)


def _loo(x, y, e, n, lam_pt, qw, idx=None):
    """Leave-one-out residuals (model minus point, metres) of the TPS, for the points in idx (all by default)."""
    idx = np.arange(len(x)) if idx is None else idx
    out = np.full((len(x), 2), np.nan)
    for i in idx:
        keep = np.arange(len(x)) != i
        pe, pn = _tps(x[keep], y[keep], e[keep], n[keep], lam_pt[keep], qw[keep])(x[i:i + 1], y[i:i + 1])
        out[i] = pe[0] - e[i], pn[0] - n[i]
    return out


def _loo_affine(x, y, e, n, qw):
    out = np.empty((len(x), 2))
    for i in range(len(x)):
        keep = np.arange(len(x)) != i
        pe, pn = fit("affine", x[keep], y[keep], e[keep], n[keep], 0.0, qw[keep])(x[i:i + 1], y[i:i + 1])
        out[i] = pe[0] - e[i], pn[0] - n[i]
    return out


def _stats(d):
    d = np.asarray([v for v in d if np.isfinite(v)], float)
    if not len(d):
        return {"n": 0, "median_m": None, "p90_m": None, "max_m": None}
    return {"n": int(len(d)), "median_m": round(float(np.median(d)), 1), "p90_m": round(float(np.percentile(d, 90)), 1), "max_m": round(float(d.max()), 1)}


def check_errors(model, points):
    """Model minus check point, metres, per point; model maps plan pixels to UTM."""
    x = np.array([p["plan_x"] for p in points], float)
    y = np.array([p["plan_y"] for p in points], float)
    e, n = _TO_UTM.transform(np.array([p["lon"] for p in points], float), np.array([p["lat"] for p in points], float))
    pe, pn = model(x, y)
    reg = region_of(x, y)
    return [
        {"id": p["id"], "region": str(r), "kind": p["kind"], "dE_m": round(float(a), 1), "dN_m": round(float(b), 1), "dist_m": round(float(np.hypot(a, b)), 1)}
        for p, r, a, b in zip(points, reg, pe - np.asarray(e), pn - np.asarray(n))
    ]


def check_summary(errs):
    out = {"all": _stats([c["dist_m"] for c in errs])}
    for rg in REGIONS:
        out[rg] = _stats([c["dist_m"] for c in errs if c["region"] == rg])
    return out


def _model_of(path):
    d = json.loads(Path(path).read_text(encoding="utf8"))["transform"]
    return Panels([Fit.from_dict(f) for f in d["fits"]]) if d["type"] == "panels" else Fit.from_dict(d["fit"])


def run_fit():
    rows, excluded = read_control()
    x, y, e, n = _arrays(rows)
    qw = np.array([1.0 if r["quality"] == 1 else Q2_WEIGHT for r in rows])
    reg = np.array([r["region"] for r in rows])
    comparison = []

    def summarise(name, res, loo, extra=None):
        d = np.hypot(loo[:, 0], loo[:, 1])
        item = {"name": name, "rms_m": round(_rms(res[:, 0], res[:, 1]), 1), "loo_rms_m": round(_rms(loo[:, 0], loo[:, 1]), 1), "loo_median_m": round(float(np.median(d)), 1), "per_region": {}}
        for rg in REGIONS:
            m = reg == rg
            if m.any():
                item["per_region"][rg] = {"n": int(m.sum()), "loo_rms_m": round(_rms(loo[m, 0], loo[m, 1]), 1), "loo_median_m": round(float(np.median(d[m])), 1)}
        item.update(extra or {})
        comparison.append(item)
        return item

    # 1. A plain global affine on every control point.
    aff = fit("affine", x, y, e, n, 0.0, qw)
    pe, pn = aff(x, y)
    summarise("affine, all control points", np.c_[pe - e, pn - n], _loo_affine(x, y, e, n, qw))

    # 2. One smoothing for the whole plan, by leave-one-out.
    best_global = None
    for lam in LAM_GRID:
        lam_pt = np.full(len(x), lam)
        loo = _loo(x, y, e, n, lam_pt, qw)
        m = _tps(x, y, e, n, lam_pt, qw)
        pe, pn = m(x, y)
        item = summarise(f"tps lam={lam:g}, all control points", np.c_[pe - e, pn - n], loo, {"lam": lam})
        if best_global is None or item["loo_rms_m"] < best_global[0]:
            best_global = (item["loo_rms_m"], lam)

    # 3. The smoothness limit per region: one pass over the regions, each set by the leave-one-out of its own points.
    lam_by_region = {rg: best_global[1] for rg in REGIONS}
    for rg in REGIONS:
        idx = np.where(reg == rg)[0]
        if len(idx) < 4:
            continue
        scores = []
        for lam in LAM_GRID:
            trial = dict(lam_by_region, **{rg: lam})
            lam_pt = np.array([trial[r] for r in reg])
            loo = _loo(x, y, e, n, lam_pt, qw, idx)
            scores.append((round(_rms(loo[idx, 0], loo[idx, 1]), 2), -lam, lam))
        lam_by_region[rg] = min(scores)[2]  # ties go to the smoother
    lam_pt = np.array([lam_by_region[r] for r in reg])
    new = _tps(x, y, e, n, lam_pt, qw)
    pe, pn = new(x, y)
    new_loo = _loo(x, y, e, n, lam_pt, qw)
    new_item = summarise("tps, smoothing per region", np.c_[pe - e, pn - n], new_loo, {"lam_by_region": lam_by_region})

    # 4. Score on the frozen check set: the previous fit, the affine, the new fit.
    check = read_check()
    pts = check["points"]
    previous = _model_of(PREVIOUS_PATH)
    by_model = {}
    for name, model in (("previous", previous), ("affine", aff), ("new", new)):
        by_model[name] = check_summary(check_errors(model, pts))

    # 5. The brief's rule: where the new fit does worse than the previous on the check set (median), keep the previous there.
    decisions, pinned = {}, []
    for rg in REGIONS:
        a, b = by_model["new"][rg]["median_m"], by_model["previous"][rg]["median_m"]
        if a is not None and b is not None and a > b:
            decisions[rg] = f"previous: the new fit's check median {a} m is worse than the previous {b} m"
            pinned.append(rg)
        else:
            decisions[rg] = f"new: check median {a} m against the previous {b} m"
    final, final_name = new, "tps, smoothing per region"
    fx, fy, fe, fn, flam, fqw = x, y, e, n, lam_pt, qw
    if pinned:
        from shapely.geometry import Point

        polys = region_polygons()
        keep = ~np.isin(reg, pinned)
        gx, gy = [], []
        for rg in pinned:
            p = polys[rg]
            x0, y0, x1, y1 = p.bounds
            for xx in np.arange(x0 + PIN_STEP_PX / 2, x1, PIN_STEP_PX):
                for yy in np.arange(y0 + PIN_STEP_PX / 2, y1, PIN_STEP_PX):
                    if p.contains(Point(xx, yy)):
                        gx.append(xx)
                        gy.append(yy)
        gx, gy = np.array(gx), np.array(gy)
        ge, gn = previous(gx, gy)
        fx, fy = np.r_[x[keep], gx], np.r_[y[keep], gy]
        fe, fn = np.r_[e[keep], ge], np.r_[n[keep], gn]
        flam = np.r_[lam_pt[keep], np.full(len(gx), PIN_LAM)]
        fqw = np.r_[qw[keep], np.ones(len(gx))]
        final = _tps(fx, fy, fe, fn, flam, fqw)
        final_name = f"tps, smoothing per region; held to the previous fit in {', '.join(pinned)}"
    final_errs = check_errors(final, pts)
    by_model["final"] = check_summary(final_errs)

    tr = {"type": "single", "fit": final.to_dict(), "name": final_name}
    a = fit("affine", x, y, e, n)
    lin = np.array([a.params["coef_e"][1:3], a.params["coef_n"][1:3]]) * UNIT_M / UNIT_PX
    lin = lin @ np.diag([1.0, -1.0])
    tr["inverse_step"] = np.linalg.inv(lin).tolist()
    blk = _block_cv_r8(x, y, e, n, lam_pt, qw, reg)
    verdict = {}
    for rg in REGIONS:
        s = by_model["final"][rg]
        base = max(s["median_m"] or 0, new_item["per_region"].get(rg, {}).get("loo_median_m") or 0)
        verdict[rg] = {
            "check": s,
            "loo_median_m": new_item["per_region"].get(rg, {}).get("loo_median_m"),
            "block_cv_median_m": blk["per_region_median_m"].get(rg),
            "typical_m": int(np.ceil(base / 5.0) * 5) if base else None,
            "worst_m": s["max_m"],
            "fit": "previous" if rg in pinned else "new",
            "note": REGION_NOTES[rg],
        }
    out = {
        "plan": "S01",
        "source": "Plan of the Yuanmingyuan Imperial Garden-Palace, Princeton University Art Museum 2022-27 a-c",
        "mosaic": "research/raw/plans/princeton_mosaic.jpg",
        "pixel_frame": "plan_x, plan_y: pixels on the mosaic, origin top-left",
        "datum": "control and check points WGS84 (EPSG:4326); fitted in UTM 50N (EPSG:32650)",
        "date": FIT_DATE,
        "method": "Thin-plate spline on the control points of Round 1 and Round 8, with its smoothing set per region by leave-one-out; scored on the blind check set frozen before any fit (check_points.json); in a region where it does worse than the Round 1 fit there, a grid of points every 50 m taken from the Round 1 fit holds the spline to it.",
        "n_points": len(rows),
        "n_by_round": {"r1": int(sum(r["round"] == "r1" for r in rows)), "r8": int(sum(r["round"] == "r8" for r in rows))},
        "n_by_region": {rg: int((reg == rg).sum()) for rg in REGIONS},
        "excluded_near_check": excluded,
        "global_scale": affine_summary(rows),
        "transform": tr,
        "chosen": new_item,
        "comparison": comparison,
        "check": {"file": "research/georef/check_points.json", "sha256": check["sha256"], "n": len(pts), "by_model": by_model, "points": final_errs},
        "decisions": decisions,
        "previous": {"file": "research/georef/princeton-1920s.previous.json", "name": json.loads(PREVIOUS_PATH.read_text(encoding="utf8"))["transform"]["name"]},
        "block_cross_validation": blk,
        "per_region_verdict": verdict,
        "residuals": [
            {"id": r["id"], "round": r["round"], "region": r["region"], "kind": r["kind"], "quality": r["quality"], "dE_m": round(float(a1[0]), 1), "dN_m": round(float(a1[1]), 1), "loo_dE_m": round(float(b1[0]), 1), "loo_dN_m": round(float(b1[1]), 1), "loo_m": round(float(np.hypot(*b1)), 1)}
            for r, a1, b1 in zip(rows, np.c_[pe - e, pn - n], new_loo)
        ],
    }
    JSON_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf8")
    print(f"{'transform':40s} {'rms':>6s} {'LOO':>6s} {'LOOmed':>6s}  LOO median per region")
    for c in comparison:
        pr = " ".join(f"{k}:{v['loo_median_m']:.0f}" for k, v in c["per_region"].items())
        print(f"{c['name']:40s} {c['rms_m']:6.1f} {c['loo_rms_m']:6.1f} {c['loo_median_m']:6.1f}  {pr}")
    print("smoothing per region:", lam_by_region, "| excluded near a check point:", len(excluded))
    print(f"\ncheck set ({len(pts)} points), distance in m: median / p90 / max (n)")
    for rg in ("all",) + REGIONS:
        print(f"{rg:9s} " + "  ".join(f"{k}: {s[rg]['median_m']}/{s[rg]['p90_m']}/{s[rg]['max_m']} ({s[rg]['n']})" for k, s in by_model.items()))
    for rg, dsc in decisions.items():
        print(rg, "->", dsc)
    return out


ACCURACY_CELL_M = 200.0
ACCURACY_IDW_K = 4


def run_accuracy():
    """research/layers/georef_error.geojson: how far a position read off the plan may stand from where it stood, from the check set.

    Three kinds of feature: `region` (the six regions, with the check set's median, 90th percentile and maximum under the
    fit in use and under the previous one), `cell` (a 200 m grid: the inverse-distance mean of the errors at the four nearest
    check points of the same region; an estimate between points, not a measurement) and `check_point` (each check point,
    with its error under both fits). Derived from our own readings of the plan S01 and of today's imagery (coordinates only),
    so it is public like the other traced layers.
    """
    from shapely.geometry import Point, box, mapping

    d = json.loads(JSON_PATH.read_text(encoding="utf8"))
    pts = read_check()["points"]
    errs = {c["id"]: c for c in check_errors(_model_of(JSON_PATH), pts)}
    prev = {c["id"]: c for c in check_errors(_model_of(PREVIOUS_PATH), pts)}
    polys = region_polygons()
    feats = []

    def to_ll(poly):
        def ring(coords):
            c = np.asarray(coords)
            dense = []
            for a, b in zip(c[:-1], c[1:]):
                k = max(1, int(np.hypot(*(b - a)) // 100))
                dense += [a + (b - a) * t for t in np.arange(k) / k]
            dense.append(c[-1])
            dense = np.asarray(dense)
            lon, lat = plan_to_wgs84(dense[:, 0], dense[:, 1])
            return [[round(float(a), 7), round(float(b), 7)] for a, b in zip(lon, lat)]

        geoms = [poly] if poly.geom_type == "Polygon" else list(poly.geoms)
        out = [[ring(g.exterior.coords)] + [ring(h.coords) for h in g.interiors] for g in geoms]
        return {"type": "MultiPolygon", "coordinates": out}

    by = d["check"]["by_model"]
    for rg in REGIONS:
        s, p = by["final"][rg], by["previous"][rg]
        v = d["per_region_verdict"][rg]
        feats.append({"type": "Feature", "geometry": to_ll(polys[rg]), "properties": {
            "id": f"GE-{rg}", "kind": "region", "region": rg, "name": f"Placement accuracy: {REGION_NAMES[rg]}", "n_check": s["n"],
            "median_m": s["median_m"], "p90_m": s["p90_m"], "max_m": s["max_m"],
            "previous_median_m": p["median_m"], "previous_p90_m": p["p90_m"], "previous_max_m": p["max_m"],
            "fit": v["fit"], "typical_m": v["typical_m"],
            "sources": "S01;S160;S03", "confidence": "B",
            "note": REGION_NOTES[rg] + " Figures: distance between where the fit puts a check point read on the plan and where it is today, metres.",
        }})
    # The grid: inverse-distance mean of the four nearest check points in the same region.
    cx = np.array([p["plan_x"] for p in pts], float)
    cy = np.array([p["plan_y"] for p in pts], float)
    ce, cn = _TO_UTM.transform(np.array([p["lon"] for p in pts], float), np.array([p["lat"] for p in pts], float))
    ce, cn = np.asarray(ce), np.asarray(cn)
    creg = region_of(cx, cy)
    cdist = np.array([errs[p["id"]]["dist_m"] for p in pts])
    allp = [g for g in polys.values()]
    x0 = min(g.bounds[0] for g in allp); y0 = min(g.bounds[1] for g in allp)
    x1 = max(g.bounds[2] for g in allp); y1 = max(g.bounds[3] for g in allp)
    corners_e, corners_n = plan_to_utm(np.array([x0, x1, x0, x1]), np.array([y0, y0, y1, y1]))
    k = 0
    for ee in np.arange(np.floor(corners_e.min() / ACCURACY_CELL_M) * ACCURACY_CELL_M, corners_e.max(), ACCURACY_CELL_M):
        for nn in np.arange(np.floor(corners_n.min() / ACCURACY_CELL_M) * ACCURACY_CELL_M, corners_n.max(), ACCURACY_CELL_M):
            me, mn = ee + ACCURACY_CELL_M / 2, nn + ACCURACY_CELL_M / 2
            px, py = utm_to_plan(np.array([me]), np.array([mn]))
            rg = str(region_of(px, py)[0])
            if not polys[rg].contains(Point(float(px[0]), float(py[0]))):
                continue
            m = creg == rg
            if not m.any():
                continue
            dd = np.hypot(ce[m] - me, cn[m] - mn)
            order = np.argsort(dd)[:ACCURACY_IDW_K]
            w = 1.0 / np.maximum(dd[order], 25.0) ** 2
            est = float((w * cdist[m][order]).sum() / w.sum())
            lon, lat = _TO_LL.transform(np.array([ee, ee + ACCURACY_CELL_M, ee + ACCURACY_CELL_M, ee, ee]), np.array([nn, nn, nn + ACCURACY_CELL_M, nn + ACCURACY_CELL_M, nn]))
            k += 1
            feats.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[round(float(a), 7), round(float(b), 7)] for a, b in zip(lon, lat)]]}, "properties": {
                "id": f"GE-{k:04d}", "kind": "cell", "region": rg, "name": f"Placement accuracy, a 200 m cell in {REGION_NAMES[rg]}", "expected_m": round(est, 1),
                "nearest_check_m": round(float(dd[order[0]]), 0), "sources": "S01;S160;S03", "confidence": "C",
                "note": f"Estimate between check points: inverse-distance mean of the {len(order)} nearest in {rg}.",
            }})
    for p in pts:
        a, b = errs[p["id"]], prev[p["id"]]
        feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [p["lon"], p["lat"]]}, "properties": {
            "id": p["id"], "kind": "check_point", "region": a["region"], "name": f"Check point {p['id']}", "feature": p["feature"], "point_kind": p["kind"],
            "dist_m": a["dist_m"], "dE_m": a["dE_m"], "dN_m": a["dN_m"], "previous_dist_m": b["dist_m"],
            "sources": p.get("sources", "S01;S160"), "confidence": "B", "note": "A blind check point: never in a fit. Error = fit minus today's position.",
        }})
    ERROR_LAYER.write_text(json.dumps({"type": "FeatureCollection", "name": "georef_error", "features": feats}, ensure_ascii=False) + "\n", encoding="utf8")
    print(f"georef_error: {len(REGIONS)} regions, {k} cells, {len(pts)} check points")


def _block_cv_r8(x, y, e, n, lam_pt, qw, reg, block_px=1500.0):
    """Hold out whole squares of the plan (about 300 m): the error far from any control point."""
    blocks = (x // block_px).astype(int) * 1000 + (y // block_px).astype(int)
    out = np.full((len(x), 2), np.nan)
    for b in np.unique(blocks):
        m = blocks == b
        if (~m).sum() < 10:
            continue
        pe, pn = _tps(x[~m], y[~m], e[~m], n[~m], lam_pt[~m], qw[~m])(x[m], y[m])
        out[m] = np.c_[pe - e[m], pn - n[m]]
    d = np.hypot(out[:, 0], out[:, 1])
    return {"block_px": block_px, "median_m": round(float(np.nanmedian(d)), 1), "per_region_median_m": {rg: round(float(np.nanmedian(d[reg == rg])), 1) for rg in REGIONS if (reg == rg).any()}}


# --------------------------------------------------------------- importable mapping


_MODEL = None


def _load():
    global _MODEL
    if _MODEL is None:
        d = json.loads(JSON_PATH.read_text(encoding="utf8"))["transform"]
        if d["type"] == "panels":
            m = Panels([Fit.from_dict(f) for f in d["fits"]])
        else:
            m = Fit.from_dict(d["fit"])
        _MODEL = (m, np.array(d["inverse_step"]))
    return _MODEL


def plan_to_utm(xs, ys):
    return _load()[0](np.asarray(xs, float), np.asarray(ys, float))


def utm_to_plan(es, ns, iterations=12):
    """Exact inverse of plan_to_utm by fixed-point steps on the global linear part."""
    model, step = _load()
    es, ns = np.asarray(es, float), np.asarray(ns, float)
    # Starting value from the linear part around the plan centre.
    c = np.array([6000.0, 4000.0])
    ce, cn = model(np.array([c[0]]), np.array([c[1]]))
    xs = c[0] + step[0, 0] * (es - ce[0]) + step[0, 1] * (ns - cn[0])
    ys = c[1] + step[1, 0] * (es - ce[0]) + step[1, 1] * (ns - cn[0])
    for _ in range(iterations):
        pe, pn = model(xs, ys)
        de, dn = es - pe, ns - pn
        xs = xs + step[0, 0] * de + step[0, 1] * dn
        ys = ys + step[1, 0] * de + step[1, 1] * dn
    return xs, ys


def plan_to_wgs84(xs, ys):
    """Plan pixels to (lons, lats)."""
    return _TO_LL.transform(*plan_to_utm(xs, ys))


def wgs84_to_plan(lons, lats):
    """(lons, lats) to plan pixels."""
    return utm_to_plan(*_TO_UTM.transform(np.asarray(lons, float), np.asarray(lats, float)))


# --------------------------------------------------------------- overlay and images


def global_px_per_m():
    return json.loads(JSON_PATH.read_text(encoding="utf8"))["global_scale"]["similarity_px_per_m"]


def _dense_plan_coords(lons, lats, step=32):
    """Plan pixel of every output pixel, computed on a coarse grid and interpolated (the model is smooth)."""
    h, w = lats.size, lons.size
    jc = np.arange(0, h + step, step)
    ic = np.arange(0, w + step, step)
    jc[-1], ic[-1] = h - 1, w - 1
    lonc = np.interp(ic, np.arange(w), lons)
    latc = np.interp(jc, np.arange(h), lats)
    llo, lla = np.meshgrid(lonc, latc)
    px, py = wgs84_to_plan(llo, lla)
    fi = np.interp(np.arange(w), ic, np.arange(len(ic)))
    fj = np.interp(np.arange(h), jc, np.arange(len(jc)))
    i0 = np.minimum(fi.astype(int), len(ic) - 2)
    j0 = np.minimum(fj.astype(int), len(jc) - 2)
    ti, tj = fi - i0, fj - j0
    ti, tj = ti[None, :], tj[:, None]

    def lerp(a):
        return (
            a[np.ix_(j0, i0)] * (1 - ti) * (1 - tj)
            + a[np.ix_(j0, i0 + 1)] * ti * (1 - tj)
            + a[np.ix_(j0 + 1, i0)] * (1 - ti) * tj
            + a[np.ix_(j0 + 1, i0 + 1)] * ti * tj
        )

    return lerp(px), lerp(py)


def run_overlay(res_m=0.5, max_side=8000):
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None
    plan = Image.open(MOSAIC).convert("RGB")
    w, h = plan.size
    # Bounds: the mosaic corners and edges, in lon/lat.
    ex = np.r_[np.linspace(0, w, 60), np.linspace(0, w, 60), np.zeros(60), np.full(60, w)]
    ey = np.r_[np.zeros(60), np.full(60, h), np.linspace(0, h, 60), np.linspace(0, h, 60)]
    lon, lat = plan_to_wgs84(ex, ey)
    west, east, south, north = float(lon.min()), float(lon.max()), float(lat.min()), float(lat.max())
    e0, n0 = _TO_UTM.transform((west + east) / 2, (south + north) / 2)
    _, n1 = _TO_UTM.transform((west + east) / 2, north)
    _, n2 = _TO_UTM.transform((west + east) / 2, south)
    e1, _ = _TO_UTM.transform(east, (south + north) / 2)
    e2, _ = _TO_UTM.transform(west, (south + north) / 2)
    width_m, height_m = float(e1 - e2), float(n1 - n2)
    res = max(res_m, max(width_m, height_m) / max_side)
    ow, oh = int(round(width_m / res)), int(round(height_m / res))
    lons = west + (np.arange(ow) + 0.5) * (east - west) / ow
    lats = north - (np.arange(oh) + 0.5) * (north - south) / oh
    # The plan is finer than the output: reduce first, so thin ink lines do not break up in nearest-neighbour sampling.
    reduce_by = max(1, int(res * global_px_per_m()))
    src = np.asarray(plan.reduce(reduce_by)) if reduce_by > 1 else np.asarray(plan)
    out = np.full((oh, ow, 3), 255, np.uint8)
    # Row blocks, to keep memory low on the shared machine.
    for r0 in range(0, oh, 512):
        r1 = min(oh, r0 + 512)
        px, py = _dense_plan_coords(lons, lats[r0:r1])
        ix, iy = np.rint(px / reduce_by).astype(int), np.rint(py / reduce_by).astype(int)
        inside = (ix >= 0) & (iy >= 0) & (ix < src.shape[1]) & (iy < src.shape[0])
        block = out[r0:r1]
        block[inside] = src[iy[inside], ix[inside]]
    OVERLAY.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(out).save(OVERLAY, quality=85)
    meta = {
        "image": OVERLAY.name,
        "plan": "S01",
        "note": "research-only plan: never commit, never publish. North up, linear in lon and lat (equirectangular grid in EPSG:4326).",
        "bounds_leaflet": [[south, west], [north, east]],
        "corners_lonlat": {"nw": [west, north], "ne": [east, north], "se": [east, south], "sw": [west, south]},
        "width_px": ow,
        "height_px": oh,
        "metres_per_px": round(res, 3),
        "date": date.today().isoformat(),
    }
    OVERLAY.with_suffix(".json").write_text(json.dumps(meta, indent=1), encoding="utf8")
    print("overlay", ow, oh, "m/px", round(res, 3), [south, west, north, east])


def _osm_lines():
    feats = json.loads(OSM.read_text(encoding="utf8"))["features"]
    for f in feats:
        p, g = f["properties"], f["geometry"]
        if p.get("natural") == "water" or p.get("water") or p.get("landuse") == "reservoir":
            k = "water"
        elif p.get("waterway"):
            k = "waterway"
        elif p.get("barrier") in ("wall", "city_wall"):
            k = "wall"
        elif p.get("historic") or p.get("building") == "ruins" or p.get("ruins"):
            k = "ruin"
        else:
            continue
        t, c = g["type"], g["coordinates"]
        rings = c if t in ("Polygon", "MultiLineString") else [c] if t == "LineString" else [r for q in c for r in q] if t == "MultiPolygon" else []
        for r in rings:
            yield k, np.array(r)[:, :2]


COLORS = {"water": (0, 90, 255), "waterway": (0, 170, 230), "wall": (225, 20, 20), "ruin": (240, 110, 0)}


def run_images():
    """screenshots/r8/georef_residuals.png: the check set's errors under the previous fit (grey) and the fit in use (coloured), the control points, today's OSM. No plan image: safe to show. With the local overlay, also georef_overlay.jpg."""
    from PIL import Image, ImageDraw, ImageFont

    Image.MAX_IMAGE_PIXELS = None
    SHOTS.mkdir(parents=True, exist_ok=True)
    if OVERLAY.exists():
        meta = json.loads(OVERLAY.with_suffix(".json").read_text())
        (south, west), (north, east) = meta["bounds_leaflet"]
        im = Image.open(OVERLAY).convert("RGB")
        scale = 3000 / max(im.size)
        im = Image.blend(Image.new("RGB", (int(im.width * scale), int(im.height * scale)), "white"), im.resize((int(im.width * scale), int(im.height * scale)), Image.BILINEAR), 0.5)
        d = ImageDraw.Draw(im)
        for k, q in _osm_lines():
            d.line(list(zip((q[:, 0] - west) / (east - west) * im.width, (north - q[:, 1]) / (north - south) * im.height)), fill=COLORS[k], width=2)
        im.save(SHOTS / "georef_overlay.jpg", quality=85)

    data = json.loads(JSON_PATH.read_text(encoding="utf8"))
    pts = {p["id"]: p for p in read_check()["points"]}
    prev = {c["id"]: c for c in check_errors(_model_of(PREVIOUS_PATH), list(pts.values()))}
    rows, _ = read_control()
    lo0, lo1, la0, la1 = 116.2800, 116.3150, 39.9950, 40.0150
    w = 2600
    h = int(w * (la1 - la0) / (lo1 - lo0) / np.cos(np.radians(40.005)))
    c = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(c)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    except OSError:
        font = ImageFont.load_default()

    def P(lon, lat):
        return (lon - lo0) / (lo1 - lo0) * w, (la1 - lat) / (la1 - la0) * h

    for k, q in _osm_lines():
        col = tuple(int(v * 0.4 + 255 * 0.6) for v in COLORS[k])
        d.line([P(a, b) for a, b in q], fill=col, width=1)
    polys = region_polygons()
    for rg, poly in polys.items():
        geoms = [poly] if poly.geom_type == "Polygon" else list(poly.geoms)
        for g in geoms:
            q = np.asarray(g.exterior.coords)
            lon, lat = plan_to_wgs84(q[:, 0], q[:, 1])
            d.line([P(a, b) for a, b in zip(lon, lat)], fill=(60, 60, 60), width=2)
        cxy = poly.representative_point()
        lon, lat = plan_to_wgs84(np.array([cxy.x]), np.array([cxy.y]))
        s = data["check"]["by_model"]["final"][rg]
        d.text(P(lon[0], lat[0]), f"{rg}: median {s['median_m']} m, p90 {s['p90_m']}, max {s['max_m']} (n={s['n']})", fill=(0, 0, 0), font=font)
    m_per_px = (lo1 - lo0) * 111320 * np.cos(np.radians(40.005)) / w
    exag = 3
    for r in rows:
        px, py = P(r["lon"], r["lat"])
        col = (0, 140, 0) if r["round"] == "r1" else (0, 90, 220)
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=col)
    for c_ in data["check"]["points"]:
        p = pts[c_["id"]]
        px, py = P(p["lon"], p["lat"])
        b = prev[c_["id"]]
        d.line([px, py, px + b["dE_m"] / m_per_px * exag, py - b["dN_m"] / m_per_px * exag], fill=(150, 150, 150), width=3)
        col = (0, 150, 0) if c_["dist_m"] < 10 else (230, 140, 0) if c_["dist_m"] < 25 else (200, 0, 0)
        d.line([px, py, px + c_["dE_m"] / m_per_px * exag, py - c_["dN_m"] / m_per_px * exag], fill=col, width=3)
        d.rectangle([px - 5, py - 5, px + 5, py + 5], outline=(120, 0, 200), width=2)
        d.text((px + 6, py + 4), c_["id"], fill=(120, 0, 200), font=font)
    d.rectangle([10, 10, 1250, 112], fill="white", outline="black")
    d.text((20, 16), f"S01 placement, Round 8: {data['transform']['name']}. {data['n_points']} control points (green Round 1, blue Round 8).", fill="black", font=font)
    d.text((20, 40), f"Purple squares: the {len(pts)} blind check points, never in a fit. Arrows x{exag}: grey the previous fit's error, coloured the fit in use (green under 10 m, orange 10-25, red over 25).", fill="black", font=font)
    a = data["check"]["by_model"]
    d.text((20, 64), f"Check set, all: previous median {a['previous']['all']['median_m']} m, p90 {a['previous']['all']['p90_m']} m; in use median {a['final']['all']['median_m']} m, p90 {a['final']['all']['p90_m']} m, max {a['final']['all']['max_m']} m.", fill="black", font=font)
    d.text((20, 88), "Background: OpenStreetMap contributors (ODbL). No plan image.", fill="black", font=font)
    c.save(SHOTS / "georef_residuals.png")
    print("images written")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "fit"
    {"fit": run_fit, "previous": run_fit_previous, "freeze": run_freeze, "accuracy": run_accuracy, "overlay": run_overlay, "images": run_images}[cmd]()
