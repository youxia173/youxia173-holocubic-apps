"""Append ramen to checked device streams without rebuilding existing animation assets."""
from pathlib import Path
import bisect, copy, hashlib, json, zlib
import numpy as np
from PIL import Image

R = Path(__file__).resolve().parents[2]
C = R / '代码'
O = C / 'assets/frames'
original = {p: hashlib.sha256(p.read_bytes()).digest() for p in O.iterdir() if 'ramen' not in p.name}
layout = json.loads((C / 'frame-layout.json').read_text('utf-8'))
source = json.loads((C / 'layout.json').read_text('utf-8'))
meal = next(a for a in layout['assets'] if a['id'] == 'eat')
ramen = copy.deepcopy(next(a for a in source['assets'] if a['id'] == 'eat')['variants'][0])
for key, count in [('file','frame_count'),('loop_file','loop_frame_count'),('outro_file','outro_frame_count')]:
    path = C / ramen[key]
    frames, ends, total = [], [], 0
    with Image.open(path) as im:
        for i in range(im.n_frames):
            im.seek(i)
            rgba = np.asarray(im.convert('RGBA'), dtype=np.uint16)
            frames.append((rgba[:,:,:3] * rgba[:,:,3:4] // 255).astype(np.uint16))
            total += im.info['duration']; ends.append(total)
    times = list(range(0, total, 40))
    indices = [min(len(frames)-1, bisect.bisect_right(ends,t)) for t in times]
    indices[-1] = len(frames)-1
    entries, offset = [], 0
    with (O / (path.stem + '.rgbz')).open('wb') as fp:
        for t, i in zip(times, indices):
            rgb = frames[i]; ys, xs = np.where(np.any(rgb != 0, axis=2))
            x,y,right,bottom = (int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)) if len(xs) else (0,0,1,1)
            crop = rgb[y:bottom,x:right]
            raw = (((crop[:,:,0]>>3)<<11)|((crop[:,:,1]>>2)<<5)|(crop[:,:,2]>>3)).astype('<u2').tobytes()
            packed = zlib.compress(raw,3)
            fp.write(packed)
            entries.append([offset,len(packed),min(40,total-t),format(zlib.crc32(raw),'08x'),x,y,right-x,bottom-y])
            offset += len(packed)
    meta = dict(width=200,height=150,frame_ms=40,duration_ms=total,data=path.stem+'.rgbz',frames=entries)
    (O/(path.stem+'.json')).write_text(json.dumps(meta,separators=(',',':')),'utf-8')
    ramen[key] = 'assets/frames/'+path.stem+'.json'; ramen[count] = len(entries)
    print(path.stem, len(entries), total, offset)
ramen['kind'] = 'rgb565'
meal['variant'] = 'rice'; meal['variants'] = [ramen]
layout['version'] = '1.0.6'
(C/'frame-layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),'utf-8')
assert all(hashlib.sha256(p.read_bytes()).digest()==h for p,h in original.items())
print('PASS: existing checked device streams unchanged; ramen added at 25 fps')
