import json,shutil
from petting_revision import ROOT
import nono_video as api
folder=ROOT/'04-settle';dest=ROOT/'废稿/04-settle-armpit-v1'
assert not dest.exists()
assert folder.resolve().is_relative_to(ROOT.resolve()) and dest.resolve().is_relative_to(ROOT.resolve())
p=json.loads((folder/'api_prompt.json').read_text('utf-8'));shutil.move(str(folder),str(dest));folder.mkdir()
p['105']['inputs']['value']=2;p['104']['inputs']['seed']+=100
p['10']['inputs']['text']='Locked camera, fixed girl head, knees and shoes. Single simple movement in TWO seconds. Nono transfers the cat from upright armpit lift to belly-down horizontal support. CAT HEAD ALWAYS STAYS ON SCREEN LEFT. CAT HINDQUARTERS ALWAYS STAY ON SCREEN RIGHT. Cat never turns around or faces screen right. Both hands initially under front armpits. Left forearm slides beneath cat abdomen and lifts rear half to horizontal, while cat head remains in the SAME spot on screen left. The cat lower body swings UP toward screen right into her left arm. Right hand finishes atop cat head. Compact cat body keeps same length, no stretching, no growth. Cat four paws stay pointed down under body, limp and still. No cat walking, no belly-up. Girl remains absolutely fixed in low squat. Pure green background. Follow end image exactly.'
p['23']['inputs']['text']='cat turning around, cat head on right, long cat, stretching, growing cat, huge cat, walking, kicking, pedaling, baby hold, belly up, cat reaching girl face, camera motion, zoom, girl moving, extra limbs'
p['18']['inputs']['filename_prefix']='Nono/armpit_settle_v2'
(folder/'api_prompt.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),'utf-8');(folder/'提示词.txt').write_text(p['10']['inputs']['text'],'utf-8')
job=api.request('/prompt',json.dumps({'prompt':p}).encode(),{'Content-Type':'application/json'});job.update(retry=1,start='armpit-air.png',end='hug.png',seconds=2)
(folder/'job.json').write_text(json.dumps(job),'utf-8');(folder/'armpit-version.txt').write_text('v2','utf-8');print(job)
for name in ['04-lift-04-settle','pet-enter']:
 src=ROOT/'bridges'/name;target=ROOT/'废稿'/(name+'-armpit-v1')
 assert src.resolve().is_relative_to(ROOT.resolve()) and target.resolve().is_relative_to(ROOT.resolve()) and not target.exists()
 if src.exists():shutil.move(str(src),str(target))
