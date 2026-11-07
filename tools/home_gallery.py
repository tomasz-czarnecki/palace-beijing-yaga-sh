"""The homepage's AI pictures: the full-screen hero carousel, the filled gallery slots and a locator map for each, written into site/index.html and site/zh/index.html.

  uv run python tools/home_gallery.py           write the blocks
  uv run python tools/home_gallery.py --check   also print where each camera's dot lands, against its landmark

Spec: site/assets/gallery/views.json (titles, captions, what the AI added, EN and zh, the hero's order, the gallery's rows),
site/assets/gallery/cameras.json (the layout cameras the renders started from, viewer world metres) and
site/assets/gallery/manifest.json (`ready`: the slots whose picture is in place; any other slot keeps its placeholder).
Everything between the <!-- gallery:<name>:start --> and <!-- gallery:<name>:end --> markers is written here: edit the spec, not the block.
Markers: preload (head), defs (the map symbol), hero (the slides, scrim, arrows), herofoot (each slide's caption, the dots, the locator),
day and above (the gallery's groups). The hero's headline and buttons are hand-written between hero and herofoot.
Hero pictures (Round 22b): assets/gallery/<file>-1280/-1920/-2560/-3840.webp (16:9) and -phone.webp (2:3 centre crop, max-width 700px).
Slide 1 is in the page with srcset up to 2560 (first paint under about 600 KB); main.js adds the 3840 after load. Slides 2 on come
out of <template>s, one ahead of the one shown.
Gallery pictures: Round 22's are one assets/gallery/<slot>.webp each. Round 31's come in widths, <slot>-640/-1600/-2400.webp (srcset, lazy)
and <slot>-1600.jpg (what the lightbox opens); a slot with all four takes them. A group with `posts: true` draws its one-picture rows
edge to edge (.gv-post, the full-screen posts of the Küstrin gallery, the caption card over the picture's lower left). Every picture's
lightbox carries its title, text and the AI line (data-lb-cap); main.js adds the AI label.
After the Küstrin site's scripts/home_gallery.py (the locator, the hero's templates), redrawn for this site.

The map: one <symbol id="gmap"> per page, drawn from our public layers only (site/reconstruction/data: walls_1860, water_1860
without the lakes outside the walls, hills_1860 read off the plan, not the generated ones, buildings_1860 for the seals and the axis).
Its coordinates are the 3D view's own: lon/lat go to x (east) and z (south) in metres by the affine map of
site/reconstruction/generated/ground.json `lonlat`, the same one viewer.toXZ uses (site/reconstruction/3d.js), and one SVG unit is
one metre, x right, z down. So a camera's eye (x, z) from cameras.json is the dot's (cx, cy) as it stands. North is up to within
half a degree (the frame is UTM 50N).
"""

import html
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from shapely import transform
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent.parent
GAL = ROOT / "site/assets/gallery"
DATA = ROOT / "site/reconstruction/data"
SPEC = json.loads((GAL / "views.json").read_text(encoding="utf-8"))
CAMS = json.loads((GAL / "cameras.json").read_text(encoding="utf-8"))
READY = set(json.loads((GAL / "manifest.json").read_text(encoding="utf-8"))["ready"])
LONLAT = json.loads((ROOT / "site/reconstruction/generated/ground.json").read_text(encoding="utf-8"))["lonlat"]
PAGES = {"en": (ROOT / "site/index.html", ""), "zh": (ROOT / "site/zh/index.html", "../")}
FIRST_PAINT = 600_000  # what the hero's first picture may weigh at the largest size the page offers it before load
HERO_SIZES = (1280, 1920, 2560, 3840)
HERO_W, HERO_H = 3840, 2160
GALLERY_SIZES = (640, 1600, 2400)  # Round 31's gallery pictures: <vid>-<w>.webp, and <vid>-1600.jpg for the lightbox
PHONE_W, PHONE_H = 1200, 1800

MAP_PX = 150  # the map's width on the page the dot and the labels are sized for
REACH = (320, 760)  # the wedge's length in metres, clamped: the eye-to-target distance, readable at the map's size (a view's `reach` overrides)
LABEL_AT = {"W01": (-760, -330), "W02": (880, -150), "W03": (450, 330)}  # each garden's name, in its own ring and clear of the seals and most cameras

