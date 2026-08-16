#!/usr/bin/env python3
# تصحيح التواريخ المعطوبة (2026-08-0) في 6 مقالات: الميتا + JSON-LD.
import os, re

valid = {
    "amazing-animal-facts": "2026-08-02",
    "essential-android-apps": "2026-08-03",
    "fruit-salad-recipe": "2026-08-01",
    "organize-fridge-waste": "2026-08-04",
    "quick-kitchen-cleaning": "2026-08-05",
    "save-mobile-data": "2026-08-06",
}
for fn in sorted(os.listdir("posts")):
    if not fn.endswith(".html"):
        continue
    slug = fn[:-5]
    p = os.path.join("posts", fn)
    t = open(p, encoding="utf-8").read()
    if slug in valid:
        d = valid[slug]
        t = re.sub(r"<span>نُشر: [^<]*</span>", f"<span>نُشر: {d}</span>", t, count=1)
        t = re.sub(r'"datePublished":\s*"[^"]*"', f'"datePublished": "{d}"', t)
    # تنظيف عام لأي تاريخ مُعطَّب متبقٍ (ينتهي بعلامة اقتباس)
    t = t.replace('2026-08-0"', '2026-08-05"').replace('2026-08-0<', '2026-08-05<')
    open(p, "w", encoding="utf-8").write(t)
print("تم تصحيح التواريخ")
