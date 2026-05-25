"""
Kanripo repo metadata 分析: KR1-6 分布 / dynasty filter / 量级估
读 repo-list.jsonl, 输出 stats + filtered list
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"C:\Users\lenovo\projects\ming-vintage\corpus")
REPO_LIST = ROOT / "raw" / "kanripo" / "repo-list.jsonl"
OUT_STATS = ROOT / "stats" / "kanripo-stats.md"
OUT_FILTERED = ROOT / "stats" / "kanripo-pre-1424-list.jsonl"
OUT_UNCERTAIN = ROOT / "stats" / "kanripo-uncertain.jsonl"

# 1424 之前可收 dynasty (含)
PRE_1424_DYNASTIES = {
    "先秦", "周", "西周", "東周", "春秋", "戰國",
    "秦", "西漢", "東漢", "漢", "兩漢",
    "三國", "魏", "蜀", "吳", "曹魏",
    "晉", "西晉", "東晉",
    "南北朝", "宋齊", "南朝", "北朝", "齊", "梁", "陳",
    "南宋", "宋",  # 注: 宋有 北宋/南宋, 但宋朝整体 ≤ 1279
    "北魏", "東魏", "西魏", "北齊", "北周",
    "隋",
    "唐", "唐初", "盛唐", "中唐", "晚唐", "唐初期", "唐中期", "唐末",
    "五代", "後梁", "後唐", "後晉", "後漢", "後周", "南唐", "前蜀", "後蜀",
    "遼", "金",
    "元", "蒙元", "元初", "元末",
    "明初", "明初期", "洪武", "建文", "永樂",
    "後秦",  # 鳩摩羅什等
    "北涼", "前涼", "後涼",
    "高麗",  # 朝鮮半島古书
}

# 必剔之朝代 (> 1424)
POST_1424_DYNASTIES = {
    "明中", "明後", "明末", "明中期", "明後期", "嘉靖", "萬曆", "崇禎", "天啟",
    "清", "清初", "清中", "清後", "清末", "康熙", "雍正", "乾隆", "嘉慶", "道光", "咸豐", "同治", "光緒", "宣統",
    "民國", "近代", "現代", "當代",
}

# 边界明朝 - 须看作者卒年, 默认归 uncertain
MING_AMBIGUOUS = {"明"}  # 不带具体时段标注的"明"

DYN_PATTERN = re.compile(r"-([^-]+)-")  # 提取两个 dash 之间的朝代


def parse_dynasty(desc):
    """从 description 提取 dynasty 字段, 返回 (dynasty_str, classification)"""
    if not desc:
        return ("", "no_desc")
    m = DYN_PATTERN.search(desc)
    if not m:
        return ("", "no_dynasty_field")
    dyn = m.group(1).strip()
    if not dyn:
        return ("", "empty_dynasty")
    # 分类
    for kw in PRE_1424_DYNASTIES:
        if kw in dyn:
            return (dyn, "pre_1424")
    for kw in POST_1424_DYNASTIES:
        if kw in dyn:
            return (dyn, "post_1424")
    if dyn in MING_AMBIGUOUS or dyn == "明":
        return (dyn, "ming_ambiguous")
    return (dyn, "unknown_dynasty")


def main():
    if not REPO_LIST.exists():
        print(f"ERROR: {REPO_LIST} not found")
        return

    repos = []
    with REPO_LIST.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            repos.append(json.loads(line))

    # KR 部前缀
    kr_pattern = re.compile(r"^(KR[1-6])")

    # 统计
    by_section = defaultdict(lambda: {"count": 0, "size_kb": 0})
    by_classification = defaultdict(lambda: {"count": 0, "size_kb": 0})
    by_dynasty = defaultdict(lambda: {"count": 0, "size_kb": 0})

    filtered_pre_1424 = []
    uncertain = []

    for r in repos:
        name = r.get("name", "")
        desc = r.get("description", "") or ""
        size = r.get("size", 0)

        # KR 部分类
        m = kr_pattern.match(name)
        section = m.group(1) if m else "OTHER"
        by_section[section]["count"] += 1
        by_section[section]["size_kb"] += size

        # 仅文本 repo (KR1-6 prefix), filter docs/utility repos
        if section == "OTHER":
            continue

        # dynasty 分类
        dyn, classification = parse_dynasty(desc)
        by_classification[classification]["count"] += 1
        by_classification[classification]["size_kb"] += size
        by_dynasty[dyn or "(空)"]["count"] += 1
        by_dynasty[dyn or "(空)"]["size_kb"] += size

        record = {**r, "section": section, "dynasty": dyn, "classification": classification}

        if classification == "pre_1424":
            filtered_pre_1424.append(record)
        elif classification in ("ming_ambiguous", "unknown_dynasty", "empty_dynasty", "no_dynasty_field"):
            uncertain.append(record)

    # 输出 stats markdown
    lines = ["# Kanripo Stats — 2026-05-25\n"]
    lines.append(f"**总 repo 数**: {len(repos)}")
    lines.append(f"**文本 repo (KR1-6)**: {sum(d['count'] for k, d in by_section.items() if k.startswith('KR'))}\n")

    lines.append("## 按 KR 部分布\n")
    lines.append("| 部 | 含义 | repo 数 | 总 KB | MB |")
    lines.append("|---|---|---|---|---|")
    section_names = {"KR1": "经部", "KR2": "史部", "KR3": "子部", "KR4": "集部", "KR5": "道部", "KR6": "佛部", "OTHER": "其他"}
    for sec in ["KR1", "KR2", "KR3", "KR4", "KR5", "KR6", "OTHER"]:
        d = by_section[sec]
        lines.append(f"| {sec} | {section_names[sec]} | {d['count']} | {d['size_kb']:,} | {d['size_kb']/1024:.1f} |")
    total_kr = sum(d['size_kb'] for k, d in by_section.items() if k.startswith('KR'))
    lines.append(f"| **KR1-6 合** |  |  | **{total_kr:,}** | **{total_kr/1024:.1f}** |\n")

    lines.append("## 按 1424 cutoff 分类\n")
    lines.append("| 分类 | repo 数 | 总 KB | MB |")
    lines.append("|---|---|---|---|")
    for cls in ["pre_1424", "ming_ambiguous", "post_1424", "no_dynasty_field", "empty_dynasty", "unknown_dynasty", "no_desc"]:
        d = by_classification[cls]
        lines.append(f"| {cls} | {d['count']} | {d['size_kb']:,} | {d['size_kb']/1024:.1f} |")
    lines.append("")

    lines.append("## Top 30 dynasty (by count)\n")
    lines.append("| Dynasty | repo 数 | 总 KB |")
    lines.append("|---|---|---|")
    sorted_dyn = sorted(by_dynasty.items(), key=lambda x: -x[1]["count"])
    for dyn, d in sorted_dyn[:30]:
        lines.append(f"| {dyn} | {d['count']} | {d['size_kb']:,} |")
    lines.append("")

    # 计算 pre_1424 之总 size 估
    pre_size = by_classification["pre_1424"]["size_kb"]
    amb_size = by_classification["ming_ambiguous"]["size_kb"]
    lines.append("## 量级估算\n")
    lines.append(f"- 确定 pre-1424: **{pre_size:,} KB** ≈ {pre_size/1024:.1f} MB")
    lines.append(f"- 边界明朝 (须 audit): {amb_size:,} KB ≈ {amb_size/1024:.1f} MB")
    lines.append(f"- 若按 GitHub repo size = 含全 branch, 单 default branch 字数估 size_kb × 0.15 ~ 0.3 (mandoku tag 占位)")
    lines.append(f"- **粗估字数**: pre-1424 之 default branch ≈ {pre_size * 0.2:.0f} KB UTF-8 ≈ {pre_size * 0.2 / 1.5:.0f} K 汉字 ≈ **{pre_size * 0.2 / 1.5 / 1000:.1f} M 汉字**")
    lines.append(f"- 待实测验证 (前 5 样本 cleanup 后)")

    OUT_STATS.parent.mkdir(parents=True, exist_ok=True)
    OUT_STATS.write_text("\n".join(lines), encoding="utf-8")
    print(f"stats → {OUT_STATS}")

    # 输出 pre-1424 list
    with OUT_FILTERED.open("w", encoding="utf-8") as f:
        for r in filtered_pre_1424:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"pre-1424 list ({len(filtered_pre_1424)} repos) → {OUT_FILTERED}")

    # 输出 uncertain list (须 audit)
    with OUT_UNCERTAIN.open("w", encoding="utf-8") as f:
        for r in uncertain:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"uncertain list ({len(uncertain)} repos) → {OUT_UNCERTAIN}")

if __name__ == "__main__":
    main()
