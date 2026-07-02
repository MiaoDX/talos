# agent-skill/ — the Talos skills (L3)

Skills are portable `SKILL.md` packages for Claude Code and OpenAI Codex. They map
one-to-one onto the workflow ([`../docs/concepts/workflow.md`](../docs/concepts/workflow.md)).

| Skill | Stage | Status |
| --- | --- | --- |
| [`ratchet-experiment`](./ratchet-experiment/SKILL.md) | validate | **implemented (Phase 1)** — keep/revert loop; runnable CPU demo |
| [`distill-paper`](./distill-paper/SKILL.md) | discover & distill | **v0 scaffold (Phase 2, unverified)** |
| [`repro-harness`](./repro-harness/SKILL.md) | reproduce / confirm | **v0 scaffold (Phase 2, unverified)** |
| [`graft-change`](./graft-change/SKILL.md) | graft | **v0 scaffold (Phase 2, unverified)** |
| [`escalate`](./escalate/SKILL.md) / [`attribute`](./attribute/SKILL.md) | escalation / attribution | **v0 scaffold (Phase 3, unverified)** |

`ratchet-experiment` is backed by a verified reference implementation
([`../src/talos/ratchet.py`](../src/talos/ratchet.py)) and a runnable demo
([`../examples/ratchet_demo/`](../examples/ratchet_demo/)). The v0 scaffolds are
runbooks whose end-to-end behavior is **not yet verified** (they depend on a real
codebase / evaluator); they will be hardened once a domain Phase-0 evaluator exists.

## Conventions (see ../AGENTS.md)
- Bounded autonomy: default iteration cap + time/compute budget.
- Git/ledger state belongs in the target experiment worktree, not the Talos
  control repo except when developing Talos itself.
- Crash recovery: production agent loops fix a few times; the reference engine
  resets and logs `status=crash`.
- Git-as-memory; three-state self-assessment (keep / discard / crash).
- Keep `SKILL.md` bodies short; push detail to `references/`.
