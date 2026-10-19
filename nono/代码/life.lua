local M={}
function M.new(dir,codec)
 local N={satiety=80,mood=80,energy=80,xp=0,level=1,changed_at=-1000000,signature=nil}
 local function clamp(v)return math.max(0,math.min(100,v))end
 function N.required()return 100+25*(N.level-1)end
 function N.load()
  for _,name in ipairs({'needs.json','needs.bak.json'})do
   local ok,v=pcall(function()return codec.decode(file.getcontents(dir..name) or '')end)
   if ok and type(v)=='table' and type(v.level)=='number' and v.level>=1 and v.level<=100000 and v.level==math.floor(v.level) and type(v.xp)=='number' and v.xp>=0 and v.xp<100+25*(v.level-1) and type(v.satiety)=='number' and type(v.mood)=='number' and type(v.energy)=='number' then
    N.satiety=clamp(v.satiety);N.mood=clamp(v.mood);N.energy=clamp(v.energy);N.xp=v.xp;N.level=v.level;return
   end
  end
 end
 function N.snapshot()return {satiety=N.satiety,mood=N.mood,energy=N.energy,xp=N.xp,level=N.level,required=N.required()}end
 function N.save()
  local ok,e=pcall(function()
   local old=file.getcontents(dir..'needs.json')
   if old then local valid,value=pcall(codec.decode,old);if valid and type(value)=='table' then assert(file.putcontents(dir..'needs.bak.json',old)~=false)end end
   assert(file.putcontents(dir..'needs.json',codec.encode(N.snapshot()))~=false)
  end);return ok,e
 end
 function N.observe(now)
  local key=string.format('%.0f/%.0f/%.0f/%d/%d',N.satiety,N.mood,N.energy,N.level,math.floor(N.xp))
  if N.signature and key~=N.signature then N.changed_at=now end;N.signature=key
 end
 function N.advance(id,dt,active,boost,now)
  local gain=boost and 2 or 1
  N.satiety=clamp(N.satiety-dt/120+(id=='eat' and active*gain or 0))
  N.mood=clamp(N.mood-dt/200+((id=='game' or id=='pet' or id=='laser')and active*.8*gain or 0))
  N.energy=clamp(N.energy-(dt-(id=='sleep' and active or 0))/150+(id=='sleep' and active*.8*gain or 0))
  if id=='read' then N.xp=N.xp+active end
  while N.xp>=N.required()do N.xp=N.xp-N.required();N.level=N.level+1 end
  N.observe(now)
 end
 function N.urgent()
  local id,ratio=nil,1
  if N.satiety<30 then id='eat';ratio=N.satiety/30 end
  if N.energy<25 and N.energy/25<ratio then id='sleep';ratio=N.energy/25 end
  if N.mood<35 and N.mood/35<ratio then id='play' end
  return id
 end
 function N.seconds(a)
  local value,target,decay,gain=N.mood,80,1/200,1.6
  if a.id=='eat' then value,target,decay,gain=N.satiety,80,1/120,2
  elseif a.id=='sleep' then value,target,decay,gain=N.energy,85,1/150,1.6 end
  return math.max(5,math.ceil((target-value+decay*(a.duration_ms+a.outro_duration_ms)/1000)/(gain-(a.id=='sleep' and 0 or decay))))
 end
 N.load();N.observe(0);return N
end
return M
