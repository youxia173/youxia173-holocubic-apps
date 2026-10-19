using System;

public sealed class NeedsVisibility {
 public string Mode="changed";
 public int Seconds=10;
 string previous;
 long changedAt=long.MinValue;
 public static string Signature(PetNeeds n){return n.Satiety.ToString("0")+"/"+n.Mood.ToString("0")+"/"+n.Energy.ToString("0")+"/"+n.Level+"/"+Math.Floor(n.Experience);}
 public void Observe(PetNeeds n,long now){string value=Signature(n);if(previous!=null&&value!=previous)changedAt=now;previous=value;}
 public bool Visible(long now){return Mode=="always"||(changedAt!=long.MinValue&&now-changedAt<Seconds*1000L);}
 public static void Verify(){
  var v=new NeedsVisibility();var n=new PetNeeds();v.Observe(n,0);if(v.Visible(0))throw new Exception("Unchanged startup should be hidden");
  n.Satiety=79.99;v.Observe(n,100);if(v.Visible(100))throw new Exception("Fractional decay should not pin HUD");
  n.Satiety=79;v.Observe(n,1000);if(!v.Visible(10999)||v.Visible(11000))throw new Exception("Ten second timeout");
  n.Experience=1;v.Observe(n,9000);if(!v.Visible(18000)||v.Visible(19000))throw new Exception("Retrigger timer");
  v.Mode="always";if(!v.Visible(999999))throw new Exception("Always mode");v.Mode="changed";v.Seconds=2;if(v.Visible(11000))throw new Exception("Custom duration");
  n.Level++;n.Experience=0;v.Observe(n,20000);if(!v.Visible(20000))throw new Exception("Level-up event");
 }
}
