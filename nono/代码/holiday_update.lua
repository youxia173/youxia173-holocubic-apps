local M={}
function M.convert(f,year,calendar)
 if type(year)~='number'or type(f)~='table'or f.year~=year or year<2024 or year>2100 or type(f.papers)~='table'or #f.papers==0 or type(f.days)~='table'or #f.days<20 or #f.days>80 then return nil end
 for _,p in ipairs(f.papers)do
  if type(p)~='string'then return nil end
  local host=p:match('^https://([^/]+)/');if not host or not(host=='gov.cn'or host:match('%.gov%.cn$'))then return nil end
 end
 local seen={};local result={year=year,official=true,holidays={},workdays={}};local names=''
 for _,d in ipairs(f.days)do
  if type(d)~='table'or type(d.date)~='string'or type(d.name)~='string'or #d.name>36 or type(d.isOffDay)~='boolean'then return nil end
  local y,m,day=d.date:match('^(%d%d%d%d)%-(%d%d)%-(%d%d)$');y=tonumber(y);m=tonumber(m);day=tonumber(day)
  if y~=year or not m or m<1 or m>12 or not day or day<1 or day>31 or seen[d.date]then return nil end
  local yy,mm,dd=calendar.shift(y,m,day,0);if yy~=y or mm~=m or dd~=day then return nil end
  seen[d.date]=true
  if d.isOffDay then result.holidays[#result.holidays+1]={start=d.date,['end']=d.date,name=d.name};names=names..d.name
  else result.workdays[#result.workdays+1]=d.date end
 end
 for _,n in ipairs({'元旦','春节','清明','劳动','端午','中秋','国庆'})do if not names:find(n,1,true)then return nil end end
 return result
end
function M.new(A,dir,codec,calendar,apply)
 local U={status='等待检查节假日日历',next_ms=0,busy=false};local feeds={};local serial=0
 local function decode(s)local ok,v=pcall(codec.decode,s or'');return ok and v or nil end
 for _,path in ipairs({dir..'holiday-cache.json',dir..'holiday-cache.json.bak'})do
  local cache=decode(file.getcontents(path));local valid=false
  if type(cache)=='table'and type(cache.feeds)=='table'then for _,f in ipairs(cache.feeds)do local y=M.convert(f,type(f)=='table'and f.year or 0,calendar);if y then apply(y);feeds[f.year]=f;valid=true end end end
  if valid then break end
 end
 local function save()
  local list={};for _,f in pairs(feeds)do list[#list+1]=f end
  if #list==0 then return end
  pcall(function()
   local old=file.getcontents(dir..'holiday-cache.json');if old and decode(old)then file.putcontents(dir..'holiday-cache.json.bak',old)end
   file.putcontents(dir..'holiday-cache.json',codec.encode({feeds=list}))
  end)
 end
 function U.poll(now,t)
  if U.busy or now<U.next_ms or not t or not t.year then return end
  if not(http and http.get)then U.status='固件无日历联网接口，使用本地';U.next_ms=now+21600000;return end
  U.busy=true;U.next_ms=now+86400000;serial=serial+1;local requestId=serial;local year=t.year;local results={}
  local function fetch(y)
   local ok=pcall(http.get,'https://raw.githubusercontent.com/NateScarlet/holiday-cn/master/'..y..'.json',{timeout=15000,headers={['Accept-Encoding']='identity'}},function(status,body)
    if not A.running or serial~=requestId then return end
    local f=status==200 and type(body)=='string'and #body<=65536 and decode(body)or nil
    local converted=M.convert(f,y,calendar)
    if converted then apply(converted);feeds[y]=f;results[#results+1]=y..'已更新'
    elseif type(f)=='table'and f.year==y and type(f.days)=='table'and #f.days==0 then results[#results+1]=y..'待公布'
    else results[#results+1]=y..'暂未更新';U.next_ms=A.elapsed_ms+21600000 end
    if y==year then fetch(year+1)else save();U.busy=false;U.status=table.concat(results,'；')..' · 保留本地日历'end
   end)
   if not ok then U.busy=false;U.next_ms=now+21600000;U.status='联网失败，使用本地日历'end
  end
  fetch(year)
 end
 function U.stop()serial=serial+1 end
 return U
end
return M
