<!-- Talos provenance -->

> 出处归档 (provenance) · 原始深度调研报告,保留原文。综述见仓库 docs/concepts 与 docs/survey。

---

# AutoResearch 面向应用算法团队：Claude Code & Codex Skills 的设计哲学蓝图

> 中文 review 版。技术术语、工具/项目名、文件名（如 `program.md`、`val_bpb`）与 arXiv 引用保留原文。

## TL;DR（核心结论）

- **要偷的是"循环"，不是框架。** 在所有调研过的系统里——从 Karpathy 的 autoresearch 到 AlphaEvolve、Curie、MLE-STAR 以及各类 AI Scientist——最可迁移的一个思想是一套有纪律的循环：**提出改动 → 有界预算下做实验 → 得到一个硬性标量分数 → 保留或回滚（keep-or-revert）**，其中用 git 作为回滚原语，配一个被冻结、难以被钻空子的评测器。对你们团队来说，这落地为一小组 Claude Code / Codex skills + 每个方向一份 `program.md` 式的 spec + 一套冻结的 eval harness——**而不是再造一个平台**。
- **真正的瓶颈是评测（eval），不是 agent。** 每个项目的天花板都由它的指标决定：当实验跑得比人快约 100 倍时，**一个快速、确定性、标量、难以被 game 的 eval（带硬约束否决项）就成了自治的前提**。对自动驾驶和机器人而言，这意味着要按各子团队的方向，**先把闭环仿真/打分搭好**（CARLA、nuPlan、Waymax、MetaDrive、Isaac Lab 等），再放 agent 去跑。
- **机制要和任务匹配。** 在已有代码库上做局部精修，用贪心的单谱系棘轮（ratchet）；需要跳出局部最优时，用树搜索 / 进化种群（AIDE、AI Scientist v2、ShinkaEvolve、AlphaEvolve）；需要知道"为什么有效"时，用消融归因（MLE-STAR）和多 agent 严谨性（Curie）；要挖论文没写明的隐式知识时，借鉴 paper-lineage 复现思路（AutoReproduce、Paper2Code）——但要改造，因为它们是**生成全新 repo**，而你们必须**嫁接进一个已有的大代码库**。

## 主要发现（Key Findings）

### 1. AutoResearch 范式（Karpathy，2026 年 3 月）

Karpathy 的 `autoresearch`（2026 年 3 月发布；README 口号大致是"一块 GPU、一个文件、一个指标"）是一套约 630 行的配置，核心是一个**三文件架构**，它编码了一份"所有权契约"：

- **`prepare.py` —— 不可变（IMMUTABLE）。** 数据准备、tokenizer、dataloader，以及评测函数（`evaluate_bpb`）外加固定时间预算常量。**人和 agent 都不许改**。这是完整性保证：如果 agent 能碰评测器，它就会"把考试改简单，而不是把模型做好"。
- **`train.py` —— agent 的沙盒。** agent 唯一可以改的文件：完整的 GPT 模型、Muon+AdamW 优化器、训练循环。"一切皆可改"——架构、优化器、超参、batch size。
- **`program.md` —— 人类所有。** 承载指令、约束、停止条件、那套 9 步循环，以及"简洁性准则"。它引导假设的方向（Karpathy 把探索分阶段：显然的超参调整 → 小的架构改动 → 登月式 moonshot）。

**棘轮循环（ratchet loop）：** 在一个专用 git 分支上，agent 会 (1) 读 `program.md`、`train.py`、`results.tsv`；(2) 带着明确推理提出一个改动；(3) 改 `train.py`；(4) commit；(5) 训练**恰好 5 分钟 wall-clock**（`uv run train.py > run.log`，用重定向——绝不用 `tee`——以保护上下文）；(6) grep 出 `val_bpb`/`peak_vram_mb`；若为空说明 run 崩了 → 读最后 50 行日志、尝试修复、几次后放弃；(7) 若 `val_bpb` 改善（更低）则该 commit 保留并成为新基线，否则 `git reset` 立即回滚。约 12 实验/小时，一晚约 100 个。

