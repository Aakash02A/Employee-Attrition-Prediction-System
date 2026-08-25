"""
Employee Attrition Prediction — FastAPI ML Service
Phase 6

Loads the v2 model (tuned Random Forest), its scaler, and the exact
feature-encoding schema produced during training, then exposes:

  POST /predict  — accepts raw employee attributes, returns prediction,
                    probability, and risk level
  GET  /health   — service + model liveness check

Run locally:
    uvicorn app.main:app --reload --port 8000

This service is intentionally the only place that knows about model
internals (encoding, scaling, threshold). The Spring Boot backend
should treat it as a black box: raw employee JSON in, prediction JSON out.
"""

from pathlib import Path
import json
import logging

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import EmployeeFeatures, PredictionResponse, HealthResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("attrition-ml-service")

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

app = FastAPI(
    title="Employee Attrition Prediction Service",
    description="ML microservice that predicts employee attrition risk.",
    version="1.0.0",
)

# CORS: allow the Spring Boot backend (and, during local dev, the static
# frontend if it ever calls this service directly) to reach this API.
# Tighten allow_origins to the real backend URL before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: replace with the actual Spring Boot origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Load model artifacts once at startup (not per-request)
# ------------------------------------------------------------------
_model = None
_scaler = None
_feature_columns = None
_raw_schema = None
_metadata = None


@app.on_event("startup")
def load_artifacts():
    global _model, _scaler, _feature_columns, _raw_schema, _metadata

    try:
        _model = joblib.load(MODELS_DIR / "model_v2.pkl")
        _scaler = joblib.load(MODELS_DIR / "scaler_v2.pkl")

        with open(MODELS_DIR / "feature_columns_v2.json") as f:
            _feature_columns = json.load(f)

        with open(MODELS_DIR / "raw_input_schema.json") as f:
            _raw_schema = json.load(f)

        with open(MODELS_DIR / "model_metadata_v2.json") as f:
            _metadata = json.load(f)

        logger.info(
            "Loaded model_version=%s (%s), decision_threshold=%.4f",
            _metadata["model_version"],
            _metadata["model_type"],
            _metadata["decision_threshold"],
        )
    except FileNotFoundError as e:
        logger.error("Failed to load model artifacts: %s", e)
        raise


def _risk_level(probability: float) -> str:
    """Bucket a probability into a risk label for the UI.

    These cutoffs are independent of the model's binary decision threshold
    (which decides Stay/Leave) — they exist purely to drive the risk badge
    color in the frontend (Low/Medium/High).
    """
    if probability < 0.30:
        return "LOW"
    elif probability < 0.60:
        return "MEDIUM"
    return "HIGH"


def _encode_input(features: EmployeeFeatures) -> pd.DataFrame:
    """Replicate the exact training-time preprocessing for a single request.

    1. Build a one-row DataFrame from the raw input fields.
    2. One-hot encode the categorical columns the same way training did.
    3. Reindex to the exact trained feature-column set, filling any dummy
       column absent for this single row with 0 (this is what makes
       single-row encoding match a batch encoding done during training).
    4. Scale with the fitted StandardScaler.
    """
    raw_dict = features.model_dump()
    row = pd.DataFrame([raw_dict])

    categorical_cols = _raw_schema["categorical_columns"]
    encoded = pd.get_dummies(row, columns=categorical_cols, drop_first=True)

    # Align to the exact training-time column set and order.
    encoded = encoded.reindex(columns=_feature_columns, fill_value=0)

    scaled = _scaler.transform(encoded)
    return pd.DataFrame(scaled, columns=_feature_columns)


@app.get("/health", response_model=HealthResponse)
def health():
    """Basic liveness + model-loaded check."""
    if _model is None or _scaler is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return HealthResponse(
        status="ok",
        model_version=_metadata["model_version"],
        model_type=_metadata["model_type"],
        decision_threshold=_metadata["decision_threshold"],
    )


@app.post("/predict", response_model=PredictionResponse)
def predict(features: EmployeeFeatures):
    """Predict attrition risk for a single employee.

    Applies the tuned decision threshold from training (not the default
    0.5) to decide Stay vs Leave, per the threshold-tuning done in Phase 5.
    """
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        X = _encode_input(features)
    except Exception as e:
        logger.exception("Failed to encode input")
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")

    probability = float(_model.predict_proba(X)[0, 1])
    threshold = _metadata["decision_threshold"]
    prediction = "LEAVE" if probability >= threshold else "STAY"
    risk = _risk_level(probability)

    return PredictionResponse(
        prediction=prediction,
        probability=round(probability, 4),
        risk_level=risk,
        model_version=_metadata["model_version"],
        decision_threshold=threshold,
    )
