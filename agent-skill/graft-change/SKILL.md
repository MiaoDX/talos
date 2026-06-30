---
name: graft-change
description: >-
  Integrate a confirmed idea into an existing large codebase behind tests — the step
  generic paper-to-code tools skip. Use after repro-harness, before validating with
  ratchet-experiment.
---

> **Status: v0 scaffold — unverified.** End-to-end behavior not yet validated in
> this repo; it depends on a real target codebase. See [`../../STATUS.md`](../../STATUS.md).

# graft-change

Most "paper-to-code" tools generate a fresh repo. The hard, valuable case is
grafting a confirmed idea into your **existing** large codebase without breaking it.

## Steps
1. **Localize.** Find the minimal set of modules/functions the change touches. Use a
   subagent to explore so the main context stays clean.
2. **Plan before editing.** Propose the integration (interfaces, call sites, configs)
   and, for anything safety-relevant, get human review *before* editing.
3. **Edit with a windowed, lint-checked surface** (the ACI discipline): small, local
   edits; run linters/type checks; keep changes reversible.
4. **Isolate** the work on its own branch / git-worktree so a bad attempt is
   discardable and parallel work doesn't collide.
5. **Use the codebase's own conventions** (an org `CLAUDE.md`/conventions doc): real
   internal libraries and APIs, not invented ones.
6. **Keep tests green.** The change must pass the existing test suite plus any new
   tests for the grafted behavior.

## Output
A focused, reviewed, test-passing change on an isolated branch, ready to be validated
by [`../ratchet-experiment/SKILL.md`](../ratchet-experiment/SKILL.md) against the
domain evaluator.

## Rules (see ../../AGENTS.md)
- **Safety-critical paths are candidate evidence only** — flag for human review, never
  merge autonomously.
- Don't widen scope: graft *this* idea, don't refactor everything around it.
