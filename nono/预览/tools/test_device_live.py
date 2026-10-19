from pathlib import Path
import requests,re,json,time,hashlib
s=requests.Session();s.trust_env=False;s.headers['Connection']='close';base='http://192.168.173.187'
app=Path(__file__).resolve().parents[2]
def get(path):
    r=s.get(base+path,timeout=12);r.raise_for_status();r.encoding='utf-8';return r
state=get('/api/system/state').json()
assert state['current_app']['id']=='nono' and state['current_webui'] is True
page=get('/nono/').text;assert '桌宠诺诺' in page and '__TOKEN__' not in page
token=re.search("TOKEN='([^']+)'",page)[1]
snapshot=get('/nono/api/state').json();assert snapshot['version']=='1.0.5' and len(snapshot['clock'])==8
assert snapshot['ok'] and not snapshot.get('error'),snapshot
bad=s.post(base+'/nono/api/settings',json={'seconds':{'eat':20}},timeout=12);assert bad.status_code==403
bad=s.post(base+'/nono/api/settings',json={'token':token,'seconds':{'eat':1}},timeout=12);assert bad.status_code==400
payload={k:snapshot[k] for k in ['seconds','auto','mask','needsDisplay','needsDisplaySeconds','workStart','workEnd']};payload['token']=token
saved=s.post(base+'/nono/api/settings',json=payload,timeout=12);saved.raise_for_status();assert saved.json()['seconds']==snapshot['seconds']
for name in ['main.lua','frame_player.lua','frame-layout.json','life.lua','hud.lua','weather.lua','web.lua','settings.html','app.info']:
    r=s.get(base+'/devtools/api/read',params={'path':'/sd/apps/nono/'+name,'offset':0,'size':(app/'代码'/name).stat().st_size},timeout=12);r.raise_for_status()
    content=r.content
    if name.endswith('.html'):
        # Local AdGuard adds its own script tags to HTML HTTP responses; do not change its settings.
        content=re.sub(rb'<script\b[^>]*\bsrc="//local\.adguard\.org[^\"]*"[^>]*></script>',b'',content)
    assert hashlib.sha256(content).digest()==hashlib.sha256((app/'代码'/name).read_bytes()).digest(),name
for path in ['/api/system/exit','/api/system/launch?id=nono']:
    r=s.post(base+path,timeout=12);r.raise_for_status();time.sleep(2)
again=get('/nono/api/state').json();assert again['seconds']==snapshot['seconds'] and not again.get('error')
(app/'预览/验证/设备网页验证.json').write_text(json.dumps({'current_app':state['current_app'],'webui':True,'state':again,'checks':['startup','token','validation','save','restart persistence','core SHA256']},ensure_ascii=False,indent=2),'utf-8')
print('PASS: device running, WebUI, token, input validation, save/restart persistence, core file hashes')
