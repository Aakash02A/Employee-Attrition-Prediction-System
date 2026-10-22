from __future__ import annotations

import json

import joblib
import pytest

from attrition_app.data_loader import DataValidationError
from attrition_app.predict import load_model_bundle
from attrition_app.train import train_model


def test_trains_three_candidates_and_writes_real_artifacts(trained_bundle):
    result, folder = trained_bundle
    metadata = result["metadata"]
    assert metadata["model_name"] in {"Logistic Regression", "Random Forest", "Extra Trees"}
    assert len(result["comparison"]) == 3
    assert metadata["split"]["proportions"] == "70/15/15 stratified"
    assert "Age" not in metadata["features"] and "Attrition" not in metadata["features"]
    assert result["model_path"]
    assert (folder / "reports" / "training_metadata.json").is_file()
    saved = json.loads((folder / "reports" / "test_evaluation.json").read_text(encoding="utf-8"))
    assert 0 <= saved["average_precision"] <= 1


def test_training_refuses_too_few_class_members(tmp_path, labeled_frame):
    small = labeled_frame.iloc[:20].copy()
    small["Attrition"] = ["Yes", "No"] * 10
    # Reduce the minority below the minimum required for two stratified holdouts.
    small.loc[small.index[:14], "Attrition"] = "No"
    path = tmp_path / "small.csv"
    small.to_csv(path, index=False)
    with pytest.raises(DataValidationError, match="at least 7 rows"):
        train_model(path, model_path=tmp_path / "model.joblib", report_dir=tmp_path / "reports")


def test_saved_pipeline_loads(trained_bundle):
    result, _ = trained_bundle
    bundle = load_model_bundle(result["model_path"])
    assert bundle["metadata"]["model_id"] == result["metadata"]["model_id"]
    assert bundle["pipeline"] is not None


def test_prediction_is_stable_across_artifact_serialization(trained_bundle, labeled_frame, tmp_path):
    result, _ = trained_bundle
    bundle = load_model_bundle(result["model_path"])
    features = bundle["metadata"]["features"]
    sample = labeled_frame.loc[[0], features]
    before = bundle["pipeline"].predict_proba(sample)
    path = tmp_path / "roundtrip.joblib"
    joblib.dump(bundle, path)
    restored = joblib.load(path)
    after = restored["pipeline"].predict_proba(sample)
    assert (before == after).all()
