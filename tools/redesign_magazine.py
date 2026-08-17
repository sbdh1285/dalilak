#!/usr/bin/env python3
"""تطبيق قالب «مجلة عربية عصرية» على ملفات دليلك الثابتة."""
from __future__ import annotations
import html
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "site-config.json").read_text(encoding="utf-8"))
BASE = CONFIG["baseUrl"].rstrip("/")
MONTHS = {1:"يناير",2:"فبراير",3:"مارس",4:"أبريل",5:"مايو",6:"يونيو",7:"يوليو",8:"أغسطس",9:"سبتمبر",10:"أكتوبر",11:"نوفمبر",12:"ديسمبر"}
CAT_PATHS = {"نصائح منزلية":"home-tips","وصفات لذيذة":"recipes","معلومات عامة":"knowledge","تكنولوجيا":"tech"}
CAT_DESCRIPTIONS = {item["name"]:item["description"] for item in CONFIG["categories"]}
ARTICLE_IMAGES_PATH=ROOT/'images'/'article-images.json'
ARTICLE_IMAGES=json.loads(ARTICLE_IMAGES_PATH.read_text(encoding='utf-8')) if ARTICLE_IMAGES_PATH.exists() else {}
COVER_ALTS_PATH=ROOT/'images'/'covers'/'cover-alts.json'
COVER_ALTS=json.loads(COVER_ALTS_PATH.read_text(encoding='utf-8')) if COVER_ALTS_PATH.exists() else {}
COVERS = {
    "lemon-mint-drink":("images/new-lemon-mint-drink.jpg","كأس عصير ليمون ونعناع مثلج على طاولة مضاءة طبيعيًا"),
    "fruit-salad-recipe":("images/new-lemon-mint-drink.jpg","ليمون ونعناع طازجان بتنسيق صيفي منعش"),
    "samosa-cheese-dough":("images/new-samosa-cheese-dough.jpg","سمبوسك جبن ذهبي مقرمش مقدم على طبق خزفي"),
    "zaatar-manakeesh":("images/new-samosa-cheese-dough.jpg","مخبوزات ذهبية مرتبة للتقديم بأسلوب عربي أنيق"),
    "chicken-kabsa":("images/new-samosa-cheese-dough.jpg","طعام عربي ذهبي مقدم في إضاءة طبيعية دافئة"),
    "lentil-soup-recipe":("images/new-samosa-cheese-dough.jpg","طبق عربي دافئ بتنسيق تحريري هادئ"),
    "qishta-basbousa":("images/new-qishta-basbousa.jpg","قطع بسبوسة بالقشطة واللوز على طبق أنيق"),
    "orange-cake-no-oven":("images/new-qishta-basbousa.jpg","حلوى عربية ذهبية مزينة باللوز في ضوء دافئ"),
    "laundry-guide-tips":("images/new-laundry-guide-tips.jpg","ملابس قطنية مطوية بعناية بجوار سلة غسيل"),
    "tidy-home-in-15-minutes":("images/new-quick-kitchen-cleaning.jpg","مساحة منزلية نظيفة ومنظمة بأدوات بسيطة"),
    "natural-cleaning-recipes":("images/new-quick-kitchen-cleaning.jpg","أدوات تنظيف منزلية طبيعية على سطح مطبخ مرتب"),
    "quick-kitchen-cleaning":("images/new-quick-kitchen-cleaning.jpg","مطبخ نظيف مع قطعة قماش وفرشاة وأدوات ترتيب"),
    "eliminate-bad-smells":("images/new-quick-kitchen-cleaning.jpg","سطح منزلي نظيف وأدوات عناية مرتبة"),
    "organize-fridge-waste":("images/new-quick-kitchen-cleaning.jpg","مطبخ منظم ونظيف في إضاءة طبيعية"),
    "natural-insect-repellents":("images/new-natural-insect-repellents.jpg","نباتات ريحان ونعناع على نافذة منزلية مضيئة"),
    "save-electricity-bill":("images/hero-editorial.jpg","مكتب منزلي مضاء طبيعيًا يعكس الاستخدام الهادئ للطاقة"),
    "speed-up-slow-computer":("images/new-speed-up-slow-computer.jpg","حاسوب مكتبي مرتب في مساحة عمل عصرية"),
    "ai-explained-simply":("images/new-speed-up-slow-computer.jpg","حاسوب حديث في مكتب تقني منظم"),
    "protect-online-accounts":("images/new-speed-up-slow-computer.jpg","مساحة عمل رقمية منظمة ترمز إلى الأمان التقني"),
    "safe-online-payments":("images/new-save-mobile-data.jpg","هاتف ذكي وجهاز اتصال على مكتب أنيق"),
    "save-mobile-data":("images/new-save-mobile-data.jpg","هاتف ذكي بجوار جهاز اتصال في بيئة مرتبة"),
    "essential-android-apps":("images/new-save-mobile-data.jpg","هاتف ذكي حديث على مكتب بإضاءة طبيعية"),
    "choose-smartphone-budget":("images/new-save-mobile-data.jpg","هاتف ذكي حديث مع أدوات يومية بسيطة"),
    "amazing-water-facts":("images/new-lemon-mint-drink.jpg","ماء وليمون ونعناع في مشهد طبيعي منعش"),
    "coffee-story-yemen":("images/hero-editorial.jpg","كتب وفنجان على مكتب يعكس أجواء القراءة والثقافة"),
    "age-of-earth":("images/hero-editorial.jpg","كتب ودفتر وبوصلة على مكتب للبحث والمعرفة"),
    "galaxies-and-stars":("images/hero-editorial.jpg","دفتر وبوصلة وكتب في مشهد معرفي هادئ"),
    "amazing-animal-facts":("images/new-natural-insect-repellents.jpg","نباتات خضراء في بيئة طبيعية مضيئة"),
    "amazing-human-body-facts":("images/hero-editorial.jpg","كتب ونظارة ودفتر مفتوح للدراسة والمعرفة"),
    "why-we-need-sleep":("images/hero-editorial.jpg","كتب وفنجان في مساحة منزلية هادئة ومريحة")
}

