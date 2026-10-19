from delivery_paths import DELIVERY_ROOT
import json
import numpy as np
from PIL import Image
from sequence_gif import video,bridge,palette_for,save
from laser_sequence import ROOT
DELIVERY=DELIVERY_ROOT / '诺诺-激光逗猫动画'
CROP=(64,12,800,524)
def build(size):
 def v(name):return video(next((ROOT/('laser-'+name)).glob('*.mp4')),size,CROP)
 def b(name):return bridge(ROOT/'bridges'/name,size,CROP)
 c=b('close');loop=c[8:]+v('left')[9:-9]+b('turn')+v('right')[9:-9]+c[:9]
 intro=b('start')+v('intro')[9:-8]+b('on')[1:]+v('on')[9:-8]+b('enter')[1:]
 outro=b('exit')+v('outro')[9:-8]+b('end')[1:]
 sleep=ROOT.parent/'完整睡眠';c=bridge(sleep/'bridges/idle-close',size,CROP)
 idle=c[8:]+video(next((sleep/'06-idle').glob('*.mp4')),size,CROP)[9:-9]+c[:9]
 for a,z in [(idle[-1],intro[0]),(intro[-1],loop[0]),(loop[-1],loop[0]),(loop[-1],outro[0]),(outro[-1],idle[0])]:assert np.array_equal(a,z)
 return intro,loop,outro,idle
if __name__=='__main__':
 DELIVERY.mkdir(exist_ok=True);facts={}
 for size in [(200,150),(640,480)]:
  seq=build(size);label=f'{size[0]}x{size[1]}'
  if size==(200,150):
   with Image.open(ROOT.parent.parent/'代码/assets/nono-idle-cat.gif') as old:
    used=set(np.array(old).ravel());colors=old.getpalette()[:765]
    free=[i for i in range(255) if i not in used]
    assert free,'Need a free palette slot for laser red without changing idle boundary'
    colors[free[0]*3:free[0]*3+3]=[255,24,24]
    palette=Image.new('P',(1,1));palette.putpalette(colors+colors[:3])
  else:palette=palette_for(seq)
  facts[label]={}
  for phase,frames in zip(['intro','loop','outro','idle'],seq):facts[label][phase]=save(DELIVERY/f'{phase}-{label}.gif',frames,palette,phase in ['loop','idle'])
  if size==(640,480):
   intro,loop,outro,idle=seq;facts[label]['full']=save(DELIVERY/'诺诺-激光逗猫-三圈.gif',idle+intro+loop*3+outro,palette,True)
 (DELIVERY/'时长信息.json').write_text(json.dumps(facts,indent=2),'utf-8');(ROOT/'export.json').write_text(json.dumps(facts,indent=2),'utf-8');print(facts)
