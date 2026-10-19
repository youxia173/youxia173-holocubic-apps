from delivery_paths import DELIVERY_ROOT
import json
import numpy as np
from PIL import Image
from sequence_gif import video,bridge,palette_for,save
from petting_revision import ROOT
DELIVERY=DELIVERY_ROOT / '诺诺-撸猫修正版'
CROP=(64,12,800,524)
def build(size):
 def v(name):return video(next((ROOT/name).glob('*.mp4')),size,CROP)
 def b(name):return bridge(ROOT/'bridges'/name,size,CROP)
 c=b('pet-close');loop=c[8:]+v('05-loop')[9:-9]+c[:9]
 intro=b('pet-start')
 names=['01-rub','02-crouch','03-grip','04-lift','04-settle','04-cradle']
 for i,name in enumerate(names):
  intro+=v(name)[9:-8]
  intro+=b(name+'-'+names[i+1] if i<len(names)-1 else 'pet-enter')[1:]
 outro=b('pet-exit');names=['06-lower','07-release','08-stand']
 for i,name in enumerate(names):
  outro+=v(name)[9:-8]
  outro+=b(name+'-'+names[i+1] if i<len(names)-1 else 'pet-end')[1:]
 sleep=ROOT.parent/'完整睡眠';c=bridge(sleep/'bridges/idle-close',size,CROP)
 idle=c[8:]+video(next((sleep/'06-idle').glob('*.mp4')),size,CROP)[9:152]+c[:9]
 for a,z in [(idle[-1],intro[0]),(intro[-1],loop[0]),(loop[-1],loop[0]),(loop[-1],outro[0]),(outro[-1],idle[0])]:assert np.array_equal(a,z)
 return intro,loop,outro,idle
if __name__=='__main__':
 DELIVERY.mkdir(exist_ok=True);facts={}
 for size in [(200,150),(640,480)]:
  seq=build(size);label=f'{size[0]}x{size[1]}'
  if size==(200,150):
   with Image.open(ROOT.parent.parent/'代码/assets/nono-idle-cat.gif') as im:
    colors=im.getpalette();palette=Image.new('P',(1,1));palette.putpalette(colors[:765]+colors[:3])
  else:palette=palette_for(seq)
  facts[label]={}
  for phase,frames in zip(['intro','loop','outro','idle'],seq):facts[label][phase]=save(DELIVERY/f'{phase}-{label}.gif',frames,palette,phase in ['loop','idle'])
  if size==(640,480):
   intro,loop,outro,idle=seq;facts[label]['full']=save(DELIVERY/'诺诺-完整撸猫-三圈.gif',idle+intro+loop*3+outro,palette,True)
 (DELIVERY/'时长信息.json').write_text(json.dumps(facts,indent=2),'utf-8');(ROOT/'export.json').write_text(json.dumps(facts,indent=2),'utf-8');print(facts)
