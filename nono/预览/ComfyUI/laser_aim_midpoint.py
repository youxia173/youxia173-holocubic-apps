import json,shutil
from pathlib import Path
from laser_aim_revision import ROOT
import nono_video as api
f=ROOT/'laser-left';dest=ROOT/'废稿/laser-left-v2'
assert not dest.exists() and f.resolve().is_relative_to(ROOT.resolve()) and dest.resolve().is_relative_to(ROOT.resolve())
template=json.loads((f/'api_prompt.json').read_text('utf-8'));shutil.move(str(f),str(dest))
shutil.copy2(Path('C:/Users/youxia173/.codex/generated_images/01a1447e-aa64-7370-9548-b91724178d4b/exec-6a35806e-ec70-4102-8921-b34a4e25f3f3.png'),ROOT/'关键帧/mid.png')
for i,(name,start,end,action) in enumerate([('laser-left','left.png','mid.png','红点从左端沿地面向右滑到猫前方的中点，白猫原地转向右，开始追点，前爪向右迈一小步。'),('laser-mid','mid.png','right.png','红点从中点沿地面继续向右滑一小段到尾帧位置，白猫跟着向右跑一小步，右向前爪落地，盯着红点。')]):
 f=ROOT/name;f.mkdir();p=json.loads(json.dumps(template));p['105']['inputs']['value']=1;p['104']['inputs']['seed']+=900+i
 p['16']['inputs']['image']=api.upload(ROOT/'关键帧'/start);p['9']['inputs']['image']=api.upload(ROOT/'关键帧'/end)
 p['10']['inputs']['text']='固定镜头，诺诺站姿头身双脚完全不动。一秒内只完成首图到尾图的短距离移动。'+action+'笔尖与红线像同一根笔直细杆一起绕手腕向右转，红线起点在笔尖终点在地面圆点，始终共线。红点匀速只向右，绝不超出尾帧位置，不回头。全程只一条细红直线，无残影无拖尾，无地面横线。猫大小不变。纯绿背景。'
 p['18']['inputs']['filename_prefix']='Nono/aim_'+name+'_midpoint'
 (f/'api_prompt.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),'utf-8');(f/'提示词.txt').write_text(p['10']['inputs']['text'],'utf-8')
 job=api.request('/prompt',json.dumps({'prompt':p}).encode(),{'Content-Type':'application/json'});job.update(retry=2,start=start,end=end)
 (f/'job.json').write_text(json.dumps(job),'utf-8');print(name,job['prompt_id'])
