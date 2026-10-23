"""Shared helpers used by train.py, app.py and the tests."""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "attrition_model.joblib"
TARGET = "Attrition"
# Identifiers/constants + sensitive attributes are NOT used by the model.
EXCLUDED = ["EmployeeNumber", "EmployeeCount", "Over18", "StandardHours",
            "Gender", "MaritalStatus", "Age"]
PROB_COL = "predicted_attrition_probability"
LABEL_COL = "predicted_attrition"


def feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Drop target + excluded columns -> model input columns."""
    return df.drop(columns=[c for c in [TARGET, *EXCLUDED] if c in df.columns])


def build_schema(X: pd.DataFrame) -> dict:
    """Describe each feature (used to build the input form and validate uploads)."""
    schema = {}
    for c in X.columns:
        if X[c].dtype == object or str(X[c].dtype).startswith("str"):
            schema[c] = {"type": "cat", "choices": sorted(X[c].dropna().unique().tolist())}
        else:
            schema[c] = {"type": "num", "min": float(X[c].min()), "max": float(X[c].max()),
                         "median": float(X[c].median())}
    return schema


def load_bundle(path: Path = MODEL_PATH):
    """Load the trusted local model bundle. Returns (bundle, error_message)."""
    if not Path(path).exists():
        return None, "No trained model found. Run `python train.py` first."
    try:
        return joblib.load(path), None
    except Exception as e:  # corrupted / incompatible sklearn version
        return None, f"Model file could not be loaded ({type(e).__name__}). Re-run `python train.py`."


def validate_input(df: pd.DataFrame, bundle: dict) -> dict:
    """Check an uploaded frame against the model's expected features."""
    schema = bundle["schema"]
    required = list(schema)
    missing = [c for c in required if c not in df.columns]
    extra = [c for c in df.columns if c not in required and c != TARGET]
    bad_numeric, null_cols = [], {}
    for c in required:
        if c in df.columns:
            if schema[c]["type"] == "num":
                coerced = pd.to_numeric(df[c], errors="coerce")
                if coerced.isna().sum() > df[c].isna().sum():
                    bad_numeric.append(c)
            n_null = int(df[c].isna().sum())
            if n_null:
                null_cols[c] = n_null
    return {"missing": missing, "extra": extra, "bad_numeric": bad_numeric, "null_cols": null_cols,
            "ok": not (missing or bad_numeric or null_cols)}


def predict_proba(df: pd.DataFrame, bundle: dict) -> np.ndarray:
    """Probability of attrition. Raises ValueError if the input is invalid."""
    report = validate_input(df, bundle)
    if not report["ok"]:
        raise ValueError(f"Invalid input: {report}")
    X = df[list(bundle["schema"])].copy()
    for c, s in bundle["schema"].items():
        if s["type"] == "num":
            X[c] = pd.to_numeric(X[c])
    return bundle["pipeline"].predict_proba(X)[:, 1]


def apply_threshold(proba, threshold: float):
    return np.where(np.asarray(proba) >= threshold, "Left", "Stayed")


def predict_frame(df: pd.DataFrame, bundle: dict, threshold: float | None = None) -> pd.DataFrame:
    """Input rows (same order, all original columns kept) + 2 prediction columns."""
    for c in (PROB_COL, LABEL_COL):
        if c in df.columns:
            raise ValueError(f"Input already has a column named '{c}'. Please rename it.")
    thr = bundle["threshold"] if threshold is None else threshold
    proba = predict_proba(df, bundle)
    out = df.copy()
    out[PROB_COL] = np.round(proba, 4)
    out[LABEL_COL] = apply_threshold(proba, thr)
    return out
