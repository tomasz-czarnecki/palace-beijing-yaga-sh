# palace_r30_xianfa: detailed models built from the references: the east end of the Xiyang Lou: 线法山门 Xianfa Shan Men (XY12-01), 螺蛳牌楼 Luosi Pailou (XY13) and 线法墙 Xianfa Qiang (XY15)

Round name: `palace_r30_xianfa`. Ports 9160-9169. Scratch notes: `/opt/data/cache/scratch/palace_r30_xianfa_*`.

## Why
Tomasz: "add the famous buildings to the queue. If we have pictures and references, we want to build them from reference." The kits (Round 11) draw every building from its class; the famous ones need a model that follows their own evidence. Round 13 made the engraving-overlay tool (`tools/plate_overlay.mjs`) and the pilot model of 谐奇趣 (`models/XY01-xieqiqu/`): that is your pattern. Read its README, `summary.json` and generator, `models/README.md`, and the Round 13 entry in `docs/rounds/`, before you start. Repeat the method; do not invent a new one.

## Objects
- **XY12 线法山门 (XY12-01)**: the stone gate of the perspective hill (13.6 x 2.0 m). **XY13 螺蛳牌楼 Luosi Pailou** (22.9 x 3.0 m): the spiral-pattern pailou gate. **XY15 线法墙 Xianfa Qiang** (7.3 x 1.8 m per unit): the perspective wall, in its repeated units. The dossiers are `research/xiyanglou/XY12-xianfa-shan/`, `XY13-luosi-pailou/`, `XY15-xianfa-qiang/`. Build them as the plates show them; for the repeated wall build one unit and place it by the dossier's count and spacing.

For each object, in this order of authority: its dossier (`research/xiyanglou/<ID>-*/` or `research/scenes/<ID>-*/`: README, `dimensions.json`, `views` and `viewpoints` tables), the plates and the ruin photos or paintings it lists (free copies in `research/photos/images/`, research-only ones in `research/raw/`), the plan readings, the excavation reports, and the reconstructions by others (`research/reconstructions/catalog.csv`, reading aids only: never a source for sizes, positions or details we cannot confirm from period evidence). Record, for every parameter of the model, its source, method and confidence in `summary.json`.

## Deliverables (per object)
1. **The model** in `models/<ID>-<slug>/`, following the pilot: `summary.json` (sources, parameters, confidence, `hides` only for phantom volumes, never the model's own volume), a generator (Python writing a GLB, or a JS module on the stone/hall kit, as the pilot did) and a `README.md` with the evidence list per side and the iteration log. Replace the kit form in the 3D view; the old box stays invisible as the click target. The panel shows "Our model now" with the small viewer, and says what each part is based on.
2. **Build from the references, side by side.** Put the references next to the model (engraving, photo, painting, plan) and correct the model until they agree; do not model from memory or from the typology where a picture shows the part.
   - **Every side gets detail:** undocumented façades (rear, ends) are carried round from the documented bays or the class, marked C. Windows are recessed with frames and glazing bars, readable as glass.
   - **Plain geometry, simple but faithful:** the proportions, rhythm, roof forms, stairs, balustrades, columns, ornament bands and colours that the references show. No photo textures.
   - **Everything connects:** the platform meets the ground (Round 10), paths meet the doors (Round 9), stairs meet terraces, pools meet their courts. Measure every joint in metres, before and after, and shoot close-ups of the joints and of the far sides.
3. **Match check.** For every object with plates or a camera viewpoint (`research/xiyanglou/viewpoints.csv`, or the scene's views table), run `tools/plate_overlay.mjs`, write the key-point fit table (`research/xiyanglou/plate_fit_<ID>.csv` or `research/scenes/<ID>-*/plate_fit.csv`), and state the final error per reference. Where the model and a reference disagree, say which is likely right and why; engravings idealise. Never tune the model to hide a disagreement between two references: record it as a question.
4. **Rear and side checks from the ruin photos:** for the Xiyang Lou, the ruins' photographs show the stone as it stood after 1860; use them for proportions and masonry, and the plates for the 1780s state, as the dossier says.
5. **`tools/check_models.py`** passes for the new models: sources present, the module or GLB loads, joints within 0.5 m, file size within the budget (each model under 1.5 MB compressed; say so if not).
6. **Public copy and credits:** only free images are shown on the site; the research-only overlays stay on localhost (`/_local/`).
7. **Screenshots** in `screenshots/r30/`: for each object a front, a rear, a side and a detail, all from the references' directions where possible; the overlay beside each reference (localhost only if the reference is research-only: never post those), a before (kit) and after, the panel with the viewer. Open every one yourself, compare with the reference, and fix what is wrong before you finish.
8. **Docs:** update the object's dossier README, `research/wishlist.md` (the biggest remaining guess per model and what would replace it), `CLAUDE.md`, `research/README.md` and `docs/METHOD.md` (what you learned about building from references).

- If the evidence for a part is only a plate silhouette, build that silhouette and mark it C: the ruins here are among the best known stonework of the palace, so keep the stone-by-stone survivors the dossier lists.


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
