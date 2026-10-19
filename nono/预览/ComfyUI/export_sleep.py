from delivery_paths import DELIVERY_ROOT
"""Assemble sleep and matching idle; export alpha GIFs, preview, and runtime manifest."""
import json
from pathlib import Path
import numpy as np
from sequence_gif import video,bridge,palette_for,save

ROOT=Path(__file__).resolve().parent.parent/'完整睡眠'
CODE=ROOT.parent.parent/'代码'
DELIVERY=DELIVERY_ROOT / '诺诺-完整睡眠动画'
DELIVERY.mkdir(exist_ok=True)
# Wider than the meal crop: lying down must include both the cat and the shoes.
CROP=(64,12,800,524)

def build(size):
    def v(name):return video(next((ROOT/name).glob('*.mp4')),size,CROP)
    def b(name):return bridge(ROOT/'bridges'/name,size,CROP)
    def loop(name,close):
        c=b(close)
        return c[8:]+v(name)[9:152]+c[:9]
    idle=loop('06-idle','idle-close')
    sleep=loop('03-sleep-clean','sleep-close')
    intro=b('idle-sit')+v('01-sit')[9:153]+b('sit-lie')[1:]+v('02-lie')[9:153]+b('enter-sleep')[1:]
    outro=b('exit-sleep')+v('04-wake')[9:153]+b('wake-stand')[1:]+v('05-stand')[9:153]+b('stand-idle')[1:]
    for left,right in [(idle[-1],idle[0]),(idle[-1],intro[0]),(intro[-1],sleep[0]),(sleep[-1],sleep[0]),(sleep[-1],outro[0]),(outro[-1],idle[0])]:
        assert np.array_equal(left,right),'Nonmatching endpoint'
    return intro,sleep,outro,idle

if __name__=='__main__':
    sequences=build((200,150));palette=palette_for(sequences);facts={}
    for name,frames in zip(['intro','loop','outro','idle'],sequences):
        filename='nono-idle-cat.gif' if name=='idle' else f'nono-sleep-{name}.gif'
        facts[name]=save(CODE/'assets'/filename,frames,palette,name in ['idle','loop'])
        (DELIVERY/filename).write_bytes((CODE/'assets'/filename).read_bytes())
    intro,loop,outro,idle=sequences
    save(DELIVERY/'诺诺-完整睡眠-三圈示例.gif',idle+intro+loop*3+outro,palette,True)
    large=build((640,480));large_palette=palette_for(large)
    for name,frames in zip(['入睡','睡眠循环','醒来','白猫待机'],large):
        save(DELIVERY/f'诺诺-{name}-透明-640x480.gif',frames,large_palette,name in ['睡眠循环','白猫待机'])
    layout=json.loads((CODE/'layout.json').read_text('utf-8'))
    layout['version']='0.3.0'
    for a in layout['assets']:
        if a['id']=='eat':a['loop_seconds']=layout.get('meal_seconds',30)
        if a['id']=='idle':a.update(file='assets/nono-idle-cat.gif',**facts['idle'])
        if a['id']=='sleep':
            a.update(file='assets/nono-sleep-intro.gif',loop_file='assets/nono-sleep-loop.gif',outro_file='assets/nono-sleep-outro.gif',
                     return_activity='idle',loop_seconds=60,title='诺诺 · 睡觉（完整流程，可设时长）',**facts['intro'],
                     loop_duration_ms=facts['loop']['duration_ms'],loop_frame_count=facts['loop']['frame_count'],
                     outro_duration_ms=facts['outro']['duration_ms'],outro_frame_count=facts['outro']['frame_count'])
    (CODE/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),'utf-8')
    (ROOT/'export.json').write_text(json.dumps(facts,indent=2),'utf-8')
    print(json.dumps(facts),flush=True)
