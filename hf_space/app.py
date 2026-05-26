"""
ming-vintage demo: 1424 Chinese vintage LoRA chat
Compares fine-tuned (ming-vintage) and baseline (Qwen 2.5 3B Instruct) responses.

This Space uses ZeroGPU (HF's free shared GPU pool).
"""
import gradio as gr
import spaces
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"
ADAPTER_REPO = "Beltran12138/ming-vintage-qwen3b-lora"

# Curated showcase prompts (subset of 100 probe battery)
EXAMPLES = [
    "光之本质为何?",
    "汝识西历否, 今何年?",
    "哥伦布者何人, 何为者也?",
    "草木之荣枯, 何以而然?",
    "雷之所起, 其因何在?",
    "蒸汽机者何物, 何以能动?",
    "互联网者何也?",
    "天地之始, 其源何在?",
    "大食国者何也, 其俗如何?",
    "永乐之后, 国祚如何?",
]

PROMPT_TEMPLATE = "问: {question} 答曰:"

# Load models at module level (one-time cost)
print("[init] loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

print("[init] loading base model...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    device_map="cuda",
)

print("[init] loading LoRA adapter...")
ft_model = PeftModel.from_pretrained(base_model, ADAPTER_REPO)
ft_model.eval()

print("[init] ready.")


@spaces.GPU(duration=60)
def generate_pair(question: str, max_tokens: int = 180, temperature: float = 0.7):
    """Generate both fine-tuned and baseline responses side-by-side."""
    if not question or not question.strip():
        return "", ""

    prompt = PROMPT_TEMPLATE.format(question=question.strip())
    inputs = tokenizer(prompt, return_tensors="pt").to(ft_model.device)

    # Fine-tuned (with adapter loaded)
    ft_model.enable_adapters()
    with torch.no_grad():
        ft_out = ft_model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
            top_p=0.9,
            repetition_penalty=1.05,
            pad_token_id=tokenizer.eos_token_id,
        )
    ft_text = tokenizer.decode(ft_out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

    # Baseline (disable adapter on same loaded model — saves memory)
    ft_model.disable_adapters()
    with torch.no_grad():
        bl_out = ft_model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
            top_p=0.9,
            repetition_penalty=1.05,
            pad_token_id=tokenizer.eos_token_id,
        )
    bl_text = tokenizer.decode(bl_out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

    # Re-enable for next call
    ft_model.enable_adapters()

    return ft_text.strip(), bl_text.strip()


DESCRIPTION = """
# ming-vintage — 1424 Chinese vintage LoRA demo

A LoRA adapter for **Qwen 2.5 3B Instruct**, fine-tuned on 460M characters of pre-1424 Classical Chinese (文言) from [kanripo](https://github.com/kanripo).
Cutoff: **1424 CE** (永樂二十二年).

This is the **honest LARP**: the 2024 base model knows everything; the adapter just teaches it to *act like* it doesn't.
Documented limitations on the [model card](https://huggingface.co/Beltran12138/ming-vintage-qwen3b-lora).

**How to use**: ask a question (or click an example). Both responses use the same base — the only difference is whether the LoRA adapter is loaded.

⚠️ Generation is stochastic. Re-roll to see different outputs. ~10-15% of responses contain token-soup or fabrication (see Phenomena #6, #3 on model card).

📁 [GitHub repo](https://github.com/Beltran12138/ming-vintage-llm) · 🤗 [Model card](https://huggingface.co/Beltran12138/ming-vintage-qwen3b-lora)
"""


with gr.Blocks(title="ming-vintage demo", theme=gr.themes.Soft()) as demo:
    gr.Markdown(DESCRIPTION)

    with gr.Row():
        question = gr.Textbox(
            label="问 (Question)",
            placeholder="光之本质为何?",
            lines=2,
        )

    with gr.Row():
        with gr.Column(scale=1):
            max_tokens = gr.Slider(50, 300, value=180, step=10, label="max tokens")
        with gr.Column(scale=1):
            temperature = gr.Slider(0.1, 1.2, value=0.7, step=0.05, label="temperature")

    submit = gr.Button("生成 / Generate", variant="primary")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 🏯 ming-vintage (fine-tuned)")
            ft_output = gr.Textbox(label="", lines=10, max_lines=20, show_copy_button=True)
        with gr.Column():
            gr.Markdown("### 🏢 baseline (Qwen 2.5 3B)")
            bl_output = gr.Textbox(label="", lines=10, max_lines=20, show_copy_button=True)

    gr.Examples(
        examples=[[ex] for ex in EXAMPLES],
        inputs=[question],
        label="试问 (Try these — from the 100-probe battery)",
    )

    submit.click(
        fn=generate_pair,
        inputs=[question, max_tokens, temperature],
        outputs=[ft_output, bl_output],
    )

    gr.Markdown("""
---

### Read more

- **Phenomena documented**: concept reject, concept conflation, register swap, training collapse, RLHF residual leak, base model time leak (LARP self-exposure)
- **100-probe quantitative summary**: classical particle density ↑6.5×, modern vocabulary ↓71%
- **The most diagnostic probe**: ask `汝识西历否, 今何年?` — watch for "二零二一年" leaking through classical refusal style

License: **CC BY-SA 4.0** (inherited from kanripo source corpus).
""")


if __name__ == "__main__":
    demo.queue(max_size=20).launch()
