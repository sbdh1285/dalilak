#!/usr/bin/env python3
"""كسر قالبية العناوين المتكررة عبر المقالات.

المشكلة: 41 مقالًا يحملون «الخلاصة السريعة» و«الخلاصة»، و38 يحملون «أسئلة
شائعة» — تكرار حرفي عبر الموقع كله يقرأه مراجع أدسنس ومحركات البحث كقالب
آلي لا كتحرير بشري.

الحل: صياغة بديلة مناسبة لنوع كل مقال (وصفة/نصيحة منزلية/معلومة/تقنية).
النص المعروض فقط هو ما يتغير — المعرّفات (id) تبقى كما هي حتى لا تنكسر
الأنكورات ولا جدول المحتويات ولا الروابط الخارجية.

يعمل السكربت مباشرة على ملفات posts/ ويستدعيه pre_domain_content بعد
deepen_content. idempotent: يتعرف على الصيغ البديلة فلا يعيد تدويرها.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "posts"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from artedit import sync_toc  # noqa: E402

# صيغ بديلة لكل عنوان قالبي، موزعة حسب المقال.
# المفتاح: النص الأصلي. القيمة: خريطة slug -> النص البديل.

QUICK = {
    # وصفات
    "rice-pudding-recipe": "باختصار: قوام ناجح من أول مرة",
    "arabic-coffee-guide": "باختصار: دلة متزنة في خطوات قليلة",
    "gulf-rice-spices-guide": "باختصار: خلطة متوازنة بلا مبالغة",
    "lemon-mint-drink": "باختصار: مشروب منعش في دقائق",
    "samosa-cheese-dough": "باختصار: عجينة ذهبية مقرمشة",
    "qishta-basbousa": "باختصار: بسبوسة مسقية لا تنهار",
    "fruit-salad-recipe": "باختصار: طبق فاكهة يبقى طازجًا",
    "chicken-kabsa": "باختصار: كبسة بحبات منفصلة",
    "orange-cake-no-oven": "باختصار: كيكة هشة بلا فرن",
    "lentil-soup-recipe": "باختصار: شوربة كثيفة متزنة الطعم",
    "zaatar-manakeesh": "باختصار: مناقيش بيتية اقتصادية",
    # نصائح منزلية
    "microwave-steam-clean": "الزبدة: بخار بدل الفرك",
    "drain-maintenance-tips": "الزبدة: الوقاية أرخص من التسليك",
    "cleaning-products-never-mix": "الزبدة: منتج واحد في كل مرة",
    "laundry-guide-tips": "الزبدة: الملصق قبل أي حيلة",
    "natural-insect-repellents": "الزبدة: اقطع السبب ثم اطرد",
    "quick-kitchen-cleaning": "الزبدة: الترتيب يوفّر نصف الوقت",
    "organize-fridge-waste": "الزبدة: أربع درجات وتاريخ مكتوب",
    "save-electricity-bill": "الزبدة: أكبر الأحمال أولًا",
    "eliminate-bad-smells": "الزبدة: المصدر لا العطر",
    "natural-cleaning-recipes": "الزبدة: وصفات بسيطة وحدودها",
    "tidy-home-in-15-minutes": "الزبدة: خمس عشرة دقيقة يوميًا",
    # معلومات عامة
    "learn-new-skills-guide": "الفكرة في سطور",
    "amazing-animal-facts": "الفكرة في سطور",
    "amazing-water-facts": "الفكرة في سطور",
    "galaxies-and-stars": "الفكرة في سطور",
    "age-of-earth": "الفكرة في سطور",
    "coffee-story-yemen": "الفكرة في سطور",
    "why-we-need-sleep": "الفكرة في سطور",
    "amazing-human-body-facts": "الفكرة في سطور",
    # تكنولوجيا
    "backup-photos-guide": "ابدأ من هنا",
    "android-security-settings": "ابدأ من هنا",
    "used-smartphone-checklist": "ابدأ من هنا",
    "account-recovery-plan": "ابدأ من هنا",
    "speed-up-slow-computer": "ابدأ من هنا",
    "save-mobile-data": "ابدأ من هنا",
    "essential-android-apps": "ابدأ من هنا",
    "safe-online-payments": "ابدأ من هنا",
    "ai-explained-simply": "ابدأ من هنا",
    "protect-online-accounts": "ابدأ من هنا",
    "choose-smartphone-budget": "ابدأ من هنا",
}

END = {
    # وصفات
    "rice-pudding-recipe": "قبل أن تبدأ",
    "arabic-coffee-guide": "قبل أن تبدأ",
    "gulf-rice-spices-guide": "قبل أن تبدأ",
    "lemon-mint-drink": "قبل أن تبدأ",
    "samosa-cheese-dough": "قبل أن تبدأ",
    "qishta-basbousa": "قبل أن تبدأ",
    "fruit-salad-recipe": "قبل أن تبدأ",
    "chicken-kabsa": "قبل أن تبدأ",
    "orange-cake-no-oven": "قبل أن تبدأ",
    "lentil-soup-recipe": "قبل أن تبدأ",
    "zaatar-manakeesh": "قبل أن تبدأ",
    # نصائح منزلية
    "microwave-steam-clean": "خطوتك التالية",
    "drain-maintenance-tips": "خطوتك التالية",
    "cleaning-products-never-mix": "خطوتك التالية",
    "laundry-guide-tips": "خطوتك التالية",
    "natural-insect-repellents": "خطوتك التالية",
    "quick-kitchen-cleaning": "خطوتك التالية",
    "organize-fridge-waste": "خطوتك التالية",
    "save-electricity-bill": "خطوتك التالية",
    "eliminate-bad-smells": "خطوتك التالية",
    "natural-cleaning-recipes": "خطوتك التالية",
    "tidy-home-in-15-minutes": "خطوتك التالية",
    # معلومات عامة
    "learn-new-skills-guide": "ما يستحق أن تتذكره",
    "amazing-animal-facts": "ما يستحق أن تتذكره",
    "amazing-water-facts": "ما يستحق أن تتذكره",
    "galaxies-and-stars": "ما يستحق أن تتذكره",
    "age-of-earth": "ما يستحق أن تتذكره",
    "coffee-story-yemen": "ما يستحق أن تتذكره",
    "why-we-need-sleep": "ما يستحق أن تتذكره",
    "amazing-human-body-facts": "ما يستحق أن تتذكره",
    # تكنولوجيا
    "backup-photos-guide": "خلاصة عملية",
    "android-security-settings": "خلاصة عملية",
    "used-smartphone-checklist": "خلاصة عملية",
    "account-recovery-plan": "خلاصة عملية",
    "speed-up-slow-computer": "خلاصة عملية",
    "save-mobile-data": "خلاصة عملية",
    "essential-android-apps": "خلاصة عملية",
    "safe-online-payments": "خلاصة عملية",
    "ai-explained-simply": "خلاصة عملية",
    "protect-online-accounts": "خلاصة عملية",
    "choose-smartphone-budget": "خلاصة عملية",
}

FAQ = {
    "وصفات": "أسئلة تتكرر في المطبخ",
    "منزلية": "أسئلة تتكرر عمليًا",
    "معلومات": "أسئلة يطرحها القراء",
    "تقنية": "أسئلة شائعة حول هذا الموضوع",
}

CATEGORY_OF: dict[str, str] = {}
for s in QUICK:
    if s in (
        "rice-pudding-recipe", "arabic-coffee-guide", "gulf-rice-spices-guide",
        "lemon-mint-drink", "samosa-cheese-dough", "qishta-basbousa",
        "fruit-salad-recipe", "chicken-kabsa", "orange-cake-no-oven",
        "lentil-soup-recipe", "zaatar-manakeesh",
    ):
        CATEGORY_OF[s] = "وصفات"
    elif s in (
        "learn-new-skills-guide", "amazing-animal-facts", "amazing-water-facts",
        "galaxies-and-stars", "age-of-earth", "coffee-story-yemen",
        "why-we-need-sleep", "amazing-human-body-facts",
    ):
        CATEGORY_OF[s] = "معلومات"
    elif s in (
        "backup-photos-guide", "android-security-settings", "used-smartphone-checklist",
        "account-recovery-plan", "speed-up-slow-computer", "save-mobile-data",
        "essential-android-apps", "safe-online-payments", "ai-explained-simply",
        "protect-online-accounts", "choose-smartphone-budget",
    ):
        CATEGORY_OF[s] = "تقنية"
    else:
        CATEGORY_OF[s] = "منزلية"


def retitle(body: str, old: str, new: str) -> str:
    """غيّر نص عنوان h2 دون المساس بمعرّفه."""
    pattern = re.compile(
        r'(<h2\b[^>]*>)\s*' + re.escape(old) + r'\s*(</h2>)'
    )
    return pattern.sub(lambda m: m.group(1) + new + m.group(2), body, count=1)


def process(slug: str) -> str:
    path = POSTS / f"{slug}.html"
    if not path.exists():
        return f"– {slug}: غير موجود"
    text = path.read_text(encoding="utf-8")
    before = text

    if slug in QUICK:
        text = retitle(text, "الخلاصة السريعة", QUICK[slug])
    if slug in END:
        text = retitle(text, "الخلاصة", END[slug])
    cat = CATEGORY_OF.get(slug)
    if cat:
        text = retitle(text, "أسئلة شائعة", FAQ[cat])

    if text == before:
        return f"= {slug}"
    path.write_text(text, encoding="utf-8")
    sync_toc(slug)
    return f"✓ {slug}"


def main() -> None:
    slugs = sorted({p.stem for p in POSTS.glob("*.html")})
    changed = sum(1 for s in slugs if process(s).startswith("✓"))
    print(f"تنويع العناوين: {changed} مقالًا مُحدَّثًا من {len(slugs)}.")


if __name__ == "__main__":
    main()
