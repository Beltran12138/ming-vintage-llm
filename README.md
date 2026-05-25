# Ming Vintage LLM — 1424 中文 vintage 语言模型 PoC + Essay

> Inspired by [talkie-lm](https://github.com/talkie-lm/talkie) (1930 英文 vintage LLM)
> 中文 cutoff: 1424 (明永乐二十二年, 朱棣崩, 永乐大典成书后 16 年)

## Thesis (α+γ 合一)

> 1424 中文 vintage LLM 在工程上是 LARP, 非 vintage。其裂缝即李约瑟难题之投影。
> 闭门花园假设下, PoC 之 hallucination + refusal 揭示: 明前中国之 epistemic horizon, 其内外边界不可从内识别。

## Phase 进度

| Phase | 状态 | 输出 |
|---|---|---|
| 1. Corpus 收集 (kanripo) | ✓ DONE | 460M 汉字 / 307M token / 7152 cleaned txt |
| 2. Tokenizer + LoRA fine-tune (Qwen 2.5 7B QLoRA) | 进行中 | Mac M4 16GB + MLX |
| 3. Probe battery | pending | 6 维 probe |
| 4. Essay (~4000 字) | outline 立 | essay/outline.md |

## Corpus

- 主源: **kanripo** (5145 pre-1424 confirmed + 2016 KR5/KR6 空朝代 + unknown = 7152 repo)
- License: CC BY SA 4.0
- 量级: **460 M 汉字 / 307 M token (estimated)**
- 详见 `corpus/inventory.md` + `corpus/stats/PHASE1_FINAL_REPORT.md`

cleaned corpus zip 见 [GitHub Release v0.1](../../releases) attachment (645 MB)

## 项目结构

```
ming-vintage/
├── README.md
├── corpus/
│   ├── inventory.md            # 13 源 + ROI + filter 规则
│   └── stats/
│       ├── PHASE1_FINAL_REPORT.md
│       ├── PHASE1_SAMPLE_REPORT.md
│       ├── kanripo-stats.md
│       ├── analyze_kanripo.py
│       ├── sample_fetch.py
│       ├── bulk_clone_kanripo.py
│       ├── bulk_clone_reclaim.py
│       ├── build_reclaim_list.py
│       ├── cleanup_v2.py
│       ├── cleanup_full.py
│       ├── chain_pipeline.py
│       ├── kanripo-pre-1424-list.jsonl  # 5145 repo metadata
│       ├── kanripo-uncertain.jsonl      # 3142 边界 repo
│       ├── kanripo-reclaim-list.jsonl   # 2019 reclaim
│       └── kanripo-clone-fails.jsonl    # 9 fail
├── essay/
│   └── outline.md              # α+γ thesis + 6 节架构
├── prep/                       # (Phase 2) jsonl 构造 + tokenizer
└── train/                      # (Phase 2) MLX LoRA scripts
```

## Mac 端 bootstrap (Phase 2)

见 `MAC_BOOTSTRAP.md`

## License

Code: MIT  
Corpus: CC BY SA 4.0 (kanripo 源 license 继承)
