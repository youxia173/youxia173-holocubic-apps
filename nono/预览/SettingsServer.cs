using System;
using System.IO;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Collections.Generic;
using System.Web.Script.Serialization;
using System.Windows.Forms;

// Loopback-only, bounded HTTP requests; changes require the per-process page token.
public sealed class SettingsServer:IDisposable {
 readonly HttpListener listener=new HttpListener();
 readonly NonoPreview owner;readonly string root,token=Guid.NewGuid().ToString("N");
 volatile bool stopped;public readonly string Url;
 public SettingsServer(NonoPreview form,string code){
  owner=form;root=code;var port=new TcpListener(IPAddress.Loopback,0);port.Start();int number=((IPEndPoint)port.LocalEndpoint).Port;port.Stop();Url="http://127.0.0.1:"+number+"/";listener.Prefixes.Add(Url);listener.Start();
  var thread=new Thread(Run);thread.IsBackground=true;thread.Start();
 }
 void Run(){
  while(!stopped){
   try{
    var client=listener.GetContext();
    ThreadPool.QueueUserWorkItem(delegate{
     {
      try{Handle(client);}
      catch(Exception ex){if(!stopped){try{File.AppendAllText(Path.Combine(root,"..","预览","网页错误.log"),DateTime.Now+" "+ex+Environment.NewLine);}catch{}}}
     }
    });
   }catch(Exception){if(stopped)return;}
  }
 }
 void Handle(HttpListenerContext context){
  var req=context.Request;long length=req.ContentLength64;
  if(length>4096||req.HttpMethod=="POST"&&length<0){Reply(context,413,"text/plain",Encoding.UTF8.GetBytes("Request too large"));return;}
  byte[] bytes=new byte[Math.Max(0,length)];int read=0;while(read<bytes.Length){int n=req.InputStream.Read(bytes,read,bytes.Length-read);if(n==0)break;read+=n;}
  string[] request={req.HttpMethod};string path=req.Url.AbsolutePath,mime="application/json; charset=utf-8";int status=200;byte[] body;
  var json=new JavaScriptSerializer();
  try{
   if(request[0]=="GET"&&path=="/"){mime="text/html; charset=utf-8";body=Encoding.UTF8.GetBytes(File.ReadAllText(Path.Combine(root,"..","预览","windows-settings.html")).Replace("__BASE__","").Replace("__TOKEN__",token));}
   else if(request[0]=="GET"&&path=="/icon.png"){mime="image/png";body=File.ReadAllBytes(Path.Combine(root,"main.png"));}
   else if(request[0]=="GET"&&path=="/api/state")body=Encoding.UTF8.GetBytes(json.Serialize(owner.Invoke(new Func<object>(owner.WebState))));
   else if(request[0]=="POST"&&path=="/api/settings"){
    var data=json.Deserialize<Dictionary<string,object>>(Encoding.UTF8.GetString(bytes));
    if(data==null||!data.ContainsKey("token")||!token.Equals(data["token"])){status=403;body=Encoding.UTF8.GetBytes("{\"ok\":false,\"error\":\"请刷新设置页面\"}");}
    else body=Encoding.UTF8.GetBytes(json.Serialize(owner.Invoke(new Func<object>(()=>owner.ApplyWeb(data)))));
   }else{status=404;body=Encoding.UTF8.GetBytes("{\"ok\":false,\"error\":\"Not found\"}");}
  }catch(Exception ex){status=400;body=Encoding.UTF8.GetBytes(json.Serialize(new {ok=false,error=ex.InnerException==null?ex.Message:ex.InnerException.Message}));}
  Reply(context,status,mime,body);
 }
 static void Reply(HttpListenerContext c,int status,string mime,byte[] body){var r=c.Response;r.StatusCode=status;r.ContentType=mime;r.ContentLength64=body.Length;r.Headers["Cache-Control"]="no-store";r.Headers["X-Content-Type-Options"]="nosniff";r.OutputStream.Write(body,0,body.Length);r.Close();}
 public void Dispose(){stopped=true;listener.Stop();}
}
