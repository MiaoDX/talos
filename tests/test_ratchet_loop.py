"""End-to-end tests for the ratchet loop and standalone demo surfaces."""
import shutil
import sys
import subprocess
import hashlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "examples" / "ratchet_demo"))
sys.path.insert(0, str(REPO / "examples" / "nanochat"))

from talos.adapters import ExecutionAdapter       # noqa: E402
from talos.adapters import LocalAdapter          # noqa: E402
from talos.adapters import SkyPilotAdapter       # noqa: E402
from talos.ledger import TSVLedger               # noqa: E402
from talos.ratchet import Proposal, run_ratchet  # noqa: E402
import run_demo                                  # noqa: E402
from talos.orchestration import factorial_grid   # noqa: E402
import evaluator as nanochat_evaluator           # noqa: E402
import proposals as nanochat_proposals           # noqa: E402
import skypilot_local_k8s_smoke                  # noqa: E402
import skypilot_ssh_smoke                        # noqa: E402


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


def test_local_adapter_satisfies_execution_adapter_protocol():
    assert isinstance(LocalAdapter(), ExecutionAdapter)


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


def test_external_evaluator_records_path_and_file_hash(tmp_path):
    work = run_demo.setup_workdir()
    evaluator = tmp_path / "external_evaluator.py"
    evaluator.write_text((work / "evaluator.py").read_text())

    try:
        out = run_ratchet(work, [],
                          evaluator=str(evaluator),
                          adapter=LocalAdapter(budget_s=30),
                          ledger=TSVLedger(work / "results.tsv"),
                          lower_is_better=True)
        rows = out["ledger"].rows()
        assert rows[0]["evaluator"] == str(evaluator)
        assert rows[0]["evaluator_sha"] == hashlib.sha256(evaluator.read_bytes()).hexdigest()
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_factorial_grid_is_stable_cartesian_product():
    assert factorial_grid({"lr": [0.1, 0.2], "seed": [1, 2]}) == [
        {"lr": 0.1, "seed": 1},
        {"lr": 0.1, "seed": 2},
        {"lr": 0.2, "seed": 1},
        {"lr": 0.2, "seed": 2},
    ]


def test_skypilot_adapter_generates_ssh_node_pool_task_yaml():
    adapter = SkyPilotAdapter(
        infra="ssh/rtx3090",
        accelerators="RTX3090:1",
        setup="uv sync",
        python="uv run python",
        cluster_name="talos-rtx3090",
    )
    yaml = adapter.task_yaml("examples/nanochat/evaluator.py")
    assert "infra: ssh/rtx3090" in yaml
    assert "accelerators: RTX3090:1" in yaml
    assert "uv run python examples/nanochat/evaluator.py" in yaml
    assert adapter.launch_command("task.yaml") == [
        "sky", "launch", "-y", "--cluster", "talos-rtx3090", "task.yaml"
    ]


def test_nanochat_skypilot_helpers_generate_manual_task_shapes():
    ssh = skypilot_ssh_smoke.build_adapter("rtx3090", "RTX3090:1", 10)
    ssh_yaml = ssh.task_yaml("talos_nanochat_evaluator.py")
    assert "infra: ssh/rtx3090" in ssh_yaml
    assert "setup: |\n  uv sync\n  uv run prepare.py --num-shards 1 --download-workers 2\nrun: |" in ssh_yaml
    local_k8s = skypilot_local_k8s_smoke.build_adapter(None, 10)
    yaml = local_k8s.task_yaml("talos_nanochat_evaluator.py")
    assert "infra: k8s" in yaml
    assert "accelerators:" not in yaml


