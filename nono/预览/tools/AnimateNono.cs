using System;
using System.IO;
using System.Drawing;
using System.Drawing.Imaging;
using System.Drawing.Drawing2D;

// Offline animation rig; the emitted PNG frames are encoded into one shared GIF per activity.
// Inverse deformation is continuous in time and sampled at 25 FPS. No repeated hold frames.
public static class AnimateNono {
 const int W=200,H=150,N=100;
 sealed class Sprite : IDisposable {
  public Bitmap Image;
  public Rectangle Bounds;
  public float Scale,Left,Top;
  public int RawWidth,RawHeight;
  public Sprite(string path,bool gif) {
   using(var raw=new Bitmap(path)) {
    if(gif)raw.SelectActiveFrame(FrameDimension.Time,0);
    RawWidth=raw.Width;RawHeight=raw.Height;
    int l=raw.Width,t=raw.Height,r=0,b=0;
    for(int y=0;y<raw.Height;y++)for(int x=0;x<raw.Width;x++)if(raw.GetPixel(x,y).A>96){l=Math.Min(l,x);t=Math.Min(t,y);r=Math.Max(r,x);b=Math.Max(b,y);}
    Bounds=Rectangle.FromLTRB(l,t,r+1,b+1);Scale=Math.Min(184f/Bounds.Width,142f/Bounds.Height);
    float dw=Bounds.Width*Scale,dh=Bounds.Height*Scale;Left=(W-dw)/2;Top=148-dh;
    Image=new Bitmap(W,H,PixelFormat.Format32bppArgb);
    using(var g=Graphics.FromImage(Image)){
     g.InterpolationMode=InterpolationMode.HighQualityBicubic;g.PixelOffsetMode=PixelOffsetMode.HighQuality;
     g.DrawImage(raw,new RectangleF(Left,Top,dw,dh),Bounds,GraphicsUnit.Pixel);
    }
   }
  }
  public PointF Point(float x,float y){return new PointF(Left+(x-Bounds.Left)*Scale,Top+(y-Bounds.Top)*Scale);}
  public PointF Relative(float x,float y){return Point(x*RawWidth,y*RawHeight);}
  public void Dispose(){Image.Dispose();}
 }
 static float[] Pixels(Bitmap image) {
  var data=new float[W*H*4];
  for(int y=0;y<H;y++)for(int x=0;x<W;x++){
   var c=image.GetPixel(x,y);int i=(y*W+x)*4;float a=c.A/255f;
   data[i]=c.R*a;data[i+1]=c.G*a;data[i+2]=c.B*a;data[i+3]=c.A;
  }return data;
 }
 static float Sample(float[] d,double x,double y,int channel) {
  int ix=(int)Math.Floor(x),iy=(int)Math.Floor(y);double fx=x-ix,fy=y-iy,v=0;
  for(int a=0;a<2;a++)for(int b=0;b<2;b++){int xx=ix+a,yy=iy+b;if(xx>=0&&xx<W&&yy>=0&&yy<H)v+=d[(yy*W+xx)*4+channel]*(a==0?1-fx:fx)*(b==0?1-fy:fy);}
  return (float)v;
 }
 static double Gaussian(double x,double y,double cx,double cy,double rx,double ry){return Math.Exp(-.5*(Math.Pow((x-cx)/rx,2)+Math.Pow((y-cy)/ry,2)));}
 static double EyeMask(int x,int y,PointF eye,double rx,double ry){
  double d=Math.Sqrt(Math.Pow((x-eye.X)/rx,2)+Math.Pow((y-eye.Y)/ry,2));return Math.Max(0,Math.Min(1,(1.28-d)/.28));
 }
 static int Byte(double v){return (int)Math.Max(0,Math.Min(255,Math.Round(v)));}
 public static void Run(string root) {
  string input=Path.Combine(root,"说明","形象参考"), output=Path.Combine(root,"预览","动画帧");
  Directory.CreateDirectory(output);
  foreach(string mode in new[]{"idle","eat","sleep","read","game"}) {
   using(var sprite=new Sprite(Path.Combine(input,"nono-"+mode+"-v2.png"),false))
   using(var blink=new Sprite(Path.Combine(input,"nono-idle-blink-v2.png"),false)) {
    Directory.CreateDirectory(Path.Combine(output,mode));
    float[] normal=Pixels(sprite.Image),closed=Pixels(blink.Image);
    var leftEye=sprite.Relative(.438f,.374f);var rightEye=sprite.Relative(.592f,.350f);
    var head=sprite.Relative(mode=="sleep"?.34f:.52f,mode=="sleep"?.44f:.39f);
    var chest=sprite.Relative(mode=="sleep"?.58f:.52f,mode=="sleep"?.69f:.60f);
    var hand=sprite.Relative(.435f,.51f);
    var book=sprite.Relative(.46f,.67f);
    var console=sprite.Relative(.52f,.68f);
    for(int f=0;f<N;f++) {
     double phase=2*Math.PI*f/N,breath=Math.Sin(phase),sway=Math.Sin(phase+Math.PI/4);
     double sec=f/25.0,amount=0;
     if(sec>=1.6&&sec<1.72)amount=.5-.5*Math.Cos(Math.PI*(sec-1.6)/.12);
     else if(sec>=1.72&&sec<1.80)amount=1;
     else if(sec>=1.80&&sec<1.96)amount=.5+.5*Math.Cos(Math.PI*(sec-1.80)/.16);
     float[] cel=(float[])normal.Clone();
     if(mode=="idle"&&amount>0) {
      for(int y=0;y<H;y++)for(int x=0;x<W;x++) {
       double mask=Math.Max(EyeMask(x,y,leftEye,6.5,7),EyeMask(x,y,rightEye,6.5,7))*amount;
       if(mask<=0)continue;int i=(y*W+x)*4;
       for(int c=0;c<3;c++)cel[i+c]=(float)(normal[i+c]*(1-mask)+closed[i+c]*mask);
      }
     }
     using(var frame=new Bitmap(W,H,PixelFormat.Format32bppArgb)) {
      for(int y=0;y<H;y++)for(int x=0;x<W;x++) {
       double h=Gaussian(x,y,head.X,head.Y,32,30),c=Gaussian(x,y,chest.X,chest.Y,25,17);
       double hair=Gaussian(x,y,head.X,head.Y+35,53,25)*(1-Gaussian(x,y,chest.X,chest.Y,26,42));
       double angle=(mode=="read"?.012:.004)*sway;
       double dx=angle*(y-chest.Y)*h+.45*Math.Sin(phase+.65)*hair;
       double dy=-angle*(x-head.X)*h-(mode=="sleep"?1.15:.65)*breath*h-.45*breath*c;
       dx+=(x-chest.X)*.008*breath*c;
       if(mode=="eat") {
        // Spoon, fingers and forearm approach the mouth and settle back together.
        double lift=Gaussian(x,y,hand.X,hand.Y,12,11);
        dx+=1.7*Math.Sin(phase)*lift;dy-=2.6*Math.Sin(phase)*lift;
        dy+=.3*Math.Sin(3*phase)*Gaussian(x,y,head.X,head.Y+16,7,5);
       } else if(mode=="read") {
        double page=Gaussian(x,y,book.X,book.Y,19,8);
        dx+=.9*Math.Sin(phase)*page;dy+=.65*Math.Sin(2*phase)*page;
       } else if(mode=="game") {
        double left=Gaussian(x,y,console.X-16,console.Y,6,7),right=Gaussian(x,y,console.X+16,console.Y,6,7);
        dy+=.9*Math.Sin(6*phase)*left+.8*Math.Sin(8*phase+.7)*right;
        dx+=.6*Math.Sin(2*phase)*Gaussian(x,y,console.X,console.Y,23,13);
        dy-=.35*Math.Sin(2*phase)*h;
       }
       // Contact lock: shoes, cushion and floor contact never translate or breathe.
       double ground=Math.Max(0,Math.Min(1,(132-y)/17.0));ground=ground*ground*(3-2*ground);
       dx*=ground;dy*=ground;
       double a=Sample(cel,x-dx,y-dy,3);
       if(a<1){frame.SetPixel(x,y,Color.Transparent);continue;}
       frame.SetPixel(x,y,Color.FromArgb(Byte(a),Byte(Sample(cel,x-dx,y-dy,0)*255/a),Byte(Sample(cel,x-dx,y-dy,1)*255/a),Byte(Sample(cel,x-dx,y-dy,2)*255/a)));
      }
      frame.Save(Path.Combine(output,mode,f.ToString("D3")+".png"),ImageFormat.Png);
     }
    }
   }
  }
 }
}
