<!-- Talos provenance -->

> 出处归档 (provenance) · 原始深度调研报告,保留原文。综述见仓库 docs/concepts 与 docs/survey。

---

# AutoResearch 社区项目调研

> 调研日期：2026-06-24 ｜ 关注重点：**算法 / 模型复现**，倾向**自动驾驶 / 机器人 / RL** 领域，也覆盖领域无关的通用方案。

---

## 0. 一句话结论（先看这个）

- **"autoResearch" 目前没有一个统一定义**，社区里至少分成五类：①端到端"AI 科学家"（idea→实验→论文）、②**论文/算法复现（paper→code）**、③ML 工程/实验自动化（Kaggle 式）、④进化式算法发现、⑤领域特定（含自驾/机器人/RL）。
- **跟你最相关的"复现"方向**：最值得先上手的是 **Paper2Code (PaperCoder)** 和 **AutoReproduce**，评测基准看 **PaperBench** 和 **ReproduceBench**。
- **自动驾驶/机器人领域的"专用 autoResearch"其实很稀缺**。绝大多数"LLM + 自动驾驶"的工作是把 LLM *放进驾驶系统里*（DriveGPT4、GPT-Driver、DiLu…），而不是*自动化研究过程本身*。真正做"自动化研究"的，目前更多是**领域无关**的工具 + 少量针对 RL 奖励设计 / 设计空间探索的专用工作。所以对你来说，**领域无关方案 + 自己接驾驶/机器人的评测环境**，可能是更现实的路线。
- **最 promising（综合活跃度、影响力、可复用性）**：AI Scientist v2、AlphaEvolve（及其开源复刻 OpenEvolve / ShinkaEvolve）、AI-Researcher、Paper2Code、AutoReproduce，以及 MLE-bench 生态里的 AIDE scaffold。

---

## 1. 端到端"AI 科学家"（idea → 实验 → 论文）

这类系统目标是把"提出假设 → 设计并跑实验 → 写论文"整条链路自动化。对"复现"来说不是最对口，但它们的**实验执行/调试模块**很有借鉴价值。

| 项目 | 来源 | 关键点 | 链接 |
|---|---|---|---|
| **The AI Scientist v1 / v2** | Sakana AI | v2 去掉了人工模板、跨 ML 领域泛化，用"渐进式 agentic 树搜索"+experiment manager agent；v2 生成的论文有一篇通过了 ICLR workshop 同行评审（首次全 AI 论文过审）。 | arXiv 2504.08066 ｜ `github.com/SakanaAI/AI-Scientist-v2` |
| **AI-Researcher** | 港大 (Chao Huang 组) | NeurIPS 2025 spotlight；从文献综述、假设生成到算法实现的全流程编排，基于其 AutoAgent 零代码框架。社区关注度高。 | arXiv 2505.18705 |
| **Agent Laboratory** | AMD (Schmidgall 等) | 多智能体（PhD / Postdoc / ML Engineer / Professor 角色）协作，三阶段：文献综述 → 实验 → 写作。代码开源、易改造。 | arXiv 2501.04227 |
| **AgentRxiv** | Schmidgall & Moor | 在 Agent Laboratory 之上做"协作式自治研究"——多个 agent 共享一个类 arXiv 的成果库，互相迭代。 | arXiv 2503.18102 |
| **Kosmos** | Edison Scientific / FutureHouse | 数据驱动的自治科学家，单次研究"campaign"可跑 ~12 小时，强调**可追溯、可复现的引用报告**；偏生物/材料/神经科学。 | arXiv 2511.02824 |
| **Google AI Co-Scientist** | Google | 偏"协作"而非"全自动"，多 agent 生成+辩论+排序假设；生物医学验证较多。 | arXiv 2502.18864 |
| **ML-Master** | 上交等 | "AI-for-AI"：把探索与推理整合，面向 ML 研究任务自动化。 | arXiv 2506.16499 |
| **Jr. AI Scientist** | — | 从一篇 baseline 论文出发做自治探索，并附带一份**风险报告**（值得一读，谈了这类系统的失控/造假风险）。 | arXiv 2511.04583 |

