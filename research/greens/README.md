# The planting of 1860 (Round 12)

Trees, bamboo, lotus, reeds, flower beds and the rockeries 假山 of the three gardens, by scene, from sources. **No plan draws a plant** (S01 draws halls, water, walls and ways), so every plant's *place* is generated. What a source gives is the *species* of a scene and the *side* of it: "pines behind the hall", "willows on the north bank", "lotus over the whole lake". Every figure below comes from `scripts/greens1860.py` and `tools/check_greens.py` (`research/greens/greens_check.json`).

## What the sources say

`research/greens/species.csv`: 823 rows from six readers (Round 12). One row per scene, plant and place that a source supports. 759 rows are kept and 64 rejected. They cover 110 scenes and the three gardens.

| Kind of source | Rows | What it gives |
|---|---|---|
| poem | 355 | the 1744 poems (S40) and the later imperial poems (S201, S360, S361): a plant named for a hall, often with its season |
| leaf | 298 | the 1744 album (S08), leaf by leaf; the Xiyang Lou plates (S70, S71): tree groups by side, counts, lotus share, rocks |
| preface | 62 | the prose prefaces of the 1744 poems (S40 through S05): the plant that names the scene, with its place |
| account | 45 | Attiret 1743 (S157, S911), Macartney 1793 (S1160), Wolseley, Swinhoe and others 1860 (S240 and the narratives already in `research/sources.md`) |
| text | 35 | 日下旧闻考 (S05) and other Qing prose |
| study, survivor, archive | 28 | modern studies (S1141, S1140), the park's old trees (S1161, S1162), moved rocks (S1163-S1165) |

Grades of the kept rows: 676 A (a source of the time names the plant for this scene), 68 B, 15 C. Rejected rows (`use` reject, with `reject_reason`) are allusions and figures of speech (桃源 as a name, 菱花 a mirror, 青莲 the poet Li Bai, 金荷 a wine cup), Buddhist images, plants of the Western Hills seen from the garden, and texts after 1860. Tender plants that a text says were kept indoors or in pots in winter (梅 mei, 芭蕉 banana, 桂, 兰) are kept as `potted` and not drawn; the two mei of 淳化轩 (CC02) grew in the court under a felt shed (S201, 1792) and are drawn.

What stands out:
- **Willows** line almost every shore on the leaves, 10-30 a leaf (album readers). 福海's dikes carry willow and peach alternately (S201, 1767).
- **Lotus** is painted only at 濂溪乐处 (85-90% of its lake) and 多稼如云 (about 90%); 曲院风荷 and 平湖秋月 are named for lotus in their texts but painted as open water (Q209).
- **Pines** stand behind the main halls and on the hills; Changchun Yuan's were planted young about 1770 (Q214). An earth bank planted with pine and "cedar" ran inside the outer walls (Wolseley, S240).
- **Blossom:** apricot round the village of 杏花春馆 (YM09), "ten thousand" mountain peach on 武陵春色's hills and garden peach along its stream (YM14), more than ten yulan magnolias round 含韵斋 (YM27), several hundred tree peonies before 镂月开云 (YM04).
- **Bamboo:** "ten thousand" at 天然图画 (YM05), bamboo islets and reed banks at 澡身浴德 (YM30).
- **The Xiyang Lou** has formal planting: grids of two- and three-tier clipped trees before 海晏堂 (about 50) and 线法山 (about 100), conical conifers on 线法山, natural woods behind the courts (plates P0042-P0058). The maze's walls are brick with clipped trees on top on plate P0045 (Q211).
- **Survivors:** the only old trees left are 26-28 in 正觉寺 (QC11), mostly cypresses and junipers, positions unpublished (Q213). Rocks moved away: 青莲朵 (from 蒨园 CC03 to the 中国园林博物馆), 青云片 (to 中山公园), a 狮子林 rock returned in 2020.

## What the view draws

