# MASTER BUILD PROMPT — EMPLOYEE ATTRITION PREDICTION SYSTEM
## Complete End-to-End Machine Learning Web Application

### ROLE AND OBJECTIVE

Act as a senior Machine Learning Engineer, Data Scientist, Python Developer, Streamlit Developer, Software Architect, UI/UX Designer, QA Engineer, and Technical Writer.

Your responsibility is to build a complete, functional, end-to-end project named **Employee Attrition Prediction System**.

Build the actual application, not merely an architecture proposal, tutorial, code snippets, notebook, or frontend mockup.

Inspect the available project repository, create or improve the necessary files, implement the machine learning workflow, develop the user interface, run tests, fix errors, and provide accurate instructions for running the finished project.

The final application must allow any person with access to the application to:

1. Open the application without logging in.
2. Explore employee data by uploading a CSV file.
3. Analyze historical attrition patterns when actual attrition labels are available.
4. Upload a CSV containing new employee records and generate batch attrition predictions.
5. Manually enter one employee's details and generate an individual attrition prediction.
6. View estimated attrition probabilities, classification results, visualizations, model performance, and relevant explanations.
7. Download batch prediction results as a CSV file.

The machine learning model will be trained and evaluated separately during development. The application will load the saved, trained model for inference.

**Important product decision:** This application does not require login, registration, user authentication, user roles, account management, or a database for user accounts. Do not add these features.

The project should be simple to run, easy to demonstrate, reproducible, and sufficiently robust for an academic project and portfolio.

---

# 1. PROJECT UNDERSTANDING

## 1.1 What are we building?

Employee Attrition Prediction System is a machine learning application that uses historical employee records to learn patterns associated with employee attrition.

Attrition refers to employees leaving an organization.

The system will use a trained classification model to estimate the probability of attrition for an employee profile and allow users to explore historical attrition patterns in a dataset.

The application has two primary user workflows:

**Workflow A — Upload a CSV**

The user uploads an employee dataset. Depending on its contents, the system allows the user to inspect data quality, explore historical attrition, visualize patterns, and optionally generate batch predictions for employee records.

**Workflow B — Enter employee details manually**

The user opens an individual prediction form, enters the required employee details, clicks the prediction button, and sees the estimated attrition probability and associated classification.

Both workflows use the same saved preprocessing and machine learning pipeline.

## 1.2 Project goals

- Build a genuine end-to-end machine learning application.
- Train and compare multiple classification algorithms.
- Select a model using a documented evaluation procedure.
- Make predictions using a saved model.
- Present results through a polished interactive interface.
- Support historical data analysis and prediction of new records.
- Make the application's outputs understandable to nontechnical users.
- Prevent data leakage and inconsistent preprocessing.
- Protect uploaded records by avoiding unnecessary storage or external transmission.
- Provide tests, documentation, and reproducible setup instructions.

## 1.3 Intended scope

This is an educational machine learning prototype using public employee analytics data and other datasets that users are authorized to process.

It is not a validated production HR decision system.

The application estimates patterns from historical data. It cannot know with certainty whether a particular employee will leave or prove why an employee might leave.

Never market or describe the application as providing guaranteed predictions.

---

# 2. STRICT SCOPE: NO LOGIN OR AUTHENTICATION

The application must open directly to the dashboard.

Do not implement:

- Login pages.
- Registration pages.
- Password fields.
- User accounts.
- Authentication providers.
- User role management.
- Password-reset functionality.
- Account profiles.
- JWT authentication.
- An authentication database.
- A separate authentication backend.

Do not introduce a database simply to store uploaded CSV files or employee prediction history.

The application is intended to work without a sign-in process.

Use Streamlit as the primary web interface.

Use Streamlit session state only for lightweight interface state where needed, such as selected filters, current threshold settings, or temporary navigation state.

Do not rely on session state as permanent storage.

Do not persist individual employee inputs, batch uploads, or prediction results to disk by default.

Do not transmit uploaded employee data to external APIs or model-hosting services.

The saved model must be loaded locally from a trusted artifact generated during model training.

The default application must not require a Kaggle API key, a Hugging Face access token, an external database, or an external ML inference API.

A local development environment is sufficient.

---

# 3. TECHNOLOGY STACK

Use the following stack unless a concrete compatibility problem requires a documented alternative.

| Technology | Responsibility |
|---|---|
| Python | Main programming language |
| Pandas | Data loading, tabular processing, analysis |
| NumPy | Numerical calculations |
| Scikit-learn | Preprocessing, training, classification, evaluation |
| Streamlit | Interactive web application |
| Plotly | Interactive charts and graphs |
| Joblib | Save and load trusted local model artifacts |
| Pytest | Automated tests |
| Ruff | Linting and code formatting |
| Git and GitHub | Version control and portfolio hosting |
| Jupyter Notebook | Optional experimentation and exploratory analysis |
| Hugging Face TabPFN | Optional, separately controlled model benchmark |

Use a compatible, documented Python version, such as Python 3.11, subject to the selected dependency versions.

Prefer a simple, modular Python architecture.

Do not use React, Node.js, MongoDB, PostgreSQL, FastAPI, Docker, or microservices in the initial version unless a genuine requirement emerges. Streamlit is sufficient for the required application.

The optional foundation model must not be a dependency required to start the core application.

---

# 4. DATASET

## 4.1 Primary dataset

Use the IBM HR Analytics Employee Attrition & Performance dataset.

Dataset source:

https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset

The commonly distributed CSV filename is:

`WA_Fn-UseC_-HR-Employee-Attrition.csv`

It commonly contains 1,470 records and 35 columns. Verify the actual file programmatically rather than assuming these figures.

The dataset consists of fictional employee data and must not be presented as genuine records from a real employer.

The application should work with the supplied default dataset when available, but it must also allow users to upload compatible CSV files.

Do not require a Kaggle API key or automatic download just to run the application.

## 4.2 Target variable

The target variable is:

`Attrition`

Typical values:

- `Yes`: the employee left.
- `No`: the employee stayed.

Internally, normalize the target carefully. In the UI, display understandable labels such as:

- Left.
- Stayed.

Do not assume that the target column exists in a dataset intended only for prediction.

Some uploaded datasets will contain historical outcomes; others will contain only employee features.

## 4.3 Example features

The default dataset may contain fields such as:

