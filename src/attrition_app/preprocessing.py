"""Reusable feature policy, preprocessing pipeline, and stratified split helpers."""
from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import ALWAYS_EXCLUDE, TARGET
from .data_loader import DataValidationError, normalize_target


def feature_candidates(frame: pd.DataFrame) -> list[str]:
    """Return inputs allowed by policy before data-dependent constant detection."""
    keep: list[str] = []
    compact_identifier_names = {"staffid", "recordid", "personid", "customerid", "userid"}
    for column in frame.columns:
        key = str(column).strip().casefold()
        if (key == TARGET.casefold() or key in ALWAYS_EXCLUDE or key in compact_identifier_names
                or key.endswith("_id") or key.endswith("_number")):
            continue
        keep.append(str(column))
    if not keep:
        raise DataValidationError("No feature candidates remain after applying the default exclusion policy.")
    return keep


def eligible_features(frame: pd.DataFrame, reference: pd.DataFrame | None = None) -> list[str]:
    """Exclude constants using a reference partition (training data during model fitting)."""
    candidates = feature_candidates(frame)
    observations = frame if reference is None else reference
    keep = [name for name in candidates if name in observations and observations[name].nunique(dropna=True) > 1]
    if not keep:
        raise DataValidationError("No non-constant predictive features remain in the reference data.")
    return keep


def split_features(frame: pd.DataFrame, feature_columns: list[str] | None = None) -> tuple[pd.DataFrame, pd.Series, list[str], list[str]]:
    """Separate features and binary target, returning numeric and categorical columns."""
    if TARGET not in frame:
        raise DataValidationError(f"Required target column '{TARGET}' is missing.")
    y = normalize_target(frame[TARGET])
    features = feature_columns or eligible_features(frame)
    blocked = [name for name in features if name not in feature_candidates(frame)]
    if blocked:
        raise DataValidationError(f"Target, sensitive, identifier, or otherwise excluded columns cannot be features: {blocked}")
    absent = [c for c in features if c not in frame.columns]
    if absent:
        raise DataValidationError(f"Required feature columns are missing: {absent}")
    X = frame.loc[:, features].copy()
    numeric = X.select_dtypes(include=["number"]).columns.tolist()
    categorical = [column for column in X.columns if column not in numeric]
    if not numeric and not categorical:
        raise DataValidationError("No usable feature columns were found.")
    return X, y, numeric, categorical


def make_preprocessor(numeric: list[str], categorical: list[str]) -> ColumnTransformer:
    """Fit imputation/encoding/scaling only on each model's training partition."""
    transformers: list[tuple[str, Any, list[str]]] = []
    if numeric:
        transformers.append(("numeric", Pipeline([
            ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
            ("scaler", StandardScaler()),
        ]), numeric))
    if categorical:
        transformers.append(("categorical", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent", keep_empty_features=True)),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=True)),
        ]), categorical))
    return ColumnTransformer(transformers=transformers, remainder="drop", verbose_feature_names_out=False)


def feature_profile(frame: pd.DataFrame, columns: list[str]) -> dict[str, dict[str, Any]]:
    """Build safe UI hints from aggregate training feature values, not employee rows."""
    profile: dict[str, dict[str, Any]] = {}
    for name in columns:
        series = frame[name]
        if pd.api.types.is_numeric_dtype(series):
            clean = pd.to_numeric(series, errors="coerce").dropna()
            profile[name] = {
                "kind": "number",
                "minimum": float(clean.min()) if len(clean) else 0.0,
                "maximum": float(clean.max()) if len(clean) else 100.0,
                "default": float(clean.median()) if len(clean) else 0.0,
                "integer": bool(pd.api.types.is_integer_dtype(series)),
            }
        else:
            options = sorted(series.dropna().astype(str).unique().tolist())
            profile[name] = {"kind": "category", "options": options[:100], "has_more": len(options) > 100}
    return profile
