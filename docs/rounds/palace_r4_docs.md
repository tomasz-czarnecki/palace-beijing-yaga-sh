# palace_r4_docs: document the whole project so it can serve as the reference for future jobs

You are working in `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh`, the reconstruction of the Old Summer Palace (圆明园 Yuanmingyuan) before 1860.

Four rounds are done and committed locally:
- palace_home: the homepage
- palace_r1b: research, maps, georeferencing, the building inventory
- palace_r2_map: the dev map, the 3D boxes, the building pages
- palace_r3_evidence: pictures, drawings and texts for every building

Read `CLAUDE.md`, `research/README.md` and `git log --stat`.

## What Tomasz asked for (his words)
"Make sure that you document everything in CLAUDE.md or some research documentation, so later we can use this project as a reference for different jobs."

## Deliverables
1. **`CLAUDE.md`:** bring it fully up to date, the project rulebook a new worker reads first. Cover goal, status, the rules, the layout, every pipeline step with its rebuild order, public vs private, ports, and where things live.
   - Keep it lean: under about 200 lines. Point to the docs below for depth.
   - Keep every existing rule; nothing that is still true may be dropped.
2. **`research/README.md`:** every file, field, id scheme (S, Q, P, E, building ids), confidence grade, catalogue and layer, all accurate against the actual files. Check each field name against the real headers with a script.
3. **`docs/METHOD.md`:** the reusable playbook, written so the next historical site (any town, palace or fortress, anywhere) can follow it step by step. Cover:
   - **Phases in order:**
     1. rulebook
     2. homepage
     3. research
     4. georeferencing
     5. inventory
     6. typology
     7. dev map
     8. boxes in 3D
     9. building pages
     10. evidence hunt

     For each: its inputs, outputs, the scripts involved, and how long it took (take the times from the git log and from the progress files in `/opt/data/cache/scratch/palace_*_progress.md` if they still exist).
   - **The data model:** the CSV and GeoJSON hand-offs, the ids, the confidence grades, the evidence catalogues, the panel JSON, and the parent fallback ("set of buildings").
   - **The copyright model:** free vs research-only, link cards, what may enter `site/`.
   - **Source strategy:** which kinds of sources gave the most (plans, albums, engravings, period texts, old photos, OSM, DEM, archaeology), how to search them (languages, catalogues), and what blocked.
   - **What was specific to China:** GCJ-02 and BD-09 datums, Chinese catalogues, the sensitivity of the topic.
   - **What carried over from Küstrin** (`/opt/data/workspace/000_Dev/kostrzyn-yaga-sh`, read-only) and what differed.
   - **Pitfalls hit and their fixes.** Include this one: a research round launched its subagents in the background, ended its turn, and print mode killed them after 10 minutes. Fix: foreground subagents, `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0`, and chains gated on deliverables instead of exit codes.
   - **A checklist to start the next project.**
4. **`docs/rounds/`:** copy each round's brief from `/opt/data/scripts/rounds_palace/*_brief.md` here unchanged, as `<name>.md`. Add a `docs/rounds/README.md` with one entry per round: date, model and effort, duration, what it delivered (with counts), its commit hash, and what went wrong. Take the result text from `/opt/data/cache/scratch/<name>.jsonl` (the rows with `type == "result"`) where it still exists. Read big logs with a small Python script, never in full.
5. **`docs/` stays out of `site/`.** Nothing public changes. Don't touch `site/`, the data or the generators. This is a docs-only round.

## Rules
- **Every statement must be true of the repo.** Check paths, script names, field names and counts by running commands. Mark anything you can't verify.
- **Subagents only in the foreground**, if you use any. Never end your turn while something still runs.
- **No git commands that write.** Lily commits.
- Log milestones to `/opt/data/cache/scratch/palace_r4_docs_progress.md`.

## Final message
Lead with what a future worker gets: the files, and how long `METHOD.md` is. Then list:
- anything in `CLAUDE.md` that was wrong or stale and is now fixed
- what you could not verify

Do not ask questions. Work only in this repo, plus the scratch paths named above.