**点评**：想要"开箱即用 + 好改"的，从 **Agent Laboratory** 或 **AI Scientist v2** 入手最快。想看最前沿工程设计的，看 AI-Researcher。这一类的通病是——**能过 workshop 不等于能推进领域**，产出质量方差大、依赖底座模型。

---

## 2. 论文 / 算法复现（paper → code）★你的主战场

这是和"算法、模型复现"最直接对口的一类。

### 2.1 Paper2Code / PaperCoder ⭐推荐先试
- **是什么**：多智能体 LLM 框架，把一篇 ML 论文转成可运行的代码仓库。三阶段流水线：**planning（画架构图、定文件依赖、生成配置）→ analysis（抠实现细节）→ generation（按依赖关系生成模块化代码）**。
- **效果**：在 Paper2Code benchmark（90 篇 NeurIPS/ICML/ICLR 2024 论文）和 PaperBench 上都超过强基线；作者本人评估里 **77% 偏好它生成的实现、83% 认为实用**。
- **成本**：用 o3-mini 跑一篇约 **\$0.5–0.7**，也支持本地 DeepSeek-Coder。
- **链接**：arXiv 2504.17192 ｜ `github.com/going-doer/Paper2Code`
- **局限**：作者自己说目前**只针对 ML 论文**这个范围；细节（如卷积 stride/padding、超参）常和参考实现有出入。

### 2.2 AutoReproduce ⭐推荐关注
- **是什么**：端到端"实验复现"多智能体框架。最大亮点是 **paper lineage（论文谱系）算法**——通过追踪目标论文的**引用关系**，从被引文献里挖"论文没写明的隐式领域知识/实现惯例"。
- **工程细节**：在复现过程中**同时生成单元测试**（采样式 unit test）保证代码可执行；研究 agent + 代码 agent 分工。
- **配套基准**：**ReproduceBench**（13 篇跨领域论文，人工校验过参考实现），在 PaperBench + ReproduceBench 上都超基线。
- **链接**：arXiv 2505.20662
- **为什么对你重要**："隐式知识"和"细节对不上"正是复现自驾/机器人算法时最痛的地方，paper lineage 这个思路很值得借鉴。

### 2.3 配套评测基准
- **PaperBench**（OpenAI，arXiv 2504.01848）：评 AI 复现整篇 AI 论文的能力（基于 ICML 2024 论文，含逐项 rubric）。现在几乎是复现类工作的标配 benchmark。
- **Executable Knowledge Graphs**（arXiv 2510.17795）：把论文知识表示成"可执行知识图谱"来提升可复现性——偏新、偏研究，但思路有意思。

---

## 3. ML 工程 / 实验自动化 Agent（Kaggle 式）

不直接"复现论文"，但**自动跑完整 ML 流水线**（数据→训练→调参→提交）的能力和复现高度重叠，scaffold 可以直接借用。

| 项目 | 关键点 | 链接 |
|---|---|---|
| **MLE-bench** | OpenAI 出的基准：75 个 Kaggle 竞赛离线环境，agent 最多跑 24h，用奖牌率对标人类。**生态价值 > 基准本身**——它带火了下面几个 scaffold。 | arXiv 2410.07095 ｜ `github.com/openai/mle-bench` |
| **AIDE** | Weco AI 出的 scaffold，对 Kaggle 解法做**树搜索**。在 MLE-bench 上是**最强 scaffold**（同模型下显著超过通用 scaffold）。想自己搭复现/实验 agent，AIDE 是首选骨架。 | Weco AI |
| **OpenHands / MLAB** | 通用型 agent scaffold（靠调工具行动），可塞进 MLE-bench。 | 开源 |
| **MLGym** | Meta 出的 AI 研究 agent 框架 + 基准。 | arXiv 2502.14499 |
| **FM Agent** | 在完整 MLE-bench 上达到 ~96.9% 有效提交率，鲁棒性强。 | arXiv 2510.26144 |

