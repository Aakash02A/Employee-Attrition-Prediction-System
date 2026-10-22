"""Evaluation utilities for imbalanced binary classification."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import (accuracy_score, average_precision_score, brier_score_loss,
                             classification_report, confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score)


def choose_threshold(y_true, probabilities) -> tuple[float, dict[str, float]]:
    """Choose the validation threshold maximizing F1; ties prefer recall, then 0.5 proximity."""
    y = np.asarray(y_true, dtype=int)
    p = np.asarray(probabilities, dtype=float)
    candidates = np.unique(np.concatenate(([0.05, 0.5, 0.95], p[(p >= 0.05) & (p <= 0.95)])))
    scored = []
    for threshold in candidates:
        pred = (p >= threshold).astype(int)
        precision = precision_score(y, pred, zero_division=0)
        recall = recall_score(y, pred, zero_division=0)
        f1 = f1_score(y, pred, zero_division=0)
        scored.append((f1, recall, -abs(float(threshold) - 0.5), float(threshold), precision))
    best = max(scored)
    threshold = best[3]
    return threshold, {"precision": float(best[4]), "recall": float(best[1]), "f1": float(best[0])}


def binary_metrics(y_true, probabilities, threshold: float) -> dict:
    y = np.asarray(y_true, dtype=int)
    p = np.asarray(probabilities, dtype=float)
    pred = (p >= threshold).astype(int)
    matrix = confusion_matrix(y, pred, labels=[0, 1])
    return {
        "accuracy": float(accuracy_score(y, pred)),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "f1": float(f1_score(y, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None,
        "average_precision": float(average_precision_score(y, p)) if len(np.unique(y)) == 2 else None,
        "brier_score": float(brier_score_loss(y, p)),
        "confusion_matrix": matrix.tolist(),
        "classification_report": classification_report(
            y, pred, labels=[0, 1], target_names=["Stayed (0)", "Left (1)"],
            output_dict=True, zero_division=0,
        ),
        "support": {"stayed": int((y == 0).sum()), "left": int((y == 1).sum())},
        "threshold": float(threshold),
    }
