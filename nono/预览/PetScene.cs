using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.Drawing.Drawing2D;
using System.Web.Script.Serialization;

public sealed class PetAsset {
 public string variant;
 public PetAsset[] variants;
 public string id,title,file,kind,title_file,status_file,return_activity,loop_file,outro_file;
 public int x,y,width,height,zoom,duration_ms,frame_count,loop_duration_ms,outro_duration_ms,loop_frame_count,outro_frame_count,loop_seconds;
}
public sealed class FrameAlignment {
 public string sha256;
 public float[][] frames;
}
public sealed class PetLayout {
 PetAsset[] mealChoices;
 public void SelectMeal(int choice){
  int index=Array.FindIndex(assets,a=>a.id=="eat");
  if(index<0)return;
  if(mealChoices==null){var original=assets[index];mealChoices=new[]{original}.Concat(original.variants??new PetAsset[0]).ToArray();}
  assets[index]=mealChoices[Math.Abs(choice%mealChoices.Length)];
 }
 public string version,default_activity;
 public int width,height,safe_top,actor_bottom,clock_x,clock_y,digit_width,colon_width,clock_height,title_x,title_y,status_x,status_y;
 public int auto_min_cycles,auto_max_cycles,loop_ms,meal_seconds;
 public PetAsset[] assets;
 public int LoopCount(PetAsset a,int seconds){return Math.Max(1,(int)Math.Ceiling(seconds*1000.0/a.loop_duration_ms));}
 public int ActivityDuration(PetAsset a,int seconds){return String.IsNullOrEmpty(a.loop_file)?a.duration_ms:a.duration_ms+LoopCount(a,seconds)*a.loop_duration_ms+a.outro_duration_ms;}
 public int ActivityFrames(PetAsset a,int seconds){return String.IsNullOrEmpty(a.loop_file)?a.frame_count:a.frame_count+LoopCount(a,seconds)*a.loop_frame_count+a.outro_frame_count;}

}
// Independent per-activity settings; a running sequence captures its duration on entry.
public sealed class ActivityTiming {
 readonly Dictionary<string,int> seconds=new Dictionary<string,int>();
 public ActivityTiming(PetLayout layout){
  foreach(var a in layout.assets)if(!String.IsNullOrEmpty(a.loop_file))
   seconds[a.id]=Math.Max(5,Math.Min(600,a.loop_seconds>0?a.loop_seconds:(a.id=="eat"&&layout.meal_seconds>0?layout.meal_seconds:30)));
 }
 public int Get(string id){int value;return seconds.TryGetValue(id,out value)?value:30;}
 public void Set(string id,int value){if(!seconds.ContainsKey(id))throw new ArgumentException("Unknown timed activity");seconds[id]=Math.Max(5,Math.Min(600,value));}
 public void Load(string path){
  if(!File.Exists(path))return;
  string text=File.ReadAllText(path);int old;
  if(int.TryParse(text,out old)){if(seconds.ContainsKey("eat"))Set("eat",old);return;}
  try{
   var saved=new JavaScriptSerializer().Deserialize<Dictionary<string,int>>(text);
   if(saved!=null)foreach(var pair in saved)if(seconds.ContainsKey(pair.Key))Set(pair.Key,pair.Value);
  }catch(ArgumentException){} // Keep defaults if an interrupted save left malformed JSON.
 }
 public void Save(string path){File.WriteAllText(path,new JavaScriptSerializer().Serialize(seconds));}
}
public sealed class PetScene : IDisposable {
 public readonly PetLayout Layout;
 public readonly string Root;
 public string Activity {get;private set;}
 public string MealVariant {get{return Activity=="eat"&&asset!=null?(asset.variant??"rice"):null;}}
 public string Error {get;private set;}
 public int FrameCount {get{return frames.Count;}}
 public int DurationMs {get;private set;}
 public int FrameIndex {get;private set;}
 public readonly ActivityTiming Timing;
 public PetNeeds Needs=new PetNeeds();
 public bool ShowNeeds=true;
 public bool RecoveryBoost {get;private set;}
 public TimeSpan WorkStart=TimeSpan.FromHours(9);
 public WeatherData Weather;
 public TimeSpan WorkEnd=TimeSpan.FromHours(18);
 public bool MaskEnabled,BlackBackground;
 public bool DrawBorder=true;
 public int MaskHeight;
 readonly Dictionary<string,Bitmap> ui=new Dictionary<string,Bitmap>();
 readonly List<Bitmap> frames=new List<Bitmap>();
 readonly List<int> ends=new List<int>();
 PetAsset asset;
 readonly Dictionary<string,string> hd=new Dictionary<string,string>();
 readonly Dictionary<Bitmap,Tuple<string,int>> hdFrames=new Dictionary<Bitmap,Tuple<string,int>>();
 readonly Dictionary<string,FrameAlignment> alignment=new Dictionary<string,FrameAlignment>();
 public bool AlignmentEnabled=true;
 Image hdSource;string hdPath;int hdIndex=-1;
 public bool HighDefinition {get;private set;}
 public void EnableHighDefinition(){
  string folder=Path.GetFullPath(Path.Combine(Root,"..","预览"));
  var map=new JavaScriptSerializer().Deserialize<Dictionary<string,string>>(File.ReadAllText(Path.Combine(folder,"windows-hd.json")));
  foreach(var pair in map){string path=Path.Combine(folder,pair.Value);if(!File.Exists(path))throw new FileNotFoundException("缺少高清素材",path);hd[pair.Key]=path;}
  var calibrated=new JavaScriptSerializer().Deserialize<Dictionary<string,FrameAlignment>>(File.ReadAllText(Path.Combine(folder,"windows-alignment.json")));
  foreach(var pair in calibrated)alignment[hd[pair.Key]]=pair.Value;
  HighDefinition=true;SetActivity(Activity);
 }
 public PetScene(string root) {
  Root=root;Layout=new JavaScriptSerializer().Deserialize<PetLayout>(File.ReadAllText(Path.Combine(root,"layout.json")));
  if(Layout.width!=320||Layout.height!=240)throw new InvalidDataException("Expected 320x240 layout");
  if(Layout.actor_bottom>Layout.clock_y||Layout.safe_top<0)throw new InvalidDataException("Actor overlaps clock");
  Timing=new ActivityTiming(Layout);
  MaskHeight=Layout.safe_top;
  foreach(string p in Directory.GetFiles(Path.Combine(root,"assets","ui"),"*.png"))ui.Add("assets/ui/"+Path.GetFileName(p),new Bitmap(p));
  foreach(var a in Layout.assets)if(Ui(a.title_file)==null||Ui(a.status_file)==null)throw new FileNotFoundException("Missing UI labels: "+a.id);
  SetActivity(Layout.default_activity);
 }
 Bitmap Ui(string path){Bitmap b;return path!=null&&ui.TryGetValue(path,out b)?b:null;}
 public void SetActivity(string id,int loopSeconds=0,bool recoveryBoost=false) {
  RecoveryBoost=recoveryBoost;
  if(hdSource!=null){hdSource.Dispose();hdSource=null;}hdPath=null;hdIndex=-1;hdFrames.Clear();
  foreach(var f in frames.Distinct())f.Dispose();frames.Clear();ends.Clear();DurationMs=0;FrameIndex=0;Activity=id;Error=null;
  asset=Array.Find(Layout.assets,a=>a.id==id);
  try {
   if(asset==null)throw new FileNotFoundException("Unknown resource: "+id);
   if(asset.y<Layout.safe_top || asset.y+asset.height*asset.zoom/256.0>Layout.actor_bottom)throw new InvalidDataException("Resource outside actor region");
   string[] paths=String.IsNullOrEmpty(asset.loop_file)?new[]{asset.file}:new[]{asset.file,asset.loop_file,asset.outro_file};
   foreach(string path in paths){
   int baseFrame=frames.Count,baseTime=DurationMs;
   using(var source=Image.FromFile(Path.Combine(Root,path))) {
    if(source.Width!=asset.width||source.Height!=asset.height)throw new InvalidDataException("Asset dimensions mismatch");
    int count=asset.kind=="gif"?source.GetFrameCount(FrameDimension.Time):1;byte[] delays=null;
    if(HighDefinition&&(!alignment.ContainsKey(hd[path])||alignment[hd[path]].frames.Length!=count))throw new InvalidDataException("动画校准帧数不匹配："+path);
    if(count>1)delays=source.GetPropertyItem(0x5100).Value;
    for(int i=0;i<count;i++) {
     if(count>1)source.SelectActiveFrame(FrameDimension.Time,i);
     var bitmap=new Bitmap(source.Width,source.Height,PixelFormat.Format32bppPArgb);
     using(var g=Graphics.FromImage(bitmap))g.DrawImage(source,new Rectangle(0,0,source.Width,source.Height),0,0,source.Width,source.Height,GraphicsUnit.Pixel);
     frames.Add(bitmap);DurationMs+=delays==null?1000:Math.Max(20,(int)BitConverter.ToUInt32(delays,i*4)*10);ends.Add(DurationMs);
     if(HighDefinition)hdFrames[bitmap]=Tuple.Create(hd[path],i);
    }
   }
   if(path==asset.loop_file){
    int loopFrames=frames.Count-baseFrame,loopTime=DurationMs-baseTime;
    int repeats=Layout.LoopCount(asset,loopSeconds>0?loopSeconds:Timing.Get(asset.id));
    for(int repeat=1;repeat<repeats;repeat++){
     for(int i=0;i<loopFrames;i++){frames.Add(frames[baseFrame+i]);ends.Add(ends[baseFrame+i]+repeat*loopTime);}
    }
    DurationMs=baseTime+repeats*loopTime;
   }
   }
  } catch(Exception e) {
   foreach(var f in frames.Distinct())f.Dispose();frames.Clear();ends.Clear();DurationMs=0;Error=e.Message;
  }
 }
 void DrawUi(Graphics g,string path,int x,int y){var b=Ui(path);if(b!=null)g.DrawImage(b,new Rectangle(x,y,b.Width,b.Height),0,0,b.Width,b.Height,GraphicsUnit.Pixel);}
 public void Render(Graphics g,long elapsed,DateTime clock) {
  g.Clear(BlackBackground?Color.Black:Color.Transparent);
  g.InterpolationMode=InterpolationMode.HighQualityBicubic;g.PixelOffsetMode=PixelOffsetMode.HighQuality;
  if(frames.Count>0) {
   int local=String.IsNullOrEmpty(asset.return_activity)?(int)(Math.Max(0,elapsed)%DurationMs):(int)Math.Min(DurationMs-1,Math.Max(0,elapsed));FrameIndex=0;
   while(FrameIndex<ends.Count-1 && local>=ends[FrameIndex])FrameIndex++;
   var saved=g.Save();g.SetClip(new Rectangle(0,Layout.safe_top,320,Layout.actor_bottom-Layout.safe_top));
   Image picture=frames[FrameIndex];
   if(HighDefinition){
    var frame=hdFrames[frames[FrameIndex]];
    if(hdPath!=frame.Item1){if(hdSource!=null)hdSource.Dispose();hdSource=Image.FromFile(frame.Item1);hdPath=frame.Item1;hdIndex=-1;}
    if(hdIndex!=frame.Item2){hdSource.SelectActiveFrame(FrameDimension.Time,frame.Item2);hdIndex=frame.Item2;}picture=hdSource;
   }
   float w=asset.width*asset.zoom/256f,h=asset.height*asset.zoom/256f;
   var destination=new RectangleF(asset.x,asset.y,w,h);
   if(HighDefinition&&AlignmentEnabled){
    var correction=alignment[hdPath].frames[hdIndex];
    destination=new RectangleF(asset.x+correction[1]*w/picture.Width,asset.y+correction[2]*h/picture.Height,w*correction[0],h*correction[0]);
   }
   g.DrawImage(picture,destination,new RectangleF(0,0,picture.Width,picture.Height),GraphicsUnit.Pixel);
   g.Restore(saved);
  }
  if(MaskEnabled)using(var brush=new SolidBrush(Color.FromArgb(225,30,36,45)))g.FillRectangle(brush,0,0,320,Math.Max(0,Math.Min(96,MaskHeight)));
  // Head-level needs and bottom clock/date/work countdown.
  DrawText(g,clock.ToString("HH:mm:ss"),"Consolas",22,110,184);
  if(ShowNeeds){
  DrawMeter(g,"饱食",Needs.Satiety.ToString("0")+"/100",Needs.Satiety/100,12,3,Color.FromArgb(255,197,113));
  DrawMeter(g,"心情",Needs.Mood.ToString("0")+"/100",Needs.Mood/100,166,3,Color.FromArgb(250,150,183));
  DrawMeter(g,"活力",Needs.Energy.ToString("0")+"/100",Needs.Energy/100,12,25,Color.FromArgb(116,218,189));
  DrawMeter(g,"等级 Lv."+Needs.Level,Math.Floor(Needs.Experience)+"/"+Needs.Required,Needs.Experience/Needs.Required,166,25,Color.FromArgb(147,184,255));
  }
  DrawCenteredText(g,clock.ToString("dddd · M月d日",System.Globalization.CultureInfo.GetCultureInfo("zh-CN")),12,207);
  DrawCenteredText(g,Countdown(clock,WorkStart,WorkEnd),12,222);
  DrawWeather(g,0,7);DrawWeather(g,1,231);
  // Preview canvas boundary; a one-physical-pixel outline, with transparent interior.
  if(DrawBorder)using(var border=new SolidBrush(Color.FromArgb(190,139,182,198))) {
   g.FillRectangle(border,0,0,320,1);g.FillRectangle(border,0,239,320,1);
   g.FillRectangle(border,0,1,1,238);g.FillRectangle(border,319,1,1,238);
  }
 }
 void DrawWeather(Graphics g,int ahead,float x){
  var saved=g.Save();g.SetClip(new RectangleF(x,184,82,54));
  var day=Weather==null?null:Weather.Day(ahead,DateTime.UtcNow);
  DrawText(g,ahead==0?"今日天气":"明日天气","Microsoft YaHei UI",10,x+10,184);
  if(day==null){DrawText(g,"天气待更新","Microsoft YaHei UI",10,x+8,204);DrawText(g,"-- / --°C","Consolas",11,x+12,222);}
  else{
   DrawWeatherIcon(g,x+9,211,day.code);
   DrawText(g,day.text,"Microsoft YaHei UI",10,x+22,204);
   DrawText(g,day.low.ToString("0")+"~"+day.high.ToString("0")+"°C","Consolas",12,x+11,221);
  }
  g.Restore(saved);
 }
 static void DrawWeatherIcon(Graphics g,float x,float y,int code){
  var prior=g.SmoothingMode;g.SmoothingMode=SmoothingMode.AntiAlias;
  using(var sun=new SolidBrush(Color.FromArgb(255,204,99)))using(var cloud=new SolidBrush(Color.FromArgb(192,220,238)))using(var rain=new Pen(Color.FromArgb(108,198,248),1.2f)){
   if(code<=2)g.FillEllipse(sun,x-6,y-7,11,11);
   if(code>0){g.FillEllipse(cloud,x-7,y-1,10,6);g.FillEllipse(cloud,x-2,y-5,9,10);g.FillRectangle(cloud,x-4,y+1,11,4);}
   if(code>=51){g.DrawLine(rain,x-4,y+7,x-5,y+10);g.DrawLine(rain,x+2,y+7,x+1,y+10);}
  }
  g.SmoothingMode=prior;
 }
 public static string Countdown(DateTime now,TimeSpan start,TimeSpan end){
  bool beforeStart=now.TimeOfDay<start;
  double delta=(now.Date.Add(beforeStart?start:end)-now).TotalMinutes;
  if(delta<=0)return "已到下班时间";
  int minutes=(int)Math.Ceiling(delta);return (beforeStart?"距上班 ":"距下班 ")+(minutes/60)+"小时"+(minutes%60)+"分";
 }
 static void DrawCenteredText(Graphics g,string text,float size,float y){
  using(var font=new Font("Microsoft YaHei UI",size,GraphicsUnit.Pixel)){
   float width=g.MeasureString(text,font,1000,StringFormat.GenericTypographic).Width;
   DrawText(g,text,"Microsoft YaHei UI",size,(320-width)/2,y);
  }
 }
 public void AccrueNeeds(long from,long to){
  if(to<=from)return;
  double active=0;
  if(Error==null&&asset!=null&&!String.IsNullOrEmpty(asset.loop_file))active=Math.Max(0,Math.Min(to,DurationMs-asset.outro_duration_ms)-Math.Max(from,asset.duration_ms))/1000.0;
  Needs.Advance(Activity,(to-from)/1000.0,active,RecoveryBoost?2:1);
 }
 static void DrawMeter(Graphics g,string label,string value,double fraction,float x,float y,Color color){
  DrawText(g,label,"Microsoft YaHei UI",10,x,y);
  DrawText(g,value,"Consolas",10,x+91,y);
  using(var back=new SolidBrush(Color.FromArgb(190,28,43,62)))g.FillRectangle(back,x,y+15,142,4);
  using(var fill=new SolidBrush(color))g.FillRectangle(fill,x,y+15,(float)(142*Math.Max(0,Math.Min(1,fraction))),4);
 }
 public void Snapshot(string path,long elapsed,DateTime clock){using(var b=new Bitmap(320,240,PixelFormat.Format32bppArgb)){using(var g=Graphics.FromImage(b))Render(g,elapsed,clock);b.Save(path,ImageFormat.Png);}}
 static void DrawText(Graphics g,string text,string family,float size,float x,float y){
  using(var path=new GraphicsPath())using(var font=new FontFamily(family))using(var pen=new Pen(Color.FromArgb(210,15,29,47),1))using(var ink=new SolidBrush(Color.FromArgb(244,251,255))){
   path.AddString(text,font,(int)FontStyle.Regular,size,new PointF(x,y),StringFormat.GenericTypographic);
   var previous=g.SmoothingMode;g.SmoothingMode=SmoothingMode.AntiAlias;pen.LineJoin=LineJoin.Round;g.DrawPath(pen,path);g.FillPath(ink,path);g.SmoothingMode=previous;
  }
 }
 public void Dispose(){if(hdSource!=null)hdSource.Dispose();foreach(var f in frames.Distinct())f.Dispose();foreach(var b in ui.Values)b.Dispose();}
 static bool RegionEqual(Bitmap a,Bitmap b,Rectangle r){for(int y=r.Top;y<r.Bottom;y++)for(int x=r.Left;x<r.Right;x++)if(a.GetPixel(x,y)!=b.GetPixel(x,y))return false;return true;}
 static bool ClockInkEqual(Bitmap a,Bitmap b){
  int checkedPixels=0;
  for(int y=184;y<206;y++)for(int x=110;x<216;x++){
   var c=a.GetPixel(x,y);if(c.A==255&&c.R>230&&c.G>230&&c.B>230){checkedPixels++;if(c!=b.GetPixel(x,y))return false;}
  }
  return checkedPixels>30;
 }
 public static void VerifyNeedsTiming(string root){
  var day=new DateTime(2026,10,18);var start=TimeSpan.FromHours(9);var end=TimeSpan.FromHours(18);
  if(Countdown(day,start,end)!="距上班 9小时0分"||Countdown(day.AddHours(9),start,end)!="距下班 9小时0分"||Countdown(day.AddHours(18),start,end)!="已到下班时间"||Countdown(day.AddDays(1),start,end)!="距上班 9小时0分"||Countdown(day.AddHours(9).AddSeconds(-1),start,end)!="距上班 0小时1分")throw new Exception("Work countdown boundaries");

  using(var s=new PetScene(root)){
   s.SetActivity("eat");var a=Array.Find(s.Layout.assets,v=>v.id=="eat");
   s.AccrueNeeds(0,a.duration_ms);if(s.Needs.Satiety>=80)throw new Exception("Food awarded before eating loop");
   s.Needs=new PetNeeds();s.AccrueNeeds(a.duration_ms-500,a.duration_ms+500);
   if(Math.Abs(s.Needs.Satiety-(80+.5-1.0/120))>.00001)throw new Exception("Loop overlap accounting");
   s.Needs=new PetNeeds();s.AccrueNeeds(s.DurationMs-a.outro_duration_ms,s.DurationMs);
   if(s.Needs.Satiety>=80)throw new Exception("Food awarded during outro");
  }
 }
 public static void VerifyHD(string root,string output){
  Directory.CreateDirectory(output);
  using(var s=new PetScene(root)){
   s.EnableHighDefinition();s.DrawBorder=false;
   var report=new List<string>();
   foreach(var a in s.Layout.assets){
    if(!String.IsNullOrEmpty(a.loop_file))s.Timing.Set(a.id,5);s.SetActivity(a.id);if(s.Error!=null)throw new Exception(s.Error);
    using(var bitmap=new Bitmap(1280,960,PixelFormat.Format32bppPArgb))using(var g=Graphics.FromImage(bitmap)){
     g.ScaleTransform(4,4);
     var timer=System.Diagnostics.Stopwatch.StartNew();
     for(int i=0;i<32;i++)s.Render(g,i*32,new DateTime(2026,10,18,12,34,0));
     report.Add(a.id+": 32 HD renders "+timer.ElapsedMilliseconds+" ms");
     foreach(long at in new long[]{0,a.duration_ms+1000,s.DurationMs-1}){
      s.Render(g,at,new DateTime(2026,10,18,12,34,0));
      bitmap.Save(Path.Combine(output,a.id+"-at-"+at+".png"),ImageFormat.Png);
     }
     if(bitmap.GetPixel(1,1).A!=0)throw new Exception("HD transparency failed");
     bitmap.Save(Path.Combine(output,a.id+"-hd.png"),ImageFormat.Png);
    }
   }
   foreach(int percent in new[]{200,300,400})using(var bitmap=new Bitmap(320*percent/100,240*percent/100,PixelFormat.Format32bppPArgb))using(var g=Graphics.FromImage(bitmap)){
    s.SetActivity("idle");g.ScaleTransform(percent/100f,percent/100f);s.Render(g,0,new DateTime(2026,10,18,12,34,0));bitmap.Save(Path.Combine(output,"idle-"+percent+".png"),ImageFormat.Png);
   }
   File.WriteAllLines(Path.Combine(output,"高清验证.txt"),report);
  }
 }
 public static string Verify(string root,string output) {
  Directory.CreateDirectory(output);var clock=new DateTime(2026,10,16,12,34,56);
  using(var s=new PetScene(root)) {
   if(s.Error!=null)throw new Exception(s.Error);
   var idle=Array.Find(s.Layout.assets,a=>a.id=="idle");
   if(s.FrameCount!=idle.frame_count||s.DurationMs!=idle.duration_ms)throw new Exception("Idle timing incorrect");
   s.Snapshot(Path.Combine(output,"idle.png"),0,clock);
   s.Snapshot(Path.Combine(output,"idle-blink.png"),1760,clock);
   using(var a=new Bitmap(Path.Combine(output,"idle.png")))using(var b=new Bitmap(Path.Combine(output,"idle-blink.png")))
    if(RegionEqual(a,b,new Rectangle(0,32,320,152)))throw new Exception("Idle is static");
   s.SetActivity("sleep");
   if(s.Error!=null||s.FrameCount<2)throw new Exception("GIF failed: "+s.Error);
   int count=s.FrameCount, duration=s.DurationMs;
   s.Snapshot(Path.Combine(output,"sleep-0.png"),0,clock);
   s.Snapshot(Path.Combine(output,"sleep-1.png"),350,clock);
   using(var a=new Bitmap(Path.Combine(output,"sleep-0.png")))using(var b=new Bitmap(Path.Combine(output,"sleep-1.png")))
    if(RegionEqual(a,b,new Rectangle(0,32,320,152)))throw new Exception("GIF does not advance");
   s.MaskEnabled=true;s.MaskHeight=96;s.Snapshot(Path.Combine(output,"mask.png"),700,clock);
   s.SetActivity("missing-test");if(s.Error==null)throw new Exception("Missing asset not reported");
   s.Snapshot(Path.Combine(output,"missing.png"),0,clock);
   using(var reference=new Bitmap(Path.Combine(output,"idle.png"))) {
    foreach(var filename in new[]{"sleep-0.png","sleep-1.png","mask.png","missing.png"})
     using(var current=new Bitmap(Path.Combine(output,filename)))
      if(!ClockInkEqual(reference,current))throw new Exception("Clock lost during "+filename);
    if(reference.GetPixel(1,1).A!=0)throw new Exception("Background is opaque");
   }
   s.SetActivity("idle");s.MaskEnabled=false;s.Snapshot(Path.Combine(output,"minute-change.png"),0,clock.AddMinutes(1));
   using(var a=new Bitmap(Path.Combine(output,"idle.png")))using(var b=new Bitmap(Path.Combine(output,"minute-change.png")))
    if(RegionEqual(a,b,new Rectangle(110,184,106,22)))throw new Exception("Clock frozen");
   var scheduler=new ActivityScheduler(s.Layout,12345,s.Timing);scheduler.Reset(0);
   string activity="idle";long now=0;var seen=new HashSet<string>();seen.Add(activity);
   for(int i=0;i<100;i++){
    long delay=scheduler.Due-now;
    var playing=Array.Find(s.Layout.assets,a=>a.id==activity);
    bool timed=!String.IsNullOrEmpty(playing.loop_file);
    if(timed?delay!=s.Layout.ActivityDuration(playing,s.Timing.Get(activity)):(delay<5*playing.duration_ms||delay>10*playing.duration_ms||delay%playing.duration_ms!=0))throw new Exception("Invalid automatic dwell");
    if(scheduler.Next(activity,scheduler.Due-1)!=null)throw new Exception("Early activity switch");
    now=scheduler.Due;string next=scheduler.Next(activity,now);
    if(next==null||next==activity)throw new Exception("Repeated activity");activity=next;seen.Add(next);
   }
   if(seen.Count!=s.Layout.assets.Length)throw new Exception("Unreachable activity");
   scheduler.Automatic=false;scheduler.Reset(now,"idle");if(scheduler.Next("idle",now+120000)!=null)throw new Exception("Manual override lost");
   foreach(var item in s.Layout.assets){
    s.SetActivity(item.id);if(s.Error!=null||s.FrameCount!=s.Layout.ActivityFrames(item,s.Timing.Get(item.id))||s.DurationMs!=s.Layout.ActivityDuration(item,s.Timing.Get(item.id)))throw new Exception("Bad activity: "+item.id);
    s.Snapshot(Path.Combine(output,item.id+"-activity.png"),0,clock);
    s.Snapshot(Path.Combine(output,item.id+"-motion.png"),1000,clock);
    using(var a=new Bitmap(Path.Combine(output,item.id+"-activity.png")))using(var b=new Bitmap(Path.Combine(output,item.id+"-motion.png")))
     if(RegionEqual(a,b,new Rectangle(0,32,320,152)))throw new Exception("Static activity: "+item.id);
   }
   scheduler.Reset(0,"eat");
   long mealEnd=scheduler.Due;
   if(scheduler.Next("eat",mealEnd-1)!=null||scheduler.Next("eat",mealEnd)!="idle")throw new Exception("Meal completion failed");
   foreach(var timed in s.Layout.assets){
    if(String.IsNullOrEmpty(timed.loop_file))continue;
    foreach(int seconds in new[]{5,30,95,600}){
     scheduler.Timing.Set(timed.id,seconds);scheduler.Reset(100,timed.id);long end=scheduler.Due;
     scheduler.Timing.Set(timed.id,5);
     if(scheduler.Next(timed.id,end-1)!=null||scheduler.Next(timed.id,end)!="idle")throw new Exception("Active timing changed or cut short");
    }
    s.Timing.Set(timed.id,30);s.SetActivity(timed.id);
    s.Snapshot(Path.Combine(output,timed.id+"-loop.png"),timed.duration_ms+1000,clock);
    s.Snapshot(Path.Combine(output,timed.id+"-end.png"),s.DurationMs+1000,clock);
    if(s.FrameIndex!=s.FrameCount-1)throw new Exception("Sequence unexpectedly looped");
   }
   string settingsPath=Path.Combine(output,"settings-test.json");
   try{
    File.WriteAllText(settingsPath,"45");var settings=new ActivityTiming(s.Layout);settings.Load(settingsPath);
    if(settings.Get("eat")!=45)throw new Exception("Legacy setting migration failed");
    if(Array.Exists(s.Layout.assets,a=>a.id=="sleep"&&!String.IsNullOrEmpty(a.loop_file))){
     settings.Set("sleep",95);settings.Set("read",20);settings.Set("game",50);settings.Set("pet",75);settings.Set("laser",40);
     settings.Save(settingsPath);var loaded=new ActivityTiming(s.Layout);loaded.Load(settingsPath);
     if(loaded.Get("eat")!=45||loaded.Get("sleep")!=95||loaded.Get("read")!=20||loaded.Get("game")!=50||loaded.Get("pet")!=75||loaded.Get("laser")!=40)throw new Exception("Activity settings not independent/persistent");
    }
   }finally{File.Delete(settingsPath);}
   for(int i=0;i<20;i++){s.SetActivity(i%2==0?"idle":"read");if(s.Error!=null)throw new Exception(s.Error);}
   return "PASS: shared layout 320x240; GIF "+count+" frames / "+duration+"ms; frame advance; clock persists through switch, mask, missing asset; minute rollover; transparency; 20 reloads; seven animated activities; 100 automatic switches; manual override.";
  }
 }
}