ICONS = {
"home-tips":'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 10.5 12 4l8 6.5v8a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 18.5zM9 20v-6h6v6" fill="none" stroke="currentColor" stroke-width="1.7"/></svg>',
"recipes":'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3v7m-3-7v5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2V3M7 10v11m10-18v18m0-18c-3 2-4 5-4 8h4" fill="none" stroke="currentColor" stroke-width="1.7"/></svg>',
"knowledge":'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H11v16H6.5A2.5 2.5 0 0 0 4 21.5zm16 0A2.5 2.5 0 0 0 17.5 3H13v16h4.5a2.5 2.5 0 0 1 2.5 2.5z" fill="none" stroke="currentColor" stroke-width="1.7"/></svg>',
"tech":'<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="2.5" width="14" height="19" rx="2" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M9.5 5h5M10 18.5h4" stroke="currentColor" stroke-width="1.7"/></svg>'}
BOOK_ICON='<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M5 7.5c4.2-1 7.8-.2 11 2.3v16c-3.2-2.5-6.8-3.3-11-2.3zm22 0c-4.2-1-7.8-.2-11 2.3v16c3.2-2.5 6.8-3.3 11-2.3z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M16 9.8v16" stroke="currentColor" stroke-width="2"/></svg>'
MENU_ICON='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'


def read(path:Path)->str:return path.read_text(encoding="utf-8")
def write(path:Path,text:str)->None:path.write_text(text,encoding="utf-8")
def prefix_for(path:Path)->str:return "../" if path.parent != ROOT else ""

def fmt_date(value:str)->str:
    try:
        year,month,day=map(int,value[:10].split("-"));return f"{day} {MONTHS[month]} {year}"
    except Exception:return value

