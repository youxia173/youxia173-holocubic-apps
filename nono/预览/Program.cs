using System;
using System.IO;
using System.Reflection;
using System.Windows.Forms;

[assembly: AssemblyTitle("桌宠诺诺")]
[assembly: AssemblyProduct("桌宠诺诺 Windows 模拟器")]
[assembly: AssemblyVersion("1.0.3")]
internal static class Program {
 [STAThread]
 static int Main(string[] args) {
  try {
   string home=AppDomain.CurrentDomain.BaseDirectory;
   string root=Path.Combine(home,"代码");
   if(!File.Exists(Path.Combine(root,"layout.json")))throw new FileNotFoundException("找不到动画配置，请将桌宠诺诺.exe与代码、预览文件夹放在同一目录。");
   NonoPreview.SetProcessDPIAware();
   Application.EnableVisualStyles();
   Application.SetCompatibleTextRenderingDefault(false);
   if(Array.IndexOf(args,"--verify-weather")>=0){
    WeatherService.Verify();var forecast=WeatherService.Fetch("上海长宁区");
    File.WriteAllText(Path.Combine(home,"预览","验证","weather-live.json"),new System.Web.Script.Serialization.JavaScriptSerializer().Serialize(forecast));
    using(var scene=new PetScene(root)){scene.EnableHighDefinition();scene.Weather=forecast;scene.Snapshot(Path.Combine(home,"预览","验证","weather-layout.png"),0,DateTime.Now);}return 0;
   }
   if(Array.IndexOf(args,"--verify-needs")>=0){NeedsVisibility.Verify();WeatherService.Verify();PetNeeds.Verify();PetScene.VerifyNeedsTiming(root);NeedPolicyTests.Verify(root);return 0;}
   if(Array.IndexOf(args,"--verify")>=0){PetScene.Verify(root,Path.Combine(home,"预览","验证"));return 0;}
   if(Array.IndexOf(args,"--verify-hd")>=0){PetScene.VerifyHD(root,Path.Combine(home,"预览","验证","Windows高清"));return 0;}
   using(var window=new NonoPreview(root)) Application.Run(window);
   return 0;
  } catch(Exception ex) {
   if(Array.IndexOf(args,"--verify-weather")>=0||Array.IndexOf(args,"--verify-needs")>=0||Array.IndexOf(args,"--verify")>=0||Array.IndexOf(args,"--verify-hd")>=0){File.WriteAllText(Path.Combine(AppDomain.CurrentDomain.BaseDirectory,"启动错误.txt"),ex.ToString());return 1;}
   MessageBox.Show(ex.Message,"诺诺启动失败",MessageBoxButtons.OK,MessageBoxIcon.Error);return 1;
  }
 }
}
