from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserUpdate
from core.security import get_password_hash

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email, 
        name=user.name, 
        hashed_password=hashed_password,
        avatar_url=user.avatar_url
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: User, user_update: UserUpdate):
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
        
    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

from datetime import datetime, timedelta

def update_user_streak(db: Session, user: User):
    today = datetime.now().strftime("%Y-%m-%d")
    
    if user.last_activity_date == today:
        return user
    
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    if user.last_activity_date == yesterday:
        user.current_streak += 1
    else:
        user.current_streak = 1
        
    user.last_activity_date = today
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