def article_records()->dict[str,dict]:
    records={}
    for path in sorted((ROOT/"posts").glob("*.html")):
        text=read(path); data=None
        for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S):
            obj=json.loads(raw)
            if obj.get("@type")=="Article":data=obj;break
        if not data:continue
        desc_match=re.search(r'<meta name="description" content="([^"]+)">',text)
        body_start=text.find('<div class="art-body">')
        body_ends=[x for x in (text.find('<!-- CLUSTER-LINKS-START -->',body_start),text.find('<section class="cluster-links"',body_start),text.find('<section class="sources"',body_start),text.find('<div class="share">',body_start)) if x>body_start]
        body_end=min(body_ends) if body_ends else len(text)
        word_count=len(re.sub(r'<[^>]+>',' ',text[body_start:body_end]).split())
        reading_minutes=max(2,math.ceil(word_count/180))
        custom_cover=ROOT/'images'/'covers'/f'{path.stem}.jpg'
        fallback=COVERS.get(path.stem,(f"images/og-{path.stem}.png",data["headline"]))
        configured=ARTICLE_IMAGES.get(path.stem)
        if configured:
            cover_path=configured['path'];cover_alt=configured['alt']
        else:
            cover_path=f'images/covers/{path.stem}.jpg' if custom_cover.exists() else fallback[0]
            cover_alt=COVER_ALTS.get(path.stem,fallback[1])
        records[path.stem]={
            "slug":path.stem,"title":data["headline"],"category":data["articleSection"],
            "description":html.unescape(desc_match.group(1)) if desc_match else "",
            "published":data["datePublished"],"modified":data.get("dateModified",data["datePublished"]),
            "minutes":reading_minutes,
            "image":cover_path,"imageAlt":cover_alt
        }
    return records


def logo(prefix:str="")->str:
    return f'<a class="logo" href="{prefix}index.html" aria-label="دليلك — الصفحة الرئيسية"><span class="logo-ic">{BOOK_ICON}</span><span class="logo-copy"><strong>دليلك</strong><small>مجلة عربية للمعرفة والحياة</small></span></a>'

def active_for(path:Path)->str:
    rel=path.relative_to(ROOT).as_posix()
    if rel=="index.html":return "home"
    if rel.startswith("category/"):return Path(rel).stem
    if rel=="about.html":return "about"
    if rel=="contact.html":return "contact"
    return ""

def header(path:Path)->str:
    p=prefix_for(path); active=active_for(path)
    links=[("home",f"{p}index.html","الرئيسية"),("home-tips",f"{p}category/home-tips.html","نصائح منزلية"),("recipes",f"{p}category/recipes.html","وصفات لذيذة"),("knowledge",f"{p}category/knowledge.html","معلومات عامة"),("tech",f"{p}category/tech.html","تكنولوجيا"),("about",f"{p}about.html","من نحن"),("contact",f"{p}contact.html","اتصل بنا")]
    nav="".join(f'<a href="{url}"'+(' class="on" aria-current="page"' if key==active else '')+f'>{label}</a>' for key,url,label in links)
    return f'''<div class="topline"><div class="wrap"><span>{CONFIG['shortDescription']}</span><a href="{p}editorial-policy.html">كيف نكتب ونراجع المحتوى؟</a></div></div>
<header class="site-header"><div class="wrap hbar">
{logo(p)}
<nav id="nav" aria-label="التنقل الرئيسي"><div class="mobile-nav-head"><span><strong>قائمة دليلك</strong><small>اختر القسم الذي تريد تصفحه</small></span><button id="navClose" type="button" aria-label="إغلاق القائمة">×</button></div>{nav}</nav>
<div class="h-actions"><div class="search-box"><input class="icon-btn" id="searchInput" type="search" aria-label="البحث في مقالات دليلك" autocomplete="off" placeholder="ابحث في دليلك"><div class="search-res" id="searchRes" role="status" aria-live="polite"></div></div><button class="icon-btn" id="themeBtn" type="button" aria-label="تفعيل الوضع الليلي" aria-pressed="false">◐</button><button class="icon-btn burger" id="burger" type="button" aria-label="فتح القائمة" aria-controls="nav" aria-expanded="false">{MENU_ICON}<span>القائمة</span></button></div>
</div></header><button class="nav-scrim" id="navScrim" type="button" aria-label="إغلاق القائمة" hidden></button>'''

