from functools import lru_cache
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from ..core.config import get_settings

GRADE_RISK = {"A": 8, "B": 18, "C": 32, "D": 48, "E": 64, "F": 80, "G": 92}
PURPOSE_RISK = {
    "EDUCATION": 18,
    "HOMEIMPROVEMENT": 24,
    "PERSONAL": 35,
    "VENTURE": 44,
    "MEDICAL": 48,
    "DEBTCONSOLIDATION": 56,
}
HOME_RISK = {"OWN": 12, "MORTGAGE": 22, "RENT": 42, "OTHER": 50}


@lru_cache
def load_bundle():
    path = Path(get_settings().model_path)
    if not path.is_absolute():
        path = (Path(__file__).parents[3] / path).resolve()
    if not path.exists():
        raise RuntimeError(f"Model not found at {path}; run python ml/train.py")
    return joblib.load(path)


def band(value: float, rules: list[tuple[float, str]], default: str) -> str:
    for cutoff, label in rules:
        if value >= cutoff:
            return label
    return default


def add_driver(drivers: list[dict], factor: str, impact: str, value, severity: str, direction: str = "negative"):
    drivers.append({
        "factor": factor,
        "impact": impact,
        "value": value,
        "severity": severity,
        "direction": direction,
    })


def risk_analysis(data, probability: float, loan_pct: float) -> dict:
    grade_score = GRADE_RISK[data.loan_grade]
    purpose_score = PURPOSE_RISK[data.loan_intent]
    home_score = HOME_RISK[data.home_ownership]
    affordability = min(100, round(loan_pct * 130 + max(data.interest_rate - 8, 0) * 2.2))
    credit = min(100, round(grade_score + (28 if data.previous_default == "Y" else 0) + max(5 - data.credit_history_length, 0) * 4))
    stability = min(100, round(home_score + max(3 - data.employment_length, 0) * 8 + (8 if data.age < 23 else 0)))
    pricing = min(100, round(data.interest_rate * 4.2 + grade_score * .35))
    purpose = min(100, round(purpose_score + (12 if data.loan_intent in {"MEDICAL", "DEBTCONSOLIDATION"} else 0)))
    model = round(probability * 100)

    components = [
        {"name": "Model default signal", "score": model, "status": band(model, [(70, "critical"), (45, "high"), (25, "watch")], "healthy")},
        {"name": "Affordability", "score": affordability, "status": band(affordability, [(72, "critical"), (52, "high"), (34, "watch")], "healthy")},
        {"name": "Credit profile", "score": credit, "status": band(credit, [(76, "critical"), (58, "high"), (38, "watch")], "healthy")},
        {"name": "Income stability", "score": stability, "status": band(stability, [(70, "critical"), (54, "high"), (36, "watch")], "healthy")},
        {"name": "Pricing pressure", "score": pricing, "status": band(pricing, [(74, "critical"), (56, "high"), (38, "watch")], "healthy")},
        {"name": "Loan purpose", "score": purpose, "status": band(purpose, [(70, "critical"), (55, "high"), (40, "watch")], "healthy")},
    ]

    drivers: list[dict] = []
    if loan_pct >= .5:
        add_driver(drivers, "loan_to_income", "loan request is more than half of annual income", round(loan_pct, 3), "critical")
    elif loan_pct >= .35:
        add_driver(drivers, "loan_to_income", "large repayment burden compared with income", round(loan_pct, 3), "high")
    elif loan_pct >= .25:
        add_driver(drivers, "loan_to_income", "moderate repayment burden", round(loan_pct, 3), "watch")
    elif loan_pct <= .15:
        add_driver(drivers, "loan_to_income", "small repayment burden compared with income", round(loan_pct, 3), "positive", "positive")

    if data.interest_rate >= 20:
        add_driver(drivers, "interest_rate", "very expensive credit usually signals elevated default risk", data.interest_rate, "critical")
    elif data.interest_rate >= 15:
        add_driver(drivers, "interest_rate", "expensive credit increases repayment pressure", data.interest_rate, "high")
    elif data.interest_rate >= 12:
        add_driver(drivers, "interest_rate", "pricing is above prime lending levels", data.interest_rate, "watch")
    elif data.interest_rate <= 8:
        add_driver(drivers, "interest_rate", "low pricing supports a stronger profile", data.interest_rate, "positive", "positive")

    if data.previous_default == "Y":
        add_driver(drivers, "previous_default", "prior default on file is a major policy concern", "Y", "critical")
    elif data.credit_history_length >= 8:
        add_driver(drivers, "credit_history", "longer credit history improves assessment confidence", data.credit_history_length, "positive", "positive")

    if data.loan_grade in {"F", "G"}:
        add_driver(drivers, "loan_grade", "weak loan grade materially increases expected default risk", data.loan_grade, "critical")
    elif data.loan_grade in {"D", "E"}:
        add_driver(drivers, "loan_grade", "below-prime loan grade needs closer review", data.loan_grade, "high")
    elif data.loan_grade in {"A", "B"}:
        add_driver(drivers, "loan_grade", "strong loan grade reduces expected risk", data.loan_grade, "positive", "positive")

    if data.employment_length < 1:
        add_driver(drivers, "employment_length", "limited employment history reduces repayment stability", data.employment_length, "high")
    elif data.employment_length < 3:
        add_driver(drivers, "employment_length", "short employment history should be monitored", data.employment_length, "watch")
    elif data.employment_length >= 5:
        add_driver(drivers, "employment_length", "stable employment history supports repayment capacity", data.employment_length, "positive", "positive")

    if data.credit_history_length < 2:
        add_driver(drivers, "credit_history", "thin credit file limits repayment evidence", data.credit_history_length, "high")
    elif data.credit_history_length < 5:
        add_driver(drivers, "credit_history", "short credit history adds uncertainty", data.credit_history_length, "watch")

    if data.home_ownership in {"RENT", "OTHER"}:
        add_driver(drivers, "home_ownership", "housing profile offers less collateral stability", data.home_ownership, "watch")
    else:
        add_driver(drivers, "home_ownership", "housing profile supports applicant stability", data.home_ownership, "positive", "positive")

    if data.loan_intent in {"DEBTCONSOLIDATION", "MEDICAL", "VENTURE"}:
        add_driver(drivers, "loan_intent", "purpose commonly needs additional affordability checks", data.loan_intent, "watch")

    severity_rank = {"critical": 4, "high": 3, "watch": 2, "positive": 1}
    drivers.sort(key=lambda x: severity_rank.get(x["severity"], 0), reverse=True)
    primary = [x for x in drivers if x["direction"] == "negative"][:5]
    positives = [x for x in drivers if x["direction"] == "positive"][:3]
    return {"top_drivers": primary, "positive_signals": positives, "score_components": components}


