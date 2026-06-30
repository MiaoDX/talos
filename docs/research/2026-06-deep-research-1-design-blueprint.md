# Deep Research 1 — AutoResearch for an Applied Algorithm Team: A Design-Philosophy Blueprint for Claude Code & Codex Skills

> Provenance: one of two deep-research reports that inform Talos. Topic-by-topic
> synthesis lives in [`../concepts/`](../concepts/) and [`../survey/`](../survey/).
> Several headline external numbers are self-reported or community-reported; see Caveats.

## TL;DR
- **Steal the loop, not the framework.** The single most transferable idea across every system surveyed — from Karpathy's autoresearch to AlphaEvolve, Curie, MLE-STAR, and the AI Scientists — is a disciplined *propose → bounded-budget experiment → hard scalar score → keep-or-revert* loop with git as the rollback primitive and a frozen, hard-to-game evaluator. For an applied team this becomes a small set of Claude Code / Codex skills plus a per-direction `program.md`-style spec and a frozen eval harness — not a new platform.
- **The real bottleneck is evaluation, not the agent.** Every project's ceiling is set by its metric: when experiments run ~100× faster than a human, a fast, deterministic, scalar, hard-to-game eval (with hard-constraint vetoes) becomes the precondition for autonomy. For autonomous driving and robotics this means investing up front in closed-loop simulation/scoring (CARLA, nuPlan, Waymax, MetaDrive, Isaac Lab, etc.) per sub-team direction *before* turning agents loose.
- **Match the mechanism to the task.** Use the greedy single-lineage ratchet for local refinement of an existing codebase; use tree search / evolutionary populations (AIDE, AI Scientist v2, ShinkaEvolve, AlphaEvolve) when you need to escape local optima; use ablation-guided attribution (MLE-STAR) and multi-agent rigor (Curie) when you need to know *why* something worked; and use paper-lineage reproduction ideas (AutoReproduce, Paper2Code) to mine the implicit knowledge papers omit — but adapt them, because they generate fresh repos and you must graft into a large existing one.

## Key Findings

### 1. The AutoResearch paradigm (Karpathy, March 2026)
Karpathy's `autoresearch` (released March 2026; the README slogan is effectively "one GPU, one file, one metric") is a ~630-line setup with a **three-file architecture** that encodes an ownership contract:
- **`prepare.py` — IMMUTABLE.** Data prep, tokenizer, dataloader, and the evaluation function (`evaluate_bpb`) plus the fixed time-budget constant. Neither human nor agent may edit it. This is the integrity guarantee: if the agent could touch the evaluator, it would make the test easier instead of making the model better.
- **`train.py` — AGENT SANDBOX.** The single file the agent mutates: full GPT model, Muon+AdamW optimizer, training loop. Everything is fair game — architecture, optimizer, hyperparameters, batch size.
- **`program.md` — HUMAN-OWNED.** Carries instructions, constraints, stopping criteria, the loop, and a "simplicity criterion." It steers hypotheses (Karpathy splits exploration into phases: obvious hyperparameter tuning → small architectural changes → moonshots).

**The ratchet loop:** on a dedicated git branch the agent (1) reads `program.md`, `train.py`, `results.tsv`; (2) proposes a change with explicit reasoning; (3) edits `train.py`; (4) commits; (5) runs training for **exactly 5 minutes wall-clock** (`uv run train.py > run.log`, redirected — never `tee` — to protect context); (6) greps `val_bpb` / `peak_vram_mb`; if empty the run crashed → read the last 50 log lines, attempt a fix, give up after a few tries; (7) if `val_bpb` improved (lower) the commit stays and becomes the new baseline, else `git reset` reverts instantly. ~12 experiments/hour, ~100 overnight.

