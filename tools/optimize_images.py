#!/usr/bin/env python3
"""إنشاء نسخ WebP متجاوبة للصور المستخدمة بصريًا مع إبقاء JPG للمشاركة الاجتماعية."""
from pathlib import Path
from PIL import Image,ImageOps
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'images'/'responsive'/'articles';OUT.mkdir(parents=True,exist_ok=True)
SIZES=(480,800,1200)
def save_webp(source:Path,target:Path,width:int,ratio:float):
 im=Image.open(source).convert('RGB');height=round(width/ratio);out=ImageOps.fit(im,(width,height),method=Image.Resampling.LANCZOS,centering=(.5,.5));out.save(target,'WEBP',quality=82,method=6)
def main():
 mapping=json.loads((ROOT/'images'/'article-images.json').read_text(encoding='utf-8'));manifest={'articles':{},'hero':{}}
 original_bytes=0;optimized_bytes=0
 for slug,data in mapping.items():
  source=ROOT/data['path'];original_bytes+=source.stat().st_size;manifest['articles'][slug]={}
  for width in SIZES:
   target=OUT/f'{slug}-{width}.webp';save_webp(source,target,width,1200/630);manifest['articles'][slug][str(width)]=target.relative_to(ROOT).as_posix();optimized_bytes+=target.stat().st_size
 hero=ROOT/'images'/'hero-editorial.jpg'
 for width in (640,960,1440):
  target=ROOT/'images'/'responsive'/f'hero-{width}.webp';target.parent.mkdir(parents=True,exist_ok=True);save_webp(hero,target,width,1440/900);manifest['hero'][str(width)]=target.relative_to(ROOT).as_posix();optimized_bytes+=target.stat().st_size
 (ROOT/'images'/'responsive'/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'articles':len(mapping),'sizes':len(SIZES),'originalBytes':original_bytes,'generatedBytes':optimized_bytes},ensure_ascii=False))
if __name__=='__main__':main()
