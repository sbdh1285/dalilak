#!/usr/bin/env python3
"""ربط دومين مخصص (وبريد رسمي اختياري) بموقع دليلك بأمان.

تقوم الأداة بما يلي فقط، دون المساس بسجل التوثيق أو إعادة توليد المحتوى:
  1. تحديث site-config.json (الرابط، الدومين، البريد، حالة التواصل).
  2. إنشاء ملف CNAME.
  3. استبدال الرابط القديم بالجديد في ملفات النشر فقط (html/xml/txt/json المنشورة).
  4. استبدال البريد القديم بالجديد في الصفحات (mailto والنموذج وJSON-LD).
  5. إعادة التوليد الآمن: maintain_site ثم refresh_feed ثم build_site_inventory.
  6. التحقق ببوابات الجودة، وأي فشل يوقف الأداة مع إرشاد للتراجع عبر git.

الاستخدام:
  python3 tools/configure_domain.py --domain dalilak.com --email contact@dalilak.com --enable-contact
  python3 tools/configure_domain.py --domain dalilak.com --email dalilak77505@gmail.com --enable-contact
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DOMAIN_RE = re.compile(r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}")
EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def run(script: str) -> None:
    subprocess.run([sys.executable, str(ROOT / "tools" / script)], check=True)


def published_files() -> list[Path]:
    """ملفات النشر التي يجوز تعديل روابطها (لا تشمل التوثيق ولا الأدوات)."""
    skip_dirs = {".git", "node_modules", "__pycache__", "tools", "docs", "fonts", "images"}
    skip_files = {"configure_domain.py", "CNAME"}
    results: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name in skip_files:
            continue
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.suffix not in {".html", ".xml", ".json", ".txt"}:
            continue
        if path.suffix == ".json" and path.name not in {"site-config.json", "manifest.json"}:
            continue
        results.append(path)
    return sorted(results)


def replace_in_published(old: str, new: str) -> int:
    changed = 0
    for path in published_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if old in text:
            path.write_text(text.replace(old, new), encoding="utf-8")
            changed += 1
    return changed


def remove_contact_form() -> None:
    """إزالة النموذج وعرض البريد عند تعطيل التواصل حتى لا تضيع الرسائل."""
    path = ROOT / "contact.html"
    text = path.read_text(encoding="utf-8")
    pending = (
        '<div class="contact-status" id="contact-status"><strong>قناة التواصل قيد التجهيز</strong>'
        "<p>أزلنا النموذج مؤقتًا حتى لا تضيع الرسائل. سنعلن البريد الرسمي هنا فور جاهزيته.</p></div>"
    )
    text = re.sub(r'<form class="contact-form".*?</form>', pending, text, count=1, flags=re.S)
    text = re.sub(
        r'<p class="contact-email">.*?</p>',
        '<p class="contact-email">سيُعلن قريبًا</p>',
        text,
        count=1,
        flags=re.S,
    )
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="ربط دومين مخصص بموقع دليلك")
    parser.add_argument("--domain", required=True, help="مثال: dalilak.com دون https")
    parser.add_argument("--email", required=True, help="البريد الرسمي (يُفضّل على الدومين نفسه)")
    parser.add_argument(
        "--enable-contact",
        action="store_true",
        help="فعّل النموذج (لا تستخدمه قبل التأكد من استقبال البريد لرسالة اختبار)",
    )
    args = parser.parse_args()
    domain = args.domain.lower().strip().removeprefix("https://").removeprefix("http://").strip("/")
    email = args.email.lower().strip()
    if not DOMAIN_RE.fullmatch(domain):
        raise SystemExit("صيغة الدومين غير صحيحة (مثال: dalilak.com)")
    if not EMAIL_RE.fullmatch(email):
        raise SystemExit("صيغة البريد غير صحيحة")
    if not email.endswith("@" + domain):
        print(f"تحذير: البريد {email} ليس على الدومين {domain}. يُفضّل بريد على الدومين للاحترافية.", flush=True)

    config_path = ROOT / "site-config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    old_base = config["baseUrl"].rstrip("/")
    old_email = (config.get("email") or "").strip()
    new_base = "https://" + domain
    if old_base == new_base and old_email == email:
        print("لا تغيير: الدومين والبريد مطابقان للإعداد الحالي.", flush=True)
        return

    config["baseUrl"] = new_base
    config["customDomain"] = domain
    config["email"] = email
    config["contact"] = {
        "enabled": bool(args.enable_contact),
        "provider": "formsubmit",
        "recipient": email,
        "verified": False,
        "statusMessage": (
            "النموذج جاهز وينتظر تأكيد أول رسالة من FormSubmit."
            if args.enable_contact
            else "أنشئ البريد واختبره ثم فعّل النموذج."
        ),
    }
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "CNAME").write_text(domain + "\n", encoding="utf-8")

    changed_urls = replace_in_published(old_base, new_base)
    changed_emails = replace_in_published(old_email, email) if old_email and old_email != email else 0
    # أزرار المشاركة الاجتماعية تخزن الرابط مرمّزًا (percent-encoded).
    changed_encoded = replace_in_published(quote(old_base, safe=""), quote(new_base, safe=""))
    readme = ROOT / "README.md"
    if readme.exists() and old_base in readme.read_text(encoding="utf-8"):
        readme.write_text(readme.read_text(encoding="utf-8").replace(old_base, new_base), encoding="utf-8")
    print(f"استُبدل الرابط في {changed_urls} ملفًا (وترميز المشاركة في {changed_encoded})، والبريد في {changed_emails} ملفًا.", flush=True)

    if not args.enable_contact:
        remove_contact_form()

    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nDisallow: /404.html\n\nSitemap: {new_base}/sitemap.xml\n",
        encoding="utf-8",
    )
    security_contact = f"mailto:{email}" if args.enable_contact else f"{new_base}/contact.html"
    (ROOT / "security.txt").write_text(
        f"Contact: {security_contact}\nPreferred-Languages: ar\nExpires: {date.today().year + 1}-09-01\n",
        encoding="utf-8",
    )
    human_contact = email if args.enable_contact else f"{new_base}/contact.html"
    (ROOT / "humans.txt").write_text(
        "دليلك — مجلة عربية للمعرفة والحياة\n"
        "فريق التحرير: فريق تحرير دليلك\n"
        f"التواصل: {human_contact}\n"
        "اللغة: العربية\n",
        encoding="utf-8",
    )

    try:
        run("maintain_site.py")
        run("refresh_feed.py")
        run("build_site_inventory.py")
        run("audit_site.py")
        run("content_quality_audit.py")
        run("reading_time_audit.py")
    except subprocess.CalledProcessError:
        print("فشل التحقق! راجع الأخطاء أعلاه، وللتراجع عن كل التعديلات نفّذ: git checkout -- .")
        raise SystemExit(1)

    print(f"تم تجهيز {new_base} واجتازت كل الفحوص.")
    if args.enable_contact:
        print("الخطوات المتبقية بيدك: إعداد DNS وانتظار HTTPS، ثم تأكيد أول رسالة FormSubmit واختبار النموذج.")
    else:
        print("التواصل معطّل: أنشئ البريد وأرسل رسالة اختبار إليه، ثم أعد التشغيل مع --enable-contact لتفعيل النموذج.")


if __name__ == "__main__":
    main()
