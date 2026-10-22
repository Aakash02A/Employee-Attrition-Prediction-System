"""Train, compare, select, evaluate once on held-out data, and save trusted artifacts."""
from __future__ import annotations

import argparse
import json
import logging
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from .config import DEFAULT_DATA_PATH, MODEL_PATH, RANDOM_SEED, REPORT_DIR
from .data_loader import DataValidationError, load_csv, quality_report
from .evaluate import binary_metrics, choose_threshold
from .preprocessing import feature_candidates, feature_profile, make_preprocessor, split_features

logger = logging.getLogger(__name__)


def stratified_partitions(X: pd.DataFrame, y: pd.Series, seed: int = RANDOM_SEED):
    """Create 70/15/15 partitions; require enough members in both classes."""
    counts = y.value_counts()
    if len(counts) != 2 or int(counts.min()) < 7 or int(np.ceil(0.30 * len(X))) < 4:
        raise DataValidationError(
            "A stratified 70/15/15 split requires at least 7 rows in each target class and at least 4 rows in the held-out portion. "
            "Supply more labeled data; this implementation does not silently weaken stratification."
        )
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=seed, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=seed, stratify=y_temp
    )
    return X_train, X_val, X_test, y_train, y_val, y_test


def candidate_estimators(seed: int = RANDOM_SEED) -> dict[str, object]:
    return {
        "Logistic Regression": LogisticRegression(class_weight="balanced", max_iter=2000, random_state=seed),
        "Random Forest": RandomForestClassifier(
            n_estimators=250, min_samples_leaf=2, class_weight="balanced_subsample",
            random_state=seed, n_jobs=-1,
        ),
        "Extra Trees": ExtraTreesClassifier(
            n_estimators=250, min_samples_leaf=2, class_weight="balanced",
            random_state=seed, n_jobs=-1,
        ),
    }


