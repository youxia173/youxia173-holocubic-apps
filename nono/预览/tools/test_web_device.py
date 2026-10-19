import test_device as t
lua=t.runtime()[0]
lua.execute(t.script)
lua.execute('saved_settings=nil; file.putcontents=function(path,data) saved_settings=data;return true end; sjson.encode=function(value)return "saved"end')
A=lua.globals().NONO_APP
def config(code):return lua.eval('function() return NONO_APP.configure('+code+') end')()
assert config('{seconds={eat=35,read=45},auto=false,mask=true}') is True
assert A.activity_seconds.eat==35 and A.activity_seconds.read==45 and A.auto is False
assert config('{seconds={eat=4,read=70}}')[0] is False
assert A.activity_seconds.read==45
assert config('{activity="read"}') is True and A.activity=='read'
assert config('{activity="unknown"}')[0] is False and A.activity=='read'
assert config('{auto=true}') is True and A.auto is True and A.activity=='idle'
assert A.snapshot().platform=='device'
print('PASS: device settings validation, atomic rejection, independent durations, manual/auto, persistence call')