**为什么每个选择都重要（可迁移的推理）：**
- **`val_bpb`（验证集 bits per byte）** 之所以被选中，是因为它是单一标量、越低越好、且**与词表大小无关**——所以改了架构/tokenizer 的版本之间能被公平比较。通用教训：**挑一个在你预期 agent 会做的结构性改动下仍然可比的指标**。
- **固定 wall-clock 预算** 让"训得更快"的改动和"收敛更低"的改动在同一基准上直接可比，并限制了爆炸半径（没有哪个 run 能吃光你的 GPU）；用短跑也抑制了对噪声的过拟合。
- **git 作为回滚原语**：代码库只能向前（"棘轮"）；每个保留下来的 commit 都是一次被验证过的改进；git log **就是**审计轨迹，也是 agent 的记忆（重启时它读 log 看之前试过什么）。`results.tsv` 被刻意设为不纳入 git 跟踪。
- **这不是超参搜索。** AutoML/Optuna/Ray Tune 在预定义参数空间里搜、有收敛保证；autoresearch 让 LLM 改任意代码——在**代码空间**里做开放式搜索，押注模型的文献知识，**没有任何理论保证**。
- **跑在已有的编码 agent 之上**：没有编排脚本——"直接在这个 repo 里把你的 Claude/Codex 开起来"，让它去读 `program.md`。

**已报告的结果：** 在 nanochat 排行榜上，主指标是"time to GPT-2"（在 8×H100 节点上达到 GPT-2 1.6B 的 CORE 分 0.256525 所需的 wall-clock 时间）。基线是 2.02 小时；"autoresearch round 1"把它降到 1.80 小时（约 11%），之后的"round 2"达到 1.65 小时。Karpathy 的两天延长 run 产出了约 700 个实验、约 20 项可叠加的改进（一个 QK-Norm 标量乘子修复、value-embedding 正则、带状注意力加宽、AdamW beta 修正、weight-decay 调度），并能从 depth-12 模型迁移到 depth-24 模型。他提醒"这些东西很脆弱"——有些增益没能复现，存在过拟合风险。社区有一个 run 报告 `val_bpb` 在 126 个实验里从 0.9979 → 0.9697（社区报告，非 Karpathy 本人）。

**值得注意的衍生案例 —— Shopify：** Shopify CEO Tobi Lütke 把一套 autoresearch 式循环（通过"Pi"编码 agent 和一个由 Shopify 工程师 David Cortés 共建的 `pi-autoresearch` 插件）应用到 Liquid 模板引擎上。可验证的产物是 Shopify/liquid PR #2056，"parse+render 快 53%、分配少 61%"（7,469 µs → 3,534 µs；62,620 → 24,530 次分配），来自约 120 个自动实验中的 93 个 commit，全部 974 个单元测试通过。Lütke 本人写道这"大概有些过拟合，但里面确实有非常棒的想法"，而该 PR 数月未被合并、外部对代码质量有一些批评。另外关于内部"#autoresearch-wins"频道报告 Polaris 流水线"单测快 300×""构建快 65%"的说法属于自报、未经审计，应谨慎看待。

**作者/社区报告的局限：**
- **贪心局部搜索。** 棘轮只向前；它永远不能"先变差再变好"，所以会错过那种需要两步之后才显现更大增益的改动（GitHub Issue #22）。它维持的是**单一谱系**而非种群——LLM 同时充当变异算子和选择压力。
- **RLHF 保守性。** Karpathy 指出 agent 在开放性问题上显得"谨小慎微、畏手畏脚"，归因于 RLHF 奖励安全保守的输出而非大胆实验。
- **Goodhart / 指标作弊与过拟合。** 对着同一个验证集跑 100+ 实验，会带来只针对该 eval 的"改进"；评测器的不可变性既是公平性保证，也是盲区。
- **固定短窗口会掩盖慢热型增益**；eval 成为瓶颈。
- 已有人提出一个 meta-autoresearch "bilevel"（双层）变体：外层循环改写 `program.md`/机制本身，报告称其优于只调参——说明那份**人类所有的 spec 本身就是一个可优化的对象**。

