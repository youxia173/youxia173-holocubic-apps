"""One-time relocation with content verification; never overwrite destinations."""
from pathlib import Path
import hashlib, json, re
from PIL import Image
app=Path(__file__).resolve().parents[2]
desktop=Path('D:/Desktop').resolve()
dest=(app/'预览/素材').resolve()
assert dest.is_relative_to(app.resolve())
dest.mkdir(parents=True,exist_ok=True)
def manifest(folder):
    return {str(p.relative_to(folder)):hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.rglob('*') if p.is_file()}
report=[]
for src in sorted(desktop.glob('诺诺-*')):
    if not src.is_dir():continue
    assert src.resolve().parent==desktop and not src.is_symlink()
    target=dest/src.name
    if target.exists():raise RuntimeError(f'Destination already exists: {target}')
    before=manifest(src)
    src.rename(target)
    assert before==manifest(target)
    report.append({'folder':target.name,'verified_files':len(before)})
for p in (app/'预览/ComfyUI').glob('*.py'):
    s=p.read_text('utf-8-sig')
    if p.name=='laser_aim_tools.py':
        s=s.replace(".replace('D:/Desktop/诺诺-激光逗猫动画',DELIVERY.as_posix())", ".replace(\"DELIVERY=DELIVERY_ROOT / '诺诺-激光逗猫动画'\", \"DELIVERY=DELIVERY_ROOT / '诺诺-激光指向修正版'\")")
    changed=re.sub(r"(?:ROOT\.__class__|Path)\('D:/Desktop/([^']+)'\)",r"DELIVERY_ROOT / '\1'",s)
    if changed!=s:changed='from delivery_paths import DELIVERY_ROOT\n'+changed
    changed=changed.replace('桌面素材为`诺诺-', '素材位于`预览/素材/诺诺-').replace('桌面素材`诺诺-', '素材`预览/素材/诺诺-')
    if changed!=p.read_text('utf-8-sig'):p.write_text(changed,'utf-8')
doc=app/'说明/阶段1使用与验证.md'
s=doc.read_text('utf-8-sig').replace('桌面素材为`诺诺-', '素材位于`预览/素材/诺诺-').replace('桌面素材`诺诺-', '素材`预览/素材/诺诺-')
s+='\n## Windows EXE 启动与素材目录\n\n双击软件根目录的 `诺诺.exe` 启动 Windows 模拟器，带诺诺人物图标，无需手动运行脚本。需 Windows 的 .NET Framework 4.x；保留同目录的 `代码/`、`预览/`，不要单独搬走 EXE。原有透明、置顶、倍率与独立活动时长保持不变，设置保存在 `预览/用户设置.txt`。\n\n最终动画统一保存在 `预览/素材/`，现有桌面诺诺素材文件夹已迁入，后续导出也使用此位置。原始关键帧和视频仍保存在各动作的过程目录。\n'
doc.write_text(s,'utf-8')
Image.open(app/'代码/main.png').convert('RGBA').save(app/'预览/诺诺.ico',sizes=[(16,16),(24,24),(32,32),(48,48),(64,64)])
(app/'预览/打开诺诺.cmd').write_text('@echo off\nchcp 65001 >nul\nstart "" "%~dp0..\\诺诺.exe"\n','utf-8')
(dest/'迁移记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps(report,ensure_ascii=False))
