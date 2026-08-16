#!/usr/bin/env python3
# إصلاح: النطاق sbdh285->sbdh1285، والتواريخ/«0 دقائق» باسترجاع القيم الصحيحة من النسخة الأصلية.
import os, re, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))

# 1) إصلاح النطاق في كل الملفات (html/xml)
n_domain = 0
for dp, _, fns in os.walk(ROOT):
    if ".git" in dp:
        continue
    for fn in fns:
        if fn.endswith((".html", ".xml", ".txt")):
            p = os.path.join(dp, fn)
            t = open(p, encoding="utf-8").read()
            if "sbdh285.github.io" in t:
                t = t.replace("sbdh285.github.io", "sbdh1285.github.io")
                open(p, "w", encoding="utf-8").write(t)
                n_domain += 1
print("ملفات عولجت (النطاق):", n_domain)

# 2) استرجاع التاريخ الصحيح ورقم الدقائق من حالة الملفات تمامًا قبل تعديلاتي
logs = subprocess.check_output(["git", "log", "--reverse", "--format=%H %s"]).decode().splitlines()
first_mine = None
for line in logs:
    h, _, msg = line.partition(" ")
    if "فهرس بحث" in msg or "تحسينات dalilak" in msg or "ما قبل أدسنس" in msg or "improve" in msg:
        first_mine = h
        break
if not first_mine:
    first_mine = subprocess.check_output(["git", "rev-list", "--max-parents=0", "HEAD"]).decode().split()[0]
root = subprocess.check_output(["git", "rev-parse", first_mine + "^"]).decode().strip()
n_fixed = 0
for fn in sorted(os.listdir(os.path.join(ROOT, "posts"))):
    if not fn.endswith(".html"):
        continue
    p = os.path.join("posts", fn)
    orig = subprocess.check_output(["git", "show", root + ":posts/" + fn]).decode()
    dm = re.search(r"📅 ([0-9\-]+)", orig)
    date = dm.group(1) if dm else "2026-08-01"
    tm = re.search(r"في (\d+) دقائق", orig)
    N = tm.group(1) if tm else "10"
    t = open(p, encoding="utf-8").read()
    # تصحيح تاريخ النشر
    t = re.sub(r"<span>نُشر: [^<]*</span>", f"<span>نُشر: {date}</span>", t, count=1)
    # تصحيح كل صيغ «0 دقائق» المتبقية في المتن/العناوين/المخطط
    t = t.replace("0 دقائق", f"{N} دقائق")
    # تصحيح وقت القراءة إن تحوّل إلى 0
    t = re.sub(r"مدة القراءة: 0 دقائق", f"مدة القراءة: {N} دقائق", t)
    # تصحيح تواريخ JSON-LD (datePublished / dateModified)
    t = re.sub(r'"datePublished":\s*"[^"]*"', f'"datePublished": "{date}"', t)
    t = re.sub(r'"dateModified":\s*"[^"]*"', '"dateModified": "2026-08-16"', t)
    # إصلاح وسم <h> غير الصحيح
    t = t.replace("<h>", "<h1>").replace("</h>", "</h1>")
    open(p, "w", encoding="utf-8").write(t)
    n_fixed += 1
print("مقالات عولجت (تواريخ/دقائق):", n_fixed)

# 3) التحقق
bad = 0
for fn in sorted(os.listdir(os.path.join(ROOT, "posts"))):
    if not fn.endswith(".html"):
        continue
    t = open(os.path.join("posts", fn), encoding="utf-8").read()
    if "sbdh285" in t:
        print("نطاق متبقٍ:", fn); bad += 1
    if "0 دقائق" in t:
        print("0 دقائق متبقٍ:", fn); bad += 1
    if not re.search(r"نُشر: \d{4}-\d{2}-\d{2}", t):
        print("تاريخ ناقص:", fn); bad += 1
print("مشاكل متبقية:", bad)
print("DONE")
