# Survey: eval ecosystems (illustrative, per domain)

Talos is domain-transferable: a new domain = a new **L2 eval adapter**, not a new
core. This page lists *illustrative* closed-loop eval ecosystems for our first two
domains. **It is deliberately not prescriptive** — each sub-team knows its own
direction and should write the scorer that reflects its production reality. Treat
these as prompts, and as worked examples of how to fold a domain into a single
scalar + hard-constraint vetoes.

## The principle that crosses domains
- **Open-loop** eval (compare a prediction to logged ground truth) is cheap and
  parallel but blind to compounding error and self-correction.
- **Closed-loop** eval (the policy acts and the world reacts) is the real signal
  but expensive and stochastic.
- Mature benchmarks turn multi-objective outcomes into one number with
  **multiplicative gates for hard constraints × weighted sum for soft objectives**
  (a collision/off-road event zeroes the score; progress/comfort are weighted).

## Robotics (illustrative)
- **Isaac Sim / Isaac Lab** — massively parallel GPU simulation for robot
  learning; where reward-design loops like Eureka run. (Newer eval harnesses such
  as Isaac Lab-Arena aim to cut eval from days to under an hour.)
- **MuJoCo / MJX** — fast, widely-used physics; JAX-accelerated variant for
  parallel rollouts.
- **ManiSkill**, **RoboCasa**, **LIBERO** — manipulation task suites with success
  rates as natural scalars.
- **Genesis**, **Genie Sim** — newer generative/large-scale simulation efforts.
- Typical scalar: `success_rate` over a fixed task suite + seeds; vetoes for
  unsafe contacts or constraint violations.

## Autonomous driving (illustrative)
- **CARLA** — sensor-based closed-loop with reactive traffic (the official
  leaderboard is heavy — hundreds of routes take days, so ablate on a small
  subset).
- **nuPlan / nuPlan-R** — planning-centric, real-log-based; reactive variant adds
  learning-based agents and success/pass-rate metrics.
- **Waymax** — GPU-accelerated, log-based closed-loop.
- **NAVSIM / NAVSIM v2** — *pseudo-closed-loop* (open-loop setting + pre-computed
  perturbations); a good cost/fidelity compromise for fast iteration.
- **Bench2Drive**, **MetaDrive** — multi-ability CARLA-based suite; lightweight
  reactive sim.
- Typical scalar: a driving/closed-loop score that *multiplies* in hard-constraint
  penalties (collision, off-road, wrong-direction) and *weights* soft terms
  (progress, comfort, time-to-collision).

## How this plugs into Talos
A domain adapter lives under [`../../constraints/`](../../constraints/) and
implements the L2 contract: `evaluate(artifact) -> { scalar, vetoes, metrics }`,
frozen and seed-controlled. See [`../concepts/eval-first.md`](../concepts/eval-first.md).
