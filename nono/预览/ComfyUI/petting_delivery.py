import json,importlib.util
import numpy as np
from PIL import Image,ImageDraw
from export_petting import ROOT,DELIVERY
spec=importlib.util.spec_from_file_location('validator','C:/Users/youxia173/.codex/skills/nono-animation-workflow/scripts/validate_sequence.py');validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)
facts=json.loads((DELIVERY/'时长信息.json').read_text('utf-8'));reports=[]
for size in ['200x150','640x480']:
 r=validator.validate(*(DELIVERY/f'{phase}-{size}.gif' for phase in ['intro','loop','outro']));assert r['ok'],r;reports.append(r)
# Prove the runtime idle and new sequence share the actual decoded boundary.
def frame(path,index):
 with Image.open(path) as im:
  im.seek(index if index>=0 else im.n_frames+index);a=np.array(im.convert('RGBA'));a[a[:,:,3]==0,:3]=0;return a
idle=frame(ROOT.parent.parent/'代码/assets/nono-idle-cat.gif',0)
assert np.array_equal(idle,frame(DELIVERY/'intro-200x150.gif',0))
assert np.array_equal(idle,frame(DELIVERY/'outro-200x150.gif',-1))
(DELIVERY/'验证报告.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),'utf-8')
html=(DELIVERY.parent/'诺诺-看书与游戏动画/打开动画预览.html').read_text('utf-8')
html=html.replace('看书与打游戏','完整撸猫').replace('<option>看书</option><option>打游戏</option>','<option>撸猫</option>')
html=html.replace('从站立开始，取出道具坐下，持续活动，再收好道具回到站立。白猫在旁边陪着。','白猫蹭腿撒娇，诺诺蹲下摸头并抱入怀里；抚摸结束后放下猫，回到待机。')
start=html.index('const facts=');end=html.index(';const pet=',start)
html=html[:start]+'const facts='+json.dumps({'撸猫':facts['640x480']},ensure_ascii=False)+html[end:]
html=html.replace("activity.value+'/'+phase",'phase').replace('取出道具、坐下','蹭腿、摸头、抱起').replace('收起道具、站起','放下白猫、回待机')
(DELIVERY/'打开撸猫预览.html').write_text(html,'utf-8')
(DELIVERY/'使用说明.txt').write_text('完整撸猫：待机→白猫蹭小腿→蹲下摸头→抱入怀里→抚摸循环→放下白猫→起身回待机。\nintro与outro各播放一次；loop为5.03秒完整循环，可重复指定圈数。循环次数=ceil(目标秒数*1000/5030)，准备和收尾时间另计。默认30秒为6圈。\n提供200x150设备角色素材及640x480桌面素材，均为真透明GIF，约32FPS；另附完整三圈示例与可切换背景的预览页。\n软件V0.5.0增加独立撸猫时长5–600秒，保留现有活动设置。\n关键帧使用内置图像工具，动作使用本地Wan2.2首尾帧视频工作流及RIFE接点；原图、视频、提示词保存在项目预览/完整撸猫。\n','utf-8')
sheet=Image.new('RGB',(1600,900),'#d8e1ed');d=ImageDraw.Draw(sheet)
for row,bg in enumerate(['white','#172132','checker']):
 for col,(phase,index) in enumerate([('intro',60),('intro',230),('intro',425),('loop',70),('outro',80)]):
  tile=Image.new('RGBA',(320,240),'#eff2f5' if bg=='checker' else bg)
  if bg=='checker':
   t=ImageDraw.Draw(tile)
   for x in range(0,320,16):
    for y in range(0,240,16):
     if (x//16+y//16)%2:t.rectangle((x,y,x+15,y+15),fill='#aebcce')
  im=Image.fromarray(frame(DELIVERY/f'{phase}-640x480.gif',index)).resize((320,240),Image.Resampling.LANCZOS);tile.alpha_composite(im);sheet.paste(tile.convert('RGB'),(col*320,row*300));d.text((col*320+8,row*300+250),f'{phase} / {index} / {bg}',fill='black')
sheet.save(DELIVERY/'透明背景检查.jpg',quality=92)
print('PASS: two sizes, actual runtime idle joins, loop closure, alpha, phase timing.')
