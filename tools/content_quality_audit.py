#!/usr/bin/env python3
"""فحص قيمة وأصالة واتساق جميع مقالات دليلك."""
from pathlib import Path
from html.parser import HTMLParser
import collections, hashlib, itertools, json, re, sys
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'site-config.json').read_text(encoding='utf-8'))
RISK={
'age-of-earth','ai-explained-simply','amazing-animal-facts','amazing-human-body-facts','amazing-water-facts','galaxies-and-stars','why-we-need-sleep',
'natural-cleaning-recipes','natural-insect-repellents','quick-kitchen-cleaning','laundry-guide-tips','eliminate-bad-smells','organize-fridge-waste','save-electricity-bill',
'protect-online-accounts','safe-online-payments','speed-up-slow-computer','save-mobile-data','essential-android-apps','choose-smartphone-budget',
'cleaning-products-never-mix','account-recovery-plan','used-smartphone-checklist','coffee-story-yemen'}
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,d):self.parts.append(d)
def visible(fragment):
 p=Text();p.feed(fragment);return ' '.join(' '.join(p.parts).split())
def article_data(text):
 for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S):
  d=json.loads(raw)
  if d.get('@type')=='Article':return d
errors=[];rows=[];bodies={};cover_refs=collections.defaultdict(list)
for p in sorted((ROOT/'posts').glob('*.html')):
 t=p.read_text(encoding='utf-8');a=article_data(t);slug=p.stem
 start=t.find('<div class="art-body">');ends=[x for x in (t.find('<!-- CLUSTER-LINKS-START -->',start),t.find('<section class="cluster-links"',start),t.find('<section class="sources"',start),t.find('<div class="share">',start)) if x>start];end=min(ends) if ends else len(t);body=visible(t[start:end]);bodies[slug]=body
 words=len(body.split());h2=len(re.findall(r'<h2(?:\s|>)',t[start:end]));sources='class="sources"' in t;desc=bool(re.search(r'<meta name="description" content=".{70,}">',t));author=a.get('author',{}) if a else {};cover=re.search(r'<img class="art-img" src="([^"]+)',t)
 if cover:cover_refs[cover.group(1)].append(slug)
 issues=[]
 if words<300:issues.append(f'محتوى قصير ({words} كلمة)')
 if h2<2:issues.append('تنظيم H2 ضعيف')
 if not desc:issues.append('وصف meta قصير أو مفقود')
 if not a:issues.append('Article schema مفقود')
 elif not author.get('name') or not author.get('url'):issues.append('بيانات الكاتب ناقصة')
 if slug in RISK and not sources:issues.append('المصادر مطلوبة لهذا الموضوع')
 if not cover or not (ROOT/cover.group(1).replace('../','')).exists():issues.append('غلاف مفقود')
 if issues:errors.append((slug,issues))
 rows.append((slug,words,h2,'نعم' if sources else 'غير مطلوبة/لا توجد','؛ '.join(issues) or 'اجتاز'))
# تشابه مقالات باستخدام مقاطع من خمس كلمات
shingles={s:set(zip(*(txt.split()[i:] for i in range(5)))) for s,txt in bodies.items()}
for a,b in itertools.combinations(shingles,2):
 score=len(shingles[a]&shingles[b])/max(1,len(shingles[a]|shingles[b]))
 if score>.12:errors.append((f'{a} / {b}',[f'تشابه مرتفع {score:.1%}']))
# الأغلفة يجب أن تكون مستقلة فعليًا
for ref,slugs in cover_refs.items():
 if len(slugs)>1:errors.append((ref,[f'غلاف مشترك: {slugs}']))
hashes=collections.defaultdict(list)
for ref,slugs in cover_refs.items():
 image_path=ROOT/ref.replace('../','')
 if image_path.exists():hashes[hashlib.sha256(image_path.read_bytes()).hexdigest()].extend(slugs)
for files in hashes.values():
 if len(files)>1:errors.append(('covers',[f'ملفات صور متطابقة لمقالات مختلفة: {files}']))
# اتساق العدد
search=json.loads((ROOT/'search-index.json').read_text(encoding='utf-8'))
if len(search)!=len(rows):errors.append(('count',[f'فهرس البحث {len(search)} والمقالات {len(rows)}']))
# الخصوصية والبريد والنموذج
pages=[p for p in ROOT.rglob('*.html') if 'node_modules' not in p.parts]
for p in pages:
 if p.name!='privacy-policy.html' and 'privacy-policy.html' not in p.read_text(encoding='utf-8'):errors.append((str(p.relative_to(ROOT)),['رابط الخصوصية مفقود']))
mailtos=[]
for p in pages:mailtos+=re.findall(r'mailto:([^"?]+)',p.read_text(encoding='utf-8'))
ready=bool(CFG.get('contact',{}).get('enabled') and CFG.get('email'))
forms=sum('<form' in p.read_text(encoding='utf-8') for p in pages)
if ready:
 if set(mailtos)!={CFG['email']}:errors.append(('email',[f'عناوين غير موحدة: {set(mailtos)}']))
 if forms!=1:errors.append(('contact',[f'عدد النماذج {forms} بدل 1']))
else:
 if mailtos:errors.append(('email',[f'يجب ألا يظهر بريد غير عامل: {set(mailtos)}']))
 if forms:errors.append(('contact',[f'النموذج يجب أن يكون محذوفًا مؤقتًا، الموجود {forms}']))
report=['# تقرير جودة المحتوى والأصالة','',f'**عدد المقالات:** {len(rows)}  ',f'**نتيجة الفحص:** {"اجتاز" if not errors else "يحتاج إصلاح"}','','| المقال | الكلمات | H2 | المصادر | النتيجة |','|---|---:|---:|---|---|']
report += [f'| `{s}` | {w} | {h} | {src} | {result} |' for s,w,h,src,result in rows]
report += ['','## فحوص إضافية',f'- أغلفة مستقلة: {len(cover_refs)} من {len(rows)}.',f'- تشابه مرتفع بين المقالات: {sum(1 for e in errors if "/" in e[0])}.',f'- البريد والنموذج: {"موحدان ومفعّلان" if ready else "غير منشورين حتى ربط الدومين"}.',f'- رابط الخصوصية: مفحوص في {len(pages)} صفحة.']
if errors:report+=['','## الأخطاء']+[f'- **{name}:** {"؛ ".join(items)}' for name,items in errors]
(ROOT/'docs'/'content-quality-audit.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
print(f'فحص الجودة: {len(rows)} مقالًا، {len(errors)} أخطاء.')
if errors:
 for e in errors:print('-',e)
 sys.exit(1)
