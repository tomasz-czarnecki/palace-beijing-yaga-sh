"""Stitch the three hi-res scrolls of the Princeton plan (S01) into one image on the geometry of the museum's composite photo.

Fits an affine from each scroll to the composite by correlating patches. The mosaic is the plan's pixel grid: every plan_x, plan_y in this
project refers to it. Writes research/raw/plans/princeton_mosaic.jpg and research/georef/princeton-mosaic.json. Prints the fit residuals.
"""

import json
from pathlib import Path

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
RAW = Path("research/raw/plans")
COMPOSITE = RAW / "princeton_2022-27_plan_yuanmingyuan_1920s_max.jpg"
SCROLLS = {
    "a": RAW / "princeton_2022-27_scroll1_PUAMANX23_6397_max.jpg",
    "b": RAW / "princeton_2022-27_scroll2_PUAMANX23_6395_max.jpg",
    "c": RAW / "princeton_2022-27_scroll3_PUAMANX23_6391_max.jpg",
}
GAIN = 1.75  # mosaic pixels per composite pixel, about the scrolls' own resolution
PATCH = 320  # composite pixels
PANEL_GUESS = 7403 / 3  # panel width in the composite


def grey(im: Image.Image) -> np.ndarray:
    return np.asarray(im.convert("L"), dtype=np.float32)


def phase(a: np.ndarray, b: np.ndarray) -> tuple[float, float, float]:
    """Shift (dx, dy) that moves b onto a, and the correlation peak."""
    a = a - a.mean()
    b = b - b.mean()
    w = np.outer(np.hanning(a.shape[0]), np.hanning(a.shape[1]))
    fa, fb = np.fft.rfft2(a * w), np.fft.rfft2(b * w)
    c = fa * np.conj(fb)
    c /= np.abs(c) + 1e-6
    r = np.fft.irfft2(c, s=a.shape)
    i, j = np.unravel_index(np.argmax(r), r.shape)
    dy = i if i < a.shape[0] / 2 else i - a.shape[0]
    dx = j if j < a.shape[1] / 2 else j - a.shape[1]
    return float(dx), float(dy), float(r[i, j])


def coarse(comp_small: np.ndarray, scroll_small: np.ndarray) -> tuple[int, int]:
    """Whole-image offset of a scroll in the composite at 1/8 scale, by normalised FFT correlation."""
    h = max(comp_small.shape[0], scroll_small.shape[0]) * 2
    w = max(comp_small.shape[1], scroll_small.shape[1]) * 2
    fa = np.fft.rfft2(comp_small - comp_small.mean(), s=(h, w))
    fb = np.fft.rfft2(scroll_small - scroll_small.mean(), s=(h, w))
    c = fa * np.conj(fb)
    c /= np.abs(c) + 1e-6
    r = np.fft.irfft2(c, s=(h, w))
    i, j = np.unravel_index(np.argmax(r), r.shape)
    return (j if j < w / 2 else j - w), (i if i < h / 2 else i - h)


