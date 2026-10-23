"""Employee Attrition Prediction System  ->  streamlit run app.py   (no login, nothing saved to disk)"""
import pandas as pd
import plotly.express as px
import streamlit as st

from core import (LABEL_COL, PROB_COL, ROOT, TARGET, apply_threshold, load_bundle, predict_frame,
                  validate_input)
from report import DISCLAIMER, fmt_table, make_pdf

MAX_MB = 20
st.set_page_config(page_title="Employee Attrition Prediction", page_icon="📉", layout="wide")


@st.cache_resource
def get_bundle():
    return load_bundle()


@st.cache_data
def sample_data():
    p = ROOT / "data" / "real_train_80pct.csv"
    return pd.read_csv(p) if p.exists() else None


def read_upload(file):
    """Read an uploaded CSV safely. Returns (df, error)."""
    if file.size > MAX_MB * 1024 * 1024:
        return None, f"File is larger than {MAX_MB} MB."
    try:
        df = pd.read_csv(file)
    except pd.errors.EmptyDataError:
        return None, "The file is empty."
    except (pd.errors.ParserError, UnicodeDecodeError):
        return None, "Could not parse the file as CSV."
    if df.empty:
        return None, "The file has headers but no rows."
    return df, None


def has_labels(df):
    return TARGET in df.columns and df[TARGET].notna().any() and set(df[TARGET].dropna().unique()) <= {"Yes", "No"}


def rate_by(df, col, bins=None):
    s = df[col]
    if bins is not None:
        s = pd.cut(s, bins=bins)
    g = (df[TARGET] == "Yes").groupby(s, observed=True).agg(["mean", "size"]).reset_index()
    g.columns = [col, "attrition_rate", "employees"]
    g[col] = g[col].astype(str)
    return g


def rate_chart(df, col, title, bins=None):
    g = rate_by(df, col, bins)
    fig = px.bar(g, x=col, y="attrition_rate", text=g["employees"].map(lambda n: f"n={n}"), title=title)
    fig.update_yaxes(tickformat=".0%", title="Historical attrition rate")
    fig.update_layout(margin=dict(t=50, b=10), height=330)
    return fig


bundle, model_err = get_bundle()
st.title("📉 Employee Attrition Prediction System")
st.caption("Educational prototype · no login · uploads are processed in memory and not saved · "
           "the default dataset is fictional (IBM HR Analytics).")
with st.sidebar:
    st.header("Status")
    if bundle:
        st.success(f"Model loaded: {bundle['model_name']}")
        st.caption(f"Default threshold: {bundle['threshold']:.2f}")
    else:
        st.error(model_err)
    st.markdown("**Quick help**")
    st.caption("New here? Open the **📖 How to use** tab.")
    st.info(DISCLAIMER)

tab_guide, tab_explore, tab_predict, tab_perf = st.tabs(
    ["📖 How to use", "📊 Data Explorer", "🔮 Predict", "📈 Model Performance"])

