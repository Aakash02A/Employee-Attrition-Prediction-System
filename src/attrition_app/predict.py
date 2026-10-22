"""Schema-validated inference using the exact fitted training pipeline."""
from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from .config import MODEL_PATH
from .data_loader import DataValidationError, load_csv


def load_model_bundle(path: str | Path = MODEL_PATH) -> dict:
    """Load a locally generated trusted Joblib bundle (never accept uploaded artifacts)."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"No trained model at {path}. Run the documented training command first.")
    bundle = joblib.load(path)
    if not isinstance(bundle, dict) or "pipeline" not in bundle or "metadata" not in bundle:
        raise DataValidationError("The model artifact is incompatible. Retrain it with this project version.")
    return bundle


def validate_prediction_frame(frame: pd.DataFrame, bundle: dict) -> tuple[pd.DataFrame, list[str]]:
    expected = list(bundle["metadata"].get("features", []))
    missing = [name for name in expected if name not in frame.columns]
    if missing:
        raise DataValidationError("Missing required model input columns: " + ", ".join(missing))
    ignored = [name for name in frame.columns if name not in expected]
    result = frame.loc[:, expected].copy()
    profile = bundle["metadata"].get("feature_profile", {})
    for name in expected:
        if profile.get(name, {}).get("kind") == "number":
            converted = pd.to_numeric(result[name], errors="coerce")
            invalid = result[name].notna() & converted.isna()
            if invalid.any():
                rows = (invalid[invalid].index[:5] + 1).tolist()
                raise DataValidationError(f"Column '{name}' contains non-numeric values near uploaded row(s) {rows}.")
            result[name] = converted
    return result, ignored


def predict_frame(frame: pd.DataFrame, bundle: dict, threshold: float | None = None) -> tuple[pd.DataFrame, list[str]]:
    if not 0 <= (threshold if threshold is not None else bundle["metadata"].get("threshold", 0.5)) <= 1:
        raise DataValidationError("Threshold must be between 0 and 1.")
    X, ignored = validate_prediction_frame(frame, bundle)
    if X.empty:
        raise DataValidationError("The prediction CSV has no employee rows.")
    probabilities = bundle["pipeline"].predict_proba(X)[:, 1]
    cutoff = float(threshold if threshold is not None else bundle["metadata"].get("threshold", 0.5))
    output = frame.copy()
    output["EstimatedAttritionProbability"] = probabilities
    output["ModelClassification"] = pd.Series(probabilities >= cutoff, index=output.index).map({True: "Higher estimated probability", False: "Lower estimated probability"})
    output["ClassificationThreshold"] = cutoff
    return output, ignored


def predict_one(record: dict, bundle: dict, threshold: float | None = None) -> dict:
    frame = pd.DataFrame([record])
    result, _ = predict_frame(frame, bundle, threshold)
    return result.iloc[0].to_dict()


def predict_csv(source, bundle: dict, threshold: float | None = None) -> tuple[pd.DataFrame, list[str]]:
    """Read an upload in memory; ignore target/identifier extras and report them."""
    frame = load_csv(source, require_target=False)
    # Target and protected/identifier columns are deliberately ignored, not treated as inputs.
    return predict_frame(frame, bundle, threshold)
