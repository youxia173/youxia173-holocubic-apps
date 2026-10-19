"""Install only validated laser assets and preserve the V0.5.1 release."""
import json,shutil,math
from export_laser import ROOT as MEDIA,DELIVERY
ROOT=MEDIA.parent.parent;CODE=ROOT/'代码';BACKUP=ROOT/'归档/v0.5.1-激光逗猫接入前'
assert not BACKUP.exists(),'Inspect existing backup before rerun'
facts=json.loads((DELIVERY/'时长信息.json').read_text('utf-8'))['200x150']
assert (DELIVERY/'验证报告.json').exists()
BACKUP.mkdir(parents=True);shutil.copytree(CODE,BACKUP/'代码')
rels=['预览/NonoPreview.cs','预览/PetScene.cs','预览/tools/BuildAssets.cs','预览/tools/package.py','预览/tools/test_animations.py','说明/阶段1使用与验证.md']
for rel in rels:
 dest=BACKUP/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,dest)
for phase in ['intro','loop','outro']:shutil.copy2(DELIVERY/f'{phase}-200x150.gif',CODE/f'assets/nono-laser-{phase}.gif')
layout=json.loads((CODE/'layout.json').read_text('utf-8'));layout['version']='0.6.0'
a=dict(next(x for x in layout['assets'] if x['id']=='pet'))
a.update(id='laser',title='诺诺 · 激光逗猫（完整流程，可设时长）',file='assets/nono-laser-intro.gif',loop_file='assets/nono-laser-loop.gif',outro_file='assets/nono-laser-outro.gif',title_file='assets/ui/title-laser.png',status_file='assets/ui/status-laser.png',loop_seconds=30,**facts['intro'],loop_duration_ms=facts['loop']['duration_ms'],loop_frame_count=facts['loop']['frame_count'],outro_duration_ms=facts['outro']['duration_ms'],outro_frame_count=facts['outro']['frame_count'])
assert not any(x['id']=='laser' for x in layout['assets']);layout['assets'].append(a)
(CODE/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),'utf-8')
for rel in ['代码/main.lua','代码/app.info','代码/info.html','预览/NonoPreview.cs','预览/tools/package.py','说明/阶段1使用与验证.md']:
 p=ROOT/rel;s=p.read_text('utf-8').replace('0.5.1','0.6.0').replace('抱猫修正版','激光逗猫版')
 if rel.endswith('NonoPreview.cs'):
  s=s.replace('五种完整活动','六种完整活动').replace('六种初始科技活动','七种初始科技活动').replace('id=="pet"?"撸猫":activity.title','id=="pet"?"撸猫":id=="laser"?"逗猫":activity.title')
 if rel.endswith('app.info'):s=s.replace('gaming and cat-petting','gaming, cat-petting and laser play').replace('游戏撸猫完整流程','游戏撸猫激光逗猫完整流程')
 if rel.endswith('package.py'):s=s.replace('游戏、撸猫均为','游戏、撸猫、激光逗猫均为')
 if rel.endswith('info.html'):s=s.replace('</html>','<p>新增激光逗猫：取笔→红点引导猫扑击追逐→收笔→待机。逗猫时长独立设置，循环完整结束后收尾。</p></html>')
 if rel.endswith('.md'):
  s=s.replace('“游戏时长”和“撸猫时长”','“游戏时长”“撸猫时长”和“逗猫时长”')
  # Keep the prior motion-correction history accurately versioned.
  s=s.replace('## V0.6.0 抱猫动作修正','## V0.5.1 抱猫动作修正').replace('## V0.6.0 撸猫','## V0.5.1 撸猫')
  loops=math.ceil(30000/facts['loop']['duration_ms'])
  s+=f"\n## V0.6.0 激光逗猫\n\n诺诺取出激光笔，猫盯住地面红点并扑击追逐，结束后关闭红点、收笔，猫回原位坐好，诺诺回待机。逗猫时长独立设置5–600秒，默认30秒。循环每圈{facts['loop']['duration_ms']/1000:.2f}秒，默认{loops}圈；取笔约{facts['intro']['duration_ms']/1000:.2f}秒、收笔约{facts['outro']['duration_ms']/1000:.2f}秒另计。设置在下一次活动生效。\n\n代码素材`代码/assets/nono-laser-*.gif`；原始关键帧、视频、提示词和接点在`预览/激光逗猫/`；素材`预览/素材/诺诺-激光逗猫动画/`含透明GIF、三圈示例及预览页。保留V0.5.1腋下抱猫修正。尚需真机性能验证。\n"
 p.write_text(s,'utf-8')
p=ROOT/'预览/tools/BuildAssets.cs';s=p.read_text('utf-8').replace(' public static void Run(string root) {',' public static void LaserUI(string root) {\n  string ui=Path.Combine(root,"代码","assets","ui");\n  TextImage("诺诺 · 初始",Path.Combine(ui,"title-laser.png"),170,22,"Microsoft YaHei UI",16,false);\n  TextImage("激光逗猫",Path.Combine(ui,"status-laser.png"),170,20,"Microsoft YaHei UI",12,false);\n }\n public static void Run(string root) {').replace('"game","pet"},labels=','"game","pet","laser"},labels=').replace('"打游戏","撸猫"};','"打游戏","撸猫","激光逗猫"};');p.write_text(s,'utf-8')
p=ROOT/'预览/PetScene.cs';s=p.read_text('utf-8').replace('settings.Set("pet",75);','settings.Set("pet",75);settings.Set("laser",40);').replace('loaded.Get("pet")!=75)','loaded.Get("pet")!=75||loaded.Get("laser")!=40)').replace('six animated activities','seven animated activities');p.write_text(s,'utf-8')
p=ROOT/'预览/tools/test_animations.py';s=p.read_text('utf-8').replace("['sleep','read','game','pet']","['sleep','read','game','pet','laser']").replace('five complete sequences','six complete sequences').replace('idle/sleep/read/game/pet joins','idle/sleep/read/game/pet/laser joins');p.write_text(s,'utf-8')
for path in (ROOT/'安装包').glob('*.zip'):
 dest=BACKUP/path.name;assert path.resolve().is_relative_to(ROOT.resolve()) and dest.resolve().is_relative_to(ROOT.resolve());shutil.move(str(path),str(dest))
p=ROOT.parent/'README.md';s=p.read_text('utf-8').replace('V0.5.1 抱猫修正版','V0.6.0 激光逗猫版').replace('游戏、撸猫均包含','游戏、撸猫、激光逗猫均包含');p.write_text(s,'utf-8')
print('Installed V0.6.0 laser activity. Generate LaserUI, then verify and package.')