# ───────────────────────────── How to use ─────────────────────────────
with tab_guide:
    st.subheader("Welcome 👋")
    st.write("This app does three things. Pick what you need:")
    g1, g2, g3 = st.columns(3)
    g1.markdown("#### 📊 Explore data\nUpload a CSV (or use the built-in sample) and see which groups "
                "had higher attrition in the past.")
    g2.markdown("#### 🔮 Predict\nGet an estimated attrition probability for **one employee** (form) or "
                "**many employees** (CSV upload).")
    g3.markdown("#### 📈 Check the model\nSee how well the model performed on employees it had never seen.")

    with st.expander("▶ Quick start: predict for one employee", expanded=True):
        st.markdown("1. Open the **🔮 Predict** tab and choose **Single employee**.\n"
                    "2. Fill in the form. Default values are typical ones, so change only what you know.\n"
                    "3. Click **Predict**. You get a probability, a classification (Left / Stayed) and a PDF report.\n"
                    "4. Move the **threshold slider** to see how the label changes. The probability stays the same.")

    with st.expander("▶ Quick start: predict for many employees (CSV)"):
        st.markdown("1. Open **🔮 Predict** → **Batch CSV** and download the **CSV template**.\n"
                    "2. Fill the template with one row per employee (keep the column names exactly).\n"
                    "3. Upload it, check the validation messages, then click **Run predictions**.\n"
                    "4. Download the full results as **CSV** or a summary as **PDF**.")
        if bundle:
            cols = list(bundle["schema"])
            st.markdown(f"**Required columns ({len(cols)}):** " + ", ".join(f"`{c}`" for c in cols))
            st.caption("Extra columns are ignored but kept in the output. An existing `Attrition` column is kept "
                       "as the actual label and is never used as an input. Empty cells and text in numeric "
                       "columns are rejected (nothing is filled in silently).")
            st.download_button("Download CSV template", pd.DataFrame(columns=cols).to_csv(index=False),
                               "attrition_input_template.csv", "text/csv", key="guide_template")
        else:
            st.warning("Train the model first (`python train.py`) to see the required columns.")

    with st.expander("▶ Quick start: explore historical data"):
        st.markdown("Open **📊 Data Explorer**, keep *Built-in sample* or upload your own CSV. Attrition charts "
                    "appear only if the file has an `Attrition` column with `Yes`/`No` values. Uploading here "
                    "never trains or changes the model.")

    with st.expander("▶ How to read the results"):
        st.markdown(
            "- **Estimated attrition probability**: the model's estimate (0–100%) that a profile resembles "
            "past employees who left. It is not a certainty and may be poorly calibrated.\n"
            "- **Threshold**: probabilities at or above it are labelled **Left**. Lower threshold = catches more "
            "leavers but more false alarms. Higher = fewer false alarms but more leavers missed.\n"
            "- **Historical attrition rate** (Data Explorer) is what *happened*; **estimated probability** "
            "(Predict) is what the model *estimates*. They are different things.\n"
            "- **Feature importance** shows what the model relies on, not what *causes* people to leave.")

    with st.expander("▶ Privacy and responsible use"):
        st.markdown(
            "- No login. Uploaded files are processed in memory and are **not saved** by the app.\n"
            "- Data is not sent to any external service.\n"
            "- Downloaded files are outside the app's control. If you host this publicly, anyone with the link can "
            "use it, so use only fictional or authorised data.\n"
            "- Age, Gender and Marital Status are deliberately **not** used by the model.\n"
            "- " + DISCLAIMER)

    with st.expander("▶ Troubleshooting"):
        st.markdown(
            "- **\"No trained model found\"** → run `python train.py` in the project folder, then restart the app.\n"
            "- **Upload rejected** → check the red messages: they list missing columns or bad values.\n"
            "- **`streamlit` not recognised on Windows** → use `python -m streamlit run app.py`.")

