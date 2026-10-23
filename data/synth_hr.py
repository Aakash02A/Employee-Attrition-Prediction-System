"""
Synthetic generator for the IBM HR Employee Attrition dataset.

Method: sequential CART synthesis (the approach used by the R package `synthpop`)
  - every column is modelled conditionally on the columns generated before it
  - each model is a regularised decision tree (min_samples_leaf is large on purpose,
    so no leaf is ever a single real employee -> no row copying)
  - values are drawn from the *leaf distribution* (smoothed bootstrap), not copied rows
  - business rules (years-of-service logic, role<->department, salary bands ...) are
    enforced by rejection sampling, so every synthetic row is logically valid

Usage:
    python synth_hr.py --input WA_Fn-UseC_-HR-Employee-Attrition.csv --n 12000 \
                       --seed 42 --out synthetic_hr_attrition.csv
"""
import argparse
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

CONSTANTS = {"EmployeeCount": 1, "Over18": "Y", "StandardHours": 80}
NOISE_COLS = ["DailyRate", "HourlyRate", "MonthlyRate"]  # ~independent of everything in the real data

# generation order (parents -> children). Attrition is generated last, conditioned on everything.
ORDER = [
    "Age", "Gender", "MaritalStatus", "Education", "EducationField", "DistanceFromHome",
    "TotalWorkingYears", "NumCompaniesWorked", "JobLevel", "JobRole", "Department",
    "MonthlyIncome", "YearsAtCompany", "YearsInCurrentRole", "YearsWithCurrManager",
    "YearsSinceLastPromotion", "BusinessTravel", "OverTime", "StockOptionLevel",
    "PercentSalaryHike", "TrainingTimesLastYear", "JobInvolvement", "JobSatisfaction",
    "EnvironmentSatisfaction", "WorkLifeBalance", "RelationshipSatisfaction", "Attrition",
]
NOMINAL = ["MaritalStatus", "EducationField", "JobRole", "Department"]
BINARY = {"Gender": "Male", "OverTime": "Yes", "Attrition": "Yes"}
TRAVEL = {"Non-Travel": 0, "Travel_Rarely": 1, "Travel_Frequently": 2}
CATEGORICAL_TARGETS = set(NOMINAL) | set(BINARY) | {"BusinessTravel"}
DEFAULT_LEAF = 10
BANDWIDTH = 0.30              # smoothing noise as fraction of leaf std (numeric columns)


def _features(d: pd.DataFrame, cols, cats):
    """Numeric design matrix for the tree models (one-hot for nominal columns)."""
    parts = {}
    for c in cols:
        if c in NOMINAL:
            for k in cats[c]:
                parts[f"{c}={k}"] = (d[c] == k).astype(float).values
        elif c in BINARY:
            parts[c] = (d[c] == BINARY[c]).astype(float).values
        elif c == "BusinessTravel":
            parts[c] = d[c].map(TRAVEL).astype(float).values
        else:
            parts[c] = d[c].astype(float).values
    return pd.DataFrame(parts, index=d.index)


