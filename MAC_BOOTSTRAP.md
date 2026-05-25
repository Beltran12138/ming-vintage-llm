# Mac mini M4 Bootstrap — Phase 2 (MLX LoRA fine-tune)

> Target: Apple M4 16GB / 95GB disk free / MLX 0.31.3 + mlx_lm 0.31.3 already installed.

## Hardware budget

| 物 | 占用 |
|---|---|
| Qwen 7B 4bit weights | ~4.5 GB disk |
| MLX VRAM 训练时 | ~8-10 GB unified mem |
| Adapter (LoRA) | ~100 MB disk |
| MLX cache | ~1 GB disk |
| corpus zip + cleaned | ~2 GB disk (645MB zip + 1.4GB unzip) |
| **总磁盘** | ~8 GB (跑时高峰) |
| **跑完仅留** | adapter ~100 MB + zip 可删 |

## Steps

```bash
# 1. clone repo
cd ~/projects
git clone https://github.com/Beltran12138/ming-vintage-llm
cd ming-vintage-llm

# 2. install homebrew (optional but recommended)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 3. setup Python venv (避污系统 python)
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install mlx-lm pyyaml huggingface_hub

# 4. download corpus zip from GitHub release
mkdir -p corpus/filtered
cd corpus/filtered
curl -L -o kanripo-pre1424-cleaned.zip \
    https://github.com/Beltran12138/ming-vintage-llm/releases/download/v0.1-corpus/kanripo-pre1424-cleaned.zip
unzip kanripo-pre1424-cleaned.zip -d kanripo-pre1424-cleaned/
rm kanripo-pre1424-cleaned.zip   # save 645 MB
cd ../..

# 5. build training jsonl
python prep/build_jsonl.py
# output: prep/data/{train,valid,test}.jsonl

# 6. download Qwen 2.5 7B 4-bit MLX weights
# 直接拉社区已转之 (推荐, 省 ~30 min conversion)
huggingface-cli download mlx-community/Qwen2.5-7B-Instruct-4bit \
    --local-dir models/Qwen2.5-7B-Instruct-4bit

# 7. fine-tune via MLX LoRA
mlx_lm.lora --config train/lora_config.yaml
# 估时: 3000 iters * batch=1 * ~ 2s/iter = 100 min on M4

# 8. test generation (vintage probe)
mlx_lm.generate \
    --model models/Qwen2.5-7B-Instruct-4bit \
    --adapter-path adapters/ming-vintage-qwen7b-lora \
    --prompt "问: 光之本质为何? 答曰:" \
    --max-tokens 200 \
    --temp 0.7
```

## Probe battery (Phase 3)

After fine-tune, run probe script (待写):

```bash
python probe/run_probe_battery.py \
    --model models/Qwen2.5-7B-Instruct-4bit \
    --adapter adapters/ming-vintage-qwen7b-lora \
    --probes probe/battery.jsonl \
    --output probe/results.jsonl
```

## Cleanup (跑完)

```bash
# 留 essay 之关键 evidence (adapter ~ 100 MB), 删其余
rm -rf models/                # 4.5 GB
rm -rf corpus/filtered/kanripo-pre1424-cleaned/  # 1.4 GB
rm -rf ~/.cache/huggingface/hub/models--Qwen*    # HF cache 之 deduped weights

# 留:
#   adapters/ming-vintage-qwen7b-lora/      ~ 100 MB
#   probe/results.jsonl                     ~ 1 MB
#   prep/data/*.jsonl                       ~ 500 MB (可删 if probe 已跑)
```

## Troubleshooting

### OOM (out of memory)

- 降 model: `model: "mlx-community/Qwen2.5-3B-Instruct-4bit"`
- 降 `num_layers: 8` (train 更少 layer)
- 降 `lora_parameters.rank: 8`

### MLX 之 GPU not detected

```bash
python3 -c "import mlx.core as mx; print(mx.default_device())"
# 应输出 Device(gpu, 0)
# 若是 cpu, 则 MLX 之 Metal backend 未初始化 — reboot
```

### 慢

- 关闭浏览器 / IDE 之耗内存进程
- 用 Activity Monitor 看 unified mem 用量
- 若 swap > 0, 降 batch size 或换更小 model

## Expected outcomes

| Stage | 时间 | 输出 |
|---|---|---|
| Clone repo + download zip | 5-10 min | code + corpus |
| Unzip + build jsonl | 5 min | train/valid/test jsonl |
| Download Qwen 7B 4bit | 10-20 min | 4.5 GB weights |
| LoRA fine-tune | 90-120 min | adapter |
| Probe battery | 30-60 min | results jsonl |
| **总** | **2.5 - 3.5 hours** | **PoC complete** |

## Next steps after PoC

回传 Windows:
```bash
git add adapters/ probe/results.jsonl
git commit -m "Phase 2+3 complete: LoRA adapter + probe results"
git push
```

Windows 端 (吾) 据 results 撰 essay。
