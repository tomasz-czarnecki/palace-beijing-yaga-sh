"""Georeference the Princeton plan (S01) on today's landscape.

Reads the control points in research/georef/princeton-1920s.csv, fits several transforms in UTM 50N
(EPSG:32650), compares them by leave-one-out RMS and stores the chosen one in
research/georef/princeton-1920s.json. All figures in that file come from a run of this script.

Import (numpy and pyproj only):

    from georef import plan_to_wgs84, wgs84_to_plan
    lons, lats = plan_to_wgs84(xs, ys)   # plan_x, plan_y = pixels on research/raw/plans/princeton_mosaic.jpg
    xs, ys = wgs84_to_plan(lons, lats)

Commands:

    python scripts/georef.py fit        compare transforms, write the JSON
    python scripts/georef.py overlay    warp the mosaic to research/overlays/princeton-1920s.jpg + .json
    python scripts/georef.py images     screenshots/r1/georef_overlay.jpg and georef_residuals.png
"""

import csv
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
from pyproj import Transformer

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "research/georef/princeton-1920s.csv"
JSON_PATH = ROOT / "research/georef/princeton-1920s.json"
MOSAIC = ROOT / "research/raw/plans/princeton_mosaic.jpg"
OVERLAY = ROOT / "research/overlays/princeton-1920s.jpg"
OSM = ROOT / "research/layers/osm_today.geojson"
SHOTS = ROOT / "screenshots/r1"

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
            for s in range(0, len(x), 200000):
                xs, ys = x[s : s + 200000], y[s : s + 200000]
                k = _tps_kernel((xs[:, None] - cen[:, 0]) ** 2 + (ys[:, None] - cen[:, 1]) ** 2)
                g = np.c_[np.ones_like(xs), xs, ys]
                e[s : s + 200000] = k @ w[:, 0] + g @ a[:, 0]
                n[s : s + 200000] = k @ w[:, 1] + g @ a[:, 1]
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


def run_fit():
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
        "date": date.today().isoformat(),
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
    JSON_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf8")
    print(f"{'transform':28s} {'rms':>7s} {'LOO':>7s} {'LOOmed':>7s}  LOO per area")
    for c in comparison:
        pa = " ".join(f"{k}:{v['loo_rms_m']:.0f}" for k, v in c["per_area"].items())
        print(f"{c['name']:28s} {c['rms_m']:7.1f} {c['loo_rms_m']:7.1f} {c['loo_median_m']:7.1f}  {pa}")
    print("chosen:", item["name"], "| scale:", out["global_scale"])
    if checks:
        ic = out["independent_check"]
        print("check kept:", ic["n"], ic["rms_m"], "rms", ic["median_m"], "median | shapes", ic["on_shapes"], "| labels", ic["on_osm_labels"], "| first pass", ic["first_pass"]["n"], ic["first_pass"]["rms_m"], ic["first_pass"]["median_m"])
    return out


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


def utm_to_plan(es, ns, iterations=8):
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
    from PIL import Image, ImageDraw, ImageFont

    Image.MAX_IMAGE_PIXELS = None
    SHOTS.mkdir(parents=True, exist_ok=True)
    meta = json.loads(OVERLAY.with_suffix(".json").read_text())
    (south, west), (north, east) = meta["bounds_leaflet"]
    im = Image.open(OVERLAY).convert("RGB")
    scale = 3000 / max(im.size)
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.BILINEAR)
    white = Image.new("RGB", im.size, "white")
    im = Image.blend(white, im, 0.5)
    d = ImageDraw.Draw(im)

    def to_px(q):
        return list(zip((q[:, 0] - west) / (east - west) * im.width, (north - q[:, 1]) / (north - south) * im.height))

    for k, q in _osm_lines():
        d.line(to_px(q), fill=COLORS[k], width=2)
    im.save(SHOTS / "georef_overlay.jpg", quality=85)

    # Residual map: OSM and points only, no plan, safe to show.
    data = json.loads(JSON_PATH.read_text(encoding="utf8"))
    rows = {r["id"]: r for r in read_points()}
    lo0, lo1, la0, la1 = 116.2815, 116.3175, 39.9935, 40.0170
    w = 2400
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
        col = tuple(int(v * 0.45 + 255 * 0.55) for v in COLORS[k])
        d.line([P(a, b) for a, b in q], fill=col, width=1)
    m_per_img_px = (lo1 - lo0) * 111320 * np.cos(np.radians(40.005)) / w
    exag = 3
    for r in data["residuals"]:
        src = rows[r["id"]]
        px, py = P(src["lon"], src["lat"])
        dx, dy = r["loo_dE_m"] / m_per_img_px * exag, -r["loo_dN_m"] / m_per_img_px * exag
        col = (200, 0, 0) if r["loo_m"] > 40 else (230, 120, 0) if r["loo_m"] > 20 else (0, 130, 0)
        d.line([px, py, px + dx, py + dy], fill=col, width=2)
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=col)
        d.text((px + 5, py + 4), r["id"], fill=(30, 30, 30), font=font)
    for p in data["independent_check"]["points"]:
        src = rows[p["id"]]
        px, py = P(src["lon"], src["lat"])
        dx, dy = p["dE_m"] / m_per_img_px * exag, -p["dN_m"] / m_per_img_px * exag
        d.line([px, py, px + dx, py + dy], fill=(120, 0, 200), width=2)
        d.rectangle([px - 4, py - 4, px + 4, py + 4], outline=(120, 0, 200), width=2)
        d.text((px + 5, py + 4), p["id"], fill=(120, 0, 200), font=font)
    d.rectangle([10, 10, 980, 120], fill="white", outline="black")
    d.text((20, 16), f"S01 georeferencing: {data['transform']['name']}, {data['n_points']} points. Leave-one-out residuals x{exag} (arrow scale). OSM (ODbL) background.", fill="black", font=font)
    d.text((20, 40), "Dot colours: green under 20 m, orange 20-40 m, red over 40 m. Purple squares: independent check points (not in the fit).", fill="black", font=font)
    d.text((20, 64), f"Overall: RMS {data['chosen']['rms_m']} m, leave-one-out RMS {data['chosen']['loo_rms_m']} m, median {data['chosen']['loo_median_m']} m.", fill="black", font=font)
    ic = data["independent_check"]
    d.text((20, 88), f"Check points, not blind: kept {ic['n']}, median {ic['median_m']} m; first reading {ic['first_pass']['n']}, median {ic['first_pass']['median_m']} m. © OpenStreetMap contributors", fill="black", font=font)
    c.save(SHOTS / "georef_residuals.png")
    print("images written")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "fit"
    {"fit": run_fit, "overlay": run_overlay, "images": run_images}[cmd]()
