from pathlib import Path
import json,numpy as np,cv2
from PIL import Image
p=Path('youxia173-apps/nono/预览');m=json.loads((p/'windows-hd.json').read_text('utf-8'));result={}
for key,path in m.items():
 vals=[]
 with Image.open(p/path) as im:
  for i in range(im.n_frames):
   im.seek(i);a=np.array(im.convert('RGBA'));r,g,b=[a[:,:,j].astype('int16') for j in range(3)]
   mask=((r-g>3)&(r-b>5)&(r>140)&(g>100)&(a[:,:,3]>128)).astype('uint8');mask[:,:240]=0;mask[:,450:]=0;mask[370:]=0
   mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8));n,l,stats,cent=cv2.connectedComponentsWithStats(mask)
   candidates=[v for v in stats[1:] if v[4]>150 and v[2]>20 and v[3]>15];face=max(candidates,key=lambda v:v[4]) if candidates else [0,0,0,0,0]
   solid=(a[:,:,3]>128)&~((r>g*1.4)&(r>b*1.4));region=solid[:,280:430] if "laser" in key or "idle" in key else solid[:,230:560];ys=np.where(region.any(axis=1))[0];foot=float(ys[-1]) if len(ys) else 456
   vals.append([int(face[2]),float(foot),int(face[0]),int(face[1])])
 result[key]=vals
 print(key,np.percentile(np.array(vals)[:,:2],[0,50,100],axis=0).round(1).tolist(),flush=True)
(p/'验证/geometry-measurements.json').write_text(json.dumps(result),'utf-8')

