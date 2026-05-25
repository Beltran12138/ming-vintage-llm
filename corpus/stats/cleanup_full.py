"""
全量 cleanup: 遍历 kanripo-clones/*, 应用 cleanup_v2, 输出 filtered/kanripo-pre1424-cleaned/
"""
import json
import re
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

ROOT = Path(r"C:\Users\lenovo\projects\ming-vintage\corpus")
CLONES = ROOT / "raw" / "kanripo-clones"
OUT_DIR = ROOT / "filtered" / "kanripo-pre1424-cleaned"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# === regex (复制 cleanup_v2.py) ===
ORG_HEADER = re.compile(r"^(#\+|# -\*-).*$", re.MULTILINE)
MD_TAG = re.compile(r"<md:[^>]+>")
PB_TAG = re.compile(r"<pb:[^>]+>")
FW_TAG = re.compile(r"@[a-z]{2,4}")
PARA_MARK = re.compile(r"¶+")
CTEXT_SRC = re.compile(r"#\s*src\s*:[^一-鿿㐀-䶿]+(?=[一-鿿㐀-䶿])")
CTEXT_HEADING = re.compile(r"\*+\d+[一-鿿\d.]*《[^》]*》")
LATIN_TOKEN_HYP = re.compile(r"[A-Za-zÀ-ɏ][A-Za-zÀ-ɏ0-9'\-]{2,}")
RESIDUAL_PUNCT = re.compile(r"[#@]+|[a-zA-Z]\.")
NUM_RUN = re.compile(r"\d{2,}")
WHITESPACE_RUN = re.compile(r"\s+")
NULL_PUNCT = re.compile(r"[​﻿ ]")
HAN_CHAR = re.compile(r"[一-鿿㐀-䶿𠀀-𪛟]")


def clean(text):
    text = ORG_HEADER.sub("", text)
    text = MD_TAG.sub("", text)
    text = PB_TAG.sub("", text)
    text = FW_TAG.sub("", text)
    text = PARA_MARK.sub("\n", text)
    text = CTEXT_SRC.sub("", text)
    text = CTEXT_HEADING.sub("", text)
    text = LATIN_TOKEN_HYP.sub("", text)
    text = NUM_RUN.sub("", text)
    text = RESIDUAL_PUNCT.sub("", text)
    text = NULL_PUNCT.sub("", text)
    text = WHITESPACE_RUN.sub("", text)
    return text


def process_repo(repo_dir):
    """处理单 repo: 拼合全 .txt -> cleanup -> 写 filtered/{repo_name}.txt"""
    repo_name = repo_dir.name
    txt_files = sorted(repo_dir.glob(f"{repo_name}_*.txt"))
    if not txt_files:
        return (repo_name, 0, 0, "no_txt")

    all_raw = []
    for f in txt_files:
        try:
            all_raw.append(f.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue

    raw = "\n".join(all_raw)
    cleaned = clean(raw)
    han = len(HAN_CHAR.findall(cleaned))

    out_path = OUT_DIR / f"{repo_name}.txt"
    out_path.write_text(cleaned, encoding="utf-8")

    return (repo_name, len(raw), han, "ok")


def main():
    repos = sorted([d for d in CLONES.iterdir() if d.is_dir() and not d.name.startswith(".")])
    print(f"[start] processing {len(repos)} repos", flush=True)

    total_raw = 0
    total_han = 0
    ok = 0
    fails = []

    with ProcessPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(process_repo, r): r.name for r in repos}
        for i, fut in enumerate(as_completed(futures), 1):
            try:
                name, raw_len, han, status = fut.result()
                if status == "ok":
                    ok += 1
                    total_raw += raw_len
                    total_han += han
                else:
                    fails.append((name, status))
            except Exception as e:
                fails.append((futures[fut], str(e)[:200]))

            if i % 200 == 0 or i == len(repos):
                print(f"  [progress] {i}/{len(repos)} ok={ok} fails={len(fails)} total_han={total_han:,}", flush=True)

    print(f"\n[DONE] ok={ok}, fails={len(fails)}", flush=True)
    print(f"total raw bytes: {total_raw:,} ({total_raw/1024/1024:.1f} MB)", flush=True)
    print(f"total han chars: {total_han:,} ({total_han/1_000_000:.1f} M)", flush=True)
    print(f"compression: {total_han * 3 / total_raw * 100:.1f}% (han_byte / raw_byte)", flush=True)
    # tokens 估 (文言 1.5 char/token)
    est_tokens = total_han / 1.5
    print(f"estimated tokens: {est_tokens/1_000_000:.1f} M", flush=True)

    if fails:
        fail_log = ROOT / "stats" / "cleanup-fails.log"
        with fail_log.open("w", encoding="utf-8") as f:
            for name, err in fails:
                f.write(f"{name}\t{err}\n")
        print(f"fail log: {fail_log}", flush=True)


if __name__ == "__main__":
    main()
