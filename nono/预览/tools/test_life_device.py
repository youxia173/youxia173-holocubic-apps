"""Phase-1 device adapter tests with mocked LVGL/time/file APIs; not a hardware emulator."""
from pathlib import Path
import json
from lupa.lua53 import LuaRuntime
from PIL import Image

ROOT = Path(__file__).resolve().parents[2] / "代码"
layout = json.loads((ROOT / "frame-layout.json").read_text(encoding="utf-8"))
def runtime(gif=True):
    lua = LuaRuntime(unpack_returned_tuples=True)
    def table(value):
        if isinstance(value, dict):
            return lua.table_from({k: table(v) for k, v in value.items()})
        if isinstance(value, list):
            return lua.table_from([table(v) for v in value])
        return value
    lua.globals().py_exists = lambda p: (ROOT / p.removeprefix("/sd/apps/nono/")).is_file()
    lua.globals().py_read = lambda p: (ROOT / p.removeprefix("/sd/apps/nono/")).read_text(encoding="utf-8")
    lua.globals().py_decode = lambda raw: table(json.loads(raw))
    lua.execute("""
objects={[1]={parent=0}};next_id=1;calls=0;released=0
LV_PART_MAIN=0;LV_STATE_DEFAULT=0;LV_OBJ_FLAG_SCROLLABLE=1
local function object(parent) next_id=next_id+1;objects[next_id]={parent=parent};return next_id end
lv_obj_create=object;lv_img_create=object;lv_gif_create=object
function lv_scr_act() return 1 end
function lv_obj_del(id)
 assert(objects[id],"double deletion")
 local children={};for k,v in pairs(objects)do if v.parent==id then children[#children+1]=k end end
 for _,k in ipairs(children)do lv_obj_del(k)end
 objects[id]=nil
end
function lv_obj_clean(id)
 assert(objects[id],"cleaning dead object")
 local children={};for k,v in pairs(objects)do if v.parent==id then children[#children+1]=k end end
 for _,k in ipairs(children)do lv_obj_del(k)end
end
function lv_obj_set_pos(id,x,y) assert(objects[id]);objects[id].x=x;objects[id].y=y end
function lv_obj_set_size(id,w,h) assert(objects[id]);objects[id].w=w;objects[id].h=h end
function lv_img_set_src(id,p)
 assert(objects[id],"image update after deletion")
 assert(p:sub(1,13)=="S:/apps/nono/","wrong LVGL SD image source path")
 objects[id].src=p;calls=calls+1
end
function lv_gif_set_src(id,p) assert(objects[id]);objects[id].src=p end
function lv_img_set_pivot(id,x,y)objects[id].pivot={x,y}end
function lv_img_set_zoom(id,z)objects[id].zoom=z end
function lv_obj_set_style_bg_opa(id,a,style)objects[id].alpha=a end
local function noop(...)end
lv_obj_set_style_bg_color=noop;lv_obj_set_style_border_width=noop;lv_obj_set_style_pad_all=noop
lv_obj_set_style_radius=noop;lv_obj_clear_flag=noop
file={exists=py_exists,getcontents=py_read}
sjson={decode=py_decode}
clock={year=2026,hour=23,min=59}
time={getlocal=function()return clock end}
app={exiting=function()return false end}
key={START=1,LEFT=2,RIGHT=3,UP=4,DOWN=5,on=function(f)key_callback=f end,off=function()key_callback=nil end}
tmr={ALARM_AUTO=1,create=function()return {
 alarm=function(self,ms,kind,fn) timer_callback=fn end,
 stop=function()timer_callback=nil end,unregister=function()released=released+1 end}end}
""")
    if not gif:
        lua.globals().lv_gif_create = None
    lua.globals().py_module = lambda p: "return {new=function()return {close=function()end,load=function()return true end,show=function()return true end,stats=function()return {}end}end}" if p.endswith('frame_player.lua') else (ROOT / p.removeprefix('/sd/apps/nono/')).read_text('utf-8-sig')
    lua.execute("""
local oldread=file.getcontents
file.getcontents=function(p) if p:match('layout.json$')then return oldread(p)end;return nil end
file.putcontents=function(p,v)return true end
sjson.encode=function(v)return '{}'end
loadfile=function(p)return assert(load(py_module(p)))end
LV_OBJ_FLAG_HIDDEN=2
lv_label_create=lv_obj_create
lv_label_set_text=function(id,v)objects[id].text=v end
lv_font_load=function(p)return 10 end;lv_font_free=function()end
lv_obj_add_flag=function(id,f)objects[id].hidden=true end
lv_obj_clear_flag=function(id,f)objects[id].hidden=false end
lv_obj_set_style_text_font=function()end;lv_obj_set_style_text_color=function()end;lv_obj_set_style_text_align=function()end
clock.sec=35;clock.mon=10;clock.day=18;clock.wday=1
""")
    return lua, table

