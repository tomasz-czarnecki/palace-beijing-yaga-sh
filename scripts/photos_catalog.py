"""Everything that hangs off the picture catalogs. research/photos/catalog.csv and research/reconstructions/catalog.csv are the sources of truth.

  uv run python scripts/photos_catalog.py

Writes:
  site/reconstruction/photos/P####.jpg, R####.jpg, _t.jpg   public: free pictures and free reconstructions that show an object, at most 1000 px and 400 px. `crop` (fractions x0,y0,x1,y1) cuts the web copy: the album's bifolios show the painting, the research file keeps the whole leaf
  site/credits.html, research/image-credits/CREDITS.md   the credit of every public picture, between markers

Refuses to run if a research-only picture sits in research/photos/images/, research/reconstructions/images/ or site/, or if a public picture has no licence or attribution.
"""

import csv
import html
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
FREE = ROOT / "research/photos/images"
FREE_RECON = ROOT / "research/reconstructions/images"
SITE_PHOTOS = ROOT / "site/reconstruction/photos"
CREDITS_HTML = ROOT / "site/credits.html"
CREDITS_MD = ROOT / "research/image-credits/CREDITS.md"
WEB_PX, THUMB_PX, MAX_BYTES = 1000, 400, 170_000
START, END = "<!-- photos:start (scripts/photos_catalog.py) -->", "<!-- photos:end -->"


def clean_licence(text):
    text = re.sub(r"\{\{([^}]*)\}\}", r"\1", text)
    text = re.sub(r"Commons file tags?: ", "Commons: ", text)
    text = re.sub(r"Commons LicenseShortName ", "Commons: ", text)
    text = re.sub(r"; BnF/Gallica: free non-commercial reuse with credit \(project rule, Gallica page not reachable from this server\)", "; BnF: free non-commercial reuse with credit", text)
    return text


def public_rows():
    rows = list(csv.DictReader(open(ROOT / "research/photos/catalog.csv", encoding="utf-8", newline="")))
    out = []
    for r in rows:
        if r["rights_class"] != "free":
            assert not (FREE / f"{r['photo_id']}.jpg").exists(), f"{r['photo_id']}: research-only, yet in photos/images"
            assert not (SITE_PHOTOS / f"{r['photo_id']}.jpg").exists(), f"{r['photo_id']}: research-only, yet on the site"
            continue
        if r["file"] and r["shows"]:
            assert r["licence"] and r["attribution"], f"{r['photo_id']}: free without licence or attribution"
            out.append(r)
    for r in csv.DictReader(open(ROOT / "research/reconstructions/catalog.csv", encoding="utf-8", newline="")):
        rid = r["recon_id"]
        if r["rights_class"] != "free":
            assert not (FREE_RECON / f"{rid}.jpg").exists(), f"{rid}: research-only, yet in reconstructions/images"
            assert not (SITE_PHOTOS / f"{rid}.jpg").exists(), f"{rid}: research-only, yet on the site"
            continue
        if r["local_copy"] and r["shows"]:
            assert r["licence"] and r["attribution"], f"{rid}: free without licence or attribution"
            out.append({"photo_id": rid, "file": r["local_copy"], "crop": "", "title": " ".join(x for x in (r["title"], f"by {r['author']}" if r["author"] else "") if x), "date": r["year"], "source_url": r["link"], "licence": r["licence"], "attribution": r["attribution"]})
    return out


def write_copy(im, path, px, quality):
    im = im.copy()
    im.thumbnail((px, px), Image.LANCZOS)
    for q in (quality, quality - 8, quality - 16, quality - 24):
        im.save(path, "JPEG", quality=q, optimize=True, progressive=True)
        if px != WEB_PX or path.stat().st_size <= MAX_BYTES:
            break


