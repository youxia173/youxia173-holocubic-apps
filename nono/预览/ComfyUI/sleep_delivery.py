from delivery_paths import DELIVERY_ROOT
"""Write a local transparent-background preview and human-facing delivery notes."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent/'完整睡眠'
DEST=DELIVERY_ROOT / '诺诺-完整睡眠动画'

def write():
    facts=json.loads((ROOT/'export.json').read_text('utf-8'))
    duration={k:v['duration_ms'] for k,v in facts.items()}
    html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>诺诺 · 完整睡眠</title>
<style>body{font-family:Segoe UI,Microsoft YaHei,sans-serif;background:#ecf3f8;color:#23374b;max-width:900px;margin:32px auto;padding:0 20px}button,input,select{font:inherit;padding:8px;border:1px solid #b7ccd9;border-radius:6px}#stage{margin:20px 0;border:1px solid #a7becd;border-radius:12px;display:grid;place-items:center;min-height:480px;background:repeating-conic-gradient(#dce5ed 0 25%,#f7fafc 0 50%) 0/32px 32px}img{width:640px;height:480px;max-width:100%;object-fit:contain}small{color:#54697d}</style>
<h1>诺诺 · 完整睡眠</h1><p>站立 → 坐下躺睡 → 呼吸循环 → 醒来起身 → 站立</p>
<label>睡眠时长 <input id="seconds" type="number" value="15" min="5" max="600" step="5" style="width:80px"> 秒</label>
<button id="play">完整播放</button> <button id="loop">只看睡眠循环</button>
<select id="background"><option value="check">棋盘底</option><option value="white">白底</option><option value="#151b23">深色底</option></select>
<div id="stage"><img id="pet" alt="诺诺睡眠动画"></div><p id="status"></p>
<small>设置指中间睡眠时间，向上取整至完整呼吸循环；入睡和醒来时间另计。背景色仅用于检查透明边缘，GIF本身透明。</small>
<script>
const durations=__DURATIONS__;
const files={intro:'诺诺-入睡-透明-640x480.gif',loop:'诺诺-睡眠循环-透明-640x480.gif',outro:'诺诺-醒来-透明-640x480.gif',idle:'诺诺-白猫待机-透明-640x480.gif'};
const pet=document.getElementById('pet'),status=document.getElementById('status');let timer,run=0;

function show(phase,text,then,ms){clearTimeout(timer);const token=++run;pet.onload=()=>{if(token===run&&then)timer=setTimeout(then,ms);};pet.src=files[phase]+'?play='+token;status.textContent=text;}
document.getElementById('play').onclick=()=>{let n=Number(document.getElementById('seconds').value);if(!Number.isFinite(n))n=15;n=Math.min(600,Math.max(5,n));const loops=Math.ceil(n*1000/durations.loop);show('intro','正在坐下、躺好…',()=>show('loop','正在睡觉：'+loops+'个呼吸循环，约'+(loops*durations.loop/1000).toFixed(2)+'秒',()=>show('outro','正在醒来、起身…',()=>show('idle','已回到待机'),durations.outro),loops*durations.loop),durations.intro);};
document.getElementById('loop').onclick=()=>show('loop','连续睡眠循环');
document.getElementById('background').onchange=e=>document.getElementById('stage').style.background=e.target.value==='check'?'':e.target.value;
show('idle','待机中');
</script></html>'''.replace('__DURATIONS__',json.dumps(duration))
    (DEST/'打开睡眠预览.html').write_text(html,'utf-8')
    (DEST/'使用说明.txt').write_text(f'''诺诺 V0.3.0 完整睡眠动画

1. 软件中选择“睡觉”，会依次入睡、循环呼吸、醒来并回待机。
2. 面板独立设置进食/睡眠秒数（5–600），下次对应活动生效，重启保留。
3. 睡眠每圈{duration['loop']/1000:.2f}秒，按完整循环向上取整；另加入睡{duration['intro']/1000:.2f}秒、醒来{duration['outro']/1000:.2f}秒。
4. 640×480透明GIF适合素材预览；nono-*.gif是软件使用的200×150角色画面。
5. 打开“打开睡眠预览.html”可切换背景查看边缘，也可单独重复睡眠或播放全流程。
6. 关键帧采用内置图像生成；视频由用户本机Wan首尾帧工作流生成，RIFE优化衔接和呼吸速度。绿底仅存在于中间视频。
''','utf-8')

if __name__=='__main__':write()
