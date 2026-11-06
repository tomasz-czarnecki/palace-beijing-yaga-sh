# YM03 九洲清晏 Jiuzhou Qingyan: the central axis of the emperor's residence, a detailed model (Round 18)

The eighth detailed model and the second of a Chinese compound: the central axis of 九洲清晏, the largest of the nine islands round the 后湖 Back Lake and the emperor's residence from Yongzheng to Xianfeng, as it stood from its rebuilding of 1837 until October 1860, when French and British troops looted the gardens and British troops burned them on Elgin's order (S02 pp.179-188). The three axis halls burned on 丙申九月二十六日 (1836) and Daoguang rebuilt them by 1837 'to the old form' (E1131, E1134). No picture of the rebuilt halls survives; the site is a lawn with loose stones today (P0365) and no dig report has been published (Q119).

Generator: `jiuzhouqingyan.py` (`uv run python models/YM03-jiuzhou-qingyan/jiuzhouqingyan.py`), on `scripts/hall_parts.py` (the hall kit in Python, Round 17) and `scripts/model_site.py`. Hand-edited sheet: `plan_readings.csv` (every line read on S01, in plan pixels). Writes `model.glb`, `params.json`, `keypoints.json`, `joints.json`, `summary.json`, `report.json`, and the three bridge models beside this folder (`models/YM03-21-ruyi-qiao/`, `YM03-22-nanda-qiao/`, `YM03-23-zongting-qiao/`).

## Evidence

By part, in the order of authority the brief sets (dossier, period plans and texts, the pictures, the readings of others as reading aids only). Dates: the model's state is 1837-1860; each part's own date is given.

