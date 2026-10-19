"""Preserve the generated thin red beam during chroma-key downsampling.

No trajectory is invented: only existing long red components and their floor
endpoint are desaturated-green-corrected and alpha-resampled before quantization.
"""
import numpy as np
from PIL import Image,ImageFilter
import sequence_gif
base_fit=sequence_gif.fit
def perimeter(im):
 a=np.array(im);a[0]=0;a[-1]=0;a[:,0]=0;a[:,-1]=0
 return Image.fromarray(a)
def fit(im,size,crop):
 result=base_fit(im,size,crop)
 a=np.array(im).astype(np.int16);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
 red=(r>65)&(r>g+18)&(r>b+18)
 red[:275]=False;red[:,415:]=False
 grown=np.array(Image.fromarray(red.astype('uint8')*255).filter(ImageFilter.MaxFilter(3)))>0
 points=set(zip(*np.where(grown)));selected=np.zeros(red.shape,dtype=bool)
 while points:
  seed=points.pop();stack=[seed];component=[seed]
  while stack:
   y,x=stack.pop()
   for q in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
    if q in points:points.remove(q);stack.append(q);component.append(q)
  ys,xs=zip(*component);w=max(xs)-min(xs)+1;h=max(ys)-min(ys)+1
  is_ray=max(w,h)>45 and len(component)<max(w,h)*14
  is_dot=min(ys)>475 and 3<=w<=25 and 3<=h<=25
  if is_ray or is_dot:selected[tuple(np.array(component).T)]=True
 selected&=red
 if not selected.any():return perimeter(result)
 opaque=~((g-r>25)&(g-b>25));occupied=np.flatnonzero(opaque.sum(axis=1)>=8)
 shift=500-int(occupied[-1]) if len(occupied) else 0
 layer=np.zeros((*red.shape,4),dtype='uint8');layer[selected]=[255,24,24,255]
 source=Image.fromarray(layer);grounded=Image.new('RGBA',im.size);grounded.paste(source,(0,shift));source=grounded.crop(crop);source.thumbnail(size,Image.Resampling.LANCZOS)
 canvas=Image.new('RGBA',size);canvas.paste(source,((size[0]-source.width)//2,size[1]-source.height))
 line=np.array(canvas);keep=line[:,:,3]>=35
 out=np.array(result);out[keep]=[255,24,24,255]
 # The generated point's diffuse glow may touch the crop edge. Reserve one
 # transparent perimeter pixel; character silhouettes remain inside this area.
 return perimeter(Image.fromarray(out))
