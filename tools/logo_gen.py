"""Three logo proposals for the Yuanmingyuan project. Run: uvx --from 'fonttools[woff]' python palace_logo_gen.py <repo> <outdir>
Writes A_seal.svg, B_nine_islands.svg, C_arch.svg (icons) and *_lockup.svg (icon + 圆明园 + Yuanmingyuan, all outlines, no font needed)."""
import math, pathlib, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

R = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
F = R / 'site/assets/fonts'
zh = TTFont(F / 'noto-serif-sc-subset.woff2')
la = TTFont(F / 'newsreader-latin.woff2')
RED, CREAM, DARK = '#C2452D', '#F5EEE2', '#17130F'

def glyph_path(font, ch, cx, cy, size, upm=None):
    """Glyph centred on (cx, cy) by its bounding box, em = size px."""
    gs = font.getGlyphSet(); name = font.getBestCmap()[ord(ch)]
    upm = upm or font['head'].unitsPerEm; s = size / upm
    bp = BoundsPen(gs); gs[name].draw(bp); x0, y0, x1, y1 = bp.bounds
    tx = cx - s * (x0 + x1) / 2; ty = cy + s * (y0 + y1) / 2
    pen = SVGPathPen(gs, ntos=lambda v: f'{v:.2f}'.rstrip('0').rstrip('.'))
    gs[name].draw(TransformPen(pen, (s, 0, 0, -s, tx, ty)))
    return pen.getCommands()

def line_path(font, text, x, base, size, track=0.0):
    """Latin line starting at x on baseline `base`; returns (d, width)."""
    gs = font.getGlyphSet(); cmap = font.getBestCmap(); upm = font['head'].unitsPerEm; s = size / upm
    d = []; cur = x
    for ch in text:
        name = cmap[ord(ch)]
        pen = SVGPathPen(gs, ntos=lambda v: f'{v:.2f}'.rstrip('0').rstrip('.'))
        gs[name].draw(TransformPen(pen, (s, 0, 0, -s, cur, base))); d.append(pen.getCommands())
        cur += font['hmtx'][name][0] * s + track
    return ' '.join(d), cur - x

def blob(cx, cy, hx, hy, seed, n=3.0, wob=0.04, pts=56):
    out = []
    for i in range(pts):
        t = 2 * math.pi * i / pts
        c, s_ = math.cos(t), math.sin(t)
        r = (abs(c) ** n + abs(s_) ** n) ** (-1 / n)  # superellipse radius factor
        w = 1 + wob * math.sin(3 * t + seed) + wob * 0.6 * math.sin(5 * t + seed * 2.1)
        out.append((cx + hx * r * c * w, cy + hy * r * s_ * w))
    return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in out) + 'Z'

# ---------- A: the seal (印), cut-out characters on vermilion ----------
def seal():
    g = []
    # modern reading order, row by row: 圆 明 / 园 and the round sun
    cells = {'圆': (80, 84), '明': (176, 84), '园': (80, 178)}
    for ch, (cx, cy) in cells.items():
        g.append(glyph_path(zh, ch, cx, cy, 70))
    chars = ' '.join(g)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
<defs><filter id="rough" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves="3" seed="7" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="3.2"/></filter></defs>
<g filter="url(#rough)">
<rect x="20" y="20" width="216" height="216" rx="5" fill="{RED}"/>
<rect x="30" y="30" width="196" height="196" rx="2" fill="none" stroke="{CREAM}" stroke-width="3.2"/>
<path fill="{CREAM}" stroke="{CREAM}" stroke-width="2.2" stroke-linejoin="round" d="{chars}"/>
<circle cx="176" cy="178" r="26" fill="{CREAM}"/>
</g></svg>'''

# ---------- B: nine islands inside the circle ----------
def nine(bg=None, fg=CREAM):
    isl = []
    pitch, h = 55, 21
    k = 0
    for j in (-1, 0, 1):
        for i in (-1, 0, 1):
            k += 1
            cx, cy = 128 + i * pitch, 128 + j * pitch
            hh = h - (3 if (i and j) else 0)
            col = RED if (i == 0 and j == 0) else fg
            d = blob(cx, cy, hh, hh * (0.9 if i == 0 else 1.0), seed=k * 1.7)
            isl.append(f'<path d="{d}" fill="{col}"/>')
    br = ''.join(f'<rect x="{x}" y="{y}" width="{w}" height="{h2}" fill="{fg}"/>' for x,y,w,h2 in [(123,93,10,15),(123,148,10,15),(93,123,15,10),(148,123,15,10)])
    body = '\n'.join(isl) + br
    bgs = f'<rect width="256" height="256" fill="{bg}"/>' if bg else ''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">{bgs}
<circle cx="128" cy="128" r="116" fill="none" stroke="{fg}" stroke-width="5"/>
{body}</svg>'''

# ---------- C: the stone arch of the Great Fountain against the round sun ----------
def arch(fg=CREAM):
    spokes = ''.join(f'<path d="M128 112L{128 + 34*math.cos(math.radians(t)):.1f} {112 - 34*math.sin(math.radians(t)):.1f}" stroke="{fg}" stroke-width="3.2" stroke-linecap="round"/>' for t in range(20, 161, 20))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
<circle cx="128" cy="112" r="84" fill="{RED}"/>
<g fill="{fg}">
<path d="M26 214H230V230H26Z"/>
<path d="M34 206H222V214H34Z"/>
<path fill-rule="evenodd" d="M70 206V94Q70 40 128 40Q186 40 186 94V206H160V112Q160 78 128 78Q96 78 96 112V206Z"/>
<path d="M62 104H104V112H62Z M152 104H194V112H152Z"/>
<path d="M40 206V138H46V132H64V138H70V206Z"/>
<path d="M186 206V160L193 152L199 156L205 146L212 150V206Z"/>
</g>
<g fill="none">{spokes}<path d="M96 112Q96 78 128 78Q160 78 160 112" stroke="{fg}" stroke-width="3.2"/></g></svg>'''

def lockup(icon_svg, name, bg=DARK):
    inner = icon_svg.split('>', 1)[1].rsplit('</svg>', 1)[0]
    d_zh = ' '.join(glyph_path(zh, ch, 330 + i * 78, 116, 70) for i, ch in enumerate('圆明园'))
    d_la, w = line_path(la, 'Yuanmingyuan', 296, 186, 38, track=1.2)
    d_sub, w2 = line_path(la, 'before October 1860', 298, 220, 20, track=0.6)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 256"><rect width="640" height="256" fill="{bg}"/>
<g transform="translate(14 0)">{inner}</g>
<path fill="{CREAM}" d="{d_zh}"/>
<path fill="{CREAM}" d="{d_la}"/>
<path fill="#A1927D" d="{d_sub}"/></svg>'''

icons = {'A_seal': seal(), 'B_nine_islands': nine(), 'C_arch': arch()}
for k, v in icons.items():
    (OUT / f'{k}.svg').write_text(v, encoding='utf-8')
    (OUT / f'{k}_lockup.svg').write_text(lockup(v, k), encoding='utf-8')
# light-ground variants of B and C for the favicon test
(OUT / 'B_nine_islands_ondark_ink.svg').write_text(nine(fg=DARK), encoding='utf-8')
(OUT / 'C_arch_ink.svg').write_text(arch(fg=DARK), encoding='utf-8')
print('ok', sorted(p.name for p in OUT.glob('*.svg')))
