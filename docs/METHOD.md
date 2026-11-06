# How to reconstruct a lost historical site

The playbook drawn from this project, the Old Summer Palace before 1860, and its sister Küstrin c. 1913 (`/opt/data/workspace/000_Dev/kostrzyn-yaga-sh`). Follow it for any town, palace or fortress. The result is a public website with a walkable 3D view in which every object opens a page showing its evidence.

**How to read the figures.** All times are UTC on 2026-10-31, from `docs/rounds/README.md`, the git log and the progress logs. Times per worker come from the modified time of its notes file, so they are approximate. Counts are as of commit 0bb4f81, except phase 11 and what cites Round 5, and phase 12, Round 6 on 2026-11-01.

**The whole run:** six hours by the clock, from the rulebook at 15:04 to the commit of Round 3 at 20:56, and about $178 as reported by the rounds' result rows. It took one failed run. It went this fast because Küstrin already gave the structure; expect longer without a template.

## The shape of it

| # | Phase | Inputs | Outputs | Scripts | Time here |
|---|---|---|---|---|---|
| 1 | Rulebook | the brief, a sister project | `CLAUDE.md`, `.gitignore` | none | not recorded; committed 15:04 |
| 2 | Homepage | rulebook, sister site, one free image | `site/` with credits and placeholder | none | 8 min |
| 3 | Research | rulebook | `research/sources.md`, `questions.md`, `wishlist.md`, notes | `scripts/fetch_osm.py`, `scripts/clip_dem.py` | 25–32 min per worker, pictures 102 min |
| 4 | Georeferencing | base plan, today's map, imagery | `research/plan/`, `research/georef/` | `scripts/mosaic_plan.py`, `scripts/trace_plan.py`, `scripts/georef.py`; Round 8: `scripts/georef_readings.py`, `scripts/control_derived.py`, `tools/georef_crops.py`, `tools/check_georef.py` | tracing 31 min, control points 37 min; Round 8 about 1 h 30 min: blind check set and control by six readers in two waves (18:12-18:57), fit, walls, docs |
| 5 | Inventory | texts, plan, control points | `research/buildings.csv`, `research/layers/` | `scripts/build_r1.py` | texts 25 min, plan readers 19 min, merge 10 min |
| 6 | Typology | building rules, stated sizes | `research/typology/params.json` | `scripts/typology_rules.py`, `scripts/typology_scale_check.py` | 30 min |
| 7 | Dev map | the layers | `site/reconstruction/index.html`, `app.js`, public layers | `scripts/publish_layers.py`, `tools/serve_local.py` | 11 min, shared with phase 8's data |
| 8 | Boxes in 3D | layers, typology, DEM levels | `3d.html`, `3d.js`, `halls3d.js`, `data/halls_1860.geojson`, `generated/` | `scripts/scene1860.py`, `scripts/ground1860.py`, `scripts/boxes1860.py` | 3 min for the view after that |
| 9 | Building pages | rows, boxes | `research/buildings/`, `data/buildings/`, `panel3d.js` | `scripts/building_pages.py`, `tools/check_pages.py` | 9 min |
| 10 | Evidence hunt | every object as a list | `research/photos/catalog.csv`, `research/evidence/` | `scripts/photos_catalog.py`, `scripts/apply_facts.py`, `tools/check_evidence.py` | 102 min |
| 11 | Twins and others' reconstructions | every object, its evidence | `research/twins/`, `research/reconstructions/` | `scripts/building_pages.py`, `tools/check_evidence.py`, `tools/serve_local.py` | 101 min |
| 12 | A deep dive, ready for models | the famous part, its pictures | `research/xiyanglou/`, `site/xiyanglou/` | `scripts/xiyanglou_dossiers.py`, `scripts/xiyanglou_page.py`, `scripts/boxes1860.py` | see the rounds' log |
| 13 | The same, for the whole site, breadth first | every compound, the catalogues | `research/scenes/`, `site/scenes/` | `scripts/scenes_dossiers.py`, `scripts/scenes_page.py`, `scripts/apply_facts.py` | 8 workers 35-40 min, then 3 more 12-30 min; about 1 h 45 min by the clock |

Phases 3 to 6 ran together as one round, 142 min. Phases 7 to 9 ran as one round, 30 min. Next come detailed models, which here have not started (`models/README.md`); phase 12 picks what to model first and gives it its numbers.

## The phases

### 1. Rulebook

Write `CLAUDE.md` before anything else, because every later worker starts from it. Fix the following:
- the **target state**, one date, and what evidence counts towards it;
- the **purpose**: here a showcase, so approximate is fine where evidence is missing, marked C, with research time-boxed per object;
- **confidence grades**, **evidence order**, **copyright classes**, **coordinate rules**;
- the **layout**, with what is never public;
- **who commits** and which ports are whose;
- the **tone**, if the subject is sensitive.

Copy the shape of the sister project, then rewrite each rule for the new place. Do not copy a fact.

### 2. Homepage

A small public page first: it fixes the look, the credits page and the deploy shape, and the 3D view gets an "Enter" button to land behind. Check the licence of the one image on its holder's page. Keep claimed numbers out until a script has produced them. Test on a plain static server and on one imitating the host's clean URLs (`tools/serve_local.py`).

### 3. Research

Fan out by topic, one foreground worker each: **maps and plans, the text inventory, pictures, building typology, today's site and archaeology.** Reserve an S-id block per worker so ids never collide. Have each write notes as it goes, with a coordinator alone writing the shared files.

Before launching, write a skeleton of every deliverable. Give the workers a shared brief; `docs/rounds/common/` holds the two used here.

**The main decision is the base plan.** One plan drawn with every building, at a known date, turns everything after it into reading rather than guessing. Hunt it first and record what it is, when it dates to and how sure you are (Q2, Q3).

**Date the base plan against the texts straight away.** Here the check came two rounds late: the labels at 九洲清晏 turned out to be names of a decree of 1873 (Q36), after the boxes were built on them.

### 4. Georeferencing

