"""Build a local animation preview and light/dark/checker inspection sheets."""
import json
from PIL import Image,ImageDraw
from export_ramen import OUT,ROOT

html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>诺诺 · 吃拉面</title>
<style>body{font:16px system-ui;background:#edf3f7;color:#25354d;margin:24px}button{padding:10px;margin:5px;border:0;border-radius:8px;cursor:pointer}#stage{width:640px;height:480px;max-width:95vw;border:1px solid #9bb8c9;background:repeating-conic-gradient(#ddd 0% 25%,#fff 0% 50%) 0/24px 24px}img{width:100%;height:100%;object-fit:contain}p{max-width:700px}</style>
<h1>诺诺 · 吃拉面</h1><p>完整流程：待机 → 拿碗坐下 → 吃面三圈 → 收碗站起。软件里与原吃饭随机播放，共用进食时长。</p>
<button onclick="stage.style.background='#fff'">浅色背景</button><button onclick="stage.style.background='#20252d'">深色背景</button><button onclick="stage.style.background='repeating-conic-gradient(#ddd 0% 25%,#fff 0% 50%) 0/24px 24px'">棋盘背景</button>
<div id="stage"><img src="诺诺-吃拉面-完整流程-三圈.gif" alt="诺诺吃拉面完整动画"></div>
<p><a href="intro-640x480.gif">准备段</a> · <a href="loop-640x480.gif">可循环吃面</a> · <a href="outro-640x480.gif">收拾段</a></p>
<p>素材为真实透明 GIF。循环次数按设置时长向上取整；准备、收拾时间另计。此页面离线可用。</p></html>'''
(OUT/'预览.html').write_text(html,'utf-8')
for phase in ['intro','loop','outro']:
    with Image.open(OUT/(phase+'-640x480.gif')) as im:
        sheet=Image.new('RGB',(1200,8*165),(235,240,245));d=ImageDraw.Draw(sheet)
        for row in range(8):
            i=round(row*(im.n_frames-1)/7);im.seek(i);frame=im.convert('RGBA').resize((200,150))
            for col in range(3):
                bg=Image.new('RGB',(200,150),'white' if col==0 else '#20252d')
                if col==2:
                    draw=ImageDraw.Draw(bg)
                    for y in range(0,150,12):
                        for x in range(0,200,12):draw.rectangle((x,y,x+11,y+11),fill='#ddd' if (x//12+y//12)%2 else 'white')
                bg.paste(frame,(0,0),frame);sheet.paste(bg,(col*400,row*165));sheet.paste(bg.resize((200,150)),(col*400+200,row*165))
            d.text((4,row*165+150),f'{phase} frame {i}',fill='black')
        sheet.save(ROOT/(phase+'-alpha-check.jpg'))
print('Created preview and alpha inspection sheets')
