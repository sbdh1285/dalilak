#!/usr/bin/env python3
"""إنشاء صور تحريرية موضوعية وفريدة للمقالات التي لا تملك صورة فوتوغرافية."""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,random,re,math
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'images'/'covers';OUT.mkdir(parents=True,exist_ok=True)
PHOTOS={
'lemon-mint-drink':('images/new-lemon-mint-drink.jpg','كأس عصير ليمون ونعناع مثلج مع شرائح ليمون وأوراق نعناع'),
'samosa-cheese-dough':('images/new-samosa-cheese-dough.jpg','سمبوسك جبن ذهبي مقرمش مقدم على طبق خزفي'),
'laundry-guide-tips':('images/new-laundry-guide-tips.jpg','ملابس قطنية مطوية بعناية بجوار سلة غسيل'),
'qishta-basbousa':('images/new-qishta-basbousa.jpg','قطع بسبوسة بالقشطة واللوز على طبق تقديم'),
'natural-insect-repellents':('images/new-natural-insect-repellents.jpg','نباتات ريحان ونعناع قرب نافذة منزلية مزودة بشبك'),
'speed-up-slow-computer':('images/new-speed-up-slow-computer.jpg','حاسوب مكتبي في مساحة عمل تقنية مرتبة'),
'save-mobile-data':('images/new-save-mobile-data.jpg','هاتف ذكي بجوار جهاز اتصال على مكتب'),
'quick-kitchen-cleaning':('images/new-quick-kitchen-cleaning.jpg','مطبخ مرتب مع أدوات تنظيف مناسبة للأسطح')}
SCENES={
'account-recovery-plan':'recovery','age-of-earth':'earth','ai-explained-simply':'ai','amazing-animal-facts':'animal','amazing-human-body-facts':'human','amazing-water-facts':'water','chicken-kabsa':'kabsa','choose-smartphone-budget':'phones','cleaning-products-never-mix':'chemical','coffee-story-yemen':'coffee','eliminate-bad-smells':'air','essential-android-apps':'apps','fruit-salad-recipe':'fruit','galaxies-and-stars':'galaxy','gulf-rice-spices-guide':'spices','lentil-soup-recipe':'soup','natural-cleaning-recipes':'naturalclean','orange-cake-no-oven':'cake','organize-fridge-waste':'fridge','protect-online-accounts':'shield','safe-online-payments':'payment','save-electricity-bill':'energy','tidy-home-in-15-minutes':'tidy','used-smartphone-checklist':'usedphone','why-we-need-sleep':'sleep','zaatar-manakeesh':'flatbread'}
ALTS={
'recovery':'مفتاح ورموز احتياطية حول قفل رقمي لاسترداد الحسابات','earth':'كوكب الأرض مع طبقات صخرية ومدار زمني','ai':'شريحة ذكاء اصطناعي محاطة بعقد شبكة مترابطة','animal':'حوت وأخطبوط وآثار أقدام ترمز إلى تنوع الحيوانات','human':'قلب ودماغ وعظام ضمن رسم تشريحي مبسط','water':'قطرات ماء وأمواج ودورة مائية مبسطة','kabsa':'طبق أرز بسمتي ودجاج وبهارات خليجية','phones':'ثلاثة هواتف مع علامات مقارنة واختيار','chemical':'عبوتا تنظيف منفصلتان مع علامة منع الخلط','coffee':'فنجان قهوة وحبوب ومدرجات جبلية ترمز إلى اليمن','air':'نافذة مفتوحة وتيارات هواء تزيل مصدر الرائحة','apps':'هاتف يعرض شبكة تطبيقات متنوعة بلا شعارات','fruit':'وعاء فواكه ملونة مع تفاح وبرتقال وعنب','galaxy':'مجرة حلزونية ونجوم وكواكب في فضاء عميق','spices':'أوعية بهارات وقرفة وهيل ولومي مجفف','soup':'وعاء شوربة عدس ساخنة مع ليمون وكمون','naturalclean':'ليمون وعبوة تنظيف وفرشاة للأسطح المنزلية','cake':'قطعة كيكة برتقال وقدر طهي وشرائح برتقال','fridge':'ثلاجة مفتوحة برفوف مرتبة وعلب طعام واضحة','shield':'درع وقفل ومفتاح مرور لحماية الحسابات','payment':'بطاقة دفع داخل درع مع علامة تحقق','energy':'مصباح LED ومكيف وعداد استهلاك منزلي','tidy':'غرفة مرتبة مع رف وسلة ومؤقت','usedphone':'هاتف تحت عدسة فحص مع بطارية وعلامة تحقق','sleep':'سرير وهلال ونجوم في غرفة هادئة','flatbread':'مناقيش زعتر دائرية مع زيت زيتون وأوراق زعتر'}
PALETTES={
'نصائح منزلية':('#f4f0e7','#155b55','#d67b35','#c9ddd6'),
'وصفات لذيذة':('#f7efe2','#913f2e','#dd9337','#e8c79e'),
'معلومات عامة':('#edf2ef','#284f6d','#bc6b3d','#c8dce3'),
'تكنولوجيا':('#edf1f0','#173f49','#d4773f','#bad2d0')}
def article(path):
 t=path.read_text(encoding='utf-8')
 for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',t,re.S):
  d=json.loads(raw)
  if d.get('@type')=='Article':return d
