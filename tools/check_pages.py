"""Proves the building pages are whole: every clickable object of the 3D view has a page, the public copy holds nothing private, a second run of the generator changes nothing.

  uv run python tools/check_pages.py

Exits non-zero on any failure.
"""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "site/reconstruction/data"
PUBLIC = DATA / "buildings"
LOCAL = ROOT / "research/raw/buildings"
FOLDERS = ROOT / "research/buildings"
PRIVATE_LABELS = {"Plan reader's note", "How it was read", "Plan pixels", "Where the text puts it"}
ID_RE = re.compile(r"^((?:YM|CC|XY|QC)\d+(?:-[A-Z]*\d+)?|Z-[A-Z]*\d+|G\d+)-")


def digest():
    h = hashlib.sha256()
    for folder in (FOLDERS, PUBLIC, LOCAL):
        for f in sorted(p for p in folder.rglob("*") if p.is_file()):
            h.update(str(f).encode())
            h.update(f.read_bytes())
    return h.hexdigest()


def main():
    subprocess.run([sys.executable, "scripts/building_pages.py"], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    first = digest()
    subprocess.run([sys.executable, "scripts/building_pages.py"], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    problems = [] if digest() == first else ["the generator is not idempotent"]

    fc = json.load(open(DATA / "halls_1860.geojson", encoding="utf-8"))
    clickable = {f["properties"]["building_id"] for f in fc["features"]}
    clickable |= {a for f in fc["features"] for a in f["properties"].get("also", [])}
    clickable |= set(fc.get("shared_rows", {}))
    folders = {ID_RE.match(d.name + "-")[1] for d in FOLDERS.iterdir() if d.is_dir() and ID_RE.match(d.name + "-") and (d / "index.md").exists()}
    for pid in sorted(clickable):
        for folder in (PUBLIC, LOCAL):
            if not (folder / f"{pid}.json").exists():
                problems.append(f"{pid}: no {folder.name} JSON")
        if pid not in folders:
            problems.append(f"{pid}: no page")

    public_files = sorted(PUBLIC.glob("*.json"))
    for f in public_files:
        text = f.read_text(encoding="utf-8")
        page = json.loads(text)
        if any(x.get("private") or x["label"] in PRIVATE_LABELS for x in page["facts"]):
            problems.append(f"{f.name}: a private fact")
        if "/_local/" in text or "raw/" in text or any("image" in p or "thumb" in p for p in page["photos"]):
            problems.append(f"{f.name}: a local path or an image")
        if not page["sources"] and page["kind"] != "gate":
            problems.append(f"{f.name}: no sources")
    print(f"{len(clickable)} clickable objects, {sum(p.endswith('no page') for p in problems)} without a page; {len(folders)} page folders, {len(public_files)} public files checked; generator idempotent: {'generator' not in ' '.join(problems)}")
    for p in problems:
        print("FAIL", p)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
