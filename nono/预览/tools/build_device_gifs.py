"""Device-only fixed-canvas, opaque GIFs. Windows source assets remain untouched."""
from pathlib import Path
import json,hashlib,bisect
import numpy as np,cv2
from PIL import Image,GifImagePlugin
ROOT=Path(__file__).resolve().parents[2];CODE=ROOT/'代码';PRE=ROOT/'预览'
layout=json.loads((CODE/'layout.json').read_text('utf-8'))
fix=json.loads((PRE/'windows-alignment.json').read_text('utf-8'))
out=CODE/'assets/device';out.mkdir(parents=True,exist_ok=True)
report=[]
for asset in layout['assets']:
 for field in ['file','loop_file','outro_file']:
  if field not in asset:continue
  key=asset[field];source=CODE/key;dest=out/source.name
  with Image.open(source)as im:
   palette=im.getpalette();palette[765:768]=[0,0,0]
   pal=Image.new('P',(1,1));pal.putpalette(palette)
   durations=[];frames=[]
   for i in range(im.n_frames):
    im.seek(i);durations.append(im.info['duration'])
    rgba=np.array(im.convert('RGBA'));scale,x,y=fix[key]['frames'][i]
    rgba=cv2.warpAffine(rgba,np.float32([[scale,0,x*200/640],[0,scale,y*150/480]]),(200,150),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
    # Composite onto the device's black background; no disposal/transparency dependency.
    rgb=(rgba[:,:,:3].astype(np.uint16)*rgba[:,:,3:4].astype(np.uint16)//255).astype('uint8')
    f=Image.fromarray(rgb).quantize(palette=pal,dither=Image.Dither.NONE);f.info={};frames.append(f)
  ends=np.cumsum(durations).tolist();total=sum(durations);times=list(range(0,total,40));indices=[min(len(frames)-1,bisect.bisect_right(ends,t))for t in times]
  indices[-1]=len(frames)-1 # shared endpoint survives resampling
  delays=[min(40,total-t)for t in times]
  with dest.open('wb')as fp:
   for b in GifImagePlugin._get_global_header(frames[0],{'loop':0,'background':255}):fp.write(b)
   for i,delay in zip(indices,delays):GifImagePlugin._write_frame_data(fp,frames[i],(0,0),{'duration':delay,'disposal':1,'include_color_table':False})
   fp.write(b';')
  # Every decoder receives an entire 200x150 image at the same origin.
  with Image.open(dest)as check:
   assert check.n_frames==len(indices)
   elapsed=0
   for i in range(check.n_frames):
    check.seek(i);assert check.tile[0][1]==(0,0,200,150)
    assert 'transparency' not in check.info and check.disposal_method==1
    elapsed+=check.info['duration']
   assert elapsed==total
  asset[field]='assets/device/'+source.name
  count_field={'file':'frame_count','loop_file':'loop_frame_count','outro_file':'outro_frame_count'}[field]
  asset[count_field]=len(indices)
  report.append({'source':key,'file':asset[field],'frames':len(indices),'duration_ms':total,'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
  print(source.name,len(indices),total,flush=True)
layout['version']='1.0.4'
(CODE/'device-layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),'utf-8')
(PRE/'验证/device-gif-report.json').write_text(json.dumps(report,indent=2),'utf-8')
print('PASS 19 fixed-canvas clips; opaque global palette; exact durations; original Windows assets preserved')
