# Survey: compute / execution backends (L0)

**Recommendation:** default to **SkyPilot** (k8s adapter) for BYO-cloud, plus a
**`local` subprocess** adapter for the single-GPU case. Do not build a new cloud
abstraction.

## Why SkyPilot is the default
- BYO-cloud across 20+ clouds + Kubernetes + Slurm, with cost arbitrage, gang
  scheduling, queueing, and pools. ([repo](https://github.com/skypilot-org/skypilot))
- Ships an **Agent Skill** for Claude Code / Codex, so the agent can drive it.
- Strongest AutoResearch track record: the SkyPilot team ran Karpathy's
  `autoresearch` in parallel on 13×H100 + 3×H200, ~910 experiments in 8h
  (~9× the sequential rate) for ≈$309; Shopify runs all AI training on SkyPilot.
- **China clouds** (Alibaba Cloud, Volcano Engine) are reached via their managed
  Kubernetes (ACK, VKE) or a custom SkyPilot plugin — which is exactly the
  "thin adapter, each org plugs in its own" model.

## The landscape (even-handed)

| Option | Model | Strength | Limitation |
| --- | --- | --- | --- |
| **SkyPilot** | BYOC multi-cloud/k8s/Slurm launcher | most complete; agent skill; proven | you operate it; many small details |
| **dstack** | lighter pod orchestration | cleaner UX, any Docker image | weaker cost optimization; k8s backend needs pre-provisioned nodes |
| **Runhouse** (now Kubetorch) | Pythonic send-functions-to-remote | BYOC, debuggable, K8s-native | smaller community; product pivot |
| **Modal** | managed serverless `@app.function` | simplest decorator; gVisor sandboxes | NOT BYOC; SDK lock-in; ~2× bare-metal cost |
| **Ray / KubeRay** | Python-native distributed | in-cluster task/actor parallelism | single-cloud-ish; not a multi-cloud launcher |
| **k8s-native** (Kueue, Volcano, JobSet, Kubeflow) | raw primitives / CRDs | max control; gang scheduling; quotas | high ops burden; not agent-friendly |
| **Determined** | bundled compute+tracking+HPO | all-in-one | heavy/opinionated; bundles what we want swappable |
| **Slurm** | HPC scheduler | topology-aware fixed clusters | not multi-cloud (SkyPilot can front it) |
| **Flyte / Metaflow** | typed/Pythonic ML pipelines | reproducible DAGs; great DX | workflow-oriented; setup overhead |

## The comparability decision (must-decide)
A fixed *wall-clock* budget is only comparable on identical hardware. For
multi-cloud heterogeneous GPUs, **pin a hardware class** or switch to a
**deterministic compute budget** (steps / tokens / FLOPs / scenario-count). For
closed-loop sim, fix the scenario set + seeds. Document the choice prominently.

> Takeaway: the compute layer is the *least* novel part of Talos. Reuse it and
> spend the effort on L2 (eval) and L3 (skills).
