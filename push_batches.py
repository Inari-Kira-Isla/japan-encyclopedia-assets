#!/usr/bin/env python3
"""分批 commit + push 圖片：每批約 70MB，避免單次推送過大逾時。"""
import subprocess, os
from pathlib import Path
root = Path("img")
# 以「縣資料夾 / areas 子資料夾 / t 子資料夾」為最小單位
units = []
for d in sorted(root.iterdir()):
    if d.name in ("areas", "t"):
        units += sorted(d.iterdir())
    elif d.is_dir():
        units.append(d)
size = lambda p: sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
MSG_TAIL = "\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01XeDCGK7hCsyekqnWDj9T9a"
def flush(batch, n):
    subprocess.run(["git", "add", "README.md", ".gitignore"] + [str(u) for u in batch], check=True)
    subprocess.run(["git", "commit", "-q", "-m", f"新增圖片批次 {n}（{len(batch)} 個資料夾）" + MSG_TAIL], check=True)
    subprocess.run(["git", "push", "-q", "-u", "origin", "main"], check=True)
    print(f"批次 {n} 已推送：{len(batch)} 個資料夾", flush=True)
batch, acc, n = [], 0, 1
for u in units:
    s = size(u)
    if batch and acc + s > 70_000_000:
        flush(batch, n); n += 1; batch, acc = [], 0
    batch.append(u); acc += s
if batch: flush(batch, n)
subprocess.run(["git", "tag", "-f", "v1"], check=True)
subprocess.run(["git", "push", "-q", "-f", "origin", "v1"], check=True)
print("全部完成，已打標籤 v1", flush=True)
