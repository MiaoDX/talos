# program.md — toy_mlp experiment spec (human-owned)

**Goal:** minimize validation log-loss on a synthetic binary-classification task.

**Rules**
- You may edit `solution.py` only. `evaluator.py`, the dataset, and the metric are frozen.
- Scalar metric: validation log-loss (**lower is better**).
- Hard constraint (veto): predictions and loss must be finite. A NaN/inf or a crash
  disqualifies the experiment (it will be reverted).

**Exploration phases** (cheap → bold)
1. Obvious tuning: `LR`, `EPOCHS`.
2. Representation: the two features are on very different scales — consider standardization.
3. Model structure: a different/larger model.

**Stop** when improvements stall.

> This is a tiny, CPU-only, seconds-to-run **mechanism demo** for the ratchet loop.
> It is deliberately HPO-ish; the real value of the loop is structural code changes
> on a real codebase (see `docs/pitfalls.md`).
