from pathlib import Path
import requests,re,json
preview=Path(__file__).resolve().parents[1]
base=(preview/'网页设置地址.txt').read_text('utf-8-sig').strip().rstrip('/')
s=requests.Session();s.trust_env=False
page=s.get(base,timeout=8);page.raise_for_status()
token=re.search("TOKEN='([^']+)'",page.text)[1]
original=s.get(base+'/api/state',timeout=8).json()
assert original['platform']=='windows'
assert s.post(base+'/api/settings',json={'auto':False},timeout=8).status_code==403
assert s.post(base+'/api/settings',json={'token':token,'seconds':{'eat':4}},timeout=8).status_code==400
assert s.get(base+'/api/state',timeout=8).json()['seconds']==original['seconds']
def post(p):
    r=s.post(base+'/api/settings',json=dict(p,token=token),timeout=10);r.raise_for_status();return r.json()
try:
    r=post({'seconds':{'eat':35,'read':45},'auto':False,'scale':300,'topmost':True,'black':False,'mask':True})
    assert r['seconds']['eat']==35 and r['seconds']['read']==45 and r['scale']==300 and r['mask'] and not r['auto']
    r=post({'activity':'read'});assert r['activity']=='read' and not r['auto']
    r=post({'activity':'idle'});assert r['activity']=='idle'
finally:
    post({k:original[k] for k in ['seconds','auto','scale','topmost','black','mask']})
print('PASS: token, invalid input atomicity, independent durations, display controls, manual action, restore')
