"""Clip the Copernicus GLO-30 DSM tiles (research/raw/dem/) to the site; write research/raw/dem/site_glo30.npz + a hillshade PNG and print stats.

The site straddles 40 N, so it reads two tiles. GLO-30 is a surface model (trees and buildings included), 1 arc second.
"""

import json
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image

RAW = Path("research/raw/dem")
BOX = (39.990, 116.275, 40.022, 116.325)  # south, west, north, east
STEP = 1 / 3600


def read(name: str, north: float, west: float) -> tuple[np.ndarray, float, float]:
    a = tifffile.imread(RAW / name)
    return a, north, west


def main() -> None:
    n40, _, _ = read("Copernicus_DSM_COG_10_N40_00_E116_00_DEM.tif", 41, 116)
    n39, _, _ = read("Copernicus_DSM_COG_10_N39_00_E116_00_DEM.tif", 40, 116)
    full = np.vstack([n40, n39])  # top row at 41 N
    i0 = int((41 - BOX[2]) / STEP)
    i1 = int((41 - BOX[0]) / STEP) + 1
    j0 = int((BOX[1] - 116) / STEP)
    j1 = int((BOX[3] - 116) / STEP) + 1
    dem = full[i0:i1, j0:j1]
    north = 41 - i0 * STEP
    west = 116 + j0 * STEP
    np.savez_compressed(RAW / "site_glo30.npz", dem=dem, north=north, west=west, step=STEP)
    gy, gx = np.gradient(dem.astype(float), 30.0)
    shade = np.clip(0.6 + (gx * -0.7 + gy * 0.7) * 0.5, 0, 1)
    Image.fromarray((shade * 255).astype("uint8")).resize((dem.shape[1] * 6, dem.shape[0] * 6)).save(RAW / "site_glo30_shade.png")
    stats = {
        "cells": dem.shape,
        "min_m": float(dem.min()),
        "max_m": float(dem.max()),
        "median_m": float(np.median(dem)),
        "north": north,
        "west": west,
    }
    print(json.dumps(stats))


if __name__ == "__main__":
    main()