**Why each choice matters (the transferable reasoning):**
- **`val_bpb` (validation bits-per-byte)** is chosen because it is a single scalar, lower-is-better, and *vocabulary-size-independent* — so architectural/tokenizer changes are compared fairly. The general lesson: pick a metric that stays comparable across the structural changes you expect the agent to make.
- **Fixed wall-clock budget** puts a "trains faster" change and a "converges lower" change on equal footing, and bounds blast radius (no run can run away with your GPU). Short runs also discourage overfitting to noise.
- **Git as rollback primitive:** the codebase can only move forward ("ratchet"); every kept commit is a validated improvement; the git log *is* the audit trail and the agent's memory (on restart it reads the log to see what was tried). `results.tsv` is deliberately left untracked.
- **It is NOT hyperparameter search.** AutoML/Optuna/Ray Tune search a predefined parameter space with convergence guarantees; autoresearch lets the LLM edit arbitrary code — open-ended search in *code space*, betting on the model's literature knowledge, with no theoretical guarantees.
- **Runs on top of an existing coding agent:** there is no orchestration script — "spin up your Claude/Codex in this repo" and tell it to read `program.md`.

**Reported results:** On the nanochat leaderboard the primary metric is "time to GPT-2" (wall-clock to beat the GPT-2 1.6B CORE score of 0.256525 on an 8×H100 node). The baseline was 2.02 hours; "autoresearch round 1" cut it to 1.80 hours (~11%) and a later round reached ~1.65 hours. Karpathy's two-day extended run produced ~700 experiments and ~20 additive improvements (a QK-Norm scalar multiplier fix, value-embedding regularization, banded-attention widening, AdamW beta correction, weight-decay scheduling) that transferred from a depth-12 to a depth-24 model. He cautioned the gains are "fragile" — some did not replicate, and there is overfitting risk. A community run reported `val_bpb` 0.9979 → 0.9697 over 126 experiments (community-reported, not Karpathy's own).

**Notable derivative — Shopify:** Shopify CEO Tobi Lütke applied an autoresearch-style loop (via the "Pi" coding agent and a `pi-autoresearch` plugin) to the Liquid templating engine. The verified artifact is Shopify/liquid PR #2056, "53% faster parse+render, 61% fewer allocations" (7,469 µs → 3,534 µs; 62,620 → 24,530 allocations) across 93 commits from ~120 automated experiments, with all 974 unit tests passing. Lütke himself wrote it is "probably somewhat overfit, but there are absolutely amazing ideas in this," and the PR remained unmerged for months with some external criticism of code quality. Further internal "#autoresearch-wins" claims (e.g., "unit tests 300× faster") are self-reported and unaudited.

**Limitations the authors/community report:**
- **Greedy local search.** The ratchet only moves forward; it can never go "worse before better," so it misses changes that set up a larger gain two steps later. It keeps a *single lineage*, not a population — the LLM is both mutation operator and selection pressure.
- **RLHF conservatism.** The agent feels "cagy and scared" on open-ended problems, attributable to RLHF rewarding safe, conservative outputs over bold experimentation.
- **Goodhart / metric gaming & overfitting.** Running 100+ experiments against one validation set risks improvements specific to that eval; the immutability of the evaluator is both the fairness guarantee and the blind spot.
- **Fixed short window hides slow-burn wins;** eval becomes the bottleneck.
- A meta-autoresearch "bilevel" variant (an outer loop that rewrites `program.md`/the mechanism) has been proposed and reported to beat parameter-only tuning — illustrating that the human-owned spec is itself an optimization surface.

The **awesome-autoresearch** lists document dozens of forks: GPU-kernel optimization, RAG retrieval, LiDAR SLAM on KITTI, MuJoCo/Gymnasium robotics (with simulator renderings + vision feedback), RL post-training, vision forks, and Claude/Codex skill packagings that generalize the keep/revert loop and add bounded iteration counts, git-as-memory, and safety hooks.

