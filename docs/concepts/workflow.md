# The workflow: discover → reproduce → graft → validate

Talos is built around how an *applied* algorithm team actually adopts a community
idea — not around writing papers.

```
discover & distill  →  reproduce / confirm  →  graft into our framework  →  validate by experiment
```

## 1. Discover & distill  ·  skill: `distill-paper`
You see an idea in a paper or a product. Extract the *core mechanism*, the
*claimed metric*, a *minimal reproduction*, and the *constraints* — including the
implicit conventions papers omit (often recoverable from cited references and
their repos). Output is a structured spec, the analog of `program.md`. Heavy
reading is delegated to a subagent so it stays out of the main context.

## 2. Reproduce / confirm  ·  skill: `repro-harness`
Confirm the idea actually works *in isolation* against a frozen evaluator, before
touching your own code. Borrow two ideas from the reproduction literature:
- mine the idea's cited ancestors for undocumented implementation details;
- verify executability with generated unit tests, and re-run a fresh container so
  results cannot be faked/hardcoded.
Gate with a pass/fail rubric so "did it reproduce" is a scalar.

## 3. Graft into our framework  ·  skill: `graft-change`
This is the step generic "paper-to-code" tools skip: integrate the idea into your
**existing large codebase**, not a fresh `train.py`. Use a curated, lint-checked,
windowed tool surface (localize → edit → test), git-worktree isolation, and an
org-conventions file so the agent uses your internal libraries. Safety-critical
paths get human review.

## 4. Validate by experiment  ·  skill: `ratchet-experiment`
Wrap the change in the keep/revert ratchet against your closed-loop metric. Add
ablation to attribute the gain to the specific component; re-run for
reproducibility before accepting; escalate to grid/tree search when the greedy
loop plateaus.

## Why split it into four skills
Each stage has a different failure mode and a different tool surface, so each is a
separately testable, separately improvable unit. They compose, but you can adopt
them one at a time (the roadmap starts with `ratchet-experiment`). See
[`../../agent-skill/`](../../agent-skill/).
