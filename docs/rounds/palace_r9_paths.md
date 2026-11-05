# palace_r9_paths: roads, paths, galleries and water routes of 1860, and a walkable circulation in the 3D view

You are working in `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh`, the reconstruction of the Old Summer Palace (圆明园 Yuanmingyuan) before 1860. Read these first:
- `CLAUDE.md` (rulebook), `docs/METHOD.md`, `research/README.md`
- `research/questions.md` and `research/wishlist.md`
- `research/layers/bridges_1860.geojson`, `walls_1860.geojson` (gates), `water_1860.geojson`, `footprints_1860.geojson`, `scenes_1860.geojson`, `osm_today.geojson`
- `research/scenes/` (the dossiers of Round 7: routes, courts, landing stages)
- `research/georef/` (the improved fit of Round 8 and `check_points.json`; use the current fit, not the old one)
- `scripts/boxes1860.py` (the box generator), `site/reconstruction/3d.js` (camera and walk mode), `scripts/building_pages.py`
- `docs/rounds/palace_r6_xiyanglou.md`, `palace_r7_scenes.md` and `palace_r8_georef.md` for the working style

Everything is committed and pushed (the chain commits Rounds 7 and 8 before you start). The template project `/opt/data/workspace/000_Dev/kostrzyn-yaga-sh` is read-only: never edit it. Its `research/roads/` (`lines_1913.json`, `bridges_1913.md`) and `scripts/roads1913.py` show how roads and the railway were done there.

## What Tomasz asked for
"Do we have any information about roads and walking paths?" Answer so far: only bridges (73 lines), gates, water and today's OSM paths (a hint, not evidence). There is no layer of the 1860 walkways, courtyard paths, causeways, dikes, galleries and boat routes. He said yes to building it.

