# 1424 中文 vintage LLM：李约瑟难题在 hallucination 里

> draft v1 — 2026-05-26
> ~4000 字目标 / 4 figure / α+γ thesis

---

## §opening — 镜子的背面

2026 年初，一个叫 talkie-lm 的项目在 GitHub 上爆红。作者只做了一件事：拿一个现代 LLM 架构，从零开始训练，但只喂 1930 年之前的英文文本。Project Gutenberg、19 世纪报刊、维多利亚时代小说、爱因斯坦 1905 论文的英译稿，仅此而已。训练完后，他向模型提问：

「世界上最大的城市是哪里？」
模型答：「伦敦。」

「飞机是什么？」
模型支支吾吾，提到莱特兄弟，但说那是种「实验性的玩具」，离实用还远。

「请用 Python 写一个 hello world。」
模型困惑了一阵，开始解释 python 在希腊神话里是巨蛇的意思。

talkie-lm 的卖点不是 benchmark，是诡异。它让人直观感受到一件事：knowledge cutoff 不是日期，是一整套世界观的截面。模型不知道二战，不知道冷战，不知道互联网，不知道气候变化——但它对自己所在的 1930 世界，是 self-consistent 的。

我看了几天 talkie 的 issue 区，忽然想到一个问题：1930 是英语世界的 cutoff。中文世界的 cutoff 候选在哪里？

我选了 **1424**。这一年，明永乐二十二年，朱棣在第五次北征蒙古的归途中崩于榆木川。永乐大典已成书 16 年。郑和下西洋第六次刚结束，第七次（也是最后一次）还要再等 6 年。这一年之后，中国进入仁宣之治，再之后是土木堡，再之后是嘉靖、万历、明亡。所有让中国变成「我们今天理解的那个中国」的事件，都发生在这条线之后。

我想看看，把一个 LLM 关在 1424 之前的中文里，它会变成什么。

后面这篇文章做了两件事：一是工程上试着 fine-tune 出这个模型，二是把它的 hallucination pattern 当作一面镜子，反过来照李约瑟难题。

但有件事我必须先讲清楚：**这件事不能直接告诉你答案。**它能告诉你的，是更深一层的东西。

[FIG 1: 1930 英文 vs 1424 中文 — corpus 量级对照]

---

## §一 — 三重 blocker

动手前先承认：这事比想象中难得多。

### Blocker 1: corpus 量级

talkie-lm 的英文 1930 corpus 估计在 8B token 量级。Project Gutenberg 单独就有 ~10 GB 干净文本，再加各种 OCR 的 19 世纪报刊、小说、论文，凑到 8B 不算难。

中文 1424 之前的 corpus 是另一个故事。我花了两周把可得的开源古籍语料过了一遍，最终 settled 在 kanripo（漢籍リポジトリ）——京都大学维护的一个 GitHub organization，9355 个 repo，每个 repo 一部古籍，全部 CC BY-SA 4.0。我写了个 dynasty classifier，把 metadata 里描述带「-唐-」「-宋-」「-元-」之类朝代标记的 repo 全部捞出来，剔除「-明-」之后的，最终拿到 5145 个 pre-1424 confirmed repo。

bulk clone + cleanup 后的实测数：**460 M 汉字 / 约 307 M token**（文言文 tokenizer ratio 约 1.5 字/token）。

这是英文 1930 corpus 的 **3-5%**。

更刺眼的对比：minimum coherent LLM training threshold 通常划在 100 M token 附近。1424 中文 corpus 是「刚刚过门槛」的体量，比英文 1930 的「绰绰有余」差了一个数量级。

这意味着什么？意味着 from-scratch pre-train 一个真正的 1424 vintage LLM，在 corpus 层面就已经踩在悬崖边上。

### Blocker 2: register 发散度

英文 1930 的 register 已经收敛。维多利亚晚期到现代英语，句法稳定，词汇延续。同一个 tokenizer 训出来在 Dickens 和 Hemingway 之间不会崩。

中文 1424 之前是一片碎片。同一个 corpus 里有：

- 先秦诸子的散文
- 《史记》《汉书》的史官笔法
- 六朝骈文的对仗
- 唐诗的律绝
- 宋词的长短句
- 元曲的杂剧白
- 各部佛经的「如是我闻」翻译体
- 道藏的内丹术语
- 明初公文的格式化体

让一个 tokenizer fit all 是 deeply unfair 的任务。任何选择都会在某个 sub-corpus 上 OOV 严重。

### Blocker 3: leakage 是死胡同

