# Testing strategy

This document defines how Talos proves it is standalone and useful to a user who
has a GPU machine. CPU-only coverage is still useful as the smallest smoke test,
but it is not sufficient for a release or external demo.

## Goals

- A fresh clone can run at least one local demo without external accounts.
- A GPU user can run a real AutoResearch-style workload, not only a toy CPU loop.
- The same L0 execution contract is tested through direct local execution and a
  SkyPilot-backed path.
- Experiment facts remain in the target worktree ledger and artifacts, not in
  this control repository.

## Test groups

| Group | Purpose | Runner | Required when |
| --- | --- | --- | --- |
| CPU minimal demo | Prove keep/revert/veto mechanics quickly | `LocalAdapter` on CPU | every PR / CI |
| GPU nanochat local | Prove Talos works on a real ML workload | `LocalAdapter` on a single NVIDIA GPU | release / external demo |
| SkyPilot SSH GPU | Prove the same task shape can run through SkyPilot on an existing GPU machine | `SkyPilotAdapter` targeting an SSH Node Pool | release / external demo |
| SkyPilot local Kubernetes | Prove the Kubernetes API path can be reached locally | `SkyPilotAdapter` targeting `sky local up` | optional/manual smoke |
| Cloud or production Kubernetes GPU | Prove managed multi-node/cloud execution | `SkyPilotAdapter` targeting real infra | future/manual |

## Implemented command surface

CI verifies the CPU-safe pieces of this matrix:

```bash
uv run python examples/ratchet_demo/run_demo.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest
```

The second command covers the CPU ratchet loop, ledger/artifact safeguards,
`SkyPilotAdapter` SSH Node Pool task generation, SkyPilot result parsing through
an injectable runner, the nanochat evaluator wrapper, and scripted nanochat
proposal helpers.

Release-required GPU evidence uses the manual runbooks in
[`../../examples/nanochat/`](../../examples/nanochat/):

```bash
uv run python examples/nanochat/run_local_gpu.py /path/to/autoresearch --max-iterations 2
uv sync --group sky
uv run python examples/nanochat/skypilot_ssh_smoke.py --pool <pool> --accelerators <GPU>:1 --worktree /path/to/autoresearch
```

Use `--print-yaml` on `skypilot_ssh_smoke.py` to inspect the generated
`infra: ssh/<pool>` task before launching it. SkyPilot is an optional dependency
group so the default CPU development environment remains lightweight.

## Why SSH Node Pool is the first SkyPilot GPU path

The primary GPU proof should be the shortest path to the user's hardware: run
the frozen evaluator directly on a single local GPU. The first SkyPilot proof
should then wrap an existing GPU machine as an SSH Node Pool, because that
validates the shared SkyPilot task interface without requiring Kubernetes
operations. SkyPilot documents existing-machine setup through `sky ssh up` in
its SSH Node Pool guide:
<https://docs.skypilot.co/en/latest/reservations/existing-machines.html>.

`sky local up` creates a local Kubernetes cluster through kind. That is useful
for a local Kubernetes smoke test, but it is not the default GPU proof. GPU on
Kubernetes requires cluster-level setup such as NVIDIA device plugins or GPU
operators and node labels. Those are valid production concerns, but they would
make the first public demo about Kubernetes operations instead of Talos's
eval-driven keep/revert loop. SkyPilot's local Kubernetes guide says
`sky local up` creates a 1-node kind cluster and notes kind is not the production
or GPU/multi-node path:
<https://docs.skypilot.co/en/latest/reference/kubernetes/kubernetes-deployment.html>.
For Kubernetes GPU setup requirements, see:
<https://docs.skypilot.co/en/latest/reference/kubernetes/kubernetes-setup.html>.

## Release gates

Before a release or external demo, the repo should have current evidence for:

1. `uv run python examples/ratchet_demo/run_demo.py` succeeds on CPU and records
   `baseline`, `keep`, `veto`, and `keep` rows.
2. `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest` succeeds.
3. The GPU nanochat local run succeeds on one NVIDIA GPU and writes a ledger row
   for baseline plus at least one candidate outcome.
4. The GPU nanochat overnight run either keeps at least one improving candidate
   or records a reproducible no-improvement result in the ledger. A short smoke
   proves the mechanism; release evidence should prove whether the loop can
   discover an actual gain under the chosen budget.
