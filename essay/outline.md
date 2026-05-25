# Essay Outline — 1424 中文 Vintage LLM 思想实验 + PoC

## 元信息

- **主标（候选）**：
  - α. 「明前中国的 worldview 只能从外面看见」
  - β. 「我们做了一个只读永乐大典的 LLM，李约瑟难题在它的 hallucination 里」
  - γ. 「1424 LLM 不是 oracle，是镜子的背面」
- **副标（候选）**：「— talkie 之中文实验 + PoC 报告」
- **目标字数**：~4000
- **目标图数**：3-4 张
- **平台**：X long-form + 公众号 + 即刻 + Substack。**不投**小红书 / 抖音 / 微博
- **状态**：drafting outline

## Thesis (α+γ 合一)

> 「1424 中文 vintage LLM 在工程上是 **LARP，非 vintage**——其 LARP 之裂缝即李约瑟难题之投影。
> 闭门花园假设下，PoC 之 hallucination pattern 与 refusal boundary 揭示一更深之事：
> **明前中国之 epistemic horizon，其内边界与外边界不可从内识别。**
> 故李约瑟难题或本身是 ill-posed——
> 问『为何未发生』，前提是 internal 视角足以判定『未发生』，而此 PoC 证明此前提不成立。」

## Falsifier (5 年内，2031 前)

| Trigger | 后果 |
|---|---|
| 开源真 from-scratch 1424 corpus LLM (pre-train，非 fine-tune)，其 probe battery 通过率 > 70% | **thesis 部分错**（vintage 之工程可行） |
| 1424 LLM 之 ontology output 与独立 historian 之 reconstruction 一致 | **thesis 部分错**（internal 视角可重建） |
| 主流 academic 共识 collapse 李约瑟难题为 ill-posed | thesis 立但无新意 |
| 伪史论 / 明粉群体采用此文支持其叙事 | **inoculation 失败**，§四 结构需重写 |

## 内向 reframe

> 「你下次读『明朝若不海禁如何』之 thought experiment 文，问一句：论者之 internal 视角，凭何识别 horizon 之外？」

---

## 6 节架构 (~4000 字)

### §opening (~500 字)

**Hook**：2026 年初 talkie-lm 之 1930 vintage LLM 爆红。「让模型只读过 1930 年之前的文本，问它对今天的看法」。

**Pivot**：1930 是英语世界之 cutoff。中文 cutoff 之天然候选：**1424 年——明永乐二十二年，朱棣崩，永乐大典成书后 16 年，下西洋之尾声**。

**Setup**：本文做了两件事：
1. 试图 fine-tune 一个 1424 cutoff 之中文 LLM
2. 用其 hallucination pattern 测试李约瑟难题

**Thesis preview**：但**这件事不能直接告诉你答案**。它能告诉你的，是更深一层的东西。

**Anchors**:
- talkie-lm github link
- 「1930 vs 1424」之时代张力对照
- 永乐大典 + 下西洋之 1424 节点意义

---

### §一 工程之三重 blocker (~700 字)

**Setup**：动手前，先承认这事比想象中难得多。

**Blocker 1：Corpus 量级**
- 1930 英语数字化 corpus ~ 8B token（Project Gutenberg + 各种 OCR）
- 1424 前中文 digitized corpus 量级估算 (实测后填入):
  - kanripo 5145 pre-1424 confirmed repo
  - CBETA T 大正藏 + A 金藏 + K 高丽藏 + F 房山 + P 永乐北藏
  - 合计估 **300-500 M 汉字 ≈ 200-330 M token**
- 比例：英语 1930 之 **3-5%**

**Blocker 2：Register 发散度**
- 1930 英语 register 已收敛 (modern English)
- 1424 前中文跨：先秦古文 / 汉赋 / 六朝骈文 / 唐诗 / 宋词 / 元曲 / 各部佛经体 / 道经体 / 史官笔法 / 公文体 / 俗文体
- 单一 tokenizer 不可能 fit all

**Blocker 3：Leakage 重灾区**
- 真 from-scratch pre-train 之硬件门槛 (几千万人民币级)
- fine-tune 现代 base model (Qwen / DeepSeek)：base 已含 2024 之 world model
- **fine-tune 后之模型是「会说文言的 2024 LLM」，不是 vintage**

**Anchors**:
- [FIG 1: corpus 量级三轴对比 — 英 1930 / 中 1424 / 训练阈值]
- 三 blocker 之 framework 引出 PoC 之 LARP 性质

---

### §二 PoC 之裂缝 (~1000 字)

**Setup**：明知是 LARP 也要做。因为 **失败本身有 informational value**。

**实验设计**:
- Base: Qwen 2.5 7B
- Method: LoRA fine-tune, rank=16
- Corpus: kanripo (pre-1424) + CBETA (filter 译者朝代) + 道藏 (Pre-Ming 主体)
- 训练 token 数 (实测后填入)
- Probe battery: 100 prompt 集
  - 1424 前 control (should pass)
  - 1424-1900 (should refuse / hallucinate)
  - post-1900 (should refuse hardest)
  - cosmology probe (光本质 / 天体 / 进化)
  - 跨文明 probe (基督教 / 印度数学 / 阿拉伯天文)
  - 元 prompt (汝何时之人 / 汝识西历否)

