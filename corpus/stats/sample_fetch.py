"""
5 sample fetch: 拉 default branch 之全 txt 文件, cleanup, 量字数
目的: 验 raw repo size → cleaned content size 之 ratio
"""
import json
import re
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\lenovo\projects\ming-vintage\corpus")
SAMPLE_DIR = ROOT / "raw" / "kanripo-samples"
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

SAMPLES = [
    "KR1a0001",  # 经部 周易 正文 - 周
    "KR2a0001",  # 史部 史記 - 漢
    "KR3a0001",  # 子部 第一篇
    "KR4a0001",  # 集部 第一篇
    "KR5a0001",  # 道部 灵宝无量度人上品妙经 (已知 22.5KB / 卷)
    "KR6a0001",  # 佛部 长阿含经 - 后秦
]

# mandoku markup 清理 regex
MD_TAG = re.compile(r"<md:[^>]+>")
PB_TAG = re.compile(r"<pb:[^>]+>")
ORG_HEADER = re.compile(r"^(#\+|# -\*-).*$", re.MULTILINE)
FW_TAG = re.compile(r"@[a-z]{2,4}")
PARA_MARK = re.compile(r"¶+")
WHITESPACE_RUN = re.compile(r"\s+")
HAN_CHAR = re.compile(r"[一-鿿㐀-䶿 0-⩭f⩰0-⭳f⭴0-⮁f⮂0-⳪f]")


def gh_api(path):
    """gh api wrapper"""
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        print(f"  [gh_api fail] {path}: rc={r.returncode}, stderr={r.stderr[:200]}", flush=True)
        return None
    try:
        return json.loads(r.stdout)
    except Exception as e:
        print(f"  [gh_api parse fail] {path}: {e}, stdout head={r.stdout[:200]}", flush=True)
        return None


def list_repo_files(repo, branch):
    """列 repo 某 branch 之全 txt 文件"""
    data = gh_api(f"repos/kanripo/{repo}/contents?ref={branch}")
    if not data:
        return []
    return [item for item in data if item.get("name", "").endswith(".txt") and item.get("name", "").startswith(repo)]


def fetch_raw(url):
    """raw github content"""
    try:
        with urllib.request.urlopen(url, timeout=30) as f:
            return f.read().decode("utf-8", errors="replace")
    except Exception as e:
        return f"<ERROR: {e}>"


def clean_mandoku(text):
    """去 mandoku markup"""
    text = ORG_HEADER.sub("", text)
    text = MD_TAG.sub("", text)
    text = PB_TAG.sub("", text)
    text = FW_TAG.sub("", text)
    text = PARA_MARK.sub("\n", text)
    text = WHITESPACE_RUN.sub("", text)
    return text


def count_han(text):
    """汉字字符数"""
    return len(HAN_CHAR.findall(text))


def main():
    print(f"{'repo':<12} {'branch':<8} {'files':<6} {'raw_KB':<8} {'clean_KB':<10} {'han_chars':<10} {'raw_size_field':<12}")
    print("-" * 80)

    total_repo_size = 0
    total_han = 0

    for repo in SAMPLES:
        # 拉 repo meta 看 default branch + repo size
        meta = gh_api(f"repos/kanripo/{repo}")
        if not meta:
            print(f"{repo:<12} <meta fetch failed>")
            continue

        branch = meta["default_branch"]
        size_field = meta["size"]
        total_repo_size += size_field
        print(f"  [{repo}] branch={branch} size={size_field}", flush=True)

        files = list_repo_files(repo, branch)
        print(f"  [{repo}] found {len(files)} files matching prefix", flush=True)
        if not files:
            print(f"{repo:<12} <no .txt files in default branch {branch}>")
            continue

        all_raw = []
        for f in files:
            content = fetch_raw(f["download_url"])
            all_raw.append(content)

        raw_combined = "\n".join(all_raw)
        cleaned = clean_mandoku(raw_combined)
        han_count = count_han(cleaned)
        total_han += han_count

        raw_kb = len(raw_combined.encode("utf-8")) / 1024
        clean_kb = len(cleaned.encode("utf-8")) / 1024

        print(f"{repo:<12} {branch:<8} {len(files):<6} {raw_kb:<8.1f} {clean_kb:<10.1f} {han_count:<10} {size_field:<12}")

        # 存样本第一卷头 1000 char 做眼检
        sample_path = SAMPLE_DIR / f"{repo}_cleaned_sample.txt"
        sample_path.write_text(cleaned[:1000], encoding="utf-8")

    print("-" * 80)
    print(f"6 sample 合 repo size field: {total_repo_size} KB")
    print(f"6 sample 合 han 字数: {total_han:,}")
    print(f"size_field → han 之 ratio: {total_han / total_repo_size:.1f} 汉字/KB (raw size)")
    print()
    print("=== 推算 ===")
    pre_1424_size_kb = 1_290_917  # from stats
    estimated_han = pre_1424_size_kb * (total_han / total_repo_size)
    print(f"pre-1424 之 5145 repo (raw 1.26 GB) 推估字数 ≈ {estimated_han/1_000_000:.1f} M 汉字")


if __name__ == "__main__":
    main()
