"""AGENT-EDITABLE sandbox.

Build and train a classifier on (X, y); return a predict(X) -> list of P(y=1).
Everything here is fair game: hyperparameters, features, model structure. The
evaluator owns the dataset split and the metric — you cannot change those.

Baseline: plain logistic regression via full-batch gradient descent. (Note the
features are on very different scales; this baseline does not handle that.)
"""
import math

LR = 0.1
EPOCHS = 50


def build_and_train(X, y):
    n = len(X[0])
    w = [0.0] * n
    b = 0.0
    m = len(X)
    for _ in range(EPOCHS):
        gw = [0.0] * n
        gb = 0.0
        for xi, yi in zip(X, y):
            z = b + sum(wj * xij for wj, xij in zip(w, xi))
            z = max(min(z, 50.0), -50.0)
            p = 1.0 / (1.0 + math.exp(-z))
            err = p - yi
            for j in range(n):
                gw[j] += err * xi[j]
            gb += err
        for j in range(n):
            w[j] -= LR * gw[j] / m
        b -= LR * gb / m

    def predict(Xte):
        out = []
        for xi in Xte:
            z = b + sum(wj * xij for wj, xij in zip(w, xi))
            z = max(min(z, 50.0), -50.0)
            out.append(1.0 / (1.0 + math.exp(-z)))
        return out

    return predict
