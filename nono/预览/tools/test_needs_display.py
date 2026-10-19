from pathlib import Path
import requests,re,json
p=Path('youxia173-apps/nono/预览');s=requests.Session();s.trust_env=False;u=(p/'网页设置地址.txt').read_text('utf-8-sig').strip();html=s.get(u).text;assert 'id="needsDisplay"' in html;token=re.search("TOKEN='([^']+)'",html)[1];original=s.get(u+'api/state').json()
def post(d):return s.post(u+'api/settings',json=dict(d,token=token),timeout=10)
try:
 r=post({'needsDisplay':'always','needsDisplaySeconds':3});r.raise_for_status();assert r.json()['needsVisible']
 r=post({'needsDisplay':'changed','needsDisplaySeconds':2});r.raise_for_status();assert r.json()['needsDisplay']=='changed'
 for bad in [0,601,1.5]:assert post({'needsDisplaySeconds':bad,'needsDisplay':'always'}).status_code==400
 assert s.get(u+'api/state').json()['needsDisplay']=='changed'
 assert post({'needsDisplay':'unknown'}).status_code==400
finally:post({k:original[k] for k in ['needsDisplay','needsDisplaySeconds']}).raise_for_status()
prefs=json.loads((p/'窗口设置.json').read_text('utf-8-sig'));assert prefs['needsDisplay']==original['needsDisplay'] and prefs['needsDisplaySeconds']==original['needsDisplaySeconds'];print('PASS: modes, immediate visibility, custom timeout, invalid values atomic rejection, persisted defaults restored');print(u)
