from PIL import Image,ImageDraw
from laser_sequence import ROOT
from meal_bridges import frames
for folder in ROOT.iterdir():
 paths=list(folder.glob('*.mp4')) if folder.is_dir() else []
 if not paths:continue
 dest=folder/'motion-dense.jpg'
 if dest.exists():continue
 v=frames(paths[0]);sheet=Image.new('RGB',(1248,1120));d=ImageDraw.Draw(sheet)
 for j in range(12):
  k=round(j*(len(v)-1)/11);x=j%3*416;y=j//3*280
  sheet.paste(v[k].resize((416,280)),(x,y));d.text((x+5,y+5),str(k),fill='black')
 sheet.save(dest);print(folder.name,len(v))
