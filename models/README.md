# Detailed building models

One folder per modelled building, `<ID>-<slug>/`, as in Küstrin (`/opt/data/workspace/000_Dev/kostrzyn-yaga-sh/models/README.md`). The ID is the row of `research/buildings.csv` it replaces in the 3D view; the slug is the page's (`research/buildings/<ID>-<slug>/`). Round 13 made the first: `XY01-xieqiqu/` (谐奇趣, the pilot; its README has the method, the iteration log and the fit).

Each folder holds:
- `README.md`: the evidence (a `## Evidence` list), the method, the iteration log, where the model and the pictures disagree.
- The generator: a Python script writing `model.glb` with `scripts/model_mesh.py`.
- `params.json`: every figure with `value`, `source`, `grade` and `note`.
- `keypoints.json`: named points, local and scene, for `tools/plate_overlay.py`.
- `joints.json`: `joints` (where the model touches the ground), `entries` (doors and stair feet: the ways of Round 9 snap to them, `scripts/paths1860.py`), `footprints` (polygons the ways and the planting keep clear of, `scripts/greens1860.py`).
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

A generator defines each name as a point, or as candidates picked by the camera (`facing`, `left`, `right`). With no model, `tools/plate_overlay.py` derives the `blk_*` points from the stone kit's numbers.

**Checks.** `tools/check_models.py` fails on:
- a figure without a source;
- a GLB that does not load or is not published;
- `hides` naming the model's own box;
- a joint floating more than 0.5 m, or buried more than 1.0 m;
- a way ending more than 0.5 m from an entry;
- a file over the budget.
