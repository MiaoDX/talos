# Survey: the competitive / research landscape

Where Talos sits relative to everything else building "autonomous experimentation
/ AI research engineering."

## AutoResearch-native (the direct lineage)
- **Karpathy `autoresearch`** — the paradigm reference (ratchet loop, three-file
  contract). Many single-file forks exist (robotics, RL, SLAM, vision, kernels),
  plus skill packagings for Claude/Codex and curated `awesome-autoresearch` lists.
- **SkyPilot scaling work** — parallel/multi-GPU `autoresearch`.
- **Status: saturated** for generic single-file tasks and "any measurable goal"
  skills.

## Academic "AI research engineer" systems
- **AI Scientist v1/v2** (Sakana) — agentic tree search, experiment-manager agent.
- **Curie** — rigorous experimentation (controlled trials, reproducibility);
  Reproduce → Extend → Challenge.
- **MLE-STAR** (Google) — search-grounded init + ablation-guided targeted refinement.
- **AIDE** (Weco AI) — tree search in code space; strong MLE-bench scaffold.
- **AI-Researcher** (HKUDS) — Validation + Refinement closed loop.
- Benchmarks: MLE-bench, RE-Bench, MLGym, PaperBench, EXP-Bench.
- **Recurring lesson:** these score well on novelty/clarity but below threshold on
  soundness — implementation capability is the gating factor.

## Evolutionary coding agents (escape local optima)
- **AlphaEvolve** (DeepMind, closed) — LLM + evolutionary search; needs an
  evaluation function + initial program.
- **OpenEvolve** (open), **ShinkaEvolve** (Sakana, Apache-2.0; sample-efficient via
  bandit LLM ensemble + novelty rejection), **CodeEvolve**.
- **Eureka / DrEureka** (NVIDIA) — LLM-written reward functions + evolution; the
  inner loop is a full RL training run (expensive).

## Paper-to-code / reproduction
- **Paper2Code/PaperCoder** (plan → analyze → code), **AutoReproduce** (paper
  lineage + unit tests), **PaperBench** (replication eval). These **generate fresh
  repos** — useful for the *reproduce* step, but not the *graft-into-existing*
  step.

## Robotics autoresearch (emerging)
- **ENPIRE** (NVIDIA GEAR) — autoresearch for real-hardware robot policy
  self-improvement.
- **autoresearch-robotics** — MuJoCo/Gymnasium fork with vision feedback (small).

## Where Talos fits (the under-served niche)
Not competing with paper-writing pipelines or evolutionary frameworks. Talos's
wedge is the **engineering** workflow — *distill a community idea → reproduce →
graft into an existing large codebase → validate via closed-loop sim* — combined
with a **domain-pluggable, hard-to-game eval contract** for AD and robotics. As of
mid-2026, no public repo packages that combination.
