"""Explicit targeted regeneration, preserving rejected inputs and outputs."""
import json,sys,shutil
from laser_sequence import ROOT
import nono_video as api
name=sys.argv[1];retry=int(sys.argv[2]);assert 1<=retry<=2
folder=ROOT/name;dest=ROOT/'废稿'/f'{name}-v{retry}';dest.parent.mkdir(exist_ok=True)
assert folder.resolve().is_relative_to(ROOT.resolve()) and dest.resolve().is_relative_to(ROOT.resolve()) and not dest.exists()
p=json.loads((folder/'api_prompt.json').read_text('utf-8'));shutil.move(str(folder),str(dest));folder.mkdir()
if name=='laser-intro':
 p['105']['inputs']['value']=3
 p['10']['inputs']['text']='Stationary camera and standing Nono, same body size, shoes planted on same spot. ONE simple three-second action: Nono reaches behind her right hip, takes out a small dark blue laser pointer, and immediately angles it DOWN toward floor on screen left. Her thumb presses the button ONLY AFTER it points down. A single small RED ROUND DOT appears on floor left of cat. Cat stands from sitting and crouches looking directly at the red dot. Invisible beam, clean empty green air between pointer and dot. Absolutely no visible ray, no line, no streak, no shooting. Nono does not aim up or forward. Cat remains inside canvas on left. Same girl white teal costume silver hair, same white cat and blue triangle collar. Pure green background. Smoothly match final pose.'
elif name=='laser-left':
 p['105']['inputs']['value']=2
 p['10']['inputs']['text']='固定镜头。诺诺站姿完全不变，手中小笔保持原位。地面仅有一颗红色圆点，圆点周围和上方都是干净纯绿色背景。小白猫保持原图的小巧体型和长度，先盯住左侧地面红色圆点，再后腿发力向左跳一小步，前爪落在圆点上。圆点沿地面滑到猫右侧，白猫原地转身朝右伏低，准备再次扑击。两秒单一短动作，猫不出画面，不靠近边缘，不经过诺诺双腿。画面里只有女孩、小白猫、她手里的小笔、地面的小红色圆点，其他区域完全是纯绿色空白。没有线条，没有光带，没有额外特效，猫体型全程不改变。'
else:raise ValueError(name)
p['23']['inputs']['text']='visible laser beam, light ray, line, streak, shooting, gun, weapon, sparks, glowing aura, multiple dots, camera zoom, camera motion, girl walking, extra cat, animal offscreen, stretching, morphing, jump cut, text'
p['104']['inputs']['seed']+=1000*retry;p['18']['inputs']['filename_prefix']=f'Nono/{name}_retry{retry}'
(folder/'api_prompt.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),'utf-8');(folder/'提示词.txt').write_text(p['10']['inputs']['text'],'utf-8')
job=api.request('/prompt',json.dumps({'prompt':p}).encode(),{'Content-Type':'application/json'});job.update(retry=retry)
(folder/'job.json').write_text(json.dumps(job),'utf-8');print(job)
