"""
recommend.py
Maps top SHAP risk factors to a small, human-reviewable intervention
library. Deliberately rule-based, not LLM-generated -- see README for why.
"""

# Map raw/engineered feature name fragments -> (issue label, recommended action)
INTERVENTION_LIBRARY = {
    "PromotionStagnation": (
        "Low career progression",
        "Schedule a career-path discussion and review promotion timeline.",
    ),
    "YearsSinceLastPromotion": (
        "Low career progression",
        "Schedule a career-path discussion and review promotion timeline.",
    ),
    "OverTime_Yes": (
        "High workload",
        "Review workload distribution; check for sustained overtime.",
    ),
    "JobSatisfaction": (
        "Low engagement",
        "Hold an engagement/satisfaction check-in; consider role or project change.",
    ),
    "EnvironmentSatisfaction": (
        "Low engagement",
        "Hold an engagement/satisfaction check-in; consider role or project change.",
    ),
    "ManagerTenureRatio": (
        "Manager relationship",
        "Encourage structured 1:1s; consider manager coaching.",
    ),
    "IncomePerJobLevel": (
        "Compensation concern",
        "Run a compensation benchmarking review for this role/level.",
    ),
    "MonthlyIncome": (
        "Compensation concern",
        "Run a compensation benchmarking review for this role/level.",
    ),
    "DistanceFromHome": (
        "Work-life balance",
        "Discuss flexible scheduling or remote/hybrid options.",
    ),
    "TrainingTimesLastYear": (
        "Skill stagnation",
        "Identify a relevant certification or challenging project.",
    ),
    "WorkLifeBalance": (
        "Work-life balance",
        "Discuss flexible scheduling or workload adjustment.",
    ),
}

DEFAULT_ACTION = (
    "Unclassified risk driver",
    "Flag for manual HR review -- no rule mapped to this factor yet.",
)


def _lookup(feature_name: str):
    for key, value in INTERVENTION_LIBRARY.items():
        if key in feature_name:
            return value
    return DEFAULT_ACTION


def recommend_for_employee(top_factors, top_n=3):
    """top_factors: list of (feature_name, shap_value) tuples, most
    important first. Returns a de-duplicated list of (issue, action)."""
    seen_issues = set()
    recommendations = []
    for feature_name, shap_value in top_factors:
        if shap_value <= 0:
            continue  # only explain factors pushing risk UP
        issue, action = _lookup(feature_name)
        if issue not in seen_issues:
            seen_issues.add(issue)
            recommendations.append({"issue": issue, "action": action})
        if len(recommendations) >= top_n:
            break
    return recommendations


if __name__ == "__main__":
    # quick manual smoke test
    example = [("OverTime_Yes", 0.19), ("PromotionStagnation", 0.15), ("Age", -0.02)]
    print(recommend_for_employee(example))