WORDS = {
    "en": {
        "carousel": "AI pictures of the gardens from our 3D model",
        "slide": "{i} of {n}", "dot": "Show picture {i} of {n}", "prev": "Previous picture", "next": "Next picture",
        "pause": "Pause the slideshow", "play": "Play the slideshow",
        "large": "View large", "open": "Open this view in 3D", "also": "In 3D:", "ai": "AI visualisation", "enlarge": "Enlarge",
        "map": "Map of the gardens: where this picture looks from",
        "dirs": ["north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"],
        "gardens": {"W01": "Yuanming Yuan", "W02": "Changchun Yuan", "W03": "Qichun Yuan"},
    },
    "zh": {
        "carousel": "依据我们的三维模型生成的园林 AI 图像",
        "slide": "第 {i} 幅，共 {n} 幅", "dot": "显示第 {i} 幅，共 {n} 幅", "prev": "上一幅", "next": "下一幅",
        "pause": "暂停轮播", "play": "播放轮播",
        "large": "查看大图", "open": "在三维中打开这个视角", "also": "三维中：", "ai": "AI 图像", "enlarge": "放大",
        "map": "园林地图：这幅图的视点",
        "dirs": ["北", "东北", "东", "东南", "南", "西南", "西", "西北"],
        "gardens": {"W01": "圆明园", "W02": "长春园", "W03": "绮春园"},
    },
}


def to_xz(lon, lat):
    """viewer.toXZ of site/reconstruction/3d.js, on ground.json's lonlat."""
    a = LONLAT
    dl, dp = lon - a["lon0"], lat - a["lat0"]
    return a["x"][0] + a["x"][1] * dl + a["x"][2] * dp, a["z"][0] + a["z"][1] * dl + a["z"][2] * dp


def project(geom):
    return transform(geom, lambda ll: np.column_stack(to_xz(ll[:, 0], ll[:, 1])))


def layer(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))["features"]


BUILDINGS = {f["properties"]["id"]: f for f in layer("buildings_1860.geojson")}


def place(bid):
    return to_xz(*BUILDINGS[bid]["geometry"]["coordinates"])


def name(bid, lang):
    p = BUILDINGS[bid]["properties"]
    return p["name_zh"] if lang == "zh" else f'<span lang="zh-Hans">{p["name_zh"]}</span> {p["name_pinyin"]}'


def plain(text):
    return html.unescape(re.sub(r"<[^>]+>", "", text))


def poly_path(geom, tol):
    geom = geom.simplify(tol, preserve_topology=True)
    out = []
    for p in geom.geoms if isinstance(geom, MultiPolygon) else [geom]:
        if not isinstance(p, Polygon) or p.is_empty:
            continue
        for ring in (p.exterior, *p.interiors):
            pts = [f"{x:.0f} {z:.0f}" for x, z in ring.coords[:-1]]
            if len(pts) > 2:
                out.append("M" + "L".join(pts) + "Z")
    return "".join(out)


def line_path(lines, tol):
    out = []
    for g in lines:
        for part in getattr(g.simplify(tol), "geoms", [g.simplify(tol)]):
            pts = [f"{x:.0f} {z:.0f}" for x, z in part.coords]
            if len(pts) > 1:
                out.append("M" + "L".join(pts))
    return "".join(out)


def walls():
    rings, lines = {}, []
    for f in layer("walls_1860.geojson"):
        if f["geometry"]["type"] != "LineString":
            continue
        g = project(shape(f["geometry"]))
        if f["properties"]["kind"] == "outer_wall":
            rings[f["properties"]["id"]] = Polygon(g.coords).buffer(0)
        else:
            lines.append(g)
    return rings, lines


