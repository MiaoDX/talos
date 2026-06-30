# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- **Phase 3 (v0, unverified)** — `escalate` (route safety-critical diffs to
  human review; switch search strategy on plateau) and `attribute` (ablation +
  multi-seed confirmation) skill runbooks, plus `src/talos/orchestration.py`
  (`factorial_grid` tested; `run_grid` an unverified scaffold).
- **Phase 2 (v0, unverified)** — `distill-paper` / `repro-harness` /
  `graft-change` skill runbooks and a `SkyPilotAdapter` scaffold
  (`src/talos/adapters/skypilot.py`). Documented and reviewable; not yet run
  end-to-end (no cloud/codebase in CI).
- **Phase 1** — the keep/revert ratchet engine (`src/talos/ratchet.py`), the
  `local` subprocess adapter (`src/talos/adapters/local.py`, budget-bounded), the
  git+TSV append-only ledger (`src/talos/ledger.py`), the `ratchet-experiment`
  skill, a runnable CPU demo (`examples/ratchet_demo/`), the GPU reference doc
  (`examples/nanochat/`), and an end-to-end test (`tests/test_ratchet_loop.py`).
- **Phase 0** — the L2 eval contract (`src/talos/contract.py`: `EvalResult`,
  `Veto`, `is_improvement`) and a runnable, pure-Python reference evaluator
  (`constraints/examples/toy_mlp/`: frozen `evaluator.py`, agent-editable
  `solution.py`, `program.md`).
- Initial repository scaffold: README, ARCHITECTURE, ROADMAP, STATUS.
- Concept docs (`docs/concepts/`): the AutoResearch ratchet paradigm, the
  eval-first principle, and the distill → reproduce → graft → validate workflow.
- Survey docs (`docs/survey/`): compute backends, experiment ledger, agent
  skills, safety & sandboxing, eval ecosystems (AD + robotics), and the
  competitive landscape — the deep research reorganized by topic.
- `docs/pitfalls.md`: structural failure modes and anti-patterns.
- Full deep-research reports (English) under `docs/research/`.
- Placeholder contracts: `constraints/` (L2 eval/veto contract) and
  `agent-skill/` (the four planned skills).

> Talos is **pre-alpha**: the methodology and design are documented; the skills
> and adapters are not yet implemented. See `STATUS.md` and `ROADMAP.md`.
