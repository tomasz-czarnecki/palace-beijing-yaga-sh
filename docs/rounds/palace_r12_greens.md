# palace_r12_greens: trees, rocks and planting: the gardens' vegetation, by scene, from sources

Round name: `palace_r12_greens`. Ports 8880-8889. Scratch notes: `/opt/data/cache/scratch/palace_r12_greens_*`.

## Why
Yuanmingyuan was a garden: its character was water, hills, rocks and planting (the Forty Scenes name them: apricot blossom at 杏花春馆, lotus at 曲院风荷, pine and bamboo, willows along 福海, the peach trees of 武陵春色). The project has no vegetation layer at all, so halls and hills stand bare. Küstrin did this (`scripts/greens1913.py`, `site/reconstruction/greens3d.js`, `research/greens/`): the plans draw no plants, so the trees come from dated cards and texts; the places are generated, not surveyed; each area carries a confidence for its extent and another for its trees. Do the same here, with much richer sources.

## Deliverables
1. **Sources first (`research/greens/README.md`, `research/greens/species.csv`).** For every scene of the Forty Scenes (and the compounds of Changchun and Qichun Yuan where sources exist), collect what is planted and where:
   - the Qianlong poems and prefaces (the plants named in each, the seasons)
   - 日下旧闻考 and the Qing garden texts
   - the leaves of 1744 and later paintings, read for tree groups, rocks, lotus ponds, bamboo and lawns (note which rows come from a picture)
   - the court's planting lists in the archives, where cited (e.g. 内务府 records on 松, 柏, 梅, 竹; cite the works that cite them)
   - today's survivors: old trees and rocks in the park (the park's records of ancient trees, 古树名木, surviving 太湖石), with their positions where published
   - 1860 accounts of the garden's look (Swinhoe, Loch, Wolseley, Hugo, Attiret 1743)
   Each row: scene id, species (Chinese, Latin, English), role (avenue, grove, specimen, hedge, lotus, reed, lawn, bamboo, rockery plant), place in the scene (north bank, court, along the bridge), season, `sources`, `confidence`. Plants that do not suit a scene (e.g. subtropical species in Beijing) are rejected, with the reason.
2. **Layers (`research/layers/greens_1860.geojson`, public copy under `site/reconstruction/data/`).** Polygons and lines with: `kind` (grove, avenue, specimen_tree, bamboo_grove, lotus_pond, reed_bed, lawn, flower_bed, rockery, hedge), `species`, `density`, `height_m` (a mature crown: from the texts, the leaves, or a species default), `season`, `extent_confidence` and `trees_confidence` (A/B/C), `sources`, `note`. Extents from the plan or the leaf (anchor them to the scene's own geometry, not to the painting); where only a text says "pines on the north bank", the extent is C and generated.
3. **Rockeries (假山) and garden rocks.** Where texts and leaves name them (the 太湖石 at 玉玲珑馆, the rockeries of 九洲清晏's rear lake, 绮春园's rockwork), add them as a layer with a simple lumpy-mass geometry and a stone colour; confidence per object. Each rockery is anchored on the ground (Round 10's terrain) and meets its pool edge.
4. **Generator and view (`scripts/greens1860.py`, `site/reconstruction/greens3d.js`).** The generator places individual trees in each area (seeded, with spacing, avoiding halls, paths, water, walls and boxes; avenues along the paths and causeways, weeping willows at the water's edge, lotus on the ponds' surfaces, bamboo clumps) and writes a compact data file; the browser draws them as instanced simple forms by species type (round broadleaf crown, conifer cone, willow droop, bamboo cluster, lotus leaves at the water level), colour by season (`season=spring|summer|autumn|winter`, default summer), with instancing so the whole palace stays light (state the instance count and the frame time in software WebGL). Toggle `greens=0|1`, `assumed=0` hides generated planting, `conf=1` tints by confidence. Rerun the generator after any change to halls, paths, walls or the ground, as Küstrin's note says.
5. **No vegetation through buildings,** none in water except lotus and reed, none across paths; every tree's base follows the ground. **`tools/check_greens.py`** counts areas and trees by kind, confidence and species; reports any tree inside a box, in water (except lotus and reed), or on a path; and the vertical gap to the ground; fails on any.
6. **Panel.** A scene's panel lists its plants with their sources ("Planting of this scene: …"), as text from the species table, and says what is from a source and what is typical.
7. **Screenshots** in `screenshots/r12/`: an overview, 平湖秋月 or 曲院风荷 (lotus), 杏花春馆 (blossom), 武陵春色 (the peach grove), 九洲清晏's lake and rockwork, the Xiyang Lou strip (formal planting), and a bare-versus-planted pair of the same view. Check that nothing grows through a hall or floats.

## Task-specific rules
- Mark the extent and the species of every generated area as such; never present generated planting as surveyed.
- Keep the generated data under 4 MB for the whole palace; draw trees as instances.
- Respect copyright: summarise the books; free images only (Commons) go into the panels, with credit.

## Common rules for this round
The common rules of Rounds 10 and 11 (read the rulebook and the template first; Tomasz's standing modelling decisions; subagents in the foreground with deadlines and notes in scratch; Python through `uv`, Node and Playwright in scratch; own ports, never 8790; no git writes; idempotent generators and every check passing; public site free or derived data only, growth under 15 MB; screenshots from one page load, opened and fixed; docs updated; progress lines every 15 minutes; every claim marked verified, assumed or unknown; a final message that leads with the check's numbers).
