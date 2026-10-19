import sys
from PIL import Image
import meal_bridges as mb
from petting_revision import ROOT
mb.OUT=ROOT/'bridges';mb.OUT.mkdir(exist_ok=True)
def ready(name):return bool(list((ROOT/name).glob('*.mp4')))
def frames(name):return mb.frames(next((ROOT/name).glob('*.mp4')))
def submit():
 for left,right in [('02-crouch','03-grip'),('03-grip','04-lift'),('04-lift','04-settle'),('04-settle','04-cradle'),('06-lower','07-release'),('07-release','08-stand')]:
  if ready(left) and ready(right):mb.submit(left+'-'+right,frames(left)[-9],frames(right)[8])
 if ready('05-loop'):
  v=frames('05-loop');mb.submit('pet-close',v[-9],v[8])
 anchor=mb.OUT/'pet-close/frame-08.png'
 if anchor.exists():
  a=Image.open(anchor).convert('RGB')
  if ready('04-cradle'):mb.submit('pet-enter',frames('04-cradle')[-9],a)
  if ready('06-lower'):mb.submit('pet-exit',a,frames('06-lower')[8])
if __name__=='__main__':
 if sys.argv[1]=='submit':submit()
 else:mb.collect()
