#!/usr/bin/env python3
# تحسينات ما قبل أدسنس: اسم الكاتب + تاريخ التحديث لكل مقال، استبدال عبارة "100%"، مراجعة الصور.
import os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
def read(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()
def write(p, t): open(os.path.join(ROOT, p), "w", encoding="utf-8").write(t)

AUTHOR = "فريق تحرير دليلك"
UPDATE = "16 أغسطس 2026"
UPDATED_ISO = "2026-08-16"

# 1) استبدال العبارة المبالغ فيها في كل الصفحات
total_phrase = 0
for dp, _, fns in os.walk(ROOT):
    if any(s in dp for s in ["/content", ".git"]): continue
    for fn in fns:
        if not fn.endswith(".html"): continue
        p = os.path.join(dp, fn)
        t = read(p)
        if "محتوى أصلي 100%" in t:
            t = t.replace("محتوى أصلي 100%", "محتوى عربي يُكتب ويُراجع بعناية")
            write(p, t)
            total_phrase += 1
print("استبدال العبارة في ملفات:", total_phrase)

# 2) إضافة اسم الكاتب + تاريخ التحديث + مراجعة الصور لكل مقال
added = 0
imgs_fixed = 0
for fn in sorted(os.listdir(os.path.join(ROOT, "posts"))):
    if not fn.endswith(".html"): continue
    p = os.path.join("posts", fn)
    t = read(p)
    slug = fn[:-5]
    title = re.search(r"<title>(.*?)</title>", t, re.S)
    title = title.group(1).replace(" | دليلك", "").strip() if title else slug
    changed = False

    # إضافة الكاتب وتاريخ التحديث داخل art-meta
    if "آخر تحديث" not in t:
        m = re.search(r'(<div class="art-meta">.*?</div>)', t, re.S)
        if m:
            block = m.group(1)
            new = block[:-6] + f'  <span>✍️ {AUTHOR}</span>\n  <span>🔄 آخر تحديث: {UPDATE}</span>\n</div>'
            t = t[:m.start()] + new + t[m.end():]
            changed = True

    # ضبط alt للصورة الرئيسية إن كانت فارغة/مفقودة
    def fix_alt(mm):
        tag = mm.group(0)
        if re.search(r'alt="[^"]+"', tag):
            return tag
        return tag[:-2] + f' alt="{title}">'
    new_t, n = re.subn(r'<img class="art-img"[^>]*?(?:>)', fix_alt, t)
    if n:
        t = new_t
        imgs_fixed += n
        changed = True

    if changed:
        write(p, t)
        added += 1
print("مقالات عُدّلت (كاتب/تحديث/صور):", added)
print("صور مُصلِح alt لها:", imgs_fixed)
print("DONE")
