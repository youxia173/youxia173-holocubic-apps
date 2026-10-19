"""Export ramen with shared cyclic joins, existing idle colors, and fixed camera scale."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image
from sequence_gif import video,bridge,palette_for
from ramen_sequence import ROOT

PREVIEW=ROOT.parent
OUT=PREVIEW/'素材/诺诺-吃拉面动画'
CROP=(64,12,800,524)

def save(path,frames,palette,loop=False):
    colors=np.array(palette.getpalette()[:765],dtype=np.uint32).reshape(-1,3)
    keys,slots=np.unique((colors[:,0]<<16)|(colors[:,1]<<8)|colors[:,2],return_index=True)
    indexed=[]
    for im in frames:
        a=np.array(im);rgb=a[:,:,:3].astype(np.uint32)
        packed=(rgb[:,:,0]<<16)|(rgb[:,:,1]<<8)|rgb[:,:,2]
        q=im.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE)
        indices=np.array(q);indices[indices==255]=0
        # Pillow's quantizer uses a coarse lookup; force exact existing palette
        # colors so idle boundary pixels cannot shift even by one channel level.
        found=np.minimum(np.searchsorted(keys,packed),len(keys)-1)
        exact=keys[found]==packed;indices[exact]=slots[found[exact]]
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

def build(size):
    def v(phase):return video(next((ROOT/phase).glob('*.mp4')),size,CROP)
    def b(name):return bridge(ROOT/'bridges'/name,size,CROP)
    c=b('close')
    loop=c[8:]+v('loop')[9:-9]+c[:9]
    intro=b('start')+v('intro')[9:-8]+b('enter')[1:]
    outro=b('exit')+v('outro')[9:137]+b('store')[1:]+v('store')[9:-8]+b('end-store')[1:]
    # Force the installed idle's decoded anchor, preserving its actual palette.
    mapping=json.loads((PREVIEW/'windows-hd.json').read_text('utf-8'))
    path=PREVIEW/mapping['assets/nono-idle-cat.gif'] if size==(640,480) else PREVIEW.parent/'代码/assets/nono-idle-cat.gif'
    with Image.open(path) as im:
        anchor=im.convert('RGBA');idle=[]
        for i in range(im.n_frames):im.seek(i);idle.append(im.convert('RGBA'))
    intro[0]=anchor.copy();outro[-1]=anchor.copy()
    # Use constant scale. Only correct the grounded character's contact row.
    # Do not derive zoom from the height of a seated pose or from the cat.
    if size==(640,480):
        for seq in (intro,loop,outro):
            for i,im in enumerate(seq):
                a=np.array(im);region=a[:,230:560,3]>128
                rows=np.flatnonzero(region.sum(axis=1)>=3)
                if not len(rows):raise ValueError('Missing character contact')
                dy=459-int(rows[-1]);canvas=Image.new('RGBA',size)
                canvas.paste(im,(0,dy));seq[i]=canvas
        intro[0]=anchor.copy();outro[-1]=anchor.copy()
    for x,y in [(intro[-1],loop[0]),(loop[-1],loop[0]),(loop[-1],outro[0])]:
        assert np.array_equal(x,y),'Nonidentical boundary'
    return intro,loop,outro,idle,path

def palette_with_idle(seqs,path):
    with Image.open(path) as im:
        used=set(np.array(im).ravel())-{255};colors=im.getpalette()[:768]
    extra=palette_for(seqs).getpalette()
    warm=[extra[i:i+3] for i in range(0,765,3) if extra[i]>extra[i+2]+25 and extra[i+1]>extra[i+2]+10]
    free=[i for i in range(255) if i not in used]
    for slot,color in zip(free,warm):colors[slot*3:slot*3+3]=color
    palette=Image.new('P',(1,1));palette.putpalette(colors[:765]+colors[:3]);return palette

def export():
    OUT.mkdir(parents=True,exist_ok=True);facts={}
    for size in [(200,150),(640,480)]:
        intro,loop,outro,idle,path=build(size);seqs=[intro,loop,outro,idle]
        palette=palette_with_idle(seqs,path);label='%sx%s'%size;facts[label]={}
        for phase,frames in zip(['intro','loop','outro'],seqs):
            facts[label][phase]=save(OUT/(phase+'-'+label+'.gif'),frames,palette,phase=='loop')
        if size==(640,480):
            facts[label]['full']=save(OUT/'诺诺-吃拉面-完整流程-三圈.gif',idle+intro+loop*3+outro,palette,True)
        print(label,facts[label],flush=True)
    (OUT/'时长与接入信息.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2),'utf-8')
    (ROOT/'export.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2),'utf-8')

if __name__=='__main__':export()
