# Active Capsule: Testing Strategy

Status: BLOCKED

Source plan/gate/issue: `docs/human/testing-strategy.md`

Latest user intent classification: implement the testing strategy through
`intuitive-flow`; do not stop until done.

Current slice: implementation complete, full test execution still incomplete.
CPU-safe release-demo surfaces and documentation are in place. A real local GPU
nanochat short smoke has been produced. The local SkyPilot API server is now
healthy and a same-host `rtx3090` SSH Node Pool config exists, but `sky ssh up`
is blocked by non-interactive sudo on localhost.

Blocker fingerprint: no hard blocker for CPU-safe implementation, local GPU
short smoke, SkyPilot CLI packaging, or SkyPilot API server startup. Remaining
release evidence needs overnight GPU runtime and SkyPilot SSH Node Pool
bootstrap. The concrete SkyPilot blocker is `sudo` during `sky ssh up --infra
rtx3090`: SSH succeeds, then SkyPilot fails at `sudo sshd -T` / sshd config
bootstrap because the local user does not have non-interactive sudo.

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

SkyPilot same-host SSH attempt:

```text
SkyPilot API: http://127.0.0.1:46580, ApiServerStatus.HEALTHY
Pool config: ~/.sky/ssh_node_pools.yaml -> rtx3090 localhost mi /home/mi/.ssh/id_rsa
Generated task: infra ssh/rtx3090, accelerators RTX3090:1
Launch command: uv run --group sky sky ssh up --infra rtx3090
Failure: sudo requires an interactive password during SSH Node Pool bootstrap.
```

Completed slice batch summary: nanochat wrapper/runbooks and SkyPilot adapter
plumbing are implemented; human docs now distinguish implemented CPU-safe
surfaces from release-only external evidence.

Next hypothesis or next slice: either configure non-interactive sudo/password
for the same-host SSH pool and rerun `sky ssh up --infra rtx3090`, or use a
remote GPU host whose SSH user can run SkyPilot's sudo bootstrap. In parallel,
complete the overnight local GPU run for release evidence.

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
evidence tasks on configured hardware. The SkyPilot path now has a packaged CLI
and healthy local API server; next it needs SSH Node Pool sudo bootstrap to
complete successfully.
