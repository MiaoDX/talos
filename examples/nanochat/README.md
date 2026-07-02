# nanochat — the release-required GPU reference demo

> **Status: release-required, not yet runnable here.** CPU CI does not prove the
> full Talos value proposition. A release or external demo needs current evidence
> from this path on a single NVIDIA GPU plus a SkyPilot SSH GPU smoke. Until that
> evidence exists, this demo is specified but **unverified**.

The Phase-1 flagship is reproducing Karpathy's `autoresearch` nanochat task through
Talos's loop, to show the same keep/revert mechanism on a real ML workload:

1. Provide a frozen evaluator (an L2 adapter) that returns `val_bpb` (lower-is-better)
   under a fixed compute budget, with a veto for divergence/NaN.
2. Point the `ratchet-experiment` skill (Claude Code / Codex) at the nanochat
   `train.py` as the agent-editable sandbox.
3. Run a short smoke and an overnight run via the `local` adapter on one GPU. The
   smoke only needs baseline plus one candidate outcome; the overnight release
   run should either keep at least one improvement or record a reproducible
   no-improvement result.
4. Run a short-budget smoke of the same evaluator contract through SkyPilot
   against an existing GPU machine registered as an SSH Node Pool. The first
   runbook should support using this same GPU host as the SSH pool target.
5. Start with scripted proposals so the evaluator, ledger, rollback, and adapter
   paths are proven before live agent-generated edits are introduced.

**Comparability:** pin a single GPU class **or** switch from a wall-clock budget to
a deterministic compute budget (fixed steps/tokens), so results are comparable —
see [`../../docs/concepts/eval-first.md`](../../docs/concepts/eval-first.md).

See [`../../docs/human/testing-strategy.md`](../../docs/human/testing-strategy.md)
for the release gates and SkyPilot path ordering.

Upstream reference: Karpathy's `autoresearch` (MIT).
