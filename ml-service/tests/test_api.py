import pytest
from fastapi.testclient import TestClient
from app.main import app, load_artifacts

# Ensure model artifacts are loaded
load_artifacts()

client = TestClient(app)

SAMPLE_VALID_EMPLOYEE = {
    "Age": 32,
    "DailyRate": 800,
    "DistanceFromHome": 5,
    "Education": 3,
    "EnvironmentSatisfaction": 3,
    "HourlyRate": 65,
    "JobInvolvement": 3,
    "JobLevel": 2,
    "JobSatisfaction": 3,
    "MonthlyIncome": 5500,
    "MonthlyRate": 14000,
    "NumCompaniesWorked": 2,
    "PercentSalaryHike": 14,
    "PerformanceRating": 3,
    "RelationshipSatisfaction": 3,
    "StockOptionLevel": 1,
    "TotalWorkingYears": 8,
    "TrainingTimesLastYear": 3,
    "WorkLifeBalance": 3,
    "YearsAtCompany": 5,
    "YearsInCurrentRole": 3,
    "YearsSinceLastPromotion": 1,
    "YearsWithCurrManager": 3,
    "BusinessTravel": "Travel_Rarely",
    "Department": "Sales",
    "EducationField": "Life Sciences",
    "Gender": "Female",
    "JobRole": "Sales Executive",
    "MaritalStatus": "Single",
    "OverTime": "No",
}

HIGH_RISK_EMPLOYEE = {
    "Age": 22,
    "DailyRate": 300,
    "DistanceFromHome": 35,
    "Education": 1,
    "EnvironmentSatisfaction": 1,
    "HourlyRate": 30,
    "JobInvolvement": 1,
    "JobLevel": 1,
    "JobSatisfaction": 1,
    "MonthlyIncome": 1500,
    "MonthlyRate": 4000,
    "NumCompaniesWorked": 7,
    "PercentSalaryHike": 11,
    "PerformanceRating": 3,
    "RelationshipSatisfaction": 1,
    "StockOptionLevel": 0,
    "TotalWorkingYears": 1,
    "TrainingTimesLastYear": 0,
    "WorkLifeBalance": 1,
    "YearsAtCompany": 1,
    "YearsInCurrentRole": 0,
    "YearsSinceLastPromotion": 0,
    "YearsWithCurrManager": 0,
    "BusinessTravel": "Travel_Frequently",
    "Department": "Sales",
    "EducationField": "Marketing",
    "Gender": "Male",
    "JobRole": "Sales Representative",
    "MaritalStatus": "Single",
    "OverTime": "Yes",
}

LOW_RISK_EMPLOYEE = {
    "Age": 48,
    "DailyRate": 1300,
    "DistanceFromHome": 2,
    "Education": 4,
    "EnvironmentSatisfaction": 4,
    "HourlyRate": 95,
    "JobInvolvement": 4,
    "JobLevel": 4,
    "JobSatisfaction": 4,
    "MonthlyIncome": 18000,
    "MonthlyRate": 22000,
    "NumCompaniesWorked": 1,
    "PercentSalaryHike": 20,
    "PerformanceRating": 4,
    "RelationshipSatisfaction": 4,
    "StockOptionLevel": 2,
    "TotalWorkingYears": 25,
    "TrainingTimesLastYear": 4,
    "WorkLifeBalance": 4,
    "YearsAtCompany": 20,
    "YearsInCurrentRole": 12,
    "YearsSinceLastPromotion": 2,
    "YearsWithCurrManager": 10,
    "BusinessTravel": "Non-Travel",
    "Department": "Research & Development",
    "EducationField": "Medical",
    "Gender": "Female",
    "JobRole": "Manager",
    "MaritalStatus": "Married",
    "OverTime": "No",
}


def test_health_endpoint():
    """GET /health returns 200 with model metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model_version" in data
    assert "model_type" in data
    assert "decision_threshold" in data
    assert isinstance(data["decision_threshold"], float)


def test_predict_valid_request():
    """POST /predict with valid request returns 200 and complete prediction fields."""
    response = client.post("/predict", json=SAMPLE_VALID_EMPLOYEE)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] in ["STAY", "LEAVE"]
    assert 0.0 <= data["probability"] <= 1.0
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert "model_version" in data
    assert "decision_threshold" in data


def test_predict_missing_field_returns_422():
    """POST /predict with missing required field returns 422."""
    payload = dict(SAMPLE_VALID_EMPLOYEE)
    del payload["MonthlyIncome"]
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_out_of_range_numeric_returns_422():
    """POST /predict with out-of-range Age returns 422."""
    payload = dict(SAMPLE_VALID_EMPLOYEE, Age=200)
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_invalid_categorical_returns_422():
    """POST /predict with invalid categorical value returns 422."""
    payload = dict(SAMPLE_VALID_EMPLOYEE, Department="Not Real")
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_model_discriminates_high_vs_low_risk():
    """High-risk profile produces meaningfully higher attrition probability than low-risk profile."""
    res_high = client.post("/predict", json=HIGH_RISK_EMPLOYEE)
    res_low = client.post("/predict", json=LOW_RISK_EMPLOYEE)

    assert res_high.status_code == 200
    assert res_low.status_code == 200

    prob_high = res_high.json()["probability"]
    prob_low = res_low.json()["probability"]

    assert prob_high > prob_low
    assert (prob_high - prob_low) >= 0.20, f"Expected high risk ({prob_high}) to exceed low risk ({prob_low}) by at least 0.20"


def test_probability_bounds_and_risk_bucketing():
    """Probability is strictly between 0 and 1, and risk_level matches the probability bucketing."""
    for employee in [SAMPLE_VALID_EMPLOYEE, HIGH_RISK_EMPLOYEE, LOW_RISK_EMPLOYEE]:
        res = client.post("/predict", json=employee)
        assert res.status_code == 200
        data = res.json()
        prob = data["probability"]
        risk = data["risk_level"]

        assert 0.0 <= prob <= 1.0

        if prob < 0.30:
            assert risk == "LOW"
        elif prob < 0.60:
            assert risk == "MEDIUM"
        else:
            assert risk == "HIGH"
