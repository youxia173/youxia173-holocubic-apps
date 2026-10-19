from pathlib import Path
import json,zipfile,hashlib
app=Path(__file__).resolve().parents[2]
files=[app/'桌宠诺诺.exe',app/'预览/诺诺.ico',app/'预览/windows-hd.json',app/'预览/windows-alignment.json',app/'预览/windows-settings.html',app/'说明/阶段1使用与验证.md',app/'说明/Windows动画校准说明.txt',app/'说明/Windows属性与等级.txt',app/'说明/Windows天气说明.txt',app/'说明/Windows吃拉面动画.txt']
files+=list(p for p in (app/'代码').rglob('*') if p.is_file() and p.name not in ('needs.json','needs.bak.json','user-settings.json'))
mapping=json.loads((app/'预览/windows-hd.json').read_text('utf-8'))
files+=[app/'预览'/p for p in mapping.values()]
out=app/'安装包/桌宠诺诺_Windows高清版_v1.0.3_便携包.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(set(files)):z.write(p,'桌宠诺诺/'+p.relative_to(app).as_posix())
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    for p in set(files):assert hashlib.sha256(z.read('桌宠诺诺/'+p.relative_to(app).as_posix())).digest()==hashlib.sha256(p.read_bytes()).digest()
print(f'PASS: Windows portable ZIP, {len(set(files))} files, CRC and SHA256 verified; {out.stat().st_size//1048576} MiB')
