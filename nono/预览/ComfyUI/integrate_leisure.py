"""Integrate complete reading/game sequences with a shared idle/sleep palette."""
import json,shutil
from pathlib import Path
from export_leisure import build
from export_sleep import build as sleep_build
from sequence_gif import palette_for,save
ROOT=Path(__file__).resolve().parents[2]
CODE=ROOT/'代码'
BACKUP=ROOT/'归档/v0.3.0-看书游戏接入前'
if BACKUP.exists():raise RuntimeError('Backup already exists; inspect before rerunning')
BACKUP.mkdir(parents=True)
shutil.copytree(CODE,BACKUP/'代码')
for name in ['PetScene.cs','NonoPreview.cs']:
 shutil.copy2(ROOT/'预览'/name,BACKUP/name)
seq={a:build(a,(200,150)) for a in ['read','game']}
seq['sleep']=sleep_build((200,150))
palette=palette_for([frames for series in seq.values() for frames in series])
facts={}
for activity,series in seq.items():
 facts[activity]={}
 for phase,frames in zip(['intro','loop','outro'],series):
  facts[activity][phase]=save(CODE/f'assets/nono-{activity}-{phase}.gif',frames,palette,phase=='loop')
idle=save(CODE/'assets/nono-idle-cat.gif',seq['sleep'][3],palette,True)
layout=json.loads((CODE/'layout.json').read_text('utf-8'));layout['version']='0.4.0'
for a in layout['assets']:
 if a['id']=='idle':a.update(**idle)
 if a['id'] not in facts:continue
 activity=a['id'];f=facts[activity]
 a.update(file=f'assets/nono-{activity}-intro.gif',loop_file=f'assets/nono-{activity}-loop.gif',outro_file=f'assets/nono-{activity}-outro.gif',return_activity='idle',loop_seconds=a.get('loop_seconds',30),**f['intro'],loop_duration_ms=f['loop']['duration_ms'],loop_frame_count=f['loop']['frame_count'],outro_duration_ms=f['outro']['duration_ms'],outro_frame_count=f['outro']['frame_count'])
 if activity in ['read','game']:a['title']='诺诺 · '+{'read':'看书','game':'打游戏'}[activity]+'（完整流程，可设时长）'
(CODE/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),'utf-8')
# Archive obsolete runtime GIFs and the previous package inside this app only.
for path in [CODE/'assets/nono-read.gif',CODE/'assets/nono-game.gif',*list((ROOT/'安装包').glob('*.zip'))]:
 if not path.exists():continue
 assert path.resolve().is_relative_to(ROOT.resolve())
 dest=BACKUP/path.name
 assert dest.resolve().is_relative_to(ROOT.resolve()) and not dest.exists()
 shutil.move(str(path),str(dest))
for rel in ['代码/app.info','代码/info.html','预览/NonoPreview.cs','预览/tools/package.py','说明/阶段1使用与验证.md']:
 p=ROOT/rel;s=p.read_text('utf-8').replace('0.3.0','0.4.0')
 s=s.replace('完整睡眠版','完整生活动画版')
 s=s.replace('complete sleep and meal sequences','complete meal, sleep, reading and gaming sequences')
 s=s.replace('完整睡眠与吃饭、独立时长','吃饭睡觉看书游戏完整流程、独立时长')
 if rel.endswith('NonoPreview.cs'):
  s=s.replace('自动生活 · 吃饭和睡眠完整结束后回待机','自动生活 · 四种完整活动结束后回待机')
  s=s.replace('id=="sleep"?"睡眠":activity.title','id=="sleep"?"睡眠":id=="read"?"看书":id=="game"?"游戏":activity.title')
 if rel.endswith('package.py'):s=s.replace('吃饭、睡眠均为','吃饭、睡眠、看书、游戏均为')
 if rel.endswith('info.html'):s=s.replace('吃饭与睡眠独立设置循环时长','吃饭、睡眠、看书和游戏均有完整准备及结束动作，分别独立设置循环时长')
 if rel.endswith('.md'):
  s=s.replace('完整睡眠与独立活动时长','完整生活动画与独立活动时长')
  s=s.replace('手动选择吃饭或睡觉','手动选择吃饭、睡觉、看书或游戏')
  s=s.replace('“进食时长”和“睡眠时长”独立设置5–600秒，默认分别为30秒与60秒','“进食时长”“睡眠时长”“看书时长”和“游戏时长”独立设置5–600秒；睡眠默认60秒，其余默认30秒')
  s=s.replace('看书与打游戏仍为原有动画，本次没有重新制作它们的完整流程。','看书新增取书坐下→阅读翻页循环→合书起身收好；游戏新增取掌机坐下→按键循环→收起站立。两者准备、结束各5.53秒，核心循环每圈5.03秒；默认30秒取6圈，完整活动约41.24秒。')
  s=s.replace('吃饭、睡眠会完成','吃饭、睡眠、看书、游戏会完成').replace('`eat`与`sleep`','`eat`、`sleep`、`read`与`game`')
  s+='\n看书与游戏过程文件在`预览/看书与游戏/`。本版统一待机、睡眠、看书、游戏调色板，确保软件内起止接点逐像素一致；吃饭保留既有素材。\n'
 p.write_text(s,'utf-8')
print('Integrated V0.4.0; defaults read/game 30s, independent 5–600s; previous version archived.')
