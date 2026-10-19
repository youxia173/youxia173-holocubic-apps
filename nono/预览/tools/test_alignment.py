from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image
p=Path(__file__).resolve().parents[1];mapping=json.loads((p/'windows-hd.json').read_text('utf-8'));fix=json.loads((p/'windows-alignment.json').read_text('utf-8'));raw=json.loads((p/'验证/geometry-measurements.json').read_text('utf-8'))
for key,path in mapping.items():
 info=fix[key];f=np.array(info['frames']);assert hashlib.sha256((p/path).read_bytes()).hexdigest()==info['sha256']
 with Image.open(p/path) as im:assert len(f)==im.n_frames
 assert np.isfinite(f).all() and .8<=f[:,0].min()<=f[:,0].max()<=1
 assert np.ptp(f[:,0])==0,'Pose must not change camera scale'
 ground=np.array(raw[key])[:,1]*f[:,0]+f[:,2]
 if key=='assets/nono-game-outro.gif':
  assert np.max(np.abs(np.diff(f[:,2])))<1,'Rising correction must not jump between shoes'
  assert np.max(np.abs(ground-459))<9,'Correction must stay near the contact surface'
 else:assert np.max(np.abs(ground-459))<.001
 if '-loop' in key or 'idle' in key:assert np.max(np.abs(f[0]-f[-1]))<.001,'Loop correction discontinuity'
for a in ['eat','sleep','read','game','pet','laser','ramen']:
 def v(phase):return np.array(fix['assets/nono-'+a+'-'+phase+'.gif']['frames'])
 assert np.max(np.abs(v('intro')[-1]-v('loop')[0]))<.001
 assert np.max(np.abs(v('loop')[-1]-v('outro')[0]))<.001
 if a!='eat':
  idle=np.array(fix['assets/nono-idle-cat.gif']['frames']);assert np.max(np.abs(v('intro')[0]-idle[-1]))<.001;assert np.max(np.abs(v('outro')[-1]-idle[0]))<.001
print('PASS: all source hashes/frame counts, fixed activity scale, character baseline, all loop and sequence alignment boundaries.')