def train_model(data_path: str | Path = DEFAULT_DATA_PATH, *, model_path: str | Path = MODEL_PATH,
                report_dir: str | Path = REPORT_DIR, seed: int = RANDOM_SEED) -> dict:
    frame = load_csv(data_path, require_target=True)
    data_report = quality_report(frame)
    X, y, _, _ = split_features(frame, feature_columns=feature_candidates(frame))
    X_train, X_val, X_test, y_train, y_val, y_test = stratified_partitions(X, y, seed)
    training_constant_columns = [column for column in X_train if X_train[column].nunique(dropna=True) <= 1]
    if training_constant_columns:
        X_train = X_train.drop(columns=training_constant_columns)
        X_val = X_val.drop(columns=training_constant_columns)
        X_test = X_test.drop(columns=training_constant_columns)
    if X_train.shape[1] == 0:
        raise DataValidationError("No non-constant predictive features remain in the training partition.")
    numeric = X_train.select_dtypes(include=["number"]).columns.tolist()
    categorical = [column for column in X_train.columns if column not in numeric]
    feature_columns = list(X_train.columns)

    comparison: list[dict] = []
    fitted: dict[str, tuple[Pipeline, float, float]] = {}
    for name, estimator in candidate_estimators(seed).items():
        pipeline = Pipeline([
            ("preprocessor", make_preprocessor(numeric, categorical)),
            ("classifier", estimator),
        ])
        started = time.perf_counter()
        pipeline.fit(X_train, y_train)
        duration = time.perf_counter() - started
        probabilities = pipeline.predict_proba(X_val)[:, 1]
        threshold, _ = choose_threshold(y_val, probabilities)
        metrics = binary_metrics(y_val, probabilities, threshold)
        comparison.append({
            "model": name, **metrics, "training_seconds": round(duration, 3),
            "selection_rule": "validation average precision; tie-break by validation F1",
        })
        fitted[name] = (pipeline, threshold, duration)
        logger.info("Fitted candidate %s in %.2fs", name, duration)

    # Select from validation results only. Test scores are not part of this ordering.
    best_row = max(comparison, key=lambda row: (row["average_precision"], row["f1"]))
    selected_name = best_row["model"]
    selected_pipeline, threshold, _ = fitted[selected_name]
    test_probabilities = selected_pipeline.predict_proba(X_test)[:, 1]
    test_metrics = binary_metrics(y_test, test_probabilities, threshold)
    predictions = (test_probabilities >= threshold).astype(int)

    # Permutation importance is descriptive only; it is not used for model/threshold selection.
    importance_result = permutation_importance(
        selected_pipeline, X_test, y_test, scoring="average_precision", n_repeats=5,
        random_state=seed, n_jobs=-1,
    )
    importances = pd.DataFrame({
        "feature": feature_columns,
        "importance_mean": importance_result.importances_mean,
        "importance_std": importance_result.importances_std,
    }).sort_values("importance_mean", ascending=False)

    timestamp = datetime.now(timezone.utc).isoformat()
    metadata = {
        "model_id": selected_name.lower().replace(" ", "_"), "model_name": selected_name,
        "trained_at_utc": timestamp, "random_seed": seed,
        "dataset": {"rows": int(len(frame)), "columns": int(frame.shape[1]), "source_path_name": Path(data_path).name,
                    "target_counts": data_report.target_counts},
        "features": feature_columns, "numeric_features": numeric, "categorical_features": categorical,
        "excluded_features": [c for c in frame.columns if c not in feature_columns and c != "Attrition"],
        "training_constant_columns": training_constant_columns,
        "feature_profile": feature_profile(X_train, feature_columns),
        "preprocessing": {"numeric": "median imputation + standard scaling", "categorical": "most-frequent imputation + one-hot (unknown ignored)"},
        "threshold": float(threshold), "threshold_objective": "maximize validation F1; tie-break by recall, then closest to 0.50",
        "validation_metrics": {k: v for k, v in best_row.items() if k not in {"model", "training_seconds", "selection_rule"}},
        "test_metrics": test_metrics,
        "split": {"train_rows": int(len(X_train)), "validation_rows": int(len(X_val)), "test_rows": int(len(X_test)), "proportions": "70/15/15 stratified"},
        "candidate_configurations": {
            "Logistic Regression": "class_weight=balanced, max_iter=2000",
            "Random Forest": "250 trees, min_samples_leaf=2, class_weight=balanced_subsample",
            "Extra Trees": "250 trees, min_samples_leaf=2, class_weight=balanced",
        },
        "versions": {"python": platform.python_version(), "scikit_learn": sklearn.__version__, "pandas": pd.__version__, "numpy": np.__version__, "joblib": joblib.__version__},
        "limitations": ["Fictional public dataset; not representative evidence for an actual employer.",
                        "Historical associations are not causal or individual forecasts.",
                        "Default policy excludes age, gender, marital status, identifiers, and constants."],
    }
    bundle = {
        "pipeline": selected_pipeline, "metadata": metadata,
        "comparison": comparison, "test_y": np.asarray(y_test, dtype=int).tolist(),
        "test_probabilities": np.asarray(test_probabilities, dtype=float).tolist(),
        "test_predictions": predictions.tolist(),
        "feature_importance": importances.to_dict(orient="records"),
    }
    model_path = Path(model_path)
    report_dir = Path(report_dir)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, model_path)
    (report_dir / "training_metadata.json").write_text(json.dumps(metadata, indent=2, allow_nan=False), encoding="utf-8")
    (report_dir / "model_comparison.json").write_text(json.dumps(comparison, indent=2, allow_nan=False), encoding="utf-8")
    (report_dir / "model_comparison.csv").write_text(pd.DataFrame(comparison).to_csv(index=False), encoding="utf-8")
    (report_dir / "test_evaluation.json").write_text(json.dumps(test_metrics, indent=2, allow_nan=False), encoding="utf-8")
    importances.to_csv(report_dir / "feature_importance.csv", index=False)
    logger.info("Selected %s; held-out test average precision %.4f", selected_name, test_metrics["average_precision"])
    return {"model_path": str(model_path), "report_dir": str(report_dir), "metadata": metadata, "comparison": comparison}


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and evaluate attrition models.")
    parser.add_argument("--data", default=str(DEFAULT_DATA_PATH), help="Path to labeled CSV")
    parser.add_argument("--model-path", default=str(MODEL_PATH), help="Output trusted local Joblib bundle")
    parser.add_argument("--report-dir", default=str(REPORT_DIR), help="Output report directory")
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        result = train_model(args.data, model_path=args.model_path, report_dir=args.report_dir, seed=args.seed)
    except (DataValidationError, OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f"Selected model: {result['metadata']['model_name']}")
    print(f"Bundle: {result['model_path']}\nReports: {result['report_dir']}")
    print(json.dumps(result["metadata"]["test_metrics"], indent=2))


if __name__ == "__main__":
    main()
