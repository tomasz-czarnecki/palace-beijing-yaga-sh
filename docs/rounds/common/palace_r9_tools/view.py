"""Debug view (scratch only): water, boxes, walls, bridges, paths and landings around a point, in scene metres. No plan image.
uv run python view.py <tag> <scene_id|x,z> [half_m=120]"""
import sys, json
sys.path.insert(0,'scripts')
import paths1860 as P
import numpy as np
from PIL import Image, ImageDraw, ImageFont
boxes, by_row, water, waters, bridges, gates, walls, wall_segs, scenes = P.load_world()
tag, where = sys.argv[1], sys.argv[2]
half = float(sys.argv[3]) if len(sys.argv) > 3 else 120
if ',' in where: c = np.array(list(map(float, where.split(','))))
else:
    c = np.asarray(scenes[where][1].centroid.coords[0]) if where in scenes else by_row[where][0].c
S = 1000 / (2 * half)
im = Image.new('RGB', (1000, 1000), (235, 228, 205)); d = ImageDraw.Draw(im)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 10)
px = lambda p: ((p[0] - c[0] + half) * S, (p[1] - c[1] + half) * S)
def poly(g, fill, outline=None):
    for q in getattr(g, 'geoms', [g]):
        if q.is_empty: continue
        d.polygon([px(p) for p in q.exterior.coords], fill=fill, outline=outline)
        for h in q.interiors: d.polygon([px(p) for p in h.coords], fill=(235, 228, 205))
from shapely.geometry import box as sbox
win = sbox(c[0]-half, c[1]-half, c[0]+half, c[1]+half)
poly(water.intersection(win), (150, 190, 210))
for b in boxes:
    if b.poly.intersects(win):
        col = (200, 200, 170) if b.walk_through else (150, 110, 80)
        poly(b.poly, col, (60, 40, 20)); 
        if half <= 150: d.text(px(b.c), b.id, fill=(0, 0, 0), font=F)
for w in walls:
    for q in getattr(w.intersection(win), 'geoms', [w.intersection(win)]):
        if not q.is_empty and q.geom_type == 'LineString': d.line([px(p) for p in q.coords], fill=(90, 80, 70), width=2)
for k, (bp, g) in bridges.items():
    if g.intersects(win): d.line([px(p) for p in g.coords], fill=(120, 60, 200), width=4); d.text(px(g.coords[0]), k, fill=(90, 0, 160), font=F)
COL = {'A': (0, 140, 0), 'B': (20, 60, 220), 'C': (230, 110, 0)}
for f in json.load(open('research/layers/paths_1860.geojson'))['features']:
    L = P.xz_geom(f['geometry'])
    if not L.intersects(win): continue
    p = f['properties']; col = (220, 0, 0) if p['blocked_m'] > 0.05 else COL[p['confidence']]
    d.line([px(q) for q in L.coords], fill=col, width=3 if p['kind'] != 'boat_route' else 1)
    if half <= 150: d.text(px(L.interpolate(0.5, normalized=True).coords[0]), p['id'], fill=col, font=F)
for f in json.load(open('research/layers/landings_1860.geojson'))['features']:
    q = P.xz_geom(f['geometry']).coords[0]; x, y = px(q); d.ellipse([x-5, y-5, x+5, y+5], outline=(200, 0, 200), width=2)
im.save(f'/opt/data/cache/scratch/palace_r9_crops/view_{tag}.png'); print(f'/opt/data/cache/scratch/palace_r9_crops/view_{tag}.png')