RINGS, INNER_WALLS = walls()
# the gardens, and every camera's eye with room for its dot: the overview stands 200 m south of the outer wall
_b = unary_union(list(RINGS.values()) + [Point(CAMS[v]["eye"][0], CAMS[v]["eye"][2]).buffer(60) for v in SPEC["views"] if v in CAMS]).bounds
VIEW = (math.floor(_b[0] - 70), math.floor(_b[1] - 70), math.ceil(_b[2] - _b[0] + 140), math.ceil(_b[3] - _b[1] + 140))
SCALE = VIEW[2] / MAP_PX  # metres per pixel of the map as drawn


def base_map(lang):
    """The shared drawing, once per page: every locator <use>s it."""
    inside = unary_union(list(RINGS.values()))
    water = unary_union([project(shape(f["geometry"])).buffer(0) for f in layer("water_1860.geojson") if not f["properties"].get("outside")])
    water = water.intersection(inside.buffer(30)).buffer(6).buffer(-6)  # closes slivers too thin to read at this size
    hills = unary_union([project(shape(f["geometry"])).buffer(0) for f in layer("hills_1860.geojson") if not f["properties"].get("assumed")])
    hills = hills.buffer(10).buffer(-4).difference(water)  # soft blobs, as a wash
    axis = LineString([place("YM41"), place("YM01"), place("YM03")])
    s = SCALE
    seals = "".join(f'<rect x="{x - 1.4 * s:.0f}" y="{z - 1.4 * s:.0f}" width="{2.8 * s:.0f}" height="{2.8 * s:.0f}" transform="rotate(45 {x:.0f} {z:.0f})"/>' for x, z in map(place, SPEC["seals"]))
    labels = []
    for wid, ring in RINGS.items():
        x, z = LABEL_AT[wid]
        assert ring.contains(Point(x, z)), wid
        labels.append(f'<text x="{x:.0f}" y="{z:.0f}">{WORDS[lang]["gardens"][wid]}</text>')
    fs = 7.5 * s
    return (
        '<svg class="gmap-defs" width="0" height="0" aria-hidden="true" focusable="false" style="position:absolute"><defs>'
        f'<symbol id="gmap" viewBox="{" ".join(map(str, VIEW))}">'
        f'<path class="gm-garden" d="{poly_path(inside, 4)}"/>'
        f'<path class="gm-hill" d="{poly_path(hills, 6)}"/>'
        f'<path class="gm-water" d="{poly_path(water, 5)}"/>'
        f'<path class="gm-wall" d="{line_path([r.exterior for r in RINGS.values()] + INNER_WALLS, 3)}"/>'
        f'<path class="gm-axis" d="{line_path([axis], 1)}"/>'
        f'<g class="gm-seal">{seals}</g>'
        f'<g class="gm-label" font-size="{fs:.0f}" text-anchor="middle"{" lang=" + chr(34) + "zh-Hans" + chr(34) if lang == "zh" else ""}>{"".join(labels)}</g>'
        "</symbol></defs></svg>"
    )


def bearing(dx, dz):
    """Compass bearing of a step (dx east, dz south), as cameras.json gives it."""
    return math.degrees(math.atan2(dx, -dz)) % 360


def compass(deg, lang):
    return WORDS[lang]["dirs"][round(deg / 45) % 8]


def hfov(cam, frame):
    """The picture's horizontal field: from the vertical fov and the shape the page shows."""
    t = math.tan(math.radians(cam["fov_vertical_deg"]) / 2)
    k = {"16:9": 16 / 9, "3:4": 3 / 4, "4:5": 9 / 16}[frame]  # 3:4 a centre crop of a 16:9 render; 4:5 a 9:16 render at its full width
    return 2 * math.degrees(math.atan(t * k))


def nearest(cam):
    ex, _, ez = cam["eye"]
    d = {bid: math.dist((ex, ez), place(bid)) for bid in SPEC["landmarks"]}
    bid = min(d, key=d.get)
    return bid, d[bid]


