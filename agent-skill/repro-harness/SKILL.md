---
name: repro-harness
description: >-
  Confirm a distilled idea actually works in isolation, against a frozen evaluator,
  before grafting it into a real codebase. Guards against fabricated or hardcoded
  results. Use after distill-paper and before graft-change.
---

> **Status: v0 scaffold — unverified.** End-to-end behavior not yet validated in
> this repo. See [`../../STATUS.md`](../../STATUS.md).

# repro-harness

Reproduce the idea in the smallest faithful setting and make "did it reproduce" a
**scalar**, so you trust it before touching production code.

## Steps
1. **Stand up a frozen evaluator (L2)** for the minimal reproduction — one scalar +
   hard-constraint vetoes (see [`../../constraints/`](../../constraints/)).
2. **Implement the minimal repro** in an isolated workspace (not your codebase).
3. **Verify executability** with sampling/smoke unit tests; run in a **fresh,
   isolated environment** (sandbox/container) so results cannot be hardcoded or leak
   state. See [`../../docs/survey/safety-sandboxing.md`](../../docs/survey/safety-sandboxing.md).
4. **Score against a pass/fail rubric** (the PaperBench idea): a weighted set of
   checks reduced to one number, so reproduction success is comparable.
5. **Record** the verdict and the frozen evaluator for `graft-change` to reuse.

## Output
A green/red reproduction verdict, plus a frozen evaluator the validation loop can
reuse. If it does not reproduce, stop — do not graft an unconfirmed idea.

## Notes
- Reproduction failure is information: often an implicit detail (seed, normalization,
  data split) the paper omitted — recover it via `distill-paper`'s lineage step.
