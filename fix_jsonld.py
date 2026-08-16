#!/usr/bin/env python3
# تصحيح تواريخ JSON-LD (datePublished/dateModified) لكل المقالات من تاريخ النشر الفعلي.
import os, re
for fn in sorted(os.listdir("posts")):
    if not fn.endswith(".html"):
        continue
    p = os.path.join("posts", fn)
    t = open(p, encoding="utf-8").read()
    dm = re.search(r"نُشر: (\d{4}-\d{2}-\d{2})", t)
    date = dm.group(1) if dm else "2026-08-01"
    t = re.sub(r'"datePublished":\s*"[^"]*"', f'"datePublished": "{date}"', t)
    t = re.sub(r'"dateModified":\s*"[^"]*"', '"dateModified": "2026-08-16"', t)
    open(p, "w", encoding="utf-8").write(t)
print("تم تصحيح تواريخ JSON-LD")