5. The SkyPilot SSH GPU short-budget smoke succeeds against an existing GPU
   machine using the same evaluator output contract. The SkyPilot gate proves the
   adapter path; it does not need to duplicate the full overnight local GPU run.
6. Each GPU run records the GPU model, driver/runtime basics, seed(s), budget
   type, evaluator identity, artifact reference, and kept/reverted status.

CPU-only users may stop after the minimal demo; that path is a smoke test, not
the full value proposition.

The raw proof lives in the target experiment worktree: its git lineage,
append-only ledger, and `.talos/runs/` artifacts. The Talos control repo may
link to a concise release evidence note at [`release-evidence.md`](./release-evidence.md),
but it should not absorb the raw experiment history.

## SkyPilot SSH shape

The first SkyPilot GPU runbook should support two shapes:

- **Same-host SSH pool:** register this GPU machine through SkyPilot's SSH Node
  Pool flow, then target it with `infra: ssh/<pool>`.
- **Remote GPU host:** use the same task shape against a separate SSH-reachable
  GPU machine.

The same-host path is the default public runbook because it does not require a
second machine. The remote-host variant proves the same abstraction scales to
shared GPU boxes.

## Non-goals

- Do not require Kubernetes, Docker, cloud credentials, or SkyPilot for the
  first CPU smoke test.
- Do not make kind the primary GPU path.
- Do not store production experiment history in the Talos control repo.
- Do not treat a wall-clock GPU run on arbitrary hardware as comparable unless
  the hardware class is pinned; prefer deterministic budgets such as fixed
  steps, tokens, FLOPs, or scenario counts.

## Implementation plan

1. Keep the CPU ratchet demo as the CI smoke test and add a second CPU demo only
   if it makes scalar-plus-veto behavior clearer. Do not let a second CPU demo
   block the GPU work. **Current status:** implemented and CI-covered.
2. Turn `examples/nanochat/` into the release-required GPU demo with a frozen
   evaluator wrapper, a short smoke budget, and an overnight budget. Prefer a
   deterministic budget for comparable release evidence. **Current status:**
   runbook and wrapper implemented; a real RTX 3090 short smoke is recorded in
   [`release-evidence.md`](./release-evidence.md), but overnight/improvement
   evidence is still missing.
3. Extend `SkyPilotAdapter` enough to generate and run a task against an
   existing SSH Node Pool, including an explicit `infra: ssh/<pool>` resource
   target, then parse the same `EvalResult` JSON line as `LocalAdapter`.
   **Current status:** task generation and runner/result parsing implemented and
   test-covered; SkyPilot CLI packaging is available through `uv sync --group
   sky`; same-host RTX 3090 SSH-pool smoke evidence is recorded in
   [`release-evidence.md`](./release-evidence.md).
4. Implement the first nanochat proposals as scripted proposal functions, not
   free-form agent edits. This proves the evaluator, ledger, rollback, and
   adapter contracts before adding the risk and variance of live agent proposal
   generation. **Current status:** implemented in
   [`../../examples/nanochat/proposals.py`](../../examples/nanochat/proposals.py).
5. Add manual runbooks for:
   - local GPU nanochat;
   - SkyPilot SSH GPU nanochat;
   - optional `sky local up` Kubernetes smoke.
   **Current status:** all three command surfaces exist. The Kubernetes path
   remains optional/manual and depends on `sky local up` plus local cluster
   runtime/GPU setup.
6. Keep CI focused on CPU tests unless a GPU runner is intentionally provisioned.
7. Treat timeout, nonzero exit, non-finite metric, or missing JSON result as a
   ledgered veto/crash according to the existing ratchet contract, not as an
   informal failed command. **Current status:** local and nanochat evaluator
   wrappers map these outcomes to vetoes; `run_ratchet` records crashes and
   policy violations in the ledger.

## Acceptance criteria

- A new user can follow README commands and see a successful CPU ledger in
  minutes.
- A GPU user can follow the nanochat runbook and produce a reproducible ledger
  without editing Talos internals.
- A SkyPilot user can point Talos at an SSH Node Pool and run the same evaluator
  contract through `SkyPilotAdapter`.
- A release reviewer can tell whether the current evidence is CPU-only,
  local-GPU verified, or SkyPilot-GPU verified from
  [`release-evidence.md`](./release-evidence.md), without reading chat history.
- Documentation clearly labels which gates are CI-required, release-required,
  optional/manual, and future/manual.
