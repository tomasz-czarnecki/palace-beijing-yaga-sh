# palace_r20_surroundings: what was around the palace: research and a first model of the surroundings

Round name: `palace_r20_surroundings`. Ports 8960-8969. Scratch notes: `/opt/data/cache/scratch/palace_r20_surroundings_*`.

## Why
Tomasz: "Do we have any idea what was around the palace? By now it is empty." Right: the data stops at the garden walls. Only 18 rows in `research/buildings.csv` have garden "outside the walls" (yard labels such as 船坞, 黄木厂, a ?旗房; the Z- ids), and `research/layers/fields_1860.geojson` has 10 rice-field polygons. Beyond that the view ends in a bare plain. Küstrin got a surroundings round (the land, roads, railway, the Oder island); do the equivalent here: research what stood and ran around the three gardens in 1860, and put a first, honest version into the 3D view.

## What to research (Chinese as much as English)
Leads, from general knowledge and not verified; check every one:
- **The 三山五园 belt:** 畅春园 (Changchun Yuan, southeast of us; Kangxi's garden, ruined by 1860), 清漪园 (Qingyi Yuan, about 2 km southwest, burned in 1860 and rebuilt as the Summer Palace in the 1880s: Beato's "before the burning" prints show it), 静明园 (Jade Spring Hill) and 静宜园 (Fragrant Hills), plus the smaller imperial and princely gardens of Haidian (e.g. 蔚秀园, 承泽园, 淑春园, 朗润园, 熙春园 and others). For each: where, size, state in 1860, and what the sources show of its buildings. Neighbouring gardens are context only: simple massing.
- **海淀 Haidian town** and the roads: the stone-paved imperial road from 西直门 to the gardens, the road to the Western Hills, the tracks to the villages; bridges and the 长河 canal (from the Jade Spring and Kunming lake to Beijing) and the other canals feeding the three gardens' lakes (the inflow and outflow: gates, sluices, 水闸, 涵洞).
- **The garrison and service quarter:** the Eight Banner camps ringed around the garden (圆明园八旗护军营, 内务府三旗, 外三营, 健锐营 at the Fragrant Hills), their barracks, drill grounds and parade grounds; the offices in front of the 大宫门 (六部朝房, 内务府, 总管衙门), the imperial workshops, storehouses, stables, timber yards and the boat docks (the outside labels on the plan).
- **The land:** rice paddies (京西稻), fields, orchards, villages, temples, tombs, wells, the sub-gardens 园户 households. The hills on the horizon: the Western Hills, which the garden's views were designed to borrow, and the nearer hills (万寿山, 玉泉山).
- **Sources:**
  - the 1864 plan of the palace's surroundings (Le Tour du monde, in `research/raw/plans/`) and the Malone 1934 sketch maps
  - the Yangshi Lei 三山五园 river maps; the 1860s British and French survey sketches; Bretschneider's 1876 map of Peking and environs; the Haidian maps of the 1880s-1910s
  - the 1920s Princeton plan and scrolls (what they show outside the walls)
  - the US Army Map Service 1:50,000 sheet of Peking (1944, in `research/raw/plans/`), as an independent check of roads, villages and canals
  - declassified imagery, OSM (ODbL) for today's roads and canals, the DEM
  - texts: 日下旧闻考, 清实录, the 1860 accounts of the advance on the palace (who marched where, from which village), Swinhoe, Loch, Wolseley, Hugo
  Everything gets a source id (new S-ids after the highest one), confidence A/B/C, and its place in the questions or wishlist.

## Deliverables
1. **`research/surroundings/README.md`:** one section per topic above, with what the sources say, where they disagree, and what remains unknown; the extent you decided to cover (state it: a ring about 2 km beyond the walls is the target, further for the hills and the neighbouring gardens as one-line entries).
2. **Layers (WGS84 GeoJSON, in `research/layers/`, public copies under `site/reconstruction/data/`):**
   - **`surroundings_1860.geojson`:** features with `id` (prefix `OW`, e.g. OW001), `kind` (neighbour_garden, town, village, banner_camp, office, workshop, storehouse, temple, road, canal, sluice, bridge, field, orchard, tomb, hill_far), `name_zh`, `name_pinyin`, `name_en`, `sources`, `confidence`, `assumed`, `note`. Positions through the improved georeference of Round 8; outside the original plan's area, anchor on today's survivors (roads, canals, hills) and the 1944 map.
   - **Extend `fields_1860.geojson` and `water_1860.geojson`** beyond the walls where the sources give canals and fields.
   - Add the 18 existing `Z-` rows to the layer or link them; never renumber.
3. **Ground beyond the walls.** Extend the terrain (`scripts/ground1860.py`) to the ring (open DEM; state its limits), with the nearer hills (万寿山, 玉泉山) and the Western Hills as a distant backdrop (a low-poly ridge line from the DEM, fogged), and the inflow canals meeting the garden's lakes at the sluices. Join to the existing ground without steps. Keep the generated data small (the whole round adds under 10 MB to the site).
4. **View:** the neighbouring gardens and the villages as simple massing in a muted tint (`around=0|1` toggle, on by default); roads as strips draped on the ground; canals as water bands; fields as tinted patches (green rice paddies in summer); banner camps and offices as rows of kit halls (use the hall kit for the offices at the main gate; the camps as plain low blocks); the horizon ridge; fog beyond the ring. Everything outside the palace walls carries its confidence tint with `conf=1` and `assumed=1` for guesses. Do not move anything inside the walls.
5. **Panel entries:** clicking an outside object opens a page like the others (names, what it was, sources, pictures if any, confidence), generated by `scripts/building_pages.py` (extend it for the `OW` ids), idempotent as before.
6. **Public page:** a short section on the site (`site/around/index.html`, EN and a zh draft, generated by a script) saying what surrounded the palace, with a plan of the surroundings from our own layers; free images only; linked from the homepage. Respect the sensitivity rule (the garden was destroyed from this ring: the 1860 advance came through these villages; state it factually).
7. **`tools/check_surroundings.py`:** counts by kind and confidence; every feature has a source; roads and canals connect to the garden's gates and sluices (gap in metres, fail above 1 m for A/B); nothing overlaps a wall, a hall or a lake; the ground joins without a step above 0.3 m; file sizes. Run it with `scripts/building_pages.py` twice (idempotent), `tools/check_pages.py`, `tools/check_ground.py`, `tools/check_paths.py` and `tools/check_docs.py`.
8. **Screenshots** in `screenshots/r20/`: the overview from high above (palace in its setting), the main gate with the office quarter and the Haidian road, a canal inflow at a sluice, the western view toward the Hills, a neighbouring garden, a banner camp; before and after. Check that nothing floats, that Chinese text renders (note if the screenshot browser lacks a CJK font), and that the join to the old ground is invisible.

## Task-specific rules
- Be honest about how little is known: most of the ring will be C. A believable, labelled setting is better than empty ground, and a confident fake is worse than either.
- Neighbouring gardens are not reconstructions: massing only, no detail, no claims beyond their sources.
- Keep ids stable; never touch anything inside the walls except the ground join.

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
