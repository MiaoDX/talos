# Release evidence

This note is the human-readable index for release / external-demo evidence. It
should summarize current proof and link to target worktree ledgers or artifacts;
it should not copy raw experiment history into the Talos control repo.

## Current state

- CPU minimal demo: verified by the normal local checks in [`../../STATUS.md`](../../STATUS.md).
- GPU nanochat local: no current evidence recorded in this repo.
- SkyPilot SSH GPU: no current evidence recorded in this repo.
- SkyPilot local Kubernetes smoke: optional; no current evidence recorded in this
  repo.

Until the GPU rows above link to current target worktree evidence, Talos is not
release-ready for an external GPU demo.

## Evidence template

Use one section per release candidate:

```text
## <date> <release/demo name>

- Commit: <Talos commit under test>
- Target worktree: <path or repo/ref>
- CPU checks: <command + pass/fail>
- GPU local nanochat: <ledger path + summary>
- SkyPilot SSH GPU smoke: <ledger path + summary>
- Hardware/runtime: <GPU model, driver, CUDA/runtime, Python>
- Budget: <fixed steps/tokens/FLOPs/scenario-count, or pinned hardware wall-clock>
- Seeds: <seed list>
- Result: <keep / no-improvement / veto / crash summary>
- Artifact refs: <target .talos/runs/... refs>
- Reviewer notes: <known limits or follow-up>
```
