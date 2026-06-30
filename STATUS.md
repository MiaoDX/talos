# Status

**Early. Phase 0–1 are implemented and verified on CPU; Phase 2–3 are v0 scaffolds
(documented but not yet verified).**

## Implemented & verified
- **Phase 0** — L2 eval contract (`src/talos/contract.py`) + a frozen, pure-Python
  reference evaluator (`constraints/examples/toy_mlp/`).
- **Phase 1** — the keep/revert ratchet (`src/talos/ratchet.py`), the `local`
  subprocess adapter (`src/talos/adapters/local.py`), the git+TSV ledger
  (`src/talos/ledger.py`), the `ratchet-experiment` skill, a runnable CPU demo
  (`examples/ratchet_demo/`), and an end-to-end test (`tests/`). Verified on CPU.

## Scaffolded (v0 — NOT yet verified)
- **Phase 2** — `distill-paper`, `repro-harness`, `graft-change` skill runbooks
  (`agent-skill/`) and the `SkyPilotAdapter` scaffold
  (`src/talos/adapters/skypilot.py`). Runbooks are reviewable; their end-to-end
  behavior is unverified (they depend on a real codebase / evaluator / cloud).
- Phase 3 scaffolds land next.

## Not yet runnable here
- The GPU reference demo (`examples/nanochat/`) — needs a GPU.
- Production domain evaluators — each sub-team writes its own under `constraints/`.

## Next
See `ROADMAP.md`. The real Phase 0 for a given direction is building *that domain's*
closed-loop evaluator.
