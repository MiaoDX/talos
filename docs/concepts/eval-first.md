# Eval-first: the metric is the precondition

If you remember one thing about Talos: **build the evaluator before the loop.**
Every autonomous system surveyed has its ceiling set by its metric, and in
robotics/driving the metric is the hard part.

## What a good AutoResearch metric looks like
Fast, deterministic, scalar-izable, and hard to game — with hard-constraint
vetoes. Karpathy's `val_bpb` is the gold standard *because* it is a cheap,
single-number forward pass. Your closed-loop driving/robotics metric is, by
default, none of those — which is exactly the work.

## Four hard problems (and how mature benchmarks handle them)

### 1. The eval becomes the bottleneck
When the agent proposes experiments far faster than a human could, throughput and
trustworthiness of the evaluator gate progress — not idea generation. This is the
core reason to invest in the harness first.

### 2. Comparability across heterogeneous hardware
A fixed *wall-clock* budget is only comparable on one machine; on faster GPUs the
same config gets more steps and a different score. **Pin a hardware class, or use
a deterministic compute budget** (fixed steps / tokens / FLOPs / scenarios). For
closed-loop sim, fix the scenario set and seeds, not the clock.

### 3. Goodhart's law (gaming)
A single scalar invites the agent to satisfy the *number* rather than the
*intent*. The antidotes are structural:
- the evaluator is **immutable** to the agent;
- every primary metric is paired with a **guardrail** that breaks if the metric
  is gamed (a metric *tree*, not a flat number);
- where gaming is plausible, add probes/checks — and assume even probes can be
  gamed (defense in depth). See [`../pitfalls.md`](../pitfalls.md) for a concrete
  case.

### 4. Multi-objective → one scalar
Driving and robotics are inherently multi-objective (safety / comfort /
efficiency / progress). The pattern from mature benchmarks:
**multiplicative gates for hard constraints, weighted sum for soft objectives** —
e.g., a collision or off-road event *zeroes* the score regardless of comfort,
while progress and smoothness are weighted and summed. Watch for *multi-objective
collapse*, where one term dominates and the rest stop mattering.

## Reproducibility
Fix seeds and log them in the ledger. Treat run-to-run noise as the significance
bar: a single favorable rollout is not a robust gain. Run multiple seeds; require
improvement beyond measured noise before keeping a change.

## Avoiding saturation
Static eval sets get overfit when reused across hundreds of experiments. Rotate /
evolve held-out sets; consider seed-noise credibility gates that certify a result
against the task's own measured variance before keeping it.

## Where this lives in Talos
The eval contract is **L2** ([`../../ARCHITECTURE.md`](../../ARCHITECTURE.md)),
and domain scorers plug in under [`../../constraints/`](../../constraints/).
