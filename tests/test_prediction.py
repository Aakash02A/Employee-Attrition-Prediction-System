from __future__ import annotations

import pandas as pd
import pytest

from attrition_app.data_loader import DataValidationError
from attrition_app.predict import load_model_bundle, predict_csv, predict_frame, predict_one


def _record(bundle):
    return {name: (bundle["metadata"]["feature_profile"][name].get("options", ["Sales"])[0]
                   if bundle["metadata"]["feature_profile"][name]["kind"] == "category"
                   else bundle["metadata"]["feature_profile"][name]["default"])
            for name in bundle["metadata"]["features"]}


def test_single_prediction_has_probability_and_threshold_label(trained_bundle):
    result, _ = trained_bundle
    bundle = load_model_bundle(result["model_path"])
    prediction = predict_one(_record(bundle), bundle, threshold=0.4)
    assert 0 <= prediction["EstimatedAttritionProbability"] <= 1
    assert prediction["ClassificationThreshold"] == 0.4
    assert prediction["ModelClassification"] in {"Higher estimated probability", "Lower estimated probability"}


def test_batch_csv_ignores_target_and_extra_identifier_and_preserves_order(trained_bundle, labeled_frame):
    result, _ = trained_bundle
    bundle = load_model_bundle(result["model_path"])
    rows = labeled_frame.iloc[[5, 2, 9]].copy()
    output, ignored = predict_csv(__import__("io").StringIO(rows.to_csv(index=False)), bundle)
    assert len(output) == 3
    assert output["EmployeeNumber"].tolist() == rows["EmployeeNumber"].tolist()
    assert "Attrition" in ignored and "EmployeeNumber" in ignored
    assert output["EstimatedAttritionProbability"].between(0, 1).all()


def test_missing_required_and_bad_numeric_values_fail_safely(trained_bundle):
    result, _ = trained_bundle
    bundle = load_model_bundle(result["model_path"])
    row = _record(bundle)
    missing = pd.DataFrame([{k: v for k, v in row.items() if k != bundle["metadata"]["features"][0]}])
    with pytest.raises(DataValidationError, match="Missing required"):
        predict_frame(missing, bundle)
    row["MonthlyIncome"] = "not-a-number"
    with pytest.raises(DataValidationError, match="non-numeric"):
        predict_frame(pd.DataFrame([row]), bundle)


def test_unknown_category_and_column_order_are_supported(trained_bundle):
    result, _ = trained_bundle
    bundle = load_model_bundle(result["model_path"])
    row = _record(bundle)
    row["Department"] = "New unit"
    reordered = pd.DataFrame([{key: row[key] for key in reversed(row)}])
    output, _ = predict_frame(reordered, bundle)
    assert output["EstimatedAttritionProbability"].between(0, 1).all()


def test_missing_model_is_actionable(tmp_path):
    with pytest.raises(FileNotFoundError, match="training command"):
        load_model_bundle(tmp_path / "missing.joblib")