- Age.
- Department.
- JobRole.
- BusinessTravel.
- OverTime.
- MonthlyIncome.
- JobSatisfaction.
- EnvironmentSatisfaction.
- WorkLifeBalance.
- YearsAtCompany.
- YearsInCurrentRole.
- YearsSinceLastPromotion.
- TotalWorkingYears.
- NumCompaniesWorked.
- YearsWithCurrManager.

Inspect the actual feature names and data types in the supplied data.

Do not assume every uploaded dataset has the same columns.

For prediction, validate the presence of the exact features expected by the trained model. Do not invent missing feature values simply to make a prediction succeed.

---

# 5. TWO DISTINCT DATA WORKFLOWS

This distinction is central to the design.

The application must clearly distinguish among:

1. Historical data analysis.
2. Batch prediction on new employee records.
3. Model training during development.

These operations must not be mixed together.

## 5.1 Historical analysis

When a user uploads a CSV for analysis, the application should inspect the supplied dataset and calculate descriptive statistics.

If the CSV contains a valid `Attrition` target column, it can calculate:

- Historical attrition rate.
- Number of employees who left.
- Number of employees who stayed.
- Attrition rates by available categories.
- Other descriptive statistics.

If the target is absent, do not invent historical outcomes or report actual attrition rates.

The uploaded dataset can still be inspected and analyzed, but outcome-based analysis must be marked unavailable when actual labels are missing.

## 5.2 Batch prediction

When the user wants predictions for new employee records, use a separate prediction workflow.

The user uploads a CSV that includes the feature columns expected by the trained model.

The app validates the records, generates predictions using the saved model, and provides a downloadable result file.

Batch predictions must not retrain, fine-tune, or modify the saved model.

If the uploaded file already contains an `Attrition` column, identify that column as an existing label and exclude it from predictive inputs. Clearly distinguish existing actual labels from model-generated results.

Do not overwrite actual labels with predicted labels.

Use distinct column names for model outputs, such as:

- `predicted_attrition_probability`
- `predicted_attrition`

Where relevant, users may compare actual labels and predictions for analysis, but actual labels must not enter the feature matrix.

## 5.3 Manual prediction

The user enters one employee profile in a form.

The application validates the fields and passes the values into exactly the same fitted preprocessing and model pipeline used in batch prediction.

The app returns the estimated probability and classification.

Do not train the model again when an individual prediction form is submitted.

## 5.4 Data isolation

Files uploaded for analysis or prediction must be handled in memory wherever practical.

Do not replace the original training dataset when a user uploads a file.

Do not change the saved training model based on uploaded data.

Do not automatically use user uploads as training data.

Model training must remain a separate development or maintenance operation.

---

# 6. PROJECT ARCHITECTURE

Create a modular project structure similar to the following:

```text
employee-attrition-prediction/
│
├── app.py
│
├── pages/
│   ├── 02_Data_Explorer.py
│   ├── 03_Predict_Attrition.py
│   ├── 04_Model_Performance.py
│   ├── 05_Model_Explainability.py
│   └── 06_About_and_Limitations.py
│
├── src/
│   └── attrition_app/
│       ├── __init__.py
│       ├── config.py
│       ├── schema.py
│       ├── data_loader.py
│       ├── validation.py
│       ├── eda.py
│       ├── preprocessing.py
│       ├── train.py
│       ├── evaluate.py
│       ├── predict.py
│       ├── explainability.py
│       ├── visualizations.py
│       └── utils.py
│
├── scripts/
│   └── validate_dataset.py
│
├── notebooks/
│   └── 01_exploratory_data_analysis.ipynb
│
├── data/
│   ├── raw/
│   │   └── .gitkeep
│   └── processed/
│       └── .gitkeep
│
├── models/
│   └── .gitkeep
│
├── reports/
│   └── .gitkeep
│
├── tests/
│   ├── test_data_loader.py
│   ├── test_validation.py
│   ├── test_preprocessing.py
│   ├── test_training.py
│   ├── test_prediction.py
│   └── test_app.py
│
├── requirements.txt
├── pyproject.toml
├── .gitignore
└── README.md
```

Adapt this structure when necessary, but maintain clear separation between presentation, data handling, preprocessing, model training, evaluation, and inference.

Do not create empty modules simply to satisfy the directory layout.

Each file must have an actual purpose.

The `src` directory must be importable using a documented installation or execution setup.

---

# 7. MACHINE LEARNING PIPELINE

Implement a reproducible supervised binary classification workflow.

## 7.1 Data preparation

The training pipeline must:

1. Load the historical dataset.
2. Validate the dataset schema.
3. Validate the target values.
4. Identify numerical and categorical features.
5. Inspect missing values and duplicates.
6. Exclude the target from predictive features.
7. Identify identifiers and constant columns.
8. Apply the documented feature policy.
9. Separate features from target.
10. Split the data into training, validation, and test subsets.

Document all transformations.

Do not silently remove records or columns without reporting the action.

## 7.2 Sensitive attributes and identifiers

For the default model, exclude sensitive attributes and potential protected features such as:

- Gender.
- MaritalStatus.
- Age, unless an explicitly documented experimental configuration authorizes its use.

Also evaluate exclusion of fields such as EmployeeNumber, EmployeeCount, Over18, and StandardHours when they appear in the dataset.

Use an explicit feature policy instead of simply training on every available field.

Where authorized data is available, aggregate fairness analysis can be performed separately. Do not automatically use sensitive information to make employee-level predictions.

## 7.3 Preprocessing

Use Scikit-learn `Pipeline` and `ColumnTransformer` where appropriate.

Numerical features:
- Handle missing values if present.
- Scale numerical data for models that benefit from scaling.

Categorical features:
- Handle missing values if present.
- Encode categorical variables using a suitable encoder, such as `OneHotEncoder(handle_unknown="ignore")`.

Fit preprocessing on training data only.

Apply the fitted transformations consistently to validation, test, single-record, and batch-prediction data.

Avoid creating independent preprocessing implementations for training and inference.

## 7.4 Data splitting

Use stratified splitting where feasible.

A reasonable default is:

- 70% training.
- 15% validation.
- 15% final test.

Set a fixed random seed, such as `42`.

If the dataset or class distribution makes this split unsuitable, select a documented alternative.

Use training data to fit candidate models.

Use validation data to compare candidates and select the prediction threshold.

