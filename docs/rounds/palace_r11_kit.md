# palace_r11_kit: the hall kit and the stone kit: every building drawn from its data, no empty spaces

Round name: `palace_r11_kit`. Ports 8870-8879. Scratch notes: `/opt/data/cache/scratch/palace_r11_kit_*`.

## Why
Tomasz: "let's parametrically render those that we have no picture, no data, so we don't have empty spaces." About 1,500 halls exist in the data; 937 have only a footprint on the plan. Today each is a plain box with a simple roof (`site/reconstruction/halls3d.js`, 304 lines, merged into one mesh). Replace that by a **kit**: a generator that draws a Qing hall from numbers (bays, purlins, platform, roof class, tile colour), so every hall has a believable form, plus a **stone kit** for the Xiyang Lou. Küstrin's equivalent is `site/reconstruction/typology3d.js` (drawn in the browser, no model files, seeded variation) and `models/B05-zeughaus/arsenal.py` for the one-off kits.

## Deliverables
1. **The Chinese hall kit** in the browser (`site/reconstruction/kit3d.js` or similar, loaded before `3d.js`; `halls3d.js` keeps picking and colour logic). Inputs per hall: the data of `halls_1860.geojson` and `research/typology/params.json` (frontage, depth, bays, storeys, platform, eave and ridge heights, roof class, tile colour, orientation). Draw:
   - **Platform (台基)** with steps (踏跺) on the front and the stated side, stone colour, and a marble balustrade on the great halls.
   - **Body:** column row (檐柱) in red-brown lacquer, infill walls and **windows or door leaves** per bay (the bay rhythm: central bay wide, side bays narrower), recessed with frames and lattice, dark glass or paper tone; a lighter wall colour for the assumed ones.
   - **Roofs by class:** 庑殿 (hip), 歇山 (hip-and-gable), 硬山 (flush gable), 悬山 (overhanging gable), 卷棚 (rolled ridge: the typical Yuanmingyuan form, check this in the typology), 攒尖 (pyramid, for pavilions), with eave curves (起翘) and a pitch from the 举架 rule; ridge ornament simplified (正脊, 垂脊); tiles as a flat colour with ridge lines, grey as the rule with the named exceptions (yellow, green, blue, black: typology section 5).
   - **Simplified bracket sets (斗拱) as a coloured eave band;** no per-bracket geometry.
   - **Corridors (游廊) and screens/gates (垂花门, 影壁)** when Round 9's paths have them: use the path kinds.
   - **Courtyard fill:** paved court ground between the halls of a compound, with the path strips on top; no bare ground inside walls.
   - **Variation:** seeded by the hall id (a few lacquer and wall shades, small roof differences), so groups don't look cloned; never so much that a documented hall changes look.
   - **Performance:** merged geometry or instancing; the full scene of about 1,500 halls loads and renders at a usable rate in software WebGL (state the frame time and triangle count before and after), with a lower level of detail beyond a distance.
2. **The stone kit** for the Xiyang Lou (`site/reconstruction/stonekit3d.js`): Baroque-style façades as simple geometry: a rusticated base, an order of pilasters or columns (Corinthian, with simple capitals), entablature, pediments, balustrades, arched openings, curved double stairs (as at 远瀛观 and 海晏堂), fountain basins and the stepped cascade of 大水法, with glazed-tile colour accents on roofs (the plates and the dossiers say which). Drive it from `research/xiyanglou/*/dimensions.json`. It is a kit, not the pilot model: 谐奇趣 gets its detailed pass in the next round, so here every Xiyang Lou building just gets a believable kit form.
3. **Which hall uses what:**
   - A hall with a detailed model (`models/<ID>/summary.json`, none yet) shows only its model.
   - A hall with a dossier and `dimensions.json` uses those figures (A/B/C per figure).
   - Everything else uses the class defaults, flagged `assumed: true`.
   - Add a view switch: `kit=0` returns to the plain boxes; `assumed=0` shows only sourced halls; `conf=1` tints by confidence as before; the click panel keeps working on every kit hall, and the box stays the click target.
4. **Typology defaults.** Questions Q182-Q185 propose four changes (the large-hall class: column height 5.12 → 4.2 m, platform 1.22 → 0.7 m, and others). Re-read each against its evidence. Apply those the evidence supports (record each change with its source in `params.json` and `halls.md`), leave the rest open, and report which. Rerun `scripts/boxes1860.py`.
5. **Checks (`tools/check_kit.py`):** every hall in `halls_1860.geojson` is drawn, with its roof class from the data; no kit hall exceeds its footprint by more than a roof overhang; platform tops meet the ground and the path strips (gap figures); counts by roof class, tile colour and `assumed`; frame time at the overview in software WebGL; triangle count.
6. **Screenshots** in `screenshots/r11/`: an overview of the whole palace; 正大光明 with the 大宫门; a lakeside compound (e.g. 平湖秋月 or 曲院风荷); a densely built court (e.g. 同乐园); the Xiyang Lou strip; a close-up of one hall from the front and from the rear; each before (boxes) and after, and the `assumed=0` view. Check the rear and side faces, not only the fronts.

## Task-specific rules
- Keep it light: no texture files, no new models. The kit is code plus data.
- A documented hall must not change position, footprint or height class because of the kit; the kit draws inside the box's footprint and heights from the data.
- Keep ids stable. The panel text for kit halls says plainly: "drawn from the typology of its hall class, not from a picture of this hall".
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
