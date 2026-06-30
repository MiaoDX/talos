# Survey: agent orchestration & skills (L3)

Talos packages its loop as portable **Agent Skills** — the `SKILL.md` convention
(YAML frontmatter `name` + `description`, plus a markdown body and optional
`scripts/` / `references/`) adopted across Claude Code, OpenAI Codex, and others.

## Authoring guidance
- For cross-client portability, keep to the portable core (name, description,
  plain markdown). Claude reads `.claude/skills/`; Codex reads `~/.codex/skills/`.
- Keep the body concise — it is a recurring token cost; push detail to
  `references/`. Skills are loaded lazily (progressive disclosure).
- Skills are *model-invoked* (auto-selected by description match) or *user-invoked*
  (`/skill-name`).

## Patterns worth stealing (from the ecosystem)
- **Router + commands.** One small `SKILL.md` router that dispatches to per-command
  files keeps tokens low (a community `autoresearch` skill refactored an
  800+ line monolith into a ~40-line router + command files, a ~95% reduction).
- **Resume + lessons-across-runs.** Persist what was tried and learned so a fresh
  run continues rather than repeats (codex-autoresearch).
- **Compute as a skill.** SkyPilot's agent skill lets the agent request GPUs — the
  template for our L0 adapter being agent-drivable.

## Bounded-autonomy rules (bake into every skill)
- a default iteration cap + a time/compute budget (never an unbounded loop);
- crash recovery: fix a few times, else revert and log `status=crash`;
- git-as-memory: read state + history + ledger before each step;
- a three-state self-assessment per experiment — **keep / discard / crash**;
- explicit out-of-scope file protection so the agent does not wander.

## Parallel / multi-experiment orchestration
Sequential runs = greedy hill-climbing. Parallelism enables **factorial grids**
(e.g., sweep several variants in one wave) that catch interaction effects a greedy
loop misses; expect a two-tier "screen on cheap hardware, confirm on fast"
strategy. Watch for noisy-neighbor variance — only trust results whose stddev is
small relative to the effect. (Lessons from the SkyPilot 16-GPU parallel
`autoresearch` run.)

## The four Talos skills
`distill-paper` · `repro-harness` · `graft-change` · `ratchet-experiment` — see
[`../../agent-skill/`](../../agent-skill/) and
[`../concepts/workflow.md`](../concepts/workflow.md).
