"""Paws-down petting revision; preserve the released V0.5 assets until verified."""
import sys,shutil
from pathlib import Path
import leisure_sequence as pipeline
ROOT=Path(__file__).resolve().parent.parent/'撸猫修正版'
OLD=ROOT.parent/'完整撸猫'
pipeline.ROOT=ROOT
pipeline.COMMON='锁定镜头、画幅和人物比例。诺诺从始至终保持同一低蹲姿势，双鞋原地踩地，头大小、头顶位置、脸、肩膀、膝盖、身体位置与首尾图片严格一致，身体不前后移动，不变成侧坐，不站起，不缩放。只有手臂和唯一一只纯白小猫移动。银蓝长发白青科技衣服和三角发夹保持不变。猫始终背朝上肚子朝下，四脚朝下，头朝画面左侧，不翻成仰躺，不像抱婴儿。纯绿色背景。'
pipeline.CLIPS=[
 ('03-grip','crouch.png','grip.png','诺诺从摸猫头姿态开始，只移动双手，把一只手从猫头移到胸部下方，另一只手从膝盖移到猫腹部后半段下方，双手从下方托稳白猫。猫四只爪子固定着地，原地稍转头，不走路不迈步不跳。最后双手已经分别托住胸腹，猫仍四爪着地，尚未抬起。诺诺头部和身体完全不改变位置和大小。'),
 ('04-lift','grip.png','hug.png','起始双手已经从下方托稳猫胸部和腹部。第一秒诺诺同时抬起双手，猫四只爪子同时直接离开地面至少一只脚掌的高度。猫身体被双手托起，四条腿随重力放松下垂，腿绝不轮流弯曲迈步，后脚不能在地面走，也不能在空中踩踏。之后双臂继续把猫缓慢向上并向右移动到胸前，猫全程背朝上肚子朝下，躯干保持水平，头朝左，四腿始终朝下悬垂。到怀里后左前臂持续托住猫胸腹，右手轻放头顶。诺诺保持蹲姿，鞋膝头肩完全不动。'),
 ('05-loop','hug.png','hug.png','固定低蹲抱猫的五秒循环。左前臂稳稳从下方托住猫胸腹，猫肚子始终向下，背朝上，头朝左。四只脚始终在猫身体下方自然垂着，不向上翻，不踩踏。诺诺右手在猫头顶和颈背之间小幅缓慢抚摸两次，回到原来的手掌位置。猫舒服闭眼轻呼吸，尾巴保持原来的形状，不甩动。诺诺温柔眨眼，鞋子膝盖身体与头的位置和大小保持固定，只有手指小幅移动，没有身体摆动，没有脚部动作。'),
 ('06-lower','hug.png','grip.png','诺诺始终保持原来的低蹲姿势，头、脸、肩膀、膝盖、鞋子位置和尺寸固定不变，不向前探身，不放大缩小。先把抚摸猫头的右手移到猫胸部下方，两手从下方托住胸部和腹部，缓慢把猫向左下方降低到原来的地面位置。猫背朝上肚子向下，全程四脚自然垂着，不走路、不蹬腿、不翻身。直到四爪同时稳稳接触地面，双手仍托在胸腹下方。只有双臂和猫发生移动，身体镜头绝对固定。'),
 ('07-release','grip.png','crouch.png','猫的四只爪子已经站稳地面，诺诺保持低蹲完全不动，只慢慢抽出托在猫胸腹下方的双手，右手回到猫头顶轻轻摸一下，左手回到自己膝盖。猫原地站着不走动，恢复首尾图中闭眼被摸头的姿势。人物头部和身体完全不改变位置和大小，不能放大缩小。'),
]
def setup():
 key=ROOT/'关键帧';key.mkdir(parents=True,exist_ok=True)
 gen=Path('C:/Users/youxia173/.codex/generated_images/01a1447e-aa64-7370-9548-b91724178d4b')
 for name,src in [('crouch',OLD/'关键帧/crouch.png'),('hug',gen/'exec-8f0bf778-4fd1-4d6b-bf66-ecf3188dce17.png'),('grip',gen/'exec-e44b70f9-37af-43bf-933d-baad02d91f5f.png')]:
  if not (key/f'{name}.png').exists():shutil.copy2(src,key/f'{name}.png')
 for src,dest in [('01-rub','01-rub'),('02-crouch','02-crouch'),('06-stand','08-stand'),('bridges/pet-start','bridges/pet-start'),('bridges/pet-end','bridges/pet-end'),('bridges/01-rub-02-crouch','bridges/01-rub-02-crouch')]:
  if not (ROOT/dest).exists():shutil.copytree(OLD/src,ROOT/dest)
pipeline.CLIPS.insert(2,('04-settle','air.png','hug.png','猫已被水平托起，四脚朝下悬垂，保持身体方向，平稳移近怀里。'))
pipeline.CLIPS.insert(3,('04-cradle','cradle.png','hug.png','左臂托住猫，右手移至头顶。'))
pipeline.setup=setup
if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf-8')
 if sys.argv[1]=='submit':pipeline.submit()
 else:pipeline.collect()
