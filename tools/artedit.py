#!/usr/bin/env python3
"""مساعد تحرير آمن لمقالات دليلك: استبدال جسم المقال، ومواءمة جدول المحتويات
ومدة القراءة دون إعادة توليد الصفحة الرئيسية (index.html التحريرية).

الاستخدام من داخل سكربتات:
    from artedit import read_art_body, replace_art_body, sync_toc, art_meta_span
"""
from __future__ import annotations
import re, html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "posts"

ARABIC_READING_WORDS_PER_MINUTE = 143


def count_readable_words(fragment: str) -> int:
    fragment = re.sub(r"<!--.*?-->", " ", fragment, flags=re.S)
    visible = re.sub(r"<[^>]+>", " ", fragment)
    return len(re.findall(r"[\w\u0600-\u06FF]+", html.unescape(visible), re.UNICODE))


def reading_minutes(fragment: str) -> int:
    import math
    words = count_readable_words(fragment)
    return max(2, math.floor(words / ARABIC_READING_WORDS_PER_MINUTE + 0.5))


def reading_label(minutes: int) -> str:
    if minutes == 1:
        return "دقيقة واحدة"
    if minutes == 2:
        return "دقيقتان"
    if 3 <= minutes <= 10:
        return f"{minutes} دقائق"
    return f"{minutes} دقيقة"


def balanced_close(text: str, open_idx: int) -> int:
    """أوجد إغلاق div متوازنًا يبدأ بـ <div ...> عند open_idx."""
    depth = 0
    for m in re.finditer(r"<div\b[^>]*>|</div>", text[open_idx:]):
        tag = m.group(0)
        if tag.startswith("</"):
            depth -= 1
            if depth == 0:
                return open_idx + m.end()
        else:
            depth += 1
    return -1


def art_body_span(text: str):
    i = text.find('<div class="art-body">')
    if i < 0:
        return None
    j = balanced_close(text, i)
    return i, j


def read_art_body(slug: str) -> str:
    text = (POSTS / f"{slug}.html").read_text(encoding="utf-8")
    span = art_body_span(text)
    if not span:
        raise SystemExit(f"no art-body in {slug}")
    i, j = span
    return text[i:j]


def replace_art_body(slug: str, new_inner: str) -> None:
    """استبدل محتوى art-body بالكامل (يفتح ويغلق div)."""
    path = POSTS / f"{slug}.html"
    text = path.read_text(encoding="utf-8")
    i, j = art_body_span(text)
    text = text[:i] + '<div class="art-body">' + new_inner + "</div>" + text[j:]
    path.write_text(text, encoding="utf-8")


def h2_items(text: str):
    """استخرج (id, نص) لكل h2 داخل جسم المقال."""
    items = []
    for m in re.finditer(r"<h2(?:\s+id=\"([^\"]+)\")?[^>]*>(.*?)</h2>", text, flags=re.S):
        ident, body = m.group(1), m.group(2)
        if not ident:
            continue
        txt = re.sub(r"<[^>]+>", "", body)
        txt = re.sub(r"\s+", " ", html.unescape(txt)).strip()
        items.append((ident, txt))
    return items


def sync_toc(slug: str) -> None:
    """أعد بناء قائمتي <ul> داخل وسوم nav.toc من h2 الحالي في الجسم."""
    path = POSTS / f"{slug}.html"
    text = path.read_text(encoding="utf-8")
    i, j = art_body_span(text)
    items = h2_items(text[i:j])
    if not items:
        return
    lis = "".join(
        f'<li><a href="#{ident}">{txt}</a></li>' for ident, txt in items
    )
    def repl(match: re.Match) -> str:
        head = re.sub(r"<ul>.*?</ul>", f"<ul>{lis}</ul>", match.group(0), count=1, flags=re.S)
        return head
    text = re.sub(
        r'<nav class="toc"[^>]*>.*?</nav>', repl, text, count=0, flags=re.S
    )
    path.write_text(text, encoding="utf-8")


def set_art_meta_minutes(slug: str) -> None:
    """حدّث وسم «X قراءة» داخل art-meta من طول الجسم الفعلي."""
    path = POSTS / f"{slug}.html"
    text = path.read_text(encoding="utf-8")
    i, j = art_body_span(text)
    minutes = reading_minutes(text[i:j])
    label = reading_label(minutes)
    pattern = r'(<div class="art-meta">.*?<span>)[^<]*( قراءة)(</span></div>)'
    if re.search(pattern, text, flags=re.S):
        text = re.sub(pattern, rf"\g<1>{label}\g<2>\g<3>", text, count=1, flags=re.S)
    path.write_text(text, encoding="utf-8")


def body_word_count(slug: str) -> int:
    text = (POSTS / f"{slug}.html").read_text(encoding="utf-8")
    i, j = art_body_span(text)
    return count_readable_words(text[i:j])
