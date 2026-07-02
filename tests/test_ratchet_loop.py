"""End-to-end test of the keep/revert ratchet on the toy task.

Runnable directly (`python tests/test_ratchet_loop.py`) or via pytest.
"""
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "examples" / "ratchet_demo"))

from talos.adapters import LocalAdapter          # noqa: E402
from talos.ledger import TSVLedger               # noqa: E402
from talos.ratchet import Proposal, run_ratchet  # noqa: E402
import run_demo                                  # noqa: E402


def _run():
    work = run_demo.setup_workdir()
    out = run_ratchet(work, run_demo.build_proposals(),
                      adapter=LocalAdapter(budget_s=30),
                      ledger=TSVLedger(work / "results.tsv"),
                      lower_is_better=True)
    rows = out["ledger"].rows()
    shutil.rmtree(work, ignore_errors=True)
    return out, rows


def test_ratchet_keeps_reverts_and_improves():
    out, rows = _run()
    statuses = [r["status"] for r in rows]
    # baseline, then keep (epochs), veto (diverge), keep (standardize)
    assert statuses == ["baseline", "keep", "veto", "keep"], statuses
    baseline_metric = float(rows[0]["metric"])
    assert out["best"] < baseline_metric, (out["best"], baseline_metric)
    assert out["best"] < 1.0, out["best"]   # the structural win is large


def test_veto_row_has_no_metric():
    _, rows = _run()
    veto = [r for r in rows if r["status"] == "veto"][0]
    assert veto["metric"] == "", veto


def test_ledger_records_artifacts_and_eval_metadata():
    _, rows = _run()
    kept = [r for r in rows if r["status"] == "keep"][0]
    assert kept["baseline_commit"], kept
    assert kept["candidate_commit"], kept
    assert kept["evaluator"] == "evaluator.py", kept
    assert kept["evaluator_sha"], kept
    assert kept["artifact_ref"].startswith(".talos/runs/exp-"), kept
    assert kept["seeds"] == "[0]", kept
    assert "val_logloss" in kept["metrics"], kept


def test_policy_violation_reverts_protected_path_and_records_artifact():
    work = run_demo.setup_workdir()
    original_evaluator = (work / "evaluator.py").read_text()

    def edit_evaluator(workdir):
        (Path(workdir) / "evaluator.py").write_text("print('changed')\n")

    try:
        out = run_ratchet(work, [Proposal("edit evaluator", edit_evaluator)],
                          adapter=LocalAdapter(budget_s=30),
                          ledger=TSVLedger(work / "results.tsv"),
                          lower_is_better=True,
                          editable_paths=["solution.py"])
        rows = out["ledger"].rows()
        assert [r["status"] for r in rows] == ["baseline", "policy_violation"], rows
        assert "protected path changed: evaluator.py" in rows[-1]["description"], rows[-1]
        assert (work / "evaluator.py").read_text() == original_evaluator
        artifact = work / rows[-1]["artifact_ref"] / "patch.diff"
        assert artifact.exists(), rows[-1]
        assert "evaluator.py" in artifact.read_text()
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_proposal_exception_is_recorded_and_worktree_is_reset():
    work = run_demo.setup_workdir()
    head_before = run_demo.subprocess.run(["git", "rev-parse", "HEAD"], cwd=work,
                                          capture_output=True, text=True,
                                          check=True).stdout.strip()

    def explode(workdir):
        (Path(workdir) / "solution.py").write_text("broken")
        raise RuntimeError("boom")

    try:
        out = run_ratchet(work, [Proposal("boom", explode)],
                          adapter=LocalAdapter(budget_s=30),
                          ledger=TSVLedger(work / "results.tsv"),
                          lower_is_better=True)
        rows = out["ledger"].rows()
        assert rows[-1]["status"] == "crash", rows[-1]
        head_after = run_demo.subprocess.run(["git", "rev-parse", "HEAD"], cwd=work,
                                             capture_output=True, text=True,
                                             check=True).stdout.strip()
        assert head_after == head_before
        assert "boom" in (work / rows[-1]["artifact_ref"] / "error.txt").read_text()
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    test_ratchet_keeps_reverts_and_improves()
    test_veto_row_has_no_metric()
    test_ledger_records_artifacts_and_eval_metadata()
    test_policy_violation_reverts_protected_path_and_records_artifact()
    test_proposal_exception_is_recorded_and_worktree_is_reset()
    print("PASS: ratchet keep/revert/veto + ledger/audit safeguards verified")
