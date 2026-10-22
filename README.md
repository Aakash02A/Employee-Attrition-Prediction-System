# Employee Attrition Prediction System

An educational, reproducible people-analytics application for exploring historical attrition patterns, comparing conventional classifiers, and demonstrating cautious probability estimates. It is not a validated production HR decision system.

> This application is an educational machine learning prototype using historical data. Attrition probabilities are estimates and may be inaccurate or affected by bias in the data. They must not be used as the sole basis for employment decisions.

## Features

- CSV ingestion, target validation, missing/duplicate/constant/identifier reporting.
- Interactive Streamlit overview, data explorer, and exploratory charts with counts/denominators.
- Reproducible 70/15/15 stratified training/validation/test partitions.
- Logistic Regression, Random Forest, and Extra Trees pipelines with in-pipeline imputation, encoding, and scaling.
- Validation average-precision model selection, validation-only F1 threshold selection, and one final held-out test evaluation.
- Accuracy, precision, recall, F1, ROC-AUC, average precision, Brier score, confusion matrix, ROC/PR curves, and training time.
- Single-record and in-memory batch CSV predictions using the persisted pipeline; downloadable prediction results.
- Held-out permutation importance, optional aggregate subgroup summaries, and responsible-use disclosures.
- Synthetic unit tests; no Kaggle account is required just to install or launch the app.

## Technology

Python 3.11+, Pandas/NumPy for data, scikit-learn for preprocessing and models, Streamlit for UI, Plotly for interactive charts, Joblib for locally generated trusted artifacts, Pytest and Ruff for QA.

## Dataset

The default dataset is IBM HR Analytics Employee Attrition & Performance, commonly distributed as `WA_Fn-UseC_-HR-Employee-Attrition.csv`: [Kaggle dataset page](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset). It is a fictional educational dataset, not actual employer records. The target is `Attrition` (`Yes` = left, `No` = stayed).

Place the CSV at `data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv`, or pass a different file path to the commands below. The app does not download it or require Kaggle credentials. Analysis/prediction uploads are held in memory and are not persisted by default.

## Installation

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

macOS/Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

If you prefer the requirements file, run `python -m pip install -r requirements.txt` and then `python -m pip install -e .` so the local `src` package is importable by the training module.

## Validate, train, and run

Run from the repository root after installation.

```bash
python scripts/validate_dataset.py --input data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv
python -m attrition_app.train --data data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv
streamlit run app.py
pytest -q
ruff check .
ruff format .
```

### Smoke-test without the IBM CSV

Generate a deterministic toy CSV (not real employee data and not representative of an employer):

```bash
python scripts/generate_synthetic_data.py --rows 200 --seed 42 --output data/raw/synthetic_attrition.csv
python scripts/validate_dataset.py --input data/raw/synthetic_attrition.csv
python -m attrition_app.train --data data/raw/synthetic_attrition.csv
streamlit run app.py
```

The synthetic generator includes the fields used by the default pipeline and deliberately creates a target signal for exercising the code path. Resulting model metrics only describe this generated toy sample; they are not evidence of performance on the IBM dataset or real employees. The automated tests also generate a deterministic 160-row fixture in memory/temp storage and do not require Kaggle or the raw CSV. Re-run the generator with `--force` only when you intend to replace its output file. To test code without creating a model artifact, run `pytest -q` instead; the integration fixture writes artifacts under pytest's temporary directory.

Validation reports dimensions, target classes when present, duplicates, missingness, constant fields, and identifier-like fields. Training stops with an actionable error if the data/target is invalid or either class has fewer than seven rows, which is needed for the two stratified holdout splits. Training writes `models/attrition_model.joblib` plus JSON/CSV metadata and reports under `reports/`. These locally generated files are git-ignored. Joblib files are pickle-based: load only artifacts generated locally by this project, never user-uploaded models.

## Application guide

