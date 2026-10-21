-- Nono V1.1.6-lite: lunchbox meals, no witch form.
local previous=rawget(_G,"NONO_APP")
if previous and previous.stop then pcall(previous.stop,"reload") end
local A={version="1.1.6-lite",running=true,fonts={},activity="idle",error=nil}
_G.NONO_APP=A
local DIR="/sd/apps/nono/"
local codec=rawget(_G,"sjson") or rawget(_G,"json")
assert(codec and codec.decode,"Nono: JSON codec unavailable")
local manifest=assert(file.getcontents(DIR.."frame-layout.json"),"Nono: missing layout")
local layout=assert(codec.decode(manifest))
assert(layout.width==320 and layout.height==240,"Nono: expected 320x240")
local STYLE=(rawget(_G,"LV_PART_MAIN") or 0)|(rawget(_G,"LV_STATE_DEFAULT") or 0)
local function source(relative)
 -- PNG images use LVGL's SD filesystem driver, as in the clock apps.
 -- The GIF binding resolves its existing absolute path separately.
 return (relative:match("%.png$") and "S:/apps/nono/" or "/apps/nono/")..relative
end
local function panel(parent,x,y,w,h,opacity)
 local o=lv_obj_create(parent)
 lv_obj_set_pos(o,x,y);lv_obj_set_size(o,w,h)
 lv_obj_set_style_bg_color(o,0,STYLE);lv_obj_set_style_bg_opa(o,opacity or 0,STYLE)
 lv_obj_set_style_border_width(o,0,STYLE);lv_obj_set_style_pad_all(o,0,STYLE);lv_obj_set_style_radius(o,0,STYLE)
 if lv_obj_clear_flag and LV_OBJ_FLAG_SCROLLABLE then lv_obj_clear_flag(o,LV_OBJ_FLAG_SCROLLABLE) end
 return o
end
local function image(parent,path,x,y)
 local o=lv_img_create(parent);lv_img_set_src(o,source(path));lv_obj_set_pos(o,x,y);return o
end
local root=lv_scr_act();lv_obj_clean(root)
A.root=panel(root,0,0,320,240,255)
A.actor=panel(A.root,0,layout.safe_top,320,layout.actor_bottom-layout.safe_top,0)
A.mask=panel(A.root,0,0,320,layout.safe_top,0)
A.leftRegion='today';A.rightRegion='tomorrow';local calendar=assert(loadfile(DIR..'calendar.lua'))();A.calendar=calendar.new(DIR,codec);A.holidays=assert(loadfile(DIR..'holiday_update.lua'))().new(A,DIR,codec,calendar,A.calendar.apply)
A.birthday='';A.birthday_preview_until=0
function A.birthday_active(t)return A.elapsed_ms<A.birthday_preview_until or(t and A.birthday==string.format('%02d-%02d',t.mon or 0,t.day or 0))or false end
A.elapsed_ms=0;A.needsDisplay='changed';A.needsDisplaySeconds=10;A.workStart='09:00';A.workEnd='18:00'
A.needs=assert(loadfile(DIR..'life.lua'))().new(DIR,codec)
A.weather=assert(loadfile(DIR..'weather.lua'))().new(A,DIR,codec)
A.hud=assert(loadfile(DIR..'hud.lua'))().new(A,DIR,panel)
local current
A.player=assert(loadfile(DIR..'frame_player.lua'))().new(DIR,A.actor,codec)
local function clear_actor()A.player.close()end
local function load_actor(path)
 local ok,e=A.player.load(path,current.x,current.y-layout.safe_top)
 assert(ok,e)
end
function A.render()
 if not current then return end
 local elapsed=A.activity_elapsed_ms or 0
 if current.loop_file then
  if A.sequence_phase=='loop'then elapsed=(elapsed-current.duration_ms)%current.loop_duration_ms
  elseif A.sequence_phase=='outro'then elapsed=elapsed-current.duration_ms-A.sequence_loop_total end
 else elapsed=elapsed%current.duration_ms end
 local ok,e=A.player.show(elapsed)
 if ok==false and (A.player.failure_ms or 0)>1000 then A.error=e elseif ok==true then A.error=nil end
