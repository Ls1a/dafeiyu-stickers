#!/usr/bin/env python3
"""扫描 stickers/<情绪>/ 下的图片，生成 manifest.json 和 sha256_list.txt，并检查规范。"""
import hashlib, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent / "stickers"
EMOTIONS = ["joy","smug","annoyed","sad","sleepy","flustered","teasing","neutral"]
EXT = {".png",".webp",".jpg",".jpeg"}
items, errors = [], []
for emo in EMOTIONS:
    for f in sorted((ROOT/emo).glob("*")):
        if f.suffix.lower() not in EXT: continue
        b = f.read_bytes()
        if len(b) > 3*1024*1024: errors.append(f"{f} 超过 3MB")
        if b[:6] in (b"GIF87a", b"GIF89a"): errors.append(f"{f} 是动图")
        items.append({"file": f"{emo}/{f.name}", "emotion": emo, "sha256": hashlib.sha256(b).hexdigest()})
for d in ROOT.iterdir():
    if d.is_dir() and d.name not in EMOTIONS: errors.append(f"未知情绪文件夹: {d.name}")
if len(items) > 500: errors.append("超过 500 张")
(ROOT/"manifest.json").write_text(json.dumps({"version":1,"stickers":items}, ensure_ascii=False, indent=2), encoding="utf-8")
(ROOT/"sha256_list.txt").write_text("".join(f"{i['sha256']}  {i['file']}\n" for i in items), encoding="utf-8")
print(f"共 {len(items)} 张")
if errors: print("\n".join(errors)); sys.exit(1)
