# constraints/ — the eval / veto contract (L2)

This is the layer that makes Talos eval-driven and domain-transferable. A
**constraint set** for a domain is a *frozen* evaluator: given an experiment's
artifact, it returns one scalar plus hard-constraint vetoes.

## The contract
The typed view lives in [`../src/talos/contract.py`](../src/talos/contract.py)
(`EvalResult`, `Veto`, `is_improvement`). The wire format is JSON on stdout, so an
evaluator can be written in any language:

```json
{"scalar": 0.47, "vetoes": [{"name": "divergence", "triggered": false, "detail": ""}],
 "metrics": {"val_logloss": 0.47}, "seeds": [0], "lower_is_better": true}
```

## Rules (see ../AGENTS.md)
- **Immutable during a lineage** — the agent cannot edit the evaluator to move a number.
- **Multi-objective → scalar + vetoes** — multiplicative gates for hard constraints
  (collision / off-road / unsafe-contact → veto), weighted sum for soft objectives
  (`weighted_score` helper).
- **Deterministic + seeded** — same input, same score; report across seeds.

## Reference example
[`examples/toy_mlp/`](./examples/toy_mlp/) is a tiny, CPU-only, seconds-to-run
evaluator implementing the contract:
- `evaluator.py` — **frozen**; owns the dataset, the train/val split, and the metric
  (validation log-loss, lower-is-better); vetoes non-finite predictions / crashes.
- `solution.py` — the **agent-editable** file (the sandbox).
- `program.md` — the human-owned spec.

It is the task the Phase-1 ratchet demo drives (see [`../examples/ratchet_demo/`](../examples/ratchet_demo/)).

## Domain adapters (planned, illustrative)
- `driving/` — wrap a closed-loop simulator (CARLA / nuPlan-R / Waymax / …).
- `manipulation/` — success rate over a task suite (ManiSkill / RoboCasa / …).
- `locomotion/` — task reward + stability/safety vetoes (Isaac Lab / MuJoCo / …).

Each sub-team writes the scorer that reflects its own production reality. See
[`../docs/concepts/eval-first.md`](../docs/concepts/eval-first.md) and
[`../docs/survey/eval-ecosystems.md`](../docs/survey/eval-ecosystems.md).
