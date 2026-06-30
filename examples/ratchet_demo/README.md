# ratchet_demo — a runnable CPU keep/revert loop

Drives the `ratchet-experiment` engine over the frozen `toy_mlp` evaluator with
three scripted proposals (a numeric keep, a diverging veto, a structural keep).
Runs in seconds on CPU, no GPU and no third-party dependencies.

```bash
python examples/ratchet_demo/run_demo.py
```

You should see the ledger record `keep`, `veto`, `keep`, the kept git lineage, and
the best validation log-loss dropping sharply once feature standardization lands.

This proves the **mechanism** (propose → run → score → keep/revert → ledger). In
real use the proposals come from a coding agent editing `solution.py`; the loop is
the same. For the GPU reference task, see [`../nanochat/`](../nanochat/).