def from_line(vid, lang, short=False):
    cam = CAMS[vid]
    (ex, _, ez), (tx, _, tz) = cam["eye"], cam["target"]
    side = compass(bearing(ex - tx, ez - tz), lang)
    look = compass(cam["bearing_deg"], lang)
    h = cam["height_above_ground_m"]
    bid, d = nearest(cam)
    up = round(h, -1) if h < 500 else round(h, -2)
    near = f"{round(d, -1):.0f}" if d >= 15 else f"{d:.0f}"
    if lang == "zh":
        how = "平视" if h <= 3 else ("离地几米处" if h <= 10 else f"约 {up:,.0f} 米高处")
        head = f"从{side}面{how}，向{look}看" if h <= 3 else f"从{side}面、{how}向{look}看"
        if short:
            return head
        return f"{head}。最近的地标：{name(bid, lang)}，约 {near} 米。"
    how = "at eye level" if h <= 3 else ("a few metres up" if h <= 10 else f"about {up:,.0f} m up")
    if short:
        return f"From the {side}, {how}, looking {look}"
    return f"From the {side}, {how}, looking {look}. Nearest landmark: {name(bid, lang)}, about {near} m."


def wedge(vid):
    cam = CAMS[vid]
    (ex, _, ez), (tx, _, tz) = cam["eye"], cam["target"]
    r = SPEC["views"][vid].get("reach") or min(max(math.dist((ex, ez), (tx, tz)), REACH[0]), REACH[1])
    half = math.radians(hfov(cam, SPEC["views"][vid]["frame"])) / 2
    a = math.radians(cam["bearing_deg"])
    p1 = (ex + r * math.sin(a - half), ez - r * math.cos(a - half))
    p2 = (ex + r * math.sin(a + half), ez - r * math.cos(a + half))
    return f"M{ex:.0f} {ez:.0f}L{p1[0]:.0f} {p1[1]:.0f}A{r:.0f} {r:.0f} 0 0 1 {p2[0]:.0f} {p2[1]:.0f}Z"


def locator(vid, lang):
    x0, z0, w, h = VIEW
    ex, _, ez = CAMS[vid]["eye"]
    s = SCALE
    nx, nz = x0 + w - 9 * s, z0 + 7 * s
    north = f'<path class="gm-north" d="M{nx:.0f} {nz:.0f}l{3.2 * s:.0f} {8.5 * s:.0f}l{-3.2 * s:.0f} {-2.4 * s:.0f}l{-3.2 * s:.0f} {2.4 * s:.0f}Z"/>'
    return (
        f'<svg class="gmap" viewBox="{x0} {z0} {w} {h}" role="img" aria-label="{html.escape(WORDS[lang]["map"])}">'
        f'<use href="#gmap" x="{x0}" y="{z0}" width="{w}" height="{h}"/>{north}'
        f'<path class="gm-cone" d="{wedge(vid)}"/>'
        f'<circle class="gm-dot" cx="{ex:.0f}" cy="{ez:.0f}" r="{3.6 * s:.0f}" stroke-width="{1.3 * s:.0f}"/>'
        "</svg>"
    )


def link3d(vid, pre):
    cam = CAMS[vid]
    q = ",".join(f"{v:g}" for v in (*cam["eye"], *cam["target"]))
    return f"{pre}reconstruction/3d.html?cam={q}"


def srcset(stem, sizes):
    return ", ".join(f"{stem}-{w}.webp {w}w" for w in sizes)


def hero_picture(vid, lang, pre, first):
    """Slide 1 offers up to 2560 before load (main.js adds the 3840 after); the rest offer every size."""
    stem = f"{pre}assets/gallery/{SPEC['views'][vid]['file']}"
    sizes = HERO_SIZES[:-1] if first else HERO_SIZES
    attrs = ' fetchpriority="high"' if first else ' decoding="async"'
    full = f' data-full="{stem}-3840.webp 3840w"' if first else ""
    alt = html.escape(SPEC["views"][vid]["alt"][lang], quote=True)
    return (
        "<picture>"
        f'<source media="(max-width: 700px)" type="image/webp" srcset="{stem}-phone.webp" width="{PHONE_W}" height="{PHONE_H}">'
        f'<img src="{stem}-1280.webp" srcset="{srcset(stem, sizes)}" sizes="100vw" width="{HERO_W}" height="{HERO_H}"{attrs}{full} alt="{alt}">'
        "</picture>"
    )


