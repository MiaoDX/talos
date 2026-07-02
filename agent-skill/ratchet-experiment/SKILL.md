---
name: ratchet-experiment
description: >-
  Run a disciplined keep/revert experiment loop against a frozen scalar evaluator.
  Use when iterating on a model, algorithm, or piece of code to find improvements:
  propose a change, run a bounded experiment, score it, and keep the change only if
  it improves the metric (otherwise revert). Requires a frozen evaluator that emits a
  single scalar plus hard-constraint vetoes.
---

# ratchet-experiment

Propose a change → run a **bounded** experiment → score it against the **frozen**
evaluator → **keep** (commit) if it improves the metric, else **revert** to the
pre-experiment commit. The codebase only ratchets forward; the append-only ledger
is the raw experiment memory and the git log is the kept-code lineage.

## Preconditions
- **A frozen evaluator (L2).** It owns the data and the metric and emits a
  contract-conformant JSON line: `{"scalar", "vetoes", "metrics", "seeds",
  "lower_is_better"}` (see `src/talos/contract.py`). You must **never** edit it.
- **A git repo on a dedicated branch** (e.g. `autoresearch/<task>`), with the
  agent-editable sandbox file(s) identified (the analog of `train.py`).
- **Protected paths.** The evaluator, `program.md`, data, and metric files are out
  of scope. A change to one of them is a policy violation, not an experiment.
- **A budget:** a per-experiment time/compute budget *and* an iteration cap.
- **A spec** (`program.md`) stating the goal, constraints, and stopping criteria.

## The loop (one iteration)
1. **Read** `program.md`, the code, and the ledger (`results.tsv`) — your memory.
2. **Propose ONE focused change**, with explicit reasoning. Prefer structural/idea
   changes; pure numeric hyperparameter sweeps belong in Optuna/Ray Tune.
3. **Edit** the sandbox file(s). Check that only editable paths changed and that no
   protected path changed.
4. **Save the candidate patch** under the run artifacts, then commit the candidate.
5. **Run** the evaluator via the execution adapter under the budget. Redirect logs
   to a file; **grep the scalar** — never read giant logs wholesale.
6. **If it crashed/timed out:** attempt a fix a few times; else revert and log
   `status=crash`. Do not stall waiting for a human.
7. **If the scalar improved and no veto fired:** keep the commit (new baseline).
   **Else:** reset to the pre-experiment commit.
8. **Append a row** to the ledger for every outcome: `keep`, `revert`, `veto`,
   `crash`, `policy_violation`, or `discard`.

Repeat until the iteration cap is hit or improvements stall.

## Rules (see ../../AGENTS.md)
- The evaluator, metric, and data are **immutable**. If you want to change the
  yardstick, stop — that is a separate, human-reviewed change.
- **Bounded autonomy:** respect the iteration cap and the budget; never an unbounded
  loop.
- **Three-state self-assessment** per experiment: **keep / discard / crash**.
- **Be honest:** revert changes that don't beat the metric beyond noise; never
  fabricate a number or report partial work as complete.
- **Safety-critical paths** are candidate evidence only — flag for human review,
  don't merge autonomously.
- **Ledger first:** git stores the kept code lineage; the append-only ledger stores
  the factual run history, including failed/reverted attempts.

## Reference implementation
- Engine: [`../../src/talos/ratchet.py`](../../src/talos/ratchet.py) (`run_ratchet`).
- Runnable CPU demo (seconds, no GPU): [`../../examples/ratchet_demo/`](../../examples/ratchet_demo/).
- GPU reference task (nanochat, needs a GPU): [`../../examples/nanochat/`](../../examples/nanochat/).

In production **you** are the proposer: you edit the sandbox file each iteration and
invoke the evaluator through the adapter, applying the keep/revert decision above.
The engine's scripted `Proposal` list exists so the loop can be tested without an LLM.

## Comparability
If experiments may run on different hardware, pin a single hardware class **or** use
a deterministic compute budget (fixed steps/tokens/FLOPs/scenario-count) instead of
wall-clock — otherwise scores are not comparable. See
[`../../docs/concepts/eval-first.md`](../../docs/concepts/eval-first.md).

## When to escalate
If the greedy loop plateaus, you are likely in a local-search trap: switch to a
grid/tree/evolutionary search and attribute gains by ablation (Phase 3:
`escalate` / `attribute`). See [`../../docs/pitfalls.md`](../../docs/pitfalls.md).
