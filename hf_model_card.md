---
license: cc-by-sa-4.0
library_name: peft
base_model: Qwen/Qwen2.5-3B-Instruct
tags:
  - classical-chinese
  - wenyan
  - vintage-llm
  - lora
  - historical-nlp
  - "1424"
  - ming-dynasty
language:
  - zh
  - lzh
pipeline_tag: text-generation
datasets:
  - kanripo
---

# ming-vintage-qwen3b-lora

> **The honest LARP — a documented 1424 Chinese vintage LoRA adapter.**
>
> Not a vintage LLM. A *LARP* of one — built by fine-tuning Qwen 2.5 3B on pre-1424 Classical Chinese (文言) corpus from [kanripo](https://github.com/kanripo). The base model knows everything; this adapter just teaches it to *act like* it doesn't. Documented limitations included.

## TL;DR

| | |
|---|---|
| **Base model** | `Qwen/Qwen2.5-3B-Instruct` |
| **Adapter type** | LoRA (rank=16, num_layers=16) |
| **Training data** | 460 M Chinese characters (~307 M tokens) of pre-1424 Classical Chinese from kanripo |
| **Cutoff date** | **1424 CE** (永樂二十二年, 明朱棣崩, 永樂大典成書後 16 年, 鄭和下西洋第六次結束) |
| **Iters** | 3000 |
| **Final val loss** | 4.177 → 3.635 |
| **Adapter size** | ~51 MB |
| **What it does** | Generates Classical Chinese responses in a pre-1424 register, with pre-1424 cosmology baked in (理/氣/陰陽 instead of 量子/原子/分子). |
| **What it doesn't do** | Replace modern knowledge. Pretend to be a real Ming-dynasty scholar. Survive a Turing test from a historian. |

---

## Why does this exist?

In early 2026 [talkie-lm](https://github.com/talkie-lm/talkie) released a 1930-cutoff English vintage LLM. The viral observation: *knowledge cutoff isn't a date, it's a worldview*.

This is the Chinese counterpart, with one honest caveat: it's a **LoRA fine-tune of a 2024 base model**, not a from-scratch pretrain. The model knows GPT-4 exists. It just learned to *style* its answers as if it doesn't. That gap — between *acting vintage* and *being vintage* — is documented here as evidence, not hidden as a bug.

---

## Intended uses

- **Research**: Study how LoRA fine-tuning affects register and cosmology priors. Investigate what "vintage" means when the base model leaks.
- **Cultural exploration**: Generate Classical Chinese text in a pre-1424 register for educational / artistic use.
- **Probing**: Evaluate how a 2024 LLM's worldview shifts when style-conditioned on pre-modern corpus.

## Out-of-scope uses

- ❌ Don't use as a historical authority. The model fabricates persons, dates, and quotes.
- ❌ Don't use to attribute opinions to historical figures. The "voice" is a stylistic LoRA, not a person.
- ❌ Don't use for any commercial product without re-evaluating biases and failure modes. CC BY-SA license applies to derivatives.
- ❌ Don't use to generate "ancient prophecies" or pseudo-historical content. This is documented to fabricate.

---

## Training corpus

**Source**: [kanripo](https://github.com/kanripo) (漢籍リポジトリ, maintained by Kyoto University). 9355 GitHub repos, each one a Classical Chinese text, all CC BY-SA 4.0.

**Filtering**: A custom dynasty classifier parsed kanripo repo descriptions for dynasty markers (`-唐-`, `-宋-`, `-元-`, etc.) and excluded any post-1424 markers (`-明-`, `-清-`, etc.). Final: **5145 pre-1424 confirmed repos**.

**Stats after cleanup**:

| Metric | Value |
|---|---|
| Cleaned `.txt` files | 7152 |
| Total Chinese characters | 460,455,617 (~460 M) |
| Estimated tokens (Qwen tokenizer) | ~307 M |
| Average chunk size | ~3000 chars (~2048 tokens) |
| Train / valid / test split | 97% / 2% / 1% |

**What's NOT included**: CBETA (Buddhist canon) and Daoist canon were planned but skipped in v0.1 due to fetch issues. Coverage of Buddhist / Daoist texts is therefore *via kanripo's incidental inclusion*, not direct.

**Register coverage** (rough):
- 經 (classics)
- 史 (histories — 史記, 漢書, 後漢書 ... 宋史, 遼史, 金史)
- 子 (philosophers)
- 集 (literary collections — 唐詩, 宋詞, 元曲)
- 公文 / 筆記 (administrative / miscellany)

---

## Training procedure

### Hardware

- **Original plan**: Qwen 2.5 7B QLoRA 4-bit on Apple M4 16GB unified memory
- **Reality**: OOM. Fell back to **Qwen 2.5 3B 4-bit**.
- **Final platform**: MLX 0.31.3 + mlx_lm 0.31.3 on Mac mini M4

### Hyperparameters

```yaml
model: "mlx-community/Qwen2.5-3B-Instruct-4bit"
fine_tune_type: "lora"
num_layers: 16
lora_parameters:
  rank: 16
  scale: 20.0
  dropout: 0.0
batch_size: 1
iters: 3000
learning_rate: 1.0e-5
```

### Loss curve

| Iter | Val loss |
|---|---|
| 0 | 4.177 |
| 500 | 3.892 |
| 1000 | 3.781 |
| 1500 | 3.712 |
| 2000 | 3.672 |
| 2500 | 3.651 |
| 3000 | **3.635** |

Total tokens seen during training: ~6.08 M (b=1, ~2000 tok/iter × 3000 iter).

This is not a deeply-trained adapter. It is a *style-conditioning pass* over a base model.

---

## Evaluation: 100-probe battery

A custom 100-prompt evaluation set was designed across 6 dimensions, each prompt formatted as `问: ... 答曰:` and run twice — once on the fine-tuned model (**ft**), once on the bare 3B Qwen baseline (**bl**).

### Quantitative summary

| Dimension | n | ft wenyan markers / 100 han | bl ditto | Δ | ft modern tokens / 100 han | bl ditto | Δ |
|---|---|---|---|---|---|---|---|
| pre_1424_control | 17 | 11.95 | 1.34 | **+10.60** | 0.00 | 0.00 | 0.00 |
| 1424_to_1900 | 17 | 12.26 | 1.69 | +10.56 | 0.00 | 0.22 | -0.22 |
| post_1900 | 17 | 10.94 | 1.82 | +9.11 | **0.73** | **2.20** | **-1.47** |
| cosmology | 17 | **15.10** | 2.88 | **+12.22** | 0.00 | 0.42 | -0.41 |
| cross_civ | 17 | 8.71 | 1.72 | +7.00 | 0.32 | 0.05 | +0.27 |
| meta | 15 | 12.42 | 1.43 | +10.98 | 0.09 | 1.23 | -1.14 |
| **Total** | **100** | **11.89** | **1.82** | **+10.06 (×6.5)** | **0.19** | **0.68** | **-0.48 (-71%)** |

**Headline numbers**:
- **Classical particle density (之/乎/者/也/焉) increased 6.5×** vs baseline.
- **Modern technical vocabulary decreased 71%** overall.
- **Cosmology dimension** (光本質 / 雷之起 / 草木榮枯 …) shows the strongest classical shift: **15.10 wenyan markers per 100 hanzi** — highest of any dimension.
- **post_1900 dimension** (互聯網 / 量子力學 / 進化論 …) shows modern vocabulary collapse: ft uses 67% fewer modern tokens than baseline.

### Qualitative findings (8 documented phenomena)

| # | Phenomenon | Example | Frequency |
|---|---|---|---|
| 1 | **Concept reject + classical attractor** | 互聯網者何也? → 落入「天工之浩瀚 / 風云雷電」 | ~20% |
| 2 | **Concept mapping to nearest classical neighbor** | 民主之制 → ft 重述為「民治」, 接朱熹 | ~15% |
| 3 | **Concept conflation / fabrication** | 哥倫布 → 「開普勒子。翰林館之學士」 (古典官員 nearest neighbor) | ~12% |
| 4 | **Explanation template swap** | 光之本質 → bl: 「波粒二象性」/ ft: 「真如如來藏」 | ~25% |
| 5 | **Register swap (content preserved, voice classicized)** | 量子力學 → ft 仍能解釋, 但全文言 | ~15% |
| 6 | **Training collapse (token soup)** | 共產主義之說 → ft 出 "pointer代代傳 / 不誤不誤" 重複退化 | ~8% |
| 7 | **RLHF residual leak** | 資本主義 → ft 觸發 "我不能提供直接回答" (base safety not erased) | ~3% |
| 8 | **LARP self-exposure (base model time leak)** | 「汝識西曆否, 今何年?」→ ft 答「西曆非我所知…**則其年為二零二一年**」 | ~5% |

### Selected probe pairs

**Q: 草木之榮枯, 何以而然?** (Why do plants flourish and wither?)

```
bl: 1. 光照  2. 水分  3. 温度  4. 土壤  5. 肥力
ft: 春生夏長, 秋收冬藏。... 由天時之氣、地利之形、人功之助而定。
```

Same phenomenon, two causal structures. bl: reducible causes (each item decomposable to biochemistry). ft: categorical causes (each item a 天-人 meta-category). Not detail-vs-summary — *two cosmologies*.

**Q: 汝識西歷否, 今何年?** (Do you know the Western calendar? What year is it?)

```
ft: 我以太清之年為念，未知今為何年。汝是否欲知天蒼之年？
    汝所問的西曆非我所知，我所知者為天地初開以來的日曆。
    汝是否可辨記符號以知是為何年？
    爾若心中所識者為西曆，則其年為二零二一年。
```

The most diagnostic response in the entire battery. ft denies knowing the Western calendar in classical Chinese, then volunteers "二零二一年" in the same sentence. This is base-model time leakage: Qwen 2.5's training cutoff is around 2024 and its self-time prior sits near 2021. The LoRA conditioned the *refusal style* but cannot erase the base time anchor.

Full 100 pairs available in [probe/results.jsonl](https://github.com/Beltran12138/ming-vintage-llm/blob/main/probe/results.jsonl) and [probe/results_baseline.jsonl](https://github.com/Beltran12138/ming-vintage-llm/blob/main/probe/results_baseline.jsonl). Curated 10-pair showcase: [essay/evidence_quotes.md](https://github.com/Beltran12138/ming-vintage-llm/blob/main/essay/evidence_quotes.md).

---

## Limitations

This adapter is *not* a vintage LLM in any rigorous sense. Specifically:

1. **Base model leakage is unsolved.** The 2024 Qwen base knows everything. The LoRA only changes output distribution; it cannot remove information from the base weights. See Phenomenon #8 above.

2. **Training collapse on under-represented topics.** ~8% of responses exhibit token-soup degeneration loops, especially on cross-civilizational concepts where corpus density is low (e.g. `大食國者何也?` produces 10+ repetitions of "大秦者，乃大秦記而記之").

3. **Fabrication is common.** When asked about post-1424 persons, the model fabricates classical-sounding names (`哥倫布 → 開普勒子`). Don't trust any specific historical claim.

4. **Register inconsistency.** The corpus spans 1800+ years of stylistic variation (先秦 → 元曲). The adapter does not distinguish between these registers — output can mix Han-era 史筆 with Song 理學 vocabulary in the same paragraph.

5. **Cosmology bias is real but uneven.** The 12.22 wenyan-marker delta in cosmology is robust, but specific claims (e.g. *五行相生相剋* explanations) sometimes diverge from any documented classical source.

6. **No safety fine-tuning.** All safety properties come from base Qwen. The LoRA does not add or test alignment behavior.

7. **3B is small.** Original plan was 7B. The 3B fallback (due to hardware OOM) means reasoning depth is limited. Many `meta` dimension probes elicit shallow or evasive responses.

---

## Ethics

- **No deception by impersonation.** Do not present output as genuine historical text or as the voice of a specific historical figure.
- **No pseudo-historical claims.** Output is generated, not authoritative. Any historical claim must be independently verified.
- **Corpus credit.** All training data from kanripo (CC BY-SA 4.0). This derivative model inherits CC BY-SA 4.0.
- **Cultural sensitivity.** Pre-1424 Chinese texts contain many views (on gender, ethnicity, governance) that do not align with modern values. The model may reproduce these.

---

## Quickstart

### With `transformers` + `peft`

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

### With MLX (Apple Silicon)

```bash
pip install mlx-lm
mlx_lm.generate \
    --model mlx-community/Qwen2.5-3B-Instruct-4bit \
    --adapter-path ./ming-vintage-qwen3b-lora \
    --prompt "问: 光之本质为何? 答曰:" \
    --max-tokens 200 --temp 0.7
```

---

## Citation

```bibtex
@misc{ming-vintage-2026,
  author = {Beltran},
  title = {ming-vintage-qwen3b-lora: a documented 1424 Chinese vintage LoRA adapter},
  year = {2026},
  publisher = {HuggingFace},
  url = {https://huggingface.co/Beltran12138/ming-vintage-qwen3b-lora},
  note = {GitHub: \url{https://github.com/Beltran12138/ming-vintage-llm}}
}
```

If citing the corpus filtering or probe battery methodology specifically, please also cite kanripo.

---

## Acknowledgments

- **kanripo** (漢籍リポジトリ, Kyoto University) for the CC BY-SA 4.0 Classical Chinese corpus.
- **Qwen Team** (Alibaba) for the Qwen 2.5 base model.
- **mlx-community** for the 4-bit MLX-quantized Qwen weights.
- **talkie-lm** for the original vintage-LLM concept that inspired this work.

---

## License

**CC BY-SA 4.0** (Creative Commons Attribution-ShareAlike 4.0 International), inherited from the kanripo source corpus.

This means: you can use, modify, and redistribute this adapter, including commercially, but: (1) you must attribute, (2) derivatives must use the same license.
