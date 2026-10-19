"""Phase-1 device adapter tests with mocked LVGL/time/file APIs; not a hardware emulator."""
from pathlib import Path
import json
from lupa.lua53 import LuaRuntime
from PIL import Image

ROOT = Path(__file__).resolve().parents[2] / "代码"
layout = json.loads((ROOT / "layout.json").read_text(encoding="utf-8"))
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
    return lua, table

script = (ROOT / "main.lua").read_text(encoding="utf-8")
lua, to_table = runtime()
lua.execute(script)
a = lua.globals().NONO_APP
assert a.clock == "23:59"
digit_ids = [a.digits[i] for i in range(1, 6)]
assert a.set_activity("sleep")
assert all(lua.globals().objects[i] is not None for i in digit_ids)
a.tick()
assert a.clock == "23:59"
lua.globals().clock = to_table({"year":2026,"hour":0,"min":0})
a.tick()
assert a.clock == "00:00"
a.set_mask(True, 96)
assert lua.globals().objects[a.mask].h == 96
assert not a.set_activity("missing")
a.tick()
assert a.clock == "00:00" and a.error
assert all(lua.globals().objects[i] is not None for i in digit_ids)
assert a.set_activity("idle")
lua.globals().clock = to_table({"year":1970,"hour":0,"min":0})
a.tick()
assert a.clock == "--:--"
assert lua.globals().objects[a.status].src.endswith("status-time.png")
# The timer polls lifecycle exit even with GIF active.
a.set_activity("sleep")
lua.execute("app.exiting=function()return true end")
a.tick()
assert not a.running and lua.globals().NONO_APP is None
assert lua.globals().released == 1
assert len(list(lua.globals().objects.keys())) == 1
# Autonomous scheduler: full-loop dwell, every action reachable, no immediate repeats.
lua, _ = runtime()
lua.execute(script)
a = lua.globals().NONO_APP
assets={x['id']:x for x in layout['assets']}
import math
def total(asset,seconds=None):
    if 'loop_file' not in asset:return asset['duration_ms']
    seconds=seconds if seconds is not None else asset.get('loop_seconds',layout.get('meal_seconds',30) if asset['id']=='eat' else 30)
    return asset['duration_ms']+math.ceil(seconds*1000/asset['loop_duration_ms'])*asset['loop_duration_ms']+asset['outro_duration_ms']
seen={a.activity}
for _ in range(100):
    before=a.activity
    delay=a.next_ms-a.elapsed_ms
    asset=assets[before]
    assert delay == total(asset) if 'loop_file' in asset else 5*asset['duration_ms'] <= delay <= 10*asset['duration_ms'] and delay % asset['duration_ms'] == 0
    a.advance(delay-1)
    assert a.activity == before
    a.advance(1)
    assert a.activity != before
    seen.add(a.activity)
assert seen == {asset['id'] for asset in layout['assets']}
# Manual key override persists until DOWN re-enables automatic playback.
lua.globals().key_callback(3,1)
manual=a.activity
a.advance(120000)
assert not a.auto and a.activity == ("idle" if "loop_file" in assets[manual] else manual)
lua.globals().key_callback(5,1)
assert a.auto and a.activity == 'idle'
a.advance(a.next_ms-a.elapsed_ms)
assert a.activity != 'idle'
a.auto=False
for activity,asset in assets.items():
    if 'loop_file' not in asset:continue
    for seconds in [5,30,95,600]:
        before_other=dict(a.activity_seconds.items())
        a.set_activity_seconds(activity,seconds)
        assert all(a.activity_seconds[k]==v for k,v in before_other.items() if k!=activity)
        a.set_activity(activity)
        expected_loops=math.ceil(seconds*1000/asset['loop_duration_ms'])*asset['loop_duration_ms']
        a.advance(asset['duration_ms']-1)
        assert a.sequence_phase=='intro'
        a.advance(1)
        assert a.sequence_phase=='loop' and lua.globals().objects[a.gif].src.endswith(asset['loop_file'])
        a.set_activity_seconds(activity,5)
        a.advance(expected_loops-1)
        assert a.sequence_phase=='loop'
        a.advance(1)
        assert a.sequence_phase=='outro' and lua.globals().objects[a.gif].src.endswith(asset['outro_file'])
        a.advance(asset['outro_duration_ms']-1)
        assert a.activity==activity
        a.advance(1)
        assert a.activity=='idle' and not a.auto
a.stop('test')

# Missing GIF APIs fail gracefully without destroying clock objects.
lua, _ = runtime(gif=False)
lua.execute(script)
a = lua.globals().NONO_APP
assert not a.set_activity("sleep")
a.tick()
assert a.clock == "23:59" and "GIF API missing" in a.error
a.stop("test")
# Manifest geometry and GIF facts are shared, not independently approximated.
for asset in layout["assets"]:
    assert (ROOT / asset["title_file"]).is_file() and (ROOT / asset["status_file"]).is_file()
    with Image.open(ROOT / asset["file"]) as im:
        assert im.size == (asset["width"], asset["height"])
        assert asset["y"] >= layout["safe_top"]
        assert asset["y"] + im.height * asset["zoom"]/256 <= layout["actor_bottom"]
        if asset["kind"] == "gif":
            assert im.n_frames == asset["frame_count"]
            duration = 0
            for index in range(im.n_frames):
                im.seek(index)
                duration += im.info["duration"]
            assert duration == asset["duration_ms"]
            im.seek(0)
            assert "transparency" in im.info
print("PASS: Lua startup; source paths; idle/sleep switch; midnight; invalid time; missing asset/API; mask; clock survives; exit cleanup; shared resource geometry; 100 random transitions; manual override/resume.")

