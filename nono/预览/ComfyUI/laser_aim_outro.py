import json,shutil
from laser_aim_revision import ROOT
import nono_video as api
f=ROOT/'laser-outro';dest=ROOT/'废稿/laser-outro-v1'
assert not dest.exists() and f.resolve().is_relative_to(ROOT.resolve()) and dest.resolve().is_relative_to(ROOT.resolve())
template=json.loads((f/'api_prompt.json').read_text('utf-8'));shutil.move(str(f),str(dest))
for i,(name,start,end,action) in enumerate([('laser-outro','left.png','off.png','诺诺手中的笔保持原位，不转动不收回，只按一下按钮。红线和红点立即同时熄灭，随后背景一直纯绿没有红光。猫看不到红点后转头看诺诺，原地恢复坐姿。没有爆炸闪光，没有火花，没有残留红点。'),('laser-store','off.png','idle.png','小笔已经关闭，不发光没有红点。诺诺右手将小笔移到身后，完全被身体遮挡后收好，右手回身侧。猫始终坐在原位，诺诺始终站立。')]):
 f=ROOT/name;f.mkdir();p=json.loads(json.dumps(template));p['105']['inputs']['value']=2;p['104']['inputs']['seed']+=700+i
 p['16']['inputs']['image']=api.upload(ROOT/'关键帧'/start);p['9']['inputs']['image']=api.upload(ROOT/'关键帧'/end)
 p['10']['inputs']['text']='固定镜头，诺诺与小白猫大小稳定，双鞋位置固定。'+action
 p['23']['inputs']['text']='闪光，爆炸，火花，残留光点，多条光线，红点变球，猫变大，镜头移动，缩放'
 p['18']['inputs']['filename_prefix']='Nono/aim_'+name+'_split'
 (f/'api_prompt.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),'utf-8');(f/'提示词.txt').write_text(p['10']['inputs']['text'],'utf-8')
 job=api.request('/prompt',json.dumps({'prompt':p}).encode(),{'Content-Type':'application/json'});job.update(retry=1,start=start,end=end)
 (f/'job.json').write_text(json.dumps(job),'utf-8');print(name,job['prompt_id'])
