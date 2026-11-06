# Homepage picture slots (AI renders to come)

The homepage (`site/index.html`, and `site/zh/index.html` with the same slots) shows a designed placeholder, `figure.ph`, wherever an AI render will go. Each placeholder names its slot (`data-slot`), its aspect ratio (`data-aspect`) and carries the alt text the render will get (`data-alt`).

Note: this file sits under `site/`, so a host serving `site/` would serve it too. It holds no private information; move it to `docs/` if that matters.

## How to put a render in place

1. Export the render as WebP, named after its slot: `site/assets/gallery/<slot>.webp` (for example `site/assets/gallery/home-gate-morning.webp`). Keep each file under 400 KB; if it is heavier at the size below, export it narrower.
2. Add the slot's name to `ready` in `site/assets/gallery/manifest.json`:
   `{ "ready": ["home-gate-morning"] }`
3. Done. `site/main.js` reads the manifest, puts the picture in the frame (lazy-loaded), adds the "AI visualisation" label on the picture (Chinese page: "AI 图像"), turns the caption's "Picture to come" into "AI visualisation", and opens it in the lightbox on click. Both language pages pick it up.

Without the manifest entry the placeholder stays, even if the file exists. A single figure can also be switched on by hand with `data-ready="1"` on its `figure.ph`.

Every render must carry the AI label. The component adds it by itself; do not remove it, and do not put a render anywhere on the site without it.

The drafts named below are in `/opt/data/workspace/higgsfield_output/palace_life/`. They are drafts: they stay out of the site until Tomasz picks them. The model screenshots they started from are in `refs/`, `refs_a/`, `refs_v/` and `refs_x/` there.

Sizes are twice the largest size the page shows each slot at (the gallery is at most 1440 px wide, less 48 px margins each side).

## In "A day in the gardens"

- `home-gate-morning`: file `home-gate-morning.webp`, 16:9, render at 2688 × 1512 (export about 2400 × 1350 if that stays under 400 KB). Full width. Scene: the approach from 大宫门 Da Gongmen across the inner court to 正大光明 Zhengda Guangming, from the Round 19 model. Camera and mood: at eye height on the axis inside the gate, looking north, early morning light low from the east, a few officials, calm. Closest drafts: `gate_1.jpg`, `gate_2.jpg` (16:9); `gate_v_1.jpg`, `gate_v_2.jpg` are vertical.
- `home-fuhai-dawn`: file `home-fuhai-dawn.webp`, 4:5, render at 1100 × 1375. Narrow, left of a row. Scene: 福海 Fuhai with 蓬岛瑶台 Pengdao Yaotai on its islets. Camera and mood: from the west shore a little above the water, mist lying on the lake at dawn, pale light, still water. Closest drafts: `fuhai_v_1.jpg`, `fuhai_v_2.jpg` (9:16, crop to 4:5); `fuhai_1.jpg`, `fuhai_2.jpg` (16:9).
- `home-haiyantang-afternoon`: file `home-haiyantang-afternoon.webp`, 16:9, render at 1600 × 900. Wide, right of a row. Scene: the west front of 海晏堂 Haiyan Tang with its double stair and the basin of the water clock, from the Round 14 model. Camera and mood: standing in the court looking east at the front, low afternoon sun from the west, long shadows. Keep the twelve seated figures plain and in the background: no close-up, nothing playful. Closest drafts: `haiyan_1.jpg`, `haiyan_2.jpg` (16:9); `haiyan_v_1.jpg`, `haiyan_v_2.jpg` vertical.
- `home-dashuifa-playing`: file `home-dashuifa-playing.webp`, 16:9, render at 1600 × 900. Wide, left of a row. Scene: 大水法 Dashuifa, the Great Fountain, with the niche, the water steps and the two towers of jets playing, from the Round 15 model. Camera and mood: from the court in front, near the camera of plate 15, bright midday, spray catching the light. Closest drafts: `dashuifa_1.jpg`, `dashuifa_2.jpg` (16:9); `dashuifa_v_1.jpg`, `dashuifa_v_2.jpg` vertical.
- `home-lantern-night`: file `home-lantern-night.webp`, 4:5, render at 1100 × 1375. Narrow, right of a row. Scene: lanterns along a covered way by the water at the Lantern Festival (上元), as the court paintings of the festival show it (for example P0279, the Qianlong Lantern Festival scroll). Camera and mood: at eye height along the gallery, winter night, warm lantern light on dark water, quiet. No draft yet.
- `home-snow-halls`: file `home-snow-halls.webp`, 16:9, render at 2688 × 1512 (export about 2400 × 1350 if under 400 KB). Full width. Scene: the grey rolled roofs of 九洲清晏 Jiuzhou Qingyan under snow, from the Round 18 model, the lake frozen. Camera and mood: from across the 前湖 Qian Hu, a little raised, overcast winter light, snow on roofs and rocks. No draft yet; the model screenshot `refs/jiuzhou.png` is the starting view.

## In "From above" (the sideways strip, like a handscroll)

These show at up to 300 px wide in the strip; the sizes below are 2x that. Rendering at 1.5 times more (900 × 1200 for 3:4) makes them hold up in the lightbox too.

- `home-aerial-overview`: file `home-aerial-overview.webp`, 3:4, render at 600 × 800 (or 900 × 1200). Scene: the three gardens from high in the south-west, lakes, islands and halls, the Western Hills behind. Camera and mood: high oblique, clear autumn air. Closest drafts: `aerial_overview_xhs_1.jpg`, `aerial_overview_xhs_2.jpg` (3:4); `aerial_overview_1.jpg`, `aerial_overview_2.jpg` (16:9).
- `home-aerial-axis`: file `home-aerial-axis.webp`, 3:4, render at 600 × 800 (or 900 × 1200). Scene: the main axis from 大宫门 Da Gongmen through 正大光明 Zhengda Guangming to the Back Lake. Camera and mood: high, looking north along the axis, morning. Closest drafts: `aerial_axis_xhs_1.jpg`, `aerial_axis_xhs_2.jpg` (3:4).
- `home-aerial-fuhai`: file `home-aerial-fuhai.webp`, 3:4, render at 600 × 800 (or 900 × 1200). Scene: 福海 Fuhai with its islets and the halls on its shores. Camera and mood: high above the south-west corner of the lake, soft light. Closest drafts: `aerial_fuhai_xhs_1.jpg`, `aerial_fuhai_xhs_2.jpg` (3:4); `aerial_fuhai_1.jpg`, `aerial_fuhai_2.jpg` (16:9).
- `home-aerial-xiyanglou`: file `home-aerial-xiyanglou.webp`, 3:4, render at 600 × 800 (or 900 × 1200). Scene: the strip of the European palaces along the north edge of 长春园 Changchun Yuan. Camera and mood: high from the south, looking along the strip, afternoon. Closest drafts: `aerial_xiyanglou_xhs_1.jpg`, `aerial_xiyanglou_xhs_2.jpg` (3:4); `aerial_xiyanglou_1.jpg`, `aerial_xiyanglou_2.jpg` (16:9).
- `home-surroundings`: file `home-surroundings.webp`, 9:16, render at 600 × 1067 (or 900 × 1600). Scene: the gardens in their setting from the Round 20 model: the banner camps, villages, the neighbouring gardens, 玉泉山 Yuquan Shan and the Western Hills behind. Camera and mood: very high from the south-east, hazy distance. Most of the setting is inferred, so the caption must keep saying so. No draft yet.
