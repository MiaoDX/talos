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
from talos.orchestration import factorial_grid   # noqa: E402


def _git(work, *args):
    return run_demo.subprocess.run(["git", *args], cwd=work,
                                   capture_output=True, text=True, check=True)


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


def test_policy_violation_cleans_new_untracked_files_and_records_patch():
    work = run_demo.setup_workdir()

    def add_forbidden_file(workdir):
        (Path(workdir) / "forbidden.txt").write_text("do not keep me\n")

    try:
        out = run_ratchet(work, [Proposal("add forbidden file", add_forbidden_file)],
                          adapter=LocalAdapter(budget_s=30),
                          ledger=TSVLedger(work / "results.tsv"),
                          lower_is_better=True,
                          editable_paths=["solution.py"])
        rows = out["ledger"].rows()
        assert rows[-1]["status"] == "policy_violation", rows[-1]
        assert not (work / "forbidden.txt").exists()
        assert _git(work, "status", "--porcelain").stdout == ""
        patch = (work / rows[-1]["artifact_ref"] / "patch.diff").read_text()
        assert "forbidden.txt" in patch
        assert "do not keep me" in patch
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_proposal_exception_is_recorded_and_worktree_is_reset():
    work = run_demo.setup_workdir()
    head_before = _git(work, "rev-parse", "HEAD").stdout.strip()

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
        head_after = _git(work, "rev-parse", "HEAD").stdout.strip()
        assert head_after == head_before
        assert "boom" in (work / rows[-1]["artifact_ref"] / "error.txt").read_text()
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_proposal_exception_cleans_new_untracked_files():
    work = run_demo.setup_workdir()

    def explode_with_file(workdir):
        (Path(workdir) / "scratch.txt").write_text("temporary\n")
        raise RuntimeError("boom")

    try:
        out = run_ratchet(work, [Proposal("boom with file", explode_with_file)],
                          adapter=LocalAdapter(budget_s=30),
                          ledger=TSVLedger(work / "results.tsv"),
                          lower_is_better=True)
        rows = out["ledger"].rows()
        assert rows[-1]["status"] == "crash", rows[-1]
        assert not (work / "scratch.txt").exists()
        assert _git(work, "status", "--porcelain").stdout == ""
        patch = (work / rows[-1]["artifact_ref"] / "patch.diff").read_text()
        assert "scratch.txt" in patch
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_ratchet_enforces_iteration_cap():
    work = run_demo.setup_workdir()
    calls = []

    def no_change(_workdir):
        calls.append("called")

    try:
        proposals = [Proposal("noop", no_change) for _ in range(3)]
        out = run_ratchet(work, proposals,
                          adapter=LocalAdapter(budget_s=30),
                          ledger=TSVLedger(work / "results.tsv"),
                          lower_is_better=True,
                          max_iterations=2)
        assert len(calls) == 2
        assert [h["status"] for h in out["history"]] == ["baseline", "discard", "discard"]
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_ratchet_requires_clean_experiment_worktree():
    work = run_demo.setup_workdir()
    (work / "dirty.txt").write_text("pre-existing\n")

    try:
        try:
            run_ratchet(work, [],
                        adapter=LocalAdapter(budget_s=30),
                        ledger=TSVLedger(work / "results.tsv"),
                        lower_is_better=True)
        except RuntimeError as e:
            assert "clean experiment worktree" in str(e)
            assert "dirty.txt" in str(e)
        else:
            raise AssertionError("run_ratchet accepted a dirty worktree")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_baseline_evaluator_side_effects_are_reset_before_experiments():
    work = run_demo.setup_workdir()
    evaluator = work / "evaluator.py"
    original = evaluator.read_text()
    evaluator.write_text(
        original.replace(
            "def main():\n",
            "def main():\n    open('solution.py', 'a').write('\\n# evaluator side effect\\n')\n",
            1,
        )
    )
    _git(work, "add", "evaluator.py")
    _git(work, "commit", "-q", "-m", "side-effect evaluator")

    try:
        out = run_ratchet(work, [],
                          adapter=LocalAdapter(budget_s=30),
                          ledger=TSVLedger(work / "results.tsv"),
                          lower_is_better=True)
        assert [h["status"] for h in out["history"]] == ["baseline"]
        assert "# evaluator side effect" not in (work / "solution.py").read_text()
        assert _git(work, "status", "--porcelain").stdout == ""
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_factorial_grid_is_stable_cartesian_product():
    assert factorial_grid({"lr": [0.1, 0.2], "seed": [1, 2]}) == [
        {"lr": 0.1, "seed": 1},
        {"lr": 0.1, "seed": 2},
        {"lr": 0.2, "seed": 1},
        {"lr": 0.2, "seed": 2},
    ]


if __name__ == "__main__":
    test_ratchet_keeps_reverts_and_improves()
    test_veto_row_has_no_metric()
    test_ledger_records_artifacts_and_eval_metadata()
    test_policy_violation_reverts_protected_path_and_records_artifact()
    test_policy_violation_cleans_new_untracked_files_and_records_patch()
    test_proposal_exception_is_recorded_and_worktree_is_reset()
    test_proposal_exception_cleans_new_untracked_files()
    test_ratchet_enforces_iteration_cap()
    test_ratchet_requires_clean_experiment_worktree()
    test_baseline_evaluator_side_effects_are_reset_before_experiments()
    test_factorial_grid_is_stable_cartesian_product()
    print("PASS: ratchet keep/revert/veto + ledger/audit safeguards verified")
