"""
data_prep.py
Loads the IBM HR Attrition dataset and engineers features for modeling.
"""

import pandas as pd

RAW_PATH = "data/WA_Fn-UseC_-HR-Employee-Attrition.csv"

# Columns that are constant or pure identifiers -> no predictive value
DROP_COLS = ["EmployeeCount", "EmployeeNumber", "Over18", "StandardHours"]


def load_raw(path: str = RAW_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add a few derived features that map to real HR risk signals."""
    df = df.copy()

    # Years since last promotion relative to tenure -> stagnation signal
    df["PromotionStagnation"] = df["YearsSinceLastPromotion"] / (df["YearsAtCompany"] + 1)

    # Overtime as binary flag is already OverTime (Yes/No) -> keep, model will encode

    # Income relative to job level -> rough "underpaid for level" signal
    df["IncomePerJobLevel"] = df["MonthlyIncome"] / df["JobLevel"]

    # Manager relationship proxy: how long with current manager vs total tenure
    df["ManagerTenureRatio"] = df["YearsWithCurrManager"] / (df["YearsAtCompany"] + 1)

    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=[c for c in DROP_COLS if c in df.columns])
    df["Attrition"] = df["Attrition"].map({"Yes": 1, "No": 0})
    return df


def get_processed_data(path: str = RAW_PATH) -> pd.DataFrame:
    df = load_raw(path)
    df = engineer_features(df)
    df = clean(df)
    return df


def split_features_target(df: pd.DataFrame):
    y = df["Attrition"]
    X = df.drop(columns=["Attrition"])
    X = pd.get_dummies(X, drop_first=True)
    return X, y


if __name__ == "__main__":
    data = get_processed_data()
    print(f"Rows: {len(data)}, Columns: {data.shape[1]}")
    print(f"Attrition rate: {data['Attrition'].mean():.2%}")
    data.to_csv("data/processed.csv", index=False)
    print("Saved data/processed.csv")
