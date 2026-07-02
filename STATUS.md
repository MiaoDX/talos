# Status

**Current state:** Phase 0-1 are implemented and verified on CPU; Phase 2-3 are
v0 surfaces. SkyPilot task generation/result parsing are CPU-tested, and the
SkyPilot CLI is an optional `uv` dependency group. A same-host SkyPilot SSH
smoke has run on the local RTX 3090 and returned a valid `EvalResult`.

**Next:** See `ROADMAP.md`. The real Phase 0 for a production direction is
building that domain's frozen closed-loop evaluator.

**Blockers:** no current repository blocker for the CPU reference path, local
short GPU smoke, or SkyPilot SSH GPU smoke. The release / external-demo gate
still needs overnight GPU nanochat evidence and any production domain
evaluators.

## Supported local checks

```bash
uv sync
uv run python examples/ratchet_demo/run_demo.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest
```

See [`docs/human/testing-strategy.md`](./docs/human/testing-strategy.md) for the
full standalone demo matrix. CPU checks are the default CI smoke path; the
release / external-demo gate requires overnight GPU nanochat evidence plus a
SkyPilot SSH GPU smoke against an existing GPU machine. Current release evidence,
including the short RTX 3090 nanochat smoke and same-host SkyPilot SSH smoke, is
indexed in
[`docs/human/release-evidence.md`](./docs/human/release-evidence.md).

Install optional SkyPilot tooling with `uv sync --group sky`; the default
environment intentionally does not install the SkyPilot dependency tree.

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

## Scaffolded / partial (v0)
- **Phase 2** — `distill-paper`, `repro-harness`, `graft-change` skill runbooks
  (`agent-skill/`) and `SkyPilotAdapter` (`src/talos/adapters/skypilot.py`).
  The adapter's SSH task generation and result parsing are CPU-tested; SkyPilot
  packaging is available through the optional `sky` dependency group; same-host
  SSH GPU execution is recorded in the release evidence.
- **Phase 3** — `escalate` and `attribute` skill runbooks (`agent-skill/`) and a
  parallel/factorial-grid orchestration scaffold (`src/talos/orchestration.py`;
  `factorial_grid` is a real helper, `run_grid` is an unverified scaffold).

## Not yet runnable here
- The GPU reference demo (`examples/nanochat/`) — short local RTX 3090 and
  same-host SkyPilot SSH smokes are recorded; overnight release evidence is still
  missing.
- Production domain evaluators — each sub-team writes its own under `constraints/`.

## Git / ledger scope

Talos is the control repo. Real experiment commits, ledgers, and `.talos/runs/`
artifacts should live in the target experiment repo or isolated git worktree
passed to `run_ratchet`, not in this repository except for Talos development and
the tiny reference demos.
