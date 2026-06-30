"""FROZEN reference evaluator for the toy task.

Owns the dataset, the train/val split, and the scoring metric. The agent edits
only `solution.py` and never sees the validation set. Emits a contract-conformant
JSON EvalResult on stdout. Pure-Python, deterministic (fixed seed).

Scalar: validation log-loss (lower is better).
Veto:   `divergence` if predictions/loss are non-finite, or the solution crashes.
"""
import json
import math
import random

SEED = 0
N = 600
SCALE_X2 = 100.0  # features live on very different scales (standardization matters)


def make_data(seed: int):
    rng = random.Random(seed)
    X, y = [], []
    for _ in range(N):
        x1 = rng.gauss(0, 1)
        x2 = rng.gauss(0, 1)
        logit = 2.0 * x1 + 1.5 * x2 - 0.5
        p = 1.0 / (1.0 + math.exp(-logit))
        label = 1 if rng.random() < p else 0
        X.append([x1, x2 * SCALE_X2])   # corrupt the scale of feature 2
        y.append(label)
    return X, y


def split(X, y):
    n_val = N // 3
    return X[n_val:], y[n_val:], X[:n_val], y[:n_val]


def log_loss(probs, y):
    eps = 1e-12
    total = 0.0
    for p, t in zip(probs, y):
        p = min(max(p, eps), 1 - eps)
        total += -(t * math.log(p) + (1 - t) * math.log(1 - p))
    return total / len(y)


def emit(scalar, veto_triggered, detail, metrics):
    # Keep the wire format portable: non-finite -> null (the veto carries the signal).
    if scalar != scalar or scalar in (float("inf"), float("-inf")):
        scalar = None
    print(json.dumps({
        "scalar": scalar,
        "vetoes": [{"name": "divergence", "triggered": bool(veto_triggered), "detail": detail}],
        "metrics": metrics,
        "seeds": [SEED],
        "lower_is_better": True,
    }))


def main():
    X, y = make_data(SEED)
    Xtr, ytr, Xval, yval = split(X, y)
    try:
        import solution  # the agent-editable file, imported from the cwd
        predict = solution.build_and_train([r[:] for r in Xtr], list(ytr))
        probs = list(predict([r[:] for r in Xval]))
    except Exception as e:  # a crash is a (vetoed) failed experiment, not a hang
        emit(float("inf"), True, f"crash: {type(e).__name__}: {e}", {})
        return

    bad = any((p != p) or p in (float("inf"), float("-inf")) for p in probs)
    loss = float("inf") if bad else log_loss(probs, yval)
    if loss != loss or loss == float("inf"):
        bad = True
        loss = float("inf")
    emit(loss if not bad else float("inf"), bad,
         "non-finite predictions or loss" if bad else "",
         {"val_logloss": None if bad else loss})


if __name__ == "__main__":
    main()
