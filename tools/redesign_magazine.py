#!/usr/bin/env python3
"""تطبيق قالب «مجلة عربية عصرية» على ملفات دليلك الثابتة."""
from __future__ import annotations
import html
import json
import urllib.parse
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

def count_readable_words(fragment:str)->int:
    fragment=re.sub(r'<!--.*?-->',' ',fragment,flags=re.S)
    visible=re.sub(r'<[^>]+>',' ',fragment)
    return len(re.findall(r'[\w\u0600-\u06FF]+',html.unescape(visible),re.UNICODE))

ARABIC_READING_WORDS_PER_MINUTE=143

def calculate_reading_minutes(fragment:str)->int:
    words=count_readable_words(fragment)
    return max(2,math.floor(words/ARABIC_READING_WORDS_PER_MINUTE+0.5))

def reading_time_label(minutes:int)->str:
    if minutes==1:return 'دقيقة واحدة'
    if minutes==2:return 'دقيقتان'
    if 3<=minutes<=10:return f'{minutes} دقائق'
    return f'{minutes} دقيقة'

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
        reading_minutes=calculate_reading_minutes(text[body_start:body_end])
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
    # رابط البحث يظهر داخل القائمة الجانبية للجوال حيث يُخفى صندوق البحث.
    nav+=f'<a class="nav-search-link" href="{p}search.html">بحث في الموقع</a>' 
    return f'''<div class="topline"><div class="wrap"><span>{CONFIG['shortDescription']}</span><a href="{p}editorial-policy.html">كيف نكتب ونراجع المحتوى؟</a></div></div>
<header class="site-header"><div class="wrap hbar">
{logo(p)}
<nav id="nav" aria-label="التنقل الرئيسي"><div class="mobile-nav-head"><span><strong>قائمة دليلك</strong><small>اختر القسم الذي تريد تصفحه</small></span><button id="navClose" type="button" aria-label="إغلاق القائمة">×</button></div>{nav}</nav>
<div class="h-actions"><div class="search-box"><input class="icon-btn" id="searchInput" type="search" aria-label="البحث في مقالات دليلك" autocomplete="off" placeholder="ابحث في دليلك"><div class="search-res" id="searchRes" role="status" aria-live="polite"></div></div><button class="icon-btn" id="themeBtn" type="button" aria-label="تفعيل الوضع الليلي" aria-pressed="false">◐</button><button class="icon-btn burger" id="burger" type="button" aria-label="فتح القائمة" aria-controls="nav" aria-expanded="false">{MENU_ICON}<span>القائمة</span></button></div>
</div></header><button class="nav-scrim" id="navScrim" type="button" aria-label="إغلاق القائمة" hidden></button>'''

def footer(path:Path)->str:
    p=prefix_for(path)
    contact=CONFIG.get('contact',{});contact_ready=bool(contact.get('enabled') and CONFIG.get('email'))
    contact_html=(
        f'<p class="footer-email"><span>البريد الإلكتروني</span><a href="mailto:{CONFIG["email"]}">{CONFIG["email"]}</a></p>'
        if contact_ready else ''
    )
    return f'''<footer><div class="wrap"><h2 class="sr-only">روابط الموقع</h2><div class="fgrid">
<div class="footer-brand">{logo(p)}<p>{CONFIG['description']}</p></div>
<div><h3>الأقسام</h3><a href="{p}category/home-tips.html">نصائح منزلية</a><a href="{p}category/recipes.html">وصفات لذيذة</a><a href="{p}category/knowledge.html">معلومات عامة</a><a href="{p}category/tech.html">تكنولوجيا</a></div>
<div><h3>عن دليلك</h3><a href="{p}about.html">من نحن</a><a href="{p}guide-safe-cleaning.html">أدلة دليلك</a><a href="{p}authors/editorial-team.html">فريق التحرير</a><a href="{p}editorial-policy.html">سياسة التحرير</a><a href="{p}contact.html">اتصل بنا</a><a href="{p}search.html">بحث</a><a href="{p}sitemap.html">خريطة الموقع</a></div>
<div><h3>السياسات والتواصل</h3><a href="{p}privacy-policy.html">سياسة الخصوصية</a><a href="{p}terms.html">شروط الاستخدام</a><a href="{p}disclaimer.html">إخلاء المسؤولية</a>{contact_html}</div>
</div><div class="f-bottom"><span>© 2026 دليلك — جميع الحقوق محفوظة.</span><span>محتوى عربي يُكتب ويُراجع بعناية</span></div></div></footer>'''

