# AGENTS.md

Guidance for any agent (Claude Code, OpenAI Codex, or otherwise) working in this
repository. Humans should read this too — it encodes the principles Talos is
built on.

> While Talos is documentation-first, most work here is writing and refining
> docs. The rules below also define how the *skills we are building* must behave
> once implemented.

## Non-negotiable principles

These exist because an autonomous keep/revert loop is only as safe and useful as
its evaluator and its guardrails. Violating them silently corrupts results.

1. **The evaluator is immutable during an experiment lineage.** No agent (and no
   human, mid-run) may edit the scorer, the metric, or the eval data to make a
   number move. If you find yourself wanting to change the yardstick, stop — that
   is a separate, reviewed change, not part of an experiment.
2. **Every primary metric has a guardrail.** A single scalar invites gaming
   (Goodhart). Pair it with hard-constraint vetoes (e.g., a safety violation
   zeroes the score regardless of the headline metric). Never optimize a metric
   that can be satisfied by cheating.
3. **Safety-critical changes require human review.** Anything touching a
   safety-relevant planner/controller is *candidate evidence*, never
   ship-ready. Flag it; do not merge it autonomously.
4. **Keep/revert is honest.** Commit before you verify; if a change does not
   improve the frozen metric beyond measured noise, revert it. Do not "massage"
   a result, fabricate a number, or report partial work as complete.
5. **Results must be reproducible.** Fix and log seeds. Treat run-to-run noise as
   the significance bar — one lucky run is not an improvement.

## Repository conventions

- **Docs are the product right now.** Prefer clear prose over cleverness.
- **Source references:** when stating a result or a fact about an external tool,
  keep the reference (arXiv id, repo, or doc link) so claims stay checkable.
- **Don't overclaim.** Talos is pre-alpha. Self-reported external numbers should
  be labeled as such (see `docs/pitfalls.md`).

## Branch & commit conventions

- Branch names: `feat/...`, `fix/...`, `docs/...`, `chore/...`. Do not reuse
  another agent's branch namespace.
- Commit/PR titles: `<type>(<scope>): <description>`.
- One concern per PR; PR body has a short **What** and **Why**.
- Trailer on agent-authored commits:
  ```
  🤖 Generated with Claude Code
  Co-Authored-By: Claude <noreply@anthropic.com>
  ```

## When implementing skills (Phase 1+)

- Bounded autonomy: a default iteration cap and a time/compute budget; never an
  unbounded loop.
- Crash recovery: on a failed run, attempt a fix a few times, else revert and log
  `status=crash` — do not stall waiting for a human.
- Git-as-memory: read state + history + the ledger before each step.
- Three-state self-assessment per experiment: **keep / discard / crash**.
