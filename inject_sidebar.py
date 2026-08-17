import os,json,glob
idx=json.load(open('search-index.json'))
for fn in sorted(glob.glob('posts/*.html')):
    slug=fn.split('/')[-1][:-5]
    others=[x for x in idx if x['s']!=slug][:5]
    items=''
    for x in others:
        items+='<div class="pop-item"><img class="pop-thumb" src="../images/og-%s.png" alt="%s" loading="lazy" width="120" height="120"><div><a href="../posts/%s.html">%s</a><span class="pop-cat">%s</span></div></div>'%(x['s'],x['t'],x['s'],x['t'],x['c'])
    side='<aside class="side"><div class="widget"><h3>الأكثر قراءة</h3><div class="pop-list">%s</div></div></aside>'%items
    t=open(fn,encoding='utf-8').read()
    if 'class="layout"' not in t:
        t=t.replace('<div class="art">','<div class="layout"><div class="art">',1)
        t=t.replace('</div>\n<section class="sec">','</div>%s</div>\n<section class="sec">'%side,1)
        open(fn,'w',encoding='utf-8').write(t)
print('sidebar injected into', len(glob.glob('posts/*.html')), 'posts')
