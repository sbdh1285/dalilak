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
  t=re.sub(r'<div class="contact-status".*?</div>\s*','<div class="contact-status" id="contact-status"><strong>النموذج جاهز</strong><p>بعد أول إرسال، أكد العنوان من الرسالة التي ترسلها FormSubmit.</p></div>',t,flags=re.S)
  t=re.sub(r'<form class="contact-form[^>]*>','<form class="contact-form" action="https://formsubmit.co/'+args.email.lower()+'" method="POST">',t,count=1)
  t=t.replace(' disabled','')
  t=re.sub(r'(<input type="hidden" name="_next" value=")[^"]+(">)',rf'\g<1>{new}/thanks.html\2',t,count=1)
  t=re.sub(r'<p><b>البريد الإلكتروني:</b>.*?</p>',f'<p><b>البريد الإلكتروني:</b> <a href="mailto:{args.email.lower()}">{args.email.lower()}</a></p>',t,count=1)
 contact.write_text(t,encoding='utf-8')
 (ROOT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nDisallow: /404.html\n\nSitemap: {new}/sitemap.xml\n',encoding='utf-8')
 subprocess.run([sys.executable,str(ROOT/'tools'/'maintain_site.py')],check=True)
 subprocess.run([sys.executable,str(ROOT/'tools'/'phase_one_seo.py')],check=True)
 subprocess.run([sys.executable,str(ROOT/'tools'/'pre_domain_content.py')],check=True)
 subprocess.run([sys.executable,str(ROOT/'tools'/'audit_site.py')],check=True)
 print(f'تم تجهيز {new}. راجع DNS وHTTPS ثم اختبر النموذج قبل استقبال الرسائل.')
if __name__=='__main__':main()
