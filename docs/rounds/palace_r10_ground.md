# palace_r10_ground: ground generation: hills, ground shaping, lakebeds and a draped scene

Round name: `palace_r10_ground`. Ports 8860-8869. Scratch notes: `/opt/data/cache/scratch/palace_r10_ground_*`.

## Why
The 3D ground is nearly flat, and none of the 54 polygons in `research/layers/hills_1860.geojson` has a height (`height_est_m` and `height_method` are empty). The open DEM is 30 m (Copernicus GLO-30), too coarse for garden hills. Yet the garden was made of water and hills: 福海's banks, the 后湖 islands, the artificial hills (土山) that screen each scene. Boxes on a flat plane next to a 6 m hill look wrong at once. Küstrin did terrain first (`scripts/terrain1913.py`); do the same here.

## Deliverables
1. **Hill heights (`research/terrain/hills_heights.csv`, and the fields in `hills_1860.geojson`).** For every hill polygon: `height_est_m`, `height_method`, `error_m`, `sources`, `confidence`. Methods, in order of strength:
   - **Surveyed:** a published survey or excavation height (park, archaeology reports, Tsinghua surveys).
   - **DEM and today's remains:** where a hill survives (e.g. around 福海, 后湖 islands, 线法山, 含经堂 mounds), read the best open DEM, and any finer open height data you can find (OSM `ele` tags, published contour plans). Say what the 30 m DEM can and cannot show.
   - **Read from the Forty Scenes leaves and period paintings** by module: a hill's top against a hall of known height in the same view.
   - **Texts:** "山高五丈" and similar descriptions; convert 丈/尺 with 1 chi = 0.32 m and say so.
   - **Typology:** the class default for a hill of that area (an artificial hill of a scene courtyard: 2-4 m; a major island or mountain: 6-12 m), confidence C.
2. **Ground shaping (`scripts/ground1860.py`, extend it).**
   - Build a smooth ground from the hill heights, island banks and the plain's gentle fall (the sites's slope is small; read it from the DEM).
   - **Lakebeds and canals:** water surfaces at one level per body (read the levels from sources; the canal system fell gently from west to east, check this), banks sloping into the water with a bed 1.5-2.5 m below, and steep stone-faced edges where the texts say 石岸 (stone embankment).
   - **Courts and platforms** of halls stay flat; the ground blends into them without gaps or steps beyond the platform height.
   - **Chinese gardens' rockeries** (假山) are separate: leave them to the vegetation round, but mark where the texts describe them.