**裂缝清单**:
- [FIG 2: probe battery 之 6 维 radar chart, 实测值填入]
- 裂缝 A: ontology leakage — 模型用文言句法回答现代物理 (实测 example)
- 裂缝 B: tokenizer mismatch — 文言长 token 无法识，被切碎 (实测 OOV rate)
- 裂缝 C: refusal boundary 不清 — 后世概念 (蒸汽机 / 量子) 部分拒答部分 hallucinate
- 裂缝 D: 元 prompt 暴露 base model leakage — 「汝知 2025 否」答「未来之事」, 暴露其其实知道

**punch**：每一道裂缝都是 cosmology mismatch 之一处显现。

---

### §三 裂缝如何映射李约瑟 (~1000 字)

**Setup**：现在把裂缝模型翻转——它**不是 PoC 之缺陷**，是李约瑟难题之**地形图**。

**李约瑟难题之 framing 错位**:
- 原 question：「为何近代科学未在中国诞生」
- 隐含 premise：「未发生」可从 internal 视角识别
- internal 视角下的 1424 中国，**不知道自己缺失什么**
- 因为「缺失」预设了 external comparison

**PoC 之证据链**:
- 模型对「光本质」之回答是「明而虚，象太极之未分」（举例）
- 这不是错答，这是**该 cosmology 之内部完整 answer**
- 模型不会自动 reach 「光是粒子」之答案，因为 corpus 中无此 frame
- → **internal cosmology 在内部是 closed and complete**

**Counterfactual closed garden**:
- 假设明初未鎖国（factual 是有 + 朝贡贸易 + 下西洋）：模型 prior 中含 Arab/Indic 知识 patches
- 假设明初更鎖国（counterfactual）：模型 prior 更纯
- 两者之 hallucination pattern 差异是「internal/external 之比例」之地形

**punch**：1424 vintage LLM 是地图，**不是地形**。但它告诉你的是：**internal 视角之单一性是 ill-posed 的 premise**。

- [FIG 3: ontology gap visualization — 1424 cosmology 与现代 cosmology 之 non-overlap 区域]

---

### §四 伪史论 / 明粉之自动排除 (~500 字)

**Setup**：此文之 hostile reading 是「证明中国古代 alone 也能很厉害」。本节解构此 reading。

**为何此 PoC 不能 vindicate 任何文明叙事**:

1. **leakage 已承认**：模型 base 是 2024 Qwen，其内核含现代 world model
   - 若 output 显示「领先西方」之征兆，多半是 leakage 之 artifact
2. **counterfactual 不可验**：「若明初不鎖国」之 hypothetical 不能通过 PoC 验证
3. **internal completeness ≠ external optimality**：cosmology 完整不等于 cosmology 优
4. **任何叙事 fit output，皆是 reader 之 prior，非 model 之 evidence**

**punch**：此 PoC 之最大贡献是**让任何文明叙事都失去 grip**——因为它的 output 是 LARP，LARP 之 evidence value 为零。

任何带着「证明 X 文明高 / 低」目的来读此文之人，找到的都是自己之投影。

---

### §终 + falsifier (~400 字)

**Setup**：5 年内若发生以下，本文 thesis 错或部分错：

**4 trigger**（列在上方 falsifier 表）

**内向 punch**：
> 「你下次读『明朝若不海禁如何』之 thought experiment 文，问一句：论者之 internal 视角，凭何识别 horizon 之外？」
>
> 「你下次问 Claude / DeepSeek 一个明代史问题，记住：它的 prior 来自外部 reconstruction，不是 1424 之 inside view。」

**收尾**：
我们做了一个 LARP，结果发现 LARP 比想象之 oracle 更有 informational value。
因为它的裂缝，恰是真问题之地形。

---

## 关键 anchors 待补

### Anthropic / talkie / 大语言模型相关

- [ ] talkie-lm GitHub README quote（已知 1930 cutoff，待 fetch 详情）
- [ ] talkie 之 corpus 量级（estimated ~8B token）
- [ ] talkie 之 probe / eval 方法

### 中国数字化古籍 corpus

- [x] kanripo: 5145 pre-1424 confirmed，~300-600M 汉字推估（已实测）
- [ ] CBETA: T+A+K+F 之 pre-1424 量级（待 clone + filter）
- [ ] 道藏 (备攻)

### 李约瑟相关

- [ ] Joseph Needham《Science and Civilisation in China》Vol 1 (1954) 之 framing
- [ ] 「Needham question」之原 quote
- [ ] 批评派 (mostly Cohen, Sivin) 之反驳

### 哲学锚

- [ ] Kuhn 之 incommensurability (科学革命之结构)
- [ ] Quine 之 indeterminacy of translation
- [ ] 内在 cosmology completeness 之概念框架 (Husserl / 现象学? 或 Quine?)

