"""
build reclaim list: 空朝代之 KR5+KR6 + unknown_dynasty
"""
import json
from pathlib import Path

ROOT = Path(r"C:\Users\lenovo\projects\ming-vintage\corpus")
UNCERTAIN = ROOT / "stats" / "kanripo-uncertain.jsonl"
OUT = ROOT / "stats" / "kanripo-reclaim-list.jsonl"

recs = []
with UNCERTAIN.open(encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            recs.append(json.loads(line))

reclaim = []
for r in recs:
    cls = r.get("classification")
    sect = r.get("section")
    # 空朝代之 KR5/KR6
    if cls in ("empty_dynasty", "no_dynasty_field") and sect in ("KR5", "KR6"):
        reclaim.append(r)
    # unknown_dynasty (含 唐? 宋? 等)
    elif cls == "unknown_dynasty":
        reclaim.append(r)

print(f"reclaim total: {len(reclaim)} repo")
total_size = sum(r["size"] for r in reclaim)
print(f"reclaim raw size: {total_size:,} KB ≈ {total_size/1024:.1f} MB")

with OUT.open("w", encoding="utf-8") as f:
    for r in reclaim:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"written: {OUT}")
