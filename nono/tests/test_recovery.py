from runtime_fixture import ROOT, runtime, layout

def app():
    lua, tab = runtime()
    lua.execute((ROOT/'main.lua').read_text('utf-8'))
    a = lua.globals().NONO_APP
    a.auto = False
    return a, lua

a,l=app()
l.execute("local old=file.exists;file.exists=function(p)if deny then return false end;return old(p)end;deny=true")
assert a.set_activity('read') is False
for _ in range(99):a.advance(10);a.render()
assert a.elapsed_ms==990 and a.activity_elapsed_ms==0 and a.load_retry
l.globals().deny=False;a.advance(10)
assert not a.load_retry and a.activity=='read'
a.advance(40);assert a.activity_elapsed_ms==40

a,l=app()
l.execute("local old=NONO_APP.player.load;NONO_APP.player.load=function(p,...)if p:find('read')then error('missing data')end;return old(p,...)end")
a.set_activity('read')
for _ in range(300):a.advance(10)
assert a.activity=='idle' and not a.load_retry

# Loop load failure and renderer exceptions use the same bounded recovery path.
a,l=app();a.set_activity('read')
l.execute("NONO_APP.player.load=function()error('loop read failure')end")
a.advance(next(x['duration_ms'] for x in layout['assets'] if x['id']=='read'))
assert a.load_retry
for _ in range(1000):a.advance(10)
assert a.activity=='idle' and a.load_retry

a,l=app();l.execute("NONO_APP.player.show=function()if broken then error('decode exception')end;return true end;broken=true")
a.advance(10);assert a.load_retry
l.globals().broken=False;a.advance(990);assert not a.load_retry

a,l=app();a.auto=True
l.execute("""
local old=file.exists;local checks=0;local frames=0
injected=0;print=function()end
file.exists=function(p)checks=checks+1;if checks%173==0 then injected=injected+1;return false end;return old(p)end
NONO_APP.player.show=function()frames=frames+1;if frames%8000==0 then injected=injected+1;error('decode fault')end;return true end
for i=1,86400 do NONO_APP.advance(1000);NONO_APP.render()end
""")
assert a.elapsed_ms==86400000 and l.globals().injected>0
assert {x['id'] for x in layout['assets']}=={'idle','eat','sleep','read','game','pet','laser','dance'}
print('PASS: transient recovery, three-retry idle fallback, loop failure, renderer exception, 24h simulated scheduling;',l.globals().injected,'injected faults; lite activity set preserved')