def catboost_explanations(bundle: dict, row: pd.DataFrame) -> dict:
    """Return real per-decision SHAP values when the deployed model is CatBoost.

    CatBoost calculates exact TreeSHAP values internally, so no surrogate model or
    heuristic is used for this part of the response.
    """
    if bundle.get("model_name") != "catboost":
        return {"shap_values": [], "feature_importance": []}
    try:
        from catboost import Pool
        features = bundle["pipeline"].named_steps["features"].transform(row)
        classifier = bundle["pipeline"].named_steps["classifier"]
        categories = features.select_dtypes(include=["object", "string"]).columns.tolist()
        category_positions = [features.columns.get_loc(name) for name in categories]
        pool = Pool(features, cat_features=category_positions)
        values = classifier.get_feature_importance(pool, type="ShapValues")[0]
        names = features.columns.tolist()
        contributions = sorted(
            ({"feature": name, "value": round(float(value), 6), "direction": "increases_risk" if value >= 0 else "reduces_risk"}
             for name, value in zip(names, values[:-1])), key=lambda item: abs(item["value"]), reverse=True
        )[:8]
        importance = sorted(
            ({"feature": name, "importance": round(float(value), 4)}
             for name, value in zip(names, classifier.get_feature_importance(type="FeatureImportance"))),
            key=lambda item: item["importance"], reverse=True
        )[:12]
        return {"base_value": round(float(values[-1]), 6), "shap_values": contributions, "feature_importance": importance}
    except Exception:
        # Scoring must remain available if an optional explanation computation fails.
        return {"shap_values": [], "feature_importance": []}


def predict(data) -> dict:
    bundle = load_bundle()
    loan_pct = data.loan_amount / data.income
    row = pd.DataFrame([{
        "person_age": data.age, "person_income": data.income,
        "person_home_ownership": data.home_ownership,
        "person_emp_length": data.employment_length,
        "loan_intent": data.loan_intent, "loan_grade": data.loan_grade,
        "loan_amnt": data.loan_amount, "loan_int_rate": data.interest_rate,
        "loan_percent_income": loan_pct,
        "cb_person_default_on_file": data.previous_default,
        "cb_person_cred_hist_length": data.credit_history_length,
    }])
    probability = float(bundle["pipeline"].predict_proba(row)[0, 1])
    thresholds = bundle.get("decision_thresholds", {"low": .35, "high": .65})
    low_threshold = thresholds.get("low") or .35
    high_threshold = thresholds.get("high") or .65
    risk = "high" if probability >= high_threshold else "medium" if probability > low_threshold else "low"
    decision = "reject" if risk == "high" else "manual_review" if risk == "medium" else "approve"
    confidence = max(probability, 1 - probability)
    recommendation = {"approve": "Approve under standard policy", "manual_review": "Request enhanced affordability review", "reject": "Decline or require additional security"}[decision]
    explanation = risk_analysis(data, probability, loan_pct)
    explanation.update(catboost_explanations(bundle, row))
    return {"default_probability": round(probability, 6), "risk_score": round(probability * 1000),
            "confidence": round(confidence * 100, 2), "risk_category": risk,
            "recommendation": recommendation, "explanation": explanation, "decision": decision}
