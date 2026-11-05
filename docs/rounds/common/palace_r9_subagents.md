# Round 9 (palace_r9_paths): common brief for the workers

Project: `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh`, a reconstruction of the Old Summer Palace 圆明园 before October 1860. Rulebook: its `CLAUDE.md` (read the "Research rules" and "Copyright" sections). This round builds the 1860 walkways, courtyard paths, galleries, causeways, dikes, steps, landings and boat routes, and walk routes in the 3D view.

## Hard rules
- **Write ONLY to your own scratch files** named in your task (`/opt/data/cache/scratch/palace_r9_*`). Never edit, create or delete anything in the repo. No git commands. The coordinator alone writes the repo.
- **Deadline:** the clock time in your task (`date -u`). Stop at it, whatever is left. Write your notes file incrementally (after each scene or source), so nothing is lost if you are stopped.
- **Copyright:** plan crops of S01 and research-only images stay in scratch. Quote Qing texts (public domain) verbatim; summarise modern work in your own words, with a citation. Never copy modern figures.
- **Honesty:** mark each claim `verified` (you saw it on the page or image), `assumed` (your inference) or `unknown`. Never invent a path, a quote or a locator. If a page refused you, write that down and move on; do not work round blocks, logins or robots rules. Web search budget: about 25 searches each.
- **Sources:** cite the project's source ids (S..) from `research/sources.md` where the source is already there; a new one gets `NEW: <full citation + URL>`.
- Terms: 甬道 paved way, 游廊 covered gallery, 爬山廊 mountain gallery, 垂花门 festooned gate, 踏跺/台阶 steps, 堤 dike, 码头 landing, 船坞 boat dock, 御路 imperial road.

## Confidence (as the project grades)
- A = drawn on a source made while the gardens stood (a Forty Scenes leaf of 1744, the Xiyang Lou engravings of the 1780s, a Yangshi Lei drawing, a pre-1860 text that draws it) or a remain in place (excavated paving).
- B = drawn on the base plan S01 (it counts as B, not A, in this project), or described only in words, or a later source.
- C = inferred: typology, symmetry, "a path must have led here".

## For the plan readers
Tool (from the repo folder): `cd /opt/data/workspace/000_Dev/palace-beijing-yaga-sh && uv run python /opt/data/cache/scratch/palace_r9_tools/crop.py <command>`; read its docstring first (`head -20` of that file).
- `ids <scene>` lists the rows (halls) of a scene with plan pixels, its gates and bridges.
- `crop <tag> <x> <y> [half]` writes a clean crop and one with ids, 2x, grid every 50 plan px LABELLED IN ABSOLUTE PLAN PIXELS (every 100 printed). Use a tag starting with your region (`ymc_YM01a`). Open the PNGs with the Read tool.
- `show <tag> <your traces csv> <x> <y> [half]` draws your lines over the crop: check every scene this way once.
- Context lists: `/opt/data/cache/scratch/palace_r9_context/{rows,gates,bridges,scenes}.csv` (plan pixels).
- Scale: about 4.2-4.8 plan px per metre; 10 m = about 45 px. The plan is turned about 7° from north; "up" is roughly north.

What S01 draws: halls as bay rows (rectangles with cross lines), court walls as single lines, gates as short bay rows or gaps in a wall, galleries as narrow one-bay rows joining halls (often L-shaped or curved, e.g. 谐奇趣's arms, the long rows at 含经堂), steps as small bracket marks, bridges as short strips with flared ends over water, water as outlined areas, hills as scalloped outlines. Paths in open courts are mostly NOT drawn: the court and its axis are.

**Trace, scene by scene, in your priority order:**
1. galleries 游廊 (kind `gallery`, or `mountain_gallery` where it climbs a hill outline): the centre line of the narrow bay row, end to end, `from_id`/`to_id` the halls it joins. If the gallery itself is listed as a row in `_ids` (a red id on it), give that row id in `in_box_row`. Grade B (drawn on S01).
2. dikes 堤 and causeways (kind `dike` or `causeway`): a strip of land between two waters that carries a way; centre line; B when the strip is drawn, with a note.
3. steps (kind `steps`) where drawn (bracket marks before a hall or up a hill): a short line in the direction of climb; B.
4. the court axis (kind `paved_way` 甬道): from a gate opening (G.. id, or the gate hall row id) straight to the door of the hall in line with it, and on to the next gate/hall. Inferred from the layout unless something is drawn: C, and say "court axis, not drawn".
5. paths along a shore, round a hill, between compounds (kind `courtyard_path` inside a court, `service_path` behind, `imperial_road` for the main ways outside the courts, `bridge_approach` from a bridge end to the nearest hall or path): only where something on the plan shows them (an opening, a bridge whose ends must lead somewhere, a gate in line). Else C with the reason.
6. landings (kind `landing`, one point at the water edge in front of a hall or at steps into water) and boat docks (kind `dock`, 船坞: a long narrow hall standing into the water; one point at its water end). Give the water body (`water` column: 后湖, 福海, 前湖, or "canal" / "pond" with the scene id).
7. boat routes (kind `boat_route`) only where a source names one; the Fuhai reader traces the tour (see their task).

**Ends:** start and end every line ON something: a gate (G id or gate row id), a hall's door side (row id), a bridge end (BR id), a landing (your key), or another of your lines (its key). Put those ids in `from_id` / `to_id`. The coordinator snaps the ends to the doors of the 3D boxes and measures the gaps, so get the ids right; the pixel ends may be approximate (within 10 px). Never end a line in water or inside a hall. A line never crosses water except over a bridge (then split it at the bridge ends and give the BR id).

**Output:** `/opt/data/cache/scratch/palace_r9_traces_<region>.csv`, UTF-8, header exactly:
`key,scene,kind,name_zh,from_id,to_id,points_px,in_box_row,water,drawn_on_s01,confidence,width_m,sources,note`
- `key`: your own id, region prefix + number (`YMC-001`).
- `points_px`: `x y;x y;...` in absolute plan pixels (integers), at least 2 points for a line, 1 for a landing or dock.
- `drawn_on_s01`: what on the plan shows it (`gallery bay row`, `land strip between two waters`, `steps marks`, `opening in court wall`, `nothing: court axis`, `nothing: reach only`).
- `confidence`: B if drawn, C if inferred (the coordinator raises to A where a leaf or a dig shows it).
- `width_m`: only from a drawn width (px / 4.5) or a source; else blank.
- `sources`: `S01` for what is drawn, plus any text id.
Also a notes file `/opt/data/cache/scratch/palace_r9_notes_<region>.md`: per scene, what you traced, what the plan shows and does not, doubts. Breadth first: about 5-8 minutes per scene; the famous ones first; at the deadline stop and write which scenes you did not reach.

## For the source workers
Output: your notes file, plus a CSV named in your task. Every row: what, where, source id, locator (juan:leaf, page), the quote (Qing text, verbatim) or our summary, confidence, verified/assumed/unknown, the link.
The repo already holds much: `research/evidence/catalog.csv` (2365 texts, poems, drawings, digs: grep `excerpt_zh` and `summary_en` for 甬道 游廊 廊 码头 船坞 舟 堤 桥 路 门 route boat), `research/scenes/*/README.md` and their `interior.csv`, `halls.csv` (`relation` column), `digs.csv`, `research/sources.md`. Start there before the web.
