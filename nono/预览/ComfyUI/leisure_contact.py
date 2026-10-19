"""Contact sheets for generated motion and transparent GIFs."""
from PIL import Image,ImageDraw
from leisure_sequence import ROOT
from meal_bridges import frames
for folder in ROOT.iterdir():
 paths=list(folder.glob('*.mp4')) if folder.is_dir() else []
 if not paths:continue
 dest=folder/'motion.jpg'
 if dest.exists():continue
 v=frames(paths[0]); sheet=Image.new('RGB',(1248,840),'#dddddd');draw=ImageDraw.Draw(sheet)
 for j,k in enumerate([0,20,40,60,80,100,120,140,160]):
  im=v[min(k,len(v)-1)].resize((416,280));sheet.paste(im,((j%3)*416,(j//3)*280));draw.text(((j%3)*416+5,(j//3)*280+5),str(k),fill='black')
 sheet.save(dest);print(dest)