### 2. Rigorous experimentation frameworks
- **Curie (Just-Curieous).** An **Architect Agent** designs experimental plans (hypotheses, variables) and reflects; **Technician Agents** implement and execute controlled experiments; between them an **Experimental Rigor Engine** with three modules: *Intra-Agent Rigor* (validators that check setup matches plan and re-run experiments for reproducibility), *Inter-Agent Rigor* (control-flow enforcement, partition scheduling, and tiered write access so a technician can only append to its own partition), and an *Experiment Knowledge Module*. Its signature workflow is **Reproduce → Extend → Challenge**, with a reported 3.4× improvement over the strongest baseline (arXiv:2502.16069). The steal: *rigor is a first-class component; encode validators and tiered write permissions so an agent cannot silently corrupt the experimental record.*
- **MLE-STAR (Google).** Two ideas: **search-grounded initialization** (retrieve task-specific SOTA models via web search rather than relying on priors) and **ablation-guided targeted refinement** (an outer ablation finds the highest-impact code block; an inner loop deeply explores variations of *that block*). Plus a data-leakage checker. The steal: *attribute before you optimize.*
- **AIDE (Weco AI).** Frames ML engineering as **tree search in the space of code**: each node a full solution script; best-first search guided by the metric; summarizes history rather than appending everything. Strongest scaffold on MLE-bench. The steal: *keep a searchable tree of metric-tagged solution states so you can branch from the best, not just the latest.*

### 3. ML-engineering agents & their scaffolds
- **MLE-bench (OpenAI):** 75 Kaggle competitions in Docker. Crucial finding — *the scaffold matters as much as the model*: AIDE's purpose-built search beat general OpenHands/MLAB scaffolds. Instructive failure modes: filling context by reading thousand-line files; stopping early despite a 24h budget; failing to reason about compute/time limits (sometimes crashing the machine). The steal: *budget-awareness, context hygiene, and "keep going until budget is spent" must be baked in.*
- **Related systems** (MLGym, MLAgentBench, FM Agent, ML-Master, AutoSOTA) reinforce the same vocabulary: tree search, debugging loops, long-horizon execution, resource management.

### 4. Paper/algorithm reproduction agents
- **Paper2Code / PaperCoder:** a **plan → analyze → code** multi-agent pipeline; reference-free quality approaches author repos. The steal: *decompose paper-to-code top-down, not one-shot.*
- **AutoReproduce:** a **paper-lineage** algorithm mines implicit, undocumented knowledge by following citations (default k=3 references and their repos), with sampling-based unit tests to keep code executable; ships ReproduceBench. The steal: *pull in cited ancestors' code/conventions; verify executability with generated tests.*
- **PaperBench (OpenAI):** replication scored against author-co-developed hierarchical rubrics graded by an LLM judge; a fresh-container `reproduce.sh` catches hardcoded outputs. The steal: *a weighted pass/fail rubric turns "did it work" into an automatable scalar.*
- **Critical caveat:** these mostly **generate fresh repositories**. The reusable parts for an applied team are the planning/analysis decomposition and executability verification — not the from-scratch generation.

### 5. Repo-level / codebase-aware coding agents (the actual substrate)
- **SWE-agent / SWE-bench (Princeton):** the **Agent-Computer Interface (ACI)** insight — give the agent a curated, guard-railed action set (localize, windowed file view, linted edit, test) rather than a raw shell (+10.7 points in ablation). The steal: *curated, lint-checked, windowed tools + explicit sub-tasks, not raw bash.*
- **Claude Code & Codex:** exploit built-ins — git-worktree isolation per task, plan mode (read/propose before editing), subagents for codebase exploration (context hygiene), and skills (`SKILL.md` + scripts, portable to Codex). A real caveat: in large monorepos, worktrees can cost more (duplicated deps, DB/Redis instances) than they save.
- **Aider** is the executor used by The AI Scientist v1 — a thin git-aware edit/run loop is sufficient substrate.
- **Org-specific idioms:** encode libraries, conventions, and constraints in a `CLAUDE.md`/skill so the agent uses internal APIs — the equivalent of `program.md` carrying constraints.

