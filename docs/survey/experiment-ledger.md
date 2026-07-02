# Survey: experiment ledger / tracking (L1)

**Recommendation:** git + append-only factual ledger as **Tier 0** (default);
**MLflow** as the swappable Tier-1 tracker; an internal-system adapter as Tier 2.
See [`../decisions/0001-ledger-and-audit-model.md`](../decisions/0001-ledger-and-audit-model.md)
for the audit-model decision.

## Separation of responsibilities

Talos deliberately does **not** treat git log, the ledger, and docs as three ways
to store the same thing:

- **Git** stores code state and rollback. The kept lineage should contain the
  candidate commits that beat the frozen evaluator.
- **The ledger** stores every experiment fact, including failed/reverted attempts
  that should not remain on the kept lineage: `experiment, baseline_commit,
  candidate_commit, metric, delta, status, description, evaluator, seeds, vetoes,
  metrics, artifact_ref`.
- **Docs** store human decisions and summaries: evaluator rationale, phase
  summaries, known failed directions, and strategy changes.

This split is important because reverted experiments are still research memory,
but keeping every failed candidate in the main git lineage makes the branch noisy
and fragile.

## Tier 0 — git + TSV (default)

The AutoResearch-native idiom is still the starting point: a git branch is the
rollback primitive and an append-only TSV is the run ledger. Talos extends the TSV
beyond the minimal `experiment, commit, metric, delta, status, description` row so
that the agent and reviewer can reconstruct what happened without reading the git
log as a database.

For single-machine and small-team use, this gives zero-infrastructure provenance:
code states are in git, run facts are in the ledger, and candidate patches / raw
evaluator outputs are preserved under `.talos/runs/` when available.

## Tier 1 — when TSV is not enough

- **MLflow** — recommended default OSS tracker: language-agnostic, REST/auto-log,
  dominant adoption, clean model registry, free self-host.
- **Aim** — best lightweight local-first option; fast UI; can sit on an MLflow
  backend.
- **ClearML** — bundles tracking + orchestration + HPO; steeper setup.
- **W&B (self-host)** — most polished, but per-seat pricing scales poorly and the
  core is not OSI-open.
- **DVC / DVCLive** — git-centric data + experiment versioning.

## Design rule

Keep everything behind the L1 contract (`append(record)`, `query(...)`), so the
choice is reversible and a team can start with TSV and graduate to MLflow without
touching skills.

## Why immutability matters

The ledger is also the **anti-fabrication** record: an append-only log plus
candidate patch/artifact references means a reported result can be re-derived
from the exact code and evaluator that produced it. See [`../../AGENTS.md`](../../AGENTS.md).