# ───────────────────────────── Data Explorer ─────────────────────────────
with tab_explore:
    st.subheader("Explore historical attrition")
    st.caption("Uploading here does NOT train or change the model.")
    choice = st.radio("Dataset", ["Built-in sample", "Upload my own CSV"], horizontal=True)
    df = None
    if choice == "Built-in sample":
        df = sample_data()
        if df is None:
            st.warning("Built-in sample not found in data/. Upload a CSV instead.")
    else:
        up = st.file_uploader("CSV file", type="csv", key="explore_upload")
        if up:
            df, err = read_upload(up)
            if err:
                st.error(err)

    if df is not None:
        labelled = has_labels(df)
        c = st.columns(4)
        c[0].metric("Rows", f"{len(df):,}")
        c[1].metric("Columns", df.shape[1])
        if labelled:
            left = int((df[TARGET] == "Yes").sum())
            c[2].metric("Left", f"{left:,}")
            c[3].metric("Historical attrition rate", f"{left / df[TARGET].notna().sum():.1%}")
        else:
            st.info("No valid `Attrition` (Yes/No) column found, so historical attrition statistics are "
                    "unavailable for this file. Use the Predict tab to estimate attrition for new records.")

        with st.expander("Data quality", expanded=not labelled):
            const = [col for col in df.columns if df[col].nunique(dropna=False) <= 1]
            idlike = [col for col in df.columns if len(df) > 1 and df[col].nunique() == len(df)]
            q = st.columns(4)
            q[0].metric("Missing cells", int(df.isna().sum().sum()))
            q[1].metric("Duplicate rows", int(df.duplicated().sum()))
            q[2].metric("Constant columns", len(const))
            q[3].metric("ID-like columns", len(idlike))
            st.caption(f"Constant: {', '.join(const) or '–'}  ·  ID-like: {', '.join(idlike) or '–'}")
            st.dataframe(df.head(50), width="stretch")

        if labelled:
            specs = [("Department", "By department", None), ("JobRole", "By job role", None),
                     ("OverTime", "By overtime", None), ("JobSatisfaction", "By job satisfaction", None),
                     ("WorkLifeBalance", "By work-life balance", None)]
            charts = [rate_chart(df, col, t) for col, t, _ in specs if col in df.columns]
            if "YearsAtCompany" in df.columns:
                charts.append(rate_chart(df, "YearsAtCompany", "By years at company", bins=[-1, 2, 5, 10, 60]))
            if "MonthlyIncome" in df.columns:
                charts.append(rate_chart(df, "MonthlyIncome", "By monthly income", bins=[0, 3000, 6000, 10000, 1e6]))
            for i in range(0, len(charts), 2):
                cols = st.columns(2)
                for col, fig in zip(cols, charts[i:i + 2]):
                    col.plotly_chart(fig, width="stretch")
            st.caption("Historical rates describe the data; they show association, not cause. "
                       "Small groups (see n=) are noisy.")

        blocks = [("h", "Dataset overview"),
                  ("table", [["Rows", "Columns", "Missing cells", "Duplicate rows"],
                             [len(df), df.shape[1], int(df.isna().sum().sum()), int(df.duplicated().sum())]])]
        if labelled:
            blocks += [("p", f"Historical attrition rate: {(df[TARGET] == 'Yes').mean():.1%} "
                             f"({int((df[TARGET] == 'Yes').sum())} of {len(df)} employees left).")]
            for col in ("Department", "JobRole", "OverTime"):
                if col in df.columns:
                    g = rate_by(df, col)
                    blocks += [("h", f"Attrition by {col}"),
                               ("table", fmt_table(g.values.tolist(), [col, "Attrition rate", "Employees"]))]
        else:
            blocks += [("p", "No valid Attrition column: historical attrition statistics cannot be calculated.")]
        st.download_button("⬇️ Download analysis report (PDF)",
                           make_pdf("Dataset Analysis Report", blocks),
                           "employee_attrition_analysis_report.pdf", "application/pdf")

