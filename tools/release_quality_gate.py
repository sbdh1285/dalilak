#!/usr/bin/env python3
"""بوابة الجودة النهائية قبل النشر."""
from pathlib import Path
import json,re,subprocess,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];errors=[]
pages=[p for p in ROOT.rglob('*.html') if 'node_modules' not in p.parts];posts=list((ROOT/'posts').glob('*.html'))
required={'title':r'<title>','description':r'<meta name="description"','canonical':r'<link rel="canonical"','og:title':r'<meta property="og:title"','og:description':r'<meta property="og:description"','og:url':r'<meta property="og:url"','og:image':r'<meta property="og:image"','robots':r'<meta name="robots"'}
for p in pages:
 t=p.read_text(encoding='utf-8');rel=p.relative_to(ROOT).as_posix()
 miss=[name for name,pat in required.items() if not re.search(pat,t)]
 if miss:errors.append((rel,'حقول مفقودة: '+', '.join(miss)))
 if t.count('<h1')!=1:errors.append((rel,f'عدد H1: {t.count("<h1")}'))
 if '<html lang="ar" dir="rtl">' not in t:errors.append((rel,'lang/RTL'))
 if p.name!='privacy-policy.html' and 'privacy-policy.html' not in t:errors.append((rel,'رابط الخصوصية مفقود'))
 if re.search(r'(?<!\d)0 (?:دقائق قراءة|تطبيقات|مقالات)',t):errors.append((rel,'قيمة صفر ظاهرة'))
 if re.search(r'privacy\.html',t):errors.append((rel,'رابط privacy.html خاطئ'))
# الوظائف المؤقتة
cfg=json.loads((ROOT/'site-config.json').read_text(encoding='utf-8'));ready=bool(cfg.get('contact',{}).get('enabled') and cfg.get('email'));forms=sum('<form' in p.read_text(encoding='utf-8') for p in pages);mailtos=set(x for p in pages for x in re.findall(r'mailto:([^"?]+)',p.read_text(encoding='utf-8')))
if ready:
 if forms!=1:errors.append(('contact',f'عدد النماذج {forms}'))
 if mailtos!={cfg['email']}:errors.append(('email',f'غير موحد {mailtos}'))
else:
 if forms:errors.append(('contact','نموذج غير عامل ظاهر'))
 if mailtos:errors.append(('email',f'بريد غير عامل ظاهر {mailtos}'))
# ملفات XML والإعلانات
for name in ('sitemap.xml','feed.xml'):
 try:ET.parse(ROOT/name)
 except Exception as e:errors.append((name,str(e)))
for p in ROOT.rglob('*'):
 if p.is_file() and p.suffix in {'.html','.js','.json','.txt'} and p.name!='ads.txt':
  try:t=p.read_text(encoding='utf-8')
  except UnicodeDecodeError:continue
  if re.search(r'adsbygoogle|ca-pub-[0-9]|pagead2\.googlesyndication',t):errors.append((str(p.relative_to(ROOT)),'كود إعلاني قبل الأوان'))
# شغّل الفحوص المتخصصة
for script in ('content_quality_audit.py','audit_site.py'):
 result=subprocess.run([sys.executable,str(ROOT/'tools'/script)],capture_output=True,text=True)
 if result.returncode:errors.append((script,result.stdout+result.stderr))
summary={'pages':len(pages),'articles':len(posts),'sources':sum('class="sources"' in p.read_text(encoding='utf-8') for p in posts),'mappedImages':len(json.loads((ROOT/'images'/'article-images.json').read_text(encoding='utf-8'))),'sitemapUrls':len(ET.parse(ROOT/'sitemap.xml').getroot()),'forms':forms,'publishedEmails':len(mailtos),'errors':len(errors)}
report=['# تقرير بوابة الجودة قبل النشر','',f'**التاريخ:** 17 أغسطس 2026  ',f'**النتيجة:** {"اجتاز" if not errors else "فشل"}','','## الملخص']+[f'- {k}: {v}' for k,v in summary.items()]+['','## الفحوص','- بنية الصفحات وحقول SEO وOpen Graph.','- H1 وlang وRTL وCanonical.','- تطابق جدول المحتويات وترتيب الخلاصة.','- الصور والمسارات والتكرار والنصوص البديلة.','- الروابط الداخلية والخصوصية والنموذج والبريد.','- sitemap وRSS وعدم وجود كود AdSense.','- أصالة المقالات وتشابه النصوص والمصادر المطلوبة.']
if errors:report+=['','## الأخطاء']+[f'- **{a}:** {b}' for a,b in errors]
(ROOT/'docs'/'release-quality-report.md').write_text('\n'.join(report)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False))
if errors:
 for x in errors:print('-',x)
 sys.exit(1)
