# palace_r13_pilot: the engraving overlay tool and the pilot model of 谐奇趣 (Xieqiqu, XY01)

Round name: `palace_r13_pilot`. Ports 8890-8899. Scratch notes: `/opt/data/cache/scratch/palace_r13_pilot_*`.

## Why
The Xiyang Lou round named 谐奇趣 (XY01) as the first detailed model: it is the only building photographed from three sides before it fell (Ohlmer 1873, P0183-P0189 and others) and plates 1 and 2 of the 1783-86 copperplate engravings agree on its height (top eave about 15 m). Before and while building it we need an objective quality gate: render our model from each plate's camera and lay it over the engraving. The cameras are in `research/xiyanglou/viewpoints.csv` (position, bearing, distance, error). Round 11 gave the Xiyang Lou a stone kit; this round puts a hand-built layer on top of it for one building, and proves the method.

## Deliverables
1. **The overlay tool (`tools/plate_overlay.mjs` plus `tools/plate_overlay.py` if needed, and a dev-page mode `?plate=<n>` in the 3D view).** Given an object and a plate, it:
   - loads the plate image (free copy from `research/photos/images/`; the Commons high-resolution copy in `research/raw/plates/` if the plate is research-only: such overlays are localhost only),
   - sets the 3D camera from `viewpoints.csv` (position, bearing, eye height, and a focal length fitted to the plate's field of view, where the viewpoint row states `f`; otherwise fit it and record it),
   - renders the model with the engraving beside it, as a 50 % blend and as an edge overlay, and writes the images to `screenshots/r13/`,
   - **measures** the match: key points (ridge ends, cornice corners, pediment tips, door heads, stair feet) clicked or listed per plate in `research/xiyanglou/plate_keypoints.csv` (plate, object, point name, x, y in the plate's pixels, from a careful reading), versus the projected model points, giving the pixel error and the equivalent in metres at the object. Write the table to `research/xiyanglou/plate_fit_<object>.csv`.
   - Keep the tool generic: any plate, any XY object.
2. **The pilot model of 谐奇趣 (`models/XY01-xieqiqu/`).** In the repo's convention (`models/README.md`): `summary.json` (sources, confidence, `hides` if any, parameters with their sources), a generator (`models/XY01-xieqiqu/xieqiqu.py` that writes a GLB, or a JS module built on the stone kit; follow what Round 11 made and the Küstrin pattern), the README with the evidence list. Build the main block, its two wings with the colonnades, the octagonal music pavilion (八角奏乐亭) and the oval fountain basin in front (海棠形喷水池, a basin of 30 × 18 m as the data has it), from:
   - the dossier `research/xiyanglou/XY01-xieqiqu/` and its `dimensions.json`, the plates 1 and 2 and the ruin photos P0183-P0189, the ISPRS 2015 paper's description (S108, cited, not copied), and the Tsinghua / park reconstructions as reading aids only.
   - **Every side gets detail:** the façades with no picture (the west end, the rear) are carried round from the documented bays and marked C. Windows are recessed with frames; the stone base, the pilasters, the balustrades and the glazed roof tiles follow the plates.
   - Replace the XY01 kit form in the view; the old box stays invisible as the click target; the panel shows "Our model now" with its small viewer (as Küstrin's `model3d.js`).
3. **Iterate against the plates.** Run the overlay for plates 1 and 2 and for the ruin photos' viewpoints, fix the model where the match is worst, and repeat until the key-point error is within what the evidence allows (state the final error per plate, and where the model and the engraving disagree, say which is likely right and why; some engraving elements are idealised). Keep the iteration log in the README. Do not tune the model to hide a disagreement between plates: record it as a question.
4. **Joint and ground checks.** The model's platform meets the Round 10 ground (gap in metres), the pool and the fountain meet the court, the path strips of Round 9 meet its doors. Close-ups of every joint and of the rear side.
5. **A second building, if time allows:** apply the tool to 海晏堂 (XY08) with the kit only and report the plate fit as a baseline for the next model round; no detailed model.
6. **`tools/check_models.py`:** every `models/*/summary.json` has its sources, the GLB or module loads, `hides` never lists the model's own volume, joints within 0.5 m, file size under the budget (state it: a model under 1.5 MB compressed).
7. **Screenshots** in `screenshots/r13/`: the overlay for plate 1 and plate 2 (localhost only if research-only: never post an overlay of a research-only plate on the public site), the model from the Ohlmer viewpoints, a front and a rear view, a before (kit) and after, the panel with the viewer. Public views must show only free images.

## Task-specific rules
- Free images may be shown publicly with credit. Research-only plate copies and any overlay made with them stay on localhost (`/_local/`).
- The model is a showcase of the method, not a one-to-one reconstruction: approximations are fine when marked C with a reason, and the wishlist gets a row for each biggest guess (the Yangshi Lei sheet 985 would replace most of them).
- After this round the final message names the next three models, in the order the Round 7 analysis gave (正大光明 with the 大宫门, 含经堂, the 九洲清晏 axis), with the evidence each has.

## Common rules for this round

As for Round 12 (`docs/rounds/palace_r12_greens.md`, "Common rules for this round"): subagents in the foreground with a clock deadline and notes in scratch, the worker alone writing shared files; Python through the repo's `uv`, Node and Playwright outside the repo; own ports, stopped at the end; no git writes; generators idempotent and every check passing; the site growing by under 15 MB of free or derived data only; screenshots from one page load, opened and fixed; docs updated (`CLAUDE.md`, `research/README.md`, `docs/METHOD.md`, this brief and its row in `docs/rounds/README.md`); progress lines in scratch; every claim marked verified, assumed or unknown; the final message leading with the check script's numbers, before and after.