def footer(path:Path)->str:
    p=prefix_for(path)
    contact=CONFIG.get('contact',{});contact_ready=bool(contact.get('enabled') and CONFIG.get('email'))
    contact_html=f'<a href="mailto:{CONFIG["email"]}">{CONFIG["email"]}</a>' if contact_ready else '<span class="footer-contact-pending">البريد الرسمي قيد التجهيز</span>'
    return f'''<footer><div class="wrap"><div class="fgrid">
<div class="footer-brand">{logo(p)}<p>{CONFIG['description']}</p></div>
<div><h4>الأقسام</h4><a href="{p}category/home-tips.html">نصائح منزلية</a><a href="{p}category/recipes.html">وصفات لذيذة</a><a href="{p}category/knowledge.html">معلومات عامة</a><a href="{p}category/tech.html">تكنولوجيا</a></div>
<div><h4>عن دليلك</h4><a href="{p}about.html">من نحن</a><a href="{p}guide-safe-cleaning.html">أدلة دليلك</a><a href="{p}authors/editorial-team.html">فريق التحرير</a><a href="{p}editorial-policy.html">سياسة التحرير</a><a href="{p}contact.html">اتصل بنا</a><a href="{p}sitemap.html">خريطة الموقع</a></div>
<div><h4>السياسات والتواصل</h4><a href="{p}privacy-policy.html">سياسة الخصوصية</a><a href="{p}terms.html">شروط الاستخدام</a><a href="{p}disclaimer.html">إخلاء المسؤولية</a>{contact_html}</div>
</div><div class="f-bottom"><span>© 2026 دليلك — جميع الحقوق محفوظة.</span><span>محتوى عربي يُكتب ويُراجع بعناية</span></div></div></footer>'''

def inject_shell(path:Path,text:str)->str:
    text=re.sub(r'<div class="topline">.*?</div></div>\s*','',text,count=1,flags=re.S)
    text=re.sub(r'<header.*?</header>(?:<button class="nav-scrim".*?</button>)?',header(path),text,count=1,flags=re.S)
    text=re.sub(r'<footer>.*?</footer>',footer(path),text,count=1,flags=re.S)
    text=text.replace('css/style.css?v=6','css/style.css?v=8').replace('css/style.css?v=7','css/style.css?v=8')
    text=text.replace('<meta name="theme-color" content="#0f766e">','<meta name="theme-color" content="#124e4a">')
    p=prefix_for(path)
    preload=f'<link rel="preload" href="{p}fonts/ibm-plex-arabic-700.ttf" as="font" type="font/ttf" crossorigin>'
    if 'ibm-plex-arabic-700.ttf' not in text:text=text.replace('</head>',preload+'\n</head>')
    if '<meta property="og:title"' not in text:
        title_match=re.search(r'<title>(.*?)</title>',text,re.S);desc_match=re.search(r'<meta name="description" content="([^"]+)"',text);canonical_match=re.search(r'<link rel="canonical" href="([^"]+)"',text)
        if title_match and desc_match and canonical_match:
            social_title=re.sub(r'\s*\|\s*دليلك\s*$','',title_match.group(1));desc=desc_match.group(1);url=canonical_match.group(1);image=f'{BASE}/images/og-default.png'
            tags=f'<meta property="og:type" content="website"><meta property="og:title" content="{html.escape(social_title,quote=True)}"><meta property="og:description" content="{html.escape(desc,quote=True)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{image}"><meta property="og:site_name" content="دليلك"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{html.escape(social_title,quote=True)}"><meta name="twitter:description" content="{html.escape(desc,quote=True)}"><meta name="twitter:image" content="{image}">'
            text=text.replace('</head>',tags+'\n</head>')
    return text

def article_card(a:dict,prefix:str="",lead:bool=False)->str:
    cls="card lead-card" if lead else "card"
    return f'''<article class="{cls}"><a href="{prefix}posts/{a['slug']}.html"><img class="card-img" src="{prefix}{a['image']}" alt="{html.escape(a['imageAlt'])}" loading="{'eager' if lead else 'lazy'}" decoding="async" width="1200" height="630"></a><div class="card-body"><span class="cat-chip">{a['category']}</span><h3><a href="{prefix}posts/{a['slug']}.html">{a['title']}</a></h3><p>{a['description']}</p><div class="card-meta"><time datetime="{a['published']}">{fmt_date(a['published'])}</time><span>{a['minutes']} دقائق قراءة</span></div></div></article>'''

def story_row(a:dict,prefix:str="")->str:
    return f'''<a class="story-row" href="{prefix}posts/{a['slug']}.html"><img src="{prefix}{a['image']}" alt="" loading="lazy" decoding="async" width="240" height="126"><div><span class="cat-chip">{a['category']}</span><h3>{a['title']}</h3><span class="story-meta">{fmt_date(a['published'])} · {a['minutes']} دقائق</span></div></a>'''

def more_story(a:dict,prefix:str="")->str:
    return f'''<a class="more-story" href="{prefix}posts/{a['slug']}.html"><img src="{prefix}{a['image']}" alt="" loading="lazy" decoding="async" width="320" height="168"><div><span class="cat-chip">{a['category']}</span><h3>{a['title']}</h3><p>{a['description']}</p></div></a>'''

