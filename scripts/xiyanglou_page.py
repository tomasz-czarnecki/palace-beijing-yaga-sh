"""The public page on the European palaces, in English and a Chinese draft, with its key plan. Built from the dossiers, so it stays in step. Idempotent: a second run changes nothing.

  uv run python scripts/xiyanglou_page.py        (after xiyanglou_dossiers.py and photos_catalog.py)

Reads research/xiyanglou/ (about.json, views.csv, best.csv, rephoto.csv, fragments.csv, viewpoints.csv, <ID>-<slug>/dimensions.json), research/photos/catalog.csv, research/sources.md, research/layers/water_1860, research/layers/walls_1860, research/buildings.csv, site/reconstruction/data/halls_1860.geojson, and the web copies in site/reconstruction/photos/.
Writes site/xiyanglou/index.html, site/zh/xiyanglou/index.html, site/xiyanglou/keyplan.svg (our own traced layers only). Free pictures only, by the web copies; a research-only picture is a link card (asserted). No file outside site/ is referenced.
"""

import csv
import html
import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
XY = ROOT / "research/xiyanglou"
SITE = ROOT / "site"
PHOTOS = SITE / "reconstruction/photos"
LAT_M, LON_M = 111034.0, 85276.0
BBOX = (116.3006, 40.01075, 116.3120, 40.01345)
GALLERY_MAX = 6  # free pictures per heading: the rest are a click away in the panel
LINKS_MAX = 8  # link cards per building

T = {
    "en": dict(
        lang="en", title="西洋楼 Xiyang Lou, the European palaces of 圆明园 · Yuanmingyuan", desc="The European palaces of the Old Summer Palace, building by building: the engravings of the 1780s, the ruin photographs then and now, what is known of their sizes, what survives and where the fragments are.",
        root="../", other_lang_href="../zh/xiyanglou/", enter="Enter the reconstruction", brand_home="../", home_lang="zh-Hans", nav_aria="Language",
        eyebrow="长春园 Changchun Yuan · what the ruins hold", h1_top="西洋楼", h1_mid="Xiyang Lou", h1_en="The European palaces",
        plan="The strip on our plan", plan_cap="The arrows show where each of the 20 plates was drawn from, estimated from the plates themselves: read them as approximate. Click a name for its section. Traced from the Qing plan S01, image courtesy of the Princeton University Art Museum.",
        contents="The buildings", in3d="See it in the 3D view", what="What it was", after="After 1860", survives="What survives", fragments="Where the fragments are", engraving="The engraving", views="Pictures by side", then_now="Then and now", same_view={"exact": "the same view", "close": "nearly the same view", "rough": "roughly the same view"}, dims="What is known of its size", dims_more="All {n} figures", linkcards="Not ours to copy, at the holder", view_at="View at", more_in_panel="More pictures, and the texts, in the 3D view's panel.", plates_h="The plates", water_h="The water", survive_h="What is left", notxy_h="Stones that are not from these buildings", side={"Ruins today": "Ruins today", "South façade": "South façade", "North façade": "North façade", "East façade": "East façade", "West façade": "West façade", "Roof and fountains": "Roof and fountains", "Plans and views from above": "Plans and views from above", "Details and fragments": "Details and fragments", "Other pictures": "Other pictures"},
        col=["Part", "What", "Size", "How", "Grade", "Source"], method={"a": "a survey", "b": "b ruin or plan", "c": "c engraving", "d": "d photograph", "e": "e no survey"}, extract="search extract", credits="Sources and image credits", sources_h="Sources cited on this page", now_at="Now at", moved="Moved", footer="<span lang=\"zh-Hans\">圆明园</span> Yuanmingyuan · a Yaga.sh experiment", draft="", none_frag="No moved piece is documented for it in what we read.",
    ),
    "zh": dict(
        lang="zh-Hans", title="西洋楼：圆明园的欧式宫殿 · 圆明园复原", desc="圆明园西洋楼，逐栋介绍：1780年代铜版画、新旧废墟照片、已知尺寸、现存遗迹及流散石件去向。",
        root="../../", other_lang_href="../../xiyanglou/", enter="进入复原", brand_home="../", home_lang="en", nav_aria="语言",
        eyebrow="长春园 · 废墟之所存", h1_top="西洋楼", h1_mid="Xiyang Lou", h1_en="圆明园的欧式宫殿",
        plan="平面示意", plan_cap="箭头表示20幅铜版画的大致视点，系从画面本身估算，仅供参考。点击名称可跳至对应段落。据清代地盘图S01描绘，图像由普林斯顿大学艺术博物馆提供。",
        contents="各建筑", in3d="在三维视图中查看", what="概况", after="1860年以后", survives="现存", fragments="流散石件去向", engraving="铜版画", views="各面图像", then_now="新旧对比", same_view={"exact": "同一视角", "close": "视角接近", "rough": "视角大致相同"}, dims="已知尺寸", dims_more="全部{n}个数字", linkcards="版权所限，请至收藏方查看", view_at="查看：", more_in_panel="更多图片和文献见三维视图的资料面板。", plates_h="铜版画", water_h="水法", survive_h="现存遗迹", notxy_h="并非出自西洋楼的石件", side={"Ruins today": "今日遗址", "South façade": "南面", "North façade": "北面", "East façade": "东面", "West façade": "西面", "Roof and fountains": "屋顶与喷泉", "Plans and views from above": "平面与俯视", "Details and fragments": "细部与残件", "Other pictures": "其他图像"},
        col=["部位", "项目", "尺寸", "方法", "等级", "来源"], method={"a": "a 测绘", "b": "b 遗址或地盘图", "c": "c 铜版画", "d": "d 照片", "e": "e 无测绘依据"}, extract="仅见搜索摘要", credits="资料来源与图片版权（英文）", sources_h="本页引用的资料", now_at="现存于", moved="移动", footer="圆明园 · a Yaga.sh experiment", draft="中文为草稿，尚未经母语者审读；图片说明、部位名称和石件表暂为英文。", none_frag="我们读到的资料中未见其流散石件的记载。",
    ),
}
XY_SIDE = {"S": "South façade", "N": "North façade", "E": "East façade", "W": "West façade", "roof": "Roof and fountains", "fountain": "Roof and fountains", "aerial": "Plans and views from above", "detail": "Details and fragments", "fragment": "Details and fragments"}
XY_FRONT = {"XY02": "E", "XY05": "W", "XY08": "W", "XY12": "W", "XY13": "W", "XY15": "W", "XY07": "N", "XY11": "N", "XY03": "N"}
LABEL_NUDGE = {"XY01": (-62, -6), "XY02": (-8, -14), "XY03": (74, -30), "XY04": (-50, -8), "XY05": (6, -16), "XY06": (0, -22), "XY07": (0, 28), "XY08": (0, -36), "XY09": (-44, -18), "XY10": (84, 34), "XY11": (0, 28), "XY12": (0, -26), "XY13": (0, 26), "XY14": (0, 2), "XY15": (6, -44)}
CJK = re.compile(r"([㐀-鿿]+)")


