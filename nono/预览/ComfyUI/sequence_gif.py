"""Video-to-transparent-GIF helpers; one coordinate system and palette per sequence."""
import numpy as np
from PIL import Image
import imageio_ffmpeg as ff

def fit(im, size, crop):
    # The image model may shift the shared ground between poses. Translate the
    # entire frame (never individual body parts) to a fixed contact baseline.
    raw=np.array(im).astype(np.int16)
    opaque=~(((raw[:,:,1]-raw[:,:,0])>25)&((raw[:,:,1]-raw[:,:,2])>25))
    occupied=np.flatnonzero(opaque.sum(axis=1)>=8)
    if len(occupied):
        shift=500-int(occupied[-1])
        grounded=Image.new('RGB',im.size,(0,255,0))
        grounded.paste(im,(0,shift));im=grounded
    im=im.crop(crop)
    im.thumbnail(size,Image.Resampling.LANCZOS)
    canvas=Image.new('RGB',size,(0,255,0))
    canvas.paste(im,((size[0]-im.width)//2,size[1]-im.height))
    a=np.array(canvas).astype(np.int16)
    key=((a[:,:,1]-a[:,:,0])>25)&((a[:,:,1]-a[:,:,2])>25)
    rgba=np.dstack([a.astype(np.uint8),np.where(key,0,255).astype(np.uint8)])
    rgba[key,:3]=0
    return Image.fromarray(rgba)

def video(path,size,crop):
    reader=ff.read_frames(str(path));meta=next(reader)
    assert meta['size']==(832,560),meta['size']
    return [fit(Image.frombytes('RGB',meta['size'],b),size,crop) for b in reader]

def bridge(folder,size,crop):
    files=sorted(folder.glob('frame-*.png'))
    assert len(files)==17,(folder,len(files))
    return [fit(Image.open(p).convert('RGB'),size,crop) for p in files]

def palette_for(sequences):
    samples=[im.resize((100,75)) for seq in sequences for im in seq[::8]]
    sheet=Image.new('RGB',(1000,75*((len(samples)+9)//10)))
    for i,im in enumerate(samples):sheet.paste(im.convert('RGB'),((i%10)*100,(i//10)*75))
    palette=sheet.quantize(colors=255,method=Image.Quantize.MEDIANCUT)
    colors=palette.getpalette()
    palette.putpalette(colors[:765]+colors[:3])
    return palette

def save(path,frames,palette,loop=False):
    indexed=[]
    for im in frames:
        a=np.array(im)
        q=im.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE)
        indices=np.array(q)
        # Quantization may select reserved index 255, which duplicates index 0.
        # Remap it before applying alpha so dark opaque outlines never vanish.
        indices[indices==255]=0
        indices[a[:,:,3]==0]=255
        q=Image.fromarray(indices,'P');q.putpalette(palette.getpalette()[:765]+[0,0,0]);indexed.append(q)
    delays=[int(round((i+1)*100/32)-round(i*100/32))*10 for i in range(len(frames))]
    options=dict(save_all=True,append_images=indexed[1:],duration=delays,transparency=255,disposal=2,optimize=False)
    if loop:options['loop']=0
    indexed[0].save(path,**options)
    with Image.open(path) as gif:
        total=0
        for i in range(gif.n_frames):gif.seek(i);total+=gif.info['duration']
        return dict(frame_count=gif.n_frames,duration_ms=total)
