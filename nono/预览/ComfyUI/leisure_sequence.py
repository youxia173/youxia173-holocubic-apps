"""Resumable reading/gaming asset production; never modifies runtime files."""
import json,sys,shutil
from pathlib import Path
import nono_video as api
ROOT=Path(__file__).resolve().parent.parent/'看书与游戏'
COMMON='固定镜头，纯绿色背景，保持参考中的诺诺科技服装、银蓝长发、三角发夹、蓝眼睛和一只白猫。角色大小稳定，坐稳站稳，重心贴地，动作自然连续，手与道具始终接触，不出现字幕和特效。'
CLIPS=[
 ('read-intro','idle.png','read.png','诺诺先把右手伸到身后，取出一本深蓝封面的实体书，双手拿稳合着的书，然后缓慢屈膝侧坐到地上，坐稳后打开书放在膝上开始阅读。书从背后移出，绝不凭空出现。白猫原地坐着看她。'),
 ('read-loop','read.png','read.png','诺诺始终侧坐，双手拿着同一本打开的书，专心阅读，视线轻微移动，眨眼一次，右手自然翻过一张纸页后重新握好书，身体轻柔呼吸，最后回到初始持书姿态。白猫眨眼，尾尖轻轻摆动复位。五秒循环，书一直打开，不起身不合书，无可读页码。'),
 ('read-outro','read.png','idle.png','诺诺先慢慢合上书，左手拿稳合着的书，右手撑地，收腿蹲起，慢慢站直，然后把合上的书移到背后收好，双臂自然放回身体两侧，微笑待机。书必须连续移动到身体遮挡后才消失。白猫始终原地坐着。'),
 ('game-intro','idle.png','game.png','诺诺先把右手伸到身后，拿出一台白蓝色掌上游戏机，双手拿稳，然后缓慢屈膝侧坐在地上，坐稳后把游戏机放在膝前握好，低头看着屏幕。设备从背后取出，绝不凭空出现。白猫原地坐着看她。'),
 ('game-loop','game.png','game.png','五秒自然循环。诺诺始终侧坐在地上，双手握住同一台游戏机，双拇指交替轻轻按键，专心看屏幕，轻微左右倾身几厘米，眨眼，露出小小开心笑容，然后恢复开始的握持姿态。设备大小外形稳定，屏幕始终朝向诺诺，背面朝镜头。白猫好奇看着双手，轻眨眼和小幅摆尾后复位。不放下游戏机，不起身，不举过头顶。'),
 ('game-outro','game.png','idle.png','诺诺停止按键，轻轻按下游戏机上方电源键，左手握住游戏机，右手撑地，收腿蹲起，慢慢站直，再把游戏机移到背后收好，双手放松回身体两侧恢复微笑站立。设备必须连续移动到身后遮挡才消失。白猫始终原地坐着。'),
]
def setup():
 p=ROOT/'关键帧';p.mkdir(parents=True,exist_ok=True)
 generated=Path('C:/Users/youxia173/.codex/generated_images/01a1447e-aa64-7370-9548-b91724178d4b')
 for src,name in [(ROOT.parent/'连续喂饭/关键帧/A01-站立待机.png','idle.png'),(generated/'exec-ce2fbaed-5993-4078-ae51-f1ec24c89e9f.png','read.png'),(generated/'exec-7d387119-8cfb-407a-ae75-ca3392f9dfd7.png','game.png')]:
  if not (p/name).exists():shutil.copy2(src,p/name)
def submit():
 setup(); current=api.request('/object_info');template=json.loads((ROOT.parent/'连续喂饭/完整动画/04-坐下吃饭/api_prompt.json').read_text('utf-8'))
 assert all(n['class_type'] in current for n in template.values())
 uploads={}
 for i,(name,start,end,action) in enumerate(CLIPS):
  folder=ROOT/name;folder.mkdir(exist_ok=True)
  if (folder/'job.json').exists():continue
  for file in (start,end):
   if file not in uploads:uploads[file]=api.upload(ROOT/'关键帧'/file)
  p=json.loads(json.dumps(template));p['16']['inputs']['image']=uploads[start];p['9']['inputs']['image']=uploads[end]
  p['10']['inputs']['text']=COMMON+action
  p['23']['inputs']['text']='镜头移动，缩放，跳切，漂浮，脚滑，倒放，额外手指，额外四肢，多只猫，机器人，换衣服，道具融合，道具变形，凭空消失，书和游戏机同时出现，字幕，文字，阴影，背景变化，魔法'
  p['104']['inputs']['seed']=1732026102000+i;p['18']['inputs']['filename_prefix']='Nono/leisure_'+name
  (folder/'提示词.txt').write_text(COMMON+action,'utf-8');(folder/'api_prompt.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),'utf-8')
  job=api.request('/prompt',json.dumps({'prompt':p,'client_id':'nono-leisure'}).encode(),{'Content-Type':'application/json'})
  job.update(start=start,end=end,phase=name.split('-')[1]);(folder/'job.json').write_text(json.dumps(job,indent=2),'utf-8');print(name,job['prompt_id'],flush=True)
 (ROOT/'分镜.json').write_text(json.dumps(CLIPS,ensure_ascii=False,indent=2),'utf-8')
def collect():
 for name,*_ in CLIPS:
  folder=ROOT/name
  if list(folder.glob('*.mp4')):print(name,'downloaded');continue
  job=json.loads((folder/'job.json').read_text('utf-8'));item=api.request('/history/'+job['prompt_id']).get(job['prompt_id'])
  if item:api.status(type('Args',(),{'output':str(folder)})())
  else:print(name,'pending')
if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf-8')
 if sys.argv[1]=='submit':submit()
 else:collect()
