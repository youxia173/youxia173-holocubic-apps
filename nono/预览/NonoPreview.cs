using System;
using System.IO;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using System.Windows.Forms;
using System.Collections.Generic;
using System.Web.Script.Serialization;

public sealed class NonoPreview : Form {
 [DllImport("user32.dll")]public static extern bool SetProcessDPIAware();
 [StructLayout(LayoutKind.Sequential)]struct P{public int X,Y;public P(int x,int y){X=x;Y=y;}}
 [StructLayout(LayoutKind.Sequential)]struct S{public int W,H;public S(int w,int h){W=w;H=h;}}
 [StructLayout(LayoutKind.Sequential,Pack=1)]struct B{public byte Op,Flags,Alpha,Format;}
 [DllImport("user32.dll")]static extern bool ShowWindow(IntPtr h,int c);
 [StructLayout(LayoutKind.Sequential)]struct Rect{public int Left,Top,Right,Bottom;}
 [DllImport("user32.dll")]static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")]static extern bool GetClientRect(IntPtr h,out Rect r);
 [DllImport("user32.dll")]static extern bool ClientToScreen(IntPtr h,ref P p);
 [DllImport("user32.dll")]static extern bool IsIconic(IntPtr h);
 [DllImport("user32.dll")]static extern bool SetWindowPos(IntPtr h,IntPtr after,int x,int y,int w,int height,uint flags);
 [DllImport("user32.dll")]static extern int GetWindowLong(IntPtr h,int index);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)]static extern int GetClassName(IntPtr h,System.Text.StringBuilder name,int count);
 [DllImport("user32.dll")]static extern IntPtr GetDC(IntPtr h);
 [DllImport("user32.dll")]static extern int ReleaseDC(IntPtr h,IntPtr dc);
 [DllImport("gdi32.dll")]static extern IntPtr CreateCompatibleDC(IntPtr dc);
 [DllImport("gdi32.dll")]static extern IntPtr SelectObject(IntPtr dc,IntPtr o);
 [DllImport("gdi32.dll")]static extern bool DeleteObject(IntPtr o);
 [DllImport("gdi32.dll")]static extern bool DeleteDC(IntPtr dc);
 [DllImport("user32.dll",SetLastError=true)]static extern bool UpdateLayeredWindow(IntPtr h,IntPtr dc,ref P p,ref S s,IntPtr src,ref P origin,int color,ref B blend,int flags);
 readonly PetScene scene;
 readonly ActivityScheduler scheduler;
 Bitmap canvas=new Bitmap(640,480,PixelFormat.Format32bppPArgb);
 readonly Timer timer=new Timer();
 readonly System.Diagnostics.Stopwatch elapsed=System.Diagnostics.Stopwatch.StartNew();
 public int DisplayPercent {get;private set;}
 bool dragging,moved;
 Point dragStart,windowStart;
 long activityStart;
 string preferences;
 SettingsServer web;
 NotifyIcon tray;
 ContextMenuStrip trayMenu;
 bool resourcesDisposed;
 bool requestedTopMost=true,fullscreenUnpin=true;
 long nextFullscreenCheck;
 string windowPreferences;
 readonly NeedsVisibility needsVisibility=new NeedsVisibility();
 WeatherService weather;string weatherCity="上海长宁区";
 string needsPath;long needsTick,needsSaveTick;
 public NonoPreview(string root) {
  scene=new PetScene(root);scene.EnableHighDefinition();scene.DrawBorder=false;DisplayPercent=200;
  scheduler=new ActivityScheduler(scene.Layout,Environment.TickCount & int.MaxValue,scene.Timing);scheduler.Reset(0);
  preferences=Path.GetFullPath(Path.Combine(root,"..","预览","用户设置.txt"));
  scene.Timing.Load(preferences);
  weather=new WeatherService(Path.Combine(Path.GetDirectoryName(preferences),"天气缓存.json"));
  needsPath=Path.Combine(Path.GetDirectoryName(preferences),"诺诺属性.json");scene.Needs=PetNeeds.Load(needsPath);scheduler.Needs=scene.Needs;
  Text="桌宠诺诺 · Windows 高清版 · 640×480";
  string iconPath=Path.GetFullPath(Path.Combine(root,"..","预览","诺诺.ico"));
  if(File.Exists(iconPath)){Icon=new Icon(iconPath);}
  AutoScaleMode=AutoScaleMode.None;FormBorderStyle=FormBorderStyle.None;ClientSize=new Size(640,480);
  StartPosition=FormStartPosition.CenterScreen;KeyPreview=true;TopMost=true;ShowInTaskbar=false;
  windowPreferences=Path.Combine(Path.GetDirectoryName(preferences),"窗口设置.json");
  if(File.Exists(windowPreferences)){try{ApplyWeb(new JavaScriptSerializer().Deserialize<Dictionary<string,object>>(File.ReadAllText(windowPreferences)));}catch(Exception){}}
  var handle=Handle;
  web=new SettingsServer(this,root);
  File.WriteAllText(Path.Combine(Path.GetDirectoryName(preferences),"网页设置地址.txt"),web.Url);
  var menu=new ContextMenuStrip();
  menu.Items.Add("打开网页设置",null,delegate{OpenSettings();});
  var pin=new ToolStripMenuItem("置顶"){CheckOnClick=true,Checked=requestedTopMost};pin.CheckedChanged+=delegate{if(pin.Checked!=requestedTopMost)ApplyWeb(new Dictionary<string,object>{{"topmost",pin.Checked}});};menu.Opening+=delegate{pin.Checked=requestedTopMost;};menu.Items.Add(pin);
  menu.Items.Add("退出",null,delegate{Close();});ContextMenuStrip=menu;
  trayMenu=new ContextMenuStrip();
  trayMenu.Items.Add("打开设置网页",null,delegate{OpenSettings();});
  trayMenu.Items.Add("退出",null,delegate{Close();});
  tray=new NotifyIcon{Icon=Icon,Text="桌宠诺诺",ContextMenuStrip=trayMenu,Visible=true};
  activityStart=elapsed.ElapsedMilliseconds;scheduler.Reset(activityStart,scene.Activity);
  needsTick=elapsed.ElapsedMilliseconds;needsSaveTick=needsTick;needsVisibility.Observe(scene.Needs,needsTick);scene.ShowNeeds=needsVisibility.Visible(needsTick);
  bool first=true;
  timer.Interval=15;timer.Tick+=delegate{
   long now=elapsed.ElapsedMilliseconds;
   if(now>=nextFullscreenCheck){UpdateTopMost();nextFullscreenCheck=now+500;}
   UpdateNeeds(now);weather.Poll(weatherCity);scene.Weather=weather.Data;
   string next=scheduler.Next(scene.Activity,now);
   if(next!=null){scene.SetActivity(next,scheduler.PlannedSeconds,scheduler.PlannedSeconds>0);activityStart=elapsed.ElapsedMilliseconds;scheduler.Delay(activityStart-now);}
   Present();
   if(first){first=false;ShowWindow(Handle,5);}
  };timer.Start();
 }
 void UpdateTopMost(){
  bool suppress=false;
  if(fullscreenUnpin&&requestedTopMost){
   IntPtr foreground=GetForegroundWindow();
   if(foreground!=IntPtr.Zero&&foreground!=Handle&&!IsIconic(foreground)){
    var name=new System.Text.StringBuilder(256);GetClassName(foreground,name,name.Capacity);
    string kind=name.ToString();
    if(kind!="Progman"&&kind!="WorkerW"&&kind!="Shell_TrayWnd"&&kind!="Shell_SecondaryTrayWnd"){
     Rect client;var origin=new P(0,0);
     if(GetClientRect(foreground,out client)&&ClientToScreen(foreground,ref origin)){
      var screen=Screen.FromHandle(foreground).Bounds;
      // Client area must cover the display, excluding ordinary maximized windows with title bars.
      suppress=Bounds.IntersectsWith(screen)&&origin.X<=screen.Left+2&&origin.Y<=screen.Top+2
       &&origin.X+client.Right>=screen.Right-2&&origin.Y+client.Bottom>=screen.Bottom-2;
     }
    }
   }
  }
  bool desired=requestedTopMost&&!suppress;
  bool actual=(GetWindowLong(Handle,-20)&8)!=0;
  // Do not activate the pet while changing its z-order: the fullscreen app keeps focus.
  if(actual!=desired)SetWindowPos(Handle,new IntPtr(desired?-1:-2),0,0,0,0,0x13);
 }
 void UpdateNeeds(long now){
  // Keep playback and recovery accounting on the same clock after suspension.
  if(needsTick>0&&now-needsTick>5000){long pause=now-needsTick-5000;activityStart+=pause;scheduler.Delay(pause);}
  long from=Math.Max(needsTick,now-5000);
  scene.AccrueNeeds(Math.Max(0,from-activityStart),Math.Max(0,now-activityStart));needsTick=now;
  needsVisibility.Observe(scene.Needs,now);scene.ShowNeeds=needsVisibility.Visible(now);
  if(now-needsSaveTick>=30000){SaveNeeds();needsSaveTick=now;}
 }
 void SaveNeeds(){if(needsPath!=null)try{scene.Needs.Save(needsPath);}catch(IOException){}catch(UnauthorizedAccessException){}}
 public void PlayActivity(string id){
  if(!Array.Exists(scene.Layout.assets,a=>a.id==id))throw new ArgumentException("Unknown activity");
  UpdateNeeds(elapsed.ElapsedMilliseconds);
  scheduler.ClearPlan();scheduler.PrepareActivity(id);scene.SetActivity(id);activityStart=elapsed.ElapsedMilliseconds;scheduler.Reset(activityStart,id);
 }
 public void OpenSettings(){System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo(web.Url){UseShellExecute=true});}
 public object WebState(){
  var seconds=new Dictionary<string,int>();foreach(var a in scene.Layout.assets)if(!String.IsNullOrEmpty(a.loop_file))seconds[a.id]=scene.Timing.Get(a.id);
  return new Dictionary<string,object>{{"ok",true},{"platform","windows"},{"version","1.0.3"},{"activity",scene.Activity},{"mealVariant",scene.MealVariant},{"auto",scheduler.Automatic},{"mask",scene.MaskEnabled},{"seconds",seconds},{"scale",DisplayPercent},{"topmost",requestedTopMost},{"fullscreenUnpin",fullscreenUnpin},{"black",scene.BlackBackground},{"error",scene.Error},{"needs",scene.Needs},{"activityReason",scheduler.Reason},{"recoverySeconds",scheduler.PlannedSeconds},{"recoveryBoost",scene.RecoveryBoost},{"needsDisplay",needsVisibility.Mode},{"needsDisplaySeconds",needsVisibility.Seconds},{"needsVisible",scene.ShowNeeds},{"weatherCity",weatherCity},{"weatherStatus",weather==null?"正在获取天气":weather.Status},{"weather",weather==null?null:weather.Data},{"workStart",scene.WorkStart.ToString(@"hh\:mm")},{"workEnd",scene.WorkEnd.ToString(@"hh\:mm")},{"workCountdown",PetScene.Countdown(DateTime.Now,scene.WorkStart,scene.WorkEnd)}};
 }
 public object ApplyWeb(Dictionary<string,object> p){
  foreach(string key in new[]{"auto","mask","topmost","black","fullscreenUnpin"})if(p.ContainsKey(key)&&!(p[key] is bool))throw new ArgumentException("开关格式错误");
  var seconds=new Dictionary<string,int>();
  if(p.ContainsKey("seconds")){
   var values=p["seconds"] as Dictionary<string,object>;if(values==null)throw new ArgumentException("时长格式错误");
   foreach(var pair in values){if(!(pair.Value is int)||!Array.Exists(scene.Layout.assets,a=>a.id==pair.Key&&!String.IsNullOrEmpty(a.loop_file)))throw new ArgumentException("未知时长设置");int n=(int)pair.Value;if(n<5||n>600)throw new ArgumentException("时长应为5–600整数秒");seconds[pair.Key]=n;}
  }
  int scale=DisplayPercent;if(p.ContainsKey("scale")){if(!(p["scale"] is int))throw new ArgumentException("尺寸格式错误");scale=(int)p["scale"];if(Array.IndexOf(new[]{100,150,200,300,400},scale)<0)throw new ArgumentException("不支持此尺寸");}
  if(p.ContainsKey("activity")&&(!(p["activity"] is string)||!Array.Exists(scene.Layout.assets,a=>a.id==(string)p["activity"])))throw new ArgumentException("未知活动");
  TimeSpan workStart=scene.WorkStart,workEnd=scene.WorkEnd;
  if(p.ContainsKey("workStart")&&(!(p["workStart"] is string)||!TimeSpan.TryParseExact((string)p["workStart"],@"hh\:mm",System.Globalization.CultureInfo.InvariantCulture,out workStart)||workStart.TotalHours>=24))throw new ArgumentException("上班时间格式应为 HH:mm");
  if(p.ContainsKey("workEnd")&&(!(p["workEnd"] is string)||!TimeSpan.TryParseExact((string)p["workEnd"],@"hh\:mm",System.Globalization.CultureInfo.InvariantCulture,out workEnd)||workEnd.TotalHours>=24))throw new ArgumentException("下班时间格式应为 HH:mm");
  if(workStart>=workEnd)throw new ArgumentException("下班时间须晚于上班时间");
  string city=weatherCity;
  if(p.ContainsKey("weatherCity")){if(!(p["weatherCity"] is string)||String.IsNullOrWhiteSpace((string)p["weatherCity"])||((string)p["weatherCity"]).Length>60)throw new ArgumentException("请输入1–60字的天气城市或区县");city=((string)p["weatherCity"]).Trim();}
  string display=needsVisibility.Mode;int displaySeconds=needsVisibility.Seconds;
  if(p.ContainsKey("needsDisplay")){if(!(p["needsDisplay"] is string)||((string)p["needsDisplay"]!="always"&&(string)p["needsDisplay"]!="changed"))throw new ArgumentException("未知的属性显示方式");display=(string)p["needsDisplay"];}
  if(p.ContainsKey("needsDisplaySeconds")){if(!(p["needsDisplaySeconds"] is int)||(int)p["needsDisplaySeconds"]<1||(int)p["needsDisplaySeconds"]>600)throw new ArgumentException("属性显示时长应为1–600整数秒");displaySeconds=(int)p["needsDisplaySeconds"];}
  needsVisibility.Mode=display;needsVisibility.Seconds=displaySeconds;scene.ShowNeeds=needsVisibility.Visible(elapsed.ElapsedMilliseconds);
  weatherCity=city;
  scene.WorkStart=workStart;scene.WorkEnd=workEnd;
  foreach(var pair in seconds)scene.Timing.Set(pair.Key,pair.Value);
  scene.Timing.Save(preferences);
  if(p.ContainsKey("mask"))scene.MaskEnabled=(bool)p["mask"];
  if(p.ContainsKey("black"))scene.BlackBackground=(bool)p["black"];
  if(p.ContainsKey("topmost"))requestedTopMost=(bool)p["topmost"];
  if(p.ContainsKey("fullscreenUnpin"))fullscreenUnpin=(bool)p["fullscreenUnpin"];
  UpdateTopMost();
  SetDisplayScale(scale);
  if(p.ContainsKey("activity")){scheduler.Automatic=false;PlayActivity((string)p["activity"]);}
  else if(p.ContainsKey("auto")&&(bool)p["auto"]!=scheduler.Automatic){scheduler.Automatic=(bool)p["auto"];if(scheduler.Automatic)PlayActivity(scene.Layout.default_activity);}
  var saved=new Dictionary<string,object>{{"needsDisplay",needsVisibility.Mode},{"needsDisplaySeconds",needsVisibility.Seconds},{"weatherCity",weatherCity},{"scale",DisplayPercent},{"topmost",requestedTopMost},{"fullscreenUnpin",fullscreenUnpin},{"black",scene.BlackBackground},{"mask",scene.MaskEnabled},{"auto",scheduler.Automatic},{"workStart",scene.WorkStart.ToString(@"hh\:mm")},{"workEnd",scene.WorkEnd.ToString(@"hh\:mm")}};
  if(windowPreferences!=null)File.WriteAllText(windowPreferences,new JavaScriptSerializer().Serialize(saved));
  return WebState();
 }
 protected override CreateParams CreateParams{get{var p=base.CreateParams;p.ExStyle|=0x80000;return p;}}
 protected override void OnPaintBackground(PaintEventArgs e){}
 protected override void OnPaint(PaintEventArgs e){}
 protected override void OnMouseDown(MouseEventArgs e){base.OnMouseDown(e);if(e.Button==MouseButtons.Left){dragging=true;moved=false;dragStart=Cursor.Position;windowStart=Location;Capture=true;Activate();}}
 protected override void OnMouseMove(MouseEventArgs e){base.OnMouseMove(e);if(dragging){var d=new Size(Cursor.Position.X-dragStart.X,Cursor.Position.Y-dragStart.Y);if(Math.Abs(d.Width)+Math.Abs(d.Height)>4)moved=true;if(moved)Location=windowStart+d;}}
 protected override void OnMouseUp(MouseEventArgs e){base.OnMouseUp(e);if(e.Button==MouseButtons.Left){dragging=false;Capture=false;}}
 protected override void OnKeyDown(KeyEventArgs e){base.OnKeyDown(e);if(e.KeyCode==Keys.Escape)Close();if(e.KeyCode==Keys.F1)OpenSettings();}
 public void SetDisplayScale(int percent){
  if(percent!=100&&percent!=150&&percent!=200&&percent!=300&&percent!=400)throw new ArgumentOutOfRangeException("percent");
  if(percent==DisplayPercent)return;
  var next=new Bitmap(320*percent/100,240*percent/100,PixelFormat.Format32bppPArgb);
  var previous=canvas;canvas=next;DisplayPercent=percent;ClientSize=canvas.Size;previous.Dispose();
  var area=Screen.FromControl(this).WorkingArea;
  Location=new Point(Math.Max(area.Left,Math.Min(Left,area.Right-Width)),Math.Max(area.Top,Math.Min(Top,area.Bottom-Height)));
  Text=String.Format("桌宠诺诺 · Windows 高清版 · {0}×{1} · {2}%",canvas.Width,canvas.Height,percent);
  if(IsHandleCreated)Present();
 }
 void Present(){
  using(var g=Graphics.FromImage(canvas)){
   g.ScaleTransform(DisplayPercent/100f,DisplayPercent/100f);
   scene.Render(g,elapsed.ElapsedMilliseconds-activityStart,DateTime.Now);
   g.ResetTransform();
   // Keep the user's thin outline at one physical pixel at every zoom level.
   using(var border=new SolidBrush(Color.FromArgb(190,139,182,198))){
    g.FillRectangle(border,0,0,canvas.Width,1);g.FillRectangle(border,0,canvas.Height-1,canvas.Width,1);
    g.FillRectangle(border,0,1,1,canvas.Height-2);g.FillRectangle(border,canvas.Width-1,1,1,canvas.Height-2);
   }
  }
  IntPtr dc=GetDC(IntPtr.Zero),mem=IntPtr.Zero,bmp=IntPtr.Zero,old=IntPtr.Zero;
  try{
   mem=CreateCompatibleDC(dc);bmp=canvas.GetHbitmap(Color.FromArgb(0));old=SelectObject(mem,bmp);
   var p=new P(Left,Top);var s=new S(canvas.Width,canvas.Height);var o=new P(0,0);var b=new B{Alpha=255,Format=1};
   if(!UpdateLayeredWindow(Handle,dc,ref p,ref s,mem,ref o,0,ref b,2))throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error());
  }finally{if(old!=IntPtr.Zero)SelectObject(mem,old);if(bmp!=IntPtr.Zero)DeleteObject(bmp);if(mem!=IntPtr.Zero)DeleteDC(mem);if(dc!=IntPtr.Zero)ReleaseDC(IntPtr.Zero,dc);}
 }
 protected override void Dispose(bool d){if(d&&!resourcesDisposed){resourcesDisposed=true;if(tray!=null){tray.Visible=false;tray.Dispose();}if(trayMenu!=null)trayMenu.Dispose();if(weather!=null)weather.Dispose();UpdateNeeds(elapsed.ElapsedMilliseconds);SaveNeeds();if(web!=null)web.Dispose();timer.Stop();timer.Dispose();scene.Dispose();canvas.Dispose();if(ContextMenuStrip!=null)ContextMenuStrip.Dispose();}base.Dispose(d);}
}

