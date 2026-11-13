"""Write the public tour pages site/tour.html (/tour) and site/zh/tour.html (/zh/tour) from site/reconstruction/3d.html (Round 32).

  uv run python tools/tour_page.py [--check]

The tour is the 3D view itself: the same markup, the same scripts (3d.js, which fetches tour3d.js and data/tour.json for a body
data-tour="page"), so nothing of the viewer is forked. This script only swaps the head (title, description, the share card,
canonical and language links), marks the body as the tour page (no dev header, no cog: the tour draws its own chrome) and puts
the poster in front: an AI picture of the gardens, labelled, with the title and a "Begin the tour" button (a gesture, so full
screen can follow). The gardens load behind the poster. Both pages keep 3d.html's <base href="/reconstruction/">, so they work at
/tour on the preview (:8790), tools/serve_local.py and a host with clean URLs alike (site/vercel.json cleanUrls: no rewrite needed).
Never hand-edit the two pages; rerun this after any change to 3d.html. --check exits 1 if they are stale (tools/tour_test.mjs runs it).
"""

import argparse
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
SRC = SITE / "reconstruction/3d.html"
# No domain yet (no host, CLAUDE.md "Website and git"): the share card's picture and canonical are root paths until there is one.
SITE_URL = ""
POSTER = "assets/gallery/hero-1-overview"

TEXT = {
    "en": {
        "out": SITE / "tour.html", "lang": "en", "path": "/tour",
        "title": "A guided tour · 圆明园 Yuanmingyuan before October 1860",
        "desc": "A live, guided tour of the 3D reconstruction of 圆明园 Yuanmingyuan, the Old Summer Palace in Beijing, as it stood before October 1860: sixteen chapters, about five minutes, every building graded by its sources.",
        "og": "圆明园 Yuanmingyuan: a guided tour of the reconstruction",
        "sub": "before October 1860, a reconstruction",
        "line": "A live tour of the 3D reconstruction, about five minutes. It plays here, in your browser.",
        "begin": "Begin the tour",
        "note": "The gardens are loading behind this picture; on a slow connection the first chapter may wait a moment.",
        "alt": "AI picture: a vast garden of lakes, islands and halls among trees seen from high above in low golden light.",
        "ai": "AI visualisation based on our 3D model, not a historical photograph",
        "home": ("../", "Homepage"), "view": ("3d.html", "3D view"), "other": ("../zh/tour.html", "中文", "zh-Hans"),
        "aria": "Start of the tour",
    },
    "zh": {
        "out": SITE / "zh/tour.html", "lang": "zh-Hans", "path": "/zh/tour",
        "title": "圆明园导览 · 1860年10月以前的圆明园",
        "desc": "圆明园三维复原的实时导览：1860年10月以前的圆明园，十六章，约五分钟，每座建筑都按史料分级。（中文草稿）",
        "og": "圆明园：复原导览",
        "sub": "1860年10月以前的复原",
        "line": "三维复原的实时导览，约五分钟，在你的浏览器中播放。",
        "begin": "开始导览",
        "note": "园林正在这张图后面载入；网速较慢时，第一章可能需要稍等。",
        "alt": "AI图像：从高空俯瞰的广阔园林，湖泊、岛屿和殿宇掩映在树木间，金色的低角度光线。",
        "ai": "基于我们三维模型的AI图像，不是历史照片",
        "home": ("../zh/", "首页"), "view": ("3d.html", "三维视图"), "other": ("../tour.html", "English", "en"),
        "aria": "导览开始",
    },
}

