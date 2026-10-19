from pathlib import Path
import json,sys
from PIL import Image
app=Path(__file__).resolve().parents[2]
preview=app/'预览'; material=preview/'素材'; out=material/'Windows高清'
out.mkdir(exist_ok=True)
# Reuse only exporter function definitions, never its device installation steps.
script=preview/'连续喂饭/导出循环吃饭.py'
source=script.read_text('utf-8').split('intro, loop, outro = sequences((200,150))')[0]
source=source.replace("DELIVERY = Path('D:/Desktop/诺诺-可循环吃饭动画')", "DELIVERY = ROOT.parent / '素材' / 'Windows高清'")
ns={'__file__':str(script)};exec(compile(source,str(script),'exec'),ns)
if not (out/'eat-outro.gif').exists():
    seqs=ns['sequences']((640,480));palette=ns['palette_for'](seqs)
    for name,frames in zip(['intro','loop','outro'],seqs):
        ns['save'](out/f'eat-{name}.gif',frames,palette,name=='loop')
        print('Exported eating '+name,flush=True)
    del seqs
mapping={}
layout=json.loads((app/'代码/layout.json').read_text('utf-8'))
folders={'pet':'诺诺-撸猫修正版','laser':'诺诺-激光指向修正版','read':'诺诺-看书与游戏动画/看书','game':'诺诺-看书与游戏动画/打游戏'}
for a in [v for item in layout['assets'] for v in [item]+item.get('variants',[])]:
    for field,part in [('file','intro'),('loop_file','loop'),('outro_file','outro')]:
        if field not in a:continue
        if a['id']=='idle':p=material/'诺诺-激光指向修正版/idle-640x480.gif'
        elif a.get('variant')=='ramen':p=material/'诺诺-吃拉面动画'/f'{part}-640x480.gif'
        elif a['id']=='eat':p=out/f'eat-{part}.gif'
        elif a['id']=='sleep':p=material/'诺诺-完整睡眠动画'/('诺诺-'+{'intro':'入睡','loop':'睡眠循环','outro':'醒来'}[part]+'-透明-640x480.gif')
        else:p=material/folders[a['id']]/f'{part}-640x480.gif'
        with Image.open(p) as im:
            assert im.size==(640,480)
            count=im.n_frames;duration=0
            for i in range(count):im.seek(i);duration+=im.info['duration']
        prefix='' if field=='file' else part+'_'
        assert count==a[prefix+'frame_count'],(p,count)
        assert duration==a[prefix+'duration_ms'],(p,duration)
        mapping[a[field]]=str(p.relative_to(preview))
(preview/'windows-hd.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),'utf-8')
print(f'PASS: {len(mapping)} HD sequences match declared timing',flush=True)