def copies(rows):
    SITE_PHOTOS.mkdir(parents=True, exist_ok=True)
    made = 0
    wanted = set()
    for r in rows:
        pid, src = r["photo_id"], ROOT / r["file"]
        web, thumb = SITE_PHOTOS / f"{pid}.jpg", SITE_PHOTOS / f"{pid}_t.jpg"
        wanted |= {web.name, thumb.name}
        if web.exists() and thumb.exists() and web.stat().st_mtime >= src.stat().st_mtime and not r["crop"]:
            continue
        if web.exists() and thumb.exists() and pid.startswith("P") and web.stat().st_mtime >= (ROOT / "research/photos/catalog.csv").stat().st_mtime:
            continue
        im = Image.open(src).convert("RGB")
        if r["crop"]:
            x0, y0, x1, y1 = (float(v) for v in r["crop"].split(","))
            im = im.crop((int(x0 * im.width), int(y0 * im.height), int(x1 * im.width), int(y1 * im.height)))
        write_copy(im, web, WEB_PX, 76)
        write_copy(im, thumb, THUMB_PX, 68)
        made += 1
    for f in SITE_PHOTOS.glob("*.jpg"):
        if f.name not in wanted:
            f.unlink()
    return made


def credits(rows):
    esc = html.escape
    rows = sorted(rows, key=lambda r: r["photo_id"])
    trs = []
    for r in rows:
        pid = r["photo_id"]
        trs.append(f'            <tr id="{pid}"><td class="credit-thumb"><img src="reconstruction/photos/{pid}_t.jpg" loading="lazy" alt="" width="96"></td>'
                   f'<td>{esc(r["title"])}{", " + esc(r["date"]) if r["date"] else ""}. <a href="{esc(r["source_url"])}">Source</a></td>'
                   f'<td>{esc(clean_licence(r["licence"]))}</td><td>{esc(r["attribution"])}</td></tr>')
    block = "\n".join([START, '        <div class="credits-block">', f"          <h2>Pictures in the 3D view ({len(rows)})</h2>", '          <p class="credit-note">Album leaves and other BnF items: Source gallica.bnf.fr / BnF, free for non-commercial use. Pictures on other holders\' pages are linked from the panel and are not copied here. Ids beginning with R are reconstructions by other people, shown as modern interpretations.</p>', '          <div class="credit-scroll">', '          <table class="credit-table">', '            <thead><tr><th scope="col">Image</th><th scope="col">Title, date, source</th><th scope="col">Licence</th><th scope="col">Credit</th></tr></thead>', "            <tbody>", *trs, "            </tbody>", "          </table>", "          </div>", "        </div>", END])
    text = CREDITS_HTML.read_text(encoding="utf-8")
    if START in text:
        text = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: block, text, flags=re.S)
    else:
        anchor = '        <div class="credits-block">\n          <h2>Fonts</h2>'
        assert anchor in text
        text = text.replace(anchor, block + "\n\n" + anchor)
    CREDITS_HTML.write_text(text, encoding="utf-8")

    md = ["| File | Title, date | Source | Licence | Attribution to show |", "|---|---|---|---|---|"]
    cell = lambda s: (s or "").replace("|", "/").replace("\n", " ")
    for r in rows:
        md.append(f"| `{r['photo_id']}` | {cell(r['title'])}, {cell(r['date'])} | {r['source_url']} | {cell(clean_licence(r['licence']))} | {cell(r['attribution'])} |")
    block_md = "\n".join([START, "", "## Pictures in the 3D view", "", "Web copies at most 1000 px in `site/reconstruction/photos/`; the album leaves are cut to the painting. BnF items: Source gallica.bnf.fr / BnF, non-commercial.", "", *md, "", END])
    text = CREDITS_MD.read_text(encoding="utf-8")
    if START in text:
        text = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: block_md, text, flags=re.S)
    else:
        text = text.rstrip("\n") + "\n\n" + block_md + "\n"
    CREDITS_MD.write_text(text, encoding="utf-8")


def main():
    rows = public_rows()
    made = copies(rows)
    credits(rows)
    size = sum(f.stat().st_size for f in SITE_PHOTOS.glob("*.jpg"))
    print(f"{len(rows)} public pictures, {made} copies made; site/reconstruction/photos {size / 1e6:.0f} MB")


if __name__ == "__main__":
    main()
