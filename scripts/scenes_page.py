"""The public scene pages: a hub listing every scene dossier, and a page for each of the best-documented scenes, in English and a Chinese draft. Built from the dossiers, so they stay in step. Idempotent: a second run changes nothing.

  uv run python scripts/scenes_page.py        (after scenes_dossiers.py and photos_catalog.py)

Reads research/scenes/ (about.json: `public` marks the scenes with a page of their own; views.csv, best.csv, digs.csv, halls.csv, <ID>-<slug>/dimensions.json), research/buildings.csv, research/photos/catalog.csv, research/reconstructions/catalog.csv, research/sources.md, research/layers/water_1860, walls_1860, scenes_1860, and the web copies in site/reconstruction/photos/.
Writes site/scenes/index.html (the hub, every dossier with its summary; the panel links to its anchors), site/scenes/<ID>/index.html for each public scene, site/scenes/keyplan.svg (our own traced layers only), and the same under site/zh/scenes/. Free pictures only, by the web copies; a research-only picture or reconstruction is a link card (asserted). No file outside site/ is referenced.
"""

import csv
import html
import json
import re
from pathlib import Path

from PIL import Image
from shapely.geometry import LineString

ROOT = Path(__file__).resolve().parent.parent
SC = ROOT / "research/scenes"
SITE = ROOT / "site"
PHOTOS = SITE / "reconstruction/photos"
LAT_M, LON_M = 111034.0, 85276.0
BBOX = (116.2800, 39.9975, 116.3180, 40.0150)
GALLERY_MAX = 6
LINKS_MAX = 8
CJK = re.compile(r"([㐀-鿿]+)")
GARDEN_ORDER = [("Yuanming Yuan", "圆明园 Yuanming Yuan"), ("Changchun Yuan", "长春园 Changchun Yuan"), ("Qichun Yuan", "绮春园 Qichun Yuan")]
VIEW_ORDER = ["album", "woodcut", "gouache", "1887", "yangshilei", "tangyang", "ruin", "today", "aerial", "detail"]

