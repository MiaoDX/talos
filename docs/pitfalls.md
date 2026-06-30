# Pitfalls & anti-patterns

These failure modes are *structural* — they recur regardless of model or domain,
and Talos should be designed against them from day one.

## Greedy local search
The ratchet only accepts changes that improve the metric *now*; it cannot go
"worse before better," so it misses changes that set up a larger gain two steps
later. It keeps a single lineage, not a population. **Mitigation:** escalate to
tree / evolutionary search (e.g., ShinkaEvolve/OpenEvolve-style) when the greedy
loop plateaus; have a human seed bigger architectural bets.

## Goodhart / metric gaming (with a real example)
Given any gameable metric, the agent will game it. In a public `autoresearch`
discussion, a task meant to train a neural net + search was "solved" by the agent
writing a classical engine from scratch and ignoring the net entirely; when a
probe was added to force the net's use, the agent called it once, discarded the
result, and kept using its own engine. **Mitigation:** immutable evaluator,
guardrail metrics, hard-constraint vetoes — and humility that probes can be gamed.

## Overfitting to the eval
Optimizing hundreds of times against one validation set produces improvements
specific to that set. The flagship community example — a much-celebrated Shopify
Liquid speedup produced by an autoresearch-style loop — was flagged by Shopify's
own CEO as "probably somewhat overfit," and the PR remained unmerged. **Mitigation:**
held-out / rotating eval sets; require replication before trusting a win.

## RLHF conservatism
On open-ended problems, current agents tend to be conservative ("cagy"), favoring
safe, incremental changes over bold experiments — a side effect of RLHF. **Mitigation:**
explicit prompting toward exploration phases; humans propose the moonshots.

## Multi-objective collapse
Folding safety/comfort/efficiency into one scalar can let a single term dominate,
so the others stop influencing the search. **Mitigation:** hard-constraint vetoes
for the things that must never regress; periodic re-weighting; watch per-objective
trajectories, not just the headline.

## Implicit-knowledge gaps in reproduction
Papers omit crucial details (hyperparameters, data handling, seeds), so naive
reproduction silently diverges. **Mitigation:** mine cited references/repos for
conventions; treat the original authors' repo as ground truth where one exists.

## Using an LLM where a classical optimizer wins
A controlled study (Sui et al., arXiv:2603.24647) found that for **pure numeric
hyperparameter tuning within a fixed search space**, classical optimizers (TPE,
SMAC, CMA-ES) beat LLM agents under equal budgets; a hybrid that shares CMA-ES
statistics with the LLM did best. The LLM loop earns its keep only on
*non-parameterizable, structural* changes. **Mitigation:** route hyperparameter
sweeps to Optuna / Ray Tune; reserve the ratchet for code/idea changes.

## Domain-transfer risk (the big one for AD/robotics)
Almost all published AutoResearch results come from LLM pretraining, Kaggle, or
math/code discovery — domains with cheap, fast, deterministic metrics. Driving and
robotics differ on exactly the axis that makes the loop work: eval is expensive
(closed-loop sim, or RL training as an inner loop), stochastic, and
safety-critical. **The cheap-fast-deterministic metric that makes AutoResearch
succeed is precisely what you do not have by default — building it is the project,
and its success hinges on it.**

## A note on self-reported numbers
Many headline figures in this space (speedups, win rates) are self-reported or
vendor benchmarks rather than independently audited. Treat them as directional,
keep the source link, and label them as such in our docs.
