"""Round 20: the public page on what surrounded the gardens, in English and a Chinese draft, with a plan drawn from our own layers. Idempotent: a second run changes nothing.

  uv run python scripts/around_page.py        (after scripts/surroundings1860.py and scripts/photos_catalog.py)

Reads research/surroundings/about.json (the text, EN and zh, hand-edited), research/layers/surroundings_1860.geojson, walls_1860, water_1860, research/photos/catalog.csv, research/sources.md.
Writes site/around/index.html, site/zh/around/index.html and site/around/plan.svg. Free pictures only (asserted); no path of research/ on the page.
After changing the Chinese text, run tools/font_subset.py <repo> around from a folder holding the full Noto files (site/around/fonts.css).
"""

import csv
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

from shapely.geometry import LineString, shape

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scenes_page  # noqa: E402
from scenes_page import Pics, esc, figure, paras, shell, write_if_changed, zh_wrap  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
LAYERS = ROOT / "research/layers"
ABOUT = ROOT / "research/surroundings/about.json"
BBOX = (116.236, 39.976, 116.343, 40.031)  # west, south, east, north: the ring of the layer, 玉泉山 at the west edge
LAT_M, LON_M = 111034.0, 85276.0
S = 0.25  # plan units per metre

T = {
    "en": dict(lang="en", root="../", enter="Enter the reconstruction", home_lang="zh-Hans", nav_aria="Language", credits="Sources and image credits", sources_h="Sources cited on this page",
               footer="<span lang=\"zh-Hans\">圆明园</span> Yuanmingyuan · a reconstruction in progress", plan_h="The surroundings on our plan",
               legend=[("garden", "The three gardens (our plan of S01)"), ("neighbour", "Neighbouring gardens"), ("water", "Water"), ("road", "Roads"), ("canal", "Canals and rivers"), ("place", "Villages, camps, temples, offices"), ("dash", "Dashed or pale: inferred (C)")],
               counts_h="How sure the setting is", counts_line="{n} objects in the layer: {A} shown on a source of the time (A), {B} from a later source or a text only (B), {C} inferred (C); {assumed} placed by a guess.",
               in3d="See the setting in the 3D view", kinds={"neighbour_garden": "neighbouring gardens", "town": "town", "village": "villages", "banner_camp": "banner camps", "office": "offices", "workshop": "workshops", "storehouse": "storehouses and yards", "temple": "temples", "road": "roads", "canal": "canals", "river": "rivers", "sluice": "sluices", "bridge": "bridges", "field": "fields", "paddy": "paddies", "orchard": "orchards", "tomb": "tombs", "hill_far": "hills", "lake": "lakes", "spring": "springs", "other": "other"}),
    "zh": dict(lang="zh-Hans", root="../../", enter="进入复原", home_lang="en", nav_aria="语言", credits="资料来源与图片版权（英文）", sources_h="本页引用的资料", footer="<span>圆明园复原 · 进行中</span>", plan_h="周边平面示意",
               legend=[("garden", "圆明三园（据S01）"), ("neighbour", "相邻园林"), ("water", "水面"), ("road", "道路"), ("canal", "河渠"), ("place", "村落、营房、寺庙、衙署"), ("dash", "虚线或浅色：推测（C）")],
               counts_h="可信程度", counts_line="图层共{n}项：同时代资料所示{A}项（A），后世资料或仅有文字{B}项（B），推测{C}项（C）；其中{assumed}项位置为推测。",
               in3d="在三维视图中查看周边", kinds={"neighbour_garden": "相邻园林", "town": "市镇", "village": "村落", "banner_camp": "八旗营房", "office": "衙署", "workshop": "作坊", "storehouse": "仓厂", "temple": "寺庙", "road": "道路", "canal": "河渠", "river": "河流", "sluice": "闸", "bridge": "桥", "field": "田地", "paddy": "稻田", "orchard": "果园", "tomb": "墓", "hill_far": "山", "lake": "湖", "spring": "泉", "other": "其他"}),
}
COL = {"bg": "#221C16", "garden": "#3D4A2E", "garden_edge": "#7E8C5A", "neighbour": "#4A4A33", "neighbour_edge": "#9C9567", "water": "#2C4650", "road": "#B79A6B", "canal": "#5E8FA3", "place": "#E0A060", "place_c": "#8F7556", "text": "#F5EEE2", "muted": "#A1927D"}


