# Release evidence

This note is the human-readable index for release / external-demo evidence. It
should summarize current proof and link to target worktree ledgers or artifacts;
it should not copy raw experiment history into the Talos control repo.

## Current state

| Gate | Current evidence | Status |
| --- | --- | --- |
| CPU minimal demo | Normal local checks in [`../../STATUS.md`](../../STATUS.md). | Passing |
| GPU nanochat local short smoke | RTX 3090 run on 2026-07-02 in `/tmp/talos_nanochat_gpu_UzMZRz/autoresearch`; baseline `val_bpb=1.16269`; scripted candidate `DEPTH 4 -> 3` produced `val_bpb=1.182209` and was reverted. | Passing as a short smoke |
| GPU nanochat overnight/improvement | No overnight ledger yet. | Missing |
| SkyPilot SSH GPU | API server is healthy and the same-host SSH pool config was created, but `sky ssh up --infra rtx3090` is blocked by non-interactive sudo on localhost. | Blocked |
| SkyPilot local Kubernetes smoke | Optional; no current evidence recorded in this repo. | Not run |

Until the GPU rows above link to current target worktree evidence, Talos is not
release-ready for an external GPU demo.

## Review artifacts

- Short-smoke visual summary: [`assets/rtx3090-short-smoke.svg`](./assets/rtx3090-short-smoke.svg)
- Target ledger: `/tmp/talos_nanochat_gpu_UzMZRz/autoresearch/results.tsv`
- Candidate artifact: `/tmp/talos_nanochat_gpu_UzMZRz/autoresearch/.talos/runs/exp-0001/`

## 2026-07-02 RTX 3090 local nanochat smoke

- Commit: Talos worktree under active local changes; target worktree based on
  upstream `karpathy/autoresearch` `228791f`.
- Target worktree: `/tmp/talos_nanochat_gpu_UzMZRz/autoresearch`
- CPU checks: `uv run python examples/ratchet_demo/run_demo.py` pass;
  `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest` pass.
- GPU local nanochat: `results.tsv` in the target worktree.
  - baseline: `val_bpb=1.16269`, `training_seconds=300.0`,
    `num_steps=7249`, `peak_vram_mb=1900.3`, `depth=4`
  - candidate: `DEPTH 4 -> 3`, `val_bpb=1.182209`, `status=revert`,
    `artifact_ref=.talos/runs/exp-0001`
- SkyPilot SSH GPU smoke: not run. `uv sync --group sky` installs the CLI and
  `uv run --group sky sky api info` currently reports no connected SkyPilot API
  server. Next proof needs `sky api start` or `sky api login`, plus a configured
  SSH Node Pool.
- Hardware/runtime: NVIDIA GeForce RTX 3090, driver `570.211.01`, 24576 MiB;
  target env `torch==2.9.1+cu128`.
- Budget: upstream `TIME_BUDGET=300` seconds per train run, using an RTX3090
  smoke setup commit that sets `DEPTH=4`, `DEVICE_BATCH_SIZE=16`, and
  `TOTAL_BATCH_SIZE=2**15`.
- Seeds: none emitted by the upstream train wrapper.
- Result: local GPU short smoke passed with one baseline and one reverted
  candidate; no improving keep found in this short smoke.
- Artifact refs: target `.talos/runs/exp-0001/eval_result.json` and
  `.talos/runs/exp-0001/patch.diff`.
- Reviewer notes: this proves the local GPU path can run a real nanochat
  evaluator on RTX 3090-class hardware. It also proves the optional SkyPilot CLI
  dependency group installs. It does not satisfy the overnight release gate or
  the SkyPilot SSH GPU gate.

## 2026-07-02 same-host SkyPilot SSH attempt

- Talos commit under test: `c0ed4aa` plus this evidence update.
- SkyPilot packaging: `uv sync --group sky` installs the CLI; `uv run --group sky
  sky --version` reports `skypilot, version 0.12.3.post1`.
- API server: `uv run --group sky sky api start` started a local server at
  `http://127.0.0.1:46580`; `uv run --group sky sky api info` reports
  `ApiServerStatus.HEALTHY`.
- SSH pool config: `~/.sky/ssh_node_pools.yaml` now contains pool `rtx3090`
  pointing to `localhost`, user `mi`, key `/home/mi/.ssh/id_rsa`.
- Local prerequisites verified: SSH to localhost with that key succeeds;
  `nvidia-smi` over SSH reports `NVIDIA GeForce RTX 3090, 24576 MiB`; `jq` and
  user-local `kubectl v1.36.2` are available.
- Generated task: `uv run --group sky python
  examples/nanochat/skypilot_ssh_smoke.py --pool rtx3090 --accelerators
  RTX3090:1 --print-yaml` emits `infra: ssh/rtx3090` and
  `accelerators: RTX3090:1`.
- Actual launch attempt: `uv run --group sky sky ssh up --infra rtx3090`.
- Result: blocked before cluster creation. SSH connection to `localhost`
  succeeded, then SkyPilot's bootstrap command failed at `sudo sshd -T` /
  `sudo sed ... /etc/ssh/sshd_config` because sudo requires an interactive
  password: `sudo: a terminal is required to read the password` and
  `sudo: a password is required`.
- Reviewer notes: this resolves the earlier "No SkyPilot API server is
  connected" issue but does not satisfy the SkyPilot SSH GPU gate. Continuing
  requires either passwordless sudo for the local user on this machine or a
  password-bearing SSH Node Pool config, then rerunning `sky ssh up --infra
  rtx3090` before launching the nanochat SkyPilot smoke.

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
