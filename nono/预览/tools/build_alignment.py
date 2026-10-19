"""Windows-only source-space alignment. Never normalizes by full-body height.
Only the known crop mismatch changes scale; pose and face measurements never drive zoom.
All corrections are applied to the full RGBA canvas by the Windows renderer.
"""
from pathlib import Path
import json,hashlib
import numpy as np,cv2
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1]
mapping=json.loads((P/'windows-hd.json').read_text('utf-8'))
measure=json.loads((P/'验证/geometry-measurements.json').read_text('utf-8'))
def smooth(v,r=16):
 v=np.asarray(v,dtype=float);med=np.array([np.median(v[max(0,i-r):min(len(v),i+r+1)]) for i in range(len(v))]);return np.convolve(np.pad(med,(r,r),mode='edge'),np.ones(2*r+1)/(2*r+1),mode='valid')
output={};report={}
for key,path in mapping.items():
 raw=np.array(measure[key]);n=len(raw);meal='eat-' in key;base=512/552 if meal else 1.0
 # Geometry correction for the old 552-wide meal crop versus the shared 736-wide crop.
 # Both exports fitted into a 640x480 transparent canvas.
 bx=9.5072463768 if meal else 0
 # Keep one fixed scale throughout an activity: posture and facial expressions
 # must never drive automatic zoom. Correct only the known export crop mismatch.
 extra=np.ones(n);scale=base*extra
 # Anchor the measured character contact row, not the cat/laser or full-image bounds.
 floor=raw[:,1]
 if key=='assets/nono-game-outro.gif':
  # During rising, the contact detector switches between two shoes. Its
  # lowest pixel is not a stable camera anchor. Smooth only the correction,
  # preserving the source pose motion and the shared endpoint transforms.
  floor=smooth(floor,10)
  for endpoint in [0,n-1]:
   delta=raw[endpoint,1]-floor[endpoint]
   for j in range(20):
    t=j/19;weight=1-3*t*t+2*t*t*t
    idx=j if endpoint==0 else n-1-j
    floor[idx]+=delta*weight
 frames=np.column_stack([scale,extra*bx+350*(1-extra),459-scale*floor])
 output[key]={'sha256':hashlib.sha256((P/path).read_bytes()).hexdigest(),'frames':np.round(frames,6).tolist()}
 report[key]={'frames':n,'scale_min':float(scale.min()),'scale_max':float(scale.max()),'ground_before_range':float(np.ptp(raw[:,1])),'ground_after_range':float(np.ptp(raw[:,1]*scale+frames[:,2]))}
(P/'windows-alignment.json').write_text(json.dumps(output,separators=(',',':')),'utf-8')
(P/'验证/alignment-report.json').write_text(json.dumps(report,indent=2),'utf-8')
# Before/after comparison at the three independently sampled positions of each clip.
sheet=Image.new('RGB',(1200,len(mapping)*160),(45,50,55));draw=ImageDraw.Draw(sheet)
for row,(key,path) in enumerate(mapping.items()):
 with Image.open(P/path) as im:
  for col,i in enumerate([0,im.n_frames//2,im.n_frames-1]):
   im.seek(i);a=np.array(im.convert('RGBA'));s,x,y=output[key]['frames'][i];fixed=cv2.warpAffine(a,np.float32([[s,0,x],[0,s,y]]),(640,480),flags=cv2.INTER_LANCZOS4)
   for side,pic in enumerate([Image.fromarray(a),Image.fromarray(fixed)]):
    pic.thumbnail((200,150));sheet.paste(pic,(col*400+side*200,row*160),pic)
 draw.text((2,row*160),key.replace('assets/nono-','')+'  before | after',fill='white')
sheet.save(P/'验证/alignment-before-after.jpg')
print('Generated Windows alignment for',len(output),'clips; original GIFs untouched.',flush=True)
