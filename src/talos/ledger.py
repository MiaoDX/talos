"""L1 — the experiment ledger.

An append-only TSV: the agent's cross-run memory and the human audit trail. By
convention it is NOT tracked by git (so keep/revert can never clobber it), mirroring
autoresearch's untracked `results.tsv`.
"""
from __future__ import annotations

import time
from pathlib import Path

COLUMNS = ["ts", "experiment", "commit", "metric", "delta", "status", "description"]


class TSVLedger:
    def __init__(self, path):
        self.path = Path(path)
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text("\t".join(COLUMNS) + "\n")

    def append(self, experiment, commit, metric, delta, status, description):
        metric_s = "" if metric is None else f"{metric:.6g}"
        delta_s = "" if delta is None else f"{delta:+.6g}"
        row = [time.strftime("%Y-%m-%dT%H:%M:%S"), str(experiment), str(commit)[:10],
               metric_s, delta_s, status,
               str(description).replace("\t", " ").replace("\n", " ")]
        with self.path.open("a") as f:
            f.write("\t".join(row) + "\n")

    def rows(self):
        lines = self.path.read_text().splitlines()[1:]
        return [dict(zip(COLUMNS, ln.split("\t"))) for ln in lines if ln.strip()]
