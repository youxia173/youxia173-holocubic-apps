-- Cubic app-relative WebUI lifecycle, following official httpd/app examples.
local Web={}
function Web.new(dir,A)
 local W={routes={},base=app.route_base and app.route_base() or '/nono',token=tostring(tmr.now())..'-'..tostring(math.random(100000,999999))}
 if W.base=='' then W.base='/nono' end
 local function reply(body,status,mime)return {status=status or '200 OK',type=mime or 'application/json; charset=utf-8',headers={['Cache-Control']='no-store',['X-Content-Type-Options']='nosniff'},body=body}end
 local function json(value,status)return reply(sjson.encode(value),status)end
 function W:register(method,path,fn)local route=self.base..path;assert(not httpd.dynamic(method,route,fn),'Web route failed');self.routes[#self.routes+1]={method,route}end
 function W:start()
  httpd.start({webroot='/sd',auto_index=httpd.INDEX_NONE,max_handlers=256})
  local function index()return reply(assert(file.getcontents(dir..'settings.html')):gsub('__BASE__',self.base):gsub('__TOKEN__',self.token),nil,'text/html; charset=utf-8')end
  self:register(httpd.GET,'',index);self:register(httpd.GET,'/',index)
  self:register(httpd.GET,'/icon.png',function()return reply(file.getcontents(dir..'main.png'),nil,'image/png')end)
  self:register(httpd.GET,'/api/state',function()return json(A.snapshot())end)
  self:register(httpd.POST,'/api/settings',function(req)
   local chunks,n={},0
   if req.getbody then while true do local b=req.getbody();if not b or b=='' then break end;n=n+#b;if n>4096 then return json({ok=false,error='请求过大'},'413 Payload Too Large')end;chunks[#chunks+1]=b end end
   local ok,p=pcall(sjson.decode,table.concat(chunks))
   if not ok or type(p)~='table' or p.token~=self.token then return json({ok=false,error='请刷新设置页面'},'403 Forbidden')end
   local valid,err=A.configure(p);if not valid then return json({ok=false,error=tostring(err)},'400 Bad Request')end
   return json(A.snapshot())
  end)
  if app.set_webui then app.set_webui(true)end
 end
 function W:stop()for _,r in ipairs(self.routes)do pcall(httpd.unregister,r[1],r[2])end;self.routes={};if app.set_webui then pcall(app.set_webui,false)end end
 return W
end
return Web