def fit_scroll(comp: Image.Image, scroll: Image.Image, panel: int) -> dict:
    """Affine scroll -> composite. Start: uniform scale, tested over a small range; refine on a patch grid."""
    cg = grey(comp)
    x0 = int(panel * PANEL_GUESS)
    x1 = int((panel + 1) * PANEL_GUESS)
    best = None
    for s in np.arange(0.545, 0.60, 0.003):  # composite px per scroll px
        sm = scroll.resize((int(scroll.width * s / 8), int(scroll.height * s / 8)), Image.BILINEAR)
        comp_small = np.asarray(comp.crop((x0, 0, x1, comp.height)).resize(((x1 - x0) // 8, comp.height // 8), Image.BILINEAR).convert("L"), dtype=np.float32)
        dx, dy = coarse(comp_small, grey(sm))
        if best is None or True:
            sc = np.asarray(sm.convert("L"), dtype=np.float32)
            # score: correlation on the overlap
            ax0, ay0 = max(dx, 0), max(dy, 0)
            ax1, ay1 = min(comp_small.shape[1], dx + sc.shape[1]), min(comp_small.shape[0], dy + sc.shape[0])
            if ax1 - ax0 < 50 or ay1 - ay0 < 50:
                continue
            a = comp_small[ay0:ay1, ax0:ax1]
            b = sc[ay0 - dy : ay1 - dy, ax0 - dx : ax1 - dx]
            score = float(np.corrcoef(a.ravel(), b.ravel())[0, 1])
            if best is None or score > best[0]:
                best = (score, float(s), dx * 8 + x0, dy * 8)
    score, s, ox, oy = best
    print(f"  coarse scale {s:.3f} offset {ox},{oy} score {score:.3f}")
    src, dst = [], []
    for cy in range(PATCH // 2, comp.height - PATCH // 2, PATCH // 2):
        for cx in range(x0 + PATCH // 2, x1 - PATCH // 2, PATCH // 2):
            a = cg[cy - PATCH // 2 : cy + PATCH // 2, cx - PATCH // 2 : cx + PATCH // 2]
            if a.std() < 8:
                continue
            sx, sy = (cx - ox) / s, (cy - oy) / s
            half = PATCH / 2 / s
            box = (sx - half, sy - half, sx + half, sy + half)
            if box[0] < 0 or box[1] < 0 or box[2] > scroll.width or box[3] > scroll.height:
                continue
            b = grey(scroll.crop(tuple(int(v) for v in box)).resize((PATCH, PATCH), Image.BILINEAR))
            dx, dy, peak = phase(a, b)
            if peak > 0.06:
                src.append((sx, sy))
                dst.append((cx - dx, cy - dy))
    src, dst = np.array(src), np.array(dst)
    keep = np.ones(len(src), bool)
    for _ in range(6):
        A = np.c_[src[keep], np.ones(keep.sum())]
        M, *_ = np.linalg.lstsq(A, dst[keep], rcond=None)
        res = np.c_[src, np.ones(len(src))] @ M - dst
        err = np.hypot(*res.T)
        keep = err < max(1.5, np.median(err[keep]) * 2.5)
    rms = float(np.sqrt((err[keep] ** 2).mean()))
    print(f"  patches {len(src)} kept {keep.sum()} rms {rms:.2f} composite px")
    return {"to_composite": M.T.tolist(), "patches": int(keep.sum()), "rms_composite_px": round(rms, 2), "coarse_scale": s}


def main() -> None:
    comp = Image.open(COMPOSITE)
    W, H = comp.size
    out = Image.new("RGB", (int(W * GAIN), int(H * GAIN)), (235, 225, 210))
    report = {"composite": COMPOSITE.name, "gain": GAIN, "size": list(out.size), "scrolls": {}}
    for panel, (key, path) in enumerate(SCROLLS.items()):
        print("scroll", key)
        scroll = Image.open(path)
        fit = fit_scroll(comp, scroll, panel)
        report["scrolls"][key] = {"file": path.name, **fit}
        M = np.array(fit["to_composite"])  # 2x3, scroll -> composite
        F = np.vstack([M * GAIN, [0, 0, 1]])  # scroll -> mosaic
        I = np.linalg.inv(F)  # mosaic -> scroll, what PIL wants
        warped = scroll.transform(out.size, Image.AFFINE, tuple(I[:2].ravel()), Image.BICUBIC, fillcolor=None)
        x0 = int(panel * PANEL_GUESS * GAIN) + (int(report.get("_seam", 0)))
        x1 = int((panel + 1) * PANEL_GUESS * GAIN)
        out.paste(warped.crop((x0, 0, x1, out.height)), (x0, 0))
    out.save(RAW / "princeton_mosaic.jpg", quality=90)
    Path("research/georef/princeton-mosaic.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=1)[:600])


if __name__ == "__main__":
    main()