- **Overview Dashboard:** historical outcome mix, department/job-role filters, available subgroup rates (department, job role, overtime, satisfaction, work-life balance), tenure/income bands, and a setup state when data is absent.
- **Data Explorer:** local or uploaded CSV preview, schema, missing values, duplicates, numerical/categorical distributions, numeric relationships, and optional aggregate protected-group auditing (minimum group size default 20).
- **Predict Attrition:** dynamic single-profile form or batch CSV upload; required features are checked, extra fields (including target/identifiers) are reported as ignored, and output CSV preserves row order. Adjusting the threshold changes labels, not probabilities.
- **Model Performance:** candidate validation comparison and saved held-out test metrics/curves only; no placeholder scores.
- **Model Explainability:** held-out permutation importance and limitations.
- **About and Limitations:** scope, methodology, privacy, ethics, and reproduction notes.

## Machine-learning methodology

Default exclusions include `Age`, `Gender`, `MaritalStatus`, target, identifier-like fields, and constants. Missing numeric values are median-imputed then scaled; categorical values are most-frequent imputed and one-hot encoded with unseen values ignored. Preprocessing is part of each scikit-learn pipeline and is fitted only on the training partition. Candidate models use class weighting. Selection prioritizes validation average precision, breaking ties with validation F1. For the selected model, the threshold maximizes validation F1 (ties prefer recall, then closeness to 0.50). Test data is evaluated after those choices are fixed and is never used in model selection. False positives flag an employee who stays; false negatives miss an employee who leaves. Threshold choice expresses a trade-off, not a policy recommendation.

Permutation importance measures the change in held-out average precision when one input column is shuffled. It is a global model-reliance summary, not causality. The optional aggregate audit is descriptive, suppresses groups below the chosen size, and is not a fairness certification.

## Foundation model licensing

TabPFN is intentionally not included in the core dependency or prediction path. The cited TabPFN 3.5 model-card terms restrict use to research/limited internal evaluation and prohibit commercial/production use without authorization; check the current [model card](https://huggingface.co/Prior-Labs/tabpfn_3_5) and license before any separate experiment. No TabPFN benchmark was run or is claimed by this project.

## Structure

```text
app.py                         Streamlit overview/dashboard
pages/                         Explorer, prediction, performance, explanations, about
src/attrition_app/              Data, preprocessing, training, evaluation, inference, EDA
scripts/validate_dataset.py     Standalone CSV validator
tests/                          Synthetic unit/integration tests
data/raw/                       User-supplied local dataset (ignored)
models/                          Local model artifact (ignored)
reports/                         Local training reports (ignored)
```

## Limitations and privacy

The public dataset is small, fictional, and may not represent a real organization or current workforce. Historical associations can encode bias, probabilities can be inaccurate and uncalibrated, and no causal interpretation is justified. Direct protected attributes are excluded from predictive features by default, but proxy effects remain possible. Do not use this prototype to rank employees, recommend dismissal, or automate employment actions. Real employee-data use requires authorization, security controls, governance, and legal review. Uploaded data is not sent to external services or persisted by default. Avoid committing datasets, artifacts, or secrets.

TabPFN, SHAP explanations, authentication, databases, production monitoring, and a hosted deployment are not implemented. No deployment has been performed.

## Troubleshooting and demonstration deployment

- **CSV not found:** download the fictional dataset from the source above and use the expected path or pass `--data`.
- **Unexpected target values:** normalize labels to `Yes`/`No` or `1`/`0` and ensure both are represented.
- **Small/imbalanced sample:** training requires at least seven rows in each class for the stratified 70/15/15 split.
- **No predictions:** train locally first; generated artifacts are excluded from Git and should be reproduced from the authorized dataset.
- **Import errors:** activate the virtual environment and install the package from the repository root.

For a demonstration on Streamlit Community Cloud, push the source without private data, choose `app.py`, and install dependencies from `pyproject.toml`/`requirements.txt`. Because model artifacts and datasets are git-ignored, provide only public authorized data and reproduce training in a controlled environment or document a separately governed artifact-delivery mechanism. Verify platform resource and dependency limits before publishing; this repository has not been deployed.
