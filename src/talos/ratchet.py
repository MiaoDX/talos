"""The keep/revert ratchet — the engine behind the `ratchet-experiment` skill.

`workdir` is a git repo whose current commit is the baseline. For each proposal:
edit files -> commit -> evaluate (L0) -> keep (leave the commit) if it improves the
frozen metric (L2), else reset to the pre-experiment commit. Every step is logged
to the append-only ledger (L1), including policy violations and crashes.

In production the *proposals* are made by a coding agent (Claude Code / Codex)
editing the sandbox file; here a `Proposal.apply` callable stands in so the loop
is testable without an LLM.
"""
from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass
from itertools import islice
from pathlib import Path
from typing import Callable, Optional

from .adapters.local import LocalAdapter
from .contract import EvalResult, Veto, is_improvement
from .ledger import TSVLedger


@dataclass
class Proposal:
    description: str
    apply: Callable[[Path], None]   # mutate files in the workdir


def _git(workdir, *args):
    return subprocess.run(["git", *args], cwd=str(workdir),
                          capture_output=True, text=True, check=True)


def _head(workdir) -> str:
    return _git(workdir, "rev-parse", "HEAD").stdout.strip()


def _rel_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _evaluator_rel(evaluator: str, workdir: Path) -> str:
    path = Path(evaluator)
    if path.is_absolute():
        try:
            return path.resolve().relative_to(workdir.resolve()).as_posix()
        except ValueError:
            return ""
    return path.as_posix()


def _blob_sha(workdir: Path, relpath: str) -> str:
    if not relpath:
        return ""
    try:
        return _git(workdir, "rev-parse", f"HEAD:{relpath}").stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def _exclude_path(workdir: Path, path: Path):
    """Keep ledger/artifacts untracked so `git add -A` and reset never touch them."""
    try:
        rel = path.resolve().relative_to(workdir.resolve())
    except ValueError:
        return  # path lives outside the workdir; nothing to exclude
    exclude = workdir / ".git" / "info" / "exclude"
    if exclude.parent.exists():
        existing = exclude.read_text() if exclude.exists() else ""
        if rel.as_posix() not in existing.split():
            with exclude.open("a") as f:
                f.write(f"\n{rel.as_posix()}\n")


def _changed_paths(workdir: Path) -> set[str]:
    paths: set[str] = set()
    for line in _git(workdir, "status", "--porcelain").stdout.splitlines():
        if not line:
            continue
        raw = line[3:]
        # Rename lines look like "old -> new"; protect both sides.
        for part in raw.split(" -> "):
            part = part.strip()
            if part and not (part == "__pycache__" or part.startswith("__pycache__/")):
                paths.add(part)
    return paths


def _untracked_paths(workdir: Path) -> set[str]:
    paths: set[str] = set()
    for line in _git(workdir, "status", "--porcelain").stdout.splitlines():
        if line.startswith("?? "):
            path = line[3:].strip()
            if path:
                paths.add(path)
    return paths


def _clean_untracked(workdir: Path, paths: set[str]):
    """Remove only the untracked paths created by this experiment attempt."""
    for path in sorted(paths):
        if not path or path.startswith(".git/"):
            continue
        _git(workdir, "clean", "-fd", "--", path)


def _candidate_patch(workdir: Path, base: str, untracked_paths: set[str]) -> str:
    if untracked_paths:
        _git(workdir, "add", "-N", "--", *sorted(untracked_paths))
    return _git(workdir, "diff", "--binary", base).stdout


def _matches(path: str, roots: set[str]) -> bool:
    path = path.strip("/")
    return any(path == root or path.startswith(root.rstrip("/") + "/") for root in roots)


def _policy_violation(changed: set[str], *, editable_paths: Optional[set[str]],
                      protected_paths: set[str]) -> str | None:
    for path in sorted(changed):
        if _matches(path, protected_paths):
            return f"protected path changed: {path}"
        if editable_paths is not None and not _matches(path, editable_paths):
            return f"outside editable paths: {path}"
    return None


