"""
train.py
Trains a Logistic Regression baseline and an XGBoost model on the
attrition dataset, handling class imbalance, and saves the best model.

NOTE: This is a long-running step (a few minutes on CPU depending on
grid size). See INSTRUCTIONS.md before running.
"""

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from data_prep import get_processed_data, split_features_target
from evaluate import evaluate_model


def train_baseline(X_train, y_train):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    model = LogisticRegression(max_iter=1000, class_weight="balanced")
    model.fit(X_scaled, y_train)
    return model, scaler


def train_xgboost(X_train, y_train):
    # scale_pos_weight handles the ~84/16 class imbalance
    neg, pos = (y_train == 0).sum(), (y_train == 1).sum()
    scale_pos_weight = neg / pos

    model = XGBClassifier(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        eval_metric="aucpr",
        random_state=42,
    )
    model.fit(X_train, y_train)
    return model


def main():
    print("Loading data...")
    df = get_processed_data()
    X, y = split_features_target(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    print("\n--- Logistic Regression baseline ---")
    lr_model, scaler = train_baseline(X_train, y_train)
    X_test_scaled = scaler.transform(X_test)
    evaluate_model(lr_model, X_test_scaled, y_test, name="LogisticRegression")

    print("\n--- XGBoost ---")
    xgb_model = train_xgboost(X_train, y_train)
    evaluate_model(xgb_model, X_test, y_test, name="XGBoost")

    print("\nSaving XGBoost model (used by dashboard) to models/xgb_model.joblib")
    joblib.dump(xgb_model, "models/xgb_model.joblib")
    joblib.dump(list(X.columns), "models/feature_columns.joblib")
    print("Done.")


if __name__ == "__main__":
    main()