Keep the final test set untouched until model selection and threshold selection have been completed.

Never use final test performance as a repeated tuning objective.

## 7.5 Candidate models

Implement and compare at least three conventional classifiers.

### Logistic Regression

Use as an interpretable baseline with appropriate preprocessing.

### Random Forest Classifier

Use as a nonlinear ensemble candidate with controlled hyperparameters and a fixed random seed.

### Extra Trees Classifier

Use as an additional tree-based candidate.

You may include additional appropriate models if justified, but do not add complexity without a reason.

Do not assume any particular candidate is best before evaluation.

## 7.6 Class imbalance

The dataset may have significantly more employees who stayed than employees who left.

Therefore:

- Do not evaluate with accuracy alone.
- Report precision and recall for the attrition class.
- Consider class-weighted classifiers.
- Compare useful model candidates on validation data.
- Use an appropriate classification threshold.

Resampling techniques such as SMOTE are optional and must only be used within training folds if implemented.

## 7.7 Metrics

Calculate actual metrics from actual predictions.

Include:

- Accuracy.
- Precision.
- Recall.
- F1-score.
- ROC-AUC.
- Average precision or precision-recall AUC.
- Confusion matrix.
- Classification report.

Where suitable, also report:

- Brier score.
- Calibration curve.
- Training duration.
- Prediction duration.

Explain false positives and false negatives.

Do not fabricate scores or promise a specific accuracy level.

## 7.8 Classification threshold

Keep estimated probability separate from the predicted class.

The application should display the estimated probability and the currently selected classification threshold.

Use validation results to choose a documented default threshold.

Allow the user to change the threshold for interactive exploration where appropriate.

Changing the threshold must change the classification label, not the model's underlying estimated probability.

Avoid presenting uncalibrated probability outputs as guaranteed or perfectly calibrated real-world probabilities.

## 7.9 Model selection

Choose the best-supported model using a predefined validation-based selection rule that prioritizes a suitable metric, such as average precision, with other evaluation metrics considered according to the objective.

Do not choose the model using final test metrics.

Once selected, evaluate it on the held-out test set.

Save the fitted pipeline, the threshold, model metadata, and evaluation results.

---

# 8. MODEL PERSISTENCE AND INFERENCE

The model must be trained separately and saved to a local artifact.

Use Joblib or another compatible serialization mechanism for trusted locally generated models.

The artifact should contain or reference:

- Fitted preprocessing pipeline.
- Fitted estimator.
- Feature schema.
- Feature list.
- Target definition.
- Classification threshold.
- Model version.
- Training configuration.
- Random seed.
- Model selection details.
- Validation metrics.
- Final test metrics.
- Compatible dependency versions.
- Training metadata.

Use a documented path such as:

`models/attrition_pipeline.joblib`

Store metadata separately in JSON if that produces a clearer architecture.

Do not load arbitrary model artifacts supplied by users.

Only load artifacts generated and maintained by the project.

If the model is missing or incompatible:
- Do not generate fake predictions.
- Display a clear explanation.
- Explain how to train or install the project's trusted local model.
- Keep pages that do not require a model usable.

The application should not retrain automatically on startup or on every page interaction.

---

# 9. OPTIONAL HUGGING FACE MODEL

Evaluate the optional model:

`Prior-Labs/tabpfn_3_5`

Reference:

https://huggingface.co/Prior-Labs/tabpfn_3_5

It is a foundation model for structured tabular prediction, not an attrition classifier automatically trained on our particular dataset.

If the model is compatible with the environment and its current license permits the planned evaluation:
- Fit it on the training data.
- Evaluate it with an appropriate validation protocol.
- Compare its results and compute costs against the conventional classifiers.
- Record its dependency and model versions.

The model card has imposed restrictions on commercial and production use. Verify the current license and terms before integrating it.

Do not deploy or make prohibited use of TabPFN 3.5 under a restricted license.

Keep the foundation model optional.

The core application must work without it, and the standard Scikit-learn model pipeline must remain the default inference path unless another legally appropriate, tested configuration is deliberately selected.

Do not require a Hugging Face account, access token, or remote inference endpoint for basic application use.

Do not upload the user's employee data to Hugging Face.

If the optional model cannot run, explain the limitation and continue with the conventional ML application.

---

# 10. STREAMLIT APPLICATION DESIGN

Build a polished and cohesive analytics interface.

The user must land directly on the dashboard without any login page.

Use Streamlit's supported layout and navigation mechanisms.

The interface should be intuitive to a person who understands employee data but may not understand machine learning.

Use Plotly for interactive charts.

Use appropriate headings, spacing, readable typography, restrained colors, accessible form labels, useful tooltips, and actionable error messages.

Do not create decorative charts that have no meaning.

Do not populate the application with fake prediction results or fake model evaluation scores.

Use actual data or clearly marked example content.

## PAGE 1: OVERVIEW DASHBOARD — `app.py`

Purpose: provide an overview of the selected dataset and its historical attrition patterns.

### Dataset selection and initial state

- Attempt to load the configured default dataset if available.
- If the default dataset is missing, show a clear upload option for in-memory analysis.
- Explain that uploading data for analysis does not train the model.
- Never silently replace the model's training data.

### KPI cards

When the relevant data is available, display:
- Total employee records.
- Number of employees who left.
- Number of employees who stayed.
- Historical attrition rate.
- Number of available input features.
- Trained model status, where applicable.

Compute every displayed value from actual data and metadata.

If the target is absent, mark target-dependent statistics as unavailable rather than estimating actual historical attrition.

### Charts

Where the relevant columns exist, include:
- Attrition distribution.
- Historical attrition by department.
- Historical attrition by job role.
- Historical attrition by overtime.
- Historical attrition by job satisfaction.
- Historical attrition by work-life balance.
- Historical attrition by tenure or income band.

Add helpful filters where useful.

Handle missing categories, empty selections, invalid values, and small subgroups gracefully.

Clearly distinguish historical attrition rates from predicted attrition probabilities.

### Initial state

If the dataset and model are absent, show an informative landing state explaining how users can upload data and how the project maintainer can train the model.

Do not crash or display fabricated metrics.

---

## PAGE 2: DATA EXPLORER — `pages/02_Data_Explorer.py`

Purpose: let users upload and inspect an employee dataset without training or modifying the ML model.

### Features