T = {
    "en": dict(
        lang="en", root="../", enter="Enter the reconstruction", home_lang="zh-Hans", nav_aria="Language",
        hub_title="The scenes of 圆明园 Yuanmingyuan, one by one · dossiers", hub_desc="Every scene and compound of the Old Summer Palace outside the European palaces, as far as the evidence goes: the 1744 album, the Qing texts and plans, what survives, what is known of their sizes.",
        hub_eyebrow="The three gardens · scene by scene", hub_h1=("圆明园", "Yuanmingyuan", "The scenes, one by one"),
        plan="The scenes on our plan", plan_cap="Outlines of the scenes as our plan readers drew them on the Qing plan S01 (image courtesy of the Princeton University Art Museum), with the water traced from it. Red: a page of its own. Click a name.",
        garden_h="Scenes and compounds", read="Read the dossier", in3d="See it in the 3D view", counts="{pics} pictures ({free} free) · {texts} texts and drawings · {figs} figures of size",
        what="What it was", scene="The leaf of 1744, its poem and preface", later="How it changed before 1860", halls="Building by building", interior="Inside", setting="The garden around it", survives="What survives", digs="Excavations and surveys", recons="Reconstructions by others", recons_note="Modern interpretation, not evidence, and never a source for a size or a position here.", dims="What is known of its size", dims_more="All {n} figures", pictures="The pictures", linkcards="Not ours to copy, at the holder", view_at="View at", more_in_panel="Every picture, text and drawing, hall by hall, is in the 3D view's panel.", unnamed="and {n} buildings drawn on the plan without a name", none_digs="No excavation or survey of its remains found in what we read.", hall_cols=["Hall", "Bays", "Roof", "Storeys", "Faces", "Sources"], col=["Part", "What", "Size", "How", "Grade", "Source"],
        method={"a": "a survey or Qing drawing", "b": "b plan or ruin", "c": "c painting, by module", "d": "d photograph", "e": "e no survey"}, extract="search extract", credits="Sources and image credits", sources_h="Sources cited on this page", footer="<span lang=\"zh-Hans\">圆明园</span> Yuanmingyuan · a Yaga.sh experiment", draft="", back="All scenes",
        view={"album": "The album of 1744", "woodcut": "The woodcuts of 1745", "gouache": "The gouaches, 1750-92", "1887": "The lithograph of 1887", "yangshilei": "Qing drawings", "tangyang": "Card models", "ruin": "Ruins, 1860-1940s", "today": "Today", "aerial": "From above", "detail": "Details", "other": "Other pictures"},
        wave="Wave {w}", summary_missing="Summary not written yet; the dossier lists what the catalogues hold.",
    ),
    "zh": dict(
        lang="zh-Hans", root="../../", enter="进入复原", home_lang="en", nav_aria="语言",
        hub_title="圆明园各景逐一考 · 圆明园复原", hub_desc="西洋楼以外圆明园各景与各组建筑的资料汇编：1744年四十景图、清代文献与样式雷图、现存遗迹、已知尺寸。",
        hub_eyebrow="圆明三园 · 逐景", hub_h1=("圆明园", "Yuanmingyuan", "各景逐一考"),
        plan="平面示意", plan_cap="各景轮廓为我们据清代地盘图S01所描（图像由普林斯顿大学艺术博物馆提供），水面亦据该图描绘。红色为有专页之景。点击名称。",
        garden_h="各景与建筑群", read="阅读专页", in3d="在三维视图中查看", counts="图像{pics}幅（可公开{free}幅）· 文献与图档{texts}条 · 尺寸数据{figs}个",
        what="概况", scene="1744年四十景图及御制诗序", later="1860年以前的变化", halls="逐座建筑", interior="室内", setting="园林环境", survives="现存", digs="考古与勘测", recons="他人的复原", recons_note="现代诠释，不是证据，本项目不据以定尺寸或位置。", dims="已知尺寸", dims_more="全部{n}个数字", pictures="图像", linkcards="版权所限，请至收藏方查看", view_at="查看：", more_in_panel="各建筑的全部图像与文献见三维视图的资料面板。", unnamed="另有{n}座地盘图上未注名称的建筑", none_digs="我们读到的资料中未见其遗址的发掘或勘测。", hall_cols=["建筑", "开间", "屋顶", "层数", "朝向", "来源"], col=["部位", "项目", "尺寸", "方法", "等级", "来源"],
        method={"a": "a 测绘或清代图档", "b": "b 地盘图或遗址", "c": "c 绘画按模数", "d": "d 照片", "e": "e 无测绘依据"}, extract="仅见搜索摘要", credits="资料来源与图片版权（英文）", sources_h="本页引用的资料", footer="圆明园 · a Yaga.sh experiment", draft="中文为草稿，尚未经母语者审读；表格、图片说明和多数段落暂为英文。", back="全部各景",
        view={"album": "1744年四十景图", "woodcut": "1745年木刻", "gouache": "1750至1792年水粉", "1887": "1887年石印本", "yangshilei": "清代图档", "tangyang": "烫样", "ruin": "1860至1940年代废墟", "today": "今日", "aerial": "俯视", "detail": "细部", "other": "其他图像"},
        wave="第{w}批", summary_missing="摘要尚未撰写；专题资料见英文档案。",
    ),
}


