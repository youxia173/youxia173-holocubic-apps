from pathlib import Path
import requests,json,time,sys
sys.stdout.reconfigure(encoding='utf-8')
app=Path(__file__).resolve().parents[2];code=app/'代码';base='http://40.40.105.194'
s=requests.Session();s.trust_env=False
s.headers['Connection']='close'
def api(path,method='GET',**kwargs):
    for attempt in range(3):
        try:
            data=kwargs.get('data')
            if hasattr(data,'seek'):data.seek(0)
            r=s.request(method,base+path,timeout=(10,45),**kwargs);r.raise_for_status();d=r.json()
            if d.get('ok') is False:raise RuntimeError(d)
            return d
        except (requests.ConnectionError,requests.Timeout):
            if attempt==2:raise
            print(f'Connection interrupted, retry {attempt+1}: {path}',flush=True)
            time.sleep(2)
print('Connecting to device file service',flush=True)
# New application only: preserve device settings and all other apps.
for folder in ['/sd/apps/nono','/sd/apps/nono/assets','/sd/apps/nono/assets/ui']:
    print('Checking '+folder,flush=True)
    check=s.get(base+'/devtools/api/stat',params={'path':folder},timeout=20)
    if check.status_code!=200 or not check.json().get('ok'):api('/devtools/api/mkdir','POST',params={'path':folder})
files=sorted(p for p in code.rglob('*') if p.is_file() and p.name!='user-settings.json')
report=[]
for i,p in enumerate(files):
    relative=p.relative_to(code).as_posix();remote='/sd/apps/nono/'+relative
    print('Uploading '+relative,flush=True)
    with p.open('rb') as f:d=api('/api/system/fs/upload','PUT',params={'path':remote},data=f,headers={'Content-Type':'application/octet-stream'})
    stat=api('/devtools/api/stat',params={'path':remote})
    if stat.get('entry',stat).get('size')!=p.stat().st_size:raise RuntimeError('Size mismatch: '+str(stat))
    report.append({'path':relative,'bytes':p.stat().st_size})
    print(f'Uploaded {i+1}/{len(files)} {relative}',flush=True)
api('/devtools/api/apps/rescan','POST')
api('/api/system/launch','POST',params={'id':'nono'})
(app/'预览/验证/部署记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
print('Deployment uploaded and launch requested',flush=True)
