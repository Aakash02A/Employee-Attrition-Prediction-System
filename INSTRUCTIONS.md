# Instructions — run these in order

These steps were left for you to run locally because they're the
long-running / compute steps (model training, SHAP computation) that
should happen in your own editor/terminal, not baked into the zip.

Everything below assumes your terminal's working directory is the
project root: `attrition-prediction-system/`.

---

## 1. Set up the environment

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Takes 1-3 minutes depending on your connection (xgboost and shap are the
biggest downloads).

---

## 2. Train the model (long-running step)

```bash
python3 src/train.py
```

What it does: loads and cleans the data, trains a Logistic Regression
baseline and an XGBoost model, prints evaluation metrics for both, and
saves the XGBoost model to `models/xgb_model.joblib`.

Expected runtime: 10-30 seconds on a normal laptop CPU (1,470 rows is
small — this won't feel "long," but it's the step people usually forget
to re-run after editing features).

Expected output: ROC-AUC around 0.75-0.85 for both models. If you see
numbers far outside that range, something changed upstream (recheck
`data_prep.py`) — do not proceed until this step looks reasonable.

**If you change anything in `data_prep.py` (add/remove features), you
must re-run this step before anything downstream will be consistent.**

---

## 3. Generate SHAP explanations (long-running step)

```bash
python3 src/explain.py
```

What it does: computes a SHAP value for every feature, for every one of
the 1,470 employees, and saves the top 5 risk drivers per employee to
`outputs/shap_explanations.joblib`.

Expected runtime: 30 seconds to a few minutes — this is the slowest step
in the pipeline because it's per-employee, not a single batch
prediction. If you extend this to a larger dataset later, expect this
step to dominate total runtime; consider sampling employees for
explanation instead of running all of them.

Requires step 2 to have completed first (it loads `models/xgb_model.joblib`).

---

## 4. Sanity-check the recommendation engine (optional, fast)

```bash
python3 src/recommend.py
```

Runs a quick built-in example. If you add new rules to
`INTERVENTION_LIBRARY` in `src/recommend.py`, re-run this to confirm the
matching logic still works before wiring it into the dashboard.

---

## 5. Launch the dashboard

```bash
streamlit run dashboard/app.py
```

Opens in your browser automatically (usually `localhost:8501`). Use the
"Employee index" field to drill into any of the 1,470 employees and see
their risk score, top factors, and recommended actions.

Requires steps 2 and 3 to have completed — the dashboard will show an
error message telling you which one is missing if you skip ahead.

---

## Order matters — full sequence

```bash
python3 src/train.py       # step 2 — creates models/xgb_model.joblib
python3 src/explain.py     # step 3 — creates outputs/shap_explanations.joblib
streamlit run dashboard/app.py   # step 5
```

## If you want to iterate

- Edit `src/data_prep.py` to add/remove features → re-run steps 2 and 3.
- Edit `INTERVENTION_LIBRARY` in `src/recommend.py` → no retraining
  needed, just restart the dashboard.
- Edit model hyperparameters in `src/train.py` (`n_estimators`,
  `max_depth`, etc.) → re-run step 2, then step 3.
