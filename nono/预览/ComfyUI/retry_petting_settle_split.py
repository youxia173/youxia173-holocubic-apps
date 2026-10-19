import json,shutil
from pathlib import Path
from petting_revision import ROOT
import nono_video as api
folder=ROOT/'04-settle';dest=ROOT/'废稿/04-settle-armpit-v2'
assert not dest.exists() and folder.resolve().is_relative_to(ROOT.resolve()) and dest.resolve().is_relative_to(ROOT.resolve())
template=json.loads((folder/'api_prompt.json').read_text('utf-8'));shutil.move(str(folder),str(dest))
shutil.copy2(Path('C:/Users/youxia173/.codex/generated_images/01a1447e-aa64-7370-9548-b91724178d4b/exec-975a3ecd-17b9-4cae-a76f-139117e816b2.png'),ROOT/'关键帧/cradle.png')
specs=[('04-settle','armpit-air.png','cradle.png','诺诺双手抱着已经离地的白猫，左手迅速托住猫臀部向右上方抬，使猫在胸前从竖直转成横卧，猫头始终在画面左边，猫后腿转到画面右边。右手始终托猫前腋下。猫身体大小和长度不变，四脚朝下悬垂，不迈步，不放回地上。'),('04-cradle','cradle.png','hug.png','诺诺左前臂稳稳托着白猫腹部和后半身，猫保持横卧背朝上肚子朝下、四脚向下，猫头固定在画面左边。诺诺只把右手从猫胸下移到头顶，轻轻摸头。猫原地不动不转身不变大不变长。')]
for i,(name,start,end,action) in enumerate(specs):
 folder=ROOT/name;folder.mkdir();p=json.loads(json.dumps(template));p['105']['inputs']['value']=1;p['104']['inputs']['seed']+=200+i
 p['16']['inputs']['image']=api.upload(ROOT/'关键帧'/start);p['9']['inputs']['image']=api.upload(ROOT/'关键帧'/end)
 p['10']['inputs']['text']='固定镜头，诺诺蹲姿、头部、脸、双膝和双鞋的位置和大小完全不变。纯绿背景。只有手臂和一只小白猫动作。一秒内完成单一动作。'+action
 p['18']['inputs']['filename_prefix']='Nono/split_'+name
 (folder/'api_prompt.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),'utf-8');(folder/'提示词.txt').write_text(p['10']['inputs']['text'],'utf-8')
 job=api.request('/prompt',json.dumps({'prompt':p}).encode(),{'Content-Type':'application/json'});job.update(retry=2,start=start,end=end,seconds=1)
 (folder/'job.json').write_text(json.dumps(job),'utf-8');(folder/'armpit-version.txt').write_text('split-v3','utf-8');print(name,job['prompt_id'])
