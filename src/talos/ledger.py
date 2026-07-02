"""L1 — the experiment ledger.

An append-only TSV: the agent's cross-run memory and the human audit trail. Git
stores code states and rollback points; the ledger stores structured experiment
facts for every attempt.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

COLUMNS = [
    "ts",
    "experiment",
    "commit",
    "metric",
    "delta",
    "status",
    "description",
    "baseline_commit",
    "candidate_commit",
    "evaluator",
    "evaluator_sha",
    "seeds",
    "vetoes",
    "metrics",
    "artifact_ref",
]


def _fmt_number(value: Any) -> str:
    if value is None:
        return ""
    return f"{value:.6g}"


def _fmt_delta(value: Any) -> str:
    if value is None:
        return ""
    return f"{value:+.6g}"


def _fmt_json(value: Any) -> str:
    if value in (None, ""):
        return ""
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _cell(value: Any) -> str:
    return str(value).replace("\t", " ").replace("\n", " ")


class TSVLedger:
    def __init__(self, path):
        self.path = Path(path)
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text("\t".join(COLUMNS) + "\n")

    def append(self, experiment, commit, metric, delta, status, description, *,
               baseline_commit="", candidate_commit="", evaluator="",
               evaluator_sha="", seeds=None, vetoes=None, metrics=None,
               artifact_ref=""):
        row = [
            time.strftime("%Y-%m-%dT%H:%M:%S"),
            experiment,
            str(commit)[:10] if commit else "",
            _fmt_number(metric),
            _fmt_delta(delta),
            status,
            description,
            str(baseline_commit)[:10] if baseline_commit else "",
            str(candidate_commit)[:10] if candidate_commit else "",
            evaluator,
            evaluator_sha,
            _fmt_json(seeds),
            _fmt_json(vetoes),
            _fmt_json(metrics),
            artifact_ref,
        ]
        with self.path.open("a") as f:
            f.write("\t".join(_cell(v) for v in row) + "\n")

    def rows(self):
        rows = []
        for ln in self.path.read_text().splitlines()[1:]:
            if not ln.strip():
                continue
            cells = ln.split("\t")
            if len(cells) < len(COLUMNS):
                cells.extend([""] * (len(COLUMNS) - len(cells)))
            rows.append(dict(zip(COLUMNS, cells)))
        return rows
