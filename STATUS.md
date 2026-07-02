# Status

**Current state:** Phase 0-1 are implemented and verified on CPU; Phase 2-3 are
v0 scaffolds, documented but not yet verified end-to-end.

**Next:** See `ROADMAP.md`. The real Phase 0 for a production direction is
building that domain's frozen closed-loop evaluator.

**Blockers:** no current repository blocker for the CPU reference path. GPU
demo, SkyPilot execution, and production domain evaluators need external
hardware, cloud, or domain-specific evaluator work.

## Supported local checks

```bash
uv sync
uv run python examples/ratchet_demo/run_demo.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest
```

Fresh clones or worktrees should enable the repo hook with
`git config core.hooksPath .githooks` so `.venv` stays synced from `uv.lock`
after checkout.

## Implemented & verified
- **Phase 0** — L2 eval contract (`src/talos/contract.py`) + a frozen, pure-Python
  reference evaluator (`constraints/examples/toy_mlp/`).
- **Phase 1** — the keep/revert ratchet (`src/talos/ratchet.py`), the `local`
  subprocess adapter (`src/talos/adapters/local.py`), the git+TSV ledger
  (`src/talos/ledger.py`), the `ratchet-experiment` skill, a runnable CPU demo
  (`examples/ratchet_demo/`), clean-worktree safeguards, a default iteration cap,
  and end-to-end tests (`tests/`). Verified on CPU.

## Scaffolded (v0 — NOT yet verified)
- **Phase 2** — `distill-paper`, `repro-harness`, `graft-change` skill runbooks
  (`agent-skill/`) and the `SkyPilotAdapter` scaffold
  (`src/talos/adapters/skypilot.py`). Runbooks are reviewable; their end-to-end
  behavior is unverified (they depend on a real codebase / evaluator / cloud).
- **Phase 3** — `escalate` and `attribute` skill runbooks (`agent-skill/`) and a
  parallel/factorial-grid orchestration scaffold (`src/talos/orchestration.py`;
  `factorial_grid` is a real helper, `run_grid` is an unverified scaffold).

## Not yet runnable here
- The GPU reference demo (`examples/nanochat/`) — needs a GPU.
- Production domain evaluators — each sub-team writes its own under `constraints/`.

## Git / ledger scope

Talos is the control repo. Real experiment commits, ledgers, and `.talos/runs/`
artifacts should live in the target experiment repo or isolated git worktree
passed to `run_ratchet`, not in this repository except for Talos development and
the tiny reference demos.
