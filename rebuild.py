#!/usr/bin/env python3
# إعادة بناء المقالات من النسخة الأصلية السليمة + تطبيق آمن للتحسينات (دون لمس الأرقام).
import os, re, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
logs = subprocess.check_output(["git", "log", "--reverse", "--format=%H %s"]).decode().splitlines()
first_mine = [l.split(" ", 1)[0] for l in logs if ("فهرس بحث" in l or "تحسينات dalilak" in l or "improve" in l)][0]
parent = subprocess.check_output(["git", "rev-parse", first_mine + "^"]).decode().strip()

UPDATE = "16 أغسطس 2026"
AUTHOR = "فريق تحرير دليلك"

# استخرج قسم التوسيع السليم من الملفات الحالية (آخر H2 قبل المشاركة فقط)
EXTRA = {}
for fn in sorted(os.listdir(os.path.join(ROOT, "posts"))):
    if not fn.endswith(".html"):
        continue
    t = open(os.path.join("posts", fn), encoding="utf-8").read()
    m = re.search(r'(<h2>(?:(?!<h2>).)*?)<div class="share"', t, re.S)
    if m:
        EXTRA[fn[:-5]] = m.group(1).strip()

n = 0
for fn in sorted(os.listdir(os.path.join(ROOT, "posts"))):
    if not fn.endswith(".html"):
        continue
    slug = fn[:-5]
    # النسخة الأصلية السليمة
    t = subprocess.check_output(["git", "show", parent + ":posts/" + fn]).decode()
    # تنظيف محدِّدات التنوع اللوني + النطاق
    t = t.replace("\ufe0f", "")
    t = t.replace("sbdh285.github.io", "sbdh1285.github.io")
    # تحويل رموز الميتا إلى نصوص (دون مسّ الأرقام/التواريخ)
    t = t.replace("📅 ", "نُشر: ")
    t = re.sub(r"⏱️ (\d+) دقائق قراءة", r"مدة القراءة: \1 دقائق", t)
    t = t.replace("✍️ ", "الكاتب: ").replace("🔄 ", "").replace("🗂️ ", "")
    t = t.replace("<h>", "<h1>").replace("</h>", "</h1>")
    # إضافة تاريخ التحديث داخل الميتا
    t = re.sub(r"</div>\s*<div class=\"art-body\">",
               '  <span>آخر تحديث: ' + UPDATE + r'</span>\n</div>\n<div class="art-body">', t, count=1)
    # إدراج قسم التوسيع الأصلي قبل المشاركة
    if slug in EXTRA:
        t = t.replace('<div class="share"', EXTRA[slug] + '\n<div class="share"', 1)
    open(os.path.join("posts", fn), "w", encoding="utf-8").write(t)
    n += 1
print("أُعيد بناء", n, "مقالًا")
print("DONE")
