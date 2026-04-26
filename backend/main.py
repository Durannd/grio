from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from api.v1.endpoints import users, concepts, assessment, auth, learning_path, chatbot, assessment_report, study_plan, study
from database import engine, Base
import models.user
import models.question
import models.assessment

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
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
