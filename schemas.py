"""
Pydantic schemas for the Employee Attrition Prediction ML service.

Field constraints (ranges, allowed categories) are taken directly from
`models/raw_input_schema.json`, which was derived from the actual training
data (see ml-service/data/employee_attrition.csv). If the model is ever
retrained on different/expanded data, regenerate raw_input_schema.json and
update the constraints below to match.
"""

from typing import Literal
from pydantic import BaseModel, Field


class EmployeeFeatures(BaseModel):
    """Raw employee attributes required for a prediction.

    Field order does not matter here — the service re-encodes and reorders
    to match the trained feature set internally.
    """

    # --- Numeric fields (bounds reflect the training data's observed min/max) ---
    Age: int = Field(..., ge=18, le=60, description="Employee age")
    DailyRate: int = Field(..., ge=100, le=1500)
    DistanceFromHome: int = Field(..., ge=0, le=50, description="Distance from home, km")
    Education: int = Field(..., ge=1, le=5, description="1=Below College ... 5=Doctor")
    EnvironmentSatisfaction: int = Field(..., ge=1, le=4)
    HourlyRate: int = Field(..., ge=20, le=110)
    JobInvolvement: int = Field(..., ge=1, le=4)
    JobLevel: int = Field(..., ge=1, le=5)
    JobSatisfaction: int = Field(..., ge=1, le=4)
    MonthlyIncome: int = Field(..., ge=1000, le=25000)
    MonthlyRate: int = Field(..., ge=2000, le=27000)
    NumCompaniesWorked: int = Field(..., ge=0, le=10)
    PercentSalaryHike: int = Field(..., ge=10, le=25)
    PerformanceRating: int = Field(..., ge=1, le=4)
    RelationshipSatisfaction: int = Field(..., ge=1, le=4)
    StockOptionLevel: int = Field(..., ge=0, le=3)
    TotalWorkingYears: int = Field(..., ge=0, le=45)
    TrainingTimesLastYear: int = Field(..., ge=0, le=6)
    WorkLifeBalance: int = Field(..., ge=1, le=4)
    YearsAtCompany: int = Field(..., ge=0, le=45)
    YearsInCurrentRole: int = Field(..., ge=0, le=20)
    YearsSinceLastPromotion: int = Field(..., ge=0, le=15)
    YearsWithCurrManager: int = Field(..., ge=0, le=20)

    # --- Categorical fields (exact category sets seen during training) ---
    BusinessTravel: Literal["Non-Travel", "Travel_Frequently", "Travel_Rarely"]
    Department: Literal["Human Resources", "Research & Development", "Sales"]
    EducationField: Literal[
        "Human Resources", "Life Sciences", "Marketing",
        "Medical", "Other", "Technical Degree",
    ]
    Gender: Literal["Female", "Male"]
    JobRole: Literal[
        "Healthcare Representative", "Human Resources", "Laboratory Technician",
        "Manager", "Manufacturing Director", "Research Director",
        "Research Scientist", "Sales Executive", "Sales Representative",
    ]
    MaritalStatus: Literal["Divorced", "Married", "Single"]
    OverTime: Literal["No", "Yes"]

    model_config = {
        "json_schema_extra": {
            "example": {
                "Age": 29,
                "DailyRate": 800,
                "DistanceFromHome": 5,
                "Education": 3,
                "EnvironmentSatisfaction": 2,
                "HourlyRate": 65,
                "JobInvolvement": 3,
                "JobLevel": 2,
                "JobSatisfaction": 2,
                "MonthlyIncome": 4500,
                "MonthlyRate": 15000,
                "NumCompaniesWorked": 2,
                "PercentSalaryHike": 14,
                "PerformanceRating": 3,
                "RelationshipSatisfaction": 3,
                "StockOptionLevel": 0,
                "TotalWorkingYears": 6,
                "TrainingTimesLastYear": 2,
                "WorkLifeBalance": 2,
                "YearsAtCompany": 3,
                "YearsInCurrentRole": 2,
                "YearsSinceLastPromotion": 1,
                "YearsWithCurrManager": 2,
                "BusinessTravel": "Travel_Rarely",
                "Department": "Sales",
                "EducationField": "Marketing",
                "Gender": "Female",
                "JobRole": "Sales Executive",
                "MaritalStatus": "Single",
                "OverTime": "Yes",
            }
        }
    }


class PredictionResponse(BaseModel):
    # protected_namespaces=() silences Pydantic's warning about fields
    # starting with "model_" (it reserves that prefix for its own internals
    # by default; our field names are intentional and don't collide with
    # anything Pydantic actually uses).
    model_config = {"protected_namespaces": ()}

    prediction: Literal["STAY", "LEAVE"]
    probability: float = Field(..., ge=0, le=1, description="Probability of attrition (0-1)")
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    model_version: str
    decision_threshold: float


class HealthResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    status: Literal["ok"]
    model_version: str
    model_type: str
    decision_threshold: float