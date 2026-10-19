import json,importlib.util
import numpy as np
from PIL import Image,ImageDraw
from export_laser import ROOT,DELIVERY
spec=importlib.util.spec_from_file_location('validator','C:/Users/youxia173/.codex/skills/nono-animation-workflow/scripts/validate_sequence.py');validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)
facts=json.loads((DELIVERY/'时长信息.json').read_text('utf-8'));reports=[]
for size in ['200x150','640x480']:
 r=validator.validate(*(DELIVERY/f'{phase}-{size}.gif' for phase in ['intro','loop','outro']));assert r['ok'],r;reports.append(r)
def frame(path,index):
 with Image.open(path) as im:
  im.seek(min(index,im.n_frames-1) if index>=0 else im.n_frames+index);a=np.array(im.convert('RGBA'));a[a[:,:,3]==0,:3]=0;return a
idle=frame(ROOT.parent.parent/'代码/assets/nono-idle-cat.gif',0)
assert np.array_equal(idle,frame(DELIVERY/'intro-200x150.gif',0))
assert np.array_equal(idle,frame(DELIVERY/'outro-200x150.gif',-1))
(DELIVERY/'验证报告.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),'utf-8')
html=(DELIVERY.parent/'诺诺-看书与游戏动画/打开动画预览.html').read_text('utf-8')
html=html.replace('看书与打游戏','激光逗猫').replace('<option>看书</option><option>打游戏</option>','<option>逗猫</option>')
html=html.replace('从站立开始，取出道具坐下，持续活动，再收好道具回到站立。白猫在旁边陪着。','诺诺取出激光笔，白猫追逐地面红点并扑击；结束后收笔，猫回原位坐好。')
start=html.index('const facts=');end=html.index(';const pet=',start)
html=html[:start]+'const facts='+json.dumps({'逗猫':facts['640x480']},ensure_ascii=False)+html[end:]
html=html.replace("activity.value+'/'+phase",'phase').replace('取出道具、坐下','取出激光笔').replace('收起道具、站起','收笔、回待机')
(DELIVERY/'打开逗猫预览.html').write_text(html,'utf-8')
ms=facts['640x480']['loop']['duration_ms']
(DELIVERY/'使用说明.txt').write_text(f'完整流程：待机→取出激光笔→猫盯住红点、扑击追逐循环→关闭红点、收笔→回待机。\n循环每圈{ms/1000:.2f}秒，循环次数=ceil(目标秒数*1000/{ms})，准备和收尾另计。\n提供200x150与640x480真透明GIF、完整三圈示例和可切换背景预览。软件V0.6.0支持独立设置逗猫时长。\n关键帧使用内置图像生成，视频使用本地Wan2.2和RIFE。原始素材、提示词在项目预览/激光逗猫。','utf-8')
sheet=Image.new('RGB',(1600,900),'#d8e1ed');d=ImageDraw.Draw(sheet)
for row,bg in enumerate(['white','#172132','checker']):
 for col,(phase,index) in enumerate([('intro',60),('intro',130),('loop',30),('loop',100),('outro',80)]):
  tile=Image.new('RGBA',(320,240),'#eff2f5' if bg=='checker' else bg)
  if bg=='checker':
   t=ImageDraw.Draw(tile)
   for x in range(0,320,16):
    for y in range(0,240,16):
     if (x//16+y//16)%2:t.rectangle((x,y,x+15,y+15),fill='#aebcce')
  im=Image.fromarray(frame(DELIVERY/f'{phase}-640x480.gif',index)).resize((320,240),Image.Resampling.LANCZOS);tile.alpha_composite(im);sheet.paste(tile.convert('RGB'),(col*320,row*300));d.text((col*320+8,row*300+250),f'{phase} / {index} / {bg}',fill='black')
sheet.save(DELIVERY/'透明背景检查.jpg',quality=92)
print('PASS: two sizes, runtime idle joins, loop closure, transparency, timing.')