1. Stitch scans into **one pixel grid** and never change it: all plan coordinates refer to it (`research/georef/princeton-mosaic.json`). Keep the stitch reproducible from the holder's server: here `research/raw/` was cleared between rounds, the four IIIF images were fetched again and `scripts/mosaic_plan.py` gave the same grid.
2. Trace the plan by script, with manual inputs as small files that give a reason for each entry (`research/plan/*_manual.*`). Keep it deterministic: rerunning here gives identical files.
3. Pick control points on **what survives unchanged**: shores, ruins, islands. Record the datum per point. Round 1: 159 points, 111 in the fit (59 shore, 51 ruin, 20 island, 15 wall, 14 junction among all).
4. Compare transforms by leave-one-out RMS, in a metric projection. Here thin-plate spline, 16.5 m, beat similarity at 33.6 m, affine at 28.7 m and polynomial at 22.0 m.
5. **A blind check set, fixed before any fit** (Round 8, `research/georef/check_points.json`). Readers who never see a prediction or an error find each feature by its form on two crops, today's imagery and the plan, the plan crop's centre shifted at random so it gives no hint (`tools/georef_crops.py`); they read on zoomed crops with labelled grids, skip on doubt and never edit a written point. Keep check points apart from the fit points (here 30 m; 60 m between check points) and keep every new control point 60 m from any check point, or off the same pool or platform. Freeze the set by hash (`scripts/georef.py freeze`) and let a checker fail on any edit or on a region getting worse (`tools/check_georef.py`). Round 1 edited its check set after seeing errors: its median went from 52 m to 31 m; Round 8's blind set gives 19.8 m for the same fit.
6. **Expect a thin check set where the site is well used.** Round 1's fit already held most sharp features that survive, so six readers found 19 points at 60 m from them and 22 at 30 m (a rule changed before any error was computed, and written down). Four of six regions have three points or fewer: report n beside every figure, and say what the figure can't tell.
7. **Piecewise, region by region, with the previous fit as the fallback.** A thin-plate spline whose smoothing is set per region by leave-one-out on the control points; scored on the check set against the previous fit and a plain affine; where it does worse in a region, a grid of points every 50 m from the previous fit holds it there (`scripts/georef.py`). Keep the previous fit in the repo and rebuildable (`princeton-1920s.previous.json`, `georef.py previous`). Here the new fit won nowhere by more than 0.4 m and lost in YM west and east, which keep Round 1's: the plan cannot be placed better than the surviving ground allows.
8. **Control points derived by script** (`scripts/control_derived.py`): a lake that keeps its outline gives its centre, and a large one each quarter, by the shift that lays the traced shore on today's; only where the shores agree (median under 6 m after the shift, 60% within 10 m, the traced water 0.7-1.4 times today's) and leaving out the shore near any check point. Map through the previous fit only, so the file does not depend on the fit it feeds and the chain is a fixed point. Exclude what a reader saw re-dug, rebuilt (the maze) or placed by interpolation.
9. Report by area what the plan reads to, not one number, **and by kind**: here foundations in place read 2-8 m off, shores and channel mouths at re-dug places 14-46 m. Publish it as a layer (`research/layers/georef_error.geojson`, the dev map's "Placement accuracy").
10. Measure the plan's scale; don't trust the stated one. Here 1:1070 against a stated 1:1300, and buildings are drawn at another scale from the ground.
11. **Walls: measure them against today's line before moving them.** Here the south wall agreed with the rebuilt wall to 4-5 m, the north wall stood 17-53 m inside it, and the plan draws three parallel lines there (Q186): left as traced, with the doubt written down. Where a wall runs through ruins in place and the plan's line there is a guess (a scroll seam), the ruins win: move the run, say by how much, and move its gates with it (Q64).

### 5. Inventory

Merge two lists: what the **texts** name and what the **plan** draws.
- A worker extracts rows from the texts, with quotes (`research/plan/inventory_texts.csv`).
- Detect buildings on the plan by script: `research/plan/blocks.csv`, 1453 blocks, precision about 0.92 and recall about 0.85 by eye on three crops.
- Plan readers, one per area, tie labels to blocks by viewing crops: `research/plan/readings/`, with `read` as `sure`, `likely` or `guess`, and adding or rejecting blocks.
- One script merges it all, `scripts/build_r1.py`. It holds the decisions as constants and prints its counts. Spot-check at random: here 12 `sure` rows viewed, 12 right.

An unnamed block gets a row. Something with no position gets a row and no invented position.

### 6. Typology

Defaults by class of building for what no source states: heights, roofs, bays. Each number has a source and a grade (`research/typology/params.json`). A stated size in `by_name` always wins. Rule arithmetic and the scale check are scripts, so the numbers come from runs. State how narrow the basis is: here roofs rest on two album leaves and a modern summary of the rules.

### 7. Dev map

A Leaflet page with one toggle per layer, doubling as the legend, with popups, for checking the data. `noindex`, reached only from a small button in the 3D view. On localhost it also offers the plan as an overlay, from `/_local/`. `scripts/publish_layers.py` makes the public copies and drops working fields. Vendor the libraries.

### 8. Boxes in 3D

Every building as a box before any detail: a whole site is what impresses, and it exposes data errors that a table hides.
- One shared frame, `scripts/scene1860.py`: scene metres, base levels.
- `scripts/ground1860.py`: land cut to the water layer. Use the DEM for base levels only, because it holds today's trees and fill.
- `scripts/boxes1860.py`: one feature per box, with `basis` saying what it stands on and `assumed: true` for a guess. It prints checks: overlaps, boxes in water, walls through boxes.
- Merged meshes with picking in the browser. URL switches for screenshots: `?b=`, `?shot=1`, `?conf=1`.

### 9. Building pages

One page per row and per gate, written by a script, with a hand-written `## Notes` the script never touches, and two JSON copies: public, and local with the private fields. `scripts/building_pages.py` asserts what may be public, by key. `tools/check_pages.py` proves every clickable object has a page, and that a second run changes nothing.

### 10. Evidence hunt

Goal: **no empty panel.** Breadth first, then depth on the famous objects.
1. Give the workers the object lists as TSV, with names, gardens and positions.
2. Wave 1 by kind of source. Here eight topics: dated Qing texts, Malone and Western witnesses, Qichun Yuan, Qing art, old photographs, Yangshi Lei drawings, archaeology, modern photographs.
3. Workers write JSON lines with a fixed schema (`source`, `picture`, `evidence`, `fact`, `question`, `wish`; see `docs/rounds/common/palace_r3_subagents.md`). They write nothing in the repo. The coordinator merges and verifies.
4. Build the panel on the first merge, then measure the gaps with `tools/check_evidence.py`.
5. Wave 2 on the gaps. Here four topics: the park's compilations, exact-phrase search on Commons, the Yangshi Lei site again, and halls and gates still bare.
6. Verify: compare quotes against the fetched text by script, sample links, view screenshots. Here 149 of 149 日下旧闻考 quotes and 40 of 40 prefaces matched, and 88 of 92 from Malone.

Say what was searched. A hall with nothing of its own shows "Evidence for the whole compound ..." and a line of what was searched and not found.

### 11. Twins and other people's reconstructions

The owner's reaction to phase 10 will be "most of those places are just sketches". For a lost site that is true, and two things can still put real images on the panels: **what still stands that is like it,** and **what others have built.** Both are kept apart from the evidence on screen and in the data, and neither ever sets a position or a size.

1. **Twins.** Hunt the **stated relation first**: Qing texts name their models (`S05`: 文源阁 「天一取阁式」, 如园 「略仿瞻园」, 安佑宫 「恭仿寿皇殿之制」). A worker reads the texts and writes pairings; another, the only one on Commons, finds pictures from the same list as it grows. Grade the relation A, B or C; a pairing with no source is `comparable`, C, with its reason. Add **a comparable per class of hall** in a page of its own, so every plain hall reaches a standing building. Say when a twin is a rebuild.
2. **Reconstructions.** Author, institution, year, method as stated, on every row. Note **what state each shows**: here some aim at 1744, and the card models of 1873–74 are period objects, not modern ones. Free images come mainly from **open-access papers**: read the licence on the paper, take only figures with no other credit, open every one.
3. **Keep a record of what stays off the panel.** Here 22 rows: models of the zodiac heads, items of another garden.
4. **Panel order:** period evidence, reconstructions (labelled modern interpretation, not evidence), comparables (labelled not this building), the set of buildings. Compounds' rows reach halls by the same fallback; garden and class come folded.
5. **Measure before and after,** with a file fixed before the round (`research/evidence/coverage_before_r5.json`).

### 12. A deep dive: dossiers and dimension sheets

Breadth leaves the famous part as thin as the rest. Before modelling, take the part people know, here the ruins of the Xiyang Lou, and go through it building by building.

1. **Fan out by topic again,** in the site's language too: every impression of the key plates; surveys, drawings and archaeology; ruin photographs and rephotography; fragments, period texts and materials; pictures' sides; perspective; footprints. Seven workers, then a wave on the gaps.
2. **A dimension sheet, with a method per figure.** a a published survey; b measured on the plan or the ruin, by script; c read from an engraving by perspective; d a photograph with a known object; e typology, or a figure with no survey behind it. Keep every reading, also the ones that disagree: the disagreement is a finding. A tourist page is e, whatever it says.
3. **Perspective reading of engravings,** by worker with a script: overlay a numbered grid on crops and read pixels on a displayed crop, never from memory; find the horizon and vanishing points; note whether the façade plane is frontal; take a scale from a width measured on the ground; test the focal length on a plate that has something measured on it, and say that it is carried to the rest as an assumption. Give the error: at least ±10% unless two plates agree. Where a plate can be tested, here it squeezed widths to about 60%, so heights hold better than widths.
4. **Measure footprints on what is there,** by script, and test the plan's scale against what has a surveyed size. Here it held at ratio 1 in this strip, against what the method said elsewhere.
5. **Fix the inventory from the evidence,** with facts: name a part, merge it, retire it, never renumber. `correct` rows keep the old figure in the note, and a generated row stays generated.
6. **Side per picture.** Each picture states which face it shows and how well it serves a modeller (`views.csv`). The panel and the page group by it. Then the gaps show as missing sides.
7. **Then and now.** Only pairs where both were opened. Say exact, close or rough.
8. **A public page from the dossiers,** generated, so it stays in step, with a key plan drawn from your own layers.
9. **Verify before it goes public.** A worker with no part in writing the text checks each sentence against the source cited, and marks it held, changed or not verifiable. Here 195 checks gave 33 changes: a throne platform called lost that stands, a gate called rebuilt that nobody has seen, one side of a dispute given as fact, a search extract stated as a dig report. Do this after any prose written from workers' notes.

### 13. Breadth dossiers: every compound, scene by scene

Once the famous part has its dossiers, everything else still shows its compound's fallback. Do the same for the whole site, in waves by fame, with a dossier for every compound even where little is known: here 81 scenes and compounds in four waves.

1. **Generate the dossier from what you hold, before any research.** `scripts/scenes_dossiers.py` writes a full dossier for every compound from the inventory and the catalogues alone: halls with sizes and fronts, evidence per hall, pictures, texts, reconstructions, questions, wishes. Research then fills hand-edited sheets beside it (`about.json`, `halls.csv`, `dimensions.csv`, `views.csv`, `digs.csv`, `interior.csv`), and nothing is ever blank: an empty section says "not written yet", and what the catalogues hold stands below it.
2. **Split by source, not by scene,** with the waves inside each worker: texts (two workers), drawings, digs and studies, today's photographs (the only one on Commons), the period pictures read for a modeller, and two breadth workers for the minor gardens. Every worker cites the catalogue rows by id, so the dossier text links to the evidence the panel shows.
3. **Read the album leaves hall by hall.** One worker, local images only, enlarged crops on a grid: bays, storeys, roof form, tile colour, columns, for every hall it can tie by position. It gave the roofs of all 40 scenes, which the typology had sampled on two leaves, and it tied 66 pictures to halls. Its finding that the 1887 lithograph re-cuts the 1745 woodcuts tree for tree took one side-by-side crop.
4. **Take the Qing figures as written.** Yangshi Lei slips write 丈尺: record the original, the 营造尺 used (0.32 m) and the metres, method a. A plan of a later repair (here Tongzhi's, 1873-74) is a later source for the target state: grade it B, never A, however exact its figures.
5. **Let figures correct the inventory through facts,** not by hand: a hall's overall frontage and depth from a method-a figure replace the plan's estimate (`apply_facts.py`), a text that says which way a hall faces turns an assumed front (only a half turn; a quarter turn is a question). Rebuild the rows from their inputs (`build_r1.py`, then `apply_facts.py`) every time the facts change, so a trial run leaves nothing behind.
6. **Measure what you can by script:** each scene's outline, its islands and the water inside it, on your own traced layers (method b, status `run`), counted apart from the figures research brought.
7. **The typology check comes free** once figures carry a method: compare the measured halls with the class defaults by script and propose, don't apply. Here the residential "grand halls" stood 0.6-1 m lower in the column than the audience hall the default was taken from.
8. **Public pages only for the best documented,** by a stated score and two rules a reader would expect (at least one free picture, enough text), and a hub listing every dossier so each panel can link to its summary.
9. **Check every sentence before it goes public,** by workers who did not write it, and keep the checks (`research/scenes/checks.csv`). Here 275 sentences: 154 held, 116 changed, 5 not verifiable. The same workers then wrote the zh drafts from the corrected text.

### 14. The ways: roads, paths, galleries, landings and boat routes

Boxes on a plain are not yet a place you can walk. Round 9 drew the circulation of 1860 (`research/paths/README.md`):
1. **Ask each kind of source the same question, how did one get from here to there,** each its own worker: the plan read region by region (what it draws: galleries as narrow bay rows, steps, dikes as land strips, a few labelled roads; courts and their axes, but no paving across them), the period paintings read for circulation (paved ways, galleries, steps, landings, moored boats, how each scene is reached), the texts (routes "from X to Y", boat trips, ceremonies, terms), the digs (landings, steps, aprons; no published path width).
2. **Readers trace in plan pixels with the ids they join,** not in metres: the coordinator puts every line through the georeference in use and snaps the ends, so a later refit moves the ways with everything else. A crop tool with absolute pixel labels and the ids drawn (`docs/rounds/common/palace_r9_tools/crop.py`) made that quick: five readers traced 611 lines in 20 minutes.
3. **Snap, measure, never hide a gap.** Each end to a door (a side mid-point of its box, the least detour), a gate, a bridge end, a landing or another line; the gap before and after is in the layer and the check fails above 0.5 m for an A or B line. A line through a box or water is rerouted on a fine grid near its trace, and what cannot be is written in `exceptions.csv` with the reason: here land necks under the traced water, stairs inside the Xiyang Lou terrace boxes, roads running beyond the trace.
4. **Grade by what draws it:** A for a period picture or a dig, B for the base plan or a text, C for inference. Raise traces by a mechanical match to the leaves (same scene, kind, an end in common), not by eye.
5. **Add only what makes a hall reachable,** marked `assumed`, in its own mesh and tint, so it can be switched off. Here the links outnumber the traced lines: say so, and show the view without them.
6. **Routes are waypoints, not drawings:** the shortest way through the network between halls a source names, with the stops. Where the network falls apart, one marked link, and the route's note says what is our choice (here: the bridge the emperor crossed).
7. **Today's paths are a hint, never evidence:** judge them by script against the old water and halls (on fill, modern; on a shore, a dike or a traced way, plausible) and keep them out of the layer.
8. **Fix the layers you lean on when they are wrong,** in their inputs: two bridges had been read along their decks, not across the water; ids stay.

### 15. The ground: hills, water levels, banks, and everything draped on it

Boxes on a flat plane next to water read wrong at once. Round 10 shaped the ground (`research/terrain/README.md`):
1. **Find out first what the base plan draws.** S01 draws halls, shores and rockeries 假山 as black hatched clumps, but no earth hills: a hill reading of the plan could never be enough. Look at three crops before planning a reading pass.
2. **Ask each kind of source for heights, and expect few.** Five workers, in the foreground, about 25 minutes: surveys and data, the Qing texts, the water, and the album in two halves. One published hill height came back (the park's 8 m for 线法山). The texts give positions ("殿後為山") and no figure. The album gives where the hills stand and what each shore is, but paints hills three to five times too tall against its own halls. Use a painting for ranking and sides, and scale it to an eyewitness range (Attiret's 6.5-19.5 m) by a run, not by eye.
3. **A ladder per object:** surveyed, today's DEM, painting, text, typology, the first that gives a figure. Each hill keeps its method, its error and the readings it used (`research/terrain/hills_heights.csv`). A 30 m surface model is not a hill survey: only a rise over 4 m on two cells counts, minus 2 m for trees, and the result is C.
4. **Generate what the sources say exists but nobody drew,** marked `assumed`, on the land nothing else needs (free land: away from halls, ways, bridges, walls, landings, fields and shores). Make it switchable (`assumed=0` flattens it and gives it level ground's colour). Here that was 111 ha against 5 ha drawn: say so plainly.
5. **Water at one level per body,** a body being the polygons that touch. The level comes from the plain along its own shore. The land is pulled to a freeboard near the water and left on the plain far from it. A text that disagrees with the DEM on the fall (S05: high north-west; the DEM: falls north-east) goes to the questions.
6. **Banks by kind:** an earth slope by default, stone where a hall or a landing meets the water, and a leaf or text for a scene and side. An earth bank's bed starts just under the water, with no skirt. Stone and rock get a face down to the bed.
7. **Pads, not tilted boxes:** the boxes of one compound share one level, blended out. A box on ground that is still not flat stands on its highest land.
8. **The surface that is walked and draped is the drawn mesh itself,** rasterised. Every check measures against what the view shows: boxes (floating, buried past the platform), ways (strip points, ends against decks and platforms), bridges (deck ends), walls (stepped courses), landings. Measure the old state with the same script (`--before`).
9. **Size:** a quadtree mesh (20, 10 and 5 m cells, 2:1 balanced, cut cells never coarser than their neighbours) with int16 positions and uint16 indices in chunks took 24 MB down to 5.4 MB. The walk raster covers only where anything stands.

### 16. The kit: every building drawn from its numbers

Boxes say where and how big. A kit says what kind of building. Round 11 (`research/kit/README.md`):
1. **Numbers in a generator, shapes in the browser.** `scripts/kit1860.py` writes every hall's bays, porches, steps, roof class, tiles and band, and where each comes from (`src`, `fig`). `kit3d.js` turns them into geometry and adds no number of its own. So the check and the panel can read what is drawn, and a better source changes one row, not the code.
2. **The kit draws inside the box and never moves it.** The platform is the footprint, the columns stand its edge inside, the roof reaches the overhang beyond, the heights are the box's. Measure it: track every vertex's distance outside the footprint, by part (body, roof, steps). A probe that only samples the ground must not count.
3. **Fix the typology before you draw it.** A class default taken from the grandest hall (正大光明殿's 5.12 m column) makes the whole class too tall. Re-read the defaults against the measured halls of the class (medians, by a run) before the kit makes them visible.
4. **A hall's own figure wins, and says so.** Dossier figures by method (survey, ruin or plan, painting, photograph) set the box; a roof or tile read for that hall on the album sets its roof. Everything else is the class's, flagged `assumed`, and the panel says "drawn from the typology of its hall class, not from a picture of this hall".
5. **Every side gets detail.** Rear façades get windows and sometimes a door. Gables get brick and a panel (硬山) or windows. Steps go where the ways of the paths round arrive, not only at the front. A side over water gets none.
6. **Nothing below the roof pokes through it.** A band 0.2 m outside the column line at the eave's height shows as a stripe along every roof. Cap every band, beam and wall top at the roof's own profile there.
7. **Cost: levels of detail by tile, built lazily.** A near level for 1634 halls at 740 triangles each is 1.7 M triangles, and with float colours and normals about 0.9 GB. Build the far level (76 triangles a hall) at load, and a tile's near level only when the camera comes near. Drop far ones beyond a cap. Store colours as bytes, and let the material shade flat (no normals). Measure frame time and triangles before and after in one session (`tools/check_kit.py --browser`); software WebGL varies by a quarter between runs.
8. **`assumed=0` shows what is sourced.** Hide the boxes with no block. Draw a hall whose form is only its class's as its plain box. Keep the kit where the hall's own figures drive it.
### 17. The planting: species from sources, places generated

No plan draws a plant, so a planting layer is two separate claims: what grew in a scene (the sources), and where each plant stands (generated). Round 12 (`research/greens/README.md`):
1. **One row per scene, plant and place a source supports,** before any geometry (`research/greens/species.csv`). Readers split by source family (poems and prefaces, the album leaves in halves, later texts, survivors and eyewitnesses) and write a controlled `place` (a side of the scene, the shore, the courts, beside a named hall, on the water), the source's own words beside it, and a count where the picture or text gives one. Reject allusions and figures of speech with the reason: in this corpus a third of the plant words were names, metaphors or Buddhist images.
2. **Two grades per area.** The species takes the rows' grade; the extent is B only where a picture shows that side of the scene, C where a text names it or the whole scene. The fill (planting no source names) is its own kind, `assumed`, with its basis written in the area, and switched off with `assumed=0`.
3. **Anchor to the scene's own geometry,** never to the painting: the outline, its water, islands, hills, courts and halls cut the zone; the painting gives the side and the count.
4. **Clearance by the crown, not the trunk.** A crown that reaches over a roof is a tree through a building. Keep every crown its radius from the boxes, let a tree beside a hall shrink to 60% rather than drop, keep trunks off way strips, walls, bridges and landings, and land plants off the water by a margin. Check every plant against the same files the view draws (`tools/check_greens.py`).
5. **Store the base, check the slope.** Each plant's base is the walk surface at its point; sink the trunk 0.5 m and refuse a place where the ground falls further than that within the trunk's reach. A lotus or reed takes its body's level, never a place where two levels meet.
6. **Bake, don't instance, in software WebGL.** 180 k instanced triangles cost about 500 ms a frame there; the same plants baked into merged meshes per 200 m tile (a far level of 14-triangle lumps, a near level within 260 m) cost about 120-160 ms. Leave sub-pixel plants (flower beds, floating leaves) out of the far level.
7. **Counts from the text are counts of a specimen, not of a grove.** "A large weeping tree" is one tree; "thickly planted" is a density. Restrict word counts to specimens, give a specimen with no count a few trees and a flower bed a few dozen plants; an area-sized count for a specimen filled a maze court with 98 trees.

## The data model

**Hand-offs are plain files,** each step reading the last one's output:

```
georef/readings_r8/ -> georef_readings.py -> check_points.json (frozen), control_r8.csv
plan/regions.json, layers/osm_today, buildings.csv + facts -> control_derived.py -> control_shapes.csv
princeton-1920s.csv, control_*.csv, check_points.json, princeton-1920s.previous.json -> georef.py fit -> princeton-1920s.json
plan/*, inventory_texts.csv, typology/params.json, georef/*.json, xiyanglou/boxes.csv (courts, walls off the ruins)
  -> build_r1.py -> buildings.csv, layers/*_1860.geojson
check_points.json, princeton-1920s.json -> georef.py accuracy -> layers/georef_error.geojson
evidence/facts.csv -> apply_facts.py -> buildings.csv
layers/ -> publish_layers.py -> site data
layers/ -> ground1860.py -> generated/
layers/, buildings.csv, params.json, generated/ground_grid.i16 -> boxes1860.py -> halls_1860.geojson
photos/catalog.csv -> photos_catalog.py -> web copies, credits
buildings.csv, catalogues, questions.md, sources.md, halls_1860 -> building_pages.py -> pages, panel JSON
```

**Ids.** S sources, Q questions, P pictures, E evidence, and building ids that say where a thing is: `YM03` a compound, `YM03-11` a hall from the texts, `YM03-N02` first named on the plan, `YM03-B0835` an unnamed block, `Z-B1234` in no compound, `G01` a gate. Ids are never renumbered, because rows cite them. The full table is in `research/README.md`.

**Confidence.** A = shown on a source made while the site stood, or measured on unchanged remains. B = a later source, or a written description. C = inferred, every guess. Grade **what** and **where** apart (`confidence`, `pos_confidence`), and record how the reading was made (`read`). A grade may be held down for a stated reason: S01 stays B until Q2 is settled, so no box is A.

**Catalogues are sources of truth.** `research/photos/catalog.csv` and `research/evidence/catalog.csv` are hand-edited after the round that builds them. Both tie to objects the same way: `shows` = `ID:sure|likely|guess;...`, a garden tag for a whole garden. `rights_class` is `free` or `research-only`. Evidence also has `status`: `viewed`, or `snippet` if seen only in a search summary, and the panel says so.

**Facts apart from rows.** A fact goes in `research/evidence/facts.csv` with its source, quote and a `decision`: `apply`, `name`, `note`, `gate` or `lead`. A script applies it, so a conflict stays visible rather than being overwritten, and a `lead` waits for someone to read it.

**The panel JSON.** `site/reconstruction/data/buildings/<ID>.json`; its keys are in `research/README.md`. Order on screen: own pictures, own texts and drawings, the plan as a link, what was searched, reconstructions by others, surviving comparables, what speaks for the set of buildings.

**Parent fallback ("set of buildings").** Most buildings of a lost site have no picture of their own: here 937 of 1510 halls show only the plan and their compound's evidence. So a page holds a reference, not a copy: `fallback` = `[{kind, id, name}]`, `kind` being compound, nearest (with the distance) or garden. The panel fetches that page, so nothing is written twice, and the heading says plainly that this is evidence for the compound. `GARDEN-*.json` holds what speaks for a garden.

**Boxes state their basis.** `basis` = `plan`, `stated`, `xiyang`, `layout`, `default`, `gate`; `assumed: true` for a guess. `?conf=1` colours by confidence.

## The copyright model

| Class | What | In git | On the site |
|---|---|---|---|
| Free | public domain, CC0, CC BY, CC BY-SA, licence checked on the holder's page; PD-Art of pre-1900 two-dimensional works on Commons | yes | yes, credited |
| Free with a condition | BnF / Gallica: non-commercial, credit "Source gallica.bnf.fr / BnF" | yes | yes, so the project stays non-commercial |
| Research-only | everything else, and every NC or ND licence | no copy, `research/raw/` at most | a link card: title, date, holder, what it shows, "View at ..."; on localhost the local copy, marked |
| Tiles | Esri, Google and others | never | dev-map basemap only |
| Traced geometry | our tracing of a plan with no copyright on it, credited | yes | yes |

**Rules that held up:**
- **Facts are not copyright.** A research-only source can be cited for a fact in our words.
- **Quote only the public domain.** Qing texts are quoted; modern work is summarised in one to three sentences of our own.
- **Licence as stated, per file.** Album leaves on Commons here carry different tags. Quote the tag in `licence`.
- **One way in.** Web copies reach `site/` only through `scripts/photos_catalog.py`, which refuses to run on a research-only picture in a public folder or a public picture with no credit.
- **Checks, not care.** `tools/check_evidence.py` fails on a research-only image, a missing file or copied research-only text. `site/.vercelignore` and `.gitignore` are a second lock.
- **Unsettled calls go on a list for the owner:** Q6 and Q50 here.

## Source strategy

**What gave most:**

| Kind | Here | What it gave |
|---|---|---|
| Measured plan | S01, Princeton | every position and footprint: 1560 boxes. Nothing else comes close |
| Compilations of period texts | S360, S361, the park's own PDFs | 1445 of 2397 evidence rows, dated poems hall by hall |
| Period gazetteer | S05 日下旧闻考, on Kanripo | the scene-by-scene inventory, 150 rows |
| The standard monograph | S02 Malone 1934 | the plan's identity, measured foundations, 96 rows |
| Painted albums and engravings | S08, the woodcuts S76, the gouaches S77, the 20 plates | form and roofs: the free core of the pictures, but only for the Forty Scenes and the Xiyang Lou |
| Later editions | S260, lithograph of 1887 | 80 free pictures and text pages for all 40 scenes |
| Old photographs | S86 Östasiatiska, S280 Skušek, Commons | ruins in form; captions often wrong |
| Drawing archives | S13, S310 Yangshi Lei | what stood by date, but research-only and often search summaries only |
| Archaeology | reports and press | measured sizes, as facts only; 48 rows |
| OSM and imagery | S03, S160 | the anchors of the georeference; hints for names, with errors (Q32) |
| DEM | S04 | base levels only |
| Wikipedia | S06, S07 | leads and a first timeline; B at best |
| Open-access papers | S108, S590–S594, S605, S606 | the free reconstructions: 17 of the 23 on the site, some by the Tsinghua team itself under CC BY |
| Qing texts, read for models | S05 | 14 of the 15 relations at grade A |
| Commons, patiently | S440, S640 | 153 twin pictures, at about 15 calls between 429s |
| A modern monograph that weighs the claims | S415, Rabreau 2022 | what about the European models holds, which is little |
| Old photo collections at holders | S460, S465, S654 | five free ruin plates and much correction; most captions are wrong (Q60) |
| The first book on a subject, reprinted on Commons | S871, Teng Gu 1933 | free copies of the five Ohlmer negatives no holder would give free |
| A dense modern article, read as page images | S603 Durand, S600 Shingei | the only stated survey of the strip, and the dated story of the water machines |

**How to search:**
- **In the site's language as much as in English,** then the languages of those who were there: French and English eyewitnesses here. The best material was never in English.
- **Go to the catalogues,** not only the search engine: Commons API with category and `deepcat` searches, Internet Archive full text, Kanripo's GitHub for Chinese texts, K-samsök for Swedish holdings, national library portals, the site's own administration.
- **Read the standard monograph early.** Malone pp.231–232 identified the plan as the "Official Map" and gave its scale and history.
- **Name by name once you have an inventory.** Then a list of unnamed blocks is honest about why nothing can be found.
- **Check form against caption.** Several captions were overruled by the plate of the same building (Q49).

**What blocked** (Q33), and what to do about it: never work round a bot check, log-in or paywall. Log it, add a wishlist line, move on.
- mhymy.com drops every record page, so 87 Yangshi Lei rows rest on search summaries.
- yuanmingyuanpark.cn answers in bursts, then times out.
- ctext.org has a security check; Kanripo's GitHub text served instead.
- Gallica's licence page refuses automated access.
- Commons and Wikisource rate-limit at about 9–14 requests a minute on a shared address: 187 name searches did not run, so "no picture found" there is not proof.
- A session's web search budget ended at 200 searches, at 19:45 in Round 3. Keep some back for the last wave. Round 5 gave each worker a share and stayed within it, at about 170.
- Round 5: Duke, Harvard's API, Gallica's SRU, the Library of Congress, Getty, and most of mhymy.com. Q62 has the full list; `research/wishlist.md` says who could open them by hand.

- Round 6: Duke, Gallica's SRU, Smithsonian, the Library of Congress, Harvard, Yale, Manchester's LUNA, the British Museum, NYPL's item pages and most of mhymy.com, by bot check or refused connection; Commons' image host answered 429 with Retry-After 600 twice. Public IIIF manifests and Manchester Digital Collections answered where the portals did not. Fetch at 1280 px, one every 6 s.
- Round 7: mhymy.com answered all day, one request every 6 s, about 95 record pages: catalogue header and introduction free, slips and images behind a reply wall or payment, so 70 Yangshi Lei rows moved from search summary to viewed but most 丈尺 stay out of reach. yuanmingyuanpark.cn timed out on 38 of 39 pages for ten minutes, then answered. Commons answered 429 seven times; it is exhausted for these scenes, and Openverse (20 results a page, not 50) reached free Flickr sets that Commons lacked. Not tried, as asked: Duke, Harvard, the Royal BC Museum. Web searches: 61 by the workers' own counts, well inside the budget.

**The wishlist is a deliverable.** What, what it would replace, where it is held, how to ask (`research/wishlist.md`).

## What was specific to China

- **Shifted datums.** Amap/Gaode, Tencent and Google's road tiles inside China use GCJ-02, a few hundred metres off (540 m here); Baidu uses BD-09. This project used only OSM and Esri, which are WGS84, and checked them against each other: 2.7 m E, 1.8 m N over 54 outlines. Record the datum of every control point.
- **Catalogues in Chinese,** with holders that rarely state a licence: so most modern Chinese material is research-only, and its facts are cited. Yangshi Lei drawings are expensive in print and hard to read online.
- **Reign dates.** Some records convert them wrongly (Q51): use the reign date as stated.
- **Name variants.** One place has several written forms and plaques moved (Q20). Keep them in the row and don't merge on spelling alone.
- **The topic is a national wound.** State who, when and what. No sensational or cute framing, and the twelve zodiac heads stay out of any playful content. The Küstrin speech bubble and sway were removed from the homepage for this reason. Keep looting and burning apart, as the sources do; the first draft of this rulebook blurred them.
- **Chinese fonts** are large. The site uses subsets of the characters in use, and a new character falls back to a system font until the subset is rebuilt. A long Chinese page gets a subset of its own with a `unicode-range`, in a stylesheet only it loads, so the homepage stays light.
- **No native reader yet.** The `zh/` page is a draft.

## From Küstrin: what carried over and what differed

**Carried over:**
- the layout: `site/` as the only public folder, `research/`, `scripts/`, `tools/`, `models/`;
- S, Q and P ids; grades A, B, C; source status;
- the picture catalogue with `rights_class` and `shows`; link cards for research-only pictures;
- generated pages with a hand-written `## Notes`, `%% private %%`, and public and local JSON;
- `tools/serve_local.py` with `/_local/`, `?public=1`, `?b=`; `tools/check_pages.py`; `site/.vercelignore`;
- the dev map behind a small button, with the 3D view as the way in;
- the `summary.json` shape for detailed models;
- the homepage's look and fonts.

**Differed:**

| | Küstrin | Here |
|---|---|---|
| The base | several plans; a 1913 plan with an address book, house by house | one plan drawing every building |
| The ground | a terrain scan, with today's rubble taken out | a flat base from a coarse DEM, with land cut to the traced water |
| Georeferencing | `georef.py` of 92 lines | spline over 111 points, by area, `scripts/georef.py` of 708 lines |
| Reading the plan | lot numbers by OCR and by eye | a tracer, then area readers viewing crops |
| Object count | 447 rows | 1824 rows, so everything is a generator |
| Rows | landmarks and houses | compounds with halls under them (`parent_id`) |
| Non-image evidence | in facts and notes | its own catalogue and `facts.csv`, new here |
| Bare objects | a page with what it has | parent fallback, new here |
| How it grew | 184 commits, feature by feature | five rounds from written briefs |
| Dev map library | a CDN | vendored |
| Plan image | local | local (Q6); traced geometry public |
| Grade A means | seen on a source of 1900–1914 | a source made while the gardens stood; S01 held at B |

### 18. A detailed model, tested against the plates and the photographs

Round 13 (`models/XY01-xieqiqu/README.md`, `tools/plate_overlay.py`). The order that worked:
1. **Fix a key-point vocabulary first,** then let readers read every picture with it, in the pixels of a named copy, with a sureness grade, each point checked with a cross on a fresh crop. Readers differ in what a name means (one took an octagon's outline, another the face's ends): keep their notes, rename a reading to what was read, and skip a silhouette (a colonnade passing behind a pavilion) with the reason rather than force it.
2. **Photographs measure, plates test.** A ruin photograph is a true perspective; an engraving of the 1780s is not. Fit each photograph's camera jointly with the few figures that matter (storeys, widths, depth), the plan's frontage as the scale; carry the figures into the model; then fit the plates to that model and measure what is left. Run the measurement twice: the first pass is pulled by its priors.
3. **Measure the engraver, don't tune it away.** A plate camera with one more unknown, its heights drawn k times its widths, separates the idealisation (plate 1: 1.57, plate 2: 1.11) from the model's error. Record what the plates enlarge (the top storey, here) as a question, and say which source is likely right and why.
4. **Two fits per picture:** on the points the plan places (`anchored`: an honest test of the heights) and on all points (the best one camera can do: the shape disagreement). A picture's distance prior can be far off (P0186's catalogue guess by 70 m); a fit that runs to absurd places (a pool 35 m into the lake) says the picture does not constrain that figure: drop it.
5. **Render the overlay, look at it.** The residual table found the storeys; the blend found the stair (its flights run north-south, which a second look at the plate confirmed). Render from the fitted camera in the real view, one page load for all pictures, and compose blend, edges and side-by-side.
6. **The model joins the rest:** its entries become the doors the ways snap to, its footprints what the ways route round and the planting keeps clear of, its boxes stay the click target, unseen. A traced way that starts inside the model (the plan sits about 12 m off the ruin here) loses its points inside and snaps from the first point beyond.
7. **Carry round, mark it.** Faces no picture shows are copied from the documented ones into their own `~fill` materials: one switch hides them, one tints them.

Round 14 (`models/XY08-haiyan-tang/README.md`) built a whole complex of five parts the same way, from four plates and few photographs, and added:
8. **The readers' notes on form are worth more than their points.** The points measure; the notes find the form. Three findings came from the notes, and each moved plate 12's or plate 10's fit by a third or more: the bent stairs (an upper flight outward, a landing, a lower flight forward along the pool), the four flights a side of the east stair, and the east tier being a long hall. Ask readers to describe how stairs run and what stands where, not only to place crosses.
9. **Fit by part.** One camera cannot hold a complex whose parts a plate draws at different scales (plates 11 and 13 draw the water building 1.4 times too long against the west block). A camera per part (`--parts`) tests each part's own heights and widths, and the disagreement between parts becomes a question (Q225) instead of a residual spread over everything.
10. **Check a key point's definition before you move the model.** The middle ridge's point was put where the range ends; the plate shows where the ridge runs into the pavilion's hip, 3.8 m further out. A large residual on one point and none on its neighbours is usually a definition, not a form.
11. **Let the footings follow the ground.** A plinth drawn down to the lowest ground under a whole part sank 1.2-2.8 m where the court rose. Draw the skirt along each edge at the ground there (`skirt` in the generator): every contact is then 0.1-0.2 m in.
12. **The model's court can cover what the ground does not know.** Round 10 holds the water clock's pool as a sunken water body 1.5 m below the court; the model's pool, its paved court (plate 10) and steps down at the court's front cover it, and the planting keeps off the court as a footprint.
13. **When the photographs are too few, the plate's figures stand, and the photograph's disagreement is written down.** Ohlmer's single west photograph puts the attic 1.65 ± 0.42 m high against the plate's 2.6 m (`models/XY08-haiyan-tang/measure.py`): recorded (Q228), not carried.

Round 15 (`models/XY10-da-shuifa/README.md`, `models/XY11-guan-shuifa/README.md`) built a fountain ensemble and a screen with its court, from two plates and fourteen photographs of 1873-2025, and added:
14. **Ask what a drawn band is before you model it.** Plate 15's "ribbed quarter-arch bands" beside the piers were modelled first as buttresses. The 1873 photograph shows a balustrade on top of the same curl: the bands are the parapets of the stairs to the terrace, and the ribs are their balusters. The plate draws them edge-on. The plan's hatched blocks (CCX-023, 024) and plate 14's two stairs said the same. One look at the oldest photograph beside the plate settled the form; the fit alone would not have.
15. **A model can reach a neighbour's guess, and then the guess must move.** The stairs climb to about 4.6 m (the plate's curl at the piers' flare, P0776, P0762), but 远瀛观's terrace was a 2.0 m guess. Stairs that end in the air break the rule, so the neighbour's box was raised (`xiyanglou/boxes.csv`, Q232) with the evidence written beside it. Change the neighbour's numbers, never its place.
16. **A flat set of points needs a lens prior.** Eight points on one façade let a fit shrink the focal length to 79 px and lift the camera 13 m (P0762). An assumed lens (`hfov_deg`, a weak prior: 50° for the old photographs, 60-65° for today's phones) keeps the camera physical; its distance then rests on the lens, so such a fit tests proportions, not size. Say so in the table.
17. **Read the state, not the ruin.** Today's niche opening runs down to the plinth; in the 1780s a sill stood at the terrace's level with the cascade below. A reading of today's feet is right for today and wrong for 1860: keep it with `use` skip and the reason, and model the 1780s from the plate and the oldest photograph.
18. **Four photographs agreeing beat one plate.** The niche's head stood 1 m inside its posts' caps on P0641, P0340, P0169 and P0776; the plate drew it full width. The four photographs moved it (P0641 from 0.47 to 0.19 m). The same rule kept the gates of 观水法 at P0193's proportion against plate 16's taller ones (Q233).
19. **Courts and terraces a model draws are met at the model's doors.** The ways treated the court box as walk-through and ended in its middle, 26 m from the basin. `scripts/paths1860.py` now gives a model's entries to every box of its rows, walk-through or not.

Round 16 (`models/XY09-yuanying-guan/README.md`, `models/XY06-fangwai-guan/README.md`) built a hall on its terrace and a small pavilion, from two plates and fourteen photographs of 1873-2013, and added:
20. **Test the module before the heights.** 远瀛观's dossier held heights read on plate 14 at a module that made the columns 4.2 m apart, so the whole front came to 18 m against Durand's 28 m. The plate's own ratios against the survey's frontage, and a door on a ruin photograph, both gave 6.0 m. One wrong module scales every height in the row: check it against the widest surveyed figure first. A `stretch` fit near k = 1 afterwards says the module and the heights agree.
21. **A free camera on one façade cannot test scale.** Every ruin photograph of the clock gate fitted the 4.2 m model as well as the 6.0 m one: a camera of its own absorbs the size of a plane front. The plate, which holds the whole building at once, is the scale test; the photographs then set the proportions of what they show (the order taller than the plate draws it, the pier between column and opening wider).
22. **Check a photograph's side by the order of its windows.** P0773 was catalogued as the south-west corner; its front recedes to the left of the near corner, which only a south-east view (or a mirrored print) gives. Relabelled, its oval came from 1.7 to 0.65 m. Before fitting an oblique view, list which face is left of the near corner and check it against the bearing.
23. **A raised floor a model draws carries the ways.** The ways lie on the ground of Round 10; a terrace 4.3 m up hid them inside it, and a way to the door ended 4.24 m below it. A model now declares its terrace as a deck (`Site.deck`, `models/XY09-yuanying-guan/joints.json` `decks`): the view lays the ways on it and `tools/check_models.py` measures there.
24. **A neighbour's model gives the joint.** 远瀛观's terrace front and the heads of 大水法's stairs are read from 大水法's own files, not from the boxes: the two models meet at 0.00 m in plan and height, and the hall's origin moved 0.72 m onto the shared axis.
25. **Hide the neighbour for the overlay, not in the scene.** 大水法's niche stands between every camera and 远瀛观; `plate_overlay.mjs --only` (3d.html `&plateonly=`) hides the other detailed models in the renders. Kit halls are not hidden: plate 8's near-elevation from 50 m runs through the five pavilions of 五竹亭, which the engraver left out; compare against the model's own frontal view instead.

### 19. A Chinese compound from the kit and its evidence (Round 17, the recipe; Rounds 18-19)

Round 17 (`models/CC02-hanjing-tang/README.md`) built the first Chinese compound, 含经堂, where no picture of any hall standing survives: the plan, a Yangshi Lei plan in print, texts that give bays and roofs, and the excavated platforms as displayed today. The recipe:
1. **One model for the whole walled compound,** not hall by hall. The ruin showed the compound on a terrace 2.1 m above its forecourt; drawing only the axis would have left the side courts' kit halls 2 m below the courts' floor. Every box inside the wall is an alias; the halls of the side courts are drawn from their own kit entries (`fill`), so the compound is one level and one style.
2. **The kit in Python** (`scripts/hall_parts.py`): the same platform, flights, columns, bands, bracket sets, doors, windows and roofs as `kit3d.js`, so the modelled halls sit among the kit's without a seam. A hall starts from its kit entry (`kit_1860.json`) and is adapted: bays, porches, double eaves, tiles, platform from the dossier and the ruin. Mark a hall `doc` only where the dossier has a figure of its own (`fig` in the kit entry); the rest is `fill`.
3. **Read the plan again for the model, in plan pixels** (`models/CC02-hanjing-tang/plan_readings.csv`): walls, terrace edges, galleries, screens, the shapes of the ranges. The Round 1 boxes were drawn for the inventory; their labels can sit one court off (Q14) and their outlines merge a ⊐ range into one block (梵香楼 43 x 21 m). Put every reading through the georeferencing fit, so the model and the boxes agree where they should.
4. **The ruin's platforms are the test.** A displayed dig is a set of platforms, flights and terrace walls: name their corners (`<hall>_pl_foot_SW`, `_pl_top_`, `_fl_front_L_foot`) in the generator, give readers a labelled plan of the model, and fit each photograph's camera (`tools/plate_overlay.py fit --sheets research/scenes/<ID>-<slug>`). Readers' notes found the three things the plan got wrong: the gate's projection 13 m wide, not 24 (Q244), a front terrace before 含经堂 (Q245), the flights of 淳化轩's terrace 2.5 m in from its ends.
5. **Measure a height by a sweep.** Run the model at five terrace heights and fit the three photographs each time: the summed rms at the object fell to its least at 2.1 m (1.73 m against 1.82 at 2.4, 2.23 at 3.0). A shallow curve: say so, and keep it C.
6. **A terrace is a deck, a court is clear.** The terrace's floor is a deck (the ways lie on it); the courts and the forecourt's lawns go in `clear` (`models/CC02-hanjing-tang/joints.json`: the planting keeps off them, the ways do not route round them). Only walls, platforms, galleries and rocks are footprints. Joints on the deck are measured against the deck in the model's own report (`models/CC02-hanjing-tang/report.json` `deck_joints`); only what stands on the ground of Round 10 is a joint for `tools/check_models.py`.
7. **Where the texts name the planting of a court, plant it in the model** (the plums of 淳化轩's court, the pine, bamboo and plum of 三友轩): Round 12's planting stands on the ground, not on a deck.
8. **Flight names follow the viewer:** L and R as seen standing before the flight looking at the platform. The first version had them mirrored for every side but one; the readers followed the brief, and the fit showed it.

Round 18 (`models/YM03-jiuzhou-qingyan/README.md`) used the recipe on an axis with no ruin to read and no dig published, 九洲清晏, and learned:
9. **Date every part and take the latest source for each.** The plan carried the names of a later, partly unbuilt design (Q36); the album leaf showed the state before a fire and a rebuilding. The model's state (1837-1860) was assembled part by part: the front hall from a slip of 1855 (A), the rear porch from a record of 1855 (A), the courts from the plan (B, positions) checked against a survey of 1873-74 (B, written figures), the colours and the galleries from the leaf of 1744 (A for 1744, B for 1860). Write each part's date in its row.
10. **Where a written figure and the plan disagree on a width, test it against the neighbours.** The survey's court width (25.98 m) put the walls through the halls the plan draws beside the courts; the plan's 22.6 m is drawn with them. A figure that would make the model cut its neighbours stays a question (Q250), however precise it looks.
11. **Keep a model's extent to what its panel can frame.** The bridges 60-110 m out shrank the axis to a speck in the panel's small view: each named bridge became its own small model written by the same generator (one Site, its frame moved to the bridge), and `models.json` `bridges` tells the view to leave out Round 10's plain deck.
12. **Define key points on the geometry the kit draws, not on a formula of your own.** The 歇山 ridge ends were first computed as for a 庑殿 and came out 40% short; the leaf's ridges looked twice too long until the definition followed `hall_parts.roof` (the hip steps in 0.4 of the slope).
13. **Check a painting's points on the overlay of the fitted camera.** Two points read on the leaf at 3x had run a hall's end onto its neighbour; the fit looked better with them (2.55 m) than with the corrected ones (3.79 m). The overlay of crosses and circles found them; a good number is not a check.

Round 19 (`models/YM01-zhengda-guangming/README.md`) used it on the formal entrance, 正大光明 with 大宫门, a sequence of courts 160 m deep, and learned:
14. **Look at what the layers hold inside the model before drawing it.** The court before the hall held a generated hill of 7 m (Round 10's free land), which lifted the terrace 5.8 m on the first run; the garden wall of Round 1 ran along the canal through the bridge; a gate box of `gates.json` stood on the bridge. Fix each at its source: `hills1860.py` keeps the free land's hills off every court a model paves (`clear`, `decks`), the wall ring W01 moved to the 大宫门 line where S01 draws it (`plan/walls.json`), the gate box in the model's `hides`, which `kit1860.py` now reads.
15. **Water the plan draws is water in the ground, not in the model.** The canal is two ink lines 3 m apart, too narrow for the tracer; traced by hand in plan pixels (`research/plan/water_manual.json`) it becomes a body of Round 10 with its level and bed, the ways see it and the bridge carries them; the model draws only its marble lining, coping and railings.
16. **Put the frame on the axis the plan draws.** The main box's bearing ran 2° off the line through the halls; over 100 m it put the outer gate 3 m off the axis. The frame's z now runs from the middle of the inner group to the middle of the outer one, and the reads' spread fell from 4.3 to 2.8 m.
17. **When the plan draws a hall smaller than every written figure, keep the figures and centre them on the plan's drawing.** S01's hall and terrace are 0.8 times the slip's and Malone's sizes, while its gates are near their dug and written sizes; the model keeps the stated sizes where S01 places the group and states how far each end moved (Q256).
18. **A model owns the walls it draws.** Where a wall of Round 1 runs through a model, the model draws the wall itself and names the outline in `walls_cut`; the view leaves out the plan's segments there, and the ring's ends meet the model's walls.
19. **A painting shows a colonnade's feet, not a platform's corners.** Points `<hall>_col_<corner>` (the front corner column's foot) were added for the leaf; the platform's corners stand 1.6 m further out on a hall with a deep edge.

### 20. The surroundings: a labelled setting round the site (Round 20)

Round 20 (`research/surroundings/README.md`) put what stood round the gardens into the layers and the view: the neighbouring gardens, the town, the camps, villages, temples, the water and the roads. The recipe:
1. **Four readers by topic, one sheet by the editor.** Gardens, water and roads, people (camps, villages, temples, the events of the time), old maps. Each wrote rows with a representative point, its basis and two grades. A merge table (`docs/rounds/common/palace_r20_merge.py`) chose one row per object, kept the others as cross-checks in its note, and gave the ids in the table's order. The table's order is also the massing's precedence: what is sourced and small comes first, villages and camps last, so the generated houses keep clear of everything placed before them.
2. **Grade the object and its place separately.** A Qing text naming a village makes the village A; its place, taken from the village name that survives today, is C. The view tints by the weaker of the two. Without the split, three quarters of the ring would have read A.
3. **A map known only from later maps is C for the target date,** whatever its fit. The 1944 sheet's villages are B for 1944 and C for 1860.
4. **Size the massing from the figure the source gives, and say the layout is generated.** A camp of 1,550 rooms is drawn as 14 rows of eleven ten-bay houses in a walled rectangle; the count is the text's, the rows and the wall are C. Where nothing gives a count, the houses are a guess and marked.
5. **An assumed extent is drawn as an irregular outline, not a circle.** A circle looked more exact than it was. The outline is seeded from the id, so it stays the same from run to run.
6. **Lines join by name.** A road's or canal's end is snapped to a gate, the end of a way, or an earlier line (`joins`), and the gap before and after is measured. Two A-grade roads ended 0.3 and 38 m from a garden wall until they were joined to the road they meet.
7. **The ground beyond: the plain extended, the relief only where it is real.** Today's surface model holds the city. The ring takes the inner ground's plane and uses the DEM only on the massifs that carry a named peak, opened to strip roofs and crowns. A backdrop of 200 m cells to the hills sits under fog.
8. **The join is measured where the two grounds share vertices.** The 20 m ring cannot follow a 1.4 m bank inside 5 m. The view fans the edge cells through the inner mesh's edge vertices, so the seam is closed; the check fails on the shared nodes (0 m) and reports the lattice's departure between them (0.54 m at one bank).
9. **Water outside gets bodies of its own.** A lake outside the walls touching the inner domain would otherwise merge with the gardens' water and move its levels.
10. **Keep the triangles inside a budget by merging what repeats.** The barracks were 2,338 houses of five bays; as 1,165 double houses of ten bays they kept the count of rooms and brought the round's mesh under 250k triangles.
11. **Run the chain until it stops changing.** The ground reads the boxes of the last run: after a change to the ground, step 6 took three passes before no file changed.

### 21. Light: a chosen day and an assumed night (Round 23)

Round 23 ported Küstrin's Beautiful light (`site/reconstruction/beauty3d.js`, `site/reconstruction/night3d.js`): a sun over the site's latitude by the local clock, two shadow cascades, a sky, haze, water that takes the sky, tone mapping and a baked occlusion, all as patches on the existing materials, so Clean stays the historical view and costs nothing. What carries to the next site:
1. **The light is a choice, not evidence, and the view says so.** A clear day per season (the Season selector moves the sun: 1 July by default, 15 January in winter), the hour, the clouds and the haze are picked for the look. The panel's legend says it in one line.
2. **Lights at night are assumed, grade C.** No source places a lantern or says which room was lit. They are generated by fixed, written rules (the header of `night3d.js`: a lantern every third bay of a covered gallery, a pair under the front eave of the gates and main halls, one before a third of the side halls, one on a post at each landing, a share of the models' windows, a scatter on the villages beyond the walls), hidden with the Assumed switch, and named as a festival look, not a record.
3. **Port the generic, rewrite the site's.** The shader patches, the cascades, the sky, the occlusion bake and the quality probe came over unchanged; the sun's table of latitude and noon, the occlusion box, the casters' height, how water is found (Küstrin by the terrain's paint, here by its own material and the land's vertex colour), the halls' windows (a pane colour, lit by cells of the site) and the haze are the site's own.
4. **A wide site needs haze, not fog.** At 4 km of gardens under a 10-40 km horizon, three's fog either hides the gardens or leaves the hills flat. A haze that thins with height and turns from blue-grey to the sky's horizon colour makes the ridges stand in layers and meet the sky without a seam; the horizon is the far plane's straight line under full haze.
5. **Merged meshes without normals get a slope-scaled depth offset** in their shadow pass (a custom depth material) in place of the normal bias they can't take; flat things laid on the ground (paths, courts, patches) take shadow but cast none.
6. **Every tool that compares pictures asks for Clean** (`light=clean`): the plate overlay, the AI-picture cameras, the checks' screenshots.

## Pitfalls and fixes

**The kit (Round 11):**
- **A coloured band at the eave poked through every roof as a red stripe.** The bracket band stood 0.26 m outside the column line at the eave's height, where the roof is already lower. Fix: every band is capped at the roof's profile above it.
- **Ground probes counted as geometry.** The steps' ground samples went through the same transform that measures how far a hall reaches beyond its box, so every hall seemed 0.3 m too wide. Fix: a probe flag.
- **Shore steps hung in the air.** A flight's foot was read on the land-only ground, and its blocks stopped there over a sloping bank. Fix: sample the flight's four corners; skip it if any is water; reach down to the lowest.
- **4.8 M triangles in memory at load.** Every tile's near level was built at once. Fix: lazy near tiles, byte colours, no normals: 0.67 M at the overview.

**The pilot model (Round 13):**
- **An octagon's left and right were swapped** (the viewer's left taken as the face's own): plate 1's error halved when fixed. Test a view-dependent point on a picture before trusting a residual.
- **The plate camera ran 190 m back with a 5,900 px lens.** Plate 1 is a near-parallel elevation, not a view from 69 m: the octagons' spacing against the block allows no strong perspective. Report it as such; the `stretch` fit then explains the heights.
- **The dossier's heights (15.1 m eave, 18.3 m ridge) were the plates' module.** The photographs gave 11.6 and 14.0 m. Heights read on an engraving by a module inherit its idealisation.
- **The panel's model view showed an empty disc.** The copy handed to `model3d.js` kept its transform on the group; that file reads raw positions. Bake the transform into the copied geometry.
- **A background "foreground" agent.** The Agent tool started the readers in the background by default; they finished before the turn ended. Keep waiting for every notification before the final message.

**The second model (Round 14):**
- **The agents went to the background again** (the Agent tool's default; `run_in_background: false` must be set on each call). All three finished within 10 minutes and before the turn ended.
- **Arches hung upside down.** `arc_pts` took its start angle from `atan2(y - cy, -half)`; for a semicircle `y - cy` is ±0.0 and the angle came out -π for some arches. 20 of the pilot's 204 arches had been inverted unseen since Round 13. A frontal close-up of one wall found it; the fix is `t0 = π - t1`. Shoot at least one frontal close-up of every kind of opening.
- **A body box covered its own façade.** The link's and the wings' solid boxes stood in the planes of their faces, so the arches and windows cut in the faces showed a flat wall. Draw the faces as the walls and keep any inside block behind them.
- **Degenerate cameras.** Two photographs with one and two points gave a camera with a focal length of 0 or 10⁸ px and errors of 10⁶ m in the table. The tool now leaves out a picture with fewer than four points.
- **Panels without Chinese.** Headless Chromium had no CJK font: point `FONTCONFIG_FILE` at a fonts.conf that adds the Noto files (`/opt/data/cache/fonts`).

**Running the agents:**
- **A research round launched its subagents in the background, ended its turn "waiting", and print mode killed them after 10 minutes.** It exited 0 with almost nothing delivered ($9, 17 min). Fix: foreground subagents only, several Agent calls in one message; `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` in the chain; and chains gated on deliverables, not on the exit code alone.
- **Partial work lost in a crash.** Skeletons of every deliverable first; workers append notes as they go.
- **A worker overruns.** The pictures worker ran about 100 minutes against a 30–45 minute scope. Give a deadline by the clock (`date -u`), and turn what's missing into a wish row.
- **Rules broken under pressure.** One worker ran `git checkout` twice despite "no git writes"; others wrote shared files; one fetched tiles too fast. Say so in the final message; those reports are in `docs/rounds/README.md`.
- **Late shared facts.** The plan's scale was corrected after wave 1, so the correction was added to the common brief before wave 2. Keep that brief a living file.
- **Workers in one scripts folder.** Two overwrote each other's contact-sheet script. Fix: a prefix per worker.
- **Workers' "can't".** The brief said skip without `pdfimages`, so ten free rows came back with no image. A small library in scratch fixed it in minutes. Check what a worker skipped before accepting it.
- **Valuable tools left in scratch.** Round 3's merge scripts sat outside the repo. Catalogues are the truth, so a rebuild doesn't need them, but they can't be rerun from a clone. Copy what's reusable into `tools/`, as was done with the font subsetter (`tools/font_subset.py`).

**Building the ground (Round 10):**
- **A new per-vertex attribute added after the last run** made the browser read the position bytes as hill shades: a blotched plain. Rerun the generator after changing what it writes, before the first screenshot.
- **A bed that meets an earth bank at the land's height** stands above the water in narrow canals, where its mesh has only shore points: light streaks. Start the bed just under the water.
- **The water's polygon offset** hid boat lines 0.25 m above it. Draw them after the water and higher.
- **Deck ends inside the water polygon** (the line stops short of the bank) took a guessed level and floated 1.4 m. They take the nearest land's height there now.
- **A pad on a hilltop is wider than the hill's top:** with the blend it flattens about 20 m round 线法山's pavilion. Acceptable at this scale; say so.

**Reading evidence:**
- **A check that isn't blind.** The georeference worker edited its check set after seeing errors: first pass median 52 m, kept set 31 m. Both stay in the JSON, and Q7 says it plainly. Fix the check set first. Round 8 did: blind readers, a hash, a checker; it gave 19.8 m for the same fit.
- **A rule that leaves the readers nothing.** 60 m from any fit point left 19 check points over 335 ha; the rule went to 30 m before any error was computed, and both fits hold every old point, so the comparison stays even. Decide such a change before scoring, and record it.
- **A generator that reads its own output.** The first lake derivation read the water layer, which follows the fit in use, so a rerun after the refit moved its points 0.3 m. Read the tracing in plan pixels and map through a fixed fit.
- **OSM keeps big lakes as relations.** 福海 and four other lakes are relations of ways, which a polygon filter skips: close them before comparing shores.
- **The stated scale was wrong** (1:1300 against 1:1070), and buildings are drawn at another scale again. Measure; never size a building from a global px/m.
- **Things that look like what they aren't.** Labelled 稻田 rice fields look like ponds. Read labels before classing regions.
- **Dating the base plan by feel.** See Q36. Test plan labels against dated decrees early.
- **Wrong people, wrong place.** Beato's photographs of 1860 show Qingyi Yuan, not this garden. Prints credited to Piry, Child or Ohlmer may be by C. F. Moore. Skušek's album names are unreliable (Q49).
- **Same thing twice.** Parallel workers gave one item two source ids, and two names can be one place (QC40 = QC25). Keep ids; note the identity.
- **Snippets posing as sources.** Mark them `snippet`, hold their facts as `lead`, and let the panel say so.
- **A caption's place name.** Before 1900, "Yuen Ming Yuen" and "Summer Palace" name other gardens too: Favier, Thomson and Beato at the holders themselves. Check form, always.
- **Viral claims.** "Photographs of the garden before the fire" come with no holder and no picture named. Test them, write down the test, and leave them out.
- **A twin's chain of repeats.** 海晏堂 follows the Trianon comes from one book of 1971 and fills the web. Find a work that weighs the claim.
- **Confidence inflation.** "On a source" here means position and footprint; heights and roofs still come from the typology. Say that where the number is quoted.

- **A worker's reads that never came back.** One perspective worker's image reads returned "media removed: request limit", and its first script held pixel values anyway. It caught this, withdrew the table and re-read all 20 plates on displayed grids. Ask workers to check that a read came back before using it.
- **A brief's own errors.** The brief said Malone measured foundations, the Bergen columns went to Peking University in 2014, and a paper shows an Archimedes screw. None held. Tell workers that the brief can be wrong, and read their corrections first.
- **The whole-site polygon taken as a building.** The box of 远瀛观 took an OSM outline that also holds the niche of 大水法; its row stood 27 m off. Test each outline against its neighbours before it becomes a size.
- **A stone's place is not evidence.** Ruins are re-laid: here from 1976 on, and not always in the original place (S821). State who moved what, and when.

**Building it:**
- **Stated sizes not reaching boxes,** because a row's name differed from the key: 文源阁, 大宫门, 雷峰夕照. Print what didn't bind.
- **Workers' shorthand in public text.** Clean notes by rule and view real panels. File names as titles, and the same work tied twice at two grades, showed up only in screenshots.
- **Boxes fighting the plan.** At full hall scale 315 pairs overlap. Reduce towards the drawn size first, then move at most 2 m, and report what is left (Q34).
- **Views that look wrong:** the outer plain hid the water, land colours skipped colour conversion, labels too small, wall tops through low roofs. Only viewing screenshots catches these.
- **Two facts on one row.** The first stated size changed `size_source`, so the second was taken for a conflict and noted: three rows of earlier rounds (YM34-03, YM34-04, YM36-02) had lost their depth that way. Fixed in `apply_facts.py`; check every rule that reads a field it also writes.
- **A merge of two readings.** Two workers read the same labels at 九洲清晏, one merging a row, one keeping it; the merge would have taken a box away from a hall that had one. Where workers disagree the row stays, the doubt is written down, and `boxes1860.py` stops on a merge into a row with no box.
- **Tall screenshots repeat themselves.** Past about 8000 px the headless capture here tiled the top of the page again, and lazy images stayed blank. Scroll the page first, capture in segments from the same load, stitch (`docs/rounds/common/palace_r7_shots.js`). Headless Chromium has no Chinese font: point fontconfig at the Noto files.
- **Generators that must be idempotent.** `scripts/building_pages.py` writes only if changed, and `tools/check_pages.py` runs it twice and compares.
- **Clean URLs break relative links.** With `trailingSlash: false`, `/reconstruction` has no slash: links need to work on both.
- **Size.** At Round 3 `site/` was 106 MB, `research/photos/images/` 161 MB, `.git` 267 MB; after Round 6 `site/` is about 150 MB and `research/photos/images/` about 240 MB. Round 3 cut new images to 1600 px and about 300 KB. Check the host's limits before setting one up.
- **The planting's first runs (Round 12).** A garden-wide row placed with `place` scene filled the whole garden; `outside_wall` for GARDEN-ALL needs every wall. A species key taken from a name lost the row's form (clipped pines became pines; 松;菊 a chrysanthemum drawn as a pine). Far crowns of an octahedron read as a field of diamonds. The fill sat out wherever a sourced zone had been drawn, however sparse: keep it clear of the sourced plants, not of their zones.
- **Docs that drift.** `tools/check_docs.py` compares field names and paths with the files. Round 4 found `research/README.md` claiming `scripts/georef.py` alone writes the overlay, and `CLAUDE.md` listing screenshot scripts that aren't there.

## Running it as rounds

Each round is one `claude -p` run from a written brief, with its own log and marker. A chain waits for the marker, gates on deliverables, commits, starts the next:

```bash
export CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0
while [ ! -f "$R/prev.done" ]; do sleep 60; done
[ "$(($(wc -l < research/buildings.csv) - 1))" -ge 30 ] || block "too few rows"
[ -s research/sources.md ] || block "no sources"
git add -A && git commit -q -m "..."
claude -p "$(cat "$R/next_brief.md")" --model opus --effort xhigh --permission-mode acceptEdits \
  --allowedTools 'Read,Write,Edit,Bash,WebFetch,WebSearch,Agent' --add-dir "$S" --add-dir "$SISTER" \
  --output-format stream-json --verbose > "$S/next.jsonl" 2> "$S/next.err"
echo "exit $? at $(date -u +%H:%MZ)" > "$R/next.done"
```

**What goes in a brief** (examples in `docs/rounds/`): the owner's words; where it stands, measured; the deliverables with their gates; data rules; how to work; verification; what the final message must lead with. Workers don't ask questions: they decide, write the reason down, and report. Workers don't commit.

## Checklist for the next project

**Before any work:**
- [ ] Create the repo; add it to `000_Dev/CLAUDE.md`.
- [ ] Pick the sister project; name it read-only in the rulebook.
- [ ] Write `CLAUDE.md`: target state, purpose, grades, evidence order, copyright, coordinates, layout, tone, ports, who commits.
- [ ] Copy `.gitignore`, `site/.vercelignore`, `site/vercel.json`, `pyproject.toml`; run `uv sync`.
- [ ] Reserve a preview port and a `/opt/data/scripts/rounds_<name>/` folder.
- [ ] Check for local datum trouble and which map services are safe.
- [ ] Ask whether the project stays non-commercial; it decides what is free.

**Round by round:**
- [ ] Homepage, one checked image, credits.
- [ ] Find and date the base plan. Test its labels against dated texts now.
- [ ] Research fan-out, foreground, with skeletons, deadlines, S-id blocks, a common brief.
- [ ] Mosaic, trace, control points, a check set fixed in advance by blind readers and frozen by hash (`tools/check_georef.py`), accuracy per area and per kind, as a layer.
- [ ] Text inventory, plan readers, merge script, random spot check.
- [ ] Typology with a source per number.
- [ ] Dev map, then boxes, then pages. View the screenshots.
- [ ] Evidence wave by kind, panel, measure gaps, wave on the gaps, verify quotes by script.
- [ ] Twins by stated relation, typology comparables, reconstructions by others with their period and method; before and after counted.
- [ ] `tools/check_pages.py`, `tools/check_evidence.py`, `tools/check_docs.py` pass.
- [ ] Rebuild in a scratch copy: every committed file comes out the same.
- [ ] Wishlist and rights questions written for the owner.
- [ ] Docs round: rulebook, research README, a round log, and copies of the briefs.
- [ ] Measure the site's size against the host's limits before the first deploy.
- [ ] Before the setting goes in: grade the object and its place separately, and give every generated house, row and outline `assumed` (section 20).

**The fifth and sixth models (Round 16):**
- **The readers went to the background again** (the Agent tool's default). All three finished within 10 minutes and before the turn ended.
- **A footing skirt covered its own door.** `Site.footing` draws a face on every side of its outline; on 方外观's podium and porch those faces stood in the planes of the walls with the door and the ovals cut in them. Where a face has openings, draw the wall from below the ground and keep only the joints.
- **`Parts.oval` fills its centre.** Used as a frame round an opening it covered the glass; a ring (`frame_ring` in the generator) leaves the opening open.
- **A planar front lets the camera slide.** P0183's sixteen points on the clock gate's front moved its camera 22.5 m back with double the assumed lens; the print is cropped, so the lens prior does not hold. The pixel residuals stand, the camera's place does not.
