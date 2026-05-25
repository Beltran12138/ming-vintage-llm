# Corpus Inventory — 1424 Cutoff 中文 Vintage LLM

> **目的**：列全候选数字化文言 corpus 源，标注 ROI，定 Phase 1 攻击次序。
>
> **filter 时代界**：作品 / 作者卒年 ≤ 1424（明永乐二十二年，朱棣崩）。
>
> **状态**：v0.1，初列，量级估为先验估算，待 Phase 1 抓取后修正。

---

## 候选源全列（13 源）

### 一、ctext.org（中国哲学书电子化计划）★ 降级 ROI 1 → ROI 4 备用

| 字段 | 值 |
|---|---|
| URL | https://ctext.org |
| 维护者 | Donald Sturgeon（独立学者，UC Berkeley PhD） |
| 数字化质量 | 高，多版本对照，含点校 |
| License | free for academic，**ToS 明禁 bulk scrape** |
| 量级估计 | ~100M 字（含完整 pre-Han + 经史子集主要部分） |
| 时代覆盖 | 先秦至清末，**含完整明前** |
| 1424 filter 难度 | **易**（每作品有作者朝代 metadata） |
| 取法 | REST API（4 endpoint：gettext / getlink / readlink / getstatus），**bulk 严禁** |
| 已知 blocker | **ToS：「automatic download software on this site is strictly prohibited」**；rate limit 未公开；部分 endpoint 须登录 |
| 优先级 | **★ 备用补缺**（仅 small-sample，用于 kanripo 之版本对照 / 缺失补漏） |

**ToS 警示**：2026-05-25 fetch 之 ctext API docs 明示禁 bulk。Phase 1 不主攻；仅在 kanripo 之文本残缺 / 质量差时，小样本 register account 之后 polite fetch（< 1 req/sec）。

**重定向**：原 ctext 之主攻量级（100M 字）由 **kanripo 大量镜像 ctext-quality 点校本** 承担。Donald Sturgeon 本人亦 contribute 过 kanripo。

---

### 二、CBETA（中华电子佛典协会）★ ROI 2

| 字段 | 值 |
|---|---|
| URL | https://www.cbeta.org / https://github.com/cbeta-org |
| 维护者 | 中华电子佛典协会（台北） |
| 数字化质量 | 极高，TEI XML，含校勘记 |
| License | **free，CC-BY-NC**，bulk download |
| 量级估计 | ~180M 字（《大正藏》+《卍续藏》+《嘉兴藏》） |
| 时代覆盖 | 后汉至民国，**1424 前主体清晰** |
| 1424 filter 难度 | **中**（按译者 / 撰者朝代 filter，部分续藏含明后） |
| 取法 | GitHub repo clone + offline parse |
| 已知 blocker | TEI XML 须 parse；异体字符 normalization |
| 优先级 | **★★★ 必攻** |

**fetch design**：
- `git clone https://github.com/cbeta-org/xml-p5` (TEI P5 版)
- parse XML，按 `<respStmt>` / dynasty tag filter
- 异体字按 CBETA `<g>` 标签处理
- 估 4-8h 完整 parse
- 输出 `corpus/raw/cbeta/<canon>/<text_id>.txt`

---

### 三、kanripo（汉籍リポジトリ）★★ 升级 ROI 3 → ROI 1 主攻

| 字段 | 值 |
|---|---|
| URL | https://www.kanripo.org / https://github.com/kanripo |
| 维护者 | 京都大学人文科学研究所 |
| 数字化质量 | 高，TEI XML，多重底本 |
| License | free, CC，bulk download via Git |
| 量级估计 | ~80M 字（含先秦至清部分汉籍） |
| 时代覆盖 | 先秦至清，**与 ctext 大量重叠** |
| 1424 filter 难度 | **易**（按朝代分目录） |
| 取法 | git clone per 单一 text repo（kanripo 用 git-per-text 架构） |
| 已知 blocker | 数千 repo，须脚本批量 clone |
| 优先级 | **★★★ 必攻（作为 ctext de-dup 与补充）** |

**fetch design**：
- 调 GitHub API 列 kanripo org 下全 repo（估 3000+）
- filter repo 名按朝代 prefix（KR1 经，KR2 史，etc）
- batch clone（限并发避免 rate limit）
- parse TEI → plain text
- **与 ctext de-dup**：用 fingerprint 去重，留点校质量高者

---

### 四、Wikisource 中文（中文维基文库）

| 字段 | 值 |
|---|---|
| URL | https://zh.wikisource.org |
| 维护者 | Wikimedia 社区 |
| 数字化质量 | 中下，volunteer 校对，部分含错 |
| License | CC-BY-SA, free |
| 量级估计 | ~50M 字（明前部分） |
| 时代覆盖 | 全 |
| 1424 filter 难度 | 中（须按 category 与作者 page filter） |
| 取法 | dump.wikimedia.org bulk + parse |
| 已知 blocker | wikitext markup 须 clean；与 ctext 重叠高 |
| 优先级 | **★★ 备攻**（与 ctext 重叠后剩余价值低） |

