from pathlib import Path
import requests,time,json,zlib
R=Path(__file__).resolve().parents[2];s=requests.Session();s.trust_env=False;s.headers['Connection']='close';base='http://192.168.173.187'
def req(method,path,**kw):
 r=s.request(method,base+path,timeout=(5,15),**kw);r.raise_for_status();
 if method!='GET':print(path,r.text,flush=True)
 return r
original=(R/'代码/main.lua').read_bytes()
extra=b"""
do
 local result={canvas=type(lv_canvas_blit_rgb565),inflate=type(zlib.inflate),files={}}
 local ok,err=pcall(function()
  for _,name in ipairs({'nono-idle-cat.gif','nono-read-outro.gif','nono-read-loop.gif'})do
   local fd=assert(file.open(DIR..'assets/device/'..name,'r'));local crc=0;local count=0
   while true do local b=fd:read(16384);if not b or #b==0 then break end;crc=zlib.crc32(b,crc);count=count+#b end
   fd:close();result.files[name]={bytes=count,crc=crc}
  end
 end)
 result.ok=ok;result.error=tostring(err)
 file.putcontents(DIR..'gif-diagnostic.json',sjson.encode(result))
end
"""
try:
 req('POST','/api/system/exit')
 req('PUT','/api/system/fs/upload',params={'path':'/sd/apps/nono/main.lua'},data=original+extra,headers={'Content-Type':'application/octet-stream'})
 req('POST','/devtools/api/apps/rescan')
 req('POST','/api/system/launch',params={'id':'nono'});time.sleep(5)
 d=req('GET','/devtools/api/read',params={'path':'/sd/apps/nono/gif-diagnostic.json','size':4096}).json()
 for name,v in d['files'].items():
  b=(R/'代码/assets/device'/name).read_bytes();v['matches']=v['bytes']==len(b)and(v['crc']&0xffffffff)==zlib.crc32(b)
 (R/'预览/验证/gif-diagnostic.json').write_text(json.dumps(d,indent=2),'utf-8');print(json.dumps(d),flush=True)
finally:
 req('POST','/api/system/exit')
 req('PUT','/api/system/fs/upload',params={'path':'/sd/apps/nono/main.lua'},data=original,headers={'Content-Type':'application/octet-stream'})
 req('POST','/devtools/api/apps/rescan')
 req('POST','/api/system/launch',params={'id':'nono'})
