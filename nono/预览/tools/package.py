from pathlib import Path
import hashlib
import zipfile
root=Path(__file__).resolve().parents[2]
code=root/"代码"
out=root/"安装包"/"桌宠诺诺_v1.0.6_完整安装包_网页设置版.zip"
out.parent.mkdir(exist_ok=True)
instruction="桌宠诺诺 V1.0.6 网页设置版。启动后打开应用网页设置自动生活、各活动时长及画面遮挡。把 nono 文件夹复制到 SD 卡 apps 下。退出旧版本后覆盖同名文件，刷新或重启。饭盒和拉面每次进食随机选择并共用时长。吃饭、睡眠、看书、游戏、撸猫、激光逗猫均为开始→可调循环→结束→待机；在网页设置各活动5–600秒，中间循环时间向上取整，开始结束另计。左右键手动选择，下键恢复自动，上键遮挡测试。含属性等级、需求驱动双倍恢复、上下班倒计时及 Cubic Control 天气。保留 user-settings.json、needs.json 及 needs.bak.json。"
files=sorted(p for p in code.rglob("*") if p.is_file() and p.suffix.lower()!='.gif' and p.name not in ('user-settings.json','needs.json','needs.bak.json'))
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,"nono/"+p.relative_to(code).as_posix())
    z.writestr("安装说明.txt",instruction)
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    expected={"nono/"+p.relative_to(code).as_posix() for p in files}|{"安装说明.txt"}
    assert set(z.namelist())==expected
    for p in files:
        assert hashlib.sha256(z.read("nono/"+p.relative_to(code).as_posix())).digest()==hashlib.sha256(p.read_bytes()).digest()
print(f"PASS: {len(files)} runtime files, correct nono/ root, CRC and SHA-256 match current code. ZIP bytes={out.stat().st_size}")

