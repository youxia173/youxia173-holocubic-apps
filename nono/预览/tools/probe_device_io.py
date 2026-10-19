from pathlib import Path
import requests,time,json
R=Path(__file__).resolve().parents[2];s=requests.Session();s.trust_env=False;s.headers['Connection']='close';base='http://192.168.173.187'
def req(method,path,**kw):
 r=s.request(method,base+path,timeout=12,**kw);r.raise_for_status();return r
original=(R/'代码/main.lua').read_bytes()
extra=b"""
do
 local d={probe_id="gc-v2"}
 local ok,e=pcall(function()
  local path=DIR..'assets/frames/nono-idle-cat.rgbz'
  local f=assert(file.open(path,'r'))
  local function probe(name,offset,n)
   local pos=f:seek('set',offset);local b=f:read(n)
   d[name]={pos=pos,len=b and #b or -1}
  end
  probe('initial',0,100)
  collectgarbage('collect');probe('after_gc',0,100)
  for i=1,30 do local t=file.open(path,'r');t:read(50);t:close()end
  collectgarbage('collect');probe('after_other_closed_gc',0,100)
  f:close();f=nil;collectgarbage('collect');f=assert(file.open(path,'r'))
  collectgarbage('collect');probe('after_reopen_gc',0,100)
  file.getcontents(DIR..'frame-layout.json');probe('after_getcontents',100,100)
  file.putcontents(DIR..'io-probe.tmp','ok');probe('after_putcontents',200,100)
  f:close();f=assert(file.open(path,'r'));local size=f:seek('end',0)
  probe('tail',size-100,100);probe('rewind_after_tail',0,100)
  f:seek('end',0);f:read(1);probe('rewind_after_eof',0,100)
  f:close()
 end)
 d.ok=ok;d.error=tostring(e);file.putcontents(DIR..'io-probe.json',sjson.encode(d))
end
"""
try:
 req('POST','/api/system/exit')
 req('PUT','/api/system/fs/upload',params={'path':'/sd/apps/nono/main.lua'},data=original+extra,headers={'Content-Type':'application/octet-stream'})
 req('POST','/devtools/api/apps/rescan');req('POST','/api/system/launch',params={'id':'nono'});time.sleep(8)
 d=req('GET','/devtools/api/read',params={'path':'/sd/apps/nono/io-probe.json','size':4096}).json()
 (R/'预览/验证/io-probe.json').write_text(json.dumps(d,indent=2),'utf-8');print(d,flush=True)
finally:
 req('POST','/api/system/exit');req('PUT','/api/system/fs/upload',params={'path':'/sd/apps/nono/main.lua'},data=original,headers={'Content-Type':'application/octet-stream'})
 req('POST','/devtools/api/apps/rescan');req('POST','/api/system/launch',params={'id':'nono'})
