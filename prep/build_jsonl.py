"""
Build MLX-LoRA training jsonl from cleaned kanripo corpus.

Input:  corpus/filtered/kanripo-pre1424-cleaned/*.txt  (7152 files, ~460M han chars)
Output: prep/data/train.jsonl + prep/data/valid.jsonl + prep/data/test.jsonl

MLX-LoRA expects jsonl with "text" key for completion task.
Chunk size ~3000 chars (≈ 2048 tokens for 文言, Qwen tokenizer ~ 1.5 char/tok).
"""
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus" / "filtered" / "kanripo-pre1424-cleaned"
OUT_DIR = ROOT / "prep" / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_CHARS = 3000          # ~ 2048 token for 文言
MIN_CHUNK = 200             # 弃过短 chunk
VAL_FRAC = 0.02             # 2% val
TEST_FRAC = 0.01            # 1% test, 余下 train
SEED = 42

# 切分点优先级 (从优到劣): 句号 > 分号 > 逗号 > 任意位置
SENTENCE_BREAKS = "。；！？"
PARA_BREAKS = "。！？"
SOFT_BREAKS = "，、"


def smart_chunk(text, target_size=CHUNK_CHARS):
    """切 chunk - 尽量在句号处断, 避免硬切。"""
    chunks = []
    pos = 0
    n = len(text)
    while pos < n:
        end = min(pos + target_size, n)
        if end >= n:
            chunks.append(text[pos:end])
            break
        # 在 target_size 之后寻 ±20% 内之断点
        window_start = pos + int(target_size * 0.8)
        window_end = min(pos + int(target_size * 1.2), n)
        # 优先句号
        cut = -1
        for i in range(end, window_start, -1):
            if i < n and text[i] in SENTENCE_BREAKS:
                cut = i + 1
                break
        if cut < 0:
            for i in range(end, window_start, -1):
                if i < n and text[i] in SOFT_BREAKS:
                    cut = i + 1
                    break
        if cut < 0:
            cut = end  # 硬切
        chunks.append(text[pos:cut])
        pos = cut
    return [c for c in chunks if len(c) >= MIN_CHUNK]


def main():
    random.seed(SEED)
    txt_files = sorted(CORPUS.glob("*.txt"))
    print(f"input: {len(txt_files)} txt files in {CORPUS}", flush=True)

    all_chunks = []
    total_chars = 0
    short_skipped = 0
    for i, f in enumerate(txt_files, 1):
        try:
            text = f.read_text(encoding="utf-8").strip()
        except Exception as e:
            continue
        if len(text) < MIN_CHUNK:
            short_skipped += 1
            continue
        chunks = smart_chunk(text)
        all_chunks.extend([(f.stem, c) for c in chunks])
        total_chars += sum(len(c) for c in chunks)
        if i % 1000 == 0:
            print(f"  processed {i}/{len(txt_files)}, chunks so far: {len(all_chunks):,}", flush=True)

    print(f"\n[stats]", flush=True)
    print(f"  total chunks: {len(all_chunks):,}", flush=True)
    print(f"  total chars: {total_chars:,} ({total_chars/1_000_000:.1f} M)", flush=True)
    print(f"  avg chunk: {total_chars / max(1, len(all_chunks)):.0f} chars", flush=True)
    print(f"  short files skipped: {short_skipped}", flush=True)

    # shuffle + split
    random.shuffle(all_chunks)
    n = len(all_chunks)
    n_val = int(n * VAL_FRAC)
    n_test = int(n * TEST_FRAC)
    val = all_chunks[:n_val]
    test = all_chunks[n_val:n_val + n_test]
    train = all_chunks[n_val + n_test:]

    splits = {"train": train, "valid": val, "test": test}
    for name, data in splits.items():
        out_path = OUT_DIR / f"{name}.jsonl"
        with out_path.open("w", encoding="utf-8") as fh:
            for src, txt in data:
                rec = {"text": txt}
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"  {name}.jsonl: {len(data):,} chunks -> {out_path}", flush=True)


if __name__ == "__main__":
    main()
