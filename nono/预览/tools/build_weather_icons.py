from pathlib import Path
from PIL import Image,ImageDraw
import math
out=Path(__file__).resolve().parents[2]/'代码/assets/ui'
S=4
def icon(kind):
 im=Image.new('RGBA',(72,72));d=ImageDraw.Draw(im)
 def ellipse(box,fill):d.ellipse(tuple(round(v*S)for v in box),fill=fill)
 def line(points,fill,width=1):d.line([(round(x*S),round(y*S))for x,y in points],fill=fill,width=round(width*S))
 def sun(cx=9,cy=8):
  for i in range(8):
   a=i*math.pi/4;line([(cx+5*math.cos(a),cy+5*math.sin(a)),(cx+7*math.cos(a),cy+7*math.sin(a))],'#FFD568',1.2)
  ellipse((cx-3.5,cy-3.5,cx+3.5,cy+3.5),'#FFD568')
 def cloud():
  for box in [(2,7,10,13),(6,4,14,13),(10,7,17,13)]:ellipse(box,'#D2E8F3')
  d.rectangle((4*S,9*S,15*S,13*S),fill='#D2E8F3')
 if kind in ('sun','hot'):sun()
 elif kind=='partly':sun(6,5);cloud()
 elif kind=='cloud':cloud()
 elif kind in ('rain','storm','sleet','snow'):
  cloud()
  if kind=='storm':d.polygon([(10*S,11*S),(7*S,15*S),(10*S,15*S),(8*S,18*S),(14*S,13*S),(11*S,13*S)],fill='#FFE477')
  elif kind=='snow':
   for x in [5,12]:
    line([(x,14),(x,18)],'#B5EDFF');line([(x-2,16),(x+2,16)],'#B5EDFF');line([(x-1.5,14.5),(x+1.5,17.5)],'#B5EDFF')
  else:
   for x in [5,10,15]:line([(x,14),(x-2,17)],'#65CFFF',1.5)
   if kind=='sleet':ellipse((10,15,12,17),'#FFFFFF')
 elif kind in ('fog','dust'):
  color='#D8DCE1' if kind=='fog' else '#DFC087'
  for y in [5,9,13]:line([(2,y),(16,y)],color,1.5)
 elif kind=='cold':
  for i in range(6):
   a=i*math.pi/3;line([(9,9),(9+7*math.cos(a),9+7*math.sin(a))],'#A6E6FF',1.5)
 elif kind=='wind':
  for y in [5,9,13]:line([(2,y),(14,y),(16,y-2)],'#B5DCE7',1.3)
 else:
  ellipse((2,2,16,16),'#597385');line([(9,5),(9,10)],'#DBEEF4',1.5);ellipse((8.3,12,9.7,13.4),'#DBEEF4')
 im.resize((18,18),Image.Resampling.LANCZOS).save(out/('weather-'+kind+'.png'))
for kind in ['sun','partly','cloud','rain','storm','sleet','snow','fog','dust','hot','cold','wind','unknown']:icon(kind)
print('Built 13 transparent weather icons (18x18)')
