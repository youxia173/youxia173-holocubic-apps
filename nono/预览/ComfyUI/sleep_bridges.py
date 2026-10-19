"""Submit only available, not-yet-submitted sleep seam jobs; resume with collect."""
import sys
from pathlib import Path
from PIL import Image
import meal_bridges as bridge

ROOT=Path(__file__).resolve().parent.parent/'完整睡眠'
bridge.OUT=ROOT/'bridges'
bridge.OUT.mkdir(exist_ok=True)

def clip(name):
    path=next((ROOT/name).glob('*.mp4'),None)
    return bridge.frames(path) if path else None

def pair(name,left,right):
    if (bridge.OUT/name/'job.json').exists():return
    a=clip(left)
    if a is None:return
    first=a[-9];del a
    b=clip(right)
    if b is not None:bridge.submit(name,first,b[8])

def anchor(name):
    path=bridge.OUT/name/'frame-08.png'
    return Image.open(path).convert('RGB') if path.exists() else None

if __name__=='__main__':
    if sys.argv[1]=='collect':bridge.collect()
    else:
        pair('sit-lie','01-sit','02-lie')
        pair('wake-stand','04-wake','05-stand')
        pair('sleep-close','03-sleep-clean','03-sleep-clean')
        pair('idle-close','06-idle','06-idle')
        for name,point,video,enter in [
            ('enter-sleep','sleep-close','02-lie',True),
            ('exit-sleep','sleep-close','04-wake',False),
            ('idle-sit','idle-close','01-sit',False),
            ('stand-idle','idle-close','05-stand',True)]:
            if (bridge.OUT/name/'job.json').exists():continue
            a=anchor(point)
            if a is None:continue
            seq=clip(video)
            if seq is not None:bridge.submit(name,seq[-9] if enter else a,a if enter else seq[8])
