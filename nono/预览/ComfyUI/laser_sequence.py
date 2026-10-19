"""Standing laser-pointer cat hunt, complete intro/loop/outro."""
import sys,shutil
from pathlib import Path
import leisure_sequence as pipeline
ROOT=Path(__file__).resolve().parent.parent/'激光逗猫'
pipeline.ROOT=ROOT
pipeline.COMMON='固定镜头，诺诺站在原地，头大小、身体比例、双鞋地面位置固定，银蓝长发白青科技服装三角发夹不变。只有一只白猫，蓝色三角项圈。纯绿色背景，无地板纹理无阴影无文字。一支深蓝青色激光笔，只有一个红色圆点在地面上，没有可见光束。红点不变成球，不悬浮。猫和红点始终完整位于画面左半边的中部，不出画，不穿过诺诺双腿。'
pipeline.CLIPS=[
 ('laser-intro','idle.png','laser.png','诺诺右手先伸到身后，取出一支小激光笔，拿到身前朝左下方地面按下开关，地面出现一个红色小圆点。猫原地从坐姿站起，看到地面红点后转向左侧，目光牢牢盯住红点，慢慢伏低前身、后腿蓄力，尾巴翘起准备捕猎。诺诺温柔微笑，激光笔沿连续路径从身后出现，不凭空变出。最后与尾帧一致。'),
 ('laser-loop','laser.png','laser.png','五秒捕猎循环。诺诺一直原地站立，只轻轻左右转动持笔手腕。地面唯一的红色圆点先向左滑动一小段，白猫眼睛和头先追踪红点，压低身体，然后后腿发力，前爪伸向圆点向左短距离扑过去，四爪落地。圆点立即向右滑回，白猫转身向右追赶，再用前爪扑拍地面红点。红点再回左边最初位置，猫灵巧转向左、退回起始位置压低身体准备再次扑击。猫始终是正常四足小猫，只跳出一小步，不站成人，不翻跟头，不飞走。动作有盯住、蓄力、扑击和落地的节奏，不原地走路。所有动作在诺诺左侧小范围内完成，不出画面，红点全程清晰可见，最后恢复起始姿势。'),
 ('laser-outro','laser.png','idle.png','诺诺先停止移动激光笔，让地面红点停住。猫前爪轻轻按住红点位置。诺诺按下按钮关掉红点，收回右手，把整支激光笔连续移动到身后收好，激光笔被身体遮住以后才消失。猫抬头看诺诺，慢慢回到最初待机位置坐好。诺诺右手回到身侧，恢复双臂放松站立微笑待机。镜头与人物大小固定，猫保持可见，最终和尾帧一致。')]
def setup():
 key=ROOT/'关键帧';key.mkdir(parents=True,exist_ok=True)
 for src,name in [(ROOT.parent/'连续喂饭/关键帧/A01-站立待机.png','idle.png'),(Path('C:/Users/youxia173/.codex/generated_images/01a1447e-aa64-7370-9548-b91724178d4b/exec-61108b76-d908-4d4c-9e96-f01d10c41281.png'),'laser.png')]:
  if not (key/name).exists():shutil.copy2(src,key/name)
pipeline.CLIPS[1:2]=[('laser-left','laser.png','right.png','向左扑击后转向右侧红点。'),('laser-right','right.png','laser.png','向右扑击后回到左向蓄力姿势。')]
pipeline.CLIPS.insert(1,('laser-on','off.png','laser.png','拇指开灯，猫看到红点准备扑击。'))
pipeline.setup=setup
if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf-8')
 if sys.argv[1]=='submit':pipeline.submit()
 else:pipeline.collect()
