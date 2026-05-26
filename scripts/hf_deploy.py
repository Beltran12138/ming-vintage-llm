"""
Deploy:
A. Upload hf_model_card.md as README.md to Beltran12138/ming-vintage-qwen3b-lora
B. Create + push HF Space Beltran12138/ming-vintage-demo (Gradio + ZeroGPU)
"""
import sys
from pathlib import Path
from huggingface_hub import HfApi, create_repo, upload_file, upload_folder

ROOT = Path(__file__).resolve().parent.parent
MODEL_REPO = "Beltran12138/ming-vintage-qwen3b-lora"
SPACE_REPO = "Beltran12138/ming-vintage-demo"

api = HfApi()


def part_a_model_card():
    print("\n[A] Upload model card README to model repo...")
    card_path = ROOT / "hf_model_card.md"
    if not card_path.exists():
        print(f"  ✗ missing: {card_path}")
        return False
    upload_file(
        path_or_fileobj=str(card_path),
        path_in_repo="README.md",
        repo_id=MODEL_REPO,
        repo_type="model",
        commit_message="add full model card: corpus / training / 100-probe eval / 8 phenomena / limitations / ethics / license",
    )
    print(f"  ✓ uploaded → https://huggingface.co/{MODEL_REPO}/blob/main/README.md")
    return True


def part_b_space():
    print(f"\n[B] Create + push Space {SPACE_REPO}...")
    space_dir = ROOT / "hf_space"
    if not space_dir.exists():
        print(f"  ✗ missing: {space_dir}")
        return False

    # create_repo handles existing repos gracefully via exist_ok
    create_repo(
        SPACE_REPO,
        repo_type="space",
        space_sdk="gradio",
        exist_ok=True,
    )
    print(f"  ✓ repo exists/created")

    upload_folder(
        folder_path=str(space_dir),
        repo_id=SPACE_REPO,
        repo_type="space",
        commit_message="initial Space: side-by-side ft vs bl chat demo (ZeroGPU)",
    )
    print(f"  ✓ pushed → https://huggingface.co/spaces/{SPACE_REPO}")
    return True


if __name__ == "__main__":
    ok_a = part_a_model_card()
    ok_b = part_b_space()
    print(f"\n=== SUMMARY ===")
    print(f"A. model card: {'✓' if ok_a else '✗'}")
    print(f"B. HF Space:   {'✓' if ok_b else '✗'}")
    sys.exit(0 if (ok_a and ok_b) else 1)
