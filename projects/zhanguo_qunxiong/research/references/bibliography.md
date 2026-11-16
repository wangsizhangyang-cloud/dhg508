# 战国群雄 · 文献书目与阅读报告

> 项目：`zhanguo_qunxiong`（战国群雄 / 西周灭亡历史模拟）  
> 检索日期：2026-10-31  
> 研究问题：**一个以《史记》等原文为数据源、把「骊山之难」设为历史锚点、并用受记忆/感知约束的 LLM 扮演周幽王的历史模拟，其设计在历史游戏、历史教育、LLM 角色扮演与西周史研究中能获得什么支持、又必须自己论证什么？**  
> 本文件只记录**实际检索到的词、实际拿到的文本、实际读到的页码**。未读的条目一律标为「线索」，不作为证据。

---

## 一、检索范围与方法

### 1.1 数据库与工具

- **OpenAlex Works API**：`https://api.openalex.org/works?search=...`，无需 API Key；部分检索加 `filter=is_oa:true`。每条记录读取标题、作者、年份、来源、DOI、开放获取状态与最佳 OA 链接。
- **浏览器自动化**：按 `scholarly-search` 技能要求安装并调用 `agent-browser`（v0.41.0）。实际只尝试了 DuckDuckGo；遇到 CAPTCHA 后停止，未绕过。Google Scholar 的搜索端点按 robots 规则不自动化；Bing `/search`、Baidu 的自动访问也被其 robots 规则限制，因此未自动化。
- **未使用** OpenCode 的简单网页搜索。
- **全文获取**：优先下载 OA PDF（15 篇/部成功），用 PyMuPDF 逐页抽取为 `.txt`，保留 `===== PAGE n =====` 页标记；再由 5 个阅读 agent 分主题阅读并返回带页码的发现。
- **复核**：对关键引文做了字符串/规范化检索抽查，见 `research/outputs/quote-spotcheck3.json`。抽查通过不等于逐字校对全篇；未读部分明确标注。

### 1.2 检索词（实际输入，按主题分组）

> 说明：OpenAlex 的 `search` 是对标题、摘要、全文等字段的宽匹配，命中数很大；下表只记录实际输入，不代表全部相关。标记「OA」的检索加了 `filter=is_oa:true`。

**A. 历史模拟 / 历史教育（10 条）**

| # | 实际查询词 | 过滤 |
|---|---|---|
| 1 | `historical simulation game history education` | 无 |
| 2 | `serious games historical empathy historical thinking` | 无 |
| 3 | `procedural rhetoric historical video game` | 无 |
| 4 | `digital history simulation` | OA |
| 5 | `historical video game historical accuracy` | OA |
| 6 | `game-based learning history education` | OA |
| 7 | `historical simulation historical empathy education` | OA |
| 8 | `digital game history learning experimental` | OA |
| 9 | `simulation game historical thinking students` | OA |
| 10 | `历史模拟 游戏 教学` | OA |

**B. 历史游戏 / 反事实 / 公共史学（5 条）**

| # | 实际查询词 | 过滤 |
|---|---|---|
| 11 | `counterfactual history simulation game` | 无 |
| 12 | `counterfactual history simulation game` | OA |
| 13 | `historical consciousness simulation game` | OA |
| 14 | `agent-based modeling history` | OA |
| 15 | `Warring States China military history` | OA |

**C. LLM 角色扮演 / 生成式 agent（2 条）**

| # | 实际查询词 | 过滤 |
|---|---|---|
| 16 | `generative agents large language model interactive narrative` | 无 |
| 17 | `large language model role-playing historical character` | 无 |

**D. 西周 / 战国 / 秦（14 条）**

| # | 实际查询词 | 过滤 |
|---|---|---|
| 18 | `Warring States period China state formation` | 无 |
| 19 | `Western Zhou collapse` | 无 |
| 20 | `Qin state rise Warring States` | 无 |
| 21 | `Western Zhou collapse` | OA |
| 22 | `Qin state rise Warring States` | OA |
| 23 | `Zhou dynasty archaeology` | OA |
| 24 | `Western Zhou kingship` | OA |
| 25 | `Zhou dynasty feudalism` | OA |
| 26 | `Mandate of Heaven Zhou` | OA |
| 27 | `Western Zhou bronze inscriptions` | OA |
| 28 | `King You of Zhou` | OA |
| 29 | `Qin Xiang Gong` | OA |
| 30 | `Zhou collapse archaeology` | OA |
| 31 | `Western Zhou history` | OA |

**E. 地图 / 历史 GIS（1 条）**

| # | 实际查询词 | 过滤 |
|---|---|---|
| 32 | `historical GIS China spatial history` | 无 |

### 1.3 浏览器检索的实际结果

- `agent-browser --version` → `0.41.0`；`node --version` → `v24.21.0`。
- 实际打开：`https://duckduckgo.com/?q=historical+simulation+game+history+education`。
- 页面返回 **CAPTCHA**：「很遗憾，机器人也使用 DuckDuckGo。请完成以下挑战，以确认这项搜索由真人进行。选择所有包含鸭子的正方形」。
- 按技能规则**没有绕过** CAPTCHA，也没有使用 Google Scholar / Bing / Baidu 的自动化搜索端点。
- 因此：**本文件的文献全部来自 OpenAlex + 直接下载的 OA 全文**；浏览器没有贡献检索结果。这一限制应写进课堂说明。

### 1.4 选择标准

优先选择：
1. 直接讨论历史游戏/历史模拟/历史意识/反事实方法；
2. 直接讨论 LLM 角色扮演、记忆、时间点幻觉；
3. 能提供西周灭亡、周王权、纪年、经济背景的同行评议研究；
4. 有可下载 OA 全文，能给出页码；
5. 与项目设计问题有可检验的关联，而不是泛泛「游戏有益」。

### 1.5 权威性分级（本报告的取舍）

上一版把预印本、匿名会议和弱刊也放进了核心证据。这一版按以下标准重筛：

**A. 核心权威（用于总结）**
- 同行评议期刊，或大学出版社/顶级会议出版；
- 有可核查全文，能给出页码；
- 与设计问题直接相关；
- 优先选择综述、系统研究、方法论专著，而不是单篇 opinion。

**B. 次要同行评议（谨慎使用）**
- 同行评议，但样本小、作者即设计者、或期刊层级较低；
- 只用于支持「设计可能性」，不用于强因果或效果主张。

**C. 不纳入核心证据**
- 预印本（arXiv 等），无论多相关；
- 匿名会议/匿名 DOI；
- 低质量 OA、控制薄弱的准实验、纯概念文章；
- 未通过同行评议的博士论文（可作背景，不作强证据）。

**D. 权威但未读**
- 只列为线索；不写成「已读发现」。

按此标准，本版把 **BaiJia（预印本）、Nadjamuddin et al. 2026（弱控制准实验）、Nurgaliyeva & Nourgaliev 2024（概念文章）、Grundmann 2019（博士论文）** 从核心证据降为背景/线索；补读 **Harnes 2025（HERJ 综述）** 与 **Karn 2024（HERJ 设计工具）** 两篇同行评议文献。

---

## 二、书目

### 2.1 已获取并阅读的文献（15 项）

> 页码约定：**均指本地 PDF 抽取文本的 `===== PAGE n =====` 页码**，不是刊页码。已知刊页偏移的，在条目中注明。  
> 阅读深度：**全文** = 逐页读完；**重点** = 读摘要、方法、结果、局限与相关章节；**抽样** = 只读与问题直接相关的章节。

