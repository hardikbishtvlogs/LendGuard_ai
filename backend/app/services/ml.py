from functools import lru_cache
from pathlib import Path
import joblib
import pandas as pd
from ..core.config import get_settings


@lru_cache
def load_bundle():
    path = Path(get_settings().model_path)
    if not path.is_absolute():
        path = (Path(__file__).parents[3] / path).resolve()
    if not path.exists():
        raise RuntimeError(f"Model not found at {path}; run python ml/train.py")
    return joblib.load(path)


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
    drivers = []
    if loan_pct > .35: drivers.append({"factor": "loan_to_income", "impact": "increases risk", "value": round(loan_pct, 3)})
    if data.interest_rate > 14: drivers.append({"factor": "interest_rate", "impact": "increases risk", "value": data.interest_rate})
    if data.previous_default == "Y": drivers.append({"factor": "previous_default", "impact": "increases risk", "value": "Y"})
    if data.loan_grade in "AB": drivers.append({"factor": "loan_grade", "impact": "reduces risk", "value": data.loan_grade})
    if not drivers: drivers.append({"factor": "combined_profile", "impact": "model-weighted assessment", "value": "mixed"})
    recommendation = {"approve": "Approve under standard policy", "manual_review": "Request enhanced affordability review", "reject": "Decline or require additional security"}[decision]
    return {"default_probability": round(probability, 6), "risk_score": round(probability * 1000),
            "confidence": round(confidence * 100, 2), "risk_category": risk,
            "recommendation": recommendation, "explanation": {"top_drivers": drivers}, "decision": decision}
