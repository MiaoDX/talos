# Talos

**An eval-driven, domain-transferable AutoResearch framework — delivered as skills for coding agents.**

> *Talos was the bronze automaton that tirelessly walked the shores of Crete. This Talos tirelessly runs your experiments while you sleep — and only keeps the ones the evaluator says are better.*

[Architecture](./ARCHITECTURE.md) · [Roadmap](./ROADMAP.md) · [Status](./STATUS.md) · [Human docs](./docs/human/README.md)

---

## The idea in one line

A coding agent's ceiling is set by its **harness**, not the model:

```
coding agent = AI model(s) + harness
```

For software, the harness is mature (run tests, read the diff, iterate). For
**research-style work — "I saw an idea in a paper/product; does it actually help
*our* system?"** — the harness has been missing. "AutoResearch" is that harness:
a disciplined loop that proposes a change, runs a bounded experiment, scores it
against a frozen metric, and **keeps it only if it's better** (otherwise reverts).

Talos packages this loop as portable **skills for Claude Code and OpenAI Codex**,
built to be **eval-driven first** and **easy to move across domains**. Autonomous
driving and robotics are our first two instantiations; nothing in the core is
specific to either.

## Why another repo? (what Talos is and is not)

The AutoResearch ecosystem already has the paradigm (Karpathy's
[`autoresearch`](https://github.com/karpathy/autoresearch)), the compute
substrate ([SkyPilot](https://github.com/skypilot-org/skypilot)), and many
single-file forks. Talos does **not** reinvent any of that. Its bet is on the
two things nobody has packaged well:

1. **Grafting a community idea into an *existing* large codebase** — not
   generating a fresh `train.py` from scratch.
2. **A domain-pluggable, hard-to-game *evaluation* contract** — because in
   robotics and driving the metric (closed-loop simulation, multi-objective,
   safety-gated) is the hard part, and it is the precondition for any autonomy.

Talos is **a thin methodology layer + a set of agent skills**, not a platform.
Compute, experiment tracking, and sandboxing are **reused** from existing tools.

This repository is the **control repo**: it contains the Talos method, reference
engine, skills, docs, and tiny demos. Real experiment git history, ledgers, and
`.talos/runs/` artifacts belong in the **target experiment worktree** passed to
`run_ratchet`, not in this repo except when developing Talos itself.

## The workflow it supports

```
discover & distill  →  reproduce / confirm  →  graft into our framework  →  validate by experiment
   (read a paper)        (does it work?)         (our existing codebase)        (keep/revert loop)
```

Each stage is (will be) a skill: `distill-paper`, `repro-harness`,
`graft-change`, `ratchet-experiment`. See [`agent-skill/`](./agent-skill/).

## Architecture at a glance

Four loosely-coupled, individually swappable layers (full detail in
[`ARCHITECTURE.md`](./ARCHITECTURE.md)):

| Layer | What | Build or reuse |
| --- | --- | --- |
| **L0** Execution contract + adapters | submit an experiment → get a scalar + artifacts | thin contract (ours) + `local` and `skypilot` adapters (reuse) |
| **L1** Ledger contract | append-only experiment record = the agent's memory + audit trail | git + TSV (default); MLflow/Aim behind the contract |
| **L2** Eval contract | a frozen scorer returning one scalar + hard-constraint vetoes | **ours to define; domain adapters plug in here** ([`constraints/`](./constraints/)) |
| **L3** Agent skills | the loop, packaged for Claude Code / Codex | **the product** ([`agent-skill/`](./agent-skill/)) |

## Status

**Pre-alpha. Phase 0–1 are implemented and CPU-verified; Phase 2–3 are reviewable
v0 surfaces.** A short local RTX 3090 nanochat smoke is recorded, and the
SkyPilot SSH path has a same-host RTX 3090 smoke. Overnight GPU improvement
evidence is not recorded yet. Talos is no longer documentation-only, but it is
not yet a production platform.

Implemented and verified now:

- **Phase 0:** L2 eval contract (`src/talos/contract.py`) plus the pure-Python
  `toy_mlp` reference evaluator under `constraints/examples/toy_mlp/`.
- **Phase 1:** the keep/revert ratchet (`src/talos/ratchet.py`), local subprocess
  adapter, git+TSV append-only ledger, `ratchet-experiment` skill, runnable CPU
  demo, clean-worktree safeguards, a default iteration cap, and end-to-end tests.

Scaffolded / partially verified:

- **Phase 2:** `distill-paper`, `repro-harness`, `graft-change`, and the
  `SkyPilotAdapter` task/result path. The SSH GPU smoke is recorded; broader
  Kubernetes/cloud execution remains manual/future evidence.
- **Phase 3:** `escalate`, `attribute`, and parallel/grid orchestration scaffolds.

The first real milestone for any production direction remains **building that
specific domain's frozen evaluator**. See [`STATUS.md`](./STATUS.md) and
[`ROADMAP.md`](./ROADMAP.md).

## Documentation

- **Current orientation** — [`STATUS.md`](./STATUS.md),
  [`ARCHITECTURE.md`](./ARCHITECTURE.md), [`ROADMAP.md`](./ROADMAP.md),
  [`docs/human/README.md`](./docs/human/README.md)
- **Architecture lessons** — [`docs/human/executor-lessons.md`](./docs/human/executor-lessons.md)
- **Concepts** — [`docs/concepts/paradigm.md`](./docs/concepts/paradigm.md),
  [`eval-first.md`](./docs/concepts/eval-first.md),
  [`workflow.md`](./docs/concepts/workflow.md)
- **Survey (the research, by topic)** —
  [`compute-backends`](./docs/survey/compute-backends.md),
  [`experiment-ledger`](./docs/survey/experiment-ledger.md),
  [`agent-skills`](./docs/survey/agent-skills.md),
  [`safety-sandboxing`](./docs/survey/safety-sandboxing.md),
  [`eval-ecosystems`](./docs/survey/eval-ecosystems.md),
  [`landscape`](./docs/survey/landscape.md)
- **Pitfalls** — [`docs/pitfalls.md`](./docs/pitfalls.md)
- **Deep research (full reports)** — [`docs/research/`](./docs/research/)

## Run locally

Talos is managed with [uv](https://docs.astral.sh/uv/). The reference runtime is
still zero-dependency, but the locked dev environment includes pytest.

```bash
uv sync
uv run python examples/ratchet_demo/run_demo.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest
```

For fresh clones or git worktrees, enable the checked-in environment hook once:

```bash
git config core.hooksPath .githooks
```

SkyPilot is intentionally optional so the reference core stays lightweight. To
install the SkyPilot CLI for SSH/Kubernetes smoke tests:

```bash
uv sync --group sky
uv run --group sky sky --version
```

## Acknowledgements

Talos stands on the shoulders of the open AutoResearch ecosystem — most directly
Andrej Karpathy's `autoresearch`, SkyPilot, and the broader work surveyed in
[`docs/survey/landscape.md`](./docs/survey/landscape.md).

## License

[MIT](./LICENSE).
