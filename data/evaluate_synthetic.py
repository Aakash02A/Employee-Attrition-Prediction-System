"""
Honest evaluation of the synthetic data.
Protocol (repeated over several random splits):
  1. split REAL data 80/20 (stratified on Attrition)
  2. fit the generator on the 80% train part ONLY, generate N synthetic rows
  3. compare synthetic vs real (fidelity), check rules, check privacy
  4. train models on {real-train, synthetic, real-train + synthetic}
     and score ALL of them on the untouched real 20% hold-out (AUC)
"""
import sys, json, warnings
import numpy as np, pandas as pd
from scipy.stats import ks_2samp
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import NearestNeighbors
from synth_hr import build

warnings.filterwarnings("ignore")
PATH = sys.argv[1]
N_SYN = 12000
SEEDS = [1, 2, 3, 4, 5]
DROP = ["EmployeeNumber", "EmployeeCount", "Over18", "StandardHours"]
NUM = ["Age", "DailyRate", "DistanceFromHome", "HourlyRate", "MonthlyIncome", "MonthlyRate",
       "NumCompaniesWorked", "PercentSalaryHike", "TotalWorkingYears", "TrainingTimesLastYear",
       "YearsAtCompany", "YearsInCurrentRole", "YearsSinceLastPromotion", "YearsWithCurrManager"]
CAT = ["BusinessTravel", "Department", "EducationField", "Gender", "JobRole", "MaritalStatus", "OverTime",
       "Education", "EnvironmentSatisfaction", "JobInvolvement", "JobLevel", "JobSatisfaction",
       "PerformanceRating", "RelationshipSatisfaction", "StockOptionLevel", "WorkLifeBalance"]


def encode(df, cols_ref):
    X = pd.get_dummies(df.drop(columns=DROP + ["Attrition"]), columns=[c for c in CAT if c in df.columns])
    return X.reindex(columns=cols_ref, fill_value=0).astype(float)


def models():
    return {
        "LogReg": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=0.3)),
        "RandomForest": RandomForestClassifier(n_estimators=300, min_samples_leaf=3, random_state=0, n_jobs=-1),
        "GradBoost": GradientBoostingClassifier(random_state=0),
    }


def tvd(a, b):
    pa, pb = a.value_counts(normalize=True), b.value_counts(normalize=True)
    idx = pa.index.union(pb.index)
    return 0.5 * np.abs(pa.reindex(idx, fill_value=0) - pb.reindex(idx, fill_value=0)).sum()


def rules_violations(d):
    v = {
        "YearsAtCompany > TotalWorkingYears": (d.YearsAtCompany > d.TotalWorkingYears).sum(),
        "YearsInRole/Mgr/Promo > YearsAtCompany": ((d.YearsInCurrentRole > d.YearsAtCompany) |
                                                   (d.YearsWithCurrManager > d.YearsAtCompany) |
                                                   (d.YearsSinceLastPromotion > d.YearsAtCompany)).sum(),
        "TotalWorkingYears > Age-18": (d.TotalWorkingYears > d.Age - 18).sum(),
        "Rating inconsistent with hike": (((d.PercentSalaryHike >= 20) & (d.PerformanceRating != 4)) |
                                          ((d.PercentSalaryHike < 20) & (d.PerformanceRating != 3))).sum(),
    }
    return v


