from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from crud import user as crud_user
from schemas import user as schema_user
from database import get_db
from core.deps import get_current_user
from models.user import User

router = APIRouter()


@router.post("/", response_model=schema_user.User)
def create_user(
    user: schema_user.UserCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_user.create_user(db=db, user=user)
