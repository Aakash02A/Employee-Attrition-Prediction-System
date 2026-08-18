"""
evaluate.py
Metrics for imbalanced attrition prediction: accuracy is not reported
because it's misleading on an ~84/16 class split.
"""

import numpy as np
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)


def precision_at_k(y_true, y_proba, k):
    """Of the top-k highest-risk employees, what fraction actually left?
    Mirrors a real HR intervention budget of k employees."""
    order = np.argsort(y_proba)[::-1][:k]
    return y_true.iloc[order].mean() if hasattr(y_true, "iloc") else np.mean(y_true[order])


def evaluate_model(model, X_test, y_test, name="model", k=50):
    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= 0.5).astype(int)

    roc_auc = roc_auc_score(y_test, y_proba)
    pr_auc = average_precision_score(y_test, y_proba)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    k_eff = min(k, len(y_test))
    p_at_k = precision_at_k(y_test, y_proba, k_eff)
    cm = confusion_matrix(y_test, y_pred)

    print(f"[{name}]")
    print(f"  ROC-AUC:          {roc_auc:.3f}")
    print(f"  PR-AUC:           {pr_auc:.3f}")
    print(f"  Precision:        {precision:.3f}")
    print(f"  Recall:           {recall:.3f}")
    print(f"  F1:               {f1:.3f}")
    print(f"  Precision@top{k_eff}: {p_at_k:.3f}")
    print(f"  Confusion matrix:\n{cm}")

    return {
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "precision_at_k": p_at_k,
    }