Provide:
- CSV upload.
- Dataset preview.
- Row and column counts.
- Column names and data types.
- Missing-value report.
- Duplicate-row count.
- Constant-column detection.
- Potential identifier detection.
- Numerical summaries.
- Categorical summaries.
- Numerical feature distribution charts.
- Categorical frequency charts.
- Optional correlation analysis.
- Optional group summaries.
- Historical attrition analysis if a valid target is available.

Users should be able to inspect files with unexpected schemas without the application immediately crashing.

Use clear warnings for invalid or unsupported columns.

Provide meaningful messages when the dataset cannot support a requested analysis.

Group summaries are descriptive statistics, not fairness certification.

Do not automatically train a model when a dataset is uploaded on this page.

Do not permanently save uploaded files by default.

Keep the uploaded dataset separate from the model's original training dataset.

If a user wants predictions, direct them to the dedicated prediction page.

---

## PAGE 3: PREDICT ATTRITION — `pages/03_Predict_Attrition.py`

Purpose: provide the two core prediction workflows.

The page requires a compatible trained local model.

Display a clear setup message if a trusted model artifact is unavailable.

### Workflow A: SINGLE EMPLOYEE PREDICTION

Create a clean employee input form dynamically based on the trained model's expected feature schema.

Organize the inputs logically into sections such as:
- Job and department information.
- Work experience.
- Compensation.
- Satisfaction and working conditions.

Use suitable input widgets:
- Number inputs for numerical features.
- Dropdowns for categorical features.
- Appropriate validation and constraints.

Do not require personally identifying information.

Do not add employee name, email, phone number, or employee ID unless genuinely required by an explicit project need. They are not required for the default prediction workflow.

When the user submits the form:

1. Validate the input.
2. Check that every required feature is present.
3. Create a data frame with exactly the expected input feature schema.
4. Apply the saved preprocessing pipeline.
5. Generate a probability estimate from the fitted model.
6. Apply the selected threshold to obtain the classification.
7. Display the outputs.

### Results display

Show:
- Estimated attrition probability.
- Classification at the current threshold.
- Current threshold value.
- A simple probability visualization.
- A concise explanation of uncertainty.
- Model-related feature explanations if supported.

Use neutral language.

Do not say that the employee will definitely leave or that the prediction reveals their true intentions.

Use a result format such as:

**Estimated attrition probability:** 0.63, or 63%.

**Model classification:** Left, at a threshold of 0.50.

Clearly identify such values as actual runtime outputs, not examples. The displayed values must come from the fitted model.

Allow the user to reset the form and enter another profile.

Do not store individual records after the prediction unless the user explicitly downloads a result or separately chooses a documented export feature.

### Workflow B: BATCH CSV PREDICTION

Allow the user to upload a CSV containing multiple employee records.

Expected workflow:

1. Upload the CSV.
2. Validate file format and required feature columns.
3. Display the detected row count and column issues.
4. Preview the input records.
5. Allow the user to initiate predictions.
6. Run inference using the saved model.
7. Display the prediction summary and result table.
8. Allow the user to download the resulting CSV.

The result file should preserve source row order and include the original input columns together with:
- `predicted_attrition_probability`
- `predicted_attrition`

Optional additional fields can include the threshold used or a concise prediction status.

Avoid overwriting existing target or identifier fields.

If the upload already contains `Attrition`, retain the original column as an actual label and exclude it from model features. Use separate names for predictions.

Report required columns that are missing and unexpected columns that were ignored.

Do not silently fabricate values for missing required features.

Handle unknown categorical values according to the fitted preprocessing pipeline.

Do not persist the input upload to disk by default.

### Threshold control

Provide a clear threshold selector or slider where appropriate.

When the threshold changes:
- Keep estimated probabilities unchanged.
- Recalculate classification labels.
- Update summary counts and charts.
- Update the threshold displayed alongside the results.

Explain that different thresholds trade recall against precision.

Do not use the final test dataset to select a threshold through this page.

### Prediction safeguards

- Do not retrain the model because an upload was made.
- Do not automatically learn from predicted labels.
- Do not send employee records to external APIs.
- Do not persist records silently.
- Do not produce predictions from a missing or incompatible artifact.
- Validate the upload before invoking the model.
- Handle empty and malformed CSV files gracefully.

---

## PAGE 4: MODEL PERFORMANCE — `pages/04_Model_Performance.py`

Purpose: let users review the actual performance of the training workflow.

Show results saved from the training process, not values calculated from fabricated or unrelated sample data.

### Required sections

**Model comparison**

Display validation metrics for all trained candidates:
- Logistic Regression.
- Random Forest.
- Extra Trees.
- Optional foundation model only if it was actually trained and evaluated.

**Selected model**

Show the chosen model, its selection criteria, and its metadata.

**Evaluation metrics**

Display:
- Accuracy.
- Precision.
- Recall.
- F1-score.
- ROC-AUC.
- Average precision.
- Confusion matrix.

Include ROC and precision-recall curves when the required probability outputs and evaluation data are available.

**Held-out test results**

Show the final evaluation of the selected model on the held-out test set.

Keep validation and test results visually distinct.

The user must be able to understand that:
- Validation metrics supported model selection.
- Final test metrics estimate performance on a previously untouched subset of the supplied dataset.
- Neither guarantees performance on new organizations or people.

Explain false positives and false negatives accurately.

If no model has been trained, show a helpful empty state. Do not display a fabricated high accuracy to make the application look complete.

---

## PAGE 5: MODEL EXPLAINABILITY — `pages/05_Model_Explainability.py`

Purpose: explain which features influenced model behavior in the evaluated dataset.

Implement a real, documented global feature-importance method.

Use permutation importance with the held-out evaluation features and an explicitly stated scoring measure, such as average precision, where appropriate.

Display:
- Ranked features.
- Importance values.
- A horizontal bar chart.
- A clear description of the method.
- Warnings about interpretation limitations.

If SHAP is optionally integrated, verify compatibility and label the method correctly.

Do not create hardcoded or randomized feature-importance values.

Explain that importance indicates how a feature contributes to the model's predictive performance under a particular evaluation procedure. It does not prove that a factor causes attrition.

Do not claim that the default global importance chart explains every individual prediction.

If the required model metadata or trusted data is unavailable, provide a meaningful empty state.

---

