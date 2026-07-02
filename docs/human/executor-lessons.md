# Lessons From Executor

Talos is not a smaller clone of Executor. Executor is an internal operator repo:
it combines a CLI, an AI skill, workflow runbooks, target graphs, credentials,
and many platform adapters. Talos extracts the parts of that approach that are
portable enough to share publicly.

## What Talos keeps

1. **Workflow first.** Broad or multi-step requests should route through an
   explicit workflow/runbook before an agent starts composing low-level commands.
2. **Contract first.** Every boundary needs a stable shape: command input,
   structured result, failure mode, and artifact location.
3. **JSON for machines, Markdown for humans.** Agents need parseable outputs;
   humans need concise current-truth docs and decision records.
4. **Backend isolation.** Local subprocess, SkyPilot, Executor, CloudML, Slurm, or
   an internal queue should differ only behind an execution adapter.
5. **Durable evidence.** A run is not real because a chat transcript says so.
   Keep patches, result JSON, errors, job IDs or handles, and ledger rows.
6. **Protected scoring surface.** Evaluators, metric definitions, eval data, and
   `program.md` are not candidate-change material during an experiment lineage.
7. **Clean rollback.** Failed, reverted, or policy-violating attempts must not
   pollute the next experiment.
8. **Status docs are operational truth.** A new agent should quickly learn what
   is runnable, what is scaffolded, and what needs external hardware or accounts.

## What Talos leaves out

Talos deliberately does not include a general YAML target graph, internal account
defaults, team-specific command trees, browser login state, cloud credentials, or
platform-specific SOPs. Those are valid in an operator repo, but they would make a
public AutoResearch harness harder to inspect and reuse.

Instead, Talos keeps the stable spine small:

```
target worktree + frozen evaluator
  -> ExecutionAdapter
  -> EvalResult
  -> Ledger
  -> bounded search loop
```

Executor-style systems can still plug in as one execution backend. The adapter
boundary is the point: Talos should learn from platform experience without
turning into the platform.

## Design implications

- Add new compute systems under `src/talos/adapters/`, not in the ratchet core.
- Add new domains under `constraints/`, with frozen evaluators that emit the
  `EvalResult` JSON contract.
- Add new search behavior beside the ratchet loop, consuming the same ledger and
  evaluator results.
- Promote a platform detail into Talos only after it can be stated as a portable
  contract.
