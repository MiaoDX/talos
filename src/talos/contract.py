"""L2 — the eval contract.

An evaluator returns one scalar plus hard-constraint vetoes. It is FROZEN during
an experiment lineage: neither the agent nor a mid-run human edits it. The wire
format is JSON (so an evaluator can be written in any language); `EvalResult`
is just the typed view of that JSON.

JSON schema emitted by an evaluator process (stdout):
    {
      "scalar": <float>,            # the optimized metric
      "vetoes": [{"name": str, "triggered": bool, "detail": str}],
      "metrics": {<str>: <number|null>},  # sub-metrics, NOT optimized directly
      "seeds": [<int>, ...],
      "lower_is_better": <bool>
    }
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class Veto:
    """A hard constraint. If `triggered`, the result is disqualified."""
    name: str
    triggered: bool
    detail: str = ""


@dataclass
class EvalResult:
    scalar: float
    vetoes: list[Veto] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    seeds: list[int] = field(default_factory=list)
    lower_is_better: bool = True

    @property
    def vetoed(self) -> bool:
        return any(v.triggered for v in self.vetoes)

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @staticmethod
    def from_json(s: str) -> "EvalResult":
        d = json.loads(s)
        d["vetoes"] = [Veto(**v) for v in d.get("vetoes", [])]
        d.setdefault("metrics", {})
        d.setdefault("seeds", [])
        d.setdefault("lower_is_better", True)
        return EvalResult(**d)


def is_improvement(candidate: EvalResult, baseline_scalar: float,
                   lower_is_better: bool) -> bool:
    """The keep/revert decision. A vetoed result never improves."""
    if candidate.vetoed:
        return False
    s = candidate.scalar
    if s is None or (isinstance(s, float) and (math.isnan(s) or math.isinf(s))):
        return False
    return s < baseline_scalar if lower_is_better else s > baseline_scalar


def weighted_score(objectives: dict[str, float], weights: dict[str, float]) -> float:
    """Soft objectives -> one number (higher-is-better convention).

    Pair with vetoes for the documented AD/robotics pattern:
    multiplicative gates (vetoes) x weighted sum (soft objectives).
    """
    return sum(weights[k] * objectives[k] for k in weights)
