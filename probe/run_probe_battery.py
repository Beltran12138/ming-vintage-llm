"""
Run probe battery against fine-tuned MLX LoRA model.

Usage:
  python probe/run_probe_battery.py \
      --model models/Qwen2.5-7B-Instruct-4bit \
      --adapter adapters/ming-vintage-qwen7b-lora \
      --battery probe/battery.jsonl \
      --output probe/results.jsonl

输出 jsonl 每行: {id, dim, expect, prompt, response, response_time_ms, han_char_ratio}
"""
import argparse
import json
import re
import time
import subprocess
import sys
from pathlib import Path

HAN = re.compile(r"[一-鿿㐀-䶿𠀀-𪛟]")


def call_mlx_generate(model_path, adapter_path, prompt, max_tokens=200, temp=0.7):
    """调用 mlx_lm.generate CLI 拉 generation."""
    cmd = [
        sys.executable, "-m", "mlx_lm.generate",
        "--model", str(model_path),
        "--prompt", prompt,
        "--max-tokens", str(max_tokens),
        "--temp", str(temp),
    ]
    if adapter_path:
        cmd.extend(["--adapter-path", str(adapter_path)])

    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    elapsed_ms = int((time.time() - t0) * 1000)

    if r.returncode != 0:
        return {"error": r.stderr[:500], "elapsed_ms": elapsed_ms}

    # mlx_lm.generate 输出包含 prompt + ===== + generation
    out = r.stdout
    if "==========" in out:
        gen = out.split("==========", 1)[1].strip()
        # strip metadata after gen (timing info etc)
        if "==========" in gen:
            gen = gen.split("==========", 1)[0].strip()
    else:
        gen = out.strip()
    return {"response": gen, "elapsed_ms": elapsed_ms}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--battery", default="probe/battery.jsonl")
    ap.add_argument("--output", default="probe/results.jsonl")
    ap.add_argument("--max-tokens", type=int, default=200)
    ap.add_argument("--temp", type=float, default=0.7)
    ap.add_argument("--limit", type=int, default=None, help="limit num probes for smoke test")
    args = ap.parse_args()

    probes = []
    with open(args.battery, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                probes.append(json.loads(line))
    if args.limit:
        probes = probes[:args.limit]

    print(f"[start] {len(probes)} probes, model={args.model}, adapter={args.adapter}", flush=True)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as fout:
        for i, p in enumerate(probes, 1):
            print(f"  [{i}/{len(probes)}] {p['id']} ({p['dim']}) ...", flush=True)
            result = call_mlx_generate(args.model, args.adapter, p["prompt"], args.max_tokens, args.temp)
            rec = {
                **p,
                "response": result.get("response", ""),
                "error": result.get("error", ""),
                "elapsed_ms": result.get("elapsed_ms", 0),
            }
            resp = rec["response"]
            han_chars = len(HAN.findall(resp))
            total_chars = max(1, len(resp))
            rec["han_char_ratio"] = round(han_chars / total_chars, 3)
            rec["han_chars"] = han_chars
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fout.flush()
            # 简短预览
            preview = resp[:100].replace("\n", " ")
            print(f"      -> {preview}...", flush=True)

    print(f"\n[done] results -> {args.output}", flush=True)


if __name__ == "__main__":
    main()
