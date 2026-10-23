"""Train the attrition model.   Usage:  python train.py

Honest protocol:
  1. Candidate models are compared with 5-fold CV on REAL training rows only
     (synthetic rows are excluded here, because they were generated from these same rows).
  2. The best candidate (by average precision) is picked; the decision threshold is the
     F1-optimal point on the out-of-fold predictions.
  3. The chosen model is refit on real + synthetic rows (real rows weighted x5).
  4. Everything is reported on the untouched real hold-out file. The hold-out is never used
     for selection or threshold choice.
"""
import json
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, confusion_matrix, f1_score,
                             precision_recall_curve, precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from core import MODEL_PATH, ROOT, TARGET, build_schema, feature_frame

SEED, REAL_WEIGHT = 42, 5.0
DATA = ROOT / "data"


def make_pipeline(estimator, X: pd.DataFrame) -> Pipeline:
    cat = [c for c in X.columns if X[c].dtype == object or str(X[c].dtype).startswith("str")]
    num = [c for c in X.columns if c not in cat]
    pre = ColumnTransformer([("num", StandardScaler(), num),
                             ("cat", OneHotEncoder(handle_unknown="ignore"), cat)])
    return Pipeline([("pre", pre), ("model", estimator)])


def candidates():
    return {
        "LogisticRegression": LogisticRegression(C=0.3, max_iter=3000),
        "RandomForest": RandomForestClassifier(n_estimators=300, min_samples_leaf=5, random_state=SEED, n_jobs=-1),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=150, max_depth=2, learning_rate=0.05,
                                                       subsample=0.8, random_state=SEED),
    }


def metrics_at(y, proba, thr):
    pred = (proba >= thr).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {"accuracy": accuracy_score(y, pred), "precision": precision_score(y, pred, zero_division=0),
            "recall": recall_score(y, pred), "f1": f1_score(y, pred), "roc_auc": roc_auc_score(y, proba),
            "average_precision": average_precision_score(y, proba),
            "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}}


def main():
    real = pd.read_csv(DATA / "real_train_80pct.csv")
    syn = pd.read_csv(DATA / "synthetic_hr_attrition_12000.csv")
    hold = pd.read_csv(DATA / "real_holdout_20pct_DO_NOT_TRAIN.csv")
    Xr, yr = feature_frame(real), (real[TARGET] == "Yes").astype(int)
    Xs, ys = feature_frame(syn), (syn[TARGET] == "Yes").astype(int)
    Xh, yh = feature_frame(hold), (hold[TARGET] == "Yes").astype(int)
    print(f"real train {len(Xr)} | synthetic {len(Xs)} | hold-out {len(Xh)} | features {Xr.shape[1]}")

    # 1) compare candidates, real rows only
    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
    comp, oof = {}, {}
    for name, est in candidates().items():
        t = time.time()
        p = cross_val_predict(make_pipeline(est, Xr), Xr, yr, cv=cv, method="predict_proba")[:, 1]
        oof[name] = p
        comp[name] = {"cv_roc_auc": roc_auc_score(yr, p), "cv_average_precision": average_precision_score(yr, p),
                      "seconds": round(time.time() - t, 1)}
        print(f"  {name:20s} CV AUC {comp[name]['cv_roc_auc']:.3f}  AP {comp[name]['cv_average_precision']:.3f}")
    best = max(comp, key=lambda k: comp[k]["cv_average_precision"])

    # 2) threshold = F1-optimal on out-of-fold predictions (no hold-out involved)
    pr, rc, th = precision_recall_curve(yr, oof[best])
    f1s = 2 * pr[:-1] * rc[:-1] / np.clip(pr[:-1] + rc[:-1], 1e-9, None)
    threshold = float(th[np.argmax(f1s)])
    print(f"selected: {best} | threshold {threshold:.3f}")

    # baseline (real only) and final (real + synthetic), both scored on the hold-out
    base = make_pipeline(candidates()[best], Xr).fit(Xr, yr)
    base_m = metrics_at(yh, base.predict_proba(Xh)[:, 1], threshold)
    Xa, ya = pd.concat([Xr, Xs], ignore_index=True), np.r_[yr, ys]
    w = np.r_[np.full(len(Xr), REAL_WEIGHT), np.ones(len(Xs))]
    final = make_pipeline(candidates()[best], Xa).fit(Xa, ya, model__sample_weight=w)
    final_m = metrics_at(yh, final.predict_proba(Xh)[:, 1], threshold)

    # 3) permutation importance on the hold-out
    pi = permutation_importance(final, Xh, yh, scoring="average_precision", n_repeats=20, random_state=SEED)
    importance = sorted(({"feature": c, "importance": float(m), "std": float(s)}
                         for c, m, s in zip(Xh.columns, pi.importances_mean, pi.importances_std)),
                        key=lambda d: -d["importance"])

    bundle = {"pipeline": final, "threshold": threshold, "schema": build_schema(Xr), "model_name": best,
              "metrics": {"candidates_cv": comp, "holdout_real_only": base_m, "holdout_final": final_m,
                          "importance": importance},
              "info": {"seed": SEED, "real_weight": REAL_WEIGHT, "n_real_train": len(Xr), "n_synthetic": len(Xs),
                       "n_holdout": len(Xh), "excluded_columns": [c for c in real.columns if c not in Xr.columns]}}
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(bundle, MODEL_PATH)
    (MODEL_PATH.parent / "metrics.json").write_text(json.dumps(
        {"model": best, "threshold": threshold, **bundle["metrics"], **bundle["info"]}, indent=2))
    print("\nHOLD-OUT (real, never used for selection):")
    for k, m in (("real only    ", base_m), ("real+synthetic", final_m)):
        print(f"  {k} AUC {m['roc_auc']:.3f} AP {m['average_precision']:.3f} "
              f"P {m['precision']:.2f} R {m['recall']:.2f} F1 {m['f1']:.2f}")
    print(f"saved -> {MODEL_PATH}")


if __name__ == "__main__":
    main()