def inject_shell(path:Path,text:str)->str:
    text=re.sub(r'<div class="topline">.*?</div></div>\s*','',text,count=1,flags=re.S)
    text=re.sub(r'<header.*?</header>(?:<button class="nav-scrim".*?</button>)?',header(path),text,count=1,flags=re.S)
    text=re.sub(r'<footer>.*?</footer>',footer(path),text,count=1,flags=re.S)
    text=text.replace('js/main.js?v=1','js/main.js?v=2')
    text=text.replace('css/style.css?v=6','css/style.css?v=11').replace('css/style.css?v=7','css/style.css?v=11').replace('css/style.css?v=10','css/style.css?v=11')
    text=text.replace('<meta name="theme-color" content="#0f766e">','<meta name="theme-color" content="#124e4a">')
    p=prefix_for(path)
    preload=f'<link rel="preload" href="{p}fonts/ibm-plex-arabic-700.woff2" as="font" type="font/woff2" crossorigin>'
    if 'ibm-plex-arabic-700.woff2' not in text:text=text.replace('</head>',preload+'\n</head>')
    # اكتشاف RSS من كل صفحة.
    rss=f'<link rel="alternate" type="application/rss+xml" title="دليلك — أحدث المقالات" href="{p}feed.xml">'
    if 'application/rss+xml' not in text:text=text.replace('</head>',rss+'\n</head>')
    # أيقونات التطبيق على iOS واسم الاختصار.
    if 'apple-touch-icon' not in text:
        text=text.replace('</head>',f'<link rel="apple-touch-icon" href="{p}images/icons/icon-192.png">'
                                    f'<meta name="apple-mobile-web-app-title" content="دليلك">\n</head>')
    # أكمل وسوم تويتر إن كانت og موجودة وtwitter ناقصة (حالة صفحات الأدلة).
    if '<meta property="og:title"' in text and 'name="twitter:card"' not in text:
        og_t=re.search(r'<meta property="og:title" content="([^"]*)"',text)
        og_d=re.search(r'<meta property="og:description" content="([^"]*)"',text)
        og_i=re.search(r'<meta property="og:image" content="([^"]*)"',text)
        if og_t and og_d and og_i:
            tw=(f'<meta name="twitter:card" content="summary_large_image">'
                f'<meta name="twitter:title" content="{og_t.group(1)}">'
                f'<meta name="twitter:description" content="{og_d.group(1)}">'
                f'<meta name="twitter:image" content="{og_i.group(1)}">')
            text=text.replace(og_i.group(0),og_i.group(0)+tw,1)
    if '<meta property="og:title"' not in text:
        title_match=re.search(r'<title>(.*?)</title>',text,re.S);desc_match=re.search(r'<meta name="description" content="([^"]+)"',text);canonical_match=re.search(r'<link rel="canonical" href="([^"]+)"',text)
        if title_match and desc_match and canonical_match:
            social_title=re.sub(r'\s*\|\s*دليلك\s*$','',title_match.group(1));desc=desc_match.group(1);url=canonical_match.group(1);image=f'{BASE}/images/og-default.png'
            tags=f'<meta property="og:type" content="website"><meta property="og:title" content="{html.escape(social_title,quote=True)}"><meta property="og:description" content="{html.escape(desc,quote=True)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{image}"><meta property="og:site_name" content="دليلك"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{html.escape(social_title,quote=True)}"><meta name="twitter:description" content="{html.escape(desc,quote=True)}"><meta name="twitter:image" content="{image}">'
            text=text.replace('</head>',tags+'\n</head>')
    return text

