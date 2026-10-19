"""Six ordered clips for the complete cat-affection activity."""
import sys,shutil,json
from pathlib import Path
import leisure_sequence as pipeline
ROOT=Path(__file__).resolve().parent.parent/'完整撸猫'
pipeline.ROOT=ROOT
pipeline.COMMON='固定镜头和纯绿色背景，银蓝长发白青科技裙诺诺和唯一一只小白猫，保持参考衣服、大小、三角发夹和猫项圈。动作缓慢自然，身体重心贴地，不跳切不瞬移，手和猫始终分离清楚，猫身体有支撑，无额外动物。'
pipeline.CLIPS=[
 ('01-rub','idle.png','rub.png','白猫从画面左侧坐姿站起，向右走两小步到诺诺画面左侧的小腿边，先用脸颊轻轻蹭她的小腿，再用侧身亲昵蹭一下，尾巴自然竖起。诺诺双脚原地站稳，微微低头看猫并温柔微笑，双手在身侧。猫在脚外侧，不穿过腿和鞋，最后脸颊贴近小腿。'),
 ('02-crouch','rub.png','crouch.png','白猫留在诺诺脚边，四爪着地。诺诺慢慢弯膝降低重心，双鞋始终踩地，蹲下来，右手缓缓落到猫头上，在两耳之间轻轻抚摸一下，左手放在自己的膝上。白猫舒服地闭眼，身体不消失不被压扁。先蹲稳再摸头，最后停在温柔摸头的姿态。'),
 ('03-lift','crouch.png','hug.png','诺诺从蹲姿开始，先停止摸头，双手靠近猫，一只手托住猫胸前，另一只手托住猫肚子和后腿，慢慢把白猫从地面抱到自己胸前。猫四爪随身体一起离地，没有留在地上的第二只猫。诺诺顺势慢慢坐到地面，腿弯在身侧，把猫横抱在怀里，猫头始终朝画面左侧，后腿朝右。一条手臂一直托住猫的躯干，另一只手轻放猫头。全过程猫形状完整，不瞬移，不抛起。'),
 ('04-loop','hug.png','hug.png','五秒温柔撸猫循环。诺诺始终侧坐稳稳抱猫，左臂持续托住猫身体和后腿，右手从猫头顶慢慢抚摸到颈背，再轻抬几厘米返回头顶，完成两次轻柔抚摸。诺诺温柔眨眼微笑，头轻轻靠近猫再回原处。唯一的白猫始终横躺怀里，头朝画面左边，舒服闭眼，尾尖和小爪轻轻动后复位，呼吸自然。首尾抱持位置相同，不放下猫，不起身，不把猫变成衣袖，地上没有猫。'),
 ('05-lower','hug.png','crouch.png','诺诺停止抚摸，保持双手托住唯一的白猫胸前与后腿，缓慢把猫从怀里移到画面左侧脚旁的地面。先让猫的前爪轻轻接触地面，再让后爪落地，四爪站稳后才放开托住身体的手。诺诺收拢双腿变为低蹲姿，再用右手轻轻摸猫头，左手放到膝上。这是主动放猫下地，不能倒放抱猫，不能扔猫、猫不能瞬移或出现第二只。'),
 ('06-stand','crouch.png','idle.png','诺诺蹲着摸猫头，轻轻收回手，双脚踩稳缓慢站起，双臂回到身体两侧。白猫等手离开头后，向画面左侧走两小步，回到最初待机位置坐好，抬头睁开蓝眼睛看诺诺。女孩站直微笑，最后恢复待机参考构图。猫始终可见，不穿过腿，不突然消失，头发自然垂落。'),
]
def setup():
 p=ROOT/'关键帧';p.mkdir(parents=True,exist_ok=True)
 gen=Path('C:/Users/youxia173/.codex/generated_images/01a1447e-aa64-7370-9548-b91724178d4b')
 sources={'idle':ROOT.parent/'连续喂饭/关键帧/A01-站立待机.png','rub':gen/'exec-2b94d1b6-d002-4076-a554-20a88a0fef0c.png','crouch':gen/'exec-f1ecbf9a-ab9f-4c6c-981b-dba906f92a79.png','hug':gen/'exec-06cc5aaa-fcec-4a3c-9a57-3e662613a804.png'}
 for name,src in sources.items():
  if not (p/f'{name}.png').exists():shutil.copy2(src,p/f'{name}.png')
pipeline.setup=setup
if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf-8')
 if sys.argv[1]=='submit':pipeline.submit()
 else:pipeline.collect()
