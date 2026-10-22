"""Data Explorer page; analysis uploads remain in session memory only."""
from __future__ import annotations

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import plotly.express as px
import streamlit as st

from attrition_app.config import DEFAULT_DATA_PATH, TARGET
from attrition_app.data_loader import DataValidationError, load_csv, quality_report
from attrition_app.eda import aggregate_group_audit

st.title("Data Explorer")
st.caption("Inspect schema and quality before analysis. Uploads are not used to train or replace a model.")
source = st.radio("Dataset source", ["Default local dataset", "Upload for analysis"], horizontal=True)
frame = None
if source == "Default local dataset":
    if DEFAULT_DATA_PATH.is_file():
        try:
            frame = load_csv(DEFAULT_DATA_PATH)
        except DataValidationError as exc:
            st.error(str(exc))
    else:
        st.info(f"Dataset not found: `{DEFAULT_DATA_PATH}`. Place the public IBM HR CSV there or select Upload for analysis.")
else:
    upload = st.file_uploader("Select CSV (maximum 20 MB)", type=["csv"])
    if upload:
        try:
            frame = load_csv(upload)
        except DataValidationError as exc:
            st.error(str(exc))

if frame is not None:
    report = quality_report(frame)
    a, b, c = st.columns(3)
    a.metric("Rows", f"{report.rows:,}")
    b.metric("Columns", f"{report.columns:,}")
    c.metric("Duplicate rows", f"{report.duplicate_rows:,}")
    st.subheader("Preview")
    st.dataframe(frame.head(100), use_container_width=True)
    st.subheader("Data quality")
    st.json(report.to_dict())
    if report.warnings:
        for warning in report.warnings:
            st.warning(warning)
    missing = frame.isna().sum().rename("missing").to_frame()
    missing["missing_percent"] = (missing["missing"] / max(len(frame), 1) * 100).round(2)
    st.subheader("Missing values by column")
    st.dataframe(missing[missing["missing"] > 0].sort_values("missing", ascending=False) if missing["missing"].any() else missing.head(0), use_container_width=True)
    numeric = frame.select_dtypes(include="number").columns.tolist()
    categorical = [c for c in frame.columns if c not in numeric]
    tab_num, tab_cat, tab_corr, tab_fair = st.tabs(["Numerical distributions", "Categorical distributions", "Numeric relationships", "Aggregate subgroup audit"])
    with tab_num:
        if numeric:
            col = st.selectbox("Numerical feature", numeric)
            st.plotly_chart(px.histogram(frame, x=col, marginal="box", title=f"Distribution of {col}"), use_container_width=True)
        else:
            st.info("No numeric columns were found.")
    with tab_cat:
        choices = [c for c in categorical if c != TARGET]
        if choices:
            col = st.selectbox("Categorical feature", choices)
            top = frame[col].fillna("Missing").astype(str).value_counts().head(30).rename_axis(col).reset_index(name="records")
            st.plotly_chart(px.bar(top, x=col, y="records", title=f"Most frequent values in {col}"), use_container_width=True)
        else:
            st.info("No categorical feature columns were found.")
    with tab_corr:
        if len(numeric) >= 2:
            pair = st.columns(2)
            x_axis = pair[0].selectbox("X feature", numeric, key="scatter_x")
            y_choices = [name for name in numeric if name != x_axis]
            y_axis = pair[1].selectbox("Y feature", y_choices, key="scatter_y")
            color = TARGET if TARGET in frame else None
            st.plotly_chart(px.scatter(frame, x=x_axis, y=y_axis, color=color, title=f"{y_axis} vs {x_axis}"), use_container_width=True)
            st.caption("Patterns show association in the observed sample; they do not establish causation.")
        else:
            st.info("At least two numeric columns are needed for a pairwise relationship chart.")
    with tab_fair:
        if TARGET not in frame:
            st.info("Add an Attrition target column to calculate aggregate group rates.")
        else:
            protected = [c for c in ["Gender", "MaritalStatus", "Age"] if c in frame]
            selected = st.multiselect("Optional audit dimensions (excluded from training by default)", protected)
            minimum = st.number_input("Minimum group count shown", min_value=1, value=20, step=1)
            st.caption("Descriptive group-level rates only. Small groups are suppressed; these are not fairness certifications.")
            for name, table in aggregate_group_audit(frame, selected, minimum_group_size=int(minimum)).items():
                st.markdown(f"**{name}**")
                st.dataframe(table, use_container_width=True)
    st.caption("Charts describe observed data patterns only; association does not establish causation.")
