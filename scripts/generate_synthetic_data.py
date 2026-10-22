"""Generate clearly synthetic records for local pipeline smoke tests only."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def generate_synthetic_dataset(rows: int = 200, seed: int = 42) -> pd.DataFrame:
    """Create deterministic toy data with both target classes and known synthetic structure."""
    if rows < 50:
        raise ValueError("Use at least 50 rows so the example is suitable for the project's stratified split.")
    rng = np.random.default_rng(seed)
    department = rng.choice(["Sales", "Research & Development", "Human Resources"], rows, p=[0.45, 0.45, 0.10])
    roles = rng.choice(["Sales Executive", "Research Scientist", "Laboratory Technician", "Manager"], rows)
    overtime = rng.choice(["Yes", "No"], rows, p=[0.30, 0.70])
    years = rng.integers(0, 25, rows)
    satisfaction = rng.integers(1, 5, rows)
    work_life = rng.integers(1, 5, rows)
    risk_score = (
        0.90 * (overtime == "Yes")
        + 0.45 * (years <= 2)
        + 0.35 * (satisfaction <= 2)
        + 0.35 * (work_life <= 2)
        + rng.normal(0.0, 0.65, rows)
    )
    cutoff = float(np.quantile(risk_score, 0.70))
    attrition = np.where(risk_score >= cutoff, "Yes", "No")
    if min(int((attrition == "Yes").sum()), int((attrition == "No").sum())) < 7:
        raise ValueError("The generated target has too few examples in one class. Increase --rows or change --seed.")

    level = rng.integers(1, 6, rows)
    return pd.DataFrame({
        "EmployeeNumber": np.arange(1, rows + 1),
        "Age": rng.integers(18, 61, rows),
        "Gender": rng.choice(["Female", "Male"], rows),
        "MaritalStatus": rng.choice(["Single", "Married", "Divorced"], rows),
        "Department": department,
        "JobRole": roles,
        "JobLevel": level,
        "MonthlyIncome": rng.integers(2200, 9500, rows) + level * 250 + years * 70,
        "OverTime": overtime,
        "YearsAtCompany": years,
        "JobSatisfaction": satisfaction,
        "WorkLifeBalance": work_life,
        "EmployeeCount": 1,
        "Over18": "Y",
        "StandardHours": 80,
        "Attrition": attrition,
    })


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic data for local pipeline testing only.")
    parser.add_argument("--rows", type=int, default=200, help="Synthetic row count (minimum 50; default: 200)")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic generation seed")
    parser.add_argument("--output", type=Path, default=Path("data/raw/synthetic_attrition.csv"), help="Output CSV path")
    parser.add_argument("--force", action="store_true", help="Allow replacing an existing output file")
    args = parser.parse_args()
    if args.output.exists() and not args.force:
        parser.error(f"Output already exists: {args.output}. Choose another path or pass --force to replace it.")
    try:
        frame = generate_synthetic_dataset(args.rows, args.seed)
    except ValueError as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False)
    print("Generated synthetic test data only; it is not real employee data or a representative HR sample.")
    print(f"Rows: {len(frame)} · target counts: {frame['Attrition'].value_counts().to_dict()}")
    print(f"CSV: {args.output}")


if __name__ == "__main__":
    main()
