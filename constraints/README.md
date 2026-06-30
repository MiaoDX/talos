# constraints/ — the eval / veto contract (L2)

> **Placeholder.** Talos is pre-alpha; this directory currently documents the
> intended design. No implementations yet.

This is the layer that makes Talos eval-driven and domain-transferable. A
**constraint set** for a domain is a *frozen* scorer: given an experiment's
artifact, it returns a single scalar plus hard-constraint vetoes.

## The contract (intended)
```
evaluate(artifact) -> {
    scalar:  float,            # the one number the ratchet optimizes (lower- or higher-is-better)
    vetoes:  list[Veto],       # hard constraints; any triggered veto zeroes/disqualifies the result
    metrics: dict,             # sub-metrics for attribution / dashboards (not optimized directly)
    seeds:   list[int],        # seeds used (logged to the ledger)
}
```

## Rules (see ../AGENTS.md)
- **Immutable during a lineage** — the agent cannot edit a constraint set to move
  a number.
- **Multi-objective → scalar + vetoes** — multiplicative gates for hard
  constraints (e.g., collision/off-road/unsafe-contact → veto), weighted sum for
  soft objectives (progress, comfort, efficiency).
- **Deterministic + seeded** — same input, same score; report across seeds.

## Domain adapters (planned, illustrative)
- `driving/` — wrap a closed-loop simulator (CARLA / nuPlan-R / Waymax / …).
- `manipulation/` — success rate over a task suite (ManiSkill / RoboCasa / …).
- `locomotion/` — task reward + stability/safety vetoes (Isaac Lab / MuJoCo / …).

These are examples; each sub-team writes the scorer that reflects its own
production reality. See [`../docs/concepts/eval-first.md`](../docs/concepts/eval-first.md)
and [`../docs/survey/eval-ecosystems.md`](../docs/survey/eval-ecosystems.md).