### 6. End-to-end "AI Scientist" systems (transferable patterns, not products to adopt)
- **Sakana AI Scientist v1/v2:** v1 mutates an idea tree, checks novelty, uses Aider, has an automated reviewer; v2 uses a progressive agentic best-first **tree search** under an **experiment-manager agent** with VLM feedback on figures. (v2 is *less* reliable than v1 when a strong template exists — more exploration, less reliability.)
- **AI-Researcher (HKUDS):** a **Design → Implementation → Validation → Refinement** closed loop with explicit Validation and Refinement phases and an advisor that proposes the next ablation.
- **Google AI co-scientist:** a "generate, debate, evolve" loop where a Ranking agent runs an **Elo tournament** of pairwise scientific debates. The steal: *tournament/Elo ranking scalarizes "which idea is better" when no single metric suffices.*
- **Agent Laboratory & AgentRxiv:** a literature→experiment→writeup pipeline plus a **shared preprint server** where agent labs build on each other's reports (a 13.7% relative MATH-500 improvement when shared; arXiv:2503.18102). The steal: *a shared, searchable store of prior findings compounds results.*
- **Kosmos:** a **structured world model** (entities, relationships, results, open questions, updated each task) sustains coherence over ~200 rollouts (arXiv:2511.02824). The steal: *a persistent world model beats raw context windows for long-horizon coherence.*
- **Jr. AI Scientist:** explicitly **warns against real submissions**, cataloguing risks: fabricated results, mis-citation, method overfitting, scientific superficiality, "review hacking." The steal: *the risk catalogue is your anti-pattern checklist.*