- **The plan and the layout (B, 1873 or later):** S01, re-read in Round 18 on 1.6, 2.4 and 5 times enlarged crops (`plan_readings.csv`): 圆明园殿 and its two-cell ear rooms, the front yard's two lines to the shore, the first court's two marks, 奉三无私殿 drawn wall to wall and its front terrace, the axis's two walls, 九洲清晏殿, the link and 同道堂 to its west, the front and back shores with Round 9's landings on them. S01's labels on this island are those of the Tongzhi design of 1873-74 (Q36, Q120, Q121): the east of the axis (七间殿, the jade-disc pond) is that design and is not modelled; the axis halls kept their names.
- **圆明园殿 (A, 1855):** the yellow slip of NLC 样007-9-1 (1855.3; the same figures on the 1837 sheet), as transcribed on mhymy record 11195 (S310): five bays, 明间 13 尺 and four 次间 12 尺 (4.16 + 4 x 3.84 m), 进深 22 尺 between the 金柱 lines with porches of 6 尺 front and back (7.04 + 2 x 1.92 m), 檐柱 12 尺 (3.84 m), 台明 2.2 尺 (0.70 m), 下檐出 2.9 尺 (0.93 m). Record 11195 also: the doors moved to the 金柱 line in 1837 and 墀头 on the gables, from which it infers a 硬山 roof after the fire (B). The 1744 leaf draws a 歇山 (Q100, Q252). Kangxi's plaque 圆明园 (S05 j80:1b, 21a; record 7105).
- **奉三无私殿:** seven bays (S05 j80:20b, A for the 1780s), porches front and back (record 7271, B); S01 draws it wall to wall (23.3 m with its edges). Every width, the depth and the heights are C (the Yangshi Lei sheets E1161-E1171 hold them: wishlist).
- **九洲清晏殿:** five bays with porches front and back and a three-bay rear porch 抱厦 added in 咸丰五年 (1855) (record 7237, 10881: A); S05 gives seven bays for the 1780s (Q101, Q163). Widths fitted to S01's drawn 18.2 m, depth and heights C. Plaques 九洲清晏 (Yongzheng) and 蔚然深秀 (S05 j80:21a, 23a).
- **同道堂:** joined to the hall's west in the approved rebuilding of 1837 (样010-3, E1169); at S01's boxes F0569 and F0022, the class's form (C).
- **The courts:** the Tongzhi survey 样006-3 = 样062-24 (1873-74, quoted on mhymy record 11901; B for 1860): 圆明园殿 to 奉三无私 33.92 m, 奉三无私 to 九洲清晏 18.27 m, both 25.98 m wide. S01 gives 34.5 m, 22.5 m and 22.6 m (between the eave columns and between the walls' inner faces): the plan is kept (Q250).
- **Colours, roofs and galleries (A for 1744):** the album leaf P0003 (S08, free): grey tile throughout, red columns, green-blue lattice and beams, white walls with a row of pierced windows on the covered galleries between the axis halls, pink-flowering trees in the courts, a timber bridge with red railings on the island's west side and one at its south-east. The 1745 woodcut P0089 (S76): rolled ridges with curved ends; an open verandah on the front hall.
- **The setting:** Malone's caption of the 1744 woodcut (S02 p.78, B): reeds and rocks at the water's edge before 圆明园殿. Round 9's landings YMC-023 (front) and YMC-031 (back); Round 10's ground (the island at 2.07-2.29 m, the 前湖 at 0.80 m and the 后湖 at 0.54 m above the datum's water).
- **Today (B):** P0365 (the 九洲清晏殿 site, a low mound by the back lake), P0367 (南大桥 rebuilt on dressed-stone abutments), P0368 (棕亭桥 rebuilt as a pavilion bridge), P0793 (如意桥 rebuilt on its surviving abutments; no local copy).
- **The hall classes (C):** `scripts/hall_parts.py`, `research/typology/params.json`, the 举架 of S101; the bands, brackets, doors and windows, the ear rooms, the gates, the vessels.
- **Reading aids, not evidence:** the Tsinghua reconstructions (R0037, R0038, R0046), the Tongzhi card models of 九洲清晏殿 and 天地一家春 (R0290, R0291, Q104), the twin 烟波致爽殿 (T007): not used for any size or position.

## What the model draws, and on what

- **The front yard:** paving from 圆明园殿 to the 前湖 between two low white walls (S01; height C); a dressed-stone landing with steps to the water at YMC-023 (C); rock piles at the water's edge either side (S02 p.78; places C).
- **圆明园殿:** the 1855 slip's bays, section, column and platform (A); flights front and back; open porches with the doors on the 金柱 line (B); rolled 硬山 with 墀头 gable walls (B); the plaque on the front eave (A; board C). Ear rooms at both ends (S01, C).
- **The first court:** paving and a raised axis way (C); covered galleries along both walls with their pierced windows (P0003; where they run C); a gate in each side wall (the leaf shows one east of the front hall; both C); two bronze vessels on stands at S01's two marks (C); two flowering trees (the leaf; places C).
- **奉三无私殿:** seven bays wall to wall, porches front and back, rolled 歇山 grey (P0003), the front terrace as S01 draws it (0.6 m, C), a balustrade; doors front and back in the middle three bays.
- **The second court:** paving, the axis way, galleries along the walls turning to the hall's porch ends (C), two trees.
- **九洲清晏殿:** five bays with porches, rolled 歇山, the island's largest roof (P0003); the 1855 rear porch of three bays with its own rolled roof joined to the hall's back slope (A; form C); a flight down from the porch towards the 后湖.
- **The west annex:** the link and 同道堂 at their boxes (E1169, S01; C).
- **The back:** a paved way to a dressed-stone landing on the 后湖 at YMC-031 (C).
- **The walls:** white plaster with grey coping (P0003; height 3.2 m C), on S01's lines, from 圆明园殿's back corners to the line of 九洲清晏殿's back.
- **The bridges (their own models):** 南大桥 YM03-22 and 如意桥 YM03-21 with dressed-stone abutments (P0367, P0793, B) and timber decks with red railings (P0003, A for 1744), 棕亭桥 YM03-23 with a pavilion on it (the name and P0368; C). Decks at Round 10's levels, so walking and the ways stay on them. The view leaves out their plain decks (`models.json` `bridges`).

## Match check

The only period picture of the axis is the album leaf of 1744 (P0003), a painting, not a perspective: 15 points read (`research/scenes/YM03-jiuzhou-qingyan/plate_keypoints.csv`): eave tips, ridge ends and column feet of the three halls, 圆明园殿's ridge ends skipped (the leaf's 歇山 against the model's 硬山 of 1837, a change of state). A free pinhole camera, `tools/plate_overlay.py fit --sheets research/scenes/YM03-jiuzhou-qingyan`: **3.79 m rms at the object (median 3.01 m, max 7.51 m) on 13 points.** It fits 九洲清晏殿's west half and its feet to 0.7-1.7 m and 奉三无私殿's west eave and feet to 1.7 m; it misses the east ends of both (4.5-7.5 m): the leaf paints 奉三无私殿 narrower than the model (85 px against 九洲清晏殿's 108 px) and 九洲清晏殿 as the widest hall of the axis, as the seven bays of S05 (1780s) would make it, where the model follows the five bays of 1855 (record 7237) and S01's 18 m. The leaf is the older state and a painting; the model is not tuned to it (Q251). The 1745 woodcut P0089 is too schematic and its trees hide the axis (dossier); the ruin photographs show no outline of a hall (P0365, P0364, P0451); none was fitted.

## Iteration log

- **v1:** the walls at the Tongzhi survey's court width (25.98 m between their inner faces), 奉三无私殿 26.2 m (the box F0019), galleries 2.4 m wide, the bridges in the model. On the shots the walls cut the halls S01 draws west and east of the courts (the kit's F1142, B0908, B0909 and the east block) by up to 1.6 m: S01 draws the walls 22.6 m apart and 奉三无私殿 wall to wall. 18,514 triangles.
- **v2:** the walls on S01's lines, 奉三无私殿 23.3 m (seven bays of 2.88-3.52 m, C), galleries 2.0 m, ear rooms to S01's outer ends; the court-1 camera moved out of 圆明园殿. Key points: the 歇山 ridge ends first defined with the 庑殿 formula (too short); fixed to the roof the kit draws (the hip steps in 0.4 of the slope). The leaf's fit first ran on two misread points (奉三无私殿's and 圆明园殿's east ends on their neighbours: 2.97 m and then 2.55 m rms); re-read on the overlay of the fitted points: 3.79 m.
- **v3 (final):** the panel's small view framed the whole island (the bridges 60-110 m out): each named bridge is now its own small model, the unnamed bridge to 来青亭 (BR007) back to Round 10's deck; the 1855 rear porch's roof lifted (v2 drew its ridge 0.4 m above its eave). 15,798 triangles (4,782 fill), 0.51 MB, 0.12 MB compressed.

## Joints and ways

- 72 ground joints (platform corners, wall and gallery feet, gate piers, vessel stands, quay feet): highest 0.07 m above the ground, deepest 0.33 m into it (`tools/check_models.py`).
- 14 entries (the flights' feet, the gates both sides, the landings' tops). Before `scripts/paths1860.py` re-snapped them, eight ways of Round 9 ended 0.92-8.90 m from the model's doors; after, 8 ways at the model's boxes, 0 off.
- 25 footprints (platforms, walls, galleries, vessels) and 4 `clear` areas (the two courts, the front yard, the back way): the planting keeps off them.

## Where the model and the pictures disagree

See `research/questions.md` Q250-Q255. In short: the court widths and the second court's depth of the Tongzhi survey against S01 (Q250); the leaf's widths against the 1855 bays (Q251); 圆明园殿's roof after 1837 (Q252, with Q100); which halls of the leaf are the axis (Q253); where the galleries ran (Q254); what stood east of 九洲清晏殿 in 1860, where the kit draws S01's Tongzhi 七间殿 (Q255).
