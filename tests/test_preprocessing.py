from __future__ import annotations

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from attrition_app.preprocessing import eligible_features, make_preprocessor, split_features


def test_target_sensitive_identifier_and_constant_columns_are_excluded(labeled_frame):
    features = eligible_features(labeled_frame)
    assert "Attrition" not in features
    assert "Age" not in features
    assert "Gender" not in features
    assert "EmployeeNumber" not in features
    assert "Constant" not in features
    assert "Department" in features


def test_pipeline_handles_missing_and_unseen_categories(labeled_frame):
    X, y, numeric, categorical = split_features(labeled_frame)
    pipeline = Pipeline([
        ("preprocessor", make_preprocessor(numeric, categorical)),
        ("classifier", LogisticRegression(max_iter=500)),
    ])
    pipeline.fit(X.iloc[:120], y.iloc[:120])
    sample = X.iloc[[121]].copy()
    if categorical:
        sample.loc[:, categorical[0]] = "Previously unseen category"
    result = pipeline.predict_proba(sample)
    assert result.shape == (1, 2)
    assert abs(result.sum() - 1.0) < 1e-9


def test_features_preserve_requested_order(labeled_frame):
    chosen = ["OverTime", "MonthlyIncome"]
    X, _, _, _ = split_features(labeled_frame, chosen)
    assert list(X.columns) == chosen