def responsive_picture(a:dict,prefix:str,img_class:str,loading:str='lazy',sizes:str='(max-width: 640px) 100vw, 33vw',priority:bool=False,picture_class:str='')->str:
    slug=a['slug'];srcset=', '.join(f'{prefix}images/responsive/articles/{slug}-{w}.webp {w}w' for w in (480,800,1200));attrs=' fetchpriority="high"' if priority else ''
    return f'<picture class="{picture_class}"><source type="image/webp" srcset="{srcset}" sizes="{sizes}"><img class="{img_class}" src="{prefix}{a["image"]}" alt="{html.escape(a["imageAlt"],quote=True)}" loading="{loading}" decoding="async" width="1200" height="630"{attrs}></picture>'

def responsive_picture_bare(a:dict,prefix:str,sizes:str,loading:str='lazy',priority:bool=False,picture_class:str='')->str:
    """صورة تحريرية بلا class على الوسم img — تستخدمها واجهة المجلة (ed-*)."""
    slug=a['slug'];srcset=', '.join(f'{prefix}images/responsive/articles/{slug}-{w}.webp {w}w' for w in (480,800,1200))
    attrs=' fetchpriority="high"' if priority else ''
    return (f'<picture class="{picture_class}"><source type="image/webp" srcset="{srcset}" sizes="{sizes}">'
            f'<img src="{prefix}{a["image"]}" alt="{html.escape(a["imageAlt"],quote=True)}" width="1200" height="630" '
            f'loading="{loading}"{attrs} decoding="async"></picture>')

def article_card(a:dict,prefix:str="",lead:bool=False)->str:
    cls="card lead-card" if lead else "card";picture=responsive_picture(a,prefix,'card-img','eager' if lead else 'lazy','(max-width: 640px) calc(100vw - 28px), (max-width: 900px) 50vw, 33vw',lead,'card-picture')
    return f'''<article class="{cls}"><a href="{prefix}posts/{a['slug']}.html">{picture}</a><div class="card-body"><span class="cat-chip">{a['category']}</span><h3><a href="{prefix}posts/{a['slug']}.html">{a['title']}</a></h3><p>{a['description']}</p><div class="card-meta"><time datetime="{a['published']}">{fmt_date(a['published'])}</time><span>{reading_time_label(a['minutes'])} قراءة</span></div></div></article>'''

def story_row(a:dict,prefix:str="")->str:
    picture=responsive_picture(a,prefix,'story-img','lazy','128px',False,'story-picture')
    return f'''<a class="story-row" href="{prefix}posts/{a['slug']}.html">{picture}<div><span class="cat-chip">{a['category']}</span><h3>{a['title']}</h3><span class="story-meta">{fmt_date(a['published'])} · {reading_time_label(a['minutes'])}</span></div></a>'''

def more_story(a:dict,prefix:str="")->str:
    picture=responsive_picture(a,prefix,'more-img','lazy','(max-width: 640px) 125px, 172px',False,'more-picture')
    return f'''<a class="more-story" href="{prefix}posts/{a['slug']}.html">{picture}<div><span class="cat-chip">{a['category']}</span><h3>{a['title']}</h3><p>{a['description']}</p></div></a>'''

def ed_lead(a:dict)->str:
    picture=responsive_picture_bare(a,'','(max-width:900px) 100vw, 62vw','eager',True,'ed-lead-pic')
    return (f'<a class="ed-lead" href="posts/{a["slug"]}.html">{picture}'
            f'<div class="ed-lead-body"><span class="ed-kicker ed-kicker-accent">{a["category"]}</span>'
            f'<h1 class="ed-lead-title">{a["title"]}</h1>'
            f'<p class="ed-lead-dek">{a["description"]}</p>'
            f'<span class="ed-byline">{CONFIG["authorName"]}<i></i>{fmt_date(a["published"])}<i></i>{reading_time_label(a["minutes"])}</span>'
            f'</div></a>')

