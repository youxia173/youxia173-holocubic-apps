"""Resume submitted ramen clips, inspect motion, and close their real endpoints."""
import json, sys, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw
import nono_video as api
import meal_bridges as mb

api.BASE='http://youxia173.myds.me:8888'
ROOT=Path(__file__).resolve().parent.parent/'完整拉面'
mb.OUT=ROOT/'bridges'
mb.OUT.mkdir(exist_ok=True)

def collect():
    for phase in ('intro','loop','outro','store'):
        folder=ROOT/phase
        if list(folder.glob('*.mp4')):
            print(phase,'downloaded');continue
        job=json.loads((folder/'job.json').read_text('utf-8'))
        item=api.request('/history/'+job['prompt_id']).get(job['prompt_id'])
        if not item:print(phase,'pending');continue
        (folder/'history.json').write_text(json.dumps(item,ensure_ascii=False,indent=2),'utf-8')
        if item['status']['status_str']!='success':raise RuntimeError(item['status'])
        for media in item['outputs']['18']['gifs']:
            if not media['filename'].endswith('.mp4'):continue
            query=urllib.parse.urlencode({k:media[k] for k in ('filename','subfolder','type')})
            with urllib.request.urlopen(api.BASE+'/view?'+query,timeout=120) as res:
                (folder/Path(media['filename']).name).write_bytes(res.read())
        print(phase,'downloaded')

def frames(phase):return mb.frames(next((ROOT/phase).glob('*.mp4')))

def contact():
    for phase in ('intro','loop','outro','store'):
        if not list((ROOT/phase).glob('*.mp4')):continue
        v=frames(phase);sheet=Image.new('RGB',(1280,4*230),(35,35,40));d=ImageDraw.Draw(sheet)
        for j in range(16):
            i=round(j*(len(v)-1)/15);im=v[i].copy();im.thumbnail((320,210));sheet.paste(im,(j%4*320,j//4*230));d.text((j%4*320+5,j//4*230+210),str(i),fill='white')
        sheet.save(ROOT/(phase+'-contact.jpg'))

def bridges():
    idle=Image.open(ROOT.parent/'完整睡眠/bridges/idle-close/frame-08.png').convert('RGB')
    ready=lambda phase:bool(list((ROOT/phase).glob('*.mp4')))
    if ready('loop'):
        v=frames('loop');mb.submit('close',v[-9],v[8])
    if ready('intro'):mb.submit('start',idle,frames('intro')[8])
    if ready('store'):
        mb.submit('end-store',frames('store')[-9],idle)
        mb.submit('store',frames('outro')[136],frames('store')[8])
    anchor=mb.OUT/'close/frame-08.png'
    if anchor.exists():
        a=Image.open(anchor).convert('RGB')
        if ready('intro'):mb.submit('enter',frames('intro')[-9],a)
        if ready('outro'):mb.submit('exit',a,frames('outro')[8])

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='collect':collect()
    elif mode=='contact':contact()
    elif mode=='bridges':bridges()
    elif mode=='collect-bridges':mb.collect()
    else:raise ValueError(mode)
