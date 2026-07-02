"""L0 — local execution adapter.

Run an evaluator as a local subprocess under a time budget; parse its JSON stdout
into an EvalResult. A timeout or crash becomes a veto (bounded blast radius). This
is the zero-dependency "run it on my own machine" adapter; a `skypilot` adapter
(Phase 2) implements the same shape for cloud/k8s.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from ..contract import EvalResult, Veto
from .base import ExecutionAdapter


class LocalAdapter(ExecutionAdapter):
    def __init__(self, budget_s: float = 300.0, python: str = "python3"):
        self.budget_s = budget_s
        self.python = python

    def run(self, evaluator: str, cwd) -> EvalResult:
        try:
            proc = subprocess.run(
                [self.python, evaluator], cwd=str(Path(cwd)),
                capture_output=True, text=True, timeout=self.budget_s)
        except subprocess.TimeoutExpired:
            return EvalResult(None, [Veto("timeout", True, f"exceeded {self.budget_s}s")])
        if proc.returncode != 0:
            return EvalResult(None, [Veto("crash", True, (proc.stderr or "")[-200:])])
        lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
        if not lines:
            return EvalResult(None, [Veto("no_output", True, "evaluator emitted nothing")])
        try:
            return EvalResult.from_json(lines[-1])
        except Exception as e:
            return EvalResult(None, [Veto("bad_output", True, str(e)[:200])])
