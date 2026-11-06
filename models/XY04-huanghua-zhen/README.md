# XY04 黄花阵 Huanghua Zhen, the maze: the model built from the plate and the plan (Round 26)

The twelfth detailed model of the project, made by the pilot's method (`models/XY01-xieqiqu/README.md`). It covers the maze of the Xiyang Lou with its centre and its north hall (aliases XY04-01, XY04-N01):
- the **maze walls** of carved grey brick, 1.2 × 0.6 m (S310), as the plan S01 draws them: 171 runs, 1,233 m, traced in plan pixels by `trace_maze.py` and set into the block of S310 (58.56 × 88.64 m) where today's rebuilt maze stands; a coping, a framed band of raised keys on both faces for the 卐字不断 carving, clipped trees of three tiers on the copings every 5.5 m (plate 5);
- the **outer wall**, 276 m, 1.5 m high (C), open at the south gate (花园门 XY03 stands there: its own row, plate 4, drawn by the kit), at a **west and an east gate** with pineapple-finial piers and iron leaves (plate 5; S01's openings) and at the north behind the hall;
- the **drum** (12 m across, its top 3.8 m up, carved panels), the **straight flight** to a landing, the two **curved flights** of 20 steps climbing round the drum behind a carved **parapet** with a balustrade to meet at its back, the drum's balustrade and urn posts (plate 5; S01's ring and flight);
- the **pavilion** (XY04-01): an octagon 6.4 m across of four large faces with open arches and four small ones with windows (S258), corner columns, the entablature, a tiled **skirt**, the ribbed **dome** with cartouches, the open **lantern** and the gilt ball, 16.7 m above the ground;
- the **north hall** (XY04-N01): two storeys (S02), five bays, a **gable roof** with finials on the ridge's ends (plate 5), its terrace with balustrades and its flight;
- four **weeping pagoda trees** 龙爪槐 in round curbs at the inner corners (S310), a half-round **basin** before the hall (S01), and the paved floor of the paths (assumed).

It is a showcase of the method, not a one-to-one reconstruction. Every figure is C unless `params.json` says otherwise. The square pavilion on the hill to the north (XY04-N02, scene CC22) and the gate 花园门 (XY03) are not part of it.

Files:
- `trace_maze.py`: reads the plan S01 (`research/raw/plans/princeton_mosaic.jpg`, local only), thins the ink inside the outer wall to centrelines and writes `plan_readings.csv` (committed): the walls `W001`-`W171` and the rows `RECT`, `RING`, `STAIR`, `HALL`, `BASIN`, `GATE_*`.
- `huanghuazhen.py`, the generator, on `scripts/model_site.py` and `scripts/model_parts.py`; it writes `model.glb`, `params.json`, `keypoints.json`, `joints.json`, `summary.json` and `report.json`.
- The frame: origin on the south wall's centre line at its middle (box XY04-M10, `front_offset` 0), x east, y up, z south; the block from z 0 to z -88.64.
- Run: `uv run python models/XY04-huanghua-zhen/huanghuazhen.py`, then step 6 (`scripts/paths1860.py`, `scripts/kit1860.py`, `scripts/greens1860.py`, `scripts/building_pages.py`). The test: `tools/plate_overlay.py fit --object XY04 --shots screenshots/r26`, `node tools/plate_overlay.mjs --object XY04 --fits all --out screenshots/r26`, `tools/plate_overlay.py compose --object XY04 --shots screenshots/r26`, `tools/check_models.py`.

## Evidence

Every picture named here is free, as `research/photos/catalog.csv` records. The research-only items (the impressions of plate 5 at Manchester, the NYPL, the Getty and the V&A; the Yangshi Lei plan 样337-146, E0945 and E2411; the reconstructions R0096, R0139, R0181, R0186) are only cited.

**From the south (the only side any period picture shows)**
- **Plate 5** (P0045, 花园正面, 1783-86, the Palace Museum impression): the whole maze from high in the south: the outer wall with the side gates and the stream outside, the walls with their bands and clipped trees, the four weeping trees, the drum with its flights and parapet, the pavilion, the north hall's roof. 44 key points read by the Round 26 reader (6 sure 1, 26 sure 2, 13 sure 3).
- **Today's rebuilt maze** (P0733, P0734, P0735, P0737, P0739, P0350, P0351, P0506, P0507, P0736, P0783, 2002-2018): the walls' height and section and the outline of the rebuild of 1987-89 (S847, S310). The rebuild is not the original (the pavilion was redesigned): used for the block's place and size, never for a form.
- **Ohlmer's view of the strip** (P0779, 1867-1879): the maze's place among the ruins; no form.