def line(draw,points,color,width=12):draw.line(points,fill=color,width=width,joint='curve')
def icon(draw,scene,cx,cy,s,dark,accent,soft,bg):
 w=max(7,int(s*.035))
 if scene in {'recovery','shield'}:
  draw.polygon([(cx,cy-s*.5),(cx+s*.42,cy-s*.32),(cx+s*.34,cy+s*.24),(cx,cy+s*.5),(cx-s*.34,cy+s*.24),(cx-s*.42,cy-s*.32)],fill=dark)
  draw.rounded_rectangle((cx-s*.18,cy-s*.05,cx+s*.18,cy+s*.24),radius=18,fill=accent);draw.arc((cx-s*.14,cy-s*.25,cx+s*.14,cy+s*.06),180,360,fill=accent,width=w)
  if scene=='recovery':line(draw,[(cx+s*.35,cy+s*.2),(cx+s*.58,cy+s*.2),(cx+s*.58,cy+s*.36)],accent,w)
 elif scene=='earth':
  draw.ellipse((cx-s*.47,cy-s*.47,cx+s*.47,cy+s*.47),fill=dark);draw.polygon([(cx-s*.3,cy-s*.2),(cx-s*.05,cy-s*.35),(cx+s*.1,cy-s*.15),(cx+s*.34,cy-s*.05),(cx+s*.15,cy+s*.12),(cx-s*.08,cy+s*.08),(cx-s*.22,cy+s*.28),(cx-s*.38,cy+s*.12)],fill=soft);draw.arc((cx-s*.68,cy-s*.25,cx+s*.68,cy+s*.25),5,175,fill=accent,width=w)
 elif scene=='ai':
  draw.rounded_rectangle((cx-s*.34,cy-s*.34,cx+s*.34,cy+s*.34),radius=30,fill=dark);draw.ellipse((cx-s*.08,cy-s*.08,cx+s*.08,cy+s*.08),fill=accent)
  for a in range(0,360,45):
   x=cx+math.cos(math.radians(a))*s*.62;y=cy+math.sin(math.radians(a))*s*.62;line(draw,[(cx,cy),(x,y)],dark,w//2);draw.ellipse((x-18,y-18,x+18,y+18),fill=accent)
 elif scene=='animal':
  draw.ellipse((cx-s*.42,cy-s*.18,cx+s*.28,cy+s*.2),fill=dark);draw.polygon([(cx+s*.25,cy-s*.12),(cx+s*.55,cy-s*.32),(cx+s*.48,cy),(cx+s*.58,cy+s*.22),(cx+s*.24,cy+s*.12)],fill=dark);draw.ellipse((cx-s*.5,cy-s*.02,cx-s*.38,cy+s*.1),fill=accent)
  for x,y in [(-.28,.4),(-.08,.34),(.12,.36),(.3,.44)]:draw.ellipse((cx+s*x-18,cy+s*y-22,cx+s*x+18,cy+s*y+22),fill=accent)
 elif scene=='human':
  draw.polygon([(cx,cy+s*.45),(cx-s*.42,cy),(cx-s*.35,cy-s*.32),(cx-s*.08,cy-s*.42),(cx,cy-s*.18),(cx+s*.08,cy-s*.42),(cx+s*.35,cy-s*.32),(cx+s*.42,cy)],fill=accent);draw.ellipse((cx+s*.18,cy-s*.55,cx+s*.55,cy-s*.2),outline=dark,width=w);line(draw,[(cx+s*.36,cy-s*.5),(cx+s*.36,cy-s*.25)],dark,w//2)
 elif scene=='water':
  for ox,scale,col in [(-.28,.62,dark),(.18,.48,accent),(.42,.3,dark)]:
   x=cx+s*ox;ss=s*scale;draw.polygon([(x,cy-ss*.55),(x-ss*.35,cy+ss*.08),(x-ss*.24,cy+ss*.36),(x,cy+ss*.48),(x+ss*.24,cy+ss*.36),(x+ss*.35,cy+ss*.08)],fill=col)
  line(draw,[(cx-s*.55,cy+s*.48),(cx-s*.2,cy+s*.38),(cx+s*.15,cy+s*.48),(cx+s*.55,cy+s*.35)],dark,w)
 elif scene in {'kabsa','fruit','soup','flatbread','spices','cake'}:
  if scene=='soup':draw.ellipse((cx-s*.5,cy-s*.18,cx+s*.5,cy+s*.4),fill=dark);draw.ellipse((cx-s*.4,cy-s*.23,cx+s*.4,cy+s*.2),fill=accent);line(draw,[(cx-s*.2,cy-s*.35),(cx-s*.1,cy-s*.55)],dark,w);line(draw,[(cx+s*.1,cy-s*.35),(cx+s*.2,cy-s*.58)],dark,w)
  elif scene=='fruit':
   draw.arc((cx-s*.5,cy-s*.12,cx+s*.5,cy+s*.48),0,180,fill=dark,width=w*2);draw.line((cx-s*.48,cy+s*.18,cx+s*.48,cy+s*.18),fill=dark,width=w)
   for ox,oy,r,col in [(-.28,-.04,.14,accent),(-.02,-.13,.17,dark),(.25,-.02,.15,accent),(.08,.06,.12,soft)]:draw.ellipse((cx+s*(ox-r),cy+s*(oy-r),cx+s*(ox+r),cy+s*(oy+r)),fill=col,outline=dark,width=w//3)
   line(draw,[(cx-s*.04,cy-s*.28),(cx+s*.08,cy-s*.43)],dark,w//2)
  elif scene=='kabsa':
   draw.ellipse((cx-s*.52,cy-s*.28,cx+s*.52,cy+s*.4),fill=dark);draw.ellipse((cx-s*.4,cy-s*.2,cx+s*.4,cy+s*.26),fill=accent)
   for ox,oy in [(-.25,-.04),(-.08,.08),(.12,-.08),(.28,.08)]:draw.ellipse((cx+s*ox-16,cy+s*oy-9,cx+s*ox+16,cy+s*oy+9),fill=soft)
   draw.ellipse((cx-s*.12,cy-s*.26,cx+s*.24,cy+s*.02),fill=dark);draw.ellipse((cx+s*.17,cy-s*.2,cx+s*.43,cy+s*.06),fill=dark);draw.ellipse((cx+s*.37,cy-s*.12,cx+s*.5,cy+s*.02),fill=soft)
  elif scene=='cake':draw.polygon([(cx-s*.42,cy+s*.32),(cx+s*.42,cy+s*.32),(cx+s*.25,cy-s*.35),(cx-s*.25,cy-s*.35)],fill=accent);draw.rectangle((cx-s*.28,cy-s*.08,cx+s*.3,cy+s*.02),fill=bg);draw.ellipse((cx+s*.3,cy-s*.52,cx+s*.55,cy-s*.27),outline=dark,width=w)
  elif scene=='flatbread':
   for ox,oy in [(-.25,-.05),(.18,.02),(.02,.28)]:draw.ellipse((cx+s*(ox-.28),cy+s*(oy-.18),cx+s*(ox+.28),cy+s*(oy+.18)),fill=accent,outline=dark,width=w//2)
   for ox,oy in [(-.32,-.1),(.1,.0),(.05,.28)]:draw.ellipse((cx+s*ox-8,cy+s*oy-8,cx+s*ox+8,cy+s*oy+8),fill=dark)
  elif scene=='spices':
   for ox,col in [(-.32,dark),(0,accent),(.32,dark)]:draw.ellipse((cx+s*(ox-.22),cy-s*.05,cx+s*(ox+.22),cy+s*.28),fill=col);draw.ellipse((cx+s*(ox-.18),cy-s*.1,cx+s*(ox+.18),cy+s*.12),fill=soft)
   line(draw,[(cx-s*.48,cy-s*.4),(cx+s*.45,cy-s*.18)],accent,w);line(draw,[(cx-s*.42,cy-s*.5),(cx+s*.38,cy-s*.28)],dark,w)
  else:
   draw.ellipse((cx-s*.52,cy-s*.32,cx+s*.52,cy+s*.38),fill=dark);draw.ellipse((cx-s*.4,cy-s*.23,cx+s*.4,cy+s*.25),fill=accent)
   colors=[soft,bg,dark,soft]
   for i,(ox,oy) in enumerate([(-.22,-.04),(.08,-.08),(.28,.1),(-.05,.15)]):draw.ellipse((cx+s*ox-30,cy+s*oy-30,cx+s*ox+30,cy+s*oy+30),fill=colors[i])
 elif scene in {'phones','apps','usedphone'}:
  xs=[0] if scene!='phones' else [-.34,0,.34]
  for ox in xs:
   x=cx+s*ox;draw.rounded_rectangle((x-s*.18,cy-s*.43,x+s*.18,cy+s*.43),radius=24,outline=dark,width=w);draw.line((x-s*.07,cy+s*.34,x+s*.07,cy+s*.34),fill=accent,width=w)
  if scene=='apps':
   for ix in [-.08,.08]:
    for iy in [-.16,0,.16]:draw.rounded_rectangle((cx+s*ix-20,cy+s*iy-20,cx+s*ix+20,cy+s*iy+20),radius=6,fill=accent if iy else dark)
  if scene=='usedphone':draw.ellipse((cx+s*.05,cy-s*.25,cx+s*.5,cy+s*.2),outline=accent,width=w*2);line(draw,[(cx+s*.38,cy+s*.12),(cx+s*.6,cy+s*.38)],accent,w*2)
 elif scene=='chemical':
  for ox,col in [(-.22,dark),(.22,accent)]:
   draw.rounded_rectangle((cx+s*(ox-.18),cy-s*.12,cx+s*(ox+.18),cy+s*.43),radius=20,fill=col);draw.rectangle((cx+s*(ox-.08),cy-s*.3,cx+s*(ox+.08),cy-s*.1),fill=col)
  line(draw,[(cx-s*.45,cy-s*.48),(cx+s*.45,cy+s*.48)],dark,w*2);line(draw,[(cx+s*.45,cy-s*.48),(cx-s*.45,cy+s*.48)],dark,w*2)
 elif scene=='coffee':
  for i in range(4):line(draw,[(cx-s*.58+i*18,cy-s*.5+i*28),(cx+s*.1+i*18,cy-s*.5+i*28)],soft,w//2)
  draw.rounded_rectangle((cx-s*.38,cy-s*.18,cx+s*.22,cy+s*.34),radius=25,fill=dark);draw.arc((cx+s*.05,cy-s*.08,cx+s*.48,cy+s*.28),270,90,fill=dark,width=w*2)
  for ox in [-.2,0,.2]:draw.ellipse((cx+s*ox-22,cy+s*.48-16,cx+s*ox+22,cy+s*.48+16),fill=accent)
  line(draw,[(cx-s*.2,cy-s*.32),(cx-s*.1,cy-s*.55)],accent,w)
 elif scene=='air':
  draw.rectangle((cx-s*.48,cy-s*.42,cx+s*.1,cy+s*.42),outline=dark,width=w);line(draw,[(cx-s*.18,cy-s*.42),(cx-s*.18,cy+s*.42)],dark,w//2);line(draw,[(cx-s*.48,cy),(cx+s*.1,cy)],dark,w//2)
  for oy in [-.22,0,.22]:draw.arc((cx,cy+s*oy-45,cx+s*.55,cy+s*oy+45),180,350,fill=accent,width=w)
 elif scene=='galaxy':
  for r in [s*.18,s*.33,s*.48]:draw.arc((cx-r,cy-r*.55,cx+r,cy+r*.55),10,335,fill=dark if r!=s*.33 else accent,width=w)
  draw.ellipse((cx-22,cy-22,cx+22,cy+22),fill=accent)
  for ox,oy in [(-.5,-.35),(.48,-.28),(.4,.38),(-.42,.3)]:draw.ellipse((cx+s*ox-10,cy+s*oy-10,cx+s*ox+10,cy+s*oy+10),fill=dark)
 elif scene=='naturalclean':
  draw.rounded_rectangle((cx-s*.34,cy-s*.1,cx-s*.02,cy+s*.42),radius=18,fill=dark);draw.rectangle((cx-s*.26,cy-s*.28,cx-s*.1,cy-s*.08),fill=dark);draw.ellipse((cx+s*.05,cy-s*.28,cx+s*.46,cy+s*.15),fill=accent);line(draw,[(cx+s*.1,cy-s*.05),(cx+s*.4,cy-s*.18)],soft,w)
 elif scene=='fridge':
  draw.rounded_rectangle((cx-s*.36,cy-s*.52,cx+s*.36,cy+s*.52),radius=20,fill=dark);line(draw,[(cx-s*.36,cy-s*.08),(cx+s*.36,cy-s*.08)],accent,w)
  for x,y,col in [(-.17,-.3,soft),(.12,-.28,accent),(-.15,.12,accent),(.14,.16,soft)]:draw.rounded_rectangle((cx+s*x-35,cy+s*y-25,cx+s*x+35,cy+s*y+25),radius=8,fill=col)
 elif scene=='payment':
  draw.rounded_rectangle((cx-s*.48,cy-s*.28,cx+s*.3,cy+s*.28),radius=28,fill=dark);draw.rectangle((cx-s*.38,cy-s*.08,cx-s*.08,cy+s*.02),fill=accent);draw.polygon([(cx+s*.3,cy-s*.45),(cx+s*.56,cy-s*.32),(cx+s*.5,cy+s*.12),(cx+s*.3,cy+s*.35),(cx+s*.1,cy+s*.12),(cx+s*.04,cy-s*.32)],fill=accent)
 elif scene=='energy':
  draw.ellipse((cx-s*.28,cy-s*.48,cx+s*.28,cy+s*.08),outline=dark,width=w*2);draw.rectangle((cx-s*.12,cy+s*.06,cx+s*.12,cy+s*.32),fill=dark);line(draw,[(cx-s*.5,cy-s*.14),(cx-s*.36,cy-s*.14)],accent,w);line(draw,[(cx+s*.36,cy-s*.14),(cx+s*.5,cy-s*.14)],accent,w);draw.arc((cx-s*.48,cy+s*.18,cx+s*.48,cy+s*.55),190,350,fill=accent,width=w)
 elif scene=='tidy':
  draw.rectangle((cx-s*.5,cy-s*.42,cx+s*.5,cy+s*.42),outline=dark,width=w);line(draw,[(cx-s*.5,cy-s*.05),(cx+s*.5,cy-s*.05)],dark,w);draw.rectangle((cx-s*.35,cy-s*.32,cx-s*.08,cy-s*.12),fill=accent);draw.rectangle((cx+s*.05,cy-s*.32,cx+s*.32,cy-s*.12),fill=soft);draw.rectangle((cx-s*.2,cy+s*.05,cx+s*.22,cy+s*.32),fill=accent)
 elif scene=='sleep':
  draw.rectangle((cx-s*.5,cy+s*.12,cx+s*.48,cy+s*.38),fill=dark);draw.rectangle((cx-s*.42,cy-s*.1,cx+s*.3,cy+s*.14),fill=soft);draw.ellipse((cx+s*.16,cy-s*.55,cx+s*.48,cy-s*.23),fill=accent);draw.ellipse((cx+s*.28,cy-s*.58,cx+s*.54,cy-s*.3),fill=bg)
def cover(slug,title,cat,scene):
 bg,dark,accent,soft=PALETTES[cat];seed=int(hashlib.sha256(slug.encode()).hexdigest()[:12],16);rng=random.Random(seed);im=Image.new('RGB',(1200,630),bg);d=ImageDraw.Draw(im)
 variant=seed%5
 if variant==0:d.ellipse((690,-180,1240,370),fill=soft);d.rectangle((0,500,1200,630),fill=dark);cx,cy=560,285
 elif variant==1:d.polygon([(0,0),(520,0),(360,630),(0,630)],fill=dark);d.ellipse((760,70,1180,490),fill=soft);cx,cy=820,300
 elif variant==2:d.rounded_rectangle((85,75,1115,555),radius=65,fill=soft);d.rectangle((0,0,1200,22),fill=accent);cx,cy=600,315
 elif variant==3:d.ellipse((-160,110,420,690),fill=soft);d.rectangle((875,0,1200,630),fill=dark);cx,cy=600,300
 else:d.polygon([(0,0),(1200,0),(1200,240),(0,560)],fill=soft);d.ellipse((110,270,500,660),fill=dark);cx,cy=720,330
 # نقاط تحريرية خفيفة لا تتداخل مع الموضوع
 for _ in range(4):
  x=rng.randint(70,1130);y=rng.randint(60,570);r=rng.randint(8,18);d.ellipse((x-r,y-r,x+r,y+r),fill=accent)
 icon(d,scene,cx,cy,280,dark,accent,soft,bg)
 d.rectangle((55,52,175,62),fill=accent);d.rectangle((55,82,265,90),fill=dark if variant!=1 else soft)
 p=OUT/f'{slug}.jpg';im.save(p,quality=90,optimize=True,progressive=True);return {'path':f'images/covers/{slug}.jpg','alt':ALTS[scene]}
def main():
 mapping={};generated={}
 for path in sorted((ROOT/'posts').glob('*.html')):
  a=article(path);slug=path.stem
  if slug in PHOTOS:mapping[slug]={'path':PHOTOS[slug][0],'alt':PHOTOS[slug][1]}
  else:
   scene=SCENES.get(slug,'tidy');mapping[slug]=cover(slug,a['headline'],a['articleSection'],scene);generated[slug]=mapping[slug]['alt']
 (ROOT/'images'/'article-images.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(OUT/'cover-alts.json').write_text(json.dumps(generated,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 # حذف أغلفة قديمة غير مستخدمة
 used={Path(x['path']).name for x in mapping.values() if x['path'].startswith('images/covers/')}
 for p in OUT.glob('*.jpg'):
  if p.name not in used:p.unlink()
 print(f'تم تجهيز {len(mapping)} صورة: {len(PHOTOS)} فوتوغرافية و{len(generated)} رسومات موضوعية فريدة.')
if __name__=='__main__':main()