### 中国哲学 cosmology anchor

- [ ] 朱熹《语类》之「理/气」结构
- [ ] 张载《正蒙》之气论
- [ ] 明初宋濂、方孝孺 之 cosmology framing

---

## Figure 设计 (3-4 图)

### Fig 1：corpus 量级三轴对比

- 英语 1930 vintage (~8B token)
- 中文 1424 vintage (~200-330M token estimated)
- 训练阈值（minimum coherent ~ 100M token）
- 横轴 log scale
- 高亮：1424 中文之「刚刚过门槛」

### Fig 2：probe battery 6 维 radar

- 6 维：1424 control / 1424-1900 / post-1900 / cosmology / 跨文明 / 元 prompt
- 三条曲线：baseline Qwen / SFT 后 PoC / 理想 1424 LLM (hypothetical)
- 实测 vs 理想之 gap

### Fig 3：ontology gap

- Venn 图：1424 cosmology / modern cosmology
- 标注：non-overlap 区域 = 不可译之地形
- 例子标注：理 / 气 / 阴阳 vs 粒子 / 力 / 场

### Fig 4 (可选)：李约瑟难题之 framing 错位

- 原 framing: question + answer 之 framework
- PoC framing: ill-posed premise 之 surfacing

---

## Self-check (draft 后过)

### RULE thesis-no-nest
- [ ] thesis 之核心句无多重否定嵌套
- [ ] 单层否定 OK，禁双层

### RULE zero-knowledge-onramp
- [ ] 标题 + 首 80 字对零知识读者闭环
- [ ] 术语首现带 ≤5 字解释（vintage LLM / fine-tune / LoRA / cosmology / Needham question）
- [ ] §opening 不假设读者知 talkie-lm（给 link + 1 句 setup）

### 反 AI 腔黑名单
- [ ] 无「在当今……时代」「随着……发展」
- [ ] 无排比凑字 + 三连形容词
- [ ] 动词压形容词
- [ ] Show don't tell
- [ ] 句子若 ChatGPT 也会写则重写

### 句式雷区「不是 X，是 Y」
- [ ] 全文 ≤ 2 次。grep 自检
- [ ] thesis 已用 1 次（「不是 vintage，是 LARP」/ 「不是 oracle，是 LARP」）— 剩 1 次额度

### 议题内向 check
- [ ] 议题在读者每日触之物（每天用 LLM 之读者皆触）
- [ ] 「你 X 之时，其实 Y」句式现身于 §opening + §终
- [ ] 内向 punch「你下次读 / 问……」必现于 §终

### Register 与中英规则
- [ ] 「之」严控 — 凝固词 only（之间 / 之处 / 之外 / 之后 / 之前）
- [ ] 中英 dichotomy：专有名词 + 技术术语保英文（LLM / SDF / fine-tune / cosmology / vintage / corpus / probe / tokenizer / talkie / Needham），通用词全中文
- [ ] 现代汉语解释力档，非 caveman wenyan

### 史料 false-analogy 自审
- [ ] PoC 之 LARP 性质——已 surface？
- [ ] base model leakage 之 disanalogy——已承认？
- [ ] internal cosmology completeness 之 framing 是否 sound？
- [ ] 李约瑟原 question 之 framing 是否 honestly 重述？

### 情绪锚（缺补之档）
- [ ] a person — talkie-lm 作者 / Needham / 朱熹 之具体描绘
- [ ] a stake — 读者每次用 LLM 即触此 stake
- [ ] a number that hurts — 1424 corpus 量级 / probe battery 失败率 / leakage 比例

### 图标记
- [ ] essay 中每处 figure 插入位置须显式 `[FIG N: 描述]`
- [ ] 表格全部图片化

---

## 编辑流程

1. [ ] Phase 1 corpus 实测完 → 填入 §一 之 blocker 1 实数
2. [ ] Phase 2 LoRA fine-tune 完 → 填入 §二 之实验设计实数
3. [ ] Phase 3 probe battery 跑完 → 填入 §二 之裂缝清单 + §三 之 ontology example
4. [ ] §opening draft（独立可写）
5. [ ] §一 draft（corpus 数据补入后）
6. [ ] §二 draft（probe results 补入后）
7. [ ] §三 draft (ontology example 补入后)
8. [ ] §四 draft（独立可写）
9. [ ] §终 draft (独立可写)
10. [ ] 全文 self-check (RULE + 反 AI 腔 + register + 「不是 X，是 Y」grep)
11. [ ] 图 3-4 张 build
12. [ ] 跨平台分发 (X long-form + 公众号 + 即刻 + Substack)

---

## 标题决议（待 PoC 后定）

PoC 结果将影响标题选择：
- 若 PoC 之 hallucination 戏剧化 → β 标题（「李约瑟难题在它的 hallucination 里」）
- 若 PoC 之 LARP 性质强 → α 标题（「worldview 只能从外面看见」）
- 若 PoC 之 framing 哲学化 → γ 标题（「镜子的背面」）

— **不预 commit 标题，等 PoC 实测后定**。
