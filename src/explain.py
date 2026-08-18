"""
explain.py
Generates SHAP explanations so each risk score has a "why" attached.

NOTE: Computing SHAP values for the full dataset is the other
long-running step alongside training. See INSTRUCTIONS.md.
"""

import joblib
import pandas as pd
import shap

from data_prep import get_processed_data, split_features_target


def load_artifacts():
    model = joblib.load("models/xgb_model.joblib")
    feature_columns = joblib.load("models/feature_columns.joblib")
    return model, feature_columns


def compute_shap_values(model, X: pd.DataFrame):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    return shap_values, explainer


def top_factors_for_employee(shap_values_row, feature_names, top_n=5):
    """Return the top_n features driving this employee's risk score,
    ranked by absolute SHAP contribution."""
    pairs = list(zip(feature_names, shap_values_row))
    pairs.sort(key=lambda p: abs(p[1]), reverse=True)
    return pairs[:top_n]


def main():
    model, feature_columns = load_artifacts()
    df = get_processed_data()
    X, y = split_features_target(df)
    X = X[feature_columns]  # keep column order consistent with training

    shap_values, _ = compute_shap_values(model, X)

    # Save per-employee top factors for the dashboard to consume
    records = []
    for i in range(len(X)):
        factors = top_factors_for_employee(shap_values[i], feature_columns)
        records.append(
            {
                "index": i,
                "risk_score": model.predict_proba(X.iloc[[i]])[0, 1],
                "top_factors": factors,
            }
        )

    joblib.dump(records, "outputs/shap_explanations.joblib")
    print(f"Saved SHAP explanations for {len(records)} employees to outputs/shap_explanations.joblib")


if __name__ == "__main__":
    main()
