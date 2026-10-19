import json,shutil
from pathlib import Path
from laser_sequence import ROOT
import nono_video as api
folder=ROOT/'laser-intro';dest=ROOT/'废稿/laser-intro-v2'
assert not dest.exists() and folder.resolve().is_relative_to(ROOT.resolve()) and dest.resolve().is_relative_to(ROOT.resolve())
p0=json.loads((folder/'api_prompt.json').read_text('utf-8'));shutil.move(str(folder),str(dest))
shutil.copy2(Path('C:/Users/youxia173/.codex/generated_images/01a1447e-aa64-7370-9548-b91724178d4b/exec-8a850286-3263-49ba-bfb3-3e1605fdf0bd.png'),ROOT/'关键帧/off.png')
for i,(name,start,end,action) in enumerate([
 ('laser-intro','idle.png','off.png','诺诺右手伸到身后，取出一支小小深蓝色圆柱笔，然后伸到身前朝左下方。笔没有发光，笔只是一支关闭状态的普通小笔，整个过程中都不发光。白猫一直坐在地上看诺诺，身体不动。'),
 ('laser-on','off.png','laser.png','诺诺手臂和笔完全保持原位朝向左下方，不举笔不转笔。拇指轻轻按一下开关，猫左前方地面渐渐出现一个小红色圆点。空气完全空白纯绿，没有线条和光束。猫看向地面圆点，从坐姿站起转向左侧，前身伏低、后腿蓄力，眼睛盯住地面红点。')]):
 f=ROOT/name;f.mkdir();p=json.loads(json.dumps(p0));p['105']['inputs']['value']=2;p['104']['inputs']['seed']+=2000+i
 p['16']['inputs']['image']=api.upload(ROOT/'关键帧'/start);p['9']['inputs']['image']=api.upload(ROOT/'关键帧'/end)
 p['10']['inputs']['text']='固定镜头，诺诺头部、身体、双鞋位置与比例完全不动，只有右手活动。纯绿色背景，唯一一只小白猫，白青科技服装不变。'+action
 p['23']['inputs']['text']='激光束，光线，射线，光带，光剑，射击，枪，闪光，发射，武器，举起手臂，摄像机移动，缩放，猫变大，额外动物，瞬移，文字'
 p['18']['inputs']['filename_prefix']='Nono/'+name+'_split'
 (f/'api_prompt.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),'utf-8');(f/'提示词.txt').write_text(p['10']['inputs']['text'],'utf-8')
 job=api.request('/prompt',json.dumps({'prompt':p}).encode(),{'Content-Type':'application/json'});job.update(retry=2,start=start,end=end,seconds=2)
 (f/'job.json').write_text(json.dumps(job),'utf-8');print(name,job['prompt_id'])
