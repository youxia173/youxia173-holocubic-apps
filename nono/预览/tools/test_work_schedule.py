from pathlib import Path
import requests,re,json
p=Path(__file__).resolve().parents[1];u=(p/'网页设置地址.txt').read_text('utf-8-sig').strip();s=requests.Session();s.trust_env=False
html=s.get(u,timeout=10).text;assert 'id="workStart"' in html and 'id="workEnd"' in html;token=re.search("TOKEN='([^']+)'",html)[1];state=s.get(u+'api/state').json()
def post(data):return s.post(u+'api/settings',json=dict(data,token=token),timeout=10)
try:
 for bad in [{'workStart':'25:00'},{'workEnd':'08:00'},{'workStart':'18:00','workEnd':'18:00'}]:
  assert post(bad).status_code==400
  assert s.get(u+'api/state').json()['workStart']==state['workStart']
 r=post({'workStart':'09:30','workEnd':'17:45'});r.raise_for_status();d=r.json();assert d['workStart']=='09:30' and d['workEnd']=='17:45'
 saved=json.loads((p/'窗口设置.json').read_text('utf-8-sig'));assert saved['workStart']=='09:30' and saved['workEnd']=='17:45'
finally:post({k:state[k] for k in ['workStart','workEnd']}).raise_for_status()
print('PASS: work time inputs, validation, atomic rejection, settings persistence, original schedule restored.');print(u)
