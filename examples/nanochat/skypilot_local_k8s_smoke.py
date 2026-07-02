"""Generate or run the optional SkyPilot local Kubernetes nanochat smoke."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from talos.adapters import SkyPilotAdapter  # noqa: E402


def build_adapter(accelerators: str | None, timeout_s: float) -> SkyPilotAdapter:
    return SkyPilotAdapter(
        infra="k8s",
        accelerators=accelerators,
        budget_s=timeout_s,
        setup="uv sync",
        python="uv run python",
        cluster_name="talos-local-k8s",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accelerators", default=None)
    parser.add_argument("--timeout-s", type=float, default=900)
    parser.add_argument("--print-yaml", action="store_true")
    parser.add_argument("--worktree", default=".", help="worktree passed to SkyPilotAdapter.run")
    args = parser.parse_args(argv)

    adapter = build_adapter(args.accelerators, args.timeout_s)
    if args.print_yaml:
        print(adapter.task_yaml("talos_nanochat_evaluator.py"))
        return 0

    worktree = Path(args.worktree).resolve()
    evaluator = worktree / "talos_nanochat_evaluator.py"
    shutil.copy(Path(__file__).with_name("evaluator.py"), evaluator)
    try:
        result = adapter.run(evaluator.name, worktree)
        print(result.to_json())
        return 0
    finally:
        evaluator.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
