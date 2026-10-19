"""Human-facing local preview and instructions for the standalone GIF collection."""
import json
from pathlib import Path
from export_leisure import DELIVERY
DELIVERY.mkdir(parents=True,exist_ok=True)
data={}
for title in ['看书','打游戏']:
 data[title]=json.loads((DELIVERY/title/'时长与接入信息.json').read_text('utf-8'))['sizes']['640x480']
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>诺诺 · 看书与打游戏</title>
<style>body{margin:28px auto;max-width:950px;font:16px system-ui;background:#edf3fc;color:#283851}h1{font-size:25px}.controls{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:18px 0}button,select,input{font:inherit;border:1px solid #9fb6d4;border-radius:9px;padding:9px;background:white}button{cursor:pointer}input{width:80px}#stage{width:640px;max-width:100%;height:480px;border:1px solid #94abc7;border-radius:12px;display:grid;place-items:center}#pet{width:640px;max-width:100%;height:480px;object-fit:contain}.checker{background-color:#fff;background-image:linear-gradient(45deg,#dde4ee 25%,transparent 25%),linear-gradient(-45deg,#dde4ee 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#dde4ee 75%),linear-gradient(-45deg,transparent 75%,#dde4ee 75%);background-size:24px 24px;background-position:0 0,0 12px,12px -12px,-12px 0}p{line-height:1.7}.note{color:#52657d;font-size:14px}</style>
<h1>诺诺 · 看书与打游戏</h1><p>从站立开始，取出道具坐下，持续活动，再收好道具回到站立。白猫在旁边陪着。</p>
<div class="controls"><select id="activity"><option>看书</option><option>打游戏</option></select><label>持续时间 <input id="seconds" type="number" min="5" max="600" value="30"> 秒</label><button id="play">播放完整流程</button><button id="repeat">只看循环段</button><button id="stop">回待机</button></div>
<div class="controls"><span>检查透明背景：</span><select id="background"><option value="checker">棋盘格</option><option value="white">白色</option><option value="#172132">深色</option></select></div>
<div id="stage" class="checker"><img id="pet" alt="诺诺动画"></div><p id="status"></p>
<p class="note">循环按完整圈数向上取整，持续时间不包含准备和收拾。GIF 是真透明背景；浏览器切换独立文件可能存在少量加载延迟。完整流程 GIF 可直接检查连续播放。</p>
<script>const facts=__DATA__;const pet=document.querySelector('#pet'),activity=document.querySelector('#activity'),status=document.querySelector('#status');let timer,token=0;const names={intro:'取出道具、坐下',loop:'持续活动',outro:'收起道具、站起',idle:'待机'};
function show(phase,cb){const mine=++token;clearTimeout(timer);pet.onload=()=>{if(mine!==token)return;if(cb)timer=setTimeout(cb,facts[activity.value][phase].duration_ms)};pet.src=activity.value+'/'+phase+'-640x480.gif?play='+token;}
function idle(){status.textContent='待机';show('idle')}
document.querySelector('#play').onclick=()=>{const s=Math.max(5,Math.min(600,Number(document.querySelector('#seconds').value)||30));const n=Math.ceil(s*1000/facts[activity.value].loop.duration_ms);status.textContent=names.intro;show('intro',()=>{status.textContent='持续'+n+'圈，约'+(n*facts[activity.value].loop.duration_ms/1000).toFixed(2)+'秒';show('loop',()=>{});const mine=token;pet.onload=()=>{if(token!==mine)return;timer=setTimeout(()=>{status.textContent=names.outro;show('outro',idle)},n*facts[activity.value].loop.duration_ms)}})};
document.querySelector('#repeat').onclick=()=>{status.textContent='核心动作无限循环';show('loop')};document.querySelector('#stop').onclick=idle;activity.onchange=idle;
document.querySelector('#background').onchange=e=>{const stage=document.querySelector('#stage');stage.className=e.target.value==='checker'?'checker':'';stage.style.backgroundColor=e.target.value==='checker'?'':e.target.value};idle();</script></html>'''
(DELIVERY/'打开动画预览.html').write_text(html.replace('__DATA__',json.dumps(data,ensure_ascii=False)),'utf-8')
(DELIVERY/'使用说明.txt').write_text('''诺诺 · 看书与打游戏透明 GIF

打开“打开动画预览.html”选择活动、持续秒数和背景即可检查完整动作。
各活动目录包含：
intro：待机 → 取出道具 → 坐下。单次播放。
loop：核心动作。无限循环，可自定义重复圈数。
outro：收起道具 → 起身 → 回待机。单次播放。
idle：与本套调色板、接点匹配的白猫待机。
完整流程-三圈：待机、准备、3圈核心动作、收拾，全流程循环示例。

640x480 用于桌面和素材检查；200x150 是设备角色素材尺寸，不等于整个320x240软件窗口。
时长按 JSON 里的实际毫秒数，循环次数=向上取整(目标秒数*1000/循环毫秒数)。
默认查看30秒，准备、收拾另算。GIF为二值透明，播放器的性能可能影响显示帧率。
本次交付动画素材，未改动已安装桌宠及其设置。
关键帧、提示词、原始视频与生成任务保留在项目“预览/看书与游戏”目录。
角色关键帧使用内置图像生成工具，运动使用本地 Wan2.2 首尾帧工作流，接点使用 RIFE。
''','utf-8')
print(DELIVERY)
