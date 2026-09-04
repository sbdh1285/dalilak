#!/usr/bin/env python3
"""ترقية تحريرية وتقنية لجودة الموقع قبل أدسنس."""
from __future__ import annotations

import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from content import BODIES  # noqa: E402
from content.extras import extra_block  # noqa: E402
from content.pads import pad_block  # noqa: E402

CFG = json.loads((ROOT / "site-config.json").read_text(encoding="utf-8"))
BASE = CFG["baseUrl"].rstrip("/")
TODAY = "2026-09-04"
CAT_PATH = {
    "نصائح منزلية": "home-tips",
    "وصفات لذيذة": "recipes",
    "معلومات عامة": "knowledge",
    "تكنولوجيا": "tech",
}
MARKER = "<!-- PROF-2026 -->"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def css_for(path: Path) -> str:
    nested = path.parent != ROOT
    prefix = "../" if nested else ""
    return f'{prefix}css/style.css?v=10'


def rebuild_toc(body: str) -> str:
    headings = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body, re.S)
    items = "".join(
        f'<li><a href="#{anchor}">{re.sub("<.*?>", "", title)}</a></li>'
        for anchor, title in headings
    )
    return f'<nav class="toc" aria-label="جدول محتويات المقال"><b>محتويات المقال</b><ul>{items}</ul></nav>'


def patch_jsonld(text: str, slug: str, meta: dict) -> str:
    def repl(match: re.Match) -> str:
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            return match.group(0)
        if data.get("@type") == "Article":
            data["headline"] = meta["title"]
            data["description"] = meta["description"]
            data["dateModified"] = TODAY
        if data.get("@type") == "WebPage":
            data["name"] = meta["title"]
            data["description"] = meta["description"]
        if data.get("@type") == "BreadcrumbList":
            try:
                data["itemListElement"][-1]["name"] = meta["title"]
            except Exception:
                pass
        if data.get("@type") == "Recipe":
            data["dateModified"] = TODAY
        if data.get("@type") == "Organization" and data.get("name") == "دليلك":
            if CFG.get("contact", {}).get("enabled") and CFG.get("email"):
                data["email"] = CFG["email"]
            else:
                data.pop("email", None)
        return '<script type="application/ld+json">' + json.dumps(
            data, ensure_ascii=False, separators=(",", ":")
        ) + "</script>"

    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', repl, text, flags=re.S)