def hero_block(lang, pre):
    """The picture layer: the slides, the scrim under the words, the arrows, the live region."""
    w = WORDS[lang]
    ids = SPEC["hero"]
    n = len(ids)
    slides = []
    for i, vid in enumerate(ids):
        v = SPEC["views"][vid]
        pic = hero_picture(vid, lang, pre, i == 0)
        pic = pic if i == 0 else f'<template class="hero-slide-tpl">{pic}</template>'
        top, bottom = v["bg"]
        slides.append(
            f'<div class="hero-slide{" is-on" if i == 0 else ""}" role="group" aria-roledescription="slide" aria-label="{w["slide"].format(i=i + 1, n=n)}" '
            f'data-slide="{vid}" data-title="{html.escape(plain(v["title"][lang]), quote=True)}" style="--bg-top:{top};--bg-bot:{bottom}"{"" if i == 0 else " inert"}>{pic}</div>'
        )
    return (
        f'<div class="hero-slides">{"".join(slides)}</div>'
        '<div class="hero-scrim" aria-hidden="true"></div>'
        f'<button class="hero-arrow hero-prev" type="button" aria-label="{w["prev"]}" hidden><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10 3L5 8l5 5"/></svg></button>'
        f'<button class="hero-arrow hero-next" type="button" aria-label="{w["next"]}" hidden><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M6 3l5 5-5 5"/></svg></button>'
        '<p class="hero-status" aria-live="polite"></p>'
    )


def hero_foot(lang, pre):
    """Under the buttons: each slide's title, its one line on what the AI invented, the label; the dots and pause; the locator."""
    w = WORDS[lang]
    ids = SPEC["hero"]
    n = len(ids)
    caps, locs = [], []
    for i, vid in enumerate(ids):
        v = SPEC["views"][vid]
        on = " is-on" if i == 0 else ""
        hide = "" if i == 0 else ' aria-hidden="true"'
        title = plain(v["title"][lang])
        stem = f"{pre}assets/gallery/{v['file']}"
        lb_cap = f"{title}. {plain(v['ai'][lang])}" if lang == "en" else f"{title}。{plain(v['ai'][lang])}"
        big = (f'<a class="hero-large" href="{stem}-3840.webp" data-lb data-lb-ai data-lb-cap="{html.escape(lb_cap, quote=True)}" '
               f'data-lb-alt="{html.escape(v["alt"][lang], quote=True)}"{"" if i == 0 else " tabindex=" + chr(34) + "-1" + chr(34)}>{w["large"]}</a>')
        caps.append(
            f'<div class="hero-cap{on}" data-i="{i}"{hide}><p class="hero-title">{v["title"][lang]}</p>'
            f'<p class="hero-note">{v["short"][lang]}</p>'
            f'<p class="hero-meta"><span class="hero-ai">{SPEC["label"][lang]}</span>{big}</p></div>'
        )
        locs.append(
            f'<div class="hero-loc{on}" data-i="{i}"{hide}><p class="hero-from">{from_line(vid, lang, short=True)}</p>{locator(vid, lang)}</div>'
        )
    dots = "".join(f'<button class="hero-dot" type="button" aria-label="{w["dot"].format(i=i + 1, n=n)}"{" aria-current=" + chr(34) + "true" + chr(34) if i == 0 else ""}></button>' for i in range(n))
    nav = (
        '<div class="hero-nav" hidden>'
        f'<span class="hero-dots">{dots}</span>'
        f'<button class="hero-pause" type="button" aria-label="{w["pause"]}" data-pause="{w["pause"]}" data-play="{w["play"]}">'
        '<svg class="i-pause" viewBox="0 0 16 16" aria-hidden="true"><path d="M5 3v10M11 3v10"/></svg><svg class="i-play" viewBox="0 0 16 16" aria-hidden="true"><path d="M5 3l8 5-8 5z"/></svg></button>'
        '<span class="hero-progress" aria-hidden="true"><i></i></span>'
        "</div>"
    )
    return (
        '<div class="hero-foot">'
        f'<div class="hero-caps">{"".join(caps)}</div>{nav}<div class="hero-where">{"".join(locs)}</div>'
        "</div>"
    )


