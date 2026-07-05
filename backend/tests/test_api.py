from fastapi.testclient import TestClient
from app.main import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_public_demo_prediction():
    payload = {"age": 30, "income": 72000, "employment_length": 5, "loan_amount": 15000,
               "interest_rate": 11.5, "credit_history_length": 8, "home_ownership": "MORTGAGE",
               "loan_intent": "PERSONAL", "loan_grade": "B", "previous_default": "N"}
    with TestClient(app) as client:
        response = client.post("/api/v1/predictions/demo", json=payload)
        assert response.status_code == 200
        assert 0 <= response.json()["default_probability"] <= 1
