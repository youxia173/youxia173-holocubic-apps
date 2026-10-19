import json,shutil,sys
from pathlib import Path
import nono_video as api
import laser_sequence as original
ROOT=original.ROOT.parent/'激光逗猫指向修正版'
OLD=original.ROOT
SPECS=[
 ('laser-on','off.png','left.png',2,'诺诺保持站姿，右手的小笔从关闭状态转向左下方，拇指按一下按钮，一条细红色直线从笔尖延伸到左侧地面红点。笔身轴线、笔尖、红线、红点始终共线。白猫从坐姿站起，向左转头盯住地面红点并伏低。'),
 ('laser-left','left.png','right.png',3,'单向从左到右。地面红色圆点从画面左侧端点沿地面匀速向右移动到猫右前方。诺诺右手同步转动笔尖向右扫，细红线起点始终粘在笔尖，终点始终粘在地面红点，笔身与线始终共线。白猫先转向右侧，眼睛和头跟踪右移红点，紧接着四脚向右追跑两小步并向右短扑一次，落地后在右侧盯住红点。猫一路跟着点向右移动，不往左跑，不原地空踏。红点本段绝不向左返回。'),
 ('laser-right','right.png','left.png',3,'单向从右到左。地面红色圆点从右侧端点沿地面匀速向左移动到左端。诺诺右手同步转动笔尖向左扫，细红线起点始终粘在笔尖，终点始终粘在地面红点，笔身与线始终共线。白猫转向左侧，眼睛和头跟踪左移红点，四脚向左追跑两小步并向左短扑一次，落地后伏低看着左侧红点，恢复尾帧姿势。猫一路向左追点，不向右跑，不原地空踏。红点本段绝不向右返回。'),
 ('laser-outro','left.png','idle.png',4,'诺诺停止移动手腕，让细红线和地面红点停在左侧端点。拇指按按钮，红线和红点同时熄灭。然后右手把已关闭的小笔连续移动到身后收起来，被身体遮住后才消失，双手恢复身侧放松。猫抬头看诺诺，回到初始位置坐好。最后恢复站立待机。')]
COMMON='固定镜头，诺诺头身大小双脚位置完全不动，小白猫大小不变，白青科技服和蓝色猫项圈保持。背景纯绿色。只有一支笔、一条细红色直线、一个红色地面圆点。红点贴地，笔尖发射端始终朝向圆点，红线与笔身轴线在同一直线上。红线不弯曲不断开，不从画外发出，不从手掌发出。猫和光点保持在画面内、诺诺脚左边。'
def setup():
 key=ROOT/'关键帧';key.mkdir(parents=True,exist_ok=True)
 gen=Path('C:/Users/youxia173/.codex/generated_images/01a1447e-aa64-7370-9548-b91724178d4b')
 for src,name in [(OLD/'关键帧/idle.png','idle.png'),(OLD/'关键帧/off.png','off.png'),(gen/'exec-328f9f1a-10e0-40cc-ab6e-83b74788606b.png','left.png'),(gen/'exec-e791ec5b-dea2-4d7e-8057-1aecf9e5a980.png','right.png')]:
  if not (key/name).exists():shutil.copy2(src,key/name)
 for name in ['laser-intro','bridges/start']:
  if not (ROOT/name).exists():shutil.copytree(OLD/name,ROOT/name)
def submit():
 setup();template=json.loads((OLD/'laser-right/api_prompt.json').read_text('utf-8'));classes=api.request('/object_info');assert all(n['class_type'] in classes for n in template.values())
 for i,(name,start,end,seconds,action) in enumerate(SPECS):
  f=ROOT/name;f.mkdir(exist_ok=True)
  if (f/'job.json').exists():continue
  p=json.loads(json.dumps(template));p['16']['inputs']['image']=api.upload(ROOT/'关键帧'/start);p['9']['inputs']['image']=api.upload(ROOT/'关键帧'/end);p['105']['inputs']['value']=seconds
  p['10']['inputs']['text']=COMMON+action;p['23']['inputs']['text']='弯曲光线，断开的光线，笔尖与红点错位，画外光线，多条光线，多个红点，光点离地，笔身指错方向，猫反向跑，猫变大，身体拉长，额外四肢，瞬移，镜头移动，缩放，文字'
  p['104']['inputs']['seed']=1732026102300+i;p['18']['inputs']['filename_prefix']='Nono/aim_'+name
  (f/'api_prompt.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),'utf-8');(f/'提示词.txt').write_text(COMMON+action,'utf-8')
  job=api.request('/prompt',json.dumps({'prompt':p}).encode(),{'Content-Type':'application/json'});job.update(start=start,end=end,seconds=seconds)
  (f/'job.json').write_text(json.dumps(job),'utf-8');print(name,job['prompt_id'],flush=True)
 (ROOT/'分镜.json').write_text(json.dumps(SPECS,ensure_ascii=False,indent=2),'utf-8')
def bind():
 original.ROOT=ROOT;original.pipeline.ROOT=ROOT
 if not any(x[0]=='laser-store' for x in original.pipeline.CLIPS):original.pipeline.CLIPS.append(('laser-store','off.png','idle.png','关闭后收笔回待机。'))
 if not any(x[0]=='laser-mid' for x in original.pipeline.CLIPS):original.pipeline.CLIPS.append(('laser-mid','mid.png','right.png','中点向右端。'))
def collect():
 bind();original.pipeline.collect()
if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf-8')
 if sys.argv[1]=='submit':submit()
 else:collect()
