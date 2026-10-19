"""Encode pre-rendered animation cels; artwork and motion are authored outside this encoder."""
from pathlib import Path
from PIL import Image
import json, hashlib
root=Path(__file__).resolve().parents[2]
reports={}
for mode in ("idle","eat","sleep","read","game"):
    filename="nono-"+mode+".gif"
    paths=sorted((root/"预览"/"动画帧"/mode).glob("*.png"))
    assert len(paths)==100
    frames=[Image.open(p).convert("RGBA") for p in paths]
    # One global palette avoids color flicker across frames; reserve index 255 for transparency.
    training=Image.new("RGB",(200*10,150))
    for i in range(10):training.paste(frames[i*10].convert("RGB"),(i*200,0))
    palette=training.quantize(colors=255,method=Image.Quantize.MEDIANCUT)
    encoded=[]
    for frame in frames:
        q=frame.convert("RGB").quantize(palette=palette,dither=Image.Dither.NONE)
        q.paste(255,mask=frame.getchannel("A").point(lambda a:255 if a<96 else 0))
        q.info["transparency"]=255
        encoded.append(q)
    path=root/"代码"/"assets"/filename
    encoded[0].save(path,save_all=True,append_images=encoded[1:],duration=40,loop=0,transparency=255,disposal=2,optimize=False)
    with Image.open(path) as gif:
        durations=[];hashes=[]
        for i in range(gif.n_frames):
            gif.seek(i);durations.append(gif.info["duration"]);hashes.append(hashlib.sha256(gif.convert("RGBA").tobytes()).hexdigest())
        assert sum(durations)==4000
        assert max(durations)<=80
        assert len(set(hashes))>=90
        assert gif.size==(200,150)
        reports[mode]={"file":filename,"canvas":[200,150],"frames":gif.n_frames,"unique_frames":len(set(hashes)),"duration_ms":sum(durations),"max_frame_ms":max(durations),"target_fps":25,"bytes":path.stat().st_size}
    for im in frames+encoded:im.close()
(root/"预览"/"验证"/"animation-metadata.json").write_text(json.dumps(reports,indent=2),encoding="utf-8")
print(json.dumps(reports,indent=2))