def preload_block(pre):
    stem = f"{pre}assets/gallery/{SPEC['views'][SPEC['hero'][0]]['file']}"
    return (
        f'<link rel="preload" as="image" type="image/webp" href="{stem}-phone.webp" media="(max-width: 700px)" fetchpriority="high">\n  '
        f'<link rel="preload" as="image" type="image/webp" imagesrcset="{srcset(stem, HERO_SIZES[:-1])}" imagesizes="100vw" media="(min-width: 701px)" fetchpriority="high">'
    )


def where(vid, lang, pre):
    w = WORDS[lang]
    v = SPEC["views"][vid]
    also = ""
    if v.get("open"):
        also = f'<p class="gv-pages">{w["also"]} <a href="{pre}reconstruction/3d.html?b={v["open"]}">{name(v["open"], lang)}</a></p>'
    return (
        f'<div class="gv-where">{locator(vid, lang)}<div class="gv-where-text">'
        f'<p class="gv-from">{from_line(vid, lang)}</p>'
        f'<a class="gv-3d" href="{link3d(vid, pre)}">{w["open"]}</a>{also}</div></div>'
    )


def sized(vid):
    """Round 31: a picture in several widths, <vid>-640/-1600/-2400.webp, and <vid>-1600.jpg for the lightbox. Round 22's are one <vid>.webp."""
    return all((GAL / f"{vid}-{w}.webp").exists() for w in GALLERY_SIZES) and (GAL / f"{vid}-1600.jpg").exists()


def lb_caption(vid, lang):
    """The lightbox's line: the title, the text and what the AI added (main.js appends the AI label)."""
    v = SPEC["views"][vid]
    stop = ". " if lang == "en" else "。"
    return f"{plain(v['title'][lang])}{stop}{plain(v['text'][lang])} {plain(v['ai'][lang])}"


def card(vid, lang, pre, strip=False, sizes="100vw"):
    """A filled slot: the picture in its frame, the caption with what the AI added, the locator. Classes as Round 21's placeholder once filled, so its CSS and the lightbox hold."""
    w = WORDS[lang]
    v = SPEC["views"][vid]
    title = plain(v["title"][lang])
    alt = html.escape(v["alt"][lang], quote=True)
    stem = f"{pre}assets/gallery/{vid}"
    if sized(vid):
        im = Image.open(GAL / f"{vid}-{GALLERY_SIZES[-1]}.webp")
        big = f"{stem}-1600.jpg"
        img = (f'<img src="{stem}-1600.webp" srcset="{srcset(stem, GALLERY_SIZES)}" sizes="{sizes}" width="{im.width}" height="{im.height}" '
               f'loading="lazy" decoding="async" alt="{alt}">')
    else:
        im = Image.open(GAL / f"{vid}.webp")
        big = f"{stem}.webp"
        img = f'<img src="{stem}.webp" width="{im.width}" height="{im.height}" loading="lazy" decoding="async" alt="{alt}">'
    h = "h3"
    return (
        f'<figure class="ph ph-filled" data-slot="{vid}" data-aspect="{v["frame"]}" id="view-{vid}">'
        f'<a class="gv-pic ph-link" href="{big}" data-lb data-lb-ai data-lb-cap="{html.escape(lb_caption(vid, lang), quote=True)}" aria-label="{w["enlarge"]}: {html.escape(title, quote=True)}">'
        f'<span class="ph-frame">{img}'
        f'<span class="pic-tag is-ai">{w["ai"]}</span></span></a>'
        f'<figcaption class="gv-cap"><{h}>{v["title"][lang]}</{h}><p>{v["text"][lang]}</p><p class="gv-ai">{v["ai"][lang]}</p>'
        f'{where(vid, lang, pre)}<span class="gv-label">{w["ai"]}</span></figcaption>'
        "</figure>"
    )


