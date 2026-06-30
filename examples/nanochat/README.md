# nanochat — the GPU reference demo (needs a GPU)

> **Status: documented, not yet runnable here.** This repo's CI/sandbox has no GPU,
> so this demo is specified but **unverified**. Run it on a single NVIDIA GPU
> (RTX 3090/4090-class, 24GB; scalable down).

The Phase-1 flagship is reproducing Karpathy's `autoresearch` nanochat task through
Talos's loop, to show the same keep/revert mechanism on a real ML workload:

1. Provide a frozen evaluator (an L2 adapter) that returns `val_bpb` (lower-is-better)
   under a fixed compute budget, with a veto for divergence/NaN.
2. Point the `ratchet-experiment` skill (Claude Code / Codex) at the nanochat
   `train.py` as the agent-editable sandbox.
3. Run overnight via the `local` adapter on one GPU; the ledger should ratchet
   `val_bpb` downward.

**Comparability:** pin a single GPU class **or** switch from a wall-clock budget to
a deterministic compute budget (fixed steps/tokens), so results are comparable —
see [`../../docs/concepts/eval-first.md`](../../docs/concepts/eval-first.md).

Upstream reference: Karpathy's `autoresearch` (MIT).