def _save_artifact(workdir: Path, artifact_root: Optional[Path], run_id: str, *,
                   patch: str = "", result: Optional[EvalResult] = None,
                   error: str = "") -> str:
    if artifact_root is None:
        return ""
    run_dir = artifact_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    if patch:
        (run_dir / "patch.diff").write_text(patch)
    if result is not None:
        (run_dir / "eval_result.json").write_text(result.to_json() + "\n")
    if error:
        (run_dir / "error.txt").write_text(error + "\n")
    return _rel_path(run_dir, workdir)


def _reset_to(workdir: Path, sha: str, *, clean_paths: Optional[set[str]] = None):
    _git(workdir, "reset", "--hard", "-q", sha)
    if clean_paths:
        _clean_untracked(workdir, clean_paths)


def _veto_dicts(result: Optional[EvalResult]):
    if result is None:
        return None
    return [asdict(v) for v in result.vetoes]


def _with_veto(result: EvalResult, name: str, detail: str) -> EvalResult:
    result.vetoes = list(result.vetoes) + [Veto(name, True, detail)]
    return result


def run_ratchet(workdir, proposals, *, evaluator: str = "evaluator.py",
                adapter: Optional[LocalAdapter] = None,
                ledger: Optional[TSVLedger] = None,
                lower_is_better: Optional[bool] = None,
                editable_paths: Optional[list[str]] = None,
                protected_paths: Optional[list[str]] = None,
                artifact_dir: Optional[str | Path] = None,
                max_iterations: Optional[int] = 25):
    workdir = Path(workdir)
    adapter = adapter or LocalAdapter()
    ledger = ledger or TSVLedger(workdir / "results.tsv")
    artifact_root = Path(artifact_dir) if artifact_dir is not None else workdir / ".talos" / "runs"
    if not artifact_root.is_absolute():
        artifact_root = workdir / artifact_root
    _exclude_path(workdir, ledger.path)
    _exclude_path(workdir, artifact_root)

    evaluator_rel = _evaluator_rel(evaluator, workdir)
    protected = {p.strip("/") for p in (protected_paths or []) if p}
    protected.update({"program.md"})
    if evaluator_rel:
        protected.add(evaluator_rel.strip("/"))
    editable = {p.strip("/") for p in editable_paths} if editable_paths is not None else None
    if max_iterations is not None and max_iterations < 1:
        raise ValueError("max_iterations must be >= 1 or None")

    dirty = _changed_paths(workdir)
    if dirty:
        raise RuntimeError(
            "run_ratchet requires a clean experiment worktree; dirty paths: "
            + ", ".join(sorted(dirty)[:10]))

    baseline_sha = _head(workdir)
    evaluator_sha = _blob_sha(workdir, evaluator_rel)
    baseline_untracked = _untracked_paths(workdir)
    base = adapter.run(evaluator, workdir)
    _reset_to(workdir, baseline_sha,
              clean_paths=_untracked_paths(workdir) - baseline_untracked)
    direction = base.lower_is_better if lower_is_better is None else lower_is_better
    if base.lower_is_better != direction:
        base = _with_veto(
            base, "direction_mismatch",
            f"baseline emitted lower_is_better={base.lower_is_better}, expected {direction}")
    best = base.scalar if not base.vetoed and base.scalar is not None \
        else (float("inf") if direction else float("-inf"))
    ledger.append("baseline", baseline_sha, base.scalar, None,
                  "baseline" if not base.vetoed else "veto", "initial state",
                  baseline_commit=baseline_sha, candidate_commit=baseline_sha,
                  evaluator=evaluator_rel, evaluator_sha=evaluator_sha,
                  seeds=base.seeds, vetoes=_veto_dicts(base), metrics=base.metrics)
    history = [{"experiment": "baseline", "result": base, "status": "baseline"}]

    proposal_iter = proposals if max_iterations is None else islice(proposals, max_iterations)
    for i, p in enumerate(proposal_iter, 1):
        run_id = f"exp-{i:04d}"
        pre_head = _head(workdir)
        pre_existing_untracked = _untracked_paths(workdir)
        candidate_sha = ""
        patch = ""
        res: Optional[EvalResult] = None
        try:
            p.apply(workdir)
            changed = _changed_paths(workdir)
            if not changed:
                artifact_ref = _save_artifact(workdir, artifact_root, run_id)
                ledger.append(i, pre_head, None, None, "discard",
                              f"{p.description} [no file changes]",
                              baseline_commit=pre_head, evaluator=evaluator_rel,
                              evaluator_sha=evaluator_sha, artifact_ref=artifact_ref)
                history.append({"experiment": i, "result": None, "status": "discard"})
                continue
            violation = _policy_violation(changed, editable_paths=editable, protected_paths=protected)
            if violation:
                clean_paths = _untracked_paths(workdir) - pre_existing_untracked
                patch = _candidate_patch(workdir, "HEAD", clean_paths)
                artifact_ref = _save_artifact(workdir, artifact_root, run_id,
                                              patch=patch, error=violation)
                _reset_to(workdir, pre_head, clean_paths=clean_paths)
                ledger.append(i, pre_head, None, None, "policy_violation",
                              f"{p.description} [{violation}]",
                              baseline_commit=pre_head, evaluator=evaluator_rel,
                              evaluator_sha=evaluator_sha, artifact_ref=artifact_ref)
                history.append({"experiment": i, "result": None,
                                "status": "policy_violation"})
                continue

            _git(workdir, "add", "-A")
            _git(workdir, "commit", "-q", "-m", f"exp {i}: {p.description}")
            candidate_sha = _head(workdir)
            patch = _git(workdir, "show", "--format=", "--binary", candidate_sha).stdout
            res = adapter.run(evaluator, workdir)
            if res.lower_is_better != direction:
                res = _with_veto(
                    res, "direction_mismatch",
                    f"candidate emitted lower_is_better={res.lower_is_better}, expected {direction}")
            artifact_ref = _save_artifact(workdir, artifact_root, run_id,
                                          patch=patch, result=res)
            post_eval_untracked = _untracked_paths(workdir) - pre_existing_untracked
            if is_improvement(res, best, direction):
                delta = res.scalar - best
                best = res.scalar
                status = "keep"
                _reset_to(workdir, candidate_sha, clean_paths=post_eval_untracked)
            else:
                # Revert the candidate commit and any evaluator side effects.
                _reset_to(workdir, pre_head, clean_paths=post_eval_untracked)
                delta = None
                status = "veto" if res.vetoed else "revert"
            ledger.append(i, candidate_sha, res.scalar, delta, status, p.description,
                          baseline_commit=pre_head, candidate_commit=candidate_sha,
                          evaluator=evaluator_rel, evaluator_sha=evaluator_sha,
                          seeds=res.seeds, vetoes=_veto_dicts(res), metrics=res.metrics,
                          artifact_ref=artifact_ref)
            history.append({"experiment": i, "result": res, "status": status})
        except Exception as e:
            try:
                clean_paths = _untracked_paths(workdir) - pre_existing_untracked
                if not patch:
                    patch = _candidate_patch(workdir, pre_head, clean_paths)
                _reset_to(workdir, pre_head, clean_paths=clean_paths)
            except Exception:
                pass
            artifact_ref = _save_artifact(workdir, artifact_root, run_id,
                                          patch=patch, result=res, error=str(e)[:500])
            ledger.append(i, candidate_sha or pre_head, None, None, "crash",
                          f"{p.description} [error: {type(e).__name__}: {e}]",
                          baseline_commit=pre_head, candidate_commit=candidate_sha,
                          evaluator=evaluator_rel, evaluator_sha=evaluator_sha,
                          seeds=getattr(res, "seeds", None), vetoes=_veto_dicts(res),
                          metrics=getattr(res, "metrics", None), artifact_ref=artifact_ref)
            history.append({"experiment": i, "result": res, "status": "crash"})

    return {"best": best, "ledger": ledger, "history": history}
