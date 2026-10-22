from __future__ import annotations

import pandas as pd

from attrition_app.eda import attrition_by, attrition_by_numeric_band, target_summary
from attrition_app.evaluate import binary_metrics, choose_threshold


def test_known_historical_rates_include_denominators():
    frame = pd.DataFrame({"Attrition": ["Yes", "No", "Yes", "No"], "Department": ["A", "A", "B", "B"]})
    summary = target_summary(frame)
    assert summary["left"] == 2 and summary["stayed"] == 2
    assert summary["attrition_rate"] == 0.5
    rates = attrition_by(frame, "Department").set_index("Department")
    assert rates.loc["A", "records"] == 2
    assert rates.loc["A", "attrition_rate"] == 0.5


def test_threshold_is_selected_from_validation_probabilities():
    threshold, scores = choose_threshold([0, 0, 1, 1], [0.1, 0.4, 0.6, 0.9])
    assert 0.05 <= threshold <= 0.95
    assert scores["f1"] > 0.0
    metrics = binary_metrics([0, 0, 1, 1], [0.1, 0.4, 0.6, 0.9], threshold)
    assert "Left (1)" in metrics["classification_report"]
    assert metrics["confusion_matrix"] == [[2, 0], [0, 2]]


def test_single_class_filters_and_numeric_bands_are_supported():
    frame = pd.DataFrame({
        "Attrition": ["No", "No", "Yes", "No"],
        "YearsAtCompany": [1, 2, 8, 12],
    })
    summary = target_summary(frame.iloc[:2])
    assert summary["stayed"] == 2 and summary["left"] == 0
    bands = attrition_by_numeric_band(frame, "YearsAtCompany", bins=2)
    assert bands["records"].sum() == 4
    assert bands["left"].sum() == 1


def test_streamlit_app_starts_without_dataset_or_model():
    from pathlib import Path
    from streamlit.testing.v1 import AppTest

    root = Path(__file__).resolve().parents[1]
    app = AppTest.from_file(str(root / "app.py"), default_timeout=20).run()
    assert not app.exception
    assert any("Employee Attrition Analytics" in str(item.value) for item in app.title)
