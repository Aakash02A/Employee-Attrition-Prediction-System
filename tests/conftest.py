from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


@pytest.fixture(scope="module")
def labeled_frame() -> pd.DataFrame:
    rng = np.random.default_rng(17)
    n = 160
    overtime = np.where(np.arange(n) % 3 == 0, "Yes", "No")
    leave = np.where((np.arange(n) % 4 == 0) | ((overtime == "Yes") & (np.arange(n) % 5 == 0)), "Yes", "No")
    return pd.DataFrame({
        "MonthlyIncome": rng.integers(1800, 12000, size=n),
        "YearsAtCompany": rng.integers(0, 25, size=n),
        "Department": np.where(np.arange(n) % 2, "Sales", "Research"),
        "OverTime": overtime,
        "Age": rng.integers(18, 65, size=n),
        "Gender": np.where(np.arange(n) % 2, "Female", "Male"),
        "EmployeeNumber": np.arange(1, n + 1),
        "Constant": 1,
        "Attrition": leave,
    })


@pytest.fixture(scope="module")
def trained_bundle(tmp_path_factory, labeled_frame):
    from attrition_app.train import train_model

    folder = tmp_path_factory.mktemp("trained")
    dataset = folder / "synthetic.csv"
    labeled_frame.to_csv(dataset, index=False)
    result = train_model(dataset, model_path=folder / "model.joblib", report_dir=folder / "reports")
    return result, folder
