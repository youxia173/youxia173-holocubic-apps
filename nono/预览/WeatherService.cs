using System;
using System.IO;
using System.Net;
using System.Threading;
using System.Collections.Generic;
using System.Web.Script.Serialization;
using System.Globalization;

public sealed class WeatherDay {public string date,text;public int code;public double low,high;}
public sealed class WeatherData {
 public string query,location;public DateTime fetchedUtc;public int offset;public WeatherDay[] days;
 public WeatherDay Day(int ahead,DateTime utc){if(days==null||utc-fetchedUtc>TimeSpan.FromHours(6))return null;string date=utc.AddSeconds(offset).Date.AddDays(ahead).ToString("yyyy-MM-dd");return Array.Find(days,d=>d.date==date);}
}
public sealed class WeatherService:IDisposable {
 readonly string cache;readonly object gate=new object();bool busy,disposed;string requested="";DateTime next=DateTime.MinValue;
 public volatile WeatherData Data;public volatile string Status="正在获取天气";
 public WeatherService(string path){cache=path;try{if(File.Exists(path))Data=new JavaScriptSerializer().Deserialize<WeatherData>(File.ReadAllText(path));}catch{}}
 public static string Describe(int code){
  if(code==0)return "晴";if(code==1)return "晴间多云";if(code==2)return "多云";if(code==3)return "阴";
  if(code==45||code==48)return "雾";if(code>=51&&code<=57)return "毛毛雨";
  if(code>=61&&code<=67)return code==61?"小雨":code==63?"中雨":code==65?"大雨":"冻雨";
  if(code>=71&&code<=77)return "降雪";if(code>=80&&code<=82)return "阵雨";if(code==85||code==86)return "阵雪";
  if(code>=95&&code<=99)return "雷雨";return "未知天气";
 }
 static Dictionary<string,object> Get(string url){
  ServicePointManager.SecurityProtocol|=SecurityProtocolType.Tls12;
  var r=(HttpWebRequest)WebRequest.Create(url);r.Timeout=15000;r.ReadWriteTimeout=15000;r.UserAgent="NonoDesktop/0.8.2";r.AutomaticDecompression=DecompressionMethods.GZip;
  using(var response=r.GetResponse())using(var reader=new StreamReader(response.GetResponseStream()))return new JavaScriptSerializer().Deserialize<Dictionary<string,object>>(reader.ReadToEnd());
 }
 static double Number(object value){return Convert.ToDouble(value,CultureInfo.InvariantCulture);}
 public static WeatherData Fetch(string city){
  double lat,lon;string location;
  if(city=="上海长宁区"||city=="上海市长宁区"){lat=31.21739;lon=121.42105;location="上海 · 长宁区";}
  else {
   var geo=Get("https://geocoding-api.open-meteo.com/v1/search?name="+Uri.EscapeDataString(city)+"&count=1&language=zh");
   if(!geo.ContainsKey("results"))throw new Exception("未找到地点，请使用城市名或拼音");
   var list=geo["results"] as System.Collections.IList;if(list==null||list.Count==0)throw new Exception("未找到地点，请使用城市名或拼音");
   var first=(Dictionary<string,object>)list[0];lat=Number(first["latitude"]);lon=Number(first["longitude"]);location=(first.ContainsKey("admin1")?first["admin1"]+" · ":"")+first["name"];
  }
  var raw=Get("https://api.open-meteo.com/v1/forecast?latitude="+lat.ToString(CultureInfo.InvariantCulture)+"&longitude="+lon.ToString(CultureInfo.InvariantCulture)+"&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto&forecast_days=3");
  var daily=(Dictionary<string,object>)raw["daily"];var dates=(System.Collections.IList)daily["time"];var codes=(System.Collections.IList)daily["weather_code"];var high=(System.Collections.IList)daily["temperature_2m_max"];var low=(System.Collections.IList)daily["temperature_2m_min"];
  var days=new List<WeatherDay>();for(int i=0;i<dates.Count;i++){if(codes[i]==null||high[i]==null||low[i]==null)continue;int code=Convert.ToInt32(codes[i]);days.Add(new WeatherDay{date=dates[i].ToString(),code=code,text=Describe(code),high=Number(high[i]),low=Number(low[i])});}
  if(days.Count<2)throw new Exception("预报数据暂不完整");
  return new WeatherData{query=city,location=location,offset=Convert.ToInt32(raw["utc_offset_seconds"]),fetchedUtc=DateTime.UtcNow,days=days.ToArray()};
 }
 public void Poll(string city){
  lock(gate){
   if(disposed)return;
   if(city!=requested){requested=city;next=DateTime.MinValue;if(Data!=null&&Data.query!=city)Data=null;Status="正在获取天气";}
   if(busy||DateTime.UtcNow<next)return;busy=true;next=DateTime.UtcNow.AddMinutes(30);
  }
  ThreadPool.QueueUserWorkItem(delegate{
   WeatherData value=null;string error=null;try{value=Fetch(city);}catch(Exception ex){error=ex is WebException?"天气网络连接失败，将自动重试":ex.Message;}
   lock(gate){busy=false;if(disposed||requested!=city)return;
    if(value!=null){Data=value;Status="已更新 · "+value.location;try{File.WriteAllText(cache,new JavaScriptSerializer().Serialize(value));}catch(IOException){}}
    else{Status=error;next=DateTime.UtcNow.AddMinutes(5);}
   }
  });
 }
 public void Dispose(){lock(gate)disposed=true;}
 public static void Verify(){
  var utc=new DateTime(2026,1,1,15,59,0,DateTimeKind.Utc);var w=new WeatherData{offset=28800,fetchedUtc=utc,days=new[]{new WeatherDay{date="2026-01-01"},new WeatherDay{date="2026-01-02"},new WeatherDay{date="2026-01-03"}}};
  if(w.Day(0,utc).date!="2026-01-01"||w.Day(1,utc.AddMinutes(2)).date!="2026-01-03"||w.Day(0,utc.AddHours(7))!=null)throw new Exception("Forecast date/cache expiry");
  if(Describe(0)!="晴"||Describe(63)!="中雨"||Describe(999)!="未知天气")throw new Exception("Weather codes");
 }
}
