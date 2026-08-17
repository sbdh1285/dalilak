#!/usr/bin/env python3
"""إنشاء أغلفة تحريرية مستقلة لكل مقال دون نصوص أو تدرجات."""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json, random, re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'images'/'covers';OUT.mkdir(parents=True,exist_ok=True)
PALETTES={
'نصائح منزلية':('#f3eee4','#155c56','#d77832','#d8e5df'),
'وصفات لذيذة':('#f6eee2','#8c3f2e','#d68b35','#e7c9a7'),
'معلومات عامة':('#edf1eb','#294c68','#b86b3d','#cad9df'),
'تكنولوجيا':('#edf0ef','#173e48','#cf713c','#b9d0cf')}

def data(path):
 t=path.read_text(encoding='utf-8')
 for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',t,re.S):
  x=json.loads(raw)
  if x.get('@type')=='Article':return x

def icon_kind(slug,title,cat):
 s=slug+' '+title
 for keys,kind in [
  (('clean','smell','insect','kitchen'), 'clean'),(('laundry',),'laundry'),(('fridge',),'fridge'),(('electric',),'bulb'),
  (('account','payment','recovery'), 'lock'),(('smartphone','mobile','android','used-phone'), 'phone'),(('computer','ai-'), 'laptop'),
  (('sleep',),'moon'),(('water',),'water'),(('animal',),'paw'),(('earth','galax'), 'orbit'),(('coffee',),'coffee'),
  (('kabsa','soup','cake','salad','basbousa','samosa','manakeesh','drink','spices'), 'food')]:
  if any(k in s for k in keys):return kind
 return 'food' if cat=='وصفات لذيذة' else 'book'

