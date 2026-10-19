from pathlib import Path
import requests,time,json
ROOT=Path(__file__).resolve().parents[2];CODE=ROOT/'代码'
s=requests.Session();s.trust_env=False;s.headers['Connection']='close'
base='http://192.168.173.187'
def call(path,method='GET',**kw):
 for attempt in range(3):
  try:
   r=s.request(method,base+path,timeout=(5,12),**kw);r.raise_for_status();return r
  except requests.RequestException:
   if attempt==2:raise
   time.sleep(1)
files=['main.lua','frame_player.lua','frame-layout.json','hud.lua','settings.html','app.info','info.html']
files+=['assets/frames/'+p.name for p in sorted((CODE/'assets/frames').iterdir()) if p.is_file()]
backup=ROOT/'归档/部署前备份_v1.0.5';backup.mkdir(parents=True,exist_ok=True)
print(call('/nono/api/state').text,flush=True)
for name in ['main.lua','hud.lua','settings.html','app.info','info.html','user-settings.json']:
 try:
  raw=call('/devtools/api/read',params={'path':'/sd/apps/nono/'+name,'offset':0,'size':65536}).content
  
  if not (backup/name).exists():(backup/name).write_bytes(raw)
 except requests.RequestException:pass
call('/api/system/exit','POST')
try:call('/devtools/api/mkdir','POST',params={'path':'/sd/apps/nono/assets/frames'})
except requests.RequestException:pass
for name in files:
 data=(CODE/name).read_bytes()
 d=call('/api/system/fs/upload','PUT',params={'path':'/sd/apps/nono/'+name},data=data,headers={'Content-Type':'application/octet-stream'}).json()
 assert d.get('ok') is not False,d
 stat=call('/devtools/api/stat',params={'path':'/sd/apps/nono/'+name}).json()
 assert stat.get('entry',stat).get('size')==len(data),stat
 print('Uploaded '+name,flush=True)
call('/devtools/api/apps/rescan','POST')
print(call('/api/system/launch','POST',params={'id':'nono'}).text,flush=True)
time.sleep(3)
print(call('/nono/api/state').text,flush=True)
