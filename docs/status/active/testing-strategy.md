# Active Capsule: Testing Strategy

Status: PARTIAL

Source plan/gate/issue: `docs/human/testing-strategy.md`

Latest user intent classification: implement the testing strategy through
`intuitive-flow`; do not stop until done.

Current slice: implementation complete, full test execution still incomplete
only because overnight/improvement GPU evidence is still missing. CPU-safe
release-demo surfaces and documentation are in place. A real local GPU nanochat
short smoke and a real same-host SkyPilot SSH GPU smoke have both been produced.

Blocker fingerprint: no hard blocker for CPU-safe implementation, local GPU
short smoke, SkyPilot CLI packaging, SkyPilot API server startup, or SkyPilot
SSH GPU smoke. Remaining release evidence needs overnight GPU runtime and any
production-domain evaluator evidence.

Last proven evidence:

```bash
uv run python examples/ratchet_demo/run_demo.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest
```

The CPU demo produced `baseline`, `keep`, `veto`, and `keep` ledger rows. Pytest
passed 21 tests covering the CPU ratchet loop, external evaluator hashing,
nanochat evaluator/proposals, SkyPilot SSH/local-Kubernetes task generation, and
SkyPilot result parsing/cleanup.

Local GPU smoke evidence:

```text
Target worktree: /tmp/talos_nanochat_gpu_UzMZRz/autoresearch
Hardware: NVIDIA GeForce RTX 3090, driver 570.211.01, 24576 MiB
Baseline: val_bpb=1.16269, depth=4, training_seconds=300.0
Candidate: DEPTH 4 -> 3, val_bpb=1.182209, status=revert
Artifact: .talos/runs/exp-0001
```

SkyPilot same-host SSH smoke:

```text
SkyPilot API: http://127.0.0.1:46580, ApiServerStatus.HEALTHY
Pool config: ~/.sky/ssh_node_pools.yaml -> rtx3090 localhost mi /home/mi/.ssh/id_rsa
Generated task: infra ssh/rtx3090, accelerators RTX3090:1
Launch command: uv run --group sky python examples/nanochat/skypilot_ssh_smoke.py --pool rtx3090 --accelerators RTX3090:1 --timeout-s 1800 --worktree /tmp/talos_nanochat_gpu_UzMZRz/autoresearch
SkyPilot job: talos-rtx3090 job 2, status SUCCEEDED, log ~/sky_logs/sky-2026-07-02-18-50-28-135583
Result: val_bpb=1.181977, num_steps=7846, total_seconds=334.8, vetoes=[]
```

Completed slice batch summary: nanochat wrapper/runbooks and SkyPilot adapter
plumbing are implemented; human docs now distinguish implemented CPU-safe
surfaces from release-only external evidence.

Next hypothesis or next slice: complete the overnight local GPU run for release
evidence. SkyPilot SSH is no longer the active blocker.

Next proof command/artifact:

```bash
uv run python examples/ratchet_demo/run_demo.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest
```

Stop condition: not met for the full testing plan. Full CPU verification and a
local GPU short smoke and SkyPilot SSH GPU short smoke passed, but overnight GPU
proof is still missing.

No-touch scope: do not alter evaluator metrics/data to make a number improve;
do not claim release readiness without overnight/improvement GPU evidence.

Parked work: overnight local GPU run remains a release evidence task on
configured hardware. Optional Kubernetes/cloud SkyPilot paths remain manual
future evidence.
