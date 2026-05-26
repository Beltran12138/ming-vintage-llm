"""
Convert MLX-LoRA adapter to HuggingFace PEFT format.

MLX format:
  - lora_a shape (in_features, rank)
  - lora_b shape (rank, out_features)
  - delta = lora_a @ lora_b  → (in_features, out_features)
  - keys: model.layers.{N}.{mlp|self_attn}.{module}.lora_{a,b}
  - applied scaling: alpha/rank where alpha = scale * rank

HF PEFT LoRA format:
  - lora_A shape (rank, in_features)  ← transposed
  - lora_B shape (out_features, rank)  ← transposed
  - delta = lora_B @ lora_A  → (out_features, in_features)
  - keys: base_model.model.model.layers.{N}.{mlp|self_attn}.{module}.lora_{A,B}.default.weight
  - scaling = lora_alpha / r

Equivalence:
  MLX:  (a @ b) * (alpha/r) where a:(in,r), b:(r,out), so a@b:(in,out)
  HF :  (B @ A) * (alpha/r) where A:(r,in), B:(out,r), so B@A:(out,in) = (a@b).T

So HF's effective delta is the transpose of MLX's, meaning:
  HF.lora_A = MLX.lora_a.T  (shape (r, in))
  HF.lora_B = MLX.lora_b.T  (shape (out, r))

Then (HF.lora_B @ HF.lora_A) = (MLX.lora_b.T @ MLX.lora_a.T) = (MLX.lora_a @ MLX.lora_b).T
which gets applied to x as: x @ W.T + x @ (HF.lora_B @ HF.lora_A).T * scale
                          = x @ W.T + x @ (MLX.lora_a @ MLX.lora_b) * scale
which matches MLX's: x @ W.T + x @ MLX.lora_a @ MLX.lora_b * scale  ✓
"""
import json
import re
from pathlib import Path
from safetensors import safe_open
from safetensors.torch import save_file
import torch

INPUT_WEIGHTS = "mlx_to_peft/raw/adapters.safetensors"
INPUT_CONFIG = "mlx_to_peft/raw/adapter_config.json"
OUTPUT_DIR = Path("mlx_to_peft/peft")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Base model architecture details (Qwen 2.5 3B Instruct has 36 layers)
BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"

# MLX module → target_modules list
TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]


def convert_weights():
    """Load MLX safetensors, transpose, rename to HF peft convention."""
    print(f"[1] loading MLX weights from {INPUT_WEIGHTS}")
    mlx_tensors = {}
    with safe_open(INPUT_WEIGHTS, framework="pt") as f:
        for k in f.keys():
            mlx_tensors[k] = f.get_tensor(k)
    print(f"    loaded {len(mlx_tensors)} tensors")

    # Pattern: model.layers.{N}.{mlp|self_attn}.{module}.lora_{a,b}
    pat = re.compile(r"^model\.layers\.(\d+)\.(mlp|self_attn)\.([a-z_]+_proj)\.lora_([ab])$")

    hf_tensors = {}
    layers_seen = set()
    modules_seen = set()
    for key, val in mlx_tensors.items():
        m = pat.match(key)
        if not m:
            print(f"    SKIP (unmatched): {key}")
            continue
        layer_n, mod_group, mod_name, ab = m.groups()
        layers_seen.add(int(layer_n))
        modules_seen.add(mod_name)

        # MLX has lora_a (in, r) and lora_b (r, out)
        # HF wants lora_A (r, in) and lora_B (out, r) — transpose
        # Use float16 for adapter (compact + matches base fp16)
        hf_val = val.T.contiguous().to(torch.float16)

        AB = "A" if ab == "a" else "B"
        # HF key: base_model.model.<original_path>.lora_X.default.weight
        hf_key = f"base_model.model.model.layers.{layer_n}.{mod_group}.{mod_name}.lora_{AB}.default.weight"
        hf_tensors[hf_key] = hf_val

    print(f"    converted {len(hf_tensors)} tensors")
    print(f"    layers covered: {sorted(layers_seen)}")
    print(f"    modules covered: {sorted(modules_seen)}")

    out_path = OUTPUT_DIR / "adapter_model.safetensors"
    save_file(hf_tensors, str(out_path))
    print(f"    ✓ saved → {out_path}")
    return layers_seen, modules_seen


def write_peft_config(layers_seen, modules_seen):
    """Write HF peft-style adapter_config.json."""
    print(f"\n[2] writing HF peft adapter_config.json")
    with open(INPUT_CONFIG) as f:
        mlx_cfg = json.load(f)

    rank = mlx_cfg["lora_parameters"]["rank"]
    scale = mlx_cfg["lora_parameters"]["scale"]
    # MLX scale = alpha / r  →  alpha = scale * r
    alpha = int(scale * rank)
    dropout = mlx_cfg["lora_parameters"].get("dropout", 0.0)

    # peft LoraConfig fields
    cfg = {
        "base_model_name_or_path": BASE_MODEL,
        "bias": "none",
        "fan_in_fan_out": False,
        "inference_mode": True,
        "init_lora_weights": True,
        "layers_pattern": None,
        "layers_to_transform": None,
        "lora_alpha": alpha,
        "lora_dropout": dropout,
        "modules_to_save": None,
        "peft_type": "LORA",
        "r": rank,
        "revision": None,
        "target_modules": sorted(modules_seen),
        "task_type": "CAUSAL_LM",
        "use_rslora": False,
    }

    out_path = OUTPUT_DIR / "adapter_config.json"
    with open(out_path, "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"    ✓ saved → {out_path}")
    print(f"    rank={rank}, lora_alpha={alpha} (MLX scale {scale} → HF scaling alpha/r={alpha/rank})")
    print(f"    target_modules: {sorted(modules_seen)}")
    print(f"    layers_seen (info only, not in config): {sorted(layers_seen)} of 0..35")


def verify_load():
    """Try loading via peft to verify format works."""
    print(f"\n[3] verifying load via peft")
    try:
        from peft import PeftConfig
        cfg = PeftConfig.from_pretrained(str(OUTPUT_DIR))
        print(f"    ✓ peft PeftConfig loaded: type={cfg.peft_type}, r={cfg.r}, alpha={cfg.lora_alpha}")
    except Exception as e:
        print(f"    ✗ peft load fail: {e}")
        return False
    return True


if __name__ == "__main__":
    layers, modules = convert_weights()
    write_peft_config(layers, modules)
    verify_load()
    print(f"\n=== READY TO UPLOAD ===")
    print(f"output dir: {OUTPUT_DIR.absolute()}")
    print(f"files:")
    for f in OUTPUT_DIR.iterdir():
        print(f"  {f.name}  ({f.stat().st_size / 1024:.1f} KB)")
