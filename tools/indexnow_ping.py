#!/usr/bin/env python3
"""إشعار فوري لمحركات البحث (Bing وYandex وSeznam) عبر بروتوكول IndexNow.

يجمع الروابط المطلوب إشعارها بأحد الأوضاع التالية ثم يرسلها إلى
النقطة الموحّدة https://api.indexnow.org/IndexNow التي توجّه الطلب
إلى كل المحركات المشاركة في البروتوكول:

    --url URL          رابط صريح (يمكن تكراره لأكثر من رابط).
    --git-before SHA   الملفات HTML التي تغيّرت بين SHA وHEAD (وضع الدفع).
    --feed-top N       أحدث N مقالات من feed.xml (وضع احتياطي).
    --sitemap          كل روابط sitemap.xml (وضع الإشعار الكامل الدوري).

إن لم تُنتج الأوضاع الأخرى روابط، يتحوّل السكربت تلقائيًا إلى أحدث
المقالات من feed.xml حتى لا يمر دفع بلا إشعار.

مفتاح IndexNow يُقرأ من الملف <المفتاح>.txt في جذر المستودع (نفس
الملف المنشور عبر GitHub Pages)، ورابط الموقع من site-config.json.

الاستخدام:
    python3 tools/indexnow_ping.py --git-before <sha>      # بعد كل دفع
    python3 tools/indexnow_ping.py --url https://...       # رابط واحد
    python3 tools/indexnow_ping.py --sitemap               # إشعار كامل
    python3 tools/indexnow_ping.py --feed-top 10 --dry-run # تجربة بلا إرسال
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "site-config.json").read_text(encoding="utf-8"))
BASE_URL = CONFIG["baseUrl"].rstrip("/")
HOST = urlparse(BASE_URL).netloc
INDEXNOW_ENDPOINT = "https://api.indexnow.org/IndexNow"
USER_AGENT = "dalilak-indexnow/1.0 (+https://api.indexnow.org)"
MAX_URLS_PER_REQUEST = 10_000  # الحد الأقصى في بروتوكول IndexNow
FALLBACK_FEED_COUNT = 10

# صفحات لا ينبغي إشعار المحركات بها (noindex أو غير مقصودة للفهرسة)
NOINDEX_PAGES = {"404.html", "search.html", "thanks.html"}
SKIP_PATTERNS = (re.compile(r"^google[0-9a-f]+\.html$"),)  # ملفات توثيق Google Search Console


def discover_key() -> str:
    """يبحث عن ملف المفتاح <32-رمزًا سداسيًا>.txt في جذر المستودع."""
    for candidate in sorted(ROOT.glob("*.txt")):
        if re.fullmatch(r"[0-9a-f]{32}", candidate.stem):
            key = candidate.read_text(encoding="utf-8").strip()
            if key == candidate.stem:
                return key
    sys.exit("✗ لم يُعثر على ملف مفتاح IndexNow في جذر المستودع.")


def key_location(key: str) -> str:
    """المسار المنشور لملف المفتاح (BASE_URL يشمل مجلد المشروع في GitHub Pages)."""
    return f"{BASE_URL}/{key}.txt"


def changed_html(before: str) -> list[str]:
    """ملفات HTML المضافة أو المعدّلة بين SHA وHEAD (مقارنًا بجذر المستودع)."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMRT", before, "HEAD", "--", "*.html"],
        capture_output=True, text=True, check=True, cwd=ROOT,
    )
    pages = []
    for line in result.stdout.splitlines():
        page = line.strip().replace("\\", "/")
        if not page:
            continue
        if page in NOINDEX_PAGES or any(pattern.fullmatch(page) for pattern in SKIP_PATTERNS):
            continue
        path = ROOT / page
        if not path.is_file() or "noindex" in path.read_text(encoding="utf-8", errors="ignore")[:4096]:
            continue
        pages.append(page)
    return pages


def page_to_url(page: str) -> str:
    if page == "index.html":
        return f"{BASE_URL}/"
    return f"{BASE_URL}/{page}"


def feed_urls(count: int) -> list[str]:
    """أحدث الروابط من feed.xml."""
    items = ElementTree.fromstring((ROOT / "feed.xml").read_bytes()).findall("channel/item/link")
    return [item.text.strip() for item in items if item.text and item.text.strip()][:count]


