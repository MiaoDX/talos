# ADR 0001: Ledger and audit model

**Status:** Accepted  
**Date:** 2026-07-01

## Context

The ratchet loop uses git because git is the right rollback primitive: commit a
candidate, evaluate it, keep the commit only if the frozen metric improves, and
reset otherwise. That is not the same thing as using git as the experiment
database.

The git repository in this model is the **target experiment repo/worktree**. The
Talos repository itself is a control repo that should remain small: it contains
the method, reference engine, runbooks, docs, tests, and demos, not production
experiment history.

A reverted candidate disappears from the kept lineage, but failed experiments are
still research signal. They prevent the agent from repeating known-bad changes,
show which vetoes fired, and give humans an audit trail for claims about the
loop. Hand-written docs are useful for summaries, but they are too lossy and too
easy to forget as the raw source of truth.

## Decision

Talos separates the audit model into three layers:

1. **Git stores code state and rollback.** The kept branch should contain only the
   current validated lineage. Optional experiment refs may preserve reverted
   candidate commits, but the main branch is not the run database. For real
   experiments, this branch lives in the target repo/worktree passed to Talos.
2. **The append-only ledger stores every experiment fact.** Every baseline,
   keep, revert, veto, crash, policy violation, and no-change attempt gets a row.
   The ledger records commit IDs, metric/delta, status, evaluator identity,
   seeds, vetoes, sub-metrics, and an artifact reference when available.
3. **Docs store human decisions and summaries.** ADRs and experiment reports
   explain why the evaluator, budget, and search strategy were chosen. They can be
   generated or curated from the ledger, but they are not the raw record.

For now the Tier-0 implementation remains TSV for zero-dependency portability,
but its schema is explicitly factual and extensible. A future JSONL or MLflow
adapter can implement the same contract without changing the ratchet semantics.

## Implementation rules

- The ledger is append-only and excluded from `git add -A` / reset side effects.
- Per-run artifacts live under `.talos/runs/<run_id>/` by default and are also
  excluded from the candidate commit. Each run should preserve the candidate patch
  and, when available, the raw evaluator result or error text.
- The experiment worktree must be clean before a ratchet run starts. Failed,
  vetoed, or policy-violating attempts reset to the pre-experiment commit and
  remove only untracked files created by that attempt.
- The evaluator, `program.md`, and any configured protected paths are checked
  before commit. Changing one is a `policy_violation`, not an experiment.
- If `editable_paths` is configured, changes outside that sandbox are rejected
  before commit.
- Proposal, git, or adapter exceptions become `status=crash` rows and the worktree
  is reset to the pre-experiment commit.
- The evaluator's `lower_is_better` direction must match the run direction; a
  mismatch is represented as a veto rather than silently changing the comparison.

## Consequences

This makes the ratchet more explicit: git remains clean and forward-only, while
failed attempts are still visible to agents and reviewers. It also clarifies the
role of docs: they are the decision layer, not the fragile place where every raw
run must be hand-entered.
