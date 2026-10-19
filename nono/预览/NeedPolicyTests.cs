using System;
public static class NeedPolicyTests {
 static void Check(bool ok,string message){if(!ok)throw new Exception(message);}
 public static void Verify(string root){
  VerifyMeals(root);
  using(var scene=new PetScene(root)){
   var normal=new PetNeeds();var boosted=new PetNeeds();normal.Advance("eat",5,5);boosted.Advance("eat",5,5,2);Check(Math.Abs(boosted.Satiety-normal.Satiety-5)<.00001,"Recovery multiplier must only multiply gain");
   var layout=scene.Layout;var scheduler=new ActivityScheduler(layout,321,scene.Timing);scheduler.Needs=scene.Needs;
   scene.Needs.Satiety=30;scene.Needs.Energy=25;scene.Needs.Mood=35;Check(ActivityScheduler.Urgent(scene.Needs)==null,"Strict thresholds");
   scene.Needs.Satiety=29;Check(ActivityScheduler.Urgent(scene.Needs)=="eat","Food threshold");scene.Needs.Energy=1;Check(ActivityScheduler.Urgent(scene.Needs)=="sleep","Urgency ranking");scene.Needs.Mood=0;Check(ActivityScheduler.Urgent(scene.Needs)=="play","Mood urgency");
   foreach(string id in new[]{"eat","sleep","game","pet","laser"}){
    scene.Needs=new PetNeeds{Satiety=20,Energy=20,Mood=20};var a=Array.Find(layout.assets,v=>v.id==id);int saved=scene.Timing.Get(id);
    int seconds=ActivityScheduler.RecoverySeconds(a,scene.Needs);scene.SetActivity(id,seconds,true);
    scene.AccrueNeeds(0,scene.DurationMs);
    double value=id=="eat"?scene.Needs.Satiety:id=="sleep"?scene.Needs.Energy:scene.Needs.Mood;
    Check(value>=(id=="sleep"?85:80)-.0001,"Recovery must reach target after outro: "+id);
    Check(scene.DurationMs==layout.ActivityDuration(a,seconds),"Whole-loop duration");Check(scene.Timing.Get(id)==saved,"Recovery changed manual settings");
   }
   scheduler.Needs=new PetNeeds{Satiety=20};scheduler.Reset(0,"idle");var idle=Array.Find(layout.assets,v=>v.id=="idle");
   Check(scheduler.Next("idle",idle.duration_ms-1)==null,"Idle loop interrupted");Check(scheduler.Next("idle",idle.duration_ms)=="eat","Low food not scheduled");
   long due=scheduler.Due;int planned=scheduler.PlannedSeconds;scheduler.Needs.Energy=0;
   Check(scheduler.Next("eat",due-1)==null&&scheduler.PlannedSeconds==planned,"Running activity interrupted/replanned");Check(scheduler.Next("eat",due)=="idle","Recovery didn't return to idle");
   Check(scheduler.Next("idle",due+idle.duration_ms)=="sleep","Pending urgent need not handled");
   scheduler.Automatic=false;scheduler.ClearPlan();scheduler.Reset(0,"idle");Check(scheduler.Next("idle",999999)==null,"Manual mode started automatic recovery");
   scheduler.Reset(0,"eat");Check(scheduler.Next("eat",scheduler.Due)=="idle","Manual complete flow failed");
   scheduler.Automatic=true;scheduler.Needs=new PetNeeds();scheduler.Reset(0,"idle");
   for(int i=0;i<30;i++){string next=scheduler.Next("idle",scheduler.Due);Check(next!="eat"&&next!="sleep","Healthy leisure included recovery-only action");scheduler.Reset(scheduler.Due,"idle");}
  }
 }
 static void VerifyMeals(string root){
  using(var scene=new PetScene(root)){
   scene.EnableHighDefinition();
   var scheduler=new ActivityScheduler(scene.Layout,173,scene.Timing);
   var variants=new System.Collections.Generic.HashSet<string>();
   for(int i=0;i<60;i++){scheduler.PrepareActivity("eat");variants.Add(Array.Find(scene.Layout.assets,a=>a.id=="eat").variant??"rice");}
   Check(variants.Contains("rice")&&variants.Contains("ramen"),"Both meals must be reachable");
   for(int choice=0;choice<2;choice++){
    scene.Layout.SelectMeal(choice);
    var a=Array.Find(scene.Layout.assets,v=>v.id=="eat");
    foreach(int seconds in new[]{5,600}){
     scene.Timing.Set("eat",seconds);scene.SetActivity("eat");
     Check(scene.Error==null,"Meal failed to decode: "+scene.Error);
     scheduler.ClearPlan();scheduler.Reset(0,"eat");
     Check(scene.DurationMs==scheduler.Due,"Meal variant scheduler duration mismatch");
     if(seconds==5){
      string folder=System.IO.Path.GetFullPath(System.IO.Path.Combine(root,"..","预览","验证","拉面"));System.IO.Directory.CreateDirectory(folder);
      scene.Snapshot(System.IO.Path.Combine(folder,(a.variant??"rice")+"-loop.png"),a.duration_ms+a.loop_duration_ms/2,DateTime.Now);
      scene.Snapshot(System.IO.Path.Combine(folder,(a.variant??"rice")+"-end.png"),scene.DurationMs-1,DateTime.Now);
     }
     string before=scene.MealVariant;
     Check(scheduler.Next("eat",scheduler.Due-1)==null&&scene.MealVariant==before,"Meal changed before complete");
     Check(scheduler.Next("eat",scheduler.Due)=="idle","Meal must finish at idle");
    }
    scene.Needs=new PetNeeds{Satiety=20};int recovery=ActivityScheduler.RecoverySeconds(a,scene.Needs);
    scene.SetActivity("eat",recovery,true);scene.AccrueNeeds(0,scene.DurationMs);
    Check(scene.Needs.Satiety>=80-.0001,"Both meal variants must recover food after cleanup");
    Check(scene.Timing.Get("eat")==600,"Automatic meal changed user duration");
   }
  }
 }
}
