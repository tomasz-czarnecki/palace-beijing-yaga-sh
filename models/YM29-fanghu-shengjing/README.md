# YM29 方壶胜境 Fanghu Shengjing: the towers on their terraces over the water, a detailed model (Round 24)

The tenth detailed model and the fourth of a Chinese compound: the scene near the north-east corner of the 圆明园 proper, on the inlet that opens south into 福海 (S02 p.93), as the leaf of 1744 paints it and S01 draws it. Nine two-storey towers stand in three ranges, each a five-bay middle block with a pair of side towers (S361's note, E1852). At the water stands the front range, whose upper floor bore the plaque 宜春殿 (S05). On the upper, brick-faced terrace (Malone) stand 哕鸾殿 and, behind it, 琼华楼. Galleries join the towers' upper floors. On the water stand three pavilions: 迎薰亭 at the end of the causeway, 集瑞亭 and 凝祥亭 on two cruciform terraces at the ends of the galleries. Built about 1738-1740 (S06, S02; Q25). Its halls were lost when the gardens were burned by British troops on Elgin's order on 18-19 October 1860 (S02 pp.187-188, on the gardens as a whole; Q176). Under the Republic most of its masonry was pulled down for building material (S02 p.218). The line of its bastions still stands in the water (P0383, P0787).

Generator: `fanghushengjing.py` (`uv run python models/YM29-fanghu-shengjing/fanghushengjing.py`, after `scripts/kit1860.py` has run once), on `scripts/hall_parts.py` (the hall kit in Python, Round 17) and `scripts/model_site.py`. Hand-edited sheet: `plan_readings.csv` (every line read on S01, in plan pixels). Writes `model.glb`, `params.json`, `keypoints.json`, `joints.json`, `summary.json`, `report.json`.

## Evidence

By part, in the order of authority the brief sets: the dossier (`research/scenes/YM29-fanghu-shengjing/`), the period plan and texts, the pictures, and the readings of others as reading aids only. Each part's own date is given.

- **The plan and the layout (B):** S01, re-read in Round 24 on 3x and 4x crops (`plan_readings.csv`). It gives:
  - the lower terrace's outline with its stepped bastions;
  - the upper terrace's walls and south face;
  - the three ranges of a five-cell middle block with two side blocks;
  - the links, and the two strips of cells down the court's sides;
  - the stair on the axis between the terraces;
  - the entry before the front range, and the flight from its jut;
  - the strips out to the two stepped crosses, the causeway and the square terrace with its flights;
  - the two three-cell gates astride the walls;
  - the rectangle behind 琼华楼.

  The frame's z runs along the axis S01 draws, 0.6° off the box F0164's bearing. The seven reads on the axis spread over 1.56 m.
- **The water (B):** the inlet the terraces stand in. On S01 it is the tracer's region R0018, classed land by default, so Round 10's ground made it dry land with trees. It is water since Round 24 (`research/plan/water_manual.json`, W0365, Q191). The ink band of S01's flights round the square terrace is joined to it. The leaf paints the terraces standing in the water (P0029). Its level is Round 10's rule for a body (42.76 m, C).
- **The names and the counts (A, B):**
  - S05 j82:12a-13a: 臨池樓宇為方壺勝境上下各五楹南建坊座二其北樓宇為噦鸞殿又北為瓊華樓, and the plaques (E1847, A);
  - the twenty gilt plaques of 1740 (S310 rec. 8298): 迎薰亭, 集瑞亭, 凝祥亭, 宜春殿, 锦绮楼, 翡翠楼, 哕鸾殿, 碧云楼, 紫霞楼, 琼华楼, 千祥阁, 万福阁, the archways' four, 蕊珠宫, 依仁殿, 履义殿, 蕊珠门;
  - S361's note: three five-bay towers, each with a pair of side towers; 2,235 Buddha images in the nine towers (E1852, B);
  - Malone: on the upper terrace two large and four smaller buildings, all of two storeys, with elevated walks joining their second storeys; three two-storey buildings on the lower terrace; a bridge and two piers to three small terraces, with marble balustrades and steps for the barge (S02 pp.92-93, E1850, B);
  - S258: every building has an upper floor except the three pavilions on the water; a pailou at the foot of the first stair (E1849, B).
- **The forms and colours (A for 1744):** the leaf P0029 (S08), read on 3x and 5x crops:
  - the front range: two storeys, red columns and red lattice on both, a balustraded balcony at the upper floor, a 歇山 roof with a yellow field and green trim 剪边;
  - its side towers: their gables turned to the water, yellow with green trim;
  - the entry: a lower front with a door in the middle, under the upper floor's white rail;
  - 哕鸾殿 and its side towers: 歇山, a purple-brown field with green trim, a skirt roof between the storeys;
  - 琼华楼: a double top eave, a yellow field with blue trim; its side towers purple-brown with green trim, also with two tiers;
  - 迎薰亭: double eaves, a yellow pyramid with a gilt finial;
  - the two side pavilions: 重檐 with cross ridges, gables on all four sides, blue with yellow trim;
  - white marble terraces with balustrades and many flights down to the water;
  - four dark bronze figures at the square terrace's corners;
  - the middle court grey-paved, with bronze vessels in a row and potted flowering trees.

  `research/scenes/halls.csv` holds the Round 7 readings, and Q175 the colours against Malone's 'golden tile'.
- **The bronzes (B for the subject):** 方壶胜境铜龙、凤立样底图, an elevation sheet of the bronze dragons and phoenixes (S310, E1856, title only).
- **Today (B):** the stepped stone bastions in the water (P0383, P0384, P0787, P0788: free photographs, 2012-2013). They match S01's line of the lower terrace's front.
- **The hall classes (C):** `scripts/hall_parts.py`, `research/typology/params.json` (storeyed_hall), the 举架 of S101. These give every height, every bay's width, the galleries' width, the brackets and the stair's steps.
- **Reading aids, not evidence:** the reconstructions by others listed in the dossier (R0035, R0117 and others) and the twin 排云殿-佛香阁 (T026). None was used for a size or a position.

## What the model draws, and on what

- **The lower terrace:** S01's outline with its bastions (B). White marble faces, a coping and flags (the leaf). A balustrade along the water edges, broken where the strips and the causeway meet it. Its top is 2.6 m above the water (C).
- **The upper terrace:** S01's outline (B). Brick faces (Malone, B). A balustrade along its south edge, broken at the head of the stair (the leaf). Its top is 3.0 m above the lower terrace (C). Behind 琼华楼 stands S01's rectangle as a terrace (C). The walls run on the west, east and north lines, red with yellow glazed coping (colour C), with a gate in the west and east walls at S01's gate cells (form C). A flight runs down the terrace's face outside each gate (C).
- **The stair on the axis:** from the front range's platform up to the upper terrace, 2.55 m, in 17 steps, in the 5.3 m S01 leaves there (S01's cells; steps C). The front range's middle hall is the way through: it has a door front and back.
- **宜春殿 (the front range's middle block):** S01's five cells, 20.6 x 10.6 m (B). Five bays (S05, A). Two storeys with a skirt roof and a balcony between (the leaf). A 1.2 m front porch (C). 歇山, yellow with green trim (the leaf). Heights C: platform 0.45 m, ground storey 3.6 m, upper storey 3.2 m.
- **The entry:** S01's block before the middle bays, 8.5 x 5.0 m (B). One storey of three bays (C), its flat roof the upper floor's balcony with a rail (the leaf). The plaque 方壶胜境 hangs over its door (S05 額為皇上御書; board C). A flight runs down from the jut to the causeway (S01).
- **锦绮楼 and 翡翠楼:** S01's blocks (B). Two storeys, 歇山 with the gables to the water, yellow with green trim (the leaf). Which name goes with which tower is C.
- **哕鸾殿, 碧云楼, 紫霞楼:** S01's blocks (B). Two storeys, 歇山, purple-brown with green trim (the leaf). Flights to the court.
- **琼华楼, 千祥阁, 万福阁:** S01's blocks (B). Two storeys under a double top eave (the leaf): yellow with blue trim in the middle, purple-brown with green trim at the sides.
- **The galleries:** two-storey galleries 4.0 m wide in 3.2 m bays. They join each middle block to its side towers, and run down the court's sides from the rear side towers to the middle ones (S01, Malone; width and roofs C, green tile C). Single-storey galleries stand on the strips out to the cross terraces (S01; single storey C).
- **The water terraces:** two stepped crosses about 10 m across, 1.9 m above the water (S01; height C). On them stand 集瑞亭 and 凝祥亭: square, open, red columns, a lower eave and a cross-ridge 十字脊 roof, blue with yellow trim (the leaf; size C). A flight runs down from each strip to its cross.
- **The causeway and its archways:** 5.8 m wide and 1.9 m above the water (S01; height C), with balustrades. The two archways 坊座 stand at its two ends (S05: two, south of the front building, A). Their form is C: four red posts on stone drums with braces, three yellow roofs with green trim, plaques front and back (the leaf's small yellow roof on red posts; S258).
- **The square terrace:** S01's 18.6 x 16.2 m. A balustrade, a flight on each side, and three flights to the water for the barge (S01, Malone). 迎薰亭 stands on it: 6.6 m square, three bays a side, open, double eaves, a yellow pyramid with a gilt finial (the leaf; size C). Four bronzes stand at the corners, two dragons and two phoenixes, on stone stands (E1856; their form, size and places C).
- **The courts:** flagged (the leaf; S258's octagonal paving is not drawn). Four bronze vessels on stands and four potted flowering trees before 哕鸾殿 (the leaf; number and places C).

## Match check

The only period picture of the scene is the album leaf of 1744 (P0029). It is a painting, not a perspective. The 1745 woodcut P0068 and its re-cut P0260 repeat its layout; the gouache P0114 recolours it (Q128). On 3x and 5x crops of the 1920 px copy we read 28 points (`research/scenes/YM29-fanghu-shengjing/plate_keypoints.csv`):
- 迎薰亭's finial, eave tip and front columns;
- the entry's front columns;
- the front side towers' gable apexes and eave tips, and 宜春殿's eave tips;
- the water pavilions' tops and eave tips;
- the ridge ends and eave tips of 哕鸾殿, 琼华楼 and two of their side towers.

One free pinhole camera (`tools/plate_overlay.py fit --object YM29 --sheets research/scenes/YM29-fanghu-shengjing`; the numbers of the final run are in the round's entry, `docs/rounds/README.md`): **2.97 m rms at the object (13.0 px; median 2.42 m, max 5.78 m) on 28 points**. Where they disagree:
- **The east water pavilion:** the leaf paints it 23-25 px (about 5.5 m) nearer the axis than S01 places it, while the west one lies on the leaf's.
- **迎薰亭:** the leaf paints its eaves 9-22 px higher (taller columns, as the album paints halls 1.5-1.9 times too tall elsewhere, Q198).
- **哕鸾殿:** its ridge is 20 px shorter on the leaf at the east end.

Nothing was tuned to hide these (Q281, Q282). The overlay is `screenshots/r24/overlay_P0029_YM29_all_*`.

The ruin photographs show only the bastions at the waterline. Their tops are cut down and today's water level is not 1860's, so they test the plan's line, not a height. We did not read them for a fit: no bastion can be tied to a vertex of S01 with confidence (Q283).

## Iteration log

- **v0 (before the model):** the inlet was land in Round 10's ground (R0018 classed land by default). The kit's boxes stood among trees on grass, and the boat routes YMF-043 and YMF-044 crossed 90 m of dry land (Q191). The inlet became manual water W0365.
- **v1:** Round 10's land poked out beside the square terrace: the ink band of S01's flights is no region, so it was land. Fixed in the water layer, not by hiding it in the model.
- **v2:** the first reading of the gap between the upper terrace's face and the front range's back took the face's most southerly corner: 4.2 m, too short for a 3 m flight, so the stair was cut into the terrace. S01's face runs 2.6° off the axis frame (3.6 m over the terrace's width), and at the axis the gap is 5.3 m. The flight (17 steps, 2.55 m) stands in it as S01's cells draw it, from the face to the front range's platform, and the notch was dropped. The front range gained a back door: its middle hall is the way through. The same corner value had also filtered out the upper terrace's south balustrade (v2 and v3 shots); it is now drawn along the face and broken at the stair's head.
- **v3:** the cruciform terraces had diagonal edges, from a wrong vertex order; they are now the union of a square and two arms. They were also cut to S01's size (about 10 m across, from 12.7 m). Two cameras of the review set were re-aimed: one stood inside the hill behind the upper terrace.
- **The fit:** the first fit collapsed its focal length from the level start. A seen-from-far painting whose points lie off the sheet's middle needs another start. `tools/plate_overlay.py` now also starts from the prior's place aimed at the points' middle, with the focal length from their spread. This start only counts where it lowers the cost.

## Joints and ways

Measured by `tools/check_models.py` and `report.json` (the final numbers are in the round's entry):
- **Joints with the ground:** every terrace's corners on the ground of Round 10 or the lake's bed, and the walls' and gates' feet.
- **Decks:** the lower and upper terraces, the strips, the causeway and the three water terraces. Halls, flights and paving stand on them; the ways that cross them are laid on them.
- **Entries:** at the feet and heads of every flight, both sides of the two gates, and the entry's door.
- **Footprints:** every terrace, hall, wall, archway post and bronze stand.
- **Clear areas:** the two flagged courts.

## Where the model and the pictures disagree

See `research/questions.md` Q281-Q286. In short:
- Q281: the east water pavilion's place, on the leaf against S01.
- Q282: the leaf's heights.
- Q283: the ruin photographs.
- Q284: the terraces' heights.
- Q285: which side tower bore which plaque, and the archways' places.
- Q286: S01's rear rectangle.