def placeholder(slot, lang, strip=False):
    """Round 21's designed placeholder, for a slot whose picture is not in place yet (main.js fills it once the manifest lists it)."""
    if slot in SPEC["placeholders"]:
        p = SPEC["placeholders"][slot]
        aspect, alt, title, text = p["aspect"], p["alt"][lang], p["title"][lang], p["text"][lang]
    else:
        v = SPEC["views"][slot]
        aspect, alt, title, text = v["frame"], v["alt"][lang], v["title"][lang], v["text"][lang]
    to_come = "AI render to come" if lang == "en" else "AI 图像待补"
    seal = '<span class="ph-seal" lang="zh-Hans" aria-hidden="true">待</span>' if lang == "en" else '<span class="ph-seal" aria-hidden="true">待</span>'
    frame = f'<span class="ph-frame"><svg class="ph-art" aria-hidden="true" focusable="false"><use href="#ph-land"/></svg>{seal}<span class="ph-label"><b>{to_come}</b><code>{slot}</code> · {aspect}</span></span>'
    label = "" if strip else f'<span class="gv-label" data-filled="{WORDS[lang]["ai"]}">{"Picture to come" if lang == "en" else "图像待补"}</span>'
    return (
        f'<figure class="ph" data-slot="{slot}" data-aspect="{aspect}" data-alt="{html.escape(alt, quote=True)}">{frame}'
        f'<figcaption class="gv-cap"><h3>{title}</h3><p>{text}</p>{label}</figcaption></figure>'
    )


def slot(vid, lang, pre, strip=False, sizes="100vw"):
    if vid in READY and vid in SPEC["views"] and ((GAL / f"{vid}.webp").exists() or sized(vid)):
        return card(vid, lang, pre, strip, sizes)
    return placeholder(vid, lang, strip)


ROW_SIZES = {"wide": "(max-width: 900px) 100vw, 58vw", "narrow": "(max-width: 900px) 100vw, 42vw"}  # the 7fr and 5fr columns of a .gv-row, at most 1440 px


def group_block(g, lang, pre):
    """A group: its heading, then its rows. A `posts` group (Round 31) draws its one-picture rows edge to edge (.gv-post), the full-screen posts of the Küstrin gallery;
    a row of two 16:9 pictures puts its wide column on the left, then on the right, in turn."""
    out = [f'<div class="views-head"><div class="eyebrow"><span class="eyebrow-bar"></span>{g["eyebrow"][lang]}</div><h2>{g["h2"][lang]}</h2></div>']
    if "strip" in g:
        cards = "\n".join(slot(v, lang, pre, strip=True) for v in g["strip"])
        out.append(f'<div class="scroll-strip"><div class="scroll-track" tabindex="0" role="region" aria-label="{g["strip_label"][lang]}">\n{cards}\n</div><p class="scroll-hint">{g["hint"][lang]}</p></div>')
    pairs = 0
    for i, row in enumerate(g.get("rows", [])):
        if len(row) == 1:
            post = " gv-post" if g.get("posts") else ""
            out.append(f'<div class="gv gv-full{post} reveal">{slot(row[0], lang, pre)}</div>')
        else:
            # the row's narrow slot is the 4:5 one; its side alternates as in Round 21
            kinds = ["narrow" if SPEC["views"].get(v, {}).get("frame") == "4:5" else "wide" for v in row]
            cls = "gv-row gv-row-narrow" if kinds[0] == "narrow" else "gv-row"
            cols = ["wide", "narrow"] if cls == "gv-row" else ["narrow", "wide"]  # the 7fr and 5fr columns, for each picture's `sizes`
            if g.get("posts") and kinds == ["wide", "wide"]:
                if pairs % 2:
                    cls, cols = "gv-row gv-row-flip", ["narrow", "wide"]  # both stay 16:9, the wide column moves right
                pairs += 1
            out.append(f'<div class="{cls}">' + "".join(f'<div class="gv gv-{k} reveal">{slot(v, lang, pre, sizes=ROW_SIZES[c])}</div>' for v, k, c in zip(row, kinds, cols)) + "</div>")
    return "\n".join(out)


def fill(page, key, block):
    start, end = f"<!-- gallery:{key}:start -->", f"<!-- gallery:{key}:end -->"
    assert start in page and end in page, f"marker {key} missing"
    return re.sub(re.escape(start) + r".*?" + re.escape(end), lambda _: f"{start}\n{block}\n{end}", page, flags=re.S)


