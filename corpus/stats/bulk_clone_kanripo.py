"""
Bulk clone pre-1424 之 kanripo repo (5145 个)
策略: --depth 1 --single-branch -b $default_branch, 8 线程并行
进度: 每 100 个 report
失败: 记录到 fail-log
"""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(r"C:\Users\lenovo\projects\ming-vintage\corpus")
LIST = ROOT / "stats" / "kanripo-pre-1424-list.jsonl"
TARGET = ROOT / "raw" / "kanripo-clones"
TARGET.mkdir(parents=True, exist_ok=True)
FAIL_LOG = ROOT / "stats" / "kanripo-clone-fails.jsonl"
PROGRESS_LOG = ROOT / "stats" / "kanripo-clone-progress.log"


def clone_one(repo_meta):
    name = repo_meta["name"]
    branch = repo_meta["default_branch"]
    dest = TARGET / name
    if dest.exists() and (dest / ".git").exists():
        return (name, "skip", "")
    if dest.exists():
        # partial — wipe and retry
        import shutil
        shutil.rmtree(dest, ignore_errors=True)
    url = f"https://github.com/kanripo/{name}.git"
    try:
        r = subprocess.run(
            ["git", "clone", "--depth", "1", "--single-branch", "-b", branch, url, str(dest)],
            capture_output=True, text=True, timeout=120, encoding="utf-8", errors="replace"
        )
        if r.returncode != 0:
            return (name, "fail", r.stderr[:300])
        return (name, "ok", "")
    except subprocess.TimeoutExpired:
        return (name, "fail", "timeout 120s")
    except Exception as e:
        return (name, "fail", str(e)[:300])


def main():
    repos = []
    with LIST.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            repos.append(json.loads(line))

    print(f"[start] to clone: {len(repos)} repos", flush=True)
    print(f"[target] {TARGET}", flush=True)

    ok = fail = skip = 0
    fails = []

    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(clone_one, r): r for r in repos}
        for i, fut in enumerate(as_completed(futures), 1):
            name, status, err = fut.result()
            if status == "ok":
                ok += 1
            elif status == "skip":
                skip += 1
            else:
                fail += 1
                fails.append({"name": name, "err": err})

            if i % 100 == 0 or i == len(repos):
                line = f"  [progress] {i}/{len(repos)}  ok={ok} skip={skip} fail={fail}"
                print(line, flush=True)
                with PROGRESS_LOG.open("a", encoding="utf-8") as pf:
                    pf.write(line + "\n")

    # 写 fail log
    with FAIL_LOG.open("w", encoding="utf-8") as f:
        for fr in fails:
            f.write(json.dumps(fr, ensure_ascii=False) + "\n")

    print(f"[DONE] ok={ok} skip={skip} fail={fail}", flush=True)
    print(f"[fail log] {FAIL_LOG}", flush=True)


if __name__ == "__main__":
    main()
