# Contributing to Talos

Talos is early and the design is still moving, so issues, critiques, and
discussion are at least as valuable as code right now.

## Where things live
- **Concepts** (`docs/concepts/`) — the mental model: the ratchet paradigm, the
  eval-first principle, the discover → reproduce → graft → validate workflow.
- **Survey** (`docs/survey/`) — the landscape research, by topic.
- **Architecture** (`ARCHITECTURE.md`) — the layered design (L0–L3).
- **Roadmap** (`ROADMAP.md`) — what we are building and in what order.
- **Provenance** (`docs/zh/research/`) — the original research reports.

## Ground rules that matter here
Talos is a framework for running agent-written experiments. A few principles are
non-negotiable and are spelled out in [`AGENTS.md`](./AGENTS.md):
- The **evaluator is immutable** during an experiment lineage.
- Every primary metric needs a **guardrail / hard-constraint veto**.
- **Safety-critical** changes require human review.

## PR conventions
- Title: `<type>(<scope>): <description>` with type in
  `{feat, fix, docs, refactor, chore, test}`.
- Keep each PR to a single concern.
- PR description: a short **What** and **Why**.

## License
By contributing you agree your contributions are licensed under the MIT License
(see `LICENSE`).
