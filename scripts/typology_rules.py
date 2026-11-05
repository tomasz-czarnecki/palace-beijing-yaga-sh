#!/usr/bin/env python
"""Qing rules applied to hall classes. All lengths metres; 1 chi = 0.32 m (S105).
Rules (S100 scan; S101 summary):
 column H: 小式 0.8 x bay for 6-7 purlins, 0.7 x bay for 4-5 purlins; 大式 70 doukou incl. plate and brackets.
 overhang 上出 = 0.3 H (no brackets); 下出 = 0.8 x 上出 ; platform = H/5 ; column dia = 0.07 x bay.
 举架: 5 purlins 五举/七举 ; 7 purlins 五/六五/八五 ; 大式 五/六五/七五/九.
 Rolled (even purlins): flat top step about 0.6 of a normal step (S101: 1/5 of 四架梁 span, sides 2/5 -> ratio 0.5; 0.6 used, C).
 Ridge allowance = purlin dia + 0.25 m for boards and tile (C, assumption, not from a source).
"""
import json, math
CHI=0.32
def roof(depth, porch, ju, rolled=True, D=0.25):
    """depth col-to-col; porch step at each end; ju = list of 举 from eave up, ju[0] applied to the porch/eave step."""
    n=len(ju)-1  # normal inner steps per side
    inner=depth-2*porch
    s=inner/(2*n+(0.6 if rolled else 0))
    top=0.6*s if rolled else 0
    rise=porch*ju[0]+sum(s*j for j in ju[1:])
    half=depth/2-(top/2)
    return dict(step=round(s,2),top=round(top,2),rise=round(rise,2),pitch=round(math.degrees(math.atan2(rise,half)),1),
                arith=f"inner {inner:.2f} = 2x{n}x{s:.2f}"+(f" + top {top:.2f}" if rolled else "")+"; rise = "+f"{porch:.2f}x{ju[0]}"+"".join(f" + {s:.2f}x{j}" for j in ju[1:])+f" = {rise:.2f}")
C={}
def make(name,bay_c,bay_s,n,porch,depth,H,plat,ju,rolled=True,over=None,lower=None):
    r=roof(depth,porch,ju,rolled)
    o=over if over else round(0.3*H,2)
    dia=round(0.07*bay_c,2)
    eave=round(plat+H,2); tip=round(eave-0.5*o,2)
    ridge=round(plat+H+r['rise']+dia+0.25,2)
    front=round(bay_c+(n-1)*bay_s+2*(porch if porch else 0),2)
    C[name]=dict(bays=n,bay_central=bay_c,bay_side=bay_s,porch=porch,frontage=front,depth=depth,column=H,platform=plat,overhang=o,lower_out=round(.8*o,2),dia=dia,eave=eave,eave_tip=tip,rise=r['rise'],ridge=ridge,pitch=r['pitch'],arith=r['arith'])
J5=[.5,.7]; J7=[.5,.65,.85]; JB=[.5,.65,.75,.9]; J6=[.5,.6,.75,.9]
#   name,        bay_c,bay_s,n, porch, depth,  H,   plat, ju
make('grand_hall_r1',5.50,4.70,7,1.70,16.74,5.12,1.22,J6)  # Round 1: 正大光明殿 as the type
# Round 11 (Q182, Q183): the class from its measured halls (research/scenes/dimensions.csv, method a), 正大光明殿 keeping its own figures through by_name.
import csv, statistics
DIMS=list(csv.DictReader(open('research/scenes/dimensions.csv',encoding='utf-8')))
def fig(bid,what): return [float(r['value_m']) for r in DIMS if r['id']==bid and r['what']==what and r['method']=='a']
GH=['YM03-11','YM02-08','YM23-01','YM20-01']  # 慎德堂, 保合太和殿, 慎修思永, 田字殿: the measured residential and office halls of the class
cols=[fig(b,'column_h')[0] for b in GH if fig(b,'column_h')]
plats=[fig(b,'platform_h')[0] for b in GH if fig(b,'platform_h')]
H11=round(statistics.median(cols),2); P11=round(statistics.median(plats),2)
print('grand_hall Round 11: columns',cols,'median',H11,'; platforms',plats,'median',P11)
zb=[fig('YM01-08',w) for w in ('bay_width','other:secondary_bay_width','other:end_bay_width')]
print('正大光明殿 bays (NLC 样001-4 slip via S310): central, next, end',zb)
make('grand_hall',round(zb[0][0],2),round(zb[1][0],2),7,1.70,16.74,H11,P11,J6)
make('main_hall', 4.16,3.84,5,1.60, 9.60,3.70,0.70,J7)
make('main_hall_3roll_note',4.16,3.84,5,1.92,8.00,4.32,0.96,J7)
make('side_hall', 3.84,3.52,3,1.28, 7.04,3.10,0.54,J7)
make('small_house',3.20,2.88,3,1.28,6.40,2.75,0.45,J5)
make('gate_hall', 4.48,3.84,5,0.0 , 8.96,3.70,0.77,J7)
make('temple_hall',5.12,4.48,9,1.60,16.00,5.60,1.40,JB,rolled=False,over=2.16)
make('gallery',   2.88,2.88,1,0.0 , 2.24,2.40,0.30,[.5,.7][:1]+[.7],rolled=True)
make('pavilion_square',4.48,4.48,1,1.12,6.72,3.20,0.48,[.5,.7,.9],rolled=False)
make('storeyed_lower',3.20,2.88,5,1.28,6.40,3.20,0.45,J5)
for k,v in C.items():
    print(k,json.dumps(v,ensure_ascii=False))
print()
print('Primary examples of the rule')
print(' 卷二十 (S100): bay 14 chi -> H 11.2 chi = %.3f m, dia 1.12 chi = %.3f m' % (11.2*CHI,1.12*CHI))
print(' 小式 7-purlin (S101 quote): bay 11 chi -> H 8.8 chi = %.3f m, dia 0.77 chi = %.3f m' % (8.8*CHI,.77*CHI))
print(' 大式 doukou 2.5 cun=0.08 m (S101 quote): central bay 7 sets x 11 x 0.08 = %.2f m, next bay 6 x 11 x 0.08 = %.2f m; column+plate+brackets 70 x 0.08 = %.2f m; net 14.3 chi = %.2f m; roof overhang 21+6 doukou = %.2f m' % (7*11*.08,6*11*.08,70*.08,14.3*CHI,27*.08))
print()
print('Observed halls vs rule')
obs=[('春雨轩土地庙',3.20,2.56,.32,None,'S114'),('惠如春',3.20,2.75,None,None,'S111'),('雷峰夕照',3.20,2.91,None,None,'S111'),
     ('藏密楼 lower',3.20,3.20,.32,None,'S111'),('万字房',4.48,3.68,.58,.86,'S113'),('观澜堂',4.16,4.32,.96,1.12,'S111'),
     ('松风阁',None,3.10,.54,.70,'S111'),('正大光明殿',None,5.12,1.22,None,'S106;S02')]
for n,b,h,p,lo,src in obs:
    s=f' {n:10} H={h:.2f}'
    if b: s+=f' bay={b:.2f} H/bay={h/b:.2f}'
    if p: s+=f' plat={p:.2f} plat/H={p/h:.2f}'
    if lo: s+=f' 下出={lo:.2f} rule .8x.3H={.24*h:.2f}'
    print(s,src)
json.dump(C,open('research/typology/rules_out.json','w'),ensure_ascii=False,indent=1)