**Plan, texts and figures**
- **The plan S01** (B): every maze wall as one ink line, the ring with its steps, the octagon, the straight flight, the north hall's grid with its flights, the basin, the dotted paths through the openings in the outer wall. Its maze reads 73.7 × 99.3 m (Q292).
- **S310** (B, a lead with no survey cited, method e): the block 58.56 × 88.64 m (183 × 277 尺), the walls 1.2 × 0.6 m, about 1,600 m of wall in all, carved 卐字不断 brick, the tree circles with one 龙爪槐 each, the clipped trees on the plates; sods laid on the walls in 1793.
- **S02 p.145** (B): carved brick walls about shoulder high topped with little pines; an octagonal pavilion in the centre; a two-storey building at the north end. **S258 pp.178-179** (B): an octagon on a circular base, arches on its large faces, windows on the small ones, a dome.
- **S850** (B): today's rebuilt outline 55.5-58.7 × 88.4-89.5 m, read on imagery in Round 6.
- **Not in hand**: the Yangshi Lei plan 黄花阵地基图样 样337-146 (National Library of China), on the wishlist; it would replace the trace of S01 and every size of the centre.

## How it was built

1. **The walls from S01.** `trace_maze.py` thresholds the ink inside the outer wall (darker than 110), masks the ring, the stair, the hall and the basin's wave marks, thins the rest to one pixel (Zhang-Suen), traces the chains, drops the dots of the paths (shorter than 9 px) and the joins into the outer wall's band, and writes 171 lines. Mapped onto the block by the outer wall's rectangle (S01's double line, W 8706, N 415, E 9056, S 888 px), they come to 1,233 m; with the outer wall's 276 m, 1,509 m against S310's 'over 1,600 m' (6% short: some short pieces S01 draws were dropped as dots).
2. **v1** from the dossier, plate 5 and S01: the centre's sizes read on plate 5 against the pavilion's width (C), the north hall at S01's grid on the block, the gates where S01 opens the outer wall.
3. **Fits** on plate 5 (`tools/plate_overlay.py`, 44 points): 1.99 m rms. The reader saw a **gable roof** on the north hall, not the hip of v1: with the ridge over the whole length, 1.61 m.
4. **Tests, not tunings.** The centre scaled 0.65-1.2 times (1.0 best: 1.61 m; 0.75: 2.17 m; 1.2: 1.86 m); the drum and ring alone at 5.4/7.4 m, 5.0/7.0 m, 4.6/6.6 m (1.59-1.61 m: no difference, so S01's ring stays); the block at S01's 73.7 × 99.3 m (2.05 m) and at 66 × 94 m (1.74 m) against S310's 58.56 × 88.64 m (1.61 m): plate 5 bears out S310's proportions (Q292).
5. **Found on the shots and fixed**: the side gates' leaves drew as a black slab (now bars and rails); two close-up cameras stood in the garden wall and on a coping (moved).

## The fit (plate 5, P0045)

| Fit | Points | rms | median | max |
|---|---|---|---|---|
| all | 44 | 39.3 px, 1.61 m | 1.04 m | 4.95 m (`owall_top_NW`) |
| stretch (k 1.10) | 44 | 40.3 px, 1.69 m | 0.95 m | 5.24 m |
| anchored (on the outer wall's corners and the gate's ends) | 44 | 64.0 px, 2.65 m | 2.30 m | 4.91 m |

By part (all): the pavilion and the drum 0.74 m rms over 16 points (max 1.19 m); the hall 1.32 m (6); the trees 1.16 m (4); the side gates 1.80 m (8); the outer wall 2.49 m (8, max 4.95 m at the far corners); the ring's sides 2.67 m (2).

## Where the model and the plate disagree

- **The engraving's perspective is constructed.** The far wall converges more than any pinhole camera allows against the near wall and the side gates: the far corners stand 4-5 m off, the side gates 1.8 m (Round 6: 'an imagined view', the eye about 48 m up). The reader also found the plate tilted (the near wall's top falls 12 px left to right) and the east gate drawn 26 px lower than the west one. None of this is tuned into the model.
- **The ring's sides** sit 2.7 m out and high on the plate whatever the ring's size: the plate draws the flights lower at the sides than a steady climb from the landing to the back gives. Kept: S01's ring, the steady climb (C).
- **The block**: S01 draws it 73.7 × 99.3 m, S310 and the rebuild give 58.56 × 88.64 m; plate 5 fits the latter better (Q292).
- **The south gate** (XY03) is the kit's tall box; plate 5 draws two finial piers and an arched screen behind them, and the near wall stops 2-3 m further from the axis than the box's width allows (`swall_top_gate_L` 2.3 m). For a model of 花园门 from plate 4.
- **The north hall**: only its roof shows; its two storeys are Malone's (S02), its façades carried from the group (assumed).

## Iteration log

- v1: 90,457 triangles, plate 5 1.99 m.
- v2: the north hall's gable roof (1.61 m); the tests above; the side gates' bars; 90,777 triangles (6,781 fill), GLB 2.75 MB, 0.87 MB compressed.