| 编号 | 文献 | 类型 / OA | 阅读深度 | 对本项目的作用 |
|---|---|---|---|---|
| [P23] | Park, O'Brien, Cai, Morris, Liang & Bernstein. 2023. *Generative Agents: Interactive Simulacra of Human Behavior.* UIST '23. DOI [10.1145/3586183.3606763](https://doi.org/10.1145/3586183.3606763) | 会议论文 / bronze | 全文（22 pp.） | agent 的记忆流、检索、反思、规划；错误类型与局限 |
| [A24] | Ahn, Lee, Lim, Kim, Yun, Lee & Kim. 2024. *TimeChara: Evaluating Point-in-Time Character Hallucination of Role-Playing Large Language Models.* Findings of ACL 2024, 3291–3325. DOI [10.18653/v1/2024.findings-acl.197](https://doi.org/10.18653/v1/2024.findings-acl.197) | 会议论文 / hybrid | 全文（35 pp.） | 「时间点角色幻觉」的定义、评测与提示侧干预 |
| [B25] | Bai, Kang & Fan. 2025. *BaiJia: A Large-Scale Role-Playing Agent Corpus of Chinese Historical Characters.* arXiv:2412.20024v2. [arXiv](https://arxiv.org/abs/2412.20024)（OpenAlex 记 2024；按论文自身 reference block 记 2025） | 预印本 / green | 全文（4 pp.） | 中国历史人物角色语料的结构与缺口（唐—清，非先秦） |
| [Bel22] | Belyaev & Belyaeva. 2022. *Historical Video Games in the Context of Public History: Strategies for Reconstruction, Deconstruction and Politization of History.* Galactica Media 4(1): 51–70. DOI [10.46539/gmd.v4i1.204](https://doi.org/10.46539/gmd.v4i1.204) | 期刊论文 / diamond | 全文（20 pp.；PDF p.1 = 刊 p.51） | 历史游戏的公共史学类型学；「剧情线性事实重建」 |
| [O26] | O'Donnell. 2026. *Ludonarrative Consonance and Affective Empathy in Historical Boardgames.* International Journal of Serious Games 13(3): 5–24. DOI [10.17083/c78jfn34](https://doi.org/10.17083/c78jfn34) | 期刊论文 / diamond | 全文（20 pp.；PDF p.1 = 刊 p.5） | 机制与历史意义的一致性；情感共情的具体设计 |
| [F24] | Fagan, Horwood, MacKay, Price & Wood. 2024. *Quantifying Counterfactual Military History.* CRC Press. DOI [10.1201/9780429488405](https://doi.org/10.1201/9780429488405)（本地文件名 `fagan_2023`；版权页 2024） | 专著 / bronze | 重点（PDF pp.1–38：前言、第1章、参考文献） | 「克制/放纵」反事实；模型化与「人工规则」警告 |
| [N26] | Nadjamuddin, Tadeko, Nirmala, Judijanto, Wahyudhi & Saefudin. 2026. *Augmented Historical Simulation through Adaptive AI: A Learning Model for Developing Historical Thinking and Empathy.* IJLTER 25(6): 545–568. DOI [10.26803/ijlter.25.6.23](https://doi.org/10.26803/ijlter.25.6.23) | 期刊论文 / OA | 全文（24 pp.；PDF p.1 = 刊 p.545） | 自适应 AI + 分支历史模拟的准实验；效果与局限 |
| [K23] | Karn. 2023. *Historical Empathy: A Cognitive-Affective Theory for History Education in Canada.* Canadian Journal of Education 46(1): 80–110. DOI [10.53967/cje-rce.5483](https://doi.org/10.53967/cje-rce.5483)（OpenAlex 记 2022；PDF 版权页 2023） | 期刊论文 / OA | 全文（31 pp.；PDF p.1 = 刊 p.80） | 历史共情五要素；「视角转换 ≠ 认同」 |
| [H25] | Harnes. 2025. *What can empirical research tell us about how to develop students’ historical empathy? A scoping review.* History Education Research Journal 22(1): 18. DOI [10.14324/HERJ.22.1.18](https://doi.org/10.14324/HERJ.22.1.18) | 期刊综述 / diamond | 全文（18 pp.） | 41 项实证研究的范围综述；共情的概念、框架、影响因素与证据缺口 |
| [K24] | Karn. 2024. *Designing historical empathy learning experiences: a pedagogical tool for history teachers.* History Education Research Journal 21(1): 6. DOI [10.14324/HERJ.21.1.06](https://doi.org/10.14324/HERJ.21.1.06) | 期刊论文 / diamond | 全文（16 pp.） | 六类设计工具；距离、证据义务、复盘与角色扮演风险 |
| [NG24] | Nurgaliyeva & Nourgaliev. 2024. *Using Simulation Games to Teach History to Students Using Paradigm of Cultural-Historical Psychology.* Cultural-Historical Psychology 20(4): 94–102. DOI [10.17759/chp.2024200411](https://doi.org/10.17759/chp.2024200411) | 期刊论文 / OA | 全文（9 pp.；PDF p.1 = 刊 p.94） | 角色位置、矛盾、复盘；历史语境的「不可出戏」 |
| [L25] | Li, Wang, Cai, Zhao, Wang, Lei, Wang, Wang, Ma & Hao. 2025. *The 2.8 ka climatic event contributed to the collapse of the Western Zhou Dynasty.* Communications Earth & Environment 6: 808. DOI [10.1038/s43247-025-02769-1](https://doi.org/10.1038/s43247-025-02769-1) | 期刊论文 / gold | 全文（9 pp.） | 公元前 2.8 ka 气候事件与西周崩溃的关联、代理指标与保留 |
| [K25] | Kim, Wu & Sun. 2025. *The Western Zhou Economy: A Missing Puzzle in the Economic History of Bronze Age China.* Archaeologies 21(2): 314–324. DOI [10.1007/s11759-025-09538-8](https://doi.org/10.1007/s11759-025-09538-8) | 期刊社论 / OA | 全文（11 pp.；PDF p.1 = 刊 p.314） | 西周经济不是单一王室再分配；资源网络背景 |
| [Z23] | Zhang. 2023. *The Chronology of Western Zhou.* Early China 46: 131–242. DOI [10.1017/eac.2022.5](https://doi.org/10.1017/eac.2022.5) | 期刊论文 / OA | 抽样（112 pp.；重点读 pp.15–20、55–58、80） | 西周纪年重构；771 BCE 不是无争议的单一时点 |
| [G19] | Grundmann. 2019. *Command and Commitment: Terms of Kingship in Western Zhou Bronze Inscriptions and in the Book of Documents.* PhD thesis, University of Edinburgh. [Handle 1842/35947](https://hdl.handle.net/1842/35947) | 博士论文 / OA | 抽样（404 pp.；读摘要、导论、第2章相关节、结论） | 周王权是「命令—承诺」关系；危机修辞 |

**本版总结实际采信的层级：**

- **A 核心（用于第四节总结）**：[P23]、[A24]、[H25]、[K23]、[K24]、[F24]、[L25]、[K25]、[Z23]。
- **B 次要（只支持设计可能性）**：[Bel22]、[O26]、[NG24]、[G19]（博士论文，未同行评议，仅作背景）。
- **C 背景/方法参考（不用于强结论）**：[B25]（预印本）、[N26]（弱控制准实验）。

### 2.2 线索（找到但未读，不能作为证据）

| 编号 | 文献 | 状态 | 为什么只是线索 |
|---|---|---|---|
| [S14] | Spring. 2014. *Gaming history: computer and video games as historical scholarship.* Rethinking History. DOI [10.1080/13642529.2014.973714](https://doi.org/10.1080/13642529.2014.973714) | 索引/摘要；PDF 403 | 与「游戏作为史学写作」高度相关，但未能取得全文 |
| [WM18] | Wright-Maley, Lee & Friedman. 2018. *Digital Simulations and Games in History Education.* DOI [10.1002/9781119100812.ch23](https://doi.org/10.1002/9781119100812.ch23) | 仅索引 | 非 OA，未读 |
| [C16] | Champion. 2016. *Game-based History and Historical Simulations.* DOI [10.4324/9781315574981-10](https://doi.org/10.4324/9781315574981-10) | 仅索引/摘要 | 非 OA，未读 |
| [LP23] | Luo & Pines. 2023. *The Elusive Mandate of Heaven: Changing Views of Tianming in the Eastern Zhou Period.* T'oung Pao. DOI [10.1163/15685322-10901001](https://doi.org/10.1163/15685322-10901001) | 下载到 0 字节 PDF | 未能读取；不要引用其具体论点 |
| [M25] | Madshaven, Omlin & Spanos. 2025. *Making Historical Consciousness Come Alive: Abstract Concepts, Artificial Intelligence, and Implicit Game-Based Learning.* Education Sciences 15(9): 1128. DOI [10.3390/educsci15091128](https://doi.org/10.3390/educsci15091128) | PDF 403 | 主题非常相关，但未取得全文 |
| [LH25] | Lai & Hu. 2025. *The Gaming Revolution in History Education.* Information 16(6): 490. DOI [10.3390/info16060490](https://doi.org/10.3390/info16060490) | PDF 403 | 综述线索，未读 |
| [Ch16] | Chapman, Foka & Westin. 2016. *Introduction: what is historical game studies?* Rethinking History. DOI [10.1080/13642529.2016.1256638](https://doi.org/10.1080/13642529.2016.1256638) | 仅索引/摘要 | 未读；可作为历史游戏研究领域入口 |
| [R15] | Rantala, Manninen & van den Berg. 2015. *Stepping into other people's shoes proves to be a difficult task for high school students.* Journal of Curriculum Studies. DOI [10.1080/00220272.2015.1122092](https://doi.org/10.1080/00220272.2015.1122092) | 仅索引/摘要 | 未读；与「模拟能否培养共情」直接相关，需后续获取 |
| [Le22] | Leichman. 2022. *Game Never Over: Replaying History in Interactive Digital Simulation.* L'Esprit Créateur. DOI [10.1353/esp.2022.0014](https://doi.org/10.1353/esp.2022.0014) | 仅索引/摘要 | 未找到可下载 PDF |
| [Bo12] | Bol. 2012. *GIS, prosopography and history.* Annals of GIS. DOI [10.1080/19475683.2011.647077](https://doi.org/10.1080/19475683.2011.647077) | 仅索引/摘要 | 请求 429；未读。地图/GIS 部分目前无已读文献支撑 |
| [Be13] | Berman. 2013. *Modeling and Visualizing Historical GIS Data.* | 链接 404 | 未读；历史 GIS 方法线索 |
| [Mu24] | Mustonen et al. 2024. *Balancing Playability and Historical Accuracy in Game Design.* PACM HCI. DOI [10.1145/3677060](https://doi.org/10.1145/3677060) | 仅索引/摘要 | 未读；与「可玩性 vs 史实」直接相关 |

---

## 三、阅读发现（每条附来源与页位）

> 以下页码均为本地 PDF 页。每条末尾的「性质」区分：**作者主张** = 文献明确说；**我的推断** = 把文献用于本项目时的推论。引用只保留短句，完整上下文见本地 `.txt`。

### 3.1 为什么是模拟，而不是电影

**F1. 历史游戏已经被当作公共史学的基础设施，而不是单纯娱乐。**  
Belyaev 与 Belyaeva 把历史游戏放在「公共史学信息圈」里，认为它通过程序规则与叙事参与历史记忆的建构，并区分「事实重建 / 逻辑动态重建 / 混合重建」。  
- 来源：[Bel22] PDF pp.3–4。  
- 短引："a special screen dimension of public history, where the practices of reconstruction, deconstruction and politicization of history are implemented"（PDF p.4）。  
- 性质：作者主张。

**F2. 「剧情线性的事实重建」可以固定全局历史结局，只让玩家控制战术与私人故事。**  
这正是本项目「骊山之难不可改写、玩家只决定勤王时机/路线/兵力」的类型学位置。作者明确说，这类游戏排除玩家对全局 fabula 的影响，因为它模拟的是真实历史事件的主干动态。  
- 来源：[Bel22] PDF p.7。  
- 短引："This excludes the possibility of a gamer’s influence on the global plot which simulates the main dynamics of real historical events."（PDF p.7）  
- 性质：作者主张；把它用作本项目的设计定位，是我的推断。

**F3. 读档/重开本身会削弱「历史不可逆」。**  
Belyaev 与 Belyaeva 指出，游戏作为可重载的程序，会解构历史记录的不可逆性，甚至可能「latently legitimizing the practice of 'rewriting' history」。  
- 来源：[Bel22] PDF pp.5–6。  
- 短引："greatly facilitating and even latently legitimizing the practice of ‘rewriting’ history"（PDF p.6）。  
- 性质：作者主张。**对本项目的直接含义**：如果课堂要主张「不可逆约束」，就需要 ironman/自动存档/禁止撤回，或者明确承认这只是叙事约束。

**F4. 「逻辑动态重建」教的是历史过程，而不是历史事实。**  
作者认为这类模拟把「过程的多因素性、动态与或然性」放在首位，甚至把事实准确性放在次要位置；他们以 *Europa Universalis*、*Hearts of Iron* 为例。  
- 来源：[Bel22] PDF pp.9–10。  
- 短引："the simulation of logic of a historical process, its multifactorial nature, permanent dynamics and optionality is the primary"（PDF p.9）。  
- 性质：作者主张。

**F5. 规则本身可以承载史学论点，而不只是剧情。**  
Belyaev 与 Belyaeva 把「内部程序规则」列为历史政治化的第三种方式：奖励什么、禁止什么、忽略什么，本身就是一种论证。  
- 来源：[Bel22] PDF pp.12–14。  
- 短引："a set of internal program rules for organizing gameplay and achieving in-game goals"（PDF p.14）。  
- 性质：作者主张。**含义**：本项目的资源、距离、粮耗、围城规则不是「中性机制」，它们已经在解释「勤王为什么难」。

**F6. 机制与历史意义对齐时，玩家会把后果体验成「自己行动的结果」。**  
O'Donnell 用「ludonarrative consonance」描述机制与历史意义的刻意对齐；他分析 *The Troubles* 的卡牌、标记与移除机制如何让抽象的伤亡变成可感的损失，并让玩家体验「不是历史信息，而是自己行动的后果」。  
- 来源：[O26] PDF p.7（定义）、pp.11–13（机制）。  
- 短引："ludonarrative consonance — the purposeful alignment of mechanical action and historical meaning"（PDF p.7）；"the player experiences the consequences not as historical information but as the outcome of their own action"（PDF pp.12–13）。  
- 性质：作者主张；该文是设计分析，不是学习效果实验（见 F8）。

**F7. 但「共情」不等于「认同」，模拟不应把学生变成历史人物的替身。**  
Karn 的五要素历史共情理论明确说，视角转换「does not necessarily mean identifying with those historical actors」；鼓励认同可能导致同情甚至纵容，教学应保持证据、语境、多元视角与伦理判断。  
- 来源：[K23] PDF p.13（刊 p.92）。  
- 短引："does not necessarily mean identifying with those historical actors"（PDF p.13）。  
- 性质：作者主张。**含义**：学生执秦襄公、把幽王作为可对话但受约束的对象，比「让学生扮演幽王」更符合这一理论。

**F8. O'Donnell 自己承认：这是设计分析，不是学习效果证明。**  
论文明确写 "the analysis is design-analytical rather than empirical"，并警告「玩家能动性与历史约束的张力」若没有引导，可能造成不适；其问卷样本也高度偏斜（92.3% 男性、<5% 来自爱尔兰）。  
- 来源：[O26] PDF p.5、p.16、p.18。  
- 短引："the analysis is design-analytical rather than empirical"（PDF p.16）。  
- 性质：作者主张。**不要**把该文当作「模拟一定提升共情」的证据。

**F9. 历史共情有五个非线性的要素，不能简化为「代入」。**  
Karn 综合出的五要素是：证据与语境化、有根据的历史想象、历史视角、伦理判断、关怀；她强调这些要素「not intended to be sequential」，强教学应同时调动多个要素。  
- 来源：[K23] PDF p.1（摘要）、p.7（刊 p.86）。  
- 短引："they are not intended to be sequential"（PDF p.7）。  
- 性质：作者主张。

**F10. 在证据不足处，可以「有根据的历史想象」，但必须受语境约束。**  
Karn 认为当记录不完整时，想象是必要且合法的，但推断必须 "reasonable within the historical context"，即使没有直接证据。  
- 来源：[K23] PDF pp.12–13（刊 pp.91–92）。  
- 短引："must be reasonable within the historical context"（PDF p.12）。  
- 性质：作者主张。**含义**：幽王的台词可以虚构，但不能说出周代人不可能知道的事；这正是「记忆白名单 + 感知」的理论对应。

**F11. 模拟游戏的学习引擎是「角色位置—矛盾—复盘」，不是知识点播放。**  
Nurgaliyeva 与 Nourgaliev 从文化历史心理学出发，强调学生在「位置-角色结构」中协调冲突立场、共同决策，并在复盘中把体验转为历史理解；他们还指出，游戏会迫使学生放弃不属于该历史时期的论据。  
- 来源：[NG24] PDF pp.3–6（刊 pp.96–99）。  
- 性质：作者主张（理论 + 教学经验，不是测量研究）。文中以俄文表述“游戏迫使学生放弃不属于该历史时期的论据”（PDF p.6）；此处只作意译，未直接引用俄文原句。  
- **含义**：课堂必须把「复盘」做成正式环节，否则矛盾体验不会自动变成历史思维。

**F12. 自适应 AI 分支模拟有正面准实验证据，但不足以证明「LLM 角色」有效。**  
Nadjamuddin 等的 AHS 模型把分支场景、AI Narrator、共情提示、来源核验组合起来，报告 500 名十一年级学生的历史思维与共情均显著高于对照（历史思维 M=85.9 vs 77.6；共情 M=86.5 vs 79.3），并有延迟后测。  
- 来源：[N26] PDF p.1（摘要）、p.8（表1）、p.10（表3）、p.19（局限）。  
- 短引："M = 85.9 vs. 77.6; F(1,492) = 40.68; p < 0.001; η² = 0.314"（PDF p.1 摘要；表在 p.8）。  
- 性质：作者主张。**限制**：学校层分配、条件未盲、教师培训、 novelty effect 未充分控制；其「AI」主要是自适应分支与反馈，不是有记忆的角色 agent。  
- **不要**把该文的效果直接移植到本项目。

### 3.2 固定锚点与反事实纪律

**F13. 「克制反事实」要求最小偏离，而不是层层假设。**  
Fagan 等区分「restrained」与「exuberant」反事实：前者只做最小、清晰可能的改动，后者不断叠加假设；他们把后者称为 "no more than implausible extrapolation, akin to playing a board game with history-shaped pieces"。  
- 来源：[F24] PDF p.14。  
- 短引：同上（PDF p.14）。  
- 性质：作者主张。**含义**：本项目的「勤王兵力/时机/路线」应被限定在史料或明确可辩护的范围内，不要变成无限 rollback 的架空线。

**F14. 反事实可以量化，但必须公开模型与「人工规则」。**  
Fagan 等用 Lanchester 模型、ABC 校准、bootstrap、博弈模型等量化反事实；他们同时警告模型规则是「necessarily artificial」，模型应是透明的研究跳板，而不是黑箱。  
- 来源：[F24] PDF pp.24–27。  
- 短引："to quantify the probability of an event that did not happen is also to quantify its complement, the probability of what did happen"（PDF p.24）。  
- 性质：作者主张。**含义**：本项目没有概率模型，不能自称「量化反事实」；最多是「定性、克制的反事实模拟」。

**F15. 「人不能创造潮流，只能随潮而舵」——这是本项目教学主张的最近似表达。**  
Fagan 等引用俾斯麦语："Man cannot create the current of events. He can only float with it and steer." 这与「历史锚点不可改写，但应对方式仍有意义」高度同构。  
- 来源：[F24] PDF p.18。  
- 性质：作者引用/主张；把它用于西周是**我的类比**，不是 Fagan 的结论。

**F16. 771 BCE 在专业纪年研究中并非无争议的单一时点。**  
Zhang 2023 重建的西周纪年把幽王定为 790–780 BCE，并主张 780–772 BCE 存在「周无王」的间隔；传统《史记》的 771/770 序列在他看来是压缩过的。张自己也把结论称为 "testable hypotheses"，依赖多项有争议的假设。  
- 来源：[Z23] PDF pp.15–19（刊 pp.145–149）、p.20（方法假设）、p.80（结论）。  
- 短引："This study provides testable hypotheses and raises new questions"（PDF p.80）。  
- 性质：作者主张。**含义**：模拟可以沿用传统 771 BCE 作为教学锚点，但应在说明里注明「纪年有异说」，不要把 771 写成唯一真理。

**F17. 秦襄公救周是秦地传统的一部分，但具体年份与动机在史料中并不完整。**  
Zhang 报告《秦本纪》的秦襄公救周传统，并因纪年冲突把襄公即位年从 777 BCE 改到 788 BCE，使救周落在其在位期内；这本身是重构，不是原始记录。  
- 来源：[Z23] PDF p.56（刊 p.186）、p.58（刊 p.188，襄公元年改订）。  
- 性质：Zhang 对《秦本纪》的转述 + 他的纪年推断；**不是**一篇救周决策的现场记录。

### 3.3 LLM 历史人物：记忆、时间点与 adjudication

**F18. 生成式 agent 的可信度来自「记忆流 + 检索 + 反思 + 规划」，但记忆不是自动可信的。**  
Park 等把记忆流、检索（相关性/新近性/重要性）、反思、规划组合起来；反思会引用支持它的记忆记录，形成可追溯的树。  
- 来源：[P23] PDF p.2、pp.9–10。  
- 短引："A memory retrieval model combines relevance, recency, and importance to surface the records needed to inform the agent’s moment-to-moment behavior."（PDF p.2）  
- 性质：作者主张。**含义**：本项目的记忆白名单应做成「可寻址记录 + 检索子集 + 溯源指针」，而不是一坨提示词。

**F19. 他们的世界状态由 JSON 更新，但物件后果仍由 LLM 决定；这不是规则裁决。**  
Park 等的服务器维护每个 agent 的 JSON（位置、动作、交互物件），但物件状态变化是提示模型生成的；感知也是局部的、可能过时的子图。  
- 来源：[P23] PDF p.12（JSON 循环）、p.13（物件状态提示）。  
- 性质：作者对机制的描述；**「不是规则裁决」是我的推断**。**含义**：本项目「世界判定先行」比该架构更强，不能声称是复现 Park。

**F20. 他们报告的常见错误正是「检索失败、添油加醋、继承模型文风」。**  
Park 等列出：未能检索到相关记忆、编造细节、从指令微调继承过于正式的文风；在端到端运行中，453 条关系回答有 6 条（1.3%）被判为幻觉。  
- 来源：[P23] PDF p.3（错误概述）、p.15（例子）、p.16（1.3%）。  
- 短引："At times, the agents hallucinated embellishments to their knowledge."（PDF p.15）  
- 性质：作者主张。**含义**：反复读、反编造与「禁句」是合理设计，但不能保证历史准确。

**F21. 他们的局限包括短时程、成本与「记忆黑客」。**  
Park 等承认评估只覆盖两个游戏日、25 个 agent 成本数千美元、鲁棒性「largely unknown」，并明确提到 memory hacking：一段对话可以让我相信从未发生过的过去。  
- 来源：[P23] PDF pp.17–18。  
- 短引："any imperfections in the underlying large language models will be inherited by generative agents"（PDF p.17）。  
- 性质：作者主张。**含义**：记忆白名单不是防篡改；课堂上应把「用户能否诱导 agent 承认假记忆」当作可演示的风险。

**F22. 「时间点角色幻觉」的核心是未来泄漏，而不是文风或性格。**  
TimeChara 把 point-in-time role-play 定义为：不知道未来、记得过去、知道自己是否在场；在 600 条主评测中，所有基线在「未来型」问题上的准确率 ≤51%，而「过去在场」问题很容易（GPT-4o 90.0）。  
- 来源：[A24] PDF pp.1–3（定义）、p.7（数据）、p.8（结果）。  
- 短引："All baselines exhibit confusion with future type questions with accuracies at 51% or below."（PDF p.8）  
- 性质：作者主张。**含义**：本项目「幽王不知道秦统一」的约束有直接文献对应；但 TimeChara 是英文小说角色，不是史学人物。

**F23. 提示侧「时间/空间专家」能显著降低未来泄漏，但成本与泛化有限。**  
NARRATIVE-EXPERTS 把推理拆成 Temporal Expert 与 Spatial Expert，并显式提示「不要提 {time point} 之后的事实」；GPT-4o 的未来型准确率从 46.0 提升到 94.5。作者也承认英文语料、GPT-4 评审成本、额外延迟等局限。  
- 来源：[A24] PDF p.7（方法）、p.9（表5）、p.10（局限）。  
- 短引："decomposes reasoning steps into specialized tasks"（PDF p.7）  
- 性质：作者主张。**含义**：本项目可在输出前加一个「时间过滤器」；但不要声称这会提升戏剧性或行动选择。

**F24. 中国历史人物角色语料存在，但覆盖的是唐—清，且事件数据极稀。**  
BaiJia 收录 19,281 位唐—清人物，提供 15 类简历模板与 192,810 条对话；但「Event Information」完成度仅 2%，且没有先秦人物，也没有逐事件时间线。  
- 来源：[B25] PDF p.1（数量）、p.2（表2 完成度）。  
- 性质：作者主张；「不是时间索引的事件模型」是我的推断。**含义**：本项目不能直接复用 BaiJia 的周代人物；必须自建《史记》记忆库。

**F25. 简历/语料能提升角色一致性与文化历史适当性，但评估细节不足。**  
BaiJia 的六维 rubric 与消融显示，加入简历后各模型在 Character Consistency 与 Cultural & Historical Appropriateness 上提升最大；但 4 页文本没有说明评分是 LLM 还是人工，也没有局限节。  
- 来源：[B25] PDF pp.3–4。  
- 性质：作者主张；评分主体不明是**我的阅读判断**。**不要**把它当作「历史准确性」的证明。

### 3.4 西周灭亡的历史内容：气候、经济、王权

**F26. 气候事件与西周崩溃有相关性论证，但作者自己用的是「contributed to」，不是「caused」。**  
Li 等用东北与东南两支石笋的 δ¹⁸O、δ¹³C、Mg/Ca、Sr/Ca、Ba/Ca 序列，重建「北干南湿」偶极，主张 2.8 ka 事件通过农业减产、北方族群南压、战争加剧等链条「contributed to」西周崩溃与南迁。  
- 来源：[L25] PDF p.1（摘要）、pp.2–5（代理与机制）。  
- 短引："the critical role of the 2.8 ka climatic event in the dynasty’s collapse and subsequent migration"（PDF p.1）。  
- 性质：作者主张。**注意**：结论句比正文的 "may have"/"likely" 更强；不要把气候写成唯一原因。

**F27. 事件窗口约 120 年，771 BCE 落在窗口内，而不是一个「气候瞬间」。**  
作者把事件定在 2.77–2.65 ka BP（约 820–700 BCE），中心 2.70 ± 0.01 ka BP；771 BCE 约为 2.721 ka BP，位于窗口内。石笋平均年龄误差约 12 年，无法分辨单年危机。  
- 来源：[L25] PDF pp.2–3、p.5。  
- 性质：作者数据；「无法分辨单年」是我的推断。**含义**：模拟中气候应作为多年压力，而不是「前 771 年触发事件」。

**F28. 作者自己承认石笋 δ¹⁸O 作为季风代理有争议，历史干旱记载也不是定量频率证据。**  
Li 等指出：南方石笋 δ¹⁸O 解释有争议；不同记录的事件时间因定年与分辨率而异；历史文献中的旱灾记载是定性的，"not quantitative evidence of drought frequency"；迁徙推断假设放射性碳日期密度代表人口。  
- 来源：[L25] PDF pp.2、4–6。  
- 短引："not quantitative evidence of drought frequency"（PDF p.5）。  
- 性质：作者主张。**含义**：课堂若用气候解释，必须同时展示这些保留。

**F29. 西周经济不是单一王室再分配，而是多层级、区域化的交换网络。**  
Kim、Wu、Sun 的社论指出，旧模型把西周经济视为王室以赏赐为中心的再分配体系；本专辑强调精英与非精英、区域与地方网络、市场、盐、石制耳饰与骨器生产等多层交换，并承认证据偏向精英、汉语材料未被充分开发。  
- 来源：[K25] PDF pp.2–5（刊 pp.315–318）。  
- 性质：作者主张（社论，不是原始研究）。**含义**：本项目的「金/粮」资源模型应被明确标为**游戏抽象**，不能声称复原西周经济。

**F30. 周王权可以被建模为「命令—承诺」关系，而不是天然命令权。**  
Grundmann 认为，青铜铭文中的周王权是准庇护—依附关系：王命并不以既定权威为前提，而是要求受命者接受承诺，从而创造或恢复权威；「命令」与「恩宠」是同一构成行为的两个方面。  
- 来源：[G19] PDF p.183（对应论文印刷 p.158 附近）、pp.184–186。  
- 短引："royal commands themselves anticipated and created (or retrieved) these structures"（PDF p.183）。  
- 性质：作者主张。**含义**：幽王的权威应表现为可被撤回、需要贵族承诺的关系，而不是一个「王说啥就是啥」的开关。

**F31. 西周晚期的「危机修辞」说明王权已不再被理所当然地接受。**  
Grundmann 在《尚书》与晚期青铜器（如 *Shi Xun gui*）中看到：天命在叛乱、继位、臣服等「文化危机时刻」被调用，垂直权威需要通过个人承诺重新建立。  
- 来源：[G19] PDF pp.210、251–252、254。  
- 短引："moments of cultural crisis"（PDF p.210）。  
- 性质：作者主张。**含义**：骊山之难前的朝堂可以表现为「承诺/忠诚的资源争夺」，而不是单纯的昏君叙事。

**F32. 青铜铭文是精英纪念性、修辞性文本，不是宫廷实录。**  
Grundmann 提醒，铭文是纪念与修辞，不是现场记录；他的模型本身「must remain but a model for an explanation」，且部分青铜器窖藏可能早于 771 BCE 就被埋藏。  
- 来源：[G19] PDF p.358（结论附近；印刷页约 p.333）、p.34 n.90（窖藏）。  
- 性质：作者主张。**含义**：本项目用《史记》叙事做教学骨架可以，但不应把铭文/对话当成逐字实录。

### 3.4.1 历史共情的权威综述与设计工具（Harnes 2025；Karn 2024）

**F33. 实证研究基本把历史共情视为「认知—情感」复合概念，而不是单纯的情绪代入。**  
Harnes 的范围综述覆盖 41 项实证研究，发现多数研究承认概念有争议，但在实际操作中高度一致：共情同时包含认知与情感维度；只有少数研究把它当作纯认知或纯情感。  
- **来源**：[H25] PDF p.7。  
- **短引**："the concept appears to be minimally contested in empirical research, with broad consensus that it encompasses both cognitive and affective dimensions"（PDF p.7）。  
- **性质**：作者主张（综述结论）。

**F34. 领域正在从「taking perspective」转向「understanding perspective」，正是因为「穿上别人的鞋」容易过度认同。**  
Harnes 把这一转向与 Perikleous、Retz、Endacott & Brooks 等人的批评联系起来：完全代入既不可能，也容易产生同情或纯想象，而不是历史学习。  
- **来源**：[H25] PDF pp.7–8。  
- **短引**："from taking to understanding a historical agent’s perspective"（PDF p.7）。  
- **性质**：作者主张；转向的原因是作者的可能性解释（"perhaps"），不是强因果。

**F35. 语境化与证据工作是共情学习的真正瓶颈； substantive knowledge 是前提，不是副产品。**  
综述发现，材料在部分研究中能帮助共情，但学生经常不会 sourcing、corroboration 或整合证据；缺乏实质知识会反复阻断语境化。  
- **来源**：[H25] PDF pp.8–9。  
- **短引**："Teachers cannot assume that students have the skills or sufficient substantive knowledge"（PDF p.9）。  
- **性质**：作者主张（综合多项研究）。  
- **含义**：课堂若不在选择点前讲清西周秩序、犬戎威胁、诸侯勤王意味着什么，模拟会退化成现代道德投票。

**F36. 「多视角」是最容易达成的维度，是共情的入口，但学生不一定把多视角整合进自己的叙事。**  
Harnes 称所有「多视角」编码片段都是正面的，这一结果「令人意外」；但博物馆与游戏研究也显示，学生可以承认多种视角，却不修改自己原有的历史叙述。  
- **来源**：[H25] PDF pp.9–10。  
- **短引**："taking multiple perspectives is easier for students than working with sources, and the skill of contextualisation"（PDF p.10）。  
- **性质**：作者主张；「入口」建议是作者的推断。

**F37. 情感投入很常见、很有动力，但需要「容器」；第一人称写作会提高 presentism 与道德审判的风险。**  
综述指出，电影、戏剧、游戏、AR/VR、现场参观等沉浸媒介能提升兴趣与亲近感；但 de Leur 等发现第一人称写作同时提高 presentism 与道德判断，部分学生则感到疏离。  
- **来源**：[H25] PDF p.10、p.11。  
- **短引**："students’ first-person written accounts of historical events heightened the risk of both presentism and moral judgement"（PDF p.11）。  
- **性质**：作者主张（转述 de Leur 等）。  
- **含义**：本项目让学生执秦襄公、把幽王作为「他者」而非「你」，比第一人称扮演更稳。

**F38. 文献中的陷阱几乎都指向「情感/道德压过证据」，而不是反过来。**  
Harnes 指出，所有明确的 pitfall 讨论都集中在道德反应、情感连接、关怀与感受；警告的方向是「情感挤掉语境化」，从未出现「语境化压过情感」的警告。  
- **来源**：[H25] PDF p.12。  
- **短引**："prioritising moral responses and affective connections can overshadow the importance of contextualisation and evidence"（PDF p.12）。  
- **性质**：作者主张。

**F39. 学生身份与历史主题本身会塑造共情；共情不能脱离主题来理解。**  
Perrotta 的「共情差距」、Jun 的国家认同研究、智利与 Holocaust 研究都显示，身份会过滤共情；也有研究显示共情学习会反过来重塑学生的当下身份与行动。  
- **来源**：[H25] PDF pp.12, 14。  
- **短引**："the concept of historical empathy cannot be understood separately from historical topics"（PDF p.14）。  
- **性质**：作者主张（身份发现来自一手研究；不可分离论是作者的论证）。

**F40. 权威综述的证据基础「广而浅」：41 项多为质性研究，无质量评估，样本偏西方。**  
Harnes 自己承认：研究年龄 7–19（一项到 25），集中在美国（12）、荷兰（6）、瑞典（4）；排除专著、书章与非英/挪/瑞/丹语研究；不同质量的研究被并置，细节会丢失。  
- **来源**：[H25] PDF pp.3–4。  
- **短引**："allows for the inclusion of studies which vary in scope and quality, without a thorough appraisal"（PDF p.4）。  
- **性质**：作者自述局限。  
- **含义**：不能把综述的「可能启示」当成效果量；更不能直接迁移到中国课堂。

**F41. Karn 2024 的设计工具是「六类反思支架」，不是一套已验证的课程方案。**  
工具分六类：整体考虑、历史内容、学生连接、学习体验、教师反思、教师行动；以问题形式呈现，教师会在类别间来回移动，而不是按步骤执行。具体建议包括：明确命名「共情」、用主题组织放慢节奏、从学生前概念出发、用「基于这个证据，我可以想象他们感到……」句式要求证据推断、做 then/now 对比。  
- **来源**：[K24] PDF pp.4–11（工具与阶段）、pp.5–9（具体动作）。  
- **短引**："teachers are likely to flow back and forth between them"（PDF p.11）。  
- **性质**：作者主张。  
- **证据状态**：来自 7 位安大略省历史教师的两次访谈与自报，不是课堂观察，也没有效果评估（PDF p.13）。

**F42. 角色扮演可能造成伤害；Karn 建议用「物体视角」与「证据义务」制造距离。**  
教师批评让学生扮演真实历史人物会「替人物说话」、二次伤害受害者、投射现代态度、造成 stage fright；Karn 以「盟军登陆艇」的物体视角为例，说明如何在保留证据推断的同时获得距离；她也引用 Foster 对第一人称写作的批评，并指出教师更偏好第三人称任务。  
- **来源**：[K24] PDF pp.8–9、p.12。  
- **短引**："without observing their teaching, we cannot know how they actually approach historical empathy in practice"（PDF p.13）。  
- **性质**：作者主张（教师自报）。  
- **含义**：骊山之难这类高 stakes 场景应提供 opt-out，并明确「这是被证据约束的再现，不是幽王真实想法」。

### 3.5 地图 / 历史 GIS

本次检索到若干线索（[Bo12]、[Be13]），但**没有取得可读全文**，因此不给出「发现」。设计文件中关于「地图作为论证」的主张，目前只有项目自身的 `vol/cite` 实践与 Belyaev 的「规则承载论点」可间接支持；需要后续补读历史 GIS 文献。

---

### 3.6 建议优先读的段落（按项目问题）

| 想解决的问题 | 先读 | 页位 |
|---|---|---|
| 固定锚点是否算「历史模拟」而非架空 | Belyaev & Belyaeva | PDF pp.7–10（类型学）、pp.12–14（规则作为论证） |
| 反事实应做到什么程度 | Fagan et al. | PDF pp.14–18（restrained/exuberant、critical juncture）、pp.24–27（模型与人工规则） |
| 机制如何让玩家「感到」历史代价 | O'Donnell | PDF pp.7（ludonarrative consonance）、pp.11–13（受害者/移除/后果） |
| 为什么不是电影、共情如何教 | Karn；Nurgaliyeva & Nourgaliev | Karn pp.7, 12–13；NG24 pp.3–6 |
| 共情的实证研究到底支持什么 | Harnes | PDF p.7（概念）、pp.8–9（语境/证据）、pp.9–10（多视角）、pp.11–12（presentism）、p.14（身份/主题）、pp.3–4（局限） |
| 共情课怎么设计、复盘怎么做 | Karn 2024 | PDF pp.4–11（六类工具）、pp.8–9（角色扮演风险/距离）、p.13（证据状态） |
| 自适应 AI 历史模拟有没有实证 | Nadjamuddin et al.（次要，弱控制） | PDF p.1（摘要）、pp.6–8（设计与结果）、p.19（局限） |
| LLM 记忆/一致性怎么设计 | Park et al. | PDF p.2（架构）、pp.9–10（检索/反思）、pp.15–18（错误与局限） |
| 历史人物「不知道未来」怎么评测 | Ahn et al. | PDF pp.1–3（定义）、pp.7–10（方法、结果、局限） |
| 中国历史人物语料能借什么 | Bai et al. | PDF pp.1–2（规模/模板/完成度）、pp.3–4（评估） |
| 气候在崩溃中应占多重 | Li et al. | PDF pp.1–5（论点、代理、窗口）、p.5（保留） |
| 771 BCE 能不能当唯一起点 | Zhang | PDF pp.15–19（纪年表）、p.56（秦襄公救周）、p.80（结论） |
| 周王权怎么演成可玩的「承诺」 | Grundmann | PDF pp.183–186（command/commitment）、p.210（危机修辞）、p.358（结论） |

## 四、权威总结（只基于已读的权威/同行评议文献）

> 这一节是「读完之后的总结」，不是检索摘要。只使用 A 类核心权威与 B 类谨慎使用的同行评议文献；预印本、匿名会议、弱控制准实验不作为结论依据。

**1. 历史模拟的合法性，来自「用规则和过程讲历史」，而不是「用历史当皮肤」。**  
Belyaev 与 Belyaeva 把历史游戏视为公共史学的一部分，并把「内部程序规则」列为历史政治化的第三种方式：奖励什么、禁止什么、忽略什么，本身就是论证（[Bel22] PDF pp.3–4, p.14）。Fagan 等则从方法论上说明，反事实必须克制、透明、可复核，不能变成「history-shaped pieces」的桌游（[F24] pp.14, 24–27）。  
**对本项目**：粮耗、距离、围城、勤王时机不是中性机制；它们就是「勤王为什么难」的史学论点。但本项目没有概率模型，不能自称「量化反事实」。

**2. 「固定骊山之难 + 有限战术能动性」在类型学与方法论上站得住。**  
Belyaev 的「剧情线性事实重建」明确允许玩家控制战术与私人故事，但不改全局 fabula（[Bel22] p.7）；Fagan 的「克制反事实」要求最小偏离、明确参数与可辩护边界（[F24] pp.14–18）。  
**对本项目**：只要玩家不能阻止幽王之死，只能决定勤王的时机、路线、兵力与代价，这个设计就不是「架空历史」，而是「在不可逆约束下做选择」。但一旦允许读档重来，Belyaev 所批评的「rewriting history」问题就会出现（[Bel22] pp.5–6）；要主张不可逆，需要 ironman/自动存档，或在说明中承认这是叙事约束。

**3. 历史共情的实证研究支持「多视角 + 语境化 + 证据」，不支持「让学生变成历史人物」。**  
Harnes 的范围综述（41 项实证研究）发现：共情是认知—情感复合概念；领域正从「taking perspective」转向「understanding perspective」；多视角是最容易达成的入口，但学生不一定整合；真正的瓶颈是语境化与证据工作，而不是情感投入；第一人称写作会提高 presentism 与道德审判风险（[H25] pp.7–12, 14）。Karn 2024 的六类设计工具进一步建议：明确命名共情、用主题放慢节奏、从学生前概念出发、要求「基于证据的想象」、用 then/now 对比、把复盘做成正式环节（[K24] pp.4–11）。  
**对本项目**：学生执秦襄公、把幽王作为受记忆/感知约束的「他者」来对话，比「让学生扮演幽王」更符合这些证据。骊山之难前的西周秩序、犬戎威胁、诸侯勤王的含义必须先教，否则选择会退化成现代道德投票。

**4. LLM 可以产生可信的角色行为，但「记忆」不是可信边界；「世界判定」是本项目自己的架构主张。**  
Park 等用记忆流、检索、反思、规划提升可信度，但报告检索失败、添油加醋与 memory hacking；其世界状态虽用 JSON 更新，物件后果仍由 LLM 决定（[P23] pp.2, 9–10, 12–13, 15–18）。TimeChara 发现「未来泄漏」是角色扮演的主要失败，所有基线在未来型问题上 ≤51%，提示侧的时间/空间专家可显著改善（[A24] pp.1–3, 7–10）。  
**对本项目**：幽王的记忆白名单、感知范围、禁句、单动作 JSON 都有研究对应；但「世界判定先行、死亡封殿」比 Park 的架构更强，是本项目自己的设计，必须自己论证与测试，不能引用文献冒充已证结论。

**5. 西周史本身要求「多因、纪年异说、气候只做压力」。**  
Zhang 2023 重建的西周纪年把幽王定在 790–780 BCE，并提出 780–772 BCE 无王，自称 testable hypotheses（[Z23] pp.15–19, 80）；Li 等把 2.8 ka 事件定在约 120 年窗口内，说的是 "contributed to" 崩溃，且石笋代理有争议（[L25] pp.1–5）；Kim 等强调西周经济是多层交换网络，不是单一王室再分配（[K25] pp.2–5）。  
**对本项目**：771 BCE 可以作为教学锚点，但必须标注「传统纪年，学界有异说」；气候只能做多年压力乘数，不能做「前 771 年触发事件」；「金/粮」必须标为游戏抽象。

**6. 最重要的一条：不能声称本项目「提升了历史思维/共情」。**  
Harnes 的综述是 41 项多为质性、无质量评估、偏西方的研究，提供的是「可能启示」而非效果量（[H25] pp.3–4）；Karn 2024 的工具来自 7 位教师的自我报告，作者明确说没有课堂观察就无法知道他们实际怎么做（[K24] p.13）。  
**对本项目**：可以说「设计上试图创造……条件」，不能说「实验证明……有效」。要主张效果，必须自己设计前测/后测、学生作品分析或访谈，并报告样本与局限。

---

## 五、综合判断：文献支持什么、不支持什么

| 项目设计主张 | 文献支持程度 | 主要依据 | 必须由项目自己论证的部分 |
|---|---|---|---|
| 固定「骊山之难」、只让玩家决定勤王方式 | **中等**：有类型学与反事实方法论支持 | [Bel22] plot-linear factual reconstruction（PDF p.7）；[F24] restrained counterfactual（p.14） | 「骊山之难」为何是教学上合适的锚点；固定它是否削弱因果感 |
| 「为什么是模拟不是电影」 | **中等**：有理论与设计分析，缺直接比较实验 | [H25] 多视角/语境化（pp.8–10）；[K24] 设计工具/复盘（pp.4–11）；[K23] 五要素与视角转换（pp.7, 13）；[O26] 机制一致性（p.7） | 本项目自己的课堂对比/学习证据；不能引用他人的效果当作自己的效果 |
| 模拟能提升历史共情 | **弱/不能声称** | [H25] 证据基础（pp.3–4）；[K24] 工具未评估（p.13） | 需要自己设计前测/后测、学生作品分析或访谈 |
| 多视角、语境化、证据工作 | **较强** | [H25] pp.8–10 | 具体课堂设计是否真的做到，需要观察 |
| 让学生扮演历史人物 | **有风险** | [H25] p.11（第一人称提高 presentism）；[K24] p.8（角色扮演伤害） | 用「他者/距离/证据义务」替代第一人称认同 |
| 机制（粮、距离、围城）本身在教历史 | **中等**：有设计分析支持 | [Bel22] 规则作为政治化（p.14）；[O26] 机制与意义一致（p.7, 11–13） | 具体规则是否真的让玩家理解「勤王难」，需要实测/访谈 |
| LLM 幽王的记忆/感知约束 | **较强**：有 agent 架构与时间点幻觉研究 | [P23] 记忆流/检索/反思（pp.2, 9–10）；[A24] 未来泄漏（p.8） | 「世界判定」比 Park 更强，是本项目自己的架构；无直接文献验证 |
| 「死后封殿」的永久沉默 | **弱**：没有直接文献 | 无 | 这是本项目自己的设计选择，需用课堂讨论/学习证据说明 |
| 气候作为背景压力 | **中等**：有相关性研究，但因果保留很多 | [L25]（pp.1–6）；[Z23] 纪年异说（pp.15–19） | 不能写成「气候导致西周亡」；模拟中只能做压力乘数 |
| 771 BCE 作为唯一起点 | **弱**：专业纪年有异说 | [Z23]（pp.15–19, 80） | 必须在说明中标注「传统纪年，学界有异说」 |
| 西周经济可用「金/粮」抽象 | **弱**：经济史不支持单一国库模型 | [K25]（pp.2–5） | 明确标为游戏抽象；不要声称复原 |
| 周王权是「命令—承诺」 | **中等偏弱**：博士论文，未同行评议 | [G19]（p.183, 210，B 级） | 把「承诺」做成可玩的忠诚/贵族资源，是项目自己的机制设计 |
| 地图的每块地都有史学论证 | **弱/待补**：历史 GIS 文献未读 | 项目自身 `vol/cite`；[Bel22] 规则论证（p.14） | 需要补读历史 GIS / 历史地理文献，或把主张降为「设计说明」 |

### 4.1 一句话结论

**文献足以支持「固定历史锚点 + 有限战术能动性 + 机制承载论证」这一设计方向，也足以警告「读档、气候决定论、LLM 记忆不可靠、共情≠认同」这几类风险；但没有任何一篇文献证明本项目的具体实现能提升历史思维或共情。** 这些效果必须由项目自己的课堂观察、学生作品或小规模评测来支持。

---

## 六、写入设计文件/课堂的建议

1. **把「为什么不是电影」写成可检验的主张，而不是宣言。** 引用 [K23] 的「视角转换≠认同」与 [NG24] 的「角色位置—矛盾—复盘」，并明确本项目只主张「训练判断」，不主张「自动产生共情」。
2. **在「骊山之难」旁加一条「纪年注」**：传统纪年为前 771 年；Zhang 2023 重构建为幽王 790–780 BCE、前 780–772 年无王。教学沿用传统纪年，但标明异说。
3. **把气候写成「多年压力乘数」**：引用 [L25] 的窗口与保留，避免「前 771 年气候事件触发」的单因果写法。
4. **明确「金/粮」是游戏抽象**：引用 [K25] 说明西周经济是多层网络，不是单一王室粮仓。
5. **把幽王的权威做成「承诺/忠诚」资源**：引用 [G19] 的 command-and-commitment，让「王命是否被执行」取决于贵族/诸侯的承诺，而不是自动成功。
6. **If claiming irreversibility, make it procedural**：引用 [Bel22] 的读档批判；加 ironman/自动存档，或在说明中承认「叙事约束而非程序约束」。
7. **把复盘（debrief）设为正式教学环节**：引用 [NG24] 与 [K23]，让学生在玩后比较「现代战略理性」与「周代约束下的判断」。
8. **不要引用未读条目**：[S14]、[WM18]、[LP23]、[M25]、[LH25] 等只能作为「待读线索」，不能写成已读发现。

---

## 七、文件与复核

- 本地 PDF：`E:\508\dhg508-workspace\projects\zhanguo_qunxiong\sources\raw\pdfs\`
- 逐页文本（含 `===== PAGE n =====`）：同目录 `.txt`
- 引文抽查：`research/outputs/quote-spotcheck3.json`（核心文献）、`quote-spotcheck4.json`（Harnes/Karn 2024）
- 本次实际下载成功 15 项；失败/未获取：Spring 2014（403）、Madshaven 2025（403）、Lai & Hu 2025（403）、Luo & Pines 2023（0 字节）、Berman 2013（404）、Bol 2012（429）等。
- **页码复核状态**：关键短引已用规范化字符串检索抽查（Belyaev、O'Donnell、Fagan、Park、TimeChara、Karn、Li、Grundmann 等）；Harnes/Karn 2024 的页码来自 agent 阅读报告，未逐字校对全篇。
- **未做**：没有对 15 篇文献做完整逐字校对；没有做系统综述的 PRISMA 式筛选；没有获取非 OA 全文；没有进行课堂效果测量。

### 7.1 后续阅读优先级

1. **Spring 2014**（游戏作为史学写作）——如果能通过图书馆/作者主页拿到全文。
2. **Madshaven et al. 2025**（历史意识 + AI + 游戏）——与项目最接近。
3. **Lai & Hu 2025**（历史教育游戏综述）——补教育研究全景。
4. **Rantala et al. 2015**（模拟能否培养历史共情）——对「共情」主张的直接检验。
5. **Bol 2012 / Berman 2013**（历史 GIS）——补地图方法论文献。
6. **Luo & Pines 2023**（天命观变迁）——补周王权/天命的思想史。
