from pathlib import Path
app=Path(__file__).resolve().parents[2];preview=app/'预览'
p=preview/'NonoPreview.cs';s=p.read_text('utf-8-sig')
start=s.index(' void BuildTools(){');end=s.index(' protected override CreateParams',start);s=s[:start]+s[end:]
start=s.index(' void Log(string text)');end=s.index(' protected override CreateParams',start);s=s[:start]+s[end:]
for line in [' readonly Form tools=new Form();',' readonly ListBox events=new ListBox();',' readonly Label diagnostics=new Label();',' readonly CheckBox simulated=new CheckBox();',' readonly DateTimePicker simulatedTime=new DateTimePicker();',' ComboBox choices;','  BuildTools();']:
    s=s.replace(line+'\n','')
s=s.replace('tools.Icon=Icon;','')
s='\n'.join(line for line in s.split('\n') if 'diagnostics.Text=' not in line and 'if(tools.Visible)' not in line)
start=s.index(' public void PlayActivity(string id){');end=s.index(' public void OpenSettings()',start)
s=s[:start]+''' public void PlayActivity(string id){
  if(!Array.Exists(scene.Layout.assets,a=>a.id==id))throw new ArgumentException("Unknown activity");
  scene.SetActivity(id);activityStart=elapsed.ElapsedMilliseconds;scheduler.Reset(activityStart,id);
 }
'''+s[end:]
s=s.replace('if(scheduler.Automatic)choices.SelectedIndex=0;', 'if(scheduler.Automatic)PlayActivity(scene.Layout.default_activity);')
s=s.replace('simulated.Checked?simulatedTime.Value:DateTime.Now','DateTime.Now').replace('tools.Close();','').replace('tools.Dispose();','')
p.write_text(s,'utf-8-sig')
p=app/'代码/info.html';s=p.read_text('utf-8').replace('诺诺 V','桌宠诺诺 V').replace('桌面面板可直接设置并保存','网页设置可直接调整并保存');s=s.replace('</html>','<p>V0.7.0：全新诺诺与白猫图标，网页设置支持自动生活、活动切换和独立时长。启动后访问应用网页即可设置。</p></html>');p.write_text(s,'utf-8')
p=preview/'tools/package_windows.py';s=p.read_text('utf-8').replace("'诺诺/'","'桌宠诺诺/'");p.write_text(s,'utf-8')
p=preview/'tools/package.py';s=p.read_text('utf-8').replace('诺诺 V0.7.0','桌宠诺诺 V0.7.0').replace('网页设置版。','网页设置版。启动后打开应用网页设置自动生活、各活动时长及画面遮挡。');p.write_text(s,'utf-8')
p=app.parent/'README.md';s=p.read_text('utf-8');lines=s.splitlines();lines=[line.replace('0.6.1','0.7.0').replace('| 诺诺 |','| 桌宠诺诺 |') if 'nono/' in line or '`nono`' in line else line for line in lines];p.write_text('\n'.join(lines)+'\n','utf-8')
print('Removed native debug panel; web settings is now the only settings interface')
