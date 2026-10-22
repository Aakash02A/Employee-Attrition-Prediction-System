"""Streamlit entry point: overview dashboard and dataset setup."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
import plotly.express as px
import streamlit as st

from attrition_app.config import DEFAULT_DATA_PATH, DISCLAIMER, MODEL_PATH, TARGET
from attrition_app.data_loader import DataValidationError, load_csv
from attrition_app.eda import attrition_by, attrition_by_numeric_band, target_summary
from attrition_app.preprocessing import eligible_features

st.set_page_config(page_title="Attrition Analytics", page_icon="📊", layout="wide")
st.markdown("""<style>
.block-container {padding-top: 1.5rem; max-width: 1400px;}
[data-testid="stMetric"] {background:#f4f7fb;padding:14px 16px;border-radius:10px;border:1px solid #e5eaf1;}
section[data-testid="stSidebar"] {background:#f8fafc;}
</style>""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def _load_local(path: str, modified: float):
    del modified
    return load_csv(path, require_target=False)


def current_data() -> pd.DataFrame | None:
    uploaded = st.session_state.get("analysis_upload")
    if uploaded is not None:
        return uploaded
    if DEFAULT_DATA_PATH.is_file():
        try:
            return _load_local(str(DEFAULT_DATA_PATH), DEFAULT_DATA_PATH.stat().st_mtime)
        except (DataValidationError, OSError) as exc:
            st.error(f"Could not load the configured CSV: {exc}")
    return None


def main() -> None:
    st.title("Employee Attrition Analytics")
    st.caption("Explore historical patterns and transparent model estimates using authorized data.")
    frame = current_data()
    if frame is None:
        st.info(f"No dataset found at `{DEFAULT_DATA_PATH}`. Add the fictional IBM HR CSV there, or upload a CSV for in-memory exploration.")
        upload = st.file_uploader("Upload a CSV for this session's analysis", type=["csv"], key="dashboard_analysis_upload")
        if upload is not None:
            try:
                st.session_state["analysis_upload"] = load_csv(upload, require_target=False)
                st.rerun()
            except DataValidationError as exc:
                st.error(str(exc))
        st.markdown("To train a model, first place a labeled CSV at the path above and run `python -m attrition_app.train --data <your-file.csv>`. Uploaded analysis data does not train or replace a model.")
        return

    try:
        summary = target_summary(frame)
    except DataValidationError as exc:
        st.error(f"Historical attrition cannot be summarized: {exc}")
        summary = {"available": False}
    cols = st.columns(4)
    cols[0].metric("Employee records", f"{len(frame):,}")
    if summary["available"]:
        cols[1].metric("Left in historical data", f"{summary['left']:,}")
        cols[2].metric("Stayed in historical data", f"{summary['stayed']:,}")
        cols[3].metric("Historical attrition rate", f"{summary['attrition_rate']:.1%}", help=f"{summary['left']:,} of {summary['records']:,} labeled rows")
    else:
        cols[1].metric("Columns", f"{frame.shape[1]:,}")
        cols[2].metric("Target status", "Not present")
        st.info("A valid Attrition target is unavailable. Historical attrition analysis cannot be calculated; prediction workflows can still use the data if required features are present.")
    try:
        feature_count = len(eligible_features(frame))
    except DataValidationError:
        feature_count = 0
    status_cols = st.columns(2)
    status_cols[0].metric("Eligible predictive features", feature_count)
    status_cols[1].metric("Selected model", "Available" if MODEL_PATH.is_file() else "Training needed")

    if TARGET in frame and summary.get("available"):
        st.subheader("Historical attrition patterns")
        filters = st.columns(2)
        dept_options = ["All"] + sorted(frame["Department"].dropna().astype(str).unique()) if "Department" in frame else ["All"]
        role_options = ["All"] + sorted(frame["JobRole"].dropna().astype(str).unique()) if "JobRole" in frame else ["All"]
        dept = filters[0].selectbox("Department", dept_options)
        role = filters[1].selectbox("Job role", role_options)
        view = frame.copy()
        if dept != "All" and "Department" in view:
            view = view[view["Department"].astype(str) == dept]
        if role != "All" and "JobRole" in view:
            view = view[view["JobRole"].astype(str) == role]
        dist = target_summary(view)
        st.plotly_chart(px.pie(names=["Stayed", "Left"], values=[dist["stayed"], dist["left"]], hole=.55, title="Historical outcome mix"), use_container_width=True)
        group_columns = [name for name in ["Department", "JobRole", "OverTime", "JobSatisfaction", "WorkLifeBalance"] if name in view]
        for index in range(0, len(group_columns), 2):
            chart_columns = st.columns(2)
            for slot, name in enumerate(group_columns[index:index + 2]):
                rates = attrition_by(view, name)
                chart_columns[slot].plotly_chart(px.bar(
                    rates, x=name, y="attrition_rate", hover_data=["records", "left"],
                    title=f"Historical attrition rate by {name}",
                    labels={"attrition_rate": "Attrition rate", "records": "Records", "left": "Left"},
                ), use_container_width=True)
        numeric_bands = [name for name in ["YearsAtCompany", "MonthlyIncome"] if name in view]
        for index in range(0, len(numeric_bands), 2):
            chart_columns = st.columns(2)
            for slot, name in enumerate(numeric_bands[index:index + 2]):
                bands = attrition_by_numeric_band(view, name)
                if not bands.empty:
                    chart_columns[slot].plotly_chart(px.bar(
                        bands, x="band", y="attrition_rate", hover_data=["records", "left"],
                        title=f"Historical attrition rate by {name} band",
                        labels={"attrition_rate": "Attrition rate", "band": name},
                    ), use_container_width=True)
        st.caption("These are historical associations in the supplied data, not causal findings or forecasts for any individual.")

    st.divider()
    model_status = "Trained model available" if MODEL_PATH.is_file() else "No trained model yet"
    st.caption(f"{frame.shape[1]} columns · {model_status} · Analysis data is processed in memory; uploads are not saved by this app.")
    st.warning(DISCLAIMER)


main()
