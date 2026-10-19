using System;
using System.IO;
using System.Web.Script.Serialization;

public sealed class PetNeeds {
 public double Satiety=80, Mood=80, Energy=80, Experience=0;
 public int Level=1;
 public double Required {get{return 100+25.0*(Level-1);}}
 static double Clamp(double v){return Double.IsNaN(v)||Double.IsInfinity(v)?80:Math.Max(0,Math.Min(100,v));}
 public void Advance(string activity,double elapsedSeconds,double activeSeconds,double multiplier=1){
  if(elapsedSeconds<=0)return;
  activeSeconds=Math.Max(0,Math.Min(elapsedSeconds,activeSeconds));
  Satiety=Clamp(Satiety-elapsedSeconds/120+(activity=="eat"?activeSeconds*multiplier:0));
  Mood=Clamp(Mood-elapsedSeconds/200+((activity=="game"||activity=="pet"||activity=="laser")?activeSeconds*.8*multiplier:0));
  Energy=Clamp(Energy-(elapsedSeconds-(activity=="sleep"?activeSeconds:0))/150+(activity=="sleep"?activeSeconds*.8*multiplier:0));
  if(activity=="read")Experience+=activeSeconds;
  while(Experience>=Required){Experience-=Required;Level++;}
 }
 public static PetNeeds Load(string path){
  foreach(string file in new[]{path,path+".bak"}){
   try{if(!File.Exists(file))continue;var n=new JavaScriptSerializer().Deserialize<PetNeeds>(File.ReadAllText(file));
    if(n==null||n.Level<1||n.Level>100000||Double.IsNaN(n.Experience)||Double.IsInfinity(n.Experience)||n.Experience<0||n.Experience>=n.Required)continue;
    n.Satiety=Clamp(n.Satiety);n.Mood=Clamp(n.Mood);n.Energy=Clamp(n.Energy);return n;
   }catch(IOException){}catch(ArgumentException){}catch(InvalidOperationException){}
  }
  return new PetNeeds();
 }
 public void Save(string path){
  string temp=path+".tmp";File.WriteAllText(temp,new JavaScriptSerializer().Serialize(this));
  if(File.Exists(path))File.Replace(temp,path,path+".bak");else File.Move(temp,path);
 }
 public static void Verify(){
  var n=new PetNeeds();n.Advance("eat",10,0);if(n.Satiety>=80)throw new Exception("Intro must not award recovery");
  n.Advance("eat",30,30);if(n.Satiety!=100)throw new Exception("Food cap");
  foreach(string id in new[]{"game","pet","laser"}){n.Mood=50;n.Advance(id,10,10);if(n.Mood<=50)throw new Exception("Play recovery");}
  n.Energy=40;n.Advance("sleep",30,30);if(Math.Abs(n.Energy-64)>.001)throw new Exception("Sleep recovery");
  n.Experience=95;n.Advance("read",150,150);if(n.Level!=3||n.Experience!=20||n.Required!=150)throw new Exception("Multi-level carry");
  n.Advance("idle",100000,0);if(n.Satiety!=0||n.Mood!=0||n.Energy!=0)throw new Exception("Lower bounds");
  string path=Path.Combine(Path.GetTempPath(),"nono-needs-"+Guid.NewGuid()+".json");
  try{n.Save(path);var loaded=Load(path);if(loaded.Level!=3||loaded.Experience!=20)throw new Exception("Persistence");n.Save(path);File.WriteAllText(path,"broken");if(Load(path).Level!=3)throw new Exception("Backup recovery");}
  finally{foreach(string suffix in new[]{"",".bak",".tmp"})if(File.Exists(path+suffix))File.Delete(path+suffix);}
 }
}
