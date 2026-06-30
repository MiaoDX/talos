# Talos

**一个 eval 驱动、可跨领域迁移的 AutoResearch 框架 —— 以 coding agent 的 skills 形式交付。**

> *Talos 是希腊神话里不知疲倦巡守克里特海岸的青铜自动机。这个 Talos 在你睡觉时不知疲倦地跑实验 —— 并且只保留评测器判定更好的那些。*

[English](./README.md) · [架构](./ARCHITECTURE.md) · [路线图](./ROADMAP.md) · [状态](./STATUS.md)

---

## 一句话

coding agent 的上限取决于它的 **harness**,而不是模型本身:

```
coding agent = AI model(s) + harness
```

软件开发的 harness 已经成熟(跑测试、看 diff、迭代)。但**研究型工作——"我在某篇 paper / 某个 product 里看到一个想法,它对*我们的*系统真的有用吗?"——的 harness 一直缺失**。"AutoResearch" 就是这个 harness:一个有纪律的循环,提出一个改动、跑一个有界实验、用一个冻结的指标打分、**只在更好时保留**(否则回滚)。

Talos 把这个循环打包成 **Claude Code 和 OpenAI Codex 的可移植 skills**,设计上**eval 驱动优先**、且**易于跨领域迁移**。自动驾驶和机器人是我们的前两个落地领域;核心里没有任何东西是绑定其中之一的。

## 为什么再做一个 repo?(Talos 是什么、不是什么)

AutoResearch 生态已经有了范式(Karpathy 的 [`autoresearch`](https://github.com/karpathy/autoresearch))、算力底座([SkyPilot](https://github.com/skypilot-org/skypilot))、以及很多单文件 fork。Talos **不重造**这些。它押注于没人打包好的两件事:

1. **把社区想法嫁接进一个*已有的*大代码库** —— 而不是从零生成一个 `train.py`。
2. **一个领域可插拔、难以被 game 的*评测*契约** —— 因为在机器人和驾驶里,指标(闭环仿真、多目标、安全门控)才是难点,而它是任何自治的前提。

Talos 是**一个薄的方法论层 + 一组 agent skills**,不是一个平台。算力、实验追踪、沙箱都**复用**已有工具。

## 它支持的工作流

```
发现 & 提炼  →  复现 / 确认  →  嫁接进我们的框架  →  用实验验证
 (读 paper)     (是否有效?)      (我们已有的代码库)      (keep/revert 循环)
```

每一步(将)是一个 skill:`distill-paper`、`repro-harness`、`graft-change`、`ratchet-experiment`。见 [`agent-skill/`](./agent-skill/)。

## 架构一览

四个松耦合、各自可替换的层(完整细节见 [`ARCHITECTURE.md`](./ARCHITECTURE.md)):

| 层 | 是什么 | 自建还是复用 |
| --- | --- | --- |
| **L0** 执行契约 + adapter | 提交一个实验 → 拿到标量 + 产物 | 薄契约(我们)+ `local`/`skypilot` adapter(复用) |
| **L1** 账本契约 | append-only 实验记录 = agent 的记忆 + 审计轨迹 | git + TSV(默认);MLflow/Aim 藏在契约后 |
| **L2** Eval 契约 | 一个冻结的打分器,返回标量 + 硬约束否决项 | **由我们定义;领域 adapter 插在这里** ([`constraints/`](./constraints/)) |
| **L3** Agent skills | 把循环打包给 Claude Code / Codex | **产品本体** ([`agent-skill/`](./agent-skill/)) |

## 状态

**Pre-alpha —— 文档优先。** 思路和设计已经在这里;skills 和 adapter 尚未实现。我们先把架构公开出来以便在开放环境里讨论。见 [`STATUS.md`](./STATUS.md) 和 [`ROADMAP.md`](./ROADMAP.md)。第一个里程碑是**建评测器**,不是写 skill。

## 文档

- **概念** — [`docs/concepts/paradigm.md`](./docs/concepts/paradigm.md)、[`eval-first.md`](./docs/concepts/eval-first.md)、[`workflow.md`](./docs/concepts/workflow.md)
- **综述(深度调研,按主题)** — [`compute-backends`](./docs/survey/compute-backends.md)、[`experiment-ledger`](./docs/survey/experiment-ledger.md)、[`agent-skills`](./docs/survey/agent-skills.md)、[`safety-sandboxing`](./docs/survey/safety-sandboxing.md)、[`eval-ecosystems`](./docs/survey/eval-ecosystems.md)、[`landscape`](./docs/survey/landscape.md)
- **坑** — [`docs/pitfalls.md`](./docs/pitfalls.md)
- **出处** — 原始调研报告在 [`docs/zh/research/`](./docs/zh/research/)

## 致谢

Talos 站在开放 AutoResearch 生态的肩膀上 —— 最直接的是 Andrej Karpathy 的 `autoresearch`、SkyPilot,以及 [`docs/survey/landscape.md`](./docs/survey/landscape.md) 中梳理的更广泛工作。

## 许可

[MIT](./LICENSE)。
