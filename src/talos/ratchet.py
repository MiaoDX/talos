"""The keep/revert ratchet — the engine behind the `ratchet-experiment` skill.

`workdir` is a git repo whose current commit is the baseline. For each proposal:
edit files → commit → evaluate (L0) → keep (leave the commit) if it improves the
frozen metric (L2), else `git reset --hard HEAD~1` to revert. Every step is logged
to the ledger (L1). The codebase only ratchets forward.

In production the *proposals* are made by a coding agent (Claude Code / Codex)
editing the sandbox file; here a `Proposal.apply` callable stands in so the loop
is testable without an LLM.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from .adapters.local import LocalAdapter
from .contract import is_improvement
from .ledger import TSVLedger


@dataclass
class Proposal:
    description: str
    apply: Callable[[Path], None]   # mutate files in the workdir


def _git(workdir, *args):
    return subprocess.run(["git", *args], cwd=str(workdir),
                          capture_output=True, text=True, check=True)


def _head(workdir) -> str:
    return _git(workdir, "rev-parse", "HEAD").stdout.strip()


def _exclude_ledger(workdir: Path, ledger_path: Path):
    """Keep the ledger untracked so `git add -A` / `git reset --hard` never touch it."""
    try:
        rel = ledger_path.resolve().relative_to(workdir.resolve())
    except ValueError:
        return  # ledger lives outside the workdir; nothing to exclude
    exclude = workdir / ".git" / "info" / "exclude"
    if exclude.parent.exists():
        existing = exclude.read_text() if exclude.exists() else ""
        if str(rel) not in existing.split():
            with exclude.open("a") as f:
                f.write(f"\n{rel}\n")


def run_ratchet(workdir, proposals, *, evaluator: str = "evaluator.py",
                adapter: Optional[LocalAdapter] = None,
                ledger: Optional[TSVLedger] = None, lower_is_better: bool = True):
    workdir = Path(workdir)
    adapter = adapter or LocalAdapter()
    ledger = ledger or TSVLedger(workdir / "results.tsv")
    _exclude_ledger(workdir, ledger.path)

    base = adapter.run(evaluator, workdir)
    best = base.scalar if not base.vetoed and base.scalar is not None \
        else (float("inf") if lower_is_better else float("-inf"))
    ledger.append("baseline", _head(workdir), base.scalar, None,
                  "baseline" if not base.vetoed else "veto", "initial state")
    history = [{"experiment": "baseline", "result": base, "status": "baseline"}]

    for i, p in enumerate(proposals, 1):
        p.apply(workdir)
        _git(workdir, "add", "-A")
        _git(workdir, "commit", "-q", "-m", f"exp {i}: {p.description}")
        sha = _head(workdir)                      # the experiment's own commit
        res = adapter.run(evaluator, workdir)
        if is_improvement(res, best, lower_is_better):
            delta = res.scalar - best
            best = res.scalar
            status = "keep"
        else:
            _git(workdir, "reset", "--hard", "-q", "HEAD~1")   # revert
            delta = None
            status = "veto" if res.vetoed else "revert"
        ledger.append(i, sha, res.scalar, delta, status, p.description)
        history.append({"experiment": i, "result": res, "status": status})

    return {"best": best, "ledger": ledger, "history": history}