STYLE = """
  <style>
    /* Round 32: the tour page (tools/tour_page.py): the 3D view without its dev header, the poster in front until Begin */
    body.tour-page .recon-header, body.tour-page #panel, body.tour-page #bpanel, body.tour-page #back, body.tour-page #walk-tip, body.tour-page #walk-exit { display: none !important; }
    body.tour-page #loading { top: 0; }
    body.tour-page { background: #0b0a08; }
    @font-face { font-family: 'Newsreader'; src: url('/assets/fonts/newsreader-latin.woff2') format('woff2'); font-style: italic; font-weight: 200 800; font-display: swap; }
    @font-face { font-family: 'Noto Serif SC'; src: url('/assets/fonts/noto-serif-sc-subset.woff2') format('woff2'); font-weight: 500; font-display: swap; }
    @font-face { font-family: 'Noto Serif SC Tour'; src: url('/assets/fonts/noto-serif-sc-tour.woff2') format('woff2'); font-weight: 500; font-display: swap; }
    #tour-poster { position: fixed; inset: 0; z-index: 4000; display: flex; align-items: flex-end; color: #F5EEE2; background: #2b2620; transition: opacity .9s ease; font: 14px/1.45 'Geist', 'Noto Serif SC', 'Noto Serif SC Tour', system-ui, sans-serif; }
    #tour-poster.gone { opacity: 0; pointer-events: none; }
    #tour-poster picture, #tour-poster picture img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
    #tour-poster .tp-scrim { position: absolute; inset: 0; background: linear-gradient(180deg, #0b0a0830 0%, #0b0a0800 35%, #0b0a08b0 78%, #0b0a08e0 100%); }
    #tour-poster .tp-copy { position: relative; box-sizing: border-box; width: min(720px, 100%); padding: 0 clamp(18px, 5vw, 64px) clamp(28px, 8vh, 84px); }
    #tour-poster .tp-seal { width: 64px; height: 64px; display: block; margin-bottom: 14px; }
    #tour-poster h1 { margin: 0; font: 500 clamp(34px, 5.5vw, 64px)/1.1 'Noto Serif SC', 'Noto Serif SC Tour', 'Songti SC', serif; letter-spacing: .06em; }
    #tour-poster h1 .en { display: block; margin-top: 6px; font: 600 clamp(13px, 1.4vw, 16px) 'Geist Mono', ui-monospace, monospace; letter-spacing: .34em; text-transform: uppercase; }
    #tour-poster .tp-sub { margin: 10px 0 0; font: italic clamp(18px, 2vw, 24px) 'Newsreader', Georgia, serif; color: #EDE3D2; }
    #tour-poster .tp-line { margin: 14px 0 0; max-width: 520px; color: #E7DccB; }
    #tour-poster button { margin-top: 22px; min-height: 52px; padding: 0 28px; border: 0; border-radius: 26px; background: #F5EEE2; color: #17130F; font: 600 14px 'Geist Mono', ui-monospace, monospace; letter-spacing: .12em; text-transform: uppercase; cursor: pointer; box-shadow: 0 6px 24px #0006; }
    #tour-poster button:hover { background: #fff; } #tour-poster button:focus-visible { outline: 3px solid #DB6543; outline-offset: 3px; }
    #tour-poster .tp-note { margin: 12px 0 0; font-size: 12px; color: #CFC3B0; }
    #tour-poster .tp-links { margin: 14px 0 0; font: 12px 'Geist Mono', ui-monospace, 'Noto Serif SC', 'Noto Serif SC Tour', monospace; letter-spacing: .06em; text-transform: uppercase; }
    #tour-poster .tp-links a { color: #F5EEE2; text-decoration: none; border-bottom: 1px solid #F5EEE266; }
    #tour-poster .tp-ai { position: absolute; right: 14px; bottom: 12px; padding: 3px 8px; border-radius: 3px; background: #17130Fb0; font-size: 11px; color: #E7DCCB; }
    @media (max-width: 700px) { #tour-poster .tp-ai { left: 14px; right: auto; bottom: auto; top: 12px; } #tour-poster .tp-seal { width: 48px; height: 48px; } }
  </style>"""

POSTER_JS = """<script>
  // The poster: Begin hides it and tells tour3d.js (window.__tourBegin, the event tour-begin); ?poster=0 skips it; ?fs=1 asks for full screen on that press.
  (function () {
    var q = new URLSearchParams(location.search), el = document.getElementById("tour-poster");
    var go = function () {
      if (window.__tourBegin) return;
      window.__tourBegin = true;
      if (q.get("fs") === "1" && document.documentElement.requestFullscreen) document.documentElement.requestFullscreen().catch(function () {});
      el.classList.add("gone");
      setTimeout(function () { el.remove(); }, 1000);
      dispatchEvent(new Event("tour-begin"));
    };
    if (q.get("poster") === "0" || q.get("shot")) { el.remove(); window.__tourBegin = true; return; }
    document.getElementById("tour-begin").onclick = go;
    document.getElementById("tour-begin").focus({ preventScroll: true });
  })();
</script>"""


