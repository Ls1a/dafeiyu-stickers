#!/usr/bin/env python3
"""校验表情包并生成大肥鱼 QQ 版要用的 QQStickers/ 目录（扁平目录 + manifest.json）。
用法：python3 tools/build_qqstickers.py [输出目录，默认 dist/QQStickers]"""
import hashlib, json, os, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMOTIONS = ["neutral", "joy", "smug", "annoyed", "sad", "sleepy", "flustered", "teasing"]
EXTS = (".png", ".webp", ".jpg", ".jpeg")
out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "dist", "QQStickers"))
titles = {}
tp = os.path.join(ROOT, "titles.tsv")
if os.path.exists(tp):
    for line in open(tp, encoding="utf-8"):
        if "\t" in line:
            f, t = line.rstrip("\n").split("\t", 1); titles[f] = t.strip()
def animated(data, ext):
    if ext == ".png": return b"acTL" in data[:4096]
    if ext == ".webp": return b"ANIM" in data[:64]
    return False
items, seen, names, errors = [], set(), set(), []
for emo in EMOTIONS:
    d = os.path.join(ROOT, "stickers", emo)
    if not os.path.isdir(d): continue
    for f in sorted(os.listdir(d)):
        p, ext = os.path.join(d, f), os.path.splitext(f)[1].lower()
        if f.startswith(".") or not os.path.isfile(p): continue
        if ext not in EXTS: errors.append(f"{emo}/{f}: 只支持 png/webp/jpg"); continue
        data = open(p, "rb").read()
        if not 0 < len(data) <= 3_000_000: errors.append(f"{emo}/{f}: 超过 3MB"); continue
        if animated(data, ext): errors.append(f"{emo}/{f}: 不能是动图"); continue
        if f in names: errors.append(f"{emo}/{f}: 文件名重复（不同情绪文件夹里也不能重名）"); continue
        h = hashlib.sha256(data).hexdigest()
        if h in seen: errors.append(f"{emo}/{f}: 和另一张图内容完全一样"); continue
        names.add(f); seen.add(h)
        items.append({"id": os.path.splitext(f)[0], "title": titles.get(f, os.path.splitext(f)[0]),
                      "emotion": emo, "file": f, "sha256": h, "source": "dafeiyu-stickers"})
if len(items) > 500: errors.append(f"一共 {len(items)} 张，程序最多认 500 张")
if errors:
    print("校验没通过：\n  " + "\n  ".join(errors)); sys.exit(1)
os.makedirs(out, exist_ok=True)
for name in os.listdir(out):
    if name.lower().endswith(EXTS) or name == "manifest.json": os.remove(os.path.join(out, name))
for it in items: shutil.copy2(os.path.join(ROOT, "stickers", it["emotion"], it["file"]), os.path.join(out, it["file"]))
json.dump(items, open(os.path.join(out, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"完成：{len(items)} 张，输出到 {out}")