## PAGE 6: ABOUT AND LIMITATIONS — `pages/06_About_and_Limitations.py`

Explain:
- Project objective.
- Dataset source.
- Fictional nature of the default dataset.
- Machine learning approach.
- Technology stack.
- Target variable.
- Prediction workflow.
- Model evaluation methodology.
- Privacy behavior.
- Model training instructions.
- Model metadata.
- Limitations.
- Ethical considerations.
- Optional model licensing.

Display the locally trained model's information when available.

Include the following statement:

"This application is an educational machine learning prototype using historical data. Attrition probabilities are estimates and may be inaccurate or affected by bias in the data. They must not be used as the sole basis for employment decisions."

Explain that no login is required and that uploads are processed in memory by default.

Do not claim a formal fairness certification or production readiness.

---

# 11. DATA VALIDATION AND ERROR HANDLING

Create reusable validation functions.

Support:
- Valid CSV files.
- Missing files.
- Empty files.
- Invalid file formats.
- Malformed CSV data.
- Missing feature columns.
- Unexpected extra columns.
- Duplicate rows.
- Missing values.
- Wrong numerical types.
- Unknown categories.
- Missing target column.
- Unexpected target values.
- Single-class training data.
- Insufficient class examples.
- Missing model artifacts.
- Corrupted or incompatible artifacts.
- Optional dependency failures.

Show actionable messages rather than raw exceptions or stack traces.

Log technical details for debugging without exposing sensitive employee records.

Never silently substitute a random prediction for an actual model result.

---

# 12. PRIVACY AND RESPONSIBLE USE

The application does not have authentication. Treat this as a deliberate scope decision, not a reason to ignore privacy.

Implement the following:

1. Process uploads in memory wherever practical.
2. Do not automatically persist uploaded data or predictions.
3. Do not transmit employee records to third-party services.
4. Do not commit real employee datasets to Git.
5. Do not collect unnecessary personal identifiers.
6. Validate uploads and impose a reasonable configurable file-size limit.
7. Do not execute uploaded code.
8. Do not load arbitrary uploaded model artifacts.
9. Do not log complete employee records.
10. Do not use predictions for automated employment actions.
11. Clearly explain uncertainty and potential bias.
12. Use synthetic or authorized data in demonstrations.

Because the application has no login, do not imply that user-specific access controls or account isolation exist.

If the application is deployed publicly, uploads and predictions are accessible to anyone who can access the app, subject to hosting and network configuration. Use the fictional example dataset for public demonstrations unless appropriate security and authorization controls have been established for real data.

Do not describe the application as secure for confidential HR records merely because uploads are not saved by default.

---

# 13. MODEL TRAINING COMMAND

Training must be separate from the running application.

Provide a reproducible training command, such as:

```bash
python -m attrition_app.train \
  --data data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv
```

Adapt command syntax if necessary, but ensure it matches a real implemented entry point.

Training should:
1. Load and validate the chosen training file.
2. Prepare training, validation, and test splits.
3. Fit preprocessing on training data.
4. Train candidate models.
5. Calculate validation metrics.
6. Select a model using the predefined validation rule.
7. Select a threshold using validation evidence.
8. Evaluate the selected model on held-out test data.
9. Save the fitted model bundle.
10. Save metadata and real evaluation results.
11. Save a model comparison report.
12. Print a useful completion summary.

Do not train the model when an application user uploads a prediction CSV.

Do not trigger retraining automatically on Streamlit startup.

If training fails, report the cause and do not overwrite a previously valid model with an invalid artifact.

---

# 14. COMMAND-LINE SETUP AND EXECUTION

Create clear setup instructions for Windows, macOS, and Linux as applicable.

## 14.1 Create the virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS and Linux:

```bash
source .venv/bin/activate
```

## 14.2 Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 14.3 Validate the dataset

Provide a working command such as:

```bash
python scripts/validate_dataset.py \
  --input data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv
```

## 14.4 Train the model

```bash
python -m attrition_app.train \
  --data data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv
```

Ensure Python can import the package from the project root with the documented environment setup. Do not leave import paths dependent on undocumented IDE configuration.

## 14.5 Start the application

```bash
streamlit run app.py
```

The browser should display the overview dashboard directly without asking for credentials.

## 14.6 Run the tests

```bash
pytest -q
```

Add a documented Ruff command for linting.

Verify every command before putting it in the final README.

---

# 15. TESTING

Implement automated tests using Pytest.

Use small synthetic fixtures where practical so the test suite does not require internet access or the full IBM dataset.

Test at least:

### Data loading
- Valid CSV.
- Missing file.
- Malformed CSV.
- Empty file.
- Missing target.
- Invalid target values.

### Preprocessing
- Numerical features.
- Categorical features.
- Missing values.
- Unknown categories.
- Input column order.
- Excluded identifiers.
- Target-column exclusion.
- No preprocessing leakage.

### Training
- Candidate models fit on valid data.
- Invalid datasets fail safely.
- Stratified splitting works when supported by the data.
- Model selection relies on validation metrics.
- Threshold selection does not use the final test set.
- Metadata is saved correctly.

### Prediction
- Single-profile prediction.
- Batch CSV prediction.
- Missing feature validation.
- Extra column reporting.
- Probability values are in the valid range.
- Classification changes when the threshold changes.
- Changing the threshold does not change the probability.
- Saved and reloaded model produces consistent predictions.

### Application
- Dashboard handles missing datasets.
- Prediction page handles missing model artifacts.
- Empty file uploads produce useful messages.
- No fabricated metrics are shown.
- Data Explorer does not automatically train models.
- Uploading prediction data does not modify the trained model.

Include appropriate Streamlit testing for important page states and controls where practical.

Do not weaken tests merely to make them pass.

---

# 16. USER INTERFACE DESIGN

The application must feel like a coherent, professional HR analytics dashboard.

Use:
- Consistent typography.
- Well-structured sections.
- Restrained colors.
- Readable metric cards.
- Interactive Plotly visualizations.
- Responsive layouts.
- Clear navigation.
- Helpful field labels.
- Actionable error messages.
- Useful empty states.

Make the main workflows easy to discover.

On the prediction page, clearly separate single-record prediction from batch prediction.

Use consistent terminology for:
- Historical attrition.
- Estimated probability.
- Classification threshold.
- Model classification.
- Validation metrics.
- Test metrics.

Do not make every statistic a giant KPI card.