# ───────────────────────────── Predict ─────────────────────────────
with tab_predict:
    if not bundle:
        st.error(model_err)
    else:
        schema, info = bundle["schema"], bundle["info"]
        thr = st.slider("Classification threshold", 0.05, 0.95, float(round(bundle["threshold"], 2)), 0.01,
                        help="Employees with probability ≥ threshold are labelled 'Left'. Lower = catches more "
                             "leavers but more false alarms. Changing it never changes the probability.")
        mode = st.radio("Mode", ["Single employee", "Batch CSV"], horizontal=True)

        if mode == "Single employee":
            with st.form("single_form"):
                cols = st.columns(3)
                values = {}
                for i, (name, s) in enumerate(schema.items()):
                    w = cols[i % 3]
                    if s["type"] == "cat":
                        values[name] = w.selectbox(name, s["choices"])
                    else:
                        lo, hi, med = s["min"], s["max"], s["median"]
                        values[name] = w.number_input(name, min_value=int(lo), max_value=int(hi),
                                                      value=int(round(med)), step=1,
                                                      help=f"Range seen in training data: {lo:g}–{hi:g}")
                if st.form_submit_button("Predict", type="primary"):
                    st.session_state["single_record"] = values
            if "single_record" in st.session_state:
                rec = pd.DataFrame([st.session_state["single_record"]])
                prob = float(predict_frame(rec, bundle, thr)[PROB_COL].iloc[0])
                label = apply_threshold([prob], thr)[0]
                st.divider()
                a, b, c = st.columns(3)
                a.metric("Estimated attrition probability", f"{prob:.1%}")
                b.metric("Model classification", label)
                c.metric("Threshold used", f"{thr:.2f}")
                st.progress(min(prob, 1.0))
                st.caption("An estimate from a statistical model trained on historical data, not a statement "
                           "about what this person will do. Probabilities may be poorly calibrated.")
                blocks = [("h", "Prediction"),
                          ("table", [["Estimated probability", "Classification", "Threshold", "Model"],
                                     [f"{prob:.1%}", label, f"{thr:.2f}", bundle["model_name"]]]),
                          ("p", "Probability is a model estimate and may be inaccurate. It is not a certainty."),
                          ("h", "Submitted input values"),
                          ("table", [["Feature", "Value"], *[[k, v] for k, v in st.session_state["single_record"].items()]])]
                st.download_button("⬇️ Download prediction report (PDF)",
                                   make_pdf("Individual Prediction Report", blocks),
                                   "employee_attrition_prediction_report.pdf", "application/pdf")
        else:
            st.download_button("Download CSV template", pd.DataFrame(columns=list(schema)).to_csv(index=False),
                               "attrition_input_template.csv", "text/csv")
            up = st.file_uploader("Employee CSV (one row per employee)", type="csv", key="batch_upload")
            if up:
                if st.session_state.get("batch_name") != up.name:
                    st.session_state.pop("batch_df", None)
                    st.session_state["batch_name"] = up.name
                data, err = read_upload(up)
                if err:
                    st.error(err)
                else:
                    rep = validate_input(data, bundle)
                    st.write(f"**{len(data):,} rows**, {data.shape[1]} columns detected.")
                    if rep["missing"]:
                        st.error("Missing required columns: " + ", ".join(rep["missing"]))
                    if rep["bad_numeric"]:
                        st.error("Non-numeric values in numeric columns: " + ", ".join(rep["bad_numeric"]))
                    if rep["null_cols"]:
                        st.error("Missing values (not filled in automatically): "
                                 + ", ".join(f"{k} ({v})" for k, v in rep["null_cols"].items()))
                    if rep["extra"]:
                        st.info("Ignored extra columns: " + ", ".join(rep["extra"]))
                    if TARGET in data.columns:
                        st.info("Existing `Attrition` column kept as the actual label and not used as a model input.")
                    st.dataframe(data.head(10), width="stretch")
                    if rep["ok"] and st.button("Run predictions", type="primary"):
                        try:
                            st.session_state["batch_df"] = predict_frame(data, bundle, thr)
                        except ValueError as e:
                            st.error(str(e))
            res = st.session_state.get("batch_df")
            if res is not None:
                res = res.copy()
                res[LABEL_COL] = apply_threshold(res[PROB_COL], thr)  # threshold change -> labels only
                n_left = int((res[LABEL_COL] == "Left").sum())
                st.divider()
                m = st.columns(4)
                m[0].metric("Records", f"{len(res):,}")
                m[1].metric("Classified Left", f"{n_left:,}")
                m[2].metric("Classified Stayed", f"{len(res) - n_left:,}")
                m[3].metric("Mean probability", f"{res[PROB_COL].mean():.1%}")
                fig = px.histogram(res, x=PROB_COL, nbins=30, title="Distribution of estimated probabilities")
                fig.add_vline(x=thr, line_dash="dash", annotation_text=f"threshold {thr:.2f}")
                st.plotly_chart(fig, width="stretch")
                st.dataframe(res.head(200), width="stretch")
                st.caption("Predicted labels are model outputs, not observed outcomes. Showing the first 200 rows; "
                           "the CSV contains all rows.")
                d1, d2 = st.columns(2)
                d1.download_button("⬇️ Download all results (CSV)", res.to_csv(index=False),
                                   "employee_attrition_batch_predictions.csv", "text/csv")
                blocks = [("h", "Batch summary"),
                          ("table", [["Records", "Classified Left", "Classified Stayed", "Threshold", "Model"],
                                     [len(res), n_left, len(res) - n_left, f"{thr:.2f}", bundle["model_name"]]]),
                          ("h", "Probability statistics"),
                          ("table", [["Mean", "Median", "Min", "Max"],
                                     [f"{res[PROB_COL].mean():.3f}", f"{res[PROB_COL].median():.3f}",
                                      f"{res[PROB_COL].min():.3f}", f"{res[PROB_COL].max():.3f}"]]),
                          ("p", "Predicted classifications are model outputs, not actual observed attrition."),
                          ("h", "Sample of results (first 15 rows)"),
                          ("table", [[PROB_COL.replace("predicted_attrition_", ""), "classification"],
                                     *res[[PROB_COL, LABEL_COL]].head(15).values.tolist()])]
                d2.download_button("⬇️ Download batch report (PDF)", make_pdf("Batch Prediction Report", blocks),
                                   "employee_attrition_batch_report.pdf", "application/pdf")

