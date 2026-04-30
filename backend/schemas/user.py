from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator
import re

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=50)
    avatar_url: str | None = None
    is_diagnostic_completed: bool = False

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Senha deve conter ao menos uma letra maiúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('Senha deve conter ao menos um número')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9À-ÿ\s\-]{2,50}$', v):
            raise ValueError('Nome deve conter apenas letras, números, espaços e hífens (2-50 caracteres)')
        dangerous_patterns = ['<', '>', '&', '"', "'", 'javascript', 'onerror', 'onload', 'script']
        v_lower = v.lower()
        if any(pattern in v_lower for pattern in dangerous_patterns):
            raise ValueError('Nome contém caracteres não permitidos')
        return v.strip()

class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=50)
    password: str | None = Field(None, min_length=8, max_length=128)
    avatar_url: str | None = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v is None:
            return v
        if not re.search(r'[A-Z]', v):
            raise ValueError('Senha deve conter ao menos uma letra maiúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('Senha deve conter ao menos um número')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is None:
            return v
        if not re.match(r'^[a-zA-Z0-9À-ÿ\s\-]{2,50}$', v):
            raise ValueError('Nome deve conter apenas letras, números, espaços e hífens (2-50 caracteres)')
        dangerous_patterns = ['<', '>', '&', '"', "'", 'javascript', 'onerror', 'onload', 'script']
        v_lower = v.lower()
        if any(pattern in v_lower for pattern in dangerous_patterns):
            raise ValueError('Nome contém caracteres não permitidos')
        return v.strip()

class User(UserBase):
    id: int
    current_streak: int = 0
    last_activity_date: str | None = None

    model_config = ConfigDict(from_attributes=True)

