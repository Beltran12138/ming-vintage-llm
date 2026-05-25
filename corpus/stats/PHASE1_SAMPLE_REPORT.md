# Phase 1 Sample Fetch Report — 2026-05-25

## TL;DR

**kanripo pre-1424 之 5145 repo 推估 ≈ 300-600 M 汉字 (200-400 M token)。过 Gate 阈值 150M token。**

## Sample 实测

6 sample 跨 KR1-6 全部部，default branch fetch，mandoku markup cleanup 后字数：

| Repo | 内容 | Branch | 文件数 | Raw KB | Cleaned KB | 汉字数 | Ratio (汉字/KB raw) |
|---|---|---|---|---|---|---|---|
| KR1a0001 | 周易 (正文) - 周 | master | 69 | 153.1 | 93.3 | 22,776 | 345 |
| KR2a0001 | 史記 - 漢 司馬遷 | master | 14 | 3076.7 | 2490.3 | 983,842 | 953 |
| KR3a0001 | 子部首篇 | master | 12 | 246.3 | 216.6 | 72,339 | 233 |
| KR4a0001 | 集部首篇 | master | 10 | 198.4 | 148.9 | 76,980 | 1040 |
| KR5a0001 | 靈寶無量度人上品妙經 - 道 | CK-KZ | 62 | 1372.1 | 1034.4 | 349,426 | 236 |
| KR6a0001 | 長阿含經 - 後秦 | master | 22 | 794.5 | 722.3 | 198,543 | 277 |
| **合** |  |  | **189** | **5841.1** | **4705.8** | **1,703,906** | **avg 463** |

## Observations

1. **Ratio 跨样本 233-1040 大跳**。size 字段非可靠 proxy。**KR2a0001 史記 1032 KB → 984K 汉字** (ratio 953) 是 outlier 之一—— mandoku markup 占比较小，因 史記 是高密度叙事文。**KR4a0001 ratio 1040** 是另一 outlier，集部首篇内容紧凑。
2. **道部 (KR5)** ratio 偏低 (236)，因道经 markup 密集 + 反复段落 (`¶` 多)。
3. **mandoku cleanup loss**: raw → cleaned 平均损失 ~ 20% (markup + ¶ + headers)。
4. **多 branch 系统**：6 sample 中 5 个用 `master` branch（GitHub default），1 个 (KR5a0001) 用 `CK-KZ`。批量 clone 须 follow `default_branch` field 不可硬编码 master。

## 推估

按 6-sample avg ratio 463：

```
pre-1424 size_field 合 = 1,290,917 KB
推估字数 = 1,290,917 × 463 = 597.7 M 汉字
```

按保守 ratio 200-300：

```
低估 = 258 - 387 M 汉字
```

按文言 1.5 char/token 转 LLM token：

```
低估 → 172-258 M token
中估 → 200-300 M token  (按 ratio 350-450)
高估 → 400 M token
```

**结论**：保守 200 M token 已过 Phase 1 Gate 之 150M token 阈值。**量级问题解决**。

## 加成项 (尚未计入)

- **明朝边界 1088 repo (389 MB raw)**：audit 后若 30% 是明初 (洪武建文永乐 / 卒年 ≤ 1424)，加 ~ 117 MB raw → ~ 50 M 汉字
- **空朝代 1806 repo (97 MB raw)**：audit 后估 50-80% 是 pre-1424 (道部 KR5 多无明确朝代)，加 ~ 50 MB raw → ~ 23 M 汉字
- **CBETA 全攻** (180 M 汉字 估)：尚未做，纯加成
- **道藏 / Wikisource** (备攻)：尚未做

—— **若全部加成 + CBETA，合计可达 400-800 M 汉字 (270-530 M token)**。

## Cleanup Pipeline Spec

### 已验证之 markup 处理

```python
ORG_HEADER = re.compile(r"^(#\+|# -\*-).*$", re.MULTILINE)
MD_TAG     = re.compile(r"<md:[^>]+>")
PB_TAG     = re.compile(r"<pb:[^>]+>")
FW_TAG     = re.compile(r"@[a-z]{2,4}")
PARA_MARK  = re.compile(r"¶+")
```

### 待补 cleanup 规则 (留 Phase 1 后期 audit)

- 异体字 normalization (是否走 Unihan / CBETA `<g>` 标准)
- 注释 vs 正文之分离（部分文本含 `[注: ...]`）
- 空白 / 排版字符 (`　` 全角空格)
- 多 branch 之文本可能含 校勘记 / 校异 标注

### 异体字策略 — 二选一

| 策略 | 利 | 弊 |
|---|---|---|
| **保留原貌** | 历史真实，tokenizer 学到异体 | OOV 多，vocab 爆炸 |
| **normalize 至正体** | OOV 少，tokenizer 高效 | 损失部分语言信息 |

—— Phase 2 tokenizer 设计时定。Phase 1 不动。

## 下一动 (Phase 1 推进)

1. **Bulk clone pre-1424 之 5145 repo** (按 default branch)
2. 同时 **CBETA 全攻** (并行)
3. **明朝边界 audit** (按作者卒年 cross-check) — 1088 repo
4. **空朝代 audit** (按文本 inspection) — 1806 repo

预估 bulk clone 时间：5145 repo × ~ 200 KB avg = ~ 1 GB。git clone 单线程估 6-12h，并行 8 线程 1-2h。

## Risks

| Risk | 缓解 |
|---|---|
| GitHub rate limit (5000 / hour authenticated) | gh auth 已有，5000 req/h 足够 9355 repo metadata + bulk clone |
| 单 repo 之多 branch 重复占盘 | clone 时 `--single-branch -b $default_branch` |
| Mandoku cleanup miss 之 markup variant | 实际 bulk clone 后再 sample inspect 修复 |
| 明朝 audit 之作者卒年数据 | 用 wikidata SPARQL 或 CBDB (中国历代人物传记数据库) cross-check |
