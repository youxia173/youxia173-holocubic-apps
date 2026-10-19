from delivery_paths import DELIVERY_ROOT
"""Export standalone reading/gaming delivery, retaining installed app unchanged."""
import json,sys
from pathlib import Path
import numpy as np
from sequence_gif import video,bridge,palette_for,save
from leisure_sequence import ROOT
DELIVERY=DELIVERY_ROOT / '诺诺-看书与游戏动画'
CROP=(64,12,800,524)
def build(activity,size):
 def v(phase):return video(next((ROOT/f'{activity}-{phase}').glob('*.mp4')),size,CROP)
 def b(name):return bridge(ROOT/'bridges'/f'{activity}-{name}',size,CROP)
 c=b('close');loop=c[8:]+v('loop')[9:152]+c[:9]
 intro=b('start')+v('intro')[9:153]+b('enter')[1:]
 outro=b('exit')+v('outro')[9:153]+b('end')[1:]
 sleep=ROOT.parent/'完整睡眠';c=bridge(sleep/'bridges/idle-close',size,CROP)
 idle=c[8:]+video(next((sleep/'06-idle').glob('*.mp4')),size,CROP)[9:152]+c[:9]
 for a,z in [(idle[-1],intro[0]),(intro[-1],loop[0]),(loop[-1],loop[0]),(loop[-1],outro[0]),(outro[-1],idle[0])]:assert np.array_equal(a,z),'join mismatch'
 return intro,loop,outro,idle
def export(activity):
 title={'read':'看书','game':'打游戏'}[activity];out=DELIVERY/title;out.mkdir(parents=True,exist_ok=True)
 facts={}
 for size in [(200,150),(640,480)]:
  seq=build(activity,size);palette=palette_for(seq);label=f'{size[0]}x{size[1]}'
  facts[label]={}
  for phase,frames in zip(['intro','loop','outro','idle'],seq):
   facts[label][phase]=save(out/f'{phase}-{label}.gif',frames,palette,phase in ('loop','idle'))
  intro,loop,outro,idle=seq
  if size==(640,480):facts[label]['full']=save(out/f'诺诺-{title}-完整流程-三圈.gif',idle+intro+loop*3+outro,palette,True)
 (out/'时长与接入信息.json').write_text(json.dumps({'activity':activity,'title':title,'sizes':facts,'repeat_rule':'ceil(seconds * 1000 / loop.duration_ms)','order':['idle','intro','loop × N','outro','idle']},ensure_ascii=False,indent=2),'utf-8')
 (ROOT/f'{activity}-export.json').write_text(json.dumps(facts,indent=2),'utf-8');print(activity,facts,flush=True)
if __name__=='__main__':
 for a in sys.argv[1:] or ['read','game']:export(a)
