# palace_r8 reading workers: common brief

Project: `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh`, the Old Summer Palace (圆明园) before 1860. The base plan S01 (a Qing plan, Princeton) is tied to today's ground by control points. Round 8 improves that tie. **You read points; you never fit or judge errors.**

## What you deliver
JSON lines in `/opt/data/cache/scratch/palace_r8_out_<you>.jsonl`, one object per point, written **as soon as each point is read** (append). Notes and progress in `/opt/data/cache/scratch/palace_r8_notes_<you>.md` (append a line per point or per skipped feature).

```
{"set": "check" | "control", "id": "K-<RG>-01" (check) or "C8-<RG>-01" (control), "region": "<RG>",
 "kind": "shore" | "island" | "ruin" | "bridge" | "gate" | "wall" | "hill",
 "feature": "short description, with the Chinese name if known (e.g. 蓬岛瑶台 NW islet centre)",
 "lon": 116.xxxxxxx, "lat": 40.xxxxxxx, "ground_from": "Esri z18 read" or "Esri z19 read",
 "plan_x": 1234.5, "plan_y": 2345.6, "plan_read": "sure" | "likely",
 "unchanged_because": "why this feature is where it was in 1860 (surviving lake shore kept in form, ruin foundation in place, gate rebuilt on its old base, modern wall rebuilt on the old line ...)",
 "tags": ["the crop tags you used"], "note": "anything doubtful"}
```
`RG` is your region code. Datum: WGS84 (Esri World Imagery is WGS84 Web Mercator, checked against OSM to 3 m). No GCJ-02 or BD-09 source is used.

## The tool
`/opt/data/workspace/000_Dev/palace-beijing-yaga-sh/.venv/bin/python /opt/data/cache/scratch/palace_r8_tools/r8crop.py <command>` (read its docstring with no arguments). Use a unique tag per crop, prefixed with your region code (e.g. `YW-pond3`, `YW-pond3z`).
1. `pair <tag> <lon> <lat> 120` shows today's imagery (yellow grid) and the plan (magenta grid) of about the same ground. The plan crop is **not centred on the same point**: its centre is shifted at random by up to 35 m, it covers about 15% more ground, and it is unrotated plan pixels, turned about 7° from true north. Find the feature **by its form** on both.
2. Zoom on each: `img <tag> <lon> <lat> 40` (z19, about 0.13 m per crop pixel) centred on your rough imagery reading, and `plan <tag> <plan_x> <plan_y> 150` centred on your rough plan reading. Read the exact crop pixel of the feature on each zoom, then convert: `img2ll <tag> <col> <row>` and `plan2px <tag> <col> <row>`.
3. **Open every crop and check that the image came back before reading it.** Read pixels off the displayed grid (lines every 64 px, labelled; dots every 16 px); never from memory, never estimated without the image.
4. `near - <lon> <lat>` prints the distance to the nearest old fit point and to the nearest check point any worker has written so far.

## Rules
- **Blind.** Never compute the old transform's prediction, never compare your plan reading with the crop centre, never compute an error. Identity is decided by form and context (shape of an island, the corner of a lake, a hall's foundation, a bridge), never by which candidate is nearer. If you cannot find the feature on the plan with certainty, skip it and write why in your notes; never take the nearest look-alike.
- **What counts as unchanged since 1860:** lake and island shores that keep their old form (福海, 后湖, the Changchun lakes, most islands; many lakes were re-dug and lined after 1980 on the old outline), ruin foundations in place (Xiyang Lou ruins, excavated and displayed foundations), gates rebuilt on their old base (长春园宫门, 绮春园宫门), bridges whose abutments survive, the garden wall (rebuilt 1984-2006 on the old line, a later source: say so). **Do not use:** modern ditches, ponds and canals dug after 1950 (straight, regular, or not drawn on the plan), new paths and roads, the rebuilt maze 黄花阵 (its line is in doubt), loose stones and re-erected panels (moved after 1976), hills for the check set (a hill top cannot be read precisely on either).
- Prefer **sharp, small features**: a corner of a shore, the tip of a peninsula, the centre of a small island or of a pool, a corner of a foundation, a bridge's end. Read the same physical point on both images (e.g. the island's centre on both, or the corner where two shores meet on both).
- **Check set first (`"set": "check"`):** the number your task gives, spread over your whole region, each at least 60 m from any old fit point (`near`), and at least 80 m from each other. Mix kinds. Choose them by what can be read, before you know anything about errors. Once a check point is written, never edit or delete it; if you later think it is wrong, add a note line in your notes file, and keep it.
- **Then control points (`"set": "control"`):** as many as your task gives, at least 60 m from **any** check point (yours and other workers', `near`). Put them where the old fit has none: your task names the gaps.
- Quality: `plan_read` `sure` when the form is unmistakable on both; `likely` when it is clear but the shore or ruin has some doubt. If doubt is more than that, skip.
- Never write in the repo; no git commands; one crop command at a time (the machine is shared). Do not fetch anything else from the web.
- **Deadline:** your task gives a clock time (`date -u`). Check sets first; if time runs short, stop the control points and finish with a last notes line. Final message: counts written (check, control), what you skipped and why, any doubt about a point.
