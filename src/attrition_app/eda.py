"""Data summaries used by analytics screens; all rates include their denominators."""
from __future__ import annotations

import pandas as pd

from .config import TARGET
from .data_loader import DataValidationError, normalize_target


def target_summary(frame: pd.DataFrame) -> dict:
    if TARGET not in frame.columns:
        return {"available": False, "records": int(len(frame))}
    if frame.empty:
        return {"available": True, "records": 0, "left": 0, "stayed": 0, "attrition_rate": None}
    y = normalize_target(frame[TARGET], require_both=False)
    left = int(y.sum())
    stayed = int((y == 0).sum())
    return {"available": True, "records": int(len(frame)), "left": left, "stayed": stayed,
            "attrition_rate": left / len(y) if len(y) else None}


def attrition_by(frame: pd.DataFrame, column: str, *, minimum_group_size: int = 1) -> pd.DataFrame:
    if TARGET not in frame.columns or column not in frame.columns:
        return pd.DataFrame(columns=[column, "records", "left", "attrition_rate"])
    if frame.empty:
        return pd.DataFrame(columns=[column, "records", "left", "attrition_rate"])
    data = pd.DataFrame({column: frame[column].fillna("Missing").astype(str), "left": normalize_target(frame[TARGET], require_both=False)})
    grouped = data.groupby(column, dropna=False)["left"].agg(records="size", left="sum").reset_index()
    grouped["attrition_rate"] = grouped["left"] / grouped["records"]
    return grouped[grouped["records"] >= minimum_group_size].sort_values("attrition_rate", ascending=False)


def attrition_by_numeric_band(frame: pd.DataFrame, column: str, *, bins: int = 5) -> pd.DataFrame:
    """Summarize attrition by quantile bands, excluding missing numeric values explicitly."""
    columns = ["band", "records", "left", "attrition_rate"]
    if TARGET not in frame or column not in frame or frame.empty:
        return pd.DataFrame(columns=columns)
    values = pd.to_numeric(frame[column], errors="coerce")
    valid = values.notna()
    unique = int(values[valid].nunique())
    if unique < 2:
        return pd.DataFrame(columns=columns)
    categories = pd.qcut(values[valid], q=min(max(2, bins), unique), duplicates="drop")
    data = pd.DataFrame({"band": categories.astype(str), "left": normalize_target(frame.loc[valid, TARGET], require_both=False)})
    grouped = data.groupby("band", observed=True)["left"].agg(records="size", left="sum").reset_index()
    grouped["attrition_rate"] = grouped["left"] / grouped["records"]
    return grouped[columns]


def aggregate_group_audit(frame: pd.DataFrame, protected_columns: list[str], *, minimum_group_size: int = 20) -> dict[str, pd.DataFrame]:
    """Optional descriptive subgroup rate tables; suppress small groups by default."""
    if TARGET not in frame:
        raise DataValidationError("Aggregate auditing requires an Attrition target column.")
    return {column: attrition_by(frame, column, minimum_group_size=minimum_group_size)
            for column in protected_columns if column in frame.columns}
