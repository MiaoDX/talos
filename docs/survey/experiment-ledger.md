# Survey: experiment ledger / tracking (L1)

**Recommendation:** git + append-only TSV as **Tier 0** (default); **MLflow** as
the swappable Tier-1 tracker; an internal-system adapter as Tier 2.

## Tier 0 — git + TSV (default)
The AutoResearch-native idiom: each row is `experiment, commit, metric, delta,
status, description` (+ seeds, resource usage). The git history is the audit
trail; the log is the agent's memory across runs. Keep it append-only/immutable.
This is enough for single-machine and small-team use, and it doubles as
provenance with zero infrastructure.

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
git-committed code means a reported result can be re-derived from the exact commit
that produced it. See [`../../AGENTS.md`](../../AGENTS.md).
