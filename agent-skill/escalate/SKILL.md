---
name: escalate
description: >-
  Handle the two situations the greedy ratchet cannot: route safety-critical or
  high-risk changes to human review, and switch search strategy when the loop
  plateaus (greedy local search -> grid / tree / evolutionary). Use from inside a
  ratchet-experiment loop.
---

> **Status: v0 scaffold — unverified.** Behavior not yet validated end-to-end in this
> repo. See [`../../STATUS.md`](../../STATUS.md).

# escalate

The keep/revert ratchet is greedy and autonomous. Two conditions require escalation.

## Trigger 1 — safety-critical / high-risk change
If a proposed change touches a safety-relevant path (planner, controller, anything
that could cause real-world harm) or is otherwise high-risk:
- **Stop autonomous merging.** Treat the result as *candidate evidence only*.
- Open a human-review request with: the diff, the measured effect, the evaluator
  used, and the residual risks.
- Proceed only after a human approves. See [`../../AGENTS.md`](../../AGENTS.md).

## Trigger 2 — the loop has plateaued (local-search trap)
If `N` consecutive experiments fail to improve the metric beyond measured noise, the
greedy ratchet is likely stuck in a local optimum (see
[`../../docs/pitfalls.md`](../../docs/pitfalls.md)). Switch strategy:
- **Factorial grid** — sweep several variants in parallel to catch interaction
  effects (see [`../../src/talos/orchestration.py`](../../src/talos/orchestration.py)).
- **Tree search** — branch from the best node, not just the latest (AIDE-style).
- **Evolutionary search** — a population with novelty rejection (ShinkaEvolve /
  OpenEvolve-style) when single-lineage search is exhausted.
- Or **hand a moonshot to a human** to seed a bigger architectural bet.

## Output
Either a human-review request (Trigger 1) or a switch to a broader search procedure
(Trigger 2), recorded in the ledger so the change of strategy is auditable.