Do not add animations, unnecessary libraries, or decorative features that detract from usability.

Every visible button, input, upload control, and filter must work.

If a feature cannot be implemented, do not present it as completed.

---

# 17. PERFORMANCE AND DEPENDABILITY

Use caching appropriately for:
- Trusted local dataset loading.
- Trusted local model loading.
- Expensive deterministic computations.

Avoid unnecessary cache retention of uploaded employee records.

Ensure changes to model artifacts or relevant configurations do not cause stale model results.

The core application should run on a normal development laptop using the default dataset and standard Scikit-learn models.

Make TabPFN, SHAP, and other heavy optional dependencies optional rather than essential to startup.

The absence of the default dataset, saved model, or optional dependencies must not cause unrelated pages to crash.

---

# 18. GIT AND DELIVERABLES

Create a suitable `.gitignore` that excludes:
- Virtual environments.
- Python caches.
- Local environment variables and secrets.
- Unnecessary generated files.
- Private employee data.
- Local model artifacts when appropriate for their size and licensing.
- Test caches and temporary files.

Do not commit a real employee database.

Do not include secrets in the source code.

Create a complete `README.md` describing:
- Project objective.
- Main features.
- Technology stack.
- Dataset source.
- Installation.
- Dataset placement.
- Dataset validation.
- Model training.
- Model evaluation.
- Application startup.
- CSV prediction workflow.
- Individual prediction workflow.
- Project structure.
- Tests.
- Limitations.
- Privacy precautions.
- Troubleshooting.
- Optional model licensing.

Make the setup instructions copy-paste friendly.

Document future enhancements separately from features actually implemented.

---

# 19. ACCEPTANCE CRITERIA

The project is considered complete when all applicable criteria below have been implemented and verified.

## Core model
- The training workflow runs.
- Multiple conventional classifiers are compared.
- Preprocessing is fitted on training data.
- The held-out test set is not used for selection or threshold tuning.
- Actual model metrics are generated.
- A trusted model artifact is saved.
- The artifact loads correctly for inference.

## Application access
- The dashboard opens without authentication.
- There is no login or registration system.
- There is no requirement for a user-account database.

## Data analysis
- Users can upload a CSV.
- Users can preview and inspect the uploaded data.
- Historical attrition statistics appear when actual labels are available.
- Missing labels do not result in fabricated historical rates.
- Uploading data does not trigger training.
- Uploaded data does not silently replace the default training dataset.

## Prediction
- Users can manually enter a valid employee profile.
- Single-record predictions use the saved model.
- Users can upload a CSV for batch predictions.
- Prediction results contain estimated probabilities and classification labels.
- Users can download the resulting CSV.
- Required feature validation works.
- Changing the threshold does not change the estimated probability.
- No fabricated predictions are displayed.

## Reporting
- Model performance comes from real evaluation results.
- Validation and test metrics are distinguished.
- Feature-importance results are genuine.
- Model limitations are clearly stated.

## Engineering
- Code is modular and reusable.
- Documented commands work.
- The application handles missing files and common errors gracefully.
- Tests execute and real failures are fixed.
- Uploaded data is not automatically persisted.
- The README describes the actual implementation.

## Final verification
- Launch the app locally if execution is available.
- Run the test suite.
- Run static analysis.
- Exercise the essential workflows with actual or synthetic test data.
- Clearly disclose any commands or tests that could not be executed.

Do not claim a deployment, trained model, successful test, or measured accuracy unless it has actually been verified.

---

# 20. IMPLEMENTATION ORDER

Follow this sequence while continuing through the entire application.

### Phase 1 — Inspect and configure
Inspect the repository, define the architecture, establish dependencies, configure paths and logging, and create the initial documentation.

### Phase 2 — Data handling
Build data loading, schema validation, CSV validation, and data-quality reporting.

### Phase 3 — Exploratory analysis
Implement statistical summaries and interactive visualizations.

### Phase 4 — Machine learning pipeline
Build preprocessing, data splitting, conventional model candidates, evaluation, selection, threshold selection, and artifact persistence.

### Phase 5 — Optional Hugging Face experiment
Evaluate the optional tabular foundation model only if compatible and permitted by its current terms.

### Phase 6 — Inference
Implement a shared prediction module for individual inputs and batch CSV processing.

### Phase 7 — Streamlit application
Build all six pages: Overview Dashboard, Data Explorer, Predict Attrition, Model Performance, Model Explainability, and About and Limitations.

### Phase 8 — Testing and robustness
Test core data workflows, model behavior, prediction consistency, error handling, and application startup states. Correct actual implementation problems.

### Phase 9 — Documentation and delivery
Complete the README, environment setup, training commands, tests, limitations, and final delivery report.

These phases are implementation steps, not reasons to stop after building a basic interface. Complete all feasible stages within the available environment.

---

# 21. RULES FOR THE CODING AGENT

1. Inspect existing files before modifying them.
2. Preserve useful code that already works.
3. Implement working code rather than pseudocode.
4. Do not ask unnecessary clarifying questions when sensible defaults are available.
5. Do not create login, authentication, registration, or account-management functionality.
6. Do not add a database without a real requirement.
7. Do not automatically retrain the model from user uploads.
8. Do not use uploaded employee data as training data unless a separately documented training workflow explicitly requests it.
9. Do not fabricate data, predictions, metrics, or model explanations.
10. Do not silently bypass validation.
11. Do not swallow exceptions and return fake successful results.
12. Keep the conventional ML pipeline independent of optional Hugging Face integrations.
13. Do not silently transmit or persist user data.
14. Use maintainable Python modules and meaningful names.
15. Execute the tests and fix actual failures.
16. Verify documented commands.
17. Do not claim something works unless you have evidence that it works.
18. When execution is impossible, explain the exact limitation.

Do not stop after generating the folder structure or implementing the dashboard. Build the complete workflow through actual model training, saved-model inference, testing, documentation, and verification.

---

# 22. FINAL DELIVERY REPORT

After implementation, summarize:

1. The functionality built.
2. The final project structure.
3. The technology stack.
4. The implemented training and evaluation workflow.
5. Which models were actually trained.
6. Whether the optional Hugging Face integration was usable.
7. The model artifact location.
8. The commands to validate data, train the model, launch the app, and run tests.
9. Actual test results.
10. Actual evaluation metrics if training ran successfully.
11. How users upload CSV files for analysis.
12. How users upload CSV files for batch predictions.
13. How users enter individual employee details for prediction.
14. How prediction results can be downloaded.
15. Any incomplete functionality or unresolved errors.
16. Any required follow-up for deployment.

