using System;
using System.IO;
using System.Drawing;
using System.Drawing.Imaging;
using System.Drawing.Drawing2D;
public static class BuildAssets {
 static void TextImage(string text,string path,int w,int h,string family,float size,bool centered) {
  using(var b=new Bitmap(w,h,PixelFormat.Format32bppArgb)) using(var g=Graphics.FromImage(b)) using(var p=new GraphicsPath()) {
   g.SmoothingMode=SmoothingMode.AntiAlias;
   using(var font=new FontFamily(family)) {
    var format=(StringFormat)StringFormat.GenericTypographic.Clone();
    if(centered) format.Alignment=StringAlignment.Center;
    p.AddString(text,font,(int)FontStyle.Regular,size,new RectangleF(0,0,w,h),format);
    format.Dispose();
   }
   using(var outline=new Pen(Color.FromArgb(210,15,29,47),2)){outline.LineJoin=LineJoin.Round;g.DrawPath(outline,p);}
   using(var ink=new SolidBrush(Color.FromArgb(244,251,255)))g.FillPath(ink,p);
   b.Save(path,ImageFormat.Png);
  }
 }
 public static void PettingUI(string root) {
  string ui=Path.Combine(root,"代码","assets","ui");
  TextImage("诺诺 · 初始",Path.Combine(ui,"title-pet.png"),170,22,"Microsoft YaHei UI",16,false);
  TextImage("撸猫",Path.Combine(ui,"status-pet.png"),170,20,"Microsoft YaHei UI",12,false);
 }
 public static void LaserUI(string root) {
  string ui=Path.Combine(root,"代码","assets","ui");
  TextImage("诺诺 · 初始",Path.Combine(ui,"title-laser.png"),170,22,"Microsoft YaHei UI",16,false);
  TextImage("激光逗猫",Path.Combine(ui,"status-laser.png"),170,20,"Microsoft YaHei UI",12,false);
 }
 public static void Run(string root) {
  string assets=Path.Combine(root,"代码","assets"),ui=Path.Combine(assets,"ui");
  Directory.CreateDirectory(ui);
  using(var src=new Bitmap(Path.Combine(root,"说明","形象参考","nono-idle-v2.png"))) {
   int l=src.Width,t=src.Height,r=0,b=0;
   for(int y=0;y<src.Height;y++)for(int x=0;x<src.Width;x++)if(src.GetPixel(x,y).A>24){l=Math.Min(l,x);t=Math.Min(t,y);r=Math.Max(r,x);b=Math.Max(b,y);}
   using(var small=new Bitmap(142,150,PixelFormat.Format32bppArgb))using(var g=Graphics.FromImage(small)){
    g.InterpolationMode=InterpolationMode.HighQualityBicubic;g.PixelOffsetMode=PixelOffsetMode.HighQuality;
    // Uniformly fit the source bounds into the shared device-sized bitmap.
    float scale=Math.Min(142f/(r-l+1),150f/(b-t+1));float w=(r-l+1)*scale,h=(b-t+1)*scale;
    g.DrawImage(src,new RectangleF((142-w)/2,(150-h)/2,w,h),new Rectangle(l,t,r-l+1,b-t+1),GraphicsUnit.Pixel);
    small.Save(Path.Combine(assets,"nono-initial.png"),ImageFormat.Png);
   }
  }
  foreach(char c in "0123456789:-")TextImage(c.ToString(),Path.Combine(ui,"clock-"+(c==':'?"colon":c=='-'?"dash":c.ToString())+".png"),c==':'?12:24,38,"Consolas",32,true);
  string[] modes={"idle","eat","sleep","read","game","pet","laser"},labels={"站立待机","吃饭","睡觉","看书","打游戏","撸猫","激光逗猫"};
  for(int i=0;i<modes.Length;i++){
   TextImage("诺诺 · 初始",Path.Combine(ui,"title-"+modes[i]+".png"),170,22,"Microsoft YaHei UI",16,false);
   TextImage(labels[i],Path.Combine(ui,"status-"+modes[i]+".png"),170,20,"Microsoft YaHei UI",12,false);
  }
  TextImage("素材加载失败",Path.Combine(ui,"status-error.png"),170,20,"Microsoft YaHei UI",12,false);
  TextImage("等待设备校时",Path.Combine(ui,"status-time.png"),170,20,"Microsoft YaHei UI",12,false);
  using(var src=new Bitmap(Path.Combine(assets,"nono-initial.png")))using(var icon=new Bitmap(64,64))using(var g=Graphics.FromImage(icon)){
   g.InterpolationMode=InterpolationMode.HighQualityBicubic;g.DrawImage(src,2,0,60,64);icon.Save(Path.Combine(root,"代码","main.png"),ImageFormat.Png);
  }
 }
}
