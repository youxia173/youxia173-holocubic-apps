from delivery_paths import DELIVERY_ROOT
"""Reuse the verified converter with isolated revision roots."""
import sys,runpy
from pathlib import Path
from laser_aim_revision import ROOT,bind
bind();HERE=Path(__file__).resolve().parent
DELIVERY=DELIVERY_ROOT / '诺诺-激光指向修正版'
mode=sys.argv[1]
if mode=='contact':runpy.run_path(str(HERE/'laser_contact.py'),run_name='__main__')
elif mode in ['submit','collect']:
 sys.argv=['laser_bridges.py',mode]
 source=(HERE/'laser_bridges.py').read_text('utf-8').replace("if ready('laser-outro'):mb.submit('end',frames('laser-outro')[-9],idle)","if ready('laser-store'):mb.submit('end',frames('laser-store')[-9],idle)\n if ready('laser-outro') and ready('laser-store'):mb.submit('store',frames('laser-outro')[-9],frames('laser-store')[8])")
 source=source.replace("if ready('laser-left') and ready('laser-right'):","if ready('laser-left') and ready('laser-mid') and ready('laser-right'):").replace("mb.submit('turn',left[-9],right[8]);mb.submit('close',right[-9],left[8])","mid=frames('laser-mid');mb.submit('mid',left[-9],mid[8]);mb.submit('turn',mid[-9],right[8]);mb.submit('close',right[-9],left[8])")
 exec(compile(source,str(HERE/'laser_bridges.py'),'exec'),{'__name__':'__main__'})
elif mode=='export':
 import sequence_gif,laser_line_key
 sequence_gif.fit=laser_line_key.fit
 source=(HERE/'export_laser.py').read_text('utf-8').replace("DELIVERY=DELIVERY_ROOT / '诺诺-激光逗猫动画'", "DELIVERY=DELIVERY_ROOT / '诺诺-激光指向修正版'")
 source=source.replace("outro=b('exit')+v('outro')[9:-8]+b('end')[1:]","outro=b('exit')+v('outro')[9:-8]+b('store')[1:]+v('store')[9:-8]+b('end')[1:]")
 source=source.replace("v('left')[9:-9]+b('turn')","v('left')[9:-9]+b('mid')+v('mid')[9:-9]+b('turn')")
 source=source.replace('else:palette=palette_for(seq)',"else:\n   palette=palette_for(seq);colors=palette.getpalette();colors[762:765]=[255,24,24];palette.putpalette(colors)")
 exec(compile(source,str(HERE/'export_laser.py'),'exec'),{'__name__':'__main__'})
elif mode=='delivery':
 import export_laser
 export_laser.ROOT=ROOT;export_laser.DELIVERY=DELIVERY
 source=(HERE/'laser_delivery.py').read_text('utf-8').replace('V0.6.0','V0.6.1').replace('项目预览/激光逗猫','项目预览/激光逗猫指向修正版')
 exec(compile(source,str(HERE/'laser_delivery.py'),'exec'),{'__name__':'__main__'})
else:raise ValueError(mode)
