from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

Role = Literal["admin", "loan_officer", "customer"]


class Register(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=160)
    password: str = Field(min_length=8)
    role: Role = "customer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    full_name: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class CustomerIn(BaseModel):
    name: str
    email: EmailStr | None = None
    phone: str | None = None


class CustomerOut(CustomerIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
    created_at: datetime


class LoanApplication(BaseModel):
    customer_id: int | None = None
    age: float = Field(ge=18, le=100)
    income: float = Field(gt=0)
    employment_length: float = Field(ge=0, le=80)
    loan_amount: float = Field(gt=0)
    interest_rate: float = Field(ge=0, le=100)
    credit_history_length: float = Field(ge=0, le=80)
    home_ownership: Literal["RENT", "OWN", "MORTGAGE", "OTHER"]
    loan_intent: Literal["EDUCATION", "MEDICAL", "VENTURE", "PERSONAL", "HOMEIMPROVEMENT", "DEBTCONSOLIDATION"]
    loan_grade: Literal["A", "B", "C", "D", "E", "F", "G"]
    previous_default: Literal["Y", "N"]


class PredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    default_probability: float
    risk_score: int
    confidence: float
    risk_category: str
    recommendation: str
    explanation: dict
    decision: str
    created_at: datetime


class AssessmentOut(BaseModel):
    default_probability: float
    risk_score: int
    confidence: float
    risk_category: str
    recommendation: str
    explanation: dict
    decision: str