// A running activity is never interrupted by automatic needs selection.
public sealed class ActivityScheduler {
 readonly PetLayout layout;long seed,idleCheck;
 public long Due {get;private set;}
 public bool Automatic=true;
 public PetNeeds Needs;
 public int PlannedSeconds {get;private set;}
 public string Reason {get;private set;}
 public readonly ActivityTiming Timing;
 public ActivityScheduler(PetLayout l,int initialSeed,ActivityTiming timing=null){layout=l;Timing=timing??new ActivityTiming(l);seed=Math.Max(1,initialSeed%2147483647);}
 int Pick(int count){seed=seed*48271%2147483647;return (int)(seed%count);}
 public void PrepareActivity(string id){if(id=="eat")layout.SelectMeal(Pick(2147483647));}
 public void Delay(long ms){Due+=ms;idleCheck+=ms;}
 public void ClearPlan(){PlannedSeconds=0;Reason=null;}
 public void Reset(long now,string current=null){
  current=current??layout.default_activity;
  var a=Array.Find(layout.assets,item=>item.id==current);
  idleCheck=now+(a==null?layout.loop_ms:a.duration_ms);
  if(a!=null&&!String.IsNullOrEmpty(a.return_activity)){Due=now+layout.ActivityDuration(a,PlannedSeconds>0?PlannedSeconds:Timing.Get(a.id));return;}
  Due=now+(layout.auto_min_cycles+Pick(layout.auto_max_cycles-layout.auto_min_cycles+1))*(a==null?layout.loop_ms:a.duration_ms);
 }
 public static string Urgent(PetNeeds n){
  string id=null;double urgency=1;
  if(n.Satiety<30){urgency=n.Satiety/30;id="eat";}
  if(n.Energy<25&&n.Energy/25<urgency){urgency=n.Energy/25;id="sleep";}
  if(n.Mood<35&&n.Mood/35<urgency)id="play";
  return id;
 }
 public static int RecoverySeconds(PetAsset a,PetNeeds n){
  double value,target,decay,gain;
  if(a.id=="eat"){value=n.Satiety;target=80;decay=1.0/120;gain=1;}
  else if(a.id=="sleep"){value=n.Energy;target=85;decay=1.0/150;gain=.8;}
  else{value=n.Mood;target=80;decay=1.0/200;gain=.8;}
  // Include preparation/cleanup consumption, and round upward to a full loop later.
  double needed=target-value+decay*(a.duration_ms+a.outro_duration_ms)/1000.0;
  return Math.Max(5,(int)Math.Ceiling(needed/(gain*2-(a.id=="sleep"?0:decay))));
 }
 string BeginNeed(string need,long now){
  string id=need=="play"?new[]{"game","pet","laser"}[Pick(3)]:need;
  PrepareActivity(id);
  var a=Array.Find(layout.assets,item=>item.id==id);
  PlannedSeconds=RecoverySeconds(a,Needs);
  Reason=need=="eat"?"饱食偏低，自动吃饭至80":need=="sleep"?"活力偏低，自动睡觉至85":"心情偏低，自动玩耍至80";
  Reset(now,id);return id;
 }
 public string Next(string current,long now){
  var a=Array.Find(layout.assets,item=>item.id==current);
  bool completeActivity=a!=null&&!String.IsNullOrEmpty(a.return_activity);
  if(!completeActivity&&Automatic&&Needs!=null&&now>=idleCheck){
   long cycle=a==null?layout.loop_ms:a.duration_ms;idleCheck+=((now-idleCheck)/cycle+1)*cycle;
   string need=Urgent(Needs);if(need!=null)return BeginNeed(need,now);
  }
  if(now<Due)return null;
  if(completeActivity){ClearPlan();Reset(now,a.return_activity);return a.return_activity;}
  if(!Automatic)return null;
  ClearPlan();
  var candidates=Array.FindAll(layout.assets,item=>item.id!=current&&(Needs==null||(item.id!="eat"&&item.id!="sleep")));
  if(candidates.Length==0)return null;
  string selected=candidates[Pick(candidates.Length)].id;PrepareActivity(selected);Reset(now,selected);return selected;
 }
}
