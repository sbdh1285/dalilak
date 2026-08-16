#!/usr/bin/env python3
# تحسينات موقع dalilak: إصلاح فهرس البحث، صفحات جديدة، مخطط WebSite، إصلاح روابط نتائج البحث.
import os, re, json

ROOT = os.path.dirname(os.path.abspath(__file__))

def read(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()

def write(p, t):
    open(os.path.join(ROOT, p), "w", encoding="utf-8").write(t)

# 1) استخراج CSS من about.html ليكون موحّدًا
about = read("about.html")
css = re.search(r"<style>(.*?)</style>", about, re.S).group(1)

# 2) عناصر مشتركة
HEADER = '''<header><div class="wrap hbar">
  <a class="logo" href="index.html"><span class="logo-ic">📘</span> دليلك</a>
  <nav id="nav"><a href="index.html">الرئيسية</a><a href="category/home-tips.html">نصائح منزلية</a><a href="category/recipes.html">وصفات لذيذة</a><a href="category/knowledge.html">معلومات عامة</a><a href="category/tech.html">تكنولوجيا</a><a href="about.html">من نحن</a><a href="contact.html">اتصل بنا</a></nav>
  <div class="h-actions">
    <div class="search-box">
      <input class="icon-btn" id="searchInput" placeholder="🔍" style="width:150px;text-align:right;padding:0 12px;font-family:inherit">
      <div class="search-res" id="searchRes"></div>
    </div>
    <button class="icon-btn" id="themeBtn" title="الوضع الليلي">🌙</button>
    <button class="icon-btn burger" id="burger" aria-label="القائمة">☰</button>
  </div>
</div></header>'''

FOOTER = '''<footer><div class="wrap">
  <div class="fgrid">
    <div>
      <div class="logo-ic" style="width:44px;height:44px;font-size:1.3rem">📘</div>
      <h4 style="margin:10px 0 8px">دليلك</h4>
      <p>دليلك اليومي لنصائح عملية، وصفات شهية، ومعلومات مفيدة. محتوى عربي أصلي، مكتوب بعناية، ويحدّث باستمرار ليقدم لك الفائدة أولًا.</p>
    </div>
    <div>
      <h4>الأقسام</h4>
      <a href="category/home-tips.html">نصائح منزلية</a><a href="category/recipes.html">وصفات لذيذة</a><a href="category/knowledge.html">معلومات عامة</a><a href="category/tech.html">تكنولوجيا</a>
    </div>
    <div>
      <h4>روابط مهمة</h4>
      <a href="about.html">من نحن</a>
      <a href="contact.html">اتصل بنا</a>
      <a href="privacy-policy.html">سياسة الخصوصية</a>
      <a href="terms.html">شروط الاستخدام</a>
      <a href="disclaimer.html">إخلاء المسؤولية</a>
      <a href="sitemap.html">خريطة الموقع</a>
    </div>
    <div>
      <h4>تواصل معنا</h4>
      <p>📧 contact@dalilak.com</p>
      <p>نرحب بملاحظاتك واقتراحاتك حول المواضيع التي تهمك.</p>
    </div>
  </div>
  <div class="f-bottom">
    <span>© 2026 دليلك — جميع الحقوق محفوظة.</span>
    <span>صُنع بحب ❤️ للمحتوى العربي المفيد</span>
  </div>
</div></footer>'''

BEHAVIOR = '''<script>
(function(){
var idx=null, base='';
if(location.pathname.indexOf('/posts/')>=0||location.pathname.indexOf('/category/')>=0)base='../';
fetch(base+'search-index.json').then(function(r){return r.json()}).then(function(d){idx=d}).catch(function(){idx=[]});
var theme=localStorage.getItem('theme');
if(theme==='dark')document.documentElement.setAttribute('data-theme','dark');
document.getElementById('themeBtn').addEventListener('click',function(){var d=document.documentElement;if(d.getAttribute('data-theme')==='dark'){d.removeAttribute('data-theme');localStorage.setItem('theme','light')}else{d.setAttribute('data-theme','dark');localStorage.setItem('theme','dark')}});
var sb=document.getElementById('searchInput'),res=document.getElementById('searchRes');
sb.addEventListener('input',function(){var q=sb.value.trim().toLowerCase();res.innerHTML='';if(q.length<2){res.classList.remove('open');return}if(!idx||!idx.length){res.innerHTML='<a>جارٍ التحميل…</a>';res.classList.add('open');return}var hits=idx.filter(function(x){return (x.t&&x.t.toLowerCase().indexOf(q)>-1)||(x.c&&x.c.toLowerCase().indexOf(q)>-1)}).slice(0,7);if(!hits.length){res.innerHTML='<a>لا توجد نتائج مطابقة</a>';res.classList.add('open');return}hits.forEach(function(x){var e=document.createElement('a');e.href=base+'posts/'+x.s+'.html';e.innerHTML='<span class="sr-cat">'+x.c+'</span>'+x.t;res.appendChild(e)});res.classList.add('open')});
document.addEventListener('click',function(e){if(!e.target.closest('.search-box'))res.classList.remove('open')});
document.getElementById('burger').addEventListener('click',function(){document.getElementById('nav').classList.toggle('open')});
window.copyLink=function(){var u=location.href;navigator.clipboard.writeText(u).then(function(){var t=document.getElementById('toast');t.classList.add('show');setTimeout(function(){t.classList.remove('show')},2200)})};
})();
</script>'''

CHROME = '<div id="progress"></div>\n<button id="toTop" title="العودة للأعلى">↑</button>\n<div id="toast">✅ تم نسخ الرابط</div>'

def page_shell(title, desc, body, slug):
    canon = "https://sbdh1285.github.io/dalilak/" + slug
    return f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | دليلك</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="https://sbdh1285.github.io/dalilak/images/og-default.png">
<meta property="og:site_name" content="دليلك">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://sbdh1285.github.io/dalilak/images/og-default.png">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#0f766e">
<link rel="preload" href="fonts/tajawal-700.woff2" as="font" type="font/woff2" crossorigin>
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<link rel="manifest" href="manifest.json">
<style>{css}</style>
</head>
<body>
{CHROME}
{HEADER}
<main>
<div class="page">
{body}
</div>
</main>
{FOOTER}
{BEHAVIOR}
</body>
</html>'''

# 3) بناء فهرس البحث من كل المقالات (إصلاح نقص المقالات المفقودة)
idx = []
for fn in sorted(os.listdir(os.path.join(ROOT, "posts"))):
    if not fn.endswith(".html"):
        continue
    t = read(os.path.join("posts", fn))
    m = re.search(r"<title>(.*?)</title>", t, re.S)
    title = m.group(1).replace(" | دليلك", "").strip() if m else fn[:-5]
    cm = re.search(r'category/([a-z0-9-]+)\.html">([^<]+)<', t)
    cat = cm.group(2) if cm else ""
    idx.append({"t": title, "s": fn[:-5], "c": cat})
json.dump(idx, open(os.path.join(ROOT, "search-index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("search-index.json entries:", len(idx))

# 4) تطبيق التعديلات على كل صفحات HTML الموجودة
html_files = []
for dp, _, fns in os.walk(ROOT):
    if any(s in dp for s in ["/content", "/.git"]):
        continue
    for fn in fns:
        if fn.endswith(".html"):
            html_files.append(os.path.join(dp, fn))
edited = 0
for p in html_files:
    t = read(p)
    orig = t
    # استبدال سكربت السلوك بالكامل (يزيل idx المضمّن ويصلح روابط النتائج)
    t = re.sub(r"<script>(.*?)</script>", BEHAVIOR, t, count=1, flags=re.S)
    # إضافة روابط إخلاء المسؤولية وخريطة الموقع للفوتر (مرة واحدة، مع مراعاة المسار النسبي)
    if "disclaimer.html" not in t:
        rel = "../" if os.path.basename(os.path.dirname(p)) in ("posts", "category") else ""
        t = t.replace(
            f'<a href="{rel}terms.html">شروط الاستخدام</a>',
            f'<a href="{rel}terms.html">شروط الاستخدام</a>\n      <a href="{rel}disclaimer.html">إخلاء المسؤولية</a>\n      <a href="{rel}sitemap.html">خريطة الموقع</a>'
        )
    # مخطط WebSite+SearchAction على الرئيسية
    if os.path.basename(p) == "index.html" and "SearchAction" not in t:
        ld = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"WebSite","name":"دليلك",'
              '"url":"https://sbdh1285.github.io/dalilak/","potentialAction":{"@type":"SearchAction",'
              '"target":"https://sbdh1285.github.io/dalilak/search.html?q={search_term_string}",'
              '"query-input":"required name=search_term_string"}}</script>')
        t = t.replace("</head>", ld + "\n</head>")
    if t != orig:
        write(p, t)
        edited += 1
print("ملفات مُعدّلة:", edited)

# 5) صفحات جديدة
disclaimer_body = '''<h1>إخلاء المسؤولية</h1>
<p class="sub">حدود ما يقدمه موقع دليلك</p>
<p>محتوى دليلك مقدم لأغراض تثقيفية وإرشادية عامة. نحرص على الدقة، لكن المعلومات قد تتغير بمرور الوقت.</p>
<h2>لا نصيحة متخصصة</h2>
<p>المقالات لا تُعدّ بديلاً عن استشارة المختصين في المسائل الصحية أو القانونية أو المالية. عند اتخاذ قرار مهم، راجع مصدراً موثوقاً.</p>
<h2>دقة المحتوى</h2>
<p>نسعى للدقة، لكن لا نضمن خلو المحتوى من أخطاء. تحقّق من المصادر الرسمية قبل الاعتماد على أي معلومة.</p>
<h2>الإعلانات وقبول البرامج</h2>
<p>الموقع قد يعرض إعلانات (مثل Google AdSense). قبول أي موقع في برامج الإعلانات يخضع لمراجعة المزوّد وسياساته، ولا يمكن ضمانه مسبقاً. لا تقدّم مقالاتنا وعوداً بالربح أو النتائج المضمونة.</p>
<h2>المسؤولية</h2>
<p>استخدام الموقع على مسؤوليتك الخاصة. نحن غير مسؤولين عن أي ضرر ناتج عن الاعتماد على المحتوى دون تحقّق مستقل.</p>'''

sitemap_body = '''<h1>خريطة الموقع</h1>
<p class="sub">دليل سريع لكل أقسام وصفحات دليلك</p>
<h2>الأقسام</h2>
<ul>
<li><a href="category/home-tips.html">نصائح منزلية</a></li>
<li><a href="category/recipes.html">وصفات لذيذة</a></li>
<li><a href="category/knowledge.html">معلومات عامة</a></li>
<li><a href="category/tech.html">تكنولوجيا</a></li>
</ul>
<h2>الصفحات الأساسية</h2>
<ul>
<li><a href="index.html">الرئيسية</a></li>
<li><a href="about.html">من نحن</a></li>
<li><a href="contact.html">اتصل بنا</a></li>
<li><a href="privacy-policy.html">سياسة الخصوصية</a></li>
<li><a href="terms.html">شروط الاستخدام</a></li>
<li><a href="disclaimer.html">إخلاء المسؤولية</a></li>
<li><a href="search.html">بحث في الموقع</a></li>
</ul>
<h2>المقالات</h2>
<p>جميع المقالات متاحة من صفحات الأقسام، أو عبر مربع البحث في الأعلى. أحدث المقالات تجدها في <a href="index.html">الرئيسية</a>.</p>'''

search_body = '''<h1>بحث في دليلك</h1>
<p class="sub">ابحث في كل مقالات الموقع</p>
<div class="search-box" style="position:static;max-width:560px;margin:14px 0 22px">
  <input id="pageSearch" class="search-input" style="width:100%;padding:12px 14px;border:1px solid var(--bd);border-radius:12px;font-family:inherit;font-size:1rem" placeholder="اكتب كلمة للبحث…">
</div>
<div id="pageResults" class="grid"></div>
<script>
(function(){
var box=document.getElementById('pageSearch'),out=document.getElementById('pageResults'),idx=null;
var base=(location.pathname.indexOf('/posts/')>=0||location.pathname.indexOf('/category/')>=0)?'../':'';
fetch(base+'search-index.json').then(function(r){return r.json()}).then(function(d){idx=d;var q=new URLSearchParams(location.search).get('q');if(q){box.value=q;run(q.toLowerCase())}}).catch(function(){});
function run(q){out.innerHTML='';if(!idx||!q||q.length<2){out.innerHTML='<p style="color:var(--mut)">اكتب كلمة من حرفين على الأقل.</p>';return;}
var h=idx.filter(function(x){return (x.t&&x.t.toLowerCase().indexOf(q)>-1)||(x.c&&x.c.toLowerCase().indexOf(q)>-1)});
if(!h.length){out.innerHTML='<p style="color:var(--mut)">لا توجد نتائج مطابقة.</p>';return;}
h.forEach(function(x){var a=document.createElement('a');a.className='card';a.href=base+'posts/'+x.s+'.html';a.innerHTML='<div class="card-body"><span class="cat-chip">'+x.c+'</span><h3>'+x.t+'</h3></div>';out.appendChild(a)});}
box.addEventListener('input',function(){run(box.value.trim().toLowerCase())});
})();
</script>'''

write("disclaimer.html", page_shell("إخلاء المسؤولية", "إخلاء مسؤولية دليلك: المحتوى للأغراض العامة ولا يشكل نصيحة متخصصة.", disclaimer_body, "disclaimer.html"))
write("sitemap.html", page_shell("خريطة الموقع", "دليل صفحات وأقسام موقع دليلك.", sitemap_body, "sitemap.html"))
write("search.html", page_shell("بحث", "ابحث في كل مقالات موقع دليلك.", search_body, "search.html"))
print("تم إنشاء: disclaimer.html, sitemap.html, search.html")
print("DONE")
