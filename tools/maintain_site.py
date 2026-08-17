#!/usr/bin/env python3
"""صيانة ملفات موقع دليلك الثابتة والتحقق من اتساق البيانات."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://sbdh1285.github.io/dalilak"
TODAY = "2026-08-17"

CATEGORY_ICONS = {
    "نصائح منزلية": "🏠",
    "وصفات لذيذة": "🍽️",
    "معلومات عامة": "💡",
    "تكنولوجيا": "📱",
}

SOURCES = {
    "age-of-earth": [
        ("هيئة المسح الجيولوجي الأمريكية (USGS) — عمر الأرض", "https://pubs.usgs.gov/gip/geotime/age.html"),
        ("المتحف الوطني للتاريخ الطبيعي — عمر الأرض", "https://naturalhistory.si.edu/education/teaching-resources/anthropology-and-social-studies/age-earth"),
    ],
    "ai-explained-simply": [
        ("المعهد الوطني للمعايير والتقنية (NIST) — الذكاء الاصطناعي وإدارة مخاطره", "https://www.nist.gov/itl/ai-risk-management-framework"),
        ("منظمة التعاون الاقتصادي والتنمية — مبادئ الذكاء الاصطناعي", "https://oecd.ai/en/ai-principles"),
    ],
    "amazing-animal-facts": [
        ("حديقة الحيوان الوطنية التابعة لسميثسونيان — موسوعة الحيوانات", "https://nationalzoo.si.edu/animals"),
        ("الموسوعة البريطانية — المملكة الحيوانية", "https://www.britannica.com/animal/animal"),
    ],
    "amazing-human-body-facts": [
        ("MedlinePlus — تشريح جسم الإنسان", "https://medlineplus.gov/anatomy.html"),
        ("المكتبة الوطنية للطب (NLM) — أجهزة وأعضاء جسم الإنسان", "https://toxtutor.nlm.nih.gov/08-003.html"),
    ],
    "amazing-water-facts": [
        ("هيئة المسح الجيولوجي الأمريكية — علوم المياه", "https://www.usgs.gov/special-topics/water-science-school"),
        ("منظمة الصحة العالمية — مياه الشرب", "https://www.who.int/news-room/fact-sheets/detail/drinking-water"),
    ],
    "galaxies-and-stars": [
        ("وكالة ناسا — ما المجرة؟", "https://spaceplace.nasa.gov/galaxy/en/"),
        ("وكالة ناسا للعلوم — الكون", "https://science.nasa.gov/universe/"),
    ],
    "why-we-need-sleep": [
        ("المراكز الأمريكية لمكافحة الأمراض — معلومات عن النوم", "https://www.cdc.gov/sleep/about/index.html"),
        ("المعهد الوطني للقلب والرئة والدم — الحرمان من النوم", "https://www.nhlbi.nih.gov/health/sleep-deprivation"),
    ],
    "coffee-story-yemen": [
        ("الموسوعة البريطانية — تاريخ القهوة", "https://www.britannica.com/topic/coffee"),
        ("المنظمة الدولية للقهوة — القهوة اليمنية وانتشارها من ميناء المخا", "https://www.ico.org/documents/icc-105-14e-statement-yemen.pdf"),
    ],
    "choose-smartphone-budget": [
        ("لجنة التجارة الفيدرالية — نصائح شراء الأجهزة المتصلة", "https://consumer.ftc.gov/articles/how-secure-your-voice-assistant-and-protect-your-privacy"),
        ("Android Help — تحسين عمر بطارية الجهاز", "https://support.google.com/android/answer/7664692"),
    ],
    "protect-online-accounts": [
        ("وكالة الأمن السيبراني الأمريكية CISA — المصادقة متعددة العوامل", "https://www.cisa.gov/MFA"),
        ("CISA — كلمات المرور القوية", "https://www.cisa.gov/secure-our-world/use-strong-passwords"),
    ],
    "essential-android-apps": [
        ("Google Play — الحماية من التطبيقات الضارة", "https://support.google.com/googleplay/answer/2812853"),
        ("Android — الأمان والخصوصية", "https://www.android.com/safety/"),
    ],
    "safe-online-payments": [
        ("لجنة التجارة الفيدرالية — التسوق والدفع عبر الإنترنت", "https://consumer.ftc.gov/articles/online-shopping"),
        ("CISA — التسوق الآمن عبر الإنترنت", "https://www.cisa.gov/news-events/news/shop-safely-online-holiday-season-tips-secure-our-world"),
    ],
    "save-mobile-data": [
        ("Android Help — تقليل استخدام بيانات الجوال", "https://support.google.com/android/answer/9458407"),
        ("Google Help — استخدام وضع توفير البيانات", "https://support.google.com/android/answer/9458407"),
    ],
    "speed-up-slow-computer": [
        ("Microsoft Support — نصائح لتحسين أداء الكمبيوتر", "https://support.microsoft.com/windows/tips-to-improve-pc-performance-in-windows-b3b3ef5b-5953-fb6a-2528-4bbed82fba96"),
        ("Microsoft Support — تحرير مساحة القرص", "https://support.microsoft.com/windows/free-up-drive-space-in-windows-85529ccb-c365-490d-b548-831022bc9b32"),
    ],
    "save-electricity-bill": [
        ("وزارة الطاقة الأمريكية — دليل توفير الطاقة", "https://www.energy.gov/energysaver/articles/energy-saver-guide"),
        ("وكالة الطاقة الدولية — كفاءة الطاقة", "https://www.iea.org/topics/energy-efficiency"),
    ],
    "organize-fridge-waste": [
        ("وزارة الزراعة الأمريكية — سلامة التبريد والغذاء", "https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/refrigeration"),
        ("ENERGY STAR — الثلاجات الموفرة للطاقة", "https://www.energystar.gov/products/refrigerators"),
    ],
    "natural-cleaning-recipes": [
        ("وكالة حماية البيئة — التنظيف الأكثر أمانًا", "https://www.epa.gov/saferchoice"),
        ("مراكز مكافحة الأمراض — تنظيف المنزل وتعقيمه", "https://www.cdc.gov/hygiene/about/when-and-how-to-clean-and-disinfect-your-home.html"),
    ],
    "natural-insect-repellents": [
        ("وكالة حماية البيئة — مكافحة الآفات بأمان", "https://www.epa.gov/safepestcontrol"),
        ("وكالة حماية البيئة — الإدارة المتكاملة للآفات", "https://www.epa.gov/ipm"),
    ],
    "laundry-guide-tips": [
        ("وكالة حماية البيئة — برنامج Safer Choice", "https://www.epa.gov/saferchoice"),
        ("Energy Star — غسالات الملابس", "https://www.energystar.gov/products/clothes_washers"),
    ],
    "quick-kitchen-cleaning": [
        ("مراكز مكافحة الأمراض — تنظيف المنزل وتعقيمه", "https://www.cdc.gov/hygiene/about/when-and-how-to-clean-and-disinfect-your-home.html"),
        ("وزارة الزراعة الأمريكية — نظافة المطبخ وسلامة الغذاء", "https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/cleanliness-helps-prevent"),
    ],
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def article_data(path: Path) -> dict:
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', read(path), re.S):
        data = json.loads(raw)
        if data.get("@type") == "Article":
            return data
    raise ValueError(f"لا توجد بيانات Article في {path}")


def collect_articles() -> list[dict]:
    articles = []
    for path in sorted((ROOT / "posts").glob("*.html")):
        data = article_data(path)
        articles.append({
            "path": path,
            "slug": path.stem,
            "title": data["headline"],
            "category": data["articleSection"],
            "date": data["datePublished"],
        })
    return articles


def remove_common_inline_script(text: str) -> str:
    pattern = re.compile(r'<script>(.*?)</script>', re.S)
    def replace(match: re.Match) -> str:
        body = match.group(1)
        if "localStorage.getItem('theme')" in body and "themeBtn" in body:
            return ""
        return match.group(0)
    return pattern.sub(replace, text)


def add_shared_script(text: str, nested: bool) -> str:
    if "js/main.js" in text:
        return text
    src = "../js/main.js?v=1" if nested else "js/main.js?v=1"
    return text.replace("</body>", f'<script src="{src}" defer></script>\n</body>')


def fix_accessibility(text: str) -> str:
    # رأس الصفحة وأدواته
    text = re.sub(
        r'<input class="icon-btn" id="searchInput"[^>]*>',
        '<input class="icon-btn" id="searchInput" type="search" aria-label="البحث في مقالات دليلك" '
        'autocomplete="off" placeholder="ابحث…" style="width:150px;text-align:right;padding:0 12px;font-family:inherit">',
        text,
    )
    text = re.sub(
        r'<div class="search-res" id="searchRes"[^>]*>',
        '<div class="search-res" id="searchRes" role="status" aria-live="polite"></div>',
        text,
    )
    # عالج الإغلاق المكرر الناتج من الاستبدال السابق
    text = text.replace('<div class="search-res" id="searchRes" role="status" aria-live="polite"></div></div>', '<div class="search-res" id="searchRes" role="status" aria-live="polite"></div>')
    text = re.sub(
        r'<button class="icon-btn" id="themeBtn"[^>]*>.*?</button>',
        '<button class="icon-btn" id="themeBtn" type="button" aria-label="تفعيل الوضع الليلي" aria-pressed="false">🌙</button>',
        text,
    )
    text = re.sub(
        r'<button class="icon-btn burger" id="burger"[^>]*>.*?</button>',
        '<button class="icon-btn burger" id="burger" type="button" aria-label="فتح القائمة" aria-controls="nav" aria-expanded="false">☰</button>',
        text,
    )
    text = text.replace('<nav id="nav">', '<nav id="nav" aria-label="التنقل الرئيسي">')
    text = text.replace('<nav class="toc">', '<nav class="toc" aria-label="جدول محتويات المقال">')
    text = re.sub(r'<button id="toTop"(?![^>]*\btype=)', '<button id="toTop" type="button"', text)
    text = re.sub(r'<button class="sh-cp"', '<button type="button" class="sh-cp"', text)
    if '<body>' in text and 'class="skip-link"' not in text:
        text = text.replace('<body>', '<body>\n<a class="skip-link" href="#main-content">تجاوز إلى المحتوى</a>')
    text = text.replace('<main>', '<main id="main-content">')
    return text


def update_jsonld(text: str) -> str:
    pattern = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)
    def replace(match: re.Match) -> str:
        try:
            data = json.loads(match.group(2))
        except json.JSONDecodeError:
            return match.group(0)
        if data.get("@type") == "Article":
            data["dateModified"] = TODAY
            data["author"] = {
                "@type": "Organization",
                "name": "فريق تحرير دليلك",
                "url": f"{BASE}/authors/editorial-team.html",
            }
        if data.get("@type") == "Organization" and data.get("name") == "دليلك":
            data["url"] = BASE
            data["email"] = "contact@dalilak.com"
        return match.group(1) + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + match.group(3)
    return pattern.sub(replace, text)


def source_section(slug: str) -> str:
    items = SOURCES.get(slug)
    if not items:
        return ""
    links = "".join(
        f'<li><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></li>'
        for title, url in items
    )
    return (
        '<section class="sources" aria-labelledby="sources-title">'
        '<h2 id="sources-title">المصادر والمراجع</h2>'
        '<p>رُوجعت المعلومات العامة في هذا المقال بالاستناد إلى المصادر التالية. الروابط الخارجية قد تُحدّث محتواها بمرور الوقت.</p>'
        f'<ul>{links}</ul></section>\n'
    )


def fix_post(path: Path, categories: dict[str, str]) -> None:
    text = read(path)
    slug = path.stem
    text = remove_common_inline_script(text)
    text = fix_accessibility(text)
    text = update_jsonld(text)

    # احذف نسخة المصادر السابقة إن أعيد تشغيل السكربت، ثم أضف النسخة الحالية.
    text = re.sub(r'<section class="sources".*?</section>\s*', '', text, flags=re.S)
    sources = source_section(slug)
    if sources:
        text = text.replace('<div class="share">', sources + '<div class="share">', 1)

    # اربط اسم فريق التحرير بصفحته.
    text = text.replace(
        '<b>فريق تحرير دليلك</b>',
        '<b><a href="../authors/editorial-team.html" rel="author">فريق تحرير دليلك</a></b>',
    )
    text = text.replace(
        'فريق دليلك يكتب محتوى عربيًا أصليًا ومفيدًا، ويراجع المعلومات بدقة قبل نشرها.',
        'فريق تحريري يراجع وضوح المحتوى ومصادر الادعاءات القابلة للتحقق، ويحدّث المقالات عند الحاجة.',
    )

    # أصلح تصنيفات بطاقات «الأكثر قراءة» داخل الشريط الجانبي.
    def fix_pop(match: re.Match) -> str:
        block = match.group(0)
        slug_match = re.search(r'href="\.\./posts/([^"/]+)\.html"', block)
        if slug_match and slug_match.group(1) in categories:
            category = categories[slug_match.group(1)]
            block = re.sub(r'<span class="pop-cat">.*?</span>', f'<span class="pop-cat">{category}</span>', block)
        return block
    text = re.sub(r'<div class="pop-item">.*?</div></div>', fix_pop, text, flags=re.S)

    text = replace_footer(text, nested=True)
    text = add_shared_script(text, nested=True)
    write(path, text)


def root_link_block(prefix: str = "") -> str:
    return f'''<footer><div class="wrap">
  <div class="fgrid">
    <div><div class="logo-ic" style="width:44px;height:44px;font-size:1.3rem">📘</div><h4 style="margin:10px 0 8px">دليلك</h4><p>دليلك اليومي لمحتوى عربي عملي ومفيد، مكتوب بوضوح ويُراجع ويُحدّث عند الحاجة.</p></div>
    <div><h4>الأقسام</h4><a href="{prefix}category/home-tips.html">نصائح منزلية</a><a href="{prefix}category/recipes.html">وصفات لذيذة</a><a href="{prefix}category/knowledge.html">معلومات عامة</a><a href="{prefix}category/tech.html">تكنولوجيا</a></div>
    <div><h4>روابط مهمة</h4><a href="{prefix}about.html">من نحن</a><a href="{prefix}contact.html">اتصل بنا</a><a href="{prefix}privacy-policy.html">سياسة الخصوصية</a><a href="{prefix}terms.html">شروط الاستخدام</a><a href="{prefix}disclaimer.html">إخلاء المسؤولية</a><a href="{prefix}editorial-policy.html">سياسة التحرير</a><a href="{prefix}authors/editorial-team.html">فريق التحرير</a><a href="{prefix}sitemap.html">خريطة الموقع</a></div>
    <div><h4>تواصل معنا</h4><p><a href="mailto:contact@dalilak.com">contact@dalilak.com</a></p><p>نرحب بالتصحيحات والملاحظات واقتراحات المواضيع.</p></div>
  </div>
  <div class="f-bottom"><span>© 2026 دليلك — جميع الحقوق محفوظة.</span><span>محتوى عربي مفيد ومراجع</span></div>
</div></footer>'''


def replace_footer(text: str, nested: bool) -> str:
    prefix = "../" if nested else ""
    return re.sub(r'<footer>.*?</footer>', root_link_block(prefix), text, count=1, flags=re.S)


def fix_general_page(path: Path) -> None:
    nested = path.parent != ROOT
    text = read(path)
    text = remove_common_inline_script(text)
    text = fix_accessibility(text)
    text = replace_footer(text, nested=nested)
    text = add_shared_script(text, nested=nested)
    text = text.replace('fonts/tajawal-00.woff2', 'fonts/tajawal-700.woff2')
    text = text.replace('font-size:.3rem', 'font-size:1.3rem').replace('margin:0px 0 8px', 'margin:10px 0 8px')
    text = text.replace('<h>', '<h1>').replace('</h>', '</h1>')
    text = update_jsonld(text)
    write(path, text)


def standard_head(title: str, description: str, canonical: str, prefix: str = "") -> str:
    return f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | دليلك</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#0f766e">
<link rel="preload" href="{prefix}fonts/tajawal-700.woff2" as="font" type="font/woff2" crossorigin>
<link rel="icon" type="image/svg+xml" href="{prefix}favicon.svg">
<link rel="manifest" href="{prefix}manifest.json">
<link rel="stylesheet" href="{prefix}css/style.css?v=6">
</head>'''


def standard_header(prefix: str = "") -> str:
    return f'''<header><div class="wrap hbar">
<a class="logo" href="{prefix}index.html"><span class="logo-ic">📘</span> دليلك</a>
<nav id="nav" aria-label="التنقل الرئيسي"><a href="{prefix}index.html">الرئيسية</a><a href="{prefix}category/home-tips.html">نصائح منزلية</a><a href="{prefix}category/recipes.html">وصفات لذيذة</a><a href="{prefix}category/knowledge.html">معلومات عامة</a><a href="{prefix}category/tech.html">تكنولوجيا</a><a href="{prefix}about.html">من نحن</a><a href="{prefix}contact.html">اتصل بنا</a></nav>
<div class="h-actions"><div class="search-box"><input class="icon-btn" id="searchInput" type="search" aria-label="البحث في مقالات دليلك" autocomplete="off" placeholder="ابحث…" style="width:150px;text-align:right;padding:0 12px;font-family:inherit"><div class="search-res" id="searchRes" role="status" aria-live="polite"></div></div><button class="icon-btn" id="themeBtn" type="button" aria-label="تفعيل الوضع الليلي" aria-pressed="false">🌙</button><button class="icon-btn burger" id="burger" type="button" aria-label="فتح القائمة" aria-controls="nav" aria-expanded="false">☰</button></div>
</div></header>'''


def make_info_page(filename: str, title: str, description: str, body: str, nested: bool = False) -> None:
    prefix = "../" if nested else ""
    canonical = f"{BASE}/{'authors/' if nested else ''}{filename}"
    html = f'''{standard_head(title, description, canonical, prefix)}
<body>
<a class="skip-link" href="#main-content">تجاوز إلى المحتوى</a>
<div id="progress"></div>
{standard_header(prefix)}
<main id="main-content"><div class="page"><h1>{title}</h1>{body}</div></main>
{root_link_block(prefix)}
<button id="toTop" type="button" aria-label="العودة إلى أعلى الصفحة">↑</button>
<script src="{prefix}js/main.js?v=1" defer></script>
</body></html>'''
    target = ROOT / ("authors" if nested else "") / filename
    write(target, html)


def create_trust_pages() -> None:
    if (ROOT / "site-config.json").exists() and (ROOT / "authors" / "editorial-team.html").exists():
        return
    make_info_page(
        "editorial-policy.html",
        "سياسة التحرير",
        "تعرف على آلية إعداد محتوى دليلك ومراجعته وتصحيحه وتحديثه.",
        '''<p class="sub">كيف نكتب ونراجع ونحدّث المحتوى</p>
<h2>اختيار الموضوع</h2><p>نختار المواضيع بناءً على فائدتها العملية للقارئ العربي، ونتجنب العناوين المضللة والوعود غير القابلة للإثبات.</p>
<h2>الكتابة والمراجعة</h2><p>يُراجع كل مقال من حيث الوضوح، واللغة، واتساق الخطوات، والادعاءات التي يمكن التحقق منها. نضيف روابط إلى مصادر رسمية أو مؤسسات معروفة عندما يتناول المقال معلومات علمية أو صحية أو أمنية أو تقنية.</p>
<h2>الوصفات والتجارب العملية</h2><p>نوضح المقادير والخطوات واحتياطات السلامة قدر الإمكان. تختلف النتائج بحسب المكونات والأجهزة والظروف، لذلك ينبغي استخدام الحكم الشخصي واتباع تعليمات السلامة الخاصة بالمنتجات.</p>
<h2>التصحيحات والتحديثات</h2><p>عند اكتشاف خطأ جوهري نصححه ونحدّث تاريخ المراجعة. نرحب بتنبيهات القراء عبر <a href="contact.html">صفحة الاتصال</a>.</p>
<h2>الاستقلالية والإعلانات</h2><p>لا تعني الإعلانات أو الروابط الخارجية تأييدًا تلقائيًا لمنتج أو جهة. وإذا نُشر مستقبلًا محتوى برعاية جهة ما فسيُوسم بوضوح.</p>
<h2>حدود المحتوى</h2><p>المحتوى للتثقيف العام وليس بديلًا عن الطبيب أو المختص أو التعليمات الرسمية، خصوصًا في مسائل الصحة والسلامة والأمن الرقمي.</p>''',
    )
    make_info_page(
        "editorial-team.html",
        "فريق تحرير دليلك",
        "صفحة فريق تحرير دليلك المسؤول عن إعداد المحتوى العربي ومراجعته وتحديثه.",
        '''<p class="sub">الجهة التحريرية المسؤولة عن محتوى الموقع</p>
<div class="author author-page"><div class="author-av">✍</div><div><h2>من نحن؟</h2><p>فريق تحرير دليلك هو الاسم التحريري المستخدم للمقالات المنشورة في الموقع. نعمل على تقديم شروحات ونصائح ووصفات ومعلومات عامة بلغة عربية واضحة.</p></div></div>
<h2>مسؤولياتنا</h2><ul><li>مراجعة بنية المقال ووضوحه قبل النشر.</li><li>الرجوع إلى مصادر موثوقة في الموضوعات القابلة للتحقق.</li><li>إضافة تنبيهات السلامة وحدود الاستخدام عند الحاجة.</li><li>تصحيح الأخطاء وتحديث المحتوى القديم.</li></ul>
<h2>تواصل مع الفريق</h2><p>يمكنك إرسال تصحيح موثق أو اقتراح موضوع عبر <a href="../contact.html">صفحة اتصل بنا</a> أو البريد <a href="mailto:contact@dalilak.com">contact@dalilak.com</a>.</p>
<p class="transparency-note"><strong>ملاحظة شفافية:</strong> هذه الصفحة تعرّف بالجهة التحريرية للموقع ولا تدّعي وجود اعتماد مهني طبي أو قانوني. يُذكر اسم المختص واعتماده بوضوح إذا شارك مستقبلًا في مراجعة محتوى تخصصي.</p>''',
        nested=True,
    )
    make_info_page(
        "thanks.html",
        "شكرًا لتواصلك",
        "تم استلام رسالة التواصل المرسلة إلى فريق دليلك.",
        '''<p class="sub">وصلت رسالتك بنجاح</p><div class="box"><p>شكرًا لك. سنراجع الرسالة ونرد على البريد الذي أدخلته متى كان الرد مطلوبًا.</p><p><a class="btn btn-a" href="index.html">العودة إلى الرئيسية</a></p></div>''',
    )


def update_contact() -> None:
    path = ROOT / "contact.html"
    text = read(path)
    form = f'''<h2>أرسل رسالة</h2>
<form class="contact-form" action="https://formsubmit.co/contact@dalilak.com" method="POST">
  <input type="hidden" name="_subject" value="رسالة جديدة من موقع دليلك">
  <input type="hidden" name="_next" value="{BASE}/thanks.html">
  <input type="hidden" name="_captcha" value="true">
  <input class="form-honeypot" type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true">
  <div class="form-grid"><div><label for="contact-name">الاسم</label><input id="contact-name" name="name" type="text" autocomplete="name" required></div><div><label for="contact-email">البريد الإلكتروني</label><input id="contact-email" name="email" type="email" autocomplete="email" required></div></div>
  <label for="contact-topic">الموضوع</label><select id="contact-topic" name="topic" required><option value="">اختر الموضوع</option><option>اقتراح مقال</option><option>تصحيح محتوى</option><option>استفسار عام</option><option>إعلان أو شراكة</option></select>
  <label for="contact-message">الرسالة</label><textarea id="contact-message" name="message" rows="7" minlength="10" required></textarea>
  <p class="form-note">بإرسال النموذج توافق على معالجة البيانات اللازمة للرد وفق <a href="privacy-policy.html">سياسة الخصوصية</a>. لا ترسل معلومات حساسة.</p>
  <button class="btn btn-a" type="submit">إرسال الرسالة</button>
</form>'''
    if '<form class="contact-form"' not in text:
        text = text.replace('  <h2>اقتراحات المواضيع</h2>', form + '\n  <h2>اقتراحات المواضيع</h2>')
    write(path, text)


def update_legal_pages() -> None:
    privacy = ROOT / "privacy-policy.html"
    text = read(privacy)
    text = text.replace('آخر تحديث: 6 أغسطس 2026', 'آخر تحديث: 17 أغسطس 2026')
    text = text.replace('<h2>. المعلومات التي نجمعها</h2>', '<h2>1. المعلومات التي نجمعها</h2>')
    old = 'يستخدم الموقع ملفات تعريف الارتباط لتخزين تفضيلات الزائرين وتتبع الصفحات التي تمت زيارتها، مما يساعدنا على تحسين المحتوى والتجربة. يمكنك تعطيل ملفات تعريف الارتباط من إعدادات متصفحك في أي وقت.'
    new = 'لا يستخدم الموقع حاليًا ملفات تعريف ارتباط خاصة به لتتبع الزائرين. نحفظ تفضيل الوضع الليلي محليًا في متصفحك عبر localStorage. وقد تستخدم خدمات خارجية ملفات تعريف ارتباط إذا أضفنا إعلانات أو أدوات قياس مستقبلًا، وعندها سنحدّث هذه السياسة ونطلب الموافقة حيث يلزم.'
    text = text.replace(old, new)
    text = text.replace('يعرض الموقع إعلانات من طرف ثالث', 'قد يعرض الموقع مستقبلًا إعلانات من طرف ثالث')
    form_privacy = '<h2>4. نموذج التواصل والخدمات الخارجية</h2><p>عند إرسال نموذج التواصل، تُرسل البيانات التي تدخلها إلى خدمة FormSubmit لمعالجة الرسالة وتسليمها إلى بريدنا. لا ترسل كلمات مرور أو بيانات مالية أو معلومات حساسة. يمكنك بدلًا من ذلك مراسلتنا مباشرة عبر البريد.</p>'
    text = text.replace('<h2>4. روابط خارجية</h2>', form_privacy + '<h2>5. روابط خارجية</h2>')
    text = text.replace('<h2>5. حقوقك</h2>', '<h2>6. حقوقك</h2>').replace('<h2>6. تحديثات السياسة</h2>', '<h2>7. تحديثات السياسة</h2>')
    write(privacy, text)

    terms = ROOT / "terms.html"
    text = read(terms)
    text = text.replace('آخر تحديث:  أغسطس 2026', 'آخر تحديث: 17 أغسطس 2026')
    text = text.replace('<h2>. استخدام المحتوى</h2>', '<h2>1. استخدام المحتوى</h2>')
    text = text.replace('<h2>. التواصل</h2>', '<h2>7. التواصل</h2>')
    write(terms, text)


def update_manifest() -> None:
    path = ROOT / "manifest.json"
    data = json.loads(read(path))
    data["start_url"] = "/dalilak/"
    data["scope"] = "/dalilak/"
    data["id"] = "/dalilak/"
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def update_index_and_css() -> None:
    index = ROOT / "index.html"
    text = read(index)
    text = text.replace(
        '<title>دليلك | دليلك اليومي لنصائح عملية، وصفات شهية، ومعلومات مفيدة | دليلك</title>',
        '<title>دليلك | نصائح ووصفات ومعلومات عربية مفيدة</title>',
    )
    text = text.replace('محتوى أصلي 100%', 'محتوى عربي مفيد')
    write(index, text)

    css = ROOT / "css/style.css"
    text = read(css)
    additions = '''
/* ===== الوصول والنماذج والمصادر ===== */
.skip-link{position:fixed;top:8px;right:8px;z-index:9999;background:var(--dk);color:#fff;padding:10px 16px;border-radius:10px;transform:translateY(-150%);transition:transform .15s}
.skip-link:focus{transform:translateY(0);color:#fff}
.search-message{display:block;padding:14px;color:var(--mut)}
.all-results{font-weight:800;text-align:center;color:var(--p)!important}
.sources{margin:32px 0;padding:22px;background:var(--card);border:1px solid var(--bd);border-radius:var(--r2)}
.sources h2{margin:0 0 10px!important;font-size:1.2rem!important}
.sources p{font-size:.92rem;color:var(--mut);margin-bottom:10px}
.sources ul{margin:0;padding-right:22px;display:grid;gap:8px}
.contact-form{margin:18px 0 34px;padding:24px;background:var(--card);border:1px solid var(--bd);border-radius:var(--r2);box-shadow:var(--sh1);display:grid;gap:8px}
.contact-form label{font-weight:800;margin-top:6px}
.contact-form input,.contact-form textarea,.contact-form select{width:100%;font:inherit;color:var(--tx);background:var(--bg);border:1px solid var(--bd);border-radius:10px;padding:11px 12px}
.contact-form textarea{resize:vertical;min-height:150px}
.contact-form input:focus,.contact-form textarea:focus,.contact-form select:focus{border-color:var(--p);outline:3px solid var(--ring)}
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.form-honeypot{position:absolute!important;right:-9999px!important;width:1px!important;height:1px!important}
.form-note,.transparency-note{font-size:.9rem;color:var(--mut)}
.author-page{margin:22px 0}.author-page h2{margin-top:0}
@media(max-width:640px){.form-grid{grid-template-columns:1fr}.search-box #searchInput{width:116px!important}}
'''
    if 'MAGAZINE DESIGN' not in text and '/* ===== الوصول والنماذج والمصادر ===== */' not in text:
        text += additions
    write(css, text)


def update_sitemaps() -> None:
    sitemap = ROOT / "sitemap.xml"
    text = read(sitemap)
    additions = [
        f"  <url><loc>{BASE}/editorial-policy.html</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>",
        f"  <url><loc>{BASE}/authors/editorial-team.html</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>",
    ]
    for line in additions:
        url = re.search(r'<loc>(.*?)</loc>', line).group(1)
        if url not in text:
            text = text.replace('</urlset>', line + '\n</urlset>')
    # حدّث تاريخ الصفحات التي تغيرت.
    text = re.sub(r'<lastmod>2026-08-16</lastmod>', f'<lastmod>{TODAY}</lastmod>', text)
    write(sitemap, text)

    html_map = ROOT / "sitemap.html"
    text = read(html_map)
    if 'editorial-policy.html' not in text:
        text = text.replace('</div></main>', '<h2>الثقة والتحرير</h2><ul><li><a href="editorial-policy.html">سياسة التحرير</a></li><li><a href="authors/editorial-team.html">فريق التحرير</a></li></ul></div></main>')
    write(html_map, text)


def update_readme() -> None:
    if (ROOT / "site-config.json").exists():
        return
    text = '''# دليلك

موقع محتوى عربي ثابت منشور عبر GitHub Pages، يضم نصائح منزلية ووصفات ومعلومات عامة وشروحات تقنية.

## النسخة المنشورة

https://sbdh1285.github.io/dalilak/

## المحتوى والبنية

- 30 مقالًا في أربعة أقسام.
- صفحات تعريف واتصال وخصوصية وشروط وإخلاء مسؤولية.
- صفحة لسياسة التحرير وصفحة لفريق التحرير.
- SEO: canonical وOpen Graph وJSON-LD وsitemap وRSS.
- تصميم RTL متجاوب، خطوط محلية، ووضع ليلي.
- بحث محلي دون قاعدة بيانات.

## الصيانة

شغّل أداة الصيانة بعد تعديل المقالات أو بياناتها:

```bash
python3 tools/maintain_site.py
python3 tools/audit_site.py
```

تقوم أداة الصيانة بإعادة بناء `search-index.json` من بيانات Article، وتوحيد الوظائف المشتركة، وفحص تصنيفات الشريط الجانبي.

## النشر

الموقع ملفات ثابتة ويُنشر من فرع `main` عبر GitHub Pages. لا يحتاج خطوة build ولا قاعدة بيانات.

## نموذج التواصل

يستخدم النموذج خدمة FormSubmit ويرسل إلى `contact@dalilak.com`. عند أول رسالة قد تطلب الخدمة تأكيد العنوان من صندوق البريد. يجب التأكد من أن البريد يعمل قبل الاعتماد على النموذج.

## AdSense

ملف `ads.txt` قالب فقط إلى أن يتم قبول الموقع والحصول على معرف ناشر حقيقي. لا تضع معرفًا وهميًا.

## ملاحظات تحريرية

- لا يُضمن قبول AdSense؛ القرار يعود إلى Google.
- راجع الحقائق والمصادر قبل نشر أي تحديث.
- لا تنشر نصائح صحية أو أمنية تخصصية دون مصادر موثوقة وتنبيه مناسب.
- حدّث تاريخ `dateModified` عند إجراء تغيير جوهري فقط.
'''
    write(ROOT / "README.md", text)


def main() -> None:
    articles = collect_articles()
    categories = {item["slug"]: item["category"] for item in articles}

    # فهرس البحث الصحيح، الأحدث أولًا.
    search = [
        {"t": item["title"], "s": item["slug"], "c": item["category"]}
        for item in sorted(articles, key=lambda item: (item["date"], item["slug"]), reverse=True)
    ]
    write(ROOT / "search-index.json", json.dumps(search, ensure_ascii=False, indent=2) + "\n")

    for item in articles:
        fix_post(item["path"], categories)

    for path in sorted(ROOT.rglob("*.html")):
        if "node_modules" in path.parts or "qa" in path.parts or path.parent.name == "posts":
            continue
        fix_general_page(path)

    update_manifest()
    update_index_and_css()
    update_contact()
    update_legal_pages()
    create_trust_pages()
    update_sitemaps()
    update_readme()

    # وحّد إصدار CSS بعد التعديل.
    for path in ROOT.rglob("*.html"):
        if "node_modules" in path.parts or "qa" in path.parts:
            continue
        text = read(path).replace('css/style.css?v=5', 'css/style.css?v=6')
        write(path, text)

    redesign = ROOT / "tools" / "redesign_magazine.py"
    if redesign.exists():
        subprocess.run([sys.executable, str(redesign)], check=True)
    print(f"تمت صيانة {len(articles)} مقالًا وتحديث فهرس البحث والصفحات المشتركة.")


if __name__ == "__main__":
    main()