**awesome-autoresearch** 系列清单（WecoAI、yibie、alvinunreal、AI4Scientist）记录了数十个 fork：GPU kernel 优化（AutoKernel）、RAG 检索、KITTI 上的 LiDAR SLAM（autoslam）、MuJoCo/Gymnasium 机器人（autoresearch-robotics，用仿真渲染 + 视觉反馈）、RL 后训练（autoresearch-rl）、CIFAR/MNIST/医学影像视觉 fork，以及 Claude/Codex 的 skill 封装（uditgoenka/autoresearch、leo-lilinxiao/codex-autoresearch），这些把 keep/revert 循环一般化，并加了默认有界迭代次数、git 作记忆、安全 hook。

### 2. 严谨实验框架（Rigorous experimentation）

- **Curie（Just-Curieous）。** 一个 **Architect Agent** 负责设计高层实验计划（假设、变量）并对发现做反思；多个 **Technician Agent** 负责实现并执行受控实验；二者之间是 **Experimental Rigor Engine（实验严谨性引擎）**，含三个模块：**Intra-Agent Rigor（智能体内严谨性）**（校验器检查设置是否符合计划、参数是否正确，并**多次重跑实验以保证可复现**）、**Inter-Agent Rigor（智能体间严谨性）**（方法论上的控制——细粒度计划切分、控制流强制、资源约束下的分区调度，以及**分级写权限**，使 technician 只能向自己的分区追加结果）、以及一个用于可解释文档的 **Experiment Knowledge Module（实验知识模块）**。Curie 的标志性工作流是 **Reproduce → Extend → Challenge（复现 → 扩展 → 挑战）**，并报告在一个 46 题的基准上比最强基线（OpenHands 和 Microsoft Magentic）有 3.4× 提升——据 Kon 等人 "Curie"（arXiv:2502.16069）："我们在正确回答实验问题上取得了 3.4 倍的提升"。该团队还构建了 **EXP-Bench**（"AI 能否开展 AI 研究实验"）。**值得偷的点**：*严谨性是一等组件，不是事后补丁；把校验器和分级写权限编码进去，让 agent 无法悄悄污染实验记录。*
- **MLE-STAR（Google）。** 两个思想。其一，**搜索接地的初始化**：一个检索 agent 用网络搜索拉取任务专属的 SOTA 模型和代码，而不是只靠 LLM 先验。其二，**消融引导的定向精修**：一个嵌套循环，外层用**消融研究**找出对性能影响最大的那个代码块，内层再深度探索**那个块**的各种变体（而不是粗暴重写整条流水线）。外加一个新颖的集成 agent 和若干鲁棒性模块（调试、**数据泄漏检查器**、数据用法检查器）。用 Gemini-2.5-Pro 在 MLE-bench-Lite 上拿牌率 64%（36% 金牌），从此前最佳的 25.8% 提升而来——据 Google Research 的 MLE-STAR（arXiv:2506.15692）。**值得偷的点**：*先归因再优化——用消融找到高杠杆的组件，然后在那里深挖；显式检查数据泄漏。*
- **AIDE（Weco AI）。** 把 ML 工程建模为**代码空间里的树搜索**：每个节点是一份完整的解法脚本；LLM 生成的补丁派生出子节点；一个由 eval 指标引导的最佳优先搜索会复用有希望的节点、剪掉失败的，并且它会**总结**相关历史而非全量追加（上下文纪律）。它是 MLE-bench 上最强的 scaffold，在 METR 的 RE-Bench 上也有竞争力。**值得偷的点**：*维护一棵可搜索的解法状态树、每个节点带指标标签，这样你能从最好的节点而非最近的节点分叉。*

### 3. ML 工程 agent 及其 scaffold

- **MLE-bench（OpenAI）** 在 Docker 容器里用 75 个 Kaggle 竞赛评测 agent（例如 36 CPU、440GB RAM、单块 A10、最长 24h）。关键的 scaffold 结论：**scaffold 和模型一样重要。** AIDE 的专用搜索打败了通用的 OpenHands 和 MLAB scaffold（GPT-4o：拿牌率 8.7% vs 4.4% vs 0.8%）。失败模式很有启发：MLAB 因为去读上千行的文件把上下文塞满；MLAB/OpenHands 经常在有 24h 预算的情况下**过早停止**；**三者都不会对算力/时间限制做推理**，有时因把磁盘/内存压垮而搞崩机器。o1-preview+AIDE 达到 16.9% pass@1，在 pass@8 时翻倍到约 34%。**值得偷的点**：*预算意识、上下文卫生（绝不整文件读巨型文件）、以及明确的"把预算用完前别停"的指令，必须烤进你的 skills 里。*
- **相关系统**（MLGym/Meta、MLAgentBench、FM Agent、ML-Master、AutoSOTA）强化了同样的模式——树搜索、调试循环、长程执行、资源管理——构成 ML 工程 agent 反复出现的设计词汇。