def ed_side_item(a:dict,num:int)->str:
    return (f'<a class="ed-side-item" href="posts/{a["slug"]}.html">'
            f'<span class="ed-side-num">{num:02d}</span><div>'
            f'<span class="ed-kicker">{a["category"]}</span><h3>{a["title"]}</h3>'
            f'<span class="ed-byline sm">{fmt_date(a["published"])}<i></i>{reading_time_label(a["minutes"])}</span>'
            f'</div></a>')

def ed_riv(a:dict)->str:
    picture=responsive_picture_bare(a,'','(max-width:640px) 96px, 148px','lazy',False,'ed-riv-pic')
    return (f'<a class="ed-riv" href="posts/{a["slug"]}.html">{picture}'
            f'<div class="ed-riv-body"><span class="ed-kicker">{a["category"]}</span>'
            f'<h3>{a["title"]}</h3><p>{a["description"]}</p>'
            f'<span class="ed-byline sm">{fmt_date(a["published"])}<i></i>{reading_time_label(a["minutes"])}</span>'
            f'</div></a>')

def ed_band(cat:dict,arts:list[dict])->str:
    lead,rest=arts[0],arts[1:4]
    picture=responsive_picture_bare(lead,'','(max-width:900px) 100vw, 46vw','lazy',False,'ed-band-pic')
    lead_html=(f'<a class="ed-band-lead" href="posts/{lead["slug"]}.html">{picture}<div>'
               f'<h3>{lead["title"]}</h3><p>{lead["description"]}</p>'
               f'<span class="ed-byline sm">{fmt_date(lead["published"])}<i></i>{reading_time_label(lead["minutes"])}</span>'
               f'</div></a>')
    items=''.join(f'<a class="ed-band-item" href="posts/{x["slug"]}.html"><h4>{x["title"]}</h4>'
                  f'<span class="ed-byline sm">{fmt_date(x["published"])}<i></i>{reading_time_label(x["minutes"])}</span></a>'
                  for x in rest)
    return (f'<section class="ed-sec ed-band"><div class="wrap">'
            f'<div class="ed-sec-h"><h2 class="ed-sec-t">{cat["name"]}</h2>'
            f'<a class="ed-more" href="category/{cat["slug"]}.html">كل المقالات</a></div>'
            f'<div class="ed-band-grid">{lead_html}<div class="ed-band-list">{items}</div></div>'
            f'</div></section>')

