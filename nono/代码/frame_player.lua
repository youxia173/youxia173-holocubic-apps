local M={}
function M.new(dir,parent,codec)
 local P={presented=0,skipped=0,failures=0,recoveries=0,max_ms=0,last_ms=0,frame=0,crc=''}
 assert(lv_canvas_create and lv_canvas_blit_rgb565 and zlib and zlib.inflate and zlib.crc32,'RGB565 playback APIs missing')
 P.canvas=assert(lv_canvas_create(parent,200,150,rawget(_G,'LV_IMG_CF_TRUE_COLOR')or 4))
 local function close_file()if P.fd then pcall(function()P.fd:close()end);P.fd=nil end end
 function P.close()close_file();P.meta=nil;P.frame=0 end
 function P.load(path,x,y)
  P.close();P.error=nil
  local raw=assert(file.getcontents(dir..path),'Missing frame index');local m=assert(codec.decode(raw))
  assert(m.width==200 and m.height==150 and m.frame_ms==40 and #m.frames>0,'Invalid frame index')
  P.path=dir..(path:match('^(.*[/])')or '')..m.data
  assert(file.exists(P.path),'Missing frame data');P.meta=m
  lv_obj_set_pos(P.canvas,x,y)
  -- A transient first-frame read keeps the preceding verified picture; the timer retries.
  P.show(0);return true
 end
 function P.show(ms)
  if not P.meta then return end
  local i=math.min(#P.meta.frames,math.floor(math.max(0,ms)/P.meta.frame_ms)+1)
  if i==P.frame then return end
  local started=tmr.now();local e=P.meta.frames[i];local pixels,crc
  local ok,err
  for attempt=1,2 do
   ok,err=pcall(function()
    if not P.fd then P.fd=assert(file.open(P.path,'r'),'Frame open failed')end
    assert(P.fd:seek('set',e[1])==e[1],'Frame seek failed')
    local packed=assert(P.fd:read(e[2]),'Frame read failed');assert(#packed==e[2],'Short frame read')
    local read_done=tmr.now();P.read_ms=(read_done-started)%2147483648/1000
    local why;pixels,why=zlib.inflate(packed);assert(pixels,why or 'Frame inflate failed')
    assert(e[5]>=0 and e[6]>=0 and e[7]>0 and e[8]>0 and e[5]+e[7]<=200 and e[6]+e[8]<=150,'Invalid frame rectangle')
    assert(#pixels==e[7]*e[8]*2,'Wrong frame byte count')
    local inflate_done=tmr.now();P.inflate_ms=(inflate_done-read_done)%2147483648/1000
    crc=string.format('%08x',zlib.crc32(pixels)&0xffffffff);assert(crc==e[4],'Frame CRC mismatch')
    P.check_ms=(tmr.now()-inflate_done)%2147483648/1000
   end)
   if ok then if attempt>1 then P.recoveries=P.recoveries+1 end;break end
   P.lastError=tostring(err);close_file()
  end
  if not ok then
   P.failures=P.failures+1;P.failedFrame=i;P.error=tostring(err);P.failed_at=P.failed_at or started
   P.failure_ms=(tmr.now()-P.failed_at)%2147483648/1000
   return false,P.error
  end
  local draw_start=tmr.now()
  lv_canvas_frame_begin(P.canvas)
  local drawn,message=pcall(function()
   lv_canvas_fill_bg(P.canvas,0,255)
   lv_canvas_blit_rgb565(P.canvas,e[5],e[6],e[7],e[8],pixels,{byte_order='little'})
  end)
  lv_canvas_frame_end(P.canvas);assert(drawn,message)
  if P.failed_at then P.recoveries=P.recoveries+1 end
  P.error=nil;P.failed_at=nil;P.failure_ms=0;P.crc=crc;P.draw_ms=(tmr.now()-draw_start)%2147483648/1000
  if i>P.frame+1 and P.frame>0 then P.skipped=P.skipped+i-P.frame-1 end
  P.frame=i;P.presented=P.presented+1;P.last_ms=(tmr.now()-started)%2147483648/1000;P.max_ms=math.max(P.max_ms,P.last_ms)
  return true
 end
 function P.stats()return {frame=P.frame,presented=P.presented,skipped=P.skipped,failures=P.failures,recoveries=P.recoveries,crc=P.crc,lastMs=P.last_ms,maxMs=P.max_ms,readMs=P.read_ms,inflateMs=P.inflate_ms,checkMs=P.check_ms,drawMs=P.draw_ms,error=P.error,lastError=P.lastError,failedFrame=P.failedFrame,failureMs=P.failure_ms}end
 return P
end
return M
