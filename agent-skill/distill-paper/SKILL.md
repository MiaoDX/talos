---
name: distill-paper
description: >-
  Read a paper or product writeup (and its key references) and distill it into a
  structured, implementable spec: the core mechanism, the claimed metric, a minimal
  reproduction, and the constraints. Use at the start of adopting a community idea,
  before reproducing or grafting it.
---

> **Status: v0 scaffold — unverified.** This runbook's end-to-end behavior has not
> been validated end-to-end in this repo; it will be hardened against real papers.
> See [`../../STATUS.md`](../../STATUS.md).

# distill-paper

Turn "I saw an idea in a paper/product" into a spec you can act on — the analog of
`program.md`.

## Steps
1. **Read with a subagent** so heavy reading stays out of the main context.
2. **Follow the lineage.** Pull the most relevant cited references (and their repos)
   to recover *implicit* conventions the paper omits (the AutoReproduce idea).
3. **Extract**:
   - the **core mechanism** (what actually changes and why it should help);
   - the **claimed metric** and dataset/benchmark;
   - a **minimal reproduction** (smallest setting that should show the effect);
   - the **constraints / assumptions** (compute, data, preconditions);
   - **risks** (what the authors gloss over; overfitting, cherry-picked baselines).
4. **Emit a structured spec** (Markdown) with those sections.

## Output
A spec file that downstream skills consume: `repro-harness` (to confirm) and
`graft-change` (to integrate). Keep claims sourced (links/arXiv ids) so they stay
checkable.

## Notes
- Distinguish the *idea* from the paper's *framing*; you want the transferable
  mechanism, not the narrative.
- Flag any number you could not verify rather than restating it as fact.
