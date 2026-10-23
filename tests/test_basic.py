import numpy as np
import pandas as pd
import pytest

from core import (LABEL_COL, MODEL_PATH, PROB_COL, ROOT, TARGET, apply_threshold, feature_frame,
                  load_bundle, predict_frame, validate_input)
from report import make_pdf

pytestmark = pytest.mark.skipif(not MODEL_PATH.exists(), reason="run `python train.py` first")


@pytest.fixture(scope="module")
def bundle():
    b, err = load_bundle()
    assert err is None
    return b


@pytest.fixture(scope="module")
def holdout():
    return pd.read_csv(ROOT / "data" / "real_holdout_20pct_DO_NOT_TRAIN.csv")


def test_excluded_columns_not_features(bundle):
    for c in ["Age", "Gender", "MaritalStatus", "EmployeeNumber", TARGET]:
        assert c not in bundle["schema"]


def test_missing_columns_rejected(bundle, holdout):
    rep = validate_input(holdout.drop(columns=["OverTime"]), bundle)
    assert not rep["ok"] and rep["missing"] == ["OverTime"]
    with pytest.raises(ValueError):
        predict_frame(holdout.drop(columns=["OverTime"]), bundle)


def test_batch_prediction_preserves_rows_and_labels(bundle, holdout):
    out = predict_frame(holdout, bundle)
    assert len(out) == len(holdout)
    assert (out[TARGET].values == holdout[TARGET].values).all()            # actual label kept
    assert (out["EmployeeNumber"].values == holdout["EmployeeNumber"].values).all()  # order kept
    assert out[PROB_COL].between(0, 1).all()
    assert set(out[LABEL_COL]) <= {"Left", "Stayed"}


def test_threshold_changes_label_not_probability(bundle, holdout):
    lo, hi = predict_frame(holdout, bundle, 0.1), predict_frame(holdout, bundle, 0.9)
    assert (lo[PROB_COL] == hi[PROB_COL]).all()
    assert (lo[LABEL_COL] == "Left").sum() > (hi[LABEL_COL] == "Left").sum()


def test_unknown_category_and_extra_column_ok(bundle, holdout):
    df = holdout.head(5).copy()
    df["JobRole"] = "Space Pirate"
    df["SomeExtra"] = 1
    assert validate_input(df, bundle)["extra"].count("SomeExtra") == 1
    assert predict_frame(df, bundle)[PROB_COL].notna().all()


def test_existing_prediction_column_not_overwritten(bundle, holdout):
    df = holdout.head(3).copy()
    df[PROB_COL] = 0
    with pytest.raises(ValueError):
        predict_frame(df, bundle)


def test_same_input_same_output(bundle, holdout):
    a, b = predict_frame(holdout.head(20), bundle), predict_frame(holdout.head(20), bundle)
    assert np.allclose(a[PROB_COL], b[PROB_COL])


def test_pdf_is_valid():
    pdf = make_pdf("T", [("h", "H"), ("p", "text"), ("table", [["a", "b"], [1, 2]])])
    assert pdf[:5] == b"%PDF-" and len(pdf) > 1000


def test_app_starts_without_errors():
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    assert not at.exception