def home_main(records:dict[str,dict],old:str)->str:
    ordered=sorted(records.values(),key=lambda x:x['published'],reverse=True)
    feat=records[CONFIG['featuredArticle']]; latest=[x for x in ordered if x['slug']!=feat['slug']]
    cats="".join(f'''<a class="cat-card" href="category/{c['slug']}.html"><div class="cat-ic">{ICONS[c['slug']]}</div><h3>{c['name']}</h3><p>{c['description']}</p><span class="cnt">استكشف القسم ←</span></a>''' for c in CONFIG['categories'])
    latest_html=article_card(latest[0],lead=True)+f'<div class="story-stack">{"".join(story_row(x) for x in latest[1:5])}</div>'
    more="".join(more_story(x) for x in latest[5:11])
    organization={"@context":"https://schema.org","@type":"Organization","name":CONFIG['siteName'],"url":BASE,"description":CONFIG['description']}
    if CONFIG.get('contact',{}).get('enabled') and CONFIG.get('email'):organization['email']=CONFIG['email']
    faq_items=[
        ("ما هو موقع دليلك؟","مجلة عربية تقدم محتوى عمليًا في النصائح المنزلية والوصفات والمعرفة والتكنولوجيا بلغة واضحة وتصميم مريح."),
        ("هل المحتوى مجاني؟","نعم، جميع المقالات متاحة للقراءة دون تسجيل أو اشتراك."),
        ("كيف يُراجع المحتوى؟","نراجع وضوح المقال ومصادر الادعاءات القابلة للتحقق، ونحدّث المحتوى عند اكتشاف خطأ أو تغير المعلومة."),
        ("هل يمكن اقتراح موضوع أو إرسال تصحيح؟","نعم، نستقبل الاقتراحات والتصحيحات الموثقة عبر صفحة اتصل بنا.")]
    faq={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq_items]}
    jsonlds='\n'.join('<script type="application/ld+json">'+json.dumps(x,ensure_ascii=False,separators=(',',':'))+'</script>' for x in (organization,faq))
    return f'''<main id="main-content">
<section class="home-hero"><div class="wrap"><div class="hero-grid"><div class="hero-copy"><span class="eyebrow">مجلة عربية عصرية</span><h1>{CONFIG['tagline']}</h1><p>{CONFIG['description']}</p><div class="cta-row"><a class="btn btn-a" href="category/home-tips.html">ابدأ القراءة</a><a class="btn btn-b" href="about.html">تعرّف على دليلك</a></div></div><div class="hero-media"><img src="{CONFIG['heroImage']}" alt="مكتب هادئ يضم كتبًا ودفترًا وأدوات ترمز إلى المعرفة والحياة اليومية" width="1440" height="900" fetchpriority="high" decoding="async"></div></div><div class="value-strip"><div class="value-item"><strong>محتوى واضح</strong><span>لغة مباشرة دون تعقيد</span></div><div class="value-item"><strong>أقسام متنوعة</strong><span>المنزل والطعام والمعرفة والتقنية</span></div><div class="value-item"><strong>قراءة مريحة</strong><span>تصميم عربي يركز على المحتوى</span></div><div class="value-item"><strong>تحديثات مستمرة</strong><span>مراجعة وتصحيح عند الحاجة</span></div></div></div></section>
<section class="sec"><div class="wrap"><div class="sec-h"><div class="sec-title"><span class="section-kicker">اختيار التحرير</span><h2>مقال مميز</h2></div></div><a class="featured" href="posts/{feat['slug']}.html"><img src="{feat['image']}" alt="{html.escape(feat['imageAlt'])}" width="1200" height="630" decoding="async"><div class="f-body"><span class="f-tag">{feat['category']}</span><h2>{feat['title']}</h2><p>{feat['description']}</p><span class="read-link">اقرأ المقال ←</span></div></a></div></section>
<section class="sec"><div class="wrap"><div class="sec-h"><div class="sec-title"><span class="section-kicker">تصفّح حسب اهتمامك</span><h2>أقسام دليلك</h2></div></div><div class="cats">{cats}</div></div></section>
<section class="sec"><div class="wrap"><div class="sec-h"><div class="sec-title"><span class="section-kicker">نُشر حديثًا</span><h2>أحدث المقالات</h2></div><a href="sitemap.html">جميع المقالات ←</a></div><div class="magazine-latest">{latest_html}</div></div></section>
<section class="sec"><div class="wrap"><div class="sec-h"><div class="sec-title"><span class="section-kicker">مختارات إضافية</span><h2>للقراءة بعد ذلك</h2></div></div><div class="more-grid">{more}</div></div></section>
<section class="sec"><div class="wrap"><div class="sec-h"><div class="sec-title"><span class="section-kicker">مسارات عملية</span><h2>أدلة دليلك</h2></div><a href="sitemap.html">كل الأدلة والمقالات ←</a></div><div class="guide-feature-grid"><a href="guide-safe-cleaning.html"><span>01</span><h3>دليل التنظيف الآمن</h3><p>المنتجات والتهوية ومنع الخلطات الخطرة.</p></a><a href="guide-account-security.html"><span>02</span><h3>دليل حماية الحسابات</h3><p>المنع والاسترداد والدفع الآمن.</p></a><a href="guide-gulf-recipes.html"><span>03</span><h3>دليل الوصفات الخليجية</h3><p>الأرز والبهارات والمقبلات والمشروبات.</p></a><a href="guide-smartphone.html"><span>04</span><h3>دليل الهاتف</h3><p>الاختيار والفحص والحماية والاستخدام.</p></a></div></div></section>
<section class="sec"><div class="wrap"><div class="sec-h"><div class="sec-title"><span class="section-kicker">عن الموقع</span><h2>أسئلة شائعة</h2></div></div><div class="faq"><details open><summary>ما هو موقع دليلك؟</summary><p>مجلة عربية تقدم محتوى عمليًا في النصائح المنزلية والوصفات والمعرفة والتكنولوجيا بلغة واضحة وتصميم مريح.</p></details><details><summary>هل المحتوى مجاني؟</summary><p>نعم، جميع المقالات متاحة للقراءة دون تسجيل أو اشتراك.</p></details><details><summary>كيف يُراجع المحتوى؟</summary><p>نراجع وضوح المقال ومصادر الادعاءات القابلة للتحقق، ونحدّث المحتوى عند اكتشاف خطأ أو تغير المعلومة.</p></details><details><summary>هل يمكن اقتراح موضوع أو إرسال تصحيح؟</summary><p>نعم، نستقبل الاقتراحات والتصحيحات الموثقة عبر صفحة اتصل بنا.</p></details></div></div></section>
<section class="sec"><div class="wrap"><div class="trust-panel"><div><h2>الثقة تبدأ بالوضوح</h2><p>تعرّف على طريقة اختيار الموضوعات ومراجعة المعلومات والتعامل مع التصحيحات في سياسة التحرير.</p></div><a class="btn" href="editorial-policy.html">اقرأ سياسة التحرير</a></div></div></section>
{jsonlds}</main>'''

