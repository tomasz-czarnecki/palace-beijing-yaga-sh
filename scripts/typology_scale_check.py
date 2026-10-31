#!/usr/bin/env python
"""Scale check of S01 (princeton_mosaic.jpg): ground scale from surviving features vs hall scale from stated sizes.
Plan numbers are readings from labelled crops / prof.py darkness projections (scratch palace_r1b_typology/crops)."""
import json, math
import numpy as np
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform
OSM='research/layers/osm_today.geojson'
tr=Transformer.from_crs(4326,32650,always_xy=True).transform
fs=json.load(open(OSM))['features']
def find(name=None,area=None,near=None):
    best=None
    for f in fs:
        p=f['properties']
        if name and p.get('name')!=name: continue
        g=transform(tr,shape(f['geometry']))
        if area and abs(g.area-area)>1: continue
        best=g; break
    return best
ctrl=[('方河',find('方河'),(11894,1111),'plan outline centre / OSM water polygon'),
      ('后湖',find('后湖'),(3300,4030),'plan water centre / OSM water polygon'),
      ('方外观 ruin',find(area=880),(9405,989),'plan label+block / OSM ruins 44x24'),
      ('远瀛观 ruin',find(area=2351),(10566,840),'plan hall / OSM ruins 59x51'),
      ('海晏堂 ruin',find(area=5506),(10028,1111),'plan complex centre / OSM ruins 135x54'),
      ('方壶胜境 ruin',find(area=5063),(8020,950),'plan 琼华楼 complex / OSM ruins 93x93'),
      ('长春园宫门',find('长春园宫门') if False else None,(11036,4914),'plan gate / OSM building'),
      ('正大光明 point',find('正大光明'),(3305,5445),'plan hall / OSM attraction point')]
# 长春园宫门: use the polygon, not the point
for f in fs:
    if f['properties'].get('name')=='长春园宫门' and f['geometry']['type']=='Polygon':
        ctrl[6]=(ctrl[6][0],transform(tr,shape(f['geometry'])),ctrl[6][2],ctrl[6][3])
A=[];B=[];names=[]
for n,g,(x,y),_ in ctrl:
    c=g.centroid; A.append([x,y,1]); B.append([c.x,c.y]); names.append(n)
A=np.array(A,float);B=np.array(B,float)
M,*_=np.linalg.lstsq(A,B,rcond=None)
res=A@M-B
sx=math.hypot(M[0,0],M[1,0]); sy=math.hypot(M[0,1],M[1,1])
print('GROUND FIT (affine, plan px -> UTM50N), n=',len(A))
print(' m per px x,y:',round(sx,4),round(sy,4),' => px per m x,y:',round(1/sx,3),round(1/sy,3))
print(' rotation deg:',round(math.degrees(math.atan2(M[1,0],M[0,0])),2))
for n,r in zip(names,res): print(f'  {n}: resid {math.hypot(*r):.1f} m')
print(' RMS m:',round(float(np.sqrt((res**2).sum(1).mean())),1))
paper_px_per_m=12955/2.53
print(' paper px/m (12955 px over 253 cm):',round(paper_px_per_m),' implied scale 1:',round(paper_px_per_m/(0.5*(1/sx+1/sy))))
print(' Malone 1:1300 gives px/m:',round(paper_px_per_m/1300,2))
# water / feature sizes
sizes=[('后湖 E-W',1076,228,'OSM bbox'),('后湖 N-S',900,211,'OSM bbox'),('方河 E-W',647,149.2,'OSM mrr'),('方河 N-S',253,45.0,'OSM mrr')]
print('SURVIVING WATER'); 
for n,px,m,s in sizes: print(f'  {n}: {px} px / {m} m = {px/m:.2f} px/m ({s})')
# halls: (id,name,axis,px,metres,what metres are,source)
H=[('YM01-01','正大光明殿','F',151.4,39.32,'foundation 129 ft (Malone measured)','S02 p.75'),
   ('YM01-01','正大光明殿 月台','F',151,38.40,'月台 面宽12丈','S119'),
   ('YM01-01','正大光明殿','D',57.5,19.20,'foundation 63 ft','S02 p.75'),
   ('YM01-01','正大光明殿 月台','D',74.5,14.82,'月台 深4丈6尺3寸','S119'),
   ('YM41-01','大宫门','F',98.5,21.57,'台基通面宽','S102'),
   ('YM41-01','大宫门','D',26.5,11.33,'台基进深','S102'),
   ('YM33-01','观澜堂','F',97.7,23.36,'4.16+4x3.84+2x1.92 (columns)','S111'),
   ('YM33-01','观澜堂','D',82.6,26.49,'3x7.55+2x1.92 (columns)','S111'),
   ('YM33-01','观澜堂 central bay','B',20.2,4.16,'明间','S111'),
   ('YM33-01','观澜堂 side bays mean','B',16.2,3.84,'次间','S111'),
   ('YM41-02','文源阁','F',123.8,22.72,'5.12+4x4.0+1.6 (丈尺册)','S105'),
   ('YM41-02','文源阁','D',56.1,14.72,'7.68+2x3.52 (丈尺册)','S105'),
   ('YM36-02','藏密楼 3 bays','F',42.6,8.96,'3.20+2x2.88','S111'),
   ('YM36-03','松风阁','D',40.5,6.40,'3.84+2x1.28','S111'),
   ('YM20-01','田字房 room row','B',24.5,4.48,'room side (excavated)','S104'),
   ('YM20-01','田字房 well','B',43.5,3.80,'天井 side (excavated)','S104'),
   ('YM13-01','万字房 arm','D',23.5,7.04,'4.48+2x1.28','S113'),
   ('YM41-03','舍卫城 south gate 墩台','F',58.3,15.4,'墩台宽 (excavated)','S107'),
   ('YM41-03','舍卫城 south gate 墩台','D',41.5,12.6,'墩台进深 (excavated)','S107'),
   ('XY08','海晏堂 complex (rough)','F',460,135.2,'OSM ruins polygon','S03'),
   ('XY08','海晏堂 complex (rough)','D',229,54.5,'OSM ruins polygon','S03'),
   ('XY08','海晏堂 central strip = 蓄水楼 tank?','F',130,27.36,'锡海 E-W length','S109'),
   ('XY04','黄花阵 outer','F',350,59,'stated, unsourced','S06'),
   ('XY04','黄花阵 outer','D',470,89,'stated, unsourced','S06')]
print('HALLS  (F=frontage/long axis, D=depth, B=single bay)')
out=[]
for r in H:
    v=r[3]/r[4]; out.append(dict(id=r[0],name=r[1],axis=r[2],px=r[3],m=r[4],what=r[5],src=r[6],px_per_m=round(v,2)))
    print(f'  {r[0]:8} {r[1]:22} {r[2]} {r[3]:7.1f} px / {r[4]:6.2f} m = {v:5.2f} px/m   [{r[5]}; {r[6]}]')
for ax,lab,ex in (('F','frontage',('XY','YM01-01x')),('D','depth',('XY',))):
    v=[o['px_per_m'] for o in out if o['axis']==ax and not o['id'].startswith('XY')]
    print(f' {lab}, Chinese halls: n={len(v)} min={min(v)} median={float(np.median(v)):.2f} max={max(v)}')
json.dump(dict(ground=dict(px_per_m_x=round(1/sx,3),px_per_m_y=round(1/sy,3),rms_m=round(float(np.sqrt((res**2).sum(1).mean())),1)),halls=out),open('research/typology/scale_check.json','w'),ensure_ascii=False,indent=1)