### 7. Algorithm-discovery / evolutionary-search systems
- **FunSearch (DeepMind, 2023):** LLM + evaluator evolving small functions — the proof of concept.
- **AlphaEvolve (DeepMind, May 2025):** evolves **entire codebases**; the user supplies an initial program and an **evaluation function returning scalar metrics**; a Gemini ensemble is the mutation operator; a program database (MAP-Elites + island models) balances exploration/exploitation; supports multi-objective optimization; found a 48-multiplication algorithm for 4×4 complex matrix multiplication (beating Strassen's 49, a record since 1969). The crux: *the evaluation function is the whole game.*
- **OpenEvolve / CodeEvolve:** open-source reimplementations.
- **ShinkaEvolve (Sakana, Sept 2025):** sample-efficient via adaptive parent sampling, **novelty-based rejection sampling**, and **bandit-based LLM ensemble selection**; new SOTA on 26-circle packing in only 150 samples (arXiv:2509.19349). The steal: *novelty filtering and bandit model-selection slash wasted experiments.*
- **Eureka / DrEureka (NVIDIA):** LLM-written reward functions evolved with **reward reflection** (the LLM reads RL training stats and revises the reward); outperforms human experts on 83% of tasks (arXiv:2310.12931). Key tension: each outer iteration requires a full RL training run — expensive feedback. The steal (for robotics): *LLMs can author/refine reward/eval functions, but only as fast as the inner training+eval allows.*

### 8. Evaluation infrastructure as a first-class concern
The recurring lesson: **a fast, deterministic, scalar-izable, hard-to-game metric is the precondition for any autonomous loop.**
- **Eval becomes the bottleneck** when experiments run ~100× faster than humans — build the eval *first*.
- **Goodhart / hard-to-game design:** freeze the evaluator from the agent; use **hard-constraint vetoes** (e.g., nuPlan zeroes a scenario on at-fault collision or drivable-area violation regardless of comfort); use multi-objective → scalarization carefully, watching for multi-objective collapse.
- **Bound scope and fix budgets;** MLE-bench shows agents that ignore compute limits crash.
- **Reproducibility / determinism / seeds:** Curie re-runs for reproducibility; multi-seed runs handle non-determinism.
- **Static-benchmark saturation:** evolving/held-out sets keep the metric honest.
- **Illustrative pointers for AD/robotics (not prescriptive):** open-loop (cheap, compounding-error-blind) vs closed-loop (predictive but expensive) — CARLA, MetaDrive (sensor-based, reactive), nuPlan, Waymax (planning-centric, log-based), nuScenes (open-loop), NAVSIM (sensor-based, non-reactive), Bench2Drive (CARLA v2), Isaac Sim/Lab (robotics). Stand up the right closed-loop scorer per direction before automating.

## Details: A blueprint for the workflow loop

The loop — **discover & distill → reproduce/confirm → graft into the existing framework → validate the effect** — maps onto these motifs:

- **Stage A — Discover & distill (`distill-paper`).** Borrow Paper2Code's top-down decomposition and AutoReproduce's paper-lineage idea: a subagent reads the paper *and its key references/repos* to extract explicit method + implicit conventions, emitting a structured spec (the analog of `program.md`). Keep heavy reading out of the main context via subagents.
- **Stage B — Reproduce/confirm (`repro-harness`).** Stand up a frozen eval harness *first* (the immutable-`prepare.py` lesson). Use AutoReproduce's unit tests and PaperBench's fresh-container `reproduce.sh` to confirm executability and guard against fabricated results. Gate with a hierarchical pass/fail rubric so "did it reproduce" is a scalar.
- **Stage C — Graft into the existing codebase (`graft-change`).** Where from-scratch generators don't help. Use SWE-agent ACI discipline (windowed reads, linted edits, localize→edit→test), git-worktree isolation, and an org-idioms `CLAUDE.md`. Plan mode + human-review checkpoints for safety-critical paths.
- **Stage D — Validate the effect (`ratchet-experiment`).** Wrap the change in the ratchet: fixed compute/sim budget, scalar closed-loop metric with hard-constraint vetoes, commit on improvement / reset on regression, append to a ledger. Add MLE-STAR-style ablation for attribution and Curie-style reproducibility re-runs before accepting; escalate to AIDE/ShinkaEvolve tree/population search when local search plateaus.
- **Cross-cutting orchestration:** keep a shared, searchable experiment store (AgentRxiv/Kosmos lesson); use a bandit/Elo idea when choosing among models or ranking ideas without a single clean metric.

## Recommendations
- **Phase 0 — Build the evaluator (per direction).** A fast, deterministic, scriptable closed-loop scorer returning a scalar + hard-constraint vetoes, fixed budgets, seed control. Do not start agentic loops until it exists. *Pass when:* same input → same score; a known-good and known-bad change are ranked correctly; one trial fits the budget.
- **Phase 1 — Codify the ratchet as a skill.** `ratchet-experiment` for Claude Code/Codex with bounded iterations, context hygiene, crash recovery, budget-awareness. Start on a non-safety-critical offline-metric task.
- **Phase 2 — Add distill/repro/graft skills.** Require a green reproduction before any graft; human review on safety-critical diffs; encode org idioms.
- **Phase 3 — Escalation & attribution.** Ablation on every accepted win; reproducibility re-runs; tree/population search where the greedy ratchet plateaus; a shared experiment store.
- **Thresholds:** wins fail to replicate → eval overfit, rotate/expand it; quick plateau → switch to tree/evolutionary search; eval-bound → parallelize + novelty filter; one objective dominates → re-weight or veto.

## Caveats
- **Maturity varies widely.** Karpathy's autoresearch is weeks old and explicitly a minimal, "fragile" demonstrator; AlphaEvolve is closed-source; Curie/AIDE/ShinkaEvolve/Paper2Code/AutoReproduce/AI-Researcher are research-grade open source; Claude Code/Codex/SWE-agent are production substrate. Treat the AI-Scientist systems as *pattern sources*, not products.
- **Reported numbers need scrutiny.** Several figures are self-reported or community-reported (Shopify's internal multipliers; the 126-experiment run); the verified Shopify artifact is PR #2056, which the CEO flagged as "probably somewhat overfit."
- **Domain transfer is unproven.** Almost all results are from LLM pretraining, Kaggle, or math/code discovery. AD/robotics differ decisively: eval is far more expensive (closed-loop sim or RL training as the inner loop) and safety-critical, so human-review checkpoints and hard-constraint vetoes are non-negotiable.
- **The known failure modes are structural, not bugs:** local-search traps, Goodhart/metric gaming, RLHF conservatism, multi-objective collapse, and implicit-knowledge gaps in reproduction will recur and should be designed against from day one.