def redesign_home(path:Path,records:dict[str,dict])->None:
    text=read(path); newmain=home_main(records,text)
    text=re.sub(r'<main id="main-content">.*?</main>',newmain,text,count=1,flags=re.S)
    text=inject_shell(path,text)
    text=text.replace('<meta property="og:title" content="دليلك | دليلك اليومي لنصائح عملية، وصفات شهية، ومعلومات مفيدة">','<meta property="og:title" content="دليلك | أفكار مفيدة لحياة يومية أسهل">').replace('<meta name="twitter:title" content="دليلك | دليلك اليومي لنصائح عملية، وصفات شهية، ومعلومات مفيدة">','<meta name="twitter:title" content="دليلك | أفكار مفيدة لحياة يومية أسهل">')
    text=re.sub(r'<meta name="description" content="[^"]+">',f'<meta name="description" content="{CONFIG["description"]}">',text,count=1)
    text=re.sub(r'<meta property="og:description" content="[^"]+">',f'<meta property="og:description" content="{CONFIG["description"]}">',text,count=1)
    text=re.sub(r'<meta name="twitter:description" content="[^"]+">',f'<meta name="twitter:description" content="{CONFIG["description"]}">',text,count=1)
    def fix_webpage(match:re.Match)->str:
        try: data=json.loads(match.group(1))
        except json.JSONDecodeError:return match.group(0)
        if data.get('@type')=='WebPage': data.update({'name':'دليلك | أفكار مفيدة لحياة يومية أسهل','description':CONFIG['description']})
        return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False,separators=(',',':'))+'</script>'
    text=re.sub(r'<script type="application/ld\+json">(.*?)</script>',fix_webpage,text,flags=re.S)
    write(path,text)