### 4. 论文/算法复现 agent

- **Paper2Code / PaperCoder** 模仿软件工程，用 **plan → analyze → code** 的多 agent 流水线：planning 构建路线图、架构、文件依赖与配置；analysis 产出文件级 spec；generation 输出模块化、依赖感知的代码。其无参考的质量逼近作者发布的 repo。**值得偷的点**：*自顶向下分解 paper-to-code（先 plan/架构）而不是一次性生成。*
- **AutoReproduce** 引入 **paper-lineage（论文谱系）算法**：通过顺着引用关系（默认 k=3 个最相关参考文献及其 repo）来挖**隐式、未写明的知识**，因为复现常常依赖论文从未陈述的惯例。它用**采样/批量式单元测试**保持代码可执行，并发布了 **ReproduceBench**。**值得偷的点**：*要复现一个想法，就自动把它引用的"祖先"代码和惯例拉进来；边做边用生成的单元测试验证可执行性。*
- **PaperBench（OpenAI）** 用**作者共同制定的分层 rubric** 给 20 篇 ICML 2024 论文的复现打分（8,316 个叶子标准，每个 pass/fail，沿树加权汇总成 0–100% 的复现分），由一个在 JudgeEval 上被验证过的 LLM 评判器来判。提交依赖一个在全新 GPU 容器里运行的 `reproduce.sh`；硬编码输出会被抓出来。被测表现最好的 agent 是 Claude 3.5 Sonnet (New) 配开源 scaffold，得分 21.0%，而招募的 ML 博士平均 41.4%——据 OpenAI "PaperBench"（arXiv:2504.01848）。**值得偷的点**：*一个加权的分层 pass/fail rubric，把模糊的"它跑通了没"变成可自动化的标量——而全新容器里重跑能防止结果造假。*
- **对你们团队的关键警示：** 这些系统大多**生成全新仓库**。你们的任务正相反——把一个想法嫁接进一个已有的大代码库——所以可复用的是其中的*plan/analyze 分解*和*可执行性验证*，而不是从零生成。

### 5. 仓库级 / 代码库感知的编码 agent（你们真正的底座）

- **SWE-agent / SWE-bench（Princeton）。** 核心思想是 **Agent-Computer Interface（ACI，智能体-计算机接口）**：LLM agent 是一类新的"终端用户"，它们受益于**为它们设计的**接口——一小组带护栏的动作（定位、带窗口的文件查看、带 lint 的编辑、测试），而不是裸 shell。这个 ACI 洞见（经消融验证：比裸 Linux shell 高 10.7 分）传播到了之后大多数 agent。**值得偷的点**：*给你的 agent 一套精选、带 lint 校验、带窗口的工具面，以及明确的子任务（定位 → 编辑 → 测试），而不是裸 bash。*
- **Claude Code & Codex。** 几个你应该直接利用的内建模式：**git-worktree 隔离**（`claude -w`/`--worktree`）让每个任务有自己的分支、文件状态和上下文，使并行 agent 不互相干扰、一个跑歪的会话可以直接丢弃；**plan mode**（先读、先提案，再编辑）；**subagent**（把代码库探索委派出去，只把结论带回主上下文——大 repo 的上下文卫生）；**skills**（`SKILL.md` + 脚本，可移植到 Codex 的 `~/.codex/skills`）。一个现实警示（Trigger.dev）：在有很多共享服务的大型 monorepo 里，worktree 的搭建成本（重复的 node_modules、各自的 DB/Redis/ClickHouse 实例）可能超过它省下的收益——所以隔离策略要因 repo 而异。
- **Aider** 是 The AI Scientist v1 用来运行和编辑代码、并维护实验日志的执行器——证明一个轻量、git 感知的"编辑/运行"循环已经够当底座。
- **组织专属惯例。** 把你们的库、约定和约束编码进一个 `CLAUDE.md`/skill，让 agent 用对内部 API——这等价于 `program.md` 承载约束。自我改进的"skill 进化"循环（EvoSkill、autoimprove-cc）把 autoresearch 的 keep/revert 循环应用到 `SKILL.md` 文件本身，对着一个 eval 集打分。