rows_fid, rows_priv, rows_util, rows_viol = [], [], [], []
real_all = pd.read_csv(PATH)
for seed in SEEDS:
    tr, te = train_test_split(real_all, test_size=0.2, stratify=real_all.Attrition, random_state=seed)
    gen = build(tr.reset_index(drop=True), seed=seed)
    gen.fit_schema(real_all)
    syn = gen.sample(N_SYN, seed=seed)

    # ---- fidelity
    ks = np.mean([ks_2samp(tr[c], syn[c]).statistic for c in NUM])
    tv = np.mean([tvd(tr[c], syn[c]) for c in CAT + ["Attrition"]])
    corr_r = tr[NUM + ["JobLevel", "StockOptionLevel", "WorkLifeBalance", "JobSatisfaction"]].corr(method="spearman")
    corr_s = syn[corr_r.columns].corr(method="spearman")
    cdiff = np.abs(corr_r - corr_s).values[np.triu_indices(len(corr_r), 1)].mean()
    # baseline: how different is a *real* hold-out from real train? (sampling noise floor)
    ks_floor = np.mean([ks_2samp(tr[c], te[c]).statistic for c in NUM])
    rows_fid.append(dict(seed=seed, KS_mean=ks, KS_real_vs_real_floor=ks_floor, TVD_mean=tv, corr_abs_diff=cdiff))
    rows_viol.append(rules_violations(syn))

    # ---- privacy: exact copies + distance to closest record (DCR)
    key = [c for c in tr.columns if c not in ("EmployeeNumber",)]
    exact = syn.merge(tr[key].drop_duplicates(), on=key, how="inner").shape[0]
    cols_ref = pd.get_dummies(tr.drop(columns=DROP + ["Attrition"]), columns=CAT).columns
    Xtr, Xte, Xsy = encode(tr, cols_ref), encode(te, cols_ref), encode(syn.sample(len(te), random_state=seed), cols_ref)
    sc = StandardScaler().fit(Xtr)
    nn = NearestNeighbors(n_neighbors=1).fit(sc.transform(Xtr))
    d_syn = nn.kneighbors(sc.transform(Xsy))[0].ravel()
    d_te = nn.kneighbors(sc.transform(Xte))[0].ravel()
    rows_priv.append(dict(seed=seed, exact_copies_of_train=exact,
                          DCR_median_synthetic=np.median(d_syn), DCR_median_real_holdout=np.median(d_te)))

    # ---- utility (TSTR): everything scored on the real hold-out
    Xtr_full, Xte_full, Xsy_full = encode(tr, cols_ref), encode(te, cols_ref), encode(syn, cols_ref)
    ytr, yte = (tr.Attrition == "Yes").astype(int).values, (te.Attrition == "Yes").astype(int).values
    ysy = (syn.Attrition == "Yes").astype(int).values
    for name, mk in models().items():
        res = {"seed": seed, "model": name}
        m = mk.fit(Xtr_full, ytr);               res["train_on_real"] = roc_auc_score(yte, m.predict_proba(Xte_full)[:, 1])
        res["real_train_AUC_in_sample"] = roc_auc_score(ytr, m.predict_proba(Xtr_full)[:, 1])
        m = models()[name].fit(Xsy_full, ysy);   res["train_on_synthetic"] = roc_auc_score(yte, m.predict_proba(Xte_full)[:, 1])
        res["syn_train_AUC_in_sample"] = roc_auc_score(ysy, m.predict_proba(Xsy_full)[:, 1])
        Xa, ya = pd.concat([Xtr_full, Xsy_full]), np.r_[ytr, ysy]
        w = np.r_[np.full(len(ytr), 5.0), np.ones(len(ysy))]   # real rows weighted higher
        m = models()[name]
        try:
            m.fit(Xa, ya, **({"sample_weight": w} if name != "LogReg" else {"logisticregression__sample_weight": w}))
        except TypeError:
            m.fit(Xa, ya)
        res["real_plus_synthetic"] = roc_auc_score(yte, m.predict_proba(Xte_full)[:, 1])
        rows_util.append(res)

fid, priv, util = pd.DataFrame(rows_fid), pd.DataFrame(rows_priv), pd.DataFrame(rows_util)
viol = pd.DataFrame(rows_viol)
print("\n=== FIDELITY (mean over 5 splits) ===\n", fid.drop(columns="seed").mean().round(4).to_string())
print("\n=== RULE VIOLATIONS in 12,000 synthetic rows (sum over 5 runs) ===\n", viol.sum().to_string())
print("\n=== PRIVACY ===\n", priv.drop(columns="seed").mean().round(3).to_string())
print("\n=== UTILITY: AUC on untouched real hold-out (mean ± sd over 5 splits) ===")
agg = util.groupby("model")[["train_on_real", "train_on_synthetic", "real_plus_synthetic",
                              "real_train_AUC_in_sample", "syn_train_AUC_in_sample"]].agg(["mean", "std"]).round(3)
print(agg.to_string())
out = {"fidelity": fid.to_dict("list"), "violations": viol.to_dict("list"),
       "privacy": priv.to_dict("list"), "utility": util.to_dict("records")}
json.dump(out, open("/tmp/eval_results.json", "w"), default=float)
