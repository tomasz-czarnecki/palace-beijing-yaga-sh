# Detailed building models

Empty for now: Round 2 made boxes only. One folder per modelled building, `<ID>-<slug>/`, as in Küstrin (`/opt/data/workspace/000_Dev/kostrzyn-yaga-sh/models/README.md`). The ID is the row of `research/buildings.csv` it replaces in the 3D view; the slug is the page's (`research/buildings/<ID>-<slug>/`).

Each folder holds the evidence and method (`README.md`), every dimension with source and confidence (`params.json`), the generator, `model.glb`, and a `summary.json` that the site reads:

```json
{
  "id": "YM01-08",
  "aliases": [],
  "name": "正大光明殿 Zhengda Guangming Dian",
  "glb": "model.glb",
  "position": [-561.0, 1.5, 291.0],
  "rotationY": 0.0,
  "line": "One sentence for the panel: what it is modelled from, and what is assumed.",
  "rows": [["Foundation", "39.3 x 19.2 x 1.22 m (S02, B)"]],
  "caption": {"frontage_m": 39.32, "eave_m": 6.34, "ridge_m": 12.4, "depth_m": 19.2, "assumed": false, "confidence": "B"},
  "hides": ["F0005"]
}
```

- `id`: a row of `buildings.csv`. Its boxes in `data/halls_1860.geojson` (`building_id`) give way to the model.
- `aliases`: other rows whose page is this object, such as a hall drawn in the model.
- `position`, `rotationY`: scene coordinates of the model's origin (x east, z south, y above the water; `scripts/scene1860.py`), façade towards +Z.
- `caption`: the panel's one-line size; `frontage_m` and `depth_m` replace the box's figures, so both are required.
- `hides` is optional: box ids (`F0005`, `L002`) standing inside the model, hidden and not clickable as soon as the index is read. Never a box of the model's own row: those go by `id`.
- `ground_glb`, `photo_glb` are optional, as in Küstrin.

Not built yet: the publishing step. When the first model comes, add to `scripts/building_pages.py` what Küstrin's does (check each summary, copy the GLB to `site/reconstruction/models/<ID>/`, write `data/models.json`, put `line` and `rows` into the panel) and to `site/reconstruction/3d.js` the loader (`glb_lite.js`). Keep each GLB under 3 MB.
