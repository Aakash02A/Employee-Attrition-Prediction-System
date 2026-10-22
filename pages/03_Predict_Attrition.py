"""Prediction page using only a trusted locally trained model bundle."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import streamlit as st

from attrition_app.config import DISCLAIMER, MODEL_PATH
from attrition_app.data_loader import DataValidationError
from attrition_app.predict import load_model_bundle, predict_csv, predict_one


def _reset_single_form() -> None:
    st.session_state["single_form_version"] = st.session_state.get("single_form_version", 0) + 1


st.title("Predict Attrition")
st.caption("Estimated probabilities are uncertain associations, not decisions or guarantees.")
if not MODEL_PATH.is_file():
    st.info(f"No trained model found at `{MODEL_PATH}`. Validate your labeled CSV, then train with `python -m attrition_app.train --data data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv`.")
    st.warning(DISCLAIMER)
    st.stop()

@st.cache_resource(show_spinner="Loading local model…")
def _bundle(path: str, modified: float):
    del modified
    return load_model_bundle(path)

try:
    bundle = _bundle(str(MODEL_PATH), MODEL_PATH.stat().st_mtime)
except (OSError, ValueError, DataValidationError) as exc:
    st.error(f"The local model could not be loaded: {exc}")
    st.stop()
metadata = bundle["metadata"]
threshold = st.slider("Classification threshold", min_value=0.05, max_value=0.95, value=float(metadata["threshold"]), step=0.01, help="Changes the threshold-dependent label only; the estimated probability is unchanged.")
form_version = st.session_state.get("single_form_version", 0)
st.caption(f"Selected model: {metadata['model_name']} · threshold {threshold:.2f}")

single_tab, batch_tab = st.tabs(["Single employee profile", "Batch CSV"])
with single_tab:
    profile = metadata.get("feature_profile", {})
    with st.form("single_prediction"):
        values = {}
        columns = st.columns(2)
        for index, name in enumerate(metadata["features"]):
            spec = profile.get(name, {})
            with columns[index % 2]:
                if spec.get("kind") == "number":
                    low, high = spec.get("minimum", 0), spec.get("maximum", 100)
                    padding = max((high - low) * 0.15, 1.0)
                    floor, ceiling = float(low - padding), float(high + padding)
                    default = min(max(float(spec.get("default", low)), floor), ceiling)
                    values[name] = st.number_input(name, min_value=floor, max_value=ceiling, value=default, key=f"single_{form_version}_{name}",
                        step=1.0 if spec.get("integer") else 0.1, help="Feature value; range is based on training data with modest room outside it.")
                else:
                    options = spec.get("options", [])
                    if options and not spec.get("has_more"):
                        values[name] = st.selectbox(name, options, key=f"single_{form_version}_{name}")
                    else:
                        values[name] = st.text_input(name, key=f"single_{form_version}_{name}", help="Enter a category. Unseen categories are handled as unknown by the fitted encoder.")
        submitted = st.form_submit_button("Estimate probability", type="primary")
    if submitted:
        try:
            result = predict_one(values, bundle, threshold)
            st.metric("Estimated attrition probability", f"{float(result['EstimatedAttritionProbability']):.1%}")
            st.write(f"**Model classification at threshold {threshold:.2f}:** {result['ModelClassification']}")
            st.caption("This estimate reflects patterns learned from historical training data. It does not explain causation or predict an individual's future with certainty.")
        except (DataValidationError, ValueError) as exc:
            st.error(str(exc))
    st.button("Clear single-record form", on_click=_reset_single_form)

with batch_tab:
    upload = st.file_uploader("Upload prediction CSV (maximum 20 MB)", type=["csv"], key="batch_prediction")
    if upload:
        try:
            output, ignored = predict_csv(upload, bundle, threshold)
            if ignored:
                st.info("Ignored columns: " + ", ".join(ignored))
            st.dataframe(output.head(100), use_container_width=True)
            st.download_button("Download prediction results", output.to_csv(index=False).encode("utf-8"), file_name="attrition_predictions.csv", mime="text/csv")
            st.caption(f"Predicted {len(output):,} rows in memory; records are not saved by the application. Probabilities are unchanged when the threshold moves.")
        except (DataValidationError, OSError, ValueError) as exc:
            st.error(f"Could not create predictions: {exc}")
st.warning(DISCLAIMER)