def gallery_views():
    """Every view the gallery shows, group by group: rows, then the strip."""
    return [v for g in SPEC["groups"] for v in [x for r in g.get("rows", []) for x in r] + g.get("strip", [])]


def check():
    """Where each dot lands, against the landmark the picture says it shows. `off line` is how far the landmark stands from the
    eye-to-target line (Round 31: the building a caption names should be within about 60 m of it), `inside` whether the dot is in a garden."""
    print(f"map viewBox {VIEW}; 1 SVG unit = 1 m; {SCALE:.1f} m per px at {MAP_PX} px wide")
    print(f"{'view':28} {'eye (svg x, y)':>18} {'landmark':10} {'landmark (svg)':>18} {'dist m':>7} {'bearing':>7} {'to lm':>6} {'off line':>8} inside")
    gardens = unary_union(list(RINGS.values()))
    for vid in SPEC["hero"] + gallery_views():
        if vid not in CAMS or vid not in SPEC["views"]:
            continue
        cam = CAMS[vid]
        ex, _, ez = cam["eye"]
        tx, _, tz = cam["target"]
        lm = SPEC["views"][vid]["landmark"]
        lx, lz = place(lm)
        # the camera's own bearing against the one its eye and target give
        b = bearing(tx - ex, tz - ez)
        to_lm = bearing(lx - ex, lz - ez)
        off = LineString([(ex, ez), (ex + 3 * (tx - ex), ez + 3 * (tz - ez))]).distance(Point(lx, lz))  # the line runs on past the target
        inside = "yes" if gardens.buffer(30).contains(Point(ex, ez)) else "no"
        print(f"{vid:28} {ex:8.1f} {ez:8.1f}  {lm:10} {lx:8.1f} {lz:8.1f} {math.dist((ex, ez), (lx, lz)):7.0f} {cam['bearing_deg']:4.0f}/{b:3.0f} {to_lm:6.0f} {off:8.0f} {inside:6} nearest {nearest(cam)[0]}")


def main():
    first = SPEC["views"][SPEC["hero"][0]]["file"]
    for size in (*HERO_SIZES[:-1], "phone"):
        assert (GAL / f"{first}-{size}.webp").stat().st_size <= FIRST_PAINT, f"{first}-{size}: the first slide is over its budget"
    for vid in SPEC["hero"]:
        stem = SPEC["views"][vid]["file"]
        for size in (*HERO_SIZES, "phone"):
            assert (GAL / f"{stem}-{size}.webp").exists(), f"{stem}-{size}.webp missing"
        assert Image.open(GAL / f"{stem}-3840.webp").size == (HERO_W, HERO_H), stem
        assert Image.open(GAL / f"{stem}-phone.webp").size == (PHONE_W, PHONE_H), stem
    for vid, v in SPEC["views"].items():
        assert vid in CAMS, f"{vid} has no camera"
        x0, z0, w, h = VIEW
        assert x0 <= CAMS[vid]["eye"][0] <= x0 + w and z0 <= CAMS[vid]["eye"][2] <= z0 + h, f"{vid}: the camera is outside the map"
        for lang in ("en", "zh"):
            for k in ("title", "text", "ai", "alt", "short"):
                if k in v:
                    assert "\u2014" not in v[k][lang] and "\u2013" not in v[k][lang], f"{vid} {k} {lang}: a dash"
    for lang, (path, pre) in PAGES.items():
        page = path.read_text(encoding="utf-8")
        blocks = {"preload": preload_block(pre), "defs": base_map(lang), "hero": hero_block(lang, pre), "herofoot": hero_foot(lang, pre)}
        blocks.update({g["id"]: group_block(g, lang, pre) for g in SPEC["groups"]})
        done = []
        for key, block in blocks.items():
            if f"<!-- gallery:{key}:start -->" in page:
                page = fill(page, key, block)
                done.append(key)
        path.write_text(page, encoding="utf-8")
        print(f"{path.name} ({lang}): wrote {', '.join(done)}")
    print("hero", len(SPEC["hero"]), "slides; filled slots", sum(1 for v in gallery_views() if v in READY), "; map defs", len(base_map("en")), "bytes")
    if "--check" in sys.argv:
        check()


if __name__ == "__main__":
    main()
