# Employee Attrition Prediction System (MVP)

A scoped-down, buildable version of an AI-powered attrition prediction and
retention system. Predicts which employees are at risk of leaving, explains
*why* using SHAP, and maps risk factors to a small rule-based intervention
library — reviewed by a human, never automated.

## Why rule-based, not LLM, for recommendations

An LLM layer sounds more impressive but risks generating plausible-but-wrong
HR advice (hallucination) and is harder to justify in a demo or report. A
transparent lookup table you designed yourself is easier to defend and just
as functional for an MVP. The architecture leaves room to swap in an LLM
later if you want to extend it.

## Dataset

`data/WA_Fn-UseC_-HR-Employee-Attrition.csv` — the real IBM HR Analytics
Employee Attrition & Performance dataset (1,470 employees, 35 attributes,
~16% attrition rate). Already included, no download needed.

## Project structure

```
attrition-prediction-system/
├── data/
│   └── WA_Fn-UseC_-HR-Employee-Attrition.csv   # dataset (included)
├── src/
│   ├── data_prep.py     # loading, feature engineering, cleaning
│   ├── train.py          # Logistic Regression + XGBoost training
│   ├── evaluate.py       # ROC-AUC, PR-AUC, precision@K (not accuracy)
│   ├── explain.py        # SHAP per-employee explanations
│   └── recommend.py      # rule-based intervention mapping
├── dashboard/
│   └── app.py             # Streamlit HR dashboard
├── models/                 # trained model saved here (after you run training)
├── outputs/                 # SHAP explanations saved here
├── requirements.txt
└── INSTRUCTIONS.md          # what to run, in what order, and why
```

## How it fits together

```
data_prep.py  →  train.py  →  explain.py  →  recommend.py  →  dashboard/app.py
(clean data)     (model)      (SHAP)          (rules)          (view it all)
```

## Metrics used (and why)

Accuracy is not reported anywhere in this project. With ~84/16 class
imbalance, a model that always predicts "stays" gets 84% accuracy while
being useless. Instead:

- **ROC-AUC** — overall ranking quality
- **PR-AUC** — more informative than ROC-AUC under imbalance
- **Precision@top-K** — of the K highest-risk employees HR could actually
  act on, how many really left? This mirrors a real intervention budget.

## Known limitations (be upfront about these)

- Dataset is small (1,470 rows) and IBM's own synthetic/anonymized data,
  not a real company's HR system — treat feature relationships as
  illustrative, not causal.
- SHAP shows *correlation* the model learned, not proven causation.
- Recommendations are a demo-scale rule table (~10 mappings), not a real
  HR policy engine.
- No fairness/bias auditing implemented — flagged as required before any
  real deployment, out of scope for this MVP.