## Deliverables
1. **`research/paths/README.md`: what the sources say.** One section per source type, with the findings and the limits:
   - **Qing plans:** the Yangshi Lei ground plans and the 1920s and 1933 plans (what they draw: 甬道 paved ways, 游廊 covered galleries, 爬山廊, 垂花门, steps, bridges, 堤 dikes, 岸 landings, boat docks 船坞).
   - **The Forty Scenes leaves (1744) and later paintings:** how a visitor walks through each scene.
   - **Texts:** 日下旧闻考, the poems, the Qing guides and 1860 accounts that name routes ("from X go north to Y", a gallery of N bays), boat routes (the imperial boat's tour of 福海 and the 后湖), and the Chinese terms for each path type.
   - **Today's park:** which OSM paths plausibly follow old alignments (they sit on the old causeways and the lake edges) and which are modern. Say how you judged it. A modern path is never evidence by itself.
   - **Archaeology:** surviving paving, steps, causeways and bridge abutments from the excavation reports.
2. **Layers (WGS84 GeoJSON, in `research/layers/`, public copies under `site/reconstruction/data/`):**
   - **`paths_1860.geojson`:** LineStrings with `id`, `kind` (paved_way 甬道, gallery 游廊, mountain_gallery 爬山廊, causeway, dike 堤, bridge_approach, steps, courtyard_path, imperial_road, service_path), `name_zh`, `width_m`, `surface`, `from_id`, `to_id` (the building, gate, bridge or landing it joins), `sources`, `confidence` and `note`.
   - **`landings_1860.geojson`:** boat landings and docks (points or short lines) with the water body they belong to.
   - **`routes_1860.geojson`:** the named tours and ceremonial axes as ordered sequences of path ids (the emperor's daily way from 九洲清晏 to 正大光明, the boat tour of 福海, the Xiyang Lou axis, the processional way from the gate), each with its source.
   - **Confidence:** A where a Qing plan or period picture draws it. B where a later source or text only describes it. C for any connection added only so that buildings are reachable. Keep the C paths in their own `kind` or flag (`assumed: true`) so they can be switched off.
3. **Tracing method.** For each scene and compound, in the Round 7 priority order (the famous scenes first):
   - trace what the plan and the leaf draw, through the improved georeference, and snap the ends to the gates, bridges and doors of the boxes;
   - give every path a width from a source or from the typology (a 甬道 of about 2-3 bays wide; a 游廊 of one bay, about 2.5-3 m);
   - **check that nothing floats or hangs:** every path end meets a gate, a hall door, a bridge end, a landing or another path. Measure the gap of every joint in metres before and after. A path never ends in water or in the air, and never runs through a box. Report the numbers.
   - **Do not invent a network for unexplored areas.** Where nothing is known, add only the minimal C connections between a gate and the halls of a compound, and mark them.
4. **Bridges.** Reconcile `bridges_1860` with the new paths. Every bridge gets its approaches (paths at both ends) or a note why not. Add the bridges the plans show that are missing. Never renumber ids.
5. **3D view and walk mode.**
   - Add the paths to the 3D view as flat strips on the ground (with a simple surface colour per kind), galleries as roofed corridors (a low box roof on posts, simple), and the landings as small platforms. Toggle `paths=0|1`, and a legend entry.
   - Show the C paths in a different tint; `assumed=0` hides them.
   - **Walk mode:** make the camera able to follow a route. A route menu ("Walk the emperor's way", "Boat tour of Fuhai", "The Xiyang Lou axis") that moves the camera along `routes_1860` at eye height (about 1.6 m on land), pausing at named halls with their panel. A plain camera fly-through is enough; no collision physics.
   - Keep the other views unchanged. `?shot=1` turns off anything animated.
6. **Panel and pages.** An object's panel lists the paths that touch it ("Reached from: …") and the routes that pass it, with sources. The generators stay idempotent: a second run changes nothing.
7. **Checks and docs.**
   - **`tools/check_paths.py`:** counts by kind and confidence, the joint gaps (fails above 0.5 m for A and B paths), paths crossing a box or standing in water, bridges without approaches, and routes whose ids are all present. Run it with `scripts/building_pages.py` twice (the second run changes nothing), `tools/check_pages.py`, `tools/check_evidence.py`, `tools/check_georef.py` and `tools/check_docs.py`.
   - **Screenshots** in `screenshots/r9/`, from one page load: an overview with the paths on, 九洲清晏 with its galleries, 正大光明 and the gate approach, the Xiyang Lou axis, a bridge approach close-up, and a still from each route. Open each one yourself and fix what is wrong. Public views show no research-only image.
   - **Docs:** update `CLAUDE.md`, `research/README.md` and `docs/METHOD.md` (the paths phase: sources, method, what was assumed). Copy this brief to `docs/rounds/palace_r9_paths.md` and add its row to `docs/rounds/README.md`.

## How to work
- **Subagents in the FOREGROUND only:** several Agent calls in ONE message, never `run_in_background`. Never end your turn while a subagent, crawler or background shell still runs. Split by region (Yuanming Yuan east, west and Fuhai; Changchun Yuan and the Xiyang Lou; Qichun Yuan) and by source (texts, plans and leaves, remains). Give each one a clock deadline (`date -u`, 40 minutes per wave) and incremental notes in `/opt/data/cache/scratch/palace_r9_notes_<topic>.md`. You alone write the shared repo files.
- **Time-box** about 20 minutes per scene; breadth first, the famous ones before the tail. A missing piece becomes a wishlist row.
- **Copyright exactly as in `CLAUDE.md`.** Traced geometry is derived data and may be public with credit to its source. Research-only images stay in `research/raw/`.
- **Tools:** Python from the repo `.venv` via `uv run`. Node and Playwright in `/opt/data/cache/scratch/palace_r9_tools/`.
- **Ports** 8850-8859, bound to 127.0.0.1, stopped at the end. Never use 8790.
- **No git commands that write.** The chain commits and pushes.
- **Progress:** one line per milestone, at least every 15 minutes, to `/opt/data/cache/scratch/palace_r9_paths_progress.md`.
- Mark every claim verified, assumed or unknown. Never invent a path as A or B without a source.

## Final message
Lead with the numbers from `check_paths.py`:
- path length and count by kind and by confidence (A / B / C)
- how many scenes have traced paths
- the joint gaps in metres

Then list:
- what the walk routes are, and how they look
- what the sources could not tell, and the wishlist
- what is verified and what is assumed

Do not ask questions. Work only in this repo, plus the scratch paths named above.
