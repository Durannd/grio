from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.endpoints import users, concepts, assessment, auth, learning_path, chatbot, assessment_report, study_plan
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
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(concepts.router, prefix="/api/v1/concepts", tags=["concepts"])
app.include_router(assessment.router, prefix="/api/v1/assessment", tags=["assessment"])
app.include_router(assessment_report.router, prefix="/api/v1/assessment-report", tags=["assessment-report"])
app.include_router(learning_path.router, prefix="/api/v1/learning-path", tags=["learning-path"])
app.include_router(chatbot.router, prefix="/api/v1/chatbot", tags=["chatbot"])
app.include_router(study_plan.router, prefix="/api/v1/study-plan", tags=["study-plan"])
