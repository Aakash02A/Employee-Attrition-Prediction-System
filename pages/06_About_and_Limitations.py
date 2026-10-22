"""Project scope, methodology, privacy, and limitations."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import streamlit as st

from attrition_app.config import DISCLAIMER, MODEL_PATH
from attrition_app.data_loader import DataValidationError
from attrition_app.predict import load_model_bundle

st.title("About and Limitations")
st.markdown("""## Purpose
This project demonstrates an end-to-end educational workflow for exploring historical employee attrition patterns and comparing conventional binary classifiers. The default IBM HR dataset is fictional and intended for analytics exercises.

## Method
The default candidates are class-weighted Logistic Regression, Random Forest, and Extra Trees. Numeric features are median-imputed and scaled; categorical features are imputed and one-hot encoded. A stratified 70/15/15 training/validation/test split is used. Average precision prioritizes validation model selection, with F1 as a tie-break. A validation F1 threshold is selected before the final test evaluation.

Direct sensitive attributes (age, gender, marital status), identifier-like columns, constants, and the target are excluded from predictive inputs by default. Optional subgroup tables are descriptive only and suppress small groups.

## Privacy and responsible use
The application processes uploaded CSV files in memory and does not send employee records to external APIs or save uploads by default. Do not upload data without authorization. Do not use this prototype to rank employees, recommend dismissal, or automate employment actions. Historical association is not causation; estimates may be wrong or biased and are not individual forecasts.

## Known limitations
The dataset is fictional and modest in size, generalization to any real employer is unknown, and probability calibration is not guaranteed. Group summaries are not evidence of fairness. The model explanations show global permutation importance only; individual causal explanations are not implemented. A trained local model must be generated before predictions are available.
""")
if MODEL_PATH.is_file():
    try:
        metadata = load_model_bundle(MODEL_PATH)["metadata"]
        st.caption(f"Local selected model: {metadata['model_name']} · trained {metadata['trained_at_utc']} · threshold {metadata['threshold']:.3f}")
    except (OSError, ValueError, DataValidationError) as exc:
        st.warning(f"Local model metadata unavailable: {exc}")
else:
    st.info("No trained model artifact is present in this checkout.")
st.warning(DISCLAIMER)
