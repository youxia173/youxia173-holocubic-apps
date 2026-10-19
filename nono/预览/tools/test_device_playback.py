from pathlib import Path
import requests,time,re,json
ROOT=Path(__file__).resolve().parents[2]
s=requests.Session();s.trust_env=False;s.headers['Connection']='close';base='http://192.168.173.187/nono'
def get(path):
 r=s.get(base+path,timeout=(4,10),allow_redirects=False);r.raise_for_status();return r
token=re.search("TOKEN='([^']+)'",get('/').text)[1]
def post(v):
 r=s.post(base+'/api/settings',json=dict(v,token=token),timeout=(4,10));r.raise_for_status();return r.json()
original=get('/api/state').json();records=[]
try:
 post({'seconds':{'laser':12},'activity':'laser'})
 start=time.monotonic();phases=set()
 while time.monotonic()-start<40:
  v=get('/api/state').json();assert v['version']=='1.0.5' and not v.get('error'),v
  records.append({k:v.get(k)for k in ['clock','activity','sequencePhase','activityElapsedMs','gifProfile']})
  if v['activity']=='laser':phases.add(v['sequencePhase'])
  elif v['activity']=='idle':break
  time.sleep(1)
 assert phases=={'intro','loop','outro'} and records[-1]['activity']=='idle',records
 assert len({x['clock']for x in records})>8
 print('PASS: laser intro, three loops, outro, idle; clock and HTTP responsive. Decoder pixels not observed.',flush=True)
finally:
 post({'seconds':original['seconds'],'auto':original['auto']})
 (ROOT/'预览/验证/device-playback-v1.0.5.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),'utf-8')