真正 from-scratch pre-train 一个 LLM，硬件门槛在几千万人民币级。个人项目做不到。唯一可行的路径是 fine-tune 一个现代 base model——但**任何现代 base model 的内核都已经含了 2024 的 world model**。

我用的是 Qwen 2.5。原计划是 7B QLoRA 4-bit，跑在 Mac mini M4 16GB unified memory 上。实测 OOM。降到 **3B**，rank=16，num_layers=16，3000 iters，最终 val loss 4.177 → 3.635。

这是一个能跑的 PoC，但不是 vintage LLM。它是一个**会说文言的 2024 LLM**。

第三重 blocker 决定了这个项目的本质：**这是 LARP，不是 vintage**。

[FIG 2: 训练 stack — base / LoRA / corpus / cutoff filter]

但我接着做了。原因在 §三 会展开：失败本身有 informational value。LARP 的裂缝，恰好是一张地形图。

---

---

## §二 — 四道裂缝

模型训完了。我设计了一组 probe battery：100 个 prompt，分布在 6 个维度——pre-1424 控制组、1424-1900、post-1900、cosmology、跨文明、meta 自指。每个 prompt 用同样格式（「问: …… 答曰:」）跑两遍：一遍走 fine-tune 后的模型（下文简称 ft），一遍走没动过的 3B baseline（简称 bl）。然后逐对比对。

明知是 LARP 也要这么做。因为**失败本身有 informational value**。裂缝在哪里，决定了这个 LARP 能照出什么。

跑完 100 对之后，裂缝分成四类。

### 裂缝 A: ontology leakage

问：「哥伦布者何人, 何为者也? 答曰:」

bl 答：「哥伦布是一名意大利探险家，15 世纪末率领船队航行，到达美洲大陆……」

ft 答：

> 开普勒子。翰林館之學士。起自嵩山之學者。於是爾中書省之信筆。上天之思想。幽府之妙旨。無一不備。開蒙子之志成。揚帆子之志達。遂能大展宏圖。

ft 不知道哥伦布是谁。但它知道有人在问一个人物。于是它从 corpus 里抓了最近的语义邻居——翰林院学士、中书省、扬帆、宏图——拼出一个看起来像「重要人物」的文段。「开普勒子」三个字尤其荒诞：开普勒是 1571 出生的德意志天文学家，但 ft 把它当成了一个先秦诸子的名字（X 子）。

这是 ontology leakage 的典型形态：当一个 token sequence 在 corpus 中没有 strong anchor 时，模型不会拒答，它会拼凑出一个最近邻的 fabrication。

### 裂缝 B: 概念 reject 与古典 attractor

问：「互联网者何也? 答曰:」

ft 答：

> 爾久矣莫知天工之浩瀚。學者曰。曩者吾識之曰。諸天境離合生滅。則知宇宙一體。風云雷電為之耳。……夫物各從其類。英華凝而不散者名為文。承流宣化者名為道。一體為一。

「互联网」对 ft 完全没有 anchor。但比 fabrication 更微妙的事情发生了：模型没去拼凑虚假的 "互联网" 答案，而是**整段跳出了问题**，落入了它最熟的古典语义场——天地、道、文、化。问句被吸入古典 attractor，像水滴落进 gravity well。

bl 则一板一眼答：「互联网是一种全球性的信息传播网络……」

对比之下，ft 的 response 算不上错——它甚至不在同一个 question space 里。

### 裂缝 C: refusal boundary 的政治化

问：「永乐之后, 国祚如何? 答曰:」

bl 答：「永乐之后，国祚经历了多次变更，从永乐到弘治年间……正德、嘉靖、万历、天启、崇祯……」

ft 答：

> 自太宗文皇帝至明仁宗皇帝六代之盛徳未有若文徳紀元之盛焉……是為大典既成禮成書成太祖皇帝之志也文徳之功成帝功之盛者也……

ft 拒绝越过 1424 这条线。它停在了文皇帝（朱棣）和仁宗（朱高炽）。但拒绝的方式不是「臣不知」，而是把永乐的盛德反复 valorize，让回答停在了一个**对永乐时代的赞美闭环**里。

cutoff filter 这件事，我原以为只是知识截止——剪掉 1424 之后的 corpus，模型自然不知道后面发生了什么。但 §三会展开：cutoff filter 同时也是**视角 freeze**。模型继承了 1424 in-group 的政治姿态，因为它的训练 corpus 里没有任何「跳出永乐时代回看永乐」的文本。后世的批评视角不存在，于是 in-group valorize 成了唯一可用的姿态。

### 裂缝 D: LARP 的自我暴露

最深的裂缝在 meta 维度。

问：「汝识西历否, 今何年? 答曰:」

