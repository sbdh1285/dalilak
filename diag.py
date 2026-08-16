import os, re, subprocess
def style_info(f):
    t=open(f,encoding='utf-8').read()
    n=t.count('<style>')
    i=t.find('<style>');j=t.find('</style>')
    css=t[i+7:j] if i!=-1 and j!=-1 else ''
    return n, css.count('{'), css.count('}'), len(css)
for f in ['index.html','posts/fruit-salad-recipe.html','posts/save-mobile-data.html']:
    n,ob,cb,ln=style_info(f)
    print(f, '| <style>:',n,'| { :',ob,' } :',cb,'| len',ln, '| balanced:', ob==cb)
print('--- posts with "0 دقائق":', sum(1 for fn in os.listdir('posts') if '0 دقائق' in open('posts/'+fn,encoding='utf-8').read()))
print('--- unique "نُشر:" values ---')
vals=set()
for fn in os.listdir('posts'):
    for m in re.findall(r'نُشر: ([0-9-]+)', open('posts/'+fn,encoding='utf-8').read()):
        vals.add(m)
print(sorted(vals))
print('--- title "0 دقائق" count in posts ---', sum(1 for fn in os.listdir('posts') if '0 دقائق' in open('posts/'+fn,encoding='utf-8').read()))
# root commit original fruit-salad
root=subprocess.check_output(['git','log','--reverse','--format=%H']).decode().split()[0]
orig=subprocess.check_output(['git','show',root+':posts/fruit-salad-recipe.html']).decode()
print('--- ORIGINAL fruit-salad title/date lines ---')
for line in orig.splitlines():
    if 'دقائق' in line or '2026-' in line or '<title>' in line or 'og:title' in line:
        print(repr(line[:160]))
print('--- sbdh1285 vs sbdh285 counts (html) ---')
c1285=subprocess.check_output(['grep','-rho','sbdh1285.github.io','--include=*.html','.']).decode().count('sbdh1285')
c285=subprocess.check_output(['grep','-rho','sbdh285.github.io','--include=*.html','.']).decode().count('sbdh285')
print('sbdh1285:',c1285,'| sbdh285:',c285)
