from pathlib import Path
import requests,time,re,json
R=Path(__file__).resolve().parents[2];s=requests.Session();s.trust_env=False;s.headers['Connection']='close';base='http://192.168.173.187/nono'
def get(path):
 r=s.get(base+path,timeout=(4,10));r.raise_for_status();return r
token=re.search("TOKEN='([^']+)'",get('/').text)[1]
def post(v):
 r=s.post(base+'/api/settings',json=dict(v,token=token),timeout=10);r.raise_for_status();return r.json()
original=get('/api/state').json();records=[]
try:
 for cycle in range(3):
  post({'seconds':{'read':5},'activity':'read'})
  start=time.monotonic();phases=set();idle_at=None
  while time.monotonic()-start<35:
   v=get('/api/state').json();records.append(v)
   assert not v.get('error') and v['playback']['failures']==0,v
   if v['activity']=='read':phases.add(v['sequencePhase'])
   elif idle_at is None:idle_at=time.monotonic()
   elif time.monotonic()-idle_at>=5:break
   time.sleep(1)
  assert phases=={'intro','loop','outro'} and idle_at is not None,phases
  print('Read-to-idle cycle',cycle+1,'passed;',v['playback'],flush=True)
finally:
 post({'seconds':original['seconds'],'auto':original['auto']})
 (R/'预览/验证/device-frames-live.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),'utf-8')