### 6. 端到端"AI Scientist"系统（取其可迁移模式，而非直接采用）

- **Sakana AI Scientist v1/v2。** v1 生成并变异一棵想法树、用 Semantic Scholar 查新颖性、用 **Aider** 执行代码并维护实验日志，还含一个自动评审器（<$15/篇）。v2 去掉了人工模板，改用**渐进式 agentic 最佳优先树搜索**，由一个专门的 **experiment-manager agent** 治理，配并行 worker、调试深度上限、对图的 VLM 反馈，并用一次性写作取代 Aider 的增量编辑。注意：当有强模板时，v2 的成功率**低于** v1——探索更多、可靠性更低。
- **AI-Researcher（HKUDS）。** 一个 **Design → Implementation → Validation → Refinement（设计 → 实现 → 验证 → 精修）** 闭环，配一个**知识获取**范式（被动自底向上注入 + 主动自顶向下获取）、一个会推荐补充研究的 Advisor agent，以及基于指标或基于 agent 的假设验证。**值得偷的点**：*把 Validation 和 Refinement 作为命名的循环阶段显式列出，并让一个 advisor 来提议下一个消融。*
- **Google AI co-scientist。** 一个 Supervisor 编排 Generation、Reflection、Ranking、Evolution、Proximity、Meta-review 等 agent，构成"生成、辩论、进化"的循环；**Ranking agent 跑一个 Elo 锦标赛**做成对的科学辩论（假设从 Elo 1200 起步），质量随测试时算力上升。**值得偷的点**：*当没有单一指标时，锦标赛/Elo 排名是把"哪个想法更好"标量化的一种办法。*
- **Agent Laboratory & AgentRxiv。** 一条"文献 → 实验 → 写作"的顺序流水线，外加一个**共享预印本服务器**，让各 agent lab 检索并在彼此的报告上继续构建——据 Schmidgall 等人（Johns Hopkins/ETH Zurich）"AgentRxiv"（arXiv:2503.18102），当各 lab 共享时在 MATH-500 上有 13.7% 的相对提升（用发现的 SDA 技术从 70.2%→78.2%）。**值得偷的点**：*一个共享、可搜索的"既往 agent 发现"存储会让结果复利——也就是把你们的 `results.tsv`/实验日志放大成团队知识库。*
- **Kosmos。** 用一个**结构化世界模型**（一个记录实体、关系、结果、未解问题的数据库，每个任务后更新）在数据分析 agent 和文献 agent 之间共享，单次运行最长 12 小时、可在约 200 个 rollout（每次运行约 166 个数据分析 rollout 产出约 42,000 行代码、36 个文献综述 rollout 覆盖约 1,500 篇论文）里保持连贯；经审计的陈述总体 79.4% 被评为准确（数据分析陈述 85.5%、文献综述陈述 82.1%）——据 Edison Scientific 的 Kosmos 论文（arXiv:2511.02824）。**值得偷的点**：*对长程连贯性而言，一个结构化、持久的世界模型胜过裸上下文窗口。*
- **Jr. AI Scientist** 模仿一个新手研究者（分析 baseline → 提假设 → 用现代多文件编码 agent 迭代 → 写论文），并**明确警告不要用它做真正的投稿**，列举了一串风险：编造辅助结果、错误引用、方法过拟合、科学肤浅、以及"review hacking（评审作弊）"。**值得偷的点**：*那份风险清单就是你们的反模式 checklist——要防住编造结果与指标/评审作弊。*

### 7. 算法发现 / 进化搜索系统