---

### 五、殆知阁古代汉语语料库

| 字段 | 值 |
|---|---|
| URL | http://www.daizhige.org / https://github.com/garychowcmu/daizhigev20 |
| 维护者 | 商业，部分 v2.0 在 GitHub free |
| 数字化质量 | 中（OCR + 部分点校） |
| License | 不明确，GitHub v2.0 为 free |
| 量级估计 | ~3B 字（号称，含大量后世） |
| 时代覆盖 | 先秦至清末 |
| 1424 filter 难度 | **难**（按目录粗 filter，无 fine metadata） |
| 取法 | GitHub repo clone |
| 已知 blocker | 质量参差；filter 后剩余量大但精度低 |
| 优先级 | **★ 三攻**（量大，但 noise 高） |

---

### 六、CHANT（Chinese Ancient Texts Database）

| 字段 | 值 |
|---|---|
| URL | https://www.chant.org |
| 维护者 | 香港中文大学 |
| 数字化质量 | 高 |
| License | free for academic（须 institution access） |
| 量级估计 | ~30M 字（先秦至六朝主，明前覆盖部分） |
| 时代覆盖 | 先秦至六朝 |
| 1424 filter 难度 | 易（其本身就 < 1424） |
| 取法 | web access，无 bulk API |
| 已知 blocker | 须 institution login；scrape 风险 |
| 优先级 | **★ 三攻**（与 ctext 重叠） |

---

### 七、国学大师

| 字段 | 值 |
|---|---|
| URL | http://www.guoxuedashi.net |
| 维护者 | 商业 |
| 数字化质量 | 参差，OCR 错误多 |
| License | 不明，scrape 灰色 |
| 量级估计 | ~5B 字（号称） |
| 时代覆盖 | 全 |
| 1424 filter 难度 | 难 |
| 取法 | scrape only |
| 已知 blocker | OCR 错误，无 metadata，scrape 不友好 |
| 优先级 | **× 不攻**（质量风险高于量级收益） |

---

### 八、中国基本古籍库（爱如生 searks）

| 字段 | 值 |
|---|---|
| URL | https://server.wenzibase.com |
| 维护者 | 北京爱如生数字化技术研究中心，商业 |
| 数字化质量 | **极高**（业界金标准） |
| License | 商业 paywall（机构订阅 ~ 数十万人民币 / 年） |
| 量级估计 | ~17B 字（一万种古籍） |
| 时代覆盖 | 先秦至民国 |
| 1424 filter 难度 | 易 |
| 取法 | 须机构订阅，无 free API |
| 已知 blocker | 个人不可购，scrape 违法风险 |
| 优先级 | **× 不攻**（access barrier） |

---

### 九、书同文古籍数据库

| 字段 | 值 |
|---|---|
| URL | http://www.unihan.com.cn |
| 维护者 | 书同文（北京），商业 |
| 数字化质量 | 高 |
| License | 商业 paywall |
| 量级估计 | ~12B 字 |
| 优先级 | **× 不攻** |

---

### 十、文渊阁四库全书电子版

| 字段 | 值 |
|---|---|
| URL | 商业（迪志文化） |
| 数字化质量 | 高 |
| License | 商业 paywall |
| 量级估计 | ~800M 字 |
| 时代覆盖 | 至乾隆，**须手动剔 1424 后** |
| 1424 filter 难度 | 中（按作者 metadata） |
| 取法 | 须机构访问 |
| 优先级 | **× 不攻**（access barrier） |

**注**：部分四库篇目可在 ctext / kanripo 中找到，作为间接覆盖。

---

### 十一、正统道藏（电子版）

| 字段 | 值 |
|---|---|
| URL | http://www.daoists.org / 部分 GitHub |
| 维护者 | 散见 |
| 数字化质量 | 参差 |
| License | mixed |
| 量级估计 | ~30M 字 |
| 时代覆盖 | 多 1424 前 |
| 1424 filter 难度 | 中 |
| 取法 | scrape + manual |
| 优先级 | **★★ 备攻**（道家 corpus 是李约瑟难题之关键变量） |

---

### 十二、二十四史点校本

| 字段 | 值 |
|---|---|
| URL | 中华书局，部分 wikisource / ctext 镜像 |
| 数字化质量 | 高（中华书局点校本是金标准） |
| License | 中华书局版权，wikisource 镜像 free |
| 量级估计 | ~40M 字（pre-1424：前 18 史 + 元史） |
| 时代覆盖 | 上古至元 |
| 1424 filter 难度 | **易**（《明史》成于清，剔之；其他 18 史皆 ≤ 1424） |
| 取法 | wikisource / ctext 已含 |
| 优先级 | **★★★ 通过 ctext / wikisource 间接覆盖** |

---

### 十三、古今图书集成

