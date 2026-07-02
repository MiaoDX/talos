# Active Capsule: Testing Strategy

Status: PARKED

Source plan/gate/issue: `docs/human/testing-strategy.md`

Latest user intent classification: implement the testing strategy through
`intuitive-flow`; do not stop until done.

Current slice: implementation complete, full test execution still incomplete.
CPU-safe release-demo surfaces and documentation are in place. A real local GPU
nanochat short smoke has been produced; overnight GPU and SkyPilot SSH evidence
are still missing.

Blocker fingerprint: no hard blocker for CPU-safe implementation, local GPU
short smoke, or SkyPilot CLI packaging. Remaining release evidence needs
overnight GPU runtime and SkyPilot API server / SSH Node Pool setup.

Last proven evidence:

```bash
uv run python examples/ratchet_demo/run_demo.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest
```

The CPU demo produced `baseline`, `keep`, `veto`, and `keep` ledger rows. Pytest
passed 20 tests covering the CPU ratchet loop, external evaluator hashing,
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

Completed slice batch summary: nanochat wrapper/runbooks and SkyPilot adapter
plumbing are implemented; human docs now distinguish implemented CPU-safe
surfaces from release-only external evidence.

Next hypothesis or next slice: complete the overnight local GPU run, then
complete the SkyPilot SSH GPU smoke against a configured SSH Node Pool.

Next proof command/artifact:

```bash
uv run python examples/ratchet_demo/run_demo.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest
```

Stop condition: not met for the full testing plan. Full CPU verification and a
local GPU short smoke passed, but overnight GPU/SkyPilot proof is still missing.

No-touch scope: do not alter evaluator metrics/data to make a number improve;
do not claim release readiness without real GPU and SkyPilot evidence.

Parked work: overnight local GPU run and SkyPilot SSH GPU smoke remain release
evidence tasks on configured hardware. The SkyPilot path now has a packaged CLI;
next it needs `sky api start` or `sky api login` plus an SSH Node Pool.
