# palace_r8_georef: make the map more accurate (georeferencing) and fix the wall/box mismatch (Q64)

You are working in `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh`, the reconstruction of the Old Summer Palace (圆明园 Yuanmingyuan) before 1860. Read these first:
- `CLAUDE.md` (rulebook), `docs/METHOD.md`, `research/README.md`
- `research/questions.md`: especially Q64 (walls vs boxes), the georeferencing questions (the plan's scale, the 10 m check set, the western plain) and Q71
- `research/georef/` and `research/plan/`, plus the scripts that produce them (`scripts/georef.py`, `scripts/trace_plan.py` and neighbours)
- `docs/rounds/palace_r1b.md`, `palace_r2_map.md` and `palace_r6_xiyanglou.md` for how the georeference, the boxes and the Xiyang Lou fixes were done

Everything is committed (the previous round, `palace_r7_scenes`, is committed by the chain before you start). The template project `/opt/data/workspace/000_Dev/kostrzyn-yaga-sh` is read-only: never edit it.

## Why this round
Every box, wall and panel depends on how well the Qing plan is placed on today's ground. The state at the end of Round 6:
- **Base plan fit:** the Princeton 1920s plan (`research/georef/princeton-1920s.json`) fits to about 10.6 m RMS, and about 16.5 m leave-one-out (median 11.8 m). The worker who made it edited its check set once, after seeing the errors: first pass median 52 m, kept set 31 m (METHOD.md says so). The western plain was the weakest part.
- **Walls vs boxes (Q64):** the boxes of the Xiyang Lou were moved onto the ruins, but the garden walls stayed where the plan has them. From Tomasz's camera, the maze's outer ring runs into the boundary wall, and one of 谐奇趣's gallery arms crosses it.
- **The 大水法 court (Q71):** a hill still pushes into the court, and a stray triangle of ground sits on the grass.

Better placement lifts every later model. Tomasz plans to run this project on his own machine; keep everything reproducible from the repo.

## Goal
Place the walls, water, hills and halls consistently, with an honest accuracy map: where it is good to about 3-5 m, where it is 10-20 m, and why.

## Deliverables
1. **A blind, fixed check set first.**
   - Pick it before fitting anything, from surviving features not used for the fit: lake and island shore corners, ruin footprints with surveyed coordinates (OSM and published survey points), bridge abutments, gate foundations, hill tops from the DEM.
   - Write it to `research/georef/check_points.json` with the coordinates' datum and source (WGS84; convert any GCJ-02 or BD-09 point).
   - Freeze it (a hash in the file). Never edit it after seeing the errors; if a point looks wrong, annotate it and keep it.
2. **Improve the fit, region by region.**
   - Use piecewise transforms: a thin-plate spline or local affine patches per garden region, with a smoothness limit.
   - Add control points from: today's lakes and islands (OSM, DEM-derived shorelines), the survey of the Xiyang Lou ruins, the 1933 and 1920s plans where they agree, the Forty Scenes leaves (the layouts of scenes, a lake edge on both sides) and the wall corners.
   - Compare against a plain global affine and against the current fit on the frozen check set. Report both, with the median, the 90th percentile and the maximum, per region (Yuanming Yuan east and west, Fuhai, Changchun Yuan, the Xiyang Lou strip, Qichun Yuan).
   - Keep the previous fit in the repo as `previous` (a file or a key), and build the new one beside it. Rebuild with a script (`scripts/georef.py` or a new one), not by hand.
3. **Walls and gates.**
   - Re-derive the garden walls and gates (`walls_1860`) from the improved fit, and reconcile them with the surviving wall remains and today's park boundary (OSM, DEM).
   - Where the plan and the ruins disagree, the ruins win. Record every change in `questions.md` with the shift in metres.
   - Fix Q64 for the Xiyang Lou: no wall through the maze ring or a gallery arm, and the walls still enclose the strip.
   - Fix Q71: the 大水法 court's ground and the hill.
4. **Water, islands and hills.**
   - Compare `water_1860` and `islands_1860` against today's shorelines where they survive (the lakes, Fuhai, the canal network) and against the Forty Scenes leaves.
   - Fix the layers where the new fit shows a shift, and record each change. Check that no box stands in water after the change (the boxes script prints it).
5. **Boxes.** Rerun the boxes generator (`scripts/boxes1860.py` or its current name). Report how many boxes moved by more than 3, 5 and 10 m, and any that now overlap each other or a wall. Never renumber ids.
6. **An accuracy layer for the dev map:** `research/layers/georef_error.geojson` (a grid or polygons with the expected error in metres per region, from the check set) and a toggle in the dev map ("placement accuracy"). On the public site, show it only if it is not research-only derived; otherwise localhost only.
7. **Checks and docs:**
   - **Checks:** `tools/check_georef.py`: reads `check_points.json`, computes the errors from the current layers and fails if the median per region gets worse than the committed baseline. Run `scripts/building_pages.py` twice (the second run changes nothing), `tools/check_pages.py`, `tools/check_evidence.py` and `tools/check_docs.py`.
   - **Screenshots** in `screenshots/r8/`, from one page load, each before and after: Tomasz's Xiyang Lou camera, the 大水法 court, Fuhai, 九洲清晏, the western plain, and the dev map's accuracy layer. Open each one yourself and fix what is wrong. Public views show no research-only plan; the overlay stays localhost-only.
   - **Docs:** update `CLAUDE.md`, `research/README.md` and `docs/METHOD.md` (the blind check set, the piecewise fit, what moved). Copy this brief to `docs/rounds/palace_r8_georef.md` and add its row to `docs/rounds/README.md`.

## Rules
- **Honesty:** never tune the check set to the result. Report the fit as it is, including regions where the new fit is no better. If the piecewise fit does not beat the old one on the frozen set in a region, keep the old one there and say so.
- **Subagents in the FOREGROUND only:** several Agent calls in ONE message, never `run_in_background`. Never end your turn while a subagent, crawler or background shell still runs. Give each a clock deadline (`date -u`) and incremental notes in `/opt/data/cache/scratch/palace_r8_notes_<topic>.md`.
- **Copyright exactly as in `CLAUDE.md`.** Satellite and map tiles are for reading only and are never saved into git.
- **Tools:** Python from the repo `.venv` via `uv run`. Node and Playwright in `/opt/data/cache/scratch/palace_r8_tools/`.
- **Ports** 8840-8849, bound to 127.0.0.1, stopped at the end. Never use 8790.
- **No git commands that write.** The chain commits and pushes.
- **Progress:** one line per milestone, at least every 15 minutes, to `/opt/data/cache/scratch/palace_r8_georef_progress.md`.
- Mark every claim verified, assumed or unknown. Never invent a coordinate.

## Final message
Lead with the accuracy table, before and after, per region, on the frozen check set (median, 90th percentile, max). Then list:
- how many boxes, walls and layers moved, and by how much
- Q64 and Q71: fixed or not
- where the placement is still weak, and what would improve it (a source or a visit)
- what is verified and what is assumed

Do not ask questions. Work only in this repo, plus the scratch paths named above.
