"""Live regression: shared duration, both choices, and uninterrupted ramen-to-idle."""
from pathlib import Path
import requests,re,time,json
p=Path(__file__).resolve().parents[1]
base=(p/'网页设置地址.txt').read_text('utf-8-sig').strip().rstrip('/')
s=requests.Session();s.trust_env=False
token=re.search("TOKEN='([^']+)'",s.get(base,timeout=10).text)[1]
def state():
    r=s.get(base+'/api/state',timeout=10);r.raise_for_status();return r.json()
def post(data):
    r=s.post(base+'/api/settings',json=dict(data,token=token),timeout=30);r.raise_for_status();return r.json()
original=state();seen=set()
try:
    post({'auto':False,'seconds':{'eat':5}})
    for i in range(30):
        result=post({'activity':'eat'});assert not result['error'],result['error']
        seen.add(result['mealVariant']);assert result['seconds']['eat']==5
        if seen=={'rice','ramen'} and result['mealVariant']=='ramen':break
    assert seen=={'rice','ramen'} and result['mealVariant']=='ramen',seen
    facts=json.loads((p/'素材/诺诺-吃拉面动画/时长与接入信息.json').read_text('utf-8'))['200x150']
    seconds=sum(facts[x]['duration_ms'] for x in ['intro','loop','outro'])/1000
    start=time.monotonic()
    while time.monotonic()-start<seconds+8:
        now=state();assert not now['error'],now['error']
        if now['activity']=='idle':break
        assert now['activity']=='eat' and now['mealVariant']=='ramen','Variant changed mid-meal'
        time.sleep(.5)
    assert state()['activity']=='idle','Meal did not return to idle'
    print('PASS: both random meals, common duration, no mid-meal change, complete return to idle')
finally:
    post({'seconds':original['seconds'],'auto':original['auto']})
