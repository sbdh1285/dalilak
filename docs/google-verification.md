# التحقق من ملكية الموقع في Google Search Console

هذا الدليل يشرح كيف ترفع كود التحقق من جوجل إلى موقع دليلك خطوة بخطوة.

## الخطوة 1: احصل على الكود من جوجل

1. ادخل إلى [Google Search Console](https://search.google.com/search-console).
2. أضف موقعًا جديدًا بنوع **«بادئة عنوان URL»** وأدخل رابط الموقع:
   - الرابط الحالي: `https://sbdh1285.github.io/dalilak/`
   - (بعد ربط الدومين المخصص ستضيف الموقع الجديد وتتحقق منه أيضًا).
3. ستعرض جوجل عدة طرق للتحقق — اختر واحدة:
   - **علامة HTML (موصى بها):** سطر مثل:
     `<meta name="google-site-verification" content="kFF7...ABC" />`
     انسخه كاملًا.
   - **ملف HTML:** ملف اسمه مثل `googleABC123def456.html` — لاحظ الاسم
     ومحتواه (عادة سطر واحد يبدأ بـ `google-site-verification:`).

## الخطوة 2: أضف الكود إلى الموقع

من جذر المشروع نفّذ أحد الأوامر التالية:

```bash
# الطريقة الأولى: وسم meta (يكفي وحده للتحقق)
python3 tools/add_google_verification.py --code "الصق-الكود-هنا"

# أو الصق الوسم كاملًا كما أعطتك إياه جوجل
python3 tools/add_google_verification.py --code '<meta name="google-site-verification" content="kFF7...ABC" />'

# الطريقة الثانية: ملف تحقق
python3 tools/add_google_verification.py --file googleABC123def456.html

# أو مع تحديد المحتوى إذا زودتك جوجل بنص مختلف
python3 tools/add_google_verification.py --file googleABC123def456.html --file-content "google-site-verification: googleABC123def456.html"

# لعرض الحالة الحالية دون تغيير
python3 tools/add_google_verification.py --status
```

ماذا تفعل الأداة؟

- تحفظ الكود في `site-config.json` (`googleSiteVerification`).
- تحقن الوسم في كل صفحات الموقع (بعد `viewport` مباشرة).
- تُنشئ ملف التحقق في جذر الموقع عند طلب `--file`.
- تشغّل فحص الموقع تلقائيًا للتأكد من سلامة كل شيء.

## الخطوة 3: انشر ثم اضغط «تحقق»

1. ادمج التغييرات في `main` وانتظر نشر GitHub Pages.
2. تأكد أن الوسم ظاهر في الصفحة الرئيسية (اعرض مصدر الصفحة وابحث عن `google-site-verification`)،
   أو أن ملف التحقق يُفتح على `رابط-الموقع/googleABC123def456.html`.
3. ارجع إلى Search Console واضغط **«تحقق»**.

## ملاحظات مهمة

- **لا تحذف الكود بعد التحقق** — جوجل تعيد فحصه دوريًا وقد تُفقدك الملكية.
- الكود **ثابت ودائم**: أدوات `maintain_site` و`redesign_magazine` تعيد حقن الوسم
  تلقائيًا من الإعدادات، وملف التحقق مستثنى من كل أدوات التوليد والفحص فلا يُمس ولا يُحسب كصفحة.
- ملف التحقق غير مدرج في `sitemap.xml` عمدًا، و`robots.txt` يسمح لجوجل بالوصول إليه.
- عند ربط دومين مخصص لاحقًا ستحتاج إلى **تحقق جديد** لعنوان الموقع الجديد في Search Console.
- لإزالة التحقق نهائيًا (غير موصى به): `python3 tools/add_google_verification.py --remove`.