def apply_article(slug: str, meta: dict) -> None:
    path = ROOT / "posts" / f"{slug}.html"
    text = read(path)
    title = meta["title"]
    desc = meta["description"]
    raw = meta["body"]
    extra = extra_block(slug) + pad_block(slug)
    if extra and '<h2 id="sec-end">الخلاصة</h2>' in raw:
        raw = raw.replace('<h2 id="sec-end">الخلاصة</h2>', extra + '<h2 id="sec-end">الخلاصة</h2>', 1)
    body = MARKER + raw
    start = text.find('<div class="art-body">')
    ends = [
        x
        for x in (
            text.find("<!-- CLUSTER-LINKS-START -->", start),
            text.find('<section class="cluster-links"', start),
            text.find('<section class="sources"', start),
            text.find('<div class="share">', start),
        )
        if x > start
    ]
    end = min(ends)
    text = text[: start + len('<div class="art-body">')] + body + "</div>\n" + text[end:]
    toc = rebuild_toc(body)
    text = re.sub(
        r'<nav class="toc" aria-label="جدول محتويات المقال">.*?</nav>',
        toc,
        text,
        count=1,
        flags=re.S,
    )
    esc_title = html.escape(title)
    esc_desc = html.escape(desc, quote=True)
    text = re.sub(r"<title>.*?</title>", f"<title>{esc_title} | دليلك</title>", text, count=1)
    text = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{esc_desc}">',
        text,
        count=1,
    )
    text = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc_title}">', text)
    text = re.sub(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{esc_title}">', text)
    text = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc_desc}">', text)
    text = re.sub(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{esc_desc}">', text)
    text = re.sub(r"<h1>.*?</h1>", f"<h1>{esc_title}</h1>", text, count=1)
    text = re.sub(
        r'<p class="article-summary">.*?</p>',
        f'<p class="article-summary">{html.escape(desc)}</p>',
        text,
        count=1,
    )
    def crumb_repl(match: re.Match) -> str:
        return match.group(1) + esc_title + match.group(2)

    text = re.sub(
        r'(<div class="crumb">.*?<span>).*?(</span></div>)',
        crumb_repl,
        text,
        count=1,
        flags=re.S,
    )
    text = patch_jsonld(text, slug, meta)
    text = re.sub(r'dateModified":"[0-9-]+"', f'dateModified":"{TODAY}"', text)
    write(path, text)


def global_html_fixes() -> None:
    for path in ROOT.rglob("*.html"):
        if "node_modules" in path.parts:
            continue
        text = read(path)
        text = re.sub(
            r'<meta name="viewport" content="[^"]*">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            text,
        )
        text = re.sub(
            r'<meta name="theme-color" content="[^"]*">',
            '<meta name="theme-color" content="#124e4a">',
            text,
        )
        text = re.sub(r'href="(?:/dalilak/|\.\./)?css/style\.css\?v=\d+"', f'href="{css_for(path)}"', text)
        text = text.replace("contact@dalilak.com", "")
        write(path, text)


def page_main(title: str, sub: str, inner: str) -> str:
    return f'<main id="main-content"><div class="page"><h1>{title}</h1><p class="sub">{sub}</p>{inner}<p class="page-updated">آخر تحديث: 4 سبتمبر 2026</p></div></main>'


def replace_main(path: Path, main_html: str, title: str, desc: str) -> None:
    text = read(path)
    text = re.sub(r"<main id=\"main-content\">.*?</main>", main_html, text, count=1, flags=re.S)
    esc_title = html.escape(title)
    esc_desc = html.escape(desc, quote=True)
    text = re.sub(r"<title>.*?</title>", f"<title>{esc_title} | دليلك</title>", text, count=1)
    text = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc_desc}">', text, count=1)
    text = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc_title}">', text)
    text = re.sub(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{esc_title}">', text)
    text = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc_desc}">', text)
    text = re.sub(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{esc_desc}">', text)

    def fix_json(match: re.Match) -> str:
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            return match.group(0)
        if data.get("@type") == "WebPage":
            data["name"] = title
            data["description"] = desc
        if data.get("@type") == "Organization":
            if CFG.get("contact", {}).get("enabled") and CFG.get("email"):
                data["email"] = CFG["email"]
            else:
                data.pop("email", None)
        return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "</script>"

    text = re.sub(r'<script type="application/ld\+json">(.*?)</script>', fix_json, text, flags=re.S)
    write(path, text)


def update_static_pages() -> None:
    about = page_main(
        "من نحن",
        "مجلة عربية عملية تُكتب لتُستخدم لا لتُملأ",
        """
<p>دليلك مجلة عربية مستقلة تقدم شروحًا قابلة للتطبيق في البيت والمطبخ والتقنية اليومية، مع مقالات معرفية تشرح المفاهيم بدل قوائم الغرائب. لا نعد بحلول سحرية، ولا ننشر رقمًا قابلًا للتحقق دون مراجعة مصدر.</p>
<h2>ماذا ننشر؟</h2>
<ul>
<li><strong>نصائح منزلية:</strong> تنظيف آمن، ترتيب، غسيل، وتقليل الهدر والكهرباء.</li>
<li><strong>وصفات:</strong> أطباق عربية وخليجية بمقادير وخطوات ومشكلات شائعة.</li>
<li><strong>تكنولوجيا للمبتدئ:</strong> حماية حسابات، دفع، وهواتف دون مصطلحات للتباهي.</li>
<li><strong>معرفة مبسطة:</strong> شروح لأسئلة علمية شائعة مع حدود الادعاء.</li>
</ul>
<h2>كيف نعمل؟</h2>
<p>نختار سؤالًا عمليًا، نجمع مصادر رسمية أو مؤسسات معروفة عند الحاجة، ونصوغ النص بالعربية الواضحة مع جداول وقوائم تحقق. قد تُستخدم أدوات رقمية في التنظيم والصياغة، ولا تُعامل مخرجاتها كمصدر. التفاصيل في <a href="editorial-policy.html">سياسة التحرير</a> و<a href="authors/editorial-team.html">صفحة الفريق</a>.</p>
<h2>ما الذي لا ندّعيه؟</h2>
<p>لسنا جهة طبية أو قانونية أو مالية. المحتوى تثقيفي عام. السلامة المنزلية والأمن الرقمي يُرجع فيهما إلى الملصق والجهة الرسمية المختصة.</p>
<h2>التصحيحات</h2>
<p>إن وجدت خطأ، استخدم <a href="contact.html">صفحة الاتصال</a> مع رابط المقال والعبارة ومصدر التصحيح. نحدّث تاريخ المراجعة عند التغيير الجوهري.</p>
""",
    )
    replace_main(ROOT / "about.html", about, "من نحن", "تعرّف على مجلة دليلك: منهج الكتابة والمراجعة وحدود المحتوى وكيف تُرسل تصحيحًا.")

    email = (CFG.get("email") or "").strip()
    contact_on = bool(CFG.get("contact", {}).get("enabled") and email)
    if contact_on:
        contact_inner = f"""
<p>راسلنا للتصحيح أو اقتراح موضوع أو استفسار عام. العنوان الحالي: <a href="mailto:{email}">{email}</a>. هذا بريد Gmail يعمل لاستقبال الرسائل؛ ليس عنوانًا على دومين خاص بعد.</p>
<div class="contact-status" id="contact-status"><strong>النموذج جاهز</strong><p>يصل الإرسال إلى البريد نفسه عبر FormSubmit. عند أول رسالة قد تصلك رسالة تأكيد في الوارد أو الرسائل غير المرغوب فيها؛ أكّدها حتى تُسلَّم الرسائل التالية مباشرة.</p></div>
<h2>أرسل رسالة</h2>
<form class="contact-form" action="https://formsubmit.co/{email}" method="POST">
<input type="hidden" name="_subject" value="رسالة جديدة من موقع دليلك">
<input type="hidden" name="_next" value="{BASE}/thanks.html">
<input type="hidden" name="_captcha" value="true">
<input class="form-honeypot" type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true">
<div class="form-grid"><div><label for="contact-name">الاسم</label><input id="contact-name" name="name" type="text" autocomplete="name" required></div><div><label for="contact-email">بريدك للرد</label><input id="contact-email" name="email" type="email" autocomplete="email" required></div></div>
<label for="contact-topic">الموضوع</label>
<select id="contact-topic" name="topic" required>
<option value="">اختر الموضوع</option>
<option>اقتراح مقال</option>
<option>تصحيح محتوى</option>
<option>استفسار عام</option>
<option>إعلان أو شراكة</option>
</select>
<label for="contact-message">الرسالة</label>
<textarea id="contact-message" name="message" rows="7" minlength="10" required></textarea>
<p class="form-note">بإرسال النموذج توافق على معالجة الاسم وبريدك والرسالة للرد وفق <a href="privacy-policy.html">سياسة الخصوصية</a>. لا ترسل كلمات مرور أو بيانات مالية.</p>
<button class="btn btn-a" type="submit">إرسال الرسالة</button>
</form>
<h2>قالب تصحيح محتوى</h2>
<p>انسخ العناصر التالية في الرسالة:</p>
<ul>
<li>رابط الصفحة.</li>
<li>الجملة أو الرقم غير الدقيق.</li>
<li>التصحيح المقترح.</li>
<li>رابط مصدر رسمي أو علمي إن وجد.</li>
</ul>
<h2>اقتراح موضوع</h2>
<p>اكتب السؤال الذي تريد أن يجيب عنه المقال، والجمهور (مبتدئ أو صاحب تجربة)، وما الذي جربته ولم تجد شرحًا عربيًا واضحًا له. نفضّل المنزل والوصفات والأمن الرقمي البسيط.</p>
<h2>الإعلانات والشراكات</h2>
<p>يمكن مراسلتنا على البريد نفسه. أي تعاون مستقبلي سيُوسم في الصفحة المعنية. لا نضمن قبول برامج إعلانية.</p>
"""
        contact = page_main("اتصل بنا", "بريد منشور ونموذج يصل إلى نفس العنوان", contact_inner)
        replace_main(ROOT / "contact.html", contact, "اتصل بنا", f"تواصل مع دليلك عبر النموذج أو البريد {email} للتصحيح واقتراح الموضوع.")
    else:
        contact_inner = """
<p>نريد قناة تواصل تعمل فعليًا. لذلك لا نعرض بريدًا غير موجود ولا نموذجًا يضيع الرسائل. عند تفعيل البريد سيظهر العنوان والنموذج هنا، وتُحدَّث <a href="privacy-policy.html">سياسة الخصوصية</a> قبل جمع أي بيانات.</p>
<div class="box">
<p><b>الحالة:</b> قناة البريد قيد التجهيز.</p>
<p><b>ما يمكن تحضيره الآن:</b> نص التصحيح أو اقتراح الموضوع حتى يسهل إرساله فور التفعيل.</p>
</div>
<h2>قالب تصحيح محتوى</h2>
<p>انسخ العناصر التالية إلى رسالتك لاحقًا:</p>
<ul>
<li>رابط الصفحة.</li>
<li>الجملة أو الرقم غير الدقيق.</li>
<li>التصحيح المقترح.</li>
<li>رابط مصدر رسمي أو علمي إن وجد.</li>
</ul>
<h2>اقتراح موضوع</h2>
<p>اكتب السؤال الذي تريد أن يجيب عنه المقال، والجمهور (مبتدئ أو صاحب تجربة)، وما الذي جربته ولم تجد شرحًا عربيًا واضحًا له.</p>
"""
        contact = page_main("اتصل بنا", "قناة رسمية تُفعَّل عندما تعمل، لا عنوان للزينة", contact_inner)
        replace_main(ROOT / "contact.html", contact, "اتصل بنا", "حالة التواصل في دليلك: قالب التصحيح واقتراح الموضوع حتى تفعيل البريد.")

    privacy = page_main(
        "سياسة الخصوصية",
        "آخر تحديث: 4 سبتمبر 2026",
        """
<p>توضح هذه الصفحة الممارسات الحالية للموقع. سنحدّث التاريخ عند تغيير الاستضافة أو التواصل أو التحليلات أو الإعلانات.</p>
<h2>1. التصفح والاستضافة</h2>
<p>لا نطلب حسابًا لقراءة المقالات. الموقع ملفات ثابتة قد تُستضاف على GitHub Pages أو لاحقًا على استضافة أخرى. قد تسجّل جهة الاستضافة بيانات تقنية معتادة مثل عنوان IP وسجلات الطلبات لأغراض التشغيل والأمان وفق سياستها.</p>
<h2>2. التخزين المحلي</h2>
<p>نحفظ اختيار الوضع النهاري أو الليلي في المتصفح عبر التخزين المحلي. لا نستخدم حاليًا ملفات تعريف ارتباط خاصة بنا لتتبع الزائرين.</p>
<h2>3. التواصل</h2>
<p>إن كان النموذج مفعّلًا نجمع الاسم وبريد الرد والموضوع ونص الرسالة للرد عليك فقط. تُرسل البيانات عبر FormSubmit إلى بريد الموقع المنشور في صفحة الاتصال. لا ترسل كلمات مرور أو بيانات مالية. يمكنك الكتابة مباشرة إلى البريد الظاهر بدل النموذج. تفاصيل الحالة في <a href="contact.html">اتصل بنا</a>.</p>
<h2>4. التحليلات والإعلانات</h2>
<p>لا يوجد كود Google AdSense ولا معرف ناشر حقيقي ولا أداة تحليلات إعلانية مفعّلة. ملف ads.txt قالب معلّق فقط.</p>
<p>إذا قُبل الموقع لاحقًا في برنامج إعلانات أو أضفنا قياس زيارات، فسنحدّث هذه السياسة قبل التشغيل، ونوضح ملفات تعريف الارتباط والإعلانات المخصصة، ونوفّر آلية موافقة حيث يلزم القانون. Google قد تستخدم بيانات لعرض إعلانات وفق سياساتها عند التفعيل فقط.</p>
<h2>5. الروابط الخارجية</h2>
<p>بعض المقالات تربط مصادر رسمية. سياسة الموقع الخارجي تنطبق بعد مغادرتك.</p>
<h2>6. حقوقك</h2>
<p>لطلب استفسار خصوصية استخدم <a href="contact.html">اتصل بنا</a> أو البريد المنشور هناك إن وُجد.</p>
<h2>7. التحديث</h2>
<p>أي تغيير جوهري في جمع البيانات أو الإعلانات سيظهر بتاريخ جديد في أعلى هذه الصفحة.</p>
""",
    )
    replace_main(ROOT / "privacy-policy.html", privacy, "سياسة الخصوصية", "سياسة خصوصية دليلك: الاستضافة والتخزين المحلي وحالة التواصل وخطط الإعلانات المستقبلية.")

    terms = page_main(
        "شروط الاستخدام",
        "آخر تحديث: 4 سبتمبر 2026",
        """
<p>باستخدام الموقع توافق على هذه الشروط.</p>
<h2>1. طبيعة المحتوى</h2>
<p>المحتوى تثقيفي عام. الوصفات والنصائح المنزلية والتقنية ليست ضمان نتيجة، وتختلف حسب الأدوات والمكونات والأجهزة.</p>
<h2>2. الملكية</h2>
<p>النصوص والتصميم ملك للموقع. يمكنك مشاركة رابط أو اقتباس قصير مع المصدر. لا يُعاد نشر المقال كاملًا دون إذن.</p>
<h2>3. لا نصيحة متخصصة</h2>
<p>لا يغني المحتوى عن الطبيب أو الفني أو المستشار القانوني أو المالي. اتبع ملصقات المنتجات والتعليمات الرسمية.</p>
<h2>4. سلوك الزائر</h2>
<p>يُحظر إساءة استخدام النماذج عند تفعيلها، أو محاولة تعطيل الموقع، أو إرسال محتوى مخالف للقانون.</p>
<h2>5. الإعلانات</h2>
<p>قد تظهر إعلانات لاحقًا. وجود إعلان لا يعني تأييد المنتج. القبول في برامج الإعلانات قرار الجهة المزودة ولا يُضمن.</p>
<h2>6. المسؤولية</h2>
<p>استخدامك على مسؤوليتك. تحقق مستقلًا قبل قرارات مهمة.</p>
<h2>7. التواصل</h2>
<p>للاستفسار عن الشروط استخدم <a href="contact.html">صفحة الاتصال</a>.</p>
""",
    )
    replace_main(ROOT / "terms.html", terms, "شروط الاستخدام", "شروط استخدام دليلك: طبيعة المحتوى والملكية وحدود المسؤولية والإعلانات.")

    disc = page_main(
        "إخلاء المسؤولية",
        "حدود ما يقدمه الموقع",
        """
<p>نبذل جهدًا معقولًا للدقة ونحدّث عند اكتشاف خطأ جوهري، لكن المعلومات تتغير وقد تفوتنا شائبة.</p>
<h2>الصحة والسلامة</h2>
<p>لا تجرب خلط منظفات، ولا تعتبر المقال بديل إسعاف. في أعراض مرضية أو غاز أو حريق اتبع الجهات المحلية.</p>
<h2>الأمن والمال</h2>
<p>حماية الحسابات والدفع الإلكتروني إرشادات عامة. إجراءات بنكك وقوانين بلدك مقدمة.</p>
<h2>الوصفات</h2>
<p>سلامة الغذاء: نظافة، درجات حرارة مناسبة، وتبريد بقايا. من لديهم حساسية يراجعون المكونات بأنفسهم.</p>
<h2>الإعلانات</h2>
<p>لا نضمن قبول أدسنس أو أي برنامج. لا نقدّم وعود ربح.</p>
""",
    )
    replace_main(ROOT / "disclaimer.html", disc, "إخلاء المسؤولية", "إخلاء مسؤولية دليلك: المحتوى تثقيفي ولا يغني عن المختص ولا يضمن قبول الإعلانات.")

    editorial = page_main(
        "سياسة التحرير",
        "كيف نختار ونكتب ونصحح",
        """
<h2>اختيار الموضوع</h2>
<p>نفضل سؤالًا يمكن للقارئ تطبيقه في يومه، ونتجنب العناوين التي تعد بنتيجة مضمونة أو رقمًا مدهشًا بلا سياق.</p>
<h2>المصادر</h2>
<p>الموضوعات العلمية والصحية والأمنية تُربط بمؤسسات معروفة أو وثائق أصلية. الوصفات تعتمد على خطوات مطبخية واضحة وتحذيرات سلامة غذائية عامة.</p>
<h2>اللغة</h2>
<p>عربية فصيحة مبسطة، فقرات قصيرة، جداول عند المقارنة. لا نكتب لملء الكلمات.</p>
<h2>التحديث</h2>
<p>تاريخ التعديل يتغير عند تصحيح جوهري أو توسعة حقيقية، لا عند ضبط شكلي فقط.</p>
<h2>الأدوات الرقمية</h2>
<p>يجوز استخدامها للبحث الأولي والتنظيم. الادعاء القابل للتحقق يمر على مصدر بشري ومراجعة قبل الاعتماد.</p>
<h2>الاستقلال</h2>
<p>الروابط الخارجية ليست إعلانًا. أي رعاية مستقبلية تُوسم.</p>
""",
    )
    replace_main(ROOT / "editorial-policy.html", editorial, "سياسة التحرير", "سياسة تحرير دليلك: اختيار الموضوع والمصادر والتصحيح واستخدام الأدوات الرقمية.")

    author = page_main(
        "فريق تحرير دليلك",
        "الاسم التحريري المسؤول عن النشر",
        """
<div class="transparency-box"><strong>بيان شفافية</strong><p>«فريق تحرير دليلك» اسم الجهة الناشرة وليس ادعاء اعتماد طبي أو أكاديمي. إن شارك مختص مستقبلاً سيُذكر اسمه وصفته.</p></div>
<h2>المسؤولية</h2>
<ol>
<li>تحديد سؤال القارئ.</li>
<li>جمع مصادر عند الحاجة.</li>
<li>صياغة عربية واضحة.</li>
<li>مراجعة الادعاءات القابلة للتحقق.</li>
<li>تصحيح الأخطاء الموثقة.</li>
</ol>
<h2>الخبرة العملية</h2>
<p>نكتب بوصفتنا محررين عامين للحياة اليومية: مطبخ منزلي، صيانة بيت، واستخدام تقني للمبتدئ. لا نقدّم استشارات فردية.</p>
<h2>التصحيح</h2>
<p>أرسل عبر <a href="../contact.html">اتصل بنا</a> رابط الصفحة والعبارة والمصدر. نراجع ونحدّث عند الحاجة.</p>
""",
    )
    replace_main(ROOT / "authors/editorial-team.html", author, "فريق تحرير دليلك", "الجهة التحريرية لموقع دليلك: المنهج وحدود الخبرة وطريقة التصحيح.")

    nf = read(ROOT / "404.html")
    nf = re.sub(
        r"<main id=\"main-content\">.*?</main>",
        """<main id="main-content"><div class="nf"><div class="big">404</div><h1>الصفحة غير موجودة</h1><p>ربما نُقل الرابط أو كُتب خطأ. استخدم البحث أو عد إلى الأقسام.</p><div class="cta-row" style="justify-content:center"><a class="btn btn-a" href="index.html">الصفحة الرئيسية</a><a class="btn btn-b" href="sitemap.html">خريطة الموقع</a></div></div></main>""",
        nf,
        count=1,
        flags=re.S,
    )
    write(ROOT / "404.html", nf)


def expand_guides() -> None:
    extra = (
        '<p class="guide-note">كل دليل مسار قراءة لا صفحة بديلة عن المقالات. ابدأ بالمشكلة الحالية، نفّذ قائمة تحقق واحدة، ثم انتقل للمقال التالي.</p>'
    )
    for name in (
        "guide-safe-cleaning.html",
        "guide-account-security.html",
        "guide-gulf-recipes.html",
        "guide-smartphone.html",
    ):
        path = ROOT / name
        text = read(path)
        if "guide-note" not in text:
            text = text.replace("</header><div class=\"guide-steps\">", "</header>" + extra + '<div class="guide-steps">')
        write(path, text)


def patch_tools() -> None:
    maintain = ROOT / "tools" / "maintain_site.py"
    t = read(maintain)
    t = t.replace("data[\"dateModified\"] = TODAY\n", "pass  # لا تُستبدل تواريخ المراجعة دفعة واحدة\n")
    t = t.replace('            data["email"] = "contact@dalilak.com"\n', "            data.pop('email', None)\n")
    t = t.replace(
        "def update_contact() -> None:\n    path = ROOT / \"contact.html\"\n    text = read(path)\n",
        "def update_contact() -> None:\n    if not (SITE_CONFIG.get('contact', {}).get('enabled') and SITE_CONFIG.get('email')):\n        return\n    path = ROOT / \"contact.html\"\n    text = read(path)\n",
    )
    if "gulf-rice-spices-guide" not in t.split("SOURCES")[1][:4000] if "SOURCES" in t else True:
        needle = '    "used-smartphone-checklist": [\n'
        insert = '''    "gulf-rice-spices-guide": [
        ("وزارة الزراعة الأمريكية — سلامة الطعام في المطبخ", "https://www.fsis.usda.gov/sites/default/files/media_file/2020-12/Kitchen-Companion.pdf"),
    ],
    "used-smartphone-checklist": [
'''
        if needle in t and "gulf-rice-spices-guide" not in t[t.find("SOURCES"):t.find("def read")]:
            t = t.replace(needle, insert, 1)
    write(maintain, t)

    audit = ROOT / "tools" / "content_quality_audit.py"
    a = read(audit)
    # عتبة الكلمات تبقى في أداة الفحص؛ لا تُرفع هنا حتى لا تُكسر الدفعة.
    write(audit, a)

    redesign = ROOT / "tools" / "redesign_magazine.py"
    r = read(redesign)
    r = r.replace("css/style.css?v=8", "css/style.css?v=10")
    r = r.replace("css/style.css?v=9", "css/style.css?v=10")
    if "dalilak/css/style.css" in r:
        r = r.replace("/dalilak/css/style.css?v=10", "css/style.css?v=10")
    write(redesign, r)

    phase = ROOT / "tools" / "phase_one_seo.py"
    p = read(phase)
    if "PROF-2026" not in p:
        p = p.replace(
            "def enhance_article(slug:str)->None:\n    path=ROOT/'posts'/f'{slug}.html';text=read(path)\n",
            "def enhance_article(slug:str)->None:\n    path=ROOT/'posts'/f'{slug}.html';text=read(path)\n    if 'PROF-2026' in text: return\n",
        )
        write(phase, p)

    pre = ROOT / "tools" / "pre_domain_content.py"
    pr = read(pre)
    if "PROF-2026" not in pr:
        pr = pr.replace(
            " for slug,body in FULL_BODY.items():\n  path=ROOT/'posts'/f'{slug}.html';text=read(path);",
            " for slug,body in FULL_BODY.items():\n  path=ROOT/'posts'/f'{slug}.html';text=read(path)\n  if 'PROF-2026' in text: continue\n  ",
        )
        write(pre, pr)


def update_search_titles() -> None:
    path = ROOT / "search-index.json"
    data = json.loads(read(path))
    for item in data:
        if item["s"] in BODIES:
            item["t"] = BODIES[item["s"]]["title"]
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def add_css() -> None:
    css = ROOT / "css" / "style.css"
    extra = """
.art-body h3{font-size:1.12rem;margin:22px 0 8px}
.guide-note{color:var(--muted);max-width:760px;margin:0 0 22px;font-size:1.02rem}
.page .box p{margin-bottom:8px}
"""
    text = read(css)
    if ".guide-note{" not in text:
        write(css, text + extra)


def update_sitemap_dates() -> None:
    path = ROOT / "sitemap.xml"
    text = read(path)
    text = re.sub(r"<lastmod>2026-08-17</lastmod>", f"<lastmod>{TODAY}</lastmod>", text)
    write(path, text)
    email = (CFG.get("email") or "").strip()
    contact_on = bool(CFG.get("contact", {}).get("enabled") and email)
    (ROOT / "humans.txt").write_text(
        "دليلك — مجلة عربية للمعرفة والحياة\n"
        "فريق التحرير: فريق تحرير دليلك\n"
        f"التواصل: {email if contact_on else 'صفحة اتصل بنا'}\n"
        "اللغة: العربية\n",
        encoding="utf-8",
    )
    contact_line = f"mailto:{email}" if contact_on else f"{BASE}/contact.html"
    (ROOT / "security.txt").write_text(
        f"Contact: {contact_line}\nPreferred-Languages: ar\nExpires: 2027-09-04\n",
        encoding="utf-8",
    )


def main() -> None:
    missing = [s for s in (p.stem for p in (ROOT / "posts").glob("*.html")) if s not in BODIES]
    if missing:
        raise SystemExit("مقالات بلا محتوى موسّع: " + ", ".join(missing))
    for slug, meta in BODIES.items():
        apply_article(slug, meta)
    update_static_pages()
    expand_guides()
    patch_tools()
    add_css()
    update_search_titles()
    global_html_fixes()
    subprocess.run([sys.executable, str(ROOT / "tools" / "redesign_magazine.py")], check=True)
    # redesign قد يعيد css؛ ثبّت المسارات والviewport بعد القالب
    global_html_fixes()
    update_sitemap_dates()
    # أعد بناء الفهرس الجانبي بعد القالب لأنه ينسخ toc
    for slug, meta in BODIES.items():
        path = ROOT / "posts" / f"{slug}.html"
        text = read(path)
        start = text.find('<div class="art-body">')
        end = text.find("</div>", start)
        # unreliable; use same ends
        apply_article(slug, meta)
    subprocess.run([sys.executable, str(ROOT / "tools" / "redesign_magazine.py")], check=True)
    global_html_fixes()
    print(f"وُسّع {len(BODIES)} مقالًا وحُدثت الصفحات الثابتة.")


if __name__ == "__main__":
    main()
