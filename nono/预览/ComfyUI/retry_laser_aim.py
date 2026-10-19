import json,shutil,sys
import nono_video as api
from laser_aim_revision import ROOT
name=sys.argv[1];n=int(sys.argv[2]);assert n<=2
f=ROOT/name;dest=ROOT/'废稿'/f'{name}-v{n}';dest.parent.mkdir(exist_ok=True)
assert not dest.exists() and f.resolve().is_relative_to(ROOT.resolve()) and dest.resolve().is_relative_to(ROOT.resolve())
p=json.loads((f/'api_prompt.json').read_text('utf-8'));shutil.move(str(f),str(dest));f.mkdir()
direction='LEFT to RIGHT' if name=='laser-left' else 'RIGHT to LEFT'
p['105']['inputs']['value']=2;p['104']['inputs']['seed']+=400*n
p['10']['inputs']['text']=f'Locked camera. TWO second controlled movement, exactly start to end image. The laser pointer barrel and its SINGLE STRAIGHT thin red ray rotate together as ONE RIGID STRAIGHT ROD about the girl hand. Red beam STARTS at emitting pen TIP and ENDS at single red spot on flat floor. Absolutely NO TRAIL: old ray disappears immediately as new ray moves. No second segment along floor. No polygon or bent line. Ground red dot moves ONLY {direction}, directly to end reference spot, never overshooting, never passing girl feet. Girl wrist and barrel track that exact point. Cat follows the dot {direction} with short quick ground steps then crouches at final pose. Cat stays compact and same size, all movement confined left of girl feet. Girl feet head torso size stay fixed. Green background. Match final image early and settle gently.'
p['23']['inputs']['text']='motion trail, afterimage, multiple rays, horizontal line on floor, triangle, polygon, bent beam, disconnected beam, curved beam, laser originating offscreen, wrong direction, overshoot, dot behind girl, walking girl, cat growing, long cat, teleport, camera motion, zoom'
if name=='laser-outro':
 p['105']['inputs']['value']=1
 p['10']['inputs']['text']='One-second quiet transition. The tiny red line and dot simply fade to pure green background immediately, leaving empty green space. Nono keeps hand and pen completely motionless. Cat gently turns head toward Nono and sits in final reference pose. Match final frame precisely. Fixed camera and fixed standing girl, same compact white cat. Clean plain green backdrop. Minimal calm motion.'
 p['23']['inputs']['text']='explosion, fire, spark, flash, particles, glowing aura, weapon, shooting, residual dot, red floor mark, moving pen, camera movement, zoom, extra limbs'
p['18']['inputs']['filename_prefix']=f'Nono/aim_{name}_retry{n}'
(f/'api_prompt.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),'utf-8');(f/'提示词.txt').write_text(p['10']['inputs']['text'],'utf-8')
job=api.request('/prompt',json.dumps({'prompt':p}).encode(),{'Content-Type':'application/json'});job.update(retry=n)
(f/'job.json').write_text(json.dumps(job),'utf-8');print(job)
