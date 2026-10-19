"""Install validated petting assets and archive V0.4.0 before mutations."""
import json,shutil
from pathlib import Path
from export_petting import DELIVERY,ROOT as MEDIA
ROOT=MEDIA.parent.parent;CODE=ROOT/'代码';BACKUP=ROOT/'归档/v0.4.0-撸猫接入前'
if BACKUP.exists():raise RuntimeError('Backup exists; inspect before rerun')
facts=json.loads((DELIVERY/'时长信息.json').read_text('utf-8'))['200x150']
BACKUP.mkdir(parents=True);shutil.copytree(CODE,BACKUP/'代码')
for rel in ['预览/NonoPreview.cs','预览/PetScene.cs','预览/tools/BuildAssets.cs','预览/tools/package.py','说明/阶段1使用与验证.md']:
 dest=BACKUP/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,dest)
for phase in ['intro','loop','outro']:shutil.copy2(DELIVERY/f'{phase}-200x150.gif',CODE/f'assets/nono-pet-{phase}.gif')
layout=json.loads((CODE/'layout.json').read_text('utf-8'));layout['version']='0.5.0'
a=dict(next(x for x in layout['assets'] if x['id']=='read'));a.update(id='pet',title='诺诺 · 撸猫（完整流程，可设时长）',file='assets/nono-pet-intro.gif',loop_file='assets/nono-pet-loop.gif',outro_file='assets/nono-pet-outro.gif',title_file='assets/ui/title-pet.png',status_file='assets/ui/status-pet.png',loop_seconds=30,**facts['intro'],loop_duration_ms=facts['loop']['duration_ms'],loop_frame_count=facts['loop']['frame_count'],outro_duration_ms=facts['outro']['duration_ms'],outro_frame_count=facts['outro']['frame_count'])
assert not any(x['id']=='pet' for x in layout['assets']);layout['assets'].append(a)
(CODE/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),'utf-8')
for rel in ['代码/main.lua','代码/app.info','代码/info.html','预览/NonoPreview.cs','预览/tools/package.py','说明/阶段1使用与验证.md']:
 p=ROOT/rel;s=p.read_text('utf-8').replace('0.4.0','0.5.0').replace('完整生活动画版','完整撸猫版')
 if rel.endswith('app.info'):s=s.replace('reading and gaming','reading, gaming and cat-petting').replace('吃饭睡觉看书游戏完整流程','吃饭睡觉看书游戏撸猫完整流程')
 if rel.endswith('NonoPreview.cs'):
  s=s.replace('四种完整活动','五种完整活动').replace('id=="game"?"游戏":activity.title','id=="game"?"游戏":id=="pet"?"撸猫":activity.title').replace('五种初始科技活动','六种初始科技活动')
 if rel.endswith('package.py'):s=s.replace('吃饭、睡眠、看书、游戏均为','吃饭、睡眠、看书、游戏、撸猫均为')
 if rel.endswith('info.html'):s=s.replace('吃饭、睡眠、看书和游戏','吃饭、睡眠、看书、游戏和撸猫');s=s.replace('</html>','<p>新增白猫蹭小腿→蹲下摸头→抱入怀里→抚摸循环→放下白猫→回待机。撸猫时长独立设置。</p></html>')
 if rel.endswith('.md'):
  s=s.replace('“看书时长”和“游戏时长”','“看书时长”“游戏时长”和“撸猫时长”').replace('`read`与`game`','`read`、`game`与`pet`')
  s+='\n## V0.5.0 撸猫\n\n新增完整流程：白猫蹭小腿→诺诺蹲下摸头→托住猫抱进怀里→循环抚摸→托住猫放回地面→站起，白猫回原位。手动和自动模式都按完整流程回待机。面板“撸猫时长”独立保存5–600秒，默认30秒，修改下次活动生效。准备约15.53秒、循环每圈5.03秒、放下及站起约10.53秒；默认6圈，总计约56.24秒。精确时长以layout.json为准。\n\n新素材位于`代码/assets/nono-pet-intro.gif`、`nono-pet-loop.gif`、`nono-pet-outro.gif`，过程保存在`预览/完整撸猫/`；桌面`诺诺-完整撸猫动画`含透明GIF和完整三圈示例。设备解码帧率仍需真机验证。\n'
 p.write_text(s,'utf-8')
for path in (ROOT/'安装包').glob('*.zip'):
 dest=BACKUP/path.name;assert path.resolve().is_relative_to(ROOT.resolve()) and dest.resolve().is_relative_to(ROOT.resolve());shutil.move(str(path),str(dest))
p=ROOT.parent/'README.md';s=p.read_text('utf-8').replace('V0.4.0 完整生活动画版','V0.5.0 完整撸猫版').replace('吃饭、睡眠、看书、游戏均包含','吃饭、睡眠、看书、游戏、撸猫均包含');p.write_text(s,'utf-8')
print('V0.5.0 petting integrated; prior app backed up; existing preferences preserved.')
p=ROOT/'预览/tools/BuildAssets.cs';s=p.read_text('utf-8')
s=s.replace(' public static void Run(string root) {',' public static void PettingUI(string root) {\n  string ui=Path.Combine(root,"代码","assets","ui");\n  TextImage("诺诺 · 初始",Path.Combine(ui,"title-pet.png"),170,22,"Microsoft YaHei UI",16,false);\n  TextImage("撸猫",Path.Combine(ui,"status-pet.png"),170,20,"Microsoft YaHei UI",12,false);\n }\n public static void Run(string root) {')
s=s.replace('"read","game"},labels={"站立待机","吃饭","睡觉","看书","打游戏"}','"read","game","pet"},labels={"站立待机","吃饭","睡觉","看书","打游戏","撸猫"}');p.write_text(s,'utf-8')
p=ROOT/'预览/PetScene.cs';s=p.read_text('utf-8').replace('settings.Set("game",50);','settings.Set("game",50);settings.Set("pet",75);').replace('loaded.Get("game")!=50)','loaded.Get("game")!=50||loaded.Get("pet")!=75)').replace('five animated activities','six animated activities');p.write_text(s,'utf-8')
p=ROOT/'预览/tools/test_animations.py';s=p.read_text('utf-8').replace("['sleep','read','game']","['sleep','read','game','pet']").replace('four complete sequences','five complete sequences').replace('idle/sleep/read/game joins','idle/sleep/read/game/pet joins');p.write_text(s,'utf-8')
