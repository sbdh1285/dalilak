#!/usr/bin/env python3
"""التحقق من حساب مدة القراءة وتطابقها في المقالات والبطاقات والصفحات التجميعية."""
from pathlib import Path
import re,sys
from redesign_magazine import article_records,reading_time_label
ROOT=Path(__file__).resolve().parents[1];records=article_records();errors=[];checked=0
for slug,a in records.items():
 expected=reading_time_label(a['minutes']);text=(ROOT/'posts'/f'{slug}.html').read_text(encoding='utf-8');meta=re.search(r'<div class="art-meta">.*?</div>',text,re.S)
 if not meta or f'{expected} قراءة' not in meta.group(0):errors.append((slug,'صفحة المقال',expected))
 checked+=1
for path in ROOT.rglob('*.html'):
 if 'node_modules' in path.parts:continue
 text=path.read_text(encoding='utf-8')
 if re.search(r'(?<!\d)0 (?:دقائق|دقيقة|دقيقتان)',text):errors.append((str(path.relative_to(ROOT)),'قيمة صفرية',''))
 if '2 دقائق قراءة' in text:errors.append((str(path.relative_to(ROOT)),'صياغة المثنى غير صحيحة','دقيقتان قراءة'))
 for block in re.findall(r'<article class="card[^>]*">.*?</article>',text,re.S):
  m=re.search(r'href="(?:\.\./)?posts/([^"/]+)\.html"',block)
  if not m or m.group(1) not in records:continue
  slug=m.group(1);expected=reading_time_label(records[slug]['minutes'])
  if f'{expected} قراءة' not in block:errors.append((str(path.relative_to(ROOT)),slug,expected))
  checked+=1
 for block in re.findall(r'<a class="story-row".*?</a>',text,re.S):
  m=re.search(r'href="(?:\.\./)?posts/([^"/]+)\.html"',block)
  if not m or m.group(1) not in records:continue
  slug=m.group(1);expected=reading_time_label(records[slug]['minutes'])
  if expected not in block:errors.append((str(path.relative_to(ROOT)),slug,expected))
  checked+=1
print(f'تم فحص {checked} موضعًا لمدة القراءة؛ الأخطاء: {len(errors)}.')
if errors:
 for e in errors:print('-',e)
 sys.exit(1)
