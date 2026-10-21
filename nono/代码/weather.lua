local M={}
function M.new(A,dir,codec)
 local calendar=assert(loadfile(dir..'calendar.lua'))()
 local history={};local historyAddress
 local W={status='等待天气',days={},location='',next_ms=0,busy=false,serial=0}
 local function decode(body)
  if body and zlib and zlib.isgzip and zlib.isgzip(body)then body=zlib.gunzip(body)end
  local ok,d=pcall(codec.decode,body or '');return ok and d or nil
 end
 local function enc(v)return tostring(v):gsub('([^%w%-_%.~])',function(c)return string.format('%%%02X',string.byte(c))end)end
 local function request(path,callback)
  local serial=W.serial
  http.cubicserver.get(path,'Accept-Encoding: gzip\r\n',function(status,body)
   if not A.running or serial~=W.serial then return end
   callback(status,decode(body))
  end)
 end
 function W.poll(now,t)
  if W.busy then if now-(W.started or now)>45000 then W.busy=false;W.serial=W.serial+1;W.status='天气超时';W.next_ms=now+300000 end;return end
  if now<W.next_ms then return end
  W.next_ms=now+1800000
  local settings=decode(file.getcontents('/sd/apps/settings.json'))or{}
  local address=settings.weather_address or settings.weatherAddress or ''
  local location=settings.weather_location_id or ''
  if (settings.weather_location_address or settings.weather_location_raw)~=address then location=''end
  if address~=W.address then
   W.days={};W.fetched=nil;W.address=address;history={};historyAddress=address
   local saved=decode(file.getcontents(dir..'weather-history.json'))
   if saved and saved.address==address and type(saved.days)=='table'then history=saved.days end
  end
  W.location=settings.weather_city or address
  if address=='' and location=='' then W.status='请设置天气地址';return end
  if not(http and http.cubicserver and http.cubicserver.get)then W.status='天气接口不可用';return end
  W.busy=true;W.started=now;W.serial=W.serial+1;W.status='正在更新天气'
  local function failed()W.busy=false;W.status='天气待更新';W.next_ms=A.elapsed_ms+300000 end
  local function forecast(id)
   request('/v1/weather/3d?location='..enc(id)..'&unit=m&lang=zh',function(status,d)
    if status~=200 or not d or tostring(d.code)~='200' or type(d.daily)~='table'then failed();return end
    local oldest=t and t.year and t.mon and t.day and calendar.date(calendar.shift(t.year,t.mon,t.day,-7))
    if oldest then
     local merged={};for _,v in ipairs(history)do if type(v.fxDate)=='string'and v.fxDate>=oldest then merged[v.fxDate]=v end end
     for _,v in ipairs(d.daily)do if type(v.fxDate)=='string'then merged[v.fxDate]=v end end
     history={};for _,v in pairs(merged)do history[#history+1]=v end
     table.sort(history,function(a,b)return a.fxDate<b.fxDate end)
     while #history>12 do table.remove(history,1)end
     pcall(function()file.putcontents(dir..'weather-history.json',codec.encode({address=historyAddress,days=history}))end)
    end
    W.days=d.daily;W.fetched=A.elapsed_ms;W.busy=false;W.status='已更新 · '..W.location
   end)
  end
  if location~='' then forecast(location)
  elseif address:match('^%d+$')then forecast(address)
  else request('/v1/weather/cities?location='..enc(address)..'&number=1&lang=zh',function(status,d)
   local items=d and(d.locations or d.location);local first=items and items[1]
   if status~=200 or not first or not first.id then failed();return end
   W.location=first.name or address;forecast(first.id)
  end)end
 end
 function W.day(t,ahead)
  if not t or not t.year or not t.mon or not t.day then return nil end
  local date=calendar.date(calendar.shift(t.year,t.mon,t.day,ahead))
  if ahead==-1 then
   for _,d in ipairs(history)do if d.fxDate==date then return d end end
   return nil
  end
  if not W.fetched or A.elapsed_ms-W.fetched>21600000 then return nil end
  for _,d in ipairs(W.days)do if d.fxDate==date then return d end end
 end
 function W.icon(d)
  local n=d and tonumber(d.iconDay)
  if not n then return 'unknown' end
  if n==100 or n==150 then return 'sun' end
  if n==101 or n==102 or n==103 or n==151 or n==152 or n==153 then return 'partly' end
  if n==104 or n==154 then return 'cloud' end
  if n>=200 and n<300 then return 'wind' end
  if n==302 or n==303 or n==304 then return 'storm' end
  if n==404 or n==405 or n==406 or n==456 then return 'sleet' end
  if n>=300 and n<400 then return 'rain' end
  if n>=400 and n<500 then return 'snow' end
  if n==503 or n==504 or n==507 or n==508 then return 'dust' end
  if n>=500 and n<600 then return 'fog' end
  if n==900 then return 'hot' end
  if n==901 then return 'cold' end
  return 'unknown'
 end
 function W.stop()W.serial=W.serial+1;W.busy=false end
 return W
end
return M
