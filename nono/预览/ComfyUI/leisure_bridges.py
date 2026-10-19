"""Connect actual generated poses to the existing shared idle and each cyclic anchor."""
import sys
from PIL import Image
import meal_bridges as mb
from leisure_sequence import ROOT
mb.OUT=ROOT/'bridges';mb.OUT.mkdir(exist_ok=True)
IDLE=ROOT.parent/'完整睡眠/bridges/idle-close/frame-08.png'
def frames(name):return mb.frames(next((ROOT/name).glob('*.mp4')))
def submit():
 idle=Image.open(IDLE).convert('RGB')
 for activity in ('read','game'):
  for phase in ('intro','loop','outro'):
   if not list((ROOT/f'{activity}-{phase}').glob('*.mp4')):continue
   v=frames(f'{activity}-{phase}')
   if phase=='loop':mb.submit(activity+'-close',v[-9],v[8])
   if phase=='intro':mb.submit(activity+'-start',idle,v[8])
   if phase=='outro':mb.submit(activity+'-end',v[-9],idle)
  anchor=mb.OUT/f'{activity}-close/frame-08.png'
  if anchor.exists():
   a=Image.open(anchor).convert('RGB')
   for phase,name in [('intro','enter'),('outro','exit')]:
    if list((ROOT/f'{activity}-{phase}').glob('*.mp4')):
     v=frames(f'{activity}-{phase}')
     mb.submit(activity+'-'+name,v[-9] if phase=='intro' else a,a if phase=='intro' else v[8])
if __name__=='__main__':
 if sys.argv[1]=='submit':submit()
 else:mb.collect()
