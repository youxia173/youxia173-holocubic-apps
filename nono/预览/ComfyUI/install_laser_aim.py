from delivery_paths import DELIVERY_ROOT
import json,shutil,math
from pathlib import Path
from laser_aim_revision import ROOT as MEDIA
ROOT=MEDIA.parent.parent;CODE=ROOT/'代码';DELIVERY=DELIVERY_ROOT / '诺诺-激光指向修正版'
backup=ROOT/'归档/v0.6.0-激光指向修正前';assert not backup.exists()
assert (DELIVERY/'验证报告.json').exists()
facts=json.loads((DELIVERY/'时长信息.json').read_text('utf-8'))['200x150']
backup.mkdir(parents=True);shutil.copytree(CODE,backup/'代码')
for phase in ['intro','loop','outro']:shutil.copy2(DELIVERY/f'{phase}-200x150.gif',CODE/f'assets/nono-laser-{phase}.gif')
p=CODE/'layout.json';layout=json.loads(p.read_text('utf-8'));layout['version']='0.6.1';a=next(x for x in layout['assets'] if x['id']=='laser')
a.update(**facts['intro'],loop_duration_ms=facts['loop']['duration_ms'],loop_frame_count=facts['loop']['frame_count'],outro_duration_ms=facts['outro']['duration_ms'],outro_frame_count=facts['outro']['frame_count']);p.write_text(json.dumps(layout,ensure_ascii=False,indent=2),'utf-8')
for rel in ['代码/main.lua','代码/app.info','代码/info.html','预览/NonoPreview.cs','预览/tools/package.py','说明/阶段1使用与验证.md']:
 p=ROOT/rel;dest=backup/rel
 if not dest.exists():dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 s=p.read_text('utf-8').replace('0.6.0','0.6.1').replace('激光逗猫版','激光指向修正版')
 if rel.endswith('.md'):
  loops=math.ceil(30000/facts['loop']['duration_ms'])
  s=s.replace('循环每圈4.03秒，默认8圈；取笔约4.53秒、收笔约5.53秒另计。',f"循环每圈{facts['loop']['duration_ms']/1000:.2f}秒，默认{loops}圈；取笔约{facts['intro']['duration_ms']/1000:.2f}秒、收笔约{facts['outro']['duration_ms']/1000:.2f}秒另计。")
  s=s.replace('`预览/激光逗猫/`','`预览/激光逗猫指向修正版/`').replace('`诺诺-激光逗猫动画/`','`诺诺-激光指向修正版/`')
  s+='\nV0.6.1修正：地面光点从左向右、再从右向左往返，白猫顺着移动方向追逐；细红线从笔尖连接地面圆点，手腕跟随扫动。\n'
 p.write_text(s,'utf-8')
for path in (ROOT/'安装包').glob('*.zip'):
 dest=backup/path.name;assert path.resolve().is_relative_to(ROOT.resolve()) and dest.resolve().is_relative_to(ROOT.resolve());shutil.move(str(path),str(dest))
p=ROOT.parent/'README.md';p.write_text(p.read_text('utf-8').replace('V0.6.0 激光逗猫版','V0.6.1 激光指向修正版'),'utf-8')
print('Installed V0.6.1 laser aim revision; prior release and settings preserved.')
