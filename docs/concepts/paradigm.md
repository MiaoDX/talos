# The AutoResearch paradigm (the ratchet loop)

Talos's loop is the one popularized by Andrej Karpathy's
[`autoresearch`](https://github.com/karpathy/autoresearch) (released March 2026).
Understanding *why* it is shaped this way is more useful than the code itself.

## The three-file contract

`autoresearch` splits the world into three files that encode an ownership
contract:

- **`prepare.py` — immutable.** Data prep, tokenizer, dataloader, the evaluation
  function, and the fixed budget constant. Neither human nor agent edits it
  during a run. *This is the integrity guarantee:* if the agent could touch the
  evaluator, it would make the test easier instead of making the model better.
- **`train.py` — the agent's sandbox.** The one file the agent mutates —
  architecture, optimizer, hyperparameters, everything.
- **`program.md` — human-owned.** Instructions, constraints, stopping criteria,
  and the loop itself. It steers *what kind* of changes the agent explores
  (Karpathy phases it: obvious tuning → small architectural changes → moonshots).

Talos generalizes these into the L2 eval contract (the immutable part), the
existing codebase (the sandbox), and a skill's spec (the human-owned part).

## The loop

On a dedicated git branch, the agent repeats:

1. read `program.md` / the spec, the code, and the ledger;
2. propose one change, with explicit reasoning;
3. edit the code; commit;
4. run a **fixed-budget** experiment (e.g., 5 minutes wall-clock);
5. read the scalar metric from the log; if the run crashed, try to fix it a few
   times, else give up;
6. if the metric improved, the commit stays and becomes the new baseline;
   otherwise `git reset` reverts it instantly.

This is a **ratchet**: the codebase only moves forward, every kept commit is a
validated improvement, and the git log is both the audit trail and the agent's
memory across restarts.

## Why each choice matters

- **A single, comparable scalar metric.** Karpathy uses `val_bpb` (validation
  bits-per-byte) precisely because it is one number, lower-is-better, and
  *vocabulary-independent*, so architectural/tokenizer changes are compared
  fairly. Pick a metric that stays comparable across the changes you expect.
- **A fixed budget.** It puts "trains faster" and "converges lower" on equal
  footing and bounds the blast radius of any single run.
- **Git as the rollback primitive.** Forward-only progress, free audit trail,
  durable memory.

## What it is NOT

- **Not hyperparameter search.** AutoML/Optuna/Ray Tune search a *predefined*
  parameter space with convergence guarantees. The ratchet lets the LLM edit
  *arbitrary code* — open-ended search in code space, with no guarantees. (For
  pure numeric tuning, classical optimizers are better — see
  [`../pitfalls.md`](../pitfalls.md).)
- **Not a standalone agent.** It runs *on top of* an existing coding agent
  (Claude Code / Codex). There is no orchestrator to build.

## The single most important caveat

The loop's value is bounded entirely by its metric. When experiments run ~100×
faster than a human, the **evaluator becomes the bottleneck** — which is why
Talos is eval-driven first. See [`eval-first.md`](./eval-first.md).
