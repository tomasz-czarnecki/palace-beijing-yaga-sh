# Terrain

What the ground of the 3D view stands on, and how sure each part is. The DEM figures come from runs on `research/raw/dem/site_glo30.npz` (`scripts/clip_dem.py`) and `research/layers/osm_today.geojson`; the ground's from `scripts/terrain_dem.py`, `scripts/hills1860.py`, `scripts/ground1860.py` and `tools/check_ground.py` (Round 10).

## Round 10 in short

- **Measured:** the plain's slope (from today's DEM, a surface model, not the ground of 1860); the 2.5 m surface the view draws, against which every box, way, bridge, wall and landing is checked (`ground_check.json`).
- **Read from a source:** one hill height (线法山, the park's 8 m, S1000, B); where the hills stand round each of the Forty Scenes and what kind each shore is (the 1744 album, S08, read leaf by leaf: `readings.csv`); the water's flow (S05 j80:6b-7b: in by a one-opening sluice in the south-west, out by 明春门 and 七空闸 into 清河); depths of about 2 m (S1002, a search extract).
- **Typology and guesses (C):** every other hill height; the hills of 418 pieces of free land (`assumed: true`); every water level; bank heights; the beds.
- **Not known:** the levels of 1860, the height of any single hill but 线法山, where exactly most earth hills stood. The plan S01 draws halls, shores and rockeries 假山 (black hatched clumps), but no earth hills 土山 (Q29, Q199).

## Files

| File | What | Written by |
|---|---|---|
| `readings.csv` | every row the Round 10 workers read: hills, shores, rockeries, water, surveys | hand (first merged by `docs/rounds/common/palace_r10_merge.py`) |
| `plain.json` | the plain as a plane through the DEM's low envelope; today's lake surfaces and their fall | `scripts/terrain_dem.py` (needs `raw/dem/`) |
| `glo30_rise.npz` | per DEM cell, today's height above the local low ground, decimetres | `scripts/terrain_dem.py` |
| `hills_heights.csv` | one row per hill of `layers/hills_1860`: height, method, error, sources | `scripts/hills1860.py` |
| `rockeries.csv` | rockeries the texts and leaves describe, scene by scene, for the vegetation round | `scripts/hills1860.py` |
| `water_levels.csv` | one row per water body: its polygons, level, depth | `scripts/ground1860.py` |
| `ground_report.json` | what the ground run measured: bodies, shores by kind, hills as modelled, the mesh | `scripts/ground1860.py` |
| `ground_check.json` | the joints and gaps, as `tools/check_ground.py` last measured them | `tools/check_ground.py` |

## The plain and the water

- **The plain:** 45.18 m at the scene's origin, falling 1.27 m per km towards 34° (north-east), rms 0.93 m over 7395 cells (`plain.json`). Today's five largest lakes the DEM reads unedited fall 0.8 m per km towards 26°.
- **The text says otherwise:** S05 j80 says the water was 西北高而東南低, high in the north-west and low in the south-east. Its inflow in the south-west and its outlets in the east (明春門, 七空闸 into 清河) fit a fall to the east. The model follows the DEM (Q197).
- **Water bodies:** 189, the polygons of `water_1860` touching within 1 m. Each lies at one level: 1.5 m (`FREEBOARD_M`) under the plain, taken as the median along its own shore. That gives 41.99-44.82 m (EGM2008), all C.
- **The land at the water:**
  - Near the water the land is pulled to that freeboard; 60 m away the plain rules.
  - 1.5 m lies between the album's bank tops (0.4-1.5 m) and today's step of 2-5 m from water to bank. Today's step holds trees and modern lining.
- **Depth:** 福海 2.3 m, small ponds (under 3000 m²) 1.5 m, all other water 2.0 m (S1002: 福海 about 2.3 m, 3.8 m at its deepest; 后湖 about 2 m; channels about 2 m; 长春园 and 绮春园 1.8-2.2 m. These are figures for today, read in a search extract, so C for 1860). The bed falls from the shore over 8 m.
- **Shores** (99.8 km), from `readings.csv` and two rules:
  - **Earth slope (77.2 km), the default.** The album's usual shore is a low grass bank. The land rises from the waterline over 10 m, so it stands 0.4-0.8 m above the water at 3-5 m from it.
  - **Stone (16.3 km).** A shore within 3 m of a hall, or 6 m of a landing, is stone. The album draws dressed stone under halls and terraces at the water, and Attiret has cut-stone quays where the galleries and paths end (S911). A stone shore takes the land's height or 0.9 m, whichever is higher, with a stone face down to the bed.
  - **Rock-faced (5.7 km).** Where a leaf or a text says rock for that scene and side, for example the islands of 蓬岛瑶台. 0.8 m above the water unless the row gives a height.
  - Kinds shown on a leaf are A; the heights are C. 19.1 km of the shore lies in a scene and on a side a leaf shows (A); the rest takes its kind from a text (B) or the two rules above (C).
- **Rockeries 假山:** 89 rows in 51 scenes (`rockeries.csv`). They are not drawn: they are left to the vegetation round.

## Hills

`layers/hills_1860`: the 54 outlines of S01 (`basis` plan) and 418 pieces of free land (`basis` free_land, H2001 on, `assumed: true`). Free land is land inside the walls more than 6 m from a hall, 2 m from a way, 4 m from a bridge, 2.5 m from a wall, 3 m from the water and 6 m from a landing, at least 5 m wide and 200 m². It is cut by the scene polygons, and the Xiyang Lou strip and 山高水长's open ground are kept out.

They are generated because the album rings nearly every scene with earth hills on its west, north and east, open to the water on the south (`readings.csv`, the album rows). This is the pattern of the album, not the place of any one hill. All together: 115.6 ha, against 4.9 ha of outlines on the plan.

**Height, the first method that gives one** (`hills_heights.csv`; counts from `tools/check_ground.py`):

| Method | Hills | What | Error |
|---|---|---|---|
| surveyed | 1 | 线法山: "圆形土山高约8米", the park's page (S1000), method not stated; today's hill | ±2 m |
| dem | 122 | today's GLO-30 rise inside the outline, at least 4 m over two cells, minus 2 m for trees, 2-12 m | ±3 m |
| painting | 96 | an album reading for that scene on that side; see below | ±3 m or half the height, whichever is larger |
| text | 1 | H0037 紫碧山房: "a 15-meter-high rock garden" (S1001, a newspaper, today's rockery); its outline of 191 m² holds 3.5 m of it | ±3 m |
| typology | 252 | a knoll under 400 m² 2.5 m; a courtyard hill up to 3000 m² 3.5 m; a major hill 8 m | ±1-3 m |

- **The album paints hills three to five times too tall.** Against the scene's largest hall, the main hills come out 2.5-4.5 ridges high, 10-70 m. Attiret, who was in the garden in 1743, gives 20 to 60 French feet, 6.5-19.5 m (S911 p.8).
- So a painting reading is scaled to fit: × 0.448, which puts the median of the 99 readings at the middle of Attiret's range, 13 m, and the result is clipped to that range. The scale is a run, not a source: the album gives which side carries a hill and which hill is the highest, not metres.
- **What the mound looks like:** each piece of land is one smooth mound. Its peak is at most 0.45 × its half-width + 0.3 m, so its flanks reach about 34°, an earth hill's steepest.
- **How high they come out:** modelled peaks have a median of 3.1 m (p90 6.5 m), and the highest is 12.9 m. The ratio of the modelled peak to the height estimate has a median of 0.91.
- **Halls on hills:** where a hall stands on a hill, its pad is cut into the hill.

## Pads and courts

- **Pads:** the boxes of one compound, nearer than 4 m to each other, share one pad: the median of the ground under their footprints, at least 0.4 m above the nearest water. Each pad reaches 1.5 m beyond the boxes and blends out over 6 m. There are 891 pads.
- **The sunken court:** 大水法's court lies 1.30 m below the ground round it (S603, survey; Q71).
- **Paddy:** 稻田 lies 0.25 m below the land (C).
- **Boxes on uneven ground:** where the mesh under a box is not flat (a pad's edge, a shore cell), the platform stands on its highest land, so nothing is buried past its platform.

## The mesh and the files

- **The design raster:** 2.5 m.
- **The mesh:**
  - Cells of 20 m are split to 10 m and 5 m while the raster departs from their corners' plane by more than 0.2 m.
  - The neighbours are balanced 2:1, and a cell the shore crosses is never coarser than its neighbours. The mesh has no cracks.
  - The land is cut exactly to the water polygons.
  - Land: 146441 vertices, 245821 triangles. Beds: 33954 triangles, on 20 m cells. Water: 22112 triangles.
- **Mesh against raster:** at the triangles' centres the median difference is 0.000 m, p99 0.73 m, max 4.3 m. The large differences lie in the 10 m cells the shore crosses, where the mesh has only the shore's points and the cell's corners.
- **The surface the view walks and drapes on is the mesh itself,** rasterised on the 2.5 m lattice (`ground_grid.i16`), so what is measured is what is drawn.
- **Generated files:** 7.28 MB in all (ground.bin 5.35 MB, ground_grid.i16 1.74 MB).

## Accuracy by region

From `docs/rounds/common/palace_r10_regions.py` (a record; it needs `raw/dem/`). Hill counts are by the hill's point inside the region. The water levels are those of the bodies that touch the region. The last column is the DEM's low ground against the plain's plane: how far today's open ground departs from one tilted plane.

| Region | Hills (plan + generated) | By method | Median height, error | Water levels | Plain: DEM low ground minus the plane |
|---|---|---|---|---|---|
| Xiyang Lou strip | 2 + 10 | dem 2, typology 10 | 3.5 m, ±1.5 m | 41.99-42.64 m (10) | rms 1.09 m, p90 1.73 m |
| 福海 and its shores (150 m) | 2 + 48 | dem 24, painting 11, typology 15 | 4.9 m, ±3.0 m | 42.64-44.04 m (34) | rms 1.26 m, p90 1.62 m |
| western plain (Yuanming Yuan west of x = -700 m) | 9 + 89 | dem 10, painting 41, text 1, typology 46 | 3.6 m, ±3.0 m | 43.4-44.82 m (40) | rms 1.36 m, p90 2.29 m |
| 绮春园 | 13 + 113 | dem 44, typology 82 | 3.5 m, ±1.5 m | 43.13-44.63 m (36) | rms 1.39 m, p90 2.36 m |

Every level and every hill but 线法山 is C. Absolute levels carry the DEM's own error (under 4 m LE90) on top of the plain's rms; the differences between two places are better, under 2 m on slopes (S159).

## The DEM

Copernicus DEM GLO-30 (S04, S159), tiles N39 and N40 E116, clipped by `scripts/clip_dem.py` (refetched in Round 10 from the open bucket `copernicus-dem-30m` on AWS: `research/raw/` had been cleared). 1 arc second: about 24 m E-W by 31 m N-S here.

- **Datum:** horizontal WGS84, vertical EGM2008 (EPSG:3855) (S159).
- **Stated accuracy:** absolute vertical under 4 m LE90, relative vertical under 2 m on slopes up to 20%, absolute horizontal under 6 m CE90 (S159).
- **Date:** TanDEM-X, 2011-2015 (S159). Later earth moving is not in it. The 2005 works are.
- **Type:** surface model. Trees and buildings are included. Water bodies are edited flat (S159).
- **Grid:** the GeoTIFF is `RasterPixel.IsPoint`, tie point 116.0, 41.0. So `north` and `west` in the npz are the CENTRE of row 0 and column 0: `lat = north - i*step`, `lon = west + j*step`. Reading them as edges shifts the DEM by half a cell (about 15 m N-S, 12 m E-W).

### Registration

The flattened 福海 cells (value 43.50) match the OSM 福海 polygon best at a shift of 0 m E, 4 m N, overlap 0.905 (0.891 at zero). OSM against Esri World Imagery z17: best shift 2.7 m E, 1.8 m N over 54 outlines. All three agree to within what they can resolve. GCJ-02 here would be 520 m E, 142 m N, 540 m in total.

### Surfaces today (metres, EGM2008)

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

- **Land medians include trees,** so the true ground is lower.
- **Today's levels:** take the water at about 42-43.5 m and the ground at about 45 m, with an error of 1-2 m.
- **Not the levels of 1860:** these are lined modern lakes (S148). The lakes that are not edited flat read lower than 福海, but the editing may make that difference.
- **The cleanest ground readings at the site:** the paddy at 多稼如云 reads 43.6-44.0 m, and open ground in the west about 45.5-46 m.

### Noise floor

The residual is a cell minus the median of the land cells 90-210 m away.

- **Open ground, 6 patches, 91 cells:** std 1.30 m, p5 -2.16, p95 1.86, max 3.19.
- **All park land, 3272 cells:** std 2.31 m, p95 4.52, p99 7.32, max 14.07.
- **Water not edited flat:** std 0.4-0.9 m per lake, up to 1.75 m.
- **Trees on flat ground:**
  - three conifer blocks: 1.2-3.1 m;
  - a block beside 线法山: 4.0 m;
  - a tall tree row south of the 长春园 lakes: 14.1 m;
  - the pine belt north of the 长春园 lakes: 11.8 m.

### What it can tell

- The lake and land pattern, the 2-5 m step from water to bank, and the overall slope (Round 10: 1.27 m per km towards the north-east).
- That belts of raised ground exist: 54 connected patches stand 4 m or more above their surroundings. In Round 10, 122 hills take their height from such a rise.
- That some places are flat and hill-free (藻园, 山高水长 field).

### What it cannot tell

- **The height of any single hill.**
  - Under 3 m is noise.
  - From 4 to 8 m, a low mound and a tree give the same signal; over 10 m it is canopy.
  - Most hills are narrower than 2-3 cells, and a real mound and a tree row can both reach 6-8 m.
  - The `dem` heights of Round 10 take the rise minus 2 m for trees, ±3 m, and stay C.
- **The 1860 surface.**
  - Hills were cut 1967-1973 and later (S145): 216 hills, the hills on the west shore of 福海, both sides of 多稼如云, and the south half of the west wall (S146, the hills survey worker).
  - The hills were rebuilt with modern fill: 12万 m³ of 挖湖堆山 by 2005 (S147).
  - So flat ground today does not mean flat ground in 1860.
- **The edges of ponds under about 8000 m².** They have too few cells.

## Better data

- **FABDEM** (S158): GLO-30 with trees and buildings removed, CC BY-NC-SA 4.0. Worth testing on one tile. It has the same 30 m cells and is non-commercial. Not downloaded. It may also remove real small mounds (assumed).
- **Others checked in Round 10 (`readings.csv`):**
  - OpenStreetMap has no `ele` tag, contour or hill feature in the box (S03), only the 线法山 point and a modern heap tagged as a peak.
  - OpenTopography holds no lidar here (S1013).
  - Two ICESat-2 tracks cross the box but miss the hills (S1014).
  - TanDEM-X 12 m is only on a DLR science proposal, and WorldDEM is commercial (S1016).
  - ALOS AW3D30 is 30 m, and its 12.5 m product is resampled (S1016).
  - Nothing open is finer than 30 m.
- **The real upgrade is on paper:** the 1933 survey map S15 says a 地形测量 was made and draws the hills; whether it has contours or spot heights is not known. The 1965 map predates the cutting of 1967-73. A Yangshi Lei plan of 1784 is drawn over a 10-丈 levelling grid (S1010). See `research/wishlist.md`.

## Round 20: beyond the walls

`scripts/ground_outer1860.py` (after `scripts/ground1860.py`) writes `site/reconstruction/generated/ground_outer.json` and `.bin`, `terrain/ground_outer_report.json`; `scripts/ground1860.py` also writes `terrain/ground_edge.json` (the inner ground along the domain's edge, every 2.5 m).

- **The ring:** 491 x 361 nodes at 20 m (x -5600 to 4200, z -3400 to 3800 m; 116.232-116.346 E, 39.970-40.036 N), heights in cm.
  - Its classes: plain 136,426 nodes, relief 27,135, lake bed 4,360, bank 22, paddy 9,308 (run).
  - The plain is the inner ground's plane (`plain.json`) extended (C).
  - The DEM is used only on massifs holding a named OSM peak, after an opening of 80 m that strips roofs and tree crowns: 万寿山 (47.7 ha, up to 50.5 m above the plain) and 玉泉山 with the hills north-west of it (1,044 ha).
- **The backdrop:** 346 x 261 nodes at 200 m, out to 115.77 E. The GLO-30 tiles N39 and N40 E115 were added to `raw/dem/`. The DEM is opened by 450 m and smoothed, so it gives the ranges' silhouette, not their detail; it is drawn under fog (6-40 km).
- **Lakes:** 昆明湖 (W0901) at 48.0 m, the DEM's median inside it, today's water. 未名湖 (W0902) crosses the domain's edge and takes the inner body's level, 44.63 m.
- **The join:**
  - At the 594 shared nodes of the inner domain's edge: 0 m (`tools/check_surroundings.py`).
  - Between them, against the lattice: median 0.002 m. The worst is 0.535 m at the bank by 未名湖 on the south edge, where the inner ground rises 1.4 m within 5 m; the view's fan through the inner edge vertices closes it.
  - Ring to backdrop: 0 m.
- **Limits:**
  - GLO-30 is a surface model of 2011-15. 万寿山 carries today's temples rebuilt in the 1880s-90s and today's trees, though its earth is that of 1750.
  - Everything else is the plane. Today's fill, cuttings and reservoirs are ignored, and so is any small rise of 1860 (Q280).

