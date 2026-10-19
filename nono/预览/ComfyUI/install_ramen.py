"""Install validated ramen as a Windows meal variant, keeping Cubic frame-layout unchanged."""
import json,hashlib,shutil,sys
from pathlib import Path
import numpy as np
from PIL import Image
from export_ramen import OUT,ROOT,PREVIEW

app=PREVIEW.parent
def write(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf-8')
facts=json.loads((OUT/'时长与接入信息.json').read_text('utf-8'))
for size in ['200x150','640x480']:
    report=json.loads((ROOT/('validation-'+size+'.json')).read_text('utf-8'))
    assert report['ok'],report['errors']
layout=json.loads((app/'代码/layout.json').read_text('utf-8'))
eat=next(a for a in layout['assets'] if a['id']=='eat');eat['variant']='rice'
ramen={k:v for k,v in eat.items() if k!='variants'}
ramen.update(variant='ramen',title='诺诺 · 吃拉面（进食随机）')
mapping=json.loads((PREVIEW/'windows-hd.json').read_text('utf-8'))
alignment=json.loads((PREVIEW/'windows-alignment.json').read_text('utf-8'))
geometry=json.loads((PREVIEW/'验证/geometry-measurements.json').read_text('utf-8'))
for phase,field,prefix in [('intro','file',''),('loop','loop_file','loop_'),('outro','outro_file','outro_')]:
    key='assets/nono-ramen-'+phase+'.gif';ramen[field]=key
    for name in ['duration_ms','frame_count']:ramen[prefix+name]=facts['200x150'][phase][name]
    assert facts['640x480'][phase]==facts['200x150'][phase],'HD timing mismatch'
    shutil.copy2(OUT/(phase+'-200x150.gif'),app/'代码'/key)
    hd=OUT/(phase+'-640x480.gif');mapping[key]=hd.relative_to(PREVIEW).as_posix()
    with Image.open(hd) as im:
        rows=[]
        for i in range(im.n_frames):
            im.seek(i);a=np.array(im.convert('RGBA'));ys=np.flatnonzero((a[:,230:560,3]>128).sum(axis=1)>=3)
            rows.append([0,int(ys[-1]),0,0])
    geometry[key]=rows
    alignment[key]={'sha256':hashlib.sha256(hd.read_bytes()).hexdigest(),'frames':[[1,0,0] for _ in rows]}
eat['variants']=[ramen]
write(app/'代码/layout.json',layout);write(PREVIEW/'windows-hd.json',mapping)
write(PREVIEW/'windows-alignment.json',alignment);write(PREVIEW/'验证/geometry-measurements.json',geometry)
print('Installed ramen variant; original meals and device frame-layout preserved.')