def normalize_cards(text:str,records:dict[str,dict],prefix:str)->str:
    def repl(match:re.Match)->str:
        block=match.group(0); sm=re.search(r'(?:\.\./)?posts/([^"/]+)\.html',block)
        if not sm or sm.group(1) not in records:return block
        return article_card(records[sm.group(1)],prefix=prefix)
    return re.sub(r'<article class="card">.*?</article>',repl,text,flags=re.S)

def redesign_category(path:Path,records:dict[str,dict])->None:
    text=read(path); slug=path.stem
    names={x["slug"]:x["name"] for x in CONFIG["categories"]}; name=names[slug]; desc=CAT_DESCRIPTIONS[name]
    intro=f'''<div class="wrap category-wrap"><div class="crumb"><a href="../index.html">الرئيسية</a><span>/</span><span>{name}</span></div><div class="category-intro"><div><span class="section-kicker">قسم دليلك</span><h1>{name}</h1><p>{desc}</p></div><span class="category-count">{sum(1 for x in records.values() if x['category']==name)} مقالات متاحة</span></div><div class="grid">'''
    text=re.sub(r'<div class="wrap" style="padding-top:38px">.*?<div class="grid">',intro,text,count=1,flags=re.S)
    article_count=sum(1 for x in records.values() if x['category']==name)
    text=re.sub(r'<span class="category-count">\d+ مقالات متاحة</span>',f'<span class="category-count">{article_count} مقالات متاحة</span>',text,count=1)
    grid_start=text.index('<div class="grid">',text.index('category-wrap'))+len('<div class="grid">')
    collection_start=text.index('<script type="application/ld+json">',grid_start)
    wrap_close=text.rfind('</div>',grid_start,collection_start)
    grid_close=text.rfind('</div>',grid_start,wrap_close)
    category_articles=sorted((a for a in records.values() if a['category']==name),key=lambda a:a['published'],reverse=True)
    text=text[:grid_start]+''.join(article_card(a,prefix='../') for a in category_articles)+text[grid_close:]
    category_covers={'home-tips':'images/new-quick-kitchen-cleaning.jpg','recipes':'images/new-lemon-mint-drink.jpg','knowledge':'images/hero-editorial.jpg','tech':'images/new-speed-up-slow-computer.jpg'}
    cover_url=f'{BASE}/{category_covers[slug]}'
    text=re.sub(r'<meta property="og:image" content="[^"]+">',f'<meta property="og:image" content="{cover_url}">',text,count=1)
    text=re.sub(r'<meta name="twitter:image" content="[^"]+">',f'<meta name="twitter:image" content="{cover_url}">',text,count=1)
    text=inject_shell(path,text)
    write(path,text)

