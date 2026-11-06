from pathlib import Path
import hashlib,json,zipfile

root=Path(__file__).resolve().parents[1]
code=root/'代码'
version='1.1.7-lite'
for name in ('layout.json','frame-layout.json','device-layout.json'):
    assert json.loads((code/name).read_text('utf-8'))['version']==version
assert 'version='+version in (code/'app.info').read_text('utf-8').replace(' ','')
private={'user-settings.json','needs.json','needs.bak.json','weather-history.json','holiday-cache.json'}
files=[p for p in code.rglob('*') if p.is_file() and p.suffix!='.gif' and p.name not in private and not p.name.startswith('holiday-cache.json.')]
manifest=json.loads((code/'frame-layout.json').read_text('utf-8'))
assert {a['id'] for a in manifest['assets']}=={'idle','eat','sleep','read','game','pet','laser','dance'}
for p in (code/'assets/frames').glob('*.json'):
    m=json.loads(p.read_text('utf-8'));assert (p.parent/m['data']).is_file()
    for part in m.get('segments',[]):assert (code/part['file']).is_file()
out=root/'安装包/桌宠诺诺_v1.1.7_精简完整安装包.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,'nono/'+p.relative_to(code).as_posix())
    z.writestr('安装说明.txt',(root/'说明/精简版播放恢复.txt').read_text('utf-8'))
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    assert set(z.namelist())=={'nono/'+p.relative_to(code).as_posix() for p in files}|{'安装说明.txt'}
    for p in files:assert hashlib.sha256(z.read('nono/'+p.relative_to(code).as_posix())).digest()==hashlib.sha256(p.read_bytes()).digest()
print('PASS: lite complete package, CRC and source SHA256 verified;',len(files),'files;',out.stat().st_size,'bytes')
