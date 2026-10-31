# palace_r2_map: the 2D dev map and the buildings as boxes in 3D (Yuanmingyuan, before 1860)

You are working in `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh`, a repo for a walkable 3D reconstruction of the Old Summer Palace (圆明园 Yuanmingyuan, Beijing) as it stood before October 1860. Read `CLAUDE.md` in this repo first: it is the project rulebook.

## Where things stand
- **Round 1** (research) is finished and committed locally. Read, in this order:
  - `research/README.md`, `research/questions.md`, `research/typology/halls.md` and `params.json`
  - the head of `research/buildings.csv`
  - the files in `research/layers/` and `research/georef/`
  - the end of `/opt/data/cache/scratch/palace_r1b_progress.md`, if it still exists
- **A simple homepage** is in `site/` (index.html, zh/, credits, styles). It links "Enter the reconstruction" to `reconstruction/`, and `site/reconstruction/index.html` is a placeholder you replace. Keep the homepage working; edit it only to point its button at the 3D view.
- **The template:** `/opt/data/workspace/000_Dev/kostrzyn-yaga-sh` (Küstrin 1913, live at https://kostrzyn-yaga-sh.vercel.app). Read its `site/reconstruction/` and its `tools/serve_local.py`, `scripts/building_pages.py`, `research/buildings/README.md` and one building page, and its CLAUDE.md sections on the working map, the 3D view, building pages and detailed models. **Never edit that repo** (other workers are running there). Copy and adapt its code; don't reinvent it.

## What Tomasz asked for
"Use what we did for Küstrin as reference: the folder structure, the homepage, the map preview, how we manage the buildings. 1) a map of the whole palace before destruction; 2) the old buildings, at the beginning as boxes, the same structure as Küstrin."

## Deliverables
1. **2D dev map:** `site/reconstruction/index.html` + `app.js` + `recon.css`, Leaflet vendored under `site/reconstruction/vendor/` (copy it from the Küstrin site).
   - **Layers:** every public layer from Round 1 (walls, water, islands, hills, bridges, scenes, footprints, buildings as points), plus today's park from OSM. Each has a toggle and a legend. Clicking a feature opens a popup with its names (zh, pinyin, en), sources and confidence.
   - **Overlay:** the georeferenced historical plan, with an opacity slider. If the plan is research-only, serve it only from localhost through `tools/serve_local.py` under `/_local/`, exactly like Küstrin's private overlay. `?public=1` shows what a visitor sees.
   - **Basemap:** OSM tiles, with attribution.
   - It is a dev page (`noindex`), reached from a small DEV MAP button in the 3D view.
2. **Public layers:** the scripts write the public copies to `site/reconstruction/data/`, in the Küstrin pattern (research copy in `research/layers/`, public copy without anything research-only). Nothing in `site/` may come from a research-only source except derived geometry credited to its source, as Küstrin did with its lots.
3. **3D preview (the way in):** `site/reconstruction/3d.html` + `3d.js`, three.js vendored. Keep it simple and solid:
   - **Ground:** the ground plane, from the DEM if Round 1 got one, else flat with the hills as soft mounds from `hills_1860`.
   - **Water:** water surfaces from `water_1860`, slightly below the banks.
   - **Islands and walls:** islands as raised ground; the garden walls as thin solids with gates.
   - **Every building as a box,** on a platform, with a simple roof from the typology (hip, hip-and-gable, gable or rolled ridge, with defaults by hall class).
     - Sizes come from `buildings.csv` and `footprints_1860`.
     - A compound without single halls gets a few boxes laid out from its typology. Mark those `assumed: true`, confidence C.
     - The European palaces (Xiyang Lou) get their own simple massing.
   - **Controls:** orbit and a walk mode if cheap; Küstrin's camera code is the reference.
   - **Click a building:** the panel opens with its names, garden, dates, sources, confidence and notes, and the camera zooms to it.
   - **URLs:** `?b=<ID>` does the same on load; `?shot=1` turns off anything animated, for screenshots.
4. **Boxes generator:** `scripts/boxes1860.py` (or a name in the Küstrin pattern) writes `site/reconstruction/data/halls_1860.geojson`, one feature per box. Each carries `id`, `parent_id`, `frontage_m`, `depth_m`, `platform_m`, `eave_m`, `ridge_m`, `roof`, `orientation_deg`, `sources`, `confidence` and `assumed`. Parameters are constants at the top of the script with their sources. It prints its checks: counts, overlaps between boxes, boxes standing in water.
5. **Building management, as in Küstrin:**
   - **`research/buildings/<ID>-<slug>/index.md`:** one page per building and compound, plus `research/buildings/README.md` (the list).
   - **`scripts/building_pages.py`:** writes the generated block between markers and never touches the `## Notes` part. It writes each page's public JSON to `site/reconstruction/data/buildings/<ID>.json`, and the full version to `research/raw/buildings/` for localhost. A second run must change nothing.
   - **`tools/check_pages.py`:** proves every clickable object has a page.
   - **`models/README.md`:** documents the detailed-model folder convention for later (`models/<ID>-<slug>/summary.json` with `hides`, as in Küstrin). Make no models now.
6. **`tools/serve_local.py`** (adapted from Küstrin: clean URLs, `/_local/` for the private layers and the overlay, `--public`) and `.claude/launch.json`. Clean URLs must keep working on the live preview at port 8790, which is a plain static server with `.html` fallback.
7. **Homepage:** point the "Enter" button at `reconstruction/3d.html`.
8. **Docs:** update `research/README.md` (rebuild order, public vs private) and `CLAUDE.md`. In CLAUDE.md, change only "Status" and add one short "Research"-style section on the dev map, the boxes and the building pages, in the Küstrin style, kept short.

## Verification (real, not claimed)
- **Screenshots:** Playwright headless, served by `tools/serve_local.py` on your ports, all shots of one page from a single page load (software WebGL is slow here: no GPU). Take:
  - the 3D overview of all three gardens
  - three close-ups: Zhengda Guangming / Jiuzhou Qingyan, Fuhai with Penglai Yaotai, the Xiyang Lou with Dashuifa
  - the panel open after a click
  - the dev map with all layers
  - the dev map with the overlay at 50%, on localhost only

  Save them in `screenshots/r2/` (gitignored). Open every one yourself and fix what looks wrong:
  - floating boxes
  - boxes in lakes
  - walls that cut through halls
  - z-fighting water
  - a camera that frames nothing
- **Health:** no console errors; no 404s; nothing under `site/` references a file outside `site/`.
- **Public check:** grep `site/` to prove no research-only image or plan is in it.
- **Generators:** `scripts/building_pages.py` twice (the second run changes nothing), then `tools/check_pages.py`.
- **Preview:** a final check that `http://127.0.0.1:8790/`, `http://127.0.0.1:8790/reconstruction/3d.html` and `http://127.0.0.1:8790/reconstruction/` load with a clean console. Port 8790 is the live preview (already running, serving `site/`); don't restart it.

## Rules
- **Ports:** yours are 8796–8799, bound to 127.0.0.1; stop your servers when done. Never use 8790 except for the final read-only check above.
- **Python:** the repo's `.venv` via `/opt/data/.local/bin/uv run`; don't add heavy dependencies.
- **Node:** install Playwright tooling into `/opt/data/cache/scratch/palace_r2_tools/`, not into this repo.
- **No git commands that write** (no add, commit, stash, checkout, restore, reset). Read-only git is fine. Lily commits.
- **Subagents only in the foreground** (several Agent calls in one message, never `run_in_background`). Never end your turn while a subagent or background shell still runs. Print mode kills background work about 10 minutes after your last turn, and an earlier round lost everything that way.
- Copyright and coordinates exactly as in `CLAUDE.md`.
- Mark every claim verified, assumed or unknown. Never invent a number, a date or a licence.
- Log one timestamped line per milestone to `/opt/data/cache/scratch/palace_r2_map_progress.md`.

## Final message
Lead with what Tomasz will see: how the 3D view and the map look, and how many boxes stand on a source versus on a guess (counts from the script). Then list:
- the files you made
- the flaws you saw in your own screenshots and fixed, and the ones left
- what is verified and what is assumed
- the obvious next rounds (detailed models first for which buildings, and why)

Do not ask questions. Work only in this repo, plus the scratch paths named above.