- **FunSearch（DeepMind, 2023）** 把 LLM 与一个评测器配对，进化出小（10–20 行）的 Python 函数来解数学问题——概念验证，但局限于函数模板、需要数百万次评估。
- **AlphaEvolve（DeepMind, 2025 年 5 月）** 把这件事一般化为**进化整个代码库**、支持任意语言。用户提供两样东西：**一个初始程序 + 一个返回标量指标的评测函数**。一个 Gemini 模型集成充当变异算子（由 LLM 决定改哪里、怎么改）；一个**程序数据库**用 MAP-Elites + island 模型来平衡探索/利用；整条流水线是异步的，以在算力预算内最大化"想法产出"。它支持**多目标优化**、只需数千次评估，并产出了真实成果——例如首个用 48 次标量乘法相乘两个 4×4 复数矩阵的算法（优于 Strassen 的 49 次，这是 1969 年以来保持的纪录）——据 Google DeepMind AlphaEvolve（2025 年 5 月）。一句话的要害：*评测函数就是全部的胜负手。*
- **OpenEvolve / CodeEvolve** 是开源复刻；CodeEvolve 报告在若干数学基准上超过 AlphaEvolve。
- **ShinkaEvolve（Sakana, 2025 年 9 月）** 主攻**样本效率**，用三个机制：(1) **自适应父代采样**，从 island 子种群里采样以平衡探索/利用（用幂律 / 适应度与新颖性加权，而非总是爬当前最优）；(2) **基于新颖性的拒绝采样**——对候选编辑做 embedding，若余弦相似度超过阈值就拒绝，并配一个 LLM-as-novelty-judge——以免把评估浪费在近重复上；(3) **基于 bandit 的 LLM 集成选择**（UCB1 式），把变异路由给当前增益最大的那个模型族。它在 26 圆装填问题上仅用 150 个样本就达到新 SOTA——"相比以往工作是效率上的巨大飞跃"——据 Sakana AI ShinkaEvolve（arXiv:2509.19349），且为 Apache-2.0。**值得偷的点**：*新颖性过滤和 bandit 选模能大幅削减被浪费的实验——当你们每个实验都很贵时尤其相关。*
- **Eureka / DrEureka（NVIDIA）** 用 LLM**编写奖励函数代码**给 RL，然后对**奖励代码做进化优化**，并配**奖励反思（reward reflection）**（LLM 读取 RL 训练统计量、再修订奖励）。据 Ma 等人 "Eureka"（arXiv:2310.12931）："EUREKA 在 83% 的任务上超过人类专家，平均归一化提升 52%"，覆盖 29 个环境、10 种机器人形态；DrEureka 进一步扩展到自动化 sim-to-real 域随机化。对机器人的关键设计张力：Eureka 外层循环的每一次迭代都需要一整次 RL 训练作为内层循环——反馈很贵。**值得偷的点（与你们机器人工作直接相关）**：*LLM 能编写并迭代精修奖励/eval 函数，但其速度受限于你内层训练+eval 的速度。*

### 8. 把评测基础设施当作一等公民

贯穿全部八类的反复教训：**一个快速、可标量化、难以被 game 的确定性指标，是任何自治循环的前提。** 要编码进去的原则：

- **eval 会成为瓶颈。** 当 agent 跑实验比人快约 100 倍时，决定进展的是评测器的吞吐与可信度——而不是想法生成。**先把 eval 搭好。**
- **Goodhart 定律 / 抗作弊设计。** 单一标量会招来作弊（autoresearch 的过拟合；Jr. AI Scientist 的"review hacking"；PaperBench 的硬编码输出检测）。实战中见到的防御：把评测器对 agent 冻结/封死（autoresearch 不可变的 `prepare.py`）；用**硬约束 / 否决项**（nuPlan 在发生本方有责碰撞或越出可行驶区域时，无视舒适度直接把该场景得分清零）；谨慎使用**多目标 → 标量化**（AlphaEvolve），警惕某一项主导导致的多目标坍缩。
- **限定范围、固定预算。** 固定 wall-clock 预算（autoresearch 的 5 分钟）让实验可比并限制爆炸半径；有界的默认迭代次数（Claude-autoresearch skills）防止循环失控；MLE-bench 表明不顾算力限制的 agent 会搞崩机器。
- **可复现 / 确定性 / 种子。** Curie 会多次重跑实验以求可复现；MLE-bench 用多种子运行来应对非确定性。要做出可信的 keep/revert 决策，种子管理和确定性 harness 是必须的。
- **静态基准会饱和。** 基准会饱和、会被污染；AgentRxiv 式的演进集和 held-out / walk-forward 评测能让指标保持诚实。
- **面向 AD/机器人的示例性指引（不是规定清单——每个子团队要建自己的）。** 文献强烈区分**开环（open-loop）**评测（把预测轨迹/标签和记录的真值比——便宜但对误差累积视而不见）与**闭环（closed-loop）**评测（策略真的去开、世界会反应——对真实性能预测力强得多）。仅作提示用的示例环境：**CARLA** 和 **MetaDrive**（基于传感器、反应式交通、带渲染）、**nuPlan** 和 **Waymax**（以规划为中心、基于真实日志、bounding-box 层级）、**nuScenes**（开环感知）、**NAVSIM**（基于传感器但非反应式）、**Bench2Drive**（CARLA v2、多能力）、**Isaac Sim/Lab**（机器人学习，Eureka 现在就在上面跑）。值得偷的反复出现的 eval 设计主题：反应式 vs 规则式（IDM）背景 agent；场景生成与覆盖度；把硬约束否决项折叠进一个 0–1 的标量；以及视觉/传感器域差。**把这些当作提醒：你们应该为每个方向先立起合适的闭环打分器，再去自动化——这份报告无法预知每个子团队的指标。**