def home_main(records:dict[str,dict],old:str)->str:
    # ترتيب حتمي: الأحدث أولًا، ثم الslug أبجديًا لضمان نتيجة ثابتة عند تساوي التاريخ.
    ordered=sorted(records.values(),key=lambda x:(x['published'],[-ord(c) for c in x['slug']]),reverse=True)
    # المقال الرئيسي: اختيار التحرير إن حُدّد في site-config.json، وإلا الأحدث تلقائيًا.
    lead=records[CONFIG['featuredArticle']] if CONFIG.get('featuredArticle') in records else ordered[0]
    # الهيرو: المقال المميز + أحدث ثلاثة من أقسام مختلفة عنه
    side=[];seen_cats={lead['category']}
    for a in ordered:
        if a['slug']==lead['slug'] or a['category'] in seen_cats:continue
        side.append(a);seen_cats.add(a['category'])
        if len(side)==3:break
    # لو لم تكتمل ثلاثة أقسام مختلفة، أكمل بالأحدث بغض النظر عن القسم.
    if len(side)<3:
        for a in ordered:
            if a['slug']==lead['slug'] or any(s['slug']==a['slug'] for s in side):continue
            side.append(a)
            if len(side)==3:break
    used={lead['slug'],*(s['slug'] for s in side)}
    river=[a for a in ordered if a['slug'] not in used][:7]
    strip=''.join(f'<a href="category/{c["slug"]}.html">{c["name"]}</a>' for c in CONFIG['categories'])
    bands=''
    for c in CONFIG['categories']:
        arts=[a for a in ordered if a['category']==c['name']][:4]
        if len(arts)>=4:bands+=ed_band(c,arts)
    guides=[('01','guide-safe-cleaning.html','دليل التنظيف الآمن','المنتجات والتهوية ومنع الخلطات الخطرة.'),
            ('02','guide-account-security.html','دليل حماية الحسابات','المنع والاسترداد والدفع الآمن.'),
            ('03','guide-gulf-recipes.html','دليل الوصفات الخليجية','الأرز والبهارات والمقبلات والمشروبات.'),
            ('04','guide-smartphone.html','دليل الهاتف','الاختيار والفحص والحماية والاستخدام.')]
    guides_html=''.join(f'<a class="ed-guide" href="{h}"><span class="ed-gnum">{n}</span><h3>{t}</h3><p>{d}</p>'
                        f'<span class="ed-garrow">ابدأ المسار</span></a>' for n,h,t,d in guides)
    organization={"@context":"https://schema.org","@type":"Organization","name":CONFIG['siteName'],"url":BASE,"description":CONFIG['description']}
    if CONFIG.get('contact',{}).get('enabled') and CONFIG.get('email'):organization['email']=CONFIG['email']
    faq_items=[
        ("ما هو موقع دليلك؟","مجلة عربية تقدم محتوى عمليًا في النصائح المنزلية والوصفات والمعرفة والتكنولوجيا بلغة واضحة وتصميم مريح."),
        ("هل المحتوى مجاني؟","نعم، جميع المقالات متاحة للقراءة دون تسجيل أو اشتراك."),
        ("كيف يُراجع المحتوى؟","نراجع وضوح المقال ومصادر الادعاءات القابلة للتحقق، ونحدّث المحتوى عند اكتشاف خطأ أو تغير المعلومة."),
        ("هل يمكن اقتراح موضوع أو إرسال تصحيح؟","نعم، نستقبل الاقتراحات والتصحيحات الموثقة عبر صفحة اتصل بنا.")]
    faq={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq_items]}
    faq_html=''.join(f'<details{" open" if i==0 else ""}><summary>{q}</summary><p>{a}</p></details>' for i,(q,a) in enumerate(faq_items))
    jsonlds='\n'.join('<script type="application/ld+json">'+json.dumps(x,ensure_ascii=False,separators=(',',':'))+'</script>' for x in (organization,faq))
    return f'''<main id="main-content">
<section class="ed-hero"><div class="wrap"><div class="ed-hero-grid">{ed_lead(lead)}<div class="ed-hero-side"><div class="ed-side-head"><h2 class="ed-kicker">أبرز ما نُشر</h2></div>{''.join(ed_side_item(a,i+1) for i,a in enumerate(side))}</div></div></div></section><nav class="ed-strip" aria-label="الأقسام"><div class="wrap"><div class="ed-strip-in"><span class="ed-strip-lbl">تصفّح</span>{strip}<a class="ed-strip-all" href="sitemap.html">خريطة الموقع</a></div></div></nav><section class="ed-sec"><div class="wrap"><div class="ed-sec-h"><h2 class="ed-sec-t">أحدث المقالات</h2><a class="ed-more" href="sitemap.html">جميع المقالات</a></div><div class="ed-river">{''.join(ed_riv(a) for a in river)}</div></div></section>{bands}<section class="ed-sec ed-guides-sec"><div class="wrap"><div class="ed-sec-h inv"><h2 class="ed-sec-t">أدلة دليلك</h2><a class="ed-more" href="sitemap.html">كل الأدلة</a></div><div class="ed-guides">{guides_html}</div></div></section><section class="ed-sec"><div class="wrap"><div class="ed-trust"><div><span class="ed-kicker ed-kicker-light">منهجية التحرير</span><h2>الثقة تبدأ بالوضوح</h2><p>نراجع وضوح المقال ومصادر الادعاءات القابلة للتحقق، ونحدّث المحتوى عند اكتشاف خطأ أو تغيّر المعلومة.</p></div><div class="ed-trust-actions"><a class="ed-btn-light" href="editorial-policy.html">سياسة التحرير</a><a class="ed-btn-ghost" href="authors/editorial-team.html">فريق التحرير</a></div></div></div></section><section class="sec"><div class="wrap"><div class="sec-h"><div class="sec-title"><span class="section-kicker">عن الموقع</span><h2>أسئلة شائعة</h2></div></div><div class="faq">{faq_html}</div></div></section>
{jsonlds}</main>'''