script=(ROOT/'main.lua').read_text('utf-8-sig')
lua,tab=runtime();lua.execute(script);a=lua.globals().NONO_APP
assert a.clock=='23:59:35'
assert a.snapshot().version=='1.0.6'
a.needs.satiety=29;a.needs.energy=80;a.needs.mood=80
a.advance(next(x['duration_ms'] for x in layout['assets'] if x['id']=='idle'))
assert a.activity=='eat' and a.recoveryBoost
loop=a.sequence_loop_total
assert loop>=25000 and loop<40000
meal=next(x for x in layout['assets'] if x['id']=='eat')
def selected():
 return meal['variants'][0] if a.mealVariant=='ramen' else meal
asset=selected()
a.advance(asset['duration_ms']+loop+asset['outro_duration_ms'])
assert a.activity=='idle' and not a.recoveryBoost and a.needs.satiety>=80
before=a.needs.satiety
a.auto=False;a.set_activity('eat');asset=selected();a.advance(asset['duration_ms']+5000)
assert 4<a.needs.satiety-before<5
assert not a.recoveryBoost
assert a.configure(tab({'needsDisplay':'always','needsDisplaySeconds':12,'workStart':'08:30','workEnd':'17:30'}))==True
a.tick();assert not lua.globals().objects[a.hud.head].hidden
assert a.configure(tab({'workStart':'18:00','workEnd':'08:00'}))[0]==False
assert a.workStart=='08:30'
a.needs.satiety=30;a.needs.energy=25;a.needs.mood=35
assert a.needs.urgent() is None
a.needs.energy=10;assert a.needs.urgent()=='sleep'
a.needs.satiety=1;assert a.needs.urgent()=='eat'
a.needs.level=1;a.needs.xp=99;a.needs.advance('read',2,2,True,0)
assert a.needs.level==2 and a.needs.xp==1
seen=set()
for seconds in (5,600):
 a.set_activity_seconds('eat',seconds)
 for _ in range(30):
  a.set_activity('eat');asset=selected();seen.add(a.mealVariant)
  variant=a.mealVariant;loop=a.sequence_loop_total
  assert seconds*1000<=loop<seconds*1000+asset['loop_duration_ms']
  a.advance(asset['duration_ms']);assert a.sequence_phase=='loop' and a.mealVariant==variant
  a.advance(loop);assert a.sequence_phase=='outro' and a.mealVariant==variant
  a.advance(asset['outro_duration_ms']);assert a.activity=='idle' and a.error is None
assert seen=={'rice','ramen'}
seen=set()
for _ in range(30):
 a.needs.satiety=29;a.set_activity('eat',True);asset=selected();seen.add(a.mealVariant)
 a.advance(asset['duration_ms']+a.sequence_loop_total+asset['outro_duration_ms'])
 assert a.activity=='idle' and 80<=a.needs.satiety<91
 assert a.activity_seconds['eat']==600
assert seen=={'rice','ramen'}
a.stop('test');assert len(list(lua.globals().objects.keys()))==1
print('PASS Cubic: startup, clock seconds, need thresholds, doubled automatic recovery, normal manual gains, XP, settings validation, cleanup')
