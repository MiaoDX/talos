"""CPU-only, seconds-to-run demo of the keep/revert ratchet on the toy_mlp task.

It drives three scripted proposals through a throwaway git repo:
  1. tune EPOCHS 50->400      (numeric)     -> small improvement, KEEP
  2. tune LR 0.1->50          (diverges)    -> non-finite -> VETO -> revert
  3. standardize features     (structural)  -> large improvement, KEEP (best)

In production these proposals come from a coding agent (Claude Code / Codex)
editing solution.py; scripting them here lets the loop run without an LLM so the
mechanism (propose -> run -> score -> keep/revert -> ledger) is verifiable.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from talos.adapters import LocalAdapter          # noqa: E402
from talos.ledger import TSVLedger               # noqa: E402
from talos.ratchet import Proposal, run_ratchet   # noqa: E402

TOY = REPO / "constraints" / "examples" / "toy_mlp"

A_EPOCHS = '''import math
LR = 0.1
EPOCHS = 400

def build_and_train(X, y):
    n = len(X[0]); w = [0.0]*n; b = 0.0; m = len(X)
    for _ in range(EPOCHS):
        gw = [0.0]*n; gb = 0.0
        for xi, yi in zip(X, y):
            z = max(min(b + sum(wj*xij for wj, xij in zip(w, xi)), 50.0), -50.0)
            p = 1.0/(1.0+math.exp(-z)); err = p - yi
            for j in range(n): gw[j] += err*xi[j]
            gb += err
        for j in range(n): w[j] -= LR*gw[j]/m
        b -= LR*gb/m
    def predict(Xte):
        o = []
        for xi in Xte:
            z = max(min(b + sum(wj*xij for wj, xij in zip(w, xi)), 50.0), -50.0)
            o.append(1.0/(1.0+math.exp(-z)))
        return o
    return predict
'''

B_DIVERGE = '''import math
LR = 50.0
EPOCHS = 50

def build_and_train(X, y):
    n = len(X[0]); w = [0.0]*n; b = 0.0; m = len(X)
    for _ in range(EPOCHS):
        gw = [0.0]*n; gb = 0.0
        for xi, yi in zip(X, y):
            z = b + sum(wj*xij for wj, xij in zip(w, xi))   # no clamp -> overflow
            p = 1.0/(1.0+math.exp(-z)); err = p - yi
            for j in range(n): gw[j] += err*xi[j]
            gb += err
        for j in range(n): w[j] -= LR*gw[j]/m
        b -= LR*gb/m
    def predict(Xte):
        return [1.0/(1.0+math.exp(-(b+sum(wj*xij for wj, xij in zip(w, xi))))) for xi in Xte]
    return predict
'''

C_STANDARDIZE = '''import math
LR = 0.1
EPOCHS = 50

def build_and_train(X, y):
    n = len(X[0]); m = len(X)
    mean = [sum(r[j] for r in X)/m for j in range(n)]
    var = [sum((r[j]-mean[j])**2 for r in X)/m for j in range(n)]
    std = [(v**0.5) or 1.0 for v in var]
    def norm(r): return [(r[j]-mean[j])/std[j] for j in range(n)]
    Xs = [norm(r) for r in X]
    w = [0.0]*n; b = 0.0
    for _ in range(EPOCHS):
        gw = [0.0]*n; gb = 0.0
        for xi, yi in zip(Xs, y):
            z = max(min(b + sum(wj*xij for wj, xij in zip(w, xi)), 50.0), -50.0)
            p = 1.0/(1.0+math.exp(-z)); err = p - yi
            for j in range(n): gw[j] += err*xi[j]
            gb += err
        for j in range(n): w[j] -= LR*gw[j]/m
        b -= LR*gb/m
    def predict(Xte):
        o = []
        for r in Xte:
            xi = norm(r)
            z = max(min(b + sum(wj*xij for wj, xij in zip(w, xi)), 50.0), -50.0)
            o.append(1.0/(1.0+math.exp(-z)))
        return o
    return predict
'''


def _write_solution(text):
    def _apply(workdir):
        (Path(workdir) / "solution.py").write_text(text)
    return _apply


def setup_workdir() -> Path:
    """Create a throwaway git repo with the frozen evaluator + baseline solution."""
    work = Path(tempfile.mkdtemp(prefix="talos_ratchet_"))
    for f in ("evaluator.py", "solution.py", "program.md"):
        shutil.copy(TOY / f, work / f)
    (work / ".gitignore").write_text("results.tsv\n__pycache__/\n*.pyc\n.talos/\n")
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=work, check=True)
    subprocess.run(["git", "config", "user.email", "demo@talos"], cwd=work, check=True)
    subprocess.run(["git", "config", "user.name", "talos-demo"], cwd=work, check=True)
    subprocess.run(["git", "add", "-A"], cwd=work, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "baseline"], cwd=work, check=True)
    return work


def build_proposals():
    return [
        Proposal("tune: EPOCHS 50->400", _write_solution(A_EPOCHS)),
        Proposal("tune: LR 0.1->50 (diverges)", _write_solution(B_DIVERGE)),
        Proposal("structural: standardize features", _write_solution(C_STANDARDIZE)),
    ]


def main():
    work = setup_workdir()
    try:
        out = run_ratchet(
            work, build_proposals(),
            adapter=LocalAdapter(budget_s=30),
            ledger=TSVLedger(work / "results.tsv"),
            lower_is_better=True,
        )
        print("=== ledger (results.tsv) ===")
        print((work / "results.tsv").read_text())
        print(f"best val_logloss = {out['best']:.4f}")
        print("git log (kept lineage):")
        print(subprocess.run(["git", "log", "--oneline"], cwd=work,
                             capture_output=True, text=True).stdout)
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
