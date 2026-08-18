"""
app.py
Streamlit dashboard: org-level risk overview + per-employee drill-down
with SHAP-driven explanations and rule-based recommendations.

Run with: streamlit run dashboard/app.py
Requires models/xgb_model.joblib and outputs/shap_explanations.joblib
to already exist (run src/train.py then src/explain.py first).
"""

import os
import sys

import joblib
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from data_prep import get_processed_data
from recommend import recommend_for_employee

st.set_page_config(page_title="Attrition Risk Dashboard", layout="wide")


@st.cache_data
def load_data():
    df = get_processed_data()
    explanations = joblib.load("outputs/shap_explanations.joblib")
    return df, explanations


def risk_bucket(score):
    if score >= 0.6:
        return "HIGH"
    if score >= 0.3:
        return "MEDIUM"
    return "LOW"


def main():
    st.title("Employee Attrition Risk Dashboard")

    if not os.path.exists("outputs/shap_explanations.joblib"):
        st.error(
            "outputs/shap_explanations.joblib not found. "
            "Run `python src/train.py` then `python src/explain.py` first."
        )
        return

    df, explanations = load_data()
    scores = [e["risk_score"] for e in explanations]
    buckets = [risk_bucket(s) for s in scores]

    st.header("Organization overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Employees monitored", len(scores))
    col2.metric("High risk", buckets.count("HIGH"))
    col3.metric("Medium risk", buckets.count("MEDIUM"))
    col4.metric("Predicted attrition rate", f"{sum(scores) / len(scores):.1%}")

    st.divider()
    st.header("Employee drill-down")

    idx = st.number_input(
        "Employee index", min_value=0, max_value=len(explanations) - 1, value=0, step=1
    )
    record = explanations[idx]
    score = record["risk_score"]
    bucket = risk_bucket(score)

    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("Risk level", bucket)
        st.metric("Probability", f"{score:.0%}")

    with c2:
        st.subheader("Key risk factors")
        for name, value in record["top_factors"]:
            direction = "increases" if value > 0 else "decreases"
            st.write(f"- **{name}** {direction} risk (impact: {value:+.3f})")

    st.subheader("Recommended actions")
    recs = recommend_for_employee(record["top_factors"])
    if not recs:
        st.write("No risk-increasing factors in the top drivers -- low priority.")
    else:
        for r in recs:
            st.checkbox(f"{r['issue']}: {r['action']}", key=f"{idx}-{r['issue']}")

    st.caption(
        "Recommendations are rule-based suggestions for HR review, not automated decisions. "
        "No action should be taken solely on this score."
    )


if __name__ == "__main__":
    main()