## 细节：你们工作流循环的蓝图（A Blueprint for Your Workflow Loop）

你们陈述的循环——**发现并提炼一个想法 → 复现/确认它有效 → 把它嫁接进我们已有的框架 → 验证效果**——干净地映射到调研出的设计母题上。建议的 skill/runbook 拆解：

**阶段 A —— 发现并提炼（skill：`distill-paper`）。** 借鉴 Paper2Code 的自顶向下分解和 AutoReproduce 的 paper-lineage 思想：一个 subagent 读这篇论文**及其关键引用文献/repo**，把显式方法和*隐式惯例*都抽出来，产出一份结构化 spec（即 `program.md` 的对应物）：核心机制、声称的指标、最小复现、约束。用 Claude Code 的 subagent，让繁重的阅读留在主上下文之外。

**阶段 B —— 复现/确认（skill：`repro-harness`）。** **先**立起一个冻结的 eval harness（不可变 `prepare.py` 的教训）。用 AutoReproduce 的采样式单测和 PaperBench 的"全新容器里跑 `reproduce.sh`"思路来确认可执行性、防住编造/硬编码结果。用一个分层 pass/fail rubric（PaperBench）来 gate，让"复现成功与否"成为一个标量。

**阶段 C —— 嫁接进已有代码库（skill：`graft-change`）。** 这正是从零生成器帮不上忙的地方。用 SWE-agent 的 ACI 纪律（带窗口读、带 lint 编辑、定位→编辑→测试）、每个实验一个 git-worktree 隔离、以及一个组织惯例 `CLAUDE.md`，让 agent 用你们的内部库和约定。对任何触及安全关键路径的改动，用 plan mode + 人审 checkpoint。

**阶段 D —— 验证效果（skill：`ratchet-experiment`）。** 把改动裹进 autoresearch 棘轮：每次试验固定算力/仿真预算、标量闭环指标带硬约束否决项、改进则 `git commit` / 退化则 `git reset`、追加到实验日志。加上 MLE-STAR 式的**消融**把增益归因到具体组件，以及 Curie 式的**可复现重跑**后再接受。当局部搜索停滞时，升级到 AIDE/ShinkaEvolve 式的树/种群搜索 + 新颖性过滤。

**贯穿性编排。** 维护一个共享、可搜索的实验存储（AgentRxiv/Kosmos 的世界模型教训），让结果在各子团队间复利。当你必须在多个模型间选择、或在没有单一干净指标时给想法排序时，用 bandit/Elo 思路（ShinkaEvolve、AI co-scientist）。

## 建议（Recommendations）

**Phase 0 —— 先建评测器（按方向，数周）。** 为每个子团队方向立起一个快速、确定性、可脚本化的闭环打分器，返回单一标量 + 硬约束否决项，配固定时间/算力预算和种子控制。**在它存在之前，不要启动 agentic 循环。** *推进门槛：* 同样的输入可靠地得到同样的分数；一个已知好的改动和一个已知坏的改动被正确排序；单次试验在你的目标预算内跑完。

