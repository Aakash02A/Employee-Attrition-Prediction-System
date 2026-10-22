"""Model evaluation page; all displayed metrics come from a real training run."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.metrics import precision_recall_curve, roc_curve

from attrition_app.config import MODEL_PATH
from attrition_app.data_loader import DataValidationError
from attrition_app.predict import load_model_bundle

st.title("Model Performance")
if not MODEL_PATH.is_file():
    st.info("No evaluation artifacts exist yet. Add a labeled dataset and run `python -m attrition_app.train --data <path-to-csv>`; this page will not show placeholder metrics.")
    st.stop()
try:
    bundle = load_model_bundle(MODEL_PATH)
except (OSError, ValueError, DataValidationError) as exc:
    st.error(f"Unable to read local model artifacts: {exc}")
    st.stop()
meta = bundle["metadata"]
metrics = meta["test_metrics"]
st.caption(f"Training source: {meta['dataset']['source_path_name']} · {meta['dataset']['rows']:,} rows · model ID {meta['model_id']}")
st.caption("Candidate comparison uses validation results. Final performance below is from the held-out test split, evaluated after selection.")
st.subheader("Validation comparison")
comparison = pd.DataFrame(bundle["comparison"])
st.dataframe(comparison[[c for c in ["model", "average_precision", "roc_auc", "precision", "recall", "f1", "accuracy", "training_seconds"] if c in comparison]], use_container_width=True)
st.markdown(f"**Selected:** {meta['model_name']} · selection prioritized validation average precision (tie-break: F1). The threshold `{meta['threshold']:.3f}` was selected on validation data by maximizing F1.")
st.subheader("Held-out test evaluation")
metric_cols = st.columns(5)
for col, label, key in zip(metric_cols, ["Average precision", "ROC-AUC", "Precision", "Recall", "F1"], ["average_precision", "roc_auc", "precision", "recall", "f1"]):
    value = metrics.get(key)
    col.metric(label, "Not available" if value is None else f"{value:.3f}")
cm = np.asarray(metrics["confusion_matrix"])
left, right = st.columns(2)
left.plotly_chart(px.imshow(cm, text_auto=True, x=["Predicted stayed", "Predicted left"], y=["Actual stayed", "Actual left"], color_continuous_scale="Blues", title="Held-out test confusion matrix"), use_container_width=True)
left.caption(f"Test support: {metrics['support']['stayed']} stayed, {metrics['support']['left']} left. False positives flag employees who stayed; false negatives miss an employee who left.")
st.markdown("**Held-out test classification report**")
report_rows = {
    name: value if isinstance(value, dict) else {"accuracy": value}
    for name, value in metrics["classification_report"].items()
}
st.dataframe(pd.DataFrame.from_dict(report_rows, orient="index"), use_container_width=True)
y = np.asarray(bundle["test_y"], dtype=int)
p = np.asarray(bundle["test_probabilities"], dtype=float)
if len(np.unique(y)) == 2:
    fpr, tpr, _ = roc_curve(y, p)
    fig = go.Figure(go.Scatter(x=fpr, y=tpr, mode="lines", name="ROC"))
    fig.add_shape(type="line", x0=0, y0=0, x1=1, y1=1, line={"dash":"dash", "color":"gray"})
    fig.update_layout(title="Held-out test ROC curve", xaxis_title="False positive rate", yaxis_title="True positive rate")
    right.plotly_chart(fig, use_container_width=True)
    precision, recall, _ = precision_recall_curve(y, p)
    pr = go.Figure(go.Scatter(x=recall, y=precision, mode="lines", name="Precision–recall"))
    pr.update_layout(title="Held-out test precision–recall curve", xaxis_title="Recall", yaxis_title="Precision")
    st.plotly_chart(pr, use_container_width=True)
st.caption(f"Training run: {meta['trained_at_utc']} · random seed {meta['random_seed']} · split {meta['split']['proportions']} · Brier score {metrics['brier_score']:.3f}. Calibration is not certified; Brier score is shown as a proper scoring metric.")
