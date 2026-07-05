from datetime import datetime
from io import BytesIO
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import create_token, current_user, hash_password, verify_password
from ..models.entities import Customer, Prediction, User
from ..schemas.api import AssessmentOut, CustomerIn, CustomerOut, LoanApplication, PredictionOut, Register, Token, UserOut
from ..services.ml import predict
from ..services.powerbi import push_prediction

router = APIRouter(prefix="/api/v1")


@router.post("/auth/register", response_model=Token, status_code=201)
def register(body: Register, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(409, "Email already registered")
    # Public registration cannot self-assign privileged roles.
    user = User(email=body.email.lower(), full_name=body.full_name, password_hash=hash_password(body.password), role="customer")
    db.add(user); db.commit(); db.refresh(user)
    return Token(access_token=create_token(user.id, user.role), user=user)


@router.post("/auth/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username.lower()).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    return Token(access_token=create_token(user.id, user.role), user=user)


@router.get("/users/me", response_model=UserOut)
def me(user=Depends(current_user)): return user


@router.post("/customers", response_model=CustomerOut, status_code=201)
def create_customer(body: CustomerIn, db: Session = Depends(get_db), user=Depends(current_user)):
    item = Customer(owner_id=user.id, **body.model_dump()); db.add(item); db.commit(); db.refresh(item); return item


@router.get("/customers", response_model=list[CustomerOut])
def customers(db: Session = Depends(get_db), user=Depends(current_user)):
    q = db.query(Customer)
    return q.all() if user.role == "admin" else q.filter(Customer.owner_id == user.id).all()


@router.post("/predictions", response_model=PredictionOut, status_code=201)
async def make_prediction(body: LoanApplication, tasks: BackgroundTasks, db: Session = Depends(get_db), user=Depends(current_user)):
    result = predict(body)
    record = Prediction(user_id=user.id, customer_id=body.customer_id, inputs=body.model_dump(), **result)
    db.add(record); db.commit(); db.refresh(record)
    tasks.add_task(push_prediction, {"predictionId": record.id, "timestamp": record.created_at.isoformat(), **result, **body.model_dump()})
    return record


@router.post("/predictions/demo", response_model=AssessmentOut)
def demo_prediction(body: LoanApplication):
    """Public demo; authenticated scoring persists a full audit trail."""
    return predict(body)


@router.get("/predictions", response_model=list[PredictionOut])
def history(db: Session = Depends(get_db), user=Depends(current_user)):
    q = db.query(Prediction)
    if user.role == "customer": q = q.filter(Prediction.user_id == user.id)
    return q.order_by(Prediction.created_at.desc()).limit(500).all()


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user=Depends(current_user)):
    q = db.query(Prediction)
    if user.role == "customer": q = q.filter(Prediction.user_id == user.id)
    rows = q.all(); total = len(rows)
    by_risk = {k: sum(x.risk_category == k for x in rows) for k in ("low", "medium", "high")}
    approved = sum(x.decision == "approve" for x in rows)
    return {"total_applications": total, "approved": approved, "rejected": sum(x.decision == "reject" for x in rows),
            "approval_rate": round(approved / total * 100, 2) if total else 0, "risk_distribution": by_risk,
            "average_default_probability": round(sum(x.default_probability for x in rows) / total, 4) if total else 0}


def report_rows(db, user):
    q = db.query(Prediction)
    return (q if user.role != "customer" else q.filter(Prediction.user_id == user.id)).order_by(Prediction.created_at.desc()).all()


@router.get("/reports/excel")
def excel_report(db: Session = Depends(get_db), user=Depends(current_user)):
    wb = Workbook(); ws = wb.active; ws.title = "Predictions"
    ws.append(["ID", "Date", "Probability", "Risk", "Score", "Decision"])
    for x in report_rows(db, user): ws.append([x.id, x.created_at.isoformat(), x.default_probability, x.risk_category, x.risk_score, x.decision])
    stream = BytesIO(); wb.save(stream)
    return Response(stream.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=loan-risk-report.xlsx"})


@router.get("/reports/pdf")
def pdf_report(db: Session = Depends(get_db), user=Depends(current_user)):
    stream = BytesIO(); c = Canvas(stream, pagesize=A4); y = 800
    c.setFont("Helvetica-Bold", 18); c.drawString(45, y, "LendGuard AI — Risk Report"); y -= 35
    c.setFont("Helvetica", 9)
    for x in report_rows(db, user):
        c.drawString(45, y, f"#{x.id}  {x.created_at:%Y-%m-%d}  Risk: {x.risk_category.upper()}  Probability: {x.default_probability:.1%}  Decision: {x.decision}")
        y -= 16
        if y < 45: c.showPage(); y = 800
    c.save()
    return Response(stream.getvalue(), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=loan-risk-report.pdf"})


@router.get("/powerbi/config")
def powerbi_config(user=Depends(current_user)):
    from ..core.config import get_settings
    return {"embed_url": get_settings().powerbi_embed_url, "configured": bool(get_settings().powerbi_embed_url)}
