#!/usr/bin/env python3
"""إبلاغ قوقل فورًا بالصفحات الجديدة/المعدّلة عبر Google Indexing API.

الاستعداد لمرة واحدة (5 دقائق، مجاني):
1. افتح console.cloud.google.com وأنشئ مشروعًا جديدًا.
2. من "APIs & Services" فعّل خدمة «Web Search Indexing API».
3. أنشئ Service Account وحمّل مفتاحه بصيغة JSON.
4. في Search Console: الإعدادات ← المستخدمون والأذونات ← أضف بريد الـService
   Account (المنتهي بـ iam.gserviceaccount.com) بصلاحية «مالك».

التشغيل:
    pip install google-auth requests
    python3 tools/indexing_api_ping.py path/to/key.json               # كل روابط السايت ماب
    python3 tools/indexing_api_ping.py path/to/key.json --url رابط   # رابط واحد
    python3 tools/indexing_api_ping.py path/to/key.json --removed     # إبلاغ عن حذف

ملاحظة: الوجهة صُممت رسميًا لصفحات JobPosting والبث، واستخدامها لصفحات أخرى
شائع بين ممارسي SEO؛ تجاهل قوقل لها في أسوأ الأحوال لا يضر الموقع.
الحصة الافتراضية: 200 إبلاغ يوميًا.
"""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"


def sitemap_urls() -> list[str]:
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    tree = ET.parse(ROOT / "sitemap.xml")
    locs = [el.text for el in tree.getroot().findall(".//s:loc", ns)]
    return [u for u in locs if u and "/posts/" in u or (u and u.rstrip("/").endswith("dalilak"))]


def get_token(key_path: Path) -> str:
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
    except ImportError:
        sys.exit("ثبّت المتطلبات أولًا:  pip install google-auth requests")
    creds = service_account.Credentials.from_service_account_file(
        str(key_path), scopes=["https://www.googleapis.com/auth/indexing"]
    )
    creds.refresh(Request())
    return creds.token


def publish(token: str, url: str, notification: str) -> None:
    import requests
    resp = requests.post(
        ENDPOINT,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"url": url, "type": notification},
        timeout=30,
    )
    body = resp.json() if resp.text else {}
    if resp.status_code == 200:
        print(f"✓ {url}")
    else:
        print(f"✗ {url} — HTTP {resp.status_code}: {json.dumps(body, ensure_ascii=False)[:200]}")


def main() -> None:
    parser = argparse.ArgumentParser(description="إبلاغ Indexing API بروابط الموقع")
    parser.add_argument("key", type=Path, help="مسار ملف مفتاح Service Account (JSON)")
    parser.add_argument("--url", help="إبلاغ رابط واحد بدل كل السايت ماب")
    parser.add_argument("--removed", action="store_true", help="إبلاغ URL_DELETED بدل URL_UPDATED")
    args = parser.parse_args()

    urls = [args.url] if args.url else sitemap_urls()
    notification = "URL_DELETED" if args.removed else "URL_UPDATED"
    print(f"سيتم إبلاغ قوقل بـ {len(urls)} رابطًا ({notification})")
    token = get_token(args.key)
    for url in urls:
        publish(token, url, notification)
    print("انتهى. تابع الحالة من Search Console ← تغطية الفهرس خلال الساعات القادمة.")


if __name__ == "__main__":
    main()
