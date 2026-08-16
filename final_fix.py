#!/usr/bin/env python3
# 1) استخراج CSS إلى css/style.css برابط نسبي.
# 2) استرجاع index.html وصفحات الأقسام من النسخة السليمة + تطبيق التحسينات (إصلاح بطاقات 0 تطبيقات/0 دقائق).
# 3) استبدال كل <style> برابط stylesheet في كل الصفحات.
import os, re, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))

# 1) استخراج CSS
ref = open("index.html", encoding="utf-8").read()
css = ref[ref.find("<style>") + 7: ref.find("</style>")]
css = css.replace("url('fonts/", "url('../fonts/")
os.makedirs("css", exist_ok=True)
open(os.path.join("css", "style.css"), "w", encoding="utf-8").write(css)
print("css/style.css:", len(css), "بايت")

# 2) استرجاع وتحسين الرئيسية + الأقسام
logs = subprocess.check_output(["git", "log", "--reverse", "--format=%H %s"]).decode().splitlines()
first_mine = [l.split(" ", 1)[0] for l in logs if ("فهرس بحث" in l or "تحسينات dalilak" in l or "improve" in l)][0]
parent = subprocess.check_output(["git", "rev-parse", first_mine + "^"]).decode().strip()

WEBITE = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"WebSite","name":"دليلك",'
          '"url":"https://sbdh1285.github.io/dalilak/","potentialAction":{"@type":"SearchAction",'
          '"target":"https://sbdh1285.github.io/dalilak/search.html?q={search_term_string}",'
          '"query-input":"required name=search_term_string"}}</script>')

def improve(t, rel, is_index=False):
    t = t.replace("sbdh285.github.io", "sbdh1285.github.io")
    t = t.replace("✅ ", "").replace("⭐ ", "").replace("📧 ", "").replace(" ❤️", "").replace("📡 ", "")
    t = t.replace('<span class="t-ic">💡</span>', "")
    t = t.replace("📚 ", "").replace("🗂 ", "").replace("🚀 ", "")
    if "disclaimer.html" not in t:
        t = t.replace(f'<a href="{rel}terms.html">شروط الاستخدام</a>',
                      f'<a href="{rel}terms.html">شروط الاستخدام</a>\n      <a href="{rel}disclaimer.html">إخلاء المسؤولية</a>\n      <a href="{rel}sitemap.html">خريطة الموقع</a>')
    if is_index and "SearchAction" not in t:
        t = t.replace("</head>", WEBITE + "\n</head>")
    return t

pages = ["index.html", "category/home-tips.html", "category/recipes.html",
         "category/knowledge.html", "category/tech.html"]
for p in pages:
    t = subprocess.check_output(["git", "show", parent + ":" + p]).decode()
    rel = "../" if p.startswith("category/") else ""
    t = improve(t, rel, is_index=(p == "index.html"))
    open(p, "w", encoding="utf-8").write(t)
print("تم استرجاع وتحسين صفحات:", len(pages))

# 3) استبدال <style> برابط stylesheet في كل الصفحات
n = 0
for dp, _, fns in os.walk(ROOT):
    if ".git" in dp:
        continue
    for fn in fns:
        if not fn.endswith(".html"):
            continue
        p = os.path.join(dp, fn)
        t = open(p, encoding="utf-8").read()
        if "<style>" in t:
            rel = "../" if (p.startswith(os.path.join(ROOT, "posts")) or p.startswith(os.path.join(ROOT, "category"))) else ""
            t = re.sub(r"<style>.*?</style>", f'<link rel="stylesheet" href="{rel}css/style.css">', t, flags=re.S)
            open(p, "w", encoding="utf-8").write(t)
            n += 1
print("صفحات حُوّلت لـ CSS خارجي:", n)
print("DONE")
