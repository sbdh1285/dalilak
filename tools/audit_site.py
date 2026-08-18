#!/usr/bin/env python3
"""فحص اتساق موقع دليلك؛ يعيد رمز خروج غير صفري عند وجود مشكلة."""
from __future__ import annotations
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

class Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []
        self.h1 = 0
        self.title = ""
        self._in_title = False
        self.images: list[dict[str, str]] = []
        self.ids: list[str] = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag in {"a", "link", "script", "img", "form"}:
            value = data.get("href") or data.get("src")
            if value:
                self.refs.append(value)
        if tag == "source" and data.get("srcset"):
            self.refs.extend(item.strip().split()[0] for item in data["srcset"].split(",") if item.strip())
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self._in_title = True
        if tag == "img":
            self.images.append(data)
        if "id" in data:
            self.ids.append(data["id"])

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data

html_files = sorted(path for path in ROOT.rglob("*.html") if "node_modules" not in path.parts and "qa" not in path.parts)
for path in html_files:
    text = path.read_text(encoding="utf-8")
    parser = Parser()
    parser.feed(text)
    rel = path.relative_to(ROOT)
    if parser.h1 != 1:
        errors.append(f"{rel}: عدد H1 هو {parser.h1}")
    if not parser.title.strip():
        errors.append(f"{rel}: title مفقود")
    if len(parser.ids) != len(set(parser.ids)):
        errors.append(f"{rel}: توجد IDs مكررة")
    if "<h>" in text or "</h>" in text:
        errors.append(f"{rel}: وسم h غير صالح")
    if "tajawal-00.woff2" in text:
        errors.append(f"{rel}: رابط خط مكسور")
    if "localStorage.getItem('theme')" in text:
        errors.append(f"{rel}: كود مشترك ما زال مضمّنًا")
    if "js/main.js" not in text:
        errors.append(f"{rel}: main.js غير مربوط")
    for image in parser.images:
        if "alt" not in image:
            errors.append(f"{rel}: صورة بلا alt: {image.get('src', '')}")
    for ref in parser.refs:
        if ref.startswith(("#", "mailto:", "tel:", "javascript:", "data:", "http://", "https://")):
            continue
        clean = unquote(ref.split("#")[0].split("?")[0])
        if not clean:
            continue
        if clean.startswith("/dalilak/"):
            target = ROOT / clean.removeprefix("/dalilak/")
        elif clean.startswith("/"):
            target = ROOT / clean.lstrip("/")
        else:
            target = path.parent / clean
        if not target.exists():
            errors.append(f"{rel}: مرجع مكسور {ref}")
    for index, raw in enumerate(re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S), 1):
        try:
            json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{rel}: JSON-LD رقم {index} غير صالح: {exc}")

search = json.loads((ROOT / "search-index.json").read_text(encoding="utf-8"))
posts = list((ROOT / "posts").glob("*.html"))
if len(search) != len(posts):
    errors.append(f"فهرس البحث يحتوي {len(search)} عنصرًا بينما عدد المقالات {len(posts)}")
if len({item["s"] for item in search}) != len(search):
    errors.append("فهرس البحث يحتوي slugs مكررة")
category_counts = {category: sum(item["c"] == category for item in search) for category in {item["c"] for item in search}}
expected = {}
for post in posts:
    article = None
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', post.read_text(encoding="utf-8"), re.S):
        data = json.loads(raw)
        if data.get("@type") == "Article": article = data; break
    if article: expected[article["articleSection"]] = expected.get(article["articleSection"], 0) + 1
if category_counts != expected:
    errors.append(f"توزيع التصنيفات غير صحيح: {category_counts} والمتوقع {expected}")

manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
site_config = json.loads((ROOT / "site-config.json").read_text(encoding="utf-8")) if (ROOT / "site-config.json").exists() else {}
expected_base_path = "/" if site_config.get("customDomain") else "/dalilak/"
if manifest.get("start_url") != expected_base_path or manifest.get("scope") != expected_base_path:
    errors.append("إعداد manifest لمسار النشر غير صحيح")

posts = list((ROOT / "posts").glob("*.html"))
source_count = sum('class="sources"' in p.read_text(encoding="utf-8") for p in posts)
if source_count < 18:
    errors.append(f"عدد المقالات التي تحمل مصادر منخفض: {source_count}")

if errors:
    print("فشل الفحص:")
    for error in errors:
        print("-", error)
    sys.exit(1)

print(f"نجح الفحص: {len(html_files)} صفحة، {len(posts)} مقالًا، {source_count} مقالًا موثقًا بالمصادر.")
print("توزيع فهرس البحث:", category_counts)
