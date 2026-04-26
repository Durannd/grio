from fastapi import Depends, HTTPException, status, Cookie
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from models.user import User
from database import get_db
from core.security import SECRET_KEY, ALGORITHM

def get_current_user(
    access_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if access_token is None:
        raise credentials_exception
        
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
