#!/usr/bin/env python3
"""تثبيت خريطة الصور الفوتوغرافية والتحقق من أبعادها وارتباطها بالمقالات."""
from pathlib import Path
from PIL import Image
import json
ROOT=Path(__file__).resolve().parents[1]
IMAGES={
'lemon-mint-drink':('images/new-lemon-mint-drink.jpg','كأس عصير ليمون ونعناع مثلج مع شرائح ليمون وأوراق نعناع'),
'samosa-cheese-dough':('images/new-samosa-cheese-dough.jpg','سمبوسك جبن ذهبي مقرمش مقدم على طبق خزفي'),
'laundry-guide-tips':('images/new-laundry-guide-tips.jpg','ملابس قطنية مطوية بعناية بجوار سلة غسيل'),
'qishta-basbousa':('images/new-qishta-basbousa.jpg','قطع بسبوسة بالقشطة واللوز على طبق تقديم'),
'natural-insect-repellents':('images/new-natural-insect-repellents.jpg','نباتات ريحان ونعناع قرب نافذة منزلية مزودة بشبك'),
'speed-up-slow-computer':('images/new-speed-up-slow-computer.jpg','حاسوب مكتبي في مساحة عمل تقنية مرتبة'),
'save-mobile-data':('images/new-save-mobile-data.jpg','هاتف ذكي بجوار جهاز اتصال على مكتب'),
'quick-kitchen-cleaning':('images/new-quick-kitchen-cleaning.jpg','مطبخ مرتب مع أدوات تنظيف مناسبة للأسطح'),
'account-recovery-plan':('images/editorial/account-recovery-plan.jpg','يد ترتب رموز استرداد ومفتاح أمان بجوار حاسوب'),
'age-of-earth':('images/editorial/age-of-earth.jpg','باحثة جيولوجيا تفحص طبقات صخرية قديمة بجوار مجسم للأرض'),
'ai-explained-simply':('images/editorial/ai-explained-simply.jpg','محطة حاسوب تعرض شبكة بيانات مترابطة ترمز إلى الذكاء الاصطناعي'),
'amazing-animal-facts':('images/editorial/amazing-animal-facts.jpg','مكتب باحث حياة برية يضم منظارًا وآثار حيوانات وصورًا ميدانية'),
'amazing-human-body-facts':('images/editorial/amazing-human-body-facts.jpg','نماذج تشريحية للقلب والدماغ مع سماعة طبية على مكتب'),
'amazing-water-facts':('images/editorial/amazing-water-facts.jpg','عينات ماء وأدوات قياس مخبرية بجوار مجرى طبيعي'),
'chicken-kabsa':('images/editorial/chicken-kabsa.jpg','طبق كبسة دجاج سعودي مع أرز بسمتي وبهارات وتزيين'),
'choose-smartphone-budget':('images/editorial/choose-smartphone-budget.jpg','ثلاثة هواتف مختلفة موضوعة للمقارنة قبل الشراء'),
'cleaning-products-never-mix':('images/editorial/cleaning-products-never-mix.jpg','عبوتا تنظيف منفصلتان مع قفازات على سطح مطبخ'),
'coffee-story-yemen':('images/editorial/coffee-story-yemen.jpg','قهوة وحبوب ومصب نحاسي أمام مدرجات جبلية يمنية'),
'eliminate-bad-smells':('images/editorial/eliminate-bad-smells.jpg','مطبخ نظيف بنافذة مفتوحة وتهوية طبيعية'),
'essential-android-apps':('images/editorial/essential-android-apps.jpg','هاتف ذكي يعرض تطبيقات متنوعة بلا شعارات تجارية'),
'fruit-salad-recipe':('images/editorial/fruit-salad-recipe.jpg','وعاء سلطة فواكه طازجة مع صوص عسل وليمون'),
'galaxies-and-stars':('images/editorial/galaxies-and-stars.jpg','تلسكوب يرصد مجرة درب التبانة في سماء ليلية صافية'),
'gulf-rice-spices-guide':('images/editorial/gulf-rice-spices-guide.jpg','أوعية بهارات خليجية تضم الهيل والقرفة والقرنفل واللومي حول الأرز'),
'lentil-soup-recipe':('images/editorial/lentil-soup-recipe.jpg','وعاء شوربة عدس كريمية مع ليمون وكمون وخبز'),
'natural-cleaning-recipes':('images/editorial/natural-cleaning-recipes.jpg','ليمون وبيكربونات وخل وفرشاة للتنظيف المنزلي'),
'orange-cake-no-oven':('images/editorial/orange-cake-no-oven.jpg','كيكة برتقال بجوار قدر طهي وثمار برتقال'),
'organize-fridge-waste':('images/editorial/organize-fridge-waste.jpg','ثلاجة مفتوحة مرتبة بعلب طعام وخضروات وألبان'),
'protect-online-accounts':('images/editorial/protect-online-accounts.jpg','هاتف يعرض مصادقة متعددة العوامل بجوار حاسوب ومفتاح أمان'),
'safe-online-payments':('images/editorial/safe-online-payments.jpg','بطاقة مصرفية وهاتف يعرض تأكيد عملية دفع إلكترونية'),
'save-electricity-bill':('images/editorial/save-electricity-bill.jpg','مصباح موفر وعداد استهلاك وجهاز تحكم بالتكييف'),
'tidy-home-in-15-minutes':('images/editorial/tidy-home-in-15-minutes.jpg','غرفة معيشة مرتبة مع سلة تنظيم ومؤقت منزلي'),
'used-smartphone-checklist':('images/editorial/used-smartphone-checklist.jpg','يدان تفحصان هاتفًا مستعملًا بجوار قائمة تحقق وكابل شحن'),
'why-we-need-sleep':('images/editorial/why-we-need-sleep.jpg','غرفة نوم هادئة بإضاءة قمرية وسرير مرتب'),
'zaatar-manakeesh':('images/editorial/zaatar-manakeesh.jpg','مناقيش زعتر طازجة مع زيت زيتون وأوراق زعتر')}
def main():
 posts={p.stem for p in (ROOT/'posts').glob('*.html')}
 if posts!=set(IMAGES):raise SystemExit(f'عدم تطابق المقالات والصور: ناقص {posts-set(IMAGES)} زائد {set(IMAGES)-posts}')
 mapping={}
 for slug,(path,alt) in IMAGES.items():
  file=ROOT/path
  if not file.exists():raise SystemExit(f'صورة مفقودة: {file}')
  if Image.open(file).size!=(1200,630):raise SystemExit(f'أبعاد غير صحيحة: {file} {Image.open(file).size}')
  mapping[slug]={'path':path,'alt':alt}
 (ROOT/'images'/'article-images.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f'تم التحقق من {len(mapping)} صورة فوتوغرافية مستقلة.')
if __name__=='__main__':main()
