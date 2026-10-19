from pathlib import Path
import zlib,json
from lupa.lua53 import LuaRuntime
R=Path(__file__).resolve().parents[2]/'代码';L=LuaRuntime(encoding=None,unpack_returned_tuples=True)
def table(v):
 if isinstance(v,dict):return L.table_from({k.encode():table(x)for k,x in v.items()})
 if isinstance(v,list):return L.table_from([table(x)for x in v])
 if isinstance(v,str):return v.encode()
 return v
G=L.globals();G[b'py_read']=lambda p:(R/p.decode().removeprefix('/sd/apps/nono/')).read_bytes()
G[b'py_decode']=lambda b:table(json.loads(b));G[b'py_inflate']=zlib.decompress;G[b'py_crc']=zlib.crc32
L.execute(b"""
file={exists=function()return true end,getcontents=py_read,open=function(path)
 local raw=py_read(path);local pos=0
 return {seek=function(self,whence,offset)pos=offset;return pos end,
 read=function(self,n)local b=raw:sub(pos+1,pos+n);pos=pos+#b;if corrupt then return b:sub(1,-2)end;return b end,
 close=function()end}
end}
zlib={inflate=py_inflate,crc32=py_crc};tmr={now=function()return 100 end}
lv_canvas_create=function()return 1 end;lv_obj_set_pos=function()end
lv_canvas_frame_begin=function()inframe=true end;lv_canvas_frame_end=function()inframe=false end
lv_canvas_fill_bg=function()assert(inframe)end
blits=0;lv_canvas_blit_rgb565=function(c,x,y,w,h,pixels,opts)assert(inframe and #pixels==w*h*2 and x>=0 and y>=0 and x+w<=200 and y+h<=150);blits=blits+1 end
""")
module=L.execute((R/'frame_player.lua').read_bytes());player=module[b'new'](b'/sd/apps/nono/',1,L.table_from({b'decode':G[b'py_decode']}))
for k in range(3):
 for name in [p.stem for p in sorted((R/'assets/frames').glob('*.json'))]:
  player[b'load'](('assets/frames/'+name+'.json').encode(),60,1)
  meta=json.loads((R/'assets/frames'/(name+'.json')).read_text())
  for t in range(0,meta['duration_ms'],40):
   result=player[b'show'](t);assert result is None or result is True,result
assert player[b'stats']()[b'failures']==0
before=G[b'blits'];G[b'corrupt']=True
player[b'load'](b'assets/frames/nono-idle-cat.json',60,1)
result=player[b'show'](40)
assert result[0] is False and G[b'blits']==before and player[b'stats']()[b'failures']==2
player[b'close']()
print('PASS: 3 complete read-to-idle sequences, RGB565 byte counts and checksums; damaged read rejected before blit')
