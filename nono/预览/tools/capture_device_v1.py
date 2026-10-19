from pathlib import Path
import requests,time,json
root=Path(__file__).resolve().parents[2];s=requests.Session();s.trust_env=False;s.headers['Connection']='close'
base='http://40.40.105.194'
def req(method,path,**kw):
 r=s.request(method,base+path,timeout=(5,12),**kw);r.raise_for_status();return r
original=(root/'代码/main.lua').read_bytes()
extra=b"""
local capture=tmr.create()
capture:alarm(2000,tmr.ALARM_SINGLE,function()
 A.needsDisplay='always';A.tick()
 local shot=lv_snapshot_take(lv_scr_act())
 if shot then lv_snapshot_save_to_png(shot,DIR..'v1-preview.png');lv_snapshot_free(shot)end
 local raw=file.getcontents(DIR..'v1-preview.png')
 for i=0,math.ceil(#raw/4096)-1 do
  local part=raw:sub(i*4096+1,(i+1)*4096):gsub('.',function(c)return string.format('%02x',string.byte(c))end)
  A.web:register(httpd.GET,'/capturehex/'..i,function()return {type='text/plain',body=part}end)
 end
end)
"""
try:
 req('POST','/api/system/exit')
 req('PUT','/api/system/fs/upload',params={'path':'/sd/apps/nono/main.lua'},data=original+extra)
 req('POST','/api/system/launch',params={'id':'nono'})
 time.sleep(4)
 stat=req('GET','/devtools/api/stat',params={'path':'/sd/apps/nono/v1-preview.png'}).json();print(stat,flush=True)
 size=stat['size'];data=b''
 for i in range((size+4095)//4096):
  data+=bytes.fromhex(req('GET','/nono/capturehex/'+str(i)).text)
 assert len(data)==size
 (root/'预览/验证/Cubic-v1.0.0.png').write_bytes(data)
finally:
 req('POST','/api/system/exit')
 req('PUT','/api/system/fs/upload',params={'path':'/sd/apps/nono/main.lua'},data=original)
 req('POST','/api/system/launch',params={'id':'nono'})
print('Screenshot saved; clean runtime restored',flush=True)