def draw_icon(d,kind,cx,cy,s,color,accent):
 w=max(5,s//30)
 if kind=='phone':
  d.rounded_rectangle((cx-s*.34,cy-s*.55,cx+s*.34,cy+s*.55),radius=s*.08,outline=color,width=w);d.line((cx-s*.12,cy+s*.43,cx+s*.12,cy+s*.43),fill=accent,width=w)
 elif kind=='lock':
  d.rounded_rectangle((cx-s*.42,cy-s*.05,cx+s*.42,cy+s*.48),radius=s*.07,fill=color);d.arc((cx-s*.27,cy-s*.48,cx+s*.27,cy+s*.15),180,360,fill=color,width=w*2);d.ellipse((cx-s*.05,cy+s*.14,cx+s*.05,cy+s*.25),fill=accent)
 elif kind=='laptop':
  d.rounded_rectangle((cx-s*.48,cy-s*.42,cx+s*.48,cy+s*.28),radius=s*.04,outline=color,width=w);d.polygon([(cx-s*.62,cy+s*.34),(cx+s*.62,cy+s*.34),(cx+s*.48,cy+s*.48),(cx-s*.48,cy+s*.48)],fill=color);d.rectangle((cx-s*.2,cy-s*.15,cx+s*.2,cy+s*.04),fill=accent)
 elif kind=='clean':
  d.rounded_rectangle((cx-s*.28,cy-s*.15,cx+s*.28,cy+s*.5),radius=s*.08,fill=color);d.rectangle((cx-s*.12,cy-s*.38,cx+s*.12,cy-s*.13),fill=color);d.line((cx,cy-s*.38,cx+s*.32,cy-s*.5),fill=color,width=w);d.ellipse((cx+s*.42,cy-s*.38,cx+s*.5,cy-s*.3),fill=accent)
 elif kind=='laundry':
  d.polygon([(cx-s*.5,cy-s*.32),(cx-s*.2,cy-s*.52),(cx-s*.08,cy-s*.3),(cx+s*.08,cy-s*.3),(cx+s*.2,cy-s*.52),(cx+s*.5,cy-s*.32),(cx+s*.32,cy),(cx+s*.28,cy+s*.52),(cx-s*.28,cy+s*.52),(cx-s*.32,cy),(cx-s*.5,cy-s*.32)],fill=color);d.line((cx-s*.2,cy+s*.1,cx+s*.2,cy+s*.1),fill=accent,width=w)
 elif kind=='fridge':
  d.rounded_rectangle((cx-s*.36,cy-s*.55,cx+s*.36,cy+s*.55),radius=s*.04,fill=color);d.line((cx-s*.36,cy-s*.12,cx+s*.36,cy-s*.12),fill=accent,width=w);d.line((cx+s*.2,cy-s*.02,cx+s*.2,cy+s*.16),fill=accent,width=w)
 elif kind=='bulb':
  d.ellipse((cx-s*.38,cy-s*.5,cx+s*.38,cy+s*.23),outline=color,width=w*2);d.rectangle((cx-s*.17,cy+s*.2,cx+s*.17,cy+s*.48),fill=color);d.line((cx-s*.6,cy-s*.12,cx-s*.45,cy-s*.12),fill=accent,width=w);d.line((cx+s*.45,cy-s*.12,cx+s*.6,cy-s*.12),fill=accent,width=w)
 elif kind=='moon':
  d.ellipse((cx-s*.48,cy-s*.48,cx+s*.48,cy+s*.48),fill=color);d.ellipse((cx-s*.2,cy-s*.58,cx+s*.54,cy+s*.22),fill=accent)
 elif kind=='water':
  for ox,scale in [(-.25,.65),(.25,.48),(0,.36)]:
   ss=s*scale;x=cx+s*ox;y=cy+s*(.18 if ox else -.28);d.polygon([(x,y-ss*.55),(x-ss*.35,y+ss*.05),(x-ss*.25,y+ss*.35),(x,y+ss*.48),(x+ss*.25,y+ss*.35),(x+ss*.35,y+ss*.05)],fill=color if ox<=0 else accent)
 elif kind=='paw':
  d.ellipse((cx-s*.32,cy-s*.05,cx+s*.32,cy+s*.48),fill=color)
  for ox,oy in [(-.4,-.25),(-.13,-.42),(.16,-.42),(.42,-.22)]:d.ellipse((cx+s*(ox-.12),cy+s*(oy-.14),cx+s*(ox+.12),cy+s*(oy+.14)),fill=accent)
 elif kind=='orbit':
  d.ellipse((cx-s*.18,cy-s*.18,cx+s*.18,cy+s*.18),fill=accent);d.ellipse((cx-s*.55,cy-s*.3,cx+s*.55,cy+s*.3),outline=color,width=w);d.ellipse((cx-s*.32,cy-s*.55,cx+s*.32,cy+s*.55),outline=color,width=w);d.ellipse((cx+s*.4,cy-s*.12,cx+s*.52,cy),fill=color)
 elif kind=='coffee':
  d.rounded_rectangle((cx-s*.42,cy-s*.18,cx+s*.24,cy+s*.38),radius=s*.08,fill=color);d.arc((cx+s*.08,cy-s*.06,cx+s*.55,cy+s*.3),270,90,fill=color,width=w*2);d.arc((cx-s*.22,cy-s*.58,cx,cy-s*.12),180,355,fill=accent,width=w)
 elif kind=='food':
  d.ellipse((cx-s*.56,cy-s*.35,cx+s*.56,cy+s*.45),fill=color);d.ellipse((cx-s*.42,cy-s*.24,cx+s*.42,cy+s*.32),fill=accent);d.ellipse((cx-s*.17,cy-s*.1,cx+s*.04,cy+s*.11),fill=color);d.ellipse((cx+s*.1,cy-s*.14,cx+s*.32,cy+s*.06),fill=color)
 else:
  d.polygon([(cx-s*.55,cy-s*.4),(cx-s*.04,cy-s*.28),(cx,cy+s*.48),(cx-s*.5,cy+s*.34)],fill=color);d.polygon([(cx+s*.55,cy-s*.4),(cx+s*.04,cy-s*.28),(cx,cy+s*.48),(cx+s*.5,cy+s*.34)],fill=accent)

def make(slug,title,cat):
 bg,dark,accent,soft=PALETTES[cat];seed=int(hashlib.sha256(slug.encode()).hexdigest()[:12],16);rng=random.Random(seed)
 im=Image.new('RGB',(1200,630),bg);d=ImageDraw.Draw(im)
 # بنية تحريرية ثابتة مع تفاصيل مختلفة لكل مقال
 d.rectangle((0,0,430,630),fill=dark);d.rectangle((430,0,448,630),fill=accent)
 for _ in range(8):
  x=rng.randint(500,1150);y=rng.randint(30,600);r=rng.randint(12,50);d.ellipse((x-r,y-r,x+r,y+r),fill=soft)
 d.rounded_rectangle((525,95,1080,535),radius=22,fill=soft)
 draw_icon(d,icon_kind(slug,title,cat),805,315,260,dark,accent)
 # علامة تحريرية صغيرة غير نصية
 d.rectangle((65,72,220,82),fill=accent);d.rectangle((65,105,330,116),fill=soft);d.rectangle((65,137,280,148),fill=soft)
 d.line((520,565,1090,565),fill=dark,width=3)
 im.save(OUT/f'{slug}.jpg',quality=88,optimize=True,progressive=True)
 return f'رسم تحريري مستقل يرمز إلى موضوع «{title}»'

def main():
 alts={}
 for path in sorted((ROOT/'posts').glob('*.html')):
  x=data(path)
  if x:alts[path.stem]=make(path.stem,x['headline'],x['articleSection'])
 (OUT/'cover-alts.json').write_text(json.dumps(alts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f'تم إنشاء {len(alts)} غلافًا تحريريًا مستقلًا.')
if __name__=='__main__':main()