def redesign_home(path:Path,records:dict[str,dict])->None:
    text=read(path); newmain=home_main(records,text)
    text=re.sub(r'<main id="main-content">.*?</main>',newmain,text,count=1,flags=re.S)
    text=inject_shell(path,text)
    # واجهة المجلة تعتمد على editorial.css — تأكد من ربطه دائمًا بعد style.css.
    if 'css/editorial.css' not in text:
        text=text.replace('<link rel="stylesheet" href="css/style.css?v=11">',
                          '<link rel="stylesheet" href="css/style.css?v=11">\n<link rel="stylesheet" href="css/editorial.css?v=1">',1)
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

def add_breadcrumbs(text:str,trail:list[tuple[str,str]])->str:
    """يضيف BreadcrumbList قبل </main> إن لم يكن موجودًا."""
    if 'BreadcrumbList' in text:return text
    data={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":n,"item":u} for i,(n,u) in enumerate(trail)]}
    tag='<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False,separators=(',',':'))+'</script>'
    return text.replace('</main>',tag+'</main>',1) if '</main>' in text else text

def redesign_category(path:Path,records:dict[str,dict])->None:
    text=read(path); slug=path.stem
    names={x["slug"]:x["name"] for x in CONFIG["categories"]}; name=names[slug]; desc=CAT_DESCRIPTIONS[name]
    intro=f'''<div class="wrap category-wrap"><div class="crumb"><a href="../index.html">الرئيسية</a><span>/</span><span>{name}</span></div><div class="category-intro"><div><span class="section-kicker">قسم دليلك</span><h1>{name}</h1><p>{desc}</p></div><span class="category-count">{sum(1 for x in records.values() if x['category']==name)} مقالات متاحة</span></div><h2 class="sr-only">مقالات قسم {name}</h2><div class="grid">'''
    text=re.sub(r'<div class="wrap" style="padding-top:38px">.*?<div class="grid">',intro,text,count=1,flags=re.S)
    article_count=sum(1 for x in records.values() if x['category']==name)
    text=re.sub(r'<span class="category-count">\d+ مقالات متاحة</span>',f'<span class="category-count">{article_count} مقالات متاحة</span>',text,count=1)
    # عنوان قسم مخفي بصريًا يمنع قفزة h1->h3 في بطاقات المقالات (يعمل حتى لو أُعيد التوليد).
    if 'sr-only">مقالات قسم' not in text:
        text=text.replace('</div><div class="grid">',f'</div><h2 class="sr-only">مقالات قسم {name}</h2><div class="grid">',1)
    grid_start=text.index('<div class="grid">',text.index('category-wrap'))+len('<div class="grid">')
    collection_start=text.index('<script type="application/ld+json">',grid_start)
    wrap_close=text.rfind('</div>',grid_start,collection_start)
    grid_close=text.rfind('</div>',grid_start,wrap_close)
    category_articles=sorted((a for a in records.values() if a['category']==name),key=lambda a:a['published'],reverse=True)
    text=text[:grid_start]+''.join(article_card(a,prefix='../') for a in category_articles)+text[grid_close:]
    # أغلفة أقسام مخصّصة (1200x630) بدل إعادة استخدام صور المقالات.
    cover_url=f'{BASE}/images/og-{slug}.png'
    text=re.sub(r'<meta property="og:image" content="[^"]+">',f'<meta property="og:image" content="{cover_url}">',text,count=1)
    text=re.sub(r'<meta name="twitter:image" content="[^"]+">',f'<meta name="twitter:image" content="{cover_url}">',text,count=1)
    text=add_breadcrumbs(text,[("الرئيسية",f"{BASE}/"),(name,f"{BASE}/category/{slug}.html")])
    text=inject_shell(path,text)
    write(path,text)

def share_bar(a:dict)->str:
    """شريط مشاركة موحّد لكل المقالات (واتساب/تيليجرام/فيسبوك/إكس/نسخ)."""
    url=f'{BASE}/posts/{a["slug"]}.html'
    u=urllib.parse.quote(url,safe='');tt=urllib.parse.quote(a['title'],safe='')
    return ('<div class="share"><b>شارك المقال:</b>'
        f'<a class="sh-wa" href="https://wa.me/?text={tt}%20{u}" target="_blank" rel="noopener">واتساب</a>'
        f'<a class="sh-tg" href="https://t.me/share/url?url={u}&text={tt}" target="_blank" rel="noopener">تيليجرام</a>'
        f'<a class="sh-fb" href="https://www.facebook.com/sharer/sharer.php?u={u}" target="_blank" rel="noopener">فيسبوك</a>'
        f'<a class="sh-x" href="https://twitter.com/intent/tweet?url={u}&text={tt}" target="_blank" rel="noopener">إكس</a>'
        '<button type="button" class="sh-cp" onclick="copyLink()">نسخ الرابط</button></div>')

def redesign_post(path:Path,records:dict[str,dict])->None:
    text=read(path); a=records[path.stem]; cat_slug=CAT_PATHS[a['category']]
    text=normalize_cards(text,records,"../")
    text=re.sub(r'<div class="art-meta">.*?</div>',f'''<div class="art-meta"><span>بقلم <a href="../authors/editorial-team.html" rel="author">{CONFIG['authorName']}</a></span><span>نُشر <time datetime="{a['published']}">{fmt_date(a['published'])}</time></span><span>حُدّث <time datetime="{a['modified']}">{fmt_date(a['modified'])}</time></span><span>{reading_time_label(a['minutes'])} قراءة</span></div>''',text,count=1,flags=re.S)
    art_picture=responsive_picture(a,'../','art-img','eager','(max-width: 960px) calc(100vw - 40px), 800px',True,'art-picture')
    text=re.sub(r'(?:<picture class="art-picture">.*?</picture>|<img class="art-img"[^>]+>)',art_picture,text,count=1,flags=re.S)
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
    # وحّد شريط المشاركة في كل المقالات (كان 11 مقالًا بزر نسخ فقط).
    text=re.sub(r'<div class="share">.*?</div>\s*(?=<div class="author")',share_bar(a),text,count=1,flags=re.S)
    text=text.replace('📑 محتويات المقال','محتويات المقال').replace('🔗 نسخ الرابط','نسخ الرابط').replace('<span class="t-ic">💡</span>','<span class="t-ic">مهم</span>').replace('<div class="author-av">✍</div>','<div class="author-av">د</div>')
    text=re.sub(r'<aside class="side"><nav class="toc".*?</nav>','<aside class="side">',text,count=1,flags=re.S)
    toc_match=re.search(r'<nav class="toc".*?</nav>',text,re.S)
    if toc_match:
        side_toc=toc_match.group(0).replace('aria-label="جدول محتويات المقال"','aria-label="فهرس المقال الجانبي"')
        text=text.replace('<aside class="side">','<aside class="side">'+side_toc,1)
    def fix_pop_cover(match:re.Match)->str:
        block=match.group(0); slug_match=re.search(r'href="\.\./posts/([^"/]+)\.html"',block)
        if not slug_match or slug_match.group(1) not in records:return block
        item=records[slug_match.group(1)];picture=responsive_picture(item,'../','pop-thumb','lazy','78px',False,'pop-picture')
        return re.sub(r'(?:<picture class="pop-picture">.*?</picture>|<img class="pop-thumb"[^>]+>)',picture,block,count=1,flags=re.S)
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
