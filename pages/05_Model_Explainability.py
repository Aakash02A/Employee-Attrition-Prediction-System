"""Explainability page using saved held-out permutation importance."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import plotly.express as px
import streamlit as st

from attrition_app.config import MODEL_PATH
from attrition_app.data_loader import DataValidationError
from attrition_app.explainability import explanation_method, global_importance
from attrition_app.predict import load_model_bundle

st.title("Model Explainability")
if not MODEL_PATH.is_file():
    st.info("Train a model to generate real feature explanations. No sample or fabricated importance values are shown.")
    st.stop()
try:
    bundle = load_model_bundle(MODEL_PATH)
except (OSError, ValueError, DataValidationError) as exc:
    st.error(f"Unable to read the model artifact: {exc}")
    st.stop()
importance = global_importance(bundle)
if importance.empty:
    st.info("No stored feature-importance results are available. Retrain to generate held-out permutation importance.")
else:
    n = st.slider("Features shown", 5, min(30, max(5, len(importance))), min(15, max(5, len(importance))))
    top = importance.head(n).sort_values("importance_mean")
    st.plotly_chart(px.bar(top, x="importance_mean", y="feature", orientation="h", error_x="importance_std", title="Global permutation importance (held-out test data)", labels={"importance_mean":"Decrease in average precision after shuffling", "feature":"Feature", "importance_std":"Across-repeat variability"}), use_container_width=True)
    st.caption(explanation_method())
st.warning("Feature importance describes how this fitted model uses information in this dataset. It is not evidence of causation, does not explain an individual's behavior, and does not imply that changing a feature will prevent attrition.")
st.caption("Directly sensitive attributes, age, identifiers, and constant columns are excluded from training by default. This does not establish fairness or eliminate proxy bias.")
