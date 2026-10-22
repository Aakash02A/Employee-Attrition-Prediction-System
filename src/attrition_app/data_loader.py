"""CSV ingestion and dataset validation without silently dropping records."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import pandas as pd

from .config import TARGET


class DataValidationError(ValueError):
    """Raised when a dataset cannot safely be used for the requested workflow."""


@dataclass
class DataQualityReport:
    rows: int
    columns: int
    duplicate_rows: int
    missing_cells: int
    missing_by_column: dict[str, int]
    constant_columns: list[str]
    suspicious_identifiers: list[str]
    target_column: str | None
    target_counts: dict[str, int]
    warnings: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def _read_csv(source: str | Path | BinaryIO | BytesIO) -> pd.DataFrame:
    errors: list[str] = []
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            if hasattr(source, "seek"):
                source.seek(0)
            frame = pd.read_csv(source, encoding=encoding)
            if frame.empty and len(frame.columns) == 0:
                raise DataValidationError("The CSV is empty. Add a header row and at least one record.")
            if frame.shape[1] == 0:
                raise DataValidationError("No columns were found in the CSV.")
            return frame
        except UnicodeDecodeError as exc:
            errors.append(str(exc))
        except pd.errors.EmptyDataError as exc:
            raise DataValidationError("The CSV is empty. Add a header row and at least one record.") from exc
        except pd.errors.ParserError as exc:
            raise DataValidationError(f"Malformed CSV: {exc}") from exc
        except DataValidationError:
            raise
        except (OSError, ValueError) as exc:
            raise DataValidationError(f"Could not read the CSV: {exc}") from exc
    raise DataValidationError("Could not decode the CSV as UTF-8 or Windows-1252. Re-save it as UTF-8.")


def load_csv(source: str | Path | BinaryIO | BytesIO, *, require_target: bool = False) -> pd.DataFrame:
    """Load a CSV and safely trim column-name whitespace; retain all rows/columns."""
    frame = _read_csv(source)
    cleaned = [str(name).strip() for name in frame.columns]
    if any(not name for name in cleaned):
        raise DataValidationError("Every CSV column must have a non-empty name.")
    if len(set(cleaned)) != len(cleaned):
        raise DataValidationError("Column names are duplicated after trimming whitespace; rename them and retry.")
    frame.columns = cleaned
    target_matches = [c for c in frame.columns if c.casefold() == TARGET.casefold()]
    if len(target_matches) > 1:
        raise DataValidationError("More than one column matches the target name Attrition.")
    if target_matches and target_matches[0] != TARGET:
        frame = frame.rename(columns={target_matches[0]: TARGET})
    if require_target and TARGET not in frame.columns:
        raise DataValidationError(f"Required target column '{TARGET}' is missing.")
    if frame.empty:
        raise DataValidationError("The CSV contains headers but no data rows.")
    return frame


def normalize_target(values: pd.Series, *, require_both: bool = True) -> pd.Series:
    """Map common attrition labels to 1=left and 0=stayed; reject ambiguity."""
    mapping = {"yes": 1, "no": 0, "1": 1, "0": 0, "1.0": 1, "0.0": 0, "true": 1, "false": 0,
               "left": 1, "stayed": 0, "stay": 0, "leave": 1}
    normalized = values.astype("string").str.strip().str.casefold().map(mapping)
    if normalized.isna().any():
        bad = sorted(values[normalized.isna()].astype(str).unique().tolist())[:10]
        raise DataValidationError(f"Unexpected or missing Attrition labels: {bad}. Expected Yes/No or 1/0.")
    normalized = normalized.astype("int8")
    if require_both and set(normalized.unique()) != {0, 1}:
        raise DataValidationError("Training requires both attrition classes (Yes/No or 1/0).")
    return normalized


def quality_report(frame: pd.DataFrame, *, has_target: bool | None = None) -> DataQualityReport:
    target_exists = TARGET in frame.columns if has_target is None else has_target
    missing = frame.isna().sum()
    constants = [str(c) for c in frame.columns if frame[c].nunique(dropna=True) <= 1]
    suspicious = [str(c) for c in frame.columns if str(c).casefold() in {"id", "employeeid", "employeenumber"} or str(c).casefold().endswith("_id")]
    warnings: list[str] = []
    dupes = int(frame.duplicated().sum())
    if dupes:
        warnings.append(f"{dupes} duplicate rows found; none were removed automatically.")
    if missing.sum():
        warnings.append(f"{int(missing.sum())} missing cells found; model preprocessing imputes feature values.")
    if constants:
        warnings.append("Constant columns are excluded from predictive features: " + ", ".join(constants))
    counts: dict[str, int] = {}
    if target_exists:
        try:
            normalized = normalize_target(frame[TARGET], require_both=False)
            counts = {"Stayed (0)": int((normalized == 0).sum()), "Left (1)": int((normalized == 1).sum())}
            if not all(counts.values()):
                warnings.append("Only one Attrition class is present; supervised training requires both classes.")
        except DataValidationError as exc:
            warnings.append(str(exc))
    return DataQualityReport(
        rows=int(len(frame)), columns=int(frame.shape[1]), duplicate_rows=dupes,
        missing_cells=int(missing.sum()), missing_by_column={str(k): int(v) for k, v in missing.items() if v},
        constant_columns=constants, suspicious_identifiers=suspicious,
        target_column=TARGET if target_exists else None, target_counts=counts, warnings=warnings,
    )