3. **Drape everything on the new ground.** The boxes, the paths strips and galleries of Round 9, the bridges, the walls and gates, and the Xiyang Lou terraces: every object's base follows the ground (or sits on its platform on the ground). Report the vertical gaps in metres before and after: nothing floats, nothing is buried more than its platform. Bridges meet the banks at both ends; measure each joint. Walls follow the ground with stepped courses, not a slab hanging in the air.
4. **View.** `ground3d`-style rendering in `site/reconstruction/` with a ground tint by confidence (toggle `conf=1` as the project does), contour lines as an option (`contours=1`), and no z-fighting between water and banks. The ground data stays small: keep the generated files under 8 MB in total (compress to int16 or reduce resolution where the terrain is flat).
5. **Accuracy and sources.** A short `research/terrain/README.md`: what is measured, what is read, what is typology, with the error per region (the Xiyang Lou strip, 福海, the western plain, 绮春园). Open questions go to `questions.md`; a wishlist row for any missing survey (the 1933 contour plan, if it exists).
6. **`tools/check_ground.py`:** counts hills by method and confidence; checks every hill has a height; reports every object's vertical gap (fail above 0.3 m for A/B objects); water bodies have one level each; no box in water, and no joint gap above 0.5 m for bridges and path ends.
7. **Screenshots** in `screenshots/r10/`: an overview, 福海 with its islands, 九洲清晏 and its water, a hill with a hall on it (e.g. 线法山 or 山高水长's surroundings), the Xiyang Lou strip, a bridge joint close-up; before and after. The terrain must read at a glance: hills as hills, water as water.

## Task-specific rules
- Be honest about what the 30 m DEM cannot show. Most hill heights will be C; say so and keep the error figures.
- Never move a box, wall or path horizontally; only the vertical fit changes in this round (Round 8 fixed the plan placement).
- Keep every id stable.
## Common rules for this round (read before the task)

You are working in `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh`, the reconstruction of the Old Summer Palace (圆明园 Yuanmingyuan) before 1860. Everything earlier is committed and pushed (the chain commits after each round). Read first: `CLAUDE.md` (rulebook), `docs/METHOD.md`, `research/README.md`, `research/questions.md`, `research/typology/halls.md` and `params.json`, and the latest entries of `docs/rounds/README.md`.

**The template project** `/opt/data/workspace/000_Dev/kostrzyn-yaga-sh` is read-only: never edit it. Its generators show the pattern: `scripts/terrain1913.py`, `scripts/greens1913.py` with `site/reconstruction/greens3d.js`, `site/reconstruction/typology3d.js`, `houses3d.js`, `ground3d.js`, `model3d.js`, `glb_lite.js` and its `models/<ID>/summary.json` convention (`models/README.md`).

**Standing modelling decisions of Tomasz** (from the Küstrin project, they hold here):
- **Approx is OK where evidence is missing.** Guess, mark it C with a one-line reason, move on. The goal is a realistic, good-looking view.
- **Every side gets detail:** estimate the undocumented façades from the documented bays or the typology (C), never a blank box. Windows must read as glass, recessed, with frames.
- **Everything connects:** nothing floats, nothing ends in the air or in the water. Measure joints in metres before and after.
- **Plain geometry by default,** no photo-textured façades.
- **Mark the fill.** Anything generated without a source for that specific object carries `assumed: true`, confidence C, and its own tint in the view. A switch (`assumed=0`) hides it or shows only what is sourced.
- **Numbers come from runs.** Every figure comes from a script run on the repo data.
- **Respect the sensitivity rule** in `CLAUDE.md`: factual and respectful, no cute framing.

**How to work:**
- **Subagents in the FOREGROUND only:** several Agent calls in ONE message, never `run_in_background`. Never end your turn while a subagent, crawler, server or background shell still runs. Give each a clock deadline (`date -u`) and incremental notes in `/opt/data/cache/scratch/<round>_notes_<topic>.md`. You alone write the shared repo files.
- Python from the repo `.venv` via `/opt/data/.local/bin/uv run`. Node and Playwright in `/opt/data/cache/scratch/<round>_tools/`, not in the repo. The server has no GPU: Chrome draws WebGL in software, so take all screenshots of one view from one page load, and keep parallel 3D jobs to a minimum.
- **Ports:** use only your own range (given in the task), bound to 127.0.0.1, and stop the servers at the end. Never use 8790 (the live preview).
- **No git commands that write.** The chain commits and pushes. Never edit `research/raw/` contents except to add files.
- **Generators are idempotent:** run `scripts/building_pages.py` twice (the second run changes nothing), then `tools/check_pages.py`, `tools/check_evidence.py`, `tools/check_georef.py`, `tools/check_paths.py` and `tools/check_docs.py`; all must pass.
- **Public site only gets free or derived data.** Research-only files stay in `research/raw/`. Keep the site growth of this round under 15 MB.
- **Screenshots** go to `screenshots/<round>/`, from one page load, each with a before and after where something changed. Open every one yourself and fix what is wrong. A lazy-loaded image that has not loaded, a floating sticky header, or an unreadable full-page capture counts as a flaw: shoot real viewports.
- **Docs:** update `CLAUDE.md`, `research/README.md` and `docs/METHOD.md` with what this round added and learned. Copy this brief to `docs/rounds/<round>.md` and add its row to `docs/rounds/README.md`.
- **Progress:** one line per milestone, at least every 15 minutes, to `/opt/data/cache/scratch/<round>_progress.md`.
- Mark every claim verified, assumed or unknown. Never invent a number, a source or a licence.
- **Final message** leads with the numbers from your check script, before and after, then what the view looks like now, what is still weak, what is verified and what is assumed. Do not ask questions. Work only in this repo plus the scratch paths named above.
