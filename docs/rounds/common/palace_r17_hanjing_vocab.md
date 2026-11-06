# Round 17: key points on the ruin photographs of 含经堂 (CC02)

For the readers of `palace_r17_hanjing`. The model `models/CC02-hanjing-tang/` draws the compound of 1860; the photographs show the excavated and consolidated ruin (2007, 2013). What both share is the **platforms** (their outlines and their heights over the courts), the **flights** up them, the compound's **terrace** over the forecourt with its retaining wall and central flight, the **screen wall's** base and the **archways'** footings. Read only those, and only where you can tell which platform it is.

## The plan
`/opt/data/cache/scratch/palace_r17_hanjing/diagram.png`: the model's platforms (red, by name) and the terrace's points (blue), in the model's frame: x east (right), z south (down), metres, north up. The axis runs up the middle (x about 0): forecourt (z 45 to 115, the three archways `pailou_W`, `pailou_S`, `pailou_E`), the terrace's edge with the gate's yard (`terr_*`), the gate (`gate`), the 含经堂 court with its screen (`screen`), the side halls (`peidian_W`, `peidian_E`) and the two ⊐-shaped ranges (`fanxiang_*` west = 梵香楼, `xiazhu_*` east = 霞翥楼), 含经堂 (`hanjingtang`), the rockery court, 淳化轩's terrace (`chx_terrace`) and 淳化轩 (`chunhuaxuan`), 蕴真斋 with its front terrace and back porch (`yunzhenzhai_*`), the north gate. The west court holds 三友轩 (`sanyouxuan`); the east court the stage (`stage`) and the halls named `side_F....` by their box.

The plan is a reading of a sketch plan to about 10 m; the ruin is the truth for the outlines. If a photograph shows a platform that the plan does not have, or puts it elsewhere, say so in the note column.

## Names
- `<platform>_pl_foot_<SW|SE|NW|NE>`: a platform's corner where it meets the court (its foot), by compass on the diagram (N up).
- `<platform>_pl_top_<SW|SE|NW|NE>`: the same corner at the platform's top edge.
- `<platform>_fl_<front|back|left|right>_<L|R>_<foot|top>`: the outer edges of a flight (the side slabs 垂带 included) at its foot and at its top, L and R as you see them standing in front of the flight looking at the platform. `front` is the platform's main face (south for most; `peidian_W` faces east, `peidian_E` west, `fanxiang_range` east, `xiazhu_range` west, `*_wingN` south, `*_wingS` north).
- `chx_terrace_fl_W_<L|R>_<foot|top>`, `chx_terrace_fl_E_...`: 淳化轩's terrace has two flights at the ends of its south face (W and E).
- The terrace over the forecourt: `terr_yard_SW_<top|foot>`, `terr_yard_SE_...` (the front corners of the gate's yard, which juts south), `terr_yard_NW_...`, `terr_yard_NE_...` (where the yard's sides meet the curved edge), `terr_W_end_...`, `terr_E_end_...` (where the curved edge meets the forecourt's side walls); `gate_flight_<L|R>_<foot|top>` the central flight down from the yard.
- `screen_foot_<W|E>`, `screen_base_top_<W|E>` (the top of its stone base, about 0.7 m), `screen_top_<W|E>`: the screen wall's south face, its ends.
- `pailou_<W|S|E>_base_<SW|SE|NW|NE>`: an archway's footing's corners on the ground.

## What to write
Two CSV files, your own (the coordinator merges them):
1. `/opt/data/cache/scratch/palace_r17_hanjing_kp_<reader>.csv` with the header `plate,photo_id,object,point,x,y,sure,use,note`: `plate` empty; `object` CC02; `x`, `y` pixels of the repo copy `research/photos/images/<photo_id>.jpg` (origin top left); `sure` 1 (within 3 px), 2 (within 8 px), 3 (about 15 px); `use` empty, or `skip: <reason>` for a point you read but believe the display changed (re-built, raised); `note` what you see.
2. `/opt/data/cache/scratch/palace_r17_hanjing_vp_<reader>.csv` with the header `photo_id,x_local,z_local,bearing_diagram_deg,dist_m,err_m,eye_m,hfov_deg,basis`: where the camera stood on the diagram (model frame metres), the direction it looks (0 = up the diagram, 90 = right), how far from what it shows, the radius you trust (m), the eye height over the ground there (1.6 standing), the lens's horizontal field of view if you can judge it (else empty), and one sentence why.

At least six points a photograph, spread in depth and across the picture, and at least three `foot` points (they carry the camera). Make gridded or zoomed crops with `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh/.venv/bin/python` (PIL) into `/opt/data/cache/scratch/palace_r17_hanjing_rd_<reader>/`, never into the repo. Do not write in the repo.

The photographs' captions on Commons and Flickr (research/photos/catalog.csv, `why` and `notes`): P0402 含经堂以及影壁遗址 (the court of 含经堂 and the screen's remains); P0403 含经堂遗址宫门前以及南牌楼遗址 (before the gate, the south archway's remains); P0404 含经堂淳化轩遗址 (淳化轩, from the south-west, the rockery before it); P0405 含经堂蕴真斋遗址（从北向南拍摄） (蕴真斋, taken from the north looking south); P0406 三友轩遗址以及庭院中残存的叠石假山 (三友轩 and its rockery, west of 淳化轩); P0408 含经堂西侧梵香楼遗址 (梵香楼, the west range); P0410 位于淳化轩东侧的扮戏房以及大戏楼遗址 (the dressing room and the stage east of 淳化轩); P0505 含经堂遗址 (geotag 40.006913 N, 116.307557 E, maybe a place tag); P0815, P0816, P0817 (2007, while the display was being laid: the long retaining wall with its central flight, the platforms round a sunk court).
