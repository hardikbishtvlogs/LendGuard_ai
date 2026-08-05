import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from .api.routes import router
from .core.config import get_settings
from sqlalchemy import text
from .core.database import Base, engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if s.environment == "production" and s.secret_key == "change-me-in-production":
        raise RuntimeError("SECRET_KEY must be set in production")
    Base.metadata.create_all(engine)
    yield


s = get_settings()
app = FastAPI(title=s.app_name, version="1.0.0", description="Enterprise loan-default risk API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=s.origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
if s.environment == "production":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=s.hosts)
app.include_router(router)


@app.get("/health")
def health(): return {"status": "healthy", "service": s.app_name}


@app.get("/ready")
def ready():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ready", "service": s.app_name}


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    logging.exception("Unhandled request error")
    return JSONResponse(status_code=500, content={"detail": "Internal server error", "request_id": request.headers.get("x-request-id")})
