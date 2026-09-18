#!/usr/bin/env python3
"""المرحلة الثانية من تحسين SEO لموقع دليلك.

تنفّذ دفعة تحسينات منهجية قابلة للتكرار (idempotent):
1. حقن مخطط FAQPage (JSON-LD) في كل مقال يملك قسم «أسئلة شائعة» مرئيًا.
2. إضافة رابط RSS البديل (rel=alternate) إلى ترويسة كل الصفحات.
3. ترقية وسم robots إلى max-image-preview:large لدعم الظهور في «اكتشف» وصور البحث.
4. حقن مخطط ItemList في صفحات الأقسام الأربعة.
5. إعادة بناء sitemap.xml بالكامل مع مساحة أسماء الصور وتواريخ lastmod محدّثة
   للمقالات التي تغيّرت فعليًا.

التشغيل: python3 tools/seo_phase_two.py
"""
from __future__ import annotations

import html as html_lib
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_CONFIG = json.loads((ROOT / "site-config.json").read_text(encoding="utf-8"))
BASE = SITE_CONFIG.get("baseUrl", "https://sbdh1285.github.io/dalilak").rstrip("/")
TODAY = date.today().isoformat()
SITE_NAME = SITE_CONFIG.get("siteName", "دليلك")

HTML_GLOBS = [p for p in ROOT.rglob("*.html") if "node_modules" not in p.parts and "qa" not in p.parts]

CATEGORY_PAGES = {
    "home-tips": "نصائح منزلية",
    "recipes": "وصفات لذيذة",
    "knowledge": "معلومات عامة",
    "tech": "تكنولوجيا",
}

# صفحات لا تُفهرس/لا تدخل السايت ماب.
EXCLUDE_FROM_SITEMAP = {"search.html", "404.html", "thanks.html"}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def strip_tags(value: str) -> str:
    value = re.sub(r"<script.*?</script>", " ", value, flags=re.S)
    value = re.sub(r"<style.*?</style>", " ", value, flags=re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    value = html_lib.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def article_meta(path: Path) -> dict:
    text = read(path)
    slug = path.stem
    title_m = re.search(r"<title>(.*?)\s*\|\s*دليلك</title>", text)
    desc_m = re.search(r'<meta name="description" content="([^"]+)"', text)
    pub_m = re.search(r'"datePublished":"([^"]+)"', text)
    mod_m = re.search(r'"dateModified":"([^"]+)"', text)
    cat_m = re.search(r'<span class="cat-chip">([^<]+)</span>', text) or re.search(
        r'"articleSection":"([^"]+)"', text)
    og_m = re.search(r'<meta property="og:image" content="([^"]+)"', text)
    return {
        "slug": slug,
        "title": strip_tags(title_m.group(1)) if title_m else slug,
        "description": desc_m.group(1) if desc_m else "",
        "published": pub_m.group(1) if pub_m else "2026-07-01",
        "modified": mod_m.group(1) if mod_m else (pub_m.group(1) if pub_m else "2026-07-01"),
        "category": strip_tags(cat_m.group(1)) if cat_m else "",
        "image": og_m.group(1) if og_m else "",
    }


def extract_faq_pairs(text: str) -> list[tuple[str, str]]:
    """استخراج أسئلة وأجوبة قسم «أسئلة شائعة» المرئي (h2 متبوعًا بأزواج h3/p)."""
    m = re.search(r'<h2[^>]*>\s*أسئلة شائعة\s*</h2>(.*?)(?=<h2|</div>\s*</article>|<section class="cluster-links"|$)',
                  text, flags=re.S)
    if not m:
        return []
    region = m.group(1)
    pairs = []
    for q, a in re.findall(r"<h3[^>]*>(.*?)</h3>\s*<p>(.*?)</p>", region, flags=re.S):
        question = strip_tags(q)
        answer = strip_tags(a)
        if question and answer and len(answer) >= 10:
            pairs.append((question, answer))
    return pairs


FAQ_BLOCK = re.compile(r'\s*<script type="application/ld\+json">\{"@context":"https://schema\.org","@type":"FAQPage".*?</script>', re.S)


def add_faq_schema() -> int:
    """حقن/تحديث مخطط FAQPage ليطابق قسم «أسئلة شائعة» المرئي الحالي في كل مقال."""
    count = 0
    for path in sorted((ROOT / "posts").glob("*.html")):
        text = read(path)
        text = FAQ_BLOCK.sub("", text)
        pairs = extract_faq_pairs(text)
        if not pairs:
            write(path, text)
            continue
        data = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a},
                }
                for q, a in pairs
            ],
        }
        script = '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "</script>"
        text = text.replace("</body>", script + "\n</body>", 1)
        write(path, text)
        count += 1
    return count


