#!/usr/bin/env python3
"""إضافة كود التحقق من Google إلى موقع دليلك (Search Console).

يدعم طريقتي التحقق الرسميتين:
  1. وسم meta في <head> (يُحقن في كل صفحات الموقع ويُحفظ تلقائيًا عند إعادة التوليد).
  2. ملف تحقق googleXXXX.html في جذر الموقع (تتجاهله أدوات التوليد والفحص حتى لا يتلف).

الاستخدام:
  python3 tools/add_google_verification.py --status
  python3 tools/add_google_verification.py --code "kFF7...ABC"
  python3 tools/add_google_verification.py --code '<meta name="google-site-verification" content="kFF7...ABC" />'
  python3 tools/add_google_verification.py --file googleABC123.html
  python3 tools/add_google_verification.py --file googleABC123.html --file-content "google-site-verification: googleABC123.html"
  python3 tools/add_google_verification.py --code "kFF7...ABC" --file googleABC123.html
  python3 tools/add_google_verification.py --remove

بعد التشغيل: ادمج وانشر، ثم اضغط «تحقق» في Search Console. لا تحذف الكود بعد التحقق.
"""
from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "site-config.json"
META_RE = re.compile(r'<meta\s+name="google-site-verification"\s+content="[^"]*"\s*/?>')
CONTENT_RE = re.compile(r'content\s*=\s*"([^"]+)"')
VIEWPORT_RE = re.compile(r'(<meta name="viewport"[^>]*>)')
FILE_RE = re.compile(r"google[a-zA-Z0-9_-]+\.html")


def is_verification_file(path: Path) -> bool:
    """ملف تحقق جوجل: في الجذر واسمه يبدأ بـ google وينتهي بـ .html."""
    return path.parent == ROOT and path.name.startswith("google") and path.suffix == ".html"


def site_pages() -> list[Path]:
    """كل صفحات الموقع ما عدا ملفات التحقق والمجلدات المستثناة."""
    pages = []
    for path in sorted(ROOT.rglob("*.html")):
        if "node_modules" in path.parts or "qa" in path.parts:
            continue
        if is_verification_file(path):
            continue
        pages.append(path)
    return pages


def extract_code(raw: str) -> str:
    """يستخرج قيمة الكود سواء أُعطي خامًا أو وسم meta كاملًا."""
    raw = raw.strip().strip("'\"")
    if "google-site-verification" in raw:
        match = CONTENT_RE.search(raw)
        if not match:
            raise SystemExit("تعذّر استخراج content من الوسم. الصق الوسم كاملًا كما أعطتك إياه جوجل.")
        return match.group(1).strip()
    return raw.strip()


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def save_config(config: dict) -> None:
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def inject_meta(text: str, code: str) -> tuple[str, bool]:
    """يحقن وسم التحقق أو يحدّثه. يعيد (النص، هل تغيّر؟)."""
    tag = f'<meta name="google-site-verification" content="{html_lib.escape(code, quote=True)}">'
    if 'name="google-site-verification"' in text:
        new_text = META_RE.sub(tag, text, count=1)
        return new_text, new_text != text
    if "<head>" not in text:
        return text, False
    if "<meta name=\"viewport\"" in text:
        return VIEWPORT_RE.sub(r"\1\n" + tag, text, count=1), True
    return text.replace("</head>", tag + "\n</head>", 1), True


def remove_meta(text: str) -> tuple[str, bool]:
    if 'name="google-site-verification"' not in text:
        return text, False
    # الحقن يضيف سطرًا جديدًا مع الوسم، فالإزالة تحذفهما معًا لاستعادة النص الأصلي حرفيًا.
    new_text, count = re.subn(
        r'\n<meta\s+name="google-site-verification"\s+content="[^"]*"\s*/?>', "", text, count=1
    )
    if not count:
        new_text, count = re.subn(
            r'<meta\s+name="google-site-verification"\s+content="[^"]*"\s*/?>\n?', "", text, count=1
        )
    return new_text, bool(count)


def run_audit() -> None:
    result = subprocess.run([sys.executable, str(ROOT / "tools" / "audit_site.py")])
    if result.returncode:
        raise SystemExit("أُضيف الكود لكن فحص الموقع رصد مشكلة — راجع الأخطاء أعلاه.")