`scripts/greens1860.py` turns the kept rows into areas and plants:
- **Areas:** rows that say the same thing (scene, plant, place, hall) make one area, its zone cut from the scene's free land: the scene's outline on S01 less water, boxes, ways, walls, bridges, landings, paddy and courts, and then by `place` (a side of the scene's centre, the shore band 1-5 m from the water, its islands, hills, courts in front of or behind the main hall, 2.5-14 m round a named hall, the dikes, the ways, the water for lotus and reeds). A scene with no outline (福海 YM54) takes its water body's shore.
- **Patterns:** avenues along the ways or the shore; a pair (or the stated number) either side of a hall's front for a specimen; a grid set square to the hall for topiary; seeded darts for groves, bamboo and flower beds; clumps on the water for lotus, floating leaves and reeds, with gaps by a seeded smooth noise at the share the leaf gives (else 60%, 35% for a C row).
- **Counts:** "about N" in a row's note (the painter's or the text's count), a Chinese count (二株, 十余本), a specimen's English count ("four tree-arbours"); else the zone's area at the kind's spacing and the density the note gives. A specimen with no count is 3 trees, a flower bed 36 plants.
- **Fill:** free land with no sourced plant within 5 m of its crown gets the typical planting, one area per garden and zone: willows at the shores, mixed pine, broadleaf and blossom on the hills, sparse clumps with open grass elsewhere. `assumed: true`, C, its basis in the area's `note`; garden-wide rows (GARDEN-YM, -ALL) say what grew there and are cited, never where.
- **Sizes:** species defaults (C): pines 12 m with an 8 m crown, willows 11 m, broadleaf trees 13 m, peach 4.5 m, apricot 6 m, magnolia 8 m, bamboo clumps 5 m; each plant ±12%. Beside a hall a crown may shrink to 60% so it never reaches over the roof.

**Numbers (`tools/check_greens.py`):**
- 40,161 plants: lotus 13,147, reeds 7,568, bamboo clumps 4,447, pines 4,324, blossom 2,825, floating leaves 2,728, broadleaf 2,530, willows 1,451, flower beds 624, cypresses 261, topiary 255.
- Species grade: A 28,789, B 3,456, C 7,916. Extent grade: B 7,070 (a leaf or a survivor shows that side of the scene), C 33,091. Assumed (the fill) 6,508.
- 466 areas in 87 scenes: 209 groves, 103 specimen groups, 42 bamboo groves, 40 lotus ponds, 26 flower beds, 24 avenues, 21 reed beds, 1 hedge; nine are the fill.
- 86 rockeries: 32 shore rockwork (all reach the water), 27 rock hills, 24 standing stones, 3 rock screens; grade A 52, B 27, C 7; their place B 32, C 54; 3.25 m above the ground at the median, 6 m at most (typology).
- Clearances: no plant in a box or with its crown over one, none on a way, a wall or a bridge, none in a rockery; no land plant in water and no water plant on land.
- Ground: bases within 0.00 m of the walk surface (max), the ground under a trunk at most 0.39 m below its base (the trunk sinks 0.5 m); water plants within 0.005 m of their body's level.
- Files: `site/reconstruction/generated/greens_1860.bin` 0.56 MB, `site/reconstruction/data/greens_1860.json` 0.06 MB, `site/reconstruction/data/greens_1860.geojson` 2.52 MB: 3.14 MB.

**Cost** (`research/greens/greens_browser.json`, software WebGL, 1400 x 900, one page load): overview 402 ms with the planting off, 565 ms on (254 k far triangles, 111 tiles); 九洲清晏 from 220 m 310 → 384 ms (3,000 plants near); 曲院风荷 from 140 m 248 → 333 ms (7,800 near). The plants are baked into merged meshes per 200 m tile, a far level everywhere and a near level within 260 m: software WebGL drew the same triangles several times slower as instances.

## Rockeries

From the rows whose plant is a rock (石, 假山) and the 89 readings of `research/terrain/rockeries.csv` (Round 10): grouped by scene and kind. A standing stone stands in a court 4-12 m before the hall named; a rock screen runs behind the hall, as wide as its front (正大光明殿's 峭石壁立, S40); shore rockwork follows 16 m of the scene's shore, half in the water; a rock hill sits on the scene's highest hill. The base is the lowest ground or bed under the footprint less 0.3 m, so nothing floats and a shore rockery runs down into the water. Sizes are typology (C); the stones moved away give the only measured one (青莲朵, 145 x 228 x 123 cm, S1165).

## What is weak

- Every place is generated; 33,091 plants stand on C extents (Q218).
- Lotus at 曲院风荷 and 平湖秋月 follows the texts against the leaves (Q209).
- The commonest painted tree is unnamed (Q210); species sizes are defaults.
- With `assumed=0` the plants on generated hills are lowered by what the hill adds (11,799 plants), and the fill is hidden.
- Qichun Yuan's rows are of Jiaqing's time (Q215); the maze walls (Q211) and the tall tiers at 大水法 (Q212) are open.
- 39 rows found no land or water for their place (the scene's free land is all court, or the hall named has no box); 37 areas got no plant (no room once the earlier areas stood). Both lists are in `research/greens/greens_report.json`.
