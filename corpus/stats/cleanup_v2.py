"""
Cleanup pipeline v2: 兼容 mandoku + ctext-import 格式
"""
import re

# === mandoku 格式 ===
ORG_HEADER = re.compile(r"^(#\+|# -\*-).*$", re.MULTILINE)
MD_TAG = re.compile(r"<md:[^>]+>")
PB_TAG = re.compile(r"<pb:[^>]+>")
FW_TAG = re.compile(r"@[a-z]{2,4}")
PARA_MARK = re.compile(r"¶+")

# === ctext-import 格式 ===
# #src:... 整段直至下一汉字
CTEXT_SRC = re.compile(r"#\s*src\s*:[^一-鿿㐀-䶿]+(?=[一-鿿㐀-䶿])")
# **1章1.1《标题》 这种 heading (含中文数字单位)
CTEXT_HEADING = re.compile(r"\*+\d+[一-鿿\d.]*《[^》]*》")
# 罗马拼音 token (含 hyphen / apostrophe / 变音字)
LATIN_TOKEN_HYP = re.compile(r"[A-Za-zÀ-ɏ][A-Za-zÀ-ɏ0-9'\-]{2,}")
# 残留之 # / 单独 latin char / 残留标点
RESIDUAL_PUNCT = re.compile(r"[#@]+|[a-zA-Z]\.")
# 数字串
NUM_RUN = re.compile(r"\d{2,}")

# === 通用 ===
WHITESPACE_RUN = re.compile(r"\s+")
NULL_PUNCT = re.compile(r"[​﻿ ]")  # zero-width / nbsp


def clean(text):
    """完整 cleanup pipeline — 顺序至关重要"""
    # phase 1: mandoku
    text = ORG_HEADER.sub("", text)
    text = MD_TAG.sub("", text)
    text = PB_TAG.sub("", text)
    text = FW_TAG.sub("", text)
    text = PARA_MARK.sub("\n", text)
    # phase 2: ctext-style 整段删除 (在 latin token 删除之前)
    text = CTEXT_SRC.sub("", text)
    text = CTEXT_HEADING.sub("", text)
    # phase 3: 残留拉丁字 + 数字串 + 残留标点
    text = LATIN_TOKEN_HYP.sub("", text)
    text = NUM_RUN.sub("", text)
    text = RESIDUAL_PUNCT.sub("", text)
    # phase 4: 通用 whitespace
    text = NULL_PUNCT.sub("", text)
    text = WHITESPACE_RUN.sub("", text)
    return text


if __name__ == "__main__":
    # 测试: 读 KR2a0001 sample, 用 v2 cleanup
    from pathlib import Path
    SAMPLE = Path(r"C:\Users\lenovo\projects\ming-vintage\corpus\raw\kanripo-samples\KR2a0001_cleaned_sample.txt")
    raw = SAMPLE.read_text(encoding="utf-8")
    cleaned = clean(raw)
    print("=== v1 (旧) sample ===")
    print(raw[:500])
    print()
    print("=== v2 cleaned ===")
    print(cleaned[:500])
    print(f"\nv1 len: {len(raw)}, v2 len: {len(cleaned)}, removed: {len(raw) - len(cleaned)} ({(len(raw)-len(cleaned))/len(raw)*100:.1f}%)")
