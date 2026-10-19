import json,shutil
from pathlib import Path
from laser_sequence import ROOT
import nono_video as api
folder=ROOT/'laser-loop';dest=ROOT/'废稿/laser-loop-v1'
assert not dest.exists() and folder.resolve().is_relative_to(ROOT.resolve()) and dest.resolve().is_relative_to(ROOT.resolve())
p0=json.loads((folder/'api_prompt.json').read_text('utf-8'));shutil.move(str(folder),str(dest))
shutil.copy2(Path('C:/Users/youxia173/.codex/generated_images/01a1447e-aa64-7370-9548-b91724178d4b/exec-28bd0f6e-b47b-46f7-adb6-cd9f250ea6b2.png'),ROOT/'关键帧/right.png')
for i,(name,start,end,action) in enumerate([
 ('laser-left','laser.png','right.png','The cat stares at the red floor dot on its LEFT, crouches then makes ONE SHORT forward pounce LEFT onto the dot, lands on front paws then rear paws. The dot smoothly slides RIGHT only a short distance toward the other side of cat. Cat turns in place to face RIGHT and crouches watching dot, exactly matching final image. No running out of frame.'),
 ('laser-right','right.png','laser.png','The cat stares at red floor dot on its RIGHT, crouches then makes ONE SHORT pounce RIGHT, paws tapping the floor dot. Dot smoothly slides back LEFT a short distance. Cat turns in place to face LEFT and crouches in original spot, watching the dot, exactly matching final image. No running past girl.')]):
 f=ROOT/name;f.mkdir();p=json.loads(json.dumps(p0));p['105']['inputs']['value']=2;p['104']['inputs']['seed']+=1100+i
 p['16']['inputs']['image']=api.upload(ROOT/'关键帧'/start);p['9']['inputs']['image']=api.upload(ROOT/'关键帧'/end)
 p['10']['inputs']['text']='Fixed camera. Nono girl stays exactly still in reference standing pose and size. White cat stays SMALL, SAME HEAD SIZE and compact SAME BODY LENGTH all frames. Cat and red dot stay fully inside canvas, within space LEFT of girl and far from left edge. No scaling or stretching. Only one small red ROUND DOT ON GROUND, no visible laser beam, no ray or line. Girl wrist gently aims down. '+action+' Cat tracks dot with eyes and head. Two-second action. Pure green background. Preserve blue cat collar and girl identity.'
 p['23']['inputs']['text']='giant cat, growing cat, stretched cat, long body, offscreen, cropped tail, cat crossing girl, camera zoom, moving girl, visible laser beam, streak, multiple dots, ball, extra legs, floating, flying, human pose, text'
 p['18']['inputs']['filename_prefix']='Nono/'+name+'_split'
 (f/'api_prompt.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),'utf-8');(f/'提示词.txt').write_text(p['10']['inputs']['text'],'utf-8')
 job=api.request('/prompt',json.dumps({'prompt':p}).encode(),{'Content-Type':'application/json'});job.update(retry=1,start=start,end=end,seconds=2)
 (f/'job.json').write_text(json.dumps(job),'utf-8');print(name,job['prompt_id'])
