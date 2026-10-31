"""Public-safe review render of the layers (no plan image): screenshots/r1/layers_public.png. Red = named building, grey = unnamed block on S01."""
import json,sys
from PIL import Image,ImageDraw,ImageFont
L='research/layers/'
def load(n): return json.load(open(L+n+'.geojson',encoding='utf-8'))['features']
W,H=2400,1800
x0,x1,y0,y1=116.2805,116.3155,39.9945,40.0150
kx=W/(x1-x0); ky=H/(y1-y0); ky=kx/0.766 # equal metres
H=int((y1-y0)*ky)
im=Image.new('RGB',(W,H),(240,236,226)); d=ImageDraw.Draw(im,'RGBA')
T=lambda p:((p[0]-x0)*kx,(y1-p[1])*ky)
def poly(f,fill,outline=None):
    g=f['geometry']
    rs=g['coordinates'] if g['type']=='Polygon' else [c for m in g['coordinates'] for c in m[:1]]
    d.polygon([T(p) for p in rs[0]],fill=fill,outline=outline)
    for h in (rs[1:] if g['type']=='Polygon' else []):
        d.polygon([T(p) for p in h],fill=(240,236,226,255))
for f in load('water_1860'): poly(f,(120,170,215,255))
for f in load('fields_1860'): poly(f,(190,200,120,160))
for f in load('islands_1860'): poly(f,(170,200,130,110),(70,130,50,220))
for f in load('scenes_1860'): poly(f,(205,190,150,60),(130,100,40,160))
for f in load('hills_1860'): poly(f,(150,120,80,150))
for f in load('footprints_1860'):
    c=(190,50,40,255) if f['properties']['building_id'] and not '-B' in f['properties']['building_id'] and not '-A' in f['properties']['building_id'] else (70,70,70,230)
    poly(f,c)
for f in load('bridges_1860'): d.line([T(p) for p in f['geometry']['coordinates']],fill=(120,60,160,255),width=3)
for f in load('walls_1860'):
    g=f['geometry']
    if g['type']=='LineString': d.line([T(p) for p in g['coordinates']],fill=(40,40,40,255),width=3)
    else:
        x,y=T(g['coordinates']); d.ellipse((x-5,y-5,x+5,y+5),fill=(230,120,20,255))
F=ImageFont.load_default(15)
for f in load('scenes_1860'):
    p=f['properties']
    if p['id'].startswith(('YM','XY')) and p['name_zh'] and int(p['id'][2:])<=40 or p['id'].startswith('XY'):
        ring=f['geometry']['coordinates'][0]
        cx=sum(q[0] for q in ring)/len(ring); cy=sum(q[1] for q in ring)/len(ring)
        x,y=T((cx,cy)); d.text((x-20,y-8),p['id'],font=F,fill=(0,0,0,255),stroke_width=2,stroke_fill=(255,255,255,200))
im.save('screenshots/r1/layers_public.png'); print(im.size)
