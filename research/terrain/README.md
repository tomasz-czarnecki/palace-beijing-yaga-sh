# Terrain

All figures come from runs on `research/raw/dem/site_glo30.npz` and `research/layers/osm_today.geojson`.

## Data

Copernicus DEM GLO-30 (S04, S159), tiles N39 and N40 E116, clipped by `scripts/clip_dem.py`. 1 arc second: about 24 m E-W by 31 m N-S here.

- **Datum:** horizontal WGS84, vertical EGM2008 (EPSG:3855) (S159).
- **Stated accuracy:** absolute vertical under 4 m LE90, relative vertical under 2 m on slopes up to 20%, absolute horizontal under 6 m CE90 (S159).
- **Date:** TanDEM-X, 2011-2015 (S159). Later earth moving is not in it. The 2005 works are.
- **Type:** surface model. Trees and buildings are included. Water bodies are edited flat (S159).
- **Grid:** the GeoTIFF is `RasterPixel.IsPoint`, tie point 116.0, 41.0. So `north` and `west` in the npz are the CENTRE of row 0 and column 0: `lat = north - i*step`, `lon = west + j*step`. Reading them as edges shifts the DEM by half a cell (about 15 m N-S, 12 m E-W).

## Registration

The flattened 福海 cells (value 43.50) match the OSM 福海 polygon best at a shift of 0 m E, 4 m N, overlap 0.905 (0.891 at zero). OSM against Esri World Imagery z17: best shift 2.7 m E, 1.8 m N over 54 outlines. All three agree to within what they can resolve. GCJ-02 here would be 520 m E, 142 m N, 540 m in total.

## Surfaces today (metres, EGM2008)

| Surface | Median | Spread | Cells |
|---|---|---|---|
| 福海 | 43.5 | flat, edited | 288 |
| 后湖 | 42.2 | p10-p90 41.5-42.9 | 28 |
| 曲院风荷 lake | 42.3 | 41.2-42.8 | 11 |
| 绮春园 lakes | 42.5 | 41.8-43.4 | 62 |
| 长春园 lakes | 41.2-41.4 | 40.8-42.2 | 12-45 per lake |
| Land, 圆明园 west | 45.7 | p25-p75 44.8-46.8 | 1270 |
| Land around 福海 | 46.9 | 45.2-48.6 | 614 |
| Land, 长春园 | 44.8 | 43.2-47.1 | 517 |
| Land, 西洋楼 strip | 46.5 | 44.8-49.4 | 334 |
| Land, 绮春园 | 46.5 | 45.3-48.0 | 777 |

Land medians include trees, so true ground is lower. Take water at about 42-43.5 m and ground at about 45 m as today's levels, with an error of 1-2 m. These are lined modern lakes (S148), so they are not the water levels of 1860. The lakes that are not edited flat read lower than 福海, but that difference may come from the editing.

The paddy at 多稼如云 reads 43.6-44.0 m and open ground in the west about 45.5-46 m. Those are the cleanest ground readings at the site.

## Noise floor

Residual = cell minus the median of land cells 90-210 m away.

- **Open ground, 6 patches, 91 cells:** std 1.30 m, p5 -2.16, p95 1.86, max 3.19.
- **All park land, 3272 cells:** std 2.31 m, p95 4.52, p99 7.32, max 14.07.
- **Water not edited flat:** std 0.4-0.9 m per lake, up to 1.75 m.
- **Trees on flat ground:** three conifer blocks 1.2-3.1 m, a block beside 线法山 4.0 m. A tall tree row S of the 长春园 lakes 14.1 m, the pine belt N of the 长春园 lakes 11.8 m.

## What it can tell

- The lake and land pattern, the 2-5 m step from water to bank, and the overall slope.
- That belts of raised ground exist. 54 connected patches stand 4 m or more above their surroundings.
- That some places are flat and hill-free (藻园, 山高水长 field).

## What it cannot tell

- **The height of any single hill.** Under 3 m is noise. From 4 to 8 m, a low mound and a tree are the same signal. Over 10 m is canopy. Most hills are narrower than 2-3 cells, and a real mound and a tree row can both reach 6-8 m.
- **The 1860 surface.** Hills were cut 1967-1973 and later (S145), and rebuilt with modern fill: 12万 m3 of 挖湖堆山 by 2005 (S147).
- **Edges of ponds under about 8000 m2.** They have too few cells.

## How to use it

Use the DEM for base levels only. Take hill outlines from S01 and the surveys, and give heights by class: a 3-6 m default and up to about 10 m for named large hills, within Attiret's range of 6-18 m (S157). All are grade C with that reason.

## Better data

- **FABDEM** (S158): GLO-30 with trees and buildings removed, CC BY-NC-SA 4.0. Worth testing on one tile. It has the same 30 m cells and is non-commercial. Not downloaded. It may also remove real small mounds (assumed).
- **MERIT-Urban corrected DEM, Beijing** (Bristol, viewed, Non-Commercial Government Licence): a city product, too coarse for hills (resolution not checked).
- **AW3D30, MERIT:** 30 m and 90 m surface models. No gain over GLO-30 (assumed, not checked).
- **TanDEM-X 12 m:** not open, on application (found, search snippet).
- **Beijing LiDAR or 1 m DEM:** no open source found.
- **The real upgrade is on paper:** the 1933 and 1963 surveys of the ruins (S136, S146). See `research/wishlist.md`.

## Hills

`research/layers/hills_1860.geojson` takes outlines from S01. Height: the site reading in `research/plan/hills_texts.csv` where one lies within 120 m (mostly snapped to a residual peak, so it runs high), otherwise sqrt(area)/8 clipped to 3-10 m. All grade C.
