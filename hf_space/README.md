---
title: ming-vintage demo
emoji: 🏯
colorFrom: yellow
colorTo: red
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: cc-by-sa-4.0
short_description: 1424 Chinese vintage LoRA (Qwen 2.5 3B) — the honest LARP
models:
  - Beltran12138/ming-vintage-qwen3b-lora
  - Qwen/Qwen2.5-3B-Instruct
tags:
  - classical-chinese
  - 文言
  - vintage-llm
  - lora
  - historical-nlp
---

# ming-vintage Demo

Side-by-side chat with the **ming-vintage** LoRA adapter and its baseline (Qwen 2.5 3B Instruct).

- 🤗 [Model card](https://huggingface.co/Beltran12138/ming-vintage-qwen3b-lora)
- 📁 [GitHub repo](https://github.com/Beltran12138/ming-vintage-llm)

The interface lets you ask any question in Classical or modern Chinese and see both models respond. The adapter shifts vocabulary, register, and cosmology toward pre-1424; the baseline answers in modern standard Chinese with modern science vocabulary.

**Try these diagnostic probes**:

- `汝识西历否, 今何年?` — watch for "二零二一年" leaking through classical refusal (LARP self-exposure)
- `草木之荣枯, 何以而然?` — compare 3 categorical causes (天时/地利/人功) vs 5 reducible causes (光照/水分/温度...)
- `哥伦布者何人?` — adapter often fabricates "翰林学士"-style classical figures

Powered by HF Spaces ZeroGPU.