def sitemap_urls() -> list[str]:
    """كل الروابط من sitemap.xml بأي مساحة أسماء."""
    root = ElementTree.fromstring((ROOT / "sitemap.xml").read_bytes())
    return [element.text.strip() for element in root.iter() if element.tag.endswith("loc") and element.text]


def validate(url: str) -> str:
    if not url.startswith(BASE_URL + "/") and url != BASE_URL:
        sys.exit(f"✗ الرابط خارج نطاق الموقع ({BASE_URL}): {url}")
    return url


def submit(urls: list[str], key: str, dry_run: bool) -> int:
    """يرسل الروابط إلى IndexNow. يعيد رمز الخروج (0 نجاح)."""
    seen: dict[str, None] = {}
    for url in urls:
        seen.setdefault(validate(url), None)
    urls = list(seen)[:MAX_URLS_PER_REQUEST]
    if len(seen) > MAX_URLS_PER_REQUEST:
        print(f"⚠ تجاوز الحد {MAX_URLS_PER_REQUEST} رابطًا؛ سيُرسل الأول منها فقط.")

    if not urls:
        return 0

    payload = {
        "host": HOST,
        "key": key,
        "keyLocation": key_location(key),
        "urlList": urls,
    }
    print(f"• المضيف: {HOST}")
    print(f"• ملف المفتاح: {payload['keyLocation']}")
    print(f"• عدد الروابط: {len(urls)}")
    for url in urls:
        print(f"  - {url}")

    if dry_run:
        print("• وضع التجربة: لم يُرسل شيء.")
        return 0

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        INDEXNOW_ENDPOINT,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": USER_AGENT},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            print(f"✓ استجابة {response.status}: أُبلغت المحركات المشاركة (Bing وYandex وSeznam) بالروابط.")
            print("✅ تم الإشعار بنجاح.")
            return 0
    except urllib.error.HTTPError as error:
        explanation = {
            400: "طلب غير صالح — راجع صيغة الحمولة.",
            403: "المفتاح غير صالح أو ملفه غير متاح على الموقع (keyLocation).",
            422: "الروابط لا تطابق المفتاح أو المضيف المُرسَل.",
            429: "تجاوز الحد المسموح من الطلبات — أعد المحاولة لاحقًا.",
        }[error.code] if error.code in (400, 403, 422, 429) else error.reason
        if error.code == 429:
            print(f"⚠ استجابة {error.code}: {explanation} — ليست مشكلة إعداد؛ سيتعامل معها التحديث التالي.")
            return 0
        print(f"✗ استجابة {error.code}: {explanation}", file=sys.stderr)
        return 1
    except urllib.error.URLError as error:
        print(f"✗ تعذّر الوصول إلى {INDEXNOW_ENDPOINT}: {error.reason}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="إشعار فوري عبر IndexNow")
    parser.add_argument("--url", action="append", default=[], help="رابط صريح (يمكن تكراره)")
    parser.add_argument("--git-before", metavar="SHA", help="أشعِر بالملفات HTML المتغيرة بين SHA وHEAD")
    parser.add_argument("--feed-top", type=int, metavar="N", help="أشعِر بأحدث N مقالات من feed.xml")
    parser.add_argument("--sitemap", action="store_true", help="أشعِر بكل روابط sitemap.xml")
    parser.add_argument("--dry-run", action="store_true", help="اعرض الروابط دون إرسال")
    args = parser.parse_args()

    key = discover_key()
    urls: list[str] = []

    if args.url:
        urls += args.url
    if args.git_before:
        urls += [page_to_url(page) for page in changed_html(args.git_before)]
    if args.sitemap:
        urls += sitemap_urls()
    if args.feed_top:
        urls += feed_urls(args.feed_top)

    # الوضع الاحتياطي: دفع بلا روابط → أحدث المقالات من feed.xml
    if not urls and not any([args.url, args.sitemap, args.feed_top]):
        print("• لا تغييرات HTML في هذا الدفع؛ الإشعار بأحدث المقالات من feed.xml.")
        urls = feed_urls(FALLBACK_FEED_COUNT)

    if not urls:
        print("• لا روابط للإشعار. انتهى.")
        return 0

    return submit(urls, key, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
