import sys
from PIL import Image
import meal_bridges as mb
from petting_sequence import ROOT
mb.OUT=ROOT/'bridges';mb.OUT.mkdir(parents=True,exist_ok=True)
def frames(name):return mb.frames(next((ROOT/name).glob('*.mp4')))
def ready(name):return bool(list((ROOT/name).glob('*.mp4')))
def submit():
 idle=Image.open(ROOT.parent/'完整睡眠/bridges/idle-close/frame-08.png').convert('RGB')
 if ready('01-rub'):mb.submit('pet-start',idle,frames('01-rub')[8])
 if ready('06-stand'):mb.submit('pet-end',frames('06-stand')[-9],idle)
 for left,right in [('01-rub','02-crouch'),('02-crouch','03-lift'),('05-lower','06-stand')]:
  if ready(left) and ready(right):mb.submit(left+'-'+right,frames(left)[-9],frames(right)[8])
 if ready('04-loop'):
  v=frames('04-loop');mb.submit('pet-close',v[-9],v[8])
 anchor=mb.OUT/'pet-close/frame-08.png'
 if anchor.exists():
  a=Image.open(anchor).convert('RGB')
  if ready('03-lift'):mb.submit('pet-enter',frames('03-lift')[-9],a)
  if ready('05-lower'):mb.submit('pet-exit',a,frames('05-lower')[8])
if __name__=='__main__':
 if sys.argv[1]=='submit':submit()
 else:mb.collect()
