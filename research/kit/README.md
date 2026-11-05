# The hall kit and the stone kit (Round 11)

Every box of `site/reconstruction/data/halls_1860.geojson` is drawn in the 3D view from numbers, not as a plain box: a Qing hall by the **hall kit** (`site/reconstruction/kit3d.js`), a European building of the Xiyang Lou by the **stone kit** (`site/reconstruction/stonekit3d.js`). The numbers come from `scripts/kit1860.py`, written to `site/reconstruction/data/kit_1860.json`. The browser adds no number of its own, only the shapes of the parts and the colours of the view. There are no textures and no model files.

The kit draws inside the box. The platform is the box's footprint. The columns stand the platform's edge (下出) inside it. The roof reaches the overhang (上出) beyond the columns. The heights are the box's (`boxes1860.py`). The kit never moves a box or changes its footprint, heights or class. The box stays the click target, and the panel stays the box's page.

## Where each hall's form comes from

| `src` | What | Halls | Panel |
|---|---|---|---|
| `class` | the defaults of its hall class (`research/typology/params.json`), assumed, C | 1476 | "drawn from the typology of its hall class, not from a picture of this hall" |
| `dossier` | its own figures in a dossier (`research/scenes/*/dimensions.json`, `research/xiyanglou/*/dimensions.json`: column, platform, ridge, bays, porch, 下出), or its own reading in `research/scenes/halls.csv` (roof form, tiles), each with method and grade (`fig`). The other numbers come from the class | 154 (75 Qing halls, 79 Xiyang Lou boxes) | its figures listed |
| `stated` | a size a source states (`by_name`) | 4 | |
| `model` | a detailed model in `models/<ID>-<slug>/summary.json`: the kit draws nothing for it | 0 (none yet) | |

Counts are from `research/kit/kit_check.json`. The Xiyang Lou's façades are the kit's reading of the plates, so they are `assumed` and C even where the box is surveyed.

## What the hall kit draws

- **Platform 台基** of stone with a coping. **Steps 踏跺** on the front always (gates also on the back), and on every side a way of Round 9 reaches (`paths_1860`, `from_at`, `to_at`): at the middle bay, or where the way arrives if that lies further out (`so`). The rise is 0.15 m. The flight is never longer than the overhang. A side whose ground is water gets no steps. The blocks reach the lowest ground under them. **Marble balustrade** on the great halls (`grand_hall`, `temple_hall`) and on any platform of 0.95 m or more.
- **Body:** red-brown lacquer columns 檐柱 on the bay lines. The walls stand behind porches (`pf`, `pb`, `ps`: front, back, all round; 前后廊 at 惠如春 and 松风阁, S111; 周围廊 at 正大光明殿, S02). Doors 隔扇 go in the middle bay, windows 槛窗 over a sill wall 槛墙 in the others, and a transom 横披 above. The panes are set back 0.12 m behind their frames, with reveals and lattice bars. The rear has windows, with a door in the middle on half of the main and grand halls (seeded, C). Gable walls 硬山 are brick with a plaster panel; the other sides have windows. Gates 门殿 get plank doors and red plaster in the side bays. Pavilions are open, with a bench 坐凳 and a hanging fascia 倒挂楣子. A 牌楼 gets posts with stone clamps, beams and a small roof over each bay.
- **Bay rhythm:** the count from `buildings.csv`, else the plan's bays, else from the class's bay. The middle bay is widest. Widths come from the dossier (正大光明殿: 5.17 / 4.83 / 4.32 m) or the class, scaled to the box.
- **Eave band:** a painted beam 额枋 on every hall. On 大式 halls (`grand_hall`, `temple_hall`, `gate_hall`, `tower`) bracket sets 斗拱 are shown as a stepped coloured band (S101; 澹怀堂 and 长春园宫门 have them on grey rolled roofs, S112), with no bracket geometry. Every band stays under the roof's own profile.
- **Roofs by class from the data** (`roof`, `rolled`, `double` of the box): 庑殿 hip (`wd`), 歇山 hip-and-gable (`xs`, with a red 山花 gable), 硬山 flush gable (`ys`, the roof ending at the gable wall), 悬山 overhanging gable (`xu`, with barge boards), 攒尖 pyramid (`cj`, 4, 6 or 8 sides), 卷棚 rolled ridge (`rl`, an arc over the two ridge purlins), 重檐 double eaves (`db`), 勾连搭 parallel rolls. The profile is concave, taken from the 举架 steps of the class (`ju`; S101). Hipped forms have corner lift 起翘. A sharp ridge gets a 正脊 with end blocks; the hips and verges get raised strips. Tiles are a flat colour, with an edge colour 剪边 where a leaf shows one (`te`). An unread gable on a `small_house` is 硬山 or 悬山 by seed, 60 / 40 (C: `params.json` gives "卷棚硬山 or 悬山").
- **Courts:** paving between the halls of each compound (`generated/courts.bin`, 17.3 ha, 58,582 triangles), closed over gaps up to 22 m, with a 1.5 m apron round each hall (S104: drip courses), less water, hills and the halls, cut to the compound's outline. Assumed, C: no source draws a court's paving.
- **Galleries of Round 9** (`paths_1860`, kind `gallery`, not inside a box): posts, a bench on one side, a beam and a rolled 悬山 roof per straight run (`params.json` `gallery`). The plain slab roofs of `paths3d.js` show only when the kit is off.
- **Variation** only on `class` halls, seeded by the box id: three lacquer and three wall shades, the roof's curve (±15 %) and corner lift (±20 %), 硬山 or 悬山, the rear door. A documented hall keeps the first shade and the plain curve.