def add_rss_alternate() -> int:
    count = 0
    link = f'<link rel="alternate" type="application/rss+xml" title="{SITE_NAME} — آخر المقالات" href="{BASE}/feed.xml">'
    for path in HTML_GLOBS:
        if path.parent.name == "posts" or path.name in {"404.html"}:
            target_head = True
        else:
            target_head = True
        if not target_head:
            continue
        text = read(path)
        if 'rel="alternate" type="application/rss+xml"' in text:
            continue
        if path.name == "feed.xml":
            continue
        text = text.replace("</head>", link + "\n</head>", 1)
        write(path, text)
        count += 1
    return count


def upgrade_robots_meta() -> int:
    count = 0
    for path in HTML_GLOBS:
        text = read(path)
        new = text.replace(
            '<meta name="robots" content="index, follow">',
            '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">',
        )
        if new != text:
            write(path, new)
            count += 1
    return count


def add_category_itemlists() -> int:
    posts = sorted((ROOT / "posts").glob("*.html"))
    metas = [article_meta(p) for p in posts]
    count = 0
    for slug, cat_name in CATEGORY_PAGES.items():
        path = ROOT / "category" / f"{slug}.html"
        if not path.exists():
            continue
        text = read(path)
        if '"ItemList"' in text:
            continue
        items = [m for m in metas if m["category"] == cat_name]
        items.sort(key=lambda m: (m["published"], m["slug"]), reverse=True)
        if not items:
            continue
        data = {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": f"{cat_name} — {SITE_NAME}",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "url": f"{BASE}/posts/{m['slug']}.html",
                    "name": m["title"],
                }
                for i, m in enumerate(items)
            ],
        }
        script = '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "</script>"
        text = text.replace("</body>", script + "\n</body>", 1)
        write(path, text)
        count += 1
    return count


def rebuild_sitemap(changed_slugs: set[str]) -> int:
    """إعادة بناء sitemap.xml كاملًا مع امتداد الصور وتحديث lastmod للمقالات المعدّلة."""
    entries: list[tuple[str, str, str, str, list[str]]] = []  # loc, lastmod, changefreq, priority, images

    def add(loc: str, lastmod: str, changefreq: str, priority: str, images: list[str] | None = None) -> None:
        entries.append((loc, lastmod, changefreq, priority, images or []))

    add(f"{BASE}/", TODAY, "weekly", "1.0")

    metas = [article_meta(p) for p in (ROOT / "posts").glob("*.html")]
    metas.sort(key=lambda m: (m["published"], m["slug"]), reverse=True)
    for m in metas:
        lastmod = TODAY if m["slug"] in changed_slugs else m["modified"]
        img = m["image"] if m["image"].startswith(BASE) else ""
        add(f"{BASE}/posts/{m['slug']}.html", lastmod, "monthly", "0.8", [img] if img else [])

    for slug in CATEGORY_PAGES:
        add(f"{BASE}/category/{slug}.html", TODAY, "weekly", "0.7")

    for guide in sorted(ROOT.glob("guide-*.html")):
        add(f"{BASE}/{guide.name}", guide.name and "2026-09-04", "monthly", "0.7")

    info_pages = ["about.html", "contact.html", "privacy-policy.html", "terms.html",
                  "disclaimer.html", "editorial-policy.html", "sitemap.html",
                  "authors/editorial-team.html"]
    for name in info_pages:
        if (ROOT / name).exists():
            lm = TODAY if name in {"editorial-policy.html", "authors/editorial-team.html"} else "2026-09-04"
            add(f"{BASE}/{name}", lm, "monthly", "0.6")

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
             '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    for loc, lastmod, changefreq, priority, images in entries:
        lines.append("  <url>")
        lines.append(f"    <loc>{html_lib.escape(loc)}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <changefreq>{changefreq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        for img in images:
            lines.append("    <image:image>")
            lines.append(f"      <image:loc>{html_lib.escape(img)}</image:loc>")
            lines.append("    </image:image>")
        lines.append("  </url>")
    lines.append("</urlset>")
    write(ROOT / "sitemap.xml", "\n".join(lines) + "\n")
    return len(entries)


def changed_today() -> set[str]:
    """المقالات المعدّلة اليوم (حسب الطابع الزمني لنظام الملفات)."""
    import time
    today_start = time.mktime(time.strptime(TODAY, "%Y-%m-%d"))
    changed: set[str] = set()
    for p in (ROOT / "posts").glob("*.html"):
        if p.stat().st_mtime >= today_start:
            changed.add(p.stem)
    return changed


def main() -> None:
    faq = add_faq_schema()
    rss = add_rss_alternate()
    robots = upgrade_robots_meta()
    itemlists = add_category_itemlists()
    sitemap_urls = rebuild_sitemap(changed_today())
    print(json.dumps({
        "faq_schema_injected": faq,
        "rss_alternate_added": rss,
        "robots_upgraded": robots,
        "category_itemlists": itemlists,
        "sitemap_urls": sitemap_urls,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
