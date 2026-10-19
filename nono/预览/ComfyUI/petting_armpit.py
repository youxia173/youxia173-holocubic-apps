"""User-requested armpit lift: separate keyframes, keep lowering endpoints intact."""
import json, shutil, sys
from pathlib import Path
import nono_video as api
from petting_revision import ROOT

SPECS=[
 ('03-grip','crouch.png','armpit-ground.png',3,'The cat stands still on the floor. Nono moves BOTH hands under the cat TWO FRONT ARMPITS, one hand under each front shoulder, cupping its upper chest. All paws stay on ground until hands are in position. Only hands move, no lift yet.'),
 ('04-lift','armpit-ground.png','armpit-air.png',2,'Both hands already support the cat under BOTH FRONT ARMPITS. Nono raises both hands vertically together. The cat leaves the ground directly, rear paws leave once and hang loosely straight down. The cat does NOT walk, step, kick or pedal. Its compact torso tilts naturally upright while being lifted by its front armpits. Preserve its size and limb lengths. No stretching. End with all paws clearly airborne.'),
 ('04-settle','armpit-air.png','hug.png',3,'Cat already airborne, held beneath BOTH FRONT ARMPITS. Nono smoothly brings it toward her chest, transfers its weight onto her left forearm supporting belly and hindquarters. Cat rotates gently from upright to horizontal belly-down, NEVER belly-up. Four paws point down throughout, no kicking or walking. Right hand then rests on top of cat head. Finish in exact reference hug pose.')]
COMMON='Locked camera. Girl Nono remains in exact same low squat with head size, face position, knees and both shoes fixed. Only arms and one white cat move. Preserve silver-blue hair, white teal tech costume, triangle hairclip, pure green background. '

def submit():
 gen=Path('C:/Users/youxia173/.codex/generated_images/01a1447e-aa64-7370-9548-b91724178d4b')
 for src,name in [('exec-3cc6f4c0-e22f-4d11-844b-b8fdd72dccc7.png','armpit-ground.png'),('exec-e9353cdf-64ab-437f-9238-f7f4b757a11f.png','armpit-air.png')]:
  shutil.copy2(gen/src,ROOT/'关键帧'/name)
 template=json.loads((ROOT.parent/'连续喂饭/完整动画/04-坐下吃饭/api_prompt.json').read_text('utf-8'))
 for i,(name,start,end,seconds,action) in enumerate(SPECS):
  folder=ROOT/name
  if (folder/'armpit-version.txt').exists():continue
  dest=ROOT/'废稿'/(name+'-before-armpit-request')
  if folder.exists():
   assert folder.resolve().is_relative_to(ROOT.resolve()) and dest.resolve().is_relative_to(ROOT.resolve()) and not dest.exists()
   shutil.move(str(folder),str(dest))
  folder.mkdir()
  p=json.loads(json.dumps(template));p['16']['inputs']['image']=api.upload(ROOT/'关键帧'/start);p['9']['inputs']['image']=api.upload(ROOT/'关键帧'/end)
  p['10']['inputs']['text']=COMMON+action;p['105']['inputs']['value']=seconds
  p['23']['inputs']['text']='walking, stepping hind legs, kicking, pedaling, belly up, baby cradle, stretching cat, extra limbs, giant cat, camera zoom, changing girl size, standing up, body sway, background change'
  p['104']['inputs']['seed']=1732026102200+i;p['18']['inputs']['filename_prefix']='Nono/armpit_'+name
  (folder/'api_prompt.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),'utf-8');(folder/'提示词.txt').write_text(COMMON+action,'utf-8')
  job=api.request('/prompt',json.dumps({'prompt':p,'client_id':'nono-armpit'}).encode(),{'Content-Type':'application/json'});job.update(start=start,end=end,seconds=seconds,user_revision='both front armpits')
  (folder/'job.json').write_text(json.dumps(job,indent=2),'utf-8');(folder/'armpit-version.txt').write_text('user-requested armpit lift','utf-8');print(name,job['prompt_id'],flush=True)
 for name in ['02-crouch-03-grip','03-grip-04-lift','04-lift-04-settle','pet-enter']:
  folder=ROOT/'bridges'/name;dest=ROOT/'废稿'/(name+'-before-armpit-request')
  if folder.exists():
   assert folder.resolve().is_relative_to(ROOT.resolve()) and dest.resolve().is_relative_to(ROOT.resolve()) and not dest.exists()
   shutil.move(str(folder),str(dest))
 (ROOT/'腋下抱起分镜.json').write_text(json.dumps(SPECS,ensure_ascii=False,indent=2),'utf-8')
if __name__=='__main__':submit()