def xy(lon, lat):
    return (lon - BBOX[0]) * LON_M * S, (BBOX[3] - lat) * LAT_M * S


def path_of(coords, closed, tol=1.0):
    line = LineString([xy(*c[:2]) for c in coords]).simplify(tol)
    pts = list(line.coords)
    if len(pts) < 2:
        return ""
    return "M" + "L".join(f"{x:.0f} {y:.0f}" for x, y in pts) + ("Z" if closed else "")


def rings(geom):
    g = geom["coordinates"]
    if geom["type"] == "Polygon":
        return [g[0]]
    if geom["type"] == "MultiPolygon":
        return [p[0] for p in g]
    return []


def lines(geom):
    if geom["type"] == "LineString":
        return [geom["coordinates"]]
    if geom["type"] == "MultiLineString":
        return geom["coordinates"]
    return []


def sources_block(text, t):
    """scenes_page's list of the sources a text cites, for ids of up to four digits (S1207)."""
    used = sorted(set(re.findall(r"\bS\d{2,4}\b", text)), key=lambda s: int(s[1:]))
    return _sources(used, t)


def _sources(used, t):
    src = {}
    for line in (ROOT / "research/sources.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| (S\d+) \| ([^|]*)\|", line)
        if m:
            url = re.search(r"https?://[^\s|)]+", line)
            src[m[1]] = (re.split(r"(?<=[a-z0-9)])\. ", m[2].strip())[0][:170], url[0].rstrip(".,;") if url else "")
    items = []
    lang = "en" if t["lang"] == "en" else "zh"
    for s in used:
        if s in src:
            name, url = src[s]
            items.append(f'<li><b>{s}</b> ' + (f'<a href="{esc(url)}" rel="noopener noreferrer" target="_blank">{zh_wrap(name, lang)}</a>' if url else zh_wrap(name, lang)) + "</li>")
    return f'<details class="xy-more"><summary>{t["sources_h"]} ({len(items)})</summary><ul class="xy-sources">{"".join(items)}</ul></details>'


