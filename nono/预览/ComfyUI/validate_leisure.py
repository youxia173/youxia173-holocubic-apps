"""Validate decoded outputs and create three-background visual QA sheets."""
import sys,json,importlib.util
import numpy as np
from PIL import Image,ImageDraw
from export_leisure import DELIVERY
spec=importlib.util.spec_from_file_location('validator','C:/Users/youxia173/.codex/skills/nono-animation-workflow/scripts/validate_sequence.py');validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)
reports=[]
def decoded(path,index):
 with Image.open(path) as im:
  im.seek(index if index>=0 else im.n_frames+index);rgba=im.convert('RGBA');a=np.array(rgba);a[a[:,:,3]==0,:3]=0;return a
for title in ['看书','打游戏']:
 folder=DELIVERY/title
 for size in ['200x150','640x480']:
  r=validator.validate(*(folder/f'{p}-{size}.gif' for p in ['intro','loop','outro']))
  r['joins']['idle_to_intro']=np.array_equal(decoded(folder/f'idle-{size}.gif',-1),decoded(folder/f'intro-{size}.gif',0))
  r['joins']['outro_to_idle']=np.array_equal(decoded(folder/f'outro-{size}.gif',-1),decoded(folder/f'idle-{size}.gif',0))
  r['ok']=r['ok'] and all(r['joins'].values());reports.append(r);assert r['ok'],r
 sheet=Image.new('RGB',(1280,3*290),'#dae1eb');draw=ImageDraw.Draw(sheet)
 for row,bg in enumerate(['#ffffff','#172132','checker']):
  for col,(phase,idx) in enumerate([('intro',80),('loop',40),('loop',120),('outro',85)]):
   tile=Image.new('RGBA',(320,240),bg if bg!='checker' else '#edf0f4')
   if bg=='checker':
    d=ImageDraw.Draw(tile)
    for x in range(0,320,16):
     for y in range(0,240,16):
      if (x//16+y//16)%2:d.rectangle((x,y,x+15,y+15),fill='#b8c3d2')
   im=Image.fromarray(decoded(folder/f'{phase}-640x480.gif',idx)).resize((320,240),Image.Resampling.LANCZOS);tile.alpha_composite(im)
   sheet.paste(tile.convert('RGB'),(col*320,row*290));draw.text((col*320+8,row*290+250),f'{phase} frame {idx} / {bg}',fill='black')
 sheet.save(folder/'透明背景检查.jpg',quality=92)
(DELIVERY/'验证报告.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),'utf-8')
print('PASS: 4 sequences, alpha and all 5 joins; three-cycle full GIFs exported.')