**点评**：如果你的目标是"给定一个驾驶/感知任务，让 agent 自动迭代出一个能跑的模型"，**AIDE scaffold + 自己的任务环境**是性价比最高的起点。

---

## 4. 进化式算法发现（algorithm discovery）★对"算法"特别相关

不是复现，而是**发现/优化新算法**。如果你关注的"算法"包括"让系统自己改进算法"，这一类是核心。

| 项目 | 关键点 | 链接 |
|---|---|---|
| **AlphaEvolve** ⭐ | Google DeepMind，2025-05 发布。LLM（Gemini）+ 进化算法的**通用**编码 agent：给定评估函数 + 初始算法，反复让 LLM 产生变体并择优。已在矩阵乘法、数学构造等问题上拿到 SOTA。**通用性是它和 AlphaTensor/AlphaFold 的关键区别。** | arXiv 2506.13131 ｜ 结果开源 `github.com/google-deepmind/alphaevolve_results`（注意：**只放了结果，没放运行代码**） |
| **OpenEvolve** | AlphaEvolve 的**开源复刻**，把核心进化机制做成可用实现。想自己跑 AlphaEvolve 风格的，从这个入手。 | 开源 (Sharma, 2025) |
| **ShinkaEvolve** | Sakana 出的**样本高效**版本：bandit 式 LLM 集成 + 基于新颖性的拒绝采样，减少无效尝试。 | Lange et al. 2025 |
| **CodeEvolve** | 又一个开源进化编码 agent，强调通用性和可复现/透明。 | arXiv 2510.14150 |
| **AlphaResearch** | 针对 AlphaEvolve"暴力采样成本高"的问题，做更高效的新算法发现。 | arXiv 2511.08522 |
| **FunSearch** | DeepMind 的前身工作（LLM + evaluator 发现数学启发式）。 | (Romera-Paredes et al.) |

---

## 5. 自动驾驶 / 机器人 / RL 相关 ★你的领域

**重要提醒**：这里要区分两件事——
- ❌ **"LLM 用于自动驾驶"**（DriveGPT4、GPT-Driver、DiLu、LMDrive、LLM4AD…）：这些是把 LLM/VLM *放进驾驶决策栈*，**不是 autoResearch**。数量很多，但不是你要找的。
- ✅ **"自动化研究过程"在驾驶/机器人/RL 领域的应用**：相对稀缺，目前主要是下面这些。

| 项目 | 做什么 | 链接 |
|---|---|---|
| **Multi-Agent LLM DSE for Autonomous Driving** | 多智能体 LLM 做**自驾系统的设计空间探索（DSE）**：自动生成设计点、跑 3D 仿真、读图+读文本分析瓶颈。robotaxi（L4）案例上，同等预算下比遗传算法找到更多 Pareto 最优、成本更低的方案。**这是最接近"自驾领域 autoResearch"的工作。** | arXiv 2512.08476 |
| **Eureka** | NVIDIA。用 LLM**自动写/优化 RL 奖励函数**，在多项任务上超过人工设计的奖励。机器人/RL 研究自动化的代表作。 | NVIDIA |
| **ARCHIE** | 用 GPT-4 从自然语言任务描述**自动生成奖励函数 + 成功判据**，一次性把人类描述变成可部署的机器人技能（双臂/单臂操作，真机验证）。 | arXiv 2503.04280 |
| **POISE / "From AI Assistant to AI Scientist"** | 复旦。**自动发现 LLM-RL 算法**：从 GRPO 出发评估 64 个候选算法，发现了 analytic-variance scaling、validity masking 等改进（AIME25 pass@32 从 26.7%→43.3%）。对"自动改进 RL 算法"很有参考价值。 | arXiv 2603.23951 |
| **AutoResearch-RL** | 把"LLM 预训练研究"形式化成 RL 问题做**神经架构自动发现**，带自评估提前终止无望实验。 | arXiv 2603.07300 |
| **AutoSOTA** | 端到端**自动发现 SOTA AI 模型**的研究系统。 | arXiv 2604.05550 |
| **ATLAS** | Active Theory Learning：主动学习框架，迭代"生成机制假设（Disentangled RNN）↔ 设计最优区分实验"，在**恢复 RL agent 的行为模型**上样本效率显著提升。 | (见下方资源列表) |

