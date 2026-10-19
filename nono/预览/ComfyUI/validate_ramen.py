"""Run skill validation plus installed-idle and fixed-ground regressions."""
import json,sys,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from export_ramen import ROOT,OUT,PREVIEW
sys.path.insert(0,str(Path.home()/'.codex/skills/nono-animation-workflow/scripts'))
from validate_sequence import validate

def pixels(path,index=0):
    with Image.open(path) as im:
        im.seek(index);rgba=im.convert('RGBA')
        clear=Image.new('RGBA',im.size);clear.paste(rgba,(0,0),rgba.getchannel('A'));return clear.tobytes()

for size in ['200x150','640x480']:
    report=validate(*[OUT/(phase+'-'+size+'.gif') for phase in ['intro','loop','outro']])
    (ROOT/('validation-'+size+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
    assert report['ok'],report['errors']
    mapping=json.loads((PREVIEW/'windows-hd.json').read_text('utf-8'))
    idle=PREVIEW/mapping['assets/nono-idle-cat.gif'] if size=='640x480' else PREVIEW.parent/'代码/assets/nono-idle-cat.gif'
    assert pixels(OUT/('intro-'+size+'.gif'))==pixels(idle),'Idle to intro mismatch'
    with Image.open(OUT/('outro-'+size+'.gif')) as im:last=im.n_frames-1
    assert pixels(OUT/('outro-'+size+'.gif'),last)==pixels(idle),'Outro to idle mismatch'
    print('PASS',size,'transparent, animated, cyclic, joins and exact installed-idle endpoints')

original=json.loads((ROOT/'原动画SHA256.json').read_text('utf-8'))
mapping=json.loads((PREVIEW/'windows-hd.json').read_text('utf-8'))
for key,expected in original.items():assert hashlib.sha256((PREVIEW/mapping[key]).read_bytes()).hexdigest()==expected
print('PASS: original animations unchanged')
