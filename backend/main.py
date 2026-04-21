from fastapi import FastAPI
from backend.api.v1.endpoints import users
from backend.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