def redesign_post(path:Path,records:dict[str,dict])->None:
    text=read(path); a=records[path.stem]; cat_slug=CAT_PATHS[a['category']]
    text=normalize_cards(text,records,"../")
    text=re.sub(r'<div class="art-meta">.*?</div>',f'''<div class="art-meta"><span>بقلم <a href="../authors/editorial-team.html" rel="author">{CONFIG['authorName']}</a></span><span>نُشر <time datetime="{a['published']}">{fmt_date(a['published'])}</time></span><span>حُدّث <time datetime="{a['modified']}">{fmt_date(a['modified'])}</time></span><span>{a['minutes']} دقائق قراءة</span></div>''',text,count=1,flags=re.S)
    text=re.sub(r'<img class="art-img"[^>]+>',f'<img class="art-img" src="../{a["image"]}" alt="{html.escape(a["imageAlt"])}" width="1200" height="630" fetchpriority="high" decoding="async">',text,count=1)
    cover_url=f'{BASE}/{a["image"]}'
    text=re.sub(r'<meta property="og:image" content="[^"]+">',f'<meta property="og:image" content="{cover_url}">',text,count=1)
    text=re.sub(r'<meta name="twitter:image" content="[^"]+">',f'<meta name="twitter:image" content="{cover_url}">',text,count=1)
    def fix_article_json(match:re.Match)->str:
        try: data=json.loads(match.group(1))
        except json.JSONDecodeError:return match.group(0)
        if data.get('@type')=='Article': data['image']=cover_url
        return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False,separators=(',',':'))+'</script>'
    text=re.sub(r'<script type="application/ld\+json">(.*?)</script>',fix_article_json,text,flags=re.S)
    if 'class="art-category"' not in text:
        text=text.replace('<h1>'+a['title']+'</h1>',f'<a class="art-category" href="../category/{cat_slug}.html">{a["category"]}</a><h1>{a["title"]}</h1><p class="article-summary">{a["description"]}</p>',1)
    text=text.replace('📑 محتويات المقال','محتويات المقال').replace('🔗 نسخ الرابط','نسخ الرابط').replace('<span class="t-ic">💡</span>','<span class="t-ic">مهم</span>').replace('<div class="author-av">✍</div>','<div class="author-av">د</div>')
    text=re.sub(r'<aside class="side"><nav class="toc".*?</nav>','<aside class="side">',text,count=1,flags=re.S)
    toc_match=re.search(r'<nav class="toc".*?</nav>',text,re.S)
    if toc_match:
        side_toc=toc_match.group(0).replace('aria-label="جدول محتويات المقال"','aria-label="فهرس المقال الجانبي"')
        text=text.replace('<aside class="side">','<aside class="side">'+side_toc,1)
    def fix_pop_cover(match:re.Match)->str:
        block=match.group(0); slug_match=re.search(r'href="\.\./posts/([^"/]+)\.html"',block)
        if not slug_match or slug_match.group(1) not in records:return block
        item=records[slug_match.group(1)]
        return re.sub(r'<img class="pop-thumb"[^>]+>',f'<img class="pop-thumb" src="../{item["image"]}" alt="{html.escape(item["imageAlt"])}" loading="lazy" decoding="async" width="120" height="63">',block,count=1)
    text=re.sub(r'<div class="pop-item">.*?</div></div>',fix_pop_cover,text,flags=re.S)
    text=text.replace('<meta property="og:type" content="website">','<meta property="og:type" content="article">',1)
    text=inject_shell(path,text)
    write(path,text)

def sync_css_config()->None:
    path=ROOT/'css'/'style.css'; text=read(path); theme=CONFIG['theme']
    replacements={'--primary':theme['primary'],'--primary-deep':theme['primaryDark'],'--accent':theme['accent'],'--bg':theme['background'],'--surface':theme['surface'],'--text':theme['text'],'--muted':theme['muted']}
    root_start=text.index(':root{'); root_end=text.index('}',root_start); block=text[root_start:root_end]
    for name,value in replacements.items(): block=re.sub(rf'{re.escape(name)}:[^;]+',f'{name}:{value}',block,count=1)
    text=text[:root_start]+block+text[root_end:]; write(path,text)

def update_favicon()->None:
    write(ROOT/"favicon.svg",'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="8" fill="#124e4a"/><path d="M12 17c8-2 14-.5 20 4v31c-6-4.5-12-6-20-4zm40 0c-8-2-14-.5-20 4v31c6-4.5 12-6 20-4z" fill="none" stroke="#fff" stroke-width="4" stroke-linejoin="round"/><path d="M32 21v31" stroke="#d97732" stroke-width="4"/></svg>''')

def main()->None:
    records=article_records()
    redesign_home(ROOT/"index.html",records)
    for path in (ROOT/"category").glob("*.html"):redesign_category(path,records)
    for path in (ROOT/"posts").glob("*.html"):redesign_post(path,records)
    handled={ROOT/"index.html",*set((ROOT/"category").glob("*.html")),*set((ROOT/"posts").glob("*.html"))}
    for path in ROOT.rglob("*.html"):
        if 'node_modules' in path.parts or path.parts[-2:-1]==('qa',):
            continue
        if path not in handled:
            text=inject_shell(path,read(path)).replace('<div class="author-av">✍</div>','<div class="author-av">د</div>')
            if path.name=='about.html':
                for mark in ('🏠 ','🍽 ','💡 ','📱 '): text=text.replace(mark,'')
            write(path,text)
    sync_css_config()
    update_favicon()
    page_count=sum(1 for p in ROOT.rglob('*.html') if 'node_modules' not in p.parts)
    print(f"تم تطبيق قالب المجلة على {page_count} صفحة و{len(records)} مقالًا.")
if __name__=="__main__":main()
