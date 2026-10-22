"""Model-supported explanation accessors."""
from __future__ import annotations

import pandas as pd


def global_importance(bundle: dict) -> pd.DataFrame:
    rows = bundle.get("feature_importance", [])
    if not rows:
        return pd.DataFrame(columns=["feature", "importance_mean", "importance_std"])
    return pd.DataFrame(rows).sort_values("importance_mean", ascending=False, ignore_index=True)


def explanation_method() -> str:
    return "Held-out permutation importance scored by average precision. Values describe model reliance, not causality."
