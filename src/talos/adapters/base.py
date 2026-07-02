"""L0 execution adapter contract.

Adapters are the only place where Talos should know how an experiment is run:
local subprocess, SkyPilot, Executor, CloudML, Slurm, or an internal queue all
conform by returning the same EvalResult.
"""
from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from ..contract import EvalResult


@runtime_checkable
class ExecutionAdapter(Protocol):
    """Run a frozen evaluator inside an experiment worktree."""

    def run(self, evaluator: str, cwd: str | Path) -> EvalResult:
        """Execute `evaluator` from `cwd` and return a contract result."""