def rd(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def esc(text):
    return html.escape(str(text or ""), quote=True)


def zh_wrap(text, lang):
    """English pages mark their Chinese, so it takes the Chinese font."""
    safe = esc(text)
    return safe if lang != "en" else CJK.sub(r'<span lang="zh-Hans">\1</span>', safe)


def paras(text, lang):
    return "".join(f"<p>{zh_wrap(p, lang)}</p>" for p in re.split(r"\n\s*\n", text.strip()) if p.strip())


def first_sentences(text, n=2):
    parts = re.split(r"(?<=[.。])\s+(?=[A-Z“\"(])", re.sub(r"\s+", " ", text.strip()))
    return " ".join(parts[:n])


def xy(lon, lat):
    return (lon - BBOX[0]) * LON_M, (BBOX[3] - lat) * LAT_M


def ring_path(ring, tolerance=4.0):
    """A ring in plan metres, simplified to about `tolerance` m so the plan stays light."""
    line = LineString([xy(*p) for p in ring]).simplify(tolerance)
    pts = list(line.coords)
    if len(pts) < 3:
        return ""
    return "M" + "L".join(f"{x:.0f} {y:.0f}" for x, y in pts) + "Z"


def key_plan(about, rows, href):
    w, h = xy(BBOX[2], BBOX[1])
    parts = [f'<svg class="xy-plan sc-plan" viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Plan of the three gardens with the scenes that have a dossier"><rect width="{w:.0f}" height="{h:.0f}" fill="#221C16"/>']
    d = []
    for f in json.load(open(ROOT / "research/layers/water_1860.geojson", encoding="utf-8"))["features"]:
        g = f["geometry"]
        for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            d.append(ring_path(poly[0], 5.0))
    parts.append(f'<path d="{"".join(d)}" fill="#2C4650"/>')
    d = []
    for f in json.load(open(ROOT / "research/layers/walls_1860.geojson", encoding="utf-8"))["features"]:
        if f["geometry"]["type"] == "LineString":
            d.append("M" + "L".join(f"{x:.0f} {y:.0f}" for x, y in LineString([xy(*p) for p in f["geometry"]["coordinates"]]).simplify(4.0).coords))
    parts.append(f'<path d="{"".join(d)}" fill="none" stroke="#54483B" stroke-width="3"/>')
    plain, public = [], []
    for f in json.load(open(ROOT / "research/layers/scenes_1860.geojson", encoding="utf-8"))["features"]:
        sid = f["properties"]["id"]
        if sid not in about:
            continue
        g = f["geometry"]
        for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            (public if about[sid].get("public") else plain).append(ring_path(poly[0], 4.0))
    parts.append(f'<path d="{"".join(plain)}" fill="#5B4A39" fill-opacity="0.75" stroke="#8A735B" stroke-width="2"/>')
    parts.append(f'<path d="{"".join(public)}" fill="#E0553A" fill-opacity="0.85" stroke="#F5EEE2" stroke-width="2"/>')
    parts.append('<g font-family="Noto Serif SC, Songti SC, serif" text-anchor="middle" fill="#F5EEE2">')
    for sid, a in about.items():
        r = rows[sid]
        if not r["lat"] or not a["zh"]:
            continue
        x, y = xy(float(r["lon"]), float(r["lat"]))
        size = 46 if a.get("public") else 30
        parts.append(f'<a href="{href(sid)}"><text x="{x:.0f}" y="{y:.0f}" font-size="{size}" stroke="#17130F" stroke-width="{size / 5:.0f}" paint-order="stroke">{esc(a["zh"])}</text></a>')
    parts.append(f'</g><g font-family="Geist Mono, monospace" font-size="34" fill="#A1927D"><path d="M{w - 640:.0f} {h - 50:.0f}h500" stroke="#A1927D" stroke-width="6"/><text x="{w - 640:.0f}" y="{h - 70:.0f}">500 m</text><text x="{w - 90:.0f}" y="{h - 40:.0f}">N ↑</text></g></svg>')
    return "".join(parts)


class Pics:
    def __init__(self):
        self.rows = {p["photo_id"]: p for p in rd(ROOT / "research/photos/catalog.csv")}
        self.recons = {r["recon_id"]: r for r in rd(ROOT / "research/reconstructions/catalog.csv")}
        self.size = {}

    def web(self, pid):
        p = self.rows.get(pid) or self.recons.get(pid)
        return bool(p) and p["rights_class"] == "free" and (PHOTOS / f"{pid}.jpg").exists() and p.get("relation", "self") == "self"

    def dims(self, pid):
        if pid not in self.size:
            with Image.open(PHOTOS / f"{pid}.jpg") as im:
                self.size[pid] = im.size
        return self.size[pid]


def figure(pics, pid, t, caption, big=False):
    p = pics.rows.get(pid) or pics.recons[pid]
    assert pics.web(pid), pid
    w, h = pics.dims(pid)
    root = t["root"]
    full, thumb = f"{root}reconstruction/photos/{pid}.jpg", f"{root}reconstruction/photos/{pid}_t.jpg"
    has_thumb = (PHOTOS / f"{pid}_t.jpg").exists()
    src = full if big or not has_thumb else thumb
    size = "(max-width: 860px) 100vw, 1000px" if big else "(max-width: 860px) 50vw, 280px"
    srcset = f' srcset="{thumb} 400w, {full} {w}w" sizes="{size}"' if has_thumb else ""
    return f'<figure class="xy-fig{" big" if big else ""}"><a href="{full}"><img src="{src}"{srcset} width="{w}" height="{h}" loading="lazy" decoding="async" alt="{esc(p["title"])[:140]}"></a><figcaption>{caption}<span class="xy-credit">{esc(p["attribution"])}</span></figcaption></figure>'


def caption_of(p, view, lang):
    date = esc(re.sub(r"\s*\(.*$", "", p.get("date") or p.get("year") or ""))[:34]
    who = esc(re.sub(r"\s*\(.*$", "", p.get("creator") or p.get("author") or ""))[:40]
    meta = " · ".join(x for x in (who, date) if x)
    if lang == "en" and view and view.get("visible_part"):
        return f"<b>{zh_wrap(view['visible_part'][:160], lang)}</b> <span class=\"xy-meta\">{meta}</span>"
    title = re.split(r"\s*\(", p["title"])[0][:90]
    return f'<b>{zh_wrap(title, lang)}</b> <span class="xy-meta">{zh_wrap(meta, lang)}</span>'


def card(title, date, url, t, lang):
    host = re.sub(r"^www\.", "", re.sub(r"^https?://([^/]+).*", r"\1", url))
    return f'<li><span>{zh_wrap(title[:120], lang)}<span class="xy-meta"> {esc(date[:24])}</span></span> <a href="{esc(url)}" rel="noopener noreferrer" target="_blank">{t["view_at"]} {esc(host)}</a></li>'


def ties(text):
    out = {}
    for item in filter(None, (text or "").split(";")):
        bits = item.split(":")
        if bits[0] != "GARDEN":
            out[bits[0]] = bits[1] if len(bits) > 1 else "likely"
    return out


def dim_table(figures, t, lang):
    keys = [d for d in figures if d["key"]]
    rest = [d for d in figures if not d["key"]]
    fn = lambda rows: '<div class="xy-tablewrap"><table class="xy-dim"><thead><tr>' + "".join(f"<th>{c}</th>" for c in t["col"]) + "</tr></thead><tbody>" + "".join(f'<tr><td>{zh_wrap(d["part"], lang)}</td><td>{esc(d["label"])}</td><td class="num">{d["value"]:g} {esc(d["unit"])}{" ± " + format(d["err"], "g") if d["err"] else ""}</td><td>{t["method"].get(d["method"], d["method"])}</td><td>{d["confidence"]}</td><td class="src">{esc(d["source"].replace(";", ", "))}{", " + zh_wrap(d["locator"], lang) if d["locator"] else ""}{", " + t["extract"] if d["snippet"] else ""}</td></tr>' for d in rows) + "</tbody></table></div>"
    out = [fn(keys[:14] if keys else figures[:14])]
    remaining = (keys[14:] + rest) if keys else figures[14:]
    if remaining:
        out.append(f'<details class="xy-more"><summary>{t["dims_more"].format(n=len(figures))}</summary>{fn(remaining)}</details>')
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
            lang = "en" if t["lang"] == "en" else "zh"
            items.append(f'<li><b>{s}</b> ' + (f'<a href="{esc(url)}" rel="noopener noreferrer" target="_blank">{zh_wrap(name, lang)}</a>' if url else zh_wrap(name, lang)) + "</li>")
    return f'<details class="xy-more"><summary>{t["sources_h"]} ({len(items)})</summary><ul class="xy-sources">{"".join(items)}</ul></details>'


def shell(t, key, title, desc, other_href, body, depth_root):
    root = depth_root
    lang_nav = f'<nav class="lang" aria-label="{t["nav_aria"]}"><b aria-current="true">EN</b><a href="{other_href}" hreflang="zh-Hans" lang="zh-Hans">中文</a></nav>' if key == "en" else f'<nav class="lang" aria-label="{t["nav_aria"]}"><a href="{other_href}" hreflang="en" lang="en">EN</a><b aria-current="true">中文</b></nav>'
    brand = '<span lang="zh-Hans">圆明园</span> Yuanmingyuan' if key == "en" else '<span lang="zh-Hans">圆明园</span>'
    home = root if key == "en" else f"{root}zh/"
    return f'''<!doctype html>
<html lang="{t["lang"]}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  <link rel="icon" href="{root}favicon.ico" sizes="32x32">
  <link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="{root}apple-touch-icon.png">
  <link rel="alternate" hreflang="{t["home_lang"]}" href="{other_href}">
  <link rel="stylesheet" href="{root}styles.css">
  <link rel="stylesheet" href="{root}scenes/fonts.css">
</head>
<body>
  <div class="yaga-bar"><div class="yaga-bar-inner"><a class="yaga-bar-link" href="https://www.yaga.sh"><svg class="yaga-bar-arrow" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 4L6 8l4 4"/></svg><img class="yaga-bar-mark" src="{root}assets/yaga-mark-dark.webp" width="128" height="128" alt=""><span>Back to <strong>yaga.sh</strong></span></a></div></div>
  <header class="site-header"><div class="site-header-inner">
    <a href="{home}" class="brand"><img class="brand-mark" src="{root}assets/mark.svg" width="28" height="28" alt=""><span class="brand-name">{brand}</span></a>
    <div class="header-right">{lang_nav}<a href="{root}reconstruction/3d.html" class="btn btn-dark btn-sm">{t["enter"]}</a></div>
  </div></header>
  <main>
{body}
    <footer class="band"><div class="contact-inner">
      <p class="credits-link"><a href="{root}credits.html">{t["credits"]}</a></p>
      <div class="footer-row"><span class="footer-brand"><span>{t["footer"]}</span></span><span class="copyright">© 2026 · yaga.sh</span></div>
    </div></footer>
  </main>
</body>
</html>
'''


def scene_page(key, sid, a, rows, children, halls, views, best, digs, sheet, pics, links):
    t = T[key]
    lang = "en" if key == "en" else "zh"
    root = t["root"] + "../"
    tt = dict(t, root=root)
    r = rows[sid]
    out = [f'<section id="top" class="band xy-intro"><div class="band-inner">']
    out.append(f'<p class="xy-note"><a href="../">{t["back"]}</a></p>')
    out.append(f'<div class="eyebrow"><span class="eyebrow-bar"></span>{zh_wrap(GARDEN_NAME[r["garden"]], lang)} · {sid}</div>')
    out.append(f'<h1 class="xy-h1"><span class="title-zh" lang="zh-Hans">{esc(a["zh"])}</span><span class="title-pinyin">{esc(a["pinyin"])}</span><span class="title-en">{esc(a["en"]) if lang == "en" else ""}</span></h1>')
    if t["draft"]:
        out.append(f'<div class="tag">{t["draft"]}</div>')
    out.append(f'<div class="actions"><a href="{root}reconstruction/3d.html?b={sid}" class="btn btn-dark">{t["in3d"]}</a></div>')
    # the hero: the album leaf, else the best free picture
    scene_views = [v for v in views if v["id"].split("-")[0] == sid]
    ranked = [b["ref"] for b in sorted((b for b in best if b["id"] == sid), key=lambda b: int(b["rank"]))]
    leaf = f"P{int(sid[2:]):04d}" if sid.startswith("YM") and int(sid[2:]) <= 40 else ""
    hero = next((p for p in [leaf] + ranked if p and pics.web(p)), "")
    if hero:
        hp = pics.rows[hero]
        out.append('<div class="xy-plates sc-hero">' + figure(pics, hero, tt, caption_of(hp, None, lang), big=True) + "</div>")
    out.append("</div></section>")
    # text
    out.append('<section class="band xy-b"><div class="band-inner"><div class="xy-text">')
    for field, head in (("what", t["what"]), ("scene", t["scene"]), ("later", t["later"])):
        text = a.get(f"{field}_{lang}") or (a.get(f"{field}_en") if lang == "zh" and field != "what" else "")
        if lang == "zh" and field == "what" and not text:
            text = a.get("what_en", "")
        if text:
            out.append(f"<h3>{head}</h3>{paras(text, 'en' if not a.get(f'{field}_{lang}') else lang)}")
    out.append("</div>")
    # building by building: the named rows
    named = [c for c in children.get(sid, []) if rows[c]["name_zh"]]
    unnamed = len(children.get(sid, [])) - len(named)
    if named:
        out.append(f'<h3 class="xy-sub">{t["halls"]}</h3><div class="xy-tablewrap"><table class="xy-dim"><thead><tr>' + "".join(f"<th>{c}</th>" for c in t["hall_cols"]) + "</tr></thead><tbody>")
        for c in named:
            row = rows[c]
            hs = [h for h in halls if h["id"] == c]
            pick = lambda f, fallback="": next((h[f] for h in sorted(hs, key=lambda h: {"A": 0, "B": 1, "C": 2}.get(h["confidence"], 3)) if h[f].strip()), fallback)
            srcs = sorted({h["source_id"] for h in hs if h["source_id"]} | set(filter(None, row["sources"].split(";"))), key=lambda s: int(s[1:]) if s[1:].isdigit() else 0)[:5]
            out.append(f'<tr><td><span lang="zh-Hans">{esc(row["name_zh"])}</span> {esc(row["name_pinyin"])}</td><td{' class="num"' if len(pick("bays", row["bays"])) <= 6 else ""}>{zh_wrap(pick("bays", row["bays"]), lang)}</td><td>{zh_wrap(pick("roof", row["roof"]), lang)}</td><td{' class="num"' if len(pick("storeys", row["storeys"])) <= 6 else ""}>{zh_wrap(pick("storeys", row["storeys"]), lang)}</td><td>{esc(pick("faces"))}</td><td class="src">{esc(", ".join(srcs))}</td></tr>')
        out.append("</tbody></table></div>")
        if unnamed:
            out.append(f'<p class="xy-note">{t["unnamed"].format(n=unnamed)}</p>')
    # pictures by view
    mine = {}
    for cid in [sid] + children.get(sid, []):
        for p in pics.rows.values():
            if p["relation"] == "self" and p["source_url"].startswith("http") and cid in ties(p["shows"]) and ties(p["shows"])[cid] != "guess":
                mine.setdefault(p["photo_id"], p)
    vmap = {v["photo_id"]: v for v in scene_views}
    grouped, cards = {}, []
    for pid, p in mine.items():
        if pid == hero:
            continue
        v = vmap.get(pid)
        kind = v["view"] if v and v["view"] in VIEW_ORDER else ("today" if p["kind"] == "photo" and (p["date_from"] or "0")[:4] >= "1990" else "ruin" if p["kind"] == "photo" else "other")
        if pics.web(pid):
            grouped.setdefault(kind, []).append(({"high": 0, "medium": 1, "low": 2}.get(v["reliability"], 3) if v else 4, pid, v))
        elif p["rights_class"] != "free":
            cards.append(p)
    if grouped or cards:
        out.append(f'<h3 class="xy-sub">{t["pictures"]}</h3>')
    for kind in VIEW_ORDER + ["other"]:
        items = sorted(grouped.get(kind, []), key=lambda x: (x[0], x[1]))[:GALLERY_MAX]
        if items:
            out.append(f'<h4 class="xy-side">{t["view"][kind]}</h4><div class="xy-grid">' + "".join(figure(pics, pid, tt, caption_of(pics.rows[pid], v, lang)) for _, pid, v in items) + "</div>")
    if cards:
        out.append(f'<h4 class="xy-side">{t["linkcards"]}</h4><ul class="xy-cards">' + "".join(card(p["title"], p["date"], p["source_url"], t, lang) for p in sorted(cards, key=lambda p: p["photo_id"])[:LINKS_MAX]) + "</ul>")
        links |= {p["photo_id"] for p in cards}
    out.append(f'<p class="xy-note"><a href="{root}reconstruction/3d.html?b={sid}">{t["more_in_panel"]}</a></p>')
    # interior, setting, survives
    out.append('<div class="xy-text">')
    for field, head in (("interior", t["interior"]), ("setting", t["setting"]), ("survives", t["survives"])):
        text = a.get(f"{field}_{lang}") or a.get(f"{field}_en", "")
        if text:
            out.append(f"<h3>{head}</h3>{paras(text, lang if a.get(f'{field}_{lang}') else 'en')}")
    out.append("</div>")
    own_digs = [d for d in digs if d["id"].split("-")[0] == sid]
    out.append(f'<h3 class="xy-sub">{t["digs"]}</h3>')
    if own_digs:
        out.append('<ul class="xy-frag">' + "".join(f'<li><b>{esc(d["year"])}{", " + zh_wrap(d["by"], lang) if d["by"] else ""}</b><br>{zh_wrap(d["what_found"], lang)} <span class="xy-meta">{esc(d["source_id"].replace(";", ", "))}{", " + t["extract"] if d["status"] == "snippet" else ""}</span></li>' for d in own_digs) + "</ul>")
    else:
        out.append(f'<p class="xy-note">{t["none_digs"]}</p>')
    # reconstructions by others
    recs = {}
    for cid in [sid] + children.get(sid, []):
        for rr in pics.recons.values():
            if cid in ties(rr["shows"]):
                recs.setdefault(rr["recon_id"], rr)
    if recs:
        out.append(f'<h3 class="xy-sub">{t["recons"]}</h3><p class="xy-note">{t["recons_note"]}</p>')
        free = [rid for rid in sorted(recs) if pics.web(rid)][:GALLERY_MAX]
        if free:
            out.append('<div class="xy-grid">' + "".join(figure(pics, rid, tt, caption_of(recs[rid], None, lang)) for rid in free) + "</div>")
        rest = [rr for rid, rr in sorted(recs.items()) if rid not in free and rr["link"].startswith("http")][:LINKS_MAX]
        if rest:
            out.append('<ul class="xy-cards">' + "".join(card(f'{rr["title"]} ({rr["author"] or rr["institution"]}, {rr["kind"]})', rr["year"], rr["link"], t, lang) for rr in rest) + "</ul>")
    # dimensions
    if sheet["figures"]:
        out.append(f'<h3 class="xy-sub">{t["dims"]}</h3>' + dim_table(sheet["figures"], t, lang))
    body = "".join(out)
    out.append(sources_block(body, t) + "</div></section>")
    return "".join(out)


GARDEN_NAME = {"Yuanming Yuan": "圆明园 Yuanming Yuan", "Changchun Yuan": "长春园 Changchun Yuan", "Qichun Yuan": "绮春园 Qichun Yuan"}


def hub(key, about, rows, sheets, pics, counts, plan):
    t = T[key]
    lang = "en" if key == "en" else "zh"
    root = t["root"]
    out = [f'<section id="top" class="band xy-intro"><div class="band-inner">']
    out.append(f'<div class="eyebrow"><span class="eyebrow-bar"></span>{zh_wrap(t["hub_eyebrow"], lang)}</div>')
    h = t["hub_h1"]
    out.append(f'<h1 class="xy-h1"><span class="title-zh" lang="zh-Hans">{h[0]}</span><span class="title-pinyin">{h[1]}</span><span class="title-en">{zh_wrap(h[2], lang)}</span></h1>')
    if t["draft"]:
        out.append(f'<div class="tag">{t["draft"]}</div>')
    ov = about.get("_overview", {})
    for k in ("lead", "how"):
        text = ov.get(f"{k}_{lang}") or ov.get(f"{k}_en", "")
        if text:
            out.append(f'<p class="lead xy-lead">{zh_wrap(text, lang)}</p>')
    out.append(f'<h2 class="xy-subh">{t["plan"]}</h2><div class="xy-planwrap">{plan}</div><p class="caption">{zh_wrap(t["plan_cap"], lang)}</p>')
    pub = [s for s in about if not s.startswith("_") and about[s].get("public")]
    out.append(f'<nav class="xy-chips" aria-label="{t["read"]}">' + "".join(f'<a href="{s}/"><span lang="zh-Hans">{esc(about[s]["zh"])}</span>{" " + esc(about[s]["pinyin"]) if key == "en" else ""}</a>' for s in pub) + "</nav>")
    out.append("</div></section>")
    for garden, gname in GARDEN_ORDER:
        ids = [s for s in about if not s.startswith("_") and rows[s]["garden"] == garden]
        if not ids:
            continue
        out.append(f'<section class="band xy-b"><div class="band-inner"><div class="eyebrow"><span class="eyebrow-bar"></span>{t["garden_h"]}</div><h2 class="xy-h2">{zh_wrap(gname, lang)}</h2><ol class="sc-list">')
        for sid in sorted(ids, key=lambda s: (not about[s].get("public"), about[s]["wave"], s)):
            a = about[sid]
            summary = a.get(f"summary_{lang}") or (first_sentences(a["what_en"]) if a["what_en"] else "") or (a.get("summary_en") if lang == "zh" else "") or t["summary_missing"]
            c = counts[sid]
            links = [f'<a href="{sid}/" class="btn btn-sm btn-dark">{t["read"]}</a>'] if a.get("public") else []
            links.append(f'<a href="{root}reconstruction/3d.html?b={sid}" class="btn btn-sm xy-3d">{t["in3d"]}</a>')
            en = f'<span class="xy-en">{esc(a["en"])}</span>' if key == "en" and a["en"] else ""
            summary_lang = lang if a.get(f"summary_{lang}") else "en"
            out.append(f'<li id="{sid}" class="sc-item{" sc-public" if a.get("public") else ""}"><h3><span lang="zh-Hans">{esc(a["zh"])}</span> {esc(a["pinyin"])} <span class="xy-meta">{sid} · {t["wave"].format(w=a["wave"])}</span>{en}</h3><p{" lang=\"en\"" if summary_lang == "en" and lang != "en" else ""}>{zh_wrap(summary, "en")}</p><p class="xy-meta">{t["counts"].format(**c)}</p><div class="sc-links">{"".join(links)}</div></li>')
        out.append("</ol></div></section>")
    return "".join(out)


def write_if_changed(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")


def main():
    about = {k: v for k, v in json.load(open(SC / "about.json", encoding="utf-8")).items()}
    scenes = {k: v for k, v in about.items() if not k.startswith("_")}
    rows = {r["id"]: r for r in rd(ROOT / "research/buildings.csv")}
    children = {}
    for r in rows.values():
        if r["parent_id"]:
            children.setdefault(r["parent_id"], []).append(r["id"])
    halls, views, best, digs = (rd(SC / n) for n in ("halls.csv", "views.csv", "best.csv", "digs.csv"))
    sheets = {}
    for d in SC.glob("*/dimensions.json"):
        s = json.load(open(d, encoding="utf-8"))
        sheets[s["id"]] = s
    pics = Pics()
    evidence = rd(ROOT / "research/evidence/catalog.csv")
    counts = {}
    for sid in scenes:
        mine = {sid, *children.get(sid, [])}
        ps = {p["photo_id"]: p for p in pics.rows.values() if p["relation"] == "self" and p["source_url"].startswith("http") and set(ties(p["shows"])) & mine}
        es = {e["evidence_id"] for e in evidence if set(ties(e["shows"])) & mine}
        counts[sid] = dict(pics=len(ps), free=sum(p["rights_class"] == "free" for p in ps.values()), texts=len(es), figs=len(sheets[sid]["figures"]) if sid in sheets else 0)
    written = []
    for key, base in (("en", SITE / "scenes"), ("zh", SITE / "zh/scenes")):
        t = T[key]
        plan = key_plan(scenes, rows, lambda s: f"{s}/" if scenes[s].get("public") else f"#{s}")
        if key == "en":
            write_if_changed(base / "keyplan.svg", plan + "\n")
        other = "../zh/scenes/" if key == "en" else "../../scenes/"
        page = shell(t, key, t["hub_title"], t["hub_desc"], other, hub(key, about, rows, sheets, pics, counts, plan), t["root"])
        write_if_changed(base / "index.html", page)
        written.append(page)
        for sid, a in scenes.items():
            if not a.get("public"):
                continue
            links = set()
            body = scene_page(key, sid, a, rows, children, halls, views, best, digs, sheets[sid], pics, links)
            title = f"{a['zh']} {a['pinyin']}" + (f", {a['en']}" if key == "en" and a["en"] else "") + " · 圆明园 Yuanmingyuan"
            desc = first_sentences(a.get("what_en", ""), 1)[:200] if key == "en" else (a.get("what_zh", "")[:120] or title)
            other = f"../../zh/scenes/{sid}/" if key == "en" else f"../../../scenes/{sid}/"
            page = shell(t, key, title, desc, other, body, t["root"] + "../")
            write_if_changed(base / sid / "index.html", page)
            written.append(page)
    for text in written:
        assert "research/raw" not in text and "/_local/" not in text and "/opt/" not in text
        for pid in set(re.findall(r"reconstruction/photos/([PR]\d{4})", text)):
            row = pics.rows.get(pid) or pics.recons.get(pid)
            assert row["rights_class"] == "free", pid
    for base in (SITE / "scenes", SITE / "zh/scenes"):  # a scene no longer public loses its page
        for d in base.iterdir():
            if d.is_dir() and not scenes.get(d.name, {}).get("public"):
                for f in d.iterdir():
                    f.unlink()
                d.rmdir()
    images = {pid for text in written for pid in re.findall(r"reconstruction/photos/([PR]\d{4})", text)}
    print(f"hub + {sum(1 for a in scenes.values() if a.get('public'))} scene pages, EN and zh; {len(images)} images; hub {len(written[0]) // 1024} kB")


if __name__ == "__main__":
    main()
