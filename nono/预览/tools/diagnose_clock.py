from pathlib import Path
import requests,time
app=Path(__file__).resolve().parents[2];s=requests.Session();s.trust_env=False;base='http://40.40.105.194'
source=(app/'代码/main.lua').read_text('utf-8')+'''
local diag=tmr.create()
diag:alarm(1500,tmr.ALARM_SINGLE,function()
 local d={clock=A.clock,activity=A.activity}
 local ok,t=pcall(time.getlocal);d.time_ok=ok;if ok then d.local_time=t end
 local shot,e=lv_snapshot_take(lv_scr_act())
 if shot then d.saved,d.save_error=lv_snapshot_save_to_png(shot,DIR..'clock-diagnostic.png');lv_snapshot_free(shot)else d.snapshot_error=tostring(e)end
 file.putcontents(DIR..'clock-diagnostic.json',sjson.encode(d))
end)
'''
for method,path,kwargs in [('POST','/api/system/exit',{}),('PUT','/api/system/fs/upload',{'params':{'path':'/sd/apps/nono/main.lua'},'data':source.encode(),'headers':{'Content-Type':'application/octet-stream'}}),('POST','/api/system/launch?id=nono',{})]:
 r=s.request(method,base+path,timeout=20,**kwargs);r.raise_for_status()
time.sleep(3)
for name in ['clock-diagnostic.json','clock-diagnostic.png']:
 r=s.get(base+'/devtools/api/read',params={'path':'/sd/apps/nono/'+name,'size':262144},timeout=20);r.raise_for_status()
 (app/'预览/验证'/name).write_bytes(r.content)
 if name.endswith('json'):print(r.text)
