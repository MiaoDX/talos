"""L3 helper — parallel / factorial-grid orchestration (v0 SCAFFOLD, partly unverified).

A sequential ratchet is greedy hill-climbing. Running a *factorial grid* of variants
in parallel catches interaction effects a greedy loop misses, and a two-tier
"screen on cheap hardware, confirm on fast" strategy controls cost.

`factorial_grid` is real and tested. `run_grid` (parallel dispatch + screen/confirm)
is a v0 scaffold: real parallel execution needs the SkyPilot adapter plus a real
evaluator, neither available in CI. See docs/survey/agent-skills.md.
"""
from __future__ import annotations

from itertools import product
from typing import Any


def factorial_grid(axes: dict[str, list[Any]]) -> list[dict[str, Any]]:
    """Cartesian product of named axes -> list of parameter dicts (stable order)."""
    keys = list(axes)
    return [dict(zip(keys, combo)) for combo in product(*(axes[k] for k in keys))]


def run_grid(*args, **kwargs):  # pragma: no cover - v0 scaffold, unverified
    raise NotImplementedError(
        "run_grid is a v0 scaffold. Intended flow: build the grid with "
        "factorial_grid(), submit each cell in PARALLEL via an execution adapter "
        "(e.g. SkyPilotAdapter) under a cheap 'screen' budget, take the top-k by "
        "scalar, then re-run those under a higher-fidelity 'confirm' budget — "
        "trusting only results whose seed variance is small relative to the effect. "
        "Add novelty filtering to cut wasted runs. "
        "See docs/survey/agent-skills.md and docs/concepts/eval-first.md.")