Separate completed features from planned enhancements and environmental blockers.

The final result must be a working Employee Attrition Prediction System with no authentication requirements, a real saved machine learning pipeline, two practical prediction workflows, historical data analysis, meaningful visualizations, and reproducible setup instructions.

**Start by inspecting the repository and then implement the entire application. Do not finish by merely describing what needs to be coded.**

# ADDITIONAL CORE FEATURE: COMPLETE REPORT GENERATION AND DOWNLOAD

## 1. Objective

Implement a comprehensive report-generation and download system for the Employee Attrition Prediction System.

After the user completes a data analysis, individual prediction, batch prediction, or model evaluation, they must be able to generate and download a professional report containing the actual results.

The main report format must be **PDF**.

For batch predictions, also provide a downloadable CSV containing the complete row-level prediction results.

Report generation must use actual data and computations from the application. Never insert fabricated statistics, predictions, charts, explanations, or evaluation metrics.

## 2. Report Generation Interface

Create a dedicated **Reports & Downloads** page accessible through the Streamlit sidebar.

Also provide relevant download controls directly on the results pages so users can download their reports immediately without navigating elsewhere.

The report interface should support:

- Generate Complete PDF Report.
- Download Dataset Analysis Report.
- Download Prediction Report.
- Download Model Evaluation Report.
- Download Batch Prediction Results as CSV.
- Download Complete Report Package, where technically practical.

Show a brief preview of the report contents before download.

Display helpful messages when a particular report cannot be generated because the necessary analysis, predictions, or model evaluation results are unavailable.

Do not show download buttons that produce empty, fabricated, or invalid reports.

## 3. Complete PDF Report Contents

Create a professional PDF report with a title page, table of contents where appropriate, section headings, tables, charts, page numbers, a generation timestamp, and a footer identifying the project.

The report should include the following sections when the underlying information is available.

### Section A: Executive Summary

Include:
- Project name: Employee Attrition Prediction System.
- Report generation date and time.
- Report type.
- Dataset filename or descriptive dataset identifier.
- Number of records analyzed.
- Main findings from the actual analysis.
- Model used for predictions, if applicable.
- A concise summary of the results.
- Key limitations and responsible-use notice.

The executive summary must be generated from actual results. Do not use hardcoded business conclusions.

### Section B: Dataset Overview

Include:
- Number of rows and columns.
- Target variable, if available.
- Numerical and categorical feature counts.
- Target class distribution.
- Number and percentage of missing values.
- Duplicate record count.
- Constant columns.
- Detected identifier-like columns.
- Data validation warnings.
- Any excluded or ignored columns.

If the uploaded dataset does not contain actual attrition labels, explicitly state that historical attrition statistics cannot be calculated from that dataset.

### Section C: Exploratory Data Analysis

Include suitable charts and findings derived from the available data.

Examples:
- Attrition distribution.
- Historical attrition rate.
- Department-level attrition patterns.
- Job-role comparisons.
- Overtime-related comparisons.
- Satisfaction distributions.
- Numerical feature distributions.
- Selected correlations.
- Other relevant analyses supported by the uploaded dataset.

Include labels, legends, sample sizes, and explanatory captions where appropriate.

Use only analyses actually performed. Omit irrelevant charts instead of inserting empty placeholders.

Describe associations as associations, not proof of causation.

### Section D: Machine Learning Methodology

When the report includes model training or evaluation information, document:
- Target definition.
- Predictive features.
- Excluded fields.
- Preprocessing strategy.
- Training, validation, and test split strategy.
- Random seed.
- Candidate algorithms.
- Class imbalance handling.
- Model-selection criterion.
- Classification threshold.
- Evaluation methodology.

Clearly distinguish the trained model's development workflow from the current user's analysis or prediction workflow.

### Section E: Model Performance

Include actual available results:
- Candidate model comparison table.
- Validation metrics.
- Selected model.
- Held-out test metrics.
- Accuracy.
- Precision.
- Recall.
- F1-score.
- ROC-AUC.
- Average precision.
- Confusion matrix.
- ROC curve.
- Precision-recall curve.
- Calibration results, if calculated.
- Model version and training metadata.

Clearly distinguish validation results from final test results.

If model training or evaluation data is unavailable, state that the section cannot be completed. Do not manufacture metrics or charts.

### Section F: Individual Attrition Prediction

For an individual prediction report, include:
- Estimated attrition probability.
- Classification produced at the selected threshold.
- Actual threshold used.
- Model identifier.
- Prediction timestamp.
- A probability visualization.
- A feature-based explanation, if genuinely supported by the implementation.
- A brief explanation of uncertainty.
- Relevant limitations.

If useful, include the input feature values that were actually submitted for the prediction, subject to a clear privacy-conscious option.

Do not include employee names, emails, phone numbers, or other personal identifiers by default.

Never state that the employee will certainly leave or claim that the model has established the cause of their behavior.

### Section G: Batch Prediction Results

For a batch prediction report, include:
- Source file identifier.
- Number of input records.
- Number of successful predictions.
- Number of rejected or invalid records, if partial processing is supported.
- Selected model.
- Classification threshold.
- Counts classified as `Left` and `Stayed`.
- Distribution of estimated probabilities.
- Appropriate charts.
- Summary statistics.
- Validation warnings.
- Prediction limitations.

Clearly state that predicted classifications are model outputs, not actual observed attrition outcomes.

The PDF may include a manageable, clearly labeled sample of the result table. Do not attempt to fit thousands of employee rows into a PDF without a usable layout.

Provide a separate **complete CSV download** containing all successfully processed input rows, their original row order, and the generated prediction columns.

Use descriptive output columns:
- `predicted_attrition_probability`
- `predicted_attrition`

Preserve any original actual target column without overwriting it.

### Section H: Model Explainability

When real explanation results are available, include:
- Feature-importance method.
- Ranked feature-importance table.
- A readable chart.
- An explanation of how to interpret the results.
- Limitations of the methodology.

Do not present feature importance as proof of causation or evidence that changing a feature will prevent an employee from leaving.

### Section I: Conclusions and Limitations

