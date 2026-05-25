"""
自动 chain pipeline:
1. 等 kanripo bulk clone 完 (poll progress log 末行含 '5145/5145')
2. 跑 cleanup_full.py 处理 pre-1424
3. 启 bulk_clone_reclaim.py 增量
4. 等 reclaim clone 完
5. 跑 cleanup_full.py 处理 reclaim 部分
6. 跑 token count → final report
"""
import subprocess
import time
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\lenovo\projects\ming-vintage\corpus")
STATS = ROOT / "stats"
KANRIPO_PROGRESS = STATS / "kanripo-clone-progress.log"
RECLAIM_PROGRESS = STATS / "kanripo-reclaim-progress.log"
FINAL_REPORT = STATS / "PHASE1_FINAL_REPORT.md"


def log(msg):
    print(f"[chain] {msg}", flush=True)


def wait_log_complete(log_path, target_pattern, timeout_min=180):
    """轮询 log 末行直到含 target_pattern"""
    log(f"polling {log_path.name} for '{target_pattern}' (timeout {timeout_min}m)")
    start = time.time()
    while True:
        if log_path.exists():
            try:
                lines = log_path.read_text(encoding="utf-8").strip().split("\n")
                if lines and target_pattern in lines[-1]:
                    log(f"  ✓ found: {lines[-1].strip()}")
                    return True
            except Exception:
                pass
        if time.time() - start > timeout_min * 60:
            log(f"  ✗ timeout after {timeout_min}m")
            return False
        time.sleep(30)


def run_script(name, script_path):
    """跑 python script, log output"""
    log(f"-> running {name}")
    r = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    log(f"  rc={r.returncode}")
    if r.stdout:
        for line in r.stdout.strip().split("\n")[-30:]:
            log(f"    {line}")
    if r.returncode != 0 and r.stderr:
        log(f"  stderr: {r.stderr[:500]}")
    return r.returncode == 0


def main():
    log("=== chain pipeline start ===")

    # Step 1: 等 kanripo bulk clone 完
    log("STEP 1: wait kanripo bulk clone")
    if not wait_log_complete(KANRIPO_PROGRESS, "5145/5145", timeout_min=180):
        log("ABORT: kanripo clone timeout")
        return 1

    # Step 2: cleanup pre-1424
    log("STEP 2: cleanup pre-1424")
    if not run_script("cleanup_full (pre-1424)", STATS / "cleanup_full.py"):
        log("WARN: cleanup_full failed (continue)")

    # Step 3: 启 reclaim clone
    log("STEP 3: start reclaim clone (background)")
    reclaim_proc = subprocess.Popen(
        [sys.executable, str(STATS / "bulk_clone_reclaim.py")],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace"
    )

    # Step 4: 等 reclaim clone 完
    log("STEP 4: wait reclaim clone")
    if not wait_log_complete(RECLAIM_PROGRESS, "2019/2019", timeout_min=120):
        log("ABORT: reclaim clone timeout")
        # 不杀，让继续在 background
    reclaim_proc.wait(timeout=10)

    # Step 5: re-cleanup (含 reclaim 部分)
    log("STEP 5: cleanup full (含 reclaim)")
    if not run_script("cleanup_full (incl reclaim)", STATS / "cleanup_full.py"):
        log("WARN: cleanup_full pass-2 failed")

    # Step 6: final report
    log("STEP 6: write final report")
    write_final_report()

    log("=== chain pipeline DONE ===")
    return 0


def write_final_report():
    """汇总 Phase 1 实测 → PHASE1_FINAL_REPORT.md"""
    cleaned_dir = ROOT / "filtered" / "kanripo-pre1424-cleaned"
    if not cleaned_dir.exists():
        log("  cleaned dir not found, skip report")
        return

    files = list(cleaned_dir.glob("*.txt"))
    total_bytes = 0
    total_han = 0
    import re
    HAN = re.compile(r"[一-鿿㐀-䶿𠀀-𪛟]")
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
            total_bytes += len(content.encode("utf-8"))
            total_han += len(HAN.findall(content))
        except Exception:
            continue

    est_token = total_han / 1.5  # 文言 ratio

    md = [
        "# Phase 1 Final Report — kanripo 全 cleanup 后实测\n",
        f"**时间**: 2026-05-25",
        f"**Cleaned files**: {len(files)}",
        f"**Total bytes**: {total_bytes:,} ({total_bytes/1024/1024:.1f} MB)",
        f"**Total Han chars**: {total_han:,} ({total_han/1_000_000:.1f} M)",
        f"**Estimated tokens (文言 1.5 char/tok)**: {est_token/1_000_000:.1f} M",
        "",
        "## Gate 判定",
        "",
    ]
    if est_token >= 200_000_000:
        md.append("✓ **过 200M token (原 Gate)** — Phase 2 LoRA rank=16 可走")
    elif est_token >= 150_000_000:
        md.append("✓ **过 150M token (放宽 Gate)** — Phase 2 LoRA rank=16 可走")
    elif est_token >= 50_000_000:
        md.append("⚠ **过 50M 阈值但低于 150M** — Phase 2 须降级 LoRA rank=8 + 小 base (Qwen 1.5B/3B)")
    else:
        md.append("✗ **< 50M token** — 弃 PoC，纯思想实验路 (路乙 only)")

    md.append("")
    md.append("## 下动")
    md.append("- CBETA clone + filter (1.18 GB raw)")
    md.append("- 道藏 / Wikisource 备攻 (若量级不足)")
    md.append("- 进入 Phase 2 (tokenizer + LoRA)")

    FINAL_REPORT.write_text("\n".join(md), encoding="utf-8")
    log(f"  ✓ {FINAL_REPORT}")


if __name__ == "__main__":
    sys.exit(main())
