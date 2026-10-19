"""Submit Nono clips through the user's existing first/last-frame workflow."""
import argparse
import json
import sys
import uuid
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = 'http://192.168.31.146:8888'

def request(path, data=None, headers=None):
    req = urllib.request.Request(BASE + path, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(e.read().decode('utf-8', errors='replace')) from e

def upload(path):
    path = Path(path)
    boundary = 'Nono' + uuid.uuid4().hex
    name = 'nono_' + uuid.uuid4().hex[:10] + '.png'
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{name}"\r\nContent-Type: image/png\r\n\r\n').encode() + path.read_bytes() + f'\r\n--{boundary}--\r\n'.encode()
    result = request('/upload/image', body, {'Content-Type': 'multipart/form-data; boundary=' + boundary})
    return (result.get('subfolder', '') + '/' + result['name']).lstrip('/')

def convert():
    workflow = json.loads((ROOT / '原始首尾帧工作流.json').read_text(encoding='utf-8'))
    info = json.loads((ROOT / 'object_info.json').read_text(encoding='utf-8'))
    nodes = {n['id']: n for n in workflow['nodes']}
    links = {l[0]: l for l in workflow['links']}
    setters = {n['widgets_values'][0]: n for n in nodes.values() if n['type'] in ('SetNode', 'easy setNode')}
    def resolve(node_id, slot):
        node = nodes[node_id]
        if node['type'] in ('GetNode', 'easy getNode'):
            node = setters[node['widgets_values'][0]]
        if node['type'] in ('SetNode', 'easy setNode'):
            link = links[node['inputs'][0]['link']]
            return resolve(link[1], link[2])
        return [str(node_id), slot]
    result = {}
    for node in nodes.values():
        kind = node['type']
        if kind in ('GetNode', 'SetNode', 'easy getNode', 'easy setNode'):
            continue
        if kind not in info:
            raise ValueError('Unavailable node: ' + kind)
        values = node.get('widgets_values', [])
        widgets = [i['name'] for i in node.get('inputs', []) if 'widget' in i]
        if kind == 'WanMoeKSampler':
            values = values[:2] + values[3:]  # frontend seed-control widget
        inputs = dict(values) if isinstance(values, dict) else dict(zip(widgets, values))
        inputs.pop('videopreview', None)
        inputs.pop('upload', None)
        for inp in node.get('inputs', []):
            if inp.get('link') is not None:
                link = links[inp['link']]
                inputs[inp['name']] = resolve(link[1], link[2])
        result[str(node['id'])] = {'class_type': kind, 'inputs': inputs}
    return result, workflow

def submit(args):
    target = Path(args.output)
    target.mkdir(parents=True, exist_ok=True)
    if (target / 'job.json').exists():
        raise RuntimeError('Job already submitted here; inspect it before resubmitting.')
    prompt, workflow = convert()
    prompt['16']['inputs']['image'] = upload(args.start)
    prompt['9']['inputs']['image'] = upload(args.end)
    prompt['10']['inputs']['text'] = Path(args.prompt).read_text(encoding='utf-8')
    prompt['26']['inputs']['expression'] = f'a*{args.fps}+1'
    prompt['18']['inputs'].update(frame_rate=args.fps, filename_prefix='Nono/meal_' + args.name)
    prompt['27']['inputs']['background_color'] = '#00FF00'
    prompt['104']['inputs']['seed'] = args.seed
    prompt['23']['inputs']['text'] += '，镜头移动，缩放，切镜，跳切，身体漂浮，脚滑动，绿背景变化，额外人物，多只猫，物体凭空出现，碗变形'
    (target / 'api_prompt.json').write_text(json.dumps(prompt, ensure_ascii=False, indent=2), encoding='utf-8')
    payload = {'prompt': prompt, 'client_id': 'nono-' + uuid.uuid4().hex}
    job = request('/prompt', json.dumps(payload).encode(), {'Content-Type': 'application/json'})
    job.update(start=str(Path(args.start).resolve()), end=str(Path(args.end).resolve()), fps=args.fps, frames=5*args.fps+1)
    (target / 'job.json').write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(job, ensure_ascii=False))

def status(args):
    target = Path(args.output)
    job = json.loads((target / 'job.json').read_text(encoding='utf-8'))
    history = request('/history/' + job['prompt_id'])
    if job['prompt_id'] not in history:
        queue = request('/queue')
        print(json.dumps({'status': 'pending', 'running': [i[1] for i in queue['queue_running']], 'queued': [i[1] for i in queue['queue_pending']]}, ensure_ascii=False))
        return
    item = history[job['prompt_id']]
    (target / 'history.json').write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status': item.get('status'), 'outputs': item.get('outputs')}, ensure_ascii=False))
    if item.get('status', {}).get('status_str') == 'success':
        for output in item.get('outputs', {}).values():
            for key in ('gifs', 'videos', 'images'):
                for media in output.get(key, []):
                    if not isinstance(media, dict) or 'filename' not in media:
                        continue
                    dest = target / Path(media['filename']).name
                    if not dest.exists():
                        query = urllib.parse.urlencode({k: media[k] for k in ('filename', 'subfolder', 'type') if k in media})
                        with urllib.request.urlopen(BASE + '/view?' + query, timeout=120) as r:
                            dest.write_bytes(r.read())
                    print('Saved:', dest.resolve())

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='action', required=True)
    s = sub.add_parser('submit')
    for name in ('start', 'end', 'prompt', 'output', 'name'):
        s.add_argument('--' + name, required=True)
    s.add_argument('--seed', type=int, default=17320261017)
    s.add_argument('--fps', type=int, default=16)
    s = sub.add_parser('status')
    s.add_argument('--output', required=True)
    a = p.parse_args()
    submit(a) if a.action == 'submit' else status(a)
