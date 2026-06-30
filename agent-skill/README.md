# agent-skill/ — the Talos skills (L3)

> **Placeholder.** Talos is pre-alpha; this directory documents the four planned
> skills. No implementations yet — these arrive in Phase 1+ (see
> [`../ROADMAP.md`](../ROADMAP.md)).

Skills are portable `SKILL.md` packages for Claude Code and OpenAI Codex. They map
one-to-one onto the workflow ([`../docs/concepts/workflow.md`](../docs/concepts/workflow.md)):

| Skill | Stage | What it does |
| --- | --- | --- |
| `distill-paper` | discover & distill | read a paper/product (+ key references); emit a structured spec: mechanism, claimed metric, minimal repro, constraints |
| `repro-harness` | reproduce / confirm | confirm the idea works in isolation against a frozen evaluator; guard against fabricated results |
| `graft-change` | graft | integrate the idea into the *existing* codebase behind tests; windowed edits + git-worktree isolation |
| `ratchet-experiment` | validate | the keep/revert loop: propose → bounded run → score → commit-or-revert → log; ablation for attribution; escalation when plateaued |

## Conventions (see ../AGENTS.md)
- Bounded autonomy: default iteration cap + time/compute budget.
- Crash recovery: fix a few times, else revert and log `status=crash`.
- Git-as-memory; three-state self-assessment (keep / discard / crash).
- Keep `SKILL.md` bodies short; push detail to `references/`.

## Build order
Phase 1 starts with **`ratchet-experiment`** + the `local` adapter, demonstrated
by reproducing Karpathy's nanochat `autoresearch` task on a single GPU.
