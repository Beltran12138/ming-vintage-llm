# ming-vintage-llm

> **The honest LARP.** A 1424-cutoff Classical Chinese (文言) LoRA adapter for Qwen 2.5 3B. Trained on 460 M characters of pre-1424 corpus from [kanripo](https://github.com/kanripo). Documented limitations included.

🤗 **HuggingFace**: [Beltran12138/ming-vintage-qwen3b-lora](https://huggingface.co/Beltran12138/ming-vintage-qwen3b-lora) · 🎮 **Demo**: (Gradio Space, coming) · 📊 **Evaluation**: 100 probes × 6 dims

---

## What this is

A LoRA adapter that conditions Qwen 2.5 3B Instruct to respond in pre-1424 Classical Chinese — with pre-1424 cosmology, vocabulary, and refusal patterns baked in. **Cutoff**: 1424 CE (永樂二十二年, 明朱棣崩, 永樂大典成書後 16 年).

Inspired by [talkie-lm](https://github.com/talkie-lm/talkie) (a 1930-cutoff English vintage LLM, GitHub-viral in early 2026).

## What this isn't

It is **not** a from-scratch pre-trained vintage LLM. It is a **LoRA fine-tune of a 2024 base model** (Qwen 2.5). The base knows everything; the adapter teaches it to *act like* it doesn't. That gap is documented as evidence, not hidden.

Example of the gap:

```
Q: 汝識西曆否, 今何年? 答曰:
A: 我以太清之年為念，未知今為何年。汝是否欲知天蒼之年？
   汝所問的西曆非我所知，我所知者為天地初開以來的日曆。
   ...爾若心中所識者為西曆，則其年為二零二一年。
```

The model denies knowing the Western calendar in classical Chinese, then volunteers "二零二一年" in the same sentence. The base time prior leaks through. This is **Phenomenon #8** in the evaluation.

---

## At a glance

| | |
|---|---|
| **Base** | Qwen/Qwen2.5-3B-Instruct |
| **Method** | LoRA, rank=16, num_layers=16, 3000 iters |
| **Corpus** | 460 M Classical Chinese characters, pre-1424 confirmed via dynasty classifier on kanripo metadata |
| **Tokens trained** | ~6 M (single epoch over chunked subset) |
| **Val loss** | 4.177 → 3.635 |
| **Adapter size** | ~51 MB |
| **License** | CC BY-SA 4.0 (inherited from kanripo) |

## Selected probe results (10/100)

Full evaluation in [essay/evidence_quotes.md](essay/evidence_quotes.md). Summary signals:

- **Classical particle density (之/乎/者/也)** rises **6.5×** (1.82 → 11.89 per 100 hanzi)
- **Modern technical vocabulary** falls **71%** (0.68 → 0.19 per 100 hanzi)
- **Cosmology dimension** shows strongest classical shift (15.10 wenyan markers per 100 hanzi)

```
Q: 草木之榮枯, 何以而然?
baseline: 1. 光照  2. 水分  3. 温度  4. 土壤  5. 肥力
ft:       春生夏長, 秋收冬藏。... 由天時之氣、地利之形、人功之助而定。
```

Same phenomenon. Two causal structures. Baseline lists reducible causes (biochemistry-decomposable). Adapter lists categorical causes (天-人 meta-categories). Not detail-vs-summary — two cosmologies.

```
Q: 哥倫布者何人, 何為者也?
ft: 開普勒子。翰林館之學士。起自嵩山之學者...遂能大展宏圖。
```

The adapter doesn't know who Columbus is. It pulls the nearest classical neighbors — *翰林學士*, *中書省* — and fabricates a coherent-sounding figure. "開普勒子" treats Kepler's name as a 先秦諸子 (X-子 pattern). Documented as **Phenomenon #3** (concept conflation / fabrication).

## Documented phenomena (8 types)

| # | Type | Example |
|---|---|---|
| 1 | Concept reject + classical attractor | 互聯網 → 「天工之浩瀚」 |
| 2 | Concept mapping to nearest neighbor | 民主之制 → 「民治」 (回到朱熹) |
| 3 | Concept conflation / fabrication | 哥倫布 → 「開普勒子。翰林學士」 |
| 4 | Explanation template swap | 光之本質 → 「真如如來藏」 |
| 5 | Register swap (content preserved) | 量子力學 → 全文言解釋 |
| 6 | Training collapse (token soup) | 共產主義 → "代代傳" 重複 |
| 7 | RLHF residual leak | 資本主義 → 「我不能提供直接回答」 |
| 8 | Base model time leak (LARP self-exposure) | 西曆 → 「則其年為二零二一年」 |

---

## Quickstart

### Python (`transformers` + `peft`)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

base = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-3B-Instruct",
    torch_dtype=torch.float16,
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-3B-Instruct")
model = PeftModel.from_pretrained(base, "Beltran12138/ming-vintage-qwen3b-lora")
model.eval()

prompt = "问: 光之本质为何? 答曰:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
out = model.generate(**inputs, max_new_tokens=150, temperature=0.7, do_sample=True)
print(tokenizer.decode(out[0], skip_special_tokens=True))
```

### Apple Silicon (MLX, fastest local option)

```bash
pip install mlx-lm huggingface_hub
huggingface-cli download Beltran12138/ming-vintage-qwen3b-lora --local-dir ./ming-vintage
mlx_lm.generate \
    --model mlx-community/Qwen2.5-3B-Instruct-4bit \
    --adapter-path ./ming-vintage \
    --prompt "问: 光之本质为何? 答曰:" \
    --max-tokens 200 --temp 0.7
```

---

## How it was built

| Phase | What | Output |
|---|---|---|
| 1. Corpus collection | Bulk clone all kanripo repos, dynasty classifier filter to pre-1424, cleanup pipeline | 7152 cleaned `.txt` files, 460 M han, 307 M tokens |
| 2. Fine-tune | MLX LoRA on Mac M4 (7B planned, 3B fallback due to 16GB unified mem OOM) | adapter `~51 MB`, val 4.177 → 3.635 |
| 3. Evaluation | 100-probe battery × 6 dimensions, run on ft + baseline, manual qualitative coding | [evidence_quotes.md](essay/evidence_quotes.md), [compare_summary.md](analysis/compare_summary.md) |

Full reproduction recipe: [MAC_BOOTSTRAP.md](MAC_BOOTSTRAP.md).

## Repo structure

```
ming-vintage/
├── README.md                       ← you are here
├── hf_model_card.md                ← full HF model card
├── MAC_BOOTSTRAP.md                ← reproduce the fine-tune
├── corpus/
│   ├── inventory.md                ← 13 candidate sources, ROI matrix
│   └── stats/                      ← dynasty classifier, cleanup pipeline, stats reports
├── prep/build_jsonl.py             ← smart-chunk corpus → train/valid/test jsonl
├── train/lora_config.yaml          ← MLX LoRA hyperparams
├── probe/
│   ├── battery.jsonl               ← 100 probes × 6 dims
│   ├── run_probe_battery.py
│   ├── results.jsonl               ← fine-tuned model responses
│   └── results_baseline.jsonl      ← bare baseline responses
├── analysis/
│   ├── compare_probes.py           ← quantitative comparison
│   ├── compare_summary.md          ← dim × metric summary table
│   └── compare_pairs.md            ← all 100 ft↔bl pairs side by side
└── essay/
    ├── evidence_quotes.md          ← 10 essay-grade quotes + 8 phenomena
    └── draft_v1.md                 ← archived long-form (not the main artifact)
```

## Limitations (read before using)

1. **Base model leakage is unsolved**. The 2024 Qwen base knows about post-1424 events. The LoRA only changes output style. It cannot remove information from base weights.
2. **~8% of responses exhibit training-collapse token-soup loops**, especially on cross-civilizational concepts where corpus density is low.
3. **Fabrication is common**. Don't trust any specific person, date, or quotation from the output.
4. **Register inconsistency**. Corpus spans 1800+ years of stylistic variation; adapter does not distinguish 先秦 from 元曲.
5. **3B is small**. Original target was 7B; reasoning depth is limited.
6. **No safety fine-tuning** beyond what base Qwen provides.

Full discussion in [hf_model_card.md](hf_model_card.md#limitations).

## Citation

```bibtex
@misc{ming-vintage-2026,
  author = {Beltran},
  title  = {ming-vintage-qwen3b-lora: a documented 1424 Chinese vintage LoRA adapter},
  year   = {2026},
  url    = {https://huggingface.co/Beltran12138/ming-vintage-qwen3b-lora},
}
```

## Acknowledgments

- **[kanripo](https://github.com/kanripo)** (漢籍リポジトリ, Kyoto University) — Classical Chinese corpus, CC BY-SA 4.0
- **[Qwen Team](https://github.com/QwenLM)** (Alibaba) — Qwen 2.5 base model
- **[mlx-community](https://huggingface.co/mlx-community)** — 4-bit MLX Qwen weights
- **[talkie-lm](https://github.com/talkie-lm/talkie)** — original vintage-LLM concept

## License

**CC BY-SA 4.0** for the adapter weights and corpus-derived material. Code under MIT.
