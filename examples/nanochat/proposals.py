"""Scripted proposal helpers for the nanochat release demo.

They mutate only `train.py`, matching the upstream autoresearch ownership
contract. The first release run should start with scripted edits before live
agent-generated proposals are trusted.
"""
from __future__ import annotations

import re
from pathlib import Path

from talos.ratchet import Proposal


def _replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"pattern not found: {old}")
    return text.replace(old, new, 1)


def _replace_assignment_int(text: str, name: str, new_value: int) -> str:
    pattern = re.compile(rf"^({name}\s*=\s*)\d+(\s*(?:#.*)?)$", re.MULTILINE)
    if not pattern.search(text):
        raise ValueError(f"assignment not found: {name}")
    return pattern.sub(rf"\g<1>{new_value}\2", text, count=1)


def _edit_train(transform):
    def _apply(workdir):
        path = Path(workdir) / "train.py"
        path.write_text(transform(path.read_text()))
    return _apply


def build_smoke_proposals() -> list[Proposal]:
    """Conservative first edits that exercise keep/revert on real training code."""
    return [
        Proposal(
            "smoke: reduce DEPTH for a smaller model",
            _edit_train(lambda s: _replace_assignment_int(s, "DEPTH", 3)),
        ),
        Proposal(
            "smoke: simplify attention window pattern",
            _edit_train(lambda s: _replace_once(
                s,
                'WINDOW_PATTERN = "SSSL"',
                'WINDOW_PATTERN = "L"',
            )),
        ),
    ]
