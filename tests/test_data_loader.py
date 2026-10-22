from __future__ import annotations

from io import StringIO

import pandas as pd
import pytest

from attrition_app.data_loader import DataValidationError, load_csv, normalize_target, quality_report


def test_load_csv_trims_names_and_requires_target_when_requested():
    frame = load_csv(StringIO(" Attrition , Department\nYes,Sales\nNo,Research\n"), require_target=True)
    assert list(frame.columns) == ["Attrition", "Department"]
    assert normalize_target(frame["Attrition"]).tolist() == [1, 0]


def test_missing_required_target_is_actionable():
    with pytest.raises(DataValidationError, match="Attrition"):
        load_csv(StringIO("Department\nSales\n"), require_target=True)


def test_duplicate_names_after_trimming_rejected():
    with pytest.raises(DataValidationError, match="duplicated"):
        load_csv(StringIO("Department, Department \nSales,Sales\n"))


def test_target_rejects_missing_and_unexpected_labels():
    with pytest.raises(DataValidationError, match="Unexpected or missing"):
        normalize_target(pd.Series(["Yes", "maybe"]))
    with pytest.raises(DataValidationError, match="both attrition classes"):
        normalize_target(pd.Series(["Yes", "Yes"]))


def test_quality_report_keeps_duplicate_rows_and_reports_missing():
    frame = pd.DataFrame({"Attrition": ["Yes", "No", "No", "Yes"], "value": [1, 1, None, 1], "constant": [2, 2, 2, 2]})
    report = quality_report(frame)
    assert report.rows == 4
    assert report.duplicate_rows == 1
    assert report.missing_cells == 1
    assert "constant" in report.constant_columns
    assert report.target_counts == {"Stayed (0)": 2, "Left (1)": 2}


def test_malformed_and_empty_csv_have_readable_errors():
    with pytest.raises(DataValidationError, match="empty"):
        load_csv(StringIO(""))
    with pytest.raises(DataValidationError):
        load_csv(StringIO("a,b\n1,2,3\n"))
