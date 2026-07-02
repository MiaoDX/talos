"""Talos EvalResult wrapper for the nanochat/autoresearch GPU demo.

This wrapper preserves the upstream contract: run the training script, parse the
final summary, and optimize `val_bpb` as a lower-is-better scalar. It adds Talos
vetoes for crashes, timeouts, missing metrics, non-finite values, and optional
VRAM/budget guardrails.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path


SUMMARY_RE = re.compile(r"^([A-Za-z_]+):\s+([-+0-9.eE]+)\s*$")


def parse_summary(text: str) -> dict[str, float]:
    metrics: dict[str, float] = {}
    for line in text.splitlines():
        match = SUMMARY_RE.match(line.strip())
        if match:
            metrics[match.group(1)] = float(match.group(2))
    return metrics


def emit(scalar, veto_name: str | None, detail: str, metrics: dict, seeds: list[int]):
    if isinstance(scalar, float) and (math.isnan(scalar) or math.isinf(scalar)):
        scalar = None
    vetoes = []
    if veto_name:
        vetoes.append({"name": veto_name, "triggered": True, "detail": detail})
    print(json.dumps({
        "scalar": scalar,
        "vetoes": vetoes,
        "metrics": metrics,
        "seeds": seeds,
        "lower_is_better": True,
    }))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-cmd", default=os.environ.get("TALOS_NANOCHAT_TRAIN_CMD", "uv run train.py"))
    parser.add_argument("--timeout-s", type=float, default=float(os.environ.get("TALOS_NANOCHAT_TIMEOUT_S", "900")))
    parser.add_argument("--max-vram-mb", type=float, default=float(os.environ.get("TALOS_NANOCHAT_MAX_VRAM_MB", "0")))
    parser.add_argument("--min-steps", type=int, default=int(os.environ.get("TALOS_NANOCHAT_MIN_STEPS", "1")))
    parser.add_argument("--seed", type=int, action="append", default=None)
    parser.add_argument("--log", default=os.environ.get("TALOS_NANOCHAT_LOG", "run.log"))
    args = parser.parse_args(argv)

    try:
        proc = subprocess.run(
            args.train_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=args.timeout_s,
        )
    except subprocess.TimeoutExpired as e:
        Path(args.log).write_text((e.stdout or "") + (e.stderr or ""))
        emit(None, "timeout", f"exceeded {args.timeout_s}s", {}, args.seed or [])
        return 0

    output = proc.stdout + proc.stderr
    Path(args.log).write_text(output)
    if proc.returncode != 0:
        emit(None, "crash", output[-500:], {}, args.seed or [])
        return 0

    metrics = parse_summary(output)
    scalar = metrics.get("val_bpb")
    if scalar is None:
        emit(None, "missing_metric", "train output did not contain val_bpb", metrics, args.seed or [])
        return 0
    if math.isnan(scalar) or math.isinf(scalar):
        emit(None, "non_finite_metric", "val_bpb was not finite", metrics, args.seed or [])
        return 0

    if args.min_steps and metrics.get("num_steps", 0) < args.min_steps:
        emit(scalar, "budget_incomplete", f"num_steps < {args.min_steps}", metrics, args.seed or [])
        return 0
    if args.max_vram_mb and metrics.get("peak_vram_mb", 0) > args.max_vram_mb:
        emit(scalar, "vram_limit", f"peak_vram_mb > {args.max_vram_mb}", metrics, args.seed or [])
        return 0

    emit(scalar, None, "", metrics, args.seed or [])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
