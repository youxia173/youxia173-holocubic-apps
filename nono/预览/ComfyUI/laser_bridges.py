import sys
from PIL import Image
import meal_bridges as mb
from laser_sequence import ROOT
mb.OUT=ROOT/'bridges';mb.OUT.mkdir(parents=True,exist_ok=True)
def ready(name):return bool(list((ROOT/name).glob('*.mp4')))
def frames(name):return mb.frames(next((ROOT/name).glob('*.mp4')))
def submit():
 idle=Image.open(ROOT.parent/'完整睡眠/bridges/idle-close/frame-08.png').convert('RGB')
 if ready('laser-intro'):mb.submit('start',idle,frames('laser-intro')[8])
 if ready('laser-intro') and ready('laser-on'):mb.submit('on',frames('laser-intro')[-9],frames('laser-on')[8])
 if ready('laser-outro'):mb.submit('end',frames('laser-outro')[-9],idle)
 if ready('laser-left') and ready('laser-right'):
  left=frames('laser-left');right=frames('laser-right')
  mb.submit('turn',left[-9],right[8]);mb.submit('close',right[-9],left[8])
 anchor=mb.OUT/'close/frame-08.png'
 if anchor.exists():
  a=Image.open(anchor).convert('RGB')
  if ready('laser-on'):mb.submit('enter',frames('laser-on')[-9],a)
  if ready('laser-outro'):mb.submit('exit',a,frames('laser-outro')[8])
if __name__=='__main__':
 if sys.argv[1]=='submit':submit()
 else:mb.collect()