def build(key):
    t = TEXT[key]
    src = SRC.read_text(encoding="utf-8")
    e = html.escape
    head = (
        f'  <title>{e(t["title"])}</title>\n'
        f'  <meta name="description" content="{e(t["desc"])}">\n'
        f'  <link rel="canonical" href="{SITE_URL}{t["path"]}">\n'
        f'  <link rel="alternate" hreflang="en" href="{SITE_URL}/tour">\n'
        f'  <link rel="alternate" hreflang="zh-Hans" href="{SITE_URL}/zh/tour">\n'
        f'  <meta property="og:type" content="website">\n'
        f'  <meta property="og:title" content="{e(t["og"])}">\n'
        f'  <meta property="og:description" content="{e(t["desc"])}">\n'
        f'  <meta property="og:image" content="{SITE_URL}/{POSTER}-1920.webp">\n'
        f'  <meta property="og:image:alt" content="{e(t["alt"])}">\n'
        f'  <meta name="twitter:card" content="summary_large_image">'
    )
    out = src
    out, n1 = re.subn(r'<html lang="[^"]*">', f'<html lang="{t["lang"]}">', out, count=1)
    out, n2 = re.subn(r"  <title>.*?</title>\n  <meta name=\"description\" content=\"[^\"]*\">", head.replace("\\", "\\\\"), out, count=1, flags=re.S)
    out, n3 = re.subn(r"</head>", STYLE.replace("\\", "\\\\") + "\n</head>", out, count=1)
    hl, hn = t["home"]
    vl, vn = t["view"]
    ol, on, olang = t["other"]
    poster = f"""<body class="tour-page" data-tour="page">
  <div id="tour-poster" role="dialog" aria-label="{e(t['aria'])}">
    <picture><source media="(max-width: 700px)" type="image/webp" srcset="../{POSTER}-phone.webp"><img src="../{POSTER}-1920.webp" srcset="../{POSTER}-1280.webp 1280w, ../{POSTER}-1920.webp 1920w, ../{POSTER}-2560.webp 2560w, ../{POSTER}-3840.webp 3840w" sizes="100vw" width="3840" height="2160" fetchpriority="high" alt="{e(t['alt'])}"></picture>
    <div class="tp-scrim"></div>
    <div class="tp-copy">
      <img class="tp-seal" src="../assets/mark.svg" width="64" height="64" alt="">
      <h1><span lang="zh-Hans">圆明园</span>{'' if key == 'zh' else '<span class="en">Yuanmingyuan</span>'}</h1>
      <p class="tp-sub">{e(t['sub'])}</p>
      <p class="tp-line">{e(t['line'])}</p>
      <button type="button" id="tour-begin">{e(t['begin'])}</button>
      <p class="tp-note">{e(t['note'])}</p>
      <p class="tp-links"><a href="{hl}">{e(hn)}</a> · <a href="{vl}">{e(vn)}</a> · <a href="{ol}" hreflang="{olang}" lang="{olang}">{e(on)}</a></p>
    </div>
    <span class="tp-ai">{e(t['ai'])}</span>
  </div>
  {POSTER_JS}"""
    out, n4 = re.subn(r"<body>", poster.replace("\\", "\\\\"), out, count=1)
    if (n1, n2, n3, n4) != (1, 1, 1, 1):
        sys.exit(f"tour_page.py: 3d.html changed shape ({n1, n2, n3, n4}); update the patterns")
    stamp = "<!-- Generated by tools/tour_page.py from site/reconstruction/3d.html (Round 32): never hand-edit; rerun it after changing 3d.html. -->\n"
    return t["out"], out.replace("<!doctype html>\n", "<!doctype html>\n" + stamp, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    stale = []
    for key in TEXT:
        path, text = build(key)
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(str(path.relative_to(ROOT)))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)} ({len(text.encode()) // 1024} KB)")
    if stale:
        sys.exit("stale, rerun tools/tour_page.py: " + ", ".join(stale))
    if args.check:
        print("tour pages up to date")


if __name__ == "__main__":
    main()