# ───────────────────────────── Model Performance ─────────────────────────────
with tab_perf:
    if not bundle:
        st.error(model_err)
    else:
        M, info = bundle["metrics"], bundle["info"]
        st.subheader("How the model was built and tested")
        st.markdown(
            f"- **Selected model:** {bundle['model_name']} (chosen by 5-fold CV average precision on "
            f"{info['n_real_train']} real training rows)\n"
            f"- **Threshold {bundle['threshold']:.2f}:** F1-optimal on out-of-fold predictions\n"
            f"- **Final model** trained on real rows + {info['n_synthetic']:,} synthetic rows (real weighted "
            f"×{info['real_weight']:g})\n"
            f"- **Excluded from inputs:** {', '.join(info['excluded_columns'])}\n"
            f"- **Hold-out:** {info['n_holdout']} real employees never used for training, model selection or "
            "threshold choice")

        st.markdown("##### Candidate comparison (cross-validation, real training rows)")
        cand = pd.DataFrame(M["candidates_cv"]).T.rename(columns={
            "cv_roc_auc": "ROC-AUC", "cv_average_precision": "Avg. precision", "seconds": "Seconds"})
        st.dataframe(cand.round(3), width="stretch")

        st.markdown("##### Hold-out results (real, untouched)")
        keys = ["accuracy", "precision", "recall", "f1", "roc_auc", "average_precision"]
        hold = pd.DataFrame({"Real data only": {k: M["holdout_real_only"][k] for k in keys},
                             "Real + synthetic (deployed)": {k: M["holdout_final"][k] for k in keys}}).round(3)
        st.dataframe(hold, width="stretch")
        st.caption(f"With only {info['n_holdout']} hold-out employees (~47 who left), differences of a few points "
                   "are within noise. Synthetic data cannot add new information beyond the real rows; its value is "
                   "mainly regularisation. These scores do not guarantee performance on other organisations.")

        cm = M["holdout_final"]["confusion_matrix"]
        a, b = st.columns(2)
        z = [[cm["tn"], cm["fp"]], [cm["fn"], cm["tp"]]]
        fig = px.imshow(z, text_auto=True, x=["Pred Stayed", "Pred Left"], y=["Actual Stayed", "Actual Left"],
                        color_continuous_scale="Blues", title="Confusion matrix (hold-out)")
        fig.update_layout(coloraxis_showscale=False, height=340)
        a.plotly_chart(fig, width="stretch")
        a.caption("False positive = flagged as Left but stayed. False negative = missed a real leaver.")
        imp = pd.DataFrame(M["importance"]).head(15).iloc[::-1]
        fig2 = px.bar(imp, x="importance", y="feature", orientation="h", error_x="std",
                      title="Permutation importance (drop in avg. precision on hold-out)")
        fig2.update_layout(height=340, margin=dict(t=50, b=10))
        b.plotly_chart(fig2, width="stretch")
        b.caption("Shows which features the model relies on, not what causes attrition.")

        blocks = [("h", "Methodology"),
                  ("p", f"Model: {bundle['model_name']}. Threshold {bundle['threshold']:.2f}. Seed {info['seed']}. "
                        f"Excluded columns: {', '.join(info['excluded_columns'])}."),
                  ("h", "Candidate comparison (CV on real training rows)"),
                  ("table", fmt_table([[k, v["cv_roc_auc"], v["cv_average_precision"]]
                                       for k, v in M["candidates_cv"].items()], ["Model", "ROC-AUC", "Avg. precision"])),
                  ("h", "Hold-out metrics (real, untouched)"),
                  ("table", fmt_table([[k, M["holdout_real_only"][k], M["holdout_final"][k]] for k in keys],
                                      ["Metric", "Real only", "Real + synthetic"])),
                  ("p", f"Confusion matrix: TN={cm['tn']}, FP={cm['fp']}, FN={cm['fn']}, TP={cm['tp']}."),
                  ("h", "Top features (permutation importance)"),
                  ("table", fmt_table([[d["feature"], d["importance"]] for d in M["importance"][:10]],
                                      ["Feature", "Importance"])),
                  ("p", "Importance shows predictive reliance, not causation.")]
        st.download_button("⬇️ Download model evaluation report (PDF)",
                           make_pdf("Model Evaluation Report", blocks),
                           "employee_attrition_model_evaluation.pdf", "application/pdf")