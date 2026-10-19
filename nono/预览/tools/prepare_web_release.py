from pathlib import Path
from PIL import Image
import shutil,json
app=Path(__file__).resolve().parents[2];preview=app/'预览';code=app/'代码'
archive=app/'归档/v0.6.1-Windows高清与网页设置前';archive.mkdir(parents=True,exist_ok=True)
for p in list((app/'安装包').glob('*.zip'))+[app/'诺诺.exe']:
    if p.exists():
        target=archive/p.name
        assert p.resolve().is_relative_to(app.resolve()) and target.resolve().is_relative_to(archive.resolve())
        if not target.exists():p.rename(target)
source=Path('C:/Users/youxia173/.codex/generated_images/01a1447e-aa64-7370-9548-b91724178d4b/exec-bd32cb88-377e-4027-b5a4-4d79dcc65666.png')
out=preview/'素材/软件图标';out.mkdir(exist_ok=True)
shutil.copy2(source,out/'桌宠诺诺-图标原图.png')
im=Image.open(source).convert('RGBA');im.resize((64,64),Image.Resampling.LANCZOS).save(code/'main.png')
im.resize((256,256),Image.Resampling.LANCZOS).save(preview/'诺诺.ico',sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
for p in [code/'app.info',code/'info.html',code/'main.lua',code/'layout.json',preview/'Program.cs',preview/'NonoPreview.cs']:
    s=p.read_text('utf-8-sig').replace('0.6.1.1','0.7.0').replace('0.6.1.0','0.7.0.0').replace('0.6.1','0.7.0')
    if p.name=='app.info':s=s.replace('name = Nono','name = 桌宠诺诺').replace('= 诺诺','= 桌宠诺诺').replace('= 諾諾','= 桌寵諾諾').replace('name_en = Nono','name_en = Nono Desktop Pet')
    if p.name in ['Program.cs','NonoPreview.cs']:s=s.replace('诺诺 ·','桌宠诺诺 ·').replace('诺诺桌宠','桌宠诺诺').replace('诺诺 Windows','桌宠诺诺 Windows').replace('诺诺.exe','桌宠诺诺.exe')
    p.write_text(s,'utf-8-sig' if p.suffix=='.cs' else 'utf-8')
p=preview/'tools/构建Windows.ps1';s=p.read_text('utf-8-sig').replace('诺诺.exe','桌宠诺诺.exe');s=s.replace("(Join-Path $preview 'Program.cs')","(Join-Path $preview 'SettingsServer.cs') (Join-Path $preview 'Program.cs')");p.write_text(s,'utf-8-sig')
p=preview/'启动预览.ps1';s=p.read_text('utf-8-sig').replace("@((Join-Path $PSScriptRoot 'PetScene.cs')","@((Join-Path $PSScriptRoot 'SettingsServer.cs'),(Join-Path $PSScriptRoot 'PetScene.cs')");p.write_text(s,'utf-8-sig')
p=preview/'打开诺诺.cmd';p.write_text('@echo off\nchcp 65001 >nul\nstart "" "%~dp0..\\桌宠诺诺.exe"\n','utf-8')
for name in ['package.py','package_windows.py']:
    p=preview/'tools'/name;s=p.read_text('utf-8-sig').replace('0.6.1.1','0.7.0').replace('0.6.1','0.7.0').replace('诺诺.exe','桌宠诺诺.exe').replace('诺诺_v','桌宠诺诺_v').replace('诺诺_Windows','桌宠诺诺_Windows').replace('激光指向修正版','网页设置版');p.write_text(s,'utf-8')
p=app/'AGENTS.md';p.write_text(p.read_text('utf-8').replace('`诺诺.exe`','`桌宠诺诺.exe`'),'utf-8')
p=app/'说明/阶段1使用与验证.md';s=p.read_text('utf-8').replace('诺诺.exe','桌宠诺诺.exe');s+='\n## V0.7.0 桌宠诺诺 · 网页设置\n\n软件更名为桌宠诺诺，使用诺诺与白猫的新图标。Windows右键桌宠选择“打开网页设置”，或按F1；原调试窗口不再显示。设置网页共用于Windows和Cubic设备，支持自动生活、手动活动、各活动5–600秒和顶部遮挡，Windows另有倍率、置顶和黑底开关。窗口设置与活动时长保存到预览目录。设备设置保存为软件目录user-settings.json，安装包不包含该文件。\n\n设备启动应用后访问 http://40.40.105.194/nono/ 。设备版安装到 /sd/apps/nono/，网页路由在退出时注销。参考官方仓库 https://github.com/clocteck/holocubic-apps/ 的应用WebUI生命周期，采用 app.route_base、httpd.dynamic、app.set_webui。\n';p.write_text(s,'utf-8')
print('Release prepared')