def show_status() -> None:
    config = load_config()
    code = (config.get("googleSiteVerification") or "").strip()
    files = sorted(p.name for p in ROOT.glob("google*.html"))
    pages = site_pages()
    tagged = sum(1 for p in pages if 'name="google-site-verification"' in p.read_text(encoding="utf-8"))
    print(f"الكود المحفوظ في الإعدادات: {'موجود (' + str(len(code)) + ' حرفًا)' if code else 'لا يوجد'}")
    print(f"ملفات التحقق في الجذر: {', '.join(files) if files else 'لا يوجد'}")
    print(f"الصفحات الحاملة للوسم: {tagged} من {len(pages)}")
    if code and tagged < len(pages):
        print("تنبيه: بعض الصفحات بلا وسم — أعد تشغيل الأداة مع --code لتعميمه.")
    if not code and not files:
        print("لا يوجد تحقق بعد. راجع docs/google-verification.md لخطوات الحصول على الكود.")


def apply_code(code: str) -> None:
    config = load_config()
    config["googleSiteVerification"] = code
    save_config(config)
    changed = 0
    for path in site_pages():
        text = path.read_text(encoding="utf-8")
        new_text, did_change = inject_meta(text, code)
        if did_change:
            path.write_text(new_text, encoding="utf-8")
            changed += 1
    print(f"حُفظ الكود في site-config.json وحُقن الوسم في {changed} صفحة.")


def apply_file(name: str, content: str | None) -> None:
    name = name.strip()
    if not FILE_RE.fullmatch(name):
        raise SystemExit("اسم الملف غير صالح. يجب أن يكون مثل: googleABC123def456.html")
    body = (content or f"google-site-verification: {name}").strip() + "\n"
    (ROOT / name).write_text(body, encoding="utf-8")
    print(f"أُنشئ ملف التحقق: {name}")


def remove_all() -> None:
    config = load_config()
    config["googleSiteVerification"] = ""
    save_config(config)
    changed = 0
    for path in site_pages():
        text = path.read_text(encoding="utf-8")
        new_text, did_change = remove_meta(text)
        if did_change:
            path.write_text(new_text, encoding="utf-8")
            changed += 1
    deleted = []
    for path in ROOT.glob("google*.html"):
        if path.suffix == ".html":
            path.unlink()
            deleted.append(path.name)
    print(f"أُزيل الوسم من {changed} صفحة وحُذف من الإعدادات.")
    print(f"ملفات التحقق المحذوفة: {', '.join(deleted) if deleted else 'لا يوجد'}")
    print("تحذير: إزالة التحقق قد تُفقدك ملكية الموقع في Search Console.")


def main() -> None:
    parser = argparse.ArgumentParser(description="إضافة كود التحقق من Google إلى موقع دليلك")
    parser.add_argument("--code", help="قيمة الكود أو وسم meta الكامل من Search Console")
    parser.add_argument("--file", help="اسم ملف التحقق مثل googleABC123.html")
    parser.add_argument("--file-content", help="محتوى ملف التحقق كما أعطتك إياه جوجل")
    parser.add_argument("--status", action="store_true", help="عرض حالة التحقق الحالية دون تغيير")
    parser.add_argument("--remove", action="store_true", help="إزالة كل آثار التحقق (وسم + ملفات + إعدادات)")
    args = parser.parse_args()

    if args.status:
        show_status()
        return
    if args.remove:
        if args.code or args.file:
            raise SystemExit("لا تجمع بين --remove وخيارات الإضافة.")
        remove_all()
        run_audit()
        return
    if not args.code and not args.file:
        parser.print_help()
        raise SystemExit("حدّد --code أو --file (أو --status للعرض فقط).")
    if args.file_content and not args.file:
        raise SystemExit("--file-content يتطلب --file أيضًا.")
    if args.code:
        code = extract_code(args.code)
        if not code or len(code) < 8 or "<" in code or ">" in code:
            raise SystemExit("الكود يبدو ناقصًا أو غير صالح. الصقه كاملًا كما أعطتك إياه جوجل.")
        apply_code(code)
    if args.file:
        apply_file(args.file, args.file_content)
    run_audit()
    print("تم. الخطوة الأخيرة: انشر الموقع ثم اضغط «تحقق» في Search Console.")


if __name__ == "__main__":
    main()
