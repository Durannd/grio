from fastapi import FastAPI
from api.v1.endpoints import users, concepts, assessment
from database import engine, Base
import models

app = FastAPI()

app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(concepts.router, prefix="/api/v1/concepts", tags=["concepts"])
app.include_router(assessment.router, prefix="/api/v1/assessment", tags=["assessment"])
