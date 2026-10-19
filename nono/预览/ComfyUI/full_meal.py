"""Build the complete eight-clip meal cycle with the existing user workflow."""
import importlib.util
import json
import sys
import uuid
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
root = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('nono_video', root / 'nono_video.py')
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)
meal = root.parent / '连续喂饭'
output = meal / '完整动画'
output.mkdir(exist_ok=True)
names = ['拿出猫粮碗', '放碗喂猫', '拿出饭盒', '坐下吃饭', '吃完合盖', '收碗起身', '藏到身后', '回到待机']
frames = sorted(p for p in (meal / '关键帧').glob('A*.png') if '草稿' not in p.name)
assert len(frames) == 9

def submit():
    image_names = {}
    for image in frames:
        image_names[image.name] = api.upload(image)
    for i, name in enumerate(names):
        folder = output / f'{i+1:02d}-{name}'
        folder.mkdir(exist_ok=True)
        if (folder / 'job.json').exists():
            print('Existing job:', folder.name, flush=True)
            continue
        prompt, _ = api.convert()
        prompt['16']['inputs']['image'] = image_names[frames[i].name]
        prompt['9']['inputs']['image'] = image_names[frames[i+1].name]
        text = (meal / f'{i+1:02d}-视频提示词.txt').read_text(encoding='utf-8-sig')
        # Keep the model's original 81-frame temporal length, then interpolate.
        prompt['26']['inputs']['expression'] = 'a*16+1'
        prompt['27']['inputs']['background_color'] = '#00FF00'
        prompt['10']['inputs']['text'] = '两头身Q版动漫女孩诺诺，银蓝色长发蓝眼睛，科技服装正面始终是白色连衣裙、青色细边、白色独立袖子，白色长袜科技鞋。保持首尾图的服装图案和配色，一只蓝眼白猫，固定镜头，纯绿色背景。' + text
        prompt['23']['inputs']['text'] += '，换衣服，黑色上衣，衣服变色，成年体型，额外猫，额外手臂，额外手指，道具融合，碗穿模，字幕，镜头移动，缩放，切镜，脚滑，人物悬浮'
        prompt['104']['inputs']['seed'] = 17320261017 + i
        prompt['201'] = {'class_type': 'RIFE VFI', 'inputs': {'ckpt_name': 'rife47.pth', 'frames': ['122', 0], 'clear_cache_after_n_frames': 10, 'multiplier': 2, 'fast_mode': True, 'ensemble': True, 'scale_factor': 1.0}}
        prompt['18']['inputs'].update(images=['201', 0], frame_rate=32, filename_prefix=f'Nono/full_meal_{i+1:02d}')
        (folder / 'api_prompt.json').write_text(json.dumps(prompt, ensure_ascii=False, indent=2), encoding='utf-8')
        job = api.request('/prompt', json.dumps({'prompt': prompt, 'client_id': 'nono-full-' + uuid.uuid4().hex}).encode(), {'Content-Type': 'application/json'})
        job.update(segment=i+1, name=name, native_fps=16, output_fps=32, start=frames[i].name, end=frames[i+1].name)
        (folder / 'job.json').write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(job, ensure_ascii=False), flush=True)

def collect():
    results = []
    for folder in sorted(output.glob('[0-9][0-9]-*')):
        job = json.loads((folder / 'job.json').read_text(encoding='utf-8'))
        history = api.request('/history/' + job['prompt_id'])
        item = history.get(job['prompt_id'])
        if not item:
            results.append({'segment': folder.name, 'status': 'pending'})
            continue
        (folder / 'history.json').write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding='utf-8')
        status = item.get('status', {}).get('status_str')
        if status == 'success':
            for out in item.get('outputs', {}).values():
                for media in out.get('gifs', []):
                    path = folder / media['filename']
                    if not path.exists():
                        query = api.urllib.parse.urlencode({k: media[k] for k in ('filename', 'subfolder', 'type')})
                        with api.urllib.request.urlopen(api.BASE + '/view?' + query, timeout=120) as r:
                            path.write_bytes(r.read())
            results.append({'segment': folder.name, 'status': status, 'files': [p.name for p in folder.glob('*.mp4')]})
        else:
            results.append({'segment': folder.name, 'status': status, 'messages': item.get('status', {}).get('messages')})
    print(json.dumps(results, ensure_ascii=False, indent=2), flush=True)

submit() if sys.argv[1] == 'submit' else collect()
