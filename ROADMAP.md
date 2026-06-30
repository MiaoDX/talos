# Roadmap

Talos is sequenced **evaluator-first**. The hard, non-skippable part is the
evaluation harness; the loop and the skills are comparatively easy once a good
metric exists.

## Phase 0 — Build the evaluator (the precondition)
Before writing a single skill, stand up **one** frozen evaluator for **one**
concrete internal task: a deterministic scorer returning a scalar + hard-
constraint vetoes, with a fixed budget and seed control.

- **Done when:** the same input reliably yields the same score; a known-good and
  a known-bad change are ranked correctly; one trial runs within the target
  budget; a human agrees the metric reflects production reality.
- **Why first:** every downstream loop is only as trustworthy as this. See
  [`docs/concepts/eval-first.md`](./docs/concepts/eval-first.md).

## Phase 1 — Codify the ratchet skill
Implement `ratchet-experiment` + the `local` (subprocess) adapter + the git+TSV
ledger.

- **Reference demo:** reproduce Karpathy's `autoresearch` on nanochat on a single
  GPU (RTX 3090/4090-class), end-to-end, as a public, low-cost example.
- **Done when:** the loop runs unattended overnight, produces a clean git history
  + ledger, and recovers from a crash.

## Phase 2 — Add distill / repro / graft skills + SkyPilot adapter
`distill-paper`, `repro-harness`, `graft-change`; the `skypilot` adapter for
cloud/k8s; sandboxing for agent-written code.

- **Done when:** one real community idea is distilled, reproduced, grafted into an
  existing codebase, and validated with a measured effect.

## Phase 3 — Escalation, attribution, parallelism
Factorial-grid parallel waves via SkyPilot; an attribution step (ablation) for
every accepted gain; an escalation step that routes safety-critical diffs to
human review.

- **Done when:** the loop can escape a local optimum it would otherwise be stuck
  in, and every kept change has an attributed cause.

## Decision thresholds (when to change strategy)
- Wins **fail to replicate** on a held-out set → the eval is overfit; rotate /
  expand it before continuing.
- The loop **plateaus quickly** → local-search trap; switch greedy ratchet →
  tree / evolutionary search.
- Experiments are **eval-bound** (agent idle, waiting) → parallelize across
  workers/GPUs; add novelty filtering to cut wasted runs.
- One objective term **dominates** → re-weight, or convert it to a hard-constraint
  veto.
- A task is **pure numeric hyperparameter tuning** → use Optuna / Ray Tune, not
  the LLM loop (see [`docs/pitfalls.md`](./docs/pitfalls.md)).

## Out of scope (deliberately)
- A new cloud/compute abstraction (we reuse SkyPilot).
- A new experiment-tracking product (we reuse git+TSV / MLflow).
- A research-paper-writing pipeline (Talos is engineering-oriented).