| 字段 | 值 |
|---|---|
| URL | 多镜像 |
| 数字化质量 | 中 |
| 时代覆盖 | 雍正成书（1725），**须整书剔** |
| 优先级 | **× 不攻**（post-1424） |

---

## ROI 矩阵（2026-05-25 修订，ctext ToS warning 后）

| 源 | 量级估 | filter 难度 | access | 总 ROI |
|---|---|---|---|---|
| **kanripo** | 80M（与 ctext 大量重叠，实际更高） | 易 | **git clone，合规** | **★★★★ 主攻** |
| **CBETA** | 180M | 中 | free GitHub | **★★★ 主攻** |
| 道藏 | 30M | 中 | mixed | **★★ 备攻**（Gate 后视量定） |
| Wikisource | 50M（剩余去重后 ~10M） | 中 | free | ★★ 备攻 |
| ctext（小样本补缺） | < 10M（仅 polite fetch） | 易 | API + ToS 约束 | ★ 仅 fallback |
| 二十四史（经 kanripo） | 40M | 易 | free（间接） | 已含于 kanripo |
| 殆知阁 v2.0 | 估 100-300M（剩余去重后） | 难 | free | ★ 三攻 |
| 其余商业 / 国学大师 | × | × | × | × |

**新主攻合**：kanripo 80M+ + CBETA 180M = **~260M 字 ≈ 175M token**。

—— **过 Phase 1 Gate 200M 线之边缘**。若实测略低，备攻道藏（30M）+ Wikisource（10M）补至 220M 字 ≈ 145M token。**Gate 阈值或须从 200M token 下调至 150M token**，待 Phase 1 实测再定。

---

## Phase 1 攻击次序（2026-05-25 修订）

```
Week 1
  Day 1-3: kanripo 全攻 → corpus/raw/kanripo/
           - GitHub API 列 kanripo org 全 repo
           - filter 按 KR1-KR6 朝代 prefix
           - batch clone
           - parse TEI → plain text

  Day 4-6: CBETA bulk download + TEI parse → corpus/raw/cbeta/
           - git clone cbeta-org/xml-p5
           - parse + filter 译者 ≤ 1424

  Day 7:   kanripo × CBETA de-dup → corpus/filtered/main-merged/
           - fingerprint 去重
           - 留高质量者

Week 2
  Day 8:   实测 token stats → corpus/stats/main-stats.json
  Day 9:   若 < 150M token：启备攻（道藏 + Wikisource）
           若 ≥ 150M token：直入 Phase 1 Gate
  Day 10:  ctext 补缺（仅 < 10 个 kanripo 缺失之关键文本，polite fetch）

Phase 1 Gate（Day 10）:
  - 实测 token 总量
  - 若 ≥ 150M token: Phase 2 fine-tune 可行（LoRA rank=16）
  - 若 50-150M:      降级为 LoRA rank=8 + smaller base (Qwen 1.5B / 3B)
  - 若 < 50M:        弃 PoC，纯思想实验路（路乙 only），essay 改写
```

---

## Filter 规则（1424 cutoff）

### 收入条件

作品须满足以下其一：
1. 作者卒年 ≤ 1424
2. 作品成书年 ≤ 1424
3. 译本须译者卒年 ≤ 1424（佛典关键）

### 边界 case

| case | 处理 |
|---|---|
| 作者生于明初，卒于 1424 后（如方孝孺 1357-1402 ✓） | 按卒年判 |
| 续作 / 后世增补本（如《元史》成于 1370，洪武 ✓） | 按成书年判，**1424 前洪武 / 永乐成书皆 ✓** |
| 永乐大典本身（1408 成） | ✓ |
| 文集中含 1424 后作者批注 | 剔批注，留正文 |
| 朝代不明 / 伪托（如《阴符经》、《关尹子》） | 按学界主流断代，若 ≤ 1424 则 ✓ |
| 佛典之后世续藏 | 按译者朝代 filter，多数大藏经主体 ≤ 1424 |

### 已知须剔之关键作品

- 《明史》（清乾隆成）
- 《古今图书集成》（雍正成）
- 《四库全书》（乾隆成，但其收录之 1424 前作品 ✓）
- 《资治通鉴纲目》（朱熹原本 ✓，但明清增补本须剔）
- 王阳明、李贽（明中后期，× post-1424）

---

## 待补 / 未决问题

- [ ] ctext 实际 API rate limit 与 bulk dump 可用性
- [ ] kanripo repo 总数实际值（估 3000+）
- [ ] CBETA 续藏明后部分之精确剔法
- [ ] 异体字 normalization 标准（建议用 Unihan）
- [ ] 标点：保留点校本之标点，或剥离（影响 tokenizer 训练）

---

## 下一动

1. 用户审此 inventory
2. 通过 → 写 ctext fetch 脚本（攻 ROI 1）
3. Day 10 Phase 1 Gate review，决定 PoC scale
