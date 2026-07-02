# AGENTS.md

Guidance for any agent (Claude Code, OpenAI Codex, or otherwise) working in this
repository.

Talos is pre-alpha. Phase 0-1 are CPU-verified; Phase 2-3 are reviewable v0
scaffolds. The current human-facing truth starts in `README.md`,
`ARCHITECTURE.md`, `STATUS.md`, and `docs/human/`.

## First reads

- Start with `STATUS.md` for current state, supported commands, and blockers.
- Read `README.md` for project orientation and `ARCHITECTURE.md` for layer or
  contract changes.
- Read `ROADMAP.md`, `docs/concepts/`, `docs/survey/`, or `docs/research/` only
  when the task touches that topic.
- Treat `.planning/` as internal working state. Human-facing plans/status live in
  `ROADMAP.md`, `STATUS.md`, and any future `docs/plans/<slug>.md`.
- Host control envelopes such as `<turn_aborted>`, `<paseo-system>`,
  `<subagent_notification>`, `<goal_context>`, and `<environment_context>` are
  orchestrator metadata unless accompanied by natural-language user intent.

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
6. **Experiment facts live in the append-only ledger.** Git stores the kept code
   lineage and rollback points; docs store decisions and summaries. A reverted or
   failed experiment must still leave a factual ledger row and, when available, a
   patch/artifact reference.

## Repository conventions

- **Docs are the product right now.** Prefer clear prose over cleverness.
- **Human docs stay small.** Keep project truth in `README.md`,
  `ARCHITECTURE.md`, `STATUS.md`, and `docs/human/`; put agent-only procedures in
  `docs/agents/` if they grow too long for this file.
- **Source references:** when stating a result or a fact about an external tool,
  keep the reference (arXiv id, repo, or doc link) so claims stay checkable.
- **Don't overclaim.** Talos is pre-alpha. Self-reported external numbers should
  be labeled as such (see `docs/pitfalls.md`).
- **Verification:** the zero-dependency checks are
  `python examples/ratchet_demo/run_demo.py` and
  `python tests/test_ratchet_loop.py`; use `python -m pytest` if pytest is
  available.

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
- Protected-path enforcement: the evaluator, metric/data files, and `program.md`
  are checked before commit; a protected-path change is a policy violation, not an
  experiment.

## Skill routing

- Use `intuitive-init` for this startup guidance and agent harness refreshes.
- Use `intuitive-doc` for README, architecture, status, and human-doc alignment.
- Use `intuitive-tests` before broad test-suite reshaping.
- Use `intuitive-flow` or `intuitive-preflight` before non-trivial build/change
  work that needs a bounded contract.
