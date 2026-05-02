from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from api.v1.endpoints import users, concepts, assessment, auth, learning_path, chatbot, assessment_report, study_plan, study, diagnostic
from api import health_check
from database import engine, Base
from sqlalchemy import text
from core.env import validate_environment
from core.logger import logger
from core.rate_limit import limiter
from core.csrf_middleware import setup_csrf_middleware
from core.error_handler import global_exception_handler
import models.user
import models.question
import models.assessment
import os

# Validar environment na startup
validate_environment()

Base.metadata.create_all(bind=engine)

# Garante que a coluna exigida no MVP exista no banco de dados, caso o SQLAlchemy não tenha atualizado o schema
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_diagnostic_in_progress BOOLEAN DEFAULT FALSE;"))
        conn.commit()
        logger.info("Verificação do schema da tabela users concluída com sucesso.")
except Exception as e:
    logger.error(f"Erro ao verificar/atualizar o schema do banco de dados: {e}")

logger.info("Starting Griô backend...")

app = FastAPI()
app.add_exception_handler(Exception, global_exception_handler)

# CORS origins from environment variable
allowed_origins_str = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173"
)
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
)

# Adicionar Rate Limiting middleware (antes do CSRF)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Adicionar CSRF middleware
setup_csrf_middleware(app)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return Response(
        content="Muitas requisições. Tente novamente em alguns minutos.",
        status_code=429,
        headers={"Retry-After": "60"}
    )

@app.middleware("http")
async def add_security_headers(request, call_next):
    response: Response = await call_next(request)
    # Refined CSP for API responses
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'; sandbox"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-XSS-Protection"] = "0" # Modern standard: disable legacy filter
    return response

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(concepts.router, prefix="/api/v1/concepts", tags=["concepts"])
app.include_router(assessment.router, prefix="/api/v1/assessment", tags=["assessment"])
app.include_router(assessment_report.router, prefix="/api/v1/assessment-report", tags=["assessment-report"])
app.include_router(learning_path.router, prefix="/api/v1/learning-path", tags=["learning-path"])
app.include_router(chatbot.router, prefix="/api/v1/chatbot", tags=["chatbot"])
app.include_router(study_plan.router, prefix="/api/v1/study-plan", tags=["study-plan"])
app.include_router(study.router, prefix="/api/v1/study", tags=["study"])
app.include_router(diagnostic.router, prefix="/api/v1/diagnostic", tags=["diagnostic"])
app.include_router(health_check.router, tags=["health"])