end
-- Local deterministic RNG, independent of other apps' math.random state.
local seed=1
pcall(function()local t=time.getlocal();seed=math.max(1,((t.hour or 0)*3600+(t.min or 0)*60+(t.sec or 0)+1)) end)
pcall(function()if tmr.now then seed=math.max(1,tmr.now()%2147483647) end end)
local function pick(count) seed=(seed*48271)%2147483647;return seed%count end
function A.set_activity(id,recoverySeconds,highMoodDance)
 if not A.running then return false end
 current=nil
 for _,asset in ipairs(layout.assets) do if asset.id==id then current=asset;break end end
 if current and current.variants then
  local choice=pick(#current.variants+1);if choice>0 then current=current.variants[choice] end
 end
 A.mealVariant=id=='eat' and (current.variant or 'rice') or nil
 if recoverySeconds==true then recoverySeconds=A.needs.seconds(current) end
 A.highMoodDance=id=='dance'and highMoodDance==true;A.recoveryBoost=recoverySeconds~=nil;A.activity=id;A.activity_elapsed_ms=0;A.idle_check_ms=0;A.sequence_phase="intro";A.error=nil;clear_actor()
 if current and current.loop_file then
  A.sequence_loop_total=math.max(1,math.ceil((recoverySeconds or A.activity_seconds[id] or current.loop_seconds or 30)*1000/current.loop_duration_ms))*current.loop_duration_ms
 end
 local ok,err=pcall(function()
  assert(current,"Unknown asset: "..tostring(id))
  assert(current.y>=layout.safe_top and current.y+current.height*current.zoom/256<=layout.actor_bottom,"Asset outside actor area")
  assert(file.exists(DIR..current.file),"Missing asset: "..current.file)
  if current.loop_file then
   assert(file.exists(DIR..current.loop_file),"Missing asset: "..current.loop_file)
   assert(file.exists(DIR..current.outro_file),"Missing asset: "..current.outro_file)
  end
  load_actor(current.file)
 end)
 if not ok then A.error=tostring(err);clear_actor();print("[Nono] "..A.error) end
 return ok
end
A.auto=true;A.elapsed_ms=0;A.activity_seconds={}
for _,asset in ipairs(layout.assets) do
 if asset.loop_file then A.activity_seconds[asset.id]=math.max(5,math.min(600,tonumber(asset.loop_seconds or (asset.id=="eat" and layout.meal_seconds)) or 30)) end
end
function A.set_activity_seconds(id,seconds)
 assert(A.activity_seconds[id],"Activity has no timed loop")
 A.activity_seconds[id]=math.max(5,math.min(600,tonumber(seconds) or 30))
end
function A.profession()return 'science'end
function A.request_activity(id)
 A.set_activity(id);A.reset_auto()
end
function A.set_meal_seconds(seconds) A.set_activity_seconds("eat",seconds) end
local function sequence_total()
 return current.duration_ms+A.sequence_loop_total+current.outro_duration_ms
end
function A.reset_auto()
 if current and current.return_activity then A.next_ms=A.elapsed_ms+(current.loop_file and sequence_total() or current.duration_ms);return end
 A.next_ms=A.elapsed_ms+(layout.auto_min_cycles+pick(layout.auto_max_cycles-layout.auto_min_cycles+1))*(current and current.duration_ms or layout.loop_ms)
end
function A.set_auto(enabled)
 A.auto=enabled==true
 if A.auto then A.request_activity(layout.default_activity) end
end
function A.advance(ms)
 A.render()
 if not A.running then return end
 local before=A.activity_elapsed_ms or 0
 local active=0
 if current and current.loop_file then active=math.max(0,math.min(before+ms,current.duration_ms+A.sequence_loop_total)-math.max(before,current.duration_ms)) end
 A.elapsed_ms=A.elapsed_ms+ms
 local dance=A.highMoodDance and not A.error and current and math.max(0,math.min(before+ms,current.duration_ms)-math.max(0,before))/1000 or 0
 A.needs.advance(A.activity,ms/1000,active/1000,A.recoveryBoost,A.elapsed_ms,dance)
 A.activity_elapsed_ms=(A.activity_elapsed_ms or 0)+ms
 if current and current.return_activity then
  local total=current.loop_file and sequence_total() or current.duration_ms
  if current.loop_file and A.activity_elapsed_ms<total then
   local phase=A.activity_elapsed_ms<current.duration_ms and "intro" or (A.activity_elapsed_ms<current.duration_ms+A.sequence_loop_total and "loop" or "outro")
   if phase~=A.sequence_phase then
    A.sequence_phase=phase
    if A.player then
     local path=phase=="loop" and current.loop_file or current.outro_file
     local ok,err=pcall(load_actor,path)
     if not ok then A.error=tostring(err) end
    end
   end
  end
  if A.activity_elapsed_ms>=total then A.set_activity(current.return_activity);A.reset_auto() end
  return
 end
 if not A.auto then return end
 if current and A.activity_elapsed_ms>=(A.idle_check_ms or 0)+current.duration_ms then
  A.idle_check_ms=math.floor(A.activity_elapsed_ms/current.duration_ms)*current.duration_ms
  local urgent=A.needs.urgent()
  if urgent then
   if urgent=='play' then local play={'game','pet','laser'};urgent=play[pick(3)+1]end
   for _,asset in ipairs(layout.assets)do if asset.id==urgent then A.set_activity(urgent,true);A.reset_auto();return end end
  end
  if A.activity=='idle'and A.needs.mood>90 then A.set_activity('dance',nil,true);A.reset_auto();return end
 end
 if A.elapsed_ms<A.next_ms then return end
 local candidates={}
 for _,asset in ipairs(layout.assets) do if not asset.manual_only and asset.id~=A.activity and asset.id~="eat" and asset.id~="sleep" then candidates[#candidates+1]=asset.id end end
 if #candidates>0 then A.set_activity(candidates[pick(#candidates)+1]) end
 A.reset_auto()
end
function A.set_mask(enabled,height)
 A.mask_enabled=enabled==true
 lv_obj_set_size(A.mask,320,math.max(0,math.min(96,tonumber(height) or layout.safe_top)))
 lv_obj_set_style_bg_opa(A.mask,A.mask_enabled and 225 or 0,STYLE)
end
function A.tick()
 if not A.running then return end
 if app and app.exiting and app.exiting() then A.stop("app.exiting");return end
 local ok,t=pcall(function()return time.getlocal()end)
 local valid=ok and type(t)=="table" and tonumber(t.year) and t.year>=2024
  and tonumber(t.hour) and t.hour>=0 and t.hour<24 and tonumber(t.min) and t.min>=0 and t.min<60
 A.clock=valid and string.format('%02d:%02d:%02d',t.hour,t.min,t.sec or 0)or '--:--:--'
 A.hud.update(valid and t or nil)
 A.weather.poll(A.elapsed_ms,valid and t or nil)
 A.holidays.poll(A.elapsed_ms,valid and t or nil)
 if A.elapsed_ms-(A.last_save or 0)>=30000 then A.last_save=A.elapsed_ms;A.needs.save()end
end
function A.snapshot()
 return {ok=true,platform='device',version=A.version,clock=A.clock,activity=A.activity,profession=A.profession(),mealVariant=A.mealVariant,auto=A.auto,mask=A.mask_enabled==true,seconds=A.activity_seconds,error=A.error,needs=A.needs.snapshot(),recoveryBoost=A.recoveryBoost,highMoodDance=A.highMoodDance==true,leftRegion=A.leftRegion,rightRegion=A.rightRegion,needsDisplay=A.needsDisplay,needsDisplaySeconds=A.needsDisplaySeconds,birthday=A.birthday,workStart=A.workStart,workEnd=A.workEnd,holidayStatus=A.holidays.status,weatherStatus=A.weather.status,weatherCity=A.weather.location,sequencePhase=A.sequence_phase,activityElapsedMs=A.activity_elapsed_ms,gifProfile='rgb565-checked-25fps',playback=A.player.stats()}
end
function A.configure(p)
 local birthday=p.birthday;if birthday==nil then birthday=A.birthday end
 local function validBirthday(v)
  if v==''then return true end
  if type(v)~='string'then return false end
  local m,d=v:match('^(%d%d)%-(%d%d)$');m=tonumber(m);d=tonumber(d)
  return m and m>=1 and m<=12 and d>=1 and d<=({31,29,31,30,31,30,31,31,30,31,30,31})[m]
 end
 if not validBirthday(birthday)then return false,'生日请填写有效公历月日，如10-20'end
 if p.birthdayPreview~=nil and type(p.birthdayPreview)~='boolean'then return false,'预览格式错误'end
 local seconds={};for id,n in pairs(A.activity_seconds)do seconds[id]=n end
 if p.seconds~=nil then
  if type(p.seconds)~='table' then return false,'时长格式错误'end
  for id,n in pairs(p.seconds)do if not seconds[id] or type(n)~='number' or n~=math.floor(n) or n<5 or n>600 then return false,'时长应为5–600整数秒'end;seconds[id]=n end
 end
 for _,k in ipairs({'auto','mask'})do if p[k]~=nil and type(p[k])~='boolean' then return false,'开关格式错误'end end
 if p.activity~=nil then local found=false;for _,a in ipairs(layout.assets)do if a.id==p.activity then found=true end end;if not found then return false,'未知活动'end end
 local display=p.needsDisplay or A.needsDisplay
 local duration=p.needsDisplaySeconds or A.needsDisplaySeconds
 local ws=p.workStart or A.workStart;local we=p.workEnd or A.workEnd
 local function validTime(v)return type(v)=='string' and v:match('^%d%d:%d%d$')and tonumber(v:sub(1,2))<24 and tonumber(v:sub(4,5))<60 end
 if display~='changed' and display~='always' and display~='hidden' then return false,'属性显示模式错误'end
 if type(duration)~='number' or duration~=math.floor(duration) or duration<1 or duration>600 then return false,'显示时长应为1–600整数秒'end
 if not validTime(ws)or not validTime(we)or ws>=we then return false,'上班时间应早于下班时间'end
 for _,k in ipairs({'leftRegion','rightRegion'})do if p[k]~=nil and not calendar.valid(p[k])then return false,'底部区域内容错误'end end
 local left=p.leftRegion or A.leftRegion;local right=p.rightRegion or A.rightRegion
 if not calendar.valid(left)or not calendar.valid(right)then return false,'底部区域内容错误'end
 local next_auto=A.auto;if p.auto~=nil then next_auto=p.auto end;if p.activity then next_auto=false end
 local next_mask=A.mask_enabled==true;if p.mask~=nil then next_mask=p.mask end
 local ok,err=pcall(function()assert(file.putcontents,'Settings write API missing');local result=file.putcontents(DIR..'user-settings.json',codec.encode({seconds=seconds,auto=next_auto,mask=next_mask,leftRegion=left,rightRegion=right,needsDisplay=display,needsDisplaySeconds=duration,birthday=birthday,workStart=ws,workEnd=we}));if result==false then error('设置保存失败')end end)
 if not ok then return false,tostring(err)end
 A.leftRegion=left;A.rightRegion=right;A.needsDisplay=display;A.needsDisplaySeconds=duration;A.workStart=ws;A.workEnd=we
 A.birthday=birthday;if p.birthdayPreview~=nil then A.birthday_preview_until=p.birthdayPreview and A.elapsed_ms+15000 or 0 end
 A.activity_seconds=seconds;A.set_mask(next_mask)
 if p.activity then A.auto=false;A.request_activity(p.activity)
 elseif next_auto~=A.auto then A.set_auto(next_auto)end
 return true
end
function A.stop(reason)
 if not A.running then return end
 A.needs.save();A.weather.stop();A.holidays.stop()
 A.running=false
 if A.web then A.web:stop();A.web=nil end
 if A.timer then pcall(function()A.timer:stop();A.timer:unregister()end);A.timer=nil end
 if A.key_registered and key and key.off then pcall(key.off);A.key_registered=false end
 clear_actor()
 if A.root then pcall(lv_obj_del,A.root);A.root=nil end
 A.hud.free()
 if rawget(_G,"NONO_APP")==A then _G.NONO_APP=nil end
end
A.shutdown=A.stop
A.set_activity(layout.default_activity)
A.reset_auto()
A.tick()
if file.exists(DIR..'user-settings.json')then
 local ok,p=pcall(function()return codec.decode(file.getcontents(DIR..'user-settings.json'))end)
 if ok and type(p)=='table'then local saved,err=A.configure(p);if not saved then print('[Nono] settings: '..tostring(err))end end
end
if httpd and httpd.dynamic then
 local ok,err=pcall(function()A.web=assert(loadfile(DIR..'web.lua'))().new(DIR,A);A.web:start()end)
 if not ok then if A.web then pcall(function()A.web:stop()end)end;print('[Nono] WebUI: '..tostring(err))end
end
if key and key.on then
 key.on(function(code,event)
  if not A.running or event~=key.START then return end
  -- Manual debug override; DOWN resumes autonomous activity selection.
  if code==key.LEFT or code==key.RIGHT then
   A.auto=false
   local choices={};for _,a in ipairs(layout.assets)do if not a.manual_only then choices[#choices+1]=a end end
   local index=1
   for i,asset in ipairs(choices)do if asset.id==A.activity then index=i;break end end
   index=((index-1+(code==key.RIGHT and 1 or -1))%#choices)+1
   A.request_activity(choices[index].id)
  elseif key.DOWN and code==key.DOWN then A.set_auto(true)
  elseif code==key.UP then A.set_mask(not A.mask_enabled) end
 end)
 A.key_registered=true
end
local clock_elapsed=0
local last_us=tmr.now and tmr.now()
A.timer=tmr.create();A.timer:alarm(10,tmr.ALARM_AUTO,function()
 local ms=10
 if last_us then local now=tmr.now();ms=math.max(0,math.min(5000,(now-last_us)%2147483648/1000));last_us=now end
 clock_elapsed=clock_elapsed+ms
 if clock_elapsed>=250 then clock_elapsed=0;A.tick() end
 A.advance(ms)
 A.render()
end)
print("[Nono] automatic life ready; LEFT/RIGHT manual action, DOWN auto, UP safe-area mask")

