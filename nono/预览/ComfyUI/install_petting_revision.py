"""Install the corrected paws-down sequence without changing user preferences."""
import json,shutil,math
from export_petting_revision import ROOT as MEDIA,DELIVERY
ROOT=MEDIA.parent.parent;CODE=ROOT/'代码';backup=ROOT/'归档/v0.5.0-抱猫姿势修正前'
assert not backup.exists(),'Inspect existing backup before rerun'
facts=json.loads((DELIVERY/'时长信息.json').read_text('utf-8'))['200x150']
backup.mkdir(parents=True);shutil.copytree(CODE,backup/'代码')
for phase in ['intro','loop','outro']:shutil.copy2(DELIVERY/f'{phase}-200x150.gif',CODE/f'assets/nono-pet-{phase}.gif')
layout=json.loads((CODE/'layout.json').read_text('utf-8'));layout['version']='0.5.1';a=next(a for a in layout['assets'] if a['id']=='pet')
a.update(**facts['intro'],loop_duration_ms=facts['loop']['duration_ms'],loop_frame_count=facts['loop']['frame_count'],outro_duration_ms=facts['outro']['duration_ms'],outro_frame_count=facts['outro']['frame_count'])
(CODE/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),'utf-8')
for rel in ['代码/main.lua','代码/app.info','代码/info.html','预览/NonoPreview.cs','预览/tools/package.py','说明/阶段1使用与验证.md']:
 p=ROOT/rel;dest=backup/rel
 if not dest.exists():dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 s=p.read_text('utf-8').replace('0.5.0','0.5.1').replace('完整撸猫版','抱猫修正版')
 if rel.endswith('.md'):
  loops=math.ceil(30000/facts['loop']['duration_ms'])
  timing=f"准备约{facts['intro']['duration_ms']/1000:.2f}秒、循环每圈{facts['loop']['duration_ms']/1000:.2f}秒、放下及站起约{facts['outro']['duration_ms']/1000:.2f}秒；默认{loops}圈，总计约{(facts['intro']['duration_ms']+loops*facts['loop']['duration_ms']+facts['outro']['duration_ms'])/1000:.2f}秒。"
  s=s.replace('准备约15.53秒、循环每圈5.03秒、放下及站起约10.53秒；默认6圈，总计约56.24秒。',timing)
  s=s.replace('过程保存在`预览/完整撸猫/`；桌面`诺诺-完整撸猫动画`','过程保存在`预览/撸猫修正版/`；桌面`诺诺-撸猫修正版`')
  s+='\n## V0.5.1 抱猫动作修正\n\n双手从猫两个前肢腋下托起，后腿自然悬垂，再收进怀里改由前臂托住胸腹。猫在怀里背朝上、腹朝下，四脚朝下；诺诺保持低蹲。放下时保持同一蹲姿和机位，落地后单独松手。新素材和实际提交提示词在`预览/撸猫修正版/`；素材位于`预览/素材/诺诺-撸猫修正版/`。时长设置及原有活动保持不变。\n'
 if rel.endswith('info.html'):s=s.replace('</html>','<p>抱猫姿势修正：背朝上、四脚朝下。先托稳再抬离地面，放下时保持同一蹲姿及人物比例。</p></html>')
 p.write_text(s,'utf-8')
for path in (ROOT/'安装包').glob('*.zip'):
 dest=backup/path.name;assert path.resolve().is_relative_to(ROOT.resolve()) and dest.resolve().is_relative_to(ROOT.resolve());shutil.move(str(path),str(dest))
p=ROOT.parent/'README.md';s=p.read_text('utf-8').replace('V0.5.0 完整撸猫版','V0.5.1 抱猫修正版');p.write_text(s,'utf-8')
print('Installed V0.5.1 corrected petting; settings preserved.')
