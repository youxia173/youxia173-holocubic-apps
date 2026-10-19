"""Resumable six-clip sleep/idle production using the user's Wan workflow."""
import json
import sys
from pathlib import Path
import nono_video as api

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parent.parent / '完整睡眠'
COMMON = '固定正面略俯视镜头，纯绿色背景，没有阴影平面。银蓝色长发蓝眼睛Q版女孩诺诺，白色青边科技连衣裙、白色独立袖子深蓝袖口、白色长袜与白青科技鞋，三角发夹。保持首尾图的同一角色、衣服、身体比例，一只白猫。动作自然连贯，重心贴地，人物不漂浮，道具不出现。'
CLIPS = [
 ('01-sit','S01-站立.png','S02-坐下.png','intro','诺诺站在地上，困倦地眨眼，小幅弯膝降低重心，用左手扶地，缓慢侧坐在地面，双腿自然弯到右侧，再右手遮嘴轻轻打一个哈欠，白猫在左侧原地坐着也打一个小哈欠。先坐稳再打哈欠，不能忽然跪坐或跳变。'),
 ('02-lie','S02-坐下.png','S03-躺睡.png','intro','诺诺始终面朝镜头，鼻子朝前，身体不转向背面也不翻滚。她从侧坐姿势开始，放下遮嘴的手，把双手慢慢叠放到画面左侧靠近白猫的地面。她的头始终向画面左下方移动，先左肩下降，再把左脸缓缓枕在画面左侧的双手上。她的双脚始终向画面右侧伸展，头在画面左边、脚在画面右边，绝不能反过来。整个动作是一条缓慢单向侧躺轨迹，没有滚动，没有中途四肢着地爬行。身体和脸始终保持面向镜头的三分之四角度，脸部一直可见。最后闭眼侧躺睡着。白猫留在画面左侧，原地蜷起来闭眼睡着。'),
 ('03-sleep','S03-躺睡.png','S03-躺睡.png','loop','五秒无缝睡眠循环。诺诺始终侧躺闭眼，头枕双手，不醒来、不起身。仅有胸肩轻柔的呼吸起伏，发梢微微摆动后回原位。白猫始终蜷睡，身体轻柔呼吸，耳朵轻微动一下后复位。一个完整缓慢呼吸周期，首尾姿态与运动速度一致。嘴保持自然放松，绝不张眼或大幅移动。'),
 ('04-wake','S03-躺睡.png','S02-坐下.png','outro','诺诺从侧躺睡姿缓缓醒来，先睁眼，轻轻抬起头，双手撑地把上半身抬起来，腿保持自然弯曲，慢慢恢复侧坐姿势。坐稳后右手遮嘴打一个小哈欠。白猫舒展身体，从蜷睡变回坐姿，也轻轻打哈欠。动作按顺序发生，不能播放倒放睡倒动作，不要悬空。'),
 ('05-stand','S02-坐下.png','S01-站立.png','outro','诺诺侧坐着，放下遮嘴的手，双脚收回身体下方，用手支撑地面，先蹲起再缓慢站直，放松双臂到身体两侧，恢复首尾参考里的自然站立待机，睁开蓝眼睛微笑。白猫始终在左侧坐着，恢复精神。头发自然垂落，不倒放，不跳起，不改变服装。'),
 ('06-idle','S01-站立.png','S01-站立.png','idle','五秒无缝站立待机循环。诺诺双脚始终稳定站在地上，身体极轻微呼吸起伏，温柔眨眼一次，发梢轻微摆动再复位，双手保持在身侧。白猫始终坐在左侧，眨眼，尾尖小幅摆动后回原位。保持角色大小和位置，首尾姿态和速度一致，不走路，不抬脚，不蹲下，不出现道具。'),
]

def submit():
    current = api.request('/object_info')
    template = json.loads((ROOT.parent/'连续喂饭/完整动画/04-坐下吃饭/api_prompt.json').read_text('utf-8'))
    assert all(n['class_type'] in current for n in template.values())
    uploads = {}
    for name, start, end, phase, action in CLIPS:
        folder=ROOT/name;folder.mkdir(parents=True,exist_ok=True)
        if (folder/'job.json').exists():
            print(name,'already submitted');continue
        for file in [start,end]:
            if file not in uploads:uploads[file]=api.upload(ROOT/'关键帧'/file)
        prompt=json.loads(json.dumps(template))
        prompt['16']['inputs']['image']=uploads[start]
        prompt['9']['inputs']['image']=uploads[end]
        prompt['10']['inputs']['text']=COMMON+action
        prompt['23']['inputs']['text']+='，床，被子，枕头，食物，餐具，魔法，额外猫，换衣服，字幕，Z字符，地面阴影，镜头移动'
        prompt['104']['inputs']['seed']=1732026101900+int(name[:2])+(100 if name=='02-lie' else 0)
        prompt['18']['inputs']['filename_prefix']='Nono/sleep_'+name
        (folder/'提示词.txt').write_text(COMMON+action,'utf-8')
        (folder/'api_prompt.json').write_text(json.dumps(prompt,ensure_ascii=False,indent=2),'utf-8')
        job=api.request('/prompt',json.dumps({'prompt':prompt,'client_id':'nono-sleep'}).encode(),{'Content-Type':'application/json'})
        job.update(start=start,end=end,phase=phase)
        (folder/'job.json').write_text(json.dumps(job,ensure_ascii=False,indent=2),'utf-8')
        print(name,job['prompt_id'],flush=True)
    (ROOT/'分镜.json').write_text(json.dumps([dict(segment_id=n,start_image=s,end_image=e,phase=p,duration_target_s=5,action=a) for n,s,e,p,a in CLIPS],ensure_ascii=False,indent=2),'utf-8')

if __name__=='__main__':
    if sys.argv[1]=='submit':submit()
    else:
        for name,*_ in CLIPS:
            if (ROOT/name/'job.json').exists():
                if list((ROOT/name).glob('*.mp4')):print(name,'downloaded');continue
                job=json.loads((ROOT/name/'job.json').read_text('utf-8'))
                item=api.request('/history/'+job['prompt_id']).get(job['prompt_id'])
                if not item:print(name,'pending');continue
                api.status(type('Args',(),{'output':str(ROOT/name)})())