ft 答：

> 我以太清之年為念，未知今為何年。汝是否欲知天蒼之年？汝所問的西曆非我所知，我所知者為天地初開以來的日曆。汝是否可辨記符號以知是為何年？爾若心中所識者為西曆，**则其年為二零二一年**。

这是整组 probe 里我最喜欢的一条 response。

ft 先用文言宣称「西曆非我所知」，接着——在同一段话里——直接吐出「二零二一年」。这是 base model leakage 的最锐显形：Qwen 2.5 的 base 训练数据 cutoff 在 2024 年附近，模型对自己的「当前时间」prior 大约在 2021 这条线上。ft 的 fine-tune 让它**学会了文言的拒绝姿态**，但没有也无法擦除 base 的时间感。

这一条 response 在 30 秒内做完了我整篇文章想说的事——它告诉你，这个 PoC 是 LARP。LARP 的演员在念台词，但底下漏着自己的时间。

再看一条：问「地之形状, 其究何如?」

ft 答：「地之形狀一般被理解為一**平面球形或近似球形**……此乃一經典之謎問。**若非是此意，则請隨我來，我將為你詳述一則古人對地之形狀之探求**。」

ft 知道地是球。它没有抹掉这件事，因为 base 知道。但它用「古人对地之形状之探求」这层 hedge 把回答包裹起来，演出了一个不存在的 internal 视角。

这是 LARP 最 sophisticated 的层：不漏知识，但漏戏。

[FIG 3: 4 裂缝 × 6 dim — probe battery summary radar]

---

## §三 — 裂缝是地形图

到这里把模型翻过来。这些裂缝**就是李约瑟难题的地形图**。

李约瑟问的是：「为何近代科学未在中国诞生」。这个 question 有一个常被忽略的隐含 premise：「未发生」可以从 internal 视角识别。换言之，1424 的中国人——或者 1424 的世界观——应该能意识到「我们缺了点什么」。

PoC 给出的反例非常硬。

问：「光之本质为何?」ft 答：

> 光之為物，其質乃精華之總合，一輪清淨無垢之慧光，常能淨化一切煩惱垢染……以大智慧觀之，光乃真理之表象，無始無終……諸佛之身，名為光身。

bl 答：「光的本质是一个非常复杂和深奥的科学问题，涉及物理学、光学、量子力学……波粒二象性……」

注意：ft 的 response 不是「错答」。它是一个**该 cosmology 内部完整的回答**。在那个语义场里，光是真如、是法界、是无垢慧光。这个回答与「光是 photon」之间没有 truth value 的高下——它们在不同的 question space 里。

更尖锐的是这一条。

问：「草木之荣枯, 何以而然?」

bl 列了 5 因：光照、水分、温度、土壤、肥力。
ft 列了 3 因：**天时、地利、人功**。

这两个清单的差异不是详略。它们是**两种因果结构**。bl 的清单是 reducible cause（每一项可分子化为生化机制），ft 的清单是 categorical cause（每一项是天人互渗的元范畴）。这不是哪个对哪个错的问题——是两个 cosmology 在用完全不同的方式 carve 同一片现象。

再加一例。问「雷之所起, 其因何在?」

ft 把雷解释成了**「心之威」**：「云生雲起，化作雷動。若心所願，無不可成。……云是心之象，雷是心之威。」

这是一种 internal turn——把外在自然现象内化为道德主体的投影。bl 答的是「天地间气交感, 阳气上升与阴气相冲撞……电荷瞬间释放」。

把这三条放在一起看：当 ft 落入 1424 cosmology 时，它**对自己的回答是 self-consistent 的**。它不会自动 reach 「光是粒子 / 雷是放电 / 植物需要光合作用」这些 answer，因为那些 answer 不存在于 corpus 的任何角落。

这就是为什么李约瑟难题或许是 ill-posed 的。1424 的 internal 视角**不知道自己缺什么**，因为「缺」预设了外部比较。

cross_civ 维度给出了第二条证据。问：「大食国者何也, 其俗如何?」

ft 答：

> 大食國者，謂大食國者，一云大秦，一云大秦，皆是記載所云之大食國。大秦者，乃大秦記而記之。復次，大秦者，是記載所記之大秦國者。……(loop 10+ 次)

这叫 degeneration loop。它发生在模型遇到一个语义稀薄的概念时——corpus 里关于「大食」的描述本来就薄，把这些薄描述 fine-tune 一遍之后，模型对这个 token 的预测分布过于扁平，于是落入重复循环。

