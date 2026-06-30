# Survey: safety & governance for agent-written code

AutoResearch means letting an agent write and execute training/eval code
autonomously. Two concerns: **isolation** (untrusted code) and **integrity**
(don't let the loop cheat or ship something unsafe).

## Sandboxing (isolation)
Standard Docker/runc is insufficient for genuinely untrusted code. Options:

| Tool | Isolation | Notes |
| --- | --- | --- |
| **SkyPilot Sandboxes** | your own k8s | BYOC, fast launches, ~4–10× cheaper than hosted; pairs with our `skypilot` adapter |
| **E2B** | Firecracker microVMs | hardware-level isolation; widely used; good for GPU passthrough |
| **Modal Sandboxes** | gVisor | simple API; managed (not BYOC) |
| **Daytona** | gVisor | blocks GPU passthrough |

For GPU workloads on your own infra, SkyPilot Sandboxes (BYOC) or E2B
(Firecracker) are the natural fits. Sandboxing wraps the **L0** layer.

## Integrity (don't let the loop cheat or ship unsafe changes)
- **Immutable evaluator.** The agent structurally cannot edit the yardstick
  during a lineage.
- **Guardrail metrics + hard-constraint vetoes.** Every primary metric is paired
  with a check that breaks if it is gamed; safety violations zero the score.
- **Branch-namespace isolation.** All experiments on a dedicated branch prefix;
  agents don't cross into each other's namespace.
- **Human-review checkpoints.** Anything touching safety-critical
  planners/controllers is candidate evidence, reviewed before merge — never
  shipped autonomously.
- **Result-fabrication guards.** Append-only ledger + fresh-container re-runs +
  seed-noise credibility gates so a result can't be faked or be a lucky fluke.

See [`../../AGENTS.md`](../../AGENTS.md) for these as enforced rules and
[`../pitfalls.md`](../pitfalls.md) for a concrete gaming example.
