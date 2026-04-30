from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from crud import user as crud_user
from schemas import user as schema_user
from database import get_db
from core.deps import get_current_user
from core.rate_limit import limiter
from models.user import User

router = APIRouter()


@router.post("/", response_model=schema_user.User)
@limiter.limit("5/minute")
def create_user(
    request: Request,
    user: schema_user.UserCreate, 
    db: Session = Depends(get_db)
):
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_user.create_user(db=db, user=user)
