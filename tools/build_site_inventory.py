#!/usr/bin/env python3
"""إنشاء جرد داخلي للصفحات والمقالات والصور والروابط."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
def jsonlds(text):
 for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S):
  try:yield json.loads(raw)
  except json.JSONDecodeError:pass
pages=[];articles=[]
for p in sorted(ROOT.rglob('*.html')):
 if 'node_modules' in p.parts:continue
 t=p.read_text(encoding='utf-8');rel=p.relative_to(ROOT).as_posix();title=re.search(r'<title>(.*?)</title>',t,re.S);desc=re.search(r'<meta name="description" content="([^"]+)',t);canonical=re.search(r'<link rel="canonical" href="([^"]+)',t);h1=re.search(r'<h1[^>]*>(.*?)</h1>',t,re.S)
 links=sorted(set(re.findall(r'<a[^>]+href="([^"]+)',t)));images=sorted(set(re.findall(r'<img[^>]+src="([^"]+)',t)))
 pages.append({'path':rel,'title':re.sub('<.*?>','',title.group(1)).strip() if title else None,'description':desc.group(1) if desc else None,'canonical':canonical.group(1) if canonical else None,'h1':re.sub('<.*?>','',h1.group(1)).strip() if h1 else None,'links':links,'images':images})
 article=next((x for x in jsonlds(t) if x.get('@type')=='Article'),None)
 if article:
  toc_match=re.search(r'<nav class="toc" aria-label="جدول محتويات المقال">.*?<ul>(.*?)</ul></nav>',t,re.S);toc=[{'id':a,'title':re.sub('<.*?>','',n).strip()} for a,n in re.findall(r'href="#([^"]+)">(.*?)</a>',toc_match.group(1),re.S)] if toc_match else []
  cover=re.search(r'<img class="art-img" src="([^"]+)" alt="([^"]+)',t)
  articles.append({'slug':p.stem,'path':rel,'headline':article.get('headline'),'category':article.get('articleSection'),'datePublished':article.get('datePublished'),'dateModified':article.get('dateModified'),'author':article.get('author'),'cover':{'src':cover.group(1),'alt':cover.group(2)} if cover else None,'toc':toc,'sources':[url for section in re.findall(r'<section class="sources".*?</section>',t,re.S) for url in re.findall(r'href="([^"]+)"',section)]})
out={'generated':'2026-08-17','summary':{'pages':len(pages),'articles':len(articles),'images':len(set(i for p in pages for i in p['images'])),'links':len(set(i for p in pages for i in p['links']))},'articles':articles,'pages':pages}
(ROOT/'docs'/'site-inventory.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(out['summary'])
