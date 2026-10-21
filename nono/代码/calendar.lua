local M={}
function M.valid(v)return v=='today'or v=='yesterday'or v=='tomorrow'or v=='weekend'or v=='holiday'or v=='rest'end
local function leap(y)return y%4==0 and(y%100~=0 or y%400==0)end
function M.shift(y,m,d,n)
 local md={31,leap(y)and 29 or 28,31,30,31,30,31,31,30,31,30,31};d=d+n
 while d<1 do m=m-1;if m<1 then m=12;y=y-1 end;md[2]=leap(y)and 29 or 28;d=d+md[m]end
 while d>md[m]do d=d-md[m];m=m+1;if m>12 then m=1;y=y+1;md[2]=leap(y)and 29 or 28 end end
 return y,m,d
end
function M.date(y,m,d)return string.format('%04d-%02d-%02d',y,m,d)end
local function weekday(y,m,d)
 local offsets={0,3,2,5,0,3,5,1,4,6,2,4};if m<3 then y=y-1 end
 return (y+math.floor(y/4)-math.floor(y/100)+math.floor(y/400)+offsets[m]+d)%7
end
function M.format(seconds)
 if seconds>=86400 then return math.ceil(seconds/86400)..'天'end
 local n=math.ceil(math.max(0,seconds)/60);return string.format('%d小时%d分',math.floor(n/60),n%60)
end
function M.new(dir,codec)
 local raw=file.getcontents(dir..'holidays.json');local data=raw and codec.decode(raw)or{years={}}
 local C={}
 function C.apply(year)
  for i,y in ipairs(data.years)do if y.year==year.year then data.years[i]=year;return end end
  data.years[#data.years+1]=year
 end
 function C.describe(mode,t)
  local title=mode=='weekend'and'距周末'or mode=='holiday'and'距节假日'or'距休息日'
  if not t or not t.year or not t.mon or not t.day then return {title,'等待时间',''}end
  for i=0,369 do
   local y,m,d=M.shift(t.year,t.mon,t.day,i);local date=M.date(y,m,d);local year
   for _,v in ipairs(data.years)do if v.year==y then year=v;break end end
   if not year and mode~='weekend'then return {title,'待更新日历',''}end
   local holiday,working
   if year then
    for _,h in ipairs(year.holidays)do if h.start<=date and date<=h['end']then holiday=h;break end end
    for _,v in ipairs(year.workdays)do if v==date then working=true;break end end
   end
   local wd=weekday(y,m,d);local weekend=(wd==0 or wd==6)and not working
   local useHoliday=mode~='weekend'and holiday
   if useHoliday or(mode~='holiday'and weekend)then
    local value=i==0 and(useHoliday and'假期中'or'周末中')or M.format(i*86400-(t.hour or 0)*3600-(t.min or 0)*60-(t.sec or 0))
    return {title,value,useHoliday and(holiday.name..(year.official and''or'*'))or string.format('%d/%d',m,d)}
   end
  end
  return {title,'待更新日历',''}
 end
 return C
end
return M