def rd(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def esc(text):
    return html.escape(str(text or ""), quote=True)


def zh_wrap(text, lang):
    """English pages mark their Chinese, so it takes the Chinese font."""
    safe = esc(text)
    return safe if lang != "en" else CJK.sub(r'<span lang="zh-Hans">\1</span>', safe)


def xy(lon, lat):
    return (lon - BBOX[0]) * LON_M, (BBOX[3] - lat) * LAT_M


def ring_path(ring):
    pts = [xy(*p) for p in ring]
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"


def key_plan(about, viewpoints, rows):
    w, h = xy(BBOX[2], BBOX[1])
    parts = [f'<svg class="xy-plan" viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Plan of the Xiyang Lou strip with the viewpoints of the plates"><rect width="{w:.0f}" height="{h:.0f}" fill="#221C16"/>']

    def inside(ring):
        return any(BBOX[0] <= x <= BBOX[2] and BBOX[1] <= y <= BBOX[3] for x, y in ring)

    d = []
    for f in json.load(open(ROOT / "research/layers/water_1860.geojson", encoding="utf-8"))["features"]:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            if inside(poly[0]):
                d.append(ring_path(poly[0][:: max(1, len(poly[0]) // 120)]))
    parts.append(f'<path d="{"".join(d)}" fill="#2C4650"/>')
    d = []
    for f in json.load(open(ROOT / "research/layers/walls_1860.geojson", encoding="utf-8"))["features"]:
        if f["geometry"]["type"] != "LineString":
            continue
        pts = f["geometry"]["coordinates"]
        if inside(pts):
            d.append("M" + "L".join(f"{xy(*p)[0]:.1f} {xy(*p)[1]:.1f}" for p in pts))
    parts.append(f'<path d="{"".join(d)}" fill="none" stroke="#54483B" stroke-width="1.6"/>')
    other, mine, pools, courts = [], [], [], []
    for f in json.load(open(SITE / "reconstruction/data/halls_1860.geojson", encoding="utf-8"))["features"]:
        ring, p = f["geometry"]["coordinates"][0], f["properties"]
        if not inside(ring):
            continue
        if p["building_id"].startswith("XY"):
            (courts if p.get("shape") == "court" else pools if p.get("shape") in ("pool", "basin") else mine).append(ring_path(ring))
        else:
            other.append(ring_path(ring))
    parts.append(f'<path d="{"".join(other)}" fill="#3A3026"/>')
    parts.append(f'<path d="{"".join(courts)}" fill="#3B4630"/>')
    parts.append(f'<path d="{"".join(pools)}" fill="#3C6776"/>')
    parts.append(f'<path d="{"".join(mine)}" fill="#E0553A"/>')
    parts.append('<g font-family="Geist Mono, monospace" font-size="9" text-anchor="middle">')
    for v in viewpoints:
        import math
        x0, y0 = xy(float(v["lon"]), float(v["lat"]))
        b = math.radians(float(v["bearing"]))
        length = min(float(v["dist_m"]) * 0.7, 28)
        x1, y1 = x0 + math.sin(b) * length, y0 - math.cos(b) * length
        ax, ay = math.sin(b - 2.6) * 6, -math.cos(b - 2.6) * 6
        cx, cy = math.sin(b + 2.6) * 6, -math.cos(b + 2.6) * 6
        parts.append(f'<path d="M{x0:.1f} {y0:.1f}L{x1:.1f} {y1:.1f}M{x1 + ax:.1f} {y1 + ay:.1f}L{x1:.1f} {y1:.1f}L{x1 + cx:.1f} {y1 + cy:.1f}" stroke="#8EA3C0" stroke-width="1.3" fill="none"/>')
        parts.append(f'<circle cx="{x0:.1f}" cy="{y0:.1f}" r="7" fill="#17130F" stroke="#8EA3C0"/><text x="{x0:.1f}" y="{y0 + 3.2:.1f}" fill="#F5EEE2">{v["plate"]}</text>')
    parts.append("</g>")
    parts.append('<g font-family="Noto Serif SC, Songti SC, serif" font-size="14" text-anchor="middle" fill="#F5EEE2">')
    for bid in [k for k in about if k.startswith("XY")]:
        r = rows[bid]
        x, y = xy(float(r["lon"]), float(r["lat"]))
        nx, ny = LABEL_NUDGE.get(bid, (0, 0))
        parts.append(f'<a href="#{bid}"><text x="{x + nx:.1f}" y="{y + ny:.1f}" stroke="#17130F" stroke-width="3" paint-order="stroke">{about[bid]["zh"]}</text></a>')
    parts.append(f'</g><g font-family="Geist Mono, monospace" font-size="10" fill="#A1927D"><path d="M{w - 150:.0f} {h - 14:.0f}h100" stroke="#A1927D" stroke-width="1.5"/><text x="{w - 150:.0f}" y="{h - 20:.0f}">100 m</text><text x="{w - 30:.0f}" y="{h - 12:.0f}">N ↑</text></g></svg>')
    return "".join(parts)


class Pics:
    def __init__(self):
        self.rows = {p["photo_id"]: p for p in rd(ROOT / "research/photos/catalog.csv")}
        self.size = {}

    def web(self, pid):
        p = self.rows[pid]
        return p["rights_class"] == "free" and (PHOTOS / f"{pid}.jpg").exists() and p["relation"] == "self"

    def dims(self, pid):
        if pid not in self.size:
            with Image.open(PHOTOS / f"{pid}.jpg") as im:
                self.size[pid] = im.size
        return self.size[pid]


def credit(p):
    return " · ".join(x for x in (p["attribution"],) if x)


def figure(pics, pid, t, caption, sizes="(max-width: 860px) 50vw, 280px", big=False):
    p = pics.rows[pid]
    assert pics.web(pid), pid
    w, h = pics.dims(pid)
    root = t["root"]
    full = f"{root}reconstruction/photos/{pid}.jpg"
    thumb = f"{root}reconstruction/photos/{pid}_t.jpg"
    src = full if big else thumb
    size = "(max-width: 860px) 100vw, 1000px" if big else sizes
    alt = esc(p["title"])[:140]
    return f'<figure class="xy-fig{" big" if big else ""}"><a href="{full}"><img src="{src}" srcset="{thumb} 400w, {full} {w}w" sizes="{size}" width="{w}" height="{h}" loading="lazy" decoding="async" alt="{alt}"></a><figcaption>{caption}<span class="xy-credit">{esc(credit(p))}</span></figcaption></figure>'


def caption_of(p, view, lang):
    date = esc(re.sub(r"\s*\(.*$", "", p["date"]))[:34]
    who = esc(re.sub(r"\s*\(.*$", "", p["creator"]))[:34]
    meta = " · ".join(x for x in (who, date) if x)
    if lang == "en" and view and view.get("visible_part"):
        return f"<b>{zh_wrap(view['visible_part'], lang)}</b> <span class=\"xy-meta\">{meta}</span>"
    return f'<span class="xy-meta">{zh_wrap(meta, lang)}</span>'


def section(bid, a, t, pics, views, rephoto, fragments, sheet, links):
    lang, root = ("en", t["root"]) if t["lang"] == "en" else ("zh", t["root"])
    side_text = t["side"]
    out = [f'<section id="{bid}" class="band xy-b"><div class="band-inner">']
    head_zh = f'<span lang="zh-Hans">{a["zh"]}</span> {a["pinyin"]}'
    out.append(f'<div class="eyebrow"><span class="eyebrow-bar"></span>{bid}</div><h2 class="xy-h2">{head_zh}<span class="xy-en">{esc(a["en"]) if lang == "en" else ""}</span></h2>')
    out.append(f'<a class="btn btn-sm xy-3d" href="{root}reconstruction/3d.html?b={bid}">{t["in3d"]}</a>')
    key = "en" if lang == "en" else "zh"
    out.append(f'<div class="xy-text"><h3>{t["what"]}</h3><p>{zh_wrap(a["what_" + key], lang)}</p><h3>{t["after"]}</h3><p>{zh_wrap(a["after_" + key], lang)}</p><h3>{t["survives"]}</h3><p>{zh_wrap(a["survives_" + key], lang)}</p></div>')
    # the plates first, large
    plate_ids = [f"P{40 + n:04d}" for n in a["plates"]]
    my_views = {v["photo_id"]: v for v in views if v["id"] == bid}
    for v in views:
        if v["id"].split("-")[0] == bid:
            my_views.setdefault(v["photo_id"], v)
    out.append(f'<h3 class="xy-sub">{t["engraving"]}</h3><div class="xy-plates">')
    for pid in plate_ids:
        p = pics.rows[pid]
        title = re.split(r"\s*\(", p["title"])[0]
        out.append(figure(pics, pid, t, f'<b><span lang="zh-Hans">{esc(title)}</span></b> <span class="xy-meta">1783-86</span>', big=True))
    out.append("</div>")
    # then and now
    pairs = [r for r in rephoto if r["id"].split("-")[0] == bid and pics.web(r["old"]) and pics.web(r["new"])]
    pairs.sort(key=lambda r: {"exact": 0, "close": 1, "rough": 2}.get(r["same_view"], 3))
    shown = set(plate_ids)
    if pairs:
        out.append(f'<h3 class="xy-sub">{t["then_now"]}</h3>')
        for r in pairs[:4]:
            old, new = pics.rows[r["old"]], pics.rows[r["new"]]
            what = f'<p class="xy-pair-note">{t["same_view"].get(r["same_view"], "")}{": " + zh_wrap(r["what_changed"], lang) if lang == "en" else ""}</p>'
            out.append('<div class="xy-pair">' + figure(pics, r["old"], t, caption_of(old, None, lang), sizes="(max-width: 860px) 50vw, 480px") + figure(pics, r["new"], t, caption_of(new, None, lang), sizes="(max-width: 860px) 50vw, 480px") + what + "</div>")
            shown |= {r["old"], r["new"]}
    # by side
    front = XY_SIDE[XY_FRONT.get(bid, "S")]
    order = [front] + [s for s in ("South façade", "North façade", "East façade", "West façade", "Roof and fountains", "Plans and views from above", "Details and fragments", "Ruins today") if s != front]
    grouped = {}
    rank = {"high": 0, "medium": 1, "low": 2}
    for pid, v in my_views.items():
        if pid in shown or not pics.web(pid):
            continue
        tie = {x.split(":")[0]: x.rsplit(":", 1)[1] for x in pics.rows[pid]["shows"].split(";") if x}
        if tie.get(v["id"]) == "guess" or tie.get(bid) == "guess":
            continue
        g = "Ruins today" if v["state"] == "today" else XY_SIDE.get(v["side"])
        if g:
            grouped.setdefault(g, []).append((rank.get(v["reliability"], 3), pid, v))
    if grouped:
        out.append(f'<h3 class="xy-sub">{t["views"]}</h3>')
    for g in order:
        rows = sorted(grouped.get(g, []), key=lambda x: (x[0], x[1]))[:GALLERY_MAX]
        if not rows:
            continue
        out.append(f'<h4 class="xy-side">{side_text[g]}</h4><div class="xy-grid">')
        for _, pid, v in rows:
            out.append(figure(pics, pid, t, caption_of(pics.rows[pid], v, lang)))
        out.append("</div>")
    out.append(f'<p class="xy-note"><a href="{root}reconstruction/3d.html?b={bid}">{t["more_in_panel"]}</a></p>')
    cards = [pics.rows[pid] for pid in my_views if pics.rows[pid]["rights_class"] != "free" and pics.rows[pid]["source_url"].startswith("http")]
    cards = sorted(cards, key=lambda p: (rank.get(my_views[p["photo_id"]]["reliability"], 3), p["photo_id"]))[:LINKS_MAX]
    if cards:
        out.append(f'<h4 class="xy-side">{t["linkcards"]}</h4><ul class="xy-cards">')
        for p in cards:
            host = re.sub(r"^www\.", "", re.sub(r"^https?://([^/]+).*", r"\1", p["source_url"]))
            links.add(p["photo_id"])
            out.append(f'<li><span>{zh_wrap(p["title"][:120], lang)}<span class="xy-meta"> {esc(p["date"][:24])}</span></span> <a href="{esc(p["source_url"])}" rel="noopener noreferrer" target="_blank">{t["view_at"]} {esc(host)}</a></li>')
        out.append("</ul>")
    # dimensions
    figures = sheet["figures"]
    keys = [d for d in figures if d["key"]]
    rest = [d for d in figures if not d["key"]]
    tablefn = lambda rows: '<div class="xy-tablewrap"><table class="xy-dim"><thead><tr>' + "".join(f"<th>{c}</th>" for c in t["col"]) + "</tr></thead><tbody>" + "".join(f'<tr><td>{zh_wrap(d["part"], lang)}</td><td>{esc(d["label"])}</td><td class="num">{d["value"]:g} {esc(d["unit"])}{" ± " + format(d["err"], "g") if d["err"] else ""}</td><td>{t["method"].get(d["method"], d["method"])}</td><td>{d["confidence"]}</td><td class="src">{esc(d["source"].replace(";", ", "))}{", " + zh_wrap(d["locator"], lang) if d["locator"] else ""}{", " + t["extract"] if d["snippet"] else ""}</td></tr>' for d in rows) + "</tbody></table></div>"
    if figures:
        out.append(f'<h3 class="xy-sub">{t["dims"]}</h3>')
        out.append(tablefn(keys[:14] if keys else figures[:14]))
        remaining = keys[14:] + rest
        if remaining:
            out.append(f'<details class="xy-more"><summary>{t["dims_more"].format(n=len(figures))}</summary>{tablefn(remaining)}</details>')
    # fragments
    frag = [f for f in fragments if f["id"].split("-")[0] == bid]
    out.append(f'<h3 class="xy-sub">{t["fragments"]}</h3>')
    if frag:
        out.append('<ul class="xy-frag">')
        for f in frag:
            place = " ".join(x for x in (f["now_at"], f["now_place_zh"] if lang == "zh" else "") if x)
            out.append(f'<li><b>{zh_wrap(f["what"], lang)}</b><br><span>{t["now_at"]}: {zh_wrap(place, lang)}.</span>{" " + t["moved"] + ": " + zh_wrap(f["moved"], lang) + "." if f["moved"] else ""} <span class="xy-meta">{esc(f["source_id"].replace(";", ", "))}, {esc(f["confidence"])}</span></li>')
        out.append("</ul>")
    else:
        out.append(f'<p class="xy-note">{t["none_frag"]}</p>')
    out.append("</div></section>")
    return "".join(out)


def sources_block(text, t):
    used = sorted(set(re.findall(r"\bS\d{2,3}\b", text)), key=lambda s: int(s[1:]))
    src = {}
    for line in (ROOT / "research/sources.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| (S\d+) \| ([^|]*)\|", line)
        if m:
            url = re.search(r"https?://[^\s|)]+", line)
            src[m[1]] = (re.split(r"(?<=[a-z0-9)])\. ", m[2].strip())[0][:170], url[0].rstrip(".,;") if url else "")
    items = []
    for s in used:
        if s in src:
            name, url = src[s]
            items.append(f'<li><b>{s}</b> ' + (f'<a href="{esc(url)}" rel="noopener noreferrer" target="_blank">{zh_wrap(name, t["lang"] == "en" and "en")}</a>' if url else zh_wrap(name, t["lang"] == "en" and "en")) + "</li>")
    return f'<details class="xy-more"><summary>{t["sources_h"]} ({len(items)})</summary><ul class="xy-sources">{"".join(items)}</ul></details>'


def page(key, plan, about, views, rephoto, fragments, sheets, pics, viewpoints):
    t = T[key]
    root = t["root"]
    ov = about["_overview"]
    lang = "en" if key == "en" else "zh"
    ids = [k for k in about if k.startswith("XY")]
    links = set()
    sections = [section(b, about[b], t, pics, views, rephoto, fragments, sheets[b], links) for b in ids]
    chips = "".join(f'<a href="#{b}"><span lang="zh-Hans">{about[b]["zh"]}</span>{" " + about[b]["pinyin"] if key == "en" else ""}</a>' for b in ids)
    other = [f for f in fragments if not f["id"].startswith("XY") and f["id"] != "GARDEN:ALL"]
    groupfrag = "".join(f'<li><b>{zh_wrap(f["what"], lang)}</b><br>{t["now_at"]}: {zh_wrap(" ".join(x for x in (f["now_at"], f["now_place_zh"] if key == "zh" else "") if x), lang)}. <span class="xy-meta">{esc(f["source_id"].replace(";", ", "))}, {esc(f["confidence"])}</span></li>' for f in other)
    intro = f'''<section id="top" class="band xy-intro"><div class="band-inner">
<div class="eyebrow"><span class="eyebrow-bar"></span>{zh_wrap(t["eyebrow"], lang)}</div>
<h1 class="xy-h1"><span class="title-zh" lang="zh-Hans">{t["h1_top"]}</span><span class="title-pinyin">{t["h1_mid"]}</span><span class="title-en">{zh_wrap(t["h1_en"], lang)}</span></h1>
{f'<div class="tag">{t["draft"]}</div>' if t["draft"] else ""}
<p class="lead xy-lead">{zh_wrap(ov["lead_" + key], lang)}</p>
<p class="lead xy-lead">{zh_wrap(ov["how_" + key], lang)}</p>
<div class="actions"><a href="{root}reconstruction/3d.html?b=XY09" class="btn btn-dark">{t["enter"]}</a></div>
<h2 class="xy-subh">{t["plan"]}</h2>
<div class="xy-planwrap">{plan}</div>
<p class="caption">{zh_wrap(t["plan_cap"], lang)}</p>
<nav class="xy-chips" aria-label="{t["contents"]}">{chips}</nav>
</div></section>
<section class="band paper"><div class="band-inner xy-cols">
<div><h3>{t["plates_h"]}</h3><p>{zh_wrap(ov["plates_" + key], lang)}</p></div>
<div><h3>{t["water_h"]}</h3><p>{zh_wrap(ov["water_" + key], lang)}</p></div>
<div><h3>{t["survive_h"]}</h3><p>{zh_wrap(ov["survive_" + key], lang)}</p></div>
</div></section>'''
    body = intro + "".join(sections)
    closing = f'<section class="band xy-b"><div class="band-inner"><h3 class="xy-sub">{t["fragments"]}: {t["notxy_h"] if False else ""}</h3><ul class="xy-frag">{groupfrag}</ul>{sources_block(body, t)}</div></section>'
    lang_nav = f'<nav class="lang" aria-label="{t["nav_aria"]}"><b aria-current="true">EN</b><a href="{t["other_lang_href"]}" hreflang="zh-Hans" lang="zh-Hans">中文</a></nav>' if key == "en" else f'<nav class="lang" aria-label="{t["nav_aria"]}"><a href="{t["other_lang_href"]}" hreflang="en" lang="en">EN</a><b aria-current="true">中文</b></nav>'
    brand = f'<span lang="zh-Hans">圆明园</span> Yuanmingyuan' if key == "en" else '<span lang="zh-Hans">圆明园</span>'
    home = root if key == "en" else f"{root}zh/"
    return f'''<!doctype html>
<html lang="{t["lang"]}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(t["title"])}</title>
  <meta name="description" content="{esc(t["desc"])}">
  <link rel="icon" href="{root}favicon.ico" sizes="32x32">
  <link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="{root}apple-touch-icon.png">
  <link rel="alternate" hreflang="{t["home_lang"]}" href="{t["other_lang_href"]}">
  <link rel="stylesheet" href="{root}styles.css">
  <link rel="stylesheet" href="{root}xiyanglou/fonts.css">
</head>
<body>
  <div class="yaga-bar"><div class="yaga-bar-inner"><a class="yaga-bar-link" href="https://www.yaga.sh"><svg class="yaga-bar-arrow" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 4L6 8l4 4"/></svg><img class="yaga-bar-mark" src="{root}assets/yaga-mark-dark.webp" width="128" height="128" alt=""><span>Back to <strong>yaga.sh</strong></span></a></div></div>
  <header class="site-header"><div class="site-header-inner">
    <a href="{home}" class="brand"><img class="brand-mark" src="{root}assets/mark.svg" width="28" height="28" alt=""><span class="brand-name">{brand}</span></a>
    <div class="header-right">{lang_nav}<a href="{root}reconstruction/3d.html" class="btn btn-dark btn-sm">{t["enter"]}</a></div>
  </div></header>
  <main>
{body}
{closing}
    <footer class="band"><div class="contact-inner">
      <p class="credits-link"><a href="{root}credits.html">{t["credits"]}</a></p>
      <div class="footer-row"><span class="footer-brand"><span>{t["footer"]}</span></span><span class="copyright">© 2026 · yaga.sh</span></div>
    </div></footer>
  </main>
</body>
</html>
'''


def write_if_changed(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")


def main():
    about = json.load(open(XY / "about.json", encoding="utf-8"))
    views, rephoto, fragments, viewpoints = rd(XY / "views.csv"), rd(XY / "rephoto.csv"), rd(XY / "fragments.csv"), rd(XY / "viewpoints.csv")
    rows = {r["id"]: r for r in rd(ROOT / "research/buildings.csv")}
    sheets = {}
    for d in XY.glob("XY*/dimensions.json"):
        s = json.load(open(d, encoding="utf-8"))
        sheets[s["id"]] = s
    pics = Pics()
    plan = key_plan(about, viewpoints, rows)
    write_if_changed(SITE / "xiyanglou/keyplan.svg", plan + "\n")
    en = page("en", plan, about, views, rephoto, fragments, sheets, pics, viewpoints)
    zh = page("zh", plan, about, views, rephoto, fragments, sheets, pics, viewpoints)
    for text in (en, zh):
        assert "research/raw" not in text and "/_local/" not in text and "/opt/" not in text
        for pid in set(re.findall(r"reconstruction/photos/(P\d{4})", text)):
            assert pics.rows[pid]["rights_class"] == "free", pid
    write_if_changed(SITE / "xiyanglou/index.html", en)
    write_if_changed(SITE / "zh/xiyanglou/index.html", zh)
    images = len(set(re.findall(r"reconstruction/photos/(P\d{4})", en)))
    per = {b: len(set(re.findall(r"reconstruction/photos/(P\d{4})", en.split(f'id="{b}"')[1].split('<section id="')[0]))) for b in about if b.startswith("XY")}
    print(f"site/xiyanglou/index.html {len(en) // 1024} kB, {images} images, keyplan {len(plan) // 1024} kB; per building {per}; zh {len(zh) // 1024} kB")


if __name__ == "__main__":
    main()
