from pathlib import Path
from PIL import Image
import numpy as np,json,zlib
R=Path(__file__).resolve().parents[2];C=R/'代码';O=C/'assets/frames';O.mkdir(parents=True,exist_ok=True)
layout=json.loads((C/'device-layout.json').read_text('utf-8'));report=[]
for a in layout['assets']:
 for key in ['file','loop_file','outro_file']:
  if key not in a:continue
  old=C/a[key];stem=old.stem;entries=[];offset=0
  with Image.open(old)as im,(O/(stem+'.rgbz')).open('wb')as fp:
   for i in range(im.n_frames):
    im.seek(i);rgb=np.asarray(im.convert('RGB'),dtype=np.uint16)
    mask=np.any(rgb!=0,axis=2);ys,xs=np.where(mask)
    x0,y0,x1,y1=(int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)) if len(xs) else (0,0,1,1)
    crop=rgb[y0:y1,x0:x1]
    pixels=(((crop[:,:,0]>>3)<<11)|((crop[:,:,1]>>2)<<5)|(crop[:,:,2]>>3)).astype('<u2').tobytes()
    packed=zlib.compress(pixels,3);assert zlib.decompress(packed)==pixels
    fp.write(packed);entries.append([offset,len(packed),im.info['duration'],format(zlib.crc32(pixels),'08x'),x0,y0,x1-x0,y1-y0]);offset+=len(packed)
  meta={'width':200,'height':150,'frame_ms':40,'duration_ms':sum(x[2]for x in entries),'data':stem+'.rgbz','frames':entries}
  (O/(stem+'.json')).write_text(json.dumps(meta,separators=(',',':')),'utf-8')
  a[key]='assets/frames/'+stem+'.json';report.append({'clip':stem,'frames':len(entries),'bytes':offset})
 a['kind']='rgb565'
layout['version']='1.0.5'
(C/'frame-layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),'utf-8')
(R/'预览/验证/frame-export-report.json').write_text(json.dumps(report,indent=2),'utf-8')
print('Packed',len(report),'clips,',sum(x['frames']for x in report),'independent CRC-checked RGB565 frames;',sum(x['bytes']for x in report),'bytes')

# Reapply variants after rebuilding the base device frame manifest.
import runpy
runpy.run_path(str(Path(__file__).with_name('build_device_ramen.py')),run_name='__main__')
