local M={}
function M.new(A,dir,panel)
 local H={};local S=0;local font=assert(lv_font_load(dir..'font/ui10-bold.bin'))
 local function label(parent,x,y,w,f,color)
  local o=lv_label_create(parent);lv_obj_set_pos(o,x,y);lv_obj_set_size(o,w,14)
  lv_obj_set_style_text_font(o,f or font,S);lv_obj_set_style_text_color(o,color or 0xb9d9eb,S)
  return o
 end
 local texts={}
 local function text(o,v)if texts[o]~=v then lv_label_set_text(o,v);texts[o]=v end end
 H.head=panel(A.root,0,0,320,44,0);H.bars={}
 for i,name in ipairs({'饱食','心情','活力','等级'})do
  local x=i%2==1 and 12 or 166;local y=i<=2 and 2 or 24
  local o=label(H.head,x,y,142);local bg=panel(H.head,x,y+15,142,3,255)
  lv_obj_set_style_bg_color(bg,0x233747,S)
  local bar=panel(bg,0,0,142,3,255);lv_obj_set_style_bg_color(bar,({0xf0c276,0xf1a5bb,0x91d7bc,0x94b8ff})[i],S)
  H.bars[i]={label=o,bar=bar,name=name}
 end
 -- Fixed cells keep HH:mm:ss centered independently of glyph advances.
 H.clock=panel(A.root,104,184,112,24,0);H.clock_digits={}
 local clock_x=0
 for i=1,8 do
  local width=(i==3 or i==6)and 8 or 16
  local o=label(H.clock,clock_x,0,width,rawget(_G,'LV_FONT_MONTSERRAT_20')or 20,0xe0f4ff)
  lv_obj_set_size(o,width,24)
  lv_obj_set_style_text_align(o,rawget(_G,'LV_TEXT_ALIGN_CENTER')or 1,S)
  H.clock_digits[i]=o;clock_x=clock_x+width
 end
 H.date=label(A.root,94,208,132);H.work=label(A.root,86,224,148)
 for _,o in ipairs({H.date,H.work})do lv_obj_set_style_text_align(o,rawget(_G,'LV_TEXT_ALIGN_CENTER')or 1,S)end
 H.weather={}
 for i,x in ipairs({7,239})do
  local image=lv_img_create(A.root);lv_obj_set_pos(image,x,201)
  H.weather[i]={label(A.root,x,187,75),label(A.root,x+22,204,53),label(A.root,x,221,75),icon=image}
 end
 H.birthday_images={}
 for _,spec in ipairs({{'header',0},{'footer',182}})do
  local o=lv_img_create(A.root);lv_img_set_src(o,'S:/apps/nono/assets/ui/birthday-'..spec[1]..'.png');lv_obj_set_pos(o,0,spec[2]);lv_obj_add_flag(o,LV_OBJ_FLAG_HIDDEN);H.birthday_images[#H.birthday_images+1]=o
 end
 local days={'日' ,'一','二','三','四','五','六'}
 local function minutes(v)return tonumber(v:sub(1,2))*60+tonumber(v:sub(4,5))end
 function H.update(t)
  local birthday=A.birthday_active(t)
  local function visible(o,on)if on then lv_obj_clear_flag(o,LV_OBJ_FLAG_HIDDEN)else lv_obj_add_flag(o,LV_OBJ_FLAG_HIDDEN)end end
  if H.birthday~=birthday then
   for _,o in ipairs(H.birthday_images)do visible(o,birthday)end
   visible(H.work,not birthday)
   for _,items in ipairs(H.weather)do for j=1,3 do visible(items[j],not birthday)end end
   H.birthday=birthday
  end
  local n=A.needs;local values={n.satiety,n.mood,n.energy,n.xp/n.required()*100}
  for i,b in ipairs(H.bars)do
   text(b.label,i==4 and string.format('等级 Lv.%d  %d/%d',n.level,math.floor(n.xp),n.required())or string.format('%s  %.0f',b.name,values[i]))
   local width=math.max(1,math.floor(142*values[i]/100))
   if b.width~=width then lv_obj_set_size(b.bar,width,3);b.width=width end
  end
  local shown=not birthday and A.needsDisplay~='hidden' and(A.needsDisplay=='always' or A.elapsed_ms-n.changed_at<A.needsDisplaySeconds*1000)
  if H.shown~=shown then
   if shown then lv_obj_clear_flag(H.head,LV_OBJ_FLAG_HIDDEN)else lv_obj_add_flag(H.head,LV_OBJ_FLAG_HIDDEN)end
   H.shown=shown
  end
  local clock_text=A.clock or '--:--:--'
  for i,o in ipairs(H.clock_digits)do text(o,clock_text:sub(i,i))end
  text(H.date,t and string.format('星期%s · %d月%d日',days[t.wday or 1]or '日',t.mon or 1,t.day or 1)or '等待时间同步')
  local work='等待时间同步'
  if t then
   local now=t.hour*60+t.min+(t.sec or 0)/60;local start,finish=minutes(A.workStart),minutes(A.workEnd)
   local target=now<start and start or finish;local left=math.max(0,math.ceil(target-now))
   work=now>=finish and '已到下班时间' or string.format('%s%d小时%d分',now<start and '距上班 'or '距下班 ',math.floor(left/60),left%60)
  end
  text(H.work,work)
  for i,items in ipairs(H.weather)do
   local mode=i==1 and A.leftRegion or A.rightRegion;local x=i==1 and 7 or 239
   local isweather=mode=='today'or mode=='yesterday'or mode=='tomorrow'
   if items.isweather~=isweather or items.birthday~=birthday then
    items.birthday=birthday
    if isweather and not birthday then lv_obj_clear_flag(items.icon,LV_OBJ_FLAG_HIDDEN)else lv_obj_add_flag(items.icon,LV_OBJ_FLAG_HIDDEN)end
    lv_obj_set_pos(items[2],x+(isweather and 22 or 0),204);lv_obj_set_size(items[2],isweather and 53 or 75,14);items.isweather=isweather
   end
   if isweather then
    local d=A.weather.day(t,mode=='yesterday'and -1 or mode=='tomorrow'and 1 or 0)
    local path='S:/apps/nono/assets/ui/weather-'..A.weather.icon(d)..'.png'
    if items.icon_path~=path then lv_img_set_src(items.icon,path);items.icon_path=path end
    text(items[1],mode=='yesterday'and'昨天天气*'or mode=='today'and'今日天气'or'明日天气')
    text(items[2],d and(d.textDay or '--')or '--')
    text(items[3],d and(tostring(d.tempMin)..'~'..tostring(d.tempMax)..'°C')or(mode=='yesterday'and'暂无记录'or'等待更新'))
   else
    local rows=A.calendar.describe(mode,t);for j=1,3 do text(items[j],rows[j])end
   end
  end
 end
 function H.free()if font and lv_font_free then lv_font_free(font);font=nil end end
 return H
end
return M
