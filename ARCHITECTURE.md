# Architecture

Talos is four loosely-coupled layers. Each is independently swappable behind a
thin contract. The contribution lives in **L2 (eval)** and **L3 (skills)**; L0
and L1 are mostly *reuse*.

```
┌─────────────────────────────────────────────────────────────────┐
│ L3  Agent skills  (the product)                                   │
│     distill-paper · repro-harness · graft-change · ratchet-exp    │
├─────────────────────────────────────────────────────────────────┤
│ L2  Eval contract  (frozen scorer → scalar + hard-constraint vetoes)
│     domain adapters plug in here  →  constraints/                 │
├─────────────────────────────────────────────────────────────────┤
│ L1  Ledger contract  (append-only record = memory + audit trail)  │
│     default: git + TSV   ·   optional: MLflow / Aim               │
├─────────────────────────────────────────────────────────────────┤
│ L0  Execution contract + adapters                                 │
│     submit(experiment) → poll → fetch(scalar, artifacts)          │
│     adapters: local (subprocess) · skypilot (cloud/k8s)           │
└─────────────────────────────────────────────────────────────────┘
```

## Design principles

1. **Eval-driven first.** The loop is meaningless without a fast, deterministic,
   scalar, hard-to-game metric. The eval contract (L2) is therefore the center of
   gravity, not an afterthought. See [`docs/concepts/eval-first.md`](./docs/concepts/eval-first.md).
2. **Reuse, don't rebuild.** Compute, tracking, and sandboxing are solved
   problems. Talos wraps them behind thin contracts and ships reference adapters.
3. **Domain-pluggable.** Moving to a new domain (driving → manipulation →
   locomotion → anything) means writing a new **L2 adapter**, not touching L0/L1/L3.
4. **Thin, honest contracts.** A contract is the *intersection* of what the
   underlying tools already do — small enough that anything able to run a scored
   experiment conforms.

## L0 — Execution contract + adapters

A minimal interface, roughly:

```
submit(experiment_spec) -> handle      # ship code + resource spec + budget, start a run
poll(handle)            -> status      # queued | running | done | failed
fetch(handle)           -> result      # { scalar, metrics, logs, artifact_ref }
```

- **`local` adapter** — a subprocess on the current machine. Zero dependencies.
  This is the single-GPU "run it overnight on my own box" path, mirroring
  `autoresearch`'s "just spin up your agent in this repo."
- **`skypilot` adapter** — delegates to [SkyPilot](https://github.com/skypilot-org/skypilot)
  for BYO-cloud / Kubernetes / Slurm, cost arbitrage, and queueing. China clouds
  are reached via their managed Kubernetes (Alibaba ACK, Volcano Engine VKE) or a
  custom SkyPilot plugin. We do **not** define a new cloud abstraction.

**The comparability decision (important).** A *fixed wall-clock* budget makes
experiments comparable on one machine but breaks across heterogeneous GPUs (the
same config scores differently on an H100 vs an H200 because the step count in a
fixed window differs). For multi-cloud you must either **pin a hardware class** or
switch to a **deterministic compute budget** (fixed steps / tokens / FLOPs /
scenario-count). For closed-loop simulation, fix the scenario set and seeds, not
the wall clock. See [`docs/survey/compute-backends.md`](./docs/survey/compute-backends.md).

## L1 — Ledger contract

An append-only record of every experiment: `experiment, commit, metric, delta,
status, description`, plus seeds and resource usage. It is simultaneously the
**agent's cross-run memory** and the **human audit trail**.

- **Tier 0 (default):** a git-committed TSV. The git history *is* the audit
  trail; the agent reads the log before each step. Immutable / append-only.
- **Tier 1 (optional):** MLflow (recommended) or Aim behind the same contract,
  for a queryable UI at scale.
- **Tier 2:** an adapter to an internal tracking system.

See [`docs/survey/experiment-ledger.md`](./docs/survey/experiment-ledger.md).

## L2 — Eval contract (the moat)

A frozen scorer that nobody edits during a lineage, exposing **one scalar**
(lower- or higher-is-better) plus **hard-constraint vetoes**. This is where your
domain expertise becomes the differentiator.

- **Multi-objective → scalar + vetoes.** Real tasks are multi-objective (safety /
  comfort / efficiency / progress). The pattern, borrowed from mature benchmarks:
  **multiplicative gates for hard constraints** (a collision zeroes the score),
  **weighted sum for soft objectives**.
- **Domain adapters** live in [`constraints/`](./constraints/). A driving adapter
  might wrap a closed-loop simulator; a manipulation adapter might wrap a success
  rate over a task suite. Both are *illustrative* — each sub-team writes the
  scorer that reflects its own production reality.
- **Anti-gaming is structural:** the evaluator is immutable to the agent;
  guardrails break if the headline metric is gamed. See [`docs/pitfalls.md`](./docs/pitfalls.md).

See [`docs/concepts/eval-first.md`](./docs/concepts/eval-first.md) and
[`docs/survey/eval-ecosystems.md`](./docs/survey/eval-ecosystems.md).

## L3 — Agent skills (the product)

The loop, packaged as portable Agent Skills (`SKILL.md` + scripts) for Claude Code and OpenAI Codex:

- **`distill-paper`** — read a paper/product (and its key references); extract the
  core mechanism, the claimed metric, a minimal reproduction, and the constraints.
- **`repro-harness`** — confirm the idea works in isolation against a frozen eval;
  guard against fabricated / hardcoded results.
- **`graft-change`** — integrate the idea into the *existing* codebase behind
  tests, using a curated, lint-checked tool surface and git-worktree isolation.
- **`ratchet-experiment`** — the keep/revert loop: propose → bounded run → score →
  commit-or-revert → log; escalate to grid/tree search when the greedy loop
  plateaus; attribute gains via ablation.

See [`agent-skill/`](./agent-skill/) and [`docs/survey/agent-skills.md`](./docs/survey/agent-skills.md).

## How the layers compose

A single `ratchet-experiment` step:

```
read ledger (L1) + program/spec
  → propose a change, edit code (L3, via the coding agent on the existing repo)
  → submit experiment with a fixed budget (L0 adapter: local or skypilot)
  → score with the frozen evaluator + vetoes (L2)
  → keep (git commit) or revert (git reset); append to ledger (L1)
```

Sandboxing (running agent-written code safely) wraps L0 — see
[`docs/survey/safety-sandboxing.md`](./docs/survey/safety-sandboxing.md).