**给你的建议**：自驾/机器人领域目前**没有成熟的"专用 autoResearch 平台"可以直接拿来复现算法**。更现实的两条路：
1. **复现方向**：用领域无关的 Paper2Code / AutoReproduce + 你自己的仿真/数据环境，把驾驶/感知论文喂进去。
2. **算法发现方向**：用 AlphaEvolve/OpenEvolve（接你的评估函数）或 Eureka 风格（自动设计奖励）来做规划/控制/RL 的算法迭代。

---

## 6. 横向对比 & 推荐

### 按"你最可能想做的事"推荐

| 你的目标 | 首选 | 备选 |
|---|---|---|
| 复现一篇算法/模型论文 → 出可跑代码 | **Paper2Code** | AutoReproduce（尤其在意"隐式细节"时） |
| 评估复现质量 / 立 benchmark | **PaperBench** | ReproduceBench |
| 自动迭代出一个能跑的模型（给定任务） | **AIDE scaffold**（+ MLE-bench 环境） | OpenHands、FM Agent |
| 让系统自己发现/改进算法 | **AlphaEvolve → OpenEvolve** | ShinkaEvolve、AlphaResearch |
| 自动设计 RL 奖励 / 机器人技能 | **Eureka** | ARCHIE |
| 自驾系统设计空间探索 | **Multi-Agent LLM DSE (2512.08476)** | — |
| 端到端"AI 科学家"全流程 | **AI Scientist v2** | Agent Laboratory、AI-Researcher |

### "最 promising" 主观排序（活跃度 + 影响力 + 可复用）

1. **AlphaEvolve / OpenEvolve** —— 算法发现范式，通用性强，社区复刻多。
2. **AI Scientist v2** —— 端到端标杆，开源活跃，工程参考价值大。
3. **Paper2Code** —— 复现方向最成熟、可直接用、成本低。
4. **AI-Researcher** —— 学术影响力大（NeurIPS spotlight）、框架完整。
5. **AutoReproduce** —— "paper lineage + 单元测试"的工程思路对真实复现很有用。
6. **AIDE + MLE-bench 生态** —— 想自建实验 agent 的最佳起点。

---

## 7. 持续追踪资源

- **GitHub: `tmgthb/Autonomous-Agents`** —— 每日更新的自治 agent 论文列表（含 ATLAS 等最新工作），追前沿最省事。
- **Turing Post: "12 AI Co-Scientists of 2026"** —— 2026 年 AI 协作科学家盘点（含 6 个开源项目），适合快速扫一遍全景。
- **AI4Research Survey**（Chen et al., 2025）—— "AI for Scientific Research" 综述。
- **SCP / Scientific Context Protocol**（`github.com/open-sciencelab/scp`）—— 想做"多 agent 科学发现的基础设施/协议层"可参考。
- **aiXiv**（arXiv 2508.15126）—— 面向 AI 科学家产出的"下一代开放获取生态"，关注成果发布/评审基础设施。

---

## 8. 几点提醒（避坑）

- **质量方差大**：端到端系统能产出论文 ≠ 产出有价值的研究；复现工具能生成代码 ≠ 数值能对齐。务必配评测基准。
- **隐式知识是复现的核心难点**：论文常省略关键训练细节（超参、数据处理、随机种子）。AutoReproduce 的 paper lineage、以及"拿原作者 repo 当 ground truth"是目前主要应对手段。
- **成本与底座强相关**：这些系统效果高度依赖底座模型（o3/GPT-5/Gemini/Claude 等）和 scaffold，换模型结论可能翻盘。
- **安全/伦理**：Jr. AI Scientist 的风险报告值得一读，尤其当你打算让 agent 自动写并执行任意代码时。
