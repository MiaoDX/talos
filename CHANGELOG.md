# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- **Extensibility architecture docs** — added an architecture SVG, an explicit
  extension model, and a concise Executor lessons note that explains how Talos
  extracts the internal operator pattern without importing platform complexity.
- **Standalone testing strategy implementation** — added the nanochat evaluator
  wrapper, scripted smoke proposals, local-GPU and SkyPilot SSH runbooks, tested
  SkyPilot SSH task/result plumbing, and external evaluator hashing in the
  ledger.
- **Ratchet hardening and scope clarity** — `run_ratchet` now enforces a default
  iteration cap, requires a clean experiment worktree, cleans only untracked files
  created by failed/reverted attempts, preserves patches for untracked candidate
  files, and documents that experiment git/ledger state belongs in the target
  worktree rather than the Talos control repo.
- **Ledger/audit model hardening** — ADR 0001 separates git (kept code lineage),
  append-only ledger (raw experiment facts), and docs (human decisions/summaries).
  The ratchet now records richer ledger metadata, preserves per-run patches/results
  under `.talos/runs/`, enforces protected/editable path policy before commit, and
  logs proposal failures as `crash` rows instead of leaving ambiguous worktree state.
- **Phase 3 (v0, unverified)** — `escalate` (route safety-critical diffs to
  human review; switch search strategy on plateau) and `attribute` (ablation +
  multi-seed confirmation) skill runbooks, plus `src/talos/orchestration.py`
  (`factorial_grid` tested; `run_grid` an unverified scaffold).
- **Phase 2 (v0, partially verified)** — `distill-paper` / `repro-harness` /
  `graft-change` skill runbooks and `SkyPilotAdapter`
  (`src/talos/adapters/skypilot.py`). SSH task generation and result parsing are
  tested; real SkyPilot infrastructure execution is not yet recorded.
- **Phase 1** — the keep/revert ratchet engine (`src/talos/ratchet.py`), the
  `local` subprocess adapter (`src/talos/adapters/local.py`, budget-bounded), the
  git+TSV append-only ledger (`src/talos/ledger.py`), the `ratchet-experiment`
  skill, a runnable CPU demo (`examples/ratchet_demo/`), the GPU reference
  runbook (`examples/nanochat/`), and an end-to-end test
  (`tests/test_ratchet_loop.py`).
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

> Talos is **pre-alpha**: Phase 0–1 are implemented and CPU-verified; Phase 2–3
> are reviewable v0 surfaces. Real GPU/SkyPilot evidence is still required for a
> release or external demo. See `STATUS.md` and `ROADMAP.md`.
