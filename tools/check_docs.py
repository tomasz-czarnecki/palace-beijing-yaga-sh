"""The docs say what the repo holds: every CSV column, layer property and panel key is named in the docs, every field a table names exists, every path and script the docs name is there.

  uv run python tools/check_docs.py

Reads CLAUDE.md, research/README.md, research/photos/README.md, docs/METHOD.md, docs/rounds/README.md. Writes nothing. Exits non-zero on any failure.
"""

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
csv.field_size_limit(10**8)
README = ROOT / "research/README.md"
PHOTOS_README = ROOT / "research/photos/README.md"
DOCS = [ROOT / "CLAUDE.md", README, PHOTOS_README, ROOT / "docs/METHOD.md", ROOT / "docs/rounds/README.md"]
# Where a backticked relative path may start from.
BASES = [ROOT, ROOT / "research", ROOT / "research/plan", ROOT / "research/plan/readings/ym_west", ROOT / "research/photos", ROOT / "research/evidence", ROOT / "research/georef", ROOT / "research/typology", ROOT / "site", ROOT / "site/reconstruction", ROOT / "site/reconstruction/data", ROOT / "site/reconstruction/generated", ROOT / "docs", ROOT / "docs/rounds", ROOT / "scripts", ROOT / "tools"]
PATH_RE = re.compile(r"`([^`\s]+)`")
LOOKS_LIKE_PATH = re.compile(r"^[\w./-]+(\.(py|csv|json|geojson|md|html|js|css|i16|bin|lock|toml)|/)$")
# Names of files in another project, gone from this one, or meant as a pattern.
NOT_HERE = {"build_catalog.py", "scripts/build_catalog.py", "palace_home_subset.py", "summary.json", "index.md", "notes.md", "package.json", "000_Dev/CLAUDE.md", "plans/", "dem/", "osm/", "photos/", "plancrops/", "buildings/"}


def section(text, heading):
    """The body under a heading, up to the next heading of the same or a higher level."""
    m = re.search(rf"^(#+) {re.escape(heading)}\s*$", text, re.M)
    if not m:
        return None
    rest = text[m.end():]
    end = re.search(rf"^#{{1,{len(m[1])}}} ", rest, re.M)
    return rest[:end.start()] if end else rest


def main():
    problems = []
    readme = README.read_text(encoding="utf-8")
    both = readme + PHOTOS_README.read_text(encoding="utf-8")
    named = {name for line in both.splitlines() for name in re.findall(r"`([^`]+)`", line)}  # line by line: a stray backtick spoils one line, not the rest

    # every column named; the five reader files share their headers
    files = [p for p in (ROOT / "research").rglob("*.csv") if "raw" not in p.parts and "overlays" not in p.parts]
    checked = 0
    for path in sorted(files):
        with open(path, encoding="utf-8", newline="") as h:
            header = next(csv.reader(h))
        for col in header:
            checked += 1
            if col not in named:
                problems.append(f"{path.relative_to(ROOT)}: column {col} is not in the README")
    # every layer property, public or working; OSM keeps its own tags
    for path in sorted((ROOT / "research/layers").glob("*_1860.geojson")) + sorted((ROOT / "site/reconstruction/data").glob("*_1860.geojson")):
        props = {k for f in json.load(open(path, encoding="utf-8"))["features"] for k in f["properties"]}
        for prop in sorted(props):
            checked += 1
            if prop not in named:
                problems.append(f"{path.relative_to(ROOT)}: property {prop} is not in the README")
    # every panel key
    page = json.load(open(ROOT / "site/reconstruction/data/buildings/YM03.json", encoding="utf-8"))
    for key in page:
        checked += 1
        if key not in named:
            problems.append(f"panel JSON: key {key} is not in the README")

    # the other way round: each field table names only real columns
    for heading, rel in (("buildings.csv", "research/buildings.csv"), ("evidence/catalog.csv", "research/evidence/catalog.csv"), ("evidence/facts.csv", "research/evidence/facts.csv"), ("georef/princeton-1920s.csv", "research/georef/princeton-1920s.csv")):
        body = section(readme, heading)
        if body is None:
            problems.append(f"README: no section {heading}")
            continue
        with open(ROOT / rel, encoding="utf-8", newline="") as h:
            header = set(next(csv.reader(h)))
        for cell in re.findall(r"^\| ([^|]+) \|", body, re.M):
            for field in re.findall(r"`([^`]+)`", cell):
                if field not in header:
                    problems.append(f"README {heading}: {field} is not a column of {rel}")

    # every path and script named
    paths = 0
    for doc in DOCS:
        if not doc.exists():
            problems.append(f"{doc.relative_to(ROOT)} is missing")
            continue
        for token in PATH_RE.findall(doc.read_text(encoding="utf-8")):
            token = token.split(" ")[0].rstrip(":,")
            if token.startswith("/") or "<" in token or "*" in token or token in NOT_HERE or not LOOKS_LIKE_PATH.match(token):
                continue
            paths += 1
            if token.startswith(("raw/", "overlays/", "research/raw/", "research/overlays/")):
                continue  # local, gitignored: not there on a fresh clone
            if not any((base / token).exists() for base in BASES):
                problems.append(f"{doc.relative_to(ROOT)}: {token} does not exist")

    print(f"{checked} columns, properties and keys checked; {paths} paths checked")
    for p in problems:
        print("FAIL", p)
    print("OK" if not problems else f"{len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
