"""Run the nanochat GPU demo through Talos's local keep/revert loop.

Run this from an upstream `karpathy/autoresearch` worktree after copying or
referencing the Talos evaluator/proposal files. It requires prepared data,
PyTorch dependencies, and one NVIDIA GPU.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from proposals import build_smoke_proposals  # noqa: E402
from talos.adapters import LocalAdapter      # noqa: E402
from talos.ledger import TSVLedger           # noqa: E402
from talos.ratchet import run_ratchet        # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("worktree", help="clean upstream autoresearch worktree")
    parser.add_argument("--timeout-s", type=float, default=900)
    parser.add_argument("--max-iterations", type=int, default=2)
    args = parser.parse_args(argv)

    worktree = Path(args.worktree).resolve()
    evaluator = Path(__file__).with_name("evaluator.py").resolve()
    subprocess.run(["git", "status", "--porcelain"], cwd=worktree,
                   check=True, capture_output=True, text=True)
    out = run_ratchet(
        worktree,
        build_smoke_proposals(),
        evaluator=str(evaluator),
        adapter=LocalAdapter(budget_s=args.timeout_s),
        ledger=TSVLedger(worktree / "results.tsv"),
        lower_is_better=True,
        editable_paths=["train.py"],
        protected_paths=["prepare.py", "program.md"],
        max_iterations=args.max_iterations,
    )
    print((worktree / "results.tsv").read_text())
    print(f"best val_bpb = {out['best']:.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
