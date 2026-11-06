# Detailed building models

One folder per modelled building, `<ID>-<slug>/`, as in Küstrin (`/opt/data/workspace/000_Dev/kostrzyn-yaga-sh/models/README.md`). The ID is the row of `research/buildings.csv` it replaces in the 3D view; the slug is the page's (`research/buildings/<ID>-<slug>/`). Round 13 made the first: `XY01-xieqiqu/` (谐奇趣, the pilot; its README has the method, the iteration log and the fit). Round 14 made the second: `XY08-haiyan-tang/` (海晏堂, the whole complex, west block to east stairs, with the water clock and the reservoir). Round 15 made the third and fourth: `XY10-da-shuifa/` (大水法, the niche, the piers, the stairs to 远瀛观, the basin, the two towers and the court's floor) and `XY11-guan-shuifa/` (观水法, the screen, the platform, the gates on the gardens' strip). Round 16 made the fifth and sixth: `XY09-yuanying-guan/` (远瀛观, the terrace with its forecourt, the hall with its wings, lanterns, clock gate and tiered roofs) and `XY06-fangwai-guan/` (方外观, the podium, the upper storey, the double roof, the curved stairs). Round 17 made the seventh and the first of a Chinese compound: `CC02-hanjing-tang/` (含经堂, the whole walled compound and its forecourt on its terrace, every hall inside the wall drawn by the hall kit in Python, `scripts/hall_parts.py`, and adapted to its evidence; the layout read on S01 in `plan_readings.csv`).

Each folder holds:
- `README.md`: the evidence (a `## Evidence` list), the method, the iteration log, where the model and the pictures disagree.
- The generator: a Python script writing `model.glb` with `scripts/model_mesh.py`. From Round 15 the frame from a box, the walk surface, the footings (`skirt`, `footing`), the joints, entries and footprints and the four JSON files come from `scripts/model_site.py` (`Site(box_id)`); 海晏堂 and the pilot keep their own copies. From Round 14 the façade openings, pilasters, entablatures, cartouches, balustrades, urns, jets and hip roofs come from `scripts/model_parts.py` (`Parts(mesh)`); the pilot keeps its own copies so that its GLB stays as it was.
- `views.json` (optional, Round 14): the model's own views, `[name, eye, target]` in its frame, for `tools/plate_overlay.mjs --views`.
- `params.json`: every figure with `value`, `source`, `grade` and `note`.
- `keypoints.json`: named points, local and scene, for `tools/plate_overlay.py`.
- `joints.json`: `joints` (where the model touches the ground), `entries` (doors and stair feet: the ways of Round 9 snap to them, `scripts/paths1860.py`), `footprints` (polygons the ways and the planting keep clear of, `scripts/greens1860.py`), and from Round 16 `decks` (raised floors the model draws and people walk on, a terrace: `name`, `y`, `poly`; `Site.deck` in `scripts/model_site.py`). `scripts/building_pages.py` publishes the decks in `models.json`; `3d.js` lays the ways that cross a deck on it, and `tools/check_models.py` measures a way's end there.
- `clear` in `joints.json` (Round 17, optional): polygons the planting keeps off without barring the ways (a paved court, a forecourt's lawns); `scripts/greens1860.py` also keeps off every deck. Footprints are what the ways route round: walls, platforms, galleries, rocks.
- `plan_readings.csv` (Round 17, a compound): every line the generator draws from the plan, in plan pixels of S01 with a note; placed by the fit in use (`scripts/georef.py` `plan_to_wgs84`).
- `report.json` (Round 17): what the generator measured (the deck's level, the joints on the deck, the halls' figures).
- `summary.json`: what the site reads.

```json
{
  "id": "XY01",
  "aliases": ["XY01-01", "XY01-N01", "XY01-02"],
  "name": "谐奇趣 Xieqiqu",
  "glb": "model.glb",
  "position": [466.299, 0.6, -733.096],
  "rotationY": 0.108246,
  "line": "One sentence for the panel: what it is modelled from, and what is assumed.",
  "rows": [["Main block", "27.2 × 8.6 m, three storeys ... (plates 1-2, P0187-P0189, C)"]],
  "caption": {"frontage_m": 27.2, "depth_m": 8.6, "eave_m": 11.6, "ridge_m": 14.0, "assumed": true, "confidence": "C"},
  "hides": []
}
```

- `id`: a row of `buildings.csv`. Its boxes in `data/halls_1860.geojson` (`building_id`) give way to the model.
- `aliases`: other rows the model draws (the octagons, the pool). Their boxes give way too, and their panels show the model.
- `position`, `rotationY`: scene coordinates of the model's origin (x east, z south, y above the water; `scripts/scene1860.py`), the main front towards +Z. The generator takes them from the main box (its middle and its front, as `halls3d.js` reads a box).
- `caption`: the panel's one-line size; `frontage_m` and `depth_m` replace the box's figures, so both are required.
- `hides` is optional: box ids standing inside the model that are not its own (`F0005`). Never a box of the model's own rows: those go by `id` and `aliases`.

**GLB.** One node, one mesh, a primitive per material. Positions are quantised uint16 with the node's scale and translation (KHR_mesh_quantization), normals int8. Every material is double-sided. A material named `<name>~fill` is a part carried round with no picture of it (assumed, C): the view hides it with `?assumed=0` and tints it pale with `?conf=1`, and the rest takes the C tint. `glass_*` loads with a small highlight. Budget: 1.5 MB compressed, 3 MB raw (`tools/check_models.py`). Read by `site/reconstruction/glb_lite.js`, copied from Küstrin, which here also honours `doubleSided`.

**Publishing.** `scripts/building_pages.py` checks every summary and copies the GLB to `site/reconstruction/models/<ID>/model.glb`. It writes `site/reconstruction/data/models.json` (`url`, `name`, `aliases`, `position`, `rotationY`, `caption`, `hides`, `boxes`) and puts `line` and `rows` into the panel (`model.detailed` names the model). `scripts/kit1860.py` gives the model's boxes `src` `model`: the kit draws nothing for them. `halls3d.js` puts them in a buffer of their own (`pM`) that hides once the model has loaded; they stay the click target. `3d.js` loads the GLB and tints it when selected. `model3d.js` (from Küstrin) shows it in the panel's "Our model now". A way the model draws itself (steps, galleries ending at its boxes) is not drawn as a strip; the exceptions for `tools/check_paths.py` are in `research/paths/exceptions.csv`.

**The key-point vocabulary** for a Xiyang Lou building, so that readers and generators agree. It was written for 谐奇趣 in Round 13; the generic part is the scheme.
- Compass corners (`_SW`, `_NE`) and the picture's left and right (`_L`, `_R`) as seen.
- A level and a part: `foot`, `base_top` (top of the ground storey), `wing_cornice`, `wing_rail`, `top_foot`, `top_cornice`, `roof_eave`, `ridge`.
- Openings: `win2_S_head`, `door2_N_head`, `topwin_S_head`.
- Stairs and pools: `stair_rail_S`, `nland_C`, `nstair_foot_E`, `pool_rim_W`, `nfount_rim_L`.
- The octagons and colonnades: `oct?_low_L` (the end of the face turned to the viewer), `oct?_lowout_L` (the outline's extreme), `col?_in`, `col?_out`.
- 海晏堂's kit baseline: `blk_foot_NW`, `blk_cornice_SE`, `blk_ridge_N`, `blk_eave_NE`, `blk_ped_apex_W`, `blk_door_W_head`, `blk_stair_land_W`, `pool12_rim_W`.

海晏堂's vocabulary (Round 14), the same scheme for a complex of several parts:
- The west block: the `blk_*` names of the kit baseline, plus `attic_top_N`, `attic_crest_top`, `colW_N_cap`, `midroof_ridge_N` (where the middle ridge meets a pavilion's hip), `wing_rail_NW`, `end_panel_N`.
- The terrace and the water clock: `terr_rail_N`, `stair_N_landing` (the post at the landing's front end, inner side), `stair_N_foot`, `zod_N1_head` and `zod_N6_head` (figures numbered from the back), `zod_plinth_N6_front`, `pool12_rim_W`, `pool12_rim_L` and `_R` (the rim's extremes as seen), `shell_top`, `vase_top`, `ped_N_top`.
- The water building: `link_rail_N`, `wb_foot_NW`, `wb_cornice_NW`, `wb_rail_NW` (the W end is the one by the west block), `wb_door_NW_head`, `wb_door_NC_head`, `wbpav_W_eave_NE`, `wbpav_E_ridge`.
- The east block: `es_door_head`, `es_foot_N`, `es_corner_NE_foot`, `es_L1_rail_N`, `es_L3_rail_N`, `es_top_rail_C`.
- The readers' brief with every definition: `docs/rounds/common/palace_r14_haiyan_vocab.md`.

大水法's and 观水法's vocabulary (Round 15, every definition in `docs/rounds/common/palace_r15_dashuifa_vocab.md`):
- The niche: `niche_crest_top`, `niche_head_top`, `niche_head_W` and `_E` (the shoulder scrolls' extremes), `niche_open_top`, `niche_open_foot_W` and `_E`, `niche_post_cap_W` and `_E`, `cascade_top`; the same points on the back carry `_N` (P0762, seen from the terrace).
- The piers: `pier_W_cap_SW`, `_SE` (and `pier_E_`), `pier_W_finial_top`, `pier_W_flare_S`, `pier_W_foot_S`. The stairs: `scroll_W_top`, `scroll_W_end`, `stair_W_rail_low`, `stair_W_rail_high`.
- The basin and the towers: `basin_rim_S`, `_W`, `_E`, `base_course_C`, `stag_top`, `stag_foot`, `tower_W_ped_top_SW` and `_SE`, `tower_W_ped_foot_SW` and `_SE`, `tower_W_top`, `twbasin_W_rim_L`, `_R`, `_S`.
- The screen (east is the picture's left on plate 16): `scr_cornice_E` and `_W`, `scr_endpier_top_E`, `pan_C_top`, `pan_C_foot`, `pan_E1_top`, `pan_E2_top`, `pan_E2_foot` (and `_W`), `socle_top_C`, `socle_foot_E`, `crest_top_C`, `finial_E_top`.
- The platform and its ornaments: `plat_front_C`, `steps_foot_C`, `_E`, `_W`, `throne_top`, `trophy_E_ped_top`, `obel_E_top`, `obel_E_foot`. The gates and the wall: `gate_E_top`, `gate_E_jamb_in`, `gate_E_steps_foot`, `wall_top_E` (and `_W`).

远瀛观's and 方外观's vocabulary (Round 16, every definition in `docs/rounds/common/palace_r16_yuanying_vocab.md`):
- 远瀛观: the wings `wing_W_foot_SW`, `wing_W_cornice_SE`, `wing_W_win_head`, `_sill` (and `_E_`); the lanterns `lantern_W_top`, `lantern_W_eave_L`, `_R`, `lantern_W_clock`, `lantern_W_rail_L`, `_R`; the centre `ctr_cornice_L`, `_R`, `ctr_foot_L`, `_R`; the order `col_W_cap`, `col_W_base`, `col_W_ped_foot`, `ent_W_top` (and `_E_`); `door_head`, `door_sill`, `ctrwin_W_head`, `ctrwin_W_foot_L`, `_R`; the attic `clock_C`, `clock_arch_top`, `clock_crest_top`, `attic_scroll_L`, `_R`; the roofs `scale_eave_L`, `_R`, `roof_C_eave_L`, `_R`, `roof_C_apex`, `crown_top`; the terrace `terr_rail_C`, `_L`, `_R`, `hall_step_C`. A point read from the north carries `_N`.
- 方外观: `pod_foot_SW`, `pod_top_SW` (and `_SE`), `porch_foot_L`, `porch_top_L` (and `_R`), `door_head`, `door_sill`, `oval_W_top`, `oval_W_foot` (and `_E_`), `step_foot_C`; `up_cornice_SW`, `_SE`, `_NW`, `_NE`, `upwin_C_head`, `upwin_C_sill`, `upwin_W_head`, `upwin_E_head`, `bal_rail_C`, `_L`, `_R`; `eave_lo_SW`, `eave_up_SW` (and `_SE`), `ridge_W`, `ridge_E`, `crest_top_C`; the stairs `stair_W_foot`, `stair_W_top`, `stair_W_out`, `stair_W_rail_foot` (and `_E_`), `end_W_win_head`, `end_E_win_head`.

含经堂's vocabulary (Round 17, a compound documented from its ruin, every definition in `docs/rounds/common/palace_r17_hanjing_vocab.md`): a platform's corners `<hall>_pl_foot_<SW|SE|NW|NE>` and `<hall>_pl_top_<...>` (compass on the plan), a flight's edges `<hall>_fl_<front|back|left|right>_<L|R>_<foot|top>` (L and R as seen standing before the flight), the terrace `terr_yard_<SW|SE|NW|NE>_<top|foot>`, `terr_W_end_`, `terr_E_end_`, `gate_flight_<L|R>_`, the screen `screen_foot_<W|E>`, `screen_base_top_`, `screen_top_`, the archways `pailou_<W|S|E>_base_<corner>`. The generator defines them for every hall it draws (`kp_platform`, `kp_flight`). A scene's key points, viewpoints and fit live in its own dossier folder (`tools/plate_overlay.py fit --sheets research/scenes/CC02-hanjing-tang`: `plate_keypoints.csv`, `photo_viewpoints.csv`, `plate_fit.csv`, `plate_cameras.json`).

**Overlays past a neighbour.** `node tools/plate_overlay.mjs --object <ID> --only` renders with the other detailed models hidden (3d.html `&plateonly=<ID>`, a development switch): 大水法's niche stands between every picture of 远瀛观 and the hall.

**Fits by part.** Where a plate draws the parts of a complex at different scales (plates 11 and 13 draw 海晏堂's water building 1.4 times too long against its west block), `tools/plate_overlay.py fit --parts 'west=^(blk|...)_;water=^(wb|wbpav|link)_'` fits a camera of its own to each part with six points or more (`part_<name>` in the fit table and in `plates.json`). It tests each part's own heights and widths; the disagreement between the parts is a question, not a residual to tune.

A generator defines each name as a point, or as candidates picked by the camera (`facing`, `left`, `right`). With no model, `tools/plate_overlay.py` derives the `blk_*` points from the stone kit's numbers.

**Checks.** `tools/check_models.py` fails on:
- a figure without a source;
- a GLB that does not load or is not published;
- `hides` naming the model's own box;
- a joint floating more than 0.5 m, or buried more than 1.0 m;
- a way ending more than 0.5 m from an entry (in plan and in height; on a deck, its height is the deck's);
- a file over the budget.
