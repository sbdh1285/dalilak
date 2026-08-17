#!/usr/bin/env python3
"""تجهيز الموقع للدومين والبريد الرسمي من أمر واحد."""
from pathlib import Path
import argparse, json, re, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]

def main():
 ap=argparse.ArgumentParser(description='ربط دومين وبريد رسمي بموقع دليلك')
 ap.add_argument('--domain',required=True,help='مثال: dalilak.com دون https')
 ap.add_argument('--email',required=True,help='البريد الرسمي على الدومين')
 ap.add_argument('--enable-contact',action='store_true',help='فعّل النموذج بعد إنشاء البريد والتأكد من استقباله')
 args=ap.parse_args();domain=args.domain.lower().strip().removeprefix('https://').removeprefix('http://').strip('/')
 if not re.fullmatch(r'(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}',domain):raise SystemExit('صيغة الدومين غير صحيحة')
 if not re.fullmatch(r'[^@\s]+@'+re.escape(domain),args.email.lower()):raise SystemExit('يجب أن يكون البريد على الدومين نفسه')
 p=ROOT/'site-config.json';cfg=json.loads(p.read_text(encoding='utf-8'));old=cfg['baseUrl'].rstrip('/');new='https://'+domain
 cfg['baseUrl']=new;cfg['customDomain']=domain;cfg['email']=args.email.lower();cfg['contact']={'enabled':bool(args.enable_contact),'provider':'formsubmit','recipient':args.email.lower(),'verified':False,'statusMessage':'النموذج جاهز وينتظر تأكيد البريد.' if args.enable_contact else 'أنشئ البريد واختبره ثم فعّل النموذج.'}
 p.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(ROOT/'CNAME').write_text(domain+'\n',encoding='utf-8')
 # استبدال النطاق القديم في الملفات المنشورة قبل إعادة التوليد.
 for path in ROOT.rglob('*'):
  if not path.is_file() or any(x in path.parts for x in ('.git','node_modules','__pycache__')) or path.suffix not in {'.html','.xml','.json','.txt','.md','.py'}:continue
  try:text=path.read_text(encoding='utf-8')
  except UnicodeDecodeError:continue
  if path.name!='configure_domain.py':path.write_text(text.replace(old,new),encoding='utf-8')
 # إعداد نموذج التواصل.
 contact=ROOT/'contact.html';t=contact.read_text(encoding='utf-8')
 if args.enable_contact:
  active=f'''<h2>أرسل رسالة</h2><div class="contact-status" id="contact-status"><strong>النموذج جاهز</strong><p>بعد أول إرسال، أكد العنوان من الرسالة التي ترسلها FormSubmit.</p></div><form class="contact-form" action="https://formsubmit.co/{args.email.lower()}" method="POST"><input type="hidden" name="_subject" value="رسالة جديدة من موقع دليلك"><input type="hidden" name="_next" value="{new}/thanks.html"><input type="hidden" name="_captcha" value="true"><input class="form-honeypot" type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true"><div class="form-grid"><div><label for="contact-name">الاسم</label><input id="contact-name" name="name" type="text" autocomplete="name" required></div><div><label for="contact-email">البريد الإلكتروني</label><input id="contact-email" name="email" type="email" autocomplete="email" required></div></div><label for="contact-topic">الموضوع</label><select id="contact-topic" name="topic" required><option value="">اختر الموضوع</option><option>اقتراح مقال</option><option>تصحيح محتوى</option><option>استفسار عام</option></select><label for="contact-message">الرسالة</label><textarea id="contact-message" name="message" rows="7" minlength="10" required></textarea><p class="form-note">بإرسال النموذج توافق على معالجة البيانات اللازمة للرد وفق <a href="privacy-policy.html">سياسة الخصوصية</a>. لا ترسل معلومات حساسة.</p><button class="btn btn-a" type="submit">إرسال الرسالة</button></form>'''
  t=re.sub(r'<h2>(?:التواصل|أرسل رسالة)</h2>.*?(?=<h2>اقتراحات المواضيع</h2>)',active,t,count=1,flags=re.S)
  t=re.sub(r'<p><b>البريد الإلكتروني:</b>.*?</p>',f'<p><b>البريد الإلكتروني:</b> <a href="mailto:{args.email.lower()}">{args.email.lower()}</a></p>',t,count=1)
  t=t.replace('هذه الصفحة توضح حالة قناة التواصل. لن نعرض بريدًا أو نموذجًا غير عامل، وسيتم تحديثها فور ربط الدومين والبريد الرسمي.','نرحب بالملاحظات والتصحيحات واقتراحات الموضوعات عبر البريد أو النموذج الرسمي أدناه.')
  t=t.replace('سنفتح استقبال اقتراحات الموضوعات عند تشغيل قناة التواصل الرسمية.','يمكنك إرسال اقتراح موضوع عبر النموذج مع اختيار «اقتراح مقال».')
  t=t.replace('لا نستقبل حاليًا طلبات الإعلانات أو الشراكات حتى يتم تشغيل البريد الرسمي.','لطلبات الإعلانات أو الشراكات استخدم البريد الرسمي مع عنوان واضح للرسالة.')
 contact.write_text(t,encoding='utf-8')
 security_contact=f'mailto:{args.email.lower()}' if args.enable_contact else f'{new}/contact.html'
 (ROOT/'security.txt').write_text(f'Contact: {security_contact}\nPreferred-Languages: ar\nExpires: 2027-08-16\n',encoding='utf-8')
 human_contact=args.email.lower() if args.enable_contact else f'{new}/contact.html'
 (ROOT/'humans.txt').write_text(f'دليلك — مجلة عربية للمعرفة والحياة\nفريق التحرير: فريق تحرير دليلك\nالتواصل: {human_contact}\nاللغة: العربية\n',encoding='utf-8')
 (ROOT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nDisallow: /404.html\n\nSitemap: {new}/sitemap.xml\n',encoding='utf-8')
 subprocess.run([sys.executable,str(ROOT/'tools'/'pre_domain_content.py')],check=True)
 subprocess.run([sys.executable,str(ROOT/'tools'/'audit_site.py')],check=True)
 print(f'تم تجهيز {new}. راجع DNS وHTTPS ثم اختبر النموذج قبل استقبال الرسائل.')
if __name__=='__main__':main()
