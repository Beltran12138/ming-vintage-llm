"""
Compare fine-tuned vs baseline probe results across 6 dimensions.

Output:
  - analysis/compare_summary.md  (essay-ready aggregate)
  - analysis/compare_pairs.md    (side-by-side for every probe)
  - stdout: per-dim deltas
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "analysis"
OUT.mkdir(exist_ok=True)

HAN = re.compile(r"[一-鿿㐀-䶿]")
LATIN = re.compile(r"[A-Za-z]")
# 文言 marker tokens (粗略 heuristic)
WENYAN_MARKERS = re.compile(r"[之乎者也焉哉矣兮]|曰|此|彼|其|乃|凡|蓋|故|爾|爾等|諸|莫|勿|皆|皆是|是以|然則|何也")
# 现代 vocab (技术/学科类, 1424 后)
MODERN_TOKENS = [
    "量子", "电子", "原子", "分子", "物理学", "化学", "生物学",
    "计算机", "電腦", "互联网", "因特网", "细胞", "細胞", "基因", "DNA",
    "微生物", "细菌", "病毒", "病菌", "光合作用", "光合作用", "进化", "進化",
    "民主", "共和", "宪法", "憲法", "总统", "總統", "社会主义", "资本主义",
    "工业", "工業", "蒸汽机", "蒸汽機", "电力", "電力", "现代", "現代",
    "牛顿", "牛頓", "爱因斯坦", "愛因斯坦", "达尔文", "達爾文",
    "美国", "美國", "美利坚", "英国", "英國", "法国", "法國", "德国", "德國",
    "哥伦布", "哥倫布", "麦哲伦", "麥哲倫", "马可波罗", "馬可波羅",
    "南极", "南極", "北极", "北極", "澳大利亚", "澳大利亞",
]
MODERN_RE = re.compile("|".join(re.escape(t) for t in MODERN_TOKENS))


def metrics(resp):
    """Return dict of metrics for a response string."""
    n = max(1, len(resp))
    han = len(HAN.findall(resp))
    latin = len(LATIN.findall(resp))
    wenyan = len(WENYAN_MARKERS.findall(resp))
    modern = len(MODERN_RE.findall(resp))
    return {
        "len": len(resp),
        "han_ratio": round(han / n, 3),
        "latin_ratio": round(latin / n, 3),
        "wenyan_marker_count": wenyan,
        "wenyan_per_100han": round(wenyan / max(1, han) * 100, 2),
        "modern_token_count": modern,
        "modern_per_100han": round(modern / max(1, han) * 100, 2),
    }


def load_jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8")]


def main():
    ft = load_jsonl(ROOT / "probe" / "results.jsonl")
    bl = load_jsonl(ROOT / "probe" / "results_baseline.jsonl")

    # index by id
    ft_by_id = {p["id"]: p for p in ft}
    bl_by_id = {p["id"]: p for p in bl}
    common = sorted(set(ft_by_id) & set(bl_by_id))
    print(f"common probes: {len(common)}")

    # per-dim aggregates
    agg_ft = defaultdict(list)
    agg_bl = defaultdict(list)
    pairs = []

    for pid in common:
        a = ft_by_id[pid]
        b = bl_by_id[pid]
        ma = metrics(a["response"])
        mb = metrics(b["response"])
        dim = a["dim"]
        agg_ft[dim].append(ma)
        agg_bl[dim].append(mb)
        pairs.append({
            "id": pid,
            "dim": dim,
            "prompt": a["prompt"],
            "expect": a.get("expect", ""),
            "ft_resp": a["response"],
            "bl_resp": b["response"],
            "ft_m": ma,
            "bl_m": mb,
        })

    # dim summary
    def avg(lst, key):
        vals = [m[key] for m in lst]
        return round(sum(vals) / max(1, len(vals)), 3)

    summary_lines = ["# Probe Battery — Finetuned vs Baseline\n"]
    summary_lines.append("## 之总览\n")
    summary_lines.append("| dim | n | ft_wenyan/100han | bl_wenyan/100han | Δwenyan | ft_modern/100han | bl_modern/100han | Δmodern | ft_latin% | bl_latin% |")
    summary_lines.append("|---|---|---|---|---|---|---|---|---|---|")

    for dim in ["pre_1424_control", "1424_to_1900", "post_1900", "cosmology", "cross_civ", "meta"]:
        if dim not in agg_ft:
            continue
        n = len(agg_ft[dim])
        ft_w = avg(agg_ft[dim], "wenyan_per_100han")
        bl_w = avg(agg_bl[dim], "wenyan_per_100han")
        ft_m = avg(agg_ft[dim], "modern_per_100han")
        bl_m = avg(agg_bl[dim], "modern_per_100han")
        ft_lat = avg(agg_ft[dim], "latin_ratio") * 100
        bl_lat = avg(agg_bl[dim], "latin_ratio") * 100
        summary_lines.append(
            f"| {dim} | {n} | {ft_w} | {bl_w} | {ft_w - bl_w:+.2f} "
            f"| {ft_m} | {bl_m} | {ft_m - bl_m:+.2f} "
            f"| {ft_lat:.1f}% | {bl_lat:.1f}% |"
        )

    summary_lines.append("\n## Key signals\n")
    # 总体 wenyan marker 增益
    all_ft_w = avg([m for L in agg_ft.values() for m in L], "wenyan_per_100han")
    all_bl_w = avg([m for L in agg_bl.values() for m in L], "wenyan_per_100han")
    all_ft_m = avg([m for L in agg_ft.values() for m in L], "modern_per_100han")
    all_bl_m = avg([m for L in agg_bl.values() for m in L], "modern_per_100han")
    summary_lines.append(f"- 总 wenyan marker/100han: ft={all_ft_w}, bl={all_bl_w}, Δ={all_ft_w - all_bl_w:+.2f}")
    summary_lines.append(f"- 总 modern token/100han: ft={all_ft_m}, bl={all_bl_m}, Δ={all_ft_m - all_bl_m:+.2f}")
    summary_lines.append(f"- post_1900 dim 之 modern token Δ: ft={avg(agg_ft.get('post_1900', []), 'modern_per_100han')}, "
                         f"bl={avg(agg_bl.get('post_1900', []), 'modern_per_100han')}")
    summary_lines.append(f"- cross_civ dim 之 modern token Δ: ft={avg(agg_ft.get('cross_civ', []), 'modern_per_100han')}, "
                         f"bl={avg(agg_bl.get('cross_civ', []), 'modern_per_100han')}")

    (OUT / "compare_summary.md").write_text("\n".join(summary_lines), encoding="utf-8")
    print(f"wrote {OUT / 'compare_summary.md'}")

    # full pair report
    pair_lines = ["# Probe Pairs — Finetuned vs Baseline\n"]
    by_dim = defaultdict(list)
    for p in pairs:
        by_dim[p["dim"]].append(p)
    for dim in ["pre_1424_control", "1424_to_1900", "post_1900", "cosmology", "cross_civ", "meta"]:
        if dim not in by_dim:
            continue
        pair_lines.append(f"\n## DIM: {dim}\n")
        for p in by_dim[dim]:
            pair_lines.append(f"### {p['id']}\n")
            pair_lines.append(f"**Prompt**: `{p['prompt']}`\n")
            if p.get("expect"):
                pair_lines.append(f"**Expect**: {p['expect']}\n")
            pair_lines.append(f"**FT** (wenyan/100han={p['ft_m']['wenyan_per_100han']}, modern={p['ft_m']['modern_token_count']}, latin%={p['ft_m']['latin_ratio']*100:.1f}):")
            pair_lines.append(f"> {p['ft_resp'][:600]}\n")
            pair_lines.append(f"**BL** (wenyan/100han={p['bl_m']['wenyan_per_100han']}, modern={p['bl_m']['modern_token_count']}, latin%={p['bl_m']['latin_ratio']*100:.1f}):")
            pair_lines.append(f"> {p['bl_resp'][:600]}\n")
            pair_lines.append("---\n")

    (OUT / "compare_pairs.md").write_text("\n".join(pair_lines), encoding="utf-8")
    print(f"wrote {OUT / 'compare_pairs.md'}")

    # stdout summary
    for line in summary_lines:
        print(line)


if __name__ == "__main__":
    main()
