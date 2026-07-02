"""Talos: an eval-driven, domain-transferable AutoResearch framework.

Reference core (pure-Python):
- contract:  L2 eval contract (EvalResult, Veto, is_improvement)
- ledger:    L1 append-only experiment ledger
- adapters:  L0 execution adapters (local subprocess; skypilot task/result path)
- ratchet:   the keep/revert loop engine used by the ratchet-experiment skill
"""
from .contract import Veto, EvalResult, is_improvement  # noqa: F401

__version__ = "0.0.0"
