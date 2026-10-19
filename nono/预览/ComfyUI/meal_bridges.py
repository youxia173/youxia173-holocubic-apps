"""Lossless RIFE bridges around meal cuts, with a shared loop anchor."""
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path
import imageio_ffmpeg as ff
from PIL import Image
import nono_video as api

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parent.parent / '连续喂饭'
OUT = ROOT / '循环吃饭' / 'bridges'
OUT.mkdir(exist_ok=True)

def frames(path):
    reader = ff.read_frames(str(path))
    meta = next(reader)
    return [Image.frombytes('RGB', meta['size'], b) for b in reader]

def submit(name, first, last):
    folder = OUT / name
    folder.mkdir(exist_ok=True)
    if (folder / 'job.json').exists():
        return
    prompt = {}
    for key, im in [('1', first), ('2', last)]:
        path = folder / (key + '.png')
        im.save(path)
        prompt[key] = {'class_type': 'LoadImage', 'inputs': {'image': api.upload(path)}}
    prompt['3'] = {'class_type': 'ImageBatch', 'inputs': {'image1': ['1', 0], 'image2': ['2', 0]}}
    prompt['4'] = {'class_type': 'RIFE VFI', 'inputs': {'ckpt_name': 'rife47.pth', 'frames': ['3', 0], 'clear_cache_after_n_frames': 10, 'multiplier': 16, 'fast_mode': True, 'ensemble': True, 'scale_factor': 1.0}}
    prompt['5'] = {'class_type': 'SaveImage', 'inputs': {'images': ['4', 0], 'filename_prefix': 'Nono/bridges/' + name}}
    job = api.request('/prompt', json.dumps({'prompt': prompt}).encode(), {'Content-Type': 'application/json'})
    (folder / 'job.json').write_text(json.dumps(job), 'utf-8')
    print(name, job, flush=True)

def collect():
    complete = True
    for folder in sorted(OUT.iterdir()):
        if not folder.is_dir():
            continue
        job = json.loads((folder / 'job.json').read_text('utf-8'))
        item = api.request('/history/' + job['prompt_id']).get(job['prompt_id'])
        if not item:
            print(folder.name, 'pending'); complete = False; continue
        if item['status']['status_str'] != 'success':
            raise RuntimeError(item['status'])
        media = item['outputs']['5']['images']
        for i, info in enumerate(media):
            path = folder / f'frame-{i:02d}.png'
            if not path.exists():
                query = urllib.parse.urlencode(info)
                with urllib.request.urlopen(api.BASE + '/view?' + query, timeout=60) as res:
                    path.write_bytes(res.read())
        print(folder.name, len(media), 'ready')
    return complete

if __name__ == '__main__':
    if sys.argv[1] == 'collect':
        collect()
    elif sys.argv[1] == 'cuts':
        paths = sorted((ROOT / '完整动画').glob('[0-9][0-9]-*/*.mp4'))
        # Work pairwise to avoid retaining eight full-resolution clips in memory.
        for i in [0, 1, 2, 4, 5, 6]:
            first = frames(paths[i])[-9]
            last = frames(paths[i+1])[8]
            submit(f'cut-{i+1:02d}', first, last)
    elif sys.argv[1] == 'loop':
        clip = frames(next((ROOT / '循环吃饭').glob('*.mp4')))
        submit('loop-close', clip[-9], clip[8])
    elif sys.argv[1] == 'links':
        anchor = Image.open(OUT / 'loop-close/frame-08.png').convert('RGB')
        paths = sorted((ROOT / '完整动画').glob('[0-9][0-9]-*/*.mp4'))
        submit('enter-loop', frames(paths[3])[-9], anchor)
        submit('exit-loop', anchor, frames(paths[4])[8])
