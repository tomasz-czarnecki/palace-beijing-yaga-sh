"""Rebuild the Chinese font subsets used by the site (site/assets/fonts/noto-{sans,serif}-sc-subset.woff2).

Run it after adding Chinese text to the pages; a character missing from the subset falls back to a system font.
Inputs: the full Noto Sans SC and Noto Serif SC OpenType files (SIL Open Font License), saved as sans.otf and
serif.otf in the current directory. They are about 8 and 12 MB, so they are not committed; download them from
https://github.com/notofonts/noto-cjk (Sans/OTF/SimplifiedChinese, Serif/OTF/SimplifiedChinese).
Usage: cd <folder with sans.otf and serif.otf> && python3 <repo>/tools/font_subset.py <repo>
Needs uvx (/opt/data/.local/bin/uvx) for fonttools. Copied from the homepage round's scratch script palace_home_subset.py.
"""
import pathlib
import subprocess
import sys

R = pathlib.Path(sys.argv[1])
text = ''
for f in ['index.html', 'zh/index.html', 'credits.html', 'reconstruction/index.html']:
    text += (R / 'site' / f).read_text(encoding='utf-8')
chars = sorted({c for c in text if ord(c) > 0x2E7F})
print(len(chars), 'chars')
u = ''.join(chars) + '，。、：；“”《》（）·'
for src, out in [('sans.otf', 'noto-sans-sc-subset.woff2'), ('serif.otf', 'noto-serif-sc-subset.woff2')]:
    subprocess.run(['uvx', '--from', 'fonttools[woff]', 'pyftsubset', src, '--text=' + u, '--flavor=woff2',
                    '--layout-features=*', '--output-file=' + str(R / 'site/assets/fonts' / out)], check=True)
