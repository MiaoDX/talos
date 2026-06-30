# Status

**Stage: pre-alpha (documentation-first).**

Talos today is a *design + methodology* repository, not yet a runnable tool. We
are publishing the thinking before the code so the architecture can be reviewed
and discussed in the open.

## What exists now
- A clear thesis and architecture (`README.md`, `ARCHITECTURE.md`).
- The deep research that informs the design, reorganized by topic
  (`docs/concepts/`, `docs/survey/`), with the original reports archived under
  `docs/zh/research/`.
- A phased adoption plan (`ROADMAP.md`).
- Contract placeholders for the eval layer (`constraints/`) and the agent skills
  (`agent-skill/`).

## What does NOT exist yet
- Working `agent-skill/` implementations (`distill-paper`, `repro-harness`,
  `graft-change`, `ratchet-experiment`).
- Reference execution adapters (`local`, `skypilot`).
- A runnable end-to-end demo.

## Next
See `ROADMAP.md`. The first milestone (Phase 0) is **building an evaluator**,
not writing a skill — the evaluator is the precondition for everything else.