def plan_svg(feats, key):
    t = T[key]
    w, h = xy(BBOX[2], BBOX[1])
    out = [f'<svg class="xy-plan sc-plan" viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(t["plan_h"])}"><rect width="{w:.0f}" height="{h:.0f}" fill="{COL["bg"]}"/>']
    garden = [path_of(f["geometry"]["coordinates"], True) for f in json.load(open(LAYERS / "walls_1860.geojson", encoding="utf-8"))["features"] if f["geometry"]["type"] == "LineString" and f["properties"]["kind"] == "outer_wall"]
    neigh = []
    for f in feats:
        if f["properties"]["kind"] == "neighbour_garden" and f["geometry"]["type"] in ("Polygon", "MultiPolygon"):
            g = shape(f["geometry"]).buffer(-0.0011).buffer(0.0011)  # about 100 m: as the view draws it, without today's thin strips
            neigh += [path_of(list(q.exterior.coords), True) for q in getattr(g, "geoms", [g]) if not q.is_empty]
    out.append(f'<path d="{"".join(neigh)}" fill="{COL["neighbour"]}" stroke="{COL["neighbour_edge"]}" stroke-width="2" stroke-dasharray="6 5"/>')
    out.append(f'<path d="{"".join(garden)}" fill="{COL["garden"]}" stroke="{COL["garden_edge"]}" stroke-width="2.5"/>')
    water = [path_of(r, True, 1.5) for f in json.load(open(LAYERS / "water_1860.geojson", encoding="utf-8"))["features"] for r in rings(f["geometry"])]
    out.append(f'<path d="{"".join(water)}" fill="{COL["water"]}"/>')
    for f in feats:
        p = f["properties"]
        if p["kind"] in ("field", "paddy", "orchard"):
            out.append(f'<path d="{"".join(path_of(r, True) for r in rings(f["geometry"]))}" fill="#56603A" fill-opacity="0.45"/>')
    for kind, colour, wid in (("canal", COL["canal"], 3.5), ("river", COL["canal"], 4.5), ("road", COL["road"], 3.0)):
        for conf in ("C", "B", "A"):
            d = "".join(path_of(ln, False) for f in feats if f["properties"]["kind"] == kind and f["properties"]["confidence"] == conf for ln in lines(f["geometry"]))
            if d:
                out.append(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{wid}" stroke-linecap="round"' + (' stroke-dasharray="8 6" stroke-opacity="0.8"' if conf == "C" else "") + "/>")
    out.append(f'<g font-family="Noto Serif SC, Songti SC, serif" text-anchor="middle" fill="{COL["text"]}">')
    placed = []
    for f in feats:
        p = f["properties"]
        if p["kind"] not in ("neighbour_garden", "town", "banner_camp", "village") or not p["name_zh"]:
            continue  # one label per garden, town, camp and village; temples, bridges, sluices and the lines of 1860 are in the 3D view and its panels
        g = shape(f["geometry"])
        c = g.representative_point() if g.geom_type != "Point" else g
        x, y = xy(c.x, c.y)
        if not (0 < x < w and 0 < y < h):
            continue
        big = p["kind"] in ("neighbour_garden", "town")
        size = 30 if big else 19
        if any(abs(x - a) < 60 and abs(y - b) < 16 for a, b in placed):
            continue
        placed.append((x, y))
        if not big:
            out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="4" fill="{COL["place"] if p["confidence"] != "C" else COL["place_c"]}"/>')
        name = re.split(r"\s*[(（/]", p["name_zh"])[0].replace("护军营房", "").replace("护军大营房", "大营").replace("护军小营房", "小营")
        out.append(f'<text x="{x:.0f}" y="{y - (8 if not big else -10):.0f}" font-size="{size}" stroke="#17130F" stroke-width="{size / 5:.0f}" paint-order="stroke">{esc(name)}</text>')
    for zh, en, lon, lat in (("圆明园", "Yuanming Yuan", 116.2935, 40.0090), ("长春园", "Changchun Yuan", 116.3088, 40.0090), ("绮春园", "Qichun Yuan", 116.3035, 39.9985)):
        x, y = xy(lon, lat)
        out.append(f'<text x="{x:.0f}" y="{y:.0f}" font-size="34" fill="#F5EEE2" stroke="#17130F" stroke-width="7" paint-order="stroke">{zh}</text>')
    km = 1000 * S
    out.append(f'</g><g font-family="Geist Mono, monospace" font-size="22" fill="{COL["muted"]}"><path d="M{w - km - 60:.0f} {h - 34:.0f}h{km:.0f}" stroke="{COL["muted"]}" stroke-width="4"/><text x="{w - km - 60:.0f}" y="{h - 46:.0f}">1 km</text><text x="{w - 40:.0f}" y="{h - 26:.0f}">N ↑</text></g></svg>')
    return "".join(out)


def legend(key):
    t = T[key]
    sw = {"garden": f'<span class="ar-sw" style="background:{COL["garden"]};border-color:{COL["garden_edge"]}"></span>', "neighbour": f'<span class="ar-sw" style="background:{COL["neighbour"]};border-color:{COL["neighbour_edge"]};border-style:dashed"></span>',
          "water": f'<span class="ar-sw" style="background:{COL["water"]}"></span>', "road": f'<span class="ar-ln" style="border-color:{COL["road"]}"></span>', "canal": f'<span class="ar-ln" style="border-color:{COL["canal"]}"></span>',
          "place": f'<span class="ar-dot" style="background:{COL["place"]}"></span>', "dash": f'<span class="ar-ln" style="border-color:{COL["muted"]};border-top-style:dashed"></span>'}
    return '<ul class="ar-legend">' + "".join(f"<li>{sw[k]}{zh_wrap(v, key)}</li>" for k, v in t["legend"]) + "</ul>"


def page_body(key, about, feats, pics):
    t = T[key]
    L = "en" if key == "en" else "zh"
    n = Counter(f["properties"]["confidence"] for f in feats)
    kinds = Counter(f["properties"]["kind"] for f in feats)
    counts = t["counts_line"].format(n=len(feats), A=n["A"], B=n["B"], C=n["C"], assumed=sum(1 for f in feats if f["properties"].get("assumed")))
    kind_line = (", " if key == "en" else "，").join(f"{t['kinds'][k]} {v}" for k, v in sorted(kinds.items(), key=lambda kv: (-kv[1], kv[0])) if k != "other")
    h = about[f"h1_{L}"]
    out = ['<section id="top" class="band xy-intro"><div class="band-inner">', f'<div class="eyebrow"><span class="eyebrow-bar"></span>{zh_wrap(about[f"eyebrow_{L}"], key)}</div>',
           f'<h1 class="xy-h1"><span class="title-zh" lang="zh-Hans">{esc(h[0])}</span><span class="title-pinyin">{esc(h[1])}</span><span class="title-en">{zh_wrap(h[2], key)}</span></h1>']
    if key == "zh":
        out.append(f'<div class="tag">{esc(about["draft_zh"])}</div>')
    out += [f'<p class="lead xy-lead">{zh_wrap(p, key)}</p>' for p in re.split(r"\n\s*\n", about[f"lead_{L}"].strip())]
    out.append(f'<h2 class="xy-subh">{zh_wrap(t["plan_h"], key)}</h2><div class="xy-planwrap">{plan_svg(feats, key)}</div><p class="caption">{zh_wrap(about[f"plan_cap_{L}"], key)}</p>{legend(key)}')
    out.append(f'<p><a href="{t["root"]}reconstruction/3d.html?cam={esc(about["cam"])}" class="btn btn-sm btn-dark">{t["in3d"]}</a></p></div></section>')
    for sec in about["sections"]:
        figs = "".join(figure(pics, q["id"], t, zh_wrap(q[f"cap_{L}"], key)) for q in sec.get("pictures", []) if pics.web(q["id"]))
        out.append(f'<section id="{esc(sec["id"])}" class="band xy-b"><div class="band-inner"><h2 class="xy-h2">{zh_wrap(sec[f"h_{L}"], key)}</h2>{paras(sec[L], key)}' + (f'<div class="xy-grid">{figs}</div>' if figs else "") + "</div></section>")
    out.append(f'<section id="sure" class="band xy-b"><div class="band-inner"><h2 class="xy-h2">{zh_wrap(t["counts_h"], key)}</h2><p>{zh_wrap(counts, key)}</p><p class="caption">{zh_wrap(kind_line, key)}</p>{paras(about[f"unknown_{L}"], key)}')
    out.append(sources_block(json.dumps(about, ensure_ascii=False), t) + "</div></section>")
    return "\n".join(out)


def main():
    about = json.load(open(ABOUT, encoding="utf-8"))
    feats = json.load(open(LAYERS / "surroundings_1860.geojson", encoding="utf-8"))["features"]
    pics = Pics()
    written = []
    write_if_changed(SITE / "around/plan.svg", plan_svg(feats, "en") + "\n")
    for key, base, other in (("en", SITE / "around", "../zh/around/"), ("zh", SITE / "zh/around", "../../around/")):
        t = T[key]
        L = "en" if key == "en" else "zh"
        page = shell(t, key, about[f"title_{L}"], about[f"desc_{L}"], other, page_body(key, about, feats, pics), t["root"])
        page = page.replace(f'href="{t["root"]}scenes/fonts.css"', f'href="{t["root"]}around/fonts.css"')
        write_if_changed(base / "index.html", page)
        written.append(page)
    for text in written:
        assert "research/" not in text and "/_local/" not in text and "/opt/" not in text, "a private path on the page"
        for pid in set(re.findall(r"reconstruction/photos/([PR]\d{4})", text)):
            row = pics.rows.get(pid) or pics.recons.get(pid)
            assert row["rights_class"] == "free", pid
    print(f"site/around/ and site/zh/around/: {len(feats)} objects on the plan; {len(written[0]) // 1024} kB EN")


if __name__ == "__main__":
    main()