def test_skypilot_adapter_parses_evalresult_from_runner(monkeypatch, tmp_path):
    monkeypatch.setattr("talos.adapters.skypilot.shutil.which", lambda _: "/usr/bin/sky")
    calls = []

    def runner(cmd, cwd, timeout):
        calls.append((cmd, cwd, timeout))
        assert "infra: ssh/gpu" in (cwd / ".talos-skypilot-task.yaml").read_text()
        return subprocess.CompletedProcess(
            cmd, 0, stdout='log\n{"scalar":0.42,"vetoes":[],"metrics":{"val_bpb":0.42},"seeds":[7],"lower_is_better":true}\n',
            stderr="",
        )

    adapter = SkyPilotAdapter(
        infra="ssh/gpu",
        accelerators="L4:1",
        budget_s=12,
        cluster_name="talos-gpu",
        runner=runner,
    )
    result = adapter.run("evaluator.py", tmp_path)
    assert result.scalar == 0.42
    assert result.metrics == {"val_bpb": 0.42}
    assert result.seeds == [7]
    assert calls[0] == (
        ["sky", "launch", "-y", "--cluster", "talos-gpu", ".talos-skypilot-task.yaml"],
        tmp_path,
        12,
    )
    assert not (tmp_path / ".talos-skypilot-task.yaml").exists()


def test_skypilot_adapter_finds_json_before_trailing_sky_status(monkeypatch, tmp_path):
    monkeypatch.setattr("talos.adapters.skypilot.shutil.which", lambda _: "/usr/bin/sky")

    def runner(cmd, cwd, timeout):
        return subprocess.CompletedProcess(
            cmd, 0,
            stdout=(
                "\x1b[36m(task)\x1b[0m "
                '{"scalar":0.5,"vetoes":[],"metrics":{"val_bpb":0.5},'
                '"seeds":[],"lower_is_better":true}\n'
                "\x1b[32m✓ Job finished (status: SUCCEEDED).\x1b[0m\n"
            ),
            stderr="",
        )

    result = SkyPilotAdapter(runner=runner).run("evaluator.py", tmp_path)
    assert result.scalar == 0.5
    assert result.metrics == {"val_bpb": 0.5}


def test_skypilot_adapter_maps_missing_cli_to_veto(monkeypatch, tmp_path):
    monkeypatch.setattr("talos.adapters.skypilot.shutil.which", lambda _: None)
    result = SkyPilotAdapter().run("evaluator.py", tmp_path)
    assert result.vetoed
    assert result.vetoes[0].name == "skypilot_missing"


def test_nanochat_evaluator_parses_summary_and_emits_contract(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cmd = (
        "python -c \"print('---'); "
        "print('val_bpb:          0.997900'); "
        "print('peak_vram_mb:     1000.0'); "
        "print('num_steps:        12')\""
    )
    assert nanochat_evaluator.main([
        "--train-cmd", cmd,
        "--timeout-s", "5",
        "--min-steps", "10",
        "--seed", "123",
    ]) == 0
    result = nanochat_evaluator.json.loads(capsys.readouterr().out)
    assert result["scalar"] == 0.9979
    assert result["vetoes"] == []
    assert result["metrics"]["peak_vram_mb"] == 1000.0
    assert result["seeds"] == [123]
    assert (tmp_path / "run.log").exists()


def test_nanochat_evaluator_vetoes_missing_metric(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert nanochat_evaluator.main([
        "--train-cmd", "python -c \"print('no metric here')\"",
        "--timeout-s", "5",
    ]) == 0
    result = nanochat_evaluator.json.loads(capsys.readouterr().out)
    assert result["scalar"] is None
    assert result["vetoes"][0]["name"] == "missing_metric"


def test_nanochat_smoke_proposals_mutate_only_train_file(tmp_path):
    train = tmp_path / "train.py"
    train.write_text('WINDOW_PATTERN = "SSSL"\nDEPTH = 4\nDEVICE_BATCH_SIZE = 16\n')
    proposals = nanochat_proposals.build_smoke_proposals()
    proposals[0].apply(tmp_path)
    assert "DEPTH = 3" in train.read_text()
    proposals[1].apply(tmp_path)
    text = train.read_text()
    assert 'WINDOW_PATTERN = "L"' in text
    assert sorted(p.name for p in tmp_path.iterdir()) == ["train.py"]