Generate a concise, evidence-based summary of the results.

Include:
- The main observed data patterns.
- Model performance findings, where available.
- Data-quality limitations.
- Dataset scope and representativeness limitations.
- Uncertainty in individual predictions.
- Possible bias.
- The difference between historical patterns and predicted outcomes.

Avoid automatically generating prescriptive employment decisions.

Include this notice:

"This application is an educational machine learning prototype. Its analyses and attrition predictions are based on the available dataset and may be inaccurate or affected by bias. They must not be used as the sole basis for employment decisions."

## 4. Report Types

Implement the following report options.

**A. Complete Project Report**

A consolidated PDF containing all relevant sections for which results are available, including dataset analysis, model methodology, model performance, explainability, and any predictions included in the current report context.

**B. Dataset Analysis Report**

A PDF containing dataset structure, data quality, descriptive statistics, relevant charts, historical attrition analysis where labels exist, and limitations.

**C. Individual Prediction Report**

A concise PDF containing the selected model's prediction, estimated probability, threshold-based classification, relevant explanation, and limitations for one submitted profile.

**D. Batch Prediction Report**

A PDF containing the batch summary, prediction distribution, charts, validation details, and methodology.

Also provide a separate CSV containing the complete row-level prediction results.

**E. Model Evaluation Report**

A PDF containing candidate model comparisons, validation metrics, final test results, confusion matrix, classification metrics, ROC and precision-recall visualizations, explainability summaries, and model metadata.

Do not require every report to contain all sections. Each report must include the sections relevant to its type.

## 5. Complete Report Package

Where practical, allow the user to download a ZIP file containing a consolidated report package.

The package may contain:
- `complete_report.pdf`
- `dataset_analysis_report.pdf`, when available.
- `prediction_report.pdf`, when available.
- `model_evaluation_report.pdf`, when available.
- `batch_prediction_results.csv`, when available.
- `report_metadata.json`, summarizing included files, the selected model, threshold, dataset summary, and generation timestamp.

Generate the ZIP only when valid report contents are available.

Do not include the trained model artifact, raw employee datasets, credentials, or unnecessary personal information in the package by default.

If ZIP packaging is not supported, the individual download options must still work.

## 6. Technical Implementation

Implement reusable report-generation code in a dedicated module, for example:

`src/attrition_app/reporting.py`

Use a suitable Python PDF-generation library such as ReportLab, and add it to the dependency configuration.

Generate PDF documents in memory using a `BytesIO` buffer where practical.

Use Streamlit's download functionality to deliver report files to the user.

Use actual computed data from the shared analysis, inference, and evaluation modules. Do not independently recalculate conflicting statistics or hardcode report contents.

For PDF charts, render the required visualizations into static images using a supported plotting workflow, or create suitable PDF-native charts. Do not rely on interactive web charts displaying directly inside the PDF.

Make tables readable:
- Handle long text.
- Wrap cell content.
- Support multiple pages.
- Repeat table headers when tables span pages.
- Prevent content from overlapping or extending beyond page margins.
- Use consistent titles, spacing, and page numbering.

Use appropriate file names such as:
- `employee_attrition_complete_report.pdf`
- `employee_attrition_analysis_report.pdf`
- `employee_attrition_prediction_report.pdf`
- `employee_attrition_model_evaluation.pdf`
- `employee_attrition_batch_predictions.csv`
- `employee_attrition_report_package.zip`

## 7. User Experience

After the user completes a supported workflow, show a clear results section followed by a prominent but appropriately styled **Download Report** action.

For example, after a batch prediction:

1. Display the prediction summary.
2. Display the results table.
3. Show the estimated probability distribution.
4. Explain the threshold and limitations.
5. Provide a PDF report download.
6. Provide a complete CSV download.
7. Provide an optional complete report-package download.

After an individual prediction:

1. Display the prediction.
2. Display the estimated probability and threshold.
3. Show a supported explanation.
4. Provide a PDF report download.

After data analysis:

1. Display the analysis and charts.
2. Display any applicable data-quality warnings.
3. Provide the dataset analysis report download.

After model evaluation:

1. Display actual evaluation results.
2. Provide a model evaluation report download.

The user must not need to log in, create an account, or save records to a database to generate reports.

Report generation must not retrain the model or change its predictions.

## 8. Data Privacy and Temporary Storage

Keep report-generation workflows consistent with the application's privacy requirements.

- Process uploads and build reports in memory wherever practical.
- Do not persist report source data unnecessarily.
- Do not send employee records to external report-generation APIs.
- Do not transmit employee data to Hugging Face or other model-hosting services.
- Do not include sensitive attributes or personal identifiers in exported reports unless explicitly necessary and authorized.
- Do not log full uploaded records.
- Do not claim that the absence of permanent file storage constitutes complete security.

Users intentionally downloading reports are choosing to export their results, so explain that downloaded files are outside the application's control.

## 9. Testing Requirements

Add automated tests for report generation.

Verify that:
- A valid analysis produces a readable PDF.
- An individual prediction report contains the actual probability and selected threshold.
- A batch report contains the real batch summary.
- The batch CSV contains every successfully predicted row in source order.
- The original target column is preserved when present.
- Prediction columns do not overwrite input columns.
- A model evaluation report uses actual saved metrics.
- Missing report sections are handled gracefully.
- Empty datasets and invalid results do not produce fabricated content.
- PDF files are structurally valid and nonempty.
- ZIP packages contain the files they declare.
- Temporary processing does not overwrite the training dataset or model artifacts.

Use synthetic test fixtures where appropriate. Do not require a live dataset or internet access for basic report-generation tests.

## 10. Acceptance Criteria

The report feature is complete only when users can actually download valid files.

- Dataset analysis can be exported as a PDF.
- Individual predictions can be exported as a PDF.
- Batch prediction summaries can be exported as a PDF.
- Complete batch results can be downloaded as CSV.
- Model evaluation results can be exported as a PDF.
- A consolidated report is available for the results currently available.
- The report package can be downloaded when ZIP packaging is implemented.
- All exported values come from real application results.
- Report layouts remain readable for multi-page content.
- No login, user account, or database is required.
- Report generation does not trigger retraining or change model outputs.
- The feature is documented in the README.
- Tests verify the actual files generated.

Implement and test this functionality as part of the application, rather than merely adding a button with no working export logic.