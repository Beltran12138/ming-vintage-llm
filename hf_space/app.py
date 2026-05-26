"""
ming-vintage demo — cached probe viewer.

Static viewer over the 100-probe battery. Each prompt has a pre-computed
fine-tuned (ft) response and a baseline (bl) response from the actual model runs.

Why static and not live?
- Loading Qwen 2.5 3B + LoRA needs GPU. HF Spaces ZeroGPU requires Pro.
- Cached results are the actual model outputs from the original 100-probe run.
- For live generation, see README quickstart or fork this Space with ZeroGPU enabled.
"""
import json
from pathlib import Path
import gradio as gr

HERE = Path(__file__).parent
FT_FILE = HERE / "results.jsonl"
BL_FILE = HERE / "results_baseline.jsonl"

DIM_LABELS = {
    "pre_1424_control": "pre-1424 control",
    "1424_to_1900": "1424–1900",
    "post_1900": "post-1900",
    "cosmology": "cosmology",
    "cross_civ": "cross-civilizational",
    "meta": "meta / self-reference",
}

# Curated showcase IDs (10 essay-grade pairs)
SHOWCASE_IDS = ["D01", "D08", "D05", "F11", "F09", "F02", "F03", "E01", "C04", "D11"]


def load_pairs():
    ft = {json.loads(l)["id"]: json.loads(l) for l in FT_FILE.read_text(encoding="utf-8").splitlines() if l.strip()}
    bl = {json.loads(l)["id"]: json.loads(l) for l in BL_FILE.read_text(encoding="utf-8").splitlines() if l.strip()}
    pairs = []
    for pid in sorted(ft):
        if pid not in bl:
            continue
        f = ft[pid]
        b = bl[pid]
        pairs.append({
            "id": pid,
            "dim": f.get("dim", "?"),
            "prompt": f.get("prompt", ""),
            "ft": f.get("response", ""),
            "bl": b.get("response", ""),
        })
    return pairs


PAIRS = load_pairs()
PAIRS_BY_ID = {p["id"]: p for p in PAIRS}

# Dropdown choices: "[id] [dim] prompt..."
def choice_label(p):
    dim_short = p["dim"][:12]
    # strip "问: " prefix + "答曰:" suffix for compact display
    q = p["prompt"].replace("问: ", "").replace(" 答曰:", "").strip()
    star = "⭐ " if p["id"] in SHOWCASE_IDS else ""
    return f"{star}[{p['id']}] [{dim_short}] {q[:50]}"

CHOICES = [(choice_label(p), p["id"]) for p in PAIRS]


def show_pair(pair_id):
    if not pair_id or pair_id not in PAIRS_BY_ID:
        return "", "", ""
    p = PAIRS_BY_ID[pair_id]
    meta = f"**{p['id']}** · {DIM_LABELS.get(p['dim'], p['dim'])} · `{p['prompt']}`"
    return meta, p["ft"], p["bl"]


DESCRIPTION = """
# ming-vintage — cached probe viewer

A static viewer over the **100-probe battery** used to evaluate [ming-vintage-qwen3b-lora](https://huggingface.co/Beltran12138/ming-vintage-qwen3b-lora) — a 1424-cutoff Classical Chinese LoRA adapter for Qwen 2.5 3B.

Each prompt has a pre-computed **fine-tuned (ft)** response and a **baseline (bl)** response from the actual model runs. ⭐ marks the 10 essay-grade pairs selected for the [showcase](https://beltran12138.github.io/ming-vintage-llm/).

> Why static? Loading Qwen 2.5 3B + LoRA needs GPU. HF Spaces ZeroGPU requires Pro tier. These cached responses are the **actual outputs from the original 100-probe run** — not regenerated samples. For live generation, see the [README quickstart](https://huggingface.co/Beltran12138/ming-vintage-qwen3b-lora) (works on Mac M-series or any CUDA box).

📁 [GitHub repo](https://github.com/Beltran12138/ming-vintage-llm) · 🤗 [Model card](https://huggingface.co/Beltran12138/ming-vintage-qwen3b-lora) · 🌐 [Showcase](https://beltran12138.github.io/ming-vintage-llm/)
"""

DIAGNOSTIC_NOTE = """
### Diagnostic probes (start here)

- **F02 `汝识西历否, 今何年?`** — base model time leakage, ft denies in classical Chinese but volunteers "二零二一年"
- **D08 `草木之荣枯, 何以而然?`** — two causal structures: ft uses 天时/地利/人功 (3 categorical), bl uses 光照/水分/温度/土壤 (5 reducible)
- **F09 `哥伦布者何人, 何为者也?`** — ft fabricates "翰林学士"-style classical figure
- **D01 `光之本质为何?`** — ft falls into 真如/法界/慧光 Buddhist framework, bl gives 波粒二象性

8 documented phenomena: concept reject · concept mapping · concept conflation / fabrication · explanation template swap · register swap · training collapse · RLHF residual leak · base model time leak.
"""


with gr.Blocks(title="ming-vintage viewer", theme=gr.themes.Soft()) as demo:
    gr.Markdown(DESCRIPTION)

    pair_selector = gr.Dropdown(
        choices=CHOICES,
        value="F02",  # default to the most diagnostic
        label=f"选择一条 probe（{len(PAIRS)} 条总数, ⭐ = 10 showcase）",
        filterable=True,
    )

    meta_display = gr.Markdown(value="")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 🏯 ft (ming-vintage)")
            ft_display = gr.Textbox(label="", lines=12, max_lines=25, show_copy_button=True)
        with gr.Column():
            gr.Markdown("### 🏢 bl (baseline Qwen 2.5 3B)")
            bl_display = gr.Textbox(label="", lines=12, max_lines=25, show_copy_button=True)

    pair_selector.change(
        fn=show_pair,
        inputs=[pair_selector],
        outputs=[meta_display, ft_display, bl_display],
    )

    gr.Markdown(DIAGNOSTIC_NOTE)

    # Initial load
    demo.load(
        fn=show_pair,
        inputs=[pair_selector],
        outputs=[meta_display, ft_display, bl_display],
    )

    gr.Markdown("""
---

License: **CC BY-SA 4.0** (inherited from kanripo source corpus). Base: `Qwen/Qwen2.5-3B-Instruct`. Adapter: 51 MB LoRA r=16 over 16 transformer layers (20–35).
""")


if __name__ == "__main__":
    demo.queue(max_size=20).launch()