class HRSynthesizer:
    def __init__(self, leaf=DEFAULT_LEAF, seed=0):
        self.leaf, self.seed = leaf, seed

    # ------------------------------------------------------------------ fit
    def fit(self, real: pd.DataFrame):
        self.real = real.reset_index(drop=True)
        r = self.real
        self.cats = {c: sorted(r[c].unique()) for c in NOMINAL}
        self.int_cols = [c for c in r.columns if pd.api.types.is_integer_dtype(r[c])]
        self.bounds = {c: (r[c].min(), r[c].max()) for c in r.columns if c in self.int_cols}
        self.level_income = r.groupby("JobLevel").MonthlyIncome.agg(["min", "max"])
        self.valid_role_dept = set(zip(r.JobRole, r.Department))
        self.valid_role_level = set(zip(r.JobRole, r.JobLevel))
        self.models = {}
        for i, col in enumerate(ORDER):
            if i == 0:
                continue
            X = _features(r, ORDER[:i], self.cats)
            msl = self.leaf
            if col == "Attrition":
                # outcome: regularised LogReg + shallow GBM blend -> probability -> Bernoulli draw
                y = (r[col] == "Yes").astype(int).values
                lr = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=3000)).fit(X, y)
                gb = GradientBoostingClassifier(n_estimators=100, max_depth=2, learning_rate=0.05,
                                                subsample=0.7, min_samples_leaf=20, random_state=self.seed).fit(X, y)
                self.models[col] = ((lr, gb), None)
                continue
            if col in CATEGORICAL_TARGETS:
                y = r[col].values
                tree = DecisionTreeClassifier(min_samples_leaf=msl, random_state=self.seed)
                tree.fit(X, y)
            else:
                y = r[col].astype(float).values
                tree = DecisionTreeRegressor(min_samples_leaf=msl, random_state=self.seed)
                tree.fit(X, y)
            leaves = tree.apply(X)
            leaf_vals = {l: y[leaves == l] for l in np.unique(leaves)}
            self.models[col] = (tree, leaf_vals)
        return self

    # ------------------------------------------------------------- sampling
    def _sample_leaf(self, col, leaf_ids, rng):
        _, leaf_vals = self.models[col]
        out = []
        for l in leaf_ids:
            v = leaf_vals[l]
            x = v[rng.integers(len(v))]
            if col not in CATEGORICAL_TARGETS:
                x = x + (rng.normal(0, BANDWIDTH * v.std()) if v.std() > 0 else 0)
            out.append(x)
        return np.array(out, dtype=object if col in CATEGORICAL_TARGETS else float)

    def _independent(self, col, n, rng):
        """near-independent columns: smoothed marginal (empirical value + uniform jitter)"""
        v = np.sort(self.real[col].values)
        base = v[rng.integers(len(v), size=n)]
        step = max(1.0, (v.max() - v.min()) / len(v) * 3)
        return base + rng.uniform(-step / 2, step / 2, size=n)

    def _draw(self, n, rng):
        d = pd.DataFrame(index=range(n))
        # root column: smoothed marginal of Age
        a = self.real["Age"].values
        d["Age"] = (a[rng.integers(len(a), size=n)] + rng.normal(0, 0.3 * a.std() / 3, size=n)).round().clip(18, 60)
        for i, col in enumerate(ORDER):
            if i == 0:
                d[col] = self._clip_int(col, d[col])
                continue
            tree, _ = self.models[col]
            X = _features(d, ORDER[:i], self.cats)
            if col == "Attrition":
                lr, gb = tree
                p = 0.5 * lr.predict_proba(X)[:, 1] + 0.5 * gb.predict_proba(X)[:, 1]
                d[col] = np.where(rng.random(len(d)) < p, "Yes", "No")
                continue
            leaves = tree.apply(X)
            vals = self._sample_leaf(col, leaves, rng)
            d[col] = vals
            if col in self.int_cols:   # integer columns become integers immediately
                lo_, hi_ = self.bounds[col]
                d[col] = pd.to_numeric(d[col]).astype(float).round().clip(lo_, hi_)
            # logical caps applied immediately so children see consistent parents
            # (clipping keeps the distribution's mass; rejection would bias it low)
            if col == "TotalWorkingYears":
                d[col] = np.minimum(d[col].round(), d["Age"].round() - 18).clip(lower=0)
            elif col == "YearsAtCompany":
                d[col] = np.minimum(d[col].round(), d["TotalWorkingYears"]).clip(lower=0)
            elif col in ("YearsInCurrentRole", "YearsWithCurrManager", "YearsSinceLastPromotion"):
                d[col] = np.minimum(d[col].round(), d["YearsAtCompany"]).clip(lower=0)
        for c in NOISE_COLS:
            d[c] = self._clip_int(c, pd.Series(self._independent(c, n, rng)))
        # derived columns
        d["PercentSalaryHike"] = d["PercentSalaryHike"].astype(float).round().clip(11, 25)
        d["PerformanceRating"] = np.where(d["PercentSalaryHike"] >= 20, 4, 3)
        # salary band by job level (real min/max)
        lo = d["JobLevel"].map(self.level_income["min"])
        hi = d["JobLevel"].map(self.level_income["max"])
        d["MonthlyIncome"] = d["MonthlyIncome"].clip(lo, hi).round().astype(int)
        return d

    @staticmethod
    def _clip_int(col, s):
        return s  # integer rounding/clipping happens in _finalise_ints

    def _finalise_ints(self, d):
        for c in self.int_cols:
            if c in d.columns and c not in ("EmployeeNumber", *CONSTANTS):
                lo, hi = self.bounds[c]
                d[c] = d[c].astype(float).round().clip(lo, hi).astype(int)
        return d

    def _valid(self, d):
        ok = (
            (d.TotalWorkingYears >= d.YearsAtCompany)
            & (d.YearsAtCompany >= d.YearsInCurrentRole)
            & (d.YearsAtCompany >= d.YearsSinceLastPromotion)
            & (d.YearsAtCompany >= d.YearsWithCurrManager)
            & (d.Age - 18 >= d.TotalWorkingYears)
            & (d.NumCompaniesWorked >= 1)
        )
        ok = np.array(ok, dtype=bool)
        ok &= np.array([(r, dp) in self.valid_role_dept for r, dp in zip(d.JobRole, d.Department)])
        ok &= np.array([(r, l) in self.valid_role_level for r, l in zip(d.JobRole, d.JobLevel)])
        return ok

    def sample(self, n, seed=0):
        rng = np.random.default_rng(seed)
        chunks, have = [], 0
        while have < n:
            d = self._finalise_ints(self._draw(int(n * 1.5), rng))
            d = d[self._valid(d)]
            chunks.append(d)
            have += len(d)
        out = pd.concat(chunks, ignore_index=True).iloc[:n].copy()
        out["EmployeeNumber"] = np.arange(1, n + 1)
        for k, v in CONSTANTS.items():
            out[k] = v
        return out[self.real_columns].astype(self.real_dtypes)

    # keep original column order / dtypes
    def fit_schema(self, original: pd.DataFrame):
        self.real_columns = list(original.columns)
        self.real_dtypes = original.dtypes.to_dict()
        return self


def build(real: pd.DataFrame, seed=0):
    g = HRSynthesizer(seed=seed)
    g.fit_schema(real)
    g.fit(real)
    return g


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--n", type=int, default=12000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="synthetic_hr_attrition.csv")
    a = ap.parse_args()
    real = pd.read_csv(a.input)
    gen = build(real, seed=a.seed)
    syn = gen.sample(a.n, seed=a.seed)
    syn.to_csv(a.out, index=False)
    print(f"wrote {len(syn)} rows -> {a.out}")
