---
name: attribute
description: >-
  For an accepted improvement, attribute the gain to the specific component via
  ablation, and confirm it is real (not noise) with multi-seed re-runs, before
  trusting or shipping it. Use after ratchet-experiment keeps a change.
---

> **Status: v0 scaffold — unverified.** Behavior not yet validated end-to-end in this
> repo. See [`../../STATUS.md`](../../STATUS.md).

# attribute

A kept change is not yet an understood change. Before trusting a win, find out *what*
caused it and whether it survives noise (guards against overfitting / lucky runs —
see [`../../docs/pitfalls.md`](../../docs/pitfalls.md)).

## Steps
1. **Ablate.** For the accepted change, construct minimal variants that remove or
   vary the suspected component (the MLE-STAR idea), each scored by the same frozen
   evaluator. The drop when the component is removed is its contribution.
2. **Re-run across seeds.** Run the change and the baseline over multiple seeds; treat
   run-to-run variance as the significance bar. Keep the gain only if it exceeds noise.
3. **Check for gaming / leakage.** Confirm the gain is not the metric being satisfied
   by a shortcut (Goodhart) or data leakage.

## Output
An attribution report: which component caused the gain, the effect size, and its
seed-stability — attached to the experiment in the ledger. If the gain does not
survive ablation or seeds, revert it.