**Phase 1 —— 把棘轮固化成一个 skill（1–2 周）。** 为 Claude Code 和 Codex 实现 `ratchet-experiment`：读 spec → 提出一个聚焦的改动 → commit → 跑固定预算 eval → keep/revert → 记录。包含有界默认迭代、上下文卫生规则（重定向日志、绝不整读巨型文件、grep 出指标）、崩溃恢复、以及一个预算意识指令。先在一个*非安全关键*的离线指标任务上开跑以建立信任。

**Phase 2 —— 加上 distill/repro/graft 三个 skill（2–4 周）。** 叠上 `distill-paper`、`repro-harness`、`graft-change`。要求在任何嫁接之前先有一次绿色的复现（rubric 通过），并对安全关键的 diff 做人审。把组织惯例编码进 `CLAUDE.md`。

**Phase 3 —— 升级与归因（持续）。** 给每次被接受的胜果加上消融归因（MLE-STAR）、可复现重跑（Curie），并对贪心棘轮会停滞的问题加上带新颖性过滤的树/种群搜索（AIDE/ShinkaEvolve）。立起一个共享实验存储。

**会改变计划的阈值：**
- 如果胜果在一个 held-out 场景集上反复**无法复现** → 你的 eval 过拟合了；在继续之前轮换/扩充 eval 集（演进基准的教训）。
- 如果 agent **很快停滞** → 你陷入了局部搜索陷阱；从棘轮切换到树/进化搜索。
- 如果实验是 **eval-bound**（agent 在等仿真而空闲）→ 跨 worktree/GPU 并行试验，并加新颖性过滤来削减被浪费的 run。
- 如果某个单一目标项**主导**（多目标坍缩）→ 重新加权，或把它转成一个硬约束否决项。

## 注意事项（Caveats）

- **成熟度差异很大。** Karpathy 的 autoresearch 只有几周大（2026 年 3 月），且明确是一个极简、"脆弱"的演示器；AlphaEvolve 是闭源的（只有白皮书细节）；Curie、AIDE、ShinkaEvolve、Paper2Code、AutoReproduce、AI-Researcher 是研究级开源、传播度一般；Claude Code/Codex/SWE-agent 是生产级底座。把各 AI-Scientist 系统当作*模式来源*，而不是要采用的产品。
- **报告的数字需要审视。** 若干头条数字是自报或社区报告（Shopify 的"#autoresearch-wins"倍数；那个 126 实验的 `val_bpb` run），而非独立审计；解说博客有时把 Karpathy 本人的结果和社区结果混在一起。可验证的 Shopify 产物是 PR #2056（53% / 61%），CEO 本人也标注其"大概有些过拟合"。另外 autoresearch 发布日期有个小出入（有来源写 2026 年 3 月 6 日，也有写 3 月 7 日）。
- **领域迁移未经证实。** 几乎所有结果都来自 LLM 预训练、Kaggle、或数学/代码发现。自动驾驶和机器人在两个决定性方面不同：eval 贵得多（闭环仿真，或如 Eureka 那样把一整次 RL 训练当内层循环），且安全关键得多——所以人审 checkpoint 和硬约束否决项不可省。
- **已知失败模式是结构性的，不是 bug：** 局部搜索陷阱、Goodhart/指标作弊、开放性问题上的 RLHF 保守性、多目标坍缩、以及复现中的隐式知识缺口——这些在你们的场景里都会重现，应从第一天就做防御性设计。

---

### 附：术语对照（便于 review）

| 英文 | 中文 |
|---|---|
| ratchet (loop) | 棘轮（循环），只前进不后退的保留/回滚机制 |
| keep-or-revert | 保留或回滚 |
| evaluator / eval harness | 评测器 / 评测框架 |
| closed-loop / open-loop | 闭环 / 开环 |
| scalar metric | 标量指标 |
| ablation | 消融 |
| tree search / population | 树搜索 / 种群 |
| single-lineage | 单一谱系 |
| blast radius | 爆炸半径（影响范围） |
| Goodhart's law | 古德哈特定律（指标一旦成为目标就会被钻空子） |
| hard constraint / veto | 硬约束 / 否决项 |
| local-search trap | 局部搜索陷阱 |
| multi-objective collapse | 多目标坍缩 |
| reward reflection | 奖励反思 |
| ACI (Agent-Computer Interface) | 智能体-计算机接口 |
| spec | 规格说明（这里指 program.md 式的任务描述） |
