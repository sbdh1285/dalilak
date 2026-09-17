#!/usr/bin/env python3
"""إعادة بناء feed.xml (أحدث 20 مقالًا) من المقالات المنشورة فعليًا.

الاستخدام:
    python3 tools/refresh_feed.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from redesign_magazine import article_records  # noqa: E402

CONFIG = json.loads((ROOT / "site-config.json").read_text(encoding="utf-8"))
BASE = CONFIG["baseUrl"].rstrip("/")
LIMIT = 20


def pub_date(value: str) -> str:
    try:
        moment = datetime.fromisoformat(value[:10])
    except ValueError:
        moment = datetime.now(timezone.utc).replace(tzinfo=None)
    return format_datetime(moment.replace(tzinfo=timezone.utc))


def main() -> None:
    records = article_records()
    ordered = sorted(records.items(), key=lambda item: item[1]["published"], reverse=True)[:LIMIT]
    items = []
    for slug, article in ordered:
        items.append(
            "<item><title>{title}</title><link>{base}/posts/{slug}.html</link>"
            "<guid>{base}/posts/{slug}.html</guid><pubDate>{pub}</pubDate>"
            "<description>{desc}</description></item>".format(
                title=escape(article["title"]),
                base=BASE,
                slug=slug,
                pub=pub_date(article["published"]),
                desc=escape(article["description"]),
            )
        )
    feed = (
        '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>'
        "<title>دليلك</title><link>{base}</link>"
        "<description>أحدث مقالات دليلك</description><language>ar</language>{items}"
        "</channel></rss>"
    ).format(base=BASE, items="".join(items))
    (ROOT / "feed.xml").write_text(feed, encoding="utf-8")
    print(f"تم تحديث feed.xml: {len(items)} مقالًا من أصل {len(records)}.")
    print("الأحدث:", ", ".join(slug for slug, _ in ordered[:7]))


if __name__ == "__main__":
    main()
