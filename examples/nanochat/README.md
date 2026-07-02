# nanochat - the release-required GPU reference demo

> **Status: implemented runbook, not release-verified.** CPU CI verifies the
> Talos wrapper code and SkyPilot task shape. A release or external demo still
> needs current evidence from this path on a single NVIDIA GPU plus a SkyPilot SSH
> GPU smoke.

The Phase-1 flagship is reproducing Karpathy's `autoresearch` nanochat task
through Talos's loop, to show the same keep/revert mechanism on a real ML
workload:

1. Use [`evaluator.py`](./evaluator.py) as the Talos L2 wrapper. It runs
   upstream training, parses `val_bpb` (lower is better), and maps crashes,
   timeouts, missing metrics, non-finite values, and optional budget/VRAM
   guardrails to vetoes.
2. Point the `ratchet-experiment` skill (Claude Code / Codex) at the nanochat
   `train.py` as the agent-editable sandbox.
3. Start with the scripted proposals in [`proposals.py`](./proposals.py), so the
   evaluator, ledger, rollback, and adapter paths are proven before live
   agent-generated edits are introduced.
4. Run a short smoke and an overnight run via the `local` adapter on one GPU. The
   smoke only needs baseline plus one candidate outcome; the overnight release
   run should either keep at least one improvement or record a reproducible
   no-improvement result.
5. Run a short-budget smoke of the same evaluator contract through SkyPilot
   against an existing GPU machine registered as an SSH Node Pool. The same-host
   path is supported by [`skypilot_ssh_smoke.py`](./skypilot_ssh_smoke.py).

## Local GPU smoke

Use a clean upstream `karpathy/autoresearch` worktree with data prepared:

```bash
git clone https://github.com/karpathy/autoresearch.git /tmp/autoresearch
cd /tmp/autoresearch
uv sync
uv run prepare.py
```

Then run the Talos wrapper from this control repo:

```bash
uv run python examples/nanochat/run_local_gpu.py /tmp/autoresearch --max-iterations 2
```

The target worktree receives the kept git lineage, `results.tsv`, and
`.talos/runs/` artifacts. The Talos control repo should only link concise
evidence in [`../../docs/human/release-evidence.md`](../../docs/human/release-evidence.md).

## SkyPilot SSH smoke

Register an existing GPU host as a SkyPilot SSH Node Pool, then inspect the task:

```bash
uv sync --group sky
uv run python examples/nanochat/skypilot_ssh_smoke.py \
  --pool rtx3090 \
  --accelerators RTX3090:1 \
  --print-yaml
```

Run without `--print-yaml` from a prepared worktree to launch the same evaluator
contract through `SkyPilotAdapter`:

```bash
uv run python examples/nanochat/skypilot_ssh_smoke.py \
  --pool rtx3090 \
  --accelerators RTX3090:1 \
  --worktree /tmp/autoresearch
```

## Optional local Kubernetes smoke

After `sky local up`, inspect the Kubernetes task:

```bash
uv sync --group sky
uv run python examples/nanochat/skypilot_local_k8s_smoke.py --print-yaml
```

Then run it from the prepared worktree if the local cluster has the required
runtime and, for GPU checks, GPU device setup:

```bash
uv run python examples/nanochat/skypilot_local_k8s_smoke.py --worktree /tmp/autoresearch
```

**Comparability:** pin a single GPU class **or** switch from a wall-clock budget
to a deterministic compute budget (fixed steps/tokens), so results are
comparable. See [`../../docs/concepts/eval-first.md`](../../docs/concepts/eval-first.md).

See [`../../docs/human/testing-strategy.md`](../../docs/human/testing-strategy.md)
for the release gates and SkyPilot path ordering.

Upstream reference: Karpathy's `autoresearch` (MIT).