## What the stone kit draws

A rusticated ground storey and pilasters at the bays, with base and capital. Arched openings with a marble surround and keystone. An entablature at each storey, a balustrade at the roof's foot, and a pediment over the middle of the main fronts. Glazed roofs of Chinese form: 谐奇趣 yellow-ochre with an orange-red edge (S700, `research/xiyanglou/materials.csv`), 方外观 blue (S06, Q69), the others green with a violet edge by the strip's rule in `materials.csv` (C). It also draws the curved double stairs at 海晏堂's west front, 远瀛观's terrace and 方外观's terrace, fitted inside their boxes; the arcades of 谐奇趣's corridors; the octagonal music pavilions; the 13-tier fountain towers of 大水法 (S109); the niche of 大水法 with a stepped cascade; basins and pools with a jet; the maze's brick walls with a strip of trimmed pines (S02 p.145); and screens with framed panels. Straight flights stand where a way reaches a European block. Storeys, bays and stairs come from the part as `xiyanglou/boxes.csv` names it, bay widths from the dossiers' `bay_width`, else 4.3 m (海晏堂, plate 10).

## Levels of detail and cost

The gardens are cut into 180 m tiles (124). Each tile has a far level, built at load: platform, a body block and the roof's shape, a median 76 triangles a hall. It also has a near level: every part, a median 740 triangles a hall. The near level is built only when the camera comes within 420 m plus most of a tile (`kit.update` in `3d.js`). A tile far away is dropped again once more than 48 near tiles are built. All near levels together would hold 1.68 M triangles; the view holds 0.67-1.3 M at a time. The colours are bytes, and there are no normals: the material shades flat from the screen.

Measured in software WebGL, 1400 x 900, median of 12 frames, before and after in one session (`research/kit/kit_browser.json`):

| View | Before (Round 10, boxes) | After, boxes (`kit=0`) | After, kit |
|---|---|---|---|
| overview | 325 ms, 458 k triangles drawn | 305 ms, 458 k | 325 ms, 575 k |
| 同乐园 from 150 m | 165 ms, 458 k | 150 ms, 458 k | 272 ms, 548 k |
| one hall from 40 m | 174 ms, 458 k | 178 ms, 458 k | 280 ms, 586 k |

About 400 k of each figure is the ground. Frame time in software WebGL varies by about ±25 % between runs on this shared machine.

## Checks: `tools/check_kit.py`

It fails on:
- a box with no entry;
- a hall the browser did not draw;
- a roof class, rolled ridge or double eave other than the box's;
- a hall beyond its box by more than its overhang (body or roof);
- steps beyond the overhang (1.6 m on a European block);
- a step foot off the ground by more than 0.3 m;
- an A or B way ending at a box side with no flight within 1.5 m and a drop over 0.3 m;
- a browser report older than the spec.

`--browser` measures the view first; `--before-url` also measures an older export. Round 11:
- all 1634 boxes are drawn;
- beyond the box: median 0.19 m, max 0.66 m (a hexagonal roof's corner), none over its overhang;
- 2385 step flights, feet on the ground within 0.01 m;
- of 1351 way ends at a box side, 1333 meet a flight within 1.5 m (gap median 0 m, max 0.1 m), 11 end at a pool, a wall, a court or a hall on a terrace, and 7 meet a side within 0.14 m of the platform's top;
- before Round 11 none had steps: the drop from platform to way was 0.41 m median, up to 2.13 m.

## Files

| File | What |
|---|---|
| `site/reconstruction/data/kit_1860.json` | `halls` (one entry per box id), `gallery`, `courts`, `note` (the keys), `credit` |
| `site/reconstruction/generated/courts.bin` | the courts: int16 triples, x and z in 0.2 m, y in cm above the datum, three per triangle |
| `research/kit/kit_check.json` | what `tools/check_kit.py` measured: `counts`, `drawn`, `beyond_box_m`, `joints`, `cost`, `files_mb`, `fails` |
| `research/kit/kit_browser.json` | the last browser run: `spec_hash`, `measured_utc`, `after` and `before` views (frame times, triangles drawn and in memory), `load_s`, `errors` |
| `research/kit/kit_report.json` | the kit's own report: per box the roof drawn, triangles near and far, how far it reaches beyond the box (`out`: body, roof, steps), its step flights (`steps`: side, x, z, foot, top, run, width) |

## What is weak

- Almost every form is the class's: 1476 of 1634 boxes. The kit makes the gardens read as Qing halls, not as these halls. The panel says so.
- Window patterns, door types and the lacquer colour are not read from any picture of this garden. Glass or paper is not settled (Q205). Red is the rule of the imperial palaces, and green-lacquered columns occur in gardens (Q204).
- 硬山 or 悬山 on an unread gable, and the rear door, are seeded.
- The stone kit gives every European building the same vocabulary. The plates show each front differently: 谐奇趣 gets its own model next.
- The courts are a closing of the halls' outlines, not the walls of the compounds, which are not traced.