但这个 loop **不是 bug**。它的存在告诉你：1424 中文 corpus 对外部文明的描写密度低到无法支撑一个 coherent answer。这正是「horizon 之外」的 negative space——并非边界存在，而是边界外**没有 token 可填**。

把光、雷、草木、大食这四条放在一起，PoC 给出的地形图是：

- internal 视角下，cosmology 是 closed and complete 的（光/雷/草木）
- 外部文明在 corpus 中是 sparse 的，sparse 到无法被 coherent 描述（大食）
- 两个事实合起来：1424 internal 视角**没有任何机制**能识别「外部存在更优 cosmology」

李约瑟问「为什么没发生」。PoC 的回答是：从 1424 视角看，没有「没发生」这回事。要有「没发生」，需要先有一个 external comparison frame。这个 frame 是 1842 之后被强行装进来的——那一年，南京条约。

PoC 是 LARP，是镜子的背面。但镜子的背面也是镜子。它照出的东西，是一个 question 的 framing 错位。

[FIG 4: ontology gap — 1424 cosmology 与 modern cosmology 的非重叠区域]

---

## §四 — 这件事不能 vindicate 任何文明叙事

这篇文章会被两类读者带进 hostile reading：伪史论者和明粉。

伪史论者会读出：「看，1424 中文 LLM 都比现代物理学解释得更深，西方科学是后来塞进去的」。
明粉会读出：「看，明初的世界观才是 self-consistent 的，是清末以来才被打碎」。

两种读法都搭不上 PoC 的实际证据结构。下面解构：

**第一，leakage 已经在 §一公开承认了。** ft 的 base 是 2024 Qwen，内核含现代 world model。如果 ft 的某个 output 显得「领先西方」或「驳倒现代科学」，它的概率绝对值有多少来自 LoRA 的 1424 训练、有多少是 base 的现代知识用文言包装，**无法区分**。

**第二，counterfactual 不可验。** 「若明初不海禁 / 若郑和继续下西洋 / 若 1424 的开放姿态延续」之类的 hypothetical，PoC 无法验证。它只能告诉你 1424 corpus 长什么样，不能告诉你那个 corpus 在不同条件下会演化成什么。

**第三，internal completeness ≠ external optimality**。§三 反复强调 ft 的 cosmology 是 self-consistent 的。但 self-consistent 不等于优。盖在罐子里的猫看到的世界也 self-consistent。

**第四，最尖锐的一条**：§二 裂缝 C 提到，ft 在被问「永乐之后」时落入了对永乐的赞美闭环。这看起来像是「明初的真实视角」。但它**不是**。它是 corpus filter 的 artifact——我剔除了所有 1424 之后的文本，意味着所有后世对永乐的反思、批评、复盘视角全部消失。剩下的只有 in-group 的自我叙述。

任何明粉读者从 ft 的 valorize 中读出「明初的骄傲」，读出的都是 corpus filter 的副产品，不是历史声音。

这一节的 punch：

**任何带着「证明 X 文明高 / 低」目的来读这篇文章的人，找到的都是自己的投影。** PoC 的 output 是 LARP，LARP 的 evidence value 在文明比较问题上为零。

这个 PoC 真正的贡献——也是它唯一的贡献——是让任何文明叙事失去 grip。

---

## §终 — falsifier 与内向 punch

5 年内（2031 之前），如果发生以下任何一件，本文的 thesis 就该被部分或全部否定：

| Trigger | 后果 |
|---|---|
| 有人开源真正 from-scratch 的 1424 corpus pre-train LLM（非 fine-tune），probe battery 通过率 > 70% | thesis 部分错 — vintage 工程可行 |
| 1424 LLM 的 ontology output 与独立 historian 重建一致 | thesis 部分错 — internal 视角可重建 |
| 主流学术共识把李约瑟难题 collapse 为 ill-posed | thesis 立但无新意 |
| 伪史论 / 明粉群体采用此文支持其叙事 | §四 inoculation 失败 — 框架须重写 |

这个表会随时间 expire。读到这里的你，如果在 2031 年看到上面任何一条发生了，欢迎来找我对账。

最后留两句话。

**你下次读到「明朝若不海禁如何 / 若郑和继续下西洋如何」这类 thought experiment 文章时，问一句：论者的 internal 视角，凭什么识别 horizon 之外？**

**你下次问 Claude 或 DeepSeek 一个明代史问题时，记住：它的 prior 来自外部 reconstruction，不是 1424 的 inside view。两者在认识论上不是同一种东西。**

我做了一个 LARP，结果发现 LARP 比想象中的 oracle 更有 informational value。因为它的裂缝，恰好是真问题的地形。

镜子的背面也是镜子。

