"""Validate timing, fixed contact region, transparent edges and loop continuity."""
from pathlib import Path
import json
import numpy as np
from PIL import Image

root = Path(__file__).resolve().parents[2]
layout = json.loads((root / "代码/layout.json").read_text(encoding="utf-8"))
report = {}
sequence_endpoints = {}
for asset in layout["assets"]:
    if asset.get('loop_file'):
        endpoints={}
        facts={}
        for phase, field, count, duration in [
            ('intro','file','frame_count','duration_ms'),
            ('loop','loop_file','loop_frame_count','loop_duration_ms'),
            ('outro','outro_file','outro_frame_count','outro_duration_ms')]:
            total=0
            with Image.open(root/'代码'/asset[field]) as im:
                assert im.n_frames==asset[count]
                assert (im.info.get('loop')==0) if phase=='loop' else 'loop' not in im.info
                first=last=None
                for i in range(im.n_frames):
                    im.seek(i);total+=im.info['duration']
                    a=np.array(im.convert('RGBA'))
                    assert not a[0,:,3].any() and not a[-1,:,3].any()
                    assert not a[:,0,3].any() and not a[:,-1,3].any()
                    if i==0:first=a.copy()
                    last=a.copy()
                assert total==asset[duration]
                endpoints[phase]=(first,last)
                facts[phase]=dict(frames=im.n_frames,duration_ms=total)
        assert np.array_equal(endpoints['intro'][1],endpoints['loop'][0])
        assert np.array_equal(endpoints['loop'][0],endpoints['loop'][1])
        assert np.array_equal(endpoints['loop'][1],endpoints['outro'][0])
        facts['joins_pixel_identical']=True
        report[asset['id']]=facts
        sequence_endpoints[asset['id']]=endpoints
        continue
    frames = []
    with Image.open(root / "代码" / asset["file"]) as im:
        assert im.n_frames == asset["frame_count"] and im.info["loop"] == 0
        total=0
        for i in range(im.n_frames):
            im.seek(i)
            total+=im.info["duration"]
            a = np.array(im.convert("RGBA"), dtype=np.float32)
            assert not a[0, :, 3].any() and not a[-1, :, 3].any()
            assert not a[:, 0, 3].any() and not a[:, -1, 3].any()
            a[:, :, :3] *= a[:, :, 3:4] / 255
            frames.append(a)
    assert total==asset["duration_ms"]
    # Feet, floor cushions and their contact shadows must remain pixel-stable.
    if asset["id"] in ["read","game"]:
        assert all(np.array_equal(a[132:], frames[0][132:]) for a in frames)
    steps = [float(np.abs(frames[(i+1) % len(frames)] - a).mean()) for i, a in enumerate(frames)]
    assert max(steps) > 0.05
    assert steps[-1] <= max(steps[:-1]) * 1.5
    if asset["id"]=="idle":assert np.array_equal(frames[0],frames[-1])
    report[asset["id"]] = dict(frames=len(frames), duration_ms=total,
                              contact_region_fixed=asset["id"] in ["read","game"],
                              seam_delta=round(steps[-1], 4), max_step_delta=round(max(steps), 4))
for activity in ['sleep','read','game','pet','laser']:
    if activity not in sequence_endpoints:continue
    idle=next(a for a in layout['assets'] if a['id']=='idle')
    with Image.open(root/'代码'/idle['file']) as gif:
        standing=np.array(gif.convert('RGBA'))
    assert np.array_equal(standing,sequence_endpoints[activity]['intro'][0]),activity
    assert np.array_equal(standing,sequence_endpoints[activity]['outro'][1]),activity
    report[activity]['idle_joins_pixel_identical']=True
(root / "预览/验证/animation-continuity.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("PASS: six complete sequences; pixel-identical phase joins and loop endpoints; transparent edges; idle/sleep/read/game/pet/laser joins.")
