from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import os

from database import get_db
from crud.user import get_user_by_email
from core.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from core.rate_limit import limiter, get_rate_limit
from schemas.user import User, UserCreate
from crud.user import create_user
from core.deps import get_current_user
from pydantic import BaseModel

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/login")
@limiter.limit(get_rate_limit("login"))
def login_for_access_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    is_production = os.getenv("ENV", "development") == "production"
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="strict",
        secure=is_production,
    )
    
    return {"message": "Login successful"}

@router.post("/logout")
def logout(response: Response, access_token: str = Cookie(None)):
    if access_token:
        try:
            from jose import jwt as jwt_decode
            from core.security import SECRET_KEY, ALGORITHM
            from core.redis_client import blacklist_token
            import time

            payload = jwt_decode.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            jti = payload.get("jti")
            exp = payload.get("exp")
            if jti and exp:
                ttl = int(exp - time.time())
                if ttl > 0:
                    blacklist_token(jti, ttl)
        except Exception:
            pass  # Token inválido/expirado, não precisa revogar
    response.delete_cookie(key="access_token")
    return {"message": "Logout successful"}

@router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/signup")
@limiter.limit(get_rate_limit("signup"))
def signup(
    request: Request,
    response: Response,
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="O usuário com este e-mail já existe no sistema.",
        )
    user = create_user(db, user=user_in)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    is_production = os.getenv("ENV", "development") == "production"
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="strict",
        secure=is_production,
    )
    
    return {"message": "Signup successful"}


@router.get("/csrf-token")
@limiter.limit("30/minute")
def get_csrf_token(request: Request):
    """Retorna um token CSRF para requisições POST/PUT/DELETE"""
    from core.csrf import csrf_validator, get_csrf_token_expiry
    
    client_ip = request.headers.get("x-forwarded-for")
    if client_ip:
        client_ip = client_ip.split(',')[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"
        
    user_agent = request.headers.get("user-agent", "")
    session_id = f"{client_ip}:{user_agent}"
    
    token = csrf_validator.issue_token(session_id)
    
    return {
        "csrf_token": token,
        "expires_at": get_csrf_token_expiry()
    }
