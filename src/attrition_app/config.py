"""Shared configuration and repository paths."""
from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATH = Path(os.getenv("ATTRITION_DATA", PROJECT_ROOT / "data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv"))
MODEL_PATH = Path(os.getenv("ATTRITION_MODEL", PROJECT_ROOT / "models/attrition_model.joblib"))
REPORT_DIR = Path(os.getenv("ATTRITION_REPORT_DIR", PROJECT_ROOT / "reports"))
TARGET = "Attrition"
RANDOM_SEED = int(os.getenv("ATTRITION_RANDOM_SEED", "42"))
MAX_UPLOAD_MB = 20

# Exclude target, identifiers, constant fields, and direct sensitive attributes by default.
ALWAYS_EXCLUDE = {
    "employeenumber", "employeecount", "over18", "standardhours", "age",
    "gender", "maritalstatus", "employeeid", "id",
}

DISCLAIMER = (
    "This application is an educational machine learning prototype using historical data. "
    "Attrition probabilities are estimates and may be inaccurate or affected by bias in the data. "
    "They must not be used as the sole basis for employment decisions."
)
